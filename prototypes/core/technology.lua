-- Core Discovery.
--
-- Measured, not assumed: a planet nothing unlocks is unreachable. A platform
-- reports no_path to it however well-formed the connection is, and researching
-- every other technology does not help, because none of them names it. This is
-- the sixth tech tree's entry point, and it sits behind promethium science
-- because the Core is past the point where that research already takes you.

local derive = require("prototypes.derive")

-- A technology still wearing a vanilla icon is a placeholder like a building
-- wearing vanilla sprites, and it is recorded the same way, so the data-stage
-- report counts it and grep finds it.
local PLACEHOLDER_ICON = "__space-age__/graphics/technology/aquilo.png"
local function tech_icon(tech, icon)
  if icon then
    tech.icon = icon
  else
    tech.icon = PLACEHOLDER_ICON
    derive.placeholder_art(tech, "wears Aquilo's technology icon until its own exists")
  end
  tech.icon_size = 256
  return tech
end

data:extend({
  {
    type = "technology",
    name = "sae-core-discovery",
    -- The planet constant in the corner, as every planet-discovery technology
    -- in Space Age carries it.
    icons = util.technology_icon_constant_planet(
      "__space-age-extended__/graphics/technology/sae-core-discovery.png"),
    essential = true,
    effects =
    {
      {
        type = "unlock-space-location",
        space_location = "sae-core",
        use_icon_overlay_constant = true
      }
    },
    prerequisites = { "promethium-science-pack" },
    unit =
    {
      count = 500,
      ingredients =
      {
        { "automation-science-pack", 1 },
        { "logistic-science-pack", 1 },
        { "chemical-science-pack", 1 },
        { "production-science-pack", 1 },
        { "utility-science-pack", 1 },
        { "space-science-pack", 1 },
        { "metallurgic-science-pack", 1 },
        { "electromagnetic-science-pack", 1 },
        { "agricultural-science-pack", 1 },
        { "cryogenic-science-pack", 1 },
        { "promethium-science-pack", 1 }
      },
      time = 60
    }
  }
})

-- Tier 0 of the Core's tree: standing the foothold up.
--
-- **Every technology here is a trigger technology.** A technology takes `unit`
-- *or* `research_trigger`, never both: the trigger replaces the cost outright
-- while prerequisites still gate when it can fire, so the tree keeps its shape
-- and only the currency changes. It is the move vanilla makes on every new
-- world -- the first local technology is paid for by doing the local thing.
--
-- **The rule every trigger obeys**: the thing that fires it is reachable from
-- that technology's own prerequisites and no further. A trigger needing
-- something from a non-prerequisite is a technology that can never fire, and it
-- would not read as a bug -- it would read as the tree simply stopping.
--
-- Only `mine-entity` and `craft-item` are used, deliberately: they are the two
-- whose field layout is unambiguous, and a trigger that fails to load takes the
-- whole mod with it.
--
-- Every technology lists only the one before it. The chain already carries
-- everything further back, and a redundant prerequisite draws a second arrow
-- across the technology screen for a dependency the first one already states.
-- The one exception is Vent tapping's Uranium mining, which the chain does not
-- carry; see there.
--
-- The melt line, the farm, the lift and everything geodynamic went with the cut.
--
local function landfall(name, prereqs, effects, trigger, icon)
  return tech_icon(
  {
    type = "technology",
    name = name,
    effects = effects,
    prerequisites = prereqs,
    research_trigger = trigger
  }, icon)
end

local KAMACITE_PROCESSING = "sae-kamacite-processing"

