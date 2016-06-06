#!/usr/bin/env python

import sys

from . import consolekit as ck
from .get_args import get_args
from .path_to_x import path_to_text
from . import pygments_util
from . import shakyo
from .text_to_lines import text_to_lines
from . import log



def get_example_lines(example_path,
                      console,
                      *,
                      lexer_name,
                      style_name,
                      colorize,
                      decorate):
  return text_to_lines(
      path_to_text(example_path),
      console,
      lexer=pygments_util.guess_lexer(lexer_name=lexer_name,
                                      path=example_path),
      style_name=style_name,
      colorize=colorize,
      decorate=decorate)


def main():
  args = get_args()

  if not sys.stdout.isatty(): log.error("stdout is not a tty.")

  with ck.Console(asciize=args.asciize,
                  spaces_per_tab=args.spaces_per_tab,
                  background_rgb=args.background_rgb) as console:
    shakyo.Shakyo(console,
                  get_example_lines(args.example_path,
                                    console,
                                    lexer_name=args.lexer_name,
                                    style_name=args.style_name,
                                    colorize=args.colorize,
                                    decorate=args.decorate)).do()


if __name__ == "__main__":
  main()
