"""Reaction Plant redesign, options round: four lit blockouts, one per option.

  $BLENDER -b --python options_blockout.py -- <out-dir> <A|B|C|D> [--frames N] [--quick]
           [--dirs] [--only working|idle]

Writes into <out-dir>/<option>/, at 4x sprite size (rig.SS) on a 352 x 384 sprite
canvas with the entity origin at (160, 240):

  working-NN.png  the machine running, frame NN of the signature loop (N frames,
                  default 24), the input stubs drawn for a north-facing plant
  idle.png        the same, stopped and unlit, at frame 0
  dir-<N|E|S|W>.png  with --dirs: idle, with the engine's stubs where a plant
                  facing that way has them (two inputs on the faced side, the
                  dormant output opposite drawn as a cover) -- the one plate under
                  rotation

A blockout, not a model: the shared layered finish (tools/blender/materials.py)
on blocked-out forms so the read, the finish and the light are judged, not the
detail count. The stubs are stand-ins for the engine-drawn pipe pictures, in the
plant's own metal. Nothing here is adopted.

Units are tiles; north is +Y; a point (x, y, z) lands about (x, y + z/2) tiles up
the screen from the origin. Every loop is periodic by construction: the fluid's
patterns are driven by a phase that turns a whole number of cycles per loop,
bubbles and flecks wrap, and the couplings are six-fold and turn 60 degrees.
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
from materials import layered, hazard_pattern  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR, OPTION = argv[0], argv[1].upper()
QUICK = "--quick" in argv
DIRS = "--dirs" in argv
NF = int(argv[argv.index("--frames") + 1]) if "--frames" in argv else 24
ONLY = argv[argv.index("--only") + 1] if "--only" in argv else None
OUT = os.path.join(OUT_DIR, OPTION)
os.makedirs(OUT, exist_ok=True)

CANVAS = (352, 384)
CENTRE = (160, 240)

sc = rig.reset()
sc.cycles.samples = 20 if QUICK else 64
ROOT = rig.turntable(rig.stretch_root())


def swatch(name):
    return os.path.join(HERE, "..", "model", "swatches", f"concept_{name}.png")


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
    bpy.ops.object.transform_apply(scale=True)
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
    x = d[0] * 1.36 + (tile if d[1] else 0)
    y = d[1] * 1.36 + (tile if d[0] else 0)
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
    """Inputs on the faced side at tiles -1 and +1, the output opposite at 0 (spec 2)."""
    face = direction
    opp = {"N": "S", "S": "N", "E": "W", "W": "E"}[face]
    port_stub(face, -1)
    port_stub(face, 1)
    port_stub(opp, 0, cover=True)


def status_lamp(x, y, z):
    cyl((x, y, z), 0.045, 0.05, "cast", verts=16)
    sphere((x, y, z + 0.035), 0.032, "lamp", seg=12)


# ======================================================================= options
def valve(x, y, z=0.0, h=0.42, r=0.07):
    """A standing gate valve: body, bonnet, stem and handwheel."""
    cyl((x, y, z + 0.1), r * 1.3, 0.2, "cast", verts=20)
    cyl((x, y, z + 0.1 + h * 0.4), r * 0.7, h * 0.5, "steel", verts=16)
    handwheel((x, y, z + h), 0.085)


def drum_ns(x, y0, y1, z, r, mat="plate", bands=(), saddles=()):
    """A drum lying north-south on saddles, with dished ends."""
    L = y1 - y0
    cyl((x, (y0 + y1) / 2, z), r, L, mat, rot=(math.pi / 2, 0, 0), verts=48)
    for yy, s in ((y0, -1), (y1, 1)):
        h = head(x, yy, z, r, 0.13, mat)
        h.rotation_euler = (-s * math.pi / 2, 0, 0)
    for yy in bands:
        cyl((x, yy, z), r + 0.025, 0.07, "lead", rot=(math.pi / 2, 0, 0), verts=48)
    for yy in saddles:
        box((x, yy, (z - r * 0.5) / 2 + 0.02), (r * 1.6, 0.12, z - r * 0.5 + 0.04), "cast")


def option_a():
    """THE SIGHT COLUMN. A tall banded precipitation column in the back-left corner,
    its middle a strapped glass barrel where the blue solution swirls and bubbles;
    a low run of plant down the right flank and across the front (a gas
    conditioning drum, a valve manifold, a pump skid, a lead-lined cell box); fat
    hoses climb from the low plant to the column's flanges."""
    cx, cy, R = -0.66, 0.56, 0.64
    cyl((cx, cy, 0.08), R + 0.1, 0.16, "cast", verts=64)
    cyl((cx, cy, 0.46), R, 0.62, "shell", verts=64)
    band(cx, cy, 0.26, R)
    band(cx, cy, 0.58, R, lug_a=-math.pi / 3)
    fz0, fz1 = 0.82, 1.9
    flange_ring(cx, cy, fz0 - 0.04, R)
    flange_ring(cx, cy, fz1 + 0.01, R)
    cyl((cx, cy, (fz0 + fz1) / 2), R - 0.005, fz1 - fz0, "glass", verts=64, bevel=0)
    cyl((cx, cy, (fz0 + fz1) / 2), R - 0.07, fz1 - fz0 - 0.02, fluid("fl_a", "flow", scale=4.0, k=1),
        verts=64, bevel=0)
    for i in range(8):
        a = 2 * math.pi * (i + 0.5) / 8
        box((cx + (R + 0.012) * math.cos(a), cy + (R + 0.012) * math.sin(a), (fz0 + fz1) / 2),
            (0.045, 0.045, fz1 - fz0), "steel", rz=a, bevel=0.004)
    bubbles(cx, cy, fz0 + 0.02, fz1 - 0.04, R - 0.04, 26, 7)
    cyl((cx, cy, 2.3), R, 0.76, "shell", verts=64)
    band(cx, cy, 2.06, R, lug_a=-math.pi / 3)
    band(cx, cy, 2.44, R, lug_a=-2 * math.pi / 3)
    head(cx, cy, 2.68, R, 0.24, "lead")
    cyl((cx + 0.18, cy + 0.06, 2.95), 0.1, 0.2, "steel", verts=24)
    flange_ring(cx + 0.18, cy + 0.06, 3.06, 0.09, mat="steel", h=0.04, nb=8)
    cyl((cx - 0.22, cy - 0.14, 2.88), 0.07, 0.14, "brass", verts=6)
    gauge((cx - 0.22, cy - 0.14, 2.98), (0, -0.3, 1))
    box((cx + 0.05, cy - R - 0.01, 2.3), (0.26, 0.05, 0.32), "teal")              # inspection hatch
    for z in (0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4):
        box((cx - R - 0.03, cy - 0.15, z), (0.04, 0.16, 0.025), "steel", bevel=0.004)
    # right flank: gas conditioning drum lying N-S
    dx, dr = 0.95, 0.42
    drum_ns(dx, -0.35, 1.22, 0.56, dr, bands=(0.1, 0.75), saddles=(-0.15, 1.0))
    cyl((dx, 1.0, 1.0), 0.09, 0.14, "steel", verts=24)
    box((dx - 0.05, 0.35, 0.97), (0.24, 0.22, 0.06), "teal")                       # manway cover
    bolts(dx - 0.05, 0.35, 1.0, 0.13, 8, r=0.014)
    # front-left: pump skid, motor, free coupling, volute
    box((-0.72, -1.02, 0.08), (1.25, 0.62, 0.16), "cast")
    box((-1.1, -1.02, 0.36), (0.42, 0.4, 0.4), "teal")
    for i in range(6):
        box((-1.1, -1.02 + 0.06 * (i - 2.5), 0.57), (0.38, 0.02, 0.02), "cast", bevel=0)
    coupling(-0.8, -1.02, 0.36, 0.15, axis=(1, 0, 0))
    cyl((-0.48, -1.02, 0.38), 0.21, 0.24, "cast", rot=(0, math.pi / 2, 0), verts=32)
    cyl((-0.48, -1.02, 0.64), 0.07, 0.14, "steel", verts=16)
    cyl((-0.22, -1.02, 0.38), 0.07, 0.3, "steel", rot=(0, math.pi / 2, 0), verts=16)
    # front-right: lead-lined cell box
    box((0.78, -1.0, 0.3), (0.72, 0.7, 0.6), "lead", bevel=0.02)
    box((0.78, -1.0, 0.615), (0.58, 0.54, 0.03), "cast", bevel=0.006)
    bolts(0.78, -1.0, 0.64, 0.27, 12, r=0.014)
    handwheel((0.78, -1.0, 0.7), 0.12)
    box((0.78, -1.36, 0.32), (0.6, 0.02, 0.1), "hazard", bevel=0)
    status_lamp(1.06, -0.75, 0.64)
    # middle: valve manifold on a copper header between the pump, column and drum
    pipe([(-0.22, -1.02, 0.38), (0.0, -0.75, 0.3), (0.05, -0.4, 0.28), (0.4, -0.3, 0.28), (dx - 0.3, -0.25, 0.4)],
         r=0.065, mat="copper")
    for vx, vy in ((0.04, -0.62), (0.3, -0.33), (0.5, -0.3)):
        valve(vx, vy, 0.18, 0.45)
    # hoses
    hose([(-0.48, -1.02, 0.72), (-0.45, -0.7, 0.95), (-0.42, -0.2, 0.8), (cx + 0.3, cy - R + 0.03, 0.72)], r=0.09)
    hose([(dx, 1.0, 1.08), (0.75, 1.1, 1.7), (0.1, 0.75, 2.1), (cx + R * 0.72, cy - 0.12, 1.96)], r=0.095)
    hose([(dx - 0.2, 0.0, 0.95), (0.55, 0.1, 1.6), (0.05, 0.3, 2.65), (cx + 0.18, cy + 0.06, 3.1)],
         r=0.08, mat="hose_k")
    hose([(0.78, -0.7, 0.62), (0.5, -0.15, 0.9), (0.0, 0.1, 1.0), (cx + R * 0.85, cy - R * 0.4, fz0 - 0.08)],
         r=0.075)
    lagged([(1.33, 1.3, 0.22), (0.6, 1.33, 0.24), (0.1, 1.25, 0.3), (cx + R + 0.02, cy + 0.25, 0.36)], r=0.11)
    lagged([(1.35, -0.6, 0.2), (1.32, -0.45, 0.3), (dx + 0.25, -0.3, 0.45)], r=0.09)
    bundle([(-1.1, -0.82, 0.5), (-1.3, -0.4, 0.2), (-1.36, 0.2, 0.12), (-1.36, 1.1, 0.12)])
    box((-1.3, -0.25, 0.25), (0.16, 0.3, 0.4), "plate")
    gauge((-1.3, -0.42, 0.36), (0, -1, 0.2), r=0.06)


