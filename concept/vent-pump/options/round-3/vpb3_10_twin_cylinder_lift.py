"""Vent Pump, round 3, concept 10: THE TWIN CYLINDER LIFT (3 x 3). Artist B.

  $BLENDER -b --python vpb3_10_twin_cylinder_lift.py -- <out-dir> [--quick] [--only working|idle] [--colourmap] [--check]

Round 2's lift (options/round-2/vpb_10_twin_cylinder_lift.py), the plumbing made honest and
the helium shown at work. What helium does: it is the piston -- let into the head of a full
cylinder, it presses on the melt and drives it up the dip tube and out, while the other
cylinder vents its spent helium and fills from the vent.

The chain: helium-3 in at the south nozzle, through the turning flow meter into the
switching valve chest; from the chest a grey-violet line climbs to each cylinder's admit
valve. Each half loop one admit valve kicks open (its rod strokes up, its red flag turns),
the meter races and that side's gauge on the chest swings up, and then that cylinder's
window empties as the melt surges out of it. Its vent valve (green flag) is shut meanwhile;
the other cylinder's is open, its spent helium going down the vent header to the recovery
receiver (north-east), on to the recovery compressor (south-east) and back into the chest.
The melt: up from the vent into the bottom manifold, through the check valves into the
cylinder that is filling, out up its dip tube when pushed, over the header and down the
lagged leg to the north nozzle.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpb3_kit import *  # noqa: F401,F403,E402
import vpb3_kit as K  # noqa: E402

K.build_materials(((0.45, 0.3), (1.2, 0.4), (1.95, 0.5)))
NF = 24
CY = 0.12
CXS = (-0.64, 0.64)
CR = 0.43
ZB, ZH = 0.3, 1.95
WZ0, WZ1 = 0.5, 1.75


def fill(t):
    t = t % 1.0
    if t < 0.5:
        return smooth((t - 0.04) / 0.42)
    return 1.0 - smooth((t - 0.54) / 0.42)


def admit(t, side):
    """1 while that cylinder's admit valve is open (it is being emptied)."""
    t = (t + (0.5 if side else 0.0)) % 1.0
    return ramp(t, 0.47, 0.53) - ramp(t, 0.97, 1.0) if t >= 0.47 else 0.0


def charge(t, side=None):
    """The rush of helium just after an admit valve opens (A at 0.5, B at 0)."""
    a = pulse(t, 0.5, 0.66, 0.04)
    b = pulse(t, 0.0, 0.16, 0.04)
    return {None: max(a, b), 0: a, 1: b}[side]


RATE = lambda t: 0.15 + charge(t)          # noqa: E731

# ---------------------------------------------------------------- the vent collar and the bottom manifold
vent_collar(0, CY, 0.36, h=0.22)
foundation(-1.12, CY - 0.5, 1.12, CY + 0.5, 0.2, "refractory")
FEED = {}
for cx in CXS:
    s = 1 if cx > 0 else -1
    FEED[s] = [(0.0, CY, 0.28), (s * 0.22, CY - 0.05, 0.3), (cx - s * CR * 0.6, CY - 0.1, 0.32)]
    lagged(FEED[s], r=0.1, bands=0.15, name=f"bottom manifold to cylinder {'B' if s > 0 else 'A'} (melt)")
    cyl((s * 0.28, CY - 0.06, 0.34), 0.12, 0.16, "iron_dk", rot=(0, PI / 2, 0), verts=24)
    cyl((s * 0.28, CY - 0.06, 0.48), 0.05, 0.14, "iron_dk", verts=12)
label(1, "the vent collar and the bottom manifold: melt into the cylinder that is filling", (0, CY - 0.3, 0.3))

