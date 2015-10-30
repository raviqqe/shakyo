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
    if char in QUIT_CHARS:
      self.display_screen = None
    self.display_screen = self.__display_game_screen

  def __display_game_screen(self):
    self.game.set_window(self.window)
    self.game.play()
    self.display_screen = self.__display_result_screen

  def __display_result_screen(self):
    self.window.clear()
    self.window.addstr(0, 0, "Good job!")
    self.window.addstr(1, 0, "Press any key...")
    self.window.getch()
    self.display_screen = None


class Game:
  def __init__(self, sample):
    self.window = None
    self.sample = sample
    self.geometry = Geometry(window)
    self.input_text = ""
    num_of_lower_sample_lines \
        = self.geometry.bottom_line - self.geometry.input_line - 1
    self.sample_lines = collections.deque(self.sample.readlines(
                             num_of_lower_sample_lines))
    if len(self.sample_lines) == 0:
      raise Exception("No line can be read from stdin.")
    self.is_over = False

  def set_window(self, window):
    self.window = window

  def play(self):
    self.window.clear()
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


class Geometry:
  def __init__(self, window):
    self.input_line = window.getmaxyx()[0] // 2
    self.sample_line = self.input_line - 1
    self.bottom_line = window.getmaxyx()[0] - 1


class Sample:
  def __init__(self, sample_file, line_length=79):
    self.file = sample_file
    self.line_length = line_length
    self.buffered_lines = []

  def read_line(self):
    if len(buffered_lines) > 0:
      return buffered_lines.pop(0)

    line = self.file.readline()
    if len(line) == 0:
      return None

    assert line.endwith('\n')
    line = line.strip()

    if len(line) > self.line_length:
      line, rest_line = self.__split_line(line)
      while len(rest_line) > line_length:
        buffered_line, rest_line = self.__split_line(rest_line)
        self.buffered_lines.append(buffered_line)
      self.buffered_lines.append(rest_line)
    return line

  def read_lines(self, num_of_lines=INFINITY_INT):
    lines = []
    for _ in range(num_of_lines):
      line = self.read_line()
      if line == None: break
      lines.append(line)
    return lines

  def __split_line(self, line):
    return line[self.line_length:].strip(), line[:self.line_length].strip()




# functions

def reset_stdin():
  temporary_fd = 3
  tty_device_file = "/dev/tty"

  os.dup2(sys.stdin.fileno(), temporary_fd)
  os.close(sys.stdin.fileno())
  sys.stdin = open(tty_device_file)
  original_stdin = os.fdopen(temporary_fd)
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
    console = Console(window,
              Game(Sample(sample_file, line_length=window.getmaxyx()[1] - 1)))

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
