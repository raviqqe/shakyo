import unicodedata

from . import attribute
from . import misc



class Character:
  def __init__(self, string, attr=attribute.DecorationAttribute.normal):
    assert misc.is_printable_char(string) and isinstance(attr, int)
    self._string = string
    self._attr = attr

  def __str__(self):
    return self._string

  def __eq__(self, you):
    return str(self) == str(you)

  @property
  def attr(self):
    return self._attr

  @property
  def width(self):
    return 1 if unicodedata.east_asian_width(self._string) not in {"W", "F"} \
           else 2
