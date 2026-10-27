"""Radiant Generator, round 5, suggestion 7: THE PLATE RACK (4x4).

Direct collection: the cells stand in a lead trough between charged collector plates; the
isotope's emission charges the plates, two copper bus bars gather it as direct current,
and a rotary converter (a DC motor driving an AC alternator on one shaft) turns it into
the grid's current. A gantry shuttle runs the rack's length, setting a fresh cell into
the next slot and lifting the spent one out.

  cell magazine (W, ochre) -> gantry shuttle (ochre bridge, E-W) -> collector rack (lead
  trough, copper plates, cells between) -> bus bars -> rotary converter (S: green DC
  motor, commutator, coupling, grey AC machine) -> transformer (SE, cream) -> cable
  trunks (E).  Coolant: the trough's jacket -> pump (N) -> copper radiator bank (NE).

  $BLENDER -b --python r5b_7_plate_rack.py -- <out-dir> [--quick] [--only idle|working]
Not a model; nothing is adopted.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r5b_kit import *  # noqa: E402,F401,F403

W, H = 4, 4
X0, X1, Y0, Y1, ZT = -1.42, 1.25, -0.42, 0.78, 0.72     # the trough
NP = 11                                                   # collector plates


def trough():
    """The lead trough: thick walls, bolted dark-steel copings with the gantry's rails on
    them, the plates and cells inside, the light seen between the plates from above."""
    xm, ym = (X0 + X1) / 2, (Y0 + Y1) / 2
    box((xm, ym, 0.06), (X1 - X0 + 0.2, Y1 - Y0 + 0.2, 0.12), "dark_steel")
    tw = 0.12
    for yy in (Y0, Y1):
        box((xm, yy, ZT / 2 + 0.06), (X1 - X0 + 0.12, tw, ZT), "lead", bevel=0.02)
        box((xm, yy, ZT + 0.09), (X1 - X0 + 0.16, tw + 0.06, 0.05), "dark_steel", bevel=0.008)
        box((xm, yy, ZT + 0.14), (X1 - X0 + 0.1, 0.05, 0.05), "bare", bevel=0.006)          # rail
        for k in range(14):
            cyl((X0 + 0.05 + k * (X1 - X0 - 0.1) / 13, yy + 0.06 * (1 if yy == Y1 else -1), ZT + 0.125), 0.013,
                0.015, "bolt", verts=6, bevel=0)
    for xx in (X0, X1):
        box((xx, ym, ZT / 2 + 0.06), (tw, Y1 - Y0 - tw, ZT), "lead", bevel=0.02)
        box((xx, ym, ZT + 0.09), (tw + 0.06, Y1 - Y0 + 0.1, 0.05), "dark_steel", bevel=0.008)
    for xx in (X0 + 0.5, xm + 0.3, X1 - 0.45):                                           # wall bands
        box((xx, Y0 - 0.065, ZT / 2 + 0.06), (0.07, 0.02, ZT + 0.02), "bare", bevel=0.004)
    # the floor of light: what the cells give off, seen between the plates
    box((xm, ym, 0.16), (X1 - X0 - 0.16, Y1 - Y0 - 0.16, 0.04), fluid("fl_floor", "swirl", scale=1.5, k=1, arms=3,
                                                                    bright=0.3), bevel=0)
    point((xm, ym - 0.2, 0.55), 6.0, radius=0.4, pulse=lambda t: 0.85 + 0.15 * math.sin(4 * PI * t))
    xs = [X0 + 0.2 + i * (X1 - X0 - 0.4) / (NP - 1) for i in range(NP)]
    for i, xx in enumerate(xs):
        box((xx, ym, 0.44), (0.035, Y1 - Y0 - 0.2, 0.52), "copper", bevel=0.004)
        box((xx, ym, 0.71), (0.06, Y1 - Y0 - 0.16, 0.03), "dark_steel", bevel=0.003)
        for yy in (ym - 0.22, ym + 0.22):                                               # bus clips
            box((xx, yy, 0.79), (0.04, 0.04, 0.12), "brass", bevel=0.003)
    for i in range(NP - 1):                                                             # the cells
        xx = (xs[i] + xs[i + 1]) / 2
        if i in (3,):
            continue                                                                    # the empty slot
        cell((xx, ym - 0.18, 0.4), (0, 0, 1), r=0.075, h=0.42, lit=(i not in (8,)))
        cell((xx, ym + 0.2, 0.4), (0, 0, 1), r=0.075, h=0.42)
    # the north half under hinged lead lids, bolted, handles: only the south row is seen
    for i in range(5):
        lx0 = X0 + 0.08 + i * (X1 - X0 - 0.16) / 5
        lw = (X1 - X0 - 0.16) / 5 - 0.03
        box((lx0 + lw / 2, ym + 0.27, 0.95), (lw, 0.5, 0.06), "lead", bevel=0.012)
        cyl((lx0 + lw / 2, Y1 - 0.02, 0.95), 0.03, lw * 0.9, "bare", rot=(0, PI / 2, 0), verts=12)   # hinge
        torus((lx0 + lw / 2, ym + 0.06, 0.99), 0.035, 0.008, "yellow", rot=(PI / 2, 0, 0), seg=12)
        for dx in (-lw / 2 + 0.04, lw / 2 - 0.04):
            for dy in (0.08, 0.46):
                cyl((lx0 + lw / 2 + dx, ym + dy, 0.985), 0.012, 0.012, "bolt", verts=6, bevel=0)
        box((lx0 + lw / 2, ym + 0.3, 0.985), (lw * 0.5, 0.12, 0.006), "stencil" if i % 2 else "lead_new", bevel=0)
    for yy in (ym - 0.22, ym + 0.22):                                                   # bus bars
        box((xm, yy, 0.87), (X1 - X0 - 0.3, 0.07, 0.04), "copper", bevel=0.006)
    for xx in (X0 + 0.1, X1 - 0.1):
        box((xx, ym, 0.84), (0.08, Y1 - Y0 - 0.1, 0.06), "dark_steel", bevel=0.006)
    # a cable tray over the lids from the bus bars' east end to the converter's drop
    tray([(X1 - 0.2, ym + 0.3, 1.02), (xm, ym + 0.32, 1.02), (X0 + 0.9, ym + 0.32, 1.02)])
    bundle([(X1 - 0.2, ym + 0.3, 1.05), (xm, ym + 0.32, 1.05), (X0 + 0.9, ym + 0.32, 1.05), (X0 + 0.75, Y0 + 0.1, 0.95)],
           cols=("red", "black", "grey"), r=0.02)
    insp_flat = (xm - 0.6, Y0 - 0.07, 0.42)
    flat_plate(insp_flat, 0.36, 0.3, mat="lead_new")
    id_panel((xm + 0.45, Y0 - 0.07, 0.5), 0.26, 0.14, stripe="yellow")
    hazard_tag((xm + 0.45, Y0 - 0.07, 0.28), 0.4, 0.06)
    gauge((X1 - 0.3, Y0 - 0.08, 0.5), (0, -1, 0.2), r=0.06)
    gauge((X0 + 0.25, Y0 - 0.08, 0.5), (0, -1, 0.2), r=0.055)
    return xs


def gantry(xs):
    """The shuttle: an ochre bridge on end trucks running the rails, a trolley under it
    with a gripper. Out east with a fresh cell, lowered into the empty slot; back west
    with the spent one, lowered into the magazine's throat."""
    G = pivot((0, 0, 0))
    ym = (Y0 + Y1) / 2
    zr = ZT + 0.17
    for yy in (Y0, Y1):
        box((0, yy, zr + 0.07), (0.34, 0.14, 0.14), "dark_steel", parent=G)
        for s in (-1, 1):
            cyl((s * 0.11, yy, zr + 0.03), 0.045, 0.16, "bare", rot=(PI / 2, 0, 0), verts=16, parent=G)
    box((0, ym, zr + 0.22), (0.2, Y1 - Y0 + 0.2, 0.16), "ochre", bevel=0.012, parent=G)
    for s in (-1, 1):
        box((s * 0.105, ym, zr + 0.22), (0.015, Y1 - Y0 + 0.1, 0.12), "dark_steel", bevel=0, parent=G)
    box((0, Y0 - 0.12, zr + 0.22), (0.16, 0.04, 0.1), "hazard", bevel=0, parent=G)
    box((0.14, Y1 - 0.05, zr + 0.36), (0.22, 0.18, 0.14), "green", parent=G)                   # travel motor
    bundle([(0.14, Y1 + 0.05, zr + 0.38), (0.3, Y1 + 0.35, zr + 0.2), (0.5, Y1 + 0.5, 0.6)], cols=("black", "yellow"))
    T = pivot((0, ym - 0.18, zr + 0.06), parent=G)
    box((0, 0, 0.0), (0.18, 0.2, 0.1), "dark_steel", parent=T)
    cyl((0, 0, -0.1), 0.02, 0.2, "bare", verts=8, parent=T)
    Gr = pivot((0, 0, -0.2), parent=T)
    box((0, 0, 0), (0.16, 0.06, 0.04), "yellow", parent=Gr)
    for s in (-1, 1):
        box((s * 0.07, 0, -0.06), (0.02, 0.05, 0.1), "dark_steel", parent=Gr)
    fresh = []
    spent = []
    for lit, store in ((True, fresh), (False, spent)):
        first = len(OBJS)
        cell((0, 0, -0.27), (0, 0, 1), r=0.07, h=0.38, parent=Gr, lit=lit)
        store.extend(OBJS[first:])
    xa, xb = X0 + 0.15, (xs[3] + xs[4]) / 2
    # the slot the shuttle fills is 3 (empty in the rack)

    def pose(t):
        t = (t + 0.2) % 1.0        # the loop starts with the shuttle on its way out
        # out (0 -> 0.42), lower and set (0.42 -> 0.58), back (0.58 -> 1.0), lower at the magazine at 0/1
        if t < 0.42:
            u = ease_step(t, 0.06, 0.42)
            x = xa + (xb - xa) * u
        elif t < 0.58:
            x = xb
        else:
            u = ease_step(t, 0.58, 0.94)
            x = xb + (xa - xb) * u
        G.location.x = x
        low = max(0.0, 1 - abs(t - 0.5) / 0.08) + max(0.0, 1 - min(t, 1 - t) / 0.06)
        T.location.z = zr + 0.06
        Gr.location.z = -0.2 - 0.22 * min(1.0, low)
        carry_fresh = t < 0.5
        for o in fresh:
            o.hide_render = not carry_fresh
        for o in spent:
            o.hide_render = carry_fresh
    ANIM.append(pose)


