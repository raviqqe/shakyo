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
  black =   curses.COLOR_BLACK
  blue =    curses.COLOR_BLUE
  cyan =    curses.COLOR_CYAN
  green =   curses.COLOR_GREEN
  red =     curses.COLOR_RED
  white =   curses.COLOR_WHITE
  yellow =  curses.COLOR_YELLOW
