"""Radiant Generator, round 5, suggestion 3: THE CAROUSEL COLLECTOR (5 x 5).

  $BLENDER -b --python r5a_3_carousel.py -- <out-dir> [--quick] [--only working|idle] [--colourmap]

Direct collection. The chain, cell to wire: cells go into the lead loading hopper on the
west and drop into the pockets of a great turning magazine, eight lead-capped pockets
on a ring-geared turntable; the turntable indexes an eighth of a turn each cycle, so
every cell comes round in turn under the collector head on the south side; the head's
charge collector takes the cell's emission straight off as current (its window lights
as each cell arrives, and dims as the table moves); the copper bus carries it to the
capacitor bank and the transformer, then the armoured trunks. Spent cells leave on the
north side into the lead spent-cell bin. The drive is a geared motor on the east
pinion; the collector's heat goes from its finned hood. The isotope's light shows only
in the collector head's window.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r5a_kit import *  # noqa: F401,F403,E402
import r5a_kit as K  # noqa: E402

TX, TY = -0.25, 0.35            # the turntable's centre
RR, RP = 1.55, 1.02             # its rim radius, the pockets' radius
ZD = 0.5                        # the deck's top
HOLD = 0.55


def lit(t):
    """The window: full while a cell sits under the head, dimming as the table moves."""
    if t < HOLD:
        return 0.9 + 0.1 * math.sin(2 * PI * t / HOLD * 2)
    u = (t - HOLD) / (1 - HOLD)
    return 0.25 + 0.75 * (math.cos(2 * PI * u) * 0.5 + 0.5) ** 2


K.build_materials(((0.4, 0.3), (0.95, 0.35), (1.3, 0.3)))
radiant("rg_window", "swirl", scale=4.0, k=1, bright=2.4, fn=lit, arms=3)


def turntable():
    # the fixed base ring and its bolted foot
    annulus((TX, TY, 0.12), RR - 0.35, RR + 0.12, 0.24, "dark_steel", seg=96)
    for k in range(24):
        a = 2 * PI * k / 24
        cyl((TX + (RR + 0.06) * math.cos(a), TY + (RR + 0.06) * math.sin(a), 0.25), 0.022, 0.025, "bolt", verts=6,
            bevel=0)
    # the turning table: a lead-lined deck, the ring gear, eight pockets, rim marks
    piv = pivot((TX, TY, 0.0))
    cyl((0, 0, 0.38), RR, 0.24, "lead_new", verts=96, parent=piv)
    cyl((0, 0, 0.27), RR + 0.04, 0.05, "bare", verts=96, parent=piv)
    for k in range(64):                                      # the ring gear's teeth
        a = 2 * PI * k / 64
        box(((RR + 0.05) * math.cos(a), (RR + 0.05) * math.sin(a), 0.38), (0.07, 0.05, 0.16), "dark_steel",
            rz=a, bevel=0.004, parent=piv)
    for k in range(8):
        a = 2 * PI * k / 8 + PI / 8
        px, py = RP * math.cos(a), RP * math.sin(a)
        cyl((px, py, ZD + 0.04), 0.26, 0.08, "dark_steel", verts=32, parent=piv)
        cyl((px, py, ZD + 0.12), 0.2, 0.1, "lead", verts=32, parent=piv)
        bolts(px, py, ZD + 0.09, 0.23, 8, r=0.013, parent=piv)
        torus((px, py, ZD + 0.19), 0.05, 0.012, "yellow", rot=(PI / 2, 0, a), seg=12, parent=piv)
        b = a + PI / 8                                       # rim marks between the pockets
        box(((RR - 0.12) * math.cos(b), (RR - 0.12) * math.sin(b), ZD + 0.005), (0.22, 0.07, 0.012), "hazard",
            rz=b, bevel=0, parent=piv)
        box((0.62 * math.cos(b), 0.62 * math.sin(b), ZD + 0.01), (0.3, 0.04, 0.02), "seam", rz=b, bevel=0,
            parent=piv)
    spin(piv, 1 / 8, ease=lambda t: ease_index(t, HOLD))
    # the fixed hub: a lead dome over the centre bearing, a stencil band, a manway
    cyl((TX, TY, ZD + 0.2), 0.52, 0.4, "lead", verts=64)
    head(TX, TY, ZD + 0.4, 0.52, 0.3, "lead")
    vessel_band(TX, TY, ZD + 0.25, 0.52, n_rivets=12)
    manway_top(TX + 0.12, TY + 0.1, ZD + 0.66, r=0.12, nb=8)
    status_lamp(TX - 0.2, TY - 0.15, ZD + 0.64)
    ladder(TX + 0.42, TY - 0.38, ZD, ZD + 0.55, axis="x", mat="ochre")
    label(2, "turning magazine: 8 lead-capped pockets", (TX + RP * math.cos(PI * 0.62), TY + RP * math.sin(PI * 0.62),
                                                            ZD + 0.2))


def drive():
    """The east pinion: a geared motor turning the ring gear, its coupling seen moving."""
    gx = TX + RR + 0.32
    gy = TY - 0.2
    skid(gx - 0.25, gy - 0.75, gx + 0.45, gy + 0.3, 0.12)
    box((gx, gy, 0.38), (0.32, 0.36, 0.5), "dark_steel")                  # the gearbox
    pin = pivot((gx - 0.14, gy, 0.38))
    for k in range(10):
        a = 2 * PI * k / 10
        box((0.1 * math.cos(a), 0.1 * math.sin(a), 0), (0.06, 0.04, 0.14), "bare", rz=a, bevel=0, parent=pin)
    spin(pin, 2, ease=lambda t: ease_index(t, HOLD))      # whole turns: the loop closes
    end = motor(gx + 0.12, gy - 0.48, 0.42, d=(0, 1), s=0.85)
    coupling(gx + 0.12, gy - 0.22, 0.42, 0.11, axis=(0, 1, 0), turns=3, ease=lambda t: ease_index(t, HOLD))
    id_panel((gx, gy - 0.185, 0.45), 0.2, 0.12, stripe="green")
    bundle([(gx + 0.12, gy - 0.48, 0.62), (gx + 0.4, gy - 0.9, 0.3), (1.95, -1.25, 0.2)], cols=("black", "red"))
    label(3, "drive: geared motor, pinion on the ring gear", (gx + 0.12, gy - 0.48, 0.6))


def collector():
    """The collector head over the south pocket: an oxide hooded bridge, finned, its
    window on the south face; behind it the copper bus to the bank."""
    hx, hy = TX, TY - RP
    for s in (-1, 1):                                       # the bridge's two legs, off the table
        box((hx + s * 0.55, hy - 0.42, 0.55), (0.18, 0.24, 1.1), "oxide")
    box((hx, hy - 0.05, 1.08), (1.3, 0.8, 0.26), "oxide", bevel=0.02)
    box((hx, hy - 0.05, 0.86), (0.7, 0.62, 0.3), "oxide", bevel=0.02)
    for k in range(9):                                      # the hood's radiating fins
        box((hx - 0.48 + 0.12 * k, hy + 0.05, 1.3), (0.035, 0.6, 0.2), "grey", bevel=0.004)
    # the window: a bolted bullseye frame, the cell's light behind thick glass
    wy = hy - 0.47
    cyl((hx, wy, 0.86), 0.3, 0.06, "dark_steel", rot=(PI / 2, 0, 0), verts=40)
    win = cyl((hx, wy - 0.035, 0.86), 0.24, 0.02, "rg_window", rot=(PI / 2, 0, 0), verts=40, bevel=0)
    cyl((hx, wy - 0.05, 0.86), 0.24, 0.012, "pane", rot=(PI / 2, 0, 0), verts=40, bevel=0)
    for k in range(10):
        a = 2 * PI * k / 10
        cyl((hx + 0.27 * math.cos(a), wy - 0.04, 0.86 + 0.27 * math.sin(a)), 0.014, 0.02, "bolt",
            rot=(PI / 2, 0, 0), verts=6, bevel=0)
    for s in (-1, 1):                                       # lead louvres beside the window
        for z in (0.76, 0.86, 0.96):
            box((hx + s * 0.4, wy + 0.04, z), (0.14, 0.03, 0.04), "lead_new", bevel=0.003)
    gauge((hx + 0.48, hy - 0.46, 1.08), (0, -1, 0.2), r=0.07, live=lambda t: 0.4 * (lit(t) - 0.6))
    hazard_tag((hx, hy - 0.455, 1.15), 0.9, 0.05)
    id_panel((hx - 0.45, hy - 0.455, 1.06), 0.2, 0.1, stripe="red")
    label(4, "collector head: the cell's emission taken off as current", (hx, wy, 1.0))
    # the copper bus off the head's east side, on stand-off insulators, to the bank
    bus = [(hx + 0.65, hy - 0.05, 1.1), (0.9, -1.0, 1.0), (1.35, -1.35, 0.95), (1.5, -1.55, 0.9)]
    for dz in (0.0, 0.08):
        pipe([(x, y, z + dz) for x, y, z in bus], r=0.025, mat="copper", flanges=False)
    for (px, py) in ((0.9, -1.0), (1.3, -1.32)):
        cyl((px, py, 0.45), 0.03, 0.9, "dark_steel", verts=8)
        cyl((px, py, 0.92), 0.05, 0.08, "ceramic", verts=12)
    label(5, "copper bus", (0.9, -1.0, 1.05))


def bank():
    """The capacitor bank (green cans) and the transformer (grey, finned), at the south-east."""
    skid(0.85, -2.45, 2.45, -1.55, 0.12)
    for k in range(3):
        x = 1.05 + 0.32 * k
        cyl((x, -2.15, 0.5), 0.14, 0.76, "green", verts=32)
        head(x, -2.15, 0.88, 0.14, 0.05, "dark_steel")
        cyl((x, -2.15, 0.96), 0.03, 0.08, "ceramic", verts=12)
        cyl((x, -2.15, 1.02), 0.02, 0.04, "copper", verts=8)
        torus((x, -2.15, 0.3), 0.143, 0.012, "dark_steel", seg=32)
    pipe([(1.05, -2.15, 1.02), (1.69, -2.15, 1.02)], r=0.018, mat="copper", flanges=False)
    # transformer: a grey tank with radiating fin panels down both flanks
    box((2.0, -1.95, 0.55), (0.6, 0.62, 0.86), "grey", bevel=0.02)
    for s in (-1, 1):
        for k in range(6):
            box((2.0 + s * 0.36, -2.2 + 0.1 * k, 0.5), (0.12, 0.025, 0.66), "grey", bevel=0.004)
    for k in range(3):
        cyl((1.85 + 0.15 * k, -1.85, 1.05), 0.04, 0.14, "ceramic", verts=12)
    gauge((2.0, -2.27, 0.75), (0, -1, 0.1), r=0.06, live=lambda t: 0.15 * math.sin(2 * PI * 2 * t))
    id_panel((2.0, -2.265, 0.5), 0.26, 0.12, stripe="yellow")
    trunk([(2.15, -1.7, 0.8), (2.3, -1.3, 0.5), (2.47, -1.1, 0.1)], r=0.065)
    trunk([(2.25, -1.8, 0.6), (2.4, -1.5, 0.3), (2.48, -1.4, 0.08)], r=0.06)
    label(6, "capacitor bank and transformer", (1.4, -2.15, 0.9))
    label(7, "armoured trunks: the wire", (2.35, -1.4, 0.4))


def feed():
    """The loading hopper on the west pocket, the spent-cell bin on the north."""
    a = PI                                                   # west
    px, py = TX + RP * math.cos(a) - 0.05, TY
    box((px - 0.55, py, 0.55), (0.55, 0.62, 1.1), "lead", bevel=0.025)
    box((px - 0.55, py, 1.12), (0.62, 0.7, 0.06), "dark_steel")
    cone((px - 0.55, py, 1.32), 0.26, 0.12, 0.34, "lead_new", verts=8)
    box((px - 0.15, py, 0.86), (0.4, 0.3, 0.1), "lead_new", rot=(0, 0.45, 0))
    box((px - 0.55, py - 0.315, 0.6), (0.4, 0.02, 0.08), "hazard", bevel=0)
    id_panel((px - 0.55, py - 0.315, 0.82), 0.22, 0.12, stripe="green")
    label(1, "cells in: the loading hopper", (px - 0.55, py, 1.4))
    # the spent bin, north, lead, with a chute from the north pocket
    bx, by = TX + 0.1, 2.2
    box((bx, by, 0.35), (0.85, 0.48, 0.7), "lead", bevel=0.02)
    box((bx, by, 0.72), (0.9, 0.52, 0.05), "dark_steel")
    handwheel((bx + 0.25, by, 0.82), 0.1)
    box((bx - 0.1, by - 0.35, 0.62), (0.3, 0.3, 0.08), "lead_new", rot=(-0.4, 0, 0))
    label(8, "spent cells out: the lead bin", (bx, by, 0.75))


def clutter():
    # a coolant-free machine: the clutter is power and service gear
    jbox(-2.05, -1.0, mat="grey")
    jbox(-2.05, -1.45, w=0.26, mat="green")
    bundle([(-2.05, -1.0, 0.42), (-1.7, -1.7, 0.2), (-0.6, -2.1, 0.18), (0.85, -2.0, 0.2)],
           cols=("black", "red", "yellow"))
    bundle([(-2.05, -1.45, 0.4), (-1.9, -0.3, 0.25), (-1.6, 0.3, 0.6)], cols=("grey", "black"))
    for k, (x, y) in enumerate(((-2.1, 1.9), (-1.85, 2.1), (-2.15, 1.55))):
        cyl((x, y, 0.19), 0.12, 0.38, ("lead", "grey", "hazard")[k], verts=24)
        for zz in (0.1, 0.28):
            torus((x, y, zz), 0.122, 0.011, "bare", seg=24)
    valve(1.0, 1.6, 0.0, 0.5, wheel="red")
    hose([(1.0, 1.6, 0.25), (0.9, 1.3, 0.2), (TX + 0.5, TY + 0.55, ZD + 0.35)], r=0.05, mat="hose_k")
    reel_x, reel_y = 1.75, 1.2
    box((reel_x, reel_y, 0.12), (0.5, 0.5, 0.24), "dark_steel")
    for s in (-1, 1):
        cyl((reel_x + s * 0.17, reel_y, 0.42), 0.27, 0.03, "green", rot=(0, PI / 2, 0), verts=32)
    cyl((reel_x, reel_y, 0.42), 0.2, 0.3, "hose_k", rot=(0, PI / 2, 0), verts=32)
    for k in range(5):
        torus((reel_x - 0.12 + 0.06 * k, reel_y, 0.42), 0.2, 0.035, "hose_k", rot=(0, PI / 2, 0), seg=24)
    stain(TX, TY - RR - 0.3, 0.7, 0.18)
    stain(1.4, -0.4, 0.3, 0.2)
    stain(-1.95, 0.5, 0.2, 0.4)
    stain(1.7, -2.4, 0.5, 0.1)


turntable()
drive()
collector()
bank()
feed()
clutter()
run(dict(name="the carousel collector", footprint=[5, 5]), nf=24)
