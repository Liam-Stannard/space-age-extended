-- N8. The Gas Pump, the siderane vent it stands on, and the turbine that burns
-- what it draws.
--
-- concept/crust-tap/building-spec-crust-tap.md, §A. The largest of the nine,
-- because it is not one prototype: it is a fluid, a vent resource, the pump and
-- a companion generator.
--
-- **This is the Core's landing-day power**, and it should stay small: a foothold,
-- not a power strategy. A player who builds fifty pumps should still find the
-- melt-and-steam line the better answer by a wide margin, or the Core's central
-- tension is undercut by its own tutorial.
--
-- **One pump for every gas, on vents that run down.** Siderane used to come up
-- through an offshore pump standing on a vent *tile*, and a tile holds no
-- amount, so it never ran down; helium-3 came through the Vent Pump. Both now
-- come through the Gas Pump, a `mining-drill` as the pumpjack is, standing on
-- vent *resources* in the `sae-gas` category. Depletion belongs to the resource,
-- as an oil field's does: the engine slows a vent as it is drawn and reports
-- `no_minable_resources` with no script. A future gas costs a resource and a
-- fluid, and no new machine. The Vent Pump keeps the kamacite vent, alone.
--
-- Two measurements from spike S10 and one engine change shape the turbine, and
-- all three are the kind that pass every check in the repo while being wrong:
--
--   1. **`burns_fluid` ignores temperature entirely**, taking its power from the
--      fluid's `fuel_value`. Measured: a turbine burning gas at 25 degrees with
--      `fuel_value = "200kJ"` produced exactly its declared 1.80 MW under load.
--      That is why the gas needs no temperature and the pump never declares
--      one: a steam turbine wants 500 degrees, and nothing here is that hot.
--
--   2. **`maximum_temperature` is mandatory on a generator even so.** Leaving it
--      out fails the data stage outright. It does no work in this mode; it still
--      has to be declared.
--
--   3. **`minimum_input_temperature` has to be cleared.** Factorio 2.1.22 gave
--      the vanilla steam turbine a 100-degree minimum, and the turbine derives
--      from it: inherited, a minimum stops a generator taking any fluid below
--      it, so 25-degree gas would never burn. Unset, there is no minimum.
--
-- Proven end to end on the rig, because none of it is visible from the data
-- stage: a pump on a vent, piped to a turbine, under load, produced the declared
-- 1.8 MW with no electric network anywhere on the surface.
--
-- And one that is about the *test* rather than the building: `can_place_entity`
-- defaults to a lenient check, which is not how a player builds. Anything testing
-- where this pump may stand has to pass `build_check_type = manual`, or it is
-- not testing the rule.

local item_sounds = require("__base__.prototypes.item_sounds")
local tile_sounds = require("__base__.prototypes.tile.tile-sounds")
local resource_autoplace = require("resource-autoplace")

local derive = require("prototypes.derive")
-- Defines the `circuit_connector_definitions` and `universal_connector_template`
-- globals the pump's wire post is built from, as base's own entities file does.
require("circuit-connector-sprites")

--------------------------------------------------------------------------------
-- The gas.
--
-- No temperature anywhere, by design -- see the burns_fluid note above. The
-- fuel value is what the turbine reads, and it is the number that sets the
-- foothold's size.
--------------------------------------------------------------------------------

data:extend({
  {
    type = "fluid",
    name = "sae-crust-gas",
    icon = "__space-age-extended__/graphics/icons/fluid/siderane.png",
    subgroup = "fluid",
    order = "z[sae]-e[crust-gas]",
    default_temperature = 25,
    -- Chartreuse, #A8D82A (Liam, 2026-10-09): no vanilla fluid and no other in
    -- this mod is a bright yellow-green, so siderane reads as itself in a pipe
    -- and in the Gas Pump's sight glass. The ochre it had sank into the brown
    -- steel round it.
    base_color = { r = 0.66, g = 0.85, b = 0.16 },
    flow_color = { r = 0.82, g = 0.95, b = 0.50 },
    fuel_value = "200kJ",
    auto_barrel = false
  }
})

--------------------------------------------------------------------------------
-- The siderane vent.
--
-- A resource, as crude oil is, and for crude oil's reason: an amount that falls
-- as it is drawn. `infinite`, so it never quite stops -- `minimum` is the floor
-- a drawn-out vent settles at, crude oil's own fifth of `normal`, so an old vent
-- still turns a turbine at a fifth of its speed. The landing's power fades into
-- a trickle rather than going dark, and the player has a reason to move on to
-- the melt line.
--
-- **The yield is read against `normal`.** A vent holding exactly `normal` gives
-- 9 siderane a second to a pump of mining speed 1 -- one 9-unit cycle a second,
-- which is exactly one Siderane turbine's burn, 1.8 MW -- and a vent at
-- `minimum` gives 1.8. One vent, one turbine: the landing's power is counted in
-- vents. `normal` and `minimum` are crude oil's, so the fade takes as long as an
-- oil field's: ten per cycle off the amount, some six and a half hours of one
-- pump to reach the floor.
--
-- **And the vents are thin**, as crude oil's are, so that count stays a
-- foothold. The landing gets a field of four wells, every one between 40 and 56
-- tiles from spawn and every one holding exactly `normal`; beyond 150 tiles
-- there are crude oil's scattered patches, thinned by `random_probability`.
-- The first build, at the other vents' density, put 13 in one starting patch.
--
-- 2x2, under the pump that draws it.
--
-- **The sprite is the helium-3 vent's**, crude oil's sheet, tinted toward the
-- gas's own chartreuse, and the map colour is the helium vent's turned the same way.
-- Both are the gas vent's stand-ins until a vent of the Core's own is drawn.
--------------------------------------------------------------------------------

