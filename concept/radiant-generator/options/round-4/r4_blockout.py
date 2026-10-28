"""Radiant Generator, options round 4: bulk and cooling. Round 3's three 5x5 variants
reworked as heavy power plants that have to shed heat, each keeping its signature motion
and light, each with its stage-4 Radiant Reactor block (7x7) linked by a shared corner mast.

  $BLENDER -b --python r4_blockout.py -- <out-dir> <1|2|3> <mode> [--samples N]

modes:
  hero      4x renders (256 px a tile): working.png (frame 0) and idle.png
  anim      2x renders (128 px a tile): f000.png ... one per frame of the loop, working, and idle.png
  reactor   2x renders: reactor.png, a 2x2 block of 7x7 Radiant Reactors, working
  mask      1x flat render of the categories (cooling study): mask.png, frame 0 working

  1  THE GYRE SPIRE   the spire out of the gyre's core, now on a thick shield drum in a ring
                      of sloped radiator banks; four masts on piers among the banks
  2  THE BANDED SPIRE the tiered cage on the Reaction Plant's banded drum, raised and ringed
                      by radiator banks; three masts on piers
  3  THE CROWN        the gyre on a shield drum, its crown and needle raised; the four
                      corner masts stand on the corner pump skids

Cooling (near-vacuum: heat leaves by radiation and coolant, not air): circulation pumps
with motors, expansion tanks, heat-exchanger shells, a ring header on the shield drum,
fat lagged loops and ribbed hoses, and radiator banks (the round-3 fin bed made into
heavy sloped panels with headers along their tops). No orange heat, no steam.

Every object carries a category (o["cat"]) for the mask mode: shield, cool (coolant
plumbing), vessel (tanks and exchanger shells), pump, radiator, mast, light, other.

Round 3's helpers (geometry, glow, lights, the masts, bands, column) are copied in so
round 3 stays as it was. Every render carries its ground shadow on a transparent film.
Canvas, origin and frame count go to <out-dir>/info.json for r4_sheets.py. Units are
tiles; north is +Y; (x, y, z) lands at screen (x, y + z/2) tiles from the origin.

Not a model: a lit blockout for the options round. Nothing here is adopted.
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
CAT = ["other"]     # the category new objects get (round 4: the cooling study's mask pass)


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
    o["cat"] = CAT[0]
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
    o["cat"] = CAT[0]
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


# ================================================================= round 3: materials added

# The masts' porcelain: brown-glazed long-rod insulators, alternating big and small sheds,
# an aluminium grading ring at the head. The turbine's bushings (crust-turbine round 2) are
# short white terminal bushings on a brass box; these are tall, dark, glossy and ringed.
M["glaze"] = plain("glaze", "#45200F", 0.1, 0.0)
M["grading"] = plain("grading", "#BFC2C6", 0.22, 1.0)
M["lagging"] = L("lagging", "#8F8A7E", paint_rough=0.9, wear=0.1, rust=0.05, dust=0.6)
M["brass"] = L("brass", "#7A6232", metal="#B89A50", paint_metal=0.8, paint_rough=0.35, wear=0.2, patina=0.2)
M["red"] = L("red", "#7A2A22", wear=0.4, rust=0.2)

# ================================================================= arcs (round 2's)

ARC_OBJS = []


def arc(p0, p1, rng, jag=0.07, n=9, r=0.022, m="arc", parent=None, bow=0.12):
    p0, p1 = Vector(p0), Vector(p1)
    pts = []
    side = (p1 - p0).cross(Vector((0, 0, 1)))
    side = side.normalized() if side.length > 1e-4 else Vector((1, 0, 0))
    for i in range(n + 1):
        t = i / n
        p = p0.lerp(p1, t)
        if 0 < i < n:
            p += Vector((rng.uniform(-jag, jag), rng.uniform(-jag, jag), rng.uniform(-jag, jag)
                         + math.sin(math.pi * t) * bow))
            p += side * rng.uniform(-jag, jag)
        pts.append(tuple(p))
    o = tube(pts, r, m, res=2, parent=parent)
    ARC_OBJS.append(o)
    return o


def clear_arcs():
    for o in ARC_OBJS:
        OBJS.remove(o)
        bpy.data.objects.remove(o, do_unlink=True)
    ARC_OBJS.clear()


# ================================================================= the shared kit

def mast(base, length, P, tilt=0.0, toward=(0.0, 0.0), arm=0.3, sheds=None, foot=True):
    """A porcelain mast: lead foot, brown-glazed long-rod insulator (big and small sheds
    alternating), aluminium grading ring, copper electrode on an arm reaching `arm` toward
    `toward` (P-local x, y). tilt: lean toward `toward`, radians. Returns the electrode's
    P-local position."""
    bx, by, bz = base
    head = math.atan2(toward[1] - by, toward[0] - bx)
    E = empty((bx, by, bz), (0, 0, 0), parent=P)
    E.rotation_euler = Euler((0, tilt, head), "XYZ")       # local +X points at `toward`, leans in by tilt
    if foot:
        box((0, 0, 0.08), (0.36, 0.36, 0.16), "collar", parent=E)
        cyl((0, 0, 0.19), 0.18, 0.06, "lead", verts=24, parent=E)
        bolts(0, 0, 0.23, 0.14, 6, 0.02, parent=E)
    cyl((0, 0, length / 2), 0.055, length, "lead", verts=16, parent=E)
    z0, z1 = 0.32, length * 0.8
    cyl((0, 0, (z0 + z1) / 2), 0.085, z1 - z0, "glaze", verts=20, parent=E)
    n = sheds or max(5, int((z1 - z0) / 0.125))
    for i in range(n):
        z = z0 + 0.04 + i * (z1 - z0 - 0.08) / (n - 1)
        r = 0.19 if i % 2 == 0 else 0.12
        cone((0, 0, z), r, 0.09, 0.05, "glaze", verts=24, parent=E)
    cyl((0, 0, z0 - 0.04), 0.12, 0.08, "collar", verts=20, parent=E)       # base fitting
    cyl((0, 0, z1 + 0.06), 0.1, 0.12, "collar", verts=20, parent=E)        # head fitting
    torus((0, 0, z1 + 0.16), 0.2, 0.026, "grading", seg=32, parent=E)      # grading ring
    for k in range(3):
        a = 2 * math.pi * k / 3
        tube([(0.09 * math.cos(a), 0.09 * math.sin(a), z1 + 0.1), (0.2 * math.cos(a), 0.2 * math.sin(a), z1 + 0.16)],
             0.012, "grading", parent=E)
    zt = length + 0.02
    tube(smooth_path([(0, 0, z1 + 0.1), (0, 0, zt), (arm * 0.6, 0, zt + 0.06), (arm, 0, zt + 0.02)], n=6), 0.035,
         "copper", parent=E)
    sphere((arm, 0, zt), 0.075, "copper", parent=E)
    # electrode, P-local
    rot = E.rotation_euler.to_matrix()
    tip = Vector((bx, by, bz)) + rot @ Vector((arm + 0.04, 0, zt))
    return tuple(tip)


def shield_bands(cz, P, r_in=0.5, r_out=0.7, h_in=0.72, h_out=0.48, gimbal=True):
    """The Gyre's counter-rotating bands round a point at height cz. Returns (inner, outer, gim)."""
    inner = empty(parent=P)
    for q in range(4):
        a0 = q * math.pi / 2
        band(r_in, r_in + 0.06, cz - h_in / 2, cz + h_in / 2, a0, a0 + math.radians(58), "lead", parent=inner)
        for z in (cz - h_in / 2, cz + h_in / 2 - 0.06):
            band(r_in + 0.055, r_in + 0.085, z, z + 0.06, a0, a0 + math.radians(58), "copper", parent=inner)
    torus((0, 0, cz - h_in / 2 - 0.04), r_in + 0.03, 0.03, "collar", parent=inner)
    outer = empty(parent=P)
    for q in range(6):
        a0 = q * math.pi / 3
        band(r_out, r_out + 0.07, cz - h_out / 2 + 0.1, cz + h_out / 2 + 0.1, a0, a0 + math.radians(38), "collar",
             parent=outer)
        band(r_out + 0.07, r_out + 0.09, cz + 0.06, cz + 0.14, a0, a0 + math.radians(38), "teal", parent=outer)
    torus((0, 0, cz - h_out / 2 + 0.08), r_out + 0.04, 0.03, "collar", parent=outer)
    gim = empty(parent=P)
    if gimbal:
        tilt = empty((0, 0, cz), (math.radians(24), 0, 0), parent=gim)
        torus((0, 0, 0), (r_in + r_out) / 2 + 0.02, 0.022, "copper", parent=tilt)
        for q in range(3):
            a = q * 2 * math.pi / 3
            rr = (r_in + r_out) / 2 + 0.02
            box((rr * math.cos(a), rr * math.sin(a), 0), (0.09, 0.11, 0.09), "collar", rz=a, parent=tilt)
    return inner, outer, gim


