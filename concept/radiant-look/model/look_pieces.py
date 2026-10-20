"""Radiant look study: one way of seeing the radiant solution through glass, three candidates.

  blender -b --python look_pieces.py -- <out-dir> --look A|B|C [--frames 16] [--samples 40] [--no-bubbles]

Five test pieces in a row, each housed in the mod's layered finish (tools/blender/materials.py,
the Reaction Plant's palette), under the shared rig (tools/blender/rig.py):

  1 column   a vertical glass leg on a cast foot, flanged, strapped, capped (the RP legs)
  2 port     a round bolted bullseye port in a vessel's south face, the solution behind it
  3 slot     a long glazed slot in a lead roof (the generator's collector slot)
  4 tubes    a ring of six small glass emitter tubes on a plinth (the generator's tubes)
  5 well     an open well mouth, no glass, the solution's surface below the coping (the
             generator's well, the pool seen close)

Renders (4x, downsampled after by look_sheets.py):
  idle.png            the solution unlit: the plate as the stopped machine draws it
  work-NN.png         the machine working, frame NN: plate and window animation, no glow
  glow-NN.png         the glow layer the engine would draw additively (draw_as_glow): the
                      sun and sky off, only the solution's light and what it lights round it

The three looks (see LOOKS):
  A  "deep column"  plate-led: the light lives in the plate. A bright pale core falling off to
                    saturated blue and to deep navy at the glass's edges (facing ratio, or
                    distance from the window's centre), a caustic net drifting up through it;
                    a thin glow layer (the same light at 0.4) so it holds at night.
  B  "lamp behind smoked glass"  glow-led, as vanilla's fusion reactor and centrifuge: the
                    plate's window is dark smoked glass over a dim navy liquid with dark
                    internals (a heater rod, a grid, baffles); the light is in the glow layer, a
                    pale core falling off to blue, spilling onto the bezels. A slow breathing
                    pulse. Day and night read the same. Chosen (Liam, 2026-10-12), with C's
                    rising bubbles in the column: now drawn by the shared helper,
                    tools/blender/radiant.py, at its default tuning -- its glass, its liquid,
                    its pulse and flicker, its bubbles in the column (--no-bubbles leaves them
                    out) and its glow pass. Its bloom is per shape (radiant.BLOOM), added
                    by pack.py from a model's declaration: TIGHT (3 px x 0.9 + 16 px x 0.6)
                    for the tubes, the port (disc) and the slot, WIDE (3 px x 0.9 + 24 px
                    x 1.0) for the column and the well (surface). This script renders every
                    piece in one glow pass and adds no bloom; look_sheets.py still adds the
                    study's B bloom (3 px at 0.9) to the whole row, so its candidate sheets
                    are not the tuned look -- bloom each piece with its own shape's stages
                    to see that.
  C  "rising stream" lit from below: the solution brightest at the bottom and darkening up,
                    a bright meniscus, streams of pale bubbles rising and dark flecks sinking
                    (the internal silhouettes); the well boils in convection cells. The glow
                    carries the bubbles and the lit bottom.
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
# tools/blender from this worktree (concept/radiant-look/model -> repo root)
TOOLS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "tools", "blender"))
sys.path.insert(0, TOOLS)
import rig  # noqa: E402
import radiant  # noqa: E402
from materials import layered  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0]
LOOK = argv[argv.index("--look") + 1] if "--look" in argv else "A"
NF = int(argv[argv.index("--frames") + 1]) if "--frames" in argv else 16
SAMPLES = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 40
ONLY = argv[argv.index("--only") + 1] if "--only" in argv else None
ONE = ONLY == "one"            # every pass, frame 0 only: the quick look while tuning
BUBBLES = "--no-bubbles" not in argv      # B: the chosen look's rising bubbles in the column
if ONE:
    ONLY = None
os.makedirs(OUT, exist_ok=True)

CANVAS = (544, 192)
CENTRE = (272, 140)
PI = math.pi
XS = (-3.4, -1.7, 0.0, 1.7, 3.4)         # the five pieces' centres, tiles east

sc = rig.reset()
sc.cycles.samples = SAMPLES
ROOT = rig.turntable(rig.stretch_root())

# ---------------------------------------------------------------- the housings' finish
M = {
    "lead": layered("lead", "#6A6258", metal="#BCB4A2", paint_metal=0.3, paint_rough=0.55, wear=0.3,
                    rust=0.06, dust=0.5, grime=0.8, jitter=0.08, ground=0.75),
    "grey": layered("grey", "#6E6A62", metal="#9A9488", paint_metal=0.15, paint_rough=0.55, wear=0.3,
                    rust=0.2, dust=0.35, grime=0.7, jitter=0.06, ground=0.8),
    "dark_steel": layered("dark_steel", "#3E3934", metal="#8C8272", paint_metal=0.35, paint_rough=0.55,
                          wear=0.4, rust=0.35, dust=0.35, grime=0.7, ground=0.8),
    "bare": layered("bare", "#A8A090", metal="#D8D0BE", paint_metal=0.85, paint_rough=0.3, wear=0.5,
                    rust=0.16, dust=0.12, grime=0.5, ground=0.6),
    "bolt": layered("bolt", "#5A4A3A", metal="#A89880", paint_metal=0.5, paint_rough=0.5, wear=0.5,
                    rust=0.75, dust=0.2, grime=0.6),
    "copper": layered("copper", "#94592C", metal="#D09060", paint_metal=0.9, paint_rough=0.32, wear=0.45,
                      rust=0.04, dust=0.2, grime=0.5, patina=0.9),
    # the inside of a well or a slot: soot-dark, wet
    "well": layered("well", "#24201C", metal="#4A4440", paint_metal=0.3, paint_rough=0.35, wear=0.1,
                    rust=0.3, dust=0.0, grime=0.9),
}


def glass_mat(name):
    """A and C's clear glass; B's smoked glass is the helper's (radiant.Radiant.glass)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#C8D8E0")
    b.inputs["Roughness"].default_value = 0.06
    b.inputs["IOR"].default_value = 1.47
    b.inputs["Transmission Weight"].default_value = 0.92
    b.inputs["Coat Weight"].default_value = 0.5
    return m


