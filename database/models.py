from typing import Literal
from peewee import SqliteDatabase, CharField, BlobField, Field, Model
from PIL import Image
from io import BytesIO

db = SqliteDatabase('./database/students.db')


class ImageField(Field):
    field_type = 'blob'

    def python_value(self, bytes) -> :
        return Image.frombytes(BytesIO(value))

    def db_value(self, value) -> Image:
        return 

class Person(Model):
    school: Literal["stolaf", "carleton"] = CharField()
    birthday = BlobField()

    class Meta:
        database = db # This model uses the "people.db" database.