data:extend({
  { type = "autoplace-control", name = "sae-crust-vent", category = "resource", richness = true, order = "z[sae]-bb" }
})

local vent_sheet = table.deepcopy(data.raw.resource["crude-oil"].stages.sheet)
vent_sheet.tint = { r = 0.85, g = 1.0, b = 0.45 }

-- STARTING_FIELD: the landing's own wells, by offset from the field's centre in
-- tiles. Each is one vent: wells are at least five tiles apart, so two never
-- touch, and a vent is 2x2, so a well never holds two.
local STARTING_FIELD = { { 0, 0 }, { 5, -3 }, { -2, 5 }, { 6, 4 } }
-- How far out the field's centre sits. The wells spread up to eight tiles round
-- it, so every one lands between 40 and 56 tiles from spawn: clear of the
-- landing spot, as vanilla keeps its starting ore 40 out, and inside 64.
local STARTING_REACH = 48
-- How many bearings the field tries round the compass.
local BEARINGS = 16

do
  -- **Vanilla's starting patch could not be used.** It lands anywhere from 40
  -- to 150 tiles out and does not know the radiant pool is there: measured over
  -- twelve seeds it put none inside 64 tiles on one, six on another, and dropped
  -- a whole patch into the pool. So the field reads the basin term
  -- (map-gen.lua) at sixteen bearings and stands at the driest -- the one
  -- furthest above the pool. On most maps every bearing is dry and the choice
  -- is the terrain's; on a map whose landing is nearly an island it is the
  -- only way out of the water. The bearings start from the map seed's, so on a
  -- flat map the field still moves from map to map.
  local function bearing(k)
    return string.format("(2 * pi * (map_seed_normalized + %d / %d))", k, BEARINGS)
  end
  local locals = {}
  for k = 0, BEARINGS - 1 do
    locals["v" .. k] = string.format("sae_core_basin_at{px = %d * cos(%s), py = %d * sin(%s), reach = %d}",
      STARTING_REACH, bearing(k), STARTING_REACH, bearing(k), STARTING_REACH)
    if k == 0 then
      locals.best0 = "v0"
      locals.pick0 = bearing(0)
    else
      locals["best" .. k] = string.format("max(best%d, v%d)", k - 1, k)
      locals["pick" .. k] = string.format("if(v%d > best%d, %s, pick%d)", k, k - 1, bearing(k), k - 1)
    end
  end
  local terms, extent = {}, 0
  for i, w in ipairs(STARTING_FIELD) do
    -- The furthest well's centre from the field's, plus the 2x2 vent's half.
    extent = math.max(extent, math.sqrt(w[1] ^ 2 + w[2] ^ 2) + 1)
    local wx = string.format("((%d) * cos(b) - (%d) * sin(b) + %d * cos(b))", w[1], w[2], STARTING_REACH)
    local wy = string.format("((%d) * sin(b) + (%d) * cos(b) + %d * sin(b))", w[1], w[2], STARTING_REACH)
    terms[i] = string.format("(abs(x - %s) < 1) * (abs(y - %s) < 1)", wx, wy)
  end
  data:extend({
    {
      -- The field's bearing, in radians, as its own expression, with its
      -- distance and how far its wells spread round its centre: the other
      -- starting patches (map-gen.lua) take their bearings from this one and
      -- keep clear of the field by the other two.
      type = "noise-expression",
      name = "sae_crust_vent_bearing",
      expression = "pick" .. (BEARINGS - 1),
      local_expressions = locals
    },
    { type = "noise-expression", name = "sae_crust_vent_reach", expression = STARTING_REACH },
    { type = "noise-expression", name = "sae_crust_vent_extent", expression = extent },
    {
      type = "noise-expression",
      name = "sae_crust_vent_start",
      -- And never in the pool or on its shore, well by well: the pool's tiles
      -- refuse a resource outright, and the shore is where the solution is drawn.
      expression = "(sae_core_basin > 92) * min(1, " .. table.concat(terms, " + ") .. ")",
      local_expressions = { b = "sae_crust_vent_bearing" }
    }
  })
end

-- Everything else is crude oil's way: patches of scattered wells, thinned by
-- `random_probability`, and none of them inside the starting area -- with
-- `has_starting_area_placement = false` they fade in from 150 tiles out.
local regular = resource_autoplace.resource_autoplace_settings
{
  name = "sae-crust-vent",
  order = "d",
  base_density = 0.8,
  random_probability = 1 / 10,
  random_spot_size_minimum = 1,
  random_spot_size_maximum = 1,
  additional_richness = 300000,
  has_starting_area_placement = false
}
local on = "(var('control:sae-crust-vent:size') > 0)"
local vent_autoplace =
{
  -- Placed before every other resource, so the kamacite's starting patch
  -- cannot take a well's ground: measured, it took two of four on one seed.
  -- Resources earlier in this order win the ground they share.
  order = "a",
  probability_expression = "max(" .. regular.probability_expression .. ", " .. on .. " * sae_crust_vent_start)",
  -- A starting well holds exactly `normal`, so the landing's pumps each run
  -- at the full 9 a second; the patches beyond hold what crude oil's do.
  richness_expression = "if(sae_crust_vent_start > 0, " .. on ..
    " * var('control:sae-crust-vent:richness') * 300000, " .. regular.richness_expression .. ")"
}

