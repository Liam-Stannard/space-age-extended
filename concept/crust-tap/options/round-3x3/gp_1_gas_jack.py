"""Gas Pump 3x3, options round, take 1: THE GAS JACK (vanilla's pumpjack, worked on gas).

  $BLENDER -b --python gp_1_gas_jack.py -- <out-dir> [--quick] [--frames N] [--only working|idle] [--helium]

The pumpjack's own language at its own size: a long walking beam nodding on a tall samson post that stands over
the vent, its horsehead at the west end over a single-acting compressor cylinder; a gas engine that burns a slip of
the vent's own gas turns the cranks under the beam's east end (the pump needs no power, spec A.2: void).

The chain: the vent, under the wellhead between the samson post's legs; the suction line west to the compressor
cylinder's foot; the cylinder (its rod rising and falling on the horsehead's bridle); the discharge down into the
receiver (its gauge kicking each stroke); out of the receiver along the outlet line, north through the sight glass,
to the north nozzle (the line at the connection's bore, stepping down only at the nozzle's reducer). The fuel: a
tan hose from the receiver through the scrubber and the regulator to the engine's mixer.

Motion: the beam nods once a loop (the crank one turn), the rod, carrier and bridle with it; the cranks, their
counterweights and the pitman arms; the engine's flywheel and the coupling, two turns; the receiver's gauge kicks
each stroke; the gas drifts in the sight glass. Idle: all stop where they are, the glass empty.
"""
import math
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gp_kit import *  # noqa: F401,F403,E402
import gp_kit as GP  # noqa: E402
import vpb5_kit as K5  # noqa: E402
import vpb3_kit as K  # noqa: E402
from mathutils import Vector  # noqa: E402

K5.build_materials5(((0.45, 0.3), (1.3, 0.4)))
NF = 24

# ---------------------------------------------------------------- the linkage
PX, PZ = 0.15, 2.62           # the beam's pivot, on the samson post over the vent
LH, LT = 1.1, 0.98            # pivot to the horsehead's face (the bridle hangs at x = PX - LH), to the tail
CX, CZ, RC = 1.06, 0.74, 0.3  # the cranks' shaft and throw
HX = PX - LH                  # the bridle's line, over the compressor cylinder
theta, pin, tail = fourbar((PX, PZ), LT, (CX, CZ), RC, phi0=0.0)
ZC0 = 2.1                     # the carrier bar with the beam level (its lowest 1.74, over the guide at 1.64)
PHASE = 0.25                  # the loop starts with the head at the top of its nod


def th(t, on):
    return theta(((t if on else 0.0) + PHASE) % 1.0)


def carrier_z(t, on):
    return ZC0 - LH * th(t, on)


def stroke(t):
    """The compressor's delivery: the head (and rod) going down, 0..1."""
    d = th((t + 0.01) % 1.0, True) - th((t - 0.01) % 1.0, True)
    return max(0.0, min(1.0, d * 12))


# ---------------------------------------------------------------- footings: a unit on each, no deck
foundation(-0.42, -0.5, 0.62, 0.5, 0.16, "refractory")            # the wellhead and the samson post, over the vent
vent_collar(0, 0, 0.26, h=0.26)
foundation(-1.44, -0.4, -0.5, 0.42, 0.14)                         # the compressor cylinder
foundation(0.66, -0.42, 1.46, 0.5, 0.12)                          # the gearbox and cranks
foundation(0.44, -1.44, 1.42, -0.52, 0.1)                         # the gas engine
foundation(-1.42, -1.4, -0.5, -0.46, 0.1)                         # the receiver
foundation(-0.44, -1.42, 0.38, -0.56, 0.08, anchors=False)        # the fuel scrubber
foundation(-1.44, 0.5, -0.5, 1.42, 0.08)                          # the drip pot and bottles
foundation(-0.44, 0.56, 0.6, 1.46, 0.08, anchors=False)           # the outlet
foundation(0.66, 0.58, 1.42, 1.42, 0.08)                          # the control cabinet

# ---------------------------------------------------------------- 1. the wellhead over the vent, between the post's legs
cyl((0, 0, 0.36), 0.17, 0.2, "dark_steel", verts=32)
flange_ring(0, 0, 0.27, 0.17, nb=10)
flange_ring(0, 0, 0.46, 0.17, nb=10)
cyl((0, 0, 0.56), 0.1, 0.16, "bare", verts=24)
handwheel((0, 0, 0.7), 0.09, mat="red")
label(1, "vent under the wellhead, between the samson post's legs", (0.0, -0.15, 0.6))

