"""Review sheets for the radiant asteroid's maps, beside promethium's and the radiant chunk icon.

    <python with numpy and Pillow> sheets.py <promethium dir> <maps dir> <chunk icon> <out dir>

writes <out dir>/maps-sheet.png (every map, channel by channel, promethium's above ours),
<out dir>/lit-sheet.png (both lit by the engine's shader, shade.py) and <out dir>/lit-measures.json.

The lit preview is asteroid.frag itself, ported (shade.py), with asteroid.lua's shading data:
promethium's as the rock inherits it today (red rim) and the same with the rim blue (T03's
change, previewed). It approximates: the texture is shaded at its own resolution ("zoom 2",
where one texel is one screen pixel) and, for zoom 1, at mip 1 (each map box-averaged 2x2,
then shaded); the rock is unrotated (the engine turns it, and turns its normals with it, so
the light stays put); no shadow, no space background or parallax, no bloom or post.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shade import PROMETHIUM, RIM_BLUE, over, shade  # noqa: E402

SPACE = (5, 6, 10)
SHEET = (24, 24, 28)
INK = (225, 225, 225)
DIM = (150, 150, 155)
COUNT = {"small": 7, "chunk": 6}


def font(n):
    try:
        return ImageFont.load_default(size=n)
    except TypeError:
        return ImageFont.load_default()


def rgba(p):
    return np.array(Image.open(p).convert("RGBA"))


def maps(d, kind, size, v):
    stem = os.path.join(d, size, f"asteroid-{kind}-{size}-%s-{v:02d}.png")
    return [rgba(stem % k) for k in ("colour", "normal", "roughness")]


def mip1(img, normal=False):
    f = img.astype(float)
    h, w = f.shape[:2]
    f = f[:h // 2 * 2, :w // 2 * 2]
    if normal:
        return f.reshape(h // 2, 2, w // 2, 2, 4).mean(axis=(1, 3))
    a = f[..., 3:4] / 255
    pre = np.concatenate([f[..., :3] * a, f[..., 3:4]], -1).reshape(h // 2, 2, w // 2, 2, 4).mean(axis=(1, 3))
    with np.errstate(invalid="ignore", divide="ignore"):
        rgb = np.where(pre[..., 3:4] > 0, pre[..., :3] / (pre[..., 3:4] / 255), 0)
    return np.concatenate([rgb, pre[..., 3:4]], -1)


def lit(c, n, r, sd, zoom1=False):
    if zoom1:
        c, n = mip1(c), mip1(n, normal=True)
        r = mip1(r)
    o = shade(c, n, r, sd)
    return (over(o, SPACE) * 255).round().astype(np.uint8), o[..., 3] > 0.5


def up(a, k):
    return np.kron(a, np.ones((k, k, 1), dtype=a.dtype)) if a.ndim == 3 else np.kron(a, np.ones((k, k), dtype=a.dtype))


def tile(arr, k):
    if arr.ndim == 2:
        arr = np.repeat(arr[..., None], 3, 2)
    return Image.fromarray(up(arr[..., :3].astype(np.uint8), k))


class Sheet:
    def __init__(self, w, h):
        self.im = Image.new("RGB", (w, h), SHEET)
        self.d = ImageDraw.Draw(self.im)
        self.y = 16

    def text(self, x, y, s, n=16, col=INK):
        self.d.text((x, y), s, fill=col, font=font(n))

    def paste(self, img, x, y):
        self.im.paste(img, (x, y))


def maps_sheet(van, ours, icon, out):
    LABEL = 230
    rows = [("colour (RGB)", lambda m: m[0]), ("normal (RGB)", lambda m: m[1]),
            ("roughness RGB: subsurface colour", lambda m: m[2]),
            ("roughness A: roughness (raw)", lambda m: m[2][..., 3]),
            ("colour A", lambda m: m[0][..., 3])]
    k = {"small": 2, "chunk": 4}
    cell = {s: {"small": 128, "chunk": 50}[s] * k[s] + 8 for s in k}
    width = LABEL + max(cell[s] * COUNT[s] for s in k) + 24
    height = 140 + sum(len(rows) * 2 * cell[s] + 70 for s in k)
    sh = Sheet(width, height)
    sh.text(16, sh.y, "Radiant asteroid and chunk: maps beside promethium's (each pair: promethium above, radiant below)", 22)
    sh.text(16, sh.y + 30, "as the engine reads them: colour; normal (R = x east, G = y south, B facing); roughness map RGB = "
            "subsurface colour, A = roughness. Black = transparent.", 15, DIM)
    ic = Image.open(icon).convert("RGBA")
    bg = Image.new("RGBA", ic.size, SHEET + (255,))
    bg.alpha_composite(ic)
    sh.paste(bg.convert("RGB").resize((ic.width * 2, ic.height * 2), Image.NEAREST), width - ic.width * 2 - 16, 60)
    sh.text(width - ic.width * 2 - 16, 60 + ic.height * 2 + 4, "radiant chunk icon (graphics/icons), 2x", 13, DIM)
    y = 60 + ic.height * 2 + 30
    for size in ("small", "chunk"):
        px = {"small": 128, "chunk": 50}[size]
        sh.text(16, y, f"{size}: {COUNT[size]} variations, {px} px, shown {k[size]}x", 20)
        y += 34
        for label, pick in rows:
            for who, d, kind in (("promethium", van, "promethium"), ("radiant", ours, "radiant")):
                sh.text(16, y + 8, label, 14, INK if who == "radiant" else DIM)
                sh.text(16, y + 28, who, 14, DIM)
                for v in range(1, COUNT[size] + 1):
                    sh.paste(tile(pick(maps(d, kind, size, v)), k[size]), LABEL + (v - 1) * cell[size], y)
                y += cell[size]
            y += 6
        y += 24
    sh.im = sh.im.crop((0, 0, width, y))
    sh.im.save(os.path.join(out, "maps-sheet.png"))


def lit_sheet(van, ours, icon, out):
    LABEL = 300
    sets = [("promethium: its own maps and shading", van, "promethium", PROMETHIUM),
            ("radiant: shading as inherited (red rim)", ours, "radiant", PROMETHIUM),
            ("radiant: rim light blue (T03, previewed)", ours, "radiant", RIM_BLUE)]
    meas = {}
    k = {"small": 2, "chunk": 4}
    cell = {s: {"small": 128, "chunk": 50}[s] * k[s] + 8 for s in k}
    width = LABEL + cell["small"] * 7 + 24
    sh = Sheet(width, 6000)
    sh.text(16, sh.y, "Radiant asteroid and chunk, lit by the engine's asteroid shader (asteroid.frag, ported), beside promethium", 22)
    sh.text(16, sh.y + 30, "Approximate: shaded at texture resolution and at mip 1; unrotated; no shadow, space background, "
            "parallax or bloom. Light from asteroid.lua: key {0.75, 0.22, -1}, rim {0.5, 0, 0.95}.", 15, DIM)
    ic = Image.open(icon).convert("RGBA")
    bg = Image.new("RGBA", ic.size, SPACE + (255,))
    bg.alpha_composite(ic)
    sh.paste(bg.convert("RGB").resize((ic.width * 2, ic.height * 2), Image.NEAREST), width - ic.width * 2 - 16, 60)
    sh.text(width - ic.width * 2 - 16, 60 + ic.height * 2 + 4, "radiant chunk icon, 2x", 13, DIM)
    y = 60 + ic.height * 2 + 30
    for size in ("small", "chunk"):
        sh.text(16, y, f"{size}: zoomed in (texture resolution, game zoom 2), shown {k[size]}x", 20)
        y += 34
        for label, d, kind, sd in sets:
            sh.d.rectangle((LABEL - 4, y - 4, LABEL + cell[size] * COUNT[size], y + cell[size] - 4), fill=SPACE)
            sh.text(16, y + 8, label, 14)
            px_all, white, clip = [], 0, 0
            for v in range(1, COUNT[size] + 1):
                img, m = lit(*maps(d, kind, size, v), sd)
                sh.paste(tile(img, k[size]), LABEL + (v - 1) * cell[size], y)
                px_all.append(img[m])
                white += int((img[m] >= 250).all(-1).sum())
                clip += int((img[m] >= 255).any(-1).sum())
            p = np.concatenate(px_all).astype(float)
            lum = 0.299 * p[:, 0] + 0.587 * p[:, 1] + 0.114 * p[:, 2]
            meas[f"{size} | {label}"] = dict(lum_p5_50_95=[int(np.percentile(lum, q)) for q in (5, 50, 95)],
                                            white_px=white, clipped_px=clip, px=int(len(p)))
            y += cell[size]
        y += 10
        sh.text(16, y, f"{size}: game zoom 1 (mip 1), actual pixels, then 3x", 20)
        y += 34
        for label, d, kind, sd in sets:
            imgs = [lit(*maps(d, kind, size, v), sd, zoom1=True)[0] for v in range(1, COUNT[size] + 1)]
            strip = np.concatenate([np.pad(i, ((0, 0), (0, 6), (0, 0)), constant_values=SPACE[0]) for i in imgs], 1)
            sh.text(16, y + 4, label, 14)
            sh.paste(Image.fromarray(strip), LABEL, y)
            y += strip.shape[0] + 6
            sh.paste(Image.fromarray(up(strip, 3)), LABEL, y)
            y += strip.shape[0] * 3 + 14
        y += 24
    sh.im = sh.im.crop((0, 0, max(width, sh.im.width), y))
    sh.im.save(os.path.join(out, "lit-sheet.png"))
    json.dump(meas, open(os.path.join(out, "lit-measures.json"), "w"), indent=1)
    for k_, v_ in meas.items():
        print(k_, v_)


if __name__ == "__main__":
    van, ours, icon, out = sys.argv[1:5]
    os.makedirs(out, exist_ok=True)
    maps_sheet(van, ours, icon, out)
    lit_sheet(van, ours, icon, out)
