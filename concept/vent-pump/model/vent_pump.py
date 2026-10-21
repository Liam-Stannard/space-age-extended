"""Vent Pump (sae-vent-pump): the Gas Lift Tower, round 5 variant (a) -- the shipping model (T07, T07c).

  BLENDER=<blender 5> tools/blender/render.sh concept/vent-pump/model/vent_pump.py <out-dir> --ports --icon
  (or directly: blender -b --python vent_pump.py -- <out-dir> [--idle | --ports | --icon | --collide]
                [--samples N] [--anim-samples N] [--only north,east] [--south round5])

  --idle     plate, still, lens and working-lit frame 0 per direction only: the quick loop for the finish
  --only D,D render only these directions (tuning; never for a pack: pack.py wants all four)
  --ports    the four pipe pictures and their caps, port-<face>.png and cover-<face>.png
  --icon     icon.png: the whole tower facing north, working (the melt and the helium lit)
  --collide  no render: in every direction, every moving part in every frame against every other part,
             and every fixed part against every other, by BVH; collide.txt and collide-model.txt in <out-dir>
  --south round5   the south footing as round 5 had it (the join's "before", for the review only)
  --ends     no render: every run's two ends, where they sit and on the sprite (ends.json), for the ends' crops
  --embers-only    T07d tuning: render the ember layer (embers, embers-light) alone, nothing declared
  --ember-check <renders dir>   no render: the holdout check of the packed-to-be ember frames (sprite size,
             render.sh's <out-dir>/renders): for every frame and direction, every pixel the embers draw is cast
             back into the scene as 4 x 4 rays through it; a pixel fails when the embers draw it (alpha 16 or
             more) and no ray of it meets a spark before the machine, though one meets a spark behind a part
             (a spark drawn over a part nearer the camera). Writes <out-dir>/ember-check.json, and per
             direction near-<d>.pgm: the parts nearer the camera than the bin's slag by 0.1 tile or more
             (the "before" count for T07c's PIL embers)

Spec: concept/vent-pump/building-spec-vent-pump.md (written 9e067a3): the Gas Lift Tower, round 5,
variant (a) "Warmer paints" (Liam, 2026-10-20). The geometry and the surfacing are round 5's
(options/round-5/vpb5_08_gas_lift_tower.py --variant a), built with its kit, copied unchanged into
kit/ (each kit file's first line says what the copy changed).

T07 (2026-10-20) changed from round 5: the south join (the inlet's footing carried to the south edge);
the two status lenses (control house green, switchgear amber: a glow and a white-cut light each); the
layers declared to the packers; no roll-off of round 5's own (pack.py's); the canvas on the entity origin.

T07c (2026-10-21), Liam on T07 (Q5): "Handle it how factorio handles it for the chemical plant. A
variation of the mode which shows it still". Vanilla's chemical plant (base/prototypes/entity/entities.lua,
chemical-plant; graphics/entity/chemical-plant/) draws a base, two animation layers and a shadow for each
of its four directions, and in every one its vessel's big window faces the camera: what turns with the
building is the plumbing round it (its four pipe connections and their runs), and its liquid and foam
windows are working_visualisations with a sprite and a shift per direction (north_animation ...
west_animation), its smoke an animation placed per direction (north_position ...). So here, per direction:

  - the core faces the camera in all four: the tower with its glass riser, the head tank with its melt
    window, the float chamber, the ladder, the sparger ring, the tower's footing (CORE_PARTS). It stands
    where the quarter turn puts the tower's axis (AX), and is never turned;
  - the periphery turns with the fluid boxes, as T07 turned the whole machine: the inlet run (nozzle,
    stop valve, meter, tee), the units on their footings (compressor, receiver, control house,
    switchgear, gas bottles, skimmings bin) and the outlet nozzle. West is east's periphery mirrored
    (turned, west put the switchgear and its amber lens behind the tower);
  - the instruments face the camera wherever the periphery puts them: the sight glass (its dark backing
    behind it), the flow meter's dial, the two gauges, the receiver's ID plate;
  - the lines between the core and the periphery are routed per direction (ROUTES): the downcomer from
    the head tank to the outlet nozzle, the recovery line from the tank's gas offtake to the compressor,
    the helium from the sight glass to the sparger ring, the switchgear's cable to the tower, and, east
    and west, the compressor's discharge to the receiver (turned, it ran through the ladder);
  - south only: the sight glass stands east of the tower (turned, it stood behind it), with the
    injection controller; the tool chest takes its old place.

  And the layers are spec 7's split, which T07 could not pack when facing south hid the glass: the
  plate is the machine stopped (the melt and the helium unlit, the glass full and still, no moving
  part); "riser" (the riser's melt, glass and bubbles, the head tank's window) and "glass" (the
  sight glass) are working layers, each with its light over it as a glow animation (riser-light,
  glass-light: the light alone, the sun and sky off, everything else held out, so no light falls
  anywhere but on the melt and the glass); the turning and rocking parts one layer, "mech".

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
from mathutils import Matrix, Vector

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
EMBERS_ONLY = "--embers-only" in argv          # T07d tuning: the ember layer alone, no declaration
EMBERS_FREE = "--embers-free" in argv          # with --embers-only: nothing held out (the check's "without")
EMBER_CHECK = argv[argv.index("--ember-check") + 1] if "--ember-check" in argv else None
SOUTH = argv[argv.index("--south") + 1] if "--south" in argv else "fixed"
assert SOUTH in ("fixed", "round5"), SOUTH


def _opt(name, default):
    return type(default)(argv[argv.index(name) + 1]) if name in argv else default


PI = math.pi
TAU = 2 * PI
NF = 24                             # spec 6.2 and 9: a 24-frame loop, two helium charges a loop
SPEED = _opt("--speed", 0.2)        # Liam, 2026-10-21: "0.2" -- a charge a mining operation, the loop 2 s
CANVAS = (416, 416)                 # the origin at its centre
PORT_CANVAS = (320, 320)            # the pictures reach a tile outside every face
PLATE_SAMPLES = _opt("--samples", 80)          # round 5's (the kit's)
ANIM_SAMPLES = _opt("--anim-samples", 80)
DIRS = ("north", "east", "south", "west")
ONLY = tuple(_opt("--only", ",".join(DIRS)).split(","))
assert all(d in DIRS for d in ONLY), ONLY

MECH = ("meter", "gauge-line", "gauge-receiver", "float", "coupling")      # the moving parts' groups: one layer, mech
CONTENT = ("riser", "glass")        # working layers: what moves inside the glass
LENSES = ("lens-green", "lens-amber")
DECL = dict(
    footprint=(3, 3),
    directions="four",              # each direction its own variation (the docstring); none is turned whole
    passes=[
        # the machine stopped: nothing lit, no moving part, the sight glass full and still
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
        # spec 7: the riser (the melt climbing its glass, the head tank's window) and the helium's sight
        # glass, each a working layer drawn over the plate, its light over it as a glow
        dict(name="riser", frames=NF, motion="flow", working=True, animation_speed=SPEED),
        dict(name="riser-light", kind="glow", over="riser", frames=NF, motion="flow"),
        dict(name="glass", frames=NF, motion="flow", working=True, animation_speed=SPEED),
        dict(name="glass-light", kind="glow", over="glass", frames=NF, motion="flow"),
        # the turning and rocking parts (spec 6.2: the meter, the two gauges, the float lever, the coupling), one
        # layer, part of the stopped machine at frame 0. One, not one each: each variation hides some of them
        # (facing south the meter and the line gauge stand behind the tower, east the receiver's gauge and,
        # behind the sight glass, the meter), and pack.py refuses a layer empty in a direction. "cycle": each
        # turns or rocks about a pivot off its own centroid, so nothing holds to a point or a line
        dict(name="mech", frames=NF, motion="cycle", animation_speed=SPEED),
        # T07d (Liam, 2026-10-21, on T07c's E2): the embers off the skimmings bin, rendered here, not drawn
        # in PIL, each frame with every other part held out, so a part nearer the camera than an ember hides
        # it in the sheet itself and the engine may draw the layer over the whole machine. 48 frames at
        # twice the loop's speed: two ember frames to a machine frame, in step with it (the mech parts are
        # held out at frame f // 2), so it must not run at constant_speed. "embers" the cinders as the
        # sun shows them (unlit, the riser's way), "embers-light" their light alone, drawn as glow
        dict(name="embers", frames=48, motion="flow", working=True, animation_speed=round(2 * SPEED, 6)),
        dict(name="embers-light", kind="glow", over="embers", frames=48, motion="flow"),
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

# ---------------------------------------------------------------- groups, assemblies, variations
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
VAR = {}            # object name -> the direction whose variation it is part of
CONT = {}           # object name -> the empty it was built under (None: built in ROOT's own frame)
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


# ================================================================ where each direction puts things
TX, TY = 0.0, 0.18          # the tower's axis, over the vent, as modelled (facing north)
HW = 0.34                   # the shaft's half-width
Z0, Z1 = 0.36, 2.92         # the shaft
ZT = 3.25                   # the head tank's axis
SLOT = 0.13                 # half the slot down the south face
EDGE = 1.5

# the tower's axis in each direction: where the quarter turn puts it (the vent turns with the building)
AX = {"north": (0.0, 0.18), "east": (0.18, 0.0), "south": (0.0, -0.18), "west": (-0.18, 0.0)}
# the periphery's turn, as the empty it is built under carries it: (angle about z, mirrored in x first)
TURN = {"north": (0.0, False), "east": (-PI / 2, False), "south": (PI, False), "west": (PI / 2, True)}


def P2(d, x, y):
    """A periphery point (as modelled, facing north) where direction d puts it: east and south the
    building's quarter and half turn, west east's arrangement mirrored."""
    if d == "north":
        return x, y
    if d == "east":
        return y, -x
    if d == "south":
        return -x, -y
    return -y, -x


def pp(d, p):
    x, y = P2(d, p[0], p[1])
    return (x, y, p[2])


def cp(d, p):
    """A core point (as modelled) in direction d: the core is moved to the turned axis, never turned."""
    ax = AX[d]
    return (p[0] - TX + ax[0], p[1] - TY + ax[1], p[2])


class variant:
    """with variant(d, kind): every object built inside is direction d's; kind "core" builds it under an
    empty moved to AX[d], "peri" under one turned (and mirrored) by TURN[d], "root" in ROOT's own frame."""

    def __init__(self, d, kind):
        self.d, self.kind = d, kind

    def __enter__(self):
        self.before = set(bpy.data.objects)
        self.n0 = len(OBJS)
        self.e = None
        if self.kind != "root":
            e = bpy.data.objects.new(f"{self.kind}-{self.d}", None)
            sc.collection.objects.link(e)
            e.parent = ROOT
            if self.kind == "core":
                e.location = (AX[self.d][0] - TX, AX[self.d][1] - TY, 0.0)
            else:
                a, mirror = TURN[self.d]
                e.rotation_euler = (0.0, 0.0, a)
                if mirror:
                    e.scale = (-1.0, 1.0, 1.0)
            self.e = e
        return self

    def __exit__(self, *a):
        if self.e is not None:
            for o in bpy.data.objects:
                if o not in self.before and o is not self.e and o.parent == ROOT:
                    o.parent = self.e
        for o in OBJS[self.n0:]:
            VAR[o.name] = self.d
            CONT[o.name] = self.e


