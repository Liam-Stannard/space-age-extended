#!/usr/bin/env python3
"""Ballast Drill, T03j (task ballast-drill-ports): three takes on the wet-only pipework for the
T03i drill (option B2 on the 0.85 plate), each a flat-shaded game-view sketch in all four
directions, drawn as code. Plain SVG text, fixed number formatting, nothing random and no
timestamps, so running this again gives byte-identical files.

    python3 pipe_concepts.py [--png] [--t03i <take dir>]

Writes take-a.svg, take-b.svg, take-c.svg (each: dry and wet north at 2x, wet in the four
directions at 1x) and sheet.svg (the phone sheet: T03i's render beside each take, same scale
and centre); --png renders sheet.png with rsvg-convert. --t03i <dir> rebuilds the T03i stills
(t03i-*.png) from that take's dry/ and wet/ sheets (rig-round-6 take.sh output, frame 0, as
review_sheet.py composites them); without it the stills beside this file are used.

The body is option B2 as plate_concepts.py (at 271f85d) draws it, imported from
../plate-concepts unchanged; only its T03i runs, risers, girders and saddles are left out.
Coordinates: tiles, origin at the footprint's centre, y north, z up; the game view's screen up
is y + z/2 (rig.py's camera), 64 px a tile at 1x.

Where the fluid is used: the cutting head, under the press (spec 3.2), so every run ends at the
press's landing shoulder (r 1.40, top 1.01) or, in take B, at a ring main round its foot. The
wall fittings stay closed in the plate wall at vanilla's pipe-picture positions (T03h); each
run starts where the pipe comes up through the plate top beside its fitting.
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(HERE, "..", "plate-concepts"))
import plate_concepts as pc     # noqa: E402

pc.set_raised()
PT = pc.PLATE_TOP               # 0.85
TONE = pc.TONE
n = pc.n
K1 = pc.GV_K                    # 64 px a tile
CELL = pc.GV_CELL               # 448
GC = pc.GV_C                    # (224, 256)
DIRS = pc.DIR_NAMES
SH_R = pc.SH_R                  # 1.40, the landing shoulder
T03I_BORE = 2 * 0.22            # rig-round-6/rig_parts.py R_RUN 0.22: 0.44 across

# ---------------------------------------------------------------- the body's obstacles (plan)
PARTS, _ = pc.build("B2")
BY = {p.key: p for p in PARTS}
BASTIONS = [BY[k] for k in ("bast-NE", "bast-NW", "bast-SE", "bast-SW")]
FEET = [BY[k] for k in ("gfoot-NE", "gfoot-NW")]


def bay_depth(x, y, r):
    """How far a disc of radius r at (x, y) reaches over an open bay (0 if it does not)."""
    best = 0.0
    for b in pc.bay_rects(pc.BAY_R):
        x0, x1, y0, y1 = b.bbox()
        dx = max(x0 - x, 0.0, x - x1)
        dy = max(y0 - y, 0.0, y - y1)
        if dx == 0.0 and dy == 0.0:
            best = max(best, r + min(x - x0, x1 - x, y - y0, y1 - y))
        else:
            d = math.hypot(dx, dy)
            if d < r:
                best = max(best, r - d)
    return best


# ---------------------------------------------------------------- paths
def fillet(pts, rad, k=10):
    """A polyline with every inner corner replaced by a tangent arc of radius up to rad (less
    where the legs are short). Returns the plan points."""
    if len(pts) < 3:
        return list(pts)
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        u = (a[0] - b[0], a[1] - b[1])
        v = (c[0] - b[0], c[1] - b[1])
        lu, lv = math.hypot(*u), math.hypot(*v)
        u, v = (u[0] / lu, u[1] / lu), (v[0] / lv, v[1] / lv)
        cosang = max(-1.0, min(1.0, u[0] * v[0] + u[1] * v[1]))
        ang = math.acos(cosang)                       # the corner's inner angle
        if ang > math.pi - 1e-6:
            out.append(b)
            continue
        t = math.tan(ang / 2)
        d = min(rad / t, 0.5 * lu if i > 1 else 0.9 * lu, 0.5 * lv if i < len(pts) - 2 else 0.9 * lv)
        r_ = d * t
        p1 = (b[0] + u[0] * d, b[1] + u[1] * d)
        p2 = (b[0] + v[0] * d, b[1] + v[1] * d)
        bis = (u[0] + v[0], u[1] + v[1])
        lb = math.hypot(*bis)
        cdist = r_ / math.sin(ang / 2)
        cx, cy = b[0] + bis[0] / lb * cdist, b[1] + bis[1] / lb * cdist
        a1 = math.atan2(p1[1] - cy, p1[0] - cx)
        a2 = math.atan2(p2[1] - cy, p2[0] - cx)
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for j in range(k + 1):
            a_ = a1 + da * j / k
            out.append((cx + r_ * math.cos(a_), cy + r_ * math.sin(a_)))
    out.append(pts[-1])
    return out


def catmull(pts, k=12):
    """A Catmull-Rom curve through the points (the hoses: one continuous sweep)."""
    p = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for j in range(k if i < len(p) - 3 else k + 1):
            t = j / k
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[c] + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in (0, 1)))
    return out


def on_circle(a, b, r):
    """Where the segment a->b (a outside) first meets the circle of radius r about the centre."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    A = dx * dx + dy * dy
    B = 2 * (a[0] * dx + a[1] * dy)
    C = a[0] ** 2 + a[1] ** 2 - r * r
    t = (-B - math.sqrt(B * B - 4 * A * C)) / (2 * A)
    return (a[0] + dx * t, a[1] + dy * t)


