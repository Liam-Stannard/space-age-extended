"""The Ballast Drill's fitting runs (task ballast-drill-ports, T03c: options for Liam).

Imported by ballast_drill.py under --fittings --runs=<take>; without --runs the fittings are
T03a's, unchanged. Each take adds, for every connection of a direction, a run from the
connection to where the fluid is used, in that direction's fittings group (fit-behind-<d> or
fit-front-<d>, by the connection's side, as T03a), so the layers split as T03a's.

Where the runs go. The plate does not turn, so in every direction a connection lands on one
of eight places: a face's tile either side of its bay (the middle tile, where the chute or a
shut hatch is). Behind each of the eight the plate stands tall (the gear-houses' drive
cabinets, the south housings) except the two east and west tiles south of the centre; but
every one of them is beside a bay, and a direction's connections are never beside the bay its
chute is in (big-mining-drill.lua:570-580: no connection on the output face). A bay is cut
to the ground in front of the cutting head's shroud (the riser at Y_STEP stands over it), so
in four takes the runs come out of the bay's side wall (the casting carries them the 0.3
from the connection), lie on the shut hatch and enter the riser's foot: the cutting head.
(A take to the landing shoulder over the deck was worked out and dropped: between the riser and
the shoulder there is 0.23 of deck, under the bore's 0.56, and behind six of the eight
connections the plate stands tall.)

Takes (sizes are the run's outer diameter in tiles; the connection's stub, T03a's, is 0.56):
  rigid     a cast elbow and spool at the connection's bore, flanged at both walls
  hose      a ribbed rubber hose of the connection's bore, crimped into flanged nozzles
  valve     rigid at the bore, a hand-wheel gate valve in each run
  reducer   vanilla's look: a valve body at the bore on the side wall, a cast reducer
            cone from it down to a 0.30 hose (the narrowing shown by the reducer), arched
            over the riser into a gland in the deck over the cutting head
  manifold  rigid at the bore: a header across the bay from the side wall, a tee in the bay's
            middle and one spool into the riser; two connections on one face share them
"""
import math

from mathutils import Vector

TAKES = ("rigid", "hose", "valve", "reducer", "manifold")
R_BORE = 0.28                       # the connection's: T03a's stub radius (ballast_drill.py fitting())
R_SMALL = 0.15                      # the reducer take's line


def build(g, take, d, conns, group_of):
    """Add take's runs for direction d: conns are its connections (x, y, face), y down as a
    pipe_connections position, group_of(y) its fittings group. Returns the diameters table."""
    assert take in TAKES, take
    rows = []
    for x, y, f in conns:
        grp = group_of(y)
        bay = g["BAYS"][f]
        # the connection's side of its bay, in the bay's own frame (x across, y out of the face)
        a = math.radians(g["FACE_DEG"][f])
        xa = Vector((math.cos(a), math.sin(a)))
        s = 1 if Vector((x, -y)).dot(xa) > 0 else -1
        kw = {}
        if take == "manifold":
            mates = [c for c in conns if c[2] == f]
            if len(mates) == 2:
                front = [group_of(c[1]) for c in mates if group_of(c[1]).startswith("fit-front")]
                first = (x, y, f) == mates[0]
                kw = dict(shared=True, front=(front[0] if front else group_of(mates[0][1])) if first else None)
        rows.append(dict(conn=[x, y, f], layer=grp.split("-")[1], **RUNS[take](g, bay, s, grp, **kw)))
    return rows


# ------------------------------------------------------------------ parts, in a bay's frame

def _rot(axis):
    return {"x": (0, math.pi / 2, 0), "y": (math.pi / 2, 0, 0), "z": (0, 0, 0)}[axis]


