-- The Core's machinery: what draws the kamacite vent. The gas vents are the
-- Gas Pump's (crust-tap.lua).

local derive = require("prototypes.derive")
local item_sounds = require("__base__.prototypes.item_sounds")

-- The vent pump. A pumpjack with an input fluid box added, because drawing
-- melt costs helium-3 -- the scarce vent throttling the rich one. The engine
-- reports missing_required_fluid when the helium runs out, which is a legible
-- failure the player can read without a wiki.
local pump = derive.from("mining-drill", "pumpjack", "sae-vent-pump")
pump.icon = "__space-age-extended__/graphics/icons/vent-pump.png"
pump.minable = { mining_time = 0.5, result = "sae-vent-pump" }

-- Art: rendered in Blender from concept/vent-pump/model/vent_pump.py, the Gas
-- Lift Tower signed off by Liam on 2026-10-21 (T07, T07c, T07d), through
--
--   BLENDER=<blender> tools/blender/render.sh \
--       concept/vent-pump/model/vent_pump.py <scratch> --ports --icon
--
-- Every size and shift below is copied from the meta.json files the packer
-- writes (sheets/meta.json, sheets/ports/meta.json) and from the effects'
-- effects.json; none was measured off a sheet. Sprites are rendered at 2x and
-- drawn at scale 0.5.
--
-- **Four directions, each its own variation, as vanilla's chemical plant.** The
-- tower, its glass riser and the head tank face the camera in all four; the
-- plumbing and the units round it turn with the fluid boxes, so the glass is
-- seen whichever way the pump faces (spec 5).
--
-- **The plate is the machine stopped.** `mech` -- the flow meter, the two
-- gauges, the float lever and the compressor's coupling -- is a layer of the
-- main animation, so it is drawn in every state and only moves while the pump
-- works; its frame 0 is the stopped machine. The plate and shadow are one frame
-- each, repeated to the loop's 24. 0.2 is Liam's loop speed (spec 9).
local VP = "__space-age-extended__/graphics/entity/vent-pump/"
local VP_FRAMES = 24
local VP_SPEED = 0.2

-- Per direction: { width, height, shift } of each sheet, from sheets/meta.json.
local VP_SHEETS =
{
  north =
  {
    base               = { 194, 247, { 0, -0.38281 } },
    shadow             = { 255, 200, { 0.46094, -0.04688 } },
    riser              = { 25, 96, { -0.05469, -0.76562 } },
    riser_light        = { 16, 69, { -0.01562, -0.67969 } },
    glass              = { 26, 38, { 0.3125, 0.53125 } },
    glass_light        = { 17, 15, { 0.30469, 0.66406 } },
    mech               = { 135, 186, { 0.08594, -0.35938 } },
    embers             = { 46, 104, { -0.875, -1.82812 } },
    embers_light       = { 49, 105, { -0.88281, -1.83594 } },
    lens_working_glow  = { 7, 8, { 1.25781, -1.1875 } },
    lens_no_fluid_glow = { 7, 7, { 1.33594, -0.05469 } }
  },
  east =
  {
    base               = { 194, 252, { 0, -0.40625 } },
    shadow             = { 266, 197, { 0.5625, -0.00781 } },
    riser              = { 24, 96, { 0.125, -0.57812 } },
    riser_light        = { 15, 76, { 0.17969, -0.4375 } },
    glass              = { 26, 35, { -0.84375, -0.02344 } },
    glass_light        = { 17, 14, { -0.83594, 0.125 } },
    mech               = { 146, 157, { 0.09375, -0.39844 } },
    embers             = { 45, 97, { 1.11719, -1.83594 } },
    embers_light       = { 46, 98, { 1.10938, -1.82812 } },
    lens_working_glow  = { 7, 8, { 0.66406, 0.73438 } },
    lens_no_fluid_glow = { 7, 7, { -0.32031, 0.96094 } }
  },
  south =
  {
    base               = { 194, 234, { 0, -0.29688 } },
    shadow             = { 256, 199, { 0.46875, -0.05469 } },
    riser              = { 25, 96, { -0.05469, -0.40625 } },
    riser_light        = { 16, 76, { -0.01562, -0.26562 } },
    glass              = { 24, 38, { 0.67188, -0.35938 } },
    glass_light        = { 17, 14, { 0.66406, -0.23438 } },
    mech               = { 140, 22, { -0.04688, -1.26562 } },
    embers             = { 54, 87, { 1, 0.08594 } },
    embers_light       = { 55, 87, { 0.99219, 0.08594 } },
    lens_working_glow  = { 7, 7, { -1.25781, 0.13281 } },
    lens_no_fluid_glow = { 7, 7, { -1.33594, -0.69531 } }
  },
  west =
  {
    base               = { 194, 250, { 0, -0.39062 } },
    shadow             = { 242, 197, { 0.39062, -0.00781 } },
    riser              = { 24, 96, { -0.23438, -0.57812 } },
    riser_light        = { 15, 76, { -0.17969, -0.4375 } },
    glass              = { 26, 35, { 0.84375, -0.02344 } },
    glass_light        = { 17, 14, { 0.83594, 0.125 } },
    mech               = { 45, 157, { 0.69531, -0.39844 } },
    embers             = { 40, 103, { -0.9375, -1.78906 } },
    embers_light       = { 42, 103, { -0.9375, -1.78906 } },
    lens_working_glow  = { 7, 8, { -0.66406, 0.73438 } },
    lens_no_fluid_glow = { 7, 7, { 0.32031, 0.96094 } }
  }
}

