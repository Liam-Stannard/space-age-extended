"""Vent Pump, round 4 (T03): the helium sight glass's measures and its sheet panel, for both artists'
sheet scripts (vpa4_sheets.py, vpb4_sheets.py). The definitions are the study's
(helium-study/vp4_helium_sheet.py), over the whole frame where they can be:

  white      px with alpha >= 8 and R, G, B all >= 250, in every frame: the idle frame, the plate,
             every working frame, every rotation, every helium-glow frame; at 1x and at 2x; counted
             in the helium-glow frames, inside the glass (lit idle and working frames) and over the
             whole lit frame
  clipped    px with alpha >= 8 and any channel at 255, the same frames; the whole frame's also split
             out as the melt's orange (R > 150, R - B > 80)
  he_peak    the brightest luminance (0.299 R + 0.587 G + 0.114 B) of the helium-glow frames
             (vp4_glass.run4: sun, sky, ground and the melt's glow off) composited on black, 1x and
             2x: vanilla's 87-171
  he_hue     the luminance-weighted mean hue of those frames' px with L >= 24, and its 5th-95th
             percentile range, degrees
  pale_cyan  px inside the glass (hemask.png) in the lit idle and working frames with hue 165-215,
             HSV saturation >= 0.10 and L >= 110; 1x and 2x
  frost      px inside the glass in those frames with L >= 200 and saturation <= 0.12
  glass_px   the glass's area at 1x (mask > 128), the glass's box in px
  level_dL   the mean |dL| inside the glass between consecutive working frames at 1x (the idle frame
             is one frame: still by construction)
  full, draw the working frames with the least and the most helium glow inside the glass: the level
             full between strokes, and the deepest draw (the peach-pink flush)
"""
import colorsys
import glob
import math
import os

from PIL import Image, ImageChops, ImageDraw

CYAN = (int(165 * 255 / 360), int(215 * 255 / 360))


def _load(path, canvas, k):
    im = Image.open(path).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    if k != 4:
        im = im.convert("RGBa").resize((canvas[0] * k, canvas[1] * k), Image.LANCZOS).convert("RGBA")
    return im


def _wc(im, within=None, split=False):
    """White and clipped px (alpha >= 8); within: a mask to count inside; split: also return the clipped
    px that are the melt's orange (R > 150, R - B > 80: its crest #FF9E52 has R at 255 by definition)."""
    r, g, b, a = im.split()
    op = a.point(lambda v: 255 if v >= 8 else 0)
    if within is not None:
        op = ImageChops.multiply(op, within)
    w = ImageChops.multiply(ImageChops.multiply(r.point(lambda v: 255 if v >= 250 else 0),
                                                g.point(lambda v: 255 if v >= 250 else 0)),
                            b.point(lambda v: 255 if v >= 250 else 0))
    c = ImageChops.lighter(ImageChops.lighter(r.point(lambda v: 255 if v == 255 else 0),
                                              g.point(lambda v: 255 if v == 255 else 0)),
                           b.point(lambda v: 255 if v == 255 else 0))
    wn, cn = ImageChops.multiply(w, op).histogram()[255], ImageChops.multiply(c, op).histogram()[255]
    if not split:
        return wn, cn
    orange = ImageChops.multiply(r.point(lambda v: 255 if v > 150 else 0),
                                 ImageChops.subtract(r, b).point(lambda v: 255 if v > 80 else 0))
    cm = ImageChops.multiply(ImageChops.multiply(c, op), orange).histogram()[255]
    return wn, cn, cm


def _on_black(im):
    blk = Image.new("RGBA", im.size, (0, 0, 0, 255))
    blk.alpha_composite(im)
    return blk.convert("RGB")


def _cyan_frost(im, mask):
    rgb = im.convert("RGB")
    h, s, _ = rgb.convert("HSV").split()
    L = rgb.convert("L")
    op = ImageChops.multiply(im.getchannel("A").point(lambda v: 255 if v >= 128 else 0), mask)
    cy = ImageChops.multiply(ImageChops.multiply(h.point(lambda v: 255 if CYAN[0] <= v <= CYAN[1] else 0),
                                                 s.point(lambda v: 255 if v >= 26 else 0)),
                             L.point(lambda v: 255 if v >= 110 else 0))
    fr = ImageChops.multiply(L.point(lambda v: 255 if v >= 200 else 0), s.point(lambda v: 255 if v <= 31 else 0))
    return ImageChops.multiply(cy, op).histogram()[255], ImageChops.multiply(fr, op).histogram()[255]


