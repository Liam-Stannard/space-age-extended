"""Vacuum furnace (sae-vacuum-furnace), built from its spec, rendered in every pass.

  blender -b --python vacuum_furnace.py -- <out-dir> [--idle | --icon | --ports]
  tools/blender/render.sh concept/vacuum-furnace/model/vacuum_furnace.py <out-dir> [--icon]

  --idle   idle.png and working.png only: the quick loop
  --ports  the four pipe pictures, port-<face>.png, rendered alone on the port canvas;
           pipe_pictures.py (beside this file) cuts them to assembler 3's sheets. Not
           through render.sh --ports: pack_ports.py packs a rendered cover with every
           fitting, and this building's covers are vanilla's (spec 8)

The layout is blockout revision 4, approved by Liam 2026-10-07
(blockout-v4.png, vacuum_furnace_blockout_v4.py); the finish is the first finished
model's (materials.py's layered finish through this building's concept swatches).
Spec: concept/vacuum-furnace/building-spec-vacuum-furnace.md -- 3.2 the parts, 3.3
the palette, 5 four directions and a building that never turns, 6 what moves,
8 the input.

  - a battered octagonal hull filling the footprint: its walls lean back 0.22 over
    1.2, so at the middle of each face the wall reaches the top of the pipe
    picture's plate (0.688 tiles below the origin on screen for the south one);
  - the welded drum (R 1.08), round and on the footprint's centre, its deck level
    with the hull's rail, so the parapet runs round the hatch evenly;
  - the hatch flat in the roof, with its eight dogs; no dome and no lifting eye;
  - the sight port at the hatch's centre, its glass flat in the roof: the only heat
    glow, and the indicator -- its glass, cut white, is the light pass the engine
    tints by status (spec 3.2); there is no separate lamp;
  - three radiator stacks across the corners, in niches cut into the hull;
  - the vacuum pump in the south-east niche: a barrel, a heavy flywheel upright in
    front of it on its drive motor's shaft (the animation: 16 frames through 60 degrees, its six-fold
    symmetry), free all round, and a vacuum gauge flat on the barrel's head, its dull
    dial recessed in a hood and bare -- the needle is Animatorio's (spec 6);
  - a copper ring on the deck round the hatch, with feeders down the diagonals to
    the three stacks, none crossing a face's middle;
  - no base and no socket: the input is the engine's pipe picture, rendered here
    to assembler 3's outline exactly (a backing slab traced from its pixels), in
    the furnace's metal, and vanilla's cover;
  - no frost anywhere (Liam, 2026-10-02).

Roof and clamps: the roof warmed toward the adopted plate's beige (#958577) and the
dogs bronze, as spec 3.3 has them.

Units are tiles; north is +Y. A model point (x, y, z) lands on screen at
(x, y + z/2) tiles from the origin.
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


def swatch(name):
    """This building's concept swatches: swatches/bake_concept.py."""
    return os.path.join(HERE, "swatches", f"concept_{name}.png")


import rig  # noqa: E402
import contract  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = argv[0]
os.makedirs(OUT_DIR, exist_ok=True)
ICON = "--icon" in argv
IDLE = "--idle" in argv
PORTS = "--ports" in argv

FACES = "NESW"
CANVAS = (320, 288)                   # entity origin at (160, 144); the shadow reaches east
PORT_CANVAS = (320, 320)              # the pictures reach a tile outside on every side
DECL = dict(
    footprint=(3, 3),
    directions="one",                 # drawn once; only the input turns (spec 5)
    passes=[
        dict(name="idle", kind="plate", sheet="base"),
        dict(name="still", kind="still"),
        dict(name="working", kind="glow", over="idle", sheet="port-glow"),
        dict(name="shadow", kind="shadow", sheet="base-shadow"),
        dict(name="indicator", kind="light", sheet="viewport-status"),
    ],
    # spec 6: the flywheel turns while working; six spokes, so 60 degrees is a loop
    animations=[dict(name="flywheel", frames=16, motion="turn")],
    # the one input, {0, 1} facing south at rest, and where the engine turns it
    ports=[dict(tile=(0, -1), face="N"), dict(tile=(1, 0), face="E"),
           dict(tile=(0, 1), face="S"), dict(tile=(-1, 0), face="W")],
)

sc = rig.reset()
ROOT = rig.turntable(rig.stretch_root())

# ---------------------------------------------------------------- materials

from materials import layered  # noqa: E402

