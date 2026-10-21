"""Gas Pump 3x3, refine (T04): take 2, THE FLYWHEEL COMPRESSOR, from ../round-3x3/gp_2_flywheel_compressor.py (baf235d).

Liam's notes (T03, 2026-10-21): "Whole machine turns"; helium-3 "Violet, like the Vent Pump" (gp_kit.py);
"Keep the gas engine"; motion (3.7 % moving at 1x): "Iterate on the current design to improve this".
Changed here, the motion only, the design kept (every change marked T04 below):
  flywheel     the six spokes cast into a web in the same green, standing only a little proud of it (no open
               gaps: the spokes no longer flick dark/light past a pixel six times a turn, take 2's strobe), and a
               big yellow balance weight bolted between two spokes in place of take 2's small red lug: one bold
               mark a turn, so the turn reads at 1x and a pixel sees it pass once a loop;
  crossheads   bare steel on an oil-dark guide floor (was green), the stroke 0.13 -> 0.15 either side (mid
               0.52 -> 0.54 out, clear of the crankcase's rod bore), a yellow slipper on each crosshead's top,
               so the slide reads against its frame;
  rockers      the power cylinders' rockers nod 0.28 -> 0.40 rad;
  cable marks  the ignition bundle's markers cream, not the label paint (they rolled to white px).
Its own first line follows.

Gas Pump 3x3, options round, take 2: THE FLYWHEEL COMPRESSOR (the 2x2 Gas Pump's crank and flywheel, grown).

  $BLENDER -b --python gp_2_flywheel_compressor.py -- <out-dir> [--quick] [--frames N] [--only working|idle] [--helium]

The 2x2 Gas Pump's idea -- a flywheel and crank driving a compressor, a gauge kicking, gas in a sight glass, its
green casing -- grown into an oilfield integral engine-compressor: one crankcase carrying two upright power
cylinders (burning a slip of the vent's gas) and two horizontal compressor cylinders, opposed, their rods and
crossheads seen sliding in open distance pieces; a big spoked flywheel on the crankshaft's south end. The vent is
under a tall suction scrubber.

The chain: the vent, the wellhead, the suction scrubber (the liquid knocked out), the suction lines over the top
to both compressor cylinders, their discharges up each side, the east one through the sight glass, into the
discharge bottle along the north face, out of the bottle's north side at the connection's size to the nozzle (no
step: the bottle's stub is the nozzle's bore). The fuel: a tan hose from the scrubber's head through the
regulator to the power cylinders' gas rail.

Motion: the flywheel one turn a loop; both crossheads and rods out and back once (opposed: they move apart and
together); the power cylinders' rocker arms nod; the gauge board's three needles kick on the strokes; the gas
drifts in the sight glass. Idle: all stop where they are, the glass empty.
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

K5.build_materials5(((0.45, 0.3), (1.5, 0.4)))
NF = 24
CY = -0.76                 # the compressor line (E-W) and the crankcase's middle
CZ = 0.58                  # the compressor cylinders' axis
STROKE = 0.15              # each crosshead's travel either side of mid (T04: was 0.13)


def xh(t, on):
    """A crosshead's offset outward from mid: the crank one turn a loop."""
    return STROKE * math.cos(2 * PI * (t if on else 0.0))


def delivery(t):
    """1 while the cylinders deliver (the crossheads moving out), eased."""
    return max(0.0, math.sin(2 * PI * t)) ** 0.7


# ---------------------------------------------------------------- footings
foundation(-0.5, -1.46, 0.5, -0.2, 0.14)                           # the crankcase and flywheel
foundation(-1.46, -1.1, -0.52, -0.38, 0.12)                        # west compressor cylinder
foundation(0.52, -1.1, 1.46, -0.38, 0.12)                          # east compressor cylinder
foundation(-0.42, -0.18, 0.42, 0.6, 0.22, "refractory")            # the wellhead and scrubber over the vent
vent_collar(0, 0.12, 0.28, h=0.3)
foundation(-1.42, 0.68, 0.62, 1.42, 0.1)                           # the discharge bottle
foundation(-1.44, -0.34, -0.48, 0.62, 0.08)                        # the gauge board
foundation(0.48, -0.34, 1.44, 0.62, 0.08)                          # the sight glass run
foundation(0.68, 0.68, 1.42, 1.42, 0.1)                            # the lube tank and the panel

