def interpret_string_rgb(string_rgb):
  assert len(string_rgb) == 6
  int_rgb = int(string_rgb, 16)
  return (int_rgb >> 16 & 0xff, int_rgb >> 8 & 0xff, int_rgb & 0xff)
