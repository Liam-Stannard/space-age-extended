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
-- **Every technology here is a trigger technology, and the boundary is the
-- science pack.** Tier 0 is the stretch in which the Core cannot yet fund its
-- own research: the geodynamic pack is a field conductor, a reinforced frame
-- and four whiskers, and until all three are in reach there is no pack to pay
-- with. Priced in science, that stretch could only be billed to planets the
-- player already left -- 200 units of seven packs each, promethium among them,
-- twelve times over, for the privilege of bootstrapping a world that gives
-- nothing back until it is running. The player lands, cannot make a watt,
-- cannot use the ore they can already pick up, and flies home to research.
--
-- So tier 0 is earned by doing rather than bought, and tier 1 and up is paid
-- for in geodynamic packs. Two currencies, one boundary, and the boundary is
-- the moment the Core can make its own science. `04-the-core.md` §6 already
-- promised this in as many words -- "some technologies will be trigger techs
-- to aid players progress through the mod" -- and nothing implemented it.
--
-- **The mechanism.** A technology takes `unit` *or* `research_trigger`, never
-- both: the trigger replaces the cost outright while prerequisites still gate
-- when it can fire, so the shape of the tree is unchanged and only the currency
-- is. It is the same move vanilla makes on every new world -- the first local
-- technology is paid for by doing the local thing, not by shipping packs home.
--
-- **The rule every trigger below obeys**: the thing that fires it is reachable
-- from that technology's own prerequisites and no further. A trigger needing
-- something from a technology that is not a prerequisite is a technology that
-- can never fire, and it would not look like a bug -- it would look like the
-- tree simply stopping. Checked for all nine.
--
-- Only two trigger shapes are used, `mine-entity` and `craft-item`, and that is
-- deliberate rather than incidental: they are the two whose field layout is
-- unambiguous, and a trigger that fails to load takes the whole mod with it.
--
-- The chain they make is the mod's opening, and it is all one motion:
--
--   mine a boulder            -> Crust Tapping        (power at all)
--   craft a Crust Tap         -> Core Survey          (drill, crusher, smelter)
--   craft a kamacite plate    -> Gravity Settling     (the melt line)
--   craft bed-grade dross     -> Whisker Beds         (the farm)
--   craft a cast ingot        -> Orbital Lift         (the cargo that needs orbit)
--   harvest a whisker plant   -> Cold Welding         (vacuum as a process)
--   craft a welded plate      -> Vacuum Electronics   (circuits without copper)
--   craft a combed tow        -> Integration: Frame
--   craft a homogenised ingot -> Integration: Conductor
--   craft a field conductor   -> Geodynamic Science   (the Core funds itself)
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
  -- The melt line, earned by the first plate off the ore line.
  --
  -- Those are the survey's two halves: ore -> crusher -> smelter on one side,
  -- vent pump -> molten kamacite on the other. The plate is the moment the
  -- first half closes, and settling is the only thing to do with the second --
  -- so a plate in the player's hand is exactly when this becomes the next move.
  landfall("sae-gravity-settling", { "sae-core-survey" },
    {
      { type = "unlock-recipe", recipe = "sae-gravity-settling" },
      { type = "unlock-recipe", recipe = "sae-quenched-settling" },
      { type = "unlock-recipe", recipe = "sae-dross-resettling" },
      { type = "unlock-recipe", recipe = "sae-ingot-casting" },
      { type = "unlock-recipe", recipe = "sae-orbital-homogenisation" },
      -- Settling is what makes dross, and the beds are laid on the classified
      -- grade rather than the raw -- so the classifier has to arrive with the
      -- settling that feeds it, and before the beds that need it.
      { type = "unlock-recipe", recipe = "sae-dross-classifier" },
      { type = "unlock-recipe", recipe = "sae-classification" },
      -- The relief valve on helium. Needs melt, so it arrives with the melt.
      { type = "unlock-recipe", recipe = "sae-helium-concentrator" },
      { type = "unlock-recipe", recipe = "sae-degassing" }
    },
    { type = "craft-item", item = "sae-kamacite-plate" },
    "__space-age-extended__/graphics/technology/sae-gravity-settling.png"),
  -- The farm, earned by the ground it is laid on.
  --
  -- Beds are laid on bed-grade dross and nothing else, and classification is
  -- the only source of it -- so the first classified batch is the player
  -- holding a material with no consumer, which is the right moment to be told
  -- what it is for.
  landfall("sae-whisker-beds", { "sae-gravity-settling" },
    {
      { type = "unlock-recipe", recipe = "sae-whisker-bed" },
      { type = "unlock-recipe", recipe = "sae-seed-plate" },
      { type = "unlock-recipe", recipe = "sae-bed-tender" },
      { type = "unlock-recipe", recipe = "sae-whisker-comber" },
      { type = "unlock-recipe", recipe = "sae-whisker-combing" },
      { type = "unlock-recipe", recipe = "sae-whisker-matting" }
    },
    { type = "craft-item", item = "sae-bed-dross" },
    "__space-age-extended__/graphics/technology/sae-whisker-beds.png"),
  -- Vacuum as a process, earned by the first harvest.
  --
  -- Welding is 4 plate and 2 whiskers, and the whisker is the half the player
  -- does not have until a bed has grown one. `mine-entity` rather than
  -- `craft-item` because a whisker is harvested, not crafted -- the Bed Tender
  -- mines the plant, and so does a player who walks up and takes one by hand.
  landfall("sae-cold-welding", { "sae-whisker-beds" },
    {
      { type = "unlock-recipe", recipe = "sae-cold-welding" }
    },
    { type = "mine-entity", entity = "sae-whisker-plant" }),
  -- The lift. `04-the-core.md` §4 puts half the endgame in orbit and every trip
  -- costs a rocket, but a rocket part is a processing unit, a low density
  -- structure and a rocket fuel -- and the Core could make none of the three, so
  -- the whole lift was freight. These are the two alternates that fix the heavy
  -- end of it; see recipes.lua for what they are and why the processing unit is
  -- deliberately not among them.
  --
  -- Off the beds because the structure is fibre-reinforced, and off the tapping
  -- because the propellant is crust gas.
  --
  -- Triggered by a cast ingot, because an ingot is the lift's entire cargo:
  -- homogenisation is the one step that cannot happen on the ground, so the
  -- first ingot out of the caster is the first thing on this planet that has
  -- somewhere else to be.
  landfall("sae-orbital-lift", { "sae-whisker-beds", "sae-crust-tapping" },
    {
      { type = "unlock-recipe", recipe = "sae-cast-structure" },
      { type = "unlock-recipe", recipe = "sae-crust-propellant" }
      -- Provisional home: the brine needs a Crust Tap (Crust Tapping) and
      -- helium-3 (Core Survey), and this is the first technology whose
      -- prerequisites carry both.
      , { type = "unlock-recipe", recipe = "sae-radiant-precipitation" }
    },
    { type = "craft-item", item = "sae-cast-ingot" }),
  -- Circuits, on a world with no copper and no plastic. Field emission out of
  -- combed whiskers, switching across a vacuum gap -- see recipes.lua for what
  -- that is and why the Core is the only place it works.
  --
  -- Off cold welding rather than the beds, and both halves of that are load
  -- bearing: cold welding is where the mod establishes that vacuum is a process
  -- and not just an absence, and the processor is canned in a welded plate.
  --
  -- Triggered by a welded plate, which is both halves of the argument in one
  -- item: the player has just proved that clean metal bonds in vacuum, and the
  -- processor is canned in exactly that plate.
  landfall("sae-vacuum-electronics", { "sae-cold-welding" },
    {
      { type = "unlock-recipe", recipe = "sae-emitter-array" },
      { type = "unlock-recipe", recipe = "sae-valve-logic" },
      { type = "unlock-recipe", recipe = "sae-valve-processor" }
    },
    { type = "craft-item", item = "sae-welded-plate" })
})

