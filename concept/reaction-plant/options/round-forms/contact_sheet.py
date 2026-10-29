#!/usr/bin/env python3
"""T06g: the round's contact sheet -- the three building forms in four directions beside the references and the
signed-off model (T06e's contact_sheet.py).

  python3 contact_sheet.py <scratch> <out.png>

<scratch> holds full-<form>/ for each form (form_sheet.py's input: run-<d>/ and measure-<d>/measures.json). Drawn
at 1.5x of the engine's 64 px a tile, working (precipitation: vanilla pipes joined to the two inputs, the legs
lit), each panel captioned with measure.py's cover and rise for that direction. The references: the chemical
plant and the oil refinery in all four directions (base game's turned plates), the signed-off model's one plate
with the engine's pipe pictures at its three connections (model/sheets, Liam 2026-10-19), and the four-way
model as T06d left it is not repeated here (model/four-way/t06d/contact.png).
"""
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import form_sheet as ts  # noqa: E402
import form_plans as takes  # noqa: E402

SCR, OUT = sys.argv[1], sys.argv[2]
SIGNED = os.path.normpath(os.path.join(HERE, "..", "..", "model", "sheets"))
K = 1.5
DIRS = ts.DIRS


def scaled(im):
    return im.resize((round(im.width * K), round(im.height * K)), Image.LANCZOS)


def cap(im, a, b=None):
    return ts.label(im, a, b, size=20)


def vanilla(stem, foot, shadow=None, extra=(0, 0)):
    import re
    def side(st):
        t = open(st + ".lua").read()
        w = int(re.search(r"width\s*=\s*(\d+)", t).group(1))
        h = int(re.search(r"height\s*=\s*(\d+)", t).group(1))
        sx, sy = map(float, re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", t).groups())
        return w, h, sx * 2, sy * 2
    g, o = ts.panel(1, 6.4, 7.4, 4.0)
    if shadow:
        w, h, sx, sy = side(shadow)
        ts.place(g, Image.open(shadow + ".png").convert("RGBA").crop((0, 0, w, h)), (o[0] + sx + extra[0], o[1] + sy + extra[1]))
    w, h, sx, sy = side(stem)
    ts.place(g, Image.open(stem + ".png").convert("RGBA").crop((0, 0, w, h)), (o[0] + sx + extra[0], o[1] + sy + extra[1]))
    d = ImageDraw.Draw(g)
    hh = foot * 32
    d.rectangle([o[0] - hh, o[1] - hh, o[0] + hh, o[1] + hh], outline=(255, 220, 140, 120))
    return scaled(g)


def signed():
    sh = ts.Sheets(SIGNED)
    pm = json.load(open(os.path.join(SIGNED, "ports", "meta.json")))
    g, o = ts.panel(1, 6.4, 7.4, 4.0)
    conns = ts.CONNS["north"]
    def pics(north):
        for x, y, f in conns:
            if (f == "N") != north:
                continue
            dx, dy = ts.FACE[f]
            cx, cy = o[0] + (x + dx) * 64, o[1] + (y + dy) * 64
            sx, sy = pm[f"port-{f}"]["shift"]
            ts.place(g, ts.sprite(os.path.join(SIGNED, "ports", f"port-{f}.png")), (cx + sx * 64, cy + sy * 64))
    sh.draw(g, o, "shadow", 0, 1)
    pics(True)
    sh.draw(g, o, "base", 0, 1)
    for n in ts.LOOPS:
        if sh.has(n):
            sh.draw(g, o, n, 0, 1)
    sh.draw(g, o, "press", 0, 1)
    sh.draw(g, o, "legs", 0, 1)
    sh.draw(g, o, "legs-glow", 0, 1, add=True)
    pics(False)
    return scaled(g)


def main():
    ENT = ts.ENT
    sec = []
    W = 4 * round(6.4 * 64 * K) + 3 * 16
    sec.append(ts.heading("T06g: three building forms for the Circulator, each connection entering the building's wall", W, 30))
    sec.append(ts.para(["Liam, 2026-10-21: \"it would help if it looked more like a building than some tanks on the ground\"; "
                        "connections \"Should enter the building's wall\"; \"Fittings look wrong\"; \"Raise the sun ~4 %\".",
                        "Connections fixed: inputs north at -1 (solution) and +1 (gas), output south at 0, turning with the "
                        "building. Working, 1.5x, vanilla pipes joined to all three; figures are measure.py's."], W, 20))
    sec.append(ts.heading("The references (turned plates) and the signed-off model", W, 24))
    sec.append(ts.row([cap(vanilla(f"{ENT}/chemical-plant/chemical-plant-{d}-base", 3, extra=(0, -18)),
                           f"chemical plant, {d}") for d in ("north", "east")] +
                      [cap(vanilla(f"{ENT}/oil-refinery/{d}/oil-refinery-{d}", 5,
                                   shadow=f"{ENT}/oil-refinery/{d}/oil-refinery-shadow-{d}"), f"oil refinery, {d}")
                       for d in ("north", "east")]))
    sec.append(ts.row([cap(signed(), "signed off (2026-10-19), north", "one plate; the engine's pictures at the connections")]))
    for key in ("casing", "frame", "rotunda"):
        full = os.path.join(SCR, f"full-{key}")
        if not os.path.isdir(os.path.join(full, "run-west", "sheets")):
            continue
        ts.setup(full, key)
        cells = []
        for d in DIRS:
            sh = ts.Sheets(os.path.join(full, f"run-{d}", "sheets"))
            g, o = ts.panel(1, 6.4, 7.4, 4.0)
            ts.machine(sh, g, o, 1, working=True, conns=ts.CONNS[d])
            mp = os.path.join(full, f"measure-{d}", "measures.json")
            sub = None
            if os.path.isfile(mp):
                dn = json.load(open(mp))["directions"][""]
                c, t = dn["coverage"], dn["tonal"].get("plate", {})
                sub = f"cover {c['footprint_pct']} %, rise {c['rise_tiles']}, p50 {t.get('p50')}"
            cells.append(cap(scaled(g), f"{key}, {d}", sub))
        sec.append(ts.heading(f"Form {ts.FORM_NO[key]}: \"{takes.TAKES[key]['pitch']}\"", W, 24))
        sec.append(ts.row(cells))
    out = ts.stack(sec)
    if max(out.size) >= 8000:
        r = 7990 / max(out.size)
        out = out.resize((round(out.width * r), round(out.height * r)), Image.LANCZOS)
    out.convert("RGB").save(OUT, optimize=True)
    print(OUT, out.size)


if __name__ == "__main__":
    main()