def pane_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#D8E4EA")
    b.inputs["Roughness"].default_value = 0.04
    b.inputs["IOR"].default_value = 1.08
    b.inputs["Transmission Weight"].default_value = 1.0
    b.inputs["Specular IOR Level"].default_value = 0.35
    return m


SMOKY = LOOK == "B"
R = radiant.Radiant() if SMOKY else None         # B: the shared helper, at its default tuning
M["glass"] = R.glass("glass") if SMOKY else glass_mat("glass")
M["pane"] = R.glass("pane", pane=True) if SMOKY else pane_mat("pane")

# ---------------------------------------------------------------- the solution
PHASES = []      # value nodes set to t (0..1) per frame
STRENGTHS = []   # (strength socket, {"work": v, "glow": v, "idle": v}, fn(t) -> multiplier)
RAMPS = {
    # position -> sRGB hex; every ramp runs inside #1F63FF -> #73ADFF, with a navy foot and,
    # where the look has a hot core, a pale top (B's ramps are the helper's: radiant.PLATE_RAMP
    # and radiant.GLOW_RAMP)
    "A": [(0.0, "#040C24"), (0.30, "#0B2A8C"), (0.55, "#1F63FF"), (0.80, "#73ADFF"), (1.0, "#D2E6FF")],
    "C": [(0.0, "#061436"), (0.35, "#0B2A8C"), (0.62, "#1F63FF"), (0.88, "#73ADFF"), (1.0, "#B8D6FF")],
}


