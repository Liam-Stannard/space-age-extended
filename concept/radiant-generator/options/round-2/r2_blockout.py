"""Radiant Generator, options round 2: five showpiece blockouts, each built round a
signature animation, plus a thumbnail of the stage-4 Radiant Reactor in its language.

  $BLENDER -b --python r2_blockout.py -- <out-dir> <A|B|C|D|E> <mode> [--samples N]

modes:
  hero      4x renders (256 px a tile): working.png (frame 0) and idle.png
  anim      2x renders (128 px a tile): f000.png ... one per frame of the loop, working
  reactor   2x renders: reactor.png, a 2x2 block of Radiant Reactors, working

Every render carries its ground shadow (a shadow catcher in the same pass), on a
transparent film. Canvas, origin and frame count are written to <out-dir>/info.json
so r2_sheets.py can place them. Units are tiles; north is +Y; (x, y, z) lands at
screen (x, y + z/2) tiles from the origin.

Not a model: the lit blockout the options round needs when ChatGPT is not
reachable -- the layered finish (tools/blender/materials.py), the radiant blue as
emission with a light at the core, so the light falls on the machine as it would.
Nothing here is adopted.

Render device: GPU (OptiX, else CUDA) unless SAE_BLENDER_DEVICE=CPU.
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Euler, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import materials  # noqa: E402
import rig  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR, OPTION, MODE = argv[0], argv[1].upper(), argv[2]
SAMPLES = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else None
os.makedirs(OUT_DIR, exist_ok=True)


def use_gpu(sc):
    want = os.environ.get("SAE_BLENDER_DEVICE", "").strip().upper() or "GPU"
    if want == "CPU":
        sc.cycles.device = "CPU"
        print("render device: CPU", flush=True)
        return
    import _cycles
    prefs = bpy.context.preferences.addons["cycles"].preferences
    built = dict(zip(("CUDA", "OPTIX", "HIP", "METAL", "ONEAPI"), _cycles.get_device_types()))
    for backend in ("OPTIX", "CUDA"):
        if not built.get(backend):
            continue
        prefs.compute_device_type = backend
        found = [d for d in prefs.get_devices_for_type(backend) if d.type == backend]
        if not found:
            continue
        for d in prefs.devices:
            d.use = d.type == backend
        sc.cycles.device = "GPU"
        print(f"render device: GPU {backend} on {', '.join(d.name for d in found)}", flush=True)
        return
    sys.exit("render device: GPU asked for, none found; SAE_BLENDER_DEVICE=CPU renders on the CPU")


sc = rig.reset()
use_gpu(sc)
sc.cycles.samples = SAMPLES or (64 if MODE == "hero" else 40)
sc.cycles.max_bounces = 6
STRETCH = rig.stretch_root()
ROOT = rig.turntable(STRETCH)

# ---------------------------------------------------------------- materials

L = materials.layered
M = {
    "body": L("body", "#5C564B", wear=0.3, rust=0.25, dust=0.35),
    "dark": L("dark", "#4A463F", wear=0.25, rust=0.3, ground=0.6),
    "fin": L("fin", "#8A8580", paint_metal=0.5, paint_rough=0.4, wear=0.2, rust=0.15),
    "collar": L("collar", "#3B3B40", wear=0.45, rust=0.2),
    "lead": L("lead", "#6A6A70", paint_metal=0.3, wear=0.3, rust=0.15),
    "teal": L("teal", "#2A7F7A", wear=0.4, rust=0.2),
    "copper": L("copper", "#8A5A32", metal="#C08050", paint_metal=0.8, paint_rough=0.35, wear=0.2, patina=0.35),
    "hose": L("hose", "#2E2C2A", paint_rough=0.8, wear=0.1, rust=0.0),
    "ceramic": L("ceramic", "#B8B0A0", paint_rough=0.35, wear=0.15, rust=0.05, dust=0.5),
}


def plain(name, hexcol, rough=0.3, metal=0.9):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb(hexcol)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


M["mirror"] = plain("mirror", "#8E8B85", 0.32, 0.95)       # collector faces: polished, they catch the blue
M["recess"] = plain("recess", "#141518", 0.8, 0.2)

GLOWS = {}          # name -> (material, strength when working at full)


def glow(name, hexcol, strength, base="#0C1630"):
    if name in GLOWS:                      # one material per name, however many buildings use it
        return GLOWS[name][0]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb(base)
    b.inputs["Roughness"].default_value = 0.35
    b.inputs["Emission Color"].default_value = rig.srgb(hexcol)
    b.inputs["Emission Strength"].default_value = 0.0
    GLOWS[name] = (m, strength)
    M[name] = m
    return m


def set_glow(name, k):
    m, s = GLOWS[name]
    m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = s * k


def wave_glow(name, hexcol, axis, freq, strength, floor=0.15, sharp=4.0):
    """Emission travelling along a world axis: bands at `freq` per tile, moved by the 'phase' value.

    strength * (floor + (1 - floor) * pulse), pulse = ((sin(2pi (freq*s - phase)) + 1) / 2) ** sharp
    """
    if name in M:
        return M[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt, n = m.node_tree, m.node_tree.nodes
    b = n["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#0C1630")
    b.inputs["Roughness"].default_value = 0.3
    b.inputs["Emission Color"].default_value = rig.srgb(hexcol)
    geo = n.new("ShaderNodeNewGeometry")
    sep = n.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    phase = n.new("ShaderNodeValue")
    phase.name = "phase"
    k = n.new("ShaderNodeValue")
    k.name = "k"
    k.outputs[0].default_value = 0.0

    def op(kind, a, bb=None):
        nd = n.new("ShaderNodeMath")
        nd.operation = kind
        for i, v in enumerate((a, bb)):
            if v is None:
                continue
            if isinstance(v, bpy.types.NodeSocket):
                nt.links.new(v, nd.inputs[i])
            else:
                nd.inputs[i].default_value = v
        return nd.outputs[0]

    s = sep.outputs[{"x": 0, "y": 1, "z": 2}[axis]]
    arg = op("MULTIPLY", op("SUBTRACT", op("MULTIPLY", s, freq), phase.outputs[0]), 2 * math.pi)
    pulse = op("POWER", op("MULTIPLY", op("ADD", op("SINE", arg), 1.0), 0.5), sharp)
    lvl = op("ADD", floor, op("MULTIPLY", pulse, 1.0 - floor))
    nt.links.new(op("MULTIPLY", op("MULTIPLY", lvl, strength), k.outputs[0]), b.inputs["Emission Strength"])
    M[name] = m
    return m


def set_wave(name, k, phase):
    n = M[name].node_tree.nodes
    n["k"].outputs[0].default_value = k
    n["phase"].outputs[0].default_value = phase


# the radiant blue, #1F63FF -> #73ADFF
BLUE_DEEP, BLUE_HOT = "#1F63FF", "#73ADFF"

# ---------------------------------------------------------------- geometry helpers

OBJS = []


def _fin(o, m, bevel=0.012, smooth=False, parent=None):
    if isinstance(m, str):
        m = M[m]
    o.data.materials.append(m)
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments, mod.limit_method = bevel, 2, "ANGLE"
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    o.parent = parent or ROOT
    OBJS.append(o)
    return o


def empty(loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new("pivot", None)
    sc.collection.objects.link(e)
    e.parent = parent or ROOT
    e.location = loc
    e.rotation_euler = rot
    return e


def box(loc, size, m, rz=0.0, rot=None, bevel=0.012, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot or (0, 0, rz))
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _fin(o, m, bevel, parent=parent)


def cyl(loc, r, h, m, rot=(0, 0, 0), verts=40, bevel=0.01, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    return _fin(bpy.context.active_object, m, bevel, smooth=True, parent=parent)


def cone(loc, r1, r2, h, m, rot=(0, 0, 0), verts=40, parent=None):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=h, location=loc, rotation=rot)
    return _fin(bpy.context.active_object, m, 0.01, smooth=True, parent=parent)


def sphere(loc, r, m, scale=(1, 1, 1), parent=None, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2)
    o = bpy.context.active_object
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    return _fin(o, m, 0, smooth=True, parent=parent)


def torus(loc, R, r, m, rot=(0, 0, 0), seg=64, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot,
                                     major_segments=seg, minor_segments=10)
    return _fin(bpy.context.active_object, m, 0, smooth=True, parent=parent)


def mesh_obj(name, verts, faces, m, bevel=0.01, parent=None, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    return _fin(o, m, bevel, smooth=smooth, parent=parent)


def loft(lo, hi, z0, z1, m, bevel=0.02, parent=None):
    n = len(lo)
    verts = [(x, y, z0) for x, y in lo] + [(x, y, z1) for x, y in hi]
    faces = [list(reversed(range(n))), list(range(n, 2 * n))]
    faces += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    return mesh_obj("loft", verts, faces, m, bevel, parent)


def octagon(ex, ey, c):
    return [(-ex, -ey + c), (-ex + c, -ey), (ex - c, -ey), (ex, -ey + c),
            (ex, ey - c), (ex - c, ey), (-ex + c, ey), (-ex, ey - c)]


def band(r0, r1, z0, z1, a0, a1, m, seg=12, parent=None, bevel=0.008):
    """A solid sector of a ring: radii r0..r1, heights z0..z1, angles a0..a1 (radians)."""
    verts, faces = [], []
    for i in range(seg + 1):
        a = a0 + (a1 - a0) * i / seg
        c, s = math.cos(a), math.sin(a)
        for r, z in ((r0, z0), (r1, z0), (r1, z1), (r0, z1)):
            verts.append((r * c, r * s, z))
    for i in range(seg):
        for k in range(4):
            a, b = 4 * i + k, 4 * i + (k + 1) % 4
            faces.append((a, b, b + 4, a + 4))
    faces.append((3, 2, 1, 0))
    e = 4 * seg
    faces.append((e, e + 1, e + 2, e + 3))
    return mesh_obj("band", verts, faces, m, bevel, parent, smooth=True)


def tube(points, r, m, parent=None, res=4):
    cu = bpy.data.curves.new("tube", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(points) - 1)
    for p, co in zip(sp.points, points):
        p.co = (*co, 1)
    o = bpy.data.objects.new("tube", cu)
    sc.collection.objects.link(o)
    o.data.materials.append(M[m] if isinstance(m, str) else m)
    o.parent = parent or ROOT
    OBJS.append(o)
    return o


def smooth_path(ctrl, n=24):
    """Catmull-Rom through control points."""
    pts = [Vector(c) for c in ctrl]
    pts = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-2])
    return [tuple(p) for p in out]


def hose(ctrl, r=0.045, m="hose", ribs=True, parent=None):
    """A corrugated hose (vanilla's reactor hoses): a tube with collars every so often."""
    pts = smooth_path(ctrl)
    tube(pts, r, m, parent)
    if ribs:
        acc = 0.0
        for a, b in zip(pts, pts[1:]):
            a, b = Vector(a), Vector(b)
            acc += (b - a).length
            if acc > 0.07:
                acc = 0.0
                q = (b - a).normalized().to_track_quat("Z", "Y").to_euler()
                torus(tuple(a), r * 1.02, r * 0.35, m, rot=tuple(q), seg=12, parent=parent)
    for end in (pts[0], pts[-1]):
        cyl(end, r * 1.6, r * 1.4, "collar", verts=16, parent=parent)


def fins_radial(r0, r1, z0, z1, n, m="fin", skip=(), t=0.03, parent=None):
    for k in range(n):
        a = 2 * math.pi * k / n
        if any(abs((a - s + math.pi) % (2 * math.pi) - math.pi) < w for s, w in skip):
            continue
        r = (r0 + r1) / 2
        box((r * math.cos(a), r * math.sin(a), (z0 + z1) / 2), (r1 - r0, t, z1 - z0), m, rz=a, bevel=0.004,
            parent=parent)


def fin_bank_y(x0, x1, y0, y1, z0, z1, pitch=0.11, t=0.032, m="fin"):
    n = max(1, int((y1 - y0) / pitch))
    for i in range(n + 1):
        y = y0 + i * (y1 - y0) / n
        box(((x0 + x1) / 2, y, (z0 + z1) / 2), (abs(x1 - x0), t, z1 - z0), m, bevel=0.004)


def bolts(cx, cy, z, r, n, size=0.03, parent=None):
    for k in range(n):
        a = 2 * math.pi * k / n
        cyl((cx + r * math.cos(a), cy + r * math.sin(a), z), size, size * 1.2, "collar", verts=8, bevel=0,
            parent=parent)


def hatch(x, y, z, w, d, ports=2, rz=0.0):
    """The fuel hatch: a teal lid with two loading ports (fuel_inventory_size 2)."""
    box((x, y, z + 0.03), (w, d, 0.06), "teal", rz=rz, bevel=0.015)
    c, s = math.cos(rz), math.sin(rz)
    for k in range(ports):
        off = (k - (ports - 1) / 2) * w * 0.45
        px, py = x + off * c, y + off * s
        cyl((px, py, z + 0.09), 0.1, 0.06, "collar", verts=24)
        cyl((px, py, z + 0.121), 0.065, 0.01, "recess", verts=24, bevel=0)


def junction(x, y, z, w=0.22, d=0.16, h=0.18, rz=0.0, m="body"):
    box((x, y, z + h / 2), (w, d, h), m, rz=rz, bevel=0.012)
    box((x, y, z + h + 0.01), (w * 0.8, d * 0.8, 0.02), "collar", rz=rz, bevel=0.004)


def cable_drop(x, y, z, dx, dy, r=0.06):
    """A copper cable trunk off a block, down to the ground."""
    tube(smooth_path([(x, y, z), (x + dx * 0.6, y + dy * 0.6, z - 0.05), (x + dx, y + dy, z * 0.4),
                      (x + dx * 1.05, y + dy * 1.05, 0.02)], n=8), r, "copper")
    cyl((x, y, z), r * 1.7, 0.08, "collar", rot=(math.pi / 2, 0, math.atan2(dy, dx) + math.pi / 2), verts=16)


POINTS = []         # (light, energy at full)


def core_light(loc, energy, radius=0.15, parent=None, colour=BLUE_HOT):
    d = bpy.data.lights.new("core", "POINT")
    d.energy = 0.0
    d.shadow_soft_size = radius
    d.color = rig.srgb(colour)[:3]
    o = bpy.data.objects.new("core", d)
    sc.collection.objects.link(o)
    o.parent = parent or ROOT
    o.location = loc
    POINTS.append((o, energy))
    return o


def set_lights(k_each):
    """k_each: one level for every core light, or a list, one per light."""
    for i, (o, e) in enumerate(POINTS):
        k = k_each[i] if isinstance(k_each, (list, tuple)) else k_each
        o.data.energy = e * k


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ================================================================= A: the Gyre

def option_a(ox=0.0, oy=0.0, s=1.0, reactor=False):
    """An emitter core turning inside counter-rotating shield bands; the light leaks
    through the gaps and sweeps the radiator bed like a lighthouse. 4x4."""
    P = empty((ox, oy, 0))
    P.scale = (s, s, s)
    E = 1.95
    CZ = 1.3                                                                   # the core's height
    loft(octagon(E, E, 0.55), octagon(E - 0.14, E - 0.14, 0.5), 0.0, 0.26, "dark", parent=P)
    # radiator bed: radial fins round the bowl, broken for the magazine (south) and converter (north)
    fins_radial(1.0, 1.78, 0.26, 0.6, 64, skip=((-math.pi / 2, 0.42), (math.pi / 2, 0.36)), parent=P)
    torus((0, 0, 0.6), 1.78, 0.028, "collar", parent=P)                        # tie ring at the fin tips
    # the bowl: low, so the beams clear its lip and fall on the fins
    cyl((0, 0, 0.38), 0.98, 0.24, "body", verts=64, parent=P)
    torus((0, 0, 0.5), 0.97, 0.05, "lead", parent=P)
    bolts(0, 0, 0.54, 0.97, 32, parent=P)
    cyl((0, 0, 0.5), 0.92, 0.02, "mirror", verts=64, bevel=0, parent=P)        # polished dish, catches the core
    # four pylons and the crown bearing
    for q in range(4):
        a = math.pi / 4 + q * math.pi / 2
        c, sn = math.cos(a), math.sin(a)
        box((1.0 * c, 1.0 * sn, 1.15), (0.17, 0.22, 1.5), "lead", rz=a, parent=P)
        box((0.9 * c, 0.9 * sn, 1.95), (0.36, 0.2, 0.16), "lead", rz=a, parent=P)
        box((1.08 * c, 1.08 * sn, 0.56), (0.26, 0.3, 0.2), "collar", rz=a, parent=P)
        for z in (0.9, 1.4):
            box((1.0 * c, 1.0 * sn, z), (0.21, 0.26, 0.06), "collar", rz=a, parent=P)
        hose([(1.06 * c, 1.06 * sn, 1.6), (1.4 * c, 1.4 * sn, 1.2), (1.55 * c, 1.55 * sn, 0.66)], r=0.04,
             parent=P)
    torus((0, 0, 2.0), 0.74, 0.05, "collar", parent=P)
    torus((0, 0, 2.06), 0.74, 0.025, "copper", parent=P)
    # the core: an emitter sphere on a lead spindle, hung from the crown by four tie rods
    cyl((0, 0, 0.8), 0.1, 0.6, "lead", verts=24, parent=P)
    cone((0, 0, 0.98), 0.08, 0.2, 0.14, "collar", parent=P)
    sphere((0, 0, CZ), 0.28, glow("a_core", "#5C9BFF", 2.6, base="#2A3A60"), parent=P)
    for q in range(4):
        a = q * math.pi / 2
        tube([(0.24 * math.cos(a), 0.24 * math.sin(a), CZ + 0.14), (0.7 * math.cos(a), 0.7 * math.sin(a), 1.98)],
             0.016, "copper", parent=P)
    core_light((0, 0, CZ), 600.0 * s * s, 0.1, parent=P)
    # inner band: 4 plates, 58 deg each, turns +90 deg a loop
    inner = empty(parent=P)
    for q in range(4):
        a0 = q * math.pi / 2
        band(0.5, 0.56, CZ - 0.36, CZ + 0.36, a0, a0 + math.radians(58), "lead", parent=inner)
        band(0.555, 0.585, CZ - 0.36, CZ - 0.3, a0, a0 + math.radians(58), "copper", parent=inner)
        band(0.555, 0.585, CZ + 0.3, CZ + 0.36, a0, a0 + math.radians(58), "copper", parent=inner)
    torus((0, 0, CZ - 0.4), 0.53, 0.03, "collar", parent=inner)
    # outer band: 6 plates, 38 deg each, turns -60 deg a loop, lower and wider
    outer = empty(parent=P)
    for q in range(6):
        a0 = q * math.pi / 3
        band(0.7, 0.77, CZ + 0.02, CZ + 0.5, a0, a0 + math.radians(38), "collar", parent=outer)
        band(0.77, 0.79, CZ + 0.22, CZ + 0.3, a0, a0 + math.radians(38), "teal", parent=outer)
    torus((0, 0, CZ + 0.0), 0.74, 0.03, "collar", parent=outer)
    # a tilted gimbal ring, precessing: 3 clamps, 120 deg a loop
    gim = empty(parent=P)
    tilt = empty((0, 0, CZ), (math.radians(24), 0, 0), parent=gim)
    torus((0, 0, 0), 0.64, 0.022, "copper", parent=tilt)
    for q in range(3):
        a = q * 2 * math.pi / 3
        box((0.64 * math.cos(a), 0.64 * math.sin(a), 0), (0.09, 0.11, 0.09), "collar", rz=a, parent=tilt)
    # magazine, south: two ports, teal lid, a chute up into the core; spent drawer beside it
    box((0, -1.55, 0.36), (0.9, 0.6, 0.6), "body", bevel=0.03, parent=P)
    if not reactor:
        hatch(0, -1.6, 0.66, 0.66, 0.4)
    tube(smooth_path([(0, -1.3, 0.62), (0, -1.05, 0.7), (0, -0.85, 0.62)], n=6), 0.07, "lead", parent=P)
    box((0.62, -1.5, 0.2), (0.3, 0.3, 0.3), "lead", parent=P)
    # converter, north: finned block, copper trunks to the ground
    box((0, 1.52, 0.42), (1.1, 0.62, 0.74), "body", bevel=0.03, parent=P)
    for i in range(7):
        box((-0.42 + i * 0.14, 1.52, 0.86), (0.035, 0.5, 0.18), "fin", bevel=0.004, parent=P)
    if not reactor:
        for x in (-0.38, 0.0, 0.38):
            cable_drop(x, 1.84, 0.32, 0, 0.18)
        hose([(-0.98, 0.98, 1.3), (-0.9, 1.3, 1.0), (-0.45, 1.5, 0.8)], parent=P)
        hose([(0.98, 0.98, 1.3), (0.9, 1.3, 1.0), (0.45, 1.5, 0.8)], parent=P)
        junction(-1.3, -1.25, 0.26)
        junction(1.35, 1.25, 0.26, rz=0.4)

    def animate(ph, working):
        inner.rotation_euler.z = ph * math.pi / 2 if working else 0.0
        outer.rotation_euler.z = -ph * math.pi / 3 if working else math.radians(20)
        gim.rotation_euler.z = ph * 2 * math.pi / 3 if working else 0.0
        return (0.85 + 0.15 * math.sin(2 * math.pi * 2 * ph)) if working else 0.0
    return animate


# ================================================================= B: the Lotus

def petal(pivot, L_=1.3, w0=0.62, w1=0.14, cup=0.12, thick=0.045):
    """A collector petal on its hinge pivot: inner face polished (toward -Y), back armoured and ribbed."""
    nu, nv = 6, 8
    verts, faces = [], []
    for j in range(nv + 1):
        v = j / nv
        w = w0 + (w1 - w0) * v ** 1.3
        for i in range(nu + 1):
            u = -1 + 2 * i / nu
            y = -cup * (1 - u * u) * (1 - 0.5 * v)        # cupped toward the centre
            verts.append((u * w / 2, -y - cup, L_ * v))
    for j in range(nv):
        for i in range(nu):
            a = j * (nu + 1) + i
            faces.append((a, a + nu + 1, a + nu + 2, a + 1))     # normals toward -Y (inner)
    o = mesh_obj("petal", verts, faces, "mirror", bevel=0, parent=pivot, smooth=True)
    o.data.materials.append(M["lead"])
    sol = o.modifiers.new("solid", "SOLIDIFY")
    sol.thickness = thick
    sol.offset = 1.0                 # shell outward (+Y): the original faces stay the polished inner face
    sol.material_offset = 1
    sol.material_offset_rim = 1
    # ribs on the back: the petals are the radiators
    for i in (-1, 0, 1):
        x = i * w0 * 0.28
        box((x * 0.9, 0.04, L_ * 0.42), (0.035, 0.07, L_ * 0.72), "fin", rot=(0, 0, 0), bevel=0.004,
            parent=pivot)
    box((0, 0.03, 0.06), (w0 * 0.8, 0.08, 0.1), "collar", bevel=0.01, parent=pivot)      # root clamp
    cyl((0, -0.02, 0.0), 0.05, w0 * 0.9, "lead", rot=(0, math.pi / 2, 0), verts=16, parent=pivot)  # knuckle
    return o


def option_b(ox=0.0, oy=0.0, s=1.0, reactor=False):
    """Eight collector petals round a radiant pool: a shielded bud when idle, an open
    flower that breathes when working, the inner faces catching the blue. 4x4."""
    P = empty((ox, oy, 0))
    P.scale = (s, s, s)
    E = 1.95
    loft(octagon(E, E, 0.6), octagon(E - 0.14, E - 0.14, 0.55), 0.0, 0.24, "dark", parent=P)
    cyl((0, 0, 0.36), 1.3, 0.24, "body", verts=64, parent=P)
    torus((0, 0, 0.48), 1.3, 0.05, "lead", parent=P)
    bolts(0, 0, 0.5, 1.22, 40, parent=P)
    cyl((0, 0, 0.5), 0.96, 0.06, "collar", verts=64, parent=P)
    cyl((0, 0, 0.545), 0.78, 0.02, glow("b_pool", BLUE_DEEP, 0.6, base="#0E1A3A"), verts=64, bevel=0, parent=P)
    for r in (0.3, 0.55):
        torus((0, 0, 0.565), r, 0.02, glow("b_ring", BLUE_HOT, 3.0), seg=48, parent=P)
    # the emitter spindle rising out of the pool, lead-ringed
    cone((0, 0, 0.62), 0.24, 0.14, 0.16, "collar", parent=P)
    cyl((0, 0, 1.0), 0.13, 0.66, glow("b_core", "#5C9BFF", 3.0, base="#2A3A60"), verts=24, parent=P)
    for z in (0.78, 1.02, 1.24):
        torus((0, 0, z), 0.15, 0.03, "lead", seg=24, parent=P)
    cone((0, 0, 1.38), 0.16, 0.05, 0.14, "lead", parent=P)
    core_light((0, 0, 1.0), 500.0 * s * s, 0.2, parent=P)
    pivots = []
    n = 12 if reactor else 8
    for k in range(n):
        a = 2 * math.pi * k / n
        pv = empty((0.86 * math.cos(a), 0.86 * math.sin(a), 0.56), parent=P)
        pv.rotation_euler = (0, 0, a - math.pi / 2)     # local +Y points outward
        petal(pv, w0=0.66 if not reactor else 0.46)
        pivots.append(pv)
    # outer skirt clutter: hinge drive housings between petals (gear boxes, not pistons)
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n
        box((1.08 * math.cos(a), 1.08 * math.sin(a), 0.56), (0.16, 0.2, 0.14), "collar", rz=a, parent=P)
    if not reactor:
        # magazine south-east, spent drawer, converter north-west; hoses round the skirt
        box((1.25, -1.25, 0.32), (0.62, 0.52, 0.5), "body", rz=math.pi / 4, bevel=0.03)
        hatch(1.25, -1.25, 0.57, 0.5, 0.36, rz=math.pi / 4)
        box((-1.25, 1.25, 0.38), (0.7, 0.55, 0.6), "body", rz=math.pi / 4, bevel=0.03)
        for i in range(5):
            o = -0.24 + i * 0.12
            box((-1.25 + o * 0.707, 1.25 + o * 0.707, 0.74), (0.03, 0.42, 0.14), "fin", rz=math.pi / 4,
                bevel=0.004)
        cable_drop(-1.5, 1.0, 0.3, -0.2, -0.2)
        cable_drop(-1.0, 1.5, 0.3, -0.2, -0.2)
        hose([(1.0, -1.2, 0.4), (0.6, -1.45, 0.3), (0.0, -1.6, 0.32), (-0.8, -1.4, 0.3), (-1.3, -0.9, 0.3)])
        hose([(1.45, 0.3, 0.3), (1.6, 0.9, 0.28), (1.0, 1.5, 0.3)], r=0.04)
        junction(-1.55, -0.55, 0.24)
        junction(1.6, 0.1, 0.24, rz=0.3)

    def animate(ph, working):
        if working:
            open_ = math.radians(38 + 14 * math.sin(2 * math.pi * ph))
        else:
            open_ = math.radians(-50)
        for i, pv in enumerate(pivots):
            lag = (0.03 * math.sin(2 * math.pi * (ph - i / len(pivots)))) if working else 0.0
            pv.rotation_euler.x = -(open_ + lag)
        return (0.8 + 0.2 * math.sin(2 * math.pi * ph)) if working else 0.0
    return animate


# ================================================================= C: the Arc Spire

ARC_OBJS = []


def arc(p0, p1, rng, jag=0.07, n=9, r=0.022, m="c_arc"):
    p0, p1 = Vector(p0), Vector(p1)
    pts = []
    side = (p1 - p0).cross(Vector((0, 0, 1)))
    side = side.normalized() if side.length > 1e-4 else Vector((1, 0, 0))
    for i in range(n + 1):
        t = i / n
        p = p0.lerp(p1, t)
        if 0 < i < n:
            bow = math.sin(math.pi * t) * 0.12
            p += Vector((rng.uniform(-jag, jag), rng.uniform(-jag, jag), rng.uniform(-jag, jag) + bow))
            p += side * rng.uniform(-jag, jag)
        pts.append(tuple(p))
    o = tube(pts, r, m, res=2)
    ARC_OBJS.append(o)
    return o


def clear_arcs():
    for o in ARC_OBJS:
        OBJS.remove(o)
        bpy.data.objects.remove(o, do_unlink=True)
    ARC_OBJS.clear()


def option_c(ox=0.0, oy=0.0, s=1.0, reactor=False, top=3.1):
    """A radiant plasma column standing in a lead cage on a banded drum, three insulator
    masts round it; blue arcs crawl from the column to the masts, bright bands climb it. 3x3."""
    P = empty((ox, oy, 0))
    P.scale = (s, s, s)
    E = 1.45
    loft(octagon(E, E, 0.42), octagon(E - 0.1, E - 0.1, 0.38), 0.0, 0.22, "dark", parent=P)
    cyl((0, 0, 0.5), 1.08, 0.56, "body", verts=64, parent=P)
    for z in (0.32, 0.66):
        cyl((0, 0, z), 1.12, 0.1, "lead", verts=64, parent=P)
    cyl((0, 0, 0.79), 1.04, 0.03, "body", verts=64, bevel=0, parent=P)
    torus((0, 0, 0.8), 0.9, 0.05, "teal", parent=P)                              # the plant's roof paint, a ring
    torus((0, 0, 0.8), 0.98, 0.04, "collar", parent=P)
    # slots round the drum: the light seen low as well
    for k in range(10):
        a = 2 * math.pi * k / 10 + 0.3
        box((1.1 * math.cos(a), 1.1 * math.sin(a), 0.5), (0.05, 0.16, 0.07), M.get("c_slot") or
            glow("c_slot", BLUE_DEEP, 3.0), rz=a, bevel=0, parent=P)
    # the column: a glowing rod with bands climbing it, in a cage of lead bars and collars
    cyl((0, 0, 0.86), 0.42, 0.14, "collar", verts=48, parent=P)
    cyl((0, 0, 0.98), 0.32, 0.12, "lead", verts=48, parent=P)
    rod = cyl((0, 0, (1.0 + top) / 2), 0.15, top - 1.0, wave_glow("c_rod", "#5C9BFF", "z", 1.2, 4.0, 0.3, 3.0),
              verts=24, bevel=0, parent=P)
    for k in range(4):
        a = 2 * math.pi * k / 4 + math.pi / 4
        box((0.27 * math.cos(a), 0.27 * math.sin(a), (1.0 + top) / 2), (0.05, 0.05, top - 1.0), "lead",
            rz=a, bevel=0.005, parent=P)
    for z in [1.1 + i * (top - 1.3) / 2 for i in range(3)]:
        torus((0, 0, z), 0.28, 0.035, "collar", seg=32, parent=P)
    cyl((0, 0, top + 0.05), 0.34, 0.12, "lead", verts=32, parent=P)
    cone((0, 0, top + 0.2), 0.3, 0.12, 0.18, "lead", parent=P)
    torus((0, 0, top - 0.04), 0.36, 0.03, glow("c_corona", BLUE_HOT, 2.5), seg=32, parent=P)
    core_light((0, 0, (1.0 + top) / 2), 120.0 * s * s, 0.15, parent=P)
    # three insulator masts
    tips = []
    for k in range(3):
        a = 2 * math.pi * k / 3 + math.pi / 6
        c, sn = math.cos(a), math.sin(a)
        R = 0.86
        zt = top - 0.3
        cyl((R * c, R * sn, (0.8 + zt) / 2), 0.07, zt - 0.8, "lead", verts=16, parent=P)
        for i in range(6):
            cyl((R * c, R * sn, 1.05 + i * 0.13), 0.14, 0.05, "ceramic", verts=20, parent=P)
        zt = top - 0.3
        tube([(R * c, R * sn, zt - 0.05), (R * c, R * sn, zt + 0.1), (0.62 * c, 0.62 * sn, zt + 0.16)], 0.05,
             "lead", parent=P)
        sphere((0.58 * c, 0.58 * sn, zt + 0.16), 0.08, "copper", parent=P)
        tips.append((0.52 * c, 0.52 * sn, zt + 0.16))
        box((R * c, R * sn, 0.86), (0.3, 0.3, 0.14), "collar", rz=a, parent=P)
    glow("c_arc", "#8DBBFF", 6.0, base="#8DBBFF")
    if not reactor:
        box((0, -1.2, 0.3), (0.9, 0.4, 0.46), "body", bevel=0.03)
        hatch(0, -1.22, 0.53, 0.6, 0.3)
        box((1.2, 0.6, 0.35), (0.38, 0.8, 0.6), "body", bevel=0.03)
        for i in range(6):
            box((1.2, 0.3 + i * 0.12, 0.7), (0.3, 0.03, 0.12), "fin", bevel=0.004)
        cable_drop(1.38, 0.3, 0.25, 0.12, 0)
        cable_drop(1.38, 0.9, 0.25, 0.12, 0)
        hose([(-1.0, 0.5, 0.6), (-1.3, 0.8, 0.4), (-1.0, 1.25, 0.25)])
        hose([(-0.6, -1.0, 0.7), (-1.15, -0.9, 0.4), (-1.3, -0.4, 0.25)], r=0.04)
        junction(-1.15, 1.1, 0.22)
    state = {"tips": tips, "top": top, "P": P, "s": s, "ox": ox, "oy": oy}

    def animate(ph, working, frame_i=0, seed=0):
        clear_arcs() if not reactor else None
        if not working:
            set_wave("c_rod", 0.0, 0.0)
            return 0.0
        set_wave("c_rod", 1.0, ph * 2)
        rng = random.Random(1000 + frame_i + seed)
        for k, tip in enumerate(tips):
            # each mast throws an arc that walks up and down the column with the loop
            z = 1.3 + (top - 1.9) * (0.5 + 0.5 * math.sin(2 * math.pi * (ph + k / 3)))
            a = math.atan2(tip[1], tip[0]) + rng.uniform(-0.5, 0.5)
            end = (0.16 * math.cos(a), 0.16 * math.sin(a), z)
            o = arc(tip, end, rng)
            o.parent = P
            if rng.random() < 0.45:
                o2 = arc(tip, (0.12 * math.cos(a + 0.6), 0.12 * math.sin(a + 0.6), z + rng.uniform(-0.3, 0.3)),
                         rng, r=0.015)
                o2.parent = P
        return 0.85 + 0.15 * rng.random()
    return animate


# ================================================================= D: the Conduit

def option_d(ox=0.0, oy=0.0, s=1.0, reactor=False):
    """An emitter vault at one end; radiant light runs in pulses along three glazed
    collector channels to the converter at the other, as the fusion generator's plasma
    runs its ducts. 3x5."""
    wave_glow("d_chan", "#5C9BFF", "y", 0.9, 3.2, 0.18, 6.0)
    glow("d_slot", BLUE_HOT, 4.0)
    glow("d_coil", BLUE_HOT, 3.0)
    Lh = 2.42
    loft(octagon(1.45, Lh, 0.3), octagon(1.36, Lh - 0.08, 0.26), 0.0, 0.2, "dark")
    # the vault, south
    VY = -1.45
    cyl((0, VY, 0.42), 0.98, 0.44, "body", verts=64)
    torus((0, VY, 0.64), 0.98, 0.05, "lead")
    sphere((0, VY, 0.64), 0.86, "lead", scale=(1, 1, 0.62))
    for k in range(12):
        a = 2 * math.pi * k / 12
        box((0.92 * math.cos(a), VY + 0.92 * math.sin(a), 0.82), (0.07, 0.24, 0.06), "copper", rz=a, bevel=0.006)
    # oculus: a lit ring and a lead plug on the dome's crown
    torus((0, VY, 1.16), 0.28, 0.04, "d_slot", seg=48)
    cyl((0, VY, 1.17), 0.22, 0.1, "collar", verts=32)
    hatch(0, VY, 1.2, 0.34, 0.22)
    for k in range(8):                                          # slot ring round the drum
        a = 2 * math.pi * k / 8 + math.pi / 8
        if math.sin(a) > 0.5:
            continue
        box((1.0 * math.cos(a), VY + 1.0 * math.sin(a), 0.42), (0.04, 0.22, 0.08), "d_slot", rz=a, bevel=0)
    # the three channels: glass ducts in armoured cradles, windowed between clamps, the
    # centre one raised on the spine
    for x, z in ((-0.72, 0.42), (0.0, 0.7), (0.72, 0.42)):
        y0 = VY + (0.78 if x == 0 else 0.6)
        y1 = 1.58
        ym, ln = (y0 + y1) / 2, y1 - y0
        box((x, ym, (z - 0.1) / 2 + 0.1), (0.26, ln, z - 0.1), "body", bevel=0.02)          # the cradle
        cyl((x, ym, z), 0.085, ln, "d_chan", rot=(math.pi / 2, 0, 0), verts=24, bevel=0)  # the duct
        n = int(ln / 0.3)
        for i in range(n + 1):
            y = y0 + i * ln / n
            cyl((x, y, z), 0.125, 0.07, "lead", rot=(math.pi / 2, 0, 0), verts=24)        # clamps
            if i < n:
                box((x, y + ln / n / 2, z + 0.1), (0.05, ln / n - 0.1, 0.03), "collar", bevel=0.004)  # spine strap
    for sx in (-1, 1):                                       # elbows where the side ducts leave the vault
        tube(smooth_path([(sx * 0.5, VY + 0.7, 0.62), (sx * 0.68, VY + 0.85, 0.48), (sx * 0.72, VY + 1.05, 0.42)],
                         n=8), 0.085, "d_chan")
    # flank radiators between and outside the channels
    for sx in (-1, 1):
        fin_bank_y(sx * 1.05, sx * 1.4, -0.7, 1.4, 0.2, 0.52, pitch=0.1)
        box((sx * 1.4, 0.35, 0.52), (0.04, 2.15, 0.04), "collar", bevel=0.004)
    # the converter, north: receiving coils where each channel lands, finned block
    box((0, 1.95, 0.46), (2.5, 0.8, 0.72), "body", bevel=0.03)
    for x, z in ((-0.78, 0.5), (0.0, 0.76), (0.78, 0.5)):
        for i in range(3):
            torus((x, 1.58 + i * 0.08, z), 0.17, 0.035, "d_coil", rot=(math.pi / 2, 0, 0), seg=24)
            torus((x, 1.62 + i * 0.08, z), 0.19, 0.03, "copper", rot=(math.pi / 2, 0, 0), seg=24)
    for i in range(9):
        box((-0.96 + i * 0.24, 2.05, 0.9), (0.04, 0.55, 0.18), "fin", bevel=0.004)
    for x in (-0.9, -0.3, 0.3, 0.9):
        cable_drop(x, 2.33, 0.3, 0, 0.12)
    # magazine on the vault's west flank, spent drawer east
    box((-1.12, -2.0, 0.3), (0.5, 0.6, 0.5), "body", bevel=0.03)
    hatch(-1.12, -2.0, 0.55, 0.3, 0.44, rz=math.pi / 2)
    tube([(-0.9, -1.85, 0.5), (-0.7, -1.7, 0.62)], 0.06, "lead")
    box((1.12, -2.05, 0.2), (0.34, 0.4, 0.3), "lead")
    hose([(0.95, -0.9, 0.5), (1.2, -0.75, 0.6), (1.25, -0.4, 0.56)], r=0.04)
    hose([(-0.95, -0.9, 0.5), (-1.25, -0.6, 0.62), (-1.22, -0.2, 0.56)], r=0.04)

    def animate(ph, working):
        k = 1.0 if working else 0.0
        set_wave("d_chan", k, ph)
        set_glow("d_slot", k * (0.85 + 0.15 * math.sin(2 * math.pi * ph * 2)))
        # the coils light as a pulse lands: pulse crests reach y ~1.6 at ph where 0.9*1.6 - ph = n
        land = ((0.9 * 1.6 - ph) % 1.0)
        set_glow("d_coil", k * (0.25 + 0.75 * max(0.0, math.cos(2 * math.pi * land)) ** 4))
        return k * (0.85 + 0.15 * math.sin(2 * math.pi * ph * 2))
    return animate


def reactor_d(ox, oy):
    """The Conduit as a reactor: a 5x5 hub vault, channels out to all four sides."""
    wave_glow("d_chan", "#5C9BFF", "y", 0.9, 3.2, 0.18, 6.0)
    glow("d_slot", BLUE_HOT, 4.0)
    glow("d_coil", BLUE_HOT, 3.0)
    P = empty((ox, oy, 0))
    loft(octagon(2.45, 2.45, 0.6), octagon(2.35, 2.35, 0.55), 0.0, 0.22, "dark", parent=P)
    cyl((0, 0, 0.5), 1.25, 0.56, "body", verts=64, parent=P)
    torus((0, 0, 0.78), 1.25, 0.06, "lead", parent=P)
    sphere((0, 0, 0.78), 1.12, "lead", scale=(1, 1, 0.6), parent=P)
    torus((0, 0, 1.45), 0.34, 0.05, "d_slot", seg=48, parent=P)
    cyl((0, 0, 1.46), 0.28, 0.12, "collar", verts=32, parent=P)
    core_light((ox, oy, 0.9), 90.0)
    for q in range(4):
        a = q * math.pi / 2
        c, s_ = math.cos(a), math.sin(a)
        for off in (-0.45, 0.45):
            x0, y0 = 1.2 * c - off * s_, 1.2 * s_ + off * c
            x1, y1 = 2.5 * c - off * s_, 2.5 * s_ + off * c
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            box((mx, my, 0.3), (1.3 if c else 0.4, 0.4 if c else 1.3, 0.4), "body", bevel=0.02, parent=P)
            box((mx, my, 0.52), (1.3 if c else 0.26, 0.26 if c else 1.3, 0.04), "d_chan", bevel=0, parent=P)
        fin_x = 1.8 * math.cos(a + math.pi / 4) * 1.0
        fin_y = 1.8 * math.sin(a + math.pi / 4) * 1.0
        for i in range(7):
            box((fin_x + (i - 3) * 0.1 * (-math.sin(a + math.pi / 4)),
                 fin_y + (i - 3) * 0.1 * math.cos(a + math.pi / 4), 0.45),
                (0.6, 0.03, 0.46), "fin", rz=a + math.pi / 4, bevel=0.004, parent=P)


# ================================================================= E: the Feeder

def option_e(ox=0.0, oy=0.0, s=1.0, reactor=False):
    """A gantry carries a fuel cell from the magazine to the well and lowers it in; the
    iris opens and the well flares, then closes to a steady glow. 3x5."""
    glow("e_pool", BLUE_HOT, 6.0, base="#20305A")
    glow("e_slot", BLUE_HOT, 3.5)
    glow("e_cell", BLUE_HOT, 3.0)
    Lh = 2.42
    loft(octagon(1.45, Lh, 0.3), octagon(1.36, Lh - 0.08, 0.26), 0.0, 0.2, "dark")
    WY = -0.55
    well = empty((0, WY, 0))
    band(0.6, 0.98, 0.2, 0.7, 0, 2 * math.pi, "body", seg=64, parent=well)   # the well: a thick drum round a bore
    band(0.58, 0.61, 0.3, 0.7, 0, 2 * math.pi, "lead", seg=64, parent=well)
    for z in (0.3, 0.62):
        band(0.95, 1.02, z - 0.045, z + 0.045, 0, 2 * math.pi, "lead", seg=64, parent=well)
    for k in range(14):
        a = 2 * math.pi * k / 14
        if math.sin(a) > 0.3:
            continue
        box((1.0 * math.cos(a), WY + 1.0 * math.sin(a), 0.46), (0.04, 0.14, 0.09), "e_slot", rz=a, bevel=0)
    torus((0, WY, 0.71), 0.84, 0.07, "collar")
    torus((0, WY, 0.74), 0.92, 0.04, "teal", seg=64)
    cyl((0, WY, 0.3), 0.6, 0.04, "e_pool", verts=48, bevel=0)                    # the pool at the bore's foot
    core_light((0, WY, 0.45), 500.0, 0.3)
    # the iris: 8 leaves pivoting on the rim
    leaves = []
    for k in range(8):
        a = 2 * math.pi * k / 8
        pv = empty((0.66 * math.cos(a), WY + 0.66 * math.sin(a), 0.74))
        pv.rotation_euler.z = a + math.pi / 2
        mesh_obj("leaf", [(0, 0, 0), (0.0, 0.62, 0), (-0.42, 0.34, 0), (0, 0, 0.03), (0.0, 0.62, 0.03),
                          (-0.42, 0.34, 0.03)],
                 [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], "lead", bevel=0.006, parent=pv)
        leaves.append((pv, a))
    # gantry: rails along both flanks on A-frame posts
    for sx in (-1, 1):
        box((sx * 1.22, 0.0, 1.42), (0.1, 4.6, 0.1), "collar", bevel=0.01)
        box((sx * 1.22, 0.0, 1.5), (0.06, 4.6, 0.05), "copper", bevel=0.005)
        for y in (-2.1, 0.0, 2.1):
            for dy in (-0.2, 0.2):
                tube([(sx * 1.3, y + dy * 1.6, 0.2), (sx * 1.22, y, 1.38)], 0.045, "lead")
            box((sx * 1.3, y, 0.22), (0.2, 0.5, 0.06), "collar")
    bridge = empty((0, 0, 0))
    box((0, 0, 1.52), (2.6, 0.22, 0.14), "body", bevel=0.02, parent=bridge)
    for sx in (-1, 1):
        box((sx * 1.22, 0, 1.56), (0.22, 0.34, 0.16), "collar", parent=bridge)
    box((0, 0, 1.46), (0.34, 0.3, 0.18), "teal", bevel=0.015, parent=bridge)          # the hoist
    grab = empty((0, 0, 0), parent=bridge)
    cable = cyl((0, 0, 0.5), 0.012, 1.0, "collar", verts=8, bevel=0, parent=bridge)
    box((0, 0, 0.0), (0.32, 0.12, 0.06), "lead", parent=grab)
    for sx in (-1, 1):
        box((sx * 0.14, 0, -0.1), (0.04, 0.1, 0.18), "lead", parent=grab)
    cell = empty((0, 0, 0), parent=grab)
    cyl((0, 0, -0.26), 0.12, 0.36, "collar", verts=24, parent=cell)
    for z in (-0.18, -0.3):
        torus((0, 0, z), 0.12, 0.018, "e_cell", seg=24, parent=cell)
    cyl((0, 0, -0.05), 0.08, 0.06, "teal", verts=16, parent=cell)
    # magazine, north: a rack of cells under a teal lid; two ports
    box((0, 1.85, 0.42), (2.1, 0.8, 0.5), "body", bevel=0.03)
    hatch(-0.55, 1.85, 0.67, 0.6, 0.4)
    for i in range(3):
        cyl((0.1 + i * 0.26, 1.85, 0.78), 0.1, 0.22, "collar", verts=20)
        torus((0.1 + i * 0.26, 1.85, 0.8), 0.1, 0.016, "e_cell", seg=20)
    # converter, south
    box((0, -2.0, 0.38), (2.2, 0.75, 0.6), "body", bevel=0.03)
    for i in range(8):
        box((-0.84 + i * 0.24, -2.0, 0.76), (0.04, 0.55, 0.16), "fin", bevel=0.004)
    for x in (-0.6, 0.0, 0.6):
        cable_drop(x, -2.33, 0.3, 0, -0.12)
    hose([(-0.9, -0.1, 0.55), (-1.15, 0.4, 0.4), (-0.95, 1.4, 0.5)])
    hose([(0.9, -1.1, 0.5), (1.15, -1.5, 0.3), (0.95, -1.7, 0.55)], r=0.04)

    YM, YW = 1.85, WY            # magazine, well

    def animate(ph, working):
        if not working:
            bridge.location.y, gz, iris, glow_k, carry = YM, 1.0, 0.0, 0.0, False
        else:
            f = ph * 64
            if f < 8:
                bridge.location.y, gz, carry = YM, 1.0 - 0.3 * math.sin(math.pi * f / 8), f >= 4
            elif f < 24:
                bridge.location.y, gz, carry = YM + (YW - YM) * ease((f - 8) / 16), 1.0, True
            elif f < 28:
                bridge.location.y, gz, carry = YW, 1.0, True
            elif f < 36:
                bridge.location.y, gz, carry = YW, 1.0 - 0.55 * ease((f - 28) / 8), True
            elif f < 44:
                bridge.location.y, gz, carry = YW, 0.45 + 0.55 * ease((f - 36) / 8), False
            elif f < 48:
                bridge.location.y, gz, carry = YW, 1.0, False
            else:
                bridge.location.y, gz, carry = YW + (YM - YW) * ease((f - 48) / 16), 1.0, False
            iris = ease((f - 24) / 4) if f < 44 else 1.0 - ease((f - 44) / 4)
            flare = ease((f - 33) / 3) * (1 - ease((f - 40) / 6)) if 33 <= f < 46 else 0.0
            glow_k = 0.35 + 0.35 * iris + 0.9 * flare
        grab.location.z = 0.42 + gz
        cable.scale.z = max(0.05, (1.42 - grab.location.z) / 1.0)
        cable.location.z = (1.42 + grab.location.z) / 2
        cell.hide_render = not carry
        for pv, a in leaves:
            # the leaves slide straight out into the drum wall: a shutter iris, no rams
            out = 0.42 * iris
            pv.location = (0.66 * math.cos(a) + out * math.cos(a), WY + 0.66 * math.sin(a) + out * math.sin(a),
                           0.74 + 0.02 * iris)
        set_glow("e_pool", min(glow_k, 1.6))
        set_glow("e_slot", min(1.0, glow_k * 1.2))
        set_glow("e_cell", 1.0 if working else 0.0)
        return glow_k
    return animate


# ================================================================= reactors (stage 4 thumbnails)

def reactor_block(opt):
    """A 2x2 block of Radiant Reactors in the option's language, 6x6 each (5x5 for D)."""
    animators = []
    pitch = 5.0 if opt == "D" else 6.0
    for ix in (-0.5, 0.5):
        for iy in (-0.5, 0.5):
            ox, oy = ix * pitch, iy * pitch
            if opt == "A":
                animators.append(option_a(ox, oy, 1.5, reactor=True))
            elif opt == "B":
                animators.append(option_b(ox, oy, 1.5, reactor=True))
            elif opt == "C":
                animators.append(option_c(ox, oy, 1.7, reactor=True, top=3.0))
            elif opt == "D":
                reactor_d(ox, oy)
            elif opt == "E":
                reactor_e(ox, oy)
    # neighbour bridges: the bonus made visible
    for (x0, y0, x1, y1) in ((-pitch / 2, -pitch / 2, pitch / 2, -pitch / 2), (-pitch / 2, pitch / 2, pitch / 2, pitch / 2),
                             (-pitch / 2, -pitch / 2, -pitch / 2, pitch / 2), (pitch / 2, -pitch / 2, pitch / 2, pitch / 2)):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        horiz = abs(x1 - x0) > 0
        if opt == "C":
            # arcs jump the gap between neighbouring spires
            pass
        else:
            box((mx, my, 0.35), (1.2 if horiz else 0.5, 0.5 if horiz else 1.2, 0.4), "body", bevel=0.02)
            box((mx, my, 0.57), (1.0 if horiz else 0.22, 0.22 if horiz else 1.0, 0.04),
                "d_chan" if opt == "D" else M.get("bridge_glow") or glow("bridge_glow", BLUE_HOT, 3.0), bevel=0)
            for d in (-0.4, 0.0, 0.4):
                box((mx + (d if horiz else 0), my + (0 if horiz else d), 0.6),
                    (0.06 if horiz else 0.36, 0.36 if horiz else 0.06, 0.06), "lead", bevel=0.005)
    return animators, pitch


def reactor_e(ox, oy):
    """The Feeder as a reactor: a polar crane turning over a big ringed well. 6x6."""
    glow("e_pool", BLUE_HOT, 6.0, base="#20305A")
    glow("e_slot", BLUE_HOT, 3.5)
    glow("e_cell", BLUE_HOT, 3.0)
    P = empty((ox, oy, 0))
    loft(octagon(2.95, 2.95, 0.8), octagon(2.85, 2.85, 0.75), 0.0, 0.22, "dark", parent=P)
    cyl((0, 0, 0.5), 1.7, 0.6, "body", verts=64, parent=P)
    for z in (0.32, 0.72):
        cyl((0, 0, z), 1.74, 0.1, "lead", verts=64, parent=P)
    torus((0, 0, 0.82), 1.5, 0.08, "collar", parent=P)
    cyl((0, 0, 0.8), 1.42, 0.02, "teal", verts=64, bevel=0, parent=P)
    for k in range(4):
        a = 2 * math.pi * k / 4 + math.pi / 4
        cyl((0.7 * math.cos(a), 0.7 * math.sin(a), 0.82), 0.36, 0.04, "e_pool", verts=40, bevel=0, parent=P)
        torus((0.7 * math.cos(a), 0.7 * math.sin(a), 0.84), 0.4, 0.05, "collar", parent=P)
    core_light((ox, oy, 1.0), 200.0)
    torus((0, 0, 1.9), 2.2, 0.08, "collar", parent=P)
    for k in range(8):
        a = 2 * math.pi * k / 8
        tube([(2.5 * math.cos(a), 2.5 * math.sin(a), 0.2), (2.2 * math.cos(a), 2.2 * math.sin(a), 1.88)], 0.06,
             "lead", parent=P)
    arm = empty((0, 0, 0), (0, 0, 0.6), parent=P)
    box((0, 0, 2.0), (4.4, 0.26, 0.16), "body", parent=arm)
    box((1.0, 0, 1.86), (0.4, 0.34, 0.22), "teal", parent=arm)
    fins_radial(1.8, 2.7, 0.22, 0.55, 72, parent=P)


# ================================================================= scene

BUILDERS = {"A": option_a, "B": option_b, "C": option_c, "D": option_d, "E": option_e}
INFO = {
    #       footprint, canvas tiles (w, h), origin tiles (x, y) from top-left, frames
    "A": dict(foot=(4, 4), canvas=(7.5, 8.5), origin=(3.0, 5.5), frames=48),
    "B": dict(foot=(4, 4), canvas=(7.5, 8.0), origin=(3.0, 5.0), frames=32),
    "C": dict(foot=(3, 3), canvas=(6.5, 8.0), origin=(2.5, 5.6), frames=24),
    "D": dict(foot=(3, 5), canvas=(6.0, 8.5), origin=(2.4, 5.2), frames=32),
    "E": dict(foot=(3, 5), canvas=(6.0, 8.5), origin=(2.4, 5.2), frames=64),
}
info = dict(INFO[OPTION])

rig.sun()
GROUND = rig.ground_catcher(size=40)
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground(size=40)


def camera(canvas, origin, ss):
    w, h = int(canvas[0] * rig.PX_PER_TILE), int(canvas[1] * rig.PX_PER_TILE)
    rig.camera(w, h, centre_px=(origin[0] * rig.PX_PER_TILE, origin[1] * rig.PX_PER_TILE), ss=ss)
    return w, h


def no_shadow_emitters():
    """An emitter casts no shadow: the core lights sit inside them, and would be shut in."""
    lit = {m for m, _ in GLOWS.values()} | {M[n] for n in ("c_rod", "d_chan") if n in M}
    for o in OBJS:
        if o.data and any(sl.material in lit for sl in o.material_slots):
            o.visible_shadow = False


def shoot(path, anim, ph, working, **kw):
    k = anim(ph, working, **kw) if kw else anim(ph, working)
    no_shadow_emitters()
    for name in list(GLOWS):
        if name in ("e_pool", "e_slot", "e_cell", "d_slot", "d_coil"):
            continue                                   # these the animator sets itself
        set_glow(name, k if name != "c_arc" else (1.0 if working else 0.0))
    set_lights(k)
    rig.render(path)


if MODE == "reactor":
    anims, pitch = reactor_block(OPTION)
    size = 2 * (pitch + 1.2)
    info.update(canvas=(size + 1.6, size + 1.4), origin=(size / 2 + 0.2, size / 2 + 1.2), foot=(pitch, pitch),
                block=(2, 2), pitch=pitch)
    camera(info["canvas"], info["origin"], 2)
    sc.cycles.samples = SAMPLES or 48

    def all_anim(ph, working):
        k = 1.0
        for a in anims:
            k = a(ph, working) if OPTION != "C" else a(ph, working, frame_i=0, seed=len(ARC_OBJS))
        return k if OPTION not in ("D", "E") else 1.0
    if OPTION == "D":
        set_wave("d_chan", 1.0, 0.3)
        glow("d_slot", BLUE_HOT, 4.0) if "d_slot" not in GLOWS else None
        set_glow("d_slot", 1.0)
        set_glow("d_coil", 0.5)
    if OPTION == "E":
        set_glow("e_pool", 1.0)
        set_glow("e_slot", 1.0)
        set_glow("e_cell", 1.0)
    if OPTION == "C":
        # arcs between neighbouring spires: the neighbour bonus as light
        glow("c_arc", "#A8CCFF", 14.0, base="#A8CCFF") if "c_arc" not in GLOWS else None
        rng = random.Random(7)
        h, z = pitch / 2, 2.7 * 1.7
        for (a, b) in (((-h + 1.2, -h, z), (h - 1.2, -h, z)), ((-h + 1.2, h, z), (h - 1.2, h, z)),
                       ((-h, -h + 1.2, z), (-h, h - 1.2, z)), ((h, -h + 1.2, z), (h, h - 1.2, z))):
            arc(a, b, rng, jag=0.2, n=14, r=0.03)
            arc(a, b, rng, jag=0.25, n=14, r=0.018)
    shoot(f"{OUT_DIR}/reactor.png", all_anim, 0.0, True)
else:
    anim = BUILDERS[OPTION]()
    N = info["frames"]
    if MODE == "hero":
        camera(info["canvas"], info["origin"], 4)
        kw = {"frame_i": 0} if OPTION == "C" else {}
        shoot(f"{OUT_DIR}/working.png", anim, 0.0 if OPTION != "E" else 34 / 64, True, **kw)
        shoot(f"{OUT_DIR}/idle.png", anim, 0.0, False, **kw)
    elif MODE == "anim":
        camera(info["canvas"], info["origin"], 2)
        for i in range(N):
            kw = {"frame_i": i} if OPTION == "C" else {}
            shoot(f"{OUT_DIR}/f{i:03d}.png", anim, i / N, True, **kw)
        kw = {"frame_i": 0} if OPTION == "C" else {}
        shoot(f"{OUT_DIR}/idle.png", anim, 0.0, False, **kw)

with open(f"{OUT_DIR}/info.json", "w") as f:
    json.dump(dict(info, option=OPTION, mode=MODE, ss={"hero": 4, "anim": 2, "reactor": 2}[MODE]), f)
print("done", OPTION, MODE)