def _circ(hs):
    if not hs:
        return None, None
    x = sum(math.cos(math.radians(h)) * w for h, w in hs)
    y = sum(math.sin(math.radians(h)) * w for h, w in hs)
    c = math.degrees(math.atan2(y, x)) % 360
    d = sorted(((h - c + 180) % 360 - 180) for h, _ in hs)
    return round(c, 1), [round((c + d[int(0.05 * (len(d) - 1))]) % 360, 1), round((c + d[int(0.95 * (len(d) - 1))]) % 360, 1)]


def mask_of(d, canvas, k):
    m = Image.open(os.path.join(d, "hemask.png")).convert("L")
    if k != 4:
        m = m.resize((canvas[0] * k, canvas[1] * k), Image.LANCZOS)
    return m.point(lambda v: 255 if v > 128 else 0)


def measure(d, canvas, nf):
    m = {}
    M1, M2 = mask_of(d, canvas, 1), mask_of(d, canvas, 2)
    m["glass_px_1x"] = M1.histogram()[255]
    m["glass_box_1x"] = list(M1.getbbox() or ())
    lit = [os.path.join(d, "idle.png"), os.path.join(d, "plate.png")] + \
        [os.path.join(d, f"working-{f:02d}.png") for f in range(nf)] + sorted(glob.glob(os.path.join(d, "rot-*.png")))
    W = {1: 0, 2: 0}
    C = {1: 0, 2: 0}
    CM = {1: 0, 2: 0}
    WG = {1: 0, 2: 0}
    CG = {1: 0, 2: 0}
    cy = fr = 0
    work1 = []
    for p in lit:
        for k, mk in ((1, M1), (2, M2)):
            im = _load(p, canvas, k)
            w, c, cm = _wc(im, split=True)
            W[k] += w
            C[k] += c
            CM[k] += cm
            name = os.path.basename(p)
            if name == "idle.png" or name.startswith("working-"):
                wg, cg = _wc(im, within=mk)
                WG[k] += wg
                CG[k] += cg
                a, b = _cyan_frost(im, mk)
                cy += a
                fr += b
                if k == 1 and name.startswith("working-"):
                    work1.append(im)
    GW = {1: 0, 2: 0}
    GC = {1: 0, 2: 0}
    pk = {1: 0, 2: 0}
    hs = []
    glow_in = []
    box = M1.getbbox()
    for f in range(nf):
        for k in (1, 2):
            im = _load(os.path.join(d, f"heglow-{f:02d}.png"), canvas, k)
            w, c = _wc(im)
            GW[k] += w
            GC[k] += c
            ob = _on_black(im)
            L = ob.convert("L")
            pk[k] = max(pk[k], L.getextrema()[1])
            if k == 1:
                glow_in.append(sum(i * n for i, n in enumerate(ImageChops.multiply(L, M1).histogram())))
                if box:
                    x0, y0, x1, y1 = box
                    sub = ob.crop((x0 - 4, y0 - 4, x1 + 4, y1 + 4))
                    for r_, g_, b_ in sub.getdata():
                        Lv = 0.299 * r_ + 0.587 * g_ + 0.114 * b_
                        if Lv >= 24:
                            hs.append((colorsys.rgb_to_hsv(r_ / 255, g_ / 255, b_ / 255)[0] * 360, Lv))
    m["white"] = dict(lit_1x=W[1], lit_2x=W[2], glow_1x=GW[1], glow_2x=GW[2])
    m["clipped"] = dict(lit_1x=C[1], lit_2x=C[2], glow_1x=GC[1], glow_2x=GC[2])
    m["clipped_melt_orange"] = dict(lit_1x=CM[1], lit_2x=CM[2])
    m["in_glass"] = dict(white_1x=WG[1], white_2x=WG[2], clipped_1x=CG[1], clipped_2x=CG[2])
    m["frames_checked"] = dict(lit=len(lit), glow=nf, scales=["1x", "2x"])
    m["he_peak_1x"], m["he_peak_2x"] = round(pk[1]), round(pk[2])
    m["he_peak_in_87_171"] = 87 <= pk[1] <= 171
    m["he_hue_deg"], m["he_hue_p5_p95"] = _circ(hs)
    m["pale_cyan_px"], m["frost_px"] = cy, fr
    dl = []
    for f in range(nf):
        a = work1[f].convert("L")
        b = work1[(f + 1) % nf].convert("L")
        diff = ImageChops.multiply(ImageChops.difference(a, b), M1)
        dl.append(sum(i * n for i, n in enumerate(diff.histogram())) / max(1, m["glass_px_1x"]))
    m["level_dL_1x"] = round(sum(dl) / len(dl), 2)
    m["full_frame"] = min(range(nf), key=lambda f: glow_in[f])
    m["draw_frame"] = max(range(nf), key=lambda f: glow_in[f])
    return m


