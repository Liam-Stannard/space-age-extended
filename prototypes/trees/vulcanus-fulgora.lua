-- Vulcanus <-> Fulgora: a magnet from glass and storms.
--
-- design/trees/vulcanus-fulgora.md is the source of every number here.
--
-- THE CROSSING. Both legs run Fulgora -> Vulcanus, and each is forced by a
-- fluid with no barrel:
--
--   superconducting coil   because winding it takes electrolyte
--   holmium oxide          because making it takes ozone, which only
--                          lightning makes
--
-- Nothing has to come back. Vulcanus's answer is the capstone itself: only the
-- induction foundry casts and charges the field core, and lava makes Vulcanus
-- the cheap place to stand one.
--
-- THE MECHANIC: surge supply. Ozone arrives only when lightning strikes an
-- ozone collector, and the steps that drink it (holmium oxide, oxide
-- superconductor) run all the time, so the player buffers it through the calm.
--
-- The three buildings are here: the ozone collector, the induction foundry and
-- the magnetic collector. The script that turns a strike on an ozone collector
-- into ozone is scripts/trees/vulcanus-fulgora.lua.
--
-- AND AFTER THE TREE: the magnetic collector catches the magnetic chunk, which
-- flies only on a new direct Vulcanus <-> Fulgora route; crushed, it gives
-- magnetite, and magnetite makes the magnetite round (tech 11, after the
-- railgun).

local derive = require("prototypes.derive")
local item_sounds = require("__base__.prototypes.item_sounds")
local space_age_item_sounds = require("__space-age__.prototypes.item_sounds")
local hit_effects = require("__base__.prototypes.entity.hit-effects")
local entity_sounds = require("__base__.prototypes.entity.sounds")

local SA = "__space-age__/graphics/"
local BASE = "__base__/graphics/"

-- Hot sulfuric acid: what lava heats it to, and what obsidian flux needs.
local HOT = 500

--------------------------------------------------------------------------------
-- Stand-in icons: a vanilla icon in this tree's own tint. Every prototype that
-- wears one is recorded as a placeholder, so the data-stage report counts it.
--------------------------------------------------------------------------------

local function tinted(file, tint, size)
  return { { icon = file, icon_size = size or 64, tint = tint } }
end

-- A recipe icon: what it makes, with what makes it different in the corner, as
-- vanilla marks its alternates.
local function badged(main, badge)
  local icons = table.deepcopy(main)
  for _, layer in ipairs(badge) do
    local b = table.deepcopy(layer)
    b.scale = 0.25
    b.shift = { -8, -8 }
    icons[#icons + 1] = b
  end
  return icons
end

-- derive.placeholder_art keys its record by name alone, and in this tree one
-- name can be several prototypes: sae-obsidian is the ore and the item it
-- yields, and each building is an entity, an item and a recipe. So everything
-- but a building's entity is recorded under its type as well ("item/...",
-- "resource/..."), and the records stay apart. A building's entity keeps the
-- bare name (see the buildings below), the key derive.own_graphics strikes off
-- when its art arrives.
local function stand_in(p, note)
  derive.placeholder_art({ name = p.type .. "/" .. p.name },
    note or "wears a tinted vanilla icon until its own exists")
  return p
end

local ICON =
{
  obsidian = tinted(BASE .. "icons/stone.png", { 0.32, 0.26, 0.40 }),
  glass = tinted(BASE .. "icons/stone-brick.png", { 0.45, 0.35, 0.60 }),
  flux = tinted(SA .. "icons/calcite.png", { 0.75, 0.55, 0.85 }),
  slag = tinted(BASE .. "icons/stone.png", { 0.55, 0.50, 0.45 }),
  oxide = tinted(SA .. "icons/holmium-ore.png", { 1.0, 0.92, 0.70 }),
  coil = tinted(SA .. "icons/superconductor.png", { 0.60, 0.80, 1.0 }),
  core = tinted(SA .. "icons/supercapacitor.png", { 0.55, 0.55, 0.75 }),
  ozone = tinted(SA .. "icons/fluid/fluorine.png", { 0.60, 0.85, 1.0 }),
  refined = tinted(SA .. "icons/fluid/molten-iron.png", { 0.80, 0.90, 1.0 }),
  holmium_iron = tinted(SA .. "icons/fluid/molten-iron.png", { 0.90, 0.60, 0.90 }),
  hot_acid = tinted(BASE .. "icons/fluid/sulfuric-acid.png", { 1.0, 0.55, 0.30 })
}

local function vanilla(file) return { { icon = file, icon_size = 64 } } end

--------------------------------------------------------------------------------
-- The tree's one change to a vanilla prototype.
--
-- FluidPrototype's max_temperature defaults to default_temperature, which for
-- sulfuric acid is 25, so today it cannot be heated at all. Raising the ceiling
-- changes nothing for cold acid: geysers, chemical plants and barrels still
-- make it at 25. Only the heating recipe below makes it hotter.
--------------------------------------------------------------------------------

data.raw.fluid["sulfuric-acid"].max_temperature = HOT

--------------------------------------------------------------------------------
-- The induction foundry's own category. Only that building crafts it, and it
-- runs no vanilla recipe: the three field recipes and the five induction casts.
--------------------------------------------------------------------------------

data:extend({ { type = "recipe-category", name = "sae-induction" } })

--------------------------------------------------------------------------------
-- Obsidian, on Vulcanus.
--
-- Wired the way vanilla wires tungsten: the resource's own autoplace is
-- probability 0, and Vulcanus's map_gen_settings name the planet's expressions
-- for it. In the basalt lowlands near the lava, as tungsten, with no starting
-- patch. Against tungsten: 10 spots a region (15), radius 25 x size (as tungsten),
-- richness 15,000 (10,000), the non-metal spot function's region size.
--
-- Placed only in chunks generated after the mod loads; an old save's Vulcanus
-- needs its surface map_gen_settings given the same three entries.
--------------------------------------------------------------------------------

local OBSIDIAN_TINT = { 0.32, 0.26, 0.40 }

local obsidian_sheet = table.deepcopy(data.raw.resource["stone"].stages.sheet)
obsidian_sheet.tint = OBSIDIAN_TINT

data:extend({
  { type = "autoplace-control", name = "sae-obsidian", category = "resource", richness = true, order = "z[sae]-vf-a" },
  {
    type = "noise-expression",
    name = "sae_obsidian_size",
    expression = "slider_rescale(var('control:sae-obsidian:size'), 2)"
  },
  {
    -- -1 to 1, as vanilla's: positive where the patch is. The spot seed and
    -- offset are the ones T02's five-seed test measured.
    type = "noise-expression",
    name = "sae_obsidian_region",
    expression = "min(1 - vulcanus_starting_circle,\z
                      vulcanus_place_non_metal_spots(4471, 10, 0,\z
                                                     sae_obsidian_size * min(1.2, vulcanus_ore_dist) * 25,\z
                                                     var('control:sae-obsidian:frequency'),\z
                                                     vulcanus_basalts_resource_favorability))"
  },
  {
    type = "noise-expression",
    name = "sae_obsidian_probability",
    expression = "(var('control:sae-obsidian:size') > 0)\z
                  * (1000 * ((1 + sae_obsidian_region) * random_penalty_between(0.9, 1, 1) - 1))"
  },
  {
    type = "noise-expression",
    name = "sae_obsidian_richness",
    expression = "sae_obsidian_region * random_penalty_between(0.9, 1, 1)\z
                  * 15000 * vulcanus_starting_area_multiplier\z
                  * var('control:sae-obsidian:richness') / sae_obsidian_size"
  },
  stand_in({
    type = "resource",
    name = "sae-obsidian",
    icons = ICON.obsidian,
    flags = { "placeable-neutral" },
    -- Any drill, no fluid.
    category = "basic-solid",
    order = "z[sae]-vf-a[obsidian]",
    tree_removal_probability = 0.8,
    tree_removal_max_distance = 32 * 32,
    minable =
    {
      mining_particle = "stone-particle",
      mining_time = 1,
      result = "sae-obsidian"
    },
    walking_sound = data.raw.resource["stone"].walking_sound,
    driving_sound = data.raw.resource["stone"].driving_sound,
    mining_visualisation_tint = { r = 0.45, g = 0.38, b = 0.55, a = 1 },
    collision_box = { { -0.1, -0.1 }, { 0.1, 0.1 } },
    selection_box = { { -0.5, -0.5 }, { 0.5, 0.5 } },
    -- After tungsten ("b"), so where the two meet tungsten keeps the tile.
    autoplace = { order = "c", probability_expression = 0 },
    stage_counts = { 15000, 9500, 5500, 2900, 1300, 400, 150, 80 },
    -- Vanilla stone's sheet in the ore's own dark glass tint, until it has art.
    stages = { sheet = obsidian_sheet },
    map_color = { r = 0.60, g = 0.20, b = 0.45 }
  })
})

