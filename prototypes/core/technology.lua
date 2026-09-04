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
    icon = "__space-age__/graphics/technology/planet-discovery-aquilo.png",
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
    icon = "__space-age__/graphics/technology/planet-discovery-aquilo.png",
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
  foothold("sae-cold-welding", { "sae-whisker-beds" },
    {
      { type = "unlock-recipe", recipe = "sae-cold-welding" }
    })
})