def charge(t):
    """Helium let in in two charges a loop."""
    return max(pulse(t, 0.06, 0.3, 0.06), pulse(t, 0.56, 0.8, 0.06))


RATE = lambda t: 0.2 + charge(t)          # noqa: E731

# the sight glass, as modelled: T07's east of the line (north, east, west); south, east of the tower
GLASS_AT = {"fixed": ((0.31, -0.84, 0.3), (0.31, -0.84, 0.98)), "south": ((-0.66, -0.05, 0.3), (-0.66, -0.05, 0.98))}
CTRL_AT = {"fixed": (0.27, -0.47, 0.28), "south": (-0.62, 0.3, 0.28)}
CHEST_AT = {"fixed": ((-0.65, 0.02, 0.3), (0.26, 0.7, 0.4)), "south": ((0.32, -0.88, 0.3), (0.2, 0.6, 0.4))}
TEE = (0, -0.56, ZA)
RECEIVER = (-0.94, -0.94)
OUT_IN = {}
GLASS_PTS = {}


# ================================================================ the core: faces the camera in every direction
def build_core(d):
    # ---------------------------------------------------------------- footings: each unit on its own, no deck
    # the tower's footing over the vent. East and west its south edge 0.06 in: there the turned control house
    # (east) or its mirror (west) stands 0.04 into it (T07c --collide); the riser's foot still stands on it
    foundation(-0.5, -0.30 if d in ("east", "west") else -0.36, 0.5, 0.7, 0.3, "refractory")
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

    # ---------------------------------------------------------------- the glass riser in the slot
    GX, GY = TX, TY - HW + 0.05
    GZ0, GZ1 = Z0 + 0.12, Z1 - 0.08
    riser_m = melt(f"mt_riser_{d}", "flow", scale=1.6, k=2, soft=True, bright=1.0, axis="Z",
                   fn=lambda t: 0.82 + 0.18 * charge(t))
    with grp("riser"), asm():
        cyl((GX, GY, (GZ0 + GZ1) / 2), 0.085, GZ1 - GZ0, riser_m, verts=32, bevel=0)
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

    # ---------------------------------------------------------------- the head tank on the tower top
    with asm():
        box((TX, TY, Z1 + 0.08), (1.02, 0.8, 0.06), "dark_steel")
        for sx in (-1, 1):
            for y in (TY - 0.38, TY + 0.38):
                box((TX + sx * 0.49, y, Z1 + 0.28), (0.025, 0.025, 0.36), "yellow", bevel=0.003)
            box((TX + sx * 0.49, TY, Z1 + 0.45), (0.025, 0.78, 0.025), "yellow", bevel=0.003)
        for xs in (-0.3, 0.3):
            box((TX + xs, TY, Z1 + 0.18), (0.1, 0.5, 0.16), "dark_steel")
    tank_m = melt(f"mt_tank_{d}", "flow", scale=7.0, k=1, bright=0.85, axis="X")
    with asm():
        cyl((TX, TY, ZT), 0.3, 0.86, "iron_dk", rot=(0, PI / 2, 0), verts=48)
        for xx, s in ((TX - 0.43, -1), (TX + 0.43, 1)):
            h_ = head(xx, TY, ZT, 0.3, 0.1, "iron_dk")
            h_.rotation_euler = (0, s * PI / 2, 0)
        for xx in (TX - 0.25, TX, TX + 0.25):
            cyl((xx, TY, ZT), 0.318, 0.05, "nickel", rot=(0, PI / 2, 0), verts=48)
        cyl((GX, GY, Z1 + 0.06), 0.1, 0.18, "heat", verts=24)                      # the riser's head into the tank
        with grp("riser"):
            box((TX - 0.12, TY - 0.285, ZT - 0.04), (0.3, 0.03, 0.07), tank_m, bevel=0.003)
        box((TX - 0.12, TY - 0.3, ZT - 0.04), (0.36, 0.02, 0.12), "dark_steel", bevel=0.004)
        with grp("riser"):
            box((TX - 0.12, TY - 0.305, ZT - 0.04), (0.3, 0.012, 0.07), "pane", bevel=0)
    manway_top(TX - 0.12, TY + 0.05, ZT + 0.29, r=0.09)
    cyl((TX + 0.2, TY, ZT + 0.27), 0.06, 0.08, "bare", verts=16)               # the tank's gas offtake

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

    # the sparger ring round the tower's foot: helium blown into the melt
    with asm():
        torus((TX, TY, 0.44), 0.44, 0.04, "he_lag", seg=48)
        for i in range(8):
            a = 2 * PI * (i + 0.5) / 8
            torus((TX + 0.44 * math.cos(a), TY + 0.44 * math.sin(a), 0.44), 0.045, 0.01, "he_band", rot=(0, 0, 0), seg=16)
            cyl((TX + 0.4 * math.cos(a), TY + 0.4 * math.sin(a), 0.41), 0.02, 0.08, "bare", rot=(0, PI / 2, a), verts=8,
                bevel=0)
    # the ladder up the tower's west side
    ladder(TX - HW - 0.1, TY - 0.1, 0.22, Z1 + 0.1, axis="y", mat="ochre")
    with asm():
        for z in (1.0, 1.6, 2.2):
            torus((TX - HW - 0.18, TY - 0.1, z), 0.14, 0.012, "ochre", rot=(0, 0, 0), seg=24)


