#!/usr/bin/env python

import os
import os.path
import pygments
import pygments.formatter
import pygments.lexers
import pygments.lexers.special
import pygments.styles
import sys
import urllib.parse
import urllib.request
import validators

import arg
import consolekit as ck
import const
import log



# constants

CURSOR_WIDTH = 1
ENCODING = "UTF-8"
LEXER_OPTIONS = {"stripall" : True}
FALLBACK_LEXER = pygments.lexers.special.TextLexer(**LEXER_OPTIONS)
SUPPORTED_SCHEMES = {"http", "https", "ftp"}
TTY_DEVICE_FILE = "/dev/tty" # POSIX compliant



# classes

class Shakyo:
  ATTR_CORRECT = ck.RenditionAttribute.normal
  ATTR_WRONG = ck.RenditionAttribute.reverse

  def __init__(self, console, example_lines):
    self.__console = console
    self.__geometry = Geometry(console)
    self.__input_line = ck.Line()
    self.__example_lines = FormattedLines(example_lines,
                                          max_width=(console.screen_width - 1))
    if self.__example_lines[0] is None:
      raise Exception("No line can be read from the example source.")

  def do(self):
    self.__print_all_example_lines()

    while self.__example_lines[0] is not None:
      self.__update_input_line()
      char = self.__console.get_char()

      if char in const.QUIT_CHARS:
        break
      elif char == const.CLEAR_CHAR:
        self.__input_line = ck.Line()
      elif char in const.DELETE_CHARS:
        self.__input_line = self.__input_line[:-1]
      elif char == const.PAGE_DOWN_CHAR:
        self.__input_line = ck.Line()
        self.__page_down()
      elif char == const.PAGE_UP_CHAR:
        self.__input_line = ck.Line()
        self.__page_up()
      elif char == const.SCROLL_UP_CHAR:
        self.__input_line = ck.Line()
        self.__scroll_up()
      elif (char == '\n' and self.__input_line.normalized
                             == self.__example_lines[0].normalized) \
           or (char == const.SCROLL_DOWN_CHAR):
        self.__input_line = ck.Line()
        self.__scroll_down()
      elif ck.is_printable_char(char) \
           and (self.__input_line + ck.Character(char)).width \
               + CURSOR_WIDTH <= self.__console.screen_width:
        self.__input_line += ck.Character(char, self.__next_attr(char))

  def __update_input_line(self):
    self.__console.print_line(self.__geometry.y_input, self.__example_lines[0])
    self.__console.print_line(self.__geometry.y_input,
                              self.__input_line,
                              clear=False)

  def __scroll_down(self):
    self.__example_lines.base_index += 1
    bottom_line_index = self.__geometry.y_bottom - self.__geometry.y_input
    if self.__example_lines[bottom_line_index] is not None:
      self.__console.scroll(self.__example_lines[bottom_line_index])
    else:
      self.__console.scroll()

  def __scroll_up(self):
    if self.__example_lines[-1] is None: return
    self.__example_lines.base_index -= 1
    top_line_index = 0 - self.__geometry.y_input
    if self.__example_lines[top_line_index] is not None:
      self.__console.scroll(self.__example_lines[top_line_index], direction=-1)
    else:
      self.__console.scroll(direction=-1)

  def __page_down(self):
    for _ in range(self.__console.screen_height):
      if self.__example_lines[1] is None: break
      self.__scroll_down()

  def __page_up(self):
    for _ in range(self.__console.screen_height):
      if self.__example_lines[-1] is None: break
      self.__scroll_up()

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
    next_input_line = self.__input_line + ck.Character(char)
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


