-- New recipes introduced by Space Age Extended.
-- See design/vulcanus-fulgora.md §1-6.
--
-- "Heat" in the design doc's ingredient lists is not a literal Factorio
-- ingredient (Foundry has no heat-network input) -- it's represented by
-- each recipe's energy_required draw against the crafting building's
-- normal electric energy source, same as any vanilla Foundry recipe.
--
-- All amounts below are v0.1 placeholders (design doc §16 "Open Balancing
-- Questions"), sized off the vanilla casting-iron/casting-copper ratios so
-- the chain is internally consistent; real tuning happens during playtesting.

data:extend({
  -- Section 1: Scrap Remelting (Foundry, Fulgora)
  {
    type = "recipe",
    name = "sae-scrap-remelting",
    categories = { "metallurgy" },
    subgroup = "fulgora-processes",
    order = "e[sae]-a[scrap-remelting]",
    enabled = false,
    ingredients = {
      { type = "item", name = "scrap", amount = 25 },
      { type = "item", name = "calcite", amount = 10 },
    },
    results = {
      { type = "fluid", name = "sae-molten-scrap", amount = 50 },
    },
    energy_required = 3.2,
    allow_decomposition = false,
  },

  -- Section 2: Ferrous / Non-Ferrous Separation (Electromagnetic Plant, Fulgora)
  {
    type = "recipe",
    name = "sae-separate-molten-scrap",
    icon = "__space-age-extended__/graphics/icons/separate-molten-scrap.png",
    icon_size = 64,
    categories = { "electromagnetics" },
    subgroup = "fulgora-processes",
    order = "e[sae]-b[separate-molten-scrap]",
    enabled = false,
    ingredients = {
      { type = "fluid", name = "sae-molten-scrap", amount = 50 },
    },
    results = {
      { type = "fluid", name = "sae-molten-ferrous-metal", amount = 30 },
      { type = "fluid", name = "sae-molten-non-ferrous-metal", amount = 20 },
    },
    energy_required = 2,
  },

  -- Section 3: Ferrous Refinement (Foundry, Fulgora)
  -- Deliberately 1:1 into vanilla molten-iron -- the "surplus" comes from
  -- how little of it downstream recipes actually consume, not from an
  -- inflated yield here (design doc §3).
  {
    type = "recipe",
    name = "sae-ferrous-refinement",
    categories = { "metallurgy" },
    subgroup = "fulgora-processes",
    order = "e[sae]-c[ferrous-refinement]",
    enabled = false,
    ingredients = {
      { type = "fluid", name = "sae-molten-ferrous-metal", amount = 30 },
    },
    results = {
      { type = "fluid", name = "molten-iron", amount = 30 },
    },
    energy_required = 3.2,
    allow_decomposition = false,
  },

  -- Section 4: Non-Ferrous Separation (Electromagnetic Plant, Fulgora)
  -- 95/5 copper/holmium split -- Holmium is a deliberate trickle, not a
  -- primary output (design doc §4).
  {
    type = "recipe",
    name = "sae-non-ferrous-separation",
    icon = "__space-age-extended__/graphics/icons/non-ferrous-separation.png",
    icon_size = 64,
    categories = { "electromagnetics" },
    subgroup = "fulgora-processes",
    order = "e[sae]-d[non-ferrous-separation]",
    enabled = false,
    ingredients = {
      { type = "fluid", name = "sae-molten-non-ferrous-metal", amount = 20 },
    },
    results = {
      { type = "fluid", name = "molten-copper", amount = 19 },
      { type = "fluid", name = "sae-holmium-rich-residue", amount = 1 },
    },
    energy_required = 4,
  },

  -- Section 5: Holmium Extraction (Electromagnetic Plant, Fulgora)
  -- Deliberately slow/low-yield -- supplementary recovery only, not a
  -- replacement for Fulgora's existing Holmium production (design doc §5).
  {
    type = "recipe",
    name = "sae-holmium-extraction",
    categories = { "electromagnetics" },
    subgroup = "fulgora-processes",
    order = "e[sae]-e[holmium-extraction]",
    enabled = false,
    ingredients = {
      { type = "fluid", name = "sae-holmium-rich-residue", amount = 5 },
    },
    results = {
      { type = "item", name = "holmium-ore", amount = 1 },
    },
    energy_required = 8,
  },

  -- Section 6: Copper Foil (Foundry, Fulgora)
  -- Copper-skewed with a small Iron kicker -- gives the Section 3 iron
  -- surplus a genuine, partial consumer (design doc §6).
  {
    type = "recipe",
    name = "sae-copper-foil",
    categories = { "metallurgy" },
    subgroup = "fulgora-processes",
    order = "e[sae]-f[copper-foil]",
    enabled = false,
    ingredients = {
      { type = "fluid", name = "molten-copper", amount = 15 },
      { type = "fluid", name = "molten-iron", amount = 1 },
    },
    results = {
      { type = "item", name = "sae-copper-foil", amount = 10 },
    },
    energy_required = 3.2,
    allow_decomposition = false,
    auto_recycle = false,
  },

  -- Section 7: Electromagnetic circuit alt-recipes (Electromagnetic Plant, Fulgora)
  -- Output the literal vanilla item -- no new circuit tier. Copper Foil
  -- substitutes only the copper-cable slot of each vanilla recipe (design
  -- doc §7's substitution rule); everything else stays identical to vanilla.
  {
    type = "recipe",
    name = "sae-electromagnetic-electronic-circuit",
    categories = { "electromagnetics" },
    subgroup = "fulgora-processes",
    order = "e[sae]-g[electromagnetic-electronic-circuit]",
    enabled = false,
    ingredients = {
      { type = "item", name = "sae-copper-foil", amount = 1 }, -- replaces 3 Copper Cable
      { type = "item", name = "iron-plate", amount = 1 },
    },
    results = {
      { type = "item", name = "electronic-circuit", amount = 1 },
    },
    energy_required = 0.5,
    allow_productivity = true,
  },
  {
    type = "recipe",
    name = "sae-electromagnetic-advanced-circuit",
    categories = { "electromagnetics" },
    subgroup = "fulgora-processes",
    order = "e[sae]-h[electromagnetic-advanced-circuit]",
    enabled = false,
    ingredients = {
      { type = "item", name = "sae-copper-foil", amount = 1 }, -- replaces 4 Copper Cable
      { type = "item", name = "electronic-circuit", amount = 2 },
      { type = "item", name = "plastic-bar", amount = 2 },
    },
    results = {
      { type = "item", name = "advanced-circuit", amount = 1 },
    },
    energy_required = 6,
    allow_productivity = true,
  },
  {
    -- Processing Unit has no direct copper ingredient in vanilla -- its
    -- copper is embedded inside the Electronic Circuit input. Reducing
    -- that count and substituting Copper Foil directly also implicitly
    -- discounts the Iron Plate each removed circuit carried; this is
    -- accepted deliberately (design doc §7.3 balancing note).
    type = "recipe",
    name = "sae-electromagnetic-processing-unit",
    categories = { "electromagnetics" },
    subgroup = "fulgora-processes",
    order = "e[sae]-i[electromagnetic-processing-unit]",
    enabled = false,
    ingredients = {
      { type = "item", name = "sae-copper-foil", amount = 5 },
      { type = "item", name = "electronic-circuit", amount = 15 }, -- reduced from vanilla's 20
      { type = "item", name = "advanced-circuit", amount = 2 },
      { type = "fluid", name = "sulfuric-acid", amount = 5 },
    },
    results = {
      { type = "item", name = "processing-unit", amount = 1 },
    },
    energy_required = 10,
    allow_productivity = true,
  },
})
