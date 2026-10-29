#!/usr/bin/env python3
"""Ballast Drill, T03h1 (task ballast-drill-ports): three 2D concepts for the drill rebuilt to
stand on its raised plate, each a top plan and south and east elevations at one scale, to the
footprint grid. Drawn as code: plain SVG text, fixed number formatting, nothing random and no
timestamps, so running this again gives byte-identical SVGs.

    python3 plate_concepts.py [--png]

Writes option-a.svg, option-b.svg, option-c.svg and sheet.svg beside this file; --png also
renders sheet.png (the phone sheet, one option per row) with rsvg-convert.

T03h2 (Liam picked B; plate raised to ~0.85): the same run then writes option-b2.svg (B on the
raised plate: plan and elevations), option-b2-gameview.svg (a flat-shaded sketch in the game's
projection, four directions at 1x and north at 2x, beside the T03h model's stills) and
sheet-b2.svg; --png-b2 (or --png) renders sheet-b2.png. T03h1's files are written first, with
the heights they had, so they stay byte-identical. --t03h <r5-final/wet> rebuilds the T03h
stills (t03h-wet-*.png) from that take's sheets; without it the ones beside this file are used.

    python3 plate_concepts.py --png-b2 [--t03h <dir>]

Coordinates are the model's (ballast_drill.py, rig-round-5/rig_parts.py at 401696a): tiles,
origin at the footprint's centre, y north, z up. The numbers below are the signed-off model's
unless an option says otherwise. The body never turns (only the rig does), so one plan serves
all four directions; the runs and fittings drawn solid are the north direction's (wet), the
other directions' fitting positions dashed. A dry drill draws no runs and no fittings.

Support: every solid part names what it stands on. The script samples each part's plan on a
0.02-tile grid and counts a cell as borne where a named support covers it at the part's base
height (its top within 0.011 of the base, or the base inside the support's height: set into
it). Unborne cells are hatched red in the plan and their span drawn red on the part's base
line in the elevations; borne spans are drawn cyan. Moving parts (the ring), pipes and the
legs are checked by their ends, in the notes.
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- the signed-off numbers
FACE = 2.496            # the plate's faces (rig_parts PLATE_FACE)
PLATE_TOP = 0.66        # rig_parts PLATE_TOP
NX, NCH = 1.5, 3.35     # the corner notch: |x|, |y| > 1.5 and |x| + |y| > 3.35 (chassis_outline)
BAY_HW, BAY_R = 0.70, 1.60      # the discharge bays: |lateral| < 0.70, out from 1.60 (in_plate_plan)
Y_STEP, AP = 1.63, 0.20         # the bay's riser and its apron's height
DECK_TOP = 0.87         # the chassis top round the press (ZT)
GAL = 1.94              # the gallery's inner line (rig_parts CUT_IN); its corners arcs of 0.44 about (1.5, 1.5)
GAL_ARC = 0.44
R_AX, ARC_C = 2.24, 1.5         # the run's axis out from the centre; its corner bends about (1.5, 1.5)
Z_RUN, R_RUN = 0.96, 0.22       # the run's axis height; the bore's radius (0.44 across)
ZA = 0.42               # the wall fitting's axis height
H_RING_R, V_RING_R = 0.363, 0.398   # the end rings (E/W, N/S)
R_HEAD, HEAD_TOP = 0.26, Z_RUN + 0.30
FLANGE_R = 0.28
SH_R, SH_TOP = 1.40, 1.01       # the landing shoulder
RB_OUT, RB_IN, Z_RING, RING_TOP = 1.30, 0.98, 1.385, 2.135     # the ring, raised (frame 0)
COL_R, COL_TOP = 0.34, 3.20     # the central column; its collar to 3.30, its dome to 3.44
GUIDE_R = 0.17
GUIDE_S = (0.0, -1.14)          # the south guide column, through the band, to 2.36
HB, H_ROOF = 2.31, 3.00         # the gear-houses: floor (wall foot) and roof top
PAD, PAD_R = 2.12, 0.34         # the legs' pads
LEG_ROOT = 1.675 - 0.0707       # the leg's root, on the notch face, along the diagonal
GIRDER_Z0 = 0.56
POST_DEG, POST_OUT = 34, 0.07
STUB_SADDLE = 1.40
V_AXIS_U, H_AXIS_V = 0.5 / 64, 1.0 / 64
FIT_CONNS = [(-2, -1, "W"), (2, -1, "E"), (1, 2, "S"), (-1, 2, "S")]   # big-mining-drill.lua:570-580

# ---------------------------------------------------------------- the tones (flat, one per material)
TONE = {
    "bg": "#1B1B1D", "ground": "#2A2723", "grid": "#3A3833",
    "plate": "#575249", "plate_side": "#45413A",          # cast iron (chassis #4A463F-#6E685C)
    "deck": "#6E685C", "deck_side": "#5A554B",
    "apron": "#34312C",
    "press": "#4A4A4E", "ring": "#3E3E42", "column": "#5E5E63",
    "guide": "#8A8580",
    "cabinet": "#77726A",                                 # the cast housings (house iron, lighter)
    "oxide": "#7C2C1E",                                   # red oxide: press frame, drive cabinets, tank, rig frame
    "pipe": "#A39684", "pipe_edge": "#2A2622",            # cast-iron pipe
    "steel": "#A6A8AE",                                   # fittings, flanges
    "leg": "#5E584D", "hazard": "#C8A23A",
    "line": "#121212", "text": "#E8E6E1", "dim": "#B9B4A8", "muted": "#8C877C",
    "bear": "#46C8E8", "float": "#FF4A3A",
}
S = 86                   # px a tile
VIEW = 7.0               # each view's box, tiles
FONT = "DejaVu Sans"


def n(v):
    s = f"{v:.1f}"
    return "0.0" if s == "-0.0" else s


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- shapes
class Poly:
    def __init__(self, pts):
        self.pts = [(float(x), float(y)) for x, y in pts]

    def contains(self, x, y):
        inside = False
        p = self.pts
        j = len(p) - 1
        for i in range(len(p)):
            xi, yi = p[i]
            xj, yj = p[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                inside = not inside
            j = i
        return inside

    def bbox(self):
        xs = [q[0] for q in self.pts]
        ys = [q[1] for q in self.pts]
        return min(xs), max(xs), min(ys), max(ys)


class Circ:
    def __init__(self, cx, cy, r):
        self.cx, self.cy, self.r = cx, cy, r

    def contains(self, x, y):
        return (x - self.cx) ** 2 + (y - self.cy) ** 2 <= self.r ** 2

    def bbox(self):
        return self.cx - self.r, self.cx + self.r, self.cy - self.r, self.cy + self.r


class Ann(Circ):
    def __init__(self, cx, cy, ro, ri):
        super().__init__(cx, cy, ro)
        self.ri = ri

    def contains(self, x, y):
        d = (x - self.cx) ** 2 + (y - self.cy) ** 2
        return self.ri ** 2 <= d <= self.r ** 2


class Fn:
    """A shape given by a test and a bounding box (the plate, the deck)."""
    def __init__(self, test, box):
        self.test, self.box = test, box

    def contains(self, x, y):
        return self.test(x, y)

    def bbox(self):
        return self.box


class Union:
    def __init__(self, shapes):
        self.shapes = shapes

    def contains(self, x, y):
        return any(s_.contains(x, y) for s_ in self.shapes)

    def bbox(self):
        bs = [s_.bbox() for s_ in self.shapes]
        return min(b[0] for b in bs), max(b[1] for b in bs), min(b[2] for b in bs), max(b[3] for b in bs)


def rect(x0, x1, y0, y1):
    return Poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def mirror_x(pts):
    return [(-x, y) for x, y in reversed(pts)]


def mirror_y(pts):
    return [(x, -y) for x, y in reversed(pts)]


def in_bay(x, y, r0=BAY_R):
    ax, ay = abs(x), abs(y)
    if ay >= ax and abs(x) < BAY_HW and ay > r0:
        return True
    if ax >= ay and abs(y) < BAY_HW and ax > r0:
        return True
    return False


def in_plate(x, y):
    ax, ay = abs(x), abs(y)
    if ax > FACE or ay > FACE:
        return False
    if ax > NX and ay > NX and ax + ay > NCH:
        return False
    return not in_bay(x, y)


def in_deck(x, y):
    ax, ay = abs(x), abs(y)
    if ax > GAL or ay > GAL:
        return False
    if ax > NX and ay > NX and ax + ay > NCH:
        return False                     # the notch: the deck stops where the plate does
    return not in_bay(x, y, Y_STEP)


def plate_outline(e=FACE):
    q = [(NX, -e), (NX, -(NCH - NX)), (NCH - NX, -NX), (e, -NX)]
    pts = []
    for k in range(4):
        c, s_ = math.cos(math.pi / 2 * k), math.sin(math.pi / 2 * k)
        for x, y in q:
            pts.append((c * x - s_ * y, s_ * x + c * y))
    return pts


def deck_outline():
    return plate_outline(GAL)


def bay_rects(r0):
    out = []
    for face in "NESW":
        if face == "N":
            out.append(rect(-BAY_HW, BAY_HW, r0, FACE))
        elif face == "S":
            out.append(rect(-BAY_HW, BAY_HW, -FACE, -r0))
        elif face == "E":
            out.append(rect(r0, FACE, -BAY_HW, BAY_HW))
        else:
            out.append(rect(-FACE, -r0, -BAY_HW, BAY_HW))
    return out


def arc_band(cx, cy, r0, r1, a0, a1, k=16):
    outer = [(cx + r1 * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
              cy + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / k))) for i in range(k + 1)]
    inner = [(cx + r0 * math.cos(math.radians(a1 - (a1 - a0) * i / k)),
              cy + r0 * math.sin(math.radians(a1 - (a1 - a0) * i / k))) for i in range(k + 1)]
    return Poly(outer + inner)


# ---------------------------------------------------------------- the connections
def conns(turns):
    out = []
    for x, y, f in FIT_CONNS:
        for _ in range(turns):
            x, y, f = -y, x, "NESW"[("NESW".index(f) + 1) % 4]
        out.append((x, y, f))
    return out


def fit_pos(c):
    """(face, lateral) of a connection in model coordinates: N/S lateral is x, E/W lateral is y."""
    x, y, f = c
    if f in "NS":
        return f, x + V_AXIS_U
    return f, -y + H_AXIS_V - ZA / 2


ALL_FITS = []
for _t in range(4):
    for _c in conns(_t):
        _p = fit_pos(_c)
        if _p not in ALL_FITS:
            ALL_FITS.append(_p)
NORTH_FITS = [fit_pos(c) for c in conns(0)]


def on_face(face, lat, r):
    return {"N": (lat, r), "S": (lat, -r), "E": (r, lat), "W": (-r, lat)}[face]


def run_path(r_ax, c, rr, corner, ya, xb, k=12):
    """A run round a corner: from the junction on the E/W face at y=ya, along it to the bend,
    round the bend (radius rr about (sx*c, sy*c)), along the N/S face to the junction at x=xb.
    Returns three pieces of plan points."""
    sx, sy = corner
    s1 = [(sx * r_ax, ya), (sx * r_ax, sy * c)]
    a0 = 0.0 if sx > 0 else 180.0
    a1 = 90.0 if sy > 0 else 270.0
    if sx < 0 and sy < 0:
        a0, a1 = 180.0, 270.0
    if sx > 0 and sy < 0:
        a0, a1 = 360.0, 270.0
    arc = [(sx * c + rr * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
            sy * c + rr * math.sin(math.radians(a0 + (a1 - a0) * i / k))) for i in range(k + 1)]
    s2 = [(sx * c, sy * r_ax), (xb, sy * r_ax)]
    return [s1, arc, s2]


def loop_path(r_ax, c, rr, k=12):
    pts = []
    for a0 in (-90, 0, 90, 180):
        cx = c if a0 in (-90, 0) else -c
        cy = c if a0 in (0, 90) else -c
        for i in range(k + 1):
            a = math.radians(a0 + 90 * i / k)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    pts.append(pts[0])
    return pts


def riser_lat(lat):
    """Where a junction's riser stands across its face: at its fitting, unless that would put the
    riser over the open bay; then just clear of the bay's edge, the pipe jogging to it inside the
    plate (the E/W fittings at 0.806: their risers stand at 0.98)."""
    if abs(lat) - R_HEAD < BAY_HW + 0.02:
        return math.copysign(BAY_HW + R_HEAD + 0.02, lat)
    return lat


# ---------------------------------------------------------------- an option's parts
class Part:
    def __init__(self, key, name, mat, shape, z0, z1, on=(), kind="stand", tag=None, note="", walls=None):
        self.key, self.name, self.mat, self.shape = key, name, mat, shape
        self.walls = walls           # a gear-house: the walls that must bear (its roof spans to the column)
        self.z0, self.z1, self.on, self.kind, self.tag, self.note = z0, z1, list(on), kind, tag, note
        self.unborne = []            # [(x0, x1, y)] cell spans not borne
        self.cells = 0


def build(option):
    """The parts of option 'A', 'B' or 'C'. Returns (parts, runs, extra) where runs is a dict of
    the run geometry and extra the option's notes."""
    P = []
    raised = option == "B2"         # T03h2: option B on the raised plate (set_raised()): no deck
    if raised:
        option = "B"

    def add(*a, **k):
        p = Part(*a, **k)
        P.append(p)
        return p

    deck = option in "AB" and not raised
    base = DECK_TOP if deck else PLATE_TOP
    base_on = "deck" if deck else "plate"
    add("plate", "plate", "plate", Fn(in_plate, (-FACE, FACE, -FACE, FACE)), 0.0, PLATE_TOP, ["ground"], "plate")
    if deck:
        add("deck", "deck (chassis top)", "deck", Fn(in_deck, (-GAL, GAL, -GAL, GAL)), PLATE_TOP, DECK_TOP,
            ["plate"], "deck")
    add("shoulder", "landing shoulder", "press", Circ(0, 0, SH_R), base, SH_TOP, [base_on], tag="1")
    add("column", "central column", "column", Circ(0, 0, COL_R), SH_TOP, COL_TOP + 0.10, ["shoulder"], tag="2")
    add("ring", "ballast ring (raised)", "ring", Ann(0, 0, RB_OUT, RB_IN), Z_RING, RING_TOP, ["guide-S"],
        kind="moving", tag="3", note="moves: rides the guides on its ropes, lands on the shoulder")
    add("guide-S", "south guide column", "guide", Circ(*GUIDE_S, GUIDE_R), SH_TOP, 2.41, ["shoulder"], tag="4")

    # the north guide columns: 45 degrees, r 1.65 in every option (signed off: 30/150, r 1.95)
    gc = 1.65 / math.sqrt(2)
    for sx, sd in ((1, "E"), (-1, "W")):
        foot_top = DECK_TOP + 0.14 if deck else PLATE_TOP + (0.14 if raised else 0.06)
        add(f"gfoot-N{sd}", f"N{sd} guide foot", "press", Circ(sx * gc, gc, 0.20), base, foot_top, [base_on])
        add(f"guide-N{sd}", f"N{sd} guide column", "guide", Circ(sx * gc, gc, GUIDE_R), foot_top, HB,
            [f"gfoot-N{sd}"], tag="5")

    if option == "A":
        # A: every part kept, cut back to the gallery line; the drive cabinet an L round the
        # column's north and outer sides, from the plate to the gear-house's floor
        L = [(1.55, 0.78), (GAL, 0.78), (GAL, NX), (NCH - NX, NX), (NX, NCH - NX), (NX, GAL), (0.72, GAL),
             (0.72, 1.50), (1.55, 1.50)]
        core = [(0.78, -1.94), (1.50, -1.94), (1.50, -1.40), (0.78, -1.40)]
        wing = [(1.50, -1.40), (GAL, -1.40), (GAL, -NX), (NCH - NX, -NX), (NX, -(NCH - NX))]
        for sx, sd in ((1, "E"), (-1, "W")):
            pts = L if sx > 0 else mirror_x(L)
            add(f"drive-N{sd}", f"N{sd} drive cabinet", "oxide", Poly(pts), PLATE_TOP, HB, ["plate"], tag="6")
            hp = [(0.90, 0.78), (GAL, 0.78), (GAL, NX), (NCH - NX, NX), (NCH - 1.76, 1.76), (0.90, 1.76)]
            wl = [rect(0.90, NCH - 1.76 - 0.01, 1.70, 1.76), rect(GAL - 0.06, GAL, 0.78, NX),
                  Poly([(NCH - NX - 0.01, NX), (NCH - 1.76 - 0.01, 1.76), (NCH - 1.76 - 0.05, 1.72),
                        (NCH - NX - 0.05, NX - 0.04)]),
                  rect(GAL - 0.08, GAL, 0.78, 0.86)]
            add(f"house-N{sd}", f"N{sd} gear-house", "oxide", Poly(hp if sx > 0 else mirror_x(hp)), HB, H_ROOF,
                [f"drive-N{sd}", f"guide-N{sd}"], tag="7", note="front open on the gear; roof spans to the column",
                walls=wl if sx > 0 else [Poly(mirror_x(w.pts)) for w in wl])
        for sx, sd, nm in ((-1, "W", "hydraulic"), (1, "E", "switchgear")):
            add(f"core-S{sd}", f"S{sd} housing ({nm})", "cabinet", Poly(core if sx > 0 else mirror_x(core)),
                PLATE_TOP, 2.10, ["plate"], tag="8")
            add(f"wing-S{sd}", f"S{sd} wing", "cabinet", Poly(wing if sx > 0 else mirror_x(wing)), PLATE_TOP, 1.75,
                ["plate"], tag="9")
        add("roofcab", "pump cabinet", "cabinet", rect(-1.44, -1.16, -1.88, -1.44), 2.10, 2.55, ["core-SW"], tag="10")
        add("tank", "reservoir (on the roof)", "oxide", rect(-1.08, -0.82, -1.88, -1.46), 2.10, 2.36, ["core-SW"],
            tag="11")
        add("bottles", "accumulator bottles", "oxide", rect(0.83, 1.17, -1.88, -1.50), 2.10, 2.27, ["core-SE"],
            tag="12")
    elif option == "B":
        # B: four diagonal bastions, one per corner inside the runs' bends (|x| + |y| >= 2.75,
        # their outer faces chamfered at 3.55); gear-houses on the north pair
        cor = [(NX, GAL), (NX, NCH - NX), (NCH - NX, NX), (GAL, NX)]
        nb = [(0.90, 1.85), (0.90, GAL)] + cor + [(GAL, 0.81)]
        sb = mirror_y([(0.90, 1.85), (0.90, GAL)] + cor + [(GAL, 1.40), (1.35, 1.40)])
        hp = [(0.90, 1.15), (0.90, GAL)] + cor + [(GAL, 0.81), (1.24, 0.81)]
        for sx, sd in ((1, "E"), (-1, "W")):
            add(f"bast-N{sd}", f"N{sd} bastion (drive)", "oxide", Poly(nb if sx > 0 else mirror_x(nb)), PLATE_TOP, HB,
                ["plate"], tag="6")
            wl = [rect(0.90, NX, GAL - 0.06, GAL), rect(GAL - 0.06, GAL, 0.88, NX),
                  Poly([(NX, 1.84), (1.84, NX), (1.80, 1.46), (1.46, 1.80)])]
            add(f"house-N{sd}", f"N{sd} gear-house", "oxide", Poly(hp if sx > 0 else mirror_x(hp)), HB, H_ROOF,
                [f"bast-N{sd}", f"guide-N{sd}"], tag="7", note="front open on the gear; roof spans to the column",
                walls=wl if sx > 0 else [Poly(mirror_x(w.pts)) for w in wl])
        for sx, sd, nm in ((-1, "W", "hydraulic"), (1, "E", "switchgear")):
            add(f"bast-S{sd}", f"S{sd} bastion ({nm})", "cabinet", Poly(sb if sx > 0 else mirror_x(sb)), PLATE_TOP,
                2.10, ["plate"], tag="8")
        add("tank", "reservoir (pump inside)", "oxide", rect(-1.48, -1.14, -1.92, -1.66), 2.10, 2.36, ["bast-SW"],
            tag="11")
        add("bottles", "accumulator bottles", "oxide", rect(1.10, 1.46, -1.92, -1.70), 2.10, 2.27, ["bast-SE"],
            tag="12")
    else:
        # C: the cabinets at the plate's edge, flush with its wall, one each side of every bay
        # (lateral 0.72 to 1.50, 0.50 deep); the runs inboard on a loop round the press
        spec = (("N", 2.31, "oxide", "drive"), ("S", 1.75, "cabinet", None),
                ("E", None, "cabinet", "starter"), ("W", None, "cabinet", "starter"))
        for face, top, mat, role in spec:
            for s in (1, -1):
                if face == "N":
                    sh = rect(0.72, 1.50, 2.0, FACE) if s > 0 else rect(-1.50, -0.72, 2.0, FACE)
                    side = "E" if s > 0 else "W"
                    nm = f"N{side} wall cabinet (drive)"
                elif face == "S":
                    sh = rect(0.72, 1.50, -FACE, -2.0) if s > 0 else rect(-1.50, -0.72, -FACE, -2.0)
                    side = "E" if s > 0 else "W"
                    nm = f"S{side} wall cabinet ({'switchgear' if s > 0 else 'hydraulic'})"
                else:
                    xs = (2.0, FACE) if face == "E" else (-FACE, -2.0)
                    sh = rect(xs[0], xs[1], 0.72, 1.50) if s > 0 else rect(xs[0], xs[1], -1.50, -0.72)
                    side = "N" if s > 0 else "S"
                    top = 1.40 if s > 0 else 1.10
                    nm = f"{face} face {'north' if s > 0 else 'south'} wall cabinet"
                key = f"wall-{face}{side}" if face in "NS" else f"wall-{face}{'n' if s > 0 else 's'}"
                tg = {"N": "6", "S": "8", "E": "13", "W": "13"}[face]
                add(key, nm, mat, sh, PLATE_TOP, top, ["plate"], tag=tg)
        for sx, sd in ((1, "E"), (-1, "W")):
            hp = [(0.72, 0.92), (1.50, 0.92), (1.50, FACE), (0.72, FACE)]
            wl = [rect(0.72, 1.50, 2.44, 2.48), rect(1.44, 1.50, 0.92, 2.48), rect(1.42, 1.50, 0.92, 1.00)]
            add(f"house-N{sd}", f"N{sd} gear-house (bridge)", "oxide", Poly(hp if sx > 0 else mirror_x(hp)), HB,
                H_ROOF, [f"wall-N{sd}", f"guide-N{sd}"], tag="7",
                note="outer wall spans 1.1 over the runs, column to wall cabinet",
                walls=wl if sx > 0 else [Poly(mirror_x(w.pts)) for w in wl])
        add("tank", "reservoir", "oxide", rect(-1.42, -0.80, -2.40, -2.10), 1.75, 2.05, ["wall-SW"], tag="11")
        add("bottles", "accumulator bottles", "oxide", rect(0.90, 1.30, -2.445, -2.075), 1.75, 1.92, ["wall-SE"],
            tag="12")

    # ---------------------------------------------------------------- the runs (north direction, wet)
    if option in "AB":
        r_ax, c, rr = R_AX, ARC_C, R_AX - ARC_C
    else:
        r_ax, c, rr = 1.65, 1.20, 0.45
    lat_of = {f: riser_lat(l) for f, l in NORTH_FITS if f in "EW"}
    s_lats = sorted(riser_lat(l) for f, l in NORTH_FITS if f == "S")
    runs = [run_path(r_ax, c, rr, (-1, -1), lat_of["W"], s_lats[0]),
            run_path(r_ax, c, rr, (1, -1), lat_of["E"], s_lats[1])]
    loop = loop_path(r_ax, c, rr)
    junctions = []
    for f, lat in ALL_FITS:
        jx, jy = on_face(f, riser_lat(lat), r_ax)
        junctions.append((f, lat, jx, jy, (f, lat) in NORTH_FITS))
    for i, (f, lat, jx, jy, used) in enumerate(junctions):
        if used:
            add(f"riser-{f}{i}", f"junction riser {f}", "oxide", Circ(jx, jy, R_HEAD), PLATE_TOP, HEAD_TOP, ["plate"],
                kind="riser", tag="R")
    # supports under the runs
    if option in "AB":
        for sx in (-1, 1):
            add(f"saddle-S{sx}", "face saddle", "plate_side", rect(sx * STUB_SADDLE - 0.10, sx * STUB_SADDLE + 0.10,
                -R_AX - 0.13, -R_AX + 0.13), PLATE_TOP, Z_RUN - R_RUN, ["plate"], tag="s")
            add(f"saddle-E{sx}", "face saddle", "plate_side", rect(sx * R_AX - 0.13, sx * R_AX + 0.13,
                -STUB_SADDLE - 0.10, -STUB_SADDLE + 0.10), PLATE_TOP, Z_RUN - R_RUN, ["plate"], tag="s")
            # the corner girder over the open notch, its ends set into the plate's notch faces;
            # two red-oxide posts on the ground under it, and a saddle on it at the bend's middle
            a0, a1 = (270, 360) if sx > 0 else (180, 270)
            add(f"girder-S{sx}", "corner girder", "plate_side",
                arc_band(sx * ARC_C, -ARC_C, rr - 0.10, rr + 0.10, a0, a1), GIRDER_Z0, PLATE_TOP,
                [f"post-S{sx}a", f"post-S{sx}b", "plate"], kind="beam", tag="g")
            mid = math.radians((a0 + a1) / 2)
            add(f"gsaddle-S{sx}", "girder saddle", "plate_side",
                Circ(sx * ARC_C + rr * math.cos(mid), -ARC_C + rr * math.sin(mid), 0.09), PLATE_TOP, Z_RUN - R_RUN,
                [f"girder-S{sx}"], tag="s")
            for ab, d in (("a", -POST_DEG), ("b", POST_DEG)):
                a = mid + math.radians(d)
                px, py = sx * ARC_C + (rr + POST_OUT) * math.cos(a), -ARC_C + (rr + POST_OUT) * math.sin(a)
                add(f"post-S{sx}{ab}", "frame post", "oxide", rect(px - 0.08, px + 0.08, py - 0.08, py + 0.08), 0.0,
                    GIRDER_Z0, ["ground"], tag="p")
    else:
        # a saddle on the plate at the far edge of each bay a run bridges (the riser holds the
        # near side); the run crosses the bay's inner end, 0.27 of its bore over the open bay
        for sx in (-1, 1):
            add(f"saddle-{'E' if sx > 0 else 'W'}", "bay saddle", "plate_side",
                rect(sx * r_ax - 0.13, sx * r_ax + 0.13, -0.85, -0.71), PLATE_TOP, Z_RUN - R_RUN, ["plate"], tag="s")
    return P, dict(r_ax=r_ax, c=c, rr=rr, runs=runs, loop=loop, junctions=junctions)


