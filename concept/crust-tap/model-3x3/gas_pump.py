"""Gas Pump 3x3 (sae-gas-pump): the Flywheel Compressor -- the shipping model (gas-pump-3x3 T08).

  BLENDER=<blender 5> tools/blender/render.sh concept/crust-tap/model-3x3/gas_pump.py <out-dir> --ports --icon \
      [--collide [--collide-allow <pattern> ...]]
  (or directly: blender -b --python gas_pump.py -- <out-dir> [--idle | --ports | --icon | --collide | --tints]
                [--samples N] [--anim-samples N] [--only north,east])

  --idle     the plate and the still per direction only: the quick loop for the finish
  --only D,D render only these directions (tuning; never for a pack: pack.py wants all four)
  --ports    the four pipe pictures and their caps, port-<face>.png and cover-<face>.png (the Vent Pump
             model's, in assembler 3's outline: the same nozzle, the same kit)
  --icon     icon.png: the machine facing north on the house camera, working, the flywheel's yellow weight
             up where a 32 px icon shows it, siderane in the glass
  --collide  no render: every moving part in every frame against every other part, and every fixed part
             against every other, by BVH (the whole machine turns, so north answers for all four);
             collide.txt and collide-model.txt in <out-dir>
  --tints    no pack: the glass layer rendered in each gas's own paint (siderane #A8D929, helium-3 #B6A6C8),
             north, frames 0 and 12, for the review's check that the engine's tint of the white layer matches

Spec: concept/crust-tap/building-spec-crust-tap.md (written 7bed91d): the Flywheel Compressor, take 2 of the
3x3 round, refined (T04, ba32d3d) and signed off as the concept by Liam on 2026-10-21. The geometry and the
surfacing are the concept's (options/round-3x3-refine/gp_2_flywheel_compressor.py, built with its kit, copied
into kit/; each kit file's first line says what the copy changed), copied here verbatim between the marks
below. Changed from the concept, each from Liam:

  - the lubricator (T05: "Add a lubricator"; spec 3.2, "Artist places it"): a red-oxide force-feed lubricator
    on its own pedestal and footing east of the flywheel, its ratchet lever worked by a short rod off a crank
    pin on the flywheel hub, so it rocks once a turn; two copper oil lines from its back, one to the east
    compressor cylinder's crank-end flange, one to the crankcase;
  - helium-3 #B6A6C8 (T05): the glass layer is rendered white and the engine tints it with the vent's
    mining_visualisation_tint (spec A.5: siderane #A8D929, helium-3 #B6A6C8), as the 2x2 Gas Pump's glass;
  - four drawings, the whole machine turned (T03: "Whole machine turns"; spec 5): the root turned a quarter a
    direction, camera and sun fixed; the outlet at {0, -1} facing north;
  - one flywheel turn a second (spec A.7, "One turn a second"): 24 frames a turn at animation_speed 0.4
    (a drill's animation progress is 1: the 2x2 pump measured 0.4 frames a tick in game).
  - the outlet's fitting (Liam's standing rule, 2026-10-21: a connection enters through a fitting set into the
    wall or casing, never a stub standing off the machine): a pad welded on the discharge bottle, a flanged sleeve to
    the north edge, the bore open; per direction, so facing east or west it lines up with the engine's pipe
    (OUTLET_FITTING below), the bottle's nearest band and saddle moved off the pad; the pipe pictures are a mating
    flange and a short spool (fitting()), and the wiring draws vanilla's covers.
  - T13b (Liam, 2026-10-27, Q20.2/3 "Accept"): facing north the fitting is not drawn past the north edge line, so
    vanilla's north cover shows (NORTH_CUT; port-N is rendered for pack_ports but the north picture ships empty), and
    the west picture carries the plate's outer flange and sleeve over the flange's shadow band (west_seam()).

And three changes not from Liam, put to him with the T08 report: the footings' seams closed (--seams; the note at
CLOSED below), for the coverage bar; the sun a step down, 10 -> 9.85 (--sun), for the tonal bar facing south; the
glass layer's neutral at 0.65 (--gas-white), so the drift is not driven flat white (T08b replaced it: the note at
GAS_WHITE). Nothing else of the concept moved.

The layers (contract.py):
  idle (plate, "base")   the machine stopped, no moving part drawn, the glass empty (dark). The moving parts
                         stand at frame 0 unseen by the camera, so their shadows fall on the plate as they do
                         in the still
  still                  the plate with every moving part at frame 0 (the frame-0 check)
  shadow                 the catcher alone
  mech (24 frames)       every moving part -- the flywheel, the crossheads and their two rods each, the
                         rockers, the gauge needles, the lubricator's crank, rod and lever -- the rest held out;
                         drawn always, so idle it stops where it is, as the pumpjack's head does
  glass (24, light)      the gas drifting in the sight glass, white, the rest held out and the pane hidden; the
                         engine tints it and draws it only while working
The gas is paint, never light: nothing on this building glows (spec 3.3).

Units are tiles; north is +Y. Nothing here is adopted: the sheets move to graphics/ only on Liam's sign-off.
"""
import json
import math
import os
import random
import re
import sys

import bpy
from mathutils import Matrix, Vector

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "kit"))
from gp_kit import *  # noqa: F401,F403,E402
import gp_kit as GP  # noqa: E402
import vpb5_kit as K5  # noqa: E402
import vpb3_kit as K  # noqa: E402
import contract  # noqa: E402  (tools/blender, on the path from vpb3_kit)
import rig  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0]
IDLE = "--idle" in argv
PORTS = "--ports" in argv
ICON = "--icon" in argv
COLLIDE = "--collide" in argv
TINTS = "--tints" in argv


def _opt(name, default):
    return type(default)(argv[argv.index(name) + 1]) if name in argv else default


TAU = 2 * PI
SPEED = 0.4                         # spec A.7: one turn a second, 24 frames over 60 ticks
CANVAS = (416, 416)                 # the origin at its centre
PORT_CANVAS = (320, 320)
PLATE_SAMPLES = _opt("--samples", 80)          # the kit's
ANIM_SAMPLES = _opt("--anim-samples", 80)
DIRS = ("north", "east", "south", "west")
TURN = {"north": 0.0, "east": -PI / 2, "south": PI, "west": PI / 2}
ONLY = tuple(_opt("--only", ",".join(DIRS)).split(","))
assert all(d in DIRS for d in ONLY), ONLY
SIDERANE_HEX, HELIUM_HEX = "#A8D929", "#B6A6C8"     # spec 3.3 and A.5: the vents' mining_visualisation_tint

DECL = dict(
    footprint=(3, 3),
    directions="four",              # the whole machine turned, the root a quarter a direction
    passes=[
        dict(name="idle", kind="plate", sheet="base"),
        dict(name="still", kind="still"),
        dict(name="shadow", kind="shadow", sheet="shadow"),
    ],
    animations=[
        dict(name="mech", frames=24, motion="cycle", animation_speed=SPEED),
        dict(name="glass", frames=24, motion="flow", kind="light", animation_speed=SPEED),
    ],
    # one picture per face, on the middle tile of each: facing north the gas leaves by the north face
    # (spec 8 and 24: {0, -1}), and turned, the same pictures serve every face it reaches
    ports=[dict(tile=(0, -1), face="N"), dict(tile=(1, 0), face="E"),
           dict(tile=(0, 1), face="S"), dict(tile=(-1, 0), face="W")],
)

# ---------------------------------------------------------------- T08: the footings' seams (the one change not from Liam)
# The concept stands on nine footings with seams of ground 0.02-0.08 tile between them. Two things measure.py found on
# the model: facing west, the seam between the discharge bottle's footing and the wellhead's crosses the outlet's axis
# 56 px in and cuts the bottle off from the machine (join west: 41 of 41 gap columns); and the seams are ground inside
# the footprint (coverage 91.1-91.9 % in three directions, under the 92 % bar; the concept's 92.9 % was packed by
# gp_pack.py, which dilates the working frames a px). "--seams closed" (the default) pours each footing against its
# neighbour: the same blocks, at their own heights, meeting; "--seams open" builds the concept's exactly.
SEAMS = _opt("--seams", "closed")
assert SEAMS in ("closed", "open"), SEAMS
CLOSED = {                                   # the concept's footing -> the same footing, met (x0, y0, x1, y1)
    (-1.46, -1.1, -0.52, -0.38): (-1.46, -1.1, -0.5, -0.38),        # west compressor cylinder, to the crankcase's
    (0.52, -1.1, 1.46, -0.38): (0.5, -1.1, 1.46, -0.38),            # east compressor cylinder
    (-0.42, -0.18, 0.42, 0.6): (-0.42, -0.2, 0.42, 0.6),            # the wellhead, to the crankcase's
    (-1.42, 0.68, 0.62, 1.42): (-1.42, 0.6, 0.62, 1.42),            # the discharge bottle, to the wellhead's
    (-1.44, -0.34, -0.48, 0.62): (-1.44, -0.38, -0.5, 0.6),         # the gauge board, to the crankcase's line
    (0.48, -0.34, 1.44, 0.62): (0.5, -0.38, 1.44, 0.6),             # the sight glass run
    (0.68, 0.68, 1.42, 1.42): (0.62, 0.6, 1.42, 1.42),              # the lube tank and the panel
}
_foundation0 = foundation


def foundation(x0, y0, x1, y1, h, *a, **kw):  # noqa: F811
    if SEAMS == "closed":
        x0, y0, x1, y1 = CLOSED.get((x0, y0, x1, y1), (x0, y0, x1, y1))
    return _foundation0(x0, y0, x1, y1, h, *a, **kw)


