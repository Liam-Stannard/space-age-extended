"""Radiant Generator, round 5, suggestion 8: THE CHARGE-AND-DUMP BANK (4x4).

The cell sits in a lead collector pot; the collector charges six capacitor drums standing
round it, and a rotary distributor on the pot's head -- a heavy copper arm on a geared
hub -- sweeps round, touching each drum's contact in turn and dumping it into the output
bus. Each drum's charge column climbs as it fills and drops as the arm passes; the output
meter kicks at every dump.

  cell magazine (SW, ochre) -> lead throat -> collector pot (centre, two bullseye ports)
  -> six capacitor drums (grey and cream) -> contact posts -> distributor arm (turning)
  -> hub and slip collector -> bus duct down the pot -> output cabinet (S, oxide) and
  meter -> cable trunks (SE).  Coolant: the pot's jacket -> pump (NE) -> radiator (N).

  $BLENDER -b --python r5b_8_charge_bank.py -- <out-dir> [--quick] [--only idle|working]
Not a model; nothing is adopted.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r5b_kit import *  # noqa: E402,F401,F403

W, H = 4, 4
PX, PY, PR, PH = 0.0, 0.22, 0.6, 1.15        # the collector pot
ZA = PH + 0.42                              # the arm's height
DR = 1.38                                   # the drums' ring
DRUM_A = [math.radians(a) for a in (0, 55, 125, 180, 235, 305)]
ARM_PHASE = math.radians(-90)               # where the arm points at t = 0


def arm_angle(t):
    return ARM_PHASE + 2 * PI * t


def level(t, a):
    """A drum's charge, 0..1: it climbs steadily from the moment the arm leaves it and
    drops to nothing as the arm passes."""
    d = ((arm_angle(t) - a) / (2 * PI)) % 1.0       # fraction of a turn since the arm passed
    return min(1.0, d / 0.92)


def pot():
    cyl((PX, PY, 0.1), PR + 0.14, 0.2, "dark_steel", verts=72)
    bolts(PX, PY, 0.21, PR + 0.08, 18, r=0.02)
    cyl((PX, PY, PH / 2 + 0.12), PR, PH - 0.08, "lead", verts=96)
    for z in (0.42, 1.0):
        vessel_band(PX, PY, z, PR, n_rivets=12, lug_a=-PI / 2 - 0.7)
    head(PX, PY, PH + 0.08, PR, 0.2, "lead")
    flange_ring(PX, PY, PH + 0.08, PR - 0.03, mat="bare", h=0.05, nb=18)
    porthole(PX, PY, 0.72, PR, -PI / 2 - 0.42, 0.12, "fl_port1", k=2, arms=3)
    porthole(PX, PY, 0.72, PR, -PI / 2 + 0.42, 0.12, "fl_port2", k=-2, arms=3, spin=0.7)
    point((PX, PY - PR - 0.3, 0.72), 3.5, pulse=lambda t: 0.8 + 0.2 * math.sin(2 * PI * 6 * t))
    insp_plate(PX, PY, PR, -PI / 2, 0.3, 0.5, 0.18, mat="lead_new")
    hazard_tag((PX, PY - PR + 0.03, 1.1), 0.3, 0.06)
    # the hub on the head: a geared turret, the slip collector, the bus duct down the side
    cyl((PX, PY, PH + 0.3), 0.26, 0.14, "dark_steel", verts=40)
    for k in range(24):
        a = 2 * PI * k / 24
        box((PX + 0.27 * math.cos(a), PY + 0.27 * math.sin(a), PH + 0.3), (0.03, 0.03, 0.12), "bare", rz=a, bevel=0)
    box((PX + 0.32, PY + 0.2, PH + 0.32), (0.22, 0.2, 0.2), "green", rz=0.6)          # drive motor
    cyl((PX + 0.32, PY + 0.2, PH + 0.45), 0.05, 0.06, "bare", verts=12)
    box((PX + 0.42, PY - 0.42, 0.75), (0.14, 0.12, 1.2), "grey", rz=-0.8, bevel=0.01)     # bus duct
    bundle([(PX + 0.32, PY + 0.32, PH + 0.42), (0.6, 0.75, 1.0), (0.85, 1.05, 0.15)], cols=("black", "yellow"))


def arm():
    A = pivot((PX, PY, ZA))
    cyl((0, 0, 0), 0.16, 0.12, "dark_steel", verts=32, parent=A)
    cyl((0, 0, 0.09), 0.1, 0.06, "brass", verts=6, bevel=0, parent=A)
    box((0.42, 0, 0.0), (0.66, 0.1, 0.07), "copper", bevel=0.01, parent=A)
    box((0.42, 0, 0.05), (0.6, 0.05, 0.02), "hazard", bevel=0, parent=A)
    box((-0.22, 0, 0.0), (0.2, 0.16, 0.12), "dark_steel", bevel=0.01, parent=A)       # counterweight
    box((0.78, 0, -0.04), (0.12, 0.16, 0.08), "brass", bevel=0.01, parent=A)          # contact shoe
    b0 = A.rotation_euler.copy()

    def pose(t):
        A.rotation_euler = b0
        A.rotation_euler.rotate_axis("Z", arm_angle(t))
    ANIM.append(pose)


def drums():
    for i, a in enumerate(DRUM_A):
        x, y = PX + DR * math.cos(a), PY + DR * math.sin(a)
        mat = "cream" if i % 2 == 0 else "green"
        r, h = 0.3, 1.0
        cyl((x, y, 0.07), r + 0.07, 0.14, "dark_steel", verts=48)
        cyl((x, y, h / 2 + 0.1), r, h - 0.06, mat, verts=48)
        for k in range(16):                                         # corrugations
            b = 2 * PI * k / 16
            box((x + (r + 0.005) * math.cos(b), y + (r + 0.005) * math.sin(b), h / 2 + 0.1), (0.025, 0.03, h - 0.2),
                mat, rz=b, bevel=0.006)
        for z in (0.2, h + 0.02):
            cyl((x, y, z), r + 0.025, 0.05, "dark_steel", verts=48)
        cyl((x, y, h + 0.1), r - 0.02, 0.08, "dark_steel", verts=40)
        bolts(x, y, h + 0.15, r - 0.07, 8, r=0.014)
        # the contact post: an insulated rod up and in to where the arm's shoe passes
        ix, iy = PX + 0.84 * math.cos(a), PY + 0.84 * math.sin(a)
        cyl((x, y, h + 0.24), 0.05, 0.2, "hose_k", verts=12)
        pipe([(x, y, h + 0.32), (x + (ix - x) * 0.4, y + (iy - y) * 0.4, ZA + 0.06), (ix, iy, ZA - 0.03)], r=0.028,
             mat="copper")
        box((ix, iy, ZA - 0.07), (0.1, 0.1, 0.05), "brass", rz=a, bevel=0.004)
        # the charge column on the lid: a dark-steel mast, five lamps facing the camera
        lx, ly = x - 0.13 * math.cos(a) + 0.08, y - 0.13 * math.sin(a) - 0.06
        box((lx, ly + 0.02, h + 0.4), (0.1, 0.05, 0.56), "dark_steel", bevel=0.006)
        cyl((lx, ly + 0.02, h + 0.7), 0.05, 0.04, "bare", verts=12)
        for j in range(5):
            m = lamp_mat(f"lvl{i}_{j}", "#D8FFC8" if j < 4 else "#FFFFFF",
                         pulse=(lambda t, a=a, j=j: 1.0 if level(t, a) > (j + 0.5) / 5 else 0.04))
            box((lx, ly - 0.012, h + 0.18 + 0.1 * j), (0.07, 0.02, 0.06), m, bevel=0.003)
        if math.sin(a) < -0.2:
            stencil((x, y - r - 0.02, 0.92), (0.2, 0.01, 0.06), 0.0)
        # the drum's strap to its neighbour on the ground: the charging lead from the pot
        hose([(PX + (PR + 0.05) * math.cos(a), PY + (PR + 0.05) * math.sin(a), 0.3),
              (PX + 0.95 * math.cos(a), PY + 0.95 * math.sin(a), 0.22),
              (x - (r + 0.02) * math.cos(a), y - (r + 0.02) * math.sin(a), 0.35)], r=0.045,
             mat="hose_k" if i % 2 else "cable_red")


def magazine():
    """The cell magazine in the south-west corner (ochre), a lead throat into the pot."""
    mx, my = -1.42, -1.35
    box((mx, my, 0.55), (0.6, 0.6, 1.1), "ochre", bevel=0.025)
    box((mx, my, 1.13), (0.66, 0.66, 0.06), "dark_steel", bevel=0.01)
    for dx in (-0.14, 0.14):
        cyl((mx + dx, my, 1.2), 0.1, 0.08, "lead", verts=6, bevel=0.005)
    box((mx, my - 0.31, 0.6), (0.4, 0.02, 0.08), "hazard", bevel=0)
    id_panel((mx, my - 0.31, 0.82), 0.24, 0.12, stripe="green")
    cyl((-0.82, -0.82, 0.45), 0.12, 0.62, "lead", rot=(0, PI / 2, PI / 4), verts=24)
    box((mx + 0.42, my, 0.18), (0.3, 0.5, 0.36), "lead", bevel=0.02)                     # spent box
    for k in range(2):
        spent_cell((mx + 0.4, my - 0.1 + 0.2 * k, 0.4), (1, 0.2, 0), r=0.06, h=0.26)


def output():
    """The output cabinet (oxide) south of the pot, the big dump meter, cable trunks."""
    cx, cy = 0.75, -1.55
    box((cx, cy, 0.5), (1.0, 0.62, 1.0), "oxide", bevel=0.02)
    box((cx, cy, 1.03), (1.06, 0.68, 0.06), "dark_steel", bevel=0.01)
    meter((cx - 0.2, cy - 0.32, 0.68), (0, -1, 0.1), r=0.14,
          swing=lambda t: -0.5 + 1.1 * sum(max(0.0, 1 - (((arm_angle(t) - a) / (2 * PI)) % 1.0) / 0.12)
                                           for a in DRUM_A))
    meter((cx + 0.22, cy - 0.32, 0.72), (0, -1, 0.1), r=0.08, swing=lambda t: 0.3)
    for i in range(4):
        box((cx + 0.22, cy - 0.32, 0.3 + 0.07 * i), (0.36, 0.02, 0.025), "dark_steel", bevel=0)
    status_lamp(cx + 0.35, cy - 0.1, 1.08)
    hazard_tag((cx - 0.2, cy - 0.32, 0.42), 0.3, 0.06)
    jbox(cx - 0.15, cy + 0.05, 0.36, 0.3, 0.26, mat="grey", z=1.06)
    for k, dx in enumerate((-0.25, 0.0, 0.25)):
        hose([(cx + 0.5, cy + dx * 0.6, 0.55), (1.5, cy + dx * 0.8, 0.45), (1.7, cy - 0.15 + dx, 0.12),
              (1.78, cy - 0.2 + dx, -0.05)], r=0.06, mat="hose_k")


def cooling():
    """The pot's jacket coolant: a pump skid in the north-east, a radiator bank in the
    north between the drums, an expansion pot in the north-west corner."""
    radiator_bank(-0.75, 0.75, 1.55, 1.95, 0.1, 0.85, 7, mat="copper", along_x=True)
    pv = pump(1.45, 1.55, (0, -1), 0.6)
    hose([pv, (1.2, 1.2, 0.8), (0.8, 1.6, 0.98)], r=0.07, mat="hose")
    hose([(-0.8, 1.75, 0.2), (-0.55, 1.0, 0.3), (PX - 0.3, PY + PR - 0.02, 0.4)], r=0.08, mat="hose")
    vtank(-1.6, 1.6, 0.28, 0.9, "ochre", bands=(0.45,), top="dark_steel", nozzle=(0.2, -0.2))
    valve(1.75, 0.95, 0.0, 0.45, wheel="red")


pot()
arm()
drums()
magazine()
output()
cooling()
stain(0.2, -0.9, 0.4, 0.15)
stain(-1.4, -1.85, 0.3, 0.1)
stain(1.5, 1.2, 0.25, 0.25)
stain(1.7, -1.0, 0.15, 0.3)
run(W, H, name="8-the-charge-and-dump-bank")
