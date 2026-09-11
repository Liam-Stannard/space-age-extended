-- Terrain for the Core.
--
-- The elevation expression never dips below sea level, so no water tile can
-- ever place -- which is how "no fluids on the surface" is enforced by the
-- terrain rather than by a rule.
--
-- Everything else here is one choice: which palette the crust wears. Four are
-- defined below and one is selected by PALETTE; they differ in their tile lists
-- *and* in the climate that selects those tiles, because a tile list on its own
-- decides nothing. Tiles choose themselves by temperature, moisture and aux, so
-- naming a tile that no point on the surface qualifies for simply means it
-- never appears -- which is exactly how an earlier version of this file ended
-- up all snow while listing no snow at all.
--
-- To try another one: change PALETTE, then generate a *new* surface. Map
-- generation applies only to chunks that do not exist yet, so an existing save
-- keeps whatever terrain it was born with, and nothing you do here will change
-- ground you have already walked on.

local PALETTE = "struck-nickel"

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

local palettes =
{
  -- Built from the renders of the four below (concept/planet-core/terrain/):
  -- every one of them came out four-fifths Space Age volcanic ash, because
  -- those tiles' own autoplace beats the mineral ground, and none ever placed
  -- the accent tile it was named for. So this one lists NO volcanic tile while
  -- the pack is present, and puts its temperature where the tiles actually
  -- answer: the mineral dirts want 0..30, frost wants below 0, and the orange
  -- heat wants 100..135 -- unreachable by one gentle noise, so heat arrives as
  -- `veins`: a second, long-wavelength noise whose rare peaks are added on top,
  -- so the crust is cold nearly everywhere and split by a few hot seams. That
  -- is the planet brief's own read -- grey-brown metal, pale frost in patches,
  -- heat only through sparse fractures -- and the first palette to attempt it
  -- with the tiles' windows in hand rather than guessed.
  -- frosted-iron with the frost taken out, because the Core has no water to
  -- freeze. The pale here is bare nickel -- the white dirt, but in plates the
  -- size of a room rather than a snowfield, cut by a high-frequency dip in the
  -- colour axis -- and the seams carry two lights: melt-orange where the crust
  -- is grey, arc-blue where it is dark, which is where a strike earths itself.
  -- The blue is the same heat mechanism; the tiles split it by colour axis.
  -- Five without grey, drawn up from the coloured mineral tiles' windows.
  -- Alien Biomes bands its colours by temperature -- cold 0..30: black, grey,
  -- white; mid 30..60: beige, cream, dustyrose, aubergine; hot 60..100: brown,
  -- tan, red, purple, violet -- and within a band by aux: 0.15 pale, 0.45 mid,
  -- 0.7 red-ish, 0.85..0.95 dark and purple. A palette is a choice of band and
  -- a spread across aux; the plates and seams machinery is shared.

  -- Heat-treated iron shows temper colours -- straw, brown, purple, blue -- so
  -- the ground itself says metal that has been hot. Brown body, violet and
  -- purple blooms where aux runs high, straw-tan where it runs low.
  ["tempered-steel"] =
  {
    temperature = { centre = 78, amplitude = 14, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.55, amplitude = 0.34, octaves = 3, persistence = 0.5, scale = 340 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-brown-dirt-1", "mineral-brown-dirt-2", "mineral-brown-dirt-3", "mineral-brown-sand-1",
      "mineral-violet-dirt-1", "mineral-violet-dirt-2", "mineral-purple-dirt-1",
      "mineral-tan-dirt-1", "mineral-tan-sand-1", "mineral-tan-sand-3",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2",
      "volcanic-blue-heat-1", "volcanic-purple-heat-1"
    }
  },

  -- The ore's own colour. A shattered iron core oxidised at the surface: red
  -- and dusty-rose body, plates of tan where the crust is scoured bare, and
  -- cooler dips that go dustyrose. Warm, dark, unmistakably iron.
  ["rust-iron"] =
  {
    temperature = { centre = 72, amplitude = 22, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.70, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 340 },
    plates      = { threshold = 0.45, drop = 1.2, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-red-dirt-1", "mineral-red-dirt-2", "mineral-red-dirt-3", "mineral-red-sand-1",
      "mineral-dustyrose-dirt-1", "mineral-dustyrose-dirt-2", "mineral-dustyrose-sand-1",
      "mineral-brown-dirt-1", "mineral-tan-sand-1", "mineral-tan-dirt-1",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2", "volcanic-blue-heat-1"
    }
  },

  -- The design's own first tile list had a slag flat in it. Black glassy slag
  -- for a body, and plates of pale warm slag foam -- cream, not white -- that
  -- warm themselves into the mid band so cream answers rather than white.
  ["slag-flats"] =
  {
    temperature = { centre = 14, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.45, amplitude = 0.18, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.86, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    plates      = { threshold = 0.45, drop = 1.4, warm = 70, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-black-dirt-1", "mineral-black-dirt-2", "mineral-black-dirt-3",
      "mineral-black-sand-1", "mineral-black-sand-3",
      "mineral-cream-dirt-1", "mineral-cream-dirt-3", "mineral-cream-sand-1", "mineral-beige-dirt-1",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2", "volcanic-blue-heat-1"
    }
  },

  -- A cut meteorite: bronze-brown with crystalline banding. The bands come
  -- from stretching the colour noise along one axis, so tan and red run in
  -- streaks through the brown rather than pooling.
  ["meteorite-face"] =
  {
    temperature = { centre = 76, amplitude = 16, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.16, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.42, amplitude = 0.34, octaves = 2, persistence = 0.5, scale = 220, stretch = 0.18 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-brown-dirt-1", "mineral-brown-dirt-2", "mineral-brown-dirt-3", "mineral-brown-sand-1",
      "mineral-tan-dirt-1", "mineral-tan-dirt-3", "mineral-tan-sand-1",
      "mineral-red-dirt-1", "mineral-red-sand-1",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2", "volcanic-blue-heat-1"
    }
  },

  -- The cool dark of a core whose field died. Aubergine and violet body in
  -- the mid band, dustyrose plates, black where the ground dips cold, and the
  -- seams come up blue because aux runs high. The most alien of the set, and
  -- the one the machines' copper has to warm.
  ["dead-dynamo"] =
  {
    temperature = { centre = 42, amplitude = 16, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.88, amplitude = 0.08, octaves = 3, persistence = 0.5, scale = 340 },
    plates      = { threshold = 0.45, drop = 0.35, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-aubergine-dirt-1", "mineral-aubergine-dirt-2", "mineral-aubergine-dirt-3", "mineral-aubergine-sand-1",
      "mineral-dustyrose-dirt-1", "mineral-dustyrose-dirt-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-purple-heat-1", "volcanic-orange-heat-1"
    }
  },

  ["scoured-nickel"] =
  {
    temperature = { centre = 16, amplitude = 24, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    -- Grey-to-black body, and the range starts above white dirt's window
    -- (0.15 +/- 0.15) on purpose: a render centred at 0.52 let white in as
    -- continents covering a quarter of the ground. Pale here comes only from
    -- the plates term below. Orange heat wants aux below 0.7 and blue above
    -- 0.8, so seams come out a mix of the two -- and neither glows: Alien
    -- Biomes' heat tiles carry no light, so at night a seam is a black line.
    -- Lit fissures need the Core's own tile art.
    aux         = { centre = 0.58, amplitude = 0.26, octaves = 3, persistence = 0.5, scale = 340 },
    -- Bare plates: a short-wavelength noise whose peaks pull aux down toward
    -- white dirt's 0.15 window, in patches a few tiles across.
    plates      = { threshold = 0.45, drop = 1.2, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },

    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },

    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-grey-dirt-1", "mineral-grey-dirt-2", "mineral-grey-dirt-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "mineral-white-dirt-1", "mineral-white-dirt-3",
      "mineral-grey-sand-1", "mineral-grey-sand-3",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-purple-heat-1"
    }
  },

  ["frosted-iron"] =
  {
    -- Centre 14, swing 30: mostly inside the dirts' 0..30, dipping under zero
    -- for frost about a third of the time. The veins are the zero contours of
    -- a second noise: within `width` of a crossing, temperature climbs by up
    -- to `gain` * width -- +120 here -- into the orange heat's window. Contours
    -- always exist, so the seams always appear; a peak-above-threshold version
    -- gave 3% heat on one seed and none at all on the next.
    -- Three renders in: amplitude 30 put a quarter of one seed under frost,
    -- width 0.06 put 7% of the ground in the heat window. Both narrowed.
    temperature = { centre = 16, amplitude = 26, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    -- Dirt wants 0.5 +/- 0.1; sand wants 0.2 +/- 0.2. A 0.14 swing keeps it
    -- dirt with the odd sand flat.
    -- First render: 0.50 +/- 0.14 gave 38% sand, a paler ground than the brief.
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    -- Aux is the colour axis: white at 0.15, grey at 0.5, black at 0.85. Leaning
    -- past the middle keeps white dirt rare (23% in the first render) and lets
    -- black through, which is where the brief's dark metal comes from.
    aux         = { centre = 0.58, amplitude = 0.32, octaves = 3, persistence = 0.5, scale = 340 },

    -- Craters and frost only; the brown volcanic rocks, sulfur crusts and
    -- Fulgora stones are what made the other four read as borrowed ground.
    decoratives = { "snow", "frost" },
    -- "vulcanus" as well as "volcanic": the large rock decal is named after the
    -- planet. And Aquilo's lithium icebergs answer to "ice" -- 56,000 of them in
    -- 256 chunks on the first render, on a world with no lithium.
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium" },

    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      -- No white dirt: on one seed it covered a third of the ground and read as
      -- a snowfield. The pale in this palette is frost, in patches, on metal.
      "mineral-grey-dirt-1", "mineral-grey-dirt-2", "mineral-grey-dirt-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "mineral-grey-sand-1", "mineral-grey-sand-3",
      "frozen-snow-0", "frozen-snow-1", "frozen-snow-3",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2"
    }
  },

  -- Grey worked metal, cool unlit cracks, and a rare scorch where the dead
  -- dynamo still earths itself. The accent is electrical rather than molten,
  -- which ties the ground to the arc storms instead of to volcanism, and keeps
  -- the Core from reading as a second Vulcanus.
  ["struck-nickel"] =
  {
    -- Cool base, tall peaks: the centre sits far below the heat tiles' window
    -- so glowing ground is the exception, and the long input scale gathers what
    -- little there is into veins rather than scattering it as speckle.
    temperature = { centre = 30, amplitude = 90, octaves = 2, persistence = 0.45, scale = 520 },
    moisture    = { centre = 0.50, amplitude = 0.16, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.35, amplitude = 0.20, octaves = 3, persistence = 0.5, scale = 300 },

    -- Nothing warm-looking scattered on it: the ground is cold worked metal,
    -- and the only heat on this world should be the heat the player made.
    decoratives = {},

    tiles       = { "volcanic-cracks", "volcanic-ash-dark", "volcanic-ash-flats" },
    alien_tiles =
    {
      "mineral-grey-dirt-1", "mineral-grey-dirt-2", "mineral-grey-dirt-3",
      "mineral-grey-sand-1", "mineral-grey-sand-3",
      "mineral-white-dirt-1", "mineral-white-dirt-3",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2",
      "volcanic-purple-heat-1"
    }
  },

  -- Black and grey ground, dark ash, and no lit tile anywhere: heat exists on
  -- this world only where the player has built for it. The darkest of the four,
  -- and the one belts and foundries stand out hardest against.
  ["iron-crust"] =
  {
    -- Capped below the heat window on purpose -- nothing here should ever glow.
    temperature = { centre = 35, amplitude = 35, octaves = 3, persistence = 0.55, scale = 340 },
    moisture    = { centre = 0.50, amplitude = 0.18, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.30, amplitude = 0.18, octaves = 3, persistence = 0.5, scale = 300 },

    decoratives = { "ash" },

    tiles       = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-ash-cracks" },
    alien_tiles =
    {
      "mineral-black-dirt-1", "mineral-black-dirt-2", "mineral-black-dirt-3",
      "mineral-grey-dirt-1", "mineral-grey-dirt-2", "mineral-grey-dirt-3",
      "mineral-grey-sand-1"
    }
  },

  -- The design document's own sentence, made visible: a frozen crust over a
  -- still-hot interior. Cold ground in the majority, cut by hot veins where the
  -- interior comes close -- which is terrain that tells the player something.
  ["frozen-crust"] =
  {
    -- The widest swing of the four, so both ends of the tile range are reached:
    -- frozen ground at the troughs, lit cracks at the peaks, and the long scale
    -- keeps each of them a region rather than a fleck.
    temperature = { centre = 25, amplitude = 100, octaves = 2, persistence = 0.5, scale = 600 },
    moisture    = { centre = 0.45, amplitude = 0.22, octaves = 3, persistence = 0.5, scale = 280 },
    aux         = { centre = 0.40, amplitude = 0.22, octaves = 3, persistence = 0.5, scale = 300 },

    decoratives = { "snow", "frozen", "ice" },

    tiles       = { "volcanic-cracks", "volcanic-cracks-warm", "volcanic-ash-dark" },
    alien_tiles =
    {
      "frozen-snow-0", "frozen-snow-1", "frozen-snow-3",
      "mineral-grey-sand-1", "mineral-grey-sand-3", "mineral-grey-dirt-1",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2"
    }
  },

  -- Ash and lit cracks, hot everywhere. The most dramatic and the least
  -- distinct: it is Vulcanus's palette, and orange ground competes with the arc
  -- flashes, which are the surface's actual event.
  ["ashen-furnace"] =
  {
    -- Centred inside the heat window rather than below it, which is what makes
    -- lit ground common instead of rare.
    temperature = { centre = 85, amplitude = 45, octaves = 3, persistence = 0.55, scale = 300 },
    moisture    = { centre = 0.35, amplitude = 0.18, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.45, amplitude = 0.20, octaves = 3, persistence = 0.5, scale = 300 },

    decoratives = { "ash", "cinder", "lava" },

    tiles =
    {
      "volcanic-ash-dark", "volcanic-ash-light", "volcanic-ash-flats",
      "volcanic-ash-cracks", "volcanic-cracks", "volcanic-cracks-warm",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2",
      "volcanic-orange-heat-3", "volcanic-orange-heat-4"
    },
    alien_tiles =
    {
      "mineral-black-dirt-1", "mineral-black-dirt-3",
      "mineral-grey-dirt-1"
    }
  }
}

