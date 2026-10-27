"""Vent Pump, round 2, concept 5: THE SIPHON BELL (3 x 3).

  $BLENDER -b --python vpa_5_siphon_bell.py -- <out-dir> [--quick] [--only working|idle|rot] [--colourmap]

A squat, ribbed, oxide-red bell is sealed over the vent: a bolted skirt held down by a ring of
hydraulic clamps. Helium-3 comes in at the south face, through the charging valve, into the
bell's flank; it pressurises the bell and forces the melt up a heavy gooseneck from the crown,
over an arch (its sight window lit as each surge passes) and down to the north face. Then the
three vent valves on the bell's shoulder lift, the spent gas goes round a vent header to the
recovery receiver in the north-east corner, the bell refills from the vent, and the cycle runs
again. The clamps' hydraulic power unit (south-east) and the charging bottles (south-west) and
the switch cabinet (north-west) fill the corners. Two cycles a loop.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpa_kit import *  # noqa: F401,F403,E402
import vpa_kit as K  # noqa: E402

K.build_materials(((0.45, 0.3), (1.0, 0.35), (1.4, 0.3)))
NF = 32
K.SUN_E = 11.5                      # the oxide bell reads dark at the kit's 10
CYC = (-0.08, 0.42)                 # the charge: helium in, the melt surges (at its height in frame 0)
VENT = (0.16, 0.66)                 # the vents lift


def surge(t):
    return pulse(t, [c + 0.02 for c in CYC], rise=0.06, fall=0.22)


def venting(t, i=0):
    return pulse(t, [c + 0.025 * i for c in VENT], rise=0.04, fall=0.16)


BX, BY = 0.0, -0.08
RB, ZC, ZD = 0.84, 0.72, 0.5        # the bell's radius, its cylinder's top, the dome's height
# ---------------------------------------------------------------- the bell, sealed over the vent
cyl((BX, BY, 0.08), 1.0, 0.16, "dark_steel", verts=72)
cyl((BX, BY, 0.22), 0.94, 0.12, "dark_steel", verts=72)
bolts(BX, BY, 0.29, 0.9, 32, r=0.018)
cyl((BX, BY, (0.28 + ZC) / 2), RB, ZC - 0.28, "oxide", verts=72)
head(BX, BY, ZC, RB, ZD, "oxide")
for z in (0.36, ZC - 0.02):
    cyl((BX, BY, z), RB + 0.02, 0.05, "dark_steel", verts=72)
# twelve ribs down the dome and the wall
for k in range(12):
    a = PI / 12 + 2 * PI * k / 12
    pts = []
    for j in range(9):
        ph = (PI / 2) * j / 8 * 0.86
        r_ = RB * math.cos(ph) + 0.03
        pts.append((BX + r_ * math.cos(a), BY + r_ * math.sin(a), ZC + ZD * math.sin(ph) + 0.01))
    pts = [(BX + (RB + 0.03) * math.cos(a), BY + (RB + 0.03) * math.sin(a), 0.3)] + pts
    P = catmull(pts, step=0.02)
    sweep(P, 0.028, "dark_steel", seg=6)
# the hold-down clamps round the skirt: a bracket and a hydraulic cylinder each
for k in range(12):
    a = 2 * PI * k / 12
    c, s_ = math.cos(a), math.sin(a)
    box((BX + 1.02 * c, BY + 1.02 * s_, 0.2), (0.18, 0.12, 0.4), "dark_steel", rz=a, bevel=0.01)
    box((BX + 0.93 * c, BY + 0.93 * s_, 0.42), (0.2, 0.1, 0.05), "dark_steel", rz=a, bevel=0.006)
    cyl((BX + 1.08 * c, BY + 1.08 * s_, 0.5), 0.045, 0.2, "yellow", verts=12)
    cyl((BX + 1.08 * c, BY + 1.08 * s_, 0.62), 0.02, 0.06, "bare", verts=8)
label(3, "the bell, sealed over the vent: skirt, hold-down clamps", (BX - 0.7, BY - 0.62, 0.5))
stencil((BX, BY - RB - 0.01, 0.52), (0.42, 0.012, 0.1))
box((BX + 0.32, BY - RB + 0.06, 0.52), (0.18, 0.012, 0.1), "hazard", rz=-0.4, bevel=0)

# ---------------------------------------------------------------- the vents on the shoulder
VA = (PI * 1.15, PI * 1.5, PI * 1.85)
POP = []
for i, a in enumerate(VA):
    r_ = RB * 0.62
    ph = math.acos(0.62)
    x, y, z = BX + r_ * math.cos(a), BY + r_ * math.sin(a), ZC + ZD * math.sin(ph)
    cyl((x, y, z + 0.05), 0.08, 0.14, "bare", verts=20)
    cyl((x, y, z + 0.13), 0.1, 0.03, "dark_steel", verts=20)
    bolts(x, y, z + 0.15, 0.085, 6, r=0.011)
    pv = pivot((x, y, z + 0.16))
    cyl((0, 0, 0.03), 0.07, 0.05, "red", verts=20, parent=pv)
    cyl((0, 0, 0.08), 0.02, 0.06, "bare", verts=8, parent=pv)
    cyl((0, 0, 0.115), 0.045, 0.015, "dark_steel", verts=6, parent=pv)
    POP.append((pv, (x, y, z + 0.16), i))
    # each vent's tail to the header ring
    pipe([(x, y, z + 0.1), (x * 1.25, y * 1.1 + BY * -0.1, z + 0.02), (x * 1.42, y * 1.25, 1.0)], r=0.03, mat="bare",
         flanges=False)


def lift(t, on):
    for pv, (x, y, z), i in POP:
        pv.location = (x, y, z + (0.07 * venting(t, i) if on else 0.0))


K.ANIM.append(lift)
label(5, "vent valves: lift in turn to let the spent gas off", (BX, BY - 0.6, 1.25))
# the vent header: half a ring round the south of the dome, up to the receiver
ring_pts = [(BX + 1.18 * math.cos(a), BY + 1.18 * math.sin(a) * 0.98, 1.0)
            for a in [PI * 0.95 + PI * 1.05 * k / 16 for k in range(17)]]
pipe(ring_pts + [(1.0, 0.45, 1.05), (1.02, 0.85, 1.2)], r=0.045, mat="bare", flanges=True)
for a in [PI * 1.1 + PI * 0.8 * k / 4 for k in range(5)]:
    x, y = BX + 1.18 * math.cos(a), BY + 1.18 * math.sin(a) * 0.98
    strut((x, y, 0.6), (x, y, 0.96), 0.022, "dark_steel")

# ---------------------------------------------------------------- the gooseneck and the outlet
cyl((BX, BY, ZC + ZD + 0.02), 0.26, 0.1, "dark_steel", verts=40)
bolts(BX, BY, ZC + ZD + 0.08, 0.23, 12, r=0.015)
GN = [(BX, BY, ZC + ZD), (BX, BY + 0.02, 1.7), (BX, 0.14, 2.08), (BX, 0.5, 2.24), (BX, 0.86, 2.1), (BX, 1.04, 1.7),
      (BX, 1.06, 1.0), (BX, 1.06, ZA + 0.2), (BX, 1.12, ZA)]
_, GP, GT, GS = sweep(catmull(GN, step=0.01), 0.17, "heat", seg=24)
for f in (0.12, 0.62, 0.88):
    i = int(f * (len(GP) - 1))
    cyl(tuple(GP[i]), 0.22, 0.05, "bare", rot=tuple(along(GT[i])), verts=32)
# the window on the arch's crown, its melt beneath
WY0, WY1, WZ = 0.26, 0.74, 2.0
i0 = min((i for i in range(len(GP)) if GP[i].z > 1.7), key=lambda i: abs(GP[i].y - (WY0 + WY1) / 2))
crown = GP[i0]
zt = crown.z + 0.17
for sx in (-1, 1):
    box((sx * 0.1, (WY0 + WY1) / 2, zt - 0.01), (0.05, WY1 - WY0 + 0.1, 0.09), "dark_steel", bevel=0.006)
    for y in (WY0, (WY0 + WY1) / 2, WY1):
        sphere((sx * 0.1, y, zt + 0.035), 0.012, "bolt", seg=8)
for y in (WY0 - 0.03, WY1 + 0.03):
    box((0, y, zt + 0.0), (0.26, 0.05, 0.05), "dark_steel", bevel=0.006)
wm = box((0, (WY0 + WY1) / 2, zt + 0.006), (0.15, WY1 - WY0, 0.024),
         melt("gooseneck", scale=12.0, k=2, axis="Y", bright=1.3, fn=lambda t: 0.15 + 0.85 * surge(t)), bevel=0)
box((0, (WY0 + WY1) / 2, zt + 0.027), (0.16, WY1 - WY0, 0.006), "pane", bevel=0)
label(6, "the gooseneck: its window glows as each surge passes", (0.25, 0.5, 2.0))
sphere((BX, 1.12, ZA), 0.19, "heat", seg=24)
face_nozzle("N", 1.1, r=0.2, mat="heat", label_n=7, text="molten kamacite out (north face)")
# a stand under the gooseneck's down leg
for sx in (-1, 1):
    strut((sx * 0.3, 1.06, 0.0), (sx * 0.2, 1.06, 1.25), 0.035, "ochre")
strut((-0.26, 1.06, 0.9), (0.26, 1.06, 0.9), 0.025, "ochre")

# ---------------------------------------------------------------- helium in, the charging valve
face_nozzle("S", -1.2, r=0.2, mat="bare", label_n=1, text="helium-3 in (south face)")
box((0, -1.2, 0.3), (0.46, 0.26, 0.48), "grey", bevel=0.02)
cyl((0, -1.2, 0.6), 0.09, 0.14, "yellow", verts=20)
cyl((0, -1.2, 0.69), 0.1, 0.03, "dark_steel", verts=20)
gauge((0.16, -1.34, 0.4), (0, -1, 0.3), r=0.055, live=lambda t: 0.8 * surge(t))
pipe([(0.0, -1.07, 0.42), (0.0, -0.98, 0.5), (BX, BY - RB - 0.02, 0.52)], r=0.06, mat="bare", flanges=True)
label(2, "charging valve: helium into the bell's flank", (0.0, -1.2, 0.75))

# ---------------------------------------------------------------- the corners
# south-west: the charging bottles
skid(-1.497, -1.497, -0.6, -0.72, 0.1)
bottle_rack(-1.06, -1.1, n=4, axis="x", L=0.62, r=0.08, z0=0.1)
pipe([(-0.68, -1.1, 0.3), (-0.4, -1.2, 0.3), (-0.23, -1.2, 0.3)], r=0.035, mat="bare", flanges=False)
label(8, "charging bottles", (-1.06, -1.1, 0.4))
# south-east: the clamps' hydraulic power unit, its pump turning
box((1.06, -1.06, 0.1), (0.86, 0.86, 0.2), "dark_steel", bevel=0.012)
box((1.06, -0.92, 0.42), (0.7, 0.5, 0.44), "green", bevel=0.02)
cyl((1.25, -0.92, 0.7), 0.06, 0.12, "dark_steel", verts=16)
end = motor(0.84, -1.3, 0.38, d=(1, 0), s=0.85, mat="green")
coupling(end[0] + 0.04, end[1], end[2], 0.09, axis=(1, 0, 0), turns=3)
box((1.32, -1.3, 0.36), (0.22, 0.2, 0.26), "dark_steel", bevel=0.01)
label(9, "clamp hydraulics (pump turning)", (1.06, -0.92, 0.7))
for k, a in enumerate((-0.35, -0.75, -1.15)):
    c, s_ = math.cos(a), math.sin(a)
    hose([(1.0 - 0.1 * k, -0.68, 0.55), (0.95 + 0.2 * c, BY + 0.9 * s_ - 0.1, 0.75),
          (BX + 1.08 * c, BY + 1.08 * s_, 0.66)], r=0.022, mat="hose_k")
# north-east: the helium recovery receiver, the header's end
box((1.04, 1.02, 0.1), (0.9, 0.94, 0.2), "dark_steel", bevel=0.012)
top = vtank(1.06, 1.02, 0.34, 1.3, mat="cream", bands=(0.5, 0.95), nozzle=(-0.3, -0.4))
label(4, "helium recovery receiver (the spent gas)", (1.06, 0.66, 1.0))
# north-west: the switch cabinet, its cables to the HPU and the valves
cabinet(-1.04, 1.08, 0.9, 0.78, 1.0, mat="grey")
id_panel((-1.04, 0.685, 0.6), 0.32, 0.16, stripe="red")
box((-1.2, 1.25, 1.06), (0.36, 0.3, 0.12), "dark_steel", bevel=0.01)
jbox(-0.82, 1.28, w=0.24, d=0.18, h=0.2, mat="grey", z=1.0)
bundle([(-0.75, 0.7, 0.95), (-0.55, 0.3, 1.25), (-0.4, -0.3, 1.3), (BX + 0.62 * math.cos(VA[0]),
                                                                   BY + 0.62 * math.sin(VA[0]) + 0.1, 1.22)],
       cols=("black", "yellow"), r=0.015)
trunk([(-1.3, 0.7, 0.4), (-1.3, -0.2, 0.3), (-1.0, -0.7, 0.35), (0.5, -1.45, 0.35), (0.84, -1.3, 0.5)], r=0.03)
# east and west: the clamps' accumulators, a tool chest
for sx in (-1, 1):
    box((sx * 1.23, -0.02, 0.16), (0.54, 1.26, 0.32), "dark_steel", bevel=0.012)
    cyl((sx * 1.3, -0.12, 0.6), 0.1, 0.56, "yellow" if sx > 0 else "oxide", verts=24)
    head(sx * 1.3, -0.12, 0.88, 0.1, 0.06, "dark_steel")
    cyl((sx * 1.3, 0.16, 0.45), 0.1, 0.26, "dark_steel", verts=24)
box((-0.42, 1.2, 0.18), (0.4, 0.58, 0.36), "ochre", bevel=0.015)
box((-0.42, 1.2, 0.37), (0.42, 0.6, 0.03), "dark_steel", bevel=0.005)
box((0.42, 1.2, 0.12), (0.36, 0.58, 0.24), "dark_steel", bevel=0.012)
for sx in (-1, 1):
    box((sx * 0.42, -1.22, 0.14), (0.4, 0.56, 0.28), "dark_steel", bevel=0.012)
cyl((-0.42, -1.25, 0.42), 0.1, 0.28, "bare", verts=24)
cyl((-0.42, -1.25, 0.58), 0.11, 0.04, "dark_steel", verts=24)
box((0.42, -1.25, 0.38), (0.26, 0.22, 0.2), "grey", bevel=0.01)
stain(0.6, -0.95, 0.2, 0.12)
stain(-0.62, 0.95, 0.2, 0.15)
run(dict(name="the siphon bell", footprint=[3, 3]), nf=NF)