# ---------------------------------------------------------------- the support check
GRID = 0.02


def check(parts):
    by = {p.key: p for p in parts}
    ground = Fn(lambda x, y: True, (-9, 9, -9, 9))
    report = []
    for p in parts:
        if p.kind in ("plate", "deck", "moving"):
            continue
        sup = []
        for k in p.on:
            if k == "ground":
                sup.append((ground, -1.0, 0.0))
            else:
                s = by[k]
                sup.append((s.shape, s.z0, s.z1))
        test = Union(p.walls) if p.walls else p.shape
        x0, x1, y0, y1 = test.bbox()
        i0, i1 = math.floor(x0 / GRID), math.ceil(x1 / GRID)
        j0, j1 = math.floor(y0 / GRID), math.ceil(y1 / GRID)
        total = bad = 0
        for j in range(j0, j1):
            y = (j + 0.5) * GRID
            span = None
            for i in range(i0, i1 + 1):
                x = (i + 0.5) * GRID
                miss = False
                if i <= i1 - 1 and test.contains(x, y):
                    total += 1
                    ok = any(sh.contains(x, y) and za - 0.011 <= p.z0 <= zb + 0.011 for sh, za, zb in sup)
                    if not ok:
                        miss = True
                        bad += 1
                if miss and span is None:
                    span = i * GRID
                elif not miss and span is not None:
                    p.unborne.append((span, i * GRID, j * GRID))
                    span = None
        p.cells = total
        if p.kind == "beam":
            # a beam: its two ends must bear; its span is open by design
            ends = (p.shape.pts[0], p.shape.pts[len(p.shape.pts) // 2 - 1])
            ok = all(any(sh.contains(ex, ey) for sh, za, zb in sup) for ex, ey in
                     ((e[0] * 0.995, e[1] * 0.995) for e in ends))
            report.append((p, None, "both ends bear" if ok else "AN END DOES NOT BEAR"))
            p.unborne = []
        else:
            report.append((p, bad / total if total else 0.0, ""))
    return report


# ---------------------------------------------------------------- drawing
class Svg:
    def __init__(self):
        self.o = []

    def add(self, s):
        self.o.append(s)

    def poly(self, pts, fill, stroke=TONE["line"], sw=1.0, extra=""):
        d = " ".join(f"{n(x)},{n(y)}" for x, y in pts)
        self.add(f'<polygon points="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{n(sw)}"{extra}/>')

    def rect(self, x, y, w, h, fill, stroke=TONE["line"], sw=1.0, extra=""):
        self.add(f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{n(sw)}"{extra}/>')

    def circle(self, cx, cy, r, fill, stroke=TONE["line"], sw=1.0, extra=""):
        self.add(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{n(sw)}"{extra}/>')

    def line(self, x0, y0, x1, y1, stroke, sw=1.0, extra=""):
        self.add(f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="{stroke}" '
                 f'stroke-width="{n(sw)}"{extra}/>')

    def path(self, d, fill, stroke=TONE["line"], sw=1.0, extra=""):
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{n(sw)}"{extra}/>')

    def text(self, x, y, t, size=12, fill=TONE["text"], anchor="start", weight="normal", extra=""):
        self.add(f'<text x="{n(x)}" y="{n(y)}" font-family="{FONT}" font-size="{n(size)}" fill="{fill}" '
                 f'text-anchor="{anchor}" font-weight="{weight}"{extra}>{esc(t)}</text>')


DASH = ' stroke-dasharray="5,4"'
HATCH = ' fill="url(#hatch)"'


def defs():
    return ('<defs><pattern id="hatch" patternUnits="userSpaceOnUse" width="6" height="6" '
            'patternTransform="rotate(45)"><rect width="6" height="6" fill="#FF4A3A" fill-opacity="0.25"/>'
            '<line x1="0" y1="0" x2="0" y2="6" stroke="#FF4A3A" stroke-width="2.5"/></pattern></defs>')


def tone(p):
    return TONE[p.mat]


def plan(svg, ox, oy, parts, rg, option):
    """The top plan, north up, its centre at (ox, oy) px."""
    def P(x, y):
        return ox + x * S, oy - y * S

    def pts(ps):
        return [P(x, y) for x, y in ps]
    # the ground and the footprint grid
    h = VIEW / 2 * S
    svg.rect(ox - h, oy - h, 2 * h, 2 * h, TONE["ground"], "none", 0)
    for k in range(6):
        v = -2.5 + k
        svg.line(*P(v, -2.9), *P(v, 2.9), TONE["grid"], 1)
        svg.line(*P(-2.9, v), *P(2.9, v), TONE["grid"], 1)
    by = {p.key: p for p in parts}
    # the plate, its bays down to the apron
    svg.poly(pts(plate_outline()), TONE["plate"], sw=1.5)
    for b in bay_rects(BAY_R):
        svg.poly(pts(b.pts), TONE["apron"], sw=1.0)
    if "deck" in by:
        svg.poly(pts(deck_outline()), TONE["deck"], sw=1.2)
        for b in bay_rects(Y_STEP):
            x0, x1, y0, y1 = b.bbox()
            x0, x1 = max(x0, -GAL - 0.01), min(x1, GAL + 0.01)
            y0, y1 = max(y0, -GAL - 0.01), min(y1, GAL + 0.01)
            if x1 > x0 and y1 > y0:
                svg.poly(pts(rect(x0, x1, y0, y1).pts), TONE["apron"], "none", 0)
    # the legs and pads, in the open corners
    for sx in (-1, 1):
        for sy in (-1, 1):
            r = (sx * LEG_ROOT, sy * LEG_ROOT)
            f = (sx * PAD, sy * PAD)
            nx_, ny_ = -sy / math.sqrt(2), sx / math.sqrt(2)
            q = [(r[0] + nx_ * 0.20, r[1] + ny_ * 0.20), (f[0] + nx_ * 0.15, f[1] + ny_ * 0.15),
                 (f[0] - nx_ * 0.15, f[1] - ny_ * 0.15), (r[0] - nx_ * 0.20, r[1] - ny_ * 0.20)]
            svg.circle(*P(*f), PAD_R * S, TONE["hazard"])
            svg.circle(*P(*f), 0.27 * S, TONE["leg"])
            svg.poly(pts(q), TONE["leg"])
    # everything else by height, lowest first
    rest = [p for p in parts if p.kind not in ("plate", "deck")]
    order = sorted(range(len(rest)), key=lambda i: (rest[i].z1, i))
    runs_drawn = False
    for i in order:
        p = rest[i]
        if not runs_drawn and p.z1 > Z_RUN + R_RUN + 0.01:
            draw_runs_plan(svg, P, rg)
            runs_drawn = True
        sh = p.shape
        fill = tone(p)
        if isinstance(sh, Ann):
            cx, cy = P(sh.cx, sh.cy)
            svg.circle(cx, cy, (sh.r + sh.ri) / 2 * S, "none", fill, (sh.r - sh.ri) * S)
            svg.circle(cx, cy, sh.r * S, "none", TONE["line"], 1)
            svg.circle(cx, cy, sh.ri * S, "none", TONE["line"], 1)
        elif isinstance(sh, Circ):
            if p.kind == "riser":
                svg.circle(*P(sh.cx, sh.cy), FLANGE_R * S, TONE["steel"])
            svg.circle(*P(sh.cx, sh.cy), sh.r * S, fill)
        else:
            svg.poly(pts(sh.pts), fill)
        for x0, x1, y in p.unborne:
            a = P(x0, y + GRID)
            svg.add(f'<rect x="{n(a[0])}" y="{n(a[1])}" width="{n((x1 - x0) * S)}" height="{n(GRID * S + 0.3)}"'
                    f'{HATCH} stroke="none"/>')
    if not runs_drawn:
        draw_runs_plan(svg, P, rg)
    # the dome on the column
    svg.circle(*P(0, 0), 0.34 * S, TONE["column"])
    svg.circle(*P(0, 0), 0.10 * S, TONE["steel"])
    # the wall fittings: north direction's solid, the other directions' dashed
    for f, lat, jx, jy, used in rg["junctions"]:
        ex, ey = on_face(f, lat, FACE)
        rr_ = V_RING_R if f in "NS" else H_RING_R
        if f in "NS":
            out = -1 if f == "S" else 1
            y_out = -2.74 if f == "S" else FACE + 0.01
            box = rect(lat - rr_, lat + rr_, min(ey, y_out) - 0.02, max(ey, y_out) + 0.02)
        else:
            out = 1 if f == "E" else -1
            box = rect(min(ex, out * (FACE + 0.03)), max(ex, out * (FACE + 0.03)), lat - rr_, lat + rr_)
        if used:
            svg.poly(pts(box.pts), TONE["steel"], sw=1)
            # the pipe in the plate, from the fitting to the riser's flange
            svg.line(*P(ex, ey), *P(jx, jy), TONE["pipe"], 3, DASH)
        else:
            svg.poly(pts(box.pts), "none", TONE["steel"], 1.2, DASH)
            svg.circle(*P(jx, jy), R_HEAD * S, "none", TONE["muted"], 1.2, DASH)
    # tags
    for p in rest:
        if not p.tag or p.tag in ("R", "s", "g", "p"):
            continue
        x0, x1, y0, y1 = p.shape.bbox()
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if isinstance(p.shape, Poly):
            xs = [q[0] for q in p.shape.pts]
            ys = [q[1] for q in p.shape.pts]
            cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        if p.key == "shoulder":
            cx, cy = -1.05, -0.62
        if p.key == "ring":
            cx, cy = 0.0, -1.14 + 0.32
        if p.key == "column":
            cx, cy = 0.0, 0.0
        if p.key == "guide-S":
            cx, cy = 0.30, -1.14
        if p.key.startswith("gfoot") or p.key.startswith("guide-N"):
            continue
        if p.key.startswith("drive-N") or p.key.startswith("bast-N"):
            cx, cy = math.copysign(1.15, cx), 1.86      # on its strip north of the gear-house
        if p.key.startswith("house-N") and "deck" in by:
            cy -= 0.10
        tag_mark(svg, *P(cx, cy), p.tag)
    for sx in (-1, 1):
        g = 1.65 / math.sqrt(2)
        tag_mark(svg, *P(sx * (g - 0.28), g - 0.28), "5")


def draw_runs_plan(svg, P, rg):
    # the other directions' runs: the loop's centreline, dashed
    d = "M " + " L ".join(f"{n(P(x, y)[0])},{n(P(x, y)[1])}" for x, y in rg["loop"])
    svg.path(d, "none", TONE["muted"], 1.2, DASH)
    for run in rg["runs"]:
        allp = []
        for piece in run:
            allp += piece
        d = "M " + " L ".join(f"{n(P(x, y)[0])},{n(P(x, y)[1])}" for x, y in allp)
        svg.path(d, "none", TONE["pipe_edge"], 2 * R_RUN * S + 2.5, ' stroke-linejoin="round"')
        svg.path(d, "none", TONE["pipe"], 2 * R_RUN * S - 1.0, ' stroke-linejoin="round"')


def tag_mark(svg, x, y, t):
    svg.circle(x, y, 9, "#F2EFE8", TONE["line"], 1)
    svg.text(x, y + 4, t, 11, "#141414", "middle", "bold")


def elevation(svg, ox, gy, parts, rg, view):
    """An elevation. view 'S': from the south, x to the right; 'E': from the east, y (north) to
    the right. (ox, gy): the centre's px across and the ground line's px."""
    def H(x, y):
        return x if view == "S" else y

    def depth(bb):                       # larger = nearer the viewer: drawn later
        x0, x1, y0, y1 = bb
        return -y0 if view == "S" else x1

    def X(h):
        return ox + h * S

    def Z(z):
        return gy - z * S
    h = VIEW / 2 * S
    svg.rect(ox - h, gy - 5.3 * S, 2 * h, 5.3 * S + 0.9 * S, TONE["bg"], "none", 0)
    svg.rect(ox - h, gy, 2 * h, 0.9 * S, TONE["ground"], "none", 0)
    svg.line(ox - h, gy, ox + h, gy, TONE["dim"], 1.2)
    for k in range(6):
        v = -2.5 + k
        svg.line(X(v), gy, X(v), gy + 8, TONE["dim"], 1)
    items = []                           # (depth, order, fn)

    def push(bb, fn):
        items.append((depth(bb), len(items), fn))

    def prism(bb, z0, z1, fill, p=None, dash=False):
        x0, x1, y0, y1 = bb
        a, b = (x0, x1) if view == "S" else (y0, y1)

        def fn():
            svg.rect(X(a), Z(z1), (b - a) * S, (z1 - z0) * S, fill, sw=1.0, extra=DASH if dash else "")
            if p is not None and p.kind not in ("moving",) and p.on and p.on != ["ground"]:
                base_line(p, a, b)
        push(bb, fn)

    def base_line(p, a, b):
        # cyan where the part's base is borne, red where any cell above that span is not
        bad = []
        for x0, x1, y in p.unborne:
            if view == "S":
                bad.append((x0, x1))
            else:
                bad.append((y, y + GRID))
        bad.sort()
        merged = []
        for u, v in bad:
            if merged and u <= merged[-1][1] + 1e-9:
                merged[-1][1] = max(merged[-1][1], v)
            else:
                merged.append([u, v])
        zb = Z(p.z0)
        svg.line(X(a) + 1, zb - 1.5, X(b) - 1, zb - 1.5, TONE["bear"], 3)
        for u, v in merged:
            svg.line(X(max(u, a)), zb - 1.5, X(min(v, b)), zb - 1.5, TONE["float"], 3)

    by = {p.key: p for p in parts}
    # the plate, in pieces so the open corners show the legs: the middle band, the two side
    # bands, the corner chamfers
    pieces = [rect(-NX, NX, -FACE, FACE), rect(NX, FACE, -NX, NX), rect(-FACE, -NX, -NX, NX)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            pieces.append(Poly([(sx * NX, sy * NX), (sx * (NCH - NX), sy * NX), (sx * NX, sy * (NCH - NX))]))
    for pc in pieces:
        prism(pc.bbox(), 0.0, PLATE_TOP, TONE["plate_side"])
    # the bay facing the viewer: down to its apron, the riser behind
    if view == "S":
        bb = (-BAY_HW, BAY_HW, -FACE - 0.001, -FACE)
    else:
        bb = (FACE, FACE + 0.001, -BAY_HW, BAY_HW)

    def bay_fn():
        svg.rect(X(-BAY_HW), Z(PLATE_TOP), 2 * BAY_HW * S, PLATE_TOP * S, TONE["deck_side"] if "deck" in by
                 else TONE["plate_side"], sw=1.0)
        svg.rect(X(-BAY_HW), Z(AP), 2 * BAY_HW * S, AP * S, TONE["apron"], sw=1.0)
    push(bb, bay_fn)
    if "deck" in by:
        dk = [rect(-NX, NX, -GAL, GAL), rect(-GAL, GAL, -NX, NX)]
        for pc in dk:
            prism(pc.bbox(), PLATE_TOP, DECK_TOP, TONE["deck_side"])
    # legs
    for sx in (-1, 1):
        for sy in (-1, 1):
            rt = (sx * LEG_ROOT, sy * LEG_ROOT, 0.445)
            ft = (sx * PAD, sy * PAD, 0.17)
            bb = (min(rt[0], ft[0]) - PAD_R, max(rt[0], ft[0]) + PAD_R, min(rt[1], ft[1]) - PAD_R,
                  max(rt[1], ft[1]) + PAD_R)

            def leg_fn(rt=rt, ft=ft):
                a, b = H(rt[0], rt[1]), H(ft[0], ft[1])
                q = [(X(a), Z(rt[2] + 0.2)), (X(b), Z(ft[2] + 0.15)), (X(b), Z(ft[2] - 0.15)), (X(a), Z(rt[2] - 0.2))]
                svg.poly(q, TONE["leg"])
                svg.rect(X(b - PAD_R), Z(0.19), 2 * PAD_R * S, 0.10 * S, TONE["leg"])
                svg.rect(X(b - PAD_R), Z(0.09), 2 * PAD_R * S, 0.09 * S, TONE["hazard"])
            push(bb, leg_fn)
    # parts
    for p in parts:
        if p.kind in ("plate", "deck"):
            continue
        sh = p.shape
        bb = sh.bbox()
        if p.key == "column":
            def col_fn(bb=bb):
                svg.rect(X(-COL_R), Z(COL_TOP), 2 * COL_R * S, (COL_TOP - SH_TOP) * S, TONE["column"])
                svg.rect(X(-0.44), Z(COL_TOP + 0.10), 0.88 * S, 0.10 * S, TONE["column"])
                svg.path(f"M {n(X(-0.34))},{n(Z(COL_TOP + 0.10))} A {n(0.34 * S)},{n(0.143 * S)} 0 0 1 "
                         f"{n(X(0.34))},{n(Z(COL_TOP + 0.10))} Z", TONE["column"])
            push((bb[0], bb[1], bb[2], bb[3]), col_fn)
            continue
        if p.kind == "riser":
            def riser_fn(sh=sh, p=p):
                c = H(sh.cx, sh.cy)
                svg.rect(X(c - FLANGE_R), Z(PLATE_TOP + 0.03), 2 * FLANGE_R * S, 0.03 * S, TONE["steel"])
                svg.rect(X(c - 0.24), Z(Z_RUN), 0.48 * S, (Z_RUN - PLATE_TOP - 0.03) * S, TONE["oxide"])
                svg.rect(X(c - R_HEAD), Z(HEAD_TOP), 2 * R_HEAD * S, (HEAD_TOP - Z_RUN + 0.05) * S, TONE["oxide"])
            push(bb, riser_fn)
            continue
        prism(bb, p.z0, p.z1, tone(p), p)
    # the runs (north direction): each piece a band at the run's height
    for run in rg["runs"]:
        for piece in run:
            xs = [q[0] for q in piece]
            ys = [q[1] for q in piece]
            bb = (min(xs), max(xs), min(ys), max(ys))
            hs = [H(x, y) for x, y in piece]

            def run_fn(a=min(hs), b=max(hs)):
                w = (b - a + 2 * R_RUN) * S
                svg.rect(X(a - R_RUN), Z(Z_RUN + R_RUN), w, 2 * R_RUN * S, TONE["pipe"], TONE["pipe_edge"], 1.5,
                         f' rx="{n(R_RUN * S)}"')
            push(bb, run_fn)
    # the wall fittings
    for f, lat, jx, jy, used in rg["junctions"]:
        facing = (view == "S" and f == "S") or (view == "E" and f == "E")
        edge = (view == "S" and f in "EW") or (view == "E" and f in "NS")
        rr_ = V_RING_R if f in "NS" else H_RING_R
        ex, ey = on_face(f, lat, FACE + (0.24 if f == "S" else 0.0))
        bb = (ex - 0.01, ex + 0.01, ey - 0.01, ey + 0.01)
        if facing:
            def fit_fn(lat=lat, used=used, rr_=rr_):
                if used:
                    svg.circle(X(lat), Z(ZA), rr_ * S, TONE["steel"])
                    svg.circle(X(lat), Z(ZA), (rr_ - 0.07) * S, "#8D9096")
                else:
                    svg.circle(X(lat), Z(ZA), rr_ * S, "none", TONE["steel"], 1.2, DASH)
            push(bb, fit_fn)
        elif edge and used:
            def fit_fn2(ex=ex, ey=ey, rr_=rr_):
                c = H(ex, ey)
                svg.rect(X(c - 0.03), Z(ZA + rr_), 0.06 * S, 2 * rr_ * S, TONE["steel"])
            push(bb, fit_fn2)
    for _, _, fn in sorted(items, key=lambda t: (t[0], t[1])):
        fn()


def dim_v(svg, x, z0, z1, gy, label, side=-1):
    a, b = gy - z0 * S, gy - z1 * S
    svg.line(x, a, x, b, TONE["dim"], 1)
    for yy in (a, b):
        svg.line(x - 4, yy, x + 4, yy, TONE["dim"], 1)
    svg.text(x + side * 6, (a + b) / 2 + 4, label, 11, TONE["dim"], "end" if side < 0 else "start")


def dim_h(svg, x0, x1, y, label):
    svg.line(x0, y, x1, y, TONE["dim"], 1)
    for xx in (x0, x1):
        svg.line(xx, y - 4, xx, y + 4, TONE["dim"], 1)
    svg.text((x0 + x1) / 2, y - 5, label, 11, TONE["dim"], "middle")


# ---------------------------------------------------------------- an option's panel
CAPTION = {
    "A": "A  Pulled in: every part keeps its kind and place but stops at the gallery line (1.94); the plate's "
         "outer 0.56 is a clear gallery all round, and the runs follow it as in T03h.",
    "B": "B  Four corner bastions: the cabinets merge into four diagonal blocks, one per corner inside the runs' "
         "bends; the gear-houses sit on the north pair; the faces' middles are bare deck.",
    "C": "C  Wall cabinets: the cabinets stand at the plate's edge, plumb with its wall, over the fittings; the runs "
         "move inboard to a loop round the press (r 1.65); no deck, no girders over the corners.",
}
HEIGHTS = {
    "A": [(0.66, "plate 0.66"), (0.96, "run axis 0.96"), (1.75, "wing 1.75"), (2.10, "housing 2.10"),
          (2.31, "drive cab. 2.31"), (3.00, "gear-house 3.00")],
    "B": [(0.66, "plate 0.66"), (0.96, "run axis 0.96"), (2.10, "S bastion 2.10"), (2.31, "N bastion 2.31"),
          (3.00, "gear-house 3.00")],
    "C": [(0.66, "plate 0.66"), (0.96, "run axis 0.96"), (1.75, "S wall cab. 1.75"), (2.31, "N wall cab. 2.31"),
          (3.00, "gear-house 3.00")],
}
PANEL_W = 3 * VIEW * S + 4.6 * S
PANEL_H = VIEW * S + 1.25 * S


def panel(option, x0, y0):
    parts, rg = build(option)
    rep = check(parts)
    svg = Svg()
    svg.add(f'<g transform="translate({n(x0)},{n(y0)})">')
    svg.rect(0, 0, PANEL_W, PANEL_H, TONE["bg"], "none", 0)
    svg.text(14, 30, f"Option {option}", 22, TONE["text"], weight="bold")
    svg.text(130 + 14 * (len(option) - 1), 29, CAPTION[option][3:], 14, TONE["text"])
    top = 1.0 * S
    # plan
    cx, cy = VIEW / 2 * S, top + VIEW / 2 * S
    plan(svg, cx, cy, parts, rg, option)
    svg.text(cx - VIEW / 2 * S + 8, top + 16, "PLAN (north up; wet, north direction)", 12, TONE["text"])
    dim_h(svg, cx - 2.5 * S, cx + 2.5 * S, cy - 2.78 * S, "5.00 (footprint)")
    if option[:1] in "AB":
        svg.line(cx + GAL * S, cy + 0.15 * S, cx + FACE * S, cy + 0.15 * S, TONE["dim"], 1)
        svg.text(cx + 2.22 * S, cy + 0.36 * S, "gallery 0.56", 10, TONE["dim"], "middle")
    else:
        svg.text(cx + 2.24 * S, cy + 0.10 * S, "cab. 0.50", 10, TONE["dim"], "middle")
        svg.text(cx + 1.65 * S, cy - 0.20 * S, "run r 1.65", 10, TONE["dim"], "end")
    svg.text(cx, cy + 3.0 * S, "bay 1.40", 10, TONE["dim"], "middle")
    # south elevation
    ex = VIEW * S + VIEW / 2 * S
    gy = top + VIEW * S - 1.2 * S
    elevation(svg, ex, gy, parts, rg, "S")
    svg.text(ex - VIEW / 2 * S + 8, top + 16, "SOUTH ELEVATION (from the south; x right)", 12, TONE["text"])
    xl = ex - 2.65 * S
    for z, lab in HEIGHTS[option]:
        svg.line(xl, gy - z * S, xl + 8, gy - z * S, TONE["dim"], 1)
        svg.text(xl - 4, gy - z * S + 4, lab, 10, TONE["dim"], "end")
    svg.line(xl + 4, gy, xl + 4, gy - 3.0 * S, TONE["dim"], 1)
    svg.text(ex, gy + 0.55 * S, "5.00", 11, TONE["dim"], "middle")
    # east elevation
    ex2 = 2 * VIEW * S + VIEW / 2 * S
    elevation(svg, ex2, gy, parts, rg, "E")
    svg.text(ex2 - VIEW / 2 * S + 8, top + 16, "EAST ELEVATION (from the east; north right)", 12, TONE["text"])
    xl = ex2 - 2.65 * S
    for z, lab in EAST_HEIGHTS.get(option, EAST_HEIGHTS["A"]):
        svg.line(xl, gy - z * S, xl + 8, gy - z * S, TONE["dim"], 1)
        svg.text(xl - 4, gy - z * S + 4, lab, 10, TONE["dim"], "end")
    svg.text(ex2 - 2.5 * S, gy + 0.55 * S, "S", 11, TONE["dim"], "middle")
    svg.text(ex2 + 2.5 * S, gy + 0.55 * S, "N", 11, TONE["dim"], "middle")
    svg.text(ex - 2.5 * S, gy + 0.55 * S, "W", 11, TONE["dim"], "middle")
    svg.text(ex + 2.5 * S, gy + 0.55 * S, "E", 11, TONE["dim"], "middle")
    # the support list
    lx = 3 * VIEW * S + 0.25 * S
    ly = top + 18
    svg.text(lx, ly, "SUPPORT (what each part stands on)", 12, TONE["text"], weight="bold")
    ly += 20
    by = {p.key: p for p in parts}

    def pair(nm):
        """'NE drive cabinet' and 'NW drive cabinet' read as one line, 'N drive cabinet (E, W)'."""
        if nm[:3] in ("NE ", "NW "):
            return "N" + nm[2:] + " (E, W)"
        if nm[:7] in ("E face ", "W face "):
            return "E/W face " + nm[7:]
        return nm
    lines = []
    plate_parts = []
    for p, frac, msg in rep:
        if p.kind == "riser" or p.tag in ("s", "p"):
            continue
        nm = pair(p.name)
        if p.on == ["plate"] and frac is not None and frac < 0.005:
            if nm not in plate_parts:
                plate_parts.append(nm)
            continue
        ons = " + ".join("ground" if k == "ground" else pair(by[k].name) for k in p.on)
        if frac is None:
            state, col = msg, TONE["text"]
        elif frac < 0.005:
            state, col = ("walls borne" if p.walls else "borne"), TONE["bear"]
        else:
            state, col = (f"{round(frac * 100)}% of its walls over open air" if p.walls
                          else f"{round(frac * 100)}% over open air"), TONE["float"]
        t = (p.tag, nm, ons, state, col, p.note)
        if t not in lines:
            lines.append(t)
    for tag, label, ons, state, col, note in lines:
        if ly > PANEL_H - 70:
            break
        if tag and tag != "g":
            tag_mark(svg, lx + 9, ly - 4, tag)
        svg.text(lx + 24, ly, label, 11, TONE["text"])
        ly += 14
        if len(ons) > 40:
            svg.text(lx + 24, ly, f"on {ons}:", 10, TONE["muted"])
            ly += 13
            svg.text(lx + 24, ly, state, 10, col, weight="bold")
        else:
            svg.text(lx + 24, ly, f"on {ons}: ", 10, TONE["muted"])
            svg.text(lx + 24 + 5.6 * (len(ons) + 5), ly, state, 10, col, weight="bold")
        ly += 13
        if note:
            svg.text(lx + 24, ly, note, 10, TONE["muted"])
            ly += 13
        ly += 4
    wrap = []
    cur = "on the plate top, borne: "
    for nm in plate_parts:
        add_ = nm + ", "
        if len(cur) + len(add_) > 64:
            wrap.append(cur)
            cur = ""
        cur += add_
    wrap.append(cur.rstrip(", ") + ".")
    for w in wrap:
        svg.text(lx + 4, ly, w, 10, TONE["bear"])
        ly += 13
    ly += 4
    for w in RUN_NOTE[option]:
        svg.text(lx + 4, ly, w, 10, TONE["muted"])
        ly += 13
    svg.add("</g>")
    return svg, rep


EAST_HEIGHTS = {
    "A": ((0.66, "plate 0.66"), (0.42, "fitting 0.42"), (0.96, "run 0.96"), (2.135, "ring 2.14"), (3.44, "dome 3.44")),
    "B2": ((0.85, "plate 0.85"), (0.42, "fitting 0.42"), (1.15, "run 1.15"),
           (2.135, "ring 2.14"), (3.44, "dome 3.44")),
}

RUN_NOTE = {
    "A": ["Runs: on the gallery (r 2.24) as T03h; on junction risers,",
          "face saddles at 1.40, and over each open corner a cast girder",
          "(ends set in the notch faces, two red-oxide posts on the",
          "ground) with a saddle at the bend. Legs: root in the plate's",
          "notch face, pad on the ground."],
    "B": ["Runs: on the gallery (r 2.24) as T03h; on junction risers,",
          "face saddles at 1.40, and over each open corner a cast girder",
          "(ends set in the notch faces, two red-oxide posts on the",
          "ground) with a saddle at the bend. Legs: root in the plate's",
          "notch face, pad on the ground."],
    "C": ["Runs: on the plate top inboard (r 1.65), every bend on the",
          "plate, none over the open corners; on junction risers and",
          "saddles each side of the bays they bridge. The pipe runs in",
          "the plate from each closed wall fitting to its riser's",
          "flange (dashed). Legs: root in the plate's notch face, pad",
          "on the ground; the corners hold only the legs."],
}


def legend(svg, x, y):
    items = [("plate", "plate (cast iron)"), ("deck", "deck / chassis top"), ("press", "press (shoulder)"),
             ("cabinet", "cabinets (cast)"), ("oxide", "red oxide (press frame, drive, rig frame)"),
             ("pipe", "pipe (cast iron)"), ("steel", "wall fitting / flange"), ("hazard", "pad hazard band")]
    cx = x
    for mat, lab in items:
        svg.rect(cx, y - 11, 16, 14, TONE[mat])
        svg.text(cx + 22, y, lab, 12, TONE["text"])
        cx += 30 + 7.0 * len(lab)
    y += 24
    cx = x
    svg.line(cx, y - 5, cx + 22, y - 5, TONE["bear"], 3)
    svg.text(cx + 28, y, "base borne by what is under it", 12, TONE["text"])
    cx += 260
    svg.line(cx, y - 5, cx + 22, y - 5, TONE["float"], 3)
    svg.add(f'<rect x="{n(cx + 28)}" y="{n(y - 12)}" width="16" height="14"{HATCH} stroke="none"/>')
    svg.text(cx + 50, y, "not borne (open air under it)", 12, TONE["text"])
    cx += 290
    svg.line(cx, y - 5, cx + 22, y - 5, TONE["muted"], 1.2, DASH)
    svg.text(cx + 28, y, "other directions' runs and fittings; pipe inside the plate", 12, TONE["text"])


def document(body, w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{n(w)}" height="{n(h)}" '
            f'viewBox="0 0 {n(w)} {n(h)}">\n' + defs() + "\n" + "\n".join(body) + "\n</svg>\n")


HEADER = ["Ballast Drill  T03h1: rebuilt to stand on its raised plate, three options",
          "Plan, south and east elevations at one scale (86 px a tile), to the 5x5 footprint grid. Wet, north direction; "
          "a dry drill draws no runs and no fittings.",
          "Common to all three: plate top 0.66, closed wall fittings at vanilla's pipe-picture positions, the pipe up "
          "through a flange on the plate top; cabinets' walls down to the plate; corners open, legs and pads on the "
          "ground;",
          "the north guide columns move in to 45 degrees, r 1.65 (signed off: 30/150 degrees, r 1.95), so no cabinet "
          "wall has to stand outside the shoes' sweep. Sizes from rig-round-5 at 401696a."]


# ================================================================ T03h2: option B on the raised plate
# Liam (2026-10-28, judging T03h1): option B; "The wall should be above the top of the pipe" ->
# "Above the fitting" -> "Yes, raise to ~0.85": the plate's top over every end ring, the wall
# fittings wholly inside the plate's wall, the runs on top lifted with it.
# The end rings' tops (rig-round-5/rig_parts.py at 401696a; ZA 0.42):
RING_TOPS = (("E/W end ring", ZA + 26 / 64 / 1.118 - 0.02),     # H_RING_R - 0.02: 0.763
             ("N end ring", ZA + 0.38 - 0.01),                  # POCKET_HW - 0.01: 0.790
             ("S end ring", ZA + 25.5 / 64 - 0.02))             # V_RING_R - 0.02: 0.798
RING_MARGIN = 0.05
RAISED_TOP = math.ceil((max(z for _, z in RING_TOPS) + RING_MARGIN) * 100) / 100     # 0.798 + 0.05 -> 0.85
RUN_LIFT = 0.30         # the run's axis over the plate top, as T03h (0.96 - 0.66): bore 0.44, 0.08 under it


def set_raised():
    """Option B2: rebind the heights that follow the plate. Called after T03h1's files are written,
    so they come out as before."""
    global PLATE_TOP, Z_RUN, HEAD_TOP, GIRDER_Z0
    PLATE_TOP = RAISED_TOP
    Z_RUN = round(PLATE_TOP + RUN_LIFT, 3)
    HEAD_TOP = round(Z_RUN + 0.30, 3)
    GIRDER_Z0 = round(PLATE_TOP - 0.10, 3)


CAPTION["B2"] = ("B2 Option B on the raised plate: plate top 0.85, over the highest end ring (0.80) by 0.05; B's deck "
                 "(0.87) merges into the plate; the runs lift with it (axis 1.15).")
HEIGHTS["B2"] = [(0.85, "plate 0.85"), (1.15, "run axis 1.15"), (2.10, "S bastion 2.10"), (2.31, "N bastion 2.31"),
                 (3.00, "gear-house 3.00")]
RUN_NOTE["B2"] = ["Runs: on the gallery (r 2.24), axis 1.15 (0.30 over the plate",
                  "top, as T03h); on junction risers (flange on the plate top),",
                  "face saddles at 1.40, and over each open corner a cast girder",
                  "(0.75 to 0.85, ends set in the notch faces, two red-oxide",
                  "posts on the ground) with a saddle at the bend. Fittings:",
                  "end rings 0.76 to 0.80, all under the plate top (0.85).",
                  "Legs: root in the plate's notch face, pad on the ground."]
HEADER_B2 = ["Ballast Drill  T03h2: option B on the raised plate, then the game view",
             "Plan, south and east elevations at one scale (86 px a tile), to the 5x5 footprint grid. Wet, north "
             "direction; a dry drill draws no runs and no fittings.",
             "Plate top 0.85: the highest end ring (S, 0.798) + 0.05. Fittings at ZA 0.42, the pipe in the plate up "
             "through a flange on the plate top; B's deck (0.87) merges into the plate; runs lifted 0.19 to axis 1.15.",
             "Game view below: the camera the Blender rig uses (tools/blender/rig.py: 60 degrees, Y stretched by "
             "1/sin 60), so a ground point draws top-down and a height z draws z/2 up the screen; 64 px a tile."]


def corner_supports(corner):
    """The supports under a run round one corner (as build() gives the north direction's two):
    a face saddle on each straight at 1.40, the cast girder over the open notch with its saddle
    at the bend, and two red-oxide posts on the ground under it."""
    sx, sy = corner
    rr = R_AX - ARC_C
    out = [Part(f"saddle-{sx}{sy}a", "face saddle", "plate_side",
                rect(sx * STUB_SADDLE - 0.10, sx * STUB_SADDLE + 0.10, sy * R_AX - 0.13, sy * R_AX + 0.13),
                PLATE_TOP, Z_RUN - R_RUN, ["plate"], tag="s"),
           Part(f"saddle-{sx}{sy}b", "face saddle", "plate_side",
                rect(sx * R_AX - 0.13, sx * R_AX + 0.13, sy * STUB_SADDLE - 0.10, sy * STUB_SADDLE + 0.10),
                PLATE_TOP, Z_RUN - R_RUN, ["plate"], tag="s")]
    a0 = 0.0 if sx > 0 else 180.0
    a1 = 90.0 if sy > 0 else 270.0
    if sx > 0 and sy < 0:
        a0 = 360.0
    gk = f"girder-{sx}{sy}"
    out.append(Part(gk, "corner girder", "plate_side", arc_band(sx * ARC_C, sy * ARC_C, rr - 0.10, rr + 0.10, a0, a1),
                    GIRDER_Z0, PLATE_TOP, [f"post-{sx}{sy}a", f"post-{sx}{sy}b", "plate"], kind="beam", tag="g"))
    mid = math.radians((a0 + a1) / 2)
    out.append(Part(f"gsaddle-{sx}{sy}", "girder saddle", "plate_side",
                    Circ(sx * ARC_C + rr * math.cos(mid), sy * ARC_C + rr * math.sin(mid), 0.09),
                    PLATE_TOP, Z_RUN - R_RUN, [gk], tag="s"))
    for ab, d in (("a", -POST_DEG), ("b", POST_DEG)):
        a = mid + math.radians(d)
        px, py = sx * ARC_C + (rr + POST_OUT) * math.cos(a), sy * ARC_C + (rr + POST_OUT) * math.sin(a)
        out.append(Part(f"post-{sx}{sy}{ab}", "frame post", "oxide", rect(px - 0.08, px + 0.08, py - 0.08, py + 0.08),
                        0.0, GIRDER_Z0, ["ground"], tag="p"))
    return out


def rig_dir(turns):
    """The wet rig for a direction (0 north, 1 east, 2 south, 3 west): the four connections'
    fittings and junctions, and two runs, each pairing a N/S junction with an E/W one round the
    corner between them (the pairing with the shorter runs), as the north direction's."""
    rr = R_AX - ARC_C
    fits = [fit_pos(c) for c in conns(turns)]
    ns = [q for q in fits if q[0] in "NS"]
    ew = [q for q in fits if q[0] in "EW"]

    def J(q):
        return on_face(q[0], riser_lat(q[1]), R_AX)

    def cost(pr):
        return sum(abs(J(a)[0] - J(b)[0]) + abs(J(a)[1] - J(b)[1]) for a, b in pr)
    pairs = min((list(zip(ns, p)) for p in (ew, ew[::-1])), key=cost)
    runs = []
    for a, b in pairs:
        corner = (1 if b[0] == "E" else -1, 1 if a[0] == "N" else -1)
        runs.append((corner, run_path(R_AX, ARC_C, rr, corner, riser_lat(b[1]), riser_lat(a[1]))))
    junctions = [(f, l) + J((f, l)) for f, l in fits]
    return dict(fits=fits, runs=runs, junctions=junctions)


def shape_dist(sh, x, y):
    """The plan distance from (x, y) to a part's shape (0 inside)."""
    if isinstance(sh, Ann):
        d = math.hypot(x - sh.cx, y - sh.cy)
        return max(0.0, d - sh.r, sh.ri - d)
    if isinstance(sh, Circ):
        return max(0.0, math.hypot(x - sh.cx, y - sh.cy) - sh.r)
    if sh.contains(x, y):
        return 0.0
    best = 9.0
    p = sh.pts
    for i in range(len(p)):
        (ax, ay), (bx, by) = p[i], p[(i + 1) % len(p)]
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy or 1)))
        best = min(best, math.hypot(x - ax - t * dx, y - ay - t * dy))
    return best


def run_clearance(parts, runs):
    """Every body part beside or over the runs: the plan gap from the bore's side to the part,
    for parts whose heights meet the run's; the height over the bore's top, for parts over it."""
    lo, hi = Z_RUN - R_RUN, Z_RUN + R_RUN
    pts = []
    for _, run in runs:
        for piece in run:
            for (ax, ay), (bx, by) in zip(piece, piece[1:]):
                k = max(1, int(math.hypot(bx - ax, by - ay) / 0.02))
                pts += [(ax + (bx - ax) * i / k, ay + (by - ay) * i / k) for i in range(k + 1)]
    out = []
    for p in parts:
        if p.kind in ("plate", "riser", "beam") or p.tag in ("s", "p"):
            continue
        d = min(shape_dist(p.shape, x, y) for x, y in pts)
        if d < R_RUN and p.z0 >= hi - 1e-9:
            out.append((p.key, "over", round(p.z0 - hi, 3)))
        elif p.z1 > lo and p.z0 < hi:
            out.append((p.key, "beside", round(d - R_RUN, 3)))
    return out


# ---------------------------------------------------------------- the game view
GV_K = 64                     # px a tile, 1x (rig.py PX_PER_TILE)
GV_CELL = 448                 # a cell, 7 tiles
GV_C = (224, 256)             # the footprint's centre in a cell, px (as the T03h stills are placed)
LIGHT_SIDE = 0.62             # the shaded face's tone, of the lit one's
SH_KX, SH_KY = 0.79, 0.25     # rig.py SHADOW_KX/KY: a height h' up the screen casts kx h' right, ky h' up
DIR_NAMES = ("north", "east", "south", "west")


def shade(hexc, f=LIGHT_SIDE):
    h = hexc.lstrip("#")
    return "#" + "".join(f"{min(255, round(int(h[i:i + 2], 16) * f)):02X}" for i in (0, 2, 4))


def circ_pts(cx, cy, r, a0, a1, k=24):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / k))) for i in range(k + 1)]