local crust_vent =
{
  type = "resource",
  name = "sae-crust-vent",
  icon = "__space-age-extended__/graphics/icons/fluid/siderane.png",
  flags = { "placeable-neutral" },
  category = "sae-gas",
  subgroup = "mineable-fluids",
  order = "z[sae]-bb[crust-vent]",
  infinite = true,
  -- A vent is one well, not a field of tiles, so it is not snapped to the
  -- resource grid -- as crude oil is not.
  map_grid = false,
  highlight = true,
  minimum = 60000,
  normal = 300000,
  infinite_depletion_amount = 10,
  resource_patch_search_radius = 12,
  tree_removal_probability = 1,
  tree_removal_max_distance = 32 * 32,
  minable =
  {
    mining_time = 1,
    results =
    {
      { type = "fluid", name = "sae-crust-gas", amount = 9 }
    }
  },
  walking_sound = tile_sounds.walking.oil({}),
  driving_sound = tile_sounds.driving.oil,
  collision_box = { { -0.9, -0.9 }, { 0.9, 0.9 } },
  selection_box = { { -1, -1 }, { 1, 1 } },
  autoplace = vent_autoplace,
  stage_counts = { 0 },
  stages = { sheet = vent_sheet },
  map_color = { r = 0.66, g = 0.85, b = 0.16 },
  -- The colour the Gas Pump's sight glass shows while it draws from this vent:
  -- siderane's own chartreuse, its `base_color` above.
  mining_visualisation_tint = { r = 0.66, g = 0.85, b = 0.16 }
}
-- Marked, as the vent tile it replaces was: vanilla's sheet, until the Core's
-- own vent is drawn.
derive.placeholder_art(crust_vent, "wears crude oil's resource sheet, tinted, until its own exists")
data:extend({ crust_vent })

--------------------------------------------------------------------------------
-- The pump.
--
-- From the pumpjack, because the pumpjack is the vanilla machine that draws a
-- fluid out of a resource: an output fluid box and no input, and nothing for
-- `vector_to_place_result` to place, since nothing it makes is an item. It
-- takes the `sae-gas` category alone, so it stands on a gas vent and nowhere
-- else -- not on bare ground, and not on the kamacite vent, which is the Vent
-- Pump's.
--
-- **No power at all: a `void` energy source.** The landing has no grid until
-- this pump and its turbine are running, so the pump cannot need one.
--------------------------------------------------------------------------------

local pump = derive.from("mining-drill", "pumpjack", "sae-gas-pump")
pump.icon = "__space-age-extended__/graphics/icons/gas-pump.png"
pump.icon_size = 64
pump.minable = { mining_time = 0.3, result = "sae-gas-pump" }
pump.resource_categories = { "sae-gas" }
pump.collision_box = { { -0.9, -0.9 }, { 0.9, 0.9 } }
pump.selection_box = { { -1, -1 }, { 1, 1 } }
pump.mining_speed = 1
-- The burner drill's reach, the four tiles under the pump, and not the
-- pumpjack's 0.49. **Measured, not assumed:** the engine places every resource
-- at a tile centre, a 2x2 vent included, while a 2x2 machine's centre is a tile
-- corner -- so the pumpjack's half-tile reach from that corner contains no tile
-- centre at all, and a pump built over a vent found nothing to mine. A drill
-- finds a resource by its position, so this reach takes the vent under any one
-- of the pump's four tiles. Vents are 2x2 and never overlap, so it never takes
-- two.
pump.resource_searching_radius = 0.99
-- Nothing it makes is an item, so nothing is placed; but the field is
-- mandatory on a mining drill (the data stage refuses the pump without it), so
-- it stays at the pumpjack's own inert { 0, 0 }.
pump.vector_to_place_result = { 0, 0 }
pump.module_slots = 0
-- And no beacons either, so nothing but the vent sets the rate: a fresh vent is
-- one turbine's burn and no more. Mining productivity research still applies.
pump.effect_receiver = { uses_module_effects = false, uses_beacon_effects = false }
pump.energy_source = { type = "void" }
pump.surface_conditions = { { property = "gravity", min = 45 } }
pump.max_health = 150
-- The pumpjack is 3x3 and its rubble, explosion and wire post are placed for
-- that. A 2x2's rubble, vanilla's 2x2 drill's explosion, and a connector on the
-- near corner as the accumulator's is.
pump.corpse = "medium-small-remnants"
pump.dying_explosion = "burner-mining-drill-explosion"
pump.circuit_connector = circuit_connector_definitions.create_vector(
  universal_connector_template,
  {
    { variation = 26, main_offset = util.by_pixel(18.5, 19), shadow_offset = util.by_pixel(20.5, 25.5), show_shadow = true },
    { variation = 26, main_offset = util.by_pixel(18.5, 19), shadow_offset = util.by_pixel(20.5, 25.5), show_shadow = true },
    { variation = 26, main_offset = util.by_pixel(18.5, 19), shadow_offset = util.by_pixel(20.5, 25.5), show_shadow = true },
    { variation = 26, main_offset = util.by_pixel(18.5, 19), shadow_offset = util.by_pixel(20.5, 25.5), show_shadow = true }
  }
)
-- A gas pump hisses rather than nods: the offshore pump's sounds, which this
-- building wore when it was one, in place of the nodding donkey's.
do
  local offshore = data.raw["offshore-pump"]["offshore-pump"]
  pump.working_sound = table.deepcopy(offshore.working_sound)
  pump.open_sound = table.deepcopy(offshore.open_sound)
  pump.close_sound = table.deepcopy(offshore.close_sound)
