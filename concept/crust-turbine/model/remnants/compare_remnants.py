#!/usr/bin/env python3
"""The Siderane turbine's wreck beside vanilla's steam-turbine-remnants, at 1x and 2x, on the Core's ground and
on vanilla's.

  python3 compare_remnants.py <render.sh out-dir> <compare.png> [--previous <sheets dir> <label>]

Reads <out-dir>/sheets (remnants.png and meta.json, as pack.py packed them) and <out-dir>/renders (the intact
machine: still-<direction>.png and shadow-<direction>.png). One row per direction and ground, every panel on
that ground at 64 px a tile (the sprites' own scale: vanilla's remnants are scale 0.5 at 64 px a tile, as ours
are) with the footprint's grid:

  intact    ours, the stopped machine: its shadow at 50 %, then the still -- for reference
  wreck     ours: the remnants sheet's row for the direction, at its shift, as the corpse draws it
  previous  with --previous: an earlier round's wreck (its remnants.png and meta.json), for the change
  vanilla   steam-turbine-remnants, its row for the direction (north for vertical, east for horizontal), at its
            shift (util.by_pixel(6, 0): 12 px), remnants.lua:2739-2765
  2x        the wreck and vanilla's, the middle 3.5 x 3.5 tiles, doubled (nearest)

Grounds: the Core's -- Alien Biomes' mineral-white-dirt-1 and mineral-black-dirt-1 (prototypes/core/map-gen.lua's
palette), read from the mod's zip in ~/.factorio/mods -- and vanilla's dirt-1. Each is laid from its sheet's
4 x 4-tile variants. Under each wreck: pack.py's own remnants figures (wreck_parts, reach), computed the same way
for vanilla's, and tonal.py's and finish.py's on the wreck's solid pixels.
"""
import io
import os
import random
import subprocess
import sys
import tempfile
import zipfile
import json

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
TOOLS = os.path.join(REPO, "tools", "blender")
sys.path.insert(0, TOOLS)
import pack  # noqa: E402

