-- New technologies introduced by Space Age Extended.
-- See design/vulcanus-fulgora.md §14.

data:extend({
  {
    type = "technology",
    name = "sae-metallurgical-recovery",
    icon = "__space-age-extended__/graphics/technology/metallurgical-recovery.png",
    icon_size = 256,
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
})