class LineFormatter(pygments.formatter.Formatter):
  """
  TODO: Follow Liskov substitution principle.
  """

  def __init__(self, style="default", colorize=True, decorate=True):
    super().__init__(style=style)

    self.__attrs = {}
    for token_type, properties in self.style:
      attr = ck.RenditionAttribute.normal
      if colorize and properties["color"]:
        attr |= ck.ColorAttribute.get_best_match(
                interpret_string_rgb(properties["color"]))
      if decorate and properties["bold"]:
        attr |= ck.RenditionAttribute.bold
      if decorate and properties["underline"]:
        attr |= ck.RenditionAttribute.underline
      self.__attrs[token_type] = attr

  def format(self, tokens):
    line = ck.Line()
    for token_type, string in tokens:
      while token_type not in self.__attrs:
        token_type = token_type.parent

      for char in string:
        if char == '\n':
          yield line
          line = ck.Line()
        elif ck.is_printable_char(char):
          line += ck.Character(char, self.__attrs[token_type])

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

def is_uri(uri):
  return validators.url(uri)


def read_from_stdin():
  try:
    text = sys.stdin.read()
  except KeyboardInterrupt:
    log.error("Nothing could be read from stdin.")

  os.close(sys.stdin.fileno())
  sys.stdin = open(TTY_DEVICE_FILE)

  return text


def read_local_file(path):
  try:
    with open(path, "rb") as f:
      return f.read().decode(ENCODING, "replace")
  except (FileNotFoundError, PermissionError) as e:
    log.error(e)


def read_remote_file(uri):
  if urllib.parse.urlparse(uri).scheme not in SUPPORTED_SCHEMES:
    log.error("Invalid scheme of URI is detected. "
          "(supported schemes: {})"
          .format(", ".join(sorted(SUPPORTED_SCHEMES))))

  log.message("Loading a page...")
  try:
    with urllib.request.urlopen(uri) as response:
      return response.read().decode(ENCODING, "replace")
  except urllib.error.URLError as e:
    log.error(e)


def guess_lexer(text, filename=None):
  lexer = None
  if filename is not None:
    lexer = get_lexer_for_filename(filename)
  if lexer is None:
    lexer = guess_lexer_from_text(text)
  if lexer is None:
    lexer = FALLBACK_LEXER
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
  return LineFormatter(style=style, colorize=colorize, decorate=decorate) \
         .format(lexer.get_tokens(strip_text(text)))


def interpret_string_rgb(string_rgb):
  assert len(string_rgb) == 6
  int_rgb = int(string_rgb, 16)
  return (int_rgb >> 16 & 0xff, int_rgb >> 8 & 0xff, int_rgb & 0xff)


def strip_text(text):
  return '\n'.join(line.rstrip() for line in text.split('\n'))


def get_lexer_by_name(lexer_name):
  return pygments.lexers.get_lexer_by_name(lexer_name)


def uri_to_filename(uri):
  return os.path.basename(urllib.parse.urlparse(uri).path)


def get_filename_and_text(path):
  if path is None:
    return None, read_from_stdin()
  elif is_uri(path):
    return uri_to_filename(path), read_remote_file(path)
  else:
    return os.path.basename(path), read_local_file(path)



# main routine

def main():
  args = arg.get_args()

  if not sys.stdout.isatty(): log.error("stdout is not a tty.")

  filename, example_text = get_filename_and_text(args.example_path)

  try:
    # CAUTION:
    # You need to raise some Exception instead of calling exit() here
    # to prevent curses from messing up your terminal.

    console = ck.turn_on_console(asciize=args.asciize,
                                 spaces_per_tab=args.spaces_per_tab,
                                 background_rgb=args.background_rgb)

    if args.lexer_name is not None:
      lexer = get_lexer_by_name(args.lexer_name)
    else:
      lexer = guess_lexer(example_text, filename)
    example_lines = text2lines(example_text, lexer,
                               style_name=args.style_name,
                               colorize=args.colorize,
                               decorate=args.decorate)

    Shakyo(console, example_lines).do()
  except KeyboardInterrupt:
    pass
  finally:
    ck.turn_off_console()


if __name__ == "__main__":
  main()
