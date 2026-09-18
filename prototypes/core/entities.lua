-- The Core's machinery: what draws the vents.

local derive = require("prototypes.derive")
local item_sounds = require("__base__.prototypes.item_sounds")

-- The vent pump. A pumpjack with an input fluid box added, because drawing
-- melt costs helium-3 -- the scarce vent throttling the rich one. The engine
-- reports missing_required_fluid when the helium runs out, which is a legible
-- failure the player can read without a wiki.
local pump = derive.from("mining-drill", "pumpjack", "sae-vent-pump")
pump.icon = "__space-age-extended__/graphics/icons/vent-pump.png"
pump.minable = { mining_time = 0.5, result = "sae-vent-pump" }

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
local covers = pump.output_fluid_box.pipe_covers
pump.output_fluid_box =
{
  volume = 1000,
  pipe_covers = covers,
  pipe_connections =
  {
    { flow_direction = "output", direction = defines.direction.north, position = { 0, -1 } }
  }
}
pump.input_fluid_box =
{
  volume = 200,
  pipe_covers = covers,
  pipe_connections =
  {
    { flow_direction = "input", direction = defines.direction.south, position = { 0, 1 } }
  }
}
-- Only the Core's vents, and only this machine on them. See the note beside the
-- `sae-vent` resource category in resources.lua for what this closes.
pump.resource_categories = { "sae-vent" }

-- Art: four plates, drawn together and split by tools/cut-rotation-strip.py.
--
-- **The four are one machine with its plumbing moved, not four camera angles.**
-- §5 is blunt about it: ask a generator for four viewpoints and it returns a
-- turntable, which is unusable, because Factorio's camera never moves.
--
-- **And the plumbing has to match the prototype, because on this building the
-- pipes are the fluid boxes.** Helium enters the south face and melt leaves the
-- north face, both on the centre tile of their edge (see the fluid boxes above),
-- and the four plates rotate that pair rigidly: north is riser-top/intake-bottom,
-- east is riser-right/intake-left, south is riser-bottom/intake-top, west is
-- riser-left/intake-right. Checked against the declared connections rather than
-- trusted -- a plate whose plumbing disagrees is a building the player plumbs
-- backwards, and the two fluids are not interchangeable.
--
-- **Every scale and shift is measured off the base plate, never off the
-- content.** The pipes stick out further in some views than others, so content
-- centring slides the machine off its own tile in exactly the views whose
-- plumbing hangs furthest over the edge. The cutter fits the BASE SQUARE to
-- 3.000 tiles and centres on it; the four came out at 3.000, 2.969, 2.984 and
-- 2.953 tiles, all at or under the footprint, which is the safe side to miss on.
--
-- The y shifts differ between the axes and that is not a mistake: a riser
-- leaving through the top edge is drawn standing up, so it adds height above the
-- base and pushes the base low in its canvas. North needs a quarter tile of lift
-- where east and west need almost none.
local VP = "__space-age-extended__/graphics/entity/vent-pump/"
local function vp_plate(dir, w, h, sx, sy, sw, sh, ssx)
  return
  {
    layers =
    {
      {
        filename = VP .. "base-" .. dir .. ".png",
        priority = "high",
        width = w, height = h,
        shift = { sx, sy },
        scale = 0.5
      },
      {
        filename = VP .. "base-" .. dir .. "-shadow.png",
        priority = "high",
        draw_as_shadow = true,
        width = sw, height = sh,
        shift = { ssx, sy },
        scale = 0.5
      }
    }
  }
end

-- The one thing that moves: the melt rising and falling in the riser's sight
-- glass, sixteen frames, four directions.
--
-- **Four directions, because the sight port is on the riser.** §6.1 used to say
-- this layer needed one, "because the sight port and flow disc sit on the stack,
-- which does not rotate" -- but the port is on the riser, and the riser is the
-- fluid box, so it is the one part of this building that *must* turn. Measured
-- off the cut plates: the glow sits top-centre in north, right in east, bottom
-- in south, left in west.
--
-- **Sixteen frames, not thirty-two.** The glass is 12 x 29 plate px in the north
-- view -- six by fifteen on screen -- so a rising level has at most sixteen
-- distinct pictures in it. Thirty-two would be sixteen images and sixteen
-- duplicates, which is the arithmetic that cut the Dross Classifier's shake from
-- sixty-four frames to twelve.
--
-- **It is a brightening laid over a lit plate, not a glow lifted out of an unlit
-- one.** That is the opposite of what this mod usually does, and the reason is
-- the building: `split-glow.py` works when the emissive parts are strongly
-- chromatic against near-neutral iron-nickel, and this riser is copper. Every
-- threshold that saved the port took half the riser with it. So the plate keeps
-- its glow and this sheet adds to it -- which is also the truer reading, since a
-- wellhead full of melt is warm whether or not it is pumping. What changes when
-- it runs is how much of the glass is full.
--
--   tools/build-fill-frames.py base-north.png --region 87 29 108 64 \
--       --frames 16 --min-lightness 0.50 --out port-north.png
--
-- **And it is a small gesture, knowingly.** The port is 16.7 % of the building's
-- own box against vanilla's 72-113 %, and the plate is cut, so it cannot grow.
-- It is built because it costs sixteen tiny derived sprites and gives the
-- machine a running-versus-stopped tell it otherwise has none of -- not under any
-- illusion that it carries the read at play zoom. `04-the-core.md` §26 is the
-- standing warning and this is the exception taken with its eyes open.
local function vp_port(dir, w, h, sx, sy)
  return
  {
    filename = VP .. "port-" .. dir .. ".png",
    priority = "high",
    draw_as_glow = true,
    width = w, height = h,
    frame_count = 16, line_length = 8,
    animation_speed = 0.25,        -- the loop in a little over a second
    shift = { sx, sy },
    scale = 0.5
  }
end

derive.own_graphics(pump,
{
  animation =
  {
    north = vp_plate("north", 203, 281,  0.00781, -0.23438, 441, 301, 1.71094),
    east  = vp_plate("east",  248, 198,  0.00000, -0.02344, 420, 218, 1.18750),
    south = vp_plate("south", 202, 265, -0.00781, -0.14844, 427, 285, 1.59375),
    west  = vp_plate("west",  247, 198, -0.01562, -0.02344, 419, 218, 1.17188)
  },
  working_visualisations =
  {
    -- No `always_draw`, so it is drawn only while the pump is working. The
    -- shifts are the port crop's own offset plus the plate's, both measured.
    {
      north_animation = vp_port("north", 21, 35, -0.05469, -1.70313),
      east_animation  = vp_port("east",  24, 28,  1.39062, -0.35156),
      south_animation = vp_port("south", 23, 29, -0.07812,  1.02344),
      west_animation  = vp_port("west",  26, 28, -1.32031, -0.35156)
    }
  }
})

data:extend({ pump })