class N:
    """A small node-graph helper."""

    def __init__(self, m):
        self.m = m
        self.n = m.node_tree.nodes
        self.l = m.node_tree.links

    def new(self, kind, **ins):
        nd = self.n.new(kind)
        for k, v in ins.items():
            if isinstance(v, bpy.types.NodeSocket):
                self.l.new(v, nd.inputs[k])
            else:
                nd.inputs[k].default_value = v
        return nd

    def op(self, operation, a, b=None, clamp=False):
        nd = self.n.new("ShaderNodeMath")
        nd.operation = operation
        nd.use_clamp = clamp
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, bpy.types.NodeSocket):
                self.l.new(v, nd.inputs[i])
            else:
                nd.inputs[i].default_value = v
        return nd.outputs[0]

    def remap(self, v, lo, hi, a=0.0, b=1.0):
        nd = self.new("ShaderNodeMapRange", Value=v)
        nd.inputs["From Min"].default_value = lo
        nd.inputs["From Max"].default_value = hi
        nd.inputs["To Min"].default_value = a
        nd.inputs["To Max"].default_value = b
        return nd.outputs[0]

    def xyz(self, vec):
        return self.new("ShaderNodeSeparateXYZ", Vector=vec).outputs

    def vec(self, x, y, z):
        nd = self.n.new("ShaderNodeCombineXYZ")
        for i, v in enumerate((x, y, z)):
            if isinstance(v, bpy.types.NodeSocket):
                self.l.new(v, nd.inputs[i])
            else:
                nd.inputs[i].default_value = v
        return nd.outputs[0]

    def vadd(self, a, b):
        nd = self.n.new("ShaderNodeVectorMath")
        nd.operation = "ADD"
        self.l.new(a, nd.inputs[0])
        self.l.new(b, nd.inputs[1])
        return nd.outputs[0]

    def ramp(self, fac, stops):
        nd = self.new("ShaderNodeValToRGB", Fac=fac)
        cr = nd.color_ramp
        cr.elements[0].position, cr.elements[0].color = stops[0][0], rig.srgb(stops[0][1])
        cr.elements[1].position, cr.elements[1].color = stops[-1][0], rig.srgb(stops[-1][1])
        for p, h in stops[1:-1]:
            e = cr.elements.new(p)
            e.color = rig.srgb(h)
        return nd.outputs["Color"]


def looped(g, tex, p, drift, phase):
    """A texture moving by `drift` a loop and closing the loop exactly: two copies, one a
    loop behind the other, crossfaded -- tex(p + d t)(1 - t) + tex(p + d (t - 1)) t."""
    d = Vector(drift)
    sh1 = g.vec(g.op("MULTIPLY", phase, d.x), g.op("MULTIPLY", phase, d.y), g.op("MULTIPLY", phase, d.z))
    tm1 = g.op("SUBTRACT", phase, 1.0)
    sh2 = g.vec(g.op("MULTIPLY", tm1, d.x), g.op("MULTIPLY", tm1, d.y), g.op("MULTIPLY", tm1, d.z))
    a = tex(g.vadd(p, sh1))
    b = tex(g.vadd(p, sh2))
    mix = g.new("ShaderNodeMix", Factor=phase)
    mix.data_type = "FLOAT"
    g.l.new(a, mix.inputs["A"])
    g.l.new(b, mix.inputs["B"])
    # the crossfade flattens the middle of the loop: give the contrast back
    dev = g.op("SUBTRACT", mix.outputs["Result"], 0.5)
    w = g.op("ADD", 1.0, g.op("MULTIPLY", g.op("MULTIPLY", phase, g.op("SUBTRACT", 1.0, phase)), 1.6))
    return g.op("ADD", 0.5, g.op("MULTIPLY", dev, w))


def core_of(g, kind, size):
    """0 at the window's edge, 1 at its middle: where a thick body of light reads brightest."""
    p = g.new("ShaderNodeTexCoord").outputs["Object"]
    s = g.xyz(p)
    if kind in ("column", "tube"):
        face = g.new("ShaderNodeLayerWeight", Blend=0.5).outputs["Facing"]
        return g.op("POWER", g.op("SUBTRACT", 1.0, face, clamp=True), 1.6)
    if kind in ("disc", "surface"):
        r = g.op("DIVIDE", g.op("SQRT", g.op("ADD", g.op("MULTIPLY", s["X"], s["X"]),
                                             g.op("MULTIPLY", s["Y"], s["Y"]))), size[0])
        return g.op("SUBTRACT", 1.0, g.op("POWER", g.op("MINIMUM", r, 1.0), 1.5), clamp=True)
    # slot: across its width, and fading at its two ends
    across = g.op("SUBTRACT", 1.0, g.op("ABSOLUTE", g.op("DIVIDE", s["Y"], size[1])), clamp=True)
    ends = g.op("SUBTRACT", 1.0, g.op("POWER", g.op("ABSOLUTE", g.op("DIVIDE", s["X"], size[0])), 4.0),
                clamp=True)
    return g.op("MULTIPLY", g.op("POWER", across, 0.7), ends)