# ---------------------------------------------------------------- 1-2. the wellhead, the suction scrubber
SX, SY = 0.0, 0.16
cyl((SX, SY, 0.36), 0.2, 0.16, "dark_steel", verts=32)
flange_ring(SX, SY, 0.28, 0.2, nb=10)
top = vtank(SX, SY, 0.32, 1.42, mat="green", bands=(0.62, 1.12), nozzle=None)
for z in (0.62, 1.12):
    rivet_ring(SX, SY, z, 0.355, 14)
manway_top(SX, SY, top - 0.02, r=0.1)
cyl((SX, SY - 0.33, 0.46), 0.05, 0.1, "bare", rot=(PI / 2, 0, 0), verts=12)            # the dump valve
handwheel((SX, SY - 0.42, 0.46), 0.07, axis=(0, -1, 0.2), mat="red")
cyl((0.32, -0.22, 0.12), 0.07, 0.2, "dark_steel", verts=16)                                   # the drain pot
hose([(SX, SY - 0.37, 0.4), (0.2, -0.22, 0.24), (0.32, -0.22, 0.2)], r=0.035, mat="hose_k",
     name="scrubber dump to the drain")
stencil((SX - 0.12, SY - 0.33, 0.95), (0.18, 0.012, 0.1))
id_panel((SX + 0.12, SY - 0.325, 0.78), 0.14, 0.09, stripe="yellow")
label(1, "vent under the wellhead", (SX, SY - 0.3, 0.32))
label(2, "suction scrubber over the vent: the liquid knocked out", (SX, SY - 0.2, 1.1))

# ---------------------------------------------------------------- the crankcase, the power cylinders, the flywheel
box((0, CY, 0.44), (0.62, 0.86, 0.6), "green", bevel=0.035)
box((0, CY, 0.76), (0.66, 0.9, 0.05), "dark_steel")
for yy in (CY - 0.2, CY + 0.2):
    cyl((0, yy, 1.0), 0.15, 0.44, "green", verts=32)
    for k in range(4):
        torus((0, yy, 0.86 + 0.08 * k), 0.155, 0.012, "dark_steel", seg=32)
    cyl((0, yy, 1.25), 0.17, 0.07, "dark_steel", verts=32)
    bolts(0, yy, 1.29, 0.14, 8, r=0.012)
    box((0, yy, 1.33), (0.1, 0.22, 0.06), "dark_steel", bevel=0.006)                   # the rocker stand
    rk = pivot((0, yy, 1.45))
    box((0, 0, 0), (0.05, 0.3, 0.04), "ochre", bevel=0.005, parent=rk)
    sphere((0, 0.15, 0), 0.025, "bare", parent=rk)
    sphere((0, -0.15, 0), 0.025, "bare", parent=rk)
    rock(rk, 0.40, cycles=1, axis="X", phase=0.0 if yy < CY else 0.5)
    cyl((0.12, yy, 1.12), 0.018, 0.12, "nickel", rot=(0, PI / 2, 0), verts=8)          # the spark plug
box((0.0, CY - 0.44, 0.45), (0.5, 0.03, 0.4), "dark_steel", bevel=0.006)              # the crankcase door
bolts(0, CY - 0.46, 0.45, 0.0, 1)
fy = -1.28
cyl((0, fy + 0.12, CZ + 0.1), 0.05, 0.36, "bare", rot=(PI / 2, 0, 0), verts=16)       # the crankshaft's end
fw = pivot((0, fy, CZ + 0.1), along((0, -1, 0)))
torus((0, 0, 0), 0.44, 0.06, "dark_steel", seg=56, parent=fw)
cyl((0, 0, 0), 0.08, 0.1, "bare", verts=20, parent=fw)
FW_WEB = os.environ.get("GP_FW_WEB", "green")                # T04 trial knob: the web and spokes' paint
FW_WEIGHT = os.environ.get("GP_FW_WEIGHT", "yellow")        # T04 trial knob: the balance weight's paint
cyl((0, 0, -0.012), 0.405, 0.02, FW_WEB, verts=56, bevel=0.003, parent=fw)       # T04: the web the spokes are cast in
for k in range(6):
    a = 2 * PI * k / 6
    box((0.22 * math.cos(a), 0.22 * math.sin(a), -0.004), (0.38, 0.05, 0.02), FW_WEB, rz=a, bevel=0.006, parent=fw)
