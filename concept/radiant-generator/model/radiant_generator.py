"""Radiant Generator (sae-radiant-generator): the Carousel Foundry at 5x5 -- the shipping model.

  BLENDER=<blender 5> tools/blender/render.sh concept/radiant-generator/model/radiant_generator.py <out-dir> \
      --ports --icon [--collide]
  (or directly: blender -b --python radiant_generator.py -- <out-dir> [--idle | --ports | --icon | --collide |
                --wreck] [--samples N] [--anim-samples N])

  --idle     the plate, the still and a working frame 0 (plate + glow lit in one render) only
  --ports    render.json alone: the generator has no ports (spec 5, 8), and the contract says so
  --icon     icon.png: the whole machine, working, framed to a 1024 px square
  --collide  no render: every moving part in every frame against every other part, by BVH;
             collide.txt in <out-dir>
  --wreck    the wreck alone (wreck.png): the quick loop for the remnants

Spec: concept/radiant-generator/building-spec-radiant-generator.md (written 35d626b, Liam
"Agreed to all the drafts", 2026-10-20). Built from the signed-off concept, options round 7
(r7_carousel_foundry.py and r7_kit.py, Liam 2026-10-19 "Sign off"): the same parts in the same
places, the same finish. What the shipping model changes (task radiant-generator-options, T08):

  - the light through tools/blender/radiant.py (spec 3.3), flicker 0, round 7's strength
    curves (rg_kit.lights, pose_light);
  - the layers of spec 7, each its own cropped sheet, declared to the packers (DECL): the
    plate (everything that does not move, openings dark); the moving parts, one layer per
    part that moves apart from the others (the carousel table, its drive pinion and coupling,
    the well's lid, the crane, the commutator, the two other couplings, the three gauges),
    each rendered alone with every other part a shadow catcher, so it carries the shadow it
    casts on the rest of the machine and is cut by whatever stands in front of it; the
    working windows (radiant.py's plate light) and their glow, one layer, every opening's
    bloom TIGHT (the well's too: rg_kit's note on R); the status lamps, white-cut;
  - the moving parts keep their finish as they move: materials.layered() reads world
    position, so each moving part reads the position it had at frame 0 instead (pin());
  - 32 frames, one crane cycle, at round 7's 1x GIF pace: 70 ms a frame, animation_speed
    60 x 0.070 = 4.2 ticks a frame, 5/21 (spec 6, decision 10);
  - its own wreck (spec 6: "the machine's own wreck, as the Siderane turbine's"): wreck.py;
  - what --collide found in round 7's geometry, fixed (FIX 1-14, in rg_kit.py and here): the hood's
    walls over the turning table, the chute, the bin and its lid, the hub, the pinion and its case,
    the crane's wheels and the housing's roof fittings in its path, the well (a solid disc over its
    mouth: now a ring with a bore, the hoists setting the cell on the light), the lid's hinge, the
    commutator's riser and its bed (a pit), the posts inside the housing, a ladder, a barrel, the
    lagged line, the pockets' bores; collide.py says which contacts are meant and why;
  - the glow renders' black floor taken out (glow_floor()); the slot's pane inset from its frame;
    the port's glow emission 18 (rg_kit's note on R); the cable sleeves' label paint matte cream.

Units are tiles; north is +Y. Nothing here is adopted: the sheets move to graphics/ only on
Liam's sign-off.
"""
import json
import math
import os
import re
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rg_kit as K  # noqa: E402
from rg_kit import *  # noqa: F401,F403,E402
import contract  # noqa: E402

IDLE = "--idle" in K.argv
PORTS = "--ports" in K.argv
ICON = "--icon" in K.argv
COLLIDE = "--collide" in K.argv
WRECK_ONLY = "--wreck" in K.argv
PLATE_SAMPLES = K.opt("--samples", 80)          # round 7's
ANIM_SAMPLES = K.opt("--anim-samples", 64)
SUN_E = K.opt("--sun", 8.8)                     # round 7's

