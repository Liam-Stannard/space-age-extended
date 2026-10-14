"""Radiant Generator, round 5, suggestion 5: THE CHOPPER WHEEL (3 x 3). Replaces the
heat-pipe spider of the starting list (the spider's converter pods have to be one of the
other conversions, so it repeats 1 or 2; the chopper's moving part is the conversion).

  $BLENDER -b --python r5a_5_chopper.py -- <out-dir> [--quick] [--only working|idle] [--colourmap]

Direct collection, chopped into alternating current. The chain, cell to wire: two cells
go into the lead cask through its two charging plugs; their emission leaves the cask
only through one bolted window on its south face; in front of the window turns the
chopper wheel, copper collector sectors between open slots: each sector catches the
emission as it crosses the window and the slots let it by, so the brushes at the hub
and rim take off a current that rises and falls with every sector -- alternating
current made by the turning wheel itself; the drive motor turns it through a right-
angle gearbox; the current goes up the finned transformer and out on the armoured
trunks. The isotope's light shows only through the wheel's slots as they pass the
window: a flicker that is the generator's frequency.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r5a_kit import *  # noqa: F401,F403,E402
import r5a_kit as K  # noqa: E402

KX, KY, KR, KH = -0.2, 0.62, 0.66, 1.3
WX, WY, WZ, WR = -0.2, -0.3, 0.74, 0.6      # the wheel: centre and radius (axis north-south)
NS = 8                                        # sectors
K.build_materials(((0.5, 0.3), (1.0, 0.35), (1.3, 0.3)))
radiant("rg_window", "swirl", scale=3.0, k=1, bright=2.6, fn=lambda t: 0.9 + 0.1 * math.sin(2 * PI * 3 * t),
        arms=4)


def cask():
    cyl((KX, KY, 0.08), KR + 0.12, 0.16, "dark_steel", verts=64)
    bolts(KX, KY, 0.17, KR + 0.07, 16)
    cyl((KX, KY, KH / 2 + 0.08), KR, KH - 0.16, "lead", verts=64)
    for z in (0.3, 1.18):
        vessel_band(KX, KY, z, KR, n_rivets=14, lug_a=-PI / 2 + 0.9)
    head(KX, KY, KH, KR + 0.02, 0.2, "lead")
    flange_ring(KX, KY, KH + 0.01, KR - 0.02, mat="bare", h=0.05, nb=18)
    for s in (-1, 1):                         # the two charging plugs
        px, py = KX + s * 0.26, KY + 0.12
        cyl((px, py, KH + 0.18), 0.13, 0.1, "dark_steel", verts=32)
        cyl((px, py, KH + 0.25), 0.11, 0.05, "lead_new", verts=32)
        bolts(px, py, KH + 0.28, 0.085, 6, r=0.012)
        torus((px, py, KH + 0.31), 0.04, 0.01, "yellow", rot=(PI / 2, 0, 0), seg=12)
    # the window: a square cast frame on a flat boss on the south face, the light behind glass
    by = KY - KR + 0.06
    box((KX, by - 0.06, WZ), (0.98, 0.16, 0.98), "lead", bevel=0.03)
    box((KX, by - 0.15, WZ), (0.9, 0.04, 0.9), "dark_steel", bevel=0.01)
    cyl((KX, by - 0.17, WZ), WR - 0.08, 0.02, "rg_window", rot=(PI / 2, 0, 0), verts=48, bevel=0)
    for k in range(16):
        a = 2 * PI * k / 16
        cyl((KX + 0.42 * math.cos(a) * 1.0, by - 0.18, WZ + 0.42 * math.sin(a)), 0.014, 0.02, "bolt",
            rot=(PI / 2, 0, 0), verts=6, bevel=0)
    status_lamp(KX + 0.35, KY - 0.2, KH + 0.16)
    label(1, "cells in: two charging plugs", (KX, KY + 0.12, KH + 0.3))
    label(2, "lead cask: one window, the emission's only way out", (KX - 0.55, KY - 0.2, 1.0))


def wheel():
    """The chopper: eight copper collector sectors between open slots, a lead rim, a hub
    with slip rings, turning in front of the window about a north-south axis."""
    piv = pivot((WX, WY, WZ), (PI / 2, 0, 0))
    span = 2 * PI / NS
    for k in range(NS):
        a0 = k * span
        sector((0, 0, 0), 0.16, WR - 0.06, a0, a0 + span * 0.55, 0.04, "copper", seg=6, parent=piv)
        # a radial stiffening rib down each sector
        a = a0 + span * 0.275
        box(((WR / 2 + 0.05) * math.cos(a), (WR / 2 + 0.05) * math.sin(a), -0.03), (WR - 0.22, 0.03, 0.03),
            "dark_steel", rz=a, bevel=0.003, parent=piv)
    annulus((0, 0, 0), WR - 0.07, WR, 0.07, "lead_new", seg=64, parent=piv)
    for k in range(NS * 2):
        a = 2 * PI * k / (NS * 2)
        cyl(((WR - 0.035) * math.cos(a), (WR - 0.035) * math.sin(a), -0.04), 0.012, 0.02, "bolt", verts=6,
            bevel=0, parent=piv)
    cyl((0, 0, 0), 0.18, 0.1, "dark_steel", verts=32, parent=piv)
    cyl((0, 0, -0.07), 0.12, 0.06, "brass", verts=32, parent=piv)
    bolts(0, 0, -0.1, 0.09, NS, r=0.014, parent=piv)
    spin(piv, 3 / NS)                     # three sectors past the window a loop
    # the guard: a dark-steel half shroud over the wheel's lower half and its feet
    sector((WX, WY + 0.02, WZ), WR + 0.02, WR + 0.12, PI + 0.15, 2 * PI - 0.15, 0.24, "dark_steel",
           rot=(PI / 2, 0, 0), seg=24)
    for s in (-1, 1):
        box((WX + s * 0.5, WY + 0.02, 0.18), (0.2, 0.3, 0.36), "dark_steel", bevel=0.01)
    box((WX, WY - 0.12, 0.2), (0.7, 0.03, 0.08), "hazard", bevel=0)
    # the brushes: a rim brush box at the top, the hub brushes on the gearbox
    box((WX, WY + 0.0, WZ + WR + 0.08), (0.22, 0.2, 0.12), "dark_steel", bevel=0.008)
    for dx in (-0.06, 0.0, 0.06):
        box((WX + dx, WY + 0.0, WZ + WR + 0.01), (0.035, 0.06, 0.06), "dark", bevel=0)
    label(3, "the chopper wheel: copper sectors catch it, slots let it by", (WX + 0.35, WY, WZ + 0.35))


def drive():
    """A right-angle gearbox on the wheel's axle, the motor beside it to the east."""
    gy = WY - 0.18
    box((WX, gy, WZ), (0.24, 0.16, 0.24), "dark_steel", bevel=0.012)
    bolts_ = [(WX + 0.09 * s, gy - 0.085, WZ + 0.09 * u) for s in (-1, 1) for u in (-1, 1)]
    for b in bolts_:
        cyl(b, 0.014, 0.02, "bolt", rot=(PI / 2, 0, 0), verts=6, bevel=0)
    box((WX, gy - 0.02, WZ - 0.42), (0.16, 0.14, 0.6), "dark_steel")
    cyl((WX + 0.25, gy, WZ), 0.04, 0.3, "bare", rot=(0, PI / 2, 0), verts=12)
    coupling(WX + 0.33, gy, WZ, 0.1, axis=(1, 0, 0), turns=3)
    box((WX + 0.72, gy, WZ - 0.4), (0.46, 0.3, 0.6), "dark_steel")
    motor(WX + 0.66, gy, WZ, d=(-1, 0), s=0.85, mat="green")
    gauge((WX + 0.68, gy - 0.16, WZ - 0.25), (0, -1, 0.15), r=0.055, live=lambda t: 0.2 * math.sin(2 * PI * 3 * t))
    label(4, "drive: motor, coupling, right-angle gearbox", (WX + 0.66, gy, WZ + 0.2))


