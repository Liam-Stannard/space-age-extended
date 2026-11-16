#!/usr/bin/env python3
"""Review sheets for T03h (task ballast-drill-ports): the cast take's drill on a raised plate, its
runs on the plate's top.

  python3 plate_sheet.py <T03g phone sheet> <T03h take dir> <out dir> [--one north]

<T03g phone sheet>: T03g's kept before-after-phone.png (evidence/ballast-drill-t03g/sheets/): its
right-hand column is T03g's cast take drawn by take_sheet.ours() at 1.5x, per direction dry then
wet, so it is cut from there and set beside T03h's, drawn the same way (no T03g re-render).
<T03h take dir>: as take.sh leaves it (plate/sheets, rig/sheets). --one <direction>: the take was
the one-direction proof (SAE_RIG_ONE: files unsuffixed); only that direction is drawn.

Writes to <out dir>:
  before-after-phone.png  1080 px wide: per direction dry, then wet (vanilla's covers), T03g | T03h
  fittings-4x.png         4x nearest (the sprite's own pixels): per direction each connection, from
                          the end ring at the plate's wall up the slot to the junction's head on
                          the plate's top and the run leaving it (wet, covers)
  clipping-2x.png         2x nearest: every run end and corner the runs turn, every run's crossing
                          of a discharge bay (wet, covers); the frame's corners and the plate's
                          edges under the overhangs (dry)
Drawn as take_sheet.ours() draws a drill (the engine's layer order, shadows emulated).
"""
import os
import sys

from PIL import Image, ImageDraw

import take_sheet as ts
import vanilla_bmd as v
import rig_parts_geom as geo

DIRS = ts.DIRS
PPT = v.PPT
BG = (32, 32, 34)
Z_RUN, ZA, PLATE_TOP = 0.96, 0.42, 0.66       # rig_parts.py's


class Take(ts.Take):
    """A take; with `one`, its plate and rig sheets unsuffixed (the one-direction proof)."""

    def __init__(self, label, d, one=""):
        super().__init__(label, d)
        self.one = one

    def frame(self, where, stem, f=0):
        if self.one and where in ("plate", "rig"):
            meta = self.plate if where == "plate" else self.rig
            if stem not in meta and stem.endswith("-" + self.one):
                stem = stem[:-len(self.one) - 1]
        return super().frame(where, stem, f)


def label(dr, x, y, text, size=16, fill=(240, 200, 90)):
    dr.text((x, y), text, fill=fill, font=v.font(size))


def window(img, x0, x1, top, bottom):
    """A crop of a composite (origin at its centre), in screen tiles (x right, y down)."""
    cx, cy = img.width / 2, img.height / 2
    return img.crop((round(cx + x0 * PPT), round(cy + top * PPT), round(cx + x1 * PPT), round(cy + bottom * PPT)))


def phone(out, t03g_sheet, t, dirs):
    W, crop, k = 1080, 360, 1.5
    C = round(crop * k)
    head = 30
    g = Image.open(t03g_sheet).convert("RGB")
    assert g.size == (1080, 60 + 8 * (C + head)), g.size
    rows = [(d, wet) for d in dirs for wet in (False, True)]
    H = 60 + len(rows) * (C + head)
    sheet = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 8, "Ballast drill, cast take: T03g (before) | T03h, on a raised plate (after)", 22, (240, 240, 240))
    label(dr, 8, 34, "1.5x; wet with vanilla's covers; per direction dry, then wet", 16, (200, 200, 200))
    m = (ts.CELL - crop) // 2
    for r, (d, wet) in enumerate(rows):
        y = 60 + r * (C + head)
        rg = [(dd, ww) for dd in DIRS for ww in (False, True)].index((d, wet))
        yg = 60 + rg * (C + head) + head
        sheet.paste(g.crop((C, yg, 2 * C, yg + C)), (0, y + head))
        im = ts.ours(t, d, wet=wet).convert("RGB").crop((m, m, m + crop, m + crop))
        sheet.paste(im.resize((C, C), Image.LANCZOS), (C, y + head))
        for i, nm in enumerate(("T03g", "T03h")):
            label(dr, i * C + 8, y + 6, f"{d}, {'wet' if wet else 'dry'}: {nm}", 18)
    sheet.save(out)
    print(out, sheet.size)