def fin_bed(r0, r1, P, skip=(), n=72, z1=0.56):
    """The Gyre's radial radiator bed on a low ring skirt (no full plinth)."""
    cyl((0, 0, 0.1), r1 + 0.04, 0.2, "dark", verts=72, parent=P)
    fins_radial(r0, r1, 0.2, z1, n, skip=skip, parent=P)
    torus((0, 0, z1), r1, 0.028, "collar", parent=P)
    torus((0, 0, z1 * 0.6), r1 + 0.02, 0.02, "collar", parent=P)
    # hold-down lugs round the skirt
    for k in range(16):
        a = 2 * math.pi * k / 16 + 0.1
        if any(abs((a - s + math.pi) % (2 * math.pi) - math.pi) < w for s, w in skip):
            continue
        box(((r1 + 0.05) * math.cos(a), (r1 + 0.05) * math.sin(a), 0.1), (0.14, 0.1, 0.2), "collar", rz=a,
            bevel=0.006, parent=P)


def column(z0, z1, P, name, r=0.15, cage=0.27, collars=3):
    """The Arc Spire's column of light in its lead cage."""
    rod = cyl((0, 0, (z0 + z1) / 2), r, z1 - z0, wave_glow(name, "#5C9BFF", "z", 1.2, 4.0, 0.3, 3.0),
              verts=24, bevel=0, parent=P)
    for k in range(4):
        a = 2 * math.pi * k / 4 + math.pi / 4
        box((cage * math.cos(a), cage * math.sin(a), (z0 + z1) / 2), (0.05, 0.05, z1 - z0), "lead",
            rz=a, bevel=0.005, parent=P)
    for i in range(collars):
        z = z0 + 0.15 + i * (z1 - z0 - 0.3) / max(1, collars - 1)
        torus((0, 0, z), cage + 0.01, 0.035, "collar", seg=32, parent=P)
    return rod


def cap(z, P, name):
    cyl((0, 0, z + 0.06), 0.34, 0.12, "lead", verts=32, parent=P)
    cone((0, 0, z + 0.2), 0.3, 0.1, 0.16, "lead", parent=P)
    sphere((0, 0, z + 0.32), 0.07, "copper", parent=P)
    torus((0, 0, z - 0.03), 0.36, 0.03, glow(name, BLUE_HOT, 2.5), seg=32, parent=P)
    bolts(0, 0, 0.0 + z + 0.13, 0.28, 10, 0.022, parent=P)


def lagged(ctrl, r=0.06, P=None, straps=0.22):
    """A lagged pipe run: insulation wrap (pale, rough) held by straps."""
    pts = smooth_path(ctrl, n=10)
    tube(pts, r, "lagging", parent=P)
    acc = 0.0
    for a, b in zip(pts, pts[1:]):
        a, b = Vector(a), Vector(b)
        acc += (b - a).length
        if acc > straps:
            acc = 0.0
            q = (b - a).normalized().to_track_quat("Z", "Y").to_euler()
            torus(tuple(a), r * 1.03, r * 0.22, "collar", rot=tuple(q), seg=16, parent=P)
    for end in (pts[0], pts[-1]):
        cyl(end, r * 1.5, r * 1.2, "collar", verts=16, parent=P)


def valve(x, y, z, P, rz=0.0):
    cyl((x, y, z), 0.05, 0.16, "collar", verts=12, parent=P)
    torus((x, y, z + 0.1), 0.08, 0.015, "red", seg=16, parent=P)
    box((x, y, z + 0.1), (0.16, 0.02, 0.02), "red", rz=rz, bevel=0, parent=P)


def gauge(x, y, z, P):
    cyl((x, y, z), 0.06, 0.03, "collar", verts=16, parent=P)
    cyl((x, y, z + 0.018), 0.045, 0.01, "ceramic", verts=16, bevel=0, parent=P)


def tank(x, y, z, length, r, rz, P):
    """A horizontal coolant canister on saddles, strapped."""
    c, s = math.cos(rz), math.sin(rz)
    cyl((x, y, z), r, length, "lead", rot=(0, math.pi / 2, rz), verts=32, parent=P)
    for e in (-1, 1):
        sphere((x + e * length / 2 * c, y + e * length / 2 * s, z), r, "lead", scale=(1, 1, 1), parent=P, seg=24)
    for e in (-0.3, 0.3):
        box((x + e * length * c, y + e * length * s, z - r * 0.7), (0.1, r * 2.1, r * 0.8), "collar", rz=rz,
            parent=P)
        torus((x + e * length * c, y + e * length * s, z), r * 1.02, 0.018, "collar",
              rot=(0, math.pi / 2, rz), seg=24, parent=P)
    gauge(x, y, z + r + 0.01, P)


def cell_rack(x, y, P, rz=0.0, n=(3, 2)):
    """The spent-cell rack: lead canisters standing in a frame."""
    c, s = math.cos(rz), math.sin(rz)
    box((x, y, 0.08), (0.62, 0.46, 0.16), "dark", rz=rz, parent=P)
    for i in range(n[0]):
        for j in range(n[1]):
            u, v = (i - (n[0] - 1) / 2) * 0.19, (j - (n[1] - 1) / 2) * 0.19
            px, py = x + u * c - v * s, y + u * s + v * c
            cyl((px, py, 0.3), 0.075, 0.3, "lead", verts=16, parent=P)
            cyl((px, py, 0.46), 0.05, 0.03, "teal", verts=16, parent=P)
    for e in (-1, 1):
        box((x + e * 0.3 * c, y + e * 0.3 * s, 0.32), (0.04, 0.46, 0.04), "collar", rz=rz, parent=P)


def magazine(x, y, P, rz=0.0, chute_to=None):
    """The fuel magazine: two ports under a teal lid (fuel_inventory_size 2), a chute in."""
    box((x, y, 0.32), (0.92, 0.62, 0.64), "body", rz=rz, bevel=0.03, parent=P)
    box((x, y, 0.18), (1.0, 0.7, 0.08), "collar", rz=rz, bevel=0.01, parent=P)
    c, s = math.cos(rz), math.sin(rz)
    box((x, y, 0.67), (0.7, 0.42, 0.06), "teal", rz=rz, bevel=0.015, parent=P)
    for k in (-1, 1):
        px, py = x + k * 0.17 * c, y + k * 0.17 * s
        cyl((px, py, 0.72), 0.1, 0.06, "collar", verts=24, parent=P)
        cyl((px, py, 0.751), 0.065, 0.01, "recess", verts=24, bevel=0, parent=P)
    for k in (-1, 1):                                        # hinge lugs and a warning plate
        box((x + k * 0.4 * c, y + k * 0.4 * s, 0.5), (0.08, 0.66, 0.1), "collar", rz=rz, parent=P)
    if chute_to:
        tube(smooth_path([(x, y, 0.6), ((x + chute_to[0]) / 2, (y + chute_to[1]) / 2, chute_to[2] + 0.15),
                          chute_to], n=6), 0.075, "lead", parent=P)


def converter(x, y, P, rz=0.0, w=0.66, d=1.1, cables=3, side=1):
    """The converter: finned block, copper trunks to the ground on its outer face."""
    c, s = math.cos(rz), math.sin(rz)
    box((x, y, 0.38), (w, d, 0.7), "body", rz=rz, bevel=0.03, parent=P)
    n = int(d / 0.12)
    for i in range(n):
        v = -d / 2 + 0.08 + i * (d - 0.16) / (n - 1)
        box((x - v * s, y + v * c, 0.8), (w * 0.8, 0.03, 0.16), "fin", rz=rz, bevel=0.004, parent=P)
    for i in range(cables):
        v = (i - (cables - 1) / 2) * 0.3
        px, py = x - v * s + side * (w / 2) * c, y + v * c + side * (w / 2) * s
        tube(smooth_path([(px, py, 0.45), (px + side * 0.12 * c, py + side * 0.12 * s, 0.38),
                          (px + side * 0.2 * c, py + side * 0.2 * s, 0.03)], n=6), 0.055, "copper", parent=P)
        cyl((px, py, 0.45), 0.09, 0.08, "collar", rot=(math.pi / 2, 0, rz + math.pi / 2), verts=16, parent=P)
    box((x, y, 0.06), (w + 0.1, d + 0.1, 0.12), "collar", rz=rz, bevel=0.01, parent=P)
    gauge(x + 0.1 * c, y + 0.1 * s, 0.74, P)


