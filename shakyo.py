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
import typing
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
SPACES_PER_TAB = 2

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
    window.keypad(True)
    window.scrollok(True)
    self.__window = window

  def __save_position(method):
    def wrapper(self, *args, **keyword_args):
      position = self.__window.getyx()
      method(self, *args, **keyword_args)
      self.__window.move(*position)
    return wrapper

  @property
  def screen_height(self):
    return self.__window.getmaxyx()[0]

  @property
  def screen_width(self):
    return self.__window.getmaxyx()[1]

  @property
  def x(self):
    return self.__window.getyx()[1]

  def get_char(self) -> str:
    return chr(self.__window.getch())

  @__save_position
  def put_char(self, char: str, attr=curses.A_NORMAL):
    assert self.__is_single_width_ascii_char(char)
    self.__window.addch(ord(char), attr)

  @__save_position
  def put_line(self, line_pos, text):
    assert len(text) <= self.screen_width
    self.__window.move(line_pos, 0)
    self.__window.clrtoeol()
    self.__window.addstr(line_pos, 0, text)

  def move(self, y, x):
    self.__window.move(y, x)

  def move_right(self):
    y, x = self.__window.getyx()
    if x == self.screen_width - 1: return
    self.__window.move(y, x + 1)

  def move_left(self):
    y, x = self.__window.getyx()
    if x == 0: return
    self.__window.move(y, x - 1)

  @__save_position
  def clear(self):
    self.__window.clear()

  @__save_position
  def scroll(self):
    self.__window.scroll()

  @staticmethod
  def __is_single_width_ascii_char(char: str):
    return len(char) == 1 and (curses.ascii.isprint(char) or char == " ")


class TypingGame:
  def __init__(self, api, example_file):
    self.__api = api
    self.__example_text = FormattedText(example_file,
                                        line_length=(api.screen_width - 1))
    self.__geometry = Geometry(api.screen_height)
    self.__input_text = InputText()
    if self.__example_text[0] == None:
      raise Exception("No line can be read from example source.")

  def play(self):
    self.__initialize_screen()

    game_over = False
    while not game_over:
      char = self.__api.get_char()

      if char in QUIT_CHARS:
        return
      elif char == CLEAR_CHAR:
        self.__clear_input_text()
      elif char in DELETE_CHARS:
        self.__delete_char()
      elif char == CHEAT_CHAR and CAN_CHEAT:
        game_over = self.__cheat()
      elif len(char) == 1 and (curses.ascii.isprint(char)
           or curses.ascii.isspace(char)):
        game_over = self.__add_char(char)

  def __add_char(self, char: str) -> bool:
    go_to_next_line = char == '\n' \
                      and self.__input_text == self.__example_text[0]
    if go_to_next_line and self.__example_text[1] == None:
      return True

    if go_to_next_line:
      self.__scroll()
    elif len(self.__input_text) == len(self.__example_text[0]):
      pass
    elif (char in string.printable
        and not unicodedata.category(char).startswith("C")) or char == "\t":
      self.__input_text.push_char(char)
      for printed_char in normalize_text(char):
        self.__print_char(printed_char)
    return False

  def __print_char(self, char: str):
    attr = ATTR_CORRECT if char == self.__example_text[0][self.__api.x] \
           else ATTR_ERROR
    self.__api.put_char(char, attr=attr)
    self.__api.move_right()

  def __delete_char(self):
    if len(self.__input_text) == 0: return
    for _ in range(len(normalize_text(self.__input_text.pop_char()))):
      self.__api.move_left()
      self.__api.put_char(self.__example_text[0][self.__api.x])

  def __cheat(self) -> bool:
    if self.__example_text[1] == None:
      return True
    self.__scroll()
    return False

  def __initialize_screen(self):
    self.__api.clear()
    self.__print_all_example_text()
    self.__clear_input_text()

  def __scroll(self):
    self.__api.scroll()
    del self.__example_text[0]
    self.__print_bottom_example_text()
    self.__clear_input_text()

  def __clear_input_text(self):
    self.__input_text = InputText()
    self.__api.put_line(self.__geometry.current_line, self.__example_text[0])
    self.__api.move(self.__geometry.current_line, 0)

  def __print_bottom_example_text(self):
    index = self.__geometry.bottom_line - self.__geometry.current_line
    if self.__example_text[index] != None:
      self.__api.put_line(self.__geometry.bottom_line,
                          self.__example_text[index])

  def __print_all_example_text(self):
    for index in range(self.__geometry.bottom_line
                       - self.__geometry.current_line + 1):
      if self.__example_text[index] == None: break
      self.__api.put_line(self.__geometry.current_line + index,
                          self.__example_text[index])


class InputText:
  def __init__(self):
    self.__text = ""

  def __eq__(self, text):
    return normalize_text(self.__text) == text

  def __len__(self):
    return len(normalize_text(self.__text))

  def push_char(self, char: str):
    self.__text += char

  def pop_char(self):
    last_char = self.__text[-1]
    self.__text = self.__text[:-1]
    return last_char


class Geometry:
  def __init__(self, screen_height):
    self.current_line = (screen_height - 1) // 2
    self.bottom_line = screen_height - 1


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

  message("Loading page...")
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