# ================================================================ the periphery: turns with the fluid boxes
def build_periphery(d):
    var = "south" if d == "south" else "fixed"
    G0_, G1_ = GLASS_AT[var]
    ga, gb = axis_pts(G0_, G1_, 0.1)
    GLASS_PTS[d] = (G0_, G1_, ga, gb)
    out_in = nozzle("N", length=0.36, mat="heat")
    OUT_IN[d] = pp(d, out_in)
    # ---------------------------------------------------------------- the helium in: the grey-violet line
    in_in = nozzle("S", length=0.3, mat="bare")
    # T07, the south join (Liam: "Fix in the model"): the inlet's footing carried out under the nozzle to the
    # south edge (round 5's stopped at y -1.18, 0.32 tile short). Its grout ring ends at the edge.
    foundation(-0.42, -1.18 if SOUTH == "round5" else -1.485, 0.42, -0.4, 0.1, anchors=False)
    valve(0, -1.06, z=ZA - 0.1, h=0.36, r=0.06)
    he_line([in_in, (0, -1.06, ZA), (0, -0.9, ZA)], name="helium in: nozzle to the flow meter")
    with asm():
        cyl(TEE, 0.1, 0.16, "bare", rot=(PI / 2, 0, 0), verts=20)                   # the tee where the recovered gas joins
        cyl((0, -0.56, ZA + 0.14), 0.035, 0.2, "bare", verts=12)
    he_line([(0, -0.66, ZA), (0, -0.62, ZA)], name="helium: meter to tee")
    if d == "south":
        # the glass east of the tower (as built: west of the line, on the gas bottles' footing)
        he_line([(0, -0.48, ZA), (-0.15, -0.45, ZA), (-0.4, -0.42, 0.42), (-0.58, -0.22, 0.3), ga, G0_],
                name="helium: tee to the sight glass")
    else:
        he_line([(0, -0.48, ZA), (0.12, -0.5, 0.3), (0.22, -0.66, 0.2), ga, G0_], name="helium: tee to the sight glass")
    box((-0.24, -0.78, 0.3), (0.22, 0.4, 0.4), "green", bevel=0.02)            # the meter's transmitter
    box(CTRL_AT[var], (0.24, 0.26, 0.36), "grey", bevel=0.02)                   # the injection controller
    bundle([(-0.18, -0.7, 0.5), (-0.1, -0.74, 0.52), (-0.03, -0.78, ZA + 0.1)], cols=("black", "grey"), r=0.012,
           name="meter cable")

    # ---------------------------------------------------------------- the compressor skid (SE)
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
    hazard_tag((0.85, -1.425, 0.3), 0.3, 0.06)
    if d in ("north", "south"):
        # its discharge west, over the inlet, to the recovery receiver (SW); east and west, ROUTES
        he_line([(0.85, -0.95, 1.06), (0.7, -0.9, 1.12), (0.3, -0.42, 1.0), (-0.3, -0.42, 1.0), (-0.75, -0.62, 1.2),
                 (-0.92, -0.9, 1.32)], r=0.05, name="recovery: compressor to the receiver")
    # ---------------------------------------------------------------- the recovery receiver (SW)
    foundation(-1.4, -1.4, -0.48, -0.48, 0.12)
    vtank(-0.94, -0.94, 0.4, 1.2, mat="grey", bands=(0.4, 0.85), band_mat="he_edge", nozzle=None)
    cyl((-0.94, -0.94, 1.32), 0.07, 0.12, "bare", verts=16)
    he_line([(-0.6, -0.86, 0.3), (-0.35, -0.6, 0.32), (-0.1, -0.56, ZA)], r=0.05,
            name="recovery: receiver back into the line at the tee")

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
    # T07: the switchgear's lens, amber when the fluid is missing, at its south-east corner
    lens(1.34, -0.32, 0.72, "lens-amber")
    bundle([(1.2, -0.36, 0.6), (1.28, -0.6, 0.75), (1.25, -0.95, 0.72)], cols=("black", "yellow"), r=0.014,
           name="switchgear to the compressor motor")
    bundle([(0.93, 0.6, 0.9), (0.95, 0.5, 0.75), (0.95, 0.45, 0.7)], cols=("black", "grey"), r=0.012,
           name="control house to the switchgear")

    # ---------------------------------------------------------------- the gas bottles and tool chest (W), the skimmings bin (NW)
    foundation(-1.5, -0.42, -0.52, 0.5, 0.1)
    for k, yy in enumerate((-0.2, 0.25)):
        vtank(-1.05, yy, 0.22, 0.95 - 0.12 * k, mat=("green", "ochre")[k], bands=(0.45,), nozzle=None)
    box(*CHEST_AT[var], "dark_steel", bevel=0.02)      # T07: was at x -0.7, on the bottles' feet; south: moved
    foundation(-1.46, 0.52, -0.42, 1.46, 0.1)
    with asm():
        box((-0.92, 0.95, 0.42), (0.86, 0.8, 0.64), "oxide", bevel=0.025)
        for sx, sy, w, dd in ((0, -0.38, 0.9, 0.06), (0, 0.38, 0.9, 0.06), (-0.42, 0, 0.06, 0.82), (0.42, 0, 0.06, 0.82)):
            box((-0.92 + sx, 0.95 + sy, 0.76), (w, dd, 0.06), "dark_steel", bevel=0.006)
        box((-0.92, 0.95, 0.7), (0.78, 0.72, 0.04), "slag", bevel=0)
        box((-0.92, 1.35, 0.98), (0.86, 0.04, 0.4), "dark_steel", bevel=0.01)
        box((-0.56, 1.3, 0.98), (0.03, 0.03, 0.42), "bare", bevel=0)
    hazard_tag((-0.92, 0.55, 0.4), 0.6, 0.07)
    stain(0.4, -0.3, 0.25, 0.1)
    stain(-0.3, 1.2, 0.2, 0.08)


