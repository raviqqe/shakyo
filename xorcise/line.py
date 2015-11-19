import text_unidecode
import unicodedata

from .character import Character



class Line:
  """
  A immutable class which represents one-line text on console.
  """

  SPACES_PER_TAB = 4
  ASCIIZE = False

  def __init__(self, *chars):
    assert all(isinstance(char, Character) for char in chars)
    self.__chars = chars

  def __len__(self):
    return len(self.__chars)

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
    for char in self.__chars:
      yield char

  def __add__(self, char_or_line):
    if isinstance(char_or_line, Character):
      char = char_or_line
      return Line(*self, char)
    elif isinstance(char_or_line, Line):
      line = char_or_line
      return Line(*self, *line)

  def __getitem__(self, key):
    if isinstance(key, int):
      return self.__chars[key]
    elif isinstance(key, slice):
      return Line(*self.__chars[key])
    else:
      raise IndexError("Invalid key for Line class is detected. (key: {})"
                       .format(key))

  @property
  def normalized(self):
    return Line(*self.__normalize_chars)

  @property
  def width(self):
    return sum(char.width for char in self.normalized)

  @property
  def __normalize_chars(self):
    position = 0
    for char in self.__chars:
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
    return (position // cls.SPACES_PER_TAB + 1) * cls.SPACES_PER_TAB

  @classmethod
  def __normalize_char(cls, char):
    if cls.ASCIIZE:
      return [Character(string_char, char.attr)
             for string_char in text_unidecode.unidecode(char.value)]
    else:
      return [Character(string_char, char.attr)
             if not unicodedata.category(string_char).startswith("Z")
             else Character(' ', char.attr)
             for string_char in unicodedata.normalize("NFC", char.value)]
