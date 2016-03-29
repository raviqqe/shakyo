#!/usr/bin/env python

import os
import re
import setuptools
import shutil
import sys

if not sys.version_info >= (3, 5):
  exit("Sorry, Python's version must be later than 3.5.")



# constants

COMMAND_NAME = "shakyo"
README_BASENAME = "README"
RST_EXT = "rst"
MD_EXT = "md"



# functions

def warn(*text):
  print("WARNING:", *text, file=sys.stderr)


def version():
  with open("shakyo/const.py") as f:
    lines = f.readlines()
  return next(re.match(r"_*VERSION\s*=\s*\"((\d|\.)*)\"", line)
              for line in lines if line.startswith("VERSION")).group(1)


def read_text_file(filename):
  with open(os.path.join(os.path.dirname(__file__), filename)) as f:
    return f.read()


def readme_text():
  readme_rst = README_BASENAME + "." + RST_EXT
  readme_md = README_BASENAME + "." + MD_EXT

  try:
    import pypandoc
    with open(readme_rst, "w") as f:
      f.write(pypandoc.convert(readme_md, RST_EXT))
    return read_text_file(readme_rst)
  except ImportError as e:
    if os.path.isfile(readme_rst):
      os.remove(readme_rst)
    warn(e)
    shutil.copyfile(readme_md, README_BASENAME)
    return read_text_file(README_BASENAME)



# main routine

def main():
  setuptools.setup(
      name=COMMAND_NAME,
      version=version(),
      description="a tool to learn about something just by typing it",
      long_description=readme_text(),
      license="Public Domain",
      author="raviqqe",
      author_email="raviqqe@gmail.com",
      url="http://github.com/raviqqe/shakyo/",
      packages=["shakyo", "shakyo.consolekit"],
      entry_points={
        "console_scripts" : [COMMAND_NAME + "=shakyo.__main__:main"]
      },
      install_requires=["pygments", "text_unidecode", "validators"],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: Console :: Curses",
          "Intended Audience :: Developers",
          "Intended Audience :: End Users/Desktop",
          "License :: Public Domain",
          "Operating System :: POSIX",
          "Programming Language :: Python :: 3.5",
          "Topic :: Education :: Computer Aided Instruction (CAI)",
          "Topic :: Games/Entertainment",
      ],
  )


if __name__ == "__main__":
  main()