def solution(name, kind, size, seed=0):
    """The radiant solution for one window, in the look being rendered.

    kind: column | tube (a cylinder, local Z up), disc (a port, local Z its normal),
    slot (a box, local X along it), surface (an open well's face, local Z up).
    size: the window's half-extents in its local units (radius, or half-length/half-width).
    """
    if LOOK == "B":
        # the chosen look: the shared helper's liquid (its pulse, flicker and glow ramp)
        M[name] = R.liquid(name, kind, size)
        return name
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    g = N(m)
    b = g.n["Principled BSDF"]
    phase = g.new("ShaderNodeValue").outputs[0]
    PHASES.append(phase.node)
    p = g.new("ShaderNodeTexCoord").outputs["Object"]
    s = g.xyz(p)
    core = core_of(g, kind, size)
    scale = 1.0 / max(0.06, min(size[0], size[1] if len(size) > 1 else size[0]))

    if LOOK == "A":
        # caustic net: thin bright cell edges drifting up through a thick body of light
        def vor(v):
            nd = g.new("ShaderNodeTexVoronoi", Vector=v, Scale=scale * (1.3 if kind in ("column", "tube") else 3.2),
                       Randomness=0.9)
            nd.feature = "DISTANCE_TO_EDGE"
            return g.remap(nd.outputs["Distance"], 0.0, 0.09, 1.0, 0.0)
        up = (0, 0, 0.9 / scale * 2.0) if kind in ("column", "tube") else (0.9 / scale * 1.6, 0.4 / scale, 0)
        caus = looped(g, vor, p, up, phase)
        fac = g.op("ADD", g.op("MULTIPLY", core, 0.74), g.op("MULTIPLY", caus, 0.13))
        col = g.ramp(g.op("MINIMUM", fac, 1.0), RAMPS["A"])
        g.l.new(col, b.inputs["Emission Color"])
        b.inputs["Base Color"].default_value = rig.srgb("#0A1430")
        b.inputs["Roughness"].default_value = 0.2
        STRENGTHS.append((b.inputs["Emission Strength"], {"idle": 0.0, "work": 2.1, "glow": 0.9}, None))
    else:
        # lit from below: bright at the foot, darker up the column; a bright meniscus line;
        # the open surface boils in convection cells
        if kind in ("column", "tube"):
            h = g.remap(s["Z"], -size[1], size[1], 0.0, 1.0)       # 0 foot .. 1 top
            body = g.op("SUBTRACT", 1.0, g.op("POWER", h, 0.55))
            men = g.remap(s["Z"], size[1] * 0.86, size[1] * 0.97, 0.0, 1.0)
            men = g.op("MULTIPLY", men, g.remap(s["Z"], size[1] * 0.99, size[1] * 0.97, 0.0, 1.0))
            fac = g.op("ADD", g.op("ADD", g.op("MULTIPLY", body, 0.72), g.op("MULTIPLY", core, 0.2)),
                       g.op("MULTIPLY", men, 0.75))
        else:
            def cells(v):
                nd = g.new("ShaderNodeTexVoronoi", Vector=v, Scale=scale * 3.0, Randomness=1.0)
                nd.feature = "DISTANCE_TO_EDGE"
                return g.remap(nd.outputs["Distance"], 0.0, 0.12, 1.0, 0.0)
            # the cells drift slowly across the surface, closing the loop
            drift = (0.7 / scale, 0.25 / scale, 0.0)
            cel = looped(g, cells, p, drift, phase)
            fac = g.op("ADD", g.op("MULTIPLY", core, 0.55), g.op("MULTIPLY", cel, 0.42))
        col = g.ramp(g.op("MINIMUM", fac, 1.0), RAMPS["C"])
        g.l.new(col, b.inputs["Emission Color"])
        b.inputs["Base Color"].default_value = rig.srgb("#0A1838")
        b.inputs["Roughness"].default_value = 0.15
        STRENGTHS.append((b.inputs["Emission Strength"], {"idle": 0.0, "work": 2.0, "glow": 1.1}, None))
    M[name] = m
    return name


