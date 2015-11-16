from .character import Character



class Line:
  """
  A immutable class which represents one-line text on console.
  """

  SPACES_PER_TAB = 4

  def __init__(self, *chars):
    assert all(map(lambda char: isinstance(char, Character), chars))
    self._chars = chars

  def __len__(self):
    return len(self._chars)

  def __eq__(self, line):
    assert isinstance(line, Line)

    if len(self) != len(line): return False
    for my_char, your_char in zip(self, line):
      if my_char.value != your_char.value: return False
    return True

  def __iter__(self):
    return self._chars

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
  def width(self):
    return sum(char.width for char in self._printable_chars)

  @property
  def _printable_chars(self):
    position = 0
    for char in self._chars:
      if char.value == '\t':
        boundary = self.__next_tab_boundary(position)
        while position != boundary:
          position += 1
          yield Character(' ', char.attr)
        continue

      for normalized_char in char._normalized:
        position += normalized_char.width
        yield normalized_char

  @classmethod
  def __next_tab_boundary(cls, position):
    return (position // cls.SPACES_PER_TAB + 1) * cls.SPACES_PER_TAB
