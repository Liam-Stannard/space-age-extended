#!/usr/bin/env python3
"""T15 (gas-pump-3x3): the review sheets for the outlet, from packed sheets, drawn as compose.py draws them.

  python3 sheet.py <out-dir> --before <sheets> --after <sheets> [--alt <sheets> <label>] [--figs <compose.json>]

  phone-outlet.png     2x (64 px a tile), every direction a row: the Gas Pump as shipped (its port pictures), the
                       T15 sheets (no pictures), vanilla's pumpjack and assembling machine 2, each with vanilla's
                       cover (open) and with vanilla's straight pipe (joined); the 3x3 edge in red, vanilla's cover
                       reach (N 22, E 13, S 20, W 12 px) as a cyan tick, the furthest px of the building in the lane
                       as a yellow one
  before-after-4x.png  the connection alone at 4x, every direction a row: shipped and T15, open and joined
                       (and --alt's north, if given)
Engine order (compose.py): shadows; a pipe on a tile north of the centre, or level with it, and the north cover;
the building (a north pipe picture behind it, as secondary_draw_orders north = -1 sets it); the other pictures; a
pipe south of the centre, the south, east and west covers. The assembler's pictures and the pumpjack's sprites are
vanilla's own numbers (assembler-pictures.lua, mining-drill.lua).
"""
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

FD = "/mnt/data/SteamLibrary/steamapps/common/Factorio/data/base/graphics/entity/"
PPT = 64
P = 6 * PPT                      # a panel: six tiles, the entity at its centre
GROUND = (74, 66, 58)
DIRS = ("north", "east", "south", "west")
FACE = {"north": "N", "east": "E", "south": "S", "west": "W"}
VEC = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
COVER = {"N": "north", "E": "east", "S": "south", "W": "west"}
VAN_REACH = {"N": 22, "E": 13, "S": 20, "W": 12}


def font(n):
    for p in ("/usr/share/fonts/TTF/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.isfile(p):
            return ImageFont.truetype(p, n)
    return ImageFont.load_default()


def load(p, crop=None):
    im = Image.open(p).convert("RGBA")
    return im.crop((0, 0) + crop) if crop else im


def solid(im):
    return im.getchannel("A").point(lambda v: 255 if v >= 128 else 0)


class Building:
    """layers: (image, centre x px, centre y px) from the entity centre at 2x; back/front: pictures behind and over."""
    def __init__(self, body, shadow, conn, back=(), front=()):
        self.body, self.shadow, self.conn, self.back, self.front = body, shadow, conn, list(back), list(front)


def gas_pump(sheets, d, pictures=False):
    meta = json.load(open(os.path.join(sheets, "meta.json")))

    def fr(stem):
        m = meta[stem]
        return load(os.path.join(sheets, stem + ".png"), tuple(m["size"])), m["shift"][0] * PPT, m["shift"][1] * PPT
    f = FACE[d]
    tile = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}[f]
    back, front = [], []
    if pictures:
        pm = json.load(open(os.path.join(sheets, "ports", "meta.json")))[f"port-{f}"]
        tgt = (tile[0] + VEC[f][0], tile[1] + VEC[f][1])
        pic = (load(os.path.join(sheets, "ports", f"port-{f}.png")), (tgt[0] + pm["shift"][0]) * PPT,
               (tgt[1] + pm["shift"][1]) * PPT)
        (back if f == "N" else front).append(pic)
    return Building([fr(f"base-{d}"), fr(f"mech-{d}")], [fr(f"shadow-{d}")], (tile, f), back, front)


def pumpjack(d):
    f = FACE[d]
    tile = {"N": (1, -1), "E": (1, 1), "S": (-1, 1), "W": (-1, -1)}[f]
    B = FD + "pumpjack/"
    body = [(load(B + "pumpjack-base.png", (261, 273)), -4.5, -9.5), (load(B + "pumpjack-horsehead.png", (206, 172)), -9, -58)]
    sh = [(load(B + "pumpjack-base-shadow.png", (261, 273)), -4, -10), (load(B + "pumpjack-horsehead-shadow.png", (292, 78)), 35.5, 29)]
    return Building(body, sh, (tile, f))


AM2 = {"N": (0.5, 11.0), "E": (-23.0, 1.5), "S": (0.0, -24.0), "W": (23.0, 0.5)}     # game px (the .lua files)


def assembler2(d):
    f = FACE[d]
    tile = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}[f]
    tgt = (tile[0] + VEC[f][0], tile[1] + VEC[f][1])
    B = FD + "assembling-machine-2/"
    body = [(load(B + "assembling-machine-2-base.png"), 0, 5), (load(B + "assembling-machine-2-anim.png", (148, 158)), 3, -31)]
    sh = [(load(B + "assembling-machine-2-shadow.png"), 91, 1)]
    sx, sy = AM2[f]
    pic = (load(B + f"assembling-machine-2-pipe-{f}.png"), tgt[0] * PPT + sx * 2, tgt[1] * PPT + sy * 2)
    return Building(body, sh, (tile, f), back=[pic] if f == "N" else [], front=[] if f == "N" else [pic])


