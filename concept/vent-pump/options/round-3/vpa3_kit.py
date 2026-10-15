"""Vent Pump, round 3, artist A (concepts 1, 2, 5, 7): the round-3 additions to round 2's kit.

Round 2's kit (../round-2/vpa_kit.py: the Reaction Plant round-5 finish, the melt, the parts,
run()) is used whole and unchanged; this adds what Liam's round-3 amendment asks for:

  - the helium line's family colour (helium-colour.txt, shared with artist B): a lagged line in
    grey-violet canvas (#7E7488) with pale-violet ID bands (#B6A6C8) and bare flanges at both
    ends; no frost, no blue;
  - a turning flow meter on that line (a dial read from above, a red-and-cream rotor under
    glass) that runs while working and stops idle, faster at each charge;
  - a poppet (purge or vent valve) that lifts with a timing function;
  - bottles whose valves and header face the line they feed;
  - pad(): a skid or plinth with chamfered corners, so the footprint's square breaks;
  - PATHS: every helium, melt and spent-gas run recorded in world space, written to meta.json
    for the sheet's path overlay (projected as label() is: x, y + z/2, 64 px a tile).

  $BLENDER -b --python vpa3_<n>_*.py -- <out-dir> [--quick] [--frames N] [--only ...] [--colourmap]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "round-2"))
from vpa_kit import *  # noqa: F401,F403,E402
import vpa_kit as K  # noqa: E402
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
import rig  # noqa: E402
from materials import layered  # noqa: E402

PATHS = {"helium": [], "melt": [], "spent": []}
HE_LAG, HE_BAND = "#7E7488", "#B6A6C8"


def build_materials3(lead_tops):
    K.build_materials(lead_tops)
    M = K.M
    M["he_lag"] = layered("he_lag", HE_LAG, metal="#5A5260", paint_metal=0.0, paint_rough=0.88, wear=0.25,
                          rust=0.1, dust=0.45, grime=0.65, jitter=0.08, ground=0.6)
    K.FINISH["he_lag"] = (HE_LAG, 0.0, "#5A5260", 0.3, 0.2, 0.2, None, 0.12, 0.4)
    M["he_band"] = layered("he_band", HE_BAND, metal="#6A6070", paint_metal=0.05, paint_rough=0.6, wear=0.3,
                           rust=0.05, dust=0.3, grime=0.4, jitter=0.05)
    K.FINISH["he_band"] = (HE_BAND, 0.35, "#6A6070", 0.2, 0.0, 0.1, None, 0.0, 0.25)
    for k in ("he_lag", "he_band"):
        K.soften_grain(M[k])
        p, ch, und, ru, wi, wa, sh, mo, fi = K.FINISH[k]
        K.worn_paint(M[k], p, chips=ch, under=und, rust=ru, wiped=wi, warm=wa, sheen=sh, mottle=mo, film=fi)
    K.GROUP["he_lag"] = ("helium line (grey-violet lagging)", "#9C80D0")
    K.GROUP["he_band"] = ("helium line (grey-violet lagging)", "#9C80D0")


# ---------------------------------------------------------------- paths for the overlay
def record(kind, pts, step=0.04):
    """Record a run (world points, tiles) for the path overlay; catmull-smoothed like the pipe."""
    P = catmull(pts, step=step) if len(pts) > 2 else [Vector(p) for p in pts]
    PATHS[kind].append([[round(v, 4) for v in p] for p in P])


def he_line(pts, r=0.065, bands=0.24, kind="helium", flanges=True):
    """The lagged helium line: grey-violet canvas, pale-violet bands, bare flanges at both ends."""
    P = catmull(pts)
    _, P, T, s = sweep(P, r, "he_lag", seg=18)
    nxt = bands / 2
    for i, p in enumerate(P):
        if bands and nxt <= s[i] < s[-1] - 0.06:
            cyl(tuple(p), r + 0.007, 0.05, "he_band", rot=along(T[i]), verts=20, bevel=0.002)
            nxt += bands
    if flanges:
        for p, t in ((P[0], T[0]), (P[-1], T[-1])):
            cyl(tuple(p), r * 1.4, 0.035, "bare", rot=along(t), verts=20, bevel=0.004)
    if kind:
        record(kind, pts)
    return P


def spent_line(pts, r=0.045):
    """Spent or recovered helium: bare steel, a violet band at each end so it reads as the
    helium family; recorded as 'spent'."""
    P = pipe(pts, r=r, mat="bare", marks=((0.12, "he_band"), (0.88, "he_band")))
    record("spent", pts)
    return P


def melt_path(pts):
    record("melt", pts)


# ---------------------------------------------------------------- timing
def burst_ease(centres, base=0.3, rise=0.05, fall=0.25, n=400):
    """An ease(t) for spin(): a rate of `base` plus a pulse at each centre, integrated and
    normalised so a whole number of turns a loop stays seamless."""
    rates = [base + pulse(i / n, centres, rise, fall) for i in range(n)]
    cum = [0.0]
    for r_ in rates:
        cum.append(cum[-1] + r_)
    tot = cum[-1]

    def ease(t):
        x = (t % 1.0) * n
        i = int(x)
        return (cum[i] + (cum[i + 1] - cum[i]) * (x - i)) / tot
    return ease


# ---------------------------------------------------------------- helium kit
def flow_meter(x, y, z, d=(1, 0), turns=4, ease=None, r=0.12):
    """An inline turbine meter on the helium line, read from above: a grey body across the line
    (ports at +-d), a brass bezel, a cream dial and a half-red, half-dark rotor disc that turns
    `turns` a loop while working (ease: a burst_ease), still idle. Returns (inlet, outlet)."""
    dx, dy = d
    cyl((x, y, z), r, 0.16, "grey", verts=32)
    for s_ in (-1, 1):
        cyl((x + s_ * dx * (r + 0.03), y + s_ * dy * (r + 0.03), z), 0.06, 0.08, "bare",
            rot=along((dx, dy, 0)), verts=16)
    torus((x, y, z + 0.085), r * 0.95, 0.016, "brass", seg=32)
    cyl((x, y, z + 0.082), r * 0.86, 0.01, "gauge", verts=32, bevel=0)
    piv = pivot((x, y, z + 0.092))
    sector((0, 0, 0), 0.01, r * 0.8, 0.0, PI, 0.01, "red", seg=12, parent=piv)
    sector((0, 0, 0), 0.01, r * 0.8, PI, 2 * PI, 0.01, "dark", seg=12, parent=piv)
    box((r * 0.4, 0, 0.006), (r * 0.8, 0.02, 0.006), "label", bevel=0, parent=piv)
    cyl((0, 0, 0.008), 0.02, 0.016, "brass", verts=8, parent=piv)
    bolts(x, y, z + 0.09, r * 0.98, 6, r=0.010)
    box((x - dy * (r + 0.04), y + dx * (r + 0.04), z + 0.02), (0.08, 0.06, 0.06), "dark_steel", bevel=0.005)
    spin(piv, turns, ease=ease)
    p_in = (x - dx * (r + 0.07), y - dy * (r + 0.07), z)
    p_out = (x + dx * (r + 0.07), y + dy * (r + 0.07), z)
    return p_in, p_out


def poppet(x, y, z, fn, lift=0.07, r=0.07, cap="red"):
    """A purge or vent valve on a vessel top: a bare body, a bolted bonnet, a red poppet that
    lifts by lift * fn(t) while working. Returns the body's side port height."""
    cyl((x, y, z + 0.05), r + 0.01, 0.12, "bare", verts=20)
    cyl((x, y, z + 0.12), r + 0.03, 0.03, "dark_steel", verts=20)
    bolts(x, y, z + 0.14, r + 0.015, 6, r=0.010)
    pv = pivot((x, y, z + 0.15))
    cyl((0, 0, 0.025), r, 0.05, cap, verts=20, parent=pv)
    cyl((0, 0, 0.07), 0.018, 0.05, "bare", verts=8, parent=pv)
    cyl((0, 0, 0.1), 0.04, 0.014, "dark_steel", verts=6, parent=pv)

    def pose(t, on):
        pv.location = (x, y, z + 0.15 + (lift * fn(t) if on else 0.0))
    K.ANIM.append(pose)
    return z + 0.05