def magazine():
    """The cell magazine at the rack's west end (ochre, a sloped hopper top, two loading
    ports for the two fuel slots), the spent bin beside it (lead)."""
    mx, my = -1.72, 0.18
    box((mx, my, 0.8), (0.5, 0.9, 1.6), "ochre", bevel=0.025)
    for zz in (0.4, 1.15):
        box((mx, my, zz), (0.53, 0.93, 0.04), "dark_steel", bevel=0.006)
    box((mx, my, 1.63), (0.44, 0.84, 0.06), "ochre", bevel=0.01)
    for dy in (-0.2, 0.2):
        cyl((mx, my + dy, 1.7), 0.12, 0.1, "lead", verts=6, bevel=0.006)
        cyl((mx, my + dy, 1.76), 0.1, 0.02, "dark_steel", verts=6, bevel=0)
    handwheel((mx + 0.12, my - 0.36, 1.72), 0.06, mat="red")
    gauge((mx + 0.1, my - 0.46, 1.38), (0, -1, 0.2), r=0.05)
    id_panel((mx, my - 0.46, 0.75), 0.24, 0.14, stripe="red")
    hazard_tag((mx, my - 0.46, 1.12), 0.36, 0.06)
    box((mx + 0.28, my - 0.12, ZT + 0.2), (0.12, 0.3, 0.3), "lead", bevel=0.01)              # throat
    ladder(mx - 0.25, my + 0.15, 0.2, 1.3, axis="y", mat="dark_steel")
    bx, by = -1.65, -0.85
    box((bx, by, 0.25), (0.56, 0.5, 0.42), "lead", bevel=0.02)
    box((bx, by, 0.47), (0.48, 0.42, 0.03), "dark", bevel=0)
    for k, (dx, dy) in enumerate(((-0.1, -0.06), (0.08, 0.05), (0.12, -0.1))):
        spent_cell((bx + dx, by + dy, 0.52), (1, 0.4 * (k - 1), 0.1), r=0.06, h=0.28)
    box((bx, by - 0.26, 0.24), (0.36, 0.02, 0.08), "hazard", bevel=0)


