"""The radiant family's icons in look B (radiant-look, chosen by Liam 2026-10-12): the light
is a lamp behind smoked glass or dark rock, not paint.

A proposal beside the signed-off radiant_icons.py, which stays as it is. Rendered the
same way, by tools/blender/render-icons.sh (icon_rig.py's camera, sun and framing;
icon_post.py's per-size rules):

    tools/blender/render-icons.sh \
        concept/items/radiant/radiant_icons_b.py <out-dir>

The shared helper (tools/blender, branch radiant-look) was not ready when this was
made, so the recipe is the study's look B, taken directly from
concept/radiant-look/model/look_pieces.py on that branch:

  light    B's glow ramp, saturated throughout, no pale top:
           #000000 > #04103A > #0B2A8C > #1F63FF > #5A9CFF, on a "core" term (bright in
           the thick middle of the body, soft falloff to deep navy at its edges)
  plate    the liquid itself a dim navy (#0C1838), the glass in front of it smoked
           (#55606E, transmission 0.85), dark internals (#1A1C22) silhouetted against
           the light

What changes against radiant_icons.py, item by item (the family's form, lead and
worn finish stay: the same chunk hull, the same hex cell, rails, collars, copper):

  radiant-fuel      the pale rod becomes a lamp behind smoked glass: a smoked hex
                    sleeve over a navy liquid lit from its core, a dark heater rod
                    and three baffle plates silhouetted in it
  sae-spent-cell    the same cell with the light out: the navy liquid behind the
                    smoked glass, the heater rod and baffles barely readable
  radiant-chunk     the veins as light inside the rock: a narrow hot line on the ramp's
                    top, a wider dim seam round it falling to navy in the scorched groove
  radiant-solution  the same dark liquid with a lit core: a navy body, light rising
                    from its belly on the ramp, darker sediment swirls through the light,
                    a matte skin with one soft highlight instead of a lacquer coat
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
sys.path.insert(0, os.path.join(REPO, "concept", "items"))

import icon_rig  # noqa: E402
import rig  # noqa: E402
from icon_kit import lathe, lift, link, obj_coords  # noqa: E402
from materials import _G, layered  # noqa: E402

FINISHES = ("radiant",)

# B's ramps (look_pieces.py RAMPS["Bglow"]; the plate's liquid)
BGLOW = [(0.0, "#000000"), (0.25, "#04103A"), (0.55, "#0B2A8C"), (0.8, "#1F63FF"), (1.0, "#5A9CFF")]
LIQUID = "#0C1838"
SMOKE = "#55606E"
INTERNAL = "#1A1C22"

SLATE = "#4E4D4B"
SLATE_BARE = "#807E7A"
ARMOUR = "#8A8476"
ARMOUR_BARE = "#B0AAA0"
COLLAR = "#3B3B40"
COPPER = ("#8A5A32", "#C88A4A")

VEINS = {64: (2.8, 0.045, 0.47), 32: (2.3, 0.055, 0.47), 16: (1.7, 0.08, 0.45), 8: (1.3, 0.11, 0.44)}
CELL_GLOW = {64: 4.2, 32: 4.2, 16: 4.4, 8: 4.5}     # the lamp's strength (look B's glow pass: 2.3; the smoked glass takes ~half)
CHUNK_GLOW = 0.95                                     # open light: under the clip with the sun on the rock added (round 4: 1.2 still went #76D1FF)
CHUNK_GAIN = {64: 1.6, 32: 1.6, 16: 1.8, 8: 1.9}
DROP_GLOW = 1.0
DROP_GAIN = 1.5


# ---------------------------------------------------------------- B's pieces

def ramp(g, fac, stops=BGLOW):
    nd = g.node("ShaderNodeValToRGB", Fac=fac)
    cr = nd.color_ramp
    cr.elements[0].position, cr.elements[0].color = stops[0][0], rig.srgb(stops[0][1])
    cr.elements[1].position, cr.elements[1].color = stops[-1][0], rig.srgb(stops[-1][1])
    for p, h in stops[1:-1]:
        e = cr.elements.new(p)
        e.color = rig.srgb(h)
    return nd.outputs["Color"]


def emit(m, fac, strength, gain=1.0):
    """B's light on a material: fac (0..1) times gain, clamped, through the glow ramp; emission
    x strength. Brightness is raised by gain, not strength: past ~1.2 the ramp's top
    (#5A9CFF, linear blue 1.0) clips in blue under the camera grade and its green climbs --
    the core turns cyan (round 3: #89F4FF, hue 186)."""
    g = _G(m)
    b = g.n["Principled BSDF"]
    if gain != 1.0:
        fac = g.math("MINIMUM", g.math("MULTIPLY", fac, gain), 1.0)
    g.l.new(ramp(g, fac), b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = strength
    return m


def plain(name, hexcol, rough=0.4, metallic=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb(hexcol)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Coat Weight"].default_value = coat
    return m


def smoked_glass(name="smoke"):
    m = plain(name, SMOKE, rough=0.08)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["IOR"].default_value = 1.47
    b.inputs["Transmission Weight"].default_value = 0.85
    b.inputs["Coat Weight"].default_value = 0.4
    return m


def metal(name, paint, bare, metalness=0.45, rough=0.4, wear=0.4):
    return layered(name, paint, metal=bare, paint_metal=metalness, paint_rough=rough, wear=wear,
                   rust=0.04, dust=0.0, grime=0.45, jitter=0.06)


# ---------------------------------------------------------------- the chunk

def rock_mat(size):
    cells, width, keep = VEINS[size]

    def field(g):
        """distance-to-edge of the crack network, and the break-up mask"""
        p = obj_coords(g)
        warp = g.node("ShaderNodeVectorMath")
        warp.operation = "ADD"
        g.l.new(p, warp.inputs[0])
        nz = g.node("ShaderNodeTexNoise", Vector=p, Scale=2.5, Detail=2.0)
        g.l.new(nz.outputs["Color"], warp.inputs[1])
        vor = g.node("ShaderNodeTexVoronoi", Vector=warp.outputs["Vector"], Scale=cells)
        vor.feature = "DISTANCE_TO_EDGE"
        part = g.remap(g.noise(p, 3.2, detail=2), keep - 0.03, keep + 0.03)
        return vor.outputs["Distance"], part

    def pattern(g):
        d, part = field(g)
        # the scorched groove: wider than the light, so the light sits deep in dark rock
        groove = g.math("MULTIPLY", g.remap(d, width * 2.2, width * 0.5), part, clamp=True)
        return g.mixc(groove, rig.srgb(SLATE), rig.srgb("#141820"))
    m = layered("slate", SLATE, metal=SLATE_BARE, paint_metal=0.4, paint_rough=0.45, wear=0.45,
                rust=0.0, dust=0.0, grime=0.5, jitter=0.05, pattern=pattern)
    _rock_bump(m, size)
    g = _G(m)
    d, part = field(g)
    # light: a hot narrow line on the ramp's top, a soft seam falling to navy round it
    hot = g.remap(d, width * 0.75, width * 0.15)
    seam = g.remap(d, width * 1.9, width * 0.2)
    fac = g.math("MULTIPLY", g.math("ADD", g.math("MULTIPLY", seam, 0.62), g.math("MULTIPLY", hot, 0.38)),
                 part, clamp=True)
    return emit(m, fac, CHUNK_GLOW, CHUNK_GAIN[size])


def _rock_bump(m, size):
    g = _G(m)
    bsdf = g.n["Principled BSDF"]
    old = [n for n in g.n if n.bl_idname == "ShaderNodeBump"][0]
    p = obj_coords(g)
    h = g.math("ADD", g.noise(p, {64: 9.0, 32: 7.0, 16: 4.5, 8: 3.0}[size], detail=6, rough=0.65),
               g.math("MULTIPLY", g.noise(p, 30.0, detail=3), 0.4))
    bump = g.node("ShaderNodeBump", Strength={64: 0.7, 32: 0.6, 16: 0.45, 8: 0.3}[size], Distance=0.05, Height=h)
    g.l.new(old.outputs["Normal"], bump.inputs["Normal"])
    g.l.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def chunk(finish, size):
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
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=r, radius2=r, depth=z1 - z0)
    vs = res["verts"]
    bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0), matrix=Matrix.Rotation(rot, 3, "Z"))
    bmesh.ops.translate(bm, verts=vs, vec=(0, 0, (z0 + z1) / 2))
    return vs


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


def liquid_mat(lit, size, L, R):
    """The navy liquid in the cell; lit, its core glows on B's ramp: brightest along the
    axis in the middle of the length, falling to navy at the glass and toward the collars."""
    m = plain("liquid" if lit else "liquid_spent", LIQUID, rough=0.3)
    if not lit:
        return m
    g = _G(m)
    s = g.node("ShaderNodeSeparateXYZ", Vector=obj_coords(g)).outputs
    face = g.node("ShaderNodeLayerWeight", Blend=0.5).outputs["Facing"]
    across = g.math("POWER", g.math("SUBTRACT", 1.0, face, clamp=True), 0.6)
    along = g.math("SUBTRACT", 1.0, g.math("POWER", g.math("ABSOLUTE", g.math("DIVIDE", s["Z"], L)), 3.0),
                   clamp=True)
    flick = g.remap(g.noise(obj_coords(g), 2.2, detail=2), 0.3, 0.7, -0.08, 0.08)
    fac = g.math("ADD", g.math("MULTIPLY", g.math("MULTIPLY", across, along), 0.95), flick, clamp=True)
    return emit(m, fac, CELL_GLOW[size])


def cell(finish, size, lit):
    L, R = 0.62, 0.34
    cage = metal("cage", ARMOUR, ARMOUR_BARE)
    collar = metal("collar", COLLAR, "#6A6A72", metalness=0.6, rough=0.35, wear=0.3)
    copper = metal("copper", COPPER[0], COPPER[1], metalness=0.7, rough=0.35, wear=0.5)
    internal = plain("internal", INTERNAL, rough=0.45, metallic=0.6)
    rails = {64: 0.07, 32: 0.08, 16: 0.10, 8: 0.12}[size]
    bands = {64: (0.0,), 32: (0.0,), 16: (0.0,), 8: ()}[size]
    bev = {64: 0.012, 32: 0.016, 16: 0.022, 8: 0.03}[size]
    rot = math.radians(30)
    parts = []
    # the smoked sleeve, the liquid inside it, and the internals in the liquid
    parts.append(_part("sleeve", (smoked_glass(),), lambda bm: _hex(bm, R, -L, L, rot)))
    parts.append(_part("liquid", (liquid_mat(lit, size, L, R),),
                       lambda bm: _hex(bm, R * 0.86, -L + 0.01, L - 0.01, rot)))
    if size >= 16:
        rod_r = {64: 0.055, 32: 0.07, 16: 0.09}[size]
        baffles = {64: (-0.36, 0.0, 0.36), 32: (-0.3, 0.3), 16: (0.0,)}[size]

        def internals_bm(bm):
            res = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=rod_r, radius2=rod_r,
                                        depth=2 * L - 0.04)
            for z in baffles:
                res = bmesh.ops.create_cube(bm, size=1.0)
                vs = res["verts"]
                bmesh.ops.scale(bm, verts=vs, vec=(2 * R * 0.84, 0.05, 0.035 if size == 64 else 0.05))
                bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0),
                                 matrix=Matrix.Rotation(rot + math.radians(60) + z, 3, "Z"))
                bmesh.ops.translate(bm, verts=vs, vec=(0, 0, z))
        parts.append(_part("internals", (internal,), internals_bm))

    def rails_bm(bm):
        for i in range(6):
            a = rot + i * math.pi / 3
            c = Vector((math.cos(a), math.sin(a), 0)) * (R + rails * 0.15)
            res = bmesh.ops.create_cube(bm, size=1.0)
            vs = res["verts"]
            bmesh.ops.scale(bm, verts=vs, vec=(rails, rails, 2 * L))
            bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0), matrix=Matrix.Rotation(a, 3, "Z"))
            bmesh.ops.translate(bm, verts=vs, vec=c)
        for z in bands:
            _hex(bm, R + rails * 0.55, z - rails * 0.6, z + rails * 0.6, rot)
    parts.append(_part("rails", (cage,), rails_bm, bevel=bev))
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
    root = bpy.data.objects.new("cell", None)
    bpy.context.scene.collection.objects.link(root)
    for p in parts:
        p.parent = root
    m = Euler((0, 0, math.radians(38))).to_matrix().to_4x4() @ Euler((0, math.radians(90), 0)).to_matrix().to_4x4()
    root.matrix_world = m
    bpy.context.view_layer.update()
    zmin = min((p.matrix_world @ Vector(c)).z for p in parts for c in p.bound_box)
    root.location.z -= zmin
    return parts


