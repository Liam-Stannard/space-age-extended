-- The endgame: what the Core is for.
--
-- The Ignition Array is a rocket silo in everything but purpose. It behaves the
-- way the player already understands one -- parts accumulate, a bar fills, it
-- fires once -- because that familiarity is worth more here than novelty. What
-- it fires is a current through the crust, and what that restarts is the field
-- the planet lost.
--
-- Its part is the Field Coil Segment, and the segment is built from the Core's
-- own end products, three stages below the capstones. See design/04-the-core.md.

local derive = require("prototypes.derive")
local item_sounds = require("__base__.prototypes.item_sounds")

data:extend({
  {
    -- Its own category, so nothing else can be persuaded to make segments.
    type = "recipe-category",
    name = "sae-ignition"
  }
})

--------------------------------------------------------------------------------
-- TEMPORARY: stand-ins for the five capstone products.
--
-- Each of these is the end of a cross-planet tree that does not exist yet. They
-- are craftable from nothing so that the whole endgame is playable long before
-- the trees are built -- which is the earliest point at which anyone can find
-- out whether the Core is any good. Replacing a stub with a real chain later is
-- a recipe change and a migration, not a redesign.
--------------------------------------------------------------------------------

-- Fulgora <-> Aquilo is built, so its capstone is no longer among these.
local stub_items =
{
  { name = "sae-magnetar-alloy",          icon = "__space-age__/graphics/icons/tungsten-plate.png",   order = "b" },
  { name = "sae-cultured-alloy",          icon = "__space-age__/graphics/icons/bioflux.png",          order = "c" },
  { name = "sae-bio-polymer",             icon = "__base__/graphics/icons/plastic-bar.png",           order = "d" }
}

for _, s in pairs(stub_items) do
  data:extend({
    {
      type = "item",
      name = s.name,
      icon = s.icon,
      subgroup = "raw-material",
      order = "zz[sae-stub]-" .. s.order,
      inventory_move_sound = item_sounds.metal_small_inventory_move,
      pick_sound = item_sounds.metal_small_inventory_pickup,
      drop_sound = item_sounds.metal_small_inventory_move,
      stack_size = 50,
      weight = 2 * kg
    },
    {
      type = "recipe",
      name = s.name .. "-stub",
      categories = { "crafting" },
      energy_required = 1,
      ingredients = { { type = "item", name = "iron-plate", amount = 1 } },
      results = { { type = "item", name = s.name, amount = 1 } },
      icon = s.icon,
      icon_size = 64,
      enabled = true
    }
  })
end

data:extend({
  {
    type = "fluid",
    name = "sae-cryoprotectant",
    icon = "__space-age__/graphics/icons/fluid/fluoroketone-cold.png",
    subgroup = "fluid",
    order = "zz[sae-stub]-e",
    default_temperature = -50,
    base_color = { r = 0.45, g = 0.70, b = 0.85 },
    flow_color = { r = 0.70, g = 0.88, b = 1.0 }
  },
  {
    type = "recipe",
    name = "sae-cryoprotectant-stub",
    categories = { "chemistry" },
    energy_required = 1,
    ingredients = { { type = "item", name = "iron-plate", amount = 1 } },
    results = { { type = "fluid", name = "sae-cryoprotectant", amount = 50 } },
    icon = "__space-age__/graphics/icons/fluid/fluoroketone-cold.png",
    icon_size = 64,
    enabled = true
  }
})

--------------------------------------------------------------------------------
-- The end products, and the segment built from them.
--
-- The items are permanent; their recipes here are temporary, and Phase 5
-- replaces them with the two-stage chain that runs through the intermediates.
--------------------------------------------------------------------------------

