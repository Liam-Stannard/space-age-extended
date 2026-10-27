#!/usr/bin/env python3
"""Radiant Generator, round 7 (the Carousel Foundry refined): the sheet, GIFs, crops, measures.

  python3 r7_sheets.py <full-dir> <cmap-dir> <before-dir> <out-dir>

<full-dir>/1/ is r7_carousel_foundry.py's output (idle.png, plate.png, working-NN.png and
glow-NN.png at 4x, meta.json); <cmap-dir>/1/ its --colourmap run; <before-dir> round 6's
r6_1_carousel_foundry.py run unchanged (idle, plate, working-NN at 4x), for the before/after.
Round 6's helpers (load, ground, measure, motion map, palette, GIF) are unchanged, so the
measures are taken the same way: cover = plate alpha > 128 inside the footprint at 1x;
rise = the plate's top over the north edge; blue = the isotope's blue share of the opaque
working frame 0; moving = pixels that change by > 30 over the loop. Added in round 7:
corners (each corner tile's cover), the blue share before and after, and the flicker check
(strobe(): pixels whose 1x luminance reverses by > 20 on consecutive frames 3 times or more
a loop, the frame-to-frame back-and-forth that reads as strobing). Writes:

  1-the-carousel-foundry.png         the sheet
  1-the-carousel-foundry-1x.gif      the working loop at game scale (lit frames)
  1-the-carousel-foundry-2x.gif      the same at 2x (keep out of git)
  blue-before-after-4x.png, blue-before-after-1x.png   the crops
  measures.json
"""
import argparse
import json
import os

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageMath

ap = argparse.ArgumentParser()
ap.add_argument("full")
ap.add_argument("cmap")
ap.add_argument("before")
ap.add_argument("out")
args = ap.parse_args()
FULL, CMAP, BEFORE, OUT = args.full, args.cmap, args.before, args.out
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






# ---------------------------------------------------------------- round 7
def glow_over_black(path, k):
    """A glow pass (transparent, the lights only) at k x, premultiplied onto black."""
    im = load(path, k)
    b = Image.new("RGBA", im.size, (0, 0, 0, 255))
    b.alpha_composite(im)
    return b


def add(base, glow):
    return Image.merge("RGBA", (*ImageChops.add(base.convert("RGB"), glow.convert("RGB")).split(),
                                base.getchannel("A")))


def corners(plate1, foot):
    fw, fh = foot
    x0, y0 = ORIGIN[0] - fw * 32, ORIGIN[1] - fh * 32
    a = plate1.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    out = {}
    for nm, (i, j) in dict(NW=(0, 0), NE=(fw - 1, 0), SW=(0, fh - 1), SE=(fw - 1, fh - 1)).items():
        c = a.crop((x0 + 64 * i, y0 + 64 * j, x0 + 64 * i + 64, y0 + 64 * j + 64))
        out[nm] = round(100 * c.histogram()[255] / 4096, 1)
    return out


def strobe(frames1, thr=20, need=3):
    """255 where a pixel's 1x luminance (on the ground) reverses by > thr on consecutive frames
    `need` times or more a loop."""
    g = []
    for f in frames1:
        b = Image.new("RGBA", f.size, GROUND)
        b.alpha_composite(f)
        g.append(b.convert("L").convert("F"))
    n = len(g)
    d = [ImageMath.lambda_eval(lambda a: a["x"] - a["y"], x=g[(i + 1) % n], y=g[i]) for i in range(n)]
    acc = None
    for i in range(n):
        r = ImageMath.lambda_eval(lambda a: ((a["p"] * a["q"]) < 0) * (abs(a["p"]) > thr) * (abs(a["q"]) > thr),
                                  p=d[i], q=d[(i + 1) % n])
        acc = r if acc is None else ImageMath.lambda_eval(lambda a: a["x"] + a["y"], x=acc, y=r)
    return ImageMath.lambda_eval(lambda a: (a["x"] >= need) * 255, x=acc).convert("L")


def strobe_view(frame1, mask, k=2):
    b = Image.new("RGBA", frame1.size, GROUND)
    b.alpha_composite(frame1)
    o = Image.blend(b.convert("RGB"), Image.new("RGB", b.size, (30, 30, 30)), 0.5)
    o.paste((255, 0, 255), mask=mask)
    return o.resize((o.width * k, o.height * k), Image.NEAREST).convert("RGBA")


