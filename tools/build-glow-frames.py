#!/usr/bin/env python3
"""Build the Arc Mast's charge and discharge spritesheets from one glow plate.

Section 9 of the spec: charge is light arriving, travelling *down* from the tip
to the drum, bright, 19 frames. Discharge is light leaving, travelling *up* out
of the drum, about half as bright, dispersing at the insulator stack without
reaching the tip, 24 frames. Both are one-shot.

Neither is a separate piece of art. They are the same recovered light, revealed
along the column by a moving window and scaled by an envelope -- which is what
section 12 means by deriving frames rather than generating them. Generating 19
whole buildings would let the geometry drift; a mask cannot.
"""

import argparse
from PIL import Image, ImageChops


def envelope(i, n, attack=0.15):
    """Bright immediately, then fall away to nothing by the last frame."""
    t = i / (n - 1)
    return min(1.0, t / attack) * (1.0 - t) ** 0.7 / (1.0 - attack) ** 0.7


def band_mask(size, head, softness, downward):
    """A vertical gradient: fully lit behind the travelling head, dark ahead."""
    w, h = size
    m = Image.new("L", (1, h))
    px = m.load()
    for y in range(h):
        pos = y / (h - 1)
        d = (head - pos) if downward else (pos - head)
        if d >= 0:
            v = 255
        elif d > -softness:
            v = int(255 * (1 + d / softness))
        else:
            v = 0
        px[0, y] = v
    return m.resize((w, h))


def limit_mask(size, top, bottom, soft=0.06):
    """Confine light to a vertical span (used to keep discharge off the tip)."""
    w, h = size
    m = Image.new("L", (1, h))
    px = m.load()
    for y in range(h):
        p = y / (h - 1)
        v = 255
        if p < top:
            v = int(255 * max(0.0, 1 - (top - p) / soft))
        elif p > bottom:
            v = int(255 * max(0.0, 1 - (p - bottom) / soft))
        px[0, y] = v
    return m.resize((w, h))


def sheet(glow, frames, line_length, downward, gain, span=None, path=""):
    w, h = glow.size
    cols = min(line_length, frames)
    rows = (frames + line_length - 1) // line_length
    out = Image.new("RGBA", (cols * w, rows * h), (0, 0, 0, 0))
    limit = limit_mask((w, h), *span) if span else None

    for i in range(frames):
        head = (i / (frames - 1)) * 1.35 - 0.15 if downward else 1.15 - (i / (frames - 1)) * 1.35
        mask = band_mask((w, h), head, 0.28, downward)
        if limit:
            mask = ImageChops.multiply(mask, limit)
        e = envelope(i, frames) * gain
        a = ImageChops.multiply(glow.getchannel("A"), mask)
        a = a.point(lambda p: min(255, int(p * e)))
        f = glow.copy()
        f.putalpha(a)
        out.paste(f, ((i % line_length) * w, (i // line_length) * h))

    out.save(path)
    print(f"  ok  {path}  {out.width}×{out.height}  "
          f"{frames} frames, {w}×{h} each, line_length {line_length}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glow", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    glow = Image.open(args.glow).convert("RGBA")
    sheet(glow, 19, 8, True, 1.0, None,
          f"{args.out_dir}/charge.png")
    # Discharge: half brightness, and confined below the insulator stack so it
    # disperses without ever reaching the electrode tip.
    sheet(glow, 24, 8, False, 0.5, (0.30, 1.0),
          f"{args.out_dir}/discharge.png")


if __name__ == "__main__":
    main()
