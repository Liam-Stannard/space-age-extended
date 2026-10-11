"""Siderane turbine (sae-crust-turbine), built from its spec, rendered in every pass and direction.

  blender -b --python crust_turbine.py -- <out-dir> [--idle | --collide]
  BLENDER=... tools/blender/render.sh concept/crust-turbine/model/crust_turbine.py <out-dir>

  --idle     idle- and still-<direction>.png only: the quick loop
  --collide  no render: every part against every other assembly it is not fastened to,
             and the rotor in every frame against everything fixed; prints "COLLIDE ..."
             and each clash
  $TURBINE_FLAT=1  the blockout: every material a flat colour, so the form is judged alone

Spec: concept/crust-turbine/building-spec-crust-turbine.md. The design is the adopted
Collared Pair (concept/crust-turbine/adopted/E-sheet.png) as the two master plates draw it
(master-v1.png, master-v2.png: the same machine, its camera rejected, spec 12). The model
reproduces it, read off the plates' plan:

  - a long low body lying along the long axis: a riveted let-down housing at one end, the
    rotor casing in the middle, the generator can at the other;
  - THREE MACHINED COLLARS of one design, a bright ring with a full circle of bronze bolts:
    the two end collars, identical, each with its flanged stub out to the middle of its end
    tile's edge (the two fluid connections, spec 8), and the third, on top in the middle,
    framing the rotor window -- a face pointed at the camera, so the rotor turns as the
    engine sees it (spec 9);
  - the let-down stage, a cast expansion housing low on the near flank UNDER the let-down
    end's collar, frost blooming from beneath it and running back along the body -- matte,
    never glowing, and STOPPING SHORT of the end collar (spec 11: "the frost comes off the
    collars"; template convention 5);
  - a compact generator can at the far end, low, with a brass terminal box and cleated
    cable runs; copper runs along the top and the near flank; lifting eyes;
  - a small white status lens on the middle collar's far rim, painted, not lit;
  - nothing hot, nothing glowing, no port but the two ends (spec 3.1, 11).

The prototype (prototypes/core/crust-tap.lua) is derived from the steam turbine and keeps
its boxes: a 3 x 5 footprint (selection {-1.5, -2.5}..{1.5, 2.5}), two directions, the
connections at {0, -2} north and {0, 2} south. Spec 2 says 2 x 5; the prototype is what the
engine places, so the model is 3 x 5 (the report proposes the spec's wording).

Directions: "horizontal-vertical" -- vertical as modelled (the long axis north-south, the
let-down end south), horizontal turned to face east (the let-down end west, as the plates
draw it). A generator draws one Animation per direction, so both are this one machine
turned; only BODY's place on the footprint differs (PLACE): the stubs' axis must land on
the pipe's line on the screen, and a point at height z draws z/2 tiles up the screen, so in
the horizontal direction the machine sits PLACE tiles toward the near (south) edge, as
vanilla's steam turbine draws its own.

What moves (spec 9): the rotor, behind the middle collar's window, ROTOR_FRAMES frames
through one vane pitch. The frost does not animate (spec 9). A generator has no working
visualisations (GeneratorPictures is animation and frozen_patch only), so the frost
cannot thicken with state and the lens cannot be tinted by status: the frost is in the
plate and the lens is painted (the report says so and proposes the spec's wording).

Units are tiles; north is +Y, +X is the near flank in the horizontal direction. A model
point (x, y, z) lands on screen at (x, y + z/2) tiles from the origin, facing north.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))

import rig  # noqa: E402
import contract  # noqa: E402
from materials import layered  # noqa: E402


def swatch(name):
    """This building's concept swatches: swatches/bake_concept.py."""
    return os.path.join(HERE, "swatches", f"concept_{name}.png")


argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = argv[0]
os.makedirs(OUT_DIR, exist_ok=True)
IDLE = "--idle" in argv
COLLIDE = "--collide" in argv
FLAT = os.environ.get("TURBINE_FLAT") == "1"

CANVAS = (448, 448)                  # 7 x 7 tiles: the 5-tile length either way, the shadow east
ROTOR_FRAMES = 8                     # vanilla's steam turbine runs 8
VANES = 12
DECL = dict(
    footprint=(3, 5),
    directions="horizontal-vertical",
    passes=[
        dict(name="idle", kind="plate", sheet="base"),
        dict(name="still", kind="still"),
        dict(name="shadow", kind="shadow", sheet="base-shadow"),
    ],
    # spec 9: the rotor, a face pointed at the camera; twelve vanes, so 30 degrees is a loop
    animations=[dict(name="rotor", frames=ROTOR_FRAMES, motion="turn")],
    ports=[],                        # the connections are drawn in the plate, as the steam turbine's
)

sc = rig.reset()
ROOT = rig.turntable(rig.stretch_root())

# ---------------------------------------------------------------- dimensions
ZB = 0.9                             # the long axis' height: the collars, the stubs, the generator can
R_COLLAR = 0.80                      # the end collars' rings
R_STUB = 0.27                        # the stub's pipe
R_END = 0.38                         # its end flange: 54 px tall across (horizontal), 49 wide (vertical);
                                     # vanilla's pipe ring is 52 and 51 (pipe_pictures.py's RING)
Y_END = 2.5                          # the stub's face: the middle of its end tile's edge (spec 8)
Y_COLLAR = (1.52, 2.04)              # an end collar, inner face to outer
Y_CORE = 1.52
# the stubs' axis on the pipe's line (vanilla's straight pipe: 1 px above the tile's centre)
PLACE = {"vertical": 0.0, "horizontal": ZB / 2 - 1.0 / 64}
RC = (0.0, 0.0)                      # the rotor casing's centre
R_CASE = 0.60
Z_RING = 1.52                        # the middle collar's foot; its top at Z_RING + 0.12
R_WIN = 0.44                         # the window
Z_ROTOR = 1.40                       # the rotor's disc

# ---------------------------------------------------------------- materials


