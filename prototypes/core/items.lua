-- Items the Core makes from what it has.

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