def fuel(finish, size):
    return cell(finish, size, True)


def spent(finish, size):
    return cell(finish, size, False)


# ---------------------------------------------------------------- the solution

def drop_profile(n=48, p=1.15, aspect=0.66):
    pts = []
    for i in range(n + 1):
        t = math.pi * (1 - i / n)
        x = math.sin(t) * math.sin(t / 2) ** p
        z = math.cos(t)
        pts.append((max(0.0, x) * aspect / 0.77, z))
    pts[0] = (0.0, pts[0][1])
    pts[-1] = (0.0, pts[-1][1])
    return pts


def solution(finish, size):
    m = plain("solution", LIQUID, rough=0.5)
    g = _G(m)
    b = g.n["Principled BSDF"]
    face = g.node("ShaderNodeLayerWeight", Blend=0.5).outputs["Facing"]
    # the body: navy, deepening to near-black at the rim; no fresnel sheen at the edge
    g.l.new(g.mixc(g.remap(face, 0.1, 0.8), rig.srgb(LIQUID), rig.srgb("#02081A")), b.inputs["Base Color"])
    g.l.new(g.remap(face, 0.5, 0.85, 0.15, 0.0), b.inputs["Specular IOR Level"])
    # the light within: thick toward the eye and in the round belly, through darker swirls
    f2 = g.node("ShaderNodeLayerWeight", Blend=0.35).outputs["Facing"]
    z = g.node("ShaderNodeSeparateXYZ", Vector=obj_coords(g)).outputs["Z"]
    belly = g.remap(z, 0.7, -0.5, 0.45, 1.0)
    core = g.math("MULTIPLY", g.remap(f2, 0.42, 0.0), belly, clamp=True)
    swirl = g.remap(g.noise(obj_coords(g), {64: 2.6, 32: 2.2, 16: 1.6, 8: 1.2}[size], detail=3, distortion=0.6),
                    0.38, 0.62, {64: 0.78, 32: 0.82, 16: 0.9, 8: 0.95}[size], 1.0)
    fac = g.math("MULTIPLY", core, swirl, clamp=True)
    emit(m, fac, DROP_GLOW, DROP_GAIN)
    ob = lathe("radiant_solution", drop_profile(), (m,), segments=64, smooth=True)
    ob.rotation_euler = (math.radians(-45), 0, 0)
    return lift([ob])


ITEMS = {"radiant-chunk": chunk, "radiant-fuel": fuel, "sae-spent-cell": spent,
         "radiant-solution": solution}

# icon_post.py's rules: radiant_icons.py's, unchanged
_RULES = {
    64: {"alpha": [16, 245], "rim": [0.7, 36]},
    32: {"sharpen": [0.6, 50], "alpha": [20, 235], "rim": [0.7, 38]},
    16: {"contrast": 1.25, "sharpen": [0.5, 90], "alpha": [48, 208], "rim": [0.8, 40]},
    8: {"contrast": 1.35, "sharpen": [0.5, 80], "alpha": [72, 184], "rim": [0.9, 44]},
}
_RIM = {n: {64: [1.0, 50], 32: [1.0, 50], 16: [1.0, 50], 8: [1.0, 52]}
        for n in ("radiant-fuel", "sae-spent-cell")}
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
