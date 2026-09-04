-- Whisker beds: ground made from dross, and the only surface metal will grow on.
--
-- Graphics are a vanilla placeholder until the art pass.

local bed = table.deepcopy(data.raw.tile["stone-path"])
bed.name = "sae-whisker-bed"
bed.order = "z[sae]-a[whisker-bed]"
bed.minable = { mining_time = 0.2, result = "sae-whisker-bed" }
bed.map_color = { r = 0.42, g = 0.40, b = 0.36 }
bed.can_be_part_of_blueprint = true
data:extend({ bed })

data:extend({
  {
    type = "item",
    name = "sae-whisker-bed",
    icon = "__base__/graphics/icons/stone-brick.png",
    subgroup = "terrain",
    order = "z[sae]-a[whisker-bed]",
    stack_size = 100,
    weight = 500,
    place_as_tile =
    {
      result = "sae-whisker-bed",
      condition_size = 1,
      condition = { layers = { water_tile = true } }
    }
  }
})