def plain(name, hexcol, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb(hexcol)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


# the blockout's flat colours: each material's 3.3 hex, so the masses read as they will
FLAT_HEX = dict(body="#6E685C", body_dark="#4A463F", collar="#8A857C", gencan="#5A5047", steel="#77716A",
                bronze="#8A5A32", copper="#94592C", brass="#9C7034", frost="#A9C2D4", rotor="#4A4642",
                vane="#6A655E", recess="#221D18", lens="#E6E4DE", rubber="#7C5240", tie="#2A2826",
                seam="#6E675E", skid="#3E3A34")


def frost_material():
    """Rime: matte, pale blue-white, its crystal grain from the concept swatch and a fine
    voronoi bump -- a surface, never a light (spec 3.2, 11)."""
    # #BFD8E8, 3.3's dark end, at swatch_gain 0.8: lit by the sun it rises to 3.3's light end
    # (#E8F2F8) and no further, so it never clips to white
    m = layered("frost", "#BFD8E8", metal="#E8F2F8", paint_metal=0.0, paint_rough=0.9, wear=0.1,
                rust=0.0, dust=0.0, grime=0.5, jitter=0.08, swatch=swatch("frost"), swatch_scale=1.6,
                swatch_gain=0.8)
    t = m.node_tree
    b = t.nodes["Principled BSDF"]
    vor = t.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 90.0
    geo = t.nodes.new("ShaderNodeNewGeometry")
    t.links.new(geo.outputs["Position"], vor.inputs["Vector"])
    bump = t.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.6
    bump.inputs["Distance"].default_value = 0.01
    t.links.new(vor.outputs["Distance"], bump.inputs["Height"])
    t.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


if FLAT:
    M = {k: plain(k, v, rough=0.55) for k, v in FLAT_HEX.items()}
else:
    M = {
        # spec 3.3 body #4A463F -> #6E685C, on the concept's own swatches
        "body": layered("body", "#6E685C", paint_metal=0.1, paint_rough=0.6, wear=0.45, rust=0.3, dust=0.35,
                        grime=0.7, swatch=swatch("body"), swatch_scale=1.2, ground=0.6, ground_h=0.4,
                        drips=((1.4, 0.5),), drip=0.6),
        "body_dark": layered("body_dark", "#4A463F", paint_metal=0.1, paint_rough=0.65, wear=0.45, rust=0.3,
                             dust=0.3, grime=0.7, swatch=swatch("body_dark"), swatch_scale=1.2, ground=0.7,
                             ground_h=0.4),
        # the three collars: bare machined metal, bright, a little rust in the pits (spec 3.3 #8A857C)
        "collar": layered("collar", "#8A857C", metal="#C4BEB2", paint_metal=0.75, paint_rough=0.35, wear=0.35,
                          rust=0.22, dust=0.15, grime=0.45, swatch=swatch("collar"), swatch_scale=1.4),
        "gencan": layered("gencan", "#5A5047", paint_metal=0.1, paint_rough=0.6, wear=0.4, rust=0.25, dust=0.3,
                          grime=0.7, swatch=swatch("gencan"), swatch_scale=1.2, ground=0.6, ground_h=0.4),
        "steel": layered("steel", "#77716A", metal="#B4AEA4", paint_metal=0.8, paint_rough=0.35, wear=0.45,
                         rust=0.25, dust=0.1, grime=0.5, ground=0.6),
        # the bolts round every collar: bronze, as the plates draw them
        "bronze": layered("bronze", "#8A5A32", metal="#C88A4A", paint_metal=0.85, paint_rough=0.35, wear=0.5,
                          rust=0.15, dust=0.1, grime=0.5),
        "copper": layered("copper", "#94592C", metal="#C08452", paint_metal=0.9, paint_rough=0.38, wear=0.4,
                          rust=0.1, dust=0.15, grime=0.5, swatch=swatch("copper"), patina=0.6),
        "brass": layered("brass", "#9C7034", metal="#C49C5C", paint_metal=0.9, paint_rough=0.38, wear=0.4,
                         rust=0.15, dust=0.15, swatch=swatch("brass")),
        "frost": frost_material(),
        "rotor": layered("rotor", "#3E3A36", metal="#8A847A", paint_metal=0.8, paint_rough=0.4, wear=0.4,
                         rust=0.15, dust=0.0, grime=0.6),
        # the vanes' leading faces a step lighter, so the turning reads at 1x against the dark hub
        "vane": layered("vane", "#5E5952", metal="#A8A298", paint_metal=0.85, paint_rough=0.32, wear=0.5,
                        rust=0.1, dust=0.0, grime=0.5),
        "recess": plain("recess", "#231E19", rough=0.7),
        "lens": plain("lens", "#E6E4DE", rough=0.3),               # painted white: the engine cannot tint it
        "rubber": layered("rubber", "#7C5240", metal="#9A7A66", paint_metal=0.0, paint_rough=0.72, wear=0.15,
                          rust=0.0, dust=0.3, grime=0.6, jitter=0.06),
        "tie": plain("tie", "#2A2826", rough=0.5),
        "seam": layered("seam", "#6E675E", metal="#C8C0B2", paint_metal=0.6, paint_rough=0.45, wear=0.3,
                        rust=0.2, dust=0.0, jitter=0.04),
        "skid": layered("skid", "#3E3A34", metal="#8A847A", paint_metal=0.3, paint_rough=0.6, wear=0.5,
                        rust=0.4, dust=0.4, grime=0.8, ground=0.9, ground_h=0.2),
    }
    for _name, _hex, _edge in (("red", "#9A4632", "#C87A62"), ("black", "#3E3D39", "#7A7672"),
                               ("grey", "#6E6C66", "#9E9A92")):
        M[f"cable-{_name}"] = layered(f"cable-{_name}", _hex, metal=_edge, paint_metal=0.0, paint_rough=0.5,
                                      wear=0.3, rust=0.0, dust=0.25, grime=0.4, jitter=0.05)
if FLAT:
    for _name in ("red", "black", "grey"):
        M[f"cable-{_name}"] = plain(f"cable-{_name}", {"red": "#9A4632", "black": "#3E3D39", "grey": "#6E6C66"}[_name])

# ---------------------------------------------------------------- geometry

PARTS = {}          # group name -> [objects]; the passes toggle whole groups
ASM = {}            # object name -> its assembly, for --collide
HOSTS = {}          # assembly -> the assemblies it is fastened to (contact there is meant)
_asm = ["core"]


class assembly:
    """Everything built inside is one assembly, fastened to `on` (contact there is meant)."""

    def __init__(self, name, on=()):
        self.name, self.on = name, tuple(on)

    def __enter__(self):
        HOSTS.setdefault(self.name, set()).update(self.on)
        _asm.append(self.name)

    def __exit__(self, *a):
        _asm.pop()


BODY = bpy.data.objects.new("body", None)          # the whole machine: placed per direction (PLACE)
sc.collection.objects.link(BODY)
BODY.parent = ROOT


def _finish(obj, mat, group, bevel=0.012, smooth=False, parent=None):
    obj.data.materials.append(M[mat])
    if bevel:
        mod = obj.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    obj.parent = parent or BODY
    PARTS.setdefault(group, []).append(obj)
    ASM[obj.name] = _asm[-1]
    return obj


def box(loc, size, mat, group="static", rot=(0, 0, 0), bevel=0.012, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, group, bevel, parent=parent)


def cyl(loc, r, h, mat, group="static", verts=48, rot=(0, 0, 0), bevel=0.01, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    o = _finish(bpy.context.active_object, mat, group, bevel, smooth=True, parent=parent)
    for p in o.data.polygons:          # the caps flat: a smoothed n-gon cap shades as a dark star
        if len(p.vertices) > 4:
            p.use_smooth = False
    return o


def torus(loc, major, minor, mat, group="static", rot=(0, 0, 0), parent=None, seg=64):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, rotation=rot,
                                     major_segments=seg, minor_segments=10)
    return _finish(bpy.context.active_object, mat, group, bevel=0, smooth=True, parent=parent)


def rivet(loc, r=0.016, mat="steel", group="static", parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=8, ring_count=5)
    o = bpy.context.active_object
    o.scale.z = 0.6
    return _finish(o, mat, group, bevel=0, smooth=True, parent=parent)


def mesh_object(name, build, mat, group, bevel, smooth=False, parent=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    return _finish(o, mat, group, bevel, smooth=smooth, parent=parent)


def ring(loc, r_out, r_in, h, mat, group="static", parent=None, verts=64, bevel=0.01, rot=(0, 0, 0)):
    """A thick washer about local Z: open through the middle."""
    def build(bm):
        rows = [[bm.verts.new((r * math.cos(2 * math.pi * i / verts), r * math.sin(2 * math.pi * i / verts), z))
                 for i in range(verts)] for r, z in ((r_out, -h / 2), (r_out, h / 2), (r_in, h / 2), (r_in, -h / 2))]
        for k in range(4):
            a, b = rows[k], rows[(k + 1) % 4]
            for i in range(verts):
                j = (i + 1) % verts
                bm.faces.new((a[i], a[j], b[j], b[i]))
    o = mesh_object("ring", build, mat, group, bevel, smooth=True, parent=parent)
    o.location, o.rotation_euler = loc, rot
    return o


def pipe(pts, r, mat, bend=0.07, group="static"):
    """A rigid pipe through pts, each corner turned through an elbow of radius ~bend."""
    out = [Vector(pts[0])]
    for i in range(1, len(pts) - 1):
        p, a_, b_ = Vector(pts[i]), Vector(pts[i - 1]), Vector(pts[i + 1])
        e = min(bend, 0.45 * (a_ - p).length, 0.45 * (b_ - p).length)
        s0, s1 = p + (a_ - p).normalized() * e, p + (b_ - p).normalized() * e
        for k in range(9):
            t = k / 8
            out.append((1 - t) ** 2 * s0 + 2 * (1 - t) * t * p + t * t * s1)
    out.append(Vector(pts[-1]))
    return poly_tube(out, r, mat, group, name="pipe")


def spline(ctrl, per=10):
    """A smooth path through ctrl (Catmull-Rom), sampled densely."""
    P = [Vector(c) for c in ctrl]
    P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(per):
            t = k / per
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2])
    return out


