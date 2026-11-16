#!/usr/bin/env python3
"""Sheets for the frame round (task ballast-drill-ports, T03f: a steel frame under the rig).

  python3 frame_sheet.py top <out.png> <label>=<take out-dir> ...
      the phone sheet, 1080 px wide: per take a row, north dry and north wet (vanilla's covers),
      1x the sprite's pixels scaled to fit
  python3 frame_sheet.py dry <out.png> <label> <take out-dir> <views dir>
      one take dry (no connections): the four directions as the game draws a dry drill, 2x, and
      the frame from low obliques at each corner (views dir: rig_parts.py's "views" pass,
      SAE_RIG_CORNERS=1, view-dry-c<NE|NW|SE|SW><0|1|2>.png)
  python3 frame_sheet.py vanilla <out.png> <label>=<take out-dir> ...
      the corner frames beside vanilla's: the big mining drill's frame (its dry still and its
      support) and the pumpjack's (its base and horsehead frame 0), all at 2x the sprite's
      pixels, the same scale as each take's south-east corner, dry
  python3 frame_sheet.py crops <out.png> <label> <take out-dir> <views dir>
      the clipping check at 2x: every run end and corner per direction (wet, covers), each
      corner frame dry (posts' feet and caps, braces, the head), and the oblique corner views
"""
import os
import sys

from PIL import Image, ImageDraw

import take_sheet as ts
import vanilla_bmd as v

DIRS = v.DIRS
DATA = None


def factorio_data():
    here = os.path.dirname(os.path.abspath(__file__))
    tools = os.path.normpath(os.path.join(here, "..", "..", "..", "..", "tools"))
    sys.path.insert(0, tools)
    import paths
    return paths.factorio_data() if hasattr(paths, "factorio_data") else paths.get("factorio-data")


def label(dr, x, y, text, size=18, fill=(240, 200, 90)):
    dr.text((x, y), text, fill=fill, font=v.font(size))


def top(out, takes):
    W = 1080
    cell = W // 2
    head = 26
    crop = 400
    m = (ts.CELL - crop) // 2
    H = 40 + len(takes) * (cell + head)
    sheet = Image.new("RGB", (W, H), (32, 32, 34))
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 10, "Ballast drill rig, T03f: the steel frame on each take (north)", 20, (240, 240, 240))
    for r, t in enumerate(takes):
        y = 40 + r * (cell + head)
        for k, (lab, wet) in enumerate((("dry, no connections", False), ("wet, vanilla covers", True))):
            im = ts.ours(t, "north", wet=wet).convert("RGB").crop((m, m, m + crop, m + crop))
            sheet.paste(im.resize((cell, cell), Image.LANCZOS), (k * cell, y + head))
            label(dr, k * cell + 6, y + 4, f"{t.label}: {lab}", 17)
    sheet.save(out)
    print(out, sheet.size)


