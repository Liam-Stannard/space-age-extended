#!/usr/bin/env python3
"""Paint an additive glow into a recessed ring already drawn on a plate.

The normal way to get a glow is to difference a lit render against its unlit
twin -- `derive-glow.py`, and template Appendix C is emphatic that you should
not ask a generator for "just the light on transparency", because it invents
geometry that will not line up with the plate.

This is not that. It does not invent anything: it *finds* the ring the plate
already has, by searching for the darkest closed ellipse on the building's
upper face, and lights exactly those pixels. Registration is by construction --
the light is placed on the plate's own groove, in the plate's own canvas.

It exists because the superconducting store's lit twin could not be got out of
the image editor: five rounds in, the "make the ring glow" edit kept returning
the unlit image pixel-identical. Differencing is still the right first choice
for anything whose light is a shape rather than a curve. Use this only when the
lit twin will not come, and only for a channel that really is a ring.

Usage:
  tools/ring-glow.py graphics/entity/superconducting-store/base.png \\
      --out graphics/entity/superconducting-store/glow.png \\
      --inner "#9FC4E8" --core "#E8F4FF"
"""

import argparse
import math

from PIL import Image, ImageDraw, ImageFilter


def luminance(p):
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]


def find_ring(im, samples=96, min_hit=0.94):
    """The darkest closed ellipse on the plate: (cx, cy, rx, ry).

    Searched rather than fitted. A recessed channel is the darkest thing on an
    otherwise lit upper face, so the ellipse whose circumference has the lowest
    mean luminance is the channel -- and requiring nearly every sample to land
    on opaque pixels keeps the search from wandering off the silhouette.
    """
    px = im.load()
    w, h = im.size
    ring = None
    xs = range(int(w * 0.35), int(w * 0.65), 2)
    ys = range(int(h * 0.15), int(h * 0.45), 2)
    for cx in xs:
        for cy in ys:
            for ry in range(int(h * 0.07), int(h * 0.22)):
                for rx in range(int(w * 0.13), int(w * 0.32)):
                    tot = n = 0
                    for k in range(samples):
                        t = 2 * math.pi * k / samples
                        x = int(round(cx + rx * math.cos(t)))
                        y = int(round(cy + ry * math.sin(t)))
                        if 0 <= x < w and 0 <= y < h and px[x, y][3] > 200:
                            tot += luminance(px[x, y])
                            n += 1
                    if n >= samples * min_hit:
                        mean = tot / n
                        if ring is None or mean < ring[0]:
                            ring = (mean, cx, cy, rx, ry)
    return ring


def paint(size, ring, inner, core, width, bloom):
    """Two strokes and a blur: a bright core inside a wider, softer band."""
    _, cx, cy, rx, ry = ring
    halo = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(halo)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
              outline=inner + (255,), width=max(2, width + 2))
    halo = halo.filter(ImageFilter.GaussianBlur(bloom))

    hot = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(hot)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
              outline=core + (255,), width=width)
    hot = hot.filter(ImageFilter.GaussianBlur(max(0.5, bloom / 3)))

    glow = halo
    glow.alpha_composite(hot)
    return glow


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plate")
    ap.add_argument("--out", required=True)
    ap.add_argument("--inner", default="#9FC4E8")
    ap.add_argument("--core", default="#E8F4FF")
    ap.add_argument("--width", type=int, default=2)
    ap.add_argument("--bloom", type=float, default=2.2)
    args = ap.parse_args()

    im = Image.open(args.plate).convert("RGBA")
    ring = find_ring(im)
    if not ring:
        raise SystemExit("no closed ring found on this plate")
    mean, cx, cy, rx, ry = ring
    print(f"  ring found at ({cx}, {cy}) radii {rx}x{ry}, "
          f"channel mean luminance {mean:.1f}")

    rgb = lambda s: tuple(int(s.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    glow = paint(im.size, ring, rgb(args.inner), rgb(args.core),
                 args.width, args.bloom)

    # Light only where the building is, so the bloom cannot spill off the
    # silhouette into open ground -- the same rule derive-glow.py applies.
    keep = im.getchannel("A").filter(ImageFilter.MaxFilter(3))
    glow.putalpha(Image.composite(glow.getchannel("A"),
                                  Image.new("L", im.size, 0), keep))
    glow.save(args.out)

    a = glow.getchannel("A")
    hist = a.histogram()
    total = im.width * im.height
    print(f"  ok  {args.out}  {im.width}×{im.height}")
    print(f"      mean light {sum(i * n for i, n in enumerate(hist)) / total:.1f}"
          f"/255 · covers {sum(hist[9:]) / total:.1%} of the canvas")


if __name__ == "__main__":
    main()