data:extend({
  landfall("sae-crust-tapping", { "sae-core-discovery" },
    {
      { type = "unlock-recipe", recipe = "sae-gas-pump" },
      { type = "unlock-recipe", recipe = "sae-crust-turbine" }
    },
    { type = "mine-entity", entities = { "sae-core-boulder" } },
    "__space-age-extended__/graphics/technology/sae-crust-tapping.png"),

  landfall(KAMACITE_PROCESSING, { "sae-crust-tapping" },
    {
      { type = "unlock-recipe", recipe = "sae-heavy-crusher" },
      { type = "unlock-recipe", recipe = "sae-crushing" },
      { type = "unlock-recipe", recipe = "sae-kamacite-smelting" },
      { type = "unlock-recipe", recipe = "sae-fines-smelting" }
    },
    { type = "mine-entity", entities = { "sae-kamacite-ore" } }),

  -- **Uranium mining is here for the engine, not the story.** The kamacite vent
  -- needs helium-3 to mine, and the engine refuses a player's build of any drill
  -- on a resource that needs a fluid until the force has mining-with-fluid.
  -- Uranium mining is the only technology that grants it, and nothing else in
  -- the Core's chain leads to it, so without this the Vent Pump could only be
  -- placed by script. It costs a second arrow on the technology screen.
  landfall("sae-vent-tapping", { KAMACITE_PROCESSING, "uranium-mining" },
    {
      { type = "unlock-recipe", recipe = "sae-vent-pump" }
    },
    { type = "craft-item", item = "sae-kamacite-fines", count = 50 },
    "__space-age-extended__/graphics/technology/sae-vent-tapping.png"),

  -- Power that does not run out, earned by the first machine that outgrows the
  -- turbines.
  --
  -- A pump and a turbine are landing-day power and Crust Tapping says as much.
  -- The Vent Pump is the first building on this planet that runs continuously
  -- and the first that everything downstream waits on, so crafting one is the
  -- moment a player finds out what the turbines are worth. That is when the
  -- planet should offer them the fuel it precipitates for itself.
  --
  -- The trigger obeys the rule this tier is built on: `sae-vent-pump` is Vent
  -- Tapping's own recipe and Vent Tapping is this technology's only
  -- prerequisite, so what fires it is reachable from its prerequisites and no
  -- further.
  landfall("sae-radiant-power", { "sae-vent-tapping" },
    {
      { type = "unlock-recipe", recipe = "sae-radiant-precipitation" },
      { type = "unlock-recipe", recipe = "sae-radiant-generator" },
      { type = "unlock-recipe", recipe = "sae-radiant-crushing" }
    },
    { type = "craft-item", item = "sae-vent-pump" },
    "__space-age-extended__/graphics/technology/sae-radiant-power.png")
})

-- Fulgora <-> Aquilo. Available once both worlds are running, which is what
-- "after Aquilo" means in practice, and researched on packs the player already
-- makes: this is a cross-planet tree, not Core content.
data:extend({
  {
    type = "technology",
    name = "sae-fa-cryogen",
    icon = "__space-age-extended__/graphics/technology/sae-fa-cryogen.png",
    icon_size = 256,
    effects =
    {
      { type = "unlock-recipe", recipe = "sae-cryogen" }
    },
    prerequisites = { "cryogenic-science-pack" },
    unit =
    {
      count = 300,
      ingredients =
      {
        { "automation-science-pack", 1 }, { "logistic-science-pack", 1 },
        { "chemical-science-pack", 1 }, { "production-science-pack", 1 },
        { "utility-science-pack", 1 }, { "space-science-pack", 1 },
        { "electromagnetic-science-pack", 1 }, { "cryogenic-science-pack", 1 }
      },
      time = 60
    }
  },
  {
    type = "technology",
    name = "sae-fa-fluorinated-holmium",
    icon = "__space-age-extended__/graphics/technology/sae-fa-fluorinated-holmium.png",
    icon_size = 256,
    -- Recovery moved here from `sae-fa-cryogen`. Nothing makes spent cryogen
    -- until fluorination does, so unlocking the loop-closer a technology early
    -- put a recipe in the menu that could not run.
    effects =
    {
      { type = "unlock-recipe", recipe = "sae-fluorinated-holmium" },
      { type = "unlock-recipe", recipe = "sae-cryogen-recovery" }
    },
    prerequisites = { "sae-fa-cryogen" },
    unit =
    {
      count = 400,
      ingredients =
      {
        { "automation-science-pack", 1 }, { "logistic-science-pack", 1 },
        { "chemical-science-pack", 1 }, { "production-science-pack", 1 },
        { "utility-science-pack", 1 }, { "space-science-pack", 1 },
        { "electromagnetic-science-pack", 1 }, { "cryogenic-science-pack", 1 }
      },
      time = 60
    }
  },
  {
    type = "technology",
    name = "sae-fa-superconducting-winding",
    icon = "__space-age-extended__/graphics/technology/sae-fa-superconducting-winding.png",
    icon_size = 256,
    essential = true,
    effects =
    {
      { type = "unlock-recipe", recipe = "sae-superconducting-winding" },
      { type = "unlock-recipe", recipe = "sae-superconducting-store" }
    },
    prerequisites = { "sae-fa-fluorinated-holmium" },
    unit =
    {
      count = 600,
      ingredients =
      {
        { "automation-science-pack", 1 }, { "logistic-science-pack", 1 },
        { "chemical-science-pack", 1 }, { "production-science-pack", 1 },
        { "utility-science-pack", 1 }, { "space-science-pack", 1 },
        { "electromagnetic-science-pack", 1 }, { "cryogenic-science-pack", 1 }
      },
      time = 60
    }
  }
})
