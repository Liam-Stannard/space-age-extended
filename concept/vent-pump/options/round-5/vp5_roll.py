"""Vent Pump, round 5 (T05): vp5_shoulder.py's highlight roll-off as a function, for an image at the scale
it is delivered at (vp5_sheet.py's and vp5_pack.py's 2x and 1x downsamples).

The 4x renders are rolled off once by vp5_shoulder.py; the premultiplied LANCZOS downsample to 2x and 1x
overshoots at a bright edge and lands some px back on 255, so the same curve is applied again after
the downsample: a px whose brightest channel m passes KNEE is scaled whole (hue and saturation kept) so
that channel lands at KNEE + (TOP - KNEE) * (1 - exp(-(m - KNEE) / (TOP - KNEE))), under TOP. Below the
knee nothing changes. The curve is idempotent in effect (a rolled px is under TOP, a second pass moves it
by under a level).
"""
import math

from PIL import Image, ImageChops

KNEE, TOP = 236, 250


def _f(m):
    return m if m <= KNEE else KNEE + (TOP - KNEE) * (1 - math.exp(-(m - KNEE) / (TOP - KNEE)))


LUT = [255 if m <= KNEE else round(255 * _f(m) / m) for m in range(256)]


def roll(im):
    """An RGBA image with its highlights rolled off (straight alpha kept)."""
    r, g, b, a = im.convert("RGBA").split()
    k = ImageChops.lighter(ImageChops.lighter(r, g), b).point(LUT)
    return Image.merge("RGBA", [ImageChops.multiply(c, k) for c in (r, g, b)] + [a])
