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
    icons =
    {
      { icon = "__space-age-extended__/graphics/icons/fluid/settled-melt.png" },
      { icon = "__space-age-extended__/graphics/icons/dross.png", scale = 0.25, shift = { 8, 8 } }
    },
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
    icons =
    {
      { icon = "__space-age-extended__/graphics/icons/fluid/settled-melt.png" },
      { icon = "__base__/graphics/icons/fluid/steam.png", scale = 0.25, shift = { 8, 8 } }
    },
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

--------------------------------------------------------------------------------
-- What the nine Core machines run.
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

  -- N3. Classification. A tenth of the mass is lost, so classifying is not free
  -- and stockpiling raw dross stays a legitimate choice.
  {
    type = "recipe",
    name = "sae-classification",
    icon = "__space-age-extended__/graphics/icons/dross.png",
    categories = { "sae-classification" },
    energy_required = 5,
    ingredients = { { type = "item", name = "sae-dross", amount = 10 } },
    results =
    {
      { type = "item", name = "sae-bed-dross", amount = 6 },
      { type = "item", name = "sae-kamacite-fines", amount = 3 }
    },
    enabled = false
  },

  -- N4. Magnetic separation, on a world with no field to borrow.
  {
    type = "recipe",
    name = "sae-magnetic-separation",
    icon = "__space-age-extended__/graphics/icons/dross.png",
    categories = { "sae-separation" },
    energy_required = 4,
    ingredients = { { type = "item", name = "sae-crushed-kamacite", amount = 6 } },
    results =
    {
      { type = "item", name = "sae-schreibersite", amount = 1 },
      { type = "item", name = "sae-kamacite-fines", amount = 2 }
    },
    enabled = false
  },

  -- N5. The comb and the mat. Combing is four times slower per whisker, so
  -- neither is the right answer and the ratio is a standing decision.
  {
    type = "recipe",
    name = "sae-whisker-combing",
    categories = { "sae-fibre" },
    energy_required = 12,
    ingredients = { { type = "item", name = "sae-kamacite-whiskers", amount = 8 } },
    results = { { type = "item", name = "sae-whisker-tow", amount = 1 } },
    enabled = false
  },
  {
    type = "recipe",
    name = "sae-whisker-matting",
    categories = { "sae-fibre" },
    energy_required = 3,
    ingredients = { { type = "item", name = "sae-kamacite-whiskers", amount = 4 } },
    results = { { type = "item", name = "sae-whisker-felt", amount = 1 } },
    enabled = false
  },

  -- N6. The relief valve. Worse than settling at making melt and far worse than
  -- a vent at making helium: the bad trade taken when one of them has run out.
  {
    type = "recipe",
    name = "sae-degassing",
    icon = "__space-age-extended__/graphics/icons/fluid/helium-3.png",
    categories = { "sae-degassing" },
    energy_required = 20,
    ingredients = { { type = "fluid", name = "sae-molten-kamacite", amount = 100 } },
    results =
    {
      { type = "fluid", name = "sae-helium-3", amount = 10 },
      { type = "fluid", name = "sae-settled-melt", amount = 40 }
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
  },

  -- N9. Helium and a great deal of electricity, into something that will not
  -- keep. See items.lua for the spoil timer that is the mechanic.
  {
    type = "recipe",
    name = "sae-ignition-charge",
    categories = { "sae-ignition-charge" },
    energy_required = 4,
    ingredients = { { type = "fluid", name = "sae-helium-3", amount = 25 } },
    results = { { type = "item", name = "sae-ignition-charge", amount = 1 } },
    enabled = false
  }
})

--------------------------------------------------------------------------------
-- Re-sourcing, so the new machines are not optional decoration.
--
-- Both of these are required by a spec rather than chosen here.
--
-- Plate smelting took raw ore, which made the Drop Crusher skippable: a player
-- could ignore tier one entirely and still have plate. It takes crushed kamacite
-- now, and the crusher's own spec says so in as many words.
--
-- Whisker beds were laid on raw dross, which left the Dross Classifier with
-- nothing that needed it. They are laid on bed-grade dross now.
--------------------------------------------------------------------------------

