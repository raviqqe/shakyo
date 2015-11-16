import curses
import curses.ascii

from .character import Character
from .line import Line



ESCAPE_CHARS = {chr(curses.ascii.ESC), curses.ascii.ctrl('[')}
DELETE_CHARS = {chr(curses.ascii.DEL), chr(curses.KEY_DC)}
BACKSPACE_CHARS = {chr(curses.ascii.BS), chr(curses.KEY_BACKSPACE)}


def char_with_control_key(char):
  return curses.ascii.ctrl(char)


def set_option(name, value):
  if name == "spaces_per_tab":
    assert isinstance(value, int)
    Line.SPACES_PER_TAB = value
  elif name == "asciize":
    assert isinstance(value, bool)
    Line.ASCIIZE = value
  else:
    raise Exception("Invalid option name is detected.")
