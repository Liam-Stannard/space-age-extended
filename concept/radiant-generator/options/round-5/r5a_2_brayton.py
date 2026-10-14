"""Radiant Generator, round 5, suggestion 2: THE BRAYTON LOOP (4 x 4).

  $BLENDER -b --python r5a_2_brayton.py -- <out-dir> [--quick] [--only working|idle] [--colourmap]

A space-power closed Brayton loop. The chain, cell to wire: two cells sit in the lead
heat-source cask (its two charging ports are the two fuel slots); sealed gas is heated
round them and runs down the lagged hot duct into the radial turbine (the cream scroll);
the turbine turns the compressor and, through the coupling, an open-frame alternator
whose rotor is in plain sight; the exhaust gas gives up heat in the recuperator, sheds
the rest from the tilted radiator wing, and the compressor sends it back to the cask.
The alternator's output goes through the switchgear cabinet into the armoured trunks.

Unlike the Siderane turbine (one long riveted barrel with a bladed rotor face looking
up): a train of separate machines on a skid, the rotor seen side-on as a drum of
painted poles, and the mass of the building in the heat-source cask and the radiator
wing. The isotope's light: five sight slots round the cask's head, nowhere else.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r5a_kit import *  # noqa: F401,F403,E402
import r5a_kit as K  # noqa: E402

KX, KY, KR, KH = -1.18, 0.62, 0.6, 1.5
AY, AZ = -1.32, 0.52            # the machine train's axis
K.build_materials(((0.55, 0.3), (1.1, 0.35), (1.5, 0.3)))
radiant("rg_slot", "flow", scale=4.0, k=1, bright=2.0, fn=lambda t: 0.82 + 0.18 * math.sin(2 * PI * t))


def cask():
    """The heat-source cask: lead, banded, a heavy head with two charging ports; the gas
    in and out at its shoulder; three sight slots in a cast ring round its head."""
    cyl((KX, KY, 0.08), KR + 0.14, 0.16, "dark_steel", verts=64)
    bolts(KX, KY, 0.17, KR + 0.08, 16)
    cyl((KX, KY, KH / 2 + 0.08), KR, KH - 0.16, "lead", verts=64)
    for z in (0.45, 1.35):
        vessel_band(KX, KY, z, KR, n_rivets=14, lug_a=-PI / 2 + 0.5)
    weld_ring(KX, KY, 0.82, KR)
    # the cast slot ring and its three slots
    ZS = KH - 0.42
    cyl((KX, KY, ZS), KR + 0.05, 0.3, "dark_steel", verts=64)
    for a in (-PI / 2 - 1.1, -PI / 2 - 0.55, -PI / 2, -PI / 2 + 0.55, -PI / 2 + 1.1):
        n = Vector((math.cos(a), math.sin(a), 0))
        p = Vector((KX, KY, ZS)) + n * (KR + 0.055)
        box(tuple(p), (0.26, 0.02, 0.2), "rg_slot", rz=a + PI / 2, bevel=0)
        for dz in (-0.1, 0.1):
            box(tuple(p + n * 0.015 + Vector((0, 0, dz))), (0.3, 0.05, 0.04), "lead_new", rz=a + PI / 2, bevel=0)
        box(tuple(p + n * 0.02), (0.28, 0.02, 0.02), "lead_new", rz=a + PI / 2, bevel=0)
    head(KX, KY, KH, KR + 0.02, 0.22, "lead")
    flange_ring(KX, KY, KH + 0.01, KR - 0.02, mat="bare", h=0.05, nb=18)
    for s in (-1, 1):                 # the two charging ports: lead plugs with yellow lifting eyes
        px, py = KX + s * 0.24, KY + 0.06
        cyl((px, py, KH + 0.2), 0.14, 0.12, "dark_steel", verts=32)
        cyl((px, py, KH + 0.28), 0.12, 0.06, "lead_new", verts=32)
        bolts(px, py, KH + 0.32, 0.09, 6, r=0.012)
        torus((px, py, KH + 0.36), 0.04, 0.01, "yellow", rot=(PI / 2, 0, 0), seg=12)
    id_panel((KX + 0.25, KY - KR - 0.01, 0.82), 0.22, 0.12, stripe="red")
    ladder(KX + KR * 0.7 + 0.05, KY - KR * 0.7 - 0.05, 0.2, KH, axis="y", mat="ochre")
    label(1, "cells in: two charging ports (the fuel slots)", (KX, KY + 0.06, KH + 0.3))
    label(2, "lead heat-source cask: the cells heat the gas", (KX - 0.3, KY - KR, 0.7))


def train():
    """Compressor, turbine, coupling, open-frame alternator, exciter: one shaft, one skid."""
    skid(-1.15, AY - 0.45, 1.95, AY + 0.45, 0.14)
    # the compressor: a grey scroll and its inlet bell
    cyl((-0.82, AY, AZ), 0.3, 0.22, "grey", rot=(0, PI / 2, 0), verts=40)
    torus((-0.82, AY, AZ), 0.3, 0.09, "grey", rot=(0, PI / 2, 0), seg=40)
    cone((-1.04, AY, AZ), 0.2, 0.12, 0.2, "bare", rot=(0, PI / 2, 0), verts=32)
    box((-0.82, AY, 0.22), (0.3, 0.6, 0.18), "dark_steel")
    # the turbine: a cream scroll, its hot inlet up into the lagged duct
    cyl((-0.3, AY, AZ + 0.02), 0.34, 0.26, "cream", rot=(0, PI / 2, 0), verts=40)
    torus((-0.3, AY, AZ + 0.02), 0.34, 0.11, "cream", rot=(0, PI / 2, 0), seg=40)
    rivet_x = [(-0.3 + 0.13 * s) for s in (-1, 1)]
    for xx in rivet_x:
        for k in range(12):
            a = 2 * PI * k / 12
            sphere((xx, AY + 0.3 * math.cos(a), AZ + 0.02 + 0.3 * math.sin(a)), 0.016, "bolt", seg=8)
    cyl((-0.3, AY + 0.1, AZ + 0.5), 0.12, 0.3, "cream", verts=24)
    box((-0.3, AY, 0.22), (0.36, 0.62, 0.18), "dark_steel")
    # shaft and the coupling: both seen turning
    cyl((0.1, AY, AZ), 0.05, 0.6, "bare", rot=(0, PI / 2, 0), verts=12)
    coupling(0.12, AY, AZ, 0.15, axis=(1, 0, 0), turns=2)
    # the open-frame alternator: ochre end frames and bars, the rotor in sight
    x0, x1, R = 0.38, 1.42, 0.38
    for xx in (x0, x1):
        annulus((xx, AY, AZ + 0.04), 0.3, R + 0.06, 0.1, "ochre", rot=(0, PI / 2, 0))
        box((xx, AY, 0.25), (0.14, 0.82, 0.22), "ochre", bevel=0.012)
        bolts_x = 10
        for k in range(bolts_x):
            a = 2 * PI * (k + 0.5) / bolts_x
            sphere((xx + (0.055 if xx == x1 else -0.055), AY + (R + 0.02) * math.cos(a),
                    AZ + 0.04 + (R + 0.02) * math.sin(a)), 0.016, "bolt", seg=8)
    for k in range(8):                       # the stator bars, laminated, wound in copper
        a = 2 * PI * (k + 0.5) / 8
        if -2.4 < a - PI < -0.75 or k in (0, 7):
            pass
        cyl(((x0 + x1) / 2, AY + (R - 0.02) * math.cos(a), AZ + 0.04 + (R - 0.02) * math.sin(a)), 0.035,
            x1 - x0 - 0.08, "ochre", rot=(0, PI / 2, 0), verts=10)
    rot = pivot(((x0 + x1) / 2, AY, AZ + 0.04), (0, PI / 2, 0))
    cyl((0, 0, 0), 0.2, x1 - x0 - 0.16, "dark_steel", verts=32, parent=rot)
    for k in range(4):                       # four poles: red and copper, so the turn reads
        a = 2 * PI * k / 4
        box((0.22 * math.cos(a), 0.22 * math.sin(a), 0), (0.08, 0.17, x1 - x0 - 0.2),
            "red" if k % 2 else "copper", rz=a, bevel=0.01, parent=rot)
        for z in (-0.38, 0.38):
            box((0.25 * math.cos(a), 0.25 * math.sin(a), z), (0.05, 0.19, 0.04), "bare", rz=a, bevel=0.004,
                parent=rot)
    spin(rot, 1)
    cyl((x1 + 0.1, AY, AZ + 0.04), 0.06, 0.2, "bare", rot=(0, PI / 2, 0), verts=12)
    # the exciter: slip rings and brushes, exposed, on its own pedestal
    ex = pivot((1.62, AY, AZ + 0.04), (0, PI / 2, 0))
    for k in range(3):
        cyl((0, 0, -0.08 + 0.08 * k), 0.13, 0.05, "copper" if k != 1 else "brass", verts=24, parent=ex)
    box((0, 0.13, 0.0), (0.05, 0.03, 0.22), "hazard", bevel=0, parent=ex)
    spin(ex, 2)
    for k in range(3):
        box((1.54 + 0.08 * k, AY, AZ + 0.22), (0.035, 0.06, 0.1), "dark", bevel=0)
    box((1.62, AY, AZ + 0.3), (0.3, 0.12, 0.04), "dark_steel", bevel=0.004)
    box((1.62, AY, 0.28), (0.3, 0.4, 0.28), "dark_steel")
    head(1.86, AY, AZ + 0.04, 0.16, 0.08, "dark_steel").rotation_euler = (0, PI / 2, 0)
    gauge((0.9, AY - 0.44, 0.26), (0, -1, 0.3), r=0.06, live=lambda t: 0.15 * math.sin(2 * PI * 2 * t))
    hazard_tag((0.9, AY - 0.455, 0.12), 0.6, 0.05)
    label(4, "radial turbine: gas spins the shaft", (-0.3, AY, AZ + 0.3))
    label(5, "open-frame alternator: rotor in sight", ((x0 + x1) / 2, AY, AZ + 0.5))


def loop():
    """The gas loop: hot duct, recuperator, radiator wing, return."""
    # the lagged hot duct from the cask's shoulder down into the turbine's inlet
    lagged([(KX + 0.5, KY - 0.3, 1.18), (-0.35, -0.2, 1.15), (-0.3, AY + 0.1, 1.05), (-0.3, AY + 0.1, 0.72)],
           r=0.13, marks=((0.35, "red"),))
    # the recuperator: a grey shell lying E-W in the middle, channel heads, nozzles
    yr, zr = 0.05, 0.62
    cyl((0.42, yr, zr), 0.34, 1.0, "grey", rot=(0, PI / 2, 0), verts=48)
    for xx, s in ((-0.08, -1), (0.92, 1)):
        h = head(xx, yr, zr, 0.34, 0.12, "grey")
        h.rotation_euler = (0, s * PI / 2, 0)
        cyl((xx, yr, zr), 0.4, 0.07, "dark_steel", rot=(0, PI / 2, 0), verts=48)
        for k in range(10):
            a = 2 * PI * k / 10
            cyl((xx, yr + 0.37 * math.cos(a), zr + 0.37 * math.sin(a)), 0.014, 0.09, "bare",
                rot=(0, PI / 2, 0), verts=6, bevel=0)
    for xx in (0.15, 0.7):
        box((xx, yr, 0.18), (0.1, 0.5, 0.36), "dark_steel")
    weld_ring_x = [0.42]
    for xx in weld_ring_x:
        torus((xx, yr, zr), 0.345, 0.01, "seam", rot=(0, PI / 2, 0), seg=48)
    stencil((0.42, yr - 0.345, zr + 0.05), (0.42, 0.01, 0.1))
    # turbine exhaust -> recuperator; recuperator -> radiator wing; compressor -> recuperator -> cask
    hose([(-0.12, AY + 0.25, 0.75), (-0.1, -0.7, 0.85), (-0.08, yr - 0.15, 0.85)], r=0.1, mat="hose")
    pipe([(0.92, yr + 0.1, zr + 0.25), (1.0, 0.4, 1.0), (1.05, 0.7, 1.15)], r=0.08, mat="bare",
         marks=((0.5, "yellow"),))
    hose([(-0.82, AY + 0.3, 0.75), (-0.75, -0.5, 0.7), (-0.6, -0.1, 0.62), (-0.12, yr + 0.15, 0.7)], r=0.08,
         mat="hose_k")
    lagged([(0.0, yr + 0.3, 0.85), (-0.35, 0.65, 0.8), (KX + KR - 0.02, KY + 0.05, 0.75)], r=0.085,
           marks=((0.5, "green"),))
    # the radiator wing: four panels tilted to the sky on a frame (heat leaves by radiation)
    x0, x1, y0, y1 = 0.12, 1.94, 0.75, 1.95
    for xx in (x0 + 0.05, x1 - 0.05):
        for yy, h in ((y0 + 0.06, 0.4), (y1 - 0.06, 1.05)):
            box((xx, yy, h / 2), (0.07, 0.07, h), "dark_steel", bevel=0.006)
    tilt = math.atan2(1.05 - 0.4, y1 - y0)
    L = math.hypot(1.05 - 0.4, y1 - y0)
    piv = pivot(((x0 + x1) / 2, (y0 + y1) / 2, (0.4 + 1.05) / 2 + 0.04), (tilt, 0, 0))
    W = x1 - x0
    box((0, 0, 0), (W, L, 0.04), "dark_steel", bevel=0.006, parent=piv)
    for k in range(4):
        cx = -W / 2 + W * (k + 0.5) / 4
        box((cx, 0, 0.03), (W / 4 - 0.05, L - 0.08, 0.015), "teal", bevel=0.004, parent=piv)
        for j in range(9):
            box((cx, -L / 2 + 0.08 + (L - 0.16) * j / 8, 0.045), (W / 4 - 0.08, 0.018, 0.02), "dark_steel",
                bevel=0.003, parent=piv)
        for j in range(7):
            cyl((cx, -L / 2 + 0.1 + (L - 0.2) * j / 6, 0.05), 0.016, W / 4 - 0.1, "copper", rot=(0, PI / 2, 0),
                verts=8, bevel=0, parent=piv)
        cyl((cx - W / 8 + 0.04, 0, 0.05), 0.02, L - 0.12, "copper", rot=(PI / 2, 0, 0), verts=8, bevel=0, parent=piv)
        cyl((cx + W / 8 - 0.04, 0, 0.05), 0.02, L - 0.12, "copper", rot=(PI / 2, 0, 0), verts=8, bevel=0, parent=piv)
    for k in range(5):
        box((-W / 2 + W * k / 4, 0, 0.04), (0.04, L, 0.05), "bare", bevel=0.004, parent=piv)
    pipe([(x0 + 0.1, y0 + 0.05, 0.6), (x0 + 0.1, 0.4, 0.45), (-0.6, -0.55, 0.4), (-0.82, AY + 0.25, 0.5)],
         r=0.07, mat="bare", marks=((0.3, "green"), (0.7, "green")))
    label(3, "recuperator (gas to gas)", (0.42, yr - 0.34, zr))
    label(6, "radiator wing: the loop's heat leaves by radiation", (1.0, 1.3, 1.0))
    label(7, "compressor: gas back to the cask", (-0.95, AY, AZ + 0.3))


def switchgear():
    cabinet(1.6, -0.3, 0.62, 0.48, 1.1, mat="grey")
    gauge((1.45, -0.55, 0.78), (0, -1, 0.15), r=0.07, live=lambda t: 0.3 * math.sin(2 * PI * t))
    gauge((1.75, -0.55, 0.78), (0, -1, 0.15), r=0.07, live=lambda t: 0.1 * math.sin(2 * PI * 4 * t))
    id_panel((1.6, -0.545, 0.52), 0.3, 0.12, stripe="yellow")
    trunk([(1.0, AY + 0.3, 0.95), (1.25, -0.8, 1.15), (1.45, -0.3, 1.12)], r=0.055)
    trunk([(1.85, -0.2, 0.5), (1.97, 0.05, 0.25), (1.99, 0.4, 0.08)], r=0.065)
    trunk([(1.8, -0.15, 0.75), (1.93, 0.25, 0.4), (1.94, 0.55, 0.08)], r=0.065)
    label(8, "switchgear, armoured trunks: the wire", (1.6, -0.3, 1.1))


def clutter():
    # the gas make-up bottles and a valve station at the cask's foot (west)
    for k, yy in enumerate((-0.1, 0.12)):
        cyl((-1.82, yy, 0.42), 0.1, 0.84, "green" if k else "grey", verts=24)
        head(-1.82, yy, 0.84, 0.1, 0.05, "dark_steel")
        cyl((-1.82, yy, 0.92), 0.025, 0.08, "brass", verts=8)
    box((-1.82, 0.01, 0.3), (0.28, 0.5, 0.05), "dark_steel")
    hose([(-1.82, -0.1, 0.96), (-1.6, -0.2, 1.0), (KX - 0.3, KY - KR + 0.05, 0.9)], r=0.035, mat="hose_k")
    valve(-1.45, -0.45, 0.0, 0.48, wheel="red")
    valve(-1.15, -0.62, 0.0, 0.42, wheel="yellow")
    bundle([(-1.0, AY + 0.4, 0.2), (-1.4, -0.75, 0.15), (KX - 0.2, KY - KR - 0.05, 0.3)], cols=("black", "red"))
    bundle([(1.5, -0.55, 0.2), (1.2, AY + 0.45, 0.15), (0.7, AY + 0.45, 0.15)], cols=("grey", "yellow", "black"))
    jbox(-1.7, 1.55, mat="green")
    pipe([(KX - 0.4, KY + 0.45, 1.2), (-1.65, 1.5, 0.9), (-1.7, 1.55, 0.5)], r=0.03, mat="copper", flanges=False)
    status_lamp(KX + 0.4, KY - 0.2, KH + 0.18)
    stain(-0.4, AY - 0.45, 0.7, 0.12)
    stain(1.2, AY - 0.45, 0.5, 0.1)
    stain(-1.5, -0.55, 0.3, 0.2)
    stain(1.0, 0.65, 0.5, 0.15)


cask()
train()
loop()
switchgear()
clutter()
run(dict(name="the brayton loop", footprint=[4, 4]), nf=24)