NF = 32                                         # one crane cycle (spec 6)
SPEED = 5 / 21                                  # 70 ms a frame: 4.2 ticks (spec 6, decision 10)
# the moving layers in the order they are drawn: the crane last, over the table and the lid it
# shadows
LAYERS = ("carousel", "drive", "lid", "crane", "commutator", "coupling-converter", "coupling-pump",
          "gauge-switchgear", "gauge-converter", "gauge-transformer")
# about their own axes, held to their centroid; the pump's coupling is half hidden behind its motor and
# pump, so its visible centroid moves as it turns (7.5 px on the first pack): a cycle, unchecked
TURNING = ("commutator", "coupling-converter")
GLOWS = [("window-glow" if "disc" in g else "well-glow", g) for g in K.R.groups(("disc", "slot", "tube", "surface"))]
WRECK_CANVAS = (576, 576)       # 9 x 9 tiles: the wreck on its 5 x 5, its scorch and shadow past it


def anim(name):
    return dict(name=name, frames=NF, motion="turn" if name in TURNING else "cycle", animation_speed=SPEED)


window = K.R.window_animation("window", NF)
window["animation_speed"] = SPEED
DECL = dict(
    footprint=(5, 5),
    directions="one",               # spec 5: one picture for all four directions
    passes=[
        dict(name="idle", kind="plate", sheet="base"),
        dict(name="still", kind="still"),
        dict(name="shadow", kind="shadow", sheet="shadow"),
        dict(name="lamp", kind="light", sheet="status-lamp"),
        dict(name="wreck", kind="remnants", sheet="remnants", canvas=WRECK_CANVAS),
    ],
    animations=[anim(n) for n in LAYERS] + [window]
    + [K.R.glow_animation(name, "window", NF, shapes) for name, shapes in GLOWS],
    ports=[],                       # spec 8: no fluid box, no facing port
)

# ---------------------------------------------------------------- the machine (round 7, as signed off)
K.build_materials(((0.45, 0.3), (0.95, 0.35), (1.4, 0.3)))
lights([5])

CX, CY, RR, ZD = -1.05, 0.45, 1.25, 0.85
ZR = 1.8
# the deck is the floor between the units, not a plinth to the edge
floor(x0=-2.2, x1=2.2, n=9, notches=((1.7, 1.7, 2.5, 2.5), (-2.5, 1.75, -1.6, 2.5), (-2.5, -2.5, -1.75, -1.9),
                                     (1.5, -2.5, 2.5, -1.9)))

car = carousel(CX, CY, RR, n=8, zd=ZD, pick_a=0.0, L=4, drive_a=1.95)
P = car["pick"]
# the spent bin under the chute, west
box((-2.28, -0.3, 0.28), (0.42, 0.5, 0.56), "lead", bevel=0.02)          # FIX 3: 0.04 lower, its lid under the
box((-2.28, -0.3, 0.58), (0.46, 0.54, 0.05), "dark_steel")                # turning table's rim (round 7's crossed it)
handwheel((-2.28, -0.5, 0.7), 0.08)
hazard_tag((-2.28, -0.555, 0.4), 0.36, 0.05)

# the crucible and its plate rack, east
X0, X1, Y0, Y1, ZT = 0.45, 2.02, -0.8, 1.5, 1.05
W = crucible(X0, X1, Y0, Y1, ZT, well=(1.25, CY), slot=(0.75, 1.75, 0.95, 1.33), hinge="E", plates="x")
# tubes on the east flank, arms into the wall
TY = [-0.62 + 0.46 * i for i in range(5)]
box((2.25, 0.3, 0.06), (0.42, 2.3, 0.12), "dark_steel")
for i, y in enumerate(TY):
    tube(2.25, y, 0.1, i, h=0.9, arm=(-1, 0), arm_len=0.2)
pipe([(2.44, TY[0] - 0.2, 1.2), (2.44, TY[-1] + 0.1, 1.2)], r=0.03, mat="copper", flanges=False)

