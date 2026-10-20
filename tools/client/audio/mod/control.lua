-- The sound-capture probe. Driven by config.lua, which
-- tools/client/audio/capture.py writes beside this file for each run: it
-- returns the spec as a JSON string (see capture.py's header for the fields).
--
-- On the planet's own surface (so its surface conditions hold) one copy of the
-- machine is built on a cleared patch, powered (a hidden pole and supply out of
-- the picture) and given its recipe but no ingredients: it stands idle, and the
-- engine draws no "no power" icon over it. The local player is put in god mode
-- on top of it at the spec's zoom with the GUI hidden, so the middle of the
-- client's window is the machine, and the listener is the machine too. Then,
-- by the game's clock (ticks after the probe's first tick):
--
--   START                 setup and camera
--   READY                 `ready` is written; capture.py starts recording
--   READY + each marker   a white square drawn for a few ticks beside the
--                         machine and a click played, on one tick: a picture
--                         and a sound the engine starts together, for
--                         capture.py to measure the recording chain's offset
--   READY + start_after   the ingredients go in: the machine starts
--   that + work_ticks     `enough` is written; capture.py stops recording
--
-- From the start, every 30 ticks the ingredients are topped up and the output
-- emptied, so the machine never stops for either; every 30 ticks a line of
-- status.jsonl records what the engine says of it. Everything lands in
-- script-output/sae-audio/; every error the probe catches is appended to
-- errors.txt, which fails the run.

-- luacheck: read globals helpers prototypes rendering remote

local spec = helpers.json_to_table(require("config"))

local OUT = "sae-audio/"
local START = 30

local function log(s)
  helpers.write_file(OUT .. "log.txt", s .. "\n", true)
end

local function fail(what, err)
  local line = what .. " error: " .. tostring(err)
  log(line)
  helpers.write_file(OUT .. "errors.txt", line .. "\n", true)
end

local function name_of(defs, value)
  for k, v in pairs(defs) do
    if v == value then return k end
  end
  return tostring(value)
end

local S = { t0 = nil }

local function ready_at() return START + (spec.ready_after or 120) end
local function start_at() return ready_at() + spec.start_after end

