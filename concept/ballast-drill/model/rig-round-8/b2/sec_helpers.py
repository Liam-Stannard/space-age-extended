
# T03i (B2): the plate's top. The chassis is the plate: one casting from the ground to PT over the
# chassis's outline (the corner notches and the four bays open), flat; B2's deck (0.87) merges
# into it: the landing shoulder and the north guide columns' feet stand on it at PT. ZT (0.87,
# the signed-off deck) is kept for the ring's numbers only (ZS = ZT + 0.14), so the stroke and
# every height above the shoulder are the signed-off ones.
PT = 0.85
GAL = 1.94                            # the gallery's inner line: the runs lie outside it (rig_parts.py)
NORTH_ANG = (45, 135)                 # B2: the north guide columns at 45 degrees, r 1.65 ("Accept the move")
GR_N_B2 = 1.65


def _area(pts):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1])) / 2


def ccw(pts):
    """The outline counter-clockwise from above (stack() makes its top face up from that)."""
    return list(pts) if _area(pts) > 0 else list(reversed(pts))


def _isect(p, t, q, u):
    """Where the line p + a t meets the line q + b u, or None if parallel."""
    den = t.x * u.y - t.y * u.x
    if abs(den) < 1e-9:
        return None
    a = ((q - p).x * u.y - (q - p).y * u.x) / den
    return p + t * a


def offset_poly(pts, d, keep=None):
    """A counter-clockwise outline grown by d on every edge (mitred), or by 0 on an edge
    keep(a, b) says False for."""
    P = [Vector(p) for p in ccw(pts)]
    n = len(P)
    lines = []
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]
        t = (b - a).normalized()
        nrm = Vector((t.y, -t.x))
        dd = d if keep is None or keep(tuple(a), tuple(b)) else 0.0
        lines.append((a + nrm * dd, t))
    out = []
    for i in range(n):
        (p0, t0), (p1, t1) = lines[i - 1], lines[i]
        q = _isect(p0, t0, p1, t1)
        out.append(tuple(q) if q is not None else tuple(p1))
    return out


def on_notch_line(a, b):
    """An edge on the plate's corner-notch line (|x| + |y| = 3.35, both beyond 1.5)."""
    return all(abs(abs(p[0]) + abs(p[1]) - 3.35) < 0.01 and abs(p[0]) >= 1.499 and abs(p[1]) >= 1.499 for p in (a, b))


def offset_chain(chain, t, inside):
    """An open polyline moved t toward the side `inside` (a plan point) lies on, mitred."""
    P = [Vector(p) for p in chain]
    ins = Vector(inside)
    segs = []
    for a, b in zip(P, P[1:]):
        tt = (b - a).normalized()
        nrm = Vector((-tt.y, tt.x))
        if (ins - a).dot(nrm) < 0:
            nrm = -nrm
        segs.append((a + nrm * t, tt))
    out = [segs[0][0]]
    for (p0, t0), (p1, t1) in zip(segs, segs[1:]):
        q = _isect(p0, t0, p1, t1)
        out.append(q if q is not None else p1)
    pl, tl = segs[-1]
    out.append(pl + tl * (P[-1] - P[-2]).length)
    return [tuple(p) for p in out]


def wall_outline(chain, t, inside):
    """A wall t thick along an open polyline, on its `inside` side: a closed outline."""
    inner = offset_chain(chain, t, inside)
    return ccw([tuple(p) for p in chain] + list(reversed(inner)))

