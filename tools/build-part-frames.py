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

**Which motions are honest, and which are a lie.** The test is not "does it
rotate out of the view plane" -- that was this tool's first answer and it was
wrong. The test is **does the silhouette change**:

    slide   a piston, ram or shuttle along its axis             yes
    spin    a wheel or fan whose face is toward the camera      yes
    ribs    a drum whose surface carries a repeating feature    yes, best
    scroll  the same, but moving the shading with it            yes, worse
    shake   the whole machine oscillating on its mounts         yes
    --      an arm, crane or turntable that presents a
            different shape at every angle                      NO

A cylinder spinning about its own axis never changes outline, and nothing on it
occludes anything else that was not already occluded. What moves is the surface:
a mark on the drum travels down the visible face, leaves at the bottom edge,
goes round the back and returns at the top. That is a wrap-scroll, and it is
exactly right rather than an approximation.

An arm is the opposite, and that is what `build-crane-sheets.py` is kept in the
tree to record: vanilla's own sheets show genuinely different views at every
angle -- different shading, different self-occlusion, and some frames *empty*
because the part is hidden. One drawing stamped into all of them gives an arm
whose segments never change as it swings. No transform recovers that; it needs a
3D model or a recolour of vanilla's, which is `tools/recolour-crane.py`.

`spin` is for a face pointed at the camera. Used on a drum seen from the side it
rotates the drum's *highlights and foreshortening* with it, and the result is a
barrel tumbling end over end -- tried on the Dross Classifier's drive, and it
looks exactly as wrong as it sounds.

**Prefer `ribs` to `scroll` on any drum.** `scroll` carries the whole region
round, shading included, and a barrel's light and shade belong to the lamp
rather than to the metal: the bright side must stay bright while the surface
runs under it. `ribs` splits the two first and freezes the shading. Measured on
the Classifier's drum across twelve frames, mean per-pixel movement of the
low-frequency component: **23.2 under `scroll`, 6.2 under `ribs`** -- a
73 per cent reduction -- while keeping two thirds of the rib travel. On screen
`scroll` visibly lurches and `ribs` does not.

Usage:
  tools/build-part-frames.py --part drive.png --mode spin --frames 16 \\
      --out graphics/entity/<b>/drive.png
  tools/build-part-frames.py --part base.png --mode shake --frames 8 \\
      --amplitude 2 --axis 70 --out graphics/entity/<b>/shake.png
  tools/build-part-frames.py --part drive.png --mode scroll --frames 12 \\
      --region 106 5 130 46 --out graphics/entity/<b>/drum.png
