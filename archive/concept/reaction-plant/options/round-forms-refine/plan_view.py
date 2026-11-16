#!/usr/bin/env python3
"""T06h: a tuning aid, not a measure -- forms.py --plan's plan.json drawn from above: every part's footprint
shaded by how high its top stands (the building's own parts in blue outline), on a 0.1-tile grid.

  python3 plan_view.py <plan.json> <out.png> [--min-top Z]
"""
import json
import sys

from PIL import Image, ImageDraw

items = json.load(open(sys.argv[1]))
mt = float(sys.argv[sys.argv.index("--min-top") + 1]) if "--min-top" in sys.argv else -1
S, C = 160, 480
img = Image.new("RGB", (2 * C, 2 * C), (24, 24, 24))
d = ImageDraw.Draw(img)


def px(x, y):
    return (C + x * S, C - y * S)


for i in range(-25, 26):
    c = (110, 110, 110) if i % 5 == 0 else (45, 45, 45)
    d.line([px(i / 10, -2.5), px(i / 10, 2.5)], fill=c)
    d.line([px(-2.5, i / 10), px(2.5, i / 10)], fill=c)
for it in sorted(items, key=lambda t: t["top"]):
    h = it["hull"]
    if len(h) < 3 or it["top"] < mt:
        continue
    if it["building"]:
        d.polygon([px(*p) for p in h], outline=(90, 160, 220))
    else:
        g = int(60 + min(195, it["top"] * 60))
        d.polygon([px(*p) for p in h], fill=(g, int(g * 0.85), int(g * 0.6)), outline=(20, 20, 20))
for i in range(-25, 26, 5):
    d.text(px(i / 10, -2.5), f"{i / 10:+.1f}", fill=(220, 220, 120))
    d.text(px(-2.5, i / 10), f"{i / 10:+.1f}", fill=(220, 220, 120))
img.save(sys.argv[2])
