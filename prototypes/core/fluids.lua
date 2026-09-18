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
    icon = "__space-age-extended__/graphics/icons/fluid/molten-kamacite.png",
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
    type = "fluid",
    name = "sae-helium-3",
    icon = "__space-age-extended__/graphics/icons/fluid/helium-3.png",
    subgroup = "fluid",
    order = "z[sae]-b[helium-3]",
    default_temperature = 15,
    base_color = { r = 0.55, g = 0.78, b = 0.90 },
    flow_color = { r = 0.78, g = 0.90, b = 1.0 },
    auto_barrel = false
  }
})

-- Radiant solution: the corridor's decaying isotope, seeped into the Core's low
-- ground as a liquid and pooled there. Drawn by a Crust Tap standing on the
-- pool's shore; precipitated into radiant fuel with helium-3 (corridor.lua).
-- Never barrelled: it is the Core's, like every fluid here.
data:extend({
  {
    type = "fluid",
    name = "sae-radiant-solution",
    icon = "__space-age-extended__/graphics/icons/radiant-fuel.png",
    subgroup = "fluid",
    order = "z[sae]-ae[radiant-solution]",
    default_temperature = 15,
    base_color = { r = 0.12, g = 0.39, b = 1.0 },
    flow_color = { r = 0.45, g = 0.68, b = 1.0 },
    auto_barrel = false
  }
})
