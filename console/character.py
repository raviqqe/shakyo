import text_unidecode
import unicodedata

from .attribute import Attribute, RenditionAttribute



class Character:
  ASCIIZE = True

  def __init__(self, value, attr=RenditionAttribute.normal):
    assert self.__is_valid_char(value) and isinstance(attr, int)
    self.__value = value
    self.__attr = attr

  @property
  def value(self):
    return self.__value

  @value.setter
  def value(self, value):
    assert self.__is_valid_char(value)
    self.__value = value

  @property
  def attr(self):
    return self.__attr

  @attr.setter
  def attr(self, attr):
    assert isinstance(attr, int)
    self.__attr = attr

  @property
  def width(self):
    return 1 if unicodedata.east_asian_width(self.value) == "N" else 2

  @property
  def _normalized(self):
    if self.ASCIIZE:
      return self.__str2chars(text_unidecode.unidecode(self.value), self.attr)
    else:
      return self.__str2chars(unicodedata.normalize("NFC", self.value),
                              self.attr)

  @staticmethod
  def __is_valid_char(char):
    return not unicodedata.category(char).startswith("C") or char == '\t'

  @staticmethod
  def __str2chars(string, attr):
    return [Character(char, attr) for char in string]
