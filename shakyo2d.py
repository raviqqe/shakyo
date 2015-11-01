#!/usr/bin/env python3

import argparse
import curses
import curses.ascii
import os
import sys
import text_unidecode
import typing



# constants

DESCRIPTION = "shakyo2d is a tool to learn about something just copying it " \
              "by hand."

TTY_DEVICE_FILE = "/dev/tty" # POSIX compliant

QUIT_CHARS = {chr(curses.ascii.ESC), curses.ascii.ctrl('[')}
DELETE_CHARS = {chr(curses.ascii.DEL), chr(curses.ascii.BS),
                chr(curses.KEY_BACKSPACE), chr(curses.KEY_DC)}
CLEAR_CHAR = curses.ascii.ctrl('u')
CHEAT_CHAR = curses.ascii.ctrl('n')

CAN_CHEAT = False
SPACES_PER_TAB = 2

ATTR_CORRECT = curses.A_NORMAL
ATTR_ERROR = curses.A_REVERSE



# the order of bugs

def error(*message):
  print("ERROR:", *message, file=sys.stderr)

def fail(*message):
  error(*message)
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

  def get_char(self) -> typing.Optional[str]:
    char = self.__window.getkey()
    return char if self.__is_ascii_char(char) else None

  @__save_position
  def put_char(self, char: str, attr=curses.A_NORMAL):
    assert self.__is_ascii_char(char)
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
  def __is_ascii_char(char):
    return len(char) == 1 and curses.ascii.isascii(char)



class TypingGame:
  def __init__(self, api, example_file):
    self.__api = api
    self.__example_text = FormattedText(example_file,
                                        line_length=(api.screen_width - 1))
    self.__geometry = Geometry(api.screen_height)
    self.__input_text = ""
    if self.__example_text[0] == None:
      raise Exception("No line can be read from example souce.")

  def play(self):
    self.__initialize_screen()

    game_over = False
    while not game_over:
      char = self.__get_char()

      if char in QUIT_CHARS:
        return
      elif char == CLEAR_CHAR:
        self.__clear_input_text()
      elif char in DELETE_CHARS:
        self.__delete_char()
      elif char == CHEAT_CHAR and CAN_CHEAT:
        game_over = self.__cheat()
      elif curses.ascii.isprint(char) or curses.ascii.isspace(char):
        game_over = self.__add_char(char)

  def __get_char(self):
    char = self.__api.get_char()
    while char == None:
      char = self.__api.get_char()
    return char

  def __add_char(self, char: str) -> bool:
    go_to_next_line = char == '\n' \
                      and self.__input_text == self.__example_text[0]
    if go_to_next_line and self.__example_text[1] == None:
      return True

    if go_to_next_line:
      self.__scroll()
    elif len(self.__input_text) == len(self.__example_text[0]):
      pass
    elif char == '\t':
      for _ in range(SPACES_PER_TAB):
        result = self.__add_char(' ')
        assert result == False
    elif curses.ascii.isprint(char):
      self.__input_text += char
      attr = ATTR_CORRECT \
             if char == self.__example_text[0][len(self.__input_text) - 1] \
             else ATTR_ERROR
      self.__api.put_char(char, attr=attr)
      self.__api.move_right()
    return False

  def __delete_char(self):
    if len(self.__input_text) == 0: return
    self.__input_text = self.__input_text[:-1]
    self.__api.move_left()
    self.__api.put_char(self.__example_text[0][len(self.__input_text)])

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
    self.__input_text = ""
    self.__api.put_line(self.__geometry.current_line, self.__example_text[0])
    self.__api.move(self.__geometry.current_line, 0)

  def __print_bottom_example_text(self):
    index = self.__geometry.bottom_line - self.__geometry.current_line
    if self.__example_text[index] != None:
      self.__api.put_line(self.__geometry.bottom_line,
                          self.__example_text[index])

  def __print_all_example_text(self):
    for index in range(self.__geometry.bottom_line
                       - self.__geometry.current_line):
      if self.__example_text[index] == None: break
      self.__api.put_line(self.__geometry.current_line + index,
                          self.__example_text[index])


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

    if index < len(self.__buffered_lines):
      return self.__buffered_lines[index]
    return None

  def __delitem__(self, index: int):
    del self.__buffered_lines[index]

  def __read_lines_from_file(self):
    lines = self.__file.readlines()

    for line in lines:
      self.__buffer_line(self.__preprocess_text(line))

  def __buffer_line(self, line):
    line = line.rstrip()

    while len(line) > self.__line_length:
      buffered_line, line = self.__split_line(line)
      self.__buffered_lines.append(buffered_line)
    self.__buffered_lines.append(line)

  def __split_line(self, line):
    return line[self.__line_length:].rstrip(), \
           line[:self.__line_length].strip()

  @staticmethod
  def __preprocess_text(text):
    return text_unidecode.unidecode(text.replace('\t', ' ' * SPACES_PER_TAB))



# functions

def reset_stdin():
  TEMPORARY_FD = 3

  os.dup2(sys.stdin.fileno(), TEMPORARY_FD)
  os.close(sys.stdin.fileno())
  sys.stdin = open(TTY_DEVICE_FILE)
  original_stdin = os.fdopen(TEMPORARY_FD)
  return original_stdin


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
  curses.endwin() # should be in the very last line



# main routine

def main():
  if not sys.stdout.isatty(): fail("stdout is not a tty.")
  if sys.stdin.isatty(): fail("stdin is a tty.")

  example_file = reset_stdin()

  try:
    # CAUTION:
    # You need to raise some Exception() instead of calling exit() here
    # to prevent curses messing up your terminal.

    window = initialize_curses()

    TypingGame(ConsoleApi(window), example_file).play()
  finally:
    finalize_curses()


def parse_args():
  arg_parser = argparse.ArgumentParser(description=DESCRIPTION)
  arg_parser.add_argument("-c", "--cheat",
                          dest="can_cheat",
                          action="store_true",
                          help="enable the cheat key, {}"
                               .format(curses.ascii.unctrl(CHEAT_CHAR)))
  arg_parser.add_argument("-t", "--spaces-per-tab",
                          type=int, dest="spaces_per_tab",
                          help="set number of spaces per tab")

  args = arg_parser.parse_args()
  if args.spaces_per_tab != None:
    global SPACES_PER_TAB
    SPACES_PER_TAB = args.spaces_per_tab
  if args.can_cheat == True:
    global CAN_CHEAT
    CAN_CHEAT = True


if __name__ == "__main__":
  parse_args()
  main()
