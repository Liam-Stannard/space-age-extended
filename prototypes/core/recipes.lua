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
  -- one turbine per vessel -- against 150 for the metal-heavy form.
  --
  -- **Net of the foundry, which the six-times figure used to leave out.** The
  -- vessel itself draws 2.5MW, so quenched settling clears **+2.96MW** and the
  -- metal-heavy form runs at **-1.59MW**: one route is paid for power, the other
  -- pays for metal. That is the real shape of the decision, and it is the number
  -- the arc mast has to be tuned against -- see storms.lua, where a mast used to
  -- out-earn a whole quenched vessel by more than two to one while costing
  -- nothing at all.
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


--------------------------------------------------------------------------------
-- The lift, and how the Core pays for it.
--
-- `04-the-core.md` §4 puts half the endgame in orbit: settling happens on the
-- surface under 50 g, homogenisation happens on a platform where nothing
-- settles, and the same material needs both. That loop is flown, and every trip
-- costs a rocket.
--
-- A rocket part is a processing unit, a low density structure and a rocket fuel,
-- and **the Core could make none of the three.** Low density structure wants
-- copper and plastic; rocket fuel wants light oil; the Core has no copper, no
-- carbon and nothing that ever lived. So the lift the endgame is built around
-- was, in full, a freight problem -- and by weight it is the dominant one: 50
-- rocket parts need 50 structures at 5 t and 50 fuels at 10 t, which is 750 of
-- the 1,000 tonnes a rocket lifts. Three quarters of a cargo rocket spent
-- shipping the means to launch the next one.
--
-- These are the two alternates that fix the heavy end of it, in the shape
-- vanilla already uses for exactly this: Vulcanus does not get a new rocket
-- part, it gets `casting-low-density-structure` beside the assembled one, and
-- Gleba gets `rocket-fuel-from-jelly`. A planet earns a different route to the
-- same item.
--
-- **The processing unit is deliberately not among them.** It is twenty
-- electronic circuits, two advanced circuits and sulfuric acid -- copper all the
-- way down, on a world that has none -- and it is the light quarter of the
-- weight. Leaving it imported keeps the corridor carrying the brains and lets
-- the Core carry the mass, which is the right division for a planet whose whole
-- premise is that it is rich in metal and poor in everything else. The capstone
-- products are untouched by any of this: §3's guarantee rests on those, and all
-- five still arrive from their own pair of planets.
--------------------------------------------------------------------------------

data:extend({
  {
    -- Low density, high strength, and it is the whiskers that make it so.
    -- Single-crystal metal fibre is absurdly strong in tension and useless in
    -- every other direction -- which is what a composite is for, and what
    -- `06-core-production-tree.md` T5 says the comb is for. Combed tow rather
    -- than felt, because a structure wants its fibres aligned.
    --
    -- This is the recipe that ties the lift to the farm. Whiskers grow at the
    -- rate they grow, so the answer to "launch more often" is more floor -- the
    -- Core's signature constraint, now applied to its own logistics.
    type = "recipe",
    name = "sae-cast-structure",
    -- **`auto_recycle = false`, and it is not optional.** `__recycler__`
    -- walks every recipe in the game and generates `<product>-recycling` by
    -- inverting it -- so when two recipes make the same product, whichever the
    -- iteration reaches last silently becomes the recycling result for
    -- everyone. This one won, and rewrote vanilla's `low-density-structure-recycling`
    -- to return the Core's materials: recycling a structure on Fulgora came
    -- back as kamacite, which put this planet's exclusive metal into every
    -- scrap line in the game.
    --
    -- `auto_recycle` is the opt-out the generator actually reads -- Space Age
    -- sets it on 73 of its own recipes. (`allow_decomposition` is *not* it,
    -- which cost an hour: the recycler sets that flag on the recipes it
    -- creates, and never reads it on the recipes it consumes.)
    auto_recycle = false,
    categories = { "metallurgy" },
    energy_required = 15,
    ingredients =
    {
      { type = "fluid", name = "sae-settled-melt", amount = 80 },
      { type = "item", name = "sae-whisker-tow", amount = 1 }
    },
    results = { { type = "item", name = "low-density-structure", amount = 2 } },
    subgroup = "sae-core-processes",
    order = "z[sae]-ha[cast-structure]",
    allow_productivity = true,
    enabled = false
  },
  {
    -- Propellant out of the crust vents, and this is the second job that
    -- building has ever had. The tap and its turbine were a landing-day
    -- foothold and nothing after it -- 1.8 MW, then a machine the player walks
    -- past for the rest of the game. Now a vent field is worth returning to,
    -- and the lift is sited on the map the way everything else on this planet
    -- is: you launch from where the gas is.
    --
    -- 200 gas a craft is 13.3/s, so one tap at 30/s runs a little over two of
    -- these -- or a little under one alongside three turbines. The tap is a
    -- decision again rather than a formality.
    type = "recipe",
    name = "sae-crust-propellant",
    -- **`auto_recycle = false`, and it is not optional.** `__recycler__`
    -- walks every recipe in the game and generates `<product>-recycling` by
    -- inverting it -- so when two recipes make the same product, whichever the
    -- iteration reaches last silently becomes the recycling result for
    -- everyone. This one won, and rewrote vanilla's `rocket-fuel-recycling`
    -- to return the Core's materials: recycling rocket fuel on Fulgora came
    -- back as kamacite, which put this planet's exclusive metal into every
    -- scrap line in the game.
    --
    -- `auto_recycle` is the opt-out the generator actually reads -- Space Age
    -- sets it on 73 of its own recipes. (`allow_decomposition` is *not* it,
    -- which cost an hour: the recycler sets that flag on the recipes it
    -- creates, and never reads it on the recipes it consumes.)
    auto_recycle = false,
    categories = { "chemistry" },
    energy_required = 15,
    ingredients =
    {
      { type = "fluid", name = "sae-crust-gas", amount = 200 },
      { type = "item", name = "sae-kamacite-plate", amount = 1 }
    },
    results = { { type = "item", name = "rocket-fuel", amount = 1 } },
    subgroup = "sae-core-processes",
    order = "z[sae]-hb[crust-propellant]",
    allow_productivity = true,
    enabled = false
  }
})