def cable_tray(ctrl, P, n=3, r=0.022):
    """A bundle of cables running side by side (copper and black)."""
    pts = smooth_path(ctrl, n=8)
    for i in range(n):
        off = (i - (n - 1) / 2) * 2.4 * r
        sh = []
        for k, p in enumerate(pts):
            a = Vector(pts[max(0, k - 1)])
            b = Vector(pts[min(len(pts) - 1, k + 1)])
            d = (b - a)
            d.z = 0
            side = Vector((-d.y, d.x, 0)).normalized() if d.length > 1e-5 else Vector((1, 0, 0))
            sh.append(tuple(Vector(p) + side * off))
        tube(sh, r, "copper" if i % 2 == 0 else "hose", parent=P)


def breaker(x, y, P, rz=0.0):
    """A breaker cabinet: a tall box, a lever, a cable gland at its foot."""
    box((x, y, 0.3), (0.42, 0.3, 0.6), "body", rz=rz, bevel=0.02, parent=P)
    box((x, y, 0.62), (0.48, 0.36, 0.05), "collar", rz=rz, bevel=0.01, parent=P)
    c, s_ = math.cos(rz), math.sin(rz)
    box((x - 0.16 * s_, y + 0.16 * c, 0.4), (0.05, 0.05, 0.22), "red", rz=rz, bevel=0.004, parent=P)
    for k in (-1, 1):
        cyl((x + k * 0.1 * c, y + k * 0.1 * s_, 0.68), 0.04, 0.08, "copper", verts=12, parent=P)
    gauge(x + 0.08 * c, y + 0.08 * s_, 0.65, P)


def junc(x, y, P, w=0.22, d=0.16, h=0.18, rz=0.0, z=0.0):
    box((x, y, z + h / 2), (w, d, h), "body", rz=rz, bevel=0.012, parent=P)
    box((x, y, z + h + 0.01), (w * 0.8, d * 0.8, 0.02), "collar", rz=rz, bevel=0.004, parent=P)


def reactor_dress(P, corners=False):
    """The reactor thumbnails' dressing: magazine, converter, rack, tank (off the corners if masts stand there)."""
    magazine(0.75, -2.05, P)
    converter(2.08, 0.95, P, side=1, d=0.8, cables=2)
    if corners:
        tank(-2.05, 0.0, 0.28, 0.9, 0.2, math.pi / 2, P)
        cell_rack(-0.7, -2.1, P, n=(2, 2))
    else:
        cell_rack(-1.85, -1.85, P, rz=math.pi / 4)
        tank(1.85, -1.75, 0.28, 0.7, 0.2, -math.pi / 4, P)
        junc(-2.0, 1.0, P, w=0.3, d=0.24, h=0.3)


def corner_dressing(P, which):
    """Clutter for the corners and the edge gaps. which: set of keys to place."""
    if "sw_rack" in which:
        cell_rack(-1.85, -1.85, P, rz=math.pi / 4)
    if "se_tank" in which:
        tank(1.82, -1.82, 0.3, 0.9, 0.22, -math.pi / 4, P)
    if "nw_junction" in which:
        junc(-1.95, 1.75, P, w=0.32, d=0.24, h=0.34, rz=math.pi / 4)
        junc(-1.6, 2.05, P, w=0.24, d=0.18, h=0.22, rz=math.pi / 4 + 0.1)
        valve(-2.15, 1.45, 0.1, P)
    if "ne_lagged" in which:
        lagged([(2.2, 0.9, 0.18), (2.25, 1.6, 0.18), (1.9, 2.1, 0.2), (1.2, 2.35, 0.2), (0.4, 2.35, 0.22)], 0.06, P)
        valve(1.75, 2.25, 0.25, P)
    if "ne_breaker" in which:
        breaker(2.05, 1.45, P, rz=-math.pi / 4)
        cable_tray([(1.85, 1.3, 0.5), (1.6, 1.0, 0.62), (1.45, 0.75, 0.6)], P, n=2)



# ================================================================= round 4: materials added

M["tankpaint"] = L("tankpaint", "#8E8A7F", paint_rough=0.55, wear=0.3, rust=0.2, dust=0.45)
M["motor"] = L("motor", "#2F6E6A", wear=0.35, rust=0.2, dust=0.3)          # the family's teal, on motors
M["steel"] = L("steel", "#5E6266", paint_metal=0.55, paint_rough=0.4, wear=0.3, rust=0.25)
M["panel"] = L("panel", "#9A958B", paint_metal=0.45, paint_rough=0.45, wear=0.25, rust=0.2, dust=0.3)


# ================================================================= the cooling kit

def tag(c):
    CAT[0] = c


def at(x, y, rz, u, v):
    c, s = math.cos(rz), math.sin(rz)
    return x + u * c - v * s, y + u * s + v * c


def flange(loc, r, axis_rot, P, m="collar"):
    cyl(loc, r * 1.45, r * 0.55, m, rot=axis_rot, verts=20, parent=P)


def pipe(pts, r, P, m="steel", flanges=True):
    """A rigid pipe run through `pts` (straight legs), flanged at every joint."""
    tube(pts, r, m, parent=P, res=3)
    if flanges:
        for i, p in enumerate(pts):
            a = Vector(pts[max(0, i - 1)])
            b = Vector(pts[min(len(pts) - 1, i + 1)])
            d = (b - a).normalized() if (b - a).length > 1e-6 else Vector((0, 0, 1))
            q = d.to_track_quat("Z", "Y").to_euler()
            cyl(p, r * 1.5, r * 0.6, "collar", rot=tuple(q), verts=20, parent=P)


def pump(x, y, rz, P, s=1.0, z=0.0, outlet_to=None):
    """A circulation pump: skid, volute, coupling guard, ribbed teal motor, terminal box.
    Local +u runs volute -> motor. Returns the outlet's top point."""
    tag("pump")
    box((x, y, z + 0.07), (1.0 * s, 0.6 * s, 0.14), "dark", rz=rz, bevel=0.015, parent=P)
    for e in (-1, 1):                                           # skid rails
        px, py = at(x, y, rz, 0, e * 0.27 * s)
        box((px, py, z + 0.17), (0.98 * s, 0.06 * s, 0.07), "collar", rz=rz, bevel=0.006, parent=P)
    vx, vy = at(x, y, rz, 0.27 * s, 0)
    rot_u = (0, math.pi / 2, rz)
    cyl((vx, vy, z + 0.42 * s), 0.25 * s, 0.24 * s, "steel", rot=rot_u, verts=32, parent=P)      # volute
    torus((vx, vy, z + 0.42 * s), 0.25 * s, 0.03 * s, "collar", rot=rot_u, seg=32, parent=P)
    box((vx, vy, z + 0.24 * s), (0.3 * s, 0.34 * s, 0.2 * s), "dark", rz=rz, parent=P)            # pedestal
    ix, iy = at(x, y, rz, 0.45 * s, 0)                                                             # suction eye
    cyl((ix, iy, z + 0.42 * s), 0.1 * s, 0.16 * s, "collar", rot=rot_u, verts=20, parent=P)
    cyl((vx, vy, z + 0.75 * s), 0.09 * s, 0.22 * s, "steel", verts=20, parent=P)                  # outlet riser
    cyl((vx, vy, z + 0.87 * s), 0.14 * s, 0.05 * s, "collar", verts=20, parent=P)
    gx, gy = at(x, y, rz, 0.03 * s, 0)
    box((gx, gy, z + 0.4 * s), (0.18 * s, 0.3 * s, 0.26 * s), "red", rz=rz, bevel=0.01, parent=P)  # coupling guard
    mx, my = at(x, y, rz, -0.27 * s, 0)
    cyl((mx, my, z + 0.4 * s), 0.19 * s, 0.4 * s, "motor", rot=rot_u, verts=32, parent=P)          # motor
    for k in range(5):
        rx, ry = at(x, y, rz, (-0.43 + k * 0.08) * s, 0)
        torus((rx, ry, z + 0.4 * s), 0.19 * s, 0.022 * s, "motor", rot=rot_u, seg=28, parent=P)
    ex, ey = at(x, y, rz, -0.49 * s, 0)
    cyl((ex, ey, z + 0.4 * s), 0.14 * s, 0.05 * s, "collar", rot=rot_u, verts=24, parent=P)       # fan cowl
    tx, ty = at(x, y, rz, -0.25 * s, 0)
    box((tx, ty, z + 0.63 * s), (0.16 * s, 0.14 * s, 0.1 * s), "body", rz=rz, bevel=0.008, parent=P)
    tag("other")
    cx, cy = at(x, y, rz, -0.25 * s, -0.36 * s)
    tube(smooth_path([(tx, ty, z + 0.63 * s), (cx, cy, z + 0.5 * s), (cx, cy, z + 0.03)], n=5), 0.025, "hose",
         parent=P)
    tag("other")
    return (vx, vy, z + 0.9 * s)


