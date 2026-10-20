"""Siderane turbine (sae-crust-turbine), built from its spec, rendered in every pass and direction.

  blender -b --python crust_turbine.py -- <out-dir> [--idle | --collide | --icon]
  BLENDER=... tools/blender/render.sh concept/crust-turbine/model/crust_turbine.py <out-dir> [--icon]

  --idle     idle- and still-<direction>.png only: the quick loop
  --collide  no render: every part against every other assembly it is not fastened to,
             and the rotor in every frame against everything fixed; prints "COLLIDE ..."
             and each clash
  --icon     icon.png: the machine, horizontal, on transparency at 1024 px
  --wreck    wreck-<direction>.png only (section 10): the quick loop for the wreck
  $TURBINE_FLAT=1  the blockout: every material a flat colour, so the form is judged alone

Round 2 (Liam, 2026-10-11, on round 1's review.png): "Remove the frost from the turbine and
add some bulk. The 3x5 is fine." Round 1 is kept beside this file in round-1/.

Spec: concept/crust-turbine/building-spec-crust-turbine.md. The design is the adopted
Collared Pair (concept/crust-turbine/adopted/E-sheet.png, master-v1.png, master-v2.png),
read off the plates' plan and made heavier to fill the 3-tile depth:

  - THREE MACHINED COLLARS of one design, a bright ring with a full circle of bronze bolts:
    the two end collars, identical, each with its flanged stub out to the middle of its end
    tile's edge (the two fluid connections, spec 8), and the third on top in the middle,
    framing the rotor window -- the rotor is round 1's, unchanged (spec 9);
  - between them, the body: at the let-down end a cast housing under a round bonnet, with
    the let-down stage, a cast expansion bell, on its near flank; in the middle the rotor
    casing over a wider volute drum; at the far end the generator can, as wide as the
    collars;
  - the mass round them, vanilla's way: a lagged balance line and a cable tray on stands
    along the far flank, a steel terminal box with a brass lid at the generator end, braces
    down to the ground, hoses and cleated cables on the near flank;
  - the signature, without frost (round 2's proposal): THREE PORCELAIN BUSHINGS on the
    generator can, copper bus out of them to the terminal box -- the machine's output
    plainly electricity, glazed and dry, nothing hot -- and a gauge pair on the let-down
    stage, one needle high and one low: the pressure difference that is the whole machine;
  - the status lens: glass, unlit, on the middle collar's far rim; its white cut is the
    `lens` light pass (spec 3.3: "the status lens the engine tints");
  - no frost, rime or ice anywhere; nothing hot, nothing glowing; no port but the two ends.

The prototype (prototypes/core/crust-tap.lua) is derived from the steam turbine and keeps
its boxes: a 3 x 5 footprint (selection {-1.5, -2.5}..{1.5, 2.5}), two directions, the
connections at {0, -2} north and {0, 2} south.

Directions: "horizontal-vertical" -- vertical as modelled (the long axis north-south, the
let-down end south), horizontal turned to face east (the let-down end west, as the plates
draw it). A generator draws one Animation per direction, so both are this one machine
turned; BODY's place on the footprint differs (PLACE, SOUTH): the stubs' axis must land on
the pipe's line on the screen, and a point at height z draws z/2 tiles up the screen, so in
the horizontal direction the machine sits PLACE tiles toward the near (south) edge, as
vanilla's steam turbine draws its own. So the machine's ground plan is held to
x in [-1.5, 1.5 - PLACE]: the far flank (-x) may reach the footprint's edge in both
directions, the near flank (+x) stops PLACE short of it.

The vertical direction's ends (amendment, 2026-10-11: north-south pipes did not meet the
turbine): the machine sits SOUTH tiles south, so the south flange's lowest pixel is on the
footprint edge where vanilla's pipe meets it; the north collar is cut back to its two rings
and the north stub runs from them to the tile edge, its flange over the north pipe's end;
both ends are section 1's spigot and flange (amendment 2). These parts are the vertical direction's own
(section 8, `only`); the horizontal direction and the icon draw exactly what they did.

What moves (spec 9): the rotor, behind the middle collar's window, ROTOR_FRAMES frames
through one vane pitch. A generator has no working visualisations (GeneratorPictures is
animation and frozen_patch only): the lens pass is packed for whoever wires it, and the
report says the engine has no slot to draw it in.

Units are tiles; north is +Y, +X is the near flank in the horizontal direction. A model
point (x, y, z) lands on screen at (x, y + z/2) tiles from the origin, facing north.
"""
import math
import os
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
ICON = "--icon" in argv
WRECK_ONLY = "--wreck" in argv
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
        # spec 3.3: the status lens, cut white for the engine to tint
        dict(name="lens", kind="light", sheet="status-lens"),
        # section 10: the wreck the corpse draws, its shadow and scorch baked in, on its own canvas
        dict(name="wreck", kind="remnants", sheet="remnants", canvas=(576, 576)),
    ],
    # spec 9: the rotor, a face pointed at the camera; twelve vanes, so 30 degrees is a loop
    animations=[dict(name="rotor", frames=ROTOR_FRAMES, motion="turn")],
    ports=[],                        # the connections are drawn in the plate, as the steam turbine's
)

sc = rig.reset()
ROOT = rig.turntable(rig.stretch_root())

# ---------------------------------------------------------------- dimensions
ZB = 0.96                            # the long axis' height: the collars, the stubs, the generator can
R_COLLAR = 0.94                      # the end collars' rings: 1.9 tiles across, the body's girth
# The connections (amendment 2, 2026-10-11, Liam: "There is still a gap between the joints"):
# a pipe laid at either end must meet turbine metal across its whole width, so the stub is a
# spigot at least vanilla's pipe wide all the way from the collar to the edge -- vanilla's
# straight pipe is 51 px across its end ring and 42 px across its body seen end-on (vertical),
# 55 px over its ring and 49-50 px over its body seen side-on (horizontal; a round section
# draws 2.24 R tall there) -- and its end flange stands proud of the pipe's ring, as the
# Vacuum Furnace's ports do. R_STUB 0.41: 52.5 px end-on, 58.7 px side-on.
R_STUB = 0.41                        # the stub: a spigot the pipe's full width
R_END = 0.46                         # its end flange: proud of vanilla's ring (59 / 66 px)
FACE_OUT = 0.004                     # east-west: the end flange's face a quarter pixel past the edge
Y_END = 2.5                          # the stub's face: the middle of its end tile's edge (spec 8)
Y_COLLAR = (1.50, 2.08)              # an end collar, inner face to outer
# the stubs' axis on the pipe's line (vanilla's straight pipe: 1 px above the tile's centre)
PLACE = {"vertical": 0.0, "horizontal": ZB / 2 - 1.0 / 64}
# The vertical direction's two ends (amendment 2026-10-11, Liam: "pipes don't connect to the
# turbine properly when going north to south"). Vanilla's vertical pipe ends on the screen
# where its tile meets ours: the south pipe's top ring 140..158 px below the origin, the north
# pipe's bottom ring 160..176 px above it. A stub on the long axis draws ZB/2 tiles up the
# screen, so, as the horizontal direction moves the machine PLACE toward the camera, the
# vertical one moves it SOUTH tiles south: the south flange's lowest pixel lands on 2.5 tiles
# (160 px), the north flange's ring over the north pipe's end. The north collar would still
# hide that ring (its crown draws 0.95 tiles above its outer face), so in this direction only
# it is cut back to its two rings (Y_COLLAR_NV) and its stub runs out to the tile edge.
R_END_V = R_END                      # the vertical direction's end flanges: the same as east-west
SOUTH = {"vertical": (ZB - R_END_V) / 2, "horizontal": 0.0}
Y_COLLAR_NV = (1.50, 1.75)           # the vertical direction's north collar, cut back to its rings
X_NEAR = 1.5 - PLACE["horizontal"] - 0.03     # the near flank's limit on the ground
X_FAR = -1.46                                 # the far flank's
RC = (0.0, 0.0)                      # the rotor casing's centre
R_CASE = 0.80                        # the casing under the middle collar
R_VOLUTE = 0.92                      # the volute drum under that
Z_RING = 1.52                        # the middle collar's foot (round 1's: the rotor is unchanged)
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


def lens_material():
    """The status lens: smoked glass, unlit -- never painted a colour. A value node, "white",
    turns it to a flat white emitter for the light pass the engine tints (spec 3.3)."""
    m = bpy.data.materials.new("lens")
    m.use_nodes = True
    t = m.node_tree
    b = t.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#2E3133")
    b.inputs["Roughness"].default_value = 0.12
    b.inputs["Metallic"].default_value = 0.0
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Emission Color"].default_value = (1, 1, 1, 1)
    white = t.nodes.new("ShaderNodeValue")
    white.name = "white"
    white.outputs[0].default_value = 0.0
    t.links.new(white.outputs[0], b.inputs["Emission Strength"])
    return m


# the blockout's flat colours: each material's 3.3 hex, so the masses read as they will
FLAT_HEX = dict(body="#6E685C", body_dark="#4A463F", collar="#8A857C", gencan="#5A5047", steel="#77716A",
                bronze="#8A5A32", copper="#94592C", brass="#9C7034", rotor="#4A4642", vane="#6A655E",
                recess="#221D18", rubber="#7C5240", tie="#2A2826", seam="#6E675E", skid="#3E3A34",
                lagging="#6A6457", porcelain="#B8AE98", dial="#CFC7B4")
if FLAT:
    M = {k: plain(k, v, rough=0.55) for k, v in FLAT_HEX.items()}
    for _name, _hex in (("red", "#9A4632"), ("black", "#3E3D39"), ("grey", "#6E6C66")):
        M[f"cable-{_name}"] = plain(f"cable-{_name}", _hex)
