#!/usr/bin/env python

import setuptools
import shutil
import sys

if not ((sys.version_info.major >= 3 and sys.version_info.minor >= 5)
    or sys.version_info.major > 3):
  exit("Sorry, Python's version must be later than 3.5.")

import shakyo


try:
  import pypandoc
  with open("README.rst", "w") as f:
    f.write(pypandoc.convert("README.md", "rst"))
except ImportError:
  shutil.copyfile("README.md", "README")


setuptools.setup(
    name=shakyo.__name__,
    version=shakyo.__version__,
    description="a tool to learn about something just by copying it by hand",
    license="Public Domain",
    author="raviqqe",
    author_email="raviqqe@gmail.com",
    url="http://github.com/raviqqe/shakyo/",
    py_modules=[shakyo.__name__],
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
