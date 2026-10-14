"""Radiant Generator, round 5, suggestion 1: THE THERMOPILE STACK (4 x 4).

  $BLENDER -b --python r5a_1_thermopile.py -- <out-dir> [--quick] [--only working|idle] [--colourmap]

The chain, cell to wire: a cell drops through the indexing plug on top of the lead
hot-core (two pockets, the two fuel slots); its decay heats the core; three thermopile
stacks clamped round the core turn the heat straight into direct current (the hot face
on the core, the cold face on coolant headers); the coolant pumps carry the cold side's
heat to the radiator panels along the north edge (radiation, in vacuum); the DC bus
runs to a rotary converter (DC motor driving an AC alternator on one shaft), whose
output goes through the terminal cabinet into the armoured trunks and out.
The isotope's light shows in the stacks' plate gaps (the hot face is open to the core)
and in two sight slots on the core's diagonal faces; nowhere else.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r5a_kit import *  # noqa: F401,F403,E402
import r5a_kit as K  # noqa: E402

CX, CY, CR, CH = -0.15, 0.3, 0.62, 1.45
K.build_materials(((0.45, 0.3), (1.0, 0.35), (1.45, 0.3)))
radiant("rg_gap", "flow", scale=5.0, k=1, bright=2.2, fn=lambda t: 0.8 + 0.2 * math.sin(2 * PI * t))
radiant("rg_slot", "flow", scale=4.0, k=2, bright=1.1, fn=lambda t: 0.85 + 0.15 * math.sin(2 * PI * t + 1.0))


# ---------------------------------------------------------------- the lead hot-core and its plug
def core():
    prism((CX, CY, 0.08), CR + 0.16, 0.16, "dark_steel", n=8, rz=PI / 8)
    bolts(CX, CY, 0.17, CR + 0.1, 16, r=0.018)
    prism((CX, CY, CH / 2 + 0.08), CR, CH - 0.16, "lead", n=8, rz=PI / 8)
    for z in (0.45, 1.0):
        prism((CX, CY, z), CR + 0.03, 0.08, "bare", n=8, rz=PI / 8, bevel=0.006)
    prism((CX, CY, CH), CR + 0.04, 0.1, "dark_steel", n=8, rz=PI / 8)
    bolts(CX, CY, CH + 0.06, CR - 0.04, 16, r=0.016)
    # sight slots on the two south diagonal faces: the isotope's light, behind lead louvres
    for a in (-PI * 3 / 4, -PI / 4):
        n = Vector((math.cos(a), math.sin(a), 0))
        ap = CR * math.cos(PI / 8)
        p = Vector((CX, CY, 0.72)) + n * (ap + 0.005)
        box(tuple(p), (0.07, 0.03, 0.44), "rg_slot", rz=a + PI / 2, bevel=0)
        for zz in (0.53, 0.91):
            box(tuple(p + n * 0.02 + Vector((0, 0, zz - 0.72))), (0.16, 0.05, 0.05), "dark_steel", rz=a + PI / 2,
                bevel=0.005)
        for zz in (0.62, 0.72, 0.82):
            box(tuple(p + n * 0.025 + Vector((0, 0, zz - 0.72))), (0.11, 0.02, 0.018), "lead_new", rz=a + PI / 2,
                bevel=0)
    # the indexing plug: two pockets (the two fuel slots), turning half a turn a loop
    piv = pivot((CX, CY, CH + 0.05))
    cyl((0, 0, 0.1), 0.44, 0.2, "lead_new", verts=48, parent=piv)
    cyl((0, 0, 0.21), 0.46, 0.03, "dark_steel", verts=48, parent=piv)
    for s in (-1, 1):
        cyl((s * 0.22, 0, 0.235), 0.13, 0.03, "grey", verts=24, parent=piv)
        bolts(s * 0.22, 0, 0.255, 0.1, 6, r=0.012, parent=piv)
        torus((s * 0.22, 0, 0.27), 0.045, 0.01, "yellow", rot=(PI / 2, 0, 0), seg=12, parent=piv)
    box((0, 0, 0.235), (0.07, 0.62, 0.025), "hazard", bevel=0, parent=piv)
    spin(piv, 0.5, ease=lambda t: ease_index(t, 0.5))
    # its drive: a small geared motor on a bracket at the core's shoulder
    box((CX + 0.55, CY + 0.32, CH + 0.12), (0.2, 0.22, 0.12), "dark_steel")
    motor(CX + 0.62, CY + 0.36, CH + 0.3, d=(0, 1), s=0.6)
    label(1, "cell in: the indexing plug (2 pockets)", (CX, CY, CH + 0.3))
    label(2, "lead hot-core: the cell decays, heat", (CX - 0.3, CY - 0.55, 0.9))


# ---------------------------------------------------------------- the thermopile stacks
def stack(x, y, w, d, n=12, axis="x"):
    """A clamped stack of thermoelectric plates, ceramic and copper, the hot face open to
    the core so the isotope's light shows in every gap; tie rods, a clamp plate, terminals."""
    pitch, z0 = 0.095, 0.16
    box((x, y, 0.08), (w + 0.1, d + 0.1, 0.16), "dark_steel")
    box((x, y, z0 + n * pitch / 2), (w - 0.015, d - 0.015, n * pitch), "rg_gap", bevel=0)
    for k in range(n):
        z = z0 + k * pitch
        box((x, y, z + 0.02), (w, d, 0.04), "ceramic", bevel=0.005)
        box((x, y, z + 0.0475), (w + 0.01, d + 0.01, 0.015), "copper", bevel=0.003)
    zt = z0 + n * pitch
    box((x, y, zt + 0.04), (w + 0.08, d + 0.08, 0.08), "dark_steel", bevel=0.012)
    for sx in (-1, 1):
        for sy in (-1, 1):
            xx, yy = x + sx * (w / 2 + 0.02), y + sy * (d / 2 + 0.02)
            cyl((xx, yy, (zt + 0.1) / 2 + 0.04), 0.022, zt, "bare", verts=10)
            cyl((xx, yy, zt + 0.1), 0.035, 0.04, "bare", verts=6, bevel=0)
    # the DC terminals on the clamp plate
    for k in (-1, 1):
        o = 0.22 * k
        tx, ty = (x + o, y) if axis == "x" else (x, y + o)
        cyl((tx, ty, zt + 0.13), 0.05, 0.1, "ceramic", verts=16)
        cyl((tx, ty, zt + 0.2), 0.03, 0.06, "copper", verts=12)
    return zt


