import curses
import enum



class Attribute(enum.IntEnum):
  pass


@enum.unique
class RenditionAttribute(Attribute):
  altcharset =  curses.A_ALTCHARSET
  blink =       curses.A_BLINK
  bold =        curses.A_BOLD
  dim =         curses.A_DIM
  normal =      curses.A_NORMAL
  reverse =     curses.A_REVERSE
  standout =    curses.A_STANDOUT
  underline =   curses.A_UNDERLINE


@enum.unique
class ColorAttribute(Attribute):
  @classmethod
  def initialize(cls):
    curses.init_pair(0, curses.COLOR_BLACK, -1)
    cls.black = curses.color_pair(0)

    curses.init_pair(1, curses.COLOR_BLUE, -1)
    cls.blue = curses.color_pair(1)

    curses.init_pair(2, curses.COLOR_CYAN, -1)
    cls.cyan = curses.color_pair(2)

    curses.init_pair(3, curses.COLOR_GREEN, -1)
    cls.green = curses.color_pair(3)

    curses.init_pair(4, curses.COLOR_MAGENTA, -1)
    cls.magenta = curses.color_pair(4)

    curses.init_pair(5, curses.COLOR_RED, -1)
    cls.red = curses.color_pair(5)

    curses.init_pair(6, curses.COLOR_WHITE, -1)
    cls.white = curses.color_pair(6)

    curses.init_pair(7, curses.COLOR_YELLOW, -1)
    cls.yellow = curses.color_pair(7)
