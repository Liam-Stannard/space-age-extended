-- The corridor: the route past the Shattered Planet, and the one thing that
-- grows out there.
--
-- Vanilla's far field is barren by design -- the useful chunks stop and
-- promethium replaces them, and promethium has no crushing recipe at all. This
-- mod adds exactly one asteroid type and leaves the barrenness intact. Carbon,
-- ice and ore remain freight from the inner system, which is what keeps the
-- corridor carrying something every hour of the endgame.
--
-- One rock, one harvest: shoot it and crush what it drops for the power
-- material. On master the same rock takes a seed missile and becomes a crop
-- instead; that second harvest is not on this branch.

local derive = require("prototypes.derive")
local hit_effects = require("__base__.prototypes.entity.hit-effects")
local sounds = require("__base__.prototypes.entity.sounds")
local item_sounds = require("__base__.prototypes.item_sounds")
local item_tints = require("__base__.prototypes.item-tints")

--------------------------------------------------------------------------------
-- Chunks. A chunk needs BOTH an asteroid-chunk prototype and an item of the
-- same name: the first is the thing that floats, the second is what a collector
-- puts in its hold. Copying only the first gives a chunk with no item form.
--------------------------------------------------------------------------------

-- The floating form keeps vanilla's chunk graphics (a chunk is a tumbling
-- sprite set, and vanilla's tumble); everything that named the source goes.
-- A chunk is not an entity, so its description does not come from
-- [entity-description] by itself -- vanilla points each one at its asteroid's,
-- and these point at their own item's, so the two forms of the rock say the
-- same thing.
local radiant_chunk = derive.from("asteroid-chunk", "promethium-asteroid-chunk", "sae-radiant-chunk")
radiant_chunk.order = "z[sae]-a[radiant]"
radiant_chunk.icon = "__space-age-extended__/graphics/icons/radiant-chunk.png"
radiant_chunk.localised_description = { "item-description.sae-radiant-chunk" }
radiant_chunk.minable = { mining_time = 0.5, results = { { type = "item", name = "sae-radiant-chunk", amount = 1 } } }

-- The held form, on vanilla's chunk-item pattern: one to a stack, a hundred
-- kilos, and the sounds of a sack of rock.
local function chunk_item(name, icon, order, tint)
  return
  {
    type = "item",
    name = name,
    icon = icon,
    subgroup = "space-material",
    order = order,
    inventory_move_sound = item_sounds.sulfur_inventory_move,
    pick_sound = item_sounds.resource_inventory_pickup,
    drop_sound = item_sounds.sulfur_inventory_move,
    stack_size = 1,
    weight = 100 * kg,
    random_tint_color = tint
  }
end

data:extend({
  radiant_chunk,
  chunk_item("sae-radiant-chunk", "__space-age-extended__/graphics/icons/radiant-chunk.png",
             "z[sae]-a[radiant]", item_tints.ice_blue)
})

--------------------------------------------------------------------------------
-- The asteroids themselves.
--------------------------------------------------------------------------------

-- The rock keeps the small promethium asteroid's graphics set. Its icon and
-- its place in the menu they do not: until the far field has its own icon art,
-- each asteroid shows the icon of the chunk it breaks into.
--
-- The preview on an asteroid's Factoriopedia page is a script naming the rock
-- it launches, so `derive.from` drops the inherited one; each page gets the
-- vanilla preview back with its own rock's name in it.
local SMALL = data.raw.asteroid["small-promethium-asteroid"]
local function own_preview(rock)
  rock.factoriopedia_simulation = table.deepcopy(SMALL.factoriopedia_simulation)
  rock.factoriopedia_simulation.init =
    rock.factoriopedia_simulation.init:gsub(
      'name="small%-promethium%-asteroid"', 'name="' .. rock.name .. '"')
end

local radiant = derive.from("asteroid", "small-promethium-asteroid", "sae-radiant-asteroid")
radiant.icon = "__space-age-extended__/graphics/icons/radiant-chunk.png"
radiant.order = "z[sae]-a[radiant]"
-- Terminal on purpose: destroyed by ordinary fire it leaves nothing behind.
radiant.dying_trigger_effect =
{
  { type = "create-explosion", entity_name = "promethium-asteroid-explosion-2", only_when_visible = true }
}
own_preview(radiant)
data:extend({ radiant })

