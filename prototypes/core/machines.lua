-- The Core's machines, scaled back to the landing: the Drop Crusher, the
-- Ballast Drill, the Vacuum Furnace and the Reaction Plant. The rest went with
-- the cut.
--
-- Each has a master spec under graphics/, and every number below is read off it
-- rather than invented here; where this file and a spec disagree, the spec is
-- right and this is a bug. Section 2 of each spec is the source.
--
-- **Every one wears its own plate**, through `derive.own_graphics`. The Drop
-- Crusher's and the Reaction Plant's are rendered from Blender models
-- (concept/<building>/model/); the Ballast Drill's and the Vacuum Furnace's are
-- still the adopted generated plates until their models are wired. Each is
-- derived from a vanilla machine of the same footprint and marked by a
-- `derive.placeholder_art` call until `own_graphics` clears it, so a building
-- that never gets its plate is still logged at data stage. That is a different
-- thing from an inherited leftover -- see prototypes/derive.lua, which strips
-- those up front.
--
-- Two shapes are not obvious, and each cost a spike or a redesign to find:
--
--   * The Vacuum Furnace is a `furnace`, not an assembling machine, and its flux
--     box is deliberately large. S12 measured that a furnace with a fluid
--     ingredient refuses its *solid* ingredient until the fluid is already in
--     the machine; a big buffer against a small draw makes that latch rare.
--   * The Gas Pump (crust-tap.lua, not here) is a `mining-drill` on a vent
--     resource, as the pumpjack is on oil, so the vent runs down as it is drawn.
--     It replaced an `offshore-pump` on a vent tile, which never could.

local derive = require("prototypes.derive")
local item_sounds = require("__base__.prototypes.item_sounds")

--------------------------------------------------------------------------------
-- Crafting categories.
--
-- Every one of these is private on purpose. A category the Core shares with
-- vanilla is a recipe a vanilla machine can run, and for several of these
-- buildings the whole argument is that the vanilla machine *cannot* -- the space
-- crusher must never run the Drop Crusher's recipe, and nothing but the Vacuum
-- Furnace may sinter.
--------------------------------------------------------------------------------

data:extend({
  { type = "recipe-category", name = "sae-crushing" },
  { type = "recipe-category", name = "sae-reaction" }
})

--------------------------------------------------------------------------------
-- Surface conditions, named once.
--
-- Two distinct locks, and the difference is the design rather than a detail.
-- `HIGH_G` is the Core's surface alone: the two gravity machines cannot be
-- carried anywhere else, because gravity is the thing doing their work. `CORE`
-- is the Core and space platforms, for machines whose argument is the absence of
-- atmosphere rather than the presence of weight. `CORE_ONLY` is the Core and
-- not the platforms: some pressure, but not much.
--------------------------------------------------------------------------------

local HIGH_G = { { property = "gravity", min = 45 } }
local CORE = { { property = "pressure", max = 9 } }
local CORE_ONLY = { { property = "pressure", min = 1, max = 9 } }

local BOX_3x3 = { { -1.4, -1.4 }, { 1.4, 1.4 } }
local SEL_3x3 = { { -1.5, -1.5 }, { 1.5, 1.5 } }

--- A 3x3 crafting machine. Only the Drop Crusher is one here, but the shape
--- is the Core's default and the furnace below borrows its boxes.
local function crafter(name, from, opts)
  local p = derive.from("assembling-machine", from, name)
  derive.placeholder_art(p, "wears " .. from .. "'s sprites until its plate exists")
  p.icon = data.raw["assembling-machine"][from].icon
  p.icons = nil
  p.minable = { mining_time = 0.5, result = name }
  p.collision_box = BOX_3x3
  p.selection_box = SEL_3x3
  p.crafting_categories = opts.categories
  p.crafting_speed = opts.speed or 1
  p.energy_usage = opts.energy
  p.energy_source = { type = "electric", usage_priority = "secondary-input" }
  p.module_slots = opts.modules
  p.surface_conditions = opts.conditions
  p.fluid_boxes = opts.fluid_boxes
  p.fluid_boxes_off_when_no_fluid_recipe = opts.fluid_boxes ~= nil
  return p
end

--------------------------------------------------------------------------------
-- N1. Drop Crusher -- concept/drop-crusher/building-spec-drop-crusher.md
--
-- Breaks ore by dropping a weight on it, so it works only where there is weight
-- to drop. Vanilla's crusher spins and is locked to zero g; this one drops and
-- is locked to high g. Neither can be built where the other belongs, and neither
-- can run the other's recipes, which is what a Core variant should mean.
--------------------------------------------------------------------------------

local crusher = crafter("sae-drop-crusher", "assembling-machine-3", {
  categories = { "sae-crushing" },
  energy = "200kW",          -- the fall is free; the lift is not
  modules = 2,
  conditions = HIGH_G
})

