"""Radiant Generator, round 5, suggestion 4: THE THERMIONIC GANTRY (5 x 3, long axis east-west).

  $BLENDER -b --python r5a_4_gantry.py -- <out-dir> [--quick] [--only working|idle] [--colourmap]

Heat to current with no moving part in the conversion, and a crane to feed it. The
chain, cell to wire: cells wait in the lead magazine at the east end (two cells: the
fuel slots); the overhead gantry picks one, runs west along its rails and lowers it
into a well of the long lead crucible; the crucible's heat drives two rows of
thermionic converter tubes standing along its flanks (hot emitter down in the
crucible's side wells, where the isotope's light shows through the glass; the copper
collector cap on top, finned to radiate its heat); the caps are bussed in copper to the
inverter at the west end, then the transformer and the armoured trunks. Caesium for the
tubes comes from the cream reservoir at the north-east.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r5a_kit import *  # noqa: F401,F403,E402
import r5a_kit as K  # noqa: E402

CY0, CY1, CZ = -0.18, 0.38, 0.62        # the crucible's south and north faces, its top
TUBES_X = [-1.62, -1.1, -0.58, -0.06, 0.46, 0.98]
ROWS_Y = [0.72, -0.52]
WELLS_X = [-1.36, -0.84, -0.32, 0.2, 0.72]
TARGET = -0.32                          # the well the gantry serves this loop
XM = 1.86                               # the magazine's pick point
ZR = 1.30                               # rail height (rise kept near +0.66)


def phase(t, k):
    """A chase along the rows, west to east, as the cell's heat spreads from its well."""
    u = (t * 2 - (TUBES_X[k] - TARGET) * 0.25) % 1.0
    return 0.55 + 0.45 * (0.5 + 0.5 * math.cos(2 * PI * u))


K.build_materials(((0.35, 0.25), (0.62, 0.3)))
for k in range(len(TUBES_X)):
    radiant(f"rg_tube{k}", "flow", scale=7.0, k=2, bright=2.4, fn=(lambda kk: (lambda t: phase(t, kk)))(k))


def well_glow(t):
    """The served well glows while its lid is off: from lowering to release."""
    return 1.0 if 0.44 <= t < 0.66 else 0.0


radiant("rg_well", "swirl", scale=5.0, k=1, bright=2.4, fn=well_glow)


def crucible():
    box((-0.38, (CY0 + CY1) / 2, 0.06), (3.3, 0.86, 0.12), "dark_steel")
    box((-0.38, (CY0 + CY1) / 2, CZ / 2 + 0.06), (3.2, CY1 - CY0, CZ - 0.12), "lead", bevel=0.03)
    for xx in (-1.85, -0.58, 0.68):
        box((xx, (CY0 + CY1) / 2, CZ / 2 + 0.06), (0.08, CY1 - CY0 + 0.05, CZ - 0.1), "bare", bevel=0.006)
    box((-0.38, (CY0 + CY1) / 2, CZ + 0.02), (3.24, CY1 - CY0 + 0.06, 0.07), "dark_steel", bevel=0.01)
    for x in WELLS_X:
        cyl((x, (CY0 + CY1) / 2, CZ + 0.08), 0.17, 0.08, "lead_new", verts=32)
        if x == TARGET:
            cyl((x, (CY0 + CY1) / 2, CZ + 0.125), 0.11, 0.01, "rg_well", verts=32, bevel=0)
            lid = [cyl((x, (CY0 + CY1) / 2, CZ + 0.13), 0.12, 0.03, "grey", verts=24)]
            n0 = len(OBJS)
            bolts(x, (CY0 + CY1) / 2, CZ + 0.15, 0.09, 6, r=0.011)
            lid += OBJS[n0:]

            def pose(t, on, lid=lid):
                for o in lid:
                    o.hide_render = on and well_glow(t) > 0
            ANIM.append(pose)
        else:
            cyl((x, (CY0 + CY1) / 2, CZ + 0.13), 0.12, 0.03, "grey", verts=24)
            bolts(x, (CY0 + CY1) / 2, CZ + 0.15, 0.09, 6, r=0.011)
    stencil((-1.2, CY0 - 0.005, 0.32), (0.5, 0.01, 0.1))
    hazard_tag((0.3, CY0 - 0.005, 0.5), 0.9, 0.05)
    id_panel((-0.2, CY0 - 0.005, 0.3), 0.22, 0.12, stripe="red")
    label(3, "lead crucible: the cell's heat", (-1.2, CY0, 0.45))


