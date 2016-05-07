import os.path
import sys

from . import consolekit as ck



VERSION = "0.0.8"

COMMAND_NAME = os.path.basename(sys.argv[0])

DELETE_CHARS = ck.DELETE_CHARS | ck.BACKSPACE_CHARS
QUIT_CHARS = ck.ESCAPE_CHARS
CLEAR_CHAR = ck.ctrl('u')
SCROLL_DOWN_CHAR = ck.ctrl('n')
SCROLL_UP_CHAR = ck.ctrl('p')
PAGE_DOWN_CHAR = ck.ctrl('f')
PAGE_UP_CHAR = ck.ctrl('b')