# ---------------------------------------------------------------- T08: the outlet's fitting, OUTLET_FITTING (Liam, 2026-10-21, a standing rule)
# "Every pipe connection enters the building through a fitting set into its wall or casing, like the Reaction Plant
# casing's recessed fitting (a bolted boss, a welded sleeve, flanges) or anything similar, rather than a pipe stub
# standing off the machine; the pipe picture shows it open, and vanilla's cover is drawn when nothing is connected."
# The concept's outlet was a nozzle on its own foot with a bare stub from the bottle (OUTLET "stub", kept for the
# review's before). Here the bottle's shell is the casing: a reinforcing pad welded on it, cut to its curve and in
# its grey, a welded sleeve 1.18 x the bore out of the pad to the north edge with a bolted flange at each end (the
# Reaction Plant's sleeve(), sized to this bottle), the bore open at the edge. On the pipe axis ZA, as before.
#
# Per direction, as the Reaction Plant's fittings are: the engine draws a pipe on the next tile with its axis on the
# tile's middle row, and a fitting at height ZA shows ZA/2 = 0.21 tile (13 px) up the screen. Facing north or south
# that is along the pipe and does not matter; facing east or west it put the fitting 13 px above the pipe. So the
# east and west drawings carry the fitting 0.194 tile along the bottle (east +x, west -x as modelled: on the ground
# 1/64 - ZA/2 south of the tile's middle, the Vent Pump's and the Reaction Plant's H_AXIS_V), with the bottle's
# nearest band and saddle moved off the pad (VARIANTS); north and south carry it on the middle.
OUTLET = _opt("--outlet", "fitting")
assert OUTLET in ("fitting", "stub"), OUTLET
OUT_DX = round(ZA / 2 - 1 / 64, 4)            # 0.1944
OUT_FLANGE = 0.3                              # the sleeve's outer flange and the picture's mating one
ALL_DIRS = frozenset(("north", "east", "south", "west"))
# (directions, the fitting's x as modelled, the bottle's bands, its saddles)
VARIANTS = [(frozenset(("north", "south")), 0.0, (-0.85, -0.35, 0.29), (-0.9, 0.3)),
            (frozenset(("east",)), OUT_DX, (-0.85, -0.35, -0.1), (-0.9, -0.1)),
            (frozenset(("west",)), -OUT_DX, (-0.85, -0.55, 0.15), (-0.9, 0.2))]
VAR = {}                                      # object name -> the directions it is drawn in (absent: all four)


class variant:
    """Every part built inside is drawn only in these directions."""
    def __init__(self, dirs):
        self.dirs = frozenset(dirs)

    def __enter__(self):
        self.n0 = len(K.OBJS)

    def __exit__(self, *a):
        for o in K.OBJS[self.n0:]:
            VAR[o.name] = self.dirs


FIT_OBJS = {}                                 # T13b: each variant's fitting parts, by its directions


def outlet_fitting(rn=0.17):
    for dirs, x, _, _ in VARIANTS:
        with variant(dirs):
            n0 = len(K.OBJS)
            _outlet_fitting(x, rn)
            FIT_OBJS[dirs] = list(K.OBJS[n0:])


def _outlet_fitting(x0, rn):
    DY_, DZ_, DR_ = 0.98, 0.52, 0.24                       # the discharge bottle's axis and radius (the concept's)
    ax = (PI / 2, 0, 0)
    y_shell = DY_ + math.sqrt(DR_ ** 2 - (ZA - DZ_) ** 2)  # the shell's north face on the pipe's axis
    y_pad = DY_ + math.sqrt((DR_ + 0.035) ** 2 - (ZA - DZ_) ** 2)
    # the pad: a cylinder along the outlet, intersected with the shell grown 0.035, so it hugs the bottle's curve
    pad = cyl((x0, (DY_ + y_pad + 0.05) / 2, ZA), rn * 1.2, y_pad + 0.05 - DY_, "grey", rot=ax, verts=48, bevel=0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=DR_ + 0.035, depth=0.8, location=(0, DY_, DZ_),
                                        rotation=(0, PI / 2, 0))
    cutter = bpy.context.active_object
    cutter.parent = ROOT_
    mod = pad.modifiers.new("pad", "BOOLEAN")
    mod.operation, mod.object, mod.solver = "INTERSECT", cutter, "EXACT"
    bpy.context.view_layer.objects.active = pad
    bpy.ops.object.modifier_apply(modifier="pad")
    bpy.data.objects.remove(cutter)
    pad.name = "outlet pad"
    yo = EDGE - 0.004                                       # the sleeve's outer face, at the footprint's edge
    cyl((x0, (y_shell + yo) / 2, ZA), rn * 1.18, yo - y_shell, "bare", rot=ax, verts=48, bevel=0.006)    # the sleeve
    # the inner flange at the pad; the outer one at the edge as wide as the vanilla pipe's body (its 41 px across the
    # screen facing east or west: measure.py's join counted the rows past a narrower flange as ground)
    for yf, out, rf in ((y_pad + 0.016, 1, rn * 1.45), (yo - 0.018, 1, OUT_FLANGE)):
        cyl((x0, yf, ZA), rf, 0.036, "dark_steel", rot=ax, verts=40, bevel=0.004)                       # a flange
        for i in range(8):
            a = 2 * PI * (i + 0.25) / 8
            cyl((x0 + (rf - 0.025) * math.cos(a), yf + out * 0.022, ZA + (rf - 0.025) * math.sin(a)), 0.018, 0.012, "bare",
                rot=ax, verts=6, bevel=0)                                                             # its nuts
    torus((x0, y_pad + 0.04, ZA), rn * 1.18 + 0.003, 0.01, "seam", rot=ax, seg=40)                       # the weld
    cyl((x0, yo + 0.001, ZA), rn * 0.96, 0.004, "dark", rot=ax, verts=40, bevel=0)                       # the bore, open


ROOT_ = K.ROOT
_drum_ew0 = drum_ew


def drum_ew(x0, x1, y, z, r, *a, **kw):  # noqa: F811
    """The discharge bottle: with the outlet's fitting, built once a variant, its bands and saddles off the pad's rim
    (the concept's (-0.85, -0.35, 0.15) and (-0.9, 0.2): a band ran through the pad, a saddle 0.063 into it)."""
    if OUTLET != "fitting" or kw.get("saddles") != (-0.9, 0.2):
        return _drum_ew0(x0, x1, y, z, r, *a, **kw)
    for dirs, _, bands, saddles in VARIANTS:
        with variant(dirs):
            _drum_ew0(x0, x1, y, z, r, *a, **dict(kw, bands=bands, saddles=saddles))

# every run's course as well as its ends (the kit's ends() keeps only the ends), for the clipping crops
RUN_PTS = {}
_ends0 = K.ends


def _ends(name, P, n0):
    RUN_PTS[len(K.PIPES)] = [tuple(p) for p in P[::3]] + [tuple(P[-1])]
    return _ends0(name, P, n0)


K.ends = _ends

# ================================================================ the concept, verbatim (gp_2_flywheel_compressor.py 49-241)
K5.build_materials5(((0.45, 0.3), (1.5, 0.4)))
NF = 24
CY = -0.76                 # the compressor line (E-W) and the crankcase's middle
CZ = 0.58                  # the compressor cylinders' axis
STROKE = 0.15              # each crosshead's travel either side of mid (T04: was 0.13)


def xh(t, on):
    """A crosshead's offset outward from mid: the crank one turn a loop."""
    return STROKE * math.cos(2 * PI * (t if on else 0.0))


def delivery(t):
    """1 while the cylinders deliver (the crossheads moving out), eased."""
    return max(0.0, math.sin(2 * PI * t)) ** 0.7


# ---------------------------------------------------------------- footings
foundation(-0.5, -1.46, 0.5, -0.2, 0.14)                           # the crankcase and flywheel
foundation(-1.46, -1.1, -0.52, -0.38, 0.12)                        # west compressor cylinder
foundation(0.52, -1.1, 1.46, -0.38, 0.12)                          # east compressor cylinder
foundation(-0.42, -0.18, 0.42, 0.6, 0.22, "refractory")            # the wellhead and scrubber over the vent
vent_collar(0, 0.12, 0.28, h=0.3)
foundation(-1.42, 0.68, 0.62, 1.42, 0.1)                           # the discharge bottle
foundation(-1.44, -0.34, -0.48, 0.62, 0.08)                        # the gauge board
foundation(0.48, -0.34, 1.44, 0.62, 0.08)                          # the sight glass run
foundation(0.68, 0.68, 1.42, 1.42, 0.1)                            # the lube tank and the panel

# ---------------------------------------------------------------- 1-2. the wellhead, the suction scrubber
SX, SY = 0.0, 0.16
cyl((SX, SY, 0.36), 0.2, 0.16, "dark_steel", verts=32)
flange_ring(SX, SY, 0.28, 0.2, nb=10)
top = vtank(SX, SY, 0.32, 1.42, mat="green", bands=(0.62, 1.12), nozzle=None)
for z in (0.62, 1.12):
    rivet_ring(SX, SY, z, 0.355, 14)
manway_top(SX, SY, top - 0.02, r=0.1)
cyl((SX, SY - 0.33, 0.46), 0.05, 0.1, "bare", rot=(PI / 2, 0, 0), verts=12)            # the dump valve
handwheel((SX, SY - 0.42, 0.46), 0.07, axis=(0, -1, 0.2), mat="red")
cyl((0.32, -0.22, 0.12), 0.07, 0.2, "dark_steel", verts=16)                                   # the drain pot
hose([(SX, SY - 0.37, 0.4), (0.2, -0.22, 0.24), (0.32, -0.22, 0.2)], r=0.035, mat="hose_k",
     name="scrubber dump to the drain")
stencil((SX - 0.12, SY - 0.33, 0.95), (0.18, 0.012, 0.1))
id_panel((SX + 0.12, SY - 0.325, 0.78), 0.14, 0.09, stripe="yellow")
label(1, "vent under the wellhead", (SX, SY - 0.3, 0.32))
label(2, "suction scrubber over the vent: the liquid knocked out", (SX, SY - 0.2, 1.1))