else:
    M = {
        # spec 3.3 body #4A463F -> #6E685C, on the concept's own swatches. Dry: no drips
        "body": layered("body", "#6E685C", paint_metal=0.1, paint_rough=0.6, wear=0.45, rust=0.3, dust=0.35,
                        grime=0.7, swatch=swatch("body"), swatch_scale=1.2, ground=0.6, ground_h=0.4),
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
        "bronze": layered("bronze", "#8A5A32", metal="#C88A4A", paint_metal=0.85, paint_rough=0.35, wear=0.5,
                          rust=0.15, dust=0.1, grime=0.5),
        "copper": layered("copper", "#94592C", metal="#C08452", paint_metal=0.9, paint_rough=0.38, wear=0.4,
                          rust=0.1, dust=0.15, grime=0.5, swatch=swatch("copper"), patina=0.6),
        "brass": layered("brass", "#9C7034", metal="#C49C5C", paint_metal=0.9, paint_rough=0.38, wear=0.4,
                         rust=0.15, dust=0.15, swatch=swatch("brass")),
        "rotor": layered("rotor", "#3E3A36", metal="#8A847A", paint_metal=0.8, paint_rough=0.4, wear=0.4,
                         rust=0.15, dust=0.0, grime=0.6),
        "vane": layered("vane", "#5E5952", metal="#A8A298", paint_metal=0.85, paint_rough=0.32, wear=0.5,
                        rust=0.1, dust=0.0, grime=0.5),
        "recess": plain("recess", "#231E19", rough=0.7),
        "rubber": layered("rubber", "#7C5240", metal="#9A7A66", paint_metal=0.0, paint_rough=0.72, wear=0.15,
                          rust=0.0, dust=0.3, grime=0.6, jitter=0.06),
        "tie": plain("tie", "#2A2826", rough=0.5),
        "seam": layered("seam", "#6E675E", metal="#C8C0B2", paint_metal=0.6, paint_rough=0.45, wear=0.3,
                        rust=0.2, dust=0.0, jitter=0.04),
        "skid": layered("skid", "#3E3A34", metal="#8A847A", paint_metal=0.3, paint_rough=0.6, wear=0.5,
                        rust=0.4, dust=0.4, grime=0.8, ground=0.9, ground_h=0.2),
        # the balance line's lagging: tarred canvas under steel bands, dark and matte
        "lagging": layered("lagging", "#5E584C", metal="#7A7264", paint_metal=0.0, paint_rough=0.9, wear=0.2,
                           rust=0.05, dust=0.45, grime=0.8, jitter=0.06),
        # the signature: glazed porcelain, a dry cream-grey, glossy, chipped at the sheds' edges
        "porcelain": layered("porcelain", "#B4AA94", metal="#6E6658", paint_metal=0.0, paint_rough=0.22,
                             wear=0.15, rust=0.0, dust=0.25, grime=0.5, jitter=0.04),
        "dial": layered("dial", "#A49C88", metal="#A49C88", paint_metal=0.0, paint_rough=0.4, wear=0.0,
                        rust=0.0, dust=0.2, grime=0.4, jitter=0.02),
    }
    for _name, _hex, _edge in (("red", "#9A4632", "#C87A62"), ("black", "#3E3D39", "#7A7672"),
                               ("grey", "#6E6C66", "#9E9A92")):
        M[f"cable-{_name}"] = layered(f"cable-{_name}", _hex, metal=_edge, paint_metal=0.0, paint_rough=0.5,
                                      wear=0.3, rust=0.0, dust=0.25, grime=0.4, jitter=0.05)
M["lens"] = lens_material()
# the vertical south stub (section 9): vanilla's straight pipe's tone, olive-grey, its highlight
# broad (pipe-straight-vertical's body: mean #837F6A); made last, so every material above is as it was
M["pipe"] = M["collar"] if FLAT else layered("pipe", "#837E66", metal="#ABA38C", paint_metal=0.6, paint_rough=0.5,
                                             wear=0.3, rust=0.3, dust=0.15, grime=0.5)

# ---------------------------------------------------------------- geometry

PARTS = {}          # group name -> [objects]; the passes toggle whole groups
ASM = {}            # object name -> its assembly, for --collide
HOSTS = {}          # assembly -> the assemblies it is fastened to (contact there is meant)
_asm = ["core"]
ONLY = {}           # object name -> the one direction it is drawn in (None: both)
_only = [None]
CUR = [None]        # the direction being rendered
# the wreck (section 10) only: the group its parts go in and the frame they are built in;
# None, as for every part of the machine, keeps _finish's own
_group = [None]
_parent = [None]


class only:
    """Everything built inside is drawn in one direction alone: the vertical ends."""

    def __init__(self, direction):
        self.direction = direction

    def __enter__(self):
        _only.append(self.direction)

    def __exit__(self, *a):
        _only.pop()


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
    obj.parent = parent or _parent[-1] or BODY
    group = _group[-1] or group
    PARTS.setdefault(group, []).append(obj)
    ASM[obj.name] = _asm[-1]
    ONLY[obj.name] = _only[-1]
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


def strut(p0, p1, w, d, mat="steel", bevel=0.008):
    """A straight member from p0 to p1, w x d in section."""
    a, b = Vector(p0), Vector(p1)
    bpy.ops.mesh.primitive_cube_add(size=1, location=tuple((a + b) / 2), rotation=facing(b - a))
    o = bpy.context.active_object
    o.scale = (w, d, (b - a).length)
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, "static", bevel)


def foot_plate(x, y, w=0.16, bolts=True):
    """A plate on the ground with its two anchor bolts."""
    box((x, y, 0.012), (w, w, 0.024), "skid", bevel=0.004)
    if bolts:
        for s in (-1, 1):
            hexbolt((x + s * w * 0.32, y, 0.024), (0, 0, 1), 0.016, 0.014, "steel")


# ---------------------------------------------------------------- 1. the end collars and stubs
# Identical at both ends (spec 8): a bright machined drum between two bolted rings, a short
# stub out of the outer ring to a flanged end on the middle of the end tile's edge.

def end(sign, name, y_collar=Y_COLLAR, r_end=R_END, ys=1.79, w=0.17, parts=("collar", "stub", "saddle"),
        square=False):
    """One end. The defaults are both ends in the horizontal direction (and the south collar
    and saddle in the vertical); the vertical direction's own parts pass theirs."""
    if "collar" in parts:
        collar(sign, name, y_collar)
    if "stub" in parts:
        stub(sign, name, y_collar, r_end, square)
    if "saddle" in parts:
        saddle(sign, name, ys, w)


def collar(sign, name, y_collar):
    with assembly(f"collar-{name}", on=("core", "skid")):
        y0, y1 = sign * y_collar[0], sign * y_collar[1]
        ym = (y0 + y1) / 2
        cyl((0, ym, ZB), R_COLLAR - 0.06, abs(y1 - y0) - 0.18, "collar", verts=96, rot=AX_Y, bevel=0.015)
        for yr in (y0 + sign * 0.06, y1 - sign * 0.06):                              # the two rings
            cyl((0, yr, ZB), R_COLLAR, 0.12, "collar", verts=96, rot=AX_Y, bevel=0.022)
        bolt_circle(y1, R_COLLAR - 0.08, 20, sign, rb=0.034, h=0.03)                 # the outer ring's bolts
        bolt_circle(y0, R_COLLAR - 0.08, 20, -sign, rb=0.034, h=0.03, phase=0.5)     # the inner ring's
        for k in range(16):                                      # the drum's girth: radial bolts
            a = 2 * math.pi * (k + 0.25) / 16
            nrm = (math.cos(a), 0, math.sin(a))
            hexbolt((nrm[0] * (R_COLLAR - 0.06), ym, ZB + nrm[2] * (R_COLLAR - 0.06)), nrm, 0.028, 0.024)
        cyl((0, y1 + sign * 0.01, ZB), 0.48, 0.02, "steel", verts=48, rot=AX_Y, bevel=0.004)      # the boss


def stub(sign, name, y_collar, r_end, square=False):
    with assembly(f"stub-{name}", on=(f"collar-{name}",)):
        ya, yb = sign * (y_collar[1] + 0.02), sign * (Y_END - 0.07)
        cyl((0, (ya + yb) / 2, ZB), R_STUB, abs(yb - ya), "collar", verts=64, rot=AX_Y, bevel=0.0)
        cyl((0, ya + sign * 0.03, ZB), R_STUB + 0.08, 0.06, "collar", verts=64, rot=AX_Y, bevel=0.01)  # root flange
        bolt_circle(ya + sign * 0.06, R_STUB + 0.04, 8, sign, rb=0.02, h=0.02)
        # the end flange, its face on the tile edge: the fluid connection
        # side-on (east-west) the face is drawn on the edge column itself: FACE_OUT carries it a
        # quarter pixel over, so the last column inside is solid metal, not 8% ground (the pipe's
        # ring draws over the quarter pixel beyond)
        out = FACE_OUT if _only[-1] == "horizontal" else 0.0
        # square: the vertical south end's flange is square (section 9); its round one is still
        # built, never drawn, so every part after it keeps the name it had
        with only("never" if square else _only[-1]):
            cyl((0, sign * (Y_END - 0.04 + out / 2), ZB), r_end, 0.08 + out, "collar", verts=64, rot=AX_Y,
                bevel=0.012)
        bolt_circle(sign * (Y_END - 0.08), (R_STUB + r_end) / 2, 10, -sign, rb=0.017, h=0.02, phase=0.5)
        cyl((0, sign * (Y_END - 0.004 + out), ZB), r_end - 0.07, 0.008, "steel", verts=64, rot=AX_Y, bevel=0.0)


def saddle(sign, name, ys, w):
    with assembly(f"saddle-{name}", on=(f"collar-{name}", "skid")):
        # a cast saddle under the collar, from the ground up round its underside
        ys, rs, hw = sign * ys, R_COLLAR - 0.02, 0.96
        prof = [(rs * math.cos(math.pi + math.pi * k / 24), ZB + rs * math.sin(math.pi + math.pi * k / 24))
                for k in range(25)]

        def build(bm):
            def loop(yy):
                f = [bm.verts.new((-hw, yy, 0.0)), bm.verts.new((hw, yy, 0.0)), bm.verts.new((hw, yy, ZB - 0.3))]
                f += [bm.verts.new((x, yy, z)) for x, z in prof[::-1] if z <= ZB - 0.3]
                f += [bm.verts.new((-hw, yy, ZB - 0.3))]
                return f
            fl, bl = loop(ys - w), loop(ys + w)
            bm.faces.new(fl[::-1])
            bm.faces.new(bl)
            for i in range(len(fl)):
                j = (i + 1) % len(fl)
                bm.faces.new((fl[i], fl[j], bl[j], bl[i]))
        mesh_object("saddle", build, "body_dark", "static", 0.02)
        for x in (-hw + 0.1, hw - 0.1):                         # its anchor bolts
            for s in (-1, 1):
                hexbolt((x, ys + s * (w - 0.06), 0.0), (0, 0, 1), 0.02, 0.018, "steel")


# the let-down end (south as modelled; west in the horizontal direction); in the vertical
# direction its collar, saddle and stub are section 9's
with only("horizontal"):
    end(-1, "S", parts=("collar",))
    end(-1, "S", parts=("stub",))
    end(-1, "S", parts=("saddle",))
with only("horizontal"):         # the generator end: the vertical direction's is section 8's
    end(+1, "N")

# ---------------------------------------------------------------- 2. the skids and the core
with assembly("skid"):
    with only("horizontal"):             # the vertical direction's rails: section 9
        for x in (-0.6, 0.6):
            box((x, 0, 0.04), (0.12, 4.0, 0.08), "skid", bevel=0.01)
    for y in (-1.0, 0.0, 1.0):
        box((0, y, 0.03), (1.36, 0.08, 0.06), "skid", bevel=0.008)

with assembly("core", on=("skid",)):
    cyl((0, 0, ZB), 0.38, 3.0, "body_dark", verts=64, rot=AX_Y, bevel=0.01)

