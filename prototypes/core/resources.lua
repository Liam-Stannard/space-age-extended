-- The Core's three sited resources.
--
-- Ore is rich, widely spaced and genuinely finite, so the base spreads and
-- rails matter. Both vents are infinite but decline with draw, the way crude
-- oil does, so a vent is permanent and worth building around.
--
-- All three are placed in the starting area. That is not generosity: helium-3
-- cannot be barrelled, so it cannot be shipped in, and melt cannot be drawn
-- without it. A landing site without a gas vent is a landing site where nothing
-- can be started.

local resource_autoplace = require("resource-autoplace")
local tile_sounds = require("__base__.prototypes.tile.tile-sounds")

-- The vents get their own mining category, and that is a gameplay fix rather
-- than tidiness.
--
-- Both vents were `basic-fluid`, the category vanilla's pumpjack works, and a
-- pumpjack has no surface conditions -- so a player could land on the Core,
-- build an ordinary pumpjack on a melt vent and draw melt for nothing. The Vent
-- Pump's entire reason to exist is that melt costs helium-3 (see the note at the
-- top of entities.lua), and the vanilla machine walked straight past it.
--
-- A private category closes it from both ends: nothing vanilla can work a vent,
-- and the Vent Pump can no longer be built on Nauvis crude oil as a pumpjack
-- that happens to need helium.
--
-- The ore gets one too, for the mirror-image reason. `basic-solid` is what
-- vanilla's drills work, and the big mining drill -- no surface conditions, 2.5
-- mining speed, the same 50 per cent drain -- was strictly better than the
-- Ballast Drill on every axis: faster, a third of the power, same penalty. The
-- Core's own drill was a building nobody would ever build.
--
-- `sae-kamacite` is the fix, and it says something the planet should say anyway.
-- Kamacite is not ore in a rock; it is the crust of a metal world, and it takes
-- a machine that presses with its own weight under 50 g. Nothing shipped in from
-- Nauvis works it, and since kamacite is the Core's only solid resource, an
-- imported drill is now scrap the moment it lands.
data:extend({
  { type = "resource-category", name = "sae-vent" },
  { type = "resource-category", name = "sae-kamacite" }
})

-- Each resource needs an autoplace control before a planet may name it.
data:extend({
  { type = "autoplace-control", name = "sae-kamacite-ore", category = "resource", richness = true, order = "z[sae]-a" },
  { type = "autoplace-control", name = "sae-melt-vent",    category = "resource", richness = true, order = "z[sae]-b" },
  { type = "autoplace-control", name = "sae-gas-vent",     category = "resource", richness = true, order = "z[sae]-c" }
})

data:extend({
  {
    type = "resource",
    name = "sae-kamacite-ore",
    icon = "__space-age-extended__/graphics/icons/kamacite-ore.png",
    flags = { "placeable-neutral" },
    category = "sae-kamacite",
    order = "z[sae]-a[kamacite-ore]",
    tree_removal_probability = 0.8,
    tree_removal_max_distance = 32 * 32,
    minable =
    {
      mining_particle = "iron-ore-particle",
      mining_time = 1,
      result = "sae-kamacite-ore"
    },
    walking_sound = tile_sounds.walking.ore,
    driving_sound = tile_sounds.driving.stone,
    -- The colour the drill's mining beam takes: the ore's own grey-violet.
    mining_visualisation_tint = { r = 0.62, g = 0.60, b = 0.66, a = 1 },
    collision_box = { { -0.1, -0.1 }, { 0.1, 0.1 } },
    selection_box = { { -0.5, -0.5 }, { 0.5, 0.5 } },
    autoplace = resource_autoplace.resource_autoplace_settings
    {
      name = "sae-kamacite-ore",
      order = "b",
      base_density = 3,               -- few patches
      regular_rq_factor_multiplier = 3, -- but very rich ones
      has_starting_area_placement = true
    },
    stage_counts = { 15000, 9500, 5500, 2900, 1300, 400, 150, 80 },
    stages =
    {
      sheet = table.deepcopy(data.raw.resource["iron-ore"].stages.sheet)
    },
    map_color = { r = 0.62, g = 0.60, b = 0.66 }
  },
  {
    type = "resource",
    name = "sae-melt-vent",
    icon = "__space-age-extended__/graphics/icons/fluid/molten-kamacite.png",
    flags = { "placeable-neutral" },
    category = "sae-vent",
    subgroup = "mineable-fluids",
    order = "z[sae]-b[melt-vent]",
    infinite = true,
    -- A vent is one pool, not a field of tiles, so it is not snapped to the
    -- resource grid -- as crude oil is not.
    map_grid = false,
    highlight = true,
    minimum = 60000,
    normal = 300000,
    infinite_depletion_amount = 10,
    resource_patch_search_radius = 12,
    tree_removal_probability = 1,
    tree_removal_max_distance = 32 * 32,
    minable =
    {
      mining_time = 1,
      -- Drawing melt costs helium-3, so the rarer vent throttles the richer one.
      required_fluid = "sae-helium-3",
      fluid_amount = 10,
      results =
      {
        { type = "fluid", name = "sae-molten-kamacite", amount = 10 }
      }
    },
    walking_sound = tile_sounds.walking.oil({}),
    driving_sound = tile_sounds.driving.oil,
    collision_box = { { -1.4, -1.4 }, { 1.4, 1.4 } },
    selection_box = { { -1.5, -1.5 }, { 1.5, 1.5 } },
    autoplace = resource_autoplace.resource_autoplace_settings
    {
      name = "sae-melt-vent",
      order = "c",
      base_density = 1.4,
      random_spot_size_minimum = 1,
      random_spot_size_maximum = 1,
      additional_richness = 150000,
      has_starting_area_placement = true
    },
    stage_counts = { 0 },
    stages =
    {
      sheet = table.deepcopy(data.raw.resource["crude-oil"].stages.sheet)
    },
    map_color = { r = 0.90, g = 0.45, b = 0.15 }
  },
  {
    type = "resource",
    name = "sae-gas-vent",
    icon = "__space-age-extended__/graphics/icons/fluid/helium-3.png",
    flags = { "placeable-neutral" },
    category = "sae-vent",
    subgroup = "mineable-fluids",
    order = "z[sae]-c[gas-vent]",
    infinite = true,
    -- A vent is one pool, not a field of tiles, so it is not snapped to the
    -- resource grid -- as crude oil is not.
    map_grid = false,
    highlight = true,
    minimum = 20000,
    normal = 100000,
    infinite_depletion_amount = 10,
    resource_patch_search_radius = 12,
    tree_removal_probability = 1,
    tree_removal_max_distance = 32 * 32,
    minable =
    {
      mining_time = 1,
      results =
      {
        { type = "fluid", name = "sae-helium-3", amount = 10 }
      }
    },
    walking_sound = tile_sounds.walking.oil({}),
    driving_sound = tile_sounds.driving.oil,
    collision_box = { { -1.4, -1.4 }, { 1.4, 1.4 } },
    selection_box = { { -1.5, -1.5 }, { 1.5, 1.5 } },
    autoplace = resource_autoplace.resource_autoplace_settings
    {
      name = "sae-gas-vent",
      order = "d",
      base_density = 0.5,            -- scarcer than melt
      random_spot_size_minimum = 1,
      random_spot_size_maximum = 1,
      additional_richness = 60000,
      has_starting_area_placement = true
    },
    stage_counts = { 0 },
    stages =
    {
      sheet = table.deepcopy(data.raw.resource["crude-oil"].stages.sheet)
    },
    map_color = { r = 0.55, g = 0.80, b = 0.92 }
  }
})
