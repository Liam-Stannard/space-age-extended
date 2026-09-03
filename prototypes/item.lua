-- New items introduced by Space Age Extended.
-- See design/vulcanus-fulgora.md §6.

data:extend({
  {
    type = "item",
    name = "sae-copper-foil",
    icon = "__space-age-extended__/graphics/icons/copper-foil.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fulgora-processes",
    order = "e[sae]-e[copper-foil]",
    stack_size = 100,
  },
  {
    type = "item",
    name = "sae-catalyst-rod",
    icon = "__space-age-extended__/graphics/icons/catalyst-rod.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fulgora-processes",
    order = "e[sae]-f[catalyst-rod]",
    stack_size = 50,
  },
  {
    type = "item",
    name = "sae-depleted-catalyst-rod",
    icon = "__space-age-extended__/graphics/icons/depleted-catalyst-rod.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fulgora-processes",
    order = "e[sae]-g[depleted-catalyst-rod]",
    stack_size = 50,
  },
  {
    type = "item",
    name = "sae-resonant-circuit",
    icon = "__space-age-extended__/graphics/icons/resonant-circuit.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fulgora-processes",
    order = "e[sae]-h[resonant-circuit]",
    stack_size = 100,
  },
  {
    -- A real fuel item (design/vulcanus-fulgora.md §9.2's "fuel, shipped up
    -- from Vulcanus") -- burned by the Thermionic Generator's own real
    -- burner fuel slot, genuinely ignited/consumed by the engine itself
    -- exactly like a nuclear reactor's fuel cell (prototypes/entity.lua --
    -- the generator is a real `reactor`-type entity), not held in a
    -- filtered chest slot and not drained by script. fuel_category is a
    -- dedicated "sae-thermionic-fuel" category rather than vanilla
    -- "chemical", so Magmatic Core can't be burned in ordinary furnaces/
    -- vehicles and vanilla fuel can't be burned in the generator.
    -- fuel_value is functionally load-bearing, not just flavour: paired
    -- with the generator's own `consumption` (4MW, prototypes/entity.lua),
    -- one core burns for fuel_value / consumption = 800MJ / 4MW = 200s --
    -- deliberately matching vanilla's uranium fuel cell exactly (8GJ at the
    -- nuclear reactor's 40MW = 200s), since a Magmatic Core is a
    -- catalyst-gated, cross-planet-shipped item (design doc §8.4) and
    -- should last at least as long as the fuel it's the platform-side
    -- analogue of. This only governs how often the slot needs refilling --
    -- the generator's heating *rate* is set independently by
    -- consumption / specific_heat (10°/s at full draw, prototypes/entity.lua)
    -- and is unaffected by how much energy one item holds.
    type = "item",
    name = "sae-magmatic-core",
    icon = "__space-age-extended__/graphics/icons/magmatic-core.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "vulcanus-processes",
    order = "e[sae]-i[magmatic-core]",
    stack_size = 50,
    fuel_category = "sae-thermionic-fuel",
    fuel_value = "800MJ",
  },
  {
    type = "item",
    name = "sae-thermionic-assembly",
    icon = "__space-age-extended__/graphics/icons/thermionic-assembly.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "intermediate-product",
    order = "e[sae]-j[thermionic-assembly]",
    stack_size = 50,
  },
  {
    -- Verified: solar-panel/accumulator/fusion-generator all use the
    -- vanilla "energy" subgroup -- reuse it rather than inventing a new
    -- one (design doc §9.2, "no new building tiers" convention).
    type = "item",
    name = "sae-thermionic-generator",
    icon = "__space-age-extended__/graphics/icons/thermionic-generator.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "energy",
    order = "e[sae]-k[thermionic-generator]",
    place_result = "sae-thermionic-generator",
    stack_size = 10,
  },
})