# ---------------------------------------------------------------- the crankcase, the power cylinders, the flywheel
box((0, CY, 0.44), (0.62, 0.86, 0.6), "green", bevel=0.035)
box((0, CY, 0.76), (0.66, 0.9, 0.05), "dark_steel")
for yy in (CY - 0.2, CY + 0.2):
    cyl((0, yy, 1.0), 0.15, 0.44, "green", verts=32)
    for k in range(4):
        torus((0, yy, 0.86 + 0.08 * k), 0.155, 0.012, "dark_steel", seg=32)
    cyl((0, yy, 1.25), 0.17, 0.07, "dark_steel", verts=32)
    bolts(0, yy, 1.29, 0.14, 8, r=0.012)
    box((0, yy, 1.33), (0.1, 0.22, 0.06), "dark_steel", bevel=0.006)                   # the rocker stand
    rk = pivot((0, yy, 1.45))
    box((0, 0, 0), (0.05, 0.3, 0.04), "ochre", bevel=0.005, parent=rk)
    sphere((0, 0.15, 0), 0.025, "bare", parent=rk)
    sphere((0, -0.15, 0), 0.025, "bare", parent=rk)
    rock(rk, 0.40, cycles=1, axis="X", phase=0.0 if yy < CY else 0.5)
    cyl((0.12, yy, 1.12), 0.018, 0.12, "nickel", rot=(0, PI / 2, 0), verts=8)          # the spark plug
box((0.0, CY - 0.44, 0.45), (0.5, 0.03, 0.4), "dark_steel", bevel=0.006)              # the crankcase door
bolts(0, CY - 0.46, 0.45, 0.0, 1)
fy = -1.28
cyl((0, fy + 0.12, CZ + 0.1), 0.05, 0.36, "bare", rot=(PI / 2, 0, 0), verts=16)       # the crankshaft's end
fw = pivot((0, fy, CZ + 0.1), along((0, -1, 0)))
torus((0, 0, 0), 0.44, 0.06, "dark_steel", seg=56, parent=fw)
cyl((0, 0, 0), 0.08, 0.1, "bare", verts=20, parent=fw)
FW_WEB = os.environ.get("GP_FW_WEB", "green")                # T04 trial knob: the web and spokes' paint
FW_WEIGHT = os.environ.get("GP_FW_WEIGHT", "yellow")        # T04 trial knob: the balance weight's paint
cyl((0, 0, -0.012), 0.405, 0.02, FW_WEB, verts=56, bevel=0.003, parent=fw)       # T04: the web the spokes are cast in
for k in range(6):
    a = 2 * PI * k / 6
    box((0.22 * math.cos(a), 0.22 * math.sin(a), -0.004), (0.38, 0.05, 0.02), FW_WEB, rz=a, bevel=0.006, parent=fw)
# T04: the balance weight, bolted between two spokes: the one bold mark on the wheel (one pass a loop at any pixel)
sector((0, 0, 0.018), 0.15, 0.4, PI / 2 - 0.62, PI / 2 + 0.62, 0.035, FW_WEIGHT, seg=12, parent=fw)
for k in range(3):
    a = PI / 2 + (k - 1) * 0.42
    cyl((0.3 * math.cos(a), 0.3 * math.sin(a), 0.04), 0.016, 0.02, "bolt", verts=8, bevel=0, parent=fw)
spin(fw, 1)
label(3, "flywheel and crankshaft, one turn a stroke", (0, fy, CZ + 0.36))
label(4, "power cylinders on the vent's own gas: the rockers nod", (0, CY - 0.2, 1.4))

# ---------------------------------------------------------------- T08: the lubricator (Liam, T05: "Add a lubricator";
# spec 3.2: "driven off the flywheel hub by a short rod", "Artist places it"). East of the flywheel, on the free ground
# between the crankcase's footing and the east cylinder's discharge loop: a red-oxide force-feed lubricator on a
# pedestal, its ratchet lever hanging on its south face. A crank pin on the hub, opposite the yellow weight, drives
# the lever through a short rod, so the lever rocks once a turn, about +-40 degrees.
LX, LY = 0.76, -1.30                 # the lubricator's axis
LZ0, LZ1 = 0.54, 0.86                # its body
foundation(0.5, -1.47, 0.96, -1.1, 0.08) if SEAMS == "closed" else foundation(0.56, -1.47, 0.96, -1.13, 0.08)
cyl((LX, LY, 0.31), 0.045, 0.46, "dark_steel", verts=16)                                 # the pedestal
box((LX, LY, 0.525), (0.2, 0.14, 0.03), "dark_steel", bevel=0.006)                       # its head plate
box((LX, LY, (LZ0 + LZ1) / 2), (0.28, 0.16, LZ1 - LZ0), "oxide", bevel=0.02)             # the body (the reservoir)
box((LX, LY, LZ1 + 0.015), (0.3, 0.18, 0.03), "dark_steel", bevel=0.006)                 # the lid
cyl((0.84, LY + 0.02, LZ1 + 0.055), 0.035, 0.05, "brass", verts=16)                      # the filler cap
for k in range(2):                                                                       # the sight feeds
    cyl((0.79 + 0.055 * k, LY - 0.085, 0.79), 0.022, 0.02, "nickel", rot=(PI / 2, 0, 0), verts=16, bevel=0)
    sphere((0.79 + 0.055 * k, LY - 0.095, 0.79), 0.013, "dark", seg=10)
LVC = Vector((0.68, LY - 0.13, 0.80))   # the lever's pivot, on a stub axle out of the body's south face
LVA = 0.16                              # the lever, pivot to the rod's pin
cyl((LVC.x, (LY - 0.08 + LVC.y) / 2, LVC.z), 0.016, abs(LVC.y - (LY - 0.08)) + 0.01, "bare", rot=(PI / 2, 0, 0),
    verts=12, bevel=0)
lv = pivot(tuple(LVC))
cyl((0, 0, 0), 0.03, 0.025, "dark_steel", rot=(PI / 2, 0, 0), verts=16, bevel=0, parent=lv)    # the ratchet's hub
box((0, 0, -LVA / 2), (0.032, 0.02, LVA + 0.03), "bare", bevel=0.005, parent=lv)            # the lever
cyl((0, -0.025, -LVA), 0.015, 0.05, "bolt", rot=(PI / 2, 0, 0), verts=10, bevel=0, parent=lv)  # its pin
# the crank on the hub's face, opposite the weight; fw's local +Z points south, out of the wheel's face
CA = -PI / 2                            # the crank pin's angle on the wheel, the weight's + PI
CR = 0.11                               # its throw
cyl((0, 0, 0.075), 0.06, 0.05, "dark_steel", verts=20, bevel=0.004, parent=fw)                 # the crank's boss
box((CR / 2 * math.cos(CA), CR / 2 * math.sin(CA), 0.11), (CR + 0.06, 0.05, 0.025), "bare", rz=CA, bevel=0.006,
    parent=fw)                                                                                  # the crank arm
PIN_L = Vector((CR * math.cos(CA), CR * math.sin(CA), 0.16))                                    # the pin, local
cyl(tuple(PIN_L), 0.018, 0.08, "bolt", verts=10, bevel=0, parent=fw)
ROD_Y = -1.46                           # the rod's plane: its eyes on the two pins, in front of the lever and the crank


def lube_pin(t, on):
    """The crank pin in model tiles, after the flywheel's pose (fw is a child of ROOT: its basis is model space)."""
    p = fw.matrix_basis @ PIN_L.copy()
    return (p.x, ROD_Y, p.z)


def _lever_tip(th):
    return Vector((LVC.x - LVA * math.sin(th), LVC.y, LVC.z - LVA * math.cos(th)))


# the rod keeps the length it has from the lever hanging straight down to the hub's centre (set on the first pose)
ROD_L = [None]


def lever_angle(t, on):
    """The lever's angle for the pin where it is: the rod's two ends ROD_L apart, solved by bisection."""
    p = Vector(lube_pin(t, on))
    if ROD_L[0] is None:
        hub = fw.location
        ROD_L[0] = (_lever_tip(0.0) - Vector((hub.x, p.y, hub.z))).length
    lo, hi = -1.3, 1.3
    for _ in range(60):
        mid = (lo + hi) / 2
        q = _lever_tip(mid)
        if Vector((q.x - p.x, 0, q.z - p.z)).length > ROD_L[0]:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


_LV0 = lv.rotation_euler.copy()


def _lever(t, on):
    lv.rotation_euler = _LV0
    lv.rotation_euler.rotate_axis("Y", lever_angle(t, on))


K.ANIM.append(_lever)


def lever_pin(t, on):
    q = _lever_tip(lever_angle(t, on))
    return (q.x, ROD_Y, q.z)


link(lube_pin, lever_pin, r=0.017, mat="nickel", name="lubricator drive rod")
pipe([(0.84, LY + 0.02, 0.62), (0.86, -1.12, 0.66), (0.82, -1.05, 0.66), (0.80, -1.03, 0.64)], r=0.016, mat="copper",
     name="oil: the lubricator to the east cylinder")
pipe([(0.68, LY + 0.02, 0.6), (0.52, -1.16, 0.66), (0.38, -1.1, 0.67), (0.29, -1.08, 0.67)], r=0.016, mat="copper",
     name="oil: the lubricator to the crankcase")
label(12, "lubricator: its lever worked off the flywheel hub by a short rod", (LX, LY, LZ1))

