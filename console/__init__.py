from .character import Character
from .console import Console
from .line import Line
from .attribute import RenditionAttribute, ColorAttribute
from .misc import ESCAPE_CHARS, DELETE_CHARS, BACKSPACE_CHARS, \
                  char_with_control_key, set_option, is_printable_char



__console = None


def turn_on_console():
  global __console
  __console = Console()
  return __console


def turn_off_console():
  __console.turn_off()

