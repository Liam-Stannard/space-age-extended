-- The Core's machines, scaled back to the landing: the Drop Crusher, the
-- Ballast Drill and the Vacuum Furnace. The rest are on master.
--
-- Each has a master spec under graphics/, and every number below is read off it
-- rather than invented here; where this file and a spec disagree, the spec is
-- right and this is a bug. Section 2 of each spec is the source.
--
-- **The art is a stand-in and says so.** None of the three has a plate yet. Each
-- borrows the sprites of a vanilla machine of the same footprint, marked by a
-- `derive.placeholder_art` call so `grep` finds every one of them, and logged at
-- data stage so the log does too. That is a different thing from an inherited
-- leftover -- see prototypes/derive.lua, which strips those up front.
--
-- Two of the three are shaped by measurements that cost a spike each, and the
-- shapes are not obvious:
--
--   * The Vacuum Furnace is a `furnace`, not an assembling machine, and its flux
--     box is deliberately large. S12 measured that a furnace with a fluid
--     ingredient refuses its *solid* ingredient until the fluid is already in
--     the machine; a big buffer against a small draw makes that latch rare.
--   * The Crust Tap is an `offshore-pump`, which draws its fluid from the *tile*
--     beneath it and not from its own filter. S10 measured one built on bare
--     ground reporting `working` and producing nothing. It is sited on a vent
--     tile, and the tile is what carries the fluid.

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
  { type = "recipe-category", name = "sae-crushing" }
})

--------------------------------------------------------------------------------
-- Surface conditions, named once.
--
-- Two distinct locks, and the difference is the design rather than a detail.
-- `HIGH_G` is the Core's surface alone: the two gravity machines cannot be
-- carried anywhere else, because gravity is the thing doing their work. `CORE`
-- is the Core and space platforms, for machines whose argument is the absence of
-- atmosphere rather than the presence of weight.
--------------------------------------------------------------------------------

local HIGH_G = { { property = "gravity", min = 45 } }
local CORE = { { property = "pressure", max = 9 } }

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