M = {
    # spec 3.3, each through the concept's own swatch (recentred on the 3.3 hex)
    "drum":     layered("drum", "#5E584E", paint_metal=0.0, paint_rough=0.65, wear=0.45, rust=0.35,
                        dust=0.2, swatch=swatch("drum")),
    "hull":     layered("hull", "#3E3B36", paint_metal=0.0, paint_rough=0.7, wear=0.5, rust=0.4,
                        dust=0.3, swatch=swatch("plinth")),
    "radiator": layered("radiator", "#6E685C", metal="#9A9488", paint_metal=0.3, paint_rough=0.45,
                        wear=0.4, rust=0.3, dust=0.15, swatch=swatch("radiator")),
    "seam":     layered("seam", "#7A7268", metal="#A49C90", paint_metal=0.7, paint_rough=0.4,
                        wear=0.3, rust=0.2, dust=0.0, jitter=0.04),
    "steel":    layered("steel", "#77716A", metal="#B4AEA4", paint_metal=0.8, paint_rough=0.35,
                        wear=0.45, rust=0.25, dust=0.1, grime=0.5),
    "rail":     layered("rail", "#77716A", metal="#B4AEA4", paint_metal=0.8, paint_rough=0.35,
                        wear=0.45, rust=0.25, dust=0.1, grime=0.5),
    "copper":   layered("copper", "#94592C", metal="#C08452", paint_metal=0.9, paint_rough=0.38,
                        wear=0.4, rust=0.1, dust=0.15, grime=0.5, swatch=swatch("copper")),
    "brass":    layered("brass", "#9C7034", metal="#C49C5C", paint_metal=0.9, paint_rough=0.38,
                        wear=0.4, rust=0.15, dust=0.15, swatch=swatch("brass")),
}
# the roof warmed toward the adopted plate's beige and the dogs bronze (spec 3.3)
M["hatch"] = layered("hatch", "#958577", metal="#B8B0A4", paint_metal=0.25, paint_rough=0.6,
                     wear=0.35, rust=0.2, dust=1.0, grime=0.9, swatch=swatch("hatch_warm"))
M["dog"] = M["copper"]
M["hinge"] = M["brass"]
# the gauge's dial: dull, so it never reads as a second light (spec 3.3)
# the flywheel: bare steel, darker than the fittings so it never glares in the niche
M["wheel"] = layered("wheel", "#55504A", metal="#9A948C", paint_metal=0.8, paint_rough=0.4,
                     wear=0.5, rust=0.3, dust=0.1, grime=0.6)
# its rim turned bright, as a flywheel's machined rim is, so the ellipse reads at 1x
# and the dark spokes move against it (Liam, 2026-10-08)
M["rim"] = layered("rim", "#9A948C", metal="#D2CCC2", paint_metal=1.0, paint_rough=0.28,
                   wear=0.15, rust=0.08, dust=0.05, grime=0.25)
M["dial"] = layered("dial", "#8E877B", paint_metal=0.0, paint_rough=0.75, wear=0.15, rust=0.05,
                    dust=0.4, grime=0.6)


VIEW_R = 0.145                         # the porthole glass