def flange(g, bay, grp, c, axis, r, t=0.05, bolts=8, mat="iron_worn"):
    """A bolted flange ring of outer radius r at c, square to axis; its bolts on the face
    toward +axis."""
    g["cyl"](tuple(c), r, t, mat, grp, verts=40, rot=_rot(axis), bevel=0.008, parent=bay)
    i = "xyz".index(axis)
    for k in range(bolts):
        th = 2 * math.pi * (k + 0.5) / bolts
        p = list(c)
        o = [j for j in range(3) if j != i]
        p[o[0]] += (r - 0.045) * math.cos(th)
        p[o[1]] += (r - 0.045) * math.sin(th)
        p[i] += t / 2 + 0.004
        g["bolt"](tuple(p), 0.016, 0.012, group=grp, rot=_rot(axis), parent=bay)


def tube(g, pts, r, mat, grp, bay, rib=0.0, pitch=0.05, seg=16):
    """ballast_drill.tube, in a group and frame of its own."""
    T, Ns, Bs, S = g["frames"](pts)

    def build(bm):
        rows = []
        for i, p in enumerate(pts):
            rr = r * (1 - rib * 0.5 * (1 - math.cos(2 * math.pi * S[i] / pitch))) if rib else r
            rows.append([bm.verts.new(p + (Ns[i] * math.cos(q) + Bs[i] * math.sin(q)) * rr)
                         for q in (2 * math.pi * k / seg for k in range(seg))])
        for a_, b_ in zip(rows, rows[1:]):
            for k in range(seg):
                bm.faces.new((a_[k], a_[(k + 1) % seg], b_[(k + 1) % seg], b_[k]))
        bm.faces.new(list(reversed(rows[0])))
        bm.faces.new(rows[-1])
    return g["mesh_object"]("run-hose", build, mat, grp, 0, smooth=True, parent=bay)


def rounded(pts, bend):
    """pts with each corner turned through an elbow of radius about bend (ballast_drill.pipe's)."""
    out = [Vector(pts[0])]
    for i in range(1, len(pts) - 1):
        p, a_, b_ = Vector(pts[i]), Vector(pts[i - 1]), Vector(pts[i + 1])
        e = min(bend, 0.48 * (a_ - p).length, 0.48 * (b_ - p).length)
        s0, s1 = p + (a_ - p).normalized() * e, p + (b_ - p).normalized() * e
        if (s0 - out[-1]).length > 1e-4:
            out += [out[-1].lerp(s0, k / 6) for k in range(1, 6)]
        for k in range(13):
            u = k / 12
            out.append((1 - u) ** 2 * s0 + 2 * (1 - u) * u * p + u * u * s1)
    end = Vector(pts[-1])
    out += [out[-1].lerp(end, k / 6) for k in range(1, 7)]
    return out


def rigid(g, pts, r, grp, bay, bend=0.24, mat="steel"):
    """A rigid run: a mesh tube (a curve's bevel shaded black here), elbows rounded."""
    return tube(g, rounded(pts, bend), r, mat, grp, bay, seg=28)


def bezier(p0, t0, p1, t1, n=40, k=0.4):
    """A cubic from p0 heading t0 to p1 arriving along t1, handles k of the chord."""
    p0, p1, t0, t1 = Vector(p0), Vector(p1), Vector(t0).normalized(), Vector(t1).normalized()
    L = (p1 - p0).length * k
    c0, c1 = p0 + t0 * L, p1 - t1 * L
    return [(1 - u) ** 3 * p0 + 3 * (1 - u) ** 2 * u * c0 + 3 * (1 - u) * u * u * c1 + u ** 3 * p1
            for u in (i / n for i in range(n + 1))]


def ferrule(g, bay, grp, p, t, r):
    """A hose's crimped ferrule and nut at p, the hose leaving along t."""
    t = Vector(t).normalized()

    def along(c, rr, h, mat, verts=24):
        rot = Vector((0, 0, 1)).rotation_difference(t).to_euler()
        g["cyl"](tuple(c), rr, h, mat, grp, verts=verts, rot=tuple(rot), bevel=0.004, parent=bay)
    p = Vector(p)
    L = min(2 * r, 0.14)                 # a short collar: a long one on the big hose hid the rubber
    along(p + t * L / 2, r * 1.1, L, "steel")
    for k in range(2):
        along(p + t * L * (0.3 + 0.45 * k), r * 1.15, 0.018, "steel")
    along(p + t * 0.012, r * 1.22, 0.04, "bolt", verts=6)


