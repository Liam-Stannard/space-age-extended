#!/usr/bin/env python3
"""The Radiant Generator model's review sheet, its working GIFs and its frame strips.

  python3 concept/radiant-generator/model/review_sheet.py <render.sh out-dir> <sheet-dir> \
      [--measures <measures.json>] [--gif2x <path>]

<sheet-dir> gets review.png (one page, under 8000 px on its longer side) and working-1x.gif;
--gif2x writes the 2x GIF where it is told (scratch: 2x GIFs stay out of git).

Every 1x panel is composited from the packed sheets and meta.json exactly as the engine
layers them (each sheet at its shift round the entity origin, 64 px a tile): the shadow at
half strength, the plate, the moving layers' frame f in the order render.json declares them,
then, working, the windows' frame f, the glows' frame f added (RGB only) and the status lamps'
white cut tinted green. Idle is the same with no window, glow or lamp: the stopped machine.
The 2x panels are made the same way from the 4x renders (hi/), brought to 2x, each glow frame
turned to light with its bloom at twice its radius and every layer rolled off as pack.py rolls
the sheets -- a closer look, not what ships.

Beside them, on the same ground at the same scale: the signed-off round 7
(options/round-7/: its 1x GIF's frame 0, and its sheet's 2x working panel) and vanilla's steam
engine, steam turbine and fusion generator (tools/blender/measure.py's vanilla() stills), with
the nuclear reactor whose rise is the bar (measure_reactor.py). Then the working loop's 32
frames, every animation layer's sheet as packed, and the wreck beside vanilla's steam-turbine
and nuclear-reactor remnants.
"""
import argparse
import json
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import contract  # noqa: E402
import measure  # noqa: E402
import pack  # noqa: E402

GROUND = (74, 66, 58, 255)
BG, TXT, HEAD = (30, 30, 30, 255), (230, 222, 205), (240, 200, 120)
LAMP = (0, 255, 0)
PPT = 64
R7 = os.path.join(HERE, "..", "options", "round-7")
FD = measure.FD


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if bold else "") + ".ttf", size)


def ground(size, origin, ppt, foot):
    """The game's ground with the tile grid, the footprint brighter."""
    g = Image.new("RGBA", size, GROUND)
    d = ImageDraw.Draw(g, "RGBA")
    ox, oy = origin
    fw, fh = foot
    for i in range(-20, 21):
        x = ox + (i - fw / 2 % 1) * ppt
        d.line([(x, 0), (x, size[1])], fill=(255, 255, 255, 28))
        y = oy + (i - fh / 2 % 1) * ppt
        d.line([(0, y), (size[0], y)], fill=(255, 255, 255, 28))
    d.rectangle([ox - fw / 2 * ppt, oy - fh / 2 * ppt, ox + fw / 2 * ppt, oy + fh / 2 * ppt],
                outline=(255, 255, 255, 90))
    return g


