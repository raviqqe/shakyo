import curses
import unicodedata

from . import line as ln



class Console:
  def __init__(self, window):
    self._window = window
    self._window.keypad(True)
    self._window.scrollok(True)
    self._window.clear()
    self._window.move(0, 0)
    self._window.refresh()

  def _keep_position(method):
    def wrapper(self, *args, **keyword_args):
      position = self._window.getyx()
      result = method(self, *args, **keyword_args)
      self._window.move(*position)
      return result
    return wrapper

  @property
  def screen_height(self):
    return self._window.getmaxyx()[0]

  @property
  def screen_width(self):
    return self._window.getmaxyx()[1]

  def get_char(self) -> str:
    if hasattr(self._window, "get_wch"):
      char = self._window.get_wch()
    else:
      char = self._window.getch()

    if isinstance(char, int):
      return chr(char)
    return char

  def print_line(self, y, line, clear=True):
    assert 0 <= y < self.screen_height
    assert isinstance(line, ln.Line)

    self._window.move(y, 0)
    if clear:
      self._window.clrtoeol()

    for char in line.normalized:
      assert not unicodedata.category(char.value).startswith("C")
      if self._window.getyx()[1] + char.width > self.screen_width:
        break
      self._window.addstr(char.value, char.attr)

  @_keep_position
  def erase(self):
    self._window.erase()

  def refresh(self):
    self._window.refresh()

  @_keep_position
  def scroll(self, line=None, direction=1):
    assert direction in {-1, 1}
    assert isinstance(line, ln.Line) or line is None

    self._window.scroll(direction)

    if line is not None and direction == 1:
      self.print_line(self.screen_height - 1, line)
    elif line is not None and direction == -1:
      self.print_line(0, line)
