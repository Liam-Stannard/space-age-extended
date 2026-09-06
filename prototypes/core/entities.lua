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

-- Art. Inherited, this drew Gleba's planted tree -- so the Core's one crop grew
-- as a tree, on a dead metal world with no air. See graphics/TODO.md section 6,
-- which flagged it with no art plan.
--
-- What it is now: four clusters of kamacite whiskers, the same hard faceted
-- silver-white needles on a dark grit base that the locked chain 2 icon draws,
-- measured at 1.94 to 2.11 tiles wide with alpha zero on all four canvas edges.
-- Four rather than vanilla's eight because these are visual variants, not growth
-- stages -- checked by looking at vanilla's own trunk sheet, which is eight
-- same-sized trees in a 4x2 grid, not a sequence.
--
-- `leaves` is required by the engine but this plant has none: the needles *are*
-- the plant, and they live in `trunk` so the whole clump takes the shadow.
local WP = "__space-age-extended__/graphics/entity/whisker-plant/"
local function whisker_variation(n)
  return
  {
    -- Two frames, and they earn their keep. The engine requires
    -- `trunk.frame_count == leaves.frame_count + 1` because a plant's trunk is
    -- what carries its growth, so rather than pad the sheet with a duplicate,
    -- frame 0 is the same clump at 62% about its own base: a young bed reads as
    -- sprouts and a ripe one as full needles. The shadow rides as a layer here
    -- rather than in the variation's own `shadow` slot, so it grows with it.
    trunk =
    {
      layers =
      {
        {
          filename = WP .. "trunk-" .. n .. ".png",
          priority = "extra-high",
          width = 176, height = 144,
          frame_count = 2, line_length = 2,
          shift = { 0, -0.34375 },       -- by_pixel(0, -11) at scale 0.5
          scale = 0.5
        },
        {
          filename = WP .. "trunk-" .. n .. "-shadow.png",
          priority = "extra-high",
          draw_as_shadow = true,
          width = 279, height = 144,
          frame_count = 2, line_length = 2,
          shift = { 0.80469, -0.34375 },
          scale = 0.5
        }
      }
    },
    leaves = util.empty_sprite(),
    -- Kept from the inherited variation so mining still throws debris, but the
    -- debris is metal: vanilla threw `yumako-leaf-particle`, which is a green
    -- leaf, off a crystal.
    leaf_generation = plant.variations[1].leaf_generation,
    branch_generation = plant.variations[1].branch_generation
  }
end

local function metal_particles(effect)
  if type(effect) ~= "table" then return end
  for k, v in pairs(effect) do
    if type(v) == "table" then
      metal_particles(v)
    elseif k == "particle_name" then
      effect[k] = "accumulator-metal-particle-small"
    end
  end
end

local whisker_variations = {}
for n = 1, 4 do
  local v = whisker_variation(n)
  metal_particles(v.leaf_generation)
  metal_particles(v.branch_generation)
  whisker_variations[n] = v
end
plant.variations = whisker_variations

-- `growth_variations` is dropped rather than trimmed. Each entry is a set of
-- warp and alpha maps the engine distorts a growing plant through, and vanilla's
-- are 640x560 at shift {2.1875, -1.25} and scale 0.429 -- measured for its tree,
-- and aligned with nothing on a 176x144 clump. This plant carries its growth in
-- the two trunk frames instead, so the warp has no work to do.
plant.growth_variations = nil
while #plant.growth_mounds > #whisker_variations do
  table.remove(plant.growth_mounds)
end

-- The mound is the little heap of ground thrown up around a growing plant, and
-- vanilla's is Gleba soil. Recoloured to the same iron-nickel grit as the bed
-- tile, so a sprouting whisker does not sit in a ring of brown earth.
for _, mound in pairs(plant.growth_mounds) do
  if type(mound) == "table" and mound.filename then
    mound.filename = "__space-age-extended__/graphics/entity/whisker-plant/mound.png"
  end
end

-- The inherited selection box was a tree's -- three tiles of headroom above the
-- trunk. A whisker clump is two tiles across and barely one tall, so the box is
-- brought down to what the art actually occupies; otherwise the cursor picks the
-- plant up from empty ground well above it.
plant.selection_box = { { -1, -1.2 }, { 1, 0.8 } }

data:extend({ plant })

