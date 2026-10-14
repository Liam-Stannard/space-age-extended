"""Vent Pump, round 2, concept 2: THE BUCKET LADDER (3 x 3).

  $BLENDER -b --python vpa_2_bucket_ladder.py -- <out-dir> [--quick] [--only working|idle|rot] [--colourmap]

A slanted, armoured ladder of ladle-buckets climbs east out of a refractory sump over the vent.
Helium-3 comes in at the south face to a cover-gas manifold and blankets the sump and the launder
(the melt meets nothing but helium). The foot tumbler dips the buckets in the melt pool; they
climb the ladder's open top run full, turn over the head tumbler (driven from the south by a
motor, coupling and gearbox on the drive frame) and tip into a heated launder that runs north
down the east side to a refractory receiving pot in the north-east corner; from the pot's foot
the melt runs west under the head and leaves by the north face. Two bucket pitches a loop: the
buckets climb and tip, and an orange spill falls into the launder.

The ladder runs west-east, across the camera, so its slant and the buckets' climb read from
the south; facing north the melt still enters at the vent (the middle) and leaves north.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpa_kit import *  # noqa: F401,F403,E402
import vpa_kit as K  # noqa: E402
from mathutils import Matrix  # noqa: E402

K.build_materials(((0.5, 0.3), (1.1, 0.35), (1.4, 0.3)))
NF = 32

# ---------------------------------------------------------------- the ladder's geometry
A = Vector((-0.42, 0.0, 0.26))       # the foot tumbler, in the pool
Bh = Vector((0.7, 0.0, 1.62))        # the head tumbler
D = (Bh - A).normalized()
LEN = (Bh - A).length
Nn = Vector((-D.z, 0.0, D.x))        # the top run's side
R = 0.14
LTOT = 2 * LEN + 2 * PI * R
NB = 16
PITCH = LTOT / NB
SPEED = 2                            # pitches a loop
HW = 0.3                             # the side plates' inner half-gap (y)


def at(s):
    """(point, tangent, outward normal) at arc length s round the loop, from the foot's top."""
    s %= LTOT
    if s < LEN:
        return A + Nn * R + D * s, D, Nn
    s -= LEN
    if s < PI * R:
        th = s / R
        n = Nn * math.cos(th) + D * math.sin(th)
        return Bh + n * R, (-Nn * math.sin(th) + D * math.cos(th)), n
    s -= PI * R
    if s < LEN:
        return Bh - Nn * R - D * s, -D, -Nn
    s -= LEN
    ph = s / R
    n = -Nn * math.cos(ph) - D * math.sin(ph)
    return A + n * R, (Nn * math.sin(ph) - D * math.cos(ph)), n


def plate_xz(pts, y0, y1, mat, bevel=0.01):
    """A plate in the XZ plane (an outline of (x, z) points), y0 to y1 thick."""
    me = bpy.data.meshes.new("plate")
    bm = bmesh.new()
    lo = [bm.verts.new((x, y0, z)) for x, z in pts]
    hi = [bm.verts.new((x, y1, z)) for x, z in pts]
    bm.faces.new(lo)
    bm.faces.new(list(reversed(hi)))
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new((lo[j], lo[i], hi[i], hi[j]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("plate", me)
    sc.collection.objects.link(o)
    return K._finish(o, mat, bevel)


def stadium(r, n=12):
    out = []
    for k in range(n + 1):
        th = PI * k / n
        p = Bh + r * (Nn * math.cos(th) + D * math.sin(th))
        out.append((p.x, p.z))
    for k in range(n + 1):
        ph = PI * k / n
        p = A + r * (-Nn * math.cos(ph) - D * math.sin(ph))
        out.append((p.x, p.z))
    return out


# ---------------------------------------------------------------- the sump over the vent
X0, X1, Y0, Y1 = -0.98, 0.3, -0.62, 0.62
OX0, OX1, OY = -0.78, 0.12, 0.34
ZS = 0.52
box(((X0 + OX0) / 2, 0, ZS / 2), (OX0 - X0, Y1 - Y0, ZS), "refr", bevel=0.02)
box(((OX1 + X1) / 2, 0, ZS / 2), (X1 - OX1, Y1 - Y0, ZS), "refr", bevel=0.02)
for s_ in (-1, 1):
    box(((OX0 + OX1) / 2, s_ * (OY + Y1) / 2, ZS / 2), (OX1 - OX0, Y1 - OY, ZS), "refr", bevel=0.02)
for z in (0.12, 0.4):
    for s_ in (-1, 1):
        box(((X0 + X1) / 2, s_ * (Y1 + 0.012), z), (X1 - X0 + 0.02, 0.025, 0.06), "dark_steel", bevel=0.004)
    box((X0 - 0.012, 0, z), (0.025, Y1 - Y0 + 0.04, 0.06), "dark_steel", bevel=0.004)
ring = [(OX1 + 0.03, -OY - 0.03), (OX1 + 0.03, OY + 0.03), (OX0 - 0.03, OY + 0.03), (OX0 - 0.03, -OY - 0.03)]
for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]):
    strut((ax, ay, ZS + 0.02), (bx, by, ZS + 0.02), 0.03, "dark_steel")