def half(im):
    a = im.getchannel("A").point(lambda v: v // 2)
    return Image.merge("RGBA", (*Image.new("RGB", im.size).split(), a))


def add_rgb(under, light):
    lit = ImageChops.add(under.convert("RGB"), light.convert("RGB"))
    return Image.merge("RGBA", (*lit.split(), under.getchannel("A")))


def light_rgb(im):
    """A glow sheet's frame as the light it adds: RGB times alpha."""
    r, g, b, a = im.split()
    return Image.merge("RGB", [ImageChops.multiply(c, a) for c in (r, g, b)])


def tint(cut, rgb):
    a = cut.getchannel("A")
    return Image.merge("RGBA", (*Image.new("RGB", cut.size, rgb).split(), a))


class Sheets:
    """The packed sheets, placed as the engine places them."""

    def __init__(self, src):
        self.dir = os.path.join(src, "sheets")
        self.meta = json.load(open(os.path.join(self.dir, "meta.json")))
        self.decl = contract.load(os.path.join(src, "renders"))
        self.canvas = tuple(self.decl["canvas"])
        self.cache = {}

    def img(self, name):
        if name not in self.cache:
            self.cache[name] = Image.open(os.path.join(self.dir, name + ".png")).convert("RGBA")
        return self.cache[name]

    def frame(self, name, f=0):
        m = self.meta[name]
        w, h = m["size"]
        n = m.get("frames", 1)
        f %= n
        line = m.get("line_length", n)
        im = self.img(name)
        return im.crop(((f % line) * w, (f // line) * h, (f % line) * w + w, (f // line) * h + h))

    def placed(self, name, f=0):
        """The sheet's frame f on the full canvas."""
        m = self.meta[name]
        fr = self.frame(name, f)
        out = Image.new("RGBA", self.canvas)
        cx, cy = self.canvas[0] / 2 + m["shift"][0] * PPT, self.canvas[1] / 2 + m["shift"][1] * PPT
        out.paste(fr, (round(cx - fr.width / 2), round(cy - fr.height / 2)))
        return out

    def compose(self, f, working):
        d = self.decl
        out = Image.new("RGBA", self.canvas)
        for p in d["passes"]:
            if p["kind"] == "shadow":
                out.alpha_composite(half(self.placed(p["sheet"])))
        out.alpha_composite(self.placed(next(p["sheet"] for p in d["passes"] if p["kind"] == "plate")))
        for a in d["animations"]:
            k = a.get("kind", "paint")
            if k == "paint" and (working or not a.get("working")):
                out.alpha_composite(self.placed(a["name"], f))
        if working:
            for a in d["animations"]:
                if a.get("kind") == "glow":
                    out = add_rgb(out, light_rgb(self.placed(a["name"], f)))
            for p in d["passes"]:
                if p["kind"] == "light":
                    out.alpha_composite(tint(self.placed(p["sheet"]), LAMP))
        return out


class Hi:
    """The 4x renders brought to 2x, layered the same way."""

    def __init__(self, src, decl):
        self.dir = os.path.join(src, "hi")
        self.decl = decl
        self.cache = {}

    def get(self, stem):
        if stem not in self.cache:
            im = Image.open(os.path.join(self.dir, stem + ".png")).convert("RGBA")
            self.cache[stem] = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
        return self.cache[stem]

    def compose(self, f, working):
        d = self.decl
        out = None
        for p in d["passes"]:
            if p["kind"] == "shadow":
                out = half(pack.clean(self.get(p["name"]).copy()))
        out.alpha_composite(pack.roll(self.get(next(p["name"] for p in d["passes"] if p["kind"] == "plate")))[0])
        for a in d["animations"]:
            k = a.get("kind", "paint")
            if k == "paint" and (working or not a.get("working")):
                out.alpha_composite(pack.roll(pack.clean(self.get(contract.frame(a["name"], f)).copy()))[0])
        if working:
            for a in d["animations"]:
                if a.get("kind") == "glow":
                    bloom = [[r * 2, g] for r, g in a.get("bloom") or ()]
                    out = add_rgb(out, light_rgb(pack.glow_frame(self.get(contract.frame(a["name"], f)), bloom)))
            for p in d["passes"]:
                if p["kind"] == "light":
                    out.alpha_composite(tint(pack.light_layer(self.get(p["name"])), LAMP))
        return out


def on_ground(im, k, foot):
    g = ground(im.size, (im.width / 2, im.height / 2), PPT * k, foot)
    g.alpha_composite(im)
    return g


def vanilla_panel(name, k=1):
    label, foot, still, shadow, light = measure.vanilla(name, "")
    im = Image.new("RGBA", still.size)
    im.alpha_composite(shadow)
    im.alpha_composite(still)
    im = add_rgb(im, light)
    g = on_ground(im, 1, foot)
    bb = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    pad = 24
    return label, g.crop((bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad))


def vanilla_remnants(rel, w, h, shift, foot, scale_note=""):
    png = os.path.join(FD, rel)
    im = Image.open(png).convert("RGBA").crop((0, 0, w, h))
    S = max(w, h) + 2 * PPT
    can = Image.new("RGBA", (S, S))
    can.alpha_composite(im, (round(S / 2 + shift[0] - w / 2), round(S / 2 + shift[1] - h / 2)))
    return on_ground(can, 1, foot)


def crop_to(im, bb, pad=16):
    return im.crop((bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--measures")
    ap.add_argument("--gif2x")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    S = Sheets(a.src)
    foot = tuple(S.decl["footprint"])
    nf = max(x["frames"] for x in S.decl["animations"])
    speed = next(x.get("animation_speed") for x in S.decl["animations"] if x.get("animation_speed"))
    ms = round(1000 / (60 * speed))

    work = [S.compose(f, True) for f in range(nf)]
    idle = S.compose(0, False)
    bb = None
    for im in work + [idle]:
        b = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    g_work = [crop_to(on_ground(im, 1, foot), bb) for im in work]
    g_idle = crop_to(on_ground(idle, 1, foot), bb)
    gif1 = os.path.join(a.out, "working-1x.gif")
    g_work[0].save(gif1, save_all=True, append_images=g_work[1:], duration=ms, loop=0, disposal=1, optimize=True)

    H = Hi(a.src, S.decl)
    bb2 = tuple(v * 2 for v in bb)
    w2_0 = crop_to(on_ground(H.compose(0, True), 2, foot), bb2, 32)
    i2 = crop_to(on_ground(H.compose(0, False), 2, foot), bb2, 32)
    if a.gif2x:
        frames2 = [w2_0] + [crop_to(on_ground(H.compose(f, True), 2, foot), bb2, 32) for f in range(1, nf)]
        frames2[0].save(a.gif2x, save_all=True, append_images=frames2[1:], duration=ms, loop=0, disposal=1,
                        optimize=True)

    r7gif = Image.open(os.path.join(R7, "1-the-carousel-foundry-1x.gif"))
    r7gif.seek(0)
    r7_1x = r7gif.convert("RGBA")
    r7_2x = Image.open(os.path.join(R7, "1-the-carousel-foundry.png")).convert("RGBA").crop((10, 128, 782, 890))

    # the wreck: its sheet on ground, beside vanilla's
    wreck = S.placed("remnants") if "remnants" in S.meta else None
    panels_w = []
    if wreck is not None:
        wc = tuple(S.decl["passes"][[p["kind"] for p in S.decl["passes"]].index("remnants")]["canvas"])
        wr = Image.new("RGBA", wc)
        fr = S.frame("remnants")
        m = S.meta["remnants"]
        wr.paste(fr, (round(wc[0] / 2 + m["shift"][0] * PPT - fr.width / 2),
                      round(wc[1] / 2 + m["shift"][1] * PPT - fr.height / 2)))
        panels_w.append(("the wreck (remnants sheet), 1x", on_ground(wr, 1, foot)))
        hi_w = Image.open(os.path.join(a.src, "hi", "wreck.png")).convert("RGBA")
        hi_w = pack.clean(hi_w.resize((hi_w.width // 2, hi_w.height // 2), Image.LANCZOS))
        panels_w.append(("the wreck, 2x (from the 4x render)", on_ground(hi_w, 2, foot)))
    panels_w.append(("vanilla steam turbine remnants, 1x",
                     vanilla_remnants("base/graphics/entity/steam-turbine/remnants/steam-turbine-remnants.png",
                                      460, 408, (12, 0), (3, 5))))
    panels_w.append(("vanilla nuclear reactor remnants, 1x",
                     vanilla_remnants("base/graphics/entity/nuclear-reactor/remnants/nuclear-reactor-remnants.png",
                                      410, 396, (14, 8), (5, 5))))

    # ------------------------------------------------------------ the page
    rows = []
    rows.append(("Beside round 7 and vanilla, 1x (64 px a tile, the sprite's own size), working frame 0", [
        ("round 7, signed off (its 1x GIF, frame 0)", r7_1x),
        ("model, working, frame 0", g_work[0]), ("model, idle (the stopped machine)", g_idle),
        *[vanilla_panel(n) for n in ("steam-engine", "steam-turbine", "fusion-generator")],
        *([("icon (--icon, keyed: the 64 px mipmap strip, 2x)",
            Image.open(os.path.join(S.dir, "icon.png")).convert("RGBA").resize((240, 128), Image.NEAREST))]
          if os.path.isfile(os.path.join(S.dir, "icon.png")) else [])]))
    rows.append(("2x: round 7's sheet panel beside the model, working and idle", [
        ("round 7, working frame 0, 2x", r7_2x), ("model, working frame 0, 2x", w2_0), ("model, idle, 2x", i2)]))
    loop = []
    for f in range(nf):
        loop.append((f"frame {f}", g_work[f]))
    rows.append((f"The working loop, 1x: {nf} frames, {ms} ms a frame (animation_speed {speed:.6f})", loop))
    strips = []
    for x in S.decl["animations"]:
        nm = x["name"]
        im = S.img(nm)
        if x.get("kind") == "glow":
            lt = light_rgb(im).convert("RGBA")
            bgi = Image.new("RGBA", im.size, (0, 0, 0, 255))
            bgi.alpha_composite(lt)
            im = bgi
        else:
            gi = Image.new("RGBA", im.size, GROUND)
            gi.alpha_composite(im)
            im = gi
        strips.append((f"{nm}: {x['frames']} frames, {x['motion']}" + (f", {x['kind']}" if x.get("kind") else "")
                       + f", sheet {im.width} x {im.height}", im))
    rows.append(("Every animation layer as packed (its sheet; glows as the light they add, on black)", strips))
    rows.append(("The wreck, beside vanilla's remnants", panels_w))

    MAXW = 7600
    f_head, f_lab, f_txt = font(30, True), font(15), font(17)
    blocks = []
    for title, panels in rows:
        # pack the panels into lines no wider than MAXW
        lines, cur, w = [], [], 0
        for lab, im in panels:
            if im.width > MAXW:
                k = MAXW / im.width
                im = im.resize((MAXW, max(1, round(im.height * k))), Image.LANCZOS)
            if cur and w + im.width + 16 > MAXW:
                lines.append(cur)
                cur, w = [], 0
            cur.append((lab, im))
            w += im.width + 16
        if cur:
            lines.append(cur)
        blocks.append((title, lines))
    text = []
    if a.measures:
        text = open(a.measures).read().splitlines()
    W = max(max(sum(im.width + 16 for _, im in ln) for ln in lines) for _, lines in blocks) + 32
    H = 60 + sum(50 + sum(max(im.height for _, im in ln) + 24 for ln in lines) for _, lines in blocks) + 24 * len(text) + 40
    page = Image.new("RGBA", (max(W, 1200), H), BG)
    d = ImageDraw.Draw(page)
    d.text((16, 12), "RADIANT GENERATOR, THE SHIPPING MODEL (T08) -- the Carousel Foundry at 5 x 5, for Liam's sign-off",
           fill=HEAD, font=f_head)
    y = 60
    for title, lines in blocks:
        d.text((16, y), title, fill=HEAD, font=font(22, True))
        y += 40
        for ln in lines:
            x = 16
            for lab, im in ln:
                d.text((x, y), lab, fill=TXT, font=f_lab)
                page.alpha_composite(im, (x, y + 20))
                x += im.width + 16
            y += max(im.height for _, im in ln) + 24
        y += 10
    for t in text:
        d.text((16, y), t, fill=TXT, font=f_txt)
        y += 24
    page = page.crop((0, 0, page.width, y + 16))
    k = min(1.0, 7990 / max(page.size))
    if k < 1:
        page = page.resize((round(page.width * k), round(page.height * k)), Image.LANCZOS)
    page.convert("RGB").save(os.path.join(a.out, "review.png"))
    print(os.path.join(a.out, "review.png"), page.size)
    print(gif1, os.path.getsize(gif1) / 1e6, "MB")
    if a.gif2x:
        print(a.gif2x, os.path.getsize(a.gif2x) / 1e6, "MB")


if __name__ == "__main__":
    main()
