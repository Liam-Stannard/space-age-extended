#!/usr/bin/env python3
"""Cut one component out of an approved plate, using a generated colour mask.

**Why this exists.** Asking a generator for a component on its own -- "draw the
flywheel, nothing else, at the position it occupies" -- returns the right
component in the wrong place. Measured on the Dross Classifier's drive: the part
came back correct in every particular and centred on its own canvas at x
0.28-0.76, y 0.20-0.58, where on the plate it sits up at the top of the
roofline. Nothing in the returned file says where it goes. That is the general
result from the first test run of graphics/animation-layer-prompts.md -- the
generator is good at *what* to draw and unreliable at *where* to put it.

So it is asked for the *what* only. The prompt returns the whole machine,
unmoved, with one component flooded in flat magenta, and that magenta region is
used as a **stencil** over the original plate. Every pixel this writes comes
from `base.png`. Nothing is redrawn, which is the same rule
`cut-plate-from-sheet.py` was written for and for the same reason.

**The registration is the work.** The returned image is still a regeneration:
it arrives at a different canvas size and, measured on the Arc Mast, with the
machine re-proportioned by about 4.7% in trimmed aspect. A stencil that is 5%
wrong is a part with a 5% wrong edge. So the mask is not used where it lands --
it is fitted to the plate first, by searching for the scale and offset that make
the *silhouettes* agree, and only then applied.

Usage:
  tools/cut-part-by-mask.py --plate graphics/entity/dross-classifier/base.png \\
      --mask concept/v2-drive-mask.png \\
      --out graphics/entity/dross-classifier/drive.png
"""

import argparse
import sys

from PIL import Image, ImageChops, ImageStat


def silhouette(im, thresh=24):
    """Binary alpha silhouette, 0 or 255."""
    return im.getchannel("A").point(lambda v: 255 if v > thresh else 0)


def key_mask(im, key=(255, 0, 255), tol=90):
    """The flooded region, as a binary mask.

    Generous tolerance on purpose. The generator will not return #FF00FF flat
    however plainly it is asked -- it shades, it anti-aliases the rim, and it
    darkens the edge. What is stable is *hue*: magenta is the one hue that
    appears nowhere on any building in this mod, which is why section 11 of the
    template picked it as the key colour in the first place. So the test is
    "much more red and blue than green", not "equal to the key".
    """
    r, g, b = im.convert("RGB").split()
    # red and blue both well above green
    rb = ImageChops.darker(r, b)                       # min(r, b)
    lift = ImageChops.subtract(rb, g, scale=1, offset=0)
    return lift.point(lambda v: 255 if v > tol else 0)


def count(mask):
    return ImageStat.Stat(mask).mean[0] * mask.size[0] * mask.size[1] / 255.0


def iou(a, b):
    inter = count(ImageChops.multiply(a, b))
    union = count(ImageChops.lighter(a, b))
    return inter / union if union else 0.0


def place(im, size, scale, dx, dy, resample=Image.LANCZOS):
    """Scale `im` about its own top-left and paste it into a `size` canvas."""
    w = max(1, int(round(im.width * scale)))
    h = max(1, int(round(im.height * scale)))
    out = Image.new(im.mode, size, 0 if im.mode == "L" else (0, 0, 0, 0))
    out.paste(im.resize((w, h), resample), (int(round(dx)), int(round(dy))))
    return out


