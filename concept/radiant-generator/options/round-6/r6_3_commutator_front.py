"""Radiant Generator, round 6, variant 3: THE COMMUTATOR FRONT (5 x 5). Plate-rack- and
converter-led.

  $BLENDER -b --python r6_3_commutator_front.py -- <out-dir> [--quick] [--only working|idle] [--colourmap]

The chain, cell to wire: cells go in through the two charging ports on the loading hood of
the carousel at the north; its collector head (west) reads each cell's charge; at the south
pocket the twin-hoist crane, running north-south down the middle, takes the fresh cell and
leaves the spent one, then runs south to the served well of the central crucible, whose
glazed plate rack (copper collector plates, the cells between) is the building's face.
Two banks of thermionic tubes stand on its east and west flanks. Plates and tubes feed the
DC bus to the switchgear at the west; the big rotary converter across the whole south
front, its open commutator and brush gear at the west end, makes AC; the transformer at
the south-east steps it up and the armoured trunks leave by the south edge. Spent cells
drop from the hood into the lead bin at the north-west.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r6_kit import *  # noqa: F401,F403,E402
import r6_kit as K  # noqa: E402

K.build_materials(((0.45, 0.3), (0.95, 0.35), (1.4, 0.3)))
lights([4, 4])

CX, CY, RR, ZD = 0.0, 1.35, 0.95, 0.7
ZR = 1.8
floor(notches=((-2.5, 1.99, -1.99, 2.5), (1.99, 1.99, 2.5, 2.5), (1.99, -0.4, 2.5, 0.1)))

car = carousel(CX, CY, RR, n=8, zd=ZD, pick_a=-PI / 2, L=4, drive_a=0.0, head_back=2)
P = car["pick"]
box((-1.3, 2.15, 0.3), (0.42, 0.46, 0.6), "lead", bevel=0.02)
box((-1.3, 2.15, 0.62), (0.46, 0.5, 0.05), "dark_steel")
handwheel((-1.3, 1.95, 0.7), 0.08)
label(11, "spent cells out: chute to the lead bin", (-1.3, 2.15, 0.65))

# the central crucible: the plate rack's glazing is the face
X0, X1, Y0, Y1, ZT = -1.0, 1.0, -1.05, 0.3, 1.05
W = crucible(X0, X1, Y0, Y1, ZT, well=(0.0, -0.62), slot=(-0.88, 0.88, -0.28, 0.2), hinge="S", plates="x")
TY = [-0.85 + 0.36 * i for i in range(4)]
for side, x in ((-1, -1.52), (1, 1.52)):
    box((x, -0.3, 0.06), (0.42, 1.5, 0.12), "dark_steel")
    for i, y in enumerate(TY):
        tube(x, y, 0.1, (0 if side < 0 else 4) + i, h=0.85, arm=(-side, 0), arm_len=0.36)
    pipe([(x - side * 0.22, TY[0] - 0.2, 1.22), (x - side * 0.22, TY[-1] + 0.2, 1.22)], r=0.03, mat="copper", flanges=False)
label(6, "thermionic tubes, two banks of four: the crucible's heat to current", (1.52, TY[1], 1.1))

# the crane, north-south down the middle, rails on posts beside the crucible
crane("y", (-1.2, 1.2), ZR, CX, P[1], W[1], P[2], W[2], -1.1, 1.3, d=0.38, label_n=4,
      rail_posts=(-1.05, 0.12, 1.25))

# the north-west shield housing with the coolant radiator, the north-east pump
housing(-2.45, 0.75, -1.25, 1.95, 1.35, mat="grey", roof="teal")
radiator(-2.4, -1.3, 0.72, 0.3, 1.25, mat="grey", fins=10)
label(12, "coolant radiator (the crucible jacket and tube caps)", (-1.85, 0.72, 1.0))
pv = motor(1.95, 2.1, 0.35, d=(1, 0), s=0.8)
coupling(pv[0] + 0.05, pv[1], pv[2], 0.1, axis=(1, 0, 0), turns=2)
cyl((pv[0] + 0.22, pv[1], 0.35), 0.16, 0.22, "oxide", rot=(0, PI / 2, 0), verts=32)
hose([(1.65, 1.9, 0.4), (1.5, 1.0, 0.5), (1.15, 0.2, 0.6)], r=0.07, mat="hose")
vtank(2.15, 0.75, 0.24, 1.0, "cream", bands=(0.5,), nozzle=(0.0, 0.0))
lagged([(1.95, 0.75, 0.9), (1.4, 0.55, 1.1), (1.0, 0.25, 1.0)], r=0.07)

# the DC bus west to the switchgear
tray([(-1.0, 0.2, 1.3), (-1.95, 0.2, 1.3), (-2.15, -0.2, 1.25)])
cabinet(-2.15, -0.55, 0.52, 0.62, 1.3, mat="grey")
cabinet(-2.15, 0.15, 0.52, 0.5, 1.1, mat="green")
gauge((-2.05, -0.87, 1.0), (0, -1, 0.15), r=0.06, live=lambda t: 0.2 * math.sin(2 * PI * t))
label(7, "DC bus and switchgear", (-2.15, -0.55, 1.3))

# the big rotary converter across the south front, commutator at the west (DC) end
cv = converter(-2.35, 1.0, -1.82, 0.72, R=0.52, dc_east=False)
bundle([(-2.15, -0.86, 0.9), (-2.1, -1.1, 1.2), (cv["com"][0], -1.2, 1.0), (cv["com"][0], -1.35, 0.8)],
       cols=("red", "black", "red"), r=0.028)

# the transformer SE, the trunks out of the south edge
tf = transformer(1.8, -1.75, 0.72, 1.0, 0.85, mat="cream")
trunk([cv["ac_top"], (0.6, -1.3, 1.4), (1.3, -1.5, 1.35), tf], r=0.05)
for x in (1.6, 2.0):
    trunk([(x, -2.2, 0.9), (x + 0.05, -2.4, 0.5), (x + 0.08, -2.49, 0.1)], r=0.065)
label(10, "armoured trunks: the wire", (2.0, -2.4, 0.5))

# clutter
for k, (x, y) in enumerate(((1.75, 1.55), (2.25, 1.6))):
    cyl((x, y, 0.3), 0.11, 0.6, ("green", "hazard")[k], verts=24)
    head(x, y, 0.6, 0.11, 0.06, "dark_steel")
jbox(2.2, -0.75, w=0.28, mat="grey", z=0.1)
bundle([(2.2, -0.75, 0.5), (2.0, -0.95, 0.3), (1.75, -1.15, 0.5)], cols=("black", "yellow"))
stain(0.0, -1.2, 0.6, 0.1)
stain(-1.6, 1.2, 0.2, 0.2)
stain(2.0, 0.3, 0.2, 0.3)
run(dict(name="the commutator front", footprint=[5, 5]), nf=32)