-- Art: the Sealed Hammer, option A of five (concept/drop-crusher/options/),
-- rendered in Blender from concept/drop-crusher/model/drop_crusher.py and signed
-- off by Liam, 2026-10-09.
--
-- The design was locked 2026-09-09 and was the first in this mod picked by
-- comparison rather than by refinement: versions 1 to 10 were all the same idea
-- made better, and the round that replaced them drew it against a sibling
-- instead. The decision record and the winner's prompt are in that directory;
-- the adopted sheet is `concept/drop-crusher/adopted/A-sheet.png`, and the model
-- reproduces it.
--
-- **Rendered, not cut**, as the Reaction Plant is: every pass comes off one model
-- through one calibrated camera (tools/blender/rig.py) on one canvas with the
-- entity origin at its centre, so the layers register by construction. Every
-- size, shift, frame count and line length below is copied from the
-- sheets/meta.json the packer writes; none was measured off a sheet. To
-- regenerate, with any Blender 5 binary:
--
--   BLENDER=<blender> tools/blender/render.sh \
--       concept/drop-crusher/model/drop_crusher.py <scratch> --icon
--
-- then copy <scratch>/sheets/icon.png to graphics/icons/drop-crusher.png, the
-- other <scratch>/sheets/*.png into graphics/entity/drop-crusher/, and the
-- numbers out of meta.json into this block.
--
-- **Nothing on this machine is hot**, which makes it the one building in the set
-- where the status lamp carries the whole read on its own. §3.3 is explicit that
-- there is no glow here: the ore is cold, the fall is free, and the only light is
-- the lens the engine tints.
--
-- **The stroke is the animation, and the plate does not contain it.** §3.2
-- calls the crown rising and falling "the entire read". The moving parts -- the
-- octagonal crown on its racked shank, the two upright gears in their housings
-- east and west of the collar with the pinions that drive them, and the trip
-- pawl -- are rendered alone, 24 frames of the window round the collar, with
-- their shadows caught on the roof. base.png is the machine WITHOUT them, the
-- collar complete beneath where the crown sits. So the stroke cannot be a
-- working visualisation, which the engine stops drawing when the machine stops:
-- the crusher would stand idle with no weight in it. It is a layer of the main
-- animation, which an assembling machine draws in every state and advances only
-- while crafting. The weight is wound up the rack over frames 0 to 16 with the
-- gears turning, the pawl trips, and it falls through 17 to 23 with each frame's
-- travel longer than the last. The gears stay meshed with the rack throughout,
-- so they spin back fast as it drops. The packer tracks the crown in every frame
-- against the declared curve (meta.json's `stroke_path_px`).
--
-- **Frame 0 is the still**: the weight seated in the collar, pawl engaged,
-- checked against a single render of the whole stopped machine. There is no
-- `idle_animation`: §9 records that one would have to carry the same 24 frames,
-- and an assembling machine simply stops on a frame instead. That frame 0 is the
-- seat is why the loop winds up from the bottom and lands back on it.
--
-- **`animation_speed` is derived, not chosen.** 24 frames at 0.2 is a two-second
-- loop, and `sae-crushing` is `energy_required = 2` at `crafting_speed = 1` -- so
-- one drop is one craft at the base rate. `constant_speed` is left false on
-- purpose, per §9: modules should make the hammer fall faster. That breaks the
-- one-drop-one-craft correspondence, which §9 is explicit nobody notices.
--
-- **The status lamp is cut white and tinted by the engine**: a caged lamp on a
-- bracket on the roof's kerb at the south-east, where nothing that moves passes
-- in front of it (moved from the wall above the hatch, where it drew 7x4 px on
-- screen and did not register). It is a status lamp, not a
-- fault lamp: it reports every state, working included, in vanilla's
-- mining-drill colours (below).
local DC = "__space-age-extended__/graphics/entity/drop-crusher/"
local DC_FRAMES = 24
local DC_SPEED = 0.2

-- The status lamp's colours: the ones vanilla's electric mining drill uses
-- (`electric_mining_drill_status_colors`, base/prototypes/entity/mining-drill.lua),
-- less `no_minable_resources`, the one state a drill has and a crafter does not --
-- the Reaction Plant's mapping, for the same reason. Red is idle or short of ore,
-- yellow is blocked, disabled or browned out, green is working.
local function dc_status_colors()
  return
  {
    no_power = { 0, 0, 0, 0 },          -- dark: nothing to report with
    idle = { 1, 0, 0, 1 },
    insufficient_input = { 1, 0, 0, 1 },
    full_output = { 1, 1, 0, 1 },
    disabled = { 1, 1, 0, 1 },
    working = { 0, 1, 0, 1 },
    low_power = { 1, 1, 0, 1 }
  }
end

crusher.icon = "__space-age-extended__/graphics/icons/drop-crusher.png"

-- From sheets/meta.json.
derive.own_graphics(crusher,
{
  status_colors = dc_status_colors(),
  animation =
  {
    layers =
    {
      -- The plate, less the moving parts. One frame, repeated to meet the
      -- stroke's count.
      {
        filename = DC .. "base.png",
        priority = "high",
        width = 198, height = 234,
        frame_count = 1,
        repeat_count = DC_FRAMES,
        animation_speed = DC_SPEED,
        shift = { 0, -0.28125 },
        scale = 0.5
      },
      -- The weight, the gears, the pinions and the pawl, in the window round the
      -- collar: one row of 24.
      {
        filename = DC .. "stroke.png",
        priority = "high",
        width = 191, height = 136,
        frame_count = DC_FRAMES,
        line_length = 24,
        animation_speed = DC_SPEED,
        shift = { 0.02344, -0.9375 },
        scale = 0.5
      },
      {
        filename = DC .. "base-shadow.png",
        priority = "high",
        draw_as_shadow = true,
        -- Leans to the right, so it is wider than the colour plate and carries
        -- its own shift.
        --
        -- Still one frame, rendered with the weight seated. The shadows the
        -- moving parts throw on the roof are in the stroke layer and travel with
        -- it; the crown's shadow on the ground does not. Cutting the ground
        -- shadow into 24 frames to move a sliver of it is a second sheet for
        -- something no player looks at. Recorded as a choice rather than an
        -- oversight.
        width = 254, height = 195,
        frame_count = 1,
        repeat_count = DC_FRAMES,
        animation_speed = DC_SPEED,
        shift = { 0.46875, -0.00781 },
        scale = 0.5
      }
    }
  },
  working_visualisations =
  {
    -- The status lamp. Rendered WHITE and cut white, because
    -- `apply_tint = "status"` hands the colour to the engine and a colour baked
    -- into the sheet would be that colour in every state for ever.
    -- `always_draw` is true because a lamp that only appears while working
    -- cannot report that the machine has stopped.
    {
      always_draw = true,
      apply_tint = "status",
      animation =
      {
        filename = DC .. "status-lamp.png",
        priority = "high",
        draw_as_glow = true,
        width = 13, height = 14,
        frame_count = 1,
        shift = { 0.38281, 0.29688 },
        scale = 0.5
      }
    }
  }
})
data:extend({ crusher })

--------------------------------------------------------------------------------
-- N2. Ballast Drill -- concept/ballast-drill/building-spec-ballast-drill.md
--
-- `resource_drain_rate_percent` is the whole building. It is the one mining-drill
-- field that changes what a patch is *worth* rather than how fast it empties,
-- and vanilla uses it exactly once, on the big mining drill. Here it turns ore
-- siting into a decision with a cost, on the one planet where ore is finite by
-- design. At 50 g the drill presses with its own mass instead of hammering,
-- which is both the fiction and the reason it cannot be carried to a world where
-- ore is effectively infinite and used as a straight upgrade.
--------------------------------------------------------------------------------

local drill = derive.from("mining-drill", "big-mining-drill", "sae-ballast-drill")
derive.placeholder_art(drill, "wears big-mining-drill's sprites until its plate exists")
drill.minable = { mining_time = 0.5, result = "sae-ballast-drill" }
-- The Core's only drill, now, and the only machine that will work kamacite at
-- all -- see the `sae-kamacite` note in resources.lua. That is what lets it be
-- generous: with nothing to be strictly worse than, its numbers can describe the
-- machine instead of defending it.
drill.resource_categories = { "sae-kamacite" }
-- **The four inherited fluid connections stay, and the art draws them.**
--
-- Nothing uses them yet: kamacite's `minable` carries no `required_fluid`, so
-- today they accept nothing. They are kept deliberately, because a mining fluid
-- for this drill is wanted later and the layout has to be settled *before* the
-- plate is cut. A flange added to a finished plate is a repaint of all four
-- directions, and the Vent Pump is the standing proof of how expensive
-- rearranging plumbing after the fact is.
--
-- **Inherited verbatim from the big mining drill, and that is the point.** The
-- shape is vanilla's, so a player who has plumbed one has already learned this
-- one: west and east take a connection a tile north of centre, the south face
-- takes two flanking the centre, and north takes none -- because north is where
-- the ore comes out (`vector_to_place_result` is { 0, -2.85 }).
--
-- **And the plate draws none of them**, which is the part worth writing down.
-- Vanilla's own drills carry no plumbing in their art at all -- checked, the big
-- mining drill's north sprite is a gantry and two ladders and nothing else. The
-- fitting is the fluid box's `pipe_covers`, and the ENGINE stamps it at whichever
-- connections are live: on an ore that needs no fluid it draws nothing.
--
-- That is why keeping the box costs the art nothing. Today the covers never
-- appear, because kamacite asks for no fluid; the day a recipe does ask, the
-- flanges appear by themselves, in the right places, in all four directions, and
-- no plate is repainted. The covers come across with the deepcopy.
--
-- The alternative -- painting flanges into the plate -- would put four visible
-- sockets on a machine that has no use for them, which is the Vent Pump's §19
-- complaint exactly.
drill.input_fluid_box = table.deepcopy(
  data.raw["mining-drill"]["big-mining-drill"].input_fluid_box)
drill.resource_drain_rate_percent = 50
-- 3.0, up from 1.3, and past the big mining drill's 2.5. The fiction was always
-- that at 50 g this thing presses with its own mass rather than hammering; a
-- number below the drill it is derived from said the opposite. (The old comment
-- claimed "~0.65 of the electric drill's" -- the electric drill is 0.5, so 1.3
-- was 2.6 times it. The comparison was to the big drill, and it was a penalty.)
drill.mining_speed = 3.0
-- Still heavy, because pressing 50 g of machine into a crust is not free, but
-- 900kW on top of half the yield was two penalties for one building.
drill.energy_usage = "600kW"
drill.energy_source = { type = "electric", usage_priority = "secondary-input" }
drill.module_slots = 4
drill.surface_conditions = HIGH_G

-- Art: the Ring Press, option B of five (concept/ballast-drill/options/).
--
-- Locked 2026-09-10. A heavy cast annulus riding up and down three guide columns
-- around a capped central shaft, on a low riveted deck. Nothing about it rises,
-- because the anti-read for this building is a derrick.
--
-- **The output was rebuilt from vanilla, not from the sheet.** The adopted sheet
-- drew an upright boom. Vanilla's drills do not, and the reason is geometric:
-- `big-mining-drill` is the same 5x5 footprint, places its ore at
-- `vector_to_place_result = {0, -2.85}` -- 0.35 tiles PAST the north edge -- and
-- draws `big-mining-drill-N-output.png`, a 128x88 six-frame drag-chain shifted
-- `by_pixel(-2, -66.5)`, which puts the chute INSIDE the footprint with its mouth
-- flush to the edge. Ours is the same idea: a short chute mouth built into the
-- back of the deck, drawn empty, with the ore an item entity the engine places in
-- front of it. See the template's convention 1 -- draw the chute, never what
-- comes out of it.
--
-- **The status lens was painted in.** Three generations of the master render came
-- back with no lamp at all, and this building has no other feedback: the ring
-- does not move in the still, nothing is hot, and the lens is the only thing that
-- can say idle from blocked. It is a bezel and a flat white disc composited into
-- the master at (340, 1015) before cutting, so it antialiases down with the rest
-- of the plate rather than being pasted onto the sprite.
--
-- **The plate is stretched 1.05x vertically.** The render came back at aspect
-- 1:0.90 against `big-mining-drill-N-still-front`'s 1:0.94 -- the camera defect
-- the template's Appendix C says to expect on every remaining building. 5% is inside the
-- band the tool's own docstring calls invisible on details. 320 px of drawn
-- machine, 5.000 tiles, checked by tools/check-footprint.py.
--
-- **The ring is RAISED in this plate**, so this frame is the top of the press
-- stroke and the frames fall from here. (The Drop Crusher's plate is the top of
-- its stroke too, for a different reason: its crown is the topmost thing on its
-- canvas, with two pixels of headroom, so it cannot rise at all. Its §9 assumed
-- the opposite until that was measured.)
--
-- **The stroke is animated, from the same route as the Drop Crusher's** --
-- Animatorio (github.com/Onoulade/Animatorio) driven by
-- tools/build-animatorio-layers.py off graphics/entity/ballast-drill/stroke.json,
-- cut into a static housing and a 228x230 window, checked to reassemble exactly.
--
-- **What moves is the ring and only the ring.** `concept/ballast-drill/options/B-ring-press.md`
-- is explicit -- "a fixed central column ... around it rides a heavy cast ballast
-- ring" -- so the column has to stay put while the mass drops around it. That is
-- two Animatorio layers, not one: a `piston` carrying the whole disc down, then a
-- `source_occluder` that paints the column back over it from the plate. The
-- column standing still while the ring falls past it is the entire read.
--
-- **65.6% of the machine's width moves**, and 30.3% of its drawn pixels change.
-- B-ring-press.md picked this design over four others precisely because it was
-- "the largest moving part of the five and the only one inside vanilla's band",
-- against 72%, 101% and 113% on assembling-machine-3, the centrifuge and the
-- electromagnetic plant. The Drop Crusher, for comparison, manages 17.7%.
--
-- **The deck behind the ring is cloned, not invented.** The plate never drew it,
-- so the band the ring uncovers has to come from somewhere: sampling 18 px up
-- lands real riveted plate there. The alternative -- inpainting from surrounding
-- colour -- gives a grey smear, and the two were rendered side by side before
-- this was chosen.
--
-- **`animation_speed` is 0.4**: 24 frames over 60 ticks is the "slow, heavy,
-- one-second stroke" §3.2 asks for, at `mining_speed = 3.0`.
--
-- **One plate for all four directions, and that is a known gap.** A mining drill
-- rotates, and `vector_to_place_result` rotates with it -- so a player who turns
-- this drill east gets ore out of its east face while the art still shows the
-- chute at the back. `graphics_set.animation` takes an Animation4Way, so the fix
-- is four plates and no prototype change; it wants the Vent Pump's route, one
-- rotation strip cut by tools/cut-rotation-strip.py. Until then the drill is
-- honest in its default orientation and wrong in the other three, which is
-- better than wearing big-mining-drill's sprites but is not finished.
local BD = "__space-age-extended__/graphics/entity/ballast-drill/"
local BD_FRAMES = 24
drill.icon = "__space-age-extended__/graphics/icons/ballast-drill.png"
drill.icons = nil
derive.own_graphics(drill,
{
  animation =
  {
    layers =
    {
      -- The plate, less the window the ring moves in. One frame, repeated to meet
      -- the animated layer's count -- vanilla's biochamber arrangement.
      {
        filename = BD .. "stroke-housing.png",
        priority = "high",
        width = 328, height = 313,
        frame_count = 1,
        repeat_count = BD_FRAMES,
        animation_speed = 0.4,
        shift = { 0, 0.13281 },
        scale = 0.5
      },
      -- The window's contents. Window is 50..278 x 16..246, so its centre sits
      -- 25.5 source px above the canvas centre -- the half comes from the canvas
      -- being an odd 313 tall. 64 source px to the tile at scale 0.5, and the
      -- plate's own 0.13281 is a rounded 8.5/64, so the sum is exactly
      -- (8.5 - 25.5)/64 = -17/64.
      {
        filename = BD .. "stroke.png",
        priority = "high",
        width = 228, height = 230,
        frame_count = BD_FRAMES,
        line_length = 6,
        animation_speed = 0.4,
        shift = { 0, -0.265625 },
        scale = 0.5
      },
      {
        filename = BD .. "base-shadow.png",
        priority = "high",
        draw_as_shadow = true,
        -- Still one frame. The ring moves 12 source px within a shadow plate 571
        -- wide; splitting the shadow to follow it is a second mask for something
        -- the camera never looks at. A choice, not an oversight.
        width = 571, height = 324,
        frame_count = 1,
        repeat_count = BD_FRAMES,
        animation_speed = 0.4,
        shift = { 1.89844, 0.21875 },
        scale = 0.5
      }
    }
  },
  working_visualisations =
  {
    {
      always_draw = true,
      apply_tint = "status",
      animation =
      {
        filename = BD .. "status-lamp.png",
        priority = "high",
        draw_as_glow = true,
        width = 328, height = 313,
        frame_count = 1,
        shift = { 0, 0.13281 },
        scale = 0.5
      }
    }
  }
})
data:extend({ drill })

--------------------------------------------------------------------------------
-- N7. Vacuum Furnace -- concept/vacuum-furnace/building-spec-vacuum-furnace.md
--
-- A `furnace`, not an assembling machine, so it picks its own recipe from what
-- it is fed -- which is what makes a smelter a smelter. It does the two things
-- the electric furnace cannot: it is the only machine in the game that accepts
-- kamacite fines, and the only one carrying `sae-sintering`. Both are powder
-- processes and both are impossible in an open furnace for the same real reason.
--
-- The flux box is deliberately large. S12 measured that a furnace with a fluid
-- ingredient refuses its solid ingredient outright until the fluid is already
-- present; a generous buffer against a small per-craft draw makes that latch
-- rare after first build. It does not remove it.
--------------------------------------------------------------------------------

local furnace = derive.from("furnace", "electric-furnace", "sae-vacuum-furnace")
furnace.minable = { mining_time = 0.5, result = "sae-vacuum-furnace" }
furnace.collision_box = BOX_3x3
furnace.selection_box = SEL_3x3
furnace.crafting_categories = { "smelting" }
furnace.crafting_speed = 1.5
furnace.energy_usage = "1200kW"
furnace.energy_source = { type = "electric", usage_priority = "secondary-input" }
furnace.module_slots = 2
furnace.surface_conditions = CORE
furnace.source_inventory_size = 1          -- one, as the electric furnace has
furnace.result_inventory_size = 1
-- Every size and shift below is copied from the model's two meta.json files
-- (concept/vacuum-furnace/model/sheets/ and sheets/ports/), as the Reaction
-- Plant's are; none was measured off a sheet or typed from memory. The needle
-- is the one layer meta.json does not carry; its own comment says where its
-- numbers come from.
local VF = "__space-age-extended__/graphics/entity/vacuum-furnace/"

local function vf_sprite(file, width, height, shift)
  return
  {
    filename = VF .. file .. ".png",
    priority = "extra-high",
    width = width, height = height,
    shift = shift,
    scale = 0.5
  }
end

-- The flux line passes THROUGH the furnace (spec sections 2 and 8): one box, a
-- port at the middle of the south face and one at the middle of the north,
-- both `input-output`, so flux comes in either side and carries on out the
-- other and a row of furnaces is fed off one line, as vanilla's boilers are.
-- Rotated once, the line runs east-west; the drawing does not turn with it.
--
-- `production_type` stays "input": the box is the recipe's flux, and it is the
-- connections, not the box, that let the fluid on through. Measured on a
-- headless 2.1 server, 2026-10-09: pipe, furnace, pipe in a line, fed at one
-- end, and the far pipe filled and joined the furnace's fluid segment -- with
-- the furnace smelting iron, a recipe with no fluid, both north-south and
-- rotated east-west, and with no recipe at all.
--
-- **No `fluid_boxes_off_when_no_fluid_recipe`.** It is an assembling machine's
-- property; the prototype docs list it there and not on the furnace, and a
-- furnace with it true and one with it false behaved identically in the run
-- above: both passed fluid and both turned with no recipe set.
--
-- The stubs are the engine's, drawn per direction and redrawn when the furnace
-- is rotated: rendered from the model in the furnace's own metal, to assembler
-- 3's shape, size and shifts, each in the tile outside its port, which is the
-- tile a pipe picture is drawn relative to. The covers are vanilla's and cap a
-- port only while nothing is plumbed to it; `secondary_draw_orders` puts a
-- north stub behind the building, as assembler 3's does and as the review sheet
-- drew it.
furnace.fluid_boxes =
{
  {
    production_type = "input",
    volume = 2000,                         -- see the S12 note above
    pipe_picture =
    {
      north = vf_sprite("pipe-N", 52, 20, { 0.01562, 0.34375 }),
      east = vf_sprite("pipe-E", 32, 74, { -0.71875, 0.0625 }),
      south = vf_sprite("pipe-S", 64, 70, { 0, -0.76562 }),
      west = vf_sprite("pipe-W", 32, 72, { 0.73438, 0.01562 })
    },
    pipe_covers = derive.pipe_covers(),
    always_draw_covers = false,
    secondary_draw_orders = { north = -1 },
    pipe_connections =
    {
      { flow_direction = "input-output", direction = defines.direction.south, position = { 0, 1 } },
      { flow_direction = "input-output", direction = defines.direction.north, position = { 0, -1 } }
    }
  }
}

-- Art: rendered in Blender from concept/vacuum-furnace/model/vacuum_furnace.py,
-- signed off by Liam and seen in game 2026-10-09.
--
-- A sealed welded drum with a flat clamped hatch, and the whole design is the
-- absence of an opening: no door, no throat, no chimney. One plate serves all
-- four directions, because nothing on it has a facing -- the ports are the
-- engine's, above.
--
-- **The viewport is the indicator.** The one light on the building is the glass
-- at the centre of the hatch, and it carries two layers cut to the same 22x21
-- canvas. While working it glows orange, additively, and fades out as the
-- machine stops. In every other state it is tinted by status: `apply_tint =
-- "status"` hands the colour to the engine, which is why the glass is cut WHITE
-- -- a colour baked into it would be that colour in every state for ever -- and
-- `always_draw` is true because an indicator that only draws while working
-- cannot report that the machine has stopped. Vanilla's electric mining drill
-- is the pattern.
--
-- **The latch does not draw magenta, measured in a client 2026-10-09.** The
-- spec settles on magenta for it (sections 3.2 and 20), but a furnace dry of
-- flux with powder in it reports `no_ingredients` and drops its recipe, and the
-- engine colours that as `idle`: dark glass, the same as a furnace nobody fed.
-- `full_output` drew pale blue on the same screenshot, so the tint itself
-- works. `status_colors` below are section 15's as written; the spec needs
-- updating to what the engine does.
--
-- **The flywheel and the gauge needle are the animation.** Both share one
-- 16-frame loop, so they are layers of the main animation and not working
-- visualisations, which the engine stops drawing when the machine stops: the
-- pump would stand idle with no wheel on its shaft. A crafting machine draws its
-- main animation in every state and advances it only while crafting, so the
-- stopped furnace is the plate with every layer on the frame it stopped at --
-- measured in a client: the wheel turned while smelting and held still, pixel
-- for pixel, once the ore ran out or the output filled. The plate and the
-- shadow are one frame each, repeated to the loop's count.
--
-- The flywheel is rendered: a spoked wheel on the pump's shaft, alone, with its
-- shadow on the pump body behind it; the plate is the machine without it. The
-- needle is Animatorio's (concept/vacuum-furnace/model/gauge.json), drawn over a
-- dial the model renders bare: base-housing.png is the plate with the dial's
-- 18 px window punched out, and needle.png is that window, 16 frames, cut by
-- tools/build-animatorio-layers.py as the Drop Crusher's stroke was.
local VF_FRAMES = 16
local VF_SPEED = 0.5                      -- as Liam saw it in the preview
local VF_SHIFT = { 0, -0.28125 }          -- the plate's, from meta.json's "base"

-- The viewport glow's `effect`, spec section 6 (A1): "uranium-glow", a slow
-- swell and settle, heat behind thick glass. "flicker" is vanilla's fire and
-- reads as an open flame, which a sealed furnace has none of (Liam, 2026-10-09).
local VF_GLOW_EFFECT = "uranium-glow"

furnace.icon = "__space-age-extended__/graphics/icons/vacuum-furnace.png"
furnace.icon_size = 64
derive.own_graphics(furnace,
{
  animation =
  {
    layers =
    {
      -- The plate, less the needle's window. One frame, repeated.
      {
        filename = VF .. "base-housing.png",
        priority = "high",
        width = 198, height = 234,
        frame_count = 1,
        repeat_count = VF_FRAMES,
        animation_speed = VF_SPEED,
        shift = VF_SHIFT,
        scale = 0.5
      },
      {
        filename = VF .. "base-shadow.png",
        priority = "high",
        draw_as_shadow = true,
        width = 223, height = 201,
        frame_count = 1,
        repeat_count = VF_FRAMES,
        animation_speed = VF_SPEED,
        shift = { 0.22656, -0.05469 },
        scale = 0.5
      },
      {
        filename = VF .. "flywheel.png",
        priority = "high",
        width = 54, height = 74,
        frame_count = VF_FRAMES,
        line_length = 16,
        animation_speed = VF_SPEED,
        shift = { 1.09375, 0.78125 },
        scale = 0.5
      },
      -- The needle's window. Not in meta.json: its size is the sheet's own
      -- (288x18, sixteen 18 px frames), and its shift is the plate's plus the
      -- window's offset from the plate's centre, 80 px right and 60 px down --
      -- { 1.25, 0.9375 }, as review_sheet.py places it from gauge.json.
      {
        filename = VF .. "needle.png",
        priority = "high",
        width = 18, height = 18,
        frame_count = VF_FRAMES,
        line_length = 16,
        animation_speed = VF_SPEED,
        shift = { VF_SHIFT[1] + 1.25, VF_SHIFT[2] + 0.9375 },
        scale = 0.5
      }
    }
  },
  -- Spec section 15, exactly. Clear while working, because the orange glow says
  -- it; clear when idle, disabled or short of power, which is dark glass.
  --
  -- No colour for the latch. The engine has no status for it: a furnace holding
  -- powder without flux reports `no_ingredients`, exactly as an unfed one does,
  -- and that takes the idle colour (tested 2026-10-09). The pass-through keeps
  -- every furnace on a primed line topped up, which is what makes it rare.
  status_colors =
  {
    working = { 0, 0, 0, 0 },              -- the orange glow says this
    full_output = { 0.4, 0.7, 1, 1 },
    idle = { 0, 0, 0, 0 },                 -- dark glass
    disabled = { 0, 0, 0, 0 },
    no_power = { 0, 0, 0, 0 },
    low_power = { 0, 0, 0, 0 }
  },
  working_visualisations =
  {
    -- The heat glow, working minus idle, differenced by the packer so it
    -- registers by construction: a glowing sintering bed seen through thick
    -- glass, white-yellow at the core to deep red at the chamber's edge, so it
    -- reads as a furnace rather than a lamp. The building's entire heat budget
    -- is this one circle; if light appears anywhere else, the seal is a lie.
    -- The light it casts is a deep red-orange, the colour of the bed.
    {
      fadeout = true,
      effect = VF_GLOW_EFFECT,
      light = { intensity = 0.3, size = 2.5, color = { 0.9, 0.45, 0.2 } },
      animation =
      {
        filename = VF .. "port-glow.png",
        priority = "high",
        blend_mode = "additive",
        draw_as_glow = true,
        width = 19, height = 19,
        frame_count = 1,
        shift = { -0.00781, -0.74219 },
        scale = 0.5
      }
    },
    -- The viewport glass, cut white and tinted by the engine.
    {
      apply_tint = "status",
      always_draw = true,                  -- mandatory, or the fault states never draw
      animation =
      {
        filename = VF .. "viewport-status.png",
        priority = "high",
        draw_as_glow = true,
        width = 22, height = 21,
        frame_count = 1,
        shift = { 0, -0.75781 },
        scale = 0.5
      }
    }
  }
})
data:extend({ furnace })

--------------------------------------------------------------------------------
-- The Reaction Plant -- concept/reaction-plant/building-spec-reaction-plant.md
--
-- No N number: it arrived after the nine above were numbered. It wears its own
-- art, rendered from a model rather than cut from a plate; see "Art" below.
--
-- Stage 1 of the radiant cycle. The Core's fuel was precipitated out of the
-- pool with helium-3, which put the power line in the queue behind the Vent
-- Pump for the one gas the planet rations. It is made from crust gas now: the
-- shore gives the solution, a vent gives the gas, and neither is a thing
-- anything else on the planet is waiting for.
--
-- Three boxes: two in on the north face at the two positions the chemical plant
-- puts its own pair, and one out at the south face's centre.
--
-- **`fluid_boxes_off_when_no_fluid_recipe` is false here, against `crafter`'s
-- default, so that a plant with no recipe can be turned.** `crafter` sets the
-- flag for every machine it hands boxes to; this one turns it off again below.
-- With it true the engine gives a machine with no recipe no fluid boxes at all,
-- and an entity with no fluid boxes has nothing to rotate: a freshly placed
-- plant, before its recipe is chosen, took a direction and snapped straight
-- back to north. Measured on a headless server, beside an assembling machine 2
-- doing the same thing for the same reason. Vanilla agrees about which machines
-- want the flag: the chemical plant, which this one is shaped after, does not
-- set it; assembling machines 2 and 3 do, and they are the ones that spend most
-- of their lives on recipes with no fluid in them at all.
--
-- **What the false flag buys, exactly.** It governs the no-recipe case and only
-- that. With no recipe the plant now carries all three boxes, draws all three
-- ports, keeps whatever direction it is given, and a pipe laid against the
-- south face joins the output. The moment a recipe is set the engine assigns
-- boxes to that recipe's own fluids and drops the ones it has no use for, so a
-- plant running precipitation -- two fluids in, a solid out -- shows its two
-- inputs and no output, and a pipe that had joined the south port goes quiet
-- until the recipe is cleared again. No flag turns that off: it is how the
-- engine handles a crafting machine's fluid boxes, and a vanilla chemical plant
-- on a recipe whose products are solid behaves identically. Measured, both.
--
-- **The output box is still declared now rather than with stage 3's recipe.** A
-- fluid box is a prototype property and not a recipe's, so declaring it later
-- would change the entity's geometry under every plant already standing and
-- every blueprint that holds one: the south face would turn from wall into
-- port, and a layout that had run belts across it would have to be redrawn.
-- Declared now, that face is spoken for, and the day stage 3's dissolve recipe
-- -- which does return fluid -- is set on a plant, the port comes alive on a
-- line the player already left room for.
--
-- **The ports are the engine's and turn with the building, which is the
-- opposite of the Helium Concentrator on purpose.** That machine paints its
-- flanges into its own plate, so it empties `pipe_picture` and the engine must
-- not draw a stub over the art. This one is the other arrangement, the one
-- assembling machines 2 and 3 use: `pipe_picture` is a stub per direction
-- that the engine draws and redraws whenever the player rotates the entity,
-- and the plate paints no flange at all. That is what lets this building stay
-- rotatable on ONE plate rather than the Gas Pump's four -- nothing in the
-- still art has a facing, so there is nothing to draw four times. The entity
-- therefore carries no `not-rotatable` flag. The stubs are the plant's own,
-- rendered from the same model as the plate (see "Art"), not vanilla's
-- `assembler2pipepictures`: that fitting is blue paint and polished brass at a
-- size that does not meet this building's gutter.
--
-- `pipe_covers` caps a port nothing is joined to -- the plant's own blind cap,
-- rendered with the stubs -- and `always_draw_covers = false` takes the cap
-- away once a pipe arrives; `secondary_draw_orders = { north = -1 }` puts a
-- north stub behind the building, as vanilla's assemblers set it.
--
-- `sae-reaction` is private like every other category in this file, and here
-- that cuts both ways: a vanilla chemical plant must not be able to make the
-- Core's fuel, and this plant must not be able to run chemistry.
--------------------------------------------------------------------------------

-- Art: rendered in Blender from concept/reaction-plant/model/reaction_plant.py,
-- and signed off by Liam with the task that put it here, 2026-10-01.
--
-- **Rendered, not cut.** There is no master plate: every pass is rendered from
-- one model, through one calibrated camera (tools/blender/rig.py), on one canvas
-- with the entity origin at the canvas centre. So the layers register by
-- construction, and every size and shift below is computed by the packer and
-- copied from the meta.json it writes -- none of them was measured off a sheet.
--
-- To regenerate, with any Blender 5 binary:
--
--   BLENDER=<blender> tools/blender/render.sh \
--       concept/reaction-plant/model/reaction_plant.py <scratch> --ports --icon
--
-- then copy <scratch>/sheets/icon.png to graphics/icons/reaction-plant.png (and
-- its keyed master, sheets/masters/icon.png, to graphics/icons/masters/
-- reaction-plant.png), the other <scratch>/sheets/*.png and
-- <scratch>/sheets/ports/*.png into graphics/entity/reaction-plant/, and the
-- numbers out of the two meta.json files into this block. render.sh prints
-- pack.py's checks; Appendix C's must hold exactly (centre_offset_px 0,
-- edge_alpha_max 0, half_width_tiles 1.5) and glow_white_px stay at 0, and the
-- run stops if coupling_drift_px goes over 1.
--
-- **One plate, for all four directions.** Nothing on it has a facing: the ports
-- are the engine's (above), and the one moving part is on the crown.
--
-- **The coupling is the animation, and the plate does not contain it.** The
-- spider coupling on the drive tower is rendered alone, 12 frames through 60
-- degrees -- six-fold symmetry makes that the whole loop -- with its shadow
-- caught on the head beneath it, and base.png is the machine WITHOUT it. So it
-- cannot be a working visualisation, which the engine stops drawing when the
-- machine stops: the plant would stand idle with a hole in its crown. It is a
-- layer of the main animation, which an assembling machine draws in every state
-- and only advances while crafting -- shown when idle, turning only while
-- working. The plate and shadow are one frame each, repeated 12 times so every
-- layer carries the same count. 0.4 is the building spec's speed (section 13):
-- one turn of the loop in half a second, a full revolution every three.
--
-- **The slot glow is working minus idle**, differenced by pack.py from a lit and
-- an unlit render of the same scene, and drawn additively and only while
-- crafting. The emission was turned down until the light kept its colour
-- (glow_white_px 0), so the layer is green and not grey.
--
-- **The status lamp is cut white and tinted by the engine.** `always_draw`,
-- because a lamp that only appears while working cannot report that the
-- machine has stopped. Vanilla declares `status_colors` only on its mining
-- drills, and an assembling machine without the table drew this lens dark in
-- every state when the render was piloted, so it is set here, as vanilla's
-- electric mining drill sets it.
local RP = "__space-age-extended__/graphics/entity/reaction-plant/"
local RP_FRAMES = 12
local RP_SPEED = 0.4

local function rp_sprite(file, width, height, shift)
  return
  {
    filename = RP .. file .. ".png",
    priority = "extra-high",
    width = width, height = height,
    shift = shift,
    scale = 0.5
  }
end

-- From sheets/ports/meta.json. Each fitting was rendered on the middle tile of
-- its face, and its shift is taken from the tile outside the port -- the one a
-- pipe picture is drawn relative to -- so the same sheet sits right at either
-- port on a face.
local RP_PORTS =
{
  north = rp_sprite("port-N", 56, 44, { 0.03125, 0.5 }),
  east = rp_sprite("port-E", 35, 63, { -0.74219, 0.07031 }),
  south = rp_sprite("port-S", 61, 55, { 0.07031, -0.83594 }),
  west = rp_sprite("port-W", 29, 65, { 0.69531, 0.08594 })
}
local RP_COVERS =
{
  north = rp_sprite("cover-N", 54, 13, { 0.03125, 0.22656 }),
  east = rp_sprite("cover-E", 9, 62, { -0.47656, 0.07812 }),
  south = rp_sprite("cover-S", 60, 30, { 0.07812, -0.60938 }),
  west = rp_sprite("cover-W", 8, 60, { 0.46875, 0.0625 })
}

-- The fault lamp's colours: the ones vanilla's electric mining drill uses
-- (`electric_mining_drill_status_colors`, base/prototypes/entity/mining-drill.lua),
-- less `no_minable_resources`, the one state a drill has and a crafter does not.
-- Red is short of input, yellow is blocked or browned out, green is working.
local function rp_status_colors()
  return
  {
    no_power = { 0, 0, 0, 0 },          -- dark: nothing to report with
    idle = { 1, 0, 0, 1 },
    insufficient_input = { 1, 0, 0, 1 },
    full_output = { 1, 1, 0, 1 },
    disabled = { 1, 1, 0, 1 },
    working = { 0, 1, 0, 1 },
    low_power = { 1, 1, 0, 1 }
  }
end

local function reaction_box(flow, direction, position)
  return
  {
    production_type = flow,
    volume = 1000,
    pipe_picture = RP_PORTS,
    pipe_covers = RP_COVERS,
    always_draw_covers = false,
    secondary_draw_orders = { north = -1 },
    pipe_connections =
    { { flow_direction = flow, direction = direction, position = position } }
  }
end

local reaction_plant = crafter("sae-reaction-plant", "chemical-plant", {
  categories = { "sae-reaction" },
  energy = "1500kW",
  modules = 3,
  conditions = CORE_ONLY,
  fluid_boxes =
  {
    reaction_box("input", defines.direction.north, { -1, -1 }),
    reaction_box("input", defines.direction.north, { 1, -1 }),
    reaction_box("output", defines.direction.south, { 0, 1 })
  }
})
-- Undoing `crafter`'s blanket setting for this machine alone: a plant with no
-- recipe has to keep a direction. See the block comment above.
reaction_plant.fluid_boxes_off_when_no_fluid_recipe = false
reaction_plant.icon = "__space-age-extended__/graphics/icons/reaction-plant.png"

-- From sheets/meta.json.
derive.own_graphics(reaction_plant,
{
  status_colors = rp_status_colors(),
  animation =
  {
    layers =
    {
      {
        filename = RP .. "base.png",
        priority = "high",
        width = 198, height = 214,
        frame_count = 1,
        repeat_count = RP_FRAMES,
        animation_speed = RP_SPEED,
        shift = { 0, -0.14062 },
        scale = 0.5
      },
      {
        filename = RP .. "coupling.png",
        priority = "high",
        width = 46, height = 37,
        frame_count = RP_FRAMES,
        line_length = 12,
        animation_speed = RP_SPEED,
        shift = { 0.10938, -0.78906 },
        scale = 0.5
      },
      {
        filename = RP .. "shadow.png",
        priority = "high",
        draw_as_shadow = true,
        width = 208, height = 193,
        frame_count = 1,
        repeat_count = RP_FRAMES,
        animation_speed = RP_SPEED,
        shift = { 0.125, -0.00781 },
        scale = 0.5
      }
    }
  },
  working_visualisations =
  {
    -- The three sight slots.
    {
      always_draw = false,
      animation =
      {
        filename = RP .. "glow.png",
        priority = "high",
        blend_mode = "additive",
        draw_as_glow = true,
        width = 58, height = 13,
        frame_count = 1,
        shift = { 0, 0.82031 },
        scale = 0.5
      }
    },
    -- The status lamp, on its post at the west rim, clear of the alt-mode icon.
    {
      always_draw = true,
      apply_tint = "status",
      animation =
      {
        filename = RP .. "status-lamp.png",
        priority = "high",
        draw_as_glow = true,
        width = 10, height = 12,
        frame_count = 1,
        shift = { -0.9375, -0.54688 },
        scale = 0.5
      }
    }
  }
})
data:extend({ reaction_plant })

--------------------------------------------------------------------------------
-- The items, and what each costs to build.
--
-- Kept beside the machines rather than in items.lua, which is where the Arc Mast
-- puts its own: a building and the thing that places it are one unit, and
-- splitting them across files is how one of them ends up forgotten.
--
-- The Coil Separator's cost is the one that carries an argument. It is priced in
-- coil assemblies -- two stages below the Field Coil Segment the whole endgame
-- runs on -- so the player spends endgame material to make more endgame
-- material. Nothing else in the mod has an ingredient list that means something.
--------------------------------------------------------------------------------

-- The item wears whatever icon its machine wears -- its own once the plate
-- exists, the stand-in until then -- so the two can never disagree. Three
-- machines had their own icon on the ground and assembling-machine-3's in the
-- inventory before this read the entity instead of a second list.
local function entity_icon(name)
  for _, t in ipairs({ "assembling-machine", "furnace", "mining-drill" }) do
    local e = data.raw[t] and data.raw[t][name]
    if e then return e.icon end
  end
  error("sae machines: no machine named " .. name)
end

local function machine_item(name, order, ingredients, seconds)
  return
  {
    {
      type = "item",
      name = name,
      icon = entity_icon(name),
      subgroup = "production-machine",
      order = "z[sae]-" .. order .. "[" .. name .. "]",
      place_result = name,
      inventory_move_sound = item_sounds.mechanical_large_inventory_move,
      pick_sound = item_sounds.mechanical_large_inventory_pickup,
      drop_sound = item_sounds.mechanical_large_inventory_move,
      stack_size = 20,
      weight = 40 * kg
    },
    {
      type = "recipe",
      name = name,
      categories = { "crafting" },
      energy_required = seconds,
      ingredients = ingredients,
      results = { { type = "item", name = name, amount = 1 } },
      enabled = false
    }
  }
end

local function plate(n) return { type = "item", name = "sae-kamacite-plate", amount = n } end
local function gear(n) return { type = "item", name = "iron-gear-wheel", amount = n } end
local function circuit(n) return { type = "item", name = "advanced-circuit", amount = n } end
local function steel(n) return { type = "item", name = "steel-plate", amount = n } end

-- **The Drop Crusher is priced in freight, and it has to be.** It is the only
-- machine that fills `sae-crushing`, crushing is the only source of crushed
-- kamacite and fines, and those two are the only route to a kamacite plate. A
-- crusher costed in plate is therefore a crusher that can never be built: the
-- first one has to come out of the corridor, exactly like the first
-- electromagnetic plant in `06-core-production-tree.md` T1. Every other machine
-- here is priced in plate because by then the player has some.
--
-- **Nothing here is priced in welded plate.** That plate needs whiskers, and
-- neither exists since the cut; before it, it was a real gate that once made
-- the Vacuum Furnace unbuildable through exactly the stretch it exists to cover.
for _, spec in ipairs({
  { "sae-drop-crusher", "a", { steel(40), gear(30), circuit(10) }, 6 },
  -- Freight-priced for the same reason the crusher is: it is now the only way to
  -- get a kamacite ore out of the ground, so it sits on the critical path to the
  -- first plate and cannot be costed in plate. That is the rule for the whole
  -- landing kit -- on the path to the first plate, it comes out of the corridor.
  { "sae-ballast-drill", "b", { steel(60), gear(40), circuit(15) }, 10 },
  { "sae-vacuum-furnace", "g",
    { plate(50), { type = "item", name = "processing-unit", amount = 10 } }, 10 },
  -- The Helium Concentrator's price, for the same reason it is the same
  -- silhouette: a 3x3 shell with fluid ports on it, built out of plate, pipe
  -- and enough circuitry to meter what goes through.
  { "sae-reaction-plant", "h",
    { plate(40), { type = "item", name = "pipe", amount = 20 }, circuit(15) }, 8 },
}) do
  data:extend(machine_item(spec[1], spec[2], spec[3], spec[4]))
end
