-- The map-gen seed harness. Driven by config.lua, which measure.py or rings.py
-- writes beside this file for each run: it returns, as a JSON string,
--   { mode = "server" | "rings", settings = <settings/core.json>, seeds = {...} }
--
-- Both modes measure a seed the same way (measure, below): a surface is made
-- from the planet's own map-gen settings with that seed, the chunks out to
-- `radius` tiles round the landing are generated, and then
--   * the nearest pool tile and the nearest shore tile (tile centre to the
--     landing), and how many pool tiles stand within the rule's `none_within`;
--   * the placed pool's bearing and whether the nearest pool tile is its;
--   * each starting patch: its centre (its reach and bearing expressions), the
--     entities of it within radius * 1.4 + 2 of that centre, how many of them
--     touch a pool or shore tile, strays of the same name elsewhere inside
--     `stray_radius`, and the nearest and centroid distance of what was placed.
--
-- mode "server": a headless server; measure.py sends /sae-measure-seed <seed>
-- over RCON and gets one JSON line back. The surface is deleted afterwards.
-- mode "rings": a client (rings.py, through launch.sh); each seed in turn is
-- measured, the rings in settings.shots are drawn round the landing with the
-- landing, the nearest pool tile and a caption marked, and the landing is
-- screenshot at each daytime. Everything lands in script-output/sae-measure-seeds/:
-- landing-<seed>-<daytime>.png, landing-<seed>.json, log.txt, errors.txt (only
-- if an error was caught) and `done`, on which the launcher stops the client.

-- luacheck: read globals helpers prototypes commands rcon rendering

local config = helpers.json_to_table(require("config"))
local S = config.settings

local OUT = "sae-measure-seeds/"
local START = 30   -- ticks after load before the first seed (rings mode)
local EVERY = 30   -- ticks between seeds (rings mode)

local function log(s)
  helpers.write_file(OUT .. "log.txt", s .. "\n", true)
end

-- A caught error: logged, and recorded in errors.txt so rings.py fails the run.
local function fail(what, err)
  local line = what .. " error: " .. tostring(err)
  log(line)
  helpers.write_file(OUT .. "errors.txt", line .. "\n", true)
end

local function round(v, places)
  if v == nil then return nil end
  local m = 10 ^ (places or 2)
  return math.floor(v * m + 0.5) / m
end

local made = 0
local function make_surface(seed)
  local mgs = prototypes.space_location[S.planet].map_gen_settings
  mgs.seed = seed
  -- Overrides, one level deep: {"autoplace_controls": {"sae-gas-vent": {...}}}
  -- replaces that one control and leaves the rest as the planet has them.
  for k, v in pairs(S.map_gen or {}) do
    if type(v) == "table" and type(mgs[k]) == "table" then
      for k2, v2 in pairs(v) do mgs[k][k2] = v2 end
    else
      mgs[k] = v
    end
  end
  made = made + 1
  local s = game.create_surface(string.format("sae-seed-%d-%d", seed, made), mgs)
  s.request_to_generate_chunks(S.landing, math.ceil(S.radius / 32))
  s.force_generate_chunk_requests()
  return s
end

-- A setting that is a number, or the name of a noise expression to read.
local function value(v, props)
  if type(v) == "number" then return v end
  return props[v][1]
end

-- The nearest tile of `name` (tile centre to the landing) inside the square of
-- half-side `radius`, and how many lie within `within`.
local function nearest_tile(s, name, within)
  local lx, ly = S.landing[1], S.landing[2]
  local r = S.radius
  local best, bx, by, inside = math.huge, nil, nil, 0
  for _, t in pairs(s.find_tiles_filtered{ area = { { lx - r, ly - r }, { lx + r, ly + r } }, name = name }) do
    local x, y = t.position.x + 0.5 - lx, t.position.y + 0.5 - ly
    local d = math.sqrt(x * x + y * y)
    if d < within then inside = inside + 1 end
    if d < best then best, bx, by = d, t.position.x + 0.5, t.position.y + 0.5 end
  end
  if not bx then return nil, nil, inside end
  return best, { round(bx, 1), round(by, 1) }, inside
end

