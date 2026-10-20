"""Vent Pump (sae-vent-pump): the Gas Lift Tower, round 5 variant (a) -- the shipping model (T07).

  BLENDER=<blender 5> tools/blender/render.sh concept/vent-pump/model/vent_pump.py <out-dir> --ports --icon
  (or directly: blender -b --python vent_pump.py -- <out-dir> [--idle | --ports | --icon | --collide]
                [--samples N] [--anim-samples N] [--south round5])

  --idle     idle-, still- and working glow frame 0 per direction only: the quick loop for the finish
  --ports    the four pipe pictures and their caps, port-<face>.png and cover-<face>.png
  --icon     icon.png: the whole tower facing north, working (the melt and the helium lit)
  --collide  no render: every moving part in every frame against every other part, and every
             fixed part against every other, by BVH; collide.txt and collide-model.txt in <out-dir>
  --south round5   the south footing as round 5 had it (the join's "before", for the review only)

Spec: concept/vent-pump/building-spec-vent-pump.md (written 9e067a3): the Gas Lift Tower, round 5,
variant (a) "Warmer paints" (Liam, 2026-10-20). The geometry and the surfacing are round 5's
(options/round-5/vpb5_08_gas_lift_tower.py --variant a), built with its kit, copied unchanged into
kit/ (vpb3_kit.py, vp4_glass.py, vpb4_kit.py, vpb5_kit.py; each file's first line says what the copy
changed: import paths, the variant fixed at (a), the glass's pose and emission handles). What this
model changes from round 5, and nothing else:

  - the south join (Liam, "Fix in the model"): the inlet's footing is carried out to the south edge
    under the nozzle (round 5's stopped 0.32 tile short of it, so measure.py saw ground between the
    pipe and the building in 7 of the pipe body's 39 columns);
  - the two status lenses (spec 3.3, 7: "House green, gear amber", drawn as a "Light"): the control
    house's lens (north-east) green, the switchgear's (east) amber, each unlit glass in the plate
    and a white-cut light pass the engine tints and lights (green while working, amber when the
    input fluid is missing). Round 5's two lenses were the kit's amber, unlit, in the same places;
  - the layers of spec 7, declared to the packers (DECL): the plate is the machine stopped (the
    melt and the helium unlit, the sight glass full and still, no bubbles in it); the riser and the
    sight glass are working layers, each with its light as a glow animation over it; the turning and
    rocking parts (flow meter, two gauges, float lever, compressor coupling) each a layer of its own;
  - no post-render roll-off of round 5's own (vp5_shoulder.py, vp5_roll.py): pack.py's highlight
    roll-off is the shared rig's now, on by default (spec 11);
  - the four directions are the whole machine turned a quarter turn under the one camera (spec 5);
    the pipe pictures are the model's own, in assembler 3's outline (spec 8), as round 1's model
    drew them;
  - the canvas centred on the entity origin (the contract's), where round 5's kit put the origin at
    (160, 208) of a 352 px square.

Units are tiles; north is +Y. Nothing here is adopted: the sheets move to graphics/ only on Liam's sign-off.
"""
import json
import math
import os
import random
import re
import sys

import bmesh
import bpy
from mathutils import Vector

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "kit"))
from vpb5_kit import *  # noqa: F401,F403,E402
import vpb5_kit as K5  # noqa: E402
import vpb3_kit as K  # noqa: E402
import vp4_glass as G  # noqa: E402
import contract  # noqa: E402  (tools/blender, on the path from vpb3_kit)
import rig  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0]
IDLE = "--idle" in argv
PORTS = "--ports" in argv
ICON = "--icon" in argv
COLLIDE = "--collide" in argv
SOUTH = argv[argv.index("--south") + 1] if "--south" in argv else "fixed"
assert SOUTH in ("fixed", "round5"), SOUTH


def _opt(name, default):
    return type(default)(argv[argv.index(name) + 1]) if name in argv else default


PI = math.pi
TAU = 2 * PI
NF = 24                             # spec 6.2 and 9: a 24-frame loop, two helium charges a loop
SPEED = _opt("--speed", 0.2)        # proposed (spec 9: "proposed at the model stage"): a charge a mining
                                    # operation, 1 s; the loop 2 s, 120 ticks, a frame every 5 ticks
CANVAS = (416, 416)                 # the origin at its centre; the head tank rises ~150 px over it and the
                                    # tower's shadow falls ~160 px east in the turned views
PORT_CANVAS = (320, 320)            # the pictures reach a tile outside every face
PLATE_SAMPLES = _opt("--samples", 80)          # round 5's (the kit's)
ANIM_SAMPLES = _opt("--anim-samples", 80)

MECH = ("meter", "gauge-line", "gauge-receiver", "float", "coupling")      # each its own layer
CONTENT = ("riser", "glass")        # working layers: what moves inside the glass
LENSES = ("lens-green", "lens-amber")
DECL = dict(
    footprint=(3, 3),
    directions="four",              # spec 5: the whole machine turned under one camera
    passes=[
        # the machine stopped: nothing lit, every moving part at frame 0, the sight glass full and still
        dict(name="idle", kind="plate", sheet="base"),
        dict(name="still", kind="still"),
        dict(name="shadow", kind="shadow", sheet="shadow"),
        # the two status lenses (Liam, 2026-10-20, after T07b): each a glow sprite, the lens lit in its
        # own colour minus the plate (draw_as_glow: seen by day and by night), and a white-cut light for
        # the halo the engine shows in the dark; the unlit lens is the plate's
        dict(name="lens-green-lit", kind="glow", over="idle", sheet="lens-working-glow"),
        dict(name="lens-amber-lit", kind="glow", over="idle", sheet="lens-no-fluid-glow"),
        dict(name="lens-green", kind="light", sheet="lens-working-halo"),
        dict(name="lens-amber", kind="light", sheet="lens-no-fluid-halo"),
    ],
    animations=[
        # the working loop, the whole machine lit, drawn only while working (round 5's arrangement: its
        # "working" layer). Spec 7's split -- the riser and the sight glass as layers with their light as
        # glow animations over them -- cannot be packed when the whole machine turns: facing south the
        # riser, the head tank's window and the sight glass are behind the tower, every frame of those
        # layers is empty, and pack.py refuses an empty layer (run1: "every frame of riser-east is empty")
        dict(name="working", frames=NF, motion="flow", working=True, animation_speed=SPEED),
    ],
    # one picture per face, on the middle tile of each; facing north the melt leaves by the north
    # face and the helium comes in by the south (spec 8), and turned, the same pictures serve
    ports=[dict(tile=(0, -1), face="N"), dict(tile=(1, 0), face="E"),
           dict(tile=(0, 1), face="S"), dict(tile=(-1, 0), face="W", neck=True)],
    cut=["E", "W"],                 # nothing of the machine drawn past its east and west edges
)

sc = K.sc
sc.cycles.samples = PLATE_SAMPLES
ROOT = K.ROOT

# ---------------------------------------------------------------- groups and assemblies
#   body       everything that stands still (the plate)
#   riser      the riser's melt core, its glass, its bubbles; the head tank's melt window and pane
#   glass      the helium sight glass's tube, backing, liquid and bubbles
#   meter, gauge-line, gauge-receiver, float, coupling   the moving parts of each layer
#   lens-green, lens-amber   the two status lenses
PART = {}
CUR = ["body"]
ASM = {}
_ASM = [None]
_NEXT = [0]
_finish0 = K._finish