# ---------------------------------------------------------------- 3. the let-down housing
# A cast block under a round bonnet: the stage the pressure drops in.
HL = dict(x0=-1.0, x1=0.80, y0=-1.50, y1=-0.82, z0=0.06, z1=1.30)
HCY = (HL["y0"] + HL["y1"]) / 2
R_BON = (HL["y1"] - HL["y0"]) / 2
with assembly("housing-S", on=("core", "skid", "collar-S", "saddle-S")):
    cx = (HL["x0"] + HL["x1"]) / 2
    box((cx, HCY, (HL["z0"] + HL["z1"]) / 2), (HL["x1"] - HL["x0"], HL["y1"] - HL["y0"], HL["z1"] - HL["z0"]),
        "body", bevel=0.08)
    cyl((cx, HCY, HL["z1"]), R_BON, HL["x1"] - HL["x0"] - 0.04, "body", verts=64, rot=(0, math.pi / 2, 0),
        bevel=0.03)                                                                          # the bonnet
    for x in (HL["x0"] + 0.06, HL["x1"] - 0.06):                                             # its flanges
        cyl((x, HCY, HL["z1"]), R_BON + 0.035, 0.07, "body_dark", verts=64, rot=(0, math.pi / 2, 0), bevel=0.012)
    for k in range(9):                                                                       # the near one's bolts
        a = math.pi * k / 8
        hexbolt((HL["x1"] - 0.025, HCY + (R_BON + 0.005) * math.cos(a), HL["z1"] + (R_BON + 0.005) * math.sin(a)),
                (1, 0, 0), 0.022, 0.018, "bronze")
    # a lap strap round the block and rivet rows on its near face
    box((cx, HCY, 0.64), (HL["x1"] - HL["x0"] + 0.03, HL["y1"] - HL["y0"] + 0.03, 0.07), "body", bevel=0.012)
    for k in range(9):
        y = HL["y0"] + 0.08 + k * (HL["y1"] - HL["y0"] - 0.16) / 8
        for z in (0.56, 0.72, 1.12):
            rivet((HL["x1"] + 0.003, y, z), 0.017, "steel")
    # the bonnet's bolted inspection cover, on its crown
    cyl((-0.15, HCY, HL["z1"] + R_BON - 0.005), 0.2, 0.04, "body_dark", verts=32, bevel=0.008)
    for k in range(6):
        a = 2 * math.pi * k / 6
        hexbolt((-0.15 + 0.16 * math.cos(a), HCY + 0.16 * math.sin(a), HL["z1"] + R_BON + 0.015), (0, 0, 1),
                0.016, 0.014, "steel")

# the let-down stage: a cast expansion bell on the near flank, where the pressure drops
LD = Vector((0.68, -1.06, 0.0))
LD_R = 0.28
with assembly("letdown", on=("housing-S", "skid", "case")):
    cyl((LD.x, LD.y, 0.42), LD_R, 0.72, "body_dark", verts=48, bevel=0.03)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=LD_R, location=(LD.x, LD.y, 0.78), segments=32, ring_count=16)
    o = bpy.context.active_object
    o.scale.z = 0.5
    _finish(o, "body_dark", "static", bevel=0, smooth=True)
    cyl((LD.x, LD.y, 0.1), LD_R + 0.03, 0.08, "body_dark", verts=48, bevel=0.01)          # its foot flange
    for k in range(8):
        a = 2 * math.pi * (k + 0.5) / 8
        hexbolt((LD.x + (LD_R + 0.012) * math.cos(a), LD.y + (LD_R + 0.012) * math.sin(a), 0.14), (0, 0, 1),
                0.016, 0.014, "steel")
    for z in (0.36, 0.6):
        torus((LD.x, LD.y, z), LD_R + 0.004, 0.02, "steel")                                   # its cast ribs

# the gauge pair (signature): high before the let-down, low after -- the pressure difference
GAUGE_TILT = Vector((1.0, 0.0, 0.9)).normalized()
# the high one on the housing, over the stage; the low one on the casing's inlet, after it
GAUGES = ((-1.16, 0.95, HL["x1"]), (-0.52, -0.95, math.sqrt(R_CASE ** 2 - 0.52 ** 2) - 0.02))
with assembly("gauges", on=("housing-S", "letdown", "case")):
    for gy, needle, mount in GAUGES:
        base = Vector((HL["x1"], gy, 1.0))
        face = base + GAUGE_TILT * 0.11
        cyl(((mount + HL["x1"] + 0.1) / 2, gy, 1.0), 0.022, HL["x1"] + 0.1 - mount, "steel", verts=12,
            rot=(0, math.pi / 2, 0), bevel=0.0)
        cyl(tuple(face), 0.105, 0.05, "steel", verts=40, rot=facing(GAUGE_TILT), bevel=0.01)          # the case
        torus(tuple(face + GAUGE_TILT * 0.026), 0.098, 0.011, "brass", rot=facing(GAUGE_TILT), seg=40)  # the bezel
        cyl(tuple(face + GAUGE_TILT * 0.026), 0.088, 0.004, "dial", verts=40, rot=facing(GAUGE_TILT), bevel=0.0)
        # the needle: across the dial from its pivot, angled high or low
        up = Vector((0, 0, 1)) - GAUGE_TILT * GAUGE_TILT.z
        up.normalize()
        side = GAUGE_TILT.cross(up)
        dirn = (up * math.cos(needle) + side * math.sin(needle)).normalized()
        p0 = face + GAUGE_TILT * 0.03
        strut(tuple(p0 - dirn * 0.015), tuple(p0 + dirn * 0.075), 0.012, 0.006, "tie", bevel=0.0)
        cyl(tuple(p0), 0.014, 0.008, "tie", verts=12, rot=facing(GAUGE_TILT), bevel=0.0)

# ---------------------------------------------------------------- 4. the rotor casing and the middle collar
with assembly("case", on=("core", "skid", "housing-S")):
    ZC = Z_ROTOR - 0.05                                          # the casing's solid top, under the rotor
    cyl((RC[0], RC[1], 0.40), R_VOLUTE, 0.68, "body_dark", verts=96, bevel=0.04)          # the volute drum
    torus((RC[0], RC[1], 0.74), R_VOLUTE - 0.05, 0.06, "body", seg=96)                     # its cast lip
    torus((RC[0], RC[1], 0.08), R_VOLUTE + 0.005, 0.03, "body_dark", seg=96)              # its foot
    cyl((RC[0], RC[1], (0.74 + ZC) / 2), R_CASE, ZC - 0.74, "body", verts=96, bevel=0.02)
    ring((RC[0], RC[1], (ZC + Z_RING) / 2), R_CASE, R_WIN + 0.002, Z_RING - ZC + 0.004, "body", verts=96,
         bevel=0.0)                                              # its wall round the well
    for z in (0.98, 1.22):
        torus((RC[0], RC[1], z), R_CASE + 0.004, 0.014, "seam", seg=96)
    for k in range(24):                                          # a rivet row under the collar
        a = 2 * math.pi * k / 24
        rivet((RC[0] + (R_CASE + 0.002) * math.cos(a), RC[1] + (R_CASE + 0.002) * math.sin(a), 1.38), 0.017)
    for k in range(20):                                          # the volute's bolted joint
        a = 2 * math.pi * (k + 0.5) / 20
        nrm = (math.cos(a), math.sin(a), 0)
        hexbolt((RC[0] + R_VOLUTE * nrm[0], RC[1] + R_VOLUTE * nrm[1], 0.5), nrm, 0.022, 0.018, "steel")
    # the recess the rotor turns in: a dark well under the window
    cyl((RC[0], RC[1], Z_ROTOR - 0.03), R_WIN + 0.005, 0.02, "recess", verts=64, bevel=0.0)
with assembly("collar-M", on=("case",)):
    ring((RC[0], RC[1], Z_RING + 0.07), R_CASE, R_WIN, 0.14, "collar", verts=96, bevel=0.022)
    ring((RC[0], RC[1], Z_ROTOR + 0.05), R_WIN + 0.002, R_WIN - 0.02, Z_RING - Z_ROTOR + 0.06, "recess", verts=64,
         bevel=0.0)                                                                                # the bore
    for k in range(12):
        a = 2 * math.pi * (k + 0.5) / 12
        hexbolt((RC[0] + 0.62 * math.cos(a), RC[1] + 0.62 * math.sin(a), Z_RING + 0.14), (0, 0, 1), 0.036, 0.03)
with assembly("lens", on=("collar-M",)):
    # the status lens on the far rim (-X: the top of the collar in the horizontal direction)
    LENS = Vector((RC[0] - 0.72, RC[1], Z_RING + 0.14))
    cyl(tuple(LENS + Vector((0, 0, 0.02))), 0.075, 0.04, "steel", verts=32, bevel=0.008)          # its bezel
    LENS_GLASS = cyl(tuple(LENS + Vector((0, 0, 0.045))), 0.052, 0.016, "lens", "lens", verts=32, bevel=0.006)

# the rotor: twelve swept vanes on a hub, under the window; turns about Z (round 1's, unchanged)
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

# ---------------------------------------------------------------- 5. the generator can and its bushings
GC = dict(y0=0.82, y1=Y_COLLAR[0], r=0.86)
GCM = (GC["y0"] + GC["y1"]) / 2


def can_top(x):
    """The can's top surface height at x."""
    return ZB + math.sqrt(max(GC["r"] ** 2 - x * x, 0.0))


with assembly("gencan", on=("core", "skid", "collar-N", "case", "saddle-N")):
    cyl((0, GCM, ZB), GC["r"], GC["y1"] - GC["y0"], "gencan", verts=96, rot=AX_Y, bevel=0.03)
    for y in (GC["y0"] + 0.06, GC["y1"] - 0.06):
        cyl((0, y, ZB), GC["r"] + 0.03, 0.08, "gencan", verts=96, rot=AX_Y, bevel=0.012)          # end bands
        for k in range(22):
            a = 2 * math.pi * k / 22
            rivet(((GC["r"] + 0.033) * math.cos(a), y, ZB + (GC["r"] + 0.033) * math.sin(a)), 0.017)
    for k in range(9):                                            # cooling ribs over its shoulders
        a = math.radians(25 + k * 16.25)
        if 75 < math.degrees(a) < 125:
            continue                                              # the bushing chamber's seat
        nrm = Vector((math.cos(a), 0, math.sin(a)))
        c = Vector((0, GCM, ZB)) + nrm * (GC["r"] + 0.02)
        box(tuple(c), (0.022, GC["y1"] - GC["y0"] - 0.26, 0.06), "gencan", rot=(0, -(math.pi / 2 - a), 0),
            bevel=0.005)
    for y in (GC["y0"] + 0.18, GC["y1"] - 0.18):                  # its feet
        box((0, y, 0.18), (1.5, 0.12, 0.32), "body_dark", bevel=0.015)

