#!/usr/bin/env python3
"""The three candidate looks' sheets and GIFs, from look_pieces.py's renders.

  python3 look_sheets.py <render-root> <concept-dir>
     <render-root>/{A,B,C}/idle.png, work-NN.png, glow-NN.png   (4x)
     writes <concept-dir>/candidate-<X>-<name>.png, candidate-<X>-<name>-1x.gif (day | night),
            candidate-<X>-<name>-2x.gif (day, the column, port and slot), and
            <concept-dir>/model/candidate-measures.json

Each sheet: idle, working day and night and the glow layer alone at 1x; every piece at 4x,
day and night; the frame strip; the pool shore and the radiant solution icon recoloured to
the look; the measures (blue share at 1x, the glow's build, the plate under the glow, the
idle plate's tonal spread). The glow layer is the glow render plus the look's bloom (a soft
halo baked into the glow sheet), drawn additively; day and night as look_common.py says.
"""
import json
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from look_common import (Sheet, blue_share, bloom, darken, day, down, light_measures, light_of, lum,  # noqa: E402
                         night, on_ground, sat, up)

ROOT, CONCEPT = sys.argv[1], sys.argv[2]
WT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
POOL = ("/tmp/claude-1000/-home-liam-stannard-git-space-age-extended/bc7d463e-8c35-4cbc-ab43-70ae859d9a08/"
        "scratchpad/tester/pool-placed/evidence/shots")
ICON = os.path.join(WT, "graphics", "icons", "fluid", "radiant-solution.png")

# the pieces' crops at 1x (canvas 544 x 192, origin (272, 140), 64 px a tile; x = -3.4 .. 3.4 tiles)
PIECES = [("column", (26, 8, 106, 176)), ("port", (118, 70, 212, 180)), ("slot", (226, 76, 330, 150)),
          ("tubes", (334, 74, 434, 152)), ("well", (444, 76, 544, 152))]

