-- New technologies introduced by Space Age Extended.
-- See design/vulcanus-fulgora.md §14.

data:extend({
  {
    type = "technology",
    name = "sae-metallurgical-recovery",
    icon = "__space-age-extended__/graphics/technology/metallurgical-recovery.png",
    icon_size = 256,
    icon_mipmaps = 4,
    effects = {
      { type = "unlock-recipe", recipe = "sae-scrap-remelting" },
      { type = "unlock-recipe", recipe = "sae-separate-molten-scrap" },
      { type = "unlock-recipe", recipe = "sae-ferrous-refinement" },
    },
    prerequisites = { "metallurgic-science-pack", "electromagnetic-science-pack" },
    unit = {
      count = 100,
      ingredients = {
        { "metallurgic-science-pack", 1 },
        { "electromagnetic-science-pack", 1 },
      },
      time = 30,
    },
  },
  {
    type = "technology",
    name = "sae-advanced-material-recovery",
    icon = "__space-age-extended__/graphics/technology/advanced-material-recovery.png",
    icon_size = 256,
    icon_mipmaps = 4,
    effects = {
      { type = "unlock-recipe", recipe = "sae-non-ferrous-separation" },
      { type = "unlock-recipe", recipe = "sae-holmium-extraction" },
    },
    prerequisites = { "sae-metallurgical-recovery" },
    unit = {
      count = 150,
      ingredients = {
        { "metallurgic-science-pack", 1 },
        { "electromagnetic-science-pack", 1 },
      },
      time = 30,
    },
  },
  {
    type = "technology",
    name = "sae-electromagnetic-metallurgy",
    icon = "__space-age-extended__/graphics/technology/electromagnetic-metallurgy.png",
    icon_size = 256,
    icon_mipmaps = 4,
    effects = {
      { type = "unlock-recipe", recipe = "sae-copper-foil" },
      { type = "unlock-recipe", recipe = "sae-electromagnetic-electronic-circuit" },
      { type = "unlock-recipe", recipe = "sae-electromagnetic-advanced-circuit" },
    },
    -- Copper Foil needs both the Ferrous and Non-Ferrous output halves of
    -- the chain, so this explicitly requires both prior technologies
    -- (design doc §14, Technology 3).
    prerequisites = { "sae-metallurgical-recovery", "sae-advanced-material-recovery" },
    unit = {
      count = 200,
      ingredients = {
        { "metallurgic-science-pack", 1 },
        { "electromagnetic-science-pack", 1 },
      },
      time = 30,
    },
  },
  {
    type = "technology",
    name = "sae-integrated-electronics",
    icon = "__space-age-extended__/graphics/technology/integrated-electronics.png",
    icon_size = 256,
    icon_mipmaps = 4,
    effects = {
      { type = "unlock-recipe", recipe = "sae-electromagnetic-processing-unit" },
    },
    prerequisites = { "sae-electromagnetic-metallurgy" },
    unit = {
      count = 250,
      ingredients = {
        { "metallurgic-science-pack", 1 },
        { "electromagnetic-science-pack", 1 },
      },
      time = 30,
    },
  },
  {
    type = "technology",
    name = "sae-resonant-electromagnetics",
    icon = "__space-age-extended__/graphics/technology/resonant-electromagnetics.png",
    icon_size = 256,
    icon_mipmaps = 4,
    effects = {
      { type = "unlock-recipe", recipe = "sae-catalyst-rod" },
      { type = "unlock-recipe", recipe = "sae-resonant-circuit" },
      { type = "unlock-recipe", recipe = "sae-purify-contaminated-sulfuric-acid" },
      { type = "unlock-recipe", recipe = "sae-magmatic-core" },
      { type = "unlock-recipe", recipe = "sae-depleted-catalyst-rod-reprocessing" },
      { type = "unlock-recipe", recipe = "sae-thermionic-assembly" },
    },
    -- The capstone requires both circuit-tier technologies (design doc §14,
    -- Technology 5).
    prerequisites = { "sae-electromagnetic-metallurgy", "sae-integrated-electronics" },
    unit = {
      count = 350,
      ingredients = {
        { "metallurgic-science-pack", 1 },
        { "electromagnetic-science-pack", 1 },
      },
      time = 45,
    },
  },
  {
    -- Technology 6 (design doc §9). Named for the subsystem it claims
    -- (framework.md §4.2, "Power") rather than a literal transliteration
    -- of the doc's section title, matching this mod's tech-naming pattern.
    type = "technology",
    name = "sae-thermionic-power",
    icon = "__space-age-extended__/graphics/technology/thermionic-power.png",
    icon_size = 256,
    icon_mipmaps = 4,
    effects = {
      { type = "unlock-recipe", recipe = "sae-quench-turbine" },
      { type = "unlock-recipe", recipe = "sae-lean-quench" },
    },
    prerequisites = { "sae-resonant-electromagnetics" },
    unit = {
      count = 500,
      ingredients = {
        { "metallurgic-science-pack", 1 },
        { "electromagnetic-science-pack", 1 },
      },
      time = 60,
    },
  },
  {
    -- Technology 7 (design doc §9.3). The efficient quench recipe, gated on
    -- Aquilo: its prerequisite is vanilla's own cryogenic-plant technology,
    -- and its recipe needs Fluoroketone, which only Aquilo produces. Power
    -- therefore cannot be solved cheaply before Aquilo -- tier 1 works, but
    -- at roughly a seventh of the electricity per shipped Magmatic Core.
    --
    -- This also unlocks the radiative cooling recipe that closes the
    -- fluoroketone loop in space; without it the tier-2 quench would stall
    -- on its own hot output, since a cryogenic plant can't be built on a
    -- platform.
    type = "technology",
    name = "sae-cryogenic-quenching",
    icon = "__space-age-extended__/graphics/technology/thermionic-power.png",
    icon_size = 256,
    icon_mipmaps = 4,
    effects = {
      { type = "unlock-recipe", recipe = "sae-quench-coolant" },
      { type = "unlock-recipe", recipe = "sae-cryogenic-quench" },
      { type = "unlock-recipe", recipe = "sae-radiative-coolant-cooling" },
    },
    prerequisites = { "sae-thermionic-power", "cryogenic-plant" },
    unit = {
      count = 750,
      ingredients = {
        { "metallurgic-science-pack", 1 },
        { "electromagnetic-science-pack", 1 },
        { "cryogenic-science-pack", 1 },
      },
      time = 60,
    },
  },
})
