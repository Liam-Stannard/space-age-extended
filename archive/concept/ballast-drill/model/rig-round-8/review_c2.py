#!/usr/bin/env python3
"""Review sheets for T03m (task ballast-drill-ports; rig-round-8: copied from rig-round-7's T03l script): the
south face back at the edge, the rams, girders and ladder posts back, the plate top's detail; cast take.

  python3 review_c2.py <T03i take dir> <T03l take dir> <out dir> [--one north]

<T03i take dir>, <T03l take dir>: as take.sh leaves them (plate/sheets, rig/sheets, wet/, dry/,
rig-notes/). --one: the T03l take is the one-direction proof (files unsuffixed); T03i is drawn in
that direction from its four.

Writes to <out dir>:
  t03i-t03l-phone.png   1080 px wide: per direction dry, then wet (vanilla's covers), T03i | T03l, 1.5x
  sketch-vs-render.png  north, 2x, wet then dry: the C2 sketch (pipe_concepts.py's T03k game view,
                        drawn again from its numbers) beside the T03l render, the same scale and centre
  hoses-4x.png          4x nearest: per direction each connection's gooseneck, hose and end boss
  clipping-2x.png       2x nearest: every hose end (gooseneck outlet, nozzle), every wall fitting, the
                        chute's drive and port per direction; the corners, bastions and services (dry)
  anim-strip.png        the ore's 24 frames per direction at its mouth (1x); the stroke's 24, north (0.5x)
  chute-strip.png       the chute's 5 frames per direction, 2x, around its port and drive (base, chute, stroke f0)
Drawn as take_sheet.ours() draws a drill (the engine's layer order, shadows emulated), each take
with its own animated layers (chute, stroke frame 0).
"""
import json
import sys as _sys
_sys.dont_write_bytecode = True   # nothing written beside pipe-concepts or plate-concepts
import os
import subprocess
import sys

from PIL import Image, ImageDraw

import take_sheet as ts
import vanilla_bmd as v
import plate_sheet as ps
import review_sheet as rs

HERE = os.path.dirname(os.path.abspath(__file__))
DIRS = ts.DIRS
PPT = v.PPT
BG = (32, 32, 34)
PT, ZA = 0.85, 0.42
label = rs.label


class Take(rs.Take):
    pass


def phone(out, a, b, dirs):
    crop, k = 360, 1.5
    C = round(crop * k)
    W = 2 * C
    head = 30
    rows = [(d, wet) for d in dirs for wet in (False, True)]
    H = 60 + len(rows) * (C + head)
    sheet = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 8, f"Ballast drill, cast take: {a.label} (before) | {b.label} (after)", 22, (240, 240, 240))
    label(dr, 8, 34, "1.5x; wet with vanilla's covers (north-facing ones on the plate top: vanilla's draw order); per direction dry, then wet", 16, (200, 200, 200))
    m = (ts.CELL - crop) // 2
    for r, (d, wet) in enumerate(rows):
        y = 60 + r * (C + head)
        for i, t in enumerate((a, b)):
            im = ts.ours(t, d, wet=wet).convert("RGB").crop((m, m, m + crop, m + crop))
            sheet.paste(im.resize((C, C), Image.LANCZOS), (i * C, y + head))
            label(dr, i * C + 8, y + 6, f"{d}, {'wet' if wet else 'dry'}: {t.label}", 18)
    assert max(sheet.size) < 8000
    sheet.save(out)
    print(out, sheet.size)


