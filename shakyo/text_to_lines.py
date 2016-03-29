import pygments.formatter
import pygments.styles

from . import consolekit as ck
from . import util



# classes

class _AttrTable:
  def __init__(self, console, style="default", colorize=True, decorate=True):
    self._token_type_to_attr = {}
    for token_type, properties in self._style_to_token_properties(style):
      attr = console.decoration_attrs.normal
      if colorize and properties["color"]:
        attr |= console.color_attrs.get_best_match(
                util.interpret_string_rgb(properties["color"]))
      if decorate and properties["bold"]:
        attr |= console.decoration_attrs.bold
      if decorate and properties["underline"]:
        attr |= console.decoration_attrs.underline
      self._token_type_to_attr[token_type] = attr

  def __getitem__(self, token_type):
    while token_type not in self._token_type_to_attr:
      if token_type == token_type.parent:
        raise KeyError("Token type, {} is not found in attribute table."
                       .format(token_type))
      token_type = token_type.parent
    return self._token_type_to_attr[token_type]

  @staticmethod
  def _style_to_token_properties(style):
    return pygments.formatter.Formatter(style=style).style



# functions

def text_to_lines(text,
                  console,
                  lexer,
                  style_name="default",
                  colorize=True,
                  decorate=True):
  style = pygments.styles.get_style_by_name(style_name)
  attr_table = _AttrTable(console,
                          style=style,
                          colorize=colorize,
                          decorate=decorate)
  return _tokens_to_lines(lexer.get_tokens(_strip_text(text)), attr_table)


def _tokens_to_lines(tokens, attr_table):
  line = ck.Line()
  for token_type, string in tokens:
    for char in string:
      if char == '\n':
        yield line
        line = ck.Line()
      elif ck.is_printable_char(char):
        line += ck.Character(char, attr_table[token_type])

  # if there is no newline character at the end of the last line
  if len(line) > 0:
    yield line


def _strip_text(text):
  return '\n'.join(line.rstrip() for line in text.split('\n'))