# the crane: rails on the north shield housing and on posts along the crucible's south face
housing(-0.2, 1.62, 1.78, 1.95, ZR - 0.06, mat="grey", roof="teal", dress=False)     # FIX 6 (rg_kit)
radiator(-0.1, 1.68, 1.6, 0.85, 1.68, mat="grey", fins=16)
# the coolant expansion tank: the north-east corner, round, standing clear of the housing
vtank(2.15, 2.02, 0.3, 1.3, mat="grey", bands=(0.4, 0.95), top="teal", nozzle=(-0.4, -0.3))
hose([(1.88, 1.85, 0.6), (1.8, 1.72, 0.85), (1.72, 1.7, 1.2)], r=0.05, mat="hose_k")
hazard_tag((2.15, 1.71, 0.7), 0.3, 0.05)
ladder(2.15, 1.63, 0.1, 1.2, axis="y", mat="ochre")     # FIX 11: 0.07 south, off the tank's wall (round 7's stood in it)
# FIX 7: at the well the hoists set the cell on the light's surface, its foot 0.005 over it (round 7's
# went 0.16 through it, and through the disc that covered the mouth)
WELL_DROP = 0.17
crane("x", (-1.0, 1.78), ZR, CY, P[0], W[0], P[2], W[2] + WELL_DROP, -0.55, 1.74, d=0.38, label_n=4,
      rail_posts=(-0.5, 0.4, 1.68), posts_on=lambda u, v: v < 1.5 or u < -0.2)       # FIX 10 (rg_kit)

# the DC bus: the tubes' and plates' bars down a tray to the switchgear, SE
tray([(2.3, -0.85, 1.2), (2.3, -1.3, 1.05), (2.05, -1.5, 1.05)])
cabinet(1.8, -1.9, 0.4, 0.6, 1.0, mat="grey")
cabinet(2.22, -1.9, 0.42, 0.6, 1.15, mat="green")
gauge((2.22, -2.21, 0.8), (0, -1, 0.15), r=0.06, live=lambda t: 0.2 * math.sin(2 * PI * t), layer="gauge-switchgear")
id_panel((1.8, -2.21, 0.6), 0.22, 0.12, stripe="red")

# the rotary converter along the south, its commutator at the east (DC) end
cv = converter(-1.75, 1.2, -1.95, 0.6, R=0.4, dc_east=True)
bundle([(1.7, -1.62, 0.95), (1.45, -1.45, 1.0), (cv["com"][0] + 0.05, -1.45, 0.95), (cv["com"][0], -1.55, 0.9)],
       cols=("red", "black", "red"), r=0.025)

# the transformer, SW, and the trunks out
tf = transformer(-2.15, -1.92, 0.58, 0.8, 0.8, mat="cream")
trunk([cv["ac_top"], (-1.2, -1.6, 1.2), (-1.9, -1.75, 1.25), tf], r=0.05)
trunk([(-2.3, -2.2, 0.9), (-2.42, -2.3, 0.5), (-2.49, -2.32, 0.1)], r=0.065)
trunk([(-2.0, -2.25, 0.9), (-1.95, -2.4, 0.5), (-1.92, -2.49, 0.1)], r=0.065)

# coolant for the crucible jacket and the tube caps: pump, hoses to the radiator housing
pv = motor(-0.6, 2.2, 0.35, d=(1, 0), s=0.8)
coupling(pv[0] + 0.05, pv[1], pv[2], 0.1, axis=(1, 0, 0), turns=2, layer="coupling-pump")
cyl((pv[0] + 0.25, pv[1], 0.35), 0.17, 0.25, "oxide", rot=(0, PI / 2, 0), verts=32)
hose([(pv[0] + 0.25, 2.2, 0.55), (0.0, 2.3, 0.9), (0.4, 2.1, 1.2)], r=0.07, mat="hose")
# FIX 13: the lagged line's middle 0.05-0.08 south, off the radiator's face (round 7's ran through its ribs)
lagged([(0.42, 1.45, 0.3), (0.3, 1.45, 0.5), (0.2, 1.47, 0.95), (0.25, 1.58, 1.3)], r=0.07)

