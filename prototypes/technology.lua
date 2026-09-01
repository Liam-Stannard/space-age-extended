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
})