data:extend({
  {
    type = "item",
    name = "sae-superconducting-winding",
    icon = "__space-age-extended__/graphics/icons/superconducting-winding.png",
    subgroup = "raw-material",
    order = "z[sae]-fa[d-winding]",
    inventory_move_sound = item_sounds.wire_inventory_move,
    pick_sound = item_sounds.wire_inventory_pickup,
    drop_sound = item_sounds.wire_inventory_move,
    stack_size = 50,
    weight = 2 * kg
  },
  {
    type = "item",
    name = "sae-coil-assembly",
    icon = "__space-age-extended__/graphics/icons/coil-assembly.png",
    subgroup = "intermediate-product",
    order = "z[sae]-a[coil-assembly]",
    inventory_move_sound = item_sounds.mechanical_large_inventory_move,
    pick_sound = item_sounds.mechanical_large_inventory_pickup,
    drop_sound = item_sounds.mechanical_large_inventory_move,
    stack_size = 20,
    weight = 10 * kg
  },
  {
    type = "item",
    name = "sae-coolant-loop",
    icon = "__space-age-extended__/graphics/icons/coolant-loop.png",
    subgroup = "intermediate-product",
    order = "z[sae]-b[coolant-loop]",
    inventory_move_sound = item_sounds.metal_barrel_inventory_move,
    pick_sound = item_sounds.metal_barrel_inventory_pickup,
    drop_sound = item_sounds.metal_barrel_inventory_move,
    stack_size = 20,
    weight = 10 * kg
  },
  {
    type = "item",
    name = "sae-field-coil-segment",
    icon = "__space-age-extended__/graphics/icons/field-coil-segment.png",
    subgroup = "intermediate-product",
    order = "z[sae]-c[field-coil-segment]",
    inventory_move_sound = item_sounds.mechanical_large_inventory_move,
    pick_sound = item_sounds.mechanical_large_inventory_pickup,
    drop_sound = item_sounds.mechanical_large_inventory_move,
    stack_size = 10,
    weight = 20 * kg
  },

  {
    type = "recipe",
    name = "sae-coil-assembly",
    categories = { "crafting" },
    energy_required = 60,
    ingredients =
    {
      { type = "item", name = "sae-field-conductor", amount = 2 },
      { type = "item", name = "sae-magnetic-core-billet", amount = 2 },
      { type = "item", name = "sae-reinforced-frame", amount = 1 },
      { type = "item", name = "sae-insulation-sleeve", amount = 2 },
      { type = "item", name = "sae-welded-plate", amount = 2 }
    },
    results = { { type = "item", name = "sae-coil-assembly", amount = 1 } },
    surface_conditions = { { property = "pressure", max = 9 } },
    enabled = false
  },
  {
    type = "recipe",
    name = "sae-coolant-loop",
    categories = { "crafting" },
    energy_required = 20,
    ingredients =
    {
      { type = "item", name = "sae-coolant-charge", amount = 2 },
      { type = "item", name = "sae-kamacite-plate", amount = 10 }
    },
    results = { { type = "item", name = "sae-coolant-loop", amount = 1 } },
    surface_conditions = { { property = "pressure", min = 1, max = 9 } },
    enabled = false
  },
  {
    type = "recipe",
    name = "sae-field-coil-segment",
    categories = { "sae-ignition" },
    energy_required = 8,
    ingredients =
    {
      { type = "item", name = "sae-coil-assembly", amount = 1 },
      { type = "item", name = "sae-coolant-loop", amount = 1 },
      -- The Ring Mast's charge, and the reason that building exists. It spoils
      -- ten seconds after it is made, with no spoil result, so a mast has to
      -- stand within a few seconds of belt of this machine or it delivers
      -- nothing at all. That timer is how one building is made to matter *near*
      -- another, which the engine cannot express directly. See machines.lua.
      { type = "item", name = "sae-ignition-charge", amount = 1 }
    },
    results = { { type = "item", name = "sae-field-coil-segment", amount = 1 } },
    enabled = false,
    hide_from_player_crafting = true
  }
})

--------------------------------------------------------------------------------
-- The Ignition Array.
--------------------------------------------------------------------------------

local array = derive.from("rocket-silo", "rocket-silo", "sae-ignition-array")
local IA = "__space-age-extended__/graphics/entity/ignition-array/"
array.icon = "__space-age-extended__/graphics/icons/ignition-array.png"
array.minable = { mining_time = 5, result = "sae-ignition-array" }
array.crafting_categories = { "sae-ignition" }
array.fixed_recipe = "sae-field-coil-segment"
array.rocket_parts_required = 100
array.energy_usage = "2MW"
-- An order of magnitude past vanilla's 3.99MW, so every megawatt the array
-- draws is melt that was not cast into the segments it also needs.
array.active_energy_usage = "50MW"
array.surface_conditions = { { property = "pressure", min = 1, max = 9 } }
-- It fires on command rather than at a platform's request: this is an ignition,
-- not a delivery.
array.launch_to_space_platforms = false

