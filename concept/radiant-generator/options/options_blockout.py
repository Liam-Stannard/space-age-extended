"""Radiant Generator, options round: five quick blockouts, one per option.

  $BLENDER -b --python options_blockout.py -- <out-dir> <A|B|C|D|E> [--quick]

Writes, per direction the option has (one, or vertical and horizontal):
  <dir>-working.png  the machine with the radiant light on
  <dir>-idle.png     the same, light off
  <dir>-shadow.png   the ground shadow alone
at 4x sprite size (rig.SS), on a 448 x 448 sprite canvas with the entity origin
at (224, 256). options_sheets.py brings them to game scale and lays out the
sheets.

A blockout, not a model: flat palette colours from the spec's 3.3 and the
Reaction Plant's (lead, teal, copper, radiant blue), one tone per kind of part,
so the form and the family are judged and not the finish. Nothing here is
adopted; it exists to compare five ideas side by side.

Units are tiles; north is +Y; a point (x, y, z) lands at screen (x, y + z/2)
tiles from the origin.
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

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR, OPTION = argv[0], argv[1].upper()
QUICK = "--quick" in argv
os.makedirs(OUT_DIR, exist_ok=True)

CANVAS = (448, 448)
CENTRE = (224, 256)

sc = rig.reset()
if QUICK:
    sc.cycles.samples = 16
ROOT = rig.turntable(rig.stretch_root())


def mat(name, hexcol, rough=0.6, metal=0.3):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb(hexcol)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


M = {
    "body": mat("body", "#5C564B"),            # spec 3.3 armour, #4A463F -> #6E685C
    "dark": mat("dark", "#4A463F"),
    "fin": mat("fin", "#8A8580", rough=0.45, metal=0.5),
    "collar": mat("collar", "#3B3B40", rough=0.7),
    "lead": mat("lead", "#6A6A70", rough=0.7, metal=0.3),   # the Reaction Plant's shield bands
    "copper": mat("copper", "#8A5A32", rough=0.4, metal=0.8),
    "teal": mat("teal", "#2A7F7A", rough=0.8, metal=0.0),   # the plant's roof paint
    "recess": mat("recess", "#15161A", rough=0.9, metal=0.0),
}
slot = mat("slot", "#0C1630", rough=0.4, metal=0.0)
sb = slot.node_tree.nodes["Principled BSDF"]
sb.inputs["Emission Color"].default_value = rig.srgb("#4A88FF")    # inside #1F63FF -> #73ADFF
sb.inputs["Emission Strength"].default_value = 0.0
M["slot"] = slot
GLOW = 2.2

OBJS = []


def _finish(o, m, bevel=0.012, smooth=False):
    o.data.materials.append(M[m])
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments, mod.limit_method = bevel, 2, "ANGLE"
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    o.parent = ROOT
    OBJS.append(o)
    return o


def box(loc, size, m, rz=0.0, rot=None, bevel=0.012):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot or (0, 0, rz))
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, m, bevel)


def cyl(loc, r, h, m, rot=(0, 0, 0), verts=40, bevel=0.01):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    return _finish(bpy.context.active_object, m, bevel, smooth=True)


def dome(loc, r, h, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=loc, segments=48, ring_count=24)
    o = bpy.context.active_object
    o.scale = (r, r, h)
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, m, 0, smooth=True)


def loft(lo, hi, z0, z1, m, bevel=0.02):
    """A slab from outline lo at z0 to outline hi at z1: a battered wall, or a prism."""
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
    return _finish(o, m, bevel)


def octagon(ex, ey, c):
    return [(-ex, -ey + c), (-ex + c, -ey), (ex - c, -ey), (ex, -ey + c),
            (ex, ey - c), (ex - c, ey), (-ex + c, ey), (-ex, ey - c)]


def slot_v(x, y, z, length, along="y", depth=0.05, w=0.09):
    """A slot in an upward-facing surface: a dark recess with the light inside."""
    sx, sy = (w, length) if along == "y" else (length, w)
    box((x, y, z - depth / 2 + 0.005), (sx + 0.05, sy + 0.05, depth), "collar", bevel=0.006)
    box((x, y, z + 0.006), (sx, sy, 0.012), "slot", bevel=0)


def slot_on_cyl(cx, cy, cz, r, ang, z, length=0.26, h=0.07):
    """A horizontal slot on a vertical cylinder's wall at angle ang (radians)."""
    rz = ang + math.pi / 2
    box((cx + (r + 0.005) * math.cos(ang), cy + (r + 0.005) * math.sin(ang), z),
        (length + 0.06, 0.06, h + 0.05), "collar", rz=rz, bevel=0.008)
    box((cx + (r + 0.04) * math.cos(ang), cy + (r + 0.04) * math.sin(ang), z),
        (length, 0.01, h), "slot", rz=rz, bevel=0)