def port_material():
    """The porthole glass: dark tinted glass when idle; working, filled with light,
    #FFD9A0 at the centre to #E8A24A at the rim (spec 3.3), by the distance from the
    glass's own centre."""
    m = bpy.data.materials.new("port")
    m.use_nodes = True
    t = m.node_tree
    b = t.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#2B2E33")         # dark glass (spec 3.3)
    b.inputs["Roughness"].default_value = 0.06
    b.inputs["Coat Weight"].default_value = 1.0                         # a glassy sheen when idle
    b.inputs["Coat Roughness"].default_value = 0.03
    co = t.nodes.new("ShaderNodeTexCoord")
    ln = t.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    t.links.new(co.outputs["Object"], ln.inputs[0])
    ramp = t.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = rig.srgb("#FFD9A0")
    ramp.color_ramp.elements[1].color = rig.srgb("#E8A24A")
    rng = t.nodes.new("ShaderNodeMapRange")
    rng.inputs["From Max"].default_value = VIEW_R
    t.links.new(ln.outputs["Value"], rng.inputs["Value"])
    t.links.new(rng.outputs[0], ramp.inputs["Fac"])
    t.links.new(ramp.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 0.0
    return m


M["port"] = port_material()

# ---------------------------------------------------------------- geometry

PARTS = {}          # group name -> [objects]; the passes toggle whole groups


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
    obj.parent = parent or ROOT
    PARTS.setdefault(group, []).append(obj)
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


def loft(lo, hi, z0, z1, mat, group="static", bevel=0.02):
    """A slab from outline `lo` at z0 to outline `hi` at z1 (same point count)."""
    def build(bm):
        a = [bm.verts.new((x, y, z0)) for x, y in lo]
        b = [bm.verts.new((x, y, z1)) for x, y in hi]
        bm.faces.new(list(reversed(a)))
        bm.faces.new(b)
        for i in range(len(lo)):
            j = (i + 1) % len(lo)
            bm.faces.new((a[i], a[j], b[j], b[i]))
    return mesh_object("loft", build, mat, group, bevel)


def prism(points, z0, z1, mat, group="static", bevel=0.015):
    return loft(points, points, z0, z1, mat, group, bevel)


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


def tube(pts, r, mat, group="static", parent=None):
    cu = bpy.data.curves.new("tube", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, co in zip(sp.bezier_points, pts):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    ob = bpy.data.objects.new("tube", cu)
    sc.collection.objects.link(ob)
    return _finish(ob, mat, group, bevel=0, parent=parent)


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    e.parent = parent or ROOT
    e.location, e.rotation_euler, e.scale = loc, rot, scale
    return e


# A face that lands on screen as a circle: tilted back 53.13 degrees, normal (0, -0.8, 0.6).
TILT = (math.atan2(0.8, 0.6), 0, 0)

# 1. The hull: battered, octagonal, filling the footprint; its face middles stand on
# the footprint edge, its corners cut into niches for the stacks.
HZ, E, C, LEAN = 1.2, 1.482, 0.9, 0.22     # the foot band, 0.01 proud, lands at 1.492
CT = C - LEAN * (2 - math.sqrt(2))     # the chamfer leans back by LEAN too, square to it


def octagon(e, c):
    return [(-e, -e + c), (-e + c, -e), (e - c, -e), (e, -e + c), (e, e - c), (e - c, e), (-e + c, e), (-e, e - c)]


def at_lean(z):
    """The hull's half-width, and chamfer, at height z."""
    f = z / HZ
    return E - LEAN * f, C + (CT - C) * f


# An open shell: the battered walls, 0.06 thick, with no lid -- the drum stands inside
# them on a deck (below), and its front wall comes through the south face.
def build_walls(bm, lo=octagon(E, C), hi=octagon(E - LEAN, CT)):
    a = [bm.verts.new((x, y, 0.0)) for x, y in lo]
    b = [bm.verts.new((x, y, HZ)) for x, y in hi]
    for i in range(len(lo)):
        j = (i + 1) % len(lo)
        bm.faces.new((a[i], a[j], b[j], b[i]))


walls = mesh_object("hull", build_walls, "hull", "hull", bevel=0.0)
sol = walls.modifiers.new("solid", "SOLIDIFY")
sol.thickness = 0.06
sol.offset = -1.0                                # inward: the outside is the approved hull
for z0, z1 in ((0.0, 0.07), (0.56, 0.6)):                         # a foot band and a girth weld
    e0, c0 = at_lean(z0)
    e1, c1 = at_lean(z1)
    loft(octagon(e0 + 0.01, c0), octagon(e1 + 0.01, c1), z0, z1, "seam", group="hull", bevel=0.004)
ER, CR = at_lean(HZ)
def octagon_ring(outer, inner, z0, z1, mat, group):
    """A slab between two octagons: the cap rail round the shell's open top."""
    def build(bm):
        rows = [[bm.verts.new((x, y, z)) for x, y in pts] for pts, z in
                ((outer, z0), (outer, z1), (inner, z1), (inner, z0))]
        n = len(outer)
        for k in range(4):
            r0, r1 = rows[k], rows[(k + 1) % 4]
            for i in range(n):
                j = (i + 1) % n
                bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    return mesh_object("rail", build, mat, group, bevel=0.012)


octagon_ring(octagon(ER + 0.01, CR), octagon(ER - 0.1, CR - 0.04), HZ - 0.01, HZ + 0.05, "rail", "hull")
PZ = HZ + 0.05
# rivets along the cap rail's corner runs, clear of every face's middle
for sx in (-1, 1):
    for sy in (-1, 1):
        for f in (0.2, 0.5, 0.8):
            x = ER - CR * (1 - f) - 0.03
            y = ER - CR * f - 0.03
            rivet((sx * x, sy * y, PZ + 0.003), 0.014)

# 2. The drum: one welded piece, raised on the hull, round and on the footprint's
# centre, its deck level with the top of the hull's rail, which runs round it as an
# even parapet (blockout revision 4, Liam 2026-10-07).
YC, K, R, H = 0.0, 1.0, 0.89, PZ
RD = 1.08                                   # the drum wall; the hatch keeps R
BODY = empty("body", loc=(0, YC, 0), scale=(1, K, 1))


def on_body(a, r, z):
    return (r * math.cos(a), r * math.sin(a), z)


cyl((0, 0, H / 2), RD, H, "drum", verts=128, bevel=0.02, parent=BODY)
torus((0, 0, 0.55), RD + 0.002, 0.011, "seam", parent=BODY, seg=128)                       # girth weld
# the deck inside the hull's walls, level with the drum's top
ED, CD = at_lean(H)
deck = prism(octagon(ED - 0.05, CD), 0.0, H - 0.012, "hull", group="hull", bevel=0.0)
# Where the drum comes through, the hull gives way to it: its walls, rail and deck are
# cut by the drum's own shape (a hidden cutter), so nothing of the hull crosses the roof.
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=RD + 0.004, depth=4.0, location=(0, 0, 0))
CUTTER = bpy.context.active_object
CUTTER.parent = BODY
CUTTER.hide_render = True
CUTTER.display_type = "WIRE"
for o in PARTS["hull"]:
    if o.name.startswith(("hull", "rail")) or o is deck:
        b = o.modifiers.new("drum", "BOOLEAN")
        b.operation = "DIFFERENCE"
        b.object = CUTTER
        b.solver = "EXACT"
for k in range(6):                                                                          # long welds
    a = math.radians(-60 + k * 60)
    box(on_body(a, RD + 0.002, (0.1 + H - 0.04) / 2), (0.014, 0.022, H - 0.04 - 0.1), "seam",
        rot=(0, 0, a), bevel=0.004, parent=BODY)
torus((0, 0, H - 0.005), RD - 0.005, 0.016, "seam", parent=BODY, seg=128)                  # deck edge

# the roof: flange ring and the hatch, flat in the roof (spec 3.2), with its groove
# rings; the viewport (5.) takes the middle
cyl((0, 0, H + 0.02), R + 0.03, 0.06, "hatch", verts=128, bevel=0.015, parent=BODY)
cyl((0, 0, H + 0.07), R - 0.04, 0.05, "hatch", verts=128, bevel=0.012, parent=BODY)
DOME_R, DOME_H, DZ = R - 0.11, 0.03, H + 0.09
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, DZ), segments=128, ring_count=48)
dome = bpy.context.active_object
dome.scale = (DOME_R, DOME_R, DOME_H)
bpy.ops.object.transform_apply(scale=True)
_finish(dome, "hatch", "static", bevel=0, smooth=True, parent=BODY)


