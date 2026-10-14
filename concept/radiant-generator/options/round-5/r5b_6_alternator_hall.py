"""Radiant Generator, round 5, suggestion 6: THE ALTERNATOR HALL (3x5).

The cell heats a sealed gas loop; a turbine-compressor on the loop turns, through a bevel
gearbox, an upright alternator whose rotor, slip rings and exciter stand open on top --
the moving heart of the building, seen from above as a hydro-station generator is.

  cell revolver (SE) -> lead core pot (S, three sight slots) -> hot leg (lagged, red ring)
  -> turbine | gearbox | compressor (under the alternator's south side) -> gas cooler
  radiators (E) -> cold leg (green ring) back to the core;  gearbox -> vertical shaft ->
  alternator (green, centre) -> slip rings, brushes -> bus duct -> switch house (N, oxide)
  -> cable trunks to ground (NE).

  $BLENDER -b --python r5b_6_alternator_hall.py -- <out-dir> [--quick] [--only idle|working]
Not a model; nothing is adopted.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r5b_kit import *  # noqa: E402,F401,F403

W, H = 3, 5
TLOOP = 1.0


def core():
    """The lead core pot: the cell sits in it; three shielded slots face south."""
    deck(-1.38, -2.44, -0.66, -1.5, h=0.1)
    deck(0.66, -2.44, 1.38, -1.22, h=0.1)
    cx, cy, r, h = 0.05, -1.72, 0.58, 1.3
    cyl((cx, cy, 0.17), r + 0.1, 0.14, "dark_steel", verts=64)
    bolts(cx, cy, 0.25, r + 0.06, 16, r=0.018)
    cyl((cx, cy, h / 2 + 0.12), r, h - 0.1, "lead", verts=96)
    for z in (0.42, 1.18):
        vessel_band(cx, cy, z, r, n_rivets=12, lug_a=-PI / 2 - 0.9)
    weld_ring(cx, cy, 1.0, r)
    vertical_seams(cx, cy, r, 0.5, 1.12, (-2.3, -0.6))
    for i, z in enumerate((0.62, 0.79, 0.96)):
        slot_window(cx, cy, r, -PI / 2 + 0.05, z, 0.42, 0.07, f"fl_slot{i}", k=1 + (i % 2))
    head(cx, cy, h + 0.07, r, 0.22, "lead")
    flange_ring(cx, cy, h + 0.07, r - 0.03, mat="bare", h=0.05, nb=16)
    manway_top(cx - 0.2, cy - 0.12, h + 0.24, r=0.12, nb=8)
    cyl((cx + 0.22, cy + 0.16, h + 0.3), 0.09, 0.2, "bare", verts=20)          # hot-leg nozzle
    flange_ring(cx + 0.22, cy + 0.16, h + 0.4, 0.08, mat="bare", h=0.035, nb=8)
    cyl((cx - 0.3, cy + 0.25, h + 0.26), 0.05, 0.14, "bare", verts=12)         # relief valve
    cyl((cx - 0.3, cy + 0.25, h + 0.35), 0.07, 0.05, "brass", verts=6, bevel=0)
    point((cx, cy - r - 0.25, 0.8), 6.0, pulse=lambda t: 0.8 + 0.2 * math.sin(2 * PI * t))
    hazard_tag((cx + 0.32, cy - r + 0.02, 0.3), 0.2, 0.06)
    insp_plate(cx, cy, r, -PI / 2 - 0.85, 0.5, 0.86, 0.2, mat="lead_new")
    return cx, cy, r, h


def revolver(cx, cy, r):
    """The cell revolver on the core's east flank: six cells in a drum lying east-west,
    indexing one place a loop to present the next cell to the core; its feed hopper
    above (ochre), the spent chute out the core's west side."""
    x0, y0, z0 = 0.98, -1.98, 0.52
    box((x0, y0, 0.24), (0.5, 0.56, 0.3), "dark_steel")
    for s in (-1, 1):
        box((x0 + s * 0.27, y0, 0.48), (0.06, 0.5, 0.56), "dark_steel", bevel=0.01)
    pv = pivot((x0, y0, z0), (0, PI / 2, 0))
    cyl((0, 0, 0), 0.08, 0.5, "bare", verts=16, parent=pv)
    for s in (-1, 1):
        cyl((0, 0, s * 0.21), 0.3, 0.05, "green", verts=6, bevel=0.006, parent=pv)
    for k in range(6):
        a = 2 * PI * k / 6
        cell((0.19 * math.cos(a), 0.19 * math.sin(a), 0), (0, 0, 1), r=0.075, h=0.38, parent=pv)
    b0 = pv.rotation_euler.copy()

    def pose(t):
        pv.rotation_euler = b0
        pv.rotation_euler.rotate_axis("Z", 2 * PI / 6 * ease_step(t, 0.05, 0.4))
    ANIM.append(pose)
    # the feed hopper: an ochre box, a lid, a chute down into the drum
    box((x0 + 0.05, y0 + 0.42, 0.95), (0.42, 0.36, 0.34), "ochre", bevel=0.02)
    box((x0 + 0.05, y0 + 0.42, 1.14), (0.46, 0.4, 0.04), "dark_steel", bevel=0.006)
    handwheel((x0 + 0.05, y0 + 0.42, 1.2), 0.08, mat="yellow")
    box((x0, y0 + 0.22, 0.72), (0.2, 0.16, 0.3), "dark_steel")
    id_panel((x0 + 0.05, y0 + 0.235, 0.96), 0.2, 0.1, stripe="green")
    # the feed into the core: a short lead throat
    cyl((0.62, y0 + 0.04, z0), 0.12, 0.28, "lead", rot=(0, PI / 2, 0), verts=24)
    flange_ring(0.72, y0 + 0.04, z0, 0.1, mat="bare", h=0.03, nb=8)
    # spent cells: chute west to the spent bin (lead, a green lid propped open)
    bx, by = -1.02, -2.0
    box((bx, by, 0.32), (0.56, 0.6, 0.46), "lead", bevel=0.02)
    box((bx, by, 0.56), (0.46, 0.5, 0.03), "dark", bevel=0)
    for k, (dx, dy) in enumerate(((-0.12, -0.1), (0.06, -0.08), (-0.05, 0.12))):
        spent_cell((bx + dx, by + dy, 0.6), (1, 0.3 * k, 0), r=0.065, h=0.3)
    box((bx, by + 0.36, 0.78), (0.56, 0.06, 0.4), "green", rot=(-0.35, 0, 0), bevel=0.01)
    box((bx, by - 0.315, 0.3), (0.4, 0.02, 0.1), "hazard", bevel=0)
    cyl((-0.62, by + 0.04, 0.5), 0.09, 0.3, "lead", rot=(0, PI / 2, 0), verts=24)


