import sys

from . import const



def message(*text):
  print("{}:".format(const.COMMAND_NAME), *text, file=sys.stderr)


def error(*text):
  message("error:", *text)
  exit(1)