-- Tier 1 and up: researched on geodynamic science, which is itself made from
-- two of the intermediates. Research and construction therefore draw on one
-- supply, and every pack burned is a Field Coil Segment delayed.

local function geodynamic(name, prereqs, count, effects, icon)
  return tech_icon(
  {
    type = "technology",
    name = name,
    effects = effects,
    prerequisites = prereqs,
    unit =
    {
      count = count,
      ingredients = { { "sae-geodynamic-science-pack", 1 } },
      time = 60
    }
  }, icon)
end

data:extend({
  -- The five integrations are researchable in any order: a player whose Gleba
  -- line is further along than their Aquilo line is never blocked. Each is
  -- researched on the packs they already make, because the geodynamic pack
  -- cannot exist until two of these are done.
  -- **Both prerequisites are the recipe's own ingredients, and neither used to
  -- be here.** A field conductor is two superconducting windings and a
  -- homogenised ingot. The winding is made only by the Fulgora <-> Aquilo tree,
  -- and the ingot only by orbital homogenisation, which is `sae-gravity-settling`
  -- -- so this technology used to hang off the Survey and unlock a recipe with
  -- neither of its ingredients reachable.
  --
  -- That mattered more than one dead recipe: the conductor feeds the geodynamic
  -- pack and the pack gates everything after it, so the whole tree above tier 0
  -- rested on a technology it never named. Nothing is lost by saying so --
  -- cryogenic science is already a prerequisite of promethium science, so any
  -- player standing on the Core can reach the winding chain. The other four
  -- integrations will want the same treatment the day their stubs become real.
  --
  -- **All three are triggers, and that is what closes the bootstrap.** The pack
  -- is a field conductor, a reinforced frame and four whiskers, so these are the
  -- last technologies a player needs before the Core funds its own research --
  -- and until they are done there is no geodynamic pack to pay for them with.
  -- Priced in vanilla packs they were the tail of the promethium bill; priced
  -- in nothing, the boundary between the two currencies is exactly the pack.
  --
  -- Each trigger is the ingredient the technology is about. The conductor is
  -- earned by the homogenised ingot -- the orbital step, and the only half of
  -- the conductor the Core makes itself. The frame is earned by the first
  -- combed tow. And the pack is earned by the conductor, which is the hardest
  -- of its three ingredients and the last one to come within reach.
  landfall("sae-integration-conductor", { "sae-gravity-settling", "sae-fa-superconducting-winding" },
    { { type = "unlock-recipe", recipe = "sae-field-conductor" } },
    { type = "craft-item", item = "sae-homogenised-ingot" }),
  landfall("sae-integration-frame", { "sae-whisker-beds" },
    { { type = "unlock-recipe", recipe = "sae-reinforced-frame" } },
    { type = "craft-item", item = "sae-whisker-tow" }),
  landfall("sae-geodynamic-science", { "sae-integration-conductor", "sae-integration-frame" },
    { { type = "unlock-recipe", recipe = "sae-geodynamic-science-pack" } },
    { type = "craft-item", item = "sae-field-conductor" })
})