def _finish(o, mat, bevel=0.012, smooth=False, parent=None):
    o = _finish0(o, mat, bevel, smooth, parent)
    PART[o.name] = CUR[-1]
    if _ASM[0] is None:
        _NEXT[0] += 1
    ASM[o.name] = _ASM[0] if _ASM[0] is not None else _NEXT[0]
    return o


K._finish = _finish


class grp:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        CUR.append(self.name)

    def __exit__(self, *a):
        CUR.pop()


class asm:
    """with asm(): every part built inside is one assembly (a unit, a valve, a pipe run)."""

    def __enter__(self):
        self.outer = _ASM[0] is not None
        if not self.outer:
            _NEXT[0] += 1
            _ASM[0] = _NEXT[0]

    def __exit__(self, *a):
        if not self.outer:
            _ASM[0] = None


def _assembled(fn):
    def wrapped(*a, **kw):
        with asm():
            return fn(*a, **kw)
    return wrapped


# every kit helper that builds a unit of several parts builds one assembly
for _n in ("foundation", "vent_collar", "nozzle", "valve", "he_line", "flow_meter", "he_gauge", "sight_tank",
           "lagged", "pipe", "bundle", "motor", "coupling", "vtank", "ladder", "manway_top", "head", "bolts",
           "id_panel", "hazard_tag", "bubbles", "stencil"):
    globals()[_n] = _assembled(globals()[_n])

# ---------------------------------------------------------------- the surfacing (run5's, before any part is built)
build_materials5(((0.45, 0.3), (2.6, 0.5), (3.0, 0.4)))