local vulcanus = data.raw.planet["vulcanus"].map_gen_settings
vulcanus.autoplace_controls["sae-obsidian"] = {}
vulcanus.autoplace_settings.entity.settings["sae-obsidian"] = {}
vulcanus.property_expression_names["entity:sae-obsidian:probability"] = "sae_obsidian_probability"
vulcanus.property_expression_names["entity:sae-obsidian:richness"] = "sae_obsidian_richness"

--------------------------------------------------------------------------------
-- Fluids. None has a barrel: ozone so it cannot leave Fulgora, the two irons
-- because molten iron has none either.
--------------------------------------------------------------------------------

data:extend({
  stand_in({
    type = "fluid",
    name = "sae-ozone",
    icons = ICON.ozone,
    subgroup = "fluid",
    order = "z[sae]-vf[a-ozone]",
    -- As fluorine, the one vanilla gas that has no barrel.
    default_temperature = 25,
    gas_temperature = 15,
    base_color = { r = 0.45, g = 0.65, b = 0.95 },
    flow_color = { r = 0.75, g = 0.90, b = 1.0 },
    auto_barrel = false
  }),
  stand_in({
    type = "fluid",
    name = "sae-refined-molten-iron",
    icons = ICON.refined,
    subgroup = "fluid",
    order = "z[sae]-vf[b-refined-molten-iron]",
    -- As molten iron.
    default_temperature = 1500,
    base_color = { r = 0.10, g = 0.20, b = 0.60 },
    flow_color = { r = 0.45, g = 0.80, b = 1.0 },
    draw_as_glow = true,
    auto_barrel = false
  }),
  stand_in({
    type = "fluid",
    name = "sae-molten-holmium-iron",
    icons = ICON.holmium_iron,
    subgroup = "fluid",
    order = "z[sae]-vf[c-molten-holmium-iron]",
    default_temperature = 1500,
    base_color = { r = 0.40, g = 0.10, b = 0.50 },
    flow_color = { r = 0.90, g = 0.60, b = 0.95 },
    draw_as_glow = true,
    auto_barrel = false
  })
})

--------------------------------------------------------------------------------
-- Items. Magnetar alloy is not here: it keeps the stub's item
-- (prototypes/core/endgame.lua), so saves keep what they hold, and only gains a
-- real recipe below.
--------------------------------------------------------------------------------

local function item(name, icons, subgroup, order, stack_size, sounds, weight)
  return stand_in({
    type = "item",
    name = name,
    icons = icons,
    subgroup = subgroup,
    order = order,
    inventory_move_sound = sounds.move,
    pick_sound = sounds.pick,
    drop_sound = sounds.move,
    stack_size = stack_size,
    weight = weight
  })
end

local RESOURCE = { move = item_sounds.resource_inventory_move, pick = item_sounds.resource_inventory_pickup }
local BRICK = { move = item_sounds.brick_inventory_move, pick = item_sounds.brick_inventory_pickup }
local WIRE = { move = item_sounds.wire_inventory_move, pick = item_sounds.wire_inventory_pickup }
local ELECTRIC = { move = item_sounds.electric_small_inventory_move, pick = item_sounds.electric_small_inventory_pickup }

data:extend({
  -- Mined, so nothing to weigh it by: as stone and calcite.
  item("sae-obsidian", ICON.obsidian, "vulcanus-processes", "z[sae-vf]-a[item]-a[obsidian]", 50, RESOURCE, 2 * kg),
  item("sae-obsidian-glass", ICON.glass, "vulcanus-processes", "z[sae-vf]-a[item]-b[obsidian-glass]", 100, BRICK),
  item("sae-obsidian-flux", ICON.flux, "vulcanus-processes", "z[sae-vf]-a[item]-c[obsidian-flux]", 50, RESOURCE),
  item("sae-slag-aggregate", ICON.slag, "vulcanus-processes", "z[sae-vf]-a[item]-d[slag-aggregate]", 50, RESOURCE),
  item("sae-holmium-oxide", ICON.oxide, "fulgora-processes", "z[sae-vf]-a[holmium-oxide]", 50, RESOURCE),
  -- It ships, so it stacks as the doc says: 50.
  item("sae-superconducting-coil", ICON.coil, "fulgora-processes", "z[sae-vf]-b[superconducting-coil]", 50, WIRE),
  item("sae-field-core", ICON.core, "vulcanus-processes", "z[sae-vf]-a[item]-e[field-core]", 50, ELECTRIC)
})

--------------------------------------------------------------------------------
-- Recipes.
--
-- Alternates that make a vanilla item follow vanilla's own alternates: no
-- auto-recycling (the vanilla recipe's reverse stays the one the recycler
-- uses) and no decomposition (so they never set a vanilla item's weight).
--------------------------------------------------------------------------------

local function fluid(name, amount, extra)
  local f = { type = "fluid", name = name, amount = amount }
  for k, v in pairs(extra or {}) do f[k] = v end
  return f
end
local function solid(name, amount) return { type = "item", name = name, amount = amount } end

-- A recipe that takes no productivity at all, the machine's built-in bonus
-- included. `allow_productivity = false` alone does NOT stop a machine's base
-- effect: in a client (2.1.24, T05a) an induction
-- foundry made 6 field cores from 4 crafts' worth and 30 magnetar alloy from
-- 20 field cores, both with allow_productivity false. Crafting machines clamp
-- productivity to the recipe's `maximum_productivity` (EffectReceiver,
-- productivity_limits), so 0 there is what holds it at none.
local NO_PRODUCTIVITY = { allow_productivity = false, maximum_productivity = 0 }

local function recipe(p)
  p.type = "recipe"
  p.enabled = false
  return p
end

-- An alternate route to a vanilla item.
local function alternate(p)
  p.auto_recycle = false
  p.allow_decomposition = false
  return recipe(p)
end

