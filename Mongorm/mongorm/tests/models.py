# coding=utf-8
from mongorm.BaseModel import BaseModel

class Item(BaseModel):
    def __init__(self):
        self._id = None
        self.title = None
        self.content = None
        self.tagIds = None
        self.added = None
        self.items = []