def fin_bank_y(x0, x1, y0, y1, z0, z1, pitch=0.12, t=0.035):
    """Fins standing across x, stacked along y: a radiator flank."""
    n = int((y1 - y0) / pitch)
    for i in range(n + 1):
        y = y0 + i * (y1 - y0) / n
        box(((x0 + x1) / 2, y, (z0 + z1) / 2), (abs(x1 - x0), t, z1 - z0), "fin", bevel=0.005)


def fin_bank_x(x0, x1, y0, y1, z0, z1, pitch=0.12, t=0.035):
    n = int((x1 - x0) / pitch)
    for i in range(n + 1):
        x = x0 + i * (x1 - x0) / n
        box((x, (y0 + y1) / 2, (z0 + z1) / 2), (t, abs(y1 - y0), z1 - z0), "fin", bevel=0.005)


def trunk(points, r=0.07, m="copper"):
    cu = bpy.data.curves.new("trunk", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 4
    sp = cu.splines.new("POLY")
    sp.points.add(len(points) - 1)
    for p, co in zip(sp.points, points):
        p.co = (*co, 1)
    o = bpy.data.objects.new("trunk", cu)
    sc.collection.objects.link(o)
    o.data.materials.append(M[m])
    o.parent = ROOT
    OBJS.append(o)
    return o


def hatch(x, y, z, w, d, ports=2, m="teal"):
    """The fuel hatch: a teal lid with two loading ports (fuel_inventory_size 2)."""
    box((x, y, z + 0.03), (w, d, 0.06), m, bevel=0.015)
    for k in range(ports):
        px = x + (k - (ports - 1) / 2) * w * 0.45
        cyl((px, y, z + 0.09), 0.11, 0.06, "collar", verts=24)
        cyl((px, y, z + 0.121), 0.07, 0.01, "recess", verts=24, bevel=0)


def spent_drawer(x, y, z, w=0.3, d=0.22, h=0.14):
    """The spent-cell drawer: plain lead, smaller than the fuel hatch (burnt_inventory_size 1)."""
    box((x, y, z + h / 2), (w, d, h), "lead", bevel=0.015)
    box((x, y - d / 2 - 0.01, z + h / 2), (w * 0.6, 0.03, 0.035), "collar", bevel=0.004)


# ---------------------------------------------------------------- the options

def option_a():
    """The Trough, v2 refined. 3x5, built north-south; the horizontal plate turns it."""
    L = 2.45
    # the trough body: battered walls straight off the ground, no plinth
    loft(octagon(0.78, L, 0.2), octagon(0.68, L - 0.06, 0.16), 0.0, 0.42, "dark")
    # radiator flanks: the dominant mass, fins from the ground to just under the throat
    for s in (-1, 1):
        box((s * 0.83, -0.05, 0.25), (0.08, 3.5, 0.5), "dark", bevel=0.01)       # fin root wall
        fin_bank_y(s * 0.86, s * 1.45, -1.75, 1.65, 0.02, 0.62)
        box((s * 1.43, -0.05, 0.6), (0.05, 3.55, 0.05), "collar", bevel=0.006)    # tie rail at the tips
    # the throat: a lead tube on the trough's back, three collars, three slots on top
    TZ, TR = 0.72, 0.36
    cyl((0, -0.05, TZ), TR, 3.0, "lead", rot=(math.pi / 2, 0, 0), verts=48)
    for y in (-1.45, -0.5, 0.45, 1.4):
        cyl((0, y, TZ), TR + 0.07, 0.16, "collar", rot=(math.pi / 2, 0, 0), verts=48)
        for a in range(6):
            ang = a * math.pi / 3 + math.pi / 6
            box((0.43 * math.cos(ang), y, TZ + 0.43 * math.sin(ang)), (0.06, 0.18, 0.06), "copper",
                bevel=0.008)
    for y in (-0.975, -0.025, 0.925):
        slot_v(0, y, TZ + TR - 0.01, 0.5)
    # the fuel magazine at the north end: teal sliding lid, two ports; spent drawer beside it
    box((0, 2.0, 0.45), (1.9, 0.85, 0.9), "body", bevel=0.03)
    hatch(-0.15, 2.0, 0.9, 0.95, 0.6)
    box((0.62, 2.0, 0.93), (0.08, 0.7, 0.04), "collar")                         # lid rail
    spent_drawer(0.62, 1.55, 0.25)
    # the conversion block at the south end, finned on top, cable trunks off its base
    box((0, -2.0, 0.4), (2.1, 0.85, 0.8), "body", bevel=0.03)
    fin_bank_x(-0.85, 0.85, -2.3, -1.7, 0.8, 1.02, pitch=0.11)
    for x in (-0.6, 0.0, 0.6):
        trunk([(x, -2.3, 0.35), (x, -2.42, 0.2), (x, -2.42, 0.03)], r=0.08)
        cyl((x, -2.3, 0.35), 0.11, 0.08, "collar", rot=(math.pi / 2, 0, 0), verts=24)
    return dict(dirs=("vertical", "horizontal"), footprint=(3, 5))


def option_b():
    """The Banded Cask: the Reaction Plant's drum stood up, finned at the crown. 3x3, one plate."""
    loft(octagon(1.47, 1.47, 0.45), octagon(1.3, 1.3, 0.4), 0.0, 0.32, "dark")    # hull, battered
    R, Z0, Z1 = 0.92, 0.32, 1.7
    cyl((0, 0, (Z0 + Z1) / 2), R, Z1 - Z0, "body", verts=64)
    for zb in (0.42, 0.86, 1.06):                                                # lead shield bands
        cyl((0, 0, zb), R + 0.04, 0.11, "lead", verts=64)
        for a in range(8):
            ang = a * math.pi / 4 + math.pi / 8
            box(((R + 0.07) * math.cos(ang), (R + 0.07) * math.sin(ang), zb), (0.07, 0.12, 0.15),
                "copper", rz=ang, bevel=0.01)
    for deg in (-125, -105, -90, -75, -55):                                       # the ring of slots
        slot_on_cyl(0, 0, 0, R, math.radians(deg), 0.64, length=0.2)
    # the crown is the radiator: radial fins round the upper cask
    for k in range(28):
        ang = 2 * math.pi * k / 28
        box(((R + 0.2) * math.cos(ang), (R + 0.2) * math.sin(ang), 1.42), (0.42, 0.035, 0.52), "fin",
            rz=ang, bevel=0.005)
    bpy.ops.mesh.primitive_torus_add(major_radius=R + 0.41, minor_radius=0.025, location=(0, 0, 1.66),
                                     major_segments=96, minor_segments=8)
    _finish(bpy.context.active_object, "collar", 0, smooth=True)                   # fin tie ring
    dome((0, 0, Z1), R, 0.3, "lead")
    hatch(0.0, -0.12, 1.97, 0.7, 0.42)                                             # teal fuel hatch
    spent_drawer(0.42, 0.42, 1.86, w=0.26, d=0.2, h=0.1)
    # cable trunk down the east side to the hull
    trunk([(0.6, 0.55, 1.88), (0.95, 0.75, 1.75), (1.22, 0.75, 1.2), (1.22, 0.75, 0.32)], r=0.07)
    trunk([(-0.6, 0.55, 1.88), (-0.95, 0.75, 1.75), (-1.22, 0.75, 1.2), (-1.22, 0.75, 0.32)], r=0.07)
    return dict(dirs=("one",), footprint=(3, 3))


def option_c():
    """The Radiator Cross: a low shielded vault with four radiator vanes on the diagonals. 4x4."""
    loft(octagon(0.95, 0.95, 0.38), octagon(0.85, 0.85, 0.34), 0.0, 0.85, "body")   # the vault
    dome((0, 0, 0.85), 0.55, 0.22, "lead")
    # eight slots ringing the vault's roof edge, the light seen from above
    for k in range(8):
        ang = 2 * math.pi * k / 8 + math.pi / 8
        r = 0.72
        box((r * math.cos(ang), r * math.sin(ang), 0.9), (0.24, 0.1, 0.06), "collar", rz=ang + math.pi / 2,
            bevel=0.006)
        box((r * math.cos(ang), r * math.sin(ang), 0.935), (0.18, 0.05, 0.01), "slot",
            rz=ang + math.pi / 2, bevel=0)
    hatch(0, 0.0, 1.05, 0.55, 0.38)
    # four vanes, root tall at the vault, tapering to the corners
    for q in range(4):
        ang = math.pi / 4 + q * math.pi / 2
        c, s = math.cos(ang), math.sin(ang)
        r0, r1 = 0.75, 2.5
        prof = [(r0, 0.0), (r1, 0.0), (r1, 0.35), (r0, 1.25)]
        me = bpy.data.meshes.new("vane")
        bm = bmesh.new()
        t = 0.12
        a = [bm.verts.new((r * c - (-t) * s, r * s + (-t) * c, z)) for r, z in prof]
        b = [bm.verts.new((r * c - t * s, r * s + t * c, z)) for r, z in prof]
        bm.faces.new(list(reversed(a)))
        bm.faces.new(b)
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((a[i], a[j], b[j], b[i]))
        bm.normal_update()
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new("vane", me)
        sc.collection.objects.link(o)
        _finish(o, "fin", 0.01)
        # ribs across the vane, both faces, and a heat-pipe header along its top edge
        for i in range(9):
            r = r0 + 0.12 + i * (r1 - r0 - 0.2) / 8
            zt = 1.25 - (r - r0) / (r1 - r0) * 0.9
            for side in (-1, 1):
                box((r * c - side * 0.16 * s, r * s + side * 0.16 * c, zt / 2), (0.05, 0.1, zt - 0.04),
                    "collar", rz=ang, bevel=0.004)
        a0 = Vector((r0 * c, r0 * s, 1.29))
        a1 = Vector((r1 * c, r1 * s, 0.39))
        q = (a1 - a0).normalized().to_track_quat("Z", "Y").to_euler()
        cyl(tuple((a0 + a1) / 2), 0.13, (a1 - a0).length, "lead", rot=tuple(q), verts=16)
        box((r1 * c, r1 * s, 0.2), (0.2, 0.2, 0.4), "dark", rz=ang)                # foot at the corner
    # the four bays between the vanes: spent drawer south, conversion block north,
    # cable trunks east and west
    spent_drawer(0, -1.15, 0.0, w=0.42, d=0.3, h=0.3)
    box((0, 1.25, 0.3), (0.8, 0.55, 0.6), "dark", bevel=0.02)
    fin_bank_x(-0.3, 0.3, 1.05, 1.45, 0.6, 0.8, pitch=0.1)
    for s in (-1, 1):
        box((s * 1.2, 0, 0.18), (0.5, 0.5, 0.36), "dark", bevel=0.02)
        trunk([(s * 0.95, 0.0, 0.5), (s * 1.2, 0.0, 0.5), (s * 1.45, 0, 0.3), (s * 1.6, 0, 0.04)], r=0.08)
    return dict(dirs=("one",), footprint=(4, 4))


def option_d():
    """The Twin Cask: one shielded cask per fuel slot, side by side under a radiator spine. 3x4."""
    L = 1.95
    loft(octagon(1.45, L, 0.3), octagon(1.35, L - 0.08, 0.26), 0.0, 0.18, "dark")
    CZ, CR = 0.62, 0.44
    for sx in (-0.7, 0.7):
        for y in (-0.85, 0.85):                                                    # cradle saddles
            box((sx, y, 0.32), (0.75, 0.22, 0.32), "collar", bevel=0.02)
        cyl((sx, 0.05, CZ), CR, 2.6, "body", rot=(math.pi / 2, 0, 0), verts=48)
        for y in (-0.9, -0.1, 0.7):
            cyl((sx, y, CZ), CR + 0.05, 0.14, "lead", rot=(math.pi / 2, 0, 0), verts=48)
        for y in (-0.5, 0.3):
            slot_v(sx + 0.0, y, CZ + CR - 0.01, 0.42)
        # the breech at the north end of each cask: where a cell goes in, painted teal
        cyl((sx, 1.42, CZ), CR + 0.06, 0.18, "teal", rot=(math.pi / 2, 0, 0), verts=48)
        cyl((sx, 1.53, CZ), 0.16, 0.06, "collar", rot=(math.pi / 2, 0, 0), verts=24)
        box((sx, 1.54, CZ + 0.3), (0.22, 0.06, 0.06), "copper", bevel=0.008)        # breech handle
    # the radiator spine standing between and over the casks
    box((0, 0.05, 0.55), (0.34, 2.5, 1.1), "dark", bevel=0.02)
    fin_bank_y(-0.42, 0.42, -1.15, 1.2, 0.9, 1.45, pitch=0.11)
    box((0, 0.02, 1.47), (0.12, 2.4, 0.05), "collar")
    spent_drawer(0, 1.62, 0.18, w=0.36, d=0.24)
    # the converter across the south end, with its cable trunks
    box((0, -1.6, 0.42), (2.7, 0.7, 0.84), "body", bevel=0.03)
    box((0, -1.6, 0.87), (1.6, 0.5, 0.1), "collar")
    for x in (-0.9, -0.3, 0.3, 0.9):
        trunk([(x, -1.86, 0.35), (x, -1.9, 0.2), (x, -1.9, 0.03)], r=0.07)
    return dict(dirs=("vertical", "horizontal"), footprint=(3, 4))


def option_e():
    """The Plug Well: a flat radiator bed round one heavy lead plug, the light a ring at its foot. 4x4."""
    E = 1.96
    loft(octagon(E, E, 0.62), octagon(E - 0.12, E - 0.12, 0.56), 0.0, 0.3, "dark")
    # the bed: four fields of louvred radiator panels, each louvre square to its side
    for q in range(4):
        rz = q * math.pi / 2
        c, s = math.cos(rz), math.sin(rz)
        for i in range(5):
            d = 1.05 + i * 0.17                       # distance out from the centre
            ln = 2 * min(d * 0.95, 1.25)
            x, y = 0 * c - (-d) * s, 0 * s + (-d) * c
            box((x, y, 0.4), (ln, 0.13, 0.025), "fin", rot=(math.radians(35), 0, rz), bevel=0.004)
        box((-(-1.88) * s, (-1.88) * c, 0.36), (2.5, 0.06, 0.12), "collar", rz=rz)    # header bar
    # four corner headers on the chamfers
    for q in range(4):
        ang = math.pi / 4 + q * math.pi / 2
        cyl((1.55 * math.cos(ang), 1.55 * math.sin(ang), 0.45), 0.16, 0.5, "lead", verts=24)
        cyl((1.55 * math.cos(ang), 1.55 * math.sin(ang), 0.72), 0.2, 0.06, "collar", verts=24)
    # the well: a collar ring, a light ring at the plug's foot, and the plug
    cyl((0, 0, 0.42), 0.98, 0.24, "collar", verts=64)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.82, minor_radius=0.045, location=(0, 0, 0.55),
                                     major_segments=96, minor_segments=8)
    _finish(bpy.context.active_object, "slot", 0, smooth=True)
    cyl((0, 0, 0.52), 0.86, 0.04, "recess", verts=64, bevel=0)
    cyl((0, 0, 0.78), 0.74, 0.5, "lead", verts=64)
    for zb in (0.62, 0.92):
        cyl((0, 0, zb), 0.77, 0.07, "collar", verts=64)
    dome((0, 0, 1.03), 0.74, 0.16, "lead")
    for a in range(4):                                                              # lifting lugs
        ang = a * math.pi / 2 + math.pi / 4
        box((0.6 * math.cos(ang), 0.6 * math.sin(ang), 1.08), (0.1, 0.05, 0.16), "copper", rz=ang)
    hatch(0, 0, 1.17, 0.6, 0.36)
    spent_drawer(0.95, -0.95, 0.3, w=0.3, d=0.24)
    for x in (-0.25, 0.25):
        trunk([(x - 1.0, 1.0, 0.4), (x - 1.3, 1.3, 0.35), (x - 1.45, 1.45, 0.04)], r=0.07)
    return dict(dirs=("one",), footprint=(4, 4))


INFO = {"A": option_a, "B": option_b, "C": option_c, "D": option_d, "E": option_e}[OPTION]()

# ---------------------------------------------------------------- render

rig.sun()
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()
rig.camera(*CANVAS, centre_px=CENTRE)


def glow(on):
    sb.inputs["Emission Strength"].default_value = GLOW if on else 0.0


for d in INFO["dirs"]:
    ROOT.rotation_euler.z = math.pi / 2 if d == "horizontal" else 0.0
    for o in OBJS:
        o.visible_camera = True
    GROUND.hide_render, BOUNCE.hide_render = True, False
    glow(True)
    rig.render(f"{OUT_DIR}/{d}-working.png")
    glow(False)
    rig.render(f"{OUT_DIR}/{d}-idle.png")
    for o in OBJS:
        o.visible_camera = False
    GROUND.hide_render, BOUNCE.hide_render = False, True
    rig.render(f"{OUT_DIR}/{d}-shadow.png")

with open(f"{OUT_DIR}/info.txt", "w") as f:
    f.write(f"{OPTION} {INFO['footprint'][0]}x{INFO['footprint'][1]} {' '.join(INFO['dirs'])}\n")
