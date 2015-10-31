#!/usr/bin/env python3

import curses
import curses.ascii
import os
import sys



# constants

INFINITY_INT = sys.maxsize
QUIT_CHARS = {curses.ascii.ESC, curses.ascii.ctrl('q')}
DELETE_CHARS = {curses.ascii.DEL, curses.ascii.BS, curses.KEY_BACKSPACE,
                curses.KEY_DC}
CLEAR_CHARS = {curses.ascii.ctrl('u')}
SPACES_PER_TAB = 2
ATTR_CORRECT = curses.A_NORMAL
ATTR_ERROR = curses.A_REVERSE



# the order of bugs

def error(*message):
  print("ERROR:", *message, file=sys.stderr)

def fail(*message):
  error(*message)
  exit(1)

def usage():
  fail("usage: {}".format(sys.argv[0]))



# classes

class Console:
  def __init__(self, window):
    self._window = window
    self._game = None

  @property
  def ui(self):
    class Ui:
      def __init__(self, console):
        assert isinstance(console, Console)
        self.__console = console

      def set_game(self, game):
        self.__console._game = game

      def play_game(self):
        assert self.__console._game != None
        self.__console._game.play()

    return Ui(self)

  @property
  def api(self):
    class Api:
      def __init__(self, console):
        assert isinstance(console, Console)
        self.__console = console

      @property
      def screen_height(self):
        return self.__console._window.getmaxyx()[0]

      @property
      def screen_width(self):
        return self.__console._window.getmaxyx()[1]

      def get_char(self) -> int:
        return self.__console._window.getch()

      def add_char(self, char: str, attr=curses.A_NORMAL):
        assert len(char) == 1
        if not self.__console._window.getyx()[1] < self.screen_width: return
        self.__console._window.addch(ord(char), attr)

      def delete_char(self):
        y, x = self.__console._window.getyx()
        if x == 0: return
        self.__console._window.delch(y, x - 1)

      def print_line(self, line_pos, text):
        assert len(text) <= self.screen_width
        self.__console._window.move(line_pos, 0)
        self.__console._window.clrtoeol()
        self.__console._window.addstr(line_pos, 0, text)

      def clear(self):
        self.__console._window.clear()

      def scroll(self):
        self.__console._window.scroll()

      def refresh(self):
        self.__console._window.refresh()

    return Api(self)


