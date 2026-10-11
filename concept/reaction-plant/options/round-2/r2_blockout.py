"""Reaction Plant redesign, options round 2 (5x5): five lit blockouts, one per option.

  $BLENDER -b --python r2_blockout.py -- <out-dir> <E|F|G|H|I> [--frames N] [--quick]
           [--dirs] [--only working|idle] [--ss K]

Writes into <out-dir>/<option>/, at K x sprite size (default rig.SS = 4) on a
512 x 448 sprite canvas with the entity origin at (208, 272):

  working-NN.png  the machine running, frame NN of the signature loop (N frames,
                  default 24), with the input stubs drawn for a north-facing plant
  idle.png        the same, stopped and unlit, at frame 0
  dir-<N|E|S|W>.png  with --dirs: idle, with the engine's stubs where a plant
                  facing that way has them -- the one plate under rotation

Ports: today's 3x3 ports moved out to the 5x5 edge at the same tile offsets --
two inputs at -1 and +1 on the faced side, the dormant output at 0 opposite
(art only; no port proposal). A blockout, not a model: round 1's shared helpers
(options_blockout.py) and the layered finish (tools/blender/materials.py), on
blocked-out forms. Units are tiles; north is +Y; a point (x, y, z) lands about
(x, y + z/2) tiles up the screen, so a top may rise above the north edge
(y 2.5) by y + z/2 - 2.5 -- vanilla's refinery rises 0.97. Nothing is adopted.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import rig  # noqa: E402
from materials import layered, hazard_pattern  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR, OPTION = argv[0], argv[1].upper()
QUICK = "--quick" in argv
DIRS = "--dirs" in argv
NF = int(argv[argv.index("--frames") + 1]) if "--frames" in argv else 24
ONLY = argv[argv.index("--only") + 1] if "--only" in argv else None
OUT = os.path.join(OUT_DIR, OPTION)
os.makedirs(OUT, exist_ok=True)

CANVAS = (512, 448)
CENTRE = (208, 272)
SSK = int(argv[argv.index("--ss") + 1]) if "--ss" in argv else rig.SS

sc = rig.reset()
sc.cycles.samples = 12 if QUICK else 64
ROOT = rig.turntable(rig.stretch_root())


def swatch(name):
    return os.path.join(HERE, "..", "..", "model", "swatches", f"concept_{name}.png")


# ---------------------------------------------------------------- materials
M = {
    # kamacite plate, painted and worn (spec 3.3: #4A463F -> #6E685C)
    "shell": layered("shell", "#4C4135", wear=0.6, rust=0.3, dust=0.2, swatch=swatch("drum"), ground=0.5),
    "plate": layered("plate", "#57503F", wear=0.55, rust=0.35, dust=0.3, jitter=0.15, ground=0.6),
    "steel": layered("steel", "#8A857C", metal="#C8C2B6", paint_metal=0.9, paint_rough=0.25,
                     wear=0.5, rust=0.2, dust=0.15, grime=0.5),
    "lead": layered("lead", "#5E5E66", metal="#8A8A92", paint_metal=0.3, paint_rough=0.7,
                    wear=0.3, rust=0.0, jitter=0.06, swatch=swatch("band")),
    "cast": layered("cast", "#36363C", metal="#6A6A70", paint_metal=0.5, paint_rough=0.7,
                    wear=0.3, rust=0.35, swatch=swatch("cast")),
    "copper": layered("copper", "#94592C", metal="#B88050", paint_metal=0.9, paint_rough=0.4,
                      wear=0.4, rust=0.0, dust=0.25, grime=0.5, swatch=swatch("copper"), patina=0.3),
    "brass": layered("brass", "#9C7034", metal="#C09A58", paint_metal=0.9, paint_rough=0.38,
                     wear=0.4, rust=0.0, dust=0.2, swatch=swatch("brass")),
    "teal": layered("teal", "#1C5A56", paint_metal=0.0, paint_rough=0.8, wear=0.6, rust=0.3, swatch=swatch("teal")),
    # fat rubber hose, the drop crusher's warm rust-brown rubber, and a black one
    "hose": layered("hose", "#9A5C38", metal="#C89468", paint_metal=0.0, paint_rough=0.42, wear=0.3,
                    rust=0.05, dust=0.45, grime=0.4, jitter=0.12),
    "hose_k": layered("hose_k", "#2E2B27", metal="#5A554D", paint_metal=0.0, paint_rough=0.5, wear=0.25,
                      rust=0.0, dust=0.5, grime=0.4, jitter=0.1),
    # lagging: canvas wrap over insulation, khaki, dirty
    "lag": layered("lag", "#8C8068", metal="#A89C82", paint_metal=0.0, paint_rough=0.9, wear=0.2,
                   rust=0.25, dust=0.5, grime=0.6, jitter=0.12),
    "hazard": layered("hazard", "#B8962E", paint_metal=0.1, paint_rough=0.8, wear=0.6, rust=0.4,
                      pattern=hazard_pattern),
    "gauge": layered("gauge", "#D8D2C0", paint_metal=0.0, paint_rough=0.4, wear=0.0, rust=0.0,
                     dust=0.1, grime=0.2, jitter=0.03),
    "rubber": layered("rubber", "#24221F", metal="#4A453E", paint_metal=0.0, paint_rough=0.6, wear=0.1,
                      rust=0.0, dust=0.3, grime=0.3),
}
for _n, _c in (("red", "#B04A3A"), ("blue", "#4A74B0"), ("yellow", "#D2A83E"), ("black", "#2E2C29")):
    M["cable_" + _n] = layered("cable_" + _n, _c, metal="#B0AA9E", paint_metal=0.0, paint_rough=0.45,
                               wear=0.1, rust=0.0, dust=0.25, grime=0.3, jitter=0.06)

# glass: thick, slightly smoky borosilicate
glass = bpy.data.materials.new("glass")
glass.use_nodes = True
gb = glass.node_tree.nodes["Principled BSDF"]
gb.inputs["Base Color"].default_value = rig.srgb("#C8D8E0")
gb.inputs["Roughness"].default_value = 0.06
gb.inputs["IOR"].default_value = 1.47
gb.inputs["Transmission Weight"].default_value = 0.92
gb.inputs["Coat Weight"].default_value = 0.4
M["glass"] = glass
# a flat window seen at 30 deg: thin, low-reflection, or it mirrors the sky grey
pane = bpy.data.materials.new("pane")
pane.use_nodes = True
pb = pane.node_tree.nodes["Principled BSDF"]
pb.inputs["Base Color"].default_value = rig.srgb("#D8E4EA")
pb.inputs["Roughness"].default_value = 0.04
pb.inputs["IOR"].default_value = 1.08
pb.inputs["Transmission Weight"].default_value = 1.0
pb.inputs["Specular IOR Level"].default_value = 0.25
M["pane"] = pane

PHASES = []       # (value node, cycles per loop): set per frame
GLOWS = []        # emission strength nodes, 0 when idle
GLOW = 2.4


def fluid(name, mode, scale=6.0, k=1, arms=3, bright=1.0):
    """The radiant solution: an emissive blue whose pattern moves with a phase.

    mode "flow": bands along the object's local Z, distorted by noise, travelling
    k band-widths a loop. mode "swirl": a spiral of `arms` arms about local Z,
    turning k/arms of a revolution a loop. Dark troughs, bright crests, inside
    #1F63FF -> #73ADFF; with the light off, a dark navy liquid with a sheen.
    """
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    phase = N.new("ShaderNodeValue")
    PHASES.append((phase, k))
    noise = N.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale * 0.7
    noise.inputs["Detail"].default_value = 3.0
    L.new(tc.outputs["Object"], noise.inputs["Vector"])
    if mode == "flow":
        wave = N.new("ShaderNodeTexWave")
        wave.bands_direction = "Z"
        wave.inputs["Scale"].default_value = scale
        wave.inputs["Distortion"].default_value = 11.0
        wave.inputs["Detail"].default_value = 4.0
        wave.inputs["Detail Scale"].default_value = 1.5
        L.new(tc.outputs["Object"], wave.inputs["Vector"])
        neg = N.new("ShaderNodeMath")
        neg.operation = "MULTIPLY"
        neg.inputs[1].default_value = -1.0
        L.new(phase.outputs[0], neg.inputs[0])
        L.new(neg.outputs[0], wave.inputs["Phase Offset"])
        pat = wave.outputs["Fac"]
    else:
        sep = N.new("ShaderNodeSeparateXYZ")
        L.new(tc.outputs["Object"], sep.inputs[0])
        ang = N.new("ShaderNodeMath")
        ang.operation = "ARCTAN2"
        L.new(sep.outputs[1], ang.inputs[0])
        L.new(sep.outputs[0], ang.inputs[1])
        rad = N.new("ShaderNodeVectorMath")
        rad.operation = "LENGTH"
        L.new(tc.outputs["Object"], rad.inputs[0])
        a1 = N.new("ShaderNodeMath")
        a1.operation = "MULTIPLY"
        a1.inputs[1].default_value = float(arms)
        L.new(ang.outputs[0], a1.inputs[0])
        r1 = N.new("ShaderNodeMath")
        r1.operation = "MULTIPLY"
        r1.inputs[1].default_value = scale * 2.2
        L.new(rad.outputs["Value"], r1.inputs[0])
        nz = N.new("ShaderNodeMath")
        nz.operation = "MULTIPLY"
        nz.inputs[1].default_value = 2.5
        L.new(noise.outputs["Fac"], nz.inputs[0])
        s1 = N.new("ShaderNodeMath")
        s1.operation = "ADD"
        L.new(a1.outputs[0], s1.inputs[0])
        L.new(r1.outputs[0], s1.inputs[1])
        s2 = N.new("ShaderNodeMath")
        s2.operation = "ADD"
        L.new(s1.outputs[0], s2.inputs[0])
        L.new(nz.outputs[0], s2.inputs[1])
        s3 = N.new("ShaderNodeMath")
        s3.operation = "SUBTRACT"
        L.new(s2.outputs[0], s3.inputs[0])
        L.new(phase.outputs[0], s3.inputs[1])
        sn = N.new("ShaderNodeMath")
        sn.operation = "SINE"
        L.new(s3.outputs[0], sn.inputs[0])
        mr = N.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = -1.0
        L.new(sn.outputs[0], mr.inputs["Value"])
        pat = mr.outputs["Result"]
    mix = N.new("ShaderNodeMix")
    mix.data_type = "FLOAT"
    mix.inputs["Factor"].default_value = 0.45 if mode == "flow" else 0.22
    L.new(pat, mix.inputs["A"])
    L.new(noise.outputs["Fac"], mix.inputs["B"])
    ramp = N.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position, cr.elements[0].color = 0.25, rig.srgb("#0B2A8C")
    cr.elements[1].position, cr.elements[1].color = 0.8, rig.srgb("#73ADFF")
    e = cr.elements.new(0.52)
    e.color = rig.srgb("#1F63FF")
    L.new(mix.outputs["Result"], ramp.inputs["Fac"])
    dark = N.new("ShaderNodeMix")
    dark.data_type = "RGBA"
    dark.inputs["Factor"].default_value = 0.82
    L.new(ramp.outputs["Color"], dark.inputs["A"])
    dark.inputs["B"].default_value = rig.srgb("#0A1022")
    L.new(dark.outputs["Result"], b.inputs["Base Color"])
    L.new(ramp.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Roughness"].default_value = 0.15
    b.inputs["Emission Strength"].default_value = GLOW * bright
    GLOWS.append((b.inputs["Emission Strength"], GLOW * bright))
    M[name] = m
    return name


def emissive(name, hexcol, bright=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#141C30")
    b.inputs["Emission Color"].default_value = rig.srgb(hexcol)
    b.inputs["Emission Strength"].default_value = GLOW * bright
    GLOWS.append((b.inputs["Emission Strength"], GLOW * bright))
    M[name] = m
    return name


emissive("bubble", "#A8CCFF", 1.3)
lamp = bpy.data.materials.new("lamp")
lamp.use_nodes = True
lb = lamp.node_tree.nodes["Principled BSDF"]
lb.inputs["Base Color"].default_value = rig.srgb("#203020")
lb.inputs["Emission Color"].default_value = rig.srgb("#40FF60")
lb.inputs["Emission Strength"].default_value = 3.0
M["lamp"] = lamp
LAMP_ON = lb.inputs["Emission Strength"]
M["fleck"] = layered("fleck", "#1A1E28", paint_metal=0.2, paint_rough=0.5, wear=0, rust=0, dust=0, grime=0)

# ---------------------------------------------------------------- geometry
OBJS = []
ANIM = []          # callables(t in [0,1)) that pose the moving parts
STUBS = []


def _finish(o, mat, bevel=0.012, smooth=False, parent=None):
    o.data.materials.append(M[mat])
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments, mod.limit_method = bevel, 2, "ANGLE"
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    o.parent = parent or ROOT
    OBJS.append(o)
    return o


def box(loc, size, mat, rz=0.0, rot=None, bevel=0.012, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot or (0, 0, rz))
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, bevel, parent=parent)


def cyl(loc, r, h, mat, rot=(0, 0, 0), verts=48, bevel=0.01, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    return _finish(bpy.context.active_object, mat, bevel, smooth=True, parent=parent)


def torus(loc, major, minor, mat, rot=(0, 0, 0), seg=48, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, rotation=rot,
                                     major_segments=seg, minor_segments=10)
    return _finish(bpy.context.active_object, mat, 0, smooth=True, parent=parent)


def annulus(loc, r_in, r_out, h, mat, rot=(0, 0, 0), seg=64, parent=None):
    """A thick ring: a frame, a collar, a hoop with its middle open."""
    me = bpy.data.meshes.new("annulus")
    bm = bmesh.new()
    rows = []
    for r, z in ((r_out, -h / 2), (r_out, h / 2), (r_in, h / 2), (r_in, -h / 2)):
        rows.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z))
                     for k in range(seg)])
    for i in range(4):
        a_, b_ = rows[i], rows[(i + 1) % 4]
        for k in range(seg):
            j = (k + 1) % seg
            bm.faces.new((a_[k], a_[j], b_[j], b_[k]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("annulus", me)
    sc.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    return _finish(o, mat, 0.006, smooth=True, parent=parent)


def sphere(loc, r, mat, scale=(1, 1, 1), seg=24, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2)
    o = bpy.context.active_object
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, 0, smooth=True, parent=parent)


def head(x, y, z, r, h, mat, up=True):
    """A dished head: the top of a sphere, squashed to height h."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0), segments=48, ring_count=24)
    o = bpy.context.active_object
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if (v.co.z < -0.01 if up else v.co.z > 0.01)], context="VERTS")
    bm.to_mesh(me)
    bm.free()
    o.scale = (r, r, h)
    o.location = (x, y, z)
    # scale only: the head keeps its own origin, so a drum can turn it about its end
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _finish(o, mat, 0, smooth=True)


