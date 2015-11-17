import xorcise



try:
  console = xorcise.turn_on_console()
  console.erase()
  line = xorcise.Line()
  console.print_line(0, line)
  line = xorcise.Line(
      xorcise.Character("h", xorcise.ColorAttribute.black),
      xorcise.Character("e", xorcise.ColorAttribute.blue),
      xorcise.Character("l", xorcise.ColorAttribute.red),
      xorcise.Character("l", xorcise.ColorAttribute.green),
      xorcise.Character("o", xorcise.ColorAttribute.yellow),
      xorcise.Character(","),
      xorcise.Character("\t", xorcise.ColorAttribute.cyan
                          | xorcise.RenditionAttribute.reverse),
      xorcise.Character("w", xorcise.ColorAttribute.magenta),
      xorcise.Character("o", xorcise.ColorAttribute.white),
      xorcise.Character("r"),
      xorcise.Character("l", xorcise.ColorAttribute.white),
      xorcise.Character("d"),
      xorcise.Character("!", xorcise.ColorAttribute.white
                         | xorcise.RenditionAttribute.underline),
  )
  console.print_line(1, line)
  console.print_line(2, xorcise.Line(
      xorcise.Character("\t"),
      xorcise.Character(" "),
      xorcise.Character("A", xorcise.ColorAttribute.cyan)))
  console.get_char()
  with open("debug.log", "w") as f:
    for char in line:
      f.write(char.value)
    f.write("\n")
    for char in line.normalized:
      f.write(char.value)
finally:
  xorcise.turn_off_console()
