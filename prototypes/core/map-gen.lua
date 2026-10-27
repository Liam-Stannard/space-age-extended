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
  -- Without the pack: Aquilo's snow, placed by the Core's own expressions
  -- (FALLBACK_GROUND, below). Snow only: Space Age marks Aquilo's ice
  -- meltable, and nothing heated stands on it, the Gas Pump included.
  without_pack = { "snow-flat", "snow-crests", "snow-lumpy", "snow-patchy" },
  alien_tiles =
  {
    "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
    "mineral-white-sand-1", "mineral-white-sand-3",
    "mineral-black-dirt-1", "mineral-black-dirt-2",
    "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
  }
}

-- The ground without Alien Biomes: Aquilo's four snow tiles, chosen per tile
-- by expressions of the Core's own rather than the ones they ship with.
--
-- Aquilo's own expressions do not carry over. Each adds the surface elevation
-- (snow + elevation / 25, ice - elevation / 10) and 100 for any elevation
-- above 1.5, and the Core's elevation runs 20 to 270: every snow tile came out
-- near +105, far above the pool's 6, the shore's 5 and the glow's 1.8, so all
-- three vanished, and ice never won. So each tile keeps Aquilo's selector --
-- its place on Aquilo's two short noises, `aquilo_snow_ice` (12 tiles, snow
-- low, ice high) and `aquilo_tile_variant` (6 tiles), as in
-- planet-aquilo-map-gen.lua -- and drops the elevation.
--
-- **Snow only** (Liam, 2026-10-27: "Change fallback ground", "Snow only").
-- Aquilo's ice-rough and ice-smooth are gone from it: Space Age marks them
-- meltable, which refuses every heated building, so a Gas Pump could not
-- stand on a vent that came up on ice (4 of 15 near one landing). The snow
-- tiles take the ground the ice held by their own selectors, unchanged, and
-- where a snow tile already won it still does. The ice held the high end of
-- the snow-ice axis, where every snow selector falls by one a unit and the
-- variant alone orders them, so most of it is now snow-crests (variant above
-- -0.2) and snow-lumpy (below). Measured over 30 seeds (T13c, 2026-10-27):
-- the ice was a quarter of the ground; 45 % of it went to snow-crests, 52 %
-- to snow-lumpy, 3 % to snow-patchy, and no vent stands on a meltable tile.
--
-- Two of the Core's own terms go in. The dark rims (`dark`, above) push the
-- snow-ice axis up by `rim`, so a joint is the high end's snow at its edges
-- and lit down its middle, as it is black dirt with the pack. And whichever
-- tile wins answers at exactly `level`: each is its selector less the best
-- selector at that point.
-- The level is what the volcanic tiles this replaces answered at, the highest
-- of their three expressions, so the pool and the shore, which are drawn
-- against the ground, stand where they stood on the volcanic ground (30 seeds,
-- 2026-10-20: the pool tile for tile; the shore so too, but for the few outer
-- tiles Vulcanus's noise used to give the lit cracks, tiles.lua). It reads
-- Vulcanus's noise for that level alone; which tile wins is the selectors'.
local FALLBACK_GROUND =
{
  level = "max(volcanic_ash_dark_range, volcanic_ash_flats_range, volcanic_cracks_cold_range)",
  rim = 2,
  selectors =
  {
    ["snow-flat"]   = "1 - (s + 0.5) - abs(v - 0.5)",
    ["snow-crests"] = "1.2 - abs(s - 0.2) - abs(v - 0.2)",
    ["snow-lumpy"]  = "1.2 - abs(s + 0.1) - abs(v + 0.3)",
    -- Aquilo's is 1 - ...; at 1 it held 4.0 % of the ground on one seed in 30.
    ["snow-patchy"] = "1.1 - abs(s + 0.4) - abs(v + 0.6)"
  }
}

-- Alien Biomes' temperature scale is far wider than vanilla's -- its orange
-- heat tiles peak at 110, where vanilla's whole range stops well short of that.
-- The clamp keeps every palette inside the band the tiles actually cover, so a
-- tall amplitude buys rare extremes rather than ground no tile answers for.
local TEMPERATURE_RANGE = { -15, 125 }

-- The landing's own pool, and the clearing round the landing.
--
-- Left to the basin noise, the nearest solution was anywhere from inside the
-- landing to none within 90 tiles (30 seeds: median 75, four under 24 tiles,
-- twelve with none inside 90), and easing the landing lift moved the median
-- but not the spread. So, as the starting resources are, the first pool is
-- placed: one basin, its near shore `near` tiles out and its edge `radius`
-- tiles from its centre -- about 450 tiles of solution, a small pool beside
-- the lakes the noise makes -- roughened by up to `wobble` tiles either way.
-- The basin term falls `slope` units a tile into it, about as steeply as the
-- noise's own basins fall at their shores (measured on five seeds: a median
-- of 0.8 to 1.5 a tile), so its shore is as wide as theirs, eight tiles or so.
--
-- And the clearing: inside it the noise's basins cannot reach the pool level
-- whatever the noise, so the nearest solution on every map is 42 to 48 tiles
-- out, give or take the tile it lands on (120 seeds: 41.5 to 48.9) -- the
-- placed pool, or now and then a lake the clearing has cut back -- and nothing
-- is ever within 24. It is a floor under the basin term, falling at the same
-- slope, so a lake it cuts back keeps a shore of the same width; the placed
-- pool is laid on after it and is not cut. Its least reach is `clearing`
-- tiles, a tile short of the pool's near shore, and no less: the tiles the
-- engine lays can stand a tile or two off the noise at a ragged edge (10 of
-- 14 400 tiles round one landing), and a least of 42 brought a lake to 40.2
-- tiles on one seed in 120.
--
-- A clearing of one radius cut its lakes along a circle: on about one map in
-- ten the nearest lake ended in a round headland about the landing, which
-- read as a stencil. So its edge wanders, as a shore does. It reaches up to
-- `sweep` tiles further on a noise of the bearing alone -- a few long swells
-- round the landing -- and up to `drift` further on a noise of the ground,
-- a swell every `drift_scale` tiles or so; both are clamped, so the least
-- holds on every seed. Measured over 120 seeds as the widest stretch of the
-- nearest lake's edge, 60 degrees round, that stays within 3 tiles of one
-- distance from the landing: 12 landings in 34 had one with a single radius,
-- none do now, and 1 in 34 points far out, where the noise is untouched, has one.
--
-- Nor is the floor where most lakes stop. A gentler lift, rising to `soft`
-- units a tile, starts `soft_reach` tiles beyond the clearing's edge and
-- steepens over `soft_onset` tiles, so a lake that comes near is mostly bent
-- back along its own contours and only the deepest reach the floor. Where one
-- does, noise and floor are blended over `blend` units of the basin term
-- rather than meeting in a crease, and so are the placed pool and the ground
-- it is laid into (`join`), where a crease drew a sharp tooth of crust into
-- the lake. That blend lowers the basin by at most a quarter of `join`, which
-- keeps the pool's near shore within half a tile of where it was.
local LANDING =
{
  near = 45, radius = 12, wobble = 3, slope = 1.5,
  clearing = 44, sweep = 10, drift = 10, drift_scale = 24,
  circle = 3, soft = 1, soft_reach = 24, soft_onset = 16, blend = 18, join = 8
}
-- Where the placed pool's centre stands.
LANDING.reach = LANDING.near + LANDING.radius

