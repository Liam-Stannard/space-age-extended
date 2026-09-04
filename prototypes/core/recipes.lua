-- The Core's local chain.
--
-- Three of the four Core mechanics live here. Gravity settling only runs where
-- weight can do the sorting (gravity 45+, which is the Core alone -- Vulcanus,
-- the next heaviest world, is 40). Orbital homogenisation only runs where
-- nothing settles at all. Cold welding only runs where there is no air.

data:extend({
  -- The settling line runs in a foundry: two fluid boxes in and two out, which
  -- an assembler does not have. A recipe with more fluid connections than its
  -- machine has boxes is accepted silently by set_recipe and then never runs.
  {
    type = "recipe",
    name = "sae-kamacite-smelting",
    categories = { "smelting" },
    energy_required = 6.4,
    ingredients = { { type = "item", name = "sae-kamacite-ore", amount = 2 } },
    results = { { type = "item", name = "sae-kamacite-plate", amount = 1 } },
    enabled = false
  },

  -- Settling, in two forms. The same melt becomes either metal or power, and
  -- which one is a recipe the player chooses rather than a slider.
  --
  -- A steam turbine takes 60 steam a second at 500 degrees for 5.8MW. Quenched
  -- settling gives 900 steam per 16-second craft -- 56 a second, near enough
  -- one turbine per vessel -- against 150 for the metal-heavy form. So a line
  -- run for power is roughly six times the electricity and less than half the
  -- metal, which is a decision rather than a preference.
  {
    type = "recipe",
    name = "sae-gravity-settling",
    icon = "__space-age__/graphics/icons/fluid/molten-copper.png",
    icon_size = 64,
    categories = { "metallurgy" },
    energy_required = 16,
    ingredients = { { type = "fluid", name = "sae-molten-kamacite", amount = 100 } },
    results =
    {
      { type = "fluid", name = "sae-settled-melt", amount = 60 },
      { type = "item", name = "sae-dross", amount = 2 },
      { type = "fluid", name = "steam", amount = 150, temperature = 500 }
    },
    surface_conditions = { { property = "gravity", min = 45 } },
    allow_productivity = true,
    enabled = false
  },
  {
    type = "recipe",
    name = "sae-quenched-settling",
    icon = "__base__/graphics/icons/fluid/steam.png",
    icon_size = 64,
    categories = { "metallurgy" },
    energy_required = 16,
    ingredients = { { type = "fluid", name = "sae-molten-kamacite", amount = 100 } },
    results =
    {
      { type = "fluid", name = "sae-settled-melt", amount = 25 },
      { type = "item", name = "sae-dross", amount = 2 },
      { type = "fluid", name = "steam", amount = 900, temperature = 500 }
    },
    surface_conditions = { { property = "gravity", min = 45 } },
    enabled = false
  },

  -- Dross has two outlets: it is the ground beds are made of, and it can be put
  -- back through settling to recover the metal still in it.
  {
    type = "recipe",
    name = "sae-dross-resettling",
    categories = { "metallurgy" },
    energy_required = 12,
    ingredients =
    {
      { type = "item", name = "sae-dross", amount = 10 },
      { type = "fluid", name = "sae-molten-kamacite", amount = 20 }
    },
    results = { { type = "fluid", name = "sae-settled-melt", amount = 20 } },
    surface_conditions = { { property = "gravity", min = 45 } },
    enabled = false
  },
  {
    type = "recipe",
    name = "sae-whisker-bed",
    categories = { "crafting" },
    energy_required = 2,
    ingredients =
    {
      { type = "item", name = "sae-dross", amount = 4 },
      { type = "item", name = "sae-kamacite-plate", amount = 1 }
    },
    results = { { type = "item", name = "sae-whisker-bed", amount = 4 } },
    enabled = false
  },

  {
    type = "recipe",
    name = "sae-ingot-casting",
    categories = { "metallurgy" },
    energy_required = 8,
    ingredients = { { type = "fluid", name = "sae-settled-melt", amount = 100 } },
    results = { { type = "item", name = "sae-cast-ingot", amount = 1 } },
    allow_productivity = true,
    enabled = false
  },
  {
    -- Only where nothing settles. Gravity is the thing being escaped.
    type = "recipe",
    name = "sae-orbital-homogenisation",
    categories = { "crafting" },
    energy_required = 30,
    ingredients = { { type = "item", name = "sae-cast-ingot", amount = 2 } },
    results = { { type = "item", name = "sae-homogenised-ingot", amount = 1 } },
    surface_conditions = { { property = "gravity", max = 0 } },
    allow_productivity = true,
    enabled = false
  },

  {
    type = "recipe",
    name = "sae-seed-plate",
    categories = { "crafting-with-fluid" },
    energy_required = 4,
    ingredients =
    {
      { type = "item", name = "sae-kamacite-plate", amount = 1 },
      { type = "fluid", name = "sae-settled-melt", amount = 20 }
    },
    results = { { type = "item", name = "sae-seed-plate", amount = 1 } },
    enabled = false
  },

  {
    -- Clean metal bonds on contact in vacuum. The machine is a clamp, not a
    -- furnace: this costs time and place rather than throughput.
    type = "recipe",
    name = "sae-cold-welding",
    categories = { "crafting" },
    energy_required = 40,
    ingredients =
    {
      { type = "item", name = "sae-kamacite-plate", amount = 4 },
      { type = "item", name = "sae-kamacite-whiskers", amount = 2 }
    },
    results = { { type = "item", name = "sae-welded-plate", amount = 1 } },
    surface_conditions = { { property = "pressure", max = 9 } },
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
  },
  {
    type = "recipe",
    name = "sae-bed-tender",
    categories = { "crafting" },
    energy_required = 5,
    ingredients =
    {
      { type = "item", name = "sae-kamacite-plate", amount = 20 },
      { type = "item", name = "electric-engine-unit", amount = 10 },
      { type = "item", name = "processing-unit", amount = 10 }
    },
    results = { { type = "item", name = "sae-bed-tender", amount = 1 } },
    enabled = false
  }
})
