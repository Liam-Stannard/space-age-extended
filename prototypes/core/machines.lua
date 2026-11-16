local derive = require("prototypes.derive")
local item_sounds = require("__base__.prototypes.item_sounds")

local HEAVY_CRUSHER = "sae-heavy-crusher"

data:extend({
  { type = "recipe-category", name = "sae-crushing" }
})

local crusher = derive.from("assembling-machine", "crusher", HEAVY_CRUSHER)
crusher.minable.result = HEAVY_CRUSHER
crusher.crafting_categories = { "sae-crushing" }
crusher.energy_usage = "810kW"
crusher.heating_energy = "100kW"
crusher.surface_conditions = { { property = "gravity", min = 1 } }
data:extend({ crusher })

data:extend({
  {
    type = "item",
    name = HEAVY_CRUSHER,
    icon = crusher.icon,
    subgroup = "production-machine",
    order = "z[sae]-b[" .. HEAVY_CRUSHER .. "]",
    inventory_move_sound = item_sounds.drill_inventory_move,
    pick_sound = item_sounds.drill_inventory_pickup,
    drop_sound = item_sounds.drill_inventory_move,
    place_result = HEAVY_CRUSHER,
    stack_size = 10,
    weight = 100 * kg
  },
  {
    type = "recipe",
    name = HEAVY_CRUSHER,
    categories = { "crafting" },
    energy_required = 15,
    ingredients =
    {
      { type = "item", name = "low-density-structure", amount = 30 },
      { type = "item", name = "steel-plate", amount = 15 },
      { type = "item", name = "electric-engine-unit", amount = 15 }
    },
    results = { { type = "item", name = HEAVY_CRUSHER, amount = 1 } },
    enabled = false
  }
})