def domez(r):
    return DZ + DOME_H * math.sqrt(max(0.0, 1 - (r / DOME_R) ** 2))


torus((0, 0, H + 0.096), R - 0.035, 0.012, "hull", parent=BODY, seg=128)            # flange gap
torus((0, 0, domez(0.62) - 0.004), 0.62, 0.014, "hull", parent=BODY, seg=128)       # groove
torus((0, 0, domez(0.66) + 0.002), 0.66, 0.012, "hatch", parent=BODY, seg=128)
torus((0, 0, DZ + 0.004), DOME_R - 0.01, 0.018, "hatch", parent=BODY, seg=128)
TOPZ = domez(0)
# 3. The radial dogs: one every eighth of a turn.
for k in range(8):
    a = math.radians(k * 45)
    box(on_body(a, 0.84, H + 0.13), (0.32, 0.17, 0.11), "dog", rot=(0, 0, a), bevel=0.018, parent=BODY)
    box(on_body(a, 0.97, H + 0.0), (0.09, 0.2, 0.3), "dog", rot=(0, 0, a), bevel=0.015, parent=BODY)
    box(on_body(a, 0.7, H + 0.16), (0.09, 0.21, 0.13), "hinge", rot=(0, 0, a), bevel=0.015, parent=BODY)
    rivet(on_body(a, 0.86, H + 0.195), 0.024, "steel", parent=BODY)
    rivet(on_body(a, 0.7, H + 0.23), 0.02, "steel", parent=BODY)

# 4. (there is no fault lamp: the viewport is the indicator, spec 3.2)
# 5. The sight port: at the hatch's centre, a raised boss carrying a heavy bolted ring
# and thick glass, set flat in the roof so it reads at the roof's angle (Liam,
# 2026-10-07). Dark glass when idle; working, the glass fills with orange light, the
# building's only glow; and its glass, cut white, is the indicator's light pass.
vx, vy = 0.0, YC
vz = domez(0)
cyl((vx, vy, vz - 0.04), 0.25, 0.12, "hatch", verts=64, bevel=0.02)                # the boss's skirt, on the dome
cyl((vx, vy, vz + 0.025), 0.265, 0.02, "steel", verts=64, bevel=0.006)              # its collar
# the head sits on the skirt, flat, its glass level with the roof
VP = empty("viewport", loc=(vx, vy, vz + 0.12))
cyl((0, 0, -0.14), 0.24, 0.22, "hatch", verts=64, bevel=0.015, parent=VP)           # the boss's face block
ring((0, 0, 0.0), 0.26, VIEW_R + 0.01, 0.07, "steel", parent=VP, bevel=0.015)       # heavy bolted ring
for k in range(10):
    t = 2 * math.pi * k / 10 + math.pi / 10
    rivet((0.21 * math.cos(t), 0.21 * math.sin(t), 0.04), 0.02, parent=VP)
ring((0, 0, 0.01), VIEW_R + 0.03, VIEW_R + 0.006, 0.06, "hull", parent=VP, bevel=0.008)   # glass bezel
cyl((0, 0, -0.035), VIEW_R + 0.008, 0.05, "port", group="port", verts=64, bevel=0.0, parent=VP)  # thick glass

# 6. The radiator stacks: one in each corner niche but the south-east, across the diagonal, on legs,
# bracketed back to the hull's chamfer.
SZ = 0.55
STACKS = []
for cx in (-1, 1):
    for cy in (-1, 1):
        if (cx, cy) == (1, -1):
            continue                              # the south-east niche is the pump's (6b.)
        d = math.atan2(cy, cx)
        px, py = cx * 1.12, cy * 1.12
        t = d + math.pi / 2                       # the stack's axis, across the diagonal
        rot = (math.pi / 2, 0, t + math.pi / 2)
        STACKS.append((cx, cy, px, py, d))
        cyl((px, py, SZ), 0.1, 0.5, "radiator", verts=24, rot=rot, bevel=0.006)
        for i in range(12):
            s = -0.22 + i * 0.44 / 11
            cyl((px + s * math.cos(t), py + s * math.sin(t), SZ), 0.15, 0.022, "radiator",
                verts=40, rot=rot, bevel=0.005)
        for s in (-0.27, 0.27):                   # end plates on steel legs
            fx, fy = px + s * math.cos(t), py + s * math.sin(t)
            box((fx, fy, SZ - 0.04), (0.05, 0.36, 0.38), "radiator", rot=(0, 0, t + math.pi / 2), bevel=0.012)
            box((fx, fy, (SZ - 0.22) / 2), (0.06, 0.06, SZ - 0.22), "steel", bevel=0.008)
        for zb in (SZ - 0.12, SZ + 0.12):          # brackets back to the hull's chamfer
            box((px - 0.2 * math.cos(d), py - 0.2 * math.sin(d), zb), (0.26, 0.05, 0.05), "steel",
                rot=(0, 0, d), bevel=0.008)
        box((px, py, SZ + 0.2), (0.12, 0.12, 0.06), "copper", bevel=0.01)     # header, where the feeder lands
        if cy > 0:                                # the lifting lugs, on the hull's back corners
            lx, ly = cx * 0.84, 0.84
            box((lx, ly, PZ + 0.04), (0.14, 0.14, 0.08), "brass", bevel=0.012)
            lug = empty("lug", loc=(lx, ly - 0.02, PZ + 0.18), rot=TILT)
            box((0, -0.07, 0), (0.18, 0.14, 0.06), "steel", bevel=0.014, parent=lug)
            torus((0, 0.03, 0), 0.075, 0.035, "steel", parent=lug, seg=32)

