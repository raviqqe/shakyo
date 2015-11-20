import curses
import enum



@enum.unique
class RenditionAttribute(enum.IntEnum):
  altcharset =  curses.A_ALTCHARSET
  blink =       curses.A_BLINK
  bold =        curses.A_BOLD
  dim =         curses.A_DIM
  normal =      curses.A_NORMAL
  reverse =     curses.A_REVERSE
  standout =    curses.A_STANDOUT
  underline =   curses.A_UNDERLINE


class ColorAttribute:
  @classmethod
  def initialize(cls):
    if not curses.has_colors(): return

    cls.__rgb2attr = {}
    for color_index in range(curses.COLORS):
      pair_index = color_index + 1
      if pair_index >= curses.COLOR_PAIRS: break
      curses.init_pair(pair_index, color_index, -1)
      rgb = tuple(color * 255 // 1000
                  for color in curses.color_content(color_index))
      cls.__rgb2attr[rgb] = curses.color_pair(pair_index)

  @classmethod
  def get_best_match(cls, rgb):
    assert len(rgb) == 3
    assert all(0 <= color < 256 for color in rgb)

    if not curses.has_colors():
      return curses.A_NORMAL

    if rgb in cls.__rgb2attr:
      return cls.__rgb2attr[rgb]

    attr = cls.__find_best_match(rgb)
    cls.__rgb2attr[rgb] = attr
    return attr

  @classmethod
  def __find_best_match(cls, new_rgb):
    matched_attr = curses.color_pair(0) # white on black
    min_distance = cls.__color_distance((0, 0, 0), (255, 255, 255))
    for rgb, attr in cls.__rgb2attr.items():
      distance = cls.__color_distance(new_rgb, rgb)
      if distance < min_distance:
        min_distance = distance
        matched_attr = attr
    return matched_attr

  @staticmethod
  def __color_distance(rgb1, rgb2):
    return sum((color1 - color2) ** 2 for color1, color2 in zip(rgb1, rgb2))
