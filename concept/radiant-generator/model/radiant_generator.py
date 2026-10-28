"""Radiant Generator (sae-radiant-generator): the Carousel Foundry at 5x5 -- the shipping model.

  BLENDER=<blender 5> tools/blender/render.sh concept/radiant-generator/model/radiant_generator.py <out-dir> \
      --ports --icon [--collide]
  (or directly: blender -b --python radiant_generator.py -- <out-dir> [--idle | --ports | --icon | --collide |
                --wreck] [--samples N] [--anim-samples N])

  --idle     the plate, the still and a working frame 0 (plate + glow lit in one render) only
  --ports    render.json alone: the generator has no ports (spec 5, 8), and the contract says so
  --icon     icon.png: the whole machine, working, framed to a 1024 px square
  --collide  no render: every moving part in every frame against every other part, by BVH;
             collide.txt in <out-dir>
  --wreck    the wreck alone: wreck.png (its light out) and wreck-lit.png (the well's dying blue on, the
             glow's render): the quick loop for the remnants [--dying K: the dying blue's strength]
  --study F,F,..  [--glowframes F,..]  a study, nothing packed (T08c): at each frame the whole machine working
             (look-NN) and stopped (unlit-NN); the well's light and the other openings' alone (wellglow-NN,
             otherglow-NN); the openings' and the collide fixes' places on the screen (SPOT, REGION lines)

Spec: concept/radiant-generator/building-spec-radiant-generator.md (written 35d626b, Liam
"Agreed to all the drafts", 2026-10-20). Built from the signed-off concept, options round 7
(r7_carousel_foundry.py and r7_kit.py, Liam 2026-10-19 "Sign off"): the same parts in the same
places, the same finish. What the shipping model changes (task radiant-generator-options, T08):

  - the light through tools/blender/radiant.py (spec 3.3), flicker 0, round 7's strength
    curves (rg_kit.lights, pose_light);
  - the layers of spec 7, each its own cropped sheet, declared to the packers (DECL): the
    plate (everything that does not move, openings dark); the moving parts, one layer per
    part that moves apart from the others (the carousel table, its drive pinion and coupling,
    the crane with the well's lid (T08d: one layer, so their shadows fall on each other), the commutator, the two other couplings, the three gauges),
    each rendered alone with every other part a shadow catcher, so it carries the shadow it
    casts on the rest of the machine and is cut by whatever stands in front of it; the
    working windows (radiant.py's plate light) and their glow, one layer, every opening's
    bloom TIGHT (the well's too: rg_kit's note on R); the status lamps, white-cut;
  - the moving parts keep their finish as they move: materials.layered() reads world
    position, so each moving part reads the position it had at frame 0 instead (pin());
  - 32 frames, one crane cycle, at round 7's 1x GIF pace: 70 ms a frame, animation_speed
    60 x 0.070 = 4.2 ticks a frame, 5/21 (spec 6, decision 10);
  - its own wreck (spec 6: "the machine's own wreck, as the Siderane turbine's"): wreck.py, with a faint
    dying blue in the well's torn mouth (T08c, Liam 2026-10-21: "Faint dying blue");
  - what --collide found in round 7's geometry, fixed (FIX 1-14, in rg_kit.py and here): the hood's
    walls over the turning table, the chute, the bin and its lid, the hub, the pinion and its case,
    the crane's wheels and the housing's roof fittings in its path, the well (a solid disc over its
    mouth: now a ring with a bore, the hoists setting the cell on the light), the lid's hinge, the
    commutator's riser and its bed (a pit), the posts inside the housing, a ladder, a barrel, the
    lagged line, the pockets' bores; collide.py says which contacts are meant and why;
  - the glow renders' black floor taken out (glow_floor()); the slot's pane inset from its frame;
    the port's glow emission 18 (rg_kit's note on R); the cable sleeves' label paint matte cream.

Units are tiles; north is +Y. Nothing here is adopted: the sheets move to graphics/ only on
Liam's sign-off.
"""
import json
import math
import os
import re
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rg_kit as K  # noqa: E402
from rg_kit import *  # noqa: F401,F403,E402
import contract  # noqa: E402

IDLE = "--idle" in K.argv
PORTS = "--ports" in K.argv
ICON = "--icon" in K.argv
COLLIDE = "--collide" in K.argv
WRECK_ONLY = "--wreck" in K.argv
PLATE_SAMPLES = K.opt("--samples", 80)          # round 7's
ANIM_SAMPLES = K.opt("--anim-samples", 64)
SUN_E = K.opt("--sun", 8.8)                     # round 7's

NF = 32                                         # one crane cycle (spec 6)
SPEED = 5 / 21                                  # 70 ms a frame: 4.2 ticks (spec 6, decision 10)
# the moving layers in the order they are drawn: the crane over the table it shadows
LAYERS = ("carousel", "drive", "crane", "commutator", "coupling-converter", "coupling-pump",
          "gauge-switchgear", "gauge-converter", "gauge-transformer")
# T08d (Liam 2026-10-21, "Fix: lid in the crane's layer"): the well's lid is rendered in the crane's
# layer, so their shadows fall on each other in one pass. Rendered apart, each pass saw the other part
# as a shadow catcher already shading the spot where both their shadows fall, so neither layer carried
# that shadow and frames 18-24 showed a sunlit hole by the well (idle-lid-shadow.png). The kit still
# names the lid's pivot "lid": --collide tests the lid against the crane as two layers (RAW_LAYERS)
RENDER_AS = {"lid": "crane"}
RAW_LAYERS = LAYERS + tuple(RENDER_AS)
# about their own axes, held to their centroid; the pump's coupling is half hidden behind its motor and
# pump, so its visible centroid moves as it turns (7.5 px on the first pack): a cycle, unchecked
TURNING = ("commutator", "coupling-converter")
GLOWS = [("window-glow" if "disc" in g else "well-glow", g) for g in K.R.groups(("disc", "slot", "tube", "surface"))]
WRECK_CANVAS = (576, 576)       # 9 x 9 tiles: the wreck on its 5 x 5, its scorch and shadow past it


