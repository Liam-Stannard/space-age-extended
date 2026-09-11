-- The nine machines of the Core's own production line.
--
-- Each has a master spec under graphics/, and every number below is read off it
-- rather than invented here; where this file and a spec disagree, the spec is
-- right and this is a bug. Section 2 of each spec is the source.
--
-- **The art is a stand-in and says so.** None of the nine has a plate yet. Each
-- borrows the sprites of a vanilla machine of the same footprint, marked by a
-- `derive.placeholder_art` call so `grep` finds every one of them, and logged at
-- data stage so the log does too. That is a different thing from an inherited
-- leftover -- see prototypes/derive.lua, which strips those up front.
--
-- Three of the nine are shaped by measurements that cost a spike each, and the
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
--   * The Ring Mast holds no charge at all. Its product spoils in seconds with
--     no spoil result, which is how a building is made to matter *near* another
--     one -- nothing in the engine can express that directly.

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
  { type = "recipe-category", name = "sae-classification" },
  { type = "recipe-category", name = "sae-separation" },
  { type = "recipe-category", name = "sae-fibre" },
  { type = "recipe-category", name = "sae-degassing" },
  { type = "recipe-category", name = "sae-sintering" },
  { type = "recipe-category", name = "sae-ignition-charge" }
})

--------------------------------------------------------------------------------
-- Surface conditions, named once.
--
-- Two distinct locks, and the difference is the design rather than a detail.
-- `HIGH_G` is the Core's surface alone: the three gravity machines cannot be
-- carried anywhere else, because gravity is the thing doing their work. `CORE`
-- is the Core and space platforms, for machines whose argument is the absence of
-- atmosphere rather than the presence of weight.
--------------------------------------------------------------------------------

local HIGH_G = { { property = "gravity", min = 45 } }
local CORE = { { property = "pressure", max = 9 } }
local CORE_ONLY = { { property = "pressure", min = 1, max = 9 } }

local BOX_3x3 = { { -1.4, -1.4 }, { 1.4, 1.4 } }
local SEL_3x3 = { { -1.5, -1.5 }, { 1.5, 1.5 } }

--- A 3x3 crafting machine, since six of the nine are exactly that.
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
drill.icon = data.raw["mining-drill"]["big-mining-drill"].icon
drill.icons = nil
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
-- N3. Dross Classifier -- concept/dross-classifier/building-spec-dross-classifier.md
--
-- Sorts settling dross by particle size. Shares the Drop Crusher's and the
-- Ballast Drill's argument -- gravity doing mechanical work -- applied to
-- separation rather than to breaking or extraction, so the three read as a
-- family leaning on one planetary fact. Nothing in vanilla sorts a solid by
-- density.
--------------------------------------------------------------------------------

local classifier = crafter("sae-dross-classifier", "assembling-machine-3", {
  categories = { "sae-classification" },
  energy = "150kW",          -- the sort is gravity; the shake is not
  modules = 2,
  conditions = HIGH_G
})

-- Art: the Shaker Deck, option A of five (concept/dross-classifier/options/).
--
-- The plate replaces assembling-machine-3's entirely, so the placeholder call is
-- gone with it and this machine no longer logs at data stage. Two layers, both
-- cut by tools/process-building-art.py from one approved render: 192 px of drawn
-- machine, **3.000 tiles**, centred to 0.0 px, with alpha zero on all four
-- canvas edges. The 4 px rim a side is the difference between a plate with an
-- antialiased edge and one that ends on a razor line.
--
-- There is no working visualisation and no glow. The machine's whole read is
-- that it shakes, and vibration is carried by the springs and the eccentric
-- drive being *drawn*, not by anything animating: dross is what settled out and
-- is cold by the time it arrives, so nothing here is lit.
--
-- Which is why its accent is PAINT: signal yellow on the eccentric-drive guard,
-- the four spring caps and the drive-end rail -- what a moving-part guard is
-- painted, on the machine whose whole read is that it moves. Paint never glows.
local DC = "__space-age-extended__/graphics/entity/dross-classifier/"
classifier.icon = "__space-age-extended__/graphics/icons/dross-classifier.png"
derive.own_graphics(classifier,
{
  animation =
  {
    layers =
    {
      {
        filename = DC .. "base.png",
        priority = "high",
        width = 200, height = 189,
        shift = { 0, 0 },
        scale = 0.5
      },
      {
        filename = DC .. "base-shadow.png",
        priority = "high",
        draw_as_shadow = true,
        -- Leans up and to the right, so it is wider than the colour plate and
        -- carries its own shift. Both numbers come out of the tool rather than
        -- being chosen; the y offset is the room the blur needs below the foot.
        width = 345, height = 200,
        shift = { 1.13281, 0.08594 },
        scale = 0.5
      }
    }
  }
})
data:extend({ classifier })