def poly_tube(pts, r, mat, group="static", name="cable"):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for pt, co in zip(sp.points, pts):
        pt.co = (*co, 1)
    ob = bpy.data.objects.new(name, cu)
    sc.collection.objects.link(ob)
    return _finish(ob, mat, group, bevel=0)


def _arc(pts):
    s_ = [0.0]
    for a, b in zip(pts, pts[1:]):
        s_.append(s_[-1] + (b - a).length)
    return s_


def facing(v):
    return Vector(v).normalized().to_track_quat("Z", "Y").to_euler()


def ferrule(pos, direction, r):
    """A crimped hose end: a steel sleeve over the hose, pinched by two crimp rings."""
    dv = Vector(direction).normalized()
    cyl(tuple(pos), r + 0.012, 0.055, "steel", verts=20, rot=facing(dv), bevel=0.004)
    for o in (-0.014, 0.014):
        torus(tuple(Vector(pos) + dv * o), r + 0.011, 0.005, "seam", rot=facing(dv), seg=20)


def hose(ctrl, r, mat="rubber", pitch=0.034, ends=True):
    """A flexible hose, vanilla's way: corrugated, hanging through ctrl, a crimped ferrule at each end."""
    pts = spline(ctrl)
    poly_tube(pts, r, mat, name="hose")
    s_ = _arc(pts)
    nxt = 0.07
    for i in range(1, len(pts) - 1):
        if nxt <= s_[i] <= s_[-1] - 0.07:
            nxt = s_[i] + pitch
            torus(tuple(pts[i]), r + 0.002, r * 0.16, mat, rot=facing(pts[i + 1] - pts[i - 1]), seg=16)
    if ends:
        ferrule(pts[0] + (pts[3] - pts[0]).normalized() * 0.03, pts[3] - pts[0], r)
        ferrule(pts[-1] + (pts[-4] - pts[-1]).normalized() * 0.03, pts[-4] - pts[-1], r)
    return pts


def bundle(ctrl, mats, r=0.014, gap=0.03, ties=0.14, lie=(0.0, 0.0, 1.0)):
    """Insulated cables side by side through ctrl, cleated every `ties`."""
    pts = spline(ctrl)
    L = Vector(lie)
    sides, prev = [], Vector((1, 0, 0))
    for i in range(len(pts)):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        sd = t.cross(L)
        sd = sd.normalized() if sd.length > 0.2 else prev
        if sd.dot(prev) < 0:
            sd = -sd
        sides.append(sd)
        prev = sd
    n = len(mats)
    for k, m in enumerate(mats):
        off = (k - (n - 1) / 2) * gap
        poly_tube([p + sd * off for p, sd in zip(pts, sides)], r, m)
    s_ = _arc(pts)
    nxt = 0.06
    for i in range(1, len(pts) - 1):
        if nxt <= s_[i] <= s_[-1] - 0.05:
            nxt = s_[i] + ties
            bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.14, location=tuple(pts[i]),
                                             rotation=facing(pts[i + 1] - pts[i - 1]), major_segments=16,
                                             minor_segments=6)
            o = bpy.context.active_object
            o.scale = ((n - 1) / 2 * gap + r + 0.006, r + 0.006, 0.05)
            _finish(o, "steel", "static", bevel=0, smooth=True)          # a cleat
    return pts


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    e.parent = parent or BODY
    e.location, e.rotation_euler = loc, rot
    return e


