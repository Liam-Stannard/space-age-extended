"""Vent Pump, round 2, concept 19: THE PERISTALTIC HOSE PUMP (3 x 3). Artist B.

  $BLENDER -b --python vpb_19_peristaltic_hose_pump.py -- <out-dir> [--quick] [--only working|idle] [--colourmap]

The chain, vent to outlet: helium-3 comes in bare through the south nozzle and is let into
the vent collar under the pump, a gas cap that presses the melt up the suction riser on the
north-west. The riser feeds a huge armoured hose laid in a U round the inside of a cast
track; a three-roller rotor on a vertical shaft over the vent squeezes the hose against the
track, so each roller drives a slug of melt round the U ahead of it (the bulges). The hose
leaves the track on the north-east into a sight glass, where each slug shows orange as it
passes, and on to the north nozzle. The drive is the motor on the south-east, its coupling
turning, into the right-angle gearbox in the pump's cast pedestal.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpb_kit import *  # noqa: F401,F403,E402
import vpb_kit as K  # noqa: E402

K.build_materials(((0.5, 0.3), (0.9, 0.3)))
NF = 24
RX, RY = 0.0, 0.0                 # the rotor's axis, over the vent
RH = 0.7                          # the hose's centreline radius round the U
HR = 0.13                         # the hose's radius
ZF = 0.5                          # the track's floor (the pedestal's top)
ZH = ZF + HR                      # the hose's axis
RT0, RT1 = RH + HR + 0.02, RH + HR + 0.13      # the track wall, inner and outer
YN = 0.85                         # the U's straight legs run north to here
RR, RRO = 0.47, 0.15              # the rollers' radius from the axis, the rollers' own radius
TURN = 1.0 / 3.0                  # the rotor's turns a loop: one roller pitch, seamless


def roller_angles(t):
    return [-PI / 2 + 2 * PI * k / 3 + 2 * PI * TURN * t for k in range(3)]


def gauss(x, w):
    return math.exp(-(x / w) ** 2)


def hose_fn(p, s, t):
    """Squeezed flat under each roller on the U's bend; a bulge (the slug) running ahead of it,
    midway to the next; round on the straight legs."""
    dx, dy = p.x - RX, p.y - RY
    if dy > 0.02:
        return 1.0
    phi = math.atan2(dy, dx)
    best = 9.0
    for a in roller_angles(t):
        d = (phi - a + PI) % (2 * PI) - PI           # + ahead of the roller (the rotor turns +)
        best = min(best, abs(d))
    ahead = min(((phi - a) % (2 * PI)) for a in roller_angles(t))
    return 1.0 - 0.65 * gauss(best, 0.2) + 0.3 * gauss(ahead - PI / 3, 0.38)


# ---------------------------------------------------------------- the cast pedestal (the gearbox) and the track
vent_collar(RX, RY, 0.4, h=0.12)
cyl((RX, RY, ZF / 2), RT1, ZF, "iron", verts=96)
box((RX, (RY + YN) / 2 + 0.05, ZF / 2), (2 * RT1, YN - RY + 0.1, ZF), "iron", bevel=0.02)
for k in range(10):                                                              # the pedestal's cast ribs
    a = PI + PI * k / 9
    box((RX + (RT1 + 0.02) * math.cos(a), RY + (RT1 + 0.02) * math.sin(a), ZF / 2 - 0.02), (0.08, 0.05, ZF - 0.08),
        "iron", rz=a, bevel=0.008)
cyl((RX, RY, ZF - 0.01), RT0, 0.02, "iron_dk", verts=96)                         # the track's floor plate
box((RX, (RY + YN) / 2, ZF - 0.01), (2 * RT0, YN - RY, 0.02), "iron_dk", bevel=0)
sector((RX, RY, ZF + 0.22), RT0, RT1, PI, 2 * PI, 0.44, "iron_dk", seg=48)       # the U's bend
for sx in (-1, 1):                                                               # and its straight legs
    box((RX + sx * (RT0 + RT1) / 2, (RY + YN) / 2, ZF + 0.22), (RT1 - RT0, YN - RY, 0.44), "iron_dk", bevel=0.01)
torus((RX, RY, ZF + 0.44), (RT0 + RT1) / 2, 0.035, "dark_steel", seg=96)         # the wall's cap
for i in range(18):
    a = PI + PI * (i + 0.5) / 18
    cyl((RX + (RT0 + RT1) / 2 * math.cos(a), RY + (RT0 + RT1) / 2 * math.sin(a), ZF + 0.47), 0.016, 0.02, "bolt",
        verts=6, bevel=0)
for sx in (-1, 1):                                                               # the north gate between the legs
    box((RX + sx * 0.3, YN + 0.02, ZF + 0.18), (0.36, 0.06, 0.36), "iron_dk", bevel=0.01)
box((RX, YN + 0.02, ZF + 0.18), (0.24, 0.06, 0.36), "hazard", bevel=0.004)
label(4, "the cast track: the hose laid in a U against it", (RX - 0.75, RY - 0.55, ZF + 0.4))

# ---------------------------------------------------------------- the armoured hose, its bulges travelling
pts = [Vector((-RH, YN + 0.18, ZH + 0.05)), Vector((-RH, YN - 0.1, ZH)), Vector((-RH, 0.3, ZH))]
for k in range(25):
    a = PI + PI * k / 24
    pts.append(Vector((RX + RH * math.cos(a), RY + RH * math.sin(a), ZH)))
pts += [Vector((RH, 0.3, ZH)), Vector((RH, YN - 0.1, ZH)), Vector((RH, YN + 0.18, ZH + 0.05))]
BulgeHose([tuple(p) for p in pts], HR, mat="hose_k", seg=22, step=0.015, fn=hose_fn, bands=0.1)
label(5, "the armoured hose: squeezed by the rollers, the slugs bulge ahead", (RX + 0.55, RY - 0.5, ZH + 0.1))

# ---------------------------------------------------------------- the rotor: hub, three arms, three rollers
rot = pivot((RX, RY, 0.0))
cyl((0, 0, ZF + 0.25), 0.2, 0.5, "iron_dk", verts=48, parent=rot)
cyl((0, 0, ZF + 0.52), 0.24, 0.06, "ochre", verts=48, parent=rot)
cyl((0, 0, ZF + 0.56), 0.12, 0.05, "nickel", verts=32, parent=rot)
box((0, 0, ZF + 0.595), (0.04, 0.22, 0.012), "hazard", bevel=0, parent=rot)
for k in range(3):
    a = -PI / 2 + 2 * PI * k / 3
    ca, sa = math.cos(a), math.sin(a)
    arm = pivot((0, 0, 0), (0, 0, a), parent=rot)
    for z in (ZF + 0.08, ZF + 0.48):                                              # upper and lower arms
        box((RR / 2 + 0.05, 0, z), (RR + 0.1, 0.16, 0.06), "ochre", bevel=0.012, parent=arm)
    box((RR / 2 + 0.05, 0, ZF + 0.51), (RR - 0.1, 0.08, 0.012), "hazard", bevel=0, parent=arm)
    cyl((RR, 0, ZH), RRO, 0.32, "nickel", verts=40, parent=arm)                     # the roller
    cyl((RR, 0, ZH + 0.17), RRO * 0.5, 0.04, "dark_steel", verts=20, parent=arm)
    cyl((RR, 0, ZF + 0.52), 0.05, 0.06, "dark_steel", verts=16, parent=arm)
spin(rot, TURN)
label(6, "the rotor: three rollers turning a pitch a loop", (RX, RY, ZF + 0.6))

# ---------------------------------------------------------------- the suction riser (NW) and the vent's gas cap
lagged([(-0.35, 0.3, 0.12), (-0.55, 0.9, 0.18), (-RH - 0.02, 1.12, 0.35), (-RH, YN + 0.2, ZH + 0.06)], r=0.12,
       bands=0.16)
cyl((-RH, YN + 0.2, ZH + 0.06), HR * 1.45, 0.1, "dark_steel", rot=(PI / 2, 0, 0), verts=32)   # the hose's end clamp
bolts_ring = [(-RH + HR * 1.25 * math.cos(2 * PI * i / 8), YN + 0.15, ZH + 0.06 + HR * 1.25 * math.sin(2 * PI * i / 8))
              for i in range(8)]
for b in bolts_ring:
    cyl(b, 0.014, 0.02, "bolt", rot=(PI / 2, 0, 0), verts=6, bevel=0)
box((-RH, 1.18, 0.2), (0.4, 0.3, 0.4), "refractory", bevel=0.02)                   # the riser's foot
label(3, "suction riser up from the vent", (-RH, 1.12, 0.45))

# ---------------------------------------------------------------- the outlet (NE): end clamp, sight glass, nozzle
cyl((RH, YN + 0.2, ZH + 0.06), HR * 1.45, 0.1, "dark_steel", rot=(PI / 2, 0, 0), verts=32)
melt("mt_glass", "flow", scale=6.0, k=1, bright=1.5, axis="X",
     fn=lambda t: 0.35 + 0.65 * pulse(t, 0.25, 0.6, 0.12))
out_in = nozzle("N", length=0.3, mat="heat")
pipe([(RH, YN + 0.25, ZH + 0.06), (RH - 0.05, 1.08, ZH + 0.05), (0.5, 1.12, ZH)], r=0.1, mat="heat", flanges=False)
cyl((0.36, 1.13, ZH), 0.1, 0.26, "mt_glass", rot=(0, PI / 2, 0), verts=24, bevel=0)      # the sight glass
cyl((0.36, 1.13, ZH), 0.125, 0.26, "glass", rot=(0, PI / 2, 0), verts=24, bevel=0)
for xx in (0.22, 0.5):
    cyl((xx, 1.13, ZH), 0.15, 0.04, "dark_steel", rot=(0, PI / 2, 0), verts=24)
for i in range(4):
    a = 2 * PI * (i + 0.5) / 4
    cyl((0.36, 1.13 + 0.13 * math.cos(a), ZH + 0.13 * math.sin(a)), 0.012, 0.24, "bare", rot=(0, PI / 2, 0),
        verts=6, bevel=0)
pipe([(0.24, 1.13, ZH), (0.1, 1.15, ZH - 0.05), out_in], r=0.1, mat="heat", flanges=False)
box((0.36, 1.13, 0.2), (0.3, 0.2, 0.4), "iron_dk", bevel=0.01)
label(7, "sight glass: each slug lit as it passes", (0.36, 1.13, ZH + 0.1))
label(8, "molten kamacite out, north", (0, 1.38, ZA))

# ---------------------------------------------------------------- the helium: south nozzle into the vent's gas cap
in_in = nozzle("S", length=0.3, mat="bare")
pipe([in_in, (0, -1.05, ZA), (0, -0.9, 0.3), (0, -0.82, 0.25)], r=0.06, mat="bare", flanges=False)
valve(-0.2, -1.12, z=0.05, h=0.5, r=0.06)
pipe([(-0.2, -1.12, 0.25), (-0.08, -1.12, ZA - 0.05)], r=0.03, mat="bare", flanges=False)
gauge((0.14, -1.1, 0.5), (0, -1, 0.3), r=0.05, live=lambda t: 0.2 * math.sin(2 * PI * t))
label(1, "helium-3 in, south: bare metal", (0, -1.38, ZA))
label(2, "into the vent collar: a gas cap that presses the melt up", (0, -0.86, 0.32))

# ---------------------------------------------------------------- the drive (SE): motor, coupling, gearbox
foundation(0.6, -1.5, 1.5, -0.62, 0.12)
box((0.82, -0.82, 0.32), (0.42, 0.42, 0.42), "iron_dk", bevel=0.02)                 # the right-angle gearbox
cyl((0.82, -0.82, 0.56), 0.12, 0.06, "nickel", verts=24)
cyl((0.66, -0.66, 0.3), 0.07, 0.3, "bare", rot=(0, PI / 2, PI / 4), verts=16)     # its shaft into the pedestal
pv = motor(1.18, -1.15, 0.45, d=(-1, 0), s=0.85, mat="green")
coupling(0.92, -1.15, 0.45, 0.13, axis=(-1, 0, 0), turns=3)
pipe([(0.92, -1.15, 0.45), (0.82, -1.05, 0.38)], r=0.05, mat="bare", flanges=False)
box((1.3, -0.82, 0.42), (0.3, 0.26, 0.42), "grey", bevel=0.015)
label(9, "the drive: motor and coupling into the gearbox", (1.1, -1.15, 0.65))

# ---------------------------------------------------------------- the corners
# SW: the helium buffer and the housing purge
foundation(-1.5, -1.5, -0.42, -0.62, 0.1)
vtank(-1.02, -1.08, 0.34, 0.95, mat="grey", bands=(0.45,), nozzle=(0.0, 0.0))
id_panel((-1.02, -1.43, 0.6), 0.24, 0.12, stripe="yellow")
pipe([(-0.7, -1.05, 0.35), (-0.45, -1.1, 0.3), (-0.22, -1.12, 0.25)], r=0.035, mat="bare", flanges=False)
pipe([(-1.02, -0.8, 0.95), (-0.95, -0.6, 0.9), (-0.7, -0.45, ZF + 0.5)], r=0.025, mat="bare", flanges=False)
for k, (x, y) in enumerate(((-1.35, -0.55), (-1.35, -0.3))):
    cyl((x, y, 0.22), 0.1, 0.36, ("ochre", "oxide")[k], verts=20)
    torus((x, y, 0.34), 0.102, 0.01, "bare", seg=20)
# NW: the control cabinet
foundation(-1.5, 0.6, -0.92, 1.5, 0.1)
box((-1.2, 1.05, 0.55), (0.5, 0.82, 0.9), "grey", bevel=0.025)
for k in range(3):
    box((-1.2, 0.635, 0.4 + 0.18 * k), (0.36, 0.02, 0.1), "dark_steel", bevel=0.003)
status_lens(-1.1, 0.75, 1.02)
box((-1.2, 1.2, 1.07), (0.3, 0.3, 0.14), "grey", bevel=0.01)
bundle([(-1.2, 1.35, 1.0), (-1.3, 1.4, 0.6), (-1.35, 1.3, 0.2)], cols=("black", "red", "grey"), r=0.018)
bundle([(1.27, -0.3, 0.55), (1.38, -0.6, 0.62), (1.22, -1.0, 0.66)], cols=("black", "red", "grey"), r=0.018)
# NE: the hose-change hoist post and the spare hose coil
foundation(0.92, 0.6, 1.5, 1.5, 0.1)
cyl((1.22, 1.1, 0.35), 0.24, 0.42, "dark_steel", verts=32)
for k in range(3):
    torus((1.22, 1.1, 0.2 + 0.12 * k), 0.2, 0.06, "hose_k", seg=32)
cyl((1.35, 0.75, 0.9), 0.05, 1.6, "ochre", verts=12)
box((1.1, 0.75, 1.65), (0.6, 0.08, 0.08), "ochre", bevel=0.006)
cyl((0.85, 0.75, 1.5), 0.012, 0.25, "bare", verts=6)
box((0.85, 0.75, 1.36), (0.06, 0.06, 0.06), "yellow", bevel=0.005)
# W and E flanks: the lube points and the guard rails
for s in (-1, 1):
    foundation(min(s * 1.5, s * 1.04), -0.6, max(s * 1.5, s * 1.04), 0.6, 0.1)
    box((s * 1.27, 0.0, 0.32), (0.4, 0.9, 0.44), "green" if s < 0 else "oxide", bevel=0.02)
    for k in range(3):
        cyl((s * 1.27, -0.3 + 0.3 * k, 0.6), 0.04, 0.12, "brass", verts=12)
    hose([(s * 1.27, 0.3, 0.6), (s * 1.12, 0.35, 0.8), (s * 0.98, 0.3, ZF + 0.3)], r=0.022, mat="hose")
hazard_tag((1.27, -0.455, 0.35), 0.3, 0.06)
stain(0.6, -0.5, 0.25, 0.1)
stain(-0.4, -1.2, 0.2, 0.08)
run(dict(name="the peristaltic hose pump", footprint=[3, 3]), nf=NF)