--------------------------------------------------------------------------------
-- N4. Coil Separator -- concept/coil-separator/building-spec-coil-separator.md
--
-- Magnetic beneficiation on a world with no magnetic field, which is why it is
-- so expensive to run: the field has to be generated rather than borrowed. Its
-- own build recipe costs a coil assembly, two stages below the Field Coil
-- Segment -- the player spends endgame material to make more endgame material,
-- which is the production tree's "using the thing you are building to build more
-- of it" made literal.
--------------------------------------------------------------------------------

local separator = crafter("sae-coil-separator", "electromagnetic-plant", {
  categories = { "sae-separation" },
  energy = "2500kW",         -- generating a field from nothing is the cost
  modules = 3,
  conditions = CORE
})

-- Art: the Cold Plant, option D of five (concept/coil-separator/options/).
--
-- The design is the argument: nine tenths refrigeration and one tenth magnet,
-- with the coil buried inside the vessel and never drawn. What the player sees
-- of the separation itself is one narrow slot at the base of the vessel, and
-- that slot is the only thing distinguishing this building from a cold plant --
-- which is why stage 1 was allowed exactly two changes and one of them was
-- making it wider and brighter.
--
-- 192 px of drawn machine, **3.000 tiles** on a 3-tile footprint, centred to
-- 0.0 px, alpha zero on all four canvas edges. It stands 3.25 tiles tall, so the
-- plate is shifted a quarter tile up to put its foot on the tile rather than its
-- middle: height above the footprint is what Factorio does everywhere, sideways
-- overhang is what makes a row of machines interleave.
--
-- Replacing the graphics set wholesale also removes what this prototype was
-- deep-copied from, and that matters more here than anywhere else in the file:
-- the electromagnetic plant is this building's *anti-read* -- a clean lab-white
-- box whose whole point in the fiction is that the player had to import it --
-- so wearing its sprites was a placeholder saying the opposite of the design.
local CS = "__space-age-extended__/graphics/entity/coil-separator/"
separator.icon = "__space-age-extended__/graphics/icons/coil-separator.png"
derive.own_graphics(separator,
{
  animation =
  {
    layers =
    {
      {
        filename = CS .. "base.png",
        priority = "high",
        width = 200, height = 216,
        shift = { 0, -0.12500 },
        scale = 0.5
      },
      {
        filename = CS .. "base-shadow.png",
        priority = "high",
        draw_as_shadow = true,
        width = 367, height = 227,
        shift = { 1.30469, -0.03906 },
        scale = 0.5
      }
    }
  },
  -- The field, and only while the field is on.
  --
  -- Differenced out of a lit and an unlit render of the same plate, so it
  -- registers over `base` by construction rather than by alignment -- the method
  -- the sealed roboport's lamps use, and the reason nothing here had to be drawn
  -- by hand. `always_draw` is false: a machine with nothing to separate is a
  -- machine with the field off, and 2.5 MW should look like it costs something
  -- when it runs and nothing when it does not.
  working_visualisations =
  {
    {
      always_draw = false,
      light = { intensity = 0.35, size = 3.5, color = { 0.42, 0.35, 0.78 } },
      animation =
      {
        filename = CS .. "slot-glow.png",
        priority = "high",
        blend_mode = "additive",
        draw_as_glow = true,
        width = 200, height = 216,
        frame_count = 1,
        shift = { 0, -0.12500 },
        scale = 0.5
      }
    }
  }
})

