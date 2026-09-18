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
-- This branch is the landing and nothing past it, so the chain is short:
--
--   mine a boulder      -> Crust tapping    (power at all)
--   craft a crust tap   -> Core survey      (drill, crusher, smelter)
--   craft a vent pump   -> Radiant power    (the generator, and its fuel)
--
-- The melt line, the farm, the lift and everything geodynamic are on master.
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

data:extend({
  -- Landing-day power, and now literally the first thing the player does.
  --
  -- The boulder was already "the only ore on the planet obtainable before a
  -- drill is standing" (resources.lua), described there as "a genuine early
  -- move rather than decoration with a yield attached" -- which it was not,
  -- because nothing consumed hand-mined ore until Core Survey. Triggering off
  -- it makes the claim true: the first swing at a boulder is what opens the
  -- planet, and the 25 ore it drops is waiting for the smelter two steps later.
  landfall("sae-crust-tapping", { "sae-core-discovery" },
    {
      { type = "unlock-recipe", recipe = "sae-crust-tap" },
      { type = "unlock-recipe", recipe = "sae-crust-turbine" }
    },
    { type = "mine-entity", entity = "sae-core-boulder" }),

  -- The landing kit, and the crusher is not optional in it. Plate smelting was
  -- re-sourced onto crushed kamacite when the Drop Crusher landed (see
  -- recipes.lua), so unlocking smelting without the crusher would unlock a
  -- recipe whose ingredient the player cannot make.
  --
  -- **That re-sourcing also closed a loop nobody had walked.** Crushing is the
  -- only source of crushed kamacite and fines, those are the only routes to a
  -- kamacite plate, and the crusher was priced at 40 kamacite plate -- so the
  -- first crusher could never be built, and with it nothing else on the planet.
  -- The crusher is costed in freight now; see machines.lua.
  --
  -- **Off Crust Tapping now, and triggered by the tap itself.** The survey used
  -- to hang off the discovery beside the tapping, on the grounds that tapping
  -- "needs nothing the survey teaches" -- true, and it left the two as a pair
  -- of unordered purchases. Everything this technology unlocks needs power, and
  -- the only power on this planet is a crust tap, so the tap is both the real
  -- prerequisite and the obvious trigger: build the thing that makes the
  -- electricity, and the survey that spends it lands.
  --
  -- Only Crust Tapping is listed: it already carries the discovery, and a
  -- redundant prerequisite draws a second arrow across the technology screen
  -- for a dependency the first one already states.
  landfall("sae-core-survey", { "sae-crust-tapping" },
    {
      { type = "unlock-recipe", recipe = "sae-vent-pump" },
      { type = "unlock-recipe", recipe = "sae-ballast-drill" },
      { type = "unlock-recipe", recipe = "sae-drop-crusher" },
      { type = "unlock-recipe", recipe = "sae-crushing" },
      { type = "unlock-recipe", recipe = "sae-kamacite-smelting" },
      -- The only machine that will take the crusher's second stream. Without it
      -- fines accumulate from the first craft with nowhere to go.
      { type = "unlock-recipe", recipe = "sae-vacuum-furnace" },
      { type = "unlock-recipe", recipe = "sae-fines-smelting" }
    },
    { type = "craft-item", item = "sae-crust-tap" }),
  -- Power that outlasts the turbine, earned by the first machine that runs all
  -- the time. A crust tap and a turbine are a landing, not a grid; the vent pump
  -- is the first thing the player builds that draws continuously and that
  -- everything downstream waits on. The recipe and the burner land together,
  -- because a burner unlocked without its fuel is a recipe in the menu that
  -- cannot run -- a defect this repository has fixed twice already.
  landfall("sae-radiant-power", { "sae-core-survey" },
    {
      { type = "unlock-recipe", recipe = "sae-radiant-precipitation" },
      { type = "unlock-recipe", recipe = "sae-radiant-generator" },
      { type = "unlock-recipe", recipe = "sae-radiant-crushing" }
    },
    { type = "craft-item", item = "sae-vent-pump" })
})

-- Fulgora <-> Aquilo. Available once both worlds are running, which is what
-- "after Aquilo" means in practice, and researched on packs the player already
-- makes: this is a cross-planet tree, not Core content.
data:extend({
  {
    type = "technology",
    name = "sae-fa-cryogen",
    -- Placeholder, recorded below with the others.
    icon = "__space-age__/graphics/technology/cryogenic-science-pack.png",
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
    -- Placeholder, recorded below with the others.
    icon = "__space-age__/graphics/technology/cryogenic-science-pack.png",
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
    -- Placeholder, recorded below with the others.
    icon = "__space-age__/graphics/technology/cryogenic-science-pack.png",
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

for _, name in ipairs({ "sae-fa-cryogen", "sae-fa-fluorinated-holmium", "sae-fa-superconducting-winding" }) do
  derive.placeholder_art(data.raw.technology[name], "wears the cryogenic science pack's technology icon until its own exists")
end
