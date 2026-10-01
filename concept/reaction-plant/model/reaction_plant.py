"""Reaction plant (sae-reaction-plant), built from its spec, rendered in every pass.

  tools/blender/render.sh concept/reaction-plant/model/reaction_plant.py <out-dir>
  (or directly: blender -b --python reaction_plant.py -- <out-dir> [--icon | --ports | --idle])
  --idle renders idle.png and working.png only: the quick loop for tuning finish and light.

Units are tiles; north is +Y. Spec: concept/reaction-plant/building-spec-reaction-plant.md
(section 3.1 bottom to top, 3.3 palette, 6.2 what moves, 8 hard constraints).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))


def swatch(name):
    """This building's concept swatches: swatches/bake_concept.py."""
    return os.path.join(HERE, "swatches", f"concept_{name}.png")

import rig  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = argv[0]
os.makedirs(OUT_DIR, exist_ok=True)
ICON = "--icon" in argv
PORTS = "--ports" in argv
IDLE = "--idle" in argv

sc = rig.reset()
ROOT = rig.stretch_root()

# ---------------------------------------------------------------- materials

from materials import layered, hazard_pattern, emissive  # noqa: E402

M = {
    # palette: spec 3.3. Shell and skirt are painted kamacite plate worn to metal;
    # lead is dull and barely worn; cast iron is bare; copper and brass are bare metal.
    "shell":  layered("shell", "#4C4135", wear=0.6, rust=0.25, dust=0.12, swatch=swatch("drum")),
    "skirt":  layered("skirt", "#453B30", wear=0.65, rust=0.3, dust=0.3, swatch=swatch("drum")),
    "steel":  layered("steel", "#8A857C", metal="#C8C2B6", paint_metal=0.9, paint_rough=0.2,
                      wear=0.5, rust=0.15, dust=0.1, grime=0.5),
    "lead":   layered("lead", "#5E5E66", metal="#8A8A92", paint_metal=0.3, paint_rough=0.7,
                      wear=0.3, rust=0.0, jitter=0.06, swatch=swatch("band")),
    "cast":   layered("cast", "#36363C", metal="#6A6A70", paint_metal=0.5, paint_rough=0.7,
                      wear=0.3, rust=0.3, swatch=swatch("cast")),
    "copper": layered("copper", "#94592C", metal="#B88050", paint_metal=0.9, paint_rough=0.4,
                      wear=0.4, rust=0.0, dust=0.25, grime=0.5, swatch=swatch("copper")),
    "brass":  layered("brass", "#9C7034", metal="#C09A58", paint_metal=0.9, paint_rough=0.38,
                      wear=0.4, rust=0.0, dust=0.2, swatch=swatch("brass")),
    # weathered to the concept on the plate; clean #2A7F7A in the icon, whose
    # 16 px teal area is what tells it apart (spec 3.3)
    "teal":   layered("teal", "#2A7F7A", paint_metal=0.0, paint_rough=0.8, wear=0.0, rust=0.0, dust=0.0)
              if ICON else
              layered("teal", "#1C5A56", paint_metal=0.0, paint_rough=0.8, wear=0.6, rust=0.3, swatch=swatch("teal")),
    "gauge":  layered("gauge", "#D8D2C0", paint_metal=0.0, paint_rough=0.4, wear=0.0, rust=0.0,
                      dust=0.1, grime=0.2, jitter=0.03),
    "hazard": layered("hazard", "#B8962E", paint_metal=0.1, paint_rough=0.8, wear=0.6,
                      rust=0.4, pattern=hazard_pattern),
    "slot":   emissive("slot", "#A8E8C0"),
    "lens":   emissive("lens", "#FFFFFF"),
}

# ---------------------------------------------------------------- geometry

PARTS = {}          # group name -> [objects]; the passes toggle whole groups


def _finish(obj, mat, group, bevel=0.015, smooth=False):
    obj.data.materials.append(M[mat])
    if bevel:
        mod = obj.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    obj.parent = ROOT
    PARTS.setdefault(group, []).append(obj)
    return obj


def box(loc, size, mat, group="static", rot_z=0.0, bevel=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=(0, 0, rot_z))
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, group, bevel)


def cyl(loc, r, h, mat, group="static", verts=48, rot=(0, 0, 0), bevel=0.012):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h,
                                        location=loc, rotation=rot)
    return _finish(bpy.context.active_object, mat, group, bevel, smooth=True)


