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
  }
})

--------------------------------------------------------------------------------
-- What the Core's machines make.
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
    -- The crusher's second stream. Deliberately
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
