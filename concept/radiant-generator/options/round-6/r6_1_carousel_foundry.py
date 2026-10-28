"""Radiant Generator, round 6, variant 1: THE CAROUSEL FOUNDRY (5 x 5). Carousel-led.

  $BLENDER -b --python r6_1_carousel_foundry.py -- <out-dir> [--quick] [--only working|idle] [--colourmap]

The chain, cell to wire: cells go in through the two charging ports on the carousel's lead
loading hood (the two fuel slots) and round on the great turntable, the west half of the
building; the collector head over the south pocket reads each cell's charge as it passes;
at the east pocket the twin-hoist crane takes the fresh cell (hoist A) and leaves the spent
one (hoist B), runs east and changes them over in the crucible's served well. In the lead
crucible the cells stand between copper collector plates (the plate rack); the thermionic
tubes on its south flank take its heat. Plates and tubes feed the DC bus to the switchgear,
the rotary converter makes AC, the transformer steps it up, the armoured trunks take it
out at the south-west. Spent cells leave the loading hood by the chute into the lead bin.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r6_kit import *  # noqa: F401,F403,E402
import r6_kit as K  # noqa: E402

K.build_materials(((0.45, 0.3), (0.95, 0.35), (1.4, 0.3)))
lights([5])

CX, CY, RR, ZD = -1.05, 0.45, 1.25, 0.85
ZR = 1.8
floor(notches=((1.99, 1.99, 2.5, 2.5), (-2.5, -2.5, -1.99, -1.99), (1.99, -0.35, 2.5, 0.15)))

car = carousel(CX, CY, RR, n=8, zd=ZD, pick_a=0.0, L=4, drive_a=1.95)
P = car["pick"]
# the spent bin under the chute, west
box((-2.28, -0.3, 0.3), (0.42, 0.5, 0.6), "lead", bevel=0.02)
box((-2.28, -0.3, 0.62), (0.46, 0.54, 0.05), "dark_steel")
handwheel((-2.28, -0.5, 0.7), 0.08)
hazard_tag((-2.28, -0.555, 0.4), 0.36, 0.05)
label(11, "spent cells out: chute to the lead bin", (-2.28, -0.3, 0.65))

# the crucible and its plate rack, east
X0, X1, Y0, Y1, ZT = 0.45, 2.02, -0.8, 1.5, 1.05
W = crucible(X0, X1, Y0, Y1, ZT, well=(1.25, CY), slot=(0.6, 1.88, 0.88, 1.38), hinge="E", plates="x")
# tubes on the east flank, arms into the wall
TY = [-0.62 + 0.46 * i for i in range(5)]
box((2.25, 0.3, 0.06), (0.42, 2.3, 0.12), "dark_steel")
for i, y in enumerate(TY):
    tube(2.25, y, 0.1, i, h=0.9, arm=(-1, 0), arm_len=0.2)
pipe([(2.44, TY[0] - 0.2, 1.2), (2.44, TY[-1] + 0.1, 1.2)], r=0.03, mat="copper", flanges=False)
label(6, "thermionic tubes: the crucible's heat to current, copper collector caps", (2.25, TY[2], 1.1))

# the crane: rails on the north shield housing and on posts along the crucible's south face
housing(-0.2, 1.62, 2.45, 1.95, ZR - 0.06, mat="grey", roof="teal")
radiator(-0.1, 2.35, 1.6, 0.85, 1.68, mat="grey", fins=20)
label(12, "coolant radiator (the crucible jacket and tube caps)", (1.1, 1.6, 1.3))
crane("x", (-1.0, 1.78), ZR, CY, P[0], W[0], P[2], W[2], -0.55, 2.42, d=0.38, label_n=4,
      rail_posts=(-0.5, 0.4, 1.4, 2.38))

# the DC bus: the tubes' and plates' bars down a tray to the switchgear, SE
tray([(2.3, -0.85, 1.2), (2.3, -1.3, 1.05), (2.05, -1.5, 1.05)])
cabinet(1.8, -1.9, 0.4, 0.6, 1.0, mat="grey")
cabinet(2.22, -1.9, 0.42, 0.6, 1.15, mat="green")
gauge((2.22, -2.21, 0.8), (0, -1, 0.15), r=0.06, live=lambda t: 0.2 * math.sin(2 * PI * t))
id_panel((1.8, -2.21, 0.6), 0.22, 0.12, stripe="red")
label(7, "DC bus and switchgear", (1.9, -1.9, 1.1))

# the rotary converter along the south, its commutator at the east (DC) end
cv = converter(-1.75, 1.2, -1.95, 0.6, R=0.4, dc_east=True)
bundle([(1.7, -1.62, 0.95), (1.45, -1.45, 1.0), (cv["com"][0] + 0.05, -1.45, 0.95), (cv["com"][0], -1.55, 0.9)],
       cols=("red", "black", "red"), r=0.025)

# the transformer, SW, and the trunks out
tf = transformer(-2.15, -1.92, 0.58, 0.8, 0.8, mat="cream")
trunk([cv["ac_top"], (-1.2, -1.6, 1.2), (-1.9, -1.75, 1.25), tf], r=0.05)
trunk([(-2.3, -2.2, 0.9), (-2.42, -2.3, 0.5), (-2.49, -2.32, 0.1)], r=0.065)
trunk([(-2.0, -2.25, 0.9), (-1.95, -2.4, 0.5), (-1.92, -2.49, 0.1)], r=0.065)
label(10, "armoured trunks: the wire", (-2.42, -2.3, 0.5))

# coolant for the crucible jacket and the tube caps: pump, hoses to the radiator housing
pv = motor(-0.6, 2.2, 0.35, d=(1, 0), s=0.8)
coupling(pv[0] + 0.05, pv[1], pv[2], 0.1, axis=(1, 0, 0), turns=2)
cyl((pv[0] + 0.25, pv[1], 0.35), 0.17, 0.25, "oxide", rot=(0, PI / 2, 0), verts=32)
hose([(pv[0] + 0.25, 2.2, 0.55), (0.0, 2.3, 0.9), (0.4, 2.1, 1.2)], r=0.07, mat="hose")
lagged([(0.42, 1.45, 0.3), (0.3, 1.5, 0.5), (0.2, 1.55, 0.95), (0.25, 1.58, 1.3)], r=0.07)

# clutter: gas bottles NW, valves, barrels, a ladder, stains
for k, (x, y) in enumerate(((-2.25, 2.25), (-2.0, 2.3), (-2.32, 1.95))):
    cyl((x, y, 0.3), 0.11, 0.6, ("green", "grey", "hazard")[k], verts=24)
    head(x, y, 0.6, 0.11, 0.06, "dark_steel")
valve(-1.0, 2.3, 0.0, 0.5, wheel="red")
jbox(0.0, -1.15, w=0.28, mat="grey", z=0.1)
bundle([(0.0, -1.15, 0.5), (0.3, -1.05, 0.3), (0.5, -0.95, 0.25)], cols=("black", "yellow"))
ladder(0.42, 0.0, 0.1, 1.05, axis="y", mat="ochre")
tray([(-0.45, -1.22, 0.32), (0.95, -1.22, 0.32), (1.35, -1.4, 0.32)], w=0.2, cols=("black", "red", "black"))
for k, (x, y) in enumerate(((0.62, -1.3), (0.85, -1.36))):
    cyl((x, y, 0.22), 0.1, 0.32, ("oxide", "grey")[k], verts=20)
    torus((x, y, 0.3), 0.102, 0.01, "bare", seg=20)
stain(0.2, -1.2, 0.5, 0.12)
stain(-2.0, 0.9, 0.2, 0.3)
stain(1.6, -2.35, 0.4, 0.1)
run(dict(name="the carousel foundry", footprint=[5, 5]), nf=32)
