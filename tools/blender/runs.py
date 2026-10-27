"""Runs, their fittings and the ground: a model's --collide check of what it records here.

A model's kit records, as it builds them, its runs -- every cable, bundle, hose, pipe, lagged
line or trunk -- and the fittings they land in; its --collide then calls check(), which tests
three things and prints them in the COLLIDE lines measure.py's collide step reads (pair lines
and count lines, measure.py's docstring), so a clash fails the run and a meant one can be let
through only by --collide-allow on its whole line, as any other:

  ends     every recorded run's two ends fastened (below)
  body     no recorded run passing more than BODY_DEEP into another part along its length
  ground   no part below the ground plane by more than GROUND_TOL, but those below_ok() lists

A model that calls nothing here prints nothing new: its output is what it always was.

Recording (Blender units are tiles; a point or an axis is in the space of `frame`, the object
its parts are built under -- the model's root when left out -- so a run on a moving pivot is
recorded once and tested where the pivot has taken it):

  run(objs, centreline, r, kind, name, end_fit=((), ()), frame=None)
      objs: every object the run's call built (its swept body, ties, sleeves, end fittings);
      centreline: its points in order, from end 0 to end 1; r: its outer radius (a bundle's
      overall radius); kind: "hose", "cables", "pipe", ...; name: a short label, printed, unique
      among the runs (a second run of one name raises ValueError: a tee names its run by it);
      end_fit: the objects of objs that are the run's own end fitting at end 0 and at end 1 --
      a gland, a ferrule and its nut, a flange, a collar -- () where it built none. Records
      only: builds nothing, so a render never changes. A bus bar or a bare rod is not a run:
      do not record it.
  fitting(objs, name, axis=None, ground=False, tee=None, frame=None)
      a fitting a run lands in that the run did not build: a nozzle, a wall fitting, a
      bulkhead nipple, a floor gland, a terminal's lug or stud. axis: the way a run travels
      as it goes into it (a run's outward tangent at its end), checked to AXIS_DEG; ground:
      it stands on the ground, which is then its host (a conduit collar a trunk goes down
      into); tee: the name of the recorded run whose body it stands on (a branch): that run's
      body is not tested against it, every other run's is.
  below_ok(objs, why)
      parts that go below the ground by design (a footing poured into it, piles, anchors),
      each listed with its depth and why (information), never a clash.
  reset()  forgets everything recorded (a model building twice in one process).

Whatever is recorded must be checked: when the process ends with --collide among its arguments
and something was recorded after the last check() (or none was called), it prints
  COLLIDE runs not checked follow: 0 clashes
  COLLIDE runs not checked: <n> clashes (<n> records ...)
The first line is a count of its own: it closes the block before it, so pair lines a model
printed after its last count and that --collide-allow lets through answer for that 0 and
cannot answer for the second, which no pair line answers for: the run fails rather than
passing untested.

check(root, parts, pose=None, frames=None, moving=(), shown=None, group_of=None)
  root: the model's root (rig.turntable); every figure is in its space, tiles, z up, and the
  ground is its z = 0 (rig.py: STRETCH and the turntable stand at the origin, and the ground
  catcher is the plane z = 0). parts: every mesh or curve object of the machine (not the wreck:
  its debris lies in the ground by design, and it is not tested here); recorded objects not in
  it are added. pose(f) sets frame f of `frames` (the model's own poses); with neither, the
  scene is tested as it stands. Every end, every part against the ground and every body pair is
  tested in every frame its parts are shown, so a part shown only later, or a host or fitting
  that moves away from a fixed run, is caught in the frames it happens. A part is measured
  again whenever its matrix (or the root's) has changed since it was last measured; moving
  names the objects whose mesh changes in place (a shape key, a modifier) and must be measured
  again every frame. shown(o): whether o is drawn in the frame just posed, default
  `not o.hide_render`; one not shown is not tested and is no host. Mind a model that has just
  run a render pass's setup(): it may have hidden parts the check must see (pass a shown that
  says what the plate draws). group_of(o): a key, such as the direction a part is built for
  (the Vent Pump's four variants): a run is tested only against parts of its own key.
  Call it after the model's own checks have printed their count lines, never between a pair
  line of theirs and its count: measure.py reads a count as answering for the pair lines since
  the count before it, so check()'s first count would close the model's block.

An end is fastened when, in every frame it is tested, all four hold (e the end's point, t its
outward tangent, r the run's radius):
  1. fitted    the run recorded an end fitting at it; or e is inside a recorded fitting or
               within FIT_DIST of one, and that fitting spans at least FIT_WIDTH x 2r across
               t both ways, so it covers the cut end. A bare end on a host fails.
  2. seated    that fitting is within FIT_DIST of a host: a part that is not this run's, not
               the fitting's own and not another run's (a recorded fitting on one is a host:
               a tee); or, a ground fitting, it stands on the ground. A fitting floating in the
               air fails.
  3. faces in  e + t * max(r, FIT_DIST) -- just past the end -- is inside a host, or inside the
               recorded fitting it is in, so the run goes on into what it serves; and, where
               that fitting declares an axis, t is within AXIS_DEG of it.
  4. not buried  e - t * 2r is inside no host, and some of the fitting is outside every host,
               so it can be seen.
One line an end, however many frames fail: the first frame's first failing test (its point,
host and reason, so an --collide-allow pattern stays put), and every frame that failed:
  COLLIDE LOOSE <run> end <0|1> at (x,y,z) x <host or nothing>: <why>, frames <...>
  COLLIDE ends: <n> clashes, <runs> runs, <ends> ends          (the runs and ends tested)
A recorded run none of whose parts was ever shown with polygons (hidden in every frame, a curve
with no bevel, an object with no faces) cannot be tested, and fails:
  COLLIDE UNTESTED <run> x nothing: <why>
  COLLIDE untested: <n> clashes, <runs> runs recorded

The body: a recorded run's parts but its end fittings, against every other shown part of its
key (not its own, not a tee recorded as standing on it). Where their surfaces cross, the points along the crossing
polygons' edges (at most BODY_STEP apart) and each part's vertices within the other's box; where
one lies wholly inside the other, its vertices. Those inside the other part and more than
max(2r, END_ZONE) from both of the run's ends are measured to its surface; deeper than BODY_DEEP
is a clash, one line a pair:
  COLLIDE BODY <run> x <part>: <depth> deep, frames <...>
  COLLIDE body: <n> clashes, <runs> runs                        (the runs whose body was tested)

The ground: every shown part's lowest point, its evaluated mesh in the root's space:
  COLLIDE BELOW <part> x ground: <depth> deep, frames <...>
  COLLIDE below_ok <part>: <depth> deep  (<why>)                 (information)
  COLLIDE ground: <n> clashes, <parts> parts, <k> below_ok     (the parts tested)

Last, for information: the swept tubes no run() recorded (smooth-shaded closed meshes at least
TUBE_RATIO times as long as they are thick), so a forgotten run shows:
  COLLIDE unrecorded tubes: <n> (information)[: <name>, ...]

A part is described as "<name>[<material>] at (x,y,z)", its centre in the root's space, as the
models' own checks describe theirs. An information line never names a pair or a count (no
"x" word, and no "clashes" or "overlaps" anywhere in it, not even inside a word, which
measure.py's count pattern would still read), so it neither fails a run nor answers for one.

Run with no Blender, as a script, it prints the tolerances (for a report).
"""
import atexit
import math
import re
import sys

