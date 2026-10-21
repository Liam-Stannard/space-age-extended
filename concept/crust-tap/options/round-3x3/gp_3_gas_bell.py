"""Gas Pump 3x3, options round, take 3: THE GAS BELL (a gasholder over the vent).

  $BLENDER -b --python gp_3_gas_bell.py -- <out-dir> [--quick] [--frames N] [--only working|idle] [--helium]

The vent breathes straight up into a gasholder: a square bell floating in a water-sealed tank, guided in a frame of
four columns, balanced by counterweights on chains over sheaves. The bell rises as the vent fills it; a booster
blower, driven by a gas engine on a slip of the gas, draws it down and pushes the gas out. Square in plan (no nested
circles), the frame breaking the outline at the top.

The chain: the vent, under the bell (the gas rises straight in through the water seal); the bell; its outlet down
through the seal and out of the tank's south wall to the booster blower; the blower's discharge up the east side,
through the sight glass, along the north edge to the nozzle (at the connection's size from the blower: a reducer
at the nozzle). The fuel: a tan hose from the tank's seal pot through the regulator to the engine.

Motion: the bell rises over most of the loop and is drawn down at the end, slow up and quicker down; the two
counterweights move against it and their sheaves turn; the engine's flywheel and the blower's coupling turn; the
discharge gauge kicks while the bell is drawn; the gas drifts in the sight glass. Idle: all stop where they are, the
glass empty.
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

K5.build_materials5(((0.5, 0.25), (1.2, 0.4)))
NF = 24
TY = -0.06                    # the tank's (and the bell's) middle
TX0, TX1, TY0, TY1 = -0.84, 0.84, TY - 0.68, TY + 0.68
TH = 0.42                     # the tank wall
BX, BYH = 0.7, 0.56           # the bell's half sizes
B0 = 1.02                     # the bell's top at its lowest
LIFT = 0.5                    # how far it rises
UP = 0.68                     # the share of the loop it rises in


def fill(t):
    """The bell's height, 0..1: up slowly as the vent fills it, drawn down quickly at the loop's end."""
    t %= 1.0
    if t < UP:
        return smooth(t / UP)
    return 1.0 - smooth((t - UP) / (1.0 - UP))


def drawing(t):
    t %= 1.0
    return 1.0 if t >= UP else 0.0


def fz(t, on):
    return LIFT * fill(t if on else 0.0)


# ---------------------------------------------------------------- footings
foundation(TX0 - 0.1, TY0 - 0.1, TX1 + 0.1, TY1 + 0.1, 0.1, "refractory")            # the tank's ring footing
foundation(-1.46, -1.44, 1.44, TY0 - 0.14, 0.1)                                          # the blower and engine
foundation(TX1 + 0.14, TY0 - 0.1, 1.46, 1.44, 0.08)                                      # the east run
foundation(-1.46, TY0 - 0.1, TX0 - 0.14, 1.4, 0.08)                                      # the west side
foundation(-0.6, TY1 + 0.14, TX1 + 0.1, 1.46, 0.08, anchors=False)                       # the north run

# ---------------------------------------------------------------- the tank and its water seal
for (cx, cy, sx, sy) in (((TX0 + TX1) / 2, TY0, TX1 - TX0, 0.06), ((TX0 + TX1) / 2, TY1, TX1 - TX0, 0.06),
                         (TX0, TY, 0.06, TY1 - TY0), (TX1, TY, 0.06, TY1 - TY0)):
    box((cx, cy, 0.1 + TH / 2), (sx, sy, TH), "iron", bevel=0.01)
for x in (TX0 + 0.28 * k for k in range(1, 6)):                                      # the stiffeners
    box((x, TY0 - 0.04, 0.1 + TH / 2), (0.04, 0.03, TH), "dark_steel", bevel=0.004)
for y in (TY0 + 0.27 * k for k in range(1, 5)):
    for x in (TX0 - 0.04, TX1 + 0.04):
        box((x, y, 0.1 + TH / 2), (0.03, 0.04, TH), "dark_steel", bevel=0.004)
for x, y in ((TX0, TY0), (TX1, TY0), (TX0, TY1), (TX1, TY1)):
    box((x, y, 0.1 + TH / 2), (0.1, 0.1, TH + 0.02), "dark_steel", bevel=0.008)
box((0, TY0 - 0.035, 0.1 + TH - 0.03), (TX1 - TX0, 0.02, 0.05), "dark_steel")                # the rim angle
box((0, TY, 0.1 + TH - 0.04), (TX1 - TX0 - 0.06, TY1 - TY0 - 0.06, 0.02), "slag", bevel=0)  # the water
stencil((-0.45, TY0 - 0.035, 0.32), (0.3, 0.012, 0.1))
hazard_tag((0.45, TY0 - 0.04, 0.22), 0.4, 0.06)
label(1, "vent under the bell: the gas rises straight in through the water seal", (-0.2, TY0, 0.45))

# ---------------------------------------------------------------- the bell
bell = pivot((0, TY, 0))
H = B0 - 0.28
box((0, 0, 0.28 + H / 2), (2 * BX, 2 * BYH, H), "cream", bevel=0.02, parent=bell)
for z in (0.62, 0.86):
    box((0, 0, z), (2 * BX + 0.03, 2 * BYH + 0.03, 0.035), "dark_steel", bevel=0.004, parent=bell)
for x in (-0.45, 0.0, 0.45):
    box((x, -BYH - 0.012, 0.28 + H / 2), (0.03, 0.02, H), "dark_steel", bevel=0.003, parent=bell)
box((0, 0, B0 + 0.025), (2 * BX + 0.02, 2 * BYH + 0.02, 0.05), "dark_steel", bevel=0.01, parent=bell)  # the crown
box((0, 0, B0 + 0.06), (2 * BX - 0.1, 2 * BYH - 0.1, 0.04), "cream", bevel=0.02, parent=bell)  # the crown's raised plate
for y in (-0.28, 0.28):
    box((0, y, B0 + 0.1), (2 * BX - 0.06, 0.05, 0.05), "dark_steel", bevel=0.004, parent=bell)    # the crown girders
cyl((0.3, -0.05, B0 + 0.1), 0.11, 0.06, "bare", verts=24, parent=bell)                        # the crown manway
for k in range(8):
    a = 2 * PI * k / 8
    cyl((0.3 + 0.085 * math.cos(a), -0.05 + 0.085 * math.sin(a), B0 + 0.14), 0.01, 0.02, "bolt", verts=6, bevel=0,
        parent=bell)
cyl((-0.3, 0.12, B0 + 0.14), 0.05, 0.16, "bare", verts=12, parent=bell)                      # the crown relief valve
cyl((-0.3, 0.12, B0 + 0.24), 0.09, 0.05, "red", verts=16, parent=bell)
box((-0.32, -BYH - 0.012, 0.74), (0.4, 0.012, 0.09), "stencil", bevel=0.002, parent=bell)
for k in range(3):                                                                           # the crown's handrail
    x = -0.55 + 0.55 * k
    cyl((x, -BYH + 0.08, B0 + 0.2), 0.012, 0.22, "yellow", verts=8, bevel=0, parent=bell)
box((0, -BYH + 0.08, B0 + 0.31), (1.14, 0.02, 0.02), "yellow", bevel=0, parent=bell)
for x in (-0.5, 0.0, 0.5):                                                                   # the crown's plate seams
    box((x, 0, B0 + 0.082), (0.012, 2 * BYH - 0.12, 0.006), "seam", bevel=0, parent=bell)
box((0.38, 0.3, B0 + 0.14), (0.18, 0.14, 0.12), "grey", bevel=0.01, parent=bell)           # the level transmitter
for sx in (-1, 1):                                                                           # the guide rollers
    for sy in (-1, 1):
        box((sx * (BX + 0.09), sy * (BYH - 0.02) - 0.045 * sy, B0 - 0.04), (0.2, 0.03, 0.05), "dark_steel",
            bevel=0.004, parent=bell)
        cyl((sx * (BX + 0.205), sy * (BYH - 0.02), B0 - 0.04), 0.045, 0.03, "nickel", rot=(PI / 2, 0, 0), verts=16,
            parent=bell)
K.ANIM.append(lambda t, on: setattr(bell, "location", Vector((0, TY, fz(t, on)))))
label(2, "the bell rises as the vent fills it, drawn down at the end of the loop", (0, TY - 0.3, B0 + 0.2))

# ---------------------------------------------------------------- the guide frame, the counterweights
CXF, CY0, CY1, FZ = 0.98, TY0 - 0.14, TY1 + 0.08, 2.3
for x in (-CXF, CXF):
    for y in (CY0, CY1):
        box((x, y, FZ / 2 + 0.05), (0.08, 0.08, FZ), "iron_dk", bevel=0.006)
        cyl((x, y, 0.13), 0.08, 0.06, "dark_steel", verts=6)
    box((x, (CY0 + CY1) / 2, FZ), (0.07, CY1 - CY0 + 0.08, 0.08), "iron_dk", bevel=0.006)
    for z0, z1 in ((0.2, 1.05), (1.05, FZ - 0.05)):
        xb = x * 1.06                                                                       # outboard of the rails
        link(lambda t, on, xb=xb, z0=z0: (xb, CY0, z0), lambda t, on, xb=xb, z1=z1: (xb, CY1, z1), r=0.018, mat="iron_dk",
             name="frame brace")
for y in (CY0, CY1):
    box((0, y, FZ), (2 * CXF + 0.08, 0.07, 0.08), "iron_dk", bevel=0.006)
for x in (-CXF + 0.015, CXF - 0.015):                                                        # the guide rails the rollers run on
    for y in (TY - BYH + 0.02, TY + BYH - 0.02):
        box((x, y, (0.52 + FZ) / 2), (0.03, 0.04, FZ - 0.52), "nickel", bevel=0.003)
        box((x * 1.03, y, FZ - 0.02), (0.06, 0.04, 0.05), "dark_steel", bevel=0.003)
hazard_tag((0, CY0 - 0.04, FZ), 0.6, 0.05)
SY_ = 0.12                     # the chains' line
SR = 0.16                      # the sheaves' radius
for s in (-1, 1):
    sx = s * CXF
    box((sx, SY_, FZ + 0.06), (0.1, 0.12, 0.06), "dark_steel")
    for cy_ in (SY_ - 0.13, SY_ - 0.01):                                                   # the sheave's cheeks
        box((sx, cy_, FZ + 0.2), (0.09, 0.015, 0.26), "dark_steel", bevel=0.003)
    sh = pivot((sx, SY_ - 0.07, FZ + 0.27), along((0, -1, 0)))
    torus((0, 0, 0), SR, 0.025, "dark_steel", seg=32, parent=sh)
    cyl((0, 0, 0), 0.03, 0.05, "bare", verts=12, parent=sh)
    for k in range(4):
        a = PI * k / 4
        box((0, 0, 0), (2 * SR, 0.02, 0.02), "oxide", rz=a, bevel=0, parent=sh)
    base = sh.rotation_euler.copy()

    def _sh(t, on, sh=sh, base=base, s=s):
        sh.rotation_euler = base
        sh.rotation_euler.rotate_axis("Z", s * fz(t, on) / SR)
    K.ANIM.append(_sh)
    # the chain: the bell's crown corner up to the sheave's inner side; down its outer side to the weight
    link(lambda t, on, s=s: (s * (BX - 0.06), SY_ - 0.07, B0 + 0.05 + fz(t, on)),
         lambda t, on, s=s: (s * (CXF - SR), SY_ - 0.07, FZ + 0.27), r=0.016, mat="dark", name="chain")
    WX = s * (CXF + SR)

    def wz(t, on):
        return 1.62 - fz(t, on)
    link(lambda t, on, WX=WX: (WX, SY_ - 0.07, FZ + 0.27), lambda t, on, WX=WX: (WX, SY_ - 0.07, wz(t, on)),
         r=0.016, mat="dark", name="chain")
    cw = pivot((WX, SY_ - 0.07, 1.62))
    for k in range(3):
        box((0, 0, -0.08 - 0.13 * k), (0.16, 0.2, 0.11), "dark_steel" if k % 2 else "oxide", bevel=0.012, parent=cw)
    box((0, 0, -0.02), (0.06, 0.04, 0.04), "bare", parent=cw)
    K.ANIM.append(lambda t, on, cw=cw, WX=WX: setattr(cw, "location", Vector((WX, SY_ - 0.07, wz(t, on)))))
label(3, "counterweights on chains over the sheaves, moving against the bell", (CXF + SR, SY_, 1.1))

# ---------------------------------------------------------------- the outlet: the tank's south wall to the blower
OZ = 0.34
cyl((0.45, TY0 - 0.08, OZ), 0.12, 0.1, "dark_steel", rot=(PI / 2, 0, 0), verts=24)
pipe([(0.45, TY0 - 0.1, OZ), (0.45, -0.9, OZ), (0.45, -0.98, OZ)], r=0.11, mat="iron",
     name="outlet: the bell through the seal to the blower")
BLX, BLY = 0.45, -1.16
box((BLX, BLY, 0.38), (0.5, 0.36, 0.52), "oxide", bevel=0.03)                                 # the booster blower
for xx in (BLX - 0.27, BLX + 0.27):
    box((xx, BLY, 0.38), (0.05, 0.4, 0.56), "dark_steel", bevel=0.01)
for k in range(4):
    box((BLX - 0.18 + 0.12 * k, BLY - 0.19, 0.4), (0.05, 0.02, 0.4), "dark_steel", bevel=0.003)
cyl((BLX, BLY, 0.68), 0.12, 0.06, "dark_steel", verts=20)
gauge((BLX + 0.12, BLY - 0.2, 0.62), (0, -1, 0.4), r=0.075, needle=0.02, live=lambda t: -0.3 + 1.0 * drawing(t))
hazard_tag((BLX, BLY - 0.185, 0.18), 0.4, 0.05)
label(4, "booster blower: draws the bell down and pushes the gas on", (BLX, BLY - 0.1, 0.7))

# ---------------------------------------------------------------- the gas engine (SW) driving the blower
EX, EY, EZ = -0.78, -1.08, 0.46
box((EX, EY, 0.4), (0.56, 0.5, 0.6), "green", bevel=0.03)
box((EX, EY, 0.72), (0.6, 0.54, 0.05), "dark_steel")
cyl((EX - 0.05, EY, 0.92), 0.13, 0.36, "green", verts=32)
for k in range(4):
    torus((EX - 0.05, EY, 0.8 + 0.07 * k), 0.135, 0.011, "dark_steel", seg=32)
cyl((EX - 0.05, EY, 1.12), 0.15, 0.06, "dark_steel", verts=32)
cyl((EX + 0.1, EY, 1.16), 0.018, 0.08, "nickel", verts=8)
cyl((EX - 0.22, EY + 0.12, 1.0), 0.035, 0.5, "bare", verts=12)                                 # the exhaust
cyl((EX - 0.22, EY + 0.12, 1.27), 0.065, 0.06, "dark_steel", verts=16)
fw = pivot((EX, -1.44, EZ), along((0, -1, 0)))
torus((0, 0, 0), 0.3, 0.045, "dark_steel", seg=48, parent=fw)
cyl((0, 0, 0), 0.06, 0.08, "bare", verts=16, parent=fw)
for k in range(5):
    a = 2 * PI * k / 5
    box((0.15 * math.cos(a), 0.15 * math.sin(a), 0), (0.25, 0.04, 0.03), "green", rz=a, bevel=0.004, parent=fw)
box((0.0, 0.26, 0.0), (0.12, 0.08, 0.05), "red", bevel=0.006, parent=fw)
spin(fw, 2)
cyl((EX, -1.36, EZ), 0.035, 0.16, "bare", rot=(PI / 2, 0, 0), verts=12)
cyl((-0.15, EY, 0.4), 0.035, 0.7, "bare", rot=(0, PI / 2, 0), verts=12)                         # the drive shaft
coupling(-0.05, EY, 0.4, 0.07, axis=(1, 0, 0), turns=2)
coupling(BLX - 0.36, EY, 0.4, 0.06, axis=(1, 0, 0), turns=2)
label(5, "gas engine on a slip of the gas: flywheel and couplings turning", (EX, -1.3, 0.8))
# its fuel: the tank's seal pot -> regulator -> mixer
cyl((-0.16, TY0 - 0.12, 0.3), 0.08, 0.36, "dark_steel", verts=20)                                # the seal pot
handwheel((-0.16, TY0 - 0.12, 0.52), 0.07, mat="red")
box((-0.4, -0.86, 0.32), (0.06, 0.06, 0.48), "dark_steel", bevel=0.004)                           # the regulator's post
hose([(-0.23, TY0 - 0.16, 0.3), (-0.32, -0.95, 0.42), (-0.4, -0.88, 0.6)], r=0.035, mat="hose",
     name="fuel hose: the seal pot to the regulator")
cyl((-0.4, -0.86, 0.64), 0.07, 0.14, "yellow", verts=20)                                        # the regulator
head(-0.4, -0.86, 0.71, 0.07, 0.06, "yellow")
pipe([(-0.44, -0.86, 0.62), (-0.48, -0.92, 0.64), (-0.53, -1.0, 0.62)], r=0.025, mat="bare",
     name="fuel: the regulator to the mixer")
label(6, "fuel: a tan hose from the seal pot through the regulator", (-0.36, -0.92, 0.6))

# ---------------------------------------------------------------- the discharge: up the east side, the sight glass, the north run
RO = 0.12
pipe([(BLX + 0.27, BLY, 0.42), (1.0, BLY, 0.42), (1.24, -0.98, ZA), (1.24, -0.72, ZA)], r=RO, mat="bare",
     name="discharge: the blower to the sight glass")
# (the discharge in bare steel, as vanilla's pipes)
g0, g1, _ = gas_window((1.24, -0.66, ZA), (1.24, -0.14, ZA), r=0.11, k=2)
pipe([(1.24, -0.08, ZA), (1.24, 0.6, ZA), (1.2, 0.96, ZA), (1.0, 1.1, ZA), (0.5, 1.12, ZA), (0.14, 1.12, ZA)],
     r=RO, mat="bare", name="discharge: the sight glass along the north edge")
noz = nozzle("N", length=0.24, mat="bare")
reducer((0.14, 1.12, ZA), (0.0, 1.12, ZA), RO, RO)
for y_ in (-0.5, 0.25, 0.8):
    box((1.24, y_, (ZA - RO) / 2 + 0.05), (0.14, 0.1, ZA - RO), "dark_steel")
cyl((0.0, 1.12, ZA), 0.15, 0.2, "dark_steel", verts=24)                                         # the elbow box
cyl((0.0, 1.12, ZA + 0.2), 0.05, 0.2, "bare", verts=12)
cyl((0.0, 1.12, ZA + 0.33), 0.09, 0.05, "red", verts=16)
label(7, "sight glass on the discharge up the east side", (1.24, -0.4, 0.6))
label(8, "gas out, north, along the north edge to the nozzle", (0.5, 1.12, ZA))

# ---------------------------------------------------------------- the west side: the water make-up, the control cabinet
vtank(-1.18, -0.38, 0.2, 0.7, mat="ochre", bands=(0.35,), nozzle=None)
pipe([(-1.0, -0.38, 0.3), (TX0 - 0.03, -0.38, 0.4)], r=0.03, mat="bare", name="water make-up to the tank")
cabinet(-1.1, 1.08, 0.56, 0.48, 0.8, mat="grey")
status_lens(-0.94, 0.9, 0.84)
for k, xx in enumerate((-0.62, -0.34)):
    vtank(xx, 1.22, 0.13, 0.5 + 0.06 * k, mat=("oxide", "green")[k], bands=(0.25,), nozzle=None)      # spare bottles
jbox(0.42, 0.8, w=0.3, d=0.2, h=0.34, mat="grey", z=0.08)
bundle([(0.5, 0.8, 0.4), (0.75, 0.85, 0.5), (0.88, 0.5, 0.7), (CXF + 0.03, 0.3, 0.9)], cols=("black", "grey"), r=0.013,
       name="junction box to the frame's limit switches")
box((CXF + 0.06, 0.3, 0.9), (0.06, 0.1, 0.12), "yellow", bevel=0.006)                         # a limit switch
bundle([(-1.16, 0.84, 0.4), (-1.42, 0.4, 0.25), (-1.43, -0.6, 0.28), (-1.2, -0.95, 0.5), (-1.06, -0.95, 0.55)], cols=("black", "red"),
       r=0.015, name="cabinet to the engine's ignition")
ladder(-CXF - 0.1, 0.4, 0.15, FZ, axis="y", mat="ochre")
stain(0.8, -1.3, 0.2, 0.08)
stain(-1.2, 0.3, 0.18, 0.08)

route("gas", [(0, TY, 0.2), (0, TY, 0.6), (0.3, TY - 0.2, 0.5), (0.45, TY0, OZ), (0.45, -0.98, OZ), (BLX, BLY, 0.42),
              (1.0, BLY, 0.42), (1.24, -0.98, ZA), (1.24, -0.66, ZA), (1.24, -0.14, ZA), (1.24, 0.6, ZA),
              (1.2, 0.96, ZA), (1.0, 1.1, ZA), (0.5, 1.12, ZA), (0.0, 1.12, ZA), (0, 1.5, ZA)])
route("fuel", [(-0.23, TY0 - 0.16, 0.3), (-0.32, -0.95, 0.42), (-0.4, -0.86, 0.64), (-0.48, -0.92, 0.64),
               (-0.53, -1.0, 0.62)])
run_gp(dict(name="the gas bell", footprint=[3, 3], take=3), nf=NF)
