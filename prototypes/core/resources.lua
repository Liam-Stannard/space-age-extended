-- The Core's sited resources, and the scatter between them. The siderane vent
-- is the fourth, and lives with the Gas Pump in crust-tap.lua.
--
-- Ore is rich, widely spaced and genuinely finite, so the base spreads and
-- rails matter. Every vent is infinite but declines with draw, the way crude
-- oil does, so a vent is permanent and worth building around.
--
-- All of them are placed in the starting area. That is not generosity: helium-3
-- cannot be barrelled, so it cannot be shipped in, and melt cannot be drawn
-- without it. A landing site without a gas vent is a landing site where nothing
-- can be started.
--
-- The starting patches are not vanilla's (`has_starting_area_placement`), which
-- dropped them into the radiant pool on some seeds: each is a spot of the
-- Core's own, made in map-gen.lua, laid over the patches below with max(). See
-- "The starting area" there. Everything outside it is vanilla's placement, as
-- before.

local resource_autoplace = require("resource-autoplace")
local tile_sounds = require("__base__.prototypes.tile.tile-sounds")
local derive = require("prototypes.derive")

-- A resource's autoplace: vanilla's patches everywhere, and inside the starting
-- area the Core's own starting spot `sae_core_start_<key>` (map-gen.lua), with
-- its own amount. `has_starting_area_placement = false` keeps vanilla's
-- patches out of the starting area -- they fade in from 150 tiles, exactly as
-- they did with `true` -- and no longer asks vanilla for a starting patch.
local function with_starting_spot(key, settings)
  settings.has_starting_area_placement = false
  local regular = resource_autoplace.resource_autoplace_settings(settings)
  local start = "sae_core_start_" .. key
  return
  {
    order = regular.order,
    probability_expression = "max(" .. regular.probability_expression .. ", " .. start .. " > 0)",
    richness_expression = "if(" .. start .. " > 0, " .. start .. "_richness, " .. regular.richness_expression .. ")"
  }
end

-- The vents get their own mining categories, and that is a gameplay fix rather
-- than tidiness.
--
-- The vents were `basic-fluid`, the category vanilla's pumpjack works, and a
-- pumpjack has no surface conditions -- so a player could land on the Core,
-- build an ordinary pumpjack on a kamacite vent and draw melt for nothing. The
-- Vent Pump's entire reason to exist is that melt costs helium-3 (see the note
-- at the top of entities.lua), and the vanilla machine walked straight past it.
--
-- A private category closes it from both ends: nothing vanilla can work a vent,
-- and the Vent Pump can no longer be built on Nauvis crude oil as a pumpjack
-- that happens to need helium.
--
-- **Two of them, one per machine.** `sae-vent` is the kamacite vent's alone,
-- and only the Vent Pump works it. `sae-gas` is every gas vent's -- helium-3 here,
-- siderane in crust-tap.lua -- and only the Gas Pump works it. Neither machine
-- can stand on the other's vent, and a new gas is a new resource in `sae-gas`
-- rather than a new machine.
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
  { type = "resource-category", name = "sae-gas" },
  { type = "resource-category", name = "sae-kamacite" }
})

