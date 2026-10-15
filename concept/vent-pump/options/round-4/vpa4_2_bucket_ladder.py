"""Vent Pump, round 4, concept 2: THE BUCKET LADDER (3 x 3). Round 3's (../round-3/vpa3_2_bucket_ladder.py)
with the helium sight glass in mix A (T03) standing after the flow meter, the tee to the two hoods on its
head; it drops and flushes pink as the hood purges.

  $BLENDER -b --python vpa4_2_bucket_ladder.py -- <out-dir> [--quick] [--only working|idle|rot] [--colourmap]

Round 2's bucket ladder (../round-2/vpa_2_bucket_ladder.py) with helium seen at work and every
pipe going somewhere. What helium does here: it is the cover gas -- it blankets the melt in the
sump and under the launder's sealed hood, and is purged out each time a bucket tips, so the
melt never meets anything else.

The run: helium-3 in at the south face to the inlet manifold, through the turning flow meter,
to a tee: one lagged branch into the sump's cover-gas hood, one along the drive frame and up the
east side into the launder's sealed hood. The buckets dip in the pool, climb the ladder, tip
into the launder's open mouth; the melt runs north under the hood (a sight window on it) into
the receiving pot and out of the north face. Each time a bucket tips the hood's two purge
valves lift in turn: the purged gas goes along the spent-gas header to the helium receiver
(north-west), whose recovery compressor pumps it back into the sump's hood.
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpa4_kit import *  # noqa: F401,F403,E402
import vpa_kit as K  # noqa: E402
from mathutils import Matrix  # noqa: E402

build_materials4(((0.5, 0.3), (1.1, 0.35), (1.4, 0.3)))
NF = 32
TIP = (0.0, 0.5)                     # a bucket tips (the spill's peak)
PURGE = (0.1, 0.6)                   # the hood's purge valves lift after it


def purge(t, i=0):
    return pulse(t, [c + 0.05 * i for c in PURGE], rise=0.04, fall=0.16)


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
    K.sc.collection.objects.link(o)
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
label(6, "the sump over the vent: the buckets dip in the melt pool", (-0.62, 0.1, ZS))
# the sump's cover-gas hood along its south lip (helium in from the tee, the recovered gas from the west)
box((-0.33, -0.48, ZS + 0.09), (0.9, 0.26, 0.18), "dark_steel", bevel=0.02)
box((-0.33, -0.48, ZS + 0.19), (0.8, 0.18, 0.02), "hazard", bevel=0)
for x in (-0.72, 0.06):
    cyl((x, -0.48, ZS + 0.21), 0.03, 0.04, "bolt", verts=6, bevel=0)
label(5, "the sump's cover-gas hood (helium blanket)", (-0.45, -0.48, ZS + 0.2))

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
label(7, "the armoured bucket ladder: the buckets climb full", (0.12, -0.36, 0.95))

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
label(8, "head tumbler and drive: the buckets tip", (Bh.x, -0.75, Bh.z))
# the drive on its frame, south of the head (pulled in from the corner)
FX0, FX1, FY0, FY1 = 0.52, 1.3, -1.3, -0.52
for x in (FX0, FX1):
    for y in (FY0, FY1):
        box((x, y, 0.5), (0.08, 0.08, 1.0), "ochre", bevel=0.008)
for z in (0.32, 0.96):
    for y in (FY0, FY1):
        box(((FX0 + FX1) / 2, y, z), (FX1 - FX0 + 0.08, 0.06, 0.06), "ochre", bevel=0.006)
pad(0.42, -1.495, 1.495, -0.42, 0.2, "dark_steel", cut=0.34, corners=("SE",))
cabinet3(0.93, -1.0, 0.56, 0.48, 0.74, mat="grey")
id_panel((0.93, -1.245, 0.45), 0.28, 0.15, stripe="red")
for k in range(4):
    box(((FX0 + FX1) / 2, FY0 + 0.05 + 0.23 * k, 1.0), (FX1 - FX0 + 0.06, 0.04, 0.03), "dark_steel", bevel=0.003)
gearbox(Bh.x, -0.62, Bh.z - 0.15, 0.4, 0.32, 0.46, mat="green")
cyl((Bh.x, -0.43, Bh.z), 0.05, 0.12, "bare", rot=(PI / 2, 0, 0), verts=12)
box((Bh.x, -0.72, 1.07), (0.5, 0.5, 0.14), "dark_steel", bevel=0.01)
end = motor(1.12, -0.75, 1.24, d=(-1, 0), s=0.9, mat="green")
coupling(end[0] - 0.03, end[1], end[2], 0.1, axis=(1, 0, 0), turns=3)
ladder(FX1 + 0.07, -0.95, 0.2, 1.0, axis="y", mat="yellow")

# ---------------------------------------------------------------- the spill, the launder and its sealed hood
SPX = Bh.x + R + 0.18
spill = box((SPX, 0.0, 1.42), (0.03, 0.2, 0.26), melt("spill", scale=22.0, k=4, axis="Z",
                                                         fn=lambda t: 0.75 + 0.25 * math.cos(4 * PI * t)),
            rot=(0, PI, 0), bevel=0)
K.ANIM.append(lambda t, on: setattr(spill, "hide_render", not on))
label(9, "the buckets tip: the spill into the launder's mouth", (SPX + 0.15, -0.12, 1.5))
LX, LY0, LY1 = SPX + 0.04, -0.3, 0.75
LZ0, LZ1 = 1.24, 1.06
tilt = math.atan2(LZ0 - LZ1, LY1 - LY0)
LC = Vector((LX, (LY0 + LY1) / 2, (LZ0 + LZ1) / 2))
lpv = pivot(tuple(LC), (-tilt, 0, 0))
LL = math.hypot(LY1 - LY0, LZ0 - LZ1)


def W(lx, ly, lz):
    """The launder's local frame to world."""
    c, s = math.cos(tilt), math.sin(tilt)
    return (LC.x + lx, LC.y + ly * c + lz * s, LC.z - ly * s + lz * c)


