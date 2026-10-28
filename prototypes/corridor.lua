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
-- material. The same rock once took a seed missile and became a crop instead;
-- that second harvest went with the cut back to the landing.

local derive = require("prototypes.derive")
local hit_effects = require("__base__.prototypes.entity.hit-effects")
local sounds = require("__base__.prototypes.entity.sounds")
local item_sounds = require("__base__.prototypes.item_sounds")
local item_tints = require("__base__.prototypes.item-tints")

--------------------------------------------------------------------------------
-- The radiant look, on the engine's asteroid shader.
--
-- An asteroid is not drawn from a sprite but lit by the engine: each variation
-- is a colour, a normal and a roughness map (whose RGB is the subsurface colour
-- the shader adds on the dark side), and the graphics set around them is the
-- shading data -- space-age/prototypes/entity/asteroid.lua. Our maps are drawn
-- in promethium's layout, size for size and variation for variation, so only
-- the three filenames of each variation change; the size, scale, shadow shift
-- and premultiplication the copy carries are vanilla's and stay.
--
-- The shading stays promethium's -- dark rock with its light inside it -- bar
-- the rim: promethium's second light is a red back light, and here it is the
-- radiant ramp's #1F63FF at 0.2.
--------------------------------------------------------------------------------

local RA = "__space-age-extended__/graphics/entity/radiant-asteroid/"
local RIM = { 0.024, 0.078, 0.2 }