def ring_of(n, radius, z, fn, phase=0.0):
    for i in range(n):
        a = phase + 2 * math.pi * i / n
        fn(a, Vector((radius * math.cos(a), radius * math.sin(a), z)))


def rivet(loc, r=0.016, mat="steel", group="static"):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=8, ring_count=5)
    o = bpy.context.active_object
    o.scale.z = 0.6
    return _finish(o, mat, group, bevel=0, smooth=True)


# 1. The service gutter: identical on all four sides, at the very footprint edge.
E = 1.475                     # lip face at 1.495: the plate must measure exactly 3 tiles
GW, GH = 0.2, 0.09
for side in range(4):
    rz = side * math.pi / 2
    c, s = math.cos(rz), math.sin(rz)
    def at(x, y, z):
        return (x * c - y * s, x * s + y * c, z)
    box(at(0, -E + 0.02, GH / 2), (2 * E, 0.04, GH), "skirt", rot_z=rz)          # outer lip
    box(at(0, -E + GW, GH / 2 + 0.01), (2 * E - 2 * GW + 0.04, 0.04, GH + 0.02), "skirt", rot_z=rz)
    box(at(0, -E + GW / 2, 0.012), (2 * E, GW, 0.024), "cast", rot_z=rz, bevel=0)  # channel floor
    for t in (-1, 0, 1):                          # a capped stub on every edge tile
        cyl(at(t, -E + GW / 2 + 0.03, 0.1), 0.1, GW + 0.04, "skirt",
            rot=(math.pi / 2, 0, rz), verts=24)
        cyl(at(t, -E + 0.045, 0.1), 0.135, 0.035, "copper",
            rot=(math.pi / 2, 0, rz), verts=24)
        ring_of(6, 0.1, 0, lambda a, p: rivet(at(t + p.x, -E + 0.02, 0.1 + p.y), 0.013, "brass"))
    for t in (-1.5 + 0.05, -0.5, 0.5):            # copper joint straps between tiles
        box(at(t, -E + GW / 2, GH + 0.005), (0.05, GW + 0.02, 0.02), "copper", rot_z=rz, bevel=0.004)
    for k in range(13):                           # bolts along the outer lip
        rivet(at(-E + 0.12 + k * (2 * E - 0.24) / 12, -E + 0.02, GH + 0.005), 0.014)

# 2. The skirt: low riveted plate off the gutter, hazard tape worn off the corners.
SK, SH = 1.26, 0.26
box((0, 0, SH / 2), (2 * SK, 2 * SK, SH), "skirt", bevel=0.03)
for side in range(4):
    rz = side * math.pi / 2
    c, s = math.cos(rz), math.sin(rz)
    for k in range(15):
        x = -SK + 0.1 + k * (2 * SK - 0.2) / 14
        rivet((x * c + SK * s * 1.0005, x * s - SK * c * 1.0005, SH - 0.04))
for cx in (-1, 1):
    for cy in (-1, 1):
        box((cx * SK * 1.002, cy * (SK - 0.11), SH / 2 + 0.03), (0.01, 0.2, 0.12), "hazard", bevel=0)
        box((cx * (SK - 0.11), cy * SK * 1.002, SH / 2 + 0.03), (0.2, 0.01, 0.12), "hazard", bevel=0)

# 3. The drum: squat, wider than tall, in three lead shield bands.
R, Z0, Z1 = 1.12, SH, 1.26
cyl((0, 0, (Z0 + Z1) / 2), R, Z1 - Z0, "shell", verts=96, bevel=0.02)
# the dished head: a riveted pressure-vessel top, not a flat lid. Vanilla's tops
# rise (the cryogenic plant's dome, the chemical plant's tanks); this one does it
# the way a real agitated batch reactor does.
HD = 0.34


def headz(r):
    return Z1 + HD * math.sqrt(max(0.0, 1 - (r / R) ** 2))


bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, Z1), segments=96, ring_count=48)
dome = bpy.context.active_object
dome.scale = (R, R, HD)
bpy.ops.object.transform_apply(scale=True)
_finish(dome, "shell", "static", bevel=0, smooth=True)
ring_of(48, R - 0.02, Z1 + 0.02, lambda a, p: rivet(p, 0.016))           # knuckle seam
ring_of(28, 0.72, headz(0.72) + 0.004, lambda a, p: rivet(p, 0.014))
for k in range(8):                                                     # meridian seams
    a = 2 * math.pi * k / 8 + math.pi / 8
    for j in range(4):
        rr = 0.36 + j * 0.16
        rivet((rr * math.cos(a), rr * math.sin(a), headz(rr) + 0.004), 0.013)
TOP = headz(0)
for k in range(12):                               # vertical plate seams
    a = 2 * math.pi * k / 12 + math.pi / 12
    for j in range(7):
        z = Z0 + 0.06 + j * (Z1 - Z0 - 0.12) / 6
        rivet((R * math.cos(a), R * math.sin(a), z))
for zb in (Z0 + 0.12, (Z0 + Z1) / 2, Z1 - 0.1):
    cyl((0, 0, zb), R + 0.03, 0.1, "lead", verts=96, bevel=0.01)
    ring_of(8, R + 0.06, zb, lambda a, p: box((p.x, p.y, p.z), (0.07, 0.13, 0.14), "copper",
                                             rot_z=a, bevel=0.012), phase=math.pi / 8)
    ring_of(8, R + 0.095, zb, lambda a, p: rivet((p.x, p.y, p.z), 0.022, "cast"),
            phase=math.pi / 8)

# sight slots, low on the near (south) shoulder, between the bottom two bands
ZS = (Z0 + 0.12 + (Z0 + Z1) / 2) / 2
for a_deg in (-106, -90, -74):
    a = math.radians(a_deg)
    p = Vector((R * math.cos(a), R * math.sin(a), ZS))
    box(p, (0.28, 0.08, 0.11), "cast", rot_z=a + math.pi / 2, bevel=0.01)
    q = Vector(((R + 0.043) * math.cos(a), (R + 0.043) * math.sin(a), ZS))
    box(q, (0.22, 0.004, 0.05), "slot", group="slots", rot_z=a + math.pi / 2, bevel=0)

# ladder up the east shoulder onto the head
for j in range(6):
    z = Z0 + 0.12 + j * 0.17
    box((R + 0.04, 0.55, z), (0.05, 0.03, 0.03), "cast", bevel=0.005)
    box((R + 0.04, 0.72, z), (0.05, 0.03, 0.03), "cast", bevel=0.005)
    box((R + 0.07, 0.635, z), (0.02, 0.2, 0.025), "cast", bevel=0.005)
for k in range(5):                                   # a short handrail at the ladder head
    a = math.radians(10 + k * 12)
    x, y = 0.9 * math.cos(a), 0.9 * math.sin(a)
    cyl((x, y, headz(0.9) + 0.1), 0.014, 0.2, "cast", verts=8, bevel=0)
    if k < 4:
        a2 = math.radians(16 + k * 12)
        box((0.9 * math.cos(a2), 0.9 * math.sin(a2), headz(0.9) + 0.2), (0.022, 0.2, 0.022), "brass",
            rot_z=a2, bevel=0.004)


