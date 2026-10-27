"""Vent Pump, round 2, concept 10: THE TWIN CYLINDER LIFT (3 x 3). Artist B.

  $BLENDER -b --python vpb_10_twin_cylinder_lift.py -- <out-dir> [--quick] [--only working|idle] [--colourmap]

The chain, vent to outlet: the melt rises from the vent collar into a bottom manifold and,
through a check valve, fills whichever of the two refractory cylinders is venting. The
switching valve chest on the south takes helium-3 in bare from the south nozzle and sends it
to the other cylinder's head: the helium presses on the melt and drives it up that
cylinder's dip tube, over the discharge header and down to the north nozzle. Half a loop
later the valves change over (the actuators on the heads stroke and their flags turn), and
the cylinders swap: one filling while the other empties. Each cylinder's armoured window
shows its level: rising as it fills, falling as it is pushed out.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpb_kit import *  # noqa: F401,F403,E402
import vpb_kit as K  # noqa: E402

K.build_materials(((0.45, 0.3), (1.2, 0.4), (1.95, 0.5)))
NF = 24
CY = 0.12                         # the cylinders' row
CXS = (-0.64, 0.64)               # west (A) and east (B)
CR = 0.43
ZB, ZH = 0.3, 1.95                # the shell's foot and shoulder
WZ0, WZ1 = 0.5, 1.75              # the window


def fill(t):
    """A cylinder's fill, 0..1: filling over the first half of the loop, pushed out over the
    second (eased, with a short dwell at the top and the bottom while the valves change over)."""
    t = t % 1.0
    if t < 0.5:
        return smooth((t - 0.04) / 0.42)
    return 1.0 - smooth((t - 0.54) / 0.42)


def admit(t, side):
    """1 while that cylinder's helium admit valve is open (it is being emptied)."""
    t = (t + (0.5 if side else 0.0)) % 1.0
    return ramp(t, 0.47, 0.53) - ramp(t, 0.97, 1.0) if t >= 0.47 else 0.0


# ---------------------------------------------------------------- the vent collar and the bottom manifold
vent_collar(0, CY, 0.36, h=0.22)
foundation(-1.12, CY - 0.5, 1.12, CY + 0.5, 0.2, "refractory")                  # the cylinders' footing
for cx in CXS:
    s = 1 if cx > 0 else -1
    lagged([(0.0, CY, 0.28), (s * 0.22, CY - 0.05, 0.3), (cx - s * CR * 0.6, CY - 0.1, 0.32)], r=0.1, bands=0.15)
    cyl((s * 0.28, CY - 0.06, 0.34), 0.12, 0.16, "iron_dk", rot=(0, PI / 2, 0), verts=24)   # the check valve
    cyl((s * 0.28, CY - 0.06, 0.48), 0.05, 0.14, "iron_dk", verts=12)
label(1, "the vent collar and the bottom manifold: melt to both cylinders", (0, CY - 0.3, 0.3))

# ---------------------------------------------------------------- the two refractory cylinders, their windows
melt_names = []
for side, cx in enumerate(CXS):
    nm = melt(f"mt_level{side}", "level", scale=3.0, k=1, bright=1.3, axis="Z", soft=True,
              level=(lambda sd: lambda t: WZ0 + (WZ1 - WZ0) * fill(t + 0.5 * sd))(side), idle_level=WZ0 - 1.0,
              fn=(lambda sd: lambda t: 0.75 + 0.25 * admit(t, sd))(side))
    melt_names.append(nm)
    cyl((cx, CY, ZB / 2 + 0.1), CR + 0.08, ZB, "iron_dk", verts=64)             # the skirt
    cyl((cx, CY, (ZB + ZH) / 2), CR, ZH - ZB, "refractory", verts=64)          # the lined shell
    head(cx, CY, ZH, CR, 0.2, "iron")
    for z in (0.45, 0.85, 1.25, 1.65):
        cyl((cx, CY, z), CR + 0.025, 0.06, "dark_steel", verts=64)              # the hoops
        rivet_ring(cx, CY, z, CR + 0.03, 20)
    cyl((cx, CY, ZH - 0.02), CR + 0.04, 0.07, "nickel", verts=64)
    bolts(cx, CY, ZH + 0.02, CR + 0.02, 18, r=0.016)
    # the window down the south face
    wy = CY - CR - 0.012
    box((cx, wy, (WZ0 + WZ1) / 2), (0.2, 0.03, WZ1 - WZ0), nm, bevel=0.002)
    box((cx, wy - 0.02, (WZ0 + WZ1) / 2), (0.2, 0.006, WZ1 - WZ0), "pane", bevel=0)
    for sx in (-1, 1):
        box((cx + sx * 0.125, wy - 0.02, (WZ0 + WZ1) / 2), (0.05, 0.05, WZ1 - WZ0 + 0.1), "dark_steel", bevel=0.006)
    for z in [WZ0 + (WZ1 - WZ0) * i / 3 for i in range(4)]:
        box((cx, wy - 0.035, z), (0.3, 0.03, 0.03), "dark_steel", bevel=0.004)
    stencil((cx + s * 0.0 + (0.28 if side else -0.28), CY - CR + 0.08, 1.05), (0.14, 0.012, 0.3))
    manway_top(cx - 0.15, CY + 0.12, ZH + 0.15, r=0.1)