local function measure_patch(s, p, props, field_bearing)
  local lx, ly = S.landing[1], S.landing[2]
  local r, b, radius = value(p.reach, props), value(p.bearing, props), value(p.radius, props)
  local cx, cy = lx + r * math.cos(b), ly + r * math.sin(b)
  local wet_tiles = { S.pool_tile, S.shore_tile }
  local count, wet, sx, sy, dmin, dmax = 0, 0, 0, 0, math.huge, 0
  for _, e in pairs(s.find_entities_filtered{ name = p.entity, position = { cx, cy }, radius = radius * 1.4 + 2 }) do
    count = count + 1
    if s.count_tiles_filtered{ area = e.bounding_box, name = wet_tiles } > 0 then wet = wet + 1 end
    local ex, ey = e.position.x - lx, e.position.y - ly
    sx, sy = sx + ex, sy + ey
    local d = math.sqrt(ex * ex + ey * ey)
    if d < dmin then dmin = d end
    if d > dmax then dmax = d end
  end
  local all = s.count_entities_filtered{ name = p.entity, position = S.landing, radius = S.stray_radius }
  local off = ((b - (field_bearing + 2 * math.pi * (p.turn or 0))) / (2 * math.pi) + 0.5) % 1 - 0.5
  local placed = count > 0 and (p.expect == nil or count == p.expect)
  return {
    key = p.key,
    entity = p.entity,
    reach = round(r, 2),
    bearing_deg = round(math.deg(b) % 360, 1),
    off_deg = round(off * 360, 1),
    centre = { round(cx, 1), round(cy, 1) },
    radius = round(radius, 2),
    n = count,
    wet = wet,
    stray = all - count,
    nearest = count > 0 and round(dmin, 2) or nil,
    farthest = count > 0 and round(dmax, 2) or nil,
    centroid = count > 0 and round(math.sqrt((sx / count) ^ 2 + (sy / count) ^ 2), 2) or nil,
    placed = placed,
    dry = placed and wet == 0
  }
end