def option_b():
    """THE KETTLE AND SCRUBBER. A big squat reaction kettle on the front-left, a
    round glass porthole set in a raised well on its lid where the solution turns
    in a vortex; a tall slim crust-gas scrubber in the back-right corner; fat hoses
    arch from the scrubber down into the kettle lid."""
    kx, ky, kr, kh = -0.34, -0.2, 1.02, 0.8
    cyl((kx, ky, 0.07), kr + 0.08, 0.14, "cast", verts=72)
    cyl((kx, ky, kh / 2 + 0.07), kr, kh - 0.14, "shell", verts=72)
    band(kx, ky, 0.3, kr, lugs=3)
    band(kx, ky, 0.62, kr, lugs=3, lug_a=-math.pi / 6)
    lz = kh
    cyl((kx, ky, lz + 0.03), kr + 0.03, 0.06, "cast", verts=72)
    bolts(kx, ky, lz + 0.07, kr - 0.03, 30, r=0.018)
    head(kx, ky, lz + 0.06, kr - 0.02, 0.12, "plate")
    px, py, pr = kx + 0.06, ky - 0.22, 0.46
    pz = lz + 0.26
    annulus((px, py, pz - 0.06), pr, pr + 0.08, 0.2, "shell")
    annulus((px, py, pz + 0.04), pr - 0.02, pr + 0.11, 0.06, "cast")
    bolts(px, py, pz + 0.075, pr + 0.065, 18, r=0.02)
    cyl((px, py, pz + 0.02), pr, 0.03, "glass", verts=64, bevel=0)
    cyl((px, py, pz - 0.06), pr, 0.04, fluid("fl_b", "swirl", scale=3.5, k=3, arms=3), verts=64, bevel=0)
    box((px, py, pz + 0.06), (2 * pr + 0.04, 0.05, 0.03), "steel", bevel=0.004)
    # flecks circling in the vortex, just under the glass
    rnd = random.Random(5)
    fl = []
    for i in range(16):
        o = sphere((0, 0, 0), rnd.uniform(0.012, 0.02), "bubble", seg=8)
        fl.append((o, rnd.uniform(0.08, pr - 0.05), rnd.random()))

    def pose(t):
        for o, rr, ph in fl:
            a = 2 * math.pi * (ph + t / 3)          # a third of a turn a loop: the 3-arm swirl's period
            o.location = (px + rr * math.cos(a), py + rr * math.sin(a), pz - 0.035)
    ANIM.append(pose)
    # agitator drive beside the porthole
    mx, my = kx - 0.5, ky + 0.42
    cyl((mx, my, lz + 0.22), 0.14, 0.16, "cast", verts=32)
    coupling(mx, my, lz + 0.34, 0.13)
    box((mx - 0.02, my + 0.27, lz + 0.38), (0.34, 0.28, 0.34), "teal")
    for i in range(4):
        box((mx - 0.02, my + 0.27 + 0.055 * (i - 1.5), lz + 0.56), (0.3, 0.02, 0.02), "cast", bevel=0)
    status_lamp(kx + 0.58, ky + 0.4, lz + 0.2)
    gauge((kx + 0.55, ky - 0.6, lz + 0.14), (0.3, -0.5, 1))
    # scrubber, back-right
    sx, sy, sr = 0.92, 0.88, 0.42
    cyl((sx, sy, 0.06), sr + 0.08, 0.12, "cast", verts=48)
    cyl((sx, sy, 1.36), sr, 2.5, "plate", verts=48)
    for z in (0.35, 0.85, 1.35, 1.85, 2.3):
        band(sx, sy, z, sr, h=0.06, lug_a=-math.pi * 0.75)
    head(sx, sy, 2.61, sr, 0.16, "lead")
    cyl((sx, sy, 2.8), 0.07, 0.12, "steel", verts=20)
    for z in (0.5, 0.8, 1.1, 1.4, 1.7, 2.0, 2.3):
        box((sx + sr + 0.03, sy - 0.12, z), (0.04, 0.14, 0.025), "steel", bevel=0.004)
    # gas receiver on the east flank
    cyl((1.12, 0.12, 0.5), 0.26, 0.9, "shell", verts=40)
    head(1.12, 0.12, 0.95, 0.26, 0.1, "lead")
    band(1.12, 0.12, 0.3, 0.26)
    gauge((1.12, -0.16, 0.7), (0, -1, 0.3), r=0.06)
    # hoses
    hose([(sx - 0.12, sy - 0.32, 2.1), (0.5, 0.35, 2.1), (0.15, 0.15, 1.45), (kx + 0.42, ky + 0.36, lz + 0.24)], r=0.1)
    hose([(sx - 0.34, sy - 0.12, 1.3), (0.25, 0.68, 1.35), (-0.15, 0.58, 1.2), (kx - 0.05, ky + 0.66, lz + 0.18)],
         r=0.085, mat="hose_k")
    cyl((kx + 0.42, ky + 0.36, lz + 0.15), 0.11, 0.12, "steel", verts=20)
    cyl((kx - 0.05, ky + 0.66, lz + 0.1), 0.1, 0.1, "steel", verts=20)
    hose([(1.12, 0.12, 1.02), (1.0, 0.3, 1.5), (sx - 0.1, sy - 0.4, 1.6)], r=0.07)
    # front-right: pump skid feeding the kettle
    box((0.98, -0.95, 0.08), (0.62, 0.85, 0.16), "cast")
    box((0.98, -1.2, 0.33), (0.38, 0.34, 0.34), "plate")
    coupling(0.98, -0.95, 0.33, 0.14, axis=(0, 1, 0))
    cyl((0.98, -0.68, 0.34), 0.2, 0.22, "cast", rot=(math.pi / 2, 0, 0), verts=32)
    hose([(0.98, -0.68, 0.58), (0.95, -0.4, 0.85), (0.72, -0.2, 0.62), (kx + kr, ky + 0.04, 0.48)], r=0.085)
    hose([(1.12, -0.2, 0.35), (1.18, -0.45, 0.4), (1.1, -0.68, 0.34)], r=0.07, mat="hose_k")
    # back-left: cell filter press
    box((-0.95, 1.08, 0.1), (0.85, 0.56, 0.2), "cast")
    for i in range(7):
        box((-1.28 + 0.1 * i, 1.08, 0.42), (0.075, 0.46, 0.44), "lead" if i % 2 else "plate", bevel=0.006)
    box((-0.52, 1.08, 0.42), (0.1, 0.5, 0.5), "cast")
    handwheel((-0.44, 1.08, 0.45), 0.12, axis=(1, 0, 0))
    lagged([(-1.36, 0.65, 0.22), (-1.35, 0.25, 0.28), (kx - kr + 0.05, ky + 0.3, 0.36)], r=0.1)
    pipe([(sx - 0.3, sy - 0.25, 0.4), (0.2, 0.55, 0.35), (kx + 0.5, ky + 0.72, 0.35)], r=0.065, mat="copper")
    pipe([(-0.52, 0.8, 0.3), (-0.4, 0.62, 0.45), (kx - 0.1, ky + 0.85, lz + 0.05)], r=0.055, mat="copper")
    bundle([(mx - 0.02, my + 0.42, lz + 0.3), (-0.95, 0.7, 0.62), (-1.36, 0.85, 0.2), (-1.38, 1.38, 0.1)])


