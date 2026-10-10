"""Item icon rig: the buildings' sun and colour management, an item's camera.

An item icon is a small Blender script (concept/items/<family>/...) that builds
its object with materials.layered and hands it to this rig, once per mip size:
vanilla's icons are made at 64 px first and every smaller size is then fixed by
hand (FFF #348), so here every size is its own render, at SS x its size, of a
build the script may simplify for that size (fewer, larger pieces; thicker
edges; small details dropped). icon_post.py brings the renders down and applies
the per-size image rules the script declares; key-icons.py --mips packs them.

Calibration, measured off vanilla's item icons rather than assumed:
  ELEVATION  iron-plate.png and copper-plate.png are squares turned on the
             diagonal; their top faces are 61-62 px across and 42-44 px tall
             (less the plate's ~4 px edge), so sin(elev) = 0.69-0.71 -> 45 deg.
             The buildings' camera (rig.py, 60 deg) is steeper: an item is held
             up to the eye, a building is seen from the player's height.
  LIGHT      the buildings' sun and world fill (rig.sun, rig.reset), unchanged,
             so an item is lit as the world is. Vanilla's items show no rim or
             fill light beyond that and no contact shadow: their alpha is the
             object alone (iron-plate's 173 part-transparent pixels are its
             anti-aliased outline). So: no shadow catcher, film transparent.
             The invisible bounce floor (rig.bounce_ground) stays: it is the
             world's warm underside light, not a shadow.
  FRAMING    vanilla's analogues fill their canvas edge to edge (bounding boxes
             62-64 px of 64); ours keep MARGIN px clear on every side at every
             size, so nothing touches the canvas edge, and the long side of the
             object's projection fills the rest. The fit is computed from the
             evaluated mesh, per size, so a build that changes with size is
             framed for itself.

Run by tools/blender/render-icons.sh, which calls the item script as
    blender -b --python <script> -- <out-dir> [--only item[,item]]
The script calls icon_rig.main(ITEMS, FINISHES, POST); see main().
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

import rig

ELEVATION = math.radians(45.0)
SIZES = (64, 32, 16, 8)
SS = 4
MARGIN = 1                     # px clear of the canvas edge, at every size
# and a little more inside it: the 4x render's anti-aliased rim, brought down by
# Lanczos, spreads past the mesh (first trial: 64 px renders framed to exactly 62 px
# came out 63-64 px wide with the alpha cut at 6); with the 64's alpha cut at 16 a
# quarter pixel is enough, and at 8 there is no pixel to spare
PAD = {64: 0.25, 32: 0.25, 16: 0.25, 8: 0.0}
SAMPLES = {64: 96, 32: 96, 16: 128, 8: 128}   # small renders are cheap; more samples, less noise per px


def scene(size):
    """An empty scene with the buildings' light and an item camera for size px."""
    sc = rig.reset()
    sc.cycles.samples = SAMPLES.get(size, 96)
    rig.sun()
    rig.bounce_ground()
    sc.render.resolution_x = sc.render.resolution_y = size * SS
    sc.render.resolution_percentage = 100
    cam_data = bpy.data.cameras.new("icon_cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 1.0
    cam_data.clip_start, cam_data.clip_end = 0.1, 200
    cam = bpy.data.objects.new("icon_cam", cam_data)
    sc.collection.objects.link(cam)
    tilt = math.pi / 2 - ELEVATION
    cam.rotation_euler = (tilt, 0, 0)
    d = 50.0
    cam.location = (0, -d * math.sin(tilt), d * math.cos(tilt))
    sc.camera = cam
    return sc, cam


def _projected(cam, objs):
    """Camera-space x, y of every evaluated vertex of objs."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    inv = cam.matrix_world.inverted()
    xs, ys = [], []
    for o in objs:
        if o.type not in ("MESH", "CURVE"):
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ev.matrix_world
        for v in me.vertices:
            p = inv @ (mw @ v.co)
            xs.append(p.x)
            ys.append(p.y)
        ev.to_mesh_clear()
    return xs, ys


def frame(cam, objs, size, margin=MARGIN):
    """Fit objs' projection into size px less margin (+ PAD) px a side, centred."""
    xs, ys = _projected(cam, objs)
    if not xs:
        raise SystemExit("icon_rig.frame: nothing to frame")
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    fill = (size - 2 * (margin + PAD.get(size, 0.0))) / size
    scale = max(w, h) / fill
    cam.data.ortho_scale = scale
    cam.data.shift_x = (max(xs) + min(xs)) / 2 / scale
    cam.data.shift_y = (max(ys) + min(ys)) / 2 / scale
    return {"ortho_scale": scale, "w": w / scale * size, "h": h / scale * size}


def _args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = argv[0]
    only = None
    if "--only" in argv:
        only = set(argv[argv.index("--only") + 1].split(","))
    return out, only


def main(items, finishes, post):
    """Render every item in every finish at every size.

    items:    {name: build(finish, size) -> [objects]}; build is called on an empty,
              lit scene and may change what it builds with size (the hand-finishing
              done by rule: fewer, larger pieces, heavier edges, details dropped).
    finishes: names, e.g. ("signature", "neutral"); each build receives one.
    post:     {name: {size: {...}}} -- image rules icon_post.py applies per size
              (see its header); written to <out>/icons.json beside the renders.
    Writes <out>/<item>/<finish>/<size>.png at SS x size, and <out>/icons.json.
    """
    out, only = _args()
    os.makedirs(out, exist_ok=True)
    framing = {}
    for name, build in items.items():
        if only and name not in only:
            continue
        for fin in finishes:
            for size in SIZES:
                sc, cam = scene(size)
                objs = build(fin, size)
                fr = frame(cam, objs, size)
                d = os.path.join(out, name, fin)
                os.makedirs(d, exist_ok=True)
                rig.render(os.path.join(d, f"{size}.png"))
                framing[f"{name}/{fin}/{size}"] = fr
                print(f"icon {name} {fin} {size}: {fr['w']:.1f} x {fr['h']:.1f} px", flush=True)
    decl = {"sizes": list(SIZES), "ss": SS, "margin": MARGIN, "finishes": list(finishes),
            "items": [n for n in items if not only or n in only],
            "post": {n: {str(s): r for s, r in rules.items()} for n, rules in post.items()},
            "framing": framing, "elevation_deg": math.degrees(ELEVATION)}
    with open(os.path.join(out, "icons.json"), "w") as f:
        json.dump(decl, f, indent=1)
