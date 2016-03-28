import unicodedata

from .attribute import RenditionAttribute
from .misc import is_printable_char



class Character:
  def __init__(self, value, attr=RenditionAttribute.normal):
    assert is_printable_char(value) and isinstance(attr, int)
    self._value = value
    self._attr = attr

  @property
  def value(self):
    return self._value

  @property
  def attr(self):
    return self._attr

  @property
  def width(self):
    return 1 if unicodedata.east_asian_width(self.value) not in {"W", "F"} \
           else 2