try:
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
except ImportError:                     # the tolerances only, from plain Python
    bpy = None

FIT_DIST = 0.02          # tiles: an end within this of a fitting is in it; a fitting this close to a host is on it
FIT_WIDTH = 0.9          # a separate fitting spans at least this times the run's diameter across its end
AXIS_DEG = 30.0          # a run arrives within this of a fitting's declared axis
BODY_DEEP = 0.004        # tiles: a run's body this deep into another part is a clash (RG's DEEP_TRAY)
END_ZONE = 0.05          # tiles: at least this much of each end is the end's business, not the body's
BODY_STEP = 0.004        # tiles: the spacing of the points sampled along crossing edges
GROUND_TOL = 0.005       # tiles: a part this far below z = 0 is in the ground
TUBE_RATIO = 8.0         # an unrecorded tube: this long for its thickness
_RAY = (0.5774, 0.5771, 0.5777)   # inside tests cast this way (the models' own: off every axis)

RUNS = []
FITTINGS = []
BELOW_OK = []
_COUNT = [0, 0]         # records made, and made before the last check()


def reset():
    """Forget every run, fitting and below_ok recorded."""
    RUNS.clear()
    FITTINGS.clear()
    BELOW_OK.clear()
    _COUNT[0] = _COUNT[1] = 0


