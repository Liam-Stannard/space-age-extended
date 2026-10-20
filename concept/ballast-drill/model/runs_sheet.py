#!/usr/bin/env python3
"""The contact sheet of the fitting-run takes (task ballast-drill-ports, T03c): per direction a
row, per take a column, then vanilla's big mining drill with its pipe connections, all drawn
as fittings_sheet.py draws them (its ours() and vanilla()), at 2x on its ground.

  python3 runs_sheet.py <signed-off sheets> <out.png> [--piped] <label>=<fittings sheets> ...

Unpiped by default: vanilla's cover at each connection, as a drill on its own shows it;
--piped puts vanilla's straight pipe on every connection instead.
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fittings_sheet as fs  # noqa: E402

SCALE = 2
CROP = 400                           # 1x px of each cell kept, about the centre: 6.25 tiles


def main():
    a = sys.argv[1:]
    piped = "--piped" in a
    a = [x for x in a if x != "--piped"]
    sig, out = fs.Sheets(a[0]), a[1]
    takes = [(lab, fs.Sheets(p)) for lab, p in (x.split("=", 1) for x in a[2:])]
    cols = [(lab, (lambda d, t=t: fs.ours(sig, d, t, not piped))) for lab, t in takes]
    cols.append(("vanilla big mining drill", fs.vanilla))
    C, HEAD = CROP * SCALE, 30
    W, H = len(cols) * C, 44 + len(fs.DIRS) * (C + HEAD)
    assert max(W, H) < 8000, (W, H)
    sheet = Image.new("RGB", (W, H), (32, 32, 34))
    dr = ImageDraw.Draw(sheet)
    dr.text((10, 10), "Ballast drill fitting runs, T03c takes (%s), 2x, beside vanilla's big mining drill"
            % ("piped" if piped else "vanilla covers"), fill=(240, 240, 240), font=fs.font(24))
    for r, d in enumerate(fs.DIRS):
        y = 44 + r * (C + HEAD)
        for k, (lab, fn) in enumerate(cols):
            dr.text((k * C + 8, y + 4), f"{d}: {lab}", fill=(240, 200, 90), font=fs.font(20))
            m = (fs.CELL - CROP) // 2
            im = fs.grid(fn(d)).convert("RGB").crop((m, m, m + CROP, m + CROP)).resize((C, C), Image.LANCZOS)
            sheet.paste(im, (k * C, y + HEAD))
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