data:extend({
  ------------------------------------------------------------------ 1. mining
  -- Smelted like brick.
  recipe({
    name = "sae-obsidian-glass",
    categories = { "smelting" },
    energy_required = 3.2,
    ingredients = { solid("sae-obsidian", 2) },
    results = { solid("sae-obsidian-glass", 1) },
    allow_productivity = true,
    auto_recycle = false
  }),

  ------------------------------------------------------------------ 2. flux
  -- Lava is the planet's heat. **No productivity**: the foundry's built-in
  -- +50% would otherwise turn 100 acid into 150. See NO_PRODUCTIVITY.
  stand_in(alternate({
    name = "sae-superheated-sulfuric-acid",
    icons = ICON.hot_acid,
    categories = { "metallurgy" },
    subgroup = "vulcanus-processes",
    order = "z[sae-vf]-b[melting]-a[superheated-sulfuric-acid]",
    energy_required = 4,
    ingredients = { fluid("sulfuric-acid", 100), fluid("lava", 20) },
    results = { fluid("sulfuric-acid", 100, { temperature = HOT }) },
    allow_productivity = NO_PRODUCTIVITY.allow_productivity,
    maximum_productivity = NO_PRODUCTIVITY.maximum_productivity
  })),
  recipe({
    name = "sae-obsidian-flux",
    categories = { "chemistry" },
    energy_required = 1,
    ingredients =
    {
      solid("sae-obsidian-glass", 1),
      fluid("sulfuric-acid", 10, { minimum_temperature = HOT })
    },
    results = { solid("sae-obsidian-flux", 2) },
    allow_productivity = true,
    auto_recycle = false
  }),
  stand_in(alternate({
    name = "sae-molten-iron-from-lava-flux",
    icons = badged(vanilla(SA .. "icons/fluid/molten-iron-from-lava.png"), ICON.flux),
    categories = { "metallurgy" },
    subgroup = "vulcanus-processes",
    order = "z[sae-vf]-b[melting]-b[molten-iron-from-lava-flux]",
    energy_required = 16,
    ingredients = { fluid("lava", 500), solid("sae-obsidian-flux", 1) },
    results = { fluid("molten-iron", 300), solid("stone", 10) },
    allow_productivity = true
  })),

  ------------------------------------------------------------------ 3. fluxed steel
  -- A third less iron per steel; the glass carries the impurities away as slag.
  stand_in(alternate({
    name = "sae-fluxed-steel",
    icons = badged(vanilla(SA .. "icons/casting-steel.png"), ICON.flux),
    categories = { "metallurgy" },
    subgroup = "vulcanus-processes",
    order = "z[sae-vf]-c[casting]-a[fluxed-steel]",
    energy_required = 6.4,
    ingredients =
    {
      -- The box holds what casting steel's does, give or take.
      fluid("molten-iron", 40, { fluidbox_multiplier = 8 }),
      solid("sae-obsidian-flux", 1)
    },
    results = { solid("steel-plate", 2), solid("sae-slag-aggregate", 1) },
    allow_productivity = true
  })),
  stand_in(alternate({
    name = "sae-slag-concrete",
    icons = badged(vanilla(BASE .. "icons/concrete.png"), ICON.slag),
    categories = { "metallurgy" },
    subgroup = "vulcanus-processes",
    order = "z[sae-vf]-c[casting]-b[slag-concrete]",
    energy_required = 10,
    ingredients =
    {
      fluid("molten-iron", 20),
      fluid("water", 100),
      solid("sae-slag-aggregate", 5)
    },
    results = { solid("concrete", 10) },
    allow_productivity = true
  })),
  stand_in(alternate({
    name = "sae-slag-brick",
    icons = badged(vanilla(BASE .. "icons/stone-brick.png"), ICON.slag),
    categories = { "smelting" },
    subgroup = "vulcanus-processes",
    order = "z[sae-vf]-c[casting]-c[slag-brick]",
    energy_required = 3.2,
    ingredients = { solid("sae-slag-aggregate", 2) },
    results = { solid("stone-brick", 1) },
    allow_productivity = true
  })),

  ------------------------------------------------------------------ 4. refined iron
  -- A fifth of the iron lost to slag. Its only use is the convergence.
  recipe({
    name = "sae-refined-molten-iron",
    categories = { "metallurgy" },
    subgroup = "vulcanus-processes",
    order = "z[sae-vf]-b[melting]-c[refined-molten-iron]",
    main_product = "sae-refined-molten-iron",
    energy_required = 4,
    ingredients = { fluid("molten-iron", 100), solid("sae-obsidian-flux", 2) },
    results = { fluid("sae-refined-molten-iron", 80), solid("sae-slag-aggregate", 1) },
    allow_productivity = true,
    auto_recycle = false
  }),

  ------------------------------------------------------------------ 6. holmium oxide
  -- Six plates' worth per 100 solution, not five: 20% more holmium, paid in
  -- ozone. Fulgora only, since neither fluid has a barrel.
  recipe({
    name = "sae-holmium-oxide",
    categories = { "chemistry" },
    energy_required = 5,
    ingredients = { fluid("holmium-solution", 100), fluid("sae-ozone", 50) },
    results = { solid("sae-holmium-oxide", 6) },
    allow_productivity = true,
    auto_recycle = false
  }),
  stand_in(alternate({
    name = "sae-holmium-plate-from-oxide",
    icons = badged(vanilla(SA .. "icons/holmium-plate.png"), ICON.oxide),
    categories = { "metallurgy" },
    subgroup = "fulgora-processes",
    order = "z[sae-vf]-c[holmium-plate-from-oxide]",
    energy_required = 1,
    ingredients = { solid("sae-holmium-oxide", 1) },
    results = { solid("holmium-plate", 1) },
    allow_productivity = true
  })),

  ------------------------------------------------------------------ 7. oxide superconductor
  -- Vanilla's superconductor, cheaper (oxide for plate, no light oil) while
  -- the ozone lasts.
  stand_in(alternate({
    name = "sae-oxide-superconductor",
    icons = badged(vanilla(SA .. "icons/superconductor.png"), ICON.oxide),
    categories = { "electromagnetics" },
    subgroup = "fulgora-processes",
    order = "z[sae-vf]-d[oxide-superconductor]",
    energy_required = 5,
    ingredients =
    {
      solid("sae-holmium-oxide", 1),
      solid("copper-plate", 1),
      solid("plastic-bar", 1),
      fluid("sae-ozone", 20)
    },
    results = { solid("superconductor", 2) },
    allow_productivity = true
  })),

  ------------------------------------------------------------------ 8. the coil
  -- Fulgora only (electrolyte has no barrel); the coil itself ships.
  recipe({
    name = "sae-superconducting-coil",
    categories = { "electromagnetics" },
    energy_required = 10,
    ingredients =
    {
      solid("superconductor", 4),
      solid("steel-plate", 2),
      fluid("electrolyte", 10)
    },
    results = { solid("sae-superconducting-coil", 1) },
    allow_productivity = true
  }),

  ------------------------------------------------------------------ 9. the field recipes
  -- Holmium oxide fluxed into the refined iron and held in the foundry's field.
  -- Takes the built-in +50% like any cast.
  recipe({
    name = "sae-molten-holmium-iron",
    categories = { "sae-induction" },
    -- A fluid's recipe is filed nowhere useful by its product (fluids sit in
    -- the fluids group), so it is filed by hand, as vanilla's molten iron is.
    subgroup = "vulcanus-processes",
    order = "z[sae-vf]-d[field]-a[molten-holmium-iron]",
    energy_required = 4,
    ingredients = { fluid("sae-refined-molten-iron", 100), solid("sae-holmium-oxide", 2) },
    results = { fluid("sae-molten-holmium-iron", 100) },
    allow_productivity = true,
    auto_recycle = false
  }),
  -- That fluid cast round a coil. **No productivity**, here or in the charge,
  -- so one coil always makes one alloy.
  recipe({
    name = "sae-field-core",
    categories = { "sae-induction" },
    subgroup = "vulcanus-processes",
    order = "z[sae-vf]-d[field]-b[field-core]",
    energy_required = 10,
    ingredients = { solid("sae-superconducting-coil", 1), fluid("sae-molten-holmium-iron", 50) },
    results = { solid("sae-field-core", 1) },
    allow_productivity = NO_PRODUCTIVITY.allow_productivity,
    maximum_productivity = NO_PRODUCTIVITY.maximum_productivity,
    auto_recycle = false
  }),

  ------------------------------------------------------------------ 10. the capstone
  -- Charging is time in the field and nothing else. Named for the item, and
  -- the item's only recipe: the stub's, `sae-magnetar-alloy-stub`, is gone
  -- (prototypes/core/endgame.lua, migrations/space-age-extended-0.3.4.lua).
  recipe({
    name = "sae-magnetar-alloy",
    categories = { "sae-induction" },
    energy_required = 20,
    ingredients = { solid("sae-field-core", 1) },
    results = { solid("sae-magnetar-alloy", 1) },
    allow_productivity = NO_PRODUCTIVITY.allow_productivity,
    maximum_productivity = NO_PRODUCTIVITY.maximum_productivity,
    auto_recycle = false
  })
})