# ================================================================ the instruments: face the camera wherever they stand
def build_instruments(d):
    G0_, G1_, ga, gb = GLASS_PTS[d]
    up = Vector(pp(d, (0, 1, 0)))           # the inlet line's way, turned
    with grp("meter"):
        # its dial to the camera; south, where the meter stands behind the tower with the tee south of it,
        # tipped up so it clears the tee
        flow_meter(pp(d, (0, -0.78, ZA)), tuple(up), r=0.12, turns=2, rate=RATE,
                   facing=(-0.3, -0.1, 1) if d == "south" else (-0.3, -0.55, 1))
    tee = pp(d, TEE)
    with grp("gauge-line"):
        he_gauge((tee[0], tee[1] - 0.02, ZA + 0.27), (0, -1, 0.7), live=lambda t: -0.4 + 1.2 * charge(t))
    with grp("glass"):
        sight_tank(pp(d, G0_), pp(d, G1_), stroke_pulse((0.06, 0.56), rise=0.05, fall=0.36), r=0.14)
    rx, ry, _ = pp(d, (*RECEIVER, 0))
    with grp("gauge-receiver"):
        he_gauge((rx, ry - 0.41, 0.62), (0, -1, 0.2), live=lambda t: 0.5 * math.sin(2 * PI * 3 * t))
    id_panel((rx, ry - 0.405, 0.9), 0.26, 0.12, stripe="yellow")


# ================================================================ the lines between the core and the periphery
def bracket(at, size):
    box(at, size, "dark_steel")


def build_routes(d):
    """The runs each direction routes for itself (ROUTES in the docstring), in ROOT's frame."""
    c = lambda x, y, z: cp(d, (x, y, z))      # noqa: E731  a core point
    p = lambda x, y, z: pp(d, (x, y, z))      # noqa: E731  a periphery point
    G0_, G1_, ga, gb = GLASS_PTS[d]
    out = OUT_IN[d]
    REC_TAIL = [p(0.62, -0.62, 0.7), p(0.66, -0.82, 0.62)]          # onto the compressor's crankcase
    if d == "north":                         # T07's, unchanged
        down = [c(TX - 0.45, TY, ZT - 0.05), c(TX - 0.6, TY + 0.12, ZT - 0.3), (-0.62, 0.62, 2.0), (-0.36, 0.74, 0.9),
                (-0.3, 0.95, 0.55), (-0.15, 1.1, ZA), out]
        dbr = [((-0.47, TY + 0.38, z), (0.14, 0.1, 0.04)) for z in (1.6, 2.2)]
        rec = [c(TX + 0.2, TY, ZT + 0.29), c(TX + 0.3, TY - 0.08, ZT + 0.44), c(TX + 0.44, TY - 0.42, ZT + 0.1),
               (0.44, -0.2, 2.0), (0.44, -0.24, 0.9)] + REC_TAIL
        rbr = [((TX + HW + 0.06, TY - 0.3, z), (0.08, 0.08, 0.035)) for z in (1.0, 1.7, 2.3)]
        ring = [G1_, gb, (0.22, -0.6, 1.0), (0.1, -0.38, 0.78), (0.04, -0.3, 0.5), (TX, TY - 0.44, 0.44)]
        cable = [(1.0, 0.32, 0.84), (0.7, 0.3, 1.2), (TX + HW + 0.02, TY + 0.05, 1.5)]
        c2r = None
    elif d == "east":
        # the tower at (0.18, 0); the outlet east, the compressor south-west, the receiver north-west
        down = [c(TX + 0.15, TY + 0.27, ZT), (0.42, 0.52, 3.2), (0.62, 0.66, 2.5), (0.72, 0.45, 1.5), (0.95, 0.12, 0.75),
                (1.12, 0.02, ZA + 0.02), out]
        dbr = [((0.58, 0.42, 1.9), (0.1, 0.12, 0.04))]
        rec = [c(TX + 0.2, TY, ZT + 0.29), (0.2, 0.2, 3.66), (-0.15, 0.5, 3.5), (-0.38, 0.55, 2.9), (-0.38, 0.5, 2.4),
               (-0.36, 0.48, 1.6), (-0.65, 0.35, 1.2), (-1.1, 0.2, 0.98), (-1.18, -0.3, 0.95), (-1.2, -0.5, 0.8),
               (-1.2, -0.66, 0.64)]          # down the tower's back, then west of the sight glass, not across it
        rbr = [((-0.24, 0.4, z), (0.12, 0.08, 0.035)) for z in (2.0, 2.6)]
        ring = [p(*G1_), p(*gb), (-0.6, -0.36, 0.95), (-0.35, -0.38, 0.7), (-0.2, -0.34, 0.5),
                c(TX - 0.31, TY - 0.31, 0.44)]
        cable = [p(1.0, 0.32, 0.84), (0.6, -0.65, 1.15), (0.56, -0.05, 1.5)]
        c2r = [p(0.85, -0.95, 1.06), (-1.2, -0.85, 1.22), (-1.32, -0.4, 1.45), (-1.3, 0.4, 1.5), (-1.1, 0.75, 1.52),
               p(-0.92, -0.9, 1.32)]
    elif d == "west":
        # east's periphery mirrored; the core unmirrored at (-0.18, 0): its ladder west, its float chamber east
        down = [c(TX - 0.45, TY, ZT - 0.05), (-0.78, 0.15, 2.95), (-0.95, 0.3, 2.2), (-1.0, 0.2, 1.3), (-1.1, 0.06, 0.65),
                (-1.14, 0.01, ZA + 0.02), out]
        dbr = [((-0.6, 0.27, 2.2), (0.14, 0.1, 0.04))]
        rec = [c(TX + 0.2, TY, ZT + 0.29), (0.08, 0.25, 3.62), (0.25, 0.52, 3.4), (0.38, 0.55, 2.9), (0.38, 0.5, 2.4),
               (0.36, 0.48, 1.6), (0.65, 0.35, 1.2), (1.1, 0.2, 0.98), (1.18, -0.3, 0.95), (1.2, -0.5, 0.8),
               (1.2, -0.66, 0.64)]
        rbr = [((0.24, 0.4, z), (0.12, 0.08, 0.035)) for z in (2.0, 2.6)]
        ring = [p(*G1_), p(*gb), (0.6, -0.36, 0.95), (0.35, -0.38, 0.7), (0.2, -0.34, 0.5),
                c(TX + 0.31, TY - 0.31, 0.44)]
        cable = [p(1.0, 0.32, 0.84), (-0.42, -0.7, 1.2), (-0.42, -0.38, 1.5)]
        c2r = [p(0.85, -0.95, 1.06), (1.2, -0.85, 1.22), (1.32, -0.4, 1.45), (1.3, 0.4, 1.5), (1.1, 0.75, 1.52),
               p(-0.92, -0.9, 1.32)]
    else:
        # south: the tower at (0, -0.18); the outlet south, the compressor north-west, the receiver north-east;
        # the sight glass east of the tower
        down = [c(TX - 0.45, TY, ZT - 0.05), c(TX - 0.6, TY + 0.12, ZT - 0.3), (-0.82, -0.25, 2.3), (-0.8, -0.55, 1.6),
                (-0.45, -0.8, 1.15), (-0.2, -1.0, 0.6), (-0.08, -1.12, ZA + 0.03), out]
        dbr = [((-0.47, -0.4, 2.0), (0.12, 0.1, 0.04))]
        rec = [c(TX + 0.2, TY, ZT + 0.29), (0.1, 0.0, 3.66), (-0.2, 0.3, 3.4), (-0.45, 0.3, 2.6), (-0.45, 0.32, 1.6),
               (-0.5, 0.5, 1.0), (-0.62, 0.7, 0.75), REC_TAIL[1]]
        rbr = [((-0.4, 0.24, z), (0.1, 0.12, 0.035)) for z in (1.7, 2.3)]
        ring = [p(*G1_), p(*gb), (0.48, 0.0, 1.02), (0.45, -0.08, 0.72), c(TX + 0.415, TY + 0.145, 0.44)]
        cable = [p(1.0, 0.32, 0.84), (-0.7, -0.05, 1.2), (-0.39, 0.1, 1.5)]
        c2r = None
    if d == "north":
        ring = [p(*q) for q in ring[:-1]] + [ring[-1]]
    lagged(down, r=0.12, bands=0.25, name="downcomer (melt)")
    with asm():
        for at, size in dbr:
            bracket(at, size)
    he_line(rec, r=0.055, name="recovery: head tank down to the compressor")
    with asm():
        for at, size in rbr:
            bracket(at, size)
    he_line(ring, name="helium: sight glass to the sparger ring")
    bundle(cable, cols=("black", "red", "grey"), r=0.018, name="switchgear to the tower's instruments")
    if c2r:
        he_line(c2r, r=0.05, name="recovery: compressor to the receiver")


