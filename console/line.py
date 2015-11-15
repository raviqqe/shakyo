from .character import Character



class Line:
  SPACES_PER_TAB = 4

  def __init__(self, *chars):
    assert all(map(lambda char: isinstance(char, Character),
                   chars))
    self.__chars = list(chars)

  def __eq__(self, line):
    assert isinstance(line, Line)

    if len(self) != len(line): return False
    for my_char, your_char in zip(self, line):
      if my_char.value != your_char.value: return False
    return True

  def __len__(self):
    return len(list(self))

  def __iter__(self):
    position = 0
    for char in self.__chars:
      if char.value == '\t':
        boundary = self.__next_tab_boundary(position)
        while position != boundary:
          position += 1
          yield Character(' ', attr)
        continue

      for normalized_char in char.normalized:
        position += normalized_char.width
        yield normalized_char

  def append_char(self, char):
    assert isinstance(char, Character)
    self.__chars.append(char)

  def delete_char(self):
    if len(self.__chars) != 0:
      del self.__chars[-1]

  @staticmethod
  def __next_tab_boundary(position):
    return (position // self.SPACES_PER_TAB + 1) * self.SPACES_PER_TAB
