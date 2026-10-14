"""Vent Pump, round 2, concept 9: THE ROTARY VANE PUMP (3 x 3). Artist B.

  $BLENDER -b --python vpb_09_rotary_vane_pump.py -- <out-dir> [--quick] [--only working|idle] [--colourmap]

The chain, vent to outlet: the melt is drawn up the refractory suction bell over the vent
collar into a big cast vane pump, its axis north-south; the drive is open on the south side
-- the motor on its stool over the helium line, the brake drum and coupling turning in the open
between two bearing pedestals, so the turn faces the camera. The pump throws the melt up its
discharge neck, past the armoured sight port, over the gooseneck and down to the north
nozzle. Helium-3 comes in bare through the south nozzle, under the motor stool, to the
seal-gas manifold: it blankets the shaft seals and the vane chamber (a melt pump's seals are
kept under inert gas), and that is where it is used up.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpb_kit import *  # noqa: F401,F403,E402
import vpb_kit as K  # noqa: E402

K.build_materials(((0.5, 0.3), (1.5, 0.4)))
NF = 24
PX, PY, PZ = 0.0, 0.22, 0.92        # the pump's axis (north-south) over the vent
PR, PL = 0.6, 0.86                  # the casing's radius and length
YS = PY - PL / 2                    # its south cover
YN = PY + PL / 2
NS = (PI / 2, 0, 0)                 # a cylinder's axis turned to north-south

# ---------------------------------------------------------------- the vent collar and the suction bell
vent_collar(PX, PY, 0.5, h=0.2)
cone((PX, PY, 0.3), 0.46, 0.3, 0.2, "refractory")
label(1, "suction bell over the vent collar", (PX + 0.45, PY - 0.35, 0.25))

# ---------------------------------------------------------------- the cast pump body
for sx in (-1, 1):                                                               # cast feet, west and east
    foundation(PX + sx * 0.68 - 0.13, PY - 0.5, PX + sx * 0.68 + 0.13, PY + 0.5, 0.34, "iron_dk")
    for yy in (PY - 0.3, PY + 0.3):
        box((PX + sx * 0.5, yy, 0.55), (0.2, 0.06, 0.5), "iron_dk", bevel=0.008)
cyl((PX, PY, PZ), PR, PL, "iron", rot=NS, verts=64)
for k in range(5):                                                               # cast ribs
    y = YS + 0.1 + k * (PL - 0.2) / 4
    cyl((PX, y, PZ), PR + 0.035, 0.05, "iron", rot=NS, verts=64)
for yy in (YS - 0.04, YN + 0.04):                                                # bolted end covers
    cyl((PX, yy, PZ), PR + 0.06, 0.08, "iron_dk", rot=NS, verts=64)
    for i in range(16):
        a = 2 * PI * i / 16
        cyl((PX + (PR + 0.02) * math.cos(a), yy + (0.045 if yy > PY else -0.045), PZ + (PR + 0.02) * math.sin(a)),
            0.018, 0.03, "bolt", rot=NS, verts=6, bevel=0)
cyl((PX, YS - 0.1, PZ), 0.26, 0.06, "nickel", rot=NS, verts=48)                  # the seal housing's face
cyl((PX, YS - 0.16, PZ), 0.16, 0.1, "iron_dk", rot=NS, verts=32)
box((PX + PR + 0.02, PY, PZ - 0.05), (0.05, 0.44, 0.24), "nickel", bevel=0.006)   # the cast nameplate boss
stencil((PX + PR + 0.05, PY, PZ - 0.05), (0.012, 0.32, 0.12))
label(2, "rotary vane pump: cast body bolted over the vent", (PX + 0.45, PY, PZ + 0.35))

# ---------------------------------------------------------------- the open drive, south: motor, coupling, shaft
YM = -1.12                                                                       # the motor's middle
cyl((PX, (YS - 0.2 + YM) / 2, PZ), 0.055, YS - 0.2 - YM, "bare", rot=NS, verts=24)    # the shaft
for yy in (YS - 0.26, -0.8):                                                     # bearing pedestals
    box((PX, yy, (PZ - 0.05) / 2 + 0.02), (0.34, 0.14, PZ - 0.05), "iron_dk", bevel=0.012)
    cyl((PX, yy, PZ), 0.12, 0.16, "iron_dk", rot=NS, verts=32)
    cyl((PX, yy, PZ + 0.12), 0.02, 0.06, "brass", verts=8)
box((PX, -0.57, 0.12), (0.62, 0.42, 0.24), "iron_dk", bevel=0.02)                 # the drive's bedplate
box((PX, -0.57, 0.25), (0.54, 0.34, 0.02), "dark", bevel=0)                      # its drip tray
coupling(PX, -0.69, PZ, 0.22, axis=(0, -1, 0), turns=2)
brake = pivot((PX, -0.575, PZ), along((0, -1, 0)))                               # the brake drum, slotted
cyl((0, 0, 0), 0.3, 0.06, "bare", verts=48, parent=brake)
for i in range(6):
    a = 2 * PI * i / 6
    box((0.2 * math.cos(a), 0.2 * math.sin(a), 0.032), (0.1, 0.035, 0.01), "dark", rz=a, bevel=0, parent=brake)
box((0.0, 0.24, 0.035), (0.08, 0.1, 0.012), "hazard", bevel=0, parent=brake)
spin(brake, 2)
for sx in (-1, 1):                                                               # the guard: rails, open-sided
    box((PX + sx * 0.36, -0.63, PZ + 0.12), (0.02, 0.3, 0.02), "yellow", bevel=0)
    box((PX + sx * 0.36, -0.63, (PZ + 0.12) / 2 + 0.12), (0.02, 0.02, PZ - 0.12), "yellow", bevel=0)
for sx in (-1, 1):                                                               # the motor's stool: two legs,
    box((PX + sx * 0.26, YM, 0.38), (0.1, 0.5, 0.76), "iron_dk", bevel=0.01)      # the helium line under it
box((PX, YM, 0.74), (0.62, 0.52, 0.06), "iron_dk", bevel=0.01)
motor(PX, YM, PZ + 0.04, d=(0, 1), s=1.1, mat="green")
box((PX + 0.28, YM, PZ + 0.12), (0.12, 0.24, 0.2), "green", bevel=0.01)           # its terminal box
cyl((PX, YM - 0.27, PZ + 0.04), 0.17, 0.06, "dark_steel", rot=NS, verts=24)     # its fan cowl
for k in range(5):
    box((PX - 0.12 + 0.06 * k, YM - 0.3, PZ + 0.04), (0.02, 0.012, 0.26), "bare", bevel=0)
label(3, "open drive: the brake drum and coupling turning", (PX, -0.6, PZ + 0.2))

# ---------------------------------------------------------------- the discharge: neck, sight port, gooseneck
NX, NY = PX, PY + 0.02
cyl((NX, NY, PZ + PR + 0.08), 0.2, 0.2, "iron_dk", verts=32)
SPZ = PZ + PR + 0.38
box((NX, NY - 0.02, SPZ), (0.56, 0.36, 0.56), "heat", bevel=0.03)                # the sight chest
melt("mt_port", "flow", scale=7.0, k=2, bright=1.4, axis="Z",
     fn=lambda t: 0.85 + 0.15 * math.cos(2 * PI * 2 * t))
cyl((NX, NY - 0.2, SPZ), 0.19, 0.02, "mt_port", rot=NS, verts=32, bevel=0)
cyl((NX, NY - 0.212, SPZ), 0.19, 0.004, "pane", rot=NS, verts=32, bevel=0)
torus((NX, NY - 0.22, SPZ), 0.205, 0.03, "nickel", rot=NS, seg=32)
for i in range(8):
    a = 2 * PI * (i + 0.5) / 8
    cyl((NX + 0.24 * math.cos(a), NY - 0.215, SPZ + 0.24 * math.sin(a)), 0.016, 0.03, "bolt", rot=NS, verts=6, bevel=0)
for sx in (-1, 1):                                                               # the port's armour bars
    box((NX + sx * 0.07, NY - 0.24, SPZ), (0.02, 0.02, 0.38), "dark_steel", bevel=0)
label(4, "armoured sight port: the melt lit as it passes", (NX, NY - 0.25, SPZ))
out_in = nozzle("N", length=0.3, mat="heat")
pipe([(NX, NY + 0.05, SPZ + 0.2), (NX, NY + 0.15, SPZ + 0.42), (NX, NY + 0.55, SPZ + 0.45), (NX, 0.98, SPZ + 0.15),
      (NX, 1.12, 0.9), (0, 1.16, ZA + 0.03), out_in], r=0.15, mat="heat")
box((NX, 1.08, 0.3), (0.56, 0.4, 0.6), "iron_dk", bevel=0.02)                    # the gooseneck's cast stool
box((NX, 1.0, 1.35), (0.4, 0.06, 0.05), "dark_steel")
label(5, "gooseneck over to the outlet", (NX, NY + 0.55, SPZ + 0.5))
label(6, "molten kamacite out, north", (0, 1.38, ZA))

# ---------------------------------------------------------------- the helium: bare metal to the seals
in_in = nozzle("S", length=0.28, mat="bare")
pipe([in_in, (0, -1.0, ZA), (0.15, -0.9, ZA), (0.45, -0.9, ZA)], r=0.07, mat="bare", flanges=False)
foundation(0.38, -1.5, 1.5, -0.62, 0.1)
box((0.62, -0.9, 0.36), (0.36, 0.5, 0.52), "grey", bevel=0.02)                   # the seal-gas manifold
valve(0.62, -1.28, z=0.1, h=0.5, r=0.06)
for k in range(2):
    gauge((0.48 + 0.26 * k, -1.16, 0.48), (0, -1, 0.3), r=0.05,
          live=(lambda kk: lambda t: 0.15 * math.sin(2 * PI * t + kk))(k))
pipe([(0.62, -0.7, 0.62), (0.4, -0.45, 0.85), (PX + 0.1, YS - 0.15, PZ + 0.12)], r=0.025, mat="bare", flanges=False)
pipe([(0.7, -0.7, 0.62), (0.75, -0.2, 1.0), (PX + 0.4, PY - 0.1, PZ + 0.42)], r=0.025, mat="bare", flanges=False)
pipe([(0.55, -0.7, 0.62), (0.7, 0.6, 0.85), (PX + 0.2, YN + 0.15, PZ + 0.1)], r=0.025, mat="bare", flanges=False)
label(7, "helium-3 in, south: bare metal, under the motor", (0, -1.38, ZA))
label(8, "seal-gas manifold: helium to the seals and the vanes", (0.62, -0.9, 0.6))
# SE: the helium bottle rack (bare bottles in a frame), its regulator
for i in range(2):
    for j in range(2):
        x, y = 1.05 + 0.25 * i, -1.25 + 0.3 * j
        cyl((x, y, 0.55), 0.1, 0.9, "grey", verts=24)
        head(x, y, 1.0, 0.1, 0.07, "grey")
        cyl((x, y, 1.1), 0.03, 0.08, "brass", verts=8)
for y in (-1.42, -0.8):
    for z in (0.35, 0.75):
        box((1.18, y, z), (0.6, 0.04, 0.05), "ochre", bevel=0.004)
for x in (0.9, 1.45):
    box((x, -1.11, 0.55), (0.04, 0.66, 0.05), "ochre", bevel=0.004)
pipe([(1.05, -0.95, 1.12), (0.95, -0.8, 1.15), (0.75, -0.85, 0.62)], r=0.02, mat="bare", flanges=False)
hazard_tag((1.18, -1.45, 0.55), 0.5, 0.06)

# ---------------------------------------------------------------- the west side
# SW: the purge-gas regulator and the helium drum, beside the motor stool
foundation(-1.5, -1.5, -0.38, -0.62, 0.1)
box((-0.6, -1.15, 0.32), (0.3, 0.56, 0.44), "ochre", bevel=0.02)
cyl((-0.6, -1.15, 0.6), 0.07, 0.12, "brass", verts=16)
drum_ns(-1.08, -1.38, -0.75, 0.42, 0.3, mat="grey", bands=(-1.2, -0.92), saddles=(-1.25, -0.88))
id_panel((-1.08, -1.46, 0.45), 0.24, 0.14, stripe="yellow")
pipe([(-0.78, -0.75, 0.55), (-0.5, -0.8, 0.6), (-0.3, -0.9, ZA + 0.1), (-0.06, -1.0, ZA)], r=0.035, mat="bare",
     flanges=False)
# W: the lube-oil unit for the bearings and vanes, a cooler on it
foundation(-1.5, -0.6, -0.8, 0.62, 0.12)
box((-1.15, 0.0, 0.42), (0.66, 1.18, 0.6), "green", bevel=0.025)
radiator(-1.45, -0.88, -0.6, 0.2, 0.66, mat="green", tube="copper", fins=8)
for k in range(2):
    cyl((-1.3 + 0.25 * k, 0.3, 0.8), 0.09, 0.18, "dark_steel", verts=20)        # filter pots
    cyl((-1.3 + 0.25 * k, 0.3, 0.9), 0.1, 0.03, "bare", verts=20)
motor(-1.15, -0.25, 0.84, d=(0, 1), s=0.6, mat="green")
hose([(-0.85, 0.25, 0.8), (-0.75, 0.4, 0.95), (PX - PR - 0.05, PY + 0.25, PZ + 0.1)], r=0.03, mat="hose_k")
hose([(-0.85, -0.05, 0.75), (-0.55, -0.4, 0.7), (PX - 0.15, YS - 0.3, PZ - 0.1)], r=0.03, mat="hose_k")
label(9, "lube oil for the vanes and bearings", (-1.15, 0.0, 0.75))
# NW: the starter cabinet, tall, a roof vent on it
foundation(-1.5, 0.64, -0.6, 1.5, 0.1)
box((-1.06, 1.05, 0.62), (0.8, 0.7, 1.04), "grey", bevel=0.025)
box((-1.06, 1.05, 1.17), (0.86, 0.76, 0.05), "dark_steel")
for k in range(3):
    box((-1.3 + 0.24 * k, 0.69, 0.7), (0.16, 0.02, 0.5), "dark_steel", bevel=0.003)
status_lens(-0.8, 0.85, 1.21)
box((-0.98, 1.12, 1.28), (0.4, 0.4, 0.18), "grey", bevel=0.015)
for k in range(4):
    box((-0.98, 0.92, 1.2 + 0.035 * k), (0.34, 0.02, 0.012), "dark_steel", bevel=0)
cyl((-1.35, 1.3, 1.3), 0.06, 0.2, "dark_steel", verts=12)
bundle([(-0.68, 0.8, 0.95), (-0.76, 0.0, 0.85), (-0.7, -0.6, 0.85), (-0.3, -1.0, 0.95), (PX - 0.2, YM, PZ + 0.2)],
       cols=("black", "red", "black"), r=0.02)
# NE: the transformer
foundation(0.6, 0.62, 1.5, 1.5, 0.14)
box((1.05, 1.06, 0.55), (0.8, 0.78, 0.82), "grey", bevel=0.03)
for k in range(4):
    box((0.75 + 0.2 * k, 0.66, 0.55), (0.06, 0.04, 0.7), "grey", bevel=0.004)
for k in range(3):
    cyl((0.82 + 0.22 * k, 1.12, 1.04), 0.05, 0.16, "brass", verts=12)
    for j in range(3):
        cyl((0.82 + 0.22 * k, 1.12, 1.0 + 0.05 * j), 0.07, 0.02, "cream", verts=12)
hazard_tag((1.05, 0.66, 0.9), 0.5, 0.06)
# E: the oil drums and the local stop station
foundation(0.72, -0.6, 1.5, 0.6, 0.08)
for k, (x, y) in enumerate(((0.95, -0.35), (1.22, -0.35), (0.95, -0.08), (1.22, -0.1))):
    cyl((x, y, 0.27), 0.11, 0.38, ("ochre", "oxide", "green", "oxide")[k], verts=24)
    torus((x, y, 0.4), 0.112, 0.012, "bare", seg=24)
    cyl((x + 0.04, y + 0.04, 0.47), 0.02, 0.02, "bare", verts=8)
jbox(1.15, 0.35, w=0.5, d=0.4, h=0.6, mat="grey", z=0.08)
box((0.85, 0.3, 0.4), (0.18, 0.18, 0.64), "grey", bevel=0.01)
cyl((0.85, 0.2, 0.62), 0.04, 0.03, "red", rot=NS, verts=16)
hose([(1.3, 0.2, 0.5), (1.4, -0.1, 0.6), (1.35, -0.45, 0.48)], r=0.025, mat="hose")
stain(0.5, -0.3, 0.25, 0.12)
stain(-0.5, 0.75, 0.2, 0.1)
run(dict(name="the rotary vane pump", footprint=[3, 3]), nf=NF)