def exp_tank(x, y, r, h, P, z=0.0, ladder=-2.0):
    """An expansion tank: skirt, shell, domed head, teal bands, manway, ladder, relief valve."""
    tag("vessel")
    cyl((x, y, z + 0.08), r * 1.08, 0.16, "dark", verts=40, parent=P)
    cyl((x, y, z + 0.16 + h / 2), r, h, "tankpaint", verts=48, parent=P)
    sphere((x, y, z + 0.16 + h), r, "tankpaint", scale=(1, 1, 0.45), parent=P, seg=32)
    for zz in (0.3, 0.72):
        torus((x, y, z + 0.16 + h * zz), r * 1.01, 0.022, "motor", seg=40, parent=P)
    torus((x, y, z + 0.16 + h), r * 1.0, 0.03, "collar", seg=40, parent=P)
    mx, my = x + r * math.cos(ladder + 0.9), y + r * math.sin(ladder + 0.9)
    cyl((mx, my, z + 0.16 + h * 0.4), 0.11, 0.06, "collar", rot=(math.pi / 2, 0, ladder + 0.9 + math.pi / 2),
        verts=20, parent=P)
    for e in (-0.07, 0.07):                                                 # ladder rails
        lx, ly = at(x, y, ladder, r + 0.05, e)
        box((lx, ly, z + 0.16 + h / 2), (0.018, 0.018, h), "collar", rz=ladder, bevel=0, parent=P)
    for k in range(int(h / 0.12)):
        lx, ly = at(x, y, ladder, r + 0.05, 0)
        box((lx, ly, z + 0.25 + k * 0.12), (0.016, 0.15, 0.014), "collar", rz=ladder, bevel=0, parent=P)
    cyl((x, y, z + 0.16 + h + r * 0.45 + 0.05), 0.05, 0.12, "steel", verts=12, parent=P)
    valve(x + 0.08, y, z + 0.16 + h + r * 0.4, P)
    gauge(x - r * 0.5, y - r * 0.3, z + 0.16 + h + r * 0.3, P)
    tag("other")
    return (x, y, z + 0.16 + h * 0.5)


def hx_shell(x, y, z, length, r, rz, P, nozzles=2):
    """A heat-exchanger shell: horizontal drum, flanged channel heads, saddles, nozzles on top."""
    tag("vessel")
    rot = (0, math.pi / 2, rz)
    cyl((x, y, z), r, length, "steel", rot=rot, verts=40, parent=P)
    for e in (-1, 1):
        hx, hy = at(x, y, rz, e * (length / 2 + 0.06), 0)
        cyl((hx, hy, z), r * 1.12, 0.07, "collar", rot=rot, verts=40, parent=P)          # head flange
        hx2, hy2 = at(x, y, rz, e * (length / 2 + 0.16), 0)
        cyl((hx2, hy2, z), r * 0.98, 0.16, "steel", rot=rot, verts=40, parent=P)          # channel head
        for k in range(10):
            a = 2 * math.pi * k / 10
            bx, by = at(x, y, rz, e * (length / 2 + 0.1), r * 1.06 * math.cos(a))
            cyl((bx, by, z + r * 1.06 * math.sin(a)), 0.018, 0.06, "collar", rot=rot, verts=8, bevel=0, parent=P)
        sx, sy = at(x, y, rz, e * length * 0.32, 0)
        box((sx, sy, (z - r) / 2 + 0.02), (0.1, r * 1.7, max(0.06, z - r * 0.4)), "dark", rz=rz, parent=P)
    for k in range(nozzles):
        nx, ny = at(x, y, rz, (k - (nozzles - 1) / 2) * length * 0.5, 0)
        cyl((nx, ny, z + r + 0.07), 0.07, 0.16, "steel", verts=16, parent=P)
        cyl((nx, ny, z + r + 0.16), 0.11, 0.04, "collar", verts=16, parent=P)
    for k in range(3):                                                                    # shell bands
        bx, by = at(x, y, rz, (k - 1) * length * 0.3, 0)
        torus((bx, by, z), r * 1.01, 0.018, "collar", rot=rot, seg=32, parent=P)
    gauge(*at(x, y, rz, length * 0.1, -r * 0.6), z + r * 0.8, P)
    tag("other")


def radiator_banks(R0, R1, h0, h1, P, n=32, skips=(), t=0.1, z0=0.18):
    """Heavy radiator panels standing radially in a ring, tallest at the shield, each with a
    header pipe along its top edge and an outer post; a skirt ring under them."""
    tag("radiator")
    cyl((0, 0, z0 / 2), R1 + 0.06, z0, "dark", verts=96, parent=P)
    torus((0, 0, z0), R1 + 0.04, 0.03, "collar", seg=96, parent=P)
    tops = []
    for k in range(n):
        a = 2 * math.pi * k / n + math.pi / n
        if any(abs((a - s + math.pi) % (2 * math.pi) - math.pi) < w for s, w in skips):
            continue
        c, s = math.cos(a), math.sin(a)
        tx, ty = -s * t / 2, c * t / 2
        prof = [(R0, z0), (R1, z0), (R1, z0 + h1), (R0, z0 + h0)]
        verts = [(r * c + tx, r * s + ty, z) for r, z in prof] + [(r * c - tx, r * s - ty, z) for r, z in prof]
        faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        tag("radiator")
        mesh_obj("panel", verts, faces, "panel", 0.006, P)
        for f in (0.33, 0.66):                                   # stiffener ribs, both faces
            rr = R0 + (R1 - R0) * f
            hz = z0 + h0 + (h1 - h0) * f
            box((rr * c, rr * s, (z0 + hz) / 2), (0.035, t + 0.03, hz - z0), "collar", rz=a, bevel=0.003, parent=P)
        box((R1 * c, R1 * s, z0 + h1 / 2 + 0.04), (0.08, t + 0.05, h1 + 0.08), "collar", rz=a, bevel=0.006,
            parent=P)
        tag("cool")
        p0 = (R0 * c, R0 * s, z0 + h0 + 0.04)
        p1 = (R1 * c, R1 * s, z0 + h1 + 0.04)
        tube([p0, p1], 0.032, "steel", parent=P, res=3)
        tops.append((a, p0))
    tag("cool")                       # the manifold header over the panels' inner ends
    lagged([((R0 + 0.04) * math.cos(2 * math.pi * k / 48), (R0 + 0.04) * math.sin(2 * math.pi * k / 48),
             z0 + h0 + 0.1) for k in range(49)], 0.075, P, straps=0.3)
    tag("other")
    return tops


def _tier(R, z0, z1, m, P, ribs):
    h = z1 - z0
    cyl((0, 0, z0 + h / 2), R, h, m, verts=64, parent=P)
    for f in (0.3, 0.7):
        cyl((0, 0, z0 + h * f), R + 0.04, 0.08, "collar", verts=64, parent=P)
    for k in range(ribs):
        a = 2 * math.pi * k / ribs
        box(((R + 0.02) * math.cos(a), (R + 0.02) * math.sin(a), z0 + h / 2), (0.07, 0.1, h - 0.1), "collar", rz=a,
            bevel=0.004, parent=P)
    torus((0, 0, z1), R - 0.02, 0.06, "collar", parent=P)
    cyl((0, 0, z1 + 0.01), R - 0.06, 0.04, "steel", verts=64, parent=P)
    bolts(0, 0, z1 + 0.04, R - 0.12, 32, 0.022, parent=P)


def shield_drum(R, H, P, R2=None, H2=None, blocks=12, ports=4, m="lead"):
    """Thick shielding round the core: a lead drum (R, H) and a narrower upper tier (R2, up to
    H2) stepped on it, each ribbed, banded and bolted; shield blocks round the foot and round
    the upper tier's base; inspection ports in the lower drum."""
    tag("shield")
    cyl((0, 0, 0.1), R + 0.1, 0.2, "dark", verts=64, parent=P)
    _tier(R, 0.0, H, m, P, 24)
    if R2:
        _tier(R2, H, H2, m, P, 16)
        for k in range(blocks + 4):
            a = 2 * math.pi * k / (blocks + 4) + 0.2
            rr = R2 + (R - R2) * 0.55
            box((rr * math.cos(a), rr * math.sin(a), H + 0.13), (min(0.3, R - R2), 0.3, 0.26), m, rz=a, bevel=0.02,
                parent=P)
    for k in range(blocks):
        a = 2 * math.pi * k / blocks + 0.13
        rr = R + 0.17
        box((rr * math.cos(a), rr * math.sin(a), 0.2), (0.22, 0.34, 0.4), m, rz=a, bevel=0.02, parent=P)
    for k in range(ports):
        a = 2 * math.pi * k / ports + math.pi / 4
        cyl(((R + 0.04) * math.cos(a), (R + 0.04) * math.sin(a), H * 0.5), 0.12, 0.08, "collar",
            rot=(math.pi / 2, 0, a + math.pi / 2), verts=20, parent=P)
        cyl(((R + 0.08) * math.cos(a), (R + 0.08) * math.sin(a), H * 0.5), 0.07, 0.02, "recess",
            rot=(math.pi / 2, 0, a + math.pi / 2), verts=20, bevel=0, parent=P)
    tag("other")
    return H2 if R2 else H