# the signature: three porcelain bushings in a row on a bolted chamber on the can's crown,
# the machine's output taken off it in plain sight
BUSH_X = -0.18
BUSH_Y = (0.97, 1.16, 1.35)
Z_CH = 1.92                                                       # the chamber's lid
with assembly("bushings", on=("gencan",)):
    box((BUSH_X, 1.16, (1.6 + Z_CH) / 2), (0.46, 0.6, Z_CH - 1.6), "gencan", bevel=0.03)
    box((BUSH_X, 1.16, Z_CH + 0.012), (0.5, 0.64, 0.024), "body_dark", bevel=0.008)        # the lid
    for sx in (-0.21, 0.21):
        for sy in (-0.28, -0.095, 0.095, 0.28):
            hexbolt((BUSH_X + sx, 1.16 + sy, Z_CH + 0.024), (0, 0, 1), 0.016, 0.014, "steel")
    for y in BUSH_Y:
        z = Z_CH + 0.024
        cyl((BUSH_X, y, z + 0.02), 0.08, 0.04, "steel", verts=24, bevel=0.006)              # its mounting flange
        cyl((BUSH_X, y, z + 0.2), 0.045, 0.34, "porcelain", verts=24, bevel=0.0)           # the core
        for k in range(4):                                                                  # the sheds
            zz = z + 0.08 + k * 0.07
            cyl((BUSH_X, y, zz), 0.088 - 0.006 * k, 0.026, "porcelain", verts=32, bevel=0.01)
        cyl((BUSH_X, y, z + 0.38), 0.05, 0.05, "brass", verts=24, bevel=0.008)              # the terminal cap
        cyl((BUSH_X, y, z + 0.42), 0.018, 0.04, "copper", verts=12, bevel=0.0)              # its stud

# the terminal box on the far flank: steel, a brass lid, the bus coming down into it
TBF = dict(x0=X_FAR + 0.02, x1=-0.96, y0=0.70, y1=1.42, z0=0.06, z1=1.12)
with assembly("terminal-far", on=("gencan", "skid")):
    tcx, tcy = (TBF["x0"] + TBF["x1"]) / 2, (TBF["y0"] + TBF["y1"]) / 2
    box((tcx, tcy, (TBF["z0"] + TBF["z1"]) / 2), (TBF["x1"] - TBF["x0"], TBF["y1"] - TBF["y0"], TBF["z1"] - TBF["z0"]),
        "body_dark", bevel=0.03)
    box((tcx, tcy, TBF["z1"] + 0.02), (TBF["x1"] - TBF["x0"] - 0.04, TBF["y1"] - TBF["y0"] - 0.04, 0.04), "brass",
        bevel=0.012)                                                                         # the brass lid
    for sx in (-0.17, 0.17):
        for sy in (-0.3, 0.3):
            hexbolt((tcx + sx, tcy + sy, TBF["z1"] + 0.04), (0, 0, 1), 0.016, 0.014, "steel")
    for y in BUSH_Y:                                                                         # the bus glands
        cyl((-1.12, y, TBF["z1"] + 0.07), 0.04, 0.06, "brass", verts=6, bevel=0.004)
    for y in (TBF["y0"] + 0.2, TBF["y1"] - 0.12):                 # straps to the can
        box(((TBF["x1"] - 0.76) / 2, y, 0.62), (abs(TBF["x1"] + 0.76), 0.06, 0.04), "steel", bevel=0.005)
    for y in (TBF["y0"] + 0.06, TBF["y1"] - 0.06):
        foot_plate(TBF["x0"] + 0.1, y, 0.12, bolts=False)
with assembly("bus", on=("bushings", "terminal-far")):
    for y in BUSH_Y:
        pipe([(BUSH_X, y, Z_CH + 0.41), (BUSH_X - 0.08, y, Z_CH + 0.41), (-0.95, y, 1.86), (-1.12, y, 1.58),
              (-1.12, y, TBF["z1"] + 0.08)], 0.024, "copper", bend=0.14)

# the near flank's brass terminal box, low on the can (spec 3.2)
TB = Vector((0.86, 1.12, 0.62))
with assembly("terminal", on=("gencan",)):
    box(tuple(TB), (0.16, 0.42, 0.44), "brass", bevel=0.02)
    box(tuple(TB + Vector((0.085, 0, 0))), (0.02, 0.36, 0.38), "brass", bevel=0.01)                  # its lid
    for sy in (-0.14, 0.14):
        for sz in (-0.14, 0.14):
            hexbolt(tuple(TB + Vector((0.095, sy, sz))), (1, 0, 0), 0.014, 0.012, "steel")
    for sy in (-0.1, 0.0, 0.1):                                                                    # cable glands
        cyl(tuple(TB + Vector((0.0, sy, -0.24))), 0.024, 0.05, "steel", verts=6, bevel=0.003)

# ---------------------------------------------------------------- 6. the far flank: balance line, tray, braces
X_LINE = -1.22
R_LAG = 0.10
with assembly("balance", on=("housing-S", "case", "skid")):
    pts = [(HL["x0"] + 0.02, -1.24, 0.42), (X_LINE, -1.24, 0.42), (X_LINE, 0.40, 0.42), (-0.80, 0.40, 0.42)]
    pipe(pts, R_LAG, "lagging", bend=0.2)
    for y in [-0.96 + 0.2 * k for k in range(7)]:                  # steel bands over the lagging
        torus((X_LINE, y, 0.42), R_LAG + 0.002, 0.012, "seam", rot=AX_Y, seg=24)
    for x in (-1.06,):
        torus((x, -1.24, 0.42), R_LAG + 0.002, 0.012, "seam", rot=(0, math.pi / 2, 0), seg=24)
        torus((x, 0.40, 0.42), R_LAG + 0.002, 0.012, "seam", rot=(0, math.pi / 2, 0), seg=24)
    for p in ((HL["x0"] - 0.03, -1.24, 0.42), (-0.86, 0.40, 0.42)):                       # flanged ends
        cyl(p, R_LAG + 0.04, 0.05, "steel", verts=24, rot=(0, math.pi / 2, 0), bevel=0.008)
    # a gate valve in the line, its handwheel up
    cyl((X_LINE, -0.30, 0.42), R_LAG + 0.04, 0.24, "body_dark", verts=24, rot=AX_Y, bevel=0.015)
    for y in (-0.42, -0.18):
        cyl((X_LINE, y, 0.42), R_LAG + 0.055, 0.04, "steel", verts=24, rot=AX_Y, bevel=0.008)
    box((X_LINE, -0.30, 0.6), (0.14, 0.12, 0.16), "body_dark", bevel=0.02)                   # the bonnet
    cyl((X_LINE, -0.30, 0.72), 0.018, 0.16, "steel", verts=12, bevel=0.0)                     # the stem
    torus((X_LINE, -0.30, 0.79), 0.11, 0.014, "steel", seg=32)                                # the handwheel
    for k in range(3):
        a = 2 * math.pi * k / 3
        strut((X_LINE, -0.30, 0.79), (X_LINE + 0.1 * math.cos(a), -0.30 + 0.1 * math.sin(a), 0.79), 0.012, 0.012)
    # its stands
    for y in (-0.8, 0.1):
        box((X_LINE, y, 0.15), (0.06, 0.06, 0.3), "steel", bevel=0.005)
        box((X_LINE, y, 0.31), (0.26, 0.08, 0.03), "steel", bevel=0.005)                     # the saddle clamp
        foot_plate(X_LINE, y, 0.12)

X_TRAY = -1.32
Z_TRAY = 1.0
with assembly("tray", on=("housing-S", "case", "terminal-far", "skid")):
    ty0, ty1 = -1.36, TBF["y0"]
    L = ty1 - ty0
    box((X_TRAY, (ty0 + ty1) / 2, Z_TRAY), (0.24, L, 0.02), "steel", bevel=0.004)                # the floor
    for s in (-1, 1):
        box((X_TRAY + s * 0.115, (ty0 + ty1) / 2, Z_TRAY + 0.04), (0.012, L, 0.08), "steel", bevel=0.003)
    for k in range(9):                                                                       # its rungs
        box((X_TRAY, ty0 + 0.1 + k * (L - 0.2) / 8, Z_TRAY + 0.012), (0.22, 0.03, 0.006), "steel", bevel=0.0)
    for y, x_in in ((-1.0, HL["x0"]), (-0.2, -0.76), (0.48, -0.62)):                          # posts and arms
        box((X_FAR + 0.04, y, Z_TRAY / 2), (0.06, 0.06, Z_TRAY), "steel", bevel=0.005)
        box(((X_FAR + 0.02 + x_in) / 2, y, Z_TRAY - 0.03), (abs(x_in - X_FAR), 0.05, 0.04), "steel", bevel=0.005)
        foot_plate(X_FAR + 0.06, y, 0.12)
    # the cables in it, from the terminal box to the housing's far junction box
    bundle([(-1.30, TBF["y0"] + 0.08, TBF["z1"] + 0.04), (-1.30, TBF["y0"] - 0.08, Z_TRAY + 0.04),
            (X_TRAY, 0.2, Z_TRAY + 0.03), (X_TRAY, -0.6, Z_TRAY + 0.03), (X_TRAY, -1.2, Z_TRAY + 0.04),
            (-1.12, -1.3, 1.0)], ["cable-black", "cable-red", "cable-grey", "cable-black"], r=0.016, gap=0.034,
           lie=(0, 0, 1))
    box((HL["x0"] - 0.05, -1.3, 1.0), (0.1, 0.26, 0.28), "body_dark", bevel=0.015)            # the junction box

with assembly("braces", on=("collar-S", "collar-N", "saddle-S", "saddle-N", "skid", "gencan")):
    # struts from each end collar's far shoulder down to the ground
    def collar_braces(ym, dys):
        for dy in dys:
            top = (-(R_COLLAR - 0.12) * math.cos(math.radians(30)), ym + dy, ZB + (R_COLLAR - 0.12) * 0.5)
            strut(top, (X_FAR + 0.08, ym + dy * 1.6, 0.02), 0.06, 0.05)
            foot_plate(X_FAR + 0.09, ym + dy * 1.6, 0.11, bolts=dy > 0)
    with only("horizontal"):                 # the vertical direction's: sections 8 (north) and 9 (south)
        collar_braces(-1.79, (-0.12, 0.12))
        collar_braces(1.79, (-0.12, 0.12))
    # and short gussets down the near side of the can
    for y in (GC["y0"] + 0.04, GC["y1"] - 0.1):
        strut((0.62, y, 0.5), (X_NEAR - 0.06, y, 0.02), 0.05, 0.05)