local palette = palettes[PALETTE]
if not palette then
  error("prototypes/core/map-gen.lua: unknown PALETTE '" .. tostring(PALETTE) .. "'")
end

-- Alien Biomes' temperature scale is far wider than vanilla's -- its orange
-- heat tiles peak at 110, where vanilla's whole range stops well short of that.
-- The clamp keeps every palette inside the band the tiles actually cover, so a
-- tall amplitude buys rare extremes rather than ground no tile answers for.
local TEMPERATURE_RANGE = { -15, 125 }

local function noise(field, seed)
  -- `stretch` squeezes the noise along y, so a field of blobs becomes a field
  -- of bands -- the crystalline banding of a cut meteorite.
  return string.format(
    "multioctave_noise{x = x,\z
                       y = y * %s,\z
                       seed0 = map_seed,\z
                       seed1 = %d,\z
                       octaves = %d,\z
                       persistence = %s,\z
                       input_scale = 1/%d,\z
                       output_scale = 1}",
    field.stretch or 1, seed, field.octaves, field.persistence, field.scale)
end

local function clamped(field, seed, low, high)
  return string.format("clamp(%s + %s * %s, %s, %s)",
    field.centre, field.amplitude, noise(field, seed), low, high)
end

-- Temperature, with a palette's hot veins added if it has them: along the
-- zero contours of a second noise, within `width` of the crossing, up to
-- `gain` * `width` degrees are laid on top -- so a cold crust still reaches
-- the heat tiles' window along a few thin seams.
-- The colour axis, with a palette's bare plates cut into it if it has them: a
-- short-wavelength noise whose peaks above `threshold` pull aux down by up to
-- `drop`, so small patches land in the pale tiles' window without the whole
-- region going pale.
local function aux_expression(pal, seed)
  local base = string.format("%s + %s * %s", pal.aux.centre, pal.aux.amplitude, noise(pal.aux, seed))
  if pal.plates then
    local p = pal.plates
    base = string.format("%s - max(0, %s - %s) * %s", base, noise(p, p.seed), p.threshold, p.drop)
  end
  return string.format("clamp(%s, 0, 1)", base)
