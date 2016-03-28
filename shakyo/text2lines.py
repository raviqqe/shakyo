import pygments.formatter
import pygments.styles

import consolekit as ck
from .util import *



# classes

class __LineFormatter(pygments.formatter.Formatter):
  """
  TODO: Follow Liskov substitution principle.
  """

  def __init__(self, style="default", colorize=True, decorate=True):
    super().__init__(style=style)

    self.__attrs = {}
    for token_type, properties in self.style:
      attr = ck.RenditionAttribute.normal
      if colorize and properties["color"]:
        attr |= ck.ColorAttribute.get_best_match(
                interpret_string_rgb(properties["color"]))
      if decorate and properties["bold"]:
        attr |= ck.RenditionAttribute.bold
      if decorate and properties["underline"]:
        attr |= ck.RenditionAttribute.underline
      self.__attrs[token_type] = attr

  def format(self, tokens):
    line = ck.Line()
    for token_type, string in tokens:
      while token_type not in self.__attrs:
        token_type = token_type.parent

      for char in string:
        if char == '\n':
          yield line
          line = ck.Line()
        elif ck.is_printable_char(char):
          line += ck.Character(char, self.__attrs[token_type])

    # if there is no newline character at the end of the last line
    if len(line) > 0:
      yield line



# functions

def text_to_lines(text,
                  lexer,
                  style_name="default",
                  colorize=True,
                  decorate=True):
  style = pygments.styles.get_style_by_name(style_name)
  return __LineFormatter(style=style, colorize=colorize, decorate=decorate) \
         .format(lexer.get_tokens(__strip_text(text)))


def __strip_text(text):
  return '\n'.join(line.rstrip() for line in text.split('\n'))