def length(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def resample(pts, step=0.02):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        m = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        out += [(a[0] + (b[0] - a[0]) * i / m, a[1] + (b[1] - a[1]) * i / m) for i in range(1, m + 1)]
    return out


# ---------------------------------------------------------------- the fittings
# key: face and side. N/S: the side of x; E/W: '+' the fitting one tile north of centre (model
# y 0.806 at vanilla's shift), '-' the one a tile south (y -1.194).
def fit_key(f, lat):
    return f + ("+" if lat > 0 else "-")


ALL_KEYS = sorted({fit_key(f, l) for f, l in pc.ALL_FITS})


def lat_of(key):
    for f, l in pc.ALL_FITS:
        if fit_key(f, l) == key:
            return l
    raise KeyError(key)


def mirror_route(pts, key):
    """Routes are laid for the east side (x > 0) and the north/south faces' east fittings; the
    others mirror: x for W and the west N/S fittings."""
    f, s = key[0], key[1]
    mx = (f == "W") or (f in "NS" and s == "-")
    return [(-x if mx else x, y) for x, y in pts]


def base_route(take, key):
    """(plan waypoints from the pipe's rise beside the fitting to its end at the body, the
    end's kind). Laid for an east-side fitting; mirrored by the caller."""
    f, s = key[0], key[1]
    face = "E" if f in "EW" else f
    r = TAKES[take]["bore"] / 2
    lane = round(0.90 - r - 0.01, 3)        # past the bastion's foot (x 0.90), 0.01 clear
    if face in "NS":
        sy = 1 if face == "N" else -1
        # out of the gallery past the bastion's foot (x 0.90) and the bay's edge (0.70): the lane
        # between them; then straight in to the shoulder
        if take in "AB":
            return [(0.86, sy * 2.30), (lane, sy * 1.95), (lane, sy * 1.0)], ("shoulder" if take == "A" else "ring")
        return [(0.90, sy * 2.28), (0.75, sy * 1.95), (0.64, sy * 1.37)], "nozzle"     # searched: 0.016 clear
    if s == "+":
        # the north-side E/W fitting: under the bastion's corner (1.94, 0.81), over the bay's
        # corner (y < 0.70 from x 1.60), on into the shoulder east-north-east
        if take in "AB":
            return [(2.25, 0.86), PASS[take], (0.0, 0.0)], ("shoulder" if take == "A" else "ring")
        return [(2.25, 0.88), PASS[take], (1.45, 0.27)], "nozzle"
    # the south-side E/W fitting: west on the plate between the bay (y > -0.70) and the south
    # bastion's north face (y -1.40)
    if take in "AB":
        return [(2.25, -1.194), (0.0, -1.194)], ("shoulder" if take == "A" else "ring")
    return [(2.25, -1.194), (1.62, -1.10), (1.17, -0.88)], "nozzle"


# where the north-side E/W runs pass under the bastion's corner (1.94, 0.81): tuned so the bore
# clears it by 0.01 with the least reach over the bay (searched on a 0.02 x 0.005 grid)
PASS = {"A": (1.98, 0.66), "B": (1.96, 0.665), "C": (1.94, 0.63)}


TAKES = {
    "A": dict(name="Spokes", bore=0.26, ring=None, fillet=0.30,
              z=PT + 0.15, caption=[
                  "A  Spokes: every connection its own short run, straight in to the press. The pipe comes up through a cast "
                  "boss set in the plate's edge over its fitting (plate iron, as the refinery's sockets are part of its base),",
                  "runs low on cast saddles along the lanes between the bastions and the bays, one bend, and enters the landing "
                  "shoulder through a cast socket (press iron). Nothing between connection and press but the run."]),
    "B": dict(name="Ring main", bore=0.24, ring=0.20, fillet=0.30,
              z=PT + 0.13, caption=[
                  "B  Ring main: a slim ring main bolted round the press's foot (axis r 1.50, bore 0.20; through the north guide "
                  "feet, which carry it as cast tees) is where the fluid goes, all round the head; each connection is a short",
                  "spur to it: a steel flange on the plate over the fitting, a flanged elbow up, along the same lanes as A, "
                  "into a flanged tee on the ring (the big drill's elbow boxes and clamped runs; the foundry's base ring)."]),
    "C": dict(name="Hoses", bore=0.26, ring=None, fillet=0.0,
              z=PT + 0.30, caption=[
                  "C  Hoses: a cast gooseneck rises from the plate's edge over each fitting (plate iron) and a ribbed hose "
                  "sweeps from it in one curve, lifting over the bays' corners where it must, down onto a cast nozzle on",
                  "the shoulder's rim (press iron), clamped at both ends; no straights and no elbows (the cryogenic plant's "
                  "hoses from cast corner boxes)."]),
}


def route(take, key):
    """The take's run for one fitting: plan points (smoothed), the axis heights along them, the
    rise point and the end point, and the end's kind."""
    t = TAKES[take]
    pts, kind = base_route(take, key)
    r_end = SH_R if kind != "ring" else 1.50
    if kind in ("shoulder", "ring"):
        if pts[-1] == (0.0, 0.0):
            pts = pts[:-1] + [on_circle(pts[-2], (0.0, 0.0), r_end)]
        else:
            pts = pts[:-1] + [on_circle(pts[-2], pts[-1], r_end)]
        plan = fillet(pts, t["fillet"])
    else:
        # the hose: to a nozzle on the shoulder's rim, aimed at the centre
        plan = catmull(pts)
    plan = mirror_route(plan, key)
    # heights: A and B level; C's hose from the gooseneck's mouth to the nozzle, lifted mid-span
    # where it crosses a bay's corner, otherwise sagging onto the plate
    if take == "C":
        z0, z1 = PT + 0.30, PT + 0.24
        L = length(plan)
        zs = []
        acc = 0.0
        lift = 0.10 if key[1] == "+" and key[0] in "EW" else -0.10
        for i, p in enumerate(plan):
            if i:
                acc += math.hypot(p[0] - plan[i - 1][0], p[1] - plan[i - 1][1])
            u = acc / L
            zs.append(z0 + (z1 - z0) * u + lift * math.sin(math.pi * u))
    else:
        zs = [t["z"]] * len(plan)
    return dict(plan=plan, z=zs, kind=kind, r=t["bore"] / 2)


# ---------------------------------------------------------------- checks
def check_route(take, key, rt):
    """Plan clearances along the run's centreline (bore edge to part): the bastions, the guide
    feet, the shoulder (but the last 0.25 before the end), the plate's edge and notches; the
    run's reach over the open bays; whether it ever turns back (the distance still to go to its
    end along the run must fall, and its heading never turns more than 100 degrees in all)."""
    r = rt["r"]
    pts = resample(rt["plan"])
    L = length(pts)
    acc = 0.0
    worst = {"bastion": 9.0, "foot": 9.0, "shoulder": 9.0}
    bay_max, bay_len, off_plate = 0.0, 0.0, 0
    for i, (x, y) in enumerate(pts):
        if i:
            acc += math.hypot(x - pts[i - 1][0], y - pts[i - 1][1])
        for b in BASTIONS:
            worst["bastion"] = min(worst["bastion"], pc.shape_dist(b.shape, x, y) - r)
        for ft in FEET:
            worst["foot"] = min(worst["foot"], math.hypot(x - ft.shape.cx, y - ft.shape.cy) - ft.shape.r - r)
        if L - acc > 0.25 and rt["kind"] != "ring":
            worst["shoulder"] = min(worst["shoulder"], math.hypot(x, y) - SH_R - r)
        d = bay_depth(x, y, r)
        if d > 1e-6:
            bay_max = max(bay_max, d)
            bay_len += 0.02
        if not pc.in_plate(x, y) and bay_depth(x, y, 0.0) == 0.0:
            off_plate += 1
    # heading: total turning
    hd = []
    p = rt["plan"]
    for a, b in zip(p, p[1:]):
        if math.hypot(b[0] - a[0], b[1] - a[1]) > 1e-6:
            hd.append(math.atan2(b[1] - a[1], b[0] - a[0]))
    turn = sum(abs((b - a + math.pi) % (2 * math.pi) - math.pi) for a, b in zip(hd, hd[1:]))
    net = abs((hd[-1] - hd[0] + math.pi) % (2 * math.pi) - math.pi)
    end = p[-1]
    dist = [math.hypot(x - end[0], y - end[1]) for x, y in pts]
    back = max((dist[i + 1] - dist[i] for i in range(len(dist) - 1)), default=0.0)
    return dict(length=L, bastion=worst["bastion"], foot=worst["foot"], shoulder=worst["shoulder"],
                bay_max=bay_max, bay_len=bay_len, off_plate=off_plate,
                turn=math.degrees(turn), net=math.degrees(net), back=back)


# ---------------------------------------------------------------- drawing
class GV(pc.GameView):
    def P3(self, p):
        return self.P(*p)

    def tube3(self, pts3, r, col, outline=True):
        """A pipe along 3D points: an outline, the shaded body, a lit band up-left."""
        k = self.k
        d = "M " + " L ".join(f"{n(self.P(*q)[0])},{n(self.P(*q)[1])}" for q in pts3)
        j = ' stroke-linejoin="round" stroke-linecap="butt"'
        if outline:
            self.svg.path(d, "none", TONE["line"], 2 * r * k + 2 * self.sw, j)
        self.svg.path(d, "none", pc.shade(col), 2 * r * k, j)
        o = 0.35 * r * k
        self.svg.path(d, "none", col, 0.9 * r * k, j + f' transform="translate({n(-o)},{n(-o)})"')

    def band(self, p, t, r, w, col):
        """A ring round a pipe at p (3D), t its direction (plan), r its outer radius, w its length."""
        a = (p[0] - t[0] * w / 2, p[1] - t[1] * w / 2, p[2])
        b = (p[0] + t[0] * w / 2, p[1] + t[1] * w / 2, p[2])
        (ax, ay), (bx, by) = self.P(*a), self.P(*b)
        if math.hypot(bx - ax, by - ay) < 0.5:
            bx, by = ax, ay - 0.5        # end on: a short mark so the ring still draws
        self.svg.line(ax, ay, bx, by, TONE["line"], 2 * r * self.k + 2 * self.sw)
        self.svg.line(ax, ay, bx, by, col, 2 * r * self.k)


def unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    l_ = math.hypot(dx, dy) or 1.0
    return dx / l_, dy / l_


def stage_of(y):
    if y > 1.85:
        return "ngal"
    if y > 0.0:
        return "north"
    if y >= -1.85:
        return "middle"
    return "south"


def draw_run(gv, take, key, rt, stages):
    """Queue the run's pieces on the drawing stages: split where the run crosses a stage line,
    a band over each split so no seam shows."""
    t = TAKES[take]
    r = rt["r"]
    plan, zs = rt["plan"], rt["z"]
    pts3 = [(x, y, z) for (x, y), z in zip(plan, zs)]
    col = TONE["pipe"] if take != "C" else "#7A7064"        # C: the hose, rubber, darker than the iron
    # the pieces
    pieces = []
    cur = [pts3[0]]
    st = stage_of(pts3[0][1])
    for q in pts3[1:]:
        s2 = stage_of(q[1])
        cur.append(q)
        if s2 != st:
            pieces.append((st, cur))
            cur = [q]
            st = s2
    pieces.append((st, cur))
    for i, (st, pc3) in enumerate(pieces):
        if len(pc3) < 2:
            continue

        def fn(pc3=pc3, i=i):
            if take == "A":
                # cast saddles under it, every ~0.45 along
                L = 0.0
                for a, b in zip(pc3, pc3[1:]):
                    seg = math.hypot(b[0] - a[0], b[1] - a[1])
                    if int((L + seg) / 0.45) > int(L / 0.45):
                        tx, ty = unit(a, b)
                        nx, ny = -ty, tx
                        w, h = 0.07, r + 0.05
                        q = [(b[0] - tx * w + nx * h, b[1] - ty * w + ny * h), (b[0] + tx * w + nx * h, b[1] + ty * w + ny * h),
                             (b[0] + tx * w - nx * h, b[1] + ty * w - ny * h), (b[0] - tx * w - nx * h, b[1] - ty * w - ny * h)]
                        gv.prism(q, PT, b[2] - r * 0.6, TONE["plate"])
                    L += seg
            gv.tube3(pc3, r, col)
            if take == "C":
                # ribs
                L = 0.0
                for a, b in zip(pc3, pc3[1:]):
                    seg = math.hypot(b[0] - a[0], b[1] - a[1])
                    m = int((L + seg) / 0.09) - int(L / 0.09)
                    if m > 0:
                        (ax, ay), (bx, by) = gv.P(*a), gv.P(*b)
                        dx, dy = bx - ax, by - ay
                        ll = math.hypot(dx, dy) or 1.0
                        nx, ny = -dy / ll, dx / ll
                        h = r * gv.k * 0.92
                        gv.svg.line(bx - nx * h, by - ny * h, bx + nx * h, by + ny * h, pc.shade(col, 0.78), 0.8 * gv.k / K1)
                    L += seg
            if i > 0:
                gv.band(pc3[0], unit(pc3[0], pc3[1]), r + 0.035, 0.06, TONE["steel"] if take != "A" else TONE["plate"])
        stages[st].append(fn)
    # the joint at the wall
    x0, y0, z0 = pts3[0]
    t0 = unit(pts3[0], pts3[1])

    def wall_fn():
        if take == "A":
            gv.cyl(x0, y0, r + 0.07, PT - 0.02, z0 + r + 0.02, TONE["plate"])          # the cast boss
            gv.cyl(x0, y0, r + 0.02, z0 + r + 0.02, z0 + r + 0.05, TONE["plate"])
        elif take == "B":
            gv.cyl(x0, y0, r + 0.08, PT, PT + 0.03, TONE["steel"])                     # flange on the plate
            gv.cyl(x0, y0, r, PT + 0.03, z0, TONE["pipe"])                              # the rise
            gv.cyl(x0, y0, r + 0.04, z0 - 0.06, z0 - 0.02, TONE["steel"])              # the elbow's flange
            gv.cyl(x0, y0, r, z0 - 0.02, z0 + r * 0.6, TONE["pipe"])
        else:
            gv.cyl(x0, y0, r + 0.05, PT - 0.02, z0, TONE["plate"])                      # the gooseneck
            gv.tube3([(x0, y0, z0), (x0 + t0[0] * 0.14, y0 + t0[1] * 0.14, z0)], r + 0.05, TONE["plate"])
            gv.band((x0 + t0[0] * 0.15, y0 + t0[1] * 0.15, z0), t0, r + 0.04, 0.05, TONE["steel"])
    stages[stage_of(y0)].append(wall_fn)
    # the joint at the body
    x1, y1, z1 = pts3[-1]
    t1 = unit(pts3[-2], pts3[-1])

    def body_fn():
        if take == "A":
            a = (x1 - t1[0] * 0.16, y1 - t1[1] * 0.16, z1)
            b = (x1 + t1[0] * 0.04, y1 + t1[1] * 0.04, z1)
            gv.tube3([a, b], r + 0.06, TONE["press"])                                  # the cast socket
            gv.band(a, t1, r + 0.08, 0.04, TONE["press"])
        elif take == "B":
            gv.band((x1 - t1[0] * 0.05, y1 - t1[1] * 0.05, z1), t1, r + 0.045, 0.05, TONE["steel"])   # the tee's flange
        else:
            a = (x1 - t1[0] * 0.03, y1 - t1[1] * 0.03, z1)
            b = (x1 + t1[0] * 0.16, y1 + t1[1] * 0.16, z1 - 0.10)
            gv.band((x1 - t1[0] * 0.04, y1 - t1[1] * 0.04, z1), t1, r + 0.04, 0.05, TONE["steel"])
            gv.tube3([a, b], r - 0.02, TONE["press"])                                  # the nozzle
    stages[stage_of(y1)].append(body_fn)


RING_R, RING_Z = 1.50, PT + 0.11


def draw_ring(gv, stages):
    """Take B's ring main: drawn in arcs by stage (the back half before the shoulder, the front
    after the ballast ring), the guide feet's cast tees over it."""
    r = TAKES["B"]["ring"] / 2
    pts = [(RING_R * math.cos(math.radians(a)), RING_R * math.sin(math.radians(a)), RING_Z) for a in range(0, 361, 3)]
    back = pts[:61]                                   # 0 .. 180 degrees
    front = pts[60:]                                  # 180 .. 360

    def back_fn():
        gv.tube3(back, r, TONE["pipe"])
        for a in range(15, 180, 30):
            if a in (45, 135):
                continue
            q = (RING_R * math.cos(math.radians(a)), RING_R * math.sin(math.radians(a)), RING_Z)
            gv.band(q, (-math.sin(math.radians(a)), math.cos(math.radians(a))), r + 0.03, 0.04, TONE["steel"])
        for ft in FEET:
            # the foot as the tee: a cast collar over the ring where it passes
            gv.cyl(ft.shape.cx * RING_R / 1.65, ft.shape.cy * RING_R / 1.65, r + 0.07, PT, RING_Z + r + 0.02,
                   TONE["press"])

    def front_fn():
        gv.tube3(front, r, TONE["pipe"])
        for a in range(195, 360, 30):
            q = (RING_R * math.cos(math.radians(a)), RING_R * math.sin(math.radians(a)), RING_Z)
            gv.band(q, (-math.sin(math.radians(a)), math.cos(math.radians(a))), r + 0.03, 0.04, TONE["steel"])
    stages["north"].append(back_fn)
    stages["middle"].insert(0, front_fn)


def draw_body(svg, ox, oy, k, turns, take, wet):
    """The B2 drill as plate_concepts draws it (no T03i runs), with this take's runs drawn in
    stages between its parts; dry: no runs and no fittings."""
    gv = GV(svg, ox, oy, k)
    stages = {"ngal": [], "north": [], "middle": [], "south": []}
    rig = pc.rig_dir(turns)
    runs = []
    if wet and take:
        if TAKES[take]["ring"]:
            draw_ring(gv, stages)
        for f, lat in rig["fits"]:
            key = fit_key(f, lat)
            rt = route(take, key)
            runs.append((key, rt))
            draw_run(gv, take, key, rt, stages)

    def run_stage(s):
        for fn in stages[s]:
            fn()
    # ground shadow
    svg.add('<g opacity="0.42">')
    gv.shadow(pc.plate_outline(), 0.0, PT)
    for p in PARTS:
        if isinstance(p.shape, pc.Poly) and p.kind == "stand" and p.z1 > 1.5:
            gv.shadow(p.shape.pts, PT, p.z1)
    gv.shadow(pc.circ_pts(0, 0, pc.COL_R, 0, 360, 16), PT, 3.44)
    gv.shadow(pc.circ_pts(0, 0, pc.RB_OUT, 0, 360, 24), PT, pc.RING_TOP)
    svg.add("</g>")

    def legs(sy):
        for sx in (-1, 1):
            root = (sx * (pc.NCH / 2), sy * (pc.NCH / 2), 0.445)
            gv.stick(root, (sx * pc.PAD, sy * pc.PAD, 0.17), 0.30, TONE["leg"])
            gv.cyl(sx * pc.PAD, sy * pc.PAD, pc.PAD_R, 0.0, 0.09, TONE["hazard"])
            gv.cyl(sx * pc.PAD, sy * pc.PAD, pc.PAD_R, 0.09, 0.19, TONE["leg"])
    legs(1)
    for b in pc.bay_rects(pc.BAY_R):
        gv.prism(b.pts, 0.0, pc.AP, TONE["apron"])
    gv.prism(pc.plate_with_bays(), 0.0, PT, TONE["plate"])
    run_stage("ngal")
    for sd in ("E", "W"):
        p = BY[f"bast-N{sd}"]
        gv.prism(p.shape.pts, p.z0, p.z1, TONE["oxide"])
    for sd in ("E", "W"):
        f, g = BY[f"gfoot-N{sd}"], BY[f"guide-N{sd}"]
        gv.cyl(f.shape.cx, f.shape.cy, f.shape.r, f.z0, f.z1, TONE["press"])
        gv.cyl(g.shape.cx, g.shape.cy, g.shape.r, g.z0, g.z1, TONE["guide"])
    for sd in ("E", "W"):
        p = BY[f"house-N{sd}"]
        gv.prism(p.shape.pts, p.z0, p.z1, TONE["oxide"])
    run_stage("north")
    sh = BY["shoulder"]
    gv.cyl(0, 0, SH_R, sh.z0, pc.SH_TOP, TONE["press"])
    gv.ring_back(pc.RB_IN, pc.RB_OUT, pc.Z_RING, pc.RING_TOP, TONE["ring"])
    gv.cyl(0, 0, pc.COL_R, pc.SH_TOP, pc.COL_TOP, TONE["column"])
    gv.cyl(0, 0, 0.44, pc.COL_TOP, pc.COL_TOP + 0.10, TONE["column"])
    gv.cyl(0, 0, 0.30, pc.COL_TOP + 0.10, 3.40, TONE["column"])
    gv.cyl(0, 0, 0.10, 3.40, 3.44, TONE["steel"])
    gs = BY["guide-S"]
    gv.cyl(*pc.GUIDE_S, pc.GUIDE_R, gs.z0, pc.RING_TOP, TONE["guide"])
    gv.ring_front(pc.RB_IN, pc.RB_OUT, pc.Z_RING, pc.RING_TOP, TONE["ring"])
    gv.cyl(*pc.GUIDE_S, pc.GUIDE_R, pc.RING_TOP, gs.z1, TONE["guide"])
    run_stage("middle")
    for key in ("bast-SW", "bast-SE", "tank", "bottles"):
        p = BY[key]
        gv.prism(p.shape.pts, p.z0, p.z1, TONE[p.mat])
    run_stage("south")
    legs(-1)
    if wet:
        # the wall fittings, as plate_concepts draws them: S face ones 0.24 proud, their end rings
        # towards the camera; E/W ones in the wall, edge on; N face ones behind the plate
        for f, lat, jx, jy in rig["junctions"]:
            if f == "S":
                ye = -2.53 - pc.ZA / 2
                gv.tube([(lat, -pc.FACE + 0.01), (lat, ye)], pc.ZA, pc.R_RUN, TONE["steel"])
                cx, cy = gv.P(lat, ye, pc.ZA)
                r = pc.V_RING_R - 0.02
                bk = 0.07 * k
                svg.add(f'<ellipse cx="{n(cx)}" cy="{n(cy - bk)}" rx="{n(r * k)}" ry="{n(0.5 * r * k)}" '
                        f'fill="{pc.shade(TONE["steel"])}" stroke="{TONE["line"]}" stroke-width="{n(gv.sw)}"/>')
                svg.rect(cx - r * k, cy - bk, 2 * r * k, bk, pc.shade(TONE["steel"]), "none", 0)
                svg.add(f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(r * k)}" ry="{n(0.5 * r * k)}" '
                        f'fill="{TONE["steel"]}" stroke="{TONE["line"]}" stroke-width="{n(gv.sw)}"/>')
                svg.add(f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n((pc.R_RUN - 0.03) * k)}" '
                        f'ry="{n(0.5 * (pc.R_RUN - 0.03) * k)}" fill="#1A1816" stroke="none"/>')
            elif f in "EW":
                x = pc.FACE if f == "E" else -pc.FACE
                r = (pc.H_RING_R - 0.02) * 1.118
                a = gv.P(x, lat - r, pc.ZA)
                b = gv.P(x, lat + r, pc.ZA)
                svg.rect(a[0] - 0.025 * k, b[1], 0.05 * k, a[1] - b[1], TONE["steel"], TONE["line"], gv.sw)
    return runs


