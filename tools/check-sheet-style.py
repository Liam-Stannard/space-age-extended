#!/usr/bin/env python3
"""Measure a concept against vanilla's camera and finish, instead of eyeballing it.

Appendix B of `templates/building-spec-template.md` is blunt about why this exists: judging
a plate by looking at it produced "two confident and completely wrong findings"
over five rounds on one building. A viewer composites a transparent PNG onto its
own background, so the metal's apparent value moves with whatever is behind it.

Three numbers, each chosen because it fails a specific way concepts go wrong:

  * **Drawn aspect** -- height over width for a building on a *square* footprint.
    Factorio's camera is steeply down, so a square building draws slightly wider
    than tall. A concept drawn from a lower camera, showing more of its front
    face, comes out visibly taller. This is the perspective check.
  * **Body luminance and saturation** -- the palette drifts pale and rust-orange
    on every round, and the spec argues it down explicitly. This measures whether
    that worked.
  * **Edge density** -- detail per unit area, at matched scale. A concept far
    below vanilla reads as smooth and toy-like; far above reads as noise.

Vanilla's own four style references set every band, so "matches vanilla" means
"inside the range vanilla itself occupies" rather than a number someone chose.

  tools/check-sheet-style.py REF_DIR [CROP.png ...]
"""

import argparse
import colorsys
import os
import sys

from PIL import Image, ImageFilter

# Footprints of the four standing references, so drawn aspect is comparable.
FOOTPRINT = {
    "assembling-machine-3": (3, 3),
    "electromagnetic-plant": (3, 3),
    "foundry": (5, 5),
    "rocket-silo": (9, 9),
}


def content(img):
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    a = img.getchannel("A")
    if a.getextrema()[0] == 255:            # opaque crop: use the charcoal ground
        g = img.convert("L").point(lambda v: 255 if v > 42 else 0)
        box = g.getbbox()
    else:
        box = a.point(lambda v: 255 if v > 40 else 0).getbbox()
    return img.crop(box) if box else img


def measure(img, label, foot=(1, 1)):
    img = content(img)
    w, h = img.size
    aspect = (h / w) * (foot[0] / foot[1])

    rgb = img.convert("RGB")
    px = list(rgb.getdata())
    if img.mode == "RGBA":
        al = list(img.getchannel("A").getdata())
        px = [p for p, a in zip(px, al) if a > 128]
    # Drop the darkest fifth: those are cast shadow and holes, not body metal.
    px.sort(key=lambda p: p[0] * 0.299 + p[1] * 0.587 + p[2] * 0.114)
    body = px[len(px) // 5:]
    lum = sum(p[0] * 0.299 + p[1] * 0.587 + p[2] * 0.114 for p in body) / len(body)
    sat = sum(colorsys.rgb_to_hsv(*[c / 255 for c in p])[1] for p in body) / len(body)

    g = rgb.convert("L")
    e = g.filter(ImageFilter.FIND_EDGES)
    edges = sum(1 for v in e.getdata() if v > 40) / (w * h)

    return dict(label=label, size="%dx%d" % (w, h), aspect=aspect,
                lum=lum, sat=sat, edges=edges)


def band(rows, key):
    vals = [r[key] for r in rows]
    return min(vals), max(vals)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref_dir")
    ap.add_argument("crops", nargs="*")
    args = ap.parse_args()

    refs = []
    for name, foot in sorted(FOOTPRINT.items()):
        p = os.path.join(args.ref_dir, name + ".png")
        if os.path.exists(p):
            refs.append(measure(Image.open(p), name, foot))
    if not refs:
        raise SystemExit("no vanilla references in " + args.ref_dir)

    print("VANILLA (the band everything is judged against)")
    for r in refs:
        print("  %-24s %-10s aspect %.3f  lum %5.1f  sat %.3f  edges %.3f"
              % (r["label"], r["size"], r["aspect"], r["lum"], r["sat"], r["edges"]))
    bands = {k: band(refs, k) for k in ("aspect", "lum", "sat", "edges")}
    print("  %-24s %-10s aspect %.3f-%.3f  lum %.1f-%.1f  sat %.3f-%.3f  edges %.3f-%.3f"
          % ("BAND", "", *bands["aspect"], *bands["lum"], *bands["sat"], *bands["edges"]))

    if not args.crops:
        return 0
    print("\nCONCEPTS")
    bad = 0
    for c in args.crops:
        m = measure(Image.open(c), os.path.basename(c), (9, 9))
        flags = []
        for k, nice in (("aspect", "perspective"), ("lum", "value"),
                        ("sat", "saturation"), ("edges", "detail")):
            lo, hi = bands[k]
            pad = (hi - lo) * 0.5 + 1e-9        # half a band of tolerance either side
            if not (lo - pad <= m[k] <= hi + pad):
                flags.append("%s %s" % (nice, "high" if m[k] > hi else "low"))
        bad += bool(flags)
        print("  %-24s %-10s aspect %.3f  lum %5.1f  sat %.3f  edges %.3f  %s"
              % (m["label"], m["size"], m["aspect"], m["lum"], m["sat"], m["edges"],
                 ", ".join(flags) if flags else "in band"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())


# ---------------------------------------------------------------------------
# Rule zero: the building is drawn square-on to the tile grid.
#
# Template section "Rule zero", checked against the electric mining drill in all
# four directions. A building drawn corner-on -- rotated 45 degrees so a corner
# points at the viewer -- reads as a diamond and does not sit on Factorio's grid,
# and it is the single easiest camera error to miss by eye because the render
# still looks good in isolation.
#
# The tell is the bottom of the silhouette. Square-on, the near face gives a long
# roughly-horizontal bottom edge. Corner-on, the base comes to a point and the
# bottom is a V. So: what fraction of the silhouette's width sits within a small
# band of its lowest row?
# ---------------------------------------------------------------------------

def base_flatness(img, band_frac=0.06):
    """Band scales with the building's WIDTH, not the panel's height.

    Scaled to height, a tall building in a tall panel gets a band deep enough to
    swallow its whole base and scores a perfect 1.000 while being an obvious
    diamond -- which is exactly what the Driven Column did on the first run.

    **And it is not reliable enough to act on alone.** Run against set 4 it called
    the Driven Column square-on at 1.000 when its base is plainly a diamond, and
    flagged the Storm Crown, whose base is merely round. Corner-on drawing was
    caught by eye, not by this. It is kept as a cheap first pass and a place to
    put the fix when someone works out a metric that holds -- probably one that
    reads the *top-down* panel's outline against the grid rather than guessing
    from the hero's bottom edge.
    """
    img = content(img)
    w, h = img.size
    if img.mode == "RGBA" and img.getchannel("A").getextrema()[0] < 255:
        m = img.getchannel("A").point(lambda v: 255 if v > 40 else 0)
    else:
        m = img.convert("L").point(lambda v: 255 if v > 42 else 0)
    px = m.load()
    bottom = []
    for x in range(w):
        col = [y for y in range(h) if px[x, y]]
        bottom.append(max(col) if col else None)
    ys = [b for b in bottom if b is not None]
    if not ys:
        return 0.0
    lowest = max(ys)
    band = max(2, int(band_frac * w))
    near = sum(1 for b in ys if b >= lowest - band)
    return near / len(ys)
