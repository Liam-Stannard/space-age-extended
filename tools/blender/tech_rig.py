"""Technology icon rig: a 256 px icon and its mips, rendered per size like an item's.

Vanilla ships a technology icon as a 480x256 strip (256/128/64/32), as it ships a
64 px item icon as 120x64; key-icons.py --mips packs either from per-size renders
(the base size is read off the first level). icon_post.py finishes the levels
by the rules the script declares, as it does an item's.

Calibration, measured off Space Age's technology icons (space-age/graphics/
technology; the numbers are in the review sheet's measures.json):
  BACKGROUND none: every one is cut out on transparency.
  SHADOW     a soft contact shadow, dark and part-transparent, lies on the ground
             to the lower right of buildings and items alike (1000-3800 dark
             part-transparent pixels of 65536; foundry, cryogenic plant, fusion
             reactor, lithium processing): a shadow catcher under the sun.
  FRAMING    buildings fill the square: opaque bounding boxes 207-251 px on the
             long side (foundry 242, cryogenic plant 246, EM plant 248, big
             mining drill 243); products a little less (tungsten carbide 210,
             holmium plates 213, lithium 233, carbon fibre 212). FILL below.
  CAMERA     lower than the game's 60 deg: lithium processing's disc is ~0.65
             as tall as wide, holmium processing's square plates the same, so
             ~40 deg; and a building is turned on the turntable so two faces
             show (the foundry, the cryogenic plant and the EM plant all stand
             corner-on, 20-35 deg off square).
  LIGHT      the buildings' sun and fill, as the items' icons have them.

Two ways in:

  items     a script calls tech_rig.main(ITEMS, POST) with builds as icon_rig's,
            run by render-icons.sh with TECH=1 in the environment (below)
  buildings tools/blender/tech_building.py runs a signed-off building model in
            its own --icon mode and takes over at its render call: the model
            builds exactly as it does for the game, nothing is remodelled
"""
import json
import math
import os
import sys

import bpy

import icon_rig
import rig

# the rig's own render, held here: tech_building.py replaces rig.render with its hook
# (the building model's own icon render is where it takes over)
_render = rig.render

ELEVATION = math.radians(float(os.environ.get("TECH_ELEV", "40")))   # TECH_ELEV: trials only
SIZES = tuple(int(x) for x in os.environ.get("TECH_SIZES", "256,128,64,32").split(","))   # TECH_SIZES: trials only
SS = int(os.environ.get("TECH_SS", "4"))
FILL = {"building": 228, "item": 220}          # px of 256 on the projection's long side
# the object sits this many px (of 256) left of and above centre, so the shadow it
# throws to the lower right stays on the canvas (round 1: framed centred, it ran off)
SHIFT = (-5, 6)
SAMPLES = {256: 128, 128: 128, 64: 160, 32: 160}


def camera(size):
    """An ortho camera at ELEVATION for size px; the scene and its light are the caller's."""
    sc = bpy.context.scene
    sc.render.resolution_x = sc.render.resolution_y = size * SS
    sc.render.resolution_percentage = 100
    sc.render.use_border = False
    sc.cycles.samples = SAMPLES.get(size, 128)
    data = bpy.data.cameras.new(f"tech_cam_{size}")
    data.type = "ORTHO"
    data.clip_start, data.clip_end = 0.1, 200
    cam = bpy.data.objects.new(f"tech_cam_{size}", data)
    sc.collection.objects.link(cam)
    tilt = math.pi / 2 - ELEVATION
    cam.rotation_euler = (tilt, 0, 0)
    d = 50.0
    cam.location = (0, -d * math.sin(tilt), d * math.cos(tilt))
    sc.camera = cam
    return cam


