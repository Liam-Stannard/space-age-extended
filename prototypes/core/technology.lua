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
      { icon = "__space-age__/graphics/technology/aquilo.png", icon_size = 256 },
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

local function foothold(name, prereqs, effects)
  return
  {
    type = "technology",
    name = name,
    icon = "__space-age__/graphics/technology/aquilo.png",
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
  foothold("sae-core-survey", { "sae-core-discovery" },
    {
      { type = "unlock-recipe", recipe = "sae-vent-pump" },
      { type = "unlock-recipe", recipe = "sae-kamacite-smelting" }
    }),
  foothold("sae-gravity-settling", { "sae-core-survey" },
    {
      { type = "unlock-recipe", recipe = "sae-gravity-settling" },
      { type = "unlock-recipe", recipe = "sae-quenched-settling" },
      { type = "unlock-recipe", recipe = "sae-dross-resettling" },
      { type = "unlock-recipe", recipe = "sae-ingot-casting" },
      { type = "unlock-recipe", recipe = "sae-orbital-homogenisation" }
    }),
  foothold("sae-whisker-beds", { "sae-gravity-settling" },
    {
      { type = "unlock-recipe", recipe = "sae-whisker-bed" },
      { type = "unlock-recipe", recipe = "sae-seed-plate" },
      { type = "unlock-recipe", recipe = "sae-bed-tender" }
    }),
  foothold("sae-sealed-roboports", { "sae-cold-welding" },
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
    })
})

-- Tier 1 and up: researched on geodynamic science, which is itself made from
-- two of the intermediates. Research and construction therefore draw on one
-- supply, and every pack burned is a Field Coil Segment delayed.

local function geodynamic(name, prereqs, count, effects)
  return
  {
    type = "technology",
    name = name,
    icon = "__space-age__/graphics/technology/aquilo.png",
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
  foothold("sae-integration-conductor", { "sae-core-survey" },
    { { type = "unlock-recipe", recipe = "sae-field-conductor" } }),
  foothold("sae-integration-frame", { "sae-whisker-beds" },
    { { type = "unlock-recipe", recipe = "sae-reinforced-frame" } }),
  foothold("sae-geodynamic-science", { "sae-integration-conductor", "sae-integration-frame" },
    { { type = "unlock-recipe", recipe = "sae-geodynamic-science-pack" } })
})

data:extend({
  geodynamic("sae-integration-billet", { "sae-geodynamic-science" }, 200,
    { { type = "unlock-recipe", recipe = "sae-magnetic-core-billet" } }),
  geodynamic("sae-integration-sleeve", { "sae-geodynamic-science" }, 200,
    { { type = "unlock-recipe", recipe = "sae-insulation-sleeve" } }),
  geodynamic("sae-integration-coolant", { "sae-geodynamic-science" }, 200,
    { { type = "unlock-recipe", recipe = "sae-coolant-charge" } })
})

data:extend({
  -- The last three technologies are the climb. Every pack spent here is
  -- intermediates that did not become segments.
  geodynamic("sae-field-coils",
    { "sae-integration-billet", "sae-integration-sleeve", "sae-integration-coolant", "sae-cold-welding" }, 1000,
    {
      { type = "unlock-recipe", recipe = "sae-coil-assembly" },
      { type = "unlock-recipe", recipe = "sae-coolant-loop" },
      { type = "unlock-recipe", recipe = "sae-field-coil-segment" }
    }),
  geodynamic("sae-corridor-seeding", { "sae-geodynamic-science" }, 400,
    {
      { type = "unlock-recipe", recipe = "sae-seed-missile" },
      { type = "unlock-recipe", recipe = "sae-radiant-crushing" },
      { type = "unlock-recipe", recipe = "sae-seeded-crushing" },
      { type = "unlock-recipe", recipe = "sae-radiant-generator" }
    }),
  geodynamic("sae-ignition-array", { "sae-field-coils" }, 2500,
    { { type = "unlock-recipe", recipe = "sae-ignition-array" } })
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
      { type = "unlock-recipe", recipe = "sae-cryogen" },
      { type = "unlock-recipe", recipe = "sae-cryogen-recovery" }
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
    effects = { { type = "unlock-recipe", recipe = "sae-fluorinated-holmium" } },
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
