#!/usr/bin/env python3
"""Derive an additive glow plate from a lit render and its unlit twin.

Factorio wants glow as its own additive, draw_as_glow sheet: only the light,
on transparency, registered exactly over the static picture. Generators cannot
produce that directly -- ask one for "just the light" and it invents geometry
that does not line up. What it can do is light the plate you already approved.

So: generate the lit version of the approved idle plate, then subtract. The
difference *is* the light -- but only if both plates land on the canvas under
the *same* transform. Normalising each one against its own alpha bounding box
does not do that: the lit render blooms past the metal, so its box is bigger,
and the two get different scales and different centring. The first sheets built
that way sat 6px right and 8px high of base.png. So measure the placement once,
off the unlit plate, and apply those same numbers to both.

Usage:
  tools/derive-glow.py --lit concept/v12-charge.png --unlit concept/v11-idle.png \
      --out graphics/entity/arc-mast/charge.png --width 224 --height 365 --top-margin 16
"""

import argparse
import sys

from PIL import Image, ImageChops, ImageFilter


def solid_bbox(im, alpha=20, min_run=8):
    """Bounding box of the content you can actually see.

    Must stay in step with process-building-art.py's copy: the placement this
    measures has to be the one base.png was cut with, or the glow lands
    somewhere the plate is not. See that file for why raw `getbbox()` is not
    good enough.
    """
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    a = im.getchannel("A")
    w, h = a.size
    px = a.load()
    cols = [x for x in range(w)
            if sum(1 for y in range(h) if px[x, y] > alpha) >= min_run]
    rows = [y for y in range(h)
            if sum(1 for x in range(w) if px[x, y] > alpha) >= min_run]
    if not cols or not rows:
        return None
    return (cols[0], rows[0], cols[-1] + 1, rows[-1] + 1)


def placement(im, width, height, top_margin, bottom_margin=0):
    """Work out the trim/scale/offset to use, as numbers rather than a picture.

    Same arithmetic process-building-art.py's place() does, so the plate this
    is measured off still lands exactly where base.png did -- but returned
    instead of applied, so the lit plate can be given the identical transform.
    """
    box = solid_bbox(im)
    if not box:
        sys.exit("fully transparent input")
    tw, th = box[2] - box[0], box[3] - box[1]
    target_h = height - top_margin - bottom_margin
    scale = target_h / th
    if tw * scale > width:
        scale = width / tw
    new_w, new_h = max(1, round(tw * scale)), max(1, round(th * scale))
    return box, scale, ((width - new_w) // 2, top_margin)


def place_by(im, box, scale, origin, width, height):
    """Put `im` on the canvas under a placement measured off another plate.

    The whole source is scaled, not just the crop, so light that blooms past
    the unlit silhouette survives instead of being clipped at the box edge.
    """
    im = im.convert("RGBA")
    full = im.resize((max(1, round(im.width * scale)),
                      max(1, round(im.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    canvas.paste(full, (origin[0] - round(box[0] * scale),
                        origin[1] - round(box[1] * scale)), full)
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lit", required=True)
    ap.add_argument("--unlit", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--width", type=int, default=224)
    ap.add_argument("--height", type=int, default=365)
    ap.add_argument("--top-margin", type=int, default=16)
    # These two must mirror process-building-art.py exactly. The placement here
    # has to be the one base.png was actually cut with, and a plate cut with a
    # bottom margin or a vertical stretch and a glow derived without them land
    # in different places -- which is the registration bug the module docstring
    # is about, in a new disguise.
    ap.add_argument("--bottom-margin", type=int, default=0)
    ap.add_argument("--stretch-y", type=float, default=1.0)
    ap.add_argument("--gain", type=float, default=1.0,
                    help="multiply the recovered light before clamping")
    ap.add_argument("--floor", type=int, default=18,
                    help="difference below this is treated as noise")
    args = ap.parse_args()

    lit_src = Image.open(args.lit).convert("RGBA")
    unlit_src = Image.open(args.unlit).convert("RGBA")
    if args.stretch_y != 1.0:
        h = max(1, round(lit_src.height * args.stretch_y))
        lit_src = lit_src.resize((lit_src.width, h), Image.LANCZOS)
        unlit_src = unlit_src.resize((unlit_src.width, h), Image.LANCZOS)
    if lit_src.size != unlit_src.size:
        sys.exit(f"lit is {lit_src.size} and unlit is {unlit_src.size}; a shared "
                 "placement is only meaningful if both renders share a canvas")

    # Measured off the unlit plate, applied to both. See the module docstring.
    box, scale, origin = placement(unlit_src, args.width, args.height,
                                   args.top_margin, args.bottom_margin)
    lit = place_by(lit_src, box, scale, origin, args.width, args.height)
    unlit = place_by(unlit_src, box, scale, origin, args.width, args.height)

    diff = ImageChops.subtract(lit.convert("RGB"), unlit.convert("RGB"))
    # Kill the low-level difference that is just resampling noise and the two
    # renders disagreeing about grain, then use brightness as the alpha.
    diff = diff.point(lambda p: 0 if p < args.floor else min(255, int(p * args.gain)))
    alpha = diff.convert("L").filter(ImageFilter.GaussianBlur(0.6))
    alpha = alpha.point(lambda p: 0 if p < 8 else p)

    # Light only where the building is. The lit render's corona spills past the
    # silhouette, and the generator clips it flat against its own canvas edge --
    # kept, that reads in game as a bright cap floating over the electrode.
    # Confine the glow to the unlit plate's alpha, dilated a couple of px and
    # softened so the rim still falls off rather than ending on a hard line.
    keep = unlit.getchannel("A").filter(ImageFilter.MaxFilter(5))
    keep = keep.filter(ImageFilter.GaussianBlur(1.5))
    alpha = ImageChops.multiply(alpha, keep)

    glow = diff.convert("RGBA")
    glow.putalpha(alpha)
    glow.save(args.out)

    hist = alpha.histogram()
    total = alpha.width * alpha.height
    lum = sum(i * n for i, n in enumerate(hist)) / total
    covered = sum(hist[9:]) / total
    print(f"  ok  {args.out}  {args.width}×{args.height}")
    print(f"      mean light {lum:.1f}/255 · covers {covered:.1%} of the canvas")


if __name__ == "__main__":
    main()
