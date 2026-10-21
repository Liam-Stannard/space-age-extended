"""The Radiant Generator's wreck: what its corpse draws once it is destroyed (spec 6: "the
machine's own wreck, rendered at the model stage, as the Siderane turbine's"; decision 6, "Own
wreck, like turbine").

The Carousel Foundry broken where it stood, in its own materials, sooted, low on the ground as
vanilla's remnants lie, its shadow and a scorch caught in the one picture (contract.py's
remnants pass; pack.py packs it). The Siderane turbine's recipe (concept/crust-turbine/model/
crust_turbine.py, section 10, on master): its torn shells, shards and lumps, its sooted
materials with the bare edges glinting through, its scorch, all drawn in about the centre so
the debris stays on the footprint.

  - the deck: most slabs where they lay, some heaved and tilted, a few gone;
  - the carousel: the lead drum burst open on its north-east side; the turning table thrown
    off its bearing and lying tilted on the rim; the hub's dome rolled off west; the loading
    hood's plates fallen; spent cells spilled across the deck (no fresh one, and nothing lit:
    the light is gone with the machine);
  - the crane: its bridge fallen across the deck from the crucible to the carousel, one end on
    the ground; the trolley fallen off it; two of the three posts snapped short;
  - the crucible: its lead walls standing to half their height, torn; the roof plates thrown
    off round it; copper collector plates leaning out of the open top; the well's collar on
    the deck;
  - the tubes: their sockets on the east strip, the glass broken to jagged stumps, two caps
    and one whole tube lying on the ground;
  - the converter: the bedplate in place, the AC machine rolled off it to the south, the DC
    motor's shell split, the commutator drum lying loose;
  - the transformer knocked onto its back, its bushings broken; one cabinet toppled, the
    other standing with its door torn off; the shield housing collapsed with its teal roof
    lying on the rubble; the radiator fallen flat; the expansion tank toppled; gas bottles
    and barrels lying; hoses and trunks sprawled.

Built into rg_kit's OBJS in the "wreck" group (radiant_generator.py renders it alone).
"""
import math
import random

import bmesh
import bpy
from mathutils import Vector

import rg_kit as K
from rg_kit import PI, box, cyl, torus, annulus, sector, head, sphere, cell, hose, trunk, bundle, bolts

RNG = random.Random(20261020)
WRECK_SCALE = 0.86          # the turbine's T02b: drawn in about the centre, debris on the footprint
SCORCH = (2.6, 2.6, 0.85)   # the scorch's half-axes on the ground (tiles, before the scale) and its darkest alpha


class frame:
    """Everything built inside is placed in an empty's frame: its coordinates are the empty's."""

    def __init__(self, loc=(0, 0, 0), rot=(0, 0, 0), scale=None):
        e = bpy.data.objects.new("wreck-frame", None)
        K.sc.collection.objects.link(e)
        e.parent = K.PARENT[-1] if K.PARENT else K.ROOT
        e.location, e.rotation_euler = loc, rot
        if scale:
            e.scale = (scale,) * 3
        self.e = e

    def __enter__(self):
        K.PARENT.append(self.e)
        return self.e

    def __exit__(self, *a):
        K.PARENT.pop()


def mesh_object(name, build, mat, bevel=0.0, smooth=False):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    K.sc.collection.objects.link(o)
    return K._finish(o, mat, bevel, smooth=smooth)