LOOKS = {
    "A": dict(
        name="deep-column", title="A -- DEEP COLUMN (plate-led: a thick body of light)",
        bloom=(1.5, 0.35),
        recipe=[
            "Material: the solution an emitter whose colour runs a 5-stop ramp #040C24 > #0B2A8C > #1F63FF > #73ADFF > "
            "#D2E6FF on 0.74 x core + 0.13 x caustic, emission 2.1 (glow pass 0.9).",
            "  core = the body's thickness: (1 - facing)^1.6 on a column or tube; 1 - (r/R)^1.5 on a port or well; "
            "across x ends on a slot -- a pale middle falling to saturated blue, then navy at the glass's edges.",
            "  caustic = Voronoi distance-to-edge, a net of thin bright lines drifting up the column (across a "
            "flat window), looped by crossfading two copies a loop apart.",
            "Glass: clear borosilicate, coat 0.5 (the column and tubes), a thin clear pane over the port and slot. "
            "The solution lights its bezels (visible_diffuse on).",
            "Glow layer: the same light at 0.9 (a third), sun and sky off, plus a bloom of 1.5 px at 0.35: thin, it "
            "keeps the windows lit at night. Most of the light is in the plate.",
            "Animation: the caustic net rising (one net-height a loop), 16 frames, no pulse. Idle: the liquid "
            "a dark navy (emission 0)."]),
    "B": dict(
        name="smoked-lamp", title="B -- LAMP BEHIND SMOKED GLASS (glow-led, as vanilla's lit machines)",
        bloom=(3.0, 0.9),
        recipe=[
            "Material, plate: smoked glass (#55606E, transmission 0.85) over a dim liquid -- emission 0.25 on the "
            "ramp #02081A > #0B2A8C > #1F63FF > #73ADFF > #E2EEFF: a deep navy-blue with the internals readable.",
            "  Internals, dark steel, silhouetted: a heater rod and six baffles in the column, a grid and a boss "
            "in the port, seven baffles across the slot, a filament in each tube, a grate over the well.",
            "Glow layer (where the light lives): the same pattern on a saturated ramp #000000 > #04103A > #0B2A8C > "
            "#1F63FF > #5A9CFF (no pale top: vanilla's glows are pure hue, never clip),",
            "  emission 2.3 on the core^0.8 with a faint looped noise flicker, sun and sky off, so it lights the "
            "rims and bezels round each opening; plus a bloom of 3 px at 0.9 (vanilla's soft halo).",
            "Animation: a slow breathing pulse, 0.84 > 1.0 > 0.84 a loop (cosine), and the flicker drifting up; "
            "16 frames. The plate barely moves; the glow does. Day and night read alike."]),
    "C": dict(
        name="rising-stream", title="C -- RISING STREAM (lit from below: bubbles, flecks, a meniscus)",
        bloom=(1.0, 0.5),
        recipe=[
            "Material: ramp #061436 > #0B2A8C > #1F63FF > #73ADFF > #B8D6FF, emission 2.0. In a column or tube the "
            "liquid is lit from its foot: 0.72 x (1 - h^0.55) + 0.2 x core, brightest low,",
            "  darkening up to a bright meniscus line just under the top flange (+0.75). On a flat window or the well, "
            "convection cells: Voronoi edges (0.42) on the core (0.55), drifting a cell a loop.",
            "Particles: pale bubbles (#C6DEFF emitters at 1.5, r 0.016-0.028) rising in the front of the column (30), "
            "the port (10), along the slot floor (14) and up each tube (3);",
            "  dark flecks (12, #141820) sinking in the column -- the internal silhouettes. Each covers its path once "
            "a loop, so the loop closes.",
            "Glow layer: the liquid at 1.1 and the bubbles at 1.2, sun and sky off, plus a bloom of 1 px at 0.5: "
            "the lit foot and the bubbles sparkle at night.",
            "Animation: bubbles up, flecks down, cells drifting; 16 frames."]),
}
RAMP = {"A": ["#040C24", "#0B2A8C", "#1F63FF", "#73ADFF", "#D2E6FF"],
        "B": ["#02081A", "#0B2A8C", "#1F63FF", "#73ADFF", "#E2EEFF"],
        "Bglow": ["#000000", "#04103A", "#0B2A8C", "#1F63FF", "#5A9CFF"],
        "C": ["#061436", "#0B2A8C", "#1F63FF", "#73ADFF", "#B8D6FF"]}


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def ramp(stops, v):
    """v in 0..1 over evenly spaced stops -> RGB."""
    v = max(0.0, min(1.0, v))
    n = len(stops) - 1
    i = min(n - 1, int(v * n))
    f = v * n - i
    a, b = hexrgb(stops[i]), hexrgb(stops[i + 1])
    return tuple(int(a[k] + (b[k] - a[k]) * f) for k in range(3))


def lut(stops, gain=1.0, gamma=1.0):
    return [ramp(stops, min(1.0, (i / 255) ** gamma * gain)) for i in range(256)]


def apply_lut(gray, table, mask=None):
    rgb = Image.new("RGB", gray.size)
    rgb.putdata([table[v] for v in gray.get_flattened_data()])
    return rgb


# ------------------------------------------------------------------ the pool, recoloured
def pool_crops():
    out = {}
    for when in ("day", "night"):
        im = Image.open(os.path.join(POOL, f"landing-123456789-pool-{when}.png")).convert("RGB")
        out[when] = im.crop((420, 760, 420 + 360, 760 + 240))
    return out


