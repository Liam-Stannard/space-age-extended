#!/usr/bin/env python3
"""Radiant Generator, round 5, suggestions 6-10: sheets, GIFs, measures, contact sheet.

  python3 r5b_sheets.py <renders-root> [--factorio <data>] [--master <checkout>] [--rp <rp round-5 dir>]

<renders-root>/f6 ... f10 are the r5b_<n>_*.py outputs (idle.png, plate.png,
plate-working.png at 4x; working-NN.png at 2x; info.json). Writes beside this script:

  <n>-<slug>.png          the sheet: idle and working at 2x, the cell-to-wire chain
                          numbered on the working plate, the motion map, frames, a block
                          of four, the pitch, the animation plan, the Reactor headroom,
                          the finish and the measures
  <n>-<slug>-1x.gif       the working loop at game scale (for git)
  <n>-<slug>-2x.gif       the same at 2x (out of git, as the task says)
  measures-b.json         every measure on the sheets
  contact-sheet-b.png     the five at game scale beside vanilla's steam engine, steam
                          turbine and fusion generator, the Reaction Plant (round 5) and
                          the Siderane turbine

Not adopted; nothing here is signed off.
"""
import argparse
import json
import os
import re

from PIL import Image, ImageChops, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("root")
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
ap.add_argument("--master", default=os.path.expanduser("~/git/space-age-extended/.claude/worktrees/master-merge"))
ap.add_argument("--rp", default=os.path.expanduser(
    "~/git/space-age-extended/.claude/worktrees/reaction-plant-redesign/concept/reaction-plant/options/round-5"))
args = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__))
FD = args.factorio
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT = (228, 222, 210)
SUB = (175, 168, 156)
HEAD = (240, 200, 120)
GIF_MS = 70


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


F_T, F_H, F_B, F_S = font(30, True), font(17, True), font(14), font(12)


def ground(size, origin, ppt, foot, extent=12):
    g = Image.new("RGBA", size, GROUND)
    ov = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    ox, oy = origin
    fx, fy = foot
    offx = 0.5 if fx % 2 else 0.0
    offy = 0.5 if fy % 2 else 0.0
    for i in range(-extent * 2, extent * 2 + 1):
        x = ox + (i + offx) * ppt
        y = oy + (i + offy) * ppt
        d.line([(x, 0), (x, size[1])], fill=(255, 255, 255, 26))
        d.line([(0, y), (size[0], y)], fill=(255, 255, 255, 26))
    d.rectangle([ox - fx * ppt / 2, oy - fy * ppt / 2, ox + fx * ppt / 2, oy + fy * ppt / 2],
                outline=(255, 255, 255, 120))
    g.alpha_composite(ov)
    return g


def scaled(im, f):
    im = im.convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    return im.convert("RGBa").resize((round(im.width * f), round(im.height * f)), Image.LANCZOS).convert("RGBA")


def on_ground(im, info, k):
    o = (info["origin"][0] * k, info["origin"][1] * k)
    g = ground(im.size, o, 64 * k, info["footprint"])
    g.alpha_composite(im)
    return g


def to_screen(info, k, x, y, z):
    ox, oy = info["origin"]
    return (ox + x * 64) * k, (oy - (y + z / 2) * 64) * k