def turbine_set():
    """Under the alternator's south side: turbine (W), bevel gearbox, compressor (E) on
    one shaft, a coupling either side of the gearbox that the player sees turn."""
    skid(-1.2, -0.98, 0.95, -0.42, 0.12)
    y, z = -0.7, 0.42
    cyl((-0.82, y, z), 0.24, 0.3, "grey", rot=(0, PI / 2, 0), verts=40)           # compressor volute
    for xx in (-0.95, -0.69):
        cyl((xx, y, z), 0.265, 0.035, "bare", rot=(0, PI / 2, 0), verts=40)
    cyl((-0.82, y, z + 0.28), 0.08, 0.12, "bare", verts=16)
    box((-0.08, y, 0.36), (0.34, 0.4, 0.46), "grey", bevel=0.02)                 # gearbox
    flat_plate((-0.08, y - 0.2, 0.38), 0.24, 0.22, mat="bare")
    cyl((-0.08, y + 0.05, 0.62), 0.11, 0.1, "dark_steel", verts=24)
    cyl((0.6, y, z), 0.27, 0.34, "dark_steel", rot=(0, PI / 2, 0), verts=40)       # turbine volute
    for xx in (0.45, 0.75):
        cyl((xx, y, z), 0.3, 0.04, "bare", rot=(0, PI / 2, 0), verts=40)
    cyl((0.6, y, z + 0.3), 0.1, 0.14, "bare", verts=16)
    flange_ring(0.6, y, z + 0.37, 0.09, mat="bare", h=0.03, nb=8)
    coupling(-0.47, y, z - 0.02, 0.11, axis=(1, 0, 0))
    coupling(0.3, y, z - 0.02, 0.1, axis=(1, 0, 0))
    gauge((-0.82, y - 0.27, 0.48), (0, -1, 0.2), r=0.05)
    gauge((0.62, y - 0.23, 0.46), (0, -1, 0.2), r=0.045)