-- Art: the Sealed Hammer, option A of five (concept/drop-crusher/options/).
--
-- Locked 2026-09-09 and the first design in this mod picked by comparison rather
-- than by refinement: versions 1 to 10 were all the same idea made better, and
-- the round that replaced them drew it against a sibling instead. The decision
-- record and the winner's prompt are in that directory; the sheet is
-- `concept/adopted/A-sheet.png`.
--
-- Two plates cut by tools/process-building-art.py from one master render:
-- **192 px of drawn machine, 3.000 tiles**, sitting 4 px from each side of the
-- canvas and 5 px from top and bottom, with alpha zero along every edge row --
-- checked, because a plate that ends on a razor line has no antialiased rim and
-- the arc mast shipped that way once.
--
-- **The shift is measured, not centred.** This building is taller than it is
-- deep, so the drawn 3x3 box is bottom-aligned in the content and its centre
-- lands 2 source px below the canvas centre. Half a source pixel is half an
-- in-game pixel at scale 0.5, so the plate is pulled up by 1 in-game px --
-- `-0.03125` tiles -- to put the footprint's centre on the entity's origin. The
-- shadow's shift comes out of the same tool rather than being chosen.
--
-- **Nothing on this machine is hot**, which makes it the one building in the set
-- where the status lamp carries the whole read on its own. §3.3 is explicit that
-- there is no glow here: the ore is cold, the fall is free, and the only light is
-- the lens the engine tints.
--
-- **The stroke is animated, and it is drawn the way the biochamber is.** §3.2
-- calls the crown rising and falling "the entire read". Rather than ship 24
-- copies of a 200x206 plate, this is a static housing with one 48x54 window
-- punched out of it and 24 frames of that window laid over the hole -- vanilla's
-- own arrangement in `space-age/prototypes/entity/biochamber-pictures.lua`, and
-- 103,408 px of atlas against 988,800 for a full-plate sheet. The pair is
-- checked to reassemble exactly, frame by frame, by the tool that cuts it.
--
-- **The frames come from Animatorio** (github.com/Onoulade/Animatorio), driven by
-- tools/build-animatorio-layers.py off graphics/entity/drop-crusher/stroke.json.
-- The crown and the shank travel as one part, because the rack is cut into the
-- shank -- and it is the rack's rungs travelling that sells the stroke, more
-- than the crown does.
--
-- **Frame 0 is base.png, byte for byte** -- checked, not assumed. There is no
-- `idle_animation`: §9 records that one would have to carry the same 24 frames,
-- and an assembling machine simply stops on a frame instead. That the frame it
-- stops on is the approved still is the whole reason this loop starts at the top
-- of the stroke and falls, rather than starting at the bottom and rising.
--
-- **`animation_speed` is derived, not chosen.** 24 frames at 0.2 is a two-second
-- loop, and `sae-crushing` is `energy_required = 2` at `crafting_speed = 1` -- so
-- one drop is one craft at the base rate. `constant_speed` is left false on
-- purpose, per §9: modules should make the hammer fall faster. That breaks the
-- one-drop-one-craft correspondence, which §9 is explicit nobody notices.
--
-- base.png stays in the tree and is still the locked plate: it is what the icon
-- is derived from, what the status lamp registers against, and what frame 0 is
-- checked against. It is simply no longer what the entity draws.
local DC = "__space-age-extended__/graphics/entity/drop-crusher/"
local DC_FRAMES = 24
crusher.icon = "__space-age-extended__/graphics/icons/drop-crusher.png"
derive.own_graphics(crusher,
{
  animation =
  {
    layers =
    {
      -- The plate, less the window the stroke moves in. One frame, repeated to
      -- meet the animated layer's count -- the biochamber does exactly this.
      {
        filename = DC .. "stroke-housing.png",
        priority = "high",
        width = 200, height = 206,
        frame_count = 1,
        repeat_count = DC_FRAMES,
        animation_speed = 0.2,
        shift = { 0, -0.03125 },
        scale = 0.5
      },
      -- The window's contents. Its shift is the plate's shift plus the offset of
      -- the window's centre from the plate's: the window is 79..127 x 0..54 on a
      -- 200x206 canvas, so its centre sits 3 px right and 76 px up of the
      -- canvas centre. 64 source px to the tile at scale 0.5, giving 3/64 and
      -- -76/64, and -0.03125 - 1.1875 = -1.21875. Every number is an exact
      -- sixty-fourth; none of them was rounded to get there.
      {
        filename = DC .. "stroke.png",
        priority = "high",
        width = 48, height = 54,
        frame_count = DC_FRAMES,
        line_length = 6,
        animation_speed = 0.2,
        shift = { 0.046875, -1.21875 },
        scale = 0.5
      },
      {
        filename = DC .. "base-shadow.png",
        priority = "high",
        draw_as_shadow = true,
        -- Leans up and to the right, so it is wider than the colour plate and
        -- carries its own shift. Both numbers come out of the tool.
        --
        -- Still one frame. The crown's own shadow travels with it in life, but
        -- the crown is 4.6% of the machine's drawn pixels and its shadow is a
        -- smaller share of a plate that is nearly twice as wide -- cutting the
        -- shadow apart to move that is a second mask for something no player
        -- looks at. Recorded as a choice rather than an oversight.
        width = 358, height = 217,
        frame_count = 1,
        repeat_count = DC_FRAMES,
        animation_speed = 0.2,
        shift = { 1.23438, 0.05469 },
        scale = 0.5
      }
    }
  },
  working_visualisations =
  {
    -- The fault lamp. Drawn WHITE on the plate and cut white, because
    -- `apply_tint = "status"` hands the colour to the engine and a colour baked
    -- into the plate would be that colour in every state for ever.
    -- `always_draw` is true because a lamp that only appears while working
    -- cannot report that the machine has stopped, which is the one thing it
    -- exists to say. Same canvas as the plate, so it registers by construction.
    {
      always_draw = true,
      apply_tint = "status",
      animation =
      {
        filename = DC .. "status-lamp.png",
        priority = "high",
        draw_as_glow = true,
        width = 200, height = 206,
        frame_count = 1,
        shift = { 0, -0.03125 },
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
derive.placeholder_art(furnace, "wears electric-furnace's sprites until its plate exists")
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
furnace.fluid_boxes =
{
  {
    production_type = "input",
    volume = 2000,                         -- see the S12 note above
    -- The plate draws its own frost-collared flange, so `pipe_picture` is emptied
    -- and no generic stub is laid over that art. The covers stay: they cap the
    -- port only while nothing is plumbed to it. This is the foundry's own
    -- arrangement -- see derive.pipe_covers.
    pipe_picture = util.empty_sprite(),
    pipe_covers = derive.pipe_covers(),
    always_draw_covers = false,
    -- EAST, not south, and the art is why. The adopted plate draws the
    -- frost-collared flux flange low on the right flank, and section 8 of the
    -- spec never said which flank it was -- so the round pinned it east and the
    -- prototype follows the picture rather than the other way round. A flange
    -- drawn on one face and declared on another is the arc mast's
    -- `lightning_strike_offset` defect in a different costume.
    pipe_connections = { { flow_direction = "input", direction = defines.direction.east, position = { 1, 0 } } }
  }
}
furnace.fluid_boxes_off_when_no_fluid_recipe = true

-- Art: the Pot, option A of five (concept/vacuum-furnace/options/).
--
-- A sealed welded drum with one clamped hatch, and the whole design is the
-- absence of an opening: no door, no throat, no chimney. The one thing that
-- glows is a sight port low on the near face, and it glows ONLY while the
-- furnace is running -- `always_draw = false` -- because a lit port on an idle
-- machine says it is working when it is not.
--
-- 192 px of drawn machine, **3.000 tiles** on a 3-tile footprint, centred to
-- 0.0 px, alpha zero on all four canvas edges. Vanilla's own electric furnace
-- draws 3.25 tiles on the same footprint, so ours is the more conservative cut.
local VF = "__space-age-extended__/graphics/entity/vacuum-furnace/"
furnace.icon = "__space-age-extended__/graphics/icons/vacuum-furnace.png"
derive.own_graphics(furnace,
{
  animation =
  {
    layers =
    {
      {
        filename = VF .. "base.png",
        priority = "high",
        width = 200, height = 194,
        shift = { 0, 0 },
        scale = 0.5
      },
      {
        filename = VF .. "base-shadow.png",
        priority = "high",
        draw_as_shadow = true,
        width = 349, height = 205,
        shift = { 1.16406, 0.08594 },
        scale = 0.5
      }
    }
  },
  working_visualisations =
  {
    -- The sight port, differenced out of a lit and an unlit render of the same
    -- plate so it registers by construction. 0.5% of the canvas: this machine's
    -- entire heat budget is one circle, and if light appears anywhere else the
    -- seal it is built around is a lie.
    {
      always_draw = false,
      light = { intensity = 0.3, size = 2.5, color = { 0.91, 0.64, 0.29 } },
      animation =
      {
        filename = VF .. "port-glow.png",
        priority = "high",
        blend_mode = "additive",
        draw_as_glow = true,
        width = 200, height = 194,
        frame_count = 1,
        shift = { 0, 0 },
        scale = 0.5
      }
    },
    -- The fault lamp, and the first one in this mod.
    --
    -- `apply_tint = "status"` hands the colour to the engine, which is why the
    -- lens is drawn WHITE on the plate and cut white here: a colour baked into
    -- the plate would be that colour in every state for ever. `always_draw` is
    -- true because a lamp that only appears while working cannot report that the
    -- machine has stopped -- which is the one thing it exists to say.
    --
    -- Copied from vanilla's electric mining drill, which does exactly this.
    {
      always_draw = true,
      apply_tint = "status",
      animation =
      {
        filename = VF .. "status-lamp.png",
        priority = "high",
        draw_as_glow = true,
        width = 200, height = 194,
        frame_count = 1,
        shift = { 0, 0 },
        scale = 0.5
      }
    }
  }
})
data:extend({ furnace })

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
-- neither exists on this branch; on master it was a real gate that once made
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
}) do
  data:extend(machine_item(spec[1], spec[2], spec[3], spec[4]))
end
