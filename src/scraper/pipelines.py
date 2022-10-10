# https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from io import BytesIO
import logging
import os
import typing
from pprint import pformat

from scrapy.exceptions import DropItem
from scrapy.http import Request, Response
from face_recognition import face_encodings, face_locations, load_image_file
from peewee import DatabaseError
import numpy as np

from ..database import Student
from ..settings import OLAF_IMG_URL, CARLETON_IMAGE_URL, DEFAULT_IMAGES_DIR

if typing.TYPE_CHECKING:
    from .items import ModelItem
    from scrapy import Spider


class ItemPrinter:
    """Pretty-prints the item. For debugging."""

    def process_item(self, item: "ModelItem", spider: "Spider"):
        spider.log(item, logging.DEBUG)
        return item


class GrownupFilter:
    """Drops faculty from the pipeline.
    (Sometimes Olaf employees sneak in.)"""

    STAFF_DEPARTMENTS = {
        "Center for Advising and Academic Support",
        "Writing Program",
        "Taylor Center for Equity and Inclusion",
        "Institutional Effectiveness and Assessment",
        "Alumni and Parent Relations",
        "Registrar’s Office",
        "Residence Life",
        "Student Accounts",
        "Business Office",
        "Dean of Students",
        "Student Activities",
        "Student Support Services",
    }

    def process_item(self, item: "ModelItem", spider: "Spider"):
        del spider

        if not item["year"]:
            raise DropItem(f"{item['email']} is a staff member")

        if any(major in self.STAFF_DEPARTMENTS for major in item["departments"]):
            raise DropItem(f"{item['email']} is a staff member")

        return item


class UniqueFilter:
    """Drops previously-scraped items from the pipeline."""

    def process_item(self, item: "ModelItem", spider: "Spider"):
        del spider

        # check to see if student is in database
        if Student.get_or_none(Student.email == item["email"]):
            raise DropItem("Student already exists in database.")

        # it's not, so continue
        return item


class FaceEmbedder:
    """Calculates the vector embedding of a student's
    ID portrait using the `face_recognition` library (which is just
    a Python interface to the C++ library `dlib`)."""

    IMG_URLS = {
        "stolaf": OLAF_IMG_URL,
        "carleton": CARLETON_IMAGE_URL,
    }

    DEFAULT_IMAGES = [
        load_image_file(os.path.join(DEFAULT_IMAGES_DIR, fp))
        for fp in os.listdir(DEFAULT_IMAGES_DIR)
    ]

    async def process_item(self, item: "ModelItem", spider: "Spider"):

        # fetch image
        username = item["email"].split("@")[0]
        img_url = self.IMG_URLS[item["school"]].format(username)
        req = Request(img_url)
        res: Response = await spider.crawler.engine.download(req)
        img = load_image_file(BytesIO(res.body))

        if any(np.array_equal(img, default) for default in self.DEFAULT_IMAGES):
            # image is one of the default placeholders
            spider.log(
                f"Photo doesn't exist for {item['name']} ({item['email']})",
                logging.WARNING,
            )
            return item

        # first, try to use the faster, built-in, HOG-based face-finder
        vecs = face_encodings(img)

        if vecs:
            item["face"] = vecs[0]
            return item

        # if it didn't work, try again with the CNN-based face-finder
        locs = face_locations(img, model="cnn", number_of_times_to_upsample=2)
        vecs = face_encodings(img, known_face_locations=locs)

        if vecs:
            item["face"] = vecs[0]
            return item

        spider.log(
            f"Unable to produce embedding for {item['name']} ({item['email']})",
            logging.WARNING,
        )

        return item


class DBSaver:
    """Saves the student object to the database."""

    def process_item(self, item: "ModelItem", spider: "Spider"):

        try:
            item.save()

        except DatabaseError as err:
            spider.log(
                f"Unable to save {item['email']} to the database.\n{pformat(item)}",
                logging.ERROR,
            )
            spider.log(err, logging.INFO)

        return item