def anim(name):
    return dict(name=name, frames=NF, motion="turn" if name in TURNING else "cycle", animation_speed=SPEED)


window = K.R.window_animation("window", NF)
window["animation_speed"] = SPEED
DECL = dict(
    footprint=(5, 5),
    directions="one",               # spec 5: one picture for all four directions
    passes=[
        dict(name="idle", kind="plate", sheet="base"),
        dict(name="still", kind="still"),
        dict(name="shadow", kind="shadow", sheet="shadow"),
        dict(name="lamp", kind="light", sheet="status-lamp"),
        # its glow (T08d; Liam 2026-10-21, "Make it glow at night"): the well's dying blue as a
        # draw_as_glow layer over the wreck, so the corpse shows it at night (contract.py's remnants glow)
        dict(name="wreck", kind="remnants", sheet="remnants", canvas=WRECK_CANVAS,
             glow=dict(name="wreck-lit", sheet="remnants-glow")),
    ],
    animations=[anim(n) for n in LAYERS] + [window]
    + [K.R.glow_animation(name, "window", NF, shapes) for name, shapes in GLOWS],
    ports=[],                       # spec 8: no fluid box, no facing port
    lights=None,                    # set below (LIGHTS)
)

# the four steady blue lights at the openings, for the dark (Liam 2026-10-21, Q11 "Add steady blue lights";
# T08c's positions, sizes and intensities, "Accept": four draw_as_light layers in the animation only).
# Declared here (T08i; contract.py's lights): each a draw_as_light layer of the game's light-medium.png
# (300 px), scale = size x 32 / 300, tint = colour x intensity, drawn only while working
LIGHT_COLOUR = (0.29, 0.53, 1.0)
LIGHTS = [  # name, shift (tiles from the entity's centre on the screen, x right, y down), size (tiles), intensity
    ("port", (-1.05, -0.05), 2.0, 0.5),
    ("well", (1.25, -1.02), 2.5, 0.45),
    ("slot", (1.25, -1.70), 3.5, 0.6),
    ("tubes", (2.25, -0.60), 4.0, 0.5),
]
DECL["lights"] = [dict(name=f"{n}-light", kind="layer", filename="__core__/graphics/light-medium.png",
                       width=300, height=300, scale=round(size * 32 / 300, 5),
                       tint=[round(c * inten, 4) for c in LIGHT_COLOUR], shift=list(shift), working=True)
                  for n, shift, size, inten in LIGHTS]

# ---------------------------------------------------------------- the machine (round 7, as signed off)
K.build_materials(((0.45, 0.3), (0.95, 0.35), (1.4, 0.3)))
lights([5])

CX, CY, RR, ZD = -1.05, 0.45, 1.25, 0.85
ZR = 1.8
# the deck is the floor between the units, not a plinth to the edge
floor(x0=-2.2, x1=2.2, n=9, notches=((1.7, 1.7, 2.5, 2.5), (-2.5, 1.75, -1.6, 2.5), (-2.5, -2.5, -1.75, -1.9),
                                     (1.5, -2.5, 2.5, -1.9)))

car = carousel(CX, CY, RR, n=8, zd=ZD, pick_a=0.0, L=4, drive_a=1.95)
P = car["pick"]
# the spent bin under the chute, west
box((-2.28, -0.3, 0.28), (0.42, 0.5, 0.56), "lead", bevel=0.02)          # FIX 3: 0.04 lower, its lid under the
box((-2.28, -0.3, 0.58), (0.46, 0.54, 0.05), "dark_steel")                # turning table's rim (round 7's crossed it)
handwheel((-2.28, -0.5, 0.7), 0.08)
hazard_tag((-2.28, -0.555, 0.4), 0.36, 0.05)

# the crucible and its plate rack, east
X0, X1, Y0, Y1, ZT = 0.45, 2.02, -0.8, 1.5, 1.05
W = crucible(X0, X1, Y0, Y1, ZT, well=(1.25, CY), slot=(0.75, 1.75, 0.95, 1.33), hinge="E", plates="x")
# tubes on the east flank, arms into the wall
TY = [-0.62 + 0.46 * i for i in range(5)]
box((2.25, 0.3, 0.06), (0.42, 2.3, 0.12), "dark_steel")
for i, y in enumerate(TY):
    tube(2.25, y, 0.1, i, h=0.9, arm=(-1, 0), arm_len=0.2)
# the copper bus along the caps (T08k: its end bent up into the terminal box's clamp, below)
pipe([(2.44, TY[0] - 0.2, 1.2), (2.44, TY[-1] + 0.1, 1.2)], r=0.03, mat="copper", flanges=False)

# the crane: rails on the north shield housing and on posts along the crucible's south face
housing(-0.2, 1.62, 1.78, 1.95, ZR - 0.06, mat="grey", roof="teal", dress=False)     # FIX 6 (rg_kit)
radiator(-0.1, 1.68, 1.6, 0.85, 1.68, mat="grey", fins=16)
# the coolant expansion tank: the north-east corner, round, standing clear of the housing
vtank(2.15, 2.02, 0.3, 1.3, mat="grey", bands=(0.4, 0.95), top="teal", nozzle=(-0.4, -0.3))
hose([(1.88, 1.85, 0.6), (1.8, 1.72, 0.85), (1.72, 1.7, 1.2)], r=0.05, mat="hose_k")
hazard_tag((2.15, 1.71, 0.7), 0.3, 0.05)
ladder(2.15, 1.63, 0.1, 1.2, axis="y", mat="ochre")     # FIX 11: 0.07 south, off the tank's wall (round 7's stood in it)
# FIX 7: at the well the hoists set the cell on the light's surface, its foot 0.005 over it (round 7's
# went 0.16 through it, and through the disc that covered the mouth)
WELL_DROP = 0.17
crane("x", (-1.0, 1.78), ZR, CY, P[0], W[0], P[2], W[2] + WELL_DROP, -0.55, 1.74, d=0.38, label_n=4,
      rail_posts=(-0.5, 0.4, 1.68), posts_on=lambda u, v: v < 1.5 or u < -0.2)       # FIX 10 (rg_kit)