# 6b. The vacuum pump, in the south-east niche (the corner triangle outside the
# hull's chamfer), as blockout revision 4 has it. A barrel in the hull's paint stands
# at the back of the niche on a foot; its suction line runs into the chamfer.
BX, BY, BR, BH = 1.24, -1.06, 0.17, 0.62
box((BX, BY, 0.035), (0.32, 0.32, 0.07), "steel", rot=(0, 0, math.radians(45)), bevel=0.012)  # foot: its corner at x 1.47, inside the footprint
for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    rivet((BX + 0.1 * (sx - sy) * 0.707, BY + 0.1 * (sx + sy) * 0.707, 0.072), 0.016)
cyl((BX, BY, 0.07 + BH / 2), BR, BH, "hull", verts=48, bevel=0.012)                          # barrel
cyl((BX, BY, 0.07 + BH + 0.025), BR + 0.025, 0.05, "steel", verts=48, bevel=0.01)          # its head
for k in range(8):
    a = 2 * math.pi * k / 8
    rivet((BX + (BR + 0.012) * math.cos(a), BY + (BR + 0.012) * math.sin(a), 0.07 + BH + 0.052), 0.012)
for zr in (0.22, 0.52):
    torus((BX, BY, zr), BR + 0.006, 0.015, "seam", seg=48)                                 # barrel bands
SUCK = empty("suction", loc=(BX - 0.2, BY + 0.2, 0.5), rot=(0, math.pi / 2, math.radians(135)))
cyl((0, 0, 0), 0.055, 0.26, "steel", verts=24, parent=SUCK)                                 # suction line
ring((0, 0, -0.1), 0.075, 0.05, 0.03, "steel", parent=SUCK, verts=24)                        # its flange
# The flywheel (spec 6): upright on a level north-south shaft in front of the
# barrel, facing south, so it draws as an ellipse half as tall as it is wide, at the
# camera's angle like the rest of the machine (Liam, 2026-10-08: a wheel facing the
# camera head-on looked pasted on). Heavy: a deep flat-faced rim, where a flywheel
# keeps its mass, and six short thick spokes. Free all round -- nothing touches its
# rim; behind it the shaft runs north into its drive motor, butted against the
# barrel. Its own group: the plate leaves it out and the frames draw it.
WX, WY, WZ, WR = 1.0, -1.32, 0.3, 0.26
HUB = 0.065
WHEEL_AXIS = empty("wheel-axis", loc=(WX, WY, WZ), rot=(math.pi / 2, 0, 0))   # local Z points south
WHEEL = empty("wheel", parent=WHEEL_AXIS)            # spins about its local Z, the shaft
cyl((0, 0, -0.1), 0.03, 0.14, "steel", verts=24, bevel=0.0, parent=WHEEL_AXIS)            # shaft
cyl((0, 0, -0.26), 0.1, 0.18, "hull", verts=32, bevel=0.012, parent=WHEEL_AXIS)            # drive motor
ring((0, 0, -0.17), 0.105, 0.04, 0.02, "steel", parent=WHEEL_AXIS, verts=32)               # its end plate
for k in range(4):
    t = 2 * math.pi * k / 4 + math.pi / 4
    rivet((0.078 * math.cos(t), 0.078 * math.sin(t), -0.158), 0.012, parent=WHEEL_AXIS)
box((0, -0.2, -0.26), (0.16, 0.2, 0.16), "steel", bevel=0.008, parent=WHEEL_AXIS)         # motor pedestal, to the ground
ring((0, 0, 0), WR, WR - 0.065, 0.085, "rim", group="flywheel", parent=WHEEL, verts=64)    # rim, machined bright
for k in range(6):                                                                         # spokes
    a = 2 * math.pi * k / 6
    L = WR - 0.06 - HUB + 0.02
    rr = HUB - 0.01 + L / 2
    box((rr * math.cos(a), rr * math.sin(a), 0), (L, 0.05, 0.045), "wheel", group="flywheel",
        rot=(0, 0, a), bevel=0.008, parent=WHEEL)