class GameView:
    """Flat-shaded drawing in the game's projection: screen x = x, screen up = y + z/2 (tiles).
    Every part: its top in its own tone (lit), its faces towards the camera in one darker tone
    (shaded); parts drawn far to near, supports before what they carry."""
    def __init__(self, svg, ox, oy, k):
        self.svg, self.ox, self.oy, self.k = svg, ox, oy, k
        self.sw = 0.6 * k / GV_K

    def P(self, x, y, z=0.0):
        return self.ox + x * self.k, self.oy - (y + 0.5 * z) * self.k

    def poly(self, pts, fill, stroke=True):
        self.svg.poly(pts, fill, TONE["line"] if stroke else "none", self.sw if stroke else 0,
                      ' stroke-linejoin="round"' if stroke else "")

    def prism(self, pts, z0, z1, col):
        a = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                for i in range(len(pts)))
        sides = []
        for i in range(len(pts)):
            (ax, ay), (bx, by) = pts[i], pts[(i + 1) % len(pts)]
            dx = bx - ax
            if (dx > 1e-9) if a > 0 else (dx < -1e-9):
                sides.append(((ay + by) / 2, [self.P(ax, ay, z0), self.P(bx, by, z0), self.P(bx, by, z1),
                                              self.P(ax, ay, z1)]))
        for _, q in sorted(sides, key=lambda t: -t[0]):
            self.poly(q, shade(col))
        self.poly([self.P(x, y, z1) for x, y in pts], col)

    def cyl(self, cx, cy, r, z0, z1, col):
        k = self.k
        bx, by = self.P(cx, cy, z0)
        tx, ty = self.P(cx, cy, z1)
        d = (f"M {n(bx - r * k)},{n(ty)} L {n(bx - r * k)},{n(by)} A {n(r * k)},{n(r * k)} 0 0 0 "
             f"{n(bx + r * k)},{n(by)} L {n(bx + r * k)},{n(ty)} Z")
        self.svg.path(d, shade(col), TONE["line"], self.sw)
        self.svg.circle(tx, ty, r * k, col, TONE["line"], self.sw)

    def ring_back(self, r_in, r_out, z0, z1, col):
        inner = [self.P(x, y, z1) for x, y in circ_pts(0, 0, r_in, 0, 180)]
        inner0 = [self.P(x, y, z0) for x, y in circ_pts(0, 0, r_in, 180, 0)]
        self.poly(inner + inner0, shade(col))
        top = circ_pts(0, 0, r_out, 0, 180) + circ_pts(0, 0, r_in, 180, 0)
        self.poly([self.P(x, y, z1) for x, y in top], col)

    def ring_front(self, r_in, r_out, z0, z1, col):
        o1 = [self.P(x, y, z1) for x, y in circ_pts(0, 0, r_out, 180, 360)]
        o0 = [self.P(x, y, z0) for x, y in circ_pts(0, 0, r_out, 360, 180)]
        self.poly(o1 + o0, shade(col))
        top = circ_pts(0, 0, r_out, 180, 360) + circ_pts(0, 0, r_in, 360, 180)
        self.poly([self.P(x, y, z1) for x, y in top], col)

    def tube(self, pts, z, r, col):
        k = self.k
        d = "M " + " L ".join(f"{n(self.P(x, y, z)[0])},{n(self.P(x, y, z)[1])}" for x, y in pts)
        j = ' stroke-linejoin="round" stroke-linecap="butt"'
        self.svg.path(d, "none", TONE["line"], 2 * r * k + 2 * self.sw, j)
        self.svg.path(d, "none", shade(col), 2 * r * k, j)
        o = 0.35 * r * k
        self.svg.path(d, "none", col, 0.9 * r * k, j + f' transform="translate({n(-o)},{n(-o)})"')

    def stick(self, a, b, w, col):
        """A leg: a bar from a to b ((x, y, z) each), w tiles thick, its upper half lit."""
        k = self.k
        (ax, ay), (bx, by) = self.P(*a), self.P(*b)
        self.svg.line(ax, ay, bx, by, TONE["line"], w * k + 2 * self.sw)
        self.svg.line(ax, ay, bx, by, shade(col), w * k)
        self.svg.line(ax, ay - 0.22 * w * k, bx, by - 0.22 * w * k, col, 0.45 * w * k)

    def shadow(self, pts, z0, z1):
        """The flat ground shadow of a prism (points in plan) from z0 to z1."""
        def S(x, y, z):
            return self.P(x + SH_KX * 0.5 * z, y + SH_KY * 0.5 * z, 0)
        b = [S(x, y, z0) for x, y in pts]
        t = [S(x, y, z1) for x, y in pts]
        self.svg.poly(b, "#000000", "none", 0)
        self.svg.poly(t, "#000000", "none", 0)
        for i in range(len(pts)):
            j = (i + 1) % len(pts)
            self.svg.poly([b[i], b[j], t[j], t[i]], "#000000", "none", 0)


