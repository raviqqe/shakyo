import curses
import curses.ascii
import unicodedata



SPACES_PER_TAB = 4
ASCIIZE = True

ESCAPE_CHARS = {chr(curses.ascii.ESC), curses.ascii.ctrl('[')}
DELETE_CHARS = {chr(curses.ascii.DEL), chr(curses.KEY_DC)}
BACKSPACE_CHARS = {chr(curses.ascii.BS), chr(curses.KEY_BACKSPACE)}


def char_with_control_key(char):
  return curses.ascii.ctrl(char)


def is_printable_char(char):
  return char == '\t' or not unicodedata.category(char).startswith("C")


def set_option(name, value):
  if name == "spaces_per_tab":
    assert isinstance(value, int)
    global SPACES_PER_TAB
    SPACES_PER_TAB = value
  elif name == "asciize":
    assert isinstance(value, bool)
    global ASCIIZE
    ASCIIZE = value
  else:
    raise Exception("Invalid option name is detected.")
