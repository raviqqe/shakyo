#!/usr/bin/env python

import argparse
import curses.ascii
import os
import os.path
import pygments
import pygments.formatter
import pygments.lexers
import sys
import urllib.parse
import urllib.request
import validators

import xorcise



# constants

__version__ = "0.0.3"

DESCRIPTION = "{} is a tool to learn about something just copying it " \
              "by hand. Type Esc or ^[ to exit while running it." \
              .format(os.path.basename(__file__))

TTY_DEVICE_FILE = "/dev/tty" # POSIX compliant
ENCODING = "UTF-8"
CURSOR_WIDTH = 1

QUIT_CHARS = xorcise.ESCAPE_CHARS
DELETE_CHARS = xorcise.DELETE_CHARS | xorcise.BACKSPACE_CHARS
CLEAR_CHAR = xorcise.char_with_control_key('u')
CHEAT_CHAR = xorcise.char_with_control_key('n')

CAN_CHEAT = False

SUPPORTED_SCHEMES = {"http", "https"}



# the order of bugs

def message(*text):
  print("{}:".format(os.path.basename(__file__)), *text, file=sys.stderr)

def error(*text):
  message("error:", *text)

def fail(*text):
  error(*text)
  exit(1)



# classes

class Shakyo:
  ATTR_CORRECT = xorcise.RenditionAttribute.normal
  ATTR_WRONG = xorcise.RenditionAttribute.reverse

  def __init__(self, console, example_text):
    self.__console = console
    self.__geometry = Geometry(self.__console)
    self.__input_line = xorcise.Line()
    self.__example_lines \
        = format(example_text, max_width=(self.__console.screen_width - 1))
    if len(self.__example_lines) == 0:
      raise Exception("No line can be read from example source.")

  def do(self):
    self.__print_all_example_lines()

    while len(self.__example_lines) != 0:
      self.__update_input_line()
      char = self.__console.get_char()

      if char in QUIT_CHARS:
        break
      elif char == CLEAR_CHAR:
        self.__input_line = xorcise.Line()
      elif char in DELETE_CHARS:
        self.__input_line = self.__input_line[:-1]
      elif (char == '\n' and self.__input_line.normalized
                             == self.__example_lines[0].normalized) \
           or (char == CHEAT_CHAR and CAN_CHEAT):
        self.__scroll()
      elif xorcise.is_printable_char(char) \
           and (self.__input_line + xorcise.Character(char)).width \
               + CURSOR_WIDTH <= self.__console.screen_width:
        self.__input_line += xorcise.Character(char, self.__next_attr(char))

  def __update_input_line(self):
    self.__console.print_line(self.__geometry.y_input, self.__example_lines[0])
    self.__console.print_line(self.__geometry.y_input,
                              self.__input_line,
                              clear=False)

  def __scroll(self):
    self.__console.print_line(self.__geometry.y_input, self.__example_lines[0])
    del self.__example_lines[0]
    self.__input_line = xorcise.Line()

    bottom_line_index = self.__geometry.y_bottom - self.__geometry.y_input
    if bottom_line_index < len(self.__example_lines):
      self.__console.scroll(self.__example_lines[bottom_line_index])
    else:
      self.__console.scroll()

  def __print_all_example_lines(self):
    for index in range(self.__geometry.y_bottom - self.__geometry.y_input + 1):
      if index >= len(self.__example_lines): break
      self.__console.scroll(self.__example_lines[index])

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


class CuiFormatter(pygments.formatter.Formatter):
  def __init__(self, **options):
    super().__init__(**options)

    self.__attrs = {}
    for token_type, style in self.style:
      attr = xorcise.RenditionAttribute.normal
      if style["color"]:
        attr |= xorcise.ColorAttribute.red
      if style["bold"]:
        attr |= xorcise.RenditionAttribute.bold
      if style["underline"]:
        attr |= xorcise.RenditionAttribute.underline
      self.__attrs[token_type] = attr

  def format(self, tokens):
    lines = [xorcise.Line()]
    for token_type, value in tokens:
      while token_type not in self.__attrs:
        token_type = token_type.parent

      for char in value:
        if char == '\n':
          lines.append(xorcise.Line())
        else:
          lines[-1] += xorcise.Character(char, self.__attrs[token_type])
    return lines



# functions

def format(text, max_width=79):
  tokens = pygments.lexers.guess_lexer(text, stripall=True).get_tokens(text)
  lines = CuiFormatter().format(tokens)

  new_lines = []
  for line in lines:
    while line.width > max_width:
      new_line, line = split_line(line)
      new_lines.append(new_line)
    new_lines.append(line)
  return new_lines


def split_line(line, max_width):
  assert max_width >= 2 # for double-width characters
  assert line.width > max_width

  for index in range(len(line) - 1, -1, -1):
    if line[:index].width <= max_width:
      return line[:index], line[index:]
  raise Exception("You reached to unreachable code!")


def parse_args():
  arg_parser = argparse.ArgumentParser(description=DESCRIPTION)
  arg_parser.add_argument("example_path", nargs='?', default=None,
                          help="file path or URI to example")
  arg_parser.add_argument("-c", "--cheat",
                          dest="can_cheat", action="store_true",
                          help="enable the cheat key, {}"
                               .format(curses.ascii.unctrl(CHEAT_CHAR)))
  arg_parser.add_argument("-t", "--spaces-per-tab",
                          type=int, dest="spaces_per_tab",
                          help="set number of spaces per tab")
  arg_parser.add_argument("-v", "--version",
                          dest="show_version", action="store_true",
                          help="show version information")

  args = arg_parser.parse_args()

  if args.show_version:
    print("version:", __version__)
    exit()

  if args.spaces_per_tab != None:
    xorcise.set_option("spaces_per_tab", args.spaces_per_tab)

  global CAN_CHEAT
  CAN_CHEAT = args.can_cheat

  return args


def read_from_stdin():
  text = ""
  for line in sys.stdin:
    text += line

  sys.stdin.close()
  sys.stdin = open(TTY_DEVICE_FILE)

  return text


def read_local_file(path):
  with open(path, encoding=ENCODING) as f:
    return f.read()


def read_remote_file(uri):
  if urllib.parse.urlparse(uri).scheme not in SUPPORTED_SCHEMES:
    fail("Invalid scheme of URI is detected. "
         "(supported schemes: {})".format(", ".join(SUPPORTED_SCHEMES)))

  message("Loading a page...")
  with urllib.request.urlopen(uri) as response:
    return response.read().decode(ENCODING, "replace")



# main routine

def main():
  if not sys.stdout.isatty(): fail("stdout is not a tty.")

  args = parse_args()

  if args.example_path == None:
    example_text = read_from_stdin()
  elif validators.url(args.example_path):
    example_text = read_remote_file(args.example_path)
  else:
    example_text = read_local_file(args.example_path)

  try:
    # CAUTION:
    # You need to raise some Exception instead of calling exit() here
    # to prevent curses from messing up your terminal.

    console = xorcise.turn_on_console()

    shakyo = Shakyo(console, example_text)
    shakyo.do()
  finally:
    xorcise.turn_off_console()


if __name__ == "__main__":
  main()
