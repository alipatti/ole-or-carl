from functools import lru_cache
from io import BytesIO
import json

from peewee import SqliteDatabase, Model, CharField, BlobField, IntegerField
import numpy as np
from PIL import Image
import requests

from .settings import DATABASE_PATH, CARLETON_IMG_URL, OLAF_IMG_URL

db = SqliteDatabase(DATABASE_PATH)


class NDArrayField(BlobField):
    def python_value(self, value: bytes) -> np.ndarray:
        if value is None:
            return None

        return np.load(BytesIO(value))

    def db_value(self, value: np.ndarray) -> bytes:
        if value is None:
            return None

        stream = BytesIO()
        np.save(stream, value)
        return stream.getvalue()


class ListField(CharField):
    def python_value(self, value: str) -> list:
        return json.loads(value)

    def db_value(self, value: list) -> str:
        return json.dumps(value)


class Student(Model):
    name = CharField(index=True, null=True)
    email = CharField(unique=True, null=True)
    year = IntegerField(null=True)
    school = CharField()
    pronouns = CharField(default=[])
    departments = ListField(default=[])
    source = CharField()

    face = NDArrayField(null=True)

    @property
    def username(self):
        return self.email.split("@")[0]  # pylint: disable=no-member

    @property
    def img_url(self):
        url = OLAF_IMG_URL if self.school == "stolaf" else CARLETON_IMG_URL
        return url.format(self.username)

    @property
    @lru_cache(maxsize=1)
    def image(self):
        # pylint: disable=missing-timeout
        with requests.get(self.img_url) as r:
            return Image.open(r.content)

    class Meta:
        database = db


def create_tables(safe=True):
    db.connect()
    db.create_tables([Student], safe=safe)