# T04: the balance weight, bolted between two spokes: the one bold mark on the wheel (one pass a loop at any pixel)
sector((0, 0, 0.018), 0.15, 0.4, PI / 2 - 0.62, PI / 2 + 0.62, 0.035, FW_WEIGHT, seg=12, parent=fw)
for k in range(3):
    a = PI / 2 + (k - 1) * 0.42
    cyl((0.3 * math.cos(a), 0.3 * math.sin(a), 0.04), 0.016, 0.02, "bolt", verts=8, bevel=0, parent=fw)
spin(fw, 1)
label(3, "flywheel and crankshaft, one turn a stroke", (0, fy, CZ + 0.36))
label(4, "power cylinders on the vent's own gas: the rockers nod", (0, CY - 0.2, 1.4))

# ---------------------------------------------------------------- the two compressor cylinders, opposed
for s in (-1, 1):
    xd0, xd1 = s * 0.33, s * 0.74          # the open distance piece
    for yy in (CY - 0.13, CY + 0.13):
        box(((xd0 + xd1) / 2, yy, CZ), (abs(xd1 - xd0), 0.04, 0.05), "dark_steel", bevel=0.004)
        box(((xd0 + xd1) / 2, yy, CZ - 0.16), (abs(xd1 - xd0), 0.04, 0.04), "dark_steel", bevel=0.004)
    box(((xd0 + xd1) / 2, CY, CZ - 0.22), (abs(xd1 - xd0), 0.3, 0.06), "dark", bevel=0.006)    # T04: oil-dark guide floor
    xc0 = s * 0.54                                                                               # T04: was 0.52
    ch = pivot((xc0, CY, CZ))
    box((0, 0, 0), (0.12, 0.2, 0.16), "bare", bevel=0.01, parent=ch)                            # T04: was nickel
    box((0, 0, 0.085), (0.1, 0.17, 0.012), "yellow", bevel=0.003, parent=ch)                    # T04: the top slipper
    sphere((0, -0.085, 0.0), 0.02, "bolt", parent=ch)
    cyl((s * 0.315, CY, CZ), 0.07, 0.02, "dark", rot=(0, PI / 2, 0), verts=24, bevel=0)     # the crankcase's rod bore

    def _ch(t, on, ch=ch, s=s, xc0=xc0):
        ch.location = Vector((xc0 + s * xh(t, on), CY, CZ))
    K.ANIM.append(_ch)
    link(lambda t, on, s=s, xc0=xc0: (xc0 + s * xh(t, on), CY, CZ), lambda t, on, s=s: (s * 0.76, CY, CZ),
         r=0.035, mat="nickel", name="piston rod")
    link(lambda t, on, s=s, xc0=xc0: (xc0 + s * xh(t, on), CY, CZ), lambda t, on: (0, CY, CZ),
         r=0.045, mat="dark_steel", name="connecting rod")
    xc = s * 1.06
    cyl((xc, CY, CZ), 0.25, 0.56, "green", rot=(0, PI / 2, 0), verts=40)
    for xx in (s * 0.8, s * 1.32):
        cyl((xx, CY, CZ), 0.28, 0.07, "dark_steel", rot=(0, PI / 2, 0), verts=40)
        for k in range(10):
            a = 2 * PI * (k + 0.5) / 10
            cyl((xx + s * 0.04, CY + 0.25 * math.cos(a), CZ + 0.25 * math.sin(a)), 0.012, 0.02, "bolt",
                rot=(0, PI / 2, 0), verts=6, bevel=0)
    for xx in (s * 0.94, s * 1.18):                       # the valve caps, suction on top, discharge below
        cyl((xx, CY, CZ + 0.27), 0.07, 0.08, "dark_steel", verts=16)
        bolts(xx, CY, CZ + 0.315, 0.05, 4, r=0.01)
        cyl((xx, CY - 0.26, CZ - 0.06), 0.065, 0.07, "dark_steel", rot=(PI / 2, 0, 0), verts=16)
    box((xc, CY, (CZ - 0.25) / 2 + 0.08), (0.3, 0.3, CZ - 0.25 + 0.04), "dark_steel")
    hazard_tag((s * 0.54, CY - 0.155, CZ - 0.22), 0.3, 0.05)
