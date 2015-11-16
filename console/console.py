import curses
import unicodedata

from .line import Line
from .attribute import ColorAttribute



class Console:
  def __init__(self):
    self.__window = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.use_default_colors()
    ColorAttribute.initialize()
    self.__window.immedok(True)
    self.__window.keypad(True)
    self.__window.scrollok(True)

  def turn_on(self):
    self.__window.clear()
    self.__window.move(0, 0)

  def turn_off(self):
    curses.nocbreak()
    curses.echo()
    curses.endwin()

  def __keep_position(method):
    def wrapper(self, *args, **keyword_args):
      position = self.__window.getyx()
      result = method(self, *args, **keyword_args)
      self.__window.move(*position)
      return result
    return wrapper

  @property
  def screen_height(self):
    return self.__window.getmaxyx()[0]

  @property
  def screen_width(self):
    return self.__window.getmaxyx()[1]

  def get_char(self) -> str:
    return chr(self.__window.getch())

  def print_line(self, y, line, clear=True):
    assert 0 <= y < self.screen_height
    assert isinstance(line, Line)
    self.__window.move(y, 0)
    if clear:
      self.__window.clrtoeol()
    for char in line.normalized:
      assert not unicodedata.category(char.value).startswith("C")
      self.__window.addstr(char.value, char.attr)

  @__keep_position
  def erase(self):
    self.__window.erase()

  @__keep_position
  def scroll(self, line=None):
    self.__window.scroll()
    if line != None:
      assert isinstance(line, Line)
      self.print_line(self.screen_height - 1, line)
