#!/usr/bin/env python3
"""Review sheet and measures for item icons rendered by tools/blender/render-icons.sh.

  python3 concept/items/review_sheet.py <render-out-dir> <sheet-dir> [item ...]

Writes into <sheet-dir>:
  review.png            every icon at 64/32/16/8 px, at 4x and at 1x, on the
                        inventory slot and on the ground, both finishes, beside
                        the vanilla analogues at the same sizes; and the items as
                        a recipe tooltip row
  review-downscale.png  per-size renders against "the 64 rendered once and shrunk",
                        32/16/8 at 4x and 1x, on the slot
  measures.json         the pass criteria, measured (printed too)

Backgrounds: the slot is core/graphics/gui-new.png's inventory slot face (style
"slot", {0, 424}: #2D2C2D); the ground is the buildings' review ground (#4A423A).
"""
import itertools
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

VANILLA = "/home/liam-stannard/.steam/steam/steamapps/common/Factorio/data"
# the task's analogues: iron ore, iron plate, stone, and Space Age's crushed and
# powdered items -- tungsten ore, carbon; holmium powder is not a vanilla item
# (Space Age ships holmium ore and holmium plate), so holmium ore stands in
ANALOGUES = [("iron-ore", "base"), ("iron-plate", "base"), ("stone", "base"),
             ("tungsten-ore", "space-age"), ("holmium-ore", "space-age"), ("carbon", "space-age")]
SLOT = (45, 44, 45, 255)
GROUND = (74, 66, 58, 255)
SIZES = (64, 32, 16, 8)
OFFS = (0, 64, 96, 112)
INK = (220, 214, 200, 255)
DIM = (150, 144, 132, 255)


def font(n):
    try:
        return ImageFont.load_default(size=n)
    except TypeError:
        return ImageFont.load_default()


def levels(strip):
    im = Image.open(strip).convert("RGBA")
    return {s: im.crop((o, 0, o + s, s)) for s, o in zip(SIZES, OFFS)}


def lum(p):
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


# ---------------------------------------------------------------- measures

def framing(im):
    a = im.getchannel("A")
    bb = a.point(lambda v: 255 if v else 0).getbbox()
    share = sum(1 for v in a.get_flattened_data() if v > 127) / (im.width * im.height)
    return {"share": round(share, 3), "bbox_w": bb[2] - bb[0], "bbox_h": bb[3] - bb[1], "bbox": list(bb)}


def tonal(im):
    L = sorted(lum(p) for p in im.get_flattened_data() if p[3] > 200)
    q = lambda f: round(L[int(f * (len(L) - 1))])
    return {"p5": q(.05), "p50": q(.5), "p95": q(.95)}


