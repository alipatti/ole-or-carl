# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# TODO add to ITEM_PIPELINES

from ..database.models import Student


class ImageDownloader:
    async def process_item(self, item: Student, spider):
        # get image (async)
        # convert whatever format to numpy array (w/ e.g. PIL, cv2)
        # add image field to item
        return item


class FaceEmbedder:
    def process_item(self, item: Student, spider):
        # create vector face embedding
        return item


class DBSaver:
    async def process_item(self, item: Student, spider):
        # save item to database
        return item