local function measure(s, seed)
  local rule = S.rule
  local res = { seed = seed, planet = S.planet, landing = S.landing, radius = S.radius }
  local pool, pool_at, within = nearest_tile(s, S.pool_tile, rule.none_within)
  local shore, shore_at = nearest_tile(s, S.shore_tile, rule.none_within)
  res.pool = { nearest = pool and round(pool, 3), at = pool_at, tiles_within = within }
  res.shore = { nearest = shore and round(shore, 3), at = shore_at }

  local names, seen = {}, {}
  local function want(v)
    if type(v) == "string" and not seen[v] then
      seen[v] = true
      names[#names + 1] = v
    end
  end
  want(S.reference_bearing)
  for _, p in ipairs(S.patches) do
    want(p.reach); want(p.bearing); want(p.radius)
  end
  local props = s.calculate_tile_properties(names, { S.landing })
  local fb = S.reference_bearing and value(S.reference_bearing, props) or 0
  res.reference_bearing_deg = round(math.deg(fb) % 360, 1)

  if S.placed_pool then
    local pp = S.placed_pool
    local ok, got = pcall(s.calculate_tile_properties, { pp.bearing }, { S.landing })
    if ok then
      local b = got[pp.bearing][1]
      local cx, cy = S.landing[1] + pp.reach * math.cos(b), S.landing[2] + pp.reach * math.sin(b)
      res.placed_pool = {
        bearing_deg = round(math.deg(b) % 360, 1),
        off_eighths = round(((b - fb) / (2 * math.pi) * 8) % 8, 2),
        centre = { round(cx, 1), round(cy, 1) },
        area = s.count_tiles_filtered{ position = { cx, cy }, radius = pp.area_radius, name = S.pool_tile },
        nearest_is_placed = pool_at ~= nil
          and math.sqrt((pool_at[1] - cx) ^ 2 + (pool_at[2] - cy) ^ 2) < pp.near
      }
    else
      res.placed_pool = { error = tostring(got) }
    end
  end

  res.patches = {}
  local all_dry = true
  for _, p in ipairs(S.patches) do
    local m = measure_patch(s, p, props, fb)
    res.patches[#res.patches + 1] = m
    all_dry = all_dry and m.dry
  end

  res.pool_in_band = pool ~= nil and pool >= rule.nearest_min and pool <= rule.nearest_max
  res.none_within = within == 0 and (pool == nil or pool >= rule.none_within)
  res.patches_dry = all_dry
  res.pass = res.pool_in_band and res.none_within and all_dry
  return res
end

-- ------------------------------------------------------------ server mode

local function measure_command(c)
  local seed = tonumber(c.parameter or "")
  if not seed or seed < 0 or seed > 4294967295 or seed % 1 ~= 0 then
    rcon.print(helpers.table_to_json({ error = "bad seed: " .. tostring(c.parameter) }))
    return
  end
  local s
  local ok, res = pcall(function()
    s = make_surface(seed)
    return measure(s, seed)
  end)
  if s and s.valid then game.delete_surface(s) end
  if not ok then res = { seed = seed, error = tostring(res) } end
  rcon.print(helpers.table_to_json(res))
end

if config.mode == "server" then
  commands.add_command("sae-measure-seed", "Measure one map seed (seed harness).", measure_command)
  commands.add_command("sae-measure-ping", "Seed harness: ready?", function()
    local mods = {}
    for name, version in pairs(script.active_mods) do mods[#mods + 1] = name .. " " .. version end
    table.sort(mods)
    rcon.print(helpers.table_to_json({ ready = true, mods = mods }))
  end)
  commands.add_command("sae-measure-end", "Seed harness: end of a reply.", function()
    rcon.print("sae-measure-end")
  end)
end

-- ------------------------------------------------------------- rings mode

local function draw(s, res)
  local sh = S.shots
  local L = S.landing
  local white = { 1, 1, 1 }
  local function label(text, at, color, scale)
    rendering.draw_text{ text = text, surface = s, target = at, color = color, scale = scale,
      scale_with_zoom = true, alignment = "center", vertical_alignment = "bottom" }
  end
  for _, ring in ipairs(sh.rings) do
    rendering.draw_circle{ color = ring.color, radius = ring.radius, width = sh.ring_width, filled = false,
      target = L, surface = s }
    label(tostring(ring.radius), { L[1], L[2] - ring.radius - 0.5 }, ring.color, 5)
  end
  -- The landing: a cross.
  rendering.draw_line{ color = white, width = sh.ring_width / 2, from = { L[1] - 2, L[2] }, to = { L[1] + 2, L[2] },
    surface = s }
  rendering.draw_line{ color = white, width = sh.ring_width / 2, from = { L[1], L[2] - 2 }, to = { L[1], L[2] + 2 },
    surface = s }
  -- The nearest pool tile, and a line to it.
  if res.pool.at then
    local at = res.pool.at
    rendering.draw_line{ color = { 0.3, 1, 1 }, width = sh.ring_width / 2, from = L, to = at, surface = s,
      dash_length = 1, gap_length = 0.5 }
    rendering.draw_circle{ color = { 0.3, 1, 1 }, radius = 1, width = sh.ring_width / 2, filled = false,
      target = at, surface = s }
  end
  local half = sh.view_tiles / 2
  label(string.format("seed %d  nearest pool %s tiles", res.seed,
      res.pool.nearest and string.format("%.1f", res.pool.nearest) or "none"),
    { L[1], L[2] - half + 6 }, white, 6)
end

local function shoot(seed)
  local s = make_surface(seed)
  local res = measure(s, seed)
  helpers.write_file(string.format("%slanding-%d.json", OUT, seed), helpers.table_to_json(res))
  draw(s, res)
  local sh = S.shots
  local px = math.floor(sh.view_tiles * 32 * sh.zoom)
  for _, dt in ipairs(sh.daytimes) do
    game.take_screenshot{ surface = s, position = S.landing, resolution = { px, px }, zoom = sh.zoom,
      daytime = dt.daytime, show_entity_info = false, anti_alias = false, allow_in_replay = true,
      force_render = true, path = string.format("%slanding-%d-%s.png", OUT, seed, dt.name) }
  end
  log(string.format("seed %d: nearest pool %s, within %d: %d, patches dry: %s, %d px at zoom %g",
    seed, tostring(res.pool.nearest), S.rule.none_within, res.pool.tiles_within, tostring(res.patches_dry),
    px, sh.zoom))
end

if config.mode == "rings" then
  local t0
  local seeds = config.seeds or {}
  script.on_event(defines.events.on_tick, function(e)
    if not t0 then t0 = e.tick end
    local r = e.tick - t0
    local last = START + (#seeds - 1) * EVERY
    if r >= START and r <= last and (r - START) % EVERY == 0 then
      local seed = seeds[(r - START) / EVERY + 1]
      local ok, err = pcall(shoot, seed)
      if not ok then fail("seed " .. tostring(seed), err) end
    elseif r == last + 60 then
      game.set_wait_for_screenshots_to_finish()
    elseif r == last + 61 then
      helpers.write_file(OUT .. "done", "done\n")
    end
  end)
end