def plate_with_bays():
    """The plate's outline with the four bays cut in, counter-clockwise."""
    q = [(NX, -FACE), (NX, -(NCH - NX)), (NCH - NX, -NX), (FACE, -NX)]
    bay = [(FACE, -BAY_HW), (BAY_R, -BAY_HW), (BAY_R, BAY_HW), (FACE, BAY_HW)]
    pts = []
    for k in range(4):
        c, s_ = round(math.cos(math.pi / 2 * k)), round(math.sin(math.pi / 2 * k))
        for x, y in q + bay:
            pts.append((c * x - s_ * y, s_ * x + c * y))
    return pts


def draw_gameview(svg, ox, oy, k, turns, parts):
    """The drill, wet, in direction turns, its footprint centre at (ox, oy) px, k px a tile."""
    gv = GameView(svg, ox, oy, k)
    by = {p.key: p for p in parts}
    rig = rig_dir(turns)
    sup = {}
    for corner, _ in rig["runs"]:
        sup[corner] = corner_supports(corner)
    # the ground shadow, one flat shape
    svg.add('<g opacity="0.42">')
    gv.shadow(plate_outline(), 0.0, PLATE_TOP)
    for p in parts:
        if isinstance(p.shape, Poly) and p.kind == "stand" and p.z1 > 1.5:
            gv.shadow(p.shape.pts, PLATE_TOP, p.z1)
    gv.shadow(circ_pts(0, 0, COL_R, 0, 360, 16), PLATE_TOP, 3.44)
    gv.shadow(circ_pts(0, 0, RB_OUT, 0, 360, 24), PLATE_TOP, RING_TOP)
    svg.add("</g>")

    def legs(sy):
        for sx in (-1, 1):
            root = (sx * (NCH / 2), sy * (NCH / 2), 0.445)
            gv.stick(root, (sx * PAD, sy * PAD, 0.17), 0.30, TONE["leg"])
            gv.cyl(sx * PAD, sy * PAD, PAD_R, 0.0, 0.09, TONE["hazard"])
            gv.cyl(sx * PAD, sy * PAD, PAD_R, 0.09, 0.19, TONE["leg"])

    def corner_ground(sy):
        for corner, ps in sup.items():
            if corner[1] != sy:
                continue
            for p in ps:
                if p.tag == "p":
                    gv.prism(p.shape.pts, p.z0, p.z1, TONE["oxide"])
            for p in ps:
                if p.kind == "beam":
                    gv.prism(p.shape.pts, p.z0, p.z1, TONE["plate"])

    def corner_runs(sy):
        for corner, run in rig["runs"]:
            if corner[1] != sy:
                continue
            for p in sup[corner]:
                if p.tag == "s":
                    if isinstance(p.shape, Circ):
                        gv.cyl(p.shape.cx, p.shape.cy, p.shape.r, p.z0, p.z1, TONE["plate_side"])
                    else:
                        gv.prism(p.shape.pts, p.z0, p.z1, TONE["plate_side"])
            ends = [run[0][0], run[2][-1]]
            for jx, jy in ends:
                gv.cyl(jx, jy, FLANGE_R, PLATE_TOP, PLATE_TOP + 0.03, TONE["steel"])
                gv.cyl(jx, jy, 0.24, PLATE_TOP + 0.03, Z_RUN, TONE["oxide"])
            allp = []
            for piece in run:
                allp += piece if not allp else piece[1:]
            gv.tube(allp, Z_RUN, R_RUN, TONE["pipe"])
            for jx, jy in ends:
                gv.cyl(jx, jy, R_HEAD, Z_RUN - 0.05, HEAD_TOP, TONE["oxide"])

    legs(1)
    corner_ground(1)
    for b in bay_rects(BAY_R):
        gv.prism(b.pts, 0.0, AP, TONE["apron"])
    gv.prism(plate_with_bays(), 0.0, PLATE_TOP, TONE["plate"])
    corner_runs(1)
    for sd in ("E", "W"):
        p = by[f"bast-N{sd}"]
        gv.prism(p.shape.pts, p.z0, p.z1, TONE["oxide"])
    for sd in ("E", "W"):
        f, g = by[f"gfoot-N{sd}"], by[f"guide-N{sd}"]
        gv.cyl(f.shape.cx, f.shape.cy, f.shape.r, f.z0, f.z1, TONE["press"])
        gv.cyl(g.shape.cx, g.shape.cy, g.shape.r, g.z0, g.z1, TONE["guide"])
    for sd in ("E", "W"):
        p = by[f"house-N{sd}"]
        gv.prism(p.shape.pts, p.z0, p.z1, TONE["oxide"])
    sh = by["shoulder"]
    gv.cyl(0, 0, SH_R, sh.z0, SH_TOP, TONE["press"])
    gv.ring_back(RB_IN, RB_OUT, Z_RING, RING_TOP, TONE["ring"])
    gv.cyl(0, 0, COL_R, SH_TOP, COL_TOP, TONE["column"])
    gv.cyl(0, 0, 0.44, COL_TOP, COL_TOP + 0.10, TONE["column"])
    gv.cyl(0, 0, 0.30, COL_TOP + 0.10, 3.40, TONE["column"])
    gv.cyl(0, 0, 0.10, 3.40, 3.44, TONE["steel"])
    gs = by["guide-S"]
    gv.cyl(*GUIDE_S, GUIDE_R, gs.z0, RING_TOP, TONE["guide"])
    gv.ring_front(RB_IN, RB_OUT, Z_RING, RING_TOP, TONE["ring"])
    gv.cyl(*GUIDE_S, GUIDE_R, RING_TOP, gs.z1, TONE["guide"])
    for key in ("bast-SW", "bast-SE", "tank", "bottles"):
        p = by[key]
        gv.prism(p.shape.pts, p.z0, p.z1, TONE[p.mat])
    legs(-1)
    corner_ground(-1)
    corner_runs(-1)
    # the wall fittings: S face ones stand 0.24 proud, their end rings towards the camera; E/W
    # ones sit in the wall, edge on; N face ones are behind the plate
    for f, lat, jx, jy in rig["junctions"]:
        if f == "S":
            ye = -2.53 - ZA / 2
            gv.tube([(lat, -FACE + 0.01), (lat, ye)], ZA, R_RUN, TONE["steel"])
            cx, cy = gv.P(lat, ye, ZA)
            r = V_RING_R - 0.02
            bk = 0.07 * k                       # the ring's depth (0.07 along y): its back face that far up
            svg.add(f'<ellipse cx="{n(cx)}" cy="{n(cy - bk)}" rx="{n(r * k)}" ry="{n(0.5 * r * k)}" '
                    f'fill="{shade(TONE["steel"])}" stroke="{TONE["line"]}" stroke-width="{n(gv.sw)}"/>')
            svg.rect(cx - r * k, cy - bk, 2 * r * k, bk, shade(TONE["steel"]), "none", 0)
            svg.add(f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(r * k)}" ry="{n(0.5 * r * k)}" fill="{TONE["steel"]}" '
                    f'stroke="{TONE["line"]}" stroke-width="{n(gv.sw)}"/>')
            svg.add(f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n((R_RUN - 0.03) * k)}" ry="{n(0.5 * (R_RUN - 0.03) * k)}" '
                    f'fill="#1A1816" stroke="none"/>')
        elif f in "EW":
            x = FACE if f == "E" else -FACE
            r = (H_RING_R - 0.02) * 1.118
            a = gv.P(x, lat - r, ZA)
            b = gv.P(x, lat + r, ZA)
            svg.rect(a[0] - 0.025 * k, b[1], 0.05 * k, a[1] - b[1], TONE["steel"], TONE["line"], gv.sw)
    return rig


