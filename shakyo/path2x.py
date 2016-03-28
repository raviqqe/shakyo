import os
import os.path
import sys
import urllib.parse
import urllib.request
import validators

import log



# constants

ENCODING = "UTF-8"
SUPPORTED_SCHEMES = {"http", "https", "ftp"}
TTY_DEVICE_FILE = "/dev/tty" # POSIX compliant



# functions

def __is_uri(uri):
  return validators.url(uri)


def __read_from_stdin():
  try:
    text = sys.stdin.read()
  except KeyboardInterrupt:
    log.error("Nothing could be read from stdin.")

  os.close(sys.stdin.fileno())
  sys.stdin = open(TTY_DEVICE_FILE)

  return text


def __read_local_file(path):
  try:
    with open(path, "rb") as f:
      return f.read().decode(ENCODING, "replace")
  except (FileNotFoundError, PermissionError) as e:
    log.error(e)


def __read_remote_file(uri):
  if urllib.parse.urlparse(uri).scheme not in SUPPORTED_SCHEMES:
    log.error("Invalid scheme of URI is detected. "
              "(supported schemes: {})"
              .format(", ".join(sorted(SUPPORTED_SCHEMES))))

  log.message("Loading a page...")
  try:
    with urllib.request.urlopen(uri) as response:
      return response.read().decode(ENCODING, "replace")
  except urllib.error.URLError as e:
    log.error(e)


def __uri_to_filename(uri):
  return os.path.basename(urllib.parse.urlparse(uri).path)


def path_to_filename(path):
  if path is None:
    return None
  elif __is_uri(path):
    return __uri_to_filename(path)
  else:
    return os.path.basename(path)


def path_to_text(path):
  if path is None:
    return __read_from_stdin()
  elif __is_uri(path):
    return __read_remote_file(path)
  else:
    return __read_local_file(path)