def converter():
    """The rotary converter on the south skid: the DC motor (green) with its commutator
    and brushes open on its west end, a coupling, the AC machine (grey, ribbed), the
    exciter on its east end; the bus drops into it from the rack."""
    skid(-1.35, -1.95, 0.9, -1.0, 0.12)
    y, z = -1.42, 0.5
    cyl((-0.55, y, z), 0.32, 0.62, "green", rot=(0, PI / 2, 0), verts=48)
    for xx in (-0.84, -0.26):
        cyl((xx, y, z), 0.34, 0.05, "dark_steel", rot=(0, PI / 2, 0), verts=48)
    box((-0.55, y, 0.2), (0.5, 0.56, 0.16), "dark_steel")
    box((-0.55, y + 0.12, z + 0.33), (0.3, 0.2, 0.12), "grey", bevel=0.01)                    # terminal box
    com = pivot((-1.0, y, z), (0, PI / 2, 0))
    cyl((0, 0, 0), 0.2, 0.2, "copper", verts=24, parent=com)
    for k in range(12):
        a = 2 * PI * k / 12
        box((0.2 * math.cos(a), 0.2 * math.sin(a), 0), (0.02, 0.02, 0.2), "dark", rz=a, bevel=0, parent=com)
    cyl((0, 0, -0.12), 0.06, 0.06, "bare", verts=12, parent=com)
    spin(com, "Z", 1 / 6)
    for a in (0.6, 2.5):
        box((-1.0, y + 0.26 * math.cos(a), z + 0.26 * math.sin(a)), (0.08, 0.06, 0.06), "brass", rot=(a, 0, 0),
            bevel=0.004)
    box((-1.0, y, z + 0.33), (0.06, 0.4, 0.05), "dark_steel", bevel=0.004)
    coupling(-0.08, y, z, 0.14, axis=(1, 0, 0))
    cyl((0.42, y, z), 0.36, 0.62, "grey", rot=(0, PI / 2, 0), verts=48)
    for k in range(9):
        cyl((0.15 + 0.068 * k, y, z), 0.38, 0.02, "dark_steel", rot=(0, PI / 2, 0), verts=48, bevel=0)
    box((0.42, y, 0.2), (0.5, 0.6, 0.16), "dark_steel")
    cyl((0.76, y, z), 0.2, 0.1, "cream", rot=(0, PI / 2, 0), verts=32)
    meter((0.42, y - 0.37, z + 0.05), (0, -1, 0.25), r=0.08,
          swing=lambda t: 0.2 + 0.1 * math.sin(2 * PI * t) + 0.08 * max(0.0, 1 - abs(t - 0.55) / 0.1))
    id_panel((-0.55, y - 0.33, 0.55), 0.2, 0.1, stripe="green")
    # the DC drop from the bus bars: copper straps in a dark duct, down the rack's south wall
    box((-0.6, Y0 - 0.2, 0.7), (0.22, 0.18, 0.22), "grey", bevel=0.01)
    box((-0.6, -0.85, 0.66), (0.14, 0.5, 0.1), "dark_steel", bevel=0.006)
    bundle([(-0.6, -0.95, 0.6), (-0.6, -1.1, 0.8), (-0.55, y + 0.12, z + 0.4)], cols=("red", "black"), r=0.022)