def dry(out, t, views):
    head = 28
    crop = 400
    m = (ts.CELL - crop) // 2
    C = crop * 2
    vw = 600
    vh = 450
    W = 4 * C
    H = 50 + C + head + 2 * (vh + head) + 10
    assert max(W, H) < 8000
    sheet = Image.new("RGB", (W, H), (32, 32, 34))
    dr = ImageDraw.Draw(sheet)
    label(dr, 10, 12, f"Ballast drill rig, take {t.label}, dry (no connections): the frame alone carries the corner "
          "beams; the game's view at 2x, then low obliques of each corner", 24, (240, 240, 240))
    for k, d in enumerate(DIRS):
        im = v.grid(ts.ours(t, d, wet=False)).convert("RGB").crop((m, m, m + crop, m + crop))
        sheet.paste(im.resize((C, C), Image.LANCZOS), (k * C, 50 + head))
        label(dr, k * C + 8, 54, f"{d}: dry")
    y0 = 50 + C + head
    names = [f"c{cn}{i}" for cn in ("SE", "SW", "NE", "NW") for i in (0, 1)]
    per = W // vw
    for i, n in enumerate(names):
        p = os.path.join(views, f"view-dry-{n}.png")
        if not os.path.isfile(p):
            continue
        im = Image.open(p).convert("RGB").resize((vw, vh), Image.LANCZOS)
        x, y = (i % per) * vw, y0 + (i // per) * (vh + head)
        label(dr, x + 6, y + 4, f"{n[1:3]} corner, oblique {'left' if n[-1] == '0' else 'square'}", 17, (150, 210, 255))
        sheet.paste(im, (x, y + head))
    sheet.save(out)
    print(out, sheet.size)


def vanilla(out, takes):
    data = factorio_data()
    bmd = os.path.join(data, "space-age", "graphics", "entity", "big-mining-drill")
    bg = v.GROUND + (255,)

    def on(im):
        c = Image.new("RGBA", im.size, bg)
        c.alpha_composite(im)
        return c
    pieces = []
    st = Image.open(os.path.join(bmd, "North", "big-mining-drill-N-still.png")).convert("RGBA")
    pieces.append(("vanilla big mining drill, north still (its frame: ladder legs, gantry)", on(st)))
    sp = Image.open(os.path.join(bmd, "East", "big-mining-drill-E-support.png")).convert("RGBA")
    pieces.append(("big mining drill, east support, frame 0", on(sp.crop((0, 0, sp.width // 3, sp.height // 2)))))
    pj = os.path.join(data, "base", "graphics", "entity", "pumpjack")
    # the base's first picture (261 x 273, mining-drill.lua:294-299) and the horsehead's frame 0
    # (206 x 172), placed by their shifts (px at scale 0.5, so doubled here)
    base = Image.open(os.path.join(pj, "pumpjack-base.png")).convert("RGBA").crop((0, 0, 261, 273))
    hh = Image.open(os.path.join(pj, "pumpjack-horsehead.png")).convert("RGBA").crop((0, 0, 206, 172))
    c = Image.new("RGBA", base.size, bg)
    c.alpha_composite(base)
    c.alpha_composite(hh, (round(base.width / 2 - 103 + (-9 + 4.5)), round(base.height / 2 - 86 + (-58 + 9.5))))
    pieces.append(("vanilla pumpjack (its A-frame: I-beam legs, X-braced)", c))
    for t in takes:
        g = ts.ours(t, "north", wet=False)
        cx, cy = g.width / 2, g.height / 2
        # the south-east and south-west corners of the 1x sheet, dry
        box = (round(cx - 2.9 * v.PPT), round(cy + 0.6 * v.PPT), round(cx + 2.9 * v.PPT), round(cy + 2.9 * v.PPT))
        pieces.append((f"ours, {t.label}: the south corners, dry", g.crop(box)))
    k = 2
    head = 26
    W = 0
    rows, row, rw = [], [], 0
    for p in pieces:
        w = p[1].width * k
        if rw + w > 3600 and row:
            rows.append(row)
            row, rw = [], 0
        row.append(p)
        rw += w + 10
    rows.append(row)
    W = max(sum(p[1].width * k + 10 for p in r) for r in rows)
    H = 50 + sum(max(p[1].height * k for p in r) + head + 10 for r in rows)
    assert max(W, H) < 8000, (W, H)
    sheet = Image.new("RGB", (W, H), (32, 32, 34))
    dr = ImageDraw.Draw(sheet)
    label(dr, 10, 12, "The frames at 2x the sprites' pixels: vanilla's big mining drill and pumpjack, then each take's "
          "corner frame (dry)", 24, (240, 240, 240))
    y = 50
    for r in rows:
        x = 0
        for lab, im in r:
            label(dr, x + 6, y + 4, lab, 16)
            sheet.paste(im.convert("RGB").resize((im.width * k, im.height * k), Image.LANCZOS), (x, y + head))
            x += im.width * k + 10
        y += max(p[1].height * k for p in r) + head + 10
    sheet.save(out)
    print(out, sheet.size)


def crops(out, t, views):
    import rig_parts_geom as geo
    k = 2
    CW = 1.5
    cpx = round(CW * v.PPT * k)
    head = 24
    per = 8
    items = []
    ends = geo.ends()
    for d in DIRS:
        img = ts.ours(t, d, size=(ts.CELL + 160, ts.CELL + 160))
        for name, (x, y, z) in ends[d]:
            items.append((f"{d} wet: {name}", img, ts.screen(x, y, z)))
    # the frame, dry: each corner (the plate does not turn: north's is every direction's)
    img = ts.ours(t, "north", wet=False, size=(ts.CELL + 160, ts.CELL + 160))
    for cn, (sx, sy) in (("NE", (1, 1)), ("NW", (-1, 1)), ("SE", (1, -1)), ("SW", (-1, -1))):
        items.append((f"dry: {cn} corner frame", img, ts.screen(sx * 2.0, sy * 2.0, 0.3)))
    rows = -(-len(items) // per)
    vw, vh = 512, 384
    nviews = 12
    vrows = -(-nviews // (per * cpx // vw))
    W = per * cpx
    H = 50 + rows * (cpx + head) + 40 + vrows * (vh + head)
    assert max(W, H) < 8000, (W, H)
    sheet = Image.new("RGB", (W, H), (32, 32, 34))
    dr = ImageDraw.Draw(sheet)
    label(dr, 10, 6, f"Take {t.label}: clipping check, 2x: run ends and corners (wet, covers),", 20, (240, 240, 240))
    label(dr, 10, 28, "corner frames (dry); then the frames from low obliques", 16, (240, 240, 240))
    for i, (name, img, (sx, sy)) in enumerate(items):
        cx, cy = img.width / 2 + sx * v.PPT, img.height / 2 + sy * v.PPT
        h = CW / 2 * v.PPT
        c = img.crop((round(cx - h), round(cy - h), round(cx + h), round(cy + h)))
        c = c.resize((c.width * k, c.height * k), Image.LANCZOS).convert("RGB")
        px, py = (i % per) * cpx, 50 + (i // per) * (cpx + head)
        label(dr, px + 4, py + 5, name.replace("run end at ", "end ").replace(" wet", ""), 13, (150, 210, 255))
        sheet.paste(c, (px, py + head))
    y0 = 50 + rows * (cpx + head) + 40
    names = [f"c{cn}{i}" for cn in ("SE", "SW", "NE", "NW") for i in (0, 1, 2)]
    pr = W // vw
    for i, n in enumerate(names):
        p = os.path.join(views, f"view-dry-{n}.png")
        if not os.path.isfile(p):
            continue
        im = Image.open(p).convert("RGB").resize((vw, vh), Image.LANCZOS)
        x, y = (i % pr) * vw, y0 + (i // pr) * (vh + head)
        label(dr, x + 6, y + 4, f"{n[1:3]} corner, oblique {n[-1]}", 15, (150, 210, 255))
        sheet.paste(im, (x, y + head))
    sheet.save(out)
    print(out, sheet.size)


def main():
    a = sys.argv[1:]
    if a[0] == "top":
        top(a[1], [ts.Take(*x.split("=", 1)) for x in a[2:]])
    elif a[0] == "dry":
        dry(a[1], ts.Take(a[2], a[3]), a[4])
    elif a[0] == "vanilla":
        vanilla(a[1], [ts.Take(*x.split("=", 1)) for x in a[2:]])
    elif a[0] == "crops":
        crops(a[1], ts.Take(a[2], a[3]), a[4])


if __name__ == "__main__":
    main()