# ---------------------------------------------------------------- 7. the near flank and the top
with assembly("runs-near", on=("letdown", "housing-S", "case", "terminal", "gencan", "skid", "saddle-N",
                               "gauges", "braces")):
    # the gas from the let-down stage into the volute, flanged
    pipe([(LD.x + 0.1, LD.y + 0.24, 0.34), (0.9, -0.72, 0.34), (0.72, -0.44, 0.34)], 0.06, "copper", bend=0.16)
    cyl((0.88, -0.68, 0.34), 0.095, 0.05, "steel", verts=24, rot=facing((-0.4, 0.9, 0)), bevel=0.008)
    # impulse lines from the stage to the two gauges
    pipe([(LD.x + 0.12, LD.y, 0.8), (0.86, LD.y, 0.86), (0.86, LD.y, 0.96)], 0.014, "copper", bend=0.06)
    pipe([(0.86, -0.62, 0.38), (0.86, -0.52, 0.5), (0.86, -0.52, 0.96)], 0.014, "copper", bend=0.06)
    # the sensing lines from the volute to the terminal box
    pipe([(0.84, 0.3, 0.44), (0.9, 0.56, 0.44), (0.88, 0.95, 0.42)], 0.024, "copper", bend=0.1)
    pipe([(0.82, 0.36, 0.3), (0.88, 0.6, 0.28), (0.86, 0.92, 0.42)], 0.02, "copper", bend=0.1)
    # cleated cables out of the box's glands, along the can's flank to the far collar's foot
    bundle([tuple(TB + Vector((0.0, 0.0, -0.27))), (0.9, 1.2, 0.3), (0.9, 1.45, 0.32), (0.82, 1.66, 0.34)],
           ["cable-black", "cable-red", "cable-grey"], r=0.016, gap=0.034, lie=(1, 0, 0.3))
    # a corrugated bleed hose from the stage's foot along the flank into the volute
    hose([(LD.x + 0.2, LD.y + 0.18, 0.22), (0.93, -0.9, 0.16), (0.92, -0.62, 0.12), (0.8, -0.42, 0.14)], 0.03)
    # and one up over the bonnet's near flange into the casing
    hose([(0.70, -0.92, 1.40), (0.8, -0.74, 1.54), (0.68, -0.56, 1.42), (0.5, -0.5, 1.3)], 0.032)

TOPZ = 1.84
with assembly("runs-top", on=("housing-S", "case", "core", "gencan", "collar-M", "bushings")):
    pipe([(-0.5, HCY, HL["z1"] + R_BON - 0.02), (-0.5, HCY, TOPZ), (-0.9, -0.76, TOPZ), (-0.9, 0.42, TOPZ),
          (-0.6, 0.9, TOPZ), (-0.6, 0.9, can_top(-0.6) - 0.02)], 0.042, "copper", bend=0.14)
    for y in (-0.42, 0.24):                                       # posts off the casing hold it
        box((-0.9, y, (1.1 + TOPZ) / 2), (0.04, 0.04, TOPZ - 1.1), "steel", bevel=0.005)
        box((-0.78, y, 1.12), (0.24, 0.04, 0.04), "steel", bevel=0.005)
        box((-0.9, y, TOPZ), (0.11, 0.06, 0.11), "steel", bevel=0.006)                        # the cleat
    for (x, y, z) in ((-0.5, HCY, HL["z1"] + R_BON - 0.02), (-0.6, 0.9, can_top(-0.6) - 0.02)):
        cyl((x, y, z + 0.015), 0.07, 0.03, "steel", verts=24, bevel=0.005)                       # pads

with assembly("eyes", on=("housing-S", "gencan")):
    for x, y, z in ((0.3, HCY, HL["z1"] + R_BON - 0.01), (0.34, 1.38, can_top(0.34) - 0.02)):
        box((x, y, z + 0.08), (0.18, 0.05, 0.16), "body_dark", bevel=0.02)
        torus((x, y, z + 0.17), 0.06, 0.02, "steel", rot=AX_Y, seg=32)

# ---------------------------------------------------------------- 8. the vertical direction's ends
# Built last, so every part above keeps the name (and so the render noise) it had when the
# horizontal sheets and the icon were signed off. Section 1's design, at the sizes the
# vertical joins need (SOUTH, R_END_V, Y_COLLAR_NV): the south stub as section 1's; the
# north collar cut back to its two bolted rings, its saddle and braces under
# them, and its stub out from there to the tile edge.
with only("vertical"):
    with only("never"):          # the south stub is section 9's; built, never drawn, so every
        end(-1, "S", r_end=R_END_V, parts=("stub",), square=True)      # part after keeps its name
    mid = sum(Y_COLLAR_NV) / 2
    end(+1, "N", y_collar=Y_COLLAR_NV, r_end=R_END_V, ys=mid, w=(Y_COLLAR_NV[1] - Y_COLLAR_NV[0]) / 2 - 0.01)
    with assembly("braces", on=("collar-S", "collar-N", "saddle-S", "saddle-N", "skid", "gencan")):
        collar_braces(mid, (-0.07, 0.07))

# ---------------------------------------------------------------- 9. the vertical south stub
# (amendment 3, 2026-10-11, Liam: "the southern pipe point doesn't connect to the pipe
# correctly, you can see on the edge of both objects"): amendment 2's square flange was wider
# than the pipe and showed either side of its ring. As vanilla's steam turbine: the pipe runs
# straight into the machine. The stub is vanilla's straight pipe seen end-on -- its body 41-42 px
# across, its axis 1.5 px right of the tile's centre (pipe-straight-vertical) -- bare from the
# collar's face to under the pipe's end ring, no flange, no bolt ring, nothing wider than the
# pipe. The pipe's ring (51 px, rows 140..165 below the origin) draws over the stub's end, so
# the stub runs on to Y_STUB_SV, where its end face lies wholly inside that ring and its lowest
# pixel is under the ring's: the eye sees the pipe's ring and the pipe's body, nothing else.
# Beside the ring nothing of the machine may show (the column check: in the pipe's ring's rows,
# no turbine pixel outside its 51 px): the south collar is cut back to Y_COLLAR_SV, so its rim
# clears the ring's top row (140 px) wherever it is wider than the stub, and the saddle, the
# skid rails and the brace feet under it stop short of it the same way (a point on the ground
# at y draws at y + SOUTH tiles).
Y_COLLAR_SV = (1.50, 1.96)           # the vertical direction's south collar
Y_SKID_SV = 1.92                     # the rails' south end
R_STUB_SV = 0.325                    # 41.6 px: vanilla's pipe body, 41-42 px
X_STUB_SV = 1.5 / 64                 # vanilla's pipe body sits 1.5 px right of its tile's centre
Y_STUB_SV = 2.62                     # its end face: under the pipe's ring (rows 143..163 on the screen)
with only("vertical"):
    end(-1, "S", y_collar=Y_COLLAR_SV, ys=sum(Y_COLLAR_SV) / 2 + 0.02, w=0.17, parts=("collar", "saddle"))
    with assembly("skid"):
        for x in (-0.6, 0.6):
            box((x, (2.0 - Y_SKID_SV) / 2, 0.04), (0.12, 2.0 + Y_SKID_SV, 0.08), "skid", bevel=0.01)
    with assembly("braces", on=("collar-S", "saddle-S", "skid")):
        collar_braces(-sum(Y_COLLAR_SV) / 2, (-0.07, 0.07))
with only("vertical"), assembly("stub-S", on=("collar-S",)):
    ya = Y_COLLAR_SV[1] - 0.02
    cyl((X_STUB_SV, -(ya + Y_STUB_SV) / 2, ZB), R_STUB_SV, Y_STUB_SV - ya, "pipe", verts=64, rot=AX_Y, bevel=0.0)

# ---------------------------------------------------------------- 10. the wreck (the remnants pass)
# What the corpse draws once the turbine is destroyed (tools/blender/contract.py, kind
# "remnants"): this machine broken where it stood, in its own materials, low on the ground as
# vanilla's steam-turbine-remnants lies. Built last, after every part above, so every part of
# the machine keeps the name (and so the render noise) it had; drawn only when CUR is "wreck"
# (`only`) and only in the wreck's group, so no render of the machine shows it, nor does it
# show them, and --collide never tests it (a wreck's pieces lie in and on each other).
#   - the skids stay, one rail broken and kinked, a cross member shoved askew;
#   - the end collars split open and sunk on crushed saddles, the north one leaning out; the
#     stubs torn off short, one lying on the ground;
#   - the volute drum burst open on its east side, its well open to the sky; the middle collar
#     thrown off and tilted on the rubble; the rotor fallen out of it, tilted, four vanes and
#     a third of its shroud torn away, three loose vanes on the ground;
#   - the let-down housing collapsed, its bonnet rolled off; the expansion bell knocked over
#     onto its flank; a gauge face down in the dirt beside it;
#   - the generator can split, its upper skin torn off and lying on its back; the bushing
#     chamber knocked over with one bushing still on it, another broken on the ground, shards;
#   - pipes torn: the copper bus and the top run bent and snapped, the gas pipe ripped from the
#     volute; the corrugated hose loose across the near flank, its far ferrule gone; the cable
#     bundle sprawled along the far flank, its end frayed; the lagged balance line in two;
#   - plates, bolts and lumps of heaved ground thrown low round it;
#   - and a scorch: the ground darkened under and round it, black and part transparent as
#     vanilla's remnants darken theirs (pack.py's _shadow_px counts it with the cast shadow).
# Coordinates are the machine's, as modelled (vertical: north +Y, the near flank +X); the
# horizontal direction is the same wreck turned, as the machine is.
import random  # noqa: E402

RNG = random.Random(20261020)
WRECK_CANVAS = (576, 576)            # 9 x 9 tiles: the 5-tile length, the debris and the scorch past it


class frame:
    """Everything built inside is placed in an empty's frame: its coordinates are the empty's."""

    def __init__(self, loc=(0, 0, 0), rot=(0, 0, 0)):
        self.e = empty("wreck-frame", loc, rot, parent=_parent[-1])

    def __enter__(self):
        _parent.append(self.e)
        return self.e

    def __exit__(self, *a):
        _parent.pop()