def _unchecked():
    """At exit: a failing count when records went unchecked under --collide (the module docstring)."""
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    n = _COUNT[0] - _COUNT[1]
    if n > 0 and "--collide" in argv:
        print("COLLIDE runs not checked follow: 0 clashes", flush=True)       # its own block (the docstring)
        print(f"COLLIDE runs not checked: {n} clashes ({n} records made after the last runs.check, "
              "or with none called)", flush=True)


atexit.register(_unchecked)


def _names(objs):
    return [o.name for o in objs]


def run(objs, centreline, r, kind, name, end_fit=((), ()), frame=None):
    """Record a run (the module docstring): it builds nothing."""
    pts = [tuple(p) for p in centreline]
    if len(pts) < 2:
        raise ValueError(f"run {name!r}: a centreline needs two points or more")
    if r <= 0:
        raise ValueError(f"run {name!r}: its radius must be above 0, not {r}")
    if len(end_fit) != 2:
        raise ValueError(f"run {name!r}: end_fit is (end 0's objects, end 1's), not {end_fit!r}")
    if any(rec["name"] == name for rec in RUNS):
        raise ValueError(f"run {name!r}: a run of that name is already recorded; run names must be unique "
                         "(a tee fitting names the run it stands on)")
    own = _names(objs)
    fits = (_names(end_fit[0]), _names(end_fit[1]))
    stray = [n for f in fits for n in f if n not in own]
    if stray:
        raise ValueError(f"run {name!r}: end fittings not among its objects: {stray}")
    RUNS.append(dict(objs=own, pts=pts, r=float(r), kind=kind, name=name, end_fit=fits,
                     frame=frame.name if frame is not None else None))
    _COUNT[0] += 1


def fitting(objs, name, axis=None, ground=False, tee=None, frame=None):
    """Record a fitting a run lands in (the module docstring)."""
    if not objs:
        raise ValueError(f"fitting {name!r}: no objects")
    if tee is not None and not isinstance(tee, str):
        raise ValueError(f"fitting {name!r}: tee names the run it stands on, not {tee!r}")
    FITTINGS.append(dict(objs=_names(objs), name=name, axis=tuple(axis) if axis is not None else None,
                         ground=bool(ground), tee=tee, frame=frame.name if frame is not None else None))
    _COUNT[0] += 1


def below_ok(objs, why):
    """Parts that go below the ground by design, and why (the module docstring)."""
    if not why:
        raise ValueError("below_ok: say why the parts go below the ground")
    BELOW_OK.append(dict(objs=_names(objs), why=why))
    _COUNT[0] += 1


def _quiet(text):
    """Text for an information line: no "x" word (a pair) and no "clashes" or "overlaps" (a count)."""
    text = re.sub(r"(?<!\S)x(?!\S)", "×", text)
    # anywhere, not only as a word: measure.py's COLLIDE_COUNT has no boundary before them ("foo_clashes 3")
    return re.sub(r"(clashe|overlap)(s)", r"\1(\2)", text)


def _frames_text(fs):
    fs = sorted(set(fs))
    if len(fs) > 1 and fs == list(range(fs[0], fs[-1] + 1)):
        return f"{fs[0]}-{fs[-1]}"
    return ",".join(map(str, fs))