# ------------------------------------------------------------------ the bay's geometry

def _bay(g):
    AP, YS, E, HC, ZT, EI = g["AP"], g["Y_STEP"], g["E"], g["HC"], g["ZT"], g["EI"]
    return AP, YS, E, HC, ZT, EI


SIDE = 0.70                          # the bay's side wall (BAND_HW)
VE = 2.2                             # where a run leaves the side wall, along the bay: at its mouth,
                                     # beside the connection (its flange stands over the wall's edge)


def _wall_top(g, v):
    AP, YS, E, HC, ZT, EI = _bay(g)
    return ZT if v <= EI else HC + (ZT - HC) * (E - v) / (E - EI)


def rigid_core(g, bay, s, grp, r=R_BORE, valve=False):
    """Out of the side wall at the bore, a cast elbow onto the hatch and a spool into the riser."""
    AP, YS, E, HC, ZT, EI = _bay(g)
    ax = AP + r + 0.002                              # lying on the apron and the shut hatch
    uc = SIDE - r - 0.03
    pts = [(s * (SIDE + 0.06), VE, ax), (s * uc, VE, ax), (s * uc, YS - 0.04, ax)]
    rigid(g, pts, r, grp, bay)
    flange(g, bay, grp, (s * (SIDE - 0.02), VE, ax), "x", r + 0.075)
    flange(g, bay, grp, (s * uc, YS + 0.025, ax), "y", r + 0.075)
    # the elbow's cast saddle on the hatch, bolted through
    g["box"]((s * uc, VE - 0.02, AP + 0.02), (0.3, 0.16, 0.04), "iron_worn", grp, bevel=0.008, parent=bay)
    for du in (-0.11, 0.11):
        g["bolt"]((s * uc + du, VE - 0.02, AP + 0.044), 0.016, 0.012, group=grp, parent=bay)
    out = dict(fitting=2 * R_BORE, run=2 * r, head=2 * r)
    if valve:
        vc = (s * uc, (VE + YS) / 2 - 0.01, ax)
        flange(g, bay, grp, (vc[0], vc[1] + 0.07, ax), "y", r + 0.06, t=0.04)
        flange(g, bay, grp, (vc[0], vc[1] - 0.07, ax), "y", r + 0.06, t=0.04)
        g["box"](vc, (2 * r + 0.06, 0.12, 2 * r + 0.04), "iron_worn", grp, bevel=0.02, parent=bay)   # its body
        g["cyl"]((vc[0], vc[1], ax + r + 0.12), 0.07, 0.24, "iron_worn", grp, verts=20, parent=bay)   # bonnet
        g["cyl"]((vc[0], vc[1], ax + r + 0.26), 0.022, 0.12, "polish", grp, verts=12, parent=bay)     # stem
        hw = g["ring"]((vc[0], vc[1], ax + r + 0.3), 0.17, 0.14, 0.03, "oxide", grp, parent=bay, verts=40)
        for k in range(4):                                                           # its spokes
            th = math.pi / 4 + k * math.pi / 2
            g["box"]((vc[0] + 0.075 * math.cos(th), vc[1] + 0.075 * math.sin(th), ax + r + 0.3),
                     (0.15, 0.022, 0.018), "oxide", grp, rot=(0, 0, th), bevel=0.003, parent=bay)
        out["valve"] = 2 * r + 0.06
    return out


def take_rigid(g, bay, s, grp):
    return rigid_core(g, bay, s, grp)


def take_valve(g, bay, s, grp):
    return rigid_core(g, bay, s, grp, valve=True)