# ---------------------------------------------------------------- 2. the compressor cylinder under the horsehead
cyl((HX + 0.25, 0, 0.66), 0.12, 0.06, "dark_steel", rot=(0, PI / 2, 0), verts=24)           # the suction port's boss
pipe([(-0.08, 0, 0.58), (-0.2, 0, 0.66), (-0.3, 0, 0.76), (-0.5, 0, 0.84), (-0.64, 0, 0.72), (HX + 0.26, 0.0, 0.66)],
     r=0.085,
     mat="iron",
     name="suction: the wellhead to the cylinder")
cyl((HX, 0, 0.26), 0.3, 0.24, "dark_steel", verts=40)                   # the cylinder's base
bolts(HX, 0, 0.39, 0.27, 10, r=0.016)
cyl((HX, 0, 0.82), 0.24, 0.86, "oxide", verts=40)
z = 0.48
while z < 1.22:
    torus((HX, 0, z), 0.245, 0.016, "dark_steel", seg=40)
    z += 0.1
cyl((HX, 0, 1.29), 0.28, 0.09, "dark_steel", verts=40)
bolts(HX, 0, 1.345, 0.25, 10, r=0.015)
for sx in (-1, 1):
    box((HX + sx * 0.13, 0, 1.48), (0.05, 0.08, 0.3), "dark_steel", bevel=0.006)
box((HX, 0, 1.64), (0.34, 0.1, 0.05), "dark_steel", bevel=0.006)
cyl((HX, 0, 1.38), 0.065, 0.08, "bare", verts=16)                                      # the stuffing box
stencil((HX, -0.245, 0.9), (0.18, 0.012, 0.1))
hazard_tag((HX, -0.31, 0.2), 0.4, 0.06)
link(lambda t, on: (HX, 0, 1.37), lambda t, on: (HX, 0, carrier_z(t, on)), r=0.03, mat="nickel",
     name="piston rod")
cbar = pivot((HX, 0, ZC0))
box((0, 0, 0), (0.26, 0.07, 0.06), "dark_steel", bevel=0.005, parent=cbar)
K.ANIM.append(lambda t, on: setattr(cbar, "location", Vector((HX, 0, carrier_z(t, on)))))
for sy in (-0.07, 0.07):
    link(lambda t, on, sy=sy: (HX, sy, PZ - 0.02), lambda t, on, sy=sy: (HX, sy, carrier_z(t, on) + 0.02), r=0.012,
         mat="dark", name="bridle")
label(2, "compressor cylinder: its rod rises and falls on the horsehead's bridle", (HX, -0.25, 1.0))

# ---------------------------------------------------------------- the samson post, the walking beam
for sy in (-0.5, 0.5):
    link(lambda t, on, sy=sy: (PX, sy, 0.16), lambda t, on: (PX, 0, PZ - 0.08), r=0.065, mat="green",
         name="samson leg")
    link(lambda t, on, sy=sy: (PX + 0.5, sy * 0.8, 0.16), lambda t, on: (PX + 0.04, 0, PZ - 0.3), r=0.045,
         mat="green", name="samson brace")
for z_ in (0.9, 1.7):
    w = 1.0 * (1 - (z_ - 0.16) / (PZ - 0.24))
    box((PX, 0, z_), (0.06, w, 0.06), "green", bevel=0.004)
box((PX, 0, PZ - 0.05), (0.22, 0.3, 0.12), "dark_steel", bevel=0.01)                   # the saddle bearing
beam = pivot((PX, 0, PZ))
BL0, BL1 = -LH + 0.12, LT + 0.12
box(((BL0 + BL1) / 2, 0, 0.12), (BL1 - BL0, 0.16, 0.24), "iron", bevel=0.014, parent=beam)
box(((BL0 + BL1) / 2, -0.07, 0.245), (BL1 - BL0, 0.03, 0.02), "yellow", bevel=0.004, parent=beam)
box(((BL0 + BL1) / 2, 0.0, 0.245), (BL1 - BL0 - 0.06, 0.08, 0.015), "dark_steel", bevel=0.003, parent=beam)
for x_ in (-0.7, -0.35, 0.0, 0.35, 0.7):
    box((x_, -0.085, 0.12), (0.02, 0.01, 0.2), "dark_steel", bevel=0.002, parent=beam)