# ---------------------------------------------------------------- the two compressor cylinders, opposed
for s in (-1, 1):
    xd0, xd1 = s * 0.33, s * 0.74          # the open distance piece
    for yy in (CY - 0.13, CY + 0.13):
        box(((xd0 + xd1) / 2, yy, CZ), (abs(xd1 - xd0), 0.04, 0.05), "dark_steel", bevel=0.004)
        box(((xd0 + xd1) / 2, yy, CZ - 0.16), (abs(xd1 - xd0), 0.04, 0.04), "dark_steel", bevel=0.004)
    box(((xd0 + xd1) / 2, CY, CZ - 0.22), (abs(xd1 - xd0), 0.3, 0.06), "dark", bevel=0.006)    # T04: oil-dark guide floor
    xc0 = s * 0.54                                                                               # T04: was 0.52
    ch = pivot((xc0, CY, CZ))
    box((0, 0, 0), (0.12, 0.2, 0.16), "bare", bevel=0.01, parent=ch)                            # T04: was nickel
    box((0, 0, 0.085), (0.1, 0.17, 0.012), "yellow", bevel=0.003, parent=ch)                    # T04: the top slipper
    sphere((0, -0.085, 0.0), 0.02, "bolt", parent=ch)
    cyl((s * 0.315, CY, CZ), 0.07, 0.02, "dark", rot=(0, PI / 2, 0), verts=24, bevel=0)     # the crankcase's rod bore

    def _ch(t, on, ch=ch, s=s, xc0=xc0):
        ch.location = Vector((xc0 + s * xh(t, on), CY, CZ))
    K.ANIM.append(_ch)
    link(lambda t, on, s=s, xc0=xc0: (xc0 + s * xh(t, on), CY, CZ), lambda t, on, s=s: (s * 0.76, CY, CZ),
         r=0.035, mat="nickel", name="piston rod")
    link(lambda t, on, s=s, xc0=xc0: (xc0 + s * xh(t, on), CY, CZ), lambda t, on: (0, CY, CZ),
         r=0.045, mat="dark_steel", name="connecting rod")
    xc = s * 1.06
    cyl((xc, CY, CZ), 0.25, 0.56, "green", rot=(0, PI / 2, 0), verts=40)
    for xx in (s * 0.8, s * 1.32):
        cyl((xx, CY, CZ), 0.28, 0.07, "dark_steel", rot=(0, PI / 2, 0), verts=40)
        for k in range(10):
            a = 2 * PI * (k + 0.5) / 10
            cyl((xx + s * 0.04, CY + 0.25 * math.cos(a), CZ + 0.25 * math.sin(a)), 0.012, 0.02, "bolt",
                rot=(0, PI / 2, 0), verts=6, bevel=0)
    for xx in (s * 0.94, s * 1.18):                       # the valve caps, suction on top, discharge below
        cyl((xx, CY, CZ + 0.27), 0.07, 0.08, "dark_steel", verts=16)
        bolts(xx, CY, CZ + 0.315, 0.05, 4, r=0.01)
        cyl((xx, CY - 0.26, CZ - 0.06), 0.065, 0.07, "dark_steel", rot=(PI / 2, 0, 0), verts=16)
    box((xc, CY, (CZ - 0.25) / 2 + 0.08), (0.3, 0.3, CZ - 0.25 + 0.04), "dark_steel")
    hazard_tag((s * 0.54, CY - 0.155, CZ - 0.22), 0.3, 0.05)
label(5, "compressor cylinders, opposed: rods and crossheads slide in the open frames", (-0.55, CY - 0.1, CZ))

# ---------------------------------------------------------------- suction: the scrubber's head over the top to both cylinders
for s in (-1, 1):
    pipe([(SX + s * 0.3, SY - 0.1, 1.02), (s * 0.5, SY - 0.2, 1.02), (s * 0.82, -0.3, 1.0),
          (s * 0.94, CY + 0.1, CZ + 0.42), (s * 0.94, CY, CZ + 0.31)], r=0.07, mat="green",
         name="suction: the scrubber to a cylinder")
    cyl((SX + s * 0.31, SY - 0.1, 1.02), 0.1, 0.06, "dark_steel", rot=(0, PI / 2, 0), verts=24)
label(6, "suction lines from the scrubber to both cylinders", (0.6, -0.25, 1.0))

# ---------------------------------------------------------------- discharge: up each side into the bottle, the east one through the glass
DY, DZ, DR = 0.98, 0.52, 0.24
drum_ew(-1.18, 0.44, DY, DZ, DR, mat="grey", bands=(-0.85, -0.35, 0.15), saddles=(-0.9, 0.2))
manway_top(-0.35, DY, DZ + DR - 0.02, r=0.09)
pipe([(-1.18, CY - 0.27, CZ - 0.06), (-1.18, CY - 0.42, 0.5), (-1.3, CY - 0.44, 0.5), (-1.45, CY - 0.34, 0.5),
      (-1.45, -0.3, 0.5), (-1.45, 0.6, DZ), (-1.45, DY, DZ), (-1.28, DY, DZ)], r=0.075, mat="iron", name="discharge, west: cylinder to the bottle")
g0, g1, _ = gas_window((1.16, -0.14, 0.62), (1.16, 0.4, 0.62), r=0.11, k=2)
pipe([(1.18, CY - 0.27, CZ - 0.06), (1.18, CY - 0.42, 0.5), (1.3, CY - 0.44, 0.5), (1.45, CY - 0.34, 0.5),
      (1.45, -0.42, 0.55), (1.22, -0.24, 0.62), (1.16, -0.18, 0.62)], r=0.075, mat="iron", name="discharge, east: cylinder to the sight glass")
pipe([(1.16, 0.44, 0.62), (1.16, 0.62, 0.62), (0.9, 0.85, 0.55), (0.58, DY, DZ)], r=0.075, mat="iron",
     name="discharge, east: the sight glass to the bottle")
for y_ in (0.0, 0.3):
    box((1.16, y_, 0.3), (0.12, 0.08, 0.44), "dark_steel")
if OUTLET == "stub":       # the concept's: a nozzle on its own foot, and the bottle's stub out to it
    noz = nozzle("N", length=0.24, mat="bare")
    cyl((0, DY + DR - 0.02, 0.45), 0.17, 0.12, "bare", rot=(PI / 2, 0, 0), verts=32)          # the bottle's outlet stub
    cyl((0, (DY + DR + noz[1]) / 2, 0.44), 0.17, noz[1] - DY - DR + 0.02, "bare", rot=(PI / 2, 0, 0), verts=32)
else:
    outlet_fitting()
gauge((-0.85, DY - DR - 0.02, DZ + 0.06), (0, -1, 0.5), r=0.08, needle=0.02, live=lambda t: -0.2 + 0.9 * delivery(t))
label(7, "discharge up the east side through the sight glass", (1.16, 0.12, 0.75))
label(8, "discharge bottle along the north face", (-0.6, DY, DZ + 0.3))
label(9, "gas out, north, straight off the bottle at the connection's size", (0, 1.34, ZA))

# ---------------------------------------------------------------- the gauge board (W), the fuel, the lube tank and panel (NE)
box((-0.98, 0.12, 0.42), (0.7, 0.12, 0.66), "cream", bevel=0.02)
box((-0.98, 0.18, 0.2), (0.12, 0.12, 0.3), "dark_steel")
for k, (ph, amp) in enumerate(((0.0, 0.9), (0.33, 0.7), (0.66, 1.1))):
    gauge((-1.18 + 0.2 * k, 0.05, 0.52), (0, -1, 0.15), r=0.075, needle=0.02,
          live=lambda t, ph=ph, amp=amp: -0.3 + amp * delivery((t + ph * 0.0) % 1.0))
for k in range(3):
    box((-1.18 + 0.2 * k, 0.05, 0.32), (0.14, 0.01, 0.05), "label", bevel=0)
_n0 = len(K.OBJS)
bundle([(-0.98, 0.18, 0.75), (-0.8, 0.3, 1.0), (-0.5, 0.25, 1.25), (-0.25, CY + 0.3, 1.2), (-0.14, CY + 0.22, 1.16)],
       cols=("black", "red", "grey"), r=0.014, name="gauge board to the ignition")
for _o in K.OBJS[_n0:]:                       # T04: the bundle's markers cream, not label paint (they rolled to white px)
    if _o.type == "MESH" and _o.data.materials and _o.data.materials[0].name == K.M["label"].name:
        _o.data.materials[0] = K.M["cream"]
pipe([(-0.98, 0.12, 0.74), (-0.7, -0.05, 1.1), (-0.32, SY - 0.1, 1.2), (SX - 0.3, SY, 1.2)], r=0.025, mat="bare",
     name="gauge line to the scrubber")
hose([(SX + 0.3, SY + 0.05, 1.3), (0.45, 0.0, 1.3), (0.42, -0.3, 1.2), (0.3, CY + 0.35, 0.95)], r=0.035, mat="hose",
     name="fuel hose: the scrubber to the regulator")
cyl((0.3, CY + 0.35, 0.86), 0.07, 0.16, "yellow", rot=(0, PI / 2, 0), verts=20)            # the regulator
head(0.3, CY + 0.35, 0.92, 0.07, 0.06, "yellow")
pipe([(0.25, CY + 0.35, 0.86), (0.22, CY + 0.2, 0.95), (0.2, CY - 0.2, 0.95), (0.14, CY - 0.2, 0.95)], r=0.025,
     mat="bare",
     name="fuel: the regulator to the gas rail")
label(10, "fuel: a tan hose from the scrubber through the regulator", (0.45, -0.1, 1.3))
label(11, "gauge board: three needles kick on the strokes", (-0.98, 0.05, 0.75))
vtank(1.18, 1.18, 0.2, 0.9, mat="cream", bands=(0.45,), nozzle=None)
cabinet(0.76, 1.3, 0.3, 0.22, 0.5, mat="grey")
status_lens(0.84, 1.22, 0.54)
for yy in (-1.25, -1.0):
    box((-1.08, yy, 0.2), (0.44, 0.18, 0.18), "ochre", bevel=0.015)                        # spare cylinder liners, crated
box((1.1, -1.36, 0.14), (0.22, 0.16, 0.16), "dark_steel", bevel=0.015)
stain(0.2, -0.3, 0.2, 0.08)
stain(-0.7, -1.2, 0.2, 0.08)

route("gas", [(SX, SY, 0.25), (SX, SY, 0.9), (SX + 0.3, SY - 0.1, 1.02), (0.5, SY - 0.2, 1.02), (0.82, -0.3, 1.0),
              (0.94, CY, CZ + 0.31), (1.06, CY, CZ), (1.18, CY - 0.27, CZ - 0.06), (1.45, CY - 0.3, 0.5), (1.45, -0.42, 0.55),
              (1.16, -0.14, 0.62), (1.16, 0.62, 0.62), (0.9, 0.85, 0.55), (0.44, DY, DZ), (0, DY, DZ),
              (0, 1.5, ZA)])
route("gas", [(SX, SY, 0.9), (SX - 0.3, SY - 0.1, 1.02), (-0.5, SY - 0.2, 1.02), (-0.82, -0.3, 1.0), (-0.94, CY, CZ + 0.31),
              (-1.06, CY, CZ), (-1.18, CY - 0.38, 0.5), (-1.45, CY - 0.3, 0.5), (-1.45, 0.6, DZ), (-1.18, DY, DZ),
              (-0.1, DY, DZ)])
