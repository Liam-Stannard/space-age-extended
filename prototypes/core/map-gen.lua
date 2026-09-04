-- Terrain for the Core.
--
-- The elevation expression never dips below sea level, so no water tile can
-- ever place -- which is how "no fluids on the surface" is enforced by the
-- terrain rather than by a rule. The tile set is vanilla's Aquilo land tiles
-- as a placeholder for the frozen crust; the mod's own tiles arrive with the
-- art pass, and nothing else depends on their names yet.

data:extend({
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

return function()
  return
  {
    property_expression_names =
    {
      elevation = "sae_core_elevation",
      temperature = "aquilo_temperature",
      moisture = "moisture_basic",
      aux = "aquilo_aux",
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
      ["tile"] =
      {
        settings =
        {
          ["snow-flat"] = {},
          ["snow-crests"] = {},
          ["snow-lumpy"] = {},
          ["snow-patchy"] = {},
          ["ice-rough"] = {},
          ["ice-smooth"] = {}
        }
      },
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
