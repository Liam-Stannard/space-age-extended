#!/usr/bin/env python3
"""The Gas Pump's pumping animation, for review: GIFs and a key-frame sheet.

  python3 animation_review.py <sheets-dir> <out-dir> [--r13 <round 13 sheets-dir>]

  <sheets-dir>  render.sh's packed sheets: base-, base-shadow-, pump-, sight-glass-<d> and
                meta.json (frame counts, sizes, shifts)
  <out-dir>     where the review goes:
                  gas-pump-working-<gas>-1x.gif, -2x.gif  every direction, idle then working,
                      on one ground: half a second stopped (the plate with the moving parts'
                      frame 0, the glass dark), then three loops of the stroke with the glass
                      tinted as that gas's vent tints it
                  review-animation.png  the key-frame sheet
  --r13         the signed-off round 13 sheets (base-, base-shadow-, sight-glass-<d>): drawn
                beside the new plate on the same ground at the same scale

Everything is layered as the engine draws it: the cast shadow at 50 %, the plate, the moving
parts' layer, and while working the glass's layer, multiplied by the tint (apply_tint =
"resource-color" with each vent's mining_visualisation_tint). The GIFs play a frame every
40 ms, the nearest a GIF can come to the declared 24 frames a second (one stroke a second).
"""
import json
import os
import sys

from PIL import Image, ImageDraw

PPT = 64
DIRS = ("north", "east", "south", "west")
GROUND = (74, 66, 58, 255)
BG = (30, 30, 30, 255)
TINTS = (("siderane", (0.66, 0.85, 0.16)), ("helium-3", (0.55, 0.78, 0.90)))
TILES = 3                    # each panel: the 2x2 footprint with half a tile round it


