#!/usr/bin/env python3
"""Review sheets for the rig round (task ballast-drill-ports, T03e; T03f: rig-round-3).

  python3 take_sheet.py takes <out-prefix> <label>=<take out-dir> ...
      <out-prefix>-covers.png   per direction a row; per take its dry and wet columns, wet with
                                vanilla's covers; then vanilla's big drill dry and wet; 1.5x
      <out-prefix>-piped.png    the same, wet with vanilla's straight pipe on every connection
      <out-prefix>-top.png      the covers sheet's north and east rows alone (a copy that fits
                                a phone screen, for a first look)
  python3 take_sheet.py review <out.png> <label> <take out-dir>
      one take: per direction dry, wet (covers), wet (piped), the wet layers alone (behind,
      front, shadow), at 2x; and the clipping check: 4x crops (nearest, the sprite's own
      pixels) of every run end and connection (each junction, its sleeve and end ring against
      vanilla's cover and pipe) and of every corner the runs turn

How the drill is drawn (as the engine layers a wet drill, vanilla's order; the shadows one
union at half strength, emulated, not a client's):
  shadows; covers/pipes on tiles north of the centre; base (the take's plate); rig (behind);
  chute frame 0; stroke frame 0 (the take's own render of it over the cut-back body,
  rig-notes/stroke-f0-hi.png); rig-front; covers/pipes on tiles south of the centre.
Dry: the same with no rig and no covers (no fluid box connects on an ore with no fluid).
"""
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw

import vanilla_bmd as v

HERE = os.path.dirname(os.path.abspath(__file__))
SIGNED = os.path.normpath(os.path.join(HERE, "..", "sheets"))
CELL = 480
DIRS = v.DIRS