def tubes():
    for row, y in enumerate(ROWS_Y):
        side = 1 if y > 0 else -1
        for k, x in enumerate(TUBES_X):
            box((x, y - side * 0.2, 0.3), (0.16, 0.26, 0.2), "lead_new", bevel=0.01)    # the arm into the crucible
            cyl((x, y, 0.12), 0.15, 0.24, "dark_steel", verts=24)
            bolts(x, y, 0.25, 0.12, 6, r=0.012)
            cyl((x, y, 0.62), 0.11, 0.74, "glass", verts=32, bevel=0)
            cyl((x, y, 0.42), 0.075, 0.32, f"rg_tube{k}", verts=24, bevel=0)
            cyl((x, y, 0.7), 0.018, 0.5, "bare", verts=8, bevel=0)
            for z in (0.27, 0.6):
                torus((x, y, z), 0.112, 0.012, "bare", seg=24)
            cyl((x, y, 1.02), 0.12, 0.1, "copper", verts=24)
            for j in range(8):
                a = 2 * PI * j / 8 + 0.2
                box((x + 0.15 * math.cos(a), y + 0.15 * math.sin(a), 1.04), (0.12, 0.018, 0.16), "copper", rz=a,
                    bevel=0.003)
            cyl((x, y, 1.1), 0.03, 0.06, "ceramic", verts=12)
        # the row's collector bus on stand-offs over the caps
        xs = [TUBES_X[0] - 0.55] + TUBES_X
        pipe([(xx, y, 1.16) for xx in (xs[0], xs[-1])], r=0.03, mat="copper", flanges=False)
        for xx in TUBES_X:
            cyl((xx, y, 1.14), 0.012, 0.06, "copper", verts=8, bevel=0)
        # the caesium feed manifold along the row's foot
        pipe([(TUBES_X[0], y + side * 0.2, 0.12), (TUBES_X[-1] + 0.3, y + side * 0.2, 0.12)], r=0.028, mat="bare")
        for xx in TUBES_X:
            cyl((xx, y + side * 0.15, 0.12), 0.012, 0.1, "bare", rot=(PI / 2, 0, 0), verts=6, bevel=0)
    label(4, "thermionic tubes: hot emitter below, copper collector cap", (TUBES_X[2], ROWS_Y[1], 0.8))
    label(5, "collector bus (copper)", (TUBES_X[0], ROWS_Y[0], 1.16))


def magazine():
    x = XM
    box((x, 0.1, 0.42), (0.72, 0.9, 0.84), "lead", bevel=0.03)
    box((x, 0.1, 0.86), (0.78, 0.96, 0.06), "dark_steel")
    for yy in (-0.12, 0.32):                    # the two cell bores (the two fuel slots)
        cyl((x, yy, 0.9), 0.15, 0.05, "lead_new", verts=32)
        cyl((x, yy, 0.93), 0.1, 0.02, "dark", verts=24, bevel=0)
    box((x, -0.36, 0.5), (0.5, 0.02, 0.1), "hazard", bevel=0)
    id_panel((x - 0.15, -0.355, 0.7), 0.2, 0.1, stripe="green")
    label(1, "cells in: the lead magazine", (x, 0.1, 0.95))


CELL = []