end
-- One connection, on a tile centre. On a 2x2 the middle of a face is the seam
-- between two tiles and a pipe connects to nothing there, so the outlet sits at
-- { 0.5, -0.5 } and rotates with the building round the four tile centres, as
-- §24's table gives: east { 0.5, 0.5 }, south { -0.5, 0.5 }, west
-- { -0.5, -0.5 }. The pumpjack's corner-walking `positions` list goes.
pump.input_fluid_box = nil
pump.output_fluid_box = {
  volume = 1000,
  pipe_covers = pump.output_fluid_box.pipe_covers,
  pipe_connections = {
    { flow_direction = "output", direction = defines.direction.north, position = { 0.5, -0.5 } }
  }
}
-- Art: the Gas Pump's Blender model (concept/crust-tap/model/crust_tap.py,
-- signed off by Liam 2026-10-09 after its "bulkier" round, and its pumping
-- animation 2026-10-10, round a2): a square pump casing in faded green with its
-- corners cut, on a plinth held by corner anchors; a flat riveted lid carrying
-- the wellhead and a compressor housing; orthogonal pipework, hoses and cables
-- over it; the burst disc; a sight glass inline in the lid's header; and the
-- riser. Ours, so no `derive.placeholder_art`.
--
-- FOUR DIRECTIONS, RENDERED FROM ONE MODEL, because on this building the riser
-- is the fluid box and a riser pointing the wrong way is the fluid box in the
-- wrong place. Only the riser turns; everything else is the same in all four,
-- and the riser's mouth sits on the connection above by construction.
--
-- **The riser sits on a TILE CENTRE, half a tile off the middle of its face.**
-- That is the correction §24 records, and the model agrees with the connection
-- above in all four rotations.
--
-- Each direction is three layers and a glass:
--
--   - the plate, the casing less its moving parts, one frame repeated to the
--     stroke's 24 -- vanilla's biochamber arrangement, as the Ballast Drill's;
--   - the pump layer, the crank wheel, the piston rod it drives and the gauge
--     needle that swings with each stroke, 24 frames of one stroke;
--   - the shadow, one frame repeated. The parts that move are small against
--     the shadow and it is not split to follow them;
--   - the sight glass's contents, below, 24 frames of gas moving in the glass.
--
-- Every size, shift, frame count and line length below is copied from the
-- model's sheets/meta.json; none was measured off a sheet or typed from
-- memory. Each file is named whole so tools/collect-graphics-refs.py can see it.
--
-- **`animation_speed` is 0.4, and the engine plays 0.4**: 24 frames over 60
-- ticks, one stroke a second. A drill is not a crafting machine:
-- `MiningDrillGraphicsSet::animation_progress` defaults to 1 (prototype docs,
-- doc-html/types/MiningDrillGraphicsSet.html), and the declared rate is not
-- multiplied by `mining_speed` -- the Ballast Drill's measurement, in
-- machines.lua. Measured on this pump in a client on the Core, 2026-10-10,
-- one screenshot a tick matched against the strip: 144 frames over 360 ticks
-- on a siderane vent and on a helium vent, 0.400 frames a tick, a 60-tick
-- stroke, with the glass on the pump layer's frame in every one of the 720.
--
-- **Idle, the crank stops where it is**, as the pumpjack's horsehead does. The
-- pumpjack draws its nodding head in `graphics_set.animation` with no
-- `idle_animation` (base/prototypes/entity/mining-drill.lua,
-- `pumpjack_animation`), and so does this: the engine draws `animation` every
-- tick at the frame its own progress counter has reached, and advances that
-- counter only on ticks the drill works. Stopped, the counter stops, and the
-- frame holds. The prototype docs do not spell this out; the pumpjack is the
-- reference, and it was measured here too: a pump whose outlet was shut mid
-- stroke stopped on frame 20 of 24 and held it, and its glass faded out over
-- some fifteen ticks. `reset_animation_when_frozen` (default false) sits
-- beside `frozen_patch`, the frost a drill wears on Aquilo; it is about
-- freezing, not idling, and is left alone.
local GP = "__space-age-extended__/graphics/entity/gas-pump/"
local GP_FRAMES = 24
local GP_SPEED = 0.4           -- 0.4 in game: drill progress is 1, one stroke a second

-- One frame, repeated to the stroke's length, so every layer of the animation
-- has the same frame count, as the engine requires.
local function gp_still(filename, width, height, shift)
  return
  {
    filename = filename,
    priority = "high",
    width = width, height = height,
    frame_count = 1,
    repeat_count = GP_FRAMES,
    animation_speed = GP_SPEED,
    shift = shift,
    scale = 0.5
  }
end

-- A 24-frame strip, one row.
local function gp_strip(filename, width, height, shift)
  return
  {
    filename = filename,
    priority = "high",
    width = width, height = height,
    frame_count = GP_FRAMES,
    line_length = GP_FRAMES,
    animation_speed = GP_SPEED,
    shift = shift,
    scale = 0.5
  }
end

-- The plate, the moving parts over it, and the plate's shadow.
local function gp_direction(base, pump_layer, shadow)
  shadow.draw_as_shadow = true
  return { layers = { base, pump_layer, shadow } }
end

-- The sight glass's contents: neutral white, so the engine's tint decides its
-- colour. meta.json gives all four directions the same 21 x 18 and the same
-- shift, since the glass is on the part of the model that does not turn.
local function gp_glass(filename)
  return gp_strip(filename, 21, 18, { -0.13281, -0.75 })
end

