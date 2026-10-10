#!/usr/bin/env python3
"""Cue sampler for item icons: the full set beside variants each missing one cue.

  python3 concept/items/sampler_sheet.py <render-out-dir> <sheet-dir> [--candidates]
                                         [--ref LABEL=STRIP_DIR ...]

<render-out-dir> is render-icons.sh's; its icons.json names the finishes. The first
finish is the full set, drawn at 64, 32, 16 and 8 px; every other finish (and each
--ref, e.g. an earlier round's strips) at 64, 32 and 16. Every size at 1x, with 64 at
2x and the smaller sizes at 4x above it. Left panel on the inventory slot, right on
the ground, vanilla's analogues in the last rows.

--candidates (round 3, colour candidates): every row at all four sizes, and below
the panels an inventory row per finish -- its four items in 40 px slots at 32 px,
then vanilla's raw materials, as they would sit in an inventory -- at 1x and 2x.
measures.json then also carries each icon's lit hue and saturation (hues.py) and
its distance to the nearest saturated vanilla raw material or mod fluid.

Writes <sheet-dir>/sampler.png and <sheet-dir>/measures.json: review_sheet.measure's
pass criteria 1-4 for every finish, and "cue_step" -- the mean per-pixel difference
on the slot between the full set and each variant, per item and size: how much a
cue changes the icon at that size (near zero: the cue no longer reads there).
"""
import json
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hues  # noqa: E402
import review_sheet as rs  # noqa: E402

CELL_W, CELL_H = 400, 214
LABEL_W = 170
VANILLA_ROWS = [["iron-ore", "stone", "tungsten-ore", "holmium-ore"], ["iron-plate", "carbon"]]
INVENTORY = [("base", n) for n in ("iron-ore", "copper-ore", "stone", "coal", "uranium-ore", "iron-plate",
                                    "copper-plate", "steel-plate", "sulfur")] + \
            [("space-age", n) for n in ("tungsten-ore", "holmium-ore", "calcite", "scrap", "carbon",
                                         "tungsten-plate", "holmium-plate", "lithium")]


def inventory(rows, items, path_or_none=None):
    """One inventory row per finish: its four, then vanilla's raw materials, each a
    32 px icon in a 40 px slot (the slot sprite's face colour), 1x and 2x."""
    van = [rs.levels(f"{rs.VANILLA}/{m}/graphics/icons/{n}.png")[32] for m, n in INVENTORY]
    out = []
    for lab, strips, sizes in rows:
        ours = [rs.levels(strips[it])[32] for it in items]
        icons = ours + [None] + van
        strip = Image.new("RGBA", (len(icons) * 42, 42), (36, 35, 36, 255))
        for i, ic in enumerate(icons):
            if ic is None:
                continue
            slot = Image.new("RGBA", (40, 40), rs.SLOT)
            slot.alpha_composite(ic, (4, 4))
            strip.alpha_composite(slot, (i * 42 + 1, 1))
        out.append((lab, strip))
    return out