def pool_recolour(look, crop_day):
    """The pool shore crop recoloured to a look: the pool's own value structure (its blue channel
    over its red) mapped through the look's ramp, the shore left as it is.
    Returns (day, night) at the crop's size; night = the plate darkened + the look's glow."""
    r, g, b = crop_day.split()
    sig = ImageChops.subtract(b, r)                      # how blue a pixel is
    mask = sig.point(lambda v: 255 if v > 50 else int(255 * max(0, v - 25) / 25))
    mask = mask.filter(ImageFilter.GaussianBlur(0.6))
    # the pool's own value structure, normalised to its 5th..95th percentile on the pool
    bv = sorted(x for x, k in zip(b.get_flattened_data(), mask.get_flattened_data()) if k > 200)
    p5, p95 = bv[len(bv) // 20], bv[len(bv) * 19 // 20]
    v = b.point(lambda x: int(max(0, min(255, (x - p5) * 255 / max(1, p95 - p5)))))
    rnd = random.Random(7)

    def span(img, lo, hi):
        return img.point(lambda x: int(255 * (lo + (hi - lo) * x / 255)))
    if look == "A":
        # a thick body: the slow value field as depth, the fine mottling as faint caustic lines
        depth = v.filter(ImageFilter.GaussianBlur(8))
        fine = ImageChops.subtract(v, v.filter(ImageFilter.GaussianBlur(2)))
        f = ImageChops.add(span(depth, 0.22, 0.66), fine.point(lambda x: min(255, int(x * 0.5))))
        plate = apply_lut(f, lut(RAMP["A"]))
        glow = plate.point(lambda x: int(x * 0.3))
    elif look == "B":
        f = v.filter(ImageFilter.GaussianBlur(1.2))
        plate = apply_lut(span(f, 0.12, 0.45), lut(RAMP["B"]))       # the plate: dim navy, its internals
        glow = apply_lut(span(f.filter(ImageFilter.GaussianBlur(5)), 0.15, 0.75), lut(RAMP["Bglow"])).point(lambda x: int(x * 0.7))
    else:
        f = v.filter(ImageFilter.GaussianBlur(1.0))
        plate = apply_lut(span(f, 0.2, 0.62), lut(RAMP["C"]))
        glow = plate.point(lambda x: int(x * 0.3))
        d = ImageDraw.Draw(plate)
        dg = ImageDraw.Draw(glow)
        mpx = mask.load()
        for _ in range(140):                             # bubbles breaking the surface
            x, y = rnd.randrange(crop_day.width), rnd.randrange(crop_day.height)
            if mpx[x, y] > 200:
                rr = rnd.choice((1, 1, 2))
                d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(198, 222, 255))
                dg.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(120, 160, 230))
    plate = Image.composite(plate, crop_day, mask)
    glow = Image.composite(glow, Image.new("RGB", glow.size), mask)
    if look == "B":
        # the halo reaches over the shore's edge, as a glow layer would
        glow = ImageChops.add(glow, glow.filter(ImageFilter.GaussianBlur(5)).point(lambda x: int(x * 0.35)))
    dayim = ImageChops.add(plate, glow)
    nightim = ImageChops.add(darken(plate), glow)
    return dayim, nightim


# ------------------------------------------------------------------ the icon, recoloured
def icon_recolour(look):
    src = Image.open(ICON).convert("RGBA").crop((0, 0, 64, 64))
    r, g, b, a = src.split()
    rgb = src.convert("RGB")
    sig = ImageChops.subtract(b, r)
    body = ImageChops.multiply(sig.point(lambda v: 255 if v > 40 else 0), a)
    # the core: how deep inside the drop a pixel is (the body mask blurred)
    core = body.filter(ImageFilter.GaussianBlur(7))
    core = core.point(lambda v: int(max(0, min(255, (v - 60) * 255 / 160))))
    shade = rgb.convert("L")
    spec = ImageChops.multiply(shade.point(lambda v: 255 if v > 200 else 0),
                               ImageChops.invert(sig.point(lambda v: 255 if v > 90 else 0)))
    if look == "A":
        f = ImageChops.add(core.point(lambda v: int(v * 0.6)), shade.point(lambda v: int(v * 0.25)))
        col = apply_lut(f, lut(RAMP["A"], 0.9))
    elif look == "B":
        f = ImageChops.add(core.point(lambda v: int(v * 0.95)), shade.point(lambda v: int(v * 0.1)))
        col = apply_lut(f, lut(RAMP["B"], 0.85, 1.6))
    else:
        h = Image.linear_gradient("L").resize((64, 64))        # 0 top .. 255 bottom
        f = ImageChops.add(h.point(lambda v: int(v * 0.55)), core.point(lambda v: int(v * 0.3)))
        col = apply_lut(f, lut(RAMP["C"]))
        d = ImageDraw.Draw(col)
        rnd = random.Random(3)
        bpx = body.load()
        for _ in range(40):
            x, y = rnd.randrange(64), rnd.randrange(64)
            if bpx[x, y] > 200 and y > 20:
                d.point((x, y), fill=(200, 224, 255))
    out_rgb = Image.composite(col, rgb, body)
    out_rgb = Image.composite(rgb, out_rgb, spec)            # keep the drop's own highlight
    out = Image.merge("RGBA", (*out_rgb.split(), a))
    if look == "B":
        # vanilla's lit icons (uranium) carry a soft glow past their edge
        halo = body.filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.5))
        glow = Image.new("RGBA", out.size, hexrgb("#1F63FF") + (0,))
        glow.putalpha(halo)
        out = Image.alpha_composite(glow, out)
    return src, out


