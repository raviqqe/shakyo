import unicodedata

from .attribute import Attribute, RenditionAttribute



class Character:
  def __init__(self, value, attr=RenditionAttribute.normal):
    assert self.__is_valid_char(value) and isinstance(attr, int)
    self.__value = value
    self.__attr = attr

  @property
  def value(self):
    return self.__value

  @property
  def attr(self):
    return self.__attr

  @property
  def width(self):
    return 1 if unicodedata.east_asian_width(self.value) == "N" else 2

  @staticmethod
  def __is_valid_char(char):
    return not unicodedata.category(char).startswith("C") or char == '\t'
