"""Vent Pump, round 3, concept 19: THE PERISTALTIC HOSE PUMP (3 x 3). Artist B.

  $BLENDER -b --python vpb3_19_peristaltic_hose_pump.py -- <out-dir> [--quick] [--only working|idle] [--colourmap] [--check]

Round 2's hose pump (options/round-2/vpb_19_peristaltic_hose_pump.py), the plumbing made honest
and the helium shown at work. What helium does: it is a gas cap held over the melt in the
vent's chamber under the pedestal, pressing the melt up the suction riser into the hose so
the hose never runs dry as the rollers draw; the pressure dome beside it is that gas cap's
accumulator, and it flexes as the rollers draw.

The chain: helium-3 in at the south nozzle, along the grey-violet line through the stop
valve and the turning flow meter into the pressure dome's vessel (south-west), and from it
by the gas-cap line into the vent chamber under the pedestal. Each loop, as a roller draws a
slug of melt into the hose, the dome sinks; the meter races and the gauge swings as the line
fills it again; at the top of the refill the relief valve on the east ticks and bleeds the
excess to the recovery receiver (east). The melt: from the vent chamber up the lagged
suction riser (north-west) into the hose, round the U ahead of the rollers, out on the
north-east through the sight glass to the north nozzle.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpb3_kit import *  # noqa: F401,F403,E402
import vpb3_kit as K  # noqa: E402

K.build_materials(((0.5, 0.3), (0.9, 0.3)))
NF = 24
RX, RY = 0.0, 0.0
RH = 0.7
HR = 0.13
ZF = 0.5
ZH = ZF + HR
RT0, RT1 = RH + HR + 0.02, RH + HR + 0.13
YN = 0.85
RR, RRO = 0.47, 0.15
TURN = 1.0 / 3.0


def roller_angles(t):
    return [-PI / 2 + 2 * PI * k / 3 + 2 * PI * TURN * t for k in range(3)]


def gauss(x, w):
    return math.exp(-(x / w) ** 2)


def hose_fn(p, s, t):
    dx, dy = p.x - RX, p.y - RY
    if dy > 0.02:
        return 1.0
    phi = math.atan2(dy, dx)
    best = 9.0
    for a in roller_angles(t):
        d = (phi - a + PI) % (2 * PI) - PI
        best = min(best, abs(d))
    ahead = min(((phi - a) % (2 * PI)) for a in roller_angles(t))
    return 1.0 - 0.65 * gauss(best, 0.2) + 0.3 * gauss(ahead - PI / 3, 0.38)


def draw(t):
    """A roller drawing a slug in: the gas cap gives, the dome sinks."""
    return pulse(t, 0.15, 0.45, 0.1)


def refill(t):
    """The line making the gas cap up again: the dome rises, the meter races."""
    return pulse(t, 0.5, 0.8, 0.08)


def bleed(t):
    """The relief valve ticks open at the top of the refill."""
    return pulse(t, 0.74, 0.86, 0.03)


RATE = lambda t: 0.15 + refill(t)          # noqa: E731

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
label(11, "the cast track: the hose laid in a U against it", (RX - 0.75, RY - 0.55, ZF + 0.4))

# ---------------------------------------------------------------- the armoured hose, its bulges travelling
pts = [Vector((-RH, YN + 0.18, ZH + 0.05)), Vector((-RH, YN - 0.1, ZH)), Vector((-RH, 0.3, ZH))]
for k in range(25):
    a = PI + PI * k / 24
    pts.append(Vector((RX + RH * math.cos(a), RY + RH * math.sin(a), ZH)))
pts += [Vector((RH, 0.3, ZH)), Vector((RH, YN - 0.1, ZH)), Vector((RH, YN + 0.18, ZH + 0.05))]
BulgeHose([tuple(p) for p in pts], HR, mat="hose_k", seg=22, step=0.015, fn=hose_fn, bands=0.1)
label(6, "the armoured hose: squeezed by the rollers, the slugs bulge ahead", (RX + 0.55, RY - 0.5, ZH + 0.1))

# ---------------------------------------------------------------- the rotor: hub, three arms, three rollers
rot = pivot((RX, RY, 0.0))
cyl((0, 0, ZF + 0.25), 0.2, 0.5, "iron_dk", verts=48, parent=rot)
cyl((0, 0, ZF + 0.52), 0.24, 0.06, "ochre", verts=48, parent=rot)
cyl((0, 0, ZF + 0.56), 0.12, 0.05, "nickel", verts=32, parent=rot)
box((0, 0.17, ZF + 0.552), (0.04, 0.1, 0.012), "hazard", bevel=0, parent=rot)
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
label(5, "the rotor: three rollers turning a pitch a loop", (RX, RY, ZF + 0.6))

# ---------------------------------------------------------------- the suction riser (NW) and the vent's gas cap
RISER = [(-0.35, 0.3, 0.12), (-0.55, 0.9, 0.18), (-RH - 0.02, 1.12, 0.35), (-RH, YN + 0.2, ZH + 0.06)]
lagged(RISER, r=0.12, bands=0.16, name="suction riser (melt): vent chamber to the hose")
cyl((-RH, YN + 0.2, ZH + 0.06), HR * 1.45, 0.1, "dark_steel", rot=(PI / 2, 0, 0), verts=32)   # the hose's end clamp
bolts_ring = [(-RH + HR * 1.25 * math.cos(2 * PI * i / 8), YN + 0.15, ZH + 0.06 + HR * 1.25 * math.sin(2 * PI * i / 8))
              for i in range(8)]
for b in bolts_ring:
    cyl(b, 0.014, 0.02, "bolt", rot=(PI / 2, 0, 0), verts=6, bevel=0)
box((-RH, 1.18, 0.2), (0.4, 0.3, 0.4), "refractory", bevel=0.02)                   # the riser's foot
label(4, "suction riser up from the vent chamber", (-RH, 1.12, 0.45))

# ---------------------------------------------------------------- the outlet (NE): end clamp, sight glass, nozzle
cyl((RH, YN + 0.2, ZH + 0.06), HR * 1.45, 0.1, "dark_steel", rot=(PI / 2, 0, 0), verts=32)
melt("mt_glass", "flow", scale=6.0, k=1, bright=1.5, axis="X",
     fn=lambda t: 0.35 + 0.65 * pulse(t, 0.25, 0.6, 0.12))
out_in = nozzle("N", length=0.3, mat="heat")
pipe([(RH, YN + 0.25, ZH + 0.06), (RH - 0.05, 1.08, ZH + 0.05), (0.5, 1.12, ZH)], r=0.1, mat="heat", flanges=False,
     name="hose end to the sight glass (melt)")
cyl((0.36, 1.13, ZH), 0.1, 0.26, "mt_glass", rot=(0, PI / 2, 0), verts=24, bevel=0)      # the sight glass
cyl((0.36, 1.13, ZH), 0.125, 0.26, "glass", rot=(0, PI / 2, 0), verts=24, bevel=0)
for xx in (0.22, 0.5):
    cyl((xx, 1.13, ZH), 0.15, 0.04, "dark_steel", rot=(0, PI / 2, 0), verts=24)
for i in range(4):
    a = 2 * PI * (i + 0.5) / 4
    cyl((0.36, 1.13 + 0.13 * math.cos(a), ZH + 0.13 * math.sin(a)), 0.012, 0.24, "bare", rot=(0, PI / 2, 0),
        verts=6, bevel=0)
pipe([(0.24, 1.13, ZH), (0.1, 1.15, ZH - 0.05), out_in], r=0.1, mat="heat", flanges=False,
     name="sight glass to the outlet (melt)")
box((0.36, 1.13, 0.2), (0.3, 0.2, 0.4), "iron_dk", bevel=0.01)
label(7, "sight glass: each slug lit as it passes", (0.36, 1.13, ZH + 0.1))
label(8, "molten kamacite out, north", (0, 1.38, ZA))

# ---------------------------------------------------------------- the helium: nozzle, meter, the pressure dome, the gas cap
in_in = nozzle("S", length=0.3, mat="bare")
valve(-0.12, -1.2, z=ZA - 0.1, h=0.36, r=0.055)
IN = [in_in, (-0.05, -1.2, ZA), (-0.14, -1.22, 0.58), (-0.2, -1.24, 0.72), (-0.25, -1.24, 0.74)]
he_line(IN, name="helium in: nozzle through the stop valve to the flow meter")
flow_meter((-0.36, -1.24, 0.74), (-1, 0, 0), r=0.1, turns=2, rate=RATE)
DX, DY = -0.9, -1.0                                                         # the pressure dome's vessel (SW)
foundation(-1.46, -1.46, -0.42, -0.62, 0.1)
cyl((DX, DY, 0.36), 0.36, 0.52, "he_edge", verts=48)
for zz in (0.2, 0.5):
    cyl((DX, DY, zz), 0.365, 0.05, "he_band", verts=48)
cyl((DX, DY, 0.64), 0.4, 0.06, "dark_steel", verts=48)
bolts(DX, DY, 0.68, 0.38, 16, r=0.016)
dome = head(DX, DY, 0.67, 0.33, 0.2, "rubber")                              # the diaphragm dome, flexing
breathe(dome, 0.35, lambda t: refill(t) - draw(t))
he_line([(-0.47, -1.24, 0.74), (-0.55, -1.2, 0.7), (-0.62, -1.12, 0.63)], name="helium: meter into the dome vessel")
he_gauge((DX + 0.22, DY - 0.33, 0.55), (0.3, -1, 0.3), r=0.08, live=lambda t: -0.2 + 0.9 * (refill(t) - draw(t)))
id_panel((DX - 0.15, DY - 0.37, 0.4), 0.2, 0.1, stripe="yellow")
# the gas-cap line: up from the dome vessel, over the hose, into the rotary union on the hub; the helium goes down
# the rotor's hollow shaft into the vent chamber under the pedestal
CAP = [(DX + 0.18, DY + 0.18, 0.66), (-0.72, -0.78, 1.1), (-0.42, -0.4, 1.3), (-0.12, -0.08, 1.22), (0, 0, ZF + 0.74)]
he_line(CAP, r=0.06, name="gas-cap line: dome vessel over the hose to the rotary union on the hub")
cyl((0, 0, ZF + 0.66), 0.075, 0.12, "he_edge", verts=24)                  # the rotary union (still; the hub turns under it)
cyl((0, 0, ZF + 0.62), 0.09, 0.03, "he_band", verts=24)
cyl((0, 0, ZF + 0.73), 0.05, 0.04, "bare", verts=16)
label(1, "helium-3 in, south: the grey-violet line through the stop valve and flow meter", (-0.15, -1.32, ZA))
label(2, "pressure dome: the gas cap's accumulator, sinking as the rollers draw", (DX, DY, 0.85))
label(3, "gas-cap line over the hose, down the rotor's hollow shaft: the helium presses the melt up", (-0.42, -0.4, 1.3))

# ---------------------------------------------------------------- the relief and the recovery receiver (E)
BL1 = [(0.82, -0.32, 0.3), (0.98, -0.38, 0.4), (1.06, -0.4, 0.46)]
he_line(BL1, r=0.04, bands=0.18, name="bleed: vent chamber to the relief valve")
tick_valve(1.12, -0.4, 0.46, bleed, axis=(1, 0, 0), mat="red")
BL2 = [(1.19, -0.38, 0.46), (1.26, -0.25, 0.55), (1.26, -0.05, 0.6)]
he_line(BL2, r=0.04, bands=0.18, name="bleed: relief valve into the recovery receiver")
foundation(1.04, -0.6, 1.5, 0.6, 0.1)
vtank(1.25, 0.15, 0.22, 0.95, mat="grey", bands=(0.4, 0.7), band_mat="he_edge", nozzle=None)
he_gauge((1.25, -0.08, 0.75), (0, -1, 0.2), r=0.06, live=lambda t: -0.3 + 0.7 * bleed(t))
label(10, "relief valve ticks: the excess helium to the recovery receiver", (1.12, -0.4, 0.62))

route("he", [(0, -1.5, ZA)] + IN + [(-0.36, -1.24, 0.74), (-0.55, -1.2, 0.7), (DX, DY, 0.5)] + CAP
      + [(RX, RY, 0.25)])
route("spent", [(RX + 0.4, RY - 0.15, 0.25)] + BL1 + [(1.12, -0.4, 0.46)] + BL2 + [(1.25, 0.15, 0.5)])
HOSE = [(-RH, YN + 0.2, ZH)] + [(RX + RH * math.cos(PI + PI * k / 12), RY + RH * math.sin(PI + PI * k / 12), ZH)
                               for k in range(13)] + [(RH, YN + 0.2, ZH)]
route("melt", [(RX, RY, 0.15)] + RISER + HOSE + [(RH - 0.05, 1.08, ZH + 0.05), (0.36, 1.13, ZH), (0.1, 1.15, ZH - 0.05),
                                                (0, 1.5, ZA)])

# ---------------------------------------------------------------- the drive (SE): motor, coupling, gearbox
foundation(0.6, -1.5, 1.5, -0.62, 0.12)
box((0.82, -0.82, 0.32), (0.42, 0.42, 0.42), "iron_dk", bevel=0.02)
cyl((0.82, -0.82, 0.56), 0.12, 0.06, "nickel", verts=24)
cyl((0.66, -0.66, 0.3), 0.07, 0.3, "bare", rot=(0, PI / 2, PI / 4), verts=16)
pv = motor(1.18, -1.15, 0.45, d=(-1, 0), s=0.85, mat="green")
coupling(0.92, -1.15, 0.45, 0.13, axis=(-1, 0, 0), turns=3)
cyl((0.85, -1.12, 0.45), 0.05, 0.14, "bare", rot=(0, PI / 2, 0), verts=12)       # the shaft into the gearbox
box((1.3, -0.82, 0.42), (0.26, 0.26, 0.42), "grey", bevel=0.015)
bundle([(1.3, -0.82, 0.62), (1.24, -0.98, 0.72), (1.18, -1.15, 0.64)], cols=("black", "red"), r=0.014,
       name="starter to the drive motor")
label(9, "the drive: motor and coupling into the gearbox", (1.1, -1.15, 0.65))

# ---------------------------------------------------------------- the corners
for k, (x, y) in enumerate(((-1.3, -0.5), (-1.08, -0.45))):
    cyl((x, y, 0.22), 0.1, 0.36, ("ochre", "oxide")[k], verts=20)
    torus((x, y, 0.34), 0.102, 0.01, "bare", seg=20)
foundation(-1.5, 0.6, -0.92, 1.5, 0.1)
box((-1.17, 1.01, 0.55), (0.46, 0.78, 0.9), "grey", bevel=0.025)
for k in range(3):
    box((-1.17, 0.615, 0.4 + 0.18 * k), (0.34, 0.02, 0.1), "dark_steel", bevel=0.003)
status_lens(-1.08, 0.72, 1.02)
box((-1.17, 1.16, 1.07), (0.3, 0.3, 0.14), "grey", bevel=0.01)
bundle([(-1.2, 0.75, 0.95), (-1.3, 0.55, 0.8), (-1.27, 0.35, 0.56)], cols=("black", "red", "grey"), r=0.016,
       name="control cabinet to the lube unit")
foundation(0.92, 0.6, 1.42, 1.42, 0.1)
cyl((1.2, 1.08, 0.35), 0.22, 0.42, "dark_steel", verts=32)
for k in range(3):
    torus((1.2, 1.08, 0.2 + 0.12 * k), 0.19, 0.06, "hose_k", seg=32)
cyl((1.33, 0.75, 0.9), 0.05, 1.6, "ochre", verts=12)
box((1.08, 0.75, 1.65), (0.6, 0.08, 0.08), "ochre", bevel=0.006)
cyl((0.83, 0.75, 1.5), 0.012, 0.25, "bare", verts=6)
box((0.83, 0.75, 1.36), (0.06, 0.06, 0.06), "yellow", bevel=0.005)
# W flank: the lube unit for the rotor's bearings
foundation(-1.5, -0.6, -1.04, 0.6, 0.1)
box((-1.27, 0.0, 0.32), (0.36, 0.9, 0.44), "green", bevel=0.02)
for k in range(3):
    cyl((-1.27, -0.3 + 0.3 * k, 0.6), 0.04, 0.12, "brass", verts=12)
hose([(-1.27, 0.3, 0.6), (-1.12, 0.35, 0.8), (-0.95, 0.3, ZF + 0.3)], r=0.022, mat="hose",
     name="lube to the rotor's track bearing")
hazard_tag((-1.27, -0.455, 0.35), 0.3, 0.06)
stain(0.6, -0.5, 0.25, 0.1)
stain(-0.4, -1.3, 0.2, 0.08)
run(dict(name="the peristaltic hose pump", footprint=[3, 3]), nf=NF)