-- The climate's ground, warped. The axes above are broad on purpose -- a
-- palette is chosen over hundreds of tiles -- but the pack's tiles split along
-- their contours, so where one runs straight the ground does too. A heat seam
-- worst of all: across it the temperature climbs some 14 degrees a tile, far
-- more than the pack's own tile noise moves, so its two heat tiles part down
-- its length, and one lying along a row parted in a straight line 82 tiles
-- long (30 seeds, 2026-10-20; the old lit cracks had hidden it). So, with the
-- pack, the climate is read at a point moved up to `amplitude` tiles by a
-- short noise of `scale` tiles: every edge it draws wanders, and none moves
-- further than that. The dark rims are not warped: the glow reads them too.
-- Without the pack the climate decides no tile, and is left as it is.
local CLIMATE_WARP = mods["alien-biomes"] and { amplitude = 3, scale = 10, octaves = 2, persistence = 0.5 }

local function noise(field, seed, warped)
  local x, y = "x", "y"
  if warped and CLIMATE_WARP then
    x, y = "x + sae_core_climate_warp_x", "y + sae_core_climate_warp_y"
  end
  return string.format(
    "multioctave_noise{x = %s,\z
                       y = %s,\z
                       seed0 = map_seed,\z
                       seed1 = %d,\z
                       octaves = %d,\z
                       persistence = %s,\z
                       input_scale = 1/%d,\z
                       output_scale = 1}",
    x, y, seed, field.octaves, field.persistence, field.scale)
