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
-- What is NOT in this file yet: the three buildings (ozone collector,
-- induction foundry, magnetic collector), their recipes and unlocks, and the
-- script that turns a strike into ozone. Until they land, nothing makes ozone
-- and nothing crafts `sae-induction`.

local derive = require("prototypes.derive")
local item_sounds = require("__base__.prototypes.item_sounds")

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

local function stand_in(p)
  return derive.placeholder_art(p, "wears a tinted vanilla icon until its own exists")
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
-- patch. Against tungsten: 10 spots a region (15), radius 20 x size (25),
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
                                                     sae_obsidian_size * min(1.2, vulcanus_ore_dist) * 20,\z
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
  item("sae-obsidian", ICON.obsidian, "vulcanus-processes", "z[sae-vf]-a[obsidian]", 50, RESOURCE, 2 * kg),
  item("sae-obsidian-glass", ICON.glass, "vulcanus-processes", "z[sae-vf]-b[obsidian-glass]", 100, BRICK),
  item("sae-obsidian-flux", ICON.flux, "vulcanus-processes", "z[sae-vf]-c[obsidian-flux]", 50, RESOURCE),
  item("sae-slag-aggregate", ICON.slag, "vulcanus-processes", "z[sae-vf]-d[slag-aggregate]", 50, RESOURCE),
  item("sae-holmium-oxide", ICON.oxide, "fulgora-processes", "z[sae-vf]-a[holmium-oxide]", 50, RESOURCE),
  -- It ships, so it stacks as the doc says: 50.
  item("sae-superconducting-coil", ICON.coil, "fulgora-processes", "z[sae-vf]-b[superconducting-coil]", 50, WIRE),
  item("sae-field-core", ICON.core, "vulcanus-processes", "z[sae-vf]-e[field-core]", 50, ELECTRIC)
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
  -- +50% would otherwise turn 100 acid into 150.
  stand_in(alternate({
    name = "sae-superheated-sulfuric-acid",
    icons = ICON.hot_acid,
    categories = { "metallurgy" },
    subgroup = "vulcanus-processes",
    order = "z[sae-vf]-a[melting]-a[superheated-sulfuric-acid]",
    energy_required = 4,
    ingredients = { fluid("sulfuric-acid", 100), fluid("lava", 20) },
    results = { fluid("sulfuric-acid", 100, { temperature = HOT }) },
    allow_productivity = false
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
  alternate({
    name = "sae-molten-iron-from-lava-flux",
    icons = badged(vanilla(SA .. "icons/fluid/molten-iron-from-lava.png"), ICON.flux),
    categories = { "metallurgy" },
    subgroup = "vulcanus-processes",
    order = "z[sae-vf]-a[melting]-b[molten-iron-from-lava-flux]",
    energy_required = 16,
    ingredients = { fluid("lava", 500), solid("sae-obsidian-flux", 1) },
    results = { fluid("molten-iron", 300), solid("stone", 10) },
    allow_productivity = true
  }),

  ------------------------------------------------------------------ 3. fluxed steel
  -- A third less iron per steel; the glass carries the impurities away as slag.
  alternate({
    name = "sae-fluxed-steel",
    icons = badged(vanilla(SA .. "icons/casting-steel.png"), ICON.flux),
    categories = { "metallurgy" },
    subgroup = "vulcanus-processes",
    order = "z[sae-vf]-b[casting]-a[fluxed-steel]",
    energy_required = 6.4,
    ingredients =
    {
      -- The box holds what casting steel's does, give or take.
      fluid("molten-iron", 40, { fluidbox_multiplier = 8 }),
      solid("sae-obsidian-flux", 1)
    },
    results = { solid("steel-plate", 2), solid("sae-slag-aggregate", 1) },
    allow_productivity = true
  }),
  alternate({
    name = "sae-slag-concrete",
    icons = badged(vanilla(BASE .. "icons/concrete.png"), ICON.slag),
    categories = { "metallurgy" },
    subgroup = "vulcanus-processes",
    order = "z[sae-vf]-b[casting]-b[slag-concrete]",
    energy_required = 10,
    ingredients =
    {
      fluid("molten-iron", 20),
      fluid("water", 100),
      solid("sae-slag-aggregate", 5)
    },
    results = { solid("concrete", 10) },
    allow_productivity = true
  }),
  alternate({
    name = "sae-slag-brick",
    icons = badged(vanilla(BASE .. "icons/stone-brick.png"), ICON.slag),
    categories = { "smelting" },
    subgroup = "vulcanus-processes",
    order = "z[sae-vf]-b[casting]-c[slag-brick]",
    energy_required = 3.2,
    ingredients = { solid("sae-slag-aggregate", 2) },
    results = { solid("stone-brick", 1) },
    allow_productivity = true
  }),

  ------------------------------------------------------------------ 4. refined iron
  -- A fifth of the iron lost to slag. Its only use is the convergence.
  recipe({
    name = "sae-refined-molten-iron",
    categories = { "metallurgy" },
    subgroup = "vulcanus-processes",
    order = "z[sae-vf]-a[melting]-c[refined-molten-iron]",
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
  alternate({
    name = "sae-holmium-plate-from-oxide",
    icons = badged(vanilla(SA .. "icons/holmium-plate.png"), ICON.oxide),
    categories = { "metallurgy" },
    subgroup = "fulgora-processes",
    order = "z[sae-vf]-c[holmium-plate-from-oxide]",
    energy_required = 1,
    ingredients = { solid("sae-holmium-oxide", 1) },
    results = { solid("holmium-plate", 1) },
    allow_productivity = true
  }),

  ------------------------------------------------------------------ 7. oxide superconductor
  -- Vanilla's superconductor, cheaper (oxide for plate, no light oil) while
  -- the ozone lasts.
  alternate({
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
  }),

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
    energy_required = 10,
    ingredients = { solid("sae-superconducting-coil", 1), fluid("sae-molten-holmium-iron", 50) },
    results = { solid("sae-field-core", 1) },
    allow_productivity = false,
    auto_recycle = false
  }),

  ------------------------------------------------------------------ 10. the capstone
  -- Charging is time in the field and nothing else. Named for the item; the
  -- stub's recipe is `sae-magnetar-alloy-stub`, so the two never collide.
  recipe({
    name = "sae-magnetar-alloy",
    categories = { "sae-induction" },
    energy_required = 20,
    ingredients = { solid("sae-field-core", 1) },
    results = { solid("sae-magnetar-alloy", 1) },
    allow_productivity = false,
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
  return alternate(p)
end

data:extend({
  -- Hot acid leaches copper out of the rock.
  cast({
    name = "sae-induction-molten-copper",
    icons = badged(vanilla(SA .. "icons/fluid/molten-copper-from-lava.png"), ICON.hot_acid),
    order = "z[sae-vf]-c[induction]-a[molten-copper]",
    energy_required = 15,
    ingredients = { fluid("lava", 500), solid("calcite", 1), hot_acid(20) },
    results = { fluid("molten-copper", 275), solid("stone", 15) }
  }),
  -- Flux skims the cast clean.
  cast({
    name = "sae-induction-casting-iron",
    icons = badged(vanilla(SA .. "icons/casting-iron.png"), ICON.flux),
    order = "z[sae-vf]-c[induction]-b[casting-iron]",
    energy_required = 15,
    ingredients = { fluid("molten-iron", 100, { fluidbox_multiplier = 2 }), solid("sae-obsidian-flux", 1) },
    results = { solid("iron-plate", 11) }
  }),
  -- Acid pickles the oxide skin off.
  cast({
    name = "sae-induction-casting-copper",
    icons = badged(vanilla(SA .. "icons/casting-copper.png"), ICON.hot_acid),
    order = "z[sae-vf]-c[induction]-c[casting-copper]",
    energy_required = 15,
    ingredients = { fluid("molten-copper", 100, { fluidbox_multiplier = 2 }), hot_acid(10) },
    results = { solid("copper-plate", 11) }
  }),
  -- Crushed slag as mould sand.
  cast({
    name = "sae-induction-casting-iron-gear-wheel",
    icons = badged(vanilla(SA .. "icons/casting-iron-gear-wheel.png"), ICON.slag),
    order = "z[sae-vf]-c[induction]-d[casting-iron-gear-wheel]",
    energy_required = 10,
    ingredients = { fluid("molten-iron", 100, { fluidbox_multiplier = 1 }), solid("sae-slag-aggregate", 1) },
    results = { solid("iron-gear-wheel", 11) }
  }),
  -- Flux in the melt means fewer breaks in the draw.
  cast({
    name = "sae-induction-casting-copper-cable",
    icons = badged(vanilla(SA .. "icons/casting-copper-cable.png"), ICON.flux),
    order = "z[sae-vf]-c[induction]-e[casting-copper-cable]",
    energy_required = 14,
    ingredients = { fluid("molten-copper", 75, { fluidbox_multiplier = 1 }), solid("sae-obsidian-flux", 1) },
    results = { solid("copper-cable", 33) }
  })
})

--------------------------------------------------------------------------------
-- Technologies. Ten: the Vulcanus path on metallurgic science, the Fulgora path
-- on electromagnetic, the two shared steps on both, each with the packs those
-- need. Both openers require both planets' science packs, so the tree opens
-- only once both vanilla trees are done.
--
-- The three building recipes are not unlocked here yet: they arrive with the
-- buildings, into Ozone capture, Induction foundry and Magnetar alloy.
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
  return derive.placeholder_art({
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
  { "sae-vf-induction-foundry" }, BOTH, 1000, { "sae-magnetar-alloy" })
magnetar.essential = true

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
    {}),
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
      "sae-molten-holmium-iron", "sae-field-core",
      "sae-induction-molten-copper", "sae-induction-casting-iron", "sae-induction-casting-copper",
      "sae-induction-casting-iron-gear-wheel", "sae-induction-casting-copper-cable"
    }),
  magnetar
})