-- The bed tender plants seed plates and harvests what grew. The vanilla
-- agricultural tower needs pressure 1000-2000 and is refused here, so the beds
-- would otherwise be hand-worked.
local tender = table.deepcopy(data.raw["agricultural-tower"]["agricultural-tower"])
tender.name = "sae-bed-tender"
tender.icon = "__space-age-extended__/graphics/icons/bed-tender.png"
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
-- ...and bring it down. The height was left at vanilla's 4.6 on the grounds that
-- it was "unchanged", which was wrong: 4.6 was chosen for a tower whose art is
-- 5.11 tiles tall, and this hub is 1.84. Measured off the first in-game
-- screenshot at 37.3 screen px per tile, the arm's lowest point sat 2.68 tiles
-- above the hub's centre and never touched it -- an arm pivoting on thin air a
-- storey above the bearing it is supposed to turn on. Dropping z by the measured
-- 1.85 tiles puts it on the drawn slewing ring.
tender.crane.origin = { 0, 0, 2.75 }

-- The arm is ours now, as far as it can be.
--
-- `crane` is a prototype in its own right and it is a *turntable*: nine parts,
-- each a rotational spritesheet of 64 to 128 frames so the arm can swing to any
-- angle, plus a shadow and a reflection for each -- 29 files and 37.7 megapixels,
-- rendered from a 3D model. There is no way to author a replacement without
-- building that model; an image generator asked for 64 angles of an arm gives
-- 64 different arms. So vanilla's geometry is kept and the material is changed,
-- which is what tools/recolour-crane.py does and what recolour-turbine.py
-- already does for the quench turbine.
--
-- Measured rather than eyeballed: vanilla's crane runs hue 20-70 degrees, olive
-- on the hub and brass on the segments, at a body luminance of 72-150 across
-- parts. Ours runs 65-123 with the same part-to-part spread -- the Bed Tender's
-- grey-brown with ochre banding, section 3.3, uniformly darker rather than
-- flattened.
--
-- What is still vanilla is the *movement*: the joint layout and the animation
-- are unchanged, so the arm folds the way an agricultural tower's does. Changing
-- that needs the model.
local CRANE_SRC = "__space%-age__/graphics/entity/agricultural%-tower/agricultural%-tower%-crane"
local CRANE_DST = "__space-age-extended__/graphics/entity/bed-tender/crane/crane"
local function repoint_crane(t)
  for k, v in pairs(t) do
    if type(v) == "table" then
      repoint_crane(v)
    elseif type(v) == "string" and v:find(CRANE_SRC) then
      t[k] = v:gsub(CRANE_SRC, CRANE_DST)
    end
  end
end
repoint_crane(tender.crane)

-- Art. Only the hub is ours: `crane` is a prototype in its own right and still
-- draws vanilla's arm, so this building ships a custom hub under an inherited
-- arm until the crane gets its own pass. See graphics/building-spec-bed-tender.md
-- sections 6, 7 and 13.
--
-- Every number below is measured off the cut plate, not guessed. The hub's
-- visible content is exactly 192 px -- 3.00 tiles -- so two tenders at a 3 tile
-- pitch touch rather than overlap, which is the defect that cost the arc mast
-- three rounds. shift is by_pixel(0, 6.75), which puts the plate's front skirt
-- on the footprint's near edge; vanilla's assembling machine anchors its own low
-- plate the same way, at by_pixel(0, 4).
local BT = "__space-age-extended__/graphics/entity/bed-tender/"
tender.graphics_set =
{
  animation =
  {
    layers =
    {
      {
        filename = BT .. "base.png",
        priority = "high",
        width = 224,
        height = 189,
        shift = { 0, 0.21094 },        -- by_pixel(0, 6.75) at scale 0.5
        scale = 0.5
      },
      {
        filename = BT .. "base-shadow.png",
        priority = "high",
        draw_as_shadow = true,
        -- The shadow leans up and to the right, so it is wider than the colour
        -- plate and carries its own x shift; both come out of
        -- tools/process-building-art.py rather than being chosen.
        width = 363,
        height = 189,
        shift = { 1.08594, 0.21094 },
        scale = 0.5
      }
    }
  },
  -- The harvested crystal, drawn over the collection bin the hub plate leaves
  -- empty, so a bin with something in it differs from one without.
  working_visualisations =
  {
    {
      always_draw = true,
      animation =
      {
        filename = BT .. "bin.png",
        priority = "high",
        width = 224,
        height = 189,
        shift = { 0, 0.21094 },
        scale = 0.5
      }
    }
  }
}

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
    icon = "__space-age-extended__/graphics/icons/bed-tender.png",
    subgroup = "agriculture",
    order = "z[sae]-b[bed-tender]",
    place_result = "sae-bed-tender",
    stack_size = 20,
    weight = 20000
  }
})