def ring_header(R, z, P, branches=8, a0=0.0, r=0.085):
    """The coolant ring header round the drum, drops into it at `branches` points."""
    tag("cool")
    torus((0, 0, z), R, r, "steel", seg=96, parent=P)
    for k in range(branches):
        a = a0 + 2 * math.pi * k / branches
        c, s = math.cos(a), math.sin(a)
        torus((R * c, R * s, z), r * 1.35, r * 0.4, "collar", rot=(math.pi / 2, 0, a), seg=16, parent=P)
        tube([(R * c, R * s, z), ((R - 0.2) * c, (R - 0.2) * s, z + 0.12)], r * 0.6, "steel", parent=P, res=3)
    tag("other")


def fat_loop(ctrl, P, r=0.14):
    tag("cool")
    lagged(ctrl, r, P, straps=0.2)
    tag("other")


def rib_hose(ctrl, P, r=0.07):
    tag("cool")
    hose(ctrl, r=r, parent=P)
    tag("other")


def pier(x, y, z1, P, w=0.36):
    """A lead pier to lift a mast clear of the banks."""
    tag("mast")
    box((x, y, z1 / 2), (w, w, z1), "lead", bevel=0.02, parent=P)
    box((x, y, z1 - 0.03), (w + 0.08, w + 0.08, 0.06), "collar", bevel=0.01, parent=P)
    tag("other")


def tall_mast(base, length, P, **kw):
    tag("mast")
    tip = mast(base, length, P, **kw)
    tag("other")
    return tip


# corner and edge equipment, shared by the three; `omit` drops pieces (reactor inner corners)

def skid(x, y, w, d, P, rz=0.0):
    """A low equipment skid: deck plate and two rails."""
    tag("other")
    c = min(w, d) * 0.3
    oc = [at(x, y, rz, u, v) for u, v in octagon(w / 2, d / 2, c)]
    loft(oc, oc, 0.0, 0.1, "dark", bevel=0.01, parent=P)
    for e in (-1, 1):
        px, py = at(x, y, rz, 0, e * (d / 2 - 0.05))
        box((px, py, 0.12), (w - 2 * c, 0.05, 0.05), "collar", rz=rz, bevel=0.004, parent=P)


def plant_equipment(P, layout, omit=(), up=1.3):
    """layout 'ring' (variants 1 and 2) or 'crown' (variant 3, the corners kept for the masts).
    `up`: the height the fat loops enter the shield's upper tier."""
    def want(k):
        return k not in omit
    if layout == "ring":
        for k, (sx, sy) in (("sw", (-1, -1)), ("se", (1, -1)), ("nw", (-1, 1)), ("ne", (1, 1))):
            if want(k):
                skid(sx * 1.97, sy * 1.97, 1.06, 1.06, P)
        if want("sw"):
            exp_tank(-1.9, -1.88, 0.42, 1.7, P, ladder=-2.4)
            fat_loop([(-1.68, -1.64, 1.2), (-1.4, -1.36, up + 0.4), (-1.0, -0.98, up + 0.35), (-0.72, -0.7, up)], P)
            tag("cool"); valve(-1.55, -2.38, 0.1, P); tag("other")
            cell_rack(-0.95, -2.12, P, n=(2, 2))
        if want("se"):
            o = pump(1.62, -2.08, 0.0, P)
            exp_tank(2.15, -1.36, 0.27, 1.15, P, ladder=-1.2)
            fat_loop([o, (o[0] - 0.1, o[1] + 0.35, up + 0.4), (1.1, -1.1, up + 0.4), (0.72, -0.72, up)], P)
        if want("nw"):
            o = pump(-1.72, 2.02, math.pi, P)
            fat_loop([o, (o[0] + 0.15, o[1] - 0.4, up + 0.3), (-1.1, 1.1, up + 0.3), (-0.72, 0.72, up)], P)
            junc(-2.25, 1.45, P, w=0.24, d=0.3, h=0.4)
        if want("ne"):
            hx_shell(1.5, 2.12, 0.42, 0.85, 0.3, 0.0, P)
            exp_tank(2.18, 1.5, 0.24, 1.0, P, ladder=-1.0)
            rib_hose([(1.3, 1.85, 0.7), (1.05, 1.35, up + 0.15), (0.72, 0.72, up)], P)
        if want("w"):
            skid(-2.12, -0.1, 0.62, 1.9, P)
            hx_shell(-2.12, -0.1, 0.44, 1.4, 0.31, math.pi / 2, P)
            rib_hose([(-2.05, 0.55, 0.72), (-1.7, 0.5, up + 0.1), (-1.0, 0.3, up)], P)
            rib_hose([(-2.05, -0.75, 0.72), (-1.7, -0.65, up + 0.1), (-1.0, -0.3, up)], P)
        if want("n"):
            skid(-0.25, 2.15, 1.5, 0.62, P)
            hx_shell(-0.25, 2.15, 0.38, 0.95, 0.24, 0.0, P)
            tag("cool")
            for xx in (-0.55, 0.05):
                pipe([(xx, 2.15, 0.62), (xx, 1.75, 0.95), (xx * 0.5, 1.0, up)], 0.06, P)
            tag("other")
    else:   # crown: masts at the corners, equipment along the edges
        if want("sw"):
            exp_tank(-2.06, -1.05, 0.34, 1.45, P, ladder=-2.6)
            cell_rack(-1.12, -2.08, P, n=(2, 2))
            skid(-1.15, -2.12, 0.8, 0.62, P)
        if want("se"):
            o = pump(1.15, -2.06, 0.0, P)
            exp_tank(2.08, -1.1, 0.29, 1.2, P, ladder=-1.0)
            fat_loop([o, (o[0] - 0.1, o[1] + 0.35, up + 0.35), (0.85, -0.95, up + 0.3), (0.62, -0.62, up)], P)
        if want("nw"):
            o = pump(-1.15, 2.06, math.pi, P)
            fat_loop([o, (o[0] + 0.1, o[1] - 0.4, up + 0.25), (-0.85, 0.95, up + 0.25), (-0.62, 0.62, up)], P)
        if want("ne"):
            skid(1.12, 2.12, 1.15, 0.62, P)
            hx_shell(1.12, 2.12, 0.38, 0.85, 0.26, 0.0, P)
            rib_hose([(1.2, 1.85, 0.62), (0.95, 1.35, up + 0.1), (0.62, 0.7, up)], P)
        if want("w"):
            skid(-2.12, 0.15, 0.62, 1.7, P)
            hx_shell(-2.12, 0.5, 0.38, 0.9, 0.26, math.pi / 2, P)
            rib_hose([(-1.95, 0.55, 0.66), (-1.5, 0.45, up + 0.1), (-0.95, 0.3, up)], P)
            tag("vessel")
            tank(-2.1, -0.4, 0.3, 0.5, 0.2, math.pi / 2, P)
            tag("other")
        if want("n"):
            tag("cool")
            pipe([(-0.6, 2.25, 0.28), (0.45, 2.25, 0.28)], 0.08, P)
            pipe([(0.0, 2.25, 0.28), (0.0, 1.7, 0.85), (0.0, 0.95, up)], 0.065, P)
            tag("other")


def corner_deck(P, sx, sy):
    """The deck a corner mast stands on (crown layout): an octagonal skid."""
    skid(sx * 2.03, sy * 2.03, 0.9, 0.9, P)


# ================================================================= variant 1: THE GYRE SPIRE

