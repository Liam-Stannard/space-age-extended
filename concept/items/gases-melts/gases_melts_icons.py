"""The Core's gases and melt: siderane, helium-3, molten kamacite.

Rendered by tools/blender/render-icons.sh (icon_rig.py: 45 deg camera, the
buildings' sun and fill, framed to 1 px clear of the canvas at every size):

    BLENDER=/usr/bin/blender tools/blender/render-icons.sh \
        concept/items/gases-melts/gases_melts_icons.py <out-dir>

Vanilla's and Space Age's fluid icons, measured (review_sheet's measures, every
fluid icon in base/ and space-age/graphics/icons/fluid/), use three forms:

  a drop      every liquid (crude oil, water, lubricant, fluoroketone, the
              solutions, the thruster fuels): 42x64, share 0.36, upright, glossy
  a molecule  the named gases (petroleum gas, ammonia, sulfuric acid): glossy
              space-filling atoms, white hydrogens round a coloured centre, wider
              than tall (62x49, 64x46)
  a cloud     the gases that are a vapour (steam, fluorine): a cauliflower puff,
              56x54, share 0.40, soft and light (p50 121-165)
  a pour      the melts (molten iron, molten copper): a tipped bucket pouring a
              glowing stream into a pool, 61x64, share 0.58; the bucket wears
              the metal's colour (iron's blue), the melt is orange

so, each in its in-game base colour (task rule):

  siderane          a molecule, as petroleum gas is: an "-ane", a fuel gas. A
                    chartreuse centre (#A8D82A, base_color 0.66 0.85 0.16) in four
                    white hydrogens, tetrahedral -- FeH4, after its name (sideros,
                    iron; -ane)
  helium-3          a cloud, as steam is: a noble gas has no molecule to draw. Pale
                    blue, base_color 0.55 0.78 0.90 (#8CC7E6)
  molten-kamacite   a pour, as molten iron is: the crucible in the kamacite family's
                    teal (concept/items/kamacite: base hsv(174, .30, .60)), the melt
                    base_color 0.85 0.42 0.16 (#D96B29) to its flow colour #FF9E52,
                    crusting dark in the pool

Size by size (FFF #348): fewer, larger lumps and crust patches, no trunnions,
a thicker stream as the size drops; POST declares icon_post.py's rules.
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
from icon_kit import add_glow, glossy, hsv, lathe, lift, link, obj_coords, place  # noqa: E402
from materials import layered  # noqa: E402

FINISHES = ("core",)

SIDERANE = "#A8D82A"
SIDERANE_PAINT = "#98C824"    # put in darker: lit by the sun and the coat it renders near #A8D82A
HYDROGEN = "#A4A4A0"          # vanilla's hydrogens are a lit grey, not white (petroleum gas p50 76)
HELIUM = "#8CC7E6"
HELIUM_PAINT = "#7498AE"   # put in at hue 210: the warm fill pulls a hue warm (round 6: 202 in, 194 out); a step darker than
                               # #8CC7E6 so its p50 sits in vanilla's fluids' range (round 8: 193, fluorine 165)
MELT = ("#B8501A", "#FF8A3A")          # emitted: base colour #D96B29 to flow #FF9E52, put in a step darker for the grade
CRUST = "#2A2420"
TEAL = dict(base=hsv(174, 0.30, 0.60), bare=hsv(174, 0.18, 0.85))


# ---------------------------------------------------------------- siderane

TETRA = [Vector(v).normalized() for v in ((1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1))]


def _sphere(name, r, mat, loc, subdiv=5):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=r)
    ob = link(bm, name, (mat,), smooth=True)
    ob.location = loc
    return ob


def siderane(finish, size):
    """A space-filling FeH4: the hydrogens overlap the centre, as petroleum gas's do."""
    centre = glossy("fe", SIDERANE_PAINT, rough=0.25, coat=1.0, coat_rough=0.08, rim=("#4C6A0A", 0.7))
    # the hydrogens shaded deeper toward their edges, so each reads as a ball at 8 px
    h = glossy("h", HYDROGEN, rough=0.3, coat=1.0, coat_rough=0.08, rim=("#3E3E3C", 0.95))
    # turned so all four hydrogens show: three round the rim, one toward the eye
    turn = Euler((math.radians(-60), math.radians(0), math.radians(40))).to_matrix()
    obs = [_sphere("fe", 0.47, centre, (0, 0, 0))]
    for i, d in enumerate(TETRA):
        obs.append(_sphere(f"h{i}", 0.27, h, tuple((turn @ d) * 0.56)))
    return lift(obs)


# ---------------------------------------------------------------- helium-3