# the DC bus: the tubes' and plates' bars down a tray to the switchgear, SE. T08d (Liam 2026-10-21, "The
# cables on the bottom right also clip"): round 7's tray stepped down level while its cables sloped, so they
# passed through its floor, and they ended in the air over the cabinets. Now the tray runs level from a
# terminal block on the tubes' copper bar, on a stand at its end, and its cables drop into a gland on the
# switchgear's top
# T08i: the tray open, its cables held by cleats over them, none under a bar (rg_kit.tray)
# T08j's terminal (an insulated block on a pedestal beside the plinth, 347bccc) is replaced by T08k's box.
# T08k (Liam 2026-10-21 on T08j: "Where do the wires actually connect to? They just look like they're connected
# to a floating terminal"; then "A box on the tube column's base"): a terminal box standing on the tubes' plinth,
# the plinth run on 0.4 south to carry it, its foot flange bolted down. The copper bus along the caps bends up
# over its lid's edge into it, clamped onto a ceramic bushing on the lid; the three cables leave its south face through a gland
# each, one by one as the substation's leads leave its box (terminal-vanilla-study.png), straight into the tray's
# open north end, so the power reads tubes -> bus -> box -> glands -> tray -> switchgear
# The camera's 60 degrees set the heights (the screen's v is y + z/2): a cable climbing southward points almost at
# the viewer and its twist reads as a coil, and one rising out of a lid gland and turning south crosses back over the
# gland. So the tray runs level at the switchgear's height, as T08i's did, the glands sit high on the box's south
# face on the tray's line, and the box stands as tall as that needs (its lid at 1.30, the tubes' caps 1.22-1.42)
TB_X, TB_Y, TB_W, TB_D, TB_TOP = 2.29, -1.09, 0.32, 0.26, 1.30            # the box: centre, size, its lid's top
box((2.25, -1.05, 0.06), (0.42, 0.4, 0.12), "dark_steel")                 # the plinth run on 0.4 under the box
box((TB_X - 0.005, TB_Y, 0.135), (TB_W + 0.03, TB_D + 0.03, 0.03), "dark_steel", bevel=0.004)  # its foot flange
for bx in (-1, 1):
    for by in (-1, 1):
        cyl((TB_X - 0.005 + bx * (TB_W / 2 + 0.002), TB_Y + by * (TB_D / 2 + 0.002), 0.154), 0.011, 0.01, "bolt",
            verts=6, bevel=0)
box((TB_X, TB_Y, (0.12 + TB_TOP - 0.02) / 2), (TB_W, TB_D, TB_TOP - 0.02 - 0.12), "grey", bevel=0.01)  # the box
box((TB_X, TB_Y, TB_TOP - 0.01), (TB_W + 0.02, TB_D + 0.02, 0.02), "grey", bevel=0.004)  # its bolted lid, the box's paint
for bx in (-1, 1):
    for by in (-1, 1):
        cyl((TB_X + bx * (TB_W / 2 - 0.02), TB_Y + by * (TB_D / 2 - 0.02), TB_TOP + 0.004), 0.011, 0.01, "bolt",
            verts=6, bevel=0)
flat_plate((TB_X, TB_Y - TB_D / 2, 0.66), 0.24, 0.62, mat="dark_steel")       # the cover on its south face, under the glands
hazard_tag((TB_X - 0.07, TB_Y + 0.0, TB_TOP), 0.11, 0.08, face="T")          # the live-terminal tag, on the lid
# the bushing: two cream ceramic discs on the lid, wider than the brass clamp on them that grips the copper bar's
# end, so their pale rings show round it from the camera (the substation's insulators: pale says live terminal)
BU_X, BU_Y, BU_Z = 2.405, -1.02, 1.375                                   # the clamp's centre: the bar's end in it
for k_, (rd, hd) in enumerate(((0.058, 0.024), (0.05, 0.022))):
    cyl((BU_X, BU_Y, TB_TOP + 0.024 * k_ + hd / 2), rd, hd, "ceramic", verts=20, bevel=0.005)
box((BU_X + 0.015, BU_Y, BU_Z), (0.065, 0.06, 0.07), "brass", bevel=0.005)  # the clamp, the bar into it
cyl((BU_X + 0.015, BU_Y, BU_Z + 0.04), 0.012, 0.012, "bolt", verts=6, bevel=0)
# the bus's end: off the caps' line at 1.2, bent up just north of the box (clear of tube 0's fins, 0.075 north) and
# over its lid's edge into the clamp, two quarter bends of radius 0.06 (a pipe run through evenly spaced points)
BEND = [(2.44, -0.81, 1.2)]
BEND += [(2.44, -0.86 - 0.06 * math.sin(a), 1.26 - 0.06 * math.cos(a)) for a in (PI / 2 * k / 6 for k in range(7))]
BEND += [(2.44, -0.92, 1.29)]
BEND += [(2.44, -0.98 + 0.06 * math.cos(b), 1.315 + 0.06 * math.sin(b)) for b in (PI / 2 * k / 6 for k in range(7))]
BEND += [(2.44, BU_Y - 0.01, BU_Z)]
pipe(BEND, r=0.03, mat="copper", flanges=False)
# the glands high on the box's south face, on the tray's line, west to east black, grey, red (each cable's place in
# the bundle where it starts in the tray), each cable straight out of its gland south into the tray
GL_Z, GL_FACE = 1.24, TB_Y - TB_D / 2
FAN = []
for gx, c_ in ((2.21, "black"), (2.37, "red"), (2.29, "grey")):          # in the tray's cols order
    gland(Vector((gx, GL_FACE, GL_Z)), Vector((0, 1, 0)), 0.026)        # a size up, so the brass shows round the cable
    FAN.append(((gx, GL_FACE, GL_Z), (0, -1, 0), 0.075))                # out clear of the gland's cap, then into the tray