def stacks():
    zt = stack(CX, CY - 0.95, 1.0, 0.42, axis="x")          # south
    stack(CX - 0.96, CY, 0.42, 1.0, axis="y")               # west
    stack(CX + 0.96, CY, 0.42, 1.0, axis="y")               # east
    # the cold-side headers: a vertical pipe at each outer corner of every stack, ganged
    for (hx, hy) in ((CX - 0.55, CY - 1.2), (CX + 0.25, CY - 1.2), (CX - 1.21, CY - 0.4), (CX + 1.21, CY - 0.4),
                     (CX - 1.21, CY + 0.4), (CX + 1.21, CY + 0.4)):
        cyl((hx, hy, 0.72), 0.05, 1.12, "grey", verts=16)
        cyl((hx, hy, 1.3), 0.07, 0.06, "dark_steel", verts=16)
        cyl((hx, hy, 0.18), 0.07, 0.06, "dark_steel", verts=16)
    label(3, "thermopile stacks: heat to direct current", (CX - 0.25, CY - 1.15, 0.7))
    return zt


# ---------------------------------------------------------------- the cooling loop: pumps and radiators
def cooling(zt):
    # the radiators: two framed panels standing along the north edge, an expansion tank
    radiator(-1.9, -0.75, 1.72, 0.18, 1.62, mat="grey", fins=12)
    radiator(-0.6, 0.62, 1.72, 0.18, 1.62, mat="grey", fins=12)
    for x0 in (-1.9, -0.6):
        for xx in (x0 + 0.05, x0 + 1.1):
            box((xx, 1.72, 0.09), (0.08, 0.36, 0.18), "dark_steel")
    vtank(1.18, 1.52, 0.27, 0.95, "cream", bands=(0.45,), nozzle=(0.0, 0.0))
    # headers from the radiators to the stacks
    lagged([(-1.32, 1.62, 1.62), (-1.32, 1.2, 1.55), (CX - 1.21, CY + 0.4, 1.36)], r=0.075,
           marks=((0.5, "green"),))
    lagged([(0.0, 1.62, 1.62), (0.4, 1.25, 1.52), (CX + 1.21, CY + 0.4, 1.36)], r=0.075, marks=((0.5, "green"),))
    pipe([(1.18, 1.52, 1.12), (0.9, 1.4, 1.5), (0.62, 1.62, 1.55)], r=0.04, mat="copper")
    # the pumps: two sets at the south-west corner on one skid
    skid(-1.95, -1.95, -0.85, -1.15, 0.12)
    for py in (-1.75, -1.38):
        end = motor(-1.68, py, 0.32, d=(1, 0), s=0.75)
        coupling(end[0] + 0.05, py, 0.32, 0.1, axis=(1, 0, 0), turns=2)
        cyl((-1.15, py, 0.34), 0.15, 0.18, "dark_steel", rot=(0, PI / 2, 0), verts=24)
        cyl((-1.15, py, 0.52), 0.05, 0.14, "bare", verts=12)
    hose([(-1.15, -1.75, 0.6), (-1.0, -1.45, 0.95), (CX - 0.55, CY - 1.2, 1.3)], r=0.07, mat="hose")
    hose([(-1.15, -1.38, 0.6), (-1.3, -0.9, 0.95), (CX - 1.21, CY - 0.4, 1.3)], r=0.07, mat="hose_k")
    hose([(-1.75, -1.2, 0.3), (-1.85, -0.2, 0.4), (-1.85, 1.0, 0.5), (-1.6, 1.62, 0.4)], r=0.08, mat="hose")
    valve(-1.62, -0.85, 0.0, 0.5, wheel="yellow")
    label(4, "coolant pumps (cold side)", (-1.5, -1.55, 0.6))
    label(5, "radiator panels: heat leaves by radiation", (-0.7, 1.72, 1.3))


