#!/usr/bin/env python

import setuptools
import shakyo


setuptools.setup(
    name=shakyo.__name__,
    version=shakyo.__version__,
    description="a tool to learn about something just by copying it by hand",
    author="raviqqe",
    author_email="raviqqe@gmail.com",
    url="http://github.com/raviqqe/shakyo/",
    packages=[shakyo.__name__]
    install_requires=["text_unidecode", "validators"])
