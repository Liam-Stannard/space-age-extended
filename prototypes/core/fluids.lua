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
    -- What gravity leaves behind once the dross has sunk out of the melt.
    type = "fluid",
    name = "sae-settled-melt",
    icon = "__space-age-extended__/graphics/icons/fluid/settled-melt.png",
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
    icon = "__space-age-extended__/graphics/icons/fluid/helium-3.png",
    subgroup = "fluid",
    order = "z[sae]-b[helium-3]",
    default_temperature = 15,
    base_color = { r = 0.55, g = 0.78, b = 0.90 },
    flow_color = { r = 0.78, g = 0.90, b = 1.0 },
    auto_barrel = false
  }
})

--------------------------------------------------------------------------------
-- T3, carbonyl chemistry -- design/06-core-production-tree.md.
--
-- The Core's distinctive trick: nickel and carbon monoxide combine into a *gas*
-- when cold and come apart again when hot, depositing metal of extraordinary
-- purity and handing most of the carbon monoxide back. It is metal that travels
-- through pipes.
--
-- **No temperature gating**, and that is a decision the mod already made once:
-- D4 found no vanilla recipe uses `minimum_temperature` on an ingredient, so
-- "cold" and "hot" are two separate recipes rather than one fluid at two
-- temperatures. The fiction survives; the unproven engine behaviour does not.
--------------------------------------------------------------------------------

data:extend({
  {
    -- The carrier, and the one place imported carbon enters the Core. It is a
    -- catalyst with losses rather than a consumable: 90% comes back from
    -- decomposition, so the corridor delivers a trickle rather than a torrent.
    type = "fluid",
    name = "sae-carbon-monoxide",
    icon = "__space-age-extended__/graphics/icons/fluid/helium-3.png",
    subgroup = "fluid",
    order = "z[sae]-f[carbon-monoxide]",
    default_temperature = 15,
    base_color = { r = 0.40, g = 0.42, b = 0.44 },
    flow_color = { r = 0.62, g = 0.65, b = 0.68 },
    auto_barrel = false
  },
  {
    type = "fluid",
    name = "sae-metal-carbonyl",
    icon = "__space-age-extended__/graphics/icons/fluid/molten-kamacite.png",
    subgroup = "fluid",
    order = "z[sae]-g[metal-carbonyl]",
    default_temperature = 15,
    base_color = { r = 0.52, g = 0.44, b = 0.28 },
    flow_color = { r = 0.74, g = 0.64, b = 0.42 },
    auto_barrel = false
  },
  {
    -- Schreibersite's only consumer, which is what makes the Coil Separator --
    -- and therefore magnetic separation -- worth building at all.
    --
    -- A fluid rather than an item, and S12 is the reason: a `furnace` picks its
    -- own recipe from what it is fed, and it can only do that if there is one
    -- solid ingredient to pick by. Flux as an item would give the Vacuum Furnace
    -- two solids and nothing to disambiguate them.
    type = "fluid",
    name = "sae-phosphide-flux",
    icon = "__space-age-extended__/graphics/icons/fluid/settled-melt.png",
    subgroup = "fluid",
    order = "z[sae]-h[phosphide-flux]",
    default_temperature = 15,
    base_color = { r = 0.68, g = 0.62, b = 0.34 },
    flow_color = { r = 0.86, g = 0.80, b = 0.52 },
    auto_barrel = false
  }
})

-- Radiant solution: the corridor's decaying isotope, seeped into the Core's low
-- ground as a liquid and pooled there. Drawn by a Crust Tap standing on the
-- pool's shore; precipitated into radiant fuel with crust gas (corridor.lua).
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
