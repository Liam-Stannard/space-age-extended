#!/usr/bin/env python3
"""The Siderane turbine's plates beside the adopted master and vanilla's steam turbine, at 1x and 2x.

  python3 compare_plates.py <render-dir> <compare.png> [--title <text>]

<render-dir> is render.sh's <out-dir>/renders (or any directory of sprite-size renders on
the model's canvas, origin at its centre): still-<direction>.png, and shadow-<direction>.png
when there is one. One row per direction, every panel on one ground at 64 px a tile with
the footprint's grid:

  adopted   concept/crust-turbine/master-v2.png, the adopted design's master plate (a plan
            view: its camera was rejected, spec 12), scaled so its stubs span the 5 tiles,
            its stubs' axis on the origin; turned a quarter for the vertical row
  round 1   round 1's plate (round-1/sheets: its shadow at 50 %, base and rotor frame 0 at
            meta.json's shifts), so round 2's change shows beside it
  ours      the stopped machine: shadow at 50 %, then the still (the plate with the rotor's
            frame 0)
  vanilla   steam-turbine-H / -V frame 0 and its shadow, at their prototype shifts

then the same three at 2x, cropped to the middle 3.5 x 3.5 tiles. finish.py's and
tonal.py's measures under ours and vanilla's.
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
TOOLS = os.path.join(REPO, "tools", "blender")
sys.path.insert(0, os.path.join(REPO, "tools"))
import paths  # noqa: E402   tools/paths.py: where Factorio is
VAN = os.path.join(paths.factorio_data(), "base/graphics/entity/steam-turbine")
MASTER = os.path.join(HERE, "..", "master-v2.png")
ROUND1 = os.path.join(HERE, "round-1", "sheets")
GROUND = (74, 66, 58, 255)
PPT = 64
S = 448                                    # each 1x panel; the origin at its centre
FOOT = {"horizontal": (5, 3), "vertical": (3, 5)}
# vanilla's layers: (file, frame w, h, shift in hr px) -- util.by_pixel at scale 0.5, doubled
VANILLA = {"horizontal": (("steam-turbine-H-shadow.png", 435, 150, (57, 36)),
                          ("steam-turbine-H.png", 320, 245, (0, -5.5))),
           "vertical": (("steam-turbine-V-shadow.png", 302, 260, (79, 49)),
                        ("steam-turbine-V.png", 217, 374, (9.5, 0)))}


def font(n):
    try:
        return ImageFont.load_default(n)
    except TypeError:
        return ImageFont.load_default()


def grid(im, d):
    dr = ImageDraw.Draw(im)
    c = S // 2
    for k in range(-4, 5):
        dr.line([(c + k * PPT, 0), (c + k * PPT, S)], fill=(255, 255, 255, 28))
        dr.line([(0, c + k * PPT), (S, c + k * PPT)], fill=(255, 255, 255, 28))
    w, h = FOOT[d]
    dr.rectangle([c - w * PPT / 2, c - h * PPT / 2, c + w * PPT / 2, c + h * PPT / 2], outline=(255, 255, 255, 110))


def panel(d):
    im = Image.new("RGBA", (S, S), GROUND)
    grid(im, d)
    return im


def over(base, layer, pos, alpha=1.0):
    if alpha != 1.0:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer = layer.copy()
        layer.putalpha(a)
    tmp = Image.new("RGBA", base.size)
    tmp.paste(layer, pos)
    base.alpha_composite(tmp)


def centred(base, layer, shift=(0, 0), alpha=1.0, black=False):
    if black:
        a = layer.getchannel("A")
        layer = Image.new("RGBA", layer.size, (0, 0, 0, 255))
        layer.putalpha(a)
    over(base, layer, (round(S / 2 - layer.width / 2 + shift[0]), round(S / 2 - layer.height / 2 + shift[1])), alpha)


def ours(src, d):
    im = panel(d)
    sh = os.path.join(src, f"shadow-{d}.png")
    if os.path.isfile(sh):
        centred(im, Image.open(sh).convert("RGBA"), alpha=0.5, black=True)
    centred(im, Image.open(os.path.join(src, f"still-{d}.png")).convert("RGBA"))
    return im


def round1(d):
    import json
    im = panel(d)
    meta = json.load(open(os.path.join(ROUND1, "meta.json")))
    for stem, alpha, black in ((f"base-shadow-{d}", 0.5, True), (f"base-{d}", 1.0, False), (f"rotor-{d}", 1.0, False)):
        m = meta[stem]
        lay = Image.open(os.path.join(ROUND1, f"{stem}.png")).convert("RGBA").crop((0, 0, *m["size"]))
        centred(im, lay, (m["shift"][0] * PPT, m["shift"][1] * PPT), alpha=alpha, black=black)
    return im


def vanilla(d):
    im = panel(d)
    for k, (f, w, h, sh) in enumerate(VANILLA[d]):
        lay = Image.open(os.path.join(VAN, f)).convert("RGBA").crop((0, 0, w, h))
        centred(im, lay, sh, alpha=0.5 if k == 0 else 1.0, black=k == 0)
    return im


def adopted(d):
    im = panel(d)
    m = Image.open(MASTER).convert("RGBA")
    k = 5 * PPT / (1415 - 35)                          # the stubs' outer faces span the 5 tiles
    m = m.resize((round(m.width * k), round(m.height * k)), Image.LANCZOS)
    cx, cy = 725 * k, 540 * k                          # the middle collar's centre, the stubs' axis
    if d == "vertical":
        m = m.rotate(90, expand=True)                  # the let-down end (west) to the south
        cx, cy = cy, m.height - cx
    over(im, m, (round(S / 2 - cx), round(S / 2 - cy)))
    return im


def measures(path):
    out = []
    for tool in ("finish.py", "tonal.py"):
        r = subprocess.run([sys.executable, os.path.join(TOOLS, tool), path], capture_output=True, text=True)
        out.append(" ".join(r.stdout.split()[1:]).split("(vanilla")[0])
    return out


def vanilla_measures(d):
    """finish.py and tonal.py on vanilla's frame 0, cut from its sheet into a temporary file."""
    import tempfile
    f, w, h, _ = VANILLA[d][1]
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, f"vanilla-{d}.png")
        Image.open(os.path.join(VAN, f)).convert("RGBA").crop((0, 0, w, h)).save(p)
        return measures(p)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, out = sys.argv[1], sys.argv[2]
    title = sys.argv[sys.argv.index("--title") + 1] if "--title" in sys.argv else "Siderane turbine"
    dirs = [d for d in ("horizontal", "vertical") if os.path.isfile(os.path.join(src, f"still-{d}.png"))]
    LBL, TXT, PAD = 22, 48, 10
    rows = []
    for d in dirs:
        panels = [("adopted master-v2 (plan; camera rejected, spec 12)", adopted(d)),
                  (f"round 1, {d}", round1(d)), (f"round 2, {d}", ours(src, d)),
                  (f"vanilla steam turbine, {d}", vanilla(d))]
        import measure_cover as mc
        cov = {k: mc.measure(im, d)["footprint"] for k, im in
               (("r1", mc.from_sheets(ROUND1, d)), ("r2", mc.ours(src, d)), ("van", mc.vanilla(d)))}
        texts = ["", f"footprint covered {cov['r1']:.0%}",
                 "\n".join(measures(os.path.join(src, f"still-{d}.png")) + [f"footprint covered {cov['r2']:.0%}"]),
                 "\n".join(vanilla_measures(d) + [f"footprint covered {cov['van']:.0%}"])]
        c = S // 2
        h2 = int(3.5 * PPT / 2)
        zoom = [(lbl + " 2x", p.crop((c - h2 // 1, c - h2, c + h2, c + h2)).resize((S, S), Image.NEAREST))
                for lbl, p in panels]
        rows.append((panels, texts))
        rows.append((zoom, ["", "", "", ""]))
    W = 4 * S + 5 * PAD
    H = 40 + len(rows) * (LBL + S + TXT + PAD)
    sheet = Image.new("RGBA", (W, H), (30, 30, 30, 255))
    dr = ImageDraw.Draw(sheet)
    dr.text((PAD, 10), title, fill=(230, 230, 230, 255), font=font(18))
    y = 40
    for panels, texts in rows:
        for i, ((lbl, p), t) in enumerate(zip(panels, texts)):
            x = PAD + i * (S + PAD)
            dr.text((x, y + 4), lbl, fill=(220, 220, 220, 255), font=font(13))
            sheet.paste(p, (x, y + LBL))
            dr.text((x, y + LBL + S + 2), t, fill=(200, 200, 200, 255), font=font(11))
        y += LBL + S + TXT + PAD
    sheet.convert("RGB").save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