def option_c():
    """THE SETTLING TUBE. A long horizontal glass settling tube across the front,
    cradled and hooped in lead, where the blue solution runs and the precipitate
    drifts down; a tall reactor tower in the back-left corner and a mid-height gas
    conditioner back-right, bridged by a lagged crossover; fat hoses drop from both
    into the tube's ends."""
    ty, tz, tr = -0.76, 0.52, 0.34
    x0, x1 = -1.18, 1.02
    L = x1 - x0
    xm = (x0 + x1) / 2
    for xx in (x0 + 0.28, xm, x1 - 0.28):
        box((xx, ty, 0.16), (0.12, 0.66, 0.32), "cast")
        box((xx, ty, 0.04), (0.22, 0.74, 0.08), "cast")
    cyl((xm, ty, tz), tr, L, "glass", rot=(0, math.pi / 2, 0), verts=48, bevel=0)
    cyl((xm, ty, tz), tr - 0.05, L - 0.02, fluid("fl_c", "flow", scale=2.6, k=2), rot=(0, math.pi / 2, 0),
        verts=48, bevel=0)
    for xx in [x0 + 0.05 + i * (L - 0.1) / 5 for i in range(6)]:
        cyl((xx, ty, tz), tr + 0.035, 0.075, "lead", rot=(0, math.pi / 2, 0), verts=48)
    for xx, s in ((x0, -1), (x1, 1)):
        cyl((xx + s * 0.03, ty, tz), tr + 0.07, 0.07, "cast", rot=(0, math.pi / 2, 0), verts=48)
        h = head(xx + s * 0.06, ty, tz, tr + 0.02, 0.14, "plate")
        h.rotation_euler = (0, s * math.pi / 2, 0)
    rnd = random.Random(3)
    fl_objs = []
    for i in range(22):
        o = sphere((0, 0, 0), rnd.uniform(0.012, 0.024), "fleck", scale=(1.6, 1, 0.6), seg=8)
        fl_objs.append((o, rnd.random(), rnd.uniform(-0.9, 0.9)))

    def pose(t):
        for o, ph, a in fl_objs:
            u = (ph + t) % 1.0
            ang = -math.pi / 2 + a - 0.5 * u
            o.location = (x0 + 0.12 + (L - 0.24) * u, ty + (tr - 0.03) * math.cos(ang) * 0.9,
                          tz + (tr - 0.03) * math.sin(ang) * 0.7)
    ANIM.append(pose)
    # tower back-left
    tx, tyy, R = -0.78, 0.66, 0.56
    cyl((tx, tyy, 0.07), R + 0.09, 0.14, "cast", verts=64)
    cyl((tx, tyy, 1.35), R, 2.5, "shell", verts=64)
    for z in (0.4, 0.95, 1.5, 2.05, 2.45):
        band(tx, tyy, z, R, lug_a=-math.pi / 2 + 0.6)
    head(tx, tyy, 2.6, R, 0.2, "lead")
    cyl((tx + 0.1, tyy - 0.1, 2.82), 0.09, 0.14, "steel", verts=24)
    box((tx + 0.14, tyy - R - 0.02, 1.25), (0.24, 0.05, 0.32), "teal")
    gauge((tx - 0.25, tyy - R + 0.06, 0.75), (-0.4, -1, 0.2))
    for z in (0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4):
        box((tx - R - 0.03, tyy + 0.1, z), (0.04, 0.16, 0.025), "steel", bevel=0.004)
    # conditioner back-right
    gx, gy, gr = 0.84, 0.68, 0.5
    cyl((gx, gy, 0.07), gr + 0.08, 0.14, "cast", verts=48)
    cyl((gx, gy, 0.66), gr, 1.08, "plate", verts=48)
    band(gx, gy, 0.45, gr, lug_a=-math.pi / 2 - 0.5)
    band(gx, gy, 0.9, gr, lug_a=-math.pi / 2 - 0.5)
    head(gx, gy, 1.2, gr, 0.15, "plate")
    cyl((gx, gy, 1.38), 0.1, 0.12, "steel", verts=24)
    status_lamp(gx + 0.28, gy - 0.22, 1.28)
    lagged([(gx, gy, 1.44), (gx - 0.05, gy + 0.05, 1.85), (0.0, 0.8, 2.2), (tx + R - 0.05, tyy + 0.05, 2.15)],
           r=0.12)
    hose([(tx + 0.25, tyy - R + 0.06, 0.6), (-0.9, -0.05, 0.95), (x0 - 0.02, ty + 0.1, 1.0),
          (x0 + 0.12, ty, tz + tr + 0.02)], r=0.095)
    hose([(gx - 0.12, gy - gr + 0.03, 0.42), (0.75, 0.0, 0.9), (x1 - 0.05, ty + 0.15, 1.05),
          (x1 - 0.14, ty, tz + tr + 0.02)], r=0.09, mat="hose_k")
    for xx in (x0 + 0.12, x1 - 0.14):
        cyl((xx, ty, tz + tr), 0.11, 0.08, "steel", verts=20)
    # middle: lead-lined drop box with a rotary feeder, fed from the tube's belly
    box((0.06, 0.06, 0.25), (0.7, 0.56, 0.5), "lead", bevel=0.02)
    box((0.06, 0.06, 0.515), (0.56, 0.42, 0.03), "cast", bevel=0.006)
    bolts(0.06, 0.06, 0.54, 0.22, 10, r=0.014)
    coupling(0.06, 0.06, 0.6, 0.13)
    box((0.06, -0.23, 0.27), (0.58, 0.02, 0.1), "hazard", bevel=0)
    pipe([(0.06, -0.24, 0.32), (0.06, -0.38, 0.26), (0.06, ty + tr - 0.02, 0.3)], r=0.08, mat="cast")
    # flanks
    lagged([(1.36, 1.25, 0.2), (1.36, 0.25, 0.22), (1.3, -0.1, 0.26), (x1 + 0.14, ty + 0.12, 0.42)], r=0.1)
    valve(1.25, 0.05, 0.0, 0.5)
    pipe([(-1.36, 1.3, 0.14), (-1.36, 0.2, 0.16), (tx - 0.35, tyy - 0.35, 0.22)], r=0.065, mat="copper")
    box((-1.25, -0.1, 0.28), (0.24, 0.32, 0.56), "plate")
    gauge((-1.25, -0.27, 0.42), (0, -1, 0.2), r=0.06)
    bundle([(gx + 0.3, gy - 0.32, 0.6), (1.1, 0.0, 0.2), (0.6, -0.25, 0.14), (0.38, 0.05, 0.36)])
    bundle([(-1.25, 0.06, 0.5), (-1.0, 0.1, 0.3), (tx - 0.2, tyy - R + 0.05, 0.5)], cols=("black", "yellow"))


