-- New items introduced by Space Age Extended.
-- See design/vulcanus-fulgora.md §6.

data:extend({
  {
    type = "item",
    name = "sae-copper-foil",
    icon = "__space-age-extended__/graphics/icons/copper-foil.png",
    icon_size = 64,
    subgroup = "fulgora-processes",
    order = "e[sae]-e[copper-foil]",
    stack_size = 100,
  },
  {
    type = "item",
    name = "sae-catalyst-rod",
    icon = "__space-age-extended__/graphics/icons/catalyst-rod.png",
    icon_size = 64,
    subgroup = "fulgora-processes",
    order = "e[sae]-f[catalyst-rod]",
    stack_size = 50,
  },
  {
    type = "item",
    name = "sae-depleted-catalyst-rod",
    icon = "__space-age-extended__/graphics/icons/depleted-catalyst-rod.png",
    icon_size = 64,
    subgroup = "fulgora-processes",
    order = "e[sae]-g[depleted-catalyst-rod]",
    stack_size = 50,
  },
  {
    type = "item",
    name = "sae-resonant-circuit",
    icon = "__space-age-extended__/graphics/icons/resonant-circuit.png",
    icon_size = 64,
    subgroup = "fulgora-processes",
    order = "e[sae]-h[resonant-circuit]",
    stack_size = 100,
  },
  {
    type = "item",
    name = "sae-magmatic-core",
    icon = "__space-age-extended__/graphics/icons/magmatic-core.png",
    icon_size = 64,
    subgroup = "vulcanus-processes",
    order = "e[sae]-i[magmatic-core]",
    stack_size = 50,
  },
  {
    type = "item",
    name = "sae-thermionic-assembly",
    icon = "__space-age-extended__/graphics/icons/thermionic-assembly.png",
    icon_size = 64,
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
    subgroup = "energy",
    order = "e[sae]-k[thermionic-generator]",
    place_result = "sae-thermionic-generator",
    stack_size = 10,
  },
})