def panel(d, canvas, nf, m, ground_rgba=(74, 66, 58, 255), bg=(30, 29, 28, 255), font=None, text=(228, 222, 210),
          sub=(175, 168, 156)):
    """The glass at game scale: 1x shown x4 (nearest) idle, level full, the draw; then the loop at 2x,
    every frame step, cropped round the glass; captions above each."""
    box = m["glass_box_1x"]
    x0, y0, x1, y1 = box
    pad = 14
    c1 = (x0 - pad, y0 - pad, x1 + pad, y1 + pad)

    def on_g(im):
        g = Image.new("RGBA", im.size, ground_rgba)
        g.alpha_composite(im)
        return g

    def cap(im, s1, s2=""):
        o = Image.new("RGBA", (max(im.width, 120), im.height + 36), bg)
        dr = ImageDraw.Draw(o)
        dr.text((0, 0), s1, font=font(12, True), fill=text)
        dr.text((0, 16), s2, font=font(11), fill=sub)
        o.alpha_composite(im, (0, 36))
        return o

    ims = []
    for f, s1, s2 in (("idle", "1x shown x4", "idle: unlit, still"),
                      (f"working-{m['full_frame']:02d}", "1x shown x4", f"f{m['full_frame']}: level full"),
                      (f"working-{m['draw_frame']:02d}", "1x shown x4", f"f{m['draw_frame']}: the draw")):
        im = on_g(_load(os.path.join(d, f + ".png"), canvas, 1)).crop(c1)
        ims.append(cap(im.resize((im.width * 4, im.height * 4), Image.NEAREST), s1, s2))
    step = max(1, nf // 8)
    c2 = tuple(2 * v for v in c1)
    for f in range(0, nf, step):
        im = on_g(_load(os.path.join(d, f"working-{f:02d}.png"), canvas, 2)).crop(c2)
        ims.append(cap(im, f"2x f{f}", "draw" if f == m["draw_frame"] else ("full" if f == m["full_frame"] else "")))
    H = max(i.height for i in ims)
    out = Image.new("RGBA", (sum(i.width for i in ims) + 8 * (len(ims) - 1), H), bg)
    x = 0
    for i in ims:
        out.alpha_composite(i, (x, 0))
        x += i.width + 8
    return out


def lines(m):
    return [f"Helium glow (the glass alone, melt off): peak {m['he_peak_1x']} at 1x ({m['he_peak_2x']} at 2x; vanilla "
            f"87-171: {'inside' if m['he_peak_in_87_171'] else 'OUTSIDE'}), hue {m['he_hue_deg']} deg (p5-p95 "
            f"{m['he_hue_p5_p95'][0]}-{m['he_hue_p5_p95'][1]}).",
            f"White / clipped px: the helium glow alone ({m['frames_checked']['glow']} frames, 1x and 2x) white "
            f"{m['white']['glow_1x'] + m['white']['glow_2x']}, clipped {m['clipped']['glow_1x'] + m['clipped']['glow_2x']}; "
            f"inside the glass (idle and working, 1x and 2x) white {m['in_glass']['white_1x'] + m['in_glass']['white_2x']}, "
            f"clipped {m['in_glass']['clipped_1x'] + m['in_glass']['clipped_2x']}; the whole frame "
            f"({m['frames_checked']['lit']} lit frames, 1x / 2x) white {m['white']['lit_1x']} / {m['white']['lit_2x']}, "
            f"clipped {m['clipped']['lit_1x']} / {m['clipped']['lit_2x']}, of which the melt's orange "
            f"{m['clipped_melt_orange']['lit_1x']} / {m['clipped_melt_orange']['lit_2x']} (round 3's parts and melt, "
            f"unchanged: see the report).",
            f"Inside the glass, idle and working, 1x and 2x: pale cyan {m['pale_cyan_px']} px, frost {m['frost_px']} px. "
            f"Glass {m['glass_px_1x']} px at 1x; its level's motion (mean dL in the glass, frame to frame) "
            f"{m['level_dL_1x']}; level full at f{m['full_frame']}, the deepest draw at f{m['draw_frame']}."]