--------------------------------------------------------------------------------
-- Vacuum electronics, and the Core's answer to copper.
--
-- Every circuit in the game is copper and plastic, and the Core has neither: no
-- copper ore, no carbon, nothing that ever lived. So processing units were
-- freight for ever -- ten in a Bed Tender, twenty in a Ring Mast, **two hundred
-- in the Ignition Array** -- and the planet's own electronics industry was a
-- shipping manifest.
--
-- **The way out is not to import copper. It is to stop needing a solid at all.**
-- A sharp enough metal tip in a hard enough vacuum emits electrons under field
-- alone -- cold, with no heater and no semiconductor. That is field emission,
-- it is real, and vacuum microelectronics is prized in exactly the conditions
-- this planet has: no atmosphere to break down, and radiation hardness a doped
-- wafer cannot match. The switching element is a gap.
--
-- Which means the Core's two dead ends are its two ingredients:
--
--   * **Whiskers**, which are single-crystal metal fibres -- and a field emitter
--     is a sharp single-crystal tip. `sae-whisker-combing` already aligns them,
--     because a composite wants its fibres in one direction; an emitter array
--     wants its tips in one direction for the same reason and the same recipe
--     serves both. The comb was the farm's step and it is now the fab's.
--   * **Vacuum**, which `06-core-production-tree.md` T8 names as "the Core's one
--     free advantage" and then observes that "nothing currently uses it". This
--     uses it. Everywhere else these recipes are refused outright, because a
--     pressure of 10 is a device full of air.
--
-- **This is a lateral trade, not a better circuit.** A processing unit off this
-- line costs about fourteen whiskers, and whiskers come at four per plant every
-- four minutes -- so the Core's electronics run at the speed of *growing area*,
-- which is the constraint the whole planet is built around. A Nauvis copper
-- line will out-produce it and always should. What this buys is that two
-- hundred processing units for the Array are now a farm the player builds
-- rather than a queue of cargo pods, and the corridor gets to carry things that
-- matter: the five capstones, the carbon, the engines and the steel.
--------------------------------------------------------------------------------

