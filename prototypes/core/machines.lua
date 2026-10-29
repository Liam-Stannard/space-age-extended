-- The Core's machines, scaled back to the landing: the Drop Crusher, the
-- Ballast Drill, the Vacuum Furnace and the Reaction Plant. The rest went with
-- the cut.
--
-- Each has a master spec under graphics/, and every number below is read off it
-- rather than invented here; where this file and a spec disagree, the spec is
-- right and this is a bug. Section 2 of each spec is the source.
--
-- **Every one wears its own plate**, through `derive.own_graphics`, and every
-- plate is rendered from a Blender model (concept/<building>/model/). Each is
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
-- animation, which advances only while crafting, and of the idle animation,
-- held cocked (below). The weight is wound up the rack over 16 frames with the gears
-- turning, the pawl trips, and it falls over 8 with each frame's travel longer
-- than the last. The gears stay meshed with the rack throughout, so they spin
-- back fast as it drops. The packer tracks the crown in every frame against the
-- declared curve (meta.json's `stroke_path_px`).
--
-- **The loop starts cocked** (Liam, 2026-10-11): frames 0 to 6 wind up, 6 is
-- the top, where the pawl trips, 7 to 13 fall, 14 lands seated, and 14 to 23
-- and 0 wind up again. Frame 0 is the weight just past halfway up the rack,
-- held by the pawl between two clicks (the model's PHASE: frame n is the old
-- seated-first loop's frame n + 10). It was the seat until the landing had to
-- carry a sound and the engine turned out never to fire one on frame 0 (see
-- "Sound" below); the phase moved rather than the sound.
--
-- **Frame 0 is the still**: the weight cocked, checked against a single render
-- of the whole stopped machine: the rest pose is cocked, ready to drop.
--
-- **The crusher rests cocked, through an `idle_animation`** (Liam, 2026-10-11).
-- Without one an assembling machine draws `animation` in every state and only
-- stops advancing it. A placed crusher starts its stroke on a random frame
-- (fresh ones in a client showed 2, 4, 23 and 6), and since one craft is one
-- 240-tick stroke it stops on whatever frame that leaves it on, so the cocked
-- rest pose was only ever seen in the still and the ghost. The idle animation
-- is the same three layers with the stroke held on frame 0: no new sheet,
-- the stroke sheet's first frame by `frame_sequence`. It has to run to the
-- same 24 frames as `animation` -- "Idle animation must have the same frame
-- count as animation" (WorkingVisualisations::idle_animation, which
-- CraftingMachineGraphicsSet inherits: doc-html/types/WorkingVisualisations.html)
-- -- the engine draws whichever of the two is showing at the machine's one
-- frame clock. Every one of the idle's 24 frames is the cocked pose, so
-- whatever frame the clock stopped on, it is cocked.
--
-- **The idle animation does not cover every stopped state.** The docs do not
-- say when the engine draws it; a client on the Core, 2026-10-11, showed
-- (`always_draw_idle_animation` left false):
--
--   working, browned out included     `animation`: the stroke plays (browned
--                                      out, slowed: 0.25x on 36 kW of 200 kW)
--   ran out of ore, output full,       `idle_animation`: cocked
--     recipe but no ore, no recipe
--     (powered or not), circuit-disabled
--   no power, with a recipe and ore    `animation`, frozen on whatever frame
--     (placed so, or cut mid-craft)      the clock is on: not cocked
--   ghost                              not judged (tinted)
--
-- So the idle draws in every stopped state seen except one: no power with a
-- recipe and ore, which shows the main animation frozen. Output full and
-- circuit-disabled crushers had a recipe and ore too, and drew cocked. The
-- only other idle setting the docs list, `always_draw_idle_animation`, was not
-- tried in a client: the docs give it no description, and vanilla sets it true
-- only where the idle is drawn under or instead of the working animation:
-- the electromagnetic plant's base
-- (space-age/prototypes/entity/electromagnetic-plant-pictures.lua) and the
-- centrifuge, which has no `animation` (base/prototypes/entity/entities.lua).
-- Here it would be expected to draw a second, cocked crown over the stroke
-- while it works.
--
-- The switch is a snap, not a fade: when the machine stops, the crown jumps
-- from wherever the stroke stopped to cocked, and when it starts again it
-- jumps back to that frame and carries on from there (the clock is not reset;
-- in the client, one stopped on 5 drew 0 and resumed on 5), so a restart can
-- begin mid-fall. Power restored after a cut resumes the frozen frame (one
-- cut on 14 held 14, and stepped to 15 after the power came back).
--
-- The accents count `animation`'s frames, and its clock advances only while
-- the machine crafts, so they fire only while it works (see "Sound" below).
-- Recorded in the same client: one crown at a time (none drawn twice while
-- working); the first drop after start-up on frame 14, on time; nothing fired
-- at the snap to cocked or back; 15 of 15 accents heard.
--
-- **`animation_speed = 0.2` plays at 0.1 frames a tick, and the recipe is
-- timed to that.** A crafting machine advances its animation by
-- `animation_speed x crafting_speed x animation_progress` a tick, and
-- `CraftingMachineGraphicsSet::animation_progress` defaults to 0.5 (prototype
-- docs, doc-html/types/CraftingMachineGraphicsSet.html; vanilla's assembler
-- sets the same 0.5 explicitly, base/prototypes/entity/assembler-pictures.lua).
-- No graphics set in this file sets it. Measured in a client on the Core,
-- 2026-10-10, 720 ticks, one screenshot of the stroke a tick: 72 frame changes,
-- 0.100 frames a tick, a 240-tick stroke -- 3 strokes against 6 crafts of the
-- old 2 s recipe. Liam kept that rate (a 0.2 in game looked too fast), so
-- `sae-crushing` became 4 s instead (recipes.lua): one drop is one craft at
-- crafting speed 1. `constant_speed` is left false on purpose, per §9: modules
-- should make the hammer fall faster.
--
-- **The status lamp is cut white and tinted by the engine**: a caged lamp on a
-- bracket on the roof's kerb at the south-east, where nothing that moves passes
-- in front of it (moved from the wall above the hatch, where it drew 7x4 px on
-- screen and did not register). It is a status lamp, not a
-- fault lamp: it reports every state, working included, in vanilla's
-- mining-drill colours (below).
local DC = "__space-age-extended__/graphics/entity/drop-crusher/"
local DC_FRAMES = 24
local DC_SPEED = 0.2        -- 0.1 in game: x crafting speed 1 x progress 0.5

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

-- The crusher's three layers, from sheets/meta.json: the plate, the stroke and
-- the shadow. `held` holds the stroke on its frame 0, cocked, for the idle
-- animation; otherwise it plays.
local function dc_layers(held)
  local cocked
  if held then
    cocked = {}
    for i = 1, DC_FRAMES do cocked[i] = 1 end   -- 1-based: the sheet's frame 0
  end
  return
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
    -- collar: one row of 24. Held, `frame_sequence` plays the first of them
    -- 24 times (AnimationFrameSequence: 1-based indices into the sheet, and
    -- the animation's length is the sequence's), and the sheet is still
    -- described as the 24 frames it is.
    {
      filename = DC .. "stroke.png",
      priority = "high",
      width = 191, height = 136,
      frame_count = DC_FRAMES,
      line_length = 24,
      frame_sequence = cocked,
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
      -- Still one frame, rendered with the weight cocked. The shadows the
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
end

derive.own_graphics(crusher,
{
  status_colors = dc_status_colors(),
  animation = { layers = dc_layers(false) },
  -- At rest, cocked: see "The crusher rests cocked" above.
  idle_animation = { layers = dc_layers(true) },
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

-- Sound: §3.4 of the building spec, signed off by Liam 2026-10-11, its accents
-- softened in the crusher-sound task (round 3, take A, picked by Liam
-- 2026-10-20: "A: no grit"). The files are that take's, written by
-- concept/drop-crusher/sound/round-3/A/option_a.py: drop.ogg is the generator's
-- drop (concept/drop-crusher/sound/drop_crusher_sound.py) rebuilt without its
-- grit layer and then made heavier as round 2's C (round-3/clean_tail.py,
-- round-2/heavier.py); pawl.ogg and trip.ogg are round 2 C's
-- (round-2/C/option_c.py); bed.ogg is the generator's, unchanged. Each take is
-- levelled to the file it replaces, so the volumes are still the generator's
-- VOLUME, levelled as a whole against vanilla's crusher (its loop at 0.8). It
-- replaces assembler 3's working sound, which `derive.own_graphics` left behind
-- as an ungated loop.
--
-- **The working sound is grouped like vanilla's crusher's**, at Liam's word in
-- round 3 ("Yes, like vanilla"). The accents were hardest on the ears "when
-- there is multiple", each machine's stacking on the rest. Vanilla's crusher
-- plays at most three working sounds at once (`max_sounds_per_prototype = 3`,
-- space-age entities.lua), and each accent here carries the aggregation vanilla
-- gives one-shots that can pile up (the biters' and the mech armour's): no more
-- than two of the same sound at once, counting those already playing, the rest
-- dropped rather than turned down. Captured with six crushers working, the
-- bank measured within 1 LU of the bank before the change (T01c).
--
-- **The accents name no visualisation, because the stroke is a layer of the
-- main animation** (see "The stroke is the animation" above), and an accent
-- with no `play_for_working_visualisation` counts the main animation's frames,
-- as assembler 1's do. Its cycle is 24 frames: the stroke's 24, with the plate
-- and shadow repeated to match. At 0.1 frames a tick a frame is 1/6 s and the
-- stroke four seconds, one drop a craft.
derive.working_sound(crusher, {
  -- bed.ogg: a low motor hum -- a 47 Hz rotor, a faint pinion whine and
  -- vanilla's crusher loop an octave down. 8 s, two strokes.
  bed = { filename = "__space-age-extended__/sound/drop-crusher/bed.ogg", volume = 0.8 },
  -- **No accent is on frame 0, because 2.1.21 never fires one there.** Recorded
  -- from a client on the Core, 2026-10-11: with the drop on frame 0 (the seat,
  -- as the loop then started) the pawls and the trip fired on their frames every
  -- stroke and the drop never did -- not when the loop came round, not when the
  -- machine started; the same drop on frame 1 played every stroke, and the
  -- drill's ratchet moved to its stroke's frame 0 fell silent too. `frame`
  -- defaults to 0 (doc-html/types/SoundAccent.html), so 0 reads as unset, and
  -- no vanilla accent is cued to it. derive.working_sound now refuses frame 0.
  -- So the loop starts cocked (above) and the landing falls on frame 14.
  max_sounds_per_prototype = 3,
  accents =
  {
    -- drop.ogg on frame 14: the weight lands seated in the collar there, the end
    -- of the fall from the top at 6. One craft, one bang: an oxide asteroid
    -- breaking, the mech armour landing on rock, and pebbles, pitched down 7
    -- semitones over a 40 Hz iron body; the grit that crackled in its tail is
    -- gone (round 3 A). Off frame 0 it should play on the first stroke after
    -- start-up as well as on every wrap; the recording found frame 0 silent in
    -- both.
    { sound = { filename = "__space-age-extended__/sound/drop-crusher/drop.ogg", volume = 0.35,
                aggregation = { max_count = 2, remove = true, count_already_playing = true } }, frame = 14 },
    -- pawl.ogg on frames 18, 22 and 2: the pawl clicks every fourth frame of
    -- the wind-up from the seat, 14, 18, 22, 2 and 6. Not on 14 or 6, which
    -- carry the drop and the trip; a click under either would not be heard.
    -- Frame 0 falls between 22 and 2, so nothing is lost to it. A cryogenic
    -- plant gear's tooth, pitched down 8 semitones over a 115 Hz iron body
    -- (round 2 C).
    { sound = { filename = "__space-age-extended__/sound/drop-crusher/pawl.ogg", volume = 0.6,
                aggregation = { max_count = 2, remove = true, count_already_playing = true } }, frame = 18 },
    { sound = { filename = "__space-age-extended__/sound/drop-crusher/pawl.ogg", volume = 0.6,
                aggregation = { max_count = 2, remove = true, count_already_playing = true } }, frame = 22 },
    { sound = { filename = "__space-age-extended__/sound/drop-crusher/pawl.ogg", volume = 0.6,
                aggregation = { max_count = 2, remove = true, count_already_playing = true } }, frame = 2 },
    -- trip.ogg on frame 6: the top of the wind-up, where the pawl kicks clear
    -- and the weight is let go. The foundry's clamp and a struck-steel click,
    -- low-passed at 3.5 kHz with its attack rounded (round 1 C, kept in 2 and 3).
    { sound = { filename = "__space-age-extended__/sound/drop-crusher/trip.ogg", volume = 0.5,
                aggregation = { max_count = 2, remove = true, count_already_playing = true } }, frame = 6 }
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
-- **The four inherited fluid connections stay, and the engine draws them.**
--
-- Nothing uses them yet: kamacite's `minable` carries no `required_fluid`, so
-- today they accept nothing. They are kept deliberately, because a mining fluid
-- for this drill is wanted later and the layout had to be settled *before* the
-- model was rendered. A flange added to a finished plate is a repaint of all
-- four directions, and the Vent Pump is the standing proof of how expensive
-- rearranging plumbing after the fact is.
--
-- **Inherited verbatim from the big mining drill, and that is the point.** The
-- shape is vanilla's, so a player who has plumbed one has already learned this
-- one: west and east take a connection a tile north of centre, the south face
-- takes two flanking the centre, and north takes none -- because north is where
-- the ore comes out (`vector_to_place_result` is { 0, -2.85 }).
--
-- **And the plate draws none of them**, as vanilla's drills draw none -- the big
-- mining drill's north sprite is a gantry and two ladders and nothing else. The
-- fittings belong to the fluid box: a stub per face in `pipe_picture` and a
-- blind cap in `pipe_covers`, both rendered from the drill's own model (see
-- "Art" below, where they are set), which the ENGINE stamps at the connections
-- and turns with the drill. Painting flanges into the plate instead would put
-- four visible sockets on a machine that has no use for them, which is the Vent
-- Pump's §19 complaint exactly.
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

-- Art: the Ring Press, option B of five (concept/ballast-drill/options/),
-- rendered in Blender from concept/ballast-drill/model/ballast_drill.py and
-- signed off by Liam at round 7, 2026-10-10.
--
-- A heavy cast ring riding up and down three guide columns round a capped
-- central column that does not move, in a press frame with red-oxide
-- gear-houses, on a raised cast chassis braced by four splayed legs. Nothing
-- about it rises, because the anti-read for this building is a derrick.
--
-- **Rendered, not cut**, as the Drop Crusher and the Reaction Plant are: every
-- pass comes off one model through one calibrated camera (tools/blender/rig.py)
-- on one canvas with the entity origin at its centre, so the layers register by
-- construction. Every size, shift, frame count and line length below is copied
-- from the two meta.json files the packers write; none was measured off a
-- sheet. To regenerate, with any Blender 5 binary:
--
--   BLENDER=<blender> tools/blender/render.sh \
--       concept/ballast-drill/model/ballast_drill.py <scratch> --ports --icon
--
-- then copy <scratch>/sheets/icon.png to graphics/icons/ballast-drill.png, the
-- other <scratch>/sheets/*.png and <scratch>/sheets/ports/*.png into
-- graphics/entity/ballast-drill/, and the numbers out of the two meta.json
-- files into BD_SHEETS and the port sprites below.
--
-- **The body is one plate, the same in all four directions; what turns is the
-- output.** The chute and the ore falling off it are their own layers per
-- direction, as vanilla's big mining drill draws
-- `big-mining-drill-{N,E,S,W}-output`, so the art follows
-- `vector_to_place_result` round when the drill is rotated. The four base and
-- shadow sheets are the one render, kept one per direction so that every
-- direction reads off its own meta.json entry.
--
-- **The chute** is a short drag chain at ground level in the bay the ore leaves
-- by, inside the footprint with its mouth at the face edge, and drawn empty: the
-- template's convention 1, draw the chute and never what comes out of it. The
-- plate closes every bay with a flush bolted hatch, and the chute covers the
-- hatch of the face it uses. It is an always-drawn working visualisation, as
-- vanilla's output is, so an idle drill still has its chute; its 5-frame loop
-- runs at vanilla's output speed, 0.5.
--
-- **The stroke is the animation, and the plate does not contain it.** The ring
-- with its hub, spokes, guide shoes and ropes, the press frame and the
-- gear-houses on it are rendered alone, 24 frames, with the surfaces under the
-- ring (its well, step and shoulder) and the shadows they throw on the chassis
-- and the chute; the base sheets are the machine without them. Frame 0 is the
-- ring raised. It is winched up slowly, hangs, falls under gravity and lands
-- dead on the shoulder with a pixel of rebound, and the frame jolts two pixels
-- at the landing (§3.2; the motion was signed off at round 6). The packer
-- holds the ring to the declared curve in every frame (meta.json's
-- `stroke_path_px`).
--
-- **The stroke draws over the chute, so it is a working visualisation and not
-- a layer of the main animation.** The engine draws a drill's working
-- visualisations after its `animation`, in order, and the model's layering is
-- chute first, ring over it: the stroke was rendered with the chute as a
-- catcher, so where the ring stands in front of the north chute, or throws its
-- shadow on the east one, the stroke already carries it. As a main-animation
-- layer it went under the chute, and the north chute's box was drawn across the
-- ring's rim (seen in a client on the Core, 2026-10-10). So the stroke is an
-- `always_draw` visualisation listed after the chute. It behaves as the main
-- animation did, measured in the same client both ways: it draws in every
-- state, advances 0.4 frames a tick while mining, and holds still, pixel for
-- pixel, on a drill whose output is blocked.
--
-- **The dust and the ore are the ore's colour, not the drill's.** Both are
-- rendered neutral pale grey and tinted by the engine (`apply_tint =
-- "resource-color"`, as vanilla's big drill tints its output particles), so a
-- drill throws the dust of whatever it is mining. Neither is `always_draw`, so
-- an idle drill draws neither, and `synced_fadeout` fades them with the drill,
-- as vanilla's. The dust is a low ring breaking out from under the ring at the
-- landing and settling before the next lift: 24 frames at the stroke's speed,
-- empty between landings, so it lands with the ring. The ore falls off the
-- chute's mouth.
--
-- **The status lamp is cut white and tinted by the engine**, as the Drop
-- Crusher's is: `apply_tint = "status"` hands the colour to the engine,
-- `always_draw` lets an idle drill say so, and it is the one thing on the
-- machine drawn as glow (§3.3: nothing here is hot).
--
-- **`animation_speed` is 0.4, and the engine plays 0.4**: 24 frames over 60
-- ticks is the "slow, heavy, one-second stroke" §3.2 asks for, at
-- `mining_speed = 3.0`. A drill is not a crafting machine:
-- `MiningDrillGraphicsSet::animation_progress` defaults to 1 (prototype docs,
-- doc-html/types/MiningDrillGraphicsSet.html; vanilla's electric and big drills
-- set the same 1, base/prototypes/entity/mining-drill.lua and
-- space-age/prototypes/entity/big-mining-drill.lua), and the declared rate is
-- not multiplied by `mining_speed`. Measured in a client on the Core,
-- 2026-10-10, 720 ticks mining kamacite, one screenshot of the stroke a tick:
-- 288 frame changes, 0.400 frames a tick, a 60-tick loop.
local BD = "__space-age-extended__/graphics/entity/ballast-drill/"
local BD_FRAMES = 24
local BD_SPEED = 0.4             -- 0.4 in game: a drill's progress is 1
local BD_CHUTE_SPEED = 0.5       -- vanilla's: big-mining-drill's output chain
local BD_DIRECTIONS = { "north", "east", "south", "west" }

-- From sheets/meta.json, per direction: width, height, shift, and for an
-- animation its frame count and line length.
local BD_SHEETS =
{
  north =
  {
    base = { 326, 358, { 0, -0.25 } },
    ["base-shadow"] = { 370, 329, { 0.375, -0.05469 } },
    stroke = { 310, 317, { 0.09375, -0.55469 }, 24, 24 },
    chute = { 56, 37, { 0, -2.32031 }, 5, 5 },
    ore = { 41, 32, { 0.00781, -2.8125 }, 24, 24 },
    dust = { 260, 271, { 0.03125, -0.52344 }, 24, 24 },
    ["status-lamp"] = { 13, 13, { -1.05469, 0.83594 } }
  },
  east =
  {
    base = { 326, 358, { 0, -0.25 } },
    ["base-shadow"] = { 370, 329, { 0.375, -0.05469 } },
    stroke = { 310, 317, { 0.09375, -0.55469 }, 24, 24 },
    chute = { 58, 58, { 2.0625, -0.09375 }, 5, 5 },
    ore = { 35, 44, { 2.74219, -0.0625 }, 24, 24 },
    dust = { 260, 271, { 0.03125, -0.52344 }, 24, 24 },
    ["status-lamp"] = { 13, 13, { -1.05469, 0.83594 } }
  },
  south =
  {
    base = { 326, 358, { 0, -0.25 } },
    ["base-shadow"] = { 370, 329, { 0.375, -0.05469 } },
    stroke = { 310, 317, { 0.09375, -0.55469 }, 24, 24 },
    chute = { 56, 63, { 0.01562, 2.00781 }, 5, 5 },
    ore = { 41, 39, { 0.00781, 2.69531 }, 24, 24 },
    dust = { 260, 271, { 0.03125, -0.52344 }, 24, 24 },
    ["status-lamp"] = { 13, 13, { -1.05469, 0.83594 } }
  },
  west =
  {
    base = { 326, 358, { 0, -0.25 } },
    ["base-shadow"] = { 370, 329, { 0.375, -0.05469 } },
    stroke = { 313, 317, { 0.07031, -0.55469 }, 24, 24 },
    chute = { 58, 58, { -2.0625, -0.09375 }, 5, 5 },
    ore = { 35, 42, { -2.74219, -0.07812 }, 24, 24 },
    dust = { 260, 271, { 0.03125, -0.52344 }, 24, 24 },
    ["status-lamp"] = { 13, 13, { -1.05469, 0.83594 } }
  }
}

--- One direction's sheet, <name>-<direction>.png, from BD_SHEETS.
local function bd_sheet(name, direction, extra)
  local m = BD_SHEETS[direction][name]
  local sheet =
  {
    filename = BD .. name .. "-" .. direction .. ".png",
    priority = "high",
    width = m[1], height = m[2],
    frame_count = m[4] or 1,
    line_length = m[5],
    shift = { m[3][1], m[3][2] },
    scale = 0.5
  }
  for k, v in pairs(extra or {}) do sheet[k] = v end
  return sheet
end

--- A working visualisation drawing <name> per direction, and called <name>:
--- a sound accent can only be cued to a visualisation that has a `name`
--- (SoundAccent::play_for_working_visualisation), and the drill's are cued to
--- "stroke" (below).
local function bd_visualisation(name, extra, visualisation)
  visualisation.name = name
  for _, d in ipairs(BD_DIRECTIONS) do
    visualisation[d .. "_animation"] = bd_sheet(name, d, extra)
  end
  return visualisation
end

-- The main animation per direction: the plate and its shadow, one frame each
-- repeated to the stroke's count, so the drill's own clock runs the stroke's
-- 24 frames at the stroke's rate. The stroke itself is a working
-- visualisation, below, because it has to draw over the chute.
local bd_animation = {}
for _, d in ipairs(BD_DIRECTIONS) do
  bd_animation[d] =
  {
    layers =
    {
      bd_sheet("base", d, { repeat_count = BD_FRAMES, animation_speed = BD_SPEED }),
      -- Still one frame. The ring moves 12 px within a shadow plate 370 wide,
      -- and its shadow on the chassis is in the stroke layer and travels with
      -- it; its ground shadow does not. A choice, not an oversight.
      bd_sheet("base-shadow", d,
        { draw_as_shadow = true, repeat_count = BD_FRAMES, animation_speed = BD_SPEED })
    }
  }
end

local function bd_port(file, width, height, shift)
  return
  {
    filename = BD .. file .. ".png",
    priority = "extra-high",
    width = width, height = height,
    shift = shift,
    scale = 0.5
  }
end

-- The fluid fittings, from sheets/ports/meta.json: rendered from the model in
-- its own cast iron to assembler 3's outline, one stub per face on the face's
-- middle tile, each shifted from the tile outside its port -- the one a pipe
-- picture is drawn relative to -- so the same sheet sits right at either port
-- on a face. The covers are the model's blind caps, drawn only while nothing
-- is plumbed to a port; `secondary_draw_orders` puts a north stub behind the
-- building, as assembler 3's does.
drill.input_fluid_box.pipe_picture =
{
  north = bd_port("port-N", 53, 22, { 0.00781, 0.34375 }),
  east = bd_port("port-E", 31, 71, { -0.72656, 0.05469 }),
  south = bd_port("port-S", 63, 69, { -0.00781, -0.77344 }),
  west = bd_port("port-W", 31, 72, { 0.72656, 0.01562 })
}
drill.input_fluid_box.pipe_covers =
{
  north = bd_port("cover-N", 53, 22, { 0.00781, 0.34375 }),
  east = bd_port("cover-E", 31, 71, { -0.72656, 0.05469 }),
  south = bd_port("cover-S", 63, 69, { -0.00781, -0.77344 }),
  west = bd_port("cover-W", 31, 72, { 0.72656, 0.01562 })
}
drill.input_fluid_box.always_draw_covers = false
drill.input_fluid_box.secondary_draw_orders = { north = -1 }
-- The big mining drill draws a second, plumbed copy of itself while it mines
-- with a fluid, and the copy came across with the deepcopy: on an ore that asks
-- for one, this drill wore vanilla's whole sprite set (seen in a client,
-- 2026-10-10, with a probe making kamacite ask for water). Without it the
-- engine draws `graphics_set` wet or dry, and the fittings above are the
-- plumbing.
drill.wet_mining_graphics_set = nil

-- The status lamp's colours: vanilla's electric mining drill's
-- (`electric_mining_drill_status_colors`, base/prototypes/entity/mining-drill.lua),
-- as the Drop Crusher's lamp has them, and with `no_minable_resources`, the
-- state a drill has and a crafter does not. Red is idle or out of ore, yellow
-- is blocked, disabled or browned out, green is working.
local function bd_status_colors()
  return
  {
    no_power = { 0, 0, 0, 0 },          -- dark: nothing to report with
    idle = { 1, 0, 0, 1 },
    no_minable_resources = { 1, 0, 0, 1 },
    insufficient_input = { 1, 0, 0, 1 },
    full_output = { 1, 1, 0, 1 },
    disabled = { 1, 1, 0, 1 },
    working = { 0, 1, 0, 1 },
    low_power = { 1, 1, 0, 1 }
  }
end

drill.icon = "__space-age-extended__/graphics/icons/ballast-drill.png"
drill.icons = nil
derive.own_graphics(drill,
{
  status_colors = bd_status_colors(),
  animation = bd_animation,
  working_visualisations =
  {
    bd_visualisation("chute", { animation_speed = BD_CHUTE_SPEED }, { always_draw = true }),
    -- After the chute: see "The stroke draws over the chute" above.
    bd_visualisation("stroke", { animation_speed = BD_SPEED }, { always_draw = true }),
    bd_visualisation("ore", { animation_speed = BD_SPEED },
      { apply_tint = "resource-color", synced_fadeout = true }),
    bd_visualisation("dust", { animation_speed = BD_SPEED },
      { apply_tint = "resource-color", synced_fadeout = true }),
    bd_visualisation("status-lamp", { draw_as_glow = true },
      { always_draw = true, apply_tint = "status" })
  }
})

-- Sound: §3.4 of the building spec, signed off by Liam 2026-10-11. The files
-- are built by concept/ballast-drill/sound/ballast_drill_sound.py, and each
-- volume here is that script's VOLUME, levelled against the big mining drill's
-- own mix. It replaces the big mining drill's working sound, which
-- `derive.own_graphics` had already removed whole: it walks `main_sounds` as a
-- list, and the big drill's is a single Sound, so it found nothing to keep and,
-- with no `sound` either, dropped the working sound (the start accent went with
-- the art it was cued to). Its loop was not cued to any art.
--
-- **The big drill's own two loops go too, so the drill plays only its bed,
-- landing and ratchet.** `drilling_sound` (its drilling loop, two at most) and
-- `moving_sound` (its head turning) came across with the deepcopy and played
-- under ours: a vanilla machine's voice under the one the spec signed off, and
-- the drilling loop doubling the bed's job. Its open and close sounds stay;
-- they are the GUI's, not the machine's.
--
-- The accents are cued to the "stroke" visualisation, whose 24 frames are one
-- second at 0.4 frames a tick (see "Art" above). Frame 0 is the ring raised.
--
-- **The landing aggregates and the drill is capped, so a row of drills rumbles
-- rather than stacks**, as vanilla's big mining drill keeps its own drilling
-- loop to two (its `drilling_sound`, space-age/prototypes/entity/big-mining-drill.lua,
-- the loop this drill no longer plays: see above).
-- `aggregation` is Sound::aggregation, an AggregationSpecification in the
-- prototype docs (doc-html/types/AggregationSpecification.html): at most 2
-- landings at once, counting those already playing, and any more are dropped
-- rather than turned down. `max_sounds_per_prototype` is WorkingSound's
-- (doc-html/types/WorkingSound.html): at most 2 drills play their working
-- sound at all.
derive.working_sound(drill, {
  -- bed.ogg: a low, slow winch drone -- the big mining drill's working loop
  -- pitched down 7 semitones, over a 41 Hz drone and a rumble. 6 s, so it
  -- never pulses against the one-second stroke.
  bed = { filename = "__space-age-extended__/sound/ballast-drill/bed.ogg", volume = 0.3 },
  accents =
  {
    -- landing.ogg on frame 5: the ring lands on the shoulder there (0.208 s
    -- into the stroke), with the dust breaking out under it. The building's
    -- voice, built on the stomper's stomp.
    {
      sound =
      {
        filename = "__space-age-extended__/sound/ballast-drill/landing.ogg",
        volume = 0.55,
        aggregation = { max_count = 2, remove = true, count_already_playing = true }
      },
      visualisation = "stroke",
      frame = 5
    },
    -- ratchet.ogg on frame 23: the top of the lift (0.958 s), the last frame
    -- before the loop comes round to the ring raised. A small tick, from the
    -- first tooth of the oil refinery's gear sound.
    {
      sound = { filename = "__space-age-extended__/sound/ballast-drill/ratchet.ogg", volume = 0.6 },
      visualisation = "stroke",
      frame = 23
    }
  },
  max_sounds_per_prototype = 2
})
drill.drilling_sound = nil
drill.moving_sound = nil
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
-- Plant's are from its four, one a direction; none was measured off a sheet or
-- typed from memory. The needle is the one layer meta.json does not carry; its
-- own comment says where its numbers come from.
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
--
-- **`VF_SPEED` is 2/3 so the game plays the preview's 0.5 frames a tick.** A
-- crafting machine advances by `animation_speed x crafting_speed x
-- animation_progress`, and `animation_progress` defaults to 0.5 (see the Drop
-- Crusher's note), so 2/3 x 1.5 x 0.5 = 0.5, a 32-tick loop. At 0.5 it played
-- 0.375 (measured in a client on the Core, 2026-10-10: 270 frame changes in
-- 720 ticks), slower than the preview Liam approved, and he asked for it sped
-- back up. Speed modules still turn it faster, as they do any crafter's.
local VF_FRAMES = 16
local VF_SPEED = 2 / 3                    -- 0.5 in game: x 1.5 x progress 0.5
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
-- **5x5, the oil refinery's footprint** (spec §2; Liam, 2026-10-11: "Make the
-- reaction plant 5x5 so any tall parts can mostly remain inside the grid as
-- per the FFF"). It was a 3x3 on the chemical plant's footprint, and it is
-- still derived from the chemical plant -- the machine it is shaped after, and
-- the one whose rotation it keeps (below) -- with the boxes, health and
-- remnants of a 5x5 laid over the copy. Plants placed at 3x3 will overlap their
-- neighbours: no migrations before 1.0 (Liam, 2026-10-11).
--
-- Three boxes: two in on the north face, either side of the centre column at
-- {-1, -2} and {1, -2}, and one out at the south face's centre, {0, 2}.
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
-- on a recipe whose products are solid behaves identically. Measured, both
-- (at 3x3, 2.1.19).
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
-- **The fittings are modelled into the plate, one plate per direction, and the
-- building turns with them** (spec §5, §7, §8; Liam, 2026-10-20, reversing the
-- 2026-09-17 one plate). Each connection enters the housing's wall through a
-- fitting that is part of that direction's render and casts and takes its own
-- shadows, so there is no `pipe_picture`: the engine draws nothing at a port
-- but vanilla's cover on one nothing is joined to. The entity carries no
-- `not-rotatable` flag; the two inputs sit on the faced side and the output
-- opposite, in every direction.
--
-- `pipe_covers` are vanilla's (`derive.pipe_covers()`, spec §8);
-- `always_draw_covers = false` takes the cap away once a pipe arrives;
-- `secondary_draw_orders = { north = -1 }` puts a north cover behind the
-- building, as vanilla's assemblers set it.
--
-- `sae-reaction` is private like every other category in this file, and here
-- that cuts both ways: a vanilla chemical plant must not be able to make the
-- Core's fuel, and this plant must not be able to run chemistry.
--------------------------------------------------------------------------------

-- Art: F, the Circulator in its casing, rendered in Blender from
-- concept/reaction-plant/model/forms.py (RP_FORM=casing) in four directions and
-- signed off by Liam, 2026-10-28 ("Sign off pump and plant"); with a sight glass
-- on each input line and low stubs at the connections, signed off 2026-10-29.
--
-- **Rendered, not cut.** There is no master plate: every pass is rendered from
-- one model, through one calibrated camera (tools/blender/rig.py), on one canvas
-- with the entity origin at the canvas centre. So the layers register by
-- construction, and every size, shift, frame count and line length below is
-- computed by the packer and copied from the meta.json it writes for each
-- direction -- none of them was measured off a sheet. To regenerate, with any
-- Blender 5 binary, one run a direction (spec §0):
--
--   RP_FORM=casing RP_DIRECTION=<north|east|south|west> BLENDER=<blender> \
--       tools/blender/render.sh concept/reaction-plant/model/forms.py <scratch>
--
-- (the north run with --icon as well), then copy each run's <scratch>/sheets/
-- *.png into graphics/entity/reaction-plant/<direction>/, the icon to
-- graphics/icons/reaction-plant.png, the figures of each sheets/meta.json into
-- RP_SHEETS and the connector sockets of hi/model.json into RP_SOCKETS. The
-- pack's checks hold in every direction (edge_alpha_max 0, legs-glow_white_px
-- 0, the press within 1 px of its declared path); north and south are exactly
-- 5.000 tiles wide, and east and west reach one faint pixel (alpha 29 or less)
-- past it, accepted at sign-off (Liam, 2026-10-28: "Accept, note in spec").
--
-- **Four plates, one a direction** (spec §5): the model is turned on its
-- turntable to face each direction, as vanilla's chemical plant and oil
-- refinery are, and each direction has its own plate, shadow, legs, glow,
-- lamps, press and moving parts. A part the camera does not see in a
-- direction has no sheet there and stands in the plate at frame 0.
--
-- **The plate is the machine without its moving parts**, and every moving part
-- is its own cropped sheet drawn over it (spec §6.2, §7). Seen in each
-- direction:
--
--   north  legs, drive, compressor, dosing-pump and pump couplings, press,
--          the three gauge needles, condenser drip
--   east   as north, without the dosing-pump coupling
--   south  legs, drive, compressor and pump couplings, press
--   west   legs, drive, dosing-pump coupling, press
--
-- and every direction has its plate, shadow, legs glow, status lamps and both
-- sight glasses (below). The plate's legs are unlit dark navy; the lit legs are
-- drawn over them only while crafting. No two moving sheets of one direction
-- share an opaque pixel at frame 0 (each was rendered with the rest of the
-- model held out), so the order they are drawn in does not show.
--
-- **The 24-frame parts play at 14/60 frames a tick, a loop in ~1.7 s**
-- (measures.txt), in the main animation, which an assembling machine draws in
-- every state and advances only while crafting. The layers of one Animation all
-- run at the first layer's speed (Animation::layers, 2.1.22 docs), so the plate
-- and shadow, one frame each, are repeated 24 times and carry the same speed.
--
-- **`animation_progress = 1`, so that speed is the rate in game.** A crafting
-- machine advances by `animation_speed x crafting_speed x animation_progress`
-- a tick, and `animation_progress` defaults to 0.5 (see the Drop Crusher's
-- note): left there, the press would run once every two crafts and the loops at
-- 7 fps. The spec's numbers -- 14 fps for the loops, and the press's 140
-- entries in 1200 ticks, one 20 s craft -- are rates in game, so this set says
-- 1 rather than doubling every speed. Every machine above keeps the default.
--
-- **The press is its own working visualisation** (Liam, 2026-10-20: "Own
-- working visualisation"), once per craft. Its clock is the machine's: it starts
-- at zero, advances only while the machine crafts and at the craft's own rate
-- (slowed when browned out, sped by modules), and is never reset; so one cycle
-- is one craft and the two stay in step (below).
-- Its 16 frames, each shown twice, then frame 1 held 108 times: 140 entries
-- (AnimationFrameSequence holds 255) at 7/60 entries a tick is 1200 ticks, one
-- craft of `sae-radiant-precipitation` (20 s) at crafting speed 1. Seven
-- entries a second, two to a frame: each frame of the stroke holds ~17 ticks,
-- 3.5 frames a second, and the stroke takes ~4.6 s (measured in T04). Frames
-- 1-4 (0-based) open it west, 5 the cake hangs, 6-9 it falls, 10 it lands in
-- the drop box, 11-15 it closes. A visualisation of its own because it cannot
-- be a layer of the main animation: at the parts' 14/60, 140 entries' worth of
-- hold would need 280, past the limit.
--
-- **Stopped, the press stays where it stopped: it is `always_draw`, because
-- `idle_animation` is never drawn on this plant** (Liam, 2026-10-20: "Find out
-- why, then fix", the fallback if the idle could not be made to draw). The
-- engine draws a crafting machine's `idle_animation` only while it has no live
-- fluid boxes, and this plant keeps its boxes in every state (above). Measured
-- in a client on the Core, 2026-10-20 (T02b), with each variant's idle tinted
-- red, unpowered, powered with no recipe, with a recipe and no input, working
-- and after a power cut. The plant as wired drew its frozen `animation` in
-- every stopped state and never the idle, and so did each variant with one
-- thing changed: no `animation_progress`, no `use_mirroring`, the crusher's
-- `perceived_performance`, a random start frame, an idle without the press, no
-- working visualisations, `always_draw_idle_animation`, a 4-way animation.
-- With its fluid boxes removed, its idle drew. With
-- `fluid_boxes_off_when_no_fluid_recipe` true it drew only with no recipe, when
-- the engine had switched the boxes off, and assembling machine 2 likewise.
-- The Drop Crusher has no fluid boxes, which is why its idle draws. So there is
-- no `idle_animation` here: it could only ever have been dead weight.
--
-- Visual `states` (the electromagnetic plant's) can draw a shut press whenever
-- the machine stops -- the same client drew one in every stopped state -- but a
-- visualisation gated by a state plays from the moment its state began, so a
-- press held to "working" restarted every time the state renewed and never left
-- frame 0. Keeping it once a craft that way means a chain of states timed to the
-- stroke, which would tie the press to the states rather than the craft: not
-- done.
--
-- **In practice a stopped plant shows its press shut, all but after a power
-- cut.** The press's clock and the craft move together, so each stroke opens a
-- craft, and a plant that stops for want of input or room stops between crafts,
-- on the shut hold. Measured in the same client (T02b), one press shot every 2
-- ticks over three crafts, the power cut for 90 ticks of every 250, then the
-- inputs starved: strokes began at r118, 1318, 2518 and 3822, each 18 ticks
-- (two entries of frame 1) after its craft began; every shot of the plant
-- stopped for want of input showed it shut. Only a stop in mid-craft -- the
-- power going -- can catch it open: cut 120 working ticks into a craft, it
-- stood open on its frame 7 with the cake falling, and a cut during a stroke
-- held it with the cake hanging (frame 4 or 5) until the power came back and
-- it carried on.
--
-- **The legs glow only while crafting, at one strength.** legs.png is the lit
-- legs, 24 frames, and legs-glow.png is the lit render minus the plate. The
-- glow is `draw_as_light`, so it lights the legs at night without being added
-- a second time over the lit legs by day, as an additive `draw_as_glow` would.
--
-- **Two status lamps, on the pump house and the instrument house**, in one
-- sheet, cut white and tinted by the engine. `always_draw`, because a lamp that
-- only appears while working cannot report that the machine has stopped.
--
-- **A sight glass on each input line shows the fluid in it** (spec §8; Liam,
-- 2026-10-28, T09c: "Adopt", "Sight glass"). sight-glass-1 is the line from the
-- {-1, -2} fitting, sight-glass-2 the line from {1, -2}; each is one white
-- sheet a direction, one frame, which the engine tints with the recipe's
-- colour for that line (`apply_recipe_tint`). Facing east sight-glass-1 is the
-- glass on the riser, where the camera cannot see the first one (T09d2).
-- `always_draw`: the glass shows what the line holds whether or not the
-- machine is crafting; with no recipe both are a neutral grey
-- (`recipe_not_set_tint`).
--
-- Ordinary paint, not `draw_as_light` or `draw_as_glow`, as the Gas Pump's
-- glass is (crust-tap.lua): it is fluid seen through glass, not a lamp, and a
-- light-only layer is drawn in the light map alone, so it would not show by
-- day. meta.json's `kind = "light"` is the render pipeline's name for a white
-- layer the engine tints.
--
-- **Mirrored, the two lines trade fluids, and the glasses trade tints.** The
-- engine draws a mirrored plant's sprites unmirrored and moves its fluid boxes
-- to the other side: box 1, the recipe's first fluid, then enters at {1, -2},
-- on sight-glass-2's line. `graphics_set_flipped`, which the engine draws in
-- place of `graphics_set` on a mirrored plant, is the same set with the two
-- glasses' tints swapped. Measured in the T09c spike (evidence/rp-t09c), 8 of 8
-- cases: north and east, normal and mirrored, either fluid first.
local RP = "__space-age-extended__/graphics/entity/reaction-plant/"
local RP_FRAMES = 24
local RP_SPEED = 14 / 60                  -- in game: animation_progress 1, below
local RP_PRESS_SPEED = 7 / 60
local RP_PRESS_FRAMES = 16
local RP_PRESS_LENGTH = 140               -- 140 / (7/60) = 1200 ticks, one craft

-- From each direction's sheets/meta.json: size in px, shift in tiles, and the
-- frames and line length of each sheet that moves. A direction has a sheet for
-- each part the camera sees there, and no other (spec §6.2).
local RP_SHEETS =
{
  north =
  {
    ["base"] = { width = 327, height = 367, shift = { -0.00781, -0.32031 } },
    ["shadow"] = { width = 360, height = 329, shift = { 0.3125, -0.05469 } },
    ["legs-glow"] = { width = 188, height = 57, shift = { -0.01562, 0.13281 } },
    ["status-lamp"] = { width = 14, height = 216, shift = { 2.29688, 0.17188 } },
    ["sight-glass-1"] = { width = 16, height = 19, shift = { -1.17188, -1.17969 } },
    ["sight-glass-2"] = { width = 15, height = 23, shift = { 1.53906, -2.05469 } },
    ["legs"] = { width = 189, height = 61, shift = { -0.02344, 0.11719 }, frames = 24, line_length = 24 },
    ["drive"] = { width = 64, height = 60, shift = { -0.0625, -2.10938 }, frames = 24, line_length = 24 },
    ["coupling-compressor"] = { width = 7, height = 20, shift = { 1.94531, -2.375 }, frames = 24, line_length = 24 },
    ["coupling-dosing"] = { width = 7, height = 15, shift = { -0.44531, 0.42969 }, frames = 24, line_length = 24 },
    ["coupling-pump"] = { width = 10, height = 18, shift = { 2.03125, 1.375 }, frames = 24, line_length = 24 },
    ["press"] = { width = 53, height = 65, shift = { -2.10156, 1.52344 }, frames = 16, line_length = 16 },
    ["gauge-reactor-upper"] = { width = 10, height = 5, shift = { 0.03125, -0.10156 }, frames = 24, line_length = 24 },
    ["gauge-reactor-lower"] = { width = 10, height = 7, shift = { -0.17188, 0.24219 }, frames = 24, line_length = 24 },
    ["gauge-scrubber"] = { width = 8, height = 7, shift = { -1.5, -2.02344 }, frames = 24, line_length = 24 },
    ["drip"] = { width = 23, height = 36, shift = { 2.21094, -0.03125 }, frames = 24, line_length = 24 }
  },
  east =
  {
    ["base"] = { width = 327, height = 381, shift = { -0.00781, -0.39844 } },
    ["shadow"] = { width = 353, height = 344, shift = { 0.25781, -0.09375 } },
    ["legs-glow"] = { width = 34, height = 210, shift = { -0.73438, -0.59375 } },
    ["status-lamp"] = { width = 189, height = 41, shift = { -0.82031, 1.64844 } },
    ["sight-glass-1"] = { width = 14, height = 7, shift = { 2.0, -0.47656 } },
    ["sight-glass-2"] = { width = 18, height = 14, shift = { 0.9375, 0.46875 } },
    ["legs"] = { width = 35, height = 213, shift = { -0.74219, -0.60156 }, frames = 24, line_length = 24 },
    ["drive"] = { width = 59, height = 65, shift = { 0.25781, -1.91406 }, frames = 24, line_length = 24 },
    ["coupling-compressor"] = { width = 16, height = 6, shift = { 1.75, 1.25 }, frames = 24, line_length = 24 },
    ["coupling-pump"] = { width = 17, height = 10, shift = { -1.94531, 1.42188 }, frames = 24, line_length = 24 },
    ["press"] = { width = 46, height = 52, shift = { -1.98438, -2.73438 }, frames = 16, line_length = 16 },
    ["gauge-reactor-upper"] = { width = 5, height = 11, shift = { -0.75781, -0.82031 }, frames = 24, line_length = 24 },
    ["gauge-reactor-lower"] = { width = 4, height = 10, shift = { -0.76562, -0.67188 }, frames = 24, line_length = 24 },
    ["gauge-scrubber"] = { width = 6, height = 8, shift = { 1.29688, -2.23438 }, frames = 24, line_length = 24 },
    ["drip"] = { width = 37, height = 33, shift = { -0.44531, 1.66406 }, frames = 24, line_length = 24 }
  },
  south =
  {
    ["base"] = { width = 327, height = 355, shift = { 0.00781, -0.28906 } },
    ["shadow"] = { width = 365, height = 329, shift = { 0.35156, -0.07031 } },
    ["legs-glow"] = { width = 188, height = 56, shift = { -0.01562, -1.3125 } },
    ["status-lamp"] = { width = 13, height = 164, shift = { -2.28906, -1.46875 } },
    ["sight-glass-1"] = { width = 91, height = 104, shift = { 0.58594, 0.75 } },
    ["sight-glass-2"] = { width = 14, height = 15, shift = { -1.53125, -0.16406 } },
    ["legs"] = { width = 189, height = 60, shift = { -0.02344, -1.32812 }, frames = 24, line_length = 24 },
    ["drive"] = { width = 64, height = 61, shift = { 0.0625, -1.60156 }, frames = 24, line_length = 24 },
    ["coupling-compressor"] = { width = 7, height = 20, shift = { -1.94531, 1.125 }, frames = 24, line_length = 24 },
    ["coupling-pump"] = { width = 10, height = 19, shift = { -2.03125, -2.50781 }, frames = 24, line_length = 24 },
    ["press"] = { width = 53, height = 65, shift = { 2.10156, -2.44531 }, frames = 16, line_length = 16 }
  },
  west =
  {
    ["base"] = { width = 327, height = 375, shift = { 0.00781, -0.35156 } },
    ["shadow"] = { width = 344, height = 335, shift = { 0.21875, -0.02344 } },
    ["legs-glow"] = { width = 34, height = 207, shift = { 0.70312, -0.57031 } },
    ["status-lamp"] = { width = 189, height = 25, shift = { 0.82031, -2.94531 } },
    ["sight-glass-1"] = { width = 19, height = 18, shift = { -0.63281, 0.65625 } },
    ["sight-glass-2"] = { width = 21, height = 19, shift = { -0.96094, -2.61719 } },
    ["legs"] = { width = 35, height = 210, shift = { 0.69531, -0.57812 }, frames = 24, line_length = 24 },
    ["drive"] = { width = 59, height = 65, shift = { -0.25781, -1.78906 }, frames = 24, line_length = 24 },
    ["coupling-dosing"] = { width = 6, height = 4, shift = { 1.03125, -0.17188 }, frames = 24, line_length = 24 },
    ["press"] = { width = 46, height = 72, shift = { 1.98438, 1.65625 }, frames = 16, line_length = 16 }
  }
}

local RP_DIRECTIONS = { "north", "east", "south", "west" }

-- The 24-frame parts of the main animation, drawn over the plate in this order
-- where the direction has them.
local RP_PARTS =
{
  "drive", "coupling-compressor", "coupling-dosing", "coupling-pump",
  "gauge-reactor-upper", "gauge-reactor-lower", "gauge-scrubber", "drip"
}

-- The sheets every direction has: the plate and its shadow, the lit legs and
-- their light, the lamps, the press and the two sight glasses.
local RP_ALWAYS = { "base", "shadow", "legs", "legs-glow", "status-lamp", "press",
                    "sight-glass-1", "sight-glass-2" }

-- Every sheet of a direction is drawn: either a part above, or one of these.
-- A sheet packed for a direction and not wired would be a part frozen in the
-- plate; one wired and not packed, a file that does not exist.
local RP_DRAWN = {}
for _, name in ipairs(RP_ALWAYS) do RP_DRAWN[name] = true end
for _, name in ipairs(RP_PARTS) do RP_DRAWN[name] = true end
for _, dir in ipairs(RP_DIRECTIONS) do
  for _, name in ipairs(RP_ALWAYS) do
    assert(RP_SHEETS[dir][name], "sae-reaction-plant: no " .. name .. " sheet facing " .. dir)
  end
  for name in pairs(RP_SHEETS[dir]) do
    assert(RP_DRAWN[name], "sae-reaction-plant: sheet " .. dir .. "/" .. name .. " is not drawn")
  end
end

--- One direction's sheet as an Animation, its numbers from RP_SHEETS; `extra`
--- adds to or overrides them.
local function rp_sheet(dir, name, extra)
  local s = RP_SHEETS[dir][name]
  local anim =
  {
    filename = RP .. dir .. "/" .. name .. ".png",
    priority = "high",
    width = s.width, height = s.height,
    frame_count = s.frames or 1,
    line_length = s.line_length,
    shift = s.shift,
    scale = 0.5
  }
  for k, v in pairs(extra or {}) do anim[k] = v end
  return anim
end

--- A working visualisation with four animations, one sheet a direction, as
--- `north_animation` .. `west_animation`; `vis` holds its other fields.
local function rp_four(name, extra, vis)
  vis = vis or {}
  for _, dir in ipairs(RP_DIRECTIONS) do
    vis[dir .. "_animation"] = rp_sheet(dir, name, extra)
  end
  return vis
end

-- The press's sequence: each of its 16 frames twice, then shut (frame 1) for
-- the rest of the craft.
local RP_PRESS_SEQUENCE = {}
for f = 1, RP_PRESS_FRAMES do
  RP_PRESS_SEQUENCE[2 * f - 1] = f
  RP_PRESS_SEQUENCE[2 * f] = f
end
for i = 2 * RP_PRESS_FRAMES + 1, RP_PRESS_LENGTH do RP_PRESS_SEQUENCE[i] = 1 end

--- One direction's main animation: the plate, the 24-frame parts seen in that
--- direction and the shadow, the plate and shadow repeated to the parts' 24
--- frames.
local function rp_direction(dir)
  local layers = { rp_sheet(dir, "base", { repeat_count = RP_FRAMES, animation_speed = RP_SPEED }) }
  for _, name in ipairs(RP_PARTS) do
    if RP_SHEETS[dir][name] then
      layers[#layers + 1] = rp_sheet(dir, name, { animation_speed = RP_SPEED })
    end
  end
  -- The whole machine at frame 0. The moving parts' shadows on the ground do
  -- not move with them: each is a sliver, and no player looks at it.
  layers[#layers + 1] = rp_sheet(dir, "shadow",
    { draw_as_shadow = true, repeat_count = RP_FRAMES, animation_speed = RP_SPEED })
  return { layers = layers }
end

-- **The circuit connector: one a direction, on the terminal box the model
-- carries** (spec §8). Facing each way the box sits on the housing's wall that
-- faces the camera, with its cable gland under it, and the engine's connector is
-- drawn over the box. From the model's hi/model.json (`sockets`, identical in
-- all four runs): `screen` is where the box's centre is drawn, tiles from the
-- entity centre, and `ground` the point on the ground beneath it.
local RP_SOCKETS =
{
  north = { screen = { 0.85, 2.078 }, ground = { 0.85, 2.328 } },
  east = { screen = { -0.95, 2.178 }, ground = { -0.95, 2.428 } },
  south = { screen = { 0, 2.078 }, ground = { 0, 2.328 } },
  west = { screen = { -0.6, 2.178 }, ground = { -0.6, 2.428 } }
}

-- The connector's shadow falls where the rig's sun puts the shadow of a point at
-- the box's height (tools/blender/rig.py, SHADOW_KX and SHADOW_KY, measured off
-- vanilla): a point h' tiles above its foot on screen casts kx * h' right of
-- the foot and ky * h' up. So it lands as the plate's own shadows do.
local RP_SHADOW_KX, RP_SHADOW_KY = 0.79, 0.25
-- Which of the universal connector's 40 drawings stands on the box: 18, the
-- face-on box assembling machines use (spec §13; Liam, 2026-10-28: "18,
-- face-on").
local RP_CONNECTOR_VARIATION = 18
local function rp_circuit_connector()
  local defs = {}
  for i, dir in ipairs(RP_DIRECTIONS) do
    local s = RP_SOCKETS[dir]
    local rise = s.ground[2] - s.screen[2]
    defs[i] =
    {
      variation = RP_CONNECTOR_VARIATION,
      main_offset = s.screen,
      shadow_offset = { s.ground[1] + RP_SHADOW_KX * rise, s.ground[2] - RP_SHADOW_KY * rise },
      show_shadow = true
    }
  end
  return circuit_connector_definitions.create_vector(universal_connector_template, defs)
end

local RP_COVERS = derive.pipe_covers()

-- The status lamps' colours: the ones vanilla's electric mining drill uses
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
    -- No pipe_picture: the fitting is in each direction's plate (above).
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
    reaction_box("input", defines.direction.north, { -1, -2 }),
    reaction_box("input", defines.direction.north, { 1, -2 }),
    reaction_box("output", defines.direction.south, { 0, 2 })
  }
})
-- Undoing `crafter`'s blanket setting for this machine alone: a plant with no
-- recipe has to keep a direction. See the block comment above.
reaction_plant.fluid_boxes_off_when_no_fluid_recipe = false
-- 5x5 over `crafter`'s 3x3 (spec §2), with the oil refinery's health and, until
-- the plant has its own, its remnants and explosion (spec §13, Liam 2026-10-11):
-- the 5x5 vanilla machine they fit.
reaction_plant.collision_box = { { -2.4, -2.4 }, { 2.4, 2.4 } }
reaction_plant.selection_box = { { -2.5, -2.5 }, { 2.5, 2.5 } }
reaction_plant.max_health = 350
reaction_plant.corpse = "oil-refinery-remnants"
reaction_plant.dying_explosion = "oil-refinery-explosion"
-- The chemical plant's connector is placed for a 3x3 plate; this one is on the
-- model's terminal box, one a direction (above).
reaction_plant.circuit_connector = rp_circuit_connector()
-- The lead reactor and its two lit legs (spec §14), a 64 px mipmap strip.
reaction_plant.icon = "__space-age-extended__/graphics/icons/reaction-plant.png"
-- The alt-mode recipe icon at twice the size, as the oil refinery's is (Liam,
-- 2026-10-20: "Double, like the refinery"), at the centre (spec §13; Liam,
-- 2026-10-28: "Centre"). One place for all four directions:
-- IconDrawSpecification has no per-direction form (2.1.22 docs).
reaction_plant.icon_draw_specification = { scale = 2, shift = { 0, 0 } }

-- With no recipe, the glasses' grey: neither fluid, a mid tone between the
-- plate's empty glass and the white sheet.
local RP_NO_RECIPE = { r = 0.5, g = 0.5, b = 0.5 }

--- The plant's graphics set, `line1` and `line2` the recipe tint each sight
--- glass takes: "primary" and "secondary" for `graphics_set`, swapped for
--- `graphics_set_flipped` (see "Mirrored" above). Nothing else differs.
local function rp_graphics_set(line1, line2)
  return
  {
    status_colors = rp_status_colors(),
    animation_progress = 1,               -- see "animation_progress = 1" above
    animation =
    {
      north = rp_direction("north"),
      east = rp_direction("east"),
      south = rp_direction("south"),
      west = rp_direction("west")
    },
    recipe_not_set_tint = { primary = RP_NO_RECIPE, secondary = RP_NO_RECIPE },
    working_visualisations =
    {
      -- The filter press, once a craft: see "The press" above. Named, so the
      -- landing's accent can be cued to it.
      rp_four("press", { frame_sequence = RP_PRESS_SEQUENCE, animation_speed = RP_PRESS_SPEED },
        { name = "press", always_draw = true }),   -- always_draw: see "Stopped" above
      -- The legs, lit and circulating, over the plate's dark ones.
      rp_four("legs", { animation_speed = RP_SPEED }),
      -- Their light: see "The legs glow" above.
      rp_four("legs-glow", { draw_as_light = true }),
      -- The two status lamps.
      rp_four("status-lamp", { draw_as_glow = true }, { always_draw = true, apply_tint = "status" }),
      -- The sight glasses: see "A sight glass on each input line" above.
      rp_four("sight-glass-1", nil, { always_draw = true, apply_recipe_tint = line1 }),
      rp_four("sight-glass-2", nil, { always_draw = true, apply_recipe_tint = line2 })
    }
  }
end

derive.own_graphics(reaction_plant, rp_graphics_set("primary", "secondary"))
reaction_plant.graphics_set_flipped = rp_graphics_set("secondary", "primary")
-- The chemical plant's, kept: a plant can be mirrored (spec §8, constraint 3).
reaction_plant.use_mirroring = true

-- Sound: the chemical plant's loop, kept as the bed, and one accent of ours as
-- the cake lands (spec §12-13).
--
-- **The landing falls on the press sheet's frame 11 (1-based), and which number
-- that is depends on what `frame` counts**, which no client has measured yet
-- (T04). The sequence shows it at its entries 21 and 22 (1-based), 20 and 21
-- counted from 0. Chosen: 21, counting sequence entries, as derive.working_sound
-- counts a cycle (`frame_sequence`'s length) -- and on the landing whether the
-- engine counts entries from 0 or from 1. If it counts the sheet's frames
-- instead, swap to `sprite`: 10, the landing counted from 0, as the Drop
-- Crusher's accent was measured (measures.txt's 11 is the same frame from 1).
-- Never 0: the engine fires nothing there.
--
-- The accent's sound is a stand-in, vanilla's landfill inventory sound, until
-- the plant has its own.
local RP_ACCENT = { sequence = 21, sprite = 10 }
local rp_ws = reaction_plant.working_sound   -- the chemical plant's, ungated
assert(rp_ws and rp_ws.sound, "sae-reaction-plant: the chemical plant's working sound has no loop to keep")
local rp_sound = { accents =
{
  {
    sound = { filename = "__base__/sound/item/landfill-inventory-move.ogg", volume = 0.5 },
    visualisation = "press",
    frame = RP_ACCENT.sequence
  }
} }
for k, v in pairs(rp_ws) do
  if k == "sound" then rp_sound.bed = v elseif k ~= "sound_accents" then rp_sound[k] = v end
end
derive.working_sound(reaction_plant, rp_sound)
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
  -- Plate, pipe and enough circuitry to meter what goes through: the 3x3's
  -- price raised by half as the plant grew to 5x5, toward the refinery's
  -- (Liam, 2026-10-20: "x1.5: 60/30/20, 10 s").
  { "sae-reaction-plant", "h",
    { plate(60), { type = "item", name = "pipe", amount = 30 }, circuit(20) }, 10 },
}) do
  data:extend(machine_item(spec[1], spec[2], spec[3], spec[4]))
end
