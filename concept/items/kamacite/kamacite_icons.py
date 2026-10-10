"""Kamacite's item icons: ore, crushed, fines, plate -- one material at four stages.

Rendered by tools/blender/render-icons.sh (icon_rig.py: 45 deg camera, the
buildings' sun and fill, framed to 1 px clear of the canvas at every size):

    BLENDER=/usr/bin/blender tools/blender/render-icons.sh \
        concept/items/kamacite/kamacite_icons.py <out-dir>

Each icon is simplified to its purest meaning (FFF #290) and told apart from its
siblings by silhouette first, then tone, so the four still separate at 8 px:

  ore       four rounded lumps filling the square, an outer crust broken open to
            bright metal
  crushed   a pointed heap of small, sharp-faceted fragments, mostly fresh
            fracture -- a jagged silhouette
  fines     a steep, smooth cone of powder -- the softest shape
  plate     one square plate on its diagonal, as iron-plate.png is

One finish, teal, over a meteorite structure -- see "the finishes" below.

Size by size (FFF #348: make 64, then fix each smaller size): build() takes the
size and simplifies for it -- fewer, larger pieces, larger broken-metal patches,
heavier bevels -- and POST declares the image rules icon_post.py applies.
"""
import colorsys
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Euler, Vector, noise

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))

import icon_rig  # noqa: E402
import rig  # noqa: E402
from materials import layered  # noqa: E402

# ---------------------------------------------------------------- the finishes
#
# The family's colour identity is teal (Liam, 2026-10-10, round 3), as iron ore's is
# blue: the hue sits where vanilla puts it, in the metal and its highlights (the
# base, the worn edges, the etch, the crust's specular), never in the shadows, which
# stay the world's warm grey. Over it, round 2's meteorite structure: the ore's glassy
# black fusion crust pitted with regmaglypts and broken open to metal; the
# Widmanstatten lattice on the fracture faces and the plate's top; brass flecks in the
# plate's metal and as fine glints in the fines (none on the ore or crushed).
#
# Why 160 deg: concept/items/hues.py's survey of vanilla's and Space Age's raw
# materials (lit pixels' mean hue; greys under saturation 0.12 have none) has its
# widest gap between uranium-238 (119) and ice / iron ore / helium-3 (199-201).
# Asked for at ~170, which is 29 off ice; 160 keeps >= 30 clear of both sides. The
# rendered icons measure 160-166 deg, 33-38 off ice (measures.json "hues").
# Brass (48 deg, 3-9 off stone and sulfur) and a temper iridescence (its mean on
# holmium's pink) were tried and set aside.

TEAL = dict(
    # the hue put in: the warm world fill and the camera grade pull a rendered hue
    # warm (put in at 160 it came out 134-150), so it is set past 160 to land there
    h=174, s=0.30,                 # the metal's saturation
    sp=0.20,                       # the powder's
    fleck=("#B07A1E", "#F0B848"),  # schreibersite/troilite, dark to light: the accent
)
FINISHES = ("teal",)


def hsv(h, s, v):
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360, s, v)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def palette(finish):
    c = TEAL
    h, s = c["h"], c["s"]
    return dict(
        base=hsv(h, s, 0.60),            # round 2's #9297A0 was v 0.63; a touch less pale
        bare=hsv(h, s * 0.6, 0.85),      # worn edges: the highlight carries the hue too
        etch=hsv(h, min(1, s * 1.2), 0.30),
        powder=hsv(h, c["sp"], 0.50),
        powder_bare=hsv(h, c["sp"] * 0.6, 0.76),
        spec=hsv(h, min(1, s * 1.6), 1.0),   # the crust's glassy highlight
        fleck=c["fleck"],
    )


FUSION = "#201E1C"            # fusion crust: black glass (round 2)
PLATE_GAIN = 0.9              # the plate a touch less pale than the rest (round 2: p50 141)