box(((OX0 + OX1) / 2, 0, ZS - 0.1), (OX1 - OX0, 2 * OY, 0.02), melt("pool", scale=6.0, k=1, axis="X"), bevel=0)
label(3, "the sump over the vent: the buckets dip in the melt pool", (-0.62, -0.25, ZS))
# the cover-gas hood over the sump's south lip
box((-0.33, -0.48, ZS + 0.09), (0.9, 0.26, 0.18), "dark_steel", bevel=0.02)
box((-0.33, -0.48, ZS + 0.19), (0.8, 0.18, 0.02), "hazard", bevel=0)
for x in (-0.72, 0.06):
    cyl((x, -0.48, ZS + 0.21), 0.03, 0.04, "bolt", verts=6, bevel=0)

# ---------------------------------------------------------------- the ladder
SP = stadium(R + 0.08)
for sy in (-1, 1):
    plate_xz(SP, sy * HW, sy * (HW + 0.04), "ochre")
    for k in range(1, 7):
        p = A + D * (LEN * k / 7)
        strut(p + Nn * (R + 0.07) + Vector((0, sy * (HW + 0.05), 0)),
              p - Nn * (R + 0.07) + Vector((0, sy * (HW + 0.05), 0)), 0.02, "dark_steel")
    for k in range(14):
        p = A + D * (LEN * (k + 0.5) / 14) + Nn * (R + 0.045)
        sphere((p.x, sy * (HW + 0.045), p.z), 0.013, "bolt", seg=8)
    p = A + D * (LEN * 0.45)
    box((p.x, sy * (HW + 0.045), p.z), (0.3, 0.012, 0.1), "hazard", rot=(0, -math.atan2(D.z, D.x), 0), bevel=0)
for sy in (-1, 1):
    P = [at(LTOT * k / 200)[0] + Vector((0, sy * 0.25, 0)) for k in range(201)]
    sweep(P, 0.02, "dark_steel", corr=0.4, pitch=0.06, seg=8)
for c in (A, Bh):
    cyl(tuple(c), R - 0.01, 0.46, "dark_steel", rot=(PI / 2, 0, 0), verts=6)
    cyl(tuple(c), 0.045, 0.78, "bare", rot=(PI / 2, 0, 0), verts=12)
for k in (0.33, 0.66):
    p = A + D * (LEN * k)
    for sy in (-1, 1):
        cyl((p.x, sy * (HW + 0.05), p.z), 0.05, 0.03, "bare", rot=(PI / 2, 0, 0), verts=12)
label(4, "the armoured bucket ladder: the buckets climb full", (0.12, -0.36, 0.95))

BUCKETS = []
for i in range(NB):
    pv = pivot((0, 0, 0))
    box((0, 0, 0.02), (0.46, 0.19, 0.025), "heat", bevel=0.004, parent=pv)
    box((0, -0.095, 0.09), (0.46, 0.025, 0.16), "heat", bevel=0.004, parent=pv)
    box((0, 0.09, 0.075), (0.46, 0.022, 0.13), "heat", bevel=0.004, parent=pv)
    for sx in (-1, 1):
        box((sx * 0.23, 0, 0.085), (0.024, 0.19, 0.15), "dark_steel", bevel=0.003, parent=pv)
        box((sx * 0.25, 0, 0.02), (0.03, 0.09, 0.04), "dark_steel", bevel=0.003, parent=pv)
    box((0, 0.105, 0.145), (0.48, 0.03, 0.022), "bare", bevel=0.003, parent=pv)
    mo = box((0, 0, 0.125), (0.43, 0.16, 0.012), melt(f"bucket{i}", scale=18.0, k=1, axis="X"), bevel=0, parent=pv)
    BUCKETS.append((pv, mo, PITCH * i))


