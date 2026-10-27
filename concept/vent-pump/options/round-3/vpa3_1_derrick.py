"""Vent Pump, round 3, concept 1: THE GAS-LIFT DERRICK (3 x 3).

  $BLENDER -b --python vpa3_1_derrick.py -- <out-dir> [--quick] [--only working|idle|rot] [--colourmap]

Round 2's derrick (../round-2/vpa_1_derrick.py) with helium seen at work and every pipe going
somewhere. What helium does here: it is the lifting gas -- injected down the lance into the
bore, it lightens the melt column so each charge drives a surge up the side riser.

The run: helium-3 in at the south face to the valve station (gate valve), through the turning
flow meter, up the derrick's south face in the grey-violet lagged line (a pressure gauge on it
at the crown) to the injector valve, whose lever kicks; then down the lance into the wellhead.
The melt surges out of the wellhead's east wing, up the riser (its sight glass floods orange),
over into the surge pot, where the gas breaks out of the melt; the melt leaves at the pot's foot
for the north face. The spent gas goes off the pot's head along a return line to the booster
compressor (west), which pumps it back into the valve station: the loop is closed. The bottles
(south-west) are the start-up charge, piped into the same station.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpa3_kit import *  # noqa: F401,F403,E402
import vpa_kit as K  # noqa: E402

build_materials3(((0.45, 0.3), (0.95, 0.35), (1.4, 0.3)))
NF = 32
K.SUN_E = 11.5                      # the lattice and the cellar read dark at the kit's 10
SURGE = (-0.16, 0.34)                # the riser full in frame 0
KICK = tuple(c - 0.06 for c in SURGE)   # the injector kicks just before the melt arrives


def level(t):
    return pulse(t, [c + 0.04 for c in SURGE], rise=0.12, fall=0.3)


def charge(t):
    return pulse(t, KICK, rise=0.03, fall=0.16)


# ---------------------------------------------------------------- the cellar and the wellhead
prism((0, 0, 0.11), 0.92, 0.22, "refr", n=8, rz=PI / 8, bevel=0.03)
for k in range(8):
    a = PI / 8 + k * PI / 4
    box((0.86 * math.cos(a + PI / 8), 0.86 * math.sin(a + PI / 8), 0.12), (0.06, 0.12, 0.2), "dark_steel",
        rz=a + PI / 8, bevel=0.006)
cyl((0, 0, 0.36), 0.42, 0.28, "dark_steel", verts=48)
flange_ring(0, 0, 0.5, 0.42, mat="bare", h=0.05, nb=16)
cyl((0, 0, 0.66), 0.3, 0.28, "grey", verts=40)
flange_ring(0, 0, 0.8, 0.3, mat="bare", h=0.04, nb=12)
cyl((0, 0, 0.92), 0.26, 0.2, "dark_steel", verts=40)
# the wings: east to the riser (hot), west a bolted pressure tapping with the bore gauge
cyl((0.36, 0, 0.92), 0.15, 0.24, "heat", rot=(0, PI / 2, 0), verts=32)
cyl((0.48, 0, 0.92), 0.21, 0.04, "bare", rot=(0, PI / 2, 0), verts=32)
cyl((-0.32, 0, 0.92), 0.08, 0.16, "dark_steel", rot=(0, PI / 2, 0), verts=24)
cyl((-0.41, 0, 0.92), 0.11, 0.03, "bare", rot=(0, PI / 2, 0), verts=24)
gauge((-0.44, -0.0, 1.02), (-0.3, -1, 0.7), r=0.07, live=lambda t: 0.8 * level(t))
# the master valve and the stuffing box the lance goes through
cyl((0, 0, 1.08), 0.2, 0.12, "bare", verts=32)
cyl((0, 0, 1.2), 0.15, 0.14, "dark_steel", verts=24)
handwheel((0, -0.24, 1.2), 0.1, axis=(0, -1, 0), mat="red")
cyl((0, -0.17, 1.2), 0.03, 0.1, "bare", rot=(PI / 2, 0, 0), verts=8)
cyl((0, 0, 1.3), 0.09, 0.08, "bare", verts=16)
label(7, "wellhead on the vent: the lance's helium lifts the melt", (0.0, -0.3, 0.7))

# ---------------------------------------------------------------- the derrick
B, T, ZT = 0.86, 0.3, 2.3


def leg(sx, sy, z):
    f = z / ZT
    return (sx * (B + (T - B) * f), sy * (B + (T - B) * f), z)


for sx in (-1, 1):
    for sy in (-1, 1):
        strut(leg(sx, sy, 0.2), leg(sx, sy, ZT), 0.05, "oxide")
        box((sx * B, sy * B, 0.26), (0.2, 0.2, 0.1), "dark_steel", bevel=0.01)
        for dx, dy in ((-0.06, -0.06), (0.06, -0.06), (-0.06, 0.06), (0.06, 0.06)):
            cyl((sx * B + dx, sy * B + dy, 0.32), 0.016, 0.03, "bolt", verts=6, bevel=0)
LEV = (0.2, 0.95, 1.65, ZT)
for z in LEV[1:]:
    for (ax, ay), (bx, by) in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
        strut(leg(ax, ay, z), leg(bx, by, z), 0.035, "oxide")
for z0, z1 in zip(LEV, LEV[1:]):
    for (ax, ay), (bx, by) in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
        if (ax, ay, bx, by) == (1, -1, 1, 1) and z0 < 1.0:
            continue                       # the east face's lower bay open for the riser's wing
        strut(leg(ax, ay, z0), leg(bx, by, z1), 0.025, "oxide")
        strut(leg(bx, by, z0), leg(ax, ay, z1), 0.025, "oxide")
for k in range(7):
    z = 0.35 + 0.27 * k
    strut(leg(-1, 1, z), (leg(-1, 1, z)[0] + 0.14, leg(-1, 1, z)[1] - 0.14, z), 0.012, "yellow")
# the crown: a deck, the sheave, the injector
box((0, 0, ZT + 0.06), (0.86, 0.86, 0.12), "dark_steel", bevel=0.012)
box((0, 0, ZT + 0.125), (0.78, 0.78, 0.012), "hazard", bevel=0)
for sx in (-1, 1):
    for sy in (-1, 1):
        cyl((sx * 0.36, sy * 0.36, ZT + 0.15), 0.025, 0.05, "bolt", verts=6, bevel=0)
box((0, 0.22, ZT + 0.3), (0.06, 0.06, 0.36), "oxide")
box((0, 0.22, ZT + 0.48), (0.3, 0.07, 0.06), "oxide")
cyl((0, 0.22, ZT + 0.42), 0.09, 0.05, "bare", rot=(PI / 2, 0, 0), verts=24)
# the lance: down the bore from the injector through the stuffing box, lagged like the line
cyl((0, 0, (1.3 + ZT + 0.2) / 2), 0.055, ZT + 0.2 - 1.3, "he_lag", verts=16)
for z in (1.55, 1.95):
    cyl((0, 0, z), 0.075, 0.05, "he_band", verts=16)
label(6, "the lance: helium down the bore", (0.0, 0.0, 1.75))
# the injector valve: body, actuator, the lever that kicks
cyl((0, 0, ZT + 0.24), 0.11, 0.18, "bare", verts=24)
cyl((0, 0, ZT + 0.34), 0.13, 0.03, "dark_steel", verts=24)
bolts(0, 0, ZT + 0.36, 0.11, 6, r=0.012)
cyl((0.2, -0.02, ZT + 0.24), 0.06, 0.24, "yellow", rot=(0, PI / 2, 0), verts=20)
cyl((0.33, -0.02, ZT + 0.24), 0.07, 0.03, "dark_steel", rot=(0, PI / 2, 0), verts=20)
lev = pivot((0, -0.02, ZT + 0.39))
box((0.17, 0, 0.0), (0.34, 0.05, 0.04), "red", bevel=0.006, parent=lev)
sphere((0.35, 0, 0.0), 0.045, "red", seg=16, parent=lev)
cyl((0.0, 0, 0.0), 0.045, 0.06, "bare", verts=12, parent=lev)
rod = pivot((0.0, -0.02, ZT + 0.24))
cyl((0.0, 0, 0), 0.02, 0.16, "bare", rot=(0, PI / 2, 0), verts=8, parent=rod)


def kick(t, on):
    k = charge(t) if on else 0.0
    lev.rotation_euler = (0, 0, -0.35 + 0.95 * k)
    rod.location = (0.02 + 0.06 * (1 - k), -0.02, ZT + 0.24)


K.ANIM.append(kick)
label(5, "injector valve on the crown: its lever kicks, then the surge", (0.15, 0.0, ZT + 0.4))

# ---------------------------------------------------------------- helium in: south face, station, meter
face_nozzle("S", -1.12, r=0.2, mat="bare", label_n=1, text="helium-3 in (south face)")
cyl((0, -1.08, ZA), 0.26, 0.08, "bare", rot=(PI / 2, 0, 0), verts=32)
box((0, -0.98, ZA), (0.34, 0.16, 0.36), "grey", bevel=0.02)
cyl((0, -0.98, ZA + 0.26), 0.05, 0.16, "bare", verts=12)
handwheel((0, -0.98, ZA + 0.36), 0.11, mat="red")
label(2, "valve station (the bottles and the compressor's return join here)", (0.0, -0.98, 0.8))
# the meter: off the station's east face, turning, faster with each charge
he_line([(0.17, -0.98, 0.36), (0.22, -1.02, 0.36)], r=0.05, bands=0, kind=None)
m_in, m_out = flow_meter(0.36, -1.02, 0.36, d=(1, 0), turns=4, ease=burst_ease(KICK, base=0.35))
label(3, "helium flow meter (turns while working, spurts at each charge)", (0.36, -1.02, 0.5))
record("helium", [(0, -1.5, ZA), (0, -0.98, ZA), (0.17, -0.98, 0.36), m_in])
# the lagged line: from the meter up the derrick's south face to the injector
xs = 0.16
pts = [m_out, (0.6, -0.95, 0.4), (0.5, -0.84, 0.52), (xs + 0.08, -0.84, 0.68)]
for z in (0.85, 1.3, 1.8, 2.15):
    pts.append((xs, -(B + (T - B) * z / ZT) - 0.11, z))
pts += [(xs, -0.32, ZT + 0.32), (0.08, -0.12, ZT + 0.3), (0.02, -0.04, ZT + 0.26)]
he_line(pts, r=0.065)
record("helium", [(0.0, 0.0, ZT + 0.24), (0.0, 0.0, 1.3), (0.0, 0.0, 0.92)])
for z in (0.95, 1.65):
    y = -(B + (T - B) * z / ZT)
    box((xs, y - 0.06, z), (0.18, 0.12, 0.04), "dark_steel", bevel=0.004)
# the line's pressure gauge at the crown: it jumps at each charge
cyl((xs + 0.09, -0.48, ZT + 0.2), 0.02, 0.1, "bare", rot=(0, PI / 2, 0), verts=8)
gauge((xs + 0.16, -0.5, ZT + 0.24), (0.3, -1, 0.6), r=0.075, live=lambda t: 1.4 * charge(t) - 0.2)
label(4, "lagged helium line up the derrick (gauge at the crown)", (xs, -0.7, 1.35))

# ---------------------------------------------------------------- melt: riser, surge pot, out
RX, RY = 1.06, -0.02
cyl((0.8, 0, 0.92), 0.15, 0.5, "heat", rot=(0, PI / 2, 0), verts=32)
sphere((RX, 0, 0.92), 0.17, "heat", seg=24)
cyl((RX, RY, 1.45), 0.16, 1.05, "heat", verts=32)
for z in (1.02, 1.9):
    cyl((RX, RY, z), 0.21, 0.05, "bare", verts=32)
    bolts(RX, RY, z + 0.03, 0.19, 8, r=0.013)
box((RX, RY, 0.45), (0.3, 0.3, 0.9), "dark_steel", bevel=0.015)
pad(0.83, -0.5, 1.495, 0.3, 0.4, "grey", cut=0.0, corners=())
for yy in (-0.38, 0.14):
    box((1.47, yy, 0.22), (0.03, 0.14, 0.3), "dark_steel", bevel=0.004)
stencil((1.485, -0.12, 0.3), (0.012, 0.3, 0.08))
for zz in (0.25, 0.65):
    box((RX, RY - 0.155, zz), (0.24, 0.012, 0.05), "hazard", bevel=0)
G0, G1 = 1.06, 1.84
sight_glass_v(RX, RY - 0.16, G0, G1, w=0.15, facing=(0, -1))
gpiv = pivot((RX, RY - 0.19, G0))
col = box((0, 0, 0.5), (0.145, 0.012, 1.0), melt("riser", scale=14.0, k=2, bright=1.3), bevel=0, parent=gpiv)
gpiv.scale = (1, 1, 0.001)


def flood(t, on):
    lv = level(t) if on else 0.0
    gpiv.scale = (1, 1, max(0.001, (G1 - G0) * (0.15 + 0.85 * lv)) if on else 0.001)
    col.hide_render = not on


K.ANIM.append(flood)
label(8, "side riser: its sight glass floods orange with each surge", (RX, RY - 0.2, 1.45))
pipe([(RX, RY, 1.92), (RX, RY + 0.12, 2.06), (RX - 0.02, 0.45, 2.08), (1.0, 0.82, 1.98), (0.98, 0.98, 1.86)],
     r=0.13, mat="heat", flanges=False)
PX, PY = 0.98, 1.0
cyl((PX, PY, 0.16), 0.36, 0.32, "dark_steel", verts=40)
pad(0.5, 0.505, 1.495, 1.495, 0.2, "dark_steel", cut=0.34, corners=("NE",))
cyl((PX, PY, 1.0), 0.3, 1.4, "refr", verts=40)
for z in (0.42, 0.95, 1.5):
    band(PX, PY, z, 0.3, h=0.06, mat="dark_steel", lugs=2, lug_a=-PI * 0.75)
head(PX, PY, 1.7, 0.3, 0.14, "heat")
cyl((PX, PY, 1.86), 0.14, 0.12, "heat", verts=24)
flange_ring(PX, PY, 1.92, 0.14, mat="bare", h=0.03, nb=8)
# the gas off the pot's head: a separator dome and its outlet
cyl((PX, PY, 2.0), 0.1, 0.1, "bare", verts=20)
head(PX, PY, 2.05, 0.1, 0.06, "dark_steel")
cyl((PX + 0.2, PY + 0.08, 1.8), 0.035, 0.22, "bare", verts=12)
cyl((PX + 0.2, PY + 0.08, 1.94), 0.05, 0.06, "brass", verts=12)
cyl((PX + 0.2, PY + 0.08, 2.0), 0.03, 0.06, "red", verts=12)
label(9, "surge pot: the gas breaks out of the melt", (PX, PY - 0.3, 1.2))
melt_path([(0.0, 0.0, 0.6), (0.0, 0.0, 0.92), (0.5, 0.0, 0.92), (RX, 0.0, 0.92), (RX, RY, 1.4), (RX, RY, 1.92),
           (RX, RY + 0.12, 2.06), (RX - 0.02, 0.45, 2.08), (1.0, 0.82, 1.98), (PX, PY, 1.7), (PX, PY, 0.8),
           (PX, PY, ZA)])
melt_path([(PX, PY, ZA), (0.5, 1.0, ZA), (0.0, 1.0, ZA), (0.0, 1.5, ZA)])
cyl(((PX - 0.3 + 0.08) / 2, 1.0, ZA), 0.17, PX - 0.3 - 0.08, "heat", rot=(0, PI / 2, 0), verts=32)
sphere((0.0, 1.0, ZA), 0.19, "heat", seg=24)
face_nozzle("N", 1.0, r=0.2, mat="heat", label_n=10, text="molten kamacite out (north face)")
cyl((0.36, 1.0, ZA), 0.24, 0.05, "bare", rot=(0, PI / 2, 0), verts=32)

# ---------------------------------------------------------------- spent gas: pot head -> compressor -> station
CX = -1.08
pad(-1.495, -0.36, -0.79, 0.7, 0.28, "dark_steel", cut=0.0)
gearbox(CX, 0.4, 0.48, 0.5, 0.42, 0.48, mat="green")
for k, y in enumerate((0.3, 0.52)):
    cyl((CX, y, 0.86), 0.11, 0.3, "green", verts=24)
    cyl((CX, y, 1.04), 0.13, 0.05, "dark_steel", verts=24)
    bolts(CX, y, 1.07, 0.1, 6, r=0.012)
end = motor(CX, -0.18, 0.5, d=(0, 1), s=1.05, mat="green")
coupling(end[0], end[1] + 0.02, end[2], 0.11, axis=(0, 1, 0), turns=2)
label(12, "booster compressor: recovers the spent gas", (CX, 0.3, 1.0))
spent_line([(PX, PY, 2.08), (PX - 0.05, PY, 2.2), (0.6, 1.2, 1.95), (0.0, 1.24, 1.6), (-0.6, 1.0, 1.35),
            (CX + 0.02, 0.6, 1.2), (CX, 0.52, 1.08)], r=0.045)
label(11, "spent-gas return off the pot's head", (0.0, 1.24, 1.6))
# the compressor's discharge back into the station (recovered, so lagged again)
he_line([(CX, 0.3, 1.08), (CX + 0.12, 0.2, 1.15), (-0.86, -0.3, 0.8), (-0.55, -0.82, 0.55), (-0.17, -0.96, 0.5)],
        r=0.05, kind="spent")
# north-west: the switch cabinet, cables to the motor and the actuator
cabinet3(-1.02, 1.12, 0.95, 0.75, 0.95, mat="grey", corner=("NW",), cut=0.3)
id_panel((-1.0, 0.74, 0.55), 0.3, 0.16, stripe="red")
box((-1.08, 1.1, 1.0), (0.36, 0.34, 0.1), "dark_steel", bevel=0.01)
for k in range(4):
    box((-1.08, 0.97 + 0.08 * k, 1.06), (0.32, 0.03, 0.02), "grey", bevel=0.003)
jbox(-0.82, 1.3, w=0.24, d=0.18, h=0.2, mat="grey", z=0.95)
bundle([(-0.75, 0.85, 0.9), (-0.55, 0.6, 1.5), leg(-1, 1, 1.9), (-0.1, 0.2, ZT + 0.2), (0.2, -0.02, ZT + 0.3)],
       cols=("black", "yellow"), r=0.016)
bundle([(-1.2, 0.8, 0.5), (-1.25, 0.4, 0.35), (-1.08, -0.05, 0.62)], cols=("black", "red"), r=0.018)
# south-west: the start-up bottles, their header into the station
pad(-1.495, -1.495, -0.42, -0.6, 0.1, "dark_steel", cut=0.32, corners=("SW",))
hdr, _ = bottles(-1.02, -1.04, n=4, L=0.6, r=0.085, z0=0.1, side=1)
he_line([hdr, (hdr[0] + 0.12, hdr[1], hdr[2] + 0.02), (-0.4, -1.02, 0.36), (-0.17, -1.0, 0.32)], r=0.045,
        bands=0.2)
label(13, "start-up bottles, piped into the station", (-1.0, -1.04, 0.35))
# south-east: the control desk and the heater transformer (chamfered corner)
pad(0.69, -1.495, 1.495, -0.675, 0.72, "cream", cut=0.3, corners=("SE",), bevel=0.02)
for k in range(5):
    box((1.05 - 0.28 + 0.14 * k, -1.505, 0.42), (0.08, 0.02, 0.4), "dark_steel", bevel=0.003)
box((1.05, -1.02, 0.75), (0.7, 0.78, 0.06), "dark_steel", bevel=0.008)
for x in (0.85, 1.05, 1.25):
    cyl((x, -0.9, 0.85), 0.04, 0.16, "ceramic", verts=12)
    cyl((x, -0.9, 0.95), 0.055, 0.03, "ceramic", verts=12)
status_lamp(1.2, -1.2, 0.8)
box((0.86, -1.26, 0.84), (0.3, 0.22, 0.18), "grey", bevel=0.01)
gauge((0.86, -1.375, 0.86), (0, -1, 0.4), r=0.05, live=lambda t: 0.5 * level(t))
stencil((1.0, -1.505, 0.62), (0.4, 0.012, 0.08))
trunk([(0.85, -0.9, 0.95), (0.8, -0.55, 1.1), (RX - 0.1, RY - 0.12, 1.0)], r=0.03)
label(14, "riser heater transformer", (1.05, -1.0, 0.85))
# east: a slag skip by the riser; north: tool chest
box((1.2, 0.48, 0.2), (0.5, 0.42, 0.4), "ochre", bevel=0.02)
box((1.2, 0.48, 0.41), (0.42, 0.34, 0.02), "dark", bevel=0)
box((-0.36, 1.2, 0.18), (0.36, 0.59, 0.36), "oxide", bevel=0.015)
box((-0.36, 1.2, 0.37), (0.38, 0.6, 0.03), "dark_steel", bevel=0.005)
for (x, y) in ((0.62, 0.62), (-0.5, 0.75)):
    box((x, y, 0.06), (0.36, 0.3, 0.12), "dark_steel", bevel=0.008)
box((0.0, -1.165, 0.1), (1.0, 0.66, 0.2), "dark_steel", bevel=0.012)
box((-0.5, -0.66, 0.15), (0.4, 0.3, 0.3), "ochre", bevel=0.015)
stain(0.4, 0.5, 0.25, 0.15)
stain(-0.5, -0.4, 0.2, 0.12)
stain(1.05, 0.3, 0.2, 0.15)
run3(dict(name="the gas-lift derrick", footprint=[3, 3], surges=list(SURGE), kicks=list(KICK)), nf=NF)
