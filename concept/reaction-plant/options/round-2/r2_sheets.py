#!/usr/bin/env python3
"""Reaction Plant redesign, options round 2 (5x5): concept sheets, GIFs, contact sheet.

  python3 r2_sheets.py <hi-dir> <out-dir> [--factorio <data>]

<hi-dir> is r2_blockout.py's output (<hi-dir>/<E..I>/working-NN.png, idle.png,
mask.png, dir-*.png, all 4x). Writes into <out-dir>:

  <X>-<slug>.png          one concept sheet per option: working and idle at 2x on the
                          ground with the tile grid, the moving pixels at 1x, the four
                          rotations at game scale, a frame strip of the view port, the
                          pitch, the plan and the measurements
  <X>-<slug>-idle.png     the idle still at 2x on the ground
  <X>-<slug>-working.gif  the signature loop, 2x beside 1x, every frame, at the
                          proposed speed
  contact-sheet.png       the five options working at game scale (64 px a tile) beside
                          vanilla's oil refinery (5x5) and chemical plant and round 1's
                          A, frame 0, with shadows; contact-sheet-2x.png doubled
  measures.txt            per option: cover, rise, blue share, view port, motion share

Measurements, at 64 px a tile: "cover" is the share of the 5x5 footprint square
on screen covered by the machine's own mass (mask.png, rendered without the
ground's shadow catcher, alpha > 128); "rise" is how far the sprite's top stands
above the footprint's north edge; "blue" counts pixels the light adds (working
minus idle, a lift of more than 40 in blue, with blue standing 30 above red and green
so the green lamps do not count) over the machine's opaque pixels.
"""
import argparse
import os
import re

from PIL import Image, ImageChops, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("hi")
ap.add_argument("out")
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
args = ap.parse_args()
HI, OUT, FD = args.hi, args.out, args.factorio
HERE = os.path.dirname(os.path.abspath(__file__))
R1 = os.path.normpath(os.path.join(HERE, ".."))
os.makedirs(OUT, exist_ok=True)

