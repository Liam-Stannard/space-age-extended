"""Reaction Plant redesign, animation previews: the candidate motions on round 5's Circulator.

  $BLENDER -b --python anim_previews.py -- <out-dir> --mode MODE [--quick] [--ss K] [--frames a:b]

Liam, 2026-10-11: "Could you show me what these animations would look like." Each mode
builds round 5's model and finish exactly (round-5/r5_circulator.py, executed up to its
render passes, colours untouched), adds only what that motion needs, and renders the
motion alone; every other moving part holds at frame 0. Blocked out, not final art.

  current   the legs (24 f: the solution's bands, bubbles and flecks) and the four
            free couplings (60 deg a loop), as round 5 renders them
  press     the filter press cycle: the follower (the head, its ram and handwheel, the
            feed hose flexing) backs off 0.24 tile, the cake on the last leaf peels and
            drops into the lead drop box, the follower closes. 16 unique frames; the cake
            meets the box floor on frame 10 (the sound accent; never frame 0)
  gauges    the needles of the reactor's two gauges and the scrubber's twitching with the
            flow (24 f, seamless)
  gauges_big  the same, the three dials at twice round 5's size (a model change)
  drive     the agitator drive: the head coupling replaced by an exposed shaft, a big
            five-spoked pulley, a flat belt with steel lacing clips and the motor's
            three-spoked pulley (24 f; 144 deg a loop on the big pulley, one turn on the small)
  drip      the vent condenser: condensate beads running down its copper flank and drops
            falling from a drain cock into a wet patch (24 f). No steam, no plume.
  all       everything together over 48 frames: the 24-frame loops twice, the press cycle
            once in frames 24-39 (in game it holds ~17 s between cycles at speed 1)
  test      one quick plate with every addition, for layout

Writes <out-dir>/working-NN.png (on the shadow catcher, light on), plate.png (frame 0,
working, no ground: the mask the moving share is measured on) and idle.png. Same canvas,
origin and 4x supersampling as round 5 (512 x 448, origin (208, 272)).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R5 = os.path.normpath(os.path.join(HERE, "..", "round-5", "r5_circulator.py"))

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODE = argv[argv.index("--mode") + 1]
BEFORE = "--before" in argv        # the previews as first shown (2026-10-11), before the clash fixes
BUILD = {"all": "all", "collide": "all"}.get(MODE, MODE)   # what gets built: --collide checks "all"
FRANGE = argv[argv.index("--frames-range") + 1] if "--frames-range" in argv else None

src = open(R5).read()
src = src[:src.index("\nrig.camera(*CANVAS, centre_px=CENTRE, ss=SSK)\nGROUND")]


def patch(old, new):
    global src
    assert src.count(old) == 1, old
    src = src.replace(old, new)


# capture the parts the previews move; nothing changes how they are built
# gauges_big: the reactor's and the scrubber's dials at twice their size (a model change, shown
# because at round 5's size the needles move 7 px at 1x); every other gauge as built
def GAUGE_K(loc):
    # Liam, 2026-10-11: the gauges are the double-size dials, so "all" gets them too
    if not (MODE == "gauges_big" or (not BEFORE and BUILD in ("all", "test"))):
        return 1.0
    x, y = loc[0], loc[1]
    if abs(math.hypot(x - 1.3, y - 0.1) - 0.9) < 0.15 or abs(math.hypot(x + 1.99, y - 1.85) - 0.5) < 0.12:
        return 2.0
    return 1.0


patch('    """A brass-cased gauge: a cream face, a red needle."""\n',
      '    """A brass-cased gauge: a cream face, a red needle."""\n    _k = GAUGE_K(loc)\n    r = r * _k\n'
      '    _g0 = len(OBJS)\n')
patch('(r * 0.9, 0.006, 0.012), "needle",\n        rz=math.atan2(u.y, u.x) + 0.6, bevel=0)\n',
      '(r * 0.9, 0.006, 0.012 * _k), "needle",\n        rz=math.atan2(u.y, u.x) + 0.6, bevel=0)\n')
patch("OBJS = []\nANIM = []", "OBJS = []\nNEEDLES = []\nCAP = {}\nANIM = []")
patch('    box(tuple(Vector(loc) + t * 0.022 + u * r * 0.2), (r * 0.9, 0.006, 0.012 * _k), "needle",\n'
      '        rz=math.atan2(u.y, u.x) + 0.6, bevel=0)',
      '    NEEDLES.append((box(tuple(Vector(loc) + t * 0.022 + u * r * 0.2), (r * 0.9, 0.006, 0.012 * _k), "needle",\n'
      '        rz=math.atan2(u.y, u.x) + 0.6, bevel=0), Vector(loc), t))\n'
      '    if _k != 1.0:\n        CAP.setdefault("big_gauges", []).extend(OBJS[_g0:])')
patch("    coupling(RX - 0.1, RY - 0.05, H + 0.47, 0.17)", '    CAP["head_coupling"] = coupling(RX - 0.1, RY - 0.05, H + 0.47, 0.17)')
patch('        box((L0 + 0.2 + 0.1 * i, yp, 0.9), (0.09, d - 0.08, 0.56), "lead" if i % 2 else "cream", bevel=0.01)',
      '        CAP.setdefault("leaves", []).append(box((L0 + 0.2 + 0.1 * i, yp, 0.9), (0.09, d - 0.08, 0.56), '
      '"lead" if i % 2 else "cream", bevel=0.01))')
patch('    box((L1 - 0.1, yp, 0.92), (0.18, d + 0.04, 0.76), "dark_steel")\n'
      '    cyl((L1 + 0.08, yp, 0.95), 0.14, 0.2, "green", rot=(0, PI / 2, 0), verts=24)\n'
      '    handwheel((L1 + 0.22, yp, 0.95), 0.15, axis=(1, 0, 0), mat="yellow")',
      '    _n = len(OBJS)\n'
      '    box((L1 - 0.1, yp, 0.92), (0.18, d + 0.04, 0.76), "dark_steel")\n'
      '    cyl((L1 + 0.08, yp, 0.95), 0.14, 0.2, "green", rot=(0, PI / 2, 0), verts=24)\n'
      '    handwheel((L1 + 0.22, yp, 0.95), 0.15, axis=(1, 0, 0), mat="yellow")\n'
      '    CAP["follower"] = OBJS[_n:]\n'
      '    CAP["press"] = (L0, L1, yp, d)')
patch('    hose([(L1 - 0.1, yp + 0.2, 1.32), (-0.35, -1.55, 1.2), (-0.1, -1.75, 0.95)], r=0.1, mat="hose_k")',
      '    _n = len(OBJS)\n'
      '    hose([(L1 - 0.1, yp + 0.2, 1.32), (-0.35, -1.55, 1.2), (-0.1, -1.75, 0.95)], r=0.1, mat="hose_k")\n'
      '    CAP["feed_hose"] = OBJS[_n:]')
patch("    hazard_tag((-0.72, -2.335, 1.12), 0.14, 0.06)",
      '    _n = len(OBJS)\n    hazard_tag((-0.72, -2.335, 1.12), 0.14, 0.06)\n    CAP["follower"] += OBJS[_n:]')

# ---- the clash fixes (Liam, 2026-10-11: "a small problem is the vent pump clips"), found by
# --mode collide; --before leaves them out. Each removes a crossing; none moves a mass.
STROKE = 0.24 if BEFORE else 0.18  # the press's opening stroke, tiles
RAIL_EXT = 0.0 if BEFORE else STROKE   # the press rails run on west under the tail stand's stroke


def _nd(t, u):
    """A needle's direction: in its dial's plane, 0.6 rad up from the horizontal u."""
    from mathutils import Vector as _V
    v = _V(u).cross(_V(t)).normalized()
    return (_V(u) * math.cos(0.6) + v * math.sin(0.6)).normalized()


def _nrot(t, u):
    from mathutils import Matrix as _M, Vector as _V
    d = _nd(t, u)
    tt = _V(t).normalized()
    tt = (tt - d * tt.dot(d)).normalized()
    return tuple(_M((d, tt, d.cross(tt))).transposed().to_euler())


def _axial(root, k):
    """A coupling made thinner along its shaft so it turns in the gap between its two machines."""
    root.scale = (1.0, 1.0, k)
    return root


if not BEFORE:
    # the exchanger's dished heads ran 0.05-0.1 tile into the vent condenser's copper shell (and
    # foot ring) at the east and into the scrubber at the west: both heads pulled back clear
    patch('exchanger(-1.55, 1.55, 2.14, 0.38, 0.3, mat="grey")', 'exchanger(-1.42, 1.45, 2.14, 0.38, 0.3, mat="grey")')
    # the compressor's coupling turned 0.015 into the compressor's end and its stripe into the
    # motor: centred in the 0.08 gap and 0.7 as thick
    patch("coupling(0.42, 1.36, 0.38, 0.12, axis=(1, 0, 0))",
          "_axial(coupling(0.43, 1.36, 0.38, 0.12, axis=(1, 0, 0)), 0.7)")
    # the dosing pump's coupling turned into the pump body, its stub shaft, and the hose above
    patch("coupling(-1.0, 0.13, 0.28, 0.09, axis=(1, 0, 0))",
          "_axial(coupling(-0.995, 0.13, 0.28, 0.09, axis=(1, 0, 0)), 0.6)")
    patch("hose([(-1.5, 0.38, 0.5), (-1.0, 0.3, 0.36),", "hose([(-1.5, 0.38, 0.5), (-1.0, 0.34, 0.41),")
    # every needle was turned 0.6 rad about the vertical, out of its dial's plane, so one end
    # stood off the face and the other ran back through the case (on the double dials, into the
    # reactor's wall): now it lies on the face, at the same 0.6 rad, thin side to the glass
    patch('    NEEDLES.append((box(tuple(Vector(loc) + t * 0.022 + u * r * 0.2), (r * 0.9, 0.006, 0.012 * _k), "needle",\n'
          '        rz=math.atan2(u.y, u.x) + 0.6, bevel=0), Vector(loc), t))',
          '    NEEDLES.append((box(tuple(Vector(loc) + t * 0.022 + _nd(t, u) * r * 0.2), (r * 0.9, 0.006, 0.012 * _k),\n'
          '        "needle", rot=_nrot(t, u), bevel=0), Vector(loc), t))')
    # the double dials stand 0.02 off the wall on a stem, clear of the weld beads and seams
    # they sat across; the reactor's upper one moves 0.12 rad west, off the ladder's rail
    patch('    t = Vector(facing).normalized()\n    cyl(loc, r, 0.03, "brass"',
          '    t = Vector(facing).normalized()\n'
          '    if _k != 1.0:\n'
          '        cyl(tuple(Vector(loc) - t * 0.01), 0.035, 0.05, "bare", rot=along(t), verts=12, bevel=0)\n'
          '        loc = tuple(Vector(loc) + t * 0.02)\n'
          '    cyl(loc, r, 0.03, "brass"')
    patch("    p, _ = on_wall(RX, RY, R, -1.3, 1.68, 0.0)", "    p, _ = on_wall(RX, RY, R, -1.42, 1.68, 0.0)")
    # the hose off the press head started 0.04 over the last leaf: its brass nut sat in the leaf
    patch("    hose([(L1 - 0.1, yp + 0.2, 1.32), (-0.35, -1.55, 1.2)", "    hose([(L1 - 0.06, yp + 0.2, 1.32), (-0.35, -1.55, 1.2)")
# the press: its tail stand captured (it moves now, with the leaves), the rails lengthened west;
# fixed, the tail stand's foot is raised 0.04: it stood 0.03 into the drop box's lid disc,
# which it now slides over
patch('    box((L0 + 0.06, yp, 0.9), (0.12, d, 0.7), "dark_steel")\n',
      '    CAP["tail"] = box((L0 + 0.06, yp, 0.9), (0.12, d, 0.7), "dark_steel")\n' if BEFORE else
      '    CAP["tail"] = box((L0 + 0.06, yp, 0.92), (0.12, d, 0.66), "dark_steel")\n')
patch('        box(((L0 + L1) / 2, yp + s_ * (d / 2 - 0.03), 1.18), (L1 - L0, 0.07, 0.08), "bare", bevel=0.01)',
      '        box(((L0 - RAIL_EXT + L1) / 2, yp + s_ * (d / 2 - 0.03), 1.18), (L1 - L0 + RAIL_EXT, 0.07, 0.08), '
      '"bare", bevel=0.01)')

G = {"__file__": R5, "__name__": "r5_circulator", "GAUGE_K": GAUGE_K, "_axial": _axial, "RAIL_EXT": RAIL_EXT,
     "_nd": _nd, "_nrot": _nrot}
exec(compile(src, R5, "exec"), G)
globals().update({k: v for k, v in G.items() if not k.startswith("__")})
N_R5 = len(OBJS)                   # everything after this is a preview's addition

import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

TAU = 2 * math.pi


def objs_under(root):
    return [root] + list(root.children_recursive)


def classify():
    legs, cpl = [], []
    for p in ANIM:
        (cpl if p.__qualname__.startswith("coupling.") else legs).append(p)
    return legs, cpl


LEG_POSES, CPL_POSES = classify()

# ===================================================================== the filter press
L0, L1, YP, PD = CAP["press"]
D_OPEN = STROKE                    # the opening stroke, tiles
FOLLOWER = [(o, o.matrix_basis.copy()) for o in CAP["follower"]]
# Before the fixes the follower (the hydraulic head, its ram and handwheel, the feed hose
# flexing) backed off east -- straight into the filtrate receiver, whose west end it is
# built over. Fixed: the head stays put, as a press's cylinder head is bolted down, and the
# leaf pack backs off west with the tail stand along the rails (lengthened by the stroke);
# the cake hangs off the last leaf and falls into a dark chute mouth on the drop box.
PACK = [(o, o.matrix_basis.copy()) for o in CAP["leaves"] + [CAP["tail"]]]
print("follower parts:", len(FOLLOWER), "pack parts:", len(PACK))
LAST_LEAF_E = L0 + 0.2 + 0.1 * 4 + 0.045
CAKE_T, CAKE_Z0 = (0.1, 0.62) if BEFORE else (0.08, 0.62)   # the cake: thickness, its foot (the leaves')
CAKE_D = PD - 0.14 if BEFORE else PD - 0.18
# Liam: the cake toned down from white -- a damp grey-buff filter cake, a step under the cream leaves
M["cake"] = layered("cake", "#E6E2D6" if BEFORE else "#8C8476", paint_metal=0.0, paint_rough=0.85, wear=0.0,
                    rust=0.0, dust=0.3, grime=0.35 if not BEFORE else 0.25)
CAKE = None
if BUILD in ("press", "all", "test"):
    CAKE = box((LAST_LEAF_E + CAKE_T / 2, YP, CAKE_Z0 + 0.25), (CAKE_T, CAKE_D, 0.5), "cake", bevel=0.02)
    CAKE_M0 = CAKE.matrix_basis.copy()
    CAKE.hide_render = MODE != "test"
    if not BEFORE:
        # the chute mouth the cake drops into: a dark opening in the drop box's steel lid,
        # under the gap the stroke opens
        x0, x1 = LAST_LEAF_E - STROKE - 0.015, L1 - 0.1 - 0.09 - 0.005
        box(((x0 + x1) / 2, YP, 0.582), (x1 - x0, CAKE_D + 0.03, 0.006), "dark", bevel=0)


def smooth(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


# 16 unique frames: 0 closed (the plate), 1-4 the press opens, 5 the cake hangs,
# 6-9 it peels and falls (gravity at 14 fps), 10 it is in the box (the accent), 11-15 the
# press closes.
PRESS_OPEN = [0.0, smooth(1 / 4), smooth(2 / 4), smooth(3 / 4), 1, 1, 1, 1, 1, 1, 1,
              1 - smooth(1 / 6), 1 - smooth(2 / 6), 1 - smooth(3 / 6), 1 - smooth(4 / 6), 1 - smooth(5 / 6)]
PRESS_FALL = [None, None, 0.0, 0.0, 0.0, 0.0, 0.025, 0.10, 0.225, 0.40, None, None, None, None, None, None]
if not BEFORE:          # the cake shows once the gap is wider than it (frame 2's 0.09 is not)
    PRESS_FALL[2] = None
# before: tilted into the leaf it peels off (the sign was wrong); fixed: away from it, as
# far as the gap to the head allows
PRESS_TILT = [0, 0, 0, 0, 0, 0, 4, 9, 14, 18, 0, 0, 0, 0, 0, 0] if BEFORE else \
    [0, 0, 0, 0, 0, 0, 2, 4, 5, 5, 0, 0, 0, 0, 0, 0]
PRESS_LAND = 10
HOSE_START = Vector((L1 - 0.1, YP + 0.2, 1.32))
_hose_live = []


def pose_press(k):
    global _hose_live
    dx = D_OPEN * PRESS_OPEN[k]
    if BEFORE:
        T = Matrix.Translation((dx, 0, 0))
        for o, m0 in FOLLOWER:
            o.matrix_basis = T @ m0
        # the feed hose flexes with the follower: rebuilt with its first point moved
        for o in _hose_live:
            bpy.data.objects.remove(o, do_unlink=True)
        _hose_live = []
        for o in CAP["feed_hose"]:
            o.hide_render = dx > 1e-6
        if dx > 1e-6:
            n = len(OBJS)
            hose([tuple(HOSE_START + Vector((dx, 0, 0))), (-0.35 + dx * 0.4, -1.55, 1.2), (-0.1, -1.75, 0.95)],
                 r=0.1, mat="hose_k")
            _hose_live = OBJS[n:]
    else:
        T = Matrix.Translation((-dx, 0, 0))
        for o, m0 in PACK:
            o.matrix_basis = T @ m0
    if CAKE is not None:
        fall = PRESS_FALL[k]
        CAKE.hide_render = fall is None
        if fall is not None:
            pivot = Vector((LAST_LEAF_E, YP, CAKE_Z0))
            tilt = math.radians(-PRESS_TILT[k] if BEFORE else PRESS_TILT[k])
            R = Matrix.Translation(pivot) @ Matrix.Rotation(tilt, 4, "Y") @ Matrix.Translation(-pivot)
            shift = 0.0 if BEFORE else -dx
            CAKE.matrix_basis = Matrix.Translation((shift, 0, -fall)) @ R @ CAKE_M0


# ===================================================================== the gauge needles
SX, SY = -1.99, 1.85


def gauge_group(loc):
    if abs((Vector((loc.x, loc.y)) - Vector((RX, RY))).length - R) < 0.15:
        return "reactor"
    if abs((Vector((loc.x, loc.y)) - Vector((SX, SY))).length - 0.5) < 0.12:
        return "scrubber"
    return None


TWITCH = []
for i, (o, loc, t) in enumerate(NEEDLES):
    g = gauge_group(loc)
    if g:
        TWITCH.append((o, o.matrix_basis.copy(), loc, t.normalized(), i))
print("needles twitching:", len(TWITCH), "of", len(NEEDLES))


def needle_angle(t, i):
    """Degrees; 0 at t = 0, seamless over the loop: a slow swell, a flutter, two flicks."""
    a = 9 * math.sin(TAU * (t + 0.0)) + 6 * math.sin(TAU * 3 * t + 0.0) * math.cos(TAU * (i * 0.17))
    a += 5 * math.sin(TAU * 7 * t) * (0.6 + 0.4 * math.sin(TAU * t + i))
    return a * (1.0 if i % 2 == 0 else -0.8)


def pose_gauges(t):
    for o, m0, loc, ax, i in TWITCH:
        a = math.radians(needle_angle(t, i)) if t else 0.0
        o.matrix_basis = Matrix.Translation(loc) @ Matrix.Rotation(a, 4, ax) @ Matrix.Translation(-loc) @ m0


# ===================================================================== the agitator drive
DRIVE = None
if BUILD in ("drive", "all", "test"):
    for o in objs_under(CAP["head_coupling"]):
        o.hide_render = True
    ZB = H + 0.66
    C1, R1 = Vector((RX - 0.1, RY - 0.05)), 0.3
    C2, R2 = Vector((RX + 0.36, RY + 0.34)), 0.12
    # the shaft out of the gearbox, a bearing collar, the motor's stub shaft
    cyl((C1.x, C1.y, H + 0.6), 0.055, 0.34, "bare", verts=20)
    cyl((C1.x, C1.y, H + 0.47), 0.1, 0.06, "dark_steel", verts=24)
    bolts(C1.x, C1.y, H + 0.505, 0.08, 6, r=0.014)
    cyl((C2.x, C2.y, H + 0.63), 0.04, 0.1, "bare", verts=16)

    def pulley(c, r, spokes, rim_mat, spoke_mat, h):
        root = bpy.data.objects.new("pulley", None)
        sc.collection.objects.link(root)
        root.parent = ROOT
        root.location = (c.x, c.y, ZB)
        annulus((0, 0, 0), r - 0.045, r, h, rim_mat, parent=root)
        torus((0, 0, h / 2), r - 0.02, 0.008, "bare", seg=48, parent=root)          # a worn bright lip
        cyl((0, 0, 0), r * 0.3, h + 0.02, "dark_steel", verts=24, parent=root)
        for i in range(spokes):
            a = TAU * i / spokes
            rr = (r * 0.3 + r - 0.045) / 2
            box((rr * math.cos(a), rr * math.sin(a), 0), (r - 0.045 - r * 0.3 + 0.02, r * 0.22, h * 0.7), spoke_mat,
                rz=a, bevel=0.006, parent=root)
        cyl((0, 0, h / 2 + 0.012), 0.035, 0.03, "bare", verts=6, bevel=0, parent=root)   # the shaft nut
        return root

    P1 = pulley(C1, R1, 5, "yellow", "yellow", 0.07)
    P2 = pulley(C2, R2, 3, "dark_steel", "yellow", 0.06)
    # an open flat belt: tangents of the two rims, the big arc on the far side of C1
    rb1, rb2 = R1 + 0.018, R2 + 0.018
    dv = C2 - C1
    dist, phi = dv.length, math.atan2(dv.y, dv.x)
    beta = math.acos((rb1 - rb2) / dist)
    pts = []

    def arc(c, r, a0, a1, n):
        for k in range(n):
            a = a0 + (a1 - a0) * k / n
            pts.append(Vector((c.x + r * math.cos(a), c.y + r * math.sin(a), ZB)))

    def line(p, q, n):
        for k in range(n):
            pts.append(p.lerp(q, k / n))

    pc = lambda c, r, a: Vector((c.x + r * math.cos(a), c.y + r * math.sin(a), ZB))  # noqa: E731
    line(pc(C1, rb1, phi + beta), pc(C2, rb2, phi + beta), 40)
    arc(C2, rb2, phi + beta, phi - beta, 40)
    line(pc(C2, rb2, phi - beta), pc(C1, rb1, phi - beta), 40)
    arc(C1, rb1, phi - beta, phi + beta - TAU, 120)
    seglen = [(pts[(i + 1) % len(pts)] - pts[i]).length for i in range(len(pts))]
    LB = sum(seglen)
    # the belt: a flat strip, 0.055 tall, 0.02 thick
    me = bpy.data.meshes.new("belt")
    import bmesh as _bm
    bm = _bm.new()
    rings = []
    for i, p in enumerate(pts):
        tng = (pts[(i + 1) % len(pts)] - pts[i - 1]).normalized()
        nrm = Vector((tng.y, -tng.x, 0))
        rings.append([bm.verts.new(p + nrm * sx + Vector((0, 0, sz))) for sx, sz in
                      ((-0.01, -0.028), (0.01, -0.028), (0.01, 0.028), (-0.01, 0.028))])
    for i in range(len(rings)):
        a_, b_ = rings[i], rings[(i + 1) % len(rings)]
        for k in range(4):
            j = (k + 1) % 4
            bm.faces.new((a_[k], a_[j], b_[j], b_[k]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    belt = bpy.data.objects.new("belt", me)
    sc.collection.objects.link(belt)
    _finish(belt, "hose_k", 0, smooth=True)
    TRAVEL = R1 * TAU * 2 / 5               # belt travel a loop: the big pulley turns two spoke steps
    NCLIP = max(2, round(LB / TRAVEL))
    # a lacing clip: 0.05 along the belt, over its 0.02 thickness, across its height. Before the
    # fixes each was turned a quarter, its 0.05 standing radial, and cut 0.007 into both rims
    CLIPS = [box((0, 0, 0), (0.05, 0.03 if BEFORE else 0.026, 0.062), "bare", bevel=0.004) for _ in range(NCLIP)]
    cum = [0.0]
    for s_ in seglen:
        cum.append(cum[-1] + s_)

    def at_s(s):
        s %= LB
        lo, hi = 0, len(pts)
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if cum[mid] <= s:
                lo = mid
            else:
                hi = mid
        a_, b_ = pts[lo], pts[(lo + 1) % len(pts)]
        u = (s - cum[lo]) / max(seglen[lo], 1e-9)
        return a_.lerp(b_, u), (b_ - a_).normalized()

    P1_M0, P2_M0 = P1.matrix_basis.copy(), P2.matrix_basis.copy()
    print(f"drive: belt {LB:.3f} tiles, {NCLIP} clips, small pulley {TRAVEL / R2 / TAU:.3f} turns a loop")

    def pose_drive(t):
        P1.matrix_basis = P1_M0 @ Matrix.Rotation(-TAU * 2 / 5 * t, 4, "Z")
        P2.matrix_basis = P2_M0 @ Matrix.Rotation(-TRAVEL / R2 * t, 4, "Z")
        for i, c in enumerate(CLIPS):
            p, tg = at_s(LB * (i / NCLIP + t / NCLIP))
            c.location = p
            c.rotation_euler = (0, 0, math.atan2(tg.y, tg.x) + (PI / 2 if BEFORE else 0.0))
    DRIVE = pose_drive

# ===================================================================== the vent condenser drip
DRIP = None
if BUILD in ("drip", "all", "test"):
    TX, TY, TR = 2.04, 1.92, 0.4
    M["water"] = bpy.data.materials.new("water")
    wm = M["water"]
    wm.use_nodes = True
    wb = wm.node_tree.nodes["Principled BSDF"]
    wb.inputs["Base Color"].default_value = rig.srgb("#BFD0D4")
    wb.inputs["Roughness"].default_value = 0.05
    wb.inputs["Coat Weight"].default_value = 1.0
    wb.inputs["Specular IOR Level"].default_value = 1.0
    M["wet"] = bpy.data.materials.new("wet")
    wt = M["wet"]
    wt.use_nodes = True
    tb = wt.node_tree.nodes["Principled BSDF"]
    tb.inputs["Base Color"].default_value = rig.srgb("#2A2622")
    tb.inputs["Roughness"].default_value = 0.12
    tb.inputs["Alpha"].default_value = 0.4
    # a drain cock on the condenser's flank, turned down, a brass plug-cock; the drops fall
    # clear to the ground. Before the fixes it stood on the east flank (-0.2 rad) 0.14 out:
    # its lip reached x 2.60, 0.1 tile (6 px) past the footprint's east edge, the drops fell
    # and the wet patch lay outside the building, and a bead ran through its pipe. Now it is
    # on the south-east flank, the face the camera sees, 0.11 out, all of it inside the edge
    # and the drops clear of the foot ring.
    DA, REACH = (-0.2, 0.14) if BEFORE else (-0.75, 0.11)
    dp = Vector((TX + (TR + 0.0) * math.cos(DA), TY + TR * math.sin(DA), 0.0))
    out = Vector((math.cos(DA), math.sin(DA), 0))
    Z_COCK = 1.0
    k_ = REACH / 0.14
    cyl(tuple(dp + out * 0.06 * k_ + Vector((0, 0, Z_COCK))), 0.03, 0.14 * k_, "copper", rot=along(out), verts=16)
    cyl(tuple(dp + out * 0.1 * k_ + Vector((0, 0, Z_COCK + 0.035))), 0.025, 0.05, "brass", verts=6, bevel=0)
    tip = dp + out * REACH
    cyl(tuple(tip + Vector((0, 0, Z_COCK - 0.05))), 0.028, 0.1, "copper", verts=16)
    lip = tip + Vector((0, 0, Z_COCK - 0.1))
    # the wet patch under it, glossy (before: 0.22 x 0.16, half of it past the edge)
    bpy.ops.mesh.primitive_circle_add(vertices=24, radius=0.08 if BEFORE else 0.05, fill_type="NGON",
                                      location=(lip.x, lip.y, 0.003))
    wp = bpy.context.active_object
    wp.scale = (1.4, 1.0, 1) if BEFORE else (1.0, 1.3, 1)
    _finish(wp, "wet", 0)
    print(f"drain cock lip at x {lip.x + 0.028:.3f} (the east edge is 2.5), wet patch to x {lip.x + wp.scale[0] * (0.08 if BEFORE else 0.05):.3f}")
    # drops: two a loop, each falls the 0.9 tile from the lip to the ground in 6 frames of 24 (gravity at 14 fps)
    DROPS = [sphere((0, 0, 0), 0.018, "water", scale=(1, 1, 1.4), seg=10) for _ in range(2)]
    # beads: running down the copper flank from under the upper band, slowing, wrapping
    BEADS = []
    # before the fixes three started above the upper band (z 1.31-1.39) and ran down through
    # it, and one crossed the cock's pipe; now all four start under the band's lower edge,
    # stop above the lower band, and keep 0.1 tile round the flank from the cock and the rivets
    RUNS_B = ((-0.5, 1.5, 0.95, 0.0), (-0.05, 1.48, 1.05, 0.5), (0.25, 1.45, 0.9, 0.25), (-0.3, 1.3, 0.85, 0.7)) \
        if BEFORE else \
        ((-0.4, 1.28, 0.86, 0.0), (-0.05, 1.27, 0.95, 0.5), (0.25, 1.26, 0.84, 0.25), (-1.3, 1.25, 0.88, 0.7))
    for i, (a, z0, z1, ph) in enumerate(RUNS_B):
        BEADS.append((sphere((0, 0, 0), 0.015, "water", scale=(1, 1, 1.6), seg=10), a, z0, z1, ph))

    def pose_drip(t):
        for j, o in enumerate(DROPS):
            u = round(t * 24 - j * 12) % 24     # frames since this drop let go
            if 0 < u <= 6 and t:
                s = (u / 6) ** 2
                o.location = (lip.x, lip.y, (lip.z - 0.02) * (1 - s) + 0.01)
                o.hide_render = False
            elif u == 0 or u > 22 or not t:     # swelling on the lip
                o.location = (lip.x, lip.y, lip.z - (0.02 if BEFORE else 0.024))
                o.hide_render = j != 0
            else:
                o.hide_render = True
        for o, a, z0, z1, ph in BEADS:
            u = (ph + t) % 1.0
            z = z0 + (z1 - z0) * (u ** 1.3)
            rr = TR + 0.008
            o.location = (TX + rr * math.cos(a), TY + rr * math.sin(a), z)
    DRIP = pose_drip

# ===================================================================== passes
rig.camera(*CANVAS, centre_px=CENTRE, ss=SSK)
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()


def set_legs(t):
    for p in LEG_POSES:
        p(t)
    for node, k in PHASES:
        node.outputs[0].default_value = 2 * math.pi * k * t


def set_couplings(t):
    for p in CPL_POSES:
        p(t)


def frame_state(f):
    """(legs t, couplings t, press k, gauges t, drive t, drip t) for frame f of MODE."""
    z = (0.0, 0.0, 0, 0.0, 0.0, 0.0)
    if MODE == "current":
        return (f / 24, f / 24, 0, 0.0, 0.0, 0.0)
    if MODE == "press":
        return (0.0, 0.0, f, 0.0, 0.0, 0.0)
    if MODE in ("gauges", "gauges_big"):
        return (0.0, 0.0, 0, f / 24, 0.0, 0.0)
    if MODE == "drive":
        return (0.0, 0.0, 0, 0.0, f / 24, 0.0)
    if MODE == "drip":
        return (0.0, 0.0, 0, 0.0, 0.0, f / 24)
    if BUILD == "all":
        t = (f % 24) / 24
        k = f - 24 if 24 <= f < 40 else 0
        return (t, t, k, t, t, t)
    return z


def apply(state):
    lt, ct, k, gt, dt, wt = state
    set_legs(lt)
    set_couplings(ct)
    pose_press(k)
    pose_gauges(gt)
    if DRIVE:
        DRIVE(dt)
    if DRIP:
        DRIP(wt)


def working(on):
    for sock, v in GLOWS:
        sock.default_value = v if on else 0.0
    LAMP_ON.default_value = 3.0 if on else 0.0


# ===================================================================== --mode collide
# No render. Builds what "all" builds and checks, in every one of its 48 frames:
#   moving   every moving part (couplings, leg particles, press follower and its flexed
#            hose, the cake, needles, pulleys, belt clips, drops, beads) against every
#            fixed part shown that frame, and against every other moving group;
#   added    every part the previews add or change that does not move (the drive's shaft
#            and belt, the drain cock and wet patch, the double-size dials) against the
#            fixed model;
#   model    round 5's whole fixed model, every part against every other (most of these
#            are a part seated on or let into its host: listed in <out>/collide-model.txt).
# A clash is two parts' faces crossing, or one part wholly inside a closed part. Pairs
# meant to touch -- a part on the part it is fastened to -- are listed as "meant" by MEANT.
def collide_check():
    from mathutils.bvhtree import BVHTree
    lines = []

    def out(s):
        print(s)
        lines.append(s)

    def alive(o):
        try:
            o.name
            return True
        except ReferenceError:
            return False

    RI = ROOT.matrix_world.inverted()

    def mat_of(o):
        return o.data.materials[0].name if getattr(o.data, "materials", None) and o.data.materials else "-"

    def where(o, vs):
        c = sum(vs, Vector()) / len(vs)
        c = RI @ c
        return f"({c.x:+.2f},{c.y:+.2f},{c.z:.2f})"

    def world_mesh(o):
        dg = bpy.context.evaluated_depsgraph_get()
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ev.matrix_world
        vs = [mw @ v.co for v in me.vertices]
        ps = [tuple(p.vertices) for p in me.polygons]
        ev.to_mesh_clear()
        return vs, ps

    def aabb(vs):
        xs, ys, zs = zip(*vs)
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    def meet(a, b, m=0.0):
        return all(a[0][i] <= b[1][i] + m and b[0][i] <= a[1][i] + m for i in range(3))

    def inside(tree, p):
        d = Vector((0.5774, 0.5771, 0.5777))
        n, o = 0, p.copy()
        for _ in range(64):
            hit = tree.ray_cast(o, d)
            if hit[0] is None:
                break
            n += 1
            o = hit[0] + d * 1e-5
        return n % 2 == 1

    class Part:
        def __init__(self, o, label):
            self.o, self.label = o, label
            self.vs, ps = world_mesh(o)
            self.box = aabb(self.vs) if self.vs else None
            self.tree = BVHTree.FromPolygons(self.vs, ps) if ps else None
            self.c = sum(self.vs, Vector()) / len(self.vs) if self.vs else None
            self.desc = f"{o.name}[{mat_of(o)}] at {where(o, self.vs)}" if self.vs else o.name

    def clash(a, b):
        if a.tree is None or b.tree is None or not meet(a.box, b.box):
            return None
        if a.tree.overlap(b.tree):
            return "cross"
        # no faces cross: either one is wholly inside the other, or they are apart (a vertex,
        # not the centre, is tested: a ring's centre is in its hole)
        if meet(b.box, (a.vs[0], a.vs[0])) and inside(b.tree, a.vs[0]):
            return "inside"
        if meet(a.box, (b.vs[0], b.vs[0])) and inside(a.tree, b.vs[0]):
            return "contains"
        return None

    # which parts move, and in which group
    states = [frame_state(f) for f in range(48)]
    m0 = {}
    moving = set()
    for f, st in enumerate(states):
        apply(st)
        bpy.context.view_layer.update()
        for o in OBJS:
            if not alive(o) or o in _hose_live:
                continue
            m = o.matrix_world.copy()
            if o.name not in m0:
                m0[o.name] = m
            elif any(abs(m[i][j] - m0[o.name][i][j]) > 1e-6 for i in range(4) for j in range(4)):
                moving.add(o.name)
    named = {}
    for key, objs in (("press follower", [o for o, _ in FOLLOWER]), ("press pack", [o for o, _ in PACK]),
                      ("needle", [t[0] for t in TWITCH]),
                      ("cake", [CAKE] if CAKE else []), ("belt clip", CLIPS if DRIVE else []),
                      ("drop", DROPS if DRIP else []), ("bead", [b[0] for b in BEADS] if DRIP else [])):
        for o in objs:
            named[o.name] = key
    if CAKE:
        moving.add(CAKE.name)

    def group(o):
        if o in _hose_live:
            return "feed hose (flexed)"
        if o.name in named:
            return named[o.name]
        p = o.parent
        while p is not None and p != ROOT:
            if p.name.startswith("coupling"):
                q = RI @ p.matrix_world.translation
                return f"coupling at ({q.x:+.2f},{q.y:+.2f},{q.z:.2f})"
            if p.name.startswith("pulley"):
                return "drive pulley " + ("big" if p == P1 else "small")
            p = p.parent
        return "leg particle"

    import re as _re

    def meant(g, a, b):
        for gr, ar, br, why in MEANT:
            if _re.search(gr, g) and _re.search(ar, a) and _re.search(br, b):
                return why
        return None

    stains = set(o.name for o in STAINS)
    out(f"COLLIDE mode all, {'before the fixes' if BEFORE else 'fixed'}; 48 frames; {len(moving)} moving objects")
    fixed_cache = {}
    hits = {}            # (group, moving desc, other desc, kind) -> frames
    for f, st in enumerate(states):
        apply(st)
        bpy.context.view_layer.update()
        live = [o for o in OBJS if alive(o) and o.type == "MESH" and not o.hide_render and o.name not in stains]
        mv = [o for o in live if o.name in moving or o in _hose_live]
        fx = [o for o in live if not (o.name in moving or o in _hose_live)]
        for o in fx:
            if o.name not in fixed_cache:
                fixed_cache[o.name] = Part(o, "fixed")
        mparts = [Part(o, group(o)) for o in mv]
        for a in mparts:
            for o in fx:
                b = fixed_cache[o.name]
                k = clash(a, b)
                if k:
                    hits.setdefault((a.label, a.desc if a.label != "leg particle" else "particle", b.desc, k),
                                    []).append(f)
        for i, a in enumerate(mparts):
            for b in mparts[i + 1:]:
                if a.label == b.label:
                    continue
                k = clash(a, b)
                if k:
                    hits.setdefault((a.label, a.desc, b.label + ": " + b.desc, k), []).append(f)
    n_meant = n_clash = 0
    for (g, ad, bd, k), fs in sorted(hits.items()):
        why = meant(g, ad, bd)
        tag = "meant" if why else "CLASH"
        n_meant += tag == "meant"
        n_clash += tag == "CLASH"
        fr = f"{fs[0]}-{fs[-1]}" if fs == list(range(fs[0], fs[-1] + 1)) else ",".join(map(str, fs))
        out(f"COLLIDE {tag} moving [{g}] {ad} x {bd}: {k}, frames {fr}" + (f"  ({why})" if why else ""))
    out(f"COLLIDE moving: {n_clash} clashes, {n_meant} meant contacts")

    # the previews' fixed additions and the double-size dials, against the fixed model
    apply(states[0])
    bpy.context.view_layer.update()
    added = [o for o in OBJS[N_R5:] if alive(o) and o.name not in moving and not o.hide_render
             and o.type == "MESH"] + [o for o in CAP.get("big_gauges", []) if o.name not in moving]
    addn = set(o.name for o in added)
    rest = [fixed_cache[n] for n in fixed_cache if n not in addn and not fixed_cache[n].o.hide_render]
    n_a = 0
    for o in added:
        a = fixed_cache.get(o.name) or Part(o, "added")
        for b in rest:
            k = clash(a, b)
            if k:
                why = meant("added", a.desc, b.desc)
                tag = "meant" if why else "CLASH"
                n_a += tag == "CLASH"
                out(f"COLLIDE {tag} added {a.desc} x {b.desc}: {k}" + (f"  ({why})" if why else ""))
    out(f"COLLIDE added: {len(added)} parts, {n_a} clashes")

    # round 5's whole fixed model, pair by pair: written out, counted here
    model = [p for p in rest]
    pairs = []
    for i, a in enumerate(model):
        for b in model[i + 1:]:
            k = clash(a, b)
            if k:
                pairs.append(f"{a.desc} x {b.desc}: {k}")
    open(os.path.join(OUT, "collide-model.txt"), "w").write("\n".join(pairs) + "\n")
    out(f"COLLIDE model: {len(model)} fixed parts, {len(pairs)} touching pairs (collide-model.txt)")
    open(os.path.join(OUT, "collide.txt"), "w").write("\n".join(lines) + "\n")


# (group, this part, the other part: regexes on their descriptions "name[material] at (x,y,z)",
# why): contacts that are the design -- a part on, in or against what it is fastened to.
# Every other crossing is a CLASH. Coordinates are tiles, model space.
_C = r"\(\+2\.04,\+1\.92"                  # the vent condenser's shell, foot ring and bands
MEANT = [
    (r"^needle$", "", r"\[(brass|gauge)\]", "a needle on its own dial"),
    (r"^bead$", "", r"Cylinder\.\d+\[copper\] at " + _C, "a bead running on the condenser's wall"),
    (r"^drop$", "", r"\[wet\]", "a drop landing in its wet patch"),
    (r"^drop$", "", r"\[copper\] at \(\+2\.[34]", "a drop swelling on the cock's lip"),
    (r"^added$", r"\[wet\]", r"Cylinder\.\d+\[dark_steel\] at " + _C + r",0\.07", "the wet patch run in under the foot ring"),
    (r"^added$", r"\[bare\] at ", r"\[(lead|oxide|seam)\]", "a double dial's stem into its vessel's wall"),
    (r"^press pack$", r"Cube\.101", r"^cake: ", "the cake on the leaf it peels off"),
    (r"^belt clip$", "", r"^belt\[", "a lacing clip on the belt"),
    (r"^drive pulley", "", r"\[bare\] at \(\+1\.(20|66)", "a pulley on its shaft"),
    (r"^leg particle$", "", r"\[(glass|fl_f\d)\]", "a fleck or bubble in the solution, inside the glass"),
    (r"^leg particle$", "", r"\[bare\] at \((-0\.32,\+0\.62|\+0\.12,-0\.72),1\.43\)",
     "inside the glass, behind the leg's middle band"),
    (r"^leg particle$", "", r"\[(bare|brass|hose|hose_k)\] at \((-0\.5|-0\.6|\+0\.2|\+0\.5)",
     "inside the glass, past the end of a hose let into the leg (round 5)"),
    (r"^press pack$", "", r"Cube\.\d+\[bare\] at \(-1\.\d+,-(2\.28|1\.68),1\.18\)",
     "the leaves and tail stand riding on the side rails"),
    (r"^press pack$", r"Cube\.101", r"Cube\.102\[dark_steel\]|press follower", "the last leaf shut against the head"),
    (r"^press pack$", "", r"press follower: Cube\.102", "the last leaf shut against the head"),
    (r"^cake$", "", r"Cube\.101\[cream\]|press pack: Cube\.101", "the cake on the leaf it peels off"),
    (r"^cake$", "", r"\[(lead|dark_steel|dark)\] at \(-(1\.02|0\.89),-1\.98,0\.(27|56|58)",
     "the cake dropping through the chute mouth into the drop box"),
    (r"^added$", r"\[bare\] at \(\+1\.(20|66)", r"\[(dark_steel|green)\]", "a shaft out of its gearbox or motor"),
    (r"^added$", r"\[copper\] at \(\+2\.3", r"Cylinder\.\d+\[copper\] at " + _C, "the drain cock let into the shell"),
    (r"^added$", r"\[dark\] at \(-0\.89", r"\[(dark_steel|lead)\] at \(-1\.02", "the chute mouth in the drop box's lid"),
    (r"^added$", r"\[(brass|gauge)\]", r"\[(lead|oxide|brass|gauge)\]", "a dial on its vessel's wall"),
]

if MODE == "collide":
    collide_check()
    print("done")
    sys.exit(0)

NFR = {"current": 24, "press": 16, "gauges": 24, "gauges_big": 24, "drive": 24, "drip": 24, "all": 48, "test": 0}[MODE]
if MODE == "test":
    apply((0, 0, 7, 0, 0.3, 3 / 24))
    working(True)
    GROUND.hide_render = True
    rig.render(os.path.join(OUT, "test.png"))
    print("done")
    sys.exit(0)

lo, hi = (0, NFR) if not FRANGE else map(int, FRANGE.split(":"))
if lo == 0:
    apply(frame_state(0))
    working(False)
    rig.render(os.path.join(OUT, "idle.png"))
    working(True)
    GROUND.hide_render = True
    rig.render(os.path.join(OUT, "plate.png"))
    GROUND.hide_render = False
working(True)
for f in range(lo, hi):
    apply(frame_state(f))
    rig.render(os.path.join(OUT, f"working-{f:02d}.png"))
print("done")
