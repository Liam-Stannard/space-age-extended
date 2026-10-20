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
-- The mod is cut back to the landing and nothing past it, so the chain is one
-- straight line, and each step is fired by the thing the step before it gave:
--
--   mine a boulder         -> Crust tapping     (power at all)
--   craft a gas pump       -> Core survey       (the drill)
--   craft a ballast drill  -> Gravity crushing  (the crusher, and smelting)
--   craft 50 fines         -> Vacuum sintering  (the furnace that takes them)
--   craft a vacuum furnace -> Vent tapping      (the vent pump)
--   craft a vent pump      -> Radiant power     (the generator, and its fuel)
--
-- Every technology lists only the one before it. The chain already carries
-- everything further back, and a redundant prerequisite draws a second arrow
-- across the technology screen for a dependency the first one already states.
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

data:extend({
  -- Landing-day power, and now literally the first thing the player does.
  --
  -- The boulder was already "the only ore on the planet obtainable before a
  -- drill is standing" (resources.lua), described there as "a genuine early
  -- move rather than decoration with a yield attached" -- which it was not,
  -- because nothing consumed hand-mined ore until the crusher. Triggering off
  -- it makes the claim true: the first swing at a boulder is what opens the
  -- planet, and the 25 ore it drops is waiting for the smelter three steps later.
  landfall("sae-crust-tapping", { "sae-core-discovery" },
    {
      { type = "unlock-recipe", recipe = "sae-gas-pump" },
      { type = "unlock-recipe", recipe = "sae-crust-turbine" }
    },
    { type = "mine-entity", entities = { "sae-core-boulder" } },
    "__space-age-extended__/graphics/technology/sae-crust-tapping.png"),

  -- The survey finds the ore, and the drill is how it comes out. Nothing here
  -- runs without power, and the only power on this planet starts at a gas pump
  -- on a siderane vent, so the pump is both the real prerequisite and the
  -- obvious trigger: build the thing that makes the electricity, and the survey
  -- that spends it lands.
  --
  -- **Off Crust Tapping, not beside it.** The survey used to hang off the
  -- discovery next to the tapping, on the grounds that tapping "needs nothing
  -- the survey teaches" -- true, and it left the two as a pair of unordered
  -- purchases.
  landfall("sae-core-survey", { "sae-crust-tapping" },
    {
      { type = "unlock-recipe", recipe = "sae-ballast-drill" }
    },
    { type = "craft-item", item = "sae-gas-pump" },
    "__space-age-extended__/graphics/technology/sae-core-survey.png"),

  -- The crusher and smelting land together, because plate smelting was
  -- re-sourced onto crushed kamacite when the Drop Crusher landed (see
  -- recipes.lua): smelting without the crusher is a recipe whose ingredient the
  -- player cannot make. Triggered by the drill, because the drill is what puts
  -- ore in front of the crusher.
  --
  -- **That re-sourcing also closed a loop nobody had walked.** Crushing is the
  -- only source of crushed kamacite and fines, those are the only routes to a
  -- kamacite plate, and the crusher was priced at 40 kamacite plate -- so the
  -- first crusher could never be built, and with it nothing else on the planet.
  -- The crusher is costed in freight now; see machines.lua.
  landfall("sae-gravity-crushing", { "sae-core-survey" },
    {
      { type = "unlock-recipe", recipe = "sae-drop-crusher" },
      { type = "unlock-recipe", recipe = "sae-crushing" },
      { type = "unlock-recipe", recipe = "sae-kamacite-smelting" }
    },
    { type = "craft-item", item = "sae-ballast-drill" },
    "__space-age-extended__/graphics/technology/sae-gravity-crushing.png"),

  -- The furnace for the crusher's second stream, once there is a pile of it.
  --
  -- **Fines are the crusher's second result, and a craft-item trigger counts
  -- them.** That was measured before this was written, not assumed: on a
  -- headless server a crusher on the Core fired a 50-fines craft-item trigger
  -- off its own output, with nothing else making fines. The 50 cannot back the
  -- crusher up while it waits: its fines slot holds a full stack of 100, so a
  -- crusher with nothing taking fines out still reaches the trigger.
  landfall("sae-vacuum-sintering", { "sae-gravity-crushing" },
    {
      { type = "unlock-recipe", recipe = "sae-vacuum-furnace" },
      { type = "unlock-recipe", recipe = "sae-fines-smelting" }
    },
    { type = "craft-item", item = "sae-kamacite-fines", count = 50 },
    "__space-age-extended__/graphics/technology/sae-vacuum-sintering.png"),

  -- The vent pump, once the furnace is built. Triggered by crafting a Vacuum
  -- furnace, Vacuum sintering's own recipe, so reachable from this
  -- technology's prerequisites and no further.
  --
  -- **Not by a kamacite plate**, as first agreed: craft-item counts everything
  -- made since the game began, not since the technology became available, and
  -- plate smelting lands with Gravity crushing. Almost every player smelts a
  -- plate before the 50th fine, so the plate trigger was already met and Vent
  -- tapping completed one tick after Vacuum sintering. A furnace can only be
  -- crafted once sintering is researched, so this one cannot fire early.
  landfall("sae-vent-tapping", { "sae-vacuum-sintering" },
    {
      { type = "unlock-recipe", recipe = "sae-vent-pump" }
    },
    { type = "craft-item", item = "sae-vacuum-furnace" }),

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
  --
  -- The effects land together because none of them is worth anything alone: a
  -- plant with no recipe is a shell, the recipe with no generator makes a cell
  -- nothing will burn, and the generator on its own is a burner whose fuel the
  -- Core cannot yet make. Radiant crushing comes with them because the
  -- technology that used to carry it is not on this tree.
  landfall("sae-radiant-power", { "sae-vent-tapping" },
    {
      { type = "unlock-recipe", recipe = "sae-reaction-plant" },
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
