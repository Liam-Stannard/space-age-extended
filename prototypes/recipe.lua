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
    -- 25 scrap -> 100 molten scrap (-> 60 molten iron + 38 molten copper
    -- via Sections 2-4 = ~0.24 iron plate + 0.15 copper plate per scrap).
    -- Recycling yields ~0.6 iron-equivalent per scrap plus circuits/LDS,
    -- so this is still less material-efficient than recycling -- its niche
    -- is *deterministic bulk plate* for a Fulgora base drowning in gears,
    -- not a recycling replacement (design doc §1, §16). An earlier
    -- 50-molten-scrap version was ~5x below recycling on iron alone, too
    -- low to serve even that niche. Calcite is the chain's Vulcanus import
    -- burden (§16): 2 per 100 molten metal sits well above vanilla
    -- lava-casting's 1 per 250 but no longer dwarfs the metal it flux-es.
    ingredients = {
      { type = "item", name = "scrap", amount = 25 },
      { type = "item", name = "calcite", amount = 2 },
    },
    results = {
      { type = "fluid", name = "sae-molten-scrap", amount = 100 },
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
    icon_mipmaps = 4,
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
  -- 90/10 copper/holmium split -- Holmium is a deliberate trickle, not a
  -- primary output (design doc §4). At 2 residue per craft the chain lands
  -- at ~0.016 holmium ore per scrap (via Section 5's 5-residue-per-ore
  -- extraction), just above vanilla recycling's 1% -- a genuine
  -- supplement. An earlier 95/5 version yielded ~0.008/scrap, *below*
  -- recycling, which made the holmium path add nothing over the
  -- alternative that also gives everything else.
  {
    type = "recipe",
    name = "sae-non-ferrous-separation",
    icon = "__space-age-extended__/graphics/icons/non-ferrous-separation.png",
    icon_size = 64,
    icon_mipmaps = 4,
    categories = { "electromagnetics" },
    subgroup = "fulgora-processes",
    order = "e[sae]-d[non-ferrous-separation]",
    enabled = false,
    ingredients = {
      { type = "fluid", name = "sae-molten-non-ferrous-metal", amount = 20 },
    },
    results = {
      { type = "fluid", name = "molten-copper", amount = 18 },
      { type = "fluid", name = "sae-holmium-rich-residue", amount = 2 },
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
  -- One foil = 15 molten copper = 1.5 copper plate = exactly the 3 Copper
  -- Cable it replaces in Electronic Circuit (design doc §7.1, "value-
  -- neutral substitution"). This is the single copper-equivalent tunable
  -- for all three circuit alt recipes (design doc §16) -- an earlier
  -- 10-foil-per-craft version made each foil worth 0.15 plate, a ~10x
  -- copper discount that made the alt recipes universally dominant
  -- rather than "better only when committed" (§7).
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
      { type = "item", name = "sae-copper-foil", amount = 1 },
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
      { type = "fluid", name = "molten-iron", amount = 10 }, -- replaces 1 Iron Plate, vanilla's own casting-iron ratio (20 molten-iron -> 2 iron-plate)
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

  -- Section 8: Capstone: Resonant Electromagnetics (design doc §8)
  {
    type = "recipe",
    name = "sae-catalyst-rod",
    categories = { "electromagnetics" },
    subgroup = "fulgora-processes",
    order = "e[sae]-j[catalyst-rod]",
    enabled = false,
    ingredients = {
      { type = "item", name = "holmium-ore", amount = 1 },
      { type = "item", name = "sae-copper-foil", amount = 2 },
      { type = "item", name = "iron-plate", amount = 5 },
    },
    results = {
      { type = "item", name = "sae-catalyst-rod", amount = 1 },
    },
    energy_required = 10,
    auto_recycle = false,
  },
  {
    -- The Catalyst Rod is consumed as a normal ingredient here -- Factorio
    -- has no native "wears down with use" item, so the one-time-use feel is
    -- achieved with a standard multi-output recipe (design doc §8.2).
    type = "recipe",
    name = "sae-resonant-circuit",
    categories = { "electromagnetics" },
    subgroup = "fulgora-processes",
    order = "e[sae]-k[resonant-circuit]",
    enabled = false,
    main_product = "sae-resonant-circuit",
    ingredients = {
      { type = "item", name = "processing-unit", amount = 1 },
      { type = "item", name = "sae-copper-foil", amount = 2 },
      { type = "item", name = "sae-catalyst-rod", amount = 1 },
    },
    results = {
      { type = "item", name = "sae-resonant-circuit", amount = 1 },
      { type = "item", name = "sae-depleted-catalyst-rod", amount = 1 },
      { type = "fluid", name = "sae-contaminated-sulfuric-acid", amount = 20 },
    },
    energy_required = 15,
  },
  {
    -- Mirrors vanilla's acid-neutralisation recipe, but runs on Fulgora
    -- under normal atmosphere -- deliberately no surface_conditions gate
    -- (design doc §8.3).
    type = "recipe",
    name = "sae-purify-contaminated-sulfuric-acid",
    categories = { "chemistry" },
    subgroup = "fulgora-processes",
    order = "e[sae]-l[purify-contaminated-sulfuric-acid]",
    enabled = false,
    main_product = "sulfuric-acid",
    ingredients = {
      { type = "fluid", name = "sae-contaminated-sulfuric-acid", amount = 20 },
      { type = "item", name = "calcite", amount = 1 },
    },
    results = {
      { type = "fluid", name = "sulfuric-acid", amount = 15 },
      { type = "fluid", name = "steam", amount = 50, temperature = 500 },
    },
    energy_required = 1,
    allow_decomposition = false,
  },
  {
    -- The Vulcanus half of the capstone -- Lava forces this recipe onto
    -- Vulcanus, Catalyst Rod forces the Fulgora dependency (design doc §8.4).
    type = "recipe",
    name = "sae-magmatic-core",
    categories = { "metallurgy" },
    subgroup = "vulcanus-processes",
    order = "e[sae]-m[magmatic-core]",
    enabled = false,
    main_product = "sae-magmatic-core",
    ingredients = {
      { type = "fluid", name = "lava", amount = 500 },
      { type = "item", name = "tungsten-plate", amount = 5 },
      { type = "item", name = "sae-catalyst-rod", amount = 1 },
    },
    results = {
      { type = "item", name = "sae-magmatic-core", amount = 1 },
      { type = "item", name = "sae-depleted-catalyst-rod", amount = 1 },
    },
    energy_required = 16,
    allow_decomposition = false,
  },
  {
    -- Depleted-rod counterpart to sae-holmium-extraction (design doc §5,
    -- "Variant recipe: Depleted Catalyst Rod reprocessing") -- closes the
    -- Catalyst Rod loop, but deliberately at a reduced yield versus fresh
    -- Holmium-rich Residue extraction.
    type = "recipe",
    name = "sae-depleted-catalyst-rod-reprocessing",
    categories = { "electromagnetics" },
    subgroup = "fulgora-processes",
    order = "e[sae]-n[depleted-catalyst-rod-reprocessing]",
    enabled = false,
    ingredients = {
      { type = "item", name = "sae-depleted-catalyst-rod", amount = 3 },
    },
    results = {
      { type = "item", name = "holmium-ore", amount = 1, independent_probability = 0.5 },
    },
    energy_required = 8,
  },
  {
    -- Craftable anywhere -- both inputs are already location-locked by
    -- their own production (design doc §8.5).
    type = "recipe",
    name = "sae-thermionic-assembly",
    categories = { "crafting" },
    subgroup = "intermediate-product",
    order = "e[sae]-o[thermionic-assembly]",
    enabled = false,
    ingredients = {
      { type = "item", name = "sae-resonant-circuit", amount = 1 },
      { type = "item", name = "sae-magmatic-core", amount = 1 },
    },
    results = {
      { type = "item", name = "sae-thermionic-assembly", amount = 1 },
    },
    energy_required = 10,
    auto_recycle = false,
  },

  -- Section 9: the Quench Turbine and its recipe ladder (design doc §9).
  --
  -- A quench recipe turns one Magmatic Core plus Ice into Quench Vapour at a
  -- temperature the recipe fixes. The turbine clips anything above 315
  -- degrees (prototypes/entity.lua), so a recipe that makes a little very hot
  -- vapour throws most of the core away and one that makes a lot of vapour at
  -- exactly the cap wastes nothing. Electricity per core is therefore set by
  -- which recipe the player can run, and the efficient ones sit behind later
  -- technologies -- that is the whole gate (design doc §9.3).
  --
  -- Arithmetic, per craft, against the turbine's 1.5MJ per unit at the cap:
  --   tier 1  60 vapour at 900, clipped to 315 ->  60 * 1.5MJ =  90MJ/core
  --   tier 2 400 vapour at 315, nothing wasted -> 400 * 1.5MJ = 600MJ/core
  -- Both are 10s crafts, so a chemical plant at speed 1 runs 6 cores/min:
  -- 9MW of turbine feed on tier 1, 60MW on tier 2.
  --
  -- allow_productivity = false on both: a productivity module on a recipe
  -- whose output is energy would mint electricity from nothing.
  {
    -- Tier 1, unlocked with the turbine itself. Deliberately the *only*
    -- pre-Aquilo option and deliberately wasteful -- ~11 plants and 67
    -- cores/min for 100MW, so a platform can be powered before Aquilo but
    -- only by running the Vulcanus/Fulgora line hard enough to hurt.
    type = "recipe",
    name = "sae-lean-quench",
    categories = { "chemistry" },
    subgroup = "energy",
    order = "e[sae]-q[lean-quench]",
    enabled = false,
    ingredients = {
      { type = "item", name = "sae-magmatic-core", amount = 1 },
      { type = "item", name = "ice", amount = 10 },
    },
    results = {
      { type = "fluid", name = "sae-quench-vapour", amount = 60, temperature = 900 },
    },
    energy_required = 10,
    allow_productivity = false,
    allow_decomposition = false,
    auto_recycle = false,
  },
  {
    -- Tier 2, gated on Aquilo via vanilla's own cryogenic-plant technology
    -- and, more importantly, via Fluoroketone -- which only Aquilo can make.
    -- The fluoroketone is a closed loop, not a consumable: it comes back out
    -- hot and sae-radiative-fluoroketone-cooling below returns it to cold on
    -- the platform itself. What Aquilo actually supplies is the technology
    -- plus an initial fill shipped up in barrels.
    type = "recipe",
    name = "sae-cryogenic-quench",
    categories = { "chemistry" },
    subgroup = "energy",
    order = "e[sae]-r[cryogenic-quench]",
    enabled = false,
    ingredients = {
      { type = "item", name = "sae-magmatic-core", amount = 1 },
      { type = "item", name = "ice", amount = 40 },
      { type = "fluid", name = "fluoroketone-cold", amount = 100 },
    },
    results = {
      { type = "fluid", name = "sae-quench-vapour", amount = 400, temperature = 315 },
      { type = "fluid", name = "fluoroketone-hot", amount = 100 },
    },
    main_product = "sae-quench-vapour",
    energy_required = 10,
    allow_productivity = false,
    allow_decomposition = false,
    auto_recycle = false,
  },
  {
    -- Closes the fluoroketone loop in space. Vanilla re-cools fluoroketone in
    -- a cryogenic plant, which cannot be built on a platform (its
    -- surface_conditions demand pressure >= 10), so without this a platform
    -- would fill up with hot fluoroketone and stall. Vacuum radiates, hence
    -- the surface condition -- a real physical property, the same gate
    -- vanilla's thruster uses, not a planet-name rule (framework.md §2.3).
    -- On a planet the vanilla cryogenic recipe remains the only way.
    --
    -- 10s for 10 fluid means ~10 chemical plants radiating per quench plant:
    -- that footprint is the visible cost of the tier-2 density.
    type = "recipe",
    name = "sae-radiative-fluoroketone-cooling",
    categories = { "chemistry" },
    subgroup = "energy",
    order = "e[sae]-s[radiative-fluoroketone-cooling]",
    enabled = false,
    surface_conditions = {
      { property = "pressure", min = 0, max = 0 },
    },
    ingredients = {
      { type = "fluid", name = "fluoroketone-hot", amount = 10, ignored_by_stats = 10 },
    },
    results = {
      { type = "fluid", name = "fluoroketone-cold", amount = 10, temperature = -150, ignored_by_stats = 10 },
    },
    energy_required = 10,
    allow_productivity = false,
    allow_decomposition = false,
    auto_recycle = false,
  },
  {
    -- Craftable anywhere, same as Thermionic Assembly itself -- the recipe
    -- has no planet lock of its own; only the resulting *entity's placement*
    -- is platform-restricted, via surface_conditions on the entity prototype.
    type = "recipe",
    name = "sae-quench-turbine",
    categories = { "crafting" },
    subgroup = "energy",
    order = "e[sae]-p[quench-turbine]",
    enabled = false,
    ingredients = {
      { type = "item", name = "sae-thermionic-assembly", amount = 2 },
    },
    results = {
      { type = "item", name = "sae-quench-turbine", amount = 1 },
    },
    energy_required = 10,
    auto_recycle = false,
  },
})
