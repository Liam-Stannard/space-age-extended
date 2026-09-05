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
-- The strike itself is machinery, not something to browse.
arc.hidden_in_factoriopedia = true
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

-- Footprint. The collector this copies is 2x2 with a 1.4 collision box, and
-- its art matches: vanilla's widest row is 144 px at scale 0.5, so 2.25 tiles
-- on a 2 tile pitch -- a quarter tile of sloped leg overhanging, which reads
-- fine. Ours was 3.14 tiles, and on the same 2 tile pitch a row of masts
-- overlapped by more than a whole tile: each base plate ate its neighbour. The
-- mast is genuinely a bigger machine than Fulgora's collector, which is the
-- whole point of it, so the box grew to 3x3 rather than the art shrinking to
-- a 2x2. The art is then cut to exactly 3.00 tiles to match -- see below --
-- because 3.14 tiles on a 3 tile pitch still overlaps, by a quarter of a
-- foot pad, and a row of masts still read as interleaved.
mast.collision_box = { { -1.4, -1.4 }, { 1.4, 1.4 } }
mast.selection_box = { { -1.5, -1.5 }, { 1.5, 1.5 } }

-- Art. The entity has no rotation, so there is one picture and the two
-- one-shot glow sheets the prototype exposes -- see
-- graphics/building-spec-arc-mast.md sections 6 and 15. Geometry is measured
-- off the approved plate, not guessed: the sprite is 224x365 at scale 0.5, and
-- the shift is by_pixel(0, -57) so the base plate's centre sits -0.13 tiles
-- from the origin -- the same place vanilla's collector puts its own. The
-- first pass used -81 and the mast floated two thirds of a tile above its
-- footprint, standing on nothing.
--
-- The plate is cut so its visible content is exactly 192 px -- 3.00 tiles --
-- so the art is the width of the box and a row of masts touches rather than
-- overlaps. See the footprint note above.
local ART = "__space-age-extended__/graphics/entity/arc-mast/"
mast.icon = "__space-age-extended__/graphics/icons/arc-mast.png"
mast.chargable_graphics =
{
  picture =
  {
    layers =
    {
      {
        filename = ART .. "base.png",
        priority = "high",
        width = 224,
        height = 345,
        shift = { 0, -1.78125 },   -- by_pixel(0, -57) at scale 0.5
        scale = 0.5
      },
      {
        filename = ART .. "shadow.png",
        priority = "high",
        draw_as_shadow = true,
        -- The shadow lies flat on the ground and leans up and to the right,
        -- so it is wider than the colour plate but needs no extra rows, and it
        -- carries its own shift -- both derived by
        -- tools/process-building-art.py, not guessed.
        width = 496,
        height = 345,
        shift = { 2.125, -1.78125 },
        scale = 0.5
      }
    }
  },
  charge_animation =
  {
    layers =
    {
      {
        filename = ART .. "charge.png",
        priority = "high",
        blend_mode = "additive",
        draw_as_glow = true,
        width = 224,
        height = 345,
        frame_count = 19,
        line_length = 8,
        shift = { 0, -1.78125 },   -- by_pixel(0, -57) at scale 0.5
        scale = 0.5
      }
    }
  },
  charge_animation_is_looped = false,
  charge_cooldown = 30,
  discharge_animation =
  {
    layers =
    {
      {
        filename = ART .. "discharge.png",
        priority = "high",
        blend_mode = "additive",
        draw_as_glow = true,
        width = 224,
        height = 345,
        frame_count = 24,
        line_length = 8,
        shift = { 0, -1.78125 },   -- by_pixel(0, -57) at scale 0.5
        scale = 0.5
      }
    }
  },
  discharge_cooldown = 60
}

-- The strike has to land on the electrode, so it is measured off the plate
-- rather than inherited: the cage spans -4.23 to -3.38 tiles from the origin,
-- and -3.8 is the middle of it. Vanilla's -4.8 would put the bolt a tile above
-- the mast, terminating in open air.
mast.lightning_strike_offset = { 0, -3.8 }

data:extend({ mast })

data:extend({
  {
    type = "item",
    name = "sae-arc-mast",
    icon = "__space-age-extended__/graphics/icons/arc-mast.png",
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
