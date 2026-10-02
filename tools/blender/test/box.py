"""Test model: a 2x2 box that exercises every path through the render pipeline.

  BLENDER=<blender> tools/blender/render.sh tools/blender/test/box.py <out-dir> --ports --icon

Not a building. Four directions, so every pass is rendered per direction by
turning the root (<pass>-<direction>.png); a 4-frame part sliding in a straight
line on a curve that accelerates, so the declared-path check runs instead of
the turning drift; every
pass kind (plate, still, glow, shadow, light); two ports, off the middle of
their faces, on a canvas of their own size; and an icon.

What should come out, in sheets/meta.json and sheets/ports/meta.json:
  * half_width_tiles 1.0 and footprint_rows_tiles 1.0 in every direction, with
    centre_offset_px 0 and edge_alpha_max 0: the plinth's walls stand at 0.995
    tiles, so the outermost pixel row and column are partly covered and the
    plate measures exactly two tiles;
  * slider_path_px: the slider's position in each frame, 0, 4, 12 and 28 px
    along its line as declared (steps of 4, 8 and 16), measured off the curve
    and off the line by under 1 px;
  * port-N and cover-N shifted from tile (-0.5, -1.5), port-E and cover-E from
    (1.5, 0.5): the tiles those ports point into.
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
PORTS = "--ports" in argv
ICON = "--icon" in argv

CANVAS = (192, 192)
PORT_CANVAS = (256, 256)
# the slider's stroke, tiles east of where it starts: it accelerates (4, 8, then 16 px a
# frame), so a constant-speed check would fail it and only the declared curve passes it
STROKE = (0.0, 0.0625, 0.1875, 0.4375)
DECL = dict(
    footprint=(2, 2),
    directions="four",
    passes=[
        dict(name="idle", kind="plate", sheet="base"),
        dict(name="still", kind="still"),
        dict(name="working", kind="glow", over="idle", sheet="glow"),
        dict(name="shadow", kind="shadow", sheet="shadow"),
        dict(name="lamp", kind="light", sheet="lamp"),
    ],
    animations=[dict(name="slider", frames=len(STROKE), motion="slide", path=[(x, 0, 0) for x in STROKE])],
    ports=[dict(tile=(-0.5, -0.5), face="N"), dict(tile=(0.5, 0.5), face="E")],
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
    "marker": plain("marker", "#B8962E"),
    "slider": plain("slider", "#94592C", metallic=0.8, rough=0.4),
    "steel": plain("steel", "#8A857C", metallic=0.9, rough=0.3),
    "cap": plain("cap", "#36363C", metallic=0.5, rough=0.7),
    "window": emissive("window", "#A8E8C0"),
    "lens": emissive("lens", "#FFFFFF"),
}
PARTS = {}


def part(obj, mat, group):
    obj.data.materials.append(M[mat])
    obj.parent = ROOT
    PARTS.setdefault(group, []).append(obj)
    return obj


def box(loc, size, mat, group="static"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return part(o, mat, group)


def cyl(loc, r, h, mat, group, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=r, depth=h, location=loc, rotation=rot)
    return part(bpy.context.active_object, mat, group)


# the body: a plinth with its walls at 0.995, so the plate is exactly the 2x2
# footprint, and a block on it set back to 0.8, leaving room for the fittings
E, PLINTH, B, TOP = 0.995, 0.08, 0.8, 0.6
box((0, 0, PLINTH / 2), (2 * E, 2 * E, PLINTH), "body")
box((0, 0, TOP / 2), (2 * B, 2 * B, TOP), "body")
# a flat stripe along the north edge of the roof: which way it faces, casting nothing
box((0, 0.65, TOP + 0.005), (1.4, 0.16, 0.01), "marker")
# a lit window on the west of the roof, and a lamp on a post in its north-east corner
box((-0.6, -0.1, TOP + 0.005), (0.16, 0.9, 0.01), "window", "window")
cyl((0.6, 0.5, TOP + 0.08), 0.02, 0.16, "steel", "static")
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0.6, 0.5, TOP + 0.2), segments=16, ring_count=8)
part(bpy.context.active_object, "lens", "lamp")
# the slider: a block that runs east along the roof, STROKE
SLIDER0 = (-0.35, -0.35, TOP + 0.075)
box(SLIDER0, (0.2, 0.2, 0.15), "slider", "slider")

STATIC = ("static", "window", "lamp")
rig.sun()
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()


def setup(visible=(), catchers=(), holdouts=(), ground=False):
    for g, objs in PARTS.items():
        for o in objs:
            o.hide_render = g not in visible and g not in catchers and g not in holdouts
            o.is_shadow_catcher = g in catchers
            o.is_holdout = g in holdouts
            o.visible_camera = True
    GROUND.hide_render = not ground
    BOUNCE.hide_render = ground


def light(mat, strength, base=None):
    bsdf = M[mat].node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Emission Strength"].default_value = strength
    if base:
        bsdf.inputs["Base Color"].default_value = base


def port(face, tile):
    """A stub from the block to a flange at the boundary on `tile`, and a cap just past it."""
    ax = contract.FACES[face]
    out = (ax[0], -ax[1])                         # contract y runs down the screen; Blender's runs north
    along = (tile[0], -tile[1])
    rot = (math.pi / 2, 0, 0) if out[0] == 0 else (0, math.pi / 2, 0)

    def at(t):
        # t: distance out from the entity centre, on the port's tile
        return (along[0] if out[0] == 0 else out[0] * t,
                along[1] if out[1] == 0 else out[1] * t, 0.3)
    cyl(at((B + 1.0) / 2), 0.14, 1.0 - B, "steel", f"port-{face}", rot)
    cyl(at(0.98), 0.2, 0.04, "steel", f"port-{face}", rot)
    cyl(at(1.03), 0.22, 0.06, "cap", f"cover-{face}", rot)
    cyl(at(1.08), 0.08, 0.04, "steel", f"cover-{face}", rot)


if PORTS:
    contract.declare(OUT_DIR, canvas=PORT_CANVAS, **DECL)
    for p in DECL["ports"]:
        port(p["face"], p["tile"])
    rig.camera(*PORT_CANVAS)
    body = STATIC + ("slider",)
    for p in DECL["ports"]:
        d = p["face"]
        catch = () if d == "N" else body          # north is drawn behind the building
        setup(visible=(f"port-{d}",), catchers=catch)
        rig.render(f"{OUT_DIR}/port-{d}.png")
        setup(visible=(f"cover-{d}",), catchers=catch + (f"port-{d}",))
        rig.render(f"{OUT_DIR}/cover-{d}.png")
    sys.exit(0)

if ICON:
    rig.camera(1024, 1024, ss=1).data.ortho_scale = 2.6
    setup(visible=STATIC + ("slider",))
    light("window", 1.2)
    rig.render(f"{OUT_DIR}/icon.png")
    sys.exit(0)

contract.declare(OUT_DIR, canvas=CANVAS, **DECL)
rig.camera(*CANVAS)
SLIDER = PARTS["slider"][0]
LENS_BASE = tuple(M["lens"].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value)

for d in contract.each_direction(ROOT, DECL["directions"]):
    def path(stem, d=d):
        return f"{OUT_DIR}/{contract.named(stem, d)}.png"
    SLIDER.location = SLIDER0
    setup(visible=STATIC)
    rig.render(path("idle"))
    setup(visible=STATIC + ("slider",))
    rig.render(path("still"))
    setup(visible=STATIC)
    light("window", 1.2)
    rig.render(path("working"))
    light("window", 0.0)
    setup(visible=STATIC + ("slider",), ground=True)
    for objs in PARTS.values():
        for o in objs:
            o.visible_camera = False
    rig.render(path("shadow"))
    setup(visible=("lamp",), holdouts=("static", "window", "slider"))
    light("lens", 1.0, (0.9, 0.9, 0.9, 1))
    rig.render(path("lamp"))
    light("lens", 0.0, LENS_BASE)
    setup(visible=("slider",), catchers=STATIC)
    for f, (dx, dy, dz) in enumerate(DECL["animations"][0]["path"]):
        SLIDER.location = (SLIDER0[0] + dx, SLIDER0[1] + dy, SLIDER0[2] + dz)
        rig.render(path(contract.frame("slider", f)))
