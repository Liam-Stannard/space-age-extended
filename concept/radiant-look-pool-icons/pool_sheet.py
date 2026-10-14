#!/usr/bin/env python3
"""Review sheet for the radiant pool in look B: today's pool against the proposal, in a client.

  python3 pool_sheet.py <cur-shots> <new-shots> <pieces-dir> <out-dir>

<cur-shots>, <new-shots>: the script-output/pool folders of two client runs on the same map
(seed 123456789, the Core's map-gen; the pool basin at (-70, 28), its east shore at (-56, 26)),
one with today's sheets and tiles.lua, one with this worktree's proposal. Each holds
wide-{day,night} (zoom 0.5), game-{day,night} (zoom 1: the game's own view, 32 px a tile),
sprite-{day,night} (zoom 2: 64 px a tile, the sprites' own pixels) and anim-{day,night}-NN
(32 water ticks, 4 apart: the lava shader's motion).
<pieces-dir>: look_pieces.py --look B --only one (the radiant-look study): idle.png,
work-00.png, glow-00.png at 4x.

Day and night are as the client drew them (take_screenshot daytime 0 and 0.5). The pieces'
day and night are composed as the study did (look_common.py): plate over ground plus glow;
night multiplies the lit scene by (0.17, 0.19, 0.27) and adds the glow after.

Writes <out-dir>/pool-review.png, pool-measures.json, pool-now-vs-B-{day,night}.gif.

Measures, on a crop that is pool only and one that is shore only (sprite shots):
  L        mean luminance; p5/p50/p95 its percentiles
  sat      mean saturation (max-min)/max
  blue     the study's blue share: B > 110, B > R + 45, B > G + 10 (r6_sheets.py)
  pale     share of blue-hued pixels with saturation < 0.45 and L > 150 (the pale-cyan top)
  cyan     share of coloured pixels (sat > 0.3) whose hue is under 205 deg (cyan-leaning)
  hue      mean hue of the coloured pixels, degrees (the solution's #1F63FF is 222)
  white    pixels with every channel >= 245 (clipped)
  motion   mean |dL| between consecutive animation frames (the shader's movement)
"""
import colorsys
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

BG = (30, 30, 30)
TXT = (230, 222, 205)
HEAD = (240, 200, 120)
GROUND = (74, 66, 58)
NIGHT = (0.17, 0.19, 0.27)
# crops in the sprite shots (1024 x 768, 64 px a tile, centred on (-58, 26))
POOL_BOX = (0, 160, 300, 608)
SHORE_BOX = (700, 0, 1024, 768)


def font(n, b=False):
    f = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if b else "")
    return ImageFont.truetype(f, n) if os.path.exists(f) else ImageFont.load_default()


def lum(p):
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