class _Part:
    """An object's evaluated mesh in the root's space: its vertices, polygons, box and BVH."""

    def __init__(self, o, RI):
        dg = bpy.context.evaluated_depsgraph_get()
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        m = RI @ ev.matrix_world
        self.o, self.name = o, o.name
        self.vs = [m @ v.co for v in me.vertices]
        self.ps = [tuple(p.vertices) for p in me.polygons]
        self.smooth = any(p.use_smooth for p in me.polygons)
        ev.to_mesh_clear()
        self.ok = bool(self.vs and self.ps)
        mats = getattr(o.data, "materials", None)
        self.mat = mats[0].name if mats and mats[0] else "-"
        if not self.ok:
            self.desc = f"{o.name}[{self.mat}]"
            return
        self.tree = BVHTree.FromPolygons(self.vs, self.ps)
        self.lo = Vector([min(v[i] for v in self.vs) for i in range(3)])
        self.zmin = self.lo.z
        self.hi = Vector([max(v[i] for v in self.vs) for i in range(3)])
        c = (self.lo + self.hi) / 2
        self.desc = f"{o.name}[{self.mat}] at ({c.x:+.2f},{c.y:+.2f},{c.z:.2f})"

    def near(self, p, d=0.0):
        return all(self.lo[i] - d <= p[i] <= self.hi[i] + d for i in range(3))

    def boxes_meet(self, other, d=0.0):
        return all(self.lo[i] - d <= other.hi[i] and other.lo[i] - d <= self.hi[i] for i in range(3))

    def inside(self, p):
        if not self.near(p):
            return False
        ray = Vector(_RAY)
        n, o = 0, p.copy()
        for _ in range(64):
            hit = self.tree.ray_cast(o, ray)
            if hit[0] is None:
                break
            n += 1
            o = hit[0] + ray * 1e-5
        return n % 2 == 1

    def dist(self, p):
        """0 inside, else the distance to its surface."""
        if self.inside(p):
            return 0.0
        loc = self.tree.find_nearest(p)[0]
        return (loc - p).length if loc is not None else math.inf

    def depth(self, p):
        """How far p is inside: the distance to the surface (0 when outside)."""
        if not self.inside(p):
            return 0.0
        loc = self.tree.find_nearest(p)[0]
        return (loc - p).length if loc is not None else 0.0

    def touches(self, other, d):
        """The two within d of each other: their surfaces cross, one is inside the other, or a vertex
        of either is within d of the other's surface."""
        if not self.boxes_meet(other, d):
            return False
        if self.tree.overlap(other.tree):
            return True
        for a, b in ((self, other), (other, self)):
            for v in a.vs:
                if b.near(v, d):
                    hit = b.tree.find_nearest(v, d)
                    if hit[0] is not None or b.inside(v):
                        return True
        return False


def _tangent(pts, k, r):
    """End k's point and its outward tangent: from a centreline point at least r back (or the farthest)."""
    P = pts if k == 1 else pts[::-1]
    e = P[-1]
    back = P[0]
    for q in reversed(P[:-1]):
        if (e - q).length >= r:
            back = q
            break
    t = e - back
    return e, (t.normalized() if t.length > 1e-9 else Vector((0, 0, 1)))


def _span_ok(fparts, e, t, need):
    """Whether the fitting spans `need` across t both ways round e (it covers the cut end)."""
    u = t.orthogonal().normalized()
    v = t.cross(u).normalized()
    for ax in (u, v):
        ds = [(p - e).dot(ax) for fp in fparts for p in fp.vs]
        if not ds or max(ds) - min(ds) < need:
            return False
    return True


def _edge_points(part, polys, step):
    """Points along the edges of the given polygons, at most `step` apart, and their centres."""
    seen, out = set(), []
    for pi in polys:
        ids = part.ps[pi]
        vs = [part.vs[i] for i in ids]
        out.append(sum(vs, Vector()) / len(vs))
        for a, b in zip(ids, ids[1:] + ids[:1]):
            key = (min(a, b), max(a, b))
            if key in seen:
                continue
            seen.add(key)
            pa, pb = part.vs[a], part.vs[b]
            n = min(64, max(1, math.ceil((pb - pa).length / step)))
            out += [pa.lerp(pb, i / n) for i in range(n + 1)]
    return out


def _mkey(m):
    return tuple(tuple(row) for row in m)