-- The hum, chosen rather than inherited.
--
-- `derive.own_graphics` drops the electromagnetic plant's three sounds, because
-- every one of them is cued to a vanilla animation this machine no longer has --
-- and a 2.5 MW machine standing silent is a regression, not a decision. This is
-- the cryogenic plant's ambient loop, which is ungated and is the right noise
-- for a building that is nine tenths refrigeration. Its own smoke-puff accents
-- are left behind: nothing puffs on a world with no atmosphere.
separator.working_sound =
{
  sound = { filename = "__space-age__/sound/entity/cryogenic-plant/cryogenic-plant.ogg",
            volume = 0.7 },
  fade_in_ticks = 4,
  fade_out_ticks = 30
}
data:extend({ separator })

--------------------------------------------------------------------------------
-- N5. Whisker Comber -- concept/whisker-comber/building-spec-whisker-comber.md
--
-- Splits one harvest into a quality-graded pair, both with real consumers: tow
-- for the composite line, felt for the cryostat. Combing is four times slower per
-- whisker than matting, so neither is the correct answer and the ratio is a
-- standing decision rather than a solved one.
--------------------------------------------------------------------------------

local comber = crafter("sae-whisker-comber", "assembling-machine-3", {
  categories = { "sae-fibre" },
  energy = "400kW",
  modules = 3,
  conditions = CORE
})

-- Art: the Spinner, option C of five (concept/whisker-comber/options/).
--
-- A squat standing drum rather than another low box, which is the entire reason
-- it was picked: this machine sorts things standing next to the Dross
-- Classifier, which also sorts things, and a round body is the one silhouette
-- that separates them at any zoom without a single pixel of detail.
--
-- 192 px of drawn machine, **3.000 tiles** on a 3-tile footprint, centred to
-- 0.0 px, alpha zero on all four canvas edges. It stands 3.39 tiles tall, so the
-- plate is shifted up to stand the drum's foot on the tile.
--
-- Nothing is lit, and this machine's accent is therefore PAINT rather than
-- light: service blue on the lid's dogs, the shoulder band and the skirt's
-- access panel -- the parts a person actually touches on a machine that handles
-- something which would cut you. Paint never glows; see the template's
-- "Every machine gets an accent" note for why a cold machine needs one at all.
--
-- The two recipes -- comb into tow, mat
-- into felt -- are not drawn on this machine at all; that was the cost of the
-- design and it is recorded in the spec's §3.2 rather than hidden. If the choice
-- ever has to be visible it belongs in a working visualisation, which plays only
-- while the machine crafts.
local WC = "__space-age-extended__/graphics/entity/whisker-comber/"
comber.icon = "__space-age-extended__/graphics/icons/whisker-comber.png"
derive.own_graphics(comber,
{
  animation =
  {
    layers =
    {
      {
        filename = WC .. "base.png",
        priority = "high",
        width = 200, height = 224,
        shift = { 0, -0.18750 },
        scale = 0.5
      },
      {
        filename = WC .. "base-shadow.png",
        priority = "high",
        draw_as_shadow = true,
        width = 373, height = 235,
        shift = { 1.35156, -0.10156 },
        scale = 0.5
      }
    }
  }
})
data:extend({ comber })

--------------------------------------------------------------------------------
-- N6. Helium Concentrator -- concept/helium-concentrator/building-spec-helium-concentrator.md
--
-- A relief valve on a hard cap, and priced like one: worse than gravity settling
-- at making melt *and* far worse than a gas vent at making helium. It is the bad
-- trade taken when one of the two is what has run out. Three fluid boxes -- one
-- in, two out -- which is why it is built fresh rather than copied from any
-- vanilla machine.
--------------------------------------------------------------------------------