def take_hose(g, bay, s, grp):
    """A hose of the bore: out of a flanged nozzle on the side wall, round onto the hatch and
    into a flanged nozzle on the riser."""
    AP, YS, E, HC, ZT, EI = _bay(g)
    r = 0.26                                         # the hose's body; its ferrules 0.29, the bore
    ax = AP + r + 0.004
    uc = SIDE - r - 0.05
    p0 = Vector((s * (SIDE - 0.09), VE + 0.06, ax + 0.02))
    t0 = Vector((-s, -0.55, 0))
    p1 = Vector((s * (uc - 0.02), YS + 0.11, ax))
    t1 = Vector((0, -1, 0))
    pts = bezier(p0, t0, p1, t1, n=48, k=0.55)
    tube(g, pts, r, "hose", grp, bay, rib=0.12, pitch=0.07)
    ferrule(g, bay, grp, p0 - t0.normalized() * 0.0, t0, r)
    ferrule(g, bay, grp, p1, -t1, r)
    # the nozzles: a short flanged spool from each wall, the hose's nut on it
    flange(g, bay, grp, (s * (SIDE - 0.02), VE + 0.06, ax + 0.02), "x", R_BORE + 0.075)
    flange(g, bay, grp, (s * (uc - 0.02), YS + 0.025, ax), "y", R_BORE + 0.075)
    g["cyl"]((s * (uc - 0.02), YS + 0.07, ax), R_BORE, 0.07, "steel", grp, verts=32, rot=_rot("y"), parent=bay)
    return dict(fitting=2 * R_BORE, run=2 * r, ferrule=2 * r * 1.12, head=2 * R_BORE)


def take_reducer(g, bay, s, grp):
    """Vanilla's look: a valve body at the bore on the side wall, a reducer cone to a
    smaller hose, into a nozzle of that size on the riser."""
    AP, YS, E, HC, ZT, EI = _bay(g)
    ax = AP + R_BORE + 0.002
    ub = SIDE - 0.2                                  # the body's centre, off the wall
    flange(g, bay, grp, (s * (SIDE - 0.02), VE, ax), "x", R_BORE + 0.075)
    g["cyl"]((s * (SIDE - 0.08), VE, ax), R_BORE, 0.1, "steel", grp, verts=40, rot=_rot("x"), parent=bay)
    # the body: a squat cast drum across the bore, its domed bonnet up, its cap bolted
    g["cyl"]((s * ub, VE, ax), R_BORE + 0.05, 0.26, "iron_worn", grp, verts=40, rot=_rot("x"), bevel=0.03,
             parent=bay)
    g["sphere"]((s * ub, VE, ax + 0.1), R_BORE + 0.02, "iron_worn", grp, parent=bay, squash=0.8)
    g["cyl"]((s * ub, VE, ax + 0.36), 0.09, 0.05, "steel", grp, verts=24, parent=bay)
    for k in range(6):
        th = 2 * math.pi * k / 6
        g["bolt"]((s * ub + 0.065 * math.cos(th), VE + 0.065 * math.sin(th), ax + 0.39), 0.012, 0.01,
                  group=grp, parent=bay)
    # the reducer: a cone out of the body's inner face, the bore down to the line
    rr = R_SMALL
    c0 = Vector((s * ub, VE - 0.13, ax))
    c1 = Vector((s * ub, VE - 0.32, ax + 0.03))
    n = 12
    pts = [c0.lerp(c1, i / n) for i in range(n + 1)]
    T, Ns, Bs, S = g["frames"](pts)

    def cone(bm):
        rows = []
        for i, p in enumerate(pts):
            u = i / n
            rad = R_BORE + 0.02 - (R_BORE + 0.02 - rr * 1.15) * (3 * u * u - 2 * u ** 3)
            rows.append([bm.verts.new(p + (Ns[i] * math.cos(q) + Bs[i] * math.sin(q)) * rad)
                         for q in (2 * math.pi * k / 32 for k in range(32))])
        for a_, b_ in zip(rows, rows[1:]):
            for k in range(32):
                bm.faces.new((a_[k], a_[(k + 1) % 32], b_[(k + 1) % 32], b_[k]))
        bm.faces.new(list(reversed(rows[0])))
        bm.faces.new(rows[-1])
    g["mesh_object"]("reducer", cone, "iron_worn", grp, 0, smooth=True, parent=bay)
    flange(g, bay, grp, tuple(c0 + Vector((0, 0.01, 0))), "y", R_BORE + 0.06, t=0.04, bolts=6)
    # the line: out of the reducer, arched up over the riser and down into a gland in the
    # deck between the riser and the shoulder, over the cutting head
    vg = 1.48
    gl = Vector((s * ub, vg, ZT + 0.07))
    p0 = c1
    pts = bezier(p0, (0, -1, 0.5), gl + Vector((0, 0, 0.04)), (0, -0.25, -1), n=40, k=0.7)
    tube(g, pts, rr, "hose", grp, bay, rib=0.18, pitch=0.045)
    ferrule(g, bay, grp, p0, (0, 1, -0.5), rr)
    ferrule(g, bay, grp, pts[-1], (0, 0.25, 1), rr)
    g["cyl"]((gl.x, vg, ZT + 0.03), 0.16, 0.06, "iron_worn", grp, verts=32, bevel=0.01, parent=bay)   # the gland
    for k in range(6):
        th = 2 * math.pi * (k + 0.5) / 6
        g["bolt"]((gl.x + 0.125 * math.cos(th), vg + 0.125 * math.sin(th), ZT + 0.064), 0.013, 0.01,
                  group=grp, parent=bay)
    return dict(fitting=2 * R_BORE, valve_body=2 * (R_BORE + 0.05), reducer=f"{2 * R_BORE + 0.04:.2f} -> {2 * rr:.2f}",
                run=2 * rr, head=2 * rr)


