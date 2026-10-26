"""Test model: the test box with runs and fittings recorded (runs.py), for render.sh --collide.

  SAE_TEST_ENDS=<case> tools/blender/render.sh tools/blender/test/ends_box.py <out-dir> --collide
                                               [--collide-allow <pattern> ...]

Without --collide it is box.py, run as it stands (box.py's docstring), whatever the case.

With --collide it renders nothing. It runs collide_box.py's --collide first -- the box built,
its slider checked, its two lines printed -- then adds the case's parts beside the box and
calls runs.check on the box's parts and those, printing runs.py's lines (its docstring). The
parts, in the box's space (tiles; the block's east wall at x 0.8, the plinth's top at z 0.08,
its edge at 0.995, the ground z 0):

  the nozzle   a recorded fitting on the block's east wall, its axis west (into the wall): a
               cylinder r 0.05 from x 0.80 to 0.86 at (y -0.3, z 0.35)
  the hose     a run, r 0.03, from in the nozzle (x 0.845) east, along and down to its own
               ferrule standing on the plinth's top at (0.9, 0.3), arriving from above

SAE_TEST_ENDS (the case; default fitted), and what the run prints after the box's own lines:

  fitted        the nozzle and the hose: no clash ("ends: 0", "body: 0", "ground: 0")
  loose         the hose's far end stops in the air at (0.93, 0.30, 0.45), no ferrule:
                LOOSE hose end 1 ... x nothing: no fitting within 0.02
  short         its near end 0.05 east of the nozzle: LOOSE hose end 0 ... no fitting
  side          its near end on the block's bare wall at y -0.6: LOOSE hose end 0 ... x
                <the block>: a bare end on <the block>: no fitting within 0.02
  narrow        the nozzle r 0.02, under 0.9 of the hose's width: LOOSE hose end 0 ... narrower
  tangent       its far end arriving along the plinth's top, not down into it: LOOSE hose
                end 1 ... does not face into what it serves
  axis          its near end arriving 45 degrees off the nozzle's axis: LOOSE hose end 0 ...
                arrives 45 deg off nozzle's axis
  buried        its near end 0.2 inside the block, its ferrule with it, at y -0.6: LOOSE hose
                end 0 ... buried in <the block>, and BODY hose x <the block>
  floating      the nozzle 0.1 off the wall, on nothing: LOOSE hose end 0 ... nozzle on no host
  body          a rung 0.008 thick standing across the hose: BODY hose x rung ... deep
  ground        a post from z -0.05 by the plinth: BELOW post ... x ground: 0.050 deep
  ground-ok     the same post, below_ok ("a footing poured into the ground"): a below_ok line,
                no clash
  ground-moving a plunger by the plinth whose four frames stand its foot at z 0.05, 0.02,
                -0.02 and 0.03: BELOW plunger ... 0.020 deep, frames 2
  into-ground   the fitted hose and a trunk, r 0.025, from its own gland on the wall down into
                a conduit collar standing on the ground (a ground fitting): no clash
  host-moves    the fitted hose, its nozzle on a pivot that takes it 0.3 east from frame 1 on (four
                frames; the hose itself never moves): LOOSE hose end 0 ... no fitting, frames 1-3
  shown-later   the fitted hose, and a post from z -0.15 that is hidden in frame 0 and shown in
                frames 1-3: BELOW post ... 0.150 deep, frames 1-3
  tee           the fitted hose with a stub standing on its body, recorded as a tee on it, and a
                branch, r 0.015, from a second nozzle through the stub down into a ground collar:
                the hose is not tested against the stub, the branch is: BODY branch x stub only
  untestable    the fitted hose, and a run whose one object is a curve with no bevel (no faces):
                UNTESTED wire x nothing ..., "untested: 1 clashes"
  unchecked     the nozzle and the hose recorded, runs.check never called: the exit line
                "runs not checked: 2 clashes"
  untagged      nothing recorded and runs.check not called: collide_box.py's two lines alone

test/test_ends.py runs every case and holds each to these lines and to the verdict
measure.py's collide step gives (render.sh's exit status).
"""
import math
import os
import runpy
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import runs  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
CASES = ("fitted", "loose", "short", "side", "narrow", "tangent", "axis", "buried", "floating", "body",
         "ground", "ground-ok", "ground-moving", "into-ground", "host-moves", "shown-later", "tee", "untestable",
         "unchecked", "untagged")
CASE = os.environ.get("SAE_TEST_ENDS", "fitted")
R_HOSE, R_TRUNK, R_BRANCH = 0.03, 0.025, 0.015
HOST_SHIFT = 0.3                                   # how far east the host-moves case's pivot takes the nozzle
PLUNGER_FOOT = (0.05, 0.02, -0.02, 0.03)          # the plunger's foot, frame by frame


