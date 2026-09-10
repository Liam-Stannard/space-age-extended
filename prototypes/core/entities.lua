-- The Core's machinery: what draws the vents, and what tends the beds.

local derive = require("prototypes.derive")

-- The vent pump. A pumpjack with an input fluid box added, because drawing
-- melt costs helium-3 -- the scarce vent throttling the rich one. The engine
-- reports missing_required_fluid when the helium runs out, which is a legible
-- failure the player can read without a wiki.
local pump = table.deepcopy(data.raw["mining-drill"]["pumpjack"])
pump.name = "sae-vent-pump"
pump.icon = "__space-age-extended__/graphics/icons/vent-pump.png"
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
-- Inherited from the pumpjack: 10 pollution a minute. Same reasoning as the Bed
-- Tender above -- the Core tracks no pollutant, so this is a tooltip line about
-- an atmosphere that is not there.
pump.energy_source.emissions_per_minute = nil

-- Only the Core's vents, and only this machine on them. See the note beside the
-- `sae-vent` resource category in resources.lua for what this closes.
pump.resource_categories = { "sae-vent" }

-- Art: four plates, drawn together and split by tools/cut-rotation-strip.py.
--
-- **The four are one machine with its plumbing moved, not four camera angles.**
-- §5 is blunt about it: ask a generator for four viewpoints and it returns a
-- turntable, which is unusable, because Factorio's camera never moves.
--
-- **And the plumbing has to match the prototype, because on this building the
-- pipes are the fluid boxes.** Helium enters the south face and melt leaves the
-- north face, both on the centre tile of their edge (see the fluid boxes above),
-- and the four plates rotate that pair rigidly: north is riser-top/intake-bottom,
-- east is riser-right/intake-left, south is riser-bottom/intake-top, west is
-- riser-left/intake-right. Checked against the declared connections rather than
-- trusted -- a plate whose plumbing disagrees is a building the player plumbs
-- backwards, and the two fluids are not interchangeable.
--
-- **Every scale and shift is measured off the base plate, never off the
-- content.** The pipes stick out further in some views than others, so content
-- centring slides the machine off its own tile in exactly the views whose
-- plumbing hangs furthest over the edge. The cutter fits the BASE SQUARE to
-- 3.000 tiles and centres on it; the four came out at 3.000, 2.969, 2.984 and
-- 2.953 tiles, all at or under the footprint, which is the safe side to miss on.
--
-- The y shifts differ between the axes and that is not a mistake: a riser
-- leaving through the top edge is drawn standing up, so it adds height above the
-- base and pushes the base low in its canvas. North needs a quarter tile of lift
-- where east and west need almost none.
local VP = "__space-age-extended__/graphics/entity/vent-pump/"
local function vp_plate(dir, w, h, sx, sy, sw, sh, ssx)
  return
  {
    layers =
    {
      {
        filename = VP .. "base-" .. dir .. ".png",
        priority = "high",
        width = w, height = h,
        shift = { sx, sy },
        scale = 0.5
      },
      {
        filename = VP .. "base-" .. dir .. "-shadow.png",
        priority = "high",
        draw_as_shadow = true,
        width = sw, height = sh,
        shift = { ssx, sy },
        scale = 0.5
      }
    }
  }
end

