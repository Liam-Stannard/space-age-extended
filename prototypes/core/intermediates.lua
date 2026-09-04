-- The Core's production line, stages one and two.
--
-- Five capstone products arrive from four worlds and are *consumed* here, each
-- with a different local input, to make an intermediate that only the Core can
-- produce. The intermediates combine into two end products, and only those
-- build a Field Coil Segment -- so no capstone ever touches the segment
-- directly, and the Core is a factory rather than an assembly point.
--
-- A field coil has five parts. There are five trees. Each supplies one.

data:extend({
  {
    type = "item",
    name = "sae-field-conductor",
    icon = "__space-age__/graphics/icons/superconductor.png",
    subgroup = "intermediate-product",
    order = "z[sae]-i[a-conductor]",
    stack_size = 50,
    weight = 4000
  },
  {
    type = "item",
    name = "sae-magnetic-core-billet",
    icon = "__space-age__/graphics/icons/tungsten-plate.png",
    subgroup = "intermediate-product",
    order = "z[sae]-i[b-core-billet]",
    stack_size = 50,
    weight = 6000
  },
  {
    type = "item",
    name = "sae-reinforced-frame",
    icon = "__space-age__/graphics/icons/tungsten-carbide.png",
    subgroup = "intermediate-product",
    order = "z[sae]-i[c-frame]",
    stack_size = 50,
    weight = 6000
  },
  {
    type = "item",
    name = "sae-insulation-sleeve",
    icon = "__base__/graphics/icons/plastic-bar.png",
    subgroup = "intermediate-product",
    order = "z[sae]-i[d-sleeve]",
    stack_size = 50,
    weight = 2000
  },
  {
    type = "item",
    name = "sae-coolant-charge",
    icon = "__space-age__/graphics/icons/fluid/fluoroketone-cold.png",
    subgroup = "intermediate-product",
    order = "z[sae]-i[e-coolant-charge]",
    stack_size = 50,
    weight = 4000
  },

  -- Fulgora / Aquilo, through the orbital step. The winding is drawn out in
  -- freefall, where nothing settles out of the alloy while it forms.
  {
    type = "recipe",
    name = "sae-field-conductor",
    categories = { "crafting" },
    energy_required = 30,
    ingredients =
    {
      { type = "item", name = "sae-superconducting-winding", amount = 2 },
      { type = "item", name = "sae-homogenised-ingot", amount = 1 }
    },
    results = { { type = "item", name = "sae-field-conductor", amount = 1 } },
    surface_conditions = { { property = "gravity", max = 0 } },
    enabled = false
  },

  -- Vulcanus / Fulgora, through the settling line.
  {
    type = "recipe",
    name = "sae-magnetic-core-billet",
    categories = { "crafting-with-fluid" },
    energy_required = 24,
    ingredients =
    {
      { type = "item", name = "sae-magnetar-alloy", amount = 2 },
      { type = "fluid", name = "sae-settled-melt", amount = 100 }
    },
    results = { { type = "item", name = "sae-magnetic-core-billet", amount = 1 } },
    surface_conditions = { { property = "gravity", min = 45 } },
    enabled = false
  },

  -- Vulcanus / Gleba, through the whisker beds. Grown metal reinforcing an
  -- alloy that was itself grown.
  {
    type = "recipe",
    name = "sae-reinforced-frame",
    categories = { "crafting" },
    energy_required = 24,
    ingredients =
    {
      { type = "item", name = "sae-cultured-alloy", amount = 2 },
      { type = "item", name = "sae-kamacite-whiskers", amount = 8 }
    },
    results = { { type = "item", name = "sae-reinforced-frame", amount = 1 } },
    surface_conditions = { { property = "pressure", min = 1, max = 9 } },
    enabled = false
  },

  -- Fulgora / Gleba, through the raw melt. Poured hot around the polymer so it
  -- takes the shape of what it will insulate.
  {
    type = "recipe",
    name = "sae-insulation-sleeve",
    categories = { "crafting-with-fluid" },
    energy_required = 16,
    ingredients =
    {
      { type = "item", name = "sae-bio-polymer", amount = 4 },
      { type = "fluid", name = "sae-molten-kamacite", amount = 50 }
    },
    results = { { type = "item", name = "sae-insulation-sleeve", amount = 2 } },
    surface_conditions = { { property = "pressure", min = 1, max = 9 } },
    enabled = false
  },

  -- Gleba / Aquilo, through the helium.
  {
    type = "recipe",
    name = "sae-coolant-charge",
    categories = { "crafting-with-fluid" },
    energy_required = 20,
    ingredients =
    {
      { type = "fluid", name = "sae-cryoprotectant", amount = 100 },
      { type = "fluid", name = "sae-helium-3", amount = 50 },
      { type = "item", name = "sae-kamacite-plate", amount = 4 }
    },
    results = { { type = "item", name = "sae-coolant-charge", amount = 1 } },
    surface_conditions = { { property = "pressure", min = 1, max = 9 } },
    enabled = false
  },

  -- Stage two: the Core's own goods.
  --
  -- Research uses the material sciences -- settling, growth, homogenisation.
  -- Construction uses the joining. Cold welding earns its place here.
  {
    type = "recipe",
    name = "sae-geodynamic-science-pack",
    categories = { "crafting" },
    energy_required = 20,
    ingredients =
    {
      { type = "item", name = "sae-field-conductor", amount = 1 },
      { type = "item", name = "sae-reinforced-frame", amount = 1 },
      { type = "item", name = "sae-kamacite-whiskers", amount = 4 }
    },
    results = { { type = "item", name = "sae-geodynamic-science-pack", amount = 2 } },
    surface_conditions = { { property = "pressure", min = 1, max = 9 } },
    allow_productivity = true,
    enabled = false
  },
  {
    type = "tool",
    name = "sae-geodynamic-science-pack",
    icon = "__space-age__/graphics/icons/promethium-science-pack.png",
    subgroup = "science-pack",
    order = "z[sae]-geodynamic",
    stack_size = 200,
    weight = 1000,
    durability = 1,
    durability_description_key = "description.science-pack-remaining-amount-key",
    factoriopedia_durability_description_key = "description.factoriopedia-science-pack-remaining-amount-key",
    random_tint_color = { r = 0.75, g = 0.70, b = 0.55, a = 1 }
  }
})
