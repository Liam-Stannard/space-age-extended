#!/usr/bin/env python3
"""Radiant Generator, round 6 (3 + 4 + 7 combined, bulky): sheets, GIFs, measures, contact sheet.

  python3 r6_sheets.py <full-dir> <cmap-dir> <out-dir> [--factorio <data>] [--rp-model <sheets>]
                       [--r5 <round-5 dir>] [--turbine <graphics/entity/crust-turbine>] [--only 1,2,3]

<full-dir>/<n>/ is r6_<n>_*.py's output (idle.png, plate.png, working-NN.png at 4x, meta.json
with the labelled chain); <cmap-dir>/<n>/ its --colourmap run. Round 5's helpers (load, ground,
measure, motion map, palette, GIF) are taken unchanged from round-5/r5a_sheets.py, so the
measures are taken the same way: cover = plate alpha > 128 inside the footprint at 1x; rise =
the plate's top over the north edge; blue = the isotope's blue share of the opaque working
frame 0; moving = pixels that change by > 30 over the loop, of the opaque plate. Writes:

  <n>-<slug>.png        the sheet (working and idle at 2x, the chain numbered and listed, the
                        motion map, colour map, key frames, round 5's 3, 4 and 7 beside it at
                        1x, the pitch, the animation plan, the Reactor headroom, measures)
  <n>-<slug>-1x.gif     the working loop at game scale on the ground (under 5 MB)
  <n>-<slug>-2x.gif     the same at 2x (keep out of git)
  contact-sheet.png     the three at game scale beside vanilla's steam engine, steam turbine
                        and fusion generator (working), the Reaction Plant model, the Siderane
                        turbine, and round 5's 3, 4 and 7
  measures.json
"""
import argparse
import json
import os
import re

from PIL import Image, ImageChops, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("full")
ap.add_argument("cmap")
ap.add_argument("out")
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
ap.add_argument("--rp-model", default=os.path.expanduser(
    "~/git/space-age-extended/.claude/worktrees/reaction-plant-redesign/concept/reaction-plant/model/sheets"))
ap.add_argument("--r5", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "round-5"))
ap.add_argument("--turbine", default=os.path.expanduser(
    "~/git/space-age-extended/.claude/worktrees/master-merge/graphics/entity/crust-turbine"))
ap.add_argument("--only", default="1,2,3")
args = ap.parse_args()
FULL, CMAP, OUT, FD = args.full, args.cmap, args.out, args.factorio
os.makedirs(OUT, exist_ok=True)

PPT = 64
CANVAS, ORIGIN = (512, 448), (208, 272)
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT = (228, 222, 210)
SUB = (175, 168, 156)
HEAD = (240, 200, 120)
GIF_MS = 70


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def load(path, k):
    """A 4x render brought to k x game scale, premultiplied, faint catcher fog cut."""
    im = Image.open(path).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    src = im.width // CANVAS[0]
    im = im.convert("RGBa").resize((CANVAS[0] * k, CANVAS[1] * k), Image.LANCZOS)
    return im.convert("RGBA")


def ground(size, origin, ppt, foot):
    """The game's ground with the tile grid and the footprint outlined."""
    g = Image.new("RGBA", size, GROUND)
    ov = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    ox, oy = origin
    fw, fh = foot
    offx = 0.5 if fw % 2 else 0.0
    offy = 0.5 if fh % 2 else 0.0
    for i in range(-24, 25):
        x = ox + (i + offx) * ppt
        y = oy + (i + offy) * ppt
        d.line([(x, 0), (x, size[1])], fill=(255, 255, 255, 22))
        d.line([(0, y), (size[0], y)], fill=(255, 255, 255, 22))
    d.rectangle([ox - fw * ppt / 2, oy - fh * ppt / 2, ox + fw * ppt / 2, oy + fh * ppt / 2],
                outline=(255, 255, 255, 110))
    g.alpha_composite(ov)
    return g


def on_ground(im, k, foot):
    g = ground(im.size, (ORIGIN[0] * k, ORIGIN[1] * k), PPT * k, foot)
    g.alpha_composite(im)
    return g


def text(d, xy, s, size=13, fill=TEXT, bold=False):
    d.text(xy, s, font=font(size, bold), fill=fill)


