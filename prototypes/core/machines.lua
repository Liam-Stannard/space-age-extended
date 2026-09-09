-- The nine machines of the Core's own production line.
--
-- Each has a master spec under graphics/, and every number below is read off it
-- rather than invented here; where this file and a spec disagree, the spec is
-- right and this is a bug. Section 2 of each spec is the source.
--
-- **The art is a stand-in and says so.** None of the nine has a plate yet. Each
-- borrows the sprites of a vanilla machine of the same footprint, marked by a
-- `derive.placeholder_art` call so `grep` finds every one of them, and logged at
-- data stage so the log does too. That is a different thing from an inherited
-- leftover -- see prototypes/derive.lua, which strips those up front.
--
-- Three of the nine are shaped by measurements that cost a spike each, and the
-- shapes are not obvious:
--
--   * The Vacuum Furnace is a `furnace`, not an assembling machine, and its flux
--     box is deliberately large. S12 measured that a furnace with a fluid
--     ingredient refuses its *solid* ingredient until the fluid is already in
--     the machine; a big buffer against a small draw makes that latch rare.
--   * The Crust Tap is an `offshore-pump`, which draws its fluid from the *tile*
--     beneath it and not from its own filter. S10 measured one built on bare
--     ground reporting `working` and producing nothing. It is sited on a vent
--     tile, and the tile is what carries the fluid.
--   * The Ring Mast holds no charge at all. Its product spoils in seconds with
--     no spoil result, which is how a building is made to matter *near* another
--     one -- nothing in the engine can express that directly.

local derive = require("prototypes.derive")

--------------------------------------------------------------------------------
-- Crafting categories.
--
-- Every one of these is private on purpose. A category the Core shares with
-- vanilla is a recipe a vanilla machine can run, and for several of these
-- buildings the whole argument is that the vanilla machine *cannot* -- the space
-- crusher must never run the Drop Crusher's recipe, and nothing but the Vacuum
-- Furnace may sinter.
--------------------------------------------------------------------------------

data:extend({
  { type = "recipe-category", name = "sae-crushing" },
  { type = "recipe-category", name = "sae-classification" },
  { type = "recipe-category", name = "sae-separation" },
  { type = "recipe-category", name = "sae-fibre" },
  { type = "recipe-category", name = "sae-degassing" },
  { type = "recipe-category", name = "sae-sintering" },
  { type = "recipe-category", name = "sae-ignition-charge" }
})

--------------------------------------------------------------------------------
-- Surface conditions, named once.
--
-- Two distinct locks, and the difference is the design rather than a detail.
-- `HIGH_G` is the Core's surface alone: the three gravity machines cannot be
-- carried anywhere else, because gravity is the thing doing their work. `CORE`
-- is the Core and space platforms, for machines whose argument is the absence of
-- atmosphere rather than the presence of weight.
--------------------------------------------------------------------------------

local HIGH_G = { { property = "gravity", min = 45 } }
local CORE = { { property = "pressure", max = 9 } }
local CORE_ONLY = { { property = "pressure", min = 1, max = 9 } }

local BOX_3x3 = { { -1.4, -1.4 }, { 1.4, 1.4 } }
local SEL_3x3 = { { -1.5, -1.5 }, { 1.5, 1.5 } }

--- A 3x3 crafting machine, since six of the nine are exactly that.
local function crafter(name, from, opts)
  local p = derive.from("assembling-machine", from, name)
  derive.placeholder_art(p, "wears " .. from .. "'s sprites until its plate exists")
  p.icon = data.raw["assembling-machine"][from].icon
  p.icons = nil
  p.minable = { mining_time = 0.5, result = name }
  p.collision_box = BOX_3x3
  p.selection_box = SEL_3x3
  p.crafting_categories = opts.categories
  p.crafting_speed = opts.speed or 1
  p.energy_usage = opts.energy
  p.energy_source = { type = "electric", usage_priority = "secondary-input" }
  p.module_slots = opts.modules
  p.surface_conditions = opts.conditions
  p.fluid_boxes = opts.fluid_boxes
  p.fluid_boxes_off_when_no_fluid_recipe = opts.fluid_boxes ~= nil
  return p
end

