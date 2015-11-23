#!/usr/bin/env python

import argparse
import os
import os.path
import pygments
import pygments.formatter
import pygments.lexers
import pygments.styles
import sys
import urllib.parse
import urllib.request
import validators

import xorcise



# constants

__version__ = "0.0.3"

COMMAND_NAME = os.path.basename(sys.argv[0])

DELETE_CHARS = xorcise.DELETE_CHARS | xorcise.BACKSPACE_CHARS
QUIT_CHARS = xorcise.ESCAPE_CHARS
CLEAR_CHAR = xorcise.ctrl('u')
SCROLL_UP_CHAR = xorcise.ctrl('n')
SCROLL_DOWN_CHAR = xorcise.ctrl('p')

DESCRIPTION = "{} is a tool to learn about something just by typing it. " \
              "Type {} to scroll up and {} to scroll down one line, " \
              "and Esc or ^[ to exit while running it." \
              .format(COMMAND_NAME,
                      xorcise.unctrl(SCROLL_UP_CHAR),
                      xorcise.unctrl(SCROLL_DOWN_CHAR))

ARGUMENT_DEFAULT_HELP = " (default: %(default)s)"
CURSOR_WIDTH = 1
ENCODING = "UTF-8"
LEXER_OPTIONS = {"stripall" : True}
SEPARATOR = ", "
SUPPORTED_SCHEMES = {"http", "https", "ftp"}
TTY_DEVICE_FILE = "/dev/tty" # POSIX compliant



# the order of bugs

def message(*text):
  print("{}:".format(COMMAND_NAME), *text, file=sys.stderr)


def error(*text):
  message("error:", *text)
  exit(1)



# classes

class Shakyo:
  ATTR_CORRECT = xorcise.RenditionAttribute.normal
  ATTR_WRONG = xorcise.RenditionAttribute.reverse

  def __init__(self, console, example_lines):
    self.__console = console
    self.__geometry = Geometry(console)
    self.__input_line = xorcise.Line()
    self.__example_lines = FormattedLines(example_lines,
                                          max_width=(console.screen_width - 1))
    if self.__example_lines[0] is None:
      raise Exception("No line can be read from the example source.")

  def do(self):
    self.__print_all_example_lines()

    while self.__example_lines[0] is not None:
      self.__update_input_line()
      char = self.__console.get_char()

      if char in QUIT_CHARS:
        break
      elif char == CLEAR_CHAR:
        self.__input_line = xorcise.Line()
      elif char in DELETE_CHARS:
        self.__input_line = self.__input_line[:-1]
      elif char == SCROLL_DOWN_CHAR:
        self.__input_line = xorcise.Line()
        self.__scroll_down()
      elif (char == '\n' and self.__input_line.normalized
                             == self.__example_lines[0].normalized) \
           or (char == SCROLL_UP_CHAR):
        self.__input_line = xorcise.Line()
        self.__scroll_up()
      elif xorcise.is_printable_char(char) \
           and (self.__input_line + xorcise.Character(char)).width \
               + CURSOR_WIDTH <= self.__console.screen_width:
        self.__input_line += xorcise.Character(char, self.__next_attr(char))

  def __update_input_line(self):
    self.__console.print_line(self.__geometry.y_input, self.__example_lines[0])
    self.__console.print_line(self.__geometry.y_input,
                              self.__input_line,
                              clear=False)

  def __scroll_up(self):
    self.__example_lines.base_index += 1
    bottom_line_index = self.__geometry.y_bottom - self.__geometry.y_input
    if self.__example_lines[bottom_line_index] is not None:
      self.__console.scroll(self.__example_lines[bottom_line_index])
    else:
      self.__console.scroll()

  def __scroll_down(self):
    self.__example_lines.base_index -= 1
    top_line_index = 0 - self.__geometry.y_input
    if self.__example_lines[top_line_index] is not None:
      self.__console.scroll(self.__example_lines[top_line_index], direction=-1)
    elif self.__example_lines[0] is not None:
      self.__console.scroll(direction=-1)
    else:
      self.__example_lines.base_index += 1

  def __print_all_example_lines(self):
    for index in range(self.__geometry.y_bottom - self.__geometry.y_input + 1):
      if self.__example_lines[index] is None: break
      self.__console.print_line(self.__geometry.y_input + index,
                                self.__example_lines[index])

  def __next_attr(self, char):
    normalized_input_line = self.__input_line.normalized
    normalized_example_line = self.__example_lines[0].normalized
    if len(normalized_input_line) >= len(normalized_example_line):
      return self.ATTR_WRONG
    return (self.ATTR_CORRECT if self.__is_correct_char(char)
            else self.ATTR_WRONG) \
           | normalized_example_line[min(len(normalized_input_line),
                                         len(normalized_example_line) - 1)] \
                                         .attr

  def __is_correct_char(self, char):
    next_input_line = self.__input_line + xorcise.Character(char)
    for index in range(len(self.__input_line.normalized),
                       len(next_input_line.normalized)):
      if index >= len(self.__example_lines[0].normalized) \
         or next_input_line.normalized[index].value \
            != self.__example_lines[0].normalized[index].value:
        return False
    return True


