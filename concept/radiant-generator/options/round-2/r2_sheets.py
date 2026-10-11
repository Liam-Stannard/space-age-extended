#!/usr/bin/env python3
"""Radiant Generator, round 2: option sheets, animation GIFs and the contact sheet.

  python3 r2_sheets.py <render-root> <ref-panel-dir> <out-dir>

<render-root>/r/<X>-hero, <X>-anim and <X>-reactor are r2_blockout.py's output for
each option X; <ref-panel-dir> holds ref_sheet.py's working panels of the nuclear
reactor and the fusion reactor and generator. Writes into <out-dir>:

  <X>-<slug>.png           the option: pitch, hero idle and working at 2x, key frames,
                           1x idle and working, a block of them, the reactor in the same
                           language, the animation plan and the measurements
  <X>-<slug>-1x.gif        the signature loop, working, at game scale (64 px a tile)
  <X>-<slug>-2x.gif        the same at 2x
  contact-sheet.png        every option working at game scale beside vanilla's nuclear
                           reactor, fusion reactor and fusion generator working, the steam
                           engine, the Reaction Plant and the Radiant Generator now (v2);
                           below, the five reactor blocks at half scale
  measurements.json        every number on the sheets

Bloom: the renders carry the blue as emission and its light on the metal; the soft
bloom added here stands in for the engine's light layer (draw_as_light / the entity
light), which a plate cannot carry. It is applied the same way to every option.
"""
import json
import os
import sys
import textwrap

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT, REFP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
FD = os.environ.get("FACTORIO_DATA", os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
os.makedirs(OUT, exist_ok=True)

PPT = 64
GROUND = (74, 66, 58, 255)
BG = (30, 30, 30, 255)
GRID = (255, 255, 255, 30)
FOOT = (255, 255, 255, 110)
TEXT = (225, 220, 210, 255)
SUB = (165, 160, 150, 255)
ACC = (130, 185, 255, 255)


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""), size)


# ---------------------------------------------------------------- the options

