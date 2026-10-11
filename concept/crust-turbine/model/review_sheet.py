#!/usr/bin/env python3
"""The Siderane turbine's review sheet: the new plate beside the adopted one, idle and
working, and a frame strip of the rotor.

  python3 review_sheet.py <out-dir> <review.png>

<out-dir> is render.sh's output directory: its renders/ (sprite size, the model's canvas,
origin at the centre) and sheets/meta.json (the pack checks). One row per direction, on
one ground at 64 px a tile with the footprint's grid:

  adopted   master-v2.png, as compare_plates.py places it
  idle      the shadow at 50 %, the plate, the rotor at frame 0 -- the stopped machine
  working   the same with the rotor at frame ROTOR_FRAMES / 2: a generator has no working
            layers, only its animation running (GeneratorPictures: animation, frozen_patch)

then every rotor frame in a strip, at 3x, cut to the rotor's window. The pack checks
under each row.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compare_plates as cp  # noqa: E402


def composed(rd, d, f):
    im = cp.panel(d)
    cp.centred(im, Image.open(os.path.join(rd, f"shadow-{d}.png")).convert("RGBA"), alpha=0.5, black=True)
    cp.centred(im, Image.open(os.path.join(rd, f"idle-{d}.png")).convert("RGBA"))
    cp.centred(im, Image.open(os.path.join(rd, f"rotor-{f:02d}-{d}.png")).convert("RGBA"))
    return im


def main():
    out_dir, out = sys.argv[1], sys.argv[2]
    rd = os.path.join(out_dir, "renders")
    decl = json.load(open(os.path.join(rd, "render.json")))
    meta = json.load(open(os.path.join(out_dir, "sheets", "meta.json")))
    n = decl["animations"][0]["frames"]
    PAD, LBL = 10, 20
    rows = []
    for d in ("horizontal", "vertical"):
        panels = [("adopted master-v2", cp.adopted(d)), (f"idle, {d}", composed(rd, d, 0)),
                  (f"working (rotor frame {n // 2}), {d}", composed(rd, d, n // 2))]
        # the strip: the rotor's bounding box over every frame, from the composed frames
        frames = [composed(rd, d, f) for f in range(n)]
        u = None
        for f in range(n):
            bb = Image.open(os.path.join(rd, f"rotor-{f:02d}-{d}.png")).getchannel("A").point(
                lambda v: 255 if v > 8 else 0).getbbox()
            u = bb if u is None else (min(u[0], bb[0]), min(u[1], bb[1]), max(u[2], bb[2]), max(u[3], bb[3]))
        ox = (cp.S - decl["canvas"][0]) // 2
        oy = (cp.S - decl["canvas"][1]) // 2
        box = (u[0] + ox - 4, u[1] + oy - 4, u[2] + ox + 4, u[3] + oy + 4)
        strip = [fr.crop(box).resize(((box[2] - box[0]) * 3, (box[3] - box[1]) * 3), Image.NEAREST) for fr in frames]
        checks = meta["checks"][d]
        txt = "  ".join(f"{k} {v[0] if isinstance(v, list) and k != 'half_width_tiles' and k != 'footprint_rows_tiles' else v}"
                        for k, v in checks.items())
        rows.append((d, panels, strip, txt))
    sw = max(sum(s.width + 4 for s in r[2]) for r in rows)
    W = max(3 * (cp.S + PAD) + PAD, sw + 2 * PAD)
    H = 40 + sum(LBL + cp.S + 30 + LBL + r[2][0].height + PAD * 2 for r in rows)
    sheet = Image.new("RGBA", (W, H), (30, 30, 30, 255))
    dr = ImageDraw.Draw(sheet)
    dr.text((PAD, 10), "Siderane turbine -- review", fill=(230, 230, 230, 255), font=cp.font(18))
    y = 40
    for d, panels, strip, txt in rows:
        for i, (lbl, p) in enumerate(panels):
            x = PAD + i * (cp.S + PAD)
            dr.text((x, y + 3), lbl, fill=(220, 220, 220, 255), font=cp.font(13))
            sheet.paste(p, (x, y + LBL))
        y += LBL + cp.S + 2
        dr.text((PAD, y), txt[:260], fill=(200, 200, 200, 255), font=cp.font(10))
        dr.text((PAD, y + 13), txt[260:520], fill=(200, 200, 200, 255), font=cp.font(10))
        y += 28
        dr.text((PAD, y + 3), f"rotor, frames 0-{n - 1}, {d}, 3x", fill=(220, 220, 220, 255), font=cp.font(13))
        x = PAD
        for s in strip:
            sheet.paste(s, (x, y + LBL))
            x += s.width + 4
        y += LBL + strip[0].height + PAD * 2
    sheet.convert("RGB").save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