-- Three ports on three different faces, and each one is drawn on the plate.
--
-- The prototype used to put BOTH outputs on the north face, which its own §8 does
-- not say and the adopted art does not draw: helium-3 leaves north on the riser,
-- and the heavy settled melt leaves WEST, low. A port declared on one face and
-- drawn on another is the same defect as the Vacuum Furnace's flux flange, and it
-- was found the same way -- by reading the plate against the prototype rather
-- than reading the Lua.
--
-- `pipe_picture` is emptied and `always_draw_covers` is false on all three,
-- which is the foundry's pattern: the flange belongs to the building's own art,
-- so the engine must not draw a generic stub over it.
local concentrator = crafter("sae-helium-concentrator", "chemical-plant", {
  categories = { "sae-degassing" },
  energy = "1500kW",
  modules = 3,
  conditions = CORE,
  fluid_boxes =
  {
    {
      production_type = "input",
      volume = 1000,
      pipe_picture = util.empty_sprite(),
      pipe_covers = derive.pipe_covers(),
      always_draw_covers = false,
      pipe_connections = { { flow_direction = "input", direction = defines.direction.south, position = { 0, 1 } } }
    },
    {
      production_type = "output",
      volume = 1000,
      pipe_picture = util.empty_sprite(),
      pipe_covers = derive.pipe_covers(),
      always_draw_covers = false,
      pipe_connections = { { flow_direction = "output", direction = defines.direction.north, position = { 0, -1 } } }
    },
    {
      production_type = "output",
      volume = 1000,
      pipe_picture = util.empty_sprite(),
      pipe_covers = derive.pipe_covers(),
      always_draw_covers = false,
      pipe_connections = { { flow_direction = "output", direction = defines.direction.west, position = { -1, 0 } } }
    }
  }
})

-- Art: the Twin Bottles, option C of five (concept/helium-concentrator/options/).
--
-- Two unequal vessels bridged at the waist, and the temperature split is drawn on
-- the PIPE between them: frost on the cold half, bare warm metal on the hot half,
-- and a clamp in the middle where it changes. The hot vessel's skirt joints carry
-- the only warm light on the machine, and only while it is running.
--
-- 192 px of drawn machine, **3.000 tiles** on a 3-tile footprint, centred to
-- 0.0 px, alpha zero on all four canvas edges.
--
-- The concept measured as the least detailed sheet of its round, so stage 1 was
-- allowed exactly one change beyond the light: more hardware on both shells,
-- without touching their shapes. On the cut plate it now measures denser than
-- vanilla's own chemical plant.
local HC = "__space-age-extended__/graphics/entity/helium-concentrator/"
concentrator.icon = "__space-age-extended__/graphics/icons/helium-concentrator.png"
derive.own_graphics(concentrator,
{
  animation =
  {
    layers =
    {
      {
        filename = HC .. "base.png",
        priority = "high",
        width = 200, height = 201,
        shift = { 0, 0 },
        scale = 0.5
      },
      {
        filename = HC .. "base-shadow.png",
        priority = "high",
        draw_as_shadow = true,
        width = 355, height = 212,
        shift = { 1.21094, 0.08594 },
        scale = 0.5
      }
    }
  },
  working_visualisations =
  {
    {
      always_draw = false,
      light = { intensity = 0.25, size = 2.5, color = { 0.85, 0.45, 0.18 } },
      animation =
      {
        filename = HC .. "skirt-glow.png",
        priority = "high",
        blend_mode = "additive",
        draw_as_glow = true,
        width = 200, height = 201,
        frame_count = 1,
        shift = { 0, 0 },
        scale = 0.5
      }
    }
  }
})
data:extend({ concentrator })

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
furnace.icon = data.raw["furnace"]["electric-furnace"].icon
furnace.icons = nil
furnace.minable = { mining_time = 0.5, result = "sae-vacuum-furnace" }
furnace.collision_box = BOX_3x3
furnace.selection_box = SEL_3x3
furnace.crafting_categories = { "smelting", "sae-sintering" }
furnace.crafting_speed = 1.5
furnace.energy_usage = "1200kW"
furnace.energy_source = { type = "electric", usage_priority = "secondary-input" }
furnace.module_slots = 2
furnace.surface_conditions = CORE
furnace.source_inventory_size = 1          -- the prototype maximum
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
-- N9. Ignition Ring Mast -- concept/ring-mast/building-spec-ignition-ring-mast.md
--
-- The opposite of the Arc Mast in every way that matters: that one catches
-- something episodic and banks it, this spends something continuously and cannot
-- store it at all.
--
-- **Nothing in the engine can require a building to be near another one**, and
-- this is how that is expressed anyway: the charge it makes carries a very short
-- `spoil_ticks` and no `spoil_result`, so it simply ceases to exist. Belt travel
-- is real time, so a mast more than a few seconds of belt from the Array delivers
-- nothing. Pure data, no control-stage script -- see items.lua for the timer.
--
-- No modules and no effects at all. 12 MW is meant to hurt, and a productivity
-- module undoing that would undo the point.
--------------------------------------------------------------------------------