data:extend({
  -- What the rock is worth.
  {
    type = "recipe",
    name = "sae-radiant-crushing",
    categories = { "crushing" },
    energy_required = 3,
    ingredients = { { type = "item", name = "sae-radiant-chunk", amount = 1 } },
    results =
    {
      { type = "item", name = "sae-radiant-fuel", amount = 2 },
      { type = "item", name = "sae-radiant-chunk", amount = 1, independent_probability = 0.2, ignored_by_stats = 1 }
    },
    icons =
    {
      { icon = "__space-age-extended__/graphics/icons/radiant-chunk.png" },
      { icon = "__space-age-extended__/graphics/icons/radiant-fuel.png", scale = 0.25, shift = { 8, 8 } }
    },
    allow_productivity = true,
    enabled = false
  },
  -- The corridor's power. Solar is nil out here, nothing burns, and vanilla's
  -- answer does not travel: a fusion cell needs 100 ammonia, which has no
  -- barrel, so cells can only be made on Aquilo and freighted the whole way.
  -- This is made where it is consumed, from the one thing the far field has.
  {
    type = "item",
    name = "sae-radiant-fuel",
    icon = "__space-age-extended__/graphics/icons/radiant-fuel.png",
    subgroup = "intermediate-product",
    order = "z[sae]-c[radiant-fuel]",
    inventory_move_sound = item_sounds.fuel_cell_inventory_move,
    pick_sound = item_sounds.fuel_cell_inventory_pickup,
    drop_sound = item_sounds.fuel_cell_inventory_move,
    stack_size = 50,
    weight = 2 * kg,
    fuel_category = "sae-radiant",
    -- 500MJ against a uranium cell's 8GJ and a fusion cell's 40GJ. Deliberately
    -- modest: the chunk it comes from is free, so the fuel has to be consumed
    -- fast enough that the field must actually be worked rather than sipped.
    -- One cell is fifty seconds of a generator at full output.
    fuel_value = "500MJ",
    fuel_emissions_multiplier = 0
  },
  {
    type = "fuel-category",
    name = "sae-radiant"
  }
})

--------------------------------------------------------------------------------
-- What burns it.
--
-- Nothing else will: the fuel has its own category, so a radiant cell cannot be
-- shovelled into anything that already exists, and this generator will take
-- nothing else. It works in vacuum and on the Core, which is the whole point --
-- it is the one power source that is made where it is spent.
--------------------------------------------------------------------------------

-- Written out rather than copied. Vanilla's only `burner-generator` is a
-- hidden developer entity with half a machine's fields -- no impact category,
-- no hit effect, no door sounds -- so the copy needed `hidden = false` to be
-- seen and still fell short of what every visible vanilla machine carries.
-- The field set below is the steam engine's, the same 3x5 footprint, which is
-- also why its remnants fit.
local gen =
{
  type = "burner-generator",
  name = "sae-radiant-generator",
  icon = "__space-age-extended__/graphics/icons/radiant-generator.png",
  flags = { "placeable-neutral", "player-creation" },
  minable = { mining_time = 1, result = "sae-radiant-generator" },
  max_health = 400,
  corpse = "steam-engine-remnants",
  dying_explosion = "medium-explosion",
  alert_icon_shift = util.by_pixel(0, -12),
  resistances =
  {
    { type = "fire", percent = 70 },
    { type = "impact", percent = 30 }
  },
  collision_box = { { -1.35, -2.35 }, { 1.35, 2.35 } },
  selection_box = { { -1.5, -2.5 }, { 1.5, 2.5 } },
  damaged_trigger_effect = hit_effects.entity(),
  impact_category = "metal-large",
  open_sound = sounds.machine_open,
  close_sound = sounds.machine_close,
  working_sound = table.deepcopy(data.raw.generator["steam-engine"].working_sound),
  perceived_performance = { minimum = 0.25, performance_to_activity_rate = 2.0 },
  heating_energy = "50kW",
  max_power_output = "10MW",
  energy_source = { type = "electric", usage_priority = "primary-output" },
  burner =
  {
    type = "burner",
    fuel_categories = { "sae-radiant" },
    effectivity = 1,
    fuel_inventory_size = 2,
    burnt_inventory_size = 0
  },
  -- Vacuum and the Core, and nowhere with an atmosphere to speak of.
  surface_conditions = { { property = "pressure", max = 9 } }
}