def cloud_mesh(name, mat, size):
    """A cauliflower puff: metaballs on a low, wide cluster, made a mesh and
    billowed along its normals."""
    rng = random.Random(3)
    mb = bpy.data.metaballs.new(name)
    mb.resolution = 0.035
    mb.threshold = 0.6
    n = {64: 20, 32: 16, 16: 11, 8: 8}[size]
    # a heaped puff, as steam's is (56x54): a wide base, a crown, billows between
    balls = [(Vector((0, 0, 0.35)), 0.42), (Vector((0.05, 0.05, 0.8)), 0.38), (Vector((-0.12, 0.08, 1.0)), 0.3)]
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.3, 0.3)
        up = i % 2
        rr = rng.uniform(0.25, 0.42) if up else rng.uniform(0.38, 0.5)
        z = rng.uniform(0.55, 0.85) if up else rng.uniform(0.2, 0.4)
        balls.append((Vector((rr * math.cos(a), rr * math.sin(a) * 0.7, z)),
                      rng.uniform(0.2, 0.3)))
    for c, r in balls:
        el = mb.elements.new()
        el.co = c
        el.radius = r
    mob = bpy.data.objects.new(name + "_mb", mb)
    bpy.context.scene.collection.objects.link(mob)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(mob.evaluated_get(dg))
    bpy.data.objects.remove(mob)
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    amp, freq = {64: (0.08, 6.0), 32: (0.08, 5.0), 16: (0.06, 3.5), 8: (0.0, 3.0)}[size]
    for v in bm.verts:
        b = noise.turbulence(v.co * freq, 3, True, noise_basis="PERLIN_ORIGINAL", amplitude_scale=0.5,
                             frequency_scale=2.0)
        v.co += v.normal * amp * b
    ob = link(bm, name, (mat,), smooth=True)
    return ob


def helium(finish, size):
    m = bpy.data.materials.new("helium")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb(HELIUM_PAINT)
    b.inputs["Roughness"].default_value = 1.0
    b.inputs["Subsurface Weight"].default_value = 0.15
    b.inputs["Subsurface Radius"].default_value = (0.3, 0.4, 0.5)
    b.inputs["Subsurface Scale"].default_value = 0.1
    # a little of its own light, so the shadowed side stays a pale gas, not a grey rock
    add_glow(m, lambda g: g.remap(g.node("ShaderNodeLayerWeight", Blend=0.5).outputs["Facing"], 0.8, 0.0, 0.2, 0.35),
             ("#3C78A8", "#6FA8CC"), 0.35)
    ob = cloud_mesh("helium3", m, size)
    ob.rotation_euler = (math.radians(-35), 0, 0)    # its face turned to the eye
    return lift([ob])


# ---------------------------------------------------------------- molten kamacite

def crucible_profile():
    """Outer wall up, lip, inner wall down: a thick-walled cup, corners chamfered."""
    return [(0.0, 0.0), (0.26, 0.0), (0.30, 0.02), (0.32, 0.06), (0.37, 0.52), (0.40, 0.55),
            (0.42, 0.58), (0.42, 0.62), (0.40, 0.64), (0.36, 0.64), (0.33, 0.61), (0.29, 0.12),
            (0.26, 0.09), (0.0, 0.09)]


HEAT = ("#A0280A", "#FFA060")      # the melt's emission, coolest to hottest: about base colour #D96B29


def _heat(g, p, scale):
    """Hot streaks through the melt: the colour runs from dull red-orange to a
    yellow-white core, so a melt is never one flat orange (round 4)."""
    return g.remap(g.noise(p, scale, detail=4, distortion=0.6), 0.35, 0.68)


def melt_mat(size, molten_share, centre=None, radius=None):
    """Molten where noise sits below molten_share, crust rafts elsewhere; with a
    centre and radius (the pool) the crust also closes in toward the rim."""
    import bpy
    m = layered("melt_crust", CRUST, metal="#5A4A40", paint_metal=0.1, paint_rough=0.7, wear=0.1,
                rust=0.0, dust=0.0, grime=0.2, jitter=0.03)
    sc = {64: 3.0, 32: 2.6, 16: 2.0, 8: 1.6}[size]
    from materials import _G
    g = _G(m)
    bsdf = g.n["Principled BSDF"]
    p = obj_coords(g)
    n = g.noise(p, sc, detail=3)
    if centre is not None:
        d = g.node("ShaderNodeVectorMath")
        d.operation = "DISTANCE"
        g.l.new(p, d.inputs[0])
        d.inputs[1].default_value = tuple(centre)
        n = g.math("ADD", n, g.math("MULTIPLY", g.remap(d.outputs["Value"], radius * 0.55, radius), 0.35))
    mask = g.remap(n, molten_share + 0.05, molten_share - 0.05)
    heat = g.math("MULTIPLY", _heat(g, p, {64: 5.0, 32: 4.0, 16: 2.5, 8: 2.0}[size]), mask)
    g.l.new(g.mixc(heat, rig.srgb(HEAT[0]), rig.srgb(HEAT[1])), bsdf.inputs["Emission Color"])
    g.l.new(g.math("MULTIPLY", mask, 1.7), bsdf.inputs["Emission Strength"])
    return m


