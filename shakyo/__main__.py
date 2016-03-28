#!/usr/bin/env python

import sys

import arggetter
import consolekit as ck
import path2x
import pygments_util
import shakyo
import text2lines
import log



# main routine

def main():
  args = arggetter.get_args()

  if not sys.stdout.isatty(): log.error("stdout is not a tty.")

  filename = path2x.path_to_filename(args.example_path)
  example_text = path2x.path_to_text(args.example_path)

  try:
    # CAUTION:
    # You need to raise some Exception instead of calling exit() here
    # to prevent curses from messing up your terminal.

    console = ck.turn_on_console(asciize=args.asciize,
                                 spaces_per_tab=args.spaces_per_tab,
                                 background_rgb=args.background_rgb)

    example_lines = text2lines.text_to_lines(
        example_text,
        lexer=pygments_util.guess_lexer(lexer_name=args.lexer_name,
                                        filename=filename,
                                        text=example_text),
        style_name=args.style_name,
        colorize=args.colorize,
        decorate=args.decorate)

    shakyo.Shakyo(console, example_lines).do()
  except KeyboardInterrupt:
    pass
  finally:
    ck.turn_off_console()


if __name__ == "__main__":
  main()
