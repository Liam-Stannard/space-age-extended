#!/usr/bin/env python3
"""Vent Pump model (T07e): the wall fittings at its two connections, and the circuit connector's mount.

  python3 -B review_t07e.py --new <render.sh out-dir> --old <a dir with sheets/ (T07d's, as wired in b0df5b6)>
        --out <dir> [--options <name>=<render.sh out-dir> ...] [--only-crops]

Liam's rule (2026-10-21): "Each connection enters the building through a fitting set into its wall or casing (a
recessed boss with a sleeve and flanges, as on the Reaction Plant's casing, or similar), never a stub standing off
the machine; the pipe picture shows it open, and vanilla's cover is drawn when nothing is connected." And on the
wire post (T09b): "Add a point to mount it to".

Writes into --out (each page under 8000 px a side):
  review-t07e-fittings.png   per direction and connection (output and input), 4x: old (as wired: T07d's stub and
                             pipe picture) connected and unconnected, new connected (our picture + a vanilla
                             straight pipe on the next tile) and unconnected (our picture + vanilla's cover)
  review-t07e-mount.png      the control house per direction, 4x, old (T09b's offsets) and new (the bracket, at the
                             run's model.json post_offsets): the model alone, and with vanilla's wire post
                             (universal connector, variation 26: base, pins, LED off, shadow) drawn at the offset
  review-t07e-directions.png the four directions whole, 2x, old beside new, both connections joined, the post on

Composed from the packed sheets as measure.py composes them: each sheet at its shift, the shadow at half
strength under the plate, the mech layer's frame 0 over it; a north pipe picture under the building
(secondary_draw_orders north = -1), the others over it; vanilla's pipe or cover on the tile outside. The cover
and the pipe are vanilla's hr sheets at their own size (64 px a tile, as ours). Unchecked in a client.
"""
import argparse
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("--new", required=True)
ap.add_argument("--old", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--options", nargs="*", default=[])
A = ap.parse_args()
os.makedirs(A.out, exist_ok=True)

DIRS = ("north", "east", "south", "west")
CANVAS = 416
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
HEAD, TXT = (240, 200, 120), (220, 214, 204)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "tools"))
import paths  # noqa: E402   tools/paths.py: where Factorio is
FD = os.path.join(paths.factorio_data(), "base/graphics/entity")
# the connections as each direction turns them: (output face, input face)
CONN = {"north": ("N", "S"), "east": ("E", "W"), "south": ("S", "N"), "west": ("W", "E")}
INTO = {"N": (0, -2), "E": (2, 0), "S": (0, 2), "W": (-2, 0)}
COVER = {"N": "north", "E": "east", "S": "south", "W": "west"}
# T09b's wire post, per direction (prototypes/core/entities.lua, vp_post): main_offset, tiles; the new run's from its
# model.json ("post_offsets", vent_pump.py's post_offset())
POST = {"north": (1.0, -1.07), "east": (0.95, 0.70), "south": (-1.22, 0.43), "west": (-1.12, 0.62)}
CC = os.path.join(FD, "circuit-connector")
# universal_connector_template (core/lualib/circuit-connector-generated-definitions.lua), variation 26: each sheet's
# frame size, its shift (hr px: by_pixel x 2) and whether it is a shadow
CC_SHEETS = (("ccm-universal-04b-base-shadow-sequence.png", (60, 46), (5, 5), True),
             ("ccm-universal-04a-base-sequence.png", (52, 50), (0, 2), False),
             ("ccm-universal-04c-wire-sequence.png", (62, 58), (0, 2), False),
             ("ccm-universal-04f-blue-LED-off-sequence.png", (46, 44), (0, 0), False))


def font(n, b=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if b else "") + ".ttf", n)


F_H, F_S = font(22, True), font(15)


