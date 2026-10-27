#!/usr/bin/env python3
"""Review sheets for T03g (task ballast-drill-ports): the cast take's cut-back gaps filled.

  python3 gaps_sheet.py <before take dir> <after take dir> <out dir>

<take dir>: a take as take.sh leaves it (plate/sheets, rig/sheets) or as a round keeps it
(plate-sheets, rig-sheets). Writes to <out dir>:
  before-after-phone.png  1080 px wide: per direction, dry then wet (vanilla's covers),
                          T03f (before) beside T03g (after), each 1.5x
  gap-G<n>.png            per gap of gap-list.txt, 4x (nearest, the sprite's own pixels):
                          before beside after, dry and then wet in each direction
  clipping-2x.png         2x (nearest): every wall collar, every buried junction's wall
                          fitting, every junction's run end and every corner, wet with covers;
                          the frame's posts and the infills' corners dry
Drawn as take_sheet.ours() draws a drill (the engine's layer order, shadows emulated).
"""
import json
import os
import sys

from PIL import Image, ImageDraw

import take_sheet as ts
import vanilla_bmd as v
import rig_parts_geom as geo

DIRS = ts.DIRS
PPT = v.PPT
# the gaps (gap-list.txt): name, plan box (x0, y0, x1, y1), the void's top
GAPS = [
    ("G1 under the SE cabinet (Liam's marked crop)", (0.79, -2.5, 1.5, -1.94), 1.30),
    ("G2 under the SW housing", (-1.5, -2.5, -0.79, -1.94), 1.25),
    ("G3 under the NE drive cabinet", (1.94, 0.78, 2.5, 1.5), 1.25),
    ("G4 under the NW drive cabinet", (-2.5, 0.78, -1.94, 1.5), 1.25),
]
BG = (32, 32, 34)


def label(dr, x, y, text, size=16, fill=(240, 200, 90)):
    dr.text((x, y), text, fill=fill, font=v.font(size))


def window(img, x0, x1, top, bottom):
    """A crop of a composite (origin at its centre), in screen tiles (x right, y down)."""
    cx, cy = img.width / 2, img.height / 2
    return img.crop((round(cx + x0 * PPT), round(cy + top * PPT), round(cx + x1 * PPT), round(cy + bottom * PPT)))


def phone(out, before, after):
    W, crop, k = 1080, 360, 1.5
    C = round(crop * k)
    head = 30
    rows = [(d, wet) for d in DIRS for wet in (False, True)]
    H = 60 + len(rows) * (C + head)
    sheet = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 8, "Ballast drill, cast take: T03f (before) | T03g (after)", 22, (240, 240, 240))
    label(dr, 8, 34, "1.5x; wet with vanilla's covers; per direction dry, then wet", 16, (200, 200, 200))
    m = (ts.CELL - crop) // 2
    for r, (d, wet) in enumerate(rows):
        y = 60 + r * (C + head)
        for i, (t, nm) in enumerate(((before, "before"), (after, "after"))):
            im = ts.ours(t, d, wet=wet).convert("RGB").crop((m, m, m + crop, m + crop))
            sheet.paste(im.resize((C, C), Image.LANCZOS), (i * C, y + head))
            label(dr, i * C + 8, y + 6, f"{d}, {'wet' if wet else 'dry'}: {nm}", 18)
    sheet.save(out)
    print(out, sheet.size)