def bottles(x, y, n=4, L=0.62, r=0.08, z0=0.1, side=1):
    """Horizontal helium bottles along X (bare steel) on a cradle, their valves on the `side`
    (+1 east, -1 west) end, each pigtailed into an upright header. Returns the header's top."""
    zc = z0 + 0.1 + r
    w = n * (2 * r + 0.03)
    for i in range(n):
        cy = y + (i - (n - 1) / 2) * (2 * r + 0.03)
        cyl((x, cy, zc), r, L, "bare", rot=(0, PI / 2, 0), verts=24)
        sphere((x - side * L / 2, cy, zc), r, "bare", scale=(0.6, 1, 1), seg=16)
        sphere((x + side * L / 2, cy, zc), r * 0.7, "bare", scale=(0.5, 1, 1), seg=16)
        cyl((x + side * (L / 2 + 0.05), cy, zc), 0.022, 0.08, "brass", rot=(0, PI / 2, 0), verts=8)
        cyl((x + side * (L / 2 + 0.09), cy, zc), 0.035, 0.03, "red", rot=(0, PI / 2, 0), verts=8)
        pipe([(x + side * (L / 2 + 0.07), cy, zc), (x + side * (L / 2 + 0.13), cy, zc + 0.06),
              (x + side * (L / 2 + 0.16), cy, zc + 0.12)], r=0.012, mat="copper", flanges=False)
    for k in (-0.3, 0.3):
        box((x + k * L, y, z0 + 0.06), (0.07, w + 0.04, 0.12), "dark_steel", bevel=0.006)
        box((x + k * L, y, z0 + 0.1 + 2 * r + 0.01), (0.04, w + 0.04, 0.025), "dark_steel", bevel=0.004)
    hx = x + side * (L / 2 + 0.16)
    box((hx, y, zc + 0.12), (0.06, w, 0.06), "bare", bevel=0.006)
    return (hx, y, zc + 0.12), w