end

if CLIMATE_WARP then
  for axis, seed in pairs({ x = 4483, y = 4489 }) do
    data:extend({
      {
        type = "noise-expression",
        name = "sae_core_climate_warp_" .. axis,
        expression = string.format("%g * clamp(%s, -1, 1)", CLIMATE_WARP.amplitude, noise(CLIMATE_WARP, seed))
      }
    })
  end
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
    field.centre, field.amplitude, noise(field, seed, true), low, high)
end

-- The colour axis: the body's noise, the dark rims laid on it (and stopped at
-- the waterline), and the seams' own colour. `veins.aux` shifts the axis along
-- the same contours the temperature spike follows, so a seam lands on a heat
-- colour the body's aux would never reach -- blue seams through white.
local function aux_expression(pal, seed)
  local base = string.format("%s + %s * %s", pal.aux.centre, pal.aux.amplitude, noise(pal.aux, seed, true))
  base = string.format("%s + %s * %s * (1 - %s)", base, pal.dark.amount, dark_mask(pal.dark), pool_mask(pal))
  local v = pal.veins
  base = string.format("%s + max(0, %s - abs(%s)) / %s * %s", base, v.width, noise(v, v.seed, true), v.width, v.aux)
  return string.format("clamp(%s, 0, 1)", base)
end

