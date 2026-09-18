-- The Core's local chain.
--
-- Scaled back to the landing: ore to plate, and nothing past it. The melt
-- line, the farm, the lift and the endgame are on master, not here.

data:extend({
  -- Crushed ore, not raw: plate from raw ore made the Drop Crusher skippable,
  -- and the crusher's own spec says so in as many words.
  {
    type = "recipe",
    name = "sae-kamacite-smelting",
    categories = { "smelting" },
    energy_required = 6.4,
    ingredients = { { type = "item", name = "sae-crushed-kamacite", amount = 3 } },
    results = { { type = "item", name = "sae-kamacite-plate", amount = 1 } },
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

--------------------------------------------------------------------------------
-- What the Core's machines run.
--
-- Every category here is private to one building -- see machines.lua for why
-- that matters. The numbers are the "first pass" figures in each building's
-- spec, section 2.
--------------------------------------------------------------------------------

data:extend({
  -- N1. Crushing. Two streams from one ore, so beneficiation is a choice rather
  -- than a formality.
  {
    type = "recipe",
    name = "sae-crushing",
    -- Two different results, so the engine cannot infer an icon from them.
    icon = "__space-age-extended__/graphics/icons/kamacite-ore.png",
    categories = { "sae-crushing" },
    energy_required = 2,
    ingredients = { { type = "item", name = "sae-kamacite-ore", amount = 2 } },
    results =
    {
      { type = "item", name = "sae-crushed-kamacite", amount = 3 },
      { type = "item", name = "sae-kamacite-fines", amount = 1 }
    },
    enabled = false
  },

  -- N7. The fines the crusher makes, and the only machine that will take them.
  {
    type = "recipe",
    name = "sae-fines-smelting",
    categories = { "smelting" },
    energy_required = 9.6,
    ingredients = { { type = "item", name = "sae-kamacite-fines", amount = 4 } },
    results = { { type = "item", name = "sae-kamacite-plate", amount = 1 } },
    enabled = false
  }
})