def along(t):
    return Vector(t).normalized().to_track_quat("Z", "Y").to_euler()


def catmull(pts, step=0.01):
    P = [Vector(p) for p in pts]
    ext = [2 * P[0] - P[1]] + P + [2 * P[-1] - P[-2]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1:i + 3]
        n = max(2, math.ceil((p2 - p1).length / step))
        for k in range(n):
            t = k / n
            out.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (3 * p1 - p0 - 3 * p2 + p3) * t * t * t))
    out.append(P[-1])
    return out


def frames(P):
    T = [(P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized() for i in range(len(P))]
    up = Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((1, 0, 0))
    N = [T[0].cross(up).normalized()]
    for i in range(1, len(P)):
        n = N[-1] - T[i] * N[-1].dot(T[i])
        N.append(n.normalized() if n.length > 1e-6 else N[-1])
    B = [t.cross(n) for t, n in zip(T, N)]
    return T, N, B


def sweep(P, r, mat, corr=0.0, pitch=0.03, seg=16):
    T, N, B = frames(P)
    s = [0.0]
    for a_, b_ in zip(P, P[1:]):
        s.append(s[-1] + (b_ - a_).length)
    me = bpy.data.meshes.new("sweep")
    bm = bmesh.new()
    rings = []
    for i, p in enumerate(P):
        rr = r * (1 + corr * (0.5 + 0.5 * math.cos(2 * math.pi * s[i] / pitch)))
        rings.append([bm.verts.new(p + rr * (math.cos(2 * math.pi * k / seg) * N[i]
                                             + math.sin(2 * math.pi * k / seg) * B[i])) for k in range(seg)])
    for a_, b_ in zip(rings, rings[1:]):
        for k in range(seg):
            j = (k + 1) % seg
            bm.faces.new((a_[k], a_[j], b_[j], b_[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("sweep", me)
    sc.collection.objects.link(o)
    return _finish(o, mat, 0, smooth=True), P, T, s


def hose(pts, r=0.085, mat="hose"):
    """A fat corrugated hose with crimped ferrules and big nuts at both ends."""
    P = catmull(pts)
    sweep(P, r, mat, corr=0.10, pitch=0.045, seg=18)
    for p, q in ((P[0], P[1]), (P[-1], P[-2])):
        t = (p - q).normalized()
        cyl(tuple(p - t * 0.05), r * 1.3, 0.11, "steel", rot=along(t), verts=20, bevel=0.006)
        torus(tuple(p - t * 0.09), r * 1.3, 0.010, "steel", rot=along(t), seg=20)
        cyl(tuple(p + t * 0.005), r * 1.6, 0.04, "brass", rot=along(t), verts=6, bevel=0.0)
    return P


def lagged(pts, r=0.11, bands=0.22):
    """A lagged pipe: canvas-wrapped insulation with steel straps, flanged ends."""
    P = catmull(pts)
    _, P, T, s = sweep(P, r, "lag", seg=20)
    nxt = bands / 2
    for i, p in enumerate(P):
        if s[i] >= nxt and s[i] < s[-1] - 0.05:
            torus(tuple(p), r + 0.004, 0.009, "steel", rot=along(T[i]), seg=24)
            nxt += bands
    for p, t in ((P[0], T[0]), (P[-1], T[-1])):
        cyl(tuple(p), r * 1.25, 0.04, "steel", rot=along(t), verts=24, bevel=0.005)
    return P


def pipe(pts, r=0.06, mat="steel"):
    P = catmull(pts)
    sweep(P, r, mat, seg=16)
    return P


def bundle(pts, cols=("red", "blue", "yellow", "black"), r=0.014):
    P = catmull(pts)
    T, N, B = frames(P)
    s = [0.0]
    for a_, b_ in zip(P, P[1:]):
        s.append(s[-1] + (b_ - a_).length)
    n = len(cols)
    for k, c in enumerate(cols):
        off = [r * 1.3 * (math.cos(2 * math.pi * k / n + 9 * s[i]) * N[i]
                          + math.sin(2 * math.pi * k / n + 9 * s[i]) * B[i]) for i in range(len(P))]
        sweep([p + o for p, o in zip(P, off)], r, "cable_" + c, seg=8)


def bolts(cx, cy, z, R, n, r=0.022, mat="steel"):
    for i in range(n):
        a = 2 * math.pi * i / n
        cyl((cx + R * math.cos(a), cy + R * math.sin(a), z), r, 0.025, mat, verts=6, bevel=0)


def band(x, y, z, r, h=0.07, mat="lead", lugs=2, lug_a=-math.pi / 2):
    cyl((x, y, z), r + 0.025, h, mat, verts=64)
    for i in range(lugs):
        a = lug_a + 2 * math.pi * i / lugs
        box((x + (r + 0.05) * math.cos(a), y + (r + 0.05) * math.sin(a), z), (0.06, 0.06, h + 0.05),
            "steel", rz=a, bevel=0.006)


def flange_ring(x, y, z, r, mat="cast", h=0.06, nb=16):
    cyl((x, y, z), r + 0.045, h, mat, verts=64)
    bolts(x, y, z + h / 2 + 0.008, r + 0.03, nb, r=0.016)


def gauge(loc, facing, r=0.07):
    t = Vector(facing).normalized()
    cyl(loc, r, 0.03, "brass", rot=along(t), verts=24, bevel=0.004)
    cyl(tuple(Vector(loc) + t * 0.017), r * 0.8, 0.006, "gauge", rot=along(t), verts=24, bevel=0)


def handwheel(loc, r=0.09, axis=(0, 0, 1)):
    t = Vector(axis).normalized()
    torus(loc, r, 0.014, "copper", rot=along(t), seg=24)
    cyl(loc, 0.022, 0.05, "steel", rot=along(t), verts=12)


def coupling(x, y, z, r, axis=(0, 0, 1), mat="brass"):
    """A free-turning six-lobed spider coupling: its own object, posed per frame."""
    root = bpy.data.objects.new("coupling", None)
    sc.collection.objects.link(root)
    root.parent = ROOT
    root.location = (x, y, z)
    root.rotation_euler = along(axis)
    cyl((0, 0, 0), r * 0.55, 0.09, "cast", verts=24, parent=root)
    for i in range(6):
        a = 2 * math.pi * i / 6
        box((r * 0.7 * math.cos(a), r * 0.7 * math.sin(a), 0), (r * 0.5, r * 0.32, 0.075), mat,
            rz=a, bevel=0.006, parent=root)
    box((0, 0, 0.047), (r * 0.25, r * 1.5, 0.012), "hazard", bevel=0, parent=root)   # a stripe to see it turn
    base = root.rotation_euler.copy()

    def pose(t):
        root.rotation_euler = base
        root.rotation_euler.rotate_axis("Z", 2 * math.pi / 6 * t)
    ANIM.append(pose)
    return root


def bubbles(cx, cy, z0, z1, r, n, seed, front=True):
    """Bright bubbles rising in the gap between the fluid and the glass; each
    climbs exactly the column's height a loop, so the loop is seamless."""
    rnd = random.Random(seed)
    objs = []
    for i in range(n):
        a = (-math.pi / 2 + rnd.uniform(-1.1, 1.1)) if front else rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0.008, 0.02)
        o = sphere((0, 0, 0), rr, "bubble", seg=10)
        objs.append((o, a, rnd.random(), rr))
    H = z1 - z0

    def pose(t):
        for o, a, ph, rr in objs:
            u = (ph + t) % 1.0
            o.location = (cx + r * math.cos(a + 0.4 * math.sin(6.28 * (u + ph))),
                          cy + r * math.sin(a + 0.4 * math.sin(6.28 * (u + ph))), z0 + H * u)
    ANIM.append(pose)


def port_stub(face, tile, cover=False):
    """A stand-in for the engine's pipe picture: a vanilla-sized stub in the plant's
    metal, at the footprint edge. A cover (the dormant output) is drawn flat."""
    d = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}[face]
    x = d[0] * 2.36 + (tile if d[1] else 0)
    y = d[1] * 2.36 + (tile if d[0] else 0)
    axis = (d[0], d[1], 0)
    objs = []
    if cover:
        objs.append(box((x + d[0] * 0.08, y + d[1] * 0.08, 0.06), (0.5 if d[1] else 0.12, 0.12 if d[1] else 0.5, 0.12),
                        "cast", bevel=0.01))
    else:
        objs.append(cyl((x, y, 0.30), 0.27, 0.28, "steel", rot=along(axis), verts=32))
        objs.append(cyl((x + d[0] * 0.13, y + d[1] * 0.13, 0.30), 0.33, 0.05, "cast", rot=along(axis), verts=32))
        objs.append(box((x, y, 0.08), (0.42 if d[1] else 0.24, 0.24 if d[1] else 0.42, 0.16), "cast"))
    STUBS.extend(objs)
    return objs


def stubs_for(direction):
    """Inputs on the faced side at tiles -1 and +1, the output opposite at 0 (spec 2), at the 5x5 edge."""
    face = direction
    opp = {"N": "S", "S": "N", "E": "W", "W": "E"}[face]
    port_stub(face, -1)
    port_stub(face, 1)
    port_stub(opp, 0, cover=True)


def status_lamp(x, y, z):
    cyl((x, y, z), 0.045, 0.05, "cast", verts=16)
    sphere((x, y, z + 0.035), 0.032, "lamp", seg=12)

# ======================================================================= round-2 kit
PI = math.pi


def valve(x, y, z=0.0, h=0.42, r=0.07):
    """A standing gate valve: body, bonnet, stem and handwheel."""
    cyl((x, y, z + 0.1), r * 1.3, 0.2, "cast", verts=20)
    cyl((x, y, z + 0.1 + h * 0.4), r * 0.7, h * 0.5, "steel", verts=16)
    handwheel((x, y, z + h), 0.085)


def drum_ns(x, y0, y1, z, r, mat="plate", bands=(), saddles=()):
    """A drum lying north-south on saddles, with dished ends."""
    cyl((x, (y0 + y1) / 2, z), r, y1 - y0, mat, rot=(PI / 2, 0, 0), verts=48)
    for yy, s in ((y0, -1), (y1, 1)):
        h = head(x, yy, z, r, 0.13, mat)
        h.rotation_euler = (-s * PI / 2, 0, 0)
    for yy in bands:
        cyl((x, yy, z), r + 0.025, 0.07, "lead", rot=(PI / 2, 0, 0), verts=48)
    for yy in saddles:
        box((x, yy, (z - r * 0.5) / 2 + 0.02), (r * 1.6, 0.12, z - r * 0.5 + 0.04), "cast")


def drum_ew(x0, x1, y, z, r, mat="plate", bands=(), saddles=()):
    """A drum lying east-west on saddles, with dished ends."""
    cyl(((x0 + x1) / 2, y, z), r, x1 - x0, mat, rot=(0, PI / 2, 0), verts=48)
    for xx, s in ((x0, -1), (x1, 1)):
        h = head(xx, y, z, r, 0.13, mat)
        h.rotation_euler = (0, s * PI / 2, 0)
    for xx in bands:
        cyl((xx, y, z), r + 0.025, 0.07, "lead", rot=(0, PI / 2, 0), verts=48)
    for xx in saddles:
        box((xx, y, (z - r * 0.5) / 2 + 0.02), (0.12, r * 1.6, z - r * 0.5 + 0.04), "cast")


def vtank(x, y, r, h, mat="plate", bands=(), top="lead", lug_a=-PI / 2, nozzle=(0.3, 0.0)):
    """A standing vessel on a cast foot ring, banded, dished head, a nozzle."""
    cyl((x, y, 0.07), r + 0.08, 0.14, "cast", verts=64)
    cyl((x, y, h / 2 + 0.07), r, h - 0.14, mat, verts=64)
    for z in bands:
        band(x, y, z, r, lug_a=lug_a)
    hh = min(0.24, r * 0.38)
    head(x, y, h, r, hh, top)
    if nozzle:
        nx, ny = x + nozzle[0] * r, y + nozzle[1] * r
        cyl((nx, ny, h + hh * 0.7 + 0.06), 0.085, 0.16, "steel", verts=24)
        flange_ring(nx, ny, h + hh * 0.7 + 0.14, 0.08, mat="steel", h=0.035, nb=8)
    return h + hh


def ladder(x, y, z0, z1, axis="y"):
    for z in [z0 + 0.3 * i for i in range(int((z1 - z0) / 0.3) + 1)]:
        box((x, y, z), (0.04, 0.16, 0.025) if axis == "y" else (0.16, 0.04, 0.025), "steel", bevel=0.004)
    for s in (-1, 1):
        o = (0, s * 0.08) if axis == "y" else (s * 0.08, 0)
        box((x + o[0], y + o[1], (z0 + z1) / 2), (0.025, 0.025, z1 - z0), "steel", bevel=0.003)


def pump(x, y, d=(1, 0), s=1.0):
    """A pump skid along d: motor (teal), free coupling, volute. Returns the volute's outlet top."""
    dx, dy = d
    L, Wd = 1.05 * s, 0.55 * s
    box((x, y, 0.07), (L if dx else Wd, Wd if dx else L, 0.14), "cast")
    mx, my = x - dx * 0.3 * s, y - dy * 0.3 * s
    zc = 0.14 + 0.2 * s
    box((mx, my, zc), (0.4 * s if dx else 0.38 * s, 0.38 * s if dx else 0.4 * s, 0.4 * s), "teal")
    for i in range(5):
        o = 0.065 * s * (i - 2)
        box((mx + (0 if dx else o), my + (o if dx else 0), zc + 0.21 * s),
            (0.36 * s if dx else 0.025, 0.025 if dx else 0.36 * s, 0.025), "cast", bevel=0)
    coupling(x, y, zc, 0.15 * s, axis=(dx, dy, 0))
    vx, vy = x + dx * 0.3 * s, y + dy * 0.3 * s
    cyl((vx, vy, zc + 0.02), 0.22 * s, 0.24 * s, "cast", rot=along((dx, dy, 0)), verts=32)
    cyl((vx, vy, zc + 0.27 * s), 0.07 * s, 0.16 * s, "steel", verts=16)
    return (vx, vy, zc + 0.36 * s)


def cellbox(x, y, w, d, h, wheel=True):
    """A lead-lined cell box: the solid product's drop box."""
    box((x, y, h / 2), (w, d, h), "lead", bevel=0.02)
    box((x, y, h + 0.015), (w - 0.14, d - 0.14, 0.03), "cast", bevel=0.006)
    bolts(x, y, h + 0.04, min(w, d) / 2 - 0.08, 12, r=0.014)
    box((x, y - d / 2 - 0.005, h * 0.5), (w - 0.12, 0.02, 0.1), "hazard", bevel=0)
    if wheel:
        handwheel((x, y, h + 0.1), 0.12)


def cabinet(x, y, w, d, h, mat="plate"):
    """A control cabinet: louvres, a gauge and the status lamp on the south face."""
    box((x, y, h / 2), (w, d, h), mat, bevel=0.015)
    for i in range(4):
        box((x - w * 0.15, y - d / 2 - 0.01, h * 0.35 + 0.07 * i), (w * 0.45, 0.02, 0.025), "cast", bevel=0)
    gauge((x + w * 0.25, y - d / 2 - 0.01, h * 0.7), (0, -1, 0.15), r=0.06)
    status_lamp(x + w * 0.25, y - d * 0.2, h + 0.02)


def drift(path, n, seed, mat="bubble", size=(0.012, 0.024), scale=(1, 1, 1), down=False):
    """n particles moving along path(u, a), u in [0,1) a loop: each covers the whole
    path exactly once a loop, so it wraps seamlessly. a is a fixed random in [-1,1)."""
    rnd = random.Random(seed)
    objs = []
    for i in range(n):
        o = sphere((0, 0, 0), rnd.uniform(*size), mat, scale=scale, seg=8)
        objs.append((o, rnd.random(), rnd.uniform(-1, 1)))

    def pose(t):
        for o, ph, a in objs:
            u = (ph + (-t if down else t)) % 1.0
            o.location = path(u, a)
    ANIM.append(pose)


def porthole(cx, cy, z, R, ang, r, name, k=3, arms=3, spin=0.0):
    """A bolted bullseye porthole on a vessel of radius R at angle ang: cast frame,
    a glass disc, the solution behind turning in an arms-armed vortex."""
    t = Vector((math.cos(ang), math.sin(ang), 0))
    u = t.cross(Vector((0, 0, 1))).normalized()
    w = Vector((0, 0, 1))
    c = Vector((cx, cy, z)) + t * (R - 0.02)
    cyl(tuple(c + t * 0.02), r + 0.04, 0.12, "shell", rot=along(t), verts=48)           # boss
    annulus(tuple(c + t * 0.1), r - 0.01, r + 0.1, 0.06, "cast", rot=along(t))
    for i in range(12):
        a = 2 * PI * i / 12
        cyl(tuple(c + t * 0.135 + (r + 0.055) * (math.cos(a) * u + math.sin(a) * w)), 0.017, 0.025, "steel",
            rot=along(t), verts=6, bevel=0)
    cyl(tuple(c + t * 0.095), r, 0.02, "pane", rot=along(t), verts=48, bevel=0)
    fl = cyl(tuple(c + t * 0.07), r, 0.02, fluid(name, "swirl", scale=1.2 / r, k=k, arms=arms), rot=along(t),
             verts=48, bevel=0)
    fl.rotation_euler.rotate_axis("Z", spin)
    box(tuple(c + t * 0.115), (0.04, 0.04, 2 * r + 0.06), "steel", rz=ang + PI / 2, bevel=0.004)   # a bar
    return c


def helix(cx, cy, R, z0, z1, turns, a0=0.0, n_per=56):
    n = int(turns * n_per)
    return [Vector((cx + R * math.cos(a0 + 2 * PI * turns * i / n), cy + R * math.sin(a0 + 2 * PI * turns * i / n),
                    z0 + (z1 - z0) * i / n)) for i in range(n + 1)]


def strips(x0, x1, y, zb, h0, amp, n, name, waves=1.5):
    """The sloshing surface seen through a flat window: n vertical strips of fluid
    whose tops ride a travelling wave, whole wavelengths a loop."""
    W = (x1 - x0) / n
    fl = fluid(name, "flow", scale=3.0, k=1)
    objs = []
    for i in range(n):
        o = box((x0 + W * (i + 0.5), y, zb + h0 / 2), (W * 1.02, 0.08, h0), fl, bevel=0)
        objs.append((o, i / n))

    def pose(t):
        for o, f in objs:
            hh = h0 - amp + amp * math.sin(2 * PI * (waves * f - t))
            s = hh / h0                      # box() bakes its location: scale about the floor zb
            o.scale = (1, 1, s)
            o.location.z = zb * (1 - s)
    ANIM.append(pose)




def deck(x0, y0, x1, y1, h=0.12, mat="cast", stripe=True):
    """A low bolted plant deck under the low run (a skid, not the building's base)."""
    box(((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0, y1 - y0, h), mat, bevel=0.015)
    n = max(2, int((x1 - x0) / 0.35))
    for i in range(n + 1):
        xx = x0 + 0.06 + (x1 - x0 - 0.12) * i / n
        for yy in (y0 + 0.06, y1 - 0.06):
            cyl((xx, yy, h + 0.008), 0.018, 0.02, "steel", verts=6, bevel=0)
    if stripe:
        box(((x0 + x1) / 2, y0 - 0.004, h * 0.55), ((x1 - x0) * 0.6, 0.012, h * 0.5), "hazard", bevel=0)


def barrels(x, y, n=3, seed=0, z=0.0):
    rnd = random.Random(seed)
    for dx, dy in [(0, 0), (0.27, 0.06), (0.12, -0.23), (-0.15, -0.2), (0.4, -0.18), (-0.27, 0.05)][:n]:
        m = rnd.choice(["plate", "shell", "teal", "lead", "hazard"])
        cyl((x + dx, y + dy, z + 0.19), 0.12, 0.38, m, verts=24)
        for zz in (0.1, 0.28):
            torus((x + dx, y + dy, z + zz), 0.122, 0.011, "steel", seg=24)
        cyl((x + dx + 0.05, y + dy + 0.03, z + 0.385), 0.025, 0.02, "brass", verts=8)


def jbox(x, y, w=0.32, d=0.22, h=0.4, mat="plate", z=0.0):
    box((x, y, z + h / 2), (w, d, h), mat, bevel=0.01)
    box((x, y - d / 2 - 0.01, z + h * 0.55), (w * 0.7, 0.02, h * 0.6), "cast", bevel=0.004)
    cyl((x + w * 0.3, y, z + h + 0.04), 0.03, 0.08, "steel", verts=8)


def exchanger(x0, x1, y, z, r, mat="shell"):
    """A shell-and-tube exchanger on saddles: flanged channel heads and two nozzles."""
    drum_ew(x0, x1, y, z, r, mat=mat, bands=(), saddles=(x0 + 0.25, x1 - 0.25))
    for xx in (x0 + 0.08, x1 - 0.08):
        cyl((xx, y, z), r + 0.06, 0.07, "cast", rot=(0, PI / 2, 0), verts=40)
        for i in range(10):
            a = 2 * PI * i / 10
            cyl((xx, y + (r + 0.035) * math.cos(a), z + (r + 0.035) * math.sin(a)), 0.014, 0.09, "steel",
                rot=(0, PI / 2, 0), verts=6, bevel=0)
    for xx in (x0 + 0.45, x1 - 0.45):
        cyl((xx, y, z + r + 0.06), 0.07, 0.14, "steel", verts=16)


def riser(x, y, z1, r=0.09, mat="steel"):
    cyl((x, y, z1 / 2), r, z1, mat, verts=20)
    for z in (0.15, z1 - 0.08):
        cyl((x, y, z), r + 0.04, 0.05, "cast", verts=20)


def reel(x, y, axis=(1, 0, 0)):
    """A hose reel: two cheeks, a drum of black hose."""
    t = Vector(axis).normalized()
    box((x, y, 0.12), (0.5, 0.5, 0.24) if t.x else (0.5, 0.5, 0.24), "cast")
    for s in (-1, 1):
        cyl(tuple(Vector((x, y, 0.42)) + t * 0.17 * s), 0.27, 0.03, "teal", rot=along(t), verts=32)
    cyl((x, y, 0.42), 0.2, 0.3, "hose_k", rot=along(t), verts=32)
    for k in range(5):
        torus(tuple(Vector((x, y, 0.42)) + t * (-0.12 + 0.06 * k)), 0.2, 0.035, "hose_k", rot=along(t), seg=24)

# ======================================================================= options
def option_e():
    """THE BULLSEYE TOWER. A tall riveted precipitation tower in the back-left, three
    bolted bullseye portholes climbing its face in a stair, each a turning blue vortex;
    a gas conditioner back-right and a reaction drum down the east flank; a dense
    front of pump, cell box, manifold and cabinet."""
    tx, ty, R, H = -1.15, 0.55, 0.88, 3.5
    cyl((tx, ty, 0.08), R + 0.12, 0.16, "cast", verts=72)
    cyl((tx, ty, H / 2 + 0.08), R, H - 0.16, "shell", verts=72)
    for z in (0.38, 1.3, 2.12, 2.94):
        band(tx, ty, z, R, lugs=3, lug_a=-PI / 2 + 0.9)
    head(tx, ty, H, R, 0.28, "lead")
    annulus((tx, ty, H - 0.1), R, R + 0.2, 0.05, "cast")                          # gallery
    for i in range(10):
        a = PI * 0.15 + 2 * PI * i / 13
        cyl((tx + (R + 0.17) * math.cos(a), ty + (R + 0.17) * math.sin(a), H + 0.05), 0.014, 0.28, "steel",
            verts=6, bevel=0)
    torus((tx, ty, H + 0.19), R + 0.17, 0.014, "steel")
    cyl((tx + 0.3, ty + 0.25, H + 0.36), 0.12, 0.24, "steel", verts=24)
    flange_ring(tx + 0.3, ty + 0.25, H + 0.48, 0.11, mat="steel", h=0.04, nb=8)
    gauge((tx - 0.35, ty - 0.2, H + 0.22), (0, -0.4, 1))
    for z, a, nm, sp in ((0.84, -PI / 2 - 0.5, "fl_e1", 0.0), (1.71, -PI / 2 - 0.08, "fl_e2", 1.1),
                         (2.54, -PI / 2 + 0.34, "fl_e3", 2.2)):
        porthole(tx, ty, z, R, a, 0.35, nm, k=3, arms=3, spin=sp)
    ladder(tx - R - 0.04, ty + 0.1, 0.2, H - 0.1)
    box((tx + R * 0.7, ty - R * 0.72, 3.15), (0.3, 0.06, 0.3), "teal", rz=-0.8)        # hatch
    # back-right: gas conditioner
    gx, gy = 1.5, 1.5
    vtank(gx, gy, 0.62, 2.0, "plate", bands=(0.4, 1.0, 1.6), lug_a=-PI * 0.75, nozzle=(-0.35, -0.2))
    gauge((gx - 0.3, gy - 0.6, 1.2), (-0.4, -1, 0.1))
    # east flank: reaction drum on saddles
    drum_ns(1.82, -1.05, 0.62, 0.62, 0.52, bands=(-0.6, 0.15), saddles=(-0.8, 0.4))
    box((1.65, -0.2, 1.12), (0.3, 0.26, 0.06), "teal")
    bolts(1.65, -0.2, 1.16, 0.15, 8, r=0.014)
    cyl((1.95, 0.35, 1.18), 0.09, 0.16, "steel", verts=20)
    # front
    pv = pump(-1.65, -1.85, (1, 0), 1.15)
    cellbox(-0.2, -1.85, 1.05, 0.95, 0.7)
    cabinet(1.05, -2.05, 0.72, 0.55, 0.95)
    vtank(1.95, -1.85, 0.42, 1.15, "shell", bands=(0.4,), nozzle=(0, 0.3))
    status_lamp(1.95, -1.85 - 0.3, 1.0)
    # mid: valve manifold on a copper header
    pipe([(-0.3, -1.05, 0.3), (0.3, -0.95, 0.28), (0.9, -1.0, 0.3), (1.4, -0.95, 0.42)], r=0.07, mat="copper")
    for vx, vy in ((-0.15, -1.03), (0.35, -0.96), (0.85, -1.0)):
        valve(vx, vy, 0.18, 0.48)
    box((0.35, -0.4, 0.2), (0.9, 0.5, 0.4), "plate")
    gauge((0.15, -0.66, 0.3), (0, -1, 0.2), r=0.06)
    valve(0.75, -0.35, 0.4, 0.4)
    # back-left corner and edges
    vtank(-2.1, 1.95, 0.33, 1.3, "plate", bands=(0.5,), nozzle=None)
    lagged([(-2.32, -1.1, 0.24), (-2.3, -0.3, 0.3), (-2.28, 0.4, 0.32), (tx - R + 0.05, ty - 0.35, 0.42)], r=0.12)
    lagged([(2.35, 2.3, 0.22), (1.0, 2.33, 0.25), (0.1, 2.25, 0.3), (tx + R - 0.05, ty + 0.4, 0.5)], r=0.12)
    lagged([(2.35, -0.9, 0.2), (2.33, 0.3, 0.24), (gx + 0.5, gy - 0.4, 0.4)], r=0.1)
    # hoses
    hose([(gx - 0.2, gy - 0.12, 2.25), (0.9, 1.25, 2.9), (-0.1, 0.95, 3.3), (tx + 0.3, ty + 0.25, H + 0.5)], r=0.11)
    hose([(1.95, 0.35, 1.26), (1.1, 0.4, 1.8), (0.2, 0.1, 2.0), (tx + R * 0.9, ty - 0.2, 1.72)], r=0.1,
         mat="hose_k")
    hose([pv, (-1.25, -1.45, 0.95), (-0.95, -0.85, 0.8), (tx + 0.1, ty - R + 0.05, 0.5)], r=0.1)
    hose([(-0.2, -1.5, 0.75), (-0.05, -1.0, 1.1), (-0.3, -0.45, 1.0), (tx + R * 0.75, ty - R * 0.55, 0.35)],
         r=0.085)
    hose([(1.55, -1.0, 0.95), (1.3, -0.6, 1.25), (0.95, -0.4, 0.75), (0.75, -0.35, 0.82)], r=0.075,
         mat="hose_k")
    bundle([(1.05, -1.78, 0.8), (0.6, -1.45, 0.2), (-0.7, -1.3, 0.14), (tx + 0.4, ty - R + 0.1, 0.25)])
    bundle([(gx, gy - 0.65, 0.4), (1.0, 0.7, 0.12), (0.3, 0.3, 0.12), (tx + R, ty, 0.3)], cols=("black", "yellow"))


def option_f():
    """THE CIRCULATOR. A tall reactor vessel in the back-right with two fat glass legs
    standing off its west side: a riser where the blue climbs with bubbles and a
    downcomer where it falls back with the dark precipitate -- a thermosiphon loop
    you watch go round. Scrubbers back-left, a feed drum and filter press in front."""
    rx, ry, R, H = 1.15, 0.85, 0.85, 3.2
    cyl((rx, ry, 0.08), R + 0.12, 0.16, "cast", verts=72)
    cyl((rx, ry, H / 2 + 0.08), R, H - 0.16, "plate", verts=72)
    for z in (0.4, 1.1, 1.8, 2.5):
        band(rx, ry, z, R, lugs=3, lug_a=-PI / 2 - 0.4)
    head(rx, ry, H, R, 0.28, "lead")
    # agitator drive on the head
    cyl((rx - 0.1, ry - 0.05, H + 0.3), 0.18, 0.14, "cast", verts=32)
    coupling(rx - 0.1, ry - 0.05, H + 0.42, 0.15)
    box((rx + 0.25, ry + 0.15, H + 0.38), (0.32, 0.34, 0.3), "teal")
    box((rx + R * 0.72, ry - R * 0.68, 1.45), (0.06, 0.3, 0.36), "teal", rz=PI / 4)
    ladder(rx + R + 0.04, ry + 0.1, 0.2, H - 0.1)
    gauge((rx + 0.25, ry - R - 0.02, 0.75), (0.2, -1, 0.2))
    # the legs
    legs = [(-0.05, 0.62, 2, "fl_f1"), (0.55, -0.3, -2, "fl_f2")]
    z0, z1, lr = 0.42, 2.45, 0.27
    for i, (lx, ly, k, nm) in enumerate(legs):
        cyl((lx, ly, 0.2), lr + 0.1, 0.4, "cast", verts=40)
        flange_ring(lx, ly, z0 - 0.03, lr, h=0.06)
        flange_ring(lx, ly, z1 + 0.01, lr, h=0.06)
        cyl((lx, ly, (z0 + z1) / 2), lr, z1 - z0, "glass", verts=48, bevel=0)
        cyl((lx, ly, (z0 + z1) / 2), lr - 0.05, z1 - z0 - 0.02, fluid(nm, "flow", scale=3.2, k=k), verts=48,
            bevel=0)
        band(lx, ly, (z0 + z1) / 2, lr, h=0.06, lugs=2, lug_a=0.3)
        for j in range(4):
            a = 2 * PI * (j + 0.5) / 4 + 0.3
            box((lx + (lr + 0.01) * math.cos(a), ly + (lr + 0.01) * math.sin(a), (z0 + z1) / 2),
                (0.04, 0.04, z1 - z0), "steel", rz=a, bevel=0.004)
        cyl((lx, ly, z1 + 0.16), lr * 0.75, 0.24, "cast", verts=32)
        head(lx, ly, z1 + 0.28, lr * 0.75, 0.1, "lead")
    (ax, ay, _, _), (bx, by, _, _) = legs
    drift(lambda u, a: (ax + (lr - 0.04) * math.cos(-PI / 2 + a), ay + (lr - 0.04) * math.sin(-PI / 2 + a),
                        z0 + 0.04 + (z1 - z0 - 0.08) * u), 22, 11)
    drift(lambda u, a: (bx + (lr - 0.05) * math.cos(-PI / 2 + a), by + (lr - 0.05) * math.sin(-PI / 2 + a),
                        z0 + 0.04 + (z1 - z0 - 0.08) * u), 18, 12, mat="fleck", size=(0.014, 0.024),
          scale=(1.5, 1, 0.6), down=True)
    # the loop's top: fat hoses from each leg's cap into the reactor's shoulder
    hose([(ax, ay, z1 + 0.42), (ax + 0.1, ay + 0.1, 2.95), (0.6, 0.95, 3.0), (rx - R + 0.05, ry + 0.1, 2.75)],
         r=0.12)
    hose([(bx, by, z1 + 0.42), (bx + 0.15, by + 0.05, 2.85), (0.95, 0.15, 2.7), (rx - R * 0.6, ry - R * 0.75, 2.3)],
         r=0.12, mat="hose_k")
    # the loop's foot: a cast header from the reactor foot to both legs
    pipe([(rx - R + 0.05, ry - 0.2, 0.3), (0.5, 0.45, 0.22), (ax, ay, 0.22)], r=0.11, mat="cast")
    pipe([(rx - R * 0.6, ry - R * 0.7, 0.3), (0.9, -0.2, 0.22), (bx, by, 0.22)], r=0.11, mat="cast")
    valve(0.3, 0.1, 0.0, 0.55)
    # back-left: scrubber pair
    vtank(-1.75, 1.6, 0.6, 2.0, "shell", bands=(0.4, 1.0, 1.6), lug_a=-PI / 4, nozzle=(0.3, -0.3))
    vtank(-0.75, 1.9, 0.42, 1.35, "plate", bands=(0.45, 0.95), nozzle=(0, 0))
    hose([(-1.57, 1.42, 2.4), (-0.9, 1.4, 2.85), (0.2, 1.4, 3.1), (rx - 0.3, ry + 0.3, H + 0.2)], r=0.11)
    hose([(-0.75, 1.9, 1.62), (-0.35, 1.5, 1.9), (ax - 0.1, ay + 0.1, 2.62)], r=0.085, mat="hose_k")
    # west: feed drum lying E-W
    drum_ew(-2.3, -0.75, 0.2, 0.58, 0.48, mat="plate", bands=(-1.9, -1.15), saddles=(-2.0, -1.05))
    box((-1.5, 0.2, 1.08), (0.3, 0.28, 0.06), "teal")
    hose([(-0.62, 0.2, 0.58), (-0.4, 0.4, 0.45), (ax - lr - 0.05, ay - 0.05, 0.3)], r=0.09)
    # front-left: filter press of lead and plate leaves
    box((-1.45, -1.55, 0.1), (1.6, 0.75, 0.2), "cast")
    for i in range(11):
        box((-2.1 + 0.11 * i, -1.55, 0.48), (0.085, 0.62, 0.56), "lead" if i % 2 else "plate", bevel=0.006)
    box((-0.75, -1.55, 0.48), (0.14, 0.7, 0.66), "cast")
    handwheel((-0.62, -1.55, 0.5), 0.15, axis=(1, 0, 0))
    box((-1.5, -1.94, 0.12), (1.3, 0.02, 0.08), "hazard", bevel=0)
    cellbox(-1.6, -0.62, 1.2, 0.7, 0.45, wheel=False)
    # front-right
    pv = pump(1.35, -1.85, (-1, 0), 1.15)
    cabinet(2.1, -1.0, 0.55, 0.8, 1.0)
    cabinet(0.05, -2.1, 0.7, 0.45, 0.6)
    hose([pv, (1.0, -1.4, 0.9), (0.7, -0.9, 0.8), (bx + 0.1, by - lr - 0.05, 0.6)], r=0.1)
    hose([(-0.62, -1.55, 0.85), (-0.3, -1.1, 0.95), (bx - lr, by - 0.05, 0.75)], r=0.085, mat="hose_k")
    lagged([(2.35, -2.3, 0.22), (2.33, -0.3, 0.26), (2.3, 0.6, 0.3), (rx + R * 0.7, ry - R * 0.6, 0.4)], r=0.12)
    lagged([(2.3, 2.35, 0.2), (1.2, 2.3, 0.24), (rx + 0.1, ry + R, 0.3)], r=0.1)
    lagged([(-2.35, -2.32, 0.2), (-0.6, -2.3, 0.22), (0.9, -2.32, 0.2)], r=0.1)
    bundle([(2.1, -0.65, 0.9), (1.9, -0.3, 0.2), (rx + R * 0.5, ry - R * 0.8, 0.4)])
    bundle([(0.05, -1.95, 0.55), (0.0, -1.2, 0.12), (bx - 0.2, by - 0.3, 0.3)], cols=("black", "yellow"))


def option_g():
    """THE BELTED SPHERE. A reaction sphere on six legs, west of centre, split at its
    equator by a strapped glass belt where the blue solution is spun round by the
    agitator on its crown; a tall slim vent stack back-right; receivers, a drum and
    a dense front of pump, cell box and valve rack."""
    sx, sy, R = -0.8, 0.32, 1.05
    zc, bh = 1.3, 0.42
    for i in range(6):
        a = 2 * PI * (i + 0.5) / 6
        lx, ly = sx + R * 0.86 * math.cos(a), sy + R * 0.86 * math.sin(a)
        cyl((lx, ly, zc / 2), 0.075, zc, "cast", verts=16)
        box((lx, ly, 0.06), (0.22, 0.22, 0.12), "cast")
        torus((lx, ly, zc - 0.25), 0.09, 0.02, "steel", seg=16)
    for i in range(6):
        a0, a1 = 2 * PI * (i + 0.5) / 6, 2 * PI * (i + 1.5) / 6
        p0 = Vector((sx + R * 0.86 * math.cos(a0), sy + R * 0.86 * math.sin(a0), 0.15))
        p1 = Vector((sx + R * 0.86 * math.cos(a1), sy + R * 0.86 * math.sin(a1), zc - 0.35))
        cyl(tuple((p0 + p1) / 2), 0.02, (p1 - p0).length, "steel", rot=along(p1 - p0), verts=8, bevel=0)
    head(sx, sy, zc, R, R, "plate", up=False)
    head(sx, sy, zc + bh, R, R, "plate")
    for z in (zc - 0.03, zc + bh + 0.01):
        flange_ring(sx, sy, z, R, h=0.06, nb=28)
    cyl((sx, sy, zc + bh / 2), R, bh, "glass", verts=96, bevel=0)
    cyl((sx, sy, zc + bh / 2), R - 0.06, bh - 0.01, fluid("fl_g", "swirl", scale=1.6, k=1, arms=9, bright=1.1),
        verts=96, bevel=0)
    for i in range(10):
        a = 2 * PI * (i + 0.5) / 10
        box((sx + (R + 0.012) * math.cos(a), sy + (R + 0.012) * math.sin(a), zc + bh / 2), (0.05, 0.05, bh), "steel",
            rz=a, bevel=0.004)
    rnd = random.Random(4)
    fl = []
    for i in range(20):
        o = sphere((0, 0, 0), rnd.uniform(0.014, 0.024), "fleck", scale=(1.5, 1, 0.7), seg=8)
        fl.append((o, rnd.random(), rnd.uniform(zc + 0.06, zc + bh - 0.06)))

    def pose(t):
        for o, ph, z in fl:
            a = 2 * PI * (ph + t / 9 * 1)       # one arm's width a loop, with the swirl
            o.location = (sx + (R - 0.035) * math.cos(a), sy + (R - 0.035) * math.sin(a), z)
    ANIM.append(pose)
    # meridian straps on the shells
    for i in range(8):
        a = 2 * PI * i / 8 + 0.2
        for zz in (zc - 0.45, zc + bh + 0.45):
            rr = math.sqrt(R * R - 0.45 ** 2)
            box((sx + (rr + 0.01) * math.cos(a), sy + (rr + 0.01) * math.sin(a), zz), (0.05, 0.05, 0.5), "lead",
                rz=a, rot=(0, (0.45 / R) * (1 if zz < zc else -1) * 1.0, a), bevel=0.004)
    # crown: agitator drive and nozzles
    top = zc + bh + R
    cyl((sx, sy, top + 0.02), 0.3, 0.1, "cast", verts=40)
    cyl((sx, sy, top + 0.14), 0.18, 0.16, "cast", verts=32)
    coupling(sx, sy, top + 0.27, 0.16)
    box((sx - 0.3, sy + 0.32, top + 0.12), (0.34, 0.34, 0.36), "teal")
    for i in range(4):
        box((sx - 0.3, sy + 0.32 + 0.06 * (i - 1.5), top + 0.31), (0.3, 0.02, 0.02), "cast", bevel=0)
    status_lamp(sx + 0.3, sy - 0.2, top - 0.02)
    cyl((sx + 0.5, sy + 0.45, zc + bh + 0.75), 0.1, 0.2, "steel", verts=24)
    # back-right: vent stack
    kx, ky = 1.55, 1.38
    vtank(kx, ky, 0.44, 3.08, "shell", bands=(0.4, 0.95, 1.5, 2.05, 2.6), lug_a=-PI * 0.8, nozzle=(-0.2, -0.1))
    ladder(kx + 0.48, ky - 0.05, 0.2, 2.95)
    # east: receivers and drum
    vtank(1.95, 0.35, 0.4, 1.35, "plate", bands=(0.45, 0.95), nozzle=(-0.2, 0.2))
    vtank(0.95, 0.65, 0.3, 0.95, "lead", bands=(0.4,), top="cast", nozzle=None)
    drum_ew(0.7, 2.3, -0.95, 0.52, 0.42, mat="shell", bands=(1.1, 1.9), saddles=(0.95, 2.05))
    box((1.5, -0.95, 0.96), (0.28, 0.26, 0.06), "teal")
    # front
    pv = pump(-1.6, -1.85, (1, 0), 1.15)
    cellbox(-0.15, -1.9, 1.0, 0.85, 0.65)
    box((1.3, -1.95, 0.08), (1.25, 0.6, 0.16), "cast")
    for vx in (0.85, 1.25, 1.65):
        valve(vx, -1.95, 0.16, 0.5)
    pipe([(0.7, -1.95, 0.3), (1.3, -1.95, 0.3), (1.95, -1.95, 0.3), (2.3, -1.7, 0.3)], r=0.07, mat="copper")
    cabinet(2.05, -1.65, 0.5, 0.55, 0.9)
    vtank(-2.1, -0.7, 0.3, 0.9, "plate", bands=(0.4,), nozzle=None)
    # hoses
    hose([(kx - 0.1, ky - 0.05, 3.35), (0.9, 1.15, 3.2), (0.0, 0.8, 3.05), (sx + 0.5, sy + 0.45, zc + bh + 0.85)],
         r=0.11)
    hose([(1.95, 0.35, 1.6), (1.2, 0.2, 1.7), (0.6, 0.15, 1.35), (sx + R + 0.05, sy - 0.1, zc - 0.04)], r=0.1,
         mat="hose_k")
    hose([pv, (-1.2, -1.2, 0.9), (-0.95, -0.6, 0.6), (sx, sy - 0.3, 0.35)], r=0.1)
    cyl((sx, sy, 0.3), 0.12, 0.2, "steel", verts=20)
    pipe([(sx, sy, 0.22), (sx + 0.2, sy - 0.8, 0.22), (-0.15, -1.45, 0.3)], r=0.09, mat="cast")
    hose([(1.0, -0.6, 0.8), (0.55, -0.3, 1.1), (sx + R * 0.7, sy - R * 0.6, zc - 0.1)], r=0.085)
    lagged([(-2.35, 2.35, 0.22), (-2.3, 1.0, 0.26), (-2.25, 0.1, 0.3), (sx - R * 0.86, sy - 0.2, 0.4)], r=0.12)
    lagged([(-0.4, 2.3, 0.22), (0.5, 2.25, 0.25), (kx - 0.5, ky + 0.1, 0.4)], r=0.12)
    vtank(-1.55, 2.05, 0.34, 1.2, "plate", bands=(0.45,), nozzle=(0, 0))
    lagged([(2.35, -0.5, 0.2), (2.35, 0.9, 0.22), (kx + 0.3, ky - 0.35, 0.4)], r=0.1)
    bundle([(sx - 0.3, sy + 0.32, top + 0.1), (-1.6, 1.0, 1.6), (-2.1, 1.3, 0.4), (-2.3, 2.3, 0.12)])
    bundle([(2.05, -1.4, 0.9), (1.4, -1.45, 0.14), (0.4, -1.35, 0.14), (sx + 0.5, sy - R * 0.8, 0.3)],
           cols=("black", "yellow"))


def option_h():
    """THE GLASS COIL. A tall core column in the back-left with a fat glass coil wound
    round it, three and a quarter turns, the blue solution climbing it with bubbles
    spiralling up; a gas drum on saddles down the east side and a dense front."""
    cx, cy, Rc, H = -1.05, 0.7, 0.5, 3.75
    cyl((cx, cy, 0.08), Rc + 0.14, 0.16, "cast", verts=64)
    cyl((cx, cy, H / 2 + 0.08), Rc, H - 0.16, "shell", verts=64)
    for z in (0.3, H - 0.3):
        band(cx, cy, z, Rc, lugs=4)
    head(cx, cy, H, Rc, 0.2, "lead")
    cyl((cx + 0.15, cy + 0.1, H + 0.25), 0.1, 0.2, "steel", verts=24)
    flange_ring(cx + 0.15, cy + 0.1, H + 0.35, 0.09, mat="steel", h=0.04, nb=8)
    HR, z0, z1, turns, a0 = 0.86, 0.55, 3.2, 3.25, -PI / 2 - 0.4
    P = helix(cx, cy, HR, z0, z1, turns, a0)
    sweep(P, 0.155, "glass", seg=20)
    sweep(P, 0.115, fluid("fl_h", "flow", scale=2.4, k=3, bright=1.1), seg=16)
    # clamps: a radial bracket every third of a turn, from the core to the coil
    n = len(P) - 1
    for i in range(0, n + 1, 56 // 3):
        p = P[i]
        d = Vector((p.x - cx, p.y - cy, 0)).normalized()
        mid = Vector((cx, cy, p.z)) + d * (Rc + HR) / 2
        box(tuple(mid), (HR - Rc + 0.05, 0.05, 0.06), "steel", rz=math.atan2(d.y, d.x), bevel=0.004)
        torus(tuple(p), 0.17, 0.018, "lead", rot=along(P[min(i + 1, n)] - P[max(i - 1, 0)]), seg=20)
    for p, q in ((P[0], P[1]), (P[-1], P[-2])):
        t = (p - q).normalized()
        cyl(tuple(p - t * 0.02), 0.2, 0.08, "cast", rot=along(t), verts=24)

    def coil_path(u, a):
        i = u * n
        k = min(int(i), n - 1)
        f = i - k
        p = P[k].lerp(P[k + 1], f)
        d = Vector((p.x - cx, p.y - cy, 0)).normalized()
        return tuple(p + d * 0.105 * (0.7 + 0.3 * a) + Vector((0, 0, 0.04 * a)))
    drift(coil_path, 46, 21, size=(0.014, 0.026))
    # coil feet: the solution in from a pump below, out at the top into the crown
    pv = pump(-1.65, -1.8, (1, 0), 1.15)
    hose([pv, (-1.3, -1.2, 0.95), (P[0].x + 0.05, P[0].y - 0.3, 0.75), tuple(P[0] + Vector((0.05, -0.1, -0.12)))],
         r=0.1)
    hose([tuple(P[-1] + Vector((0.06, 0.06, 0.08))), (P[-1].x + 0.3, P[-1].y + 0.1, 3.5),
          (cx + 0.15, cy + 0.1, H + 0.38)], r=0.1, mat="hose_k")
    # east: gas drum N-S on saddles and a receiver
    drum_ns(1.7, -0.45, 2.2, 0.72, 0.6, mat="plate", bands=(0.2, 1.0, 1.7), saddles=(-0.1, 1.85))
    box((1.55, 0.6, 1.3), (0.32, 0.3, 0.06), "teal")
    bolts(1.55, 0.6, 1.34, 0.17, 8, r=0.014)
    cyl((1.8, 1.6, 1.36), 0.09, 0.2, "steel", verts=20)
    vtank(0.45, 1.85, 0.42, 1.55, "shell", bands=(0.45, 1.05), nozzle=(0.2, -0.2))
    hose([(1.8, 1.6, 1.46), (1.2, 1.5, 2.3), (0.0, 1.2, 2.9), (cx + HR * 0.6, cy + 0.1, H - 0.1)], r=0.11)
    hose([(0.45, 1.85, 1.86), (0.0, 1.55, 2.05), (cx + Rc * 0.8, cy + 0.5, 2.3)], r=0.085)
    # front
    cellbox(0.15, -1.85, 1.25, 0.95, 0.7)
    cabinet(1.65, -2.0, 0.75, 0.55, 0.95)
    vtank(2.1, -1.2, 0.3, 1.0, "lead", bands=(0.35,), top="cast", nozzle=None)
    box((0.7, -0.75, 0.18), (1.2, 0.5, 0.36), "plate")
    pipe([(-0.1, -0.85, 0.42), (0.6, -0.75, 0.4), (1.35, -0.6, 0.45), (1.6, -0.35, 0.5)], r=0.07, mat="copper")
    for vx, vy in ((0.15, -0.82), (0.65, -0.75), (1.15, -0.65)):
        valve(vx, vy, 0.36, 0.42)
    hose([(0.15, -1.5, 0.75), (0.0, -0.95, 1.05), (-0.25, -0.35, 0.8), (cx + Rc * 0.7, cy - Rc * 0.7, 0.4)],
         r=0.09)
    valve(-0.35, -0.45, 0.0, 0.5)
    lagged([(-2.35, -1.0, 0.22), (-2.32, 0.5, 0.26), (-2.3, 2.35, 0.22)], r=0.12)
    lagged([(-2.3, 1.4, 0.26), (-1.95, 1.55, 0.3), (cx - 0.25, cy + Rc * 0.9, 0.35)], r=0.1)
    lagged([(-0.8, 2.35, 0.2), (0.0, 2.3, 0.24), (1.1, 2.35, 0.22), (1.25, 2.1, 0.4)], r=0.1)
    lagged([(2.35, -2.3, 0.2), (2.35, -0.8, 0.24), (2.2, -0.45, 0.4)], r=0.1)
    box((-0.35, 0.05, 0.3), (0.45, 0.4, 0.6), "teal")
    gauge((-0.35, -0.16, 0.42), (0, -1, 0.2), r=0.06)
    bundle([(1.65, -1.8, 0.95), (1.0, -1.3, 0.14), (-0.4, -1.2, 0.14), (-0.35, -0.15, 0.5)])
    bundle([(-0.35, 0.25, 0.5), (-0.1, 0.9, 0.14), (0.9, 0.6, 0.14), (1.2, 0.2, 0.4)], cols=("black", "yellow"))


def option_i():
    """THE WINDOW TANK. A long low settling tank across the front-left with a big
    framed window in its south face -- the blue solution sloshing behind three panes,
    precipitate drifting down to a dark bed; a tall reactor tower back-right drops
    fat hoses into the tank's lid, a scrubber back-left."""
    bx, by, bw, bd, bhh = -0.55, -1.2, 3.1, 1.4, 1.32
    box((bx, by, bhh / 2), (bw, bd, bhh), "plate", bevel=0.03)
    for xx in (bx - bw / 2 + 0.08, bx + bw / 2 - 0.08):
        box((xx, by, bhh / 2), (0.14, bd + 0.06, bhh + 0.02), "lead", bevel=0.01)
    box((bx, by, bhh + 0.02), (bw - 0.1, bd - 0.1, 0.04), "cast", bevel=0.008)
    fy = by - bd / 2
    wx0, wx1, wz0, wz1 = bx - 1.25, bx + 1.25, 0.22, 1.14
    box((bx, fy - 0.01, (wz0 + wz1) / 2), (wx1 - wx0 + 0.04, 0.04, wz1 - wz0 + 0.04), "fleck", bevel=0)   # dark interior
    box((bx, fy - 0.035, wz0 + 0.05), (wx1 - wx0, 0.05, 0.1), "fleck", bevel=0)                   # the bed
    strips(wx0, wx1, fy - 0.04, wz0 + 0.08, 0.8, 0.05, 30, "fl_i", waves=1.5)
    box((bx, fy - 0.125, (wz0 + wz1) / 2), (wx1 - wx0, 0.015, wz1 - wz0), "pane", bevel=0)
    # frame and mullions, bolted
    for z in (wz0 - 0.05, wz1 + 0.05):
        box((bx, fy - 0.13, z), (wx1 - wx0 + 0.2, 0.08, 0.1), "cast")
    for xx in (wx0 - 0.05, wx0 + (wx1 - wx0) / 3, wx0 + 2 * (wx1 - wx0) / 3, wx1 + 0.05):
        box((xx, fy - 0.13, (wz0 + wz1) / 2), (0.1, 0.08, wz1 - wz0 + 0.2), "cast")
    for i in range(14):
        xx = wx0 + (wx1 - wx0) * i / 13
        for z in (wz0 - 0.05, wz1 + 0.05):
            cyl((xx, fy - 0.175, z), 0.016, 0.02, "steel", rot=(PI / 2, 0, 0), verts=6, bevel=0)
    box((bx + 1.0, fy - 0.03, 0.08), (0.8, 0.02, 0.08), "hazard", bevel=0)
    drift(lambda u, a: (wx0 + 0.05 + (wx1 - wx0 - 0.1) * (0.5 + 0.5 * a), fy - 0.1, wz1 - 0.12 - 0.72 * u),
          26, 31, mat="fleck", size=(0.016, 0.026), scale=(1.4, 0.6, 1.0))
    drift(lambda u, a: (wx0 + 0.05 + (wx1 - wx0 - 0.1) * (0.5 + 0.5 * a), fy - 0.1, wz0 + 0.12 + 0.62 * u),
          18, 32, size=(0.01, 0.018))
    # lid: agitator, hatches, the hoses' landing nozzles
    lz = bhh + 0.04
    cyl((bx - 0.6, by + 0.05, lz + 0.1), 0.2, 0.2, "cast", verts=32)
    coupling(bx - 0.6, by + 0.05, lz + 0.26, 0.17)
    box((bx - 1.05, by + 0.1, lz + 0.18), (0.4, 0.42, 0.36), "teal")
    for i in range(5):
        box((bx - 1.05, by + 0.1 + 0.07 * (i - 2), lz + 0.37), (0.36, 0.02, 0.02), "cast", bevel=0)
    box((bx + 0.35, by - 0.25, lz + 0.03), (0.5, 0.4, 0.06), "teal")
    bolts(bx + 0.35, by - 0.25, lz + 0.07, 0.17, 8, r=0.014)
    for nx, ny in ((bx + 0.3, by + 0.35), (bx + 1.05, by + 0.25)):
        cyl((nx, ny, lz + 0.1), 0.12, 0.2, "steel", verts=24)
    gauge((bx + 1.05, by - 0.4, lz + 0.12), (0, -0.4, 1))
    status_lamp(bx - 1.35, by - 0.45, lz + 0.02)
    # back-right: the reactor tower
    tx, ty, R, H = 1.25, 0.95, 0.75, 3.2
    cyl((tx, ty, 0.08), R + 0.12, 0.16, "cast", verts=64)
    cyl((tx, ty, H / 2 + 0.08), R, H - 0.16, "shell", verts=64)
    for z in (0.4, 1.05, 1.7, 2.35, 2.95):
        band(tx, ty, z, R, lugs=3, lug_a=-PI / 2 - 0.5)
    head(tx, ty, H, R, 0.24, "lead")
    cyl((tx - 0.2, ty - 0.15, H + 0.3), 0.11, 0.22, "steel", verts=24)
    flange_ring(tx - 0.2, ty - 0.15, H + 0.41, 0.1, mat="steel", h=0.04, nb=8)
    ladder(tx + R + 0.04, ty, 0.2, H - 0.1)
    box((tx - R * 0.5, ty - R * 0.86, 1.4), (0.3, 0.06, 0.36), "teal", rz=-0.5)
    gauge((tx + 0.3, ty - R + 0.02, 0.75), (0.3, -1, 0.2))
    # back-left: scrubber and a pot
    vtank(-1.7, 1.4, 0.58, 2.25, "plate", bands=(0.45, 1.05, 1.65), lug_a=-PI / 3, nozzle=(0.3, -0.2))
    vtank(-0.45, 1.85, 0.38, 1.25, "lead", bands=(0.45,), top="cast", nozzle=(0, 0))
    vtank(-0.55, 0.65, 0.3, 0.8, "shell", bands=(0.35,), nozzle=None)
    # east: pump and cabinet
    pv = pump(1.85, -1.75, (0, 1), 1.15)
    cabinet(1.65, -0.5, 0.6, 0.55, 1.0)
    cabinet(2.15, -0.35, 0.4, 0.8, 0.7, mat="teal")
    # hoses
    hose([(tx - 0.45, ty - 0.55, 2.7), (0.6, 0.0, 2.6), (0.4, -0.6, 1.9), (bx + 1.05, by + 0.25, lz + 0.22)],
         r=0.12)
    hose([(tx - 0.65, ty - 0.2, 1.6), (0.2, 0.3, 1.9), (bx + 0.3, by + 0.6, 1.8), (bx + 0.3, by + 0.35, lz + 0.22)],
         r=0.11, mat="hose_k")
    hose([(-1.52, 1.25, 2.45), (-0.6, 1.4, 3.0), (0.4, 1.3, 3.2), (tx - 0.2, ty - 0.15, H + 0.45)], r=0.11)
    hose([pv, (1.6, -1.3, 0.95), (1.3, -1.2, 0.8), (bx + bw / 2 + 0.02, by + 0.1, 0.7)], r=0.1)
    hose([(-0.45, 1.85, 1.5), (-0.6, 1.2, 1.6), (-0.55, 0.65, 1.0)], r=0.08)
    lagged([(-2.35, -2.32, 0.22), (-2.35, -0.6, 0.25), (-2.32, 0.6, 0.28), (-1.7 - 0.5, 1.4 - 0.35, 0.4)], r=0.12)
    lagged([(2.35, 2.35, 0.2), (2.35, 0.3, 0.24), (tx + R * 0.8, ty - R * 0.5, 0.4)], r=0.11)
    lagged([(-2.0, 2.33, 0.22), (-0.9, 2.35, 0.24), (0.2, 2.3, 0.26), (tx - R * 0.6, ty + R * 0.75, 0.4)], r=0.1)
    pipe([(-0.55, 0.65, 0.3), (0.2, 0.2, 0.3), (0.5, -0.2, 0.25), (bx + bw / 2 - 0.3, by + bd / 2 + 0.05, 0.4)],
         r=0.08, mat="copper")
    valve(0.25, 0.1, 0.0, 0.55)
    valve(0.65, -0.05, 0.0, 0.45)
    bundle([(1.65, -0.75, 0.9), (1.2, -0.3, 0.14), (0.5, 0.45, 0.14), (tx - R, ty - 0.2, 0.4)])
    bundle([(bx - 1.05, by + 0.32, lz + 0.2), (-1.85, -0.3, 0.9), (-2.1, 0.2, 0.2), (-2.0, 0.9, 0.12)],
           cols=("black", "yellow"))




def extra_e():
    deck(-2.48, -2.48, -0.75, -1.25, 0.12)
    deck(-0.75, -2.48, 0.5, -1.3, 0.16)
    deck(0.5, -2.48, 2.48, -1.35, 0.1)
    barrels(-2.15, -0.75, 4, 1)
    jbox(-1.6, -1.05, 0.4, 0.3, 0.55)
    reel(-0.95, -1.0, (0, 1, 0))
    jbox(-0.6, -2.3, 0.3, 0.2, 0.3, z=0.16)
    barrels(0.35, -2.25, 3, 2, z=0.16)
    exchanger(-0.2, 1.3, 0.25, 0.45, 0.33)
    vtank(0.45, 1.6, 0.42, 1.6, "lead", bands=(0.5, 1.1), top="cast", nozzle=(0, -0.2))
    riser(0.2, 2.3, 1.2)
    riser(2.35, 2.35, 1.6, r=0.1, mat="copper")
    vtank(2.2, 0.95, 0.25, 0.8, "teal", nozzle=None)
    riser(-2.35, 1.0, 2.2, r=0.1)
    riser(-2.35, -0.1, 1.4, r=0.08, mat="copper")
    lagged([(-2.25, -2.0, 0.6), (-2.25, -1.3, 0.62), (-2.0, -0.4, 0.6), (-1.6, -0.15, 0.6)], r=0.1)
    valve(1.35, -1.6, 0.1, 0.5)
    jbox(2.35, -2.25, 0.2, 0.3, 0.5, z=0.1)
    hose([(0.45, 1.6, 1.86), (0.3, 1.0, 1.3), (0.0, 0.35, 0.8)], r=0.085, mat="hose_k")


def extra_f():
    deck(-2.48, -2.48, -0.4, -1.0, 0.12)
    deck(-0.4, -2.48, 2.48, -1.25, 0.14)
    deck(-0.55, -1.25, 1.0, 0.0, 0.1, stripe=False)
    barrels(-2.15, -0.7, 4, 3)
    jbox(-2.3, 0.85, 0.25, 0.5, 0.7)
    exchanger(-0.3, 0.9, -0.85, 0.42, 0.3, mat="plate")
    vtank(0.2, 1.75, 0.36, 1.2, "teal", bands=(0.45,), nozzle=None)
    riser(-0.2, 2.35, 1.0)
    riser(2.35, 1.5, 1.8, r=0.1, mat="copper")
    riser(2.35, 0.2, 1.2, r=0.08)
    vtank(1.9, -0.2, 0.3, 0.9, "lead", bands=(0.35,), top="cast", nozzle=None)
    barrels(0.6, -2.2, 3, 4, z=0.14)
    jbox(-0.2, -1.6, 0.4, 0.3, 0.5, z=0.14)
    reel(2.05, -2.05, (1, 0, 0))
    lagged([(-2.35, -0.3, 0.22), (-2.33, 0.5, 0.25), (-2.33, 1.4, 0.3), (-2.0, 1.2, 0.5)], r=0.12)
    valve(-1.1, 1.1, 0.0, 0.6)
    valve(-0.35, 0.85, 0.0, 0.5)
    hose([(-0.35, 0.85, 0.55), (-0.25, 0.4, 0.8), (ax_f(), 0.45, 0.6)], r=0.08)


def ax_f():
    return -0.05 - 0.3


def extra_g():
    deck(-2.48, -2.48, -0.75, -1.2, 0.12)
    deck(-0.75, -2.48, 0.55, -1.3, 0.16)
    deck(0.55, -2.48, 2.48, -1.45, 0.1)
    barrels(-2.15, -1.0, 4, 5)
    jbox(-2.3, 0.4, 0.25, 0.6, 0.8)
    reel(-0.2, -0.75, (0, 1, 0))
    vtank(0.1, -0.35, 0.3, 0.75, "teal", nozzle=None)
    vtank(0.35, 1.75, 0.4, 1.4, "lead", bands=(0.5,), top="cast", nozzle=(0.2, 0))
    riser(0.4, 0.9, 1.6, r=0.1, mat="copper")
    riser(-2.35, 1.6, 2.0, r=0.1)
    riser(2.35, 2.3, 1.6, r=0.09)
    vtank(2.15, 1.05, 0.25, 0.9, "plate", nozzle=None)
    barrels(1.2, 0.2, 3, 6)
    barrels(0.0, -2.25, 2, 7, z=0.16)
    jbox(1.55, -1.6, 0.4, 0.25, 0.4, z=0.1)
    jbox(2.35, -2.3, 0.2, 0.3, 0.45, z=0.1)
    valve(-1.3, -0.95, 0.0, 0.6)
    lagged([(-2.3, -2.2, 0.55), (-2.3, -1.5, 0.6), (-1.9, -0.3, 0.45), (-1.6, 0.0, 0.5)], r=0.1)
    hose([(0.35, 1.75, 1.66), (0.2, 1.2, 1.9), (-0.1, 0.9, 2.3)], r=0.085)


def extra_h():
    deck(-2.48, -2.48, -0.6, -1.2, 0.12)
    deck(-0.6, -2.48, 2.48, -1.3, 0.14)
    deck(-1.0, -1.2, 0.3, 0.05, 0.1, stripe=False)
    barrels(-1.95, -0.65, 5, 8)
    reel(-1.2, -0.9, (1, 0, 0))
    jbox(-0.7, -0.3, 0.35, 0.3, 0.55, z=0.1)
    exchanger(-0.1, 1.05, 0.45, 0.42, 0.3, mat="plate")
    vtank(0.35, 1.0, 0.25, 0.75, "teal", nozzle=None)
    riser(-2.35, 2.35, 1.8, r=0.1, mat="copper")
    riser(-2.1, 0.3, 1.4, r=0.08)
    riser(2.35, 0.3, 1.6, r=0.1)
    riser(2.35, 2.35, 1.2, r=0.09, mat="copper")
    vtank(2.2, -0.3, 0.22, 0.8, "plate", nozzle=None)
    barrels(0.6, -2.2, 3, 9, z=0.14)
    jbox(-0.75, -2.3, 0.3, 0.2, 0.4, z=0.12)
    valve(-0.2, -1.55, 0.14, 0.5)
    lagged([(-2.1, -2.3, 0.5), (-2.15, -1.6, 0.55), (-1.9, -1.2, 0.5)], r=0.1)
    hose([(0.35, 1.0, 0.85), (0.0, 0.9, 1.3), (cx_h() + 0.5, 0.95, 1.6)], r=0.085, mat="hose_k")


def cx_h():
    return -1.05


def extra_i():
    deck(-2.48, -2.48, 2.48, -1.95, 0.1)
    deck(1.0, -1.95, 2.48, -0.9, 0.12, stripe=False)
    barrels(-1.6, 0.3, 4, 10)
    jbox(-2.3, 0.2, 0.25, 0.5, 0.7)
    exchanger(-1.3, 0.35, -0.2, 0.42, 0.3, mat="shell")
    vtank(0.35, 1.85, 0.36, 1.1, "teal", bands=(0.4,), nozzle=None)
    riser(-1.05, 2.35, 1.6, r=0.1, mat="copper")
    riser(0.85, 2.35, 1.2, r=0.09)
    riser(2.35, 1.5, 1.8, r=0.1)
    riser(2.35, -0.95, 1.2, r=0.08, mat="copper")
    vtank(2.1, -1.4, 0.28, 0.9, "lead", top="cast", nozzle=None)
    barrels(0.4, 0.2, 3, 11)
    for xx in (-2.0, -1.2, -0.4, 0.4):
        jbox(xx, -2.2, 0.3, 0.18, 0.3, z=0.1)
    reel(1.3, -2.15, (1, 0, 0))
    valve(-2.1, -0.9, 0.0, 0.7)
    valve(1.1, -0.2, 0.0, 0.5)
    lagged([(-2.3, -2.2, 0.5), (-2.25, -1.4, 0.5), (-2.1, -0.6, 0.45)], r=0.1)




def rack(x, y, w, d, h, mat="plate"):
    """An instrument rack against an edge: a cabinet column with gauges and a lamp."""
    box((x, y, h / 2), (w, d, h), mat, bevel=0.012)
    for k in range(int(h / 0.35)):
        gauge((x + (w / 2 + 0.01 if w < d else 0), y - (d / 2 + 0.01 if w >= d else 0), 0.3 + 0.35 * k),
              (1 if w < d else 0, -1 if w >= d else 0, 0.2), r=0.05)
    box((x, y, h + 0.03), (w + 0.04, d + 0.04, 0.06), "cast", bevel=0.006)


def extra2_e():
    rack(-2.36, 0.65, 0.22, 1.1, 1.6, "teal")
    rack(-2.36, 1.75, 0.22, 0.6, 1.0)
    rack(2.36, 1.9, 0.22, 0.9, 1.3)
    deck(-0.75, -1.3, 1.55, -0.1, 0.1, stripe=False)
    barrels(1.15, -0.55, 3, 12, z=0.1)
    jbox(-0.45, -0.35, 0.3, 0.25, 0.45, z=0.1)


def extra2_f():
    rack(-2.36, 1.2, 0.22, 0.8, 1.3, "teal")
    rack(-2.36, -1.4, 0.22, 0.9, 0.8)
    rack(2.36, -0.85, 0.22, 0.9, 1.0)
    rack(2.36, 2.0, 0.22, 0.8, 1.2)
    deck(-0.7, -1.25, 2.48, -0.45, 0.1, stripe=False)
    vtank(-0.9, 1.15, 0.28, 0.9, "plate", nozzle=None)
    vtank(-0.75, -0.5, 0.28, 0.75, "shell", nozzle=None)
    barrels(1.35, -0.8, 3, 13, z=0.1)


def extra2_g():
    cyl((-0.8, 0.32, 0.12), 0.62, 0.24, "lead", verts=64)          # sump under the sphere
    box((-0.8, -0.1, 0.12), (0.5, 0.7, 0.24), "cast")
    rack(-2.36, 1.1, 0.22, 1.2, 1.5, "teal")
    rack(-2.36, 2.1, 0.22, 0.6, 1.0)
    rack(2.36, 2.0, 0.22, 0.8, 1.2)
    vtank(-1.85, 1.95, 0.3, 1.1, "shell", nozzle=None)
    deck(-0.1, -1.3, 1.0, 0.1, 0.1, stripe=False)
    barrels(0.6, -0.55, 3, 14, z=0.1)
    jbox(-1.55, -0.45, 0.35, 0.3, 0.5)
    jbox(-0.15, 0.75, 0.3, 0.3, 0.5)
    vtank(-2.05, 0.55, 0.27, 0.85, "plate", bands=(0.35,), nozzle=None)
    deck(-2.48, -1.2, -0.1, -0.3, 0.1, stripe=False)
    jbox(-1.05, -0.7, 0.4, 0.3, 0.45, z=0.1)
    rack(2.36, -0.95, 0.22, 0.8, 1.0)
    rack(2.36, 1.55, 0.22, 0.4, 0.9, "teal")
    jbox(1.3, 0.75, 0.3, 0.3, 0.6)


def extra2_h():
    rack(-2.36, 0.0, 0.22, 1.0, 1.2, "teal")
    rack(-2.36, 1.6, 0.22, 0.9, 1.4)
    rack(2.36, 1.3, 0.22, 0.8, 1.2)
    cellbox(-1.55, -0.05, 0.6, 0.45, 0.32, wheel=False)
    deck(0.0, -1.3, 1.6, 0.1, 0.1, stripe=False)
    barrels(0.9, -0.05, 3, 15, z=0.1)
    jbox(0.75, 1.3, 0.35, 0.3, 0.6)


def extra2_i():
    rack(-2.36, 1.6, 0.22, 1.0, 1.4, "teal")
    rack(-2.36, 0.65, 0.22, 0.7, 1.0)
    rack(2.36, 0.4, 0.22, 0.9, 1.3)
    vtank(-1.0, 0.75, 0.3, 0.9, "plate", nozzle=None)
    vtank(-0.95, 1.85, 0.3, 1.0, "teal", nozzle=None)
    jbox(0.25, 0.85, 0.35, 0.3, 0.6)
    barrels(1.45, -0.6, 3, 16, z=0.12)


BUILD = {"E": option_e, "F": option_f, "G": option_g, "H": option_h, "I": option_i}
BUILD[OPTION]()
{"E": extra2_e, "F": extra2_f, "G": extra2_g, "H": extra2_h, "I": extra2_i}[OPTION]()
{"E": extra_e, "F": extra_f, "G": extra_g, "H": extra_h, "I": extra_i}[OPTION]()

# ---------------------------------------------------------------- lights, passes
rig.camera(*CANVAS, centre_px=CENTRE, ss=SSK)
rig.sun()
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
rig.bounce_ground()


def pose(t):
    for p in ANIM:
        p(t)
    for node, k in PHASES:
        node.outputs[0].default_value = 2 * math.pi * k * t


def working(on):
    for sock, v in GLOWS:
        sock.default_value = v if on else 0.0
    LAMP_ON.default_value = 3.0 if on else 0.0


def show_stubs(direction):
    for o in STUBS:
        bpy.data.objects.remove(o, do_unlink=True)
    STUBS.clear()
    if direction:
        stubs_for(direction)


if ONLY in (None, "idle"):
    show_stubs("N")
    pose(0.0)
    working(False)
    rig.render(os.path.join(OUT, "idle.png"))
    GROUND.hide_render = True          # the mass alone, for the cover measure: no ground shadow
    rig.render(os.path.join(OUT, "mask.png"))
    GROUND.hide_render = False
if ONLY in (None, "working"):
    show_stubs("N")
    working(True)
    for f in range(NF):
        pose(f / NF)
        rig.render(os.path.join(OUT, f"working-{f:02d}.png"))
if DIRS:
    working(False)
    pose(0.0)
    for d in "NESW":
        show_stubs(d)
        rig.render(os.path.join(OUT, f"dir-{d}.png"))
print("done", OPTION)