def climb(t, on):
    for pv, mo, s0 in BUCKETS:
        s = (s0 + (SPEED * PITCH * t if on else 0.0)) % LTOT
        p, tg, n = at(s)
        x = tg.cross(n)
        rot = Matrix((x, tg, n)).transposed()
        pv.matrix_basis = Matrix.Translation(p) @ rot.to_4x4()
        # full from the pool to the turn over the head; empty from there round to the pool
        full = (s < LEN + 0.55 * PI * R) or (s > LTOT - 0.3 * PI * R)
        mo.hide_render = not (on and full)


K.ANIM.append(climb)

# ---------------------------------------------------------------- the head and its drive
for sy in (-1, 1):
    strut((Bh.x - 0.32, sy * 0.44, 0.0), (Bh.x, sy * 0.4, Bh.z - 0.1), 0.045, "ochre")
    strut((Bh.x + 0.32, sy * 0.44, 0.0), (Bh.x, sy * 0.4, Bh.z - 0.1), 0.045, "ochre")
    strut((Bh.x - 0.2, sy * 0.43, 0.6), (Bh.x + 0.2, sy * 0.43, 0.6), 0.03, "ochre")
    box((Bh.x, sy * 0.4, Bh.z), (0.22, 0.12, 0.2), "dark_steel", bevel=0.01)
    for dx in (-0.08, 0.08):
        cyl((Bh.x + dx, sy * 0.4, Bh.z + 0.11), 0.016, 0.02, "bolt", verts=6, bevel=0)
    box((Bh.x, sy * 0.44, 0.06), (0.8, 0.14, 0.12), "dark_steel", bevel=0.01)
HOOD = [Bh + (R + 0.2) * (Nn * math.cos(th) + D * math.sin(th)) for th in [-0.2 + 1.5 * k / 10 for k in range(11)]]
HOOD += [Bh + (R + 0.25) * (Nn * math.cos(th) + D * math.sin(th)) for th in [1.3 - 1.5 * k / 10 for k in range(11)]]
plate_xz([(p.x, p.z) for p in HOOD], -HW - 0.04, HW + 0.04, "ochre")
label(5, "head tumbler and drive (gearbox, coupling, motor)", (Bh.x, -0.75, Bh.z))
# the drive on its frame, south of the head
for x in (0.52, 1.44):
    for y in (-1.44, -0.52):
        box((x, y, 0.5), (0.08, 0.08, 1.0), "ochre", bevel=0.008)
for z in (0.32, 0.96):
    for y in (-1.44, -0.52):
        box((0.98, y, z), (0.9, 0.06, 0.06), "ochre", bevel=0.006)
box((0.98, -0.98, 0.1), (1.0, 1.0, 0.2), "dark_steel", bevel=0.012)
cabinet(1.06, -1.1, 0.7, 0.62, 0.78, mat="grey", lamp=False)
id_panel((1.06, -1.42, 0.45), 0.3, 0.16, stripe="red")
for k in range(4):
    box((0.98, -1.35 + 0.25 * k, 1.0), (0.9, 0.04, 0.03), "dark_steel", bevel=0.003)
gearbox(Bh.x, -0.62, Bh.z - 0.15, 0.4, 0.32, 0.46, mat="green")
cyl((Bh.x, -0.43, Bh.z), 0.05, 0.12, "bare", rot=(PI / 2, 0, 0), verts=12)
box((Bh.x, -0.72, 1.07), (0.5, 0.5, 0.14), "dark_steel", bevel=0.01)
end = motor(1.18, -0.75, 1.24, d=(-1, 0), s=0.9, mat="green")
coupling(end[0] - 0.03, end[1], end[2], 0.1, axis=(1, 0, 0), turns=3)
ladder(1.47, -0.95, 0.1, 1.0, axis="y", mat="yellow")

