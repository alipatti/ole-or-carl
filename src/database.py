from io import BytesIO
import json
from typing import Literal

from peewee import SqliteDatabase, Model, CharField, BlobField, IntegerField
import numpy as np

from .settings import DATABASE_PATH


db = SqliteDatabase(DATABASE_PATH)


class NDArrayField(BlobField):
    def python_value(self, value: bytes) -> np.ndarray:
        if value is None:
            return None

        return np.load(BytesIO(value))

    def db_value(self, value: np.ndarray) -> bytes:
        if value is None:
            return None

        stream = BytesIO
        np.save(stream, value)
        return stream.getvalue()


class ListField(CharField):
    def python_value(self, value: str) -> list:
        json.loads(value)

    def db_value(self, value: list) -> str:
        json.dumps(value)


class SchoolField(CharField):
    SCHOOLS = {"stolaf", "carleton"}

    def db_value(self, value: str) -> Literal["stolaf", "carleton"]:
        assert value in self.SCHOOLS, f"`school` must be one of {self.SCHOOLS}"
        return value


class Student(Model):
    name = CharField(index=True)
    email = CharField(unique=True)
    year = IntegerField()
    school = SchoolField()

    pronouns = CharField(null=True)

    majors = ListField()
    minors = ListField()

    # image = NDArrayField(null=True)
    # face_vector = NDArrayField(null=True)

    class Meta:
        database = db


def create_tables(safe=False):
    db.connect()
    db.create_tables([Student], safe=safe)