# the crops, in 1x sprite px (x0, y0, x1, y1) and the frame each is taken at
CROPS = [("bullseye port (collector head)", (116, 238, 170, 294), 0),
         ("plate-rack slot", (244, 136, 334, 192), 0),
         ("thermionic tubes", (328, 150, 378, 300), 0),
         ("plate-rack slot, crane over it", (244, 136, 334, 192), 21)]


def on_gr(im):
    b = Image.new("RGBA", im.size, GROUND)
    b.alpha_composite(im)
    return b


def crop_rows():
    """Before (round 6) and after (round 7) at 4x (the render) and at 1x (game scale, and the
    same 1x pixels blown up 4x nearest so they can be read)."""
    r4, r1 = [], []
    for cap, bx, f in CROPS:
        pair4, pair1 = [], []
        for d, who in ((BEFORE, "round 6"), (os.path.join(FULL, "1"), "round 7")):
            full4 = Image.open(os.path.join(d, f"working-{f:02d}.png")).convert("RGBA")
            c4 = on_gr(full4.crop(tuple(4 * v for v in bx)))
            pair4.append(captioned(c4, who, 12))
            c1 = on_gr(load(os.path.join(d, f"working-{f:02d}.png"), 1).crop(bx))
            big = c1.resize((c1.width * 4, c1.height * 4), Image.NEAREST)
            pair1.append(captioned(hrow([c1, big], 8), who + ": 1x, and 1x blown up", 12))
        r4.append(captioned(hrow(pair4, 10), f"{cap}, frame {f}"))
        r1.append(captioned(hrow(pair1, 10), f"{cap}, frame {f}"))
    a = vstack([hrow(r4[:2], 24), hrow(r4[2:], 24)], 14)
    b = vstack([hrow(r1[:2], 24), hrow(r1[2:], 24)], 14)
    return a, b


ANIM = [
    "As round 6: 32 frames, one loop = one crane cycle (frames 0-4 hoist A takes the fresh cell; 4-10 B sets the "
    "spent one in the pocket; 10-16 the bridge runs to the crucible; 16-26 B takes the spent cell from the well, "
    "A sets the fresh one; 26-32 the bridge runs back); the carousel indexes one pocket in frames 11-20; the well "
    "lid is up in frames 15-27; commutator one turn, couplings, gauges, status lamps. Idle: frame 0 still, unlit.",
    "The light, round 7 (draw_as_glow, glow-NN beside every working-NN): no pattern moves inside any opening, "
    "only its strength. Tubes swell in turn along the row, twice a loop, 70-100 % (round 6 blinked 45-100 %); the "
    "bullseye port holds steady and dims to 50 % while the table indexes (round 6 rippled +-10 % three times a "
    "loop and dropped to 20 %); the slot breathes +-8 %; the well's mouth rises over three frames as the lid lifts "
    "(round 6 switched it in under two).",
    "Toned down for 1x (the flicker check): the commutator has 8 bars in dark copper, not 12 black ones (at one "
    "turn a loop the 12 sat 2.7 frames apart and strobed); the ring gear has half the teeth (round 6's tooth pitch "
    "was close to one index-frame's travel, so it wagon-wheeled); the crane bridge's hazard ticks are gone (they "
    "twinkled as it ran).",
]
BLUE = [
    "Round 6's blue was a noise-and-wave texture, evenly bright edge to edge, moving inside every opening, under "
    "refractive glass that threw white fireflies over the dark: flat screens pasted on. Round 7 is one light seen "
    "into depth, in three kinds of opening:",
    "- Bullseye port (collector head): smaller (0.1 tile radius, was 0.155), the light recessed behind a dark "
    "bezel ring and a lens, a guard bar across it as a silhouette, a thin highlight arc on the glass.",
    "- Plate-rack slot: smaller (1.0 x 0.38 tile, was 1.28 x 0.5); the light is a floor deep in the slot, bright "
    "along its middle, deep navy at its ends; a dark liner round it is the frame's shadow; the copper plates and "
    "the cells between them stand in it as dark silhouettes; one short highlight on the glazing.",
    "- Tubes: a slim emitter column low in each glass (bright where it faces you, dark at its grazing edges), its "
    "grid rings and two supports dark in front of it, a dark collar at the socket, one highlight down the glass.",
    "- Well's mouth: recessed in the lead collar behind a dark lip, the tops of three cells dark in it. It is "
    "never seen at this camera: the lid is off only while the crane stands over it (frames 15-27), and hoist B "
    "covers it, in the lit frames and the glow layer alike; no crop.",
    "Every opening: a core grading #73ADFF -> #1F63FF -> #0B2A8C -> near-black navy, set up-sun so the frame's own "
    "shadow darkens the far rim. Glass is a thin dark film with a highlight, not refraction. The glow layer is "
    "rendered apart from the lit frames: the lights alone, everything in front of them held out.",
]