def hexbolt(loc, normal, r=0.03, h=0.03, mat="bronze", group="static"):
    """A hex bolt head on a washer, standing out of a face along `normal`."""
    n = Vector(normal).normalized()
    p = Vector(loc)
    cyl(tuple(p + n * 0.004), r * 1.25, 0.008, mat, group, verts=16, rot=facing(n), bevel=0.0)
    cyl(tuple(p + n * (0.008 + h / 2)), r, h, mat, group, verts=6, rot=facing(n), bevel=0.004)


AX_Y = (math.pi / 2, 0, 0)            # a cylinder's axis along Y


def bolt_circle(y, r, n, side, mat="bronze", rb=0.03, h=0.028, phase=0.0, x0=0.0, z0=ZB):
    """n bolts round the long axis at radius r, on the face at y looking along side (+1/-1)."""
    for k in range(n):
        a = 2 * math.pi * (k + phase) / n
        hexbolt((x0 + r * math.cos(a), y, z0 + r * math.sin(a)), (0, side, 0), rb, h, mat)


# ---------------------------------------------------------------- 1. the end collars and stubs
# Identical at both ends (spec 8): a bright machined drum between two bolted rings, a short
# stub out of the outer ring to a flanged end on the middle of the end tile's edge.

def end(sign, name):
    with assembly(f"collar-{name}", on=("core", "skid")):
        y0, y1 = sign * Y_COLLAR[0], sign * Y_COLLAR[1]
        ym = (y0 + y1) / 2
        cyl((0, ym, ZB), R_COLLAR - 0.06, abs(y1 - y0) - 0.16, "collar", verts=96, rot=AX_Y, bevel=0.015)
        for yr in (y0 + sign * 0.05, y1 - sign * 0.05):                              # the two rings
            cyl((0, yr, ZB), R_COLLAR, 0.1, "collar", verts=96, rot=AX_Y, bevel=0.02)
        bolt_circle(y1, R_COLLAR - 0.075, 16, sign, rb=0.032, h=0.03)                # the outer ring's bolts
        bolt_circle(y0, R_COLLAR - 0.075, 16, -sign, rb=0.032, h=0.03, phase=0.5)    # the inner ring's
        # the drum's girth: radial bolts in a row round its middle, as the plates' collars carry them
        for k in range(14):
            a = 2 * math.pi * (k + 0.25) / 14
            nrm = (math.cos(a), 0, math.sin(a))
            hexbolt((nrm[0] * (R_COLLAR - 0.06), ym, ZB + nrm[2] * (R_COLLAR - 0.06)), nrm, 0.026, 0.022)
        cyl((0, y1 + sign * 0.01, ZB), 0.42, 0.02, "steel", verts=48, rot=AX_Y, bevel=0.004)      # the boss
    with assembly(f"stub-{name}", on=(f"collar-{name}",)):
        ya, yb = sign * (Y_COLLAR[1] + 0.02), sign * (Y_END - 0.07)
        cyl((0, (ya + yb) / 2, ZB), R_STUB, abs(yb - ya), "collar", verts=64, rot=AX_Y, bevel=0.0)
        cyl((0, ya + sign * 0.03, ZB), R_STUB + 0.07, 0.06, "collar", verts=64, rot=AX_Y, bevel=0.01)  # root flange
        bolt_circle(ya + sign * 0.06, R_STUB + 0.035, 8, sign, rb=0.02, h=0.02)
        # the end flange, its face on the tile edge: the fluid connection
        cyl((0, sign * (Y_END - 0.04), ZB), R_END, 0.08, "collar", verts=64, rot=AX_Y, bevel=0.012)
        bolt_circle(sign * (Y_END - 0.08), R_END - 0.05, 8, -sign, rb=0.022, h=0.02, phase=0.5)
        cyl((0, sign * (Y_END - 0.004), ZB), R_END - 0.07, 0.008, "steel", verts=64, rot=AX_Y, bevel=0.0)
    with assembly(f"saddle-{name}", on=(f"collar-{name}", "skid")):
        # a cast saddle under the collar, down to the skids
        ys = sign * 1.78
        prof = []
        for k in range(17):
            a = math.pi + math.pi * k / 16
            prof.append((0.62 * math.cos(a), ZB + 0.62 * math.sin(a) * 1.0))
        def build(bm, ys=ys):
            w = 0.18
            for yy in (ys - w, ys + w):
                pass
            front = [bm.verts.new((-0.62, ys - w, 0.06)), bm.verts.new((0.62, ys - w, 0.06))]
            back = [bm.verts.new((-0.62, ys + w, 0.06)), bm.verts.new((0.62, ys + w, 0.06))]
            arc_f = [bm.verts.new((x, ys - w, z)) for x, z in prof[::-1]]
            arc_b = [bm.verts.new((x, ys + w, z)) for x, z in prof[::-1]]
            # a solid: the floor up to the collar's underside
            f_loop = [front[0], front[1]] + arc_f
            b_loop = [back[0], back[1]] + arc_b
            bm.faces.new(f_loop[::-1])
            bm.faces.new(b_loop)
            for i in range(len(f_loop)):
                j = (i + 1) % len(f_loop)
                bm.faces.new((f_loop[i], f_loop[j], b_loop[j], b_loop[i]))
        mesh_object("saddle", build, "body_dark", "static", 0.015)


end(-1, "S")             # the let-down end (south as modelled; west in the horizontal direction)
end(+1, "N")             # the generator end

# ---------------------------------------------------------------- 2. the skids and the core
with assembly("skid"):
    for x in (-0.5, 0.5):
        box((x, 0, 0.04), (0.1, 4.0, 0.08), "skid", bevel=0.01)
        for y in (-1.3, -0.4, 0.4, 1.3):
            rivet((x, y, 0.085), 0.02, "steel")
    for y in (-1.0, 0.0, 1.0):
        box((0, y, 0.03), (1.1, 0.08, 0.06), "skid", bevel=0.008)

