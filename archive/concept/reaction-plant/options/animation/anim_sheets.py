#!/usr/bin/env python3
"""Reaction Plant redesign, animation previews: GIFs, moving-pixel maps and measures.

  python3 anim_sheets.py <hi-root> <out-dir> [--factorio <data>]

<hi-root>/<mode>/ holds anim_previews.py's 4x renders for each mode (working-NN.png,
plate.png, idle.png). Writes into <out-dir>:

  <n>-<mode>.gif         the loop, 2x beside 1x on the ground with the plant's own pipe
                         pictures facing north (round 5's), and for the small motions a
                         4x detail of the moving part; ~14 fps (70 ms), as round 5
  press-frames.png       the press cycle's 16 unique frames at 2x, the accent frame marked
  moving-maps.png        each preview's moving pixels (red) over its plate at 1x, with
                         the crop boxes, and the numbers
  measures.txt           frames, loop, moving share, crops, per preview

Moving pixels as round 5 measured them (r5_sheets.py): a pixel moves if any frame
differs from frame 0 by more than 10 in a channel, at 1x; the share counts those on the
plate's opaque mask (alpha over 128) over the opaque count. The crop is the bounding box
of every moving pixel, ground included (a falling drop, a shadow), grouped into clusters
8 px apart -- what the working visualisation's sheet would have to cover.
"""
import argparse
import json
import os
from collections import deque

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("hi")
ap.add_argument("out")
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
args = ap.parse_args()
HI, OUT, FD = args.hi, args.out, args.factorio
HERE = os.path.dirname(os.path.abspath(__file__))
PORTS = os.path.normpath(os.path.join(HERE, "..", "round-5", "ports"))
PMETA = json.load(open(os.path.join(PORTS, "meta.json")))
COVER = f"{FD}/base/graphics/entity/pipe-covers/pipe-cover-"
os.makedirs(OUT, exist_ok=True)

PPT, FOOT = 64, 5
ORIGIN = (208, 272)
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT, SUB, HEAD = (228, 222, 210), (175, 168, 156), (240, 200, 120)
GIF_MS = 70
CROP1 = (8, 14, 456, 448)
CROP2 = tuple(2 * v for v in CROP1)