data:extend({
  {
    -- Tips one way, gate above, sealed in the ambient vacuum. The plate is the
    -- gate and the anode; the tow is every emitter on the array.
    type = "recipe",
    name = "sae-emitter-array",
    categories = { "crafting" },
    energy_required = 8,
    ingredients =
    {
      { type = "item", name = "sae-whisker-tow", amount = 1 },
      { type = "item", name = "sae-kamacite-plate", amount = 2 }
    },
    results = { { type = "item", name = "sae-emitter-array", amount = 2 } },
    surface_conditions = { { property = "pressure", max = 9 } },
    allow_productivity = true,
    enabled = false
  },
  {
    -- Switching. One array is a great many gaps.
    type = "recipe",
    name = "sae-valve-logic",
    -- **`auto_recycle = false`, and it is not optional.** `__recycler__`
    -- walks every recipe in the game and generates `<product>-recycling` by
    -- inverting it -- so when two recipes make the same product, whichever the
    -- iteration reaches last silently becomes the recycling result for
    -- everyone. This one won, and rewrote vanilla's `advanced-circuit-recycling`
    -- to return the Core's materials: recycling an advanced circuit on Fulgora came
    -- back as kamacite, which put this planet's exclusive metal into every
    -- scrap line in the game.
    --
    -- `auto_recycle` is the opt-out the generator actually reads -- Space Age
    -- sets it on 73 of its own recipes. (`allow_decomposition` is *not* it,
    -- which cost an hour: the recycler sets that flag on the recipes it
    -- creates, and never reads it on the recipes it consumes.)
    auto_recycle = false,
    categories = { "crafting" },
    energy_required = 6,
    ingredients =
    {
      { type = "item", name = "sae-emitter-array", amount = 1 },
      { type = "item", name = "sae-kamacite-plate", amount = 1 }
    },
    results = { { type = "item", name = "advanced-circuit", amount = 2 } },
    surface_conditions = { { property = "pressure", max = 9 } },
    subgroup = "sae-core-processes",
    order = "z[sae]-ia[valve-logic]",
    allow_productivity = true,
    enabled = false
  },
  {
    -- The same trick, stacked, in a cold-welded can. Slow on purpose: this is a
    -- vacuum process, and vacuum processes on this planet cost place and
    -- patience rather than throughput.
    --
    -- **The steam is a bake-out, and it is the reason this is not hand-craftable.**
    -- Vanilla's processing unit takes sulfuric acid, so no one has ever made one
    -- in their pocket; without a fluid this recipe quietly broke that. The fluid
    -- to reach for is the one real vacuum devices actually need: a sealed
    -- envelope holds its vacuum only if the surfaces inside it have been baked
    -- until they stop giving gas back, and the Core raises 500-degree steam as
    -- the byproduct of settling its own melt.
    --
    -- Which puts electronics on the metal-or-steam split -- the decision
    -- `04-the-core.md` §2 calls the planet's central problem -- as a third
    -- claimant beside metal and electricity. Every processing unit is steam that
    -- did not turn a turbine. `minimum_temperature` is what makes that true:
    -- ordinary 15-degree steam is refused, so this has to come off the settling
    -- line (or a reactor, which the Core's pressure does allow) rather than out
    -- of any pipe.
    type = "recipe",
    name = "sae-valve-processor",
    -- **`auto_recycle = false`, and it is not optional.** `__recycler__`
    -- walks every recipe in the game and generates `<product>-recycling` by
    -- inverting it -- so when two recipes make the same product, whichever the
    -- iteration reaches last silently becomes the recycling result for
    -- everyone. This one won, and rewrote vanilla's `processing-unit-recycling`
    -- to return the Core's materials: recycling a processing unit on Fulgora came
    -- back as kamacite, which put this planet's exclusive metal into every
    -- scrap line in the game.
    --
    -- `auto_recycle` is the opt-out the generator actually reads -- Space Age
    -- sets it on 73 of its own recipes. (`allow_decomposition` is *not* it,
    -- which cost an hour: the recycler sets that flag on the recipes it
    -- creates, and never reads it on the recipes it consumes.)
    auto_recycle = false,
    categories = { "crafting-with-fluid" },
    energy_required = 12,
    ingredients =
    {
      { type = "item", name = "sae-emitter-array", amount = 3 },
      { type = "item", name = "sae-welded-plate", amount = 1 },
      { type = "fluid", name = "steam", amount = 100, minimum_temperature = 500 }
    },
    results = { { type = "item", name = "processing-unit", amount = 1 } },
    surface_conditions = { { property = "pressure", max = 9 } },
    subgroup = "sae-core-processes",
    order = "z[sae]-ib[valve-processor]",
    allow_productivity = true,
    enabled = false
  }
})
