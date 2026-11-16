#!/usr/bin/env python3
"""T06e: how the four references take a connection into the vessel that uses it -- a study sheet.

  python3 concept/reaction-plant/options/round-layout/study_sheet.py <out.png> [--raw <dir>]

Each reference drawn as the engine draws it (64 px a tile, then 2x), in the directions that show how
its connections meet its vessels, the fluid connections marked where the engine joins a pipe (a ring
on the tile outside the footprint: blue an input, orange an output), and a note on what each
connection lands on. The chemical plant and the oil refinery come from measure.py's own reference
loader (vanilla()); the cryogenic plant, foundry and biochamber, which measure.py does not carry,
are drawn here from their sprites and the prototypes' pipe pictures (a figure measure.py cannot give:
a picture, not a measure). --raw writes each panel alone (for looking, not for the sheet).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import measure  # noqa: E402

FD = measure.FD
PPT = 64
K = 2                                   # the sheet's scale over the engine's 64 px a tile
GROUND = (74, 66, 58, 255)
IN_C, OUT_C = (90, 170, 255), (255, 150, 60)


def font(n, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if bold else "") + ".ttf", n)


def turn(c, k):
    """A connection (x, y, face, kind) turned k quarter turns clockwise (prototype tiles, y down)."""
    x, y, f, kind = c
    for _ in range(k):
        x, y, f = -y, x, "NESW"[("NESW".index(f) + 1) % 4]
    return x, y, f, kind


def sprite(rel, add=(0.0, 0.0)):
    """(image at 64 px a tile, shift px) of a vanilla sprite with a .lua sidecar; add: the prototype's
    own shift option, tiles."""
    im, sx, sy = measure.vanilla_sprite(rel)
    return im, sx + add[0] * PPT, sy + add[1] * PPT


def scene(parts, foot, conns, title, S=None):
    """parts: [(image, sx, sy)] drawn in order, centred on the entity origin; conns: connections as
    the building stands (x, y, face, 'in'|'out'). Returns the 2x panel."""
    fw, fh = foot
    half = max([max(fw, fh) / 2 + 1.6] + [max(abs(sx) + im.width / 2, abs(sy) + im.height / 2) / PPT
                                          for im, sx, sy in parts])
    S = S or int((max(fw, fh) + 3.6) * PPT)      # the same window round every reference of a size
    can = Image.new("RGBA", (S, S), GROUND)
    o = S / 2
    dr = ImageDraw.Draw(can)
    for i in range(-6, 7):
        for a in (o + i * PPT + (PPT / 2 if fw % 2 else 0),):
            dr.line([(a, 0), (a, S)], fill=(84, 76, 68))
        for b in (o + i * PPT + (PPT / 2 if fh % 2 else 0),):
            dr.line([(0, b), (S, b)], fill=(84, 76, 68))
    dr.rectangle([o - fw * PPT / 2, o - fh * PPT / 2, o + fw * PPT / 2, o + fh * PPT / 2], outline=(150, 140, 126))
    for im, sx, sy in parts:
        can.alpha_composite(im, (round(o + sx - im.width / 2), round(o + sy - im.height / 2)))
    can = can.resize((S * K, S * K), Image.LANCZOS)
    dr = ImageDraw.Draw(can)
    for x, y, f, kind in conns:
        dx, dy = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}[f]
        cx, cy = (o + (x + dx * 0.75) * PPT) * K, (o + (y + dy * 0.75) * PPT) * K
        col = IN_C if kind == "in" else OUT_C
        r = 13 * K
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=3 * K)
        # an arrow along the flow: an input points into the building, an output out of it
        s = 1 if kind == "in" else -1
        tip = (cx - dx * s * 22 * K, cy - dy * s * 22 * K)
        dr.line([(cx, cy), tip], fill=col, width=3 * K)
    dr.rectangle([0, 0, can.width, 30 * K // 2 + 8], fill=(30, 28, 26))
    dr.text((8, 6), title, font=font(13 * K // 2 + 4, True), fill=(235, 220, 180))
    return can


def chem_or_refinery(name, conns_n):
    out = []
    for k, d in enumerate(("north", "east", "south", "west")):
        label, foot, still, shadow, light = measure.vanilla(name, d)
        S = still.width
        base = Image.new("RGBA", (S, S))
        base.alpha_composite(shadow)
        base.alpha_composite(still)
        out.append(scene([(base, 0, 0)], foot, [turn(c, k) for c in conns_n], f"{measure.REFS[name]['label']}, {d}"))
    return out


def cryogenic():
    base = "space-age/graphics/entity/cryogenic-plant/cryogenic-plant-"
    main = [sprite(base + "shadow.png"), sprite(base + "main.png")]
    for n in ("anim1-base", "anim2-base", "anim4-base", "anim5-base", "anim6-base"):
        try:
            main.append(sprite(base + n + ".png"))
        except Exception:
            pass
    conns = [(-2, 2, "S", "in"), (0, 2, "S", "in"), (2, 2, "S", "in"), (-2, -2, "N", "out"), (0, -2, "N", "out"),
             (2, -2, "N", "out")]
    out = []
    for k, d in ((0, "north"), (1, "east")):
        cs = [turn(c, k) for c in conns]
        parts = list(main)
        # the pipe picture: one picture holds every connection's pipework on both faces; drawn once,
        # at the entity's centre (its own sidecar shift), it lands on all six
        parts.append(sprite(base + ("pipe-connections-v.png" if k % 2 == 0 else "pipe-connections-h.png")))
        out.append(scene(parts, (5, 5), cs, f"cryogenic plant, {d}"))
    return out


def foundry():
    b = "space-age/graphics/entity/foundry/foundry-"
    conns = [(-1, 2, "S", "in"), (1, 2, "S", "in"), (-1, -2, "N", "out"), (1, -2, "N", "out")]
    out = []
    for k, d in ((0, "north"), (1, "east")):
        parts = [sprite(b + "shadow.png"), sprite(b + "base.png"), measure.vanilla_sprite(b + "anim-1.png:foundry-anim.lua"),
                 sprite(b + f"pipe-connections-{d}.png")]
        out.append(scene(parts, (5, 5), [turn(c, k) for c in conns], f"foundry, {d}"))
    return out


def biochamber():
    b = "space-age/graphics/entity/biochamber/biochamber"
    conns = [(-1, -1, "N", "in"), (1, -1, "N", "in"), (1, 1, "S", "out"), (-1, 1, "S", "out")]
    out = []
    for k, d in ((0, "north"), (1, "east")):
        parts = [sprite(b + "-shadow.png"), sprite(b + ".png")]
        # (its pipe pictures are drawn only where a pipe joins: the plate alone shows what the vessels offer)
        out.append(scene(parts, (3, 3), [turn(c, k) for c in conns], f"biochamber, {d}"))
    return out


NOTES = {      # from looking at the panels (blue ring: an input; orange: an output; the arrow is the flow)
    "chemical": [
        "Chemical plant (3x3, the building turned: four plates)",
        "- Each of the four connections sits on the column of a vessel: two yellow tanks and two round pots stand in the corners, and the",
        "  port is that vessel's own nozzle -- a full-bore flanged stub straight out of its shell, no line run across the plant to it.",
        "- The whole machine turns with its ports (four plates), so a tank is always behind an input and a pot behind an output.",
        "- Inside, the vessels are tied together by lines about half a pipe across; nothing runs from a port past another vessel.",
        "- Its corners are filled by the round vessels themselves: cover 92.4 %, corners 84-95 %.",
    ],
    "refinery": [
        "Oil refinery (5x5, the building turned: four plates)",
        "- The two inputs land on the low pump/tank pair at the front edge (north view: the two squat vessels at the south wall);",
        "  each port is the vessel's nozzle at full bore.",
        "- The three outputs come off the back row: each column's top or a pot beside it meets the north wall on the output's column.",
        "- Flow reads front to back: low feed kit at the inputs, the tall columns in the middle, take-offs at the outputs.",
        "- Facing east and west the same vessels stand on the side walls; nothing is moved, the plate is the building turned.",
    ],
    "cryogenic": [
        "Cryogenic plant (5x5, one body; the engine draws the pipework per face)",
        "- One plate; each face gets its own pipe picture, drawn only at a connection: a short fat elbow or nozzle coming out of",
        "  the vessel nearest that column, so every port still meets a vessel in every direction.",
        "- Its hoses are its process lines (about 0.8 of a pipe): the bore does not drop between port and vessel.",
        "- The vessels are placed so that any face's middle and outer columns have a shell to land on.",
    ],
    "foundry": [
        "Foundry (5x5, one body; per-direction pipework overlays)",
        "- The inputs arrive at the melt basin's rim on the front edge, the outputs leave the tower's foot at the back:",
        "  the overlay for each direction is just the stubs from the wall to that vessel, a few px long.",
        "- Facing east the same overlay is redrawn on the side walls; the body never turns.",
    ],
    "biochamber": [
        "Biochamber (3x3, one body; pipe pictures only where a pipe joins)",
        "- The plate alone already offers a nozzle at each corner column: the dome's hood at the back, the tank ends at the front.",
        "- The engine's pipe picture is an arc from the port into that nozzle, so the port meets the vessel without a visible run.",
        "",
        "What this round takes from them: the vessel that uses a connection stands on that connection's column and owns its",
        "nozzle (a welded collar, full bore, a flange at the wall); the chain inside reads from those vessels to the next; the",
        "building turns as the chemical plant and refinery do, so the same vessel meets its port in every direction; and the",
        "corners hold vessels, which is how the chemical plant reaches 92 % cover.",
    ],
}


def note_block(lines, width):
    f = font(26)
    fb = font(28, True)
    h = 16 + 40 + 34 * len(lines)
    im = Image.new("RGBA", (width, h), (30, 28, 26, 255))
    d = ImageDraw.Draw(im)
    d.text((16, 12), lines[0], font=fb, fill=(240, 210, 140))
    for i, ln in enumerate(lines[1:]):
        d.text((16, 56 + 34 * i), ln, font=f, fill=(220, 214, 200))
    return im


def row(panels, h):
    ps = [p.resize((round(p.width * h / p.height), h), Image.LANCZOS) for p in panels]
    w = sum(p.width for p in ps) + 12 * (len(ps) - 1)
    im = Image.new("RGBA", (w, h), (30, 28, 26, 255))
    x = 0
    for p in ps:
        im.alpha_composite(p, (x, 0))
        x += p.width + 12
    return im


def main():
    out = sys.argv[1]
    raw = sys.argv[sys.argv.index("--raw") + 1] if "--raw" in sys.argv else None
    groups = [
        ("chemical", chem_or_refinery("chemical-plant", [(-1, -1, "N", "in"), (1, -1, "N", "in"), (-1, 1, "S", "out"),
                                                           (1, 1, "S", "out")])),
        ("refinery", chem_or_refinery("oil-refinery", [(-1, 2, "S", "in"), (1, 2, "S", "in"), (-2, -2, "N", "out"),
                                                       (0, -2, "N", "out"), (2, -2, "N", "out")])),
        ("cryogenic", cryogenic()),
        ("foundry", foundry()),
        ("biochamber", biochamber()),
    ]
    if raw:
        os.makedirs(raw, exist_ok=True)
        for g, ps in groups:
            for i, p in enumerate(ps):
                p.save(os.path.join(raw, f"{g}-{i}.png"))
        print("raw panels:", raw)
    if not NOTES:
        return
    W = 3200
    blocks = [note_block(STUDY_HEAD, W)]
    for g, ps in groups:
        h = 760 if len(ps) == 4 else 900
        r = row(ps, h)
        blocks.append(r)
        blocks.append(note_block(NOTES[g], W))
    H = sum(b.height for b in blocks) + 14 * len(blocks)
    sheet = Image.new("RGBA", (W, H), (30, 28, 26, 255))
    y = 0
    for b in blocks:
        sheet.alpha_composite(b, (0, y))
        y += b.height + 14
    if max(sheet.size) >= 8000:
        k = 7990 / max(sheet.size)
        sheet = sheet.resize((round(sheet.width * k), round(sheet.height * k)), Image.LANCZOS)
    sheet.convert("RGB").save(out)
    print(out, sheet.size)


STUDY_HEAD = ["How the references take a connection into the vessel that uses it (T06e study)"]

if __name__ == "__main__":
    main()
