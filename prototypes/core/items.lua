-- Items the Core makes from what it has.

data:extend({
  {
    type = "item",
    name = "sae-kamacite-ore",
    icon = "__base__/graphics/icons/iron-ore.png",
    subgroup = "raw-resource",
    order = "z[sae]-a[kamacite-ore]",
    stack_size = 50,
    weight = 2000
  },
  {
    type = "item",
    name = "sae-kamacite-plate",
    icon = "__base__/graphics/icons/steel-plate.png",
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
    icon = "__base__/graphics/icons/stone.png",
    subgroup = "raw-material",
    order = "z[sae]-c[dross]",
    stack_size = 100,
    weight = 500
  },
  {
    -- Cast under 50g, where weight has already done the sorting.
    type = "item",
    name = "sae-cast-ingot",
    icon = "__base__/graphics/icons/iron-plate.png",
    subgroup = "raw-material",
    order = "z[sae]-d[cast-ingot]",
    stack_size = 50,
    weight = 4000
  },
  {
    -- The same ingot, alloyed evenly in orbit because nothing settles there.
    type = "item",
    name = "sae-homogenised-ingot",
    icon = "__base__/graphics/icons/copper-plate.png",
    subgroup = "raw-material",
    order = "z[sae]-e[homogenised-ingot]",
    stack_size = 50,
    weight = 4000
  },
  {
    -- Planted onto a bed; grows into whiskers.
    type = "item",
    name = "sae-seed-plate",
    icon = "__base__/graphics/icons/steel-plate.png",
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
    icon = "__space-age__/graphics/icons/tungsten-plate.png",
    subgroup = "raw-material",
    order = "z[sae]-g[whiskers]",
    stack_size = 100,
    weight = 500
  },
  {
    -- Joined cold, in vacuum, slowly. No heat anywhere in it.
    type = "item",
    name = "sae-welded-plate",
    icon = "__space-age__/graphics/icons/tungsten-carbide.png",
    subgroup = "raw-material",
    order = "z[sae]-h[welded-plate]",
    stack_size = 50,
    weight = 2000
  }
})
