#!/usr/bin/env python

import argparse
import curses
import curses.ascii
import os
import os.path
import string
import sys
import tempfile
import text_unidecode
import unicodedata
import urllib.parse
import urllib.request
import validators



# constants

__version__ = "0.0.3"

DESCRIPTION = "{} is a tool to learn about something just copying it " \
              "by hand. Type Esc or ^[ to exit while running it." \
              .format(os.path.basename(__file__))

TTY_DEVICE_FILE = "/dev/tty" # POSIX compliant
UTF8 = "UTF-8"

QUIT_CHARS = {chr(curses.ascii.ESC), curses.ascii.ctrl('[')}
DELETE_CHARS = {chr(curses.ascii.DEL), chr(curses.ascii.BS),
                chr(curses.KEY_BACKSPACE), chr(curses.KEY_DC)}
CLEAR_CHAR = curses.ascii.ctrl('u')
CHEAT_CHAR = curses.ascii.ctrl('n')

CAN_CHEAT = False
SPACES_PER_TAB = 4

ATTR_CORRECT = curses.A_NORMAL
ATTR_ERROR = curses.A_REVERSE

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

class ConsoleApi:
  def __init__(self, window):
    self.__window = window

  def initialize(self):
    self.__window.keypad(True)
    self.__window.scrollok(True)
    self.__window.move(self.input_line, self.x)

  def __keep_position(method):
    def wrapper(self, *args, **keyword_args):
      position = self.__window.getyx()
      result = method(self, *args, **keyword_args)
      self.__window.move(*position)
      return result
    return wrapper

  @property
  def input_line(self):
    return (self.screen_height - 1) // 2

  @property
  def screen_height(self):
    return self.__window.getmaxyx()[0]

  @property
  def screen_width(self):
    return self.__window.getmaxyx()[1]

  @property
  def x(self):
    return self.__window.getyx()[1]

  @x.setter
  def x(self, x):
    if not 0 <= x < self.screen_width: return
    self.__window.move(self.__window.getyx()[0], x)

  def get_char(self) -> str:
    return chr(self.__window.getch())

  @__keep_position
  def put_char(self, char: str, attr=curses.A_NORMAL):
    assert self.__is_single_width_ascii_char(char)
    self.__window.addch(ord(char), attr)

  @__keep_position
  def put_line(self, line_pos, text):
    assert len(text) <= self.screen_width
    self.__window.move(line_pos, 0)
    self.__window.clrtoeol()
    self.__window.addstr(line_pos, 0, text)

  @__keep_position
  def clear(self):
    self.__window.clear()

  @__keep_position
  def scroll(self):
    self.__window.scroll()

  @staticmethod
  def __is_single_width_ascii_char(char: str):
    return len(char) == 1 and (curses.ascii.isprint(char) or char == " ")


class InputLineApi:
  def __init__(self, api):
    assert isinstance(api, ConsoleApi)
    self.__api = api

  def put_char(self, char, attr=ATTR_CORRECT):
    self.__api.put_char(char, attr=attr)

  def put_line(self, text):
    self.__api.put_line(self.__api.input_line, text)

  @property
  def x(self):
    return self.__api.x

  @x.setter
  def x(self, x):
    self.__api.x = x


class TypingGame:
  def __init__(self, api, example_file):
    assert isinstance(api, ConsoleApi)

    self.__api = api
    self.__example_text = FormattedText(example_file,
                                        line_length=(api.screen_width - 1))
    self.__input_line = InputLine(InputLineApi(api))
    if self.__example_text[0] == None:
      raise Exception("No line can be read from example source.")

  def play(self):
    self.__api.initialize()
    self.__initialize_screen()

    while True:
      char = self.__api.get_char()

      if char in QUIT_CHARS:
        break
      if char == CLEAR_CHAR:
        self.__reset_input_line()
        continue
      if char in DELETE_CHARS:
        self.__input_line.delete_char()
        continue

      if not (char == CHEAT_CHAR and CAN_CHEAT):
        line_completed = self.__input_line.append_char(char)
        if not line_completed: continue
      if self.__example_text[1] == None: break
      self.__scroll()

  def __scroll(self):
    self.__api.scroll()
    del self.__example_text[0]
    self.__print_bottom_example_text()
    self.__reset_input_line()

  def __reset_input_line(self):
    self.__input_line.initialize(self.__example_text[0])

  def __print_bottom_example_text(self):
    index = self.__bottom_line - self.__api.input_line
    if self.__example_text[index] != None:
      self.__api.put_line(self.__bottom_line, self.__example_text[index])

  def __initialize_screen(self):
    self.__api.clear()
    self.__print_all_example_text()
    self.__reset_input_line()

  def __print_all_example_text(self):
    for index in range(self.__bottom_line - self.__api.input_line + 1):
      if self.__example_text[index] == None: break
      self.__api.put_line(self.__api.input_line + index,
                          self.__example_text[index])

  @property
  def __bottom_line(self):
    return self.__api.screen_height - 1