def variant_1(ox=0.0, oy=0.0, s=1.0, reactor=False, omit=(), masts=None):
    """The spire rises out of the Gyre's core on a thick shield drum; the counter-rotating
    bands turn round its foot and throw beams across a ring of sloped radiator banks;
    four porcelain masts on lead piers among the banks arc to the column."""
    P = empty((ox, oy, 0))
    P.scale = (s, s, s)
    RS, HL, R2, HS = 1.32, 0.9, 1.0, 1.38         # shield: lower drum, upper tier (HS: its top)
    CZ = HS + 0.62
    TOP = 4.65
    glow("v1_core", "#5C9BFF", 2.6, base="#2A3A60")
    glow("arc", "#8DBBFF", 6.0, base="#8DBBFF")
    diag = [math.pi / 4 + q * math.pi / 2 for q in range(4)]
    radiator_banks(1.58, 2.24, 1.1, 0.5, P, n=40,
                   skips=[(-math.pi / 2, 0.3), (0.0, 0.26), (math.pi, 0.26), (math.pi / 2, 0.2)]
                   + [(a, 0.1) for a in diag])
    shield_drum(RS, HL, P, R2=R2, H2=HS)
    ring_header(RS + 0.12, 0.58, P, branches=8, a0=math.pi / 8)
    # the bowl crown on the drum
    tag("shield")
    cyl((0, 0, HS + 0.1), 0.98, 0.2, "body", verts=64, parent=P)
    torus((0, 0, HS + 0.2), 0.96, 0.05, "teal", parent=P)
    bolts(0, 0, HS + 0.22, 0.88, 28, parent=P)
    cyl((0, 0, HS + 0.19), 0.85, 0.02, "mirror", verts=64, bevel=0, parent=P)
    tag("other")
    cyl((0, 0, HS + 0.3), 0.12, 0.4, "lead", verts=24, parent=P)
    cone((0, 0, HS + 0.4), 0.1, 0.22, 0.12, "collar", parent=P)
    tag("light")
    sphere((0, 0, CZ), 0.27, "v1_core", parent=P)
    tag("other")
    core_light((0, 0, CZ), 420.0 * s * s, 0.1, parent=P)
    tag("shield")
    inner, outer, gim = shield_bands(CZ, P, r_in=0.46, r_out=0.66, h_in=0.62, h_out=0.42)
    torus((0, 0, CZ + 0.42), 0.36, 0.06, "collar", parent=P)
    cyl((0, 0, CZ + 0.42), 0.3, 0.1, "lead", verts=32, parent=P)
    tag("light")
    column(CZ + 0.45, TOP, P, "v1_rod", collars=4)
    cap(TOP, P, "v1_corona")
    tag("other")
    core_light((0, 0, (CZ + TOP) / 2 + 0.3), 90.0 * s * s, 0.15, parent=P)
    core_light((0, 0, TOP - 0.6), 50.0 * s * s, 0.15, parent=P)
    for a in diag:
        c, sn = math.cos(a), math.sin(a)
        tube([(0.9 * c, 0.9 * sn, HS + 0.2), (0.32 * c, 0.32 * sn, 2.9)], 0.02, "collar", parent=P)
    tips = []
    spots = masts if masts is not None else [(1.76 * math.cos(a), 1.76 * math.sin(a)) for a in diag]
    for (x, y) in spots:
        north = y > 0.5
        zp = 1.12
        pier(x, y, zp, P)
        tips.append(tall_mast((x, y, zp), 1.72 if north else 2.25, P, toward=(0, 0), arm=0.3))
        rib_hose([(x * 0.92, y * 0.92, zp + 0.25), (x * 0.75, y * 0.75, zp + 0.5), (x * 0.62, y * 0.62, HS + 0.15)],
                 P, r=0.04)
    plant_equipment(P, "ring", omit, up=HS - 0.12)
    if "s" not in omit:
        magazine(0, -1.98, P, chute_to=(0, -1.05, HS - 0.05))
    if "e" not in omit:
        converter(2.02, 0.0, P, side=1, d=1.0)
        cable_tray([(1.68, 0.4, 0.62), (1.35, 0.42, 0.9), (1.05, 0.35, 0.92)], P)
    state = dict(P=P, tips=tips, top=TOP, cz=CZ, s=s, ox=ox, oy=oy, rod="v1_rod", link_z=TOP - 0.5)

    def animate(ph, working, frame_i=0, seed=0):
        if not reactor:
            clear_arcs()
        inner.rotation_euler.z = ph * math.pi / 2 if working else 0.0
        outer.rotation_euler.z = -ph * math.pi / 3 if working else math.radians(20)
        gim.rotation_euler.z = ph * 2 * math.pi / 3 if working else 0.0
        if not working:
            set_wave("v1_rod", 0.0, 0.0)
            return 0.0
        set_wave("v1_rod", 1.0, ph * 2)
        rng = random.Random(3000 + frame_i + seed)
        tag("light")
        for k, tip in enumerate(tips):
            z = CZ + 0.9 + (TOP - CZ - 1.4) * (0.5 + 0.5 * math.sin(2 * math.pi * (ph + k / 4)))
            a = math.atan2(tip[1], tip[0]) + rng.uniform(-0.5, 0.5)
            arc(tip, (0.16 * math.cos(a), 0.16 * math.sin(a), z), rng, parent=P)
            if rng.random() < 0.4:
                arc(tip, (0.12 * math.cos(a + 0.6), 0.12 * math.sin(a + 0.6), z + rng.uniform(-0.3, 0.3)), rng,
                    r=0.015, parent=P)
        tag("other")
        return 0.85 + 0.15 * math.sin(2 * math.pi * 2 * ph)
    animate.state = state
    return animate


# ================================================================= variant 2: THE BANDED SPIRE

def variant_2(ox=0.0, oy=0.0, s=1.0, reactor=False, omit=(), masts=None, tiers=4):
    """The tiered cage on the Reaction Plant's banded drum, the drum now a raised shield
    with its ring header, the radiator banks round it; three masts on piers."""
    P = empty((ox, oy, 0))
    P.scale = (s, s, s)
    RS, HL, R2, HS = 1.42, 0.95, 1.05, 1.45     # the banded drum, and the shield tier stepped on it
    Z0 = HS + 0.2
    TIER = 0.72
    TOP = Z0 + tiers * TIER + 0.25
    glow("arc", "#8DBBFF", 6.0, base="#8DBBFF")
    glow("v2_slot", BLUE_DEEP, 3.0)
    mast_a = [math.radians(30), math.radians(150), math.radians(270)]
    radiator_banks(1.72, 2.24, 0.9, 0.45, P, n=44,
                   skips=[(-math.pi / 2, 0.42), (0.0, 0.24), (math.pi, 0.24), (math.pi / 2, 0.18)]
                   + [(a, 0.1) for a in mast_a])
    shield_drum(RS, HL, P, R2=R2, H2=HS, blocks=14, m="body")
    # the Reaction Plant's banding on it
    tag("shield")
    for z in (0.25, HL - 0.1):
        cyl((0, 0, z), RS + 0.05, 0.1, "lead", verts=64, parent=P)
    cyl((0, 0, HS - 0.08), R2 + 0.05, 0.1, "lead", verts=64, parent=P)
    torus((0, 0, HS + 0.03), R2 - 0.14, 0.05, "teal", parent=P)
    tag("light")
    for k in range(12):
        a = 2 * math.pi * k / 12 + 0.26
        box(((R2 + 0.05) * math.cos(a), (R2 + 0.05) * math.sin(a), (HL + HS) / 2 + 0.06), (0.05, 0.18, 0.08),
            "v2_slot", rz=a, bevel=0, parent=P)
    tag("other")
    ring_header(RS + 0.12, 0.5, P, branches=10, a0=0.1)
    tag("shield")
    cyl((0, 0, HS + 0.08), 0.66, 0.16, "collar", verts=48, parent=P)
    cyl((0, 0, HS + 0.17), 0.52, 0.1, "lead", verts=48, parent=P)
    tag("light")
    cyl((0, 0, (Z0 + TOP) / 2), 0.15, TOP - Z0, wave_glow("v2_rod", "#5C9BFF", "z", 1.25, 4.0, 0.35, 2.5),
        verts=24, bevel=0, parent=P)
    tag("shield")
    rings = []
    for t in range(tiers):
        zc = Z0 + TIER * (t + 0.5)
        r_in = 0.5 - 0.035 * t
        R = empty(parent=P)
        for q in range(3):
            a0 = q * 2 * math.pi / 3
            band(r_in, r_in + 0.07, zc - 0.28, zc + 0.28, a0, a0 + math.radians(82),
                 "lead" if t % 2 == 0 else "collar", parent=R)
            for z in (zc - 0.28, zc + 0.22):
                band(r_in + 0.065, r_in + 0.095, z, z + 0.06, a0, a0 + math.radians(82), "copper", parent=R)
            band(r_in + 0.07, r_in + 0.09, zc - 0.05, zc + 0.05, a0 + 0.2, a0 + math.radians(82) - 0.2,
                 "teal" if t % 2 else "collar", parent=R)
        rings.append(R)
        torus((0, 0, zc + 0.36), r_in + 0.05, 0.045, "collar", seg=48, parent=P)
        core_light((0, 0, zc), (130.0 if t == 0 else 85.0) * s * s, 0.12, parent=P)
    torus((0, 0, Z0 + 0.06), 0.55, 0.05, "collar", seg=48, parent=P)
    for k in range(4):
        a = 2 * math.pi * k / 4 + math.pi / 4
        tube([(0.62 * math.cos(a), 0.62 * math.sin(a), Z0), (0.5 * math.cos(a), 0.5 * math.sin(a), TOP)], 0.03,
             "lead", parent=P)
    tag("light")
    cap(TOP, P, "v2_corona")
    tag("other")
    tips = []
    spots = masts if masts is not None else [(1.97 * math.cos(a), 1.97 * math.sin(a)) for a in mast_a]
    for (x, y) in spots:
        zp = 0.82
        pier(x, y, zp, P)
        tips.append(tall_mast((x, y, zp), 2.5, P, toward=(0, 0), arm=0.34))
        fat_loop([(x * 0.93, y * 0.93, zp + 0.2), (x * 0.75, y * 0.75, zp + 0.55), (x * 0.56, y * 0.56, HL + 0.3)],
                 P, r=0.045)
    plant_equipment(P, "ring", omit, up=HS - 0.12)
    if "s" not in omit:
        magazine(0.78, -2.0, P, chute_to=(0.45, -1.15, HS - 0.1))
    if "e" not in omit:
        converter(2.04, 0.05, P, side=1, d=1.0)
        cable_tray([(1.7, 0.4, 0.62), (1.5, 0.5, 0.95)], P)
    zs = [Z0 + TIER * (t + 1) - 0.05 for t in range(tiers - 1)] + [Z0 + 0.25]

    def animate(ph, working, frame_i=0, seed=0):
        if not reactor:
            clear_arcs()
        for t, R in enumerate(rings):
            d = 1 if t % 2 == 0 else -1
            R.rotation_euler.z = (d * ph * 2 * math.pi / 3 + t * 0.7) if working else t * 0.7
        if not working:
            set_wave("v2_rod", 0.0, 0.0)
            return 0.0
        set_wave("v2_rod", 1.0, ph * 2)
        rng = random.Random(5000 + frame_i + seed)
        tag("light")
        for k, tip in enumerate(tips):
            g = int((ph * len(zs) + k * 1.3)) % len(zs)
            z = zs[g] + rng.uniform(-0.06, 0.06)
            a = math.atan2(tip[1], tip[0]) + rng.uniform(-0.35, 0.35)
            arc(tip, (0.2 * math.cos(a), 0.2 * math.sin(a), z), rng, parent=P, bow=0.08)
            if rng.random() < 0.45:
                arc(tip, (0.5 * math.cos(a + 0.4), 0.5 * math.sin(a + 0.4), zs[(g + 1) % len(zs)]), rng, r=0.014,
                    parent=P)
        tag("other")
        return 0.85 + 0.15 * math.sin(2 * math.pi * 3 * ph)
    animate.state = dict(P=P, tips=tips, top=TOP, s=s, ox=ox, oy=oy, rod="v2_rod", link_z=Z0 + 2 * TIER)
    return animate