def check(root, parts, pose=None, frames=None, moving=(), shown=None, group_of=None):
    """Test every recorded run's ends and body, and every part against the ground, in every frame
    (the module docstring); print the COLLIDE lines; return the counts {"ends", "untested", "body",
    "ground"} and the lines."""
    shown = shown or (lambda o: not o.hide_render)
    group_of = group_of or (lambda o: None)
    moving = set(moving)
    objs = {o.name: o for o in parts if o.type in ("MESH", "CURVE")}
    missing = []
    for rec in RUNS + FITTINGS + BELOW_OK:
        for n in rec["objs"]:
            if n not in objs:
                if n in bpy.data.objects:
                    objs[n] = bpy.data.objects[n]
                else:
                    missing.append(n)
    if missing:
        raise ValueError(f"runs.check: recorded objects not in the scene: {missing[:5]}")
    run_names = {rec["name"] for rec in RUNS}
    bad_tee = [rec["name"] for rec in FITTINGS if rec["tee"] is not None and rec["tee"] not in run_names]
    if bad_tee:
        raise ValueError(f"runs.check: tee fittings on no recorded run (their tee names none): {bad_tee}")
    run_of = {}
    for k, rec in enumerate(RUNS):
        for n in rec["objs"]:
            run_of.setdefault(n, k)
    fit_of = {}
    for k, rec in enumerate(FITTINGS):
        for n in rec["objs"]:
            fit_of.setdefault(n, k)
    tee_on = {n: rec["tee"] for rec in FITTINGS if rec["tee"] is not None for n in rec["objs"]}
    ok_why = {n: rec["why"] for rec in BELOW_OK for n in rec["objs"]}
    frame_list = list(frames) if frames is not None else [None]
    _COUNT[1] = _COUNT[0]

    lines = []

    def out(s):
        print(s, flush=True)
        lines.append(s)
    out(f"COLLIDE runs: {len(RUNS)} recorded, {len(FITTINGS)} fittings, {len(ok_why)} parts below_ok, "
        f"{len(objs)} parts; frames {len(frame_list)}")

    loose, body, below, below_info = {}, {}, {}, {}
    cache, memo = {}, {}
    tested_ends, tested_body, grounded = set(), set(), set()
    for fi, f in enumerate(frame_list):
        if pose is not None and f is not None:
            pose(f)
        bpy.context.view_layer.update()
        RI = root.matrix_world.inverted()
        rk = _mkey(root.matrix_world)
        P = {}
        for n, o in objs.items():
            if not shown(o):
                continue
            mk = (rk, _mkey(o.matrix_world))
            c = cache.get(n)
            if n in moving or c is None or c[0] != mk:      # measured again when it has moved
                c = cache[n] = (mk, _Part(o, RI))
            if c[1].ok:
                P[n] = c[1]
        key = {n: group_of(objs[n]) for n in P}

        def m_space(rec, p, RI=RI):
            fr = bpy.data.objects[rec["frame"]] if rec["frame"] else root
            return RI @ (fr.matrix_world @ Vector(p))

        def m_dir(rec, d, RI=RI):
            fr = bpy.data.objects[rec["frame"]] if rec["frame"] else root
            return ((RI @ fr.matrix_world).to_3x3() @ Vector(d)).normalized()

        # ---- the ground: every part shown this frame
        for n, p in P.items():
            grounded.add(n)
            if n in ok_why:
                below_info[n] = max(below_info.get(n, (0.0, ""))[0], -p.zmin), p.desc
            elif p.zmin < -GROUND_TOL:
                entry = below.setdefault(n, [0.0, [], p.desc])
                entry[0] = max(entry[0], -p.zmin)
                entry[1].append(fi)

        # ---- the ends: every run with a part shown this frame
        for k, rec in enumerate(RUNS):
            own = [n for n in rec["objs"] if n in P]
            if not own:
                continue
            tested_ends.add(k)
            g = key[own[0]]
            mine = set(rec["objs"])
            pts = [m_space(rec, p) for p in rec["pts"]]
            r = rec["r"]
            hosts = [p for n, p in P.items() if n not in mine and key[n] == g and (n not in run_of or n in fit_of)]
            for end in (0, 1):
                e, t = _tangent(pts, end, r)
                why, host = _end(rec, end, e, t, r, P, hosts, fit_of, key, g, mine, m_dir)
                if why:                                     # one line an end: the first frame's reason
                    loose.setdefault((k, end), [e, why, host, []])[3].append(fi)

        # ---- the body: every pair shown this frame (measured again only when either has moved)
        for k, rec in enumerate(RUNS):
            mine = set(rec["objs"])
            fits = set(rec["end_fit"][0]) | set(rec["end_fit"][1])
            bparts = [P[n] for n in rec["objs"] if n in P and n not in fits]
            if not bparts:
                continue
            tested_body.add(k)
            g = key[bparts[0].name]
            pts = [m_space(rec, p) for p in rec["pts"]]
            ends = (pts[0], pts[-1])
            zone = max(2 * rec["r"], END_ZONE)
            for n, other in P.items():
                if n in mine or key[n] != g or tee_on.get(n) == rec["name"]:
                    continue
                was = memo.get((k, n))
                if was and len(was[0]) == len(bparts) and all(x is y for x, y in zip(was[0], bparts)) \
                        and was[1] is other and was[2] == ends:
                    d = was[3]
                else:
                    d = _body_depth(bparts, other, ends, zone)
                    memo[(k, n)] = (list(bparts), other, ends, d)
                if d > BODY_DEEP:
                    entry = body.setdefault((k, n), [0.0, [], other.desc])
                    entry[0] = max(entry[0], d)
                    entry[1].append(fi)

    # ---- the lines, in blocks: each ends with its count
    for (k, end), (at, why, host, fs) in sorted(loose.items()):
        out(f"COLLIDE LOOSE {RUNS[k]['name']} end {end} at ({at.x:+.2f},{at.y:+.2f},{at.z:.2f}) x "
            f"{host or 'nothing'}: {why}, frames {_frames_text(fs)}")
    out(f"COLLIDE ends: {len(loose)} clashes, {len(tested_ends)} runs, {2 * len(tested_ends)} ends")
    untested = [k for k in range(len(RUNS)) if k not in tested_ends]
    for k in untested:
        out(f"COLLIDE UNTESTED {RUNS[k]['name']} x nothing: no part of it shown with polygons in any frame "
            "(hidden, a curve with no bevel, or no faces)")
    out(f"COLLIDE untested: {len(untested)} clashes, {len(RUNS)} runs recorded")
    for (k, n), (d, fs, desc) in sorted(body.items()):
        out(f"COLLIDE BODY {RUNS[k]['name']} x {desc}: {d:.3f} deep, frames {_frames_text(fs)}")
    out(f"COLLIDE body: {len(body)} clashes, {len(tested_body)} runs")
    for n, (d, fs, desc) in sorted(below.items()):
        out(f"COLLIDE BELOW {desc} x ground: {d:.3f} deep, frames {_frames_text(fs)}")
    for n, (d, desc) in sorted(below_info.items()):
        out(_quiet(f"COLLIDE below_ok {desc}: {max(d, 0.0):.3f} deep  ({ok_why[n]})"))
    out(f"COLLIDE ground: {len(below)} clashes, {len(grounded)} parts, {len(below_info)} below_ok")
    recorded = set(run_of) | set(fit_of)
    tubes = sorted(n for n, (_, p) in cache.items() if p.ok and n not in recorded and _tube(p))
    out(_quiet(f"COLLIDE unrecorded tubes: {len(tubes)} (information)" + (": " + ", ".join(tubes[:12]) if tubes else "")
               + (f" and {len(tubes) - 12} more" if len(tubes) > 12 else "")))
    return dict(ends=len(loose), untested=len(untested), body=len(body), ground=len(below), lines=lines)