def t03h_composite(src, here):
    """The T03h model's wet still per direction, 1x and the north one at 2x, from the take's
    sheets (r5-final/wet: meta.json and the layers), in combine.py's order with the shadows under
    at half strength (as measure.py draws a still), frame 0 of each animation; on the ground
    tone, the footprint centre at GV_C."""
    import json
    from PIL import Image
    meta = json.load(open(os.path.join(src, "meta.json")))
    g = tuple(int(TONE["ground"][i:i + 2], 16) for i in (1, 3, 5))
    for d in DIR_NAMES:
        im = Image.new("RGBA", (GV_CELL, GV_CELL), g + (255,))
        for stem in ("base-shadow", "rig-shadow", "base", "rig", "chute", "stroke", "rig-front"):
            name = f"{stem}-{d}"
            m = meta[name]
            w, h = m["size"]
            lay = Image.open(os.path.join(src, name + ".png")).convert("RGBA").crop((0, 0, w, h))
            if "shadow" in stem:
                a = lay.getchannel("A").point(lambda v: v // 2)
                lay = Image.merge("RGBA", (*Image.new("RGB", lay.size).split(), a))
            x = round(GV_C[0] + m["shift"][0] * GV_K - w / 2)
            y = round(GV_C[1] + m["shift"][1] * GV_K - h / 2)
            im.alpha_composite(lay, (x, y))
        im.convert("RGB").save(os.path.join(here, f"t03h-wet-{d}.png"), optimize=False)
        if d == "north":
            im.convert("RGB").resize((2 * GV_CELL, 2 * GV_CELL), Image.NEAREST).save(
                os.path.join(here, "t03h-wet-north-2x.png"), optimize=False)


def gameview_block(svg, x0, y0, parts):
    """The game-view sketch: row 1 the four directions at 1x, row 2 T03h's model at 1x, row 3 north
    at 2x beside T03h's north at 2x. Returns (width, height)."""
    pad, lab = 14, 26
    w = 4 * GV_CELL + 3 * pad
    y = y0
    svg.text(x0, y + 20, "GAME VIEW (option B2, wet; flat-shaded sketch, 64 px a tile) beside the T03h model render "
             "(rig-round-5 cast take, wet, frame 0), same scale and centre", 15, TONE["text"], weight="bold")
    y += 34
    for row in ("sketch", "t03h"):
        for i, d in enumerate(DIR_NAMES):
            cx = x0 + i * (GV_CELL + pad)
            svg.text(cx, y + 16, f"{d}, wet: {'B2 sketch' if row == 'sketch' else 'T03h model'} (1x)", 13,
                     TONE["dim"])
            if row == "sketch":
                svg.rect(cx, y + lab, GV_CELL, GV_CELL, TONE["ground"], "none", 0)
                svg.add(f'<svg x="{n(cx)}" y="{n(y + lab)}" width="{GV_CELL}" height="{GV_CELL}" overflow="hidden">')
                draw_gameview(svg, GV_C[0], GV_C[1], GV_K, i, parts)
                svg.add("</svg>")
            else:
                svg.add(f'<image x="{n(cx)}" y="{n(y + lab)}" width="{GV_CELL}" height="{GV_CELL}" '
                        f'href="t03h-wet-{d}.png"/>')
            footprint_marks(svg, cx, y + lab, 1)
        y += GV_CELL + lab + pad
    for i, row in enumerate(("sketch", "t03h")):
        cx = x0 + i * (2 * GV_CELL + pad)
        svg.text(cx, y + 16, f"north, wet: {'B2 sketch' if row == 'sketch' else 'T03h model'} (2x)", 13, TONE["dim"])
        if row == "sketch":
            svg.rect(cx, y + lab, 2 * GV_CELL, 2 * GV_CELL, TONE["ground"], "none", 0)
            svg.add(f'<svg x="{n(cx)}" y="{n(y + lab)}" width="{2 * GV_CELL}" height="{2 * GV_CELL}" '
                    f'overflow="hidden">')
            draw_gameview(svg, 2 * GV_C[0], 2 * GV_C[1], 2 * GV_K, 0, parts)
            svg.add("</svg>")
        else:
            svg.add(f'<image x="{n(cx)}" y="{n(y + lab)}" width="{2 * GV_CELL}" height="{2 * GV_CELL}" '
                    f'href="t03h-wet-north-2x.png"/>')
        footprint_marks(svg, cx, y + lab, 2)
    y += 2 * GV_CELL + lab + 8
    svg.text(x0, y + 14, "Ticks: the footprint's 5 tiles on the ground. Lit: each part's top in its material's tone; "
             "shaded: its faces towards the camera, 0.62 of it; light from the upper left as the rig's sun. "
             "Ground shadow flat, 0.42 black.", 12, TONE["muted"])
    return w, y + 22 - y0


def footprint_marks(svg, cx, cy, s):
    """Ticks at the footprint's corners on the ground (-2.5 .. 2.5), in a cell at scale s."""
    for gx in (-2.5, 2.5):
        for gy in (-2.5, 2.5):
            px, py = cx + (GV_C[0] + gx * GV_K) * s, cy + (GV_C[1] - gy * GV_K) * s
            dx = -1 if gx < 0 else 1
            dy = 1 if gy < 0 else -1
            svg.line(px, py, px + dx * 10 * s, py, TONE["hazard"], s)
            svg.line(px, py, px, py + dy * 10 * s, TONE["hazard"], s)


def main_b2(png):
    set_raised()
    parts, rg = build("B2")
    rep = check(parts)
    # the north direction's runs as rig_dir gives them must be build()'s
    r0 = rig_dir(0)["runs"]
    assert sorted(r for _, r in r0) == sorted(rg["runs"]), "rig_dir(0) differs from build()'s north runs"
    svg, _ = panel("B2", 0, 0)
    leg = Svg()
    legend(leg, 14, PANEL_H + 26)
    with open(os.path.join(HERE, "option-b2.svg"), "w", newline="\n") as fh:
        fh.write(document(svg.o + leg.o, PANEL_W, PANEL_H + 60))
    gsv = Svg()
    gw, gh = gameview_block(gsv, 14, 14, parts)
    gdoc_w, gdoc_h = gw + 28, gh + 28
    with open(os.path.join(HERE, "option-b2-gameview.svg"), "w", newline="\n") as fh:
        fh.write(document([f'<rect x="0" y="0" width="{n(gdoc_w)}" height="{n(gdoc_h)}" fill="{TONE["bg"]}"/>']
                          + gsv.o, gdoc_w, gdoc_h))
    # the phone sheet: header, B2's plan and elevations, the legend, the game view
    head_h = 118
    sheet = Svg()
    y = head_h
    body, _ = panel("B2", 0, y)
    y += PANEL_H + 10
    leg = Svg()
    legend(leg, 14, y + 22)
    y += 64
    g2 = Svg()
    gw, gh = gameview_block(g2, 14, y, parts)
    sh_h = y + gh + 14
    sheet.rect(0, 0, PANEL_W, sh_h, TONE["bg"], "none", 0)
    sheet.text(14, 32, HEADER_B2[0], 24, TONE["text"], weight="bold")
    for k_, t in enumerate(HEADER_B2[1:]):
        sheet.text(14, 58 + 18 * k_, t, 13, TONE["dim"])
    sheet.o += body.o + leg.o + g2.o
    with open(os.path.join(HERE, "sheet-b2.svg"), "w", newline="\n") as fh:
        fh.write(document(sheet.o, PANEL_W, sh_h))
    print(f"\nB2: plate top {PLATE_TOP} (highest end ring {max(z for _, z in RING_TOPS):.3f} + {RING_MARGIN}); "
          f"run axis {Z_RUN}, bore {R_RUN * 2}, bottom {Z_RUN - R_RUN:.2f}, top {Z_RUN + R_RUN:.2f}; "
          f"riser head top {HEAD_TOP}; girder {GIRDER_Z0}..{PLATE_TOP}")
    for nm, z in RING_TOPS:
        print(f"  {nm}: top {z:.3f}, under the plate top by {PLATE_TOP - z:.3f}")
    print(f"  in-plate pipe: top {ZA + R_RUN:.2f}, under the plate top by {PLATE_TOP - ZA - R_RUN:.2f}")
    print(f"  flange top {PLATE_TOP + 0.03:.2f}, under the run's bottom by {Z_RUN - R_RUN - PLATE_TOP - 0.03:.2f}")
    print("  support (north):")
    for p, frac, msg in rep:
        if frac is None:
            print(f"    {p.key:16s} beam: {msg}")
        else:
            print(f"    {p.key:16s} {frac * 100:5.1f}% not borne (on {', '.join(p.on)})")
    for t in range(4):
        rig = rig_dir(t)
        extra = []
        for corner, _ in rig["runs"]:
            extra += corner_supports(corner)
        allp = [p for p in parts if not (p.tag in ("s", "g", "p") or p.kind == "riser")] + extra
        bad = [(p.key, round(fr * 100, 1)) for p, fr, m in check(allp)
               if (fr is not None and fr > 0.0) or (fr is None and m != "both ends bear")]
        cl = run_clearance(parts, rig["runs"])
        over = [c for c in cl if c[1] == "over"]
        beside = sorted([c for c in cl if c[1] == "beside"], key=lambda c: c[2])
        print(f"  {DIR_NAMES[t]}: corners {[c for c, _ in rig['runs']]}; supports not borne: {bad or 'none'}; "
              f"parts over a run: {over or 'none'}; nearest beside: {beside[:3]}")
    print(f"sheet-b2 {n(PANEL_W)} x {n(sh_h)} px; game view {n(gdoc_w)} x {n(gdoc_h)} px")
    if png:
        subprocess.run(["rsvg-convert", "-o", os.path.join(HERE, "sheet-b2.png"), os.path.join(HERE, "sheet-b2.svg")],
                       check=True)


def main():
    png = "--png" in sys.argv
    reports = {}
    bodies = {}
    for opt in "ABC":
        svg, rep = panel(opt, 0, 0)
        reports[opt] = rep
        leg = Svg()
        legend(leg, 14, PANEL_H + 26)
        doc = document(svg.o + leg.o, PANEL_W, PANEL_H + 60)
        with open(os.path.join(HERE, f"option-{opt.lower()}.svg"), "w", newline="\n") as fh:
            fh.write(doc)
        bodies[opt] = svg
    # the phone sheet: a header, one option per row, the legend
    head_h = 118
    sheet = Svg()
    sheet.rect(0, 0, PANEL_W, head_h + 3 * PANEL_H + 3 * 10 + 64, TONE["bg"], "none", 0)
    sheet.text(14, 32, HEADER[0], 24, TONE["text"], weight="bold")
    for k, t in enumerate(HEADER[1:]):
        sheet.text(14, 58 + 18 * k, t, 13, TONE["dim"])
    y = head_h
    for opt in "ABC":
        svg, _ = panel(opt, 0, y)
        sheet.o += svg.o
        y += PANEL_H + 10
    legend(sheet, 14, y + 22)
    sh = y + 64
    doc = document(sheet.o, PANEL_W, sh)
    with open(os.path.join(HERE, "sheet.svg"), "w", newline="\n") as fh:
        fh.write(doc)
    for opt in "ABC":
        print(f"option {opt}:")
        for p, frac, msg in reports[opt]:
            if frac is None:
                print(f"  {p.key:16s} beam: {msg}")
            elif frac > 0.0:
                print(f"  {p.key:16s} {frac * 100:5.1f}% not borne (on {', '.join(p.on)})")
    print(f"sheet {n(PANEL_W)} x {n(sh)} px")
    if png:
        subprocess.run(["rsvg-convert", "-o", os.path.join(HERE, "sheet.png"), os.path.join(HERE, "sheet.svg")],
                       check=True)
    # T03h2: option B on the raised plate, and its game view
    if "--t03h" in sys.argv:
        t03h_composite(sys.argv[sys.argv.index("--t03h") + 1], HERE)
    main_b2("--png-b2" in sys.argv or png)


if __name__ == "__main__":
    main()