with assembly("core", on=("skid",)):
    # the inline casing the gas runs through, under everything else
    cyl((0, 0, ZB), 0.44, 2 * Y_CORE, "body_dark", verts=64, rot=AX_Y, bevel=0.01)
    for y in (-0.62, 0.62):
        torus((0, y, ZB), 0.445, 0.012, "seam", rot=AX_Y)                                   # girth welds

# ---------------------------------------------------------------- 3. the let-down housing
HL = dict(x0=-0.60, x1=0.66, y0=-Y_CORE + 0.02, y1=-0.70, z0=0.10, z1=1.42)
with assembly("housing-S", on=("core", "skid", "collar-S")):
    cx, cy = (HL["x0"] + HL["x1"]) / 2, (HL["y0"] + HL["y1"]) / 2
    box((cx, cy, (HL["z0"] + HL["z1"]) / 2), (HL["x1"] - HL["x0"], HL["y1"] - HL["y0"], HL["z1"] - HL["z0"]),
        "body", bevel=0.07)
    # riveted plate courses: a lap strap round the middle, rivet rows on the roof and near face
    box((cx, cy, 0.82), (HL["x1"] - HL["x0"] + 0.02, HL["y1"] - HL["y0"] + 0.02, 0.06), "body", bevel=0.012)
    for k in range(9):
        y = HL["y0"] + 0.08 + k * (HL["y1"] - HL["y0"] - 0.16) / 8
        rivet((HL["x1"] + 0.003, y, 0.75), 0.017, "steel")
        rivet((HL["x1"] + 0.003, y, 0.89), 0.017, "steel")
        for x in (HL["x0"] + 0.1, HL["x1"] - 0.1):
            rivet((x, y, HL["z1"] + 0.002), 0.017, "steel")
    for k in range(7):
        x = HL["x0"] + 0.1 + k * (HL["x1"] - HL["x0"] - 0.2) / 6
        rivet((x, HL["y1"] - 0.08, HL["z1"] + 0.002), 0.017, "steel")
        rivet((x, HL["y0"] + 0.08, HL["z1"] + 0.002), 0.017, "steel")
    # a bolted inspection plate on the roof
    box((0.02, cy, HL["z1"] + 0.015), (0.5, 0.42, 0.03), "body_dark", bevel=0.008)
    for sx in (-0.21, 0.21):
        for sy in (-0.17, 0.17):
            hexbolt((0.02 + sx, cy + sy, HL["z1"] + 0.03), (0, 0, 1), 0.018, 0.016, "steel")

# the let-down stage: a cast expansion housing, low on the near flank under the collar, where
# the pressure drops -- and where the frost is
LD = Vector((0.64, -1.24, 0.0))
LD_R = 0.22
with assembly("letdown", on=("housing-S", "skid")):
    cyl((LD.x, LD.y, 0.28), LD_R, 0.48, "body_dark", verts=48, bevel=0.03)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=LD_R, location=(LD.x, LD.y, 0.52), segments=32, ring_count=16)
    o = bpy.context.active_object
    o.scale.z = 0.55
    _finish(o, "body_dark", "static", bevel=0, smooth=True)
    torus((LD.x, LD.y, 0.38), LD_R + 0.005, 0.02, "steel")                                  # its cast rib
    cyl((LD.x - 0.2, LD.y, 0.38), 0.14, 0.12, "body_dark", rot=(0, math.pi / 2, 0), bevel=0.01)   # into the housing

# ---------------------------------------------------------------- 4. the rotor casing and the middle collar
with assembly("case", on=("core", "skid")):
    ZC = Z_ROTOR - 0.05                                          # the casing's solid top, under the rotor
    cyl((RC[0], RC[1], (0.06 + ZC) / 2), R_CASE, ZC - 0.06, "body", verts=96, bevel=0.02)
    ring((RC[0], RC[1], (ZC + Z_RING) / 2), R_CASE, R_WIN + 0.002, Z_RING - ZC + 0.004, "body", verts=96,
         bevel=0.0)                                              # its wall round the well
    for z in (0.35, 1.1):
        torus((RC[0], RC[1], z), R_CASE + 0.004, 0.014, "seam")
    for k in range(20):                                          # a rivet row under the collar
        a = 2 * math.pi * k / 20
        rivet((RC[0] + (R_CASE + 0.002) * math.cos(a), RC[1] + (R_CASE + 0.002) * math.sin(a), 1.32), 0.017)
    # the casing's foot: four cast lugs to the skids
    for a in (45, 135, 225, 315):
        t = math.radians(a)
        box((RC[0] + 0.58 * math.cos(t), RC[1] + 0.58 * math.sin(t), 0.12), (0.16, 0.16, 0.18), "body_dark",
            rot=(0, 0, t), bevel=0.015)
    # the recess the rotor turns in: a dark well under the window
    cyl((RC[0], RC[1], Z_ROTOR - 0.03), R_WIN + 0.005, 0.02, "recess", verts=64, bevel=0.0)
with assembly("collar-M", on=("case",)):
    ring((RC[0], RC[1], Z_RING + 0.06), 0.68, R_WIN, 0.12, "collar", verts=96, bevel=0.02)
    ring((RC[0], RC[1], Z_ROTOR + 0.05), R_WIN + 0.002, R_WIN - 0.02, Z_RING - Z_ROTOR + 0.06, "recess", verts=64,
         bevel=0.0)                                                                                # the bore
    for k in range(12):
        a = 2 * math.pi * (k + 0.5) / 12
        hexbolt((RC[0] + 0.565 * math.cos(a), RC[1] + 0.565 * math.sin(a), Z_RING + 0.12), (0, 0, 1), 0.034, 0.03)
    # the status lens on the far rim (-X: the top of the collar in the horizontal direction)
    LENS = Vector((RC[0] - 0.62, RC[1], Z_RING + 0.12))
    cyl(tuple(LENS + Vector((0, 0, 0.02))), 0.085, 0.04, "steel", verts=32, bevel=0.008)          # its bezel
    cyl(tuple(LENS + Vector((0, 0, 0.045))), 0.058, 0.015, "lens", verts=32, bevel=0.006)          # the lens