end

local function temperature_expression(pal, seed, low, high)
  local base = string.format("%s + %s * %s", pal.temperature.centre,
    pal.temperature.amplitude, noise(pal.temperature, seed))
  if pal.veins then
    local v = pal.veins
    base = string.format("%s + max(0, %s - abs(%s)) * %s", base, v.width, noise(v, v.seed), v.gain)
  end
  -- Plates may warm as well as pale: the mid-temperature colours (cream,
  -- beige, dustyrose, aubergine) sit in a 30..60 window a cold body never
  -- reaches, so a plate that wants one of them lifts its own temperature.
  if pal.plates and pal.plates.warm then
    local pl = pal.plates
    base = string.format("%s + max(0, %s - %s) * %s", base, noise(pl, pl.seed), pl.threshold, pl.warm)
  end
  return string.format("clamp(%s, %s, %s)", base, low, high)
end

data:extend({
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
    -- Always well above zero: a crust with relief, and no coastline anywhere.
    -- Shared by every palette; the look is in the climate, not the shape.
    expression = "120 + 55 * multioctave_noise{x = x,\z
                                               y = y,\z
                                               seed0 = map_seed,\z
                                               seed1 = 8417,\z
                                               octaves = 5,\z
                                               persistence = 0.62,\z
                                               input_scale = 1/220,\z
                                               output_scale = 1}"
  }
})

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

  add(palette.tiles)
  if mods["alien-biomes"] then
    add(palette.alien_tiles)
  else
    -- A palette that leans on the pack says what it wears without it.
    add(palette.without_pack)
  end

  -- Only if a palette somehow contributed nothing at all: vanilla's Aquilo
  -- ground is the wrong colour for this place, but it is ground.
  if found == 0 then
    add({ "snow-flat", "snow-crests", "snow-lumpy", "snow-patchy",
          "ice-rough", "ice-smooth" })
  end

  -- The crust vent is ours and always present, whatever tile pack is installed.
  -- It has to be listed here or it never places at all: a planet's
  -- `autoplace_settings["tile"]` is a whitelist, and a tile absent from it is
  -- excluded no matter what its own autoplace says. Measured: sixteen chunks
  -- generated exactly zero vents until this line existed.
  settings["sae-crust-vent"] = {}

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
-- settings doing nothing and inflate the count that reports success. And every
-- palette's climate still has the final say: a decorative places only where its
-- own conditions are met, so listing the whole rock family gets the grey ones
-- on struck-nickel and the ash ones on ashen-furnace without either being
-- named. That is the same mechanism the tiles use, and it is why this is safe
-- to cast wide.
--
-- Decoratives only. The big rocks are simple-entities rather than decoratives,
-- and vanilla's are refused here on purpose: they yield stone and coal, and a
-- world whose whole point is that it has no carbon should not have coal lying
-- on the ground to be picked up. The Core has its own boulder instead --
-- sae-core-boulder, in resources.lua -- which is enabled through the entity
-- settings below, where an autoplaced entity belongs.
local DECORATIVE_WANTED =
{
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
  for _, pattern in pairs(palette.decoratives or {}) do wanted[#wanted + 1] = pattern end
  for _, pattern in pairs(DECORATIVE_REFUSED) do refused[#refused + 1] = pattern end
  for _, pattern in pairs(palette.refuse or {}) do refused[#refused + 1] = pattern end

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
    -- Which cliff the cliffiness above places. Vanilla planets each name their
    -- own; the Core has none yet, so this states the default that was being
    -- taken silently -- Nauvis's cliff, at Nauvis's spacing -- rather than
    -- leaving it implied. A metallic ridge of the Core's own is outstanding.
    cliff_settings =
    {
      name = "cliff",
      cliff_elevation_0 = 10,
      cliff_elevation_interval = 40,
      richness = 1
    },
    autoplace_controls =
    {
      ["sae-kamacite-ore"] = {},
      ["sae-melt-vent"] = {},
      ["sae-gas-vent"] = {},
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
          ["sae-melt-vent"] = {},
          ["sae-gas-vent"] = {},
          ["sae-core-boulder"] = {}
        }
      }
    }
  }
end