box((0, 0, 0), (0.34, LL, 0.2), "dark_steel", bevel=0.012, parent=lpv)
box((0.17, 0, 0.12), (0.04, LL, 0.2), "dark_steel", bevel=0.008, parent=lpv)
box((0, 0, 0.095), (0.24, LL - 0.04, 0.02), "refr", bevel=0.004, parent=lpv)
box((0, -LL / 2 + 0.22, 0.108), (0.16, 0.4, 0.01), melt("launder", scale=10.0, k=2, axis="Y"), bevel=0, parent=lpv)
# the sealed hood over the rest of the run: bolted, a sight window on the melt beneath
HY0, HY1 = -0.08, LL / 2
box((0, (HY0 + HY1) / 2, 0.18), (0.36, HY1 - HY0, 0.16), "grey", bevel=0.014, parent=lpv)
for yy in (HY0 + 0.03, HY1 - 0.03):
    box((0, yy, 0.18), (0.38, 0.03, 0.17), "dark_steel", bevel=0.004, parent=lpv)
for k in range(6):
    yy = HY0 + 0.05 + (HY1 - HY0 - 0.1) * k / 5
    for sx in (-1, 1):
        cyl((sx * 0.17, yy, 0.262), 0.012, 0.012, "bolt", verts=6, bevel=0, parent=lpv)
WY = (HY0 + HY1) / 2
box((-0.05, WY, 0.258), (0.12, 0.2, 0.012), "dark_steel", bevel=0.003, parent=lpv)
box((-0.05, WY, 0.262), (0.08, 0.16, 0.01), melt("hoodwin", scale=10.0, k=2, axis="Y"), bevel=0, parent=lpv)
box((-0.05, WY, 0.268), (0.085, 0.165, 0.004), "pane", bevel=0, parent=lpv)
label(10, "the launder's sealed hood: a helium blanket over the melt", W(0.0, WY, 0.3))
for y in (-0.15, 0.45):
    z = LZ0 + (LZ1 - LZ0) * (y - LY0) / (LY1 - LY0)
    strut((LX, y, 0.0), (LX, y, z - 0.1), 0.035, "dark_steel")
# the purge valves on the hood's top; their vents into the spent-gas header along its west edge
POPS = []
for i, ly in enumerate((HY0 + 0.1, HY1 - 0.1)):
    x, y, z = W(0.08, ly, 0.26)
    poppet(x, y, z, (lambda t, i=i: purge(t, i)), lift=0.06, r=0.05)
    POPS.append((x, y, z))
label(11, "purge valves: lift in turn after each tip", W(0.08, HY1 - 0.1, 0.45))
HDR0, HDR1 = W(-0.14, HY0 + 0.06, 0.26), W(-0.14, HY1, 0.36)
for x, y, z in POPS:
    pipe([(x - 0.05, y, z + 0.06), (x - 0.12, y, z + 0.1), (HDR0[0] + 0.035, y, z + 0.1)], r=0.022, mat="bare",
         flanges=False)
RV = (-1.05, 1.05)
spent_line([HDR0, W(-0.14, HY0 + 0.12, 0.34), HDR1, (HDR1[0] - 0.05, HDR1[1] + 0.12, HDR1[2] + 0.12), (0.6, 0.86, 1.45),
            (-0.5, 0.82, 1.45), (RV[0] + 0.1, RV[1] - 0.05, 1.4), (RV[0], RV[1], 1.24), (RV[0], RV[1], 1.17)], r=0.04)