def composite(sheets_dir, d, one, wet):
    """As pipe_concepts' T03i stills are drawn: the layers in the engine's order, shadows at half
    strength, on the sketch's ground tone, the footprint's centre at GV_C (64 px a tile)."""
    sys.path.insert(0, os.path.join(HERE, "..", "..", "plate-concepts"))
    import plate_concepts as pc
    meta = json.load(open(os.path.join(sheets_dir, "meta.json")))
    g = tuple(int(pc.TONE["ground"][i:i + 2], 16) for i in (1, 3, 5))
    im = Image.new("RGBA", (pc.GV_CELL, pc.GV_CELL), g + (255,))
    stems = ("base-shadow", "rig-shadow", "base", "rig", "chute", "stroke", "rig-front") if wet else \
        ("base-shadow", "base", "chute", "stroke")
    for stem in stems:
        name = stem if one else f"{stem}-{d}"
        m = meta[name]
        w, h = m["size"]
        lay = Image.open(os.path.join(sheets_dir, name + ".png")).convert("RGBA").crop((0, 0, w, h))
        if "shadow" in stem:
            a = lay.getchannel("A").point(lambda q: q // 2)
            lay = Image.merge("RGBA", (*Image.new("RGB", lay.size).split(), a))
        x = round(pc.GV_C[0] + m["shift"][0] * pc.GV_K - w / 2)
        y = round(pc.GV_C[1] + m["shift"][1] * pc.GV_K - h / 2)
        im.alpha_composite(lay, (x, y))
    return im.convert("RGB")


def sketch_vs_render(out, take_dir, one, scratch):
    sys.path.insert(0, os.path.join(HERE, "..", "..", "pipe-concepts"))
    import pipe_concepts as P
    pc = P.pc
    W = 2 * pc.GV_CELL
    head = 64
    sheet = Image.new("RGB", (2 * W + 16, head + 2 * (W + 30)), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 8, "North, 2x, wet then dry: the C2 sketch (T03k, as drawn) | the T03l model render; same scale and "
          "centre", 20, (240, 240, 240))
    label(dr, 8, 36, "64 px a tile at 1x; ticks at the footprint's corners; the render: base, rig, chute, stroke frame 0, "
          "rig front, shadows at half strength", 14, (200, 200, 200))
    tk = pc.Svg()
    pc.footprint_marks(tk, 0, 0, 2)
    tp = os.path.join(scratch, "c2-ticks-2x.svg")
    with open(tp, "w") as fh:
        fh.write(pc.document(tk.o, W, W))
    subprocess.run(["rsvg-convert", "-o", tp[:-4] + ".png", tp], check=True)
    ticks = Image.open(tp[:-4] + ".png").convert("RGBA")
    for r, wet in enumerate((True, False)):
        svg = pc.Svg()
        svg.rect(0, 0, W, W, pc.TONE["ground"], "none", 0)
        P.draw_body_c2(svg, 2 * P.GC[0], 2 * P.GC[1], 2 * P.K1, 0, wet)
        pc.footprint_marks(svg, 0, 0, 2)
        sp = os.path.join(scratch, f"c2-sketch-north-{'wet' if wet else 'dry'}-2x.svg")
        with open(sp, "w") as fh:
            fh.write(pc.document(svg.o, W, W))
        subprocess.run(["rsvg-convert", "-o", sp[:-4] + ".png", sp], check=True)
        sk = Image.open(sp[:-4] + ".png").convert("RGB")
        ren = composite(os.path.join(take_dir, "wet" if wet else "dry"), "north", one, wet)
        ren = ren.resize((W, W), Image.NEAREST).convert("RGBA")
        ren.alpha_composite(ticks)
        y = head + r * (W + 30)
        sheet.paste(sk, (0, y))
        sheet.paste(ren.convert("RGB"), (W + 16, y))
        label(dr, 8, y + W + 6, f"C2 sketch, {'wet' if wet else 'dry'} (pipe_concepts.py at 041fc03)", 15)
        label(dr, W + 24, y + W + 6, f"T03m render, {'wet' if wet else 'dry'} (rig-round-8, cast take)", 15)
    assert max(sheet.size) < 8000
    sheet.save(out)
    print(out, sheet.size)


def hoses(take_dir):
    """{direction: [sizes]} from the rig pass's build log (c2.build)."""
    for p in (os.path.join(take_dir, "rig-notes", "rig-build.json"), os.path.join(take_dir, "rig", "rig-notes", "rig-build.json")):
        if os.path.isfile(p):
            return json.load(open(p))["sizes"]
    raise SystemExit("no rig-build.json under " + take_dir)


def hose_4x(out, t, take_dir, dirs):
    k = 4
    big = (ts.CELL + 160, ts.CELL + 160)
    sizes = hoses(take_dir)
    items = []
    for d in dirs:
        comp = ts.ours(t, d, wet=True, size=big).convert("RGB")
        for s in sizes[d]:
            gx, gy = s["gooseneck_axis"]
            nx, ny = s["nozzle"]
            pts = [ts.screen(gx, gy, 1.36), ts.screen(gx, gy, 0.0), ts.screen(nx, ny, 1.3), ts.screen(nx, ny, PT)]
            cx = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
            cy = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
            hw = max(0.75, (max(p[0] for p in pts) - min(p[0] for p in pts)) / 2 + 0.3,
                     (max(p[1] for p in pts) - min(p[1] for p in pts)) / 2 + 0.3)
            hw = min(hw, 1.0)
            c = ps.window(comp, cx - hw, cx + hw, cy - hw, cy + hw).resize((round(2 * hw * PPT), round(2 * hw * PPT)))
            items.append((f"{d}: {s['key']} {s['connection'][2]}({s['connection'][0]},{s['connection'][1]})", c))
    cw = round(2.0 * PPT * k)
    head = 24
    per = 4
    rows = -(-len(items) // per)
    sheet = Image.new("RGB", (per * cw + (per - 1) * 8, 56 + rows * (cw + head)), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 6, "T03m: each connection's gooseneck, hose and end boss (take C2, wet, vanilla's covers)", 18,
          (240, 240, 240))
    label(dr, 8, 30, "4x nearest; the gooseneck cast in the plate's top over its fitting, the 0.32 ribbed hose clamped "
          "both ends, the nozzle down into the boss on the plate against the shoulder", 14, (200, 200, 200))
    for i, (nm, c) in enumerate(items):
        x = (i % per) * (cw + 8)
        y = 56 + (i // per) * (cw + head)
        c = c.resize((c.width * k, c.height * k), Image.NEAREST)
        sheet.paste(c, (x + (cw - c.width) // 2, y + head + (cw - c.height) // 2))
        label(dr, x + 6, y + 4, nm, 15)
    assert max(sheet.size) < 8000, sheet.size
    sheet.save(out)
    print(out, sheet.size, len(items), "crops")


FACE_N = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}


def chute_face(d):
    return "NESW"[DIRS.index(d)]


def clipping(out, t, take_dir, dirs):
    k, win = 2, 1.5
    cpx = round(win * PPT * k)
    head = 22
    items = []
    sizes = hoses(take_dir)
    for d in dirs:
        for s in sizes[d]:
            gx, gy = s["gooseneck_axis"]
            nx, ny = s["nozzle"]
            items.append((d, True, f"{s['key']}: gooseneck, outlet", (gx, gy, 1.1)))
            items.append((d, True, f"{s['key']}: nozzle, boss", (nx, ny, 1.0)))
            f = s["connection"][2]
            n = FACE_N[f]
            r = s["ring_at"]
            if f in "NS":
                items.append((d, True, f"{s['key']}: wall fitting", (gx, r, ZA)))
            else:
                items.append((d, True, f"{s['key']}: wall fitting", (r, gy, ZA)))
        cf = chute_face(d)
        n = FACE_N[cf]
        fo = 2.496
        # the drive: chute frame u -0.19 across (east when facing north), v fo - 0.20
        u, vv = -0.19, fo - 0.20
        dx, dy = {"N": (u, vv), "E": (vv, -u), "S": (-u, -vv), "W": (-vv, u)}[cf]
        items.append((d, False, f"chute drive ({cf} face)", (dx, dy, 1.0)))
        items.append((d, False, f"chute port ({cf} face)", (n[0] * fo, n[1] * fo, 0.2)))
    d0 = dirs[0]
    for sx in (-1, 1):
        for sy in (-1, 1):
            items.append((d0, False, f"corner {'N' if sy > 0 else 'S'}{'E' if sx > 0 else 'W'}: leg, pad",
                          (sx * 2.1, sy * 2.1, 0.45)))
    for nm, (x, y, z) in (("SW bastion: door, chamfer", (-1.35, -1.85, 1.3)), ("SE bastion: panel, box", (1.2, -1.9, 1.3)),
                          ("SW roof: tank, lamp", (-1.4, -1.7, 2.2)), ("SE roof: bottles, 50", (1.45, -1.7, 2.2)),
                          ("SW manifold, S ram hose", (-0.9, -1.75, 0.95)), ("S ram, apron", (-0.4, -2.05, 0.9)),
                          ("W ram hoses", (-1.8, -1.0, 0.9)), ("W ram", (-2.06, -0.6, 0.9)),
                          ("E ram hose, drop", (1.8, -1.2, 1.3)), ("E ram", (2.06, -0.6, 0.9)),
                          ("N ram, hose", (-1.62, 0.95, 1.0)), ("NE bastion: door, stripe", (1.55, 1.2, 1.4)),
                          ("NW bastion: door, hoses", (-1.55, 1.2, 1.4)), ("NE house, roof", (1.4, 1.3, 2.9)),
                          ("NW house, roof", (-1.4, 1.3, 2.9)),
                          ("S face: ports, rings (dry)", (0.0, -2.496, 0.4)),
                          ("girder, posts SW", (-2.0, -2.0, 0.6)), ("girder, posts SE", (2.0, -2.0, 0.6)),
                          ("girder, posts NW", (-2.0, 2.0, 0.6)), ("girder, posts NE", (2.0, 2.0, 0.6)),
                          ("W strip: panel, bridge bolts", (-2.2, 0.15, 0.9)), ("E strip: patches, seam", (2.0, -0.25, 0.9)),
                          ("S apron: tread, seam", (0.0, -1.85, 0.9))):
        items.append((d0, False, nm, (x, y, z)))
    per_row = 6
    rows = -(-len(items) // per_row)
    W, H = per_row * cpx, 50 + rows * (cpx + head)
    sheet = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 8, "T03m clipping check, 2x nearest: every hose end, wall fitting, the chute's drive and port per direction "
          "(wet, covers); corners, bastions, roofs and services (dry)", 18, (240, 240, 240))
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
        label(dr, px + 4, py + 3, f"{d}{'' if wet else ' dry'}: {nm}"[:40], 12, (150, 210, 255))
    assert max(sheet.size) < 8000, sheet.size
    sheet.save(out)
    print(out, sheet.size, len(items), "crops")


def chute_strip(out, t, dirs):
    """The chute's frames per direction, 2x, composited on the plate (base, the chute frame, stroke frame 0)."""
    k, win = 2, 1.6
    cpx = round(win * PPT * k)
    head = 22
    size = (ts.CELL, ts.CELL)
    rows = []
    for d in dirs:
        m = t.plate[f"chute-{d}"] if f"chute-{d}" in t.plate else t.plate["chute"]
        nfr = m.get("frames", 1)
        cf = chute_face(d)
        n = FACE_N[cf]
        fo = 2.496
        sx, sy = ts.screen(n[0] * (fo - 0.25), n[1] * (fo - 0.25), 0.5)
        fr = []
        for f in range(nfr):
            c = Image.new("RGBA", size, v.GROUND + (255,))
            v.place(c, *t.frame("plate", f"base-{d}"))
            v.place(c, *t.frame("plate", f"chute-{d}", f))
            v.place(c, *t.frame("plate", f"stroke-{d}"))         # the press frame and its slung lines, over it
            fr.append(ps.window(c.convert("RGB"), sx - win / 2, sx + win / 2, sy - win / 2, sy + win / 2))
        rows.append((d, fr))
    per = max(len(fr) for _, fr in rows)
    sheet = Image.new("RGB", (per * cpx, 50 + len(rows) * (cpx + head)), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 8, "T03m: the chute's frames per direction, 2x, on the plate (its port and drive)", 18, (240, 240, 240))
    for r, (d, fr) in enumerate(rows):
        for i, c in enumerate(fr):
            c = c.resize((c.width * k, c.height * k), Image.NEAREST)
            sheet.paste(c, (i * cpx, 50 + r * (cpx + head) + head))
            label(dr, i * cpx + 4, 50 + r * (cpx + head) + 3, f"{d} frame {i}", 12, (150, 210, 255))
    assert max(sheet.size) < 8000, sheet.size
    sheet.save(out)
    print(out, sheet.size)


def anim_strip(out, t, dirs):
    """Every animation's frames: the ore per direction (24, 1x, around the mouth, on base + chute), and
    the stroke (24, north, 0.5x, the whole drill: base, chute, stroke frame f)."""
    import math
    head = 22
    rows = []
    win = 1.5
    for d in dirs:
        cf = chute_face(d)
        n = FACE_N[cf]
        fo = 2.496
        sx, sy = ts.screen(n[0] * (fo + 0.3), n[1] * (fo + 0.3), 0.1)
        fr = []
        for f in range(24):
            c = Image.new("RGBA", (ts.CELL, ts.CELL), v.GROUND + (255,))
            v.place(c, *t.frame("plate", f"base-{d}"))
            v.place(c, *t.frame("plate", f"chute-{d}", f % 5))
            v.place(c, *t.frame("plate", f"ore-{d}", f))
            fr.append(ps.window(c.convert("RGB"), sx - win / 2, sx + win / 2, sy - win / 2, sy + win / 2))
        rows.append((f"{d}: ore", fr))
    for half in (0, 1):
        fr = []
        for f in range(12 * half, 12 * half + 12):
            c = Image.new("RGBA", (ts.CELL, ts.CELL), v.GROUND + (255,))
            v.place(c, *t.frame("plate", f"base-{dirs[0]}"))
            v.place(c, *t.frame("plate", f"chute-{dirs[0]}", f % 5))
            v.place(c, *t.frame("plate", f"stroke-{dirs[0]}", f))
            c = c.convert("RGB")
            fr.append(c.resize((c.width // 2, c.height // 2), Image.LANCZOS))
        rows.append((f"{dirs[0]}: stroke {12 * half}-{12 * half + 11} (0.5x)", fr))
    W = max(sum(c.width for c in fr) for _, fr in rows)
    H = 40 + sum(head + max(c.height for c in fr) for _, fr in rows)
    sheet = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 8, "T03m: the ore's 24 frames per direction (1x, at its mouth) and the stroke's 24 (north, 0.5x)", 18,
          (240, 240, 240))
    y = 40
    for nm, fr in rows:
        label(dr, 4, y + 3, nm, 13, (150, 210, 255))
        x = 0
        for c in fr:
            sheet.paste(c, (x, y + head))
            x += c.width
        y += head + max(c.height for c in fr)
    assert max(sheet.size) < 8000, sheet.size
    sheet.save(out)
    print(out, sheet.size)


def parts_back(out, t, dirs):
    """T03m: close-ups (3x nearest) of what came back and what was added: each ram, its bulkhead and hose,
    dry and wet where a C2 hose passes over it; the corner girders and ladder posts; the plate top's detail."""
    k, win = 3, 1.3
    cpx = round(win * PPT * k)
    head = 22
    want = [
        ("W ram, hoses", (-1.9, -0.95, 0.9), ("east", "south")),
        ("E ram, hose", (1.92, -0.95, 0.9), ("south", "west")),
        ("S ram, hose", (-0.55, -1.95, 0.9), ("north", "west")),
        ("N ram, hose", (-1.65, 0.95, 0.9), ("north", "east")),
        ("girder, posts SW", (-2.0, -2.0, 0.5), ()), ("girder, posts SE", (2.0, -2.0, 0.5), ()),
        ("girder, posts NW", (-2.0, 2.0, 0.5), ()), ("girder, posts NE", (2.0, 2.0, 0.5), ()),
        ("W strip: panel, bridge bolts, wear", (-2.15, 0.0, 0.85), ()), ("E strip: patches, seam, bolts", (2.0, -0.2, 0.85), ()),
        ("S apron: tread, seam, wear", (0.0, -2.0, 0.85), ()), ("N apron: bridge bolts", (0.2, 2.2, 0.85), ()),
    ]
    items = []
    d0 = dirs[0]
    for nm, p, wets in want:
        items.append((d0, False, nm + " (dry)", p))
        for d in wets:
            if d in dirs:
                items.append((d, True, f"{nm} ({d}, wet)", p))
    per_row = 4
    rows = -(-len(items) // per_row)
    W, H = per_row * cpx, 50 + rows * (cpx + head)
    sheet = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    label(dr, 8, 8, "T03m: the parts that came back (rams and hoses, corner girders, ladder posts) and the plate top's "
          "detail, 3x nearest", 18, (240, 240, 240))
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
        label(dr, px + 4, py + 3, nm[:48], 13, (150, 210, 255))
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
    a, b, out = argv[:3]
    os.makedirs(out, exist_ok=True)
    ti = Take("T03l", a)
    tl = Take("T03m", b, one)
    dirs = (one,) if one else DIRS
    phone(os.path.join(out, "t03l-t03m-phone.png"), ti, tl, dirs)
    # (T03m: no sketch beside the render: the C2 sketch has the south face out at 2.74)
    hose_4x(os.path.join(out, "hoses-4x.png"), tl, b, dirs)
    clipping(os.path.join(out, "clipping-2x.png"), tl, b, dirs)
    chute_strip(os.path.join(out, "chute-strip.png"), tl, dirs)
    anim_strip(os.path.join(out, "anim-strip.png"), tl, dirs)
    parts_back(os.path.join(out, "parts-back-3x.png"), tl, dirs)


if __name__ == "__main__":
    main()
