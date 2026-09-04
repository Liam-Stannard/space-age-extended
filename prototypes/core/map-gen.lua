-- Terrain for the Core.
--
-- The elevation expression never dips below sea level, so no water tile can
-- ever place -- which is how "no fluids on the surface" is enforced by the
-- terrain rather than by a rule.
--
-- Tiles come from Alien Biomes when it is installed, because it has volcanic
-- and mineral ground that suits a metallic crust far better than anything
-- vanilla ships. Without it the Core falls back to vanilla's Aquilo snow, which
-- is a frozen crust of the wrong colour but entirely playable -- and that
-- fallback is what runs here, so it is the branch that gets tested.
--
-- The tiles named below are checked against data.raw before use: an optional
-- dependency that silently assumes its own presence is not optional.

data:extend({
  {
    -- Tiles choose themselves by temperature, moisture and aux, so borrowing
    -- Aquilo's temperature expression got only Aquilo's answer: frozen ground,
    -- whatever tile set was installed. The Core is a frozen crust over a hot
    -- interior, so it wants warm, bone-dry ground with cold patches -- not an
    -- ice world.
    type = "noise-expression",
    name = "sae_core_temperature",
    expression = "55 + 65 * multioctave_noise{x = x,\z
                                              y = y,\z
                                              seed0 = map_seed,\z
                                              seed1 = 2291,\z
                                              octaves = 3,\z
                                              persistence = 0.55,\z
                                              input_scale = 1/340,\z
                                              output_scale = 1}"
  },
  {
    type = "noise-expression",
    name = "sae_core_moisture",
    -- Not water: on Alien Biomes' scale this is one of the axes a tile picks
    -- itself by, and the mineral grounds want the middle of it. Measured: at
    -- 0.06 nothing but snow qualified.
    expression = "clamp(0.45 + 0.25 * multioctave_noise{x = x,\z
                                                        y = y,\z
                                                        seed0 = map_seed,\z
                                                        seed1 = 771,\z
                                                        octaves = 3,\z
                                                        persistence = 0.5,\z
                                                        input_scale = 1/260,\z
                                                        output_scale = 1}, 0, 1)"
  },
  {
    type = "noise-expression",
    name = "sae_core_aux",
    expression = "clamp(0.45 + 0.25 * multioctave_noise{x = x,\z
                                                       y = y,\z
                                                       seed0 = map_seed,\z
                                                       seed1 = 5183,\z
                                                       octaves = 3,\z
                                                       persistence = 0.5,\z
                                                       input_scale = 1/300,\z
                                                       output_scale = 1}, 0, 1)"
  },
  {
    type = "noise-expression",
    name = "sae_core_elevation",
    -- Always well above zero: a crust with relief, and no coastline anywhere.
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

-- Alien Biomes' names first, vanilla's second. Anything the installed game does
-- not actually define is dropped rather than assumed.
local function core_tiles()
  local wanted =
  {
    "volcanic-orange-heat-1", "volcanic-orange-heat-2", "volcanic-orange-heat-3",
    "volcanic-orange-heat-4",
    "volcanic-ash-dark", "volcanic-ash-light", "volcanic-ash-flats",
    "volcanic-ash-cracks", "volcanic-cracks", "volcanic-cracks-warm",
    "mineral-grey-dirt-1", "mineral-grey-dirt-2", "mineral-grey-dirt-3",
    "mineral-grey-sand-1", "mineral-grey-sand-3",
    "mineral-black-dirt-1", "mineral-black-dirt-2", "mineral-black-dirt-3",
    "frozen-snow-0", "frozen-snow-1"
  }
  local fallback =
  {
    "snow-flat", "snow-crests", "snow-lumpy", "snow-patchy",
    "ice-rough", "ice-smooth"
  }

  local settings, found = {}, 0
  for _, name in pairs(wanted) do
    if data.raw.tile[name] then settings[name] = {} found = found + 1 end
  end

  -- Half the set missing means the pack is absent or has renamed everything;
  -- either way a partial set would leave holes in the ground.
  if found < #wanted / 2 then
    settings = {}
    for _, name in pairs(fallback) do
      if data.raw.tile[name] then settings[name] = {} end
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
