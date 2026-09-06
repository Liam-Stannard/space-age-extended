#!/usr/bin/env python3
"""Recolour vanilla's agricultural tower crane into the Bed Tender's arm.

Why recolour rather than draw. The crane is not a picture, it is a **turntable**:
nine parts, each a rotational spritesheet of 64 to 128 frames so the arm can
swing to any angle, plus a shadow and a reflection sheet for each -- 29 files and
37.7 megapixels in total. Those frames were rendered from a 3D model, and the
only way to author a replacement is to build one and render it the same way. An
image generator cannot produce 64 consistent angles of anything; asking it to
would give 64 different arms.

So the geometry stays vanilla's and the material becomes ours, which is exactly
the argument tools/recolour-turbine.py makes for the quench turbine. After this
the arm reads as the Bed Tender's arm rather than as a Gleba import, which was
the actual complaint -- it still *moves* like vanilla's, and it always will until
somebody models one.

What changes. Vanilla's crane is Gleba olive and brass: measured over the opaque
pixels of four different parts, its saturated colour runs hue 20-70 degrees --
brass and tan on the arm segments, distinctly olive-green on the hub and joints.
Those become the Bed Tender's palette from section 3.3 of its spec -- an
iron-nickel grey-brown body between #4A463F and #6E685C, with the strongest,
brightest accents held back as the dull ochre #7A6A41 banding the design already
asks for on the arm edges and gripper.

Lightness is compressed rather than left alone, and only above a shoulder. Taking
the chroma out of a bright olive leaves a pale grey: measured, the hub came back
at luminance 129 against section 3.3's ceiling of 105, and read washed out beside
the hub plate. The shoulder pulls the top of the range down and leaves everything
below it exactly as vanilla drew it, so shading, ambient occlusion and specular
detail all survive and the body lands in the band. Verify by measuring, not by
looking -- `body metal` in process-building-art.py --report is the same statistic.

Shadows and masks are copied through untouched: a shadow is alpha, not colour,
and recolouring one would tint the ground.

**SUPERSEDED for the seven rotated parts.** `build-crane-sheets.py` now writes
bespoke art into `crane-1-1`, `crane-1-2`, `crane-3`, `crane-4`, `crane-5-1`,
`crane-5-2`, `crane-6`, `crane-7-1`, `crane-7-2` and `crane-8`. Re-running this
tool would overwrite all ten with recoloured vanilla again. What it is still the
only source of is the rest of the set -- the shadows, the reflections, and the
two small fittings `crane-9` and `crane-10` -- so run it *first* and then
`build-crane-sheets.py`, never the other way round.

Usage: tools/recolour-crane.py [path-to-factorio-data-dir]
Writes graphics/entity/bed-tender/crane/*.png.
"""

import colorsys
import os
import sys

from PIL import Image

# Vanilla's crane accents, measured across four parts rather than one: the
# saturated pixels run 20-70 degrees, brass and tan on the arm segments but
# distinctly olive-green on the hub and joints. A first pass windowed 11-54
# degrees off the arm alone and left the hub almost untouched, still green --
# survey every part before setting this, not the one that happens to be open.
ACCENT_HUE_LO, ACCENT_HUE_HI = 0.030, 0.250      # ~11-90 degrees
MIN_SATURATION = 0.10
MIN_LIGHTNESS, MAX_LIGHTNESS = 0.05, 0.97

BODY_HUE = 0.098          # ~35 deg, but held to a low saturation: grey-brown
BODY_SATURATION = 0.13    # #4A463F..#6E685C are barely chromatic
OCHRE_HUE = 0.117         # ~42 deg, the #7A6A41 banding
OCHRE_SATURATION = 0.31

# Only the brightest, most saturated accents survive as banding; the rest of the
# olive becomes body metal. Chosen so the arm reads as grey-brown with ochre
# markings rather than as a uniformly ochre arm.
BAND_MIN_SATURATION = 0.34
BAND_MIN_LIGHTNESS = 0.34

METAL_WARM = 0.05         # a whisper of the body hue through the neutral greys

# Lightness shoulder, applied to recoloured pixels only. Below SHOULDER nothing
# moves; above it the range is squeezed by SHOULDER_GAIN, which brings the pale
# ex-olive down into #4A463F..#6E685C without touching the darks that carry the
# shading.
SHOULDER = 0.22
SHOULDER_GAIN = 0.70


def recolour_pixel(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    if s >= MIN_SATURATION and MIN_LIGHTNESS < l < MAX_LIGHTNESS \
            and ACCENT_HUE_LO <= h <= ACCENT_HUE_HI:
        if s >= BAND_MIN_SATURATION and l >= BAND_MIN_LIGHTNESS:
            h, s = OCHRE_HUE, min(OCHRE_SATURATION, s * 0.85)
        else:
            h, s = BODY_HUE, min(BODY_SATURATION, s * 0.55)
        if l > SHOULDER:
            l = SHOULDER + (l - SHOULDER) * SHOULDER_GAIN
    elif s < MIN_SATURATION:
        h, s = BODY_HUE, min(METAL_WARM, METAL_WARM * (0.4 + l))
        if l > SHOULDER:
            l = SHOULDER + (l - SHOULDER) * SHOULDER_GAIN
    else:
        return r, g, b
    nr, ng, nb = colorsys.hls_to_rgb(h, l, s)
    return int(nr * 255 + 0.5), int(ng * 255 + 0.5), int(nb * 255 + 0.5)


def recolour_image(im):
    """Recolour through a cache over distinct colours.

    These sheets run to several megapixels each but carry only a few thousand
    distinct RGB values, so caching turns minutes of colorsys into seconds --
    the same trick recolour-turbine.py uses, and it matters far more here.
    """
    im = im.convert("RGBA")
    cache = {}
    out = []
    for r, g, b, a in im.getdata():
        if a == 0:
            out.append((0, 0, 0, 0))
            continue
        key = (r, g, b)
        hit = cache.get(key)
        if hit is None:
            hit = recolour_pixel(r, g, b)
            cache[key] = hit
        out.append(hit + (a,))
    res = Image.new("RGBA", im.size)
    res.putdata(out)
    return res, len(cache)


def main(argv):
    data = argv[1] if len(argv) > 1 else os.path.expanduser(
        "~/.steam/debian-installation/steamapps/common/Factorio/data")
    src = os.path.join(data, "space-age/graphics/entity/agricultural-tower")
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(repo, "graphics/entity/bed-tender/crane")
    os.makedirs(out, exist_ok=True)

    names = sorted(f for f in os.listdir(src)
                   if f.startswith("agricultural-tower-crane") and f.endswith(".png"))
    if not names:
        sys.exit(f"no crane sheets under {src}")

    for name in names:
        dst = name.replace("agricultural-tower-crane", "crane")
        im = Image.open(os.path.join(src, name))
        # A shadow is alpha, not colour. Tinting one would put brown on the
        # ground; a reflection is only ever seen through water, and there is no
        # water on the Core -- both are copied so the sheets stay a matched set.
        if "-shadow" in name or "-reflection" in name:
            im.save(os.path.join(out, dst))
            print(f"  ok  {dst:<28} {str(im.size):<14} copied")
            continue
        new, n = recolour_image(im)
        new.save(os.path.join(out, dst))
        print(f"  ok  {dst:<28} {str(new.size):<14} {n} distinct colours")


if __name__ == "__main__":
    main(sys.argv)