def cell(lv, bg, sizes):
    c = Image.new("RGBA", (CELL_W - 8, CELL_H - 10), bg)
    x = 4
    for s in sizes:
        k = 2 if s == 64 else 4
        c.alpha_composite(lv[s].resize((s * k, s * k), Image.NEAREST), (x, 4 + (128 - s * k)))
        x += s * k + 8
    x = 4
    for s in sizes:
        c.alpha_composite(lv[s], (x, 140 + (64 - s) // 2))
        x += s + 10
    return c


TITLE = "Kamacite icons, round 2: the meteorite cues."


def sampler(rows, items, path, inv=None):
    """rows: [(label, {item: strip path}, sizes)]; inv: inventory() rows, drawn below"""
    van = {n: rs.levels(f"{rs.VANILLA}/{m}/graphics/icons/{n}.png") for n, m in rs.ANALOGUES}
    allrows = [(lab, {it: rs.levels(p) for it, p in strips.items()}, sizes, items) for lab, strips, sizes in rows]
    for vr in VANILLA_ROWS:
        allrows.append(("vanilla", {n: van[n] for n in vr}, rs.SIZES, vr))
    pw = LABEL_W + 4 * CELL_W
    W = 2 * pw + 30
    H = 70 + len(allrows) * CELL_H + 20
    if inv:
        H += 40 + len(inv) * (2 * 42 + 60)
    sheet = Image.new("RGBA", (W, H), (28, 27, 26, 255))
    d = ImageDraw.Draw(sheet)
    rs.label(d, (12, 8), TITLE + " Each cell: 64 at 2x, 32/16(/8) at 4x, "
             "then the same at 1x. Left: inventory slot #2D2C2D; right: ground #4A423A", 18)
    for pi, bg in enumerate((rs.SLOT, rs.GROUND)):
        x0 = 12 + pi * (pw + 6)
        for ci, it in enumerate(items):
            rs.label(d, (x0 + LABEL_W + ci * CELL_W, 44), it, 15)
        for ri, (lab, lv, sizes, names) in enumerate(allrows):
            y = 70 + ri * CELL_H
            rs.label(d, (x0, y + 80), lab, 15)
            for ci, n in enumerate(names):
                sheet.alpha_composite(cell(lv[n], bg, sizes), (x0 + LABEL_W + ci * CELL_W, y))
                if lab == "vanilla":
                    rs.label(d, (x0 + LABEL_W + ci * CELL_W + 230, y + 180), n, 12, rs.DIM)
    if inv:
        y = 70 + len(allrows) * CELL_H + 20
        names = ", ".join(n for m, n in INVENTORY)
        rs.label(d, (12, y), "in an inventory: the four at 32 px in 40 px slots, then vanilla's raw materials ("
                 + names + "); 1x, then 2x", 16, rs.DIM)
        y += 30
        for lab, strip in inv:
            rs.label(d, (12, y + 14), lab, 15)
            sheet.alpha_composite(strip, (LABEL_W + 12, y))
            sheet.alpha_composite(strip.resize((strip.width * 2, strip.height * 2), Image.NEAREST),
                                  (LABEL_W + 12 + strip.width + 30, y))
            y += 2 * 42 + 60
    sheet.save(path)


def main(argv):
    out, dest = argv[0], argv[1]
    cand = "--candidates" in argv
    refs = []
    if "--ref" in argv:
        for a in argv[argv.index("--ref") + 1:]:
            if a.startswith("--"):
                break
            lab, _, p = a.partition("=")
            refs.append((lab, p))
    decl = json.load(open(os.path.join(out, "hi", "icons.json")))
    items, fins = decl["items"], decl["finishes"]
    global TITLE
    if cand:
        TITLE = "Kamacite icons, round 3: colour candidates."
        if len(fins) == 1 and not refs:
            TITLE = f"Kamacite item icons, {fins[0]}."
    os.makedirs(dest, exist_ok=True)
    rows = [(f, {it: os.path.join(out, "strips", f, it + ".png") for it in items},
             rs.SIZES if (i == 0 or cand) else (64, 32, 16)) for i, f in enumerate(fins)]
    rows += [(lab, {it: os.path.join(p, it + ".png") for it in items}, rs.SIZES if cand else (64, 32, 16))
             for lab, p in refs]
    sampler(rows, items, os.path.join(dest, "sampler.png"), inventory(rows, items) if cand else None)
    res = rs.measure(out, items, fins)
    if not cand:
        res["cue_step"] = {}
        for f in fins[1:]:
            for it in items:
                a = rs.levels(os.path.join(out, "strips", fins[0], it + ".png"))
                b = rs.levels(os.path.join(out, "strips", f, it + ".png"))
                res["cue_step"][f"{f}/{it}"] = {s: rs.diff(a[s], b[s]) for s in (64, 32, 16)}
    else:
        table = hues.survey()
        res["hue_survey"] = {n: {"hue": round(h), "sat": round(s, 2)} for n, (h, s) in table.items()}
        res["hues"] = {}
        for lab, strips, sizes in rows:
            for it in items:
                im = Image.open(strips[it])
                h, s = hues.hue_sat(hues.lit(im))
                near = hues.nearest(h, table)
                res["hues"][f"{lab}/{it}"] = {"hue": round(h), "sat": round(s, 2),
                                              "nearest": near[0], "distance": round(near[1])}
    with open(os.path.join(dest, "measures.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print("vanilla range:", json.dumps(res["vanilla_range"]))
    for k, v in res["ours"].items():
        fr, t, st = v["framing"], v["tonal"], v["strays"]
        print(f"{k:36s} {v['strip']['size']} edge_clear {v['strip']['edge_clear']} | share {fr['share']:.2f} "
              f"bbox {fr['bbox_w']}x{fr['bbox_h']} | p50 {t['p50']} p95 {t['p95']} | edge slot "
              f"{v['edge_slot']['mean']} ground {v['edge_ground']['mean']} | strays 32/16/8 "
              f"{st[32]['any_alpha']}/{st[16]['any_alpha']}/{st[8]['any_alpha']}")
    for k, v in res["pairwise"].items():
        if k.startswith("ours/") or k.startswith("vanilla/"):
            print(f"pairwise {k:30s} min {min(v.values()):5.1f}")
    for k, v in res.get("cue_step", {}).items():
        print(f"cue_step {k:40s} 64 {v[64]:5.1f}  32 {v[32]:5.1f}  16 {v[16]:5.1f}")
    for k, v in res.get("hues", {}).items():
        print(f"hue {k:40s} {v['hue']:4d} deg  sat {v['sat']:.2f}  nearest {v['nearest']} ({v['distance']} deg)")


if __name__ == "__main__":
    main(sys.argv[1:])
