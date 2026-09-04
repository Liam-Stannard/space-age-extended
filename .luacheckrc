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

-- A `files` entry REPLACES the top-level `globals` list for the files it
-- matches, so every global a prototypes/ file touches has to be named here or
-- luacheck reports W113 and `luacheck .` (the lint workflow) exits non-zero.
-- `data` is assigned; the three circuit-connector names are only ever read, so
-- they go in `read_globals`. They are set by
-- core/lualib/circuit-connector-sprites.lua, which prototypes/entity.lua pulls
-- in with `require("circuit-connector-sprites")` -- the same spelling vanilla's
-- own turrets.lua uses -- for the Reactive Edge Plating connector.
files["prototypes/**/*.lua"] = {
  globals = { "data" },
  read_globals = {
    "circuit_connector_definitions",
    "universal_connector_template",
    "default_circuit_wire_max_distance",
  },
}
files["data.lua"] = { globals = { "data" } }
files["data-updates.lua"] = { globals = { "data" } }
files["data-final-fixes.lua"] = { globals = { "data" } }
files["control.lua"] = { globals = { "script", "defines", "game", "storage" } }
files["scripts/**/*.lua"] = { globals = { "script", "defines", "game", "storage" } }

max_line_length = false