sector((0, 0, 0), LH - 0.34, LH, PI - 0.42, PI + 0.42, 0.26, "ochre", rot=(PI / 2, 0, 0), seg=18, parent=beam)
sector((0, 0, 0), LH - 0.025, LH + 0.008, PI - 0.4, PI + 0.4, 0.29, "dark_steel", rot=(PI / 2, 0, 0), seg=18,
       parent=beam)
for k in range(5):
    a = PI - 0.32 + 0.16 * k
    cyl(((LH - 0.17) * math.cos(a), -0.135, (LH - 0.17) * math.sin(a)), 0.024, 0.02, "bolt", rot=(PI / 2, 0, 0),
        verts=6, bevel=0, parent=beam)
box((LT, 0, 0.0), (0.1, 0.64, 0.08), "dark_steel", bevel=0.006, parent=beam)           # the equalizer
cyl((0, 0, 0.02), 0.08, 0.36, "bare", rot=(PI / 2, 0, 0), verts=16, parent=beam)
hazard_tag((0.45, -0.085, 0.12), 0.34, 0.08)


def _beam(t, on):
    beam.rotation_euler = (0, -th(t, on), 0)


K.ANIM.append(_beam)
label(9, "walking beam on the samson post: one nod a loop", (PX + 0.4, -0.1, PZ + 0.2))

# ---------------------------------------------------------------- 8. the gearbox and the cranks
box((CX, 0, 0.44), (0.5, 0.44, 0.64), "green", bevel=0.03)
box((CX, 0, 0.77), (0.54, 0.48, 0.05), "dark_steel")
cyl((CX, 0, CZ), 0.045, 0.62, "bare", rot=(PI / 2, 0, 0), verts=16)
for sy in (-0.3, 0.3):
    cp = pivot((CX, sy, CZ))
    box((RC / 2, 0, 0), (RC + 0.1, 0.05, 0.1), "dark_steel", bevel=0.006, parent=cp)
    sector((0, 0, 0), 0.1, 0.42, PI - 0.6, PI + 0.6, 0.06, "oxide", rot=(PI / 2, 0, 0), seg=12, parent=cp)
    cyl((RC, 0.06 * (1 if sy > 0 else -1), 0.0), 0.035, 0.16, "bare", rot=(PI / 2, 0, 0), verts=12, parent=cp)  # the crank pin, out to the arm

    def _crank(t, on, cp=cp):
        a = 2 * PI * (((t if on else 0.0) + PHASE) % 1.0)
        cp.rotation_euler = (0, -a, 0)
    K.ANIM.append(_crank)
    link(lambda t, on, sy=sy: (pin(((t if on else 0.0) + PHASE) % 1.0)[0], sy * 1.4,
                               pin(((t if on else 0.0) + PHASE) % 1.0)[1]),
         lambda t, on, sy=sy: (tail(th(t, on))[0], sy * 1.0, tail(th(t, on))[1]), r=0.035, mat="dark_steel",
         name="pitman arm")
label(8, "gearbox and cranks, the counterweights swinging", (CX, -0.3, 0.7))

# ---------------------------------------------------------------- 7. the gas engine, on the vent's own gas
EX, EY, EZ = 1.0, -0.96, 0.52
box((EX + 0.04, EY, 0.42), (0.6, 0.6, 0.64), "green", bevel=0.03)
box((EX + 0.04, EY, 0.75), (0.64, 0.64, 0.05), "dark_steel")
for k in range(4):
    box((EX - 0.16 + 0.13 * k, EY - 0.305, 0.45), (0.07, 0.02, 0.36), "dark_steel", bevel=0.003)
cyl((0.66, EY, EZ + 0.06), 0.15, 0.4, "green", rot=(0, PI / 2, 0), verts=32)
for k in range(5):
    torus((0.54 + 0.06 * k, EY, EZ + 0.06), 0.155, 0.012, "dark_steel", rot=(0, PI / 2, 0), seg=32)
cyl((0.44, EY, EZ + 0.06), 0.17, 0.06, "dark_steel", rot=(0, PI / 2, 0), verts=32)
cyl((0.48, EY, EZ + 0.25), 0.02, 0.08, "nickel", verts=8)                               # the spark plug
cyl((EX - 0.08, EY + 0.12, 0.92), 0.04, 0.32, "bare", verts=12)                          # the exhaust stack
cyl((EX - 0.08, EY + 0.12, 1.1), 0.075, 0.07, "dark_steel", verts=16)
fw = pivot((EX + 0.05, -1.41, EZ + 0.04), along((0, -1, 0)))
torus((0, 0, 0), 0.36, 0.05, "dark_steel", seg=48, parent=fw)
cyl((0, 0, 0), 0.06, 0.08, "bare", verts=16, parent=fw)
for k in range(5):
    a = 2 * PI * k / 5
    box((0.18 * math.cos(a), 0.18 * math.sin(a), 0), (0.3, 0.04, 0.035), "green", rz=a, bevel=0.004, parent=fw)
