"""Vacuum furnace, redesigned layout: a blockout, revision 3.

  blender -b --python vacuum_furnace_blockout.py -- <out-dir>
  then: python3 tools/blender/downsample.py <out-dir> <render-dir>
        python3 tools/blender/preview.py <render-dir> concept/vacuum-furnace/model/blockout.png \
            --adopted graphics/entity/vacuum-furnace/base.png@0,0

Untextured: plain greys, one tone per kind of part, so the layout is judged and
not the finish. Revision 2 follows Liam's two rules (2026-10-02, for every
building): a fluid input is vanilla's own engine-drawn pipe picture and cover,
never a modelled socket; and there is no flat base -- the machine is one
structure filling its footprint.
  - a lower hull, octagonal and battered (its walls lean back): its face middles
    stand on the footprint edge, a wall for vanilla's pipe stub to butt against,
    as the assembler's body does. Revision 3 sizes it to the stub: assembler-3's
    south picture is drawn 0.766 tiles up from the outside tile, so its bolted
    plate's top lands 0.688 tiles below the origin on screen, 0.80 screen tiles up
    from the footprint edge. Through this camera a height shows at half, so a
    plumb wall would have to stand 1.6; leaning back 0.22 over 1.2 of height, the
    face's top lands at 0.67 below the origin, just over the plate. All four faces
    are the same, so whichever way the input turns, its plate sits on wall;
  - the drum grown out of it (R 1.08) and raised (H 1.6) to clear the hull; the
    hatch, its clamps, the fault lamp and the eye keep the finished model's sizes
    and their places on the drum, on a deck ring round them;
  - four radiator stacks, one per corner across the diagonal, in niches cut into
    the hull's corners and bracketed to it;
  - the sight port in the roof: a deep glass viewport on the hatch's south-west
    shoulder, between two clamps, well clear of the lamp at the north.

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
    "lens": grey("lens", "#E6E6E2", rough=0.25),
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

# 1. The lower hull: one battered body with the drum, its face middles on the
# footprint edge (the wall vanilla's pipe stub meets), its corners cut into niches
# for the stacks.
HZ, E, C, LEAN = 1.2, 1.49, 0.9, 0.22


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


# the chamfer leans back by LEAN too, measured square to it
CT = C - LEAN * (2 - math.sqrt(2))
loft(octagon(E, C), octagon(E - LEAN, CT), 0, HZ, "plinth", bevel=0.03)
prism(octagon(E - LEAN - 0.02, CT), HZ, HZ + 0.05, "frame", bevel=0.015)         # a cap rail round the top
PZ = HZ + 0.05

# 2. The drum, roof, hatch, clamps and lamp: the finished model's, unchanged.
YC, K, R, ZB, H = -0.34, 0.86, 0.89, 0.0, 1.6
RD = 1.08                                   # the drum wall, grown; the hatch keeps R
BODY = empty(loc=(0, YC, 0), scale=(1, K, 1))


def on_body(a, r, z):
    return (r * math.cos(a), r * math.sin(a), z)


cyl((0, 0, (ZB + H) / 2), RD, H - ZB, "drum", verts=128, bevel=0.02, parent=BODY)
cyl((0, 0, PZ + 0.04), RD + 0.035, 0.08, "drum", verts=128, parent=BODY)          # foot ring on the hull
cyl((0, 0, H + 0.02), R + 0.03, 0.06, "hatch", verts=128, parent=BODY)
cyl((0, 0, H + 0.07), R - 0.04, 0.05, "hatch", verts=128, parent=BODY)
DOME_R, DOME_H, DZ = R - 0.11, 0.24, H + 0.09
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, DZ), segments=96, ring_count=32)
dome = bpy.context.active_object
dome.scale = (DOME_R, DOME_R, DOME_H)
bpy.ops.object.transform_apply(scale=True)
_finish(dome, "hatch", bevel=0, parent=BODY)
TOPZ = DZ + DOME_H
cyl((0, 0, TOPZ + 0.02), 0.27, 0.07, "hatch", verts=64, parent=BODY)
cyl((0, 0, TOPZ + 0.12), 0.12, 0.14, "frame", verts=32, parent=BODY)
EYE = empty(loc=(0, -0.01, TOPZ + 0.3), rot=TILT, parent=BODY)
box((0, -0.08, 0), (0.2, 0.16, 0.07), "frame", parent=EYE)
torus((0, 0.03, 0), 0.085, 0.04, "frame", parent=EYE)
for k in range(8):
    a = math.radians(k * 45)
    if k == 2:
        continue
    box(on_body(a, 0.84, H + 0.13), (0.32, 0.17, 0.11), "clamp", rot=(0, 0, a), parent=BODY)
    box(on_body(a, 0.97, H + 0.0), (0.09, 0.2, 0.3), "clamp", rot=(0, 0, a), parent=BODY)
    box(on_body(a, 0.7, H + 0.16), (0.09, 0.21, 0.13), "clamp", rot=(0, 0, a), parent=BODY)
a = math.radians(90)
box(on_body(a, 0.95, H + 0.08), (0.2, 0.2, 0.16), "clamp", rot=(0, 0, a), parent=BODY)
cyl(on_body(a, 0.95, H + 0.18), 0.085, 0.05, "frame", verts=32, parent=BODY)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=on_body(a, 0.95, H + 0.2), segments=24, ring_count=12)
lens = bpy.context.active_object
lens.scale.z = 0.7
_finish(lens, "lens", bevel=0, parent=BODY)

# 3. The sight port, moved into the roof: a thick deep glass viewport on a boss on
# the hatch's south-west shoulder, between the clamps at 180 and 225 degrees,
# facing the camera. The north rim keeps the lamp; the two lights never meet.
VA = math.radians(202.5)
vx, vy = 0.72 * math.cos(VA), YC + K * 0.72 * math.sin(VA)
vz = DZ + DOME_H * math.sqrt(1 - (0.72 / DOME_R) ** 2)
VP = empty(loc=(vx, vy - 0.03, vz + 0.12), rot=TILT)
cyl((0, 0, -0.2), 0.16, 0.24, "drum", verts=48, parent=VP)                     # body, back into the dome
ring((0, 0, 0.0), 0.15, 0.075, 0.06, "frame", parent=VP)                        # bolted rim
ring((0, 0, -0.03), 0.08, 0.065, 0.1, "plinth", parent=VP)                      # deep bore
bpy.ops.mesh.primitive_circle_add(vertices=40, radius=0.072, fill_type="NGON", location=(0, 0, -0.075))
glass = bpy.context.active_object
_finish(glass, "port", "port", bevel=0, parent=VP)
for prop in ("visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
    setattr(glass, prop, False)

# 4. Four radiator stacks, one per corner, lying across the corner's diagonal on a
# low frame: the middle of every face stays free for its socket.
for cx in (-1, 1):
    for cy in (-1, 1):
        d = math.atan2(cy, cx)                    # the diagonal out to this corner
        px, py = cx * 1.12, cy * 1.12               # in the corner niche
        t = d + math.pi / 2                       # the stack's axis, across the diagonal
        CZ = 0.55
        cyl((px, py, CZ), 0.1, 0.5, "radiator", rot=(math.pi / 2, 0, t + math.pi / 2), verts=24)
        for i in range(10):
            s = -0.22 + i * 0.44 / 9
            cyl((px + s * math.cos(t), py + s * math.sin(t), CZ), 0.15, 0.024, "radiator",
                rot=(math.pi / 2, 0, t + math.pi / 2), verts=32, bevel=0.004)
        for s in (-0.27, 0.27):                   # end frames, on legs to the ground
            fx, fy = px + s * math.cos(t), py + s * math.sin(t)
            box((fx, fy, CZ - 0.05), (0.05, 0.4, 0.42), "frame", rot=(0, 0, t + math.pi / 2))
            box((fx, fy, (CZ - 0.2) / 2), (0.06, 0.06, CZ - 0.2), "frame")      # leg
        for zb in (CZ - 0.12, CZ + 0.12):          # brackets back to the hull's chamfer
            box((px - 0.2 * math.cos(d), py - 0.2 * math.sin(d), zb), (0.26, 0.05, 0.05), "frame", rot=(0, 0, d))
        if cy > 0:                                # the lifting lugs, on the hull's back corners
            lx, ly = cx * 0.84, 0.84
            box((lx, ly, PZ + 0.04), (0.14, 0.14, 0.08), "clamp")
            lug = empty(loc=(lx, ly - 0.02, PZ + 0.18), rot=TILT)
            box((0, -0.07, 0), (0.18, 0.14, 0.06), "frame", parent=lug)
            torus((0, 0.03, 0), 0.075, 0.035, "frame", parent=lug)

# 5. No sockets: the fluid input is vanilla's engine-drawn pipe picture and cover
# (assembler3pipepictures, pipecoverspictures()), composited in the review only.

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