class Geometry:
  def __init__(self, console):
    self.y_input = (console.screen_height - 1) // 2
    self.y_bottom = console.screen_height - 1


class XorciseFormatter(pygments.formatter.Formatter):
  """
  TODO: Follow Liskov substitution principle.
  """

  def __init__(self, style="default", colorize=True, decorate=True):
    super().__init__(style=style)

    self.__attrs = {}
    for token_type, properties in self.style:
      attr = xorcise.RenditionAttribute.normal
      if colorize and properties["color"]:
        attr |= xorcise.ColorAttribute.get_best_match(
                interpret_string_rgb(properties["color"]))
      if decorate and properties["bold"]:
        attr |= xorcise.RenditionAttribute.bold
      if decorate and properties["underline"]:
        attr |= xorcise.RenditionAttribute.underline
      self.__attrs[token_type] = attr

  def format(self, tokens):
    line = xorcise.Line()
    for token_type, value in tokens:
      while token_type not in self.__attrs:
        token_type = token_type.parent

      for char in value:
        if char == '\n':
          yield line
          line = xorcise.Line()
        elif xorcise.is_printable_char(char):
          line += xorcise.Character(char, self.__attrs[token_type])

    # if there is no newline character at the end of the last line
    if len(line) > 0:
      yield line


class FormattedLines:
  def __init__(self, raw_lines, max_width=79):
    assert max_width >= 2 # for double-width characters
    self.__line_generator = self.__fold_lines(raw_lines, max_width)
    self.__lines = []
    self.__base_index = 0

  def __getitem__(self, relative_index):
    assert isinstance(relative_index, int)

    index = self.__base_index + relative_index

    for line in self.__line_generator:
      self.__lines.append(line)
      if index < len(self.__lines):
        break

    return self.__lines[index] if 0 <= index < len(self.__lines) else None

  @property
  def base_index(self):
    return self.__base_index

  @base_index.setter
  def base_index(self, base_index):
    assert isinstance(base_index, int)
    self.__base_index = base_index

  @classmethod
  def __fold_lines(cls, lines, max_width):
    for line in lines:
      while line.width > max_width:
        new_line, line = cls.__split_line(line, max_width)
        yield new_line
      yield line

  @staticmethod
  def __split_line(line, max_width):
    assert line.width > max_width

    # binary search for max index to construct a line of max width
    min_index = 0
    max_index = len(line)
    while min_index != max_index:
      middle_index = (max_index - min_index + 1) // 2 + min_index
      if line[:middle_index].width <= max_width:
        min_index = middle_index
      else:
        max_index = middle_index - 1

    assert line[:min_index].width <= max_width
    return line[:min_index], line[min_index:]



# functions

def parse_args():
  arg_parser = argparse.ArgumentParser(description=DESCRIPTION)

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
                               .format(COMMAND_NAME)
                               + ARGUMENT_DEFAULT_HELP)
  arg_parser.add_argument("-c", "--no-color",
                          dest="colorize", action="store_false",
                          help="disable colorization of text")
  arg_parser.add_argument("-d", "--no-decoration",
                          dest="decorate", action="store_false",
                          help="disable decoration of text")
  arg_parser.add_argument("-l", "--language", metavar="LANGUAGE",
                          dest="lexer_name", type=str, default=None,
                          help="specify a language of an example")
  arg_parser.add_argument("--show-languages",
                          dest="show_languages", action="store_true",
                          help="show all lauguages available for examples")
  arg_parser.add_argument("-s", "--style",
                          dest="style_name", type=str, default="default",
                          help="specify a style name" + ARGUMENT_DEFAULT_HELP)
  arg_parser.add_argument("--show-styles",
                          dest="show_styles", action="store_true",
                          help="show all available style names")
  arg_parser.add_argument("-t", "--spaces-per-tab",
                          dest="spaces_per_tab", type=int, default=4,
                          help="set number of spaces per tab"
                               + ARGUMENT_DEFAULT_HELP)
  arg_parser.add_argument("-v", "--version",
                          dest="show_version", action="store_true",
                          help="show version information")

  args = arg_parser.parse_args()

  if args.show_version:
    print("version:", __version__)
    exit()
  elif args.show_languages:
    print_sequence(all_lexer_names())
    exit()
  elif args.show_styles:
    print_sequence(all_style_names())
    exit()

  try:
    args.background_rgb = interpret_string_rgb(args.background_rgb)
  except (AssertionError, ValueError):
    error("\"{}\" is invalid as a hexadecimal RGB color."
          .format(args.background_rgb))

  check_args(args)

  return args