box((0.0, 0.31, 0.0), (0.14, 0.09, 0.06), "red", bevel=0.006, parent=fw)                # a balance lug: it reads turning
spin(fw, 2)
cyl((EX + 0.05, -1.32, EZ + 0.04), 0.035, 0.2, "bare", rot=(PI / 2, 0, 0), verts=12)
coupling(CX - 0.02, -0.58, 0.44, 0.07, axis=(0, 1, 0), turns=2)
cyl((CX - 0.02, -0.62, 0.44), 0.03, 0.2, "bare", rot=(PI / 2, 0, 0), verts=12)
hazard_tag((EX + 0.04, -1.265, 0.12), 0.36, 0.05)
label(7, "gas engine on a slip of the vent's own gas: flywheel and coupling turning", (EX, -1.25, 0.8))

# ---------------------------------------------------------------- 3-4. the discharge, the receiver
RX, RY, RR = -0.98, -0.92, 0.34
top = vtank(RX, RY, RR, 1.15, mat="cream", bands=(0.62, 0.92), nozzle=None)
cyl((RX, RY, top + 0.05), 0.07, 0.12, "bare", verts=16)
pipe([(HX - 0.0, -0.24, 1.12), (HX, -0.4, 1.2), (RX, RY + 0.1, top + 0.14), (RX, RY, top + 0.1)], r=0.06,
     mat="bare", name="discharge: the cylinder to the receiver")
cyl((HX, -0.23, 1.12), 0.06, 0.06, "dark_steel", rot=(PI / 2, 0, 0), verts=16)
cyl((HX - 0.0, -0.36, 1.19), 0.08, 0.1, "dark_steel", rot=(PI / 2.6, 0, 0), verts=16)    # the check valve
gauge((RX + 0.06, RY - RR - 0.02, 0.76), (0, -1, 0.35), r=0.085, needle=0.02,
      live=lambda t: -0.3 + 1.1 * stroke(t))
id_panel((RX - 0.1, RY - RR + 0.02, 0.56), 0.2, 0.1, stripe="green")
label(3, "discharge through the check valve, down into the receiver", (HX, -0.45, 1.3))
label(4, "receiver: its gauge kicks with each stroke", (RX, RY - 0.25, 1.05))

# ---------------------------------------------------------------- 5-6. the outlet line, the sight glass, the nozzle
RO = 0.13                     # the outlet line's bore, stepped down only at the nozzle's reducer
noz = nozzle("N", length=0.28, mat="bare")
OXL = -0.46
pipe([(RX + RR - 0.02, RY, ZA), (OXL - 0.12, RY, ZA), (OXL, RY + 0.14, ZA), (OXL, -0.6, ZA), (OXL, -0.1, ZA),
      (OXL, 0.12, ZA)], r=RO, mat="iron", name="outlet: the receiver north to the sight glass")
g0, g1, _ = gas_window((OXL, 0.18, ZA), (OXL, 0.66, ZA), r=0.11, k=2)
pipe([(OXL, 0.72, ZA), (OXL, 0.86, ZA), (-0.28, 1.0, ZA), (-0.08, 1.02, ZA), (0, 1.04, ZA)], r=RO, mat="iron",
     name="outlet: the sight glass to the reducer")
reducer((0, 1.04, ZA), (0, noz[1] + 0.02, ZA), RO, 0.17)
for y_ in (-0.45, 0.85):
    box((OXL, y_, (ZA - RO) / 2 + 0.05), (0.16, 0.1, ZA - RO + 0.02), "dark_steel")
valve(OXL + 0.0, -0.3, z=ZA - 0.05, h=0.34, r=0.05)                                    # the outlet's stop valve
cyl((0.26, 1.08, 0.62), 0.04, 0.52, "bare", verts=12)                                    # the relief stack
cyl((0.26, 1.08, 0.91), 0.07, 0.06, "dark_steel", verts=16)
cyl((0.13, 1.06, ZA), 0.04, 0.26, "bare", rot=(0, PI / 2, 0), verts=12)
cyl((0.26, 1.08, 0.34), 0.07, 0.1, "brass", verts=16)
label(5, "sight glass: the gas drifts through while it pumps", (OXL, 0.42, 0.55))
label(6, "gas out, north, at the connection's bore: a reducer at the nozzle", (0, 1.3, ZA))