--------------------------------------------------------------------------------
-- N1. Drop Crusher -- graphics/building-spec-drop-crusher.md
--
-- Breaks ore by dropping a weight on it, so it works only where there is weight
-- to drop. Vanilla's crusher spins and is locked to zero g; this one drops and
-- is locked to high g. Neither can be built where the other belongs, and neither
-- can run the other's recipes, which is what a Core variant should mean.
--------------------------------------------------------------------------------

local crusher = crafter("sae-drop-crusher", "assembling-machine-3", {
  categories = { "sae-crushing" },
  energy = "200kW",          -- the fall is free; the lift is not
  modules = 2,
  conditions = HIGH_G
})
data:extend({ crusher })

--------------------------------------------------------------------------------
-- N2. Ballast Drill -- graphics/building-spec-ballast-drill.md
--
-- `resource_drain_rate_percent` is the whole building. It is the one mining-drill
-- field that changes what a patch is *worth* rather than how fast it empties,
-- and vanilla uses it exactly once, on the big mining drill. Here it turns ore
-- siting into a decision with a cost, on the one planet where ore is finite by
-- design. At 50 g the drill presses with its own mass instead of hammering,
-- which is both the fiction and the reason it cannot be carried to a world where
-- ore is effectively infinite and used as a straight upgrade.
--------------------------------------------------------------------------------

local drill = derive.from("mining-drill", "big-mining-drill", "sae-ballast-drill")
derive.placeholder_art(drill, "wears big-mining-drill's sprites until its plate exists")
drill.icon = data.raw["mining-drill"]["big-mining-drill"].icon
drill.icons = nil
drill.minable = { mining_time = 0.5, result = "sae-ballast-drill" }
drill.resource_categories = { "basic-solid" }
drill.resource_drain_rate_percent = 50
drill.mining_speed = 1.3                  -- ~0.65 of the electric drill's, per ore
drill.energy_usage = "900kW"
drill.energy_source = { type = "electric", usage_priority = "secondary-input" }
drill.module_slots = 4
drill.surface_conditions = HIGH_G
data:extend({ drill })

--------------------------------------------------------------------------------
-- N3. Dross Classifier -- graphics/building-spec-dross-classifier.md
--
-- Sorts settling dross by particle size. Shares the Drop Crusher's and the
-- Ballast Drill's argument -- gravity doing mechanical work -- applied to
-- separation rather than to breaking or extraction, so the three read as a
-- family leaning on one planetary fact. Nothing in vanilla sorts a solid by
-- density.
--------------------------------------------------------------------------------

local classifier = crafter("sae-dross-classifier", "assembling-machine-3", {
  categories = { "sae-classification" },
  energy = "150kW",          -- the sort is gravity; the shake is not
  modules = 2,
  conditions = HIGH_G
})

-- Art: the Shaker Deck, option A of five (graphics/dross-classifier-options/).
--
-- The plate replaces assembling-machine-3's entirely, so the placeholder call is
-- gone with it and this machine no longer logs at data stage. Two layers, both
-- cut by tools/process-building-art.py from one approved render: 192 px of drawn
-- machine, **3.000 tiles**, centred to 0.0 px, with alpha zero on all four
-- canvas edges. The 4 px rim a side is the difference between a plate with an
-- antialiased edge and one that ends on a razor line.
--
-- There is no working visualisation and no glow. The machine's whole read is
-- that it shakes, and vibration is carried by the springs and the eccentric
-- drive being *drawn*, not by anything animating: dross is what settled out and
-- is cold by the time it arrives, so nothing here is lit.
local DC = "__space-age-extended__/graphics/entity/dross-classifier/"
classifier.icon = "__space-age-extended__/graphics/icons/dross-classifier.png"
classifier.graphics_set =
{
  animation =
  {
    layers =
    {
      {
        filename = DC .. "base.png",
        priority = "high",
        width = 200, height = 189,
        shift = { 0, 0 },
        scale = 0.5
      },
      {
        filename = DC .. "base-shadow.png",
        priority = "high",
        draw_as_shadow = true,
        -- Leans up and to the right, so it is wider than the colour plate and
        -- carries its own shift. Both numbers come out of the tool rather than
        -- being chosen; the y offset is the room the blur needs below the foot.
        width = 345, height = 200,
        shift = { 1.13281, 0.08594 },
        scale = 0.5
      }
    }
  }
}
data:extend({ classifier })