# ---------------------------------------------------------------- the T03i stills
def t03i_stills(take_dir):
    """T03i's render (rig-round-6 cast take, frame 0) per direction, dry and wet, composited as
    review_sheet.py does: the layers in combine.py's order, shadows at half strength, on the
    ground tone, the footprint centre at GV_C; 1x, and north at 2x (nearest)."""
    import json
    from PIL import Image
    g = tuple(int(TONE["ground"][i:i + 2], 16) for i in (1, 3, 5))
    for state, stems in (("wet", ("base-shadow", "rig-shadow", "base", "rig", "chute", "stroke", "rig-front")),
                         ("dry", ("base-shadow", "base", "chute", "stroke"))):
        src = os.path.join(take_dir, state)
        meta = json.load(open(os.path.join(src, "meta.json")))
        for d in DIRS:
            im = Image.new("RGBA", (CELL, CELL), g + (255,))
            for stem in stems:
                name = f"{stem}-{d}"
                m = meta[name]
                w, h = m["size"]
                lay = Image.open(os.path.join(src, name + ".png")).convert("RGBA").crop((0, 0, w, h))
                if "shadow" in stem:
                    a = lay.getchannel("A").point(lambda v: v // 2)
                    lay = Image.merge("RGBA", (*Image.new("RGB", lay.size).split(), a))
                x = round(GC[0] + m["shift"][0] * K1 - w / 2)
                y = round(GC[1] + m["shift"][1] * K1 - h / 2)
                im.alpha_composite(lay, (x, y))
            im = im.convert("RGB")
            if state == "wet":
                im.save(os.path.join(HERE, f"t03i-wet-{d}.png"), optimize=False)
            if d == "north":
                im.resize((2 * CELL, 2 * CELL), Image.NEAREST).save(os.path.join(HERE, f"t03i-{state}-north-2x.png"),
                                                                     optimize=False)


# ---------------------------------------------------------------- panels
def cell(svg, x, y, s, label, turns=0, take=None, wet=True, image=None):
    """A game-view cell at scale s (1 or 2) at (x, y): a sketch or a T03i still."""
    size = CELL * s
    svg.text(x, y + 16, label, 13, TONE["dim"])
    y += 24
    if image:
        svg.add(f'<image x="{n(x)}" y="{n(y)}" width="{size}" height="{size}" href="{image}"/>')
    else:
        svg.rect(x, y, size, size, TONE["ground"], "none", 0)
        svg.add(f'<svg x="{n(x)}" y="{n(y)}" width="{size}" height="{size}" overflow="hidden">')
        draw_body(svg, GC[0] * s, GC[1] * s, K1 * s, turns, take, wet)
        svg.add("</svg>")
    pc.footprint_marks(svg, x, y, s)
    return size + 24


PAD = 14
W = 2 * 2 * CELL + PAD * 3          # 1834


def take_block(svg, take, y0, with_t03i=True):
    """A take: its caption; T03i wet beside the take wet, north at 2x; the take wet in the four
    directions at 1x; its checks. Returns the height."""
    t = TAKES[take]
    y = y0
    svg.text(PAD, y + 24, f"Take {take}: {t['name']}  (bore {t['bore']:.2f}"
             + (f", ring main {t['ring']:.2f}" if t["ring"] else "")
             + f"; T03i {T03I_BORE:.2f})", 22, TONE["text"], weight="bold")
    y += 34
    for line in t["caption"]:
        svg.text(PAD, y + 14, line, 13, TONE["dim"])
        y += 18
    y += 6
    if with_t03i:
        h = cell(svg, PAD, y, 2, "north, wet: T03i render (2x)", image="t03i-wet-north-2x.png")
        cell(svg, 2 * PAD + 2 * CELL, y, 2, f"north, wet: take {take} sketch (2x)", 0, take, True)
    else:
        h = cell(svg, PAD, y, 2, "north, dry: no pipework (2x)", 0, take, False)
        cell(svg, 2 * PAD + 2 * CELL, y, 2, f"north, wet: take {take} sketch (2x)", 0, take, True)
    y += h + 8
    for i, d in enumerate(DIRS):
        cell(svg, PAD + i * (CELL + (W - 2 * PAD - 4 * CELL) / 3), y, 1, f"{d}, wet: take {take} (1x)", i, take, True)
    y += CELL + 24 + 8
    for line in check_lines(take):
        svg.text(PAD, y + 13, line, 12, TONE["muted"])
        y += 16
    return y - y0 + 10


def check_lines(take):
    out = []
    parts = []
    for key in ALL_KEYS:
        rt = route(take, key)
        c = check_route(take, key, rt)
        parts.append(f"{key}: {c['length']:.2f} long, turns {c['turn']:.0f} deg"
                     + (f", over bay {c['bay_max']:.2f} for {c['bay_len']:.2f}" if c["bay_max"] > 0 else ""))
    out.append("Runs (plan; N/S keyed by the fitting's side of x, E/W by north/south of centre): " + "; ".join(parts[:4]) + ";")
    out.append("   " + "; ".join(parts[4:]) + ".")
    worst = {k: min(check_route(take, key, route(take, key))[k] for key in ALL_KEYS) for k in ("bastion", "foot", "shoulder")}
    out.append(f"Clearance, bore edge in plan, worst over all 8 fittings: bastions {worst['bastion']:.2f}, guide feet "
               f"{worst['foot']:.2f}"
               + (f", shoulder before the socket {worst['shoulder']:.2f}" if worst['shoulder'] < 9 else "")
               + "; off the plate 0; never turns back (the distance still to go falls all the way, every run).")
    return out


HEADER = ["Ballast Drill  T03j: wet-only pipework, three takes (2D game-view sketches)",
          "The T03i drill (option B2 on the 0.85 plate) with all four connections live; dry draws no pipework. Flat-shaded, "
          "64 px a tile at 1x, the game's camera (screen up = y + z/2); the footprint's corners ticked.",
          "Each run starts where the pipe comes up through the plate top beside its closed wall fitting (at vanilla's "
          "pipe-picture position) and ends where the fluid is used: the cutting head under the press.",
          "Vanilla (study in the report): chemical plant and refinery fuse the connection into a cast socket of the base; "
          "foundry's connection is a piece of its base ring; cryogenic plant: ribbed hoses",
          "sweeping from cast corner boxes; big mining drill: slim pipes (about 0.32 across, measured) clamped to its frame. "
          "T03i's runs paired the connections round the gallery and never reached the press: here every run does."]


def main():
    png = "--png" in sys.argv
    if "--t03i" in sys.argv:
        t03i_stills(sys.argv[sys.argv.index("--t03i") + 1])
    # each take's own sheet
    for take in "ABC":
        s = pc.Svg()
        h = take_block(s, take, PAD, with_t03i=False)
        doc = pc.document([f'<rect x="0" y="0" width="{n(W)}" height="{n(h + 2 * PAD)}" fill="{TONE["bg"]}"/>'] + s.o,
                          W, h + 2 * PAD)
        with open(os.path.join(HERE, f"take-{take.lower()}.svg"), "w", newline="\n") as fh:
            fh.write(doc)
    # the phone sheet
    s = pc.Svg()
    y = PAD
    s.text(PAD, y + 26, HEADER[0], 26, TONE["text"], weight="bold")
    y += 40
    for line in HEADER[1:]:
        s.text(PAD, y + 14, line, 13, TONE["dim"])
        y += 18
    y += 10
    s.text(PAD, y + 20, "Dry: the same in every take (no fluid, no pipework)", 18, TONE["text"], weight="bold")
    y += 28
    h = cell(s, PAD, y, 2, "north, dry: T03i render (2x)", image="t03i-dry-north-2x.png")
    cell(s, 2 * PAD + 2 * CELL, y, 2, "north, dry: sketch, every take (2x)", 0, "A", False)
    y += h + 12
    s.text(PAD, y + 20, "T03i wet, as judged (\"doesn't flow\"), four directions (1x)", 18, TONE["text"], weight="bold")
    y += 28
    for i, d in enumerate(DIRS):
        cell(s, PAD + i * (CELL + (W - 2 * PAD - 4 * CELL) / 3), y, 1, f"{d}, wet: T03i render (1x)", image=f"t03i-wet-{d}.png")
    y += CELL + 24 + 16
    for take in "ABC":
        s.line(PAD, y, W - PAD, y, TONE["grid"], 2)
        y += 8
        y += take_block(s, take, y)
    total = y + PAD
    doc = pc.document([f'<rect x="0" y="0" width="{n(W)}" height="{n(total)}" fill="{TONE["bg"]}"/>'] + s.o, W, total)
    with open(os.path.join(HERE, "sheet.svg"), "w", newline="\n") as fh:
        fh.write(doc)
    # the checks, printed
    for take in "ABC":
        print(f"take {take} ({TAKES[take]['name']}), bore {TAKES[take]['bore']}:")
        for key in ALL_KEYS:
            c = check_route(take, key, route(take, key))
            print(f"  {key}: length {c['length']:.2f}; clear: bastion {c['bastion']:.3f}, foot {c['foot']:.3f}, "
                  f"shoulder {c['shoulder']:.3f}; bay over {c['bay_max']:.3f} for {c['bay_len']:.2f}; off plate "
                  f"{c['off_plate']}; turning {c['turn']:.0f} deg (net {c['net']:.0f}); worst step away {c['back']:.4f}")
        for t_ in range(4):
            keys = [fit_key(f, l) for f, l in pc.rig_dir(t_)["fits"]]
            print(f"  {DIRS[t_]}: {keys}")
    print(f"sheet {n(W)} x {n(total)} px")
    if png:
        subprocess.run(["rsvg-convert", "-o", os.path.join(HERE, "sheet.png"), os.path.join(HERE, "sheet.svg")], check=True)


if __name__ == "__main__":
    main()