def _lens_material(name, hexc, coat=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb(hexc)
    b.inputs["Roughness"].default_value = 0.25
    b.inputs["Coat Weight"].default_value = coat
    K.M[name] = m
    K.GROUP[name] = ("status lenses", "#40FF40" if "green" in name else "#FFB000")
    return m


_lens_material("lens_green", "#4E7446")         # unlit green glass, as the kit's amber is unlit (#A88A50)
_lens_material("lens_amber", "#6E5426")         # T07: darker than the kit's #A88A50, which read lit in the sun
LIGHT_MAT = bpy.data.materials.new("lens_cut")   # the light pass: the lens alone, white
LIGHT_MAT.use_nodes = True
_nt = LIGHT_MAT.node_tree
_nt.nodes.remove(_nt.nodes["Principled BSDF"])
_em = _nt.nodes.new("ShaderNodeEmission")
_em.inputs["Color"].default_value = (1, 1, 1, 1)
_em.inputs["Strength"].default_value = 1.0
_nt.links.new(_em.outputs[0], _nt.nodes["Material Output"].inputs["Surface"])


LENS_LIT = {}
for _g, _hex in (("lens-green", "#46F05A"), ("lens-amber", "#FF9A12")):    # never white: no clipped px
    _m = bpy.data.materials.new(_g + "_lit")
    _m.use_nodes = True
    _b = _m.node_tree.nodes["Principled BSDF"]
    _b.inputs["Base Color"].default_value = rig.srgb(_hex)
    _b.inputs["Emission Color"].default_value = rig.srgb(_hex)
    _b.inputs["Emission Strength"].default_value = 2.6
    _b.inputs["Roughness"].default_value = 0.25
    LENS_LIT[_g] = _m


def lens(x, y, z, group):
    """A status lens (kit status_lens()'s holder and size), its glass in its own group."""
    with asm():
        cyl((x, y, z), 0.045, 0.05, "dark_steel", verts=16)
        with grp(group):
            sphere((x, y, z + 0.035), 0.032, "lens_green" if group == "lens-green" else "lens_amber", seg=12)


# ================================================================ the tower (round 5, vpb5_08_gas_lift_tower.py)
TX, TY = 0.0, 0.18          # the tower's axis, over the vent
HW = 0.34                   # the shaft's half-width
Z0, Z1 = 0.36, 2.92         # the shaft
ZT = 3.25                   # the head tank's axis
SLOT = 0.13                 # half the slot down the south face


def charge(t):
    """Helium let in in two charges a loop."""
    return max(pulse(t, 0.06, 0.3, 0.06), pulse(t, 0.56, 0.8, 0.06))


RATE = lambda t: 0.2 + charge(t)          # noqa: E731

# ---------------------------------------------------------------- footings: each unit on its own, no deck
foundation(-0.5, -0.36, 0.5, 0.7, 0.3, "refractory")                       # the tower's footing over the vent
vent_collar(TX, TY, 0.42, h=0.36)

# ---------------------------------------------------------------- the tower shaft, a slot down its south face
with asm():
    for sx in (-1, 1):
        box((TX + sx * HW, TY, (Z0 + Z1) / 2), (0.04, 2 * HW, Z1 - Z0), "iron", bevel=0.006)
    box((TX, TY + HW, (Z0 + Z1) / 2), (2 * HW, 0.04, Z1 - Z0), "iron", bevel=0.006)
    for sx in (-1, 1):
        w = HW - SLOT
        box((TX + sx * (SLOT + w / 2), TY - HW, (Z0 + Z1) / 2), (w, 0.04, Z1 - Z0), "iron", bevel=0.006)
        box((TX + sx * (SLOT + 0.015), TY - HW - 0.02, (Z0 + Z1) / 2), (0.03, 0.04, Z1 - Z0), "nickel", bevel=0.004)
    box((TX, TY, Z1 + 0.02), (2 * HW + 0.06, 2 * HW + 0.06, 0.05), "dark_steel")
    box((TX, TY + HW - 0.06, (Z0 + Z1) / 2), (2 * HW - 0.08, 0.02, Z1 - Z0), "dark")
    for sx in (-1, 1):
        for sy in (-1, 1):
            box((TX + sx * HW, TY + sy * HW, (Z0 + Z1) / 2), (0.07, 0.07, Z1 - Z0 + 0.04), "dark_steel", bevel=0.006)
    zb = Z0 + 0.25
    while zb < Z1 - 0.1:
        for sx in (-1, 1):
            box((TX + sx * (HW + 0.012), TY, zb), (0.025, 2 * HW + 0.05, 0.05), "dark_steel", bevel=0.004)
        box((TX, TY + HW + 0.012, zb), (2 * HW + 0.05, 0.025, 0.05), "dark_steel", bevel=0.004)
        for sx in (-1, 1):
            box((TX + sx * (SLOT + (HW - SLOT) / 2), TY - HW - 0.012, zb), (HW - SLOT, 0.025, 0.05), "dark_steel",
                bevel=0.004)
        for k in range(4):
            sphere((TX + HW + 0.027, TY - HW + 0.1 + k * 0.16, zb), 0.012, "bolt", seg=8)
        zb += 0.42
stencil((TX + HW + 0.025, TY - 0.05, 1.05), (0.012, 0.32, 0.12))
hazard_tag((TX - 0.22, TY - HW - 0.03, 0.55), 0.12, 0.08)

# ---------------------------------------------------------------- the glass riser in the slot: bubbles climbing with each charge
GX, GY = TX, TY - HW + 0.05
GZ0, GZ1 = Z0 + 0.12, Z1 - 0.08
melt("mt_riser", "flow", scale=1.6, k=2, soft=True, bright=1.0, axis="Z",
     fn=lambda t: 0.82 + 0.18 * charge(t))
with grp("riser"), asm():
    cyl((GX, GY, (GZ0 + GZ1) / 2), 0.085, GZ1 - GZ0, "mt_riser", verts=32, bevel=0)
    cyl((GX, GY, (GZ0 + GZ1) / 2), 0.115, GZ1 - GZ0, "glass", verts=32, bevel=0)
    # T07 (--collide): the bubbles climb between the end caps, not into them (round 5's ran GZ0 to GZ1)
    bubbles(GX, GY, GZ0 + 0.06, GZ1 - 0.06, 0.1, n=8, cols=3, r=0.048, per_loop=2,
            angles=(-PI / 2 - 0.7, -PI / 2, -PI / 2 + 0.7), ease=progress(RATE))
with asm():
    z = GZ0
    while z <= GZ1 + 0.01:
        cyl((GX, GY, z), 0.125, 0.05, "nickel", verts=32)
        z += (GZ1 - GZ0) / 3
    for sx in (-1, 1):
        cyl((GX + sx * 0.13, GY - 0.03, (GZ0 + GZ1) / 2), 0.012, GZ1 - GZ0, "bare", verts=8, bevel=0)
    cyl((GX, GY, GZ0 - 0.05), 0.15, 0.1, "dark_steel", verts=32)
    cyl((GX, GY, GZ1 + 0.05), 0.15, 0.1, "dark_steel", verts=32)
label(4, "glass riser: the helium's bubbles carry the melt up, faster in each charge", (GX, GY - 0.1, 1.5))

# ---------------------------------------------------------------- the head tank on the tower top
with asm():
    box((TX, TY, Z1 + 0.08), (1.02, 0.8, 0.06), "dark_steel")
    for sx in (-1, 1):
        for y in (TY - 0.38, TY + 0.38):
            box((TX + sx * 0.49, y, Z1 + 0.28), (0.025, 0.025, 0.36), "yellow", bevel=0.003)
        box((TX + sx * 0.49, TY, Z1 + 0.45), (0.025, 0.78, 0.025), "yellow", bevel=0.003)
    for xs in (-0.3, 0.3):
        box((TX + xs, TY, Z1 + 0.18), (0.1, 0.5, 0.16), "dark_steel")
with asm():
    cyl((TX, TY, ZT), 0.3, 0.86, "iron_dk", rot=(0, PI / 2, 0), verts=48)
    for xx, s in ((TX - 0.43, -1), (TX + 0.43, 1)):
        h_ = head(xx, TY, ZT, 0.3, 0.1, "iron_dk")
        h_.rotation_euler = (0, s * PI / 2, 0)
    for xx in (TX - 0.25, TX, TX + 0.25):
        cyl((xx, TY, ZT), 0.318, 0.05, "nickel", rot=(0, PI / 2, 0), verts=48)
    cyl((GX, GY, Z1 + 0.06), 0.1, 0.18, "heat", verts=24)                      # the riser's head into the tank
    melt("mt_tank", "flow", scale=7.0, k=1, bright=0.85, axis="X")
    with grp("riser"):
        box((TX - 0.12, TY - 0.285, ZT - 0.04), (0.3, 0.03, 0.07), "mt_tank", bevel=0.003)
    box((TX - 0.12, TY - 0.3, ZT - 0.04), (0.36, 0.02, 0.12), "dark_steel", bevel=0.004)
    with grp("riser"):
        box((TX - 0.12, TY - 0.305, ZT - 0.04), (0.3, 0.012, 0.07), "pane", bevel=0)
manway_top(TX - 0.12, TY + 0.05, ZT + 0.29, r=0.09)
label(5, "head tank: the helium breaks out of the melt", (TX - 0.2, TY, ZT + 0.2))

# the float chamber on the east end, its lever rocking with the level (one rock a charge)
with asm():
    cyl((TX + 0.62, TY, ZT - 0.05), 0.11, 0.42, "iron", verts=32)
    cyl((TX + 0.62, TY, ZT + 0.17), 0.13, 0.04, "dark_steel", verts=32)
pipe([(TX + 0.45, TY, ZT - 0.12), (TX + 0.56, TY, ZT - 0.12)], r=0.035, mat="bare", name="float chamber leg")
with grp("float"), asm():
    fp = pivot((TX + 0.62, TY - 0.13, ZT + 0.05), (0, 0, 0))
    box((0.0, -0.02, 0.0), (0.03, 0.05, 0.05), "dark_steel", parent=fp)
    box((0.18, -0.03, 0.0), (0.36, 0.022, 0.022), "bare", parent=fp)
    sphere((0.36, -0.03, 0.0), 0.05, "red", parent=fp)
    box((-0.05, -0.03, 0.0), (0.06, 0.022, 0.022), "bare", parent=fp)       # T07: was 0.12 long, into the tank head
    rock(fp, 0.32, cycles=2, axis="Y", phase=-0.1)
label(6, "float chamber: its lever rocks as each charge lifts the level", (TX + 0.8, TY - 0.15, ZT + 0.05))

# ---------------------------------------------------------------- the downcomer: the melt down to the north nozzle
out_in = nozzle("N", length=0.36, mat="heat")
# T07 (--collide): its foot runs down east of the skimmings bin, not through it (round 5's: (-0.6, 0.72, 0.9),
# (-0.45, 0.95, 0.55), 0.15 tile into the bin)
DOWN = [(TX - 0.45, TY, ZT - 0.05), (TX - 0.6, TY + 0.12, ZT - 0.3), (-0.62, 0.62, 2.0), (-0.36, 0.74, 0.9),
        (-0.3, 0.95, 0.55), (-0.15, 1.1, ZA), out_in]
lagged(DOWN, r=0.12, bands=0.25, name="downcomer (melt)")
with asm():
    for z in (1.6, 2.2):                    # T07: the bracket at 0.9 dropped with the downcomer's new foot
        box((-0.47, TY + 0.38, z), (0.14, 0.1, 0.04), "dark_steel")
label(10, "downcomer, lagged: the melt drops to the outlet", (-0.62, 0.65, 1.4))
label(11, "molten kamacite out, north", (0, 1.38, ZA))

# ---------------------------------------------------------------- the helium in: the grey-violet line to the sparger
in_in = nozzle("S", length=0.3, mat="bare")
# T07, the south join (Liam: "Fix in the model"): the inlet's footing carried out under the nozzle to the
# south edge (round 5's stopped at y -1.18, 0.32 tile short). Its grout ring ends at the edge.
foundation(-0.42, -1.18 if SOUTH == "round5" else -1.485, 0.42, -0.4, 0.1, anchors=False)
valve(0, -1.06, z=ZA - 0.1, h=0.36, r=0.06)
he_line([in_in, (0, -1.06, ZA), (0, -0.9, ZA)], name="helium in: nozzle to the flow meter")
with grp("meter"):
    flow_meter((0, -0.78, ZA), (0, 1, 0), r=0.12, turns=2, rate=RATE, facing=(-0.3, -0.55, 1))   # round 5: nudged off the glass
TEE = (0, -0.56, ZA)
with asm():
    cyl(TEE, 0.1, 0.16, "bare", rot=(PI / 2, 0, 0), verts=20)                   # the tee where the recovered gas joins
    cyl((0, -0.56, ZA + 0.14), 0.035, 0.2, "bare", verts=12)
with grp("gauge-line"):
    he_gauge((0, -0.58, ZA + 0.27), (0, -1, 0.7), live=lambda t: -0.4 + 1.2 * charge(t))
he_line([(0, -0.66, ZA), (0, -0.62, ZA)], name="helium: meter to tee")
# the sight tank between the tee and the sparger, east of the line: in at its foot, out of its head, down to the ring
G0_, G1_ = (0.31, -0.84, 0.3), (0.31, -0.84, 0.98)
ga, gb = axis_pts(G0_, G1_, 0.1)
with grp("glass"):
    sight_tank(G0_, G1_, stroke_pulse((0.06, 0.56), rise=0.05, fall=0.36), r=0.14)
he_line([(0, -0.48, ZA), (0.12, -0.5, 0.3), (0.22, -0.66, 0.2), ga, G0_], name="helium: tee to the sight glass")
he_line([G1_, gb, (0.22, -0.6, 1.0), (0.1, -0.38, 0.78), (0.04, -0.3, 0.5), (TX, TY - 0.44, 0.44)],
        name="helium: sight glass to the sparger ring")
label(12, "helium sight glass: the level drops and flushes pink at each charge", (0.27, -0.84, 0.65))
with asm():
    torus((TX, TY, 0.44), 0.44, 0.04, "he_lag", seg=48)                        # the sparger ring
    for i in range(8):
        a = 2 * PI * (i + 0.5) / 8
        torus((TX + 0.44 * math.cos(a), TY + 0.44 * math.sin(a), 0.44), 0.045, 0.01, "he_band", rot=(0, 0, 0), seg=16)
        cyl((TX + 0.4 * math.cos(a), TY + 0.4 * math.sin(a), 0.41), 0.02, 0.08, "bare", rot=(0, PI / 2, a), verts=8,
            bevel=0)
box((-0.24, -0.78, 0.3), (0.22, 0.4, 0.4), "green", bevel=0.02)            # the meter's transmitter
box((0.27, -0.47, 0.28), (0.24, 0.26, 0.36), "grey", bevel=0.02)            # the injection controller (round 4: north of the glass)
bundle([(-0.18, -0.7, 0.5), (-0.1, -0.74, 0.52), (-0.03, -0.78, ZA + 0.1)], cols=("black", "grey"), r=0.012,
       name="meter cable")
label(1, "helium-3 in, south: the grey-violet line", (0, -1.38, ZA))
label(2, "stop valve and flow meter: the meter races in each charge", (0, -0.85, 0.6))
label(3, "sparger ring round the tower's foot: helium blown into the melt", (TX - 0.4, TY - 0.3, 0.45))

# ---------------------------------------------------------------- recovery: tank -> compressor -> receiver -> tee
REC = [(TX + 0.2, TY + 0.0, ZT + 0.29), (TX + 0.3, TY - 0.08, ZT + 0.44), (TX + 0.44, TY - 0.42, ZT + 0.1),
       (0.44, -0.2, 2.0), (0.44, -0.24, 0.9), (0.62, -0.62, 0.7), (0.66, -0.82, 0.62)]
cyl((TX + 0.2, TY, ZT + 0.27), 0.06, 0.08, "bare", verts=16)               # the tank's gas offtake
he_line(REC, r=0.055, name="recovery: head tank down to the compressor")
with asm():
    for z in (1.0, 1.7, 2.3):
        box((TX + HW + 0.06, TY - 0.3, z), (0.08, 0.08, 0.035), "dark_steel")
label(7, "recovery line: the broken-out helium back down", (0.46, -0.24, 1.7))
# the compressor skid (SE): two cylinders on a crankcase, a motor and an exposed coupling
foundation(0.44, -1.47, 1.47, -0.42, 0.14)
with asm():
    # T07 (--collide): the crankcase 0.46 wide (round 5's 0.62), so the coupling between it and the motor is
    # in the open; round 5's stood inside the crankcase and the motor, unseen
    box((0.77, -0.95, 0.4), (0.46, 0.95, 0.52), "oxide", bevel=0.03)
    for yy in (-0.82, -1.08):
        cyl((0.85, yy, 0.78), 0.11, 0.3, "oxide", verts=24)
        cyl((0.85, yy, 0.95), 0.13, 0.05, "dark_steel", verts=24)
        bolts(0.85, yy, 0.98, 0.1, 6, r=0.012)
pv = motor(1.30, -0.95, 0.5, d=(-1, 0), s=0.85, mat="green")              # T07: was at x 1.25
with grp("coupling"):
    coupling(pv[0] - 0.062, pv[1], pv[2], 0.075, axis=(1, 0, 0), turns=3)
pipe([(0.85, -1.08, 0.98), (0.85, -0.95, 1.04), (0.85, -0.82, 0.98)], r=0.03, mat="bare",
     name="compressor head crossover")
label(8, "recovery compressor (its coupling turning)", (0.85, -0.95, 1.0))
hazard_tag((0.85, -1.425, 0.3), 0.3, 0.06)
# its discharge west, over the inlet, to the recovery receiver (SW)
he_line([(0.85, -0.95, 1.06), (0.7, -0.9, 1.12), (0.3, -0.42, 1.0), (-0.3, -0.42, 1.0), (-0.75, -0.62, 1.2),
         (-0.92, -0.9, 1.32)], r=0.05, name="recovery: compressor to the receiver")
foundation(-1.4, -1.4, -0.48, -0.48, 0.12)
vtank(-0.94, -0.94, 0.4, 1.2, mat="grey", bands=(0.4, 0.85), band_mat="he_edge", nozzle=None)
cyl((-0.94, -0.94, 1.32), 0.07, 0.12, "bare", verts=16)
with grp("gauge-receiver"):
    he_gauge((-0.94, -1.35, 0.62), (0, -1, 0.2), live=lambda t: 0.5 * math.sin(2 * PI * 3 * t))
id_panel((-0.94, -1.345, 0.9), 0.26, 0.12, stripe="yellow")
he_line([(-0.6, -0.86, 0.3), (-0.35, -0.6, 0.32), (-0.1, -0.56, ZA)], r=0.05,
        name="recovery: receiver back into the line at the tee")
label(9, "recovery receiver: the helium back into the line at the tee", (-0.94, -0.94, 1.3))

ROUTE_IN = [(0, -1.5, ZA), (0, -1.06, ZA), (0, -0.78, ZA), (0, -0.56, ZA), (0.12, -0.5, 0.3), (0.22, -0.66, 0.2), G0_,
            G1_, (0.22, -0.6, 1.0), (0.1, -0.38, 0.78), (0.04, -0.3, 0.5), (TX, TY - 0.44, 0.44),
            (TX + 0.31, TY - 0.31, 0.44), (TX + 0.44, TY, 0.44)]
route("he", ROUTE_IN)
route("he", [(TX, TY - 0.44, 0.44), (TX - 0.31, TY - 0.31, 0.44), (TX - 0.44, TY, 0.44)])
route("melt", [(TX, TY, 0.3), (GX, GY, GZ0), (GX, GY, GZ1), (GX, GY, ZT - 0.1), (TX - 0.43, TY, ZT - 0.05)] + DOWN[1:-1]
      + [(0, 1.5, ZA)])
route("spent", REC + [(0.85, -0.95, 1.06), (0.7, -0.9, 1.12), (0.3, -0.42, 1.0), (-0.3, -0.42, 1.0),
                      (-0.75, -0.62, 1.2), (-0.94, -0.94, 1.3), (-0.94, -0.94, 0.4), (-0.6, -0.86, 0.3),
                      (-0.35, -0.6, 0.32), (-0.1, -0.56, ZA)])

# ---------------------------------------------------------------- the control house (NE) and the switchgear (E)
foundation(0.48, 0.55, 1.42, 1.42, 0.12)
with asm():
    box((0.93, 0.965, 0.12 + 0.42), (0.86, 0.78, 0.84), "cream", bevel=0.03)
    box((0.93, 0.965, 0.98), (0.92, 0.84, 0.05), "dark_steel")
    for k in range(3):
        box((0.72 + 0.2 * k, 0.565, 0.7), (0.12, 0.02, 0.3), "dark_steel", bevel=0.003)
lens(1.26, 0.66, 1.02, "lens-green")              # T07: the control house's lens, green while working
with asm():
    box((0.82, 1.06, 1.12), (0.46, 0.46, 0.22), "grey", bevel=0.02)
    cyl((0.82, 1.06, 1.235), 0.17, 0.02, "dark_steel", verts=32)
    cyl((1.24, 1.24, 1.25), 0.025, 0.55, "bare", verts=8)
    box((1.24, 1.24, 1.5), (0.14, 0.03, 0.03), "red", bevel=0)

foundation(0.5, -0.4, 1.5, 0.53, 0.1)
with asm():
    box((1.02, 0.07, 0.4), (0.9, 0.86, 0.6), "grey", bevel=0.025)
    for k in range(3):
        cyl((0.78 + 0.22 * k, 0.32, 0.74), 0.045, 0.1, "ochre", verts=12)
        cyl((0.78 + 0.22 * k, 0.32, 0.81), 0.03, 0.06, "dark_steel", verts=12)
    for k in range(4):
        box((0.8 + 0.15 * k, -0.37, 0.4), (0.1, 0.02, 0.4), "dark_steel", bevel=0.003)
# T07: the switchgear's lens, amber when the fluid is missing. At its south-east corner (round 5's unlit lens
# stood at (1.3, 0.3)): there, turned to face west, it stood straight behind the tower and could not be seen,
# and at (1.32, -0.26) the recovery line hid it (3 px); here it shows 9-14 px in every direction
lens(1.34, -0.32, 0.72, "lens-amber")
bundle([(1.0, 0.32, 0.84), (0.7, 0.3, 1.2), (TX + HW + 0.02, TY + 0.05, 1.5)], cols=("black", "red", "grey"),
       r=0.018, name="switchgear to the tower's instruments")
bundle([(1.2, -0.36, 0.6), (1.28, -0.6, 0.75), (1.25, -0.95, 0.72)], cols=("black", "yellow"), r=0.014,
       name="switchgear to the compressor motor")
bundle([(0.93, 0.6, 0.9), (0.95, 0.5, 0.75), (0.95, 0.45, 0.7)], cols=("black", "grey"), r=0.012,
       name="control house to the switchgear")

# ---------------------------------------------------------------- the ladder (W), the tool chest, the skimmings bin
ladder(TX - HW - 0.1, TY - 0.1, 0.22, Z1 + 0.1, axis="y", mat="ochre")
with asm():
    for z in (1.0, 1.6, 2.2):
        torus((TX - HW - 0.18, TY - 0.1, z), 0.14, 0.012, "ochre", rot=(0, 0, 0), seg=24)
foundation(-1.5, -0.42, -0.52, 0.5, 0.1)
for k, yy in enumerate((-0.2, 0.25)):
    vtank(-1.05, yy, 0.22, 0.95 - 0.12 * k, mat=("green", "ochre")[k], bands=(0.45,), nozzle=None)
box((-0.65, 0.02, 0.3), (0.26, 0.7, 0.4), "dark_steel", bevel=0.02)      # T07: was at x -0.7, on the bottles' feet
foundation(-1.46, 0.52, -0.42, 1.46, 0.1)
with asm():
    box((-0.92, 0.95, 0.42), (0.86, 0.8, 0.64), "oxide", bevel=0.025)
    for sx, sy, w, d in ((0, -0.38, 0.9, 0.06), (0, 0.38, 0.9, 0.06), (-0.42, 0, 0.06, 0.82), (0.42, 0, 0.06, 0.82)):
        box((-0.92 + sx, 0.95 + sy, 0.76), (w, d, 0.06), "dark_steel", bevel=0.006)
    box((-0.92, 0.95, 0.7), (0.78, 0.72, 0.04), "slag", bevel=0)
    box((-0.92, 1.35, 0.98), (0.86, 0.04, 0.4), "dark_steel", bevel=0.01)
    box((-0.56, 1.3, 0.98), (0.03, 0.03, 0.42), "bare", bevel=0)
hazard_tag((-0.92, 0.55, 0.4), 0.6, 0.07)
stain(0.4, -0.3, 0.25, 0.1)
stain(-0.3, 1.2, 0.2, 0.08)

# ================================================================ run5's finish, as round 5 rendered it
K.WORLD = K5.WORLD5
K5.catcher_unlit()
K5.fix_melt()
K5.soften_windows()
K5.satin_floor()
SUN = rig.sun(K.SUN_E)
SUN.data.color = (1.0, 0.94, 0.82)
BG = sc.world.node_tree.nodes["Background"].inputs["Strength"]
BG.default_value = K.WORLD
OBJS = K.OBJS
STAINS = K.STAINS


# ---------------------------------------------------------------- the pose
def set_pose(f, melt_lit=False, he_lit=False, glass_idle=False):
    """Every part at frame f of the working loop; the melt and the helium lit or not; the sight glass
    at its idle (full, still, no bubbles) when glass_idle."""
    t = (f % NF) / NF
    K.pose(t, True)
    if glass_idle:
        for p_ in G.TANK_POSES:
            p_(0.0, False)
    if not melt_lit:
        for sock, _, _ in K.GLOWS:
            sock.default_value = 0.0
    if not he_lit:
        for node in G.HE_EMIT:
            node.outputs[0].default_value = 0.0
    POSE_HIDE.clear()
    POSE_HIDE.update(o.name for o in OBJS if o.hide_render and any(m.name.startswith("he_bubble") for m in o.data.materials))
    bpy.context.view_layer.update()


POSE_HIDE = set()


# ---------------------------------------------------------------- the moving parts, found
def _moving():
    m0, moving = {}, set()
    for f in range(NF):
        set_pose(f)
        for o in OBJS:
            m = o.matrix_world.copy()
            if o.name not in m0:
                m0[o.name] = (m, o.hide_render)
            elif any(abs(m[i][j] - m0[o.name][0][i][j]) > 1e-6 for i in range(4) for j in range(4)) \
                    or o.hide_render != m0[o.name][1]:
                moving.add(o.name)
    set_pose(0)
    return moving


MOVING = _moving()
GLASS_MATS = ("he_glass", "he_liquid", "he_bubble", "dark")
for o in OBJS:
    g = PART[o.name]
    if g in MECH and o.name not in MOVING:
        PART[o.name] = "body"               # the meter's body, a gauge's case: they stand still
    if g == "glass" and not any(m.name.startswith(GLASS_MATS) for m in o.data.materials):
        PART[o.name] = "body"               # the tank's flanges, caps, rods and stubs
stray = [o.name for o in OBJS if o.name in MOVING and PART[o.name] == "body"]
assert not stray, f"moving parts in no layer: {stray}"
GROUPS_ALL = ("body",) + CONTENT + MECH + LENSES


def members(*groups):
    return [o for o in OBJS if PART[o.name] in groups]


# ---------------------------------------------------------------- the pipe pictures (round 1's model, in assembler 3's outline)
VANILLA = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity/assembling-machine-3")
EDGE = 1.5
E3 = EDGE - 0.005
H_AXIS_V = 1.0 / 64
V_AXIS_U = 0.5 / 64
H_RING_R = 26 / 64 / 1.118
V_RING_R = 25.5 / 64
HC = 0.66                    # the south picture's plate stands to the nozzle's top (round 1's: its rim, 0.56)
FITTINGS = {}


def rivet(loc, r=0.015):
    return sphere(loc, r, "bolt", scale=(1, 1, 0.7), seg=8)


def nut(loc, r, h, rot):
    o = cyl(loc, r, h, "bare", rot=rot, verts=6, bevel=0)
    o.rotation_euler.rotate_axis("Z", random.uniform(0, PI / 3))
    return o


def vanilla_mask(face, tile):
    stem = os.path.join(VANILLA, f"assembling-machine-3-pipe-{face}")
    bx, by = (float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)",
                                           open(stem + ".lua").read()).groups())
    img = bpy.data.images.load(stem + ".png", check_existing=True)
    w, h = img.size
    px = list(img.pixels)
    drawn = {(i, j) for j in range(h) for i in range(w) if px[((h - 1 - j) * w + i) * 4 + 3] > 127 / 255}
    n8 = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)]
    grown = {(i + a, j + b) for i, j in drawn for a, b in n8}
    drawn = {(i, j) for i, j in grown if all((i + a, j + b) in grown for a, b in n8)} | drawn
    dx, dy = contract.FACES[face]
    tx, ty = tile[0] + dx, tile[1] + dy
    return drawn, (tx + bx / 32) * 64 - w / 2, (ty + by / 32) * 64 - h / 2


