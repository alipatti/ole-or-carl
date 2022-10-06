from io import BytesIO
import json
from typing import Literal
from peewee import SqliteDatabase, CharField, BlobField, Model
import numpy as np

from ..settings import DATABASE_PATH

db = SqliteDatabase(DATABASE_PATH)


class ImageField(BlobField):
    def python_value(self, blob: bytes) -> np.ndarray:
        return np.load(BytesIO(blob))

    def db_value(self, array: np.ndarray) -> bytes:
        stream = BytesIO
        np.save(stream, array)
        return stream.getvalue()


class JsonField(CharField):
    def python_value(self, value: str) -> dict | list:
        json.loads(value)

    def db_value(self, value: dict | list) -> str:
        json.dumps(value)


class SchoolField(CharField):
    SCHOOLS = {"stolaf", "carleton"}

    def db_value(self, value: str) -> Literal["stolaf", "carleton"]:
        assert value in self.SCHOOLS
        return value


class Student(Model):
    name = CharField()
    email = CharField(primary_key=True)
    school = SchoolField()
    image = ImageField()
    majors = JsonField()
    minors = JsonField()

    class Meta:
        database = db

# this will only create the tables if they don't exist
db.connect()
db.create_tables([Student])