def shell(loc, r_out, r_in, h, mat, a0=0.0, a1=2 * math.pi, jag=0.0, seg=64, rot=(0, 0, 0), bevel=0.006):
    """A cylinder's wall about local Z from angle a0 to a1, its foot at 0 and its top at h, torn
    to a ragged top edge up to `jag` deep: a casing or a ring broken open."""
    full = abs(a1 - a0) >= 2 * math.pi - 1e-6
    n = seg if full else max(3, round(seg * abs(a1 - a0) / (2 * math.pi)))
    # the tear: a slow wave along the edge, a fine serration on it and a deep notch or two,
    # never a row of even teeth
    f1, f2, p1, p2 = RNG.uniform(2, 4), RNG.uniform(5, 9), RNG.uniform(0, 6.3), RNG.uniform(0, 6.3)
    notches = [RNG.uniform(0, 1) for _ in range(2)]
    tops = []
    for i in range(n + 1):
        u = i / n
        w = 0.5 + 0.3 * math.sin(f1 * 2 * math.pi * u + p1) + 0.2 * math.sin(f2 * 2 * math.pi * u + p2)
        w += 0.18 * (RNG.random() - 0.5)
        w += sum(0.6 * max(0.0, 1 - abs(u - c) * 14) for c in notches)
        tops.append(h - jag * min(1.0, max(0.0, w)))

    def build(bm):
        cols = []
        for i in range(n if full else n + 1):
            a = a0 + (a1 - a0) * i / n
            c, s = math.cos(a), math.sin(a)
            cols.append([bm.verts.new((r * c, r * s, z)) for r, z in
                         ((r_out, 0.0), (r_out, tops[i]), (r_in, tops[i]), (r_in, 0.0))])
        m = len(cols)
        for i in range(m if full else m - 1):
            A, B = cols[i], cols[(i + 1) % m]
            for k in range(4):
                bm.faces.new((A[k], B[k], B[(k + 1) % 4], A[(k + 1) % 4]))
        if not full:
            bm.faces.new(cols[0][::-1])
            bm.faces.new(cols[-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_object("shell", build, mat, "static", bevel, smooth=True)
    o.location, o.rotation_euler = loc, rot
    return o


def shard(loc, r, t, mat, rot=None, n=7, stretch=(1.0, 1.0)):
    """A torn plate: a ragged polygon r across, t thick."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * (i + RNG.uniform(-0.3, 0.3)) / n
        rr = r * RNG.uniform(0.5, 1.0)
        pts.append((rr * math.cos(a) * stretch[0], rr * math.sin(a) * stretch[1]))

    def build(bm):
        lo = [bm.verts.new((x, y, -t / 2)) for x, y in pts]
        hi = [bm.verts.new((x, y, t / 2)) for x, y in pts]
        bm.faces.new(lo[::-1])
        bm.faces.new(hi)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_object("shard", build, mat, "static", min(0.005, t / 3))
    o.location = loc
    o.rotation_euler = rot if rot is not None else (RNG.uniform(-0.25, 0.25), RNG.uniform(-0.25, 0.25),
                                                    RNG.uniform(0, 2 * math.pi))
    return o


def lump(loc, r, mat="skid", flat=0.45):
    """A lump of heaved ground or rubble, low and rough."""
    def build(bm):
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
        sy = RNG.uniform(0.75, 1.25)
        for v in bm.verts:
            k = RNG.uniform(0.7, 1.15)
            v.co = Vector((v.co.x * k * r, v.co.y * k * r * sy, max(v.co.z, -0.2) * k * r * flat))
    o = mesh_object("lump", build, mat, "static", 0.0, smooth=False)
    o.location, o.rotation_euler = loc, (0, 0, RNG.uniform(0, 2 * math.pi))
    return o


def scorch_material():
    """The ground darkened round the wreck: black, part transparent, its edge ragged -- the
    vanilla remnants' own darkening, which shows on any ground. A mix of a transparent and a
    black diffuse shader, so every pixel it adds is RGB 0 at the alpha it is drawn at."""
    m = bpy.data.materials.new("scorch")
    m.use_nodes = True
    t = m.node_tree
    for nd in list(t.nodes):
        if nd.bl_idname != "ShaderNodeOutputMaterial":
            t.nodes.remove(nd)
    out = next(nd for nd in t.nodes if nd.bl_idname == "ShaderNodeOutputMaterial")
    tc = t.nodes.new("ShaderNodeTexCoord")
    mp = t.nodes.new("ShaderNodeMapping")                      # the ellipse to a unit circle
    mp.inputs["Scale"].default_value = (1 / SCORCH[0], 1 / SCORCH[1], 1.0)
    t.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    ln = t.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    t.links.new(mp.outputs["Vector"], ln.inputs[0])
    nz = t.nodes.new("ShaderNodeTexNoise")                    # the ragged edge
    nz.inputs["Scale"].default_value = 2.2
    nz.inputs["Detail"].default_value = 6.0
    nz.inputs["Roughness"].default_value = 0.6
    t.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    edge = t.nodes.new("ShaderNodeMath")                       # the distance, broken by the noise
    edge.operation = "MULTIPLY_ADD"
    t.links.new(nz.outputs["Fac"], edge.inputs[0])
    edge.inputs[1].default_value = 0.55
    t.links.new(ln.outputs["Value"], edge.inputs[2])
    fall = t.nodes.new("ShaderNodeMapRange")                   # dark inside, gone by the rim
    fall.inputs["From Min"].default_value = 0.55 + 0.55 * 0.5
    fall.inputs["From Max"].default_value = 1.0 + 0.55 * 0.5
    fall.inputs["To Min"].default_value = SCORCH[2]
    fall.inputs["To Max"].default_value = 0.0
    fall.clamp = True
    t.links.new(edge.outputs["Value"], fall.inputs["Value"])
    nz2 = t.nodes.new("ShaderNodeTexNoise")                    # blotched, not even
    nz2.inputs["Scale"].default_value = 6.0
    nz2.inputs["Detail"].default_value = 4.0
    t.links.new(tc.outputs["Object"], nz2.inputs["Vector"])
    blot = t.nodes.new("ShaderNodeMapRange")
    blot.inputs["From Min"].default_value = 0.3
    blot.inputs["From Max"].default_value = 0.7
    blot.inputs["To Min"].default_value = 0.7
    blot.inputs["To Max"].default_value = 1.1
    t.links.new(nz2.outputs["Fac"], blot.inputs["Value"])
    a = t.nodes.new("ShaderNodeMath")
    a.operation = "MULTIPLY"
    a.use_clamp = True
    t.links.new(fall.outputs["Result"], a.inputs[0])
    t.links.new(blot.outputs["Result"], a.inputs[1])
    tr = t.nodes.new("ShaderNodeBsdfTransparent")
    blk = t.nodes.new("ShaderNodeBsdfDiffuse")
    blk.inputs["Color"].default_value = (0, 0, 0, 1)
    mix = t.nodes.new("ShaderNodeMixShader")
    t.links.new(a.outputs["Value"], mix.inputs["Fac"])
    t.links.new(tr.outputs["BSDF"], mix.inputs[1])
    t.links.new(blk.outputs["BSDF"], mix.inputs[2])
    t.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return m


# the scorch's half-axes on the ground, tiles, and its darkest alpha
SCORCH = (2.15, 3.15, 0.85)
M["scorch"] = scorch_material()


def collar_ring(a0, a1, drum_h=0.3, jag=0.18, skip=()):
    """An end collar lying on its face, broken: its outer ring with the bronze bolts that held
    it, the drum's stub standing torn out of it, dark inside. Built in a frame: z up off it."""
    shell((0, 0, 0), R_COLLAR, R_COLLAR - 0.14, 0.12, "collar", a0, a1, jag=0.02, seg=96, bevel=0.02)
    shell((0, 0, 0.1), R_COLLAR - 0.06, R_COLLAR - 0.12, drum_h, "collar", a0 + 0.3, a1 - 0.25, jag=jag, seg=96)
    shell((0, 0, 0.02), R_COLLAR - 0.125, R_COLLAR - 0.16, drum_h - 0.04, "recess", a0 + 0.3, a1 - 0.25,
          jag=jag, seg=96)
    for k in range(20):
        a = 2 * math.pi * (k + 0.5) / 20
        if not 0.05 < (a - a0) % (2 * math.pi) < a1 - a0 - 0.05 or k in skip:     # on what is left of it
            continue
        hexbolt(((R_COLLAR - 0.07) * math.cos(a), (R_COLLAR - 0.07) * math.sin(a), 0.12), (0, 0, 1), 0.034, 0.03)


with only("wreck"), assembly("wreck"):
    _group.append("wreck")

    # -- the ground: the scorch, and lumps of it heaved up round the machine's foot and over its edges
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.002))
    sp = bpy.context.active_object
    sp.scale = (2 * SCORCH[0] + 1.0, 2 * SCORCH[1] + 1.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    _finish(sp, "scorch", "static", bevel=0)
    sp.visible_shadow = False                         # it darkens the ground; it casts nothing
    for k in range(120):
        a = RNG.uniform(0, 2 * math.pi)
        rr = RNG.uniform(0.7, 1.02)
        lump((1.4 * rr * math.cos(a), 2.4 * rr * math.sin(a), 0.0), RNG.uniform(0.05, 0.14),
             RNG.choice(("skid", "skid", "body_dark")))
    for k in range(40):
        lump((RNG.uniform(-1.1, 1.1), RNG.uniform(-2.1, 2.1), 0.0), RNG.uniform(0.05, 0.13), "skid")

    # -- the skids: the far rail whole, the near one broken and kinked, a cross member shoved
    box((-0.6, -0.05, 0.04), (0.12, 3.9, 0.08), "skid", bevel=0.01)
    box((0.62, -1.15, 0.04), (0.12, 1.7, 0.08), "skid", rot=(0, 0, 0.05), bevel=0.01)
    box((0.74, 0.95, 0.06), (0.12, 1.75, 0.08), "skid", rot=(0.06, 0.04, -0.09), bevel=0.01)
    for y, rz in ((-1.0, 0.0), (0.05, 0.32), (1.0, -0.06)):
        box((0.05, y, 0.03), (1.36, 0.08, 0.06), "skid", rot=(0, 0, rz), bevel=0.008)
    for y, rz in ((-1.86, 0.08), (1.85, -0.06)):                          # the saddles, cracked and crushed flat
        box((-0.42, y, 0.07), (0.86, 0.3, 0.14), "body_dark", rot=(0.05, 0.12, rz), bevel=0.02)
        box((0.5, y + 0.05, 0.06), (0.8, 0.3, 0.12), "body_dark", rot=(-0.04, -0.1, rz - 0.22), bevel=0.02)

    # -- the south (let-down) collar, fallen on its face, sunk at its west side; the let-down
    # stage's dark well open inside it
    with frame((-0.12, -1.6, -0.05), (0.2, -0.16, 0.3)):
        collar_ring(0.7, 5.5, drum_h=0.3, skip=(4, 11))
        cyl((0, 0, 0.03), R_COLLAR - 0.16, 0.03, "recess", verts=64, bevel=0.0)
        for k in range(9):                                             # rubble fallen into it
            a, rr = RNG.uniform(0, 2 * math.pi), RNG.uniform(0.1, 0.65)
            lump((rr * math.cos(a), rr * math.sin(a), 0.04), RNG.uniform(0.06, 0.12), "skid")
    # its stub, torn off and lying at the south-east, the flange still on it
    with frame((0.6, -2.18, R_STUB - 0.06), (math.pi / 2, 0, -1.1)):
        shell((0, 0, 0), R_STUB, R_STUB - 0.04, 0.46, "collar", jag=0.12)
        cyl((0, 0, 0.04), R_END, 0.08, "collar", verts=64, bevel=0.012)
        for k in range(10):
            a = 2 * math.pi * (k + 0.5) / 10
            hexbolt(((R_STUB + R_END) / 2 * math.cos(a), (R_STUB + R_END) / 2 * math.sin(a), 0.0), (0, 0, -1),
                    0.017, 0.02)

    # -- the let-down housing, crushed flat between the collar and the drum; its bonnet a torn
    # skin on the ground to the west
    box((0.42, -0.98, 0.1), (1.0, 0.56, 0.2), "body", rot=(0.1, -0.12, 0.18), bevel=0.05)
    box((0.42, -0.98, 0.17), (1.03, 0.59, 0.06), "body", rot=(0.1, -0.12, 0.18), bevel=0.012)
    for k in range(7):
        rivet((0.92 + 0.004, -1.2 + k * 0.07, 0.12), 0.017, "steel")
    with frame((-1.02, -0.92, 0.0), (0.0, 0.0, 0.35)):
        with frame((0, 0, R_BON * 0.55), (0, math.pi / 2, 0)):
            shell((0, 0, -0.45), R_BON, R_BON - 0.04, 0.9, "body", math.pi * 0.55, math.pi * 1.45, jag=0.12)
    with frame((-0.55, -2.36, 0.03), (0.12, -0.08, 0.7)):             # the inspection cover, off
        cyl((0, 0, 0), 0.2, 0.04, "body_dark", verts=32, bevel=0.008)
        for k in range(6):
            if k == 2:
                continue
            a = 2 * math.pi * k / 6
            hexbolt((0.16 * math.cos(a), 0.16 * math.sin(a), 0.02), (0, 0, 1), 0.016, 0.014, "steel")

    # -- the expansion bell, knocked over onto the near flank, its foot flange to the east
    with frame((0.88, -1.62, LD_R - 0.02), (0, -math.pi / 2 + 0.12, 0.42)):
        cyl((0, 0, 0.36), LD_R, 0.72, "body_dark", verts=48, bevel=0.03)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=LD_R, location=(0, 0, 0.72), segments=32, ring_count=16)
        o = bpy.context.active_object
        o.scale.z = 0.5
        _finish(o, "body_dark", "static", bevel=0, smooth=True)
        cyl((0, 0, 0.02), LD_R + 0.03, 0.08, "body_dark", verts=48, bevel=0.01)
        for z in (0.3, 0.54):
            torus((0, 0, z), LD_R + 0.004, 0.02, "steel")
    with frame((1.16, -0.6, 0.03), (0.18, -0.1, 0.4)):              # a gauge, face up in the dirt
        cyl((0, 0, 0), 0.105, 0.05, "steel", verts=40, bevel=0.01)
        torus((0, 0, 0.026), 0.098, 0.011, "brass", rot=(0.08, 0, 0), seg=40)
        cyl((0, 0, 0.026), 0.088, 0.004, "dial", verts=40, bevel=0.0)
        strut((-0.01, 0.0, 0.032), (0.06, -0.04, 0.032), 0.012, 0.006, "tie", bevel=0.0)

    # -- the rotor casing: the volute drum burst open to the east, low, its well open to the sky
    shell((RC[0], RC[1], 0.0), R_VOLUTE, R_VOLUTE - 0.06, 0.34, "body_dark", 0.95, 5.75, jag=0.16)
    shell((RC[0], RC[1], 0.0), R_VOLUTE - 0.065, R_VOLUTE - 0.1, 0.28, "recess", 0.95, 5.75, jag=0.14)
    cyl((RC[0], RC[1], 0.03), R_VOLUTE - 0.07, 0.04, "recess", verts=64, bevel=0.0)          # the well's floor
    for k in range(10):                                                                     # rubble in it
        a, rr = RNG.uniform(0, 2 * math.pi), RNG.uniform(0.15, 0.78)
        lump((rr * math.cos(a), rr * math.sin(a), 0.05), RNG.uniform(0.06, 0.13), RNG.choice(("skid", "body_dark")))
    torus((RC[0], RC[1], 0.06), R_VOLUTE + 0.005, 0.03, "body_dark", seg=96)                 # its foot
    for k in range(20):
        a = 2 * math.pi * (k + 0.5) / 20
        if not 1.05 < a < 5.6 or k % 5 == 2:
            continue
        nrm = (math.cos(a), math.sin(a), 0)
        hexbolt((R_VOLUTE * nrm[0], R_VOLUTE * nrm[1], 0.18), nrm, 0.022, 0.018, "steel")
    shard((1.0, 0.12, 0.05), 0.22, 0.03, "body_dark", rot=(0.15, 0.3, 0.3), stretch=(0.7, 1.2))
    shard((0.95, -0.36, 0.04), 0.18, 0.03, "body", rot=(-0.1, 0.3, 1.0), stretch=(0.8, 1.1))
    # the middle collar, thrown off, tilted on the drum's broken rim
    with frame((-0.16, 0.06, 0.26), (0.14, -0.2, 0.4)):
        shell((0, 0, 0), R_CASE, R_WIN, 0.14, "collar", 0.5, 5.6, seg=96, bevel=0.018)
        for k in range(12):
            a = 2 * math.pi * (k + 0.5) / 12
            if not 0.55 < a < 5.5 or k == 6:
                continue
            hexbolt((0.62 * math.cos(a), 0.62 * math.sin(a), 0.14), (0, 0, 1), 0.036, 0.03)
        cyl((-0.72, 0, 0.16), 0.075, 0.04, "steel", verts=32, bevel=0.008)              # the lens's bezel, empty

    # -- the rotor, fallen out of the drum to the east, tilted on the rubble; four vanes and a
    # third of its shroud torn away; three loose vanes on the ground
    with frame((0.66, 0.34, 0.1), (0.3, 0.25, 0.9)):
        cyl((0, 0, 0.0), R_WIN - 0.03, 0.02, "rotor", verts=64, bevel=0.0)
        cyl((0, 0, 0.05), 0.09, 0.09, "rotor", verts=32, bevel=0.01)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(0, 0, 0.1), segments=24, ring_count=12)
        o = bpy.context.active_object
        o.scale.z = 0.6
        _finish(o, "vane", "static", bevel=0, smooth=True)
        for k in range(VANES):
            if k in (2, 3, 7, 10):
                continue
            mesh_object("vane", lambda bm, k=k: vane_build(bm, k), "vane", "static", 0.0)
        shell((0, 0, 0.018), R_WIN - 0.033, R_WIN - 0.057, 0.024, "rotor", 0.3, 4.6, bevel=0.0)
    for (x, y, rz) in ((1.0, 0.86, 0.4), (-0.3, -0.62, 2.2), (1.24, -0.12, 4.1)):
        with frame((x, y, 0.01), (0.1, 0.0, rz)):
            with frame((-0.25, 0, 0)):
                mesh_object("vane", lambda bm: vane_build(bm, 0), "vane", "static", 0.0)

    # -- the north (generator) collar, fallen on its face and leaning on the can's wreck, its
    # winding bared inside it, copper; the can's skin torn off in pieces round it
    with frame((0.06, 1.6, -0.02), (-0.24, 0.12, -0.2)):
        collar_ring(2.1, 2.1 + 5.0, drum_h=0.3, skip=(1, 8))
        with frame((0, 0, 0.22), (0.0, math.pi / 2, 0.3)):                # the winding, on its side
            cyl((0, 0, 0), 0.36, 0.6, "copper", verts=48, bevel=0.01)
            for k in range(12):
                torus((0, 0, -0.27 + k * 0.049), 0.37, 0.018, "copper", seg=48)
    with frame((-1.02, 1.0, 0.0), (0.0, 0.0, 0.12)):                     # the can's skin, on its back
        with frame((0, 0, GC["r"] * 0.78), (math.pi / 2, 0, 0)):
            shell((0, 0, -0.3), GC["r"], GC["r"] - 0.04, 0.6, "gencan", math.pi * 1.33, math.pi * 1.67, jag=0.08,
                  seg=96)
    with frame((0.98, 2.02, 0.0), (0.0, 0.0, 1.9)):
        with frame((0, 0, GC["r"] * 0.85), (math.pi / 2, 0, 0)):
            shell((0, 0, -0.2), GC["r"], GC["r"] - 0.04, 0.4, "gencan", math.pi * 1.36, math.pi * 1.62, jag=0.06,
                  seg=96)
    # its north stub, torn short, lying off the collar to the north-west
    with frame((-0.62, 2.12, R_STUB - 0.08), (math.pi / 2, 0, 1.25)):
        shell((0, 0, 0), R_STUB, R_STUB - 0.04, 0.34, "collar", jag=0.14)
        cyl((0, 0, 0.03), R_STUB + 0.08, 0.06, "collar", verts=64, bevel=0.01)
    # the bushing chamber, knocked over onto the far side, one bushing still on it
    with frame((-0.62, 0.98, 0.16), (0.0, -1.3, 0.35)):
        box((0, 0, 0.0), (0.46, 0.6, 0.3), "gencan", bevel=0.03)
        box((0, 0, 0.162), (0.5, 0.64, 0.024), "body_dark", bevel=0.008)
        for y in (-0.19, 0.0):
            cyl((0, y, 0.19), 0.08, 0.04, "steel", verts=24, bevel=0.006)
        cyl((0, 0.0, 0.36), 0.045, 0.34, "porcelain", verts=24, bevel=0.0)
        for k in range(4):
            cyl((0, 0.0, 0.24 + k * 0.07), 0.088 - 0.006 * k, 0.026, "porcelain", verts=32, bevel=0.01)
        cyl((0, 0.0, 0.54), 0.05, 0.05, "brass", verts=24, bevel=0.008)
        cyl((0, -0.19, 0.25), 0.045, 0.1, "porcelain", verts=24, bevel=0.0)        # one snapped at its root
        cyl((0, -0.19, 0.24), 0.088, 0.026, "porcelain", verts=32, bevel=0.01)
    with frame((1.0, 1.42, 0.07), (math.pi / 2 - 0.08, 0, 2.3)):         # a bushing broken off, on the ground
        cyl((0, 0, 0.0), 0.045, 0.26, "porcelain", verts=24, bevel=0.0)
        for k in range(3):
            cyl((0, 0, -0.08 + k * 0.07), 0.088 - 0.006 * k, 0.026, "porcelain", verts=32, bevel=0.01)
        cyl((0, 0, 0.15), 0.05, 0.05, "brass", verts=24, bevel=0.008)
    for x, y in ((0.55, 2.3), (0.3, 2.42), (-0.15, 2.36), (1.2, 1.7), (-1.15, 2.1)):
        shard((x, y, 0.012), RNG.uniform(0.04, 0.07), 0.018, "porcelain")

    # -- the far flank: the balance line in two, the tray down, the cables sprawled
    for (x, y, rz, L) in ((-1.26, -1.0, 0.06, 1.0), (-1.12, 0.2, -0.42, 0.78)):
        with frame((x, y, R_LAG), (math.pi / 2, 0, rz)):
            cyl((0, 0, 0), R_LAG, L, "lagging", verts=24, bevel=0.01)
            for k in range(int(L / 0.2)):
                torus((0, 0, -L / 2 + 0.1 + 0.2 * k), R_LAG + 0.002, 0.012, "seam", seg=24)
            cyl((0, 0, L / 2 + 0.02), R_LAG + 0.04, 0.05, "steel", verts=24, bevel=0.008)
    with frame((-1.2, -0.38, 0.12), (0.0, 1.35, 0.15)):                  # the gate valve, on its side
        cyl((0, 0, 0), R_LAG + 0.04, 0.24, "body_dark", verts=24, rot=AX_Y, bevel=0.015)
        torus((0, 0, 0.3), 0.11, 0.014, "steel", seg=32)
        cyl((0, 0, 0.18), 0.018, 0.2, "steel", verts=12, bevel=0.0)
    with frame((-1.36, -0.55, 0.02), (0.04, 0.08, 0.03)):                 # the tray: its floor down, a rail bent
        box((0, 0, 0), (0.24, 1.5, 0.02), "steel", bevel=0.004)
        box((-0.115, 0, 0.04), (0.012, 1.5, 0.08), "steel", bevel=0.003)
        for k in range(6):
            box((0, -0.65 + k * 0.26, 0.012), (0.22, 0.03, 0.006), "steel", bevel=0.0)
    with frame((-1.3, 0.62, 0.08), (0.3, -0.1, -0.18)):
        box((0, 0, 0), (0.24, 0.7, 0.02), "steel", bevel=0.004)
        box((0.115, 0, 0.04), (0.012, 0.7, 0.08), "steel", bevel=0.003)
    for (x, y) in ((X_FAR + 0.06, -1.0), (X_FAR + 0.1, 0.05)):            # the posts, sheared at their feet
        box((x, y, 0.03), (0.06, 0.06, 0.06), "steel", bevel=0.005)
        foot_plate(x, y, 0.12)
    strut((X_FAR + 0.1, 0.05, 0.03), (X_FAR + 0.4, 0.62, 0.05), 0.06, 0.06)
    bundle([(-1.32, 1.42, 0.05), (-1.24, 0.95, 0.04), (-1.36, 0.3, 0.03), (-1.28, -0.4, 0.06), (-1.4, -1.1, 0.04),
            (-1.18, -1.62, 0.08)], ["cable-black", "cable-red", "cable-grey", "cable-black"], r=0.016, gap=0.034,
           lie=(0, 0, 1))
    for k, (dx, dy, m) in enumerate(((-0.1, 0.2, "cable-black"), (0.02, 0.28, "cable-red"),
                                     (0.12, 0.18, "cable-grey"))):          # its end, frayed
        poly_tube(spline([(-1.32 + (k - 1) * 0.03, 1.42, 0.05), (-1.32 + dx * 0.5, 1.42 + dy * 0.5, 0.06),
                          (-1.32 + dx, 1.42 + dy, 0.02)], per=8), 0.016, m)
    # the terminal box, crushed; its brass lid thrown off to the north
    box(((TBF["x0"] + TBF["x1"]) / 2 + 0.05, 1.62, 0.15), (TBF["x1"] - TBF["x0"], 0.56, 0.3), "body_dark",
        rot=(0.1, 0.18, 0.05), bevel=0.03)
    with frame((-0.9, 2.2, 0.03), (0.06, -0.05, 0.62)):
        box((0, 0, 0), (TBF["x1"] - TBF["x0"] - 0.04, TBF["y1"] - TBF["y0"] - 0.04, 0.04), "brass", bevel=0.012)
        for sx, sy in ((-0.17, -0.3), (0.17, 0.3), (0.17, -0.3)):
            hexbolt((sx, sy, 0.02), (0, 0, 1), 0.016, 0.014, "steel")

    # -- the near flank: the brass terminal box fallen on its back, the hose loose, the gas pipe torn
    box((1.12, 0.98, 0.09), (0.44, 0.42, 0.16), "brass", rot=(0, 0.06, 0.35), bevel=0.02)
    box((1.12, 0.98, 0.18), (0.38, 0.36, 0.02), "brass", rot=(0, 0.06, 0.35), bevel=0.01)
    pts = hose([(0.5, -0.82, 0.22), (1.0, -0.62, 0.05), (1.22, -0.25, 0.04), (1.0, 0.25, 0.16), (1.2, 0.62, 0.04),
                (1.3, 1.35, 0.03), (1.06, 1.78, 0.05)], 0.032, ends=False)
    ferrule(pts[0] + (pts[3] - pts[0]).normalized() * 0.03, pts[3] - pts[0], 0.032)
    pipe([(0.72, -0.6, 0.26), (0.98, -0.42, 0.22), (1.02, -0.1, 0.06)], 0.06, "copper", bend=0.16)   # ripped out
    cyl((0.7, -0.62, 0.26), 0.095, 0.05, "steel", verts=24, rot=facing((-0.6, -0.5, 0)), bevel=0.008)
    bundle([(0.86, 0.98, 0.1), (0.98, 1.3, 0.05), (0.84, 1.62, 0.03), (0.66, 2.0, 0.05)],
           ["cable-black", "cable-red", "cable-grey"], r=0.016, gap=0.034, lie=(0, 0, 1))

    # -- the top runs, fallen: the copper bus bent and snapped, the top pipe across the wreck
    for k, y in enumerate(BUSH_Y):
        pipe([(-0.35 - 0.06 * k, y - 0.1, 0.32 - 0.05 * k), (-0.7, y, 0.26), (-0.92, y + 0.12 * k - 0.1, 0.1),
              (-1.06 + 0.05 * k, y + 0.2 + 0.1 * k, 0.03)], 0.024, "copper", bend=0.12)
    pipe([(-0.42, -1.3, 0.34), (-0.62, -0.95, 0.3), (-0.8, -0.4, 0.16), (-0.66, 0.42, 0.05), (-0.36, 0.78, 0.05)],
         0.042, "copper", bend=0.18)

    # -- plates, bolts thrown low round it, a few past the footprint's edge
    for k in range(22):
        a = RNG.uniform(0, 2 * math.pi)
        rr = RNG.uniform(0.55, 1.08)
        shard((1.5 * rr * math.cos(a), 2.5 * rr * math.sin(a), 0.012), RNG.uniform(0.05, 0.12), 0.022,
              RNG.choice(("body", "body_dark", "gencan", "collar", "steel")))
    for k in range(34):
        a = RNG.uniform(0, 2 * math.pi)
        rr = RNG.uniform(0.3, 1.06)
        hexbolt((1.5 * rr * math.cos(a), 2.5 * rr * math.sin(a), 0.0),
                (RNG.uniform(-0.6, 0.6), RNG.uniform(-0.6, 0.6), 1.0), 0.024, 0.022, RNG.choice(("bronze", "steel")))
    _group.pop()

