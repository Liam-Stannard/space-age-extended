#!/usr/bin/env python3
"""The Siderane turbine's rotor running, as a GIF: both directions at 1x, the horizontal at 2x.

  python3 rotor_gif.py <out-dir> <rotor.gif> [--ms 50]

<out-dir> is render.sh's output directory (its renders/). Each frame is the stopped machine
as review_sheet.py composes it (shadow at 50 %, the plate, the rotor frame) on the review
ground; the loop is the rotor's own ROTOR_FRAMES frames, repeated.
"""
import json
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compare_plates as cp  # noqa: E402
import review_sheet as rs  # noqa: E402


def main():
    out_dir, out = sys.argv[1], sys.argv[2]
    ms = int(sys.argv[sys.argv.index("--ms") + 1]) if "--ms" in sys.argv else 50
    rd = os.path.join(out_dir, "renders")
    n = json.load(open(os.path.join(rd, "render.json")))["animations"][0]["frames"]
    c, h = cp.S // 2, int(1.75 * cp.PPT)
    frames = []
    for f in range(n):
        hz, vt = rs.composed(rd, "horizontal", f), rs.composed(rd, "vertical", f)
        zoom = hz.crop((c - h, c - h, c + h, c + h)).resize((4 * h, 4 * h), Image.NEAREST)
        im = Image.new("RGBA", (2 * cp.S + zoom.width, max(cp.S, zoom.height)), (30, 30, 30, 255))
        im.paste(hz, (0, 0))
        im.paste(vt, (cp.S, 0))
        im.paste(zoom, (2 * cp.S, 0))
        frames.append(im.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT))
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=ms, loop=0, optimize=True)
    print(out, os.path.getsize(out), "bytes", n, "frames")


if __name__ == "__main__":
    main()