def slab(face, tile, lift, mat="dark_steel"):
    drawn, x0, y0 = vanilla_mask(face, tile)
    me = bpy.data.meshes.new(f"slab-{face}")
    bm = bmesh.new()
    corners = {}

    def corner(i, j):
        if (i, j) not in corners:
            corners[(i, j)] = bm.verts.new(lift((x0 + i) / 64, -(y0 + j) / 64))
        return corners[(i, j)]
    for i, j in drawn:
        bm.faces.new((corner(i, j + 1), corner(i + 1, j + 1), corner(i + 1, j), corner(i, j)))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(f"slab-{face}", me)
    sc.collection.objects.link(o)
    return _finish(o, mat, 0)


def fitting(p, cap):
    face, tile = p["face"], p["tile"]
    g = f"{'cover' if cap else 'port'}-{face}"
    first = len(OBJS)
    cx, cy = tile[0], -tile[1]
    if face == "S":
        yw = -(E3 + 0.035)

        def lift(u, v):
            z = 2 * (v - yw)
            return Vector((u, yw, z)) if z <= HC else Vector((u, yw + (v - yw - HC / 2), HC + 0.004))
        slab(face, tile, lift, "dark_steel")
        ax = (PI / 2, 0, 0)
        x = cx + V_AXIS_U
        for k in range(11):
            rivet((x - 0.36 + 0.072 * k, yw - 0.012, HC - 0.06), 0.017)
        for z in (0.12, 0.36):
            for sx_ in (-0.39, 0.39):
                rivet((x + sx_, yw - 0.012, z), 0.017)
        ye = -(EDGE + 0.03) - ZA / 2
        annulus((x, yw - 0.03, ZA), 0.3, 0.42, 0.05, "bare", rot=ax)
        for k in range(14):
            t = TAU * k / 14
            rivet((x + 0.37 * math.cos(t), yw - 0.06, ZA + 0.37 * math.sin(t)), 0.016)
        cyl((x, (yw + ye) / 2, ZA), 0.28, abs(ye - yw), "bare", rot=ax, verts=48, bevel=0.0)
        cyl((x, ye + 0.03, ZA), V_RING_R - 0.02, 0.06, "bare", rot=ax, verts=48, bevel=0.01)
        for k in range(8):
            t = TAU * (k + 0.5) / 8
            nut((x + 0.33 * math.cos(t), ye - 0.002, ZA + 0.33 * math.sin(t)), 0.02, 0.014, ax)
        cyl((x, ye - 0.003, ZA), 0.2 if not cap else V_RING_R - 0.06, 0.006, "dark" if not cap else "bare",
            rot=ax, verts=32, bevel=0.0)
    elif face == "N":
        yw = E3 + 0.035

        def lift(u, v):
            return Vector((u, yw, 2 * (v - yw)))
        slab(face, tile, lift, "dark_steel")
        for k in range(7):
            t = 0.35 + (PI - 0.7) * k / 6
            u, v = cx + V_AXIS_U + 0.3 * math.cos(t), EDGE + 0.2 * math.sin(t)
            rivet((u, yw - 0.015, 2 * (v - yw)), 0.016)
    else:
        sgn = 1 if face == "E" else -1
        x0 = sgn * (EDGE - 0.28)

        def lift(u, v):
            z = ZA - sgn * 1.6 * (u - x0)
            return Vector((u, v - z / 2, z))
        slab(face, tile, lift, "dark_steel")
        ya = cy + H_AXIS_V - ZA / 2
        ax = (0, PI / 2, 0)
        xf = sgn * (EDGE - 0.03)
        cyl(((x0 + xf) / 2, ya, ZA), 0.24, abs(xf - x0), "bare", rot=ax, verts=48, bevel=0.0)
        cyl((xf, ya, ZA), H_RING_R - 0.02, 0.045, "bare", rot=ax, verts=48, bevel=0.006)
        for k in range(8):
            t = TAU * (k + 0.5) / 8
            nut((xf - sgn * 0.025, ya + 0.27 * math.cos(t), ZA + 0.27 * math.sin(t)), 0.018, 0.012, ax)
    FITTINGS[g] = OBJS[first:]