class InputLine:
  def __init__(self, api):
    assert isinstance(api, InputLineApi)
    self.__api = api

  def initialize(self, example_text):
    assert example_text == normalize_text(example_text)

    self.__input_text = ""
    self.__example_text = example_text
    self.__api.put_line(example_text)
    self.__api.x = 0

  def append_char(self, char) -> bool:
    if char == "\n" \
        and normalize_text(self.__input_text) == self.__example_text:
      return True

    if len(normalize_text(self.__input_text)) < len(self.__example_text) \
        and self.__is_valid_input_char(char):
      self.__input_text += char
      for printed_char in normalize_text(char):
        if self.__api.x == len(self.__example_text):
          break
        self.__print_char(printed_char)
    return False

  def delete_char(self):
    self.__input_text = self.__input_text[:-1]
    while self.__api.x > len(normalize_text(self.__input_text)):
      self.__api.x -= 1
      self.__api.put_char(self.__example_text[self.__api.x])

  def __print_char(self, char):
    attr = ATTR_CORRECT if char == self.__example_text[self.__api.x] \
           else ATTR_ERROR
    self.__api.put_char(char, attr=attr)
    self.__api.x += 1

  @staticmethod
  def __is_valid_input_char(char):
    return (char in string.printable
            and not unicodedata.category(char).startswith("C")) or char == "\t"


class FormattedText:
  def __init__(self, text_file, line_length=79):
    self.__file = text_file
    self.__line_length = line_length
    self.__buffered_lines = []

  def __del__(self):
    self.__file.close()

  def __getitem__(self, index: int) -> str:
    self.__read_lines_from_file()

    return self.__buffered_lines[index] if index < len(self.__buffered_lines) \
           else None

  def __delitem__(self, index: int):
    del self.__buffered_lines[index]

  def __read_lines_from_file(self):
    lines = self.__file.readlines()

    for line in lines:
      self.__buffer_line(normalize_text(line))

  def __buffer_line(self, line):
    line = line.rstrip()

    while len(line) > self.__line_length:
      buffered_line, line = self.__split_line(line)
      self.__buffered_lines.append(buffered_line)
    self.__buffered_lines.append(line)

  def __split_line(self, line):
    return line[:self.__line_length].rstrip(), \
           line[self.__line_length:].rstrip()



# functions

def normalize_text(text):
  return "".join(char for char in text_unidecode.unidecode(
                 text.replace("\t", " " * SPACES_PER_TAB))
                 if char in string.printable)


def reset_stdin():
  TEMPORARY_FD = 3

  os.dup2(sys.stdin.fileno(), TEMPORARY_FD)
  os.close(sys.stdin.fileno())
  sys.stdin = open(TTY_DEVICE_FILE)

  return os.fdopen(TEMPORARY_FD)


def initialize_curses():
  window = curses.initscr()
  curses.noecho()
  curses.cbreak()
  curses.start_color()
  curses.use_default_colors()
  return window


def finalize_curses():
  curses.nocbreak()
  curses.echo()
  curses.endwin() # should be at the very last line


def parse_args():
  arg_parser = argparse.ArgumentParser(description=DESCRIPTION)
  arg_parser.add_argument("example_path", nargs='?', default=None,
                          help="path or URI to example")
  arg_parser.add_argument("-c", "--cheat",
                          dest="can_cheat",
                          action="store_true",
                          help="enable the cheat key, {}"
                               .format(curses.ascii.unctrl(CHEAT_CHAR)))
  arg_parser.add_argument("-t", "--spaces-per-tab",
                          type=int, dest="spaces_per_tab",
                          help="set number of spaces per tab")
  arg_parser.add_argument("-v", "--version",
                          dest="show_version",
                          action="store_true", default=False,
                          help="show version information")

  args = arg_parser.parse_args()

  if args.show_version:
    print("version:", __version__)
    exit()

  if args.spaces_per_tab != None:
    global SPACES_PER_TAB
    SPACES_PER_TAB = args.spaces_per_tab
  if args.can_cheat == True:
    global CAN_CHEAT
    CAN_CHEAT = True

  return args


def get_example_file():
  example_path = parse_args().example_path

  if example_path != None and validators.url(example_path) \
      and sys.stdin.isatty():
    return get_remote_file(example_path)
  elif example_path != None and sys.stdin.isatty():
    return open(example_path)
  elif example_path == None and not sys.stdin.isatty():
    return reset_stdin()
  else:
    fail("Example is read from either the path or URI specified "
         "in the argument or stdin.")


def get_remote_file(uri):
  if urllib.parse.urlparse(uri).scheme not in SUPPORTED_SCHEMES:
    fail("Invalid scheme of URI is detected. "
         "(supported schemes: {})".format(", ".join(SUPPORTED_SCHEMES)))

  message("Loading a page...")
  temporary_file = tempfile.TemporaryFile(mode="w+")
  with urllib.request.urlopen(uri) as response:
    temporary_file.write(response.read().decode(UTF8, "replace"))
  temporary_file.seek(0)
  return temporary_file



# main routine

def main():
  if not sys.stdout.isatty(): fail("stdout is not a tty.")

  example_file = get_example_file()

  try:
    # CAUTION:
    # You need to raise some Exception() instead of calling exit() here
    # to prevent curses from messing up your terminal.

    window = initialize_curses()

    TypingGame(ConsoleApi(window), example_file).play()
  finally:
    finalize_curses()


if __name__ == "__main__":
  main()
