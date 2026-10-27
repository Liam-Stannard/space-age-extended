"""Radiant Generator, round 5, suggestion 10: THE GOVERNED GYRE (4x4).

Round 4's Gyre Spire cut down to a generator: its core and counter-rotating shutter
bands kept as the regulator -- the bands open and close the core's light on the heat
exchanger round it -- under a lead lid on three posts; no column, no masts, no arcs, no
beams (those are left for the Reactor). The heat goes out in a sealed gas loop to a
compact turbine-alternator skid along the south edge.

  cell magazine (W, ochre) -> lead chute -> shield pot (lead) -> core, in the shutter
  bands (turning) -> exchanger jacket round the pot -> hot leg (lagged) -> turbine (dark
  steel) -> coupling -> alternator (green; slip rings and brushes open on its east end)
  -> breaker cabinet (SE, cream) -> cable trunks;  turbine exhaust -> radiator banks (N, E)
  -> circulator pump -> back to the jacket.

  $BLENDER -b --python r5b_10_small_gyre.py -- <out-dir> [--quick] [--only idle|working]
Not a model; nothing is adopted.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r5b_kit import *  # noqa: E402,F401,F403
from r5b_kit import _finish  # noqa: E402

W, H = 4, 4
GX, GY = -0.1, 0.38           # the gyre's axis
RS, HS = 0.86, 0.82           # the shield pot
CZ = HS + 0.5                 # the core's centre


def ring_seg(cx, cy, r0, r1, z0, z1, a0, a1, mat, parent=None, seg=12):
    """A curved band segment (round 4's band(), rebuilt for this kit), local to parent."""
    me = bpy.data.meshes.new("seg")
    bm = bmesh.new()
    vs = []
    for k in range(seg + 1):
        a = a0 + (a1 - a0) * k / seg
        c, s = math.cos(a), math.sin(a)
        vs.append([bm.verts.new((cx + r * c, cy + r * s, z)) for r, z in ((r0, z0), (r1, z0), (r1, z1), (r0, z1))])
    for k in range(seg):
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((vs[k][i], vs[k + 1][i], vs[k + 1][j], vs[k][j]))
    bm.faces.new(list(reversed(vs[0])))
    bm.faces.new(vs[-1])
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("seg", me)
    sc.collection.objects.link(o)
    return _finish(o, mat, 0.006, smooth=True, parent=parent)


def shield():
    """The lead shield pot, banded and bolted, the exchanger jacket's ring header round
    its shoulder, the core in its bands on top under the lid."""
    cyl((GX, GY, 0.09), RS + 0.14, 0.18, "dark_steel", verts=72)
    bolts(GX, GY, 0.19, RS + 0.08, 20, r=0.02)
    cyl((GX, GY, HS / 2 + 0.1), RS, HS - 0.02, "lead", verts=96)
    for z in (0.35, 0.72):
        vessel_band(GX, GY, z, RS, n_rivets=14, lug_a=-PI / 2 - 0.5)
    weld_ring(GX, GY, 0.55, RS)
    cyl((GX, GY, HS + 0.08), RS - 0.08, 0.1, "dark_steel", verts=96)
    flange_ring(GX, GY, HS + 0.13, RS - 0.12, mat="bare", h=0.04, nb=20)
    torus((GX, GY, HS - 0.05), RS + 0.09, 0.06, "bare", seg=96)                       # jacket ring header
    for k in range(8):
        a = 2 * PI * (k + 0.5) / 8
        cyl((GX + (RS + 0.06) * math.cos(a), GY + (RS + 0.06) * math.sin(a), HS - 0.2), 0.045, 0.3, "bare", verts=12)
    insp_plate(GX, GY, RS, -PI / 2 - 0.3, 0.42, 0.66, 0.22, mat="lead_new")
    # the core and its bands
    sphere((GX, GY, CZ), 0.22, glowmat("core", "#3F86FF", 1.0, pulse=lambda t: 0.85 + 0.15 * math.sin(2 * PI * t),
                                       base="#22324E"), seg=32)
    cyl((GX, GY, HS + 0.2), 0.1, 0.16, "lead", verts=24)
    point((GX, GY, CZ), 26.0, radius=0.1, pulse=lambda t: 0.85 + 0.15 * math.sin(2 * PI * t))
    inner = pivot((GX, GY, 0))
    for q in range(4):
        a0 = q * PI / 2
        ring_seg(0, 0, 0.34, 0.39, CZ - 0.3, CZ + 0.34, a0, a0 + math.radians(56), "lead", parent=inner)
        for z in (CZ - 0.3, CZ + 0.3):
            ring_seg(0, 0, 0.385, 0.41, z, z + 0.04, a0, a0 + math.radians(56), "copper", parent=inner)
    outer = pivot((GX, GY, 0))
    for q in range(6):
        a0 = q * PI / 3
        ring_seg(0, 0, 0.5, 0.56, CZ - 0.24, CZ + 0.18, a0, a0 + math.radians(36), "green", parent=outer)
        ring_seg(0, 0, 0.555, 0.575, CZ - 0.04, CZ + 0.02, a0, a0 + math.radians(36), "bare", parent=outer)
    torus((GX, GY, CZ - 0.32), 0.56, 0.03, "dark_steel", seg=72)
    gim = pivot((GX, GY, CZ))
    tilt = pivot((0, 0, 0), (math.radians(22), 0, 0), parent=gim)
    torus((0, 0, 0), 0.455, 0.018, "copper", seg=64, parent=tilt)
    for q in range(3):
        a = q * 2 * PI / 3
        box((0.455 * math.cos(a), 0.455 * math.sin(a), 0), (0.07, 0.08, 0.07), "dark_steel", rz=a, parent=tilt)
    spin(inner, "Z", 0.25)
    spin(outer, "Z", -1 / 6)
    spin(gim, "Z", 1 / 3)
    # the lid: a lead disc on three posts, the core seen only between the bands
    LZ = CZ + 0.5
    for k in range(3):
        a = PI / 2 + 2 * PI * k / 3
        px, py = GX + 0.68 * math.cos(a), GY + 0.68 * math.sin(a)
        cyl((px, py, (HS + 0.13 + LZ) / 2), 0.04, LZ - HS - 0.13, "bare", verts=16)
        cyl((px, py, HS + 0.17), 0.08, 0.06, "dark_steel", verts=16)
        box((GX + 0.46 * math.cos(a), GY + 0.46 * math.sin(a), LZ + 0.02), (0.48, 0.06, 0.05), "dark_steel", rz=a,
            bevel=0.006)
    cyl((GX, GY, LZ + 0.04), 0.26, 0.08, "lead", verts=48)
    head(GX, GY, LZ + 0.08, 0.26, 0.1, "lead")
    flange_ring(GX, GY, LZ + 0.08, 0.22, mat="bare", h=0.03, nb=10)
    cyl((GX + 0.06, GY - 0.05, LZ + 0.2), 0.04, 0.1, "bare", verts=12)
    cyl((GX + 0.06, GY - 0.05, LZ + 0.26), 0.06, 0.03, "brass", verts=6, bevel=0)


def magazine():
    mx, my = -1.62, 0.3
    box((mx, my, 0.6), (0.6, 0.8, 1.2), "ochre", bevel=0.025)
    box((mx, my, 1.23), (0.66, 0.86, 0.06), "dark_steel", bevel=0.01)
    for dy in (-0.18, 0.18):
        cyl((mx, my + dy, 1.3), 0.11, 0.08, "lead", verts=6, bevel=0.005)
    box((mx, my - 0.41, 0.7), (0.42, 0.02, 0.08), "hazard", bevel=0)
    id_panel((mx, my - 0.41, 0.92), 0.24, 0.12, stripe="green")
    gauge((mx + 0.15, my - 0.42, 0.45), (0, -1, 0.2), r=0.05)
    pipe([(mx + 0.3, my, 0.95), (-1.05, GY, 0.9), (GX - RS + 0.02, GY, 0.62)], r=0.1, mat="lead")
    bx, by = -1.6, -0.55
    box((bx, by, 0.22), (0.56, 0.48, 0.38), "lead", bevel=0.02)
    box((bx, by, 0.42), (0.48, 0.4, 0.03), "dark", bevel=0)
    for k, (dx, dy) in enumerate(((-0.1, -0.05), (0.08, 0.06), (0.12, -0.1))):
        spent_cell((bx + dx, by + dy, 0.47), (1, 0.4 * (k - 1), 0.1), r=0.06, h=0.27)
    box((bx, by - 0.25, 0.2), (0.36, 0.02, 0.08), "hazard", bevel=0)


def skid_set():
    """Along the south edge: turbine (dark steel volute), a turning coupling, the
    alternator (green, ribbed) with its slip rings and brushes open on the east end."""
    skid(-1.3, -1.92, 1.05, -1.05, 0.12)
    y, z = -1.48, 0.48
    cyl((-0.9, y, z), 0.3, 0.38, "dark_steel", rot=(0, PI / 2, 0), verts=48)
    for xx in (-1.08, -0.72):
        cyl((xx, y, z), 0.33, 0.04, "bare", rot=(0, PI / 2, 0), verts=48)
    cyl((-0.9, y + 0.1, z + 0.32), 0.1, 0.16, "bare", verts=16)
    flange_ring(-0.9, y + 0.1, z + 0.4, 0.09, mat="bare", h=0.03, nb=8)
    box((-0.9, y, 0.2), (0.4, 0.62, 0.16), "dark_steel")
    coupling(-0.5, y, z, 0.13, axis=(1, 0, 0))
    cyl((0.15, y, z), 0.36, 0.95, "green", rot=(0, PI / 2, 0), verts=64)
    for k in range(12):
        cyl((-0.28 + 0.078 * k, y, z), 0.375, 0.022, "dark_steel", rot=(0, PI / 2, 0), verts=64, bevel=0)
    box((0.15, y, 0.2), (0.85, 0.64, 0.16), "dark_steel")
    box((0.15, y + 0.15, z + 0.38), (0.36, 0.22, 0.14), "grey", bevel=0.01)                 # terminal box
    stencil((0.15, y - 0.37, z + 0.05), (0.4, 0.01, 0.08), 0.0)
    R = pivot((0.68, y, z), (0, PI / 2, 0))
    cyl((0, 0, 0.0), 0.06, 0.26, "bare", verts=16, parent=R)
    for zz in (-0.06, 0.02, 0.1):
        cyl((0, 0, zz), 0.13, 0.045, "copper", verts=32, parent=R)
    cyl((0, 0, 0.16), 0.15, 0.03, "dark_steel", verts=32, parent=R)
    box((0, 0, 0.18), (0.26, 0.04, 0.012), "hazard", bevel=0, parent=R)
    spin(R, "Z", 0.5)
    box((0.7, y + 0.2, z + 0.12), (0.26, 0.06, 0.06), "dark_steel", bevel=0.004)             # brush arm
    for zz in (-0.08, 0.0, 0.08):
        box((0.68 + zz, y + 0.14, z + 0.1), (0.035, 0.06, 0.05), "brass", bevel=0.004)
    meter((-0.9, y - 0.33, z + 0.1), (0, -1, 0.25), r=0.07,
          swing=lambda t: 0.2 + 0.08 * math.sin(2 * PI * t))
    # the hot leg from the jacket header over to the turbine's inlet
    lagged([(GX + 0.35, GY - RS - 0.08, HS - 0.05), (GX + 0.1, -0.85, 0.95), (-0.65, -1.1, 1.0),
            (-0.9, y + 0.1, z + 0.46)], r=0.1, marks=((0.5, "red"),))
    bundle([(0.15, y + 0.2, z + 0.45), (0.7, -1.0, 0.7), (1.25, -1.1, 0.95)], cols=("red", "black", "yellow"))


def breaker():
    cx, cy = 1.52, -1.35
    box((cx, cy, 0.55), (0.66, 0.9, 1.1), "cream", bevel=0.02)
    box((cx, cy, 1.13), (0.7, 0.94, 0.06), "dark_steel", bevel=0.01)
    meter((cx - 0.1, cy - 0.46, 0.75), (0, -1, 0.1), r=0.12,
          swing=lambda t: 0.3 + 0.12 * math.sin(2 * PI * t) + 0.04 * math.sin(6 * PI * t))
    for i in range(4):
        box((cx + 0.05, cy - 0.46, 0.3 + 0.07 * i), (0.4, 0.02, 0.025), "dark_steel", bevel=0)
    status_lamp(cx + 0.18, cy - 0.2, 1.18)
    handwheel((cx + 0.2, cy - 0.5, 0.72), 0.07, axis=(0, -1, 0), mat="red")
    hazard_tag((cx, cy - 0.46, 0.18), 0.4, 0.05)
    for k, dy in enumerate((-0.2, 0.05, 0.3)):
        hose([(cx + 0.33, cy + dy, 0.6), (1.9, cy + dy + 0.05, 0.45), (1.96, cy + dy + 0.1, 0.1),
              (1.98, cy + dy + 0.1, -0.05)], r=0.055, mat="hose_k")


def cooling():
    """Radiator banks along the north and the east, the circulator pump, an expansion tank
    in the north-east corner; the exhaust from the turbine back round the west side."""
    radiator_bank(-1.35, 0.95, 1.5, 1.95, 0.1, 0.95, 12, mat="grey", along_x=True)
    radiator_bank(1.25, 1.85, -0.55, 1.05, 0.1, 0.95, 8, mat="grey", along_x=False)
    vtank(1.58, 1.58, 0.3, 1.05, "cream", bands=(0.5,), top="dark_steel", nozzle=(0.2, -0.2))
    hose([(-1.1, -1.25, 0.6), (-1.35, -0.7, 0.5), (-1.25, 0.95, 0.5), (-1.0, 1.42, 0.4)], r=0.09, mat="hose")
    hose([(1.0, 1.55, 0.35), (0.9, 1.15, 0.45), (GX + 0.6, GY + 0.6, HS - 0.05)], r=0.09, mat="hose_k")
    hose([(1.2, 0.6, 0.3), (0.95, 0.25, 0.4), (GX + RS + 0.06, GY - 0.1, HS - 0.1)], r=0.09, mat="hose_k")
    pump(0.95, -0.55, (0, 1), 0.55)
    valve(0.55, 1.2, 0.0, 0.42, wheel="yellow")


shield()
magazine()
skid_set()
breaker()
cooling()
stain(-0.2, -1.95, 0.6, 0.1)
stain(1.4, -1.9, 0.3, 0.1)
stain(-1.6, -0.9, 0.25, 0.12)
stain(0.9, -0.85, 0.25, 0.15)
run(W, H, name="10-the-governed-gyre")
