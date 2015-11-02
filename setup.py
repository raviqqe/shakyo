#!/usr/bin/env python

import setuptools
import sys

if not ((sys.version_info.major >= 3 and sys.version_info.minor >= 5)
    or sys.version_info.major > 3):
  exit("Sorry, Python's version must be later than 3.5.")

import shakyo


setuptools.setup(
    name=shakyo.__name__,
    version=shakyo.__version__,
    description="a tool to learn about something just by copying it by hand",
    license="Public Domain",
    author="raviqqe",
    author_email="raviqqe@gmail.com",
    url="http://github.com/raviqqe/shakyo/",
    scripts=[shakyo.__name__],
    install_requires=["text_unidecode", "validators"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console :: Curses",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: Public Domain",
        "Operating System :: POSIX",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "Topic :: Games/Entertainment",
    ],
)