# ---------------------------------------------------------------- the two refractory cylinders, their windows
for side, cx in enumerate(CXS):
    s = 1 if cx > 0 else -1
    nm = melt(f"mt_level{side}", "level", scale=3.0, k=1, bright=1.3, axis="Z", soft=True,
              level=(lambda sd: lambda t: WZ0 + (WZ1 - WZ0) * fill(t + 0.5 * sd))(side), idle_level=WZ0 - 1.0,
              fn=(lambda sd: lambda t: 0.75 + 0.25 * admit(t, sd))(side))
    cyl((cx, CY, ZB / 2 + 0.1), CR + 0.08, ZB, "iron_dk", verts=64)
    cyl((cx, CY, (ZB + ZH) / 2), CR, ZH - ZB, "refractory", verts=64)
    head(cx, CY, ZH, CR, 0.2, "iron")
    for z in (0.45, 0.85, 1.25, 1.65):
        cyl((cx, CY, z), CR + 0.025, 0.06, "dark_steel", verts=64)
        rivet_ring(cx, CY, z, CR + 0.03, 20)
    cyl((cx, CY, ZH - 0.02), CR + 0.04, 0.07, "nickel", verts=64)
    bolts(cx, CY, ZH + 0.02, CR + 0.02, 18, r=0.016)
    wy = CY - CR - 0.012
    box((cx, wy, (WZ0 + WZ1) / 2), (0.2, 0.03, WZ1 - WZ0), nm, bevel=0.002)
    box((cx, wy - 0.02, (WZ0 + WZ1) / 2), (0.2, 0.006, WZ1 - WZ0), "pane", bevel=0)
    for sx in (-1, 1):
        box((cx + sx * 0.125, wy - 0.02, (WZ0 + WZ1) / 2), (0.05, 0.05, WZ1 - WZ0 + 0.1), "dark_steel", bevel=0.006)
    for z in [WZ0 + (WZ1 - WZ0) * i / 3 for i in range(4)]:
        box((cx, wy - 0.035, z), (0.3, 0.03, 0.03), "dark_steel", bevel=0.004)
    stencil((cx + (0.28 if side else -0.28), CY - CR + 0.08, 1.05), (0.14, 0.012, 0.3))
    manway_top(cx + s * 0.05, CY + 0.2, ZH + 0.12, r=0.09)
label(5, "cylinder A (west): helium pushes its melt out, its window empties", (CXS[0], CY - CR, 1.1))
label(6, "cylinder B (east): half a loop behind", (CXS[1], CY - CR, 1.1))


def actuator(x, y, z, open_fn, flag="red"):
    cyl((x, y, z + 0.06), 0.07, 0.12, "iron_dk", verts=20)
    cyl((x, y, z + 0.26), 0.06, 0.26, "yellow", verts=20)
    cyl((x, y, z + 0.4), 0.075, 0.03, "dark_steel", verts=20)
    rod = pivot((x, y, z + 0.4))
    cyl((0, 0, 0.05), 0.016, 0.12, "bare", verts=8, parent=rod)
    cyl((0, 0, 0.11), 0.045, 0.03, "dark_steel", verts=16, parent=rod)
    fl = pivot((0, 0, 0.13), parent=rod)
    box((0.07, 0, 0.0), (0.16, 0.04, 0.025), flag, bevel=0.003, parent=fl)
    slide(rod, (0, 0, 0.14), open_fn, idle=open_fn(0.0))
    base = fl.rotation_euler.copy()

    def pose_(t, on):
        fl.rotation_euler = base
        fl.rotation_euler.rotate_axis("Z", (PI / 2) * open_fn(t if on else 0.0))
    ANIM.append(pose_)


ZT = ZH + 0.16
for side, cx in enumerate(CXS):
    s = 1 if cx > 0 else -1
    box((cx, CY - 0.05, ZT - 0.02), (0.5, 0.24, 0.06), "dark_steel", bevel=0.01)
    actuator(cx - s * 0.13, CY - 0.06, ZT, (lambda sd: lambda t: admit(t, sd))(side), flag="red")
    actuator(cx + s * 0.13, CY - 0.06, ZT, (lambda sd: lambda t: 1.0 - admit(t, sd))(side), flag="green")