route("fuel", [(SX + 0.3, SY + 0.05, 1.3), (0.45, 0.0, 1.3), (0.42, -0.3, 1.2), (0.3, CY + 0.35, 0.95),
               (0.22, CY + 0.2, 0.95), (0.2, CY - 0.2, 0.95)])
# ================================================================ the concept ends here

# ================================================================ the concept's surfacing (gp_kit.run_gp's, before any render)
# the concept's sun, GP.SUN_GP = 10, a step down: at 10 the south drawing (the cream bottle square to the camera)
# read p50 82, over the 75-81 bar, the others 76-77; at 9.85 they read 76, 75, 81, 76 (tonal.py, 1x)
K.SUN_E = _opt("--sun", 9.85)
K.WORLD = GP.WORLD_GP
K5.catcher_unlit()
K5.soften_windows()
K5.satin_floor()
sc = K.sc
sc.cycles.samples = PLATE_SAMPLES
ROOT = K.ROOT
OBJS = K.OBJS
STAINS = K.STAINS
SUN = rig.sun(K.SUN_E)
SUN.data.color = (1.0, 0.94, 0.82)
BG = sc.world.node_tree.nodes["Background"].inputs["Strength"]
BG.default_value = K.WORLD
bpy.context.view_layer.update()


# The shipped glass layer (T08b, Liam on the T08 model: glass "Brighter", less drift, more colour, helium-3 not grey
# at 1x). The engine multiplies the layer by the vent's tint, so the gas can never be brighter than the tint itself;
# T08's layer (white 0.65, wisps 0.42-0.86, the warm sun as it falls, the gas's own sheen) put a quarter of the gas
# at 245 and over (flat tint) and its shaded side and dark wisps near black, and the sun's warmth took blue out of
# helium-3's violet (drawn mean R = B: grey). Now: the layer is mostly the gas lit through the glass (--gas-emit),
# little of it the sun (--gas-white), so the column is even from its lit side to its shaded one; its wisps narrowed
# (--gas-lo/--gas-hi) so it stays under 245 everywhere; the sun's warmth partly balanced out (--gas-neutral); the
# gas's own sheen off (--gas-spec 0), whose sun glint went white whatever the paint. The cost: the drift, from
# 81-151 px changed a frame to 0-7 (measure.py layers_alone): the gas reads as an even body of colour, its wisps
# only faintly. The T08b sweep (concept/crust-tap/model-3x3/glass-sweep.png) has the T08 layer and two between it
# and this one, keeping more drift for less brightness; --glass-sweep renders any of them.
# --gas-white: the paint's albedo, a neutral grey (linear); the painted review gases (--tints) keep the concept's.
GAS_WHITE = _opt("--gas-white", 0.025)
# the wisps' range (the concept's 0.42-0.86 of the paint) and the balance against the warm sun (--gas-neutral 1: the
# white's blue and green raised by the sun's own 1/0.82 and 1/0.94; 0: plain white; mostly lit through the glass,
# a third of that keeps the layer grey). The painted review gases keep the concept's range.
GAS_LO, GAS_HI = _opt("--gas-lo", 0.84), _opt("--gas-hi", 0.90)
GAS_NEUTRAL = _opt("--gas-neutral", 0.3)
GAS_RAMPS = [n for m in bpy.data.materials if m.name.startswith("gas_") and m.node_tree
             for n in m.node_tree.nodes if n.type == "MAP_RANGE"]
# T08b: the gas lit through the glass (--gas-emit): the shipped layer's own colour (the wisps, the neutral) also
# given off at this strength, so the side of the column away from the sun reads in the gas's colour, not dark.
# A lift for the white layer the engine tints in Blender only: the engine draws it as ordinary paint (not
# draw_as_glow, not draw_as_light), so nothing on the building glows in game (spec 3.3). Only while the glass is
# full (the gas's fill value): idle the glass is the plate's dark, empty glass as before; 0 for the painted review
# gases and the icon, which keep the concept's paint. 0 was the T08 layer.
GAS_EMIT = _opt("--gas-emit", 30.0)
# and its sheen (--gas-spec, a share of the T08 layer's specular, the satin floor's: 1 is the T08 layer): the sun's
# highlight on the gas column is white whatever the paint, and on the shipped layer that white is the engine's to
# tint flat. Only while the glass is full (the fill value): the plate's empty glass keeps its T08 sheen, so the idle
# plate is the T08 plate. The painted review gases and the icon keep the T08 specular (1 was the T08 layer).
GAS_SPEC = _opt("--gas-spec", 0.0)
GAS_EMITS = []
GAS_BSDFS = []
for m_ in bpy.data.materials:
    if not (m_.name.startswith("gas_") and m_.node_tree):
        continue
    nt_ = m_.node_tree
    bsdf_ = nt_.nodes["Principled BSDF"]
    mx_ = next(n for n in nt_.nodes if n.type == "MIX" and n.inputs["Factor"].is_linked
               and n.inputs["Factor"].links[0].from_node.type == "VALUE")
    fill_ = mx_.inputs["Factor"].links[0].from_node
    em_ = nt_.nodes.new("ShaderNodeValue")
    em_.outputs[0].default_value = 0.0
    st_ = nt_.nodes.new("ShaderNodeMath")
    st_.operation = "MULTIPLY"
    nt_.links.new(fill_.outputs[0], st_.inputs[0])
    nt_.links.new(em_.outputs[0], st_.inputs[1])
    nt_.links.new(mx_.outputs["Result"], bsdf_.inputs["Emission Color"])
    nt_.links.new(st_.outputs[0], bsdf_.inputs["Emission Strength"])
    GAS_EMITS.append(em_)
    # specular = s0 * (1 - fill * drop), drop = 1 - the --gas-spec share
    s0_ = bsdf_.inputs["Specular IOR Level"].default_value
    drop_ = nt_.nodes.new("ShaderNodeValue")
    drop_.outputs[0].default_value = 0.0
    fd_ = nt_.nodes.new("ShaderNodeMath")
    fd_.operation = "MULTIPLY"
    nt_.links.new(fill_.outputs[0], fd_.inputs[0])
    nt_.links.new(drop_.outputs[0], fd_.inputs[1])
    sp_ = nt_.nodes.new("ShaderNodeMath")
    sp_.operation = "MULTIPLY_ADD"                      # fill*drop * -s0 + s0
    nt_.links.new(fd_.outputs[0], sp_.inputs[0])
    sp_.inputs[1].default_value = -s0_
    sp_.inputs[2].default_value = s0_
    nt_.links.new(sp_.outputs[0], bsdf_.inputs["Specular IOR Level"])
    GAS_BSDFS.append(drop_)


def set_tint(hexc, white=None, lo=None, hi=None, neutral=None, emit=None, spec=None):
    """The gas's paint in the glass: a neutral for the shipped layer (the engine tints it), a gas's own for review."""
    w = GAS_WHITE if white is None else white
    nu = GAS_NEUTRAL if neutral is None else neutral
    sun = SUN.data.color
    bal = [1.0 + nu * (sun[0] / sun[c] - 1.0) for c in range(3)]
    for rgb in GP.GAS_TINT:
        rgb.outputs[0].default_value = (w * bal[0], w * bal[1], w * bal[2], 1.0) if hexc is None \
            else rig.srgb(hexc)
    painted = hexc is not None
    for n in GAS_RAMPS:
        n.inputs["To Min"].default_value = 0.42 if painted else (GAS_LO if lo is None else lo)
        n.inputs["To Max"].default_value = 0.86 if painted else (GAS_HI if hi is None else hi)
    for n in GAS_EMITS:
        n.outputs[0].default_value = 0.0 if painted else (GAS_EMIT if emit is None else emit)
    for n in GAS_BSDFS:
        n.outputs[0].default_value = 0.0 if painted else 1.0 - (GAS_SPEC if spec is None else spec)


set_tint(None)


# ---------------------------------------------------------------- the pose
def set_pose(f, gas=False):
    """Every part at frame f of the working loop (idle is a frame held: the engine stops the loop where it is);
    the glass full and drifting when gas, else empty."""
    K.pose((f % NF) / NF, True)
    for v in GP.GAS_FILL:
        v.outputs[0].default_value = 1.0 if gas else 0.0
    bpy.context.view_layer.update()


# ---------------------------------------------------------------- T13b: the north drawing's fitting trimmed at the edge line
# Liam (2026-10-27, Q20.2, "Accept"): facing north, unconnected, vanilla's north cover must show. In game (T13b probe,
# evidence/gas-pump-t13b/) the engine draws a north cover behind the building whatever secondary_draw_orders says, and
# the pipe picture over it: so the open bell (port-N) hid it, and with the bell gone the plate's own sleeve end and
# outer flange still did, standing up the screen past the north edge (at ZA, ZA/2 = 0.21 tile up) where the cover
# draws (its sprite: -1.86 to -1.50 tile, up to 0.41 either side). So, as vanilla draws a north fitting, nothing of the
# outlet's fitting is drawn past the north edge line on the screen: in the north drawing only, every part of the
# fitting is cut by the plane y + z cos(elevation) = EDGE (the camera's own view through the edge line, so the cut
# faces are edge-on and unseen); the cover caps the sleeve there while nothing is joined, the vanilla pipe meets it
# once one is, and the north pipe picture is empty (port-N is rendered for pack_ports, not shipped). The south drawing,
# the icon (the whole machine, as signed off) and --collide (the model as built) keep the fitting whole.
NORTH_CUT = []


