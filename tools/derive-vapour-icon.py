#!/usr/bin/env python3
"""Build the Quench Vapour fluid icon by gradient-mapping an existing drop.

Technique, and why it differs from tools/recolour-turbine.py: that script
rotates hue, which only works on pixels that already have some. Here the job
is to give a drop a colour it does not have, so each pixel's *luminance* picks
a colour off a warm ramp instead. The source's shading, gloss and highlight
all survive; only the colour is new.

The source is one of the mod's own rendered fluid drops rather than vanilla's
steam icon, which was the first attempt and was wrong twice over. Vanilla's
steam icon is a lumpy cloud of small nodules -- mapped to warm colours it
reads as popcorn, not as vapour -- and at 46% frame coverage it was visibly
chunkier than this mod's other fluid icons, which sit at 31-35%. Borrowing a
sibling drop instead means the icon is the same shape language, gloss and
weight as the five it sits beside in the fluid list.

Cyan-teal, matching the Quench Turbine. Warm amber was the first choice and
was measurably wrong: the set's hues are molten scrap 20, molten non-ferrous
0-20, contaminated acid 40, holmium residue 260, molten ferrous 200. An amber
vapour landed at hue 0-20, i.e. a second saturated orange drop sitting beside
the first, and a pale-gold version landed on the acid. Cyan-teal is the one
free slot in the set, it stays legible at 16px, and it ties the fluid to the
machine that consumes it -- the same relationship vanilla draws between green
fuel cells and a green reactor. It is also honest about the mechanic: this
vapour is what comes off a Magmatic Core quenched with Ice.

The fluid prototype's base_color/flow_color were changed to match, so pipes
and the fluid list agree with the icon.

This is a stopgap: a real render for Quench Vapour would replace it, and the
prompt for one belongs in graphics/icon-prompts.md.

Usage: tools/derive-vapour-icon.py
Writes graphics/icons/fluid/quench-vapour.png (120x64 four-level mip strip).
"""

import os
import sys

from PIL import Image

MIP_SIZES = (64, 32, 16, 8)

# Luminance source: molten non-ferrous metal. Picked for tone, not subject --
# it is the widest, most evenly distributed tonal range in the set (5th/50th/
# 95th percentile luminance 80/110/191), which is what a gradient map needs to
# resolve into distinct colours. Its own purple is irrelevant; only luminance
# is read. Its silhouette is already at the set's coverage, so no rescale.
SOURCE_ICON = "graphics/icons/fluid/molten-non-ferrous-metal.png"

# Luminance -> colour ramp: deep teal shadow, cyan midtones, near-white core
# so the drop reads as luminous vapour rather than a liquid. Anchors are
# (luminance, (r, g, b)) and are linearly interpolated.
RAMP = [
    (0.00, (4, 26, 30)),
    (0.18, (8, 64, 74)),
    (0.38, (14, 116, 130)),
    (0.56, (38, 170, 182)),
    (0.72, (96, 212, 218)),
    (0.86, (172, 238, 240)),
    (1.00, (240, 254, 255)),
]

# The source drop uses only the middle of the luminance range (p5 0.31, p95
# 0.75), so mapping it straight would use only the middle of the ramp and come
# out flat. Stretching those percentiles to the ramp's full span puts real
# ember in the shadows and a genuinely bright core in the highlight. The gamma
# lifts the midtones slightly so the body reads as glowing rather than dark.
LEVELS_LO, LEVELS_HI = 0.31, 0.75
CONTRAST_GAMMA = 0.85


def ramp_colour(t):
    t = max(0.0, min(1.0, t))
    for i in range(len(RAMP) - 1):
        t0, c0 = RAMP[i]
        t1, c1 = RAMP[i + 1]
        if t0 <= t <= t1:
            f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return tuple(int(c0[j] + (c1[j] - c0[j]) * f + 0.5) for j in range(3))
    return RAMP[-1][1]


def gradient_map(im):
    """Map each pixel's luminance through the ramp, preserving alpha."""
    im = im.convert("RGBA")
    lut = [ramp_colour(i / 255.0) for i in range(256)]
    out = []
    for r, g, b, a in im.getdata():
        if a == 0:
            out.append((0, 0, 0, 0))
            continue
        lum = (r * 299 + g * 587 + b * 114) / 255000.0
        lum = (lum - LEVELS_LO) / (LEVELS_HI - LEVELS_LO)
        lum = max(0.0, min(1.0, lum)) ** CONTRAST_GAMMA
        out.append(lut[int(lum * 255 + 0.5)] + (a,))
    result = Image.new("RGBA", im.size)
    result.putdata(out)
    return result


def coverage(icon):
    alpha = icon.getchannel("A")
    return sum(1 for p in alpha.get_flattened_data() if p > 12) / float(icon.width * icon.height)


def mip_strip(icon64):
    strip = Image.new("RGBA", (sum(MIP_SIZES), MIP_SIZES[0]), (0, 0, 0, 0))
    x = 0
    for size in MIP_SIZES:
        strip.paste(icon64.resize((size, size), Image.LANCZOS), (x, 0))
        x += size
    return strip


def main(argv):
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = Image.open(os.path.join(repo, SOURCE_ICON)).convert("RGBA")
    icon = src.crop((0, 0, 64, 64)) if src.width > 64 else src.resize((64, 64), Image.LANCZOS)

    before = coverage(icon)
    icon = gradient_map(icon)
    after = coverage(icon)

    out = os.path.join(repo, "graphics/icons/fluid/quench-vapour.png")
    mip_strip(icon).save(out)
    print("quench-vapour.png  from %s  coverage %.0f%% -> %.0f%%"
          % (os.path.basename(SOURCE_ICON), before * 100, after * 100))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
