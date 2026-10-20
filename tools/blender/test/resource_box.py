"""Test model: a ground resource, for the resource pass and its effect (contract.py, pack.py).

  BLENDER=<blender> tools/blender/render.sh tools/blender/test/resource_box.py <out-dir>

Not a resource anyone ships: a target, made to be read in a screenshot. A flat disc on the
ground in rings half a tile wide, each its own colour, so what shows round a building set on it
can be read off in tiles: white to 0.5 from the centre, grey to 1.0, red to 1.5, yellow to 2.0,
cyan to 2.4. Three stages, four variations, on a 320 px canvas (five tiles) with a 3 x 3
footprint (a vent's, crude oil's +-1.4):

  stage      the disc shrinks as the resource depletes: stage 0 (the richest) has every ring,
             stage 1 none past yellow (2.0), stage 2 none past red (1.5)
  variation  v + 1 black studs in a row across the grey ring's north side, 0.3 tiles apart,
             each with a cap on top: one stud in variation 0, four in variation 3
  effect     the studs' caps and a disc of "melt" 0.3 tiles across the centre, lit orange,
             the sun and sky off (radiant.py's glow pass), with a small bloom: so in game each
             cell's light lands on its own studs only if the engine draws the effect's cell
             for the resource's (stage, variation)

The resource's cells are rendered over the ground catcher, as a wreck is, so the studs' shadows
fall in the one sprite (onto the rings: there is nothing past the disc for them to reach).

What should come out, in sheets/meta.json: resource (4 x 3 cells, kind "resource") and
resource-effect (the same grid, kind "effect"); resource_edge_px 0 and resource-effect_edge_px 0;
resource-effect_white_px 0; resource_reach_tiles about 0.9 past every edge of the footprint
(the cyan ring's 2.4 tiles less the footprint's 1.5); and the pack exits 0.
test/test_resource.py holds the packing to its docs on these renders.
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import rig  # noqa: E402
import contract  # noqa: E402
from materials import emissive  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = argv[0]
os.makedirs(OUT_DIR, exist_ok=True)

CANVAS = (320, 320)
STAGES, VARIATIONS = 3, 4
# (outer radius in tiles, colour), outermost first: each ring is a disc laid over the one before
RINGS = [(2.4, "#30A0C0"), (2.0, "#D8B020"), (1.5, "#C03030"), (1.0, "#707070"), (0.5, "#E8E8E8")]
STAGE_RADIUS = (2.4, 2.0, 1.5)      # the outermost ring each stage keeps
STUD_Y, STUD_DX, STUD_R, STUD_H = 0.75, 0.3, 0.09, 0.14
MELT_R = 0.15
LIGHT = "#FF8A30"
EMISSION = 1.5
DECL = dict(
    footprint=(3, 3),
    directions="one",
    passes=[
        dict(name="resource", kind="resource", sheet="resource", stages=STAGES, variations=VARIATIONS),
        dict(name="resource-effect", kind="effect", over="resource", sheet="resource-effect",
             bloom=[[2, 0.5], [8, 0.25]]),
    ],
)

sc = rig.reset()
sc.cycles.samples = 16
ROOT = rig.turntable(rig.stretch_root())


def plain(name, hexcol, rough=0.8):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = rig.srgb(hexcol)
    bsdf.inputs["Roughness"].default_value = rough
    return m


def cyl(loc, r, h, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=r, depth=h, location=loc)
    o = bpy.context.active_object
    o.data.materials.append(mat)
    o.parent = ROOT
    return o


# the rings: thin discs, each a hair above the one it lies on
RING = [cyl((0, 0, 0.002 + 0.001 * k), r, 0.004, plain(f"ring-{k}", col)) for k, (r, col) in enumerate(RINGS)]
GLOW = emissive("light", LIGHT)
cyl((0, 0, 0.012), MELT_R, 0.004, GLOW)     # the melt
STUD_MAT = plain("stud", "#1E1E22", rough=0.5)
STUDS = []                          # [(stud, cap)], west to east
for k in range(VARIATIONS):
    x = (k - (VARIATIONS - 1) / 2) * STUD_DX
    STUDS.append((cyl((x, STUD_Y, STUD_H / 2), STUD_R, STUD_H, STUD_MAT),
                  cyl((x, STUD_Y, STUD_H + 0.003), STUD_R * 0.6, 0.006, GLOW)))

rig.sun()
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()


def pose(stage, variation):
    """The cell's resource: the rings its stage keeps, and variation + 1 studs."""
    for (r, _), o in zip(RINGS, RING):
        o.hide_render = r > STAGE_RADIUS[stage] + 1e-6
    for k, objs in enumerate(STUDS):
        for o in objs:
            o.hide_render = k > variation


def lit(on):
    """The light: the melt and the caps' emission, and for the effect the sun, the sky, the
    catcher and the bounce floor off, so the render is the light alone."""
    GLOW.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = EMISSION if on else 0.0
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0 if on else SKY
    for o in sc.objects:
        if o.type == "LIGHT":
            o.hide_render = on
    GROUND.hide_render = on
    BOUNCE.hide_render = True       # the catcher is on for the resource's cells, as a wreck's


SKY = sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value
contract.declare(OUT_DIR, canvas=CANVAS, **DECL)
rig.camera(*CANVAS)
for s, v in contract.cells(DECL):
    pose(s, v)
    lit(False)
    rig.render(f"{OUT_DIR}/{contract.cell('resource', s, v)}.png")
    lit(True)
    rig.render(f"{OUT_DIR}/{contract.cell('resource-effect', s, v)}.png")
