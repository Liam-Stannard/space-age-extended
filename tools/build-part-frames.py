#!/usr/bin/env python3
"""Turn one part plate into an animation sheet, by transform.

The other half of `cut-part-by-mask.py`. That gets a component out of the
approved plate, registered, in its own place on the plate's canvas. This moves
it, and writes the frames as a sheet Factorio can load.

**Nothing here is drawn.** Every frame is the same pixels under a different
transform, which is the whole reason the part was cut rather than generated:
a transform cannot let the geometry drift, and a generator cannot help it. That
argument is `build-glow-frames.py`'s and it is the same argument.

**The engine cannot do this for you.** `animated_shift` on a working
visualisation is parsed by a crafting machine but follows
`shift_animation_waypoints`, which is a `MiningDrillPrototype` field -- probed
on 2.1.17, an assembling machine silently ignores it on both `graphics_set` and
the prototype root. There is no free shift. It is frames or it is nothing.

**Which motions are honest, and which are a lie:**

    slide   a piston, ram or shuttle moving along its axis      yes
    spin    a wheel or fan whose face is toward the camera      yes
    shake   the whole machine oscillating on its mounts         yes
    --      a drum, turntable or arm rotating out of the
            view plane                                          NO

That last row is not a gap in this tool, it is a fact about pictures.
`build-crane-sheets.py` is kept in the tree as the record of trying anyway: one
drawing stamped into every frame gives a part whose shading and self-occlusion
never change as it turns, and vanilla's own sheets show genuinely different
views at every angle. Rotating a three-quarter-view drum with `spin` will spin
its *highlights* round with it, and it reads as a sticker on a turntable. Use
`spin` when the axis points at the camera and not otherwise.

Usage:
  tools/build-part-frames.py --part drive.png --mode spin --frames 16 \\
      --out graphics/entity/<b>/drive.png
  tools/build-part-frames.py --part base.png --mode shake --frames 8 \\
      --amplitude 2 --axis 70 --out graphics/entity/<b>/shake.png
"""

import argparse
import math
import sys

from PIL import Image, ImageChops, ImageStat


def centroid(im):
    """Alpha-weighted centre of the part -- measured, not guessed."""
    a = im.getchannel("A")
    w, h = a.size
    px = a.load()
    tx = ty = tot = 0
    for y in range(h):
        for x in range(w):
            v = px[x, y]
            if v:
                tx += x * v
                ty += y * v
                tot += v
    if not tot:
        sys.exit("the part plate is empty")
    return tx / tot, ty / tot


def offset_frame(im, dx, dy):
    """Translate on the same canvas. Not ImageChops.offset, which wraps."""
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (int(round(dx)), int(round(dy))))
    return out


def frames_for(im, mode, n, amp, axis_deg, centre, secondary):
    out = []
    ang = math.radians(axis_deg)
    for i in range(n):
        t = i / n                                  # 0 <= t < 1, so frame n == frame 0
        if mode == "spin":
            out.append(im.rotate(360.0 * t, resample=Image.BICUBIC,
                                 center=centre))
        else:
            s = math.sin(2 * math.pi * t)
            d = amp * s
            dx, dy = d * math.cos(ang), d * math.sin(ang)
            if mode == "shake" and secondary:
                # A perpendicular component at twice the rate, so the path is a
                # figure of eight rather than a line. A machine on springs does
                # not oscillate along one axis, and a straight line reads as the
                # sprite sliding rather than the machine shaking.
                s2 = math.sin(4 * math.pi * t) * secondary
                dx += s2 * math.cos(ang + math.pi / 2)
                dy += s2 * math.sin(ang + math.pi / 2)
            out.append(offset_frame(im, dx, dy))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True,
                    help="the part on the plate's canvas, from cut-part-by-mask.py")
    ap.add_argument("--mode", choices=("spin", "slide", "shake"), required=True)
    ap.add_argument("--frames", type=int, default=16)
    ap.add_argument("--line-length", type=int, default=8)
    ap.add_argument("--amplitude", type=float, default=2.0,
                    help="pixels, for slide and shake")
    ap.add_argument("--axis", type=float, default=90.0,
                    help="degrees, 0 = east, 90 = south; the line of travel")
    ap.add_argument("--secondary", type=float, default=0.0,
                    help="shake only: perpendicular amplitude, in pixels")
    ap.add_argument("--centre", nargs=2, type=float,
                    help="spin only: rotation centre; default is the part's centroid")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    im = Image.open(a.part).convert("RGBA")
    centre = tuple(a.centre) if a.centre else centroid(im)
    if a.mode == "spin":
        print("  rotation centre %.1f, %.1f%s"
              % (centre[0], centre[1], "" if a.centre else " (measured centroid)"))

    fr = frames_for(im, a.mode, a.frames, a.amplitude, a.axis, centre, a.secondary)

    # A cycle whose frames are not distinct is a still with extra file size.
    dup = sum(1 for i in range(len(fr))
              if ImageChops.difference(fr[i].convert("RGB"),
                                       fr[i - 1].convert("RGB")).getbbox() is None)
    if dup:
        print(f"  WARNING: {dup} of {a.frames} frames are identical to their "
              f"predecessor. Raise --amplitude or lower --frames: a {a.amplitude}px "
              f"amplitude cannot make {a.frames} distinct integer offsets.")

    w, h = im.size
    cols = min(a.line_length, a.frames)
    rows = (a.frames + a.line_length - 1) // a.line_length
    sheet = Image.new("RGBA", (cols * w, rows * h), (0, 0, 0, 0))
    for i, f in enumerate(fr):
        sheet.paste(f, ((i % a.line_length) * w, (i // a.line_length) * h))
    sheet.save(a.out)

    moved = [ImageStat.Stat(ImageChops.difference(
        f.convert("RGB"), fr[0].convert("RGB"))).mean[0] for f in fr]
    print(f"  ok  {a.out}  {sheet.width}×{sheet.height}  "
          f"{a.frames} frames, {w}×{h} each, line_length {a.line_length}")
    print(f"      per-frame change against frame 0: "
          f"{min(moved):.1f} .. {max(moved):.1f}")


main()
