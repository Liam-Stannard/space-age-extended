"""Radiant Generator, round 6, variant 2: THE CRANE HALL (5 x 5). Gantry- and tube-led.

  $BLENDER -b --python r6_2_crane_hall.py -- <out-dir> [--quick] [--only working|idle] [--colourmap]

The chain, cell to wire: cells go in through the two charging ports on the loading hood of
a small six-pocket carousel at the east end; its collector head reads each cell's charge
on the way round; at the west pocket the twin-hoist crane takes the fresh cell and leaves
the spent one, then runs the length of the hall (2.3 tiles) to the served well of a long
lead crucible. The cells stand between copper collector plates in the crucible (the plate
rack); twelve thermionic tubes in two rows along its flanks take its heat. Plates and
tubes feed the DC bus west to the switchgear; the rotary converter across the south front
makes AC, its commutator at the west end; the transformer at the south-east steps it up
and the armoured trunks leave by the east edge. Spent cells drop from the hood into the
lead bin at the east.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r6_kit import *  # noqa: F401,F403,E402
import r6_kit as K  # noqa: E402

K.build_materials(((0.45, 0.3), (0.95, 0.35), (1.4, 0.3)))
lights([6, 6])

CX, CY, RR, ZD = 1.62, 0.22, 0.8, 0.85
ZR = 1.8
floor(notches=((-2.5, -2.5, -1.99, -1.99), (1.99, 1.99, 2.5, 2.5), (-2.5, 1.0, -1.99, 1.5)))

car = carousel(CX, CY, RR, n=6, zd=ZD, pick_a=PI, L=2, drive_a=PI / 2, head_back=2)
P = car["pick"]
box((2.24, -0.78, 0.3), (0.4, 0.46, 0.6), "lead", bevel=0.02)
box((2.24, -0.78, 0.62), (0.44, 0.5, 0.05), "dark_steel")
handwheel((2.24, -0.98, 0.7), 0.08)
hazard_tag((2.24, -1.015, 0.4), 0.32, 0.05)
label(11, "spent cells out: chute to the lead bin", (2.24, -0.78, 0.65))

# the long crucible down the hall, its plate rack under the glazing at the west end
X0, X1, Y0, Y1, ZT = -2.05, 0.72, -0.3, 0.74, 1.0
W = crucible(X0, X1, Y0, Y1, ZT, well=(-1.2, CY), slot=(-0.75, 0.55, -0.15, 0.6), hinge="W", plates="x")
TX = [-1.85 + 0.48 * i for i in range(6)]
for row, (y, ad) in enumerate(((1.02, -1), (-0.58, 1))):
    box((-0.65, y, 0.06), (2.9, 0.42, 0.12), "dark_steel")
    for i, x in enumerate(TX):
        tube(x, y, 0.1, 6 * row + i, h=0.85, arm=(0, ad), arm_len=0.12)
    pipe([(TX[0] - 0.2, y, 1.42), (TX[-1] + 0.2, y, 1.42)], r=0.03, mat="copper", flanges=False)
label(6, "thermionic tubes, two rows of six: the crucible's heat to current", (TX[2], -0.58, 1.1))

# the crane: the north rail on the shield housing, the south rail on posts, the hall's length
housing(-2.45, 1.36, 2.45, 1.76, ZR - 0.06, mat="grey", roof="teal")
radiator(-2.3, 2.3, 1.34, 1.45, 1.68, mat="grey", fins=26)
label(12, "coolant radiator (the crucible jacket and tube caps)", (-0.3, 1.34, 1.55))
crane("x", (-0.96, 1.56), ZR, CY, P[0], W[0], P[2], W[2], -2.42, 2.42, d=0.38, label_n=4,
      rail_posts=(-2.38, -1.12, 0.12, 1.25, 2.38))

# the DC bus west to the switchgear
tray([(-2.05, -0.1, 1.25), (-2.3, -0.4, 1.25), (-2.3, -0.9, 1.15)])
cabinet(-2.2, -1.2, 0.5, 0.42, 1.25, mat="grey")
gauge((-2.1, -1.42, 0.95), (0, -1, 0.15), r=0.06, live=lambda t: 0.2 * math.sin(2 * PI * t))
label(7, "DC bus and switchgear", (-2.2, -1.2, 1.25))

# the rotary converter across the south front, commutator at the west (DC) end
cv = converter(-2.25, 0.95, -1.88, 0.62, R=0.42, dc_east=False)
bundle([(-2.2, -1.4, 1.1), (-2.05, -1.55, 1.05), (cv["com"][0], -1.45, 1.0), (cv["com"][0], -1.5, 0.9)],
       cols=("red", "black", "red"), r=0.025)

# the transformer SE, the trunks out of the east edge
tf = transformer(1.82, -1.85, 0.7, 0.9, 0.85, mat="cream")
trunk([cv["ac_top"], (0.9, -1.6, 1.25), (1.5, -1.7, 1.3), tf], r=0.05)
for k, y in enumerate((-1.55, -1.95)):
    trunk([(2.05, y, 1.0), (2.35, y - 0.05, 0.6), (2.49, y - 0.08, 0.1)], r=0.065)
label(10, "armoured trunks: the wire", (2.35, -1.6, 0.6))

# clutter: the drive's corner, the north-east pump, barrels, tanks, stains
pv = motor(2.15, 1.05, 0.35, d=(0, 1), s=0.8)
coupling(pv[0], pv[1] + 0.05, pv[2], 0.1, axis=(0, 1, 0), turns=2)
hose([(2.15, 0.85, 0.5), (2.35, 0.6, 0.8), (2.3, 1.3, 1.1)], r=0.06, mat="hose")
for k, (x, y) in enumerate(((0.95, -0.95), (1.18, -1.02))):
    cyl((x, y, 0.24), 0.1, 0.34, ("oxide", "green")[k], verts=20)
    torus((x, y, 0.33), 0.102, 0.01, "bare", seg=20)
jbox(1.0, -1.25, w=0.26, mat="grey", z=0.1)
tray([(-1.95, -1.08, 0.3), (0.8, -1.08, 0.3)], w=0.18, cols=("black", "yellow", "black"))
stain(-0.4, -1.1, 0.6, 0.12)
stain(1.4, -0.9, 0.3, 0.2)
stain(2.0, -2.4, 0.4, 0.1)
run(dict(name="the crane hall", footprint=[5, 5]), nf=32)