def alternator():
    """The upright alternator: a ribbed green stator on a dark plinth, its top open on the
    rotor -- eight copper poles on a spider -- with the slip rings and the exciter on the
    shaft above, the brush gear on a bracket beside them."""
    ax, ay = -0.12, 0.28
    cyl((ax, ay, 0.1), 0.96, 0.2, "dark_steel", verts=72)
    bolts(ax, ay, 0.21, 0.9, 20, r=0.02)
    cyl((ax, ay, 0.6), 0.8, 0.8, "green", verts=96)
    for k in range(16):
        a = 2 * PI * (k + 0.5) / 16
        box((ax + 0.81 * math.cos(a), ay + 0.81 * math.sin(a), 0.6), (0.035, 0.04, 0.66), "bare", rz=a,
            bevel=0.005)
    for z in (0.26, 0.96):
        cyl((ax, ay, z), 0.84, 0.06, "bare", verts=96)
    annulus((ax, ay, 1.0), 0.6, 0.84, 0.05, "green")
    bolts(ax, ay, 1.03, 0.72, 24, r=0.016)
    cyl((ax, ay, 0.93), 0.6, 0.02, "dark", verts=64, bevel=0)                   # the air gap's dark
    stencil((ax + 0.2, ay - 0.82, 0.62), (0.4, 0.01, 0.1), 0.0)
    id_panel((ax - 0.3, ay - 0.81, 0.45), 0.2, 0.12, stripe="yellow")
    rotor = pivot((ax, ay, 0.98))
    cyl((0, 0, 0), 0.18, 0.12, "dark_steel", verts=32, parent=rotor)
    for k in range(8):
        a = 2 * PI * k / 8
        c, s = math.cos(a), math.sin(a)
        box((0.3 * c, 0.3 * s, 0), (0.24, 0.05, 0.06), "dark_steel", rz=a, parent=rotor)
        box((0.45 * c, 0.45 * s, 0.01), (0.14, 0.17, 0.1), "copper", rz=a, bevel=0.01, parent=rotor)
        box((0.535 * c, 0.535 * s, 0.01), (0.04, 0.2, 0.1), "dark_steel", rz=a, bevel=0.004, parent=rotor)
    cyl((0, 0, 0.3), 0.07, 0.56, "bare", verts=20, parent=rotor)
    for z in (0.16, 0.25, 0.34):
        cyl((0, 0, z), 0.12, 0.05, "copper", verts=32, parent=rotor)
        cyl((0, 0, z + 0.04), 0.1, 0.02, "dark", verts=32, bevel=0, parent=rotor)
    cyl((0, 0, 0.5), 0.22, 0.2, "cream", verts=40, parent=rotor)                 # exciter
    for k in range(12):
        a = 2 * PI * k / 12
        box((0.225 * math.cos(a), 0.225 * math.sin(a), 0.5), (0.025, 0.03, 0.18), "dark_steel", rz=a, bevel=0,
            parent=rotor)
    cyl((0, 0, 0.61), 0.2, 0.02, "dark_steel", verts=40, parent=rotor)
    box((0, 0, 0.63), (0.38, 0.06, 0.012), "hazard", bevel=0, parent=rotor)
    cyl((0, 0, 0.64), 0.05, 0.04, "brass", verts=6, bevel=0, parent=rotor)
    spin(rotor, "Z", 0.5)
    # the brush gear: a bracket from the stator rim, three brass brush boxes on the rings
    bx, by = ax + 0.36, ay - 0.36
    box((bx, by, 1.15), (0.08, 0.08, 0.32), "dark_steel")
    for z in (1.14, 1.23, 1.32):
        box((ax + 0.22, ay - 0.2, z), (0.16, 0.05, 0.04), "dark_steel", rz=-PI / 4, bevel=0)
        box((ax + 0.15, ay - 0.13, z), (0.06, 0.05, 0.04), "brass", rz=-PI / 4, bevel=0.004)
    bundle([(bx, by, 1.3), (bx + 0.25, by - 0.1, 1.1), (0.75, -0.3, 0.6), (0.85, -0.1, 0.12)],
           cols=("red", "black", "yellow"))
    return ax, ay