-- Each resource needs an autoplace control before a planet may name it.
data:extend({
  { type = "autoplace-control", name = "sae-kamacite-ore",  category = "resource", richness = true, order = "z[sae]-a" },
  { type = "autoplace-control", name = "sae-kamacite-vent", category = "resource", richness = true, order = "z[sae]-b" },
  { type = "autoplace-control", name = "sae-gas-vent",      category = "resource", richness = true, order = "z[sae]-c" },
  -- Not a resource: boulders are terrain the way trees are, so they belong on
  -- the terrain slider rather than among the ore controls.
  { type = "autoplace-control", name = "sae-core-rock",   category = "terrain",  order = "z[sae]-d" }
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
    autoplace = with_starting_spot("kamacite",
    {
      name = "sae-kamacite-ore",
      order = "b",
      base_density = 3,               -- few patches
      regular_rq_factor_multiplier = 3 -- but very rich ones
    }),
    stage_counts = { 15000, 9500, 5500, 2900, 1300, 400, 150, 80 },
    stages =
    {
      sheet = table.deepcopy(data.raw.resource["iron-ore"].stages.sheet)
    },
    map_color = { r = 0.62, g = 0.60, b = 0.66 }
  },
  {
    type = "resource",
    name = "sae-kamacite-vent",
    icon = "__space-age-extended__/graphics/icons/fluid/molten-kamacite.png",
    flags = { "placeable-neutral" },
    category = "sae-vent",
    subgroup = "mineable-fluids",
    order = "z[sae]-b[kamacite-vent]",
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
    autoplace = with_starting_spot("kamacite_vent",
    {
      name = "sae-kamacite-vent",
      order = "c",
      base_density = 1.4,
      random_spot_size_minimum = 1,
      random_spot_size_maximum = 1,
      additional_richness = 150000
    }),
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
    -- Drawn by the Gas Pump, with every other gas; see crust-tap.lua.
    category = "sae-gas",
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
    -- Crude oil's boxes (Liam, 2026-10-21: "Crude oil's real boxes"), small
    -- under the 3x3 Gas Pump, which stands centred on it as the pumpjack stands
    -- on oil; see crust-tap.lua. At this size the starting patch's radius is
    -- map-gen.lua's to keep it about eleven vents.
    collision_box = { { -1.4, -1.4 }, { 1.4, 1.4 } },
    selection_box = { { -0.5, -0.5 }, { 0.5, 0.5 } },
    autoplace = with_starting_spot("gas",
    {
      name = "sae-gas-vent",
      order = "d",
      base_density = 0.5,            -- scarcer than the kamacite vent
      random_spot_size_minimum = 1,
      random_spot_size_maximum = 1,
      additional_richness = 60000
    }),
    stage_counts = { 0 },
    stages =
    {
      sheet = table.deepcopy(data.raw.resource["crude-oil"].stages.sheet)
    },
    -- Violet, #B6A6C8, the Vent Pump's paler bubble and band violet (Liam,
    -- 2026-10-21: "Violet, like the Vent Pump", then "#B6A6C8", and "Also the
    -- vent's map colour"): the colour the Gas Pump's sight glass shows while
    -- it draws from this vent, and the vent's colour on the map, so it reads
    -- apart from siderane's chartreuse in both. Helium-3's own fluid colours
    -- (fluids.lua) do not change.
    map_color = { r = 0.714, g = 0.651, b = 0.784 },
    mining_visualisation_tint = { r = 0.714, g = 0.651, b = 0.784 }
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

-- 2.0 renamed vanilla's rocks: these are the current names, biggest first.
local ROCK_SOURCES = { "huge-rock", "big-rock", "big-sand-rock" }

local rock_source
for _, name in pairs(ROCK_SOURCES) do
  if (data.raw["simple-entity"] or {})[name] then
    rock_source = name
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

-- Through derive, like every other copy of a vanilla prototype here: the rock's
-- shape and sprites are what is wanted, not its name, its page or its yield.
local boulder = derive.from("simple-entity", rock_source, "sae-core-boulder")
boulder.subgroup = "sae-core-tiles"
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
  -- Roughly one or two to a chunk, gathered rather than evenly sprinkled:
  -- enough to be worth a detour on the walk out, never enough to be a supply.
  -- The multiplier is not linear in the count, so it was measured on the rig
  -- rather than reasoned about: 0.002 gave 0.5 a chunk, 0.003 gave 1.0,
  -- 0.0035 gave 255/144 = 1.8, 0.004 gave 3.9.
  probability_expression = "clamp(0.0035 * (0.5 + multioctave_noise{x = x,\z
                                                                  y = y,\z
                                                                  seed0 = map_seed,\z
                                                                  seed1 = 3907,\z
                                                                  octaves = 3,\z
                                                                  persistence = 0.55,\z
                                                                  input_scale = 1/180,\z
                                                                  output_scale = 1}), 0, 0.01)"
}

-- The Core's own material, not a tint. A tint multiplies, and the rock's
-- texture is warm sandstone, so every blue-grey tried left it brown or black;
-- tools/build-core-rocks.py rebuilds the sheets with the sandstone's shading
-- remapped onto slate, and the prototype points at those.
do
  local FROM = "__base__/graphics/decorative/huge-rock/"
  local TO = "__space-age-extended__/graphics/entity/core-boulder/"
  local function repoint(t)
    for k, v in pairs(t) do
      if type(v) == "table" then repoint(v)
      elseif type(v) == "string" and v:sub(1, #FROM) == FROM then t[k] = TO .. v:sub(#FROM + 1) end
    end
  end
  repoint(boulder.pictures)
end

data:extend({ boulder })