def put(c, im, cx, cy, half=P // 2):
    c.alpha_composite(im, (round(half + cx - im.width / 2), round(half + cy - im.height / 2)))


def panel(b, mode, size=P):
    """(picture, building alpha, lane reach px of the building) for mode 'cover' or 'pipe'."""
    half = size // 2
    (tile, f) = b.conn
    tgt = (tile[0] + VEC[f][0], tile[1] + VEC[f][1])
    if mode == "pipe":
        van, vsh = load(FD + "pipe/pipe-straight-" + ("vertical" if f in "NS" else "horizontal") + ".png"), None
        before = tgt[1] <= 0
    else:
        van = load(FD + f"pipe-covers/pipe-cover-{COVER[f]}.png")
        vsh = load(FD + f"pipe-covers/pipe-cover-{COVER[f]}-shadow.png")
        before = f == "N"
    acc = Image.new("RGBA", (size, size))
    for im, x, y in b.shadow + ([(vsh, tgt[0] * PPT, tgt[1] * PPT)] if vsh else []):
        L = Image.new("RGBA", (size, size))
        put(L, im, x, y, half)
        acc.putalpha(ImageChops.lighter(acc.getchannel("A"), L.getchannel("A")))
    c = Image.new("RGBA", (size, size), GROUND + (255,))
    shl = Image.new("RGBA", (size, size))
    shl.putalpha(acc.getchannel("A").point(lambda v: v // 2))
    c.alpha_composite(shl)
    own = Image.new("RGBA", (size, size))
    for im, x, y in b.back:
        put(c, im, x, y, half)
        put(own, im, x, y, half)
    if before:
        put(c, van, tgt[0] * PPT, tgt[1] * PPT, half)
    for im, x, y in b.body + b.front:
        put(c, im, x, y, half)
        put(own, im, x, y, half)
    if not before:
        put(c, van, tgt[0] * PPT, tgt[1] * PPT, half)
    return c, own, reach(solid(own), f, tgt, half)


def reach(mask, f, tgt, half):
    a = mask.load()
    e = 1.5 * PPT
    tx, ty = half + tgt[0] * PPT, half + tgt[1] * PPT
    best, W = 0, mask.width
    if f in "NS":
        xs = range(int(tx - 32), int(tx + 32))
        ys = range(0, int(half - e)) if f == "N" else range(int(half + e), W)
    else:
        ys = range(int(ty - 32), int(ty + 32))
        xs = range(int(half + e), W) if f == "E" else range(0, int(half - e))
    for y in ys:
        for x in xs:
            if a[x, y]:
                best = max(best, {"N": (half - e) - y, "S": y + 1 - (half + e), "E": x + 1 - (half + e),
                                  "W": (half - e) - x}[f])
    return int(best)


def decorate(c, b, rch, half=P // 2, grid=True):
    dr = ImageDraw.Draw(c, "RGBA")
    if grid:
        for k in range(-3, 4):
            p = half + (k + 0.5) * PPT
            dr.line([(p, 0), (p, c.height)], fill=(0, 0, 0, 90))
            dr.line([(0, p), (c.width, p)], fill=(0, 0, 0, 90))
    e = 1.5 * PPT
    dr.rectangle([half - e, half - e, half + e - 1, half + e - 1], outline=(255, 60, 60, 230), width=2)
    (tile, f) = b.conn
    tgt = (tile[0] + VEC[f][0], tile[1] + VEC[f][1])
    tx, ty = half + tgt[0] * PPT, half + tgt[1] * PPT
    for lim, col, k in ((VAN_REACH[f], (0, 220, 255, 255), 0), (rch, (255, 220, 0, 255), 1)):
        o = 36 + 8 * k
        if f == "N":
            dr.rectangle([tx + o, half - e - lim, tx + o + 4, half - e], fill=col)
        elif f == "S":
            dr.rectangle([tx + o, half + e, tx + o + 4, half + e + lim], fill=col)
        elif f == "E":
            dr.rectangle([half + e, ty + o, half + e + lim, ty + o + 4], fill=col)
        else:
            dr.rectangle([half - e - lim, ty + o, half - e, ty + o + 4], fill=col)


def phone(out, cols):
    """cols: [(label, fn(d) -> Building)]"""
    F, Fs = font(22), font(20)
    lw, th, cap = 110, 64, 30
    W = lw + len(cols) * 2 * (P + 6)
    H = th + len(DIRS) * (P + cap + 8) + 90
    sheet = Image.new("RGB", (W, H), (18, 18, 18))
    dr = ImageDraw.Draw(sheet)
    for i, (lab, _) in enumerate(cols):
        for j, st in enumerate(("open (vanilla cover)", "joined (vanilla pipe)")):
            x = lw + (2 * i + j) * (P + 6)
            dr.text((x + 4, 8), lab, fill=(255, 255, 255), font=F)
            dr.text((x + 4, 36), st, fill=(190, 190, 190), font=Fs)
    for r, d in enumerate(DIRS):
        y = th + r * (P + cap + 8)
        dr.text((10, y + P // 2 - 12), d, fill=(255, 255, 255), font=F)
        for i, (lab, fn) in enumerate(cols):
            for j, mode in enumerate(("cover", "pipe")):
                b = fn(d)
                c, own, rch = panel(b, mode)
                decorate(c, b, rch)
                x = lw + (2 * i + j) * (P + 6)
                sheet.paste(c.convert("RGB"), (x, y))
                f = b.conn[1]
                col = (255, 220, 0) if rch <= VAN_REACH[f] else (255, 90, 90)
                dr.text((x + 4, y + P + 4), f"past edge {rch} px (cover {VAN_REACH[f]})",
                        fill=col, font=Fs)
    dr.text((10, H - 80), "2x, 64 px a tile, the engine's draw order. Red: the 3x3 footprint. Cyan tick: how far vanilla's cover "
            "reaches past the edge. Yellow tick: the building's own furthest px", fill=(220, 220, 220), font=Fs)
    dr.text((10, H - 52), "in the outlet's lane (its pictures included, shadows not). Pumpjack and assembler 2: vanilla's own "
            "sprites (the assembler with its pipe pictures).", fill=(220, 220, 220), font=Fs)
    sheet.save(out)
    return sheet.size


def zoom(out, rows, k=4, span=2.0):
    """rows: [(label, fn(d) -> Building, dirs)]; each cell the connection's tile and the edge, k x."""
    F, Fs = font(22), font(18)
    cell = int(span * PPT * k)
    lw, th = 250, 60
    W = lw + len(DIRS) * 2 * (cell + 6)
    H = th + len(rows) * (cell + 10) + 40
    sheet = Image.new("RGB", (W, H), (18, 18, 18))
    dr = ImageDraw.Draw(sheet)
    for i, d in enumerate(DIRS):
        for j, st in enumerate(("open", "joined")):
            dr.text((lw + (2 * i + j) * (cell + 6) + 4, 18), f"{d}, {st}", fill=(255, 255, 255), font=F)
    for r, (lab, fn, dirs) in enumerate(rows):
        y = th + r * (cell + 10)
        for n_, line in enumerate(lab.split("\n")):
            dr.text((8, y + cell // 2 - 24 + 26 * n_), line, fill=(255, 255, 255), font=F)
        for i, d in enumerate(DIRS):
            if d not in dirs:
                continue
            for j, mode in enumerate(("cover", "pipe")):
                b = fn(d)
                c, own, rch = panel(b, mode)
                decorate(c, b, rch, grid=False)
                (tile, f) = b.conn
                cx = P // 2 + (tile[0] + 0.5 * VEC[f][0]) * PPT
                cy = P // 2 + (tile[1] + 0.5 * VEC[f][1]) * PPT
                h = span * PPT / 2
                im = c.crop((int(cx - h), int(cy - h), int(cx + h), int(cy + h))).resize((cell, cell), Image.NEAREST)
                sheet.paste(im.convert("RGB"), (lw + (2 * i + j) * (cell + 6), y))
    dr.text((8, H - 32), f"{k}x, the connection's two tiles. Red: the 3x3 edge. Cyan: vanilla's cover reach. Yellow: the "
            "building's own furthest px.", fill=(220, 220, 220), font=Fs)
    sheet.save(out)
    return sheet.size


if __name__ == "__main__":
    out = sys.argv[1]
    a = sys.argv
    before, after = a[a.index("--before") + 1], a[a.index("--after") + 1]
    os.makedirs(out, exist_ok=True)
    cols = [("Gas Pump as shipped", lambda d: gas_pump(before, d, True)),
            ("Gas Pump T15", lambda d: gas_pump(after, d)),
            ("pumpjack", pumpjack), ("assembling machine 2", assembler2)]
    print("phone", phone(os.path.join(out, "phone-outlet.png"), cols))
    rows = [("as shipped\n(port pictures)", lambda d: gas_pump(before, d, True), DIRS),
            ("model-3x3 plate\nno pictures", lambda d: gas_pump(before, d), DIRS),
            ("T15", lambda d: gas_pump(after, d), DIRS)]
    if "--alt" in a:
        alt, lab = a[a.index("--alt") + 1], a[a.index("--alt") + 2]
        rows.append((lab, lambda d: gas_pump(alt, d), ("north",)))
    print("zoom", zoom(os.path.join(out, "before-after-4x.png"), rows))
