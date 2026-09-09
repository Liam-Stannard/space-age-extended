#!/usr/bin/env python3
"""Build charge and discharge spritesheets from one glow plate.

Two mask shapes, because two buildings carry their light differently. The arc
mast's runs along a column, so its mask is a band travelling down or up
(--mode column, the default). The superconducting store's runs around a ring,
so its mask is an angular wedge sweeping round the centre (--mode ring) --
section 9 of that spec is explicit that the light must travel *around* the
channel rather than fill it like a bar, because a current going round a loop is
what the building physically is.

The original docstring, still true of the column mode:

Section 9 of the spec: charge is light arriving, travelling *down* from the tip
to the drum, bright, 19 frames. Discharge is light leaving, travelling *up* out
of the drum, about half as bright, dispersing at the insulator stack without
reaching the tip, 24 frames. Both are one-shot.

Neither is a separate piece of art. They are the same recovered light, revealed
along the column by a moving window and scaled by an envelope -- which is what
section 12 means by deriving frames rather than generating them. Generating 19
whole buildings would let the geometry drift; a mask cannot.

**What "a moving window" cost when it was not one.** The first version of this
tool lit everything behind the travelling head rather than a window with two
edges, and it zeroed the envelope at both ends of the sequence. The two
together meant the shipped sheets held one still picture that filled from one
end and then throbbed: measured off them, the whole column was lit by discharge
frame 20 of 24 and never changed again, and frames 00 and 18 of charge drew
nothing at all. The RGB channel is byte-identical across every frame of both
sheets and still is -- that is what deriving from one plate *means*, and it is
survivable only if the alpha genuinely moves. It was not moving. That is fine
for a sequence seen for four tenths of a second every ninety seconds, which is
what section 9 assumes the mast does. **It is not what the mast does.** The engine
plays the discharge animation whenever energy leaves the buffer, and the mast's
100 kW drain guarantees that a mast holding anything is discharging, so the
sequence replays back to back for as long as the buffer lasts -- confirmed on a
recording at 60 UPS, where three masts pulsed every 24 ticks for fourteen
seconds with no strike anywhere on the surface. The discharge sheet is the
mast's idle appearance, and has to survive being watched.
"""

import argparse
import math

from PIL import Image, ImageChops


def envelope(i, n):
    """Bright on the first frame, then falling away, still lit on the last.

    **The frame is a span of time, not an instant, so it is sampled at its
    middle.** The curve this replaces sampled at `i / (n - 1)`, which puts the
    first frame at t=0 and the last at t=1 -- and the old expression was
    exactly zero at both. Measured off the shipped sheets: charge frames 00 and
    18 were fully transparent and discharge 00 and 23 were too, so a fifth of
    the charge sequence was blank, and the blank frames were at the two moments
    that carry the read. Section 9 step 2 puts the tip flare on the *first*
    frame of charge -- "the whole tip flares violet-white as the arc lands" --
    and that frame drew nothing at all.

    There is no attack ramp any more, for the same reason. The old one took
    three frames to reach full, so the brightest moment of a strike landing was
    frame 3 rather than frame 0. An arc arrives instantly; the mask is what
    decides that only the tip is lit when it does.
    """
    t = (i + 0.5) / n
    return ((1.0 - t) / (1.0 - 0.5 / n)) ** 0.7


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


