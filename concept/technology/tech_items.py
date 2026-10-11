"""The item technologies' icons: Cryogen, Fluorinated holmium, Superconducting winding.

Each is its product, modelled for the new pipeline in the form its current 64 px
icon has (graphics/icons/fluid/cold-cryogen.png, fluorinated-holmium.png,
superconducting-winding.png) -- the form kept, the art redone:

  sae-fa-cryogen                  cold cryogen: a pool of deep, icy blue liquid,
                                  glossy, its rim frosted white
  sae-fa-fluorinated-holmium      a square plate on its diagonal, holmium's pink
                                  under a violet crystalline fluoride crust
  sae-fa-superconducting-winding  a toroidal coil, close-wound pale blue
                                  conductor, its lead trailing off

Rendered at 256/128/64/32 by tools/blender/tech_rig.py (40 deg camera, the
buildings' sun and fill, a shadow catcher, framed to 226 of 256 px):

    BLENDER=/usr/bin/blender tools/blender/render-icons.sh \\
        concept/technology/tech_items.py <out-dir>

Round 2 (first GPU renders): the pool domed higher and its frost finer and denser,
the plate thicker.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
sys.path.insert(0, os.path.join(REPO, "concept", "items"))

import rig  # noqa: E402
import tech_rig  # noqa: E402
from icon_kit import add_glow, glossy, link, obj_coords  # noqa: E402
from materials import _G, layered  # noqa: E402

CRYO = ("#0A2E8C", "#3C8CFF")          # the liquid deep to its lit surface (the current icon's blues)
FROST = "#DCEBFF"
HOLMIUM = ("#B07890", "#D8A8C0")       # holmium plate's pink (Space Age's holmium-plate)
FLUORIDE = ("#6A4CA8", "#A890D8")      # the violet crust
WIRE = ("#5C86C8", "#A8C8F0")          # the conductor, pale blue


def cryogen():
    """A low pool: a flattened lens of liquid in a ring of frost crystals."""
    liquid = glossy("cryo", CRYO[0], rough=0.05, coat=1.0, coat_rough=0.03, rim=("#04103A", 0.8))
    add_glow(liquid, lambda g: g.remap(g.node("ShaderNodeLayerWeight", Blend=0.4).outputs["Facing"], 0.5, 0.0, 0.0, 0.6),
             CRYO, 0.6)
    bm = bmesh.new()
    seg, R = 96, 1.0
    rings = []
    for k, (rr, z) in enumerate(((1.0, 0.0), (1.0, 0.06), (0.9, 0.16), (0.55, 0.24), (0.0, 0.26))):
        ring = []
        for i in range(seg if rr else 1):
            a = 2 * math.pi * i / seg
            j = 1 + 0.05 * noise.noise(Vector((math.cos(a), math.sin(a), 0)) * 2.2)
            ring.append(bm.verts.new((rr * j * math.cos(a), rr * j * math.sin(a) * 0.8, z)))
        rings.append(ring)
    for lo, hi in zip(rings, rings[1:]):
        for i in range(seg):
            n = (i + 1) % seg
            if len(hi) == 1:
                bm.faces.new((lo[i], lo[n], hi[0]))
            else:
                bm.faces.new((lo[i], lo[n], hi[n], hi[i]))
    bm.faces.new(list(reversed(rings[0])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    pool = link(bm, "cryogen", (liquid,), smooth=True)
    # the frost: small sharp crystals around the rim
    frost = glossy("frost", FROST, rough=0.35, coat=0.3)
    rng = random.Random(4)
    bm = bmesh.new()
    for i in range(130):
        a = 2 * math.pi * i / 130 + rng.uniform(-0.02, 0.02)
        r = 1.0 + rng.uniform(-0.05, 0.06)
        c = Vector((r * math.cos(a), r * math.sin(a) * 0.8, 0.06))
        pts = [c + Vector((rng.gauss(0, 1), rng.gauss(0, 1), abs(rng.gauss(0, 1.6)))) * 0.045 * 0.75 for _ in range(6)]
        vs = [bm.verts.new(p) for p in pts + [c]]
        bmesh.ops.convex_hull(bm, input=vs)
    ice = link(bm, "frost", (frost,), smooth=False)
    return [pool, ice]


def fluorinated_holmium():
    """A plate on its diagonal (as iron plate's icon is): holmium's pink in its edges,
    a violet crystalline crust across its top."""
    def crust(g):
        # crystals: each Voronoi cell its own shade between the crust's two violets,
        # its edges a darker line (round 3's soft blend read as marble)
        p = obj_coords(g)
        vor = g.node("ShaderNodeTexVoronoi", Vector=p, Scale=11.0)
        cell = g.node("ShaderNodeSeparateColor", Color=vor.outputs["Color"]).outputs[0]
        col = g.mixc(cell, FLUOR(0), FLUOR(1))
        edge = g.node("ShaderNodeTexVoronoi", Vector=p, Scale=11.0)
        edge.feature = "DISTANCE_TO_EDGE"
        return g.mixc(g.remap(edge.outputs["Distance"], 0.03, 0.0), col, rig.srgb("#3A2A60"))

    def FLUOR(i):
        return rig.srgb(FLUORIDE[i])
    top = layered("fluoride", FLUORIDE[0], metal=FLUORIDE[1], paint_metal=0.2, paint_rough=0.3, wear=0.2,
                  rust=0.0, dust=0.0, grime=0.3, jitter=0.05, pattern=crust)
    base = layered("holmium", HOLMIUM[0], metal=HOLMIUM[1], paint_metal=0.7, paint_rough=0.3, wear=0.5,
                   rust=0.0, dust=0.0, grime=0.4, jitter=0.05)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.z = (v.co.z + 0.5) * 0.16
    for f in bm.faces:
        f.material_index = 0 if f.normal.z > 0.9 else 1
    ob = link(bm, "plate", (top, base), smooth=False)
    bev = ob.modifiers.new("bevel", "BEVEL")
    bev.width, bev.segments, bev.limit_method = 0.02, 2, "ANGLE"
    ob.rotation_euler = (0, 0, math.radians(45))
    return [ob]


def superconducting_winding():
    """A torus close-wound with conductor: a ribbed torus, and a lead leaving it."""
    wire = layered("winding", WIRE[0], metal=WIRE[1], paint_metal=0.6, paint_rough=0.3, wear=0.3,
                   rust=0.0, dust=0.0, grime=0.35, jitter=0.04)
    R, r, turns = 0.62, 0.3, 64
    bm = bmesh.new()
    seg_u, seg_v = 256, 32
    grid = []
    for i in range(seg_u):
        u = 2 * math.pi * i / seg_u
        rib = 1 + 0.05 * abs(math.sin(turns * u / 2))       # the turns, as ribs
        row = []
        for j in range(seg_v):
            v = 2 * math.pi * j / seg_v
            rr = r * rib
            row.append(bm.verts.new(((R + rr * math.cos(v)) * math.cos(u), (R + rr * math.cos(v)) * math.sin(u),
                                     rr * math.sin(v) + r)))
        grid.append(row)
    for i in range(seg_u):
        for j in range(seg_v):
            a, b = grid[i][j], grid[(i + 1) % seg_u][j]
            c, d = grid[(i + 1) % seg_u][(j + 1) % seg_v], grid[i][(j + 1) % seg_v]
            bm.faces.new((a, b, c, d))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    coil = link(bm, "coil", (wire,), smooth=True)
    cu = bpy.data.curves.new("lead", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.022
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(2)
    for bp, co in zip(sp.bezier_points, ((R + r, -0.1, r), (R + r + 0.25, -0.45, 0.1), (R + 0.2, -0.95, 0.0))):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    lead = bpy.data.objects.new("lead", cu)
    lead.data.materials.append(wire)
    bpy.context.scene.collection.objects.link(lead)
    return [coil, lead]


ITEMS = {"sae-fa-cryogen": cryogen, "sae-fa-fluorinated-holmium": fluorinated_holmium,
         "sae-fa-superconducting-winding": superconducting_winding}

tech_rig.main(ITEMS)