def take_manifold(g, bay, s, grp, shared=False, front=None):
    """A header across the bay from the side wall to its middle, a tee (or, alone, an elbow)
    and one spool into the riser; two connections on one face share the header and tee."""
    AP, YS, E, HC, ZT, EI = _bay(g)
    r = R_BORE
    ax = AP + r + 0.002
    if shared:
        rigid(g, [(s * (SIDE + 0.06), VE, ax), (s * 0.02, VE, ax)], r, grp, bay)
    else:
        rigid(g, [(s * (SIDE + 0.06), VE, ax), (0, VE, ax), (0, YS - 0.04, ax)], r, grp, bay)
    flange(g, bay, grp, (s * (SIDE - 0.02), VE, ax), "x", r + 0.075)
    flange(g, bay, grp, (s * (SIDE * 0.45), VE, ax), "x", r + 0.06, t=0.04)          # a joint in the header
    g["box"]((s * (SIDE * 0.45 + 0.12), VE, AP + 0.02), (0.14, 0.3, 0.04), "iron_worn", grp, bevel=0.008, parent=bay)
    if shared and front:                             # the tee and its spool, once, in the front group
        g["cyl"]((0, VE, ax), r + 0.04, 2 * r + 0.08, "iron_worn", front, verts=40, rot=_rot("x"), bevel=0.03,
                 parent=bay)
        g["sphere"]((0, VE, ax), r + 0.05, "iron_worn", front, parent=bay)
        rigid(g, [(0, VE, ax), (0, YS - 0.04, ax)], r, front, bay)
    if not shared or front:
        flange(g, bay, front or grp, (0, YS + 0.025, ax), "y", r + 0.075)
    return dict(fitting=2 * R_BORE, run=2 * r, head=2 * r)


RUNS = dict(rigid=take_rigid, hose=take_hose, valve=take_valve, reducer=take_reducer, manifold=take_manifold)
