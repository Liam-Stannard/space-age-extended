-- The screenshot probe. Driven by config.lua, which tools/client/shot/shot.sh
-- writes beside this file for each run: it returns the spec as a JSON string
-- (see shot.sh's header for the fields).
--
-- On the planet's own surface (so its surface properties, and the building's
-- surface conditions, hold), one copy of the entity is built per direction,
-- 100 tiles apart on a cleared patch. Each state in turn: build, fill, power
-- (a hidden pole and energy interface 30 tiles off, out of every frame),
-- refill every tick while it settles, then screenshot every direction at every
-- daytime and zoom in the same tick, record what the engine says of each copy,
-- and tear down before the next state. Everything lands in
-- script-output/sae-shot/: <state>/<direction>-<daytime>-<zoom>.png, a
-- <state>/state.json, log.txt, and `done` when the last screenshot is written.
-- Every error the probe catches is also appended to errors.txt; shot.sh fails
-- the run if that file has anything in it.

-- luacheck: read globals helpers prototypes remote

local spec = helpers.json_to_table(require("config"))

local OUT = "sae-shot/"
local SPACING = 100          -- between the copies, so no two share a pole's reach
local POLE_OFFSET = 30       -- the hidden pole and interface, out of frame
local START = 30             -- ticks after load before anything happens

local function log(s)
  helpers.write_file(OUT .. "log.txt", s .. "\n", true)
end

-- A caught error: logged, and recorded in errors.txt so the run fails.
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

local S = { t0 = nil, placed = {}, state = nil, plan = {} }

local function proto() return prototypes.entity[spec.entity] end

local function footprint(dir)
  local p = proto()
  local w, h = p.tile_width, p.tile_height
  if dir == "east" or dir == "west" then w, h = h, w end
  return w, h
end

local function origin(i) return { x = (i - 1) * SPACING, y = 0 } end