"""

import argparse
import importlib.util
import math
import os
import sys

from PIL import Image, ImageChops, ImageStat


def _shadow_fn():
    """Borrow process-building-art.py's shadow projection rather than restating it.

    Its kx/ky/blur are measured off vanilla's lightning collector; a second copy
    of those numbers here is a second copy to drift.
    """
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "process-building-art.py")
    spec = importlib.util.spec_from_file_location("pba", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.shadow


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


def scroll_frame(im, region, turn, horizontal=False):
    """Rotate a cylinder about its own axis, by warping its visible face.

    **Not a shift.** A drum's surface does not slide down the screen at a
    constant rate: a mark near the axis moves fastest and one near the rim
    barely moves at all, because it is turning away from the camera. Scrolling
    the region as a block gives a drum that visibly slides, with a hard seam
    where the wrap lands -- tried, and it looks like a barrel falling out of its
    mount.

    So each output row is sampled from where that surface point *was*. With the
    face spanning -1..1 across the region, a row at `u` sits at angle
    `asin(u)`, and one turn of `turn` radians earlier it was at `sin(asin(u) -
    turn)`. That is continuous, and periodic in `turn` with period 2*pi, so the
    cycle closes by construction.

    The far half of the drum is not in the plate and cannot be, so this repeats
    the visible half behind. On a drum banded round its circumference -- which
    is what a drive flywheel is -- that is invisible. On one with a single
    painted mark it would show as the mark appearing twice per turn.

    The alpha of the original goes back afterwards: the silhouette of a cylinder
    turning about its own axis does not change, which is the whole reason this
    is derivable at all.
    """
    x0, y0, x1, y1 = (int(v) for v in region)
    if horizontal:
        im = im.transpose(Image.ROTATE_90)
        w, h = im.size
        x0, y0, x1, y1 = y0, w - x1, y1, w - x0

    out = im.copy()
    src = im.load()
    dst = out.load()
    r = (y1 - y0) / 2.0
    yc = y0 + r
    for y in range(y0, y1):
        u = max(-1.0, min(1.0, (y + 0.5 - yc) / r))
        # Wrap the angle round the barrel rather than letting sin() fold it
        # back. sin(pi - x) == sin(x), so the naive form mirrors at the rim
        # instead of continuing, and a rib that should march off the bottom edge
        # instead reverses and smears a single source row across half the face.
        # Taking the angle modulo pi carries it round continuously. The far half
        # of the drum is not in the plate, so this repeats the visible half
        # behind -- invisible on a barrel whose ribs already repeat.
        theta = ((math.asin(u) - turn + math.pi / 2) % math.pi) - math.pi / 2
        sy = int(round(yc + r * math.sin(theta) - 0.5))
        sy = max(y0, min(y1 - 1, sy))
        for x in range(x0, x1):
            px = src[x, sy]
            # Only take a sample that is actually on the drum. The region is a
            # rectangle and the drum is not, so a naive warp pulls transparent
            # pixels into the middle of the part -- which arrives as black,
            # because the alpha is restored afterwards and transparent RGB is
            # zero. Off the surface, the pixel stays where it was.
            if px[3] > 0:
                dst[x, y] = px
    out.putalpha(im.getchannel("A"))

    if horizontal:
        out = out.transpose(Image.ROTATE_270)
    return out



def split_ribs(im, region, window=5):
    """Split a barrel into the shading that stays and the ribs that turn.

    **The shading must not rotate.** A barrel's light and shade belong to the
    lamp, not to the metal: the bright side stays bright while the surface runs
    under it. `scroll` moves everything inside the region together, so it drags
    the shading round with the ribs, which is the same mistake as a baked
    specular only smaller.

    So the region is separated first. Smoothing each column along the axis of
    travel leaves the low-frequency part -- the barrel's own light and shade,
    the *frozen base*. Subtracting that leaves the high-frequency part, which is
    the ribs and nothing else. The base is then drawn at rest in every frame and
    only the residual is carried round, so nothing outside the ribs can flicker.

    Returns (base, residual). The residual is signed and offset by 128.
    """
    x0, y0, x1, y1 = (int(v) for v in region)
    src = im.load()
    base, resid = {}, {}
    half = window // 2
    for x in range(x0, x1):
        col = [(y, src[x, y]) for y in range(y0, y1)]
        for k, (y, px) in enumerate(col):
            if px[3] == 0:
                base[x, y] = px
                resid[x, y] = (128, 128, 128)
                continue
            acc = [0, 0, 0]
            n = 0
            for j in range(max(0, k - half), min(len(col), k + half + 1)):
                q = col[j][1]
                if q[3] > 0:
                    for c in range(3):
                        acc[c] += q[c]
                    n += 1
            sm = tuple(a // n for a in acc) if n else px[:3]
            base[x, y] = (sm[0], sm[1], sm[2], px[3])
            resid[x, y] = tuple(max(0, min(255, px[c] - sm[c] + 128)) for c in range(3))
    return base, resid


def ribs_frame(im, region, turn, base, resid):
    """One phase: the frozen base, with the rib residual carried round on to it."""
    x0, y0, x1, y1 = (int(v) for v in region)
    out = im.copy()
    dst = out.load()
    r = (y1 - y0) / 2.0
    yc = y0 + r
    for y in range(y0, y1):
        u = max(-1.0, min(1.0, (y + 0.5 - yc) / r))
        theta = ((math.asin(u) - turn + math.pi / 2) % math.pi) - math.pi / 2
        sy = max(y0, min(y1 - 1, int(round(yc + r * math.sin(theta) - 0.5))))
        for x in range(x0, x1):
            b = base[x, y]
            if b[3] == 0:
                continue
            d = resid[x, sy]
            dst[x, y] = (max(0, min(255, b[0] + d[0] - 128)),
                         max(0, min(255, b[1] + d[1] - 128)),
                         max(0, min(255, b[2] + d[2] - 128)),
                         b[3])
    return out


def frames_for(im, mode, n, amp, axis_deg, centre, secondary, region=None,
               turns=1.0, window=5):
    out = []
    split = split_ribs(im, region, window) if mode == "ribs" else None
    ang = math.radians(axis_deg)
    for i in range(n):
        t = i / n                                  # 0 <= t < 1, so frame n == frame 0
        if mode == "spin":
            out.append(im.rotate(360.0 * t, resample=Image.BICUBIC,
                                 center=centre))
        elif mode == "ribs":
            turn = 2 * math.pi * turns * t * (1 if amp >= 0 else -1)
            out.append(ribs_frame(im, region, turn, *split))
        elif mode == "scroll":
            # `turns` of a revolution across the sequence. A full turn is not
            # usually what you want: only the front half of a drum is in the
            # plate, so a large rotation has to invent the back, and it shows.
            # A ribbed barrel is periodic, so a few rib pitches land frame n
            # back on frame 0 just as exactly as a whole revolution does, and
            # stay inside the surface the plate actually has.
            turn = 2 * math.pi * turns * t * (1 if amp >= 0 else -1)
            out.append(scroll_frame(im, region, turn,
                                    horizontal=(axis_deg % 180 == 0)))
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
    ap.add_argument("--mode", choices=("spin", "slide", "shake", "scroll", "ribs"), required=True)
    ap.add_argument("--frames", type=int, default=16)
    ap.add_argument("--line-length", type=int, default=8)
    ap.add_argument("--amplitude", type=float, default=2.0,
                    help="pixels, for slide and shake")
    ap.add_argument("--axis", type=float, default=90.0,
                    help="degrees, 0 = east, 90 = south; the line of travel")
    ap.add_argument("--secondary", type=float, default=0.0,
                    help="shake only: perpendicular amplitude, in pixels")
    ap.add_argument("--window", type=int, default=5,
                    help="ribs only: how many rows to smooth over when splitting "
                         "the shading from the ribs. About one rib pitch at the "
                         "widest part of the barrel.")
    ap.add_argument("--turns", type=float, default=1.0,
                    help="scroll only: revolutions the sequence covers. Set it "
                         "to a whole number of the surface's repeats -- four rib "
                         "pitches of a 24-rib drum is 1/6 -- so the cycle closes "
                         "without rotating past the half of the drum the plate has.")
    ap.add_argument("--region", nargs=4, type=float,
                    help="scroll only: x0 y0 x1 y1 of the surface that turns, "
                         "measured off the plate; default is the part's bbox")
    ap.add_argument("--centre", nargs=2, type=float,
                    help="spin only: rotation centre; default is the part's centroid")
    ap.add_argument("--out", required=True)
    ap.add_argument("--shadow-out",
                    help="also write the matching draw_as_shadow sheet. A part "
                         "that moves casts a shadow that moves with it, and "
                         "vanilla ships one per phase -- the electromagnetic "
                         "plant has shadow-warm-up, shadow-rotate, "
                         "shadow-rotate-continue and shadow-cool-down.")
    a = ap.parse_args()

    im = Image.open(a.part).convert("RGBA")
    centre = tuple(a.centre) if a.centre else centroid(im)
    if a.mode == "spin":
        print("  rotation centre %.1f, %.1f%s"
              % (centre[0], centre[1], "" if a.centre else " (measured centroid)"))

    region = tuple(int(v) for v in a.region) if a.region else im.getchannel("A").getbbox()
    if a.mode in ("scroll", "ribs"):
        print("  %s inside %s%s"
              % (a.mode, region, "" if a.region else " (the part's own bbox)"))
    fr = frames_for(im, a.mode, a.frames, a.amplitude, a.axis, centre, a.secondary,
                    region, a.turns, a.window)

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

    if a.shadow_out:
        # shadow() returns its own canvas and shift, because a cast shadow leans
        # out past the colour plate. Every frame gets the same canvas and the
        # same shift -- they must, or the shadow would swim under the part.
        project = _shadow_fn()
        shadows = [project(f) for f in fr]
        sw, sh_h = shadows[0][0].size
        dx, dy = shadows[0][1], shadows[0][2]
        sheet_s = Image.new("RGBA", (cols * sw, rows * sh_h), (0, 0, 0, 0))
        for i, (plate_i, _, _) in enumerate(shadows):
            sheet_s.paste(plate_i, ((i % a.line_length) * sw,
                                    (i // a.line_length) * sh_h))
        sheet_s.save(a.shadow_out)
        print(f"  ok  {a.shadow_out}  {sheet_s.width}×{sheet_s.height}  "
              f"{sw}×{sh_h} each, draw_as_shadow")
        print(f"      shift it by {dx/2/32:+.5f}, {dy/2/32:+.5f} tiles at "
              f"scale 0.5 relative to the colour sheet")

    moved = [ImageStat.Stat(ImageChops.difference(
        f.convert("RGB"), fr[0].convert("RGB"))).mean[0] for f in fr]
    print(f"  ok  {a.out}  {sheet.width}×{sheet.height}  "
          f"{a.frames} frames, {w}×{h} each, line_length {a.line_length}")
    print(f"      per-frame change against frame 0: "
          f"{min(moved):.1f} .. {max(moved):.1f}")


if __name__ == "__main__":
    main()