def bubble_mat():
    m = bpy.data.materials.new("bubble")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#1A2440")
    b.inputs["Emission Color"].default_value = rig.srgb("#C6DEFF")
    STRENGTHS.append((b.inputs["Emission Strength"], {"idle": 0.0, "work": 1.5, "glow": 1.2}, None))
    M["bubble"] = m


bubble_mat()
M["fleck"] = layered("fleck", "#141820", paint_metal=0.2, paint_rough=0.5, wear=0, rust=0, dust=0, grime=0)
M["internal"] = layered("internal", "#1A1C22", metal="#3A3C44", paint_metal=0.6, paint_rough=0.45, wear=0.2,
                        rust=0.1, dust=0, grime=0.6)

# ---------------------------------------------------------------- geometry
OBJS = []
LIGHTS = []      # the solution's objects
POSES = []       # callables(t)


def _finish(o, mat, bevel=0.01, smooth=False):
    o.data.materials.append(M[mat])
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments, mod.limit_method = bevel, 2, "ANGLE"
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    o.parent = ROOT
    OBJS.append(o)
    return o


def box(loc, size, mat, rz=0.0, rot=None, bevel=0.012):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot or (0, 0, rz))
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, bevel)


def cyl(loc, r, h, mat, rot=(0, 0, 0), verts=48, bevel=0.01):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    return _finish(bpy.context.active_object, mat, bevel, smooth=True)


def sphere(loc, r, mat, scale=(1, 1, 1), seg=12):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2)
    o = bpy.context.active_object
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, 0, smooth=True)


def annulus(loc, r_in, r_out, h, mat, rot=(0, 0, 0), seg=64):
    import bmesh
    me = bpy.data.meshes.new("annulus")
    bm = bmesh.new()
    rows = []
    for r, z in ((r_out, -h / 2), (r_out, h / 2), (r_in, h / 2), (r_in, -h / 2)):
        rows.append([bm.verts.new((r * math.cos(2 * PI * k / seg), r * math.sin(2 * PI * k / seg), z))
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
    return _finish(o, mat, 0.006, smooth=True)


def head(x, y, z, r, h, mat):
    import bmesh
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0), segments=48, ring_count=24)
    o = bpy.context.active_object
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.01], context="VERTS")
    bm.to_mesh(o.data)
    bm.free()
    o.scale = (r, r, h)
    o.location = (x, y, z)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _finish(o, mat, 0, smooth=True)


def bolts(cx, cy, z, R, n, r=0.018):
    for i in range(n):
        a = 2 * PI * i / n
        cyl((cx + R * math.cos(a), cy + R * math.sin(a), z), r, 0.025, "bolt", verts=6, bevel=0)


def flange(x, y, z, r, h=0.06, nb=12):
    cyl((x, y, z), r + 0.045, h, "bare", verts=64)
    bolts(x, y, z + h / 2 + 0.008, r + 0.03, nb, r=0.016)


def cut(o, shape, loc, size, rot=(0, 0, 0)):
    """Cut a hole in o: shape "box" (size = dimensions) or "cyl" (size = (r, depth))."""
    if shape == "box":
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
        c = bpy.context.active_object
        c.scale = size
    else:
        bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=size[0], depth=size[1], location=loc, rotation=rot)
        c = bpy.context.active_object
    c.hide_render = True
    c.hide_viewport = True
    mod = o.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = c
    mod.solver = "EXACT"
    # the cut first, the bevel after it
    o.modifiers.move(len(o.modifiers) - 1, 0)
    return o


def along(t):
    return Vector(t).normalized().to_track_quat("Z", "Y").to_euler()


def lit(o):
    LIGHTS.append(o)
    if R:
        R.lit(o)            # B: the helper's rim spill
    return o