def build():
    d = os.path.join(FULL, "1")
    meta = json.load(open(os.path.join(d, "meta.json")))
    nf = meta["frames"]
    foot = tuple(meta["footprint"])
    work2 = [load(os.path.join(d, f"working-{f:02d}.png"), 2) for f in range(nf)]
    work1 = [load(os.path.join(d, f"working-{f:02d}.png"), 1) for f in range(nf)]
    glow2 = [glow_over_black(os.path.join(d, f"glow-{f:02d}.png"), 2) for f in range(nf)]
    idle2 = load(os.path.join(d, "idle.png"), 2)
    idle1 = load(os.path.join(d, "idle.png"), 1)
    plate1 = load(os.path.join(d, "plate.png"), 1)
    plate2 = load(os.path.join(d, "plate.png"), 2)
    b_work1 = [load(os.path.join(BEFORE, f"working-{f:02d}.png"), 1) for f in range(nf)]
    b_plate1 = load(os.path.join(BEFORE, "plate.png"), 1)
    m = measure(1, plate1, work1[0], work1, foot)
    mb = measure(1, b_plate1, b_work1[0], b_work1, foot)
    m["corners_pct"] = corners(plate1, foot)
    mb["corners_pct"] = corners(b_plate1, foot)
    opq = plate1.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    b_opq = b_plate1.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    st, st_b = strobe(work1), strobe(b_work1)
    m["strobe_pct"] = round(100 * count(st, opq) / opq.histogram()[255], 2)
    mb["strobe_pct"] = round(100 * count(st_b, b_opq) / b_opq.histogram()[255], 2)
    REG = {"commutator": (255, 330, 300, 400), "carousel": (60, 150, 200, 300), "crane and crucible": (200, 90, 340, 300),
           "tubes": (328, 150, 378, 300)}
    m["strobe_px_by_region"] = {k: st.crop(b).histogram()[255] for k, b in REG.items()}
    mb["strobe_px_by_region"] = {k: st_b.crop(b).histogram()[255] for k, b in REG.items()}
    # the light's own share: the glow layer's lit pixels at 1x, frame 0
    g1 = load(os.path.join(d, "glow-00.png"), 1).getchannel("A").point(lambda v: 255 if v > 64 else 0)
    m["glow_px_1x_f0"] = g1.histogram()[255]
    bb1 = bbox_of([idle1] + work1[::4], 1, pad=14)
    bb2 = tuple(2 * v for v in bb1)
    g_w2 = [on_ground(f, 2, foot).crop(bb2) for f in work2]
    g_i2 = on_ground(idle2, 2, foot).crop(bb2)
    g_w1 = [on_ground(f, 1, foot).crop(bb1) for f in work1]
    g_i1 = on_ground(idle1, 1, foot).crop(bb1)
    g_b1 = on_ground(b_work1[0], 1, foot).crop(bb1)
    s1 = gif(g_w1, os.path.join(OUT, "1-the-carousel-foundry-1x.gif"))
    s2 = gif(g_w2, os.path.join(OUT, "1-the-carousel-foundry-2x.gif"))
    m["gif_1x_mb"], m["gif_2x_mb"] = round(s1, 2), round(s2, 2)
    chain = numbered(g_w2[0].copy(), dict(labels=[dict(L, px=[L["px"][0] - bb1[0], L["px"][1] - bb1[1]])
                                                   for L in meta["labels"]]))
    mm = motion_map(plate2.crop(bb2), [w.crop(bb2) for w in work2])
    mmg = ground(mm.size, ((ORIGIN[0] - bb1[0]) * 2, (ORIGIN[1] - bb1[1]) * 2), 128, foot)
    mmg.alpha_composite(mm)
    cm = Image.open(os.path.join(CMAP, "1", "colourmap.png")).convert("RGBA")
    cmg = ground(cm.size, (ORIGIN[0] * 2, ORIGIN[1] * 2), 128, foot)
    cmg.alpha_composite(cm)
    cmg = cmg.crop(bb2)
    used = used_groups(os.path.join(CMAP, "1", "colourmap.png"), os.path.join(CMAP, "1", "colourmap.json"))
    # the glow: alone, and a night view (the frame at a quarter, the glow added)
    gl0 = glow2[0].crop(bb2)
    night = Image.eval(g_w2[0].convert("RGB"), lambda v: int(v * 0.25)).convert("RGBA")
    night = add(night, gl0)
    gstrip = hrow([g.crop(bb2).resize((g.crop(bb2).width // 4, g.crop(bb2).height // 4), Image.LANCZOS)
                   for g in glow2[::4]], 4)
    # the blue: crops
    c4, c1 = crop_rows()
    c4.convert("RGB").save(os.path.join(OUT, "blue-before-after-4x.png"))
    c1.convert("RGB").save(os.path.join(OUT, "blue-before-after-1x.png"))
    # the outline: plate at 1x before and after, blown up 2x nearest, the footprint drawn
    def outline(pl):
        g = on_ground(pl, 1, foot).crop(bb1)
        return g.resize((g.width * 2, g.height * 2), Image.NEAREST)
    kf = [int(i * nf / 8) for i in range(8)]
    keys = [g_w1[i] for i in kf]
    r1 = hrow([captioned(g_w2[0], "WORKING, 2x (frame 0, the lit frame)"), captioned(g_i2, "IDLE, 2x (stopped, unlit)")])
    r2 = hrow([captioned(chain, "THE CHAIN, CELL TO WIRE (numbered, 2x)"),
               captioned(mmg, "MOTION MAP: magenta moves, cyan is the isotope's light")])
    rg = hrow([captioned(gl0, "GLOW LAYER (draw_as_glow), 2x, frame 0, on black",),
               captioned(night, "NIGHT: frame 0 at 25 %, the glow layer added")])
    ro = hrow([captioned(outline(b_plate1), f"OUTLINE BEFORE (round 6 plate, 1x shown 2x): cover {mb['cover_pct']} %\n"
                         f"corner tiles NW {mb['corners_pct']['NW']} NE {mb['corners_pct']['NE']} "
                         f"SW {mb['corners_pct']['SW']} SE {mb['corners_pct']['SE']} %"),
               captioned(outline(plate1), f"OUTLINE AFTER (round 7 plate): cover {m['cover_pct']} %\n"
                         f"corner tiles NW {m['corners_pct']['NW']} NE {m['corners_pct']['NE']} "
                         f"SW {m['corners_pct']['SW']} SE {m['corners_pct']['SE']} %")])
    rf = hrow([captioned(strobe_view(b_work1[0].crop(bb1), st_b.crop(bb1)),
                         f"FLICKER BEFORE (round 6, 1x shown 2x): strobing {mb['strobe_pct']} % of the plate"),
               captioned(strobe_view(work1[0].crop(bb1), st.crop(bb1)),
                         f"FLICKER AFTER (round 7): strobing {m['strobe_pct']} % of the plate")])
    beside = hrow([captioned(g_b1, "round 6: 1. (working, 1x)"), captioned(g_w1[0], "round 7 (working, 1x)"),
                   captioned(g_i1, "round 7 idle, 1x")], 14)
    W = max(r1.width, r2.width, rg.width, c4.width, c1.width, ro.width, rf.width) + 20
    r3 = hrow([captioned(cmg, "COLOUR MAP (each part in its palette group's key colour), 2x"),
               captioned(palette(os.path.join(CMAP, "1", "colourmap.json"), used, 520), "PALETTE")])
    r4 = captioned(vstack([hrow(keys[:4], 6), hrow(keys[4:], 6)], 6),
                   f"KEY FRAMES, 1x: frames {', '.join(map(str, kf))} of {nf}")
    sub = wrap("Round 7: round 6's variant 1, chosen by Liam 2026-10-12 (\"the blue textures look out of place and "
               "could be improved\"). The blue remade as the isotope's light seen into depth through glass; the "
               "outline broken at the edges and corners; the animation checked at 1x for flicker. Lit Blender "
               "concept on the GPU; not adopted; nothing in graphics/.", 13, W - 20)
    head_ = Image.new("RGBA", (W, 44 + 18 * len(sub)), BG)
    dd = ImageDraw.Draw(head_)
    text(dd, (10, 6), "RADIANT GENERATOR, ROUND 7 -- THE CAROUSEL FOUNDRY, REFINED  (5 x 5)", 22, HEAD, True)
    for i, ln in enumerate(sub):
        text(dd, (10, 40 + 18 * i), ln, 13, SUB)
    meas = (f"Footprint {m['footprint']} ({m['mw_per_tile']} MW a tile). Cover {m['cover_pct']} % (round 6 "
            f"{mb['cover_pct']} %; the bar is 92 %). Rise {m['rise_tiles']:+.2f} tile (round 6 {mb['rise_tiles']:+.2f}; "
            f"limit +0.66). Blue, lit frame 0, {m['blue_pct']} % of the opaque plate (round 6 {mb['blue_pct']} %). "
            f"Moving share {m['changing_pct']} % (round 6 {mb['changing_pct']} %). Strobing pixels {m['strobe_pct']} % "
            f"(round 6 {mb['strobe_pct']} %). GIF 1x {m['gif_1x_mb']} MB, 2x {m['gif_2x_mb']} MB.")
    OUTL = [
        "Round 6 ran dark-steel deck slabs to the footprint's edge: a square plinth. Round 7's deck stops 0.3 tile "
        "short (it is the floor between the units) and the equipment makes the edge: west, the carousel's rim and "
        "its drive, the spent bin proud of the face; south-west, the transformer and the trunks leaving at the "
        "corner, ground showing round them; south, the converter's bedplate and feet; south-east, the switchgear "
        "stops short and the corner is open; east, the tube column on its skid; north-east, the shield housing and "
        "radiator end short and a round teal-topped coolant expansion tank stands in the corner; north-west, the gas "
        "bottles and pump round the carousel's curve, ground in the corner.",
    ]
    rb, ra = mb["strobe_px_by_region"], m["strobe_px_by_region"]
    FLK = [
        f"Strobing pixels (1x luminance reversing by > 20 on consecutive frames 3+ times a loop): round 6 "
        f"{mb['strobe_pct']} %, round 7 {m['strobe_pct']} % of the plate. By region, round 6 -> 7 (px): "
        + ", ".join(f"{k} {rb[k]} -> {ra[k]}" for k in REG) + ".",
        "The true strobes are fixed: the commutator (12 black bars 2.7 frames apart) now has 8 dark-copper bars, two "
        "hazard keys and turns half a turn a loop (8 frames a bar), half its strobing pixels gone and the rest its keys "
        "passing; the lights no longer flicker (no moving texture; the tubes swell 70-100 %); the bridge's hazard "
        "ticks and half the ring-gear teeth are gone; the pockets carry 4 bolts, not 8.",
        "What the check still flags is texture crawl on fast, large moves, not a strobe: the carousel deck in the "
        "index (frames 10-18 only) and the crane bridge and its shadow on its two runs (frames 10-14 and 25-29), "
        "where each 1x pixel sees new lead mottling every frame. Easing it further means a slower index or crane, "
        "i.e. a longer loop; not done here. Unchecked in the client.",
    ]
    blocks = [
        block("WHAT CHANGED IN THE BLUE", BLUE, W),
        block("THE OUTLINE", OUTL, W),
        block("THE FLICKER CHECK", FLK, W),
        block("CELL TO WIRE (the numbers on the plate below)", chain_lines(meta), W, tight=True),
        block("ANIMATION (unchanged chain and motion; the light and the flicker fixes)", ANIM, W),
        block("MEASURED (64 px a tile)", [meas], W),
    ]
    sheet = vstack([head_, r1, blocks[0],
                    captioned(c4, "THE BLUE, BEFORE AND AFTER, 4x (the render)"),
                    captioned(c1, "THE BLUE, BEFORE AND AFTER, 1x (game scale), each with its 1x pixels blown up 4x"),
                    rg, captioned(gstrip, "GLOW LAYER, frames 0, 4, 8 ... 28 (0.5x)"),
                    blocks[1], ro, rf, blocks[2], r2, blocks[3],
                    captioned(beside, "BESIDE ROUND 6, 1x (64 px a tile)"), r3, r4] + blocks[4:], width=W)
    pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
    pad.alpha_composite(sheet, (10, 10))
    path = os.path.join(OUT, "1-the-carousel-foundry.png")
    pad.convert("RGB").save(path)
    json.dump({"round-7": m, "round-6 (re-rendered, unchanged)": mb}, open(os.path.join(OUT, "measures.json"), "w"),
              indent=1)
    print(path, pad.size)
    print(json.dumps({"r7": m, "r6": mb}, indent=1))


build()