def tube(pts, r, mat, clamps=False, group="static"):
    cu = bpy.data.curves.new("tube", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 4
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, co in zip(sp.bezier_points, pts):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    ob = bpy.data.objects.new("tube", cu)
    sc.collection.objects.link(ob)
    _finish(ob, mat, group, bevel=0)
    return ob


def bands_along(pts, r, n, mat):
    """Rings along a polyline, each square to its segment: corrugation, clamps."""
    segs = list(zip(pts, pts[1:]))
    total = sum((Vector(b) - Vector(a)).length for a, b in segs)
    for i in range(n):
        t = (i + 0.5) / n * total
        for a, b in segs:
            a, b = Vector(a), Vector(b)
            L = (b - a).length
            if t <= L:
                p = a + (b - a) * (t / L)
                q = (b - a).normalized().to_track_quat("Z", "Y").to_euler()
                cyl(tuple(p), r, 0.02, mat, verts=16, rot=tuple(q), bevel=0.004)
                break
            t -= L


# 4. The drive tower: a cast bearing column rising from the head, the free spider
# coupling on top of it with nothing above and a gap all round.
#
# Laid out in SCREEN space: through this camera a part at height z appears z/2
# tiles further up the screen, so everything on the head is placed south of where
# it should read. Placed at the true centre, the whole crown piled up in the
# northern half and left the head's front slope -- the part facing the player --
# blank.
TX, TY = 0.0, -0.22
tb = headz(math.hypot(TX, TY))
cyl((TX, TY, tb + 0.02), 0.34, 0.08, "cast", verts=48, bevel=0.015)           # base flange
ring_of(10, 0.3, 0, lambda a, p: rivet((TX + p.x, TY + p.y, tb + 0.065), 0.017))
TT = tb + 0.34
cyl((TX, TY, (tb + TT) / 2), 0.21, TT - tb, "cast", verts=48, bevel=0.02)      # column
for k in range(8):                                                            # cast ribs
    a = 2 * math.pi * k / 8
    box((TX + 0.22 * math.cos(a), TY + 0.22 * math.sin(a), (tb + TT) / 2 + 0.01),
        (0.08, 0.04, TT - tb - 0.04), "cast", rot_z=a, bevel=0.008)
cyl((TX, TY, TT + 0.025), 0.26, 0.05, "cast", verts=48, bevel=0.012)          # bearing cap
ring_of(8, 0.23, 0, lambda a, p: rivet((TX + p.x, TY + p.y, TT + 0.052), 0.015), phase=math.pi / 8)
CZ = TT + 0.13
cyl((TX, TY, CZ - 0.04), 0.07, 0.1, "brass", group="coupling", verts=24)        # shaft
cyl((TX, TY, CZ), 0.1, 0.1, "brass", group="coupling", verts=24)
for k in range(6):
    a = 2 * math.pi * k / 6
    box((TX + 0.16 * math.cos(a), TY + 0.16 * math.sin(a), CZ), (0.12, 0.07, 0.1), "copper",
        group="coupling", rot_z=a, bevel=0.014)
    rivet((TX + 0.2 * math.cos(a), TY + 0.2 * math.sin(a), CZ + 0.055), 0.017, group="coupling")
cyl((TX, TY, CZ + 0.06), 0.06, 0.03, "cast", group="coupling", verts=16)

# the motor: a finned drum on a steel saddle, driving the tower through the
# teal-guarded gearbox; the open gear train sits beside the guard (3.1)
MX, MY = -0.64, -0.1
MZ = headz(abs(MX)) + 0.22
for dx in (-0.14, 0.14):                                                      # saddle
    box((MX + dx, MY, (headz(abs(MX + dx)) + MZ) / 2 - 0.02), (0.05, 0.3, MZ - headz(abs(MX + dx)) + 0.02),
        "steel", bevel=0.008)
cyl((MX, MY, MZ), 0.16, 0.44, "cast", verts=48, rot=(0, math.pi / 2, 0), bevel=0.02)
for k in range(9):
    cyl((MX - 0.19 + k * 0.0475, MY, MZ), 0.18, 0.016, "cast", verts=48, rot=(0, math.pi / 2, 0), bevel=0.003)
cyl((MX - 0.24, MY, MZ), 0.12, 0.05, "steel", verts=32, rot=(0, math.pi / 2, 0), bevel=0.01)
box((MX, MY + 0.2, MZ + 0.02), (0.14, 0.08, 0.1), "cast", bevel=0.01)          # terminal box
GBZ = headz(0.34) + 0.14
box((-0.34, MY, GBZ), (0.2, 0.36, 0.3), "teal", bevel=0.03)                    # gearbox guard
ring_of(4, 0.14, 0, lambda a, p: rivet((-0.34 + p.x, MY + p.y, GBZ + 0.155), 0.014, "cast"),
        phase=math.pi / 4)


def gear(x, y, r, teeth, z):
    cyl((x, y, z), r, 0.05, "cast", verts=48, bevel=0.006)
    cyl((x, y, z + 0.035), r * 0.35, 0.03, "brass", verts=24, bevel=0.004)
    ring_of(teeth, r + 0.014, 0, lambda a, p: box((x + p.x, y + p.y, z), (0.032, 0.022, 0.05), "steel",
                                                 rot_z=a, bevel=0.004))


gz = headz(0.6) + 0.06
box((-0.45, 0.32, gz - 0.05), (0.44, 0.26, 0.07), "cast", bevel=0.012)
gear(-0.55, 0.32, 0.13, 18, gz)
gear(-0.33, 0.3, 0.07, 11, gz)

# nozzles on the head: a manway under the teal hatch, and the instrument nozzle
def nozzle(x, y, r, h):
    z0 = headz(math.hypot(x, y))
    cyl((x, y, z0 + h / 2 - 0.03), r, h + 0.06, "shell", verts=48, bevel=0.012)
    cyl((x, y, z0 + h), r + 0.05, 0.05, "copper", verts=48, bevel=0.012)
    ring_of(10, r + 0.025, 0, lambda a, p: rivet((x + p.x, y + p.y, z0 + h + 0.028), 0.014))
    return z0 + h + 0.025


HX, HY = 0.46, 0.3
zt = nozzle(HX, HY, 0.2, 0.14)
cyl((HX, HY, zt + 0.035), 0.24, 0.04, "teal", verts=48, bevel=0.012)        # hatch cover
cyl((HX - 0.23, HY, zt + 0.04), 0.025, 0.14, "cast", verts=12, rot=(math.pi / 2, 0, 0), bevel=0.004)
box((HX + 0.22, HY, zt + 0.07), (0.04, 0.12, 0.03), "brass", bevel=0.005)          # handle
zi = nozzle(0.58, -0.5, 0.12, 0.1)
box((0.58, -0.5, zi + 0.12), (0.3, 0.06, 0.22), "cast", bevel=0.012)          # gauge panel
for dx in (-0.08, 0.08):
    cyl((0.58 + dx, -0.535, zi + 0.14), 0.055, 0.03, "brass", verts=24, rot=(math.pi / 2, 0, 0), bevel=0.004)
    cyl((0.58 + dx, -0.55, zi + 0.14), 0.045, 0.004, "gauge", verts=24, rot=(math.pi / 2, 0, 0), bevel=0)

# a stiffener ring round the head, and a grated walkway with a handrail on the
# south-west of the front slope -- the face the player actually looks at
bpy.ops.mesh.primitive_torus_add(major_radius=0.86, minor_radius=0.03, location=(0, 0, headz(0.86) + 0.01),
                                 major_segments=96, minor_segments=12)
_finish(bpy.context.active_object, "cast", "static", bevel=0, smooth=True)
for k in range(9):
    a = math.radians(200 + k * 8)
    x0, y0 = 0.72 * math.cos(a), 0.72 * math.sin(a)
    x1, y1 = 1.02 * math.cos(a), 1.02 * math.sin(a)
    zm = (headz(0.72) + headz(1.02)) / 2 + 0.03
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, zm),
                                    rotation=(0, math.atan2(headz(0.72) - headz(1.02), 0.3), a))
    o = bpy.context.active_object
    o.scale = (0.32, 0.016, 0.02)
    bpy.ops.object.transform_apply(scale=True)
    _finish(o, "lead", "static", bevel=0.003)