# clutter: gas bottles NW, valves, barrels, a ladder, stains
for k, (x, y) in enumerate(((-2.25, 2.25), (-2.0, 2.3), (-2.32, 1.95))):
    cyl((x, y, 0.3), 0.11, 0.6, ("green", "grey", "hazard")[k], verts=24)
    head(x, y, 0.6, 0.11, 0.06, "dark_steel")
valve(-1.0, 2.3, 0.0, 0.5, wheel="red")
jbox(0.0, -1.15, w=0.28, mat="grey", z=0.1)
bundle([(0.0, -1.15, 0.5), (0.3, -1.05, 0.3), (0.5, -0.95, 0.25)], cols=("black", "yellow"))
ladder(0.42, 0.0, 0.1, 1.05, axis="y", mat="ochre")
tray([(-0.45, -1.22, 0.32), (0.95, -1.22, 0.32), (1.35, -1.4, 0.32)], w=0.2, cols=("black", "red", "black"))
# FIX 12: the barrels 0.03 and 0.05 west, the second out of the cable tray's bend (round 7's crossed its rail)
for k, (x, y) in enumerate(((0.59, -1.3), (0.80, -1.36))):
    cyl((x, y, 0.22), 0.1, 0.32, ("oxide", "grey")[k], verts=20)
    torus((x, y, 0.3), 0.102, 0.01, "bare", seg=20)
stain(0.2, -1.2, 0.5, 0.12)
stain(-2.0, 0.9, 0.2, 0.3)
stain(1.6, -2.35, 0.4, 0.1)

MACHINE = [o for o in K.OBJS if K.GROUP[o.name] == "machine"]

# ---------------------------------------------------------------- the wreck (remnants)
import wreck  # noqa: E402   builds into K.OBJS in the "wreck" group
WRECK = [o for o in K.OBJS if K.GROUP[o.name] == "wreck"]

# ---------------------------------------------------------------- groups
WINDOW_MATS = set(K.LIQUIDS) | {"tube_glass", "pane"}


def group_of(o):
    """window (the liquids and the glass over them), a moving layer, the plate, or the wreck."""
    if K.GROUP[o.name] == "wreck":
        return "wreck"
    names = {m.name for m in o.data.materials if m} if getattr(o.data, "materials", None) else set()
    lay = K.layer_of(o)
    if lay:
        return lay
    if names & WINDOW_MATS:
        return "window"
    return "plate"


PART = {o.name: group_of(o) for o in K.OBJS}
assert not [o.name for o in MACHINE if PART[o.name] == "window" and K.layer_of(o)], "a window on a moving part"


def members(*groups):
    return [o for o in K.OBJS if PART[o.name] in groups]


SHOW = {}


def pose(f):
    """Frame f of the 32-frame loop: every moving part, and which cells are shown (the
    carousel's pockets and the hoists' loads hide and show; SHOW keeps what the pose said)."""
    for o in MACHINE:
        o.hide_render = False
    K.pose((f % NF) / NF, True)
    for o in MACHINE:
        SHOW[o.name] = not o.hide_render


def setup(visible=(), catchers=(), holdouts=(), ground=False, camera=True):
    """Per pass: the groups the camera sees, those that catch the visible parts' shadows (and
    stand in front of them as a holdout would), and those cut out."""
    for o in K.OBJS:
        g = PART[o.name]
        shown = (g in visible or g in catchers or g in holdouts) and SHOW.get(o.name, True)
        o.hide_render = not shown
        o.is_shadow_catcher = g in catchers
        o.is_holdout = g in holdouts
        o.visible_camera = camera
    GROUND.hide_render = not ground
    BOUNCE.hide_render = ground


