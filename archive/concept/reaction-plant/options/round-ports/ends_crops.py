#!/usr/bin/env python3
"""T06i: the run-end crop sheets -- every hose's, pipe's, lagged line's, cable's and bundle's two ends at 4x, each
labelled with what it connects, in all four directions; and a before/after of each end beside T06h's.

  python3 ends_crops.py ends <render-dir> <ports.json> <out-dir>
  python3 ends_crops.py before-after <before-render-dir> <after-render-dir> <ports.json> <out-png> [direction]

<render-dir> holds forms.py --idle's renders (idle-<d>.png, 4x: 256 px a tile, the scale the sprite is
downsampled 4:1 from). <ports.json> is forms.py --ends's (ports-<form>.json): each run end's original point p
(T06h's), the surface point S it now lands on and how far off it the run's end stands (L, along N). A crop is
1.0 tile square round the port (the midpoint of S and the run's end), on the sheets' ground colour. Writes
ends-<d>.png per direction. A picture for Liam's eye, not a measure.
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

DIRS = ("north", "east", "south", "west")
DEG = dict(zip(DIRS, (0, 90, 180, 270)))
K = 256                     # px a tile in the 4x renders
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
HEAD, TEXT, SUB = (240, 200, 120), (240, 220, 170), (200, 194, 182)

# each run (forms.py's name: its unit and its number in it) -> what it is, and what each end lands on
RUNS = {
    "reactor1": ("drive motor's cable bundle", "the motor's north face (gland)", "the reactor's shell (gland)"),
    "legs1": ("loop hose, east leg", "the east leg's cap (nozzle)", "the reactor's shoulder (nozzle)"),
    "legs2": ("loop hose, west leg", "the west leg's cap (nozzle)", "the reactor's shoulder (nozzle)"),
    "gas_line1": ("gas line (crust gas)", "the compressor's discharge stack (adaptor)", "the east leg, gas lift (saddle)"),
    "feed_main1": ("feed main, lagged (solution)", "the feed drum's flank (nozzle)", "the west leg's foot (saddle)"),
    "dosing1": ("dosing hose", "the dosing pump's head (nozzle)", "the west leg (saddle)"),
    "makeup1": ("make-up hose", "the make-up pot's top nozzle (adaptor)", "the east leg (saddle)"),
    "scrubber1": ("scrubber hose", "the scrubber's top nozzle (adaptor)", "the reactor's head (nozzle)"),
    "condenser1": ("condenser vent pipe", "the condenser's wall (nozzle)", "the reactor's shell (nozzle)"),
    "settling1": ("settling hose (downcomer)", "the settling pot's top nozzle (adaptor)", "the west leg (saddle)"),
    "settling2": ("slurry hose", "the settling pot's flank (nozzle)", "the filter press's head (nozzle)"),
    "press1": ("filtrate hose (output)", "the filter press's head (nozzle)", "the receiver's crown (nozzle)"),
    "pumphouse1": ("pump discharge hose", "the pump's outlet (adaptor)", "the housing's roof (nozzle)"),
    "cabinet1": ("cabinet cable", "the cabinet's north face (gland)", "the housing's roof (gland)"),
    "pot1": ("side-nozzle spool", "the reactor's shell (nozzle)", "the side-nozzle pot (nozzle)"),
    "drain1": ("drain header, lagged", "its drain valve (nozzle)", "the settling pot's wall (nozzle)"),
    "instrument_house1": ("instrument house's bundle", "the house's south wall (gland)", "the housing's roof (gland)"),
    "socket1": ("connector cable (north only)", "the terminal box's foot (gland)", "the housing's wall (gland)"),
    "socket2": ("connector cable (east only)", "the terminal box's foot (gland)", "the housing's wall (gland)"),
    "socket3": ("connector cable (south only)", "the terminal box's foot (gland)", "the housing's wall (gland)"),
    "socket4": ("connector cable (west only)", "the terminal box's foot (gland)", "the housing's wall (gland)"),
}
SOCKET_DIR = {"socket1": "north", "socket2": "east", "socket3": "south", "socket4": "west"}


def font(n, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""), n)


def screen(p, d, w, h):
    """Model point -> pixel in a 4x render of the building facing d (the camera's origin at the canvas centre)."""
    x, y, z = p
    a = -math.radians(DEG[d])
    e, n = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
    return w / 2 + e * K, h / 2 - (n + z * 0.5) * K


def plate(rdir, d):
    """The 4x idle plate: forms.py --idle's idle-<d>.png, or render.sh's run-<d>/hi/idle.png under a full-dir."""
    p = os.path.join(rdir, f"idle-{d}.png")
    if not os.path.isfile(p):
        p = os.path.join(rdir, f"run-{d}", "hi", "idle.png")
    im = Image.open(p).convert("RGBA")
    g = Image.new("RGBA", im.size, GROUND)
    g.alpha_composite(im)
    return g


def crop(g, c, d, side=1.0):
    x, y = screen(c, d, *g.size)
    s = side * K / 2
    return g.crop((round(x - s), round(y - s), round(x + s), round(y + s)))


def tag(im, text, sub=None, size=17):
    im = im.convert("RGBA")
    dr = ImageDraw.Draw(im)
    hh = size + 8 + (size + 2 if sub else 0)
    dr.rectangle([0, 0, im.width, hh], fill=(20, 18, 16, 215))
    dr.text((5, 3), text, font=font(size, True), fill=TEXT)
    if sub:
        dr.text((5, size + 6), sub, font=font(size - 3), fill=SUB)
    return im


def grid(ims, cols, gap=8):
    w, h = max(i.width for i in ims), max(i.height for i in ims)
    rows = (len(ims) + cols - 1) // cols
    out = Image.new("RGBA", (cols * w + (cols - 1) * gap, rows * h + (rows - 1) * gap), BG)
    for i, im in enumerate(ims):
        out.alpha_composite(im, ((i % cols) * (w + gap), (i // cols) * (h + gap)))
    return out


def header(width, title, lines, size=30):
    hh = size + 20 + len(lines) * 26
    im = Image.new("RGBA", (width, hh), BG)
    dr = ImageDraw.Draw(im)
    dr.text((14, 10), title, font=font(size, True), fill=HEAD)
    for i, ln in enumerate(lines):
        dr.text((14, size + 18 + 26 * i), ln, font=font(19), fill=SUB)
    return im


def stack(ims, gap=12):
    w = max(i.width for i in ims)
    out = Image.new("RGBA", (w + 24, sum(i.height for i in ims) + gap * (len(ims) + 1)), BG)
    y = gap
    for i in ims:
        out.alpha_composite(i, (12, y))
        y += i.height + gap
    return out


def port_centre(e):
    S, N = e["S"], e["N"]
    L = e["L"]
    return tuple(S[i] + N[i] * L / 2 for i in range(3))


def ends_sheets(rdir, ports, outd):
    P = json.load(open(ports))
    for d in DIRS:
        g = plate(rdir, d)
        tiles = []
        for nm, ends in P.items():
            if nm not in RUNS:
                continue
            if nm in SOCKET_DIR and SOCKET_DIR[nm] != d:
                continue
            what, ta, tb = RUNS[nm]
            for e_, to in (("a", ta), ("b", tb)):
                e = ends.get(e_)
                if not e or e["mode"] == "none":
                    continue
                im = crop(g, port_centre(e), d)
                tiles.append(tag(im, f"{nm}:{e_}  {e['mode']}", None, 15))
                lab = Image.new("RGBA", (im.width, 46), BG)
                dr = ImageDraw.Draw(lab)
                dr.text((4, 2), what, font=font(14, True), fill=TEXT)
                dr.text((4, 22), "-> " + to, font=font(14), fill=SUB)
                t2 = Image.new("RGBA", (im.width, im.height + 46), BG)
                t2.alpha_composite(tiles.pop(), (0, 0))
                t2.alpha_composite(lab, (0, im.height))
                tiles.append(t2)
        body = grid(tiles, 8)
        top = header(body.width, f"T06i: every run end on its port, facing {d} (4x: 256 px a tile, 1.0 tile crops)", [
            "Each crop is centred on the port: the hose's ferrule and nut (or the pipe's flange, the cable's gland) seated on the",
            "port's flange; nozzle = a welded neck on a bolted pad; adaptor = the vessel's own nozzle stepped up to the run's flange",
            "(a visible reducer); saddle = a clamp round the glass leg, strapped on; gland = a brass cable gland on a backing plate.",
            "From forms.py --idle (frame 0, idle: the legs dark). A part in front of an end in this direction hides it here too.",
        ])
        stack([top, body]).convert("RGB").save(os.path.join(outd, f"ends-{d}.png"))
        print("wrote", os.path.join(outd, f"ends-{d}.png"))


def before_after(bdir, adir, ports, out, d="north"):
    P = json.load(open(ports))
    gb, ga = plate(bdir, d), plate(adir, d)
    pairs = []
    for nm, ends in P.items():
        if nm not in RUNS or (nm in SOCKET_DIR and SOCKET_DIR[nm] != d):
            continue
        what, ta, tb = RUNS[nm]
        for e_, to in (("a", ta), ("b", tb)):
            e = ends.get(e_)
            if not e or e["mode"] == "none":
                continue
            b = tag(crop(gb, e["p"], d, 0.8), "T06h", None, 14)
            a = tag(crop(ga, port_centre(e), d, 0.8), "T06i", None, 14)
            w = b.width + a.width + 4
            t = Image.new("RGBA", (w, b.height + 40), BG)
            t.alpha_composite(b, (0, 0))
            t.alpha_composite(a, (b.width + 4, 0))
            dr = ImageDraw.Draw(t)
            dr.text((4, b.height + 2), f"{nm}:{e_}  {what}", font=font(13, True), fill=TEXT)
            dr.text((4, b.height + 20), "-> " + to, font=font(13), fill=SUB)
            pairs.append(t)
    body = grid(pairs, 4, gap=14)
    top = header(body.width, f"T06i before/after: each run end, T06h (left) and T06i (right), facing {d}, 4x", [
        "T06h's crop is centred on the run's old end; T06i's on its port. 0.8 tile crops of forms.py --idle (frame 0).",
    ])
    stack([top, body]).convert("RGB").save(out)
    print("wrote", out)


if __name__ == "__main__":
    if sys.argv[1] == "ends":
        ends_sheets(*sys.argv[2:5])
    elif sys.argv[1] == "before-after":
        before_after(*sys.argv[2:6], *(sys.argv[6:7] or ["north"]))
    else:
        sys.exit(__doc__)