local function setup()
  local planet = game.planets[spec.planet or "nauvis"]
  local s = planet and (planet.surface or planet.create_surface()) or game.surfaces[spec.planet]
  S.surface = s
  local pole_offset = spec.pole_offset or 30
  s.request_to_generate_chunks({ 0, 0 }, 2)
  s.request_to_generate_chunks({ pole_offset, 0 }, 1)
  s.force_generate_chunk_requests()
  local r = spec.clear_radius or 20
  local area = { { -r, -r }, { pole_offset + 4, r } }
  for _, e in pairs(s.find_entities_filtered{ area = area }) do
    if e.valid and e.type ~= "character" then e.destroy() end
  end
  s.destroy_decoratives{ area = area }
  if spec.tile then
    local tiles = {}
    for x = -r, pole_offset + 3 do
      for y = -r, r - 1 do
        tiles[#tiles + 1] = { name = spec.tile, position = { x, y } }
      end
    end
    s.set_tiles(tiles)
  end
  -- A fixed light, so the picture does not change while it is recorded.
  s.freeze_daytime = true
  s.daytime = spec.daytime or 0

  local p = prototypes.entity[spec.entity]
  local pos = { (p.tile_width % 2) / 2, (p.tile_height % 2) / 2 }
  if spec.recipe then game.forces.player.recipes[spec.recipe].enabled = true end
  local e = s.create_entity{ name = spec.entity, position = pos, force = "player",
    create_build_effect_smoke = false }
  if not e then error("could not create " .. spec.entity) end
  S.entity = e
  if spec.recipe then e.set_recipe(spec.recipe) end
  S.pole = s.create_entity{ name = "sae-audio-pole", position = { pole_offset, 0 }, force = "player" }
  local per_tick = (spec.supply_kw or 10000) * 1000 / 60
  local ifc = s.create_entity{ name = "sae-audio-supply", position = { pole_offset + 1, 0 }, force = "player" }
  ifc.power_usage = 0
  ifc.power_production = per_tick
  ifc.electric_buffer_size = per_tick
  ifc.output_flow_limit = per_tick
  ifc.input_flow_limit = 0
  log(string.format("surface %s: %s at (%g, %g), recipe %s, powered (%g kW), no ingredients",
    s.name, spec.entity, e.position.x, e.position.y, tostring(spec.recipe), spec.supply_kw or 10000))
end

local function camera()
  local player = game.get_player(1)
  if not player then error("no player 1 to hold the camera") end
  player.set_controller{ type = defines.controllers.god }
  if not player.teleport(S.entity.position, S.surface) then error("could not move the camera") end
  player.zoom = spec.zoom or 1
  local v = player.game_view_settings
  for _, k in ipairs({ "show_controller_gui", "show_minimap", "show_research_info", "show_entity_info",
                       "show_alert_gui", "update_entity_selection", "show_side_menu", "show_pins_gui",
                       "show_entity_tooltip", "show_quickbar", "show_shortcut_bar", "show_crafting_queue",
                       "show_tool_bar", "show_hotkey_suggestions", "show_surface_list" }) do
    pcall(function() v[k] = false end)
  end
  player.game_view_settings = v
  log(string.format("camera: player 1 (god) at (%g, %g) on %s, zoom %g",
    player.position.x, player.position.y, player.surface.name, player.zoom))
end

local function feed()
  local e = S.entity
  if not (e and e.valid) then return end
  for _, it in ipairs(spec.items or {}) do
    local have = e.get_item_count(it.name)
    if have < it.count then e.insert{ name = it.name, count = it.count - have } end
  end
  local out = e.get_output_inventory()
  if out then out.clear() end
end

local function status(tick, what)
  local e = S.entity
  local row = { tick = tick, what = what }
  if e and e.valid then
    row.status = e.status and name_of(defines.entity_status, e.status) or "none"
    row.crafting_progress = e.crafting_progress
    row.products_finished = e.products_finished
    row.energy = e.energy
  end
  helpers.write_file(OUT .. "status.jsonl", helpers.table_to_json(row) .. "\n", true)
end

local function marker(tick, k)
  local m = spec.markers
  local o, size = m.offset, m.size or 2
  local p = S.entity.position
  rendering.draw_rectangle{ color = { 1, 1, 1, 1 }, filled = true, surface = S.surface,
    left_top = { p.x + o[1], p.y + o[2] }, right_bottom = { p.x + o[1] + size, p.y + o[2] + size },
    time_to_live = m.ticks_shown or 6 }
  game.play_sound{ path = m.sound or "utility/gui_click" }
  status(tick, "marker " .. k)
  log(string.format("marker %d on tick %d", k, tick))
end

-- Off the freeplay intro and crash site, so nothing takes the camera; the
-- remote interface is the scenario's own, and may not be there.
script.on_init(function()
  if remote.interfaces["freeplay"] then
    pcall(remote.call, "freeplay", "set_skip_intro", true)
    pcall(remote.call, "freeplay", "set_disable_crashsite", true)
  end
end)

local function step(tick, r)
  if r == START then
    setup()
    camera()
    status(tick, "built")
  elseif r == ready_at() then
    helpers.write_file(OUT .. "ready", helpers.table_to_json({ tick = tick }) .. "\n")
    status(tick, "ready")
  elseif r == start_at() then
    S.started = true
    feed()
    status(tick, "start")
    log(string.format("start: ingredients in on tick %d", tick))
  elseif r == start_at() + spec.work_ticks then
    status(tick, "enough")
    helpers.write_file(OUT .. "enough", helpers.table_to_json({ tick = tick }) .. "\n")
  end
  for k, at in ipairs(spec.markers.after_ready) do
    if r == ready_at() + at then marker(tick, k) end
  end
  if r > START and r % 30 == 0 then
    if S.started then feed() end
    status(tick, "tick")
  end
end

script.on_event(defines.events.on_tick, function(e)
  if S.failed then return end
  if not S.t0 then S.t0 = e.tick end
  local ok, err = pcall(step, e.tick, e.tick - S.t0)
  if not ok then
    S.failed = true
    fail("tick " .. (e.tick - S.t0), err)
  end
end)
