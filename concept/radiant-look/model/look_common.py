"""Shared by the study and the candidate sheets: downsampling, day/night compositing, the
measures, and drawing labelled panels.

Day and night are composed as the engine draws them (emulated here, not checked in a client):
  day    the plate (and its animation frame) over the ground, the glow layer added on top
  night  the same, the lit scene multiplied by NIGHT (Factorio's darkness, roughly: the
         surface's minimum brightness, blue-graded), the glow layer added after, unaffected
         (draw_as_glow)
"""
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

GROUND = (74, 66, 58)               # tools/blender/preview.py's ground
NIGHT = (0.17, 0.19, 0.27)
BG = (30, 30, 30)
TXT = (230, 222, 205)
HEAD = (240, 200, 120)


def font(size):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def bold(size):
    f = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    return ImageFont.truetype(f, size) if os.path.exists(f) else font(size)


def down(path, k=4):
    """4x render -> sprite size, premultiplied (as tools/blender/downsample.py)."""
    im = Image.open(path).convert("RGBa")
    return im.resize((im.width // k, im.height // k), Image.LANCZOS).convert("RGBA")


def on_ground(plate, ground=GROUND):
    g = Image.new("RGBA", plate.size, ground + (255,))
    return Image.alpha_composite(g, plate).convert("RGB")


def light_of(glow):
    """A glow render (emission on transparent black) as additive light: RGB times alpha."""
    g = glow.convert("RGBA")
    r, gg, b, a = g.split()
    return Image.merge("RGB", [ImageChops.multiply(c, a) for c in (r, gg, b)])


def darken(im, k=NIGHT):
    r, g, b = im.split()
    return Image.merge("RGB", (r.point(lambda v: int(v * k[0])), g.point(lambda v: int(v * k[1])),
                               b.point(lambda v: int(v * k[2]))))


def day(plate, light, ground=GROUND):
    return ImageChops.add(on_ground(plate, ground), light)


def night(plate, light, ground=GROUND):
    return ImageChops.add(darken(on_ground(plate, ground)), light)


def bloom(light, radius, gain):
    """A soft halo added to a glow layer: the layer blurred, scaled, added back."""
    if not gain:
        return light
    b = light.filter(ImageFilter.GaussianBlur(radius))
    b = b.point(lambda v: min(255, int(v * gain)))
    return ImageChops.add(light, b)


def blue_mask(im):
    """255 where a pixel is the isotope's blue: B > 110, B > R + 45, B > G + 10 (the generator
    round 6 sheets' measure, r6_sheets.py)."""
    r, g, b = im.convert("RGB").split()
    m1 = b.point(lambda v: 255 if v > 110 else 0)
    m2 = ImageChops.subtract(b, r).point(lambda v: 255 if v > 45 else 0)
    m3 = ImageChops.subtract(b, g).point(lambda v: 255 if v > 10 else 0)
    return ImageChops.multiply(ImageChops.multiply(m1, m2), m3)


def blue_share(im, alpha=None):
    """Blue pixels as a share of the opaque pixels (all pixels if no alpha)."""
    m = blue_mask(im)
    if alpha is not None:
        a = alpha.point(lambda v: 255 if v > 128 else 0)
        n = a.histogram()[255]
        m = ImageChops.multiply(m, a)
    else:
        n = im.width * im.height
    return 100.0 * m.histogram()[255] / max(1, n)


def lum(p):
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


def sat(p):
    mx, mn = max(p), min(p)
    return 0.0 if mx == 0 else (mx - mn) / mx


def light_measures(light, plate_rgb=None, thresh=12):
    """How a glow layer builds its light, on its lit pixels (any channel > thresh):
      area     lit pixels
      peak     the brightest pixel's luminance
      core%    share of lit pixels at >= 60 % of the peak: how much is hot core
      halo%    share at <= 25 % of the peak: how much is soft falloff and spill
      sat_core mean saturation of the core pixels; sat_halo of the halo pixels
      white    pixels with every channel >= 245 (clipped)
    """
    px = [p for p in light.convert("RGB").get_flattened_data() if max(p) > thresh]
    if not px:
        return dict(area=0, peak=0, core=0, halo=0, sat_core=0, sat_halo=0, white=0)
    L = [lum(p) for p in px]
    pk = max(L)
    core = [p for p, l in zip(px, L) if l >= 0.6 * pk]
    halo = [p for p, l in zip(px, L) if l <= 0.25 * pk]
    return dict(area=len(px), peak=round(pk), core=round(100 * len(core) / len(px), 1),
                halo=round(100 * len(halo) / len(px), 1),
                sat_core=round(sum(sat(p) for p in core) / max(1, len(core)), 2),
                sat_halo=round(sum(sat(p) for p in halo) / max(1, len(halo)), 2),
                white=sum(1 for p in px if min(p) >= 245))


def up(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


class Sheet:
    """Rows of labelled panels, stacked: a minimal layout for review sheets."""

    def __init__(self, title, sub=(), width=None):
        self.rows = []
        self.title, self.sub = title, list(sub)
        self.width = width

    def section(self, text, sub=()):
        self.rows.append(("section", text, list(sub)))

    def row(self, panels, gap=14):
        """panels: [(image, caption-lines)]"""
        self.rows.append(("row", panels, gap))

    def render(self, path):
        f, fb, fh = font(13), bold(15), bold(22)
        pad = 18
        blocks = []
        W = self.width or 0
        def pw(im, cap):
            return max([im.width] + [int(f.getlength(c)) + 6 for c in cap])
        for kind, a, b in self.rows:
            if kind == "row":
                w = sum(pw(im, cap) for im, cap in a) + b * (len(a) - 1)
                h = max(im.height + 18 * len(cap) for im, cap in a)
                blocks.append((kind, a, b, w, h + 16))
                W = max(W, w)
            else:
                blocks.append((kind, a, b, 0, 30 + 17 * len(b)))
        W += 2 * pad
        H = pad + 34 + 18 * len(self.sub) + 10 + sum(bl[4] for bl in blocks) + pad
        out = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(out)
        y = pad
        d.text((pad, y), self.title, font=fh, fill=HEAD)
        y += 34
        for s in self.sub:
            d.text((pad, y), s, font=f, fill=TXT)
            y += 18
        y += 10
        for kind, a, b, w, h in blocks:
            if kind == "section":
                d.text((pad, y + 6), a, font=fb, fill=HEAD)
                yy = y + 28
                for s in b:
                    d.text((pad, yy), s, font=f, fill=TXT)
                    yy += 17
            else:
                x = pad
                for im, cap in a:
                    yy = y
                    for c in cap:
                        d.text((x, yy), c, font=f, fill=TXT)
                        yy += 18
                    out.paste(im, (x, yy))
                    x += pw(im, cap) + b
            y += h
        out.save(path, optimize=True)
        return out