# the rotor: twelve swept vanes on a hub, under the window; turns about Z
ROTOR_AX = empty("rotor-axis", loc=(RC[0], RC[1], Z_ROTOR))
with assembly("rotor"):
    cyl((0, 0, 0.0), R_WIN - 0.03, 0.02, "rotor", "rotor", verts=64, bevel=0.0, parent=ROTOR_AX)
    cyl((0, 0, 0.05), 0.09, 0.09, "rotor", "rotor", verts=32, bevel=0.01, parent=ROTOR_AX)          # the hub
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(0, 0, 0.1), segments=24, ring_count=12)
    o = bpy.context.active_object
    o.scale.z = 0.6
    _finish(o, "vane", "rotor", bevel=0, smooth=True, parent=ROTOR_AX)                              # the nose

    def vane_build(bm, k):
        """One vane: a swept strip from the hub to the rim, twisted, 0.07 tall."""
        a0 = 2 * math.pi * k / VANES
        rows = []
        n = 8
        for i in range(n + 1):
            f = i / n
            r = 0.09 + f * (R_WIN - 0.06 - 0.09)
            a = a0 + 0.9 * f ** 1.2                       # swept back
            t = 0.012
            # the vane's two faces, offset across the sweep
            for side in (-1, 1):
                rows.append((r, a + side * t / r, side))
        lo, hi = 0.01, 0.075
        vs = {}
        for i in range(n + 1):
            for j, side in enumerate((-1, 1)):
                r, a, _ = rows[2 * i + j]
                for zk, z in enumerate((lo, hi - 0.03 * (i / n))):
                    vs[(i, j, zk)] = bm.verts.new((r * math.cos(a), r * math.sin(a), z))
        for i in range(n):
            for j in range(2):
                bm.faces.new((vs[(i, j, 0)], vs[(i + 1, j, 0)], vs[(i + 1, j, 1)], vs[(i, j, 1)]))
            bm.faces.new((vs[(i, 0, 1)], vs[(i + 1, 0, 1)], vs[(i + 1, 1, 1)], vs[(i, 1, 1)]))
            bm.faces.new((vs[(i, 1, 0)], vs[(i + 1, 1, 0)], vs[(i + 1, 0, 0)], vs[(i, 0, 0)]))
        for i in (0, n):
            bm.faces.new((vs[(i, 0, 0)], vs[(i, 1, 0)], vs[(i, 1, 1)], vs[(i, 0, 1)]))
    for k in range(VANES):
        o = mesh_object("vane", lambda bm, k=k: vane_build(bm, k), "vane", "rotor", 0.0, parent=ROTOR_AX)
    torus((0, 0, 0.03), R_WIN - 0.045, 0.012, "rotor", "rotor", parent=ROTOR_AX)                   # the shroud

# ---------------------------------------------------------------- 5. the generator can
GC = dict(y0=0.78, y1=Y_CORE - 0.02, r=0.60)
with assembly("gencan", on=("core", "skid", "collar-N")):
    cyl((0, (GC["y0"] + GC["y1"]) / 2, ZB), GC["r"], GC["y1"] - GC["y0"], "gencan", verts=96, rot=AX_Y, bevel=0.03)
    for y in (GC["y0"] + 0.06, GC["y1"] - 0.06):
        cyl((0, y, ZB), GC["r"] + 0.025, 0.07, "gencan", verts=96, rot=AX_Y, bevel=0.01)          # end bands
        for k in range(18):
            a = 2 * math.pi * k / 18
            rivet((0.0 + (GC["r"] + 0.028) * math.cos(a), y, ZB + (GC["r"] + 0.028) * math.sin(a)), 0.016)
    # cooling ribs along its top
    for k in range(7):
        a = math.radians(60 + k * 10)
        nrm = Vector((math.cos(a), 0, math.sin(a)))
        c = Vector((0, (GC["y0"] + GC["y1"]) / 2, ZB)) + nrm * (GC["r"] + 0.02)
        box(tuple(c), (0.02, GC["y1"] - GC["y0"] - 0.24, 0.05), "gencan", rot=(0, -(math.pi / 2 - a), 0),
            bevel=0.005)
    # its feet
    for y in (GC["y0"] + 0.15, GC["y1"] - 0.15):
        box((0, y, 0.2), (0.9, 0.12, 0.28), "body_dark", bevel=0.015)
# a valve column between the casing and the can
with assembly("column", on=("core", "case", "gencan")):
    cyl((-0.45, 0.76, 1.25), 0.07, 0.6, "steel", verts=24, bevel=0.006)
    cyl((-0.45, 0.76, 1.2), 0.11, 0.16, "body_dark", verts=24, bevel=0.01)                          # the valve body
    cyl((-0.45, 0.76, 1.56), 0.06, 0.03, "steel", verts=24, bevel=0.004)
    cyl((-0.45, 0.76, 1.59), 0.09, 0.012, "steel", verts=6, bevel=0.0)                              # the handwheel nut
    torus((-0.45, 0.76, 1.6), 0.1, 0.012, "steel", seg=32)                                           # the handwheel

# the terminal box, brass, on the can's near flank, low
TB = Vector((0.68, 1.1, 0.72))
with assembly("terminal", on=("gencan",)):
    box(tuple(TB), (0.18, 0.4, 0.42), "brass", bevel=0.02)
    box(tuple(TB + Vector((0.095, 0, 0))), (0.02, 0.34, 0.36), "brass", bevel=0.01)                  # its lid
    for sy in (-0.13, 0.13):
        for sz in (-0.13, 0.13):
            hexbolt(tuple(TB + Vector((0.105, sy, sz))), (1, 0, 0), 0.014, 0.012, "steel")
    for k, sy in enumerate((-0.1, 0.0, 0.1)):                                                      # cable glands
        cyl(tuple(TB + Vector((0.0, sy, -0.23))), 0.024, 0.05, "steel", verts=6, bevel=0.003)

