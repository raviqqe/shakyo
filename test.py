import consolekit



try:
  console = consolekit.turn_on_console()
  console.erase()
  line = consolekit.Line()
  console.print_line(0, line)
  line = consolekit.Line(
      consolekit.Character("h", consolekit.ColorAttribute.get_best_match((0, 0, 0))),
      consolekit.Character("e", consolekit.ColorAttribute.get_best_match((0, 0, 255))),
      consolekit.Character("l", consolekit.ColorAttribute.get_best_match((255, 0, 0))),
      consolekit.Character("l", consolekit.ColorAttribute.get_best_match((0, 255, 0))),
      consolekit.Character("o", consolekit.ColorAttribute.get_best_match((255, 255, 0))),
      consolekit.Character(","),
      consolekit.Character("\t", consolekit.ColorAttribute.get_best_match((0, 255, 255))
                              | consolekit.RenditionAttribute.reverse),
      consolekit.Character("w", consolekit.ColorAttribute.get_best_match((255, 0, 255))),
      consolekit.Character("o", consolekit.ColorAttribute.get_best_match((255, 255, 255))),
      consolekit.Character("r"),
      consolekit.Character("l"),
      consolekit.Character("d"),
      consolekit.Character("!", consolekit.ColorAttribute.get_best_match((255, 255, 255))
                         | consolekit.RenditionAttribute.underline),
  )
  console.print_line(1, line)
  console.print_line(2, consolekit.Line(
      consolekit.Character("\t"),
      consolekit.Character(" "),
      consolekit.Character("A", consolekit.ColorAttribute.get_best_match((0, 255, 255)))))
  console.refresh()
  console.get_char()
  with open("debug.log", "w") as f:
    for char in line:
      f.write(char.value)
    f.write("\n")
    for char in line.normalized:
      f.write(char.value)
finally:
  consolekit.turn_off_console()
