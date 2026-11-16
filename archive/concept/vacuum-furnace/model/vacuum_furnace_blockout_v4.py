"""Vacuum furnace: a blockout, revision 4 -- the flat hatch, the viewport as the
indicator, and the vacuum pump.

  blender -b --python vacuum_furnace_blockout_v4.py -- <out-dir>
  then: python3 tools/blender/downsample.py <out-dir> <render-dir>

Untextured, as revision 3 (vacuum_furnace_blockout.py, approved 2026-10-02) was:
plain greys, one tone per kind of part. What changes, from the spec as amended
2026-10-07 (sections 3.2, 3.3 and 6):
  - the hull is revision 3's, unchanged;
  - the drum is round (no squash) and stands on the footprint's centre, and its deck
    is level with the hull's rail, so the parapet runs round the hatch evenly;
  - the hatch is flat in the roof: no dome, no lifting eye, all eight dogs;
  - the sight port is at the hatch's centre, its glass flat in the roof; it is the
    indicator, and there is no separate lamp;
  - three radiator stacks, north-west, north-east and south-west;
  - the south-east niche holds the vacuum pump: a barrel standing in the niche, a
    spoked flywheel in front of it facing the camera, free all round with its hub
    on the shaft (the shaft hidden behind it), and a vacuum gauge on the barrel's
    top, its dull dial recessed in a hooded case. The gauge's needle is
    Animatorio's (spec 6), so the dial is drawn bare here.

Units are tiles; north is +Y; a model point (x, y, z) lands at screen
(x, y + z/2) tiles from the origin.
"""
import math
import os
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import rig  # noqa: E402
import contract  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = argv[0]
os.makedirs(OUT_DIR, exist_ok=True)

CANVAS = (320, 288)
DECL = dict(
    footprint=(3, 3), directions="one",
    passes=[dict(name="idle", kind="plate", sheet="base"),
            dict(name="working", kind="glow", over="idle", sheet="port-glow"),
            dict(name="shadow", kind="shadow", sheet="base-shadow")],
    animations=[], ports=[],
)

sc = rig.reset()
ROOT = rig.turntable(rig.stretch_root())


def grey(name, hexcol, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb(hexcol)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


M = {
    "plinth": grey("plinth", "#4A4844"),
    "drum": grey("drum", "#6A6762"),
    "hatch": grey("hatch", "#9A9894"),
    "clamp": grey("clamp", "#7E7A74"),
    "radiator": grey("radiator", "#5E5C58"),
    "frame": grey("frame", "#76736E"),
    "socket": grey("socket", "#8C8A86"),
    "dial": grey("dial", "#8E877B", rough=0.6),
    "wheel": grey("wheel", "#A8A49E", rough=0.35, metal=0.6),
}
port = bpy.data.materials.new("port")
port.use_nodes = True
pb = port.node_tree.nodes["Principled BSDF"]
pb.inputs["Base Color"].default_value = rig.srgb("#1E1A16")
pb.inputs["Emission Color"].default_value = rig.srgb("#F0BC72")      # mid of #E8A24A -> #FFD9A0
pb.inputs["Emission Strength"].default_value = 0.0
M["port"] = port

PARTS = {}


def _finish(obj, mat, group="static", bevel=0.01, parent=None):
    obj.data.materials.append(M[mat])
    if bevel:
        mod = obj.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments, mod.limit_method = bevel, 2, "ANGLE"
    for p in getattr(obj.data, "polygons", []):
        p.use_smooth = True
    obj.parent = parent or ROOT
    PARTS.setdefault(group, []).append(obj)
    return obj


def box(loc, size, mat, rot=(0, 0, 0), bevel=0.01, parent=None, group="static"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    for p in o.data.polygons:
        p.use_smooth = False
    return _finish(o, mat, group, bevel, parent)


def cyl(loc, r, h, mat, rot=(0, 0, 0), verts=48, bevel=0.008, parent=None, group="static"):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    return _finish(bpy.context.active_object, mat, group, bevel, parent)


def torus(loc, major, minor, mat, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, rotation=rot,
                                     major_segments=64, minor_segments=10)
    return _finish(bpy.context.active_object, mat, bevel=0, parent=parent)


def ring(loc, r_out, r_in, h, mat, parent=None, verts=48, group="static"):
    me = bpy.data.meshes.new("ring")
    bm = bmesh.new()
    rows = [[bm.verts.new((r * math.cos(2 * math.pi * i / verts), r * math.sin(2 * math.pi * i / verts), z))
             for i in range(verts)] for r, z in ((r_out, -h / 2), (r_out, h / 2), (r_in, h / 2), (r_in, -h / 2))]
    for k in range(4):
        a, b = rows[k], rows[(k + 1) % 4]
        for i in range(verts):
            j = (i + 1) % verts
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("ring", me)
    sc.collection.objects.link(o)
    o.location = loc
    return _finish(o, mat, group, 0.008, parent)


def prism(points, z0, z1, mat, bevel=0.015):
    me = bpy.data.meshes.new("prism")
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, z0)) for x, y in points]
    hi = [bm.verts.new((x, y, z1)) for x, y in points]
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    for i in range(len(points)):
        j = (i + 1) % len(points)
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("prism", me)
    sc.collection.objects.link(o)
    return _finish(o, mat, "static", bevel)


