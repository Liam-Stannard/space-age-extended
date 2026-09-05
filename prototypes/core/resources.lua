-- The Core's three sited resources, and the scatter between them.
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
local sounds = require("__base__/prototypes/entity/sounds")

-- Each resource needs an autoplace control before a planet may name it.
data:extend({
  { type = "autoplace-control", name = "sae-kamacite-ore", category = "resource", richness = true, order = "z[sae]-a" },
  { type = "autoplace-control", name = "sae-melt-vent",    category = "resource", richness = true, order = "z[sae]-b" },
  { type = "autoplace-control", name = "sae-gas-vent",     category = "resource", richness = true, order = "z[sae]-c" },
  -- Not a resource: boulders are terrain the way trees are, so they belong on
  -- the terrain slider rather than among the ore controls.
  { type = "autoplace-control", name = "sae-core-rock",   category = "terrain",  order = "z[sae]-d" }
})

data:extend({
  {
    type = "resource",
    name = "sae-kamacite-ore",
    icon = "__base__/graphics/icons/iron-ore.png",
    flags = { "placeable-neutral" },
    category = "basic-solid",
    order = "z[sae]-a[kamacite-ore]",
    tree_removal_probability = 0.8,
    tree_removal_max_distance = 32 * 32,
    minable =
    {
      mining_particle = "iron-ore-particle",
      mining_time = 1,
      result = "sae-kamacite-ore"
    },
    walking_sound = sounds.ore,
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
    icon = "__space-age__/graphics/icons/fluid/molten-iron.png",
    flags = { "placeable-neutral" },
    category = "basic-fluid",
    order = "z[sae]-b[melt-vent]",
    infinite = true,
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
    icon = "__space-age__/graphics/icons/fluid/fluoroketone-cold.png",
    flags = { "placeable-neutral" },
    category = "basic-fluid",
    order = "z[sae]-c[gas-vent]",
    infinite = true,
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

-- Kamacite boulders: the scatter worth stopping for.
--
-- Vanilla's rocks are the wrong prop here twice over. They yield stone and
-- coal, and the Core has no carbon at all -- coal lying on the ground would
-- contradict the one fact the entire world is built on. And they are Nauvis
-- sandstone to look at, on a crust of iron and nickel.
--
-- This is that silhouette with the Core's own contents: a lump of crust, hand
-- mined for ore. It is the only ore on the planet obtainable before a drill is
-- standing, which makes the scatter a genuine early move rather than decoration
-- with a yield attached -- and it runs out, like everything else here.

local ROCK_SOURCES = { "rock-huge", "rock-big", "sand-rock-big" }

local rock_source
for _, name in pairs(ROCK_SOURCES) do
  if (data.raw["simple-entity"] or {})[name] then
    rock_source = data.raw["simple-entity"][name]
    break
  end
end

-- A base-game prototype, not an optional one: if none of these exist the game
-- is not the game this mod was written against, and saying so beats shipping a
-- planet with invisible rocks on it.
if not rock_source then
  error("prototypes/core/resources.lua: no base-game rock to copy from; looked for " ..
        table.concat(ROCK_SOURCES, ", "))
end

-- Sprite tables nest differently depending on which rock was copied -- sheets,
-- variation arrays and layers all appear -- so the tint is applied by walking
-- the prototype for anything with a filename rather than by reaching into a
-- structure this file would then have to be right about. Shadows and glow
-- layers are left alone: a tinted shadow is either ignored or wrong.
local function tint_sprites(node, tint)
  if type(node) ~= "table" then return end

  if node.filename and not node.draw_as_shadow and not node.draw_as_glow then
    node.tint = tint
    node.apply_runtime_tint = false
  end

  for _, child in pairs(node) do
    tint_sprites(child, tint)
  end
end

local boulder = table.deepcopy(rock_source)
boulder.name = "sae-core-boulder"
boulder.order = "z[sae]-a[core-boulder]"
boulder.minable =
{
  mining_time = 2,
  mining_particle = "iron-ore-particle",
  results = { { type = "item", name = "sae-kamacite-ore", amount = 25 } }
}
boulder.map_color = { r = 0.62, g = 0.60, b = 0.66 }
boulder.autoplace =
{
  control = "sae-core-rock",
  order = "z[sae]-a[core-boulder]",
  -- Roughly two to a chunk, gathered rather than evenly sprinkled: enough to
  -- be worth a detour on the walk out, never enough to be a supply.
  probability_expression = "clamp(0.004 * (0.5 + multioctave_noise{x = x,\z
                                                                  y = y,\z
                                                                  seed0 = map_seed,\z
                                                                  seed1 = 3907,\z
                                                                  octaves = 3,\z
                                                                  persistence = 0.55,\z
                                                                  input_scale = 1/180,\z
                                                                  output_scale = 1}), 0, 0.01)"
}

-- Cool and grey, so it reads as metal rather than as sandstone. This is the
-- whole of the art pass on it; deleting this line returns it to the stand-in.
tint_sprites(boulder, { r = 0.62, g = 0.66, b = 0.74, a = 1 })

data:extend({ boulder })