def gap_sheets(outdir, before, after):
    k = 4
    big = (ts.CELL + 160, ts.CELL + 160)
    cache = {}

    def comp(t, d, wet):
        key = (id(t), d, wet)
        if key not in cache:
            cache[key] = ts.ours(t, d, wet=wet, size=big).convert("RGB")
        return cache[key]
    paths = []
    for gi, (name, (x0, y0, x1, y1), ztop) in enumerate(GAPS):
        sx0, sx1 = x0 - 0.3, x1 + 0.3
        top, bottom = -y1 - ztop / 2 - 0.45, -y0 + 0.3
        views = [("north", False)] + [(d, True) for d in DIRS]
        cw = round((sx1 - sx0) * PPT * k)
        ch = round((bottom - top) * PPT * k)
        head = 26
        W, H = 2 * cw + 10, 56 + len(views) * (ch + head)
        sheet = Image.new("RGB", (W, H), BG)
        dr = ImageDraw.Draw(sheet)
        label(dr, 8, 6, name, 18, (240, 240, 240))
        label(dr, 8, 30, "4x nearest: before (T03f) | after (T03g)", 14, (200, 200, 200))
        for r, (d, wet) in enumerate(views):
            y = 56 + r * (ch + head)
            for i, t in enumerate((before, after)):
                c = window(comp(t, d, wet), sx0, sx1, top, bottom)
                sheet.paste(c.resize((c.width * k, c.height * k), Image.NEAREST), (i * (cw + 10), y + head))
                lab = f"{'dry (every direction)' if not wet else d + ', wet'}: {'before' if i == 0 else 'after'}"
                label(dr, i * (cw + 10) + 6, y + 4, lab, 14)
        p = os.path.join(outdir, f"gap-G{gi + 1}.png")
        sheet.save(p)
        paths.append(p)
        print(p, sheet.size)
    return paths


def clipping(out, after):
    rj = json.load(open(os.path.join(after.dir, "rig", "hi", "rig.json")))
    k, win = 2, 1.5
    cpx = round(win * PPT * k)
    head = 22
    items = []
    ends = geo.ends()
    for d in DIRS:
        niches = {(round(n[0], 2), round(n[1], 2)) for n in rj.get("niches", {}).get(d, [])}
        for c in rj.get("collars", {}).get(d, []):
            items.append((d, True, f"collar ({c[0]:+.2f},{c[1]:+.2f})", (c[0], c[1], c[2])))
        for n in rj.get("niches", {}).get(d, []):
            items.append((d, True, f"buried junction's wall fitting {n[2]} ({n[0]:+.2f},{n[1]:+.2f})",
                          (n[0], n[1], 0.42)))
        for nm, (x, y, z) in ends[d]:
            items.append((d, True, nm, (x, y, z)))
    # dry: the frame's posts (each corner) and the infills' outer corners
    for sx in (-1, 1):
        for sy in (-1, 1):
            items.append(("north", False, f"frame, corner {'N' if sy > 0 else 'S'}{'E' if sx > 0 else 'W'}",
                          (sx * 2.1, sy * 2.1, 0.35)))
    for name, (x0, y0, x1, y1), zt in GAPS:
        items.append(("north", False, f"infill {name.split()[0]}", ((x0 + x1) / 2, (y0 + y1) / 2, zt / 2)))
    per_row = 6
    rows = -(-len(items) // per_row)
    W, H = per_row * cpx, 50 + rows * (cpx + head)
    sheet = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 8, "T03g clipping check, 2x nearest: every wall collar, buried junction fitting, run end and corner "
          "(wet, covers); frame and infills (dry)", 18, (240, 240, 240))
    big = (ts.CELL + 160, ts.CELL + 160)
    cache = {}
    for i, (d, wet, nm, (x, y, z)) in enumerate(items):
        key = (d, wet)
        if key not in cache:
            cache[key] = ts.ours(after, d, wet=wet, size=big).convert("RGB")
        img = cache[key]
        sx, sy = ts.screen(x, y, z)
        c = window(img, sx - win / 2, sx + win / 2, sy - win / 2, sy + win / 2)
        c = c.resize((c.width * k, c.height * k), Image.NEAREST)
        px, py = (i % per_row) * cpx, 50 + (i // per_row) * (cpx + head)
        sheet.paste(c, (px, py + head))
        label(dr, px + 4, py + 3, f"{d}{'' if wet else ' dry'}: {nm}", 12, (150, 210, 255))
    sheet.save(out)
    print(out, sheet.size, len(items), "crops")


def main():
    b, a, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    before, after = ts.Take("T03f", b), ts.Take("T03g", a)
    phone(os.path.join(out, "before-after-phone.png"), before, after)
    gap_sheets(out, before, after)
    clipping(os.path.join(out, "clipping-2x.png"), after)


if __name__ == "__main__":
    main()
