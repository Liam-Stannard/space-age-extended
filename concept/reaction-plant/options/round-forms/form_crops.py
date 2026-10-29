#!/usr/bin/env python3
"""T06g: per form, two crop sheets at 2x from its packed sheets (as the engine places them, form_sheet.py's compositor).

  python3 form_crops.py <full-dir> <form> <runs.json> <vanilla-dir> <out-dir>

  fittings-<n>-<form>.png  each connection's fitting in every direction (working, vanilla pipes joined), under a row of
                           vanilla's own ports (vanilla_fittings.py: chemical plant, oil refinery, cryogenic plant,
                           foundry), all 2.6 tiles square at 128 px a tile
  clipping-<n>-<form>.png  the clipping check (Liam, 2026-10-21) for his eye: per direction, a crop round each end of
                           every run (hose, pipe, lagged line, cable bundle, riser, fitting neck) and round every point
                           where two runs cross on screen, each labelled with its run; the clips the model's --clash
                           and --collide found on the way, and how each was fixed, listed at the top (CLIPS_FIXED)

<runs.json> is forms.py --clash's (every run's path and ends, model space). A picture, not a measure.
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import form_sheet as fs  # noqa: E402

K = 2
PPT = 64
DIRS = fs.DIRS
WIN = 2.6
CROP = 1.0          # a run-end crop's side, tiles
FACE = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
NAMES = ("solution in", "gas in", "output")

# the clips --clash / --collide found while the forms were built, and the fix (this round's log, 2026-10-21)
CLIPS_FIXED = {
    "all": [
        "the drive motor's cable bundle ran through the reactor's head and top band (the signed-off route): re-routed clear "
        "of both, its gland on the shell above the band",
        "the scrubber's hose to the reactor head dipped into the head before its end: brought in from above, its end clear "
        "of the gearbox and manway",
        "the slurry hose's end collar on the press head reached the leaf pack as it opened: the hose now enters the head's "
        "north face level, clear of the leaves and rails",
        "cable bundles ended bare: each now ends in a brass gland",
    ],
    "casing": [
        "a jbox and two barrels on the roof stood inside the reactor's and the receiver's skirts: moved",
        "the leg's, settling pot's and scrubber's feet met inside the housing: the scrubber moved to the north-west "
        "corner, the settling pot north, the feed drum shortened",
        "the make-up hose grazed the riser leg's glass and its own tank head: its last run now meets the glass square on",
        "the compressor's riser passed through its table: the bottle now stands on legs over the riser (no table)",
        "the instrument house's cable crossed the compressor table: led down the house's south face",
        "condensate beads and drops ran into the roof collar: they now stop on the roof",
        "the dosing hose crossed its own motor: lifted over it",
    ],
    "frame": [
        "the legs' feet met the reactor's foot ring: legs moved out 0.05",
        "the second loop hose dipped into the shell beside the downcomer's cap: it now enters the reactor's shoulder from above",
        "the foot headers ran over the reactor's foot-ring bolts: raised",
        "the girder ring crossed the slurry hose: the ring's south stanchions moved to x +-1.8, y -1.3",
        "the dosing and make-up hoses ran along the drum's shell: the dosing hose now enters its east head, the make-up "
        "hose its crown",
        "the pump-house hose ran through the volute and the cabinet; the filtrate hose along the receiver's crown; the "
        "cabinet's cable down the pump house's face: each re-routed so its last run meets its nozzle square on",
        "a door and a louvre stood where the inputs' necks pass inside the room: removed / moved",
        "a junction box stood in the receiver's flank, a valve on the riser leg's foot: removed / moved",
    ],
    "rotunda": [
        "the reactor's two dials stood inside the rotunda and its roof collar: raised above the roof",
        "the first loop hose crossed the reactor's ladder: the ladder turned to the south-west",
        "the lagged feed main crossed the condenser's vent and ran into the rotunda by the downcomer: re-routed over the "
        "settling pot, its end on the leg's outer side",
        "the gas hose ran through the scrubber: re-routed inside it",
        "the vent pipe met the condensate beads: lowered under them",
        "the settling pot's hose ran through its own head; the cabinet's cable through the cabinet: re-routed",
        "two junction boxes stood on the legs' feet and one under the condenser's drip: moved / removed",
    ],
}


def font(n, bold=False):
    return fs.font(n, bold)


def plate(sh, d, working=True):
    g, origin = fs.panel(K, 8.4, 9.2, 4.8)
    fs.machine(sh, g, origin, K, working=working, conns=fs.CONNS[d] if working else (), lamps=False)
    return g, origin


def crop_conn(g, origin, conn):
    x, y, f = conn
    dx, dy = FACE[f]
    if f in "NS":
        cx, cy = x, dy * 2.5 + dy * 0.2
    else:
        cx, cy = dx * 2.5 + dx * 0.2, y
    S = PPT * K
    box = (origin[0] + (cx - WIN / 2) * S, origin[1] + (cy - WIN / 2) * S,
           origin[0] + (cx + WIN / 2) * S, origin[1] + (cy + WIN / 2) * S)
    return g.crop(tuple(round(v) for v in box))


def tag(im, text, sub=None, size=18):
    im = im.convert("RGBA")
    d = ImageDraw.Draw(im)
    h = size + 10 + (size if sub else 0)
    d.rectangle([0, 0, im.width, h], fill=(20, 18, 16, 210))
    d.text((5, 3), text, font=font(size, True), fill=(240, 220, 170))
    if sub:
        d.text((5, size + 6), sub, font=font(size - 4), fill=(200, 194, 182))
    return im


def grid(ims, cols, gap=8, bg=(30, 29, 28, 255)):
    w, h = max(i.width for i in ims), max(i.height for i in ims)
    rows = (len(ims) + cols - 1) // cols
    out = Image.new("RGBA", (cols * w + (cols - 1) * gap, rows * h + (rows - 1) * gap), bg)
    for i, im in enumerate(ims):
        out.alpha_composite(im, ((i % cols) * (w + gap), (i // cols) * (h + gap)))
    return out


def fittings(SH, key, vdir, outd):
    W = 3 * 333 + 2 * 8
    van = []
    for f_, lab in (("vanilla-chemical-plant-N-1.png", "chemical plant, north input"),
                    ("vanilla-chemical-plant-S-1.png", "chemical plant, south output"),
                    ("vanilla-oil-refinery-S-1.png", "oil refinery, south input"),
                    ("vanilla-cryogenic-plant-S+0.png", "cryogenic plant, south"),
                    ("vanilla-foundry-S-1.png", "foundry, south input"),
                    ("vanilla-foundry-N+1.png", "foundry, north output")):
        van.append(tag(Image.open(os.path.join(vdir, f_)), lab, size=17))
    rows = [fs.heading(f"Form {fs.FORM_NO[key]}, \"{fs.TK['pitch']}\": the fittings, beside vanilla's", W, 28),
            fs.para(["2x, 2.6 tiles square. Vanilla (top two rows): a flanged sleeve, wider than the",
                     "pipe, standing out of the housing's face; the pipe joins its outer flange.",
                     "Ours (a row a direction): in a recess 0.12 deep in the building's wall, a bolted",
                     "square boss, a welded sleeve 1.22 x the bore with a bolted flange at each end,",
                     "the neck at full bore through it; working, vanilla pipes joined. A fitting on",
                     "a wall facing away is behind the building, as vanilla's are."], W, 20),
            grid(van, 3)]
    for d in DIRS:
        g, origin = plate(SH[d], d)
        cs = [tag(crop_conn(g, origin, c), f"facing {d}: {NAMES[i]}", f"tile ({c[0]}, {c[1]}), {c[2]} face", 17)
              for i, c in enumerate(fs.CONNS[d])]
        rows.append(grid(cs, 3))
    out = fs.stack(rows)
    p = os.path.join(outd, f"fittings-{fs.FORM_NO[key]}-{key}.png")
    out.convert("RGB").save(p, optimize=True)
    print(p, out.size)


def seg_x(a, b, c, d):
    """Where screen segments ab and cd cross, or None."""
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = a, b, c, d
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-9:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
    if 0 <= t <= 1 and 0 <= u <= 1:
        return x1 + t * (x2 - x1), y1 + t * (y2 - y1)
    return None


def clipping(SH, key, runs, outd):
    S = PPT * K
    half = CROP * S / 2
    runs = [r for r in runs if r["pts"]]
    for i, r in enumerate(runs):
        r["n"] = i + 1
    secs = []
    total = 0
    for d in DIRS:
        g, origin = plate(SH[d], d)
        deg = fs.DEG[d]
        ims = []
        mine = [r for r in runs if r["dir"] in (None, d)]
        scr = {r["n"]: [fs.screen(p, deg, origin, K) for p in r["pts"]] for r in mine}
        for r in mine:
            for j, e in enumerate(r["ends"]):
                x, y = fs.screen(e, deg, origin, K)
                ims.append(tag(g.crop((round(x - half), round(y - half), round(x + half), round(y + half))),
                               f"{r['n']}{'ab'[j]} {r['kind']}", size=14))
        seen = []
        for a in mine:
            for b in mine:
                if b["n"] <= a["n"]:
                    continue
                for p1, p2 in zip(scr[a["n"]], scr[a["n"]][1:]):
                    for q1, q2 in zip(scr[b["n"]], scr[b["n"]][1:]):
                        c = seg_x(p1, p2, q1, q2)
                        if c and all(math.dist(c, s_) > half * 0.8 for s_ in seen):
                            seen.append(c)
                            ims.append(tag(g.crop((round(c[0] - half), round(c[1] - half), round(c[0] + half),
                                                   round(c[1] + half))), f"{a['n']} x {b['n']}", size=14))
        total += len(ims)
        secs += [fs.heading(f"facing {d}: {len(mine)} runs, each end (a, b) and every crossing on screen", 16 * 136, 24),
                 grid(ims, 16)]
    W = 16 * 136
    legend = []
    line = ""
    for r in runs:
        e0, e1 = r["ends"]
        item = f"{r['n']} {r['kind']}{' (' + r['dir'] + ')' if r['dir'] else ''} ({e0[0]:+.1f},{e0[1]:+.1f})-({e1[0]:+.1f},{e1[1]:+.1f})"
        if len(line) + len(item) > 190:
            legend.append(line)
            line = ""
        line += item + ";  "
    legend.append(line)
    clips = sum(len(r.get("clips", [])) for r in runs)
    head = [fs.heading(f"Form {fs.FORM_NO[key]}, \"{fs.TK['pitch']}\": the clipping check (2x, working; every crop "
                       f"{CROP:.1f} tile square)", W, 30),
            fs.para([f"forms.py --clash now: {clips} run clips, 0 below ground; --collide: 0 clashes (fixed and moving parts). "
                     "By eye: look for a run passing through a part, or an end not on a fastened nozzle or gland.",
                     "Clips found on the way and fixed:"] +
                    ["  - " + t for t in CLIPS_FIXED["all"] + CLIPS_FIXED.get(key, [])], W, 20),
            fs.para(["Runs (model space, tiles, the building facing north): "] + legend, W, 16)]
    out = fs.stack(head + secs)
    if max(out.size) >= 8000:
        r_ = 7990 / max(out.size)
        out = out.resize((round(out.width * r_), round(out.height * r_)), Image.LANCZOS)
    p = os.path.join(outd, f"clipping-{fs.FORM_NO[key]}-{key}.png")
    out.convert("RGB").save(p, optimize=True)
    print(p, out.size, total, "crops")


if __name__ == "__main__":
    full, key, runs_p, vdir, outd = sys.argv[1:6]
    fs.setup(full, key, outd)
    SH = {d: fs.Sheets(os.path.join(full, f"run-{d}", "sheets")) for d in DIRS}
    fittings(SH, key, vdir, outd)
    clipping(SH, key, json.load(open(runs_p)), outd)