for _d in DIRS:
    with variant(_d, "core"):
        build_core(_d)
    with variant(_d, "peri"):
        build_periphery(_d)
    with variant(_d, "root"):
        build_instruments(_d)
        build_routes(_d)
bpy.context.view_layer.update()

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
CUR_D = ["north"]


def build_inv(o):
    """The matrix that takes o's world points back into the frame it was built in (as modelled)."""
    e = CONT.get(o.name)
    return (e.matrix_world if e is not None else ROOT.matrix_world).inverted()


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
PLATE_GROUPS = ("body",) + CONTENT + LENSES          # the plate: no moving part (each is its own layer)


def members(*groups, d=None):
    return [o for o in OBJS if PART[o.name] in groups and (d is None or VAR.get(o.name) == d)]


# ---------------------------------------------------------------- the pipe pictures (round 1's model, in assembler 3's outline)
VANILLA = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity/assembling-machine-3")
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


# ---------------------------------------------------------------- the runs' ends (the kit's check_ends, per direction)
def parity_inside(tree, p_):
    dv = Vector((0.5774, 0.5771, 0.5777))
    n, o = 0, p_.copy()
    for _ in range(64):
        hit = tree.ray_cast(o, dv)
        if hit[0] is None:
            break
        n += 1
        o = hit[0] + dv * 1e-5
    return n % 2 == 1


def check_ends(tol=0.04):
    """For every registered run, each end must sit inside another part of its own direction or within
    `tol` of its surface (parts the run made itself are not counted)."""
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get()
    bpy.context.view_layer.update()
    trees = {}

    def tree(o):
        if o.name not in trees:
            ev = o.evaluated_get(dg)
            me = ev.to_mesh()
            mw = o.matrix_world
            verts = [mw @ v.co for v in me.vertices]
            polys = [tuple(p.vertices) for p in me.polygons]
            ev.to_mesh_clear()
            trees[o.name] = BVHTree.FromPolygons(verts, polys)
        return trees[o.name]

    idx = {o.name: i for i, o in enumerate(OBJS)}
    out = []
    for name, a, b, (i0, i1) in K.PIPES:
        if i0 >= len(OBJS):
            continue
        first = OBJS[i0]
        d = VAR.get(first.name)
        e = CONT.get(first.name)
        frame = e.matrix_world if e is not None else ROOT.matrix_world
        res = []
        for p in (a, b):
            w = frame @ p
            best = None
            for o in OBJS:
                i = idx[o.name]
                if i0 <= i < i1 or o.type != "MESH" or o in STAINS or VAR.get(o.name) != d:
                    continue
                bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
                if any(w[k] < min(c[k] for c in bb) - tol or w[k] > max(c[k] for c in bb) + tol for k in range(3)):
                    continue
                loc, nrm, _, dist = tree(o).find_nearest(w)
                if loc is None:
                    continue
                inside = parity_inside(tree(o), w)        # not the normal: west's mirror turns every face over
                dd = 0.0 if inside else dist
                if dd <= tol and (best is None or dd < best[0]):
                    best = (dd, o.data.materials[0].name if o.data.materials else "?")
            res.append(dict(at=[round(v, 2) for v in p], ok=best is not None, to=(best[1] if best else None),
                            screen=screen_of(ROOT.matrix_world.inverted() @ w)))      # T07d: for the ends' crops
        out.append(dict(direction=d, name=name, ends=res, ok=all(r["ok"] for r in res)))
        print(("ok  " if out[-1]["ok"] else "LOOSE ") + f"{d}: {name}", [(r["at"], r["to"]) for r in res], flush=True)
    return out


# ---------------------------------------------------------------- --collide (round 1's model's check), per direction
DEEP = 0.03
DETAIL_MATS = {"bolt", "seam", "stencil", "hazard", "label", "gauge", "ceramic", "needle", "red", "yellow", "brass",
               "dark", "lamp", "oil", "pane", "rubber", "he_band", "he_band4", "he_edge", "lens_green", "lens_amber"}
