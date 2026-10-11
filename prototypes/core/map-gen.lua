-- Terrain for the Core.
--
-- The elevation never dips below sea level, so the engine's own water never
-- places; the one liquid on the surface is the radiant solution, placed by a
-- rule of its own below.
--
-- Everything else here is the palette: the tiles the crust wears *and* the
-- climate that selects them, because a tile list on its own decides nothing.
-- Tiles choose themselves by temperature, moisture and aux, so naming a tile
-- that no point on the surface qualifies for simply means it never appears --
-- which is exactly how an earlier version of this file ended up all snow while
-- listing no snow at all. This palette was picked from some forty rendered on
-- the rig; their renders are under concept/planet-core/terrain, and their
-- definitions are in this file's history before the branch was tidied.
--
-- Map generation applies only to chunks that do not exist yet, so an existing
-- save keeps whatever terrain it was born with, and nothing you do here will
-- change ground you have already walked on.

-- Two sources, and they are not the same promise. The volcanic-* tiles ship
-- with Space Age (they are Vulcanus's ground) and are always there; the
-- mineral-*, frozen-snow-* and *-heat-* tiles come from Alien Biomes and are
-- there only when it is installed. Keeping them in separate lists means a
-- palette degrades to its Space Age half rather than to a guess -- and it
-- replaces the old "if fewer than half the names exist, assume the pack is
-- missing" heuristic, which could not tell an absent pack from a renamed tile.
--
-- Every name is still checked against data.raw before use: an optional
-- dependency that silently assumes its own presence is not optional.
--
-- The Alien Biomes names below were taken from the pack's own tile set. To
-- re-check them against an install, run this in-game:
--   /c local t = {} for n in pairs(prototypes.tile) do
--        if n:find("mineral") or n:find("volcanic") or n:find("frozen") then
--          t[#t+1] = n end end
--      table.sort(t) game.print(table.concat(t, " "))
--
-- Decoratives are not listed at all -- see core_decoratives() below, which asks
-- data.raw what exists rather than naming anything. To see what it selected,
-- standing on the Core:
--   /c local s = game.player.surface.map_gen_settings.autoplace_settings
--                    .decorative.settings
--      local t = {} for n in pairs(s) do t[#t+1] = n end
--      table.sort(t) game.print(#t .. ": " .. table.concat(t, " "))

-- A white crust, cold and pale, jointed by dark rims that glow arc-blue down
-- their middles, with blue heat seams and lakes of radiant solution in the low
-- ground. Rocks, shards and cliffs are the Core's own, in slate.
local palette =
{
  temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
  veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
  moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
  aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
  -- The jointed crust, lit: the joints are black dirt at their edges and the
  -- Core's own hot-crack tile down the middle, which glows at night in arc
  -- blue. Rims: a band either side of a noise threshold, so the dark -- and
  -- the glow down its middle -- rings the plates and leaves their interiors whole.
  dark        = { amount = 0.72, threshold = 0.45, width = 0.10, scale = 48, octaves = 2, persistence = 0.6, feather = { amplitude = 0.12, octaves = 2, persistence = 0.6, scale = 7 } },
  glow        = { gain = 3, cut = 1.2 },
  refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                  "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-black", "-rock-", "-rock" },
  cliff       = "sae-cliff-core",
  -- The basins hold radiant solution; the band above the waterline is the
  -- shore, in lit crust, so each body is ringed by the glow. Twelve units
  -- of the basin term is a ring about three tiles wide (four gave one).
  -- Level 76 is 6-30% solution over the rig's region by seed, 15% in the middle.
  pool        = { level = 76, shore = 12 },
  without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
  alien_tiles =
  {
    "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
    "mineral-white-sand-1", "mineral-white-sand-3",
    "mineral-black-dirt-1", "mineral-black-dirt-2",
    "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
  }
}

-- Alien Biomes' temperature scale is far wider than vanilla's -- its orange
-- heat tiles peak at 110, where vanilla's whole range stops well short of that.
-- The clamp keeps every palette inside the band the tiles actually cover, so a
-- tall amplitude buys rare extremes rather than ground no tile answers for.
local TEMPERATURE_RANGE = { -15, 125 }

local function noise(field, seed)
  return string.format(
    "multioctave_noise{x = x,\z
                       y = y,\z
                       seed0 = map_seed,\z
                       seed1 = %d,\z
                       octaves = %d,\z
                       persistence = %s,\z
                       input_scale = 1/%d,\z
                       output_scale = 1}",
    seed, field.octaves, field.persistence, field.scale)
end

-- The palette's `dark` term: a 0..1 mask laid onto the colour axis by
-- `amount`, so that inside it a different tile answers -- on the white cold
-- body, +0.72 lands on black dirt. The shape is rims: a band `width` either
-- side of `threshold` on a noise, so the dark rings the plates and leaves
-- their interiors whole. `feather` adds a short-wavelength noise before the
-- threshold, which breaks the rings into fingers instead of smooth loops --
-- most of what makes an edge read as ground rather than as a stencil.
-- (Hollows, cracks, Voronoi cells and plates, craters, basins and a distance
-- gradient were all rendered on the way here; they are in this file's history.)
local function dark_mask(dk)
  local n = noise(dk, dk.seed or 9931)
  if dk.feather then
    local f = dk.feather
    n = string.format("(%s + %s * %s)", n, f.amplitude, noise(f, f.seed or 9932))
  end
  return string.format("clamp((%s - abs(%s - %s)) / %s * 3, 0, 1)", dk.width, n, dk.threshold, dk.width)
end

-- Where the pool lies, as a 0..1 mask, so the crust's own shapes can stop at
-- the waterline: a liquid is not jointed.
local function pool_mask(pal)
  return string.format("clamp((%s - sae_core_basin) * 4, 0, 1)", pal.pool.level + pal.pool.shore)
end

local function clamped(field, seed, low, high)
  return string.format("clamp(%s + %s * %s, %s, %s)",
    field.centre, field.amplitude, noise(field, seed), low, high)
end

-- The colour axis: the body's noise, the dark rims laid on it (and stopped at
-- the waterline), and the seams' own colour. `veins.aux` shifts the axis along
-- the same contours the temperature spike follows, so a seam lands on a heat
-- colour the body's aux would never reach -- blue seams through white.
local function aux_expression(pal, seed)
  local base = string.format("%s + %s * %s", pal.aux.centre, pal.aux.amplitude, noise(pal.aux, seed))
  base = string.format("%s + %s * %s * (1 - %s)", base, pal.dark.amount, dark_mask(pal.dark), pool_mask(pal))
  local v = pal.veins
  base = string.format("%s + max(0, %s - abs(%s)) / %s * %s", base, v.width, noise(v, v.seed), v.width, v.aux)
  return string.format("clamp(%s, 0, 1)", base)
end

-- Temperature, with the hot veins added: along the zero contours of a second
-- noise, within `width` of the crossing, up to `gain` * `width` degrees are
-- laid on top -- so a cold crust still reaches the heat tiles' window along a
-- few thin seams.
local function temperature_expression(pal, seed, low, high)
  local base = string.format("%s + %s * %s", pal.temperature.centre,
    pal.temperature.amplitude, noise(pal.temperature, seed))
  local v = pal.veins
  base = string.format("%s + max(0, %s - abs(%s)) * %s", base, v.width, noise(v, v.seed), v.gain)
  return string.format("clamp(%s, %s, %s)", base, low, high)
end

data:extend({
  {
    -- Where the crust's lit cracks go: the dark rims, scaled so the glow tile
    -- beats every ground tile where the mask is strong and loses where it is
    -- weak -- so a joint is black dirt at its edges and lit down its centre.
    -- The floor is deep for the reason the pool's is (below); at -1.2 the glow
    -- tile won along the heat seams, where ground tiles go negative.
    type = "noise-expression",
    name = "sae_core_glow",
    expression = string.format("(%s + 8) * %s * (1 - %s) - %s - 8",
                               palette.glow.gain, dark_mask(palette.dark), pool_mask(palette), palette.glow.cut)
  },
  {
    -- Where the solution lies: a noise of its own, not the elevation's broad
    -- term. Tied to that term (520 tiles, then 320) the sea was one basin
    -- wider than the whole region the rig looks at, and the landing site came
    -- out under 0%, 45%, 72% or 98% solution by seed. At 160 tiles the pool is
    -- bodies -- lakes a hundred tiles across, several in any region -- and
    -- the share barely moves between seeds. The last term lifts the crust
    -- around the landing site, as Nauvis does, so nobody lands in the pool:
    -- the full lift out to 32 tiles, gone by 96.
    type = "noise-expression",
    name = "sae_core_basin",
    expression = "sae_core_basin_at{px = x, py = y, reach = distance}"
  },
  {
    -- The basin term at any point, not only the one being generated: the
    -- siderane vents' starting field (crust-tap.lua) reads it at the places it
    -- might stand, to keep its wells out of the pool. `reach` is the distance
    -- from spawn.
    type = "noise-function",
    name = "sae_core_basin_at",
    parameters = { "px", "py", "reach" },
    expression = "140 + 90 * multioctave_noise{x = px,\z
                                               y = py,\z
                                               seed0 = map_seed,\z
                                               seed1 = 8419,\z
                                               octaves = 3,\z
                                               persistence = 0.5,\z
                                               input_scale = 1/80,\z
                                               output_scale = 1}\z
                  + 40 * clamp((96 - reach) / 64, 0, 1)"
  },
  {
    -- The radiant pool fills the basins: below `level` on the basin term it
    -- beats every ground tile outright, and a `shore`-wide band above it is the
    -- buildable rim.
    --
    -- The floors are deep on purpose. The engine places the tile with the
    -- highest probability even when every probability is negative, and along
    -- the seams and joints every ground tile IS negative -- the temperature
    -- spike and the colour shift push them out of their windows. A floor of -1
    -- won there, and the sea came out jointed; measured with
    -- calculate_tile_properties, which said "pool" at none of 961 samples while
    -- 157 of them were pool.
    type = "noise-expression",
    name = "sae_core_pool",
    expression = string.format("clamp((%s - sae_core_basin) * 4, 0, 1) * 16 - 10", palette.pool.level)
  },
  {
    -- The shore has no ramp on its inner side: it holds 5 right down to the
    -- waterline and lets the pool's 6 take over below it. A ramp there gave
    -- the ground tiles the last tile before the liquid, and the sea was rimmed
    -- in white dirt with no lip drawn, since the ground art knows no pool.
    type = "noise-expression",
    name = "sae_core_shore",
    expression = string.format("clamp((%s - sae_core_basin) * 4, 0, 1) * 15 - 10",
                               palette.pool.level + palette.pool.shore)
  },
  {
    type = "noise-expression",
    name = "sae_core_temperature",
    expression = temperature_expression(palette, 2291, TEMPERATURE_RANGE[1], TEMPERATURE_RANGE[2])
  },
  {
    type = "noise-expression",
    name = "sae_core_moisture",
    -- Not water: on Alien Biomes' scale this is one of the axes a tile picks
    -- itself by, and the mineral grounds want the middle of it. Measured: at
    -- 0.06 -- the honest figure for a world where no water has ever been --
    -- nothing but snow qualified.
    expression = clamped(palette.moisture, 771, 0, 1)
  },
  {
    type = "noise-expression",
    name = "sae_core_aux",
    -- Aux is the axis the mineral grounds separate their colours along, so this
    -- is what decides grey against black against white within a palette.
    expression = aux_expression(palette, 5183)
  },
  {
    type = "noise-expression",
    name = "sae_core_elevation",
    -- Always well above zero: a crust with relief, and none of the engine's
    -- water anywhere. The solution has its own basin term above.
    --
    -- Two scales of relief. The first cut was one noise at 55 over a cliff
    -- interval of 40, which drew a cliff line every few hundred tiles and read
    -- as flat. A broad term now carries the big rises and falls, a finer one
    -- the local steps, and the cliff interval is tightened -- so the crust
    -- terraces, the way a fractured metal surface would.
    expression = "140 + 90 * multioctave_noise{x = x,\z
                                               y = y,\z
                                               seed0 = map_seed,\z
                                               seed1 = 8417,\z
                                               octaves = 3,\z
                                               persistence = 0.55,\z
                                               input_scale = 1/520,\z
                                               output_scale = 1}\z
                  + 35 * multioctave_noise{x = x,\z
                                           y = y,\z
                                           seed0 = map_seed,\z
                                           seed1 = 8418,\z
                                           octaves = 4,\z
                                           persistence = 0.6,\z
                                           input_scale = 1/140,\z
                                           output_scale = 1}"
  }
})

