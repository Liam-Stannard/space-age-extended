#!/usr/bin/env python3
"""Vent Pump, round 5 (T05): the highlight shoulder on the rendered frames.

  python3 vp5_shoulder.py <render-dir> [--knee 220] [--top 246]

The clipping fixes in the model (vpb5_kit.py: satin bare steel and nickel, the melt's crest #F89A50
under a lower glow, the brightest paints a step down, the windows' gloss lower) take nearly all of
it; what is left is the sun's specular glint on a few px of metal. This rolls a px off when its brightest channel passes `knee`, scaling the whole px so that channel
lands under `top` (m' = knee + (top - knee) * (1 - exp(-(m - knee) / (top - knee)))): hue and
saturation kept, below the knee the frame is untouched (the midtones, p50, are the same). Every PNG in the folder is
rolled off once (a marker file records it) except hemask.png, the glass's mask.

Before rolling off, each frame's white (alpha >= 8, every channel >= 250) and clipped (alpha >= 8, any
channel 255) px are counted at 4x, 2x and 1x (premultiplied LANCZOS, the fog under alpha 24 cut, as
vp5_sheet.py) into raw_wc.json: what the model alone gives, reported beside the rolled-off figures.
"""
import argparse
import glob
import json
import math
import os

from PIL import Image, ImageChops

ap = argparse.ArgumentParser()
ap.add_argument("dir")
ap.add_argument("--knee", type=float, default=236)
ap.add_argument("--top", type=float, default=250)
a = ap.parse_args()
mark = os.path.join(a.dir, "shoulder.done")
if os.path.exists(mark):
    raise SystemExit(f"already rolled off: {open(mark).read().strip()}")
K, T = a.knee, a.top


def f(v):
    return v if v <= K else K + (T - K) * (1 - math.exp(-(v - K) / (T - K)))




def wc(im):
    r, g, b, al = im.split()
    op = al.point(lambda v: 255 if v >= 8 else 0)
    hi = [c.point(lambda v: 255 if v >= 250 else 0) for c in (r, g, b)]
    top = [c.point(lambda v: 255 if v == 255 else 0) for c in (r, g, b)]
    w = ImageChops.multiply(ImageChops.multiply(ImageChops.multiply(hi[0], hi[1]), hi[2]), op)
    c = ImageChops.multiply(ImageChops.lighter(ImageChops.lighter(top[0], top[1]), top[2]), op)
    return [w.histogram()[255], c.histogram()[255]]


def scales(path):
    im = Image.open(path).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    out = {"4x": wc(im)}
    for k in (2, 1):
        out[f"{k}x"] = wc(im.convert("RGBa").resize((352 * k, 352 * k), Image.LANCZOS)
                          .convert("RGBA"))
    return out


raw = {}
for p in sorted(glob.glob(os.path.join(a.dir, "*.png"))):
    if os.path.basename(p) != "hemask.png":
        raw[os.path.basename(p)] = scales(p)
tot = {k: [sum(v[k][0] for v in raw.values()), sum(v[k][1] for v in raw.values())] for k in ("4x", "2x", "1x")}
json.dump(dict(total=tot, frames=raw), open(os.path.join(a.dir, "raw_wc.json"), "w"), indent=1)
print("raw white / clipped:", tot)

n = 0
for p in sorted(glob.glob(os.path.join(a.dir, "*.png"))):
    if os.path.basename(p) == "hemask.png":
        continue
    im = Image.open(p)
    mode = im.mode
    im = im.convert("RGBA")
    px = im.load()
    W, H = im.size
    for y in range(H):
        for x in range(W):
            r, g, b, al = px[x, y]
            m = max(r, g, b)
            if m > K:
                k = f(m) / m              # the whole px scaled: hue and saturation kept
                px[x, y] = (round(r * k), round(g * k), round(b * k), al)
    im.save(p)
    n += 1
open(mark, "w").write(f"knee {K} top {T}, {n} frames\n")
print(f"{n} frames rolled off above {K} to under {T}")