-- One layer of direction `dir`: sheet `name` (its file is the name with dashes,
-- then the direction), `frames` frames in one row.
local function vp_layer(dir, name, frames, extra)
  local s = VP_SHEETS[dir][name]
  local layer =
  {
    filename = VP .. name:gsub("_", "-") .. "-" .. dir .. ".png",
    priority = "high",
    width = s[1], height = s[2],
    frame_count = frames,
    line_length = frames,
    animation_speed = VP_SPEED,
    shift = s[3],
    scale = 0.5
  }
  for k, v in pairs(extra or {}) do layer[k] = v end
  return layer
end

-- A light over its paint: the light alone (each pixel's colour times its alpha,
-- as pack.py packs a glow), so it is added, never painted.
local GLOW = { draw_as_glow = true, blend_mode = "additive" }

local function vp_plate(dir)
  return
  {
    layers =
    {
      vp_layer(dir, "base", 1, { repeat_count = VP_FRAMES }),
      vp_layer(dir, "mech", VP_FRAMES),
      vp_layer(dir, "shadow", 1, { repeat_count = VP_FRAMES, draw_as_shadow = true })
    }
  }
end

-- A working layer and its light, per direction.
local function vp_working(paint, light, frames, speed)
  local vis = { fadeout = true }
  for _, dir in ipairs({ "north", "east", "south", "west" }) do
    local extra = { animation_speed = speed }
    vis[dir .. "_animation"] =
    {
      layers =
      {
        vp_layer(dir, paint, frames, extra),
        vp_layer(dir, light, frames, { animation_speed = speed, draw_as_glow = GLOW.draw_as_glow,
                                       blend_mode = GLOW.blend_mode })
      }
    }
  end
  return vis
end

-- The status lenses (spec 7, Liam 2026-10-20 and 2026-10-21): each a glow
-- sprite, seen by day and by night, and a halo in the dark. The glow is the lens
-- lit minus the plate, so it is added over the unlit lens the plate carries. The
-- halo is the game's own light picture (Liam, "Game's light pictures"):
-- light-small.png as a draw_as_light layer centred on the lens, the way a lamp's
-- light is drawn into the light map and never onto the ground by day.
--
-- light-small.png is 150 px across; at 0.1 it is 15 screen px, about four lens
-- widths (each lens is 7 sheet px, 3.5 on screen).
local VP_HALO_SCALE = 0.1
local VP_GREEN = { 0.275, 0.941, 0.353, 1 }     -- #46F05A, the model's lit green
local VP_AMBER = { 1, 0.604, 0.071, 1 }         -- #FF9A12, the model's lit amber
local CLEAR = { 0, 0, 0, 0 }