OPTIONS = {
    "A": dict(
        slug="the-gyre", name="THE GYRE", speed=0.25,
        pitch="An emitter core hung in a cage of counter-rotating shield bands, on a radial radiator bed. "
              "Read: a lighthouse in the corridor -- the light is the core, and it leaks out through the gaps "
              "between the turning bands, sweeping four beams across the fins. Fuel in: the teal magazine on the "
              "south side, two ports, a chute up the spindle; spent cells drop to the lead drawer beside it. "
              "Signature: the counter-rotation (inner band +90 deg a loop, outer -60, the gimbal ring precessing). "
              "Finish: lead bands edged in copper, a teal stripe on the outer band, grey radial fins, bolted bowl.",
        blue="The core, open to the sky inside the crown, and four beams through the band gaps. Spec 3.1/3.3: "
             "\"the light is the emitter core, seen from above inside its turning shield bands, and the beams "
             "that leak between the bands onto the radiator bed; nowhere else.\"",
        plan=["structure + bands: 48 frames, animation_speed 0.25 (3.2 s loop); bands have 4- and 6-fold "
              "symmetry, so 90 / 60 deg a loop is seamless",
              "glow (draw_as_glow, additive): core and the band faces it lights, 48 frames, two pulses a loop",
              "light (draw_as_light): the beam sweep on the fins and ground, 48 frames",
              "idle_animation: the same 48 frames' count, one frame repeated: bands parked, core dark",
              "with output: perceived_performance -- the bands spin faster under load",
              "reactor adds: 6x6, a third band, beams crossing into its neighbours, lit bridges"],
        family="Centrifuge: the same lead bands on a horizontal drum, spinning fast. Reactor: the Gyre at 6x6 "
               "with a third band, bridged to its neighbours.",
        tiling="4x4, square and symmetric: one plate serves all four directions. Packs in any grid; magazine "
               "south, cables north, so rows share a belt.",
        block=(2, 2)),
    "B": dict(
        slug="the-lotus", name="THE LOTUS", speed=0.2,
        pitch="Eight armoured collector petals round a radiant pool. Off, they close into a shielded bud; "
              "burning, they open and breathe, their polished inner faces lit blue by the pool and the "
              "emitter spindle. Read: a machine that opens to take the light -- you can tell a fuelled "
              "generator from across the base. Fuel in: the teal magazine at the south-east corner, under the "
              "skirt to the pool. Signature: the bud opening, and the slow breathing ripple round the petals. "
              "Finish: lead petal backs ribbed as radiators (the petals are the radiators), polished faces, "
              "a bolted skirt with gearbox housings at each hinge -- no rams.",
        blue="The most of the five: pool, spindle and the petals' inner faces, all open to the sky when "
             "working, all hidden when idle. Spec 3.1/3.3: \"the light is the radiant pool and the emitter "
             "spindle, seen through the open petals and reflected on their collector faces; when the "
             "generator is idle the petals close over it and no light shows.\"",
        plan=["structure (petals): 32 frames, animation_speed 0.2 (2.7 s loop); open angle 38 +/- 14 deg "
              "with a ripple travelling round the eight",
              "glow: pool, spindle, lit petal faces, 32 frames, brightest at full open",
              "idle_animation: the closed bud, one frame repeated to 32",
              "no transition: the engine swaps animation for idle at once, so the bud snaps open "
              "(as vanilla's lights snap on) -- a startup cycle would need a script",
              "with output: perceived_performance -- faster breathing under load",
              "reactor adds: 6x6, twelve petals, lit bridges to its neighbours"],
        family="Centrifuge: a smaller bud on a spinning collar. Reactor: twelve petals at 6x6, opening on "
               "a block of four as one field of light.",
        tiling="4x4, symmetric: one plate. Petals stay inside the footprint even open, so blocks pack "
               "edge to edge.",
        block=(2, 2)),
    "C": dict(
        slug="the-arc-spire", name="THE ARC SPIRE", speed=0.5,
        pitch="A column of radiant light in a lead cage on a banded drum -- the Reaction Plant's drum and "
              "teal roof ring -- with three insulator masts round it. Blue arcs crawl from the masts to the "
              "column and bright bands climb it. Read: the tallest, most vertical of the five; a spark of "
              "life on a dead world. Fuel in: the teal hatch on the drum's south face. Signature: the arcs -- "
              "irregular, never quite repeating to the eye. Finish: stacked ceramic insulators, lead cage "
              "and collars, copper electrode balls, the plant's banded drum.",
        blue="The column through its cage, a corona ring at its cap, the arcs, and slots round the drum. "
             "Spec 3.1/3.3: \"the light is the column, seen between the bars of its cage, the arcs that "
             "jump to its masts and a ring of slots in the drum.\"",
        plan=["structure: 1 frame (nothing mechanical moves)",
              "glow: column bands (2 climbs a loop) and arcs, 24 frames, animation_speed 0.5 (0.8 s loop); "
              "arcs are drawn fresh each frame, walking up and down the column in three phases",
              "light: a flicker on the masts and ground, 24 frames",
              "idle_animation: dark column, no arcs, one frame repeated",
              "with output: perceived_performance -- the arcs crawl faster",
              "reactor adds: four spires and arcs jumping between neighbouring reactors -- the neighbour "
              "bonus as light"],
        family="Centrifuge: the same drum and cage with a spinning rotor inside. Reactor: a crown of "
               "spires; arcs bridge the gap to each neighbour.",
        tiling="3x3, symmetric: one plate. Tall (see height), so a block reads as a forest of spires; "
               "shadows fall long to the east.",
        block=(3, 2)),
    "D": dict(
        slug="the-conduit", name="THE CONDUIT", speed=0.4,
        pitch="A domed emitter vault at one end; radiant light runs in pulses through three clamped glass "
              "ducts into the converter's coils at the other -- the fusion generator's language, our "
              "colour. Read: power visibly going somewhere. Fuel in: the teal magazine on the vault's west "
              "flank, a lead drawer east. Signature: the flow, pulse after pulse along the ducts, the coils "
              "flashing as each lands. Finish: a lead dome ribbed in copper, ducts in armoured cradles with "
              "lead clamps, radiator flanks, the converter finned on top.",
        blue="Through the duct windows between the clamps, the vault's oculus ring and slots, and the "
             "converter coils. Spec 3.1/3.3: \"the light is seen through windows in three clamped ducts "
             "and at the vault's oculus and slots, and it moves: pulses from the vault to the converter.\"",
        plan=["structure: 1 frame per direction -- only light moves, the cheapest sheet of the five",
              "glow: duct pulses, oculus, slots and coils, 32 frames, animation_speed 0.4 (1.3 s loop); "
              "one pulse spacing a loop, so it is seamless",
              "idle_animation: dark ducts, one frame repeated",
              "two directions (3x5): vertical and horizontal plates, as v2",
              "with output: perceived_performance -- pulses run faster under load",
              "reactor adds: a 5x5 hub vault with ducts out of all four sides that join its neighbours' "
              "ducts, so light runs from reactor to reactor"],
        family="Centrifuge: a vault with ducts in and out. Reactor: the hub vault, ducts on all four "
               "sides, joining neighbours like the fusion reactor's plasma pipes.",
        tiling="3x5, as v2: rows side by side, magazine south-west, cables north.",
        block=(4, 1)),
    "E": dict(
        slug="the-feeder", name="THE FEEDER", speed=0.25,
        pitch="A gantry crane over a shielded well. Each cycle it takes a fuel cell from the magazine "
              "rack, runs down the rails, lowers the cell through the opening iris, and the well flares; "
              "the iris closes to a steady ring of light. Read: refuelling made a ritual -- you see the "
              "fuel go in. Fuel in: the rack under the teal lid at the north end. Signature: the carry and "
              "the flare. Finish: rails with a copper conductor strip on lead A-frames, a teal hoist, "
              "banded well, finned converter at the south.",
        blue="A steady ring of slots round the well; the well's mouth when the iris opens; the flare. "
             "Spec 3.1/3.3: \"the light shows through the slot ring round the well, and through its mouth "
             "while the iris is open to take a cell.\"",
        plan=["structure: 64 frames, animation_speed 0.25 (4.3 s loop): pick 0-8, carry 8-24, iris "
              "24-28, lower 28-36, flare 33-44, iris shut 44-48, return 48-64",
              "glow: slots, pool and flare, 64 frames",
              "idle_animation: bridge parked at the magazine, iris shut, dark",
              "decorative: the loop does not track real fuel (a cell lasts 50 s); the engine cannot sync it",
              "the costliest sheet: the bridge crosses the whole building, so every frame is full-size, "
              "x2 directions",
              "reactor adds: a polar crane turning over four wells in a ringed pit"],
        family="Centrifuge: the same rails and hoist feeding a spinning drum. Reactor: a polar crane "
               "over four wells.",
        tiling="3x5, as v2. Rails run the length, so rows side by side read as one long crane hall.",
        block=(4, 1)),
}