TRAY_Z = GL_Z - 0.07                                                    # the cables drop 0.01 off the glands into it
# 0.26 wide (T08i's trays 0.2), so the three glands' spread lies inside its rails and the outer cables never cross
# one (collide: the black one from the west gland crossed a 0.2 tray's rail); the bundle starts 0.02 in, short of
# the first cleat; off its open south end over the switchgear's north edge into T08d's gland on its top
tray([(2.3, -1.30, TRAY_Z), (2.3, -1.56, TRAY_Z)], w=0.26, fan_in=FAN, fan_len=0.02,
     lead_out=[(2.29, -1.62, 1.235), (2.265, -1.68, 1.22), (2.245, -1.72, 1.19), (2.24, -1.74, 1.15)])
box((2.3, -1.43, (TRAY_Z - 0.0125) / 2), (0.05, 0.05, TRAY_Z - 0.0125), "ochre", bevel=0.004)  # the tray's stand
box((2.3, -1.43, 0.015), (0.13, 0.13, 0.03), "dark_steel", bevel=0.004)
cabinet(1.8, -1.9, 0.4, 0.6, 1.0, mat="grey")
cabinet(2.22, -1.9, 0.42, 0.6, 1.15, mat="green")
gauge((2.22, -2.21, 0.8), (0, -1, 0.15), r=0.06, live=lambda t: 0.2 * math.sin(2 * PI * t), layer="gauge-switchgear")
id_panel((1.8, -2.21, 0.6), 0.22, 0.12, stripe="red")

# the rotary converter along the south, its commutator at the east (DC) end
# T08d: the brush leads from the terminal box on the rocker over into a gland on the switchgear's top (round 7's
# rose from the rocker and stopped in the air over the commutator)
cv = converter(-1.75, 1.2, -1.95, 0.6, R=0.4, dc_east=True,
               leads=lambda c: [(c - 0.06, -1.47, 0.78), (c - 0.06, -1.48, 0.9), (c + 0.15, -1.56, 1.08),
                                (1.45, -1.75, 1.17), (1.66, -1.86, 1.08), (1.68, -1.87, 1.0)])
# T08d: the switchgear's leads to the brush gear end in glands, on the cabinet's top (the face the camera sees;
# its north face is hidden, and a lead going in there reads as running into its side) and on a terminal
# box on the brush rocker (round 7's ran into the cabinet's side with no fitting and stopped in the air over
# the rocker)
CXM = cv["com"][0]
box((CXM + 0.02, -1.47, 0.72), (0.32, 0.12, 0.12), "dark_steel", bevel=0.008)    # the brush gear's terminal box
bundle([(1.8, -1.7, 1.0), (1.79, -1.67, 1.08), (1.66, -1.5, 1.09), (1.45, -1.42, 1.0), (CXM + 0.14, -1.44, 0.95),
        (CXM + 0.1, -1.47, 0.88), (CXM + 0.1, -1.47, 0.78)],
       cols=("red", "black", "red"), r=0.025, glands=(True, True))

# the transformer, SW, and the trunks out
# T08d: the two trunks out leave the tank's south face low, each through a gap in its fins with its gland on
# the face (round 7's ran down through the fins from inside the tank, no gland where they left it)
tf = transformer(-2.15, -1.92, 0.58, 0.8, 0.8, mat="cream", fin_gaps=(-2.288, -2.012))
trunk([cv["ac_top"], (-1.2, -1.6, 1.2), (-1.9, -1.75, 1.25), tf], r=0.05)
trunk([(-2.288, -2.32, 0.46), (-2.29, -2.44, 0.38), (-2.31, -2.47, 0.2), (-2.33, -2.47, 0.04)], r=0.065)
trunk([(-2.012, -2.32, 0.46), (-2.01, -2.44, 0.38), (-1.98, -2.47, 0.2), (-1.95, -2.47, 0.04)], r=0.065)

# coolant for the crucible jacket and the tube caps: pump, hoses to the radiator housing
pv = motor(-0.6, 2.2, 0.35, d=(1, 0), s=0.8)
coupling(pv[0] + 0.05, pv[1], pv[2], 0.1, axis=(1, 0, 0), turns=2, layer="coupling-pump")
cyl((pv[0] + 0.25, pv[1], 0.35), 0.17, 0.25, "oxide", rot=(0, PI / 2, 0), verts=32)
hose([(pv[0] + 0.25, 2.2, 0.55), (0.0, 2.3, 0.9), (0.4, 2.1, 1.2)], r=0.07, mat="hose")
# FIX 13: the lagged line's middle 0.05-0.08 south, off the radiator's face (round 7's ran through its ribs)
lagged([(0.42, 1.45, 0.3), (0.3, 1.45, 0.5), (0.2, 1.47, 0.95), (0.25, 1.58, 1.3)], r=0.07)

# clutter: gas bottles NW, valves, barrels, a ladder, stains
for k, (x, y) in enumerate(((-2.25, 2.25), (-2.0, 2.3), (-2.32, 1.95))):
    cyl((x, y, 0.3), 0.11, 0.6, ("green", "grey", "hazard")[k], verts=24)
    head(x, y, 0.6, 0.11, 0.06, "dark_steel")
valve(-1.0, 2.3, 0.0, 0.5, wheel="red")
# T08d: the junction box stands beside the tray, not across it (round 7's tray ran through it), its lead into a
# gland on the crucible's south face (round 7's stopped short in the air); the tray 0.12 higher, on stands, over
# the barrels' lids (round 7's floor cut through them), its cables up from a gland in the deck at the west end
# and down into another at the east, past the commutator (round 7's ended loose at both ends of the tray)
jbox(0.0, -0.97, w=0.28, mat="grey", z=0.1)
bundle([(0.0, -0.97, 0.5), (0.03, -0.96, 0.6), (0.3, -0.92, 0.62), (0.53, -0.86, 0.52), (0.55, -0.8, 0.5)],
       cols=("black", "yellow"), glands=(True, True))
