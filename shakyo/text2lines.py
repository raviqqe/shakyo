import pygments.formatter
import pygments.styles

import consolekit as ck
from . import util



# functions

def text_to_lines(text,
                  lexer,
                  style_name="default",
                  colorize=True,
                  decorate=True):
  style = pygments.styles.get_style_by_name(style_name)
  attrs = _create_attrs(style=style, colorize=colorize, decorate=decorate)
  return _tokens_to_lines(lexer.get_tokens(_strip_text(text)), attrs)


def _create_attrs(style="default", colorize=True, decorate=True):
  attrs = {}
  for token_type, properties \
      in pygments.formatter.Formatter(style=style).style:
    attr = ck.RenditionAttribute.normal
    if colorize and properties["color"]:
      attr |= ck.ColorAttribute.get_best_match(
              util.interpret_string_rgb(properties["color"]))
    if decorate and properties["bold"]:
      attr |= ck.RenditionAttribute.bold
    if decorate and properties["underline"]:
      attr |= ck.RenditionAttribute.underline
    attrs[token_type] = attr
  return attrs


def _tokens_to_lines(tokens, attrs):
  line = ck.Line()
  for token_type, string in tokens:
    while token_type not in attrs:
      token_type = token_type.parent

    for char in string:
      if char == '\n':
        yield line
        line = ck.Line()
      elif ck.is_printable_char(char):
        line += ck.Character(char, attrs[token_type])

  # if there is no newline character at the end of the last line
  if len(line) > 0:
    yield line


def _strip_text(text):
  return '\n'.join(line.rstrip() for line in text.split('\n'))