def _body_depth(bparts, other, ends, zone):
    """How deep the run's body parts and `other` reach into each other, away from the run's ends."""
    d = 0.0
    for bp in bparts:
        if not bp.boxes_meet(other):
            continue
        pairs = bp.tree.overlap(other.tree)
        if pairs:                               # the crossing edges, and the vertices within reach
            samples = ((other, _edge_points(bp, {i for i, _ in pairs}, BODY_STEP)
                        + [v for v in bp.vs if other.near(v)]),
                       (bp, _edge_points(other, {j for _, j in pairs}, BODY_STEP)
                        + [v for v in other.vs if bp.near(v)]))
        elif other.inside(bp.vs[0]):            # wholly inside it, no surfaces crossing
            samples = ((other, bp.vs),)
        elif bp.inside(other.vs[0]):            # it wholly inside the run
            samples = ((bp, other.vs),)
        else:
            continue
        for into, qs in samples:
            for q in qs:
                if min((q - ends[0]).length, (q - ends[1]).length) <= zone:
                    continue
                d = max(d, into.depth(q))
    return d


def _end(rec, end, e, t, r, P, hosts, fit_of, key, g, mine, m_dir):
    """Why end `end` of a run is not fastened (None when it is), and the part it is on."""
    def nearest(parts, p, d):
        best = None
        for q in parts:
            if q.near(p, d):
                dd = q.dist(p)
                if dd <= d and (best is None or dd < best[0]):
                    best = (dd, q)
        return best[1] if best else None
    own_fit = [P[n] for n in rec["end_fit"][end] if n in P]
    fit = None
    if own_fit:
        fparts = own_fit
    else:
        cands = {}
        for n, p in P.items():
            if n in fit_of and n not in mine and key[n] == g and p.near(e, FIT_DIST):
                d = p.dist(e)
                if d <= FIT_DIST and (fit_of[n] not in cands or d < cands[fit_of[n]]):
                    cands[fit_of[n]] = d
        if not cands:
            on = nearest(hosts, e, FIT_DIST)
            return (f"a bare end on it, no fitting within {FIT_DIST}" if on
                    else f"no fitting within {FIT_DIST}"), (on.desc if on else None)
        fi = min(cands, key=cands.get)
        fit = FITTINGS[fi]
        fparts = [P[n] for n in fit["objs"] if n in P]
        if not _span_ok(fparts, e, t, FIT_WIDTH * 2 * r):
            return (f"fitting {fit['name']} narrower than {FIT_WIDTH} of the run's {2 * r:.3f} across its end",
                    fit["name"])
    fnames = {p.name for p in fparts}
    seat_hosts = [h for h in hosts if h.name not in fnames]
    on = [h for h in seat_hosts if any(fp.touches(h, FIT_DIST) for fp in fparts)]
    on_ground = bool(fit and fit["ground"]) and \
        -GROUND_TOL <= min(v.z for fp in fparts for v in fp.vs) <= FIT_DIST
    label = fit["name"] if fit else "its end fitting"
    if not on and not on_ground:
        return f"{label} on no host (nothing within {FIT_DIST}, not on the ground)", label
    host = on[0].desc if on else "ground"
    q = e + t * max(r, FIT_DIST)
    into = [h for h in seat_hosts if h.inside(q)] or ([fp for fp in fparts if fp.inside(q)] if fit else [])
    if not into:
        return f"does not face into what it serves (the point {max(r, FIT_DIST):.3f} past its end is in nothing)", host
    if fit and fit["axis"] is not None:
        a = m_dir(fit, fit["axis"])
        ang = math.degrees(t.angle(a)) if t.length and a.length else 0.0
        if ang > AXIS_DEG:
            return f"arrives {ang:.0f} deg off {fit['name']}'s axis (at most {AXIS_DEG:.0f})", host
    b = e - t * 2 * r
    deep = [h for h in seat_hosts if h.inside(b)]
    if deep:
        return f"buried in {deep[0].desc} (the point {2 * r:.3f} back from its end is inside it)", deep[0].desc
    if on and all(all(any(h.inside(v) for h in on) for v in fp.vs) for fp in fparts):
        return f"buried in {on[0].desc} ({label} wholly inside it)", on[0].desc
    return None, host


def _tube(p):
    """A smooth closed mesh at least TUBE_RATIO times as long as it is thick (2 V / A its radius)."""
    if not p.smooth or len(p.vs) < 24:
        return False
    vol = area = 0.0
    for ids in p.ps:
        vs = [p.vs[i] for i in ids]
        for i in range(1, len(vs) - 1):
            a, b, c = vs[0], vs[i], vs[i + 1]
            cr = (b - a).cross(c - a)
            area += cr.length / 2
            vol += a.dot(b.cross(c)) / 6
    vol = abs(vol)
    if area <= 0 or vol <= 0:
        return False
    rad = 2 * vol / area
    length = area / (2 * math.pi * rad)
    return length >= TUBE_RATIO * 2 * rad


if __name__ == "__main__" and bpy is None:
    print(f"FIT_DIST {FIT_DIST}  FIT_WIDTH {FIT_WIDTH}  AXIS_DEG {AXIS_DEG}  BODY_DEEP {BODY_DEEP}  "
          f"END_ZONE {END_ZONE}  GROUND_TOL {GROUND_TOL}  TUBE_RATIO {TUBE_RATIO}")
