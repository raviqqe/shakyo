#!/usr/bin/env python

import sys

from . import consolekit as ck
from . import arggetter
from . import path_to_x
from . import pygments_util
from . import shakyo
from . import text_to_lines
from . import log



def get_example_lines(example_path,
                      console,
                      *,
                      lexer_name,
                      style_name,
                      colorize,
                      decorate):
  example_text = path_to_x.path_to_text(example_path)

  return text_to_lines.text_to_lines(
      example_text,
      console,
      lexer=pygments_util.guess_lexer(
          lexer_name=lexer_name,
          filename=path_to_x.path_to_filename(example_path),
          text=example_text),
      style_name=style_name,
      colorize=colorize,
      decorate=decorate)


def main():
  args = arggetter.get_args()

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