def check_args(args):
  if args.spaces_per_tab <= 0:
    error("Number of spaces per tab must be greater than 0.")
  elif args.lexer_name is not None \
      and args.lexer_name not in all_lexer_names():
    error("The language, \"{}\" is not available for examples."
          .format(args.lexer_name))
  elif args.style_name not in all_style_names():
    error("The style, \"{}\" is not available.".format(args.style_name))


def is_uri(uri):
  return validators.url(uri)


def all_lexer_names():
  return {alias for _, aliases, _, _ in pygments.lexers.get_all_lexers()
          for alias in aliases}


def all_style_names():
  return pygments.styles.get_all_styles()


def print_sequence(sequence, sep=", "):
  print(*sorted(sequence), sep=sep)


def read_from_stdin():
  try:
    text = sys.stdin.read()
  except KeyboardInterrupt:
    error("Nothing could be read from stdin.")

  os.close(sys.stdin.fileno())
  sys.stdin = open(TTY_DEVICE_FILE)

  return text


def read_local_file(path):
  try:
    with open(path, "rb") as f:
      return f.read().decode(ENCODING, "replace")
  except (FileNotFoundError, PermissionError) as e:
    error(e)


def read_remote_file(uri):
  if urllib.parse.urlparse(uri).scheme not in SUPPORTED_SCHEMES:
    error("Invalid scheme of URI is detected. "
          "(supported schemes: {})"
          .format(", ".join(sorted(SUPPORTED_SCHEMES))))

  message("Loading a page...")
  try:
    with urllib.request.urlopen(uri) as response:
      return response.read().decode(ENCODING, "replace")
  except urllib.error.URLError as e:
    error(e)


def guess_lexer(text, filename=None):
  lexer = None
  if filename is not None:
    lexer = get_lexer_for_filename(filename)
  if lexer is None:
    lexer = guess_lexer_from_text(text)
  if lexer is None:
    lexer = pygments.lexers.special.TextLexer(**LEXER_OPTIONS)
  return lexer


def get_lexer_for_filename(filename):
  try:
    return pygments.lexers.get_lexer_for_filename(filename, **LEXER_OPTIONS)
  except pygments.util.ClassNotFound:
    return None


def guess_lexer_from_text(text):
  try:
    return pygments.lexers.guess_lexer(text, **LEXER_OPTIONS)
  except pygments.util.ClassNotFound:
    return None


def text2lines(text, lexer, style_name="default",
               colorize=True, decorate=True):
  style = pygments.styles.get_style_by_name(style_name)
  return XorciseFormatter(style=style, colorize=colorize, decorate=decorate) \
         .format(lexer.get_tokens(text))


def interpret_string_rgb(string_rgb):
  assert len(string_rgb) == 6
  int_rgb = int(string_rgb, 16)
  return (int_rgb >> 16 & 0xff, int_rgb >> 8 & 0xff, int_rgb & 0xff)



# main routine

def main():
  args = parse_args()

  if not sys.stdout.isatty(): error("stdout is not a tty.")

  if args.example_path is None:
    filename = None
    example_text = read_from_stdin()
  elif is_uri(args.example_path):
    filename = os.path.basename(urllib.parse.urlparse(args.example_path).path)
    example_text = read_remote_file(args.example_path)
  else:
    filename = os.path.basename(args.example_path)
    example_text = read_local_file(args.example_path)

  try:
    # CAUTION:
    # You need to raise some Exception instead of calling exit() here
    # to prevent curses from messing up your terminal.

    console = xorcise.turn_on_console(asciize=args.asciize,
                                      spaces_per_tab=args.spaces_per_tab,
                                      background_rgb=args.background_rgb)

    if args.lexer_name is not None:
      lexer = pygments.lexers.get_lexer_by_name(args.lexer_name)
    else:
      lexer = guess_lexer(example_text, filename)
    example_lines = text2lines(example_text, lexer,
                               style_name=args.style_name,
                               colorize=args.colorize,
                               decorate=args.decorate)

    shakyo = Shakyo(console, example_lines)
    shakyo.do()
  except KeyboardInterrupt:
    pass
  finally:
    xorcise.turn_off_console()


if __name__ == "__main__":
  main()