--------------------------------------------------------------------------------
-- N4. Coil Separator -- graphics/building-spec-coil-separator.md
--
-- Magnetic beneficiation on a world with no magnetic field, which is why it is
-- so expensive to run: the field has to be generated rather than borrowed. Its
-- own build recipe costs a coil assembly, two stages below the Field Coil
-- Segment -- the player spends endgame material to make more endgame material,
-- which is the production tree's "using the thing you are building to build more
-- of it" made literal.
--------------------------------------------------------------------------------

data:extend({ crafter("sae-coil-separator", "electromagnetic-plant", {
  categories = { "sae-separation" },
  energy = "2500kW",         -- generating a field from nothing is the cost
  modules = 3,
  conditions = CORE
}) })

--------------------------------------------------------------------------------
-- N5. Whisker Comber -- graphics/building-spec-whisker-comber.md
--
-- Splits one harvest into a quality-graded pair, both with real consumers: tow
-- for the composite line, felt for the cryostat. Combing is four times slower per
-- whisker than matting, so neither is the correct answer and the ratio is a
-- standing decision rather than a solved one.
--------------------------------------------------------------------------------

data:extend({ crafter("sae-whisker-comber", "assembling-machine-3", {
  categories = { "sae-fibre" },
  energy = "400kW",
  modules = 3,
  conditions = CORE
}) })

--------------------------------------------------------------------------------
-- N6. Helium Concentrator -- graphics/building-spec-helium-concentrator.md
--
-- A relief valve on a hard cap, and priced like one: worse than gravity settling
-- at making melt *and* far worse than a gas vent at making helium. It is the bad
-- trade taken when one of the two is what has run out. Three fluid boxes -- one
-- in, two out -- which is why it is built fresh rather than copied from any
-- vanilla machine.
--------------------------------------------------------------------------------

data:extend({ crafter("sae-helium-concentrator", "chemical-plant", {
  categories = { "sae-degassing" },
  energy = "1500kW",
  modules = 3,
  conditions = CORE,
  fluid_boxes =
  {
    {
      production_type = "input",
      volume = 1000,
      pipe_connections = { { flow_direction = "input", direction = defines.direction.south, position = { 0, 1 } } }
    },
    {
      production_type = "output",
      volume = 1000,
      pipe_connections = { { flow_direction = "output", direction = defines.direction.north, position = { -1, -1 } } }
    },
    {
      production_type = "output",
      volume = 1000,
      pipe_connections = { { flow_direction = "output", direction = defines.direction.north, position = { 1, -1 } } }
    }
  }
}) })

--------------------------------------------------------------------------------
-- N7. Vacuum Furnace -- graphics/building-spec-vacuum-furnace.md
--
-- A `furnace`, not an assembling machine, so it picks its own recipe from what
-- it is fed -- which is what makes a smelter a smelter. It does the two things
-- the electric furnace cannot: it is the only machine in the game that accepts
-- kamacite fines, and the only one carrying `sae-sintering`. Both are powder
-- processes and both are impossible in an open furnace for the same real reason.
--
-- The flux box is deliberately large. S12 measured that a furnace with a fluid
-- ingredient refuses its solid ingredient outright until the fluid is already
-- present; a generous buffer against a small per-craft draw makes that latch
-- rare after first build. It does not remove it.
--------------------------------------------------------------------------------

local furnace = derive.from("furnace", "electric-furnace", "sae-vacuum-furnace")
derive.placeholder_art(furnace, "wears electric-furnace's sprites until its plate exists")
furnace.icon = data.raw["furnace"]["electric-furnace"].icon
furnace.icons = nil
furnace.minable = { mining_time = 0.5, result = "sae-vacuum-furnace" }
furnace.collision_box = BOX_3x3
furnace.selection_box = SEL_3x3
furnace.crafting_categories = { "smelting", "sae-sintering" }
furnace.crafting_speed = 1.5
furnace.energy_usage = "1200kW"
furnace.energy_source = { type = "electric", usage_priority = "secondary-input" }
furnace.module_slots = 2
furnace.surface_conditions = CORE
furnace.source_inventory_size = 1          -- the prototype maximum
furnace.result_inventory_size = 1
furnace.fluid_boxes =
{
  {
    production_type = "input",
    volume = 2000,                         -- see the S12 note above
    pipe_connections = { { flow_direction = "input", direction = defines.direction.south, position = { 0, 1 } } }
  }
}
furnace.fluid_boxes_off_when_no_fluid_recipe = true
data:extend({ furnace })