def gantry():
    # the rails on their posts, north and south, the length of the building
    for y in (-1.3, 1.3):
        box((0.0, y, ZR), (4.9, 0.12, 0.1), "ochre", bevel=0.01)
        box((0.0, y, ZR + 0.07), (4.9, 0.05, 0.04), "bare", bevel=0.004)
        for x in (-2.38, -0.1, 2.38):
            box((x, y, ZR / 2), (0.14, 0.14, ZR), "ochre", bevel=0.012)
            box((x, y, 0.06), (0.32, 0.3, 0.12), "dark_steel")
            box((x - 0.18 * (1 if x > 0 else -1), y, ZR - 0.3), (0.42, 0.06, 0.06), "ochre",
                rot=(0, 0.7 * (1 if x > 0 else -1), 0), bevel=0.004)
    for x in (-2.38, 2.38):
        box((x, 0, ZR - 0.05), (0.1, 2.64, 0.08), "ochre", bevel=0.008)
    # the bridge, the trolley and the hoist: posed per frame
    br = pivot((XM, 0, 0))
    yt = (CY0 + CY1) / 2
    for s in (-1, 1):
        box((0, s * 1.3, ZR + 0.16), (0.36, 0.2, 0.2), "ochre", bevel=0.015, parent=br)          # end trucks
        cyl((0.1, s * 1.3, ZR + 0.12), 0.06, 0.22, "dark_steel", rot=(PI / 2, 0, 0), verts=16, parent=br)
        cyl((-0.1, s * 1.3, ZR + 0.12), 0.06, 0.22, "dark_steel", rot=(PI / 2, 0, 0), verts=16, parent=br)
    for dx in (-0.09, 0.09):
        box((dx, 0, ZR + 0.22), (0.06, 2.64, 0.22), "ochre", bevel=0.008, parent=br)                # girders
    box((0, 0, ZR + 0.34), (0.26, 2.64, 0.03), "ochre", bevel=0.004, parent=br)
    box((0, 0, ZR + 0.11), (0.26, 2.64, 0.03), "ochre", bevel=0.004, parent=br)
    for k in range(7):
        box((0, -1.2 + 0.4 * k, ZR + 0.36), (0.27, 0.12, 0.012), "hazard", bevel=0, parent=br)
    box((0, yt, ZR + 0.47), (0.42, 0.42, 0.22), "ochre", bevel=0.015, parent=br)                 # trolley
    cyl((0, yt + 0.02, ZR + 0.5), 0.1, 0.3, "dark_steel", rot=(0, PI / 2, 0), verts=24, parent=br)  # hoist drum
    motor(0, yt + 0.3, ZR + 0.5, d=(1, 0), s=0.55)
    hook = pivot((0, yt, 0.0), parent=br)
    cab = []
    for dx in (-0.05, 0.05):
        cab.append((dx, cyl((dx, 0, 0.5), 0.008, 1.0, "dark_steel", verts=6, bevel=0, parent=br)))
    box((0, 0, 0.0), (0.2, 0.12, 0.1), "yellow", bevel=0.01, parent=hook)                        # hook block
    sphere((0, 0, -0.07), 0.04, "dark_steel", parent=hook)
    cell = [cyl((0, 0, -0.22), 0.09, 0.24, "lead_new", verts=24, parent=hook),
            cyl((0, 0, -0.1), 0.1, 0.03, "dark_steel", verts=24, parent=hook),
            torus((0, 0, -0.06), 0.03, 0.008, "yellow", rot=(PI / 2, 0, 0), seg=10, parent=hook)]
    zup, zdown_m, zdown_w = ZR - 0.02, 1.22, 1.02

    def sm(u):
        u = max(0.0, min(1.0, u))
        return u * u * (3 - 2 * u)

    def pose(t, on):
        if not on:
            t = 0.0
        if t < 0.08:
            x, z = XM, zdown_m
        elif t < 0.16:
            x, z = XM, zdown_m + (zup - zdown_m) * sm((t - 0.08) / 0.08)
        elif t < 0.45:
            x, z = XM + (TARGET - XM) * sm((t - 0.16) / 0.29), zup
        elif t < 0.58:
            x, z = TARGET, zup + (zdown_w - zup) * sm((t - 0.45) / 0.13)
        elif t < 0.66:
            x, z = TARGET, zdown_w
        elif t < 0.74:
            x, z = TARGET, zdown_w + (zup - zdown_w) * sm((t - 0.66) / 0.08)
        elif t < 0.94:
            x, z = TARGET + (XM - TARGET) * sm((t - 0.74) / 0.2), zup
        else:
            x, z = XM, zup + (zdown_m - zup) * sm((t - 0.94) / 0.06)
        br.location.x = x
        hook.location.z = z
        top = ZR + 0.38
        for dx, o in cab:
            o.scale = (1, 1, max(0.02, top - z))
            o.location = (dx, yt, (top + z) / 2)
        show = (t < 0.62) or not on
        for o in cell:
            o.hide_render = not show
    ANIM.append(pose)
    label(2, "the gantry: picks a cell, runs west, lowers it into a well", (XM - 0.1, 0.0, ZR + 0.5))


