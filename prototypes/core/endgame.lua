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
      stack_size = 50,
      weight = 2000
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
    stack_size = 50,
    weight = 2000
  },
  {
    type = "item",
    name = "sae-coil-assembly",
    icon = "__space-age-extended__/graphics/icons/coil-assembly.png",
    subgroup = "intermediate-product",
    order = "z[sae]-a[coil-assembly]",
    stack_size = 20,
    weight = 10000
  },
  {
    type = "item",
    name = "sae-coolant-loop",
    icon = "__space-age-extended__/graphics/icons/coolant-loop.png",
    subgroup = "intermediate-product",
    order = "z[sae]-b[coolant-loop]",
    stack_size = 20,
    weight = 10000
  },
  {
    type = "item",
    name = "sae-field-coil-segment",
    icon = "__space-age-extended__/graphics/icons/field-coil-segment.png",
    subgroup = "intermediate-product",
    order = "z[sae]-c[field-coil-segment]",
    stack_size = 10,
    weight = 20000
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
      { type = "item", name = "sae-coolant-loop", amount = 1 }
    },
    results = { { type = "item", name = "sae-field-coil-segment", amount = 1 } },
    enabled = false,
    hide_from_player_crafting = true
  }
})

--------------------------------------------------------------------------------
-- The Ignition Array.
--------------------------------------------------------------------------------

local array = table.deepcopy(data.raw["rocket-silo"]["rocket-silo"])
array.name = "sae-ignition-array"
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

-- Art. See graphics/building-spec-ignition-array.md sections 6.1 and 13.
--
-- Section 6.1 is the scoping decision and it still holds: vanilla's silo uses
-- sixteen art slots, several of them 64-frame sheets running to millions of
-- pixels, and replacing all of it is not a realistic target. What is replaced
-- here is the part that carries the read -- the deck, the cradle ring, the
-- closed iris -- measured at exactly 576 px, **9.000 tiles**, centred to 0.0 px
-- with alpha zero on all four canvas edges.
--
-- Everything that is launch-pad furniture is emptied rather than left inherited.
-- On a world whose entire premise is that nothing leaves, vanilla's blast doors
-- sliding open, its engine bell, its steam vents and its extractor fans would
-- each be a lie, and they would draw straight over our deck. Emptying them costs
-- the open-shaft frames until the iris plates of section 6.1 are drawn; the
-- alternative was vanilla's doors opening on our building.
local IA = "__space-age-extended__/graphics/entity/ignition-array/"
array.base_day_sprite =
{
  filename = IA .. "base.png",
  priority = "medium",
  width = 608, height = 602,
  shift = { 0, 0 },
  scale = 0.5
}
array.shadow_sprite =
{
  filename = IA .. "base-shadow.png",
  priority = "medium",
  draw_as_shadow = true,
  width = 1073, height = 602,
  shift = { 3.63281, 0 },
  scale = 0.5
}
array.base_front_sprite = util.empty_sprite()
array.base_night_sprite = nil
array.door_back_sprite = util.empty_sprite()
array.door_front_sprite = util.empty_sprite()
array.hole_sprite = util.empty_sprite()
array.hole_light_sprite = util.empty_sprite()
array.rocket_shadow_overlay_sprite = util.empty_sprite()
array.rocket_glow_overlay_sprite = util.empty_sprite()
array.red_lights_back_sprites = util.empty_sprite()
array.red_lights_front_sprites = util.empty_sprite()
array.satellite_animation = nil
array.arm_01_back_animation = nil
array.arm_02_right_animation = nil
array.arm_03_front_animation = nil
-- `graphics_set.working_visualisations` is left inherited on purpose. The silo
-- names one of its entries -- "crafting" -- from elsewhere in the prototype, and
-- clearing the list makes the engine refuse to load with
-- `Working visualisation "crafting" doesn't exist`. Section 6.1 wants these
-- replaced by a derived glow; until that exists they stay, which is the one
-- piece of inherited launch furniture still drawn.
array.heating_energy = nil
array.fast_replaceable_group = nil
array.next_upgrade = nil
data:extend({ array })

--------------------------------------------------------------------------------
-- The sealed roboport.
--
-- Restricted to pressure 1-9, so it works on the Core and nowhere else in the
-- game: not on a platform (0), not on any vanilla world (Aquilo is lowest at
-- 300). It competes with nothing, which is why a second roboport is not a
-- second tier.
--------------------------------------------------------------------------------

local port = table.deepcopy(data.raw.roboport["roboport"])
port.name = "sae-sealed-roboport"
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
-- 2.48 tiles above the origin. The iris centre is 99 px down from there, and the
-- dome crown 55 px, which puts them 0.94 and 1.62 tiles up.
port.spawn_and_station_height = 0.94
-- Robots pass behind the dome and then in front of it, so the swap belongs just
-- above the crown rather than at vanilla's 0.87, which is halfway up our dome.
port.stationing_render_layer_swap_height = 1.62

-- Art. See graphics/building-spec-sealed-roboport.md sections 6, 7 and 13.
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
--     This was recorded as "wrong but quiet". It is not quiet. Measured against
--     vanilla: vanilla's door frame is 97 px, a 1.52 tile opening, and the
--     aperture drawn on our dome is a connected 46 x 36 px blob -- 0.72 x 0.56
--     tiles, 47% of vanilla's width and 45% of its area. A construction robot is
--     about half a tile across, so ours is barely wider than the robot coming
--     through it, and robots appear to squeeze out of a porthole.
--
--     Half of that is fixed here, by putting the spawn height on the iris
--     instead of on vanilla's mouth. The other half needs the plate redrawn with
--     the aperture at roughly 96 px -- 1.5 tiles -- to match what vanilla gives
--     a robot to fly through.
--   * `recharging_animation` -- vanilla draws its own contact arc at each
--     charging offset. The docks are drawn in our plate at those offsets, but
--     vanilla's arc is shaped for an open pad, so it is emptied too. The light
--     stays, retinted to the amber of section 3.3, so an occupied dock still
--     reads at night.
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

port.fast_replaceable_group = nil
port.next_upgrade = nil
data:extend({ port })

data:extend({
  {
    type = "item",
    name = "sae-ignition-array",
    icon = "__space-age-extended__/graphics/icons/ignition-array.png",
    subgroup = "production-machine",
    order = "z[sae]-z[ignition-array]",
    place_result = "sae-ignition-array",
    stack_size = 1,
    weight = 500000
  },
  {
    type = "item",
    name = "sae-sealed-roboport",
    icon = "__space-age-extended__/graphics/icons/sealed-roboport.png",
    subgroup = "logistic-network",
    order = "z[sae]-a[sealed-roboport]",
    place_result = "sae-sealed-roboport",
    stack_size = 10,
    weight = 40000
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
      { type = "item", name = "sae-arc-mast", amount = 4 }
    },
    results = { { type = "item", name = "sae-ignition-array", amount = 1 } },
    enabled = false
  }
})
