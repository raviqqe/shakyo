import xorcise



try:
  console = xorcise.turn_on_console()
  console.erase()
  line = xorcise.Line()
  console.print_line(0, line)
  line = xorcise.Line(
      xorcise.Character("h", xorcise.ColorAttribute.get_best_match((0, 0, 0))),
      xorcise.Character("e", xorcise.ColorAttribute.get_best_match((0, 0, 255))),
      xorcise.Character("l", xorcise.ColorAttribute.get_best_match((255, 0, 0))),
      xorcise.Character("l", xorcise.ColorAttribute.get_best_match((0, 255, 0))),
      xorcise.Character("o", xorcise.ColorAttribute.get_best_match((255, 255, 0))),
      xorcise.Character(","),
      xorcise.Character("\t", xorcise.ColorAttribute.get_best_match((0, 255, 255))
                              | xorcise.RenditionAttribute.reverse),
      xorcise.Character("w", xorcise.ColorAttribute.get_best_match((255, 0, 255))),
      xorcise.Character("o", xorcise.ColorAttribute.get_best_match((255, 255, 255))),
      xorcise.Character("r"),
      xorcise.Character("l"),
      xorcise.Character("d"),
      xorcise.Character("!", xorcise.ColorAttribute.get_best_match((255, 255, 255))
                         | xorcise.RenditionAttribute.underline),
  )
  console.print_line(1, line)
  console.print_line(2, xorcise.Line(
      xorcise.Character("\t"),
      xorcise.Character(" "),
      xorcise.Character("A", xorcise.ColorAttribute.get_best_match((0, 255, 255)))))
  console.refresh()
  console.get_char()
  with open("debug.log", "w") as f:
    for char in line:
      f.write(char.value)
    f.write("\n")
    for char in line.normalized:
      f.write(char.value)
finally:
  xorcise.turn_off_console()