FD = os.environ.get("FACTORIO_DATA", os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
VAN = os.path.join(FD, "base/graphics/entity/steam-turbine/remnants/steam-turbine-remnants.png")
VAN_ROW = {"vertical": 0, "horizontal": 1}                 # north, east
VAN_FRAME = (460, 408)
VAN_SHIFT = (12, 0)                                        # util.by_pixel(6, 0) at scale 0.5: px at 64 a tile
AB_ZIP = os.path.expanduser("~/.factorio/mods/alien-biomes-graphics_0.8.0.zip")
AB_DIR = "alien-biomes-graphics_0.8.0/graphics/terrain/"
GROUNDS = [("Core: mineral-white-dirt-1", ("ab", "mineral-white-dirt-1.png")),
           ("Core: mineral-black-dirt-1", ("ab", "mineral-black-dirt-1.png")),
           ("vanilla: dirt-1", ("base", "dirt-1.png"))]
PPT = 64
S = 448                                                    # a 1x panel, 7 tiles; the origin at its centre
FOOT = {"vertical": (3, 5), "horizontal": (5, 3)}


def font(n):
    try:
        return ImageFont.load_default(n)
    except TypeError:
        return ImageFont.load_default()


def tile_sheet(src):
    kind, name = src
    if kind == "ab":
        with zipfile.ZipFile(AB_ZIP) as z:
            return Image.open(io.BytesIO(z.read(AB_DIR + name))).convert("RGBA")
    return Image.open(os.path.join(FD, "base/graphics/terrain", name)).convert("RGBA")


def ground(sheet, seed):
    """A panel of ground from the sheet's 4 x 4-tile variants (the bottom 256 px row, 16 of them)."""
    rng = random.Random(seed)
    im = Image.new("RGBA", (S, S))
    for y in range(0, S, 256):
        for x in range(0, S, 256):
            v = rng.randrange(sheet.width // 256)
            im.paste(sheet.crop((v * 256, sheet.height - 256, v * 256 + 256, sheet.height)), (x - 32, y - 32))
    return im


def grid(im, d):
    dr = ImageDraw.Draw(im)
    c = S // 2
    w, h = FOOT[d]
    for k in range(-4, 5):
        dr.line([(c + k * PPT - (w % 2) * 32, 0), (c + k * PPT - (w % 2) * 32, S)], fill=(255, 255, 255, 22))
        dr.line([(0, c + k * PPT - (h % 2) * 32), (S, c + k * PPT - (h % 2) * 32)], fill=(255, 255, 255, 22))
    dr.rectangle([c - w * PPT / 2, c - h * PPT / 2, c + w * PPT / 2, c + h * PPT / 2], outline=(255, 255, 255, 120))


def placed(layer, shift_px, size=S):
    """layer centred on the origin of a size x size canvas, moved by shift_px."""
    out = Image.new("RGBA", (size, size))
    out.paste(layer, (round(size / 2 - layer.width / 2 + shift_px[0]), round(size / 2 - layer.height / 2 + shift_px[1])))
    return out


def ours_wreck(sheets, d):
    meta = json.load(open(os.path.join(sheets, "meta.json")))["remnants"]
    w, h = meta["size"]
    row = meta["rows"].index(d)
    lay = Image.open(os.path.join(sheets, "remnants.png")).convert("RGBA").crop((0, row * h, w, row * h + h))
    return lay, (meta["shift"][0] * PPT, meta["shift"][1] * PPT)


def vanilla_wreck(d):
    w, h = VAN_FRAME
    r = VAN_ROW[d]
    return Image.open(VAN).convert("RGBA").crop((0, r * h, w, r * h + h)), VAN_SHIFT


def intact(renders, d):
    im = Image.new("RGBA", (S, S))
    sh = Image.open(os.path.join(renders, f"shadow-{d}.png")).convert("RGBA")
    a = sh.getchannel("A").point(lambda v: v // 2)
    black = Image.new("RGBA", sh.size, (0, 0, 0, 255))
    black.putalpha(a)
    im.alpha_composite(placed(black, (0, 0)))
    im.alpha_composite(placed(Image.open(os.path.join(renders, f"still-{d}.png")).convert("RGBA"), (0, 0)))
    return im


def figures(lay, shift, d):
    """pack.py's remnants figures on a wreck as drawn (cleaned as pack.py cleans one), on a 9-tile canvas."""
    im = pack.clean(placed(lay, shift, 576))
    sh, de = pack.wreck_parts(im)
    n = sh.histogram()[255]
    area = im.getchannel("A").point(lambda v: 255 if v else 0).histogram()[255]
    decl = {"footprint": [3, 5], "directions": "horizontal-vertical", "rig": {"px_per_tile": PPT}}
    return dict(shadow_px=n, share=round(n / area, 3),
                debris=pack.reach(de.getbbox(), decl, d, im.size),
                all=pack.reach(im.getchannel("A").getbbox(), decl, d, im.size))


def look(lay):
    """tonal.py and finish.py on the wreck's own pixels."""
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "wreck.png")
        lay.save(p)
        for tool in ("tonal.py", "finish.py"):
            r = subprocess.run([sys.executable, os.path.join(TOOLS, tool), p], capture_output=True, text=True)
            out.append(" ".join(r.stdout.split()[1:]).split("(vanilla")[0])
    return out


def fmt(f):
    r = lambda m: " ".join(f"{k}{v:+.2f}" for k, v in m.items())
    return [f"shadow {f['shadow_px']} px, {100 * f['share']:.1f} % of the wreck",
            f"debris past edge: {r(f['debris'])}", f"all past edge:    {r(f['all'])}"]


def main():
    args = sys.argv[1:]
    prev = None
    if "--previous" in args:
        i = args.index("--previous")
        prev = (args[i + 1], args[i + 2])
        del args[i:i + 3]
    if len(args) != 2:
        sys.exit(__doc__)
    src, out = args
    sheets, renders = os.path.join(src, "sheets"), os.path.join(src, "renders")
    LBL, TXT, PAD = 20, 96, 10
    rows = []
    for d in ("vertical", "horizontal"):
        ow, osh = ours_wreck(sheets, d)
        vw, vsh = vanilla_wreck(d)
        wrecks = [("Siderane turbine wreck", ow, osh)]
        if prev:
            pw, psh = ours_wreck(prev[0], d)
            wrecks.append((f"wreck, {prev[1]}", pw, psh))
        wrecks.append(("vanilla steam-turbine-remnants", vw, vsh))
        texts = ["\n".join(fmt(figures(w_, s_, d)) + look(w_)) for _, w_, s_ in wrecks]
        for gi, (gname, gsrc) in enumerate(GROUNDS):
            g = ground(tile_sheet(gsrc), 7 + gi)
            panels = []
            for lbl, layer in [("Siderane turbine, intact", intact(renders, d))] + \
                    [(n_, placed(w_, s_)) for n_, w_, s_ in wrecks]:
                p = g.copy()
                p.alpha_composite(layer)
                grid(p, d)
                panels.append((f"{lbl}, {d}, 1x", p))
            c, h2 = S // 2, int(3.5 * PPT / 2)
            for lbl, p in (panels[1], panels[-1]):
                panels.append((lbl.replace(", 1x", ", 2x"),
                               p.crop((c - h2, c - h2, c + h2, c + h2)).resize((S, S), Image.NEAREST)))
            rows.append((f"{d} on {gname}", panels, ([""] + texts + ["", ""]) if gi == 0 else [""] * len(panels)))
    n = len(rows[0][1])
    W = n * S + (n + 1) * PAD
    H = 40 + sum(LBL * 2 + S + (TXT if any(t for t in tx) else 0) + PAD for _, _, tx in rows)
    sheet = Image.new("RGBA", (W, H), (30, 30, 30, 255))
    dr = ImageDraw.Draw(sheet)
    dr.text((PAD, 10), "Siderane turbine wreck (remnants pass) beside vanilla's steam-turbine-remnants: 64 px a tile; "
            "white box = footprint", fill=(230, 230, 230, 255), font=font(18))
    y = 40
    for title, panels, texts in rows:
        dr.text((PAD, y + 2), title, fill=(240, 220, 160, 255), font=font(15))
        y += LBL
        for i, ((lbl, p), t) in enumerate(zip(panels, texts)):
            x = PAD + i * (S + PAD)
            dr.text((x, y + 3), lbl, fill=(220, 220, 220, 255), font=font(13))
            sheet.paste(p, (x, y + LBL))
            if t:
                dr.text((x, y + LBL + S + 3), t, fill=(200, 200, 200, 255), font=font(12))
        y += LBL + S + (TXT if any(texts) else 0) + PAD
    sheet.convert("RGB").save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