def coolers():
    """The gas cooler on the east flank: radiator panels in a bank N-S, headers along the
    top and foot; heat leaves by radiation (vacuum: no fans)."""
    radiator_bank(0.95, 1.45, -0.32, 1.42, 0.12, 1.12, 9, mat="grey", along_x=False)
    cyl((1.2, 1.55, 0.7), 0.1, 0.4, "bare", verts=16)
    gauge((1.36, 1.5, 0.95), (0.4, -1, 0.15), r=0.045)


def west_side():
    """The loop's make-up: an expansion tank (ochre) in the north-west corner, a small
    circulator pump on its skid, a valve station."""
    vtank(-1.08, 1.12, 0.34, 1.2, "ochre", bands=(0.5, 0.95), top="dark_steel", nozzle=(0.2, -0.2))
    ladder(-1.08 - 0.32, 1.0, 0.2, 1.1, axis="y", mat="dark_steel")
    jbox(-1.2, 0.05, 0.3, 0.26, 0.34, mat="grey")
    valve(-1.05, -0.3, 0.0, 0.4, wheel="red")


def loop(cx, cy, r, h):
    """The sealed gas loop: hot leg lagged (red mark), cold leg bare (green mark), the
    turbine's exhaust to the coolers in tan hose."""
    lagged([(cx + 0.22, cy + 0.16, h + 0.42), (cx + 0.32, cy + 0.5, h + 0.3), (0.62, -0.95, 1.2),
            (0.6, -0.7, 0.86)], r=0.1, marks=((0.45, "red"),))
    hose([(0.82, -0.62, 0.42), (0.95, -0.5, 0.3), (1.1, -0.36, 0.2)], r=0.1, mat="hose")
    pipe([(1.15, 1.44, 0.17), (0.6, 1.36, 0.2), (-0.3, 1.33, 0.2), (-0.74, 1.2, 0.25)], r=0.07, mat="bare",
         marks=((0.3, "green"), (0.75, "green")))
    hose([(-1.25, 0.82, 0.5), (-1.34, 0.3, 0.42), (-1.3, -0.3, 0.42), (-0.97, -0.68, 0.45)], r=0.09, mat="hose_k")
    pipe([(-0.82, -0.75, 0.66), (-0.75, -1.05, 0.75), (cx - r * 0.75, cy + r * 0.62, 0.75)], r=0.075, mat="bare",
         marks=((0.5, "green"),))
    valve(-0.42, -1.05, 0.0, 0.5, wheel="yellow")


