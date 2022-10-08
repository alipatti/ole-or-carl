# https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from io import BytesIO
import logging
import typing
from pprint import pformat, pprint

from scrapy.exceptions import DropItem
from scrapy.http import Request, Response
from face_recognition import face_encodings, face_locations, load_image_file
from peewee import DatabaseError

from ..database import Student
from ..settings import OLAF_IMG_URL, CARLETON_IMAGE_URL

if typing.TYPE_CHECKING:
    from .items import ModelItem


class ItemPrinter:
    """Pretty-prints the item. For debugging."""

    def process_item(self, item: "ModelItem", spider):
        pprint(item)  # for debugging
        return item


class GrownupFilter:
    """Drops faculty from the pipeline.
    (Sometimes Olaf employees sneak in.)"""

    def process_item(self, item: "ModelItem", spider):
        # TODO
        # somehow determine if the person is a staff member or a student
        # if it's staff, drop it
        return item


class UniqueFilter:
    """Drops previously-scraped items from the pipeline."""

    def process_item(self, item: "ModelItem", spider):

        # check to see if student is in database
        if Student.get_or_none(Student.email == item["email"]):
            raise DropItem("Student already exists in database")

        # it's not, so continue
        return item


class FaceEmbedder:
    """Calculates the 128-dimensional vector embedding of a student's
    ID portrait using the `face_recognition` library (which is just
    a Python interface to the C++ library `dlib`)."""

    IMG_URLS = {
        "stolaf": OLAF_IMG_URL,
        "carleton": CARLETON_IMAGE_URL,
    }

    async def process_item(self, item: "ModelItem", spider):

        # fetch image
        img_url = self.IMG_URLS[item["school"]].format(item["email"])
        req = Request(img_url)
        res = await spider.crawler.engine.download(req, spider)
        img = load_image_file(res.body)

        # TODO: check if the image is one of the default/placeholder images
        is_default = False  # implement this
        if is_default:
            spider.log(
                f"Photo doesn't exist for {item['email']}",
                logging.WARNING,
            )
            return item

        # first, try to use the faster, built-in, HOG-based face-finder
        vecs = face_encodings(img)

        if vecs:
            item["face"] = vecs[0]
            return item

        # if it didn't work, try again with the CNN-based face-finder
        locs = face_locations(item["image"], model="cnn", number_of_times_to_upsample=3)
        vecs = face_encodings(item["image"], known_face_locations=locs)

        if vecs:
            item["face"] = vecs[0]
            return item

        spider.log(
            f"Unable to produce embedding for {item['email']}",
            logging.WARNING,
        )

        return item


class DBSaver:
    """Saves the student object to the database."""

    def process_item(self, item: "ModelItem", spider):

        try:
            item.save()

        except DatabaseError:
            spider.log(
                f"Unable to save {item['email']} to the database.\n{pformat(item)}",
                logging.ERROR,
            )

        return item
