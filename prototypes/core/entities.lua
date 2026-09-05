-- The Core's machinery: what draws the vents, and what tends the beds.

-- The vent pump. A pumpjack with an input fluid box added, because drawing
-- melt costs helium-3 -- the scarce vent throttling the rich one. The engine
-- reports missing_required_fluid when the helium runs out, which is a legible
-- failure the player can read without a wiki.
local pump = table.deepcopy(data.raw["mining-drill"]["pumpjack"])
pump.name = "sae-vent-pump"
pump.icon = "__base__/graphics/icons/pumpjack.png"
pump.minable = { mining_time = 0.5, result = "sae-vent-pump" }

-- Both fluid boxes are replaced rather than inherited, and this is a decision
-- about how the building reads on the ground rather than about plumbing.
--
-- Inherited, it was a mess: the pumpjack's output sits on a *corner tile* and
-- walks around the four corners as the building rotates, while the electric
-- mining drill's input offers *three* connections at edge midpoints. Seven
-- possible hookups on a 3x3, of which a player uses two, and no arrangement of
-- art can make the other five look intended.
--
-- One in, one out, on opposite edges. Helium enters the south face, melt leaves
-- the north face, both on the centre tile of their edge, both facing straight
-- out. Fluid runs through the building in a single straight line, which is what
-- the plumbing in front of it will look like too -- pipes only ever join
-- axis-aligned, so a connector that is not square to an edge is a connector the
-- player cannot reach cleanly.
local covers = pump.output_fluid_box.pipe_covers
pump.output_fluid_box =
{
  volume = 1000,
  pipe_covers = covers,
  pipe_connections =
  {
    { flow_direction = "output", direction = defines.direction.north, position = { 0, -1 } }
  }
}
pump.input_fluid_box =
{
  volume = 200,
  pipe_covers = covers,
  pipe_connections =
  {
    { flow_direction = "input", direction = defines.direction.south, position = { 0, 1 } }
  }
}
pump.fast_replaceable_group = nil
pump.next_upgrade = nil
data:extend({ pump })

-- Whiskers: metal grown rather than smelted. Gleba farms food; the Core farms
-- kamacite. Growth time is the throughput, so scaling means more ground.
local plant = table.deepcopy(data.raw.plant["tree-plant"])
plant.name = "sae-whisker-plant"
plant.icon = "__space-age-extended__/graphics/icons/kamacite-whiskers.png"
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

-- Centre the crane's pivot. Inherited it is {0.5, -0.55, 4.6} -- half a tile
-- east and just over half north of the building's middle, because vanilla's
-- tower is not symmetrical. Ours is: the design is an armoured octagonal hub
-- with a slewing bearing ring on top of it, and the arm has to appear to turn on
-- the ring that is drawn. Moving the origin is the cheap half of that fix; the
-- alternative was drawing the bearing off-centre to chase vanilla's asymmetry.
--
-- Safe against reach: the arm's extendable segments run to 4.5 and 4.0 against a
-- planting radius of 3, so half a tile of recentring is well inside what the
-- crane can already cover.
tender.crane.origin = { 0, 0, 4.6 }

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
