# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import logging
from operator import mod
import typing
from pprint import pprint
from ..database.models import Student
from scrapy.exceptions import DropItem
from face_recognition import face_encodings, face_locations

if typing.TYPE_CHECKING:
    from .items import ModelItem


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
            raise DropItem

        # it's not, so continue
        return item


class ImageDownloader:
    """Adds a profile image to a Student object, if one exists."""

    async def process_item(self, item: "ModelItem", spider):
        pprint(item)  # for debugging
        # TODO
        # spider.crawler.engine.download
        # get image (async)
        # convert whatever format to numpy array (w/ e.g. PIL, cv2)
        # check if the image is the default one (as is often the case with stolaf)
        # add image field to item
        item["image"] = ...
        return item


class FaceEmbedder:
    """Calculates the 128-dimensional vector embedding of a student's
    ID portrait using the `dlib` api provided by the `face_recognition`
    library."""

    def process_item(self, item: "ModelItem", spider):
        if not item["image"]:
            # we weren't able to get the image in the previous step
            return item

        # try to use the faster, built-in, HOG-based face-finder
        vecs = face_encodings(item["image"])

        if vecs:
            item["face"] = vecs[0]
            return item

        # if that didn't work, try again with the CNN-based face-finder
        locs = face_locations(item["image"], model="cnn", number_of_times_to_upsample=3)
        vecs = face_encodings(item["image"], known_face_locations=locs)

        if vecs:
            item["face"] = vecs[0]
            return item

        spider.log(
            f"Unable to produce face embedding for {item['email']}",
            logging.WARNING,
        )

        return item


class DBSaver:
    """Saves the student object to the database."""

    async def process_item(self, item: "ModelItem", spider):
        result = item.save()
        if not result:
            # TODO somehow handle this (hopefully it won't happen often)
            pass
        return item