-- Temperature, with the hot veins added: along the zero contours of a second
-- noise, within `width` of the crossing, up to `gain` * `width` degrees are
-- laid on top -- so a cold crust still reaches the heat tiles' window along a
-- few thin seams.
local function temperature_expression(pal, seed, low, high)
  local base = string.format("%s + %s * %s", pal.temperature.centre,
    pal.temperature.amplitude, noise(pal.temperature, seed, true))
  local v = pal.veins
  base = string.format("%s + max(0, %s - abs(%s)) * %s", base, v.width, noise(v, v.seed, true), v.gain)
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
    -- the share barely moves between seeds. Round the landing the clearing
    -- holds the noise's basins off, and the landing's own pool is laid in
    -- beyond it (LANDING, above).
    type = "noise-expression",
    name = "sae_core_basin",
    expression = "sae_core_basin_full_at{px = x, py = y, reach = distance}"
  },
  {
    -- The noise's basins at any point, not only the one being generated, with
    -- the clearing round the landing but without the placed pool: the siderane
    -- vents' starting field (crust-tap.lua) reads it at the places it might
    -- stand, to keep its wells out of the pool, and the placed pool takes its
    -- bearing from the field's, so the field cannot read the pool itself. It
    -- stands an eighth of a turn from the field and is no risk to it.
    -- `reach` is the distance from spawn.
    --
    -- The noise's own term carries two lifts. The first lifts the crust round
    -- the landing, as Nauvis does: the full lift out to 32 tiles, gone by 96.
    -- It is what keeps the starting patches, 44 to 104 tiles out, mostly on
    -- dry ground. The second is the clearing's gentler lift (LANDING, above).
    -- The floor is the clearing itself, and the two meet in a smooth maximum,
    -- never below either, which only rounds the crease where they cross.
    type = "noise-function",
    name = "sae_core_basin_at",
    parameters = { "px", "py", "reach" },
    expression = string.format("max(noise, floor) + max(0, %g - abs(noise - floor)) ^ 2 / %g",
                               LANDING.blend, 4 * LANDING.blend),
    local_expressions =
    {
      noise = "140 + 90 * multioctave_noise{x = px,\z
                                            y = py,\z
                                            seed0 = map_seed,\z
                                            seed1 = 8419,\z
                                            octaves = 3,\z
                                            persistence = 0.5,\z
                                            input_scale = 1/80,\z
                                            output_scale = 1}\z
               + 40 * clamp((96 - reach) / 64, 0, 1)\z
               + soft",
      soft = string.format("%g * (clamp(u, 0, 1) ^ 2 / 2 + max(0, u - 1))", LANDING.soft * LANDING.soft_onset),
      u = string.format("(clear + %g - reach) / %g", LANDING.soft_reach, LANDING.soft_onset),
      clear = "sae_core_clearing_at{px = px, py = py, reach = reach}",
      floor = string.format("%d + %g * (clear - reach)",
                            palette.pool.level, LANDING.slope)
    }
  },
  {
    -- How far the clearing reaches at a point: `clearing` tiles at the least,
    -- up to `sweep` further by the bearing and up to `drift` further by the
    -- ground (LANDING, above). The bearing's noise is read on a circle
    -- `circle` units across in the noise's own space, off the lattice's
    -- origin, so it varies only with the bearing, swells a few times round,
    -- and joins up all the way round.
    type = "noise-function",
    name = "sae_core_clearing_at",
    parameters = { "px", "py", "reach" },
    expression = string.format("%d\z
                                + %g * (1 + clamp(multioctave_noise{x = %g * px / max(1, reach) + 0.37,\z
                                                                    y = %g * py / max(1, reach) + 0.61,\z
                                                                    seed0 = map_seed,\z
                                                                    seed1 = 8425,\z
                                                                    octaves = 2,\z
                                                                    persistence = 0.5,\z
                                                                    input_scale = 1,\z
                                                                    output_scale = 1}, -1, 1))\z
                                + %g * (1 + clamp(multioctave_noise{x = px,\z
                                                                    y = py,\z
                                                                    seed0 = map_seed,\z
                                                                    seed1 = 8427,\z
                                                                    octaves = 2,\z
                                                                    persistence = 0.5,\z
                                                                    input_scale = 1/%d,\z
                                                                    output_scale = 1}, -1, 1))",
      LANDING.clearing, LANDING.sweep / 2, LANDING.circle / 2, LANDING.circle / 2, LANDING.drift / 2, LANDING.drift_scale)
  },
  {
    -- A roughening for the placed pool's edge, -1 to 1: a short noise,
    -- clamped so the edge moves no more than `wobble` tiles.
    -- Short enough to vary several times round a pool this size: at 16 tiles
    -- it barely moved round it, and the pool came out an octagon.
    type = "noise-function",
    name = "sae_core_edge_at",
    parameters = { "px", "py" },
    expression = "clamp(multioctave_noise{x = px,\z
                                          y = py,\z
                                          seed0 = map_seed,\z
                                          seed1 = 8421,\z
                                          octaves = 3,\z
                                          persistence = 0.6,\z
                                          input_scale = 1/8,\z
                                          output_scale = 1}, -1, 1)"
  },
  {
    -- The placed pool's bearing, in radians and measured as the siderane
    -- field's is. The field and the three starting patches prefer the four
    -- quarter-turns from the field's bearing (STARTING_PATCHES, below), so the
    -- pool takes one of the four eighths between them: never nearer than an
    -- eighth of a turn to any of them, which at their distances leaves at
    -- least six tiles between the field's wells and the ground they would
    -- refuse round the pool, and ten for a patch's rim. Of the four it takes the lowest
    -- ground, where the noise's own basins already run: there it reads as
    -- part of the terrain, and the higher ground is left for a patch that has
    -- to move.
    type = "noise-expression",
    name = "sae_core_landing_pool_bearing",
    expression = "pick3",
    local_expressions = (function()
      local locals = {}
      for k = 0, 3 do
        local a = string.format("(sae_crust_vent_bearing + 2 * pi * %d / 8)", 2 * k + 1)
        locals["v" .. k] = string.format("sae_core_basin_at{px = %d * cos(%s), py = %d * sin(%s), reach = %d}",
          LANDING.reach, a, LANDING.reach, a, LANDING.reach)
        if k == 0 then
          locals.low0, locals.pick0 = "v0", a
        else
          locals["low" .. k] = string.format("min(low%d, v%d)", k - 1, k)
          locals["pick" .. k] = string.format("if(v%d < low%d, %s, pick%d)", k, k - 1, a, k - 1)
        end
      end
      return locals
    end)()
  },
  {
    -- The placed pool's basin: the pool level at `radius` tiles from its
    -- centre, give or take the wobble, falling `slope` a tile inward.
    type = "noise-function",
    name = "sae_core_landing_pool_at",
    parameters = { "px", "py" },
    expression = string.format("%d + %g * (((px - %d * cos(b)) ^ 2 + (py - %d * sin(b)) ^ 2) ^ 0.5 - %d)\z
                                - %g * sae_core_edge_at{px = px, py = py}",
      palette.pool.level, LANDING.slope, LANDING.reach, LANDING.reach, LANDING.radius,
      LANDING.slope * LANDING.wobble),
    local_expressions = { b = "sae_core_landing_pool_bearing" }
  },
  {
    -- The whole basin term at any point: the noise's basins and the placed
    -- pool, whichever is lower, in a smooth minimum (`join`, LANDING above).
    -- The pool, its shore, the glow, the starting patches and the siderane
    -- wells all read this.
    type = "noise-function",
    name = "sae_core_basin_full_at",
    parameters = { "px", "py", "reach" },
    expression = string.format("min(ground, pool) - max(0, %g - abs(ground - pool)) ^ 2 / %g",
                               LANDING.join, 4 * LANDING.join),
    local_expressions =
    {
      ground = "sae_core_basin_at{px = px, py = py, reach = reach}",
      pool = "sae_core_landing_pool_at{px = px, py = py}"
    }
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

-- The ground without the pack (FALLBACK_GROUND, above): one expression per
-- tile, read through `tile:<name>:probability` on the Core alone, so Aquilo
-- keeps its own.
local function fallback_name(tile)
  return "sae_core_ground_" .. (tile:gsub("-", "_"))
end

if not mods["alien-biomes"] then
  local names, selectors = {}, {}
  for tile in pairs(FALLBACK_GROUND.selectors) do names[#names + 1] = tile end
  table.sort(names)
  -- The two axes every selector reads: snow to ice, pushed up in the rims
  -- (stopped at the waterline, as the rims are), and the variant.
  local function axes()
    return
    {
      s = string.format("aquilo_snow_ice + %g * %s * (1 - %s)",
                        FALLBACK_GROUND.rim, dark_mask(palette.dark), pool_mask(palette)),
      v = "aquilo_tile_variant"
    }
  end
  for i, tile in ipairs(names) do
    selectors[i] = string.format("(%s)", FALLBACK_GROUND.selectors[tile])
  end
  data:extend({
    {
      type = "noise-expression",
      name = "sae_core_ground_best",
      expression = string.format("max(%s)", table.concat(selectors, ", ")),
      local_expressions = axes()
    }
  })
  for _, tile in ipairs(names) do
    data:extend({
      {
        type = "noise-expression",
        name = fallback_name(tile),
        -- Written so the winner's term is exactly zero, and it answers at
        -- exactly `level`.
        expression = string.format("%s - (sae_core_ground_best - (%s))",
                                   tostring(FALLBACK_GROUND.level), FALLBACK_GROUND.selectors[tile]),
        local_expressions = axes()
      }
    })
  end
end

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
-- Five things make up the starting area:
--   * the siderane field (crust-tap.lua): four wells 40 to 56 tiles out, at
--     the driest of sixteen bearings; that bearing is `sae_crust_vent_bearing`;
--   * kamacite ore and the helium-3 and kamacite vents (below), a quarter, a
--     half and three quarters of a turn round from the field, as Vulcanus
--     sets its starting spots at fixed angles from a seeded one;
--   * the landing's own pool (LANDING, above), an eighth of a turn from the
--     field and from two of the patches, 42 to 48 tiles out;
--   * the clearing and the landing lift in the basin term above: the one
--     keeps the noise's pools out to 44 tiles at least, the other thins them
--     out to 96, where these mostly stand;
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
--     the radius is the one that gives that count: 5.5 for the kamacite vent,
--     and 5.1 for the helium-3 vent since it took crude oil's +-1.4 collision
--     for the 3x3 Gas Pump (Liam, 2026-10-21: "Retune to about 11"). Measured
--     over the seed harness's 30 seeds: 9 to 13, mean 10.8, against 4 to 7 at
--     the 3.5 the 2x2 vent had; 5.2 gave a mean of 11.3. A larger patch needs a
--     wider dry rim and keeps a larger berth, so on two of the 30 a starting
--     patch stands one bearing further round (the harness reference,
--     re-recorded, names them).
-- Their distances, 56 to 72 tiles (44 to 104 if they have to move) plus the
-- radius, keep them inside 112: well within the engine's 150-tile starting
-- area, and mostly on lifted ground.
--
-- `turn` is the bearing each prefers, in turns round from the field's.
local STARTING_PATCHES =
{
  { key = "gas",           control = "sae-gas-vent",      turn = 2 / 4, reach = 56, radius = 5.1, per_vent = 60000 },
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
    expression = "min(sae_core_basin_full_at{px = px,     py = py,     reach = (px * px + py * py) ^ 0.5},\z
                      sae_core_basin_full_at{px = px + r, py = py,     reach = ((px + r) ^ 2 + py * py) ^ 0.5},\z
                      sae_core_basin_full_at{px = px - r, py = py,     reach = ((px - r) ^ 2 + py * py) ^ 0.5},\z
                      sae_core_basin_full_at{px = px,     py = py + r, reach = (px * px + (py + r) ^ 2) ^ 0.5},\z
                      sae_core_basin_full_at{px = px,     py = py - r, reach = (px * px + (py - r) ^ 2) ^ 0.5})"
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
  -- ground is the wrong colour for this place, but it is ground. Its snow
  -- alone, as without the pack: the ice is meltable.
  if found == 0 then
    add({ "snow-flat", "snow-crests", "snow-lumpy", "snow-patchy" })
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

local function property_expression_names()
  local names =
  {
    elevation = "sae_core_elevation",
    temperature = "sae_core_temperature",
    moisture = "sae_core_moisture",
    aux = "sae_core_aux",
    cliffiness = "cliffiness_basic",
    cliff_elevation = "cliff_elevation_from_elevation"
  }
  if not mods["alien-biomes"] then
    for tile in pairs(FALLBACK_GROUND.selectors) do
      names["tile:" .. tile .. ":probability"] = fallback_name(tile)
    end
  end
  return names
end

return function()
  return
  {
    property_expression_names = property_expression_names(),
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

