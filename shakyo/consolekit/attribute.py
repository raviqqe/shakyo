import curses
import enum



_CURSES_COLOR_SCALE = 1000



@enum.unique
class DecorationAttribute(enum.IntEnum):
  altcharset =  curses.A_ALTCHARSET
  blink =       curses.A_BLINK
  bold =        curses.A_BOLD
  dim =         curses.A_DIM
  normal =      curses.A_NORMAL
  reverse =     curses.A_REVERSE
  standout =    curses.A_STANDOUT
  underline =   curses.A_UNDERLINE


class ColorAttribute:
  _colors = []
  _rgb_to_attr = {}
  _background_rgb = None

  @classmethod
  def initialize(cls, background_rgb=(0, 0, 0)):
    if not curses.has_colors(): return
    cls._set_up_colors()
    cls._background_rgb = background_rgb

  @classmethod
  def get_best_match(cls, rgb):
    assert cls._is_valid_rgb(rgb)

    if not curses.has_colors():
      return curses.A_NORMAL

    if rgb in cls._rgb_to_attr:
      return cls._rgb_to_attr[rgb]

    attr = cls._find_best_match(rgb)
    cls._rgb_to_attr[rgb] = attr
    return attr

  @classmethod
  def _set_up_colors(cls):
    for color_index in range(curses.COLORS):
      pair_index = color_index + 1
      if pair_index >= curses.COLOR_PAIRS: break
      curses.init_pair(pair_index, color_index, -1)
      cls._colors.append((cls._get_rgb_by_color_index(color_index),
                          curses.color_pair(pair_index)))
    cls._colors.sort()

  @classmethod
  def _find_best_match(cls, new_rgb):
    assert cls._is_valid_rgb(new_rgb)
    matched_attr = curses.color_pair(0) # white on black
    min_distance = cls._color_distance((0, 0, 0), (255, 255, 255))
    for rgb, attr in cls._colors:
      if rgb == cls._background_rgb: continue
      distance = cls._color_distance(new_rgb, rgb)
      if distance < min_distance:
        min_distance = distance
        matched_attr = attr
    return matched_attr

  @classmethod
  def _color_distance(cls, rgb1, rgb2):
    assert cls._is_valid_rgb(rgb1) and cls._is_valid_rgb(rgb2)
    return sum((color1 - color2) ** 2 for color1, color2 in zip(rgb1, rgb2))

  @staticmethod
  def _is_valid_rgb(rgb):
    return len(rgb) == 3 and all(isinstance(color, int) and 0 <= color < 256
                                 for color in rgb)

  @staticmethod
  def _get_rgb_by_color_index(color_index):
    return tuple((color * 255) // _CURSES_COLOR_SCALE
                 for color in curses.color_content(color_index))