# ---------------------------------------------------------------- the five
S = {}
S[6] = dict(
    slug="the-alternator-hall", name="THE ALTERNATOR HALL", foot="3x5",
    why="3x5, the generator's footprint today: a long hall reads as a power station's machine floor, the "
        "chain runs south to north in one line (cell, heat, turbine, alternator, wire), and the Reactor at "
        "stage 4 is free to be the square, bigger thing.",
    pitch="A power-station machine floor on 3x5. The cell goes into a lead core pot at the south end through "
          "a six-place revolver; its heat goes into a sealed gas loop; a turbine-compressor turns, through a "
          "bevel gearbox, an upright alternator whose rotor, slip rings and exciter stand open on top -- the "
          "building's moving heart, seen from above the way a hydro-station generator is. The current leaves "
          "by a bus duct through the switch house's meters into three cable trunks. The blue shows only in "
          "the core's three slots and the cells' windows in the revolver.",
    chain=[("cell in: the revolver, six cells, indexing one place", (0.98, -1.98, 0.9)),
           ("lead core pot: the cell's heat; three shielded slots", (0.05, -2.32, 0.75)),
           ("hot leg, lagged (red ring)", (0.55, -1.25, 1.35)),
           ("turbine (dark steel)", (0.6, -0.72, 0.7)),
           ("bevel gearbox; a coupling turns either side", (-0.08, -0.92, 0.55)),
           ("compressor: the cold gas back to the core", (-0.82, -0.72, 0.7)),
           ("alternator: rotor, slip rings, exciter, brushes", (-0.12, 0.28, 1.55)),
           ("gas cooler: radiator panels (vacuum: no fans)", (1.2, 0.6, 1.15)),
           ("make-up tank on the cold return", (-1.08, 1.12, 1.4)),
           ("bus duct -> switch house; output meters", (0.1, 1.6, 0.85)),
           ("cable trunks out", (1.3, 2.05, 0.3)),
           ("spent cells out: the lead spent bin", (-1.02, -2.0, 0.65))],
    anim=["rotor, slip rings and exciter: half a turn a loop (8 poles; the exciter's stripe is 2-fold), 24 frames",
          "couplings either side of the gearbox: a sixth of a turn a loop (6 lobes), 24 frames",
          "cell revolver: indexes one place in frames 1-10, rests the rest of the loop (6-fold); proposed as its "
          "own layer so it indexes about once a cell, not once a loop (unchecked in engine)",
          "glow (draw_as_glow): the slots' light flowing, the revolver cells' windows; 24 frames",
          "meters: the needles hunt with the load, 24 frames",
          "idle_animation: the same layers parked at frame 0, glow off, lamp off",
          "perceived_performance scales the rotor and couplings with output; the glow does not scale "
          "(burner-generator: no working_visualisations)"],
    headroom="Stage 1 is one alternator behind three slots: the core is never seen, there are no masts, arcs, "
             "beams or open light, and one machine set. The Reactor keeps the open core in its turning shutters "
             "(the Gyre), the masts and arcs, the neighbour link, and drives several alternator sets from one "
             "core -- the hall becomes its wing.",
    finish="lead: the core pot, spent bin, feed throat (the isotope's housing). Weathered green: the alternator "
           "and the revolver's cheeks. Ochre: the make-up tank, the feed hopper. Cream: the switch house; oxide "
           "red: its louvre roof. Grey: gearbox, compressor, radiator panels. Dark steel: turbine, skids, decks. "
           "Bare steel pipes and ribs; copper rotor poles and slip rings; brass brushes and gauges; tan and "
           "black hose; red and yellow handwheels; ID plates, hazard tags, oil stains.",
    reactor="Radiant Reactor: the Gyre's open core at 7x7 with two alternator halls as its east and west wings; "
            "neighbours link by the shared corner mast (round 4).")
S[7] = dict(
    slug="the-plate-rack", name="THE PLATE RACK", foot="4x4",
    why="4x4: the rack wants length (ten slots between eleven plates) and the converter set wants a skid "
        "beside it; 4x4 holds both with corners for the magazine, the transformer and the radiators, and "
        "tiles square in a block.",
    pitch="Direct collection, no heat engine at all. The cells stand in a lead trough between charged copper "
          "collector plates; the isotope's emission charges the plates and two copper bus bars gather it as "
          "direct current, which a rotary converter -- a DC motor with its commutator open, coupled to an AC "
          "machine -- turns into the grid's current. An ochre gantry runs the rack's length: out with a "
          "fresh cell, set into the empty slot, back with the spent one to the magazine. The north half of "
          "the rack is under hinged lead lids; the blue shows only in the south row of cells and between "
          "the plates.",
    chain=[("cell magazine: two loading ports (ochre)", (-1.72, 0.18, 1.7)),
           ("gantry shuttle: out with a fresh cell, back with the spent", (-0.3, 0.18, 1.25)),
           ("collector rack: cells between copper plates (lead trough)", (0.3, -0.25, 0.75)),
           ("hinged lead lids over the north row", (0.0, 0.5, 1.0)),
           ("bus bars (copper) -> the DC drop", (-0.6, -0.65, 0.85)),
           ("DC motor, commutator open (turning)", (-0.85, -1.42, 0.9)),
           ("coupling -> AC machine (grey, ribbed)", (0.35, -1.42, 0.95)),
           ("transformer (cream) -> cable trunks", (1.48, -1.4, 1.15)),
           ("coolant: pump, copper radiator bank", (1.4, 1.45, 1.05)),
           ("spent bin (lead)", (-1.65, -0.85, 0.5))],
    anim=["gantry: out and back once a loop, the gripper lowering at each end; the cell it carries changes "
          "from fresh to spent at the turn (2 sprite variants of the carriage); 24 frames",
          "commutator: a sixth of a turn a loop (12 bars: seamless), 24 frames; the coupling likewise",
          "glow (draw_as_glow): the cells' windows and the faint floor between the plates, flowing; 24 frames",
          "converter meter: the needle kicks as the cell is set, 24 frames",
          "idle_animation: gantry parked over the magazine, glow off",
          "perceived_performance: the gantry's pace and the commutator"],
    headroom="Stage 1 collects from cells standing in a trough: low, no core, no heat engine, no light but "
             "window-sized. The Reactor is the first machine to concentrate the isotope into one core you can "
             "see, to make heat, and to need the masts; it outclasses the rack in kind, not only in size.",
    finish="lead: the trough, lids, throat and spent bin. Ochre: the magazine and the gantry bridge. Weathered "
           "green: the DC motor, the travel and pump motors. Grey: the AC machine, the expansion tank. Cream: "
           "the transformer. Copper: collector plates, bus bars, radiator bank, commutator. Dark steel: skids, "
           "copings, frames. Bare steel rails and pipes; brass clips and gauges; tan and black hose; cable "
           "tray with red, black and grey cables.",
    reactor="Radiant Reactor: one core (no plates); a plate rack could return there as its stage-3 cell "
            "reprocessing feed, not as power.")
