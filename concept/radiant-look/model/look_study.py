#!/usr/bin/env python3
"""The radiant look study: every current use of the radiant blue beside vanilla's lit fluids and
light through glass, measured, at 1x (64 px a tile) and 4x, day and night.

  python3 look_study.py <out.png> [--pool-shots <dir>] [--json <measures.json>]

Sources (read only):
  the Reaction Plant model's sheets   (worktree reaction-plant-redesign)
  the generator round 6 1x GIFs       (worktree radiant-generator-options; working, frame 0)
  the pool in game                    (the tester's pool-placed screenshots, day and night)
  the icons                           (graphics/icons in this worktree, the 64 px mip)
  vanilla                             (the Factorio data directory)

Day and night are composed as look_common.py says (emulated). The generator has no glow
sheet, so its night takes its blue pixels as the glow (stated on the sheet).
"""
import json
import os
import sys

from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from look_common import (GROUND, Sheet, blue_mask, blue_share, darken, day, light_measures,  # noqa: E402
                         lum, night, on_ground, sat, up)

WT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
WTS = os.path.dirname(WT)
RP = os.path.join(WTS, "reaction-plant-redesign", "concept", "reaction-plant", "model", "sheets")
GEN = os.path.join(WTS, "radiant-generator-options", "concept", "radiant-generator", "options", "round-6")
ICONS = os.path.join(WT, "graphics", "icons")
D = "/home/liam-stannard/.steam/steam/steamapps/common/Factorio/data/"
POOL = ("/tmp/claude-1000/-home-liam-stannard-git-space-age-extended/bc7d463e-8c35-4cbc-ab43-70ae859d9a08/"
        "scratchpad/tester/pool-placed/evidence/shots")

args = sys.argv[1:]
OUT = args[0]
if "--pool-shots" in args:
    POOL = args[args.index("--pool-shots") + 1]
JSON = args[args.index("--json") + 1] if "--json" in args else None


def blue_stats(im, alpha=None):
    """On the blue pixels (blue_mask): share, mean luminance, mean saturation, % pale (L >= 170)."""
    m = list(blue_mask(im).get_flattened_data())
    px = [p for p, v in zip(im.convert("RGB").get_flattened_data(), m) if v]
    if not px:
        return dict(blue=0.0, L=0, sat=0, pale=0)
    L = [lum(p) for p in px]
    return dict(blue=round(blue_share(im, alpha), 2), L=round(sum(L) / len(L)),
                sat=round(sum(sat(p) for p in px) / len(px), 2),
                pale=round(100 * sum(1 for v in L if v >= 170) / len(L), 1))


def bbox_of(mask_img, pad, size):
    bb = mask_img.getbbox()
    if not bb:
        return (0, 0, size[0], size[1])
    return (max(0, bb[0] - pad), max(0, bb[1] - pad), min(size[0], bb[2] + pad), min(size[1], bb[3] + pad))


