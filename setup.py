#!/usr/bin/env python

import os
import re
import setuptools
import shutil
import sys


def warn(*text):
  print("WARNING:", *text, file=sys.stderr)


if not ((sys.version_info.major >= 3 and sys.version_info.minor >= 5)
    or sys.version_info.major > 3):
  exit("Sorry, Python's version must be later than 3.5.")


PACKAGE_NAME = "shakyo"

with open("shakyo.py") as f:
  lines = f.readlines()
version = next(re.match(r"__version__\s*=\s*\"((\d|\.)*)\"", line)
               for line in lines if line.startswith("__version__")).group(1)


def read_text_file(filename):
  with open(os.path.join(os.path.dirname(__file__), filename)) as f:
    return f.read()

try:
  import pypandoc
  with open("README.rst", "w") as f:
    f.write(pypandoc.convert("README.md", "rst"))
  readme = read_text_file("README.rst")
except (ImportError, OSError) as e:
  os.remove("README.rst")
  warn(e)
  shutil.copyfile("README.md", "README")
  readme = read_text_file("README")


setuptools.setup(
    name=PACKAGE_NAME,
    version=version,
    description="a tool to learn about something just by copying it by hand",
    long_description=readme,
    license="Public Domain",
    author="raviqqe",
    author_email="raviqqe@gmail.com",
    url="http://github.com/raviqqe/shakyo/",
    py_modules=[PACKAGE_NAME],
    entry_points={"console_scripts" : ["shakyo=shakyo:main"]},
    install_requires=["text_unidecode", "validators"],
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