label(12, "spent-gas header to the helium receiver", (-0.2, 0.82, 1.45))

# ---------------------------------------------------------------- the receiving pot and the outlet
PX, PY = 1.02, 1.04
pad(0.55, 0.59, 1.495, 1.495, 0.2, "dark_steel", cut=0.34, corners=("NE",))
cyl((PX, PY, 0.62), 0.4, 0.84, "refr", verts=40)
for z in (0.32, 0.72, 0.98):
    band(PX, PY, z, 0.4, h=0.06, mat="dark_steel", lugs=2, lug_a=-PI * 0.75)
head(PX, PY, 1.04, 0.4, 0.13, "heat")
manway_top(PX + 0.12, PY + 0.1, 1.12, r=0.08, nb=6)
label(13, "receiving pot", (PX, PY - 0.42, 0.8))
cyl(((PX - 0.38) / 2, 1.04, ZA), 0.17, PX - 0.38, "heat", rot=(0, PI / 2, 0), verts=32)
sphere((0.0, 1.04, ZA), 0.19, "heat", seg=24)
face_nozzle("N", 1.04, r=0.2, mat="heat", label_n=14, text="molten kamacite out (north face)")
cyl((0.42, 1.04, ZA), 0.24, 0.05, "bare", rot=(0, PI / 2, 0), verts=32)
top = A + Nn * R
melt_path([(-0.33, 0.0, ZS - 0.1), tuple(top), tuple(A + Nn * R + D * LEN), (SPX, 0.0, 1.55), (SPX, 0.0, 1.3)])
melt_path([W(0, -LL / 2, 0.1), W(0, LL / 2, 0.1), (PX - 0.1, PY - 0.1, 1.0), (PX, PY, 0.6), (PX, PY, ZA),
           (0.4, 1.04, ZA), (0.0, 1.04, ZA), (0.0, 1.5, ZA)])

# ---------------------------------------------------------------- helium in: manifold, meter, tee
face_nozzle("S", -1.2, r=0.2, mat="bare", label_n=1, text="helium-3 in (south face)")
box((0.0, -1.18, 0.3), (0.5, 0.34, 0.46), "grey", bevel=0.02)
handwheel((-0.12, -1.18, 0.62), 0.1, mat="red")
cyl((-0.12, -1.18, 0.57), 0.03, 0.1, "bare", verts=8)
gauge((0.14, -1.36, 0.42), (0, -1, 0.3), r=0.055, live=lambda t: 0.3 * purge(t))
label(2, "inlet manifold", (0.0, -1.18, 0.6))
he_line([(0.0, -1.08, 0.53), (-0.2, -1.0, 0.56), (-0.24, -0.9, 0.56), (-0.13, -0.88, 0.56)], r=0.05, bands=0,
        kind=None)
m_in, m_out = flow_meter(0.06, -0.88, 0.56, d=(1, 0), turns=4, ease=burst_ease(PURGE, base=0.4))
label(3, "helium flow meter (spurts as the hood purges)", (0.06, -0.88, 0.7))
record("helium", [(0, -1.5, ZA), (0, -1.18, 0.4), (0.0, -1.08, 0.53), (-0.2, -1.0, 0.56), (-0.24, -0.9, 0.56),
                  m_in])
# the sight tank after the meter (round 4): in at its foot, out of its head into the tee on top of it
G0_, G1_ = (0.38, -0.86, 0.3), (0.38, -0.86, 1.1)
ga, gb = axis_pts(G0_, G1_, 0.1)
sight_tank(G0_, G1_, stroke_pulse(PURGE, rise=0.05, fall=0.36), r=0.14)
record("helium", [G0_, G1_, (0.38, -0.86, 1.3)])
he_line([m_out, (0.32, -0.92, 0.36), ga, G0_], r=0.05, bands=0, kind="helium")
label(17, "helium sight glass: the level drops and flushes pink as the hood purges", (0.38, -0.86, 0.7))
# the tee on the tank's head: one branch into the sump's hood, one to the launder's hood
TEE = (0.38, -0.86, 1.3)
box(TEE, (0.12, 0.12, 0.12), "bare", bevel=0.008)
he_line([G1_, gb, (TEE[0], TEE[1], TEE[2] - 0.06)], r=0.05, bands=0, kind=None)
he_line([(TEE[0] - 0.06, TEE[1], TEE[2]), (0.22, -0.78, 1.22), (0.06, -0.68, 0.9), (0.0, -0.64, 0.7),
         (0.0, -0.62, 0.62)], r=0.05, bands=0)