def rising(path, n, seed, mat="bubble", size=(0.012, 0.022), down=False, scale=(1, 1, 1)):
    """n particles each covering path(u, a) once a loop, so it wraps seamlessly."""
    rnd = random.Random(seed)
    objs = []
    for _ in range(n):
        o = sphere((0, 0, 0), rnd.uniform(*size), mat, scale=scale, seg=8)
        objs.append((o, rnd.random(), rnd.uniform(-1, 1)))

    def pose(t):
        for o, ph, a in objs:
            u = (ph + (-t if down else t)) % 1.0
            o.location = path(u, a)
    POSES.append(pose)
    return [o for o, _, _ in objs]


# 1 -------------------------------------------------------------- the column (RP leg)
def column(x):
    Z0, Z1, LR = 0.40, 2.30, 0.25
    cyl((x, 0, 0.19), LR + 0.11, 0.38, "dark_steel", verts=40)
    bolts(x, 0, 0.39, LR + 0.07, 8)
    flange(x, 0, Z0 - 0.03, LR)
    flange(x, 0, Z1 + 0.01, LR)
    cyl((x, 0, (Z0 + Z1) / 2), LR, Z1 - Z0, "glass", verts=48, bevel=0)
    h = Z1 - Z0 - 0.04
    lit(cyl((x, 0, (Z0 + Z1) / 2), LR - 0.045, h, solution("sol_col", "column", (LR - 0.045, h / 2)),
            verts=48, bevel=0))
    if LOOK == "B":
        # internals: a heater rod and a spiral baffle, silhouetted against the light
        cyl((x, 0, (Z0 + Z1) / 2), 0.055, h, "internal", verts=16, bevel=0)
        for k in range(6):
            z = Z0 + 0.15 + k * (h - 0.3) / 5
            box((x, 0, z), (2 * (LR - 0.05), 0.04, 0.04), "internal", rz=k * 0.7, bevel=0)
        if BUBBLES:
            # the chosen look's one borrowing from C: bubbles rising in the column's front
            R.column_bubbles((x, 0), LR - 0.045, (Z0 + 0.05, Z0 + 0.05 + (h - 0.1)), parent=ROOT)
    if LOOK == "C":
        # pale bubbles rising in the front of the column, dark flecks sinking
        rising(lambda u, a: (x + (LR - 0.06) * math.cos(-PI / 2 + a * 0.9),
                             (LR - 0.06) * math.sin(-PI / 2 + a * 0.9), Z0 + 0.05 + (h - 0.1) * u), 30, 11, size=(0.016, 0.028))
        rising(lambda u, a: (x + (LR - 0.07) * math.cos(-PI / 2 + a), (LR - 0.07) * math.sin(-PI / 2 + a),
                             Z0 + 0.05 + (h - 0.1) * u), 12, 12, mat="fleck", size=(0.014, 0.022), down=True,
               scale=(1.5, 1, 0.6))
    cyl((x, 0, (Z0 + Z1) / 2), LR + 0.025, 0.07, "bare", verts=64)          # middle band
    for j in range(4):
        a = 2 * PI * (j + 0.5) / 4 + 0.3
        box((x + (LR + 0.01) * math.cos(a), (LR + 0.01) * math.sin(a), (Z0 + Z1) / 2),
            (0.045, 0.045, Z1 - Z0), "bare", rz=a, bevel=0.006)
    cyl((x, 0, Z1 + 0.15), LR * 0.8, 0.22, "dark_steel", verts=32)
    head(x, 0, Z1 + 0.26, LR * 0.8, 0.1, "lead")


