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
  bubble     an animation, the resource's stateless_visualisation (contract.py): a dark ball
             running round the middle of the red ring (1.25 tiles out), a quarter turn a frame
             clockwise from north, 4 frames, motion "cycle", at crude oil's animation_speed 0.2;
             rendered alone, its shadow caught on the disc and the ground. Never in a cell
  bubble-light  a glow animation over it, motion "flow": the ball's cap lit orange, the sun
             and sky off, with a small bloom, so its light falls on the disc round it

The resource's cells are rendered over the ground catcher, as a wreck is, so the studs' shadows
fall in the one sprite (onto the rings: there is nothing past the disc for them to reach).

What should come out, in sheets/meta.json: resource (4 x 3 cells, kind "resource") and
resource-effect (the same grid, kind "effect"); resource_edge_px 0 and resource-effect_edge_px 0;
resource-effect_white_px 0; resource_reach_tiles about 0.9 past every edge of the footprint
(the cyan ring's 2.4 tiles less the footprint's 1.5); bubble (4 frames, animation_speed 0.2) and
bubble-light (4 frames, kind "glow"), bubble_cycle 4 and bubble-light_white_px, _clipped_px and
_edge_px 0; and the pack exits 0.
test/test_resource.py holds the packing, preview.py, measure.py and finish.py to their docs on
these renders.
"""
import math
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
BUBBLE_FRAMES, BUBBLE_ORBIT, BUBBLE_R = 4, 1.25, 0.12
DECL = dict(
    footprint=(3, 3),
    directions="one",
    passes=[
        dict(name="resource", kind="resource", sheet="resource", stages=STAGES, variations=VARIATIONS),
        dict(name="resource-effect", kind="effect", over="resource", sheet="resource-effect",
             bloom=[[2, 0.5], [8, 0.25]]),
    ],
    animations=[
        dict(name="bubble", frames=BUBBLE_FRAMES, motion="cycle", animation_speed=0.2),
        dict(name="bubble-light", frames=BUBBLE_FRAMES, motion="flow", kind="glow", over="bubble",
             bloom=[[2, 0.5]]),
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
MELT = cyl((0, 0, 0.012), MELT_R, 0.004, GLOW)     # the melt
STUD_MAT = plain("stud", "#1E1E22", rough=0.5)
STUDS = []                          # [(stud, cap)], west to east
for k in range(VARIATIONS):
    x = (k - (VARIATIONS - 1) / 2) * STUD_DX
    STUDS.append((cyl((x, STUD_Y, STUD_H / 2), STUD_R, STUD_H, STUD_MAT),
                  cyl((x, STUD_Y, STUD_H + 0.003), STUD_R * 0.6, 0.006, GLOW)))

# the bubble: a ball and its cap, its own light (so the melt's and the caps' stay off in its frames)
BUBBLE_LIGHT = emissive("bubble-light", LIGHT)
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=BUBBLE_R, location=(0, 0, BUBBLE_R))
BALL = bpy.context.active_object
BALL.data.materials.append(STUD_MAT)
BALL.parent = ROOT
CAP = cyl((0, 0, 2 * BUBBLE_R + 0.003), BUBBLE_R * 0.5, 0.006, BUBBLE_LIGHT)

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


def bubble(f):
    """The ball in frame f: a quarter turn a frame, clockwise from north, round the red ring;
    None hides it (every cell)."""
    BALL.hide_render = CAP.hide_render = f is None
    if f is not None:
        a = 2 * math.pi * f / BUBBLE_FRAMES
        x, y = BUBBLE_ORBIT * math.sin(a), BUBBLE_ORBIT * math.cos(a)
        BALL.location = (x, y, BUBBLE_R)
        CAP.location = (x, y, 2 * BUBBLE_R + 0.003)


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
bubble(None)
for s, v in contract.cells(DECL):
    pose(s, v)
    lit(False)
    rig.render(f"{OUT_DIR}/{contract.cell('resource', s, v)}.png")
    lit(True)
    rig.render(f"{OUT_DIR}/{contract.cell('resource-effect', s, v)}.png")
# the bubble alone, over the richest stage: the disc (rings and melt) a shadow catcher under it, nothing
# else of the cell
pose(0, VARIATIONS - 1)
for o in STUDS:
    for part in o:
        part.hide_render = True
for f in range(BUBBLE_FRAMES):
    bubble(f)
    lit(False)
    for o in RING + [MELT]:
        o.is_shadow_catcher = True
    rig.render(f"{OUT_DIR}/{contract.frame('bubble', f)}.png")
    for o in RING + [MELT]:
        o.is_shadow_catcher = False
    lit(True)
    GLOW.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.0
    BUBBLE_LIGHT.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = EMISSION
    rig.render(f"{OUT_DIR}/{contract.frame('bubble-light', f)}.png")
    BUBBLE_LIGHT.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.0
