"""Vent Pump, round 5 (T05): THE GAS-LIFT TOWER (3 x 3), Liam's pick (T04), in texture variants.

Round 4's tower (../round-4/vpb4_08_gas_lift_tower.py), copied, its geometry unchanged but for one
nudge: the flow meter's register (its dial) is smaller (r 0.15 -> 0.12) and tilted a little west, so
it no longer covers the helium sight glass east of it. The surfacing comes from vpb5_kit.py:
--variant base | a (warmer paints) | b (heavier wear and rust) | c (cleaner, newer), and the two
clipping fixes (satin bare steel; the melt's crest #F89A50, just under R 255) in every variant.

Round 3's words:
Vent Pump, round 3, concept 8: THE GAS-LIFT TOWER (3 x 3). Artist B.

  $BLENDER -b --python vpb5_08_gas_lift_tower.py --variant a -- <out-dir> [--quick] [--only working|idle] [--colourmap] [--check]

Round 2's tower (options/round-2/vpb_08_gas_lift_tower.py), the plumbing made honest and the
helium shown at work. What helium does: it is blown into the melt at the foot of the tower,
and its bubbles carry the melt up the glass riser (a gas lift); at the top it breaks out in
the head tank and is pumped round again.

The chain: helium-3 in at the south nozzle, along the grey-violet lagged line through the
stop valve and the turning flow meter, past the tee where the recovered helium joins, into
the sparger ring round the tower's foot. It is let in in two charges a loop: the meter
races and the line gauge swings with each, and the bubbles in the glass riser climb faster
with them. At the head tank the helium breaks out of the melt; the recovery line takes it
down the tower's east side to the compressor (south-east), which pushes it west over the
inlet into the recovery receiver (south-west), and from the receiver back into the line at
the tee. The melt: up from the vent through the collar into the riser, up the glass, into
the head tank, down the lagged downcomer (north-west) to the north nozzle.
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpb5_kit import *  # noqa: F401,F403,E402
import vpb3_kit as K  # noqa: E402

build_materials5(((0.45, 0.3), (2.6, 0.5), (3.0, 0.4)))
NF = 24
TX, TY = 0.0, 0.18          # the tower's axis, over the vent
HW = 0.34                   # the shaft's half-width
Z0, Z1 = 0.36, 2.92         # the shaft
ZT = 3.25                   # the head tank's axis
SLOT = 0.13                 # half the slot down the south face


def charge(t):
    """Helium let in in two charges a loop."""
    return max(pulse(t, 0.06, 0.3, 0.06), pulse(t, 0.56, 0.8, 0.06))


RATE = lambda t: 0.2 + charge(t)          # noqa: E731

# ---------------------------------------------------------------- footings: each unit on its own, no deck
foundation(-0.5, -0.36, 0.5, 0.7, 0.3, "refractory")                       # the tower's footing over the vent
vent_collar(TX, TY, 0.42, h=0.36)

# ---------------------------------------------------------------- the tower shaft, a slot down its south face
for sx in (-1, 1):
    box((TX + sx * HW, TY, (Z0 + Z1) / 2), (0.04, 2 * HW, Z1 - Z0), "iron", bevel=0.006)
box((TX, TY + HW, (Z0 + Z1) / 2), (2 * HW, 0.04, Z1 - Z0), "iron", bevel=0.006)
for sx in (-1, 1):
    w = HW - SLOT
    box((TX + sx * (SLOT + w / 2), TY - HW, (Z0 + Z1) / 2), (w, 0.04, Z1 - Z0), "iron", bevel=0.006)
    box((TX + sx * (SLOT + 0.015), TY - HW - 0.02, (Z0 + Z1) / 2), (0.03, 0.04, Z1 - Z0), "nickel", bevel=0.004)
box((TX, TY, Z1 + 0.02), (2 * HW + 0.06, 2 * HW + 0.06, 0.05), "dark_steel")
box((TX, TY + HW - 0.06, (Z0 + Z1) / 2), (2 * HW - 0.08, 0.02, Z1 - Z0), "dark")
for sx in (-1, 1):
    for sy in (-1, 1):
        box((TX + sx * HW, TY + sy * HW, (Z0 + Z1) / 2), (0.07, 0.07, Z1 - Z0 + 0.04), "dark_steel", bevel=0.006)
zb = Z0 + 0.25
while zb < Z1 - 0.1:
    for sx in (-1, 1):
        box((TX + sx * (HW + 0.012), TY, zb), (0.025, 2 * HW + 0.05, 0.05), "dark_steel", bevel=0.004)
    box((TX, TY + HW + 0.012, zb), (2 * HW + 0.05, 0.025, 0.05), "dark_steel", bevel=0.004)
    for sx in (-1, 1):
        box((TX + sx * (SLOT + (HW - SLOT) / 2), TY - HW - 0.012, zb), (HW - SLOT, 0.025, 0.05), "dark_steel",
            bevel=0.004)
    for k in range(4):
        sphere((TX + HW + 0.027, TY - HW + 0.1 + k * 0.16, zb), 0.012, "bolt", seg=8)
    zb += 0.42
stencil((TX + HW + 0.025, TY - 0.05, 1.05), (0.012, 0.32, 0.12))
hazard_tag((TX - 0.22, TY - HW - 0.03, 0.55), 0.12, 0.08)

# ---------------------------------------------------------------- the glass riser in the slot: bubbles climbing with each charge
GX, GY = TX, TY - HW + 0.05
GZ0, GZ1 = Z0 + 0.12, Z1 - 0.08
melt("mt_riser", "flow", scale=1.6, k=2, soft=True, bright=1.0, axis="Z",
     fn=lambda t: 0.82 + 0.18 * charge(t))
cyl((GX, GY, (GZ0 + GZ1) / 2), 0.085, GZ1 - GZ0, "mt_riser", verts=32, bevel=0)
cyl((GX, GY, (GZ0 + GZ1) / 2), 0.115, GZ1 - GZ0, "glass", verts=32, bevel=0)
bubbles(GX, GY, GZ0, GZ1, 0.1, n=8, cols=3, r=0.048, per_loop=2, angles=(-PI / 2 - 0.7, -PI / 2, -PI / 2 + 0.7),
        ease=progress(RATE))
z = GZ0
while z <= GZ1 + 0.01:
    cyl((GX, GY, z), 0.125, 0.05, "nickel", verts=32)
    z += (GZ1 - GZ0) / 3
for sx in (-1, 1):
    cyl((GX + sx * 0.13, GY - 0.03, (GZ0 + GZ1) / 2), 0.012, GZ1 - GZ0, "bare", verts=8, bevel=0)
cyl((GX, GY, GZ0 - 0.05), 0.15, 0.1, "dark_steel", verts=32)
cyl((GX, GY, GZ1 + 0.05), 0.15, 0.1, "dark_steel", verts=32)
label(4, "glass riser: the helium's bubbles carry the melt up, faster in each charge", (GX, GY - 0.1, 1.5))

# ---------------------------------------------------------------- the head tank on the tower top
box((TX, TY, Z1 + 0.08), (1.02, 0.8, 0.06), "dark_steel")
for sx in (-1, 1):
    for y in (TY - 0.38, TY + 0.38):
        box((TX + sx * 0.49, y, Z1 + 0.28), (0.025, 0.025, 0.36), "yellow", bevel=0.003)
    box((TX + sx * 0.49, TY, Z1 + 0.45), (0.025, 0.78, 0.025), "yellow", bevel=0.003)
for xs in (-0.3, 0.3):
    box((TX + xs, TY, Z1 + 0.18), (0.1, 0.5, 0.16), "dark_steel")
cyl((TX, TY, ZT), 0.3, 0.86, "iron_dk", rot=(0, PI / 2, 0), verts=48)
for xx, s in ((TX - 0.43, -1), (TX + 0.43, 1)):
    h_ = head(xx, TY, ZT, 0.3, 0.1, "iron_dk")
    h_.rotation_euler = (0, s * PI / 2, 0)
for xx in (TX - 0.25, TX, TX + 0.25):
    cyl((xx, TY, ZT), 0.318, 0.05, "nickel", rot=(0, PI / 2, 0), verts=48)
cyl((GX, GY, Z1 + 0.06), 0.1, 0.18, "heat", verts=24)                      # the riser's head into the tank
melt("mt_tank", "flow", scale=7.0, k=1, bright=0.85, axis="X")
box((TX - 0.12, TY - 0.285, ZT - 0.04), (0.3, 0.03, 0.07), "mt_tank", bevel=0.003)
box((TX - 0.12, TY - 0.3, ZT - 0.04), (0.36, 0.02, 0.12), "dark_steel", bevel=0.004)
box((TX - 0.12, TY - 0.305, ZT - 0.04), (0.3, 0.012, 0.07), "pane", bevel=0)
manway_top(TX - 0.12, TY + 0.05, ZT + 0.29, r=0.09)
label(5, "head tank: the helium breaks out of the melt", (TX - 0.2, TY, ZT + 0.2))

# the float chamber on the east end, its lever rocking with the level (one rock a charge)
cyl((TX + 0.62, TY, ZT - 0.05), 0.11, 0.42, "iron", verts=32)
cyl((TX + 0.62, TY, ZT + 0.17), 0.13, 0.04, "dark_steel", verts=32)
pipe([(TX + 0.45, TY, ZT - 0.12), (TX + 0.56, TY, ZT - 0.12)], r=0.035, mat="bare", name="float chamber leg")
fp = pivot((TX + 0.62, TY - 0.13, ZT + 0.05), (0, 0, 0))
box((0.0, -0.02, 0.0), (0.03, 0.05, 0.05), "dark_steel", parent=fp)
box((0.18, -0.03, 0.0), (0.36, 0.022, 0.022), "bare", parent=fp)
sphere((0.36, -0.03, 0.0), 0.05, "red", parent=fp)
box((-0.09, -0.03, 0.0), (0.12, 0.022, 0.022), "bare", parent=fp)
rock(fp, 0.32, cycles=2, axis="Y", phase=-0.1)
label(6, "float chamber: its lever rocks as each charge lifts the level", (TX + 0.8, TY - 0.15, ZT + 0.05))

# ---------------------------------------------------------------- the downcomer: the melt down to the north nozzle
out_in = nozzle("N", length=0.36, mat="heat")
DOWN = [(TX - 0.45, TY, ZT - 0.05), (TX - 0.6, TY + 0.12, ZT - 0.3), (-0.62, 0.62, 2.0), (-0.6, 0.72, 0.9),
        (-0.45, 0.95, 0.55), (-0.15, 1.1, ZA), out_in]
lagged(DOWN, r=0.12, bands=0.25, name="downcomer (melt)")
for z in (0.9, 1.6, 2.2):
    box((-0.47, TY + 0.38, z), (0.14, 0.1, 0.04), "dark_steel")
label(10, "downcomer, lagged: the melt drops to the outlet", (-0.62, 0.65, 1.4))
label(11, "molten kamacite out, north", (0, 1.38, ZA))

# ---------------------------------------------------------------- the helium in: the grey-violet line to the sparger
in_in = nozzle("S", length=0.3, mat="bare")
foundation(-0.42, -1.18, 0.42, -0.4, 0.1, anchors=False)
valve(0, -1.06, z=ZA - 0.1, h=0.36, r=0.06)
he_line([in_in, (0, -1.06, ZA), (0, -0.9, ZA)], name="helium in: nozzle to the flow meter")
flow_meter((0, -0.78, ZA), (0, 1, 0), r=0.12, turns=2, rate=RATE, facing=(-0.3, -0.55, 1))   # round 5: nudged off the glass
TEE = (0, -0.56, ZA)
cyl(TEE, 0.1, 0.16, "bare", rot=(PI / 2, 0, 0), verts=20)                   # the tee where the recovered gas joins
cyl((0, -0.56, ZA + 0.14), 0.035, 0.2, "bare", verts=12)
he_gauge((0, -0.58, ZA + 0.27), (0, -1, 0.7), live=lambda t: -0.4 + 1.2 * charge(t))
he_line([(0, -0.66, ZA), (0, -0.62, ZA)], name="helium: meter to tee")
# the sight tank between the tee and the sparger, east of the line: in at its foot, out of its head, down to the ring
G0_, G1_ = (0.31, -0.84, 0.3), (0.31, -0.84, 0.98)
ga, gb = axis_pts(G0_, G1_, 0.1)
sight_tank(G0_, G1_, stroke_pulse((0.06, 0.56), rise=0.05, fall=0.36), r=0.14)
he_line([(0, -0.48, ZA), (0.12, -0.5, 0.3), (0.22, -0.66, 0.2), ga, G0_], name="helium: tee to the sight glass")
he_line([G1_, gb, (0.22, -0.6, 1.0), (0.1, -0.38, 0.78), (0.04, -0.3, 0.5), (TX, TY - 0.44, 0.44)],
        name="helium: sight glass to the sparger ring")
label(12, "helium sight glass: the level drops and flushes pink at each charge", (0.27, -0.84, 0.65))
torus((TX, TY, 0.44), 0.44, 0.04, "he_lag", seg=48)                        # the sparger ring
for i in range(8):
    a = 2 * PI * (i + 0.5) / 8
    torus((TX + 0.44 * math.cos(a), TY + 0.44 * math.sin(a), 0.44), 0.045, 0.01, "he_band", rot=(0, 0, 0), seg=16)
    cyl((TX + 0.4 * math.cos(a), TY + 0.4 * math.sin(a), 0.41), 0.02, 0.08, "bare", rot=(0, PI / 2, a), verts=8,
        bevel=0)
box((-0.24, -0.78, 0.3), (0.22, 0.4, 0.4), "green", bevel=0.02)            # the meter's transmitter
box((0.27, -0.47, 0.28), (0.24, 0.26, 0.36), "grey", bevel=0.02)            # the injection controller (round 4: north of the glass)
bundle([(-0.18, -0.7, 0.5), (-0.1, -0.74, 0.52), (-0.03, -0.78, ZA + 0.1)], cols=("black", "grey"), r=0.012,
       name="meter cable")
label(1, "helium-3 in, south: the grey-violet line", (0, -1.38, ZA))
label(2, "stop valve and flow meter: the meter races in each charge", (0, -0.85, 0.6))
label(3, "sparger ring round the tower's foot: helium blown into the melt", (TX - 0.4, TY - 0.3, 0.45))

# ---------------------------------------------------------------- recovery: tank -> compressor -> receiver -> tee
REC = [(TX + 0.2, TY + 0.0, ZT + 0.29), (TX + 0.3, TY - 0.08, ZT + 0.44), (TX + 0.44, TY - 0.42, ZT + 0.1),
       (0.44, -0.2, 2.0), (0.44, -0.24, 0.9), (0.62, -0.62, 0.7), (0.66, -0.82, 0.62)]
cyl((TX + 0.2, TY, ZT + 0.27), 0.06, 0.08, "bare", verts=16)               # the tank's gas offtake
he_line(REC, r=0.055, name="recovery: head tank down to the compressor")
for z in (1.0, 1.7, 2.3):
    box((TX + HW + 0.06, TY - 0.3, z), (0.08, 0.08, 0.035), "dark_steel")
label(7, "recovery line: the broken-out helium back down", (0.46, -0.24, 1.7))
# the compressor skid (SE): two cylinders on a crankcase, a motor and an exposed coupling
foundation(0.44, -1.47, 1.47, -0.42, 0.14)
box((0.85, -0.95, 0.4), (0.62, 0.95, 0.52), "oxide", bevel=0.03)
for yy in (-0.82, -1.08):
    cyl((0.85, yy, 0.78), 0.11, 0.3, "oxide", verts=24)
    cyl((0.85, yy, 0.95), 0.13, 0.05, "dark_steel", verts=24)
    bolts(0.85, yy, 0.98, 0.1, 6, r=0.012)
pv = motor(1.25, -0.95, 0.5, d=(-1, 0), s=0.85, mat="green")
coupling(pv[0] - 0.03, pv[1], pv[2], 0.075, axis=(1, 0, 0), turns=3)
pipe([(0.85, -1.08, 0.98), (0.85, -0.95, 1.04), (0.85, -0.82, 0.98)], r=0.03, mat="bare",
     name="compressor head crossover")
label(8, "recovery compressor (its coupling turning)", (0.85, -0.95, 1.0))
hazard_tag((0.85, -1.425, 0.3), 0.3, 0.06)
# its discharge west, over the inlet, to the recovery receiver (SW)
he_line([(0.85, -0.95, 1.06), (0.7, -0.9, 1.12), (0.3, -0.42, 1.0), (-0.3, -0.42, 1.0), (-0.75, -0.62, 1.2),
         (-0.92, -0.9, 1.32)], r=0.05, name="recovery: compressor to the receiver")
foundation(-1.4, -1.4, -0.48, -0.48, 0.12)
vtank(-0.94, -0.94, 0.4, 1.2, mat="grey", bands=(0.4, 0.85), band_mat="he_edge", nozzle=None)
cyl((-0.94, -0.94, 1.32), 0.07, 0.12, "bare", verts=16)
he_gauge((-0.94, -1.35, 0.62), (0, -1, 0.2), live=lambda t: 0.5 * math.sin(2 * PI * 3 * t))
id_panel((-0.94, -1.345, 0.9), 0.26, 0.12, stripe="yellow")
he_line([(-0.6, -0.86, 0.3), (-0.35, -0.6, 0.32), (-0.1, -0.56, ZA)], r=0.05,
        name="recovery: receiver back into the line at the tee")
label(9, "recovery receiver: the helium back into the line at the tee", (-0.94, -0.94, 1.3))

ROUTE_IN = [(0, -1.5, ZA), (0, -1.06, ZA), (0, -0.78, ZA), (0, -0.56, ZA), (0.12, -0.5, 0.3), (0.22, -0.66, 0.2), G0_,
            G1_, (0.22, -0.6, 1.0), (0.1, -0.38, 0.78), (0.04, -0.3, 0.5), (TX, TY - 0.44, 0.44),
            (TX + 0.31, TY - 0.31, 0.44), (TX + 0.44, TY, 0.44)]
route("he", ROUTE_IN)
route("he", [(TX, TY - 0.44, 0.44), (TX - 0.31, TY - 0.31, 0.44), (TX - 0.44, TY, 0.44)])
route("melt", [(TX, TY, 0.3), (GX, GY, GZ0), (GX, GY, GZ1), (GX, GY, ZT - 0.1), (TX - 0.43, TY, ZT - 0.05)] + DOWN[1:-1]
      + [(0, 1.5, ZA)])
route("spent", REC + [(0.85, -0.95, 1.06), (0.7, -0.9, 1.12), (0.3, -0.42, 1.0), (-0.3, -0.42, 1.0),
                      (-0.75, -0.62, 1.2), (-0.94, -0.94, 1.3), (-0.94, -0.94, 0.4), (-0.6, -0.86, 0.3),
                      (-0.35, -0.6, 0.32), (-0.1, -0.56, ZA)])

# ---------------------------------------------------------------- the control house (NE) and the switchgear (E)
foundation(0.48, 0.55, 1.42, 1.42, 0.12)
box((0.93, 0.965, 0.12 + 0.42), (0.86, 0.78, 0.84), "cream", bevel=0.03)
box((0.93, 0.965, 0.98), (0.92, 0.84, 0.05), "dark_steel")
for k in range(3):
    box((0.72 + 0.2 * k, 0.565, 0.7), (0.12, 0.02, 0.3), "dark_steel", bevel=0.003)
status_lens(1.26, 0.66, 1.02)
box((0.82, 1.06, 1.12), (0.46, 0.46, 0.22), "grey", bevel=0.02)
cyl((0.82, 1.06, 1.235), 0.17, 0.02, "dark_steel", verts=32)
cyl((1.24, 1.24, 1.25), 0.025, 0.55, "bare", verts=8)
box((1.24, 1.24, 1.5), (0.14, 0.03, 0.03), "red", bevel=0)

foundation(0.5, -0.4, 1.5, 0.53, 0.1)
box((1.02, 0.07, 0.4), (0.9, 0.86, 0.6), "grey", bevel=0.025)
for k in range(3):
    cyl((0.78 + 0.22 * k, 0.32, 0.74), 0.045, 0.1, "ochre", verts=12)
    cyl((0.78 + 0.22 * k, 0.32, 0.81), 0.03, 0.06, "dark_steel", verts=12)
for k in range(4):
    box((0.8 + 0.15 * k, -0.37, 0.4), (0.1, 0.02, 0.4), "dark_steel", bevel=0.003)
status_lens(1.3, 0.3, 0.72)
bundle([(1.0, 0.32, 0.84), (0.7, 0.3, 1.2), (TX + HW + 0.02, TY + 0.05, 1.5)], cols=("black", "red", "grey"),
       r=0.018, name="switchgear to the tower's instruments")
bundle([(1.2, -0.36, 0.6), (1.28, -0.6, 0.75), (1.25, -0.95, 0.72)], cols=("black", "yellow"), r=0.014,
       name="switchgear to the compressor motor")
bundle([(0.93, 0.6, 0.9), (0.95, 0.5, 0.75), (0.95, 0.45, 0.7)], cols=("black", "grey"), r=0.012,
       name="control house to the switchgear")

# ---------------------------------------------------------------- the ladder (W), the tool chest, the skimmings bin
ladder(TX - HW - 0.1, TY - 0.1, 0.22, Z1 + 0.1, axis="y", mat="ochre")
for z in (1.0, 1.6, 2.2):
    torus((TX - HW - 0.18, TY - 0.1, z), 0.14, 0.012, "ochre", rot=(0, 0, 0), seg=24)
foundation(-1.5, -0.42, -0.52, 0.5, 0.1)
for k, yy in enumerate((-0.2, 0.25)):
    vtank(-1.05, yy, 0.22, 0.95 - 0.12 * k, mat=("green", "ochre")[k], bands=(0.45,), nozzle=None)
box((-0.7, 0.02, 0.3), (0.26, 0.7, 0.4), "dark_steel", bevel=0.02)
foundation(-1.46, 0.52, -0.42, 1.46, 0.1)
box((-0.92, 0.95, 0.42), (0.86, 0.8, 0.64), "oxide", bevel=0.025)
for sx, sy, w, d in ((0, -0.38, 0.9, 0.06), (0, 0.38, 0.9, 0.06), (-0.42, 0, 0.06, 0.82), (0.42, 0, 0.06, 0.82)):
    box((-0.92 + sx, 0.95 + sy, 0.76), (w, d, 0.06), "dark_steel", bevel=0.006)
box((-0.92, 0.95, 0.7), (0.78, 0.72, 0.04), "slag", bevel=0)
box((-0.92, 1.35, 0.98), (0.86, 0.04, 0.4), "dark_steel", bevel=0.01)
box((-0.56, 1.3, 0.98), (0.03, 0.03, 0.42), "bare", bevel=0)
hazard_tag((-0.92, 0.55, 0.4), 0.6, 0.07)
stain(0.4, -0.3, 0.25, 0.1)
stain(-0.3, 1.2, 0.2, 0.08)
run5(dict(name="the gas-lift tower", footprint=[3, 3]), nf=NF)