def fit(mask_sil, plate_sil, verbose=True):
    """Find scale and offset that make the two silhouettes agree.

    Coarse then fine, around the bounding-box fit. The bbox fit alone is not
    enough: it is driven by the extremes of the silhouette, and a generator that
    has added a pixel of bloom to one corner moves it.
    """
    mb = mask_sil.getbbox()
    pb = plate_sil.getbbox()
    if not mb or not pb:
        sys.exit("one of the images has no content")
    crop = mask_sil.crop(mb)
    base_scale = ((pb[2] - pb[0]) / crop.width + (pb[3] - pb[1]) / crop.height) / 2
    best = (0.0, base_scale, pb[0], pb[1])

    for span, step in ((0.10, 0.02), (0.03, 0.006), (0.01, 0.002)):
        _, s0, x0, y0 = best
        rng = [s0 * (1 + k * step) for k in range(-int(span / step), int(span / step) + 1)]
        off = max(2, int(round(span * 60)))
        for s in rng:
            for dx in range(int(x0) - off, int(x0) + off + 1, max(1, off // 4)):
                for dy in range(int(y0) - off, int(y0) + off + 1, max(1, off // 4)):
                    cand = place(crop, plate_sil.size, s, dx, dy, Image.NEAREST)
                    v = iou(cand, plate_sil)
                    if v > best[0]:
                        best = (v, s, dx, dy)
        if verbose:
            print("    pass span %.2f -> IoU %.4f  scale %.4f  offset %d,%d"
                  % (span, best[0], best[1], best[2], best[3]))
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plate", required=True, help="the approved base.png")
    ap.add_argument("--mask", required=True, help="the generator's flooded render")
    ap.add_argument("--out", required=True, help="the component, on the plate's canvas")
    ap.add_argument("--mask-out", help="also write the fitted stencil, for inspection")
    ap.add_argument("--housing-out",
                    help="also write the plate with the part removed: the static "
                         "layer the moving part is drawn over")
    ap.add_argument("--tol", type=int, default=90)
    ap.add_argument("--min-iou", type=float, default=0.90,
                    help="reject the fit below this; the mask is not this machine")
    a = ap.parse_args()

    plate = Image.open(a.plate).convert("RGBA")
    render = Image.open(a.mask).convert("RGBA")
    print(f"  plate {plate.size}   render {render.size}")

    p_sil = silhouette(plate)
    r_sil = silhouette(render)
    print("  fitting the render's silhouette to the plate's:")
    score, scale, dx, dy = fit(r_sil, p_sil)
    print(f"  best IoU {score:.4f}  (scale {scale:.4f}, offset {dx},{dy})")
    if score < a.min_iou:
        sys.exit(f"  REJECT: silhouettes agree to only {score:.3f}. The generator "
                 f"returned a different shape, not a recolour of this one.")

    # Fit the key region through the same transform the silhouette fitted through.
    key = key_mask(render, tol=a.tol)
    covered = 100 * count(key) / count(r_sil) if count(r_sil) else 0
    print(f"  keyed region is {covered:.1f}% of the machine")
    if covered < 0.2:
        sys.exit("  REJECT: almost nothing was flooded. Check the key colour.")
    if covered > 60:
        sys.exit("  REJECT: most of the machine was flooded, not one component.")

    mb = r_sil.getbbox()
    # BILINEAR, not LANCZOS. Lanczos overshoots at every edge, and on a binary
    # mask the undershoot lands as a haze of values 1..30 scattered right across
    # the canvas -- invisible to look at, and enough to give the cut part a
    # bounding box the size of the whole plate. The floor below removes what is
    # left; the ceiling keeps a one-pixel soft edge, which is wanted.
    stencil = place(key.crop(mb), plate.size, scale, dx, dy, Image.BILINEAR)
    stencil = stencil.point(lambda v: 0 if v < 40 else v)
    # A stencil may not reach past the machine it was cut from.
    stencil = ImageChops.multiply(stencil, p_sil)

    part = plate.copy()
    part.putalpha(ImageChops.multiply(plate.getchannel("A"), stencil))
    part.save(a.out)
    bb = stencil.getbbox()
    print(f"  wrote {a.out}  part occupies {bb} of {plate.size}, "
          f"{100 * count(stencil) / count(p_sil):.1f}% of the machine")
    if a.housing_out:
        # The static layer: everything the part is not. Needed because a part
        # that moves must not leave a second, stationary copy of itself showing
        # through from underneath.
        housing = plate.copy()
        housing.putalpha(ImageChops.multiply(
            plate.getchannel("A"), stencil.point(lambda v: 255 - v)))
        housing.save(a.housing_out)
        print(f"  wrote {a.housing_out}  (the plate with the part removed)")
    if a.mask_out:
        stencil.save(a.mask_out)
        print(f"  wrote {a.mask_out}")


main()