class Take:
    def __init__(self, label, d):
        self.label, self.dir = label, d
        # a take as take.sh leaves it (plate/sheets, rig/sheets) or as the round keeps it
        # (plate-sheets, rig-sheets: rig-round/takes/<take>, T03d's)
        kept = os.path.isdir(os.path.join(d, "plate-sheets"))
        self.plate_dir = os.path.join(d, "plate-sheets" if kept else "plate/sheets")
        self.rig_dir = os.path.join(d, "rig-sheets" if kept else "rig/sheets")
        self.plate = json.load(open(os.path.join(self.plate_dir, "meta.json")))
        rp = os.path.join(self.rig_dir, "meta.json")
        self.rig = json.load(open(rp)) if os.path.isfile(rp) else {}
        self.signed = json.load(open(os.path.join(SIGNED, "meta.json")))
        sp = os.path.join(d, "stroke-f0-hi.png" if kept else "plate/rig-notes/stroke-f0-hi.png")
        self.stroke = None
        if os.path.isfile(sp):
            im = Image.open(sp).convert("RGBa")
            self.stroke = im.resize((im.width // 4, im.height // 4), Image.LANCZOS).convert("RGBA")
        rj = os.path.join(d, "rig", "hi", "rig.json")
        self.sizes = json.load(open(rj)) if os.path.isfile(rj) else None

    def frame(self, where, stem, f=0):
        meta, base = {"plate": (self.plate, self.plate_dir),
                      "rig": (self.rig, self.rig_dir),
                      "signed": (self.signed, SIGNED)}[where]
        m = meta[stem]
        im = Image.open(os.path.join(base, stem + ".png")).convert("RGBA")
        w, h = m["size"]
        line = m.get("line_length", 1)
        f %= m.get("frames", 1)
        x, y = (f % line) * w, (f // line) * h
        return im.crop((x, y, x + w, y + h)), m["shift"]


def ours(t, d, wet=True, cover=True, size=(CELL, CELL)):
    c = Image.new("RGBA", size, v.GROUND + (255,))
    pieces = v.outside(v.conns(d), cover) if wet else []
    shadows = [t.frame("plate", f"base-shadow-{d}") + ((0, 0),)]
    if wet:
        shadows.append(t.frame("rig", f"rig-shadow-{d}") + ((0, 0),))
        shadows += [(sh, (0, 0), at) for _, sh, at, _ in pieces if sh is not None]
    c.alpha_composite(v.shadow_union(size, shadows))
    for im, _, at, over in pieces:
        if not over:
            v.place(c, im, (0, 0), at)
    v.place(c, *t.frame("plate", f"base-{d}"))
    if wet:
        v.place(c, *t.frame("rig", f"rig-{d}"))
    v.place(c, *t.frame("signed", f"chute-{d}"))
    if t.stroke is not None:
        # the stroke's frame 0 rendered whole on the model's canvas (416 x 400, origin 208, 200)
        c.alpha_composite(t.stroke, (round(size[0] / 2 - 208), round(size[1] / 2 - 200)))
    else:
        v.place(c, *t.frame("signed", f"stroke-{d}"))
    if wet:
        v.place(c, *t.frame("rig", f"rig-front-{d}"))
    for im, _, at, over in pieces:
        if over:
            v.place(c, im, (0, 0), at)
    return c


def label(dr, x, y, text, size=18, fill=(240, 200, 90)):
    dr.text((x, y), text, fill=fill, font=v.font(size))


def takes_sheet(prefix, takes):
    scale, crop = 1.5, 360
    C = round(crop * scale)
    head = 28
    for mode in ("covers", "piped"):
        cols = []
        for t in takes:
            cols.append((f"{t.label}: dry", lambda d, t=t: ours(t, d, wet=False)))
            cols.append((f"{t.label}: wet, {'covers' if mode == 'covers' else 'piped'}",
                         lambda d, t=t: ours(t, d, True, mode == "covers")))
        cols.append(("vanilla big drill: dry", lambda d: v.vanilla(d, wet=False, size=(CELL, CELL))))
        cols.append((f"vanilla: wet, {'covers' if mode == 'covers' else 'piped'}",
                     lambda d: v.vanilla(d, cover=mode == "covers", size=(CELL, CELL))))
        W, H = len(cols) * C, 50 + len(DIRS) * (C + head)
        assert max(W, H) < 8000, (W, H)
        sheet = Image.new("RGB", (W, H), (32, 32, 34))
        dr = ImageDraw.Draw(sheet)
        label(dr, 10, 12, f"Ballast drill fluid rig, T03f takes with the steel frame ({mode}), 1.5x, dry and wet, beside vanilla's big "
              "mining drill; footprint outlined, the direction's connection tiles ringed", 24, (240, 240, 240))
        m = (CELL - crop) // 2
        rows = []
        for r, d in enumerate(DIRS):
            y = 50 + r * (C + head)
            for k, (lab, fn) in enumerate(cols):
                label(dr, k * C + 8, y + 4, f"{d}: {lab}")
                im = v.grid(fn(d), conns_=v.conns(d)).convert("RGB").crop((m, m, m + crop, m + crop))
                sheet.paste(im.resize((C, C), Image.LANCZOS), (k * C, y + head))
            rows.append(y)
        sheet.save(f"{prefix}-{mode}.png")
        print(f"{prefix}-{mode}.png", sheet.size)
        if mode == "covers":
            top = sheet.crop((0, 0, W, 50 + 2 * (C + head)))
            k = min(1.0, 3000 / W)
            top.resize((round(W * k), round(top.height * k)), Image.LANCZOS).save(f"{prefix}-top.png")
            print(f"{prefix}-top.png")


def screen(x, y, z):
    """A model point (y north) on the 1x sheet: tiles right and down from the origin."""
    return x, -y - z / 2


def review(out, t):
    import rig_parts_geom as geo
    head = 28
    S2 = 2
    crop = 400
    C = crop * S2
    cols = [("dry", lambda d: ours(t, d, wet=False)), ("wet, vanilla covers", lambda d: ours(t, d)),
            ("wet, piped", lambda d: ours(t, d, True, False))]
    for stem, sh in (("rig", False), ("rig-front", False), ("rig-shadow", True)):
        def alone(d, stem=stem, sh=sh):
            c = Image.new("RGBA", (CELL, CELL), v.GROUND + (255,))
            g = ours(t, d, wet=False)
            g.putalpha(70)
            c.alpha_composite(g)
            im, shift = t.frame("rig", f"{stem}-{d}")
            if sh:
                s_ = Image.new("RGBA", im.size, (0, 0, 0, 0))
                s_.putalpha(im.getchannel("A").point(lambda a: a // 2))
                im = s_
            v.place(c, im, shift)
            return c
        cols.append(({"rig": "wet layer: behind", "rig-front": "wet layer: front",
                      "rig-shadow": "wet layer: shadow"}[stem], alone))
    # the clipping crops: per direction its four junctions and the corners its runs turn
    ends = geo.ends()
    CW, k4 = 1.25, 4
    cpx = round(CW * v.PPT * k4)
    per_row = 6
    W = max(len(cols) * C, per_row * cpx)
    n_crops = sum(len(ends[d]) for d in DIRS)
    crop_rows = -(-n_crops // per_row)
    H = 50 + len(DIRS) * (C + head) + 40 + crop_rows * (cpx + head)
    assert max(W, H) < 8000, (W, H)
    sheet = Image.new("RGB", (W, H), (32, 32, 34))
    dr = ImageDraw.Draw(sheet)
    label(dr, 10, 12, f"Ballast drill fluid rig, take {t.label}: dry, wet, the wet layers, 2x; then the clipping "
          "check, 4x (nearest)", 24, (240, 240, 240))
    m = (CELL - crop) // 2
    for r, d in enumerate(DIRS):
        y = 50 + r * (C + head)
        for k, (lab, fn) in enumerate(cols):
            label(dr, k * C + 8, y + 4, f"{d}: {lab}")
            im = v.grid(fn(d), conns_=v.conns(d)).convert("RGB").crop((m, m, m + crop, m + crop))
            sheet.paste(im.resize((C, C), Image.LANCZOS), (k * C, y + head))
    y0 = 50 + len(DIRS) * (C + head) + 40
    label(dr, 10, y0 - 34, "Clipping check, 4x: every run end (each junction: the run's flange into its head, the "
          "riser, the sleeve and end ring against vanilla's cover) and every corner, wet with covers", 20,
          (240, 240, 240))
    i = 0
    for d in DIRS:
        img = ours(t, d, size=(CELL + 160, CELL + 160))
        for name, (x, y, z) in ends[d]:
            sx, sy = screen(x, y, z)
            cx, cy = img.width / 2 + sx * v.PPT, img.height / 2 + sy * v.PPT
            h = CW / 2 * v.PPT
            c = img.crop((round(cx - h), round(cy - h), round(cx + h), round(cy + h)))
            c = c.resize((c.width * k4, c.height * k4), Image.NEAREST).convert("RGB")
            px, py = (i % per_row) * cpx, y0 + (i // per_row) * (cpx + head)
            label(dr, px + 6, py + 4, f"{d}: {name}", 16, (150, 210, 255))
            sheet.paste(c, (px, py + head))
            i += 1
    sheet.save(out)
    print(out, sheet.size)


def compare(out, old, takes):
    """T03d's take (old) beside each of this round's, 2x, on the pipework: per direction (north
    and east) the quarter where the runs turn a corner and meet their junctions."""
    head, k = 30, 2
    box = {"north": (-2.95, -1.7, 0.4, 2.95), "east": (-2.95, -0.2, 2.95, 2.95)}
    cols = [old] + takes
    cw = {d: round((b[2] - b[0]) * v.PPT * k) for d, b in box.items()}
    ch = {d: round((b[3] - b[1]) * v.PPT * k) for d, b in box.items()}
    W = max(cw.values()) * len(cols)
    H = 50 + sum(ch[d] + head for d in box)
    assert max(W, H) < 8000, (W, H)
    sheet = Image.new("RGB", (W, H), (32, 32, 34))
    dr = ImageDraw.Draw(sheet)
    label(dr, 10, 12, "The pipework at 2x: T03d's rigid take (first column) beside each T03e take, wet with vanilla's "
          "covers", 24, (240, 240, 240))
    y = 50
    for d, b in box.items():
        for i, t in enumerate(cols):
            img = ours(t, d, size=(CELL + 160, CELL + 160))
            cx, cy = img.width / 2, img.height / 2
            c = img.crop((round(cx + b[0] * v.PPT), round(cy + b[1] * v.PPT), round(cx + b[2] * v.PPT),
                          round(cy + b[3] * v.PPT)))
            c = c.resize((c.width * k, c.height * k), Image.LANCZOS).convert("RGB")
            x = i * max(cw.values())
            label(dr, x + 8, y + 4, f"{d}: {'T03d ' if i == 0 else 'T03e '}{t.label}")
            sheet.paste(c, (x, y + head))
        y += ch[d] + head
    sheet.save(out)
    print(out, sheet.size)


def main():
    a = sys.argv[1:]
    if a[0] == "takes":
        takes = [Take(*x.split("=", 1)) for x in a[2:]]
        takes_sheet(a[1], takes)
    elif a[0] == "compare":
        old = Take(*a[2].split("=", 1))
        compare(a[1], old, [Take(*x.split("=", 1)) for x in a[3:]])
    elif a[0] == "review":
        review(a[1], Take(a[2], a[3]))


if __name__ == "__main__":
    main()