def empty(loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None):
    e = bpy.data.objects.new("e", None)
    sc.collection.objects.link(e)
    e.parent = parent or ROOT
    e.location, e.rotation_euler, e.scale = loc, rot, scale
    return e


TILT = (math.atan2(0.8, 0.6), 0, 0)       # a face that lands as a circle, as in vacuum_furnace.py

# 1. The lower hull: revision 3's battered octagon, its face middles on the
# footprint edge, its corners cut back into niches.
HZ, E, C, LEAN = 1.2, 1.482, 0.9, 0.22


def octagon(e, c):
    return [(-e, -e + c), (-e + c, -e), (e - c, -e), (e, -e + c), (e, e - c), (e - c, e), (-e + c, e), (-e, e - c)]


def loft(lo, hi, z0, z1, mat, bevel=0.02):
    """A slab from outline `lo` at z0 to outline `hi` at z1 (same point count): a battered wall."""
    me = bpy.data.meshes.new("loft")
    bm = bmesh.new()
    a = [bm.verts.new((x, y, z0)) for x, y in lo]
    b = [bm.verts.new((x, y, z1)) for x, y in hi]
    bm.faces.new(list(reversed(a)))
    bm.faces.new(b)
    for i in range(len(lo)):
        j = (i + 1) % len(lo)
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("loft", me)
    sc.collection.objects.link(o)
    return _finish(o, mat, "static", bevel)


def octagon_ring(outer, inner, z0, z1, mat):
    """A slab between two octagons: the cap rail round the hull's top."""
    me = bpy.data.meshes.new("rail")
    bm = bmesh.new()
    rows = [[bm.verts.new((x, y, z)) for x, y in pts] for pts, z in
            ((outer, z0), (outer, z1), (inner, z1), (inner, z0))]
    n = len(outer)
    for k in range(4):
        r0, r1 = rows[k], rows[(k + 1) % 4]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("rail", me)
    sc.collection.objects.link(o)
    return _finish(o, mat, "static", 0.012)


CT = C - LEAN * (2 - math.sqrt(2))           # the chamfer leans back by LEAN too
ER = E - LEAN
loft(octagon(E, C), octagon(ER, CT), 0, HZ, "plinth", bevel=0.03)
octagon_ring(octagon(ER + 0.01, CT), octagon(ER - 0.1, CT - 0.04), HZ - 0.01, HZ + 0.05, "frame")
PZ = HZ + 0.05

