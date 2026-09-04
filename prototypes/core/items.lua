-- Items the Core's resources yield. Everything downstream of these arrives
-- with Phase 2.

data:extend({
  {
    type = "item",
    name = "sae-kamacite-ore",
    icon = "__base__/graphics/icons/iron-ore.png",
    subgroup = "raw-resource",
    order = "z[sae]-a[kamacite-ore]",
    stack_size = 50,
    weight = 2000
  }
})