data:extend({
  geodynamic("sae-integration-billet", { "sae-geodynamic-science" }, 150,
    { { type = "unlock-recipe", recipe = "sae-magnetic-core-billet" } }),
  geodynamic("sae-integration-sleeve", { "sae-geodynamic-science" }, 150,
    { { type = "unlock-recipe", recipe = "sae-insulation-sleeve" } }),
  geodynamic("sae-integration-coolant", { "sae-geodynamic-science" }, 150,
    { { type = "unlock-recipe", recipe = "sae-coolant-charge" } })
})

data:extend({
  -- The last three technologies are the climb. Every pack spent here is
  -- intermediates that did not become segments.
  geodynamic("sae-field-coils",
    { "sae-integration-billet", "sae-integration-sleeve", "sae-integration-coolant", "sae-cold-welding" }, 600,
    {
      { type = "unlock-recipe", recipe = "sae-coil-assembly" },
      { type = "unlock-recipe", recipe = "sae-coolant-loop" },
      -- The Ring Mast and its charge are infrastructure and land here; the
      -- segment they feed is crafted *inside* the Ignition Array and unlocks
      -- with it, the way vanilla unlocks `rocket-part` with the silo rather than
      -- a technology earlier. `04-the-core.md` §6 already groups the two as
      -- tier 4; this is the tree agreeing with it.
      { type = "unlock-recipe", recipe = "sae-ring-mast" },
      { type = "unlock-recipe", recipe = "sae-ignition-charge" }
    },
    "__space-age-extended__/graphics/technology/sae-field-coils.png"),
  -- Off the field coils, not just cold welding: a sealed roboport is priced in a
  -- coolant loop, and nothing makes one until `sae-field-coils`. `04-the-core.md`
  -- §6 puts the roboport in tier 3 beside the Core's own goods for exactly this
  -- reason -- it is the milestone that lands *with* them, not before them.
  --
  -- **And it is paid for in geodynamic packs now, which is what tier 3 means.**
  -- It was the one technology on the far side of the science pack still priced
  -- as a foothold, so with tier 0 converted to triggers it would have been the
  -- only research in the whole Core tree costing promethium -- a currency the
  -- mod otherwise asks for exactly once, at Core Discovery. 300 to match
  -- Corridor Seeding and Magnetic Separation, the siblings §6 groups it with.
  geodynamic("sae-sealed-roboports", { "sae-cold-welding", "sae-field-coils" }, 300,
    {
      { type = "unlock-recipe", recipe = "sae-sealed-roboport" }
    }),
  geodynamic("sae-corridor-seeding", { "sae-geodynamic-science" }, 300,
    {
      { type = "unlock-recipe", recipe = "sae-seed-missile" },
      { type = "unlock-recipe", recipe = "sae-radiant-crushing" },
      { type = "unlock-recipe", recipe = "sae-seeded-crushing" },
      { type = "unlock-recipe", recipe = "sae-radiant-generator" }
    }),
  -- After the field coils, and not by accident: building a Coil Separator costs
  -- a coil assembly, so the recipe cannot be reached before the thing it is
  -- priced in exists. Spending endgame material to make more endgame material
  -- is the point of the building.
  geodynamic("sae-magnetic-separation", { "sae-field-coils" }, 300,
    {
      { type = "unlock-recipe", recipe = "sae-coil-separator" },
      { type = "unlock-recipe", recipe = "sae-magnetic-separation" },
      -- Schreibersite's only consumer. Without it the separator produces
      -- something nothing wants, which is not a building worth researching.
      { type = "unlock-recipe", recipe = "sae-phosphide-flux" }
    }),
  -- Metal that travels through pipes, and the only thing that fills the Vacuum
  -- Furnace's `sae-sintering` category. After magnetic separation because the
  -- preform needs flux, and flux needs schreibersite.
  geodynamic("sae-carbonyl-chemistry", { "sae-magnetic-separation" }, 400,
    {
      { type = "unlock-recipe", recipe = "sae-carbon-monoxide" },
      { type = "unlock-recipe", recipe = "sae-metal-carbonyl" },
      { type = "unlock-recipe", recipe = "sae-carbonyl-powder" },
      { type = "unlock-recipe", recipe = "sae-sintered-preform" }
    }),
  -- Carbonyl chemistry is a prerequisite because the Array's recipe now takes
  -- sintered preforms. Without it the last technology would unlock a building
  -- the player cannot yet make a part of.
  -- No prerequisite for the superconducting stores the Array is priced in:
  -- `sae-fa-superconducting-winding` already unlocks them, and it is a
  -- transitive ancestor of this through the conductor integration. Naming it
  -- again would draw a second arrow for a dependency the tree already states.
  geodynamic("sae-ignition-array",
    { "sae-field-coils", "sae-carbonyl-chemistry" }, 1200,
    {
      { type = "unlock-recipe", recipe = "sae-ignition-array" },
      { type = "unlock-recipe", recipe = "sae-field-coil-segment" }
    })
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
