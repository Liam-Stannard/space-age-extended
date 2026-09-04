-- The Core's machinery: what draws the vents, and what tends the beds.

-- The vent pump. A pumpjack with an input fluid box added, because drawing
-- melt costs helium-3 -- the scarce vent throttling the rich one. The engine
-- reports missing_required_fluid when the helium runs out, which is a legible
-- failure the player can read without a wiki.
local pump = table.deepcopy(data.raw["mining-drill"]["pumpjack"])
pump.name = "sae-vent-pump"
pump.icon = "__base__/graphics/icons/pumpjack.png"
pump.minable = { mining_time = 0.5, result = "sae-vent-pump" }
pump.input_fluid_box = table.deepcopy(data.raw["mining-drill"]["electric-mining-drill"].input_fluid_box)
pump.fast_replaceable_group = nil
pump.next_upgrade = nil
data:extend({ pump })

-- Whiskers: metal grown rather than smelted. Gleba farms food; the Core farms
-- kamacite. Growth time is the throughput, so scaling means more ground.
local plant = table.deepcopy(data.raw.plant["tree-plant"])
plant.name = "sae-whisker-plant"
plant.icon = "__space-age__/graphics/icons/tungsten-plate.png"
plant.growth_ticks = 4 * 60 * 60          -- four minutes
plant.surface_conditions = { { property = "pressure", min = 1, max = 9 } }
plant.autoplace = { probability_expression = 0, tile_restriction = { "sae-whisker-bed" } }
plant.minable = { mining_time = 0.5, results = { { type = "item", name = "sae-kamacite-whiskers", amount = 4 } } }
plant.map_color = { r = 0.75, g = 0.75, b = 0.80 }
data:extend({ plant })

-- The bed tender plants seed plates and harvests what grew. The vanilla
-- agricultural tower needs pressure 1000-2000 and is refused here, so the beds
-- would otherwise be hand-worked.
local tender = table.deepcopy(data.raw["agricultural-tower"]["agricultural-tower"])
tender.name = "sae-bed-tender"
tender.icon = "__space-age__/graphics/icons/agricultural-tower.png"
tender.minable = { mining_time = 0.5, result = "sae-bed-tender" }
tender.surface_conditions = { { property = "pressure", min = 1, max = 9 } }
tender.fast_replaceable_group = nil
tender.next_upgrade = nil
data:extend({ tender })

data:extend({
  {
    type = "item",
    name = "sae-vent-pump",
    icon = "__base__/graphics/icons/pumpjack.png",
    subgroup = "extraction-machine",
    order = "z[sae]-a[vent-pump]",
    place_result = "sae-vent-pump",
    stack_size = 20,
    weight = 20000
  },
  {
    type = "item",
    name = "sae-bed-tender",
    icon = "__space-age__/graphics/icons/agricultural-tower.png",
    subgroup = "agriculture",
    order = "z[sae]-b[bed-tender]",
    place_result = "sae-bed-tender",
    stack_size = 20,
    weight = 20000
  }
})