S[8] = dict(
    slug="the-charge-and-dump-bank", name="THE CHARGE-AND-DUMP BANK", foot="4x4",
    why="4x4: six drums stand round the pot at 1.4 tiles; 4x4 is the smallest square that holds the ring with "
        "the magazine, output cabinet and coolant in the corners. Rotation-symmetric, so one plate could serve "
        "every direction if the cabinet turns with it.",
    pitch="A capacitor bank round a collector. The cell sits in a lead collector pot with two bullseye ports; "
          "the collector charges six capacitor drums standing round it, and a rotary distributor on the pot's "
          "head -- a heavy copper arm on a geared hub -- sweeps round, touching each drum's contact in turn and "
          "dumping it into the output bus. Each drum's lamp column climbs as it charges and drops as the arm "
          "passes; the big meter on the output cabinet kicks at every dump. The blue shows only in the two "
          "ports.",
    chain=[("cell magazine (ochre) -> lead throat", (-1.42, -1.35, 1.25)),
           ("collector pot (lead): two bullseye ports", (0.0, -0.4, 0.9)),
           ("charging leads to the drums", (-0.85, -0.35, 0.3)),
           ("six capacitor drums; charge columns", (1.38, 0.22, 1.7)),
           ("contact posts (copper)", (0.5, 1.05, 1.6)),
           ("distributor arm: sweeps, dumps each drum", (0.0, 0.22, 1.7)),
           ("hub, drive motor, bus duct down the pot", (0.42, -0.2, 1.1)),
           ("output cabinet: the dump meter", (0.75, -1.55, 1.1)),
           ("cable trunks out", (1.75, -1.6, 0.3)),
           ("coolant: radiator bank, pump", (0.0, 1.75, 1.0))],
    anim=["distributor arm: one turn a loop (6 drums: 6 dumps a loop), 24 frames",
          "charge columns (glow, draw_as_glow): five lamps a drum, each drum's level a saw that resets as the "
          "arm passes; 24 frames, white-green, never orange",
          "dump meter: kicks six times a loop, 24 frames",
          "ports (glow): the light swirling, 24 frames",
          "idle_animation: arm parked, columns dark, ports dark",
          "perceived_performance: the arm's speed (dumps a second)"],
    headroom="Stage 1 is a collector with a bank: no heat, no core seen, the light in two ports. The Reactor "
             "adds the open core, the heat, the masts and arcs; its bank, if kept, becomes a ring of drums "
             "shared between neighbours.",
    finish="lead: the pot, throat and spent box. Cream and weathered green drums, alternating; oxide red output "
           "cabinet; ochre magazine and expansion tank; copper arm, contact posts, radiator bank; brass shoe, "
           "hub nut, contacts and gauges; dark steel feet, hub, counterweight; bare steel flanges; black and "
           "red charging leads; hazard stripe on the arm so its turn reads.",
    reactor="Radiant Reactor: the Gyre core in the middle of a ring of drums at 7x7; the shared corner mast "
            "links neighbours as round 4 drew it.")