for k in range(5):                                   # rail posts on the outer edge, and the rail
    a = math.radians(200 + k * 16)
    cyl((1.04 * math.cos(a), 1.04 * math.sin(a), headz(1.04) + 0.1), 0.013, 0.2, "cast", verts=8, bevel=0)
rail = [(1.04 * math.cos(math.radians(a)), 1.04 * math.sin(math.radians(a)), headz(1.04) + 0.2)
        for a in range(200, 265, 8)]
tube(rail, 0.012, "brass")

# a steel line wrapping the south-east of the front slope into the instrument nozzle
arc = [(0.8 * math.cos(math.radians(a)), 0.8 * math.sin(math.radians(a)), headz(0.8) + 0.06)
       for a in range(280, 336, 8)]
tube(arc + [(0.62, -0.42, headz(0.75) + 0.08)], 0.045, "steel")
bands_along(arc, 0.06, 4, "cast")

# the process line off the instrument nozzle, over the shoulder to the skirt
pl = [(0.7, -0.5, zi - 0.02), (0.96, -0.5, headz(0.98) + 0.05), (R + 0.1, -0.5, 1.0),
      (R + 0.1, -0.52, SH + 0.1)]
tube(pl, 0.06, "steel")
bands_along(pl, 0.08, 4, "cast")
cyl((R + 0.1, -0.52, SH + 0.03), 0.1, 0.05, "copper", verts=24, bevel=0.008)