# ---------------------------------------------------------------- the spill, the launder, the pot
SPX = Bh.x + R + 0.18
spill = box((SPX, 0.0, 1.42), (0.03, 0.2, 0.26), melt("spill", scale=22.0, k=4, axis="Z",
                                                         fn=lambda t: 0.75 + 0.25 * math.cos(4 * PI * t)),
            rot=(0, PI, 0), bevel=0)
K.ANIM.append(lambda t, on: setattr(spill, "hide_render", not on))
label(6, "the buckets tip: the spill into the launder", (SPX + 0.15, -0.12, 1.5))
LX, LY0, LY1 = SPX + 0.04, -0.3, 0.75
LZ0, LZ1 = 1.24, 1.06
tilt = math.atan2(LZ0 - LZ1, LY1 - LY0)
lpv = pivot((LX, (LY0 + LY1) / 2, (LZ0 + LZ1) / 2), (-tilt, 0, 0))
LL = math.hypot(LY1 - LY0, LZ0 - LZ1)
box((0, 0, 0), (0.34, LL, 0.2), "dark_steel", bevel=0.012, parent=lpv)
box((0.17, 0, 0.12), (0.04, LL, 0.2), "dark_steel", bevel=0.008, parent=lpv)
box((0, 0, 0.095), (0.24, LL - 0.04, 0.02), "refr", bevel=0.004, parent=lpv)
box((0, 0, 0.108), (0.16, LL - 0.06, 0.01), melt("launder", scale=10.0, k=2, axis="Y"), bevel=0, parent=lpv)
for y0, y1 in ((-0.25, 0.02), (0.18, 0.42)):
    box((0, (y0 + y1) / 2, 0.15), (0.32, y1 - y0, 0.08), "grey", bevel=0.01, parent=lpv)
    cyl((-0.1, (y0 + y1) / 2, 0.2), 0.025, 0.04, "brass", verts=8, parent=lpv)
for y in (-0.15, 0.45):
    z = LZ0 + (LZ1 - LZ0) * (y - LY0) / (LY1 - LY0)
    strut((LX, y, 0.0), (LX, y, z - 0.1), 0.035, "dark_steel")
label(7, "heated launder (heater lids, helium-blanketed)", (LX + 0.1, 0.35, 1.25))
PX, PY = 1.02, 1.04
box((PX, PY, 0.1), (0.94, 0.9, 0.2), "dark_steel", bevel=0.012)
cyl((PX, PY, 0.62), 0.4, 0.84, "refr", verts=40)
for z in (0.32, 0.72, 0.98):
    band(PX, PY, z, 0.4, h=0.06, mat="dark_steel", lugs=2, lug_a=-PI * 0.75)
head(PX, PY, 1.04, 0.4, 0.13, "heat")
manway_top(PX + 0.12, PY + 0.1, 1.12, r=0.08, nb=6)
label(8, "receiving pot", (PX, PY - 0.42, 0.8))
cyl(((PX - 0.38) / 2, 1.04, ZA), 0.17, PX - 0.38, "heat", rot=(0, PI / 2, 0), verts=32)
sphere((0.0, 1.04, ZA), 0.19, "heat", seg=24)
face_nozzle("N", 1.04, r=0.2, mat="heat", label_n=9, text="molten kamacite out (north face)")
cyl((0.42, 1.04, ZA), 0.24, 0.05, "bare", rot=(0, PI / 2, 0), verts=32)

# ---------------------------------------------------------------- helium in: the cover-gas manifold
face_nozzle("S", -1.2, r=0.2, mat="bare", label_n=1, text="helium-3 in (south face)")
box((0.0, -1.18, 0.3), (0.5, 0.34, 0.46), "grey", bevel=0.02)
handwheel((-0.12, -1.18, 0.62), 0.1, mat="red")
cyl((-0.12, -1.18, 0.57), 0.03, 0.1, "bare", verts=8)
gauge((0.14, -1.36, 0.42), (0, -1, 0.3), r=0.055, live=lambda t: 0.2 * math.sin(2 * PI * t))
pipe([(0.0, -1.05, 0.5), (-0.1, -0.85, 0.62), (-0.33, -0.66, ZS + 0.12)], r=0.04, mat="bare", flanges=True)
pipe([(0.15, -1.05, 0.45), (0.38, -0.7, 0.5), (0.45, -0.2, 0.7), (LX - 0.12, 0.25, 1.26)],
     r=0.03, mat="bare", flanges=True)