# meant contacts of a moving part, (group, part, other part, why): printed as "meant" lines, which a
# render.sh --collide counts as clashes unless allowed; each listed here is also printed with its reason
MEANT = [
    (r"^riser$", r"\[slag\]", r"\[nickel\]",
     "a bubble passing behind one of the riser's three band clamps (each modelled as a solid disc round the glass)"),
]
# fixed parts that meet by design, (part a, part b, why), matched both ways on the parts' descriptions (each
# part's centre in the frame it was built in: the core's and the periphery's as modelled, facing north)
_F = r"^Cube[.0-9]*\[(refractory|dark_steel)\] at \([-+.0-9]+,[-+.0-9]+,0\.(0\d|1[0-5])\)"   # a footing slab or its grout
MEANT_FIXED = [
    (r"\[refractory\] at \([-+]0\.00,\+0\.(17|20),0\.15\)", r"\[dark_steel\] at \([-+]0\.00,\+0\.18,0\.03\)",
     "the vent collar's foot ring cast into the tower's footing"),
    (r"\[refractory\] at \([-+]0\.00,\+0\.(17|20),0\.15\)", r"\[ochre\] at \(-0\.44,",
     "the ladder's feet set into the tower's footing"),
    (_F, _F, "two footings poured against each other"),
    (r"\[dark_steel\] at \([-+]0\.34,[-+]0\.(16|52),1\.64\)", r"\[he_lag\] at \([-+]0\.00,\+0\.18,0\.44\)",
     "the sparger ring led through the shaft's corner posts at their foot (round 5's ring, radius 0.44)"),
    (r"\[dark_steel\] at \([-+]0\.00,-0\.11,0\.43\)", r"\[he_lag\] at \([-+]0\.00,\+0\.18,0\.44\)",
     "the sparger ring let into the riser's foot, which it feeds"),
    (r"\[dark_steel\] at \([-+]0\.00,-0\.11,2\.89\)", r"\[heat\] at \([-+]0\.00,-0\.11,2\.98\)",
     "the riser's head let through its top cap into the tank"),
    (r"\[dark_steel\] at \([-+]0\.30,\+0\.18,3\.10\)", r"\[iron_dk\] at \([-+]0\.00,\+0\.18,3\.25\)",
     "the head tank sitting in its two saddles"),
    (r"\[mt_riser_\w+\] at \([-+]0\.00,-0\.11,", r"\[nickel\] at \([-+]0\.00,-0\.11,",
     "the riser's band clamps round its glass, each modelled as a solid disc (T07c: at 0.030 deep east and west, "
     "a rounding over the 0.03 line where north measured under it)"),
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
    """Per direction, every moving part in every frame against every fixed part and every other layer's
    moving parts, then the fixed model part against part (round 1's model's, the circulator's). Each
    direction is its own variation, so each is checked on its own parts."""
    from mathutils.bvhtree import BVHTree
    lines, meant_lines, pairs = [], [], []

    def out(s_):
        print(s_, flush=True)
        lines.append(s_)
    RI = ROOT.matrix_world.inverted()
    runs = {}
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
            self.inv = build_inv(o)
            c = self.inv @ (sum(self.vs, Vector()) / len(self.vs)) if self.vs else Vector()
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
        return [x.inv @ v for v in x.vs if meet(y.box, (v, v)) and inside(y.tree, v)]

    n_meant = n_clash = n_real = n_deep = 0
    order = {"REAL": 0, "touch": 1, "seated": 2}
    for d in DIRS:
        meshes = [o for o in OBJS if o.type == "MESH" and o not in STAINS and VAR.get(o.name) == d]
        out(f"COLLIDE {d}: {len(meshes)} parts, {len([o for o in meshes if o.name in MOVING])} moving; frames 0-{NF - 1}")
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
        for (g, ad, bd, kind), fs in sorted(hits.items(), key=lambda kv: kv[0]):
            why = "its own assembly's part: a bubble in its melt and glass, a needle on its face, the liquid in its tank" \
                if kind.endswith("(own assembly)") else \
                next((w for gr, ar, br, w in MEANT if re.search(gr, g) and re.search(ar, ad) and re.search(br, bd)), None)
            fr = f"{fs[0]}-{fs[-1]}" if fs == list(range(fs[0], fs[-1] + 1)) else ",".join(map(str, fs))
            if why:
                n_meant += 1
                meant_lines.append(f"{d}: meant moving [{g}] {ad} x {bd}: {kind}, frames {fr}  ({why})")
            else:
                n_clash += 1
                out(f"COLLIDE CLASH {d}: moving [{g}] {ad} x {bd}: {kind}, frames {fr}")
        set_pose(0)
        fixed = [fixed_cache[o.name] for o in meshes if o.name in fixed_cache]
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
                pairs.append((tag, -dp, f"{d}: {tag} {a.desc} x {b.desc}: {kind}, {dp:.3f} deep" + (f"  ({why})" if why else "")))
                if tag == "REAL":
                    out(f"COLLIDE REAL {d}: fixed {a.desc} x {b.desc}: {kind}, {dp:.3f} deep")
    out(f"COLLIDE moving: {n_clash} clashes, {n_meant} meant contacts (collide-model.txt)")
    with open(os.path.join(OUT, "collide-model.txt"), "w") as f_:
        f_.write("\n".join(meant_lines) + "\n\n")
        f_.write("\n".join(l_ for _, _, l_ in sorted(pairs, key=lambda p_: (order[p_[0]], p_[1], p_[2]))) + "\n")
    out(f"COLLIDE model: {n_real} clashes (REAL: reach more than {DEEP} tile into each other and no rule explains "
        f"them); {len(pairs)} touching pairs over the four directions, {n_deep} touch at under {DEEP} "
        f"(collide-model.txt)")
    ends = check_ends()
    loose = [f"{e['direction']}: {e['name']}" for e in ends if not e["ok"]]
    out(f"COLLIDE ends: {len(ends) - len(loose)} of {len(ends)} runs end in what they serve"
        + (f"; loose (not a clash, listed): {'; '.join(loose)}" if loose else ""))
    with open(os.path.join(OUT, "collide.txt"), "w") as f_:
        f_.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- render helpers
def setup(visible=(), holdouts=(), unseen=(), ground=False):
    """Show, hold out or hide each group of the current direction's variation; a part the pose hid (a
    bubble above the glass's level, or every bubble in the idle glass) stays hidden."""
    d = CUR_D[0]
    for o in OBJS:
        g = PART[o.name]
        mine = VAR.get(o.name) == d
        o.hide_render = not mine or not (g in visible or g in holdouts or g in unseen) or o.name in POSE_HIDE
        o.is_holdout = g in holdouts
        o.visible_camera = g not in unseen
    GROUND.hide_render = not ground


def hide_glassy_holdouts():
    for o in OBJS:                      # a pane held out still leaves faint alpha the engine would tint
        if o.is_holdout and any(m.name.startswith(GLASSY) for m in o.data.materials):
            o.hide_render = True


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


def screen_of(p):
    """A ROOT point's place on the sprite, tiles from the entity origin (x right, y down): the ground
    projects square and a tile of height is cos(elevation) of a tile on the screen (contract.screen)."""
    return round(p[0], 4), round(-(p[1] + p[2] * math.cos(rig.ELEVATION)), 4)


def effect_anchors():
    """Where the agreed effects start in each direction (Liam, 2026-10-21), for effects.py and the coder."""
    out = {}
    for d in DIRS:
        pts = dict(
            wisp_a2=cp(d, (TX + 0.2, TY, ZT + 0.33)),              # the head tank's gas offtake (A2)
            embers_e2=pp(d, (-0.92, 0.95, 0.72)),                  # the skimmings bin's slag
            ground_light_e3=cp(d, (TX, TY - 0.36, 0.0)),           # the riser's foot, on the ground
            cold_breath_e4=pp(d, (0, -1.06, ZA + 0.3)),            # the stop valve's bonnet
            purge_e5=cp(d, (TX + 0.62, TY, ZT + 0.2)),             # the float chamber's cap
        )
        out[d] = {k: dict(model=[round(v, 3) for v in p_], shift_tiles=screen_of(p_)) for k, p_ in pts.items()}
    return out


# ================================================================ E2: the embers (T07d)
#   Sparks off the slag in the skimmings bin (as modelled: the slag's top at z 0.72, 0.78 x 0.72 round
#   (-0.92, 0.95)), each born at a point of the slag, rising and cooling, drifting a little with the same
#   world wind in every direction. Real objects in the scene, not in OBJS (no part of the machine, its
#   collide or its moving parts), hidden in every pass but their own. Each is a core (a short streak along
#   its flight) and a soft halo, the halo drawn only in the light pass.
NFE = 48
EMBER_SLAG = (-0.92, 0.95, 0.725)
EMBER_HALF = (0.33, 0.30)
EMBER_WIND = (0.10, 0.03)                 # world tiles over a spark's life: east and a little north
EMBER_STRENGTH = _opt("--ember-strength", 2.2)     # 9, 5, 3.2 and 2.8 drove 1-6 px to white (pack.py)
_rnd = random.Random(23)
SPARKS = [dict(phase=_rnd.random(), life=_rnd.uniform(0.24, 0.42), bx=_rnd.uniform(-1, 1), by=_rnd.uniform(-1, 1),
               rise=_rnd.uniform(1.1, 2.0), spread=(_rnd.uniform(-0.1, 0.1), _rnd.uniform(-0.06, 0.06)),
               r=_rnd.uniform(0.011, 0.016), wob=_rnd.uniform(0, TAU)) for _ in range(18)]
# a tile of rise is half a tile on the screen (the camera's 60 degrees): 1.1-2.0 lifts them 35-64 px, T07c's 48-80


def _ember_mat(name, halo=False):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    out_ = nt.nodes["Material Output"]
    if not halo:
        b = nt.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = rig.srgb("#2E1C14")       # a cinder, unlit
        b.inputs["Roughness"].default_value = 0.85
        b.inputs["Emission Strength"].default_value = 0.0
        return m, b
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    ramp = nt.nodes.new("ShaderNodeMath")
    ramp.operation = "POWER"
    ramp.inputs[1].default_value = 2.5
    nt.links.new(lw.outputs["Facing"], ramp.inputs[0])
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(ramp.outputs[0], mix.inputs[0])            # facing the camera: light; the rim: clear
    nt.links.new(em.outputs[0], mix.inputs[1])
    nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out_.inputs["Surface"])
    return m, em