# ================================================================= variant 3: THE CROWN

def variant_3(ox=0.0, oy=0.0, s=1.0, reactor=False, omit=(), masts="corners"):
    """The Gyre on a shield drum, its pylons, crown bearing and needle raised; four porcelain
    masts on the corner skids lean in and arc onto the needle."""
    P = empty((ox, oy, 0))
    P.scale = (s, s, s)
    RS, HL, R2, HS = 1.28, 0.8, 0.98, 1.2       # shield: lower drum, upper tier (HS: its top)
    CZ = HS + 0.62
    NEEDLE = 3.55
    CROWN = HS + 1.3
    glow("v3_core", "#5C9BFF", 2.6, base="#2A3A60")
    glow("v3_needle", BLUE_HOT, 3.0, base="#2A3A60")
    glow("arc", "#8DBBFF", 6.0, base="#8DBBFF")
    radiator_banks(1.56, 2.2, 1.0, 0.5, P, n=40,
                   skips=[(-math.pi / 2, 0.3), (0.0, 0.3), (math.pi, 0.4), (math.pi / 2, 0.36)])
    shield_drum(RS, HL, P, R2=R2, H2=HS)
    ring_header(RS + 0.12, 0.45, P, branches=8, a0=0.0)
    tag("shield")
    cyl((0, 0, HS + 0.08), 0.96, 0.16, "body", verts=64, parent=P)
    torus((0, 0, HS + 0.16), 0.95, 0.05, "lead", parent=P)
    bolts(0, 0, HS + 0.19, 0.95, 32, parent=P)
    cyl((0, 0, HS + 0.15), 0.9, 0.02, "mirror", verts=64, bevel=0, parent=P)
    for q in range(4):
        a = math.pi / 4 + q * math.pi / 2
        c, sn = math.cos(a), math.sin(a)
        zc = (HS + CROWN) / 2
        box((0.9 * c, 0.9 * sn, zc), (0.2, 0.26, CROWN - HS), "lead", rz=a, parent=P)
        box((0.8 * c, 0.8 * sn, CROWN - 0.05), (0.36, 0.22, 0.18), "lead", rz=a, parent=P)
        for z in (HS + 0.35, HS + 0.85):
            box((0.9 * c, 0.9 * sn, z), (0.24, 0.3, 0.06), "collar", rz=a, parent=P)
    torus((0, 0, CROWN), 0.68, 0.055, "collar", parent=P)
    torus((0, 0, CROWN + 0.06), 0.68, 0.025, "copper", parent=P)
    tag("other")
    cyl((0, 0, HS + 0.3), 0.1, 0.5, "lead", verts=24, parent=P)
    cone((0, 0, HS + 0.42), 0.08, 0.2, 0.14, "collar", parent=P)
    tag("light")
    sphere((0, 0, CZ), 0.28, "v3_core", parent=P)
    tag("other")
    core_light((0, 0, CZ), 560.0 * s * s, 0.1, parent=P)
    tag("shield")
    inner, outer, gim = shield_bands(CZ, P, r_in=0.48, r_out=0.68, h_in=0.7, h_out=0.46)
    for q in range(4):
        a = q * math.pi / 2
        tube([(0.66 * math.cos(a), 0.66 * math.sin(a), CROWN + 0.05),
              (0.12 * math.cos(a), 0.12 * math.sin(a), CROWN + 0.2)], 0.03, "lead", parent=P)
    cyl((0, 0, CROWN + 0.18), 0.16, 0.12, "collar", verts=24, parent=P)
    tag("light")
    cyl((0, 0, (CROWN + 0.2 + NEEDLE) / 2), 0.07, NEEDLE - CROWN - 0.2, "v3_needle", verts=16, bevel=0, parent=P)
    tag("shield")
    for k in range(3):
        a = 2 * math.pi * k / 3
        box((0.13 * math.cos(a), 0.13 * math.sin(a), (CROWN + 0.2 + NEEDLE) / 2), (0.035, 0.035, NEEDLE - CROWN - 0.2),
            "lead", rz=a, bevel=0.004, parent=P)
    torus((0, 0, (CROWN + NEEDLE) / 2 + 0.1), 0.14, 0.025, "collar", seg=24, parent=P)
    sphere((0, 0, NEEDLE + 0.08), 0.13, "grading", parent=P)
    torus((0, 0, NEEDLE - 0.02), 0.2, 0.028, "grading", seg=32, parent=P)
    tag("other")
    core_light((0, 0, NEEDLE - 0.3), 60.0 * s * s, 0.12, parent=P)
    tips = []
    if masts == "corners":
        spots = [(x, y) for x in (-1.98, 1.98) for y in (-1.98, 1.98)]
    else:
        spots = masts
    for (x, y) in spots:
        north = y > 0.5
        sx, sy = (1 if x > 0 else -1), (1 if y > 0 else -1)
        corner_deck(P, sx, sy)
        zp = 0.32
        pier(x, y, zp, P, w=0.42)
        tips.append(tall_mast((x, y, zp), 2.4 if north else 2.85, P, tilt=math.radians(20), toward=(0, 0), arm=0.32))
        rib_hose([(x * 0.9, y * 0.9, 0.35), (x * 0.74, y * 0.74, 0.95), (x * 0.56, y * 0.56, HS + 0.1)], P, r=0.045)
    plant_equipment(P, "crown", omit, up=HS - 0.12)
    if "s" not in omit:
        magazine(0, -1.98, P, chute_to=(0, -1.05, HS + 0.05))
    if "e" not in omit:
        converter(2.04, 0.0, P, side=1, d=1.0)
        cable_tray([(1.68, 0.45, 0.6), (1.3, 0.5, 0.85), (1.05, 0.4, 0.9)], P)

    def animate(ph, working, frame_i=0, seed=0):
        if not reactor:
            clear_arcs()
        inner.rotation_euler.z = ph * math.pi / 2 if working else 0.0
        outer.rotation_euler.z = -ph * math.pi / 3 if working else math.radians(20)
        gim.rotation_euler.z = ph * 2 * math.pi / 3 if working else 0.0
        if not working:
            return 0.0
        rng = random.Random(7000 + frame_i + seed)
        tag("light")
        for k, tip in enumerate(tips):
            zt = CROWN + 0.4 + (NEEDLE - CROWN - 0.5) * (0.5 + 0.5 * math.sin(2 * math.pi * (ph + k / 4)))
            arc(tip, (0, 0, zt), rng, parent=P, jag=0.09, n=11, bow=0.1)
            if rng.random() < 0.35:
                a = math.atan2(tip[1], tip[0])
                arc(tip, (0.68 * math.cos(a + rng.uniform(-0.4, 0.4)), 0.68 * math.sin(a + rng.uniform(-0.4, 0.4)),
                          CROWN + 0.05), rng, r=0.015, parent=P, bow=0.05)
        tag("other")
        return 0.85 + 0.15 * math.sin(2 * math.pi * 2 * ph)
    animate.state = dict(P=P, tips=tips, top=NEEDLE, s=s, ox=ox, oy=oy, link_z=NEEDLE - 0.3)
    return animate