def transformer():
    """The transformer (cream) in the south-east: a ribbed tank, its cable boxes on top,
    the trunks out the east side to the ground."""
    tx, ty = 1.48, -1.4
    box((tx, ty, 0.5), (0.6, 0.7, 0.9), "cream", bevel=0.02)
    for k in range(7):
        box((tx - 0.3 - 0.03, ty - 0.27 + 0.09 * k, 0.48), (0.06, 0.03, 0.7), "cream", bevel=0.004)
        box((tx + 0.08 - 0.24 + 0.08 * k, ty - 0.35 - 0.03, 0.48), (0.03, 0.06, 0.7), "cream", bevel=0.004)
    box((tx, ty, 0.97), (0.64, 0.74, 0.05), "dark_steel", bevel=0.006)
    for dx in (-0.15, 0.05, 0.25):
        box((tx + dx, ty + 0.1, 1.08), (0.12, 0.2, 0.16), "dark_steel", bevel=0.008)
    hose([(-0.8 + 1.55, -1.42, 0.86), (0.95, -1.3, 1.05), (tx - 0.15, ty + 0.1, 1.15)], r=0.05, mat="hose_k")
    for k, dy in enumerate((-0.1, 0.1, 0.3)):
        hose([(tx + 0.25, ty + dy, 1.12), (1.85, ty + dy + 0.05, 0.9), (1.95, ty + dy + 0.1, 0.2),
              (1.97, ty + dy + 0.1, -0.05)], r=0.055, mat="hose_k")
    id_panel((tx - 0.1, ty - 0.355, 0.75), 0.24, 0.12, stripe="red")
    hazard_tag((tx + 0.12, ty - 0.355, 0.32), 0.3, 0.06)
    status_lamp(tx - 0.2, ty - 0.2, 1.02)