label(4, "admit valve (red flag) kicks open, then the surge; vent valve (green) the opposite", (CXS[0], CY - 0.06,
                                                                                                 ZH + 0.5))

# ---------------------------------------------------------------- the helium in: nozzle, meter, the switching chest
in_in = nozzle("S", length=0.3, mat="bare")
foundation(-0.4, -1.4, 0.4, -0.42, 0.1)
he_line([in_in, (0, -1.13, ZA)], name="helium in: nozzle to the flow meter")
flow_meter((0, -1.0, ZA), (0, 1, 0), r=0.1, turns=2, rate=RATE)
box((0, -0.68, 0.42), (0.6, 0.46, 0.6), "he_edge", bevel=0.03)                # the switching valve chest
for zz in (0.26, 0.6):
    box((0, -0.68, zz), (0.61, 0.47, 0.04), "he_band", bevel=0.004)
box((0, -0.68, 0.74), (0.64, 0.5, 0.04), "dark_steel")
for side in (0, 1):
    s = 1 if side else -1
    he_gauge((s * 0.16, -0.92, 0.5), (0, -1, 0.35), r=0.08,
             live=(lambda sd: lambda t: -0.5 + 1.3 * max(charge(t, sd), 0.4 * admit(t, sd)))(side))
UP = {}
for side, cx in enumerate(CXS):
    s = 1 if cx > 0 else -1
    UP[s] = [(s * 0.15, -0.62, 0.74), (s * 0.24, -0.55, 1.2), (s * 0.24, -0.52, 2.1), (s * 0.3, -0.2, 2.3),
             (s * 0.42, CY - 0.06, 2.22), (s * 0.46, CY - 0.06, 2.18)]
    he_line(UP[s], r=0.05, bands=0.2, name=f"helium: chest up to cylinder {'B' if s > 0 else 'A'}'s admit valve")
label(2, "helium-3 in, south, through the flow meter: it races as each admit opens", (0, -1.2, ZA + 0.15))
label(3, "switching valve chest: helium to one head, then the other; a gauge each", (0, -0.68, 0.8))

# ---------------------------------------------------------------- the discharge: dip tubes, the header, the outlet
out_in = nozzle("N", length=0.34, mat="heat")
DIP = {}
for side, cx in enumerate(CXS):
    s = 1 if cx > 0 else -1
    DIP[s] = [(cx + s * 0.05, CY + 0.12, ZH + 0.1), (cx + s * 0.02, CY + 0.2, ZH + 0.4), (s * 0.35, CY + 0.3, ZH + 0.45),
              (s * 0.12, 0.55, ZH + 0.35)]
    pipe(DIP[s], r=0.1, mat="heat", name=f"dip tube {'B' if s > 0 else 'A'} to the header (melt)")
cyl((0, 0.58, ZH + 0.3), 0.15, 0.3, "heat", rot=(0, PI / 2, 0), verts=32)
cyl((0, 0.58, ZH + 0.3), 0.17, 0.05, "nickel", rot=(0, PI / 2, 0), verts=32)
LEG = [(0, 0.62, ZH + 0.2), (0, 0.85, 1.6), (0, 1.0, 0.9), (0, 1.12, ZA + 0.02), out_in]
lagged(LEG, r=0.12, bands=0.22, name="outlet leg (melt)")
box((0, 1.02, 0.28), (0.4, 0.3, 0.56), "iron_dk", bevel=0.02)
label(7, "dip tubes over the discharge header", (0, 0.58, ZH + 0.45))
label(8, "molten kamacite out, north", (0, 1.38, ZA))

# ---------------------------------------------------------------- spent helium: vent header, receiver, compressor, back
VENT_A = [(-0.82, CY - 0.06, 2.18), (-0.95, 0.3, 2.22), (-0.6, 0.92, 2.15), (0.5, 0.92, 2.15), (0.95, 0.95, 1.6),
          (1.0, 1.0, 1.08)]
