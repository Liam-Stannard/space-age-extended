-- Items the Core makes from what it has.

local derive = require("prototypes.derive")
local item_sounds = require("__base__.prototypes.item_sounds")

data:extend({
  {
    type = "item",
    name = "sae-kamacite-ore",
    icon = "__space-age-extended__/graphics/icons/kamacite-ore.png",
    subgroup = "raw-resource",
    order = "z[sae]-a[kamacite-ore]",
    inventory_move_sound = item_sounds.resource_inventory_move,
    pick_sound = item_sounds.resource_inventory_pickup,
    drop_sound = item_sounds.resource_inventory_move,
    stack_size = 50,
    weight = 2 * kg
  },
  {
    type = "item",
    name = "sae-kamacite-plate",
    icon = "__space-age-extended__/graphics/icons/kamacite-plate.png",
    subgroup = "raw-material",
    order = "z[sae]-b[kamacite-plate]",
    inventory_move_sound = item_sounds.metal_small_inventory_move,
    pick_sound = item_sounds.metal_small_inventory_pickup,
    drop_sound = item_sounds.metal_small_inventory_move,
    stack_size = 100,
    weight = 1 * kg
  },
  {
    -- What sinks out of the melt. Not waste: it is what beds are made of, and
    -- it can be put back through settling to recover the metal still in it.
    type = "item",
    name = "sae-dross",
    icon = "__space-age-extended__/graphics/icons/dross.png",
    subgroup = "raw-material",
    order = "z[sae]-c[dross]",
    inventory_move_sound = item_sounds.resource_inventory_move,
    pick_sound = item_sounds.resource_inventory_pickup,
    drop_sound = item_sounds.resource_inventory_move,
    stack_size = 100,
    weight = 0.5 * kg
  },
  {
    -- Cast under 50g, where weight has already done the sorting.
    type = "item",
    name = "sae-cast-ingot",
    icon = "__space-age-extended__/graphics/icons/cast-ingot.png",
    subgroup = "raw-material",
    order = "z[sae]-d[cast-ingot]",
    inventory_move_sound = item_sounds.metal_large_inventory_move,
    pick_sound = item_sounds.metal_large_inventory_pickup,
    drop_sound = item_sounds.metal_large_inventory_move,
    stack_size = 50,
    weight = 4 * kg
  },
  {
    -- The same ingot, alloyed evenly in orbit because nothing settles there.
    type = "item",
    name = "sae-homogenised-ingot",
    icon = "__space-age-extended__/graphics/icons/homogenised-ingot.png",
    subgroup = "raw-material",
    order = "z[sae]-e[homogenised-ingot]",
    inventory_move_sound = item_sounds.metal_large_inventory_move,
    pick_sound = item_sounds.metal_large_inventory_pickup,
    drop_sound = item_sounds.metal_large_inventory_move,
    stack_size = 50,
    weight = 4 * kg
  },
  {
    -- Planted onto a bed; grows into whiskers.
    type = "item",
    name = "sae-seed-plate",
    icon = "__space-age-extended__/graphics/icons/seed-plate.png",
    subgroup = "raw-material",
    order = "z[sae]-f[seed-plate]",
    inventory_move_sound = item_sounds.metal_small_inventory_move,
    pick_sound = item_sounds.metal_small_inventory_pickup,
    drop_sound = item_sounds.metal_small_inventory_move,
    stack_size = 50,
    weight = 1 * kg,
    plant_result = "sae-whisker-plant"
  },
  {
    type = "item",
    name = "sae-kamacite-whiskers",
    icon = "__space-age-extended__/graphics/icons/kamacite-whiskers.png",
    subgroup = "raw-material",
    order = "z[sae]-g[whiskers]",
    inventory_move_sound = item_sounds.wire_inventory_move,
    pick_sound = item_sounds.wire_inventory_pickup,
    drop_sound = item_sounds.wire_inventory_move,
    stack_size = 100,
    weight = 0.5 * kg
  },
  {
    -- Joined cold, in vacuum, slowly. No heat anywhere in it.
    type = "item",
    name = "sae-welded-plate",
    icon = "__space-age-extended__/graphics/icons/welded-plate.png",
    subgroup = "raw-material",
    order = "z[sae]-h[welded-plate]",
    inventory_move_sound = item_sounds.metal_small_inventory_move,
    pick_sound = item_sounds.metal_small_inventory_pickup,
    drop_sound = item_sounds.metal_small_inventory_move,
    stack_size = 50,
    weight = 2 * kg
  }
})

--------------------------------------------------------------------------------
-- What the nine Core machines make.
--
-- Each of these exists because a machine in machines.lua produces or consumes
-- it; the tree they belong to is design/06-core-production-tree.md. Icons are
-- borrowed from the nearest existing Core icon until each has its own, which is
-- the same stand-in arrangement the machines themselves are under.
--------------------------------------------------------------------------------