# ------------------------------------------------------------------ one look
def measures(look, idle, works, lights):
    w0, l0 = works[0], lights[0]
    d0 = day(w0, l0)
    alpha = w0.getchannel("A")
    m = dict(blue_row=round(blue_share(d0, alpha), 2),
             blue_row_night=round(blue_share(night(w0, l0), alpha), 2),
             blue_row_mean=round(sum(blue_share(day(w, li), alpha) for w, li in zip(works, lights)) / len(works), 2))
    m["blue_pieces"] = {n: round(blue_share(d0.crop(bx), alpha.crop(bx)), 2) for n, bx in PIECES}
    lm = light_measures(l0)
    under = [p for p, g in zip(w0.get_flattened_data(), l0.convert("L").get_flattened_data())
             if g >= 0.5 * lm["peak"] and p[3] > 128]
    lm["under_L"] = round(sum(lum(p) for p in under) / max(1, len(under)))
    lm["under_sat"] = round(sum(sat(p[:3]) for p in under) / max(1, len(under)), 2)
    m["glow"] = lm
    # clipped by the light: white in the day frame and not already white in the idle plate (glass glints)
    iw = [min(p) >= 245 for p in on_ground(idle).get_flattened_data()]
    m["white_day"] = sum(1 for p, w in zip(d0.get_flattened_data(), iw) if min(p) >= 245 and not w)
    m["blue_plate"] = round(blue_share(on_ground(w0), alpha), 2)
    L = sorted(lum(p) for p in idle.get_flattened_data() if p[3] > 200)
    q = lambda f: round(L[int(f * (len(L) - 1))])  # noqa: E731
    m["tonal_idle"] = dict(p5=q(.05), p50=q(.5), p95=q(.95))
    # how much the window changes over the loop (mean |frame - frame 0| on the lit px, day)
    base = d0.convert("L")
    lit = l0.convert("L").point(lambda v: 255 if v > 12 else 0)
    n = max(1, lit.histogram()[255])
    ch = []
    for w, li in zip(works[1:], lights[1:]):
        df = ImageChops.difference(day(w, li).convert("L"), base)
        ch.append(sum(v for v, k in zip(df.get_flattened_data(), lit.get_flattened_data()) if k) / n)
    m["motion_mean_dL"] = round(max(ch) if ch else 0, 1)
    return m


