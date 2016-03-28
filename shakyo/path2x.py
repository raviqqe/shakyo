import os
import os.path
import sys
import urllib.parse
import urllib.request
import validators

from .log import *



# constants

_ENCODING = "UTF-8"
_SUPPORTED_SCHEMES = {"http", "https", "ftp"}
_TTY_DEVICE_FILE = "/dev/tty" # POSIX compliant



# functions

def _is_uri(uri):
  return validators.url(uri)


def _read_from_stdin():
  try:
    text = sys.stdin.read()
  except KeyboardInterrupt:
    error("Nothing could be read from stdin.")

  os.close(sys.stdin.fileno())
  sys.stdin = open(_TTY_DEVICE_FILE)

  return text


def _read_local_file(path):
  try:
    with open(path, "rb") as f:
      return f.read().decode(_ENCODING, "replace")
  except (FileNotFoundError, PermissionError) as e:
    error(e)


def _read_remote_file(uri):
  if urllib.parse.urlparse(uri).scheme not in _SUPPORTED_SCHEMES:
    error("Invalid scheme of URI is detected. "
              "(supported schemes: {})"
              .format(", ".join(sorted(_SUPPORTED_SCHEMES))))

  message("Loading a page...")
  try:
    with urllib.request.urlopen(uri) as response:
      return response.read().decode(_ENCODING, "replace")
  except urllib.error.URLError as e:
    error(e)


def _uri_to_filename(uri):
  return os.path.basename(urllib.parse.urlparse(uri).path)


def path_to_filename(path):
  if path is None:
    return None
  elif _is_uri(path):
    return _uri_to_filename(path)
  else:
    return os.path.basename(path)


def path_to_text(path):
  if path is None:
    return _read_from_stdin()
  elif _is_uri(path):
    return _read_remote_file(path)
  else:
    return _read_local_file(path)
