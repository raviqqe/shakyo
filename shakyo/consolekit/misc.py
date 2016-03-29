import curses
import curses.ascii
import unicodedata
from curses.ascii import ctrl, unctrl



ESCAPE_CHARS = {chr(curses.ascii.ESC), curses.ascii.ctrl('[')}
DELETE_CHARS = {chr(curses.ascii.DEL), chr(curses.KEY_DC)}
BACKSPACE_CHARS = {chr(curses.ascii.BS), chr(curses.KEY_BACKSPACE)}


def is_printable_char(char):
  return char == '\t' or not unicodedata.category(char).startswith("C")
