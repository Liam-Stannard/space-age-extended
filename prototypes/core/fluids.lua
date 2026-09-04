-- The Core's two native fluids.
--
-- Both are auto_barrel = false, so neither can ever leave the planet: whatever
-- the Core exports has to be embodied in a solid. Helium-3 additionally cannot
-- be *imported*, which is why the landing site has to include a gas vent --
-- without one, no melt can be drawn at all.
--
-- Icons are vanilla placeholders until the art pass.

data:extend({
  {
    type = "fluid",
    name = "sae-molten-kamacite",
    icon = "__space-age__/graphics/icons/fluid/molten-iron.png",
    subgroup = "fluid",
    order = "z[sae]-a[molten-kamacite]",
    default_temperature = 1200,
    max_temperature = 1200,
    heat_capacity = "1kJ",
    base_color = { r = 0.85, g = 0.42, b = 0.16 },
    flow_color = { r = 1.0, g = 0.62, b = 0.32 },
    auto_barrel = false
  },
  {
    -- What gravity leaves behind once the dross has sunk out of the melt.
    type = "fluid",
    name = "sae-settled-melt",
    icon = "__space-age__/graphics/icons/fluid/molten-copper.png",
    subgroup = "fluid",
    order = "z[sae]-c[settled-melt]",
    default_temperature = 900,
    max_temperature = 1200,
    heat_capacity = "1kJ",
    base_color = { r = 0.72, g = 0.55, b = 0.30 },
    flow_color = { r = 0.95, g = 0.78, b = 0.50 },
    auto_barrel = false
  },
  {
    type = "fluid",
    name = "sae-helium-3",
    icon = "__space-age__/graphics/icons/fluid/fluoroketone-cold.png",
    subgroup = "fluid",
    order = "z[sae]-b[helium-3]",
    default_temperature = 15,
    base_color = { r = 0.55, g = 0.78, b = 0.90 },
    flow_color = { r = 0.78, g = 0.90, b = 1.0 },
    auto_barrel = false
  }
})
