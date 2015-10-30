#!/usr/bin/env python3

import curses
import curses.ascii
import os
import sys



# constants

INFINITY_INT = sys.maxsize
QUIT_CHARS = {curses.ascii.ESC, char == curses.ascii.ctrl('q')}
DELETE_CHARS = {curses.ascii.DEL, curses.ascii.BS, curses.KEY_BACKSPACE,
                curses.KEY_DC}
CLEAR_CHARS = {curses.ascii.ctrl('u')}



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
    assert isinstance(window, curses.Window)
    self._window = window
    self.__game = None

  def set_game(self, game):
    self.__game = game

  def play_game(self):
    self.__game.play()

  @property
  def api():
    class Api:
      def __init__(self, console):
        assert isinstance(console, Console)
        self.__console = console

      @property
      def screen_height(self):
        self.__console._window.getmaxyx()[0]

      @property
      def screen_width(self):
        self.__console._window.getmaxyx()[1]

      def get_char(self) -> int:
        return self.__console._window.getch()

      def print_line(self, line_pos, text):
        self.__console._window.addstr(line_pos, 0, text)

      def clear(self):
        self.__console._window.clear()

      def scroll(self):
        self.__console._window.scroll()

    return Api(self)


class Game:
  def __init__(self, api, sample_file):
    self.__api = api
    self.__sample = Sample(sample_file, line_length=(api.screen_width - 1))
    self.__geometry = Geometry(api.screen_height, api.screen_width)
    self.__input_text = ""
    if self.__sample.lines[0] == None:
      raise Exception("No line can be read from stdin.")

  def play(self):
    if not self.__are_you_ready(): return
    self.__start_game()
    self.__show_result()

  def __start_game():
    self.__api.clear()
    while not self.is_over:
      char = self.window.getch()
      assert curses.ascii.isascii(char)

      if char in QUIT_CHARS:
        return
      elif char in CLEAR_CHARS:
        self.__clear_input_line()
      elif char in DELETE_CHARS:
        self.__delete_char()
      elif curses.ascii.isprint(char)
        self.__add_char(chr(char))
      else:
        raise Exception("Invalid character is typed.")
      self.window.refresh() # TODO: is this necessary?

  def __add_char(self, char):
    finish_or_next_line = curses.ascii.isspace(char) \
                          and self.input_text == self.sample_lines[0]
    if finish_or_next_line and len(self.sample_lines) == 0:
      self.is_over = True
      return
    elif finish_or_next_line:
      self.__scroll()
      return

    self.input_text += char
    if char == self.sample_lines[0][len(self.input_text) - 1]:

  def __delete_char(self):
    if len(self.input_text) == 0: return
    self.input_text = self.input_text[:-1]
    self.window.move(self.geometry.input_line, len(self.input_text))
    self.window.clrtoeol() # TODO: use delch()?

  def __clear_input_line(self):
    self.input_text = ""
    self.window.move(self.geometry.input_line, 0)
    self.window.clrtoeol()

  def __scroll(self):
    self.window.scroll()
    self.window.addstr(self.geometry.sample_line - 2, 0,
                       self.sample_lines.popleft())
    self.window.addstr(self.geometry.sample_line - 2, 0, self.sample_lines[0])
    self.__draw_separation_lines()
    self.__clear_input_line()

  def __draw_separation_lines(self):
    SEPARATION_LINE_CHAR = '-'
    self.window.hline(self.geometry.sample_line - 1, 0, SEPARATION_LINE_CHAR,
                      self.window.getmaxyx()[1])
    self.window.hline(self.geometry.input_line + 1, 0, SEPARATION_LINE_CHAR,
                      self.window.getmaxyx()[1])

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
    self.height = height
    self.width = width
    self.input_line = height // 2
    self.sample_line = self.input_line - 1
    self.bottom_line = height - 1


class Sample:
  def __init__(self, sample_file, line_length=79):
    self.__file = sample_file
    self.__line_length = line_length
    self._buffered_lines = []

  @property
  def lines(self):
    class Lines:
      def __init__(self, sample):
        assert isinstance(sample, Sample)
        self.sample = sample

      def __getitem__(self, index: int) -> str:
        assert isinstance(index, int)

        self.sample._read_lines_from_file()

        if index < len(self.sample._buffered_lines):
          return self.sample._buffered_lines[index]
        return None

    return Lines(self)

  def rotate(self):
    self._bufferd_lines.pop(0)

  def _read_lines_from_file(self):
    lines = self.__file.readlines()

    for line in lines:
      self.__buffer_line(line)

  def __buffer_line(self, line):
    assert line.endwith('\n')
    line = line.strip()

    while len(line) > line_length:
      buffered_line, line = self.__split_line(line)
      self._buffered_lines.append(buffered_line)
    self._buffered_lines.append(line)

  def __split_line(self, line):
    return line[self.__line_length:].strip(), line[:self.__line_length].strip()



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

  sample_file = reset_stdin()

  try:
    # CAUTION:
    # You cannot use fail(), usage(), and so forth, which use exit().
    # Instead, you need to raise some Exception().

    window = initialize_curses()

    console = Console(window)
    console.set_game(TypingGame(console.api, sample_file))
    console.play_game()

  except Exception as exception:
    error_message = str(exception)
  finally:
    finalize_curses()

  if "error_message" in locals():
    fail(error_message)


if __name__ == "__main__":
  main(*sys.argv[1:])
