-- The sound-capture probe's own helpers: nothing a player sees or can build.
--
-- The machine under test needs power that can be switched on at a chosen tick
-- without anything in the picture: a pole with no sprite and no wires whose
-- supply area reaches it from well outside the recorded view, and an energy
-- interface with no sprite that supplies it (created at the tick the machine
-- is to start).

local EMPTY = { filename = "__core__/graphics/empty.png", priority = "extra-high", width = 1, height = 1 }
local NOTHING = { layers = {} }

local HIDDEN = { "not-on-map", "placeable-off-grid", "not-blueprintable", "not-deconstructable" }

data:extend({
  {
    type = "electric-pole",
    name = "sae-audio-pole",
    icon = "__core__/graphics/empty.png",
    icon_size = 1,
    hidden = true,
    flags = HIDDEN,
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
  {
    type = "electric-energy-interface",
    name = "sae-audio-supply",
    icon = "__core__/graphics/empty.png",
    icon_size = 1,
    hidden = true,
    flags = HIDDEN,
    max_health = 1,
    collision_box = { { -0.4, -0.4 }, { 0.4, 0.4 } },
    collision_mask = NOTHING,
    selectable_in_game = false,
    energy_source =
    {
      type = "electric",
      buffer_capacity = "100MJ",
      usage_priority = "primary-output",
      input_flow_limit = "0W",
      output_flow_limit = "1GW"
    },
    energy_production = "0W",
    energy_usage = "0W",
    picture = EMPTY
  }
})
