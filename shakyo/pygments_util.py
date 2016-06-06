import pygments
import pygments.lexers
import pygments.styles
import pygments.lexers.special

from .path_to_x import path_to_filename, path_to_text



# constants

_LEXER_OPTIONS = {"stripall" : True}
_FALLBACK_LEXER = pygments.lexers.special.TextLexer(**_LEXER_OPTIONS)



# functions

def guess_lexer(lexer_name=None, path=None):
  if lexer_name is not None:
    return pygments.lexers.get_lexer_by_name(lexer_name)
  return _guess_lexer_from_path(path)


def _guess_lexer_from_path(path):
  lexer = None

  filename = path_to_filename(path)
  if filename is not None:
    lexer = _guess_lexer_from_filename(filename)

  text = path_to_text(path)
  if text is not None and lexer is None:
    lexer = _guess_lexer_from_text(text)

  if lexer is None:
    lexer = _FALLBACK_LEXER

  return lexer


def _guess_lexer_from_filename(filename):
  try:
    return pygments.lexers.get_lexer_for_filename(filename, **_LEXER_OPTIONS)
  except pygments.util.ClassNotFound:
    return None


def _guess_lexer_from_text(text):
  try:
    return pygments.lexers.guess_lexer(text, **_LEXER_OPTIONS)
  except pygments.util.ClassNotFound:
    return None


def all_lexer_names():
  return {alias for _, aliases, _, _ in pygments.lexers.get_all_lexers()
          for alias in aliases}


def all_style_names():
  return pygments.styles.get_all_styles()