data:extend({
  {
    -- The Drop Crusher's main stream, and what plate smelting should be sourced
    -- from -- see recipes.lua. If plate can still be made from raw ore, tier one
    -- is skippable and the crusher is decoration.
    type = "item",
    name = "sae-crushed-kamacite",
    icon = "__space-age-extended__/graphics/icons/kamacite-ore.png",
    subgroup = "raw-material",
    order = "z[sae]-b[crushed-kamacite]",
    inventory_move_sound = item_sounds.resource_inventory_move,
    pick_sound = item_sounds.resource_inventory_pickup,
    drop_sound = item_sounds.resource_inventory_move,
    stack_size = 100,
    weight = 2 * kg
  },
  {
    -- The crusher's second stream and the classifier's recovery. Deliberately
    -- not waste: the Vacuum Furnace is the only machine in the game that will
    -- take it, which is that furnace's reason to exist.
    type = "item",
    name = "sae-kamacite-fines",
    icon = "__space-age-extended__/graphics/icons/dross.png",
    subgroup = "raw-material",
    order = "z[sae]-b[kamacite-fines]",
    inventory_move_sound = item_sounds.resource_inventory_move,
    pick_sound = item_sounds.resource_inventory_pickup,
    drop_sound = item_sounds.resource_inventory_move,
    stack_size = 100,
    weight = 1 * kg
  },
  {
    -- Dross sorted to a usable grade. The whisker beds are laid on this rather
    -- than on raw dross, which is what makes classifying worth doing.
    type = "item",
    name = "sae-bed-dross",
    icon = "__space-age-extended__/graphics/icons/dross.png",
    subgroup = "raw-material",
    order = "z[sae]-c[bed-dross]",
    inventory_move_sound = item_sounds.resource_inventory_move,
    pick_sound = item_sounds.resource_inventory_pickup,
    drop_sound = item_sounds.resource_inventory_move,
    stack_size = 100,
    weight = 0.5 * kg
  },
  {
    -- Whiskers combed into one direction. Strength is directional, so alignment
    -- is a processing step rather than a property of the harvest.
    type = "item",
    name = "sae-whisker-tow",
    icon = "__space-age-extended__/graphics/icons/kamacite-whiskers.png",
    subgroup = "raw-material",
    order = "z[sae]-g[whisker-tow]",
    inventory_move_sound = item_sounds.wire_inventory_move,
    pick_sound = item_sounds.wire_inventory_pickup,
    drop_sound = item_sounds.wire_inventory_move,
    stack_size = 100,
    weight = 0.5 * kg
  },
  {
    -- A field emitter array: a plate of aligned whisker tips, sealed facing a
    -- gate under the Core's own vacuum.
    --
    -- This is real, and it is the one electronic device that wants exactly what
    -- this planet has. A sharp enough metal tip in a hard enough vacuum emits
    -- electrons from a cold surface under field alone -- no heater, no
    -- semiconductor, no copper. Sharp single-crystal metal tips, all pointing
    -- the same way, are precisely what comes off the comber, and hard vacuum is
    -- what the Core is. Everywhere else in the game an emitter array would need
    -- a pump, an envelope and a getter to hold a vacuum that here is simply the
    -- weather.
    type = "item",
    name = "sae-emitter-array",
    icon = "__space-age-extended__/graphics/icons/kamacite-whiskers.png",
    subgroup = "raw-material",
    order = "z[sae]-g[emitter-array]",
    inventory_move_sound = item_sounds.electric_small_inventory_move,
    pick_sound = item_sounds.electric_small_inventory_pickup,
    drop_sound = item_sounds.electric_small_inventory_move,
    stack_size = 100,
    weight = 0.5 * kg
  },
  {
    -- Unaligned, and cheap. A use for whiskers not worth the comb.
    type = "item",
    name = "sae-whisker-felt",
    icon = "__space-age-extended__/graphics/icons/kamacite-whiskers.png",
    subgroup = "raw-material",
    order = "z[sae]-g[whisker-felt]",
    inventory_move_sound = item_sounds.wire_inventory_move,
    pick_sound = item_sounds.wire_inventory_pickup,
    drop_sound = item_sounds.wire_inventory_move,
    stack_size = 100,
    weight = 0.5 * kg
  },
  {
    -- The Core's only phosphorus, pulled out of crushed kamacite by a field the
    -- planet cannot supply. See the Coil Separator.
    type = "item",
    name = "sae-schreibersite",
    icon = "__space-age-extended__/graphics/icons/dross.png",
    subgroup = "raw-material",
    order = "z[sae]-d[schreibersite]",
    inventory_move_sound = item_sounds.resource_inventory_move,
    pick_sound = item_sounds.resource_inventory_pickup,
    drop_sound = item_sounds.resource_inventory_move,
    stack_size = 100,
    weight = 1 * kg
  },
  {
    -- The Ring Mast's product, and the only item in the mod that is *meant* to
    -- be lost. Ten seconds of spoil and no spoil result, so a mast more than a
    -- few seconds of belt from the Array delivers nothing at all. That timer is
    -- the whole "ring" mechanic: the engine cannot require one building to be
    -- near another, so real belt time is made to do it instead.
    type = "item",
    name = "sae-ignition-charge",
    icon = "__space-age-extended__/graphics/icons/field-coil-segment.png",
    subgroup = "intermediate-product",
    order = "z[sae]-z[ignition-charge]",
    inventory_move_sound = item_sounds.reactor_inventory_move,
    pick_sound = item_sounds.reactor_inventory_pickup,
    drop_sound = item_sounds.reactor_inventory_move,
    stack_size = 20,
    weight = 2 * kg,
    spoil_ticks = 10 * 60
  }
})