S[9] = dict(
    slug="the-pebble-column", name="THE PEBBLE COLUMN", foot="3x3",
    why="3x3: the smallest footprint here, a tower instead of a floor: ten megawatts from a column of cells "
        "is the read, and the Reactor (bigger, square, open-cored) has every inch of size to grow into.",
    pitch="A column of cells. A bucket elevator lifts each fresh cell up the east side and tips it into the "
          "head of a lead column; the cells settle down past four thermoelectric rings -- copper collars whose "
          "cold sides are finned radiators -- and a star valve at the foot lets the spent ones out to the spent "
          "bin. The rings make the current directly; their taps run down to the combiner cabinet and out. "
          "The blue shows in four slots between the rings, falling as the bed falls, and in the cells "
          "climbing in the elevator's buckets.",
    chain=[("boot: the inserter's loading port (ochre)", (0.98, -0.2, 0.55)),
           ("bucket elevator: fresh cells climb the front run", (0.98, 0.05, 2.0)),
           ("head chute into the column's hopper", (0.4, 0.2, 3.3)),
           ("lead column: the bed of cells, falling in four slots", (-0.22, -0.25, 1.6)),
           ("thermoelectric rings: copper, finned cold side", (-0.85, 0.2, 2.3)),
           ("ring taps -> combiner cabinet, output meter", (-1.0, -0.95, 1.0)),
           ("cable trunk out", (-1.45, -1.0, 0.3)),
           ("star valve at the foot (turning)", (-0.22, -0.4, 0.5)),
           ("spent bin (lead)", (0.88, -0.98, 0.55))],
    anim=["bucket elevator: 16 buckets, two pitches a loop up the front run (cells lit going up, empty "
          "coming down), 24 frames",
          "star valve: a sixth of a turn a loop (6 pockets), its gear-motor coupling turning; 24 frames",
          "head drive: coupling, a sixth of a turn a loop",
          "glow (draw_as_glow): the bed's light falling in the four slots, 24 frames; the buckets' cells",
          "combiner meter: hunting with the load, 24 frames",
          "idle_animation: elevator stopped, glow off",
          "perceived_performance: elevator and star valve pace"],
    headroom="Stage 1 is a slender 3x3 tower with no core and no heat engine; the Reactor is the first square, "
             "massive, open-cored machine, many times its footprint, and the only one with arcs and masts.",
    finish="lead: the column, its head, the spent chute and bin. Copper: the four rings; grey: their radiating "
           "fins. Ochre: the elevator casing and boot. Weathered green: the elevator head and the star valve's "
           "gear-motor. Grey: the combiner. Oxide: the instrument-air box. Dark steel legs, bands, feet; bare "
           "steel bands, flanges; yellow star rotor; black cable trunks, tan hose; barrels.",
    reactor="Radiant Reactor: the Gyre core; columns of this kind could stand at its corners as its cell "
            "store, not its power.")
S[10] = dict(
    slug="the-governed-gyre", name="THE GOVERNED GYRE", foot="4x4",
    why="4x4: round 4's core and shutter bands kept whole need about 2.2 tiles across with the shield pot; "
        "the turbine-alternator skid along the south and the radiators along the north and east take the "
        "rest. 3x3 could not keep the bands readable at 1x.",
    pitch="Round 4's Gyre made into a generator and governed. The core and its counter-rotating shutter bands "
          "are kept as the regulator -- the bands open and close the core's light on the exchanger jacket "
          "round the pot -- under a small lead lid on three posts; the column, masts, arcs and beams are "
          "gone, left for the Reactor. The heat leaves in a sealed gas loop to a compact turbine-alternator "
          "skid on the south edge, whose slip rings turn open on the alternator's end. The blue shows "
          "between the bands only.",
    chain=[("cell magazine (ochre) -> lead chute", (-1.62, 0.3, 1.35)),
           ("shield pot (lead), core in the shutter bands", (-0.1, -0.2, 1.4)),
           ("exchanger jacket: ring header round the pot", (0.7, -0.15, 0.85)),
           ("hot leg, lagged (red ring)", (-0.4, -1.0, 1.1)),
           ("turbine (dark steel)", (-0.9, -1.48, 0.9)),
           ("coupling (turning)", (-0.5, -1.48, 0.7)),
           ("alternator (green), slip rings turning", (0.3, -1.48, 0.95)),
           ("breaker cabinet (cream), meter -> cable trunks", (1.52, -1.35, 1.2)),
           ("radiator banks (N, E), pump, expansion tank", (1.55, 0.3, 1.05)),
           ("spent bin (lead)", (-1.6, -0.55, 0.45))],
    anim=["inner bands: a quarter turn a loop (4 segments); outer: a sixth back (6); gimbal ring: a third "
          "(3-fold); 24 frames -- round 4's motion, slower",
          "core and band gaps (glow, draw_as_glow): pulsing, 24 frames",
          "alternator slip rings: half a turn a loop (2-fold stripe); turbine coupling a sixth; 24 frames",
          "meters: hunting with the load, 24 frames",
          "idle_animation: bands parked half-closed, glow off",
          "perceived_performance: the bands and the alternator speed"],
    headroom="Stage 1 keeps only the Gyre's regulator: one small core under a lid, no column, no masts, no "
             "arcs, no beams. The Reactor gets them all back -- the spire, the masts, the arcs, the corner "
             "link -- so the family read is direct: the generator is the Reactor's core without its crown.",
    finish="lead: the shield pot, lid, chute and spent bin; copper edges on the inner bands; weathered green "
           "outer bands and the alternator; ochre magazine; cream breaker cabinet and expansion tank; grey "
           "radiator panels; dark steel turbine, skids, gimbal blocks; bare steel ring header, posts, pipes; "
           "lagged hot leg with a red ring; tan and black hose.",
    reactor="Radiant Reactor: round 4's Gyre Spire, 7x7, linked by the shared corner mast -- this suggestion "
            "is its core cut down.")


