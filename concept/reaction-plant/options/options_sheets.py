#!/usr/bin/env python3
"""Reaction Plant redesign, options round: concept sheets, GIFs, contact sheet.

  python3 options_sheets.py <hi-dir> <out-dir> [--factorio <data>]

<hi-dir> is options_blockout.py's output (<hi-dir>/<A..D>/working-NN.png,
idle.png, dir-*.png, all 4x). Writes into <out-dir>:

  <X>-<slug>.png          one concept sheet per option: working and idle at 2x on
                          the ground with the tile grid, the four rotations at game
                          scale, a frame strip of the view port, the pitch and the
                          plan, and its measurements
  <X>-<slug>-working.gif  the signature loop at 2x, every frame, at the proposed
                          game speed
  contact-sheet.png       every option working at game scale (64 px a tile) beside
                          vanilla's chemical plant and oil refinery and the current
                          Reaction Plant, all frame 0, with shadows
  contact-sheet-2x.png    the same, doubled (nearest neighbour)
  measures.txt            per option: footprint cover, rise, blue share, motion share

Measurements (sprite px, 64 a tile; the same as reference_sheet.py takes off
vanilla): "blue" counts pixels the light adds (working minus idle, a lift of
more than 40 in blue) over the sprite's opaque pixels.
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
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
os.makedirs(OUT, exist_ok=True)

PPT = 64
CANVAS, ORIGIN = (352, 384), (160, 240)
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT = (228, 222, 210)
SUB = (175, 168, 156)
HEAD = (240, 200, 120)
NF = 24
GIF_MS = 70          # 24 frames at ~14 fps: a 1.7 s loop, the proposed fluid loop


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def load(opt, name, k):
    """A 4x render brought to k x game scale, premultiplied, faint catcher fog cut."""
    im = Image.open(f"{HI}/{opt}/{name}.png").convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    im = im.convert("RGBa").resize((im.width * k // 4, im.height * k // 4), Image.LANCZOS)
    return im.convert("RGBA")


def ground(size, origin, ppt, foot=3, extent=6):
    g = Image.new("RGBA", size, GROUND)
    ov = Image.new("RGBA", size, (0, 0, 0, 0))       # lines blended over the ground, not written into its alpha
    d = ImageDraw.Draw(ov)
    ox, oy = origin
    for i in range(-extent * 2, extent * 2 + 1):
        x = ox + (i + 0.5) * ppt
        y = oy + (i + 0.5) * ppt
        d.line([(x, 0), (x, size[1])], fill=(255, 255, 255, 26))
        d.line([(0, y), (size[0], y)], fill=(255, 255, 255, 26))
    h = foot * ppt / 2
    d.rectangle([ox - h, oy - h, ox + h, oy + h], outline=(255, 255, 255, 120))
    g.alpha_composite(ov)
    return g


def on_ground(im, k, foot=3, origin=None):
    o = origin or (ORIGIN[0] * k, ORIGIN[1] * k)
    g = ground(im.size, o, PPT * k, foot)
    g.alpha_composite(im)
    return g


OPTS = {
    "A": dict(
        slug="the-sight-column",
        title="A  THE SIGHT COLUMN",
        pitch=[
            "Read: a tall banded precipitation column standing in one corner, its middle a strapped glass barrel lit",
            "blue from inside, with a low run of plant round the opposite corner -- the refinery's tall-tower-and-low-",
            "plant arrangement on a 3x3 diagonal. Fluids in: the two input stubs feed a lagged main along the edge and",
            "a copper valve manifold, which a pump lifts into the column's foot (solution) and the conditioning drum",
            "returns to its head (crust gas). Solid out: the cells drop into the lead-lined cell box at the front corner;",
            "no chute (spec 8). View port: the glass barrel, 1.1 tall x 1.3 round, eight straps -- the solution swirls",
            "and bubbles rise through it. Finish: kamacite plate, lead bands with bolted lugs, teal on the motor, the",
            "manway and the hatch only, rust-brown and black hoses with brass nuts.",
        ],
        hoses="4 hoses 0.15-0.19 tiles thick (pump->foot, drum->barrel flange, drum->head, cell box->foot), "
              "2 lagged mains (back and right edges, 0.18-0.22 thick), a copper header",
        blue="the barrel only: one strapped band on the column",
        wording="Radiant light | #1F63FF -> #73ADFF | the solution itself, seen through the column's strapped "
                "glass barrel and nowhere else. Lit only while crafting; idle, the barrel shows a still, dark navy liquid.",
        anim=[
            "fluid (working_visualisation, in the barrel): 32 f, bands rise one wavelength a loop + bubbles that wrap;",
            "  rendered with the straps as holdouts so they stay in front. Loop ~1.8 s (animation_speed 0.3)",
            "pump coupling: 12 f, six-fold, 60 deg a loop, drawn free (gap all round) on the skid",
            "glow: the barrel's light, differenced; status lamp engine-tinted. Idle: frame 0, light off",
            "recipe tint: none now (one recipe); the fluid sheet can take apply_recipe_tint 'primary' for stage 3",
        ],
        generator="Lends the generator the strapped glass barrel in a lead-banded column: the emitter seen as a lit "
                  "column of solution; the reactor = several columns round a core.",
    ),
    "B": dict(
        slug="the-kettle-and-scrubber",
        title="B  THE KETTLE AND SCRUBBER",
        pitch=[
            "Read: a big squat reaction kettle over most of one half, with a round porthole in a raised well on its lid,",
            "and a tall slim gas scrubber in the opposite corner; two fat hoses arch from the scrubber down into the",
            "lid. Fluids in: solution by the pump skid into the kettle's flank, crust gas up through the scrubber and",
            "down the hoses. Solid out: a cell filter press in the far corner, plates of lead and plate. View port: a",
            "0.9-wide porthole looking down into the kettle, where the solution turns in a three-armed vortex with",
            "bright flecks circling -- the camera looks straight into it. Finish as A; teal on the agitator motor.",
            "Risk: the kettle is a big round lid with a round window on it -- the nearest of the four to 'a plate",
            "with a dome on top', which the scrubber and the hoses have to break up.",
        ],
        hoses="4 hoses 0.15-0.2 thick (scrubber->lid x2, pump->kettle flank, receiver->scrubber), 1 lagged main, "
              "2 copper runs",
        blue="the porthole only: one round window, seen from above",
        wording="Radiant light | #1F63FF -> #73ADFF | the solution itself, seen through the round porthole in the "
                "kettle lid and nowhere else. Lit only while crafting; idle, a still, dark navy surface.",
        anim=[
            "fluid (in the porthole): 24 f, a three-armed vortex turning a third of a turn a loop (seamless), flecks",
            "  circling; under the glass's bar, which is a holdout. Loop ~1.3 s",
            "agitator coupling on the lid: 12 f, 60 deg; pump coupling on the skid: 12 f",
            "glow: the porthole, differenced; status lamp. Idle: frame 0, light off",
            "recipe tint: as A",
        ],
        generator="Lends the porthole: the generator looks down into its emitter through a bolted round window; "
                  "the reactor = a ring of them.",
    ),
    "C": dict(
        slug="the-settling-tube",
        title="C  THE SETTLING TUBE",
        pitch=[
            "Read: a long horizontal glass settling tube across one side, cradled and hooped in lead, with a tall",
            "reactor tower in the corner behind it and a mid-height gas conditioner in the other, bridged by a lagged",
            "crossover high up -- the refinery's skyline of unequal vessels. Fluids in: the tower and the conditioner",
            "each drop a fat hose into one end of the tube. Solid out: the precipitate settles out of the tube's belly",
            "into a lead-lined drop box with a rotary feeder in the middle. View port: five glass segments, 2.2 tiles",
            "long in all, where the blue runs along the tube and dark flecks of precipitate drift down and settle.",
            "Risk: the tube lies along one edge, so with the plant facing that way the input stubs land in front of",
            "its cradles -- the 'run of pipework at one edge' spec 5 warns against; it is body, not a port.",
        ],
        hoses="2 hoses 0.18-0.19 thick (tower->tube end, conditioner->tube end), a lagged crossover 0.24 thick "
              "high between the vessels, a lagged main on the right edge, a copper return",
        blue="the tube's five glass segments: the most blue of the four",
        wording="Radiant light | #1F63FF -> #73ADFF | the solution itself, seen through the settling tube's glass "
                "segments between its lead hoops and nowhere else. Lit only while crafting; idle, a still dark tube.",
        anim=[
            "fluid (in the tube): 32 f, streaks travelling two wavelengths along the tube a loop, flecks drifting",
            "  and settling; the hoops are holdouts. Loop ~1.8 s",
            "rotary feeder coupling on the drop box: 12 f, 60 deg",
            "glow: the tube, differenced; status lamp. Idle: frame 0, light off",
            "recipe tint: as A",
        ],
        generator="Lends the hooped glass tube: the same language as the generator's round-1 trough (A), so the two "
                  "would read as one plant split in two.",
    ),
    "D": dict(
        slug="the-cascade",
        title="D  THE CASCADE",
        pitch=[
            "Read: three vessels stepping down the diagonal -- a tall reactor in one corner, a mid settler in the",
            "middle, a low cell pot in the opposite corner -- joined by two strapped glass transfer pipes, so the",
            "blue runs downhill across the building. The other two corners hold a gas receiver with its feed pump,",
            "and a lead-lined cell box. Fluids in: gas from the receiver up a fat hose into the reactor's head;",
            "solution by the lagged mains into its foot. Solid out: the cell pot and the cell box. View port: the two",
            "glass runs (each 0.24 thick, ~1 tile long) and a gauge glass up the front of each vessel. The light",
            "moves: it flows from vessel to vessel, as the fusion generator's plasma runs its channels.",
        ],
        hoses="4 hoses 0.15-0.19 thick (receiver->reactor head, pump->settler, receiver->cell pot, box->settler), "
              "2 lagged mains, a copper return",
        blue="two glass transfer runs and three gauge glasses: thin lines, the least area",
        wording="Radiant light | #1F63FF -> #73ADFF | the solution itself, seen in the two glass transfer pipes "
                "between the vessels and the three gauge glasses, and nowhere else. Lit only while crafting.",
        anim=[
            "fluid (in the runs): 32 f, streaks flowing downhill two wavelengths a loop; gauge glasses: the",
            "  same sheet, slow rising bands. The runs' straps and collars are holdouts. Loop ~1.8 s",
            "feed pump coupling: 12 f, 60 deg",
            "glow: runs and gauges, differenced; status lamp. Idle: frame 0, light off",
            "recipe tint: as A",
        ],
        generator="Lends the flowing light: radiant light running along glass channels from the source to its "
                  "users -- the generator's collectors, the reactor's neighbour links.",
    ),
}


def measure(opt):
    w = load(opt, "working-00", 1)
    idle = load(opt, "idle", 1)
    a = w.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    ox, oy = ORIGIN
    fp = a.crop((ox - 96, oy - 96, ox + 96, oy + 96))
    cover = sum(1 for v in fp.get_flattened_data() if v) / (192 * 192)
    bb = a.getbbox()
    rise = (oy - 96 - bb[1]) / PPT
    opaque = sum(1 for v in a.get_flattened_data() if v)
    lift = ImageChops.subtract(w.getchannel("B"), idle.getchannel("B")).point(lambda v: 255 if v > 40 else 0)
    lift = ImageChops.multiply(lift, a)
    blue = sum(1 for v in lift.get_flattened_data() if v)
    f0 = w
    acc = Image.new("L", w.size, 0)
    for f in range(1, NF):
        d = ImageChops.difference(f0, load(opt, f"working-{f:02d}", 1)).convert("L")
        acc = ImageChops.lighter(acc, d.point(lambda v: 255 if v > 10 else 0))
    moving = sum(1 for v in ImageChops.multiply(acc, a).get_flattened_data() if v)
    lb = lift.getbbox()
    return {
        "footprint covered by mass": f"{cover * 100:.0f} %  (vanilla 92-94 %)",
        "rises above footprint top edge": f"{rise:.2f} tiles  (vanilla 0.97-1.05)",
        "sprite bbox": f"{(bb[2] - bb[0]) / PPT:.2f} wide x {(bb[3] - bb[1]) / PPT:.2f} tall tiles",
        "blue (lit) pixels / opaque": f"{blue / opaque * 100:.1f} %  (vanilla fluid: chem 3.2 %, refinery 2.0 %)",
        "blue area bbox": f"{(lb[2] - lb[0]) / PPT:.2f} x {(lb[3] - lb[1]) / PPT:.2f} tiles" if lb else "none",
        "moving pixels / opaque": f"{moving / opaque * 100:.1f} %  (vanilla: chem 5.2 %, refinery 15.9 %)",
    }, acc


MEASURES = {}


def sheet(opt):
    o = OPTS[opt]
    m, mov = measure(opt)
    MEASURES[opt] = m
    W = 2200
    work = on_ground(load(opt, "working-00", 2), 2)
    idle = on_ground(load(opt, "idle", 2), 2)
    crop = (60, 120, 640, 760)                 # 2x canvas: the building and its shadow
    work, idle = work.crop(crop), idle.crop(crop)
    H = 2400
    s = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(s)
    d.text((20, 14), o["title"], font=font(30, True), fill=TEXT)
    d.text((20, 54), "Reaction Plant redesign, options round -- lit Blender blockout (Claude in Chrome was not "
           "connected, so no ChatGPT concept). 3x3, one plate under rotation.", font=font(15), fill=SUB)
    y = 86
    d.text((20, y), "WORKING, 2x (frame 0; north-facing stubs as stand-ins)", font=font(15, True), fill=HEAD)
    d.text((20 + work.width + 16, y), "IDLE, 2x (light off, stopped)", font=font(15, True), fill=HEAD)
    s.alpha_composite(work, (20, y + 22))
    s.alpha_composite(idle, (20 + work.width + 16, y + 22))
    # motion map beside: frame 0 at 1x with moving pixels in magenta
    w1 = on_ground(load(opt, "working-00", 1), 1)
    tint = Image.new("RGBA", w1.size, (255, 0, 200, 0))
    tint.putalpha(mov.point(lambda v: int(v * 0.75)))
    w1.alpha_composite(tint)
    w1 = w1.crop((30, 60, 320, 380))
    x3 = 20 + 2 * work.width + 32
    d.text((x3, y), "1x, MOVING PIXELS IN MAGENTA", font=font(15, True), fill=HEAD)
    s.alpha_composite(w1, (x3, y + 22))
    # four rotations at game scale
    yd = y + 22 + w1.height + 20
    d.text((x3, yd), "THE ONE PLATE UNDER ROTATION, 1x", font=font(15, True), fill=HEAD)
    d.text((x3, yd + 20), "inputs on the faced side, the dormant output opposite (a cover)", font=font(12), fill=SUB)
    for i, dd in enumerate("NESW"):
        im = on_ground(load(opt, f"dir-{dd}", 1), 1).crop((40, 70, 300, 360))
        im = im.resize((im.width * 3 // 4, im.height * 3 // 4), Image.LANCZOS)
        px, py = x3 + (i % 2) * (im.width + 8), yd + 40 + (i // 2) * (im.height + 8)
        s.alpha_composite(im, (px, py))
        d.text((px + 4, py + 2), f"facing {dd}", font=font(12), fill=TEXT)
    # frame strip of the port at 3x game: every 4th frame, cropped to the lit area
    ys = y + 22 + work.height + 22
    w2 = load(opt, "working-00", 2)
    # the port itself: saturated bright blue (blue well above red), not the spill on the metal
    sat = ImageChops.subtract(w2.getchannel("B"), w2.getchannel("R")).point(lambda v: 255 if v > 110 else 0)
    bb = ImageChops.multiply(sat, w2.getchannel("A").point(lambda v: 255 if v > 200 else 0)).getbbox()
    pad = 16
    bb = (bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad)
    x3s = 20 + 2 * work.width + 32                # the rotation panels start here
    scale = min(1.0, ((x3s - 40) / 6 - 6) / (bb[2] - bb[0]), 260 / (bb[3] - bb[1]))
    d.text((20, ys), "THE VIEW PORT, 2x: frames 0, 4, 8, 12, 16, 20 of the 24-frame preview loop",
           font=font(15, True), fill=HEAD)
    xx = 20
    for f in range(0, NF, 4):
        fr = on_ground(load(opt, f"working-{f:02d}", 2), 2).crop(bb)
        if scale < 1:
            fr = fr.resize((int(fr.width * scale), int(fr.height * scale)), Image.LANCZOS)
        s.alpha_composite(fr, (xx, ys + 22))
        xx += fr.width + 6
    yt = ys + 22 + int((bb[3] - bb[1]) * scale) + 24
    # text
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
    d.text((col, yy), "PROPOSED SPEC 3.3 ROW (replaces 'the three sight slots only'; to agree with Liam)",
           font=font(14, True), fill=HEAD)
    yy += 21
    d.text((col + 10, yy), o["wording"], font=font(13), fill=TEXT)
    yy += 28
    d.text((col, yy), "ANIMATION PLAN (spec 6.2)", font=font(14, True), fill=HEAD)
    yy += 21
    for ln in o["anim"]:
        d.text((col + 10, yy), ln, font=font(13), fill=TEXT)
        yy += 18
    yy += 8
    d.text((col, yy), "MEASURED (working frame 0, 64 px a tile)", font=font(14, True), fill=HEAD)
    yy += 21
    for k, v in m.items():
        d.text((col + 10, yy), f"{k}: {v}", font=font(13), fill=TEXT)
        yy += 18
    s = s.crop((0, 0, W, max(yy + 20, yd + 40 + 2 * 226)))
    path = f"{OUT}/{opt}-{o['slug']}.png"
    s.convert("RGB").save(path)
    print(path, s.size)


def gif(opt):
    o = OPTS[opt]
    frames = []
    for f in range(NF):
        g2 = on_ground(load(opt, f"working-{f:02d}", 2), 2).crop((60, 120, 640, 760))
        g1 = on_ground(load(opt, f"working-{f:02d}", 1), 1).crop((30, 60, 320, 380))
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
    q[0].save(path, save_all=True, append_images=q[1:], duration=GIF_MS, loop=0)
    print(path)


# ------------------------------------------------------------- contact sheet
ENT = f"{FD}/base/graphics/entity"


def sidecar(stem):
    t = open(stem + ".lua").read()
    w = int(re.search(r"width\s*=\s*(\d+)", t).group(1))
    h = int(re.search(r"height\s*=\s*(\d+)", t).group(1))
    sx, sy = map(float, re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", t).groups())
    return w, h, sx, sy


def paste(canvas, im, origin, shift_px, additive=False):
    x = round(origin[0] + shift_px[0] - im.width / 2)
    y = round(origin[1] + shift_px[1] - im.height / 2)
    if additive:
        pad = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        pad.alpha_composite(im, (x, y))
        rgb = ImageChops.multiply(pad.convert("RGB"), Image.merge("RGB", [pad.getchannel("A")] * 3))
        out = ImageChops.add(canvas.convert("RGB"), rgb)
        canvas.paste(out.convert("RGBA"))
    else:
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


def current_plant(panel, origin):
    G = f"{REPO}/graphics/entity/reaction-plant"
    t = lambda v: v * PPT
    paste(panel, shadow_img(Image.open(f"{G}/shadow.png").convert("RGBA")), origin, (t(0.125), t(-0.0078)))
    paste(panel, Image.open(f"{G}/base.png").convert("RGBA"), origin, (t(0), t(-0.14062)))
    cp = Image.open(f"{G}/coupling.png").convert("RGBA")
    paste(panel, cp.crop((0, 0, cp.width // 12, cp.height)), origin, (t(0.10938), t(-0.78906)))
    paste(panel, Image.open(f"{G}/glow.png").convert("RGBA"), origin, (t(0), t(0.82031)), additive=True)


def contact():
    PH = 7 * PPT                                  # panel height: 7 tiles
    panels = []

    def panel(w_tiles, foot, label, draw):
        size = (w_tiles * PPT, PH)
        origin = (size[0] // 2, PH - int((foot / 2 + 1.0) * PPT))
        g = ground(size, origin, PPT, foot, extent=8)
        draw(g, origin)
        panels.append((label, g))

    panel(8, 5, "vanilla oil refinery, 5x5", vanilla_refinery)
    panel(5, 3, "vanilla chemical plant, 3x3", vanilla_chem)
    panel(5, 3, "Reaction Plant now, 3x3", current_plant)
    for opt in "ABCD":
        def draw(g, origin, opt=opt):
            im = load(opt, "working-00", 1)
            paste(g, im, origin, (CANVAS[0] / 2 - ORIGIN[0], CANVAS[1] / 2 - ORIGIN[1]))
        panel(5, 3, OPTS[opt]["title"].replace("  ", " ") + ", 3x3", draw)
    W = sum(p.width for _, p in panels) + 8 * (len(panels) + 1)
    sheet = Image.new("RGBA", (W, PH + 100), BG)
    d = ImageDraw.Draw(sheet)
    d.text((10, 8), "REACTION PLANT REDESIGN -- OPTIONS AT GAME SCALE", font=font(20, True), fill=TEXT)
    d.text((10, 36), "64 px a tile; frame 0 working, with shadows. Vanilla composited from its own layers "
           "(refinery tinted for advanced oil processing, chemical plant for sulfuric acid). "
           "Options are lit Blender blockouts.", font=font(12), fill=SUB)
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


for opt in "ABCD":
    sheet(opt)
    gif(opt)
contact()
with open(f"{OUT}/measures.txt", "w") as fh:
    for opt, m in MEASURES.items():
        fh.write(OPTS[opt]["title"] + "\n" + "".join(f"  {k}: {v}\n" for k, v in m.items()))
print(open(f"{OUT}/measures.txt").read())
