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

-- Globals that core/lualib modules define when a prototypes/ file `require`s
-- them, rather than globals the engine hands us. They are read and never
-- assigned, so they belong in `read_globals`; without them `luacheck .` -- what
-- .github/workflows/lint.yml runs, bare -- reports W113 and exits non-zero.
-- tools/check-data-stage.sh cannot catch this, because the engine really does
-- define all of these at load time.
--
--   * `pipecoverspictures` from `require("__base__.prototypes.entity.pipecovers")`
--     (the Quench Turbine's fluid boxes).
--   * the three connector names from `require("circuit-connector-sprites")`,
--     the same spelling vanilla's own turrets.lua uses (Reactive Edge Plating).
--
-- Declared here AND repeated on the prototypes/ entry below: the top-level
-- declaration is what makes them visible, the repetition records where they
-- are actually used and survives the entry being narrowed later.
read_globals = {
  "pipecoverspictures",
  "circuit_connector_definitions",
  "universal_connector_template",
  "default_circuit_wire_max_distance",
}

files["prototypes/**/*.lua"] = {
  globals = { "data" },
  read_globals = {
    "pipecoverspictures",
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