--------------------------------------------------------------------------------
-- T3's two solids.
--------------------------------------------------------------------------------

data:extend({
  {
    -- Ultra-pure metal, deposited out of a gas. Nothing else on the Core is
    -- this clean, which is why the laminations want it.
    type = "item",
    name = "sae-carbonyl-powder",
    icon = "__space-age-extended__/graphics/icons/kamacite-plate.png",
    subgroup = "raw-material",
    order = "z[sae]-e[carbonyl-powder]",
    inventory_move_sound = item_sounds.resource_inventory_move,
    pick_sound = item_sounds.resource_inventory_pickup,
    drop_sound = item_sounds.resource_inventory_move,
    stack_size = 100,
    weight = 1 * kg
  },
  {
    -- Powder pressed into a shape, and the only thing the `sae-sintering`
    -- category makes. An open furnace would lose the powder; the Vacuum Furnace
    -- is the only machine that can do this at all.
    type = "item",
    name = "sae-sintered-preform",
    icon = "__space-age-extended__/graphics/icons/homogenised-ingot.png",
    subgroup = "intermediate-product",
    order = "z[sae]-f[sintered-preform]",
    inventory_move_sound = item_sounds.metal_large_inventory_move,
    pick_sound = item_sounds.metal_large_inventory_pickup,
    drop_sound = item_sounds.metal_large_inventory_move,
    stack_size = 50,
    weight = 2 * kg
  }
})

--------------------------------------------------------------------------------
-- What comes back out of a radiant generator.
--------------------------------------------------------------------------------

-- The ash of the corridor's fuel, on vanilla's depleted-cell pattern: an item
-- with no fuel value and no fuel category, so nothing will burn it a second
-- time. It is carried rather than destroyed -- a generator hands it back into a
-- burnt-result slot (see prototypes/corridor.lua), and reprocessing it is a
-- later stage's job. Until then it stacks like the cell it came from, which is
-- why the stack size and the weight are the radiant cell's rather than
-- vanilla's hundred-kilogram uranium one: it is the same object, spent.
local spent_cell =
{
  type = "item",
  name = "sae-spent-cell",
  icon = "__base__/graphics/icons/depleted-uranium-fuel-cell.png",
  subgroup = "intermediate-product",
  order = "z[sae]-d[spent-cell]",
  inventory_move_sound = item_sounds.fuel_cell_inventory_move,
  pick_sound = item_sounds.fuel_cell_inventory_pickup,
  drop_sound = item_sounds.fuel_cell_inventory_move,
  stack_size = 50,
  weight = 2 * kg,
  -- No `surface_conditions`: a generator on a platform will emit these, and an
  -- item that could not exist there would be an item the engine has to delete.
  --
  -- **`auto_recycle = false`, and here it is the whole point.** `__recycler__`
  -- gives every item that no recipe produces a hidden `<item>-recycling` that
  -- takes one in and returns it with probability 0.25 -- a 75% destroyer, not a
  -- no-op. Vanilla's depleted cell carries the same generated recipe and does
  -- not care, because reprocessing is already a real sink for it; this cell has
  -- no sink yet, so that recipe would be the only thing in the game that
  -- consumes it, and a recycler on a platform would quietly answer a question
  -- that is supposed to be answered by playing: whether spent cells ship down
  -- or platforms get a deliberate void. This stays: the generator only skips an
  -- item some recipe *produces*, and nothing produces a spent cell -- a
  -- generator hands it out, which is not a recipe. Stage 3's dissolve consumes
  -- it, so it will not lift this either.
  auto_recycle = false
}

data:extend({ spent_cell })
derive.placeholder_art(spent_cell,
  "wears depleted-uranium-fuel-cell's icon until its own exists")
