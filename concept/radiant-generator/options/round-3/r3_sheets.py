#!/usr/bin/env python3
"""Radiant Generator, round 3: variant sheets, GIFs, the porcelain comparison and the contact sheet.

  python3 r3_sheets.py <render-root> <ref-panel-dir> <out-dir>

<render-root>/<V>-hero, <V>-anim, <V>-reactor are r3_blockout.py's output for each variant
V (1, 2, 3); <ref-panel-dir> holds round-2/ref_sheet.py's working panels of the nuclear
reactor, fusion reactor and fusion generator. Writes into <out-dir>:

  <V>-<slug>.png        the variant: idle and working at 2x, key frames, 1x idle/working,
                        a 2x2 block, the stage-4 reactor block, the porcelain close-up,
                        the animation plan and every measurement
  <V>-<slug>-1x.gif     the working loop at game scale (64 px a tile)
  <V>-<slug>-2x.gif     the same at 2x
  porcelain.png         our masts' porcelain beside the Siderane turbine's round-2 bushings
  contact-sheet.png     the three working at game scale beside the nuclear reactor, fusion
                        reactor and fusion generator (working) and round 2's A and C
  measurements.json     every number on the sheets

Measured at game scale (the 2x renders halved): rise = tiles the opaque silhouette
(alpha > 200, so shadows excluded) reaches above the footprint's north edge; coverage =
share of the footprint's pixels it covers; blue = round 2's measure (pixels the light
changes, spill on metal included) and the emissive-only share (saturated bright blue).
Bloom stands in for the engine's light layer, as round 2.
"""
import json
import os
import sys
import textwrap

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageSequence

ROOT, REFP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__))
R2 = os.path.join(HERE, "..", "round-2")
TURBINE = os.path.expanduser("~/git/space-age-extended/.claude/worktrees/siderane-turbine-model/concept/"
                             "crust-turbine/model/compare-plates.png")
os.makedirs(OUT, exist_ok=True)

PPT = 64
GROUND = (74, 66, 58, 255)
BG = (30, 30, 30, 255)
GRID = (255, 255, 255, 30)
FOOT = (255, 255, 255, 110)
TEXT = (225, 220, 210, 255)
SUB = (165, 160, 150, 255)
MARK = (120, 200, 255, 255)
VANILLA = json.load(open(os.path.join(HERE, "vanilla-measured.json")))


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""), size)


SPEED = 0.4          # all three: 48 frames at 0.4 = 2.0 s

PORCELAIN = ("Masts: brown-glazed long-rod insulators, 2.3-3 tiles tall, big and small sheds alternating, an "
             "aluminium grading ring and a copper electrode on an arm at the head; they stand alone, on the "
             "ground or the fin bed, and carry an arc. The turbine's (round 2) are short white terminal "
             "bushings in a row of three on a brass box, carrying cables. So: dark against white, tall "
             "against stubby, alone and ringed against grouped and capped, light-bearing against cable-"
             "bearing. Neither needs to change; if Liam wants the two further apart, the turbine keeps "
             "white and nothing else in the mod uses brown glaze.")