def north(ax, ay):
    """The bus duct from the alternator's north side to the switch house (oxide red), the
    output meter on its face, the cable trunks dropping to the ground in the NE corner."""
    box((ax + 0.05, 1.18, 0.62), (0.34, 0.4, 0.28), "grey", bevel=0.012)
    box((ax + 0.05, 1.42, 0.62), (0.4, 0.08, 0.34), "dark_steel", bevel=0.006)
    hx, hy, hw, hd, hh = 0.02, 1.98, 1.62, 0.84, 1.05
    box((hx, hy, hh / 2), (hw, hd, hh), "cream", bevel=0.02)
    box((hx, hy, hh + 0.03), (hw + 0.06, hd + 0.06, 0.06), "dark_steel", bevel=0.01)
    for dx in (0.18, 0.5):                                                           # roof vents, capped
        cyl((hx + dx, hy + 0.12, hh + 0.16), 0.11, 0.2, "grey", verts=24)
        cyl((hx + dx, hy + 0.12, hh + 0.29), 0.15, 0.04, "dark_steel", verts=24)
        for k in range(4):
            box((hx + dx, hy + 0.12 - 0.112, hh + 0.1 + 0.035 * k), (0.12, 0.01, 0.012), "dark_steel", bevel=0)
    box((hx + 0.34, hy - 0.22, hh + 0.08), (0.7, 0.16, 0.06), "oxide", bevel=0.008)     # breaker trunking
    for dx in (0.06, 0.34, 0.62):
        cyl((hx + dx, hy - 0.22, hh + 0.13), 0.04, 0.05, "brass", verts=6, bevel=0)
    flat_plate((hx - 0.1, hy + 0.1, hh + 0.06), 0.3, 0.3, face="T", mat="bare")
    for i in range(5):
        box((hx - 0.45, hy - hd / 2 - 0.01, 0.3 + 0.08 * i), (0.4, 0.02, 0.03), "dark_steel", bevel=0)
    meter((hx + 0.12, hy - hd / 2 - 0.02, 0.72), (0, -1, 0.1), r=0.13,
          swing=lambda t: 0.25 + 0.12 * math.sin(2 * PI * t) + 0.05 * math.sin(6 * PI * t))
    meter((hx + 0.45, hy - hd / 2 - 0.02, 0.72), (0, -1, 0.1), r=0.09,
          swing=lambda t: -0.1 + 0.08 * math.sin(2 * PI * t + 1.0))
    status_lamp(hx + 0.62, hy - 0.2, hh + 0.08)
    id_panel((hx - 0.45, hy - hd / 2 - 0.01, 0.8), 0.3, 0.14, stripe="yellow")
    hazard_tag((hx + 0.3, hy - hd / 2 - 0.01, 0.42), 0.36, 0.07)
    jbox(hx - 0.45, hy - 0.05, 0.4, 0.3, 0.3, mat="grey", z=hh + 0.06)
    handwheel((hx + 0.3, hy - hd / 2 - 0.06, 0.4), 0.08, axis=(0, -1, 0), mat="red")
    # cable trunks: three fat black cables out of the house's east end, down into the ground
    for k, dy in enumerate((-0.25, 0.0, 0.25)):
        hose([(hx + hw / 2 - 0.05, hy + dy, 0.55 - 0.08 * k), (1.15, hy + dy - 0.1, 0.42), (1.3, hy + dy - 0.2, 0.1),
              (1.36, hy + dy - 0.25, -0.05)], r=0.06, mat="hose_k")
    box((1.22, 1.78, 0.04), (0.36, 0.7, 0.08), "dark_steel")
    tray([(ax + 0.05, 1.0, 1.05), (ax + 0.05, 1.5, 1.1)])


cx, cy, r, h = core()
revolver(cx, cy, r)
turbine_set()
ax, ay = alternator()
coolers()
west_side()
loop(cx, cy, r, h)
north(ax, ay)
stain(-0.1, -0.8, 0.5, 0.15)
stain(1.2, -1.0, 0.2, 0.3)
stain(-1.2, 0.0, 0.2, 0.25)
stain(0.9, -2.3, 0.3, 0.12)
stain(-1.1, -2.4, 0.3, 0.1)
stain(1.25, 2.1, 0.2, 0.35)
run(W, H, name="6-the-alternator-hall")