def option_d():
    """THE CASCADE. Three vessels step down the diagonal from the back-left corner
    to the front-right -- tall reactor, mid settler, low cell pot -- and the blue
    solution runs between them through short strapped glass pipes, so the light
    flows downhill across the building."""
    V = [(-0.8, 0.76, 0.56, 2.55, "shell"), (0.06, 0.0, 0.52, 1.6, "plate"), (0.9, -0.86, 0.48, 0.8, "shell")]
    for i, (x, y, r, h, m) in enumerate(V):
        cyl((x, y, 0.07), r + 0.08, 0.14, "cast", verts=64)
        cyl((x, y, h / 2 + 0.07), r, h - 0.14, m, verts=64)
        for z in [0.3 + 0.5 * k for k in range(int((h - 0.2) / 0.5))]:
            band(x, y, z, r, lug_a=-math.pi / 2 + 0.7)
        head(x, y, h, r, 0.16, "lead")
        cyl((x, y, h + 0.17), 0.08, 0.12, "steel", verts=20)
        gz0, gz1 = 0.25, h - 0.18
        a = -math.pi / 2 - 0.35
        gx, gy = x + (r + 0.05) * math.cos(a), y + (r + 0.05) * math.sin(a)
        box((gx, gy, (gz0 + gz1) / 2), (0.15, 0.06, gz1 - gz0 + 0.08), "cast", rz=a + math.pi / 2, bevel=0.008)
        cyl((gx + 0.02 * math.cos(a), gy + 0.02 * math.sin(a), (gz0 + gz1) / 2), 0.04, gz1 - gz0, "glass",
            verts=16, bevel=0)
        cyl((gx + 0.02 * math.cos(a), gy + 0.02 * math.sin(a), (gz0 + gz1) / 2), 0.028, gz1 - gz0 - 0.01,
            fluid(f"fl_d{i}", "flow", scale=6.0, k=1, bright=0.8), verts=12, bevel=0)
    runs = [((-0.8 + 0.42, 0.76 - 0.28, 2.1), (0.06 - 0.12, 0.12, 1.66)),
            ((0.06 + 0.36, -0.16, 1.28), (0.9 - 0.12, -0.78, 0.88))]
    for j, (a, b) in enumerate(runs):
        A, B = Vector(a), Vector(b)
        t = (B - A)
        mid = (A + B) / 2
        ln = t.length
        cyl(tuple(mid), 0.12, ln - 0.1, "glass", rot=along(t), verts=32, bevel=0)
        cyl(tuple(mid), 0.09, ln - 0.12, fluid(f"fl_r{j}", "flow", scale=2.0, k=2, bright=1.1), rot=along(t),
            verts=32, bevel=0)
        for u in (0.0, 0.5, 1.0):
            p = A + t * (0.05 + 0.9 * u)
            cyl(tuple(p), 0.145, 0.055, "lead" if u == 0.5 else "cast", rot=along(t), verts=32)
        T, Nn, Bb = frames([A, B])
        for k in range(4):
            ang = 2 * math.pi * k / 4 + 0.4
            off = 0.125 * (math.cos(ang) * Nn[0] + math.sin(ang) * Bb[0])
            cyl(tuple(mid + off), 0.012, ln - 0.1, "steel", rot=along(t), verts=8, bevel=0)
    # NE: gas receiver and feed pump
    cyl((1.08, 1.08, 0.55), 0.28, 1.0, "plate", verts=40)
    head(1.08, 1.08, 1.05, 0.28, 0.1, "lead")
    band(1.08, 1.08, 0.3, 0.28)
    band(1.08, 1.08, 0.75, 0.28)
    box((0.55, 0.95, 0.08), (0.55, 0.55, 0.16), "cast")
    box((0.55, 1.12, 0.3), (0.3, 0.28, 0.28), "teal")
    coupling(0.55, 0.9, 0.3, 0.12, axis=(0, 1, 0))
    cyl((0.55, 0.7, 0.3), 0.16, 0.18, "cast", rot=(math.pi / 2, 0, 0), verts=32)
    hose([(1.08, 1.08, 1.12), (0.8, 1.0, 1.7), (0.0, 1.0, 2.3), (-0.8 + 0.25, 0.76 + 0.1, 2.55 + 0.12)], r=0.095)
    hose([(0.55, 0.7, 0.48), (0.5, 0.42, 0.85), (0.06 + 0.3, 0.2, 1.42)], r=0.08, mat="hose_k")
    hose([(1.25, 0.82, 0.4), (1.3, 0.2, 0.5), (1.25, -0.3, 0.45), (0.9 + 0.4, -0.65, 0.5)], r=0.075)
    # SW: lead-lined cell box and the motor control
    box((-0.88, -0.86, 0.3), (0.76, 0.72, 0.6), "lead", bevel=0.02)
    box((-0.88, -0.86, 0.615), (0.6, 0.56, 0.03), "cast", bevel=0.006)
    bolts(-0.88, -0.86, 0.64, 0.28, 12, r=0.014)
    box((-0.88, -1.23, 0.32), (0.6, 0.02, 0.1), "hazard", bevel=0)
    handwheel((-0.88, -0.86, 0.7), 0.12)
    box((-0.2, -1.12, 0.22), (0.36, 0.3, 0.44), "plate")
    status_lamp(-0.2, -1.12, 0.47)
    gauge((-0.2, -1.28, 0.3), (0, -1, 0.2), r=0.06)
    lagged([(-1.36, 1.3, 0.22), (-1.34, 0.9, 0.3), (-0.8 - 0.55, 0.6, 0.36)], r=0.11)
    lagged([(-1.36, 0.1, 0.2), (-1.3, -0.2, 0.3), (-0.88 - 0.3, -0.5, 0.45)], r=0.09)
    pipe([(0.9 - 0.35, -0.86, 0.3), (0.0, -0.75, 0.3), (-0.5, -0.8, 0.35)], r=0.07, mat="copper")
    hose([(-0.6, -0.55, 0.62), (-0.4, -0.35, 0.95), (0.06 - 0.38, -0.2, 0.75)], r=0.085)
    bundle([(-0.2, -0.98, 0.4), (-0.45, -0.3, 0.15), (-0.5, 0.25, 0.12), (-0.55, 0.45, 0.45)])


BUILD = {"A": option_a, "B": option_b, "C": option_c, "D": option_d}
BUILD[OPTION]()

# ---------------------------------------------------------------- lights, passes
rig.camera(*CANVAS, centre_px=CENTRE)
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
