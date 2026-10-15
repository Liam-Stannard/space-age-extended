"""Vent Pump, round 3, concept 9: THE ROTARY VANE PUMP (3 x 3). Artist B.

  $BLENDER -b --python vpb4_09_rotary_vane_pump.py -- <out-dir> [--quick] [--only working|idle] [--colourmap] [--check]

Round 2's pump (options/round-2/vpb_09_rotary_vane_pump.py), the plumbing made honest and the
helium shown at work. What helium does: it is the seal gas, kept at a pressure over the melt
in the shaft seal and the vane chamber so the melt cannot creep out along the shaft or the
vanes; what leaks past into the chamber is purged off to the spent-gas receiver.

The chain: helium-3 in at the south nozzle, under the motor stool along the grey-violet line,
east through the turning flow meter into the seal-gas manifold (south-east), topped up from
the reserve bottle rack; from the manifold two violet lines go to the shaft seal housing and
to the top of the vane chamber. Twice a loop the purge valve on the casing's east shoulder
ticks open and the chamber's gas is let off to the spent-gas receiver (east): the meter
races and the manifold's gauges swing as the manifold makes the loss up. The melt: up the
refractory suction bell from the vent into the cast pump, thrown up the discharge neck past
the armoured sight port, over the gooseneck and down to the north nozzle.
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpb4_kit import *  # noqa: F401,F403,E402
import vpb3_kit as K  # noqa: E402

build_materials4(((0.5, 0.3), (1.5, 0.4)))
NF = 24
PX, PY, PZ = 0.0, 0.22, 0.92
PR, PL = 0.6, 0.86
YS = PY - PL / 2
YN = PY + PL / 2
NS = (PI / 2, 0, 0)


def purge(t):
    """The purge valve open twice a loop."""
    return max(pulse(t, 0.1, 0.22, 0.04), pulse(t, 0.6, 0.72, 0.04))


def makeup(t):
    """The manifold making the loss up, just after each purge."""
    return max(pulse(t, 0.14, 0.36, 0.06), pulse(t, 0.64, 0.86, 0.06))


RATE = lambda t: 0.25 + makeup(t)          # noqa: E731

# ---------------------------------------------------------------- the vent collar and the suction bell
vent_collar(PX, PY, 0.5, h=0.2)
cone((PX, PY, 0.3), 0.46, 0.3, 0.2, "refractory")
label(1, "suction bell over the vent: the melt drawn up into the pump", (PX + 0.45, PY - 0.35, 0.25))

# ---------------------------------------------------------------- the cast pump body
for sx in (-1, 1):
    foundation(PX + sx * 0.68 - 0.13, PY - 0.5, PX + sx * 0.68 + 0.13, PY + 0.5, 0.34, "iron_dk")
    for yy in (PY - 0.3, PY + 0.3):
        box((PX + sx * 0.5, yy, 0.55), (0.2, 0.06, 0.5), "iron_dk", bevel=0.008)
cyl((PX, PY, PZ), PR, PL, "iron", rot=NS, verts=64)
for k in range(5):
    y = YS + 0.1 + k * (PL - 0.2) / 4
    cyl((PX, y, PZ), PR + 0.035, 0.05, "iron", rot=NS, verts=64)
for yy in (YS - 0.04, YN + 0.04):
    cyl((PX, yy, PZ), PR + 0.06, 0.08, "iron_dk", rot=NS, verts=64)
    for i in range(16):
        a = 2 * PI * i / 16
        cyl((PX + (PR + 0.02) * math.cos(a), yy + (0.045 if yy > PY else -0.045), PZ + (PR + 0.02) * math.sin(a)),
            0.018, 0.03, "bolt", rot=NS, verts=6, bevel=0)
cyl((PX, YS - 0.1, PZ), 0.26, 0.06, "nickel", rot=NS, verts=48)
cyl((PX, YS - 0.16, PZ), 0.16, 0.1, "he_edge", rot=NS, verts=32)            # the seal housing (helium-blanketed)
torus((PX, YS - 0.16, PZ), 0.16, 0.012, "he_band", rot=NS, seg=32)
box((PX + PR + 0.02, PY, PZ - 0.05), (0.05, 0.44, 0.24), "nickel", bevel=0.006)
stencil((PX + PR + 0.05, PY, PZ - 0.05), (0.012, 0.32, 0.12))
label(2, "rotary vane pump: the cast body over the vent", (PX - 0.3, PY + 0.1, PZ + 0.5))

# ---------------------------------------------------------------- the open drive, south: motor, coupling, shaft
YM = -1.12
cyl((PX, (YS - 0.2 + YM) / 2, PZ), 0.055, YS - 0.2 - YM, "bare", rot=NS, verts=24)
for yy in (YS - 0.26, -0.8):
    box((PX, yy, (PZ - 0.05) / 2 + 0.02), (0.34, 0.14, PZ - 0.05), "iron_dk", bevel=0.012)
    cyl((PX, yy, PZ), 0.12, 0.16, "iron_dk", rot=NS, verts=32)
    cyl((PX, yy, PZ + 0.12), 0.02, 0.06, "brass", verts=8)
box((PX, -0.57, 0.12), (0.62, 0.42, 0.24), "iron_dk", bevel=0.02)
box((PX, -0.57, 0.25), (0.54, 0.34, 0.02), "dark", bevel=0)
coupling(PX, -0.69, PZ, 0.22, axis=(0, -1, 0), turns=2)
brake = pivot((PX, -0.575, PZ), along((0, -1, 0)))
cyl((0, 0, 0), 0.3, 0.06, "bare", verts=48, parent=brake)
for i in range(6):
    a = 2 * PI * i / 6
    box((0.2 * math.cos(a), 0.2 * math.sin(a), 0.032), (0.1, 0.035, 0.01), "dark", rz=a, bevel=0, parent=brake)
box((0.0, 0.24, 0.035), (0.08, 0.1, 0.012), "hazard", bevel=0, parent=brake)
spin(brake, 2)
for sx in (-1, 1):
    box((PX + sx * 0.36, -0.63, PZ + 0.12), (0.02, 0.3, 0.02), "yellow", bevel=0)
    box((PX + sx * 0.36, -0.63, (PZ + 0.12) / 2 + 0.12), (0.02, 0.02, PZ - 0.12), "yellow", bevel=0)
for sx in (-1, 1):                                       # the motor's stool: legs set back, the helium line under it
    box((PX + sx * 0.26, YM - 0.08, 0.38), (0.1, 0.3, 0.76), "iron_dk", bevel=0.01)
box((PX, YM, 0.74), (0.62, 0.52, 0.06), "iron_dk", bevel=0.01)
motor(PX, YM, PZ + 0.04, d=(0, 1), s=1.1, mat="green")
box((PX + 0.28, YM, PZ + 0.12), (0.12, 0.24, 0.2), "green", bevel=0.01)
cyl((PX, YM - 0.27, PZ + 0.04), 0.17, 0.06, "dark_steel", rot=NS, verts=24)
for k in range(5):
    box((PX - 0.12 + 0.06 * k, YM - 0.3, PZ + 0.04), (0.02, 0.012, 0.26), "bare", bevel=0)
label(3, "open drive: brake drum and coupling turning", (PX - 0.2, -0.6, PZ + 0.2))

# ---------------------------------------------------------------- the discharge: neck, sight port, gooseneck
NX, NY = PX, PY + 0.02
cyl((NX, NY, PZ + PR + 0.08), 0.2, 0.2, "iron_dk", verts=32)
SPZ = PZ + PR + 0.38
box((NX, NY - 0.02, SPZ), (0.56, 0.36, 0.56), "heat", bevel=0.03)
melt("mt_port", "flow", scale=7.0, k=2, bright=1.4, axis="Z",
     fn=lambda t: 0.85 + 0.15 * math.cos(2 * PI * 2 * t))
cyl((NX, NY - 0.2, SPZ), 0.19, 0.02, "mt_port", rot=NS, verts=32, bevel=0)
cyl((NX, NY - 0.212, SPZ), 0.19, 0.004, "pane", rot=NS, verts=32, bevel=0)
torus((NX, NY - 0.22, SPZ), 0.205, 0.03, "nickel", rot=NS, seg=32)
for i in range(8):
    a = 2 * PI * (i + 0.5) / 8
    cyl((NX + 0.24 * math.cos(a), NY - 0.215, SPZ + 0.24 * math.sin(a)), 0.016, 0.03, "bolt", rot=NS, verts=6, bevel=0)
for sx in (-1, 1):
    box((NX + sx * 0.07, NY - 0.24, SPZ), (0.02, 0.02, 0.38), "dark_steel", bevel=0)
label(4, "armoured sight port: the melt lit as it passes", (NX, NY - 0.25, SPZ))
out_in = nozzle("N", length=0.3, mat="heat")
GOOSE = [(NX, NY + 0.05, SPZ + 0.2), (NX, NY + 0.15, SPZ + 0.42), (NX, NY + 0.55, SPZ + 0.45), (NX, 0.98, SPZ + 0.15),
         (NX, 1.12, 0.9), (0, 1.16, ZA + 0.03), out_in]
pipe(GOOSE, r=0.15, mat="heat", name="gooseneck (melt)")
box((NX, 1.08, 0.3), (0.56, 0.4, 0.6), "iron_dk", bevel=0.02)
box((NX, 1.0, 1.35), (0.4, 0.06, 0.05), "dark_steel")
label(5, "gooseneck over to the outlet", (NX, NY + 0.55, SPZ + 0.5))
label(6, "molten kamacite out, north", (0, 1.38, ZA))

# ---------------------------------------------------------------- the helium: south nozzle, meter, manifold, seals
in_in = nozzle("S", length=0.28, mat="bare")
IN = [in_in, (0, -1.02, ZA), (0.06, -0.97, ZA), (0.25, -0.97, ZA)]
he_line(IN, name="helium in: nozzle under the stool to the flow meter")
flow_meter((0.345, -0.97, ZA), (1, 0, 0), r=0.1, turns=2, rate=RATE)              # its body runs into the manifold
foundation(0.38, -1.47, 1.47, -0.62, 0.1)
box((0.62, -0.9, 0.36), (0.36, 0.5, 0.52), "he_edge", bevel=0.02)            # the seal-gas manifold
for zz in (0.22, 0.5):
    box((0.62, -0.9, zz), (0.37, 0.51, 0.04), "he_band", bevel=0.004)
for k in range(2):
    he_gauge((0.52 + 0.2 * k, -1.16, 0.5), (0, -1, 0.4), r=0.075,
             live=(lambda kk: lambda t: -0.3 + 1.1 * makeup(t - 0.03 * kk))(k))
# the sight tank stands on the manifold, the seal gas through it: in at its foot (the manifold's top), out of its head
G0_, G1_ = (0.56, -0.9, 0.6), (0.56, -0.9, 1.4)
ga, gb = axis_pts(G0_, G1_, 0.1)
sight_tank(G0_, G1_, stroke_pulse((0.14, 0.64), rise=0.05, fall=0.36), r=0.14)
SEAL = [G1_, gb, (0.42, -0.62, 1.42), (0.2, -0.45, 1.15), (0.08, YS - 0.16, PZ + 0.08)]
he_line(SEAL, r=0.04, bands=0.18, name="seal gas: the sight glass to the shaft seal")
label(12, "helium sight glass on the manifold: the level drops and flushes pink as it makes up", (0.56, -0.9, 1.0))
CHAMBER = [(0.75, -0.7, 0.62), (0.8, -0.3, 1.0), (PX + 0.4, PY - 0.1, PZ + 0.42)]
he_line(CHAMBER, r=0.04, bands=0.18, name="seal gas: manifold to the vane chamber")
label(7, "helium-3 in, south: the grey-violet line under the motor", (0, -1.38, ZA))
label(8, "flow meter and seal-gas manifold: the meter races, the gauges swing", (0.55, -0.95, 0.65))
label(9, "seal gas into the shaft seal and the vane chamber", (0.5, -0.5, 1.1))
# SE: the reserve bottle rack, its header into the manifold
for i in range(2):
    for j in range(2):
        x, y = 1.03 + 0.25 * i, -1.22 + 0.3 * j
        cyl((x, y, 0.55), 0.1, 0.9, "grey", verts=24)
        torus((x, y, 0.75), 0.1, 0.012, "he_band", seg=24)
        head(x, y, 1.0, 0.1, 0.07, "grey")
        cyl((x, y, 1.1), 0.03, 0.08, "brass", verts=8)
cyl((1.155, -1.22, 1.15), 0.025, 0.3, "bare", rot=(0, PI / 2, 0), verts=10)
cyl((1.155, -0.92, 1.15), 0.025, 0.3, "bare", rot=(0, PI / 2, 0), verts=10)
for y in (-1.4, -0.78):
    for z in (0.35, 0.75):
        box((1.16, y, z), (0.6, 0.04, 0.05), "ochre", bevel=0.004)
for x in (0.88, 1.43):
    box((x, -1.09, 0.55), (0.04, 0.66, 0.05), "ochre", bevel=0.004)
he_line([(1.03, -0.92, 1.15), (0.9, -0.85, 1.05), (0.75, -0.8, 0.62)], r=0.03, bands=0.15,
        name="reserve bottles into the manifold")
hazard_tag((1.16, -1.43, 0.55), 0.5, 0.06)

# ---------------------------------------------------------------- spent gas: the purge valve and the receiver (E)
PURGE_A = [(PX + 0.42, PY + 0.05, PZ + 0.42), (0.6, 0.2, 1.38), (0.78, 0.05, 1.32)]
cyl((PX + 0.38, PY + 0.05, PZ + 0.45), 0.06, 0.1, "bare", rot=(0, PI / 4, 0), verts=16)   # the chamber's purge port
he_line(PURGE_A, r=0.04, bands=0.18, name="purge: vane chamber to the purge valve")
tick_valve(0.85, 0.0, 1.3, purge, axis=(1, -0.6, 0), mat="red")
PURGE_B = [(0.92, -0.04, 1.3), (1.05, -0.08, 1.28), (1.12, -0.1, 1.18)]
he_line(PURGE_B, r=0.04, bands=0.18, name="purge: valve into the spent-gas receiver")
foundation(0.78, -0.55, 1.45, 0.5, 0.08)
vtank(1.12, -0.1, 0.3, 1.05, mat="grey", bands=(0.35, 0.75), band_mat="he_edge", nozzle=None)
he_gauge((1.12, -0.42, 0.62), (0, -1, 0.2), r=0.07, live=lambda t: 0.6 * purge(t) - 0.3)
id_panel((1.12, -0.415, 0.88), 0.22, 0.1, stripe="yellow")
label(10, "purge valve ticks: the spent gas off to the receiver", (0.85, 0.0, 1.45))
jbox(0.92, 0.35, w=0.3, d=0.24, h=0.5, mat="grey", z=0.08)
cyl((0.92, 0.22, 0.4), 0.04, 0.03, "red", rot=NS, verts=16)
route("he", [(0, -1.5, ZA)] + IN + [(0.345, -0.97, ZA), (0.56, -0.97, ZA), (0.56, -0.9, 0.62), G1_])
route("he", SEAL)
route("he", CHAMBER)
route("spent", PURGE_A + [(0.85, 0.0, 1.3)] + PURGE_B + [(1.12, -0.1, 0.6)])
route("melt", [(PX, PY, 0.2), (PX, PY, PZ), (NX, NY, PZ + PR), (NX, NY, SPZ)] + GOOSE[1:-1] + [(0, 1.5, ZA)])

# ---------------------------------------------------------------- the west side
# SW: the local stop station and the spare-vane crate
foundation(-1.46, -1.46, -0.38, -0.62, 0.1)
box((-0.6, -1.15, 0.32), (0.3, 0.5, 0.44), "ochre", bevel=0.02)
cyl((-0.6, -1.4, 0.42), 0.045, 0.03, "red", rot=NS, verts=16)
box((-1.05, -1.02, 0.3), (0.6, 0.6, 0.4), "oxide", bevel=0.02)
for k in range(3):
    box((-1.05, -1.02, 0.12 + 0.12 * k), (0.62, 0.62, 0.025), "dark_steel", bevel=0.004)
id_panel((-1.05, -1.33, 0.3), 0.24, 0.14, stripe="yellow")
bundle([(-0.6, -0.9, 0.5), (-0.4, -0.95, 0.85), (-0.12, -1.12, 1.08)], cols=("black", "red"), r=0.014,
       name="stop station to the motor")
# W: the lube-oil unit for the bearings and vanes, a cooler on it
foundation(-1.5, -0.6, -0.8, 0.62, 0.12)
box((-1.15, 0.0, 0.42), (0.66, 1.18, 0.6), "green", bevel=0.025)
radiator(-1.45, -0.88, -0.6, 0.2, 0.66, mat="green", tube="copper", fins=8)
for k in range(2):
    cyl((-1.3 + 0.25 * k, 0.3, 0.8), 0.09, 0.18, "dark_steel", verts=20)
    cyl((-1.3 + 0.25 * k, 0.3, 0.9), 0.1, 0.03, "bare", verts=20)
motor(-1.15, -0.25, 0.84, d=(0, 1), s=0.6, mat="green")
hose([(-0.85, 0.25, 0.7), (-0.75, 0.4, 0.95), (PX - PR + 0.06, PY + 0.25, PZ + 0.1)], r=0.03, mat="hose_k",
     name="lube oil to the vane chamber")
hose([(-0.85, -0.05, 0.7), (-0.55, -0.4, 0.75), (PX - 0.1, YS - 0.28, PZ - 0.1)], r=0.03, mat="hose_k",
     name="lube oil to the seal-end bearing")
label(11, "lube oil for the vanes and bearings", (-1.15, 0.0, 0.75))
# NW: the starter cabinet
foundation(-1.47, 0.64, -0.6, 1.47, 0.1)
box((-1.02, 1.03, 0.62), (0.76, 0.7, 1.04), "grey", bevel=0.025)
box((-1.02, 1.03, 1.17), (0.82, 0.76, 0.05), "dark_steel")
for k in range(3):
    box((-1.26 + 0.24 * k, 0.67, 0.7), (0.16, 0.02, 0.5), "dark_steel", bevel=0.003)
status_lens(-0.78, 0.83, 1.21)
box((-0.96, 1.1, 1.28), (0.4, 0.4, 0.18), "grey", bevel=0.015)
bundle([(-0.68, 0.8, 0.95), (-0.76, 0.0, 0.85), (-0.7, -0.6, 0.85), (-0.3, -1.0, 0.98), (-0.1, -1.12, 1.08)],
       cols=("black", "red", "black"), r=0.02, name="starter to the motor")
# NE: the transformer, its feed into the starter
foundation(0.6, 0.62, 1.4, 1.4, 0.14)
box((1.0, 1.01, 0.55), (0.74, 0.72, 0.82), "grey", bevel=0.03)
for k in range(4):
    box((0.72 + 0.18 * k, 0.645, 0.55), (0.06, 0.04, 0.7), "grey", bevel=0.004)
for k in range(3):
    cyl((0.8 + 0.2 * k, 1.08, 1.04), 0.05, 0.16, "brass", verts=12)
    for j in range(3):
        cyl((0.8 + 0.2 * k, 1.08, 1.0 + 0.05 * j), 0.07, 0.02, "cream", verts=12)
hazard_tag((1.0, 0.645, 0.9), 0.5, 0.06)
trunk([(0.8, 1.08, 1.12), (0.5, 1.3, 1.25), (-0.3, 1.35, 1.25), (-0.7, 1.2, 1.16)], r=0.035,
      name="transformer to the starter")
stain(0.5, -0.3, 0.25, 0.12)
stain(-0.5, 0.75, 0.2, 0.1)
run4(dict(name="the rotary vane pump", footprint=[3, 3]), nf=NF)