-- The pumpjack's set is replaced whole: its nodding head and its working
-- visualisations, and the mirrored copy of both, describe a machine this is not.
derive.own_graphics(pump, {
  animation = {
    north = gp_direction(gp_still(GP .. "base-north.png", 134, 152, { 0.0, -0.15625 }),
                         gp_strip(GP .. "pump-north.png", 69, 50, { 0.47656, -0.21875 }),
                         gp_still(GP .. "base-shadow-north.png", 174, 134, { 0.35938, -0.03125 })),
    east = gp_direction(gp_still(GP .. "base-east.png", 135, 138, { 0.00781, -0.04688 }),
                        gp_strip(GP .. "pump-east.png", 69, 48, { 0.47656, -0.23438 }),
                        gp_still(GP .. "base-shadow-east.png", 174, 131, { 0.35938, -0.00781 })),
    south = gp_direction(gp_still(GP .. "base-south.png", 134, 139, { 0.0, -0.03906 }),
                         gp_strip(GP .. "pump-south.png", 69, 50, { 0.47656, -0.21875 }),
                         gp_still(GP .. "base-shadow-south.png", 174, 137, { 0.35938, 0.03906 })),
    west = gp_direction(gp_still(GP .. "base-west.png", 135, 138, { -0.00781, -0.04688 }),
                        gp_strip(GP .. "pump-west.png", 69, 50, { 0.47656, -0.21875 }),
                        gp_still(GP .. "base-shadow-west.png", 174, 131, { 0.35938, -0.00781 }))
  },
  working_visualisations = {
    -- **The sight glass shows the gas.** In the plate it is dark, empty glass;
    -- while the pump is drawing, this fills it with the colour of what is
    -- drawn, moving over the stroke's 24 frames at the stroke's rate, in step
    -- with the crank. `apply_tint = "resource-color"` takes
    -- the colour from the vent under the pump -- its `mining_visualisation_tint`
    -- -- so one layer shows siderane chartreuse on a siderane vent and
    -- helium-3 blue on a helium vent, and a future gas needs only its vent's
    -- tint.
    --
    -- Ordinary paint, not glow and no light: it is gas seen through glass, not
    -- a lamp, and it should go dark at night with the rest of the machine.
    -- (meta.json's `kind = "light"` is the render pipeline's name for a white
    -- layer the engine tints, not a request for `draw_as_glow`.)
    --
    -- No `always_draw`, so it is drawn only while the pump is working; idle,
    -- blocked, unconnected or with no vent under it, the plate's empty glass
    -- shows.
    --
    -- **`synced_fadeout`, not `fadeout`**, because that is what vanilla's big
    -- mining drill sets on both of its `resource-color` layers, its tinted dust
    -- and its output particles (space-age/prototypes/entity/big-mining-drill.lua),
    -- and the glass is drawn as the big drill draws its tinted layers. The
    -- prototype docs describe neither flag; the electric drill uses plain
    -- `fadeout` on its own tinted dust.
    {
      synced_fadeout = true,
      apply_tint = "resource-color",
      north_animation = gp_glass(GP .. "sight-glass-north.png"),
      east_animation = gp_glass(GP .. "sight-glass-east.png"),
      south_animation = gp_glass(GP .. "sight-glass-south.png"),
      west_animation = gp_glass(GP .. "sight-glass-west.png")
    }
  }
})
pump.graphics_set_flipped = nil
pump.use_mirroring = nil
pump.migrate_horizontal_mirroring = nil
-- **The covers stay.** The plate draws its own mouth, which says what the
-- fitting looks like; the cover says what an *unused* one looks like, and
-- `always_draw_covers` being false means it is gone the moment a pipe is
-- actually joined. Every vanilla machine carries both, the foundry included,
-- and a pump on a vent with nothing plumbed to it is exactly the case the cover
-- exists for.
pump.output_fluid_box.always_draw_covers = false
pump.output_fluid_box.pipe_picture = util.empty_sprite()
data:extend({ pump })


--------------------------------------------------------------------------------
-- The turbine.
--
-- `burns_fluid`, so it reads the gas's `fuel_value` and ignores temperature --
-- see the S10 note at the top. Filtered to crust gas alone: it is not a general
-- fluid burner, and letting it take anything with a fuel value would make it a
-- better answer than the melt line it is meant to be worse than.
--------------------------------------------------------------------------------