--------------------------------------------------------------------------------
-- The five induction casts: vanilla core casts, each for one extra ingredient
-- with a slight gain. Batched as the doc gives them (vanilla's recipe times
-- five or ten), so one extra item goes into each craft. "Hot acid" is sulfuric
-- acid at 500 or more.
--
-- Molten iron from lava and steel are left out: the tree has its own.
--
-- Where a cast's fluid box sets its buffer, it is sized to hold what the
-- vanilla cast's box holds (iron and copper plate 200, gears 100).
--------------------------------------------------------------------------------

local function hot_acid(amount) return fluid("sulfuric-acid", amount, { minimum_temperature = HOT }) end

local function cast(p)
  p.categories = { "sae-induction" }
  p.subgroup = "vulcanus-processes"
  p.allow_productivity = true
  return stand_in(alternate(p))
end

data:extend({
  -- Hot acid leaches copper out of the rock.
  cast({
    name = "sae-induction-molten-copper",
    icons = badged(vanilla(SA .. "icons/fluid/molten-copper-from-lava.png"), ICON.hot_acid),
    order = "z[sae-vf]-e[induction]-a[molten-copper]",
    energy_required = 15,
    ingredients = { fluid("lava", 500), solid("calcite", 1), hot_acid(20) },
    results = { fluid("molten-copper", 275), solid("stone", 15) }
  }),
  -- Flux skims the cast clean.
  cast({
    name = "sae-induction-casting-iron",
    icons = badged(vanilla(SA .. "icons/casting-iron.png"), ICON.flux),
    order = "z[sae-vf]-e[induction]-b[casting-iron]",
    energy_required = 15,
    ingredients = { fluid("molten-iron", 100, { fluidbox_multiplier = 2 }), solid("sae-obsidian-flux", 1) },
    results = { solid("iron-plate", 11) }
  }),
  -- Acid pickles the oxide skin off.
  cast({
    name = "sae-induction-casting-copper",
    icons = badged(vanilla(SA .. "icons/casting-copper.png"), ICON.hot_acid),
    order = "z[sae-vf]-e[induction]-c[casting-copper]",
    energy_required = 15,
    ingredients = { fluid("molten-copper", 100, { fluidbox_multiplier = 2 }), hot_acid(10) },
    results = { solid("copper-plate", 11) }
  }),
  -- Crushed slag as mould sand.
  cast({
    name = "sae-induction-casting-iron-gear-wheel",
    icons = badged(vanilla(SA .. "icons/casting-iron-gear-wheel.png"), ICON.slag),
    order = "z[sae-vf]-e[induction]-d[casting-iron-gear-wheel]",
    energy_required = 10,
    ingredients = { fluid("molten-iron", 100, { fluidbox_multiplier = 1 }), solid("sae-slag-aggregate", 1) },
    results = { solid("iron-gear-wheel", 11) }
  }),
  -- Flux in the melt means fewer breaks in the draw.
  cast({
    name = "sae-induction-casting-copper-cable",
    icons = badged(vanilla(SA .. "icons/casting-copper-cable.png"), ICON.flux),
    order = "z[sae-vf]-e[induction]-e[casting-copper-cable]",
    energy_required = 14,
    ingredients = { fluid("molten-copper", 75, { fluidbox_multiplier = 1 }), solid("sae-obsidian-flux", 1) },
    results = { solid("copper-cable", 33) }
  })
})

--------------------------------------------------------------------------------
-- The buildings. Each is written here field by field, from the vanilla building
-- it stands in for, and wears that building's sprites in its own tint until it
-- has art (derive.placeholder_art, under the entity's bare name).
--------------------------------------------------------------------------------

-- Tint every drawn layer of a copy of vanilla sprites, in place. Shadows, glows,
-- lights and additive layers keep their colour: they are light, not metal.
local function tint_layers(t, tint)
  if type(t) ~= "table" then return end
  if t.filename or t.filenames or t.stripes then
    if not (t.draw_as_shadow or t.draw_as_glow or t.draw_as_light
            or (t.blend_mode and t.blend_mode ~= "normal")) then
      t.tint = tint
    end
  end
  for k, v in pairs(t) do
    if k ~= "stripes" and k ~= "tint" then tint_layers(v, tint) end
  end
end

local OZONE_COLLECTOR_TINT = { 0.70, 0.86, 1.0 }     -- pale blue
local INDUCTION_FOUNDRY_TINT = { 0.66, 0.64, 1.0 }   -- cold blue-violet

ICON.ozone_collector = tinted(SA .. "icons/lightning-collector.png", OZONE_COLLECTOR_TINT)
ICON.induction_foundry = tinted(SA .. "icons/foundry.png", INDUCTION_FOUNDRY_TINT)

--------------------------------------------------------------------------------
-- The ozone collector, from the lightning collector.
--
-- Against it: the same 2x2 attractor, but the rod's reach (range elongation 15,
-- not 25), and it keeps none of a strike's power (efficiency 0, which the
-- engine allows only with no energy source). What a strike gives instead is
-- 100 ozone, held up to 1,000.
--
-- A lightning attractor has no fluid box, so the building is two entities:
-- this attractor, which the player builds and sees, and a hidden storage tank
-- on the same tiles that holds the ozone and has the pipe connection. The
-- script (scripts/trees/vulcanus-fulgora.lua) puts the tank down when the
-- collector is built, takes it away with it, and adds the ozone on each strike.
--------------------------------------------------------------------------------

local OZONE_COLLECTOR = "sae-ozone-collector"
local OZONE_TANK = "sae-ozone-collector-tank"

local collector_graphics = table.deepcopy(require("__space-age__.prototypes.entity.lightning-collector-graphics"))
tint_layers(collector_graphics, OZONE_COLLECTOR_TINT)

data:extend({
  derive.placeholder_art({
    type = "lightning-attractor",
    name = OZONE_COLLECTOR,
    icons = ICON.ozone_collector,
    flags = { "placeable-neutral", "player-creation" },
    minable = { mining_time = 0.1, result = OZONE_COLLECTOR },
    max_health = 200,
    corpse = "lightning-collector-remnants",
    dying_explosion = "substation-explosion",
    efficiency = 0,
    range_elongation = 15,
    resistances =
    {
      { type = "fire", percent = 90 },
      { type = "electric", percent = 100 }
    },
    collision_box = { { -0.7, -0.7 }, { 0.7, 0.7 } },
    selection_box = { { -1, -1 }, { 1, 1 } },
    lightning_strike_offset = { 0, -4.8 },
    damaged_trigger_effect = hit_effects.entity({ { -0.5, -2.5 }, { 0.5, 0.5 } }),
    drawing_box_vertical_extension = 4.5,
    impact_category = "metal",
    -- The lightning collector's own sounds, as a stand-in wears its sprites.
    open_sound = entity_sounds.electric_large_open,
    close_sound = entity_sounds.electric_large_close,
    working_sound = table.deepcopy(data.raw["lightning-attractor"]["lightning-collector"].working_sound),
    chargable_graphics = collector_graphics
  }, "wears the lightning collector's sprites, tinted pale blue, until its own exist"),

  -- The hidden half. Nothing collides with it (it sits under the attractor),
  -- it cannot be selected, mined, blueprinted or deconstructed, and the script
  -- makes it indestructible: it lives and dies with its collector.
  {
    type = "storage-tank",
    name = OZONE_TANK,
    icons = ICON.ozone_collector,
    hidden = true,
    flags = { "not-on-map", "not-blueprintable", "not-deconstructable", "not-upgradable", "no-copy-paste",
              "not-in-kill-statistics" },
    max_health = 200,
    collision_box = { { -0.7, -0.7 }, { 0.7, 0.7 } },
    collision_mask = { layers = {} },
    selectable_in_game = false,
    fluid_box =
    {
      volume = 1000,
      filter = "sae-ozone",
      -- Capped with vanilla's cover until a pipe joins.
      pipe_covers = derive.pipe_covers(),
      pipe_connections = { { direction = defines.direction.south, position = { 0.5, 0.5 } } }
    },
    window_bounding_box = { { 0, 0 }, { 0, 0 } },
    flow_length_in_ticks = 360
  },

  stand_in({
    type = "item",
    name = OZONE_COLLECTOR,
    icons = ICON.ozone_collector,
    subgroup = "environmental-protection",
    order = "b[lightning-collector]-b[sae-ozone-collector]",
    inventory_move_sound = item_sounds.electric_large_inventory_move,
    pick_sound = item_sounds.electric_large_inventory_pickup,
    drop_sound = item_sounds.electric_large_inventory_move,
    place_result = OZONE_COLLECTOR,
    stack_size = 20
  }),

  -- Half the lightning collector's supercapacitors and electrolyte, and a
  -- storage tank for its accumulator. Fulgora only, as the collector's.
  recipe({
    name = OZONE_COLLECTOR,
    categories = { "electromagnetics" },
    surface_conditions = { { property = "magnetic-field", min = 99, max = 99 } },
    energy_required = 5,
    ingredients =
    {
      solid("lightning-rod", 1),
      solid("supercapacitor", 4),
      solid("storage-tank", 1),
      fluid("electrolyte", 40)
    },
    results = { solid(OZONE_COLLECTOR, 1) }
  })
})

