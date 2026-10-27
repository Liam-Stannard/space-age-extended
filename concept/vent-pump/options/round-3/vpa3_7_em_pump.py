"""Vent Pump, round 3, concept 7: THE ELECTROMAGNETIC PUMP (3 x 3).

  $BLENDER -b --python vpa3_7_em_pump.py -- <out-dir> [--quick] [--only working|idle|rot] [--colourmap]

Round 2's electromagnetic pump (../round-2/vpa_7_em_pump.py) with helium seen at work and every
pipe going somewhere. What helium does here: it is the coolant -- three circulators drive it
through the coil yokes' jackets, and the warm gas is bled into the bore at the wellhead.

The melt conducts, so a travelling magnetic field pushes it up a flat duct through three green
coil yokes; glow packets travel up the slots between them. The run: helium-3 in at the south face
to the inlet valve, through the turning flow meter, along a lagged header north beside the east
skid to a buffer receiver (north-east). Three circulators draw from the header (their couplings
turn) and push it up lagged lines into the jacket blocks on the yokes' east ends; the warm gas
leaves the yokes' tops into a return collector that runs down the duct and bleeds into the bore
at the wellhead, through a bleed valve whose gauge swings with each packet. The power train
fills the west: a capacitor bank (south-west), the transformer with its copper busbars up to the
yokes (west), the frequency converter (north-west).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpa3_kit import *  # noqa: F401,F403,E402
import vpa_kit as K  # noqa: E402

build_materials3(((0.5, 0.3), (1.0, 0.35), (1.4, 0.3)))
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


def wpt(f, x=0.0, z=0.0, ly=0.0):
    """The world point at local (x, ly, z) of the duct's frame at fraction f."""
    p = S0 + D * (LEN * f + ly)
    return (p.x + x, p.y - z * math.sin(TILT), p.z + z * math.cos(TILT))


def packet(t):
    """The travelling field's packets: two a loop, as the slots' glow."""
    return pulse(t, (0.0, 0.5), rise=0.06, fall=0.3)


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
label(9, "wellhead on the vent (the bleed enters its top)", (WX - 0.45, WY - 0.3, 0.5))
melt_path([(WX, WY, 0.3), (WX, WY, 0.75), tuple(wpt(-0.04)), tuple(wpt(1.0)), (0, S1.y + 0.2, 1.32),
           (0, S1.y + 0.2, ZA), (0, 1.5, ZA)])

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
label(10, "three coil yokes push the melt (no moving part in the metal)", (-0.42, 0.05, 1.25))

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
label(11, "slots in the duct: the glow travels up with the melt", (0.25, 0.1, 1.15))

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
face_nozzle("N", HY, r=0.2, mat="heat", label_n=12, text="molten kamacite out (north face)")
gauge((0.24, HY - 0.08, 1.36), (1, -1, 0.5), r=0.05)

# ---------------------------------------------------------------- helium in: the coolant circuit
face_nozzle("S", -1.18, r=0.2, mat="bare", label_n=1, text="helium-3 in (south face)")
box((0.0, -1.2, 0.26), (0.44, 0.24, 0.4), "grey", bevel=0.02)
handwheel((0.0, -1.2, 0.55), 0.09, mat="red")
cyl((0, -1.2, 0.5), 0.03, 0.08, "bare", verts=8)
gauge((-0.12, -1.33, 0.36), (0, -1, 0.3), r=0.05, live=lambda t: 0.3 * packet(t))
label(2, "inlet valve", (0.0, -1.2, 0.5))
box((0.5, -1.2, 0.12), (0.4, 0.56, 0.24), "dark_steel", bevel=0.012)
he_line([(0.22, -1.2, 0.32), (0.25, -1.2, 0.32)], r=0.05, bands=0, kind=None)
m_in, m_out = flow_meter(0.4, -1.2, 0.32, d=(1, 0), turns=4, ease=burst_ease((0.0, 0.5), base=0.6))
label(3, "helium flow meter (turns while working)", (0.4, -1.2, 0.45))
record("helium", [(0, -1.5, ZA), (0, -1.2, 0.3), (0.22, -1.2, 0.32), m_in])
HX, HZ = 0.62, 0.22
RVX, RVY = 1.08, 1.06
he_line([m_out, (0.64, -1.1, 0.26), (HX, -0.9, HZ), (HX, 0.3, HZ), (HX, 0.62, HZ), (0.7, 0.8, 0.3),
         (RVX - 0.21, RVY - 0.21, 0.35)], r=0.065)