# ---------------------------------------------------------------- 6. the runs
# the top: a copper line and a steel line along the far side, housing to can, cleated down
TOPZ = 1.48
with assembly("runs-top", on=("housing-S", "case", "core", "gencan", "column", "collar-M")):
    pipe([(-0.42, -1.2, HL["z1"] + 0.02), (-0.42, -1.2, TOPZ + 0.06), (-0.75, -0.9, TOPZ + 0.06),
          (-0.75, 0.0, TOPZ + 0.06), (-0.75, 0.8, TOPZ + 0.06), (-0.4, 1.0, TOPZ + 0.06),
          (-0.4, 1.0, ZB + GC["r"] - 0.02)], 0.042, "copper", bend=0.12)
    pipe([(-0.22, -1.32, HL["z1"] + 0.02), (-0.22, -1.32, TOPZ), (-0.56, -0.74, TOPZ),
          (-0.58, -0.4, TOPZ), (-0.58, 0.38, TOPZ), (-0.45, 0.76, TOPZ), (-0.45, 0.76, 1.55)], 0.032, "steel",
         bend=0.1)
    for y in (-0.42, 0.42):                                       # brackets off the casing hold the run
        box((-0.60, y, 1.0), (0.34, 0.04, 0.05), "steel", bevel=0.005)
        box((-0.75, y, 1.26), (0.04, 0.04, 0.5), "steel", bevel=0.005)
        box((-0.75, y, TOPZ + 0.06), (0.11, 0.05, 0.11), "steel", bevel=0.006)              # the cleat
    for (x, y, z) in ((-0.42, -1.2, HL["z1"] + 0.02), (-0.22, -1.32, HL["z1"] + 0.02),
                      (-0.4, 1.0, ZB + GC["r"] - 0.02)):
        cyl((x, y, z + 0.015), 0.07, 0.03, "steel", verts=24, bevel=0.005)                          # pads
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            hexbolt((x + 0.052 * math.cos(a), y + 0.052 * math.sin(a), z + 0.03), (0, 0, 1), 0.01, 0.01, "steel")
# the near flank, low: the gas line from the let-down stage into the rotor casing, flanged
with assembly("runs-near", on=("letdown", "housing-S", "case", "terminal", "gencan", "skid", "saddle-N")):
    GL0 = Vector((LD.x - 0.04, LD.y + LD_R - 0.04, 0.3))
    pipe([tuple(GL0), (0.78, -0.72, 0.3), (0.62, -0.42, 0.3), (0.52, -0.3, 0.3)], 0.06, "copper", bend=0.18)
    for y in (-0.62,):
        cyl((0.72, y, 0.3), 0.095, 0.05, "steel", verts=24, rot=facing((-0.3, 0.9, 0)), bevel=0.008)
    pipe([(LD.x + 0.02, LD.y + 0.2, 0.5), (0.86, -0.7, 0.52), (0.72, -0.5, 0.52), (0.58, -0.34, 0.52)],
         0.032, "copper", bend=0.12)
    # the lube and sensing lines from the casing to the terminal box
    pipe([(0.56, 0.3, 0.42), (0.7, 0.5, 0.42), (0.74, 0.82, 0.42), (0.74, 0.92, 0.5)], 0.026, "copper", bend=0.1)
    pipe([(0.5, 0.36, 0.3), (0.66, 0.56, 0.3), (0.72, 0.86, 0.3), (0.72, 0.96, 0.37)], 0.022, "copper", bend=0.1)
    # cleated cables out of the box's glands, along the can's flank to the far collar's foot
    bundle([tuple(TB + Vector((0.0, -0.0, -0.25))), (0.7, 1.14, 0.3), (0.66, 1.3, 0.2), (0.58, 1.5, 0.18),
            (0.5, 1.62, 0.2)], ["cable-black", "cable-red", "cable-grey"], r=0.016, gap=0.034,
           lie=(1, 0, 0.3))
    # a corrugated hose: the let-down's bleed, along the near flank into the casing's foot
    hose([(LD.x + 0.1, LD.y + 0.14, 0.42), (0.92, -0.8, 0.36), (0.86, -0.5, 0.2), (0.62, -0.3, 0.16),
          (0.5, -0.28, 0.16)], 0.032)

# the lifting eyes: on the housing and the can, far side (spec: as the plates draw them)
with assembly("eyes", on=("housing-S", "gencan", "case")):
    for x, y, z in ((-0.5, -1.42, HL["z1"]), (-0.36, 1.3, ZB + GC["r"] - 0.03)):
        box((x, y, z + 0.09), (0.05, 0.18, 0.18), "body_dark", bevel=0.02)
        torus((x, y, z + 0.19), 0.06, 0.02, "steel", rot=(0, math.pi / 2, 0), seg=32)

# ---------------------------------------------------------------- 7. the frost (spec 3.2, signature)
# On the let-down stage and the body behind it, matte, never on either end collar: it stops
# at FROST_STOP, 0.08 short of the let-down collar's inner face (spec 11).
FROST_STOP = -Y_CORE + 0.08
FROST = random.Random(23)
with assembly("frost", on=("letdown", "housing-S", "skid", "runs-near", "core")):
    def clump(c, r, squash=0.6):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=r, location=tuple(c))
        o = bpy.context.active_object
        o.scale = (1.0 + FROST.uniform(-0.2, 0.3), 1.0 + FROST.uniform(-0.2, 0.3), squash)
        tx = bpy.data.textures.new("rime", "VORONOI")
        tx.noise_scale = 0.03
        d = o.modifiers.new("rime", "DISPLACE")
        d.texture = tx
        d.strength = r * 0.35
        d.texture_coords = "GLOBAL"
        return _finish(o, "frost", "static", bevel=0, smooth=False)
    # the stage itself: rime crusted over its dome and down its flank, not a solid coat
    for _ in range(140):
        a = FROST.uniform(-math.pi, math.pi)
        el = FROST.uniform(0.0, 1.35)
        if a < -2.4 or a > 2.4:
            continue                                                  # its back, against the housing
        c = Vector((LD.x + (LD_R + 0.004) * math.cos(a) * math.cos(el),
                    LD.y + (LD_R + 0.004) * math.sin(a) * math.cos(el), 0.52 + LD_R * 0.55 * math.sin(el)))
        if el < 0.2:
            c.z = FROST.uniform(0.08, 0.5)
        if c.y > FROST_STOP + 0.04:
            clump(c, FROST.uniform(0.018, 0.04), 0.9)
    # blooming from beneath it onto the ground: low, small crystals
    for _ in range(50):
        a = FROST.uniform(-1.9, 1.9)
        rr = LD_R + FROST.uniform(-0.02, 0.1)
        c = Vector((LD.x + rr * math.cos(a), LD.y + rr * math.sin(a), FROST.uniform(0.0, 0.03)))
        if c.y > FROST_STOP + 0.05:
            clump(c, FROST.uniform(0.02, 0.045), 0.4)
    # and running back along the housing's near face and up over its near roof edge, thinning
    for _ in range(130):
        y = FROST.uniform(FROST_STOP + 0.05, -0.62)
        f = (y - FROST_STOP) / (-0.62 - FROST_STOP)                     # 0 at the stage, 1 at its end
        if FROST.random() < f * 0.6:
            continue
        z = FROST.uniform(0.1, HL["z1"] * (1 - 0.6 * f))
        if z > HL["z1"] - 0.08:                                         # on the roof's near margin
            c = Vector((HL["x1"] - FROST.uniform(0.0, 0.18), y, HL["z1"] + 0.004))
        else:
            c = Vector((HL["x1"] + 0.004, y, z))
        if y > HL["y1"]:
            c.x = 0.5 + FROST.uniform(0, 0.03)
            c.z = min(c.z, 0.5)
        clump(c, FROST.uniform(0.015, 0.04) * (1 - 0.4 * f), 0.7)

