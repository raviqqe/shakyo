#!/usr/bin/env python3

import curses
import curses.ascii
import os
import sys



# constants

quit_chars = curses.ascii.ESC or char == curses.ascii.ctrl('q')


# the order of bugs

def perror(*message):
  print(*message, file=sys.stderr)

def error(*message):
  perror("ERROR:", *message)

def fail(*message):
  error(*message)
  exit(1)

def usage():
  fail("usage: {}".format(sys.argv[0]))



# classes

class Console:
  def __init__(self, window, game):
    self.window = window
    self.game = game
    self.display_screen = self.__display_start_screen

  def is_down(self):
    if self.display_screen == None:
      return True
    return False

  def __display_start_screen(self):
    self.window.clear()
    self.window.addstr(0, 0, "Are you ready?")
    self.window.addstr(1, 0, "Press any key...")
    char = self.window.getch()
    if char in quit_chars:
      self.display_screen = None
    self.display_screen = self.__display_game_screen

  def __display_game_screen(self):
    self.game.play()
    self.display_screen = self.__display_result_screen

  def __display_result_screen(self):
    self.window.clear()
    self.window.addstr(0, 0, "Good job!")
    self.window.addstr(1, 0, "Press any key...")
    self.window.getch()
    self.display_screen = None


class Game:
  def __init__(self, window, sample_file):
    self.window = window
    self.sample_file = sample_file
    self.geometry = Geometry(window)

    self.input_text = ""
    self.sample_line_queue = collections.deque(self.sample_file.readlines(
                             self.geometry.num_of_lower_sample_lines))

    if len(self.sample_line_queue) == 0:
      raise Exception("No line can be read from stdin.")

  def play(self):
    self.window.clear()
    while not self.__is_over():
      char = self.window.getch()
      if char in quit_chars:
        return
      elif char == curses.ascii.ctrl('u'):
        self.__clear_input_line()

  def __is_over(self):
    pass

  def __clear_input_line(self):
    self.input_text = ""
    self.window.move(self.geometry.input_line, 0)
    self.window.clrtoeol()


class Geometry:
  def __init__(self, window):
    self.input_line = window.getmaxyx()[0] // 2
    self.sample_line = self.input_line - 1
    self.bottom_line = window.getmaxyx()[0] - 1
    self.num_of_lower_sample_lines = self.bottom_line - self.input_line - 1



# functions

def reset_stdin(stdin):
  temporary_fd = 3
  tty_device_file = "/dev/tty"

  os.dup2(stdin.fileno(), temporary_fd)
  os.close(stdin.fileno())
  new_stdin = open(tty_device_file)
  original_stdin = os.fdopen(temporary_fd)
  return new_stdin, original_stdin


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

  sys.stdin, sample_file = reset_stdin(sys.stdin)

  try:
    # CAUTION:
    # You cannot use fail(), usage(), and so forth, which use exit().
    # Instead, you need to raise some Exception().

    window = initialize_curses()
    console = Console(window, Game(window, sample_file))

    while not console.is_down():
      console.display_screen()

  except Exception as e:
    error_message = str(e)
  finally:
    finalize_curses()

  if "error_message" in locals():
    fail(error_message)


if __name__ == "__main__":
  main(*sys.argv[1:])