local function vp_lens(name, halo_tint)
  local vis = {}
  for _, dir in ipairs({ "north", "east", "south", "west" }) do
    vis[dir .. "_animation"] =
    {
      layers =
      {
        vp_layer(dir, name, 1, GLOW),
        {
          filename = "__core__/graphics/light-small.png",
          priority = "extra-high",
          width = 150, height = 150,
          draw_as_light = true,
          tint = halo_tint,
          shift = VP_SHEETS[dir][name][3],
          scale = VP_HALO_SCALE
        }
      }
    }
  end
  return vis
end

-- Green, the control house's: a plain working visualisation, so the engine
-- draws it while the pump works and in low power, and in no other state.
local vp_lens_working = vp_lens("lens_working_glow", VP_GREEN)

-- Amber, the switchgear's: drawn in every state and tinted by the status
-- (T07b). Every status colour is clear but `insufficient_input`, which is the
-- one the engine shows for missing_required_fluid, so it lights only when the
-- helium is missing -- and an unpowered dry pump reports no_power, so it stays
-- dark. Its glow and halo are white-tinted here and take the amber from the
-- status: the model's own #FF9A12.
local vp_lens_no_fluid = vp_lens("lens_no_fluid_glow", { 1, 1, 1, 1 })
vp_lens_no_fluid.always_draw = true
vp_lens_no_fluid.apply_tint = "status"

-- The effects (spec 10, effects/effects.json), each drawn only while working
-- and faded out on stop, placed per direction as the chemical plant places its
-- smoke.
local function vp_effect(file, w, h, frames, line, speed, shift)
  return
  {
    filename = VP .. file,
    priority = "high",
    width = w, height = h,
    frame_count = frames,
    line_length = line,
    animation_speed = speed,
    shift = shift,
    scale = 0.5
  }
end

-- A2, the wisp: melt-lit fume off the head tank's gas offtake, a loop of its
-- own, over the building as the chemical plant's smoke is.
local vp_wisp =
{
  fadeout = true,
  constant_speed = true,
  render_layer = "wires",
  animation = vp_effect("wisp-a2.png", 80, 176, 32, 8, 0.25, { 0, -1.21875 }),
  north_position = { 0.2, -1.97 },
  east_position = { 0.38, -1.79 },
  south_position = { 0.2, -1.61 },
  west_position = { 0.02, -1.79 }
}

-- E4, cold breath off the stop valve at each charge, in step with the loop. No
-- south: facing south the valve stands behind the tower (Liam, "Leave E4 out
-- facing south").
local vp_breath_anim = vp_effect("cold-breath-e4.png", 64, 72, 24, 12, VP_SPEED, { 0, -0.375 })
local vp_breath =
{
  fadeout = true,
  north_animation = vp_breath_anim,
  east_animation = vp_breath_anim,
  west_animation = vp_breath_anim,
  north_position = { 0, 0.7 },
  east_position = { -1.06, -0.36 },
  west_position = { 1.06, -0.36 }
}

-- E5, the purge puff off the float chamber's cap as each charge breaks out.
local vp_purge =
{
  fadeout = true,
  render_layer = "wires",
  animation = vp_effect("purge-e5.png", 64, 80, 24, 12, VP_SPEED, { 0, -0.4375 }),
  north_position = { 0.62, -1.905 },
  east_position = { 0.8, -1.725 },
  south_position = { 0.62, -1.545 },
  west_position = { 0.44, -1.725 }
}

-- E3, the melt's orange light on the ground round the tower's foot. A light,
-- so seen only in the dark. Size 2.5 (a radius in tiles): Liam, "Smaller (size
-- 2-3)", after effects.json's 7 lit fourteen tiles.
local vp_ground_light =
{
  name = "ground-light",
  fadeout = true,
  light = { type = "basic", intensity = 0.55, size = 2.5, color = { 1, 0.48, 0.18 } },
  north_position = { 0, 0.18 },
  east_position = { 0.18, 0.36 },
  south_position = { 0, 0.54 },
  west_position = { -0.18, 0.36 }
}