VENT_B = [(0.82, CY - 0.06, 2.18), (0.98, 0.3, 2.2), (1.1, 0.7, 1.7), (1.1, 1.04, 1.08)]
he_line(VENT_A, r=0.045, bands=0.2, name="spent: cylinder A's vent valve to the recovery receiver")
he_line(VENT_B, r=0.045, bands=0.2, name="spent: cylinder B's vent valve to the recovery receiver")
foundation(0.6, 0.62, 1.42, 1.42, 0.1)
vtank(1.04, 1.02, 0.34, 1.0, mat="grey", bands=(0.5,), band_mat="he_edge", nozzle=None)
he_gauge((1.04, 0.66, 0.62), (0, -1, 0.2), r=0.07, live=lambda t: 0.5 * math.sin(4 * PI * t))
pipe([(1.2, 1.2, 1.05), (1.3, 1.3, 1.2), (1.33, 1.33, 1.6)], r=0.03, mat="bare", flanges=False,
     name="receiver's relief to the stack")
cyl((1.33, 1.33, 1.75), 0.04, 0.3, "bare", verts=12)
cone((1.33, 1.33, 1.95), 0.06, 0.04, 0.1, "dark_steel")
RET = [(1.3, 0.9, 0.4), (1.42, 0.5, 0.82), (1.42, -0.2, 0.82), (1.25, -0.5, 0.78), (1.12, -0.62, 0.72)]
he_line(RET, r=0.04, bands=0.2, name="spent: receiver back to the recovery compressor")
label(9, "spent helium down the vent header to the recovery receiver", (0.2, 0.92, 2.2))
label(10, "recovery compressor: the helium back into the chest", (0.95, -0.65, 0.75))
# SE: the recovery compressor on its receiver drum, the control cabinet
foundation(0.45, -1.4, 1.42, -0.45, 0.1)
box((1.08, -1.1, 0.55), (0.6, 0.5, 0.9), "grey", bevel=0.025)
for k in range(3):
    box((0.88 + 0.2 * k, -1.36, 0.6), (0.12, 0.02, 0.5), "dark_steel", bevel=0.003)
status_lens(1.28, -1.0, 1.02)
drum_ew(0.55, 1.36, -0.65, 0.32, 0.18, mat="ochre", saddles=(0.7, 1.22))
pv = motor(0.75, -0.65, 0.62, d=(1, 0), s=0.6, mat="green")
coupling(pv[0] + 0.03, pv[1], pv[2], 0.06, axis=(1, 0, 0), turns=3)
cyl((1.12, -0.65, 0.62), 0.09, 0.2, "oxide", verts=16)
cyl((1.12, -0.65, 0.73), 0.1, 0.03, "dark_steel", verts=16)
BACK = [(0.58, -0.7, 0.35), (0.42, -0.7, 0.42), (0.28, -0.7, 0.45)]
he_line(BACK, r=0.04, bands=0.2, name="recovered: compressor's drum into the switching chest")
bundle([(1.08, -0.85, 1.0), (0.9, -0.45, 1.4), (CXS[1] + 0.15, CY - 0.1, ZT + 0.06)], cols=("black", "yellow", "grey"),
       r=0.016, name="control cabinet to cylinder B's actuators")
bundle([(0.95, -0.9, 0.95), (0.6, -0.5, 1.5), (-0.2, -0.5, 2.3), (CXS[0] + 0.25, CY - 0.1, ZT + 0.0)],
       cols=("black", "yellow"), r=0.012, name="control cabinet to cylinder A's actuators")
bundle([(0.85, -0.95, 0.85), (0.75, -0.8, 0.8), (0.75, -0.65, 0.8)], cols=("black", "red"), r=0.012,
       name="control cabinet to the compressor motor")
