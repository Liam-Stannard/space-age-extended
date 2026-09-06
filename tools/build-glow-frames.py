#!/usr/bin/env python3
"""Build charge and discharge spritesheets from one glow plate.

Two mask shapes, because two buildings carry their light differently. The arc
mast's runs along a column, so its mask is a band travelling down or up
(--mode column, the default, and the arc mast's sheets are unchanged by the
addition). The superconducting store's runs around a ring, so its mask is an
angular wedge sweeping round the centre (--mode ring) -- section 9 of that
spec is explicit that the light must travel *around* the channel rather than
fill it like a bar, because a current going round a loop is what the building
physically is.

The original docstring, still true of the column mode:

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


def ring_centre(glow):
    """Centroid of the lit pixels -- the middle of the ring, measured not guessed."""
    a = glow.getchannel("A")
    w, h = a.size
    px = a.load()
    tx = ty = tot = 0
    for y in range(h):
        for x in range(w):
            v = px[x, y]
            if v > 8:
                tx += x * v
                ty += y * v
                tot += v
    if not tot:
        return w / 2, h / 2
    return tx / tot, ty / tot


def wedge_mask(size, centre, head, softness, clockwise):
    """An angular sweep: lit behind the travelling head, dark ahead of it.

    `head` runs 0..1 as a fraction of a full turn, starting at twelve o'clock,
    so a frame at 0.25 has a quarter of the ring alight. The softness is also
    in turns, and feathers the leading edge so the head does not read as a
    hard-cut sector.
    """
    import math
    w, h = size
    cx, cy = centre
    m = Image.new("L", (w, h))
    px = m.load()
    for y in range(h):
        for x in range(w):
            ang = math.atan2(x - cx, cy - y) / (2 * math.pi)   # 0 at 12 o'clock
            if ang < 0:
                ang += 1.0
            if not clockwise:
                ang = 1.0 - ang
            d = head - ang
            if d >= 0:
                v = 255
            elif d > -softness:
                v = int(255 * (1 + d / softness))
            else:
                v = 0
            px[x, y] = v
    return m


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


def sheet(glow, frames, line_length, downward, gain, span=None, path="",
          mode="column", centre=None, hold=False):
    w, h = glow.size
    cols = min(line_length, frames)
    rows = (frames + line_length - 1) // line_length
    out = Image.new("RGBA", (cols * w, rows * h), (0, 0, 0, 0))
    limit = limit_mask((w, h), *span) if span else None

    for i in range(frames):
        if mode == "ring":
            head = (i / (frames - 1)) * 1.02
            mask = wedge_mask((w, h), centre, head, 0.10, downward)
        else:
            head = (i / (frames - 1)) * 1.35 - 0.15 if downward \
                else 1.15 - (i / (frames - 1)) * 1.35
            mask = band_mask((w, h), head, 0.28, downward)
        if limit:
            mask = ImageChops.multiply(mask, limit)
        # A ring that is filling should end full and stay full, not fade out
        # the way a pulse travelling down a mast does.
        e = (min(1.0, (i + 1) / (frames * 0.25)) if hold
             else envelope(i, frames)) * gain
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
    ap.add_argument("--mode", choices=("column", "ring"), default="column")
    args = ap.parse_args()

    glow = Image.open(args.glow).convert("RGBA")
    if args.mode == "ring":
        centre = ring_centre(glow)
        print(f"  ring centre measured at ({centre[0]:.1f}, {centre[1]:.1f})")
        # Charge fills the ring clockwise and holds it lit; discharge empties it
        # the other way at half brightness. Direction carries the meaning.
        sheet(glow, 20, 5, True, 1.0, None,
              f"{args.out_dir}/charge.png", "ring", centre, hold=True)
        sheet(glow, 20, 5, False, 0.55, None,
              f"{args.out_dir}/discharge.png", "ring", centre, hold=True)
        return
    sheet(glow, 19, 8, True, 1.0, None,
          f"{args.out_dir}/charge.png")
    # Discharge: half brightness, and confined below the insulator stack so it
    # disperses without ever reaching the electrode tip.
    sheet(glow, 24, 8, False, 0.5, (0.30, 1.0),
          f"{args.out_dir}/discharge.png")


if __name__ == "__main__":
    main()