-- The starting area: how the landing gets its kamacite, helium-3 and melt.
--
-- The Core does it the way Space Age's planets do (Vulcanus's tungsten, coal,
-- calcite and sulfur; Aquilo's crude oil and brine): each starting resource is
-- one spot at a set distance and a seeded bearing from the landing, laid over
-- the resource's own patches with max() (resources.lua). Vanilla's starting
-- placement (`has_starting_area_placement`) cannot be used here, and the
-- resources no longer ask for it. It ranks its candidate spots with
-- `starting_resources_lake_mask`, which knows only elevation-water, and the
-- Core's elevation never comes near water: its liquid is the radiant pool,
-- from the basin term above. So on some seeds the spot it chose was in the
-- pool, whose tile refuses a resource outright, and the patch was simply not
-- there -- on the landing test save, all three of them.
--
-- Four things make up the starting area:
--   * the siderane field (crust-tap.lua): four wells 40 to 56 tiles out, at
--     the driest of sixteen bearings; that bearing is `sae_crust_vent_bearing`;
--   * kamacite ore and the helium-3 and kamacite vents (below), a quarter, a
--     half and three quarters of a turn round from the field, as Vulcanus
--     sets its starting spots at fixed angles from a seeded one;
--   * the landing lift in the basin term above, which keeps the pool out to
--     32 tiles and thins it out to 96, where these mostly stand;
--   * the boulders (resources.lua), scattered everywhere, which ignore all of
--     this.
--
-- A fixed angle alone would put a patch in the pool on some maps, as vanilla
-- did, so each patch may move. It tries 24 bearings, fifteen degrees apart,
-- on four rings -- its own distance, twelve tiles in, and sixteen and
-- thirty-two out -- and takes the best: any try whose centre and rim sit well
-- above the pool counts as dry, and among the dry ones the nearest its own
-- bearing and distance wins. On most maps that is the bearing and distance it
-- was given. Some landings are on a lake's edge, with dry ground in an arc a
-- third of the way round, so a patch keeps clear of the field and of the
-- patches chosen before it by distance rather than by angle: it may stand
-- beyond another on the same bearing, never within twelve tiles of its rim.
-- Helium-3 chooses first, because nothing on the Core starts without it, then
-- kamacite, then the kamacite vent. Whatever still reaches the pool or its
-- shore is cut tile by tile, as the siderane wells are, so no starting
-- resource ever stands on either.
--
-- Sizes are what vanilla's starting placement gave these resources on the
-- seeds where it worked, measured over twelve seeds:
--   * kamacite: 120 000 ore. That is vanilla's starting amount for
--     resources.lua's base_density 3 (20000 * base_density * (frequency + 1)),
--     laid as a cone of radius 9 -- vanilla's own starting radius for that
--     amount, (2 * amount) ^ (1/3) / 7. Measured: 37 000 to 166 000.
--   * helium-3 and kamacite vents: about eleven each (measured: 7 to 16), each
--     holding its `additional_richness` (60 000 and 150 000), as vanilla's
--     did. A vent's footprint, not the cone, is what limits how many fit, so
--     the radius is the one that gives that count: 3.5 for the 2x2 gas vent,
--     5.5 for the 3x3 kamacite vent.
-- Their distances, 56 to 72 tiles (44 to 104 if they have to move) plus the
-- radius, keep them inside 112: well within the engine's 150-tile starting
-- area, and mostly on lifted ground.
--
-- `turn` is the bearing each prefers, in turns round from the field's.
local STARTING_PATCHES =
{
  { key = "gas",           control = "sae-gas-vent",      turn = 2 / 4, reach = 56, radius = 3.5, per_vent = 60000 },
  { key = "kamacite",      control = "sae-kamacite-ore",  turn = 1 / 4, reach = 64, radius = 9,   amount = 120000 },
  { key = "kamacite_vent", control = "sae-kamacite-vent", turn = 3 / 4, reach = 72, radius = 5.5, per_vent = 150000 }
}
-- Bearings tried, all round from the siderane field's; the rings tried, in
-- tiles from each patch's own distance; and the clear ground, in tiles, a
-- patch keeps between its rim and the field's or an earlier patch's.
local STARTING_BEARINGS, STARTING_RINGS, STARTING_CLEAR = 24, { 0, -12, 16, 32 }, 12
-- The basin term above which a starting resource may stand: the pool and its
-- shore end at 88, and the siderane wells keep the same 92.
local STARTING_DRY = palette.pool.level + palette.pool.shore + 4
-- How a try is scored: its dryness counts up to DRY + 8 and no further, so
-- every comfortably dry try ties; then each fifteen degrees from its own
-- bearing costs a third of a point, and another ring costs five and a tenth
-- of a point a tile -- more than any bearing can, so a patch leaves its ring
-- only when the ring is wet, and then for the nearest ring that is not.
local STARTING_CAP, STARTING_TURN_COST, STARTING_RING_COST = STARTING_DRY + 8, 8, 5
-- How far a patch's rim may reach past its radius: the edge noise below.
local STARTING_WOBBLE = 1 / 6

