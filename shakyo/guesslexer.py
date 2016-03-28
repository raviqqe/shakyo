import pygments
import pygments.lexers
import pygments.lexers.special



# constants

LEXER_OPTIONS = {"stripall" : True}
FALLBACK_LEXER = pygments.lexers.special.TextLexer(**LEXER_OPTIONS)



# functions

def guess_lexer(lexer_name=None, filename=None, text=None):
  if lexer_name is not None:
    return pygments.lexers.get_lexer_by_name(lexer_name)
  else:
    return __guess_lexer_from_filename_and_text(filename, text)


def __guess_lexer_from_filename_and_text(filename, text):
  lexer = None
  if filename is not None:
    lexer = __guess_lexer_from_filename(filename)
  if text is not None and lexer is None:
    lexer = __guess_lexer_from_text(text)
  if lexer is None:
    lexer = FALLBACK_LEXER
  return lexer


def __guess_lexer_from_filename(filename):
  try:
    return pygments.lexers.get_lexer_for_filename(filename, **LEXER_OPTIONS)
  except pygments.util.ClassNotFound:
    return None


def __guess_lexer_from_text(text):
  try:
    return pygments.lexers.guess_lexer(text, **LEXER_OPTIONS)
  except pygments.util.ClassNotFound:
    return None