def frame_of(sheets, meta, stem, f):
    im = Image.open(os.path.join(sheets, stem + ".png")).convert("RGBA")
    m = meta[stem]
    if "frames" not in m:
        return im
    w, h = m["size"]
    line = m["line_length"]
    return im.crop(((f % line) * w, (f // line) * h, (f % line) * w + w, (f // line) * h + h))


def tinted(light, rgb):
    r, g, b, a = light.split()
    return Image.merge("RGBA", (r.point(lambda v: round(v * rgb[0])), g.point(lambda v: round(v * rgb[1])),
                                b.point(lambda v: round(v * rgb[2])), a))


class Sheets:
    def __init__(self, path):
        self.path = path
        self.meta = json.load(open(os.path.join(path, "meta.json")))
        self.cache = {}

    def get(self, stem, f=0):
        k = (stem, f)
        if k not in self.cache:
            self.cache[k] = frame_of(self.path, self.meta, stem, f)
        return self.cache[k]

    def shift(self, stem):
        return self.meta[stem]["shift"]

    def frames(self, stem):
        return self.meta[stem].get("frames", 1)


def put(c, im, sx, sy, shadow=False):
    if shadow:
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        lay.paste(Image.new("RGBA", im.size, (0, 0, 0, 255)), (0, 0), im.getchannel("A").point(lambda v: v // 2))
        im = lay
    o = TILES * PPT / 2
    c.alpha_composite(im, (round(o + sx * PPT - im.width / 2), round(o + sy * PPT - im.height / 2)))


def grid(c):
    d = ImageDraw.Draw(c, "RGBA")
    n = TILES * PPT
    for i in range(TILES + 1):
        v = round(i * PPT - PPT / 2) if TILES % 2 else i * PPT
        d.line([(v, 0), (v, n)], fill=(255, 255, 255, 28))
        d.line([(0, v), (n, v)], fill=(255, 255, 255, 28))
    o = n / 2
    d.rectangle([o - PPT, o - PPT, o + PPT, o + PPT], outline=(255, 255, 255, 70))


def scene(s, d, f=0, tint=None, moving=True, glass_stem="sight-glass"):
    """One direction on the ground: shadow, plate, the moving parts in frame f, and with
    `tint` the glass's frame f tinted."""
    c = Image.new("RGBA", (TILES * PPT, TILES * PPT), GROUND)
    grid(c)
    put(c, s.get(f"base-shadow-{d}"), *s.shift(f"base-shadow-{d}"), shadow=True)
    put(c, s.get(f"base-{d}"), *s.shift(f"base-{d}"))
    if moving and f"pump-{d}" in s.meta:
        put(c, s.get(f"pump-{d}", f), *s.shift(f"pump-{d}"))
    if tint is not None:
        g = f"{glass_stem}-{d}"
        put(c, tinted(s.get(g, f % s.frames(g)), tint), *s.shift(g))
    return c


def label(im, text, bar=14):
    o = Image.new("RGBA", (im.width, im.height + bar), BG)
    o.alpha_composite(im, (0, bar))
    ImageDraw.Draw(o).text((3, 2), text, fill=(225, 225, 225, 255))
    return o


def row(ims, gap=4):
    w = sum(i.width for i in ims) + gap * (len(ims) - 1)
    h = max(i.height for i in ims)
    o = Image.new("RGBA", (w, h), BG)
    x = 0
    for i in ims:
        o.alpha_composite(i, (x, 0))
        x += i.width + gap
    return o


def column(ims, gap=6):
    w = max(i.width for i in ims)
    o = Image.new("RGBA", (w, sum(i.height for i in ims) + gap * (len(ims) - 1)), BG)
    y = 0
    for i in ims:
        o.alpha_composite(i, (0, y))
        y += i.height + gap
    return o


def up(im, k):
    return im if k == 1 else im.resize((im.width * k, im.height * k), Image.NEAREST)


def gifs(s, out):
    n = s.frames("pump-north")
    made = []
    for gas, tint in TINTS:
        frames = []
        for i in range(12):                                   # half a second stopped
            frames.append(("idle (stopped: frame 0, glass dark)", [scene(s, d, 0) for d in DIRS]))
        for loop in range(3):
            for f in range(n):
                frames.append((f"working, {gas} (frame {f:02d}/{n})", [scene(s, d, f, tint) for d in DIRS]))
        for k in (1, 2):
            ims = [label(up(row(p), k), t) for t, p in frames]
            pal = ims[len(ims) // 2].convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT)
            q = [i.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE) for i in ims]
            path = os.path.join(out, f"gas-pump-working-{gas}-{k}x.gif")
            q[0].save(path, save_all=True, append_images=q[1:], duration=40, loop=0, optimize=False, disposal=1)
            made.append((path, os.path.getsize(path), ims[0].size, len(ims)))
    return made


def crop_at(im, cx, cy, w, h):
    """A window of a scene, centred (cx, cy) tiles from the entity's origin."""
    o = TILES * PPT / 2
    return im.crop((round(o + cx * PPT - w / 2), round(o + cy * PPT - h / 2),
                    round(o + cx * PPT + w / 2), round(o + cy * PPT + h / 2)))


def sheet(s, out, r13=None):
    n = s.frames("pump-north")
    sid = TINTS[0][1]
    parts = []
    # 1. beside the signed-off round 13, the same ground and scale, 2x: idle and working
    top = []
    if r13 is not None:
        top.append(label(up(scene(r13, "north", 0, None, moving=False), 2), "round 13 (signed off), idle"))
        top.append(label(up(scene(r13, "north", 0, sid, moving=False), 2), "round 13, working (siderane)"))
    top.append(label(up(scene(s, "north", 0), 2), "new: idle (stopped, frame 0), 2x"))
    top.append(label(up(scene(s, "north", n // 2, sid), 2), f"new: working, frame {n // 2} (siderane)"))
    parts.append(row(top))
    # 2. the stroke's key frames at 4x round the compressor's roof and the gauge, siderane glass
    keys = list(range(0, n, max(1, n // 8)))
    parts.append(row([label(up(crop_at(scene(s, "north", f, sid), 0.43, -0.37, 80, 36), 4), f"frame {f:02d}")
                      for f in keys]))
    # 3. the same at 1x, unzoomed: what the player sees
    parts.append(row([label(up(crop_at(scene(s, "north", f, sid), 0.3, -0.3, 150, 110), 2), f"{f:02d} at 1x, shown 2x")
                      for f in keys]))
    # 4. the glass's key frames at 4x, helium-3 and siderane
    for gas, tint in TINTS:
        parts.append(row([label(up(crop_at(scene(s, "north", f, tint), -0.13, -0.74, 40, 24), 4),
                                f"{gas} glass {f:02d}") for f in keys]))
    # 5. every direction, stopped and mid-stroke, 1x and 2x
    parts.append(row([label(up(scene(s, d, f, sid if f else None), 2), f"{d}, {'idle' if f == 0 else f'frame {f}'}")
                      for d in DIRS for f in (0, n // 2)]))
    o = column(parts)
    path = os.path.join(out, "review-animation.png")
    o.save(path)
    return path, o.size


def main():
    args = sys.argv[1:]
    r13 = None
    if "--r13" in args:
        i = args.index("--r13")
        r13 = Sheets(args[i + 1])
        del args[i:i + 2]
    if len(args) != 2:
        sys.exit("usage: animation_review.py <sheets-dir> <out-dir> [--r13 <round 13 sheets-dir>]")
    s = Sheets(args[0])
    os.makedirs(args[1], exist_ok=True)
    print("sheet", *sheet(s, args[1], r13))
    for path, size, dims, count in gifs(s, args[1]):
        print(f"gif {path} {size / 1e6:.2f} MB {dims[0]}x{dims[1]} {count} frames")


if __name__ == "__main__":
    main()