label(5, "compressor cylinders, opposed: rods and crossheads slide in the open frames", (-0.55, CY - 0.1, CZ))

# ---------------------------------------------------------------- suction: the scrubber's head over the top to both cylinders
for s in (-1, 1):
    pipe([(SX + s * 0.3, SY - 0.1, 1.02), (s * 0.5, SY - 0.2, 1.02), (s * 0.82, -0.3, 1.0),
          (s * 0.94, CY + 0.1, CZ + 0.42), (s * 0.94, CY, CZ + 0.31)], r=0.07, mat="green",
         name="suction: the scrubber to a cylinder")
    cyl((SX + s * 0.31, SY - 0.1, 1.02), 0.1, 0.06, "dark_steel", rot=(0, PI / 2, 0), verts=24)
label(6, "suction lines from the scrubber to both cylinders", (0.6, -0.25, 1.0))

# ---------------------------------------------------------------- discharge: up each side into the bottle, the east one through the glass
DY, DZ, DR = 0.98, 0.52, 0.24
drum_ew(-1.18, 0.44, DY, DZ, DR, mat="grey", bands=(-0.85, -0.35, 0.15), saddles=(-0.9, 0.2))
manway_top(-0.35, DY, DZ + DR - 0.02, r=0.09)
pipe([(-1.18, CY - 0.27, CZ - 0.06), (-1.18, CY - 0.42, 0.5), (-1.3, CY - 0.44, 0.5), (-1.45, CY - 0.34, 0.5),
      (-1.45, -0.3, 0.5), (-1.45, 0.6, DZ), (-1.45, DY, DZ), (-1.28, DY, DZ)], r=0.075, mat="iron", name="discharge, west: cylinder to the bottle")
g0, g1, _ = gas_window((1.16, -0.14, 0.62), (1.16, 0.4, 0.62), r=0.11, k=2)
pipe([(1.18, CY - 0.27, CZ - 0.06), (1.18, CY - 0.42, 0.5), (1.3, CY - 0.44, 0.5), (1.45, CY - 0.34, 0.5),
      (1.45, -0.42, 0.55), (1.22, -0.24, 0.62), (1.16, -0.18, 0.62)], r=0.075, mat="iron", name="discharge, east: cylinder to the sight glass")
pipe([(1.16, 0.44, 0.62), (1.16, 0.62, 0.62), (0.9, 0.85, 0.55), (0.58, DY, DZ)], r=0.075, mat="iron",
     name="discharge, east: the sight glass to the bottle")
for y_ in (0.0, 0.3):
    box((1.16, y_, 0.3), (0.12, 0.08, 0.44), "dark_steel")
noz = nozzle("N", length=0.24, mat="bare")
cyl((0, DY + DR - 0.02, 0.45), 0.17, 0.12, "bare", rot=(PI / 2, 0, 0), verts=32)          # the bottle's outlet stub
cyl((0, (DY + DR + noz[1]) / 2, 0.44), 0.17, noz[1] - DY - DR + 0.02, "bare", rot=(PI / 2, 0, 0), verts=32)
gauge((-0.85, DY - DR - 0.02, DZ + 0.06), (0, -1, 0.5), r=0.08, needle=0.02, live=lambda t: -0.2 + 0.9 * delivery(t))
label(7, "discharge up the east side through the sight glass", (1.16, 0.12, 0.75))
label(8, "discharge bottle along the north face", (-0.6, DY, DZ + 0.3))
label(9, "gas out, north, straight off the bottle at the connection's size", (0, 1.34, ZA))

# ---------------------------------------------------------------- the gauge board (W), the fuel, the lube tank and panel (NE)
box((-0.98, 0.12, 0.42), (0.7, 0.12, 0.66), "cream", bevel=0.02)
box((-0.98, 0.18, 0.2), (0.12, 0.12, 0.3), "dark_steel")
for k, (ph, amp) in enumerate(((0.0, 0.9), (0.33, 0.7), (0.66, 1.1))):
    gauge((-1.18 + 0.2 * k, 0.05, 0.52), (0, -1, 0.15), r=0.075, needle=0.02,
          live=lambda t, ph=ph, amp=amp: -0.3 + amp * delivery((t + ph * 0.0) % 1.0))
