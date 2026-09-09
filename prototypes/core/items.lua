-- Items the Core makes from what it has.

data:extend({
  {
    type = "item",
    name = "sae-kamacite-ore",
    icon = "__space-age-extended__/graphics/icons/kamacite-ore.png",
    subgroup = "raw-resource",
    order = "z[sae]-a[kamacite-ore]",
    stack_size = 50,
    weight = 2000
  },
  {
    type = "item",
    name = "sae-kamacite-plate",
    icon = "__space-age-extended__/graphics/icons/kamacite-plate.png",
    subgroup = "raw-material",
    order = "z[sae]-b[kamacite-plate]",
    stack_size = 100,
    weight = 1000
  },
  {
    -- What sinks out of the melt. Not waste: it is what beds are made of, and
    -- it can be put back through settling to recover the metal still in it.
    type = "item",
    name = "sae-dross",
    icon = "__space-age-extended__/graphics/icons/dross.png",
    subgroup = "raw-material",
    order = "z[sae]-c[dross]",
    stack_size = 100,
    weight = 500
  },
  {
    -- Cast under 50g, where weight has already done the sorting.
    type = "item",
    name = "sae-cast-ingot",
    icon = "__space-age-extended__/graphics/icons/cast-ingot.png",
    subgroup = "raw-material",
    order = "z[sae]-d[cast-ingot]",
    stack_size = 50,
    weight = 4000
  },
  {
    -- The same ingot, alloyed evenly in orbit because nothing settles there.
    type = "item",
    name = "sae-homogenised-ingot",
    icon = "__space-age-extended__/graphics/icons/homogenised-ingot.png",
    subgroup = "raw-material",
    order = "z[sae]-e[homogenised-ingot]",
    stack_size = 50,
    weight = 4000
  },
  {
    -- Planted onto a bed; grows into whiskers.
    type = "item",
    name = "sae-seed-plate",
    icon = "__space-age-extended__/graphics/icons/seed-plate.png",
    subgroup = "raw-material",
    order = "z[sae]-f[seed-plate]",
    stack_size = 50,
    weight = 1000,
    place_result = nil,
    plant_result = "sae-whisker-plant"
  },
  {
    type = "item",
    name = "sae-kamacite-whiskers",
    icon = "__space-age-extended__/graphics/icons/kamacite-whiskers.png",
    subgroup = "raw-material",
    order = "z[sae]-g[whiskers]",
    stack_size = 100,
    weight = 500
  },
  {
    -- Joined cold, in vacuum, slowly. No heat anywhere in it.
    type = "item",
    name = "sae-welded-plate",
    icon = "__space-age-extended__/graphics/icons/welded-plate.png",
    subgroup = "raw-material",
    order = "z[sae]-h[welded-plate]",
    stack_size = 50,
    weight = 2000
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
    stack_size = 100,
    weight = 2000
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
    stack_size = 100,
    weight = 1000
  },
  {
    -- Dross sorted to a usable grade. The whisker beds are laid on this rather
    -- than on raw dross, which is what makes classifying worth doing.
    type = "item",
    name = "sae-bed-dross",
    icon = "__space-age-extended__/graphics/icons/dross.png",
    subgroup = "raw-material",
    order = "z[sae]-c[bed-dross]",
    stack_size = 100,
    weight = 500
  },
  {
    -- Whiskers combed into one direction. Strength is directional, so alignment
    -- is a processing step rather than a property of the harvest.
    type = "item",
    name = "sae-whisker-tow",
    icon = "__space-age-extended__/graphics/icons/kamacite-whiskers.png",
    subgroup = "raw-material",
    order = "z[sae]-g[whisker-tow]",
    stack_size = 100,
    weight = 500
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
    stack_size = 100,
    weight = 500
  },
  {
    -- Unaligned, and cheap. A use for whiskers not worth the comb.
    type = "item",
    name = "sae-whisker-felt",
    icon = "__space-age-extended__/graphics/icons/kamacite-whiskers.png",
    subgroup = "raw-material",
    order = "z[sae]-g[whisker-felt]",
    stack_size = 100,
    weight = 500
  },
  {
    -- The Core's only phosphorus, pulled out of crushed kamacite by a field the
    -- planet cannot supply. See the Coil Separator.
    type = "item",
    name = "sae-schreibersite",
    icon = "__space-age-extended__/graphics/icons/dross.png",
    subgroup = "raw-material",
    order = "z[sae]-d[schreibersite]",
    stack_size = 100,
    weight = 1000
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
    stack_size = 20,
    weight = 2000,
    spoil_ticks = 10 * 60,
    spoil_result = nil
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
    stack_size = 100,
    weight = 1000
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
    stack_size = 50,
    weight = 2000
  }
})
