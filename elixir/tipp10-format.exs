#!/usr/bin/env elixir

# This script preprocesses text from stdin for use as a TIPP10 typing tutor
# lesson.

max_lines = 400
min_char_variety = 5
replacements = [{~r/[\t ]+/, " "},
		{~r/^ /, ""},
		{~r/ $/, ""}]

IO.stream()
|> Stream.map(fn s ->
  Enum.reduce(replacements, s,
    fn {regex, replacement}, s -> Regex.replace(regex, s, replacement) end)
end)
|> Stream.filter(fn s ->
  # add one to min_char_variety because of newline
  MapSet.size(MapSet.new(String.to_charlist(s))) >= (min_char_variety + 1)
end)
|> Stream.take(max_lines)
|> Enum.each(&IO.write/1)
