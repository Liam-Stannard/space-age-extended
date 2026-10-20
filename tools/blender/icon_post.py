#!/usr/bin/env python3
"""Bring item icon renders to size, finishing each size by rule, and pack them.

  python3 icon_post.py <hi-dir> <out-dir>

<hi-dir> is what icon_rig.main wrote: <item>/<finish>/<size>.png at SS x size and
icons.json. For every item and finish this writes

  <out-dir>/sizes/<item>/<finish>/<size>.png      each size from its own render,
                                                  finished by the rules below
  <out-dir>/downscale/<item>/<finish>/<size>.png  the comparison: the finished 64
                                                  shrunk to every smaller size, as
                                                  key-icons.py's keyed path does
  <out-dir>/strips/<finish>/<item>.png            120x64, key-icons.py --mips
  <out-dir>/strips-downscale/<finish>/<item>.png  the same, from the downscale

The rules are FFF #348's hand-finishing, done by rule; the item script declares
them per size in POST (icons.json "post"), any of:

  sharpen   [radius, percent]: unsharp mask on the colour -- the edges and the
            light/dark break between faces kept as heavy at 16 px as at 64
  contrast  factor about the object's own mean luminance: small sizes lose the
            mid-tones that separated the faces, so push them apart again
  alpha     [lo, hi]: alpha below lo is cut, above hi made solid, between
            stretched -- a crisp silhouette, no grey haze round the object
  shadow    [gain, lum_max, radius, cap]: a technology icon's cast shadow, denser
            and softer -- the part-transparent pixels darker than lum_max, blurred
            by radius px, raised by gain, held at cap (applied after "alpha";
            opaque pixels are untouched)
  rim       [strength, threshold]: an outline, lightened or darkened away from
            whichever of the slot and the ground it is nearest, on the outer ring
            of pixels whose luminance sits within threshold of either -- so the
            edge reads on both (pass criterion 3)

Always, after the rules: a pixel with alpha but no neighbour with alpha (8-way)
is removed -- the stray pixel FFF #348 says breaks an icon -- and alpha within
MARGIN of the canvas edge is checked (reported, not hidden).

Downsampling is premultiplied (downsample.py's reason: no dark fringe).
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageChops, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
KEY_ICONS = os.path.join(HERE, "..", "key-icons.py")
SLOT = (45, 44, 45)          # core/graphics/gui-new.png, the inventory slot's face (style "slot", {0, 424})
GROUND = (74, 66, 58)        # the review sheets' ground (preview.py)


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def shrink(path, k):
    im = Image.open(path).convert("RGBa")
    return im.resize((im.width // k, im.height // k), Image.LANCZOS).convert("RGBA")


def _bleed(im):
    """Colour carried out under the transparent pixels, so a filter on the colour
    never pulls in transparent black at the silhouette."""
    pm = im.convert("RGBa")
    rgb = im.convert("RGB")
    covered = im.getchannel("A").point(lambda a: 255 if a else 0)
    for r in (1, 2, 4):
        # a premultiplied blur, divided back out: the colour of the nearby object
        blur = pm.filter(ImageFilter.BoxBlur(r)).convert("RGBA")
        reach = blur.getchannel("A").point(lambda a: 255 if a else 0)
        fill_here = ImageChops.subtract(reach, covered)
        rgb = Image.composite(blur.convert("RGB"), rgb, fill_here)
        covered = ImageChops.lighter(covered, reach)
    return rgb


def sharpen(im, radius, percent):
    rgb = _bleed(im).filter(ImageFilter.UnsharpMask(radius=radius, percent=int(percent), threshold=0))
    rgb.putalpha(im.getchannel("A"))
    return rgb


def contrast(im, k):
    px = [p for p in im.get_flattened_data() if p[3] > 128]
    if not px:
        return im
    m = sum(lum(p) for p in px) / len(px)
    lut = [max(0, min(255, round(m + (v - m) * k))) for v in range(256)]
    r, g, b, a = im.split()
    return Image.merge("RGBA", (r.point(lut), g.point(lut), b.point(lut), a))


def alpha_snap(im, lo, hi):
    lut = [0 if v < lo else 255 if v > hi else round((v - lo) * 255 / (hi - lo)) for v in range(256)]
    r, g, b, a = im.split()
    return Image.merge("RGBA", (r, g, b, a.point(lut)))


def rim(im, strength, threshold):
    """Push the outer ring's luminance away from the slot and the ground where it
    sits close to either."""
    a = im.getchannel("A")
    inner = a.point(lambda v: 255 if v > 0 else 0).filter(ImageFilter.MinFilter(3))
    px, ipx, apx = im.load(), inner.load(), a.load()
    out = im.copy()
    opx = out.load()
    bgs = (lum(SLOT), lum(GROUND))
    for y in range(im.height):
        for x in range(im.width):
            if apx[x, y] == 0 or ipx[x, y]:
                continue                       # transparent, or not on the outline
            r, g, b, al = px[x, y]
            L = lum((r, g, b))
            near = min(bgs, key=lambda B: abs(L - B))
            if abs(L - near) >= threshold:
                continue
            # lift if the object is brighter than that background or nearly so, else sink
            target = near + threshold if L >= near - threshold / 3 else near - threshold
            k = (1 - strength) + strength * (target / L if L > 1 else 1)
            if L <= 1:
                opx[x, y] = (round(target), round(target), round(target), al)
            else:
                opx[x, y] = (min(255, round(r * k)), min(255, round(g * k)), min(255, round(b * k)), al)
    return out


def drop_strays(im):
    a = im.getchannel("A")
    apx = a.load()
    w, h = im.size
    out = im.copy()
    opx = out.load()
    n = 0
    for y in range(h):
        for x in range(w):
            if not apx[x, y]:
                continue
            if not any(apx[x + dx, y + dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                       if (dx or dy) and 0 <= x + dx < w and 0 <= y + dy < h):
                opx[x, y] = (0, 0, 0, 0)
                n += 1
    return out, n


def edge_clear(im, margin):
    a = im.getchannel("A")
    bb = a.getbbox()
    if not bb:
        return True
    return bb[0] >= margin and bb[1] >= margin and bb[2] <= im.width - margin and bb[3] <= im.height - margin


def shadow_gain(im, gain, lum_max, radius=0.0, cap=200):
    """The cast shadow, denser and softer: the part-transparent pixels darker than
    lum_max are the shadow; their alpha is blurred by radius (so the shadow spreads
    past its hard edge, as Space Age's soft shadows do), raised by gain and held at
    cap or under, so it stays a shadow and never reads as solid. Opaque pixels and
    everything brighter than lum_max are left as they are."""
    px = im.load()
    w, h = im.size
    mask = Image.new("L", im.size, 0)
    mp = mask.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if 0 < a < 250 and lum((r, g, b)) < lum_max:
                mp[x, y] = a
    if radius:
        mask = mask.filter(ImageFilter.GaussianBlur(radius))
    mp = mask.load()
    out = im.copy()
    opx = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            m = mp[x, y]
            if not m:
                continue
            shadowish = a == 0 or (a < 250 and lum((r, g, b)) < lum_max)
            if shadowish:
                na = min(cap, round(m * gain))
                if na > a:
                    opx[x, y] = (0, 0, 0, na) if a == 0 else (r, g, b, na)
    return out


def finish(im, rules):
    if "contrast" in rules:
        im = contrast(im, rules["contrast"])
    if "sharpen" in rules:
        im = sharpen(im, *rules["sharpen"])
    if "alpha" in rules:
        im = alpha_snap(im, *rules["alpha"])
    if "shadow" in rules:
        im = shadow_gain(im, *rules["shadow"])
    # colour under alpha 0 is meaningless; zero it so the strip is clean
    im = Image.composite(im, Image.new("RGBA", im.size, (0, 0, 0, 0)), im.getchannel("A").point(lambda v: 255 if v else 0))
    if "rim" in rules:
        im = rim(im, *rules["rim"])
    return drop_strays(im)


def main(hi, out):
    decl = json.load(open(os.path.join(hi, "icons.json")))
    ss, sizes, margin = decl["ss"], decl["sizes"], decl["margin"]
    report = {}
    for item in decl["items"]:
        for fin in decl["finishes"]:
            levels, small = [], []
            for s in sizes:
                im = shrink(os.path.join(hi, item, fin, f"{s}.png"), ss)
                rules = decl["post"].get(item, {}).get(str(s), {})
                im, strays = finish(im, rules)
                p = os.path.join(out, "sizes", item, fin, f"{s}.png")
                os.makedirs(os.path.dirname(p), exist_ok=True)
                im.save(p)
                levels.append(p)
                report[f"{item}/{fin}/{s}"] = {"strays_removed": strays, "edge_clear": edge_clear(im, margin)}
            # the comparison: the finished 64 shrunk, exactly as key-icons.py's mip_strip
            big = Image.open(levels[0]).convert("RGBA")
            for s in sizes:
                p = os.path.join(out, "downscale", item, fin, f"{s}.png")
                os.makedirs(os.path.dirname(p), exist_ok=True)
                (big if s == sizes[0] else big.resize((s, s), Image.LANCZOS)).save(p)
                small.append(p)
            master = os.path.join(hi, item, fin, f"{sizes[0]}.png")
            for kind, ps in (("strips", levels), ("strips-downscale", small)):
                subprocess.run([sys.executable, KEY_ICONS, "--mips", os.path.join(out, kind, fin), item, *ps,
                                "--master", master], check=True)
    with open(os.path.join(out, "post.json"), "w") as f:
        json.dump(report, f, indent=1)
    bad = [k for k, v in report.items() if not v["edge_clear"]]
    print("edge clear at every size" if not bad else "EDGE TOUCHED: " + ", ".join(bad))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