ladder(0.42, 0.0, 0.1, 1.05, axis="y", mat="ochre")
tray([(-0.45, -1.22, 0.44), (0.95, -1.22, 0.44), (1.35, -1.4, 0.44)], w=0.2, cols=("black", "red", "black"),
     lead_in=[(-0.66, -1.28, 0.13), (-0.64, -1.26, 0.3), (-0.55, -1.23, 0.46)],
     lead_out=[(1.45, -1.45, 0.47), (1.5, -1.5, 0.3), (1.5, -1.5, 0.1)], legs=(-0.2, 0.3, 1.15))
# FIX 12: the barrels 0.03 and 0.05 west, the second out of the cable tray's bend (round 7's crossed its rail)
for k, (x, y) in enumerate(((0.59, -1.3), (0.80, -1.36))):
    cyl((x, y, 0.22), 0.1, 0.32, ("oxide", "grey")[k], verts=20)
    torus((x, y, 0.3), 0.102, 0.01, "bare", seg=20)
stain(0.2, -1.2, 0.5, 0.12)
stain(-2.0, 0.9, 0.2, 0.3)
stain(1.6, -2.35, 0.4, 0.1)

MACHINE = [o for o in K.OBJS if K.GROUP[o.name] == "machine"]

# ---------------------------------------------------------------- the wreck (remnants)
import wreck  # noqa: E402   builds into K.OBJS in the "wreck" group
WRECK = [o for o in K.OBJS if K.GROUP[o.name] == "wreck"]

# ---------------------------------------------------------------- groups
WINDOW_MATS = set(K.LIQUIDS) | {"tube_glass", "pane"}


def group_of(o):
    """window (the liquids and the glass over them), a moving layer, the plate, or the wreck."""
    if K.GROUP[o.name] == "wreck":
        return "wreck"
    names = {m.name for m in o.data.materials if m} if getattr(o.data, "materials", None) else set()
    lay = K.layer_of(o)
    if lay:
        return RENDER_AS.get(lay, lay)
    if names & WINDOW_MATS:
        return "window"
    return "plate"


PART = {o.name: group_of(o) for o in K.OBJS}
assert not [o.name for o in MACHINE if PART[o.name] == "window" and K.layer_of(o)], "a window on a moving part"


def members(*groups):
    return [o for o in K.OBJS if PART[o.name] in groups]


SHOW = {}


def pose(f):
    """Frame f of the 32-frame loop: every moving part, and which cells are shown (the
    carousel's pockets and the hoists' loads hide and show; SHOW keeps what the pose said)."""
    for o in MACHINE:
        o.hide_render = False
    K.pose((f % NF) / NF, True)
    for o in MACHINE:
        SHOW[o.name] = not o.hide_render


def setup(visible=(), catchers=(), holdouts=(), ground=False, camera=True):
    """Per pass: the groups the camera sees, those that catch the visible parts' shadows (and
    stand in front of them as a holdout would), and those cut out."""
    for o in K.OBJS:
        g = PART[o.name]
        shown = (g in visible or g in catchers or g in holdouts) and SHOW.get(o.name, True)
        o.hide_render = not shown
        o.is_shadow_catcher = g in catchers
        o.is_holdout = g in holdouts
        o.visible_camera = camera
    GROUND.hide_render = not ground
    BOUNCE.hide_render = ground


def check_layers():
    """Every part whose place or visibility changes over the loop is in a moving layer."""
    m0, moved = {}, set()
    for f in range(NF):
        pose(f)
        bpy.context.view_layer.update()
        for o in MACHINE:
            st = (tuple(tuple(r) for r in o.matrix_world), SHOW[o.name])
            if o.name not in m0:
                m0[o.name] = st
            elif any(abs(a - b) > 1e-6 for ra, rb in zip(st[0], m0[o.name][0]) for a, b in zip(ra, rb)) \
                    or st[1] != m0[o.name][1]:
                moved.add(o.name)
    stray = sorted(n for n in moved if PART[n] not in LAYERS)
    if stray:
        sys.exit(f"parts move but are in no layer: {stray[:10]}")
    still = [lay for lay in LAYERS if not any(PART[n] == lay for n in moved)]
    if still:
        sys.exit(f"layers that do not move: {still}")
    return moved


# ---------------------------------------------------------------- the finish carried by moving parts
def pin():
    """materials.layered() reads world position, so a part that moves would slide under its
    own wear. Each moving part's mesh (modifiers applied) gets its frame-0 world position as an
    attribute, P0, and its materials a copy that reads P0 where they read position: the finish
    rides with the part, and frame 0 renders as before."""
    pose(0)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    cache = {}
    for o in MACHINE:
        if PART[o.name] not in LAYERS or o.type != "MESH":
            continue
        ev = o.evaluated_get(dg)
        me = bpy.data.meshes.new_from_object(ev)
        mw = o.matrix_world.copy()
        o.modifiers.clear()
        o.data = me
        at = me.attributes.new("P0", "FLOAT_VECTOR", "POINT")
        for v, a in zip(me.vertices, at.data):
            a.vector = mw @ v.co
        for i, m in enumerate(me.materials):
            if m is None:
                continue
            if m.name not in cache:
                c = m.copy()
                c.name = m.name + "-pinned"
                t = c.node_tree
                geos = [nd for nd in t.nodes if nd.bl_idname == "ShaderNodeNewGeometry"]
                if geos:
                    attr = t.nodes.new("ShaderNodeAttribute")
                    attr.attribute_type = "GEOMETRY"
                    attr.attribute_name = "P0"
                    for nd in geos:
                        for lk in list(nd.outputs["Position"].links):
                            t.links.new(attr.outputs["Vector"], lk.to_socket)
                cache[m.name] = c
            me.materials[i] = cache[m.name]
    return len(cache)


