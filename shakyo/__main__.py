#!/usr/bin/env python

import sys

from . import consolekit as ck
from . import arggetter
from . import path_to_x
from . import pygments_util
from . import shakyo
from . import text_to_lines
from . import log



# main routine

def main():
  args = arggetter.get_args()

  if not sys.stdout.isatty(): log.error("stdout is not a tty.")

  filename = path_to_x.path_to_filename(args.example_path)
  example_text = path_to_x.path_to_text(args.example_path)

  with ck.Console(asciize=args.asciize,
                  spaces_per_tab=args.spaces_per_tab,
                  background_rgb=args.background_rgb) as console:
    example_lines = text_to_lines.text_to_lines(
        example_text,
        console,
        lexer=pygments_util.guess_lexer(lexer_name=args.lexer_name,
                                        filename=filename,
                                        text=example_text),
        style_name=args.style_name,
        colorize=args.colorize,
        decorate=args.decorate)

    shakyo.Shakyo(console, example_lines).do()


if __name__ == "__main__":
  main()
