"""The radiant family's icons: chunk, fuel, spent cell, solution.

Rendered by tools/blender/render-icons.sh (icon_rig.py: 45 deg camera, the
buildings' sun and fill, framed to 1 px clear of the canvas at every size):

    BLENDER=/usr/bin/blender tools/blender/render-icons.sh \
        concept/items/radiant/radiant_icons.py <out-dir>

The family's colour is the radiant solution's blue (Liam, 2026-10-10): the
fluid's base_color (0.12, 0.39, 1.0) #1F63FF, rising to its flow_color
(0.45, 0.68, 1.0) #73ADFF where the light is brightest -- hue ~222. (Two
earlier directions were set aside: the specs' green-white #A8E8C0, which put
the solution alone in blue, and the green-white drop that followed it.) It is
light, never paint: it glows in the rock's cracks and in the cell's windows,
and everything round it is the generator's own metal -- armour #4A463F ->
#6E685C, shielding collars #3B3B40, copper #8A5A32 -> #C88A4A.

  radiant-chunk     one broken rock of the Core's slate, filling the square as
                    vanilla's asteroid chunks do, cracked through with the glow
  radiant-fuel      a hexagonal cell lying on the diagonal (the old icon's form):
                    a glowing rod in a six-railed cage, dark collars at each end
  sae-spent-cell    the same cell, the rod gone dark -- as vanilla's depleted
                    uranium cell is its fresh cell with the light out
  radiant-solution  a glossy drop, as vanilla's liquids are: deep navy at its
                    rim, lit from inside to the flow colour at its thickest --
                    the colour depth of vanilla's fluoroketone and ammoniacal
                    solution, not round 1's flat saturated fill

Size by size (FFF #348): fewer, thicker veins, one band instead of two, heavier
rails as the size drops; POST declares icon_post.py's rules.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
sys.path.insert(0, os.path.join(REPO, "concept", "items"))

import icon_rig  # noqa: E402
import rig  # noqa: E402
from icon_kit import add_glow, glossy, lathe, lift, link, obj_coords, place  # noqa: E402
from materials import layered  # noqa: E402

FINISHES = ("radiant",)

GLOW = ("#1F63FF", "#73ADFF")      # the family's light, dim to bright: base_color to flow_color
GLOW_EMIT = ("#1F63FF", "#73ADFF")  # what is emitted; measured against the rendered hue (measures.json)
SLATE = "#4E4D4B"                  # the Core's rock (map-gen: "rocks ... in slate")
SLATE_BARE = "#807E7A"
ARMOUR = "#8A8476"
ARMOUR_BARE = "#B0AAA0"
COLLAR = "#3B3B40"
COPPER = ("#8A5A32", "#C88A4A")
SOLUTION = ("#0C2C84", "#000206")   # the drop's body and its rim: the family's blue, deep; the rim near
                                   # black, so the warm fill it catches at grazing reads as no colour (round 2's tan edge)

# per size: crack cells per unit, crack width (distance-to-edge), and how much of
# the network survives the break-up noise (lower: more of it)
VEINS = {64: (2.8, 0.045, 0.47), 32: (2.3, 0.055, 0.47), 16: (1.7, 0.08, 0.45), 8: (1.3, 0.11, 0.44)}
GLOW_STRENGTH = 1.1        # higher clips to white under the camera grade (round 1: 3.0 read white)
CHUNK_GLOW = 1.7           # the chunk's cracks brighter than the rod: thin lines need it to read at 16 px


# ---------------------------------------------------------------- materials

def _veins(size):
    cells, width, keep = VEINS[size]

    def mask(g):
        p = obj_coords(g)
        warp = g.node("ShaderNodeVectorMath")
        warp.operation = "ADD"
        g.l.new(p, warp.inputs[0])
        nz = g.node("ShaderNodeTexNoise", Vector=p, Scale=2.5, Detail=2.0)
        g.l.new(nz.outputs["Color"], warp.inputs[1])
        vor = g.node("ShaderNodeTexVoronoi", Vector=warp.outputs["Vector"], Scale=cells)
        vor.feature = "DISTANCE_TO_EDGE"
        line = g.remap(vor.outputs["Distance"], width, width * 0.3)
        # break the network up: cracks, not a net
        part = g.remap(g.noise(p, 3.2, detail=2), keep - 0.03, keep + 0.03)
        return g.math("MULTIPLY", line, part, clamp=True)
    return mask


def rock_mat(size):
    vein = _veins(size)
    cells, width, keep = VEINS[size]

    def pattern(g):
        # the rock beside a crack is scorched dark, so the light sits in a groove
        m = vein(g)
        return g.mixc(m, rig.srgb(SLATE), rig.srgb("#1E2422"))
    m = layered("slate", SLATE, metal=SLATE_BARE, paint_metal=0.4, paint_rough=0.45, wear=0.45,
                rust=0.0, dust=0.0, grime=0.5, jitter=0.05, pattern=pattern)
    _rock_bump(m, size)
    return add_glow(m, vein, GLOW_EMIT, CHUNK_GLOW)


def _rock_bump(m, size):
    """Broken-rock relief over layered's paint bump: the flat hull faces read as
    plastic without it (round 2)."""
    from materials import _G
    g = _G(m)
    bsdf = g.n["Principled BSDF"]
    old = [n for n in g.n if n.bl_idname == "ShaderNodeBump"][0]
    p = obj_coords(g)
    h = g.math("ADD", g.noise(p, {64: 9.0, 32: 7.0, 16: 4.5, 8: 3.0}[size], detail=6, rough=0.65),
               g.math("MULTIPLY", g.noise(p, 30.0, detail=3), 0.4))
    bump = g.node("ShaderNodeBump", Strength={64: 0.7, 32: 0.6, 16: 0.45, 8: 0.3}[size], Distance=0.05, Height=h)
    g.l.new(old.outputs["Normal"], bump.inputs["Normal"])
    g.l.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def metal(name, paint, bare, metalness=0.45, rough=0.4, wear=0.4):
    return layered(name, paint, metal=bare, paint_metal=metalness, paint_rough=rough, wear=wear,
                   rust=0.04, dust=0.0, grime=0.45, jitter=0.06)


def rod_mat(lit):
    if lit:
        m = glossy("rod", "#1A2C66", rough=0.3, coat=0.5)

        def mask(g):
            # brightest down the rod's middle, a little uneven along it
            p = obj_coords(g)
            return g.remap(g.noise(p, 3.0, detail=2), 0.3, 0.7, 0.75, 1.0)
        return add_glow(m, mask, GLOW_EMIT, GLOW_STRENGTH)
    # spent: dark glass over a dead rod, a trace of the light left in it
    m = glossy("rod_spent", "#1C2230", rough=0.25, coat=0.8)

    def mask(g):
        return g.remap(g.noise(obj_coords(g), 3.0, detail=2), 0.45, 0.7, 0.0, 1.0)
    # a residual blue left in the dead rod: "spent radiant", not a copper cell
    return add_glow(m, mask, ("#12306E", "#2252B0"), 0.6)


# ---------------------------------------------------------------- the chunk

def chunk(finish, size):
    """One broken rock: the convex hull of points on a lumpy ellipsoid, flat
    fracture faces, a small bevel so their edges catch the sun."""
    rng = random.Random(7)
    bm = bmesh.new()
    n = {64: 15, 32: 14, 16: 12, 8: 10}[size]
    for i in range(n):
        v = Vector((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1))).normalized()
        k = 1 + 0.18 * noise.noise(v * 2.0 + Vector((3, 1, 2)))
        bm.verts.new(Vector((v.x * 0.62, v.y * 0.52, v.z * 0.5)) * k)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    ob = link(bm, "chunk", (rock_mat(size),), smooth=False)
    bev = ob.modifiers.new("bevel", "BEVEL")
    bev.width = {64: 0.012, 32: 0.016, 16: 0.022, 8: 0.03}[size]
    bev.segments = 2
    bev.limit_method = "ANGLE"
    ob.rotation_euler = (math.radians(12), math.radians(-8), math.radians(20))
    return lift([ob])


# ---------------------------------------------------------------- the cell

def _hex(bm, r, z0, z1, rot=0.0):
    """A hexagonal prism along Z, flat faces at rot."""
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=r, radius2=r, depth=z1 - z0)
    vs = res["verts"]
    bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0), matrix=_rotz(rot))
    bmesh.ops.translate(bm, verts=vs, vec=(0, 0, (z0 + z1) / 2))
    return vs


def _rotz(a):
    from mathutils import Matrix
    return Matrix.Rotation(a, 3, "Z")


def _part(name, mats, build, smooth=False, bevel=None):
    bm = bmesh.new()
    build(bm)
    ob = link(bm, name, mats, smooth)
    if bevel:
        b = ob.modifiers.new("bevel", "BEVEL")
        b.width = bevel
        b.segments = 2
        b.limit_method = "ANGLE"
    return ob


def cell(finish, size, lit):
    """Built along Z, then laid down along the diagonal. A flat face of the hex
    turned up to the camera."""
    L, R = 0.62, 0.34                       # half-length of the rod, its radius
    cage = metal("cage", ARMOUR, ARMOUR_BARE)
    collar = metal("collar", COLLAR, "#6A6A72", metalness=0.6, rough=0.35, wear=0.3)
    copper = metal("copper", COPPER[0], COPPER[1], metalness=0.7, rough=0.35, wear=0.5)
    rails = {64: 0.07, 32: 0.08, 16: 0.10, 8: 0.12}[size]
    bands = {64: (0.0,), 32: (0.0,), 16: (0.0,), 8: ()}[size]
    bev = {64: 0.012, 32: 0.016, 16: 0.022, 8: 0.03}[size]
    rot = math.radians(30)                 # a flat face up
    parts = []
    parts.append(_part("rod", (rod_mat(lit),), lambda bm: _hex(bm, R, -L, L, rot)))
    # six rails along the corners, standing just proud of the rod
    def rails_bm(bm):
        for i in range(6):
            a = rot + i * math.pi / 3
            c = Vector((math.cos(a), math.sin(a), 0)) * (R + rails * 0.15)
            res = bmesh.ops.create_cube(bm, size=1.0)
            vs = res["verts"]
            bmesh.ops.scale(bm, verts=vs, vec=(rails, rails, 2 * L))
            bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0), matrix=_rotz(a))
            bmesh.ops.translate(bm, verts=vs, vec=c)
        for z in bands:
            _hex(bm, R + rails * 0.55, z - rails * 0.6, z + rails * 0.6, rot)
    parts.append(_part("rails", (cage,), rails_bm, bevel=bev))
    # the collars: heavier, wider hexes at each end, and an end plate with a copper boss
    cl = {64: 0.26, 32: 0.27, 16: 0.3, 8: 0.32}[size]
    def collars_bm(bm):
        for s in (-1, 1):
            z0, z1 = (L - 0.02, L + cl) if s > 0 else (-L - cl, -L + 0.02)
            _hex(bm, R + 0.12, z0, z1, rot)
    parts.append(_part("collars", (collar,), collars_bm, bevel=bev * 1.5))
    if size >= 16:
        def boss_bm(bm):
            for s in (-1, 1):
                z = s * (L + cl)
                res = bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=R * 0.55,
                                            radius2=R * 0.45, depth=0.08)
                bmesh.ops.translate(bm, verts=res["verts"], vec=(0, 0, z + s * 0.035))
        parts.append(_part("boss", (copper,), boss_bm, smooth=True, bevel=bev))
    # lay it down: Z -> X, then turned 32 deg about Z so it runs lower-left to upper-right
    root = bpy.data.objects.new("cell", None)
    bpy.context.scene.collection.objects.link(root)
    for p in parts:
        p.parent = root
    from mathutils import Euler
    m = Euler((0, 0, math.radians(38))).to_matrix().to_4x4() @ Euler((0, math.radians(90), 0)).to_matrix().to_4x4()
    root.matrix_world = m
    bpy.context.view_layer.update()
    # lift: parts have a parent, so move the root
    zmin = min((p.matrix_world @ Vector(c)).z for p in parts for c in p.bound_box)
    root.location.z -= zmin
    return parts


def fuel(finish, size):
    return cell(finish, size, True)


def spent(finish, size):
    return cell(finish, size, False)


# ---------------------------------------------------------------- the solution

def drop_profile(n=48, p=1.15, aspect=0.66):
    """A teardrop, bottom to tip: x = sin t * sin(t/2)^p, z = cos t, t from pi to 0
    (round below, a concave flank to a point above)."""
    pts = []
    for i in range(n + 1):
        t = math.pi * (1 - i / n)
        x = math.sin(t) * math.sin(t / 2) ** p
        z = math.cos(t)               # the point at t = 0, on top
        pts.append((max(0.0, x) * aspect / 0.77, z))
    pts[0] = (0.0, pts[0][1])
    pts[-1] = (0.0, pts[-1][1])
    return pts


def drop(name, mat):
    """A drop seen side-on: its axis turned toward the 45 deg camera's up."""
    ob = lathe(name, drop_profile(), (mat,), segments=64, smooth=True)
    ob.rotation_euler = (math.radians(-45), 0, 0)
    return lift([ob])


