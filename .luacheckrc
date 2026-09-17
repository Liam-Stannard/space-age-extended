std = "lua52"

-- The Lint workflow builds its own toolchain inside the workspace --
-- leafo/gh-actions-lua unpacks the interpreter into .lua/ and
-- gh-actions-luarocks puts LuaRocks and luacheck itself into .luarocks/ --
-- so a bare `luacheck .` in CI walks into both and reports on their sources
-- as if they were ours. They are third-party code we neither wrote nor can
-- fix, and they are not part of the mod; they are not checked.
exclude_files = {
  ".lua/**/*.lua",
  ".luarocks/**/*.lua",
}

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

-- Globals the engine hands the data stage, all of them read-only to us.
-- `kg` (a mass unit) and `util` come from core/lualib/util.lua; `table.deepcopy`
-- is the engine's addition to the standard `table`; the connector tables and
-- `pipecoverspictures` are side effects of the core lualib files that define
-- them, which the file using each one requires first.
local data_stage = {
  "kg",
  "util",
  "circuit_connector_definitions",
  "universal_connector_template",
  "pipecoverspictures",
  table = { fields = { "deepcopy" } },
}

-- And the ones the control stage gets: `remote` for the interfaces we register,
-- `rendering` for the objects we draw.
local control_stage = {
  "remote",
  "rendering",
}

files["prototypes/**/*.lua"] = { globals = { "data" }, read_globals = data_stage }
files["data.lua"] = { globals = { "data" }, read_globals = data_stage }
files["data-updates.lua"] = { globals = { "data" }, read_globals = data_stage }
files["data-final-fixes.lua"] = { globals = { "data" }, read_globals = data_stage }
files["control.lua"] = { globals = { "script", "defines", "game", "storage" }, read_globals = control_stage }
files["scripts/**/*.lua"] =
  { globals = { "script", "defines", "game", "storage" }, read_globals = control_stage }
-- Migration scripts run at the control stage too, on a save being loaded.
files["migrations/**/*.lua"] =
  { globals = { "script", "defines", "game", "storage" }, read_globals = control_stage }

max_line_length = false