# the motor's feed: a corrugated hose from the terminal box down the west side
hose = [(MX, MY + 0.26, MZ), (-0.95, 0.5, headz(0.95) + 0.06), (-R - 0.08, 0.5, 0.9),
        (-R - 0.08, 0.5, SH + 0.08)]
tube(hose, 0.045, "cast")
bands_along(hose, 0.055, 22, "cast")

# the status lamp on a post at the west rim: clear of the alt-mode icon, which the
# engine draws over the middle of the machine (vanilla's assembler puts it ~0.94
# tiles off-centre for the same reason)
LX, LY = -0.94, -0.28
lz = headz(math.hypot(LX, LY))
cyl((LX, LY, lz + 0.09), 0.025, 0.18, "steel", verts=12, bevel=0.004)
cyl((LX, LY, lz + 0.19), 0.075, 0.05, "cast", verts=24, bevel=0.01)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(LX, LY, lz + 0.23), segments=16, ring_count=8)
_finish(bpy.context.active_object, "lens", "lamp", bevel=0, smooth=True)

# ---------------------------------------------------------------- passes

rig.sun()
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()

ALL = [o for objs in PARTS.values() for o in objs]


def setup(visible=(), catchers=(), holdouts=(), ground=False):
    """Per pass: which groups the camera sees, catch shadow on, or cut out."""
    for g, objs in PARTS.items():
        for o in objs:
            o.hide_render = g not in visible and g not in catchers and g not in holdouts
            o.is_shadow_catcher = g in catchers
            o.is_holdout = g in holdouts
            o.visible_camera = True
    GROUND.hide_render = not ground
    BOUNCE.hide_render = ground              # never under the shadow catcher


# Slot emission. Through the contrast look anything much above this clips the
# slots to white and the glow layer loses its green: at 3.0 the core was #FFFFFF,
# at 1.2 it is #C2FFDF, inside the spec's #A8E8C0 -> #E8FFF0 (measured 2026-10-01).
GLOW = 1.2


def glow(on):
    M["slot"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = \
        GLOW if on else 0.0


STATIC = ("static", "slots", "lamp")

# ---------------------------------------------------------------- ports
#
# The engine draws a pipe_picture at every live port and a pipe_cover over every
# unconnected one; vanilla's assembler-2 fitting did not belong on this plate
# (blue paint, polished brass, a different size from the gutter). These are the
# plant's own, built on the middle tile of each face and rendered alone.
#
# Sized and placed to meet a vanilla pipe, which fills the outside tile right up
# to the boundary: the fitting itself stays inside the footprint. Vanilla's pipe
# is ~0.72 tiles thick, pale steel, and on screen its centreline sits ~0.05
# tiles below the tile centre (assembler-2's E/W fittings, and the pipe sheets).

PR = 0.35            # stub radius: a vanilla pipe, give or take a pixel
FR = 0.42            # flange radius: 0.84 tiles, the chemical plant's port width
AXZ = 0.25           # stub axis height
NS_LAT = 0.031       # vanilla's N-S pipe is centred +2.0 px (of 64) right of its tile
EW_LAT = -0.193      # E/W stubs sit south of the tile centre so, through this camera,
                     # their centreline lands on a vanilla pipe's (+5.5 px below centre).
                     # Both are medians over the whole pipe sprite, not one row.


def port(d):
    """Fitting and blind cap for the port on face d (N, E, S, W)."""
    g, c = f"port-{d}", f"cover-{d}"
    ax = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}[d]
    rot = (math.pi / 2, 0, 0) if ax[0] == 0 else (0, math.pi / 2, 0)
    lat0 = NS_LAT if ax[0] == 0 else EW_LAT

    def at(t, lat=0.0, z=AXZ):
        # t: distance out from the entity centre; lat: along the face
        if ax[0] == 0:
            return (lat0 + lat, ax[1] * t, z)
        return (ax[0] * t, lat0 + lat, z)
    # collar plate on the skirt face, bolted
    cyl(at(SK + 0.02), FR, 0.05, "skirt", group=g, verts=48, rot=rot, bevel=0.012)
    ring_of(8, FR - 0.05, 0, lambda a, p: rivet(at(SK + 0.05, p.x, AXZ + p.y), 0.02, group=g),
            phase=math.pi / 8)
    # steel stub across the gutter, and the copper flange a pipe meets, at the boundary
    cyl(at((SK + 1.5) / 2), PR, 1.5 - SK, "steel", group=g, verts=48, rot=rot, bevel=0.01)
    cyl(at(1.5 - 0.035), FR, 0.06, "copper", group=g, verts=48, rot=rot, bevel=0.012)
    ring_of(8, FR - 0.05, 0, lambda a, p: rivet(at(1.5 - 0.004, p.x, AXZ + p.y), 0.02, group=g),
            phase=math.pi / 8)
    # blind cap, just past the boundary: drawn only over an unconnected port
    cyl(at(1.5 + 0.02), FR - 0.02, 0.04, "cast", group=c, verts=48, rot=rot, bevel=0.012)
    cyl(at(1.5 + 0.05), 0.11, 0.03, "steel", group=c, verts=24, rot=rot, bevel=0.008)
    ring_of(8, FR - 0.09, 0, lambda a, p: rivet(at(1.5 + 0.045, p.x, AXZ + p.y), 0.02, group=c),
            phase=math.pi / 8)