# ---------------------------------------------------------------- passes

SUN = rig.sun()
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()


def setup(visible=(), catchers=(), holdouts=(), ground=False):
    """Per pass: which groups the camera sees, catch shadow on, or cut out."""
    for g, objs in PARTS.items():
        for o in objs:
            o.hide_render = (g not in visible and g not in catchers and g not in holdouts) \
                or ONLY.get(o.name) not in (None, CUR[0])
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

    def meant(a, b):
        return a == b or b in HOSTS.get(a, ()) or a in HOSTS.get(b, ())
    for cd in ("horizontal", "vertical"):    # the two directions' ends are their own parts
        pose(0)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        fixed = [o for g, objs in PARTS.items() if g != "rotor" for o in objs if ONLY.get(o.name) in (None, cd)]
        by_asm = {}
        for o in fixed:
            by_asm.setdefault(ASM[o.name], []).append(o)
        trees = {a: tree(objs) for a, objs in by_asm.items()}
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
            print(f"COLLIDE {cd} {a} x {b}: {n} face pairs")
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
            print(f"COLLIDE {cd} rotor x {a}: frames {fs}")
        print(f"COLLIDE {cd} assemblies {len(names)}, fixed clashes {len(clashes)}, rotor clashes {len(rotor_hits)}")
    sys.exit(0)