for k in range(3):
    box((-1.18 + 0.2 * k, 0.05, 0.32), (0.14, 0.01, 0.05), "label", bevel=0)
_n0 = len(K.OBJS)
bundle([(-0.98, 0.18, 0.75), (-0.8, 0.3, 1.0), (-0.5, 0.25, 1.25), (-0.25, CY + 0.3, 1.2), (-0.14, CY + 0.22, 1.16)],
       cols=("black", "red", "grey"), r=0.014, name="gauge board to the ignition")
for _o in K.OBJS[_n0:]:                       # T04: the bundle's markers cream, not label paint (they rolled to white px)
    if _o.type == "MESH" and _o.data.materials and _o.data.materials[0].name == K.M["label"].name:
        _o.data.materials[0] = K.M["cream"]
pipe([(-0.98, 0.12, 0.74), (-0.7, -0.05, 1.1), (-0.32, SY - 0.1, 1.2), (SX - 0.3, SY, 1.2)], r=0.025, mat="bare",
     name="gauge line to the scrubber")
hose([(SX + 0.3, SY + 0.05, 1.3), (0.45, 0.0, 1.3), (0.42, -0.3, 1.2), (0.3, CY + 0.35, 0.95)], r=0.035, mat="hose",
     name="fuel hose: the scrubber to the regulator")
cyl((0.3, CY + 0.35, 0.86), 0.07, 0.16, "yellow", rot=(0, PI / 2, 0), verts=20)            # the regulator
head(0.3, CY + 0.35, 0.92, 0.07, 0.06, "yellow")
pipe([(0.25, CY + 0.35, 0.86), (0.22, CY + 0.2, 0.95), (0.2, CY - 0.2, 0.95), (0.14, CY - 0.2, 0.95)], r=0.025,
     mat="bare",
     name="fuel: the regulator to the gas rail")
label(10, "fuel: a tan hose from the scrubber through the regulator", (0.45, -0.1, 1.3))
label(11, "gauge board: three needles kick on the strokes", (-0.98, 0.05, 0.75))
vtank(1.18, 1.18, 0.2, 0.9, mat="cream", bands=(0.45,), nozzle=None)
cabinet(0.76, 1.3, 0.3, 0.22, 0.5, mat="grey")
status_lens(0.84, 1.22, 0.54)
for yy in (-1.25, -1.0):
    box((-1.08, yy, 0.2), (0.44, 0.18, 0.18), "ochre", bevel=0.015)                        # spare cylinder liners, crated
box((1.1, -1.36, 0.14), (0.22, 0.16, 0.16), "dark_steel", bevel=0.015)
stain(0.2, -0.3, 0.2, 0.08)
stain(-0.7, -1.2, 0.2, 0.08)

route("gas", [(SX, SY, 0.25), (SX, SY, 0.9), (SX + 0.3, SY - 0.1, 1.02), (0.5, SY - 0.2, 1.02), (0.82, -0.3, 1.0),
              (0.94, CY, CZ + 0.31), (1.06, CY, CZ), (1.18, CY - 0.27, CZ - 0.06), (1.45, CY - 0.3, 0.5), (1.45, -0.42, 0.55),
              (1.16, -0.14, 0.62), (1.16, 0.62, 0.62), (0.9, 0.85, 0.55), (0.44, DY, DZ), (0, DY, DZ),
              (0, 1.5, ZA)])
route("gas", [(SX, SY, 0.9), (SX - 0.3, SY - 0.1, 1.02), (-0.5, SY - 0.2, 1.02), (-0.82, -0.3, 1.0), (-0.94, CY, CZ + 0.31),
              (-1.06, CY, CZ), (-1.18, CY - 0.38, 0.5), (-1.45, CY - 0.3, 0.5), (-1.45, 0.6, DZ), (-1.18, DY, DZ),
              (-0.1, DY, DZ)])
route("fuel", [(SX + 0.3, SY + 0.05, 1.3), (0.45, 0.0, 1.3), (0.42, -0.3, 1.2), (0.3, CY + 0.35, 0.95),
               (0.22, CY + 0.2, 0.95), (0.2, CY - 0.2, 0.95)])
run_gp(dict(name="the flywheel compressor", footprint=[3, 3], take=2), nf=NF)
