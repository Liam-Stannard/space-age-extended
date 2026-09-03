#!/usr/bin/env python3
"""Build the Quench Turbine's sprites and icon from vanilla's steam turbine.

Why not just set `tint` on the sprite layer: a tint multiplies, and vanilla's
steam turbine is *already* brass and rust -- its saturated pixels sit at hue
15-45 degrees, only ~16% of the opaque area, the rest being neutral grey
metal. Multiplying a warm tint over warm accents changes almost nothing and
darkens the greys, which is exactly the muddy result the entity comment warned
about.

So this recolours properly instead. Every pixel is taken into HLS; the warm
*accent* pixels are rotated to a cryogenic teal and left at their original
lightness, while neutral metal is passed through untouched. Keeping lightness
fixed is the point -- all of vanilla's shading, ambient occlusion and specular
detail survives, and only the hue reads differently.

Teal rather than the mod's magma orange on purpose: the turbine's job is the
*cold* half of the mechanic (Ice, and Fluoroketone at -150C), and orange would
have been indistinguishable from the vanilla sprite it starts from.

Usage: tools/recolour-turbine.py [path-to-factorio-data-dir]
Writes graphics/entity/quench-turbine/*.png and graphics/icons/quench-turbine.png.
"""

import colorsys
import os
import sys

from PIL import Image

# Accent selection. Vanilla's warm accents live in this hue band; anything
# outside it, or too desaturated/too dark/too bright, is left alone so the
# machine still reads as painted metal rather than a solid colour blob.
ACCENT_HUE_LO, ACCENT_HUE_HI = 0.0, 0.18   # ~0-65 degrees: brass, rust, orange
MIN_SATURATION = 0.12
MIN_LIGHTNESS, MAX_LIGHTNESS = 0.06, 0.96

TARGET_HUE = 0.505          # ~182 degrees, cryogenic teal
SATURATION_GAIN = 1.25      # accents read a little stronger than vanilla's
MAX_SATURATION = 0.85

# Neutral metal is nudged a touch cool so the whole body reads as one machine
# rather than a vanilla turbine wearing teal stickers. Deliberately tiny.
METAL_COOL = 0.04

MIP_SIZES = (64, 32, 16, 8)

SPRITES = [
    "steam-turbine-V.png",
    "steam-turbine-H.png",
]


def recolour_pixel(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    is_accent = (
        s >= MIN_SATURATION
        and MIN_LIGHTNESS < l < MAX_LIGHTNESS
        and (h <= ACCENT_HUE_HI or h >= 1.0 - 0.02)
        and h >= ACCENT_HUE_LO - 0.02
    )
    if is_accent:
        h = TARGET_HUE
        s = min(MAX_SATURATION, s * SATURATION_GAIN)
    elif s < MIN_SATURATION:
        # Neutral metal: give it a whisper of the same hue, no lightness change.
        h = TARGET_HUE
        s = min(METAL_COOL, METAL_COOL * (0.4 + l))
    else:
        return r, g, b
    nr, ng, nb = colorsys.hls_to_rgb(h, l, s)
    return int(nr * 255 + 0.5), int(ng * 255 + 0.5), int(nb * 255 + 0.5)


def recolour_image(im):
    """Recolour via a cached lookup over distinct colours -- these sheets are
    ~600k pixels each but only a few thousand distinct RGB values, so a cache
    turns minutes of colorsys calls into seconds."""
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
    result = Image.new("RGBA", im.size)
    result.putdata(out)
    return result, len(cache)


def mip_strip(icon64):
    strip = Image.new("RGBA", (sum(MIP_SIZES), MIP_SIZES[0]), (0, 0, 0, 0))
    x = 0
    for size in MIP_SIZES:
        strip.paste(icon64.resize((size, size), Image.LANCZOS), (x, 0))
        x += size
    return strip


def main(argv):
    data_dir = argv[1] if len(argv) > 1 else os.path.expanduser(
        "~/.steam/debian-installation/steamapps/common/Factorio/data")
    src_dir = os.path.join(data_dir, "base/graphics/entity/steam-turbine")
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(repo, "graphics/entity/quench-turbine")
    os.makedirs(out_dir, exist_ok=True)

    for name in SPRITES:
        src = os.path.join(src_dir, name)
        im = Image.open(src)
        recoloured, distinct = recolour_image(im)
        dst_name = name.replace("steam-turbine", "quench-turbine")
        recoloured.save(os.path.join(out_dir, dst_name))
        print("%-28s %s  (%d distinct colours)" % (dst_name, recoloured.size, distinct))

    # Shadows are pure alpha silhouettes -- copy them rather than recolouring,
    # so the entity can reference one directory instead of straddling two mods.
    for name in ["steam-turbine-V-shadow.png", "steam-turbine-H-shadow.png"]:
        im = Image.open(os.path.join(src_dir, name)).convert("RGBA")
        im.save(os.path.join(out_dir, name.replace("steam-turbine", "quench-turbine")))
        print("%-28s %s  (shadow, copied)" % (name.replace("steam-turbine", "quench-turbine"), im.size))

    # Item icon, from vanilla's own steam-turbine icon, same treatment.
    icon_src = os.path.join(data_dir, "base/graphics/icons/steam-turbine.png")
    icon = Image.open(icon_src).convert("RGBA")
    if icon.width > 64:
        icon = icon.crop((0, 0, 64, 64))
    elif icon.size != (64, 64):
        icon = icon.resize((64, 64), Image.LANCZOS)
    recoloured, _ = recolour_image(icon)
    mip_strip(recoloured).save(os.path.join(repo, "graphics/icons/quench-turbine.png"))
    print("%-28s (120, 64) mipmap strip" % "quench-turbine.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
