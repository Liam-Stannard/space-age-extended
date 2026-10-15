#!/usr/bin/env python3
"""The radiant pool in look B (radiant-look, Liam 2026-10-12): a dark liquid lit from below.

  python3 pool_look_b.py <space-age graphics/terrain dir> <out-dir>

Today's pool sheets are Vulcanus's lava art with the hue turned 200 deg
(tools/build-crust-glow-tile.py): every value kept, so the melt's bright orange
became a bright mid-blue leaning cyan, the dark crust stayed grey, and the whole
surface reads as flat blue paint. Here the same vanilla sheets are re-graded
instead of rotated, by how hot each pixel is:

  heat     (R + 2G) / 3 of the lava pixel: dark crust ~0.1, red melt ~0.35,
           orange ~0.6, yellow core ~0.9 -- the order the lava's light runs in
  melt     the pixel's saturation (soft, 0.25 -> 0.55): melt is coloured, crust grey
  paint    melt pixels take B's plate ramp on heat, #02081A > #04103A > #0B2A8C >
           #1F63FF > #5A9CFF (B's glow ramp's top: no pale cyan, nothing white);
           crust pixels become dark sediment, #07090E -> #1C2029 by their own
           luminance, a cool near-black: the silhouettes in the light
  light    the light sheets (the shore's and the lip's) are the melt
           alone on B's glow ramp, #000000 > #04103A > #0B2A8C > #1F63FF >
           #5A9CFF, weighted by heat so only the hot cores carry light at night

Every pixel is mapped on its own (no large-scale shading), so the sheets tile
and seam exactly as vanilla's do; the "deeper basin" has to come from the
shader's motion and the lip, not from the sheet.

Writes, into <out-dir>:
  pool.png                     from vulcanus/lava-hot.png (the pool tile's sheet)
  effect.png                   from vulcanus/lava-textures/lava.png (the shader's colour texture)
  shore.png, shore-light.png   from vulcanus/lava.png (the cooler crust the shore wears)
  lip.png, lip-light.png       from lava-transitions/lava-stone.png and its lightmap
effect-noise.png is lava's noise texture, unchanged, as today.
"""
import os
import sys

from PIL import Image

PLATE = [(0.0, "#02081A"), (0.22, "#04103A"), (0.45, "#0B2A8C"), (0.72, "#1F63FF"), (1.0, "#5A9CFF")]
GLOW = [(0.0, "#000000"), (0.25, "#04103A"), (0.5, "#0B2A8C"), (0.78, "#1F63FF"), (1.0, "#5A9CFF")]
SED = ("#07090E", "#1C2029")
ROCK = ("#16181E", "#4A4D55")     # the shore's crust plates: the Core's slate, cool and dark


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def lut(stops, gamma=1.0):
    out = []
    pts = [(p, hexrgb(h)) for p, h in stops]
    for i in range(256):
        t = (i / 255) ** gamma
        for (p0, c0), (p1, c1) in zip(pts, pts[1:]):
            if t <= p1:
                k = (t - p0) / (p1 - p0) if p1 > p0 else 0
                out.append(tuple(round(a + (b - a) * k) for a, b in zip(c0, c1)))
                break
        else:
            out.append(pts[-1][1])
    return out


def smooth(x, a, b):
    if x <= a:
        return 0.0
    if x >= b:
        return 1.0
    t = (x - a) / (b - a)
    return t * t * (3 - 2 * t)


def grade(src, out, light_out=None, heat_lo=0.12, heat_hi=0.95, plate_gamma=1.0, light_gain=1.0,
          light_floor=0.30, sed=SED):
    """Re-grade one lava sheet into look B: the paint, and optionally its light sheet."""
    im = Image.open(src).convert("RGBA")
    px = im.load()
    W, H = im.size
    P, G = lut(PLATE, plate_gamma), lut(GLOW)
    s0, s1 = hexrgb(sed[0]), hexrgb(sed[1])
    paint = Image.new("RGBA", im.size)
    pp = paint.load()
    light = Image.new("RGBA", im.size) if light_out else None
    lp = light.load() if light else None
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a == 0:
                pp[x, y] = (0, 0, 0, 0)
                if lp:
                    lp[x, y] = (0, 0, 0, 0)
                continue
            mx, mn = max(r, g, b), min(r, g, b)
            sat = 0.0 if mx == 0 else (mx - mn) / mx
            heat = (r + 2 * g) / 765.0
            t = min(1.0, max(0.0, (heat - heat_lo) / (heat_hi - heat_lo)))
            melt = smooth(sat, 0.25, 0.55) * smooth(mx / 255, 0.18, 0.40)
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            sk = min(1.0, lum / 0.45)
            sedc = tuple(c0 + (c1 - c0) * sk for c0, c1 in zip(s0, s1))
            mc = P[int(t * 255)]
            c = tuple(round(sc + (m - sc) * melt) for sc, m in zip(sedc, mc))
            pp[x, y] = c + (a,)
            if lp:
                lt = max(0.0, (t - light_floor) / (1 - light_floor)) * melt * light_gain
                gc = G[min(255, int(min(1.0, lt) * 255))]
                lp[x, y] = gc + (a,)
    paint.save(out, optimize=True)
    if light:
        light.save(light_out, optimize=True)


def grade_lightmap(src, out):
    """A vanilla lightmap (warm light on black) onto B's glow ramp by its luminance."""
    im = Image.open(src).convert("RGBA")
    G = lut(GLOW)
    r, g, b, a = im.split()
    L = Image.merge("RGB", (r, g, b)).convert("L")
    rgb = Image.merge("RGB", [L.point(lambda v, i=i: G[v][i]) for i in range(3)])
    rgb.putalpha(a)
    rgb.save(out, optimize=True)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    T, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    j = lambda *p: os.path.join(*p)  # noqa: E731
    # round 2 (client round 1: pool L 35 by day, p50 23 -- near black; shore L 20, its crust
    # lost into the sediment): the melt's ramp lifted (gamma 0.8), the light from lower
    # heat, and the shore's and lip's crust a cool dark rock rather than the pool's sediment
    # (a pool-light.png was made here too; a light layer on the pool tile draws nothing under
    # the lava shader -- measured in a client, with and without -- so it is not written)
    grade(j(T, "vulcanus", "lava-hot.png"), j(out, "pool.png"), plate_gamma=0.8)
    grade(j(T, "vulcanus", "lava-textures", "lava.png"), j(out, "effect.png"), plate_gamma=0.8)
    grade(j(T, "vulcanus", "lava.png"), j(out, "shore.png"), j(out, "shore-light.png"),
          plate_gamma=0.85, light_floor=0.0, light_gain=2.6, sed=ROCK)   # night L 12 at gain 1.2, 13.7 at 1.7
    grade(j(T, "lava-transitions", "lava-stone.png"), j(out, "lip.png"), sed=ROCK)
    grade_lightmap(j(T, "lava-transitions", "lava-stone-lightmap.png"), j(out, "lip-light.png"))
    for f in sorted(os.listdir(out)):
        print(" ", j(out, f), Image.open(j(out, f)).size)


if __name__ == "__main__":
    main()