def west_end():
    # the inverter (grey cabinet) and the transformer (green tank, finned), trunks out west
    cabinet(-2.12, -0.75, 0.56, 0.62, 1.15, mat="grey")
    gauge((-2.0, -1.07, 0.85), (0, -1, 0.15), r=0.065, live=lambda t: 0.25 * math.sin(2 * PI * 2 * t))
    gauge((-2.25, -1.07, 0.85), (0, -1, 0.15), r=0.065, live=lambda t: 0.1 * math.sin(2 * PI * 4 * t))
    id_panel((-2.12, -1.065, 0.55), 0.3, 0.12, stripe="yellow")
    box((-2.12, 0.62, 0.45), (0.56, 0.6, 0.72), "green", bevel=0.02)
    for s in (-1, 1):
        for k in range(5):
            box((-2.12 + s * 0.33, 0.4 + 0.11 * k, 0.42), (0.1, 0.025, 0.56), "green", bevel=0.004)
    for k in range(3):
        cyl((-2.24 + 0.12 * k, 0.62, 0.88), 0.035, 0.14, "ceramic", verts=12)
    for y in ROWS_Y:
        pipe([(TUBES_X[0] - 0.55, y, 1.16), (-2.12, y * 0.7, 1.2), (-2.12, -0.55 if y < 0 else 0.62, 1.18)],
             r=0.03, mat="copper", flanges=False)
    trunk([(-2.12, -0.4, 0.9), (-2.12, 0.1, 0.95), (-2.12, 0.4, 0.85)], r=0.05)
    trunk([(-2.3, 0.95, 0.4), (-2.42, 1.1, 0.2), (-2.48, 1.1, 0.08)], r=0.065)
    trunk([(-2.32, -1.0, 0.5), (-2.43, -1.15, 0.25), (-2.49, -1.2, 0.08)], r=0.065)
    label(6, "inverter (DC to AC)", (-2.12, -0.75, 1.15))
    label(7, "transformer, armoured trunks: the wire", (-2.12, 0.62, 0.8))


def clutter():
    # the caesium reservoir (cream) at the north-east and its feed
    vtank(1.52, 1.0, 0.24, 0.85, "cream", bands=(0.4,), nozzle=(0.0, 0.0))
    pipe([(1.52, 1.0, 1.0), (1.3, 0.95, 0.6), (TUBES_X[-1] + 0.3, ROWS_Y[0] + 0.2, 0.12)], r=0.028, mat="bare",
         marks=((0.5, "yellow"),))
    hose([(1.35, 0.85, 0.3), (1.35, -0.2, 0.2), (TUBES_X[-1] + 0.3, ROWS_Y[1] - 0.2, 0.12)], r=0.035, mat="hose_k")
    valve(1.25, -0.95, 0.0, 0.45, wheel="red")
    jbox(0.0, -1.2, mat="grey")
    bundle([(0.0, -1.2, 0.42), (-1.0, -1.1, 0.16), (-1.85, -1.0, 0.3)], cols=("black", "red", "yellow"))
    bundle([(XM - 0.3, -0.35, 0.3), (1.0, -1.0, 0.15), (0.1, -1.15, 0.2)], cols=("grey", "black"))
    stain(-0.5, -1.0, 0.8, 0.12)
    stain(1.86, -0.5, 0.35, 0.12)
    stain(-2.1, 0.1, 0.25, 0.3)
    stain(0.6, 1.1, 0.5, 0.1)


crucible()
tubes()
magazine()
gantry()
west_end()
clutter()
run(dict(name="the thermionic gantry", footprint=[5, 3]), nf=32)
