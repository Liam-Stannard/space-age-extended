#!/usr/bin/env python3
"""Review sheet for the radiant icons in look B, beside the signed-off icons and the study's pieces.

  python3 icon_sheet.py <pieces-dir> <out.png>

Reads (repo-relative to this worktree):
  concept/items/radiant/strips/<item>.png         the signed-off icons ("now")
  concept/items/radiant/measures.json             their measures (review_sheet.py)
  concept/items/radiant/look-b/strips/radiant/    the look-B icons (radiant_icons_b.py)
  concept/items/radiant/look-b/measures.json      their measures (review_sheet.py, the icon
                                                  pipeline's own: framing, tonal, outline
                                                  contrast on slot and ground at 64 and 16 px,
                                                  strays, pairwise distinctness at 16 and 8)
<pieces-dir>: the radiant-look study's look_pieces.py --look B --only one renders (idle,
work-00, glow-00 at 4x), composed day and night as the study does.

Adds the study's light measures per icon at 64 px (opaque pixels): the blue share (B > 110,
B > R + 45, B > G + 10), mean L and saturation of the blue pixels, pale (blue-hued, sat <
0.45, L > 150: a pale-cyan top), white (all channels >= 245), and the brightest blue's hue.
"""
import colorsys
import json
import os
import sys

from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from pool_sheet import Sheet, darken, down, light_of  # noqa: E402

ITEMS = ["radiant-chunk", "radiant-fuel", "sae-spent-cell", "radiant-solution"]
SIZES, OFFS = (64, 32, 16, 8), (0, 64, 96, 112)
SLOT = (45, 44, 45)
GROUND = (74, 66, 58)
NOW = os.path.join(REPO, "concept", "items", "radiant")
B = os.path.join(NOW, "look-b")


def levels(path):
    im = Image.open(path).convert("RGBA")
    return {s: im.crop((o, 0, o + s, s)) for s, o in zip(SIZES, OFFS)}


def on(im, bg):
    g = Image.new("RGBA", im.size, bg + (255,))
    return Image.alpha_composite(g, im).convert("RGB")


def up(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def light_stats(im):
    px = [p[:3] for p in im.get_flattened_data() if p[3] > 128]
    blue = [p for p in px if p[2] > 110 and p[2] > p[0] + 45 and p[2] > p[1] + 10]
    lum = lambda p: 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]  # noqa: E731
    sat = lambda p: 0 if max(p) == 0 else (max(p) - min(p)) / max(p)  # noqa: E731
    pale = sum(1 for p in px if p[2] >= max(p[0], p[1]) and sat(p) < 0.45 and lum(p) > 150)
    top = max(blue, key=lum) if blue else None
    return dict(blue=round(100 * len(blue) / max(1, len(px)), 1),
                L=round(sum(map(lum, blue)) / max(1, len(blue))), sat=round(sum(map(sat, blue)) / max(1, len(blue)), 2),
                pale=pale, white=sum(1 for p in px if min(p) >= 245),
                top="#%02X%02X%02X" % top if top else None,
                top_hue=round(colorsys.rgb_to_hsv(*(c / 255 for c in top))[0] * 360) if top else None)


