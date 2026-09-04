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
    -- Also explicit: cast from two fluids, so the derived default was again
    -- 100 (10,000 per rocket). Foil is a Fulgora-local intermediate and is
    -- not normally shipped, but leaving a nonsense weight on it invites a
    -- nonsense answer the first time someone does ship it.
    weight = 2000,
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
    -- The rod loop's two legs are weighted against the core they exist to
    -- produce (1000, see Magmatic Core below). Left at the engine's derived
    -- 20000 they were 50 per rocket, so moving rods to Vulcanus and spent
    -- rods back cost twenty times moving the cores themselves -- the waste
    -- leg dominating the fuel leg, which is backwards. At 2000 the loop is
    -- 4x the core's shipping cost: still the tree's standing tax, no longer
    -- the thing that decides whether the tree is worth running.
    weight = 2000,
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
    -- Same weight as a fresh Catalyst Rod: it is the same object, spent.
    weight = 2000,
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
    -- The Vulcanus half of the capstone, shipped up to platforms (design
    -- doc §9.2). No fuel_category/fuel_value: a Magmatic Core is an
    -- *ingredient* of the quench recipes, not a fuel item. The earlier Thermionic
    -- Generator burned it in a real burner slot; the Quench Turbine consumes
    -- the vapour a quench recipe makes from it instead, which is what lets
    -- the recipe tier -- not the item -- decide how much electricity one core
    -- is worth. Leaving the fuel fields on would also let any future burner
    -- with a matching category burn cores directly and bypass the ladder.
    type = "item",
    name = "sae-magmatic-core",
    icon = "__space-age-extended__/graphics/icons/magmatic-core.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "vulcanus-processes",
    order = "e[sae]-i[magmatic-core]",
    stack_size = 50,
    -- Explicit, because the engine's default was badly wrong here. Factorio
    -- derives an unspecified weight from the recipe, and this recipe is
    -- mostly Lava (a fluid, which weighs nothing) with two products, so the
    -- derived value came out at 100 -- i.e. 10,000 cores per rocket. Measured
    -- against vanilla that made a rocket of cores worth 6TJ at the cryogenic
    -- quench, three times a rocket of fusion power cells (50 x 40GJ = 2TJ)
    -- and seventy-five times a rocket of uranium fuel cells (10 x 8GJ =
    -- 80GJ). Shipping was effectively free, which guts framework.md §2.1 --
    -- the shipping principle is the whole point of a cross-planet tree.
    --
    -- 1000 puts 1000 cores in a rocket: 90GJ at the lean quench, which is
    -- uranium parity, and 600GJ at the cryogenic quench, comfortably under
    -- fusion. A 100MW platform on the cryogenic quench then burns a rocket of
    -- cores every ~100 minutes; on the lean quench, every ~15.
    weight = 1000,
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
    name = "sae-quench-turbine",
    icon = "__space-age-extended__/graphics/icons/quench-turbine.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "energy",
    order = "e[sae]-k[quench-turbine]",
    place_result = "sae-quench-turbine",
    stack_size = 10,
  },
})
