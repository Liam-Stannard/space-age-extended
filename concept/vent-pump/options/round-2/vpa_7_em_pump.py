"""Vent Pump, round 2, concept 7: THE ELECTROMAGNETIC PUMP (3 x 3).

  $BLENDER -b --python vpa_7_em_pump.py -- <out-dir> [--quick] [--only working|idle|rot] [--colourmap]

The melt conducts, so it is pushed by a travelling magnetic field and no part in the melt moves.
A refractory-lined wellhead sits on the vent; from it a flat duct climbs north at a slope through
three green coil yokes (laminated iron above and below, copper windings fore and aft), carried on
two A-frames, into a hot head elbow and down to the north face. Between the yokes the duct shows
slots where a packet of glow travels up with the flow. The yokes are cooled by helium-3: it comes
in at the south face, runs along a header to three small circulators on the east skid (their
couplings turning) and up their hoses into the yokes' jackets, and is bled into the bore at the
wellhead. The power train fills the west: a capacitor bank (south-west), the transformer with its
copper busbars up to the yokes (west), the frequency converter (north-west).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpa_kit import *  # noqa: F401,F403,E402
import vpa_kit as K  # noqa: E402

K.build_materials(((0.5, 0.3), (1.0, 0.35), (1.4, 0.3)))
NF = 32

S0 = Vector((0.0, -0.42, 0.8))       # the duct leaves the wellhead
S1 = Vector((0.0, 0.9, 1.5))        # and enters the head elbow
D = (S1 - S0).normalized()
LEN = (S1 - S0).length
TILT = math.atan2(D.z, D.y)


def on_axis(f, z=0.0, x=0.0):
    """A pivot on the duct's axis at fraction f, tilted with it: local X across, Y up the duct,
    Z its normal; offsets z (normal) and x (across)."""
    p = S0 + D * (LEN * f)
    return pivot((p.x + x, p.y - z * math.sin(TILT), p.z + z * math.cos(TILT)), (TILT, 0, 0))


# ---------------------------------------------------------------- the wellhead on the vent
WX, WY = 0.0, -0.32
cyl((WX, WY, 0.1), 0.66, 0.2, "dark_steel", verts=56)
bolts(WX, WY, 0.21, 0.6, 16, r=0.02)
cyl((WX, WY, 0.45), 0.52, 0.5, "refr", verts=48)
for z in (0.28, 0.62):
    cyl((WX, WY, z), 0.54, 0.05, "dark_steel", verts=48)
cyl((WX, WY, 0.72), 0.4, 0.06, "bare", verts=40)
bolts(WX, WY, 0.76, 0.36, 12, r=0.016)
# the duct's foot: a hot transition from the bore to the flat duct
fp = on_axis(-0.04)
box((0, 0, 0), (0.42, 0.22, 0.3), "heat", bevel=0.02, parent=fp)
label(3, "wellhead on the vent (refractory-lined)", (WX - 0.45, WY - 0.3, 0.5))

# ---------------------------------------------------------------- the duct and the yokes
dp = on_axis(0.5)
box((0, 0, 0), (0.3, LEN + 0.06, 0.12), "heat", bevel=0.012, parent=dp)
for sx in (-1, 1):
    box((sx * 0.16, 0, 0), (0.02, LEN + 0.06, 0.14), "dark_steel", bevel=0.004, parent=dp)
YF = (0.2, 0.5, 0.8)
YL = 0.2
for i, f in enumerate(YF):
    yp = on_axis(f)
    for sz in (-1, 1):
        box((0, 0, sz * 0.2), (0.9, YL, 0.26), "dark_steel", bevel=0.01, parent=yp)
        for k in range(6):
            box((0, -YL / 2 + 0.02 + (YL - 0.04) * k / 5, sz * 0.332), (0.86, 0.012, 0.006), "bare", bevel=0,
                parent=yp)
        # the windings fore and aft of the iron, copper, bound with tape
        for sy in (-1, 1):
            box((0, sy * (YL / 2 + 0.022), sz * 0.11), (0.7, 0.044, 0.09), "copper", bevel=0.015, parent=yp)
    for sx in (-1, 1):
        box((sx * 0.49, 0, 0), (0.08, YL, 0.68), "green", bevel=0.012, parent=yp)
        for zz in (-0.24, 0.24):
            cyl((sx * 0.535, 0, zz), 0.02, 0.02, "bolt", rot=(0, PI / 2, 0), verts=6, bevel=0, parent=yp)
        # the end turns: copper bundles bulging out of the cheeks, taped
        box((sx * 0.59, 0, 0), (0.12, YL + 0.1, 0.5), "copper", bevel=0.045, parent=yp)
        for zz in (-0.15, 0.0, 0.15):
            box((sx * 0.59, 0, zz), (0.125, YL + 0.105, 0.035), "cable_black", bevel=0.01, parent=yp)
    box((0, 0, 0.35), (0.92, YL - 0.03, 0.04), "green", bevel=0.008, parent=yp)
    box((0.26, 0, 0.4), (0.2, 0.15, 0.09), "grey", bevel=0.008, parent=yp)
    cyl((-0.26, 0, 0.39), 0.035, 0.05, "brass", verts=8, parent=yp)
    box((-0.05, 0, 0.375), (0.26, 0.1, 0.01), "hazard", bevel=0, parent=yp)
label(4, "three coil yokes clamp the duct (no moving part in the metal)", (-0.42, 0.05, 1.25))

# the slots between the yokes: the glow travels up them with the flow
SL = [(0.07, 0.08), (0.35, 0.15), (0.65, 0.15), (0.93, 0.08)]
for i, (f, ln) in enumerate(SL):
    sp = on_axis(f)
    box((0, 0, 0.062), (0.24, ln, 0.012), melt(f"slot{i}", scale=12.0, k=2, axis="Y", bright=1.4,
                                               fn=(lambda t, i=i: 0.45 + 0.55 * max(0.0, math.cos(
                                                   2 * PI * (2 * t - i / 4)) ** 3))), bevel=0, parent=sp)
    box((0, 0, 0.07), (0.25, ln + 0.01, 0.004), "pane", bevel=0, parent=sp)
    for sx in (-1, 1):
        box((sx * 0.14, 0, 0.07), (0.025, ln + 0.03, 0.02), "dark_steel", bevel=0.003, parent=sp)
label(5, "slots in the duct: the glow travels up with the melt", (0.25, 0.1, 1.15))

# the A-frames under the stator
for f in (0.35, 0.65):
    p = S0 + D * (LEN * f)
    for sx in (-1, 1):
        strut((sx * 0.55, p.y, 0.0), (sx * 0.42, p.y, p.z - 0.12), 0.045, "ochre")
        box((sx * 0.55, p.y, 0.05), (0.18, 0.18, 0.1), "dark_steel", bevel=0.008)
    strut((-0.44, p.y, p.z - 0.13), (0.44, p.y, p.z - 0.13), 0.04, "ochre")
    strut((-0.47, p.y, 0.4), (0.47, p.y, 0.4), 0.025, "ochre")

# ---------------------------------------------------------------- the head elbow and the outlet
hp = on_axis(1.06)
box((0, 0, 0), (0.42, 0.24, 0.34), "heat", bevel=0.03, parent=hp)
HY = S1.y + 0.2
box((0, HY, 1.32), (0.44, 0.34, 0.3), "heat", bevel=0.03)
box((0, HY, 1.48), (0.36, 0.26, 0.03), "dark_steel", bevel=0.006)
for sx in (-1, 1):
    for sy in (-1, 1):
        cyl((sx * 0.14, HY + sy * 0.09, 1.5), 0.016, 0.02, "bolt", verts=6, bevel=0)
cyl((0, HY, (1.17 + ZA) / 2), 0.17, 1.17 - ZA, "heat", verts=32)
for z in (0.75, 1.1):
    cyl((0, HY, z), 0.22, 0.05, "bare", verts=32)
sphere((0, HY, ZA), 0.19, "heat", seg=24)
face_nozzle("N", HY, r=0.2, mat="heat", label_n=6, text="molten kamacite out (north face)")
gauge((0.24, HY - 0.08, 1.36), (1, -1, 0.5), r=0.05)

# ---------------------------------------------------------------- helium in: the coolant circuit
face_nozzle("S", -1.18, r=0.2, mat="bare", label_n=1, text="helium-3 in (south face)")
box((0.0, -1.2, 0.26), (0.44, 0.24, 0.4), "grey", bevel=0.02)
handwheel((0.0, -1.2, 0.55), 0.09, mat="red")
cyl((0, -1.2, 0.5), 0.03, 0.08, "bare", verts=8)
gauge((0.15, -1.33, 0.36), (0, -1, 0.3), r=0.05, live=lambda t: 0.2 * math.sin(2 * PI * t))
pipe([(0.2, -1.2, 0.3), (0.55, -1.15, 0.3), (0.82, -1.0, 0.3), (0.82, 0.62, 0.3)], r=0.045, mat="bare",
     flanges=True)
label(2, "helium header to the yokes' circulators", (0.5, -1.15, 0.45))
# the east skid: three circulators, one a yoke, couplings turning
box((1.1, -0.44, 0.08), (0.79, 2.1, 0.16), "dark_steel", bevel=0.012)
box((1.12, -1.2, 0.3), (0.6, 0.5, 0.44), "grey", bevel=0.015)
gauge((1.0, -1.455, 0.36), (0, -1, 0.3), r=0.05)
for i, f in enumerate(YF):
    p = S0 + D * (LEN * f)
    y = p.y
    cyl((0.84, y, 0.32), 0.08, 0.22, "bare", rot=(0, PI / 2, 0), verts=20)
    cyl((0.84, y, 0.2), 0.04, 0.12, "bare", verts=12)
    end = motor(1.24, y, 0.3, d=(-1, 0), s=0.6, mat="green")
    coupling(end[0] - 0.02, end[1], end[2], 0.07, axis=(1, 0, 0), turns=2 + (i % 2))
    hose([(0.84, y, 0.42), (0.8, y - 0.04, 0.8), (0.75, y + 0.02, p.z + 0.2), (0.6, y, p.z + 0.3)],
         r=0.026, mat="hose_k")
label(7, "helium circulators cool the yokes (couplings turning)", (1.1, -0.65, 0.5))
pipe([(0.25, -0.75, 0.75), (0.2, -0.62, 0.62), (0.2, -0.45, 0.68)], r=0.03, mat="bare", flanges=True)

# ---------------------------------------------------------------- the power train, west
# south-west: the capacitor bank
box((-1.06, -1.08, 0.08), (0.86, 0.82, 0.16), "dark_steel", bevel=0.012)
for i in range(3):
    for j in range(2):
        x, y = -1.32 + 0.26 * i, -1.25 + 0.3 * j
        cyl((x, y, 0.42), 0.11, 0.52, "grey", verts=24)
        cyl((x, y, 0.7), 0.06, 0.06, "ceramic", verts=16)
        cyl((x, y, 0.75), 0.03, 0.04, "bare", verts=8)
label(8, "capacitor bank", (-1.06, -1.1, 0.8))
# west: the transformer, its copper busbars up to the yokes
box((-1.07, -0.14, 0.4), (0.84, 0.98, 0.8), "cream", bevel=0.02)
for k in range(7):
    box((-1.48, -0.45 + 0.1 * k, 0.42), (0.02, 0.06, 0.6), "dark_steel", bevel=0.003)
for i, y in enumerate((-0.35, -0.15, 0.05)):
    cyl((-0.86, y, 0.92), 0.04, 0.2, "ceramic", verts=12)
    for k in range(3):
        cyl((-0.86, y, 0.86 + 0.06 * k), 0.06, 0.02, "ceramic", verts=12)
    cyl((-1.2, y, 0.86), 0.05, 0.12, "dark_steel", verts=12)
    f = YF[i]
    p = S0 + D * (LEN * f)
    pts = [(-0.86, y, 1.04), (-0.86, y, 1.12 + 0.05 * i), (-0.75, p.y - 0.05, p.z + 0.25),
           (-0.6, p.y, p.z + 0.3)]
    for a_, b_ in zip(pts, pts[1:]):
        strut(a_, b_, 0.018, "copper")
label(9, "transformer and busbars", (-1.1, -0.15, 1.0))
# north-west: the frequency converter
cabinet(-1.04, 0.92, 0.9, 1.1, 1.1, mat="grey")
id_panel((-1.04, 0.365, 0.62), 0.34, 0.18, stripe="yellow")
for k in range(5):
    box((-1.3 + 0.13 * k, 0.92, 1.13), (0.06, 0.9, 0.04), "dark_steel", bevel=0.004)
bundle([(-0.7, 0.6, 1.05), (-0.55, 0.45, 1.3), (-0.2, 0.42, 1.45), (0.18, 0.44, 1.5)], cols=("black", "red", "yellow"),
       r=0.016)
trunk([(-0.85, -1.0, 0.75), (-0.75, -0.6, 0.85), (-0.82, -0.4, 0.95)], r=0.03)
# north-east: the helium return receiver
box((1.04, 1.04, 0.1), (0.9, 0.9, 0.2), "dark_steel", bevel=0.012)
vtank(1.08, 1.06, 0.3, 1.0, mat="yellow", bands=(0.45,), nozzle=(-0.3, -0.3))
pipe([(0.82, 0.62, 0.3), (0.82, 0.85, 0.35), (0.85, 1.0, 0.45)], r=0.04, mat="bare", flanges=True)
box((0.44, 1.16, 0.15), (0.34, 0.6, 0.3), "oxide", bevel=0.015)
box((-0.44, 1.2, 0.12), (0.3, 0.56, 0.24), "dark_steel", bevel=0.012)
box((0.5, -1.2, 0.12), (0.4, 0.56, 0.24), "dark_steel", bevel=0.012)
box((-0.45, -1.2, 0.14), (0.3, 0.56, 0.28), "dark_steel", bevel=0.012)
box((0.0, 0.62, 0.05), (1.3, 0.62, 0.1), "dark_steel", bevel=0.01)
for k in range(6):
    box((-0.55 + 0.22 * k, 0.62, 0.105), (0.02, 0.58, 0.012), "bare", bevel=0)
stain(0.0, 0.25, 0.3, 0.2)
stain(0.55, -0.6, 0.2, 0.12)
run(dict(name="the electromagnetic pump", footprint=[3, 3]), nf=NF)