--------------------------------------------------------------------------------
-- N9. Ignition Ring Mast -- graphics/building-spec-ignition-ring-mast.md
--
-- The opposite of the Arc Mast in every way that matters: that one catches
-- something episodic and banks it, this spends something continuously and cannot
-- store it at all.
--
-- **Nothing in the engine can require a building to be near another one**, and
-- this is how that is expressed anyway: the charge it makes carries a very short
-- `spoil_ticks` and no `spoil_result`, so it simply ceases to exist. Belt travel
-- is real time, so a mast more than a few seconds of belt from the Array delivers
-- nothing. Pure data, no control-stage script -- see items.lua for the timer.
--
-- No modules and no effects at all. 12 MW is meant to hurt, and a productivity
-- module undoing that would undo the point.
--------------------------------------------------------------------------------

local mast = crafter("sae-ring-mast", "assembling-machine-3", {
  categories = { "sae-ignition-charge" },
  energy = "12MW",
  modules = 0,
  conditions = CORE_ONLY,
  fluid_boxes =
  {
    {
      production_type = "input",
      volume = 400,
      pipe_connections = { { flow_direction = "input", direction = defines.direction.south, position = { 0, 1 } } }
    }
  }
})
mast.fixed_recipe = "sae-ignition-charge"
mast.allowed_effects = {}
data:extend({ mast })

--------------------------------------------------------------------------------
-- The items, and what each costs to build.
--
-- Kept beside the machines rather than in items.lua, which is where the Arc Mast
-- puts its own: a building and the thing that places it are one unit, and
-- splitting them across files is how one of them ends up forgotten.
--
-- The Coil Separator's cost is the one that carries an argument. It is priced in
-- coil assemblies -- two stages below the Field Coil Segment the whole endgame
-- runs on -- so the player spends endgame material to make more endgame
-- material. Nothing else in the mod has an ingredient list that means something.
--------------------------------------------------------------------------------

-- Item icons, for the machines whose art exists. Anything not listed here is
-- still wearing a vanilla icon on purpose, and is greppable by its absence.
local ICON = {
  ["sae-dross-classifier"] =
    "__space-age-extended__/graphics/icons/dross-classifier.png",
}

local function machine_item(name, order, ingredients, seconds)
  return
  {
    {
      type = "item",
      name = name,
      icon = ICON[name] or data.raw["item"]["assembling-machine-3"].icon,
      subgroup = "production-machine",
      order = "z[sae]-" .. order .. "[" .. name .. "]",
      place_result = name,
      stack_size = 20,
      weight = 40000
    },
    {
      type = "recipe",
      name = name,
      categories = { "crafting" },
      energy_required = seconds,
      ingredients = ingredients,
      results = { { type = "item", name = name, amount = 1 } },
      enabled = false
    }
  }
end

local function plate(n) return { type = "item", name = "sae-kamacite-plate", amount = n } end
local function welded(n) return { type = "item", name = "sae-welded-plate", amount = n } end
local function gear(n) return { type = "item", name = "iron-gear-wheel", amount = n } end
local function circuit(n) return { type = "item", name = "advanced-circuit", amount = n } end

for _, spec in ipairs({
  { "sae-drop-crusher", "a", { plate(40), gear(30), circuit(10) }, 6 },
  { "sae-ballast-drill", "b", { plate(60), welded(10), gear(40), circuit(15) }, 10 },
  { "sae-dross-classifier", "c", { plate(30), gear(20), circuit(10) }, 5 },
  { "sae-coil-separator", "d",
    { plate(40), welded(10), { type = "item", name = "sae-coil-assembly", amount = 1 },
      { type = "item", name = "processing-unit", amount = 20 } }, 12 },
  { "sae-whisker-comber", "e", { plate(30), gear(30), circuit(10) }, 6 },
  { "sae-helium-concentrator", "f",
    { plate(40), welded(8), { type = "item", name = "pipe", amount = 20 }, circuit(15) }, 8 },
  { "sae-vacuum-furnace", "g",
    { plate(50), welded(10), { type = "item", name = "processing-unit", amount = 10 } }, 10 },
  { "sae-ring-mast", "i",
    { plate(60), welded(20), { type = "item", name = "sae-superconducting-winding", amount = 4 },
      { type = "item", name = "processing-unit", amount = 20 } }, 15 },
}) do
  data:extend(machine_item(spec[1], spec[2], spec[3], spec[4]))
end