# ---------------------------------------------------------------- the rotary converter and the wire out
def converter(zt):
    skid(0.12, -1.95, 1.95, -1.05, 0.14)
    y = -1.5
    # the DC machine (oxide), its commutator end exposed to the west
    cyl((0.62, y, 0.48), 0.3, 0.5, "oxide", rot=(0, PI / 2, 0), verts=40)
    for xx in (0.42, 0.82):
        cyl((xx, y, 0.48), 0.32, 0.05, "dark_steel", rot=(0, PI / 2, 0), verts=40)
    box((0.62, y, 0.2), (0.5, 0.5, 0.12), "dark_steel")
    comm = pivot((0.3, y, 0.48), (0, PI / 2, 0))
    cyl((0, 0, 0), 0.2, 0.1, "copper", verts=24, parent=comm)
    for k in range(12):
        a = 2 * PI * k / 12
        box((0.2 * math.cos(a), 0.2 * math.sin(a), 0), (0.02, 0.03, 0.1), "dark", rz=a, bevel=0, parent=comm)
    box((0, 0, -0.06), (0.36, 0.06, 0.012), "hazard", bevel=0, parent=comm)
    spin(comm, 2)
    for a in (0.6, PI - 0.6):          # the brush gear: arms and holders
        box((0.28, y + 0.27 * math.cos(a), 0.48 + 0.27 * math.sin(a)), (0.06, 0.06, 0.1), "brass", rot=(a, 0, 0))
    torus((0.28, y, 0.48), 0.27, 0.014, "dark_steel", rot=(0, PI / 2, 0), seg=32)
    # the coupling and the AC alternator (oxide), its shaft end and a terminal box
    cyl((1.0, y, 0.48), 0.05, 0.2, "bare", rot=(0, PI / 2, 0), verts=12)
    coupling(1.04, y, 0.48, 0.14, axis=(1, 0, 0), turns=2)
    cyl((1.48, y, 0.5), 0.34, 0.58, "oxide", rot=(0, PI / 2, 0), verts=40)
    for k in range(6):
        torus((1.24 + 0.095 * k, y, 0.5), 0.345, 0.016, "oxide", rot=(0, PI / 2, 0), seg=40)
    box((1.48, y, 0.2), (0.6, 0.56, 0.12), "dark_steel")
    head(1.77, y, 0.5, 0.3, 0.1, "dark_steel").rotation_euler = (0, PI / 2, 0)
    box((1.5, y + 0.05, 0.92), (0.26, 0.22, 0.16), "grey")
    id_panel((1.5, y - 0.355, 0.5), 0.22, 0.14, stripe="yellow")
    hazard_tag((0.62, y - 0.315, 0.62), 0.24, 0.05)
    # the DC bus: copper bars on stand-offs from the stacks' terminals to the DC machine
    for (sx, sy) in ((CX + 0.22, CY - 0.95), (CX + 0.96, CY - 0.22)):
        pipe([(sx, sy, zt + 0.22), (sx + 0.15, sy - 0.2, zt + 0.3), (0.62, y + 0.15, 0.85), (0.62, y + 0.05, 0.76)],
             r=0.025, mat="copper", flanges=False)
    for (px, py) in ((0.75, -0.75), ):
        cyl((px, py, 0.55), 0.03, 1.0, "dark_steel", verts=8)
        cyl((px, py, 1.08), 0.06, 0.1, "ceramic", verts=12)
    # the terminal cabinet and the armoured trunks out (the wire leaves here)
    cabinet(1.55, -0.6, 0.62, 0.5, 1.05, mat="grey")
    gauge((1.4, -0.86, 0.75), (0, -1, 0.15), r=0.07, live=lambda t: 0.25 * math.sin(2 * PI * 3 * t))
    gauge((1.7, -0.86, 0.75), (0, -1, 0.15), r=0.07, live=lambda t: 0.12 * math.sin(2 * PI * 2 * t + 1))
    trunk([(1.5, y + 0.05, 1.0), (1.55, -1.0, 1.12), (1.55, -0.62, 1.08)], r=0.05)
    trunk([(1.8, -0.4, 0.4), (1.95, -0.2, 0.2), (1.98, 0.2, 0.08)], r=0.065)
    trunk([(1.75, -0.35, 0.65), (1.9, 0.1, 0.4), (1.92, 0.5, 0.08)], r=0.065)
    hazard_tag((1.55, -0.86, 0.98), 0.5, 0.05)
    label(6, "DC bus (copper)", (0.4, -0.95, 1.0))
    label(7, "rotary converter: DC motor drives AC alternator", (1.05, -1.5, 0.65))
    label(8, "terminal cabinet, armoured trunks: the wire", (1.75, -0.6, 1.05))