def solution(finish, size):
    m = glossy("solution", SOLUTION[0], rough=0.2, coat=0.6, coat_rough=0.15)
    from materials import _G
    g = _G(m)
    bsdf = g.n["Principled BSDF"]
    face = g.node("ShaderNodeLayerWeight", Blend=0.5).outputs["Facing"]
    # colour depth: the body darkens steadily from the middle out to a deep rim, as
    # vanilla's drops do (round 3's rim term reached only the last pixel)
    g.l.new(g.mixc(g.remap(face, 0.1, 0.8), rig.srgb(SOLUTION[0]), rig.srgb(SOLUTION[1])), bsdf.inputs["Base Color"])
    # and no fresnel sheen at the silhouette: the grazing coat mirrors the warm world
    # fill and the edge reads tan (rounds 1-3), where vanilla's deepest colour is
    # (round 3: the coat alone off left the base layer's fresnel to do it; both off now)
    g.l.new(g.remap(face, 0.5, 0.85, 0.25, 0.0), bsdf.inputs["Specular IOR Level"])
    g.l.new(g.remap(face, 0.5, 0.85, 0.6, 0.0), bsdf.inputs["Coat Weight"])

    def core(g):
        face = g.node("ShaderNodeLayerWeight", Blend=0.35).outputs["Facing"]
        # the light inside: strongest where the drop is thickest toward the eye,
        # and a little more in its round belly than toward the point
        z = g.node("ShaderNodeSeparateXYZ", Vector=obj_coords(g)).outputs["Z"]
        belly = g.remap(z, 0.6, -0.4, 0.55, 1.0)
        return g.math("MULTIPLY", g.remap(face, 0.32, 0.0), belly, clamp=True)
    add_glow(m, core, GLOW, 1.1)
    return drop("radiant_solution", m)


