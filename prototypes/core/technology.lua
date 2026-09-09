-- Core Discovery.
--
-- Measured, not assumed: a planet nothing unlocks is unreachable. A platform
-- reports no_path to it however well-formed the connection is, and researching
-- every other technology does not help, because none of them names it. This is
-- the sixth tech tree's entry point, and it sits behind promethium science
-- because the Core is past the point where that research already takes you.

data:extend({
  {
    type = "technology",
    name = "sae-core-discovery",
    icons =
    {
      { icon = "__space-age-extended__/graphics/technology/sae-core-discovery.png", icon_size = 256 },
      {
        icon = "__core__/graphics/icons/technology/constants/constant-planet.png",
        icon_size = 128, scale = 0.5, shift = { 50, 50 }, floating = true
      }
    },
    icon_size = 256,
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

-- Tier 0 of the Core's tree: standing the foothold up. These are researched on
-- packs the player already makes, because the geodynamic pack cannot exist
-- until the corridor is delivering.

local function foothold(name, prereqs, effects, icon)
  return
  {
    type = "technology",
    name = name,
    icon = icon or "__space-age__/graphics/technology/aquilo.png",
    icon_size = 256,
    effects = effects,
    prerequisites = prereqs,
    unit =
    {
      count = 200,
      ingredients =
      {
        { "automation-science-pack", 1 },
        { "logistic-science-pack", 1 },
        { "chemical-science-pack", 1 },
        { "production-science-pack", 1 },
        { "utility-science-pack", 1 },
        { "space-science-pack", 1 },
        { "promethium-science-pack", 1 }
      },
      time = 60
    }
  }
end

data:extend({
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
  foothold("sae-core-survey", { "sae-core-discovery" },
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
    }),
  -- Landing-day power, and deliberately the first thing available: a tap and a
  -- turbine are what the player builds before there is a smelter to make
  -- anything better with. Off the discovery rather than the survey, because it
  -- needs nothing the survey teaches.
  foothold("sae-crust-tapping", { "sae-core-discovery" },
    {
      { type = "unlock-recipe", recipe = "sae-crust-tap" },
      { type = "unlock-recipe", recipe = "sae-crust-turbine" }
    }),
  foothold("sae-gravity-settling", { "sae-core-survey" },
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
    "__space-age-extended__/graphics/technology/sae-gravity-settling.png"),
  foothold("sae-whisker-beds", { "sae-gravity-settling" },
    {
      { type = "unlock-recipe", recipe = "sae-whisker-bed" },
      { type = "unlock-recipe", recipe = "sae-seed-plate" },
      { type = "unlock-recipe", recipe = "sae-bed-tender" },
      { type = "unlock-recipe", recipe = "sae-whisker-comber" },
      { type = "unlock-recipe", recipe = "sae-whisker-combing" },
      { type = "unlock-recipe", recipe = "sae-whisker-matting" }
    },
    "__space-age-extended__/graphics/technology/sae-whisker-beds.png"),
  -- Off the field coils, not just cold welding: a sealed roboport is priced in a
  -- coolant loop, and nothing makes one until `sae-field-coils`. `04-the-core.md`
  -- §6 puts the roboport in tier 3 beside the Core's own goods for exactly this
  -- reason -- it is the milestone that lands *with* them, not before them.
  foothold("sae-sealed-roboports", { "sae-cold-welding", "sae-field-coils" },
    {
      { type = "unlock-recipe", recipe = "sae-sealed-roboport" }
    }),
  foothold("sae-arc-masts", { "sae-core-survey" },
    {
      { type = "unlock-recipe", recipe = "sae-arc-mast" }
    }),
  foothold("sae-cold-welding", { "sae-whisker-beds" },
    {
      { type = "unlock-recipe", recipe = "sae-cold-welding" }
    }),
  -- The lift. `04-the-core.md` §4 puts half the endgame in orbit and every trip
  -- costs a rocket, but a rocket part is a processing unit, a low density
  -- structure and a rocket fuel -- and the Core could make none of the three, so
  -- the whole lift was freight. These are the two alternates that fix the heavy
  -- end of it; see recipes.lua for what they are and why the processing unit is
  -- deliberately not among them.
  --
  -- Off the beds because the structure is fibre-reinforced, and off the tapping
  -- because the propellant is crust gas.
  foothold("sae-orbital-lift", { "sae-whisker-beds", "sae-crust-tapping" },
    {
      { type = "unlock-recipe", recipe = "sae-cast-structure" },
      { type = "unlock-recipe", recipe = "sae-crust-propellant" }
    }),
  -- Circuits, on a world with no copper and no plastic. Field emission out of
  -- combed whiskers, switching across a vacuum gap -- see recipes.lua for what
  -- that is and why the Core is the only place it works.
  --
  -- Off cold welding rather than the beds, and both halves of that are load
  -- bearing: cold welding is where the mod establishes that vacuum is a process
  -- and not just an absence, and the processor is canned in a welded plate.
  foothold("sae-vacuum-electronics", { "sae-cold-welding" },
    {
      { type = "unlock-recipe", recipe = "sae-emitter-array" },
      { type = "unlock-recipe", recipe = "sae-valve-logic" },
      { type = "unlock-recipe", recipe = "sae-valve-processor" }
    })
})

-- Tier 1 and up: researched on geodynamic science, which is itself made from
-- two of the intermediates. Research and construction therefore draw on one
-- supply, and every pack burned is a Field Coil Segment delayed.

local function geodynamic(name, prereqs, count, effects, icon)
  return
  {
    type = "technology",
    name = name,
    icon = icon or "__space-age__/graphics/technology/aquilo.png",
    icon_size = 256,
    effects = effects,
    prerequisites = prereqs,
    unit =
    {
      count = count,
      ingredients = { { "sae-geodynamic-science-pack", 1 } },
      time = 60
    }
  }
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
  foothold("sae-integration-conductor", { "sae-gravity-settling", "sae-fa-superconducting-winding" },
    { { type = "unlock-recipe", recipe = "sae-field-conductor" } }),
  foothold("sae-integration-frame", { "sae-whisker-beds" },
    { { type = "unlock-recipe", recipe = "sae-reinforced-frame" } }),
  foothold("sae-geodynamic-science", { "sae-integration-conductor", "sae-integration-frame" },
    { { type = "unlock-recipe", recipe = "sae-geodynamic-science-pack" } })
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
  -- `sae-arc-masts` because the Array's recipe takes four of them, and it was
  -- not a prerequisite of anything: a player could finish the tree and find the
  -- last building priced in a machine they had never unlocked.
  geodynamic("sae-ignition-array",
    { "sae-field-coils", "sae-carbonyl-chemistry", "sae-arc-masts" }, 1200,
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