# 2. The drum, round and centred, its deck level with the rail's top; the flat
# hatch on it.
R, H, RD = 0.89, PZ, 1.08
cyl((0, 0, H / 2), RD, H, "drum", verts=128, bevel=0.02)
cyl((0, 0, H + 0.02), R + 0.03, 0.06, "hatch", verts=128)                      # flange ring
cyl((0, 0, H + 0.07), R - 0.04, 0.05, "hatch", verts=128)                      # the flat hatch plate
TOPZ = H + 0.095
for k in range(8):                                                              # all eight dogs
    a = math.radians(k * 45)
    loc = lambda r, z: (r * math.cos(a), r * math.sin(a), z)                   # noqa: E731
    box(loc(0.84, H + 0.13), (0.32, 0.17, 0.11), "clamp", rot=(0, 0, a))
    box(loc(0.97, H + 0.0), (0.09, 0.2, 0.3), "clamp", rot=(0, 0, a))
    box(loc(0.7, H + 0.16), (0.09, 0.21, 0.13), "clamp", rot=(0, 0, a))

# 3. The sight port at the hatch's centre, its glass flat in the roof: a low boss,
# a bolted ring, a deep bore and the glass at its bottom. It is the indicator.
cyl((0, 0, TOPZ + 0.03), 0.27, 0.06, "drum", verts=64)                          # boss, its top at TOPZ + 0.06
ring((0, 0, TOPZ + 0.115), 0.24, 0.16, 0.05, "frame")                           # bolted ring
ring((0, 0, TOPZ + 0.1), 0.165, 0.15, 0.08, "plinth")                           # deep bore, standing on the boss
bpy.ops.mesh.primitive_circle_add(vertices=48, radius=0.152, fill_type="NGON", location=(0, 0, TOPZ + 0.065))
glass = bpy.context.active_object
_finish(glass, "port", "port", bevel=0)
for prop in ("visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
    setattr(glass, prop, False)

# 4. Three radiator stacks, across the diagonal in the north-west, north-east and
# south-west niches, as revision 3's.
CZ = 0.55
for cx, cy in ((-1, 1), (1, 1), (-1, -1)):
    d = math.atan2(cy, cx)
    px, py = cx * 1.12, cy * 1.12
    t = d + math.pi / 2
    cyl((px, py, CZ), 0.1, 0.5, "radiator", rot=(math.pi / 2, 0, t + math.pi / 2), verts=24)
    for i in range(10):
        s = -0.22 + i * 0.44 / 9
        cyl((px + s * math.cos(t), py + s * math.sin(t), CZ), 0.15, 0.024, "radiator",
            rot=(math.pi / 2, 0, t + math.pi / 2), verts=32, bevel=0.004)
    for s in (-0.27, 0.27):
        fx, fy = px + s * math.cos(t), py + s * math.sin(t)
        box((fx, fy, CZ - 0.05), (0.05, 0.4, 0.42), "frame", rot=(0, 0, t + math.pi / 2))
        box((fx, fy, (CZ - 0.2) / 2), (0.06, 0.06, CZ - 0.2), "frame")
    for zb in (CZ - 0.12, CZ + 0.12):
        box((px - 0.2 * math.cos(d), py - 0.2 * math.sin(d), zb), (0.26, 0.05, 0.05), "frame", rot=(0, 0, d))
for cx in (-1, 1):                                # the lifting lugs, on the hull's back corners
    lx, ly = cx * 0.84, 0.84
    box((lx, ly, PZ + 0.04), (0.14, 0.14, 0.08), "clamp")
    lug = empty(loc=(lx, ly - 0.02, PZ + 0.18), rot=TILT)
    box((0, -0.07, 0), (0.18, 0.14, 0.06), "frame", parent=lug)
    torus((0, 0.03, 0), 0.075, 0.035, "frame", parent=lug)

# 5. The vacuum pump, in the south-east niche (the corner triangle outside the
# hull's chamfer, x - y >= 2.064 at the ground), at 1.3x the first cut so it fills
# the niche (Liam, 2026-10-07). A barrel stands at the back of the niche on a foot;
# its suction line runs into the hull's chamfer.
BX, BY, BR, BH = 1.24, -1.06, 0.17, 0.62
box((BX, BY, 0.035), (0.4, 0.4, 0.07), "frame", rot=(0, 0, math.radians(45)))   # foot
cyl((BX, BY, 0.07 + BH / 2), BR, BH, "drum", verts=48)                          # barrel
cyl((BX, BY, 0.07 + BH + 0.025), BR + 0.025, 0.05, "frame", verts=48)           # its head
for zr in (0.22, 0.52):
    torus((BX, BY, zr), BR + 0.006, 0.015, "frame")                               # barrel bands
SUCK = empty(loc=(BX - 0.2, BY + 0.2, 0.5), rot=(0, math.pi / 2, math.radians(135)))
cyl((0, 0, 0), 0.055, 0.26, "frame", verts=24, parent=SUCK)                      # suction line
# The flywheel: in front of the barrel, facing the camera, turning about its shaft.
# Free all round -- nothing touches its rim. Its shaft and bearing run straight back
# along its axis, which points at the camera, so the hub hides them and nothing
# still shows between the spokes but the barrel and niche behind (Liam, 2026-10-07).
WX, WY, WZ, WR = 1.08, -1.28, 0.36, 0.26
HUB = 0.055
WHEEL = empty(loc=(WX, WY, WZ), rot=TILT)
bear = empty(loc=(WX, WY, WZ), rot=TILT)
cyl((0, 0, -0.12), HUB - 0.015, 0.2, "frame", verts=24, parent=bear)             # shaft, inside the hub's outline
torus((0, 0, 0), WR - 0.03, 0.03, "wheel", parent=WHEEL)                         # rim
for k in range(6):                                                               # spokes
    a = 2 * math.pi * k / 6
    box((0.5 * (WR - 0.035) * math.cos(a), 0.5 * (WR - 0.035) * math.sin(a), 0), (WR - 0.035, 0.036, 0.03),
        "wheel", rot=(0, 0, a), parent=WHEEL)
cyl((0, 0, 0), HUB, 0.07, "wheel", verts=24, parent=WHEEL)                       # hub, on the shaft
# The vacuum gauge on the barrel's head, its dial facing the camera, set deep in a
# hooded case so it sits in shade and never reads as a light (Liam, 2026-10-07).
# Bare: the needle is Animatorio's.
GZ = 0.07 + BH + 0.16
post = empty(loc=(BX, BY, GZ - 0.08))
cyl((0, 0, 0), 0.03, 0.1, "frame", verts=16, parent=post)
GAUGE = empty(loc=(BX, BY - 0.02, GZ + 0.05), rot=TILT)
cyl((0, 0, -0.03), 0.13, 0.06, "frame", verts=48, parent=GAUGE)                  # case
ring((0, 0, 0.02), 0.13, 0.1, 0.05, "frame", parent=GAUGE)                       # the hood, proud of the dial
cyl((0, 0, 0.0), 0.1, 0.004, "dial", verts=48, parent=GAUGE)                     # dial face, recessed

# 6. No sockets: the fluid input is vanilla's engine-drawn pipe picture and cover,
# composited in the review only.
# ---------------------------------------------------------------- passes
rig.sun()
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()
ALL = [o for objs in PARTS.values() for o in objs]
contract.declare(OUT_DIR, canvas=CANVAS, **DECL)
rig.camera(*CANVAS)
sc.cycles.samples = 32


def show(ground=False):
    for o in ALL:
        o.hide_render = False
        o.visible_camera = not ground
    GROUND.hide_render = not ground
    BOUNCE.hide_render = ground


show()
rig.render(f"{OUT_DIR}/idle.png")
pb.inputs["Emission Strength"].default_value = 1.2
rig.render(f"{OUT_DIR}/working.png")
pb.inputs["Emission Strength"].default_value = 0.0
show(ground=True)
rig.render(f"{OUT_DIR}/shadow.png")