class TypingGame:
  def __init__(self, api, example_file):
    self.__api = api
    self.__example = Sample(example_file, line_length=(api.screen_width - 1))
    self.__geometry = Geometry(api.screen_height, api.screen_width)
    self.__input_text = ""
    if self.__example.lines[0] == None:
      raise Exception("No line can be read from stdin.")

  def play(self):
    if not self.__are_you_ready(): return
    self.__start_game()
    self.__show_result()

  def __start_game(self):
    self.__api.clear()
    self.__initialize_screen()
    game_over = False
    while not game_over:
      char = self.__api.get_char()
      assert curses.ascii.isascii(char)

      if char in QUIT_CHARS:
        return
      elif char in CLEAR_CHARS:
        self.__clear_input_line()
      elif char in DELETE_CHARS:
        self.__delete_char()
      elif curses.ascii.isprint(char) or curses.ascii.isspace(char):
        game_over = self.__add_char(chr(char))
        assert isinstance(game_over, bool)

  def __add_char(self, char: str) -> bool:
    go_to_next_line = curses.ascii.isspace(char) \
                      and self.__input_text == self.__example.lines[0]
    if go_to_next_line and self.__example.lines[1] == None:
      return True

    if go_to_next_line:
      self.__scroll()
    elif len(self.__input_text) == len(self.__example.lines[0]):
      pass
    elif char == '\t':
      for _ in range(SPACES_PER_TAB):
        result = self.__add_char(' ')
        assert result == False
    elif curses.ascii.isprint(char):
      self.__input_text += char
      attr = ATTR_CORRECT \
             if char == self.__example.lines[0][len(self.__input_text) - 1] \
             else ATTR_ERROR
      self.__api.add_char(char, attr=attr)
    return False

  def __delete_char(self):
    if len(self.__input_text) == 0: return
    self.__input_text = self.__input_text[:-1]
    self.__api.delete_char()

  def __initialize_screen(self):
    self.__print_all_example_text()
    self.__draw_partitions()
    self.__clear_input_text()

  def __scroll(self):
    self.__api.scroll()
    self.__api.print_line(self.__geometry.example_line - 2,
                          self.__example.lines[0])
    self.__example.rotate()
    self.__print_current_example_text()
    self.__print_bottom_example_text()
    self.__draw_partitions()
    self.__clear_input_text()

  def __clear_input_text(self):
    self.__input_text = ""
    self.__api.print_line(self.__geometry.input_line, self.__input_text)

  def __print_current_example_text(self):
    self.__api.print_line(self.__geometry.example_line, self.__example.lines[0])

  def __print_bottom_example_text(self):
    index = self.__geometry.bottom_line - self.__geometry.next_example_line + 1
    if self.__example.lines[index] != None:
      self.__api.print_line(self.__geometry.bottom_line,
                            self.__example.lines[index])

  def __print_all_example_text(self):
    self.__print_current_example_text()
    for index in range(1, 1 + (self.__geometry.bottom_line
                               - self.__geometry.next_example_line + 1)):
      if self.__example.lines[index] == None: break
      self.__api.print_line(self.__geometry.next_example_line + (index - 1),
                            self.__example.lines[index])

  def __draw_partitions(self):
    PARTITION_CHAR = '-'
    partition = PARTITION_CHAR * self.__api.screen_width
    self.__api.print_line(self.__geometry.example_line - 1, partition)
    self.__api.print_line(self.__geometry.input_line + 1, partition)

  def __are_you_ready(self) -> bool:
    self.__api.clear()
    self.__api.print_line(0, "Are you ready?")
    self.__api.print_line(1, "Press any key...")
    char = self.__api.get_char()
    if char in QUIT_CHARS:
      return False
    return True

  def __show_result(self):
    self.__api.clear()
    self.__api.print_line(0, "Good job!")
    self.__api.print_line(1, "Press any key...")
    self.__api.get_char()


class Geometry:
  def __init__(self, height, width):
    self.input_line = height // 2
    self.example_line = self.input_line - 1
    self.next_example_line = self.input_line + 2
    self.bottom_line = height - 1


class Sample:
  def __init__(self, text_file, line_length=79):
    self.__file = text_file
    self.__line_length = line_length
    self._buffered_lines = []

  @property
  def lines(self):
    class Lines:
      def __init__(self, sample):
        assert isinstance(sample, Sample)
        self.__sample = sample

      def __getitem__(self, index: int) -> str:
        assert isinstance(index, int)

        self.__sample._read_lines_from_file()

        if index < len(self.__sample._buffered_lines):
          return self.__sample._buffered_lines[index]
        return None

    return Lines(self)

  def rotate(self):
    self._buffered_lines.pop(0)

  def _read_lines_from_file(self):
    lines = self.__file.readlines()

    for line in lines:
      self.__buffer_line(line)

  def __buffer_line(self, line):
    line = line.rstrip()

    while len(line) > self.__line_length:
      buffered_line, line = self.__split_line(line)
      self._buffered_lines.append(buffered_line)
    self._buffered_lines.append(line)

  def __split_line(self, line):
    return line[self.__line_length:].rstrip(), \
           line[:self.__line_length].strip()



# functions

def reset_stdin():
  TEMPORARY_FD = 3
  TTY_DEVICE_FILE = "/dev/tty"

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
  window.keypad(True)
  window.scrollok(True)
  return window


def finalize_curses():
  curses.nocbreak()
  curses.echo()
  curses.endwin() # should be in the very last line



# main routine

def main(*args):
  if not sys.stdout.isatty(): fail("stdout is not a tty.")
  if sys.stdin.isatty(): fail("stdin is a tty.")
  if len(args) != 0: usage()

  example_file = reset_stdin()

  try:
    # CAUTION:
    # You cannot use fail(), usage(), and so forth, which use exit().
    # Instead, you need to raise some Exception().

    window = initialize_curses()

    console = Console(window)
    console.ui.set_game(TypingGame(console.api, example_file))
    console.ui.play_game()
  finally:
    finalize_curses()


if __name__ == "__main__":
  main(*sys.argv[1:])