cyl((0, 0, 0), HUB, 0.1, "wheel", group="flywheel", verts=32, bevel=0.01, parent=WHEEL)     # hub
rivet((0, 0, 0.052), 0.024, group="flywheel", parent=WHEEL)                                # the shaft's nut
# The vacuum gauge, flat on the barrel's head and facing up, at the roof's angle like
# the viewport glass: a level circle draws as a full circle through this camera, so it
# stays as readable as a dial facing the camera head-on (Liam, 2026-10-08). Set deep in
# a hooded case so it sits in shade (spec 3.2). Bare: the needle is Animatorio's.
GAUGE = empty("gauge", loc=(BX, BY, 0.07 + BH + 0.05 + 0.06))
cyl((0, 0, -0.03), 0.13, 0.06, "brass", verts=48, bevel=0.01, parent=GAUGE)                 # case
ring((0, 0, 0.02), 0.13, 0.1, 0.05, "brass", parent=GAUGE, verts=48)                        # the hood
cyl((0, 0, 0.0), 0.1, 0.004, "dial", verts=48, bevel=0.0, parent=GAUGE)                     # dial face
cyl((0, 0, 0.004), 0.012, 0.006, "steel", verts=16, bevel=0.0, parent=GAUGE)                 # the needle's pivot

# 7. The copper: a ring on the deck round the hatch, clamped down, and a feeder down
# each diagonal to its corner's stack -- none crosses a face's middle; three stacks, three feeders.
RING_R = 1.045
pts = [on_body(2 * math.pi * k / 96, RING_R, H + 0.03) for k in range(96)]
cu = bpy.data.curves.new("deckring", "CURVE")
cu.dimensions = "3D"
cu.bevel_depth = 0.026
cu.bevel_resolution = 4
sp = cu.splines.new("POLY")
sp.points.add(len(pts) - 1)
for p, co in zip(sp.points, pts):
    p.co = (*co, 1)
sp.use_cyclic_u = True
ob = bpy.data.objects.new("deckring", cu)
sc.collection.objects.link(ob)
_finish(ob, "copper", "static", bevel=0, parent=BODY)
for k in range(16):
    a = 2 * math.pi * (k + 0.5) / 16
    box(on_body(a, RING_R, H + 0.03), (0.035, 0.07, 0.065), "brass", rot=(0, 0, a), bevel=0.006, parent=BODY)
for cx, cy, px, py, d in STACKS:
    # leave the ring where the diagonal to this corner crosses the deck edge
    lx, ly = cx * 1.0, (cy * 1.0 - YC) / K       # the corner's direction, in the drum's own frame
    th = math.atan2(ly, lx)
    q = lambda r, z: (r * math.cos(th), YC + K * r * math.sin(th), z)     # noqa: E731
    feeder = [q(RING_R, H + 0.03), q(RD + 0.08, H + 0.02), q(RD + 0.14, PZ + 0.06),
              (cx * 0.98, cy * 0.98, PZ + 0.02), (px, py, SZ + 0.22)]
    tube(feeder, 0.036, "copper")
    for (x, y, z) in feeder[2:4]:
        box((x, y, z), (0.07, 0.07, 0.035), "brass", bevel=0.006)

# 8. The pipe pictures: the engine draws one at whichever face the input is turned
# to. Each is a stub on the pipe's own centreline, ending in a flange the size of the
# pipe's bolted end ring, so the joint reads as pipe meeting pipe (Liam, 2026-10-02);
# in assembler 3's sheet size and shift, and its outline within 2 px of assembler 3's.
#
# The centrelines and rings are vanilla's straight pipes as the engine draws them in
# the tile the input points into (base/graphics/entity/pipe, 128 px at scale 0.5,
# centred on the tile; measured on the opaque body, the painted-in shadow left out):
#   horizontal (east, west): axis 1.0 px above the tile's centre; body 40 px tall,
#                            the bolted end ring 52 px tall at the tile's edge
#   vertical (north, south): axis 0.5 px right of the tile's centre; body 39 px wide,
#                            the end ring 51 px wide
# A flange is a disc square to its pipe: one across a horizontal pipe shows 1.118 r
# above and below its axis on the screen (r along y, r/2 of height), one across a
# vertical pipe r either side and r/2 above and below.
#
# Behind each stub stands its backplate: a slab of quads, one per pixel assembler
# 3's picture draws (alpha over 127), laid where the engine puts that pixel, in a
# plane that maps the screen to the model one to one -- the wall the stub comes out
# of, in vanilla's outline. The stub and its flanges stand in front of it.
import re  # noqa: E402

VANILLA = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity/assembling-machine-3")
OUTSIDE = {"N": (0, -2), "E": (2, 0), "S": (0, 2), "W": (-2, 0)}     # the tile each turn points into
H_AXIS_V = 1.0 / 64          # horizontal pipe: axis, screen tiles above its tile's centre
V_AXIS_U = 0.5 / 64          # vertical pipe: axis, screen tiles right of its tile's centre
H_RING_R = 26 / 64 / 1.118   # a flange that shows 52 px tall across a horizontal pipe: 0.363
V_RING_R = 25.5 / 64         # a flange that shows 51 px wide across a vertical pipe: 0.398
ZA = 0.62                    # the stubs' axis height