label(4, "lagged helium header to the circulators", (HX, -0.6, 0.35))
# the east skid: three circulators drawing from the header, their couplings turning
pad(0.705, -1.495, 1.495, 0.61, 0.16, "dark_steel", cut=0.32, corners=("SE",))
box((1.04, -1.1, 0.3), (0.4, 0.4, 0.44), "grey", bevel=0.015)
gauge((1.0, -1.31, 0.36), (0, -1, 0.3), r=0.05, live=lambda t: 0.5 * packet(t))
for i, f in enumerate(YF):
    y = (S0 + D * (LEN * f)).y
    cyl((0.84, y, 0.32), 0.08, 0.22, "bare", rot=(0, PI / 2, 0), verts=20)
    cyl((0.84, y, 0.2), 0.04, 0.12, "bare", verts=12)
    end = motor(1.24, y, 0.3, d=(-1, 0), s=0.6, mat="green")
    coupling(end[0] - 0.02, end[1], end[2], 0.07, axis=(1, 0, 0), turns=2 + (i % 2))
    he_line([(HX + 0.05, y, HZ + 0.02), (0.68, y, 0.3), (0.73, y, 0.32)], r=0.035, bands=0)
    # up to the jacket block on the yoke's east end
    yp = on_axis(f)
    box((0.69, 0, 0.0), (0.06, YL + 0.06, 0.3), "grey", bevel=0.008, parent=yp)
    for zz in (-0.1, 0.1):
        cyl((0.725, 0, zz), 0.016, 0.02, "bolt", rot=(0, PI / 2, 0), verts=6, bevel=0, parent=yp)
    jx, jy, jz = wpt(f, 0.72, 0.05)
    he_line([(0.84, y, 0.4), (0.86, y, 0.6), (0.84, jy, jz - 0.15), (jx + 0.06, jy, jz), (jx, jy, jz)], r=0.04,
            bands=0.18)
    record("helium", [(HX, y, HZ), (0.84, y, 0.32)])
label(5, "helium circulators (couplings turning) into the yokes' jackets", (1.1, -0.65, 0.5))
label(6, "jacket blocks: the helium cools the coils", tuple(wpt(0.5, 0.72, 0.2)))
# the warm gas: off each yoke's top to the return collector, down the duct, bled into the bore
CX_, CZ_ = -0.3, 0.52
for f in YF:
    a_ = wpt(f, -0.26, 0.39)
    b_ = wpt(f, CX_, CZ_)
    pipe([a_, (a_[0], a_[1], a_[2] + 0.05), b_], r=0.025, mat="bare", flanges=False)
col_pts = [wpt(YF[-1] + 0.06, CX_, CZ_), wpt(YF[-1], CX_, CZ_), wpt(YF[0], CX_, CZ_), wpt(0.02, CX_, CZ_ - 0.05),
           (-0.32, -0.62, 1.0), (-0.3, -0.6, 0.9), (-0.28, -0.56, 0.8)]