# ---------------------------------------------------------------- --collide (round 1's model's check)
DEEP = 0.03
DETAIL_MATS = {"bolt", "seam", "stencil", "hazard", "label", "gauge", "ceramic", "needle", "red", "yellow", "brass",
               "dark", "lamp", "oil", "pane", "rubber", "he_band", "he_band4", "he_edge", "lens_green", "lens_amber"}
# meant contacts of a moving part, (group, part, other part, why): printed as "meant" lines, which a
# render.sh --collide counts as clashes unless allowed; each listed here is also printed with its reason
MEANT = [
    (r"^riser$", r"\[slag\]", r"\[nickel\]",
     "a bubble passing behind one of the riser's three band clamps (each modelled as a solid disc round the glass)"),
]
# fixed parts that meet by design, (part a, part b, why), matched both ways on the parts' descriptions
_F = r"^Cube[.0-9]*\[(refractory|dark_steel)\] at \([-+.0-9]+,[-+.0-9]+,0\.(0\d|1[0-5])\)"   # a footing slab or its grout
MEANT_FIXED = [
    (r"\[refractory\] at \(\+0\.00,\+0\.17,0\.15\)", r"\[dark_steel\] at \([-+]0\.00,\+0\.18,0\.03\)",
     "the vent collar's foot ring cast into the tower's footing"),
    (r"\[refractory\] at \(\+0\.00,\+0\.17,0\.15\)", r"\[ochre\] at \(-0\.44,",
     "the ladder's feet set into the tower's footing"),
    (_F, _F, "two footings poured against each other"),
    (r"\[dark_steel\] at \([-+]0\.34,[-+]0\.(16|52),1\.64\)", r"\[he_lag\] at \([-+]0\.00,\+0\.18,0\.44\)",
     "the sparger ring led through the shaft's corner posts at their foot (round 5's ring, radius 0.44)"),
    (r"\[dark_steel\] at \([-+]0\.00,-0\.11,0\.43\)", r"\[he_lag\] at \([-+]0\.00,\+0\.18,0\.44\)",
     "the sparger ring let into the riser's foot, which it feeds"),
    (r"\[dark_steel\] at \([-+]0\.00,-0\.11,2\.89\)", r"\[heat\] at \(\+0\.00,-0\.11,2\.98\)",
     "the riser's head let through its top cap into the tank"),
    (r"\[dark_steel\] at \([-+]0\.30,\+0\.18,3\.10\)", r"\[iron_dk\] at \([-+]0\.00,\+0\.18,3\.25\)",
     "the head tank sitting in its two saddles"),
]