-- The one thing that moves: the melt rising and falling in the riser's sight
-- glass, sixteen frames, four directions.
--
-- **Four directions, because the sight port is on the riser.** §6.1 used to say
-- this layer needed one, "because the sight port and flow disc sit on the stack,
-- which does not rotate" -- but the port is on the riser, and the riser is the
-- fluid box, so it is the one part of this building that *must* turn. Measured
-- off the cut plates: the glow sits top-centre in north, right in east, bottom
-- in south, left in west.
--
-- **Sixteen frames, not thirty-two.** The glass is 12 x 29 plate px in the north
-- view -- six by fifteen on screen -- so a rising level has at most sixteen
-- distinct pictures in it. Thirty-two would be sixteen images and sixteen
-- duplicates, which is the arithmetic that cut the Dross Classifier's shake from
-- sixty-four frames to twelve.
--
-- **It is a brightening laid over a lit plate, not a glow lifted out of an unlit
-- one.** That is the opposite of what this mod usually does, and the reason is
-- the building: `split-glow.py` works when the emissive parts are strongly
-- chromatic against near-neutral iron-nickel, and this riser is copper. Every
-- threshold that saved the port took half the riser with it. So the plate keeps
-- its glow and this sheet adds to it -- which is also the truer reading, since a
-- wellhead full of melt is warm whether or not it is pumping. What changes when
-- it runs is how much of the glass is full.
--
--   tools/build-fill-frames.py base-north.png --region 87 29 108 64 \
--       --frames 16 --min-lightness 0.50 --out port-north.png
--
-- **And it is a small gesture, knowingly.** The port is 16.7 % of the building's
-- own box against vanilla's 72-113 %, and the plate is cut, so it cannot grow.
-- It is built because it costs sixteen tiny derived sprites and gives the
-- machine a running-versus-stopped tell it otherwise has none of -- not under any
-- illusion that it carries the read at play zoom. `04-the-core.md` §26 is the
-- standing warning and this is the exception taken with its eyes open.
local function vp_port(dir, w, h, sx, sy)
  return
  {
    filename = VP .. "port-" .. dir .. ".png",
    priority = "high",
    draw_as_glow = true,
    width = w, height = h,
    frame_count = 16, line_length = 8,
    animation_speed = 0.25,        -- the loop in a little over a second
    shift = { sx, sy },
    scale = 0.5
  }
end

derive.own_graphics(pump,
{
  animation =
  {
    north = vp_plate("north", 203, 281,  0.00781, -0.23438, 441, 301, 1.71094),
    east  = vp_plate("east",  248, 198,  0.00000, -0.02344, 420, 218, 1.18750),
    south = vp_plate("south", 202, 265, -0.00781, -0.14844, 427, 285, 1.59375),
    west  = vp_plate("west",  247, 198, -0.01562, -0.02344, 419, 218, 1.17188)
  },
  working_visualisations =
  {
    -- No `always_draw`, so it is drawn only while the pump is working. The
    -- shifts are the port crop's own offset plus the plate's, both measured.
    {
      north_animation = vp_port("north", 21, 35, -0.05469, -1.70313),
      east_animation  = vp_port("east",  24, 28,  1.39062, -0.35156),
      south_animation = vp_port("south", 23, 29, -0.07812,  1.02344),
      west_animation  = vp_port("west",  26, 28, -1.32031, -0.35156)
    }
  }
})

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

-- Five things `tree-plant` brought that describe a tree on Nauvis, all of which
-- survived unnoticed because none of them stops the game loading:
--
--   * `localised_name` was `entity-name.tree`, and a hardcoded localised_name
--     beats the locale file -- so locale/en/strings.cfg said "Kamacite whiskers"
--     and the game said "Tree".
--   * `order` was `a[tree]-c[nauvis]-...`, sorting it among Nauvis's forest.
--     It stays in the `trees` subgroup, because that is what it is, but takes
--     the `z[sae]-` order prefix every other prototype in this mod uses.
--   * `colors` tint each planted instance at random, and vanilla's seven run
--     white plus faint cyan, magenta, yellow, blue, red and green. That is
--     foliage variety; on a single silvery mineral it grows pink and cyan
--     whiskers. Replaced with three neutrals so a bed still varies without
--     changing material.
--   * `agricultural_tower_tint` is what the Bed Tender's crane flashes while
--     handling the crop, inherited as Gleba's yellow-green.
--   * `emissions_per_second` had it absorbing pollution. There is no
--     pollutant on the Core at all -- `pollutant_type` is nil -- so it absorbs
--     nothing anywhere it can be planted.
plant.localised_name = nil
plant.localised_description = nil
plant.order = "z[sae]-a[whisker-plant]"
plant.colors =
{
  { r = 255, g = 255, b = 255 },
  { r = 236, g = 240, b = 245 },
  { r = 245, g = 242, b = 236 }
}
plant.agricultural_tower_tint =
{
  primary = { r = 0.78, g = 0.80, b = 0.85, a = 1 },
  secondary = { r = 0.48, g = 0.50, b = 0.55, a = 1 }
}
plant.emissions_per_second = nil

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
-- Gleba's tower vents 4 spores a minute, which is how its crop spreads. This
-- one is locked to the Core, where `pollutant_type` is nil and nothing is
-- tracked -- so the figure does nothing but sit in the tooltip claiming the
-- machine seeds the air of a world that has none.
tender.energy_source.emissions_per_minute = nil

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