# ================================================================= stage 4: Radiant Reactor blocks

def world(st, p):
    s = st["s"]
    return (st["ox"] + s * p[0], st["oy"] + s * p[1], s * p[2])


def reactor_block(v):
    """A 2x2 block of 7x7 Radiant Reactors in the variant's language. Every variant links the
    same way (variant 3's round-3 link): where four reactors meet, one shared corner mast,
    taller, arcs into all four; each reactor's inner corner is left clear for it. Between
    neighbours a coolant bridge (two lagged pipes) and a lit duct."""
    pitch, s = 7.0, 1.38
    anims = []
    h = pitch / 2
    centres = [(ix * h, iy * h) for iy in (-1, 1) for ix in (-1, 1)]
    links = []
    for (cx, cy) in centres:
        sx, sy = (1 if cx < 0 else -1), (1 if cy < 0 else -1)        # toward the block's centre
        corner = {(1, 1): "ne", (-1, 1): "nw", (1, -1): "se", (-1, -1): "sw"}[(sx, sy)]
        omit = {corner}
        if v == "1":
            diag = [math.pi / 4 + q * math.pi / 2 for q in range(4)]
            spots = [(1.66 * math.cos(a), 1.66 * math.sin(a)) for a in diag
                     if not (math.cos(a) * sx > 0 and math.sin(a) * sy > 0)]
            anims.append(variant_1(cx, cy, s, reactor=True, omit=omit, masts=spots))
        elif v == "2":
            anims.append(variant_2(cx, cy, s, reactor=True, omit=omit, tiers=5))
        else:
            spots = [(x, y) for x in (-1.98, 1.98) for y in (-1.98, 1.98) if not (x * sx > 0 and y * sy > 0)]
            anims.append(variant_3(cx, cy, s, reactor=True, omit=omit, masts=spots))
    P0 = empty((0, 0, 0))
    tag("mast")
    box((0, 0, 0.2), (1.1, 1.1, 0.4), "dark", parent=P0)
    pier(0, 0, 0.55, P0, w=0.6)
    tip = tall_mast((0.0, 0.0, 0.55), 4.6, P0, toward=(0.01, 0.0), arm=0.02)
    for a in anims:
        links.append((tip, world(a.state, (0, 0, a.state["link_z"]))))
    tag("cool")
    for (x0, y0, x1, y1) in ((-h, -h, h, -h), (-h, h, h, h), (-h, -h, -h, h), (h, -h, h, h)):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        horiz = abs(x1 - x0) > 0
        box((mx, my, 0.18), (1.5 if horiz else 0.7, 0.7 if horiz else 1.5, 0.3), "body", bevel=0.02)
        for e in (-0.2, 0.2):
            if horiz:
                lagged([(mx - 1.1, my + e, 0.45), (mx, my + e, 0.5), (mx + 1.1, my + e, 0.45)], 0.1)
            else:
                lagged([(mx + e, my - 1.1, 0.45), (mx + e, my, 0.5), (mx + e, my + 1.1, 0.45)], 0.1)
        tag("light")
        box((mx, my, 0.34), (1.3 if horiz else 0.12, 0.12 if horiz else 1.3, 0.04),
            M.get("bridge_glow") or glow("bridge_glow", BLUE_HOT, 3.0), bevel=0)
        tag("cool")
    tag("other")
    return anims, links, pitch


# ================================================================= scene

BUILDERS = {"1": variant_1, "2": variant_2, "3": variant_3}
INFO = {
    #       footprint, canvas tiles (w, h), origin tiles (x, y) from top-left, frames
    "1": dict(foot=(5, 5), canvas=(9.0, 9.5), origin=(3.9, 5.9), frames=48),
    "2": dict(foot=(5, 5), canvas=(9.0, 9.5), origin=(3.9, 5.9), frames=48),
    "3": dict(foot=(5, 5), canvas=(9.0, 9.5), origin=(3.9, 5.9), frames=48),
}
info = dict(INFO[OPTION])

rig.sun()
GROUND = rig.ground_catcher(size=60)
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground(size=60)


def camera(canvas, origin, ss):
    w, h = int(canvas[0] * rig.PX_PER_TILE), int(canvas[1] * rig.PX_PER_TILE)
    rig.camera(w, h, centre_px=(origin[0] * rig.PX_PER_TILE, origin[1] * rig.PX_PER_TILE), ss=ss)
    return w, h


def lit_materials():
    return {m for m, _ in GLOWS.values()} | {M[n] for n in ("v1_rod", "v2_rod") if n in M}


def no_shadow_emitters():
    lit = lit_materials()
    for o in OBJS:
        if o.data and any(sl.material in lit for sl in o.material_slots):
            o.visible_shadow = False


def shoot(path, anim, ph, working, frame_i=0):
    k = anim(ph, working, frame_i=frame_i)
    no_shadow_emitters()
    for name in list(GLOWS):
        set_glow(name, (1.0 if working else 0.0) if name == "arc" else k)
    set_lights(k)
    rig.render(path)


MASK_COLOURS = {      # flat colours for the category pass (r4_sheets.py reads them back)
    "shield": "#3C64C8", "cool": "#E6B43C", "vessel": "#D2D2D2", "pump": "#3CB45A",
    "radiator": "#B45AC8", "mast": "#8C3C1E", "light": "#50E6FF", "other": "#6E6E6E",
}


def shoot_mask(path, anim):
    anim(0.0, True, frame_i=0)
    lit = lit_materials()
    flat = {}
    for c, hexcol in MASK_COLOURS.items():
        m = bpy.data.materials.new("mask_" + c)
        m.use_nodes = True
        nt = m.node_tree
        for nd in list(nt.nodes):
            nt.nodes.remove(nd)
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = rig.srgb(hexcol)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(em.outputs[0], out.inputs[0])
        flat[c] = m
    for o in OBJS:
        if not o.data or not hasattr(o.data, "materials"):
            continue
        c = o.get("cat", "other")
        if any(sl.material in lit for sl in o.material_slots):
            c = "light"
        for i in range(len(o.material_slots)):
            o.material_slots[i].material = flat[c]
    GROUND.hide_render = True
    BOUNCE.hide_render = True
    for ob in bpy.data.objects:
        if ob.type == "LIGHT":
            ob.hide_render = True
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.render.filter_size = 0.01
    sc.cycles.samples = 1
    rig.render(path)


if MODE == "reactor":
    anims, links, pitch = reactor_block(OPTION)
    size = 2 * pitch + 2.4
    info.update(canvas=(size + 1.6, size + 1.8), origin=(size / 2 + 0.2, size / 2 + 1.6), foot=(pitch, pitch),
                block=(2, 2), pitch=pitch)
    camera(info["canvas"], info["origin"], 2)
    sc.cycles.samples = SAMPLES or 48
    glow("arc", "#8DBBFF", 6.0, base="#8DBBFF")
    rng = random.Random(11)
    tag("light")
    for p0, p1 in links:
        arc(p0, p1, rng, jag=0.2, n=14, r=0.035, bow=0.25)
        arc(p0, p1, rng, jag=0.25, n=14, r=0.02, bow=0.15)
    tag("other")

    def all_anim(ph, working, frame_i=0):
        k = 1.0
        for i, a in enumerate(anims):
            k = a(ph + i * 0.17, working, frame_i=0, seed=i * 31)
        return k
    shoot(f"{OUT_DIR}/reactor.png", all_anim, 0.0, True)
else:
    anim = BUILDERS[OPTION]()
    N = info["frames"]
    if MODE == "hero":
        camera(info["canvas"], info["origin"], 4)
        shoot(f"{OUT_DIR}/working.png", anim, 0.0, True)
        shoot(f"{OUT_DIR}/idle.png", anim, 0.0, False)
    elif MODE == "anim":
        camera(info["canvas"], info["origin"], 2)
        only = os.environ.get("R4_FRAMES")            # e.g. "0,12" to test a few
        todo = [int(x) for x in only.split(",")] if only else range(N)
        for i in todo:
            shoot(f"{OUT_DIR}/f{i:03d}.png", anim, i / N, True, frame_i=i)
        shoot(f"{OUT_DIR}/idle.png", anim, 0.0, False)
    elif MODE == "mask":
        camera(info["canvas"], info["origin"], 1)
        shoot_mask(f"{OUT_DIR}/mask.png", anim)

with open(f"{OUT_DIR}/info.json", "w") as f:
    json.dump(dict(info, option=OPTION, mode=MODE, ss={"hero": 4, "anim": 2, "reactor": 2, "mask": 1}[MODE]), f)
print("done", OPTION, MODE)