def seated(a, b, inside_pts, runs):
    for x, y in ((a, b), (b, a)):
        for xr, yr, why in MEANT_FIXED:
            if re.search(xr, x.desc) and re.search(yr, y.desc):
                return why
    if ASM.get(a.o.name) == ASM.get(b.o.name):
        return "one assembly's own parts"
    for x, y in ((a, b), (b, a)):
        if x.mat in DETAIL_MATS or x.mat.startswith("cable_"):
            return f"a {x.mat} detail on its host"
        if x.size < 0.16:
            return "a small fitting on its host"
    for x, y in ((a, b), (b, a)):
        ends = runs.get(ASM.get(x.o.name))
        if ends:
            pts = inside_pts(x, y) or inside_pts(y, x)
            if pts and all(min((p_ - ends[0]).length, (p_ - ends[1]).length) < 0.45 for p_ in pts):
                return "a pipe or line's end let into what it serves"
    return None


def collide_check():
    """Every moving part in every frame against every fixed part and every other layer's moving
    parts, then the fixed model part against part (round 1's model's, the circulator's). The model
    turns rigidly for east, south and west, so facing north is every direction."""
    from mathutils.bvhtree import BVHTree
    lines = []

    def out(s_):
        print(s_, flush=True)
        lines.append(s_)
    RI = ROOT.matrix_world.inverted()
    runs = {}
    idx = {o.name: i for i, o in enumerate(OBJS)}
    for name, a_, b_, (i0, i1) in K.PIPES:
        if i0 < len(OBJS):
            runs[ASM.get(OBJS[i0].name)] = (Vector(a_), Vector(b_))

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
        d = Vector((0.5774, 0.5771, 0.5777))
        n, o = 0, p_.copy()
        for _ in range(64):
            hit = tree.ray_cast(o, d)
            if hit[0] is None:
                break
            n += 1
            o = hit[0] + d * 1e-5
        return n % 2 == 1

    class Part:
        def __init__(self, o):
            self.o = o
            self.vs, ps = world_mesh(o)
            self.box = aabb(self.vs) if self.vs else None
            self.tree = BVHTree.FromPolygons(self.vs, ps) if ps else None
            c = RI @ (sum(self.vs, Vector()) / len(self.vs)) if self.vs else Vector()
            lo, hi = (RI @ Vector(self.box[0]), RI @ Vector(self.box[1])) if self.vs else (c, c)
            self.lo = Vector((min(lo.x, hi.x), min(lo.y, hi.y), min(lo.z, hi.z)))
            self.hi = Vector((max(lo.x, hi.x), max(lo.y, hi.y), max(lo.z, hi.z)))
            self.c = c
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

    meshes = [o for o in OBJS if o.type == "MESH" and o not in STAINS]
    out(f"COLLIDE {len(meshes)} parts, {len([o for o in meshes if o.name in MOVING])} moving; frames 0-{NF - 1}")
    fixed_cache, hits = {}, {}
    for f in range(NF):
        set_pose(f)
        mv = [o for o in meshes if o.name in MOVING and not o.hide_render]
        fx = [o for o in meshes if o.name not in MOVING]
        for o in fx:
            if o.name not in fixed_cache:
                fixed_cache[o.name] = Part(o)
        mparts = [(PART[o.name], Part(o)) for o in mv]
        for lab, a in mparts:
            for o in fx:
                b = fixed_cache[o.name]
                kind = clash(a, b)
                if kind and ASM.get(a.o.name) != ASM.get(o.name):
                    hits.setdefault((lab, a.desc, b.desc, kind), []).append(f)
                elif kind:
                    hits.setdefault((lab, a.desc, b.desc, kind + " (own assembly)"), []).append(f)
        for i, (la, a) in enumerate(mparts):
            for lb_, b in mparts[i + 1:]:
                if la == lb_:
                    continue
                kind = clash(a, b)
                if kind:
                    hits.setdefault((la, a.desc, lb_ + ": " + b.desc, kind), []).append(f)
    n_meant = n_clash = 0
    meant_lines = []
    for (g, ad, bd, kind), fs in sorted(hits.items(), key=lambda kv: kv[0]):
        why = "its own assembly's part: a bubble in its melt and glass, a needle on its face, the liquid in its tank" if kind.endswith("(own assembly)") else \
            next((w for gr, ar, br, w in MEANT if re.search(gr, g) and re.search(ar, ad) and re.search(br, bd)), None)
        fr = f"{fs[0]}-{fs[-1]}" if fs == list(range(fs[0], fs[-1] + 1)) else ",".join(map(str, fs))
        if why:
            n_meant += 1
            meant_lines.append(f"meant moving [{g}] {ad} x {bd}: {kind}, frames {fr}  ({why})")
        else:
            n_clash += 1
            out(f"COLLIDE CLASH moving [{g}] {ad} x {bd}: {kind}, frames {fr}")
    out(f"COLLIDE moving: {n_clash} clashes, {n_meant} meant contacts (collide-model.txt)")

    set_pose(0)
    fixed = [fixed_cache[o.name] for o in meshes if o.name in fixed_cache]

    def depth(a, b):
        d = 0.0
        for v in a.vs:
            if meet(b.box, (v, v)) and inside(b.tree, v):
                hit = b.tree.find_nearest(v)
                if hit[0] is not None:
                    d = max(d, (RI.to_3x3() @ (hit[0] - v)).length)
        return d

    def inside_pts(x, y):
        return [RI @ v for v in x.vs if meet(y.box, (v, v)) and inside(y.tree, v)]
    pairs, n_real, n_deep = [], 0, 0
    for i, a in enumerate(fixed):
        for b in fixed[i + 1:]:
            kind = clash(a, b)
            if not kind:
                continue
            why = seated(a, b, inside_pts, runs)
            dp = max(depth(a, b), depth(b, a)) if why is None else 0.0
            tag = "seated" if why else ("REAL" if dp > DEEP else "touch")
            n_real += tag == "REAL"
            n_deep += tag == "touch"
            pairs.append((tag, -dp, f"{tag} {a.desc} x {b.desc}: {kind}, {dp:.3f} deep" + (f"  ({why})" if why else "")))
            if tag == "REAL":
                out(f"COLLIDE REAL fixed {a.desc} x {b.desc}: {kind}, {dp:.3f} deep")
    order = {"REAL": 0, "touch": 1, "seated": 2}
    with open(os.path.join(OUT, "collide-model.txt"), "w") as f_:
        f_.write("\n".join(meant_lines) + "\n\n")
        f_.write("\n".join(l_ for _, _, l_ in sorted(pairs, key=lambda p_: (order[p_[0]], p_[1], p_[2]))) + "\n")
    out(f"COLLIDE model: {n_real} clashes (REAL: reach more than {DEEP} tile into each other and no rule explains "
        f"them); {len(fixed)} fixed parts, {len(pairs)} touching pairs, {n_deep} touch at under {DEEP} "
        f"(collide-model.txt)")
    with open(os.path.join(OUT, "collide.txt"), "w") as f_:
        f_.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- render helpers