if ICON:
    import icon_rig
    sc.cycles.samples = 128
    ROOT.rotation_euler.z = -math.pi / 2                 # horizontal, as the item is held
    BODY.location.x = PLACE["horizontal"]
    CUR[0] = "horizontal"
    cam = rig.camera(1024, 1024, ss=1)
    setup(visible=("static", "lens", "rotor"))
    icon_rig.frame(cam, [o for g in ("static", "lens", "rotor") for o in PARTS[g]
                         if ONLY.get(o.name) in (None, "horizontal")], 1024, margin=8)
    rig.render(f"{OUT_DIR}/icon.png")
    sys.exit(0)

contract.declare(OUT_DIR, canvas=CANVAS, **DECL)
rig.camera(*CANVAS)


def lens_cut(on):
    """The status lens as the light pass wants it: lit white, for the engine to tint."""
    M["lens"].node_tree.nodes["white"].outputs[0].default_value = 1.0 if on else 0.0


def window(x0, x1, y0, y1):
    """Render only a window of the canvas: screen tiles from the origin, x right, y down."""
    cw, ch = CANVAS
    sc.render.use_border, sc.render.use_crop_to_border = True, False
    sc.render.border_min_x = (cw / 2 + x0 * rig.PX_PER_TILE) / cw
    sc.render.border_max_x = (cw / 2 + x1 * rig.PX_PER_TILE) / cw
    sc.render.border_max_y = 1 - (ch / 2 + y0 * rig.PX_PER_TILE) / ch
    sc.render.border_min_y = 1 - (ch / 2 + y1 * rig.PX_PER_TILE) / ch


STATIC = ("static", "lens")
MOVING = ("rotor",)
ROT = DECL["animations"][0]
if FLAT or IDLE:
    sc.cycles.samples = int(os.environ.get("SAMPLES", "24" if FLAT else "48"))

for d in ([] if WRECK_ONLY else contract.each_direction(ROOT, DECL["directions"])):
    def path(stem, d=d):
        return f"{OUT_DIR}/{contract.named(stem, d)}.png"
    BODY.location.x, BODY.location.y = PLACE[d], -SOUTH[d]
    CUR[0] = d
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
    # the status lens alone, white, everything in front of it cut out
    setup(visible=("lens",), holdouts=("static",) + MOVING)
    lens_cut(True)
    rig.render(path("lens"))
    lens_cut(False)
    # the rotor: its window only, its shadow caught on the bore and the well under it
    east, north = (0.0, -SOUTH[d]) if d == "vertical" else (0.0, -PLACE[d])
    sy = -(north + Z_ROTOR / 2)
    window(east - 0.62, east + 0.62, sy - 0.5, sy + 0.5)
    for f in range(ROT["frames"]):
        pose(f)
        setup(visible=MOVING, catchers=STATIC)
        rig.render(path(contract.frame(ROT["name"], f)))
    pose(0)
    sc.render.use_border = False
BODY.location.x, BODY.location.y = 0.0, 0.0
CUR[0] = None

# the wreck (section 10), on its own canvas over the ground catcher: its shadow and scorch
# caught in the same picture, as vanilla's remnants carry theirs; the machine where it stood
# (BODY at the origin: the wreck lies on the footprint, not on the plate's PLACE or SOUTH)
if not IDLE:
    if FLAT:
        sc.cycles.samples = int(os.environ.get("SAMPLES", "24"))
    rig.camera(*WRECK_CANVAS)
    sc.render.use_border = False
    CUR[0] = "wreck"
    for d in contract.each_direction(ROOT, DECL["directions"]):
        setup(visible=("wreck",), ground=True)
        rig.render(f"{OUT_DIR}/{contract.named('wreck', d)}.png")
    CUR[0] = None