VARIANTS = {
    "1": dict(
        slug="the-gyre-spire", name="THE GYRE SPIRE",
        layout="The spire rises out of the Gyre's core. A bowl at the centre of a radial fin bed (5x5, round, no "
               "plinth); the emitter core sits in the bowl inside the counter-rotating bands; the caged column "
               "stands on the core, held by four stays; four porcelain masts on the fin bed at the diagonals "
               "arc to it. Magazine south, converter east, spent-cell rack SW, coolant tank SE, junctions NW, "
               "lagged run and breaker NE.",
        pitch="Read: a lighthouse with a lightning rod through it -- beams sweep the fins low, arcs climb the "
              "column high, one vertical axis. Fuel in: teal magazine on the south edge, two ports, a chute "
              "into the core; spent cells to the rack SW. Blue: core through the band gaps, beams on the fins, "
              "the column through its cage, corona ring at the cap, arcs. Signature: two motions on one axis "
              "-- the bands' counter-rotation at the foot, the arcs walking up and down the column above it. "
              "Finish: lead bands edged in copper, teal stripe, grey fins, brown-glazed porcelain, lagged runs.",
        blue_rule="\"The light is the emitter core and the column standing on it: seen through the gaps of the "
                  "turning bands at its foot, as beams that sweep the radiator bed, between the bars of the "
                  "column's cage, and as arcs from the masts to the column. No other part glows.\"",
        plan=["structure (animation layer 1): 48 frames, animation_speed 0.4 (2.0 s). Moving parts only -- "
              "bands and gimbal, a crop round the core about 2.6 x 2.0 tiles; inner band +90 deg a loop, "
              "outer -60, gimbal +120 (4/6/3-fold, seamless)",
              "glow (draw_as_glow, same Animation): core, column bands climbing 2 a loop, corona, arcs; 48 "
              "frames, crop about 3.4 x 5 tiles (masts to column). Arcs drawn fresh each frame",
              "base: 1 frame repeated (repeat_count 48), the shadow 1 frame",
              "idle_animation: the same layers, 48 frames of one parked pose, no glow layer",
              "perceived_performance scales animation speed only: bands turn and arcs crawl faster under "
              "load; brightness does not scale (no working_visualisations on a burner-generator)",
              "the engine swaps idle for working at once: no start-up sequence"],
        reactor="Radiant Reactor 7x7 (block of four shown): each a bigger Gyre Spire with its own four masts; "
                "neighbours link by arcs jumping spire-top to spire-top across the gap, and a lit ground "
                "duct between their fin beds. The bonus shows as light crossing between buildings.",
        block_note="Square and symmetric bar the dressing: one plate serves four directions if the magazine "
                   "and converter are allowed to rotate with it."),
    "2": dict(
        slug="the-banded-spire", name="THE BANDED SPIRE",
        layout="The Gyre's bands become the Spire's cage. The Reaction Plant's banded drum (teal ring, slot "
               "ring) on a radial fin bed; on it a column caged by four tiers of shield rings, three plates "
               "each, the tiers turning in alternate directions; three porcelain masts (30/150/270 deg, none "
               "due north) arc into the gaps between tiers. Magazine SSE, converter east, rack SW, tank SE, "
               "junctions NW, lagged run and breaker NE.",
        pitch="Read: a tower that spins in layers -- the light breaks out through a lattice of gaps that "
              "opens and closes as the tiers pass each other, and the arcs step from gap to gap. Fuel in: "
              "teal magazine SSE, a chute up into the drum. Blue: the column through the moving lattice, slot "
              "ring round the drum, corona, arcs. Signature: the alternating tiers (the most mechanical motion "
              "of the three). Finish: the Reaction Plant's drum and teal ring, lead/collar tiers edged in "
              "copper, brown-glazed porcelain with lagged feeds.",
        blue_rule="\"The light is the column, seen through the gaps between the turning tiers of its cage, "
                  "the ring of slots round the drum, and the arcs from the masts into the cage. No other part "
                  "glows.\"",
        plan=["structure: 48 frames, animation_speed 0.4 (2.0 s); each tier +/-120 deg a loop (3-fold, "
              "seamless); crop about 1.4 x 4.5 tiles -- the narrowest moving crop of the three",
              "glow: column bands (2 climbs a loop), lattice leaks, slots, corona, arcs; 48 frames; crop about "
              "3.8 x 5 tiles",
              "base: 1 frame repeated; idle_animation: tiers parked out of step, dark",
              "perceived_performance: tiers turn and arcs step faster under load",
              "a cheap variant: the moving crop is tall and thin"],
        reactor="Radiant Reactor 7x7, five tiers: the masts move to the shared edges -- one mast stands on "
                "each edge between two reactors and arcs into both; outer edges keep a mast of their own. "
                "The bonus shows as shared masts: a lone reactor has fewer.",
        block_note="Three masts break the symmetry: one plate, rotations not needed (masts are dressing)."),
    "3": dict(
        slug="the-crown", name="THE CROWN",
        layout="Masts at the corners arcing inward. The Gyre whole and low at the centre (bowl, core, "
               "counter-rotating bands, four pylons and crown bearing), a short caged needle on the crown with "
               "a grading-ringed terminal; four porcelain masts at the corners lean in 20 deg and arc onto the "
               "needle -- the spire is drawn in light. Fin bed broken N/S/E/W for magazine S, converter E, tank "
               "W, junction and lagged run N.",
        pitch="Read: a crown of lightning over a lighthouse -- four arcs meet over the core, a tent of light "
              "taller than any metal on it. Fuel in: teal magazine south, a chute into the core. Blue: the "
              "core through the bands, beams on the fins, the needle, arcs. Signature: four arcs converging "
              "and wandering on the needle while the bands turn below. Finish: the Gyre's lead and copper, "
              "four big brown-glazed masts framing the corners (breaks the square: the silhouette is a star).",
        blue_rule="\"The light is the emitter core, seen through the gaps of its turning bands and as beams on "
                  "the radiator bed, the needle over it, and the arcs from the corner masts to the needle. No "
                  "other part glows.\"",
        plan=["structure: 48 frames, animation_speed 0.4 (2.0 s); bands and gimbal as the Gyre; crop about 2.0 x "
              "2.2 tiles",
              "glow: core pulse, needle, arcs; 48 frames; crop nearly the whole sprite (corner to corner), "
              "about 4.4 x 4.2 tiles -- the arcs make the glow sheet the largest of the three",
              "base: 1 frame repeated; idle_animation: bands parked, needle and core dark, no arcs",
              "perceived_performance: bands and arcs faster under load",
              "lowest metal of the three: the tallest thing is a mast head, so the rise is the smallest"],
        reactor="Radiant Reactor 7x7: where four reactors meet, their inner corner masts become one shared "
                "mast, taller, arcing into all four needles; edges between two reactors carry a lit ground "
                "duct. A block reads as a lattice of light; a lone reactor has four masts of its own.",
        block_note="Corner masts sit inside the footprint, so generators pack edge to edge; in a block the "
                   "masts of four neighbours stand in a cluster at each shared corner."),
}