def wrap(s, size, width):
    f = font(size)
    out, line = [], ""
    for w in s.split(" "):
        t = (line + " " + w).strip()
        if f.getlength(t) > width and line:
            out.append(line)
            line = w
        else:
            line = t
    if line:
        out.append(line)
    return out


def block(title, paras, width, size=13, tight=False):
    lines = []
    for p in paras:
        lines += wrap(p, size, width - 20) + ([] if tight else [""])
    h = 30 + len(lines) * (size + 5)
    im = Image.new("RGBA", (width, h), BG)
    d = ImageDraw.Draw(im)
    text(d, (10, 6), title, 15, HEAD, bold=True)
    y = 30
    for ln in lines:
        text(d, (14, y), ln, size)
        y += size + 5
    return im


def captioned(im, cap, size=13):
    lines = cap.split("\n")
    w = max([im.width] + [int(font(size, True).getlength(ln)) + 10 for ln in lines])
    hh = 6 + (size + 6) * len(lines)
    c = Image.new("RGBA", (w, im.height + hh), BG)
    d = ImageDraw.Draw(c)
    for i, ln in enumerate(lines):
        text(d, (4, 4 + (size + 6) * i), ln, size, HEAD if i == 0 else SUB, bold=(i == 0))
    c.alpha_composite(im, (0, hh))
    return c


def hrow(ims, gap=12):
    w = sum(i.width for i in ims) + gap * (len(ims) - 1)
    h = max(i.height for i in ims)
    r = Image.new("RGBA", (w, h), BG)
    x = 0
    for i in ims:
        r.alpha_composite(i, (x, 0))
        x += i.width + gap
    return r


def vstack(ims, gap=12, width=None):
    w = width or max(i.width for i in ims)
    h = sum(i.height for i in ims) + gap * (len(ims) - 1)
    r = Image.new("RGBA", (w, h), BG)
    y = 0
    for i in ims:
        r.alpha_composite(i, (0, y))
        y += i.height + gap
    return r


def bbox_of(ims, k, pad=10):
    box = None
    for im in ims:
        b = im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    p = pad * k
    return (max(0, box[0] - p), max(0, box[1] - p), min(CANVAS[0] * k, box[2] + p), min(CANVAS[1] * k, box[3] + p))


def blue_mask(im):
    """255 where a pixel is the isotope's blue: B > 110, B > R + 45, B > G + 10."""
    r, g, b = im.convert("RGB").split()
    m1 = b.point(lambda v: 255 if v > 110 else 0)
    m2 = ImageChops.subtract(b, r).point(lambda v: 255 if v > 45 else 0)
    m3 = ImageChops.subtract(b, g).point(lambda v: 255 if v > 10 else 0)
    return ImageChops.multiply(ImageChops.multiply(m1, m2), m3)


def count(mask, within):
    return ImageChops.multiply(mask, within).histogram()[255]



def chain_lines(meta):
    return [f"{L['n']}. {L['text']}" for L in sorted(meta["labels"], key=lambda L: L["n"])]


def measure(n, plate, work0, frames1, foot):
    """Cover (plate alpha > 128 inside the footprint), rise over the north edge, blue share
    of the working plate, moving share across the loop; all at 1x."""
    fw, fh = foot
    x0, y0 = ORIGIN[0] - fw * 32, ORIGIN[1] - fh * 32
    a = plate.getchannel("A")
    opq = a.point(lambda v: 255 if v > 128 else 0)
    inside = a.crop((int(x0), int(y0), int(x0 + fw * 64), int(y0 + fh * 64))).point(lambda v: 255 if v > 128 else 0)
    cover = inside.histogram()[255] / (fw * fh * 64 * 64)
    bb = a.point(lambda v: 255 if v > 128 else 0).getbbox()
    rise = (y0 - bb[1]) / 64
    n_op = opq.histogram()[255]
    blue = count(blue_mask(work0), opq) / n_op
    f0 = frames1[0].convert("RGB")
    diff = None
    for f in frames1[1:]:
        dd = ImageChops.difference(f0, f.convert("RGB")).convert("L").point(lambda v: 255 if v > 30 else 0)
        diff = dd if diff is None else ImageChops.lighter(diff, dd)
    moving = count(diff, opq) / n_op
    return dict(cover_pct=round(100 * cover, 1), rise_tiles=round(rise, 2), blue_pct=round(100 * blue, 1),
                changing_pct=round(100 * moving, 1), footprint=f"{fw} x {fh}",
                mw_per_tile=round(10 / (fw * fh), 2))