# ---------------------------------------------------------------- the fuel slip: receiver -> scrubber -> regulator -> engine
drum_ew(-0.14, 0.22, -0.98, 0.32, 0.18, mat="oxide", bands=(-0.05, 0.13), saddles=(-0.08, 0.15))
hose([(RX + 0.3, RY - 0.2, 0.75), (-0.5, -1.12, 0.8), (-0.3, -1.0, 0.5), (-0.25, -0.98, 0.34)], r=0.04, mat="hose",
     name="fuel hose: receiver to the fuel scrubber")
pipe([(0.05, -0.98, 0.48), (0.05, -1.0, 0.6), (0.1, -1.18, 0.56), (0.12, -1.24, 0.44)], r=0.03, mat="bare",
     name="fuel: the scrubber to the regulator")
cyl((0.12, -1.24, 0.32), 0.08, 0.18, "yellow", rot=(0, PI / 2, 0), verts=20)             # the regulator
head(0.12, -1.24, 0.39, 0.08, 0.07, "yellow")
box((0.12, -1.24, 0.14), (0.1, 0.1, 0.22), "dark_steel")
hose([(0.2, -1.24, 0.32), (0.36, -1.3, 0.36), (0.4, -1.16, 0.52), (0.44, -1.06, 0.6)], r=0.035, mat="hose",
     name="fuel hose: the regulator to the engine's mixer")
label(10, "fuel: the receiver's slip, scrubbed and regulated, to the engine", (0.1, -1.28, 0.45))

# ---------------------------------------------------------------- the control cabinet (NE), the drip pot (NW), clutter
cabinet(1.02, 1.04, 0.66, 0.52, 0.8, mat="grey")
status_lens(1.24, 0.82, 0.84)
bundle([(1.3, 0.78, 0.3), (1.42, 0.5, 0.25), (1.42, -0.3, 0.26), (1.3, -0.52, 0.5), (1.2, -0.67, 0.6)],
       cols=("black", "red"), r=0.016, name="cabinet to the engine's ignition")
vtank(-1.06, 1.04, 0.28, 0.8, mat="green", bands=(0.35,), nozzle=None)
for k, xx in enumerate((-1.28, -1.02)):
    vtank(xx, 0.62, 0.12, 0.62 + 0.06 * k, mat="ochre", bands=(0.35,), nozzle=None)
pipe([(-0.86, 0.86, 0.2), (-0.62, 0.74, 0.18), (OXL - RO + 0.01, 0.68, ZA - 0.05)], r=0.035, mat="bare",
     name="drip leg")
box((-0.8, 0.58, 0.2), (0.2, 0.2, 0.22), "oxide", bevel=0.02)                            # a tool chest
stain(0.3, -0.35, 0.22, 0.1)
stain(-0.2, -1.25, 0.18, 0.08)
stain(1.1, -0.45, 0.2, 0.08)

route("gas", [(0, 0, 0.2), (0, 0, 0.56), (-0.22, 0, 0.6), (-0.5, 0, 0.84), (HX + 0.26, 0, 0.66), (HX, 0, 0.8),
              (HX, -0.24, 1.12), (HX, -0.4, 1.2), (RX, RY + 0.1, top + 0.14), (RX, RY, 0.6),
              (RX + RR, RY, ZA), (OXL, RY + 0.14, ZA), (OXL, -0.6, ZA), (OXL, 0.18, ZA), (OXL, 0.66, ZA), (OXL, 0.86, ZA),
              (-0.28, 1.0, ZA), (0, 1.04, ZA), (0, 1.5, ZA)])
route("fuel", [(RX + 0.3, RY - 0.2, 0.75), (-0.5, -1.12, 0.8), (-0.3, -1.0, 0.5), (-0.14, -0.98, 0.32),
               (0.05, -0.98, 0.48), (0.05, -1.0, 0.6), (0.12, -1.24, 0.44), (0.2, -1.24, 0.32), (0.36, -1.3, 0.36), (0.44, -1.12, 0.5), (0.45, -1.0, 0.6)])
run_gp(dict(name="the gas jack", footprint=[3, 3], take=1), nf=NF)