label(2, "cylinder A (west): its window fills, then empties", (CXS[0], CY - CR, 1.1))
label(3, "cylinder B (east): half a loop behind", (CXS[1], CY - CR, 1.1))

# ---------------------------------------------------------------- the valve heads: actuators stroking, flags turning
def actuator(x, y, z, open_fn, flag="red"):
    """A pneumatic valve actuator: the valve body, its cylinder, a rod and cap that stroke up
    when it opens, and a position flag that turns a quarter as it does."""
    cyl((x, y, z + 0.06), 0.07, 0.12, "iron_dk", verts=20)
    cyl((x, y, z + 0.26), 0.06, 0.26, "yellow", verts=20)
    cyl((x, y, z + 0.4), 0.075, 0.03, "dark_steel", verts=20)
    rod = pivot((x, y, z + 0.4))
    cyl((0, 0, 0.05), 0.016, 0.12, "bare", verts=8, parent=rod)
    cyl((0, 0, 0.11), 0.045, 0.03, "dark_steel", verts=16, parent=rod)
    fl = pivot((0, 0, 0.13), parent=rod)
    box((0.06, 0, 0.0), (0.14, 0.03, 0.02), flag, bevel=0.003, parent=fl)
    slide(rod, (0, 0, 0.14), open_fn, idle=open_fn(0.0))         # idle: stopped as at frame 0
    base = fl.rotation_euler.copy()

    def pose_(t, on):
        fl.rotation_euler = base
        fl.rotation_euler.rotate_axis("Z", (PI / 2) * open_fn(t if on else 0.0))
    ANIM.append(pose_)


for side, cx in enumerate(CXS):
    s = 1 if cx > 0 else -1
    zt = ZH + 0.16
    box((cx, CY - 0.05, zt - 0.02), (0.5, 0.24, 0.06), "dark_steel", bevel=0.01)
    actuator(cx - s * 0.13, CY - 0.06, zt, (lambda sd: lambda t: admit(t, sd))(side), flag="red")
    actuator(cx + s * 0.13, CY - 0.06, zt, (lambda sd: lambda t: 1.0 - admit(t, sd))(side), flag="green")
label(4, "admit and vent valves: actuators stroke, flags turn", (CXS[0], CY - 0.06, ZH + 0.5))

# ---------------------------------------------------------------- the helium: south nozzle to the switching chest
in_in = nozzle("S", length=0.3, mat="bare")
foundation(-0.42, -1.18, 0.42, -0.5, 0.12)
box((0, -0.82, 0.42), (0.6, 0.46, 0.56), "grey", bevel=0.03)                    # the switching valve chest
box((0, -0.82, 0.72), (0.64, 0.5, 0.04), "dark_steel")
pipe([in_in, (0, -1.1, ZA)], r=0.07, mat="bare", flanges=False)
handwheel((0, -1.06, 0.62), r=0.08, axis=(0, 0, 1))
cyl((0, -1.06, 0.55), 0.02, 0.14, "bare", verts=8)
gauge((0.2, -1.06, 0.55), (0, -1, 0.3), r=0.05, live=lambda t: 0.3 * math.sin(4 * PI * t))
for side, cx in enumerate(CXS):
    s = 1 if cx > 0 else -1
    pipe([(s * 0.1, -0.75, 0.74), (s * 0.12, -0.45, 1.0), (s * 0.12, CY - 0.15, 1.6), (s * 0.15, CY - 0.1, ZH + 0.3),
          (cx - s * 0.13, CY - 0.06, ZH + 0.2)], r=0.035, mat="bare", flanges=False)
    pipe([(cx + s * 0.13, CY - 0.06, ZH + 0.2), (cx + s * 0.2, CY - 0.25, ZH + 0.25), (cx + s * 0.4, CY + 0.5, 2.0),
          (s * 1.0, 1.0, 1.25)], r=0.03, mat="bare", flanges=False)
label(5, "helium-3 in, south: bare metal", (0, -1.38, ZA))
label(6, "switching valve chest: helium to one head, then the other", (0, -0.82, 0.75))

# ---------------------------------------------------------------- the discharge: dip tubes, the header, the outlet
out_in = nozzle("N", length=0.34, mat="heat")
for side, cx in enumerate(CXS):
    s = 1 if cx > 0 else -1
    pipe([(cx + s * 0.05, CY + 0.12, ZH + 0.1), (cx + s * 0.02, CY + 0.2, ZH + 0.4), (s * 0.35, CY + 0.3, ZH + 0.45),
          (s * 0.12, 0.55, ZH + 0.35)], r=0.1, mat="heat")