def vanilla_mask(face):
    """Assembler 3's picture for `face`: its drawn pixels (alpha over 127) as (i, j),
    j down from the top, and the screen px of its top-left corner from the origin."""
    stem = os.path.join(VANILLA, f"assembling-machine-3-pipe-{face}")
    bx, by = (float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)",
                                           open(stem + ".lua").read()).groups())
    img = bpy.data.images.load(stem + ".png", check_existing=True)
    w, h = img.size
    px = list(img.pixels)
    drawn = {(i, j) for j in range(h) for i in range(w) if px[((h - 1 - j) * w + i) * 4 + 3] > 127 / 255}
    tx, ty = OUTSIDE[face]
    return drawn, (tx + bx / 32) * 64 - w / 2, (ty + by / 32) * 64 - h / 2


def slab(face, lift, mat):
    """The backplate: a quad per drawn pixel, its corners lifted into the model by
    `lift(u, v)` (screen tiles, u right, v up). Its own group, so the stub can be
    rendered without it to measure."""
    drawn, x0, y0 = vanilla_mask(face)

    def build(bm):
        corners = {}

        def corner(i, j):
            if (i, j) not in corners:
                corners[(i, j)] = bm.verts.new(lift((x0 + i) / 64, -(y0 + j) / 64))
            return corners[(i, j)]
        for i, j in drawn:
            bm.faces.new((corner(i, j + 1), corner(i + 1, j + 1), corner(i + 1, j), corner(i, j)))
    return mesh_object(f"slab-{face}", build, mat, f"slab-{face}", bevel=0)


def fitting_S():
    g = "port-S"
    k = LEAN / HZ + 0.5                              # screen v per unit height on the face

    def lift(u, v):
        z = (v + E + 0.035) / k
        return Vector((u, -E + LEAN * z / HZ - 0.035, z))
    slab("S", lift, "drum")

    def face_pt(x, z, out=0.0):
        return (x, -E + LEAN * z / HZ - out, z)
    for k_ in range(13):                             # bolts round the plate's edge
        rivet(face_pt(-0.36 + 0.72 * k_ / 12, 1.06, 0.045), 0.017, group=g)
    for z in (0.35, 0.6, 0.85):
        for x in (-0.41, 0.41):
            rivet(face_pt(x, z, 0.045), 0.017, group=g)
    x = V_AXIS_U                                     # on the vertical pipe's centreline
    yf = -E + LEAN * ZA / HZ - 0.035
    ax = (math.pi / 2, 0, 0)
    ring((x, yf - 0.03, ZA), 0.44, 0.33, 0.05, "steel", g, rot=ax, bevel=0.01)          # wall flange
    for k_ in range(16):
        t = 2 * math.pi * k_ / 16
        rivet((x + 0.39 * math.cos(t), yf - 0.06, ZA + 0.39 * math.sin(t)), 0.016, group=g)
    # the stub, out to a closed end disc the width of the pipe's end ring, its face
    # landing where assembler 3's does (widest at v -1.47 to -1.53)
    YE = -1.53 - ZA / 2
    cyl((x, (yf + YE) / 2, ZA), 0.33, yf - YE, "steel", g, verts=64, rot=ax, bevel=0.0)
    cyl((x, YE + 0.03, ZA), V_RING_R, 0.06, "steel", g, verts=64, rot=ax, bevel=0.012)        # closed disc
    cyl((x, YE - 0.002, ZA), V_RING_R - 0.035, 0.006, "drum", g, verts=64, rot=ax, bevel=0.0)  # its painted face


SIDE = {"E": dict(sign=1, x_plate=1.22), "W": dict(sign=-1, x_plate=-1.2)}


def fitting_side(face):
    """East or west: a dark backplate, a neck, and an end flange the height of the
    horizontal pipe's end ring, all on the pipe's centreline; the flange's outer face
    on the footprint edge, where the pipe's ring meets it."""
    p = SIDE[face]
    g, sign = f"port-{face}", p["sign"]
    x0 = p["x_plate"]

    def lift(u, v):
        z = ZA - sign * 1.6 * (u - x0)
        return Vector((u, v - z / 2, z))
    slab(face, lift, "hull")                        # the hull's dark paint: vanilla's side plate is dark
    ya = H_AXIS_V - ZA / 2                          # the axis lands on the pipe's, on the screen
    ax = (0, math.pi / 2, 0)
    t = 0.045
    xf = sign * (1.5 - t / 2)
    cyl(((x0 + xf) / 2, ya, ZA), 0.24, abs(xf - x0), "steel", g, verts=64, rot=ax, bevel=0.0)  # neck
    cyl((xf, ya, ZA), H_RING_R, t, "steel", g, verts=64, rot=ax, bevel=0.008)                  # end flange
    cyl((xf - sign * (t / 2 + 0.01), ya, ZA), H_RING_R - 0.04, 0.02, "steel", g, verts=64, rot=ax, bevel=0.004)
    for k in range(12):
        a = 2 * math.pi * k / 12
        rivet((xf - sign * (t / 2 + 0.02), ya + 0.3 * math.cos(a), ZA + 0.3 * math.sin(a)), 0.015, group=g)