def clutter():
    # the spent-cell drawer: a lead box under a chute from the core (the burnt result)
    box((-1.62, -0.75, 0.22), (0.5, 0.42, 0.44), "lead", bevel=0.02)
    box((-1.62, -0.97, 0.22), (0.4, 0.02, 0.1), "hazard", bevel=0)
    handwheel((-1.62, -0.75, 0.52), 0.1)
    pipe([(CX - 0.55, CY - 0.4, 0.4), (-1.35, -0.55, 0.42), (-1.55, -0.7, 0.46)], r=0.07, mat="lead_new")
    # cables and a bundle along the south stack's foot to the pumps
    bundle([(0.3, -1.1, 0.16), (-0.4, -1.35, 0.16), (-0.9, -1.5, 0.3)], cols=("black", "red", "yellow"))
    bundle([(CX + 0.6, CY + 0.6, CH + 0.3), (0.8, 1.0, 1.3), (1.18, 1.3, 1.0)], cols=("grey", "black"))
    # instruments on the core's flank and the stacks
    gauge((CX - 0.5, CY - 0.62, 1.25), (-0.3, -1, 0.2), r=0.06, live=lambda t: 0.2 * math.sin(2 * PI * t))
    id_panel((CX, CY - 1.17, 1.32), 0.24, 0.1, stripe="red")
    hazard_tag((CX - 0.96, CY - 0.51, 1.32), 0.3, 0.05)
    ladder(CX + 0.52, CY + 0.42, 0.2, CH, axis="x", mat="ochre")
    # oil and wet dirt at the feet
    stain(-1.4, -1.55, 0.45, 0.25)
    stain(1.05, -1.95, 0.6, 0.12)
    stain(-1.6, -0.95, 0.2, 0.1)
    stain(1.55, -0.9, 0.3, 0.12)
    stain(-0.2, 1.5, 0.5, 0.12)


core()
zt = stacks()
cooling(zt)
converter(zt)
clutter()
run(dict(name="the thermopile stack", footprint=[4, 4]), nf=24)
