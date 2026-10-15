"""Test model: a 2x2 box with a radiant window, for the animated glow layer.

  BLENDER=<blender> tools/blender/render.sh tools/blender/test/radiant_box.py <out-dir>

Not a building. The radiant solution drawn by the shared helper (tools/blender/radiant.py,
its default tuning): a glazed slot in the roof, smoked pane over the liquid with three
baffles across it, and a short glass column on the roof's south-east corner with the
rising bubbles. Four directions, eight frames:

  idle        plate: the box with the liquid stopped (dark navy, no bubbles)
  still       the same: the window's frames are working-only, so frame 0 is no part of it
  shadow      the ground catcher
  window      paint, working, flow: the window parts alone (the housing held out), the
              liquid dim and breathing, the bubbles rising
  window-glow glow over window, flow: the slot's light alone, with its bloom (3 px + 16 px),
              the sun and sky off, the housing lit only by it (the rim spill)
  column-glow glow over window too: the column's light and its bubbles, with its bloom
              (3 px + 24 px). The helper blooms per shape, one bloom a glow layer, so the two
              shapes are two layers (radiant.Radiant.groups); the column is dark in the slot's
              render and the slot in the column's, each still occluding

The canvas is 256 px for a 2 x 2 footprint: at 192 the column's 24 px tail ran into the
canvas's top edge in the south and west directions (4 in blue there); at 256 every glow
stays 28 px or more inside it (pack.py fails a glow on the edge: <glow>_edge_px; cropped to
the middle 192 px, these renders fail it for column-glow south and west).

What should come out, in sheets/meta.json, in every direction, for window-glow and for
column-glow: <glow>_white_px 0, <glow>_clipped_px 0 (counted with both glows added),
<glow>_frames [8, 8], <glow>_edge_px 0, and the pack exits 0. <glow>_light is reported, not
checked: on 2026-10-15 (the helper's per-shape defaults, blender.org 5.0.1 on the GPU)
window-glow peak 152-155, core 8.4-9.2 %, halo 75.8-76.4 %; column-glow peak 92-97, core
5.8-7.9 %, halo 79.8-83.2 % -- a small column and a glazed slot with no coping or grate,
frame 0 (the study's pieces are the measure of the tuning). A glow frame whitened by hand
(an 8 x 8 px white square in window-glow-03-north, or in column-glow-05-south) fails the
pack: 64 px white in that glow, 64 px driven to white in both, exit 1.
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import rig  # noqa: E402
import contract  # noqa: E402
import radiant  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = argv[0]
os.makedirs(OUT_DIR, exist_ok=True)

CANVAS = (256, 256)      # room round the windows for the column's 24 px tail (radiant.BLOOM)
FRAMES = 8
R = radiant.Radiant()
# one glow layer per bloom: the slot's (3 px + 16 px) and the column's (3 px + 24 px)
GLOWS = [("window-glow" if "slot" in g else "column-glow", g) for g in R.groups(("slot", "column"))]
DECL = dict(
    footprint=(2, 2),
    directions="four",
    passes=[
        dict(name="idle", kind="plate", sheet="base"),
        dict(name="still", kind="still"),
        dict(name="shadow", kind="shadow", sheet="shadow"),
    ],
    animations=[R.window_animation("window", FRAMES)] + [R.glow_animation(name, "window", FRAMES, shapes)
                                                         for name, shapes in GLOWS],
    ports=[],
)

sc = rig.reset()
sc.cycles.samples = 16
ROOT = rig.turntable(rig.stretch_root())


def plain(name, hexcol, metallic=0.0, rough=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = rig.srgb(hexcol)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    return m


M = {
    "body": plain("body", "#5A5248"),
    "steel": plain("steel", "#8A857C", metallic=0.9, rough=0.3),
    "internal": plain("internal", "#1A1C22", metallic=0.6, rough=0.45),
    "pane": R.glass("pane", pane=True),
    "glass": R.glass("glass"),
}
PARTS = {}


def part(obj, mat, group):
    obj.data.materials.append(M[mat] if isinstance(mat, str) else mat)
    obj.parent = ROOT
    PARTS.setdefault(group, []).append(obj)
    return obj


def box(loc, size, mat, group="housing"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return part(o, mat, group)


def cyl(loc, r, h, mat, group="housing"):
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=r, depth=h, location=loc)
    o = bpy.context.active_object
    for p in o.data.polygons:
        # the round side smooth, the caps flat: a smoothed cap shades as a dome and throws a
        # white glint, which the column's bloom then drives to white
        p.use_smooth = abs(p.normal.z) < 0.5
    return part(o, mat, group)


# the body: a plinth to the footprint's edge and a block on it, as box.py's
E, PLINTH, B, TOP = 0.995, 0.08, 0.8, 0.6
box((0, 0, PLINTH / 2), (2 * E, 2 * E, PLINTH), "body")
box((0, 0, TOP / 2), (2 * B, 2 * B, TOP), "body")

# the slot: the liquid sunk in the roof under a smoked pane, coping round it, baffles across
HL, HW, ZT = 0.5, 0.12, TOP + 0.005
for dy in (-1, 1):
    box((-0.15, dy * (HW + 0.05), ZT + 0.03), (2 * HL + 0.2, 0.1, 0.06), "steel")
for dx in (-1, 1):
    box((-0.15 + dx * (HL + 0.05), 0, ZT + 0.03), (0.1, 2 * HW + 0.2, 0.06), "steel")
slot = box((-0.15, 0, ZT + 0.005), (2 * HL, 2 * HW, 0.02), R.liquid("slot-liquid", "slot", (HL, HW)), "window")
R.lit(slot)
for k in range(3):
    box((-0.15 - HL + (k + 1) * 2 * HL / 4, 0, ZT + 0.025), (0.025, 2 * HW, 0.02), "internal", "window")
box((-0.15, 0, ZT + 0.045), (2 * HL, 2 * HW, 0.01), "pane", "window")

# the column: glass round the liquid, flanged at both ends, bubbles rising in its front
CX, CY, LR, Z0, Z1 = 0.5, -0.45, 0.16, TOP + 0.05, TOP + 0.75
cyl((CX, CY, Z0 - 0.025), LR + 0.05, 0.05, "steel")
cyl((CX, CY, Z1 + 0.025), LR + 0.05, 0.05, "steel")
cyl((CX, CY, (Z0 + Z1) / 2), LR, Z1 - Z0, "glass", "window")
RL = LR - 0.03
column = cyl((CX, CY, (Z0 + Z1) / 2), RL, Z1 - Z0 - 0.01,
             R.liquid("column-liquid", "column", (RL, (Z1 - Z0) / 2)), "window")
R.lit(column)
cyl((CX, CY, (Z0 + Z1) / 2), 0.03, Z1 - Z0 - 0.01, "internal", "window")          # a heater rod
PARTS["bubbles"] = R.column_bubbles((CX, CY), RL, (Z0 + 0.04, Z1 - 0.04), parent=ROOT)

rig.sun()
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()


def setup(visible=(), holdouts=(), ground=False, camera=True):
    for g, objs in PARTS.items():
        for o in objs:
            o.hide_render = g not in visible and g not in holdouts
            o.is_holdout = g in holdouts
            o.visible_camera = camera
    GROUND.hide_render = not ground
    BOUNCE.hide_render = ground


contract.declare(OUT_DIR, canvas=CANVAS, **DECL)
rig.camera(*CANVAS)

for d in contract.each_direction(ROOT, DECL["directions"]):
    def path(stem, d=d):
        return f"{OUT_DIR}/{contract.named(stem, d)}.png"
    R.pose(0.0, "idle")
    setup(visible=("housing", "window"))
    rig.render(path("idle"))
    rig.render(path("still"))
    setup(visible=("housing", "window"), ground=True, camera=False)
    rig.render(path("shadow"))
    for f in range(FRAMES):
        t = f / FRAMES
        R.pose(t, "plate")
        setup(visible=("window", "bubbles"), holdouts=("housing",))
        rig.render(path(contract.frame("window", f)))
        setup(visible=("housing", "window", "bubbles"))
        for name, shapes in GLOWS:
            R.pose(t, "glow", shapes)
            with R.glow_pass(hide=(GROUND, BOUNCE)):
                rig.render(path(contract.frame(name, f)))