def fitting_N():
    """North: a flange the width of the vertical pipe's end ring, on its centreline,
    facing the camera's way; the engine draws it behind the hull."""
    g = "port-N"
    yN, zN = 1.2, 0.62
    v0 = yN + zN / 2

    def lift(u, v):
        b = v - v0
        return Vector((u, yN + 0.6 * b, zN + 0.8 * b))
    slab("N", lift, "steel")
    ax = (math.pi / 2, 0, 0)
    # Thin, as vanilla's ring is, and leant back 7.7 degrees: assembler 3 draws this
    # ring 16 px tall above its widest row, which a disc square to the pipe shows as
    # 12.7 (r/2) -- leant back, its upper half reads r(sin 7.7 + cos 7.7 / 2) = 0.25
    # tiles. Centred at v 1.544 its top lands on assembler 3's (v 1.81) and it is
    # widest where assembler 3's is (v 1.56).
    phi = math.radians(7.7)
    cyl((V_AXIS_U, 1.544 - ZA / 2, ZA), V_RING_R, 0.04, "steel", g, verts=64,
        rot=(math.pi / 2 - phi, 0, 0), bevel=0.008)
    ys = 1.544 - ZA / 2 - 0.025
    for k in range(16):
        a = 2 * math.pi * k / 16
        rivet((V_AXIS_U + 0.34 * math.cos(a), ys - 0.005, ZA + 0.34 * math.sin(a)), 0.015, group=g)


# ---------------------------------------------------------------- passes

rig.sun()
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()

if PORTS:
    fitting_S()
    fitting_side("E")
    fitting_side("W")
    fitting_N()


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


for o in PARTS["port"]:
    # the glass lights nothing: its glow stays inside the viewport (3.3, one circle)
    for prop in ("visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
        setattr(o, prop, False)

if PORTS:
    contract.declare(OUT_DIR, canvas=PORT_CANVAS, **DECL)
    rig.camera(*PORT_CANVAS)
    for f in FACES:
        setup(visible=(f"port-{f}", f"slab-{f}"))
        rig.render(f"{OUT_DIR}/port-{f}.png")
        setup(visible=(f"port-{f}",))              # the stub alone, to measure its axis and flange
        rig.render(f"{OUT_DIR}/axis-{f}.png")
    sys.exit(0)

# Through the contrast look anything much above this clips the glass to white.
GLOW = 1.2


def glow(on):
    M["port"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = \
        GLOW if on else 0.0


STATIC = ("static", "hull", "port")
MOVING = ("flywheel",)

if ICON:
    sc.cycles.samples = 128
    cam = rig.camera(1024, 1024, centre_px=(512, 500), ss=1)
    cam.data.ortho_scale = 3.7
    setup(visible=STATIC + MOVING)
    glow(True)
    rig.render(f"{OUT_DIR}/icon.png")
    sys.exit(0)

contract.declare(OUT_DIR, canvas=CANVAS, **DECL)
rig.camera(*CANVAS)


def indicator_cut(on):
    """The viewport glass as the light pass wants it: lit white, for the engine to tint."""
    t = M["port"].node_tree
    b = t.nodes["Principled BSDF"]
    ramp = next(n for n in t.nodes if n.type == "VALTORGB")
    if on:
        indicator_cut.saved = [tuple(e.color) for e in ramp.color_ramp.elements]
        for e in ramp.color_ramp.elements:
            e.color = (1, 1, 1, 1)
        b.inputs["Emission Strength"].default_value = 1.0
    else:
        for e, c in zip(ramp.color_ramp.elements, indicator_cut.saved):
            e.color = c
        b.inputs["Emission Strength"].default_value = 0.0


FLY = DECL["animations"][0]

for d in contract.each_direction(ROOT, DECL["directions"]):
    def path(stem, d=d):
        return f"{OUT_DIR}/{contract.named(stem, d)}.png"
    sc.render.use_border = False
    WHEEL.rotation_euler.z = 0.0

    # the plate leaves the flywheel out: the engine draws it, frame by frame, over
    # the barrel and niche it uncovers
    setup(visible=STATIC)
    glow(False)
    rig.render(path("idle"))
    glow(True)
    rig.render(path("working"))
    glow(False)
    if IDLE:
        break
    # the stopped machine in one render, the flywheel at frame 0: what pack.py holds
    # idle + flywheel-00 to
    setup(visible=STATIC + MOVING)
    rig.render(path("still"))

    setup(visible=STATIC + MOVING, ground=True)
    for o in [o for objs in PARTS.values() for o in objs]:
        o.visible_camera = False
    rig.render(path("shadow"))

    # the indicator: the viewport glass alone, white, everything in front of it cut out
    setup(visible=("port",), holdouts=("static", "hull") + MOVING)
    indicator_cut(True)
    rig.render(path("indicator"))
    indicator_cut(False)

    # the flywheel: 16 frames through 60 degrees (its six spokes), its own shadow
    # caught on the barrel and niche behind it; only that window changes, so only it
    # is rendered
    setup(visible=MOVING, catchers=STATIC)
    sc.render.use_border = True
    sc.render.use_crop_to_border = False
    sc.render.border_min_x, sc.render.border_max_x = 0.55, 0.9
    sc.render.border_min_y, sc.render.border_max_y = 0.06, 0.45
    for f in range(FLY["frames"]):
        WHEEL.rotation_euler.z = -math.radians(60 / FLY["frames"] * f)
        rig.render(path(contract.frame(FLY["name"], f)))
    WHEEL.rotation_euler.z = 0.0
    sc.render.use_border = False
