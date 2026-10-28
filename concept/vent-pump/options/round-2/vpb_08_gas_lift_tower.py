"""Vent Pump, round 2, concept 8: THE GAS-LIFT TOWER (3 x 3). Artist B.

  $BLENDER -b --python vpb_08_gas_lift_tower.py -- <out-dir> [--quick] [--only working|idle] [--colourmap]

The chain, vent to outlet: helium-3 comes in bare through the south nozzle, past a stop valve
and a flow meter, and with the recovered helium from the compressor is blown into the
sparger ring at the foot of the tower, over the vent collar. The bubbles lift the melt up a
glass riser in the slot down the tower's south face; at the top a horizontal head tank
lets the helium break out of the melt (its float chamber on the east end rocks with the
level); the helium goes back down the recovery line to the compressor on the south-east
skid, and the melt drops down the lagged downcomer on the north-west to the north nozzle.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpb_kit import *  # noqa: F401,F403,E402
import vpb_kit as K  # noqa: E402

K.build_materials(((0.45, 0.3), (2.6, 0.5), (3.0, 0.4)))
NF = 24
TX, TY = 0.0, 0.18          # the tower's axis, over the vent
HW = 0.34                   # the shaft's half-width
Z0, Z1 = 0.36, 2.92         # the shaft
ZT = 3.25                   # the head tank's axis
SLOT = 0.13                 # half the slot down the south face


def strut(p, q, r, mat):
    p, q = Vector(p), Vector(q)
    cyl(tuple((p + q) / 2), r, (q - p).length, mat, rot=along(q - p), verts=10, bevel=0)


# ---------------------------------------------------------------- footings: each unit on its own, no deck
foundation(-0.5, -0.36, 0.5, 0.7, 0.3, "refractory")                       # the tower's footing over the vent
# ---------------------------------------------------------------- the vent collar and the sparger
vent_collar(TX, TY, 0.42, h=0.36)
label(3, "sparger ring over the vent collar: helium blown into the melt", (TX, TY - 0.45, 0.4))

# ---------------------------------------------------------------- the tower shaft, a slot down its south face
for sx in (-1, 1):                                        # east and west walls
    box((TX + sx * HW, TY, (Z0 + Z1) / 2), (0.04, 2 * HW, Z1 - Z0), "iron", bevel=0.006)
box((TX, TY + HW, (Z0 + Z1) / 2), (2 * HW, 0.04, Z1 - Z0), "iron", bevel=0.006)      # north wall
for sx in (-1, 1):                                        # the south wall either side of the slot
    w = HW - SLOT
    box((TX + sx * (SLOT + w / 2), TY - HW, (Z0 + Z1) / 2), (w, 0.04, Z1 - Z0), "iron", bevel=0.006)
    box((TX + sx * (SLOT + 0.015), TY - HW - 0.02, (Z0 + Z1) / 2), (0.03, 0.04, Z1 - Z0), "nickel", bevel=0.004)
box((TX, TY, Z1 + 0.02), (2 * HW + 0.06, 2 * HW + 0.06, 0.05), "dark_steel")
box((TX, TY + HW - 0.06, (Z0 + Z1) / 2), (2 * HW - 0.08, 0.02, Z1 - Z0), "dark")        # inside the slot: dark
for sx in (-1, 1):                                        # corner angles
    for sy in (-1, 1):
        box((TX + sx * HW, TY + sy * HW, (Z0 + Z1) / 2), (0.07, 0.07, Z1 - Z0 + 0.04), "dark_steel", bevel=0.006)
zb = Z0 + 0.25
while zb < Z1 - 0.1:                                       # riveted stiffening bands
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

# ---------------------------------------------------------------- the glass riser in the slot, bubbles climbing it
GX, GY = TX, TY - HW + 0.05
GZ0, GZ1 = Z0 + 0.12, Z1 - 0.08
melt("mt_riser", "flow", scale=1.6, k=2, soft=True, bright=1.0, axis="Z",
     fn=lambda t: 0.9 + 0.1 * math.cos(2 * PI * 3 * t))
cyl((GX, GY, (GZ0 + GZ1) / 2), 0.085, GZ1 - GZ0, "mt_riser", verts=32, bevel=0)
cyl((GX, GY, (GZ0 + GZ1) / 2), 0.115, GZ1 - GZ0, "glass", verts=32, bevel=0)
bubbles(GX, GY, GZ0, GZ1, 0.1, n=8, cols=3, r=0.045, per_loop=2, angles=(-PI / 2 - 0.7, -PI / 2, -PI / 2 + 0.7))
z = GZ0
while z <= GZ1 + 0.01:                                    # the glass's clamp bands and tie rods
    cyl((GX, GY, z), 0.125, 0.05, "nickel", verts=32)
    z += (GZ1 - GZ0) / 3
for sx in (-1, 1):
    cyl((GX + sx * 0.13, GY - 0.03, (GZ0 + GZ1) / 2), 0.012, GZ1 - GZ0, "bare", verts=8, bevel=0)
cyl((GX, GY, GZ0 - 0.05), 0.15, 0.1, "dark_steel", verts=32)
cyl((GX, GY, GZ1 + 0.05), 0.15, 0.1, "dark_steel", verts=32)
label(4, "glass riser: the melt climbs with the helium bubbles", (GX, GY - 0.1, 1.5))

# ---------------------------------------------------------------- the head tank on the tower top
box((TX, TY, Z1 + 0.08), (1.02, 0.8, 0.06), "dark_steel")                  # the top platform
for sx in (-1, 1):                                                          # its railing
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
melt("mt_tank", "flow", scale=7.0, k=1, bright=0.85, axis="X")
box((TX - 0.12, TY - 0.285, ZT - 0.04), (0.3, 0.03, 0.07), "mt_tank", bevel=0.003)    # the level slot
box((TX - 0.12, TY - 0.3, ZT - 0.04), (0.36, 0.02, 0.12), "dark_steel", bevel=0.004)
box((TX - 0.12, TY - 0.305, ZT - 0.04), (0.3, 0.012, 0.07), "pane", bevel=0)
manway_top(TX + 0.12, TY, ZT + 0.29, r=0.1)
label(5, "head tank: the helium breaks out of the melt", (TX - 0.2, TY, ZT + 0.2))

# the float chamber on the east end, its lever rocking with the level
cyl((TX + 0.62, TY, ZT - 0.05), 0.11, 0.42, "iron", verts=32)
cyl((TX + 0.62, TY, ZT + 0.17), 0.13, 0.04, "dark_steel", verts=32)
pipe([(TX + 0.48, TY, ZT - 0.12), (TX + 0.55, TY, ZT - 0.12)], r=0.035, mat="bare")
fp = pivot((TX + 0.62, TY - 0.13, ZT + 0.05), (0, 0, 0))
box((0.0, -0.02, 0.0), (0.03, 0.05, 0.05), "dark_steel", parent=fp)
box((0.18, -0.03, 0.0), (0.36, 0.022, 0.022), "bare", parent=fp)
sphere((0.36, -0.03, 0.0), 0.05, "red", parent=fp)
box((-0.09, -0.03, 0.0), (0.12, 0.022, 0.022), "bare", parent=fp)
rock(fp, 0.32, cycles=2, axis="Y")
label(6, "float chamber: its lever rocks with the melt level", (TX + 0.8, TY - 0.15, ZT + 0.05))

# ---------------------------------------------------------------- the downcomer: the melt down to the north nozzle
out_in = nozzle("N", length=0.36, mat="heat")
lagged([(TX - 0.45, TY, ZT - 0.05), (TX - 0.6, TY + 0.12, ZT - 0.3), (-0.62, 0.62, 2.0), (-0.6, 0.72, 0.9),
        (-0.45, 0.95, 0.55), (-0.15, 1.1, ZA), out_in], r=0.12, bands=0.25)
for z in (0.9, 1.6, 2.2):
    box((-0.47, TY + 0.38, z), (0.14, 0.1, 0.04), "dark_steel")
label(9, "downcomer, lagged: the melt drops to the outlet", (-0.62, 0.65, 1.4))
label(10, "molten kamacite out, north", (0, 1.38, ZA))

# ---------------------------------------------------------------- the helium side: bare metal, no frost
in_in = nozzle("S", length=0.3, mat="bare")
pipe([in_in, (0, -1.0, ZA), (0, -0.82, ZA)], r=0.07, mat="bare", flanges=False)
valve(0, -1.0, z=ZA - 0.1, h=0.36, r=0.06)
foundation(-0.42, -1.18, 0.42, -0.4, 0.1, anchors=False)
box((-0.24, -0.75, 0.3), (0.3, 0.6, 0.4), "green", bevel=0.02)            # the meter's transmitter
box((0.26, -0.72, 0.28), (0.28, 0.5, 0.36), "grey", bevel=0.02)             # the injection controller
cyl((0, -0.72, ZA), 0.12, 0.22, "brass", rot=(PI / 2, 0, 0), verts=24)        # the flow meter
gauge((0.11, -0.72, ZA + 0.05), (1, 0, 0.3), r=0.05, live=lambda t: 0.25 * math.sin(2 * PI * 3 * t))
pipe([(0, -0.62, ZA), (0, -0.48, ZA), (TX, TY - 0.44, 0.42)], r=0.06, mat="bare")
torus((TX, TY, 0.43), 0.44, 0.035, "bare", seg=48)                        # the sparger ring
for i in range(8):
    a = 2 * PI * (i + 0.5) / 8
    cyl((TX + 0.44 * math.cos(a), TY + 0.44 * math.sin(a), 0.4), 0.02, 0.08, "dark_steel", verts=8, bevel=0)
label(1, "helium-3 in, south: bare metal", (0, -1.38, ZA))
label(2, "stop valve and flow meter", (0, -0.9, 0.7))

# the helium receiver (SW)
foundation(-1.5, -1.5, -0.42, -0.42, 0.12)
vtank(-0.96, -0.96, 0.42, 1.25, mat="grey", bands=(0.4, 0.9), nozzle=(0.0, 0.0))
pipe([(-0.55, -0.9, 0.3), (-0.3, -0.9, 0.3), (-0.06, -0.85, ZA)], r=0.045, mat="bare")
gauge((-0.96, -1.39, 0.6), (0, -1, 0), r=0.06, live=lambda t: 0.15 * math.sin(2 * PI * t))
id_panel((-0.96, -1.385, 0.9), 0.26, 0.12, stripe="yellow")

# ---------------------------------------------------------------- recovery: helium back down to the compressor
pipe([(TX + 0.2, TY, ZT + 0.3), (TX + 0.32, TY - 0.1, ZT + 0.42), (TX + 0.42, TY - 0.42, ZT + 0.1),
      (0.44, -0.2, 2.0), (0.44, -0.24, 0.9), (0.62, -0.5, 0.55), (0.75, -0.62, 0.5)], r=0.045, mat="bare",
     marks=((0.5, "yellow"),))
for z in (1.0, 1.7, 2.3):
    box((TX + HW + 0.06, TY - 0.3, z), (0.08, 0.08, 0.035), "dark_steel")
label(7, "helium recovery line, back down", (0.46, -0.24, 1.7))
# the compressor skid (SE): two cylinders on a crankcase, a motor and an exposed coupling
foundation(0.44, -1.5, 1.5, -0.4, 0.14)
box((0.85, -0.95, 0.4), (0.62, 0.95, 0.52), "oxide", bevel=0.03)
for yy in (-0.82, -1.08):
    cyl((0.85, yy, 0.78), 0.11, 0.3, "oxide", verts=24)
    cyl((0.85, yy, 0.95), 0.13, 0.05, "dark_steel", verts=24)
    bolts(0.85, yy, 0.98, 0.1, 6, r=0.012)
pv = motor(1.3, -0.95, 0.5, d=(-1, 0), s=0.85, mat="green")
coupling(pv[0] - 0.03, pv[1], pv[2], 0.075, axis=(1, 0, 0), turns=3)
pipe([(0.85, -0.82, 0.98), (0.75, -0.68, 1.02), (0.3, -0.62, 0.6), (0.06, -0.62, ZA)], r=0.04, mat="bare")
label(8, "recovery compressor: back into the sparger", (0.85, -0.95, 1.0))
hazard_tag((0.85, -1.205, 0.3), 0.3, 0.06)

# ---------------------------------------------------------------- the control house (NE) and the switchgear (E)
foundation(0.48, 0.55, 1.5, 1.5, 0.12)
box((1.0, 1.03, 0.12 + 0.42), (0.98, 0.9, 0.84), "cream", bevel=0.03)
box((1.0, 1.03, 0.98), (1.04, 0.96, 0.05), "dark_steel")
for k in range(3):
    box((0.78 + 0.2 * k, 0.575, 0.7), (0.12, 0.02, 0.3), "dark_steel", bevel=0.003)
status_lens(1.36, 0.66, 1.02)
box((0.86, 1.12, 1.12), (0.5, 0.5, 0.22), "grey", bevel=0.02)                 # the rooftop condenser
cyl((0.86, 1.12, 1.235), 0.19, 0.02, "dark_steel", verts=32)
for k in range(4):
    box((0.86, 1.12, 1.25), (0.36, 0.035, 0.01), "dark_steel", rz=k * PI / 4, bevel=0)
cyl((1.3, 1.3, 1.25), 0.025, 0.55, "bare", verts=8)                         # the mast
box((1.3, 1.3, 1.5), (0.14, 0.03, 0.03), "red", bevel=0)
box((1.28, 0.85, 1.06), (0.3, 0.2, 0.12), "dark_steel", bevel=0.01)

foundation(0.5, -0.42, 1.5, 0.56, 0.1)
box((1.02, 0.07, 0.4), (0.9, 0.9, 0.6), "grey", bevel=0.025)                 # the switchgear
for k in range(3):
    cyl((0.78 + 0.22 * k, 0.32, 0.74), 0.045, 0.1, "ochre", verts=12)
    cyl((0.78 + 0.22 * k, 0.32, 0.81), 0.03, 0.06, "dark_steel", verts=12)
for k in range(4):
    box((0.8 + 0.15 * k, -0.39, 0.4), (0.1, 0.02, 0.4), "dark_steel", bevel=0.003)
radiator(0.6, 1.45, 0.53, 0.12, 0.42, mat="grey", tube="copper", fins=10)
status_lens(1.3, 0.3, 0.72)
jbox(0.75, -0.2, w=0.22, d=0.16, h=0.26, mat="grey", z=0.7)
bundle([(1.0, 0.32, 0.84), (0.7, 0.3, 1.2), (TX + HW + 0.04, TY + 0.05, 1.5)], cols=("black", "red", "grey"), r=0.018)
bundle([(1.2, -0.38, 0.7), (1.25, -0.6, 0.75), (1.3, -0.85, 0.72)], cols=("black", "yellow"), r=0.014)

# ---------------------------------------------------------------- the ladder (W) to the platform, the seal pot, clutter
ladder(TX - HW - 0.1, TY - 0.1, 0.22, Z1 + 0.1, axis="y", mat="ochre")
for z in (1.0, 1.6, 2.2):
    torus((TX - HW - 0.18, TY - 0.1, z), 0.14, 0.012, "ochre", rot=(0, 0, 0), seg=24)
foundation(-1.5, -0.44, -0.5, 0.5, 0.1)
for k, yy in enumerate((-0.2, 0.25)):
    vtank(-1.05, yy, 0.22, 0.95 - 0.12 * k, mat=("green", "ochre")[k], bands=(0.45,), nozzle=(0.0, 0.0))
box((-0.68, 0.02, 0.3), (0.3, 0.8, 0.4), "dark_steel", bevel=0.02)
pipe([(-0.85, -0.2, 0.7), (-0.6, -0.1, 0.62), (-0.52, 0.1, 0.55)], r=0.03, mat="bare")
foundation(-1.5, 0.48, -0.42, 1.5, 0.1)
box((-1.0, 1.02, 0.42), (0.9, 0.9, 0.64), "oxide", bevel=0.025)                 # the skimmings bin
for sx, sy, w, d in ((0, -0.43, 0.94, 0.06), (0, 0.43, 0.94, 0.06), (-0.43, 0, 0.06, 0.94), (0.43, 0, 0.06, 0.94)):
    box((-1.0 + sx, 1.02 + sy, 0.76), (w, d, 0.06), "dark_steel", bevel=0.006)
box((-1.0, 1.02, 0.7), (0.82, 0.82, 0.04), "slag", bevel=0)
box((-1.0, 1.47, 0.98), (0.9, 0.04, 0.4), "dark_steel", bevel=0.01)             # the lid, propped open
box((-0.6, 1.4, 0.98), (0.03, 0.03, 0.42), "bare", bevel=0)
hazard_tag((-1.0, 0.57, 0.4), 0.6, 0.07)
hose([(-1.05, 0.25, 0.85), (-0.85, 0.45, 1.0), (-0.55, 0.55, 1.1)], r=0.035, mat="hose")
stain(0.4, -0.3, 0.25, 0.1)
stain(-0.3, 1.2, 0.2, 0.08)
run(dict(name="the gas-lift tower", footprint=[3, 3]), nf=NF)