def setup(visible=(), holdouts=(), unseen=(), ground=False):
    """Show, hold out or hide each group; a part the pose hid (a bubble above the glass's level, or
    every bubble in the idle glass) stays hidden."""
    for o in OBJS:
        g = PART[o.name]
        o.hide_render = not (g in visible or g in holdouts or g in unseen) or o.name in POSE_HIDE
        o.is_holdout = g in holdouts
        o.visible_camera = g not in unseen
    GROUND.hide_render = not ground


def window(objs, pad=(0.12, 0.12, 0.12, 0.12)):
    """The render border (sprite px) round objs' projection over every frame, padded (left, down,
    right, up, tiles)."""
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
    x0 = max(0, int(W / 2 + (min(xs) - pad[0]) * ppt))
    x1 = min(W, int(W / 2 + (max(xs) + pad[2]) * ppt) + 1)
    y0 = max(0, int(Hc / 2 - (max(ys) + pad[3]) * ppt))
    y1 = min(Hc, int(Hc / 2 - (min(ys) - pad[1]) * ppt) + 1)
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


GLASSY = ("glass", "pane", "he_glass", "he_liquid", "he_bubble")     # transparent: hidden, not held out, in a light pass


def lights_off(off):
    SUN.hide_render = off
    BG.default_value = 0.0 if off else K.WORLD
    BOUNCE.hide_render = off