# SW: the helium buffer receiver on the chest
foundation(-1.4, -1.4, -0.45, -0.45, 0.1)
vtank(-0.95, -0.95, 0.4, 1.05, mat="grey", bands=(0.4, 0.8), band_mat="he_edge", nozzle=None)
BUF = [(-0.6, -0.86, 0.35), (-0.42, -0.74, 0.42), (-0.28, -0.7, 0.42)]
he_line(BUF, r=0.045, bands=0.2, name="buffer receiver to the switching chest")
he_gauge((-0.95, -1.36, 0.6), (0, -1, 0.2), r=0.07, live=lambda t: -0.2 + 0.6 * charge(t))
id_panel((-0.95, -1.355, 0.88), 0.26, 0.12, stripe="yellow")

route("he", [(0, -1.5, ZA), (0, -1.0, ZA), (0, -0.68, 0.5)] + UP[-1])
route("he", [(0, -0.68, 0.5)] + UP[1])
route("spent", VENT_A + [(1.04, 1.02, 0.6)] + RET + [(1.0, -0.65, 0.4), (0.58, -0.7, 0.35)] + BACK[1:])
route("spent", VENT_B)
for s in (-1, 1):
    cx = s * 0.64
    route("melt", [(0, CY, 0.2)] + FEED[s] + [(cx, CY, 0.6), (cx, CY, 1.8)] + DIP[s] + [(0, 0.58, ZH + 0.3)])
route("melt", LEG[:-1] + [(0, 1.5, ZA)])

# ---------------------------------------------------------------- the catwalk between the heads
box((0, CY - 0.38, ZH - 0.05), (0.62, 0.3, 0.04), "dark_steel", bevel=0.004)
for k in range(8):
    box((-0.28 + 0.08 * k, CY - 0.38, ZH - 0.025), (0.02, 0.3, 0.01), "ochre", bevel=0)
for sy in (-1, 1):
    box((0, CY - 0.38 + sy * 0.15, ZH + 0.2), (0.62, 0.02, 0.02), "yellow", bevel=0)
for sx in (-1, 1):
    for sy in (-1, 1):
        box((sx * 0.3, CY - 0.38 + sy * 0.15, ZH + 0.08), (0.02, 0.02, 0.26), "yellow", bevel=0)
ladder(0, CY - 0.4, 0.25, ZH - 0.05, axis="x", mat="ochre")

# ---------------------------------------------------------------- NW: the drain pot and the level transmitters
foundation(-1.4, 0.55, -0.35, 1.4, 0.1)
vtank(-1.0, 1.0, 0.3, 0.8, mat="oxide", bands=(0.45,), nozzle=None)
box((-0.55, 1.1, 0.45), (0.3, 0.5, 0.7), "cream", bevel=0.02)
for k in range(2):
    gauge((-0.55, 0.84, 0.55 + 0.2 * k), (0, -1, 0.2), r=0.05)
DRAIN = [(-1.0, 0.72, 0.3), (-0.95, 0.45, 0.28), (CXS[0], CY + 0.2, 0.3)]
lagged(DRAIN, r=0.07, bands=0.18, name="cylinder A's drain to the drain pot")
bundle([(-0.55, 0.95, 0.75), (-0.6, 0.6, 1.1), (CXS[0] + 0.1, CY + 0.38, 1.2)], cols=("black", "grey"), r=0.012,
       name="level transmitters to cylinder A")
# W and E flanks
for s in (-1, 1):
    foundation(min(s * 1.45, s * 1.12), -0.45, max(s * 1.45, s * 1.12), 0.55, 0.12)
    box((s * 1.28, 0.05, 0.42), (0.28, 0.7, 0.6), "dark_steel" if s < 0 else "green", bevel=0.02)
hazard_tag((-1.28, -0.31, 0.5), 0.25, 0.06)
stain(0.0, -0.3, 0.25, 0.1)
stain(-0.9, 0.3, 0.2, 0.1)
run(dict(name="the twin cylinder lift", footprint=[3, 3]), nf=NF)
