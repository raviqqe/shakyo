import sys

from .const import *



def message(*text):
  print("{}:".format(COMMAND_NAME), *text, file=sys.stderr)


def error(*text):
  message("error:", *text)
  exit(1)