def _north_cut():
    k = math.cos(rig.ELEVATION)
    n = Vector((0.0, 1.0, k)).normalized()                  # out of the plane, into what is cut
    t = Vector((0.0, -k, 1.0)).normalized()                 # in the plane, across the edge line
    p0 = Vector((0.0, EDGE, 0.0))                           # on the plane: the edge on the ground
    import bmesh
    # a unit cube to a slab 2 wide (x), 4 across the edge line, 2 deep on the cut side of the plane
    m4 = Matrix((
        (2.0, 0.0, 0.0, p0.x + n.x),
        (0.0, 4.0 * t.y, 2.0 * n.y, p0.y + n.y),
        (0.0, 4.0 * t.z, 2.0 * n.z, p0.z + n.z),
        (0.0, 0.0, 0.0, 1.0)))
    me = bpy.data.meshes.new("t13b north cut")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=m4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    cutter = bpy.data.objects.new("t13b north cut", me)
    bpy.context.scene.collection.objects.link(cutter)
    cutter.parent = ROOT_
    cutter.hide_render = True
    cutter.display_type = "WIRE"
    for o in FIT_OBJS.get(frozenset(("north", "south")), []):
        if o.type != "MESH":
            continue
        m = o.modifiers.new("t13b north cut", "BOOLEAN")
        m.operation, m.object, m.solver = "DIFFERENCE", cutter, "EXACT"
        NORTH_CUT.append(m)


if OUTLET == "fitting" and not (ICON or COLLIDE):
    _north_cut()

CUR_D = ["north"]


def turn(d):
    CUR_D[0] = d
    ROOT.rotation_euler = (0, 0, TURN[d])
    for m in NORTH_CUT:
        m.show_render = m.show_viewport = d == "north"
    bpy.context.view_layer.update()


def drawn_in(o, d=None):
    return (d or CUR_D[0]) in VAR.get(o.name, ALL_DIRS)


# ---------------------------------------------------------------- the layers, found
def _moving():
    m0, moving = {}, set()
    for f in range(NF):
        set_pose(f)
        for o in OBJS:
            m = o.matrix_world.copy()
            if o.name not in m0:
                m0[o.name] = m
            elif any(abs(m[i][j] - m0[o.name][i][j]) > 1e-6 for i in range(4) for j in range(4)):
                moving.add(o.name)
    set_pose(0)
    return moving


MOVING = _moving()
PART = {}
for o in OBJS:
    if o.name in MOVING:
        PART[o.name] = "mech"
    elif o.type == "MESH" and o.data.materials and o.data.materials[0].name.startswith("gas_"):
        PART[o.name] = "glass"
    else:
        PART[o.name] = "body"
GROUPS_ALL = ("body", "glass", "mech")
GLASSY = ("glass", "pane")          # transparent: hidden, not held out, where a layer is rendered alone
print(f"parts {len(OBJS)}: " + ", ".join(f"{g} {sum(1 for o in OBJS if PART[o.name] == g)}" for g in GROUPS_ALL))


def members(*groups):
    return [o for o in OBJS if PART[o.name] in groups]


def _glassy(o):
    return o.type == "MESH" and any(m is not None and m.name.startswith(GLASSY) for m in o.data.materials)


# ---------------------------------------------------------------- the pipe pictures
FITTINGS = {}


def fitting(p, cap):
    """T08: the pipe picture for one face, under Liam's fitting rule (2026-10-21): the building's own fitting (the
    pad, the sleeve and its outer flange, _outlet_fitting) already stands at the edge, so the picture is only what a
    joined pipe adds -- a mating flange bolted to the sleeve's, a visible reducer up to the vanilla pipe's bore, a
    short spool and a ring where the vanilla pipe butts on. Built where the turned machine's fitting stands: north and south on the middle,
    east and west OUT_DX south of it (the variants above). `cap` is a blind flange: rendered because pack_ports packs
    both, though the wiring draws vanilla's cover (the rule)."""
    face, tile = p["face"], p["tile"]
    g = f"{'cover' if cap else 'port'}-{face}"
    first = len(OBJS)
    u = Vector({"N": (0, 1, 0), "S": (0, -1, 0), "E": (1, 0, 0), "W": (-1, 0, 0)}[face])
    c = Vector((0.0, 0.0, ZA)) if face in "NS" else Vector((0.0, -OUT_DX, ZA))
    c += u * EDGE
    rn = 0.17
    rot = along(u)
    up = Vector((0, 0, 1))
    side = u.cross(up).normalized()
    cyl(tuple(c + u * 0.018), OUT_FLANGE, 0.036, "dark_steel", rot=rot, verts=40, bevel=0.004)        # mating flange
    for i in range(8):
        a = 2 * PI * (i + 0.25) / 8
        cyl(tuple(c + u * 0.04 + (side * math.cos(a) + up * math.sin(a)) * (OUT_FLANGE - 0.025)), 0.018, 0.012, "bare",
            rot=rot, verts=6, bevel=0)
    if cap:
        cyl(tuple(c + u * 0.045), rn * 1.2, 0.02, "dark_steel", rot=rot, verts=40, bevel=0.004)        # blind
    else:
        # a reducer out to the vanilla pipe's bore (its body is 41 px across on the screen, r 0.29 a horizontal
        # one: measure.py's join counted the rows past a narrower spool as ground), a spool at that bore, and a ring
        # where the vanilla pipe's end butts on (Liam, 2026-10-20: a change of bore only at a visible reducer)
        R = 0.29
        x0 = 0.036
        bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=rn * 1.18, radius2=R, depth=0.1,
                                        location=tuple(c + u * (x0 + 0.05)), rotation=rot)
        K._finish(bpy.context.active_object, "bare", 0.004, smooth=True)
        cyl(tuple(c + u * (x0 + 0.1 + 0.07)), R, 0.14, "bare", rot=rot, verts=48, bevel=0.004)            # the spool
        cyl(tuple(c + u * (x0 + 0.24 - 0.015)), 0.35, 0.03, "bare", rot=rot, verts=48, bevel=0.006)       # its end ring
        if face == "W":
            west_seam(first)
    FITTINGS[g] = OBJS[first:]


# T13b: the west seam (Liam, 2026-10-27, Q20.3, "Accept"). Facing west the sun is behind the sleeve's outer flange, which
# throws a band of shadow 2 px wide (at 2x) across the sleeve just inside it: between the cover (or the joined pipe's
# flange) and the lit sleeve it read as a seam. The plate keeps it; the west picture, drawn over the plate, now carries
# the plate's own outer flange, its nuts and the sleeve to X_SEAM inside the edge -- copies of the west variant's parts,
# turned as the west drawing turns them, so their surfacing is the plate's -- with no flange casting a shadow on them.
X_SEAM = 0.085                                # tiles inside the edge: the band (0.047-0.062) and a pixel each side


def west_seam(first):
    src = FIT_OBJS[frozenset(("west",))]
    turn_w = Matrix.Rotation(TURN["west"], 4, "Z")
    slab = box((-EDGE - 0.25 + X_SEAM / 2, 0.0, 0.6), (0.5 + X_SEAM, 2.0, 1.2), "bare", bevel=0)
    OBJS.remove(slab)
    slab.hide_render = True
    slab.display_type = "WIRE"
    for o in src:
        if o.type != "MESH" or o.name.startswith("outlet pad"):
            continue
        d = o.copy()
        d.data = o.data.copy()
        bpy.context.scene.collection.objects.link(d)
        d.parent = o.parent
        d.matrix_basis = turn_w @ o.matrix_basis
        m = d.modifiers.new("t13b west seam", "BOOLEAN")
        m.operation, m.object, m.solver = "INTERSECT", slab, "EXACT"
        if K.M["dark_steel"] in d.data.materials[:] or d.dimensions.length < 0.06:
            d.visible_shadow = False                # the flange and its nuts: their band is what is closed
        OBJS.append(d)
    for o in OBJS[first:]:
        if o.type == "MESH" and K.M["dark_steel"] in o.data.materials[:]:
            o.visible_shadow = False                # the picture's mating flange: no band from it either


# ---------------------------------------------------------------- the runs' ends, on the sprite (for the ends' crops)
def screen_of(p, d):
    """A model point's place on the sprite in direction d, tiles from the entity origin (x right, y down)."""
    a = TURN[d]
    x = p[0] * math.cos(a) - p[1] * math.sin(a)
    y = p[0] * math.sin(a) + p[1] * math.cos(a)
    return round(x, 4), round(-(y + p[2] * math.cos(rig.ELEVATION)), 4)


def runs_on_sprite():
    out = []
    for k, (name, a, b, _) in enumerate(K.PIPES):
        out.append(dict(name=name, ends=[dict(at=[round(v, 3) for v in p], screen={d: screen_of(p, d) for d in DIRS})
                                         for p in (a, b)],
                        course={d: [screen_of(p, d) for p in RUN_PTS.get(k, [])] for d in DIRS}))
    return out


# ---------------------------------------------------------------- --collide (the Vent Pump model's, one direction)
DEEP = 0.03
DETAIL_MATS = {"bolt", "seam", "stencil", "hazard", "label", "gauge", "ceramic", "needle", "red", "yellow", "brass",
               "dark", "lamp", "oil", "pane", "rubber"}