def edge_contrast(im, bg):
    """Mean |L| step from the outline's pixels (alpha >= 128 with a 4-neighbour below
    128) composited on bg, to bg; and the share of them stepping at least 16."""
    w, h = im.size
    px = im.load()
    Lb = lum(bg)
    steps = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            if all(0 <= x + dx < w and 0 <= y + dy < h and px[x + dx, y + dy][3] >= 128
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                continue
            k = a / 255
            c = [k * v + (1 - k) * bv for v, bv in zip((r, g, b), bg)]
            steps.append(abs(lum(c) - Lb))
    if not steps:
        return {"mean": 0, "share16": 0}
    return {"mean": round(sum(steps) / len(steps), 1), "share16": round(sum(s >= 16 for s in steps) / len(steps), 2)}


def strays(im):
    w, h = im.size
    a = im.getchannel("A").load()
    out = {}
    for name, t in (("any_alpha", 1), ("opaque", 128)):
        n = 0
        for y in range(h):
            for x in range(w):
                if a[x, y] >= t and not any(a[x + dx, y + dy] >= t for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                                             if (dx or dy) and 0 <= x + dx < w and 0 <= y + dy < h):
                    n += 1
        out[name] = n
    return out


def on(im, bg):
    c = Image.new("RGBA", im.size, bg)
    c.alpha_composite(im)
    return c


def diff(a, b, bg=SLOT):
    """Mean |RGB| difference per pixel, both composited on the slot, over the pixels
    either covers."""
    A, B = on(a, bg).load(), on(b, bg).load()
    aa, ba = a.getchannel("A").load(), b.getchannel("A").load()
    tot = n = 0
    for y in range(a.height):
        for x in range(a.width):
            if aa[x, y] or ba[x, y]:
                tot += sum(abs(A[x, y][i] - B[x, y][i]) for i in range(3)) / 3
                n += 1
    return round(tot / max(n, 1), 1)


def strip_check(path):
    im = Image.open(path)
    lv = levels(path)
    clear = all(l.getchannel("A").getbbox() is None or
                (lambda bb, s: bb[0] >= 1 and bb[1] >= 1 and bb[2] <= s - 1 and bb[3] <= s - 1)(
                    l.getchannel("A").getbbox(), l.width) for l in lv.values())
    # nothing outside the four levels' squares
    a = im.convert("RGBA").getchannel("A")
    outside = 0
    ap = a.load()
    for x in range(im.width):
        for y in range(im.height):
            inside = any(o <= x < o + s and y < s for s, o in zip(SIZES, OFFS))
            if not inside and ap[x, y]:
                outside += 1
    return {"size": list(im.size), "mode": im.mode, "edge_clear": clear, "alpha_outside_levels": outside}


def measure(out, items, finishes):
    van = {n: levels(f"{VANILLA}/{m}/graphics/icons/{n}.png") for n, m in ANALOGUES}
    res = {"vanilla": {}, "ours": {}, "downscale": {}, "pairwise": {}}
    for n, lv in van.items():
        res["vanilla"][n] = {"framing": framing(lv[64]), "tonal": tonal(lv[64]),
                             "edge_slot": edge_contrast(lv[64], SLOT), "edge_ground": edge_contrast(lv[64], GROUND)}
    vr = res["vanilla"].values()
    rng = lambda f: [min(f(v) for v in vr), max(f(v) for v in vr)]
    res["vanilla_range"] = {
        "share": rng(lambda v: v["framing"]["share"]), "bbox_w": rng(lambda v: v["framing"]["bbox_w"]),
        "bbox_h": rng(lambda v: v["framing"]["bbox_h"]), "p50": rng(lambda v: v["tonal"]["p50"]),
        "p95": rng(lambda v: v["tonal"]["p95"]), "edge_slot": rng(lambda v: v["edge_slot"]["mean"]),
        "edge_ground": rng(lambda v: v["edge_ground"]["mean"])}
    for kind, root in (("ours", "strips"), ("downscale", "strips-downscale")):
        for fin in finishes:
            for it in items:
                p = os.path.join(out, root, fin, it + ".png")
                lv = levels(p)
                res[kind][f"{fin}/{it}"] = {
                    "strip": strip_check(p), "framing": framing(lv[64]), "tonal": tonal(lv[64]),
                    "edge_slot": edge_contrast(lv[64], SLOT), "edge_ground": edge_contrast(lv[64], GROUND),
                    "edge_slot_16": edge_contrast(lv[16], SLOT), "edge_ground_16": edge_contrast(lv[16], GROUND),
                    "strays": {s: strays(lv[s]) for s in (32, 16, 8)}}
            for s in (16, 8):
                lv = {it: levels(os.path.join(out, root, fin, it + ".png"))[s] for it in items}
                res["pairwise"][f"{kind}/{fin}/{s}"] = {f"{a}~{b}": diff(lv[a], lv[b])
                                                        for a, b in itertools.combinations(items, 2)}
    for s in (16, 8):
        res["pairwise"][f"vanilla/{s}"] = {f"{a}~{b}": diff(van[a][s], van[b][s])
                                           for a, b in itertools.combinations(van, 2)}
    return res


# ---------------------------------------------------------------- sheets

def label(d, xy, text, size=14, fill=INK):
    d.text(xy, text, font=font(size), fill=fill)


def column(icons, bg, scales=(4, 1)):
    """One icon's sizes: each at 4x stacked, then the four at 1x in a row."""
    rows = [(s, 4) for s in SIZES] + [("1x", 1)]
    h = sum(s * 4 + 8 for s in SIZES) + 64 + 8
    col = Image.new("RGBA", (256, h), bg)
    y = 0
    for s in SIZES:
        col.alpha_composite(icons[s].resize((s * 4, s * 4), Image.NEAREST), ((256 - s * 4) // 2, y))
        y += s * 4 + 8
    x = 0
    for s in SIZES:
        col.alpha_composite(icons[s], (x + 8, y + (64 - s) // 2))
        x += s + 16
    return col


def review(out, items, finishes, path):
    van = [(n, levels(f"{VANILLA}/{m}/graphics/icons/{n}.png")) for n, m in ANALOGUES]
    ours = [(f"{it}\n{fin}", levels(os.path.join(out, "strips", fin, it + ".png")))
            for fin in finishes for it in items]
    cols = ours + van
    gap, head = 14, 62
    sample = column(cols[0][1], SLOT)
    W = len(cols) * (256 + gap) + gap + 30
    H = 40 + 2 * (head + sample.height + gap) + 330
    sheet = Image.new("RGBA", (W, H), (28, 27, 26, 255))
    d = ImageDraw.Draw(sheet)
    label(d, (gap, 10), "Kamacite item icons -- each column: 64, 32, 16, 8 px at 4x, then all four at 1x. "
          "Left: signature finish, then neutral, then vanilla analogues. Top: inventory slot #2D2C2D; "
          "below: ground #4A423A", 18)
    y = 40
    for bgname, bg in (("on the inventory slot", SLOT), ("on the ground", GROUND)):
        label(d, (gap, y + 4), bgname, 16, DIM)
        for i, (name, lv) in enumerate(cols):
            x = gap + i * (256 + gap)
            label(d, (x, y + 24), name, 13)
            sheet.alpha_composite(column(lv, bg), (x, y + head))
        y += head + sample.height + gap
    # the tooltip row: the four as a recipe chain, at 32 px (a tooltip's icon size) 1x and 4x
    label(d, (gap, y + 4), "as a recipe tooltip: ore -> crushed + fines -> plate (32 px; 1x, then 4x)", 16, DIM)
    y += 28
    for fi, fin in enumerate(finishes):
        x0 = gap + fi * (W // 2)
        label(d, (x0, y), fin, 14)
        lv = [levels(os.path.join(out, "strips", fin, it + ".png"))[32] for it in items]
        for k, scale in ((0, 1), (1, 4)):
            yy = y + 20 + (0 if k == 0 else 50)
            tip = Image.new("RGBA", ((32 * scale + 30 * scale // 2) * len(lv) + 20, 32 * scale + 12), (49, 48, 49, 255))
            td = ImageDraw.Draw(tip)
            xx = 6
            for j, icon in enumerate(lv):
                tip.alpha_composite(icon.resize((32 * scale, 32 * scale), Image.NEAREST), (xx, 6))
                xx += 32 * scale
                if j < len(lv) - 1:
                    td.text((xx + 2 * scale, 6 + 10 * scale), "->" if j != 1 else "+", font=font(8 * scale + 4), fill=INK)
                    xx += 30 * scale // 2
            sheet.alpha_composite(tip, (x0, yy))
    sheet.save(path)


def review_downscale(out, items, finishes, path):
    """Per-size against the 64 shrunk, 32/16/8 at 4x and 1x, on the slot."""
    gap = 12
    rows = [(fin, it) for fin in finishes for it in items]
    cw = 128 + 64 + 32 + 3 * 8 + 32 + 16 + 8 + 30
    W = 200 + 2 * (cw + gap)
    H = 50 + len(rows) * (128 + gap)
    sheet = Image.new("RGBA", (W, H), (28, 27, 26, 255))
    d = ImageDraw.Draw(sheet)
    label(d, (gap, 10), "per-size renders (left) against the 64 rendered once and shrunk (right): 32, 16, 8 at 4x, then 1x", 16)
    for r, (fin, it) in enumerate(rows):
        y = 40 + r * (128 + gap)
        label(d, (gap, y + 50), f"{it}\n{fin}", 13)
        for c, root in enumerate(("strips", "strips-downscale")):
            lv = levels(os.path.join(out, root, fin, it + ".png"))
            panel = Image.new("RGBA", (cw, 128), SLOT)
            x = 4
            for s in (32, 16, 8):
                panel.alpha_composite(lv[s].resize((s * 4, s * 4), Image.NEAREST), (x, (128 - s * 4) // 2))
                x += s * 4 + 8
            for s in (32, 16, 8):
                panel.alpha_composite(lv[s], (x, (128 - s) // 2))
                x += s + 8
            sheet.alpha_composite(panel, (200 + c * (cw + gap), y))
    sheet.save(path)


def main(out, dest, items):
    decl = json.load(open(os.path.join(out, "hi", "icons.json")))
    items = items or decl["items"]
    finishes = decl["finishes"]
    os.makedirs(dest, exist_ok=True)
    review(out, items, finishes, os.path.join(dest, "review.png"))
    review_downscale(out, items, finishes, os.path.join(dest, "review-downscale.png"))
    res = measure(out, items, finishes)
    with open(os.path.join(dest, "measures.json"), "w") as f:
        json.dump(res, f, indent=1)
    vr = res["vanilla_range"]
    print("vanilla range:", json.dumps(vr))
    for kind in ("ours", "downscale"):
        print(f"--- {kind}")
        for k, v in res[kind].items():
            fr, t = v["framing"], v["tonal"]
            st = v["strays"]
            print(f"{k:34s} strip {v['strip']['size']} {v['strip']['mode']} edge_clear {v['strip']['edge_clear']} | "
                  f"share {fr['share']:.2f} bbox {fr['bbox_w']}x{fr['bbox_h']} | p50 {t['p50']} p95 {t['p95']} | "
                  f"edge slot {v['edge_slot']['mean']} ground {v['edge_ground']['mean']} "
                  f"(16px: {v['edge_slot_16']['mean']}/{v['edge_ground_16']['mean']}) | "
                  f"strays 16 {st[16]['any_alpha']}/{st[16]['opaque']} 8 {st[8]['any_alpha']}/{st[8]['opaque']}")
    for k, v in res["pairwise"].items():
        short = lambda n: n.replace("kamacite-", "").replace("-kamacite", "")
        print(f"pairwise {k:28s} min {min(v.values()):5.1f}  " +
              "  ".join(f"{short(p.split('~')[0])}~{short(p.split('~')[1])} {d}" for p, d in v.items()))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