spent_line(col_pts, r=0.04)
cyl((-0.28, -0.56, 0.86), 0.06, 0.08, "bare", verts=16)
handwheel((-0.28, -0.56, 0.98), 0.06, mat="red")
gauge((-0.42, -0.6, 0.95), (-0.4, -1, 0.6), r=0.06, live=lambda t: 1.2 * packet(t) - 0.2)
label(7, "return collector: the warm gas off the yokes", tuple(wpt(0.6, CX_, CZ_ + 0.1)))
label(8, "bleed valve: the gas into the bore (gauge swings with each packet)", (-0.36, -0.62, 0.9))
record("spent", [(-0.28, -0.56, 0.8), (-0.2, -0.4, 0.6), (WX, WY, 0.5)])

# ---------------------------------------------------------------- the power train, west
# south-west: the capacitor bank
pad(-1.495, -1.495, -0.63, -0.67, 0.16, "dark_steel", cut=0.32, corners=("SW",))
for i in range(3):
    for j in range(2):
        x, y = -1.26 + 0.25 * i, -1.19 + 0.29 * j
        cyl((x, y, 0.42), 0.11, 0.52, "grey", verts=24)
        cyl((x, y, 0.7), 0.06, 0.06, "ceramic", verts=16)
        cyl((x, y, 0.75), 0.03, 0.04, "bare", verts=8)
label(13, "capacitor bank", (-1.06, -1.1, 0.8))
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
    e_ = wpt(f, -0.6, 0.25)
    pts = [(-0.86, y, 1.04), (-0.86, y, 1.12 + 0.05 * i), (-0.75, e_[1] - 0.04, e_[2] + 0.06), e_]
    for a_, b_ in zip(pts, pts[1:]):
        strut(a_, b_, 0.018, "copper")
label(14, "transformer and busbars", (-1.1, -0.15, 1.0))
# north-west: the frequency converter
cabinet3(-1.04, 0.92, 0.9, 1.1, 1.1, mat="grey", corner=("NW",), cut=0.3)
id_panel((-1.04, 0.365, 0.62), 0.34, 0.18, stripe="yellow")
for k in range(5):
    box((-1.22 + 0.11 * k, 0.86, 1.13), (0.06, 0.8, 0.04), "dark_steel", bevel=0.004)
tb = wpt(YF[-1], -0.26, 0.42)
bundle([(-0.7, 0.6, 1.05), (-0.55, 0.62, 1.4), (tb[0] - 0.15, tb[1], tb[2] + 0.12), tb],
       cols=("black", "red", "yellow"), r=0.016)
trunk([(-0.85, -1.0, 0.75), (-0.75, -0.7, 0.88), (-0.8, -0.5, 0.82)], r=0.03)
# north-east: the helium return receiver
pad(0.59, 0.59, 1.495, 1.495, 0.2, "dark_steel", cut=0.32, corners=("NE",))
vtank(RVX, RVY, 0.3, 1.0, mat="yellow", bands=(0.45,), nozzle=None)
cyl((RVX + 0.1, RVY + 0.05, 1.12), 0.035, 0.1, "bare", verts=12)
cyl((RVX + 0.1, RVY + 0.05, 1.19), 0.05, 0.05, "red", verts=12)
label(15, "helium buffer receiver (the header's end)", (RVX, RVY - 0.3, 0.7))
box((0.44, 1.16, 0.15), (0.34, 0.6, 0.3), "oxide", bevel=0.015)
box((-0.44, 1.2, 0.12), (0.3, 0.56, 0.24), "dark_steel", bevel=0.012)
box((-0.45, -1.2, 0.14), (0.3, 0.56, 0.28), "dark_steel", bevel=0.012)
box((0.0, 0.62, 0.05), (1.3, 0.62, 0.1), "dark_steel", bevel=0.01)
for k in range(6):
    box((-0.55 + 0.22 * k, 0.62, 0.105), (0.02, 0.58, 0.012), "bare", bevel=0)
stain(0.0, 0.25, 0.3, 0.2)
stain(0.55, -0.6, 0.2, 0.12)
run3(dict(name="the electromagnetic pump", footprint=[3, 3]), nf=NF)