def measure(im):
    px = list(im.convert("RGB").getdata())
    L = sorted(lum(p) for p in px)
    n = len(px)
    sats, hues, blue, pale, cyan, white = [], [], 0, 0, 0, 0
    for r, g, b in px:
        mx, mn = max(r, g, b), min(r, g, b)
        s = 0 if mx == 0 else (mx - mn) / mx
        sats.append(s)
        if b > 110 and b > r + 45 and b > g + 10:
            blue += 1
        if min(r, g, b) >= 245:
            white += 1
        if s > 0.3 and mx > 30:
            h = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)[0] * 360
            hues.append(h)
            if h < 205:
                cyan += 1
        if b >= r and b >= g and s < 0.45 and lum((r, g, b)) > 150:
            pale += 1
    return dict(L=round(sum(L) / n, 1), p5=round(L[n // 20]), p50=round(L[n // 2]), p95=round(L[n * 19 // 20]),
                sat=round(sum(sats) / n, 2), blue=round(100 * blue / n, 1), pale=round(100 * pale / n, 2),
                cyan=round(100 * cyan / max(1, len(hues)), 1),
                hue=round(sum(hues) / max(1, len(hues))) if hues else None, white=white)


def motion(frames):
    d = []
    for a, b in zip(frames, frames[1:]):
        df = ImageChops.difference(a.convert("L"), b.convert("L"))
        h = df.histogram()
        d.append(sum(i * c for i, c in enumerate(h)) / max(1, sum(h)))
    return round(sum(d) / len(d), 2)


def down(path, k=4):
    im = Image.open(path).convert("RGBa")
    return im.resize((im.width // k, im.height // k), Image.LANCZOS).convert("RGBA")


def light_of(glow):
    r, g, b, a = glow.convert("RGBA").split()
    return Image.merge("RGB", [ImageChops.multiply(c, a) for c in (r, g, b)])


def darken(im, k=NIGHT):
    return Image.merge("RGB", [c.point(lambda v, kk=kk: int(v * kk)) for c, kk in zip(im.split(), k)])


def pieces(pdir):
    """The study's B pieces at 1x: day and night, on the study's ground."""
    plate = down(os.path.join(pdir, "work-00.png"))
    glow = light_of(down(os.path.join(pdir, "glow-00.png")))
    g = Image.new("RGBA", plate.size, GROUND + (255,))
    base = Image.alpha_composite(g, plate).convert("RGB")
    return ImageChops.add(base, glow), ImageChops.add(darken(base), glow)


class Sheet:
    def __init__(self, title, sub):
        self.title, self.sub, self.rows = title, sub, []

    def section(self, text, sub=()):
        self.rows.append(("s", text, list(sub)))

    def row(self, panels):
        self.rows.append(("r", panels, None))

    def render(self, path):
        f, fb, fh = font(13), font(15, True), font(22, True)
        pad, W, H = 18, 0, 0
        blocks = []
        for kind, a, b in self.rows:
            if kind == "r":
                w = sum(max(im.width, max(int(f.getlength(c)) for c in cap) + 6) for im, cap in a) + 14 * (len(a) - 1)
                h = max(im.height + 18 * len(cap) for im, cap in a) + 16
                W = max(W, w)
            else:
                h = 30 + 17 * len(b)
            blocks.append((kind, a, b, h))
            H += h
        W += 2 * pad
        W = max(W, max(int(f.getlength(s)) for s in self.sub) + 2 * pad)
        H += pad * 2 + 34 + 18 * len(self.sub) + 10
        out = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(out)
        y = pad
        d.text((pad, y), self.title, font=fh, fill=HEAD)
        y += 34
        for s in self.sub:
            d.text((pad, y), s, font=f, fill=TXT)
            y += 18
        y += 10
        for kind, a, b, h in blocks:
            if kind == "s":
                d.text((pad, y + 6), a, font=fb, fill=HEAD)
                for i, s in enumerate(b):
                    d.text((pad, y + 28 + 17 * i), s, font=f, fill=TXT)
            else:
                x = pad
                for im, cap in a:
                    for i, c in enumerate(cap):
                        d.text((x, y + 18 * i), c, font=f, fill=TXT)
                    out.paste(im, (x, y + 18 * len(cap)))
                    x += max(im.width, max(int(f.getlength(c)) for c in cap) + 6) + 14
            y += h
        out.save(path, optimize=True)


def up(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def main():
    cur, new, pdir, out = sys.argv[1:5]
    os.makedirs(out, exist_ok=True)
    shots = {}
    for tag, d in (("cur", cur), ("new", new)):
        for v in ("wide", "game", "sprite"):
            for t in ("day", "night"):
                shots[tag, v, t] = Image.open(os.path.join(d, f"{v}-{t}.png")).convert("RGB")
        for t in ("day", "night"):
            shots[tag, "anim", t] = [Image.open(os.path.join(d, f"anim-{t}-{k:02d}.png")).convert("RGB")
                                     for k in range(32)]
    M = {}
    for tag in ("cur", "new"):
        for t in ("day", "night"):
            sp = shots[tag, "sprite", t]
            M[f"{tag} {t}"] = dict(pool=measure(sp.crop(POOL_BOX)), shore=measure(sp.crop(SHORE_BOX)),
                                   motion=motion([f.crop((0, 0, 128, 384)) for f in shots[tag, "anim", t]]))
    pday, pnight = pieces(pdir)
    # the pieces' row: column (RP leg), slot and tubes (the generator's windows); 64 px a tile
    with open(os.path.join(out, "pool-measures.json"), "w") as fh:
        json.dump(M, fh, indent=1)

    def cap(tag, t):
        m = M[f"{tag} {t}"]
        p, s = m["pool"], m["shore"]
        return [f"pool L {p['L']} (p5/50/95 {p['p5']}/{p['p50']}/{p['p95']}) sat {p['sat']} hue {p['hue']}",
                f"  blue {p['blue']}% cyan {p['cyan']}% pale {p['pale']}% white {p['white']}; motion {m['motion']}",
                f"shore L {s['L']} sat {s['sat']} hue {s['hue']} blue {s['blue']}% cyan {s['cyan']}% white {s['white']}"]

    sh = Sheet("RADIANT POOL in look B -- a dark liquid lit from below (proposal; client screenshots)",
               ["Seed 123456789, the Core's map-gen; one headless client per side (Factorio 2.1, llvmpipe). Day: daytime 0; night: daytime 0.5,",
                "as the client draws them (take_screenshot), lights and all. 'now' is master's sheets and tiles.lua; 'B' is this worktree's test.",
                "B: Vulcanus's lava sheets re-graded by heat instead of hue-rotated -- melt on B's ramp #02081A > #04103A > #0B2A8C > #1F63FF > #5A9CFF,",
                "the pool's crust as dark sediment #07090E-#1C2029 (the silhouettes), the shore's as cool dark rock #16181E-#4A4D55; no pale cyan top.",
                "The shore's and lip's light sheets: the melt alone on B's glow ramp. tiles.lua: the lava shader's orange shore rim off (dark_threshold,",
                "specular_threshold 0), foam/specular/particles on the ramp. The pool keeps its light at night through the shader itself (a light layer on",
                "the pool tile and lightmap_alpha were both tried: no change in a client). Measures on a pool-only and a shore-only crop of",
                "the 64 px/tile shot: L mean (p5/p50/p95), saturation, mean hue (solution #1F63FF = 222 deg), study blue share, cyan share (hue < 205),",
                "pale share (blue, sat < 0.45, L > 150), white (all channels >= 245), motion (mean |dL| frame to frame, 32 water ticks 4 apart)."])
    for v, label, k in (("wide", "1. The basin, zoom 0.5 (16 px a tile)", 2), ("game", "2. The game's own view, zoom 1 (32 px a tile)", 1)):
        sh.section(label)
        for t in ("day", "night"):
            panels = []
            for tag, name in (("cur", "now"), ("new", "B")):
                im = shots[tag, v, t]
                im = im.resize((im.width // k, im.height // k), Image.LANCZOS) if k > 1 else im.crop((0, 0, 1024, 640))
                panels.append((im, [f"{name}, {t}"] + (cap(tag, t) if v == "game" else [])))
            sh.row(panels)
    sh.section("3. Sprite scale, zoom 2 (64 px a tile = 1x), with the study's look-B pieces beside at the same 1x; then the shore's lip at 3x",
               ["Pieces (concept/radiant-look/model/look_pieces.py --look B, frame 0): column (the RP leg), port, slot, tubes (the generator's), well;",
                "plate + glow, composed as the study composes day and night."])
    for t in ("day", "night"):
        pc = pday if t == "day" else pnight
        panels = []
        for tag, name in (("cur", "now"), ("new", "B")):
            im = shots[tag, "sprite", t].crop((0, 64, 1024, 704))
            panels.append((im, [f"{name}, {t}, 1x"]))
        sh.row(panels)
        row = [(pc, [f"look B pieces, {t}, 1x"])]
        for tag, name in (("cur", "now"), ("new", "B")):
            z = shots[tag, "sprite", t].crop((560, 280, 760, 480))
            row.append((up(z, 3), [f"{name}, {t}, the lip at 3x"]))
        sh.row(row)
    sh.section("4. The shader's motion: 8 of the 32 water-tick frames (every 4th), 64 px a tile, a 2 x 6 tile strip of pool")
    for t in ("day", "night"):
        for tag, name in (("cur", "now"), ("new", "B")):
            fr = shots[tag, "anim", t]
            strip = Image.new("RGB", (8 * 136, 384), BG)
            for i in range(8):
                strip.paste(fr[4 * i].crop((0, 0, 128, 384)), (i * 136, 0))
            sh.row([(strip, [f"{name}, {t}: frames 0, 4, ... 28"])])
    sh.render(os.path.join(out, "pool-review.png"))
    # one GIF per time of day: now (left) and B (right), the 3 x 6 tiles at the pool's edge
    for t in ("day", "night"):
        frames = []
        for a, b in zip(shots["cur", "anim", t], shots["new", "anim", t]):
            f = Image.new("RGB", (2 * 192 + 8, 384), BG)
            f.paste(a.crop((0, 0, 192, 384)), (0, 0))
            f.paste(b.crop((0, 0, 192, 384)), (200, 0))
            frames.append(f)
        frames[0].save(os.path.join(out, f"pool-now-vs-B-{t}.gif"), save_all=True, append_images=frames[1:],
                       duration=67, loop=0, optimize=True)
    print(json.dumps(M, indent=1))


if __name__ == "__main__":
    main()