def build(look):
    cfg = LOOKS[look]
    d = os.path.join(ROOT, look)
    nf = len([f for f in os.listdir(d) if f.startswith("work-")])
    idle = down(os.path.join(d, "idle.png"))
    works = [down(os.path.join(d, f"work-{i:02d}.png")) for i in range(nf)]
    lights = [bloom(light_of(down(os.path.join(d, f"glow-{i:02d}.png"))), *cfg["bloom"]) for i in range(nf)]
    m = measures(look, idle, works, lights)
    w0, l0 = works[0], lights[0]
    dy, nt = day(w0, l0), night(w0, l0)

    sh = Sheet(f"RADIANT LOOK -- candidate {cfg['title']}",
               ["Five test pieces, left to right: a glass column (the RP legs), a bullseye port, a glazed slot, a ring "
                "of tube emitters, an open well. The mod's finish (materials.layered, the RP palette) under rig.py.",
                "64 px a tile at 1x; 4x is nearest. Day: plate + frame on preview.py's ground, the glow layer added. "
                "Night (emulated, unchecked in a client): the lit scene x (0.17, 0.19, 0.27), the glow added after.",
                f"Blue share at 1x (the generator's measure, of opaque px), working day frame 0: {m['blue_row']}% of the "
                f"row (loop mean {m['blue_row_mean']}%, night {m['blue_row_night']}%; the plate alone, without its glow, "
                f"{m['blue_plate']}%); per piece: "
                + ", ".join(f"{k} {v}%" for k, v in m["blue_pieces"].items()) + ".",
                f"Glow layer: peak {m['glow']['peak']}, core {m['glow']['core']}%, halo {m['glow']['halo']}%, sat "
                f"{m['glow']['sat_core']}/{m['glow']['sat_halo']}, clipped {m['glow']['white']} px; the plate under it "
                f"L {m['glow']['under_L']} sat {m['glow']['under_sat']}. Px the light clips to white (day): {m['white_day']}. "
                f"Idle plate p5/p50/p95 {m['tonal_idle']['p5']}/{m['tonal_idle']['p50']}/{m['tonal_idle']['p95']}. "
                f"Motion: up to {m['motion_mean_dL']} L on the lit px.",
                "Vanilla for comparison (the study): plate under the glow L 29-65 sat 0.16-0.33; glow halo 77-88%, "
                "core 2-8%, sat ~1.0, peak 87-171, never clipped."])
    sh.section("The recipe", cfg["recipe"])
    sh.row([(on_ground(idle), ["idle (stopped: the plate)", "1x"]), (dy, ["working, day", "1x, frame 0"]),
            (nt, ["working, night", "1x, frame 0"]), (l0, ["the glow layer alone", "1x, additive, on black"])])
    sh.section("Each piece at 4x: idle, day, night")
    for label, im in (("idle", on_ground(idle)), ("day", dy), ("night", nt)):
        sh.row([(up(im.crop(bx), 4), [f"{n}, {label}"]) for n, bx in PIECES], gap=10)
    sh.section(f"The frame strip: all {nf} frames, working day, 1x (the whole row)")
    strip = Image.new("RGB", (4 * 544, ((nf + 3) // 4) * 192))
    for i, (w, li) in enumerate(zip(works, lights)):
        strip.paste(day(w, li), ((i % 4) * 544, (i // 4) * 192))
    sh.row([(strip, ["frames 0-15, left to right, top to bottom"])])
    sh.section("... and the column, port and slot at 2x, frames 0, 4, 8, 12 (day; then night)")
    z = (20, 8, 334, 176)
    sh.row([(up(day(works[i], lights[i]).crop(z), 2), [f"frame {i}"]) for i in (0, 4, 8, 12)], gap=8)
    sh.row([(up(night(works[i], lights[i]).crop(z), 2), [f"frame {i}, night"]) for i in (0, 4, 8, 12)], gap=8)

    pc = pool_crops()
    pdy, pnt = pool_recolour(look, pc["day"])
    src, ic = icon_recolour(look)
    sh.section("The pool shore and the radiant solution icon, recoloured to this look (a 2-D remap of the current "
               "art: the look's ramp on the art's own values -- a direction, not a redraw)")
    sh.row([(pc["day"], ["pool now, day (screenshot crop)"]), (pdy, ["pool in this look, day"]),
            (pc["night"], ["pool now, night"]), (pnt, ["pool in this look, night"])], gap=10)
    sh.row([(up(on_ground(src), 4), ["radiant solution icon now, 4x"]), (up(on_ground(ic), 4), ["in this look, 4x"]),
            (on_ground(src), ["now, 1x"]), (on_ground(ic), ["this look, 1x"])], gap=10)
    sh.render(os.path.join(CONCEPT, f"candidate-{look}-{cfg['name']}.png"))
    ic.save(os.path.join(HERE, f"icon-radiant-solution-{look}.png"))

    # GIFs: 1x day | night, and 2x day of the column, port and slot; 16 frames at ~14 fps as the RP
    frames1 = []
    frames2 = []
    for w, li in zip(works, lights):
        f = Image.new("RGB", (544, 384))
        f.paste(day(w, li), (0, 0))
        f.paste(night(w, li), (0, 192))
        frames1.append(f)
        frames2.append(up(day(w, li).crop(z), 2))
    for fr, nm in ((frames1, "1x"), (frames2, "2x")):
        fr[0].save(os.path.join(CONCEPT, f"candidate-{look}-{cfg['name']}-{nm}.gif"), save_all=True,
                   append_images=fr[1:], duration=1000 // 14, loop=0, optimize=False)
    return m


if __name__ == "__main__":
    allm = {}
    for look in sys.argv[3:] or ("A", "B", "C"):
        allm[look] = build(look)
        print(look, json.dumps(allm[look]))
    json.dump(allm, open(os.path.join(HERE, "candidate-measures.json"), "w"), indent=1)
