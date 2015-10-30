#!/usr/bin/env python3

import curses
import curses.ascii
import os
import sys



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

class Game:
  def __init__(self, window, sample_file):
    self.window = window
    self.sample_file = sample_file
    self.display_screen = self.__display_start_screen

  def is_over(self):
    if self.display_screen == None:
      return True
    return False

  def __display_start_screen(self):
    self.window.clear()
    self.window.addstr(0, 0, "are you ready?")
    self.window.addstr(1, 0, "press any key...")
    char = self.window.getch()
    if char == curses.ascii.ESC or char == curses.ascii.ctrl('q'):
      self.display_screen = None
    self.display_screen = self.__display_game_screen

  def __display_game_screen(self):
    self.display_screen = self.__display_result_screen

  def __display_result_screen(self):
    self.window.clear()
    self.window.addstr(0, 0, "good job!")
    self.window.addstr(1, 0, "press any key...")
    self.window.getch()
    self.display_screen = None



# functions

def reset_stdin(stdin):
  temporary_fd = 3
  os.dup2(stdin.fileno(), temporary_fd)
  os.close(stdin.fileno())
  new_stdin = open("/dev/tty")
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
    game = Game(window, sample_file)

    while not game.is_over():
      game.display_screen()

  except Exception as e:
    error_message = str(e)
  finally:
    finalize_curses()

  if "error_message" in locals():
    fail(error_message)


if __name__ == "__main__":
  main(*sys.argv[1:])
