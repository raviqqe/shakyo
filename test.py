import console as cui



try:
  console = cui.turn_on_console()
  console.erase()
  line = cui.Line()
  console.print_line(0, line)
  line = cui.Line(
      cui.Character("h", cui.ColorAttribute.black),
      cui.Character("e", cui.ColorAttribute.blue),
      cui.Character("l", cui.ColorAttribute.red),
      cui.Character("l", cui.ColorAttribute.green),
      cui.Character("o", cui.ColorAttribute.yellow),
      cui.Character(","),
      cui.Character("\t", cui.ColorAttribute.cyan
                          | cui.RenditionAttribute.reverse),
      cui.Character("w", cui.ColorAttribute.magenta),
      cui.Character("o", cui.ColorAttribute.white),
      cui.Character("r"),
      cui.Character("l", cui.ColorAttribute.white),
      cui.Character("d"),
      cui.Character("!", cui.ColorAttribute.white
                         | cui.RenditionAttribute.underline),
  )
  console.print_line(1, line)
  console.print_line(2, cui.Line(cui.Character("\t"),
                                 cui.Character(" "),
                                 cui.Character("A", cui.ColorAttribute.cyan)))
  console.get_char()
  with open("debug.log", "w") as f:
    for char in line:
      f.write(char.value)
    f.write("\n")
    for char in line.normalized:
      f.write(char.value)
finally:
  cui.turn_off_console()
