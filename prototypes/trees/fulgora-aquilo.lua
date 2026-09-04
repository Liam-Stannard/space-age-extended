-- Fulgora <-> Aquilo: holmium in the cold.
--
-- THE ANCHOR. Both legs are forced by fluids that have no barrel, so neither
-- can be dodged by moving a machine:
--
--   Fulgora -> Aquilo   holmium plate, because fluorine cannot leave Aquilo
--   Aquilo -> Fulgora   fluorinated holmium, because electrolyte cannot leave
--                       Fulgora
--
-- THE MECHANIC: the cold loop. Every step of this chain takes cold cryogen in
-- and hands spent cryogen back, so its layouts are loops rather than lines and
-- the chiller is an overhead that scales with machine count. Re-chilling needs
-- ammonia, which also has no barrel -- so cryogen is either made on Aquilo or
-- shipped cold, and running the chain elsewhere means paying freight forever.
--
-- THE CAPSTONE: the superconducting winding, which becomes the field coil's
-- conductor on the Core, and the superconducting store, which is what a world
-- of spikes has always needed.

data:extend({
  {
    type = "fluid",
    name = "sae-cold-cryogen",
    icon = "__space-age__/graphics/icons/fluid/fluoroketone-cold.png",
    subgroup = "fluid",
    order = "z[sae]-fa[a-cold-cryogen]",
    default_temperature = -140,
    base_color = { r = 0.40, g = 0.65, b = 0.90 },
    flow_color = { r = 0.65, g = 0.85, b = 1.0 }
  },
  {
    type = "fluid",
    name = "sae-spent-cryogen",
    icon = "__space-age__/graphics/icons/fluid/fluoroketone-hot.png",
    subgroup = "fluid",
    order = "z[sae]-fa[b-spent-cryogen]",
    default_temperature = 20,
    base_color = { r = 0.70, g = 0.60, b = 0.55 },
    flow_color = { r = 0.85, g = 0.78, b = 0.70 }
  },

  {
    type = "item",
    name = "sae-fluorinated-holmium",
    icon = "__space-age__/graphics/icons/holmium-plate.png",
    subgroup = "raw-material",
    order = "z[sae]-fa[c-fluorinated-holmium]",
    stack_size = 100,
    weight = 2000
  },

  -- Aquilo only: ammonia has no barrel.
  {
    type = "recipe",
    name = "sae-cryogen",
    categories = { "chemistry" },
    energy_required = 6,
    ingredients =
    {
      { type = "fluid", name = "ammonia", amount = 50 },
      { type = "item", name = "lithium-plate", amount = 1 }
    },
    results = { { type = "fluid", name = "sae-cold-cryogen", amount = 100 } },
    enabled = false
  },
  {
    type = "recipe",
    name = "sae-cryogen-recovery",
    categories = { "chemistry" },
    energy_required = 4,
    ingredients =
    {
      { type = "fluid", name = "sae-spent-cryogen", amount = 100 },
      { type = "fluid", name = "ammonia", amount = 10 }
    },
    results = { { type = "fluid", name = "sae-cold-cryogen", amount = 90 } },
    enabled = false
  },

  -- Aquilo only: fluorine has no barrel. This is what the holmium is shipped
  -- out for.
  {
    type = "recipe",
    name = "sae-fluorinated-holmium",
    categories = { "chemistry" },
    energy_required = 8,
    ingredients =
    {
      { type = "item", name = "holmium-plate", amount = 2 },
      { type = "fluid", name = "fluorine", amount = 20 },
      { type = "fluid", name = "sae-cold-cryogen", amount = 20 }
    },
    results =
    {
      { type = "item", name = "sae-fluorinated-holmium", amount = 1 },
      { type = "fluid", name = "sae-spent-cryogen", amount = 20 }
    },
    icon = "__space-age__/graphics/icons/holmium-plate.png",
    icon_size = 64,
    allow_productivity = true,
    enabled = false
  },

  -- Fulgora only: electrolyte has no barrel. This is what comes back.
  {
    type = "recipe",
    name = "sae-superconducting-winding",
    categories = { "electromagnetics" },
    energy_required = 12,
    ingredients =
    {
      { type = "item", name = "sae-fluorinated-holmium", amount = 2 },
      { type = "fluid", name = "electrolyte", amount = 20 },
      { type = "fluid", name = "sae-cold-cryogen", amount = 20 },
      { type = "item", name = "copper-cable", amount = 8 }
    },
    results =
    {
      { type = "item", name = "sae-superconducting-winding", amount = 1 },
      { type = "fluid", name = "sae-spent-cryogen", amount = 20 }
    },
    icon = "__space-age__/graphics/icons/superconductor.png",
    icon_size = 64,
    allow_productivity = true,
    enabled = false
  }
})

-- The capstone building. A world of spikes -- Fulgora's lightning when it is
-- earned, the Core's arc storms at the end -- has always wanted somewhere to
-- put a surge that arrives faster than anything can spend it.
local store = table.deepcopy(data.raw.accumulator["accumulator"])
store.name = "sae-superconducting-store"
store.icon = "__base__/graphics/icons/accumulator.png"
store.minable = { mining_time = 0.5, result = "sae-superconducting-store" }
store.energy_source =
{
  type = "electric",
  buffer_capacity = "500MJ",
  usage_priority = "tertiary",
  input_flow_limit = "20MW",
  output_flow_limit = "20MW"
}
store.fast_replaceable_group = nil
store.next_upgrade = nil
data:extend({ store })

data:extend({
  {
    type = "item",
    name = "sae-superconducting-store",
    icon = "__base__/graphics/icons/accumulator.png",
    subgroup = "energy",
    order = "z[sae]-c[superconducting-store]",
    place_result = "sae-superconducting-store",
    stack_size = 20,
    weight = 20000
  },
  {
    type = "recipe",
    name = "sae-superconducting-store",
    categories = { "crafting" },
    energy_required = 20,
    ingredients =
    {
      { type = "item", name = "sae-superconducting-winding", amount = 10 },
      { type = "item", name = "accumulator", amount = 2 },
      { type = "item", name = "steel-plate", amount = 20 }
    },
    results = { { type = "item", name = "sae-superconducting-store", amount = 1 } },
    enabled = false
  }
})