# ---------------------------------------------------------------- measures
def measure(d, info):
    plate = Image.open(os.path.join(d, "plate.png")).convert("RGBA")
    a1 = plate.getchannel("A").resize((plate.width // 4, plate.height // 4), Image.BOX)
    ox, oy = info["origin"]
    fx, fy = info["footprint"]
    x0, x1 = ox - fx * 32, ox + fx * 32
    y0, y1 = oy - fy * 32, oy + fy * 32
    px = a1.load()
    inside = sum(1 for y in range(int(y0), int(y1)) for x in range(int(x0), int(x1)) if px[x, y] > 127)
    cover = inside / (fx * fy * 64 * 64)
    top = next((y for y in range(a1.height) if any(px[x, y] > 127 for x in range(a1.width))), y0)
    rise = (y0 - top) / 64
    # the lit: working minus idle, blue-dominant, at 1x
    w = Image.open(os.path.join(d, "plate-working.png")).convert("RGB").resize(a1.size, Image.BOX)
    i = plate.convert("RGB").resize(a1.size, Image.BOX)
    wp, ip = w.load(), i.load()
    opaque = sum(1 for y in range(a1.height) for x in range(a1.width) if px[x, y] > 127)
    lit = 0
    for y in range(a1.height):
        for x in range(a1.width):
            if px[x, y] > 127:
                r, g, b = wp[x, y]
                r0, g0, b0 = ip[x, y]
                if b - b0 > 25 and b > r + 30:
                    lit += 1
    # moving: any frame differs from frame 0 by more than 12 at 1x
    frames = sorted(f for f in os.listdir(d) if f.startswith("working-"))
    ims = [Image.open(os.path.join(d, f)).convert("RGBA").resize(a1.size, Image.BOX) for f in frames]
    acc = Image.new("L", a1.size, 0)
    for im in ims[1:]:
        diff = ImageChops.difference(im, ims[0]).convert("RGB")
        acc = ImageChops.lighter(acc, diff.convert("L"))
    mv = acc.point(lambda v: 255 if v > 12 else 0)
    mp = mv.load()
    moving = sum(1 for y in range(a1.height) for x in range(a1.width) if mp[x, y] and px[x, y] > 127)
    return dict(cover=round(100 * cover, 1), rise=round(rise, 2), blue=round(100 * lit / opaque, 1),
                moving=round(100 * moving / opaque, 1), bbox=[round(a1.getbbox()[2] / 64 - a1.getbbox()[0] / 64, 2),
                                                             round(a1.getbbox()[3] / 64 - a1.getbbox()[1] / 64, 2)],
                frames=len(frames)), mv


def wrap(d, text, xy, width, fnt, fill=TEXT, lh=None):
    x, y = xy
    lh = lh or int(fnt.size * 1.35)
    words = text.split()
    line = ""
    for wd in words:
        t = (line + " " + wd).strip()
        if d.textlength(t, font=fnt) > width:
            d.text((x, y), line, font=fnt, fill=fill)
            y += lh
            line = wd
        else:
            line = t
    if line:
        d.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def frame1x(d, info, f):
    im = Image.open(os.path.join(d, f"working-{f:02d}.png"))
    return on_ground(scaled(im, 0.5), info, 1)


def build(n, s):
    d = os.path.join(args.root, f"f{n}")
    info = json.load(open(os.path.join(d, "info.json")))
    m, mv = measure(d, info)
    idle2 = on_ground(scaled(Image.open(os.path.join(d, "idle.png")), 0.5), info, 2)
    work2 = on_ground(Image.open(os.path.join(d, "working-00.png")).convert("RGBA"), info, 2)
    chain2 = work2.copy()
    cd = ImageDraw.Draw(chain2)
    for k, (label, xyz) in enumerate(s["chain"]):
        x, y = to_screen(info, 2, *xyz)
        cd.ellipse([x - 15, y - 15, x + 15, y + 15], fill=(240, 200, 120, 235), outline=(30, 29, 28, 255), width=2)
        t = str(k + 1)
        tw = cd.textlength(t, font=F_H)
        cd.text((x - tw / 2, y - 11), t, font=F_H, fill=(30, 29, 28))
    # motion map at 1x: the moving pixels in cyan over the plate greyed
    base = frame1x(d, info, 0)
    grey = base.convert("L").convert("RGBA")
    grey = Image.blend(grey, Image.new("RGBA", grey.size, GROUND), 0.35)
    tint = Image.new("RGBA", grey.size, (60, 230, 255, 255))
    grey.paste(tint, (0, 0), mv)
    # frames at 1x
    nf = m["frames"]
    picks = [0, nf // 4, nf // 2, 3 * nf // 4]
    fr = [frame1x(d, info, f) for f in picks]
    # a block of four at 1x: 2x2, edge to edge
    fx, fy = info["footprint"]
    one = scaled(Image.open(os.path.join(d, "working-00.png")), 0.5)
    bw, bh = one.width + fx * 64, one.height + fy * 64
    ob = (info["origin"][0], info["origin"][1] + fy * 64)
    block = ground((bw, bh), (ob[0] + fx * 32, ob[1] - fy * 32), 64, (2 * fx, 2 * fy))
    for j in (1, 0):
        for i in (0, 1):
            block.alpha_composite(one, (i * fx * 64, (1 - j) * fy * 64))
    # layout
    pad = 24
    W2 = idle2.width
    top = 90
    sheet_w = max(3 * W2 + 4 * pad, 2400)
    bx_ = pad + grey.width + pad + 4 * (base.width + 8) + pad
    bh_ = block.height if bx_ + block.width <= sheet_w else block.height // 2
    row2_h = max(base.height, bh_) + 40
    sheet_h = top + idle2.height + 40 + row2_h + 980
    sh = Image.new("RGBA", (sheet_w, sheet_h), BG)
    dr = ImageDraw.Draw(sh)
    dr.text((pad, 18), f"RADIANT GENERATOR, ROUND 5 -- SUGGESTION {n}: {s['name']} ({s['foot']})", font=F_T,
            fill=HEAD)
    dr.text((pad, 58), "Lit Blender render on the GPU in the Reaction Plant's round-5 finish (palette, worn_paint, "
                       "details); ChatGPT was not used. 64 px a tile at 1x. Options round: nothing adopted, "
                       "nothing signed off.", font=F_B, fill=SUB)
    y = top
    for k, (lab, im) in enumerate((("idle (off), 2x", idle2), ("working, frame 0, 2x", work2),
                                   ("the cell-to-wire chain, 2x (numbers: legend below)", chain2))):
        x = pad + k * (W2 + pad)
        dr.text((x, y), lab, font=F_S, fill=SUB)
        sh.alpha_composite(im, (x, y + 18))
    y += idle2.height + 40
    x = pad
    dr.text((x, y), "motion map, 1x (cyan: pixels that move or change)", font=F_S, fill=SUB)
    sh.alpha_composite(grey, (x, y + 18))
    x += grey.width + pad
    for f, im in zip(picks, fr):
        dr.text((x, y), f"frame {f}/{nf}, 1x", font=F_S, fill=SUB)
        sh.alpha_composite(im, (x, y + 18))
        x += im.width + 8
    x += pad
    if x + block.width <= sheet_w:
        dr.text((x, y), "a block of four, 1x (edge to edge)", font=F_S, fill=SUB)
        sh.alpha_composite(block, (x, y + 18))
    else:
        b2 = block.resize((block.width // 2, block.height // 2), Image.LANCZOS)
        dr.text((x, y), "a block of four, 1/2 scale (edge to edge)", font=F_S, fill=SUB)
        sh.alpha_composite(b2, (x, y + 18))
    y += row2_h
    colw = (sheet_w - 3 * pad) // 2
    lx, rx = pad, pad * 2 + colw
    yl = y
    dr.text((lx, yl), "PITCH", font=F_H, fill=HEAD)
    yl = wrap(dr, s["pitch"], (lx, yl + 26), colw, F_B) + 12
    dr.text((lx, yl), "FOOTPRINT", font=F_H, fill=HEAD)
    yl = wrap(dr, s["why"], (lx, yl + 26), colw, F_B) + 12
    dr.text((lx, yl), "CELL TO WIRE (the numbers on the chain plate)", font=F_H, fill=HEAD)
    yl += 26
    for k, (lab, _) in enumerate(s["chain"]):
        yl = wrap(dr, f"{k + 1}  {lab}", (lx, yl), colw, F_B)
    yl += 12
    dr.text((lx, yl), "FINISH", font=F_H, fill=HEAD)
    yl = wrap(dr, s["finish"], (lx, yl + 26), colw, F_B) + 12
    yr = y
    dr.text((rx, yr), "ANIMATION PLAN (burner-generator: animation + idle_animation; all glow draw_as_glow in them)",
            font=F_H, fill=HEAD)
    yr += 26
    for a in s["anim"]:
        yr = wrap(dr, "- " + a, (rx, yr), colw, F_B)
    yr += 12
    dr.text((rx, yr), "REACTOR HEADROOM (stage 1 of 4)", font=F_H, fill=HEAD)
    yr = wrap(dr, s["headroom"], (rx, yr + 26), colw, F_B)
    yr = wrap(dr, s["reactor"], (rx, yr + 4), colw, F_B, fill=SUB) + 12
    dr.text((rx, yr), "MEASURED (1x, from the renders)", font=F_H, fill=HEAD)
    meas = (f"Footprint {s['foot']}. Covered by mass: {m['cover']} % of the footprint. Rise above the north edge: "
            f"{m['rise']} tiles (fusion reactor +0.66, refinery +0.97). Sprite bbox {m['bbox'][0]} x {m['bbox'][1]} "
            f"tiles (the mass, no shadow). Blue (lit) pixels: {m['blue']} % of the opaque plate (Reaction Plant r5 3.2 %). "
            f"Moving or changing pixels over the loop: {m['moving']} % (chemical plant 5.2 %, refinery 15.9 %). "
            f"Loop: {m['frames']} frames; the GIF plays at {GIF_MS} ms a frame.")
    yr = wrap(dr, meas, (rx, yr + 26), colw, F_B) + 12
    bottom = max(yl, yr) + pad
    sh = sh.crop((0, 0, sheet_w, bottom))
    slug = f"{n}-{s['slug']}"
    sh.convert("RGB").save(os.path.join(HERE, slug + ".png"), optimize=True)
    # GIFs
    for k, tag in ((1, "1x"), (2, "2x")):
        q = []
        for f in range(nf):
            im = Image.open(os.path.join(d, f"working-{f:02d}.png"))
            im = scaled(im, 0.5) if k == 1 else im.convert("RGBA")
            q.append(on_ground(im, info, k).convert("RGB").quantize(colors=255, method=Image.MEDIANCUT,
                                                                     dither=Image.FLOYDSTEINBERG))
        path = os.path.join(HERE, f"{slug}-{tag}.gif")
        q[0].save(path, save_all=True, append_images=q[1:], duration=GIF_MS, loop=0, optimize=True)
        m[f"gif_{tag}_MB"] = round(os.path.getsize(path) / 1e6, 2)
    m["sheet"] = slug + ".png"
    return m, frame1x(d, info, 0), info


# ---------------------------------------------------------------- vanilla and siblings at 1x
def sheet_frame(path, w, h, idx=0, line=1, halve=False):
    im = Image.open(path).convert("RGBA")
    c, r = idx % line, idx // line
    im = im.crop((c * w, r * h, c * w + w, r * h + h))
    return scaled(im, 0.5) if halve else im


def ref_tile(layers, foot, label):
    """layers: (image at 1x, shift in tiles); drawn on a ground cell with the footprint."""
    fx, fy = foot
    cw, ch = int((fx + 3) * 64), int((fy + 2.5) * 64)
    org = (int((0.75 + fx / 2) * 64), int((1.75 + fy / 2) * 64))
    g = ground((cw, ch), org, 64, foot)
    for item in layers:
        im, (sx, sy) = item[0], item[1]
        at = (round(org[0] + sx * 64 - im.width / 2), round(org[1] + sy * 64 - im.height / 2))
        if len(item) > 2 and item[2] == "add":       # a glow layer: added, as the engine draws it
            box_ = (at[0], at[1], at[0] + im.width, at[1] + im.height)
            under = g.crop(box_).convert("RGB")
            lit = Image.composite(im.convert("RGB"), Image.new("RGB", im.size, 0), im.getchannel("A"))
            g.paste(ImageChops.add(under, lit).convert("RGBA"), box_[:2])
        else:
            g.alpha_composite(im, at)
    return g, label


def references():
    B = f"{FD}/base/graphics/entity"
    SA = f"{FD}/space-age/graphics/entity"
    out = []
    out.append(ref_tile([(sheet_frame(f"{B}/steam-engine/steam-engine-V-shadow.png", 330, 307, 0, 8), (40.5 / 32, 9.25 / 32)),
                         (sheet_frame(f"{B}/steam-engine/steam-engine-V.png", 225, 391, 0, 8), (4.75 / 32, -6.25 / 32))],
                        (3, 5), "vanilla steam engine 3x5 (0.9 MW)"))
    out.append(ref_tile([(sheet_frame(f"{B}/steam-turbine/steam-turbine-V-shadow.png", 302, 260, 0, 1), (39.5 / 32, 24.5 / 32)),
                         (sheet_frame(f"{B}/steam-turbine/steam-turbine-V.png", 217, 374, 0, 4), (4.75 / 32, 0.0))],
                        (3, 5), "vanilla steam turbine 3x5 (5.8 MW)"))
    G = f"{SA}/fusion-generator/north/fusion-generator-north"
    main = sheet_frame(G + ".png", 244, 376, 0, 3)
    glow = sheet_frame(G + "-glow.png", 202, 336, 0, 3)
    out.append(ref_tile([(sheet_frame(G + "-shadow.png", 248, 316, 0, 1), (12.5 / 32, 4 / 32)),
                         (main, (-2 / 32, -2 / 32)), (glow, (0, -4 / 32), "add")],
                        (3, 5), "SA fusion generator 3x5, working"))
    rp = Image.open(os.path.join(args.rp, "F-the-circulator-r5-idle.png")).convert("RGBA")
    rp1 = rp.resize((rp.width // 2, rp.height // 2), Image.LANCZOS)
    out.append((rp1, "Reaction Plant, round 5 (5x5, idle)"))
    CT = os.path.join(args.master, "graphics/entity/crust-turbine")
    out.append(ref_tile([(sheet_frame(f"{CT}/base-shadow-vertical.png", 192, 340), (0.01562, 0.17188)),
                         (sheet_frame(f"{CT}/base-vertical.png", 164, 360), (-0.23438, -0.20312)),
                         (sheet_frame(f"{CT}/rotor-vertical.png", 71, 64, 0, 8), (0.08594, -0.46875))],
                        (2, 4), "Siderane (crust) turbine, adopted"))
    return out


def contact(items, path, title):
    pad = 20
    hmax = max(im.height for im, _ in items)
    W = sum(im.width for im, _ in items) + pad * (len(items) + 1)
    sh = Image.new("RGBA", (W, hmax + 110), BG)
    d = ImageDraw.Draw(sh)
    d.text((pad, 14), title, font=F_H, fill=HEAD)
    x = pad
    for im, lab in items:
        sh.alpha_composite(im, (x, 50 + hmax - im.height))
        wrap(d, lab, (x, 58 + hmax), im.width, F_S, fill=TEXT)
        x += im.width + pad
    sh.convert("RGB").save(path, optimize=True)


if __name__ == "__main__":
    allm = {}
    mine = []
    for n, s in S.items():
        if not os.path.exists(os.path.join(args.root, f"f{n}", "working-00.png")):
            print("skip", n)
            continue
        m, f0, info = build(n, s)
        allm[n] = m
        mine.append((f0, f"{n}. {s['name'].title()} {s['foot']}, working"))
        print(n, m)
    json.dump(allm, open(os.path.join(HERE, "measures-b.json"), "w"), indent=1)
    refs = references()
    contact(refs + mine, os.path.join(HERE, "contact-sheet-b.png"),
            "RADIANT GENERATOR ROUND 5, SUGGESTIONS 6-10, at game scale (64 px a tile), beside vanilla and the "
            "Core's siblings")