-- The pipe pictures are the model's own, rendered on the middle tile of each
-- face in assembler 3's outline (sheets/ports/meta.json, each shift taken from
-- the tile outside the port); the covers are vanilla's, as assembler 3's are
-- (spec 8). A north stub is drawn behind the building, as vanilla's assemblers
-- draw it.
local function vp_port(face, w, h, shift)
  return
  {
    filename = VP .. "port-" .. face .. ".png",
    priority = "extra-high",
    width = w, height = h,
    shift = shift,
    scale = 0.5
  }
end
local VP_PORTS =
{
  north = vp_port("N", 53, 22, { 0.00781, 0.34375 }),
  east = vp_port("E", 31, 71, { -0.72656, 0.05469 }),
  south = vp_port("S", 63, 69, { -0.00781, -0.77344 }),
  west = vp_port("W", 31, 72, { 0.72656, 0.01562 })
}
local covers = derive.pipe_covers()

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
pump.output_fluid_box =
{
  volume = 1000,
  pipe_picture = VP_PORTS,
  pipe_covers = covers,
  secondary_draw_orders = { north = -1 },
  pipe_connections =
  {
    { flow_direction = "output", direction = defines.direction.north, position = { 0, -1 } }
  }
}
pump.input_fluid_box =
{
  volume = 200,
  pipe_picture = VP_PORTS,
  pipe_covers = covers,
  secondary_draw_orders = { north = -1 },
  pipe_connections =
  {
    { flow_direction = "input", direction = defines.direction.south, position = { 0, 1 } }
  }
}
-- The kamacite vent, and only this machine on it. `sae-vent` holds nothing
-- else now: the gas vents moved to `sae-gas`, which the Gas Pump works, so the
-- Vent Pump draws melt only. See the note beside the categories in
-- resources.lua for what this closes.
pump.resource_categories = { "sae-vent" }

derive.own_graphics(pump,
{
  status_colors =
  {
    working = CLEAR,
    low_power = CLEAR,
    idle = CLEAR,
    no_minable_resources = CLEAR,
    insufficient_input = VP_AMBER,
    full_output = CLEAR,
    disabled = CLEAR,
    no_power = CLEAR
  },
  animation =
  {
    north = vp_plate("north"),
    east = vp_plate("east"),
    south = vp_plate("south"),
    west = vp_plate("west")
  },
  working_visualisations =
  {
    vp_working("riser", "riser_light", VP_FRAMES, VP_SPEED),
    vp_working("glass", "glass_light", VP_FRAMES, VP_SPEED),
    -- E2, the embers: rendered with every nearer part held out, so they carry
    -- their own occlusion and are drawn over the machine. 48 frames at twice
    -- the loop's speed, two to each machine frame, so not constant_speed.
    vp_working("embers", "embers_light", 48, 2 * VP_SPEED),
    vp_lens_working,
    vp_lens_no_fluid,
    vp_wisp,
    vp_breath,
    vp_purge,
    vp_ground_light
  }
})
-- The pumpjack's mirrored set draws a horsehead nodding the other way: pumpjack
-- files that describe nothing here (spec 14). Cleared, the engine draws the
-- one set flipped or not.
pump.graphics_set_flipped = nil
-- The tower and the embers stand up to 1.16 tiles above the north edge (the
-- smoke is drawn in its own layer); the pumpjack's 1 would cull the top of it.
pump.drawing_box_vertical_extension = 1.2

data:extend({ pump })

data:extend({
  {
    type = "item",
    name = "sae-vent-pump",
    icon = "__space-age-extended__/graphics/icons/vent-pump.png",
    subgroup = "extraction-machine",
    order = "z[sae]-a[vent-pump]",
    place_result = "sae-vent-pump",
    inventory_move_sound = item_sounds.pumpjack_inventory_move,
    pick_sound = item_sounds.pumpjack_inventory_pickup,
    drop_sound = item_sounds.pumpjack_inventory_move,
    stack_size = 20,
    weight = 20 * kg
  }
})
