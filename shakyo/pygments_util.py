import pygments
import pygments.lexers
import pygments.styles
import pygments.lexers.special



# constants

_LEXER_OPTIONS = {"stripall" : True}
_FALLBACK_LEXER = pygments.lexers.special.TextLexer(**_LEXER_OPTIONS)



# functions

def guess_lexer(lexer_name=None, filename=None, text=None):
  if lexer_name is not None:
    return pygments.lexers.get_lexer_by_name(lexer_name)
  else:
    return _guess_lexer_from_filename_and_text(filename, text)


def _guess_lexer_from_filename_and_text(filename, text):
  lexer = None
  if filename is not None:
    lexer = _guess_lexer_from_filename(filename)
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