-- What makes a strike on it ozone (a script effect on every lightning) and
-- Fulgora's lightning seeking it are in data-final-fixes, through
-- prototypes/trees/vulcanus-fulgora-final.lua: both edit vanilla prototypes
-- that another mod may define or replace after this file runs.

--------------------------------------------------------------------------------
-- The induction foundry, from the foundry.
--
-- The foundry's equal as a machine: 5x5, speed 4, +50% built-in productivity,
-- 4 modules. It draws 4 MW (2.5 MW) and crafts `sae-induction` only, so it runs
-- no vanilla recipe: every gain is in its eight recipes, paid for by each one's
-- extra ingredient. Field core and magnetar alloy forbid productivity, so the
-- built-in +50% never touches them.
--
-- Its fluid boxes are the foundry's: two in on the south side, two out on the
-- north. The most an induction recipe needs is two in and one out.
--------------------------------------------------------------------------------

local INDUCTION_FOUNDRY = "sae-induction-foundry"
local foundry = data.raw["assembling-machine"]["foundry"]

local induction_graphics = table.deepcopy(foundry.graphics_set)
tint_layers(induction_graphics, INDUCTION_FOUNDRY_TINT)

-- One of the four boxes. The foundry's sprites draw the pipe ends themselves
-- (its "input-pipe" and "output-pipe" visualisations), so the box draws none,
-- only vanilla's cover over a port with nothing joined, and the foundry's iced
-- pipe ends on Aquilo (the foundry gives them to two of its four boxes; a
-- stand-in gives them to all four).
local foundry_pipe_frozen = require("__space-age__.prototypes.entity.foundry-pictures").pipe_picture_frozen

local function induction_box(production_type, x)
  local south = production_type == "input"
  return
  {
    production_type = production_type,
    pipe_picture = util.empty_sprite(),
    pipe_picture_frozen = table.deepcopy(foundry_pipe_frozen),
    pipe_covers = derive.pipe_covers(),
    always_draw_covers = false,
    enable_working_visualisations = { production_type .. "-pipe" },
    volume = south and 1000 or 100,
    pipe_connections =
    {
      {
        flow_direction = production_type,
        direction = south and defines.direction.south or defines.direction.north,
        position = { x, south and 2 or -2 }
      }
    }
  }
end

data:extend({
  derive.placeholder_art({
    type = "assembling-machine",
    name = INDUCTION_FOUNDRY,
    icons = ICON.induction_foundry,
    flags = { "placeable-neutral", "player-creation" },
    minable = { mining_time = 0.2, result = INDUCTION_FOUNDRY },
    max_health = 350,
    corpse = "foundry-remnants",
    dying_explosion = "foundry-explosion",
    circuit_wire_max_distance = foundry.circuit_wire_max_distance,
    circuit_connector = table.deepcopy(foundry.circuit_connector),
    collision_box = { { -2.2, -2.2 }, { 2.2, 2.2 } },
    selection_box = { { -2.5, -2.5 }, { 2.5, 2.5 } },
    heating_energy = "300kW",
    damaged_trigger_effect = hit_effects.entity(),
    drawing_box_vertical_extension = 1.3,
    effect_receiver = { base_effect = { productivity = 0.5 } },
    module_slots = 4,
    allowed_effects = { "consumption", "speed", "productivity", "pollution", "quality" },
    icon_draw_specification = { scale = 2, shift = { 0, -0.3 } },
    icons_positioning = { { inventory_index = defines.inventory.crafter_modules, shift = { 0, 1.25 } } },
    crafting_categories = { "sae-induction" },
    crafting_speed = 4,
    energy_source =
    {
      type = "electric",
      usage_priority = "secondary-input",
      emissions_per_minute = { pollution = 6 }
    },
    energy_usage = "4MW",
    perceived_performance = { minimum = 0.25, maximum = 20 },
    use_mirroring = true,
    graphics_set = induction_graphics,
    open_sound = entity_sounds.steam_open,
    close_sound = entity_sounds.steam_close,
    -- The foundry's own, cued to frames of the main animation it wears.
    working_sound = table.deepcopy(foundry.working_sound),
    fluid_boxes =
    {
      induction_box("input", -1),
      induction_box("input", 1),
      induction_box("output", -1),
      induction_box("output", 1)
    },
    fluid_boxes_off_when_no_fluid_recipe = true
  }, "wears the foundry's sprites, tinted cold blue-violet, until its own exist"),

  stand_in({
    type = "item",
    name = INDUCTION_FOUNDRY,
    icons = ICON.induction_foundry,
    subgroup = "smelting-machine",
    order = "d[foundry]-b[sae-induction-foundry]",
    inventory_move_sound = item_sounds.steam_inventory_move,
    pick_sound = item_sounds.steam_inventory_pickup,
    drop_sound = item_sounds.steam_inventory_move,
    place_result = INDUCTION_FOUNDRY,
    stack_size = 20
  }),

  -- A foundry wound with Fulgora's coil and lined with obsidian glass. Where
  -- the foundry's own recipe can be made: pressure 4000 (Vulcanus). Made in an
  -- assembler only, never by hand (Liam, Q15): `advanced-crafting` is the
  -- category vanilla gives the engine unit for the same reason, every
  -- assembler has it and the character does not (its categories are
  -- `crafting` and `hand-crafting`).
  recipe({
    name = INDUCTION_FOUNDRY,
    categories = { "advanced-crafting" },
    surface_conditions = { { property = "pressure", min = 4000, max = 4000 } },
    energy_required = 20,
    ingredients =
    {
      solid("foundry", 1),
      solid("sae-superconducting-coil", 10),
      solid("sae-obsidian-glass", 20),
      solid("tungsten-plate", 20)
    },
    results = { solid(INDUCTION_FOUNDRY, 1) }
  })
})