local function radiant_look(set, size, count)
  assert(#set.variations == count,
         "radiant " .. size .. ": " .. count .. " maps drawn for " .. #set.variations .. " variations")
  for i, v in ipairs(set.variations) do
    local stem = RA .. size .. "/asteroid-radiant-" .. size .. "-"
    local n = string.format("-%02d.png", i)
    v.color_texture.filename = stem .. "colour" .. n
    v.normal_map.filename = stem .. "normal" .. n
    v.roughness_map.filename = stem .. "roughness" .. n
  end
  -- The rim is the second light, the one whose z is the key light's opposite
  -- (key -1, rim +0.95). Checked rather than trusted, since vanilla overrides
  -- this very light on two of its chunks.
  local rim = set.lights[2]
  assert(rim and rim.direction[3] > 0, "radiant " .. size .. ": the second light is not a rim light")
  rim.color = table.deepcopy(RIM)
end

--------------------------------------------------------------------------------
-- Chunks. A chunk needs BOTH an asteroid-chunk prototype and an item of the
-- same name: the first is the thing that floats, the second is what a collector
-- puts in its hold. Copying only the first gives a chunk with no item form.
--------------------------------------------------------------------------------

-- The floating form keeps vanilla's chunk graphics set (a chunk is a tumbling
-- set of lit maps, and vanilla's tumble) with our maps and rim in it;
-- everything that named the source goes.
-- A chunk is not an entity, so its description does not come from
-- [entity-description] by itself -- vanilla points each one at its asteroid's,
-- and these point at their own item's, so the two forms of the rock say the
-- same thing.
local radiant_chunk = derive.from("asteroid-chunk", "promethium-asteroid-chunk", "sae-radiant-chunk")
radiant_chunk.order = "z[sae]-a[radiant]"
radiant_chunk.icon = "__space-age-extended__/graphics/icons/radiant-chunk.png"
radiant_chunk.localised_description = { "item-description.sae-radiant-chunk" }
radiant_chunk.minable = { mining_time = 0.5, results = { { type = "item", name = "sae-radiant-chunk", amount = 1 } } }
radiant_look(radiant_chunk.graphics_set, "chunk", 6)

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

-- The rock keeps the small promethium asteroid's graphics set, with our maps
-- and rim in it. Its icon and its place in the menu it does not: until the far field has its own icon art,
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
radiant_look(radiant.graphics_set, "small", 7)
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
    fuel_categories = { "sae-radiant" },
    -- 500MJ against a uranium cell's 8GJ and a fusion cell's 40GJ. Deliberately
    -- modest: the chunk it comes from is free, so the fuel has to be consumed
    -- fast enough that the field must actually be worked rather than sipped.
    -- One cell is fifty seconds of a generator at full output.
    fuel_value = "500MJ",
    fuel_emissions_multiplier = 0,
    -- Burning a cell does not end it. What is left is the isotope's daughter,
    -- still in its casing, and the generator hands it back rather than
    -- destroying it -- see `burnt_inventory_size` below, and items.lua for the
    -- cell itself. Reprocessing it is a later stage's job; until that exists it
    -- accumulates, which is the point of carrying it at all.
    burnt_result = "sae-spent-cell"
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
-- The field set below follows the steam engine's: its resistances, impact
-- category, door sounds and alert shift. The rest is the building's own: a
-- 5x5 with the nuclear reactor's boxes (spec 2, Liam 2026-10-20: "5x5, reactor
-- boxes"), 600 health (Liam, 2026-10-27), the fusion generator's working sound
-- and performance curve (below), and its own wreck and explosion (further down).
local gen =
{
  type = "burner-generator",
  name = "sae-radiant-generator",
  icon = "__space-age-extended__/graphics/icons/radiant-generator.png",
  flags = { "placeable-neutral", "player-creation" },
  minable = { mining_time = 1, result = "sae-radiant-generator" },
  max_health = 600,
  alert_icon_shift = util.by_pixel(0, -12),
  resistances =
  {
    { type = "fire", percent = 70 },
    { type = "impact", percent = 30 }
  },
  collision_box = { { -2.2, -2.2 }, { 2.2, 2.2 } },
  selection_box = { { -2.5, -2.5 }, { 2.5, 2.5 } },
  damaged_trigger_effect = hit_effects.entity(),
  impact_category = "metal-large",
  open_sound = sounds.machine_open,
  close_sound = sounds.machine_close,
  -- Vanilla's fusion generator's hum, for now (Liam, 2026-10-27: "Vanilla
  -- sound for now", then "Fusion generator"); its own comes later. Its loop
  -- follows activity in speed and volume, and `perceived_performance` below is
  -- the fusion generator's too, so it slows and quietens with output as there.
  working_sound = table.deepcopy(data.raw["fusion-generator"]["fusion-generator"].working_sound),
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
    -- One slot for what the cell leaves behind. Without it the engine has
    -- nowhere to put the fuel's `burnt_result` and simply drops it, so this and
    -- that property only work as a pair. One is enough: an inserter empties the
    -- slot faster than fifty seconds of burn refills it.
    burnt_inventory_size = 1
  },
  -- Vacuum and the Core, and nowhere with an atmosphere to speak of.
  surface_conditions = { { property = "pressure", max = 9 } }
}

-- Art: rendered in Blender from concept/radiant-generator/model/
-- radiant_generator.py, the Carousel Foundry signed off by Liam on 2026-10-27
-- (T09: the T08 model with the T08k terminal box, its glows packed with T08h's
-- per-channel floor), through
--
--   BLENDER=<blender> tools/blender/render.sh \
--       concept/radiant-generator/model/radiant_generator.py <scratch> --ports --icon
--
-- then <scratch>/sheets/icon.png copied to graphics/icons/radiant-generator.png
-- and every other <scratch>/sheets/*.png into graphics/entity/radiant-generator/.
-- Every size, shift, frame count and line length below is copied from that
-- sheets/meta.json; none was measured off a sheet. Rendered at 2x, drawn at
-- scale 0.5.
--
-- **One picture for all four directions** (spec 5). There is no fluid box and
-- no facing port, so `animation` and `idle_animation` are each one Animation,
-- which an Animation4Way applies to every direction.
--
-- **Working, `animation`:** the plate, the nine moving layers over it (the
-- crane carries the well's lid, T08d), the lit glass in the four openings, the
-- isotope's light over that, the status lamps, the shadow, and four steady blue
-- lights for the dark. One crane cycle of 32 frames at 5/21 of a frame a tick,
-- 70 ms a frame, the signed-off GIF's pace (spec decision 10). That is the pace
-- at full output: `perceived_performance` slows it with output (decision 12).
--
-- **Idle, `idle_animation`** (Liam 2026-10-21: "Freeze where it stopped, glow
-- off"): the plate, the same nine moving layers and the shadow, and nothing
-- lit -- no glass, no light, no lamps, no blue lights. It has the working
-- loop's 32 frames, so the engine holds it on the frame the loop stopped on
-- (T08b): the machine stands where it stopped, dark. Unfuelled and fuelled with
-- no demand draw the same (T08b). The moving layers are already unlit, so idle
-- needs no sheets of its own (T08c).
local RG = "__space-age-extended__/graphics/entity/radiant-generator/"
local RG_FRAMES = 32
local RG_SPEED = 5 / 21

-- Each sheet: { width, height, shift } from sheets/meta.json, and the line
-- length of the animated ones; a sheet without one is a single frame.
local RG_SHEETS =
{
  ["base"]               = { 338, 361, { -0.04688, -0.21094 } },
  ["shadow"]             = { 358, 329, { 0.28125, 0.00781 } },
  ["status-lamp"]        = { 281, 170, { 0.17969, 0.21875 } },
  ["carousel"]           = { 271, 240, { -0.30469, -0.65625 }, 30 },
  ["drive"]              = { 105, 47, { -1.13281, -2.35156 }, 32 },
  ["crane"]              = { 213, 222, { 0.88281, -1.23438 }, 32 },
  ["commutator"]         = { 100, 130, { 1.35938, 1.46875 }, 32 },
  ["coupling-converter"] = { 47, 62, { 0.11719, 1.625 }, 32 },
  ["coupling-pump"]      = { 14, 25, { -0.34375, -2.30469 }, 32 },
  ["gauge-switchgear"]   = { 20, 15, { 2.125, 1.74219 }, 32 },
  ["gauge-converter"]    = { 6, 5, { -0.51562, 2.07031 }, 32 },
  ["gauge-transformer"]  = { 33, 46, { -1.97656, 2.0 }, 32 },
  ["window"]             = { 227, 148, { 0.61719, -0.82812 }, 32 },
  ["window-glow"]        = { 260, 238, { 0.625, -0.875 }, 31 },
  ["remnants"]           = { 306, 297, { 0.14062, 0.02344 } },
  ["remnants-glow"]      = { 15, 15, { 1.07031, -0.50781 } }
}

-- The moving layers, in the order the model draws them: the crane over the
-- table it shadows.
local RG_MOVING = { "carousel", "drive", "crane", "commutator", "coupling-converter", "coupling-pump",
                    "gauge-switchgear", "gauge-converter", "gauge-transformer" }

-- One layer of the 32-frame loop: an animated sheet plays it, a single frame
-- is repeated to its length, as the engine requires of every layer.
local function rg_layer(name, extra)
  local s = RG_SHEETS[name]
  local layer =
  {
    filename = RG .. name .. ".png",
    priority = "high",
    width = s[1], height = s[2],
    shift = s[3],
    animation_speed = RG_SPEED,
    scale = 0.5
  }
  if s[4] then
    layer.frame_count = RG_FRAMES
    layer.line_length = s[4]
  else
    layer.frame_count = 1
    layer.repeat_count = RG_FRAMES
  end
  for k, v in pairs(extra or {}) do layer[k] = v end
  return layer
end

-- The status lamps, cut white. A burner generator has no status colours and no
-- working visualisations to tint them with (BurnerGeneratorPrototype draws
-- `animation` and `idle_animation`, nothing else), so the tint is set here: the
-- working green the review sheets drew (vanilla's electric mining drill's), in
-- `animation` only, so the lamps are dark at idle (T08c's idle, signed off).
local RG_LAMP_GREEN = { 0, 1, 0, 1 }

-- The four steady blue lights at the openings (Liam 2026-10-21, Q11 "Add
-- steady blue lights"; T08c's places, sizes and strengths, "Accept"), as
-- meta.json's `lights` declares them: the game's own light-medium.png drawn
-- into the light map, so each shows in the dark and never on the ground by
-- day. In `animation` only (T08c: "four draw_as_light layers in animation
-- only"). Each: its shift, its scale (its size in tiles x 32 / 300 px), and its
-- tint (the model's light colour x its strength).
local RG_LIGHTS =
{
  { { -1.05, -0.05 }, 0.21333, { 0.145, 0.265, 0.5 } },     -- the collector head's bullseye port
  { { 1.25, -1.02 }, 0.26667, { 0.1305, 0.2385, 0.45 } },   -- the well's mouth
  { { 1.25, -1.7 }, 0.37333, { 0.174, 0.318, 0.6 } },       -- the plate-rack slot
  { { 2.25, -0.6 }, 0.42667, { 0.145, 0.265, 0.5 } }        -- the thermionic tubes
}

-- The machine stopped: the plate, the moving parts on the frame the loop is
-- on, and the shadow. Both looks start from it.
local function rg_machine()
  local layers = { rg_layer("base") }
  for _, name in ipairs(RG_MOVING) do layers[#layers + 1] = rg_layer(name) end
  return layers
end

local rg_working = rg_machine()
rg_working[#rg_working + 1] = rg_layer("window")
rg_working[#rg_working + 1] = rg_layer("window-glow", { draw_as_glow = true, blend_mode = "additive" })
rg_working[#rg_working + 1] = rg_layer("status-lamp", { draw_as_glow = true, tint = RG_LAMP_GREEN })
rg_working[#rg_working + 1] = rg_layer("shadow", { draw_as_shadow = true })
for _, light in ipairs(RG_LIGHTS) do
  rg_working[#rg_working + 1] =
  {
    filename = "__core__/graphics/light-medium.png",
    priority = "extra-high",
    width = 300, height = 300,
    frame_count = 1,
    repeat_count = RG_FRAMES,
    animation_speed = RG_SPEED,
    draw_as_light = true,
    shift = light[1],
    scale = light[2],
    tint = light[3]
  }
end

local rg_idle = rg_machine()
rg_idle[#rg_idle + 1] = rg_layer("shadow", { draw_as_shadow = true })

gen.animation = { layers = rg_working }
gen.idle_animation = { layers = rg_idle }

-- **Its wreck** (spec decision 6, "Own wreck, like turbine"): the model's
-- remnants pass, one picture for every direction as the building has, its
-- shadow baked in as vanilla's is. Over it the well's dying blue (Liam
-- 2026-10-21: "Faint dying blue", then "Make it glow at night", "Keep 0.4"), a
-- glow layer, so the corpse shows it in the dark. Everything else is vanilla's
-- 5x5 nuclear-reactor-remnants (base/prototypes/entity/remnants.lua): fifteen
-- minutes on the ground, left in place under a tile. Named as vanilla names
-- its own, "<the building> (remnant)", from core's locale.
local rg_remnants =
{
  type = "corpse",
  name = "sae-radiant-generator-remnants",
  localised_name = { "remnant-name", { "entity-name.sae-radiant-generator" } },
  icon = "__space-age-extended__/graphics/icons/radiant-generator.png",
  icon_size = 64,
  flags = { "placeable-neutral", "not-on-map" },
  hidden_in_factoriopedia = true,
  subgroup = "energy-remnants",
  order = "a-e-a-z[sae-radiant-generator]",
  selection_box = { { -2.5, -2.5 }, { 2.5, 2.5 } },
  tile_width = 5,
  tile_height = 5,
  selectable_in_game = false,
  time_before_removed = 60 * 60 * 15, -- 15 minutes
  expires = false,
  final_render_layer = "remnants",
  remove_on_tile_placement = false,
  animation =
  {
    layers =
    {
      {
        filename = RG .. "remnants.png",
        line_length = 1,
        width = RG_SHEETS["remnants"][1],
        height = RG_SHEETS["remnants"][2],
        direction_count = 1,
        shift = RG_SHEETS["remnants"][3],
        scale = 0.5
      },
      {
        filename = RG .. "remnants-glow.png",
        line_length = 1,
        width = RG_SHEETS["remnants-glow"][1],
        height = RG_SHEETS["remnants-glow"][2],
        direction_count = 1,
        shift = RG_SHEETS["remnants-glow"][3],
        draw_as_glow = true,
        blend_mode = "additive",
        scale = 0.5
      }
    }
  }
}

-- **How it goes: fireball and sparks, no smoke** (spec decision 6, as the
-- Siderane turbine's; crust-tap.lua has the reasoning and Liam's words). Its
-- vanilla counterpart's explosion -- the 5x5 nuclear reactor's, whose boxes it
-- has: its sound and its shower of metal, glass, cable and machine parts --
-- with every wisp of smoke taken out, the turbine's fireball, and sparks.
--
--   * **No smoke.** The explosion's own puffs go, and any debris that trails
--     smoke as it flies flies as a copy of ours with the trail struck off
--     (`derive.smokeless_explosion`).
--   * **The fireball is the turbine's**, vanilla's medium explosion: the Core
--     has a thin atmosphere wherever its pressure is above 0, so a flash of
--     fire is fair where smoke is not. Not the reactor's own: vanilla's massive
--     explosion (and the big one) burns out into a black cloud drawn into the
--     fireball itself, which no field strikes. Measured on the sheets (opaque
--     px under 70 in every channel against px with red over 150, at the peak
--     frame of each): massive 2.38 dark to fire, big 1.20, medium 0.31-0.46;
--     and in game (T11) the massive one covered the 5x5 in black from about
--     the 28th tick.
--   * **Sparks**: the construction robot's repair sparks as a small explosion
--     of their own the big one sets off where it stands, and vanilla's hit
--     sparks (what a bullet strikes off metal) thrown over the 5x5 with the
--     debris.
-- Vanilla's hit sparks, thrown from about head height over the 5x5. An
-- explosion's offsets do not turn with the building; here they need not.
local function spark_burst(particle_name, count)
  return
  {
    type = "create-particle",
    repeat_count = count,
    particle_name = particle_name,
    offset_deviation = { { -2, -2 }, { 2, 2 } },
    initial_height = 1,
    initial_height_deviation = 0.5,
    initial_vertical_speed = 0.04,
    initial_vertical_speed_deviation = 0.04,
    speed_from_center = 0.03,
    speed_from_center_deviation = 0.03,
    frame_speed = 0.5
  }
end

-- The robot's sparks, as an explosion of their own: drawn once where it is set
-- off, silent, and with nothing else in it.
local robot_sparks = data.raw["construction-robot"]["construction-robot"].sparks
assert(robot_sparks, "construction-robot/construction-robot has no sparks")
local rg_sparks =
{
  type = "explosion",
  name = "sae-radiant-generator-sparks",
  icon = "__space-age-extended__/graphics/icons/radiant-generator.png",
  icon_size = 64,
  flags = { "not-on-map" },
  hidden = true,
  subgroup = "energy-explosions",
  order = "a-d-a-z[sae-radiant-generator]-b[sparks]",
  height = 0,
  animations = table.deepcopy(robot_sparks)
}

local rg_explosion = table.deepcopy(data.raw.explosion["nuclear-reactor-explosion"])
assert(rg_explosion, "explosion/nuclear-reactor-explosion does not exist")
rg_explosion.name = "sae-radiant-generator-explosion"
rg_explosion.icon = "__space-age-extended__/graphics/icons/radiant-generator.png"
rg_explosion.icon_size = 64
rg_explosion.order = "a-d-a-z[sae-radiant-generator]"
rg_explosion.localised_name = { "dying-explosion-name", { "entity-name.sae-radiant-generator" } }
local turbine_fireball = data.raw.explosion["steam-turbine-explosion"]
assert(turbine_fireball, "explosion/steam-turbine-explosion does not exist")
rg_explosion.animations = table.deepcopy(turbine_fireball.animations)
derive.smokeless_explosion(rg_explosion, function(name) return "sae-radiant-generator-" .. name end)
for _, trigger in ipairs(derive.each(rg_explosion.created_effect)) do
  for _, delivery in ipairs(derive.each(trigger.action_delivery)) do
    if delivery.type == "instant" then
      delivery.target_effects = delivery.target_effects or {}
      table.insert(delivery.target_effects, spark_burst("spark-particle", 60))
      table.insert(delivery.target_effects, spark_burst("spark-particle-debris", 30))
      table.insert(delivery.target_effects, { type = "create-explosion", entity_name = rg_sparks.name })
    end
  end
end

gen.corpse = rg_remnants.name
gen.dying_explosion = rg_explosion.name
data:extend({ gen, rg_remnants, rg_sparks, rg_explosion })

-- The pool's solution, precipitated. Crust gas is the reagent: an offshore pump
-- on the shore draws the solution, a Gas Pump on a siderane vent the gas. The
-- fuel costs the planet nothing it rations.
--
-- Helium-3 used to be the reagent and the governor, which put the power line in
-- the queue behind the Vent Pump for the gas the Core is meanest with -- so the
-- one thing a player has to have before anything else works was gated on the
-- one thing the Core hands out last.
--
-- It runs in the Reaction Plant and nowhere else (machines.lua): the recipe's
-- category is private, so no vanilla chemical plant will take this job.
data:extend({
  {
    type = "recipe",
    name = "sae-radiant-precipitation",
    categories = { "sae-reaction" },
    energy_required = 20,
    ingredients =
    {
      { type = "fluid", name = "sae-radiant-solution", amount = 100 },
      { type = "fluid", name = "sae-crust-gas", amount = 100 }
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