# ---------------------------------------------------------------- image helpers

def info(x, mode):
    return json.load(open(f"{ROOT}/r/{x}-{mode}/info.json"))


def load(path, k):
    """A render downsampled by k, premultiplied."""
    im = Image.open(path).convert("RGBa")
    if k != 1:
        im = im.resize((im.width // k, im.height // k), Image.LANCZOS)
    return im.convert("RGBA")


def bloom(rgb, scale=1.0):
    """Soft light round the saturated radiant blue and the white-hot cores."""
    r, g, b = rgb.convert("RGB").split()
    hot = ImageChops.subtract(b, r)                     # how much bluer than red
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


def panel(sprites, inf, scale, pad=(0.8, 0.8, 1.6, 0.6), foot_outline=True, glow=True):
    """Sprites (all from renders with info inf) on a ground just big enough; pad: left, top, right, bottom tiles."""
    fw, fh = inf["foot"]
    ppt = PPT * scale
    cw, ch = inf["canvas"]
    ox, oy = inf["origin"]
    # how far the content reaches, in tiles from the origin
    top = max(fh / 2 + pad[1], max(_reach_up(s, inf, scale) for s in sprites) + 0.25)
    w = fw + pad[0] + pad[2]
    h = top + fh / 2 + pad[3]
    origin = (pad[0] + fw / 2, top)
    g = ground(w, h, origin, (fw, fh), ppt, foot_outline)
    for s in sprites:
        paste(g, s, origin[0] * ppt - ox * ppt, origin[1] * ppt - oy * ppt)
    return bloom(g, scale) if glow else g


def _reach_up(sprite, inf, scale):
    a = sprite.split()[3].point(lambda v: 255 if v > 200 else 0)
    bb = a.getbbox()
    return inf["origin"][1] - bb[1] / (PPT * scale) if bb else 0


def label(img, xy, text, size=12, fill=TEXT, bold=False):
    ImageDraw.Draw(img).text(xy, text, font=font(size, bold), fill=fill)


def row(panels, labels, gap=12, top=20, bg=BG):
    W = sum(p.width for p in panels) + gap * (len(panels) + 1)
    H = max(p.height for p in panels) + top + gap
    out = Image.new("RGBA", (W, H), bg)
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
    f = font(size)
    fb = font(size, True)
    chars = int(width / (size * 0.56))
    lines = []
    for head, body in paras:
        lines.append((head, True))
        for para in body if isinstance(body, list) else [body]:
            wrapped = textwrap.wrap(para, chars)
            for i, l in enumerate(wrapped):
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


def lit_fraction(work, idle):
    """Share of the building's solid pixels the light changes (bluer or brighter by > 40)."""
    w, i = work.convert("RGBA"), idle.convert("RGBA")
    wa = w.split()[3]
    db = ImageChops.subtract(w.split()[2], i.split()[2])
    dl = ImageChops.subtract(w.convert("L"), i.convert("L"))
    d = ImageChops.lighter(db, dl).point(lambda v: 255 if v > 40 else 0)
    solid = wa.point(lambda v: 255 if v > 200 else 0)
    n_solid = solid.histogram()[255]
    n_lit = ImageChops.multiply(d, solid).histogram()[255]
    return n_lit / max(1, n_solid)


def gif(frames, path, ms):
    """Frames (RGBA on ground) -> a looping GIF with one palette for the whole loop."""
    rgb = [f.convert("RGB") for f in frames]
    sample = Image.new("RGB", (rgb[0].width, rgb[0].height * min(4, len(rgb))))
    for j, k in enumerate(range(0, len(rgb), max(1, len(rgb) // 4))):
        if j < 4:
            sample.paste(rgb[k], (0, j * rgb[0].height))
    pal = sample.quantize(255, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in rgb]
    q[0].save(path, save_all=True, append_images=q[1:], duration=ms, loop=0, optimize=False, disposal=1)


# ---------------------------------------------------------------- per option

meas = {}
contact_opts = []
reactor_thumbs = []
for X, o in OPTIONS.items():
    ih, ia, ir = info(X, "hero"), info(X, "anim"), info(X, "reactor")
    fw, fh = ih["foot"]
    N = ia["frames"]
    hero_w2 = load(f"{ROOT}/r/{X}-hero/working.png", 2)
    hero_i2 = load(f"{ROOT}/r/{X}-hero/idle.png", 2)
    frames2 = [load(f"{ROOT}/r/{X}-anim/f{i:03d}.png", 1) for i in range(N)]
    idle2 = load(f"{ROOT}/r/{X}-anim/idle.png", 1)
    frames1 = [load(f"{ROOT}/r/{X}-anim/f{i:03d}.png", 2) for i in range(N)]
    idle1 = load(f"{ROOT}/r/{X}-anim/idle.png", 2)
    reactor1 = load(f"{ROOT}/r/{X}-reactor/reactor.png", 2)

    # measurements, at game scale
    a = frames1[0].split()[3].point(lambda v: 255 if v > 200 else 0)
    bb = a.getbbox()
    top_px = bb[1]
    foot_top = ia["origin"][1] * PPT - fh / 2 * PPT
    above = (foot_top - top_px) / PPT
    lit = [lit_fraction(f, idle1) for f in frames1]
    loop_s = N / (60 * o["speed"])
    meas[X] = dict(name=o["name"], footprint=f"{fw}x{fh}", frames=N, animation_speed=o["speed"],
                   loop_seconds=round(loop_s, 2), height_above_footprint_tiles=round(above, 2),
                   top_above_origin_tiles=round(ia["origin"][1] - top_px / PPT, 2),
                   blue_lit_mean_pct=round(100 * sum(lit) / len(lit), 1), blue_lit_max_pct=round(100 * max(lit), 1),
                   blue_lit_min_pct=round(100 * min(lit), 1))
    m = meas[X]

    # GIFs: working loop, 1x and 2x, on ground with the footprint
    ms = max(20, round(1000 / (60 * o["speed"])))
    g1 = [panel([f], ia, 1) for f in frames1]
    g2 = [panel([f], ia, 2) for f in frames2]
    gif(g1, f"{OUT}/{X}-{o['slug']}-1x.gif", ms)
    gif(g2, f"{OUT}/{X}-{o['slug']}-2x.gif", ms)
    m["gif_frame_ms"] = ms

    # the sheet
    hero_w = panel([hero_w2], ih, 2)
    hero_i = panel([hero_i2], ih, 2)
    keys = [int(N * t) for t in (0, 0.25, 0.5, 0.75)]
    keyp = [panel([frames1[k]], ia, 1, pad=(0.4, 0.4, 0.6, 0.3)) for k in keys]
    r1 = row([hero_i, hero_w] + keyp, ["idle (off) -- 2x", "working, frame 0 -- 2x"]
             + [f"frame {k}/{N} -- 1x" for k in keys])
    w1 = panel([frames1[0]], ia, 1)
    i1 = panel([idle1], ia, 1)
    # a block, edge to edge, each a different frame (they need not run in step)
    cols, rows_ = o["block"]
    bw, bh = cols * fw + 2.4, rows_ * fh + 2.6
    blk = ground(bw, bh, (1 + fw / 2, 2 + fh / 2), (0, 0))
    ImageDraw.Draw(blk).rectangle([PPT, 2 * PPT, (1 + cols * fw) * PPT, (2 + rows_ * fh) * PPT], outline=FOOT)
    for j in range(rows_):
        for i in range(cols):
            f = frames1[(i * 7 + j * 13) % N]
            ox, oy = (1 + fw / 2 + i * fw) * PPT, (2 + fh / 2 + j * fh) * PPT
            paste(blk, f, ox - ia["origin"][0] * PPT, oy - ia["origin"][1] * PPT)
    blk = bloom(blk)
    rp = ir["pitch"]
    rpan = ground(ir["canvas"][0], ir["canvas"][1], ir["origin"], (2 * rp, 2 * rp))
    paste(rpan, reactor1, 0, 0)
    rpan = bloom(rpan)
    reactor_thumbs.append((X, rpan, rp))
    r2 = row([i1, w1, blk, rpan], ["idle, 1x", "working, 1x", f"a block of {cols * rows_}, 1x (frames out of step)",
                                   f"stage 4: Radiant Reactor, {rp:g}x{rp:g}, block of 4, 1x"])
    W = max(r1.width, r2.width)
    facts = (f"Footprint {fw}x{fh}.  Height: {m['height_above_footprint_tiles']:+.2f} tiles above the footprint's "
             f"north edge (vanilla: nuclear +0.17, fusion reactor +0.67, fusion generator +0.25).  Blue: "
             f"{m['blue_lit_mean_pct']}% of the building's pixels lit, mean over the loop "
             f"({m['blue_lit_min_pct']}-{m['blue_lit_max_pct']}%; counts the blue light spilt on the metal too, so it "
             f"reads high beside vanilla's glow-layer-only 1.5 / 4.5 / 3.0%).  Loop: {N} frames at "
             f"animation_speed {o['speed']} = {loop_s:.1f} s.")
    txt = text_block(W, [("PITCH", o["pitch"]), ("HOW MUCH BLUE, AND THE SPEC WORDING", o["blue"]),
                         ("ANIMATION PLAN (burner-generator: animation + idle_animation, same frame count)", o["plan"]),
                         ("FOOTPRINT AND TILING", o["tiling"]), ("THE FAMILY", o["family"]),
                         ("MEASURED", facts)])
    head = Image.new("RGBA", (W, 54), BG)
    label(head, (10, 6), f"RADIANT GENERATOR, ROUND 2 -- OPTION {X}: {o['name']}", 22, bold=True)
    label(head, (10, 34), "Lit Blender blockout (layered finish, emission + core light, GPU). Not adopted. "
          "64 px a tile at 1x. The loop is in the GIFs beside this sheet.", 13, SUB)
    sheet = stack_v([head, r1, r2, txt], width=W)
    sheet.save(f"{OUT}/{X}-{o['slug']}.png")
    contact_opts.append((f"{X} {o['name'].lower()}, {fw}x{fh}, working", w1))
    print(X, m)

# ---------------------------------------------------------------- contact sheet


def vanilla_panel(rel, w, h, shift, foot):
    im = Image.open(os.path.join(FD, rel)).convert("RGBA").crop((0, 0, w, h))
    return sprite_panel([(im, shift)], foot)


def sprite_panel(layers, foot, h_tiles=None):
    fw, fh = foot
    h_tiles = h_tiles or fh + 3
    w = fw + 2
    origin = (w / 2, h_tiles - fh / 2 - 0.6)
    g = ground(w, h_tiles, origin, foot)
    for im, shift in layers:
        paste(g, im, origin[0] * PPT + shift[0] * PPT - im.width / 2, origin[1] * PPT + shift[1] * PPT - im.height / 2)
    return g


def ours(rel):
    return Image.open(os.path.join(REPO, rel)).convert("RGBA")


def additive(base, glow):
    g = glow.convert("RGBa")
    r, gg, b, _ = g.split()
    rgb = ImageChops.add(base.convert("RGB"), Image.merge("RGB", (r, gg, b)))
    return Image.merge("RGBA", (*rgb.split(), base.split()[3]))


rg_v = additive(ours("graphics/entity/radiant-generator/base-vertical.png"),
                ours("graphics/entity/radiant-generator/glow-vertical.png"))
refs = [
    ("vanilla nuclear reactor 5x5, working", Image.open(f"{REFP}/nuclear-reactor-working.png").convert("RGBA")),
    ("fusion reactor 6x6, working", Image.open(f"{REFP}/fusion-reactor-working.png").convert("RGBA")),
    ("fusion generator 3x5, working", Image.open(f"{REFP}/fusion-generator-working.png").convert("RGBA")),
    ("vanilla steam engine 3x5", vanilla_panel("base/graphics/entity/steam-engine/steam-engine-V.png", 225, 391,
                                               (4.75 / 32, -6.25 / 32), (3, 5))),
    ("Reaction Plant 3x3", sprite_panel(
        [(ours("graphics/entity/reaction-plant/base.png"), (0, -0.14062)),
         (ours("graphics/entity/reaction-plant/coupling.png").crop((0, 0, 46, 37)), (0.10938, -0.78906))], (3, 3))),
    ("Radiant Generator now (v2) 3x5", sprite_panel([(rg_v, (0, 0))], (3, 5))),
]
row_r = row([p for _, p in refs], [n for n, _ in refs])
row_o = row([p for _, p in contact_opts], [n for n, _ in contact_opts])
half = [(f"{X}: reactor block, 4 x {rp:g}x{rp:g} -- HALF scale", p.resize((p.width // 2, p.height // 2), Image.LANCZOS))
        for X, p, rp in reactor_thumbs]
row_x = row([p for _, p in half], [n for n, _ in half])
W = max(row_r.width, row_o.width, row_x.width)
head = Image.new("RGBA", (W, 52), BG)
label(head, (10, 6), "RADIANT GENERATOR, ROUND 2 -- SHOWPIECE OPTIONS AT GAME SCALE", 20, bold=True)
label(head, (10, 32), "64 px a tile. Top: references (vanilla working, our current art). Middle: the five options, "
      "working, frame 0, with shadows and bloom. Bottom: each option's stage-4 Radiant Reactor, a block of four, "
      "at half scale. Lit Blender blockouts.", 12, SUB)
contact = stack_v([head, row_r, row_o, row_x], width=W)
contact.save(f"{OUT}/contact-sheet.png")
print(f"{OUT}/contact-sheet.png", contact.size)
json.dump(meas, open(f"{OUT}/measurements.json", "w"), indent=1)