ITEMS = {"radiant-chunk": chunk, "radiant-fuel": fuel, "sae-spent-cell": spent,
         "radiant-solution": solution}

# icon_post.py's rules, per size: kamacite's (concept/items/kamacite/kamacite_icons.py)
_RULES = {
    64: {"alpha": [16, 245], "rim": [0.7, 36]},
    32: {"sharpen": [0.6, 50], "alpha": [20, 235], "rim": [0.7, 38]},
    16: {"contrast": 1.25, "sharpen": [0.5, 90], "alpha": [48, 208], "rim": [0.8, 40]},
    8: {"contrast": 1.35, "sharpen": [0.5, 80], "alpha": [72, 184], "rim": [0.9, 44]},
}
# and per item, as kamacite's ore: the cells' dark collars and the drop's deep rim sit
# close to the ground's value (round 8: 22-26 L off the ground, vanilla's analogues 29-63),
# so their outline is pushed harder; and the spent cell's flat tones are spread (p95 102)
_RIM = {n: {64: [1.0, 50], 32: [1.0, 50], 16: [1.0, 50], 8: [1.0, 52]}
        for n in ("radiant-fuel", "sae-spent-cell")}
# the drop's outline on the ground: its rim is near black now, so the harder rule
# sinks it further from the ground (round 2: 19.7 L off the ground)
_RIM["radiant-solution"] = {64: [1.0, 48], 32: [1.0, 48], 16: [1.0, 48], 8: [1.0, 50]}
_SPREAD = {"sae-spent-cell": 1.45, "radiant-chunk": 1.15}


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