def fittings(out, t, dirs):
    """Per connection: from the end ring at the wall to the head on the plate top, 4x."""
    k = 4
    big = (ts.CELL + 160, ts.CELL + 160)
    items = []
    for d in dirs:
        comp = ts.ours(t, d, wet=True, size=big).convert("RGB")
        for c in geo.conns(d):
            jx, jy = geo.junction(*c)
            ex, ey = geo.end_ring(*c)
            pts = [ts.screen(jx, jy, Z_RUN + 0.3), ts.screen(jx, jy, 0.0), ts.screen(ex, ey, ZA + 0.42),
                   ts.screen(ex, ey, ZA - 0.42)]
            x0 = min(p[0] for p in pts) - 0.55
            x1 = max(p[0] for p in pts) + 0.55
            top = min(p[1] for p in pts) - 0.3
            bottom = max(p[1] for p in pts) + 0.3
            # a fixed window (1.9 x 1.9 tiles) about the middle, so every crop is the same size
            cx, cy = (x0 + x1) / 2, (top + bottom) / 2
            items.append((f"{d}: {c[2]}({c[0]},{c[1]})", window(comp, cx - 0.95, cx + 0.95, cy - 0.95, cy + 0.95)))
    cw = round(1.9 * PPT * k)
    head = 24
    per = 4
    rows = -(-len(items) // per)
    sheet = Image.new("RGB", (per * cw + (per - 1) * 8, 56 + rows * (cw + head)), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 6, "T03h: where each run leaves its wall fitting and climbs onto the plate", 18, (240, 240, 240))
    label(dr, 8, 30, "4x nearest; wet, vanilla's covers; end ring at the plate's wall, riser up the slot, head and "
          "run on the plate's top", 14, (200, 200, 200))
    for i, (nm, c) in enumerate(items):
        x = (i % per) * (cw + 8)
        y = 56 + (i // per) * (cw + head)
        sheet.paste(c.resize((c.width * k, c.height * k), Image.NEAREST), (x, y + head))
        label(dr, x + 6, y + 4, nm, 15)
    assert max(sheet.size) < 8000, sheet.size
    sheet.save(out)
    print(out, sheet.size, len(items), "crops")


def clipping(out, t, dirs):
    k, win = 2, 1.5
    cpx = round(win * PPT * k)
    head = 22
    items = []
    ends = geo.ends()
    for d in dirs:
        for nm, (x, y, z) in ends[d]:
            items.append((d, True, nm, (x, y, z)))
        # each run's crossing of a discharge bay (the bays at the faces' middles): a run goes from
        # each junction along its face to the corner it shares with its pair's other face
        cs = geo.conns(d)
        for a_, b_ in ((cs[0], cs[3]), (cs[1], cs[2])):
            for p_, q_ in ((a_, b_), (b_, a_)):
                n, m = geo.NORMAL[p_[2]], geo.NORMAL[q_[2]]
                jx, jy = geo.junction(*p_)
                lat, corner = (jy, m[1]) if n[0] else (jx, m[0])
                if lat * corner < 0:
                    x, y = (n[0] * geo.R_AX, 0.0) if n[0] else (0.0, n[1] * geo.R_AX)
                    items.append((d, True, f"run over the {p_[2]} bay", (x, y, Z_RUN)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            items.append((dirs[0], False, f"frame, corner {'N' if sy > 0 else 'S'}{'E' if sx > 0 else 'W'}",
                          (sx * 2.1, sy * 2.1, 0.35)))
    for nm, (x, y) in (("plate under SE cabinet", (1.14, -2.25)), ("plate under SW housing", (-1.14, -2.25)),
                       ("plate under NE cabinet", (2.25, 1.13)), ("plate under NW cabinet", (-2.25, 1.13))):
        items.append((dirs[0], False, nm, (x, y, PLATE_TOP)))
    per_row = 6
    rows = -(-len(items) // per_row)
    W, H = per_row * cpx, 50 + rows * (cpx + head)
    sheet = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 8, "T03h clipping check, 2x nearest: every run end, corner and bay crossing (wet, covers); "
          "frame and plate under the overhangs (dry)", 18, (240, 240, 240))
    big = (ts.CELL + 160, ts.CELL + 160)
    cache = {}
    for i, (d, wet, nm, (x, y, z)) in enumerate(items):
        key = (d, wet)
        if key not in cache:
            cache[key] = ts.ours(t, d, wet=wet, size=big).convert("RGB")
        sx, sy = ts.screen(x, y, z)
        c = window(cache[key], sx - win / 2, sx + win / 2, sy - win / 2, sy + win / 2)
        c = c.resize((c.width * k, c.height * k), Image.NEAREST)
        px, py = (i % per_row) * cpx, 50 + (i // per_row) * (cpx + head)
        sheet.paste(c, (px, py + head))
        label(dr, px + 4, py + 3, f"{d}{'' if wet else ' dry'}: {nm}"[:34], 12, (150, 210, 255))
    assert max(sheet.size) < 8000, sheet.size
    sheet.save(out)
    print(out, sheet.size, len(items), "crops")


def main():
    argv = sys.argv[1:]
    one = ""
    if "--one" in argv:
        i = argv.index("--one")
        one = argv[i + 1]
        del argv[i:i + 2]
    g, a, out = argv[:3]
    os.makedirs(out, exist_ok=True)
    t = Take("T03h", a, one)
    dirs = (one,) if one else DIRS
    phone(os.path.join(out, "before-after-phone.png"), g, t, dirs)
    fittings(os.path.join(out, "fittings-4x.png"), t, dirs)
    clipping(os.path.join(out, "clipping-2x.png"), t, dirs)


if __name__ == "__main__":
    main()