data.raw.recipe["sae-kamacite-smelting"].ingredients =
  { { type = "item", name = "sae-crushed-kamacite", amount = 3 } }

data.raw.recipe["sae-whisker-bed"].ingredients =
{
  { type = "item", name = "sae-bed-dross", amount = 4 },
  { type = "item", name = "sae-kamacite-plate", amount = 1 }
}


--------------------------------------------------------------------------------
-- T3, carbonyl chemistry, and the flux that feeds it.
--
-- This is what fills `sae-sintering`, the category the Vacuum Furnace has been
-- carrying with nothing in it, and it is half that furnace's stated reason to
-- exist. It also gives schreibersite its only consumer, which is what makes the
-- Coil Separator worth building rather than a curiosity.
--
-- Numbers are a first pass and should be played before they are trusted. The one
-- that carries meaning is the 90% carbon monoxide recovery: carbon is a catalyst
-- with losses, not a consumable, so the corridor delivers a trickle rather than
-- a torrent and modules on the decomposition step visibly lower the freight bill.
--------------------------------------------------------------------------------

data:extend({
  {
    type = "recipe",
    name = "sae-carbon-monoxide",
    icon = "__space-age-extended__/graphics/icons/fluid/helium-3.png",
    categories = { "chemistry" },
    energy_required = 2,
    ingredients =
    {
      { type = "item", name = "carbon", amount = 1 },
      { type = "fluid", name = "sae-settled-melt", amount = 20 }
    },
    results = { { type = "fluid", name = "sae-carbon-monoxide", amount = 50 } },
    enabled = false
  },
  {
    -- Cold. Metal walks into the pipe here.
    type = "recipe",
    name = "sae-metal-carbonyl",
    categories = { "chemistry" },
    energy_required = 4,
    ingredients =
    {
      { type = "item", name = "sae-kamacite-fines", amount = 4 },
      { type = "fluid", name = "sae-carbon-monoxide", amount = 50 }
    },
    results = { { type = "fluid", name = "sae-metal-carbonyl", amount = 50 } },
    enabled = false
  },
  {
    -- Hot. The metal falls out and 45 of the 50 carrier units come back.
    type = "recipe",
    name = "sae-carbonyl-powder",
    icon = "__space-age-extended__/graphics/icons/kamacite-plate.png",
    categories = { "chemistry" },
    energy_required = 4,
    ingredients = { { type = "fluid", name = "sae-metal-carbonyl", amount = 50 } },
    results =
    {
      { type = "item", name = "sae-carbonyl-powder", amount = 1 },
      { type = "fluid", name = "sae-carbon-monoxide", amount = 45 }
    },
    enabled = false
  },
  {
    type = "recipe",
    name = "sae-phosphide-flux",
    categories = { "metallurgy" },
    energy_required = 8,
    ingredients =
    {
      { type = "item", name = "sae-schreibersite", amount = 2 },
      { type = "fluid", name = "sae-settled-melt", amount = 30 }
    },
    results = { { type = "fluid", name = "sae-phosphide-flux", amount = 40 } },
    enabled = false
  },
  {
    -- The `sae-sintering` recipe, and the only one. One solid ingredient and one
    -- fluid, which is exactly what a furnace can pick a recipe from -- see the
    -- flux note in fluids.lua.
    type = "recipe",
    name = "sae-sintered-preform",
    categories = { "sae-sintering" },
    energy_required = 6,
    ingredients =
    {
      { type = "item", name = "sae-carbonyl-powder", amount = 4 },
      { type = "fluid", name = "sae-phosphide-flux", amount = 20 }
    },
    results = { { type = "item", name = "sae-sintered-preform", amount = 1 } },
    enabled = false
  }
})
