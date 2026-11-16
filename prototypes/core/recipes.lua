-- The Core's local chain.
--
-- Scaled back to the landing: ore to plate, and nothing past it. The melt
-- line, the farm, the lift and the endgame went with the cut.

data:extend({
  {
    type = "recipe",
    name = "sae-kamacite-smelting",
    categories = { "smelting" },
    energy_required = 6.4,
    ingredients = { { type = "item", name = "sae-crushed-kamacite", amount = 3 } },
    results = { { type = "item", name = "sae-kamacite-plate", amount = 1 } },
    allow_productivity = true,
    auto_recycle = false,
    enabled = false
  },

  {
    type = "recipe",
    name = "sae-vent-pump",
    categories = { "crafting" },
    energy_required = 5,
    ingredients =
    {
      { type = "item", name = "steel-plate", amount = 10 },
      { type = "item", name = "electric-engine-unit", amount = 5 },
      { type = "item", name = "processing-unit", amount = 5 },
      { type = "item", name = "pipe", amount = 10 }
    },
    results = { { type = "item", name = "sae-vent-pump", amount = 1 } },
    enabled = false
  }
})

data:extend({
  {
    type = "recipe",
    name = "sae-crushing",
    -- Two different results, so the engine cannot infer an icon from them.
    -- Show what it makes: the main stream whole, the fines small in a corner,
    -- as sae-radiant-crushing does, so it does not read as the crushed item.
    icons =
    {
      { icon = "__space-age-extended__/graphics/icons/crushed-kamacite.png", icon_size = 64 },
      { icon = "__space-age-extended__/graphics/icons/kamacite-fines.png", icon_size = 64, scale = 0.25, shift = { 8, 8 } }
    },
    categories = { "sae-crushing" },
    energy_required = 4,
    ingredients = { { type = "item", name = "sae-kamacite-ore", amount = 4 } },
    results =
    {
      { type = "item", name = "sae-crushed-kamacite", amount = 6 },
      { type = "item", name = "sae-kamacite-fines", amount = 2 }
    },
    allow_productivity = true,
    auto_recycle = false,
    enabled = false
  },

  {
    type = "recipe",
    name = "sae-fines-smelting",
    categories = { "smelting" },
    energy_required = 9.6,
    ingredients = { { type = "item", name = "sae-kamacite-fines", amount = 4 } },
    results = { { type = "item", name = "sae-kamacite-plate", amount = 1 } },
    allow_productivity = true,
    auto_recycle = false,
    enabled = false
  }
})