cyl((0, 0.58, ZH + 0.3), 0.15, 0.3, "heat", rot=(0, PI / 2, 0), verts=32)      # the header's tee
cyl((0, 0.58, ZH + 0.3), 0.17, 0.05, "nickel", rot=(0, PI / 2, 0), verts=32)
lagged([(0, 0.62, ZH + 0.2), (0, 0.85, 1.6), (0, 1.0, 0.9), (0, 1.12, ZA + 0.02), out_in], r=0.12, bands=0.22)
box((0, 1.02, 0.28), (0.4, 0.3, 0.56), "iron_dk", bevel=0.02)
label(7, "dip tubes over the discharge header", (0, 0.58, ZH + 0.45))
label(8, "molten kamacite out, north", (0, 1.38, ZA))

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

# ---------------------------------------------------------------- the corners
# SW: the helium receiver
foundation(-1.5, -1.5, -0.45, -0.45, 0.1)
vtank(-0.98, -0.98, 0.4, 1.05, mat="grey", bands=(0.4, 0.8), nozzle=(0.0, 0.0))
pipe([(-0.6, -0.95, 0.35), (-0.4, -0.85, 0.4), (-0.3, -0.82, 0.42)], r=0.04, mat="bare", flanges=False)
gauge((-0.98, -1.39, 0.6), (0, -1, 0), r=0.06, live=lambda t: 0.2 * math.sin(2 * PI * t))
id_panel((-0.98, -1.385, 0.88), 0.26, 0.12, stripe="yellow")
# SE: the control cabinet and the pilot-air compressor for the actuators
foundation(0.45, -1.5, 1.5, -0.45, 0.1)
box((1.08, -1.1, 0.55), (0.7, 0.5, 0.9), "grey", bevel=0.025)
for k in range(3):
    box((0.85 + 0.22 * k, -1.36, 0.6), (0.14, 0.02, 0.5), "dark_steel", bevel=0.003)
status_lens(1.3, -1.0, 1.02)
box((0.95, -1.0, 1.06), (0.3, 0.3, 0.12), "grey", bevel=0.01)
drum_ew(0.55, 1.4, -0.65, 0.32, 0.18, mat="ochre", saddles=(0.7, 1.25))
pv = motor(0.75, -0.65, 0.62, d=(1, 0), s=0.6, mat="green")
coupling(pv[0] + 0.03, pv[1], pv[2], 0.06, axis=(1, 0, 0), turns=3)
cyl((1.12, -0.65, 0.62), 0.09, 0.2, "oxide", verts=16)
bundle([(1.08, -0.85, 1.0), (0.9, -0.45, 1.4), (CXS[1] + 0.15, CY - 0.2, ZH + 0.25)], cols=("black", "yellow", "grey"),
       r=0.016)
# NW: the drain pot and the level transmitters
foundation(-1.5, 0.55, -0.35, 1.5, 0.1)
vtank(-1.05, 1.0, 0.3, 0.8, mat="oxide", bands=(0.45,), nozzle=(0.0, 0.0))
box((-0.55, 1.1, 0.45), (0.3, 0.5, 0.7), "cream", bevel=0.02)
for k in range(2):
    gauge((-0.55, 0.84, 0.55 + 0.2 * k), (0, -1, 0.2), r=0.05)
lagged([(-1.05, 0.7, 0.3), (-0.95, 0.45, 0.28), (CXS[0], CY + 0.2, 0.3)], r=0.07, bands=0.18)
# NE: the helium vent receiver and its relief stack
foundation(0.35, 0.55, 1.5, 1.5, 0.1)
vtank(1.05, 1.02, 0.36, 1.0, mat="grey", bands=(0.5,), nozzle=(0.0, 0.0))
cyl((1.36, 1.32, 1.2), 0.04, 1.0, "bare", verts=12)
cone((1.36, 1.32, 1.75), 0.06, 0.04, 0.1, "dark_steel")
box((0.55, 1.15, 0.4), (0.32, 0.5, 0.6), "grey", bevel=0.02)
hose([(0.55, 0.9, 0.65), (0.4, 0.6, 0.9), (0.35, 0.4, 1.0)], r=0.03, mat="hose_k")
# W and E: the cylinders' flanks
for s in (-1, 1):
    foundation(min(s * 1.5, s * 1.12), -0.45, max(s * 1.5, s * 1.12), 0.55, 0.12)
    box((s * 1.3, 0.05, 0.42), (0.3, 0.7, 0.6), "dark_steel" if s < 0 else "green", bevel=0.02)
    cyl((s * 1.3, -0.15, 0.82), 0.08, 0.2, "brass", verts=16)
hazard_tag((-1.3, -0.31, 0.5), 0.25, 0.06)
stain(0.0, -0.3, 0.25, 0.1)
stain(-0.9, 0.3, 0.2, 0.1)
run(dict(name="the twin cylinder lift", footprint=[3, 3]), nf=NF)