def zoom_box(light, size, w=48, h=48):
    """A w x h box round the brightest part of a light image."""
    L = light.convert("L")
    px = list(L.get_flattened_data())
    i = max(range(len(px)), key=px.__getitem__)
    x, y = i % L.width, i // L.width
    x0 = min(max(0, x - w // 2), max(0, size[0] - w))
    y0 = min(max(0, y - h // 2), max(0, size[1] - h))
    return (x0, y0, x0 + w, y0 + h)


def panelset(name, dayim, nightim, light, box, zbox, notes):
    """1x day, 1x night (cropped to box) and 4x day + 4x night of zbox."""
    a = dayim.crop(box)
    b = nightim.crop(box) if nightim else None
    z1 = up(dayim.crop(zbox), 4)
    z2 = up(nightim.crop(zbox), 4) if nightim else None
    out = [(a, [name, "1x day"])]
    if b:
        out.append((b, ["", "1x night"]))
    out.append((z1, notes[:1] + ["4x day"]))
    if z2:
        out.append((z2, notes[1:2] + ["4x night"]))
    return out


MEAS = {}
sheet = Sheet("RADIANT LOOK -- the study: how the radiant blue is drawn now, beside vanilla's lit fluids",
              ["Crops at 1x (64 px a tile, the sheets' own size) and 4x (nearest). Day: plate + animation frame on "
               "preview.py's ground, the glow layer added. Night (emulated, not checked in a client): the lit scene "
               "x (0.17, 0.19, 0.27),",
               "the glow layer added after it (draw_as_glow). blue = the generator sheets' measure (B>110, B>R+45, "
               "B>G+10) as a share of the opaque pixels; L and sat are the mean luminance and saturation of those "
               "blue pixels; pale = blue px with L>=170.",
               "glow: core = lit px >= 60% of the peak, halo = <= 25% of the peak (as a share of lit px); "
               "under = the plate under the hottest glow (mean L / saturation); sharp = |glow - blur2|/glow, "
               "lower is softer."])

# ------------------------------------------------------------------ the Reaction Plant
meta = json.load(open(os.path.join(RP, "meta.json")))


def place(canvas, im, shift_tiles, origin):
    x = int(round(origin[0] + shift_tiles[0] * 64 - im.width / 2))
    y = int(round(origin[1] + shift_tiles[1] * 64 - im.height / 2))
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(im, (x, y))
    return layer


base = Image.open(os.path.join(RP, "base.png")).convert("RGBA")
bw, bh = base.size
o = (bw / 2 - meta["base"]["shift"][0] * 64, bh / 2 - meta["base"]["shift"][1] * 64)
legs_sheet = Image.open(os.path.join(RP, "legs.png")).convert("RGBA")
lw, lh = meta["legs"]["size"]
legs0 = legs_sheet.crop((0, 0, lw, lh))
plate = Image.alpha_composite(base, place(base, legs0, meta["legs"]["shift"], o))
idle_plate = base
lg = Image.open(os.path.join(RP, "legs-glow.png")).convert("RGB")
light = Image.new("RGB", base.size)
light.paste(lg, (int(round(o[0] + meta["legs-glow"]["shift"][0] * 64 - lg.width / 2)),
                 int(round(o[1] + meta["legs-glow"]["shift"][1] * 64 - lg.height / 2))))
rp_day, rp_night = day(plate, light), night(plate, light)
box = bbox_of(light.convert("L").point(lambda v: 255 if v > 8 else 0), 22, base.size)
zb = zoom_box(light, base.size, 40, 48)
lm = light_measures(light)
under = [p for p, g in zip(plate.get_flattened_data(), light.convert("L").get_flattened_data())
         if g >= 0.5 * lm["peak"] and p[3] > 128]
lm["under_L"] = round(sum(lum(p) for p in under) / max(1, len(under)))
lm["under_sat"] = round(sum(sat(p[:3]) for p in under) / max(1, len(under)), 2)
bs = blue_stats(on_ground(plate), plate.getchannel("A"))
MEAS["RP legs"] = dict(blue_stats=bs, glow=lm)
sheet.section("1. The Reaction Plant model: the glass legs (bands and bubbles)",
              [f"Whole building, working frame 0: blue {bs['blue']}% (L {bs['L']}, sat {bs['sat']}, pale {bs['pale']}%). "
               f"Glow: peak {lm['peak']}, core {lm['core']}%, halo {lm['halo']}%, sat {lm['sat_core']}/{lm['sat_halo']}, "
               f"under the glow the plate is L {lm['under_L']} sat {lm['under_sat']} (vanilla: 29-65, 0.16-0.33).",
               "The light is in the plate: the legs layer is the lit, saturated blue (#1F63FF..#73ADFF bands), and the "
               "glow is the same shape flattened; the solution lights nothing round it (visible_diffuse off), no halo."])
sheet.row(panelset("RP legs", rp_day, rp_night, light, box, zb, ["the legs, frame 0", ""])
          + [(up(on_ground(idle_plate).crop(zb), 4), ["", "4x idle (legs unlit)"])])

# ------------------------------------------------------------------ the generator, round 6
gm = json.load(open(os.path.join(GEN, "measures.json")))
row = []
notes = []
for k, f in (("1", "1-the-carousel-foundry-1x.gif"), ("2", "2-the-crane-hall-1x.gif"),
             ("3", "3-the-commutator-front-1x.gif")):
    g = Image.open(os.path.join(GEN, f))
    g.seek(0)
    fr = g.convert("RGB")
    bm = blue_mask(fr)
    glow_est = Image.composite(fr, Image.new("RGB", fr.size), bm)
    gn = ImageChops.add(darken(fr), glow_est)
    bs = blue_stats(fr)
    MEAS[f"generator r6 {k}"] = dict(blue_stats=bs, blue_pct_r6=gm[k]["blue_pct"])
    zb = zoom_box(glow_est, fr.size, 56, 48)
    row += [(fr, [f.split("-1x")[0], "1x working, frame 0 (GIF)"]),
            (up(fr.crop(zb), 4), ["", "4x day"]), (up(gn.crop(zb), 4), ["", "4x night (blue as glow)"])]
    notes.append(f"{k}: blue {gm[k]['blue_pct']}% of the building (r6 measures); on its blue px L {bs['L']}, "
                 f"sat {bs['sat']}, pale {bs['pale']}%")
sheet.section("2. The generator, round 6: windows, slot and tubes (\"look out of place\")",
              notes + ["Frames are from the round's 1x GIFs: the hard posterised steps in the blue are the GIF palette's, "
                       "not the render's."] + ["Same material as the RP legs (radiant(): distorted wave bands or a swirl, #0B2A8C..#73ADFF, "
                       "emission 2.4x): large flat saturated fields at 1x, no core, no falloff to the bezel, no spill "
                       "on the metal round them -- read as stickers."])
sheet.row(row[:6])
sheet.row(row[6:])

# ------------------------------------------------------------------ the pool in game
pr = []
pnotes = []
for when in ("day", "night"):
    im = Image.open(os.path.join(POOL, f"landing-123456789-pool-{when}.png")).convert("RGB")
    box = (260, 300, 260 + 520, 300 + 360)
    c = im.crop(box)
    z = up(im.crop((520, 860, 520 + 64, 860 + 64)), 4)
    bs = blue_stats(c)
    MEAS[f"pool {when}"] = dict(blue_stats=bs)
    pr += [(c, [f"pool, {when} (client screenshot)", "crop"]), (z, ["", "4x of the shore"])]
    pnotes.append(f"{when}: blue {bs['blue']}% of the crop, L {bs['L']}, sat {bs['sat']}, pale {bs['pale']}%")
sheet.section("3. The radiant pool in game (seed 123456789, the tester's screenshots; screenshot zoom, not 64 px a tile)",
              pnotes + ["A lava-hot tile shader in #1E64FF / #08183C: a mid, slightly cyan blue with dark mottling, "
                        "flat in value; at night it greys and flattens (no hot core, no spill on the shore)."])
sheet.row(pr)

# ------------------------------------------------------------------ the icons
ir = []
inotes = []
for f in ("fluid/radiant-solution.png", "radiant-fuel.png", "radiant-chunk.png", "spent-cell.png"):
    im = Image.open(os.path.join(ICONS, f)).convert("RGBA").crop((0, 0, 64, 64))
    g = on_ground(im)
    bs = blue_stats(g, im.getchannel("A"))
    MEAS[f"icon {f}"] = dict(blue_stats=bs)
    ir += [(g, [f.split("/")[-1][:-4], "1x"]), (up(g, 4), ["", "4x"])]
    inotes.append(f"{f.split('/')[-1][:-4]}: blue {bs['blue']}%, L {bs['L']}, sat {bs['sat']}, pale {bs['pale']}%")
sheet.section("4. The icons (the 64 px mip)", ["; ".join(inotes),
              "The drop is a glossy plastic blue (a white specular, no inner light); the fuel cell a flat light blue "
              "behind bars; the chunk's veins a thin cyan line with a glow -- three different blues."])
sheet.row(ir)

# ------------------------------------------------------------------ vanilla
sys.path.insert(0, os.path.join(HERE))
from look_vanilla import REFS, comp  # noqa: E402

vnotes = {
    "chemical-plant": "window: the recipe-tinted liquid under a foam layer; no glow (shown tinted #1F63FF: the same sticker)",
    "oil-refinery": "fire light only: a soft additive glow, no lit fluid",
    "nuclear-reactor": "lit plate (reactor-lights-color) as a soft additive glow on dark vents; heat glow apart",
    "fusion-generator": "plasma seen through slits: dark plate, the light a saturated glow + a UV-scrolled plasma",
    "fusion-reactor": "rings of slits; the light spills on the rims; peak only ~90",
    "centrifuge": "perforated drum: light through holes, a dark plate, a turning glow",
    "uranium-ore": "the ore's glow: saturated, soft, a lit plate under it",
    "cryogenic-plant": "windows show recipe-tinted fluid behind glass (glass highlight layer); working lights as glow",
    "lithium-brine": "the resource: no glow, a painted liquid ring",
}
vrows = []
for n, (cv, ly) in REFS.items():
    b, g = comp(cv, ly)
    dd, nn = day(b, g), night(b, g)
    lm = light_measures(g)
    pk = lm["peak"]
    if pk:
        under = [p for p, v in zip(b.get_flattened_data(), g.convert("L").get_flattened_data())
                 if v >= 0.5 * pk and p[3] > 128]
        lm["under_L"] = round(sum(lum(p) for p in under) / max(1, len(under)))
        lm["under_sat"] = round(sum(sat(p[:3]) for p in under) / max(1, len(under)), 2)
        opaque = sum(1 for p in b.get_flattened_data() if p[3] > 128)
        lm["lit_share"] = round(100 * lm["area"] / opaque, 1)
        zb = zoom_box(g, cv, 48, 48)
        if n == "cryogenic-plant":
            zb = (171, 111, 219, 159)          # the dome's window (glass layer over the fluid)
    else:
        zb = (cv[0] // 2 - 24, cv[1] // 2 - 24, cv[0] // 2 + 24, cv[1] // 2 + 24)
        if n == "chemical-plant":
            zb = (cv[0] // 2 + 23 * 2 - 30, cv[1] // 2 + 15 * 2 - 24, cv[0] // 2 + 23 * 2 + 18, cv[1] // 2 + 15 * 2 + 24)
    MEAS[f"vanilla {n}"] = dict(glow=lm)
    cap = (f"peak {lm['peak']} core {lm['core']}% halo {lm['halo']}% sat {lm['sat_core']}/{lm['sat_halo']}"
           if pk else "no glow layer")
    cap2 = (f"under L {lm['under_L']} sat {lm['under_sat']}, glow px {lm['lit_share']}% of plate px" if pk else "")
    vrows.append([(dd, [n, vnotes[n][:58]]), (nn, [vnotes[n][58:116], "night"]),
                  (up(dd.crop(zb), 4), [cap, "4x day"]), (up(nn.crop(zb), 4), [cap2, "4x night"])])
sheet.section("5. Vanilla: lit fluids and light through glass (frame 0; 1x whole, 4x round the hottest pixel)",
              ["How vanilla builds depth: the plate under the light stays DARK and greyish (L 29-65, sat 0.16-0.33): "
               "a slit, a hole, a vent, never a big lit field. The light is a separate additive glow (draw_as_glow),",
               "pure hue (sat ~1.0), soft (77-88% of its lit pixels are halo at <= 25% of peak), never clipped "
               "(peak 87-171 on machines), and it spills onto the rims and bezels round the opening.",
               "The hot area is tiny: 0.2-2.6% of the sprite; the spill 2-20%. Depth comes from dark internals "
               "(holes, grilles, slits) silhouetted against the light, a bezel in shadow, and a glass highlight",
               "on its own layer (cryogenic plant). Motion is slow: a turning drum, a scrolling plasma UV, a pulse. "
               "At night the plate drops away and the glow alone draws the machine's light, unchanged."])
for r in vrows:
    sheet.row(r)

sheet.render(OUT)
if JSON:
    json.dump(MEAS, open(JSON, "w"), indent=1)
print("wrote", OUT)
for k, v in MEAS.items():
    print(k, v)