# ---------------------------------------------------------------- the camera's windows
def window_of(objs, poses, pad=(0.3, 0.3, 1.1, 0.6), canvas=None):
    """The render border (sprite px x0, y0, x1, y1 from the canvas's top left) round objs over
    every pose, padded (left, down, right, up, tiles) for the shadows they cast (the sun throws
    them right and up the screen) or a glow's tail."""
    W_, H_ = canvas or K.CANVAS
    cam = K.sc.camera
    inv = cam.matrix_world.inverted()
    xs, ys = [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for ps in poses:
        ps()
        bpy.context.view_layer.update()
        for o in objs:
            if o.type != "MESH" or not SHOW.get(o.name, True):
                continue
            ev = o.evaluated_get(dg)
            for c in ev.bound_box:
                p_ = inv @ (ev.matrix_world @ Vector(c))
                xs.append(p_.x)
                ys.append(p_.y)
    ppt = K.rig.PX_PER_TILE
    x0 = max(0, int(W_ / 2 + (min(xs) - pad[0]) * ppt))
    x1 = min(W_, int(W_ / 2 + (max(xs) + pad[2]) * ppt) + 1)
    y0 = max(0, int(H_ / 2 - (max(ys) + pad[3]) * ppt))
    y1 = min(H_, int(H_ / 2 - (min(ys) - pad[1]) * ppt) + 1)
    return x0, y0, x1, y1


def border(win, canvas=None):
    W_, H_ = canvas or K.CANVAS
    x0, y0, x1, y1 = win
    K.sc.render.use_border = True
    K.sc.render.use_crop_to_border = False
    K.sc.render.border_min_x, K.sc.render.border_max_x = x0 / W_, x1 / W_
    K.sc.render.border_min_y, K.sc.render.border_max_y = 1 - y1 / H_, 1 - y0 / H_


def no_border():
    K.sc.render.use_border = False


def path(stem):
    return os.path.join(K.OUT, stem + ".png")


def render(stem):
    K.rig.render(path(stem))


def glow_floor(stem):
    """A glow render's black floor taken out: with the sun and sky off, the machine the light does
    not reach renders (1, 1, 1) at 1x -- the rig's film look -- and pack.py's bloom (gains 0.9 and
    0.6) lifted that to 3, over its GLOW_FLOOR of 2, so the glow layer added 3 levels of grey over
    its whole window and tipped rolled-off glints to white (measure.py's white_px 1, clipped_px 2 on
    the first full pack). Every pixel whose brightest channel is at or under 1/255 is made 0: the
    light itself is never that faint where it is seen."""
    import numpy as np
    img = bpy.data.images.load(path(stem))
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)
    dark = a[:, :, :3].max(axis=2) <= 1.5 / 255
    a[dark, :3] = 0.0
    img.pixels.foreach_set(a.ravel())
    img.filepath_raw = path(stem)
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


# ---------------------------------------------------------------- --ports: there are none
if PORTS:
    contract.declare(K.OUT, canvas=K.CANVAS, **DECL)
    print("ports: none declared (spec 5, 8: no fluid box, no facing port); nothing to render")
    print("done")
    sys.exit(0)

# ---------------------------------------------------------------- --collide
if COLLIDE:
    import collide
    # the lid apart from the crane here (RENDER_AS), so a contact between them is still a clash
    raw = {n: (K.layer_of(o) or g) if g in LAYERS else g for n, g, o in ((o.name, PART[o.name], o) for o in K.OBJS)}
    collide.check(K, MACHINE, raw, RAW_LAYERS, pose, NF, SHOW)
    print("done")
    sys.exit(0)

MOVED = check_layers()
# --no-pin and --layers a,b: a study only (round 7's finish, unpinned; just those layers' frames rendered)
PINNED = 0 if "--no-pin" in K.argv else pin()
ONLY_LAYERS = K.argv[K.argv.index("--layers") + 1].split(",") if "--layers" in K.argv else None

SUN = K.rig.sun(SUN_E)
SUN.data.color = (1.0, 0.94, 0.82)
K.sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.24      # round 7's
GROUND = K.rig.ground_catcher()
GROUND.parent = K.ROOT
BOUNCE = K.rig.bounce_ground()
MACHINE_GROUPS = ("plate", "window") + LAYERS

