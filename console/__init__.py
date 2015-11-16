import curses

from .character import Character
from .console import Console
from .line import Line
from .attribute import RenditionAttribute, ColorAttribute
from .misc import ESCAPE_CHARS, DELETE_CHARS, BACKSPACE_CHARS, \
                  char_with_control_key, set_option, is_printable_char



__console = None
__saved_visibility = None


def turn_on_console():
  window = curses.initscr()
  curses.noecho()
  curses.cbreak()

  curses.start_color()
  curses.use_default_colors()
  ColorAttribute.initialize()

  global __saved_visibility
  __saved_visibility = curses.curs_set(0)

  global __console
  __console = Console(window)

  return __console


def turn_off_console():
  curses.curs_set(__saved_visibility)
  curses.nocbreak()
  curses.echo()
  curses.endwin()