# ---------------------------------------------------------------- helpers (round 2's)

def info(v, mode):
    return json.load(open(f"{ROOT}/{v}-{mode}/info.json"))


def load(path, k):
    im = Image.open(path).convert("RGBa")
    if k != 1:
        im = im.resize((im.width // k, im.height // k), Image.LANCZOS)
    return im.convert("RGBA")


def bloom(rgb, scale=1.0):
    r, g, b = rgb.convert("RGB").split()
    hot = ImageChops.subtract(b, r)
    m = Image.eval(hot, lambda v: 0 if v < 60 else min(255, (v - 60) * 3))
    bright = Image.eval(b, lambda v: 0 if v < 150 else min(255, (v - 150) * 3))
    m = ImageChops.multiply(m, bright)
    src = Image.composite(rgb.convert("RGB"), Image.new("RGB", rgb.size), m)
    near = src.filter(ImageFilter.GaussianBlur(3 * scale))
    far = src.filter(ImageFilter.GaussianBlur(9 * scale))
    out = ImageChops.add(rgb.convert("RGB"), Image.eval(near, lambda v: int(v * 0.55)))
    out = ImageChops.add(out, Image.eval(far, lambda v: int(v * 0.45)))
    return out.convert("RGBA")


def ground(w, h, origin, foot, ppt=PPT, outline=True):
    W, H = int(w * ppt), int(h * ppt)
    g = Image.new("RGBA", (W, H), GROUND)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    ox, oy = origin[0] * ppt, origin[1] * ppt
    x0, y0 = ox - foot[0] / 2 * ppt, oy - foot[1] / 2 * ppt
    x = x0 % ppt
    while x < W:
        dr.line([(x, 0), (x, H)], fill=GRID)
        x += ppt
    y = y0 % ppt
    while y < H:
        dr.line([(0, y), (W, y)], fill=GRID)
        y += ppt
    if outline and foot[0]:
        dr.rectangle([x0, y0, x0 + foot[0] * ppt, y0 + foot[1] * ppt], outline=FOOT)
    g.alpha_composite(ov)
    return g


def paste(dst, im, x, y):
    x, y = round(x), round(y)
    cx, cy = max(0, -x), max(0, -y)
    dst.alpha_composite(im.crop((cx, cy, im.width, im.height)), (x + cx, y + cy))


def panel(sprites, inf, scale, pad=(0.8, 0.9, 2.2, 0.6), glow=True):
    fw, fh = inf["foot"]
    ppt = PPT * scale
    ox, oy = inf["origin"]
    top = fh / 2 + pad[1]
    w = fw + pad[0] + pad[2]
    h = top + fh / 2 + pad[3]
    origin = (pad[0] + fw / 2, top)
    g = ground(w, h, origin, (fw, fh), ppt)
    for s in sprites:
        paste(g, s, origin[0] * ppt - ox * ppt, origin[1] * ppt - oy * ppt)
    return bloom(g, scale) if glow else g


def label(img, xy, text, size=12, fill=TEXT, bold=False):
    ImageDraw.Draw(img).text(xy, text, font=font(size, bold), fill=fill)


def row(panels, labels, gap=12, top=20):
    W = sum(p.width for p in panels) + gap * (len(panels) + 1)
    H = max(p.height for p in panels) + top + gap
    out = Image.new("RGBA", (W, H), BG)
    x = gap
    for p, t in zip(panels, labels):
        out.alpha_composite(p, (x, top))
        label(out, (x + 2, 3), t, 12, SUB)
        x += p.width + gap
    return out


def stack_v(rows, gap=8, width=None):
    W = width or max(r.width for r in rows)
    out = Image.new("RGBA", (W, sum(r.height for r in rows) + gap * (len(rows) - 1)), BG)
    y = 0
    for r in rows:
        out.alpha_composite(r, (0, y))
        y += r.height + gap
    return out


def text_block(width, paras, size=13):
    f, fb = font(size), font(size, True)
    chars = int(width / (size * 0.56))
    lines = []
    for head, body in paras:
        lines.append((head, True))
        for para in body if isinstance(body, list) else [body]:
            for i, l in enumerate(textwrap.wrap(para, chars - 3)):
                lines.append((("- " if isinstance(body, list) and i == 0 else ("  " if isinstance(body, list) else ""))
                              + l, False))
        lines.append(("", False))
    out = Image.new("RGBA", (width, 10 + int(size * 1.45) * len(lines)), BG)
    dr = ImageDraw.Draw(out)
    y = 6
    for t, bold in lines:
        dr.text((12, y), t, font=fb if bold else f, fill=TEXT if bold else SUB)
        y += int(size * 1.45)
    return out


def solid(im):
    return im.split()[3].point(lambda v: 255 if v > 200 else 0)


def lit_fraction(work, idle):
    """Round 2's measure: share of solid pixels the light changes (bluer or brighter by > 40)."""
    db = ImageChops.subtract(work.split()[2], idle.split()[2])
    dl = ImageChops.subtract(work.convert("L"), idle.convert("L"))
    d = ImageChops.lighter(db, dl).point(lambda v: 255 if v > 40 else 0)
    s = solid(work)
    return ImageChops.multiply(d, s).histogram()[255] / max(1, s.histogram()[255])


def emissive_fraction(work):
    """Saturated bright blue only (b > 170 and b - r > 70): the glow layer's share, roughly."""
    r, g, b, _ = work.split()
    m1 = b.point(lambda v: 255 if v > 170 else 0)
    m2 = ImageChops.subtract(b, r).point(lambda v: 255 if v > 70 else 0)
    s = solid(work)
    return ImageChops.multiply(ImageChops.multiply(m1, m2), s).histogram()[255] / max(1, s.histogram()[255])


def rise_and_cover(im, inf):
    """At game scale: tiles above the north edge, share of the footprint covered."""
    a = solid(im)
    fw, fh = inf["foot"]
    ox, oy = inf["origin"][0] * PPT, inf["origin"][1] * PPT
    top = a.getbbox()[1]
    rise = (oy - fh / 2 * PPT - top) / PPT
    box = a.crop((round(ox - fw / 2 * PPT), round(oy - fh / 2 * PPT), round(ox + fw / 2 * PPT),
                  round(oy + fh / 2 * PPT)))
    return rise, box.histogram()[255] / (box.width * box.height)


def gif(frames, path, ms):
    rgb = [f.convert("RGB") for f in frames]
    sample = Image.new("RGB", (rgb[0].width, rgb[0].height * 4))
    for j, k in enumerate(range(0, len(rgb), max(1, len(rgb) // 4))):
        if j < 4:
            sample.paste(rgb[k], (0, j * rgb[0].height))
    pal = sample.quantize(128, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in rgb]
    q[0].save(path, save_all=True, append_images=q[1:], duration=ms, loop=0, optimize=False, disposal=1)


def mark_rise(p, inf, scale, pad, rise):
    """Draw the rise bar on a panel made by panel() with the same pad."""
    ppt = PPT * scale
    fw, fh = inf["foot"]
    x = (pad[0] + fw) * ppt + 8
    ny = (pad[1]) * ppt
    ty = ny - rise * ppt
    dr = ImageDraw.Draw(p)
    dr.line([(x, ty), (x, ny)], fill=MARK, width=2)
    for y in (ty, ny):
        dr.line([(x - 4, y), (x + 4, y)], fill=MARK, width=2)
    dr.text((x + 6, (ty + ny) / 2 - 7), "%+.2f t" % rise, font=font(11), fill=MARK)


# ---------------------------------------------------------------- per variant

meas = {"vanilla": VANILLA}
contact = []
for V, o in VARIANTS.items():
    ih, ia, ir = info(V, "hero"), info(V, "anim"), info(V, "reactor")
    fw, fh = ih["foot"]
    N = ia["frames"]
    hero_w2 = load(f"{ROOT}/{V}-hero/working.png", 2)
    hero_i2 = load(f"{ROOT}/{V}-hero/idle.png", 2)
    frames2 = [load(f"{ROOT}/{V}-anim/f{i:03d}.png", 1) for i in range(N)]
    frames1 = [f.resize((f.width // 2, f.height // 2), Image.LANCZOS) for f in frames2]
    idle1 = load(f"{ROOT}/{V}-anim/idle.png", 2)
    reactor1 = load(f"{ROOT}/{V}-reactor/reactor.png", 2)

    rises, covers = zip(*(rise_and_cover(f, ia) for f in frames1))
    rise_i, cover_i = rise_and_cover(idle1, ia)
    lit = [lit_fraction(f, idle1) for f in frames1]
    emi = [emissive_fraction(f) for f in frames1]
    m = dict(name=o["name"], footprint=f"{fw}x{fh}", frames=N, animation_speed=SPEED,
             loop_seconds=round(N / (60 * SPEED), 2), rise_tiles_max=round(max(rises), 2),
             rise_tiles_idle=round(rise_i, 2), coverage_pct=round(100 * cover_i, 1),
             blue_lit_mean_pct=round(100 * sum(lit) / N, 1), blue_lit_min_pct=round(100 * min(lit), 1),
             blue_lit_max_pct=round(100 * max(lit), 1), blue_emissive_mean_pct=round(100 * sum(emi) / N, 1),
             reactor=f"{ir['pitch']:g}x{ir['pitch']:g}")
    ms = round(1000 / (60 * SPEED))
    m["gif_frame_ms"] = ms
    pad = (0.8, 0.9, 2.2, 0.6)
    gpad = (0.5, 0.6, 1.5, 0.4)                       # tighter for the GIFs (1x under 5 MB)
    g1 = [panel([f], ia, 1, gpad) for f in frames1]
    g2 = [panel([f], ia, 2, gpad) for f in frames2]
    gif(g1, f"{OUT}/{V}-{o['slug']}-1x.gif", ms)
    gif(g2, f"{OUT}/{V}-{o['slug']}-2x.gif", ms)
    m["gif_1x_bytes"] = os.path.getsize(f"{OUT}/{V}-{o['slug']}-1x.gif")
    m["gif_2x_bytes"] = os.path.getsize(f"{OUT}/{V}-{o['slug']}-2x.gif")
    meas[V] = m

    hero_i = panel([hero_i2], ih, 2, pad)
    hero_w = panel([hero_w2], ih, 2, pad)
    mark_rise(hero_w, ih, 2, pad, m["rise_tiles_max"])
    keys = [int(N * t) for t in (0, 0.25, 0.5, 0.75)]
    kp = (0.4, 0.9, 1.0, 0.3)
    keyp = [panel([frames1[k]], ia, 1, kp) for k in keys]
    r1 = row([hero_i, hero_w], ["idle (off) -- 2x", f"working, frame 0 -- 2x  (rise {m['rise_tiles_max']:+.2f} t)"])
    r1b = row(keyp, [f"frame {k}/{N} -- 1x" for k in keys])
    w1 = panel([frames1[0]], ia, 1, pad)
    i1 = panel([idle1], ia, 1, pad)
    # a 2x2 block edge to edge, frames out of step
    bw, bh = 2 * fw + 3.0, 2 * fh + 2.2
    blk = ground(bw, bh, (1 + fw / 2, 1.4 + fh / 2), (0, 0))
    ImageDraw.Draw(blk).rectangle([PPT, 1.4 * PPT, (1 + 2 * fw) * PPT, (1.4 + 2 * fh) * PPT], outline=FOOT)
    for j in range(2):
        for i in range(2):
            f = frames1[(i * 7 + j * 19) % N]
            ox, oy = (1 + fw / 2 + i * fw) * PPT, (1.4 + fh / 2 + j * fh) * PPT
            paste(blk, f, ox - ia["origin"][0] * PPT, oy - ia["origin"][1] * PPT)
    blk = bloom(blk)
    rp = ir["pitch"]
    rpan = ground(ir["canvas"][0], ir["canvas"][1], ir["origin"], (2 * rp, 2 * rp))
    paste(rpan, reactor1, 0, 0)
    rpan = bloom(rpan)
    rpan_h = rpan.resize((rpan.width * 3 // 4, rpan.height * 3 // 4), Image.LANCZOS)
    r2 = row([i1, w1, blk], ["idle, 1x", "working, 1x", "a block of 4, 1x (frames out of step)"])
    r3 = row([rpan_h], [f"stage 4: Radiant Reactor, {rp:g}x{rp:g}, block of 4 -- 3/4 scale"])
    W = max(r1.width, r1b.width, r2.width, r3.width, 1500)
    facts = (f"Footprint 5x5.  Rise above the north edge: {m['rise_tiles_max']:+.2f} tiles working (vanilla: "
             f"nuclear {VANILLA['nuclear reactor 5x5']['rise_tiles']:+.2f}, fusion reactor "
             f"{VANILLA['fusion reactor 6x6']['rise_tiles']:+.2f}, refinery "
             f"{VANILLA['oil refinery 5x5 (north)']['rise_tiles']:+.2f}).  Coverage: {m['coverage_pct']}% of the "
             f"footprint (nuclear {VANILLA['nuclear reactor 5x5']['coverage_pct']}%, refinery "
             f"{VANILLA['oil refinery 5x5 (north)']['coverage_pct']}%, fusion reactor "
             f"{VANILLA['fusion reactor 6x6']['coverage_pct']}%).  Blue: {m['blue_lit_mean_pct']}% of the "
             f"building's pixels lit, mean over the loop ({m['blue_lit_min_pct']}-{m['blue_lit_max_pct']}%; light "
             f"spill on metal included, round 2's measure); emissive blue alone {m['blue_emissive_mean_pct']}%.  "
             f"Loop: {N} frames at animation_speed {SPEED} = {m['loop_seconds']} s.  GIF 1x "
             f"{m['gif_1x_bytes'] / 1e6:.1f} MB.")
    txt = text_block(W, [("LAYOUT", o["layout"]), ("PITCH", o["pitch"]),
                         ("LIGHT RULE -- spec 3.1/3.3 wording this variant needs", o["blue_rule"]),
                         ("ANIMATION PLAN (burner-generator: animation + idle_animation only; all glow is "
                          "draw_as_glow layers inside them)", o["plan"]),
                         ("STAGE 4: THE RADIANT REACTOR", o["reactor"]), ("TILING", o["block_note"]),
                         ("THE MASTS' PORCELAIN", PORCELAIN), ("MEASURED", facts)])
    head = Image.new("RGBA", (W, 54), BG)
    label(head, (10, 6), f"RADIANT GENERATOR, ROUND 3 -- VARIANT {V}: {o['name']} (5x5)", 22, bold=True)
    label(head, (10, 34), "Lit Blender blockout (layered finish, emission + core lights, GPU; ChatGPT was not "
          "reachable). Not adopted. 64 px a tile at 1x. The loop is in the GIFs beside this sheet.", 13, SUB)
    sheet = stack_v([head, r1, r1b, r2, r3, txt], width=W)
    sheet.save(f"{OUT}/{V}-{o['slug']}.png")
    contact.append((f"{V} {o['name'].lower()}, 5x5, working", w1, rpan))
    print(V, m)

# ---------------------------------------------------------------- porcelain comparison

t = Image.open(TURBINE).convert("RGBA")
turb = t.crop((1110, 600, 1380, 800))                         # round 2, horizontal 2x: the bushings
ours = []
for V in VARIANTS:
    h2 = load(f"{ROOT}/{V}-hero/working.png", 2)
    ours.append(h2)
ih = info("1", "hero")
ppt2 = 128
ox, oy = ih["origin"][0] * ppt2, ih["origin"][1] * ppt2
# variant 1's south-west mast at 2x
m1 = ours[0].crop((round(ox - 2.3 * ppt2), round(oy - 1.85 * ppt2), round(ox - 0.2 * ppt2), round(oy + 1.55 * ppt2)))
m1g = Image.new("RGBA", m1.size, GROUND)
m1g.alpha_composite(m1)
ih3 = info("3", "hero")
ox3, oy3 = ih3["origin"][0] * ppt2, ih3["origin"][1] * ppt2
m3 = ours[2].crop((round(ox3 - 2.5 * ppt2), round(oy3 - 1.4 * ppt2), round(ox3 - 0.6 * ppt2), round(oy3 + 2.5 * ppt2)))
m3g = Image.new("RGBA", m3.size, GROUND)
m3g.alpha_composite(m3)
pr = row([bloom(m1g, 2), bloom(m3g, 2), turb], ["ours: variant 1 mast, 2x", "ours: variant 3 corner mast, 2x",
                                                "turbine round 2 bushings, 2x"])
txt = text_block(pr.width, [("THE MASTS' PORCELAIN AGAINST THE TURBINE'S", PORCELAIN)])
hd = Image.new("RGBA", (pr.width, 34), BG)
label(hd, (10, 8), "RADIANT GENERATOR, ROUND 3 -- PORCELAIN: OURS AND THE TURBINE'S", 16, bold=True)
stack_v([hd, pr, txt]).save(f"{OUT}/porcelain.png")

# ---------------------------------------------------------------- contact sheet

def gif_frame0(path):
    return next(ImageSequence.Iterator(Image.open(path))).convert("RGBA")


refs = [
    ("vanilla nuclear reactor 5x5, working", Image.open(f"{REFP}/nuclear-reactor-working.png").convert("RGBA")),
    ("fusion reactor 6x6, working", Image.open(f"{REFP}/fusion-reactor-working.png").convert("RGBA")),
    ("fusion generator 3x5, working", Image.open(f"{REFP}/fusion-generator-working.png").convert("RGBA")),
    ("round 2: A the gyre, 4x4", gif_frame0(os.path.join(R2, "A-the-gyre-1x.gif"))),
    ("round 2: C the arc spire, 3x3", gif_frame0(os.path.join(R2, "C-the-arc-spire-1x.gif"))),
]
row_r = row([p for _, p in refs], [n for n, _ in refs])
row_o = row([p for _, p, _ in contact], [f"{n}  (rise {meas[n[0]]['rise_tiles_max']:+.2f} t, cover "
                                         f"{meas[n[0]]['coverage_pct']}%)" for n, _, _ in contact])
half = [(f"{n[0]}: reactor block, 4 x 7x7 -- HALF scale", r.resize((r.width // 2, r.height // 2), Image.LANCZOS))
        for n, _, r in contact]
row_x = row([p for _, p in half], [n for n, _ in half])
W = max(row_r.width, row_o.width, row_x.width)
head = Image.new("RGBA", (W, 52), BG)
label(head, (10, 6), "RADIANT GENERATOR, ROUND 3 -- THE GYRE AND THE ARC SPIRE AT 5x5, AT GAME SCALE", 20, bold=True)
label(head, (10, 32), "64 px a tile. Top: vanilla working, and round 2's A and C. Middle: the three variants, working, "
      "frame 0, shadows and bloom. Bottom: each variant's stage-4 Radiant Reactor, a block of four, half scale. "
      "Lit Blender blockouts.", 12, SUB)
stack_v([head, row_r, row_o, row_x], width=W).save(f"{OUT}/contact-sheet.png")
json.dump(meas, open(f"{OUT}/measurements.json", "w"), indent=1)
print(f"{OUT}/contact-sheet.png")