def lens_cut(group, on, mat=None):
    for o in members(group):
        o.data.materials[0] = (mat or LIGHT_MAT) if on else K.M["lens_green" if group == "lens-green" else "lens_amber"]


def mask_pass(path, groups):
    """A white silhouette of `groups` with everything else held out, no light: the stray-light map's mask."""
    keep = {}
    for o in members(*groups):
        keep[o.name] = [m for m in o.data.materials]
        for i in range(len(o.data.materials)):
            o.data.materials[i] = LIGHT_MAT
    lights_off(True)
    setup(visible=groups, holdouts=tuple(g for g in GROUPS_ALL if g not in groups))
    rig.render(path)
    lights_off(False)
    for o in members(*groups):
        for i, m in enumerate(keep[o.name]):
            o.data.materials[i] = m


# ---------------------------------------------------------------- --collide
if COLLIDE:
    collide_check()
    print("done")
    sys.exit(0)

# ---------------------------------------------------------------- --ports
if PORTS:
    random.seed(4)
    for p_ in DECL["ports"]:
        fitting(p_, cap=False)
        fitting(p_, cap=True)
    BOUNCE = rig.bounce_ground()
    contract.declare(OUT, canvas=PORT_CANVAS, **DECL)
    rig.camera(*PORT_CANVAS)
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
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()

# ---------------------------------------------------------------- --icon
if ICON:
    # spec 15: redone from the model -- the whole tower, facing north, working: the melt in the riser
    # and the helium in its glass lit (a charge's peak), on the plate's camera, framed to fill the square
    sc.cycles.samples = 128
    cam = rig.camera(1024, 1024, ss=1)
    set_pose(4, melt_lit=True, he_lit=True)
    for o in OBJS:
        o.hide_render = o in STAINS
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

# ---------------------------------------------------------------- the passes, per direction
rig.camera(*CANVAS)
if not IDLE:
    contract.declare(OUT, canvas=CANVAS, **DECL)
MASKS = os.path.join(os.path.dirname(os.path.abspath(OUT)), "masks")
os.makedirs(MASKS, exist_ok=True)
OTHERS = lambda *gs: tuple(g for g in GROUPS_ALL if g not in gs)      # noqa: E731
LIGHT_FRAMES = range(0, NF, 2)
for d in contract.each_direction(ROOT, DECL["directions"]):
    def path(stem, d=d):
        return os.path.join(OUT, contract.named(stem, d) + ".png")
    bpy.context.view_layer.update()
    no_border()
    sc.cycles.samples = PLATE_SAMPLES
    # the plate: the machine stopped -- nothing lit, every moving part at frame 0, the glass full and still
    set_pose(0, glass_idle=True)
    setup(visible=GROUPS_ALL)
    rig.render(path("idle"))
    rig.render(path("still"))
    for lg in LENSES:
        lens_cut(lg, True, LENS_LIT[lg])
        rig.render(path(lg + "-lit"))
        lens_cut(lg, False)
    if IDLE:
        set_pose(0, melt_lit=True, he_lit=True)
        setup(visible=GROUPS_ALL)
        rig.render(path("working-lit"))
        continue
    setup(visible=GROUPS_ALL, ground=True)
    for o in OBJS:
        o.visible_camera = False
    rig.render(path("shadow"))
    for lg in LENSES:
        setup(visible=(lg,), holdouts=OTHERS(lg))
        for o in OBJS:                      # a pane held out still leaves faint alpha the engine would tint
            if o.is_holdout and any(m.name.startswith(GLASSY) for m in o.data.materials):
                o.hide_render = True
        lens_cut(lg, True)
        rig.render(path(lg))
        lens_cut(lg, False)
    sc.cycles.samples = ANIM_SAMPLES
    # the working loop: the whole machine, the melt and the helium lit
    for f in range(NF):
        set_pose(f, melt_lit=True, he_lit=True)
        setup(visible=GROUPS_ALL)
        rig.render(path(contract.frame("working", f)))
    # not packed: the stray-light check's light alone (sun and sky off) and the masks of where light may be
    lights_off(True)
    for f in LIGHT_FRAMES:
        set_pose(f, melt_lit=True, he_lit=True)
        setup(visible=GROUPS_ALL)
        rig.render(os.path.join(MASKS, f"light-{d}-{f:02d}.png"))
    lights_off(False)
    set_pose(0)
    for g in CONTENT:
        mask_pass(os.path.join(MASKS, f"{g}-{d}.png"), (g,))
    set_pose(0)

with open(os.path.join(OUT, "..", "model.json"), "w") as f_:
    json.dump(dict(frames=NF, speed=SPEED, south=SOUTH, sun=K.SUN_E, world=K.WORLD,
                   samples=dict(plate=PLATE_SAMPLES, anim=ANIM_SAMPLES),
                   groups={g: len(members(g)) for g in GROUPS_ALL}, moving=len(MOVING),
                   pipes=K.check_ends()), f_, indent=1)
print("done")