label(2, "cover-gas manifold: helium blankets sump and launder", (0.0, -1.18, 0.6))

# ---------------------------------------------------------------- the corners
# south-west: the launder heaters' transformer, its conservator and bushings
box((-1.04, -1.06, 0.34), (0.9, 0.86, 0.68), "cream", bevel=0.02)
for k in range(6):
    box((-1.45, -1.3 + 0.1 * k, 0.36), (0.02, 0.06, 0.5), "dark_steel", bevel=0.003)
cyl((-1.08, -0.82, 0.86), 0.1, 0.6, "cream", rot=(0, PI / 2, 0), verts=24)
for x in (-1.25, -1.05, -0.85):
    cyl((x, -1.15, 0.76), 0.04, 0.16, "ceramic", verts=12)
    cyl((x, -1.15, 0.86), 0.055, 0.03, "ceramic", verts=12)
trunk([(-0.85, -1.15, 0.88), (-0.6, -0.95, 0.9), (0.25, -0.95, 1.0), (0.6, -0.3, 1.2), (LX - 0.1, -0.1, 1.32)],
      r=0.032)
# north-west and west: the foot's take-up screws, the lube unit, the helium receiver
box((-1.23, 0.0, 0.3), (0.53, 1.2, 0.6), "ochre", bevel=0.02)
for sy in (-1, 1):
    cyl((-1.1, sy * 0.22, 0.6), 0.04, 0.6, "bare", rot=(0, PI / 2, 0), verts=12)
    cyl((-1.38, sy * 0.22, 0.6), 0.07, 0.06, "dark_steel", rot=(0, PI / 2, 0), verts=6)
box((-1.0, 1.02, 0.12), (0.98, 0.92, 0.24), "dark_steel", bevel=0.012)
vtank(-1.12, 1.12, 0.26, 1.05, mat="oxide", bands=(0.55,), nozzle=(0.0, 0.0))
label(10, "helium receiver", (-1.12, 0.84, 0.8))
box((-0.68, 0.82, 0.42), (0.28, 0.26, 0.36), "green", bevel=0.012)
cyl((-0.68, 0.82, 0.66), 0.08, 0.12, "dark_steel", verts=16)
hose([(-0.68, 0.72, 0.5), (-0.55, 0.55, 0.62), (-0.4, 0.4, 0.6)], r=0.03, mat="hose_k")
pipe([(-1.12, 0.86, 0.5), (-0.6, 0.5, 0.3), (0.0, 0.55, 0.3), (0.3, 0.75, 0.5), (0.5, 0.5, 0.9), (LX - 0.12, 0.6, 1.2)],
     r=0.028, mat="bare", flanges=True)
box((-0.3, 0.98, 0.15), (0.42, 0.5, 0.3), "oxide", bevel=0.015)
box((0.36, 0.62, 0.12), (0.4, 0.3, 0.24), "dark_steel", bevel=0.01)
box((1.13, 0.16, 0.2), (0.72, 0.9, 0.4), "dark_steel", bevel=0.015)
box((0.0, 1.12, 0.09), (1.2, 0.74, 0.18), "dark_steel", bevel=0.012)
box((-0.42, -1.16, 0.15), (0.3, 0.66, 0.3), "dark_steel", bevel=0.012)
cyl((-0.42, -1.16, 0.45), 0.11, 0.3, "bare", verts=24)
cyl((-0.42, -1.16, 0.62), 0.12, 0.04, "dark_steel", verts=24)
box((0.37, -1.16, 0.12), (0.22, 0.66, 0.24), "dark_steel", bevel=0.01)
stain(-0.3, 0.6, 0.25, 0.15)
stain(0.6, 0.25, 0.2, 0.15)
run(dict(name="the bucket ladder", footprint=[3, 3]), nf=NF)
