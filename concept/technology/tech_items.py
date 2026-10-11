"""The item technologies' icons: Cryogen, Fluorinated holmium, Superconducting winding.

Each is its product, modelled for the new pipeline, and arranged as Space Age
arranges its product technologies (holmium processing's fanned plates, lithium's
disc with its rocks, tungsten carbide's heap of shards): a group or an angled
object that fills the square, never a flat sliver.

  sae-fa-cryogen                  cold cryogen in a dewar: a squat steel vessel
                                  brimming with pale icy blue, frost crusting its
                                  rim and creeping down its wall
  sae-fa-fluorinated-holmium      three plates fanned on one another, holmium's
                                  pink in their edges under a violet crystalline
                                  fluoride crust
  sae-fa-superconducting-winding  a toroidal coil of close-wound pale blue
                                  conductor, stood up toward the eye, its lead
                                  trailing off

Rendered at 256/128/64/32 by tools/blender/tech_rig.py (40 deg camera, the
buildings' sun and fill, a shadow catcher):

    BLENDER=... tools/blender/render-icons.sh concept/technology/tech_items.py <out-dir>

With ITEM_ICONS=1 in the environment the same builds go through icon_rig.py
instead, as 64 px item icons (cold-cryogen, fluorinated-holmium,
superconducting-winding), for comparison with the current ones.

Round 2 (first GPU renders): the pool domed higher, its frost finer, the plate
thicker. Round 3 (Liam): share 0.30-0.38 against Space Age's 0.37-0.71 -- the
pool became a dewar, the plate three plates, the coil stood up; the cryogen less
saturated, its frost under p95 236.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Euler, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
sys.path.insert(0, os.path.join(REPO, "concept", "items"))

import rig  # noqa: E402
from icon_kit import add_glow, glossy, lathe, lift, link, obj_coords  # noqa: E402
from materials import _G, layered  # noqa: E402

CRYO = ("#2E5C98", "#9CC4E8")          # the liquid deep to its lit surface: icy, not saturated
FROST = "#A4B8CA"                      # frost a pale blue-grey: white frost clipped (round 2: p95 254)
STEEL = ("#6E747C", "#A8AEB6")
HOLMIUM = ("#B07890", "#D8A8C0")       # holmium plate's pink (Space Age's holmium-plate)
FLUORIDE = ("#6A4CA8", "#A890D8")      # the violet crust
WIRE = ("#5C86C8", "#A8C8F0")          # the conductor, pale blue


def cryogen():
    """A dewar: a squat, double-walled steel vessel brimming with cryogen, frost on its
    lip and down its wall."""
    steel = layered("dewar", STEEL[0], metal=STEEL[1], paint_metal=0.6, paint_rough=0.35, wear=0.4,
                    rust=0.02, dust=0.0, grime=0.4, jitter=0.04)

    def frosted(g):
        # frost creeping down from the lip, ragged at its lower edge
        p = obj_coords(g)
        z = g.node("ShaderNodeSeparateXYZ", Vector=p).outputs["Z"]
        n = g.noise(p, 7.0, detail=4)
        return g.math("MULTIPLY", g.remap(g.math("ADD", z, g.math("MULTIPLY", n, 0.25)), 0.55, 0.75), 1.0, clamp=True)
    g = _G(steel)
    bsdf = g.n["Principled BSDF"]
    base = bsdf.inputs["Base Color"].links[0].from_socket
    m = frosted(g)
    g.l.new(g.mixc(m, base, rig.srgb(FROST)), bsdf.inputs["Base Color"])
    rough = bsdf.inputs["Roughness"].links[0].from_socket
    g.l.new(g.mixf(m, rough, 0.75), bsdf.inputs["Roughness"])
    prof = [(0.0, 0.0), (0.46, 0.0), (0.52, 0.03), (0.55, 0.08), (0.58, 0.62), (0.63, 0.66), (0.64, 0.71),
            (0.6, 0.74), (0.54, 0.73), (0.51, 0.68), (0.49, 0.12), (0.0, 0.12)]
    vessel = lathe("dewar", prof, (steel,), segments=96)
    liquid = glossy("cryo", CRYO[0], rough=0.08, coat=1.0, coat_rough=0.05, rim=("#0E2448", 0.7))
    add_glow(liquid, lambda g: g.remap(g.node("ShaderNodeLayerWeight", Blend=0.4).outputs["Facing"], 0.6, 0.0, 0.0, 0.5),
             CRYO, 0.35)
    surf = lathe("cryogen", [(0.0, 0.0), (0.5, 0.0), (0.505, -0.01)], (liquid,), segments=96)
    surf.location.z = 0.69
    frost = glossy("frost", FROST, rough=0.5, coat=0.2)
    rng = random.Random(4)
    bm = bmesh.new()
    for i in range(110):
        a = 2 * math.pi * i / 110 + rng.uniform(-0.02, 0.02)
        r = 0.6 + rng.uniform(-0.05, 0.05)
        c = Vector((r * math.cos(a), r * math.sin(a), 0.73))
        pts = [c + Vector((rng.gauss(0, 1), rng.gauss(0, 1), abs(rng.gauss(0, 1.4)))) * 0.026 for _ in range(6)]
        vs = [bm.verts.new(p) for p in pts + [c]]
        bmesh.ops.convex_hull(bm, input=vs)
    ice = link(bm, "frost", (frost,), smooth=False)
    return lift([vessel, surf, ice])


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
    def plate(name, loc, rz, tilt=(0.0, 0.0)):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.z = (v.co.z + 0.5) * 0.14
        for f in bm.faces:
            f.material_index = 0 if f.normal.z > 0.9 else 1
        ob = link(bm, name, (top, base), smooth=False)
        bev = ob.modifiers.new("bevel", "BEVEL")
        bev.width, bev.segments, bev.limit_method = 0.02, 2, "ANGLE"
        ob.location = loc
        ob.rotation_euler = (tilt[0], tilt[1], math.radians(rz))
        return ob
    # three, fanned as holmium processing's are: each laid on the one below, turned
    obs = [plate("plate_a", (0.0, 0.0, 0.0), 40),
           plate("plate_b", (0.26, 0.30, 0.15), 58, (math.radians(-6), math.radians(4))),
           plate("plate_c", (-0.22, 0.36, 0.29), 22, (math.radians(5), math.radians(-5)))]
    return lift(obs)


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
    # stood up toward the eye on a small rest of its own lead: the ring reads round,
    # not as a flat band (round 2's share 0.38)
    root = bpy.data.objects.new("winding", None)
    bpy.context.scene.collection.objects.link(root)
    for o in (coil, lead):
        o.parent = root
    root.rotation_euler = (math.radians(42), 0, math.radians(-12))   # its face tipped up to the camera
    bpy.context.view_layer.update()
    zmin = min((o.matrix_world @ Vector(c)).z for o in (coil,) for c in o.bound_box)
    root.location.z -= zmin
    return [coil, lead]


ITEMS = {"sae-fa-cryogen": cryogen, "sae-fa-fluorinated-holmium": fluorinated_holmium,
         "sae-fa-superconducting-winding": superconducting_winding}

if os.environ.get("ITEM_ICONS"):
    import icon_rig
    names = {"sae-fa-cryogen": "cold-cryogen", "sae-fa-fluorinated-holmium": "fluorinated-holmium",
             "sae-fa-superconducting-winding": "superconducting-winding"}
    # kamacite's per-size rules (concept/items/kamacite/kamacite_icons.py)
    rules = {64: {"alpha": [16, 245], "rim": [0.7, 36]},
             32: {"sharpen": [0.6, 50], "alpha": [20, 235], "rim": [0.7, 38]},
             16: {"contrast": 1.25, "sharpen": [0.5, 90], "alpha": [48, 208], "rim": [0.8, 40]},
             8: {"contrast": 1.35, "sharpen": [0.5, 80], "alpha": [72, 184], "rim": [0.9, 44]}}
    icon_rig.main({names[k]: (lambda f, size, b=b: b()) for k, b in ITEMS.items()}, ("tech-model",),
                  {n: rules for n in names.values()})
else:
    import tech_rig
    tech_rig.main(ITEMS)
