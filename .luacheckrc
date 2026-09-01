std = "lua52"

globals = {
  "data",
  "defines",
  "game",
  "script",
  "storage",
  "settings",
  "mods",
  "log",
  "table_size",
  "serpent",
}

files["prototypes/**/*.lua"] = { globals = { "data" } }
files["data.lua"] = { globals = { "data" } }
files["data-updates.lua"] = { globals = { "data" } }
files["data-final-fixes.lua"] = { globals = { "data" } }
files["control.lua"] = { globals = { "script", "defines", "game", "storage" } }
files["scripts/**/*.lua"] = { globals = { "script", "defines", "game", "storage" } }

max_line_length = false
