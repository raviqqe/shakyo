import text_unidecode
import unicodedata

from .character import Character
from .misc import ASCIIZE, SPACES_PER_TAB



class Line:
  """
  A immutable class which represents one-line text on console.
  """

  def __init__(self, *chars):
    assert all(map(lambda char: isinstance(char, Character), chars))
    self._chars = chars

  def __len__(self):
    return len(self._chars)

  def __eq__(self, line):
    if line == None: return False
    if not isinstance(line, Line):
      raise ValueError("Line cannot be compared with other class instances "
                       "except for or None.")

    if len(self) != len(line): return False
    for my_char, your_char in zip(self, line):
      if my_char.value != your_char.value: return False
    return True

  def __iter__(self):
    for char in self._chars:
      yield char

  def __add__(self, char_or_line):
    if isinstance(char_or_line, Character):
      char = char_or_line
      return Line(*self._chars, char)
    elif isinstance(char_or_line, Line):
      line = char_or_line
      return Line(*self._chars, *line._chars)

  def __getitem__(self, key):
    if isinstance(key, int):
      return self._chars[key]
    elif isinstance(key, slice):
      return Line(*self._chars[key])
    else:
      raise IndexError("Invalid key for Line class is detected. (key: {})"
                       .format(key))

  @property
  def normalized(self):
    return Line(*self.__normalize_chars)

  @property
  def width(self):
    return len(self.normalized)

  @property
  def __normalize_chars(self):
    position = 0
    for char in self._chars:
      if char.value == '\t':
        boundary = self.__next_tab_boundary(position)
        while position != boundary:
          position += 1
          yield Character(' ', char.attr)
        continue

      for normalized_char in self.__normalize_char(char):
        position += normalized_char.width
        yield normalized_char

  @classmethod
  def __next_tab_boundary(cls, position):
    return (position // SPACES_PER_TAB + 1) * SPACES_PER_TAB

  @classmethod
  def __normalize_char(cls, char):
    if ASCIIZE:
      return cls.__str2chars(text_unidecode.unidecode(char.value), char.attr)
    else:
      return cls.__str2chars(unicodedata.normalize("NFC", char.value),
                              char.attr)

  @staticmethod
  def __str2chars(string, attr):
    return [Character(char, attr) for char in string]