# meant contacts of a moving part with a fixed one: (moving part, fixed part, why), on the parts' descriptions
SHAFT = r"\[bare\] at \(\+0\.00,-1\.16,0\.68\)"          # the crankshaft's south end
MEANT = [
    (r"\[\w+\] at \([-+]0\.\d\d,-1\.[234]\d,", SHAFT,
     "the flywheel (its hub, web, spokes and weight) and the lubricator's crank keyed on the crankshaft's end"),
    (r"\[needle\]", r"\[ceramic\]", "a gauge needle over its own face (the kit's gauge: 0.001 tile)"),
    (r"connecting rod", r"\[green\] at \([-+]0\.00,-0\.76,0\.44\)",
     "a connecting rod through its bore into the crankcase, to the crank"),
    (r"\[bare\] at \([-+]0\.\d\d,-0\.76,0\.58\)", r"moving (piston|connecting) rod",
     "a rod's end in its crosshead (the concept's linkage: both rods on the crosshead's centre)"),
    (r"connecting rod", r"\[dark\] at \([-+]0\.31,-0\.76,0\.58\)", "a connecting rod through the crankcase's rod bore"),
    (r"connecting rod", r"moving connecting rod", "the two connecting rods on the one crank, inside the crankcase"),
    (r"piston rod", r"moving connecting rod", "the piston rod and the connecting rod meeting in their crosshead"),
    (r"at \(\+0\.[67]\d,-1\.4\d,0\.[5-8]\d\)", r"\[bare\] at \(\+0\.68,-1\.40,0\.80\)|lubricator drive rod",
     "the lubricator's lever on its axle, the rod's eye on the lever's pin"),
    (r"\[bolt\] at \([-+]0\.\d\d,-1\.4\d,", r"lubricator drive rod", "the rod's eye on the crank pin"),
]
# fixed parts that meet by design, as the concept built them (each part's centre as modelled, facing north)
_OUT = r"at \([-+]0\.[0-2]\d,\+1\.[0-4]\d,0\.4\d\)"         # the outlet's fitting (T08), on its variant's x
_WH = r"at \([-+]0\.00,\+0\.(1[26]|2[01]),(0\.[0-3]\d|0\.78)\)"     # the wellhead stack and the scrubber's shell
MEANT_FIXED = [
    (_WH, _WH, "the wellhead stack: the vent collar, the wellhead flange and the scrubber's shell seated in one "
               "another and in their footing"),
    (r"\[dark_steel\] at \(\+0\.00,-0\.83,0\.07\)", _WH, "the vent collar's foot ring against the crankcase's footing"),
    (r"\[dark_steel\] at \([-+]1\.06,-0\.76,0\.25\)", r"at \([-+](0\.9[89]|1\.06),-0\.7[46],0\.(06|58)\)",
     "a compressor cylinder in its saddle, the saddle on its footing"),
    (r"\[dark_steel\] at \([-+]0\.\d\d,\+0\.98,0\.22\)", r"at \([-+]0\.\d\d,\+0\.98,0\.52\)",
     "the discharge bottle and its bands in their saddles"),
    (r"\[bare\] at \(\+0\.00,\+1\.2[04],0\.4[45]\)", r"at \([-+]0\.(37|15|29),\+0\.98,0\.52\)",
     "the outlet stub let into the bottle (spec 3.1: out of the bottle's north side)"),
    (_OUT, r"at \([-+]0\.\d\d,\+0\.98,0\.52\)", "the outlet's pad welded on the bottle, its sleeve let into it"),
    (_OUT, _OUT, "the outlet fitting's own parts: pad, sleeve, flanges, weld, bore"),
    (r"\[dark_steel\] at \([-+]0\.31,\+0\.06,1\.02\)", r"at \([-+]0\.00,\+0\.16,(0\.78|1\.12)\)",
     "the suction nozzles' flanges on the scrubber's shell and its band"),
    (r"\[dark_steel\] at \(-0\.98,\+0\.18,0\.20\)", r"\[cream\] at \(-0\.98,\+0\.12,0\.42\)|\[dark_steel\] at \(-0\.9\d,\+0\.1\d,0\.04\)",
     "the gauge board on its post, the post on its footing"),
    (r"\[gas_1\]", r"\[nickel\] at \(\+1\.16,", "the gas column held in the sight glass's end ferrules"),
    (r"\[green\] at \([-+]0\.00,-0\.76,0\.44\)", SHAFT, "the crankshaft's end out of the crankcase"),
]


def collide_check():
    from mathutils.bvhtree import BVHTree
    lines = []
    if os.path.exists(os.path.join(OUT, "collide-model.txt")):
        os.remove(os.path.join(OUT, "collide-model.txt"))

    def out(s_):
        print(s_, flush=True)
        lines.append(s_)
    RI = ROOT.matrix_world.inverted()
    asm = {}                                  # object -> the run (K.PIPES index) it belongs to
    runs = {}
    idx = {o.name: i for i, o in enumerate(OBJS)}
    for k, (name, a_, b_, (i0, i1)) in enumerate(K.PIPES):
        for o in OBJS[i0:i1]:
            asm[o.name] = k
        runs[k] = (Vector(a_), Vector(b_))
    parents = {o.name: (o.parent.name if o.parent is not None and o.parent is not ROOT else None) for o in OBJS}

    def mat_of(o):
        return o.data.materials[0].name if getattr(o.data, "materials", None) and o.data.materials else "-"

    def world_mesh(o):
        dg = bpy.context.evaluated_depsgraph_get()
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ev.matrix_world
        vs = [mw @ v.co for v in me.vertices]
        ps = [tuple(p_.vertices) for p_ in me.polygons]
        ev.to_mesh_clear()
        return vs, ps

    def aabb(vs):
        xs, ys, zs = zip(*vs)
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    def meet(a, b):
        return all(a[0][i] <= b[1][i] and b[0][i] <= a[1][i] for i in range(3))

    def inside(tree, p_):
        dv = Vector((0.5774, 0.5771, 0.5777))
        n, o = 0, p_.copy()
        for _ in range(64):
            hit = tree.ray_cast(o, dv)
            if hit[0] is None:
                break
            n += 1
            o = hit[0] + dv * 1e-5
        return n % 2 == 1

    class Part:
        def __init__(self, o):
            self.o = o
            self.vs, ps = world_mesh(o)
            self.box = aabb(self.vs) if self.vs else None
            self.tree = BVHTree.FromPolygons(self.vs, ps) if ps else None
            c = RI @ (sum(self.vs, Vector()) / len(self.vs)) if self.vs else Vector()
            lo, hi = (RI @ Vector(self.box[0]), RI @ Vector(self.box[1])) if self.vs else (c, c)
            self.size = max(abs(hi.x - lo.x), abs(hi.y - lo.y), abs(hi.z - lo.z))
            self.desc = f"{o.name}[{mat_of(o)}] at ({c.x:+.2f},{c.y:+.2f},{c.z:.2f})"
            self.mat = mat_of(o)

    def clash(a, b):
        if a.tree is None or b.tree is None or not meet(a.box, b.box):
            return None
        if a.tree.overlap(b.tree):
            return "cross"
        if meet(b.box, (a.vs[0], a.vs[0])) and inside(b.tree, a.vs[0]):
            return "inside"
        if meet(a.box, (b.vs[0], b.vs[0])) and inside(a.tree, b.vs[0]):
            return "contains"
        return None

    def depth(a, b):
        dd = 0.0
        for v in a.vs:
            if meet(b.box, (v, v)) and inside(b.tree, v):
                hit = b.tree.find_nearest(v)
                if hit[0] is not None:
                    dd = max(dd, (RI.to_3x3() @ (hit[0] - v)).length)
        return dd

    def inside_pts(x, y):
        return [RI @ v for v in x.vs if meet(y.box, (v, v)) and inside(y.tree, v)]

    def seated(a, b):
        for x, y in ((a, b), (b, a)):
            for xr, yr, why in MEANT_FIXED:
                if re.search(xr, x.desc) and re.search(yr, y.desc):
                    return why
        if a.o.name in asm and asm.get(a.o.name) == asm.get(b.o.name):
            return "one run's own parts"
        for x, y in ((a, b), (b, a)):
            if x.mat in DETAIL_MATS or x.mat.startswith("cable_"):
                return f"a {x.mat} detail on its host"
            if x.size < 0.16:
                return "a small fitting on its host"
        for x, y in ((a, b), (b, a)):
            k = asm.get(x.o.name)
            if k is not None:
                pts = inside_pts(x, y) or inside_pts(y, x)
                ends = runs[k]
                if pts and all(min((p_ - ends[0]).length, (p_ - ends[1]).length) < 0.45 for p_ in pts):
                    return "a pipe or line's end let into what it serves"
        return None

    def same_rig(a, b):
        return parents[a.name] is not None and parents[a.name] == parents[b.name]

    turn("north")
    for vd in ("north", "east", "west"):          # one check a variant: the machine turns whole (south is north's)
        collide_variant(vd, out, lines, Part, clash, depth, seated, same_rig)


def collide_variant(vd, out, lines, Part, clash, depth, seated, same_rig):
    meant_lines, pairs = [], []
    meshes = [o for o in OBJS if o.type == "MESH" and o not in STAINS and vd in VAR.get(o.name, ALL_DIRS)]
    out(f"COLLIDE {vd} (the whole machine turns, as modelled; its {vd} variant): {len(meshes)} parts, "
        f"{len([o for o in meshes if o.name in MOVING])} moving; frames 0-{NF - 1}")
    fixed_cache, hits = {}, {}
    for f in range(NF):
        set_pose(f)
        mv = [o for o in meshes if o.name in MOVING]
        fx = [o for o in meshes if o.name not in MOVING]
        for o in fx:
            if o.name not in fixed_cache:
                fixed_cache[o.name] = Part(o)
        mparts = [Part(o) for o in mv]
        for a in mparts:
            for o in fx:
                kind = clash(a, fixed_cache[o.name])
                if kind:
                    hits.setdefault((a.desc, fixed_cache[o.name].desc, kind), []).append(f)
        for i, a in enumerate(mparts):
            for b in mparts[i + 1:]:
                if same_rig(a.o, b.o):
                    continue                     # one moving assembly's own parts (a wheel's web and its spokes)
                kind = clash(a, b)
                if kind:
                    hits.setdefault((a.desc, "moving " + b.desc, kind), []).append(f)
    n_meant = n_clash = 0
    for (ad, bd, kind), fs in sorted(hits.items()):
        why = next((w for ar, br, w in MEANT if (re.search(ar, ad) and re.search(br, bd))
                    or (re.search(ar, bd) and re.search(br, ad))), None)
        fr = f"{fs[0]}-{fs[-1]}" if fs == list(range(fs[0], fs[-1] + 1)) else ",".join(map(str, fs))
        if why:
            n_meant += 1
            meant_lines.append(f"meant moving {ad} x {bd}: {kind}, frames {fr}  ({why})")
        else:
            n_clash += 1
            out(f"COLLIDE CLASH moving {ad} x {bd}: {kind}, frames {fr}")
    set_pose(0)
    fixed = [fixed_cache[o.name] for o in meshes if o.name in fixed_cache]
    n_real = n_deep = 0
    order = {"REAL": 0, "touch": 1, "seated": 2}
    for i, a in enumerate(fixed):
        for b in fixed[i + 1:]:
            kind = clash(a, b)
            if not kind:
                continue
            why = seated(a, b)
            dp = max(depth(a, b), depth(b, a)) if why is None else 0.0
            tag = "seated" if why else ("REAL" if dp > DEEP else "touch")
            n_real += tag == "REAL"
            n_deep += tag == "touch"
            pairs.append((tag, -dp, f"{tag} {a.desc} x {b.desc}: {kind}, {dp:.3f} deep" + (f"  ({why})" if why else "")))
            if tag == "REAL":
                out(f"COLLIDE REAL fixed {a.desc} x {b.desc}: {kind}, {dp:.3f} deep")
    out(f"COLLIDE {vd} moving: {n_clash} clashes, {n_meant} meant contacts (collide-model.txt)")
    with open(os.path.join(OUT, "collide-model.txt"), "a") as f_:
        f_.write(f"==== {vd}\n" + "\n".join(meant_lines) + "\n\n")
        f_.write("\n".join(l_ for _, _, l_ in sorted(pairs, key=lambda p_: (order[p_[0]], p_[1], p_[2]))) + "\n")
    out(f"COLLIDE {vd} model: {n_real} clashes (REAL: reach more than {DEEP} tile into each other and no rule explains "
        f"them); {len(pairs)} touching pairs, {n_deep} touch at under {DEEP} (collide-model.txt)")
    ends = K.check_ends()
    loose = [e["name"] for e in ends if not e["ok"]]
    out(f"COLLIDE ends: {len(ends) - len(loose)} of {len(ends)} runs end in what they serve"
        + (f"; loose (not a clash, listed): {'; '.join(loose)}" if loose else ""))
    with open(os.path.join(OUT, "collide.txt"), "w") as f_:
        f_.write("\n".join(lines) + "\n")