def motion_map(idle2, frames2):
    """Idle at 2x, dimmed; pixels that change over the loop in magenta (moving metal) and
    cyan (the light)."""
    base = idle2.convert("RGB")
    f0 = frames2[0].convert("RGB")
    move = None
    light = None
    for f in frames2:
        fr = f.convert("RGB")
        dd = ImageChops.difference(f0, fr).convert("L").point(lambda v: 255 if v > 30 else 0)
        move = dd if move is None else ImageChops.lighter(move, dd)
        bl = blue_mask(fr)
        light = bl if light is None else ImageChops.lighter(light, bl)
    out = Image.blend(base, Image.new("RGB", base.size, (40, 36, 32)), 0.55)
    out.paste((230, 40, 200), mask=move)
    out.paste((60, 220, 255), mask=light)
    o = out.convert("RGBA")
    o.putalpha(idle2.getchannel("A"))
    return o


def numbered(im2, meta):
    d = ImageDraw.Draw(im2)
    for L in meta["labels"]:
        x, y = L["px"][0] * 2, L["px"][1] * 2
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(240, 200, 120), outline=(20, 18, 16), width=2)
        s = str(L["n"])
        w = font(15, True).getlength(s)
        d.text((x - w / 2, y - 9), s, font=font(15, True), fill=(20, 18, 16))
    return im2