-- Three things inherited from the silo that describe a machine this is not.
--
-- Emptied rather than left, for the same reason section 6.1 empties the blast
-- doors: on a world whose whole premise is that nothing leaves and nothing
-- burns, vanilla's furniture is not neutral, it is a lie that happens to be
-- drawn well.
--
--   * `graphics_set.working_visualisations` -- six vanilla animations played
--     while the Array crafts: `crafting` and `crafting-light` at 64 frames,
--     `engine` and `filter` at 32, and `steam-1` and `steam-2` at 64. An engine
--     and two steam plumes, at pressure 5, on a planet with no atmosphere to
--     carry either. Section 1 of design/04-the-core.md is explicit that nothing
--     burns here, and the radiant generator's spec calls a steam engine "the
--     single most wrong object that could stand on a vacuum world". The Array
--     has no working animation of its own yet, so it now has none at all, which
--     is quiet rather than wrong.
--   * `robot_door` -- vanilla's silo has a little roboport hatch, animated, with
--     passive-provider-chest sounds. Our deck has no such door drawn on it.
--   * `rocket_entity` -- pointed at `rocket-silo-rocket`, so firing the Array
--     would have sent a Factorio rocket up off the Core. control.lua already
--     says what this machine does: "it delivers nothing -- it fires a current
--     into the crust". It gets its own rocket below, with every sprite, flame
--     and smoke plume emptied, so the launch is the game ending rather than a
--     vehicle leaving.
--   * `working_sound.sound_accents` -- four welder and metal-rotation accents
--     fired on named frames of that same `crafting` visualisation. They are the
--     sound of a rocket being welded together, and with the visualisation gone
--     they are also a hard load error ("Working visualisation \"crafting\"
--     doesn't exist"), because an accent names the visualisation it plays for.
--     The ambient silo loop stays; the assembly accents go.
-- No working visualisation.
--
-- Vanilla's six went for the reasons above. The one that replaced them was drawn
-- for the v3 ring and is registered to that plate's shift, so it cannot survive
-- the change of design -- and it should not, because it answered the wrong
-- question. A `working_visualisation` plays while the machine crafts; it cannot
-- hold cumulative state, and neither can any other prototype field.
-- `LuaEntity` has no `disabled_working_visualisations` in 2.1.17 either, so
-- named visualisations cannot be switched per entity from script. All three were
-- probed on a live server.
--
-- The Array assembles a hundred field coil segments before it can fire, and that
-- is what the player needs to see. `control.lua` draws it with `LuaRendering`
-- off `(rocket_parts + crafting_progress) / rocket_parts_required` -- a smooth
-- nought to one across the whole build rather than a hundred steps.
array.graphics_set = { working_visualisations = {} }
array.robot_door = util.empty_sprite()
if array.working_sound then array.working_sound.sound_accents = nil end

-- The thing that "launches", drawn as nothing.
--
-- `rocket_entity` is mandatory on a rocket-silo, so the Array cannot simply not
-- have one. This is vanilla's rocket with its sprite, flame, glare, shadow and
-- five smoke plumes all emptied, and its explosion removed: nothing rises, and
-- what the player sees is the Array firing and the game ending.
local ignition = derive.from("rocket-silo-rocket", "rocket-silo-rocket", "sae-ignition-discharge")
for _, k in ipairs({
  "rocket_shadow_sprite",
  "rocket_flame_left_animation", "rocket_flame_right_animation",
  "rocket_smoke_bottom1_animation", "rocket_smoke_bottom2_animation",
  "rocket_smoke_top1_animation", "rocket_smoke_top2_animation", "rocket_smoke_top3_animation",
}) do
  if ignition[k] ~= nil then ignition[k] = util.empty_sprite() end
end

-- Three slots are not emptied but replaced, and they are what the player sees
-- at ignition. See tools/build-array-column.py. The layout follows vanilla's
-- rocket, inverted: vanilla's art hangs below its origin because the origin is
-- the nose of a thing that is leaving. Here the origin is the *foot*, standing
-- in the shaft, and the column rises out of it -- so the glare and the flicker
-- sit on the origin too, at the mouth, and the plate reaches north from there.
--
-- Light casts no shadow, so `rocket_shadow_sprite` stays empty above.
-- Where it starts, and when it is allowed to be seen. Both were measured on the
-- rig rather than reasoned about, and both were wrong on the first try.
--
-- `rocket_initial_offset` is inherited as { 0, 3.5 }: vanilla's rocket begins
-- three and a half tiles *south* of the silo origin, low on the pad. For a
-- column of light whose whole job is to stand in the shaft that put the
-- discharge eleven tiles south of the deck, a bright smear on the ground beside
-- the machine. It starts in the shaft.
--
-- `rocket_visible_distance_from_center` is how far the rocket must travel before
-- the engine draws it, and it is what hides a rocket that is still inside its
-- building. Setting it to zero -- on the reasoning that a column standing in the
-- shaft should be visible -- was a mistake with teeth: the Array reaches
-- `waiting_to_launch_rocket` and *stays there*, so the parked discharge stood
-- lit in the open shaft indefinitely and the machine read as permanently firing.
-- Held at 1.0, the column appears as it leaves and not before, which is also
-- what section 9 describes.
ignition.rocket_initial_offset = { 0, 0 }
ignition.rocket_visible_distance_from_center = 1.0

ignition.rocket_sprite =
{
  filename = IA .. "column.png",
  priority = "medium",
  blend_mode = "additive",
  draw_as_glow = true,
  width = 208, height = 512,
  -- The plate is drawn foot-down, and the foot is what stands in the shaft, so
  -- the shift puts the image's bottom edge on the origin and the column rises
  -- north from there: half of 512 px at scale 0.5 is 4 tiles.
  shift = { 0, -4.0 },
  scale = 0.5
}
ignition.rocket_glare_overlay_sprite =
{
  filename = IA .. "column-glare.png",
  priority = "medium",
  blend_mode = "additive",
  draw_as_glow = true,
  width = 384, height = 384,
  shift = { 0, 0 },
  scale = 0.5
}
ignition.rocket_flame_animation =
{
  filename = IA .. "column-flame.png",
  priority = "medium",
  blend_mode = "additive",
  draw_as_glow = true,
  width = 232, height = 232,
  frame_count = 8,
  line_length = 8,
  animation_speed = 0.8,
  shift = { 0, 0 },
  scale = 0.5
}
ignition.dying_explosion = nil
ignition.shadow_slave_entity = nil
ignition.glow_light = nil
-- Three takeoff roars, inherited. The Core has no atmosphere to carry them and
-- nothing leaves the pad, so the launch is silent.
ignition.flying_sound = nil
data:extend({ ignition })
array.rocket_entity = "sae-ignition-discharge"

-- Art. See concept/ignition-array/building-spec-ignition-array.md sections 6.1 and 13.
--
-- Section 6.1 is the scoping decision and it still holds: vanilla's silo uses
-- sixteen art slots, several of them 64-frame sheets running to millions of
-- pixels, and replacing all of it is not a realistic target. What is replaced
-- here is what carries the read -- the machine itself, its shadow and its
-- charge -- and everything that is launch-pad furniture is emptied rather than
-- left inherited. On a world whose entire premise is that nothing leaves,
-- vanilla's blast doors sliding open, its engine bell, its steam vents and its
-- extractor fans would each be a lie, and they would draw straight over ours.
--
-- The three plates are cut by tools/build-ignition-array.py from the adopted
-- Suspended Core render, and they are one canvas: the machine is drawn 576 px
-- wide -- **9.000 tiles**, the footprint exactly -- centred to 0.0 px, on a
-- canvas four pixels larger a side so alpha is zero on all four edges. That rim
-- is the template's Appendix C check 2, which a plate cropped to its own content
-- cannot pass: with no margin the art ends on a razor line mid-geometry, which
-- is the defect the arc mast still carries.
--
-- The deck-and-shaft geometry that earlier versions of this file described --
-- vanilla's five silo slots, tied together by one affine transform -- went with
-- the v3 ring it was measured for, and so did the seven tools that cut it. The
-- Suspended Core has no deck and no hole, so there is nothing to register
-- against vanilla's, and the slots that carried it are emptied below.
array.base_day_sprite =
{
  filename = IA .. "base.png",
  priority = "medium",
  width = 584, height = 533,
  -- 576 x 525 of drawn machine on a canvas four pixels larger a side: 9.00 x
  -- 8.20 tiles, the footprint exactly, overhanging on neither axis. The rim is
  -- there so alpha is zero on all four edges -- Appendix C's check 2, which a
  -- plate cropped to its own content cannot pass.
  --
  -- It is 0.80 tiles *short* of the box vertically, so it is centred and
  -- the shortfall is split 0.40 a side. Parking the bottom edge past the south
  -- edge the way vanilla's silo does put all of that slack at the north instead
  -- -- 1.19 tiles of empty box above the machine, and 0.39 poking out below.
  shift = { 0.0, 0.0 },
  scale = 0.5
}
-- Derived from the deck's own alpha, sheared north-east and blurred, so it is
-- the shadow of the building that is actually drawn rather than a leftover from
-- the plate this replaced. The Core's sky never moves, so it is fixed.
array.shadow_sprite =
{
  filename = IA .. "base-shadow.png",
  priority = "medium",
  draw_as_shadow = true,
  width = 655, height = 557,
  shift = { 0.36719, 0.0 },
  scale = 0.5
}
array.base_front_sprite = util.empty_sprite()
array.base_night_sprite = nil

-- No doors, and no shaft.
--
-- Both door sprites are optional -- proved on a live 2.1.17 server, not assumed:
-- a rocket-silo with `door_back_sprite` and `door_front_sprite` set to nil loads
-- cleanly, and one ran the whole launch sequence in lockstep with a vanilla silo
-- standing beside it, identical states on identical ticks, both rockets away.
-- The door phases still elapse; nothing stalls waiting for art that is not there.
--
-- So the Suspended Core has none. Its sphere is held in the frame's arms and the
-- ground is already visible under it, so there is no deck to open and no shaft
-- to reveal -- the two slots that shaped every previous version of this building
-- simply do not apply to the design that was chosen.
array.door_back_sprite = nil
array.door_front_sprite = nil
array.hole_sprite = util.empty_sprite()
array.hole_light_sprite = util.empty_sprite()

-- The shadow a rocket casts on the pad while it sits there. Nothing sits on this
-- pad, and there is no rocket to cast it.
array.rocket_shadow_overlay_sprite = util.empty_sprite()
-- The deck lit by what is coming out of it. This slot is drawn additively over
-- the whole building as the discharge leaves, and on a planet held at permanent
-- midnight it is most of what the player sees of the ignition.
array.rocket_glow_overlay_sprite =
{
  filename = IA .. "charge-glow.png",
  priority = "medium",
  blend_mode = "additive",
  draw_as_glow = true,
  width = 584, height = 533,
  shift = { 0.0, 0.0 },
  scale = 0.5
}
-- The charge plate, as a sprite prototype so `control.lua` can draw it.
--
-- It is the same 584 x 533 plate the discharge uses, at the same shift, so the
-- glow the player watches climb during the build is pixel-for-pixel the glow
-- that floods the machine when it fires. `LuaRendering` needs a named sprite;
-- it cannot be handed a filename.
data:extend({
  {
    type = "sprite",
    name = "sae-ignition-charge-glow",
    filename = IA .. "charge-glow.png",
    priority = "medium",
    blend_mode = "additive",
    draw_as_glow = true,
    width = 584, height = 533,
    scale = 0.5,
    flags = { "light" }
  }
})

array.red_lights_back_sprites = util.empty_sprite()
array.red_lights_front_sprites = util.empty_sprite()
array.satellite_animation = nil
array.arm_01_back_animation = nil
array.arm_02_right_animation = nil
array.arm_03_front_animation = nil
-- The frozen set. Aquilo draws a second, iced copy of a building when it is
-- cold, and the silo ships one: an iced hole, iced doors, an iced base and an
-- iced front. Every sprite those ice over is emptied above, so what is left is
-- a frozen picture of a rocket silo laid over an Array that has none of it. The
-- Array is pressure-locked to the Core and can never freeze, so these can never
-- correctly draw either.
array.base_frozen = util.empty_sprite()
array.base_front_frozen = util.empty_sprite()
array.door_back_frozen = util.empty_sprite()
array.door_front_frozen = util.empty_sprite()
array.hole_frozen = util.empty_sprite()

-- The launch sequence, heard but not seen. Vanilla's silo opens doors, releases
-- clamps and raises a rocket, and has a sound for each. The Array does none of
-- those things -- its doors, clamps and rocket are all emptied above -- so the
-- sounds play over nothing moving. The alarms go with them: they warn the
-- player to stand clear of a launch, and nothing here leaves the pad.
array.doors_sound = nil
array.clamps_on_sound = nil
array.clamps_off_sound = nil
array.raise_rocket_sound = nil
array.alarm_sound = nil
array.quick_alarm_sound = nil

array.heating_energy = nil
data:extend({ array })

--------------------------------------------------------------------------------
-- The sealed roboport.
--
-- Restricted to pressure 1-9, so it works on the Core and nowhere else in the
-- game: not on a platform (0), not on any vanilla world (Aquilo is lowest at
-- 300). It competes with nothing, which is why a second roboport is not a
-- second tier.
--------------------------------------------------------------------------------

local port = derive.from("roboport", "roboport", "sae-sealed-roboport")
port.icon = "__space-age-extended__/graphics/icons/sealed-roboport.png"
port.minable = { mining_time = 0.5, result = "sae-sealed-roboport" }
port.surface_conditions = { { property = "pressure", min = 1, max = 9 } }
port.energy_usage = "150kW"

-- Where robots come out, measured off the plate rather than inherited.
--
-- Vanilla's 0.3 and 0.87 were chosen for vanilla's roboport, whose mouth is a
-- wide opening low on a squat body. Ours is a dome with an iris near its crown,
-- so inherited values put robots a third of a tile off the ground -- inside the
-- deck, below the hole they are supposed to be using.
--
-- The plate is 306 px at scale 0.5 with shift -0.09375, so its top edge sits
-- 2.48 tiles above the origin. The iris centre is 111 px down from there, and
-- the dome crown 55 px, which puts them 0.75 and 1.62 tiles up. (0.94 was the
-- old, smaller iris; widening it moved its centre down the dome.)
port.spawn_and_station_height = 0.75
-- Robots pass behind the dome and then in front of it, so the swap belongs just
-- above the crown rather than at vanilla's 0.87, which is halfway up our dome.
port.stationing_render_layer_swap_height = 1.62

-- Art. See concept/sealed-roboport/building-spec-sealed-roboport.md sections 6, 7 and 13.
--
-- Measured off the cut plate: the deck's visible content is exactly 256 px --
-- 4.00 tiles -- so a block of ports tiles without overlapping, and the shift is
-- by_pixel(0, -3) so the deck's near edge lands on the footprint's near edge at
-- +2 tiles rather than being guessed.
--
-- Three of vanilla's six slots are deliberately emptied rather than replaced,
-- and that is a scoping decision, not an oversight:
--
--   * `base_patch` -- vanilla lays a ground patch under its roboport. Ours is a
--     square armoured deck that already covers the footprint, so a patch under
--     it would only peek out at the edges.
--   * `door_animation_up` / `door_animation_down` -- vanilla slides two roof
--     doors apart. Section 6 wants these as the two halves of the central iris,
--     which is real art nobody has drawn yet. Left inherited they would slide
--     vanilla's roof doors across our dome, so they are emptied: the iris is
--     drawn closed in `base` and simply stays closed.
--
--     The iris was drawn far too small to begin with, and it showed: robots
--     appeared to squeeze out of a porthole. Measured the same way on both, the
--     old aperture was 66% of the width vanilla gives a robot to fly through.
--     The plate was edited -- not regenerated -- to open it to 80 x 69 px,
--     1.25 x 1.08 tiles, which is 114% of vanilla's 70 x 64. The spawn heights
--     below are measured off that edited plate.
--   * `recharging_animation` -- vanilla draws its own contact arc at each
--     charging offset. The docks are drawn in our plate at those offsets, but
--     vanilla's arc is shaped for an open pad, so it is emptied too. The light
--     stays, retinted to the amber of section 3.3, so an occupied dock still
--     reads at night.
--
-- Two more inherited pictures are of vanilla's roboport rather than ours, and
-- both are dropped rather than emptied because neither is required:
--
--   * `frozen_patch` -- the iced version of the ground patch. The patch itself
--     is gone, and this port is pressure-locked to the Core, which never
--     freezes.
--   * `water_reflection` -- vanilla's squat silhouette mirrored in water. Wrong
--     shape for a dome, and there is no water on the Core to hold it.

-- And the sound of doors that no longer move. `open_door_trigger_effect` and
-- `close_door_trigger_effect` fire the roboport's door clunk on the animations
-- emptied just above, so the port would clunk open and shut with the iris drawn
-- shut throughout.
port.open_door_trigger_effect = nil
port.close_door_trigger_effect = nil

local RBP = "__space-age-extended__/graphics/entity/sealed-roboport/"
port.base =
{
  layers =
  {
    {
      filename = RBP .. "base.png",
      priority = "high",
      width = 288, height = 306,
      shift = { 0, -0.09375 },        -- by_pixel(0, -3) at scale 0.5
      scale = 0.5
    },
    {
      filename = RBP .. "base-shadow.png",
      priority = "high",
      draw_as_shadow = true,
      width = 519, height = 306,
      shift = { 1.80469, -0.09375 },
      scale = 0.5
    }
  }
}
port.base_patch = util.empty_sprite()
-- The amber status ring and the lit hatch frame, recovered by differencing a lit
-- render against the unlit plate -- so it registers over `base` by construction
-- rather than by alignment. One frame: the ring idles rather than animating.
port.base_animation =
{
  filename = RBP .. "lamps.png",
  priority = "high",
  blend_mode = "additive",
  draw_as_glow = true,
  width = 288, height = 306,
  frame_count = 1,
  shift = { 0, -0.09375 },
  scale = 0.5
}
port.door_animation_up = util.empty_sprite()
port.door_animation_down = util.empty_sprite()
port.recharging_animation = util.empty_sprite()
port.recharging_light = { intensity = 0.2, size = 3, color = { 0.91, 0.64, 0.23 } }

data:extend({ port })

data:extend({
  {
    type = "item",
    name = "sae-ignition-array",
    icon = "__space-age-extended__/graphics/icons/ignition-array.png",
    subgroup = "production-machine",
    order = "z[sae]-z[ignition-array]",
    place_result = "sae-ignition-array",
    inventory_move_sound = item_sounds.mechanical_large_inventory_move,
    pick_sound = item_sounds.mechanical_large_inventory_pickup,
    drop_sound = item_sounds.mechanical_large_inventory_move,
    stack_size = 1,
    weight = 500 * kg
  },
  {
    type = "item",
    name = "sae-sealed-roboport",
    icon = "__space-age-extended__/graphics/icons/sealed-roboport.png",
    subgroup = "logistic-network",
    order = "z[sae]-a[sealed-roboport]",
    place_result = "sae-sealed-roboport",
    inventory_move_sound = item_sounds.roboport_inventory_move,
    pick_sound = item_sounds.roboport_inventory_pickup,
    drop_sound = item_sounds.roboport_inventory_move,
    stack_size = 10,
    weight = 40 * kg
  },

  {
    type = "recipe",
    name = "sae-sealed-roboport",
    categories = { "crafting" },
    energy_required = 15,
    ingredients =
    {
      { type = "item", name = "sae-welded-plate", amount = 20 },
      { type = "item", name = "sae-kamacite-plate", amount = 30 },
      { type = "item", name = "processing-unit", amount = 20 },
      { type = "item", name = "sae-coolant-loop", amount = 2 }
    },
    results = { { type = "item", name = "sae-sealed-roboport", amount = 1 } },
    enabled = false
  },
  {
    type = "recipe",
    name = "sae-ignition-array",
    categories = { "crafting" },
    energy_required = 120,
    ingredients =
    {
      { type = "item", name = "sae-welded-plate", amount = 200 },
      { type = "item", name = "sae-kamacite-plate", amount = 500 },
      { type = "item", name = "sae-coil-assembly", amount = 10 },
      { type = "item", name = "processing-unit", amount = 200 },
      -- The purest metal the Core can make, in the last thing it builds. This
      -- is also what stops the sintering line being decoration: the Vacuum
      -- Furnace's second category, the Coil Separator's schreibersite and the
      -- whole carbonyl chain all end here.
      --
      -- In the Array's recipe rather than the segment's, and that is a real
      -- constraint rather than a preference: the segment is unlocked by
      -- sae-field-coils, which the Coil Separator's own build cost sits behind,
      -- which the flux sits behind, which the preform sits behind. Putting a
      -- preform in the segment would ask the player to make one before the
      -- research that allows it. The Array is built once, afterwards.
      { type = "item", name = "sae-sintered-preform", amount = 20 },
      { type = "item", name = "sae-arc-mast", amount = 4 }
    },
    results = { { type = "item", name = "sae-ignition-array", amount = 1 } },
    enabled = false
  }
})