-- Art. Two plates, because `burner-generator` maps north/south onto one
-- animation and east/west onto the other -- see
-- concept/radiant-generator/building-spec-radiant-generator.md sections 5 and 13. They are the
-- same machine rotated on the ground, drawn twice rather than rotated in
-- software: the camera looks down at an angle, so turning the building shows
-- different faces of it.
--
-- The load-bearing numbers, measured off the cut plates rather than guessed:
-- north/south is 192 px (3.000 tiles) wide, east/west is 320 px (5.000 tiles)
-- wide. Section 13 is blunt about why -- get these wrong and a row of
-- generators will not tile.
--
-- The glow is not a second render. Each plate was generated with the throat
-- already lit and then split by hue with tools/split-glow.py: the green-white
-- slots come out as the additive layer and the base keeps a dark recess where
-- each slot was. One generation per direction instead of two, and the two
-- layers register by construction because they are cut from one image.
local RG = "__space-age-extended__/graphics/entity/radiant-generator/"
local function rg_layers(dir, w, h, sw, sh, shift, sshift)
  return
  {
    layers =
    {
      {
        filename = RG .. "base-" .. dir .. ".png",
        priority = "high",
        width = w, height = h, shift = shift, scale = 0.5
      },
      {
        filename = RG .. "base-" .. dir .. "-shadow.png",
        priority = "high", draw_as_shadow = true,
        width = sw, height = sh, shift = sshift, scale = 0.5
      },
      {
        filename = RG .. "glow-" .. dir .. ".png",
        priority = "high",
        blend_mode = "additive", draw_as_glow = true,
        width = w, height = h, shift = shift, scale = 0.5
      }
    }
  }
end

local rg_vertical = rg_layers("vertical", 224, 414, 541, 414,
                              { 0, 0 }, { 1.23828, 0 })
local rg_horizontal = rg_layers("horizontal", 352, 233, 526, 233,
                                { 0, 0 }, { 1.35938, 0 })
gen.animation =
{
  north = rg_vertical,
  south = table.deepcopy(rg_vertical),
  east = rg_horizontal,
  west = table.deepcopy(rg_horizontal)
}
data:extend({ gen })

-- The pool's solution, precipitated. Helium-3 is the reagent, and it is the
-- governor: a tap on the shore gives solution faster than any use of it, so the
-- fuel is priced in the rare gas the Core throttles everything else with.
data:extend({
  {
    type = "recipe",
    name = "sae-radiant-precipitation",
    categories = { "chemistry" },
    energy_required = 20,
    ingredients =
    {
      { type = "fluid", name = "sae-radiant-solution", amount = 100 },
      { type = "fluid", name = "sae-helium-3", amount = 20 }
    },
    results = { { type = "item", name = "sae-radiant-fuel", amount = 1 } },
    icon = "__space-age-extended__/graphics/icons/radiant-fuel.png",
    icon_size = 64,
    surface_conditions = { { property = "pressure", min = 1, max = 9 } },
    enabled = false
  }
})

data:extend({
  {
    type = "item",
    name = "sae-radiant-generator",
    icon = "__space-age-extended__/graphics/icons/radiant-generator.png",
    subgroup = "energy",
    order = "z[sae]-b[radiant-generator]",
    place_result = "sae-radiant-generator",
    inventory_move_sound = item_sounds.mechanical_large_inventory_move,
    pick_sound = item_sounds.mechanical_large_inventory_pickup,
    drop_sound = item_sounds.mechanical_large_inventory_move,
    stack_size = 10,
    weight = 40 * kg
  },
  {
    type = "recipe",
    name = "sae-radiant-generator",
    categories = { "crafting" },
    energy_required = 20,
    ingredients =
    {
      { type = "item", name = "processing-unit", amount = 20 },
      { type = "item", name = "low-density-structure", amount = 20 },
      { type = "item", name = "steel-plate", amount = 40 }
    },
    results = { { type = "item", name = "sae-radiant-generator", amount = 1 } },
    enabled = false
  }
})

--------------------------------------------------------------------------------
-- Where it spawns: on the connection the mod adds, and nowhere else. The far
-- field stays as barren as vanilla left it.
--------------------------------------------------------------------------------

local spawn =
{
  {
    asteroid = "sae-radiant-asteroid",
    spawn_points =
    {
      { distance = 0.0, probability = 0.00, speed = 0.05, angle_when_stopped = 0.4 },
      { distance = 0.2, probability = 0.02, speed = 0.05, angle_when_stopped = 0.4 },
      { distance = 1.0, probability = 0.06, speed = 0.05, angle_when_stopped = 0.4 }
    }
  }
}

local connection = data.raw["space-connection"]["sae-shattered-planet-core"]
local defs = connection.asteroid_spawn_definitions or {}
for _, d in pairs(spawn) do table.insert(defs, d) end
connection.asteroid_spawn_definitions = defs