--------------------------------------------------------------------------------
-- The magnetic collector, from the asteroid collector.
--
-- Against it: twice the reach (collection radius 15, not 7.5) and arms almost
-- three times as fast (arm and turn speed 0.55, not 0.2), which is what catches
-- the magnetic chunk below; T02e measured 70-100 % of them in flight, against
-- vanilla's 0-16 %. Paid for in power, four times the energy per arm move
-- (4 kJ, slow 1.2 kJ; vanilla 1 kJ and 300 J), and in ten magnetar alloy.
--
-- No filter is set on it or changed on any collector (Liam: "We shouldn't alter
-- the filter of either collector"), so it takes every chunk there is, as
-- vanilla's does; nothing in the mod's script touches a collector. Everything
-- not named above is the asteroid collector's: the catch box 5 tiles ahead,
-- one arm and one more per quality level, the holds, the quality scaling.
--------------------------------------------------------------------------------

local MAGNETIC_COLLECTOR = "sae-magnetic-collector"
local MAGNETIC_COLLECTOR_TINT = { 0.50, 0.52, 0.58 }   -- dark iron-grey
local asteroid_collector = data.raw["asteroid-collector"]["asteroid-collector"]

local magnetic_graphics = table.deepcopy(asteroid_collector.graphics_set)
tint_layers(magnetic_graphics, MAGNETIC_COLLECTOR_TINT)

ICON.magnetic_collector = tinted(SA .. "icons/asteroid-collector.png", MAGNETIC_COLLECTOR_TINT)

data:extend({
  derive.placeholder_art({
    type = "asteroid-collector",
    name = MAGNETIC_COLLECTOR,
    icons = ICON.magnetic_collector,
    flags = { "placeable-neutral", "placeable-player", "player-creation" },
    minable = { mining_time = 0.2, result = MAGNETIC_COLLECTOR },
    max_health = 300,
    corpse = "asteroid-collector-remnants",
    dying_explosion = "asteroid-collector-explosion",
    resistances = { { type = "fire", percent = 70 } },
    impact_category = "metal",
    -- The asteroid collector's footprint: 3x3 on the platform's edge, its
    -- front over empty space.
    collision_box = { { -1.2, -1.2 }, { 1.2, 1.2 } },
    collision_mask = { layers = { is_object = true, is_lower_object = true, transport_belt = true } },
    selection_box = { { -1.5, -1.5 }, { 1.5, 1.5 } },
    tile_width = 3,
    tile_height = 3,
    tile_buildability_rules =
    {
      { area = { { -1.4, -0.4 }, { 1.4, 1.4 } }, required_tiles = { layers = { ground_tile = true } },
        colliding_tiles = { layers = { empty_space = true } }, remove_on_collision = true },
      { area = { { -1.4, -4.4 }, { 1.4, -0.6 } }, required_tiles = { layers = { empty_space = true } },
        remove_on_collision = true }
    },
    surface_conditions = { { property = "pressure", min = 0, max = 0 } },

    -- What it is for.
    collection_radius = 15,
    collection_box_offset = 5,
    deposit_radius = 1.5,
    head_collection_radius = 0.6,
    arm_count_base = 1,
    arm_count_quality_scaling = 1,
    arm_speed_base = 0.55,
    arm_speed_quality_scaling = 0.05,
    arm_angular_speed_cap_base = 0.55,
    arm_angular_speed_cap_quality_scaling = 0.05,
    minimal_arm_swing_segment_retraction = 6,
    tether_size = 0.35,
    unpowered_arm_speed_scale = 0.3,
    held_items_offset = 0.6,
    inventory_size = 39,
    inventory_size_quality_increase = 5,
    arm_inventory_size = 5,
    arm_inventory_size_quality_increase = 0,

    -- What it costs to run.
    energy_source = { type = "electric", usage_priority = "secondary-input" },
    passive_energy_usage = "200J",
    arm_energy_usage = "4kJ",
    arm_slow_energy_usage = "1.2kJ",
    energy_usage_quality_scaling = 0.1,

    circuit_wire_max_distance = asteroid_collector.circuit_wire_max_distance,
    circuit_connector = table.deepcopy(asteroid_collector.circuit_connector),
    -- The asteroid collector's sounds and arm colours, as a stand-in wears its
    -- sprites.
    open_sound = entity_sounds.mech_small_open,
    close_sound = entity_sounds.mech_small_close,
    munch_sound = table.deepcopy(asteroid_collector.munch_sound),
    arm_extend_sound = table.deepcopy(asteroid_collector.arm_extend_sound),
    arm_retract_sound = table.deepcopy(asteroid_collector.arm_retract_sound),
    deposit_sound = table.deepcopy(asteroid_collector.deposit_sound),
    arm_color_gradient = table.deepcopy(asteroid_collector.arm_color_gradient),
    graphics_set = magnetic_graphics,
    radius_visualisation_picture = table.deepcopy(asteroid_collector.radius_visualisation_picture)
  }, "wears the asteroid collector's sprites, tinted dark iron-grey, until its own exist"),

  stand_in({
    type = "item",
    name = MAGNETIC_COLLECTOR,
    icons = ICON.magnetic_collector,
    subgroup = "space-platform",
    order = "d[asteroid-collector]-b[sae-magnetic-collector]",
    inventory_move_sound = item_sounds.mechanical_inventory_move,
    pick_sound = item_sounds.mechanical_inventory_pickup,
    drop_sound = item_sounds.mechanical_inventory_move,
    place_result = MAGNETIC_COLLECTOR,
    -- As the asteroid collector: ten to a stack, ten to a rocket.
    stack_size = 10,
    weight = 100 * kg
  }),

  -- An asteroid collector given a magnetar alloy arm and a coil. In an
  -- assembler or by hand, as the asteroid collector is.
  recipe({
    name = MAGNETIC_COLLECTOR,
    categories = { "crafting" },
    energy_required = 10,
    ingredients =
    {
      solid("asteroid-collector", 1),
      solid("sae-magnetar-alloy", 10),
      solid("sae-superconducting-coil", 2)
    },
    results = { solid(MAGNETIC_COLLECTOR, 1) }
  })
})

--------------------------------------------------------------------------------
-- The magnetic chunk, and the route it flies on.
--
-- A new chunk, faster than any asteroid: own speed 0.25 tiles a tick (15 m/s;
-- vanilla's asteroids fly at 1 m/s), which an asteroid collector's arm at rest
-- cannot reach in time and a magnetic collector's can (T02e). It is the
-- metallic chunk's art until it has its own. It flies on one route only, the
-- new direct Vulcanus <-> Fulgora connection: no planet carries it, so no
-- planet's asteroid_spawn_influence can carry it onto another route.
--------------------------------------------------------------------------------

local MAGNETIC_CHUNK = "sae-magnetic-asteroid-chunk"
local MAGNETITE = "sae-magnetite"
local MAGNETIC_TINT = { 0.55, 0.70, 1.0 }
local metallic_chunk = data.raw["asteroid-chunk"]["metallic-asteroid-chunk"]

ICON.magnetic_chunk = tinted(SA .. "icons/metallic-asteroid-chunk.png", MAGNETIC_TINT)
ICON.magnetite = tinted(BASE .. "icons/iron-ore.png", { 0.42, 0.42, 0.50 })
ICON.magnetite_round = tinted(SA .. "icons/railgun-ammo.png", MAGNETIC_TINT)

data:extend({
  stand_in({
    type = "asteroid-chunk",
    name = MAGNETIC_CHUNK,
    icons = ICON.magnetic_chunk,
    -- A chunk is not an entity, so its description is pointed at its item's,
    -- as vanilla points each chunk at its asteroid's.
    localised_description = { "item-description." .. MAGNETIC_CHUNK },
    subgroup = "space-material",
    order = "z[sae-vf]-a[magnetic-asteroid-chunk]",
    minable = { mining_time = 0.2, result = MAGNETIC_CHUNK, mining_particle = "metallic-asteroid-chunk-particle-medium" },
    dying_trigger_effect =
    {
      { type = "create-entity", entity_name = "metallic-asteroid-explosion-1", only_when_visible = true }
    },
    graphics_set = table.deepcopy(metallic_chunk.graphics_set)
  }, "wears the metallic chunk's art until its own exists"),

  -- The held form, on vanilla's chunk-item pattern: one to a stack, 100 kg.
  stand_in({
    type = "item",
    name = MAGNETIC_CHUNK,
    icons = ICON.magnetic_chunk,
    subgroup = "space-material",
    order = "z[sae-vf]-a[magnetic-asteroid-chunk]",
    inventory_move_sound = space_age_item_sounds.rock_inventory_move,
    pick_sound = space_age_item_sounds.rock_inventory_pickup,
    drop_sound = space_age_item_sounds.rock_inventory_move,
    stack_size = 1,
    weight = 100 * kg
  })
})

-- THE ROUTE'S ORDINARY ASTEROIDS: a blend of Nauvis-Vulcanus and Nauvis-Fulgora
-- (Liam, Q16), built from those two connections' own spawn definitions.
--
-- How vanilla says where along a route an asteroid spawns: each definition is
-- a list of spawn points, each at a `distance` from 0 (the route's `from`) to 1
-- (its `to`), and the engine interpolates between them. Vanilla puts the two
-- planets' own mixes at distance 0.1 and 0.9 and the route's mid-point at 0.5
-- (space-age/prototypes/planet/asteroid-spawn-definitions.lua).
--
-- This route runs from Vulcanus (0) to Fulgora (1). Nauvis-Vulcanus has
-- Vulcanus at 1, so it is read end to end reversed, distance 1 - d; Nauvis-Fulgora
-- has Fulgora at 1 already. At each distance where either has a point, the
-- route's point is the two read there and mixed: all Nauvis-Vulcanus at 0.1
-- (its Vulcanus end), all Nauvis-Fulgora at 0.9 (its Fulgora end), and evenly
-- between, half each at 0.5. Probability, speed and angle are all mixed.

local VULCANUS_END, FULGORA_END = 0.1, 0.9

-- One definition's point at distance d, read straight between its points and
-- held flat beyond the first and the last.
local function point_at(points, d)
  local sorted = {}
  for _, p in ipairs(points) do sorted[#sorted + 1] = p end
  table.sort(sorted, function(a, b) return a.distance < b.distance end)
  local function of(p) return { probability = p.probability, speed = p.speed, angle = p.angle_when_stopped or 1 } end
  if d <= sorted[1].distance then return of(sorted[1]) end
  if d >= sorted[#sorted].distance then return of(sorted[#sorted]) end
  for i = 1, #sorted - 1 do
    local a, b = sorted[i], sorted[i + 1]
    if d <= b.distance then
      local t = (d - a.distance) / (b.distance - a.distance)
      local pa, pb = of(a), of(b)
      return
      {
        probability = pa.probability + t * (pb.probability - pa.probability),
        speed = pa.speed + t * (pb.speed - pa.speed),
        angle = pa.angle + t * (pb.angle - pa.angle)
      }
    end
  end
end

-- A connection's definitions by asteroid, optionally read end to end reversed.
-- A reversed distance is rounded to a millionth: 1 - 0.9 is not 0.1 in floating
-- point, and the two sides' points have to meet at the same distances.
local function definitions_of(connection_name, reversed)
  local connection = data.raw["space-connection"][connection_name]
  assert(connection, "space-connection " .. connection_name .. " does not exist")
  local out, order = {}, {}
  for _, def in ipairs(connection.asteroid_spawn_definitions or {}) do
    local points = {}
    for _, p in ipairs(def.spawn_points) do
      points[#points + 1] =
      {
        distance = reversed and math.floor((1 - p.distance) * 1e6 + 0.5) / 1e6 or p.distance,
        probability = p.probability,
        speed = p.speed,
        angle_when_stopped = p.angle_when_stopped
      }
    end
    out[def.asteroid] = { type = def.type, points = points }
    order[#order + 1] = def.asteroid
  end
  return out, order
end

local function blend(vulcanus_side, fulgora_side)
  local near, near_order = definitions_of(vulcanus_side, true)
  local far, far_order = definitions_of(fulgora_side, false)
  local names, seen = {}, {}
  for _, list in ipairs({ near_order, far_order }) do
    for _, name in ipairs(list) do
      if not seen[name] then seen[name] = true; names[#names + 1] = name end
    end
  end

  local defs = {}
  for _, name in ipairs(names) do
    local a, b = near[name], far[name]
    local distances, at = {}, {}
    for _, side in ipairs({ a or false, b or false }) do
      for _, p in ipairs(side and side.points or {}) do
        if not at[p.distance] then at[p.distance] = true; distances[#distances + 1] = p.distance end
      end
    end
    table.sort(distances)
    local points = {}
    for _, d in ipairs(distances) do
      local w = math.min(1, math.max(0, (d - VULCANUS_END) / (FULGORA_END - VULCANUS_END)))
      -- An asteroid only one route has counts as none on the other.
      local pa = a and point_at(a.points, d)
      local pb = b and point_at(b.points, d)
      pa = pa or { probability = 0, speed = pb.speed, angle = pb.angle }
      pb = pb or { probability = 0, speed = pa.speed, angle = pa.angle }
      points[#points + 1] =
      {
        distance = d,
        probability = (1 - w) * pa.probability + w * pb.probability,
        speed = (1 - w) * pa.speed + w * pb.speed,
        angle_when_stopped = (1 - w) * pa.angle + w * pb.angle
      }
    end
    defs[#defs + 1] = { type = (a or b).type, asteroid = name, spawn_points = points }
  end
  return defs
end

local route_asteroids = blend("nauvis-vulcanus", "nauvis-fulgora")

-- And the magnetic chunk, the same at every point: probability 0.0015 at each
-- of the route's three, about 4-5 % of the chunks in flight (T02e).
local MAGNETIC_CHUNK_SPEED = 0.25
local MAGNETIC_CHUNK_PROBABILITY = 0.0015
local magnetic_points = {}
for _, d in ipairs({ VULCANUS_END, 0.5, FULGORA_END }) do
  magnetic_points[#magnetic_points + 1] =
    { distance = d, probability = MAGNETIC_CHUNK_PROBABILITY, speed = MAGNETIC_CHUNK_SPEED, angle_when_stopped = 1 }
end
route_asteroids[#route_asteroids + 1] = { type = "asteroid-chunk", asteroid = MAGNETIC_CHUNK, spawn_points = magnetic_points }

data:extend({
  {
    -- Space Age's data-updates gives it vanilla's route icon (the two planets
    -- over planet-route.png), as it does every connection with none.
    type = "space-connection",
    name = "sae-vulcanus-fulgora",
    subgroup = "planet-connections",
    from = "vulcanus",
    to = "fulgora",
    -- After Vulcanus-Gleba (d), before Gleba-Fulgora (e).
    order = "d-b[sae-vulcanus-fulgora]",
    -- As every vanilla route between inner planets.
    length = 15000,
    asteroid_spawn_definitions = route_asteroids
  }
})

--------------------------------------------------------------------------------
-- Magnetite and the magnetite round.
--
-- Crushed, a magnetic chunk gives 10 magnetite (Liam: "10"), and the chunk back
-- as often as vanilla's metallic crushing gives it back. Magnetite has one use,
-- the round: railgun ammunition for the biggest targets. 15,000 physical
-- against vanilla's 10,000 kills a huge promethium asteroid (10,000 health,
-- 3,000 off a hit and then 10 %) in one shot where vanilla's takes two, and it
-- fires 1.5 times slower (cooldown_modifier 1.5: 255 ticks on the railgun
-- turret, against 170). Everything else is vanilla's railgun ammo, so vanilla's
-- railgun research boosts both alike.
--------------------------------------------------------------------------------

local MAGNETITE_ROUND = "sae-magnetite-round"

data:extend({
  -- Stacked and weighed as vanilla's ores are.
  item(MAGNETITE, ICON.magnetite, "space-material", "z[sae-vf]-b[magnetite]", 50, RESOURCE, 2 * kg),

  stand_in({
    type = "ammo",
    name = MAGNETITE_ROUND,
    icons = ICON.magnetite_round,
    ammo_category = "railgun",
    ammo_type =
    {
      target_type = "direction",
      clamp_position = true,
      cooldown_modifier = 1.5,
      action =
      {
        type = "line",
        range = 50,
        width = 1,
        range_effects = { type = "create-explosion", entity_name = "railgun-beam", only_when_visible = true },
        action_delivery =
        {
          type = "instant",
          target_effects = { type = "damage", damage = { amount = 15000, type = "physical" } },
          source_effects = { type = "create-explosion", entity_name = "explosion-gunshot", only_when_visible = true }
        }
      }
    },
    subgroup = "ammo",
    -- Beside vanilla's railgun ammo.
    order = "e[railgun-ammo]-b[sae-magnetite-round]",
    inventory_move_sound = item_sounds.ammo_large_inventory_move,
    pick_sound = item_sounds.ammo_large_inventory_pickup,
    drop_sound = item_sounds.ammo_large_inventory_move,
    stack_size = 10,
    weight = 200 * kg
  }),

  -- Vanilla's metallic crushing, with magnetite for iron ore.
  stand_in(recipe({
    name = "sae-magnetic-asteroid-crushing",
    icons = badged(tinted(SA .. "icons/metallic-asteroid-crushing.png", MAGNETIC_TINT), ICON.magnetite),
    categories = { "crushing" },
    subgroup = "space-crushing",
    order = "z[sae-vf]-a[magnetic-asteroid-crushing]",
    energy_required = 2,
    ingredients = { { type = "item", name = MAGNETIC_CHUNK, amount = 1, ignored_by_stats = 1 } },
    results =
    {
      solid(MAGNETITE, 10),
      { type = "item", name = MAGNETIC_CHUNK, amount = 1, independent_probability = 0.3, ignored_by_stats = 1 }
    },
    allow_productivity = true,
    allow_decomposition = false,
    auto_recycle = false
  })),

  -- Vanilla's round, with magnetite and the coil for its copper cable. In an
  -- assembler or by hand, as vanilla's is.
  recipe({
    name = MAGNETITE_ROUND,
    categories = { "crafting" },
    energy_required = 30,
    ingredients =
    {
      solid(MAGNETITE, 5),
      solid("sae-superconducting-coil", 2),
      solid("steel-plate", 5),
      solid("explosives", 2)
    },
    results = { solid(MAGNETITE_ROUND, 1) }
  })
})

--------------------------------------------------------------------------------
-- Technologies. Ten: the Vulcanus path on metallurgic science, the Fulgora path
-- on electromagnetic, the two shared steps on both, each with the packs those
-- need. Both openers require both planets' science packs, so the tree opens
-- only once both vanilla trees are done.
--
-- The ozone collector unlocks with Ozone capture, the induction foundry with
-- Induction foundry and the magnetic collector with Magnetar alloy.
--
-- And an eleventh, outside the tree: Magnetite rounds, after the railgun and
-- the capstone, on the railgun's ten packs at half its count.
--------------------------------------------------------------------------------

local function packs(...)
  local out = {}
  for _, name in ipairs({ "automation-science-pack", "logistic-science-pack",
                          "chemical-science-pack", "space-science-pack", ... }) do
    out[#out + 1] = { name, 1 }
  end
  return out
end
local VULCANUS = packs("metallurgic-science-pack")
local FULGORA = packs("electromagnetic-science-pack")
local BOTH = packs("metallurgic-science-pack", "electromagnetic-science-pack")

local function tech(name, icon, tint, prerequisites, ingredients, count, recipes)
  local effects = {}
  for _, r in ipairs(recipes) do effects[#effects + 1] = { type = "unlock-recipe", recipe = r } end
  return stand_in({
    type = "technology",
    name = name,
    icons = tinted(icon, tint, 256),
    effects = effects,
    prerequisites = prerequisites,
    unit = { count = count, ingredients = ingredients, time = 60 }
  }, "wears a tinted vanilla technology icon until its own exists")
end

local TECH = SA .. "technology/"
local BASE_TECH = BASE .. "technology/"

local magnetar = tech("sae-vf-magnetar-alloy", TECH .. "advanced-asteroid-processing.png", { 0.55, 0.55, 0.60 },
  { "sae-vf-induction-foundry" }, BOTH, 1000, { "sae-magnetar-alloy", MAGNETIC_COLLECTOR })
magnetar.essential = true

-- The railgun's own ten packs.
local RAILGUN = packs("military-science-pack", "utility-science-pack", "metallurgic-science-pack",
                      "electromagnetic-science-pack", "agricultural-science-pack", "cryogenic-science-pack")

data:extend({
  -- Vulcanus.
  tech("sae-vf-obsidian-mining", TECH .. "calcite-processing.png", OBSIDIAN_TINT,
    { "metallurgic-science-pack", "electromagnetic-science-pack" }, VULCANUS, 200,
    { "sae-obsidian-glass" }),
  tech("sae-vf-obsidian-flux", BASE_TECH .. "sulfur-processing.png", { 1.0, 0.60, 0.40 },
    { "sae-vf-obsidian-mining" }, VULCANUS, 300,
    { "sae-superheated-sulfuric-acid", "sae-obsidian-flux", "sae-molten-iron-from-lava-flux" }),
  tech("sae-vf-fluxed-steel", BASE_TECH .. "steel-processing.png", { 0.75, 0.60, 0.85 },
    { "sae-vf-obsidian-flux" }, VULCANUS, 400,
    { "sae-fluxed-steel", "sae-slag-concrete", "sae-slag-brick" }),
  tech("sae-vf-refined-molten-iron", TECH .. "foundry.png", { 0.80, 0.90, 1.0 },
    { "sae-vf-fluxed-steel" }, VULCANUS, 500,
    { "sae-refined-molten-iron" }),

  -- Fulgora.
  tech("sae-vf-ozone-capture", TECH .. "lightning-collector.png", { 0.60, 0.85, 1.0 },
    { "electromagnetic-science-pack", "metallurgic-science-pack", "lightning-collector" }, FULGORA, 200,
    { "sae-ozone-collector" }),
  tech("sae-vf-holmium-oxide", TECH .. "holmium-processing.png", { 1.0, 0.92, 0.70 },
    { "sae-vf-ozone-capture" }, FULGORA, 300,
    { "sae-holmium-oxide", "sae-holmium-plate-from-oxide" }),
  tech("sae-vf-oxide-superconductor", TECH .. "electromagnetic-plant.png", { 1.0, 0.90, 0.75 },
    { "sae-vf-holmium-oxide" }, FULGORA, 400,
    { "sae-oxide-superconductor" }),
  tech("sae-vf-superconducting-coil", BASE_TECH .. "electric-engine.png", { 0.60, 0.80, 1.0 },
    { "sae-vf-oxide-superconductor" }, FULGORA, 500,
    { "sae-superconducting-coil" }),

  -- Where they meet.
  tech("sae-vf-induction-foundry", TECH .. "foundry.png", { 0.55, 0.50, 0.95 },
    { "sae-vf-refined-molten-iron", "sae-vf-superconducting-coil" }, BOTH, 750,
    {
      "sae-induction-foundry", "sae-molten-holmium-iron", "sae-field-core",
      "sae-induction-molten-copper", "sae-induction-casting-iron", "sae-induction-casting-copper",
      "sae-induction-casting-iron-gear-wheel", "sae-induction-casting-copper-cable"
    }),
  magnetar,

  -- After the tree.
  tech("sae-vf-magnetite-rounds", TECH .. "railgun.png", MAGNETIC_TINT,
    { "railgun", "sae-vf-magnetar-alloy" }, RAILGUN, 1000,
    { "sae-magnetic-asteroid-crushing", MAGNETITE_ROUND })
})
