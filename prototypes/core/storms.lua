-- Arc storms.
--
-- The Core's field is dead, and what is left of it discharges through a
-- metallic crust. The hazard and the power supply are the same thing, which is
-- Fulgora's lesson on a world that looks nothing like Fulgora -- and it is
-- tuned deliberately against Fulgora so it plays differently:
--
--   Fulgora  100 damage, 1000MJ, a strike per chunk every 10 seconds.
--   The Core 600 damage, 4000MJ, a strike per chunk every 90 seconds.
--
-- Fulgora's lightning is a drizzle you harvest. This is an event you survive
-- and store, so masts are sited for coverage first and power second.

local arc = table.deepcopy(data.raw.lightning["lightning"])
arc.name = "sae-arc"
arc.damage = { amount = 600, type = "electric" }
arc.energy = "4000MJ"
data:extend({ arc })

-- Catches a strike and banks it. Worse than Fulgora's collector at converting
-- what it catches, and far bigger, because out here the strikes are the
-- exception rather than the weather.
local mast = table.deepcopy(data.raw["lightning-attractor"]["lightning-collector"])
mast.name = "sae-arc-mast"
mast.icon = "__space-age__/graphics/icons/lightning-collector.png"
mast.minable = { mining_time = 0.5, result = "sae-arc-mast" }
mast.efficiency = 0.35
mast.range_elongation = 20
mast.energy_source =
{
  type = "electric",
  buffer_capacity = "4000MJ",
  usage_priority = "primary-output",
  output_flow_limit = "40MW",
  -- Lower than vanilla's 2.5MJ, because strikes here are nine times rarer and
  -- standby loss between them matters more.
  --
  -- Note what this does *not* fix: an attractor's buffer empties within seconds
  -- when nothing draws from it, and vanilla's own collector was measured doing
  -- exactly the same -- 260MJ to zero in twelve seconds, unwired. Storage is
  -- not optional here. A mast on its own loses what it caught, so accumulators
  -- come before masts are worth building.
  drain = "100kW"
}
mast.fast_replaceable_group = nil
mast.next_upgrade = nil
data:extend({ mast })

data:extend({
  {
    type = "item",
    name = "sae-arc-mast",
    icon = "__space-age__/graphics/icons/lightning-collector.png",
    subgroup = "energy",
    order = "z[sae]-a[arc-mast]",
    place_result = "sae-arc-mast",
    stack_size = 10,
    weight = 40000
  },
  {
    type = "recipe",
    name = "sae-arc-mast",
    categories = { "crafting" },
    energy_required = 10,
    ingredients =
    {
      { type = "item", name = "sae-kamacite-plate", amount = 30 },
      { type = "item", name = "sae-welded-plate", amount = 5 },
      { type = "item", name = "processing-unit", amount = 10 },
      { type = "item", name = "accumulator", amount = 5 }
    },
    results = { { type = "item", name = "sae-arc-mast", amount = 1 } },
    enabled = false
  }
})
