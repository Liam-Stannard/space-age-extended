-- The screenshot probe's own helpers: nothing a player sees or can build.
--
-- A building's states need power arranged around it -- a load for a generator
-- to work into, a supply for a machine that consumes -- and the poles and
-- interfaces that do it must not be in the picture. So: a pole with no sprite,
-- no wires and a supply area large enough to stand well outside the frame,
-- and two energy interfaces with no sprite, one drawing and one supplying.

local EMPTY = { filename = "__core__/graphics/empty.png", priority = "extra-high", width = 1, height = 1 }
local NOTHING = { layers = {} }

local function interface(name, priority)
  return
  {
    type = "electric-energy-interface",
    name = name,
    icon = "__core__/graphics/empty.png",
    icon_size = 1,
    hidden = true,
    flags = { "not-on-map", "placeable-off-grid", "not-blueprintable", "not-deconstructable" },
    max_health = 1,
    collision_box = { { -0.4, -0.4 }, { 0.4, 0.4 } },
    collision_mask = NOTHING,
    selectable_in_game = false,
    energy_source =
    {
      type = "electric",
      buffer_capacity = "100MJ",
      usage_priority = priority,
      input_flow_limit = "1GW",
      output_flow_limit = "1GW"
    },
    energy_production = "0W",
    energy_usage = "0W",
    picture = EMPTY
  }
end

data:extend({
  {
    type = "electric-pole",
    name = "sae-shot-pole",
    icon = "__core__/graphics/empty.png",
    icon_size = 1,
    hidden = true,
    flags = { "not-on-map", "placeable-off-grid", "not-blueprintable", "not-deconstructable" },
    max_health = 1,
    collision_box = { { -0.4, -0.4 }, { 0.4, 0.4 } },
    collision_mask = NOTHING,
    selectable_in_game = false,
    supply_area_distance = 40,
    maximum_wire_distance = 1,
    auto_connect_up_to_n_wires = 0,
    draw_copper_wires = false,
    draw_circuit_wires = false,
    connection_points = { { wire = { copper = { 0, 0 } }, shadow = { copper = { 0, 0 } } } }
  },
  interface("sae-shot-load", "secondary-input"),
  interface("sae-shot-supply", "primary-output")
})