def check_layers():
    """Every part whose place or visibility changes over the loop is in a moving layer."""
    m0, moved = {}, set()
    for f in range(NF):
        pose(f)
        bpy.context.view_layer.update()
        for o in MACHINE:
            st = (tuple(tuple(r) for r in o.matrix_world), SHOW[o.name])
            if o.name not in m0:
                m0[o.name] = st
            elif any(abs(a - b) > 1e-6 for ra, rb in zip(st[0], m0[o.name][0]) for a, b in zip(ra, rb)) \
                    or st[1] != m0[o.name][1]:
                moved.add(o.name)
    stray = sorted(n for n in moved if PART[n] not in LAYERS)
    if stray:
        sys.exit(f"parts move but are in no layer: {stray[:10]}")
    still = [lay for lay in LAYERS if not any(PART[n] == lay for n in moved)]
    if still:
        sys.exit(f"layers that do not move: {still}")
    return moved


# ---------------------------------------------------------------- the finish carried by moving parts
def pin():
    """materials.layered() reads world position, so a part that moves would slide under its
    own wear. Each moving part's mesh (modifiers applied) gets its frame-0 world position as an
    attribute, P0, and its materials a copy that reads P0 where they read position: the finish
    rides with the part, and frame 0 renders as before."""
    pose(0)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    cache = {}
    for o in MACHINE:
        if PART[o.name] not in LAYERS or o.type != "MESH":
            continue
        ev = o.evaluated_get(dg)
        me = bpy.data.meshes.new_from_object(ev)
        mw = o.matrix_world.copy()
        o.modifiers.clear()
        o.data = me
        at = me.attributes.new("P0", "FLOAT_VECTOR", "POINT")
        for v, a in zip(me.vertices, at.data):
            a.vector = mw @ v.co
        for i, m in enumerate(me.materials):
            if m is None:
                continue
            if m.name not in cache:
                c = m.copy()
                c.name = m.name + "-pinned"
                t = c.node_tree
                geos = [nd for nd in t.nodes if nd.bl_idname == "ShaderNodeNewGeometry"]
                if geos:
                    attr = t.nodes.new("ShaderNodeAttribute")
                    attr.attribute_type = "GEOMETRY"
                    attr.attribute_name = "P0"
                    for nd in geos:
                        for lk in list(nd.outputs["Position"].links):
                            t.links.new(attr.outputs["Vector"], lk.to_socket)
                cache[m.name] = c
            me.materials[i] = cache[m.name]
    return len(cache)


# ---------------------------------------------------------------- the camera's windows
def window_of(objs, poses, pad=(0.3, 0.3, 1.1, 0.6), canvas=None):
    """The render border (sprite px x0, y0, x1, y1 from the canvas's top left) round objs over
    every pose, padded (left, down, right, up, tiles) for the shadows they cast (the sun throws
    them right and up the screen) or a glow's tail."""
    W_, H_ = canvas or K.CANVAS
    cam = K.sc.camera
    inv = cam.matrix_world.inverted()
    xs, ys = [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for ps in poses:
        ps()
        bpy.context.view_layer.update()
        for o in objs:
            if o.type != "MESH" or not SHOW.get(o.name, True):
                continue
            ev = o.evaluated_get(dg)
            for c in ev.bound_box:
                p_ = inv @ (ev.matrix_world @ Vector(c))
                xs.append(p_.x)
                ys.append(p_.y)
    ppt = K.rig.PX_PER_TILE
    x0 = max(0, int(W_ / 2 + (min(xs) - pad[0]) * ppt))
    x1 = min(W_, int(W_ / 2 + (max(xs) + pad[2]) * ppt) + 1)
    y0 = max(0, int(H_ / 2 - (max(ys) + pad[3]) * ppt))
    y1 = min(H_, int(H_ / 2 - (min(ys) - pad[1]) * ppt) + 1)
    return x0, y0, x1, y1


def border(win, canvas=None):
    W_, H_ = canvas or K.CANVAS
    x0, y0, x1, y1 = win
    K.sc.render.use_border = True
    K.sc.render.use_crop_to_border = False
    K.sc.render.border_min_x, K.sc.render.border_max_x = x0 / W_, x1 / W_
    K.sc.render.border_min_y, K.sc.render.border_max_y = 1 - y1 / H_, 1 - y0 / H_


def no_border():
    K.sc.render.use_border = False


def path(stem):
    return os.path.join(K.OUT, stem + ".png")


def render(stem):
    K.rig.render(path(stem))


def glow_floor(stem):
    """A glow render's black floor taken out: with the sun and sky off, the machine the light does
    not reach renders (1, 1, 1) at 1x -- the rig's film look -- and pack.py's bloom (gains 0.9 and
    0.6) lifted that to 3, over its GLOW_FLOOR of 2, so the glow layer added 3 levels of grey over
    its whole window and tipped rolled-off glints to white (measure.py's white_px 1, clipped_px 2 on
    the first full pack). Every pixel whose brightest channel is at or under 1/255 is made 0: the
    light itself is never that faint where it is seen."""
    import numpy as np
    img = bpy.data.images.load(path(stem))
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)
    dark = a[:, :, :3].max(axis=2) <= 1.5 / 255
    a[dark, :3] = 0.0
    img.pixels.foreach_set(a.ravel())
    img.filepath_raw = path(stem)
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