PPT = 64
FOOT = 5
CANVAS, ORIGIN = (512, 448), (208, 272)
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT = (228, 222, 210)
SUB = (175, 168, 156)
HEAD = (240, 200, 120)
NF = 24
GIF_MS = 70          # 24 frames at ~14 fps: a 1.7 s loop
CROP1 = (24, 30, 440, 448)                         # 1x canvas: the building and its shadow
CROP2 = tuple(2 * v for v in CROP1)


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def load(opt, name, k):
    """A 4x render brought to k x game scale, premultiplied, faint catcher fog cut."""
    im = Image.open(f"{HI}/{opt}/{name}.png").convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    im = im.convert("RGBa").resize((im.width * k // 4, im.height * k // 4), Image.LANCZOS)
    return im.convert("RGBA")


def ground(size, origin, ppt, foot=FOOT, extent=8):
    g = Image.new("RGBA", size, GROUND)
    ov = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    ox, oy = origin
    off = 0.5 if foot % 2 else 0.0
    for i in range(-extent * 2, extent * 2 + 1):
        x = ox + (i + off) * ppt
        y = oy + (i + off) * ppt
        d.line([(x, 0), (x, size[1])], fill=(255, 255, 255, 26))
        d.line([(0, y), (size[0], y)], fill=(255, 255, 255, 26))
    h = foot * ppt / 2
    d.rectangle([ox - h, oy - h, ox + h, oy + h], outline=(255, 255, 255, 120))
    g.alpha_composite(ov)
    return g


def on_ground(im, k, foot=FOOT):
    g = ground(im.size, (ORIGIN[0] * k, ORIGIN[1] * k), PPT * k, foot)
    g.alpha_composite(im)
    return g


OPTS = {
    "E": dict(
        slug="the-bullseye-tower",
        title="E  THE BULLSEYE TOWER",
        layout="tall riveted tower back-left (r 0.88, 3.8 tall) with a gallery; gas conditioner back-right; "
               "reaction drum down the east flank; exchanger, manifold and decks of pump, cell box, cabinet in front",
        pitch=[
            "Read: one tall riveted precipitation tower in the back-left corner with a railed gallery round its head,",
            "and three bolted bullseye portholes climbing its south-west face in a stair, each a blue vortex -- the",
            "refinery's tall-tower-and-low-plant on a 5x5, the tower standing inside the grid. Fluids in: the two",
            "input stubs feed the lagged mains on the west and north edges into the tower's foot (solution) and the",
            "conditioner back-right, whose fat hose arches to the tower's crown (crust gas). Solid out: the cells",
            "drop into the lead-lined cell box at the front. View port: three portholes 0.7 across, framed and",
            "barred, each turning a three-armed vortex, phased so the three don't turn in step. Finish: kamacite",
            "plate, lead bands with lugs, teal on motors, hatches and a rack, rust-brown and black hoses.",
            "Risk: the portholes face south-west on a round wall, so they foreshorten to ellipses; the tower's",
            "big head is the largest single surface on the sprite.",
        ],
        hoses="6 hoses 0.15-0.22 thick (conditioner->crown, drum->middle porthole, pump->foot, cell box->foot, "
              "receiver->drum, a black loop to the exchanger), 3 lagged mains, a copper header",
        blue="three portholes only, stacked up the tower",
        wording="Radiant light | #1F63FF -> #73ADFF | the solution itself, seen through the tower's three "
                "bullseye portholes and nowhere else. Lit only while crafting; idle, a still dark navy.",
        anim=[
            "fluid (working_visualisation, one sheet per porthole or one sheet of three): 24 f, a three-armed",
            "  vortex turning one arm a loop, seamless; the bars and frames are holdouts. Loop ~1.7 s",
            "pump coupling on the front skid: 12 f, six-fold, 60 deg a loop",
            "glow: the portholes, differenced; status lamps engine-tinted. Idle: frame 0, light off",
            "recipe tint: none now (one recipe); the fluid sheet can take apply_recipe_tint 'primary' later",
        ],
        generator="Lends the bolted bullseye porthole on a riveted drum: the generator could show its emitter "
                  "through one big porthole of the same frame.",
    ),
    "F": dict(
        slug="the-circulator",
        title="F  THE CIRCULATOR",
        layout="reactor vessel back-right (r 0.85, 3.5 tall) with agitator; two fat glass legs (r 0.27, 2 tall) off its "
               "west side; scrubber pair back-left; feed drum west; filter press, pump, cabinets in front",
        pitch=[
            "Read: a tall reactor vessel in the back-right with two fat strapped glass legs standing off its west",
            "side -- a riser, where the blue climbs with bright bubbles, and a downcomer, where it falls back with",
            "dark flecks of precipitate. Hoses close the loop at the top into the reactor's shoulder, a cast",
            "header closes it at the foot: a thermosiphon you watch go round. Fluids in: solution from the feed",
            "drum into the riser's foot; crust gas from the scrubber pair back-left over a high arching hose into",
            "the reactor head. Solid out: the filter press front-left, leaves of lead and plate. View port: the two",
            "legs, 2 tiles tall in all, side by side. Finish as E; teal on the agitator motor and racks.",
            "Risk: the legs stand mid-plate, half in front of the reactor; from the north they hide the low run.",
        ],
        hoses="7 hoses 0.17-0.24 thick (riser->reactor, downcomer->reactor, scrubber->reactor head, scrubber->riser cap, "
              "drum->riser foot, pump->downcomer, press->downcomer), 4 lagged mains, cast headers",
        blue="the two glass legs: up one, down the other",
        wording="Radiant light | #1F63FF -> #73ADFF | the solution itself, seen in the circulator's two glass "
                "legs and nowhere else. Lit only while crafting; idle, the legs hold a still dark navy.",
        anim=[
            "fluid (in the legs): 24 f, bands rising two wavelengths a loop in the riser, falling in the",
            "  downcomer; bubbles up the riser, flecks down the downcomer, each wrapping. Loop ~1.7 s",
            "agitator coupling on the reactor head: 12 f, 60 deg; pump coupling: 12 f",
            "glow: the legs, differenced; status lamps. Idle: frame 0, light off",
            "recipe tint: as E",
        ],
        generator="Lends the paired glass legs and the loop you can see go round: the generator's coolant or "
                  "solution circuit drawn as the same strapped legs.",
    ),
    "G": dict(
        slug="the-belted-sphere",
        title="G  THE BELTED SPHERE",
        layout="reaction sphere (r 1.05) on six braced legs west of centre, a glass belt at its equator, agitator on "
               "its crown; vent stack back-right (r 0.44, 3.2 tall); receivers, drum and a front of pump, cell box, valves",
        pitch=[
            "Read: a big riveted reaction sphere on six braced legs, west of centre, cut at its equator by a",
            "strapped glass belt where the blue solution is spun round by the agitator on its crown; a tall slim",
            "vent stack in the back-right corner, receivers and a drum down the east side. Fluids in: crust gas",
            "from the stack's head over a fat hose into the sphere's crown; solution from the drum into the belt's",
            "lower flange and from the pump into the sump under the sphere. Solid out: the sump drains to the cell",
            "box in front. View port: the belt, 0.42 deep and all the way round -- streaks and dark flecks circling.",
            "Finish as E. Risk: the sphere is the largest smooth form of the five; it is on legs and cut by the",
            "belt, but it is still the closest to round 1's 'dome' (B).",
        ],
        hoses="5 hoses 0.17-0.22 thick (stack->crown, receiver->belt flange, drum->belt, pump->sump, tank->stack), "
              "4 lagged mains, a cast sump drain, a copper header",
        blue="the equator belt only: one lit band round the sphere",
        wording="Radiant light | #1F63FF -> #73ADFF | the solution itself, seen through the sphere's strapped glass "
                "belt and nowhere else. Lit only while crafting; idle, the belt holds a still dark navy.",
        anim=[
            "fluid (in the belt): 24 f, nine streaks circling one streak's width a loop, flecks circling with",
            "  them; the belt's straps are holdouts. Loop ~1.7 s",
            "agitator coupling on the crown: 12 f, 60 deg; pump coupling: 12 f",
            "glow: the belt, differenced; status lamp. Idle: frame 0, light off",
            "recipe tint: as E",
        ],
        generator="Lends the lit equator belt: the generator as a sphere or drum with the same glowing band, "
                  "the reactor a ring of them.",
    ),
    "H": dict(
        slug="the-glass-coil",
        title="H  THE GLASS COIL",
        layout="core column back-left (r 0.5, 3.95 tall) wound with a fat glass coil (3.25 turns, r 0.86, tube 0.31); "
               "gas drum on saddles down the east; receiver north; exchanger, manifold, cell box, cabinet in front",
        pitch=[
            "Read: a tall core column in the back-left with a fat glass coil wound three and a quarter times round",
            "it, the blue solution climbing the coil with bright bubbles spiralling up; a long gas drum on saddles",
            "down the east side. Fluids in: solution from the front-left pump into the coil's foot; crust gas from",
            "the drum and the receiver over fat hoses into the column's crown. The coil comes off the top into the",
            "crown. Solid out: the cell box at the front. View port: the coil, ~17 tiles of glass tube in a 2-tile",
            "helix -- the most glass and the strongest silhouette of the five. Finish as E; lead clamps on the coil.",
            "Risk: the most blue of the five (see measures), and the coil's back half reads through the glass.",
        ],
        hoses="5 hoses 0.17-0.22 thick (pump->coil foot, coil top->crown, drum->crown, receiver->column, "
              "cell box->column), 4 lagged mains, a copper header",
        blue="the coil: the most of the five, wound round one column",
        wording="Radiant light | #1F63FF -> #73ADFF | the solution itself, seen in the glass coil round the core "
                "column and nowhere else. Lit only while crafting; idle, the coil holds a still dark navy.",
        anim=[
            "fluid (in the coil): 24 f, bands rising three wavelengths a loop, so the light climbs the coil;",
            "  46 bubbles each riding the whole coil once a loop; the clamps are holdouts. Loop ~1.7 s",
            "pump coupling: 12 f, 60 deg",
            "glow: the coil, differenced; status lamp. Idle: frame 0, light off",
            "recipe tint: as E",
        ],
        generator="Lends the glass coil: the generator's emitter wound in the same coil, the light climbing it "
                  "as power rises.",
    ),
    "I": dict(
        slug="the-window-tank",
        title="I  THE WINDOW TANK",
        layout="long low settling tank across the front (3.1 x 1.4, 1.3 tall) with a 2.5-wide three-pane window in its "
               "south face; reactor tower back-right (r 0.75, 3.45 tall); scrubber and pots back-left; pump east",
        pitch=[
            "Read: a long low settling tank across the front with a big framed window in its south face -- three",
            "panes where the blue solution sloshes, precipitate drifting down to a dark bed and bubbles rising --",
            "and a tall reactor tower in the back-right corner dropping fat hoses into the tank's lid; a scrubber",
            "back-left. Round 1's C gave the plate a front; this gives the 5x5 one, at ground level, in front.",
            "Fluids in: crust gas through the scrubber to the tower head; solution from the east pump into the",
            "tank's end; the tower's hoses bring the reacted solution down into the lid. Solid out: the bed under",
            "the window, drawn off to the front decks. View port: the window, 2.5 x 0.9, always on the south face.",
            "Risk: the tank's lid is a broad flat top -- the 'plate' read -- carried by the agitator and hoses on it.",
        ],
        hoses="5 hoses 0.16-0.24 thick (tower->lid x2, scrubber->tower head, pump->tank end, pot->pot), "
              "3 lagged mains, a copper return",
        blue="the window only: three panes in the tank's south face",
        wording="Radiant light | #1F63FF -> #73ADFF | the solution itself, seen through the settling tank's "
                "three-pane window and nowhere else. Lit only while crafting; idle, a still dark navy.",
        anim=[
            "fluid (in the window): 24 f, the surface riding 1.5 waves travelling across the panes, bands in the",
            "  body; dark flecks drifting down, bubbles rising, each wrapping; mullions are holdouts. Loop ~1.7 s",
            "agitator coupling on the lid: 12 f, 60 deg; pump coupling: 12 f",
            "glow: the window, differenced; status lamps. Idle: frame 0, light off",
            "recipe tint: as E",
        ],
        generator="Lends the framed window onto the solution: the generator seen through the same three-pane "
                  "frame, a slab of light behind glass.",
    ),
}


def measure(opt):
    w = load(opt, "working-00", 1)
    idle = load(opt, "idle", 1)
    mask = load(opt, "mask", 1).getchannel("A").point(lambda v: 255 if v > 128 else 0)
    cnt = lambda im: sum(1 for v in im.get_flattened_data() if v)
    ox, oy = ORIGIN
    h = FOOT * PPT // 2
    cover = cnt(mask.crop((ox - h, oy - h, ox + h, oy + h))) / (2 * h) ** 2
    bb = mask.getbbox()
    rise = (oy - h - bb[1]) / PPT
    opaque = cnt(mask)
    lift = ImageChops.subtract(w.getchannel("B"), idle.getchannel("B")).point(lambda v: 255 if v > 40 else 0)
    lift = ImageChops.multiply(lift, mask)
    # the radiant blue only, not the green status lamps' spill: blue well above green and red
    hue = ImageChops.subtract(w.getchannel("B"), ImageChops.lighter(w.getchannel("R"), w.getchannel("G")))
    lift = ImageChops.multiply(lift, hue.point(lambda v: 255 if v > 30 else 0))
    blue = cnt(lift)
    acc = Image.new("L", w.size, 0)
    for f in range(1, NF):
        d = ImageChops.difference(w, load(opt, f"working-{f:02d}", 1)).convert("L")
        acc = ImageChops.lighter(acc, d.point(lambda v: 255 if v > 10 else 0))
    moving = cnt(ImageChops.multiply(acc, mask))
    lb = lift.getbbox()
    return {
        "footprint covered by mass": f"{cover * 100:.1f} %  (vanilla refinery 92-94 %; round 1 81-85 %)",
        "rises above footprint north edge": f"{rise:.2f} tiles  (vanilla refinery 0.97)",
        "sprite bbox (mass)": f"{(bb[2] - bb[0]) / PPT:.2f} wide x {(bb[3] - bb[1]) / PPT:.2f} tall tiles",
        "blue (lit) pixels / opaque": f"{blue / opaque * 100:.1f} %  (vanilla fluid: chem 3.2 %, refinery 2.0 %; "
                                      "round 1 A 6.2 %)",
        "blue area bbox": f"{(lb[2] - lb[0]) / PPT:.2f} x {(lb[3] - lb[1]) / PPT:.2f} tiles" if lb else "none",
        "moving pixels / opaque": f"{moving / opaque * 100:.1f} %  (vanilla: chem 5.2 %, refinery 15.9 %)",
    }, acc


MEASURES = {}


def sheet(opt):
    o = OPTS[opt]
    m, mov = measure(opt)
    MEASURES[opt] = m
    work = on_ground(load(opt, "working-00", 2), 2).crop(CROP2)
    idle = on_ground(load(opt, "idle", 2), 2).crop(CROP2)
    idle.convert("RGB").save(f"{OUT}/{opt}-{o['slug']}-idle.png")
    W = work.width * 2 + 16 + 40 + 2 * 330 + 30
    H = 3000
    s = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(s)
    d.text((20, 14), o["title"], font=font(30, True), fill=TEXT)
    d.text((20, 54), "Reaction Plant redesign, options round 2 at 5x5 -- lit Blender blockout (Claude in Chrome had no "
           "browser connected, so no ChatGPT concept). One plate under rotation.", font=font(15), fill=SUB)
    d.text((20, 74), "Layout: " + o["layout"], font=font(14), fill=TEXT)
    y = 104
    d.text((20, y), "WORKING, 2x (frame 0; north-facing stubs as stand-ins)", font=font(15, True), fill=HEAD)
    d.text((20 + work.width + 16, y), "IDLE, 2x (light off, stopped)", font=font(15, True), fill=HEAD)
    s.alpha_composite(work, (20, y + 22))
    s.alpha_composite(idle, (20 + work.width + 16, y + 22))
    x3 = 20 + 2 * work.width + 40
    w1 = on_ground(load(opt, "working-00", 1), 1)
    tint = Image.new("RGBA", w1.size, (255, 0, 200, 0))
    tint.putalpha(mov.point(lambda v: int(v * 0.75)))
    w1.alpha_composite(tint)
    w1 = w1.crop(CROP1)
    d.text((x3, y), "1x, MOVING PIXELS IN MAGENTA", font=font(15, True), fill=HEAD)
    s.alpha_composite(w1, (x3, y + 22))
    yd = y + 22 + w1.height + 24
    d.text((x3, yd), "THE ONE PLATE UNDER ROTATION, 1x", font=font(15, True), fill=HEAD)
    d.text((x3, yd + 20), "inputs at -1 and +1 on the faced side, the dormant output at 0 opposite (a cover)",
           font=font(12), fill=SUB)
    for i, dd in enumerate("NESW"):
        im = on_ground(load(opt, f"dir-{dd}", 1), 1).crop((CROP1[0], CROP1[1] + 30, CROP1[2] - 60, CROP1[3]))
        im = im.resize((im.width * 3 // 4, im.height * 3 // 4), Image.LANCZOS)
        px, py = x3 + (i % 2) * (im.width + 8), yd + 40 + (i // 2) * (im.height + 8)
        s.alpha_composite(im, (px, py))
        d.text((px + 4, py + 2), f"facing {dd}", font=font(12), fill=TEXT)
    ydir_end = yd + 40 + 2 * (im.height + 8)
    # the view port's frame strip at 2x
    ys = y + 22 + work.height + 22
    w2 = load(opt, "working-00", 2)
    sat = ImageChops.subtract(w2.getchannel("B"), w2.getchannel("R")).point(lambda v: 255 if v > 110 else 0)
    bb = ImageChops.multiply(sat, w2.getchannel("A").point(lambda v: 255 if v > 200 else 0)).getbbox()
    pad = 16
    bb = (bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad)
    scale = min(1.0, ((x3 - 40) / 6 - 6) / (bb[2] - bb[0]), 300 / (bb[3] - bb[1]))
    d.text((20, ys), "THE VIEW PORT, 2x: frames 0, 4, 8, 12, 16, 20 of the 24-frame loop", font=font(15, True),
           fill=HEAD)
    xx = 20
    for f in range(0, NF, 4):
        fr = on_ground(load(opt, f"working-{f:02d}", 2), 2).crop(bb)
        if scale < 1:
            fr = fr.resize((int(fr.width * scale), int(fr.height * scale)), Image.LANCZOS)
        s.alpha_composite(fr, (xx, ys + 22))
        xx += fr.width + 6
    yt = max(ys + 22 + int((bb[3] - bb[1]) * scale) + 24, 0)
    col = 20
    d.text((col, yt), "PITCH", font=font(16, True), fill=HEAD)
    yy = yt + 24
    for ln in o["pitch"]:
        d.text((col, yy), ln, font=font(14), fill=TEXT)
        yy += 19
    yy += 8
    for k, v in (("Hoses", o["hoses"]), ("Blue", o["blue"]), ("Generator", o["generator"])):
        d.text((col, yy), f"{k}:", font=font(14, True), fill=HEAD)
        d.text((col + 95, yy), v, font=font(13), fill=TEXT)
        yy += 22
    yy += 6
    d.text((col, yy), "THE SPEC 3.3 ROW IT WOULD NEED (replaces 'the three sight slots only'; wording to agree "
           "with Liam)", font=font(14, True), fill=HEAD)
    yy += 21
    d.text((col + 10, yy), o["wording"], font=font(13), fill=TEXT)
    yy += 28
    d.text((col, yy), "ANIMATION PLAN (spec 6.2)", font=font(14, True), fill=HEAD)
    yy += 21
    for ln in o["anim"]:
        d.text((col + 10, yy), ln, font=font(13), fill=TEXT)
        yy += 18
    yy += 8
    d.text((col, yy), "MEASURED (64 px a tile; cover from the mass alone, no ground shadow)", font=font(14, True),
           fill=HEAD)
    yy += 21
    for k, v in m.items():
        d.text((col + 10, yy), f"{k}: {v}", font=font(13), fill=TEXT)
        yy += 18
    s = s.crop((0, 0, W, max(yy + 20, ydir_end + 10)))
    path = f"{OUT}/{opt}-{o['slug']}.png"
    s.convert("RGB").save(path)
    print(path, s.size)


def gif(opt):
    o = OPTS[opt]
    frames = []
    for f in range(NF):
        g2 = on_ground(load(opt, f"working-{f:02d}", 2), 2).crop(CROP2)
        g1 = on_ground(load(opt, f"working-{f:02d}", 1), 1).crop(CROP1)
        im = Image.new("RGBA", (g2.width + g1.width + 12, g2.height), BG)
        im.alpha_composite(g2, (0, 0))
        im.alpha_composite(g1, (g2.width + 12, 0))
        frames.append(im.convert("RGB"))
    strip = Image.new("RGB", (frames[0].width, frames[0].height * NF))
    for i, f in enumerate(frames):
        strip.paste(f, (0, i * f.height))
    pal = strip.quantize(colors=256)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    path = f"{OUT}/{opt}-{o['slug']}-working.gif"
    q[0].save(path, save_all=True, append_images=q[1:], duration=GIF_MS, loop=0, optimize=True)
    print(path, f"{os.path.getsize(path) / 1e6:.1f} MB")


# ------------------------------------------------------------- contact sheet
ENT = f"{FD}/base/graphics/entity"


def sidecar(stem):
    t = open(stem + ".lua").read()
    w = int(re.search(r"width\s*=\s*(\d+)", t).group(1))
    h = int(re.search(r"height\s*=\s*(\d+)", t).group(1))
    sx, sy = map(float, re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", t).groups())
    return w, h, sx, sy


def paste(canvas, im, origin, shift_px):
    x = round(origin[0] + shift_px[0] - im.width / 2)
    y = round(origin[1] + shift_px[1] - im.height / 2)
    canvas.alpha_composite(im, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))


def shadow_img(im):
    a = im.getchannel("A").point(lambda v: v // 2)
    s = Image.new("RGBA", im.size, (0, 0, 0, 0))
    s.putalpha(a)
    return s


def vanilla_chem(panel, origin):
    p = f"{ENT}/chemical-plant/chemical-plant-north"
    sh = Image.open(f"{ENT}/chemical-plant/chemical-plant-shadow.png").convert("RGBA").crop((0, 0, 312, 222))
    paste(panel, shadow_img(sh), origin, (54, 12))
    for stem in ("-base", "-anim-1", "-anim-2"):
        w, h, sx, sy = sidecar(p + stem)
        im = Image.open(p + stem + ".png").convert("RGBA").crop((0, 0, w, h))
        paste(panel, im, origin, (2 * sx, 2 * sy - 18))
    liq = Image.open(f"{ENT}/chemical-plant/chemical-plant-liquid-north.png").convert("RGBA").crop((0, 0, 66, 44))
    r, g, b, a = liq.split()
    liq = Image.merge("RGBA", (r, g.point(lambda v: v * 244 // 255), b.point(lambda v: 0), a))
    paste(panel, liq, origin, (46, 30))


def vanilla_refinery(panel, origin):
    p = f"{ENT}/oil-refinery/north/oil-refinery"
    w, h, sx, sy = sidecar(f"{p}-shadow-north")
    paste(panel, shadow_img(Image.open(f"{p}-shadow-north.png").convert("RGBA").crop((0, 0, w, h))), origin,
          (2 * sx, 2 * sy))
    stems = ["-north"] + [f"-anim-north-{i}" for i in range(1, 7)] + [f"-fluid-north-{i}" for i in range(1, 7)]
    for st in stems:
        w, h, sx, sy = sidecar(p + st)
        im = Image.open(p + st + ".png").convert("RGBA").crop((0, 0, w, h))
        if "fluid" in st:
            tv = (253, 115, 15)
            ch = [c.point(lambda v, t=t: int(2 * v * t / 255) if v < 128 else int(255 - 2 * (255 - v) * (255 - t) / 255))
                  for c, t in zip(im.split()[:3], tv)]
            im = Image.merge("RGBA", (*ch, im.getchannel("A")))
        paste(panel, im, origin, (2 * sx, 2 * sy))


def contact():
    PH = 8 * PPT
    panels = []

    def panel(w_tiles, foot, label, draw):
        size = (w_tiles * PPT, PH)
        origin = (size[0] // 2 - (PPT // 2 if foot == 5 else 0), PH - int((foot / 2 + 1.0) * PPT))
        g = ground(size, origin, PPT, foot)
        draw(g, origin)
        panels.append((label, g))

    panel(8, 5, "vanilla oil refinery, 5x5", vanilla_refinery)
    panel(5, 3, "vanilla chemical plant, 3x3", vanilla_chem)
    # round 1's A, its panel lifted whole from round 1's contact sheet (same scale, same grid)
    r1 = Image.open(f"{R1}/contact-sheet.png").convert("RGBA").crop((1184, 82, 1504, 530))
    g = Image.new("RGBA", (5 * PPT, PH), GROUND)
    g.alpha_composite(r1, (0, PH - r1.height))
    panels.append(("round 1: A the sight column, 3x3", g))
    for opt in OPTS:
        def draw(g, origin, opt=opt):
            im = load(opt, "working-00", 1)
            paste(g, im, origin, (CANVAS[0] / 2 - ORIGIN[0], CANVAS[1] / 2 - ORIGIN[1]))
        panel(8, 5, OPTS[opt]["title"].replace("  ", " ") + ", 5x5", draw)
    W = sum(p.width for _, p in panels) + 8 * (len(panels) + 1)
    sheet = Image.new("RGBA", (W, PH + 100), BG)
    d = ImageDraw.Draw(sheet)
    d.text((10, 8), "REACTION PLANT REDESIGN, ROUND 2 AT 5x5 -- OPTIONS AT GAME SCALE", font=font(20, True),
           fill=TEXT)
    d.text((10, 36), "64 px a tile; frame 0 working, with shadows. Vanilla composited from its own layers "
           "(refinery tinted for advanced oil processing, chemical plant for sulfuric acid). Options are lit "
           "Blender blockouts; round 1's A is lifted from round 1's contact sheet.", font=font(12), fill=SUB)
    x = 8
    for label, p in panels:
        d.text((x + 2, 62), label, font=font(12), fill=TEXT)
        sheet.alpha_composite(p, (x, 82))
        x += p.width + 8
    sheet = sheet.crop((0, 0, W, PH + 90))
    sheet.convert("RGB").save(f"{OUT}/contact-sheet.png")
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).convert("RGB").save(
        f"{OUT}/contact-sheet-2x.png")
    print(f"{OUT}/contact-sheet.png", sheet.size)


for opt in OPTS:
    sheet(opt)
    gif(opt)
contact()
with open(f"{OUT}/measures.txt", "w") as fh:
    for opt, m in MEASURES.items():
        fh.write(OPTS[opt]["title"] + "\n" + "".join(f"  {k}: {v}\n" for k, v in m.items()))
print(open(f"{OUT}/measures.txt").read())
