import typing
from peewee import DatabaseError

if typing.TYPE_CHECKING:
    from ..database import Student


class ModelItem(dict):
    """
    Make Peewee models Scrapy compatible.

    >>> from models import Player
    >>> player = Player(team="Vikings")
    >>> item = ModelItem(player)
    >>> item["number"] = 23
    >>> "number" in player.__data___  # True
    """

    _model: "Student"

    def __init__(self, model):
        # input data
        self.update(model.__data__)

        # store Peewee model for later
        self._model = model

    def __setitem__(self, key, value):
        self._model.__setattr__(key, value)  # update underlying Peewee model
        super().__setitem__(key, value)


    def save(self):
        if self._model.save():
            return

        raise DatabaseError(f"Unable to save {self._model}")