# per size: Widmanstatten bands per unit and etch line width (fraction of a band);
# fleck cell scale and spot radius (the plate), and the fines' finer, sparser glints;
# regmaglypt cells per unit of lump radius and depth
WIDMAN = {64: (11.0, 0.12), 32: (7.0, 0.14), 16: (4.0, 0.18), 8: (2.6, 0.2)}
FLECK = {64: (18.0, 0.34), 32: (12.0, 0.36), 16: (7.0, 0.38), 8: (5.0, 0.4)}
GLINTS = {64: (30.0, 0.22), 32: (20.0, 0.26), 16: (11.0, 0.3), 8: (8.0, 0.32)}
DIMPLE = {64: (3.2, 0.10), 32: (2.6, 0.11), 16: (2.0, 0.12), 8: (1.6, 0.12)}
OCTA = [(1, 1, 1), (1, -1, 1), (-1, 1, 1), (1, 1, -1)]
_TURN = Euler((0.43, 0.71, 0.29)).to_matrix()
OCTA_TURNED = [(_TURN @ Vector(n)).normalized() for n in OCTA]


def _coords(g, obj_space):
    if obj_space:
        return g.node("ShaderNodeTexCoord").outputs["Object"]
    return g.node("ShaderNodeNewGeometry").outputs["Position"]