he_line([(TEE[0] + 0.06, TEE[1], TEE[2]), (0.5, -0.82, 1.28), (0.62, -0.68, 1.1), (0.7, -0.67, 0.75),
         (0.8, -0.66, 0.6), (1.2, -0.66, 0.6), (FX1 - 0.12, -0.45, 0.66), (FX1 - 0.12, -0.15, 0.95),
         (FX1 - 0.12, 0.1, 1.3), W(0.24, 0.05, 0.2), W(0.185, 0.05, 0.2)], r=0.055)
gauge(W(0.27, 0.22, 0.24), (1, -0.6, 0.6), r=0.065, live=lambda t: -1.2 * purge(t) + 0.3)
cyl(W(0.22, 0.22, 0.24), 0.018, 0.08, "bare", rot=(0, PI / 2, 0), verts=8)
label(4, "lagged helium line to the launder's hood (gauge drops at each purge)", (FX1 - 0.12, -0.3, 0.8))

# ---------------------------------------------------------------- recovery: receiver, compressor, back to the sump
pad(-1.495, 0.56, -0.51, 1.495, 0.24, "dark_steel", cut=0.34, corners=("NW",))
vtank(RV[0], RV[1], 0.26, 1.05, mat="oxide", bands=(0.55,), nozzle=None)
label(15, "helium receiver (the purged gas)", (RV[0], RV[1] - 0.28, 0.8))
box((-0.68, 0.82, 0.42), (0.28, 0.26, 0.36), "green", bevel=0.012)
cyl((-0.68, 0.82, 0.66), 0.08, 0.12, "dark_steel", verts=16)
spent_line([(RV[0] + 0.2, RV[1] - 0.17, 0.42), (-0.86, 0.86, 0.42), (-0.82, 0.84, 0.42)], r=0.035)
label(16, "recovery compressor", (-0.68, 0.82, 0.7))
he_line([(-0.68, 0.82, 0.72), (-0.72, 0.7, 0.86), (-0.9, 0.4, 0.82), (-0.9, -0.2, 0.8), (-0.86, -0.44, 0.66),
         (-0.79, -0.48, 0.61)], r=0.045, kind="spent")

# ---------------------------------------------------------------- the corners and the clutter
# south-west: the launder heaters' transformer (chamfered), its conservator and bushings
pad(-1.495, -1.495, -0.59, -0.63, 0.68, "cream", cut=0.32, corners=("SW",), bevel=0.02)
for k in range(5):
    box((-1.505, -1.2 + 0.1 * k, 0.36), (0.02, 0.06, 0.5), "dark_steel", bevel=0.003)
cyl((-1.0, -0.82, 0.86), 0.1, 0.6, "cream", rot=(0, PI / 2, 0), verts=24)
for x in (-1.2, -1.0, -0.8):
    cyl((x, -1.15, 0.76), 0.04, 0.16, "ceramic", verts=12)
    cyl((x, -1.15, 0.86), 0.055, 0.03, "ceramic", verts=12)
trunk([(-0.8, -1.15, 0.88), (-0.6, -1.38, 0.95), (0.3, -1.42, 1.05), (1.42, -1.35, 1.06), (1.42, -0.6, 1.1),
       (1.36, -0.4, 1.2), W(0.21, -LL / 2 + 0.08, 0.12)], r=0.032)
# west: the foot's take-up screws
box((-1.23, 0.0, 0.3), (0.53, 1.0, 0.6), "ochre", bevel=0.02)
for sy in (-1, 1):
    cyl((-1.1, sy * 0.22, 0.6), 0.04, 0.6, "bare", rot=(0, PI / 2, 0), verts=12)
    cyl((-1.38, sy * 0.22, 0.6), 0.07, 0.06, "dark_steel", rot=(0, PI / 2, 0), verts=6)
box((-0.3, 1.02, 0.15), (0.42, 0.42, 0.3), "oxide", bevel=0.015)
box((0.36, 0.62, 0.12), (0.4, 0.3, 0.24), "dark_steel", bevel=0.01)
box((1.13, 0.06, 0.2), (0.72, 0.7, 0.4), "dark_steel", bevel=0.015)
box((0.1, 1.12, 0.09), (0.9, 0.74, 0.18), "dark_steel", bevel=0.012)
box((-0.42, -1.16, 0.15), (0.3, 0.66, 0.3), "dark_steel", bevel=0.012)
stain(-0.3, 0.6, 0.25, 0.15)
stain(0.6, 0.25, 0.2, 0.15)
run4(dict(name="the bucket ladder", footprint=[3, 3], tips=list(TIP), purges=list(PURGE)), nf=NF)