def shell(loc, r_out, r_in, h, mat, a0=0.0, a1=2 * PI, jag=0.0, seg=64, rot=(0, 0, 0)):
    """A cylinder's wall about local Z from angle a0 to a1, foot at 0, top at h, torn to a ragged
    top edge up to `jag` deep (the turbine's shell(), without its warp)."""
    full = abs(a1 - a0) >= 2 * PI - 1e-6
    n = seg if full else max(3, round(seg * abs(a1 - a0) / (2 * PI)))
    f1, f2, p1, p2 = RNG.uniform(2, 4), RNG.uniform(5, 9), RNG.uniform(0, 6.3), RNG.uniform(0, 6.3)
    notches = [RNG.uniform(0, 1) for _ in range(2)]
    tops = []
    for i in range(n + 1):
        u = i / n
        w = 0.5 + 0.3 * math.sin(f1 * 2 * PI * u + p1) + 0.2 * math.sin(f2 * 2 * PI * u + p2)
        w += 0.18 * (RNG.random() - 0.5)
        w += sum(0.6 * max(0.0, 1 - abs(u - c) * 14) for c in notches)
        tops.append(h - jag * min(1.0, max(0.0, w)))

    def build(bm):
        cols = []
        for i in range(n if full else n + 1):
            a = a0 + (a1 - a0) * i / n
            c, s = math.cos(a), math.sin(a)
            cols.append([bm.verts.new((r * c, r * s, z)) for r, z in
                         ((r_out, 0.0), (r_out, tops[i]), (r_in, tops[i]), (r_in, 0.0))])
        m = len(cols)
        for i in range(m if full else m - 1):
            A, B = cols[i], cols[(i + 1) % m]
            for k in range(4):
                bm.faces.new((A[k], B[k], B[(k + 1) % 4], A[(k + 1) % 4]))
        if not full:
            bm.faces.new(cols[0][::-1])
            bm.faces.new(cols[-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_object("shell", build, mat, 0.006, smooth=True)
    o.location, o.rotation_euler = loc, rot
    return o


def wall(loc, w, t, h, mat, rz=0.0, jag=0.12, n=12):
    """A straight wall w long, t thick, its top torn ragged up to `jag` deep."""
    tops = [h - jag * RNG.random() ** 0.7 for _ in range(n + 1)]

    def build(bm):
        cols = []
        for i in range(n + 1):
            x = -w / 2 + w * i / n
            cols.append([bm.verts.new((x, y, z)) for y, z in ((-t / 2, 0.0), (-t / 2, tops[i]), (t / 2, tops[i]),
                                                              (t / 2, 0.0))])
        for A, B in zip(cols, cols[1:]):
            for k in range(4):
                bm.faces.new((A[k], B[k], B[(k + 1) % 4], A[(k + 1) % 4]))
        bm.faces.new(cols[0][::-1])
        bm.faces.new(cols[-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_object("wall", build, mat, 0.004)
    o.location, o.rotation_euler = loc, (0, 0, rz)
    return o


def shard(loc, r, t, mat, rot=None, n=7, stretch=(1.0, 1.0)):
    """A torn plate: a ragged polygon r across, t thick."""
    pts = []
    for i in range(n):
        a = 2 * PI * (i + RNG.uniform(-0.3, 0.3)) / n
        rr = r * RNG.uniform(0.5, 1.0)
        pts.append((rr * math.cos(a) * stretch[0], rr * math.sin(a) * stretch[1]))

    def build(bm):
        lo = [bm.verts.new((x, y, -t / 2)) for x, y in pts]
        hi = [bm.verts.new((x, y, t / 2)) for x, y in pts]
        bm.faces.new(lo[::-1])
        bm.faces.new(hi)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_object("shard", build, mat, min(0.005, t / 3))
    o.location = loc
    o.rotation_euler = rot if rot is not None else (RNG.uniform(-0.25, 0.25), RNG.uniform(-0.25, 0.25),
                                                    RNG.uniform(0, 2 * PI))
    return o


def lump(loc, r, mat="dark_steel", flat=0.45):
    """A lump of rubble, low and rough."""
    def build(bm):
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
        sy = RNG.uniform(0.75, 1.25)
        for v in bm.verts:
            k = RNG.uniform(0.7, 1.15)
            v.co = Vector((v.co.x * k * r, v.co.y * k * r * sy, max(v.co.z, -0.2) * k * r * flat))
    o = mesh_object("lump", build, mat, 0.0)
    o.location, o.rotation_euler = loc, (0, 0, RNG.uniform(0, 2 * PI))
    return o


def lying_cell(x, y, a, spent=True):
    """A cell on its side on the deck (z 0 is the ground), its axis along angle a."""
    with frame((x, y, 0.09), (PI / 2, 0, a)):
        cell((0, 0, 0), not spent)


def scorch_material():
    """The ground darkened round the wreck: black, part transparent, its edge ragged (the
    turbine's scorch_material())."""
    m = bpy.data.materials.new("scorch")
    m.use_nodes = True
    t = m.node_tree
    for nd in list(t.nodes):
        if nd.bl_idname != "ShaderNodeOutputMaterial":
            t.nodes.remove(nd)
    out = next(nd for nd in t.nodes if nd.bl_idname == "ShaderNodeOutputMaterial")
    tc = t.nodes.new("ShaderNodeTexCoord")
    mp = t.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / SCORCH[0], 1 / SCORCH[1], 1.0)
    t.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    ln = t.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    t.links.new(mp.outputs["Vector"], ln.inputs[0])
    nz = t.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 2.2
    nz.inputs["Detail"].default_value = 6.0
    nz.inputs["Roughness"].default_value = 0.6
    t.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    edge = t.nodes.new("ShaderNodeMath")
    edge.operation = "MULTIPLY_ADD"
    t.links.new(nz.outputs["Fac"], edge.inputs[0])
    edge.inputs[1].default_value = 0.55
    t.links.new(ln.outputs["Value"], edge.inputs[2])
    fall = t.nodes.new("ShaderNodeMapRange")
    fall.inputs["From Min"].default_value = 0.55 + 0.55 * 0.5
    fall.inputs["From Max"].default_value = 1.0 + 0.55 * 0.5
    fall.inputs["To Min"].default_value = SCORCH[2]
    fall.inputs["To Max"].default_value = 0.0
    fall.clamp = True
    t.links.new(edge.outputs["Value"], fall.inputs["Value"])
    nz2 = t.nodes.new("ShaderNodeTexNoise")
    nz2.inputs["Scale"].default_value = 6.0
    nz2.inputs["Detail"].default_value = 4.0
    t.links.new(tc.outputs["Object"], nz2.inputs["Vector"])
    blot = t.nodes.new("ShaderNodeMapRange")
    blot.inputs["From Min"].default_value = 0.3
    blot.inputs["From Max"].default_value = 0.7
    blot.inputs["To Min"].default_value = 0.7
    blot.inputs["To Max"].default_value = 1.1
    t.links.new(nz2.outputs["Fac"], blot.inputs["Value"])
    a = t.nodes.new("ShaderNodeMath")
    a.operation = "MULTIPLY"
    a.use_clamp = True
    t.links.new(fall.outputs["Result"], a.inputs[0])
    t.links.new(blot.outputs["Result"], a.inputs[1])
    tr = t.nodes.new("ShaderNodeBsdfTransparent")
    blk = t.nodes.new("ShaderNodeBsdfDiffuse")
    blk.inputs["Color"].default_value = (0, 0, 0, 1)
    mix = t.nodes.new("ShaderNodeMixShader")
    t.links.new(a.outputs["Value"], mix.inputs["Fac"])
    t.links.new(tr.outputs["BSDF"], mix.inputs[1])
    t.links.new(blk.outputs["BSDF"], mix.inputs[2])
    t.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return m


# ---------------------------------------------------------------- the wreck
K.M["scorch"] = scorch_material()
K.CUR.append("wreck")
root = frame((0, 0, 0), scale=WRECK_SCALE)
K.PARENT.append(root.e)

CX, CY, RR, ZD = -1.05, 0.45, 1.25, 0.85

# -- the ground: the scorch, rubble heaved round the foot
bpy.ops.mesh.primitive_plane_add(size=2, location=(0.1, 0.1, 0.003))
sc_o = bpy.context.active_object
sc_o.scale = (SCORCH[0], SCORCH[1], 1)
bpy.ops.object.transform_apply(scale=True)
sc_o.visible_shadow = False
K._finish(sc_o, "scorch", 0)
for _ in range(16):
    a, r = RNG.uniform(0, 2 * PI), RNG.uniform(2.1, 2.6)
    lump((r * math.cos(a), r * math.sin(a), 0.0), RNG.uniform(0.08, 0.16), RNG.choice(("dark_steel", "lead", "grey")))

# -- the deck: slabs where they lay, some heaved, some gone
w = 4.4 / 9
for i in range(9):
    for j in range(9):
        cx, cy = -2.2 + w * (i + 0.5), -2.2 + w * (j + 0.5)
        if RNG.random() < 0.6:          # most of the deck torn up: the scorched ground shows
            continue
        hgt = RNG.choice((0.06, 0.08, 0.1))
        tilt = (RNG.uniform(-0.12, 0.12), RNG.uniform(-0.12, 0.12), RNG.uniform(-0.08, 0.08)) \
            if RNG.random() < 0.3 else (0, 0, 0)
        box((cx, cy, hgt / 2 + (0.03 if tilt[0] else 0)), (w - 0.02, w - 0.02, hgt),
            RNG.choice(("dark_steel", "dark_steel", "grey", "bare")), rot=tilt, bevel=0.01)

# -- the carousel: the drum burst open, the table thrown off, the dome rolled, cells spilled
with frame((CX, CY, 0.1)):
    cyl((0, 0, 0.0), RR + 0.16, 0.14, "dark_steel", verts=96)
    shell((0, 0, 0.05), RR + 0.06, RR - 0.02, 0.5, "lead", a0=1.3, a1=2 * PI - 0.2, jag=0.25, seg=96)
    shell((0, 0, 0.05), RR + 0.07, RR + 0.04, 0.12, "dark_steel", a0=1.6, a1=2 * PI - 0.5, jag=0.04, seg=96)
    bolts(0, 0, 0.08, RR + 0.11, 20, r=0.018)
# the table broken in three: one piece still on the rim, tilted, two fallen in and out
for (loc, rot, a0, a1) in (((CX + 0.1, CY - 0.05, 0.42), (0.18, -0.1, 0.3), -0.4, 2.6),
                           ((CX - 0.35, CY + 0.15, 0.2), (-0.35, 0.25, 0.0), 2.75, 4.3),
                           ((CX - 0.1, CY - 0.75, 0.14), (0.1, -0.5, 0.2), 4.45, 5.7)):
    with frame(loc, rot):
        sector((0, 0, 0), 0.0, RR * 0.94, a0, a1, 0.18, "lead_new", seg=24)
        sector((0, 0, -0.1), RR * 0.8, RR * 0.96, a0, a1, 0.04, "bare", seg=24)
        for k in range(8):
            a = 2 * PI * k / 8
            if not a0 + 0.2 < (a if a >= a0 else a + 2 * PI) < a1 - 0.2:
                continue
            px, py = RR * 0.62 * math.cos(a), RR * 0.62 * math.sin(a)
            cyl((px, py, 0.1), 0.18, 0.05, "dark_steel", verts=32)
            cyl((px, py, 0.125), 0.1, 0.02, "dark", verts=24, bevel=0)
            if k % 3 == 0:
                cyl((px, py, 0.16), 0.09, 0.1, "lead", verts=20)
with frame((CX - 0.95, CY + 0.6, 0.16), (0.3, 1.3, 0.4)):
    head(0, 0, 0, 0.42, 0.28, "lead")
    cyl((0, 0, -0.08), 0.42, 0.16, "lead", verts=64)
for k in range(3):
    with frame((CX + 0.9 * math.cos(2.4 + k), CY + 1.0 * math.sin(2.4 + k), 0.03), (0, 0.2, 2.4 + k)):
        sector((0, 0, 0), 0.0, 0.6, -0.3, 0.3, 0.05, "lead", seg=6)
for k, (x, y, a) in enumerate(((-0.1, -0.35, 0.4), (0.15, -0.6, 2.1), (-2.0, -0.6, 1.2), (-0.3, 1.55, 2.8),
                               (0.05, 0.85, -0.6))):
    lying_cell(x, y, a)
# the collector head toppled off south, its port shattered (dark: the light is gone)
with frame((CX + 0.55, CY - 1.55, 0.2), (0.0, 1.35, -0.4)):
    box((0, 0, 0), (0.62, 0.42, 0.22), "oxide", bevel=0.02)
    cyl((0, 0.0, 0.13), 0.12, 0.04, "dark_steel", verts=32)
    cyl((0, 0.0, 0.15), 0.09, 0.01, "dark", verts=24, bevel=0)

# -- the crucible: walls standing to half height, torn; plates leaning out; the roof thrown off
X0, X1, Y0, Y1, ZT = 0.45, 2.02, -0.8, 1.5, 1.05
box(((X0 + X1) / 2, (Y0 + Y1) / 2, 0.08), (X1 - X0 + 0.14, Y1 - Y0 + 0.14, 0.16), "dark_steel")
box(((X0 + X1) / 2, (Y0 + Y1) / 2, 0.2), (X1 - X0 - 0.1, Y1 - Y0 - 0.1, 0.1), "dark", bevel=0)
for (x, y, L, rz) in (((X0 + X1) / 2, Y0 + 0.05, X1 - X0, 0.0), ((X0 + X1) / 2, Y1 - 0.05, X1 - X0, 0.0),
                      (X0 + 0.05, (Y0 + Y1) / 2, Y1 - Y0, PI / 2), (X1 - 0.05, (Y0 + Y1) / 2, Y1 - Y0, PI / 2)):
    wall((x, y, 0.15), L, 0.1, 0.62, "lead", rz=rz, jag=0.32, n=14)
for k in range(5):
    with frame((0.75 + 0.18 * k, 1.1 - 0.05 * k, 0.2), (RNG.uniform(-0.5, -0.2), 0.0, RNG.uniform(-0.2, 0.2))):
        box((0, 0, 0.25), (0.03, 0.34, 0.5), "copper", bevel=0.003)
for _ in range(10):            # rubble fallen into the open crucible
    lump((RNG.uniform(0.7, 1.8), RNG.uniform(-0.6, 1.3), 0.26), RNG.uniform(0.16, 0.26), RNG.choice(("lead", "dark_steel")),
         flat=0.6)
for _ in range(5):            # and the plate rack's copper plates spilled among it
    shard((RNG.uniform(0.75, 1.75), RNG.uniform(-0.5, 1.2), 0.32), RNG.uniform(0.12, 0.2), 0.03, "copper")
for _ in range(9):
    a, r = RNG.uniform(-1.2, 1.4), RNG.uniform(0.95, 1.45)
    shard((1.25 + r * math.cos(a) * 0.8, 0.35 + r * math.sin(a), 0.04 + RNG.uniform(0, 0.05)),
          RNG.uniform(0.14, 0.24), 0.05, RNG.choice(("lead", "lead_new")))
with frame((1.6, -1.1, 0.05), (0.2, 0.0, 0.5)):
    annulus((0, 0, 0.0), 0.11, 0.36, 0.08, "lead", seg=40)
with frame((0.95, 0.35, 0.3), (0.6, 0.0, 0.0)):
    cyl((0, 0, 0), 0.19, 0.04, "grey", verts=32)
    bolts(0, 0, 0.025, 0.15, 8, r=0.012)

# -- the tubes: sockets on the east strip, glass broken to stumps, caps on the ground
box((2.25, 0.3, 0.06), (0.42, 2.3, 0.12), "dark_steel")
TY = [-0.62 + 0.46 * i for i in range(5)]
for i, y in enumerate(TY):
    if i == 3:
        continue
    cyl((2.25, y, 0.21), 0.16, 0.22, "dark_steel", verts=24)
    shell((2.25, y, 0.32), 0.12, 0.105, RNG.uniform(0.12, 0.3), "tube_glass", jag=0.12, seg=32)
    cyl((2.25, y, 0.36), 0.06, 0.08, "bezel", verts=16)
for (x, y, a) in ((2.38, -1.25, 0.6), (2.0, 2.05, 2.2)):
    with frame((x, y, 0.1), (PI / 2 * 0.9, 0, a)):
        cyl((0, 0, 0), 0.13, 0.12, "copper", verts=24)
        for j in range(8):
            aa = 2 * PI * j / 8 + 0.2
            box((0.16 * math.cos(aa), 0.16 * math.sin(aa), 0.01), (0.13, 0.02, 0.15), "copper", rz=aa, bevel=0.003)
with frame((1.95, TY[3] + 0.15, 0.12), (PI / 2, 0, 1.2)):
    cyl((0, 0, 0), 0.115, 0.55, "tube_glass", verts=32, bevel=0)
    cyl((0, 0, 0.05), 0.05, 0.3, "bezel", verts=16)
    cyl((0, 0, 0.33), 0.13, 0.12, "copper", verts=24)
for _ in range(6):
    shard((2.25 + RNG.uniform(-0.35, 0.3), RNG.uniform(-0.9, 1.5), 0.02), RNG.uniform(0.04, 0.08), 0.01, "tube_glass")

# -- the crane: the bridge fallen from the crucible to the carousel, the trolley off it, posts snapped
# lying across the rubble from the crucible's west wall to the deck, one end up on the wall
with frame((0.05, 0.25, 0.42), (0.0, -0.28, 0.35)):
    for dv in (-0.13, 0.13):
        box((0.0, dv, 0.0), (2.3, 0.07, 0.24), "ochre", bevel=0.008)
    box((0.0, 0.0, 0.13), (2.3, 0.3, 0.025), "ochre", bevel=0.004)
    box((-1.1, 0.0, 0.0), (0.22, 0.46, 0.2), "ochre", bevel=0.015)
for x in (-0.5, 0.4):
    box((x, CY + 1.33, 0.25), (0.14, 0.14, 0.5), "ochre", bevel=0.012)
    box((x, CY + 1.33, 0.08), (0.3, 0.3, 0.16), "dark_steel")
with frame((1.68, CY + 1.33, 0.0), (0.0, 0.5, 0.0)):
    box((0, 0, 0.7), (0.14, 0.14, 1.4), "ochre", bevel=0.012)
box((1.68, CY + 1.33, 0.08), (0.3, 0.3, 0.16), "dark_steel")
with frame((-0.45, -0.55, 0.12), (0.25, 0.1, 0.9)):
    box((0, 0, 0.0), (0.46, 0.78, 0.18), "ochre", bevel=0.015)
    for s in (-1, 1):
        cyl((0, s * 0.19, 0.12), 0.09, 0.34, "dark_steel", rot=(0, PI / 2, 0), verts=24)
lying_cell(-0.75, -0.2, 0.9)

# -- the shield housing collapsed, its roof on the rubble; the radiator flat; the tank toppled
for x, L in ((0.1, 0.6), (0.95, 0.7), (1.55, 0.4)):
    wall((x, 1.94, 0.0), L, 0.12, 0.42, "grey", jag=0.25, n=10)
with frame((0.75, 1.75, 0.38), (0.32, 0.1, 0.05)):
    box((0, 0, 0), (1.9, 0.36, 0.06), "teal", bevel=0.012)
    box((0, 0, 0.045), (1.75, 0.22, 0.03), "teal", bevel=0.008)
with frame((0.8, 1.35, 0.06), (1.45, 0.0, 0.1)):
    box((0, 0, 0), (1.6, 0.05, 0.75), "dark_steel", bevel=0.006)
    for k in range(13):
        box((-0.8 + 1.6 * k / 12, -0.035, 0), (0.022, 0.03, 0.73), "grey", bevel=0.004)
with frame((2.0, 1.75, 0.3), (0.0, PI / 2 - 0.1, 2.5)):
    cyl((0, 0, 0.0), 0.3, 1.05, "grey", verts=48)
    head(0, 0, 0.52, 0.3, 0.12, "teal")
    cyl((0, 0, 0.1), 0.325, 0.07, "dark_steel", verts=48)

# -- the converter: the bedplate, the AC machine rolled off south, the DC shell split
box((-0.27, -1.95, 0.18), (2.95, 0.98, 0.36), "dark_steel", bevel=0.015)
with frame((-0.5, -2.2, 0.36), (0.1, 0, 0.25)):
    cyl((0, 0, 0), 0.43, 0.85, "grey", rot=(0, PI / 2, 0), verts=48)
    for k in range(10):
        cyl((-0.4 + 0.08 * k, 0, 0), 0.455, 0.02, "dark_steel", rot=(0, PI / 2, 0), verts=48, bevel=0)
with frame((0.55, -1.95, 0.36), (0, PI / 2, 0)):
    shell((0, 0, -0.45), 0.4, 0.36, 0.9, "green", a0=0.6, a1=2 * PI - 0.9, jag=0.18, seg=48)
with frame((1.15, -1.45, 0.2), (0.4, 1.3, 0.0)):
    cyl((0, 0, 0), 0.32, 0.3, "copper", verts=36)
    for k in range(8):
        a = 2 * PI * k / 8
        box((0.322 * math.cos(a), 0.322 * math.sin(a), 0), (0.04, 0.035, 0.3), "sil", rz=a, bevel=0)

# -- the transformer on its back, its bushings broken; the cabinets
with frame((-2.05, -1.9, 0.42), (-1.35, 0, 0.15)):
    box((0, 0, 0), (0.58, 0.8, 0.8), "cream", bevel=0.02)
    for k in range(6):
        box((-0.25 + 0.1 * k, -0.44, 0), (0.025, 0.08, 0.64), "cream", bevel=0.004)
for k in range(4):
    shard((-1.6 + RNG.uniform(-0.3, 0.3), -1.25 + RNG.uniform(-0.2, 0.2), 0.03), 0.05, 0.03, "ceramic")
with frame((1.95, -1.65, 0.22), (PI / 2 - 0.15, 0, 0.3)):
    box((0, 0, 0), (0.42, 1.15, 0.6), "green", bevel=0.015)
box((1.75, -2.0, 0.35), (0.4, 0.6, 0.7), "grey", bevel=0.015)
with frame((1.45, -2.38, 0.02), (0.05, 0, 0.6)):
    box((0, 0, 0), (0.36, 0.5, 0.02), "grey", bevel=0.004)

# -- trunks and hoses sprawled; bottles, barrels and pump down
trunk([(-1.9, -1.3, 0.3), (-1.5, -1.0, 0.08), (-0.9, -1.15, 0.06)], r=0.05)
trunk([(-2.3, -2.2, 0.15), (-2.42, -2.3, 0.08), (-2.4, -2.45, 0.05)], r=0.065)
hose([(-1.4, 2.15, 0.08), (-0.6, 2.25, 0.07), (0.1, 1.95, 0.25)], r=0.07, mat="hose")
hose([(1.75, 1.1, 0.06), (1.5, 0.75, 0.05), (1.6, 0.4, 0.2)], r=0.05, mat="hose_k")
bundle([(1.9, -1.0, 0.05), (2.2, -0.7, 0.08), (2.4, -0.95, 0.04)], cols=("red", "black", "red"), r=0.025)
for k, (x, y, a) in enumerate(((-2.1, 2.2, 0.3), (-1.75, 2.05, 1.6), (-2.3, 1.6, 2.7))):
    with frame((x, y, 0.11), (PI / 2, 0, a)):
        cyl((0, 0, 0), 0.11, 0.6, ("green", "grey", "hazard")[k], verts=24)
        head(0, 0, 0.3, 0.11, 0.06, "dark_steel")
with frame((-0.75, 2.2, 0.2), (0, 0.25, 0.3)):
    cyl((0, 0, 0), 0.17, 0.5, "oxide", rot=(0, PI / 2, 0), verts=32)
    cyl((-0.4, 0, -0.03), 0.14, 0.3, "green", rot=(0, PI / 2, 0), verts=32)
for k, (x, y) in enumerate(((0.6, -1.3), (0.95, -1.15))):
    with frame((x, y, 0.1), (PI / 2, 0, 0.7 + k)):
        cyl((0, 0, 0), 0.1, 0.32, ("oxide", "grey")[k], verts=20)
# the spent bin, west, split; the loading hood's ports
wall((-2.28, -0.3, 0.0), 0.5, 0.42, 0.38, "lead", rz=PI / 2, jag=0.15, n=6)
for k in range(10):
    a, r = RNG.uniform(0, 2 * PI), RNG.uniform(0.3, 2.2)
    shard((r * math.cos(a), r * math.sin(a), 0.03), RNG.uniform(0.05, 0.12), 0.02,
          RNG.choice(("dark_steel", "grey", "bare", "ochre")))
for k in range(12):
    a, r = RNG.uniform(0, 2 * PI), RNG.uniform(0.4, 2.2)
    lump((r * math.cos(a), r * math.sin(a), 0.02), RNG.uniform(0.05, 0.1), RNG.choice(("dark_steel", "lead")))

K.PARENT.pop()
K.CUR.pop()


# ---------------------------------------------------------------- the soot (the turbine's T02b/T02c)
SOOT = "#0D0B09"
SOOT_MIX = (0.84, 0.98)               # the soot's share, where the noise is thinnest and thickest
SOOT_ROUGH = 0.82
SOOT_METAL = 0.45
GLINT_EDGE = (0.995, 0.95)
GLINT_R = 0.05
GLINT_METAL = "#ECE6DA"
GLINT_ROUGH = 0.2
# the share of the soot a convex edge sheds, per material: the bare metal and the lead's torn rims
# most, the paints a little
GLINT = dict(bare=0.6, seam=0.3, lead=0.2, lead_new=0.2, copper=0.3, brass=0.2, dark_steel=0.1, ochre=0.15,
             grey=0.1, green=0.1, cream=0.1, teal=0.1, oxide=0.1, bolt=0.05)


def sooted(m):
    s_ = m.copy()
    s_.name = m.name + "-soot"
    t = s_.node_tree
    b = next((nd for nd in t.nodes if nd.bl_idname == "ShaderNodeBsdfPrincipled"), None)
    if b is None:
        return m
    geo = t.nodes.new("ShaderNodeNewGeometry")
    nz = t.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.5
    nz.inputs["Detail"].default_value = 5.0
    t.links.new(geo.outputs["Position"], nz.inputs["Vector"])
    mask = t.nodes.new("ShaderNodeMapRange")
    mask.inputs["From Min"].default_value = 0.35
    mask.inputs["From Max"].default_value = 0.65
    mask.inputs["To Min"].default_value = SOOT_MIX[0]
    mask.inputs["To Max"].default_value = SOOT_MIX[1]
    mask.clamp = True
    t.links.new(nz.outputs["Fac"], mask.inputs["Value"])
    edge = t.nodes.new("ShaderNodeMapRange")
    edge.inputs["From Min"].default_value = GLINT_EDGE[0]
    edge.inputs["From Max"].default_value = GLINT_EDGE[1]
    edge.inputs["To Min"].default_value = 1.0
    edge.inputs["To Max"].default_value = 1.0 - GLINT.get(m.name.split(".")[0], 0.0)
    edge.clamp = True
    bev = t.nodes.new("ShaderNodeBevel")
    bev.samples = 8
    bev.inputs["Radius"].default_value = GLINT_R
    dot = t.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    t.links.new(bev.outputs["Normal"], dot.inputs[0])
    t.links.new(geo.outputs["Normal"], dot.inputs[1])
    t.links.new(dot.outputs["Value"], edge.inputs["Value"])
    fac = t.nodes.new("ShaderNodeMath")
    fac.operation = "MULTIPLY"
    t.links.new(mask.outputs["Result"], fac.inputs[0])
    t.links.new(edge.outputs["Result"], fac.inputs[1])

    def toward(sock, value, rgba):
        mix = t.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA" if rgba else "FLOAT"
        ins = {i.identifier: i for i in mix.inputs}
        a, bb = (ins["A_Color"], ins["B_Color"]) if rgba else (ins["A_Float"], ins["B_Float"])
        t.links.new(fac.outputs["Value"], ins["Factor_Float"])
        if sock.links:
            t.links.new(sock.links[0].from_socket, a)
        else:
            a.default_value = sock.default_value
        bb.default_value = value
        out = {o.identifier: o for o in mix.outputs}["Result_Color" if rgba else "Result_Float"]
        t.links.new(out, sock)
    toward(b.inputs["Base Color"], K.rig.srgb(SOOT), True)
    toward(b.inputs["Roughness"], SOOT_ROUGH, False)
    g = t.nodes.new("ShaderNodeMath")
    g.operation = "SUBTRACT"
    g.inputs[0].default_value = 1.0
    t.links.new(edge.outputs["Result"], g.inputs[1])
    pol = t.nodes.new("ShaderNodeMix")
    pol.data_type = "FLOAT"
    pins = {i.identifier: i for i in pol.inputs}
    t.links.new(g.outputs["Value"], pins["Factor_Float"])
    t.links.new(b.inputs["Roughness"].links[0].from_socket, pins["A_Float"])
    pins["B_Float"].default_value = GLINT_ROUGH
    t.links.new({o.identifier: o for o in pol.outputs}["Result_Float"], b.inputs["Roughness"])
    bare = t.nodes.new("ShaderNodeMix")
    bare.data_type = "RGBA"
    bins = {i.identifier: i for i in bare.inputs}
    t.links.new(g.outputs["Value"], bins["Factor_Float"])
    t.links.new(b.inputs["Base Color"].links[0].from_socket, bins["A_Color"])
    bins["B_Color"].default_value = K.rig.srgb(GLINT_METAL)
    t.links.new({o.identifier: o for o in bare.outputs}["Result_Color"], b.inputs["Base Color"])
    met = b.inputs["Metallic"]
    keep = t.nodes.new("ShaderNodeMath")
    keep.operation = "MULTIPLY_ADD"
    t.links.new(fac.outputs["Value"], keep.inputs[0])
    keep.inputs[1].default_value = -(1.0 - SOOT_METAL)
    keep.inputs[2].default_value = 1.0
    k = t.nodes.new("ShaderNodeMath")
    k.operation = "MULTIPLY"
    t.links.new(keep.outputs["Value"], k.inputs[1])
    if met.links:
        t.links.new(met.links[0].from_socket, k.inputs[0])
    else:
        k.inputs[0].default_value = met.default_value
    t.links.new(k.outputs["Value"], met)
    # nothing in the wreck glows: the light, the lamps and the glass's glint are dead
    b.inputs["Emission Strength"].default_value = 0.0
    for lk in list(b.inputs["Emission Strength"].links):
        t.links.remove(lk)
    return s_


def soot():
    """Every wreck part into its material's sooted copy. Called only after the machine's last
    render, so the copies never exist while the machine renders."""
    cache = {}
    for o in K.OBJS:
        if K.GROUP[o.name] != "wreck":
            continue
        for i, m in enumerate(o.data.materials if o.data else []):
            if m is not None and m.name != "scorch":
                if m.name not in cache:
                    cache[m.name] = sooted(m)
                o.data.materials[i] = cache[m.name]