def palette(cm_json, used, width):
    groups = json.load(open(cm_json))
    items = [(g, h) for g, h in groups.items() if g in used]
    im = Image.new("RGBA", (width, 22 * ((len(items) + 1) // 2) + 8), BG)
    d = ImageDraw.Draw(im)
    for i, (g, h) in enumerate(items):
        x = 8 + (i % 2) * (width // 2)
        y = 4 + 22 * (i // 2)
        d.rectangle([x, y, x + 16, y + 16], fill=h, outline=(0, 0, 0))
        text(d, (x + 24, y), g, 12)
    return im


def used_groups(cmap_png, cm_json):
    groups = json.load(open(cm_json))
    im = Image.open(cmap_png).convert("RGBA")
    cols = {c[1][:3] for c in im.getcolors(1 << 20) if c[1][3] > 200}
    out = set()
    for g, h in groups.items():
        rgb = tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        if any(max(abs(rgb[j] - c[j]) for j in range(3)) <= 6 for c in cols):
            out.add(g)
    return out


def gif(frames, path):
    strip = Image.new("RGB", (frames[0].width, frames[0].height * len(frames)))
    for i, f in enumerate(frames):
        strip.paste(f.convert("RGB"), (0, i * f.height))
    pal = strip.quantize(colors=256)
    q = [f.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=GIF_MS, loop=0, optimize=True)
    return os.path.getsize(path) / 1e6





MEAS = {}
FIRST = {}


def lua_shift(path):
    t = open(path).read()
    return tuple(float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", t).groups())


def ref_canvas(w_t, h_t, layers, foot, glow=()):
    """Compose sprites on a ground of w_t x h_t tiles centred on the entity; layers are
    (image, shift px at 64 px a tile, mode)."""
    W, H = int(w_t * 64), int(h_t * 64)
    c = ground((W, H), (W // 2, H // 2), 64, foot)
    for im, (sx, sy), mode in layers:
        x = round(W / 2 + sx - im.width / 2)
        y = round(H / 2 + sy - im.height / 2)
        if mode == "shadow":
            sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
            sh.putalpha(im.getchannel("A").point(lambda v: int(v * 0.5)))
            c.alpha_composite(sh, (x, y))
        elif mode == "add":
            rgb = Image.new("RGB", c.size, (0, 0, 0))
            rgb.paste(im.convert("RGB"), (x, y), im.getchannel("A"))
            c = Image.merge("RGBA", (*ImageChops.add(c.convert("RGB"), rgb).split(), c.getchannel("A")))
        else:
            c.alpha_composite(im, (x, y))
    return c


def frame(path, w, h, i=0, line=1):
    im = Image.open(path).convert("RGBA")
    return im.crop(((i % line) * w, (i // line) * h, (i % line) * w + w, (i // line) * h + h))



# ---------------------------------------------------------------- the variants' words
ANIM_COMMON = [
    "32 frames, one loop = one crane cycle; all in `animation` (burner-generator draws `animation` and "
    "`idle_animation` only), the light as draw_as_glow layers in it; `idle_animation` is frame 0 unlit.",
    "Crane cycle (bridge, trolley, two hook blocks, cables, the carried cells): hoist A lowers onto the fresh "
    "cell at the pick pocket and lifts it (frames 0-4); the trolley traverses a hoist's pitch and hoist B sets "
    "the spent cell in the empty pocket (4-10); the bridge runs to the crucible (10-16); B takes the spent cell "
    "out of the well, the trolley traverses, A sets the fresh one (16-26); the bridge runs back (26-32).",
    "Carousel index: one pocket a loop, still except frames 11-20 (an eased step); the deck, ring gear, rim marks "
    "and every pocket's cell move; the pinion two turns and the drive coupling three turns, in the step only. "
    "Cells are fresh from the loading hood to the pick, spent from the pick to the hood (the swap is under it).",
    "Well lid: hinged up frames 15-27; the well's mouth lit while it is off (draw_as_glow).",
    "Tube glow chase: each tube's emitter brightens in turn along its row, twice a loop (draw_as_glow); the "
    "plate rack's floor of light breathes +-15 %; the collector head's window is full while a cell waits under "
    "it and dims to 20 % during the index.",
    "Commutator: one turn a loop (12 bars, a hazard key and a red key, so the turn reads at 1x without aliasing); the converter coupling one "
    "turn; the coolant pump coupling two turns; gauge needles swing; the status lamps light.",
    "Idle: everything still and unlit, the crane parked over the pick with the spent cell on hoist B. Scales "
    "with perceived_performance: animation speed (crane pace, index, commutator) and the glow's alpha.",
]
S = {
    1: dict(slug="the-carousel-foundry", name="THE CAROUSEL FOUNDRY", foot=(5, 5),
            why="5 x 5, carousel-led: the turntable takes the west half (eight pockets, a visible reserve), the "
                "crucible the east, the converter the south front. Rows of them tile with the loading hoods on "
                "the west (one belt between two rows), the trunks at the south-west corner, the radiator housings "
                "back to back on the north.",
            read="A great lead turntable on a banded drum, an ochre crane bridging it to a lead crucible with its "
                 "plate rack under glazing and a column of glass tubes down the east flank; the green-and-grey "
                 "rotary converter across the front. It reads as a cell store feeding a foundry for current.",
            headroom="Stage 1: one carousel, one crane, one crucible, a rotary converter (an electromechanical, "
                     "lossy last step). The Reactor keeps in reserve: a turbine-alternator hall instead of a "
                     "converter, several crucibles under one crane, rails that run on into the neighbour (the "
                     "bonus as shared track), and an open core whose blue is a pool, not a slot.",
            finish="Lead (bloomed) on the drum, deck, hood, crucible and bins: what holds the isotope. Oxide-red "
                   "collector head with grey fins; ochre crane (vanilla's yellow, worn) with hazard bands; clear "
                   "glass tubes, copper caps, plates and bus; green DC machine, grey AC machine, cream exciter and "
                   "transformer; grey and green switchgear; a grey shield housing with the family's teal roof; "
                   "dark-steel deck slabs; worn_paint over all, rust only in seams and at the feet, oil at the "
                   "converter."),
    2: dict(slug="the-crane-hall", name="THE CRANE HALL", foot=(5, 5),
            why="5 x 5, gantry-led: the crane runs the whole width on a shield housing and a post line, its "
                "travel 2.3 tiles; the long crucible and its twelve tubes fill the middle, the converter the "
                "front. Placed east-west in a row the rails line up end to end (one long hall), the trunks on "
                "the east, the carousels' hoods facing the aisle.",
            read="A long crane hall: the ochre bridge over a long lead crucible flanked by two rows of six glass "
                 "tubes, a small carousel at the east end, the converter and transformer along the front. It "
                 "reads as a foundry line: one crane feeding a long trough of light.",
            headroom="Stage 1: one crane and one crucible feeding twelve tubes, a converter for AC. The Reactor "
                     "is the same hall grown: several crucibles on one track that runs through its neighbours "
                     "(continuous rails are the bonus made visible), tube cassettes instead of single tubes, a "
                     "turbine-alternator, and an open core.",
            finish="As variant 1 (one palette for the family): lead crucible, carousel and bin; ochre crane and "
                   "post line; glass and copper tubes; green DC and grey AC machines, cream exciter and "
                   "transformer; teal roof on the shield housing; dark-steel deck."),
    3: dict(slug="the-commutator-front", name="THE COMMUTATOR FRONT", foot=(5, 5),
            why="5 x 5, plate-rack- and converter-led: the glazed plate rack is the centre, the biggest rotary "
                "converter of the three is the whole south front, the carousel sits north and the crane runs "
                "north-south between two banks of tubes. Rows tile with the trunks on the south edge and the "
                "carousels back to back on the north.",
            read="A big green-and-grey rotary converter along the front, its copper commutator turning in the "
                 "open at the west end; behind it a lead crucible with a wide glazed plate rack, banks of glass "
                 "tubes either side, the ochre crane over it and the carousel beyond. It reads as a power house: "
                 "the machine that makes the current is the face.",
            headroom="Stage 1 ends in a rotary converter: the commutator is the visible limit. The Reactor keeps "
                     "the turbine-alternator and static conversion, several plate racks, a crane bay it shares "
                     "with its neighbour (the bonus), and an open core.",
            finish="As variant 1; the converter is the largest painted unit (green DC, grey AC, cream exciter), "
                   "the commutator bare copper with dark bars and a hazard key; lead crucible with the widest "
                   "glazing; teal-roofed shield housing at the north-west."),
}


def r5_frames():
    """Round 5's 3, 4 and 7 at game scale: frame 0 of their 1x GIFs (already on the ground)."""
    out = []
    for f, cap in (("3-the-carousel-collector-1x.gif", "round 5: 3. Carousel Collector"),
                   ("4-the-thermionic-gantry-1x.gif", "round 5: 4. Thermionic Gantry"),
                   ("7-the-plate-rack-1x.gif", "round 5: 7. Plate Rack")):
        im = Image.open(os.path.join(args.r5, f))
        im.seek(0)
        out.append((cap, im.convert("RGBA")))
    return out


def build(n):
    o = S[n]
    d = os.path.join(FULL, str(n))
    meta = json.load(open(os.path.join(d, "meta.json")))
    nf = meta["frames"]
    foot = tuple(meta["footprint"])
    work2 = [load(os.path.join(d, f"working-{f:02d}.png"), 2) for f in range(nf)]
    work1 = [load(os.path.join(d, f"working-{f:02d}.png"), 1) for f in range(nf)]
    idle2 = load(os.path.join(d, "idle.png"), 2)
    idle1 = load(os.path.join(d, "idle.png"), 1)
    plate1 = load(os.path.join(d, "plate.png"), 1)
    plate2 = load(os.path.join(d, "plate.png"), 2)
    m = measure(n, plate1, work1[0], work1, foot)
    MEAS[n] = m
    bb1 = bbox_of([idle1] + work1[::4], 1, pad=14)
    bb2 = tuple(2 * v for v in bb1)
    g_w2 = [on_ground(f, 2, foot).crop(bb2) for f in work2]
    g_i2 = on_ground(idle2, 2, foot).crop(bb2)
    g_w1 = [on_ground(f, 1, foot).crop(bb1) for f in work1]
    g_i1 = on_ground(idle1, 1, foot).crop(bb1)
    FIRST[n] = (g_w1[0], meta, foot, m)
    s1 = gif(g_w1, os.path.join(OUT, f"{n}-{o['slug']}-1x.gif"))
    s2 = gif(g_w2, os.path.join(OUT, f"{n}-{o['slug']}-2x.gif"))
    m["gif_1x_mb"], m["gif_2x_mb"] = round(s1, 2), round(s2, 2)
    chain = numbered(g_w2[0].copy(), dict(labels=[dict(L, px=[L["px"][0] - bb1[0], L["px"][1] - bb1[1]])
                                                   for L in meta["labels"]]))
    mm = motion_map(plate2.crop(bb2), [w.crop(bb2) for w in work2])
    mmg = ground(mm.size, ((ORIGIN[0] - bb1[0]) * 2, (ORIGIN[1] - bb1[1]) * 2), 128, foot)
    mmg.alpha_composite(mm)
    cm = Image.open(os.path.join(CMAP, str(n), "colourmap.png")).convert("RGBA")
    cmg = ground(cm.size, (ORIGIN[0] * 2, ORIGIN[1] * 2), 128, foot)
    cmg.alpha_composite(cm)
    cmg = cmg.crop(bb2)
    used = used_groups(os.path.join(CMAP, str(n), "colourmap.png"), os.path.join(CMAP, str(n), "colourmap.json"))
    kf = [int(i * nf / 8) for i in range(8)]
    keys = [g_w1[i] for i in kf]
    r1 = hrow([captioned(g_w2[0], "WORKING, 2x (frame 0)"), captioned(g_i2, "IDLE, 2x (stopped, unlit)")])
    r2 = hrow([captioned(chain, "THE CHAIN, CELL TO WIRE (numbered, 2x)"),
               captioned(mmg, "MOTION MAP: magenta moves, cyan is the isotope's light")])
    beside = hrow([captioned(g_w1[0], f"round 6: {n}. {o['name'].title()} (working)"),
                   captioned(g_i1, "idle")] + [captioned(im, cap) for cap, im in r5_frames()], 14)
    W = max(r1.width, r2.width, beside.width) + 20
    chain_blk = block("CELL TO WIRE (the numbers on the plate above)", chain_lines(meta), W, tight=True)
    r3 = hrow([captioned(cmg, "COLOUR MAP (each part in its palette group's key colour), 2x"),
               captioned(palette(os.path.join(CMAP, str(n), "colourmap.json"), used, 520), "PALETTE")])
    r4 = captioned(vstack([hrow(keys[:4], 6), hrow(keys[4:], 6)], 6),
                   f"KEY FRAMES, 1x: frames {', '.join(map(str, kf))} of {nf}")
    sub = wrap("Round 6: round 5's 3 (Carousel Collector), 4 (Thermionic Gantry) and 7 (Plate Rack) combined into "
               "one bulky building, one chain. 10 MW, a cell every 50 s, a spent cell out. Lit Blender concept on "
               "the GPU in the Reaction Plant's finish (worn_paint, a paint per unit, lead on what holds the "
               "isotope, blue only where the cell's light shows). Not adopted; nothing in graphics/.", 13, W - 20)
    head_ = Image.new("RGBA", (W, 44 + 18 * len(sub)), BG)
    dd = ImageDraw.Draw(head_)
    text(dd, (10, 6), f"RADIANT GENERATOR, ROUND 6 -- {n}. {o['name']}  ({foot[0]} x {foot[1]})", 22, HEAD, True)
    for i, ln in enumerate(sub):
        text(dd, (10, 40 + 18 * i), ln, 13, SUB)
    meas = (f"Footprint {m['footprint']} ({m['mw_per_tile']} MW a tile). Cover {m['cover_pct']} % of the footprint "
            f"(plate alpha > 128, 1x; the bar is 92 %). Rise over the north edge {m['rise_tiles']:+.2f} tile (the "
            f"limit +0.66). Blue (the isotope's light, lit, frame 0) {m['blue_pct']} % of the opaque plate. Pixels "
            f"that change over the loop (moving share) {m['changing_pct']} %. GIF 1x {m['gif_1x_mb']} MB, 2x "
            f"{m['gif_2x_mb']} MB.")
    blocks = [
        block("PITCH", ["READ: " + o["read"], "FOOTPRINT: " + o["why"]], W),
        chain_blk,
        block("ANIMATION PLAN (for spec 6.2)", ANIM_COMMON, W),
        block("REACTOR HEADROOM (stage 1 of 4)", [o["headroom"]], W),
        block("FINISH", [o["finish"]], W),
        block("MEASURED (64 px a tile)", [meas], W),
    ]
    sheet = vstack([head_, r1, r2] + blocks[:2] +
                   [captioned(beside, "BESIDE ROUND 5's 3, 4 AND 7, 1x (64 px a tile)"), r3, r4] + blocks[2:], width=W)
    pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
    pad.alpha_composite(sheet, (10, 10))
    path = os.path.join(OUT, f"{n}-{o['slug']}.png")
    pad.convert("RGB").save(path)
    print(path, pad.size, m)


def references():
    B, SA = f"{FD}/base/graphics/entity", f"{FD}/space-age/graphics/entity"
    out = []
    se = frame(f"{B}/steam-engine/steam-engine-H.png", 352, 257, 0, 8)
    ses = frame(f"{B}/steam-engine/steam-engine-H-shadow.png", 508, 160, 0, 8)
    out.append(("vanilla steam engine 5x3 (0.9 MW)",
                ref_canvas(8, 5, [(ses, (96, 48), "shadow"), (se, (2, -9.5), "n")], (5, 3))))
    st = frame(f"{B}/steam-turbine/steam-turbine-H.png", 320, 245, 0, 4)
    sts = frame(f"{B}/steam-turbine/steam-turbine-H-shadow.png", 435, 150, 0, 1)
    out.append(("vanilla steam turbine 5x3 (5.8 MW)",
                ref_canvas(8, 5, [(sts, (57, 36), "shadow"), (st, (0, -5.5), "n")], (5, 3))))
    G = f"{SA}/fusion-generator/north/fusion-generator-north"
    fg = frame(G + ".png", 244, 376, 0, 3)
    fgs = Image.open(G + "-shadow.png").convert("RGBA")
    fgg = frame(G + "-glow.png", 202, 336, 0, 3)
    out.append(("fusion generator 3x5, working (50 MW)",
                ref_canvas(6, 7, [(fgs, (25, 8), "shadow"), (fg, (-4, -4), "n"), (fgg, (0, -8), "add")], (3, 5))))
    R = args.rp_model
    rmeta = json.load(open(os.path.join(R, "meta.json")))
    rb = Image.open(os.path.join(R, "base.png")).convert("RGBA")
    rs = Image.open(os.path.join(R, "shadow.png")).convert("RGBA")
    out.append(("Reaction Plant model 5x5 (its base and shadow sheets)",
                ref_canvas(8, 7, [(rs, tuple(64 * v for v in rmeta["shadow"]["shift"]), "shadow"),
                                  (rb, tuple(64 * v for v in rmeta["base"]["shift"]), "n")], (5, 5))))
    T = args.turbine
    tb = Image.open(f"{T}/base-horizontal.png").convert("RGBA")
    tbs = Image.open(f"{T}/base-shadow-horizontal.png").convert("RGBA")
    tr = frame(f"{T}/rotor-horizontal.png", 58, 55, 0, 8)
    out.append(("Siderane turbine 5x3 (its sheets, 1.8 MW)",
                ref_canvas(8, 5, [(tbs, (25, 10), "shadow"), (tb, (0, -3.5), "n"), (tr, (-1, -20.5), "n")], (5, 3))))
    return out


def contact():
    refs = references()
    row_r = hrow([captioned(im, nm, 12) for nm, im in refs], 16)
    row_5 = hrow([captioned(im, cap, 12) for cap, im in r5_frames()], 16)
    ours = []
    for n in sorted(FIRST):
        im, meta, foot, m = FIRST[n]
        ours.append(captioned(im, f"{n}. {S[n]['name'].title()}, {foot[0]}x{foot[1]}, working\n"
                                  f"cover {m['cover_pct']} %, rise {m['rise_tiles']:+.2f} t, blue {m['blue_pct']} %, "
                                  f"moving {m['changing_pct']} %", 12))
    row_o = hrow(ours, 16)
    W = max(row_r.width, row_o.width, row_5.width) + 20
    head_ = Image.new("RGBA", (W, 56), BG)
    d = ImageDraw.Draw(head_)
    text(d, (10, 6), "RADIANT GENERATOR, ROUND 6 -- 3 + 4 + 7 COMBINED, BULKY, AT GAME SCALE", 20, HEAD, True)
    text(d, (10, 32), "64 px a tile, one ground. Top: vanilla's steam engine and steam turbine (frame 0), the fusion "
         "generator working, the Reaction Plant model, the Siderane turbine. Middle: round 5's 3, 4 and 7. "
         "Bottom: round 6's three, working, frame 0.", 12, SUB)
    sheet = vstack([head_, row_r, row_5, row_o], 16, width=W)
    pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
    pad.alpha_composite(sheet, (10, 10))
    pad.convert("RGB").save(os.path.join(OUT, "contact-sheet.png"))
    print(os.path.join(OUT, "contact-sheet.png"), pad.size)


for n in [int(v) for v in args.only.split(",")]:
    build(n)
json.dump(MEAS, open(os.path.join(OUT, "measures.json"), "w"), indent=1)
if len(FIRST) == 3:
    contact()