def stream_mat():
    m = glossy("stream", MELT[0], rough=0.3, coat=0.3)

    def mask(g):
        face = g.node("ShaderNodeLayerWeight", Blend=0.4).outputs["Facing"]
        # hottest down the stream's middle, cooler at its edges
        return g.remap(face, 0.75, 0.05, 0.15, 1.0)
    return add_glow(m, mask, HEAT, 1.8)


def molten(finish, size):
    teal = layered("crucible", TEAL["base"], metal=TEAL["bare"], paint_metal=0.45, paint_rough=0.4,
                   wear=0.45, rust=0.06, dust=0.0, grime=0.5, jitter=0.05)
    obs = []
    # tipped so its mouth faces down-left toward the eye, as molten iron's bucket is
    mouth = Vector((-0.85, -0.3, 0.42)).normalized()
    K = 1.5                         # the crucible large against its pool, as vanilla's bucket is
    tilt = (Matrix.Translation((0.3, 0.25, 0.8)) @ mouth.to_track_quat("Z", "Y").to_matrix().to_4x4()
            @ Matrix.Scale(K, 4))
    cru = lathe("crucible", crucible_profile(), (teal,), segments=56, smooth=True)
    cru.matrix_world = tilt
    obs.append(cru)
    # the melt brimming at the lip, inside the tipped cup
    inner = lathe("brim", [(0.0, 0.0), (0.34, 0.0), (0.345, 0.004)], (melt_mat(size, 0.6),), segments=40)
    inner.matrix_world = tilt @ Matrix.Translation((0, 0, 0.6))
    obs.append(inner)
    if size >= 32:
        # trunnions: the stubs it pivots on
        def stub(s):
            bm = bmesh.new()
            res = bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.07, radius2=0.07, depth=0.12)
            bmesh.ops.rotate(bm, verts=res["verts"], cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X"))
            ob = link(bm, f"stub{s}", (teal,), smooth=True)
            ob.matrix_world = tilt @ Matrix.Translation((0, s * 0.42, 0.38))
            return ob
        obs += [stub(-1), stub(1)]
    # the pour: from the lip's lowest point down into the pool
    down = Vector((0, 0, -1))
    u = (down - mouth * mouth.dot(down)).normalized()
    lip = tilt.to_translation() + (mouth * 0.62 + u * 0.42) * K
    pool_c = Vector((lip.x - 0.12, lip.y - 0.18, 0.0))   # under the lip: the stream falls
    cu = bpy.data.curves.new("stream", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = {64: 0.095, 32: 0.105, 16: 0.13, 8: 0.16}[size]
    cu.bevel_resolution = 6
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(2)
    pts = [lip + Vector((0, 0, -0.02)), Vector((lip.x - 0.07, lip.y - 0.07, lip.z * 0.5)), pool_c + Vector((0.0, 0.0, 0.04))]
    rad = [1.1, 0.8, 1.3]
    for bp, co, r in zip(sp.bezier_points, pts, rad):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = "AUTO"
        bp.radius = r
    st = bpy.data.objects.new("stream", cu)
    st.data.materials.append(stream_mat())
    bpy.context.scene.collection.objects.link(st)
    obs.append(st)
    # the pool: a low, lumpy puddle, crusting at its rim
    bm = bmesh.new()
    seg = 64
    rx, ry = 0.6, 0.42
    rng_off = Vector((2.3, 7.1, 0.4))
    top = []
    bot = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        k = 1 + 0.12 * noise.noise(Vector((math.cos(a), math.sin(a), 0)) * 1.8 + rng_off)
        x, y = pool_c.x + rx * k * math.cos(a), pool_c.y + ry * k * math.sin(a)
        bot.append(bm.verts.new((x, y, 0.0)))
        top.append(bm.verts.new((x, y, 0.035)))
    ctop = bm.verts.new((pool_c.x, pool_c.y, 0.07))
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
        bm.faces.new((top[i], top[j], ctop))
    bm.faces.new(list(reversed(bot)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if all(v.co.z > 0.01 for v in e.verts)],
                              cuts=3, use_grid_fill=True)
    for v in bm.verts:
        if v.co.z > 0.01:
            v.co.z += 0.03 * noise.noise(v.co * 6.0)
    pool = link(bm, "pool", (melt_mat(size, 0.6, pool_c, rx),), smooth=True)
    obs.append(pool)
    return lift(obs)


ITEMS = {"siderane": siderane, "helium-3": helium, "molten-kamacite": molten}

# icon_post.py's rules, per size: kamacite's (concept/items/kamacite/kamacite_icons.py)
_RULES = {
    64: {"alpha": [16, 245], "rim": [0.7, 36]},
    32: {"sharpen": [0.6, 50], "alpha": [20, 235], "rim": [0.7, 38]},
    16: {"contrast": 1.25, "sharpen": [0.5, 90], "alpha": [48, 208], "rim": [0.8, 40]},
    8: {"contrast": 1.35, "sharpen": [0.5, 80], "alpha": [72, 184], "rim": [0.9, 44]},
}
POST = {name: {s: dict(r) for s, r in _RULES.items()} for name in ITEMS}

icon_rig.main(ITEMS, FINISHES, POST)
