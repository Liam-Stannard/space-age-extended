#!/usr/bin/env python3
"""Colour identity survey: the mean hue and saturation of an icon's lit pixels.

  python3 concept/items/hues.py [icon.png[:label] ...]

With no arguments, surveys vanilla's and Space Age's raw resources, raw materials
and plates, plus the mod's own fluid colours (siderane, helium-3), and prints each.

  python3 concept/items/hues.py --family <strips-dir> item[=#base] ... [--into measures.json]

measures a rendered family: each item's lit hue and saturation, its nearest
saturated neighbour among the raw materials above, vanilla's and Space Age's fluid
icons (FLUIDS), the mod's own colours (OURS, MOD_ICONS) and the family's other
members, and -- for a fluid, given its in-game base colour -- the distance from
that colour's hue. --into merges the result into a review sheet's measures.json
as "hue_survey" and "hues", as the kamacite round 3 sampler did.

"Lit pixels": the 64 px level's opaque pixels (alpha > 200) in the brighter half
of the icon's own luminance -- the faces the sun catches, which is where vanilla
puts an item's colour (iron ore's lit faces are its blue; its shadows are grey).
Hue is the saturation-weighted circular mean of HSV hue, in degrees; saturation
the mean HSV saturation (0-1) of the same pixels.
"""
import colorsys
import math
import sys

from PIL import Image

V = "/home/liam-stannard/.steam/steam/steamapps/common/Factorio/data"
BASE = ["iron-ore", "iron-plate", "copper-ore", "copper-plate", "uranium-ore", "stone", "coal",
        "steel-plate", "stone-brick", "sulfur", "wood", "solid-fuel", "plastic-bar", "uranium-238", "uranium-235"]
SPACE_AGE = ["tungsten-ore", "tungsten-plate", "tungsten-carbide", "holmium-ore", "holmium-plate", "calcite",
             "scrap", "lithium", "lithium-plate", "carbon", "ice"]
OURS = {"siderane (fluid)": (0.66, 0.85, 0.16), "helium-3 (fluid)": (0.55, 0.78, 0.90)}


FLUIDS = [("base", n) for n in ("crude-oil", "heavy-oil", "light-oil", "petroleum-gas", "lubricant", "sulfuric-acid",
                                 "water", "steam")] + \
         [("space-age", n) for n in ("ammonia", "ammoniacal-solution", "electrolyte", "fluorine", "fluoroketone-cold",
                                      "fluoroketone-hot", "holmium-solution", "lava", "lithium-brine", "molten-copper",
                                      "molten-iron", "thruster-fuel", "thruster-oxidizer")]
# the mod's settled colours, as rendered or as specified
MOD_COLOURS = {"kamacite teal (rendered, 160-166)": (163, 0.29), "radiant green-white #A8E8C0": None,
               "radiant solution (fluid)": (0.12, 0.39, 1.0), "molten kamacite (fluid)": (0.85, 0.42, 0.16)}


def lit(im):
    im = im.convert("RGBA").crop((0, 0, 64, 64)) if im.width > im.height else im.convert("RGBA")
    px = [p for p in im.get_flattened_data() if p[3] > 200]
    if not px:
        return []
    L = sorted(0.299 * r + 0.587 * g + 0.114 * b for r, g, b, a in px)
    med = L[len(L) // 2]
    return [p for p in px if 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2] >= med]


def hue_sat(pixels):
    sx = sy = st = 0.0
    for r, g, b, *_ in pixels:
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        sx += s * math.cos(2 * math.pi * h)
        sy += s * math.sin(2 * math.pi * h)
        st += s
    n = max(len(pixels), 1)
    return (math.degrees(math.atan2(sy, sx)) % 360, st / n)


def icon(path):
    return hue_sat(lit(Image.open(path)))


def colour(rgb):
    h, s, v = colorsys.rgb_to_hsv(*rgb)
    return (h * 360, s)


def survey():
    out = {}
    for n in BASE:
        out[n] = icon(f"{V}/base/graphics/icons/{n}.png")
    for n in SPACE_AGE:
        out[n] = icon(f"{V}/space-age/graphics/icons/{n}.png")
    for n, c in OURS.items():
        out[n] = colour(c)
    return out


def dist(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def nearest(h, table, min_sat=0.12):
    """The nearest hue among entries saturated enough to have one."""
    best = None
    for n, (hh, s) in table.items():
        if s < min_sat:
            continue
        d = dist(h, hh)
        if best is None or d < best[1]:
            best = (n, d)
    return best


def survey_all():
    """Raw materials, every vanilla fluid icon, and the mod's own colours."""
    out = survey()
    for m, n in FLUIDS:
        out[f"{n} (fluid icon)"] = icon(f"{V}/{m}/graphics/icons/fluid/{n}.png")
    for n, c in MOD_COLOURS.items():
        if c is None:
            out[n] = colour((0xA8 / 255, 0xE8 / 255, 0xC0 / 255))
        elif len(c) == 2:
            out[n] = c
        else:
            out[n] = colour(c)
    return out


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def family(strips, specs, own=()):
    """specs: ["item" or "item=#base"]; own: table keys to leave out of the
    nearest search (the item's own base colour, so a fluid is not 'nearest' itself)."""
    import os
    table = survey_all()
    res = {}
    rendered = {}
    for sp in specs:
        it, _, base = sp.partition("=")
        rendered[it] = icon(os.path.join(strips, it + ".png"))
    for sp in specs:
        it, _, base = sp.partition("=")
        h, s = rendered[it]
        others = {k: v for k, v in table.items() if k not in own}
        others.update({f"{o} (ours)": v for o, v in rendered.items() if o != it})
        near = nearest(h, others)
        r = {"hue": round(h), "sat": round(s, 2), "nearest": near[0], "distance": round(near[1])}
        if base:
            bh, bs = colour(hexrgb(base))
            r["base_colour"] = base
            r["base_hue"] = round(bh)
            r["off_base"] = round(dist(h, bh))
        res[it] = r
    return table, res


if __name__ == "__main__" and "--family" in sys.argv:
    import json
    a = sys.argv[sys.argv.index("--family") + 1:]
    into = None
    if "--into" in a:
        into = a[a.index("--into") + 1]
        a = a[:a.index("--into")]
    strips, specs = a[0], a[1:]
    own = [k for k in MOD_COLOURS if any(w in k for w in ("solution", "molten"))] + \
          [k for k in OURS if any(sp.startswith(k.split(" ")[0]) for sp in specs)]
    table, res = family(strips, specs, own)
    for it, r in res.items():
        extra = f"  base {r['base_colour']} hue {r['base_hue']}, off by {r['off_base']}" if "base_colour" in r else ""
        print(f"{it:20s} hue {r['hue']:4d} sat {r['sat']:.2f}  nearest {r['nearest']} ({r['distance']} deg){extra}")
    if into:
        m = json.load(open(into))
        m["hue_survey"] = {n: {"hue": round(h), "sat": round(s, 2)} for n, (h, s) in table.items()}
        m["hues"] = res
        json.dump(m, open(into, "w"), indent=1)
elif __name__ == "__main__":
    table = survey()
    for a in sys.argv[1:]:
        p, _, lab = a.partition(":")
        table[lab or p] = icon(p)
    for n, (h, s) in sorted(table.items(), key=lambda kv: kv[1][0]):
        print(f"{n:22s} hue {h:5.0f}  sat {s:.2f}" + ("   (grey: no hue)" if s < 0.12 else ""))