local mast = crafter("sae-ring-mast", "assembling-machine-3", {
  categories = { "sae-ignition-charge" },
  energy = "12MW",
  modules = 0,
  conditions = CORE_ONLY,
  fluid_boxes =
  {
    {
      production_type = "input",
      volume = 400,
      -- Same arrangement as the Vacuum Furnace and the Concentrator, and it is
      -- the foundry's: the plate draws its own flange, `pipe_picture` is emptied
      -- so no generic stub is laid over that art, and the covers stay.
      --
      -- **The two are not alternatives, which took a detour to work out.** The
      -- machine's own art says what the fitting looks like; the cover says what
      -- an *unused* one looks like, and `always_draw_covers = false` means it is
      -- gone the moment a pipe is joined. The foundry carries all three at once.
      -- Four of our buildings had dropped the covers on the grounds that they
      -- draw their own flange, which simply left the second job undone.
      pipe_picture = util.empty_sprite(),
      pipe_covers = derive.pipe_covers(),
      always_draw_covers = false,
      pipe_connections = { { flow_direction = "input", direction = defines.direction.south, position = { 0, 1 } } }
    }
  }
})
mast.fixed_recipe = "sae-ignition-charge"
mast.allowed_effects = {}

-- Art: the Braced Post, option A of five (concept/ring-mast/options/).
--
-- Locked 2026-09-10. Four heavy buttresses splaying to the corners, a thick
-- banded coil at waist height, and a short blunt CLOSED cap above it. The whole
-- round exists to keep this building from reading as a lightning collector, and
-- the closed dark top is the single line that does it -- the Arc Mast next door
-- is the thing lightning hits, and these two must never be confused.
--
-- **The inlet was redrawn.** The adopted sheet drew it frost-jacketed, which was
-- generated before the template's convention 5: a fluid connection carries no
-- frost, heat or tint, because the engine stamps its own neutral cover over an
-- unconnected port and a rimed stub ends up with a bare grey flange sitting in
-- it. The master render draws it as a plain bored fitting instead -- the vanilla
-- pump's own read.
--
-- **The shift is measured, and it is positive here.** 192 px of drawn machine,
-- 3.000 tiles, checked by tools/check-footprint.py. Unlike the Drop Crusher this
-- building is SHORTER than its own footprint -- 2.83 tiles of drawn height on a
-- 3 tile box -- so the bottom-aligned box puts the footprint's centre 5.5 source
-- px ABOVE the canvas centre and the plate is pushed DOWN by 2.75 in-game px.
-- Vanilla agrees: assembling-machine-3, the other squat 3x3, ships
-- `by_pixel(-0.5, 2.5)` -- +0.078 against our +0.086.
--
-- **The band is unlit and that is on purpose.** This plate is what the charge
-- glow will be derived from, so a band drawn part-charged would bake a mid-cycle
-- state into the still machine. Until that layer exists the status lamp carries
-- the whole read, as it does on the Drop Crusher.
local RM = "__space-age-extended__/graphics/entity/ring-mast/"
mast.icon = "__space-age-extended__/graphics/icons/ring-mast.png"
mast.icons = nil
derive.own_graphics(mast,
{
  animation =
  {
    layers =
    {
      {
        filename = RM .. "base.png",
        priority = "high",
        width = 200, height = 191,
        shift = { 0, 0.08594 },
        scale = 0.5
      },
      {
        filename = RM .. "base-shadow.png",
        priority = "high",
        draw_as_shadow = true,
        width = 346, height = 202,
        shift = { 1.14062, 0.17188 },
        scale = 0.5
      }
    }
  },
  working_visualisations =
  {
    -- Cut white from the plate's own canvas, so it registers by construction.
    -- `apply_tint = "status"` hands the colour to the engine; `always_draw`
    -- because a lamp that only appears while working cannot report that the
    -- machine has stopped, which is the one thing it exists to say.
    {
      always_draw = true,
      apply_tint = "status",
      animation =
      {
        filename = RM .. "status-lamp.png",
        priority = "high",
        draw_as_glow = true,
        width = 200, height = 191,
        frame_count = 1,
        shift = { 0, 0.08594 },
        scale = 0.5
      }
    }
  }
})
data:extend({ mast })

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
local function welded(n) return { type = "item", name = "sae-welded-plate", amount = n } end
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
-- **Welded plate is off the four early machines**, and it was a real gate rather
-- than a flavour note: `sae-welded-plate` needs whiskers, so it does not exist
-- until `sae-cold-welding` -- three technologies after the Ballast Drill and the
-- Vacuum Furnace unlock. That made the Vacuum Furnace unbuildable through
-- exactly the stretch it exists to cover, since it is the only machine that will
-- smelt the fines the crusher starts making on its first craft. It stays on the
-- Coil Separator and the Ring Mast, which are endgame machines and have it.
for _, spec in ipairs({
  { "sae-drop-crusher", "a", { steel(40), gear(30), circuit(10) }, 6 },
  -- Freight-priced for the same reason the crusher is: it is now the only way to
  -- get a kamacite ore out of the ground, so it sits on the critical path to the
  -- first plate and cannot be costed in plate. That is the rule for the whole
  -- landing kit -- on the path to the first plate, it comes out of the corridor.
  { "sae-ballast-drill", "b", { steel(60), gear(40), circuit(15) }, 10 },
  { "sae-dross-classifier", "c", { plate(30), gear(20), circuit(10) }, 5 },
  { "sae-coil-separator", "d",
    { plate(40), welded(10), { type = "item", name = "sae-coil-assembly", amount = 1 },
      { type = "item", name = "processing-unit", amount = 20 } }, 12 },
  { "sae-whisker-comber", "e", { plate(30), gear(30), circuit(10) }, 6 },
  { "sae-helium-concentrator", "f",
    { plate(40), { type = "item", name = "pipe", amount = 20 }, circuit(15) }, 8 },
  { "sae-vacuum-furnace", "g",
    { plate(50), { type = "item", name = "processing-unit", amount = 10 } }, 10 },
  { "sae-ring-mast", "i",
    { plate(60), welded(20), { type = "item", name = "sae-superconducting-winding", amount = 4 },
      { type = "item", name = "processing-unit", amount = 20 } }, 15 },
}) do
  data:extend(machine_item(spec[1], spec[2], spec[3], spec[4]))
end