if PORTS:
    for d in "NESW":
        port(d)
    body = ("static", "slots", "lamp", "coupling")
    rig.camera(320, 320)                          # entity origin at (160, 160)
    for d in "NESW":
        # north is drawn behind the machine by the engine, so it renders whole;
        # the others sit in front and let the body occlude them and catch their shadow
        catch = () if d == "N" else body
        setup(visible=(f"port-{d}",), catchers=catch)
        rig.render(f"{OUT_DIR}/port-{d}.png")
        setup(visible=(f"cover-{d}",), catchers=catch + (f"port-{d}",))
        rig.render(f"{OUT_DIR}/cover-{d}.png")
    sys.exit(0)

if ICON:
    sc.cycles.samples = 128
    cam = rig.camera(1024, 1024, centre_px=(512, 560), ss=1)
    cam.data.ortho_scale = 3.5
    setup(visible=STATIC + ("coupling",))
    glow(True)
    rig.render(f"{OUT_DIR}/icon.png")
    sys.exit(0)

W = H = 256
rig.camera(W, H)                                  # entity origin at (128, 128)

setup(visible=STATIC)
glow(False)
rig.render(f"{OUT_DIR}/idle.png")
if IDLE:
    glow(True)
    rig.render(f"{OUT_DIR}/working.png")
    sys.exit(0)
# the stopped machine in one render, coupling at frame 0 and casting on the head:
# what pack.py holds idle + coupling-00 to, since the spec wants frame 0 to be
# the plate
setup(visible=STATIC + ("coupling",))
rig.render(f"{OUT_DIR}/still.png")
setup(visible=STATIC)
glow(True)
rig.render(f"{OUT_DIR}/working.png")
glow(False)

# shadow: the whole machine casts, the camera sees only the ground catcher
setup(visible=STATIC + ("coupling",), ground=True)
for o in ALL:
    o.visible_camera = False
rig.render(f"{OUT_DIR}/shadow.png")

# status lamp: the lens alone, white, with everything in front of it cut out
setup(visible=("lamp",), holdouts=("static", "coupling"))
M["lens"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.0
M["lens"].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1)
rig.render(f"{OUT_DIR}/lamp.png")

# coupling: 12 frames through 60 degrees (six-fold symmetry), with its own shadow
# caught on the static machine beneath it
setup(visible=("coupling",), catchers=("static", "slots", "lamp"))
pivot = bpy.data.objects.new("pivot", None)
sc.collection.objects.link(pivot)
pivot.parent = ROOT
# on the tower's own shaft: the tower sits south of the drum's centre (TY), and a
# pivot at the origin swung the coupling round the head instead of turning it
pivot.location = (TX, TY, 0)
for o in PARTS["coupling"]:
    o.parent = pivot
    o.location.x -= TX
    o.location.y -= TY
# only the crown changes between frames, so render just that window
sc.render.use_border = True
sc.render.use_crop_to_border = False
sc.render.border_min_x, sc.render.border_max_x = 0.36, 0.64
sc.render.border_min_y, sc.render.border_max_y = 0.58, 0.9
for f in range(12):
    pivot.rotation_euler.z = -math.radians(5 * f)
    rig.render(f"{OUT_DIR}/coupling-{f:02d}.png")