if COLLIDE:
    collide_check()
    print("done")
    sys.exit(0)

# ---------------------------------------------------------------- --ports
if PORTS:
    random.seed(4)                  # (nothing random is drawn now; kept so a later picture is repeatable)
    for p_ in DECL["ports"]:
        fitting(p_, cap=False)
        fitting(p_, cap=True)
    rig.bounce_ground()
    contract.declare(OUT, canvas=PORT_CANVAS, **DECL)
    rig.camera(*PORT_CANVAS)
    turn("north")
    set_pose(0)
    for f_ in "NESW":
        for kind in ("port", "cover"):
            show = set(map(id, FITTINGS[f"{kind}-{f_}"]))
            for o in OBJS:
                o.hide_render = id(o) not in show
                o.is_holdout = False
                o.visible_camera = True
            rig.render(os.path.join(OUT, f"{kind}-{f_}.png"))
    print("done")
    sys.exit(0)

GROUND = rig.ground_catcher()
BOUNCE = rig.bounce_ground()

# ---------------------------------------------------------------- --icon
ICON_FRAME = _opt("--icon-frame", 0)   # 0: the weight at the top of the wheel, the crossheads out (spec 16)
if ICON:
    sc.cycles.samples = 128
    cam = rig.camera(1024, 1024, ss=1)
    turn("north")
    set_tint(SIDERANE_HEX)
    set_pose(ICON_FRAME, gas=True)
    for o in OBJS:
        o.hide_render = o in STAINS or not drawn_in(o)
        o.is_holdout = False
        o.visible_camera = True
    GROUND.hide_render = True
    bpy.context.view_layer.update()
    inv = cam.matrix_world.inverted()
    xs, ys = [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for o in OBJS:
        if o.hide_render or o.type != "MESH":
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        for v in me.vertices:
            p_ = inv @ (ev.matrix_world @ v.co)
            xs.append(p_.x)
            ys.append(p_.y)
        ev.to_mesh_clear()
    span = max(max(xs) - min(xs), max(ys) - min(ys)) / 0.94
    cam.data.ortho_scale = span
    cam.data.shift_x = (max(xs) + min(xs)) / 2 / span
    cam.data.shift_y = (max(ys) + min(ys)) / 2 / span
    rig.render(os.path.join(OUT, "icon.png"))
    print(f"icon: {span:.2f} tiles across")
    print("done")
    sys.exit(0)

# ---------------------------------------------------------------- render helpers
rig.camera(*CANVAS)


def setup(visible=(), holdouts=(), unseen=(), ground=False, hide_glassy=False):
    for o in OBJS:
        g = PART[o.name]
        o.hide_render = not drawn_in(o) or not (g in visible or g in holdouts or g in unseen) \
            or (hide_glassy and _glassy(o) and g not in visible)
        o.is_holdout = g in holdouts
        o.visible_camera = g not in unseen
    GROUND.hide_render = not ground


def window(objs, pad=0.12):
    """The render border (sprite px) round objs' projection over every frame, padded."""
    cam = sc.camera
    inv = cam.matrix_world.inverted()
    xs, ys = [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for f in range(NF):
        set_pose(f)
        for o in objs:
            if o.type != "MESH":
                continue
            ev = o.evaluated_get(dg)
            for c in ev.bound_box:
                p_ = inv @ (ev.matrix_world @ Vector(c))
                xs.append(p_.x)
                ys.append(p_.y)
    set_pose(0)
    ppt = rig.PX_PER_TILE
    W, Hc = CANVAS
    x0 = max(0, int(W / 2 + (min(xs) - pad) * ppt))
    x1 = min(W, int(W / 2 + (max(xs) + pad) * ppt) + 1)
    y0 = max(0, int(Hc / 2 - (max(ys) + pad) * ppt))
    y1 = min(Hc, int(Hc / 2 - (min(ys) - pad) * ppt) + 1)
    return x0, y0, x1, y1


def border(win):
    W, Hc = CANVAS
    x0, y0, x1, y1 = win
    sc.render.use_border = True
    sc.render.use_crop_to_border = False
    sc.render.border_min_x, sc.render.border_max_x = x0 / W, x1 / W
    sc.render.border_min_y, sc.render.border_max_y = 1 - y1 / Hc, 1 - y0 / Hc


def no_border():
    sc.render.use_border = False


# ---------------------------------------------------------------- --tints: the glass in each gas's own paint (review)
if TINTS:
    sc.cycles.samples = ANIM_SAMPLES
    turn("north")
    border(window(members("glass")))
    for name, hexc, w in [("siderane", SIDERANE_HEX, None), ("helium", HELIUM_HEX, None)] + \
            [(f"white{w_:.2f}", None, w_) for w_ in (1.0, 0.8, 0.65, 0.5, 0.4)]:
        set_tint(hexc, w)
        for f in (0, 6):
            set_pose(f, gas=True)
            setup(visible=GROUPS_ALL)
            rig.render(os.path.join(OUT, f"tint-{name}-{f:02d}.png"))
    print("done")
    sys.exit(0)

# ---------------------------------------------------------------- --glass-sweep: the shipped glass layer alone (T08b)
# --glass-sweep "tag:white:lo:hi:neutral[:emit[:spec]];..." renders, per variant, the glass layer as the pass below does (the
# rest held out, the pane hidden) for --sweep-frames (default every frame) and --only's directions (default all four)
# into <OUT>/<tag>/glass-NN-<direction>.png: to the sprite size and cut as a pack would, they are the variant's sheets
SWEEP = _opt("--glass-sweep", "")
if SWEEP:
    sc.cycles.samples = ANIM_SAMPLES
    frames = [int(x) for x in _opt("--sweep-frames", ",".join(str(i) for i in range(NF))).split(",")]
    for d in ONLY:                      # --only picks the directions, as for a pack (default all four)
        turn(d)
        border(window(members("glass")))
        for spec_ in SWEEP.split(";"):
            tag, w, lo, hi, nu, *more = spec_.split(":")
            more = [float(x) for x in more] + [0.0, 1.0][len(more):]
            set_tint(None, float(w), float(lo), float(hi), float(nu), *more[:2])
            for f in frames:
                set_pose(f, gas=True)
                setup(visible=("glass",), holdouts=("body", "mech"), hide_glassy=True)
                rig.render(os.path.join(OUT, tag, f"glass-{f:02d}-{d}.png"))
    set_tint(None)
    print("done")
    sys.exit(0)

# ---------------------------------------------------------------- the passes, per direction
if not IDLE:
    contract.declare(OUT, canvas=CANVAS, **DECL)
for d in ONLY:
    turn(d)

    def path(stem, d=d):
        return os.path.join(OUT, contract.named(stem, d) + ".png")
    no_border()
    sc.cycles.samples = PLATE_SAMPLES
    # the plate: the machine stopped, no moving part drawn (they cast their frame-0 shadows), the glass empty
    set_pose(0)
    setup(visible=("body", "glass"), unseen=("mech",))
    rig.render(path("idle"))
    # the still: the plate with every moving part at frame 0
    setup(visible=GROUPS_ALL)
    rig.render(path("still"))
    if IDLE:
        continue
    setup(visible=GROUPS_ALL, ground=True)
    for o in OBJS:
        o.visible_camera = False
    rig.render(path("shadow"))
    sc.cycles.samples = ANIM_SAMPLES
    # the moving parts, the rest held out
    border(window(members("mech")))
    for f in range(NF):
        set_pose(f)
        setup(visible=("mech",), holdouts=("body", "glass"), hide_glassy=True)
        rig.render(path(contract.frame("mech", f)))
    # the gas in the glass, white, the rest held out and the pane hidden
    border(window(members("glass")))
    for f in range(NF):
        set_pose(f, gas=True)
        setup(visible=("glass",), holdouts=("body", "mech"), hide_glassy=True)
        rig.render(path(contract.frame("glass", f)))
    no_border()

with open(os.path.join(OUT, "..", "model.json"), "w") as f_:
    json.dump(dict(frames=NF, speed=SPEED, sun=K.SUN_E, world=K.WORLD,
                   samples=dict(plate=PLATE_SAMPLES, anim=ANIM_SAMPLES),
                   groups={g: len(members(g)) for g in GROUPS_ALL}, moving=sorted(MOVING),
                   runs=runs_on_sprite(), labels=K.LABELS), f_, indent=1)
print("done")