# ---------------------------------------------------------------- --icon
if ICON:
    # the whole machine working at frame 0 (the windows at radiant.py's working-plate light,
    # the lamps lit), on the plate's camera, framed to fill a 1024 px square
    K.sc.cycles.samples = 128
    cam = K.rig.camera(1024, 1024, ss=1)
    pose(0)
    K.pose_light(0.0, "plate")
    K.lamps(True)
    setup(visible=MACHINE_GROUPS)
    GROUND.hide_render = True
    for o in K.STAINS:
        o.hide_render = True
    bpy.context.view_layer.update()
    inv = cam.matrix_world.inverted()
    xs, ys = [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for o in MACHINE:
        if o.hide_render or o.type != "MESH":
            continue
        ev = o.evaluated_get(dg)
        for c in ev.bound_box:
            p_ = inv @ (ev.matrix_world @ Vector(c))
            xs.append(p_.x)
            ys.append(p_.y)
    span = max(max(xs) - min(xs), max(ys) - min(ys)) / 0.96
    cam.data.ortho_scale = span
    cam.data.shift_x = (max(xs) + min(xs)) / 2 / span
    cam.data.shift_y = (max(ys) + min(ys)) / 2 / span
    K.rig.render(os.path.join(K.OUT, "icon.png"))
    print(f"icon: {span:.2f} tiles across")
    print("done")
    sys.exit(0)

K.rig.camera(*K.CANVAS)

if "--pick" in K.argv:
    # which part the camera sees at sprite px x,y (a study aid): a ray from the camera through it
    pose(int(K.opt("--pick-frame", 0)))
    setup(visible=MACHINE_GROUPS)
    bpy.context.view_layer.update()
    cam = K.sc.camera
    for xy in K.argv[K.argv.index("--pick") + 1].split(";"):
        x, y = (float(v) for v in xy.split(","))
        W_, H_ = K.CANVAS
        span = cam.data.ortho_scale
        u, v = (x + 0.5 - W_ / 2) / max(W_, H_) * span, (H_ / 2 - y - 0.5) / max(W_, H_) * span
        m = cam.matrix_world
        o = m @ Vector((u, v, 0.0))
        d = (m.to_3x3() @ Vector((0, 0, -1))).normalized()
        dg = bpy.context.evaluated_depsgraph_get()
        for _ in range(6):                 # the first hits along the ray, nearest first
            hit, loc, nrm, idx, ob, _m = K.sc.ray_cast(dg, o, d)
            if not hit:
                break
            print("PICK", xy, ob.name, ob.data.materials[0].name if ob.data.materials else None, PART.get(ob.name),
                  tuple(round(c, 3) for c in (K.ROOT.matrix_world.inverted() @ loc)))
            o = loc + d * 1e-4
    sys.exit(0)

if "--debug-light" in K.argv:
    # the light's numbers at frame 0 in the glow pass, and one glow render of every window (not packed)
    pose(0)
    K.pose_light(0.0, "glow")
    for o in K.OBJS:
        if o.data.materials and o.data.materials[0] and o.data.materials[0].name in K.LIQUIDS:
            xs = [v.co for v in o.data.vertices]
            print("LIQUID", o.name, o.data.materials[0].name, [round(min(v[i] for v in xs), 3) for i in range(3)],
                  [round(max(v[i] for v in xs), 3) for i in range(3)], tuple(round(c, 3) for c in o.scale),
                  [m.type for m in o.modifiers])
    for name in K.LIQUIDS:
        b = K.M[name].node_tree.nodes["Principled BSDF"]
        users = [o.name for o in K.OBJS if o.data.materials and o.data.materials[0] == K.M[name]]
        print("LIGHT", name, round(b.inputs["Emission Strength"].default_value, 3), users,
              [(PART[u], K.sc.objects[u].hide_render) for u in users])
    K.sc.cycles.samples = 16
    K.glint(False)
    setup(visible=MACHINE_GROUPS)
    hide = K.argv[K.argv.index("--debug-hide") + 1].split(",") if "--debug-hide" in K.argv else []
    only = K.argv[K.argv.index("--debug-only") + 1].split(",") if "--debug-only" in K.argv else None
    for o in K.OBJS:
        nm = o.data.materials[0].name if o.data.materials and o.data.materials[0] else ""
        if nm in hide or (only and nm not in only):
            o.hide_render = True
    with K.R.glow_pass(hide=(GROUND, BOUNCE)):
        render("debug-glow")
    print("done")
    sys.exit(0)

def sprite_px(p):
    """A model point (tiles, as modelled) to sprite px from the entity origin (x right, y down, 1x)."""
    cam = K.sc.camera
    q = cam.matrix_world.inverted() @ (K.ROOT.matrix_world @ Vector(p))
    return q.x * K.rig.PX_PER_TILE, -q.y * K.rig.PX_PER_TILE


if "--study" in K.argv:
    # T08c, a study only (nothing here is packed): at each frame given, the whole machine working
    # (look-NN: windows at the working plate's light, lamps lit, on the ground catcher, as round 7's
    # working-NN renders were) and stopped (unlit-NN: the still's settings, the idle the engine will
    # draw); at each --glowframes frame (default 20), the well's light alone and the other three
    # openings' alone (wellglow-NN, otherglow-NN) for the tight / wide bloom; the openings' and the fix regions' places on the
    # screen (SPOT and REGION lines), for the light definitions and the crops
    fr_list = [int(v) for v in K.argv[K.argv.index("--study") + 1].split(",") if v]
    glow_frames = [int(v) for v in str(K.opt("--glowframes", "20")).split(",") if v]
    K.sc.cycles.samples = ANIM_SAMPLES
    for f in fr_list:
        pose(f)
        K.pose_light(f / NF, "plate")
        K.lamps(True)
        K.glint(True)
        setup(visible=MACHINE_GROUPS, ground=True)
        render(f"look-{f:02d}")
        K.pose_light(f / NF, "idle")
        K.lamps(False)
        setup(visible=MACHINE_GROUPS)
        render(f"unlit-{f:02d}")
    K.glint(False)
    K.lamps(False)
    for f in glow_frames:
        pose(f)
        for stem, shapes in ((f"wellglow-{f:02d}", ("surface",)), (f"otherglow-{f:02d}", ("disc", "slot", "tube"))):
            K.pose_light(f / NF, "glow", shapes)
            setup(visible=MACHINE_GROUPS)
            with K.R.glow_pass(hide=(GROUND, BOUNCE)):
                render(stem)
            glow_floor(stem)
    K.glint(True)
    pose(0)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    inv_root = K.ROOT.matrix_world.inverted()
    for name, (shape, _c) in K.LIQUIDS.items():
        pts = []
        for o in K.OBJS:
            if o.data and getattr(o.data, "materials", None) and o.data.materials and \
                    o.data.materials[0] and o.data.materials[0].name == name:
                ev = o.evaluated_get(dg)
                pts += [inv_root @ (ev.matrix_world @ Vector(c)) for c in ev.bound_box]
        if not pts:
            continue
        sp = [sprite_px(p) for p in pts]
        xs, ys = [s[0] for s in sp], [s[1] for s in sp]
        mid = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
        print("SPOT", name, shape, "model", [round(v, 3) for v in mid],
              "px", round((min(xs) + max(xs)) / 2, 1), round((min(ys) + max(ys)) / 2, 1),
              "w", round(max(xs) - min(xs), 1), "h", round(max(ys) - min(ys), 1))
    for tag, p in (("hood", (-2.05, -0.05, 0.95)), ("hub", (-1.05, 0.45, 1.1)), ("pick", (-0.225, 0.45, 0.9)),
                   ("pinion", (-1.61, 1.87, 0.75)), ("roof", (0.8, 1.78, 1.8)), ("well", (1.25, 0.45, 1.2)),
                   ("hinge", (1.48, 0.45, 1.3)), ("commutator", (1.055, -1.95, 0.6)), ("ladder", (2.15, 1.63, 0.7)),
                   ("barrels", (0.7, -1.33, 0.3)), ("lagged", (0.3, 1.5, 0.8)), ("bin", (-2.28, -0.3, 0.6))):
        x, y = sprite_px(p)
        print("REGION", tag, round(x, 1), round(y, 1))
    print("done")
    sys.exit(0)

if ONLY_LAYERS:
    K.sc.cycles.samples = ANIM_SAMPLES
    K.lamps(False)
    K.pose_light(0.0, "idle")
    for name in ONLY_LAYERS:
        win = window_of(members(name), [lambda f=f: pose(f) for f in range(NF)])
        border(win)
        others = tuple(g for g in MACHINE_GROUPS if g != name)
        for f in range(NF):
            pose(f)
            setup(visible=(name,), catchers=others)
            render(contract.frame(name, f))
        no_border()
    print("done")
    sys.exit(0)

if not WRECK_ONLY:
    # ------------------------------------------------------------ the plate, the still, the shadow
    K.sc.cycles.samples = PLATE_SAMPLES
    pose(0)
    K.pose_light(0.0, "idle")
    K.lamps(False)
    K.glint(True)
    # the plate: everything that does not move, the openings dark; the moving parts out of the
    # scene, so their shadows are their own layers'
    setup(visible=("plate", "window"))
    render("idle")
    # the still: the whole machine at frame 0, stopped (the reference for the frame-0 check)
    setup(visible=MACHINE_GROUPS)
    render("still")
    if IDLE:
        # the quick look: frame 0 working, the windows lit, in one render (not packed)
        K.pose_light(0.0, "plate")
        K.lamps(True)
        render("working-look")
        K.pose_light(0.0, "idle")
        K.lamps(False)
        print("done")
        sys.exit(0)
    contract.declare(K.OUT, canvas=K.CANVAS, **DECL)
    # the shadow: the whole machine at frame 0 on the ground catcher, seen by nothing else
    setup(visible=MACHINE_GROUPS, ground=True, camera=False)
    render("shadow")
    # the status lamps' lenses, lit white, everything else held out
    setup(visible=("plate",), holdouts=("window",) + LAYERS)
    for o in members("plate"):
        o.is_holdout = not (o.data.materials and o.data.materials[0] and o.data.materials[0].name == "lamp")
    K.lamp_cut(True)
    render("lamp")
    K.lamp_cut(False)

    # ------------------------------------------------------------ the moving layers
    K.sc.cycles.samples = ANIM_SAMPLES
    WINDOWS = {}
    for name in LAYERS:
        objs = members(name)
        win = window_of(objs, [lambda f=f: pose(f) for f in range(NF)])
        WINDOWS[name] = win
        border(win)
        others = tuple(g for g in MACHINE_GROUPS if g != name)
        for f in range(NF):
            pose(f)
            setup(visible=(name,), catchers=others)
            render(contract.frame(name, f))
        no_border()

    # ------------------------------------------------------------ the windows and their glow
    wobjs = members("window")
    win = window_of(wobjs, [lambda: pose(0)], pad=(0.1, 0.1, 0.1, 0.1))
    WINDOWS["window"] = win
    border(win)
    for f in range(NF):
        pose(f)
        K.pose_light(f / NF, "plate")
        setup(visible=("window",), holdouts=("plate",) + LAYERS)
        render(contract.frame("window", f))
    no_border()
    K.glint(False)
    for name, shapes in GLOWS:
        lit = [o for o in wobjs if o.data.materials[0].name in K.LIQUIDS
               and K.LIQUIDS[o.data.materials[0].name][0] in shapes]
        win = window_of(lit, [lambda: pose(0)], pad=(1.2, 1.2, 1.2, 1.2))
        WINDOWS[name] = win
        border(win)
        for f in range(NF):
            pose(f)
            K.pose_light(f / NF, "glow", shapes)
            setup(visible=MACHINE_GROUPS)
            with K.R.glow_pass(hide=(GROUND, BOUNCE)):
                render(contract.frame(name, f))
            glow_floor(contract.frame(name, f))
        no_border()
    K.glint(True)
    K.pose_light(0.0, "idle")
    pose(0)
else:
    contract.declare(K.OUT, canvas=K.CANVAS, **DECL)
    WINDOWS = {}

# ---------------------------------------------------------------- the wreck
# on its own canvas over the ground catcher: its shadow and scorch caught in the same picture,
# as vanilla's remnants carry theirs (pack.py); the machine gone
wreck.soot()
K.sc.cycles.samples = PLATE_SAMPLES
K.rig.camera(*WRECK_CANVAS)
no_border()
setup(visible=("wreck",), ground=True)
# the wreck with its light out (the well's mouth dark), then again with the dying blue on, the same
# camera, catcher and seed: pack.py takes the one from the other for the glow layer (T08d), so by day
# wreck + glow is T08c's picture, and at night the glow alone shows
wreck.dying(0.0)
render("wreck")
wreck.dying(wreck.DYING_STRENGTH)
render("wreck-lit")

with open(os.path.join(K.OUT, "model.json"), "w") as f_:
    json.dump(dict(windows=WINDOWS, frames=NF, animation_speed=SPEED, samples=dict(plate=PLATE_SAMPLES,
                   anim=ANIM_SAMPLES), sun=SUN_E, groups={g: len(members(g)) for g in MACHINE_GROUPS + ("wreck",)},
                   pinned_materials=PINNED, moving_parts=len(MOVED)), f_, indent=1)
print("done")
