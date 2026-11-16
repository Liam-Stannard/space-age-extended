#!/usr/bin/env python3
"""Review sheets for T03i (task ballast-drill-ports): the cast take rebuilt to option B2.

  python3 review_sheet.py <T03h phone sheet> <T03i take dir> <out dir> [--one north]

<T03h phone sheet>: T03h's kept before-after-phone.png (evidence/ballast-drill-t03h/sheets/): its
right-hand column is T03h drawn by take_sheet.ours() at 1.5x, per direction dry then wet, so it is
cut from there and set beside T03i's, drawn the same way (no T03h re-render).
<T03i take dir>: as take.sh leaves it (plate/sheets: the B2 body's own passes, the animated layers
included; rig/sheets; wet/). --one: the one-direction proof (files unsuffixed).

Writes to <out dir>:
  before-after-phone.png  1080 px wide: per direction dry, then wet (vanilla's covers), T03h | T03i
  sketch-vs-render.png    north, wet, 2x: the B2 sketch (plate_concepts.py's game view, drawn
                          again from its numbers) beside the T03i render, the same scale and centre
  fittings-4x.png         4x nearest: per direction each connection, the end ring in the plate's
                          wall, the riser on its flange on the plate's top, the head and the run
  clipping-2x.png         2x nearest: every run end, corner and bay crossing (wet, covers); the
                          frame's corners, the bastions' feet and faces (dry)
Drawn as take_sheet.ours() draws a drill (the engine's layer order, shadows emulated), with the
take's own animated layers (chute, stroke frame 0) in place of the signed-off ones.
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw

import take_sheet as ts
import vanilla_bmd as v
import rig_parts_geom as geo
import plate_sheet as ps

HERE = os.path.dirname(os.path.abspath(__file__))
DIRS = ts.DIRS
PPT = v.PPT
BG = (32, 32, 34)
Z_RUN, ZA, PLATE_TOP = 1.15, 0.42, 0.85       # rig_parts.py's


class Take(ps.Take):
    """A T03i take: the animated layers are its own (plate/sheets), not the signed-off sheets."""

    def __init__(self, label, d, one=""):
        super().__init__(label, d, one)
        self.signed = self.plate
        self.stroke = None

    def frame(self, where, stem, f=0):
        if where == "signed":
            where = "plate"
        return super().frame(where, stem, f)


def label(dr, x, y, text, size=16, fill=(240, 200, 90)):
    dr.text((x, y), text, fill=fill, font=v.font(size))


def phone(out, t03h_sheet, t, dirs):
    W, crop, k = 1080, 360, 1.5
    C = round(crop * k)
    head = 30
    g = Image.open(t03h_sheet).convert("RGB")
    assert g.size == (1080, 60 + 8 * (C + head)), g.size
    rows = [(d, wet) for d in dirs for wet in (False, True)]
    H = 60 + len(rows) * (C + head)
    sheet = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 8, "Ballast drill, cast take: T03h (before) | T03i, rebuilt to option B2 (after)", 22, (240, 240, 240))
    label(dr, 8, 34, "1.5x; wet with vanilla's covers; per direction dry, then wet", 16, (200, 200, 200))
    m = (ts.CELL - crop) // 2
    for r, (d, wet) in enumerate(rows):
        y = 60 + r * (C + head)
        rg = [(dd, ww) for dd in DIRS for ww in (False, True)].index((d, wet))
        yg = 60 + rg * (C + head) + head
        sheet.paste(g.crop((C, yg, 2 * C, yg + C)), (0, y + head))
        im = ts.ours(t, d, wet=wet).convert("RGB").crop((m, m, m + crop, m + crop))
        sheet.paste(im.resize((C, C), Image.LANCZOS), (C, y + head))
        for i, nm in enumerate(("T03h", "T03i (B2)")):
            label(dr, i * C + 8, y + 6, f"{d}, {'wet' if wet else 'dry'}: {nm}", 18)
    assert max(sheet.size) < 8000
    sheet.save(out)
    print(out, sheet.size)


def composite_like_concept(wet_dir, d, one):
    """As plate_concepts.t03h_composite draws the T03h still: the layers in combine.py's order,
    shadows at half strength, on the ground tone, the footprint centre at GV_C (64 px a tile)."""
    sys.path.insert(0, os.path.join(HERE, "..", "..", "plate-concepts"))
    import plate_concepts as pc
    meta = json.load(open(os.path.join(wet_dir, "meta.json")))
    g = tuple(int(pc.TONE["ground"][i:i + 2], 16) for i in (1, 3, 5))
    im = Image.new("RGBA", (pc.GV_CELL, pc.GV_CELL), g + (255,))
    for stem in ("base-shadow", "rig-shadow", "base", "rig", "chute", "stroke", "rig-front"):
        name = stem if one else f"{stem}-{d}"
        m = meta[name]
        w, h = m["size"]
        lay = Image.open(os.path.join(wet_dir, name + ".png")).convert("RGBA").crop((0, 0, w, h))
        if "shadow" in stem:
            a = lay.getchannel("A").point(lambda q: q // 2)
            lay = Image.merge("RGBA", (*Image.new("RGB", lay.size).split(), a))
        x = round(pc.GV_C[0] + m["shift"][0] * pc.GV_K - w / 2)
        y = round(pc.GV_C[1] + m["shift"][1] * pc.GV_K - h / 2)
        im.alpha_composite(lay, (x, y))
    return im.convert("RGB")


def sketch_vs_render(out, take_dir, one, scratch):
    sys.path.insert(0, os.path.join(HERE, "..", "..", "plate-concepts"))
    import plate_concepts as pc
    pc.set_raised()
    parts, _ = pc.build("B2")
    svg = pc.Svg()
    W = 2 * pc.GV_CELL
    svg.rect(0, 0, W, W, pc.TONE["ground"], "none", 0)
    pc.draw_gameview(svg, 2 * pc.GV_C[0], 2 * pc.GV_C[1], 2 * pc.GV_K, 0, parts)
    pc.footprint_marks(svg, 0, 0, 2)
    sp = os.path.join(scratch, "b2-sketch-north-2x.svg")
    with open(sp, "w") as fh:
        fh.write(pc.document(svg.o, W, W))
    pp = sp[:-4] + ".png"
    subprocess.run(["rsvg-convert", "-o", pp, sp], check=True)
    sk = Image.open(pp).convert("RGB")
    ren = composite_like_concept(os.path.join(take_dir, "wet"), "north", one)
    ren = ren.resize((W, W), Image.NEAREST)
    # the same footprint ticks over the render
    tk = pc.Svg()
    pc.footprint_marks(tk, 0, 0, 2)
    tp = os.path.join(scratch, "b2-ticks-2x.svg")
    with open(tp, "w") as fh:
        fh.write(pc.document(tk.o, W, W))
    subprocess.run(["rsvg-convert", "-o", tp[:-4] + ".png", tp], check=True)
    ren = ren.convert("RGBA")
    ren.alpha_composite(Image.open(tp[:-4] + ".png").convert("RGBA"))
    ren = ren.convert("RGB")
    head = 64
    sheet = Image.new("RGB", (2 * W + 16, W + head + 30), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 8, "North, wet, 2x: the B2 sketch (T03h2, as drawn) | the T03i model render; same scale and centre",
          20, (240, 240, 240))
    label(dr, 8, 36, "64 px a tile at 1x; ticks at the footprint's corners; the render: base, rig, chute, stroke "
          "frame 0, rig front, shadows at half strength", 14, (200, 200, 200))
    sheet.paste(sk, (0, head))
    sheet.paste(ren, (W + 16, head))
    label(dr, 8, W + head + 6, "B2 sketch (plate_concepts.py at 271f85d)", 15)
    label(dr, W + 24, W + head + 6, "T03i render (rig-round-6, cast take)", 15)
    assert max(sheet.size) < 8000
    sheet.save(out)
    print(out, sheet.size)


def fittings(out, t, dirs):
    k = 4
    big = (ts.CELL + 160, ts.CELL + 160)
    items = []
    for d in dirs:
        comp = ts.ours(t, d, wet=True, size=big).convert("RGB")
        for c in geo.conns(d):
            jx, jy = geo.junction(*c)
            ex, ey = geo.end_ring(*c)
            pts = [ts.screen(jx, jy, Z_RUN + 0.3), ts.screen(jx, jy, PLATE_TOP), ts.screen(ex, ey, ZA + 0.42),
                   ts.screen(ex, ey, ZA - 0.42)]
            cx = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
            cy = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
            items.append((f"{d}: {c[2]}({c[0]},{c[1]})", ps.window(comp, cx - 0.95, cx + 0.95, cy - 0.95, cy + 0.95)))
    cw = round(1.9 * PPT * k)
    head = 24
    per = 4
    rows = -(-len(items) // per)
    sheet = Image.new("RGB", (per * cw + (per - 1) * 8, 56 + rows * (cw + head)), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 6, "T03i: each connection's wall fitting in the plate's wall, its junction on the plate's top", 18,
          (240, 240, 240))
    label(dr, 8, 30, "4x nearest; wet, vanilla's covers; end ring in its recessed boss (south: 0.24 proud, a wall "
          "flange at the face), riser on a bolted flange, head and run at 1.15", 14, (200, 200, 200))
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
        cs = geo.conns(d)
        for a_, b_ in ((cs[0], cs[3]), (cs[1], cs[2])):
            for p_, q_ in ((a_, b_), (b_, a_)):
                n, m = geo.NORMAL[p_[2]], geo.NORMAL[q_[2]]
                jx, jy = geo.junction(*p_)
                lat, corner = (jy, m[1]) if n[0] else (jx, m[0])
                if lat * corner < 0:
                    x, y = (n[0] * geo.R_AX, 0.0) if n[0] else (0.0, n[1] * geo.R_AX)
                    items.append((d, True, f"run over the {p_[2]} bay", (x, y, Z_RUN)))
    d0 = dirs[0]
    for sx in (-1, 1):
        for sy in (-1, 1):
            items.append((d0, False, f"frame, corner {'N' if sy > 0 else 'S'}{'E' if sx > 0 else 'W'}",
                          (sx * 2.1, sy * 2.1, 0.45)))
    for nm, (x, y, z) in (("SW bastion: door, chamfer", (-1.35, -1.85, 1.3)), ("SE bastion: panel, box", (1.2, -1.9, 1.3)),
                          ("SW roof: tank, lamp", (-1.4, -1.7, 2.2)), ("SE roof: bottles, 50", (1.45, -1.7, 2.2)),
                          ("SW manifold, hoses", (-1.0, -1.45, 0.95)), ("W ram hoses", (-1.65, -1.1, 0.9)),
                          ("E ram hose", (1.65, -1.1, 1.2)), ("NE bastion: door, stripe", (1.55, 1.2, 1.4)),
                          ("NW bastion: door, hoses", (-1.55, 1.2, 1.4)), ("NE house, roof", (1.4, 1.3, 2.9)),
                          ("NW house, roof", (-1.4, 1.3, 2.9)), ("N ram hose", (-0.85, 1.65, 0.9))):
        items.append((d0, False, nm, (x, y, z)))
    per_row = 6
    rows = -(-len(items) // per_row)
    W, H = per_row * cpx, 50 + rows * (cpx + head)
    sheet = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 8, "T03i clipping check, 2x nearest: every run end, corner and bay crossing (wet, covers); the frame, "
          "bastions, roofs and services (dry)", 18, (240, 240, 240))
    big = (ts.CELL + 160, ts.CELL + 160)
    cache = {}
    for i, (d, wet, nm, (x, y, z)) in enumerate(items):
        key = (d, wet)
        if key not in cache:
            cache[key] = ts.ours(t, d, wet=wet, size=big).convert("RGB")
        sx, sy = ts.screen(x, y, z)
        c = ps.window(cache[key], sx - win / 2, sx + win / 2, sy - win / 2, sy + win / 2)
        c = c.resize((c.width * k, c.height * k), Image.NEAREST)
        px, py = (i % per_row) * cpx, 50 + (i // per_row) * (cpx + head)
        sheet.paste(c, (px, py + head))
        label(dr, px + 4, py + 3, f"{d}{'' if wet else ' dry'}: {nm}"[:36], 12, (150, 210, 255))
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
    t = Take("T03i", a, one)
    dirs = (one,) if one else DIRS
    phone(os.path.join(out, "before-after-phone.png"), g, t, dirs)
    sketch_vs_render(os.path.join(out, "sketch-vs-render.png"), a, one, out)
    fittings(os.path.join(out, "fittings-4x.png"), t, dirs)
    clipping(os.path.join(out, "clipping-2x.png"), t, dirs)


if __name__ == "__main__":
    main()