def _widman(g, col, p, size, etch):
    """The etched lattice over col. Each patch shows one set of long parallel bands
    (the set whose noise is highest there), each band its own shade and bordered by a
    thin etched line; patches of different sets meet at angles. The octahedral normals
    are turned by a fixed, unremarkable rotation first: unturned, a face cut square
    to the axes shows only two of the four directions, and the lattice reads as a
    woven grid (round 2's first plate test)."""
    f, w = WIDMAN[size]
    best = shade = lines = None
    wob = g.math("MULTIPLY", g.math("SUBTRACT", g.noise(p, 1.4, detail=2), 0.5), 0.5)
    for i, n in enumerate(OCTA_TURNED):
        dot = g.n.new("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        g.l.new(p, dot.inputs[0])
        dot.inputs[1].default_value = tuple(n)
        u = g.math("ADD", g.math("MULTIPLY", dot.outputs["Value"], f), wob)
        idx = g.math("FLOOR", u)
        fr = g.math("SUBTRACT", u, idx)
        wn = g.n.new("ShaderNodeTexWhiteNoise")
        wn.noise_dimensions = "1D"
        g.l.new(g.math("ADD", idx, 17.0 * i), wn.inputs["W"])
        s_i = wn.outputs["Value"]
        edge = g.math("MINIMUM", fr, g.math("SUBTRACT", 1.0, fr))
        l_i = g.remap(edge, w, w * 0.35)                 # 1 on the band's edge, 0 inside
        dom = g.noise(_shifted(g, p, i), 3.2, detail=2)
        if best is None:
            best, shade, lines = dom, s_i, l_i
        else:
            win = g.math("GREATER_THAN", dom, best)
            shade = g.mixf(win, shade, s_i)
            lines = g.mixf(win, lines, l_i)
            best = g.math("MAXIMUM", dom, best)
    col = g.mulc(col, g.gray(g.remap(shade, 0.0, 1.0, 0.62, 1.25)))
    return g.mixc(g.math("MULTIPLY", lines, 0.7, clamp=True), col, rig.srgb(etch))


def _shifted(g, p, i):
    nd = g.n.new("ShaderNodeVectorMath")
    nd.operation = "ADD"
    g.l.new(p, nd.inputs[0])
    nd.inputs[1].default_value = (5.3 * i, 2.1 * i, 7.7 * i)
    return nd.outputs["Vector"]


def _flecks(g, col, p, table, size, colours, share=0.5):
    scale, rad = table[size]
    vor = g.node("ShaderNodeTexVoronoi", Vector=p, Scale=scale)
    pick = g.node("ShaderNodeSeparateColor", Color=vor.outputs["Color"]).outputs[0]
    spot = g.math("MULTIPLY", g.remap(vor.outputs["Distance"], rad, rad * 0.6),
                  g.math("GREATER_THAN", pick, share))
    tone = g.mixc(g.noise(p, 9.0, detail=1), rig.srgb(colours[0]), rig.srgb(colours[1]))
    return g.mixc(spot, col, tone)


def _metal(size, pal, obj_space=False, top_only=False, flecks=False, gain=1.0):
    """The kamacite metal: tinted base, etched (all over, or on the top face only),
    flecked if asked."""
    def pat(g):
        p = _coords(g, obj_space)
        col = rig.srgb(pal["base"])
        if gain != 1.0:
            col = tuple(c * gain for c in col[:3]) + (1.0,)
        etched = _widman(g, col, p, size, pal["etch"])
        if top_only:
            nz = g.node("ShaderNodeSeparateXYZ", Vector=g.node("ShaderNodeNewGeometry").outputs["Normal"]).outputs["Z"]
            col = g.mixc(g.remap(nz, 0.8, 0.95), col, etched)
        else:
            col = etched
        if flecks:
            col = _flecks(g, col, p, FLECK, size, pal["fleck"])
        return col
    return pat


def _powder(size, pal):
    def pat(g):
        p = _coords(g, False)
        # fewer, finer glints than round 2's (Liam: its fines verged on polka dots)
        return _flecks(g, rig.srgb(pal["powder"]), p, GLINTS, size, pal["fleck"], share=0.78)
    return pat


def _spec_tint(mat, hexcol):
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Specular Tint"].default_value = rig.srgb(hexcol)
    return mat


def materials(finish, size):
    """{role: material} for the finish at a size. Roles: crust, fracture, powder, plate.
    (Metallic 0.45 as round 1 found: at the buildings' 0.8 an item's flat face only
    mirrors the dim world fill.)"""
    pal = palette(finish)
    metal = dict(metal=pal["bare"], paint_metal=0.45, paint_rough=0.38, wear=0.4, rust=0.05,
                 dust=0.0, grime=0.4, jitter=0.06)
    crust = _spec_tint(layered("fusion", FUSION, metal=pal["bare"], paint_metal=0.0, paint_rough=0.2,
                               wear=0.25, rust=0.04, dust=0.0, grime=0.25, jitter=0.05), pal["spec"])
    return {
        "crust": crust,
        # no flecks on the ore or the crushed (round 2: they never read there)
        "fracture": layered("fracture", pal["base"], pattern=_metal(size, pal), **metal),
        "plate": layered("plate", pal["base"], pattern=_metal(size, pal, obj_space=True, top_only=True,
                                                             flecks=True, gain=PLATE_GAIN), **metal),
        "powder": layered("powder", pal["powder"], metal=pal["powder_bare"], paint_metal=0.3, paint_rough=0.8,
                          wear=0.1, rust=0.03, dust=0.0, grime=0.4, jitter=0.05, pattern=_powder(size, pal)),
    }


# ---------------------------------------------------------------- geometry

def _link(bm, name, mats, smooth):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    for p in me.polygons:
        p.use_smooth = smooth
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _patches(bm, seed, freq, share):
    """Face material 1 (broken metal) where low-frequency noise is high."""
    off = Vector((seed * 7.1, seed * 3.3, seed * 5.7))
    for f in bm.faces:
        c = f.calc_center_median()
        f.material_index = 1 if noise.noise(c * freq + off) > 1 - 2 * share else 0


def lump(name, mats, seed, radius, squash, rough, metal_freq, metal_share, subdiv=4, dimples=None):
    """A rounded ore lump: a noisy sphere, sat on its flattened underside. dimples
    (cells, depth): regmaglypts -- Voronoi cells pressed in at their centres, so
    shallow cups meet in ridges."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    off = Vector((seed * 1.7, seed * 2.9, seed * 0.6))
    for v in bm.verts:
        d = v.co.normalized()
        k = 1 + rough * noise.fractal(d * 1.6 + off, 0.6, 2.0, 4) + 0.5 * rough * noise.noise(d * 4.5 + off)
        if dimples:
            cells, depth = dimples
            dist, _ = noise.voronoi(d * cells + off, distance_metric="DISTANCE")
            k += depth * (min(dist[0], 0.75) - 0.4)
        v.co = d * k
        v.co.z *= squash
    zmin = min(v.co.z for v in bm.verts)
    floor = zmin * 0.65
    for v in bm.verts:
        v.co.z = max(v.co.z, floor) - floor
        v.co *= radius
    _patches(bm, seed, metal_freq, metal_share)
    return _link(bm, name, mats, smooth=True)


def shard(name, mats, rng, size, metal_share):
    """A sharp fragment: the convex hull of a few points, flat-shaded."""
    bm = bmesh.new()
    pts = []
    for _ in range(rng.randint(7, 10)):
        v = Vector((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1))).normalized()
        pts.append(Vector((v.x, v.y * rng.uniform(0.6, 1.0), v.z * rng.uniform(0.5, 0.9))) * size)
    for p in pts:
        bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    for f in bm.faces:
        f.material_index = 1 if rng.random() < metal_share else 0
    return _link(bm, name, mats, smooth=False)


def place(ob, loc, rot=(0, 0, 0)):
    ob.location = loc
    ob.rotation_euler = rot
    return ob


# ---------------------------------------------------------------- the items

def ore(finish, size):
    """Three lumps, as iron-ore.png's four: one big in front, two behind. Fewer, larger
    broken-metal patches as the size drops, so they stay a pixel or more."""
    M = materials(finish, size)
    mats = (M["crust"], M["fracture"])
    freq = {64: 2.2, 32: 1.8, 16: 1.3, 8: 1.0}[size]
    rough = {64: 0.22, 32: 0.2, 16: 0.16, 8: 0.12}[size]
    dim = DIMPLE[size]
    # a cluster that fills the square, as vanilla's ores do (their bounding boxes are
    # 62-64 px tall; the first trial's row of three was 41 px tall and too thin)
    obs = [place(lump("ore_a", mats, 3, 0.42, 0.78, rough, freq, 0.48, dimples=dim), (0.1, -0.32, 0)),
           place(lump("ore_b", mats, 11, 0.32, 0.85, rough, freq, 0.44, dimples=dim), (-0.46, 0.18, 0)),
           place(lump("ore_c", mats, 19, 0.3, 0.85, rough, freq, 0.44, dimples=dim), (0.5, 0.3, 0)),
           place(lump("ore_e", mats, 33, 0.27, 0.9, rough, freq, 0.44, dimples=dim), (-0.02, 0.72, 0))]
    if size >= 32:                          # a pebble: detail that turns to noise below 32
        obs.append(place(lump("ore_d", mats, 27, 0.13, 0.8, rough, freq, 0.3, subdiv=3), (-0.5, -0.42, 0)))
    return obs


def crushed(finish, size):
    """A pointed heap of fragments, mostly fresh fracture; fewer, bigger pieces small."""
    M = materials(finish, size)
    mats = (M["crust"], M["fracture"])
    n, s = {64: (40, 0.17), 32: (28, 0.2), 16: (16, 0.25), 8: (9, 0.3)}[size]
    rng = random.Random(5)
    R, H = 0.45, 0.78
    obs = []
    for i in range(n):
        # fill the cone from the bottom ring up, so the heap reads as one pile
        f = (i + 0.5) / n
        rr = R * (1 - f) ** 0.7 * rng.uniform(0.6, 1.0)
        a = rng.uniform(0, 2 * math.pi) if i else 0
        z = H * (1 - rr / R) * 0.8
        sz = s * rng.uniform(0.8, 1.2)
        ob = shard(f"crushed_{i}", mats, rng, sz, 0.7)
        loc = (rr * math.cos(a), rr * math.sin(a), z)
        place(ob, loc, (rng.uniform(0, 6.3), rng.uniform(0, 6.3), rng.uniform(0, 6.3)))
        _broken_ore(ob, loc, random.Random(100 + i))   # its own stream: the heap's layout stays round 2's
        obs.append(ob)
    return obs


def _broken_ore(ob, loc, rng):
    """Crushed reads as broken ore (round 3): the faces a fragment turns outward from
    the heap keep the ore's crust, the rest are bright cut breaks -- and a few outer
    faces are breaks too, so no fragment is all crust."""
    turn = ob.rotation_euler.to_matrix()
    out = Vector((loc[0], loc[1], 0.55)).normalized()
    for poly in ob.data.polygons:
        n = turn @ poly.normal
        poly.material_index = 0 if n.dot(out) > 0.45 and rng.random() < 0.35 else 1


def fines(finish, size):
    """A smooth cone of powder, the peak rounded. (The first
    trial's low dome read as a disc from 45 deg, and loose grains at its foot as
    rivets: gone.) Its surface grain is coarser as the size drops."""
    M = materials(finish, size)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=96, v_segments=48, radius=1.0)
    # steep for powder (~58 deg): from a 45 deg camera a cone's peak only clears its
    # own back rim if it is taller than it is wide; round 3's 0.55 / 0.6 read as a disc
    R, H = 0.5, 0.82
    grain = {64: 0.05, 32: 0.06, 16: 0.04, 8: 0.0}[size]
    for v in bm.verts:
        r = min(1.0, math.hypot(v.co.x, v.co.y))
        if v.co.z <= 0:                 # the underside: a flat disc under the rim
            v.co.x, v.co.y, v.co.z = v.co.x * R * 0.98, v.co.y * R * 0.98, 0.0
            continue
        # angle of repose, the top rounded off
        prof = (1 - r) * (1 - 0.12 * (1 - r) ** 8)          # straight flanks, the peak just rounded
        jit = 1 + 0.06 * noise.noise(v.co * 3.0 + Vector((4, 1, 7)))
        v.co.x, v.co.y = v.co.x * R * jit, v.co.y * R * jit
        v.co.z = H * prof * (1 + grain * noise.noise(v.co * 14.0) + 0.05 * noise.noise(v.co * 4.0))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    return [_link(bm, "fines", (M["powder"],), smooth=True)]


def plate(finish, size):
    """One plate on its diagonal; its bevel grows as the size drops, so the lit edge
    stays a line a pixel wide."""
    M = materials(finish, size)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.z = (v.co.z + 0.5) * 0.14             # vanilla's plates: ~4-5 px of edge at 64
    ob = _link(bm, "plate", (M["plate"],), smooth=False)
    bev = ob.modifiers.new("bevel", "BEVEL")
    bev.width = {64: 0.03, 32: 0.035, 16: 0.05, 8: 0.06}[size]
    bev.segments = 2
    bev.limit_method = "ANGLE"
    ob.rotation_euler = (0, 0, math.radians(45))
    return [ob]


ITEMS = {"kamacite-ore": ore, "crushed-kamacite": crushed, "kamacite-fines": fines, "kamacite-plate": plate}

# icon_post.py's rules, per size: heavier as the size drops -- sharper, more
# contrast, a harder silhouette, a stronger outline where the object's edge sits
# close to the slot's or the ground's value (dark crust on the dark slot: round 4's
# ore stepped 27 L from the slot at its outline, vanilla's analogues 35-71)
_RULES = {
    64: {"alpha": [16, 245], "rim": [0.7, 36]},
    32: {"sharpen": [0.6, 50], "alpha": [20, 235], "rim": [0.7, 38]},
    16: {"contrast": 1.25, "sharpen": [0.5, 90], "alpha": [48, 208], "rim": [0.8, 40]},
    8: {"contrast": 1.35, "sharpen": [0.5, 80], "alpha": [72, 184], "rim": [0.9, 44]},
}
# and per item: the plate's and the powder's flat faces carry little light and shade
# of their own (round 5: the plate's p95 135-139, vanilla's analogues 142-222), so
# their tones are spread at 64 and 32 as well
_SPREAD = {"kamacite-plate": 1.25, "kamacite-fines": 1.2, "crushed-kamacite": 1.25}
# round 2: the ore's black fusion crust sits on the dark slot, so its outline is pushed
# harder than the others'
# round 3: harder still (round 2's ore stepped 33.8 L off the slot, vanilla 35-71)
_RIM = {"kamacite-ore": {64: [1.0, 54], 32: [1.0, 54], 16: [1.0, 54], 8: [1.0, 56]},
        # and the crushed heap, now crusted (round 3's first runs: 24-26 L off the ground)
        "crushed-kamacite": {64: [0.9, 46], 32: [0.9, 46], 16: [0.9, 46], 8: [1.0, 50]}}


def _rules(name):
    out = {}
    for size, r in _RULES.items():
        r = dict(r)
        if name in _SPREAD and size >= 32:
            r["contrast"] = _SPREAD[name]
        if name in _RIM:
            r["rim"] = _RIM[name][size]
        out[size] = r
    return out


POST = {name: _rules(name) for name in ITEMS}

icon_rig.main(ITEMS, FINISHES, POST)
