#!/usr/bin/env python3
"""Review sheet and measures for technology icons (480x256 strips).

  python3 concept/technology/tech_review_sheet.py <sheet-dir> label=strip.png ...

Draws each strip's 256, 128 and 64 levels on the technology screen's slot colour
and on the review ground, beside Space Age's technology icons (VANILLA), and
writes <sheet-dir>/tech-review.png and <sheet-dir>/tech-measures.json:

  strip      size and mode (480x256 RGBA), nothing outside the four levels
  framing    opaque (alpha > 200) bounding box at 256, share of the canvas
  tonal      p5/p50/p95 luminance of the opaque pixels at 256
  shadow     part-transparent dark pixels (8 < alpha <= 200, luminance < 40) at 256
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

SA = "/home/liam-stannard/.steam/steam/steamapps/common/Factorio/data/space-age/graphics/technology"
VANILLA = ["foundry", "cryogenic-plant", "big-mining-drill", "electromagnetic-plant", "holmium-processing",
           "lithium-processing", "tungsten-carbide", "carbon-fiber"]
LEVELS = ((256, 0), (128, 256), (64, 384), (32, 448))
SLOT = (45, 44, 45, 255)
GROUND = (74, 66, 58, 255)
INK = (220, 214, 200, 255)


def font(n):
    try:
        return ImageFont.load_default(size=n)
    except TypeError:
        return ImageFont.load_default()


def levels(p):
    im = Image.open(p).convert("RGBA")
    return {s: im.crop((o, 0, o + s, s)) for s, o in LEVELS}


def lum(p):
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


def measure(p):
    raw = Image.open(p)
    lv = levels(p)
    im = lv[256]
    px = list(im.get_flattened_data())
    a = im.getchannel("A")
    bo = a.point(lambda v: 255 if v > 200 else 0).getbbox()
    op = sorted(lum(q) for q in px if q[3] > 200)
    semi_dark = sum(1 for q in px if 8 < q[3] <= 200 and lum(q) < 40)
    full = raw.convert("RGBA").getchannel("A").load()
    outside = sum(1 for x in range(raw.width) for y in range(raw.height)
                  if full[x, y] and not any(o <= x < o + s and y < s for s, o in LEVELS))
    q = lambda f: round(op[int(f * (len(op) - 1))])
    return {"strip": {"size": list(raw.size), "mode": raw.mode, "alpha_outside_levels": outside},
            "framing": {"opaque_bbox_w": bo[2] - bo[0], "opaque_bbox_h": bo[3] - bo[1],
                        "share": round(len(op) / 65536, 3)},
            "tonal": {"p5": q(.05), "p50": q(.5), "p95": q(.95)}, "shadow_px": semi_dark}


def sheet(cols, path):
    cw, gap = 256 + 128 + 64 + 40, 16
    rows = (("technology slot", SLOT), ("ground", GROUND))
    W = gap + len(cols) * (cw + gap)
    H = 50 + len(rows) * (256 + 44) + 10
    im = Image.new("RGBA", (W, H), (28, 27, 26, 255))
    d = ImageDraw.Draw(im)
    d.text((gap, 10), "Technology icons: ours, then Space Age's -- 256, 128, 64 each (1x); "
           "top on the slot #2D2C2D, below on the ground #4A423A", font=font(18), fill=INK)
    for r, (lab, bg) in enumerate(rows):
        y = 50 + r * (256 + 44)
        for c, (name, lv) in enumerate(cols):
            x = gap + c * (cw + gap)
            d.text((x, y), name, font=font(13), fill=INK)
            panel = Image.new("RGBA", (cw, 256), bg)
            xx = 0
            for s in (256, 128, 64):
                panel.alpha_composite(lv[s], (xx, 256 - s))
                xx += s + 20
            im.alpha_composite(panel, (x, y + 20))
    im.save(path)


def main(argv):
    dest, specs = argv[0], argv[1:]
    os.makedirs(dest, exist_ok=True)
    ours = [(lab, p) for lab, _, p in (s.partition("=") for s in specs)]
    van = [(n, f"{SA}/{n}.png") for n in VANILLA]
    sheet([(l, levels(p)) for l, p in ours + van], os.path.join(dest, "tech-review.png"))
    res = {"ours": {l: measure(p) for l, p in ours}, "vanilla": {l: measure(p) for l, p in van}}
    vr = res["vanilla"].values()
    res["vanilla_range"] = {k: [min(f(v) for v in vr), max(f(v) for v in vr)] for k, f in (
        ("opaque_long_side", lambda v: max(v["framing"]["opaque_bbox_w"], v["framing"]["opaque_bbox_h"])),
        ("share", lambda v: v["framing"]["share"]), ("p50", lambda v: v["tonal"]["p50"]),
        ("p95", lambda v: v["tonal"]["p95"]), ("shadow_px", lambda v: v["shadow_px"]))}
    json.dump(res, open(os.path.join(dest, "tech-measures.json"), "w"), indent=1)
    print("vanilla range:", json.dumps(res["vanilla_range"]))
    for l, m in res["ours"].items():
        f, t = m["framing"], m["tonal"]
        print(f"{l:32s} {m['strip']['size']} {m['strip']['mode']} outside {m['strip']['alpha_outside_levels']} | "
              f"opaque {f['opaque_bbox_w']}x{f['opaque_bbox_h']} share {f['share']} | p50 {t['p50']} p95 {t['p95']} | "
              f"shadow {m['shadow_px']}")


if __name__ == "__main__":
    main(sys.argv[1:])
