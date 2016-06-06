import sys

from . import config



def message(*text):
  print("{}:".format(config.COMMAND_NAME), *text, file=sys.stderr)


def error(*text):
  message("error:", *text)
  exit(1)