def transformer():
    tx, ty = 1.0, 0.68
    box((tx, ty, 0.55), (0.62, 0.66, 0.9), "oxide", bevel=0.02)
    for s in (-1, 1):
        for k in range(6):
            box((tx + s * 0.37, ty - 0.27 + 0.108 * k, 0.5), (0.13, 0.025, 0.7), "oxide", bevel=0.004)
    box((tx, ty, 1.03), (0.66, 0.7, 0.06), "dark_steel")
    for k in range(3):
        cyl((tx - 0.18 + 0.18 * k, ty - 0.1, 1.14), 0.04, 0.16, "ceramic", verts=12)
        cyl((tx - 0.18 + 0.18 * k, ty - 0.1, 1.24), 0.02, 0.04, "copper", verts=8)
    cyl((tx + 0.15, ty + 0.2, 1.16), 0.1, 0.2, "grey", verts=24)              # conservator
    id_panel((tx, ty - 0.335, 0.7), 0.26, 0.12, stripe="yellow")
    hazard_tag((tx, ty - 0.335, 0.92), 0.5, 0.05)
    gauge((tx - 0.2, ty - 0.34, 0.5), (0, -1, 0.1), r=0.06, live=lambda t: 0.1 * math.sin(2 * PI * 3 * t))
    # the brushes' leads up to the transformer
    trunk([(WX + 0.1, WY + 0.05, WZ + WR + 0.14), (0.3, 0.1, 1.45), (0.82, 0.58, 1.3)], r=0.04)
    trunk([(WX + 0.0, WY - 0.3, WZ - 0.3), (0.45, -0.4, 0.3), (0.7, 0.3, 0.3), (0.75, 0.5, 0.45)], r=0.04)
    # the wire out, east edge
    trunk([(tx + 0.25, ty + 0.15, 0.9), (1.38, 0.85, 0.5), (1.48, 0.95, 0.08)], r=0.06)
    trunk([(tx + 0.28, ty - 0.1, 0.75), (1.4, 0.25, 0.4), (1.48, 0.2, 0.08)], r=0.06)
    label(5, "transformer: the chopped current stepped up", (tx, ty, 1.05))
    label(6, "armoured trunks: the wire", (1.42, 0.6, 0.4))