def cooling():
    """The trough's coolant: a jacket header along the north wall, a circulating pump,
    a copper radiator bank in the north-east, an expansion pot."""
    pipe([(X0 + 0.2, Y1 + 0.13, 0.3), (X1 - 0.1, Y1 + 0.13, 0.3)], r=0.06, mat="bare", marks=((0.3, "green"),))
    for xx in (X0 + 0.5, 0.0, X1 - 0.4):
        cyl((xx, Y1 + 0.1, 0.3), 0.075, 0.08, "dark_steel", rot=(PI / 2, 0, 0), verts=16)
    pv = pump(-0.5, 1.45, (1, 0), 0.75)
    hose([pv, (0.1, 1.3, 0.75), (0.7, 1.35, 0.6), (1.0, 1.5, 0.5)], r=0.08, mat="hose")
    hose([(X0 + 0.25, Y1 + 0.16, 0.3), (-1.2, 1.2, 0.3), (-0.95, 1.45, 0.3)], r=0.08, mat="hose_k")
    radiator_bank(0.95, 1.9, 0.98, 1.9, 0.12, 1.0, 8, mat="copper", along_x=True)
    vtank(-1.55, 1.48, 0.3, 0.95, "grey", bands=(0.45,), top="dark_steel", nozzle=(0.2, -0.2))
    valve(-1.15, 1.12, 0.0, 0.45, wheel="yellow")
    gauge((-1.55, 1.17, 0.7), (0, -1, 0.2), r=0.05)


xs = trough()
gantry(xs)
magazine()
converter()
transformer()
cooling()
stain(-0.2, -1.95, 0.6, 0.12)
stain(1.6, -1.9, 0.3, 0.12)
stain(-1.8, -1.2, 0.2, 0.2)
stain(0.0, 0.95, 0.5, 0.12)
stain(1.9, -0.6, 0.12, 0.3)
run(W, H, name="7-the-plate-rack")
