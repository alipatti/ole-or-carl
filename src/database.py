from io import BytesIO
import json

from peewee import SqliteDatabase, Model, CharField, BlobField, IntegerField
import numpy as np
from PIL import Image
import requests

from .settings import CARLETON_IMAGE_URL, DATABASE_PATH, OLAF_IMG_URL


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
    name = CharField(index=True)
    email = CharField(unique=True)
    year = IntegerField()
    school = CharField()
    pronouns = CharField(null=True)
    departments = ListField()

    face = NDArrayField(null=True)

    def get_image(self) -> Image.Image:
        url = OLAF_IMG_URL if self.email.endswith("stolaf.edu") else CARLETON_IMAGE_URL

        with requests.get(url.format(self.email)) as r:
            return Image.open(r.content)

    class Meta:
        database = db


def create_tables(safe=True):
    db.connect()
    db.create_tables([Student], safe=safe)


if __name__ == "__main__":
    a1 = np.arange(5)
    field = NDArrayField()
    as_bytes = field.db_value(a1)

    print(as_bytes)
    print(type(as_bytes))

    a2 = field.python_value(as_bytes)
    print(a2)
    print(np.array_equal(a1, a2))