def band_mask(size, head, softness, downward, length=None, tail=None):
    """A window of light travelling along the column.

    `head` is the leading edge, `length` how far the light extends behind it
    and `tail` how far that trailing edge is feathered over -- both in the same
    0..1 units as `head`, fractions of the plate's height. `softness` feathers
    the leading edge.

    **A window, not a fill.** With `length = None` this is the original mask:
    everything behind the head stays lit, so the head reaching the bottom
    leaves the whole column alight and the only thing still changing is the
    envelope. Measured on the shipped sheets, that is what made the animation
    read as one still image being turned up and down -- by discharge frame 20
    of 24 the entire column was lit and nothing moved again. Give it a length
    and the lit region has two edges, so the light travels instead of filling.
    """
    w, h = size
    m = Image.new("L", (1, h))
    px = m.load()
    if tail is None:
        tail = softness
    for y in range(h):
        pos = y / (h - 1)
        d = (head - pos) if downward else (pos - head)
        if d < 0:                                   # ahead of the head
            v = 255 * (1 + d / softness) if d > -softness else 0
        elif length is None or d <= length:         # inside the window
            v = 255
        elif d < length + tail:                     # off the trailing edge
            v = 255 * (1 - (d - length) / tail)
        else:                                       # behind the window
            v = 0
        px[0, y] = max(0, min(255, int(v)))
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
          mode="column", centre=None, hold=False,
          travel=(-0.15, 1.02, 1.0), window=None, tail=None, keep=None,
          arch=None):
    """Cut one sheet.

    `travel` is the leading edge's schedule as `(start, stop, arrive)`: where it
    enters, where it comes to rest, and the fraction of the sequence it takes to
    get there. Charge arrives before the sequence ends -- the light reaches the
    drum and settles, which is section 9 step 4 -- so its `arrive` is short of 1
    and the remaining frames are spent closing the window onto the drum rather
    than sliding the head off the bottom of the plate.

    `window` is `(open, close)`: how far the light extends behind the head at
    the start, and what that has shrunk to by the last frame. `None` restores
    the fill this replaced. `tail` is how far the trailing edge is feathered
    over, and wants setting whenever `window` is: it defaults to the leading
    edge's 0.28, which is most of a 0.35 window and smears the back of the
    pulse across the plate until the thing stops reading as a pulse at all.

    `keep` is a span that stays lit for the whole sequence regardless of where
    the window has got to. It exists for one line of the spec: section 9 step 5
    wants the tip to be the last thing to fade, and a window that has travelled
    on would otherwise have taken the tip dark by frame 5.

    `arch` replaces the decaying envelope with one that rises to the middle of
    the sequence and comes back down to the same value it started at, floored
    at `arch` so it never reaches black. **A sequence the engine replays back
    to back needs matching ends**, and discharge is such a sequence -- see the
    module docstring. A decay envelope on a loop is a sawtooth, which is the
    throb this whole change exists to remove; an arch that starts and ends at
    the same brightness joins to its own next play, so what the player sees is
    one current running up the mast rather than the mast flashing. Charge keeps
    the decay, because charge really is the one-shot section 9 assumes.
    """
    w, h = glow.size
    cols = min(line_length, frames)
    rows = (frames + line_length - 1) // line_length
    out = Image.new("RGBA", (cols * w, rows * h), (0, 0, 0, 0))
    limit = limit_mask((w, h), *span) if span else None
    held = limit_mask((w, h), *keep) if keep else None

    for i in range(frames):
        u = i / (frames - 1)
        if mode == "ring":
            head = u * 1.02
            mask = wedge_mask((w, h), centre, head, 0.10, downward)
        else:
            start, stop, arrive = travel
            head = start + (stop - start) * min(1.0, u / arrive)
            length = None
            if window:
                length = window[0] + (window[1] - window[0]) * u
            mask = band_mask((w, h), head, 0.28, downward, length, tail)
            if held is not None:
                mask = ImageChops.lighter(mask, held)
        if limit:
            mask = ImageChops.multiply(mask, limit)
        # A ring that is filling should end full and stay full, not fade out
        # the way a pulse travelling down a mast does.
        if hold:
            e = min(1.0, (i + 1) / (frames * 0.25))
        elif arch:
            e = arch + (1.0 - arch) * math.sin(math.pi * (i + 0.5) / frames)
        else:
            e = envelope(i, frames)
        e *= gain
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
    # Charge: the window enters above the tip, races down, and arrives at the
    # drum at seven tenths of the sequence -- section 9 step 4, "the drum seams
    # brighten as the charge arrives and settles" -- after which the head holds
    # and the window closes onto it rather than sliding off the plate. The tip
    # is held lit throughout by `keep`, which is step 5's "the tip last to
    # fade". The content of the plate runs from 0.05 to 0.90, measured off its
    # own alpha, which is where 0.92 and the tip span come from.
    sheet(glow, 19, 8, True, 1.0, None,
          f"{args.out_dir}/charge.png",
          travel=(-0.15, 0.92, 0.70), window=(0.40, 0.30), tail=0.18,
          keep=(0.0, 0.16))
    # Discharge: half brightness, and confined below the insulator stack so it
    # disperses without ever reaching the electrode tip. It is a window all the
    # way -- nothing settles, because the whole reading is that the energy is
    # leaving -- and it ends over the stack rather than over the drum it left.
    sheet(glow, 24, 8, False, 0.5, (0.30, 1.0),
          f"{args.out_dir}/discharge.png",
          travel=(0.64, 0.30, 1.0), window=(0.30, 0.26), tail=0.12, arch=0.35)


if __name__ == "__main__":
    main()