def column(lv, bg):
    """64/32/16/8 at 4x stacked, then the four at 1x in a row."""
    tiles = [up(on(lv[s], bg), 4) for s in SIZES]
    W = 256
    H = sum(t.height + 6 for t in tiles) + 70
    out = Image.new("RGB", (W, H), bg)
    y = 0
    for t in tiles:
        out.paste(t, ((W - t.width) // 2, y))
        y += t.height + 6
    x = 4
    for s in SIZES:
        out.paste(on(lv[s], bg), (x, y + 2))
        x += s + 6
    return out


def main():
    pdir, path = sys.argv[1], sys.argv[2]
    mnow = json.load(open(os.path.join(NOW, "measures.json")))
    mb = json.load(open(os.path.join(B, "measures.json")))
    vr = mb["vanilla_range"]
    now = {it: levels(os.path.join(NOW, "strips", it + ".png")) for it in ITEMS}
    new = {it: levels(os.path.join(B, "strips", "radiant", it + ".png")) for it in ITEMS}
    sh = Sheet("RADIANT ICONS in look B -- light behind dark glass and rock (proposal, beside the signed-off icons)",
               ["Rendered by tools/blender/render-icons.sh from concept/items/radiant/radiant_icons_b.py: the same forms, lead and worn finish as the",
                "signed-off radiant_icons.py, the light redrawn in look B -- B's glow ramp #000000 > #04103A > #0B2A8C > #1F63FF > #5A9CFF (no pale top),",
                "a navy liquid #0C1838 behind smoked glass #55606E, dark internals #1A1C22. icon_post.py rules unchanged. Measured as the icon pipeline",
                "measures (concept/items/review_sheet.py) plus the study's light measures. The shared helper (tools/blender/radiant.py on radiant-look) is",
                "still in progress there, so this uses look_pieces.py's B recipe directly; its colours equal the helper's constants (GLOW_RAMP, LIQUID, GLASS).",
                f"Vanilla's range over the analogues: p50 {vr['p50']}, p95 {vr['p95']}, outline step on slot {vr['edge_slot']}, on ground {vr['edge_ground']}."])
    for bg, bname in ((SLOT, "the inventory slot #2D2C2D"), (GROUND, "the ground #4A423A")):
        sh.section(f"On {bname}: each item now, then B -- 64, 32, 16, 8 px at 4x, then all four at 1x")
        panels = []
        for it in ITEMS:
            panels.append((column(now[it], bg), [it, "now (signed off)"]))
            panels.append((column(new[it], bg), ["", "look B"]))
        sh.row(panels)
    # inventory row: 32 px icons in 40 px slots, at 1x and 2x
    sh.section("In an inventory: now, then B (32 px in 40 px slots; 1x, then 2x)")
    inv = Image.new("RGB", (2 * (4 * 42 + 20), 42), (20, 20, 20))
    for k, src in enumerate((now, new)):
        for i, it in enumerate(ITEMS):
            x = k * (4 * 42 + 20) + i * 42
            inv.paste(Image.new("RGB", (40, 40), SLOT), (x, 1))
            inv.paste(on(src[it][32], SLOT), (x + 4, 5))
    sh.row([(inv, ["1x"]), (up(inv, 2), ["2x"])])
    # the study's pieces, for the match
    plate = down(os.path.join(pdir, "work-00.png"))
    glow = light_of(down(os.path.join(pdir, "glow-00.png")))
    base = on(plate, GROUND)
    pday, pnight = ImageChops.add(base, glow), ImageChops.add(darken(base), glow)
    # the five pieces sit 1.7 tiles apart, centred at x 272 px (1x, 64 px a tile)
    col, port, slot, tubes = (0, 0, 112, 192), (110, 40, 220, 192), (215, 40, 330, 192), (325, 40, 440, 192)
    sicon = Image.open(os.path.join(REPO, "..", "radiant-look", "concept", "radiant-look", "model",
                                    "icon-radiant-solution-B.png")).convert("RGBA") \
        if os.path.exists(os.path.join(REPO, "..", "radiant-look", "concept", "radiant-look", "model",
                                       "icon-radiant-solution-B.png")) else None
    sh.section("The match: the study's look-B pieces at 2x, day and night -- column (the RP leg), port, slot and tubes (the generator's) -- beside the B icons at 64 px, 2x",
               ["(and the study's own recolour of the drop, a 2-D remap of the current icon, when it is there)"])
    row = []
    for name, box in (("column", col), ("port", port), ("slot", slot), ("tubes", tubes)):
        row += [(up(pday.crop(box), 2), [f"{name}, day"]), (up(pnight.crop(box), 2), ["night"])]
    sh.row(row)
    row = []
    for it in ("radiant-fuel", "radiant-chunk", "radiant-solution"):
        row.append((up(on(new[it][64], GROUND), 2), [f"{it} B, 2x"]))
    if sicon:
        row.append((up(on(sicon.crop((0, 0, 64, 64)), GROUND), 2), ["study's drop recolour"]))
    sh.row(row)
    # measures
    lines = []
    out = {}
    for it in ITEMS:
        for tag, m, lv in (("now", mnow, now), ("B", mb, new)):
            o = m["ours"][f"radiant/{it}"]
            ls = light_stats(lv[it][64])
            out[f"{tag} {it}"] = dict(o, light=ls)
            lines.append(f"{it:18s} {tag:4s} share {o['framing']['share']:.2f} bbox {o['framing']['bbox_w']}x{o['framing']['bbox_h']} | "
                         f"p5/p50/p95 {o['tonal']['p5']}/{o['tonal']['p50']}/{o['tonal']['p95']} | outline slot {o['edge_slot']['mean']} "
                         f"ground {o['edge_ground']['mean']} (16 px: {o['edge_slot_16']['mean']}/{o['edge_ground_16']['mean']}) | "
                         f"strays 16/8 {o['strays']['16']['opaque']}/{o['strays']['8']['opaque']} | blue {ls['blue']}% L {ls['L']} "
                         f"sat {ls['sat']} pale {ls['pale']} white {ls['white']} top {ls['top']} ({ls['top_hue']} deg)")
    for tag, m in (("now", mnow), ("B", mb)):
        for s in (16, 8):
            p = m["pairwise"][f"ours/radiant/{s}"]
            lines.append(f"distinct at {s} px, {tag}: min {min(p.values())} -- fuel~spent {p['radiant-fuel~sae-spent-cell']}, "
                         f"fuel~drop {p['radiant-fuel~radiant-solution']}, chunk~fuel {p['radiant-chunk~radiant-fuel']}")
    vp = mb["pairwise"]["vanilla/16"]
    lines.append(f"vanilla at 16 px: uranium cell~depleted {vp['uranium-fuel-cell~depleted-uranium-fuel-cell']}, "
                 f"min over the analogues {min(vp.values())}")
    sh.section("Measures (64 px unless named; outline = mean L step from the outline to the background; distinct = mean |RGB| between two icons on the slot)", lines)
    sh.render(path)
    with open(os.path.splitext(path)[0] + "-measures.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