# mode: (number, title, frames, gif durations note, 4x detail box in 1x px or None)
MODES = [
    ("current", "1. Current plan: the legs (24 f) and the four couplings", 24, None),
    ("press", "2. Filter press cycle: follower backs off, the cake drops (16 unique f; accent on f10)", 16,
     (100, 330, 240, 440)),
    ("gauges", "3. Gauge needles: the reactor's two and the scrubber's, twitching (24 f)", 24, (255, 235, 345, 325)),
    ("gauges_big", "3b. Gauge needles on dials twice round 5's size (a model change; 24 f)", 24, (255, 235, 345, 325)),
    ("drive", "4. Agitator drive: shaft, 5-spoke pulley, belt, motor pulley (24 f)", 24, None),
    ("drip", "5. Vent condenser: condensate beads and a drain-cock drip (24 f); no steam", 24,
     (330, 60, 420, 200)),
    ("all", "6. All together (48 f: the loops twice, the press once; its in-game hold is ~17 s)", 48, None),
]
PRESS_LAND = 10


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def load(path, k):
    """A 4x render brought to k x game scale, premultiplied, faint catcher fog cut."""
    im = Image.open(path).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    if k == 4:
        return im
    im = im.convert("RGBa").resize((im.width * k // 4, im.height * k // 4), Image.LANCZOS)
    return im.convert("RGBA")


def ground(size, origin, ppt, foot=FOOT, extent=10):
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


def paste(canvas, im, centre):
    x = round(centre[0] - im.width / 2)
    y = round(centre[1] - im.height / 2)
    canvas.alpha_composite(im, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))


NAME = {"N": "north", "E": "east", "S": "south", "W": "west"}


def port_layers(face, tile, k):
    off = {"N": (tile, -3), "S": (tile, 3), "E": (3, -tile), "W": (-3, -tile)}[face]
    cx, cy = off[0] * PPT * k, off[1] * PPT * k
    sx, sy = PMETA[f"port-{face}"]["shift"]
    pic = Image.open(os.path.join(PORTS, f"port-{face}.png")).convert("RGBA")
    cov = Image.open(COVER + NAME[face] + ".png").convert("RGBA")
    if k != 1:
        pic = pic.resize((pic.width * k, pic.height * k), Image.LANCZOS)
        cov = cov.resize((cov.width * k, cov.height * k), Image.LANCZOS)
    return pic, cov, (cx + sx * PPT * k, cy + sy * PPT * k), (cx, cy)


PORTS_N = [("N", -1), ("N", 1), ("S", 0)]
_LAYERS = {}


def compose(plate, k):
    g = ground(plate.size, (ORIGIN[0] * k, ORIGIN[1] * k), PPT * k)
    o = (ORIGIN[0] * k, ORIGIN[1] * k)
    if k not in _LAYERS:
        _LAYERS[k] = [port_layers(f, t, k) for f, t in PORTS_N]

    def draw(north):
        for (f, _), (pic, cov, pc, cc) in zip(PORTS_N, _LAYERS[k]):
            if (f == "N") == north:
                paste(g, pic, (o[0] + pc[0], o[1] + pc[1]))
                paste(g, cov, (o[0] + cc[0], o[1] + cc[1]))
    draw(True)
    g.alpha_composite(plate)
    draw(False)
    return g


def cnt(im):
    return sum(1 for v in im.get_flattened_data() if v)


def clusters(mask, gap=8):
    """Bounding boxes of the moving pixels, grouped where they lie within `gap` px."""
    grown = mask.filter(ImageFilter.MaxFilter(2 * (gap // 2) + 1))
    w, h = grown.size
    px = grown.load()
    src = mask.load()
    seen = bytearray(w * h)
    out = []
    for y in range(h):
        for x in range(w):
            if px[x, y] and not seen[y * w + x]:
                q = deque([(x, y)])
                seen[y * w + x] = 1
                x0 = y0 = 10 ** 9
                x1 = y1 = -1
                n = 0
                while q:
                    cx, cy = q.popleft()
                    if src[cx, cy]:
                        x0, y0, x1, y1 = min(x0, cx), min(y0, cy), max(x1, cx), max(y1, cy)
                        n += 1
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < w and 0 <= ny < h and px[nx, ny] and not seen[ny * w + nx]:
                            seen[ny * w + nx] = 1
                            q.append((nx, ny))
                if n:
                    out.append((x0, y0, x1 + 1, y1 + 1, n))
    return sorted(out, key=lambda b: -b[4])


def measure(mode, nf):
    d = os.path.join(HI, mode)
    plate = load(os.path.join(d, "plate.png"), 1)
    mask = plate.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    opaque = cnt(mask)
    f0 = load(os.path.join(d, "working-00.png"), 1)
    acc = Image.new("L", f0.size, 0)
    for f in range(1, nf):
        df = ImageChops.difference(f0, load(os.path.join(d, f"working-{f:02d}.png"), 1))
        r, g, b, a = df.split()
        m = ImageChops.lighter(ImageChops.lighter(r, g), ImageChops.lighter(b, a))
        acc = ImageChops.lighter(acc, m.point(lambda v: 255 if v > 10 else 0))
    on = ImageChops.multiply(acc, mask)
    moving = cnt(on)
    bb = mask.getbbox()
    ox, oy = ORIGIN
    rise = (oy - FOOT * PPT // 2 - bb[1]) / PPT
    allcl = clusters(acc)
    cl = [b for b in allcl if b[4] >= 10]          # under 10 px: render flicker from moving light
    union = (min(b[0] for b in cl), min(b[1] for b in cl), max(b[2] for b in cl), max(b[3] for b in cl)) \
        if cl else (0, 0, 0, 0)
    return {"opaque": opaque, "moving": moving, "share": moving / opaque, "acc": acc, "plate": plate,
            "clusters": cl, "union": union, "rise": rise, "flicker": len(allcl) - len(cl)}


def area(b):
    return (b[2] - b[0]) * (b[3] - b[1])


def gif(idx, mode, title, nf, detail):
    d = os.path.join(HI, mode)
    frames = []
    for f in range(nf):
        p = os.path.join(d, f"working-{f:02d}.png")
        g2 = compose(load(p, 2), 2).crop(CROP2)
        g1 = compose(load(p, 1), 1).crop(CROP1)
        panels = [g2, g1]
        if detail:
            x0, y0, x1, y1 = detail
            g4 = compose(load(p, 4), 4).crop((x0 * 4, y0 * 4, x1 * 4, y1 * 4))
            if g4.height > g2.height:
                g4 = g4.resize((g4.width * g2.height // g4.height, g2.height), Image.LANCZOS)
            panels.append(g4)
        w = sum(pn.width for pn in panels) + 12 * (len(panels) - 1)
        im = Image.new("RGBA", (w, g2.height + 34), BG)
        dr = ImageDraw.Draw(im)
        dr.text((8, 8), title, font=font(16, True), fill=HEAD)
        x = 0
        labels = ["2x", "1x", "4x detail"]
        for i, pn in enumerate(panels):
            im.alpha_composite(pn, (x, 34))
            dr.text((x + 6, 38), labels[i], font=font(13, True), fill=TEXT)
            x += pn.width + 12
        tag = f"f{f:02d}"
        if mode == "press" and f == PRESS_LAND or mode == "all" and f == 24 + PRESS_LAND:
            tag += "  cake lands (accent)"
        dr.text((w - 260, 10), tag, font=font(14), fill=SUB)
        frames.append(im.convert("RGB"))
    strip = Image.new("RGB", (frames[0].width, frames[0].height * min(nf, 12)))
    for i, f in enumerate(frames[::max(1, nf // 12)][:12]):
        strip.paste(f, (0, i * f.height))
    pal = strip.quantize(colors=255)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    dur = [GIF_MS] * nf
    if mode == "press":
        dur[0] = 1400          # the hold, shortened: ~17 s of a 20 s craft at speed 1
    path = os.path.join(OUT, f"{idx}-{mode}.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=dur, loop=0, optimize=True)
    return path, os.path.getsize(path)


def press_strip():
    d = os.path.join(HI, "press")
    box = (40, 300, 300, 440)               # 1x px: the press, the receiver, the follower's stroke
    tiles = []
    for f in range(16):
        g = compose(load(os.path.join(d, f"working-{f:02d}.png"), 2), 2).crop(tuple(2 * v for v in box))
        dr = ImageDraw.Draw(g)
        dr.text((6, 4), f"f{f}", font=font(15, True), fill=HEAD if f != PRESS_LAND else (255, 120, 90))
        if f == PRESS_LAND:
            dr.rectangle([0, 0, g.width - 1, g.height - 1], outline=(255, 120, 90), width=3)
        tiles.append(g)
    cols = 4
    tw, th = tiles[0].size
    s = Image.new("RGBA", (cols * (tw + 8) + 8, 4 * (th + 8) + 48), BG)
    ImageDraw.Draw(s).text((8, 12), "THE PRESS CYCLE, 2x: 16 unique frames. f0 closed (the plate); f1-4 the follower backs "
                                    "off 0.24 tile; f5 the cake hangs; f6-9 it peels and falls; f10 it is in the box "
                                    "(the accent); f11-15 the follower closes", font=font(13), fill=TEXT)
    for i, t in enumerate(tiles):
        s.alpha_composite(t, (8 + (i % cols) * (tw + 8), 48 + (i // cols) * (th + 8)))
    p = os.path.join(OUT, "press-frames.png")
    s.convert("RGB").save(p)
    return p


def maps(results):
    tiles = []
    for (mode, title, nf, _), r in zip(MODES, results):
        base = compose(r["plate"], 1).crop(CROP1)
        dark = Image.blend(base.convert("RGB"), Image.new("RGB", base.size, (0, 0, 0)), 0.55).convert("RGBA")
        red = Image.new("RGBA", base.size, (255, 60, 40, 255))
        dark.paste(red, (0, 0), r["acc"].crop(CROP1))
        dr = ImageDraw.Draw(dark)
        for b in r["clusters"]:
            dr.rectangle([b[0] - CROP1[0], b[1] - CROP1[1], b[2] - CROP1[0] - 1, b[3] - CROP1[1] - 1],
                         outline=(255, 220, 90), width=1)
        lab = Image.new("RGBA", (dark.width, 64), BG)
        dl = ImageDraw.Draw(lab)
        dl.text((4, 4), title.split(":")[0], font=font(13, True), fill=HEAD)
        dl.text((4, 24), f"moving {r['share'] * 100:.1f} % of opaque", font=font(12), fill=TEXT)
        u = r["union"]
        dl.text((4, 42), f"union crop {u[2] - u[0]} x {u[3] - u[1]} px (1x)", font=font(12), fill=SUB)
        t = Image.new("RGBA", (dark.width, dark.height + 64), BG)
        t.alpha_composite(lab, (0, 0))
        t.alpha_composite(dark, (0, 64))
        tiles.append(t)
    tw, th = tiles[0].size
    rows = (len(tiles) + 2) // 3
    s = Image.new("RGBA", (3 * (tw + 10) + 10, rows * (th + 10) + 50), BG)
    ImageDraw.Draw(s).text((10, 14), "MOVING PIXELS at 1x (red), crops (yellow), over each preview's plate. Vanilla: "
                                     "chemical plant 5.2 %, oil refinery 15.9 %", font=font(14, True), fill=HEAD)
    for i, t in enumerate(tiles):
        s.alpha_composite(t, (10 + (i % 3) * (tw + 10), 50 + (i // 3) * (th + 10)))
    p = os.path.join(OUT, "moving-maps.png")
    s.convert("RGB").save(p)
    return p


results = []
lines = ["Reaction Plant, animation previews on round 5's Circulator (anim_previews.py, anim_sheets.py)",
         "moving pixels: any frame differs from frame 0 by > 10, at 1x; share = on the opaque mask / opaque "
         "(vanilla: chemical plant 5.2 %, oil refinery 15.9 %; round 5 3.8 %)",
         "crops: 1x px, clusters 8 px apart, ground included (falling drops, shadows); 4x renders are 4x these",
         ""]
NUM = ["1", "2", "3", "3b", "4", "5", "6"]
for i, (mode, title, nf, detail) in zip(NUM, MODES):
    r = measure(mode, nf)
    results.append(r)
    path, size = gif(i, mode, title, nf, detail)
    u = r["union"]
    lines.append(title)
    lines.append(f"  frames {nf}; moving {r['moving']} px of {r['opaque']} opaque = {r['share'] * 100:.1f} %; "
                 f"plate rises {r['rise']:.2f} tiles above the north edge (round 5 0.78)")
    lines.append(f"  union crop {u[2] - u[0]} x {u[3] - u[1]} px = {area(u)} px^2 at ({u[0]}, {u[1]})")
    for b in r["clusters"][:8]:
        lines.append(f"    cluster {b[2] - b[0]} x {b[3] - b[1]} px at ({b[0]}, {b[1]}), {b[4]} moving px")
    if len(r["clusters"]) > 8:
        lines.append(f"    ... {len(r['clusters']) - 8} more clusters")
    lines.append(f"    ({r['flicker']} specks under 10 px left out: render flicker, not motion)")
    lines.append(f"  GIF {path}  {size / 1e6:.2f} MB")
    lines.append("")
    print(lines[-3], lines[-2])
press_strip()
maps(results)
open(os.path.join(OUT, "measures.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