def pad(x0, y0, x1, y1, h, mat="dark_steel", cut=0.3, corners=(), z0=0.0, bevel=0.012):
    """A skid or plinth (x0..x1, y0..y1, z0..z0+h) with the named corners ('NE', 'SW', ...)
    chamfered at 45 degrees by `cut`: the building's square broken where it meets the ground."""
    pts = []
    for cname, (cx, cy) in (("SW", (x0, y0)), ("SE", (x1, y0)), ("NE", (x1, y1)), ("NW", (x0, y1))):
        if cname in corners:
            sx = 1 if cx == x0 else -1
            sy = 1 if cy == y0 else -1
            a, b = (cx, cy + sy * cut), (cx + sx * cut, cy)
            pts += [a, b] if cname in ("SW", "NE") else [b, a]
        else:
            pts.append((cx, cy))
    me = bpy.data.meshes.new("pad")
    bm = bmesh.new()
    lo = [bm.verts.new((px, py, z0)) for px, py in pts]
    hi = [bm.verts.new((px, py, z0 + h)) for px, py in pts]
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("pad", me)
    K.sc.collection.objects.link(o)
    return K._finish(o, mat, bevel)


def run3(meta, nf=32):
    meta = dict(meta, paths=PATHS)
    run(meta, nf=nf)


def cabinet3(x, y, w, d, h, mat="grey", corner=(), cut=0.3):
    """Round 2's switch cabinet with a chamfered corner: louvres on its south face, no lamp."""
    pad(x - w / 2, y - d / 2, x + w / 2, y + d / 2, h, mat, cut=cut, corners=corner, bevel=0.015)
    for i in range(4):
        box((x - w * 0.15, y - d / 2 - 0.01, h * 0.35 + 0.07 * i), (w * 0.45, 0.02, 0.025), "dark_steel", bevel=0)