EMBERS = {}                                # direction -> [(core, core material's BSDF, halo, halo emission)]
for _d in DIRS:
    EMBERS[_d] = []
    for _i, _s in enumerate(SPARKS):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=12, ring_count=6)
        core = bpy.context.active_object
        core.name = f"ember-{_d}-{_i}"
        cm, cb = _ember_mat(core.name)
        core.data.materials.append(cm)
        for p_ in core.data.polygons:
            p_.use_smooth = True
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=16, ring_count=8)
        halo = bpy.context.active_object
        halo.name = f"ember-halo-{_d}-{_i}"
        hm, he = _ember_mat(halo.name, halo=True)
        halo.data.materials.append(hm)
        for o in (core, halo):
            o.parent = ROOT
            o.hide_render = True
            o.visible_shadow = False        # they light nothing and shade nothing: the rest is held out
            o.visible_diffuse = o.visible_glossy = False
        EMBERS[_d].append((core, cb, halo, he))


def ember_state(s, f):
    """Spark s at ember frame f: None when not alive, else (model point, velocity, u in its life)."""
    age = ((f / NFE) - s["phase"]) % 1.0
    if age >= s["life"]:
        return None
    u = age / s["life"]
    x0, y0, z0 = EMBER_SLAG
    bx, by = x0 + s["bx"] * EMBER_HALF[0], y0 + s["by"] * EMBER_HALF[1]

    def at(uu):
        rise = s["rise"] * uu * (1.3 - 0.3 * uu)                  # quick off the slag, easing as it cools
        lat = (s["spread"][0] * uu + 0.025 * math.sin(7 * uu + s["wob"]),
               s["spread"][1] * uu + 0.02 * math.cos(6 * uu + s["wob"]))
        return bx, by, z0 + rise, lat
    return at(u), at(min(1.0, u + 0.05)), u


def ember_world(d, st):
    """A spark's place in ROOT's frame in direction d: its birth point turned with the periphery (pp),
    its lift and drift in the world (the same wind facing every way)."""
    bx, by, z, lat = st
    x, y, _ = pp(d, (bx, by, 0.0))
    return Vector((x + lat[0] + EMBER_WIND[0] * (z - EMBER_SLAG[2]) / 0.9,
                   y + lat[1] + EMBER_WIND[1] * (z - EMBER_SLAG[2]) / 0.9, z))


def place_embers(d, f, show=False, halo=False, lit=False):
    """Every spark of direction d at ember frame f; shown (cores, and halos when `halo`) only when `show`;
    lit: the cores glow (the light pass), else unlit cinders (the paint pass)."""
    for dd in DIRS:
        for core, cb, h, he in EMBERS[dd]:
            core.hide_render = h.hide_render = True
    if not show:
        return
    for s, (core, cb, h, he) in zip(SPARKS, EMBERS[d]):
        st = ember_state(s, f)
        if st is None:
            continue
        a, b, u = st
        p0, p1 = ember_world(d, a), ember_world(d, b)
        vel = p1 - p0
        r = s["r"] * (1 - 0.45 * u)
        core.location = p0
        core.rotation_mode = "QUATERNION"
        core.rotation_quaternion = vel.to_track_quat("Z", "Y") if vel.length > 1e-6 else (1, 0, 0, 0)
        core.scale = (r, r, r * 4.5)                                   # a streak along its flight
        k = (1 - u) ** 0.8 * (0.78 + 0.22 * math.sin(31 * u + s["wob"] * 3))
        col = [c0 + (c1 - c0) * u ** 0.7 for c0, c1 in zip((1.0, 0.55, 0.16), (0.85, 0.2, 0.05))]
        cb.inputs["Emission Color"].default_value = (*col, 1)
        cb.inputs["Emission Strength"].default_value = EMBER_STRENGTH * k if lit else 0.0
        core.hide_render = False
        if halo:
            h.location = p0
            h.scale = (r * 2.4,) * 3
            he.inputs["Color"].default_value = (*col, 1)
            he.inputs["Strength"].default_value = 0.2 * EMBER_STRENGTH * k
            h.hide_render = False
    bpy.context.view_layer.update()


def ember_window(d, pad=0.08):
    """The render border (sprite px) round every spark's flight in direction d, halo and all."""
    bpy.context.view_layer.update()         # a camera just made has no world matrix until the update
    inv = sc.camera.matrix_world.inverted()
    xs, ys = [], []
    for f in range(NFE):
        for s in SPARKS:
            st = ember_state(s, f)
            if st is None:
                continue
            p_ = inv @ (ROOT.matrix_world @ ember_world(d, st[0]))
            xs.append(p_.x)
            ys.append(p_.y)
    ppt = rig.PX_PER_TILE
    W, Hc = CANVAS
    m = 0.08 + pad
    return (max(0, int(W / 2 + (min(xs) - m) * ppt)), max(0, int(Hc / 2 - (max(ys) + m) * ppt)),
            min(W, int(W / 2 + (max(xs) + m) * ppt) + 1), min(Hc, int(Hc / 2 - (min(ys) - m) * ppt) + 1))


# ---------------------------------------------------------------- --ends (T07d): every run's two ends, placed on the sprite
if "--ends" in argv:
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "ends.json"), "w") as f_:
        json.dump(check_ends(), f_, indent=1)
    print("done")
    sys.exit(0)

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
        o.hide_render = o in STAINS or VAR.get(o.name) != "north"
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