local turbine = derive.from("generator", "steam-turbine", "sae-crust-turbine")
turbine.icon = "__space-age-extended__/graphics/icons/crust-turbine.png"
turbine.icon_size = 64
turbine.minable = { mining_time = 0.3, result = "sae-crust-turbine" }
turbine.burns_fluid = true
turbine.max_power_output = "1800kW"
turbine.effectivity = 1
turbine.fluid_usage_per_tick = 0.15 -- 9/s at 200 kJ = 1.8 MW
-- Mandatory even with burns_fluid, where it does nothing at all. Omitting it
-- fails the data stage with `Key "maximum_temperature" not found`.
turbine.maximum_temperature = 1000
-- Inherited from the 2.1.22 steam turbine, it would refuse the gas -- note 3.
turbine.minimum_input_temperature = nil
turbine.surface_conditions = { { property = "pressure", max = 9 } }
turbine.fluid_box = table.deepcopy(turbine.fluid_box)
turbine.fluid_box.filter = "sae-crust-gas"
turbine.fluid_box.volume = 200
-- Art: the Siderane turbine's Blender model
-- (concept/crust-turbine/model/crust_turbine.py, round 2, signed off by Liam
-- 2026-10-11): a long low body on the 3x5, three machined collars -- each end
-- one with its stub out to the middle of its end tile's edge, flanged except
-- at the south end lying north-south, where the stub is bare and its collar
-- cut back -- the rotor window in the middle one, the let-down housing with
-- its high and low gauge at one end, and the generator can with its three
-- porcelain bushings at the other. Ours, so no `derive.placeholder_art`.
--
-- **Rendered, not cut**, as the Gas Pump is: every pass comes off one model
-- through one calibrated camera on one canvas with the entity origin at its
-- centre, so the layers register by construction. Every size, shift, frame
-- count and line length below is copied from the model's sheets/meta.json;
-- none was measured off a sheet or typed from memory. To regenerate, with any
-- Blender 5 binary:
--
--   BLENDER=<blender> tools/blender/render.sh \
--       concept/crust-turbine/model/crust_turbine.py <scratch> --icon
--
-- then copy <scratch>/sheets/icon.png to graphics/icons/crust-turbine.png, the
-- other <scratch>/sheets/*.png into graphics/entity/crust-turbine/, and the
-- numbers out of meta.json into this block.
--
-- **Two directions, as the steam turbine's.** A generator's art is
-- `pictures`, one Animation per direction (GeneratorPictureSet, Factorio
-- 2.1.21 -- it has no `horizontal_animation`, `vertical_animation` or
-- `graphics_set`), and the steam turbine's `two_direction_only` is kept, so
-- `north` is the machine lying north-south (the let-down end south) and `east`
-- lying east-west (the let-down end west). A turbine built facing south or
-- west is built facing north or east: in a client, all four came back as
-- north, east, north, east, and each generated.
--
-- **The fluid boxes are the steam turbine's, and so are the covers.** Both
-- connections are on the long axis, at {0, -2} and {0, 2}, and the model drew
-- its two stubs to meet a vanilla pipe on those tiles; the covers are
-- vanilla's, capping an end with nothing joined to it. **Each end is a
-- pipe-width spigot reaching the footprint's edge**, so a pipe run into either
-- end meets turbine metal across its whole width (Liam, 2026-10-11: a neck
-- thinner than the pipe left ground showing either side of every join, and
-- that was a fail). Measured off the plates, 64 px a tile from the origin:
-- lying east-west, each spigot is 58 px tall and its flange 66, on the pipe's
-- axis 1 px above the centre, against vanilla's 52 px pipe ring; lying
-- north-south, the north spigot is 52 px wide and its flange 58 end-on, and
-- the south end, as the steam turbine's, has no flange (Liam, 2026-10-11: a
-- square flange wider than the pipe showed either side of its ring): a bare
-- stub the vanilla pipe body's width, 41 px, opaque across x -19 to 21 on
-- every row from y 138 to 153, half-covered on the column either side, then
-- rounding off to its end face past the footprint's edge (y 160), its last
-- row y 165, against the pipe's 51 px end ring.
--
-- Each direction is three layers, and one more behind TURBINE_LENS_LIT:
--
--   - the plate, the machine less its rotor, one frame repeated to the rotor's
--     8, so every layer has the same frame count, as the engine requires;
--   - the rotor, behind the middle collar's window: 8 frames through one vane
--     pitch, so the loop closes on itself;
--   - the shadow, one frame repeated. The rotor turns in place under a collar
--     and casts nothing that moves;
--   - the status lens's white cut, below.
--
-- **What moves: the rotor, and only while it generates.** A generator's
-- animation is drawn in every state and advanced only on ticks it makes power,
-- so stopped it holds whichever frame it reached -- with no load as well as
-- with no gas: a turbine full of gas on a grid that draws nothing reports
-- `working` and does not turn.
--
-- **`animation_speed` is 1/3, the review GIF's rate** (rotor.gif, 50 ms a
-- frame: 20 frames a second, a third of a frame a tick). **In game that is the
-- rate at full output and no more:** a generator's animation speed "can often
-- vary depending on the usage (output of steam engine for example)"
-- (AnimationParameters::animation_speed, doc-html/types/
-- AnimationParameters.html), scaled by `perceived_performance` ("affects
-- animation speed and working sound", GeneratorPrototype), which keeps the
-- steam turbine's { minimum = 0.25, performance_to_activity_rate = 2 }: the
-- rate follows output, but never drops below a quarter of full while it makes
-- any power at all. Measured in a client on the Core, 2026-10-11, one
-- screenshot a tick matched against the strip, 120 ticks each: 1.8 MW, 0.336
-- frames a tick in both directions (a vane pitch in 24 ticks); 0.9 MW, 0.160;
-- 90 kW (a twentieth), 0.084, the quarter floor; fed and on a grid drawing
-- nothing, 0; no gas, 0.
local CT = "__space-age-extended__/graphics/entity/crust-turbine/"
local CT_FRAMES = 8
local CT_SPEED = 1 / 3         -- the review GIF's rate, reached at full output
-- **The status lens: unlit, for now; Liam decides.** §3.3 asks for a lens the
-- engine tints, and a generator has nothing to tint it with: no working
-- visualisations, no status colours, nothing drawn by state (GeneratorPictures
-- is `animation` and `frozen_patch` alone). The plate already carries the lens
-- as unlit glass, so false draws nothing more. True adds the model's white cut
-- as a `draw_as_glow` layer in the animation -- untinted, and lit in every
-- state, idle included, because the animation it sits in is always drawn.
local TURBINE_LENS_LIT = false

-- One frame, repeated to the rotor's length.
local function ct_still(filename, width, height, shift)
  return
  {
    filename = filename,
    priority = "high",
    width = width, height = height,
    frame_count = 1,
    repeat_count = CT_FRAMES,
    animation_speed = CT_SPEED,
    shift = shift,
    scale = 0.5
  }
end

-- The rotor: an 8-frame strip, one row.
local function ct_strip(filename, width, height, shift)
  return
  {
    filename = filename,
    priority = "high",
    width = width, height = height,
    frame_count = CT_FRAMES,
    line_length = CT_FRAMES,
    animation_speed = CT_SPEED,
    shift = shift,
    scale = 0.5
  }
end

-- The plate, the rotor over it, the plate's shadow, and the lens if lit.
local function ct_direction(base, rotor, shadow, lens)
  shadow.draw_as_shadow = true
  local layers = { base, rotor, shadow }
  if TURBINE_LENS_LIT then
    lens.draw_as_glow = true
    layers[#layers + 1] = lens
  end
  return { animation = { layers = layers } }
end

derive.own_graphics(turbine, {
  north = ct_direction(ct_still(CT .. "base-vertical.png", 164, 360, { -0.23438, -0.20312 }),
                       ct_strip(CT .. "rotor-vertical.png", 71, 64, { 0.08594, -0.46875 }),
                       ct_still(CT .. "base-shadow-vertical.png", 192, 340, { 0.01562, 0.17188 }),
                       ct_still(CT .. "status-lens-vertical.png", 10, 10, { -0.71875, -0.60938 })),
  east = ct_direction(ct_still(CT .. "base-horizontal.png", 328, 197, { 0.0, -0.05469 }),
                      ct_strip(CT .. "rotor-horizontal.png", 58, 55, { -0.01562, -0.32031 }),
                      ct_still(CT .. "base-shadow-horizontal.png", 350, 168, { 0.39062, 0.15625 }),
                      ct_still(CT .. "status-lens-horizontal.png", 10, 10, { 0.0, -1.10938 }))
}, "pictures")

-- **Its wreck, and how it goes.** The steam turbine's corpse and explosion
-- rode along with `derive.from` (derive.lua keeps both on purpose), so the
-- Siderane turbine died into the steam turbine's rubble. It has its own now,
-- each written after its vanilla counterpart.
--
-- The wreck is the model's remnants pass (T02c, signed off by Liam 2026-10-20),
-- one sheet of four rows -- lying north-south, east-west, north-south,
-- east-west -- because a rotated animation's four directions are north, east,
-- south and west, and a turbine built south or west is built north or east.
-- Size, shift and layout are copied from
-- concept/crust-turbine/model/remnants/sheets/meta.json; regenerate with the
-- turbine's command above and copy sheets/remnants.png here. The shadow is
-- baked in, as vanilla's is, so it is one layer. Everything else mirrors
-- steam-turbine-remnants (base/prototypes/entity/remnants.lua): the 3x5
-- footprint, fifteen minutes on the ground, and left in place under a tile.
-- Both are named as vanilla names its own, "<the building> (remnant)" and
-- "(dying explosion)" from core's locale, by the turbine's own entity-name key,
-- so strings.cfg needs nothing new.
local turbine_remnants =
{
  type = "corpse",
  name = "sae-crust-turbine-remnants",
  localised_name = { "remnant-name", { "entity-name.sae-crust-turbine" } },
  icon = "__space-age-extended__/graphics/icons/crust-turbine.png",
  icon_size = 64,
  flags = { "placeable-neutral", "not-on-map" },
  hidden_in_factoriopedia = true,
  subgroup = "energy-remnants",
  order = "a-h-a-z[sae-crust-turbine]",
  selection_box = { { -1.5, -2.5 }, { 1.5, 2.5 } },
  tile_width = 3,
  tile_height = 5,
  selectable_in_game = false,
  time_before_removed = 60 * 60 * 15, -- 15 minutes
  expires = false,
  final_render_layer = "remnants",
  remove_on_tile_placement = false,
  animation =
  {
    filename = CT .. "remnants.png",
    line_length = 1,
    width = 325,
    height = 326,
    direction_count = 4,
    shift = { -0.02344, 0.01562 },
    scale = 0.5
  }
}

-- **Vanilla metal and fire, sparks, no smoke** (Liam, 2026-10-20: "Vanilla
-- metal, no smoke", then "Yes, no smoke at all"; sparks in place of the
-- fireball, and then, from the T06 shots, "I think we should add the
-- explosion, the core has a small atmosphere if pressure >0": "Fireball +
-- sparks, no smoke"). The steam turbine's own explosion -- its fireball, its
-- sound and its shower of metal and machine parts -- with sparks thrown in
-- and every wisp of smoke taken out.
--
--   * **No smoke.** The explosion's `smoke-fast` puffs go, and so do the
--     wisps the big and medium metal pieces trail as they fly (their
--     `regular_trigger_effect`, base/prototypes/particles.lua): those two fly
--     as copies of our own with the trail struck off. Smoke is struck by
--     field and by effect type, so one vanilla adds later goes too.
--   * **The fireball stays**, vanilla's medium explosion: the Core has a
--     small atmosphere wherever its pressure is above 0, so a flash of fire
--     is fair even where smoke is not.
--   * **And sparks with it.** The construction robot's repair sparks
--     (base/graphics/entity/sparks, `robot_animations.sparks` in
--     base/prototypes/entity/flying-robots.lua), a short fall of glowing
--     metal sparks, one of its six picked at random. An explosion draws one
--     animation, and the fireball is it, so the sparks are a small explosion
--     of their own the big one sets off where it stands -- as a bullet's hit
--     sets off vanilla's `spark-explosion` (base/prototypes/entity/
--     hit-effects.lua). They are a robot's, a spot under a tile across, so
--     vanilla's hit sparks (`spark-particle` and `spark-particle-debris`, what
--     a bullet strikes off metal) are thrown over the turbine with the debris,
--     to carry the burst to its 3x5.
local SMOKE_EFFECTS = { ["create-smoke"] = true, ["create-trivial-smoke"] = true }

-- A trigger, a delivery or an effect may each be one table or a list of them.
local function each(x)
  if x == nil then return {} end
  if x.type then return { x } end
  return x
end

-- A list of trigger effects less any that make smoke, or nil if none is left.
local function without_smoke(effects)
  local kept = {}
  for _, effect in ipairs(each(effects)) do
    if not SMOKE_EFFECTS[effect.type] then kept[#kept + 1] = effect end
  end
  return #kept > 0 and kept or nil
end

-- The two smoking pieces of vanilla's debris, as ours, without the smoke.
local SMOKELESS = {}
for _, size in ipairs({ "big", "medium" }) do
  local from = "steam-turbine-metal-particle-" .. size
  local particle = table.deepcopy(data.raw["optimized-particle"][from])
  assert(particle, "optimized-particle/" .. from .. " does not exist")
  particle.name = "sae-crust-turbine-metal-particle-" .. size
  for _, key in ipairs({ "regular_trigger_effect", "ended_on_ground_trigger_effect",
                         "ended_in_water_trigger_effect" }) do
    particle[key] = without_smoke(particle[key])
  end
  if particle.regular_trigger_effect == nil then particle.regular_trigger_effect_frequency = nil end
  SMOKELESS[from] = particle.name
  data:extend({ particle })
end

-- Vanilla's hit sparks, thrown from about head height. An explosion's offsets
-- do not turn with the building, so the spread is square, inside the 3x5 lying
-- either way.
local function spark_burst(particle_name, count)
  return
  {
    type = "create-particle",
    repeat_count = count,
    particle_name = particle_name,
    offset_deviation = { { -1.25, -1.25 }, { 1.25, 1.25 } },
    initial_height = 1,
    initial_height_deviation = 0.5,
    initial_vertical_speed = 0.04,
    initial_vertical_speed_deviation = 0.04,
    speed_from_center = 0.03,
    speed_from_center_deviation = 0.03,
    frame_speed = 0.5
  }
end

-- The robot's sparks, as an explosion of their own: drawn once where it is
-- set off, silent, and with nothing else in it.
local robot_sparks = data.raw["construction-robot"]["construction-robot"].sparks
assert(robot_sparks, "construction-robot/construction-robot has no sparks")
local turbine_sparks =
{
  type = "explosion",
  name = "sae-crust-turbine-sparks",
  icon = "__space-age-extended__/graphics/icons/crust-turbine.png",
  icon_size = 64,
  flags = { "not-on-map" },
  hidden = true,
  subgroup = "energy-explosions",
  order = "a-g-a-z[sae-crust-turbine]-b[sparks]",
  -- On the ground, as the fireball it goes off beside, and as the sparks drew
  -- when they were the explosion's own animation (T06).
  height = 0,
  animations = table.deepcopy(robot_sparks)
}

local turbine_explosion = table.deepcopy(data.raw.explosion["steam-turbine-explosion"])
assert(turbine_explosion, "explosion/steam-turbine-explosion does not exist")
turbine_explosion.name = "sae-crust-turbine-explosion"
turbine_explosion.icon = "__space-age-extended__/graphics/icons/crust-turbine.png"
turbine_explosion.icon_size = 64
turbine_explosion.order = "a-g-a-z[sae-crust-turbine]"
turbine_explosion.localised_name = { "dying-explosion-name", { "entity-name.sae-crust-turbine" } }
turbine_explosion.smoke = nil
turbine_explosion.smoke_count = nil
turbine_explosion.smoke_slow_down_factor = nil
for _, trigger in ipairs(each(turbine_explosion.created_effect)) do
  for _, delivery in ipairs(each(trigger.action_delivery)) do
    for _, key in ipairs({ "target_effects", "source_effects" }) do
      local effects = without_smoke(delivery[key])
      for _, effect in ipairs(effects or {}) do
        effect.particle_name = SMOKELESS[effect.particle_name] or effect.particle_name
      end
      delivery[key] = effects
    end
    if delivery.type == "instant" then
      delivery.target_effects = delivery.target_effects or {}
      table.insert(delivery.target_effects, spark_burst("spark-particle", 40))
      table.insert(delivery.target_effects, spark_burst("spark-particle-debris", 20))
      table.insert(delivery.target_effects,
                   { type = "create-explosion", entity_name = turbine_sparks.name })
    end
  end
end

turbine.corpse = turbine_remnants.name
turbine.dying_explosion = turbine_explosion.name
data:extend({ turbine, turbine_remnants, turbine_sparks, turbine_explosion })

--------------------------------------------------------------------------------
-- Items and build recipes.
--
-- Both are cheap and early on purpose: this is the pair a player builds on
-- landing day, before there is a smelter to make anything better with.
--
-- **Which means neither can be priced in kamacite plate**, and both were. The
-- technology says as much -- `sae-crust-tapping` hangs off Core Discovery
-- rather than the Survey, "because it needs nothing the survey teaches" -- but
-- the recipes needed 10 and 20 plate, and plate came only after the survey.
-- A player who took the landing-day technology first got two recipes they could
-- not craft. Steel, gears and pipe come out of the cargo pod, so now they can.
--------------------------------------------------------------------------------

data:extend({
  {
    type = "item",
    name = "sae-gas-pump",
    icon = "__space-age-extended__/graphics/icons/gas-pump.png",
    icon_size = 64,
    subgroup = "energy",
    order = "z[sae]-b[gas-pump]",
    place_result = "sae-gas-pump",
    inventory_move_sound = item_sounds.mechanical_inventory_move,
    pick_sound = item_sounds.mechanical_inventory_pickup,
    drop_sound = item_sounds.mechanical_inventory_move,
    stack_size = 20,
    weight = 20 * kg
  },
  {
    type = "recipe",
    name = "sae-gas-pump",
    categories = { "crafting" },
    energy_required = 4,
    ingredients = {
      { type = "item", name = "steel-plate", amount = 10 },
      { type = "item", name = "pipe", amount = 10 },
      { type = "item", name = "iron-gear-wheel", amount = 10 }
    },
    results = { { type = "item", name = "sae-gas-pump", amount = 1 } },
    enabled = false
  },
  {
    type = "item",
    name = "sae-crust-turbine",
    icon = "__space-age-extended__/graphics/icons/crust-turbine.png",
    icon_size = 64,
    subgroup = "energy",
    order = "z[sae]-c[crust-turbine]",
    place_result = "sae-crust-turbine",
    inventory_move_sound = item_sounds.mechanical_inventory_move,
    pick_sound = item_sounds.mechanical_inventory_pickup,
    drop_sound = item_sounds.mechanical_inventory_move,
    stack_size = 20,
    weight = 40 * kg
  },
  {
    type = "recipe",
    name = "sae-crust-turbine",
    categories = { "crafting" },
    energy_required = 6,
    ingredients = {
      { type = "item", name = "steel-plate", amount = 20 },
      { type = "item", name = "pipe", amount = 10 },
      { type = "item", name = "iron-gear-wheel", amount = 20 }
    },
    results = { { type = "item", name = "sae-crust-turbine", amount = 1 } },
    enabled = false
  }
})