# ---------------------------------------------------------------- passes

SUN = rig.sun()
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()


def setup(visible=(), catchers=(), holdouts=(), ground=False):
    """Per pass: which groups the camera sees, catch shadow on, or cut out."""
    for g, objs in PARTS.items():
        for o in objs:
            o.hide_render = g not in visible and g not in catchers and g not in holdouts
            o.is_shadow_catcher = g in catchers
            o.is_holdout = g in holdouts
            o.visible_camera = True
    GROUND.hide_render = not ground
    BOUNCE.hide_render = ground


def pose(f):
    ROTOR_AX.rotation_euler.z = -2 * math.pi / VANES * f / ROTOR_FRAMES


def pin_textures():
    """materials.layered samples world position, so a turning rotor would slide under its own
    finish: each rotor part gets its own copy of its material, read in the part's own
    coordinates carried to where it stands in frame 0 (the Gas Pump's way)."""
    for o in PARTS["rotor"]:
        if not o.data.materials:
            continue
        m = o.data.materials[0].copy()
        t = m.node_tree
        geos = [nd for nd in t.nodes if nd.bl_idname == "ShaderNodeNewGeometry"]
        if not geos:
            continue
        tc, mp = t.nodes.new("ShaderNodeTexCoord"), t.nodes.new("ShaderNodeMapping")
        loc, rot, sca = o.matrix_world.decompose()
        mp.inputs["Location"].default_value = loc
        mp.inputs["Rotation"].default_value = rot.to_euler()
        mp.inputs["Scale"].default_value = sca
        t.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        for nd in geos:
            for lk in list(nd.outputs["Position"].links):
                t.links.new(mp.outputs["Vector"], lk.to_socket)
        o.data.materials[0] = m


bpy.context.view_layer.update()
pose(0)
bpy.context.view_layer.update()
if not FLAT:
    pin_textures()

if COLLIDE:
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get()

    def tree(objs):
        verts, polys = [], []
        for o in objs:
            if o.type not in ("MESH", "CURVE"):
                continue
            ev = o.evaluated_get(dg)
            me = ev.to_mesh()
            mw = ev.matrix_world
            base = len(verts)
            verts.extend(mw @ v.co for v in me.vertices)
            polys.extend([base + i for i in pl.vertices] for pl in me.polygons)
            ev.to_mesh_clear()
        return BVHTree.FromPolygons(verts, polys) if polys else None

    fixed = [o for g, objs in PARTS.items() if g != "rotor" for o in objs]
    by_asm = {}
    for o in fixed:
        by_asm.setdefault(ASM[o.name], []).append(o)
    trees = {a: tree(objs) for a, objs in by_asm.items()}

    def meant(a, b):
        return a == b or b in HOSTS.get(a, ()) or a in HOSTS.get(b, ())
    clashes = []
    names = sorted(trees)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if meant(a, b) or trees[a] is None or trees[b] is None:
                continue
            hits = trees[a].overlap(trees[b])
            if hits:
                clashes.append((a, b, len(hits)))
    for a, b, n in clashes:
        print(f"COLLIDE {a} x {b}: {n} face pairs")
    rotor_hits = {}
    for f in range(ROTOR_FRAMES):
        pose(f)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        rt = tree(PARTS["rotor"])
        for a in names:
            if trees[a] is not None and rt.overlap(trees[a]):
                rotor_hits.setdefault(a, []).append(f)
    for a, fs in rotor_hits.items():
        print(f"COLLIDE rotor x {a}: frames {fs}")
    print(f"COLLIDE assemblies {len(names)}, fixed clashes {len(clashes)}, rotor clashes {len(rotor_hits)}")
    sys.exit(0)

contract.declare(OUT_DIR, canvas=CANVAS, **DECL)
rig.camera(*CANVAS)


def window(x0, x1, y0, y1):
    """Render only a window of the canvas: screen tiles from the origin, x right, y down."""
    cw, ch = CANVAS
    sc.render.use_border, sc.render.use_crop_to_border = True, False
    sc.render.border_min_x = (cw / 2 + x0 * rig.PX_PER_TILE) / cw
    sc.render.border_max_x = (cw / 2 + x1 * rig.PX_PER_TILE) / cw
    sc.render.border_max_y = 1 - (ch / 2 + y0 * rig.PX_PER_TILE) / ch
    sc.render.border_min_y = 1 - (ch / 2 + y1 * rig.PX_PER_TILE) / ch


STATIC = ("static",)
MOVING = ("rotor",)
ROT = DECL["animations"][0]
if FLAT or IDLE:
    sc.cycles.samples = int(os.environ.get("SAMPLES", "24" if FLAT else "48"))

for d in contract.each_direction(ROOT, DECL["directions"]):
    def path(stem, d=d):
        return f"{OUT_DIR}/{contract.named(stem, d)}.png"
    BODY.location.x = PLACE[d]
    sc.render.use_border = False
    pose(0)
    # the plate leaves the rotor out: the engine draws it, frame by frame, in its window
    setup(visible=STATIC)
    rig.render(path("idle"))
    setup(visible=STATIC + MOVING)
    rig.render(path("still"))
    if IDLE:
        continue
    setup(visible=STATIC + MOVING, ground=True)
    for o in [o for objs in PARTS.values() for o in objs]:
        o.visible_camera = False
    rig.render(path("shadow"))
    for o in [o for objs in PARTS.values() for o in objs]:
        o.visible_camera = True
    # the rotor: its window only, its shadow caught on the bore and the well under it
    east, north = (0.0, 0.0) if d == "vertical" else (0.0, -PLACE[d])
    sy = -(north + Z_ROTOR / 2)
    window(east - 0.62, east + 0.62, sy - 0.5, sy + 0.5)
    for f in range(ROT["frames"]):
        pose(f)
        setup(visible=MOVING, catchers=STATIC)
        rig.render(path(contract.frame(ROT["name"], f)))
    pose(0)
    sc.render.use_border = False
BODY.location.x = 0.0
