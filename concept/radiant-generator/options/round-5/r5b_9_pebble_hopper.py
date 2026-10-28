"""Radiant Generator, round 5, suggestion 9: THE PEBBLE COLUMN (3x3).

The cells are a slow-moving bed: a bucket elevator lifts each fresh cell to the head of a
lead column, the cells settle down it past four thermoelectric rings (copper-banded
collars, their cold sides finned radiators), and a star valve at the foot lets the
spent ones out into the spent bin. The rings make the current directly; their taps run
down to a combiner cabinet.

  boot (S, ochre, the inserter's loading port) -> bucket elevator (E, buckets climbing
  the open front) -> head chute -> lead column (the bed of cells; the light seen falling
  in four slots between the rings) -> thermoelectric rings (copper, finned) -> taps ->
  combiner cabinet (SW, grey) -> cable trunk (W);  column foot -> star valve (turning)
  -> spent bin (SE, lead).

  $BLENDER -b --python r5b_9_pebble_hopper.py -- <out-dir> [--quick] [--only idle|working]
Not a model; nothing is adopted.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r5b_kit import *  # noqa: E402,F401,F403

W, H = 3, 3
CX, CY, CR = -0.22, 0.22, 0.4         # the column
Z0, Z1 = 0.62, 2.62                   # its shaft
RINGS = (0.95, 1.4, 1.85, 2.3)
EX, EY = 0.98, 0.12                   # the elevator


def column():
    cyl((CX, CY, 0.1), CR + 0.32, 0.2, "dark_steel", verts=64)
    bolts(CX, CY, 0.21, CR + 0.26, 14, r=0.02)
    # the foot: a lead cone into the star valve's housing
    cyl((CX, CY, 0.42), CR + 0.08, 0.44, "lead", verts=64)
    vessel_band(CX, CY, 0.35, CR + 0.08, n_rivets=10, lug_a=-PI / 2 - 0.6)
    cyl((CX, CY, (Z0 + Z1) / 2), CR, Z1 - Z0, "lead", verts=72)
    for i in range(3):                       # the falling light between the rings
        z = (RINGS[i] + RINGS[i + 1]) / 2
        slot_window(CX, CY, CR, -PI / 2 + 0.1, z, 0.36, 0.18, f"fl_bed{i}", k=-1)
    slot_window(CX, CY, CR, -PI / 2 + 0.1, (Z0 + RINGS[0]) / 2 + 0.02, 0.36, 0.14, "fl_bed3", k=-1)
    point((CX, CY - CR - 0.3, 1.6), 6.0, pulse=lambda t: 0.85 + 0.15 * math.sin(2 * PI * t))
    for k, z in enumerate(RINGS):
        cyl((CX, CY, z), CR + 0.07, 0.16, "copper", verts=72)
        for zz in (z - 0.09, z + 0.09):
            cyl((CX, CY, zz), CR + 0.09, 0.03, "dark_steel", verts=72)
        n = 20
        for j in range(n):                   # the cold side: radiating fins
            a = 2 * PI * (j + 0.5 * (k % 2)) / n
            if abs(((a + PI / 2 + PI) % (2 * PI)) - PI) < 0.42:
                continue                     # the slot side kept clear
            box((CX + (CR + 0.25) * math.cos(a), CY + (CR + 0.25) * math.sin(a), z), (0.32, 0.025, 0.2), "grey",
                rz=a, bevel=0.004)
        # the tap: a terminal block on the ring's west side, its cable down
        tx, ty = CX + (CR + 0.12) * math.cos(-2.3), CY + (CR + 0.12) * math.sin(-2.3)
        box((tx, ty, z), (0.12, 0.12, 0.14), "dark_steel", rz=-2.3, bevel=0.006)
    bundle([(CX - 0.38, CY - 0.36, 2.3), (CX - 0.45, CY - 0.42, 1.6), (CX - 0.5, CY - 0.45, 0.9), (-0.95, -0.7, 0.75)],
           cols=("red", "black", "yellow", "black"), r=0.018)
    # the head: a hopper drum, a dished lead lid, the chute in from the elevator
    cyl((CX, CY, Z1 + 0.1), CR + 0.12, 0.2, "dark_steel", verts=64)
    cyl((CX, CY, Z1 + 0.32), CR + 0.08, 0.3, "lead", verts=64)
    head(CX, CY, Z1 + 0.47, CR + 0.08, 0.14, "lead")
    flange_ring(CX, CY, Z1 + 0.47, CR + 0.05, mat="bare", h=0.04, nb=14)
    manway_top(CX - 0.12, CY - 0.05, Z1 + 0.6, r=0.1, nb=8)
    cyl((CX + 0.2, CY + 0.15, Z1 + 0.66), 0.05, 0.14, "bare", verts=12)
    cyl((CX + 0.2, CY + 0.15, Z1 + 0.74), 0.07, 0.04, "brass", verts=6, bevel=0)
    rivet_column(CX, CY, CR, -PI / 2 - 0.75, Z0 + 0.05, RINGS[0] - 0.1)
    id_panel((CX + 0.1, CY - CR - 0.08, 0.5), 0.2, 0.1, stripe="red")
    hazard_tag((CX - 0.12, CY - CR - 0.09, 0.32), 0.24, 0.06)


def star_valve():
    """At the column's foot: the star valve (a rotary feeder), its six-pocket rotor turning
    on an axis toward the camera, a green gear-motor beside it; out its east side the
    chute to the spent bin."""
    vx, vy, vz = CX, CY - 0.5, 0.36
    box((vx, vy + 0.05, vz), (0.4, 0.3, 0.42), "dark_steel", bevel=0.02)
    cyl((vx, vy - 0.11, vz), 0.18, 0.04, "bare", rot=(PI / 2, 0, 0), verts=32)
    S = pivot((vx, vy - 0.14, vz), (PI / 2, 0, 0))
    cyl((0, 0, 0), 0.05, 0.04, "brass", verts=6, bevel=0, parent=S)
    for k in range(6):
        a = 2 * PI * k / 6
        box((0.08 * math.cos(a), 0.08 * math.sin(a), 0), (0.15, 0.028, 0.03), "yellow", rz=a, bevel=0.003, parent=S)
    spin(S, "Z", -1 / 6)
    box((vx - 0.32, vy + 0.05, 0.25), (0.22, 0.22, 0.22), "green", bevel=0.01)
    coupling(vx - 0.2, vy + 0.05, 0.25, 0.06, axis=(1, 0, 0))
    pipe([(vx + 0.2, vy + 0.05, 0.4), (0.4, -0.6, 0.45), (0.62, -0.88, 0.5)], r=0.07, mat="lead")
    # the spent bin
    bx, by = 0.88, -0.98
    box((bx, by, 0.25), (0.62, 0.5, 0.42), "lead", bevel=0.02)
    box((bx, by, 0.47), (0.54, 0.42, 0.03), "dark", bevel=0)
    for k, (dx, dy) in enumerate(((-0.12, -0.05), (0.05, 0.08), (0.15, -0.08))):
        spent_cell((bx + dx, by + dy, 0.52), (1, 0.4 * (k - 1), 0.1), r=0.06, h=0.27)
    box((bx, by - 0.26, 0.22), (0.4, 0.02, 0.08), "hazard", bevel=0)


ELEV_H = 3.0
N_BUCKETS = 16


def elevator():
    """The bucket elevator up the east side: two dark-steel legs, the front run open, the
    boot at the foot (ochre, the loading port) and the head (green, its drive motor); a
    chute from the head into the column's hopper. The buckets climb the front run with
    fresh cells and come down the back empty."""
    for dx in (-0.2, 0.2):
        box((EX + dx, EY + 0.12, ELEV_H / 2 + 0.2), (0.06, 0.06, ELEV_H - 0.2), "dark_steel", bevel=0.006)
    box((EX, EY + 0.2, ELEV_H / 2 + 0.2), (0.36, 0.06, ELEV_H - 0.4), "ochre", bevel=0.006)      # back casing
    for z in [0.6 + 0.45 * i for i in range(6)]:
        box((EX, EY - 0.1, z), (0.44, 0.03, 0.04), "dark_steel", bevel=0.004)                       # front ties
    box((EX, EY, 0.26), (0.56, 0.5, 0.52), "ochre", bevel=0.02)                                      # boot
    box((EX, EY - 0.26, 0.3), (0.3, 0.02, 0.22), "dark", bevel=0)                                    # loading port
    box((EX, EY - 0.27, 0.45), (0.36, 0.02, 0.05), "hazard", bevel=0)
    box((EX, EY + 0.05, ELEV_H + 0.2), (0.5, 0.5, 0.4), "green", bevel=0.02)                         # head
    cyl((EX + 0.05, EY - 0.27, ELEV_H + 0.2), 0.12, 0.1, "dark_steel", rot=(PI / 2, 0, 0), verts=24)
    coupling(EX + 0.05, EY - 0.38, ELEV_H + 0.2, 0.07, axis=(0, -1, 0))
    box((EX + 0.05, EY - 0.56, ELEV_H + 0.2), (0.22, 0.24, 0.22), "green", bevel=0.01)
    box((EX + 0.05, EY - 0.45, ELEV_H - 0.02), (0.08, 0.36, 0.2), "dark_steel")
    pipe([(EX - 0.22, EY + 0.05, ELEV_H + 0.25), (0.45, CY, ELEV_H + 0.15), (CX + CR + 0.05, CY, Z1 + 0.35)],
         r=0.09, mat="lead")
    gauge((EX - 0.1, EY - 0.21, ELEV_H + 0.2), (0, -1, 0.2), r=0.05)
    # the chain of buckets: a loop up the front (y = EY - 0.04) and down the back (EY + 0.14)
    z0, z1 = 0.5, ELEV_H + 0.05
    yf, yb = EY - 0.03, EY + 0.12
    L = 2 * (z1 - z0) + PI * (yb - yf) / 2 * 2
    buckets = []
    for i in range(N_BUCKETS):
        B = pivot((EX, yf, z0))
        box((0, -0.03, 0), (0.24, 0.1, 0.07), "ochre", bevel=0.008, parent=B)
        box((0, -0.075, 0.03), (0.24, 0.015, 0.06), "dark_steel", bevel=0, parent=B)
        first = len(OBJS)
        cell((0, -0.04, 0.06), (1, 0, 0), r=0.04, h=0.18, parent=B)
        buckets.append((B, OBJS[first:], i / N_BUCKETS))
    run_len = z1 - z0
    turn = PI * (yb - yf) / 2

    def pose(t):
        for B, cells, ph in buckets:
            s = ((ph + t / N_BUCKETS * 2) % 1.0) * L       # two pitches a loop
            if s < run_len:                                # up the front
                B.location = (EX, yf, z0 + s)
                up = True
            elif s < run_len + turn:
                a = (s - run_len) / turn * PI
                B.location = (EX, (yf + yb) / 2 - (yb - yf) / 2 * math.cos(a), z1 + 0.05 * math.sin(a))
                up = False
            elif s < 2 * run_len + turn:
                B.location = (EX, yb, z1 - (s - run_len - turn))
                up = False
            else:
                a = (s - 2 * run_len - turn) / turn * PI
                B.location = (EX, (yf + yb) / 2 + (yb - yf) / 2 * math.cos(a), z0 - 0.05 * math.sin(a))
                up = False
            for o in cells:
                o.hide_render = not up
    ANIM.append(pose)


def combiner():
    """The combiner cabinet (grey) in the south-west: the rings' taps in, the output meter,
    the cable trunk out the west side."""
    kx, ky = -1.0, -0.95
    box((kx, ky, 0.45), (0.7, 0.56, 0.9), "grey", bevel=0.02)
    box((kx, ky, 0.92), (0.74, 0.6, 0.05), "dark_steel", bevel=0.008)
    meter((kx + 0.1, ky - 0.29, 0.6), (0, -1, 0.1), r=0.11,
          swing=lambda t: 0.15 + 0.06 * math.sin(2 * PI * t) + 0.03 * math.sin(8 * PI * t))
    for i in range(3):
        box((kx - 0.18, ky - 0.29, 0.28 + 0.07 * i), (0.22, 0.02, 0.025), "dark_steel", bevel=0)
    status_lamp(kx + 0.2, ky - 0.1, 0.97)
    id_panel((kx - 0.18, ky - 0.29, 0.62), 0.18, 0.1, stripe="yellow")
    for k, dy in enumerate((-0.12, 0.08)):
        hose([(kx - 0.35, ky + dy, 0.5), (-1.42, ky + dy + 0.05, 0.4), (-1.47, ky + dy + 0.1, 0.1),
              (-1.49, ky + dy + 0.12, -0.05)], r=0.06, mat="hose_k")


def dressing():
    """North-west: the cell crate and a hose reel; a valve and the instrument air line."""
    barrels(-1.15, 1.15, n=3, seed=3)
    box((0.95, 1.2, 0.2), (0.5, 0.4, 0.4), "oxide", bevel=0.015)
    gauge((0.95, 0.99, 0.28), (0, -1, 0.2), r=0.045)
    hose([(0.95, 1.2, 0.42), (0.7, 1.0, 0.7), (CX + 0.35, CY + 0.3, 0.8)], r=0.05, mat="hose")
    valve(-1.2, 0.35, 0.0, 0.42, wheel="red")
    jbox(0.3, 1.15, 0.3, 0.24, 0.32, mat="green")


column()
star_valve()
elevator()
combiner()
dressing()
stain(CX, CY - 0.6, 0.35, 0.12)
stain(0.95, -0.35, 0.2, 0.2)
stain(-1.2, -1.4, 0.25, 0.1)
run(W, H, rise=2.0, name="9-the-pebble-column")