class Run:
    def __init__(self, d):
        self.sheets = os.path.join(d, "sheets")
        self.meta = json.load(open(os.path.join(self.sheets, "meta.json")))
        self.pmeta = json.load(open(os.path.join(self.sheets, "ports", "meta.json")))
        self.cache = {}

    def img(self, path):
        if path not in self.cache:
            self.cache[path] = Image.open(path).convert("RGBA")
        return self.cache[path]

    def layer(self, name, f=0):
        m = self.meta[name]
        w, h = m["size"]
        im = self.img(os.path.join(self.sheets, name + ".png"))
        if "frames" in m:
            ll = m.get("line_length", m["frames"])
            im = im.crop(((f % ll) * w, (f // ll) * h, (f % ll) * w + w, (f // ll) * h + h))
        out = Image.new("RGBA", (CANVAS, CANVAS))
        out.alpha_composite(im, (round(CANVAS / 2 + m["shift"][0] * 64 - w / 2),
                                 round(CANVAS / 2 + m["shift"][1] * 64 - h / 2)))
        return out

    def port(self, face):
        pm = self.pmeta[f"port-{face}"]
        return at_tile(self.img(os.path.join(self.sheets, "ports", f"port-{face}.png")), INTO[face], pm["shift"])


def at_tile(im, tile, shift=(0, 0), half=False):
    if half:
        im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
    out = Image.new("RGBA", (CANVAS, CANVAS))
    out.alpha_composite(im, (round(CANVAS / 2 + (tile[0] + shift[0]) * 64 - im.width / 2),
                             round(CANVAS / 2 + (tile[1] + shift[1]) * 64 - im.height / 2)))
    return out


def half_shadow(im):
    a = im.getchannel("A").point(lambda v: v // 2)
    return Image.merge("RGBA", (*Image.new("RGB", im.size).split(), a))


def scene(run, d, joined):
    """Direction d as the engine draws it; `joined`: face -> "pipe" | "cover"."""
    out = Image.new("RGBA", (CANVAS, CANVAS), GROUND)
    for face, how in joined.items():
        if how == "cover":
            out.alpha_composite(half_shadow(at_tile(Image.open(os.path.join(FD, "pipe-covers",
                                f"pipe-cover-{COVER[face]}-shadow.png")).convert("RGBA"), INTO[face])))
    out.alpha_composite(half_shadow(run.layer(f"shadow-{d}")))
    building = Image.new("RGBA", (CANVAS, CANVAS))
    for face in joined:
        if face == "N":
            building.alpha_composite(run.port(face))       # drawn behind the building
    building.alpha_composite(run.layer(f"base-{d}"))
    building.alpha_composite(run.layer(f"mech-{d}", 0))
    for face in joined:
        if face != "N":
            building.alpha_composite(run.port(face))
    behind, front = [], []
    for face, how in joined.items():
        if how == "pipe":
            p = at_tile(Image.open(os.path.join(FD, "pipe", "pipe-straight-" + ("vertical" if face in "NS" else
                                                                                 "horizontal") + ".png")).convert("RGBA"),
                        INTO[face])
            (front if INTO[face][1] > 0 else behind).append(p)
        else:      # a north cover behind the building, as the north picture (secondary_draw_orders north = -1)
            (behind if face == "N" else front).append(at_tile(Image.open(os.path.join(
                FD, "pipe-covers", f"pipe-cover-{COVER[face]}.png")).convert("RGBA"), INTO[face]))
    for p in behind:
        out.alpha_composite(p)
    out.alpha_composite(building)
    for p in front:
        out.alpha_composite(p)
    return out


def with_post(im, off, var=26):
    """The wire post drawn over the scene at main_offset `off` (shadow at half strength first)."""
    out = im.copy()
    for name, (w, h), sh, shadow in CC_SHEETS:
        sheet = Image.open(os.path.join(CC, name)).convert("RGBA")
        fr = sheet.crop(((var % 8) * w, (var // 8) * h, (var % 8) * w + w, (var // 8) * h + h))
        if shadow:
            fr = half_shadow(fr)
        lay = Image.new("RGBA", im.size)
        lay.alpha_composite(fr, (round(CANVAS / 2 + off[0] * 64 + sh[0] - w / 2), round(CANVAS / 2 + off[1] * 64 + sh[1] - h / 2)))
        out.alpha_composite(lay)
    return out


def crop_at(im, c, half=48, k=4):
    box = (round(c[0] - half), round(c[1] - half), round(c[0] + half), round(c[1] + half))
    return im.crop(box).resize((2 * half * k, 2 * half * k), Image.NEAREST)


def conn_centre(face):
    t = INTO[face]
    return CANVAS / 2 + t[0] * 0.75 * 64, CANVAS / 2 + t[1] * 0.75 * 64 - (10 if face in "NS" else 6)


def captioned(im, title, w=None):
    w = w or im.width
    out = Image.new("RGBA", (w, im.height + 30), BG)
    ImageDraw.Draw(out).text((4, 6), title, font=F_S, fill=TXT)
    out.alpha_composite(im, (0, 30))
    return out


def row(panels, gap=12):
    w = sum(p.width for p in panels) + gap * (len(panels) - 1)
    h = max(p.height for p in panels)
    out = Image.new("RGBA", (w, h), BG)
    x = 0
    for p in panels:
        out.alpha_composite(p, (x, 0))
        x += p.width + gap
    return out


def stack(blocks, title, gap=18, pad=20):
    w = max(b.width for b in blocks) + 2 * pad
    h = sum(b.height for b in blocks) + gap * (len(blocks) - 1) + 2 * pad + 40
    out = Image.new("RGBA", (w, h), BG)
    ImageDraw.Draw(out).text((pad, pad), title, font=F_H, fill=HEAD)
    y = pad + 40
    for b in blocks:
        out.alpha_composite(b, (pad, y))
        y += b.height + gap
    assert max(out.size) < 8000, out.size
    return out


def headed(im, title):
    out = Image.new("RGBA", (im.width, im.height + 32), BG)
    ImageDraw.Draw(out).text((0, 4), title, font=font(17, True), fill=HEAD)
    out.alpha_composite(im, (0, 32))
    return out


OLD, NEW = Run(A.old), Run(A.new)
OPTS = [(n, Run(p)) for n, p in (o.split("=", 1) for o in A.options)]

# ---------------------------------------------------------------- the fittings
blocks = []
for d in DIRS:
    for which, face in zip(("output (melt)", "input (helium)"), CONN[d]):
        other = [f for f in CONN[d] if f != face][0]
        panels = []
        cols = [("old", OLD)] + ([("new", NEW)] if not OPTS else OPTS)
        for name, run in cols:
            for how in ("pipe", "cover"):
                im = scene(run, d, {face: how, other: "pipe"})
                panels.append(captioned(crop_at(im, conn_centre(face)),
                                        f"{name}: {'connected' if how == 'pipe' else 'unconnected, vanilla cover'}"))
        blocks.append(headed(row(panels), f"{d.upper()}: {which}, {face} face, 4x"))
half = (len(blocks) + 1) // 2
for i, part in enumerate((blocks[:half], blocks[half:])):
    stack(part, "T07e: the connections' wall fittings, 4x" + (" (north, east)" if i == 0 else " (south, west)")) \
        .convert("RGB").save(os.path.join(A.out, f"review-t07e-fittings-{i + 1}.png"))

# ---------------------------------------------------------------- the wire post's mount
NEW_POST = {d: tuple(v) for d, v in json.load(open(os.path.join(A.new, "model.json")))["post_offsets"].items()} \
    if os.path.exists(os.path.join(A.new, "model.json")) else POST
mblocks = []
for d in DIRS:
    panels = []
    for name, run, off in (("old (T09b)", OLD, POST[d]), ("new (T07e)", NEW, NEW_POST[d])):
        im = scene(run, d, {f: "pipe" for f in CONN[d]})
        x, y = CANVAS / 2 + off[0] * 64, CANVAS / 2 + off[1] * 64
        c = (x + 5, y + 8)
        bare = crop_at(im, c, half=40)
        post = crop_at(with_post(im, off), c, half=40)
        panels += [captioned(bare, f"{name}: the model"), captioned(post, f"{name}: post at ({off[0]}, {off[1]})")]
    mblocks.append(headed(row(panels), f"{d.upper()}: the wire post, 4x"))
stack(mblocks, "T07e: the wire post's mount, 4x").convert("RGB").save(os.path.join(A.out, "review-t07e-mount.png"))

# ---------------------------------------------------------------- the four directions whole
dpanels = []
for d in DIRS:
    pr = []
    for name, run, off in (("old", OLD, POST[d]), ("new", NEW, NEW_POST[d])):
        im = with_post(scene(run, d, {f: "pipe" for f in CONN[d]}), off).crop((16, 16, CANVAS - 16, CANVAS - 16))
        pr.append(captioned(im.resize((im.width * 2, im.height * 2), Image.NEAREST), f"{d}: {name}"))
    dpanels.append(row(pr))
stack(dpanels, "T07e: the four directions, 2x, both connections joined").convert("RGB") \
    .save(os.path.join(A.out, "review-t07e-directions.png"))

# ---------------------------------------------------------------- the runs into the fittings: their ends, 4x
# the clipping check by eye: where the helium line and the downcomer meet the casings' backs (model.json "pipes",
# each end's screen point; "ok": the end lies in what it serves)
if os.path.exists(os.path.join(A.new, "model.json")):
    pipes = json.load(open(os.path.join(A.new, "model.json")))["pipes"]
    eblocks = []
    for d in DIRS:
        im = scene(NEW, d, {f: "pipe" for f in CONN[d]})
        pr = []
        for p in pipes:
            if p["direction"] != d or not ("inlet fitting" in p["name"] or "downcomer" in p["name"]):
                continue
            e = p["ends"][0] if "inlet fitting" in p["name"] else p["ends"][-1]
            sx, sy = e["screen"]
            pr.append(captioned(crop_at(im, (CANVAS / 2 + sx * 64, CANVAS / 2 + sy * 64), 32, 4),
                                f"{p['name'].split(':')[0]}: into the {e['to']} casing"
                                f"{'' if e['ok'] else ' (NOT in it)'}"))
        eblocks.append(headed(row(pr), f"{d.upper()}: the runs' ends at the fittings, 4x"))
    stack(eblocks, "T07e: clipping, the runs into the casings").convert("RGB") \
        .save(os.path.join(A.out, "review-t07e-ends.png"))

# ---------------------------------------------------------------- the phone-sized top section (1080 px wide)
F_T = font(14)
tops = []
for d in DIRS:
    out_f, in_f = CONN[d]
    joined = scene(NEW, d, {out_f: "pipe", in_f: "pipe"})
    capped = scene(NEW, d, {out_f: "pipe", in_f: "cover"})
    off = NEW_POST[d]
    c = (CANVAS / 2 + off[0] * 64 + 5, CANVAS / 2 + off[1] * 64 + 8)
    cells = [(crop_at(joined, conn_centre(out_f), 40, 3), "out, joined"),
             (crop_at(joined, conn_centre(in_f), 40, 3), "in, joined"),
             (crop_at(capped, conn_centre(in_f), 40, 3), "in, vanilla cover"),
             (crop_at(with_post(joined, off), c, 40, 3), "wire post on its bracket")]
    pr = []
    for im, t in cells:
        cap = Image.new("RGBA", (im.width, im.height + 22), BG)
        ImageDraw.Draw(cap).text((3, 3), t, font=F_T, fill=TXT)
        cap.alpha_composite(im, (0, 22))
        pr.append(cap)
    tops.append(headed(row(pr, gap=8), f"{d}"))
top = stack(tops, "Vent Pump T07e: wall fittings + post bracket, 3x", gap=10, pad=12)
top.convert("RGB").save(os.path.join(A.out, "review-t07e-top.png"))
print("done")