# 2 -------------------------------------------------------------- the bullseye port
def port(x):
    r = 0.26
    body = box((x, 0.05, 0.42), (1.05, 0.8, 0.84), "grey", bevel=0.03)
    cut(body, "cyl", (x, -0.35, 0.44), (r + 0.004, 0.4), rot=(PI / 2, 0, 0))
    box((x, 0.05, 0.86), (1.1, 0.85, 0.06), "dark_steel", bevel=0.01)
    t = Vector((0, -1, 0))
    c = Vector((x, -0.35, 0.44))
    rot = along(t)
    annulus(tuple(c + t * 0.02), r, r + 0.11, 0.08, "dark_steel", rot=rot)       # frame
    annulus(tuple(c + t * 0.065), r - 0.01, r + 0.09, 0.03, "bare", rot=rot)     # clamp ring
    for i in range(12):
        a = 2 * PI * i / 12
        u = Vector((math.cos(a), 0, math.sin(a)))
        cyl(tuple(c + t * 0.085 + (r + 0.05) * u), 0.017, 0.025, "bolt", rot=rot, verts=6, bevel=0)
    # the recess: a short dark barrel, the solution at its back, the glass at its front
    annulus(tuple(c - t * 0.01), r - 0.005, r + 0.005, 0.1, "well", rot=rot)
    cyl(tuple(c + t * 0.045), r, 0.015, "pane", rot=rot, verts=48, bevel=0)
    lit(cyl(tuple(c - t * 0.035), r, 0.02, solution("sol_port", "disc", (r, r)), rot=rot, verts=48, bevel=0))
    if LOOK == "B":
        box(tuple(c - t * 0.02), (0.035, 0.03, 2 * r), "internal", bevel=0)          # a grid
        box(tuple(c - t * 0.02), (2 * r, 0.03, 0.035), "internal", bevel=0)
        cyl(tuple(c - t * 0.03), r * 0.45, 0.02, "internal", rot=rot, verts=32, bevel=0)
        cyl(tuple(c - t * 0.025), r * 0.35, 0.03, "pane", rot=rot, verts=32, bevel=0)
    if LOOK == "C":
        rising(lambda u, a: (x + a * r * 0.8, -0.35 + 0.0,
                             0.44 - r * 0.9 + 2 * r * 0.9 * u), 10, 21, size=(0.01, 0.018))
    box((x, c.y + t.y * 0.1, 0.44), (0.04, 0.04, 2 * r + 0.06), "bare", bevel=0.004)     # the bar


# 3 -------------------------------------------------------------- the glazed slot
def slot(x):
    L, Wd, H = 1.3, 0.95, 0.5
    hl, hw = 0.5, 0.11
    zt = H + 0.005
    body = box((x, 0.0, H / 2), (L, Wd, H), "lead", bevel=0.03)
    cut(body, "box", (x, 0, H), (2 * hl, 2 * hw, 0.2))
    # the coping: dark steel bars round the slot
    for dy in (-1, 1):
        box((x, dy * (hw + 0.05), zt + 0.03), (2 * hl + 0.2, 0.1, 0.06), "dark_steel", bevel=0.01)
    for dx in (-1, 1):
        box((x + dx * (hl + 0.05), 0, zt + 0.03), (0.1, 2 * hw + 0.2, 0.06), "dark_steel", bevel=0.01)
    box((x, 0, zt - 0.08), (2 * hl, 2 * hw, 0.01), "well", bevel=0)                  # (under)
    lit(box((x, 0, zt - 0.07), (2 * hl, 2 * hw, 0.02), solution("sol_slot", "slot", (hl, hw)), bevel=0))
    if LOOK == "B":
        for k in range(7):
            box((x - hl + 0.07 + k * (2 * hl - 0.14) / 6, 0, zt - 0.03), (0.025, 2 * hw, 0.06), "internal",
                bevel=0)
    if LOOK == "C":
        rising(lambda u, a: (x - hl + 0.04 + (2 * hl - 0.08) * ((u + a) % 1.0), (a * 0.8) * hw,
                             zt - 0.055), 14, 31, size=(0.010, 0.016))
    box((x, 0, zt + 0.045), (2 * hl, 2 * hw, 0.012), "pane", bevel=0)                  # the glazing
    for k in range(3):                                                                # glazing bars
        box((x - hl + (k + 1) * 2 * hl / 4, 0, zt + 0.07), (0.035, 2 * hw + 0.12, 0.03), "bare", bevel=0.004)
    for dx in (-1, 1):
        for dy in (-1, 1):
            cyl((x + dx * (hl + 0.05), dy * (hw + 0.05), zt + 0.07), 0.018, 0.025, "bolt", verts=6, bevel=0)


