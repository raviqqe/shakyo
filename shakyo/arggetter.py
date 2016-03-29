import argparse

from . import consolekit as ck
from . import const
from . import log
from . import pygments_util
from . import util



# constants

_DEFAULT_ARGUMENT_HELP = " (default: %(default)s)"
_DESCRIPTION = "{} is a tool to learn about something just by typing it. " \
              "Type {} to scroll down and {} to scroll up one line, " \
              "{} to scroll down and {} to scroll up one page, " \
              "and Esc or ^[ to exit while running it." \
              .format(const.COMMAND_NAME,
                      ck.unctrl(const.SCROLL_DOWN_CHAR),
                      ck.unctrl(const.SCROLL_UP_CHAR),
                      ck.unctrl(const.PAGE_DOWN_CHAR),
                      ck.unctrl(const.PAGE_UP_CHAR))
_SHOW_LANGUAGES_OPTION = "--show-languages"
_SHOW_STYLES_OPTION = "--show-styles"



# functions

def get_args():
  arg_parser = argparse.ArgumentParser(description=_DESCRIPTION)

  arg_parser.add_argument("example_path", nargs='?', default=None,
                          help="file path or URI to an example")
  arg_parser.add_argument("-a", "--asciize",
                          dest="asciize", action="store_true",
                          help="enable asciization of unicode characters")
  arg_parser.add_argument("-b", "--background-color",
                          dest="background_rgb", default="000000",
                          help="tell {} the hexadecimal background color "
                               "of your terminal to avoid the same font color "
                               "as it"
                               .format(const.COMMAND_NAME)
                               + _DEFAULT_ARGUMENT_HELP)
  arg_parser.add_argument("-c", "--no-color",
                          dest="colorize", action="store_false",
                          help="disable colorization of text")
  arg_parser.add_argument("-d", "--no-decoration",
                          dest="decorate", action="store_false",
                          help="disable decoration of text")
  arg_parser.add_argument("-l", "--language", metavar="LANGUAGE",
                          dest="lexer_name", type=str, default=None,
                          help="specify a language of an example")
  arg_parser.add_argument(_SHOW_LANGUAGES_OPTION,
                          dest="show_languages", action="store_true",
                          help="show all lauguages available for examples")
  arg_parser.add_argument("-s", "--style",
                          dest="style_name", type=str, default="default",
                          help="specify a style name" + _DEFAULT_ARGUMENT_HELP)
  arg_parser.add_argument(_SHOW_STYLES_OPTION,
                          dest="show_styles", action="store_true",
                          help="show all available style names")
  arg_parser.add_argument("-t", "--spaces-per-tab",
                          dest="spaces_per_tab", type=int, default=4,
                          help="set number of spaces per tab"
                               + _DEFAULT_ARGUMENT_HELP)
  arg_parser.add_argument("-v", "--version",
                          dest="show_version", action="store_true",
                          help="show version information")

  args = arg_parser.parse_args()

  if args.show_version:
    print("version:", const.VERSION)
    exit()
  elif args.show_languages:
    _print_sequence(pygments_util.all_lexer_names())
    exit()
  elif args.show_styles:
    _print_sequence(pygments_util.all_style_names())
    exit()

  try:
    args.background_rgb = util.interpret_string_rgb(args.background_rgb)
  except (AssertionError, ValueError):
    log.error("\"{}\" is invalid as a hexadecimal RGB color."
              .format(args.background_rgb))

  _check_args(args)

  return args


def _check_args(args):
  if args.spaces_per_tab <= 0:
    log.error("Number of spaces per tab must be greater than 0.")
  elif args.lexer_name is not None \
       and args.lexer_name not in pygments_util.all_lexer_names():
    log.error("The language, \"{}\" is not available for examples. "
              "See `{} {}`."
              .format(args.lexer_name,
                      const.COMMAND_NAME,
                      _SHOW_LANGUAGES_OPTION))
  elif args.style_name not in pygments_util.all_style_names():
    log.error("The style, \"{}\" is not available. See `{} {}`."
              .format(args.style_name, const.COMMAND_NAME, _SHOW_STYLES_OPTION))


def _print_sequence(sequence):
  print(*sorted(sequence), sep=", ")