local function setup()
  local planet = game.planets[spec.planet or "nauvis"]
  local s
  if planet then
    s = planet.surface or planet.create_surface()
  else
    s = game.surfaces[spec.planet]
  end
  S.surface = s
  for i, _ in ipairs(spec.directions) do
    local o = origin(i)
    s.request_to_generate_chunks(o, 2)
    s.request_to_generate_chunks({ o.x + POLE_OFFSET, o.y }, 1)
  end
  s.force_generate_chunk_requests()
  local r = spec.clear_radius or 20
  for i, _ in ipairs(spec.directions) do
    local o = origin(i)
    local area = { { o.x - r, o.y - r }, { o.x + POLE_OFFSET + 4, o.y + r } }
    for _, e in pairs(s.find_entities_filtered{ area = area }) do
      if e.valid and e.type ~= "character" then e.destroy() end
    end
    s.destroy_decoratives{ area = area }
    if spec.tile then
      local tiles = {}
      for x = o.x - r, o.x + r - 1 do
        for y = o.y - r, o.y + r - 1 do
          tiles[#tiles + 1] = { name = spec.tile, position = { x, y } }
        end
      end
      s.set_tiles(tiles)
    end
  end
  log(string.format("surface %s (planet %s), %d directions, %d states",
    s.name, tostring(spec.planet), #spec.directions, #spec.states))
end

local function build(state)
  S.placed = {}
  for i, dir in ipairs(spec.directions) do
    local o = origin(i)
    local w, h = footprint(dir)
    local pos = { o.x + (w % 2) / 2, o.y + (h % 2) / 2 }
    local e = S.surface.create_entity{ name = spec.entity, position = pos, force = "player",
      direction = defines.direction[dir], create_build_effect_smoke = false }
    if not e then
      fail(state.name .. ": build", "could not create " .. spec.entity .. " facing " .. dir)
    else
      -- Recorded as placed at once, and the pole and interface on it as each is
      -- made, so a spec error further down (a bad recipe, item or fluid) still
      -- leaves everything built here to the teardown.
      local rec = { entity = e, dir = dir }
      S.placed[#S.placed + 1] = rec
      if state.recipe then e.set_recipe(state.recipe) end
      for _, it in ipairs(state.items or {}) do e.insert{ name = it.name, count = it.count } end
      for _, f in ipairs(state.fluids or {}) do e.insert_fluid{ name = f.name, amount = f.amount } end
      if state.power == "load" or state.power == "supply" then
        rec.pole = S.surface.create_entity{ name = "sae-shot-pole", position = { o.x + POLE_OFFSET, o.y },
          force = "player" }
        local which = state.power == "load" and "sae-shot-load" or "sae-shot-supply"
        rec.interface = S.surface.create_entity{ name = which, position = { o.x + POLE_OFFSET + 1, o.y },
          force = "player" }
        -- The buffer and flow limit are one tick's worth, so the interface
        -- draws (or gives) exactly its rate: a large empty buffer would draw
        -- the generator's full output while it fills, with no load set at all.
        local ifc = rec.interface
        if state.power == "load" then
          local per_tick = (state.load_kw or 0) * 1000 / 60
          ifc.power_production = 0
          ifc.power_usage = per_tick
          ifc.electric_buffer_size = math.max(per_tick, 1)
          ifc.input_flow_limit = per_tick
          ifc.output_flow_limit = 0
        else
          local per_tick = (state.supply_kw or 100000) * 1000 / 60
          ifc.power_usage = 0
          ifc.power_production = per_tick
          ifc.electric_buffer_size = math.max(per_tick, 1)
          ifc.output_flow_limit = per_tick
          ifc.input_flow_limit = 0
        end
      end
    end
  end
end

local function refill(state)
  if not state.refill then return end
  for _, rec in ipairs(S.placed) do
    if rec.entity.valid then
      for _, f in ipairs(state.fluids or {}) do rec.entity.insert_fluid{ name = f.name, amount = f.amount } end
    end
  end
end

local function record(rec)
  local e = rec.entity
  local r = { requested = rec.dir, actual = name_of(defines.direction, e.direction),
    position = e.position, status = e.status and name_of(defines.entity_status, e.status) or "none",
    fluids = e.get_fluid_contents() }
  if e.type == "generator" then
    r.generated_kw = e.energy_generated_last_tick * 60 / 1000
  end
  if rec.interface then
    r.interface_energy_mj = rec.interface.energy / 1e6
  end
  return r
end

local function shoot(state)
  local rows = {}
  for _, rec in ipairs(S.placed) do
    local e = rec.entity
    local w, h = footprint(rec.dir)
    local tiles = math.max(w, h) + 2 * (spec.margin or 3)
    local shift = spec.shift or { 0, 0 }
    for _, dt in ipairs(spec.daytimes) do
      for _, z in ipairs(spec.zooms) do
        local px = math.floor(tiles * 32 * z.zoom)
        game.take_screenshot{ surface = S.surface, position = { e.position.x + shift[1], e.position.y + shift[2] },
          resolution = { px, px }, zoom = z.zoom, daytime = dt.daytime, show_entity_info = false,
          anti_alias = false, allow_in_replay = true, force_render = true,
          path = string.format("%s%s/%s-%s-%s.png", OUT, state.name, rec.dir, dt.name, z.name) }
      end
    end
    rows[#rows + 1] = record(rec)
  end
  helpers.write_file(string.format("%s%s/state.json", OUT, state.name),
    helpers.table_to_json({ state = state, entity = spec.entity, copies = rows }))
  for _, r in ipairs(rows) do
    log(string.format("%s: %s (built %s) status %s%s", state.name, r.requested, r.actual, r.status,
      r.generated_kw and string.format(", generating %.1f kW", r.generated_kw) or ""))
  end
end

-- Motion: the same view a few ticks apart (spec.motion), for the parts that
-- move only in some states -- a generator's rotor turns only while it makes power.
local function motion(state, j)
  local m = spec.motion
  local dt, z
  for _, v in ipairs(spec.daytimes) do if v.name == m.daytime then dt = v end end
  for _, v in ipairs(spec.zooms) do if v.name == m.zoom then z = v end end
  if not dt or not z then
    fail(state.name .. ": motion", "no daytime " .. tostring(m.daytime) .. " or zoom " .. tostring(m.zoom))
    return
  end
  for _, rec in ipairs(S.placed) do
    local e = rec.entity
    local w, h = footprint(rec.dir)
    local px = math.floor((math.max(w, h) + 2 * (spec.margin or 3)) * 32 * z.zoom)
    local shift = spec.shift or { 0, 0 }
    game.take_screenshot{ surface = S.surface, position = { e.position.x + shift[1], e.position.y + shift[2] },
      resolution = { px, px }, zoom = z.zoom, daytime = dt.daytime, show_entity_info = false,
      anti_alias = false, allow_in_replay = true, force_render = true,
      path = string.format("%s%s/motion-%s-%d.png", OUT, state.name, rec.dir, j) }
  end
end

local function teardown()
  for _, rec in ipairs(S.placed) do
    for _, k in ipairs({ "entity", "pole", "interface" }) do
      if rec[k] and rec[k].valid then rec[k].destroy() end
    end
  end
  S.placed = {}
end

-- The timetable: setup, then for each state build at T, shoot at T + settle,
-- tear down two ticks later. A second after the last shots the game is told to
-- hold its next tick until every screenshot is on disk, and `done` (on which
-- the launcher stops the client) is written on that next tick, not before.
local function plan()
  local settle = spec.settle_ticks or 120
  local t = START + 10
  for k = 1, #spec.states do
    S.plan[#S.plan + 1] = { at = t, k = k, what = "build" }
    S.plan[#S.plan + 1] = { at = t + settle, k = k, what = "shoot" }
    local after = settle + 2
    if spec.motion then
      for j = 0, (spec.motion.frames or 2) - 1 do
        S.plan[#S.plan + 1] = { at = t + settle + 1 + j * (spec.motion.every or 6), k = k, what = "motion", j = j }
        after = settle + 2 + j * (spec.motion.every or 6)
      end
    end
    S.plan[#S.plan + 1] = { at = t + after, k = k, what = "teardown" }
    t = t + after + 3
  end
  S.plan[#S.plan + 1] = { at = t + 60, what = "flush" }
  S.plan[#S.plan + 1] = { at = t + 61, what = "done" }
end

local function run(what, k, j)
  local state = k and spec.states[k]
  if what == "build" then
    S.state = state
    S.refill_failed = false   -- a refill error is recorded once per state
    build(state)
  elseif what == "shoot" then
    shoot(state)
  elseif what == "motion" then
    motion(state, j)
  elseif what == "teardown" then
    teardown()
    S.state = nil
  elseif what == "flush" then
    game.set_wait_for_screenshots_to_finish()
  elseif what == "done" then
    helpers.write_file(OUT .. "done", "done\n")
  end
end

-- Off the freeplay intro and crash site, as the sound probe does: left on,
-- they take the camera and the client froze near tick 750 on any spec running
-- past ~700 ticks (Reaction Plant, 2026-10-20). The remote interface is the
-- scenario's own, and may not be there.
script.on_init(function()
  if remote.interfaces["freeplay"] then
    pcall(remote.call, "freeplay", "set_skip_intro", true)
    pcall(remote.call, "freeplay", "set_disable_crashsite", true)
  end
end)

script.on_event(defines.events.on_tick, function(e)
  if not S.t0 then
    S.t0 = e.tick
    plan()
  end
  local r = e.tick - S.t0
  if r == START then
    local ok, err = pcall(setup)
    if not ok then
      fail("setup", err)
      helpers.write_file(OUT .. "done", "setup failed\n")
    end
    return
  end
  if S.state then
    local ok, err = pcall(refill, S.state)
    if not ok and not S.refill_failed then
      S.refill_failed = true
      fail(S.state.name .. ": refill (recorded once per state)", err)
    end
  end
  for _, step in ipairs(S.plan) do
    if step.at == r then
      local ok, err = pcall(run, step.what, step.k, step.j)
      if not ok then
        fail((step.k and spec.states[step.k].name .. ": " or "") .. step.what, err)
      end
    end
  end
end)