# ---------------------------------------------------------------- --ports: there are none
if PORTS:
    contract.declare(K.OUT, canvas=K.CANVAS, **DECL)
    print("ports: none declared (spec 5, 8: no fluid box, no facing port); nothing to render")
    print("done")
    sys.exit(0)

# ---------------------------------------------------------------- --collide
if COLLIDE:
    import collide
    collide.check(K, MACHINE, PART, LAYERS, pose, NF, SHOW)
    print("done")
    sys.exit(0)

MOVED = check_layers()
# --no-pin and --layers a,b: a study only (round 7's finish, unpinned; just those layers' frames rendered)
PINNED = 0 if "--no-pin" in K.argv else pin()
ONLY_LAYERS = K.argv[K.argv.index("--layers") + 1].split(",") if "--layers" in K.argv else None

SUN = K.rig.sun(SUN_E)
SUN.data.color = (1.0, 0.94, 0.82)
K.sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.24      # round 7's
GROUND = K.rig.ground_catcher()
GROUND.parent = K.ROOT
BOUNCE = K.rig.bounce_ground()
MACHINE_GROUPS = ("plate", "window") + LAYERS

# ---------------------------------------------------------------- --icon
if ICON:
    # the whole machine working at frame 0 (the windows at radiant.py's working-plate light,
    # the lamps lit), on the plate's camera, framed to fill a 1024 px square
    K.sc.cycles.samples = 128
    cam = K.rig.camera(1024, 1024, ss=1)
    pose(0)
    K.pose_light(0.0, "plate")
    K.lamps(True)
    setup(visible=MACHINE_GROUPS)
    GROUND.hide_render = True
    for o in K.STAINS:
        o.hide_render = True
    bpy.context.view_layer.update()
    inv = cam.matrix_world.inverted()
    xs, ys = [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for o in MACHINE:
        if o.hide_render or o.type != "MESH":
            continue
        ev = o.evaluated_get(dg)
        for c in ev.bound_box:
            p_ = inv @ (ev.matrix_world @ Vector(c))
            xs.append(p_.x)
            ys.append(p_.y)
    span = max(max(xs) - min(xs), max(ys) - min(ys)) / 0.96
    cam.data.ortho_scale = span
    cam.data.shift_x = (max(xs) + min(xs)) / 2 / span
    cam.data.shift_y = (max(ys) + min(ys)) / 2 / span
    K.rig.render(os.path.join(K.OUT, "icon.png"))
    print(f"icon: {span:.2f} tiles across")
    print("done")
    sys.exit(0)

K.rig.camera(*K.CANVAS)

if "--pick" in K.argv:
    # which part the camera sees at sprite px x,y (a study aid): a ray from the camera through it
    pose(int(K.opt("--pick-frame", 0)))
    setup(visible=MACHINE_GROUPS)
    bpy.context.view_layer.update()
    cam = K.sc.camera
    for xy in K.argv[K.argv.index("--pick") + 1].split(";"):
        x, y = (float(v) for v in xy.split(","))
        W_, H_ = K.CANVAS
        span = cam.data.ortho_scale
        u, v = (x + 0.5 - W_ / 2) / max(W_, H_) * span, (H_ / 2 - y - 0.5) / max(W_, H_) * span
        m = cam.matrix_world
        o = m @ Vector((u, v, 0.0))
        d = (m.to_3x3() @ Vector((0, 0, -1))).normalized()
        dg = bpy.context.evaluated_depsgraph_get()
        for _ in range(6):                 # the first hits along the ray, nearest first
            hit, loc, nrm, idx, ob, _m = K.sc.ray_cast(dg, o, d)
            if not hit:
                break
            print("PICK", xy, ob.name, ob.data.materials[0].name if ob.data.materials else None, PART.get(ob.name),
                  tuple(round(c, 3) for c in (K.ROOT.matrix_world.inverted() @ loc)))
            o = loc + d * 1e-4
    sys.exit(0)

if "--debug-light" in K.argv:
    # the light's numbers at frame 0 in the glow pass, and one glow render of every window (not packed)
    pose(0)
    K.pose_light(0.0, "glow")
    for o in K.OBJS:
        if o.data.materials and o.data.materials[0] and o.data.materials[0].name in K.LIQUIDS:
            xs = [v.co for v in o.data.vertices]
            print("LIQUID", o.name, o.data.materials[0].name, [round(min(v[i] for v in xs), 3) for i in range(3)],
                  [round(max(v[i] for v in xs), 3) for i in range(3)], tuple(round(c, 3) for c in o.scale),
                  [m.type for m in o.modifiers])
    for name in K.LIQUIDS:
        b = K.M[name].node_tree.nodes["Principled BSDF"]
        users = [o.name for o in K.OBJS if o.data.materials and o.data.materials[0] == K.M[name]]
        print("LIGHT", name, round(b.inputs["Emission Strength"].default_value, 3), users,
              [(PART[u], K.sc.objects[u].hide_render) for u in users])
    K.sc.cycles.samples = 16
    K.glint(False)
    setup(visible=MACHINE_GROUPS)
    hide = K.argv[K.argv.index("--debug-hide") + 1].split(",") if "--debug-hide" in K.argv else []
    only = K.argv[K.argv.index("--debug-only") + 1].split(",") if "--debug-only" in K.argv else None
    for o in K.OBJS:
        nm = o.data.materials[0].name if o.data.materials and o.data.materials[0] else ""
        if nm in hide or (only and nm not in only):
            o.hide_render = True
    with K.R.glow_pass(hide=(GROUND, BOUNCE)):
        render("debug-glow")
    print("done")
    sys.exit(0)

if ONLY_LAYERS:
    K.sc.cycles.samples = ANIM_SAMPLES
    K.lamps(False)
    K.pose_light(0.0, "idle")
    for name in ONLY_LAYERS:
        win = window_of(members(name), [lambda f=f: pose(f) for f in range(NF)])
        border(win)
        others = tuple(g for g in MACHINE_GROUPS if g != name)
        for f in range(NF):
            pose(f)
            setup(visible=(name,), catchers=others)
            render(contract.frame(name, f))
        no_border()
    print("done")
    sys.exit(0)

if not WRECK_ONLY:
    # ------------------------------------------------------------ the plate, the still, the shadow
    K.sc.cycles.samples = PLATE_SAMPLES
    pose(0)
    K.pose_light(0.0, "idle")
    K.lamps(False)
    K.glint(True)
    # the plate: everything that does not move, the openings dark; the moving parts out of the
    # scene, so their shadows are their own layers'
    setup(visible=("plate", "window"))
    render("idle")
    # the still: the whole machine at frame 0, stopped (the reference for the frame-0 check)
    setup(visible=MACHINE_GROUPS)
    render("still")
    if IDLE:
        # the quick look: frame 0 working, the windows lit, in one render (not packed)
        K.pose_light(0.0, "plate")
        K.lamps(True)
        render("working-look")
        K.pose_light(0.0, "idle")
        K.lamps(False)
        print("done")
        sys.exit(0)
    contract.declare(K.OUT, canvas=K.CANVAS, **DECL)
    # the shadow: the whole machine at frame 0 on the ground catcher, seen by nothing else
    setup(visible=MACHINE_GROUPS, ground=True, camera=False)
    render("shadow")
    # the status lamps' lenses, lit white, everything else held out
    setup(visible=("plate",), holdouts=("window",) + LAYERS)
    for o in members("plate"):
        o.is_holdout = not (o.data.materials and o.data.materials[0] and o.data.materials[0].name == "lamp")
    K.lamp_cut(True)
    render("lamp")
    K.lamp_cut(False)

    # ------------------------------------------------------------ the moving layers
    K.sc.cycles.samples = ANIM_SAMPLES
    WINDOWS = {}
    for name in LAYERS:
        objs = members(name)
        win = window_of(objs, [lambda f=f: pose(f) for f in range(NF)])
        WINDOWS[name] = win
        border(win)
        others = tuple(g for g in MACHINE_GROUPS if g != name)
        for f in range(NF):
            pose(f)
            setup(visible=(name,), catchers=others)
            render(contract.frame(name, f))
        no_border()

    # ------------------------------------------------------------ the windows and their glow
    wobjs = members("window")
    win = window_of(wobjs, [lambda: pose(0)], pad=(0.1, 0.1, 0.1, 0.1))
    WINDOWS["window"] = win
    border(win)
    for f in range(NF):
        pose(f)
        K.pose_light(f / NF, "plate")
        setup(visible=("window",), holdouts=("plate",) + LAYERS)
        render(contract.frame("window", f))
    no_border()
    K.glint(False)
    for name, shapes in GLOWS:
        lit = [o for o in wobjs if o.data.materials[0].name in K.LIQUIDS
               and K.LIQUIDS[o.data.materials[0].name][0] in shapes]
        win = window_of(lit, [lambda: pose(0)], pad=(1.2, 1.2, 1.2, 1.2))
        WINDOWS[name] = win
        border(win)
        for f in range(NF):
            pose(f)
            K.pose_light(f / NF, "glow", shapes)
            setup(visible=MACHINE_GROUPS)
            with K.R.glow_pass(hide=(GROUND, BOUNCE)):
                render(contract.frame(name, f))
            glow_floor(contract.frame(name, f))
        no_border()
    K.glint(True)
    K.pose_light(0.0, "idle")
    pose(0)
else:
    contract.declare(K.OUT, canvas=K.CANVAS, **DECL)
    WINDOWS = {}

# ---------------------------------------------------------------- the wreck
# on its own canvas over the ground catcher: its shadow and scorch caught in the same picture,
# as vanilla's remnants carry theirs (pack.py); the machine gone
wreck.soot()
K.sc.cycles.samples = PLATE_SAMPLES
K.rig.camera(*WRECK_CANVAS)
no_border()
setup(visible=("wreck",), ground=True)
render("wreck")

with open(os.path.join(K.OUT, "model.json"), "w") as f_:
    json.dump(dict(windows=WINDOWS, frames=NF, animation_speed=SPEED, samples=dict(plate=PLATE_SAMPLES,
                   anim=ANIM_SAMPLES), sun=SUN_E, groups={g: len(members(g)) for g in MACHINE_GROUPS + ("wreck",)},
                   pinned_materials=PINNED, moving_parts=len(MOVED)), f_, indent=1)
print("done")
