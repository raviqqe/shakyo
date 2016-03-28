import text_unidecode
import unicodedata

from . import character



class Line:
  """
  A class whose instances represent one-line text on a console.
  Line instances are immutable.
  """

  SPACES_PER_TAB = 4
  ASCIIZE = False

  def __init__(self, *chars):
    assert all(isinstance(char, character.Character) for char in chars)
    self._chars = chars

  def __len__(self):
    return len(self._chars)

  def __eq__(self, line):
    if line is None: return False
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
    if isinstance(char_or_line, character.Character):
      char = char_or_line
      return Line(*self, char)
    elif isinstance(char_or_line, Line):
      line = char_or_line
      return Line(*self, *line)

  def __radd__(self, char):
    assert isinstance(char, character.Character)
    return Line(char, *self)

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
    return Line(*self._normalized_chars)

  @property
  def width(self):
    return sum(char.width for char in self.normalized)

  @property
  def _normalized_chars(self):
    position = 0
    for char in self._chars:
      if char.value == '\t':
        boundary = self._next_tab_boundary(position)
        while position != boundary:
          position += 1
          yield character.Character(' ', char.attr)
        continue

      for normalized_char in self._normalize_char(char):
        position += normalized_char.width
        yield normalized_char

  @classmethod
  def _next_tab_boundary(cls, position):
    return (position // cls.SPACES_PER_TAB + 1) * cls.SPACES_PER_TAB

  @classmethod
  def _normalize_char(cls, char):
    if cls.ASCIIZE:
      return [character.Character(string_char, char.attr)
              for string_char in text_unidecode.unidecode(char.value)]
    else:
      return [character.Character(string_char, char.attr)
              if not unicodedata.category(string_char).startswith("Z")
              else character.Character(' ', char.attr)
              for string_char in unicodedata.normalize("NFC", char.value)]
