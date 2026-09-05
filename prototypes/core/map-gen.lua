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

local palettes =
{
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

local function clamped(field, seed, low, high)
  return string.format("clamp(%s + %s * %s, %s, %s)",
    field.centre, field.amplitude, noise(field, seed), low, high)
end

data:extend({
  {
    type = "noise-expression",
    name = "sae_core_temperature",
    expression = clamped(palette.temperature, 2291, TEMPERATURE_RANGE[1], TEMPERATURE_RANGE[2])
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
    expression = clamped(palette.aux, 5183, 0, 1)
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
  if mods["alien-biomes"] then add(palette.alien_tiles) end

  -- Only if a palette somehow contributed nothing at all: vanilla's Aquilo
  -- ground is the wrong colour for this place, but it is ground.
  if found == 0 then
    add({ "snow-flat", "snow-crests", "snow-lumpy", "snow-patchy",
          "ice-rough", "ice-smooth" })
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
    autoplace_controls =
    {
      ["sae-kamacite-ore"] = {},
      ["sae-melt-vent"] = {},
      ["sae-gas-vent"] = {}
    },
    autoplace_settings =
    {
      ["tile"] = { settings = core_tiles() },
      ["decorative"] = { settings = {} },
      ["entity"] =
      {
        settings =
        {
          ["sae-kamacite-ore"] = {},
          ["sae-melt-vent"] = {},
          ["sae-gas-vent"] = {}
        }
      }
    }
  }
end