def frame(cam, objs, size, kind):
    """Fit objs' projection: the long side to FILL[kind] of 256, scaled to size, centred.
    The shadow is not framed: it may run out to the canvas edge, as vanilla's do."""
    xs, ys = icon_rig._projected(cam, objs)
    if not xs:
        raise SystemExit("tech_rig.frame: nothing to frame")
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    fill = FILL[kind] / 256 if size >= 64 else (size - 2) / size      # 1 px clear at 32
    scale = max(w, h) / fill
    cam.data.ortho_scale = scale
    k = 1 / 256 if size >= 64 else 0.0
    cam.data.shift_x = (max(xs) + min(xs)) / 2 / scale - SHIFT[0] * k
    cam.data.shift_y = (max(ys) + min(ys)) / 2 / scale - SHIFT[1] * k
    return {"ortho_scale": scale, "w": w / scale * size, "h": h / scale * size}


def shadow_floor(z=0.0, size=40):
    g = rig.ground_catcher(size)
    g.location.z = z
    return g


def render_sizes(name, objs, out, kind, finish="tech"):
    """Render objs at every size into <out>/<name>/<finish>/<size>.png; framing per size."""
    framing = {}
    for size in SIZES:
        cam = camera(size)
        fr = frame(cam, objs, size, kind)
        d = os.path.join(out, name, finish)
        os.makedirs(d, exist_ok=True)
        _render(os.path.join(d, f"{size}.png"))
        framing[f"{name}/{finish}/{size}"] = fr
        print(f"icon {name} {finish} {size}: {fr['w']:.1f} x {fr['h']:.1f} px", flush=True)
    return framing


# icon_post.py's rules for a technology icon: no alpha snap (the shadow is
# part-transparent and must stay so); sharpening and contrast grow as the size
# drops, as an item's do
# Every size cuts alpha under 30: the shadow catcher also records the sky the object
# hides from the floor around it, a faint veil (alpha 2-26) over the whole canvas
# (round 1); the sun's shadow itself is far denser and stays.
# And the shadow made denser (round 6, Liam): our shadows were lighter than Space
# Age's (343-996 dark part-transparent pixels against its 872-3819). Raising alpha
# alone made them solid and fewer (round 7: 237-576); the shadow is spread as well.
SHADOW = {256: [1.6, 40, 5.0, 190], 128: [1.6, 40, 2.5, 190], 64: [1.5, 40, 1.2, 190], 32: [1.4, 40, 0.6, 190]}
RULES = {
    256: {"alpha": [30, 255], "shadow": SHADOW[256]},
    128: {"sharpen": [0.6, 40], "alpha": [30, 255], "shadow": SHADOW[128]},
    64: {"sharpen": [0.6, 60], "contrast": 1.1, "alpha": [30, 255], "shadow": SHADOW[64]},
    32: {"sharpen": [0.5, 80], "contrast": 1.2, "rim": [0.7, 36], "alpha": [36, 255], "shadow": SHADOW[32]},
}


def declare(out, items, framing, post=None, finish="tech"):
    """icons.json for icon_post.py, merged with any already there (several runs, one dir)."""
    p = os.path.join(out, "icons.json")
    decl = json.load(open(p)) if os.path.exists(p) else {
        "sizes": list(SIZES), "ss": SS, "margin": 1, "finishes": [finish], "items": [], "post": {},
        "framing": {}, "elevation_deg": math.degrees(ELEVATION)}
    for it in items:
        if it not in decl["items"]:
            decl["items"].append(it)
        decl["post"][it] = {str(s): r for s, r in (post or RULES).items()}
    decl["framing"].update(framing)
    with open(p, "w") as f:
        json.dump(decl, f, indent=1)


def main(items, post=None):
    """Item technologies: {name: build() -> [objects]}, each on a fresh lit scene with a
    shadow floor. Run by render-icons.sh: blender -b --python <script> -- <out> [--only a,b]."""
    out, only = icon_rig._args()
    os.makedirs(out, exist_ok=True)
    framing = {}
    done = []
    for name, build in items.items():
        if only and name not in only:
            continue
        rig.reset()
        rig.sun()
        rig.bounce_ground()
        objs = build()
        shadow_floor()
        framing.update(render_sizes(name, objs, out, "item"))
        done.append(name)
    declare(out, done, framing, post)