def clutter():
    # the spent-cell drawer on the west, a lead box under a chute from the cask
    box((-1.15, -0.55, 0.2), (0.5, 0.5, 0.4), "lead", bevel=0.02)
    box((-1.15, -0.81, 0.2), (0.38, 0.02, 0.1), "hazard", bevel=0)
    handwheel((-1.15, -0.55, 0.48), 0.1)
    pipe([(KX - 0.5, KY - 0.35, 0.45), (-0.95, -0.25, 0.5), (-1.1, -0.45, 0.42)], r=0.065, mat="lead_new")
    label(7, "spent cells out", (-1.15, -0.55, 0.45))
    bundle([(KX - 0.4, KY - 0.5, 1.2), (-1.0, 0.0, 0.5), (-0.95, -0.75, 0.2), (-0.4, -1.05, 0.15),
            (WX + 0.66, WY - 0.3, 0.3)], cols=("black", "red", "yellow"))
    jbox(1.15, -1.0, mat="grey")
    bundle([(1.15, -1.0, 0.42), (1.2, -0.3, 0.2), (1.0, 0.25, 0.3)], cols=("grey", "black"))
    valve(-1.2, 1.15, 0.0, 0.45, wheel="red")
    ladder(KX - KR * 0.7 - 0.05, KY + KR * 0.7 + 0.05, 0.2, KH, axis="y", mat="ochre")
    id_panel((KX - 0.45, KY - KR * 0.75, 1.0), 0.18, 0.1, stripe="red")
    stain(WX, WY - 0.3, 0.55, 0.15)
    stain(-1.15, -0.85, 0.3, 0.1)
    stain(1.0, 0.25, 0.4, 0.12)


cask()
wheel()
drive()
transformer()
clutter()
run(dict(name="the chopper wheel", footprint=[3, 3]), nf=24)
