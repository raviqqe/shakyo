import console as cui


console = cui.Console()

try:
  console.initialize()
  console.erase()
  line = cui.Line()
  console.print_line(0, line)
  line = cui.Line(cui.Character("h"), cui.Character("e"))
  console.print_line(1, line)
  console.get_char()
finally:
  console.finalize()