data:extend({
  {
    -- How dry a starting spot would be: the basin term at its centre and at
    -- four points on its rim, whichever is lowest.
    type = "noise-function",
    name = "sae_core_start_dryness",
    parameters = { "px", "py", "r" },
    expression = "min(sae_core_basin_at{px = px,     py = py,     reach = (px * px + py * py) ^ 0.5},\z
                      sae_core_basin_at{px = px + r, py = py,     reach = ((px + r) ^ 2 + py * py) ^ 0.5},\z
                      sae_core_basin_at{px = px - r, py = py,     reach = ((px - r) ^ 2 + py * py) ^ 0.5},\z
                      sae_core_basin_at{px = px,     py = py + r, reach = (px * px + (py + r) ^ 2) ^ 0.5},\z
                      sae_core_basin_at{px = px,     py = py - r, reach = (px * px + (py - r) ^ 2) ^ 0.5})"
  }
})

do
  -- What a try keeps clear of: the centre of each thing already standing, as
  -- x and y expressions, and how far its rim reaches from that centre.
  local taken =
  {
    { x = "sae_crust_vent_reach * cos(sae_crust_vent_bearing)",
      y = "sae_crust_vent_reach * sin(sae_crust_vent_bearing)",
      extent = "sae_crust_vent_extent" }
  }

  for _, patch in ipairs(STARTING_PATCHES) do
    local prefix = "sae_core_start_" .. patch.key
    local size = string.format("var('control:%s:size')", patch.control)

    -- The bearing, in radians and measured as the siderane field's is, and
    -- the distance: the best-scoring try. A refused try scores a thousand
    -- below any real one.
    local locals, n = {}, 0
    for ring, offset in ipairs(STARTING_RINGS) do
      for k = 0, STARTING_BEARINGS - 1 do
        local a = string.format("(sae_crust_vent_bearing + 2 * pi * %d / %d)", k, STARTING_BEARINGS)
        local reach = patch.reach + offset
        local refused = {}
        for i, other in ipairs(taken) do
          refused[i] = string.format("((%d * cos(%s) - %s) ^ 2 + (%d * sin(%s) - %s) ^ 2 < (%s + %s) ^ 2)",
            reach, a, other.x, reach, a, other.y, other.extent, patch.radius * (1 + STARTING_WOBBLE) + STARTING_CLEAR)
        end
        -- How far, in turns, this try is from the patch's own bearing.
        local off = math.abs((k / STARTING_BEARINGS - patch.turn + 0.5) % 1 - 0.5)
        local cost = off * STARTING_TURN_COST + (ring > 1 and STARTING_RING_COST + math.abs(offset) / 10 or 0)
        locals["a" .. n] = a
        locals["r" .. n] = tostring(reach)
        locals["v" .. n] = string.format("min(%d, sae_core_start_dryness{px = %d * cos(%s), py = %d * sin(%s), r = %s})\z
                                          - %.4f - 1000 * min(1, %s)",
          STARTING_CAP, reach, a, reach, a, patch.radius + 2, cost, table.concat(refused, " + "))
        if n == 0 then
          locals.best0, locals.pa0, locals.pr0 = "v0", "a0", "r0"
        else
          locals["best" .. n] = string.format("max(best%d, v%d)", n - 1, n)
          locals["pa" .. n] = string.format("if(v%d > best%d, a%d, pa%d)", n, n - 1, n, n - 1)
          locals["pr" .. n] = string.format("if(v%d > best%d, r%d, pr%d)", n, n - 1, n, n - 1)
        end
        n = n + 1
      end
    end

    data:extend({
      {
        type = "noise-expression",
        name = prefix .. "_bearing",
        expression = "pa" .. (n - 1),
        local_expressions = locals
      },
      {
        type = "noise-expression",
        name = prefix .. "_reach",
        expression = "pr" .. (n - 1),
        local_expressions = locals
      },
      {
        -- The patch's shape: 1 at its centre falling to 0 at its rim, and 0
        -- everywhere else. A short noise on the distance roughens the edge,
        -- as vanilla's blob noise does, by up to a sixth of the radius: any
        -- more and a vent patch, a few tiles across, loses half its vents on
        -- some seeds. The size slider scales the radius as
        -- vanilla scales a starting patch (the cube root of its quantity), and
        -- at zero there is no patch at all.
        type = "noise-expression",
        name = prefix,
        expression = string.format("(%s > 0) * (sae_core_basin > %d)\z
                                    * clamp(1 - (d + wobble) / (%s * max(0.1, %s) ^ (1/3)), 0, 1)",
          size, STARTING_DRY, patch.radius, size),
        local_expressions =
        {
          b = prefix .. "_bearing",
          r = prefix .. "_reach",
          d = "((x - r * cos(b)) ^ 2 + (y - r * sin(b)) ^ 2) ^ 0.5",
          wobble = string.format("%s * multioctave_noise{x = x,\z
                                                         y = y,\z
                                                         seed0 = map_seed,\z
                                                         seed1 = 6203,\z
                                                         octaves = 2,\z
                                                         persistence = 0.5,\z
                                                         input_scale = 1/6,\z
                                                         output_scale = 1}", patch.radius * STARTING_WOBBLE)
        }
      },
      {
        -- What each tile of it holds. Ore is a cone, as vanilla's patches
        -- are, whose volume is the patch's amount; a vent holds the same as
        -- every other starting vent.
        type = "noise-expression",
        name = prefix .. "_richness",
        expression = patch.amount
          and string.format("var('control:%s:richness') * %.1f * max(0.1, %s) ^ (1/3) * %s",
                            patch.control, 3 * patch.amount / (math.pi * patch.radius ^ 2), size, prefix)
          or string.format("var('control:%s:richness') * %d", patch.control, patch.per_vent)
      }
    })

    taken[#taken + 1] =
    {
      x = string.format("%s_reach * cos(%s_bearing)", prefix, prefix),
      y = string.format("%s_reach * sin(%s_bearing)", prefix, prefix),
      extent = tostring(patch.radius * (1 + STARTING_WOBBLE))
    }
  end
end

local function core_tiles()
  local settings, found = {}, 0

  local function add(list)
    for _, name in pairs(list or {}) do
      if data.raw.tile[name] then
        settings[name] = {}
        found = found + 1
      end
    end
  end

  if mods["alien-biomes"] then
    add(palette.alien_tiles)
  else
    -- The palette leans on the pack, and says what it wears without it.
    add(palette.without_pack)
  end

  -- Only if the palette somehow contributed nothing at all: vanilla's Aquilo
  -- ground is the wrong colour for this place, but it is ground.
  if found == 0 then
    add({ "snow-flat", "snow-crests", "snow-lumpy", "snow-patchy",
          "ice-rough", "ice-smooth" })
  end

  -- The Core's own: the radiant pool, its shore, and the lit cracks.
  settings["sae-radiant-pool"] = {}
  settings["sae-radiant-shore"] = {}
  settings["sae-crust-glow-arc"] = {}

  return settings
end

-- Rock and mineral scatter.
--
-- Selected by name pattern rather than by list, because the decorative names
-- are the one part of an optional pack that cannot be checked from outside the
-- game -- and a list of guesses would fail silently, which is exactly the
-- failure this file has already had once. A pattern asks data.raw what exists
-- instead of telling it.
--
-- Two filters do the work beyond the patterns. Only decoratives that actually
-- carry an autoplace are enabled, since one without it would sit in the
-- settings doing nothing and inflate the count that reports success. And the
-- climate still has the final say: a decorative places only where its own
-- conditions are met, so listing the whole rock family gets only the ones
-- that suit a cold white crust. That is the same mechanism the tiles use, and
-- it is why this is safe to cast wide. The palette's `refuse` list keeps the
-- pack's coloured rocks off it all the same, since the Core has its own.
--
-- Decoratives only. The big rocks are simple-entities rather than decoratives,
-- and vanilla's are refused here on purpose: they yield stone and coal, and a
-- world whose whole point is that it has no carbon should not have coal lying
-- on the ground to be picked up. The Core has its own boulder instead --
-- sae-core-boulder, in resources.lua -- which is enabled through the entity
-- settings below, where an autoplaced entity belongs.
local DECORATIVE_WANTED =
{
  -- The Core's own shards first; the rest are the pack's, by family.
  "sae-crust",
  "rock", "stone", "pebble", "boulder", "gravel", "mineral", "crater", "pumice"
}

-- Nothing that ever lived. The Core has no organics at all, so a stray tuft of
-- grass would contradict the planet rather than decorate it -- and vanilla's
-- decorative names are not tidily separated by planet, so this list is what
-- keeps Nauvis and Gleba off the surface.
local DECORATIVE_REFUSED =
{
  "grass", "plant", "tree", "flower", "bush", "shrub", "fungus", "moss",
  "lichen", "weed", "garballo", "carpet", "leaf", "root", "vegetation",
  "water", "mud", "puddle", "oil", "scrap", "egg", "nest", "spawn"
}

local function matches_any(name, patterns)
  for _, pattern in pairs(patterns) do
    if string.find(name, pattern, 1, true) then return true end
  end
  return false
end

local function core_decoratives()
  local wanted, refused = {}, {}
  for _, pattern in pairs(DECORATIVE_WANTED) do wanted[#wanted + 1] = pattern end
  for _, pattern in pairs(DECORATIVE_REFUSED) do refused[#refused + 1] = pattern end
  for _, pattern in pairs(palette.refuse) do refused[#refused + 1] = pattern end

  local settings = {}
  -- 2.0 renamed the type: decoratives are `optimized-decorative` in data.raw.
  -- Under the old key this loop ran over nothing and the ground stayed bare.
  for name, decorative in pairs(data.raw["optimized-decorative"] or {}) do
    if decorative.autoplace
       and matches_any(name, wanted)
       and not matches_any(name, refused) then
      settings[name] = {}
    end
  end

  return settings
end

return function()
  return
  {
    property_expression_names =
    {
      elevation = "sae_core_elevation",
      temperature = "sae_core_temperature",
      moisture = "sae_core_moisture",
      aux = "sae_core_aux",
      cliffiness = "cliffiness_basic",
      cliff_elevation = "cliff_elevation_from_elevation"
    },
    -- Which cliff the cliffiness above places: the Core's own (tiles.lua),
    -- at an interval tightened from Nauvis's 40 so the crust terraces.
    cliff_settings =
    {
      name = palette.cliff,
      cliff_elevation_0 = 10,
      cliff_elevation_interval = 28,
      richness = 1
    },
    autoplace_controls =
    {
      ["sae-kamacite-ore"] = {},
      ["sae-kamacite-vent"] = {},
      ["sae-gas-vent"] = {},
      ["sae-crust-vent"] = {},
      ["sae-core-rock"] = {}
    },
    autoplace_settings =
    {
      ["tile"] = { settings = core_tiles() },
      ["decorative"] = { settings = core_decoratives() },
      ["entity"] =
      {
        settings =
        {
          ["sae-kamacite-ore"] = {},
          ["sae-kamacite-vent"] = {},
          ["sae-gas-vent"] = {},
          ["sae-crust-vent"] = {},
          ["sae-core-boulder"] = {}
        }
      }
    }
  }
end