def box_scene():
    """collide_box.py's --collide (its lines printed), and box.py's globals from inside it."""
    got = {}
    run_path = runpy.run_path

    def grab(path, *a, **k):
        g = run_path(path, *a, **k)
        if os.path.basename(path) == "box.py":
            got.update(g)
        return g
    runpy.run_path = grab
    try:
        run_path(os.path.join(HERE, "collide_box.py"), run_name="__main__")
    finally:
        runpy.run_path = run_path
    return got


def tube(name, pts, r, seg=12):
    """A capped tube swept along the polyline pts (densified to 0.01), smooth: a run's body."""
    P = [Vector(pts[0])]
    for a, b in zip(pts, pts[1:]):
        a, b = Vector(a), Vector(b)
        n = max(1, int((b - a).length / 0.01))
        P += [a.lerp(b, i / n) for i in range(1, n + 1)]
    bm = bmesh.new()
    rings = []
    up = Vector((0, 0, 1))
    for i, p in enumerate(P):
        t = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
        u = t.cross(up if abs(t.dot(up)) < 0.9 else Vector((1, 0, 0))).normalized()
        v = t.cross(u)
        rings.append([bm.verts.new(p + r * (u * math.cos(2 * math.pi * k / seg) + v * math.sin(2 * math.pi * k / seg)))
                      for k in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for k in range(seg):
            bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bm.normal_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for poly in me.polygons:
        poly.use_smooth = True
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return o


def collide():
    B = box_scene()
    part = B["part"]
    added = []

    def add(o, mat, name):
        o.name = name
        part(o, mat, "ends")
        added.append(o)
        return o

    def cyl(name, loc, r, h, mat, axis="z"):
        rot = {"x": (0, math.pi / 2, 0), "y": (math.pi / 2, 0, 0), "z": (0, 0, 0)}[axis]
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=r, depth=h, location=loc, rotation=rot)
        return add(bpy.context.active_object, mat, name)

    def block(name, loc, size, mat):
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
        o = bpy.context.active_object
        o.scale = size
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        return add(o, mat, name)

    def hose(pts, ferrule0=None, ferrule1=None):
        body = add(tube("hose", pts, R_HOSE), "cap", "hose")
        f0 = [ferrule0()] if ferrule0 else []
        f1 = [ferrule1()] if ferrule1 else []
        runs.run([body] + f0 + f1, pts, R_HOSE, "hose", "hose", end_fit=(f0, f1))
        return body

    def ferrule_down():          # the far end's ferrule, standing on the plinth's top round the hose
        return cyl("ferrule", (0.9, 0.3, 0.10), 0.04, 0.04, "steel")

    far = [(0.93, 0.0, 0.3), (0.9, 0.3, 0.2), (0.9, 0.3, 0.10)]
    if CASE == "untagged":
        return
    if CASE != "floating":
        nozzle = cyl("nozzle", (0.83, -0.3, 0.35), 0.02 if CASE == "narrow" else 0.05, 0.06, "steel", "x")
    else:
        nozzle = cyl("nozzle", (0.93, -0.3, 0.35), 0.05, 0.06, "steel", "x")
    pivot = None
    if CASE == "host-moves":                    # the nozzle on a pivot, at the box's origin in frame 0
        pivot = bpy.data.objects.new("pivot", None)
        bpy.context.scene.collection.objects.link(pivot)
        pivot.parent = B["ROOT"]
        nozzle.parent = pivot
    runs.fitting([nozzle], "nozzle", axis=(-1, 0, 0), frame=pivot)
    if CASE == "loose":
        hose([(0.845, -0.3, 0.35), (0.93, -0.3, 0.35), (0.93, 0.0, 0.4), (0.93, 0.3, 0.45)])
    elif CASE == "short":
        hose([(0.91, -0.3, 0.35), (0.95, -0.3, 0.35), (0.95, 0.0, 0.3), (0.9, 0.3, 0.2), (0.9, 0.3, 0.10)],
             ferrule1=ferrule_down)
    elif CASE == "side":
        hose([(0.80, -0.6, 0.35), (0.93, -0.6, 0.35)] + far, ferrule1=ferrule_down)
    elif CASE == "tangent":
        hose([(0.845, -0.3, 0.35), (0.93, -0.3, 0.35), (0.93, 0.1, 0.12), (0.93, 0.3, 0.12)],
             ferrule1=lambda: cyl("ferrule", (0.93, 0.3, 0.12), 0.04, 0.06, "steel", "y"))
    elif CASE == "axis":
        hose([(0.845, -0.3, 0.35), (0.91, -0.235, 0.35), (0.95, 0.0, 0.3), (0.9, 0.3, 0.2), (0.9, 0.3, 0.10)],
             ferrule1=ferrule_down)
    elif CASE == "buried":
        hose([(0.6, -0.6, 0.35), (0.93, -0.6, 0.35)] + far,
             ferrule0=lambda: cyl("ferrule", (0.62, -0.6, 0.35), 0.04, 0.04, "steel", "x"), ferrule1=ferrule_down)
    elif CASE == "floating":
        hose([(0.915, -0.3, 0.35), (1.0, -0.3, 0.35), (1.0, 0.0, 0.3), (0.9, 0.3, 0.2), (0.9, 0.3, 0.10)],
             ferrule1=ferrule_down)
    else:                                       # the fitted hose: every other case has it
        hose([(0.845, -0.3, 0.35), (0.93, -0.3, 0.35)] + far, ferrule1=ferrule_down)
    frames, pose, moving = None, None, ()
    # box.py ran to its end with its renders made no-op, so its last setup() hid every part: all
    # of the machine is drawn here (the wreck is not in PARTS), but where a case says otherwise
    shown = lambda o: True                       # noqa: E731
    if CASE == "body":
        block("rung", (0.93, -0.15, 0.325), (0.12, 0.008, 0.12), "steel")
    elif CASE in ("ground", "ground-ok"):
        post = block("post", (1.3, -0.6, 0.075), (0.06, 0.06, 0.25), "steel")
        if CASE == "ground-ok":
            runs.below_ok([post], "a footing poured into the ground")
    elif CASE == "ground-moving":
        plunger = block("plunger", (1.3, 0.6, PLUNGER_FOOT[0] + 0.03), (0.06, 0.06, 0.06), "steel")

        def pose(f):
            plunger.location.z = PLUNGER_FOOT[f] + 0.03
        frames, moving = range(len(PLUNGER_FOOT)), {plunger.name}
    elif CASE == "host-moves":
        def pose(f):                            # the pivot takes the nozzle 0.3 east from frame 1 on
            pivot.location.x = 0.0 if f == 0 else HOST_SHIFT
        frames = range(4)
    elif CASE == "shown-later":
        post = block("post", (1.3, -0.6, -0.025), (0.06, 0.06, 0.25), "steel")
        now = [0]

        def pose(f):
            now[0] = f
        frames = range(4)
        shown = lambda o: not (o.name == post.name and now[0] == 0)     # noqa: E731
    elif CASE == "tee":
        # a stub standing on the hose's body (a tee on it), and a branch through the stub to the ground
        stub = block("stub", (0.93, -0.15, 0.385), (0.05, 0.05, 0.12), "steel")
        runs.fitting([stub], "stub", tee="hose")
        nozzle2 = cyl("nozzle", (0.83, -0.15, 0.42), 0.03, 0.06, "steel", "x")
        runs.fitting([nozzle2], "nozzle2", axis=(-1, 0, 0))
        pts = [(0.845, -0.15, 0.42), (1.1, -0.15, 0.42), (1.1, -0.15, 0.04)]
        branch = add(tube("branch", pts, R_BRANCH), "cap", "branch")
        runs.run([branch], pts, R_BRANCH, "hose", "branch")
        collar = cyl("collar", (1.1, -0.15, 0.03), 0.04, 0.06, "steel")
        runs.fitting([collar], "collar", axis=(0, 0, -1), ground=True)
    elif CASE == "untestable":
        cu = bpy.data.curves.new("wire", "CURVE")               # no bevel: a line, no faces to test
        cu.dimensions = "3D"
        sp = cu.splines.new("POLY")
        wire_pts = [(0.81, 0.6, 0.3), (1.2, 0.6, 0.3)]
        sp.points.add(len(wire_pts) - 1)
        for pt, co in zip(sp.points, wire_pts):
            pt.co = (*co, 1)
        wire = bpy.data.objects.new("wire", cu)
        bpy.context.scene.collection.objects.link(wire)
        add(wire, "cap", "wire")
        runs.run([wire], wire_pts, 0.01, "cables", "wire")
    elif CASE == "unchecked":
        return                                  # recorded, never checked: runs.py's exit line fails it
    elif CASE == "into-ground":
        gland = cyl("gland", (0.81, 0.4, 0.3), 0.035, 0.02, "steel", "x")
        trunk = add(tube("trunk", [(0.815, 0.4, 0.3), (1.2, 0.4, 0.3), (1.2, 0.4, 0.04)], R_TRUNK), "cap", "trunk")
        runs.run([trunk, gland], [(0.815, 0.4, 0.3), (1.2, 0.4, 0.3), (1.2, 0.4, 0.04)], R_TRUNK, "cables",
                 "trunk", end_fit=([gland], []))
        collar = cyl("collar", (1.2, 0.4, 0.03), 0.05, 0.06, "steel")
        runs.fitting([collar], "collar", axis=(0, 0, -1), ground=True)
    machine = [o for g, objs in B["PARTS"].items() for o in objs]
    runs.check(B["ROOT"], machine, pose=pose, frames=frames, moving=moving, shown=shown)


if CASE not in CASES:
    sys.exit(f"SAE_TEST_ENDS={CASE!r}: not a case; one of {', '.join(CASES)}")
if "--collide" in argv:
    collide()
else:
    runpy.run_path(os.path.join(HERE, "box.py"), run_name="__main__")