# 4 -------------------------------------------------------------- the tube ring
def tubes(x):
    cyl((x, 0, 0.12), 0.55, 0.24, "dark_steel", verts=64)
    cyl((x, 0, 0.27), 0.45, 0.08, "grey", verts=64)
    cyl((x, 0, 0.45), 0.13, 0.36, "copper", verts=24)                               # the bus post
    sol = solution("sol_tube", "tube", (0.04, 0.15))
    for i in range(6):
        a = 2 * PI * i / 6 + PI / 6
        tx, ty = x + 0.33 * math.cos(a), 0.33 * math.sin(a)
        cyl((tx, ty, 0.35), 0.075, 0.09, "dark_steel", verts=20)
        cyl((tx, ty, 0.57), 0.065, 0.36, "glass", verts=24, bevel=0)
        lit(cyl((tx, ty, 0.57), 0.04, 0.30, sol, verts=20, bevel=0))
        if LOOK == "B":
            cyl((tx, ty, 0.57), 0.012, 0.30, "internal", verts=8, bevel=0)
        if LOOK == "C":
            rising(lambda u, a2, tx=tx, ty=ty: (tx + 0.03 * a2, ty - 0.035, 0.43 + 0.28 * u), 3, 40 + i,
                   size=(0.008, 0.012))
        cyl((tx, ty, 0.78), 0.06, 0.07, "copper", verts=20)
        head(tx, ty, 0.815, 0.06, 0.03, "copper")


# 5 -------------------------------------------------------------- the open well
def well(x):
    r = 0.36
    body = box((x, 0, 0.2), (1.15, 1.15, 0.4), "grey", bevel=0.03)
    cut(body, "cyl", (x, 0, 0.4), (r + 0.004, 0.3))
    annulus((x, 0, 0.43), r, r + 0.12, 0.08, "dark_steel")                           # coping
    bolts(x, 0, 0.475, r + 0.07, 12)
    annulus((x, 0, 0.30), r - 0.005, r + 0.005, 0.24, "well")                       # the shaft
    lit(cyl((x, 0, 0.30), r, 0.01, solution("sol_well", "surface", (r, r)), verts=64, bevel=0))
    if LOOK == "B":
        for k in (-1, 0, 1):                                                         # a grate
            box((x + k * r * 0.5, 0, 0.37), (0.03, 2 * r, 0.03), "internal", bevel=0)
        box((x, 0, 0.385), (2 * r, 0.03, 0.03), "internal", bevel=0)


for fn, x in zip((column, port, slot, tubes, well), XS):
    fn(x)

# ---------------------------------------------------------------- the passes
rig.camera(*CANVAS, centre_px=CENTRE)
SUN = rig.sun()
ground = rig.ground_catcher(size=16)
ground.parent = ROOT
bounce = rig.bounce_ground(size=16)
BG = sc.world.node_tree.nodes["Background"].inputs["Strength"]
BG0 = BG.default_value


def pose(t, mode):
    for ph in PHASES:
        ph.outputs[0].default_value = t
    for sock, vals, fn in STRENGTHS:
        sock.default_value = vals[mode] * (fn(t) if fn else 1.0)
    for p in POSES:
        p(t)
    if R:
        R.pose(t, {"idle": "idle", "work": "plate", "glow": "glow"}[mode])
        for o in R.bubbles:
            o.hide_render = mode == "idle"          # working-only


def glow_scene(on):
    SUN.hide_render = on
    ground.hide_render = on
    bounce.hide_render = on
    BG.default_value = 0.0 if on else BG0


if ONLY in (None, "idle"):
    pose(0.0, "idle")
    rig.render(os.path.join(OUT, "idle.png"))
for f in range(NF):
    t = f / NF
    if ONLY in (None, "work"):
        pose(t, "work")
        rig.render(os.path.join(OUT, f"work-{f:02d}.png"))
    if ONLY in (None, "glow"):
        pose(t, "glow")
        if R:
            with R.glow_pass(hide=(ground, bounce)):
                rig.render(os.path.join(OUT, f"glow-{f:02d}.png"))
        else:
            glow_scene(True)
            rig.render(os.path.join(OUT, f"glow-{f:02d}.png"))
            glow_scene(False)
    if ONE:
        break
print("done", LOOK)
