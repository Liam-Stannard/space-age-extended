"""Reaction Plant redesign, round 3: F, the Circulator, textured, at 5x5.

  $BLENDER -b --python r3_circulator.py -- <out-dir> [--frames N] [--quick] [--only working|idle]
           [--ss K]

Liam picked round 2's F ("the circulator is good but the textures need work"). This is
F again, still a concept before the spec is rewritten and the model is built, with:

  - the finish pushed to the signed-off models' level (tools/blender/materials.py's
    layers set as the Vacuum Furnace, Drop Crusher and Ballast Drill set them: ground
    dirt, rust runs from the bands, grime in the contact lines, patina, worn edges),
    no swatches (round 2's swatch grain read as camouflage), plus the proposed
    signature finish: weathered LEAD cladding on the vessels, its seams and runs
    bloomed with white lead salts (lead_finish below);
  - pipe-picture space clear at tiles -1, 0, +1 on every edge: nothing runs along an
    edge there, nothing crosses it, a wall meets it, and on the north edge nothing
    rises into the screen band the north pictures draw in (they are drawn behind the
    building), so the tall parts stand in the corners and the reactor moved forward;
  - the front third broken into separate units of different heights, ground between.

Writes into <out-dir>, at K x sprite size (default rig.SS = 4) on a 512 x 448 sprite
canvas with the entity origin at (208, 272):

  working-NN.png   running, frame NN of the 24-frame loop, on the shadow catcher
  idle.png         stopped and unlit, frame 0, on the shadow catcher
  plate.png        idle without the ground: the plate alone, as finish.py and tonal.py
                   measure one, and the mask for cover
  plate-working.png  frame 0 running, without the ground

No port stubs are rendered: the sheets draw vanilla's pictures over the plate as
stand-ins, as the engine would. Units are tiles; north is +Y; a point (x, y, z)
lands about (x, y + z/2) tiles up the screen. Nothing is adopted.
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
from materials import TEX, layered, hazard_pattern  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0]
QUICK = "--quick" in argv
NF = int(argv[argv.index("--frames") + 1]) if "--frames" in argv else 24
ONLY = argv[argv.index("--only") + 1] if "--only" in argv else None
os.makedirs(OUT, exist_ok=True)

CANVAS = (512, 448)
CENTRE = (208, 272)
SSK = int(argv[argv.index("--ss") + 1]) if "--ss" in argv else rig.SS

sc = rig.reset()
sc.cycles.samples = 16 if QUICK else 96
ROOT = rig.turntable(rig.stretch_root())
PI = math.pi

# ---------------------------------------------------------------- the signature finish
# Heights (z_top, run length) the bloom hangs from: the reactor's bands and its head
# flange, the scrubber's bands. World z, so one material serves every vessel.
BLOOM_TOPS = ((0.47, 0.32), (1.17, 0.42), (1.87, 0.42), (2.52, 0.5), (2.95, 0.4), (0.9, 0.3), (1.6, 0.4))


def lead_finish(tops=BLOOM_TOPS, bloom=1.0, gain=1.0):
    """Weathered lead sheet: a cool, dull grey in sheets of slightly different age,
    and white lead bloom -- the salts lead grows where the solution weeps -- hanging
    in runs below every band and flange, crusted in the seams and splashed round the
    foot. Pale and dry, never orange: it can't be read as rust, and it is the one
    bright, cool-white material on the plate."""
    def pat(g):
        geo = g.node("ShaderNodeNewGeometry")
        pos, nrm = geo.outputs["Position"], geo.outputs["Normal"]
        z = g.node("ShaderNodeSeparateXYZ", Vector=pos).outputs["Z"]
        nz = g.node("ShaderNodeSeparateXYZ", Vector=nrm).outputs["Z"]
        tone = g.remap(g.noise(pos, 1.8, detail=2), 0.42, 0.58)
        base = g.mixc(tone, rig.srgb("#5E6064"), rig.srgb("#7C7E81"))
        if gain != 1.0:
            base = g.mulc(base, (gain, gain, gain * 1.02, 1.0))
        if not bloom:
            return base
        vertical = g.remap(nz, 0.5, 0.1)
        st = g.node("ShaderNodeMapping", Vector=pos)
        st.inputs["Scale"].default_value = (1.0, 1.0, 0.3)
        runs = g.image(f"{TEX}/maps/rust_streak.png", st.outputs[0], 0.8).outputs["Color"]
        patches = g.remap(g.noise(pos, 7, detail=4), 0.6, 0.72)
        hang = None
        for top, length in tops:
            below = g.math("MULTIPLY", g.remap(z, top - length, top), g.remap(z, top + 0.015, top))
            hang = below if hang is None else g.math("MAXIMUM", hang, below)
        streak = g.math("MULTIPLY", g.math("MULTIPLY", hang, g.remap(runs, 0.3, 0.68)), vertical)
        foot = g.math("MULTIPLY", g.remap(z, 0.32, 0.04), g.remap(g.noise(pos, 12, detail=5), 0.38, 0.62))
        ao = g.node("ShaderNodeAmbientOcclusion", Distance=0.1).outputs["AO"]
        cav = g.math("MULTIPLY", g.math("SUBTRACT", 1.0, ao), g.remap(g.noise(pos, 22, detail=4), 0.4, 0.6))
        m = g.math("ADD", g.math("ADD", g.math("MULTIPLY", streak, 1.8), foot), g.math("MULTIPLY", cav, 1.8))
        m = g.math("ADD", m, g.math("MULTIPLY", patches, 0.55))
        m = g.math("MULTIPLY", m, bloom, clamp=True)
        crust = g.mixc(g.noise(pos, 37, detail=3), rig.srgb("#BEBAAC"), rig.srgb("#E4E0D2"))
        return g.mixc(m, base, crust)
    return pat


def soften_grain(mat, lo=0.86, hi=1.1):
    """FFF #146 in numbers: vanilla's speckle is low against its mid-scale variation
    (finish.py's ratio ~0.5). The shared layered() maps its photo grain to 0.7-1.22 of
    the paint, which at 64 px a tile is per-pixel speckle; this narrows that range on
    this concept's own materials only (tools/blender/materials.py is untouched)."""
    for nd in mat.node_tree.nodes:
        if nd.type == "MAP_RANGE" and abs(nd.inputs["To Min"].default_value - 0.7) < 1e-6 \
                and abs(nd.inputs["To Max"].default_value - 1.22) < 1e-6:
            nd.inputs["To Min"].default_value = lo
            nd.inputs["To Max"].default_value = hi
        if nd.type == "BUMP" and BUMP is not None:
            nd.inputs["Strength"].default_value = BUMP


GRAIN = (0.92, 1.05)   # the grain's range on every material below, from layered()'s 0.7-1.22
BUMP = 0.12            # the photo relief's strength, from layered()'s 0.3


WET = ("#2E1A0E", "#6A3818")        # the Vacuum Furnace's wet rust, for the runs below fittings
M = {
    # the signature: the vessels' lead cladding
    # rust runs from the steel bands' rivets down the lead, dark and wet, beside the bloom
    "lead": layered("lead", "#5E6064", metal="#A4A6AA", paint_metal=0.3, paint_rough=0.66, wear=0.2,
                    rust=0.04, dust=0.45, grime=0.8, jitter=0.08, ground=0.75, pattern=lead_finish(),
                    drips=tuple((t - 0.03, l * 0.8) for t, l in BLOOM_TOPS), drip=0.55, rust_tint=WET),
    # a sheet replaced: newer lead, a shade lighter, no bloom yet (3.3's variation)
    "lead_new": layered("lead_new", "#6A6C70", metal="#B4B6BA", paint_metal=0.35, paint_rough=0.6, wear=0.2,
                        rust=0.0, dust=0.25, grime=0.6, jitter=0.03, ground=0.5,
                        pattern=lead_finish(bloom=0.0, gain=1.16)),
    # the shared base: dark painted steel (kamacite plate), rust running from its bolts
    "plate": layered("plate", "#68625A", metal="#B0AA9E", paint_metal=0.12, paint_rough=0.62, wear=0.5,
                     rust=0.3, dust=0.35, grime=0.75, jitter=0.14, ground=0.7,
                     drips=((0.62, 0.32), (0.95, 0.3)), drip=0.6, rust_tint=WET),
    "shell": layered("shell", "#5E574F", metal="#A8A296", paint_metal=0.1, paint_rough=0.66, wear=0.55,
                     rust=0.35, dust=0.3, grime=0.75, jitter=0.16, ground=0.7,
                     drips=((0.8, 0.35), (1.4, 0.4)), drip=0.7, rust_tint=WET),
    "newplate": layered("newplate", "#6E6A62", metal="#B4AEA4", paint_metal=0.4, paint_rough=0.5, wear=0.2,
                        rust=0.05, dust=0.3, grime=0.5, jitter=0.02, ground=0.5),
    "steel": layered("steel", "#857F76", metal="#D2CCC2", paint_metal=0.8, paint_rough=0.33, wear=0.55,
                     rust=0.28, dust=0.1, grime=0.5, ground=0.7),
    "seam": layered("seam", "#7A7268", metal="#A49C90", paint_metal=0.7, paint_rough=0.4, wear=0.3,
                    rust=0.2, dust=0.0, jitter=0.04, ground=0.7),
    "cast": layered("cast", "#4A4744", metal="#9A968E", paint_metal=0.45, paint_rough=0.7, wear=0.4,
                    rust=0.35, dust=0.3, grime=0.7, ground=0.7, rust_tint=WET),
    "copper": layered("copper", "#94592C", metal="#C88A56", paint_metal=0.9, paint_rough=0.38, wear=0.4,
                      rust=0.08, dust=0.15, grime=0.5, patina=1.0),
    "brass": layered("brass", "#9C7034", metal="#CCA460", paint_metal=0.9, paint_rough=0.38, wear=0.45,
                     rust=0.1, dust=0.15),
    "teal": layered("teal", "#336C66", metal="#A8B0A8", paint_metal=0.05, paint_rough=0.7, wear=0.6,
                    rust=0.3, dust=0.35, grime=0.7, ground=0.6, jitter=0.1, rust_tint=WET),
    # hoses: the Vacuum Furnace's dull rust-brown rubber, a step lighter than the walls
    "hose": layered("hose", "#93603F", metal="#C89270", paint_metal=0.0, paint_rough=0.7, wear=0.4,
                    rust=0.0, dust=0.35, grime=0.6, jitter=0.06),
    "hose_k": layered("hose_k", "#3A3633", metal="#7E7872", paint_metal=0.0, paint_rough=0.6, wear=0.4,
                      rust=0.0, dust=0.45, grime=0.5, jitter=0.06),
    "lag": layered("lag", "#8E826A", metal="#B4A88E", paint_metal=0.0, paint_rough=0.9, wear=0.25,
                   rust=0.3, dust=0.5, grime=0.7, jitter=0.12, ground=0.6),
    "hazard": layered("hazard", "#B8962E", paint_metal=0.1, paint_rough=0.85, wear=0.75, rust=0.35,
                      dust=0.9, grime=0.8,
                      pattern=lambda g: g.mixc(0.4, hazard_pattern(g), (0.16, 0.13, 0.09, 1.0))),
    "stencil": layered("stencil", "#CFC6AE", metal="#5A564F", paint_metal=0.05, paint_rough=0.85, wear=0.7,
                       rust=0.2, dust=0.4, grime=0.5, jitter=0.05),
    "gauge": layered("gauge", "#8E877B", paint_metal=0.0, paint_rough=0.75, wear=0.15, rust=0.05,
                     dust=0.4, grime=0.6),
    "rubber": layered("rubber", "#24221F", metal="#4A453E", paint_metal=0.0, paint_rough=0.6, wear=0.1,
                      rust=0.0, dust=0.3, grime=0.3),
    "jbox": layered("jbox", "#5A6052", metal="#A8A498", paint_metal=0.1, paint_rough=0.6, wear=0.5, rust=0.25,
                    dust=0.4, grime=0.7, ground=0.6),
}
# cables: the Vacuum Furnace's muted set, without its blue -- blue is the solution's alone
for _n, _c, _e in (("red", "#B24C38", "#E09078"), ("yellow", "#CCA848", "#EED898"),
                   ("green", "#5E8452", "#A0C090"), ("black", "#3A3836", "#7A7672"),
                   ("grey", "#4C4A47", "#7E7A74")):
    M["cable_" + _n] = layered("cable_" + _n, _c, metal=_e, paint_metal=0.0, paint_rough=0.5, wear=0.3,
                               rust=0.0, dust=0.25, grime=0.4, jitter=0.05)
M["cable_blue"] = M["cable_grey"]     # round 2's kit defaults to a blue cable; never blue here

if GRAIN:
    for _m in M.values():
        soften_grain(_m, *GRAIN)

# ---------------------------------------------------------------- round 2's helpers (r2_blockout.py), the hose's ribs coarsened
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
    sweep(P, r, mat, corr=0.09, pitch=0.085, seg=18)   # round 3: ribs coarsened, 0.045 -> 0.085
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


# ======================================================================= round-3 kit
def arc_panel(cx, cy, r, z0, z1, a0, a1, mat, seg=24):
    """A curved sheet laid on a vessel of radius r between angles a0..a1: a
    replacement panel or a stencil field, standing just proud of the wall."""
    me = bpy.data.meshes.new("arc")
    bm = bmesh.new()
    rows = []
    for rr in (r, r + 0.012):
        ring = []
        for k in range(seg + 1):
            a = a0 + (a1 - a0) * k / seg
            ring.append((bm.verts.new((cx + rr * math.cos(a), cy + rr * math.sin(a), z0)),
                         bm.verts.new((cx + rr * math.cos(a), cy + rr * math.sin(a), z1))))
        rows.append(ring)
    inner, outer = rows
    for k in range(seg):
        bm.faces.new((outer[k][0], outer[k + 1][0], outer[k + 1][1], outer[k][1]))
        bm.faces.new((inner[k][1], inner[k + 1][1], inner[k + 1][0], inner[k][0]))
        bm.faces.new((inner[k][1], outer[k][1], outer[k + 1][1], inner[k + 1][1]))
        bm.faces.new((inner[k + 1][0], outer[k + 1][0], outer[k][0], inner[k][0]))
    for k in (0, seg):
        s = 1 if k == 0 else -1
        f = (inner[k][0], outer[k][0], outer[k][1], inner[k][1])
        bm.faces.new(f if s > 0 else tuple(reversed(f)))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("arc", me)
    sc.collection.objects.link(o)
    return _finish(o, mat, 0.004, smooth=True)


def weld_ring(cx, cy, z, r):
    torus((cx, cy, z), r + 0.004, 0.011, "seam", seg=72)


def rivet_ring(cx, cy, z, r, n, mat="steel", rr=0.019):
    for i in range(n):
        a = 2 * PI * (i + 0.5) / n
        sphere((cx + r * math.cos(a), cy + r * math.sin(a), z), rr, mat, scale=(1, 1, 0.8), seg=8)


def vessel_band(cx, cy, z, r, n_rivets=16, lugs=3, lug_a=-PI / 2):
    """A steel band: riveted both edges, bolted lugs. Rust runs from it (the plate's drips),
    the lead's bloom hangs below it."""
    band(cx, cy, z, r, h=0.075, mat="steel", lugs=lugs, lug_a=lug_a)
    rivet_ring(cx, cy, z, r + 0.032, n_rivets)


def vertical_seams(cx, cy, r, z0, z1, angles):
    for a in angles:
        box((cx + (r + 0.004) * math.cos(a), cy + (r + 0.004) * math.sin(a), (z0 + z1) / 2),
            (0.02, 0.02, z1 - z0), "seam", rz=a, bevel=0.005)


def press(x0, x1, y, d=0.72):
    """A plate-and-frame filter press lying E-W: cast feet and rails, leaves of lead and
    plate, the hydraulic head at the east end, a drip tray below."""
    L = x1 - x0
    box(((x0 + x1) / 2, y, 0.05), (L + 0.05, d + 0.06, 0.1), "cast")                      # drip tray
    for s in (-1, 1):
        box(((x0 + x1) / 2, y + s * (d / 2 - 0.03), 0.66), (L, 0.06, 0.07), "steel", bevel=0.008)  # rails
    box((x0 + 0.06, y, 0.4), (0.12, d, 0.72), "cast")                                       # tail stand
    n = int((L - 0.5) / 0.1)
    for i in range(n):
        xx = x0 + 0.17 + 0.1 * i
        box((xx, y, 0.4), (0.094, d - 0.1, 0.5 + 0.02 * (i % 3 == 0)), "lead" if i % 2 else "plate",
            bevel=0.006)
    hx = x0 + 0.17 + 0.1 * n + 0.12
    box((hx, y, 0.42), (0.16, d + 0.02, 0.78), "cast")                                       # head
    cyl((hx + 0.18, y, 0.45), 0.13, 0.26, "teal", rot=(0, PI / 2, 0), verts=24)            # ram cylinder
    handwheel((hx + 0.34, y, 0.45), 0.14, axis=(1, 0, 0))
    box(((x0 + x1) / 2, y - d / 2 - 0.035, 0.05), (L * 0.8, 0.01, 0.06), "hazard", bevel=0)
    return hx


def stencil(loc, size, rz):
    box(loc, size, "stencil", rz=rz, bevel=0.002)


def tray(pts, w=0.16):
    """A cable tray on stand-off posts: a shallow channel, the bundle lying in it."""
    P = catmull(pts, 0.05)
    for a_, b_ in zip(P[::3], P[3::3]):
        m = (a_ + b_) / 2
        t = (b_ - a_)
        box(tuple(m), (w, t.length + 0.01, 0.02), "steel", rz=math.atan2(t.y, t.x) - PI / 2, bevel=0.003)


# ======================================================================= the circulator
RX, RY, R, H = 1.5, 0.1, 0.86, 2.95            # the reactor: forward of round 2's, clear of the north pictures
LEGS = [(-0.36, 0.46, 2, "fl_f1"), (0.24, -0.6, -2, "fl_f2")]
Z0, Z1, LR = 0.42, 2.45, 0.27


def reactor():
    cyl((RX, RY, 0.08), R + 0.12, 0.16, "cast", verts=72)
    bolts(RX, RY, 0.17, R + 0.07, 24, r=0.016)
    cyl((RX, RY, H / 2 + 0.08), R, H - 0.16, "lead", verts=96)
    for z in (0.47, 1.17, 1.87, 2.52):
        vessel_band(RX, RY, z, R, lug_a=-PI / 2 - 0.4)
    for z in (0.82, 1.52, 2.2):
        weld_ring(RX, RY, z, R)
    vertical_seams(RX, RY, R, 0.52, 1.13, (-2.0, -0.6, 1.3))
    vertical_seams(RX, RY, R, 1.22, 1.83, (-1.3, 0.2, 2.4))
    vertical_seams(RX, RY, R, 1.92, 2.48, (-2.2, -0.9, 0.7))
    # a replaced sheet on the south-west face, and a stencil field on the south face
    arc_panel(RX, RY, R, 1.2, 1.84, -2.35, -1.75, "lead_new")
    rivet_ring_arc = [(-2.35 + 0.6 * i / 7) for i in range(8)]
    for a in rivet_ring_arc:
        for z in (1.24, 1.8):
            sphere((RX + (R + 0.016) * math.cos(a), RY + (R + 0.016) * math.sin(a), z), 0.012, "steel", seg=8)
    arc_panel(RX, RY, R + 0.002, 1.95, 2.12, -1.85, -1.3, "stencil")
    arc_panel(RX, RY, R + 0.002, 0.6, 0.74, -1.2, -0.85, "hazard")
    # the head: lead, a bolted manway, the agitator drive and its teal motor
    head(RX, RY, H, R, 0.28, "lead")
    flange_ring(RX, RY, H + 0.005, R - 0.02, mat="steel", h=0.05, nb=32)
    for k in range(8):                                    # the head's radial weld seams
        a = 2 * PI * (k + 0.5) / 8
        P = [Vector((RX + rr * math.cos(a), RY + rr * math.sin(a),
                     H + 0.004 + 0.28 * math.sqrt(max(0.0, 1 - (rr / R) ** 2)))) for rr in
             [0.3 + 0.52 * i / 12 for i in range(13)]]
        sweep(P, 0.011, "seam", seg=8)
    cyl((RX + 0.4, RY - 0.3, H + 0.25), 0.17, 0.1, "cast", verts=32)       # manway
    bolts(RX + 0.4, RY - 0.3, H + 0.31, 0.13, 10, r=0.014)
    cyl((RX - 0.5, RY + 0.28, H + 0.26), 0.06, 0.16, "steel", verts=16)    # relief valve
    cyl((RX - 0.5, RY + 0.28, H + 0.36), 0.09, 0.06, "brass", verts=6, bevel=0)
    cyl((RX - 0.5, RY + 0.28, H + 0.43), 0.035, 0.1, "steel", verts=12)
    cyl((RX + 0.05, RY - 0.58, H + 0.18), 0.07, 0.12, "steel", verts=16)   # a capped nozzle
    flange_ring(RX + 0.05, RY - 0.58, H + 0.24, 0.06, mat="cast", h=0.03, nb=6)
    gauge((RX - 0.42, RY - 0.4, H + 0.24), (-0.3, -0.6, 0.8), r=0.055)
    cyl((RX - 0.1, RY - 0.05, H + 0.32), 0.2, 0.16, "cast", verts=32)
    coupling(RX - 0.1, RY - 0.05, H + 0.44, 0.16)
    box((RX + 0.22, RY + 0.22, H + 0.42), (0.32, 0.34, 0.3), "teal", rz=0.3)
    for i in range(5):
        box((RX + 0.22, RY + 0.22, H + 0.58), (0.3, 0.025, 0.02), "cast", rz=0.3 + PI / 2, bevel=0)
    bundle([(RX + 0.22, RY + 0.4, H + 0.45), (RX + 0.45, RY + 0.6, H + 0.1), (RX + 0.62, RY + 0.55, 2.4)],
           cols=("black", "yellow"))
    # the ladder up the south face, a gauge and a sample valve
    ladder(RX + 0.42, RY - R * 0.88 - 0.05, 0.2, H - 0.05, axis="x")
    gauge((RX - 0.05, RY - R - 0.02, 0.95), (0.0, -1, 0.15))
    gauge((RX + 0.7, RY - R * 0.62, 1.55), (0.75, -0.62, 0.15), r=0.06)
    cyl((RX - 0.2, RY - R - 0.06, 0.32), 0.04, 0.14, "brass", rot=(PI / 2, 0, 0), verts=12)
    handwheel((RX - 0.2, RY - R - 0.14, 0.32), 0.06, axis=(0, 1, 0))


def legs():
    for lx, ly, k, nm in LEGS:
        cyl((lx, ly, 0.2), LR + 0.1, 0.4, "cast", verts=40)
        bolts(lx, ly, 0.41, LR + 0.06, 10, r=0.014)
        flange_ring(lx, ly, Z0 - 0.03, LR, h=0.06)
        flange_ring(lx, ly, Z1 + 0.01, LR, h=0.06)
        cyl((lx, ly, (Z0 + Z1) / 2), LR, Z1 - Z0, "glass", verts=48, bevel=0)
        fl = cyl((lx, ly, (Z0 + Z1) / 2), LR - 0.05, Z1 - Z0 - 0.02, fluid(nm, "flow", scale=3.2, k=k), verts=48,
                 bevel=0)
        fl.visible_diffuse = False      # the solution lights its glass, not the lead beside it: blue stays in the legs
        band(lx, ly, (Z0 + Z1) / 2, LR, h=0.06, mat="steel", lugs=2, lug_a=0.3)
        for j in range(4):
            a = 2 * PI * (j + 0.5) / 4 + 0.3
            box((lx + (LR + 0.01) * math.cos(a), ly + (LR + 0.01) * math.sin(a), (Z0 + Z1) / 2),
                (0.04, 0.04, Z1 - Z0), "steel", rz=a, bevel=0.004)
        cyl((lx, ly, Z1 + 0.16), LR * 0.75, 0.24, "cast", verts=32)
        head(lx, ly, Z1 + 0.28, LR * 0.75, 0.1, "lead")
    (ax, ay, _, _), (bx, by, _, _) = LEGS
    drift(lambda u, a: (ax + (LR - 0.04) * math.cos(-PI / 2 + a), ay + (LR - 0.04) * math.sin(-PI / 2 + a),
                        Z0 + 0.04 + (Z1 - Z0 - 0.08) * u), 22, 11)
    drift(lambda u, a: (bx + (LR - 0.05) * math.cos(-PI / 2 + a), by + (LR - 0.05) * math.sin(-PI / 2 + a),
                        Z0 + 0.04 + (Z1 - Z0 - 0.08) * u), 18, 12, mat="fleck", size=(0.014, 0.024),
          scale=(1.5, 1, 0.6), down=True)
    # the loop's top: fat hoses from each leg's cap into the reactor's shoulder
    hose([(ax, ay, Z1 + 0.42), (ax + 0.12, ay + 0.08, 2.98), (0.2, 0.56, 3.0), (RX - R + 0.04, RY + 0.32, 2.66)],
         r=0.12, mat="hose")
    hose([(bx, by, Z1 + 0.42), (bx + 0.14, by + 0.02, 2.95), (0.62, -0.5, 2.78),
          (RX - R * 0.62, RY - R * 0.72, 2.33)], r=0.12, mat="hose_k")
    # the loop's foot: a cast header from the reactor's foot to both legs, a valve on it
    pipe([(RX - R + 0.02, RY + 0.25, 0.28), (0.3, 0.45, 0.22), (ax + LR, ay, 0.22)], r=0.1, mat="cast")
    pipe([(RX - R * 0.65, RY - R * 0.7, 0.28), (0.75, -0.62, 0.22), (bx + LR, by, 0.22)], r=0.1, mat="cast")
    valve(0.2, 0.1, 0.0, 0.55)
    # between the legs' feet: the sampling box, where the precipitate is drawn off and checked
    jbox(-0.12, -0.14, 0.36, 0.3, 0.68, mat="plate")
    gauge((-0.12, -0.3, 0.5), (0, -1, 0.2), r=0.05)
    hose([(-0.12, -0.14, 0.72), (0.0, -0.3, 0.9), (bx - LR - 0.02, by + 0.1, 1.0)], r=0.04, mat="cable_black")
    valve(0.78, 0.92, 0.0, 0.6)
    return ax, ay, bx, by


def back():
    """The back strip (y > 1.3) between the corners stays under the north pictures'
    band: a low exchanger on saddles and its valves. The corners carry the height."""
    # NW: the scrubber, lead-clad as the reactor, banded
    sx, sy, sr, sh = -1.93, 1.84, 0.48, 1.7
    cyl((sx, sy, 0.07), sr + 0.08, 0.14, "cast", verts=64)
    cyl((sx, sy, sh / 2 + 0.07), sr, sh - 0.14, "lead", verts=64)
    for z in (0.9, 1.6):
        vessel_band(sx, sy, z, sr, n_rivets=11, lugs=2, lug_a=-PI / 4)
    weld_ring(sx, sy, 0.45, sr)
    vertical_seams(sx, sy, sr, 0.14, 0.86, (-1.2, 0.4))
    head(sx, sy, sh, sr, 0.19, "lead")
    nx, ny = sx + 0.16, sy - 0.16
    cyl((nx, ny, sh + 0.2), 0.085, 0.16, "steel", verts=24)
    flange_ring(nx, ny, sh + 0.28, 0.08, mat="steel", h=0.035, nb=8)
    arc_panel(sx, sy, sr + 0.002, 1.12, 1.26, -1.6, -0.9, "stencil")
    # NE: a slim vent condenser, banded plate, a copper vent on its head
    tx, ty = 2.02, 1.95
    vtank(tx, ty, 0.36, 1.85, "shell", bands=(0.7, 1.35), top="cast", nozzle=None)
    cyl((tx - 0.08, ty - 0.05, 2.05), 0.05, 0.25, "copper", verts=16)
    torus((tx - 0.08, ty - 0.05, 2.17), 0.06, 0.018, "copper", seg=16)
    # the back exchanger, low, on saddles: the north edge's wall at tiles -1, 0, +1
    exchanger(-1.18, 1.5, 2.12, 0.36, 0.27, mat="plate")
    stencil((0.2, 1.77, 0.5), (0.5, 0.01, 0.12), 0.0)
    valve(-0.95, 1.38, 0.0, 0.5)
    valve(0.95, 1.42, 0.0, 0.45)
    # the crust-gas compressor between the riser and the exchanger: low, under the band
    box((0.32, 1.32, 0.07), (1.0, 0.5, 0.14), "cast")
    cyl((0.12, 1.32, 0.38), 0.22, 0.46, "cast", rot=(0, PI / 2, 0), verts=32)
    for i in range(6):
        cyl((-0.06 + 0.07 * i, 1.32, 0.38), 0.245, 0.025, "steel", rot=(0, PI / 2, 0), verts=32, bevel=0)
    box((0.62, 1.32, 0.36), (0.36, 0.38, 0.4), "teal")
    coupling(0.39, 1.32, 0.36, 0.11, axis=(1, 0, 0))
    hose([(0.12, 1.32, 0.62), (0.05, 1.0, 0.95), (LEGS[0][0] + 0.2, LEGS[0][1] + 0.2, 1.2)], r=0.08, mat="hose")
    # the teal pot by the riser, and the scrubber's line to the reactor head
    vtank(-0.95, 1.08, 0.27, 1.05, "teal", bands=(0.5,), nozzle=None)
    hose([(nx, ny, sh + 0.32), (-1.3, 1.32, 2.3), (-0.4, 1.1, 2.72), (0.6, 0.82, 3.06),
          (RX - 0.25, RY + 0.42, 3.15)], r=0.11, mat="hose")
    hose([(-0.95, 1.08, 1.12), (-0.75, 0.82, 1.4), (LEGS[0][0] - 0.05, LEGS[0][1] + 0.1, 2.62)], r=0.08,
         mat="hose_k")
    hose([(1.3, 2.08, 0.75), (1.55, 1.4, 1.1), (RX + 0.3, RY + R - 0.02, 1.2)], r=0.085, mat="hose")
    pipe([(tx - 0.3, ty - 0.1, 0.9), (1.85, 1.2, 0.95), (RX + 0.45, RY + R * 0.75, 0.95)], r=0.06, mat="copper")


def west():
    """The feed drum lying north-south along the west edge: the west wall at tiles 0, +1."""
    drum_ns(-2.0, -0.95, 0.95, 0.56, 0.44, mat="plate", bands=(-0.5, 0.5), saddles=(-0.65, 0.65))
    for yy in (-0.5, 0.5):
        rivet_ring_ns = [2 * PI * i / 20 for i in range(20)]
        for a in rivet_ring_ns:
            sphere((-2.0 + 0.475 * math.cos(a), yy + 0.03, 0.56 + 0.475 * math.sin(a)), 0.012, "steel", seg=8)
    box((-1.92, 0.0, 1.02), (0.3, 0.34, 0.06), "teal")
    stencil((-1.59, -0.1, 0.62), (0.01, 0.5, 0.14), 0.0)
    gauge((-1.6, 0.25, 0.75), (1, 0, 0.3), r=0.06)
    ax, ay = LEGS[0][0], LEGS[0][1]
    hose([(-1.6, 0.35, 0.5), (-1.0, 0.25, 0.36), (ax - LR - 0.08, ay - 0.08, 0.3)], r=0.09, mat="hose")
    jbox(-1.38, 0.62, 0.28, 0.24, 0.5, mat="jbox")
    jbox(-0.62, 0.02, 0.26, 0.24, 0.5, mat="plate")
    gauge((-0.72, -0.02, 0.4), (0, -1, 0.2), r=0.05)
    valve(-0.6, -0.42, 0.0, 0.62)
    valve(-1.45, 1.22, 0.0, 0.5)
    lagged([(-1.55, 1.5, 0.28), (-1.25, 1.28, 0.3), (-1.05, 1.0, 0.3)], r=0.08)
    # a dosing pump on its skid between the feed drum and the riser
    skid(-1.5, 0.12, -0.78, 0.5, 0.1)
    box((-1.3, 0.31, 0.27), (0.3, 0.26, 0.26), "teal")
    cyl((-0.98, 0.31, 0.26), 0.12, 0.2, "cast", rot=(0, PI / 2, 0), verts=24)
    coupling(-1.12, 0.31, 0.26, 0.08, axis=(1, 0, 0))
    # a rack of reagent bottles: chained, capped, one with its regulator and a red line
    box((-1.1, -0.42, 0.05), (0.84, 0.62, 0.1), "cast")
    for i, (bx_, by_) in enumerate(((-1.4, -0.6), (-1.17, -0.62), (-0.94, -0.6), (-1.3, -0.33), (-1.07, -0.3),
                                    (-0.84, -0.33))):
        m = ("shell", "teal", "newplate", "shell", "plate", "teal")[i]
        cyl((bx_, by_, 0.49), 0.1, 0.78, m, verts=24)
        head(bx_, by_, 0.88, 0.1, 0.06, m)
        cyl((bx_, by_, 0.97), 0.03, 0.08, "brass", verts=8)
    box((-1.12, -0.17, 0.66), (0.8, 0.03, 0.05), "steel", bevel=0.004)
    hose([(-0.9, -0.35, 0.98), (-0.7, -0.2, 0.9), (LEGS[0][0] - 0.2, LEGS[0][1] - 0.2, 0.5)], r=0.035,
         mat="cable_red")
    bundle([(-1.38, 0.62, 0.5), (-1.1, 0.75, 0.15), (-0.7, 0.8, 0.12), (RX - R, RY + 0.4, 0.5)],
           cols=("red", "black", "grey"))


def skid(x0, y0, x1, y1, h, mat="cast"):
    """A unit's own low skid: each front unit stands on one, at its own height, so the
    front is separate pieces of plant with narrow ground between, not one deck."""
    box(((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0, y1 - y0, h), mat, bevel=0.012)
    for xx in (x0 + 0.05, x1 - 0.05):
        for yy in (y0 + 0.05, y1 - 0.05):
            cyl((xx, yy, h + 0.006), 0.018, 0.016, "steel", verts=6, bevel=0)


def front():
    """The front third broken into units of different heights, each on its own skid,
    with narrow ground between them: the filter press, its drop box and a barrel
    pallet west; the filtrate receiver; the pump skid; a cabinet and a hose reel; a
    lead pot, barrels and a valve station behind them. Each meets the south edge at
    one of tiles -1, 0, +1 with a face, and nothing runs along the edge."""
    bx, by = LEGS[1][0], LEGS[1][1]
    hx = press(-2.46, -1.08, -1.56, d=0.78)
    # the drop box under the press's discharge: the solid out, lead-lined, hazard-taped
    skid(-1.78, -2.49, -0.56, -1.96, 0.1)
    cellbox(-1.17, -2.22, 1.1, 0.48, 0.5, wheel=False)
    box((-1.2, -1.94, 0.6), (0.44, 0.16, 0.2), "plate", rot=(0.5, 0, 0))                     # chute
    handwheel((-0.8, -2.22, 0.62), 0.1)
    skid(-2.49, -2.49, -1.82, -1.98, 0.06, mat="plate")                                        # a pallet
    for i, (x_, y_) in enumerate(((-2.36, -2.12), (-2.1, -2.11), (-2.36, -2.36), (-2.1, -2.36), (-1.94, -2.2))):
        m = ("plate", "teal", "lead", "shell", "hazard")[i]       # inside the edge: nothing crosses it (rule 5)
        cyl((x_, y_, 0.25), 0.12, 0.38, m, verts=24)
        for zz in (0.16, 0.34):
            torus((x_, y_, zz), 0.122, 0.011, "steel", seg=24)
        cyl((x_ + 0.05, y_ + 0.03, 0.445), 0.025, 0.02, "brass", verts=8)
    # the filtrate receiver on its saddles and skid, the cake hose from the press
    skid(-0.82, -1.68, 0.6, -0.98, 0.14)
    drum_ew(-0.68, 0.46, -1.33, 0.5, 0.28, mat="shell", bands=(-0.25, 0.25), saddles=(-0.45, 0.25))
    stencil((-0.1, -1.62, 0.52), (0.36, 0.01, 0.1), 0.0)
    # the pump skid, its motor teal; it lifts the downcomer's return
    pv = pump(0.12, -2.15, (-1, 0), 1.15)
    hose([pv, (-0.25, -1.85, 0.9), (-0.05, -1.25, 0.95), (bx - 0.05, by - LR - 0.06, 0.6)], r=0.1, mat="hose")
    hose([(hx + 0.1, -1.56, 0.82), (-0.75, -1.05, 1.0), (bx - LR - 0.04, by - 0.02, 0.85)], r=0.085,
         mat="hose_k")
    # south-east: a cabinet on the south edge, a taller teal one on the east edge, the reel
    skid(0.82, -2.49, 1.7, -1.86, 0.08, mat="plate")
    cabinet(1.24, -2.2, 0.78, 0.5, 0.9, mat="plate")
    box((1.24, -1.92, 0.5), (0.5, 0.06, 0.6), "plate", bevel=0.01)
    skid(1.76, -2.49, 2.49, -1.76, 0.1)
    reel(2.12, -2.1, (1, 0, 0))
    skid(1.86, -1.6, 2.49, -0.72, 0.08)
    cabinet(2.2, -1.15, 0.56, 0.75, 1.2, mat="teal")
    bundle([(2.2, -0.8, 1.15), (2.0, -0.3, 0.3), (RX + R * 0.55, RY - R * 0.75, 0.45)],
           cols=("red", "yellow", "black"))
    bundle([(1.24, -1.95, 0.85), (1.05, -1.5, 0.12), (0.7, -1.0, 0.12), (bx + 0.2, by - 0.25, 0.3)],
           cols=("black", "green"))
    # behind them: a lead pot, a barrel group, a valve station
    skid(0.62, -1.8, 1.82, -1.0, 0.12, mat="plate")
    vtank(0.95, -1.4, 0.27, 0.95, "lead", bands=(0.5,), top="cast", nozzle=(0, 0))
    hose([(0.95, -1.4, 1.25), (1.0, -1.05, 1.4), (RX - R * 0.4, RY - R * 0.9, 1.15)], r=0.075, mat="hose")
    barrels(1.52, -1.5, 3, 22, z=0.12)
    valve(-0.75, -0.85, 0.0, 0.5)
    jbox(-0.55, -1.84, 0.3, 0.2, 0.46, mat="jbox")
    # a short lagged main from the drop box's side to the downcomer foot, not on the edge
    lagged([(-0.6, -2.0, 0.3), (-0.5, -1.0, 0.28), (bx - 0.2, by - 0.25, 0.25)], r=0.09)


def east():
    """The east edge: the reactor's own wall at tile 0, the teal cabinet at -1, an
    instrument box at +1. Nothing runs along it."""
    skid(2.08, 0.78, 2.49, 1.5, 0.08)
    jbox(2.3, 1.15, 0.36, 0.66, 0.9, mat="plate")
    gauge((2.12, 1.0, 0.6), (-1, -0.3, 0.2), r=0.05)
    status_lamp(2.3, 1.15, 0.92)
    status_lamp(2.2, -1.35, 1.22)
    bundle([(2.3, 1.15, 0.72), (2.1, 0.95, 0.3), (RX + R * 0.8, RY + R * 0.5, 0.35)], cols=("grey", "red"))


reactor()
legs()
back()
west()
front()
east()

# ---------------------------------------------------------------- lights, passes
rig.camera(*CANVAS, centre_px=CENTRE, ss=SSK)
rig.sun()
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()


def pose(t):
    for p in ANIM:
        p(t)
    for node, k in PHASES:
        node.outputs[0].default_value = 2 * math.pi * k * t


def working(on):
    for sock, v in GLOWS:
        sock.default_value = v if on else 0.0
    LAMP_ON.default_value = 3.0 if on else 0.0


if ONLY in (None, "idle"):
    pose(0.0)
    working(False)
    rig.render(os.path.join(OUT, "idle.png"))
    GROUND.hide_render = True
    rig.render(os.path.join(OUT, "plate.png"))
    working(True)
    rig.render(os.path.join(OUT, "plate-working.png"))
    GROUND.hide_render = False
if ONLY in (None, "working"):
    working(True)
    for f in range(NF):
        pose(f / NF)
        rig.render(os.path.join(OUT, f"working-{f:02d}.png"))
print("done")
