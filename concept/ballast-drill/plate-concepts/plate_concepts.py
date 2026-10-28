#!/usr/bin/env python3
"""Ballast Drill, T03h1 (task ballast-drill-ports): three 2D concepts for the drill rebuilt to
stand on its raised plate, each a top plan and south and east elevations at one scale, to the
footprint grid. Drawn as code: plain SVG text, fixed number formatting, nothing random and no
timestamps, so running this again gives byte-identical SVGs.

    python3 plate_concepts.py [--png]

Writes option-a.svg, option-b.svg, option-c.svg and sheet.svg beside this file; --png also
renders sheet.png (the phone sheet, one option per row) with rsvg-convert.

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

    def add(*a, **k):
        p = Part(*a, **k)
        P.append(p)
        return p

    deck = option in "AB"
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
        foot_top = DECK_TOP + 0.14 if deck else PLATE_TOP + 0.06
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
    svg.text(130, 29, CAPTION[option][3:], 14, TONE["text"])
    top = 1.0 * S
    # plan
    cx, cy = VIEW / 2 * S, top + VIEW / 2 * S
    plan(svg, cx, cy, parts, rg, option)
    svg.text(cx - VIEW / 2 * S + 8, top + 16, "PLAN (north up; wet, north direction)", 12, TONE["text"])
    dim_h(svg, cx - 2.5 * S, cx + 2.5 * S, cy - 2.78 * S, "5.00 (footprint)")
    if option in "AB":
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
    for z, lab in ((PLATE_TOP, "plate 0.66"), (ZA, "fitting 0.42"), (Z_RUN, "run 0.96"), (RING_TOP, "ring 2.14"),
                   (3.44, "dome 3.44")):
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


if __name__ == "__main__":
    main()
