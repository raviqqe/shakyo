from . import consolekit as ck
from . import const



# classes

class Shakyo:
  CURSOR_WIDTH = 1

  def __init__(self, console, example_lines):
    self._console = console
    self._geometry = _Geometry(console)
    self._input_line = ck.Line()
    self._example_lines = _FoldedLines(example_lines,
                                       max_width=(console.screen_width - 1))
    if self._example_lines[0] is None:
      raise Exception("No line can be read from the example source.")

  def do(self):
    self._print_all_example_lines()

    while self._example_lines[0] is not None:
      self._update_input_line()
      char = self._console.get_char()

      if char in const.QUIT_CHARS:
        break
      elif char == const.CLEAR_CHAR:
        self._input_line = ck.Line()
      elif char in const.DELETE_CHARS:
        self._input_line = self._input_line[:-1]
      elif char == const.PAGE_DOWN_CHAR:
        self._input_line = ck.Line()
        self._page_down()
      elif char == const.PAGE_UP_CHAR:
        self._input_line = ck.Line()
        self._page_up()
      elif char == const.SCROLL_UP_CHAR:
        self._input_line = ck.Line()
        self._scroll_up()
      elif (char == '\n' and self._input_line.normalized
                             == self._example_lines[0].normalized) \
           or (char == const.SCROLL_DOWN_CHAR):
        self._input_line = ck.Line()
        self._scroll_down()
      elif ck.is_printable_char(char) \
           and (self._input_line + ck.Character(char)).width \
               + self.CURSOR_WIDTH <= self._console.screen_width:
        self._input_line += ck.Character(char,
                                         self._next_input_char_attr(char))

  def _update_input_line(self):
    self._console.print_line(self._geometry.y_input, self._example_lines[0])
    self._console.print_line(self._geometry.y_input,
                             self._input_line,
                             clear=False)

  def _scroll_down(self):
    self._example_lines.base_index += 1
    bottom_line_index = self._geometry.y_bottom - self._geometry.y_input
    if self._example_lines[bottom_line_index] is not None:
      self._console.scroll(self._example_lines[bottom_line_index])
    else:
      self._console.scroll()

  def _scroll_up(self):
    if self._example_lines[-1] is None: return
    self._example_lines.base_index -= 1
    top_line_index = 0 - self._geometry.y_input
    if self._example_lines[top_line_index] is not None:
      self._console.scroll(self._example_lines[top_line_index], direction="up")
    else:
      self._console.scroll(direction="up")

  def _page_down(self):
    for _ in range(self._console.screen_height):
      if self._example_lines[1] is None: break
      self._scroll_down()

  def _page_up(self):
    for _ in range(self._console.screen_height):
      if self._example_lines[-1] is None: break
      self._scroll_up()

  def _print_all_example_lines(self):
    for index in range(self._geometry.y_bottom - self._geometry.y_input + 1):
      if self._example_lines[index] is None: break
      self._console.print_line(self._geometry.y_input + index,
                               self._example_lines[index])

  def _next_input_char_attr(self, char):
    attr_correct = self._console.decoration_attrs.normal
    attr_wrong = self._console.decoration_attrs.reverse
    return (attr_correct if self._is_correct_char(char) else attr_wrong) \
           | self._next_example_char_attr

  @property
  def _next_example_char_attr(self):
    normalized_example_line = self._example_lines[0].normalized
    return normalized_example_line[min(len(self._input_line.normalized),
                                       len(normalized_example_line) - 1)].attr\
           if len(normalized_example_line) != 0 else \
           self._console.decoration_attrs.normal

  def _is_correct_char(self, char):
    normalized_input_line = self._input_line.normalized
    normalized_example_line = self._example_lines[0].normalized
    normalized_new_input_line = (self._input_line + ck.Character(char)) \
                                .normalized

    if len(normalized_new_input_line) > len(normalized_example_line):
      return False
    new_char_range = slice(len(normalized_input_line),
                           len(normalized_new_input_line))
    if normalized_new_input_line[new_char_range] \
       != normalized_example_line[new_char_range]:
      return False
    return True


class _Geometry:
  def __init__(self, console):
    self.y_input = (console.screen_height - 1) // 2
    self.y_bottom = console.screen_height - 1


class _FoldedLines:
  def __init__(self, raw_lines, max_width=79):
    assert max_width >= 2 # for double-width characters
    self._line_generator = self._fold_lines(raw_lines, max_width)
    self._lines = []
    self._base_index = 0

  def __getitem__(self, relative_index):
    assert isinstance(relative_index, int)

    index = self._base_index + relative_index

    for line in self._line_generator:
      self._lines.append(line)
      if index < len(self._lines):
        break

    return self._lines[index] if 0 <= index < len(self._lines) else None

  @property
  def base_index(self):
    return self._base_index

  @base_index.setter
  def base_index(self, base_index):
    assert isinstance(base_index, int)
    self._base_index = base_index

  @classmethod
  def _fold_lines(cls, lines, max_width):
    for line in lines:
      while line.width > max_width:
        new_line, line = cls._split_line(line, max_width)
        yield new_line
      yield line

  @staticmethod
  def _split_line(line, max_width):
    assert line.width > max_width

    # binary search for max index to construct a line of max width
    min_index = 0
    max_index = len(line)
    while min_index != max_index:
      middle_index = (max_index - min_index + 1) // 2 + min_index
      if line[:middle_index].width <= max_width:
        min_index = middle_index
      else:
        max_index = middle_index - 1

    assert line[:min_index].width <= max_width
    return line[:min_index], line[min_index:]