def ember_check(renders):
    """--ember-check (the docstring): the embers' holdout, checked by rays, not by the render's own holdout."""
    import numpy as np
    from mathutils.bvhtree import BVHTree
    bpy.context.view_layer.update()
    cam = sc.camera
    cm = cam.matrix_world.copy()
    fwd = (cm.to_3x3() @ Vector((0, 0, -1))).normalized()
    ppt = rig.PX_PER_TILE
    W, Hc = CANVAS
    SUB = 4
    dg = bpy.context.evaluated_depsgraph_get

    def bvh(objs):
        vs, ps = [], []
        g = dg()
        for o in objs:
            if o.type != "MESH":
                continue
            ev = o.evaluated_get(g)
            me = ev.to_mesh()
            mw = ev.matrix_world
            n0 = len(vs)
            vs.extend(mw @ v.co for v in me.vertices)
            ps.extend([n0 + i for i in p_.vertices] for p_ in me.polygons)
            ev.to_mesh_clear()
        return BVHTree.FromPolygons(vs, ps) if ps else None

    def ray(tree, o):
        if tree is None:
            return None
        hit = tree.ray_cast(o, fwd)
        return hit[3] if hit[0] is not None else None

    def origin(x, y):                        # sprite px (x right, y down) to a point on the camera's plane
        return cm @ Vector(((x - W / 2) / ppt, (Hc / 2 - y) / ppt, 0.0))

    def alpha(path):
        im = bpy.data.images.load(path)
        a = np.empty(W * Hc * 4, dtype=np.float32)
        im.pixels.foreach_get(a)
        bpy.data.images.remove(im)
        return np.flipud(a.reshape(Hc, W, 4)[:, :, 3])

    report = {}
    for d in DIRS:
        CUR_D[0] = d
        set_pose(0)
        setup(holdouts=GROUPS_ALL)
        hide_glassy_holdouts()
        still = [o for o in OBJS if not o.hide_render and PART[o.name] not in MECH + CONTENT]
        t_still = bvh(still)
        # the "before" mask: parts nearer the camera than a point on the vertical through the slag's centre
        # that lands on the same sprite row (where T07c's flat sprite embers stood, notionally)
        A = ROOT.matrix_world @ Vector(pp(d, EMBER_SLAG))
        up_ = (ROOT.matrix_world.to_3x3() @ Vector((0, 0, 1)))
        inv = cm.inverted()
        a_c, up_c = inv @ A, inv.to_3x3() @ up_
        near = bytearray(W * Hc)
        for y in range(Hc):
            h = ((Hc / 2 - (y + 0.5)) / ppt - a_c.y) / up_c.y
            if h < -0.05:
                continue
            e_depth = -(a_c.z + h * up_c.z)        # distance along the view from the camera's plane
            for x in range(W):
                t = ray(t_still, origin(x + 0.5, y + 0.5))
                if t is not None and t < e_depth - 0.1:
                    near[y * W + x] = 255
        with open(os.path.join(OUT, f"near-{d}.pgm"), "wb") as f_:
            f_.write(f"P5 {W} {Hc} 255\n".encode() + bytes(near))
        res = dict(frames=0, px=0, fail_px=0, fail_alpha_max=0, behind_rays=0, excess_px=0, fails=[])
        dyn = {}
        for f in range(NFE):
            g = f // 2
            if g not in dyn:
                set_pose(g)
                setup(holdouts=GROUPS_ALL)
                hide_glassy_holdouts()
                dyn = {g: bvh([o for o in OBJS if not o.hide_render and PART[o.name] in MECH + CONTENT])}
            for layer, lit in (("embers", False), ("embers-light", True)):
                a = alpha(os.path.join(renders, contract.named(contract.frame(layer, f), d) + ".png"))
                place_embers(d, f, show=True, halo=lit, lit=lit)
                t_emb = bvh([o for dd in (d,) for c, _, h, _ in EMBERS[dd] for o in (c, h) if not o.hide_render])
                res["frames"] += 1
                ys, xs = np.nonzero(a > 0)
                seen, fails = [], []
                for y, x in zip(ys.tolist(), xs.tolist()):
                    vis = behind = 0
                    for i in range(SUB):
                        for j in range(SUB):
                            o = origin(x + (j + 0.5) / SUB, y + (i + 0.5) / SUB)
                            te = ray(t_emb, o)
                            if te is None:
                                continue
                            tm = min([t for t in (ray(t_still, o), ray(dyn[g], o)) if t is not None], default=None)
                            if tm is not None and tm < te:
                                behind += 1
                            else:
                                vis += 1
                    av = float(a[y, x])
                    res["px"] += 1
                    res["behind_rays"] += behind
                    if vis:
                        seen.append((x, y))
                    if av >= 16 / 255 and vis == 0 and behind > 0:
                        res["fail_px"] += 1
                        res["fail_alpha_max"] = max(res["fail_alpha_max"], round(av * 255))
                        fails.append((x, y, round(av * 255)))
                    if behind and av > vis / SUB ** 2 + 0.25:
                        res["excess_px"] += 1
                for x, y, av in fails:      # how far the pixel is from one where a spark is seen (the resample's reach)
                    near_ = min((max(abs(x - u), abs(y - v)) for u, v in seen), default=None)
                    res["fails"].append(dict(layer=layer, frame=f, x=x, y=y, alpha=av, px_from_seen=near_))
        place_embers(d, 0, show=False)
        report[d] = res
        print("EMBER-CHECK", d, {k: v for k, v in res.items() if k != "fails"},
              "px_from_seen", sorted(x_["px_from_seen"] for x_ in res["fails"]), flush=True)
    with open(os.path.join(OUT, "ember-check.json"), "w") as f_:
        json.dump(dict(rule="a pixel fails when the embers draw it (alpha >= 16) and none of its 4x4 rays meets a "
                            "spark before the machine while one meets a spark behind a part; excess_px: pixels "
                            "drawn more than 0.25 above the share of rays that see a spark, where some ray "
                            "meets a spark behind a part; fails: each failing pixel, and px_from_seen its distance "
                            "(px, the larger axis) from the nearest pixel where a ray sees a spark first",
                       directions=report), f_, indent=1)


if EMBER_CHECK:
    ember_check(EMBER_CHECK)
    print("done")
    sys.exit(0)
if not IDLE and not EMBERS_ONLY:
    contract.declare(OUT, canvas=CANVAS, **DECL)
MASKS = os.path.join(os.path.dirname(os.path.abspath(OUT)), "masks")
os.makedirs(MASKS, exist_ok=True)
OTHERS = lambda *gs: tuple(g for g in GROUPS_ALL if g not in gs)      # noqa: E731
def render_embers(d, path):
    """E2 (T07d): each ember frame with every part of the machine held out at the machine's frame f // 2,
    so whatever stands nearer the camera than a spark hides it; the cinders unlit, then their light alone."""
    border(ember_window(d))
    for lit in (False, True):
        lights_off(lit)
        for f in range(NFE):
            set_pose(f // 2)
            setup(holdouts=() if EMBERS_FREE else GROUPS_ALL)
            hide_glassy_holdouts()
            place_embers(d, f, show=True, halo=lit, lit=lit)
            rig.render(path(contract.frame("embers-light" if lit else "embers", f)))
        lights_off(False)
    place_embers(d, 0, show=False)
    no_border()


if EMBERS_ONLY:
    sc.cycles.samples = ANIM_SAMPLES
    for d in ONLY:
        CUR_D[0] = d
        render_embers(d, lambda stem, d=d: os.path.join(OUT, contract.named(stem, d) + ".png"))
    print("done")
    sys.exit(0)

for d in ONLY:
    CUR_D[0] = d

    def path(stem, d=d):
        return os.path.join(OUT, contract.named(stem, d) + ".png")
    bpy.context.view_layer.update()
    no_border()
    sc.cycles.samples = PLATE_SAMPLES
    # the plate: the machine stopped -- nothing lit, no moving part, the glass full and still
    set_pose(0, glass_idle=True)
    setup(visible=PLATE_GROUPS)
    rig.render(path("idle"))
    for lg in LENSES:
        lens_cut(lg, True, LENS_LIT[lg])
        rig.render(path(lg + "-lit"))
        lens_cut(lg, False)
    # the still: the plate with every moving part at frame 0, casting on it
    set_pose(0, glass_idle=True)
    setup(visible=GROUPS_ALL)
    rig.render(path("still"))
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
        hide_glassy_holdouts()
        lens_cut(lg, True)
        rig.render(path(lg))
        lens_cut(lg, False)
    sc.cycles.samples = ANIM_SAMPLES
    # the working layers: each group alone, the rest held out; the content's light alone over it
    for g, lit in (("riser", dict(melt_lit=True)), ("glass", dict(he_lit=True))):
        border(window(members(g, d=d)))
        for f in range(NF):
            set_pose(f)
            setup(visible=(g,), holdouts=OTHERS(g))
            hide_glassy_holdouts()
            rig.render(path(contract.frame(g, f)))
        lights_off(True)
        for f in range(NF):
            set_pose(f, **lit)
            setup(visible=(g,), holdouts=OTHERS(g))
            hide_glassy_holdouts()
            rig.render(path(contract.frame(g + "-light", f)))
        lights_off(False)
    border(window(members(*MECH, d=d)))
    for f in range(NF):
        set_pose(f)
        setup(visible=MECH, holdouts=OTHERS(*MECH))
        hide_glassy_holdouts()
        rig.render(path(contract.frame("mech", f)))
    no_border()
    render_embers(d, path)
    # not packed: the stray-light map's masks (the light's own silhouettes) and the whole machine working, lit
    set_pose(0)
    for g in CONTENT:
        mask_pass(os.path.join(MASKS, f"{g}-{d}.png"), (g,))
    set_pose(0)

with open(os.path.join(OUT, "..", "model.json"), "w") as f_:
    json.dump(dict(frames=NF, speed=SPEED, south=SOUTH, sun=K.SUN_E, world=K.WORLD,
                   samples=dict(plate=PLATE_SAMPLES, anim=ANIM_SAMPLES),
                   groups={g: len(members(g)) for g in GROUPS_ALL}, moving=len(MOVING),
                   effects=effect_anchors(), pipes=check_ends()), f_, indent=1)
print("done")
