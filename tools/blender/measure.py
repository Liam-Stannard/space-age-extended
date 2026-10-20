#!/usr/bin/env python3
"""One measuring suite for every model round: figures, pipe joins, collide, a comparison sheet.

  python3 tools/blender/measure.py <src> [--out <dir>] [--connection X,Y,F ...]
                                   [--vanilla <name> ...] [--collide <model.py>]
                                   [--collide-allow <pattern> ...]
                                   [--footprint WxH] [--directions one|four|horizontal-vertical]
                                   [--plate <stem>] [--title <text>] [--max-side <px>]

<src> is one of
  - render.sh's <out-dir>: its sheets/ (packed sheets and meta.json) and renders/render.json
    (the model's declaration, contract.py), which says what every sheet is;
  - a packed sheets directory alone (meta.json beside the sheets): a model's committed
    concept/<building>/model/sheets/, or one taken from an old commit with `git show`. With
    no render.json beside it, --footprint is needed; the directions are read off the sheet
    names, the plate is the sheet named --plate (default "base"), any sheet with "shadow" in
    its name is a shadow, "glow" a glow drawn additively, "lens", "lamp" or "light" a white
    cut the engine tints (not drawn here); an entry with frames is an animation (drawn as
    paint unless meta.json gives its kind, and as part of the stopped machine: meta.json does
    not say which layers draw only while working, so ore or dust falling counts in the still
    there). Anything else is listed in measures.json as ignored, not guessed at.

Everything is measured as the engine draws it: each sheet placed at its shift on one canvas,
the entity origin at the canvas's centre, 64 px a tile (the vanilla pipe and the references
are at that scale; another px_per_tile is refused).

Options
  --out <dir>          where measures.json and the sheet(s) go (default <src>/measures). Needed
                       when that default would be inside a concept/ folder (a model's committed
                       sheets): measure.py writes nothing into committed design unasked.
  --connection X,Y,F   a fluid connection as the model faces north: the centre of the
                       footprint tile it is on (tiles, y down, the entity centre 0,0, as a
                       pipe_connections position) and the face F (N, E, S, W) its pipe leaves
                       by. Repeatable; turned with the model into every direction. Without
                       any, render.json's ports are used (a model with no ports and none
                       given has no joins measured).
  --vanilla <name>     a vanilla reference for the sheet and for the figures beside ours:
                       one of REFS below. Repeatable, in the order given.
  --collide <model.py> run the model in Blender with --collide first ($BLENDER, as
                       render.sh); a clash fails the run.
  --collide-allow <pattern>  a clash the model means (a hub on its shaft): a Python regular
                       expression that must match the whole of a pair line's text after
                       "COLLIDE " (re.fullmatch: "a x b" allows "a x b", not "a x b2"); a line
                       it matches is allowed, listed in measures.json under collide.allowed with
                       the pattern. Repeatable. A pattern that matches the empty string (".*",
                       "") is refused (exit 2). A pair line no pattern matches still fails the run.
  --footprint WxH      the footprint in tiles as the model faces north (sheets alone)
  --directions D       one, four or horizontal-vertical (sheets alone; else read off names)
  --plate <stem>       the plate sheet's stem (sheets alone; default base)
  --title <text>       the sheet's title (default the source's path)
  --max-side <px>      every sheet image is strictly under this on its longer side (at most
                       <px> - 1): 400 to 8000, default 8000 (a page narrower than 400 px cannot
                       hold a 4x join panel's caption). ports-vs-assembler-3.png, measure_ports.py's
                       6x picture, is written at its own size (3864 x 960 for four ports), and
                       drawn into the sheet within the limit.

Exit status: 0 when every gate passes; 1 when a join shows a gap or the collide step finds a clash
(or cannot run), after measures.json and the sheet are written, naming what failed; 2 on
bad input. The figures themselves are numbers, not gates.

The figures, per direction (all at 1x, 64 px a tile; "covered" = alpha > 128):
  coverage   the still -- the plate with every non-working paint animation's frame 0 over
             it, the stopped machine -- against the footprint as it stands in that
             direction: footprint_pct (covered share of the footprint's rectangle, as the
             r5/r7 kits count it), mass_pct (every covered pixel in or out of it, over its
             area; concept/crust-turbine's measure_cover.py counted alpha > 127, so its
             "footprint" and "mass" can differ by a pixel row's worth: vanilla's vertical
             steam turbine 77.7 / 79.3 there, 77.5 / 79.1 here), corners_pct (each
             corner tile's cover, r7's corners()), outer_band_pct (the band a quarter tile
             deep inside the footprint's edge, the reaction plant's round 4), rise_tiles
             (the covered top over the footprint's north edge, r5a's rise) and
             rise_by_column_tiles (the same over each tile column), extent_tiles (the
             covered box's width and height) and centre_offset_px (its centre against the
             origin's x)
  tonal      tonal.py's p5, p50, p95, spread (alpha > 200), on the plate and the still
  finish     finish.py's black_pct, fine, mid, ratio, darkchr, on the plate and the still
  colour     on working frame 0 -- the still with every paint layer that draws while
             working, every glow added over it, on ground (74, 66, 58) -- over the plate's
             covered pixels: blue (the radiant ramp's hue, look_common.blue_mask: B > 110,
             B > R + 45, B > G + 10) px and pct; pale_px (the blue pixels with luminance
             >= 170, look_study's "pale") and pale_pct_of_blue; orange (the melt and seam
             heat ramps #C8541E -> #E8A24A -> #FFD9A0: R >= 180, R - B >= 90, G - B >= 30,
             R - G >= 30) px and pct; white_px (every channel >= 245, pack.py's white());
             clipped_px (the most pixels, in any frame of the loop, that the light drives
             to white and that are not white without it: pack.py's glow_checks, over every
             glow at once); and idle_blue_pct / idle_orange_pct, the same shares on the still
  glow       per glow layer (a glow pass, or a glow animation's frame 0), its light (RGB
             times alpha, as the engine adds it): look_common.light_measures -- area, peak,
             core %, halo %, sat_core, sat_halo, white -- and blue_pct of its lit pixels;
             for an animated glow its frames and its flicker: the light's total luminance
             per frame, flicker_step_pct (the largest change between consecutive frames,
             the wrap included, over the mean) and range_pct ((max - min) / mean)
  motion     over the loop (the least common multiple of the animations' frame counts,
             at most 240, else the longest), each frame drawn as working frame 0 is:
             moving_pct (covered pixels whose luminance difference from frame 0 is over 30
             in any frame: r5a's "changing"), strobe_pct (covered pixels whose on-ground
             luminance reverses by over 20 on consecutive frames 3 or more times a loop:
             r7's strobe()), the frame steps (pixels changed by over 8 between consecutive
             frames, measure_animation.py's) with the wrap from the last frame to the
             first against them, and per layer the same moving_pct with that layer alone
             over the plate
  layers_alone  per animation layer with more than one frame (paint, glow or light), its own
             frames as packed, RGBA, not over the plate (concept/crust-tap's
             measure_animation.py's c2 and c4): frame_px, step_px (pixels with a channel or
             alpha more than STEP_CHANGE (8) apart between consecutive frames), wrap_px (the
             last frame to the first) and wrap_within_steps, and most_changed_px with
             between_frames (the two most different frames, more than MOST_CHANGE (24) apart;
             over every pair up to PAIRS_CAP (120) frames, else null)
  light      per light layer (a white cut the engine tints, not drawn in the figures above),
             every frame alone, its pixels at alpha over LIGHT_LIT (8): px_range over the
             frames, channel_spread_max (the most, in any frame, between its alpha-weighted
             channel means: neutral white is a small spread), and frame 0's px, mean_rgb,
             channel_spread and luminance_range (concept/crust-tap's measure.py
             criterion_glass, less its outside-the-glass count, which needs the glass's own
             render)
  pack_checks  pack.py's own checks for the direction, copied from meta.json (frame0_vs_still,
             a slide's or turn's path, half_width_tiles ...)
  joins      below
  ports      when the model has port pictures (<sheets>/ports), measure_ports.py's
             comparison of each against assembler 3's outline (missed, extra, far_px)

The pipe joins, per connection in each direction. A vanilla straight pipe
(base/graphics/entity/pipe, vertical for a north or south face, horizontal for east or
west) is laid on the tile the connection points into, drawn over the building when that
tile is south of the entity's centre and under it otherwise (the stricter reading when they
are level). The building is the still, with the model's port picture for that face over it
when it has one. Measured with the pipe turned to lie south of the building (a rotation by
quarter turns, exact), so "rows" run along the pipe and "columns" across it. The rule is
Liam's (2026-10-15): no gap; anything of the building beside the pipe is fine, and clipping
is judged by eye on the 4x sheet and in client screenshots.
  gap        THE GATE, as agreed (task factorio-tools-skills, T05 criterion 2): in the pipe
             body's columns, ground of 2 px or more between the pipe's end and the building
             in at most 2 columns passes. In each column of the pipe body (the pipe's opaque
             width, alpha > 128 and its black shadow not counted, at its own tile's centre;
             GAP_TRIM 0: every column, its anti-aliased edge ones too), walk from the pipe's
             first pixel back toward the building, counting the ground (alpha <= 128), until
             the building's main piece -- its largest 4-connected part at alpha > 64 within
             two tiles, so a fitting or line not joined to it does not count -- covers
             GAP_SOLID (4) rows in a row. A column with GAP_RUN (2) px or more of ground is a
             gap column; more than GAP_COLUMNS (2) gap columns fail the join. A building not
             reached within two tiles counts as all ground. So a thin line or a lip laid in
             front of a gap (under 4 rows), or a detached fitting with ground behind it, does
             not hide the gap; a 1 px seam (vanilla's chemical plant) is not one.
             Calibrated on 128 vanilla joins of 12 buildings and pinned by probes
             (tools/blender/test/test_joins_vanilla.py): every vanilla join passes, none with
             more than 1 gap column (the refinery's (2, 2) south join), and all would still
             pass with GAP_SOLID 5 or 6. What the numbers allow, on a flat block (the
             probes): on a vertical pipe (39 px body) a stub of 37 px passes and 36 px fails,
             a 41 px stub 3 px off the axis passes and 4 px fails; on a horizontal pipe (41
             px body) a 39 px stub passes and 38 px fails; a building ending 1 px short of the
             pipe passes, 2 px fails. Known limits: a line, lip or fitting 4 px thick or more
             and joined to the body counts as the building; a stub up to 2 px narrower than
             the pipe body, or a little off its axis, passes (2 gap columns, the most the rule
             allows); whether a part clips (drawn across the pipe where it should be behind)
             is not measured -- that is the 4x sheet and client screenshots, for Liam.
Information only, never failing the run:
  ring       the pipe's end ring: from the pipe's first row, the rows until its width has
             grown past the pipe body's and fallen back to it.
  body       walking from the ring's first row into the building, the first row the
             building covers at alpha > 64 across the ring's width (else the pipe body's,
             rule "pipe body"), run on toward the pipe while the building stays a tile wide.
  band       ground in the pipe body's columns from the body to the pipe (the old gate:
             vanilla's chemical plant fails it with its 1 px seam).
  ring_band  the same across the ring's full width: the ring's shoulders.
  beside     building pixels seen beside the ring (level with its sides, its rows within
             4 px of its full width) or beside the pipe past it, outside the pipe's width
             plus RING_AA (2 px a side), within a tile of the axis, beyond the body, and not
             shadow (faint and near black: no channel at DARK (40) and alpha under SOLID
             (224), or no channel at BLACK (20)). Vanilla has up to 1700 px of it.
  beside_strict  every seen building pixel outside the ring's exact width from the body to
             the far end of the pipe's tile, dark or not.
Offsets are px, across from the pipe's axis and along from the tile edge the connection is
on (positive into the pipe's tile).

The collide step runs `$BLENDER -b --python-exit-code 1 --python-expr <make Python's output
line-buffered> --python <model.py> -- <out>/collide --collide` and reads the lines the model
prints starting "COLLIDE" (every model's --collide does; leading spaces are stripped first;
Python's output is made line-buffered so Blender's own output cannot cut a line): it fails on a
clash -- a pair line, naming a pair ("<a> x <b>": an "x" word between two words that are not
both numbers, so "grid 3 x 5" is not one), or a count above 0 ("clashes 2", "overlaps: 2", or
the number first, "2 clashes", as the Reaction Plant's circulator.py prints it) -- and when
Blender exits non-zero, the output holds a Python "Traceback" (an exception after the counts
were printed), or the model prints no count. Its output is kept in <out>/collide.log. With
--collide-allow, a pair line whose text after "COLLIDE " a pattern matches whole is allowed
(listed, with the pattern, under "allowed"); the run still fails on any pair line no pattern
matches ("not_allowed"), and when the counts add up to more clashes than the allowed pair lines.
Only pair lines can be allowed, so a line naming no pair -- a count, a header, a size -- never
adds to the allowed number; a model that counts clashes without naming each as "<a> x <b>"
(ballast_drill.py's "COLLIDE <a> <b> <material>" lines) cannot have them allowed. A pattern that
matched nothing is listed under "allow_unused" (information).

The comparison sheet (<out>/comparison.png, or comparison-1.png, -2.png ... when one image
would reach --max-side on either side): per direction ours as seen at 1x (the still, its
shadow at half strength, on ground), working frame 0 and the motion map (moving pixels
magenta, strobing cyan) when it animates, then each named vanilla reference the same way
with its figures; every join at 4x, plain and marked (gap columns red; beside, for
information, magenta and purple); the port pictures against assembler 3 at 6x; and the figures as text. Shadows
and the glow's addition are emulated here, not taken from a client.

measures.json:
  {"source": {"src", "sheets", "render_json", "directions", "footprint", "px_per_tile",
              "connections", "vanilla"},
   "directions": {"<direction>": {"layers": {...kinds...}, "ignored": [...],
                  "coverage": {...}, "tonal": {"plate", "still"}, "finish": {"plate", "still"},
                  "colour": {...}, "glow": {"<layer>": {...}}, "motion": {...} | null,
                  "layers_alone": {"<layer>": {...}}, "light": {"<layer>": {...}},
                  "pack_checks": {...} | null,
                  "joins": [{"connection", "pipe_tile", "pipe_drawn", "ring", "pipe_body",
                             "gap", "pass", "why", and for information "body", "band",
                             "ring_band", "beside", "beside_strict"}]}},
   "ports": {"<face>": {missed, extra, far_px, vanilla, ours}} | null,
   "vanilla": {"<name>": {"<direction>": {"coverage", "tonal", "finish", "colour", "glow"}}},
   "collide": {"model", "log", "allow", "returncode", "lines", "clash_lines" (every pair line),
               "counts", "allowed": [{"line", "pattern"}], "not_allowed", "allow_unused",
               "pass", "why"} | null,
   "sheets": [{"path", "size"}], "sheet_unsplit_px": [w, h],
   "gates": {"joins": bool | null, "collide": bool | null}, "pass": bool}

REFS (--vanilla): steam-turbine, steam-engine, assembling-machine-3, chemical-plant,
oil-refinery, pumpjack, fusion-generator, foundry, electromagnetic-plant. Their geometry is
read from the vanilla data (FACTORIO_DATA, default the Steam install): a sprite's .lua beside
it (util.sprite_load) or the prototype table naming it, plus what the prototype adds where the
.lua alone is wrong (vanilla_sprite's opts): the chemical plant's sprite_load shift
by_pixel(0, -9), added to its sidecars' as util.sprite_load adds it; the pumpjack base's
numbers (its file name is built in code) and its one-direction-a-column sheet.

For replacing a per-round script, every figure is a function here (coverage, tonal, finish,
colour, light_measures, motion, join, collide) that takes images, not paths, and can be
imported: `sys.path.insert(0, "tools/blender"); import measure`.
"""
import argparse
import glob
import json
import math
import os
import re
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageMath

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import contract  # noqa: E402
import measure_ports  # noqa: E402
import pack  # noqa: E402

FD = os.environ.get("FACTORIO_DATA", os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
PIPE = os.path.join(FD, "base", "graphics", "entity", "pipe")
PPT = 64
GROUND = (74, 66, 58)               # preview.py's ground, and look_common's
COVER = 128                         # covered: alpha above this
EDGE = 64                           # a joint's body: covered at alpha above this (its anti-aliased edge row)
GAP_RUN = 2                         # the join gate: a pipe-body column with this much ground or more is a gap...
GAP_COLUMNS = 2                     # ...and more than this many such columns fail (Liam, 2026-10-15: "at most 2")
GAP_TRIM = 0                        # pipe-body columns left out each side: none (every column of the body counts)
GAP_SOLID = 4                       # the building is reached where its main piece covers this many rows in a row
RING_AA = 2                         # beside (information): the ring's width plus its anti-aliased edge, px a side
DARK = 40                           # beside (information): no channel this bright and alpha under SOLID: shadow
SOLID = 224
BLACK = 20                          # beside (information): no channel this bright, whatever its alpha: shadow
MAX_SIDE = 8000
LOOP_CAP = 240
STEP_CHANGE = 8                     # layers_alone: a step counts a pixel with a channel or alpha over this apart
MOST_CHANGE = 24                    # layers_alone: the two most different frames, a pixel more than this apart
PAIRS_CAP = 120                     # layers_alone: most_changed_px over every pair only up to this many frames
LIGHT_LIT = 8                       # light: a light layer's pixel counts at alpha above this
BG, TXT, HEAD, GOOD, BAD = (30, 30, 30), (230, 222, 205), (240, 200, 120), (140, 220, 140), (255, 110, 90)
FACE = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
# turning a face's pipe to lie south of the building, and back
TO_SOUTH = {"S": None, "N": Image.Transpose.ROTATE_180, "E": Image.Transpose.ROTATE_270,
            "W": Image.Transpose.ROTATE_90}
FROM_SOUTH = {"S": None, "N": Image.Transpose.ROTATE_180, "E": Image.Transpose.ROTATE_90,
              "W": Image.Transpose.ROTATE_270}
SUFFIXES = ("north", "east", "south", "west", "vertical", "horizontal")


class Usage(Exception):
    """Bad input: exit 2."""


# ---------------------------------------------------------------- small helpers

def load(path):
    return Image.open(path).convert("RGBA")


def covered(alpha, thr=COVER):
    return alpha.point(lambda v: 255 if v > thr else 0)


def count(mask):
    return mask.histogram()[255]


def both(a, b):
    return ImageChops.multiply(a, b)


def on_ground(im, ground=GROUND):
    g = Image.new("RGBA", im.size, ground + (255,))
    g.alpha_composite(im)
    return g.convert("RGB")


def light_of(glow):
    """A glow sheet as the light the engine adds: its RGB times its alpha (look_common.light_of)."""
    r, g, b, a = glow.convert("RGBA").split()
    return Image.merge("RGB", [ImageChops.multiply(c, a) for c in (r, g, b)])


def lum(p):
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


def sat(p):
    mx, mn = max(p), min(p)
    return 0.0 if mx == 0 else (mx - mn) / mx


def bbox_list(points):
    if not points:
        return None
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return [min(xs), min(ys), max(xs) + 1, max(ys) + 1]


# ---------------------------------------------------------------- the figures

def tonal(im):
    """tonal.py's numbers on an image: luminance percentiles of the pixels at alpha > 200."""
    L = sorted(0.299 * r + 0.587 * g + 0.114 * b for r, g, b, a in im.get_flattened_data() if a > 200)
    if not L:
        return None

    def q(f):
        return round(L[int(f * (len(L) - 1))])
    return dict(p5=q(.05), p50=q(.5), p95=q(.95), spread=q(.95) - q(.05))


def finish(im):
    """finish.py's numbers on an image, rounded as it prints them."""
    a = im.getchannel("A")
    L = im.convert("L")
    b3 = L.filter(ImageFilter.BoxBlur(1))
    b9 = L.filter(ImageFilter.BoxBlur(4))
    ero = a.filter(ImageFilter.MinFilter(9))
    px = [(l, s3, s9, c) for l, s3, s9, e, c in zip(L.get_flattened_data(), b3.get_flattened_data(),
          b9.get_flattened_data(), ero.get_flattened_data(), im.convert("RGB").get_flattened_data()) if e > 250]
    n = len(px)
    if n < 4:
        return None
    black = sum(1 for p in px if p[0] < 12) / n
    fine = sum(abs(p[0] - p[1]) for p in px) / n
    mid = sum(abs(p[1] - p[2]) for p in px) / n
    dark = sorted(px, key=lambda p: p[0])[: n // 4]
    chroma = sum(max(p[3]) - min(p[3]) for p in dark) / len(dark)
    return dict(black_pct=round(100 * black, 1), fine=round(fine, 2), mid=round(mid, 2),
                ratio=round(fine / mid, 2) if mid else None, darkchr=round(chroma, 1))


def coverage(still, foot, origin, ppt=PPT):
    """The still against the footprint (w, h tiles as it stands), the origin at `origin`."""
    fw, fh = foot
    ox, oy = origin
    x0, y0 = round(ox - fw * ppt / 2), round(oy - fh * ppt / 2)
    x1, y1 = x0 + fw * ppt, y0 + fh * ppt
    a = covered(still.getchannel("A"))
    area = fw * fh * ppt * ppt
    inside = count(a.crop((x0, y0, x1, y1)))
    q = ppt // 4
    inner = count(a.crop((x0 + q, y0 + q, x1 - q, y1 - q)))
    corners = {}
    for nm, (i, j) in dict(NW=(0, 0), NE=(fw - 1, 0), SW=(0, fh - 1), SE=(fw - 1, fh - 1)).items():
        corners[nm] = round(100 * count(a.crop((x0 + ppt * i, y0 + ppt * j, x0 + ppt * i + ppt,
                                                y0 + ppt * j + ppt))) / (ppt * ppt), 1)
    bb = a.getbbox()
    out = dict(footprint=[fw, fh], footprint_pct=round(100 * inside / area, 1),
               mass_pct=round(100 * count(a) / area, 1), corners_pct=corners,
               outer_band_pct=round(100 * (inside - inner) / (area - (fw * ppt - 2 * q) * (fh * ppt - 2 * q)), 1))
    if bb is None:
        return out
    cols = []
    for i in range(fw):
        cb = a.crop((x0 + ppt * i, 0, x0 + ppt * i + ppt, a.height)).getbbox()
        cols.append(round((y0 - cb[1]) / ppt, 2) if cb else None)
    out.update(rise_tiles=round((y0 - bb[1]) / ppt, 2), rise_by_column_tiles=cols,
               extent_tiles=[round((bb[2] - bb[0]) / ppt, 2), round((bb[3] - bb[1]) / ppt, 2)],
               centre_offset_px=(bb[0] + bb[2]) / 2 - ox,
               past_edges_tiles=dict(west=round((x0 - bb[0]) / ppt, 2), east=round((bb[2] - x1) / ppt, 2),
                                     south=round((bb[3] - y1) / ppt, 2)))
    return out


def blue_mask(im):
    """The radiant ramp's blue (look_common.blue_mask): B > 110, B > R + 45, B > G + 10."""
    r, g, b = im.convert("RGB").split()
    m1 = b.point(lambda v: 255 if v > 110 else 0)
    m2 = ImageChops.subtract(b, r).point(lambda v: 255 if v > 45 else 0)
    m3 = ImageChops.subtract(b, g).point(lambda v: 255 if v > 10 else 0)
    return both(both(m1, m2), m3)


def orange_mask(im):
    """The melt and seam-heat orange (#C8541E -> #E8A24A -> #FFD9A0): R >= 180, R - B >= 90,
    G - B >= 30, R - G >= 30."""
    r, g, b = im.convert("RGB").split()
    m1 = r.point(lambda v: 255 if v >= 180 else 0)
    m2 = ImageChops.subtract(r, b).point(lambda v: 255 if v >= 90 else 0)
    m3 = ImageChops.subtract(g, b).point(lambda v: 255 if v >= 30 else 0)
    m4 = ImageChops.subtract(r, g).point(lambda v: 255 if v >= 30 else 0)
    return both(both(m1, m2), both(m3, m4))


def colour(drawn, paint, idle, frames_drawn=(), frames_paint=()):
    """drawn: working frame 0 on ground with its light (RGB); paint: the same without the light
    (RGBA); idle: the still (RGBA). frames_*: the whole loop, for clipped_px."""
    op = covered(paint.getchannel("A"))
    n = max(1, count(op))
    blue = both(blue_mask(drawn), op)
    pale = both(blue, drawn.convert("L").point(lambda v: 255 if v >= 170 else 0))
    orange = both(orange_mask(drawn), op)
    nb = count(blue)
    clipped = 0
    for d, p in zip(frames_drawn or [drawn], frames_paint or [paint]):
        clipped = max(clipped, count(ImageChops.subtract(pack.white(d), pack.white(on_ground(p)))))
    iop = covered(idle.getchannel("A"))
    ig = on_ground(idle)
    ni = max(1, count(iop))
    return dict(opaque_px=count(op), blue_px=nb, blue_pct=round(100 * nb / n, 2), pale_px=count(pale),
                pale_pct_of_blue=round(100 * count(pale) / nb, 1) if nb else 0.0,
                orange_px=count(orange), orange_pct=round(100 * count(orange) / n, 2),
                white_px=count(both(pack.white(drawn), op)), clipped_px=clipped,
                idle_blue_pct=round(100 * count(both(blue_mask(ig), iop)) / ni, 2),
                idle_orange_pct=round(100 * count(both(orange_mask(ig), iop)) / ni, 2))


def light_measures(light, thresh=12):
    """look_common.light_measures: how a light builds, on its lit pixels (any channel > thresh)."""
    px = [p for p in light.convert("RGB").get_flattened_data() if max(p) > thresh]
    if not px:
        return dict(area=0, peak=0, core=0, halo=0, sat_core=0, sat_halo=0, white=0)
    L = [lum(p) for p in px]
    pk = max(L)
    core = [p for p, v in zip(px, L) if v >= 0.6 * pk]
    halo = [p for p, v in zip(px, L) if v <= 0.25 * pk]
    return dict(area=len(px), peak=round(pk), core=round(100 * len(core) / len(px), 1),
                halo=round(100 * len(halo) / len(px), 1),
                sat_core=round(sum(sat(p) for p in core) / max(1, len(core)), 2),
                sat_halo=round(sum(sat(p) for p in halo) / max(1, len(halo)), 2),
                white=sum(1 for p in px if min(p) >= 245))


def glow_figures(lights):
    """One glow layer, its light per frame (RGB)."""
    out = light_measures(lights[0])
    lit = Image.new("L", lights[0].size)
    for c in lights[0].split():
        lit = ImageChops.lighter(lit, c.point(lambda v: 255 if v > 12 else 0))
    out["blue_pct"] = round(100 * count(both(blue_mask(lights[0]), lit)) / max(1, count(lit)), 1)
    out["frames"] = len(lights)
    if len(lights) > 1:
        tot = [sum(lights[f].convert("L").histogram()[v] * v for v in range(256)) for f in range(len(lights))]
        mean = sum(tot) / len(tot)
        steps = [abs(tot[(f + 1) % len(tot)] - tot[f]) for f in range(len(tot))]
        out.update(flicker_step_pct=round(100 * max(steps) / mean, 1) if mean else 0.0,
                   range_pct=round(100 * (max(tot) - min(tot)) / mean, 1) if mean else 0.0)
    return out


def strobe(frames_rgb, thr=20, need=3):
    """r7's strobe(): 255 where a pixel's on-ground luminance reverses by > thr on consecutive
    frames `need` times or more a loop."""
    g = [f.convert("L").convert("F") for f in frames_rgb]
    n = len(g)
    d = [ImageMath.lambda_eval(lambda a: a["x"] - a["y"], x=g[(i + 1) % n], y=g[i]) for i in range(n)]
    acc = None
    for i in range(n):
        r = ImageMath.lambda_eval(lambda a: ((a["p"] * a["q"]) < 0) * (abs(a["p"]) > thr) * (abs(a["q"]) > thr),
                                  p=d[i], q=d[(i + 1) % n])
        acc = r if acc is None else ImageMath.lambda_eval(lambda a: a["x"] + a["y"], x=acc, y=r)
    return ImageMath.lambda_eval(lambda a: (a["x"] >= need) * 255, x=acc).convert("L")


def moving(frames_rgb, thr=30):
    """r5a's changing pixels: luminance of the difference from frame 0 over thr in any frame."""
    acc = Image.new("L", frames_rgb[0].size)
    for f in frames_rgb[1:]:
        acc = ImageChops.lighter(acc, ImageChops.difference(frames_rgb[0], f).convert("L").point(
            lambda v: 255 if v > thr else 0))
    return acc


def steps(frames_rgb, thr=8):
    """measure_animation.py's frame steps: pixels with a channel more than thr apart."""
    n = len(frames_rgb)
    out = []
    for f in range(n):
        d = ImageChops.difference(frames_rgb[f], frames_rgb[(f + 1) % n]).split()
        most = ImageChops.lighter(ImageChops.lighter(d[0], d[1]), d[2])
        out.append(count(most.point(lambda v: 255 if v > thr else 0)))
    return out


def changed(a, b, thr):
    """Pixels of two RGBA frames with any channel, alpha included, more than thr apart
    (concept/crust-tap's measure_animation.py's changed())."""
    d = ImageChops.difference(a, b).split()
    most = d[0]
    for c in d[1:]:
        most = ImageChops.lighter(most, c)
    return count(most.point(lambda v: 255 if v > thr else 0))


def layer_alone(frames, cap=PAIRS_CAP):
    """One animation layer's own frames (RGBA, as packed, not over the plate): its frame steps
    with the wrap against them, and its two most different frames (measure_animation.py's c2
    and c4)."""
    n = len(frames)
    s = [changed(frames[f], frames[(f + 1) % n], STEP_CHANGE) for f in range(n)]
    out = dict(frames=n, frame_px=list(frames[0].size), step_px=s[:-1], wrap_px=s[-1],
               step_range=[min(s[:-1]), max(s[:-1])], wrap_within_steps=min(s[:-1]) <= s[-1] <= max(s[:-1]))
    if n > cap:
        out.update(most_changed_px=None, between_frames=None,
                   note=f"{n} frames: most_changed_px is measured over every pair only up to {cap}")
        return out
    best = max((changed(frames[i], frames[j], MOST_CHANGE), i, j) for i in range(n) for j in range(i + 1, n))
    out.update(most_changed_px=best[0], between_frames=[best[1], best[2]])
    return out


def light_figures(frames):
    """A light layer (a white cut the engine tints), every frame alone: its pixels at alpha over
    LIGHT_LIT, their alpha-weighted mean colour and its channel spread (neutral white is a small
    spread), and their luminance range (concept/crust-tap's measure.py criterion_glass, less its
    outside-the-glass count, which needs the glass's own render)."""
    rows = []
    for fr in frames:
        px = [p for p in fr.get_flattened_data() if p[3] > LIGHT_LIT]
        if not px:
            rows.append(dict(px=0, mean_rgb=None, channel_spread=None, luminance_range=None))
            continue
        w = sum(p[3] for p in px)
        mean = [round(sum(p[c] * p[3] for p in px) / w, 1) for c in range(3)]
        L = [round(lum(p)) for p in px]
        rows.append(dict(px=len(px), mean_rgb=mean, channel_spread=round(max(mean) - min(mean), 1),
                         luminance_range=[min(L), max(L)]))
    spreads = [r["channel_spread"] for r in rows if r["channel_spread"] is not None]
    return dict(frames=len(frames), px_range=[min(r["px"] for r in rows), max(r["px"] for r in rows)],
                channel_spread_max=max(spreads) if spreads else None, frame0=rows[0])


def pack_checks(meta, dn):
    """pack.py's own checks for one direction, as meta.json holds them (a one-direction model's
    are not keyed by direction)."""
    c = meta.get("checks")
    if not isinstance(c, dict):
        return None
    return c.get(dn) if dn else c


# ---------------------------------------------------------------- what is being measured

class Layer:
    def __init__(self, stem, kind, meta, working=False):
        self.stem, self.kind, self.meta, self.working = stem, kind, meta, working
        self.frames = int(meta.get("frames", 1))


class Source:
    """The sheets, what each is, and how to place them."""

    def __init__(self, src, footprint=None, directions=None, plate=None):
        src = os.path.abspath(src)
        if os.path.isfile(os.path.join(src, "sheets", "meta.json")):
            self.sheets, renders = os.path.join(src, "sheets"), os.path.join(src, "renders")
        elif os.path.isfile(os.path.join(src, "meta.json")):
            self.sheets, renders = src, os.path.join(os.path.dirname(src), "renders")
        else:
            raise Usage(f"{src}: neither <src>/sheets/meta.json nor <src>/meta.json: not a render.sh "
                        f"output directory or a packed sheets directory")
        self.src = src
        with open(os.path.join(self.sheets, "meta.json")) as f:
            self.meta = json.load(f)
        self.decl, self.render_json = None, None
        if os.path.isfile(os.path.join(renders, contract.FILE)):
            try:
                self.decl = contract.load(renders)
            except contract.ContractError as e:
                raise Usage(str(e)) from None
            self.render_json = os.path.join(renders, contract.FILE)
        d = self.decl or {}
        self.directions = directions or d.get("directions") or self.infer_directions()
        if self.directions not in contract.DIRECTIONS:
            raise Usage(f"--directions {self.directions!r} is not one of {', '.join(contract.DIRECTIONS)}")
        self.footprint = list(footprint or d.get("footprint") or [])
        if len(self.footprint) != 2:
            raise Usage(f"{src}: no render.json beside the sheets, so --footprint WxH is needed")
        self.ppt = float(d.get("rig", {}).get("px_per_tile", PPT))
        if self.ppt != PPT:
            raise Usage(f"px_per_tile {self.ppt:g}: measure.py works at {PPT} px a tile (the vanilla sprites')")
        self.plate = plate or "base"
        self.ports = os.path.join(self.sheets, "ports") if os.path.isfile(
            os.path.join(self.sheets, "ports", "meta.json")) else None
        self.port_meta = {}
        if self.ports:
            with open(os.path.join(self.ports, "meta.json")) as f:
                self.port_meta = json.load(f)
        self.dirs = [n for n, _ in contract.DIRECTIONS[self.directions]]
        self.layers, self.ignored, self.lights = {}, {}, {}
        for dn in self.dirs:
            self.layers[dn], self.ignored[dn] = self.classify(dn)
            if not any(lay.kind == "plate" for lay in self.layers[dn]):
                raise Usage(f"{self.sheets}: no plate sheet for direction {dn or '(one)'} "
                            f"(looked for {contract.named(self.plate, dn)!r}; --plate names it)")
        self._cache = {}
        self.size = self.canvas_size()
        self.origin = (self.size / 2, self.size / 2)

    def infer_directions(self):
        keys = [k for k in self.meta if k != "checks"]
        if any(k.endswith("-vertical") or k.endswith("-horizontal") for k in keys):
            return "horizontal-vertical"
        if any(k.endswith("-north") for k in keys):
            return "four"
        return "one"

    def classify(self, dn):
        layers, ignored = [], []
        if self.decl:
            for p in self.decl["passes"]:
                if p["kind"] == "still":
                    continue
                stem = contract.named(p["sheet"], dn)
                if stem in self.meta:
                    layers.append(Layer(stem, p["kind"], self.meta[stem], working=p["kind"] in ("glow", "paint")))
            for a in self.decl["animations"]:
                stem = contract.named(a["name"], dn)
                kind = {"paint": "anim", "light": "light", "glow": "glow-anim"}[a.get("kind", "paint")]
                if stem in self.meta:
                    layers.append(Layer(stem, kind, self.meta[stem], working=a.get("working", False)))
        else:
            suffix = f"-{dn}" if dn else ""
            for k, m in self.meta.items():
                if k == "checks" or not isinstance(m, dict):
                    continue
                if dn and not k.endswith(suffix):
                    continue
                if not dn and any(k.endswith("-" + s) for s in SUFFIXES):
                    continue
                base = k[:-len(suffix)] if suffix else k
                if base == self.plate:
                    kind = "plate"
                elif m.get("kind") == "light":
                    kind = "light"
                elif m.get("kind") == "glow":
                    kind = "glow-anim"
                elif "frames" in m:
                    kind = "anim"
                elif "shadow" in base:
                    kind = "shadow"
                elif "glow" in base:
                    kind = "glow"
                elif any(w in base for w in ("lens", "lamp", "light")):
                    kind = "light"
                else:
                    ignored.append(k)
                    continue
                layers.append(Layer(k, kind, m, working=kind == "glow"))
        layers.sort(key=lambda lay: lay.kind != "plate")
        ignored += [lay.stem + " (a white cut the engine tints: not drawn here)" for lay in layers
                    if lay.kind == "light"]
        self.lights[dn] = [lay for lay in layers if lay.kind == "light"]       # not drawn; measured alone
        return [lay for lay in layers if lay.kind != "light"], ignored

    def canvas_size(self):
        half = (max(self.footprint) / 2 + 2.5) * PPT
        for dn in self.dirs:
            for lay in self.layers[dn]:
                w, h = lay.meta["size"]
                sx, sy = lay.meta["shift"]
                half = max(half, abs(sx) * PPT + w / 2, abs(sy) * PPT + h / 2)
        return 2 * math.ceil(half + 8)

    def sheet(self, stem, ports=False):
        key = (stem, ports)
        if key not in self._cache:
            self._cache[key] = load(os.path.join(self.ports if ports else self.sheets, stem + ".png"))
        return self._cache[key]

    def frame(self, lay, f):
        im = self.sheet(lay.stem)
        w, h = lay.meta["size"]
        line = int(lay.meta.get("line_length", 1))
        f %= lay.frames
        return im.crop(((f % line) * w, (f // line) * h, (f % line) * w + w, (f // line) * h + h))

    def place(self, im, shift_tiles, at=(0.0, 0.0)):
        out = Image.new("RGBA", (self.size, self.size))
        out.alpha_composite(im, (round(self.origin[0] + (at[0] + shift_tiles[0]) * PPT - im.width / 2),
                                 round(self.origin[1] + (at[1] + shift_tiles[1]) * PPT - im.height / 2)))
        return out

    def connections(self, given):
        """Connections as the model faces north: given, or render.json's ports."""
        if given:
            return given
        return [(p["tile"][0], p["tile"][1], p["face"]) for p in (self.decl or {}).get("ports", [])]


class Scene:
    """One direction, drawn: the plate, the still, the loop's frames and their light."""

    def __init__(self, src, dn):
        self.src, self.dn = src, dn
        L = src.layers[dn]
        place = src.place
        self.plate_layer = next(lay for lay in L if lay.kind == "plate")
        self.plate = place(src.frame(self.plate_layer, 0), self.plate_layer.meta["shift"])
        self.anims = [lay for lay in L if lay.kind == "anim"]
        self.paints = [lay for lay in L if lay.kind == "paint"]
        self.glows = [lay for lay in L if lay.kind in ("glow", "glow-anim")]
        self.shadows = [lay for lay in L if lay.kind == "shadow"]
        counts = [lay.frames for lay in self.anims + self.glows if lay.frames > 1]
        n = 1
        for c in counts:
            n = n * c // math.gcd(n, c)
        self.loop = n if n <= LOOP_CAP else max(counts)
        self.still = self.plate.copy()
        for lay in self.anims:
            if not lay.working:
                self.still.alpha_composite(place(src.frame(lay, 0), lay.meta["shift"]))
        self.shadow = Image.new("RGBA", self.plate.size)
        for lay in self.shadows:
            s = place(src.frame(lay, 0), lay.meta["shift"])
            s.putalpha(s.getchannel("A").point(lambda v: v // 2))
            self.shadow.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", s.size).split(), s.getchannel("A"))))

    def paint(self, f):
        im = self.plate.copy()
        for lay in self.anims + self.paints:
            im.alpha_composite(self.src.place(self.src.frame(lay, f), lay.meta["shift"]))
        return im

    def light(self, f, only=None):
        out = Image.new("RGB", self.plate.size)
        for lay in self.glows:
            if only is None or lay is only:
                out = ImageChops.add(out, light_of(self.src.place(self.src.frame(lay, f), lay.meta["shift"])))
        return out

    def drawn(self, f):
        """Frame f as the engine draws it working, on ground."""
        p = self.paint(f)
        return ImageChops.add(on_ground(p), self.light(f)), p


def measure_direction(src, dn, conns):
    sc = Scene(src, dn)
    foot = contract.footprint_in(dict(footprint=src.footprint, directions=src.directions), dn)
    out = dict(layers={lay.stem: lay.kind + (" (working)" if lay.working else "") + (
        f", {lay.frames} frames" if lay.frames > 1 else "") for lay in src.layers[dn]},
        ignored=src.ignored[dn])
    out["coverage"] = coverage(sc.still, foot, src.origin)
    out["tonal"] = dict(plate=tonal(sc.plate), still=tonal(sc.still))
    out["finish"] = dict(plate=finish(sc.plate), still=finish(sc.still))
    frames = [sc.drawn(f) for f in range(sc.loop)]
    out["colour"] = colour(frames[0][0], frames[0][1], sc.still, [d for d, _ in frames], [p for _, p in frames])
    out["glow"] = {}
    for lay in sc.glows:
        lights = [sc.light(f, lay) for f in range(lay.frames)]
        out["glow"][lay.stem] = glow_figures(lights)
    out["motion"] = None
    maps = {}
    if sc.loop > 1:
        rgb = [d for d, _ in frames]
        op = covered(sc.still.getchannel("A"))
        n = max(1, count(op))
        mv, st = both(moving(rgb), op), both(strobe(rgb), op)
        s = steps(rgb)
        per = {}
        for lay in sc.anims + [g for g in sc.glows if g.frames > 1]:
            if lay.kind == "anim":
                fr = []
                for f in range(lay.frames):
                    im = sc.plate.copy()
                    im.alpha_composite(src.place(src.frame(lay, f), lay.meta["shift"]))
                    fr.append(on_ground(im))
            else:
                fr = [ImageChops.add(on_ground(sc.plate), sc.light(f, lay)) for f in range(lay.frames)]
            per[lay.stem] = round(100 * count(both(moving(fr), op)) / n, 2)
        out["motion"] = dict(loop_frames=sc.loop, moving_pct=round(100 * count(mv) / n, 2),
                             strobe_pct=round(100 * count(st) / n, 2), strobe_px=count(st),
                             step_px=s[:-1], wrap_px=s[-1],
                             wrap_within_steps=(min(s[:-1]) <= s[-1] <= max(s[:-1])) if len(s) > 1 else True,
                             per_layer_moving_pct=per)
        maps = dict(moving=mv, strobe=st)
    alone = [lay for lay in sc.anims + sc.glows + src.lights[dn] if lay.frames > 1]
    out["layers_alone"] = {lay.stem: layer_alone([src.frame(lay, f) for f in range(lay.frames)]) for lay in alone}
    out["light"] = {lay.stem: light_figures([src.frame(lay, f) for f in range(lay.frames)])
                    for lay in src.lights[dn]}
    out["pack_checks"] = pack_checks(src.meta, dn)
    out["joins"] = []
    pictures = []
    deg = dict(contract.DIRECTIONS[src.directions])[dn]
    for c in conns:
        res, pics = join(sc, turn(c, deg))
        out["joins"].append(res)
        pictures.append(pics)
    return out, sc, maps, pictures


# ---------------------------------------------------------------- the joins

def turn(conn, deg):
    """A connection as modelled (facing north) in a direction turned deg clockwise."""
    x, y, f = conn
    for _ in range(round(deg / 90) % 4):
        x, y, f = -y, x, "NESW"[("NESW".index(f) + 1) % 4]
    return (x, y, f)


def to_south(x, y, face):
    return {"S": (x, y), "N": (-x, -y), "E": (-y, x), "W": (y, -x)}[face]


def pipe_mask(im):
    """The pipe's own pixels: alpha > 128, its black part-transparent shadow left out."""
    r, g, b, a = im.split()
    lit = ImageChops.lighter(ImageChops.lighter(r, g), b).point(lambda v: 255 if v > 20 else 0)
    solid = a.point(lambda v: 255 if v >= 200 else 0)
    return both(covered(a), ImageChops.lighter(lit, solid))


def join(sc, conn):
    """One connection in one direction: see the docstring's "pipe joins"."""
    src = sc.src
    x, y, face = conn
    dx, dy = FACE[face]
    tx, ty = x + dx, y + dy
    sprite = load(os.path.join(PIPE, "pipe-straight-vertical.png" if face in "NS" else
                               "pipe-straight-horizontal.png"))
    pipe = src.place(sprite, (0, 0), at=(tx, ty))
    building = sc.still.copy()                       # with the port picture for this face, if any
    if src.ports and f"port-{face}" in src.port_meta:
        m = src.port_meta[f"port-{face}"]
        building.alpha_composite(src.place(src.sheet(f"port-{face}", ports=True), m["shift"], at=(tx, ty)))
    over = ty > 0
    comp = Image.new("RGBA", building.size, GROUND + (255,))
    for lay in ((building, pipe) if over else (pipe, building)):
        comp.alpha_composite(lay)
    comp = comp.convert("RGB")

    op = TO_SOUTH[face]
    B = building.getchannel("A")
    P = pipe_mask(pipe)
    r_, g_, b_, a_ = building.split()           # the building's own colour, not blended with the ground
    most = ImageChops.lighter(ImageChops.lighter(r_, g_), b_)
    solid_dark = both(most.point(lambda v: 255 if v >= BLACK else 0), a_.point(lambda v: 255 if v >= SOLID else 0))
    lit = ImageChops.lighter(most.point(lambda v: 255 if v >= DARK else 0), solid_dark)   # a part, not shadow
    if op is not None:
        B, P, lit = B.transpose(op), P.transpose(op), lit.transpose(op)
    Bd, Pd, Ld = B.load(), P.load(), lit.load()
    cx, cy = to_south(x, y, face)
    ox, oy = src.origin
    ax = ox + cx * PPT                               # the pipe's axis, a px boundary or centre
    ye = round(oy + (cy + 0.5) * PPT)                # the first row of the pipe's tile
    cols = range(math.floor(ax - PPT), math.ceil(ax + PPT))
    res = dict(connection=[x, y, face], pipe_tile=[tx, ty], pipe_drawn="over" if over else "under")

    def span(r):
        cs = [c for c in cols if Pd[c, r]]
        return (cs[0], cs[-1]) if cs else None

    def across(c0, c1):
        return [round(c0 + 0.5 - ax, 1), round(c1 + 0.5 - ax, 1)]

    rows = [r for r in range(ye - PPT, ye + PPT) if span(r)]
    body_span = span(ye + PPT // 2)
    if not rows or body_span is None:
        res.update(why="no vanilla pipe pixels at the connection (is the connection on the footprint's edge?)")
        res["pass"] = False
        return finish_join(res, comp, None, None, face, conn, src)
    t0 = rows[0]
    bw = body_span[1] - body_span[0] + 1
    ring_rows, wide = [], False
    for r in range(t0, t0 + 48):
        s = span(r)
        w = s[1] - s[0] + 1 if s else 0
        if wide and w <= bw + 2:
            break
        wide = wide or w > bw + 2
        ring_rows.append(r)
    r0 = min(span(r)[0] for r in ring_rows if span(r))
    r1 = max(span(r)[1] for r in ring_rows if span(r))
    edge = {}
    for c in cols:
        edge[c] = next((r for r in range(t0, ye + PPT) if Pd[c, r]), ye + PPT)
    sides = [r for r in ring_rows if span(r) and span(r)[1] - span(r)[0] + 1 >= r1 - r0 + 1 - 4]
    res["ring"] = dict(width_px=r1 - r0 + 1, across_px=across(r0, r1), first_row_px=t0 - ye,
                       rows=len(ring_rows), sides_rows_px=[sides[0] - ye, sides[-1] - ye])
    res["pipe_body"] = dict(width_px=bw, across_px=across(*body_span))

    def where(pts):
        bb = bbox_list(pts)
        return None if bb is None else dict(across_px=across(bb[0], bb[2] - 1), along_px=[bb[1] - ye, bb[3] - 1 - ye])
    g, gap_pts = gap_gate(Bd, cols, t0, ye, edge, body_span)
    g["where"] = where(gap_pts)
    res["gap"] = g
    res["pass"] = g["passed"]
    del g["passed"]
    res["why"] = g.pop("why")
    beside, strict = info_beside(res, Bd, Pd, Ld, over, span, where, cols, ring_rows, r0, r1,
                                 body_span, edge, t0, ye, B.width)
    return finish_join(res, comp, gap_pts, beside, face, conn, src, strict)


def main_mass(Bd, cols, rows):
    """The building's largest 4-connected piece (alpha > EDGE) in the window cols x rows: its pixels.
    A fitting or a line not joined to it by any pixel is not the building's body."""
    seen, best = set(), set()
    c0, c1, rr0, rr1 = cols[0], cols[-1], rows[0], rows[-1]
    for c in cols:
        for r in rows:
            if (c, r) in seen or not Bd[c, r] > EDGE:
                continue
            piece, todo = {(c, r)}, [(c, r)]
            seen.add((c, r))
            while todo:
                x, y = todo.pop()
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if c0 <= nx <= c1 and rr0 <= ny <= rr1 and (nx, ny) not in seen and Bd[nx, ny] > EDGE:
                        seen.add((nx, ny))
                        piece.add((nx, ny))
                        todo.append((nx, ny))
            if len(piece) > len(best):
                best = piece
    return best


def gap_gate(Bd, cols, t0, ye, edge, pipe_body, run=None, columns=None, trim=None, solid=None):
    """The join gate, no gap, in the pipe-south frame (see the module docstring). Returns its
    figures (with "passed" and "why") and the gap pixels. The keyword arguments override the
    module's GAP_RUN, GAP_COLUMNS, GAP_TRIM and GAP_SOLID (for calibration)."""
    run = GAP_RUN if run is None else run
    columns = GAP_COLUMNS if columns is None else columns
    trim = GAP_TRIM if trim is None else trim
    solid = GAP_SOLID if solid is None else solid
    mass = main_mass(Bd, cols, range(max(0, t0 - 2 * PPT), ye + PPT))
    a, b = pipe_body[0] + trim, pipe_body[1] - trim
    pts, per = [], {}
    for c in range(a, b + 1):
        ground, held = [], 0
        for r in range(edge[c] - 1, edge[c] - 1 - 2 * PPT, -1):
            if (c, r) in mass:
                held += 1
                if held >= solid:
                    break
                continue
            held = 0
            if Bd[c, r] <= COVER:
                ground.append((c, r))
        else:
            ground += [(c, edge[c] - 1)] * (2 * PPT - len(ground))      # never reached: all ground
        per[c] = len(ground)
        if len(ground) >= run:
            pts += ground
    gap_cols = [c for c, n in per.items() if n >= run]
    which = f"{trim} edge column(s) a side left out" if trim else "every one"
    out = dict(rule=f"in the pipe body's columns ({which}), the ground (alpha <= {COVER}) from the pipe's end "
                    f"back to where the building's main piece (alpha > {EDGE}, joined to the rest) covers {solid} "
                    f"rows in a row: {run} px or more makes a gap column; more than {columns} fail",
               columns=len(gap_cols), columns_allowed=columns, ground_px_counted_from=run, of_columns=b - a + 1,
               max_ground_px=max(per.values()), passed=len(gap_cols) <= columns)
    out["why"] = None if out["passed"] else (
        f"{len(gap_cols)} of the pipe body's {b - a + 1} columns show {run} px or more of ground between the "
        f"pipe and the building (at most {columns} allowed); the most in one column {max(per.values())} px")
    return out, pts


def info_beside(res, Bd, Pd, Ld, over, span, where, cols, ring_rows, r0, r1, body_span, edge, t0, ye, width):
    """Information only, never a gate (Liam, 2026-10-15): the building's body behind the joint,
    the ground in the band from it to the pipe, and the building seen beside the pipe."""
    def full(r, a, b):
        return all(Bd[c, r] > EDGE for c in range(a, b + 1))
    body, rule = None, "ring"
    for r in range(t0, t0 - 2 * PPT, -1):
        if full(r, r0, r1):
            body = r
            break
    if body is None:
        rule = "pipe body"
        for r in range(t0, t0 - 2 * PPT, -1):
            if full(r, *body_span):
                body = r
                break
    if body is None:
        res["body"] = None
        return [], []
    found = body
    axc = min(max(int((cols[0] + cols[-1] + 1) / 2), cols[0]), cols[-1])

    def width_at(r):
        if Bd[axc, r] <= EDGE:
            return 0
        a = b = axc
        while a - 1 >= 0 and Bd[a - 1, r] > EDGE:
            a -= 1
        while b + 1 < width and Bd[b + 1, r] > EDGE:
            b += 1
        return b - a + 1
    while body + 1 < ye + PPT and width_at(body + 1) >= PPT:
        body += 1
    res["body"] = dict(rule=rule, found_row_px=found - ye, last_row_px=body - ye)

    def band(c0, c1):
        n, gaps = 0, []
        for c in range(c0, c1 + 1):
            for r in range(body + 1, edge[c]):
                n += 1
                if Bd[c, r] <= COVER and not Pd[c, r]:
                    gaps.append((c, r))
        return n, gaps
    n, gaps = band(*body_span)
    rn, rgaps = band(r0, r1)
    sides = [r for r in ring_rows if span(r) and span(r)[1] - span(r)[0] + 1 >= r1 - r0 + 1 - 4]
    beside, strict = [], []
    for r in range(body + 1, ye + PPT):
        a, b = (r0, r1) if r <= sides[-1] else (span(r) or body_span)
        for c in cols:
            if not Bd[c, r] > COVER or (over and Pd[c, r]):
                continue                             # no building here, or the pipe drawn over it
            if not r0 <= c <= r1:
                strict.append((c, r))
            if r >= sides[0] and not a - RING_AA <= c <= b + RING_AA and Ld[c, r]:
                beside.append((c, r))
    res["band"] = dict(note="information only", width="pipe body", px=n, ground_px=len(gaps), where=where(gaps))
    res["ring_band"] = dict(note="information only", width="ring", px=rn, ground_px=len(rgaps), where=where(rgaps))
    res["beside"] = dict(note="information only: building seen beside the ring or the pipe; vanilla does it "
                              "everywhere", px=len(beside), where=where(beside),
                         rows_px=[max(body + 1, sides[0]) - ye, PPT - 1], edge_allowance_px=RING_AA,
                         shadow=f"max channel < {DARK} and alpha < {SOLID}, or max channel < {BLACK}")
    res["beside_strict"] = dict(note="information only: every seen building pixel outside the ring's exact width "
                                     "from the body to the far end of the pipe's tile, dark ones too",
                                px=len(strict), where=where(strict))
    return beside, strict


def finish_join(res, comp, gaps, beside, face, conn, src, strict=()):
    """The join's two pictures at 4x, in the direction as drawn: plain, and marked."""
    mark = Image.new("RGB", comp.size)
    if gaps or beside or strict:
        size = comp.size
        m = Image.new("RGB", size)
        px = m.load()
        for c, r in strict:
            px[c, r] = (120, 60, 130)
        for c, r in gaps or ():
            px[c, r] = BAD
        for c, r in beside or ():
            px[c, r] = (255, 0, 255)
        op = FROM_SOUTH[face]
        mark = m.transpose(op) if op is not None else m
    x, y, _ = conn
    dx, dy = FACE[face]
    jx = src.origin[0] + (x + dx / 2) * PPT
    jy = src.origin[1] + (y + dy / 2) * PPT
    box = (round(jx - 80), round(jy - 80), round(jx + 80), round(jy + 80))
    plain = comp.crop(box)
    mask = mark.convert("L").point(lambda v: 255 if v else 0)
    marked = Image.composite(mark, Image.blend(comp, Image.new("RGB", comp.size, BG), 0.45), mask).crop(box)
    return res, (plain.resize((640, 640), Image.NEAREST), marked.resize((640, 640), Image.NEAREST))


# ---------------------------------------------------------------- collide

# Blender's C output and its Python's share the pipe; Python block-buffered there is flushed mid-line
# (a "Blender 5.0.1 (hash ...)" header landed inside the Reaction Plant's count line), so a COLLIDE
# line could be cut in two and lost. Line-buffered, Python only ever hands over whole lines.
LINE_BUFFERED = "import sys; sys.stdout.reconfigure(line_buffering=True); sys.stderr.reconfigure(line_buffering=True)"
COLLIDE_COUNT = re.compile(r"(?:clashes|overlaps:?)\s+(\d+)|(\d+)\s+clashes\b")
NUMBER = re.compile(r"[-+]?\d+(?:\.\d+)?")


def allow_patterns(patterns):
    """--collide-allow's patterns, compiled; a bad one, or one matching the empty string (it would
    allow anything a broader pattern could), is bad input."""
    out = []
    for p in patterns:
        try:
            rx = re.compile(p)
        except re.error as e:
            raise Usage(f"--collide-allow {p!r} is not a regular expression: {e}") from None
        if rx.fullmatch(""):
            raise Usage(f"--collide-allow {p!r} matches the empty string: write it for the pair lines it allows")
        out.append((p, rx))
    return out


def collide_text(line):
    """A COLLIDE line's text after "COLLIDE " (the line already stripped)."""
    return line[len("COLLIDE"):].strip()


def names_pair(text):
    """Whether a COLLIDE line's text names a pair: an "x" word between two words that are not
    both numbers ("a x b", "Cube.001 x Cube.002"; not "grid 3 x 5")."""
    w = text.split()
    return any(t == "x" and 0 < i < len(w) - 1
               and not (NUMBER.fullmatch(w[i - 1]) and NUMBER.fullmatch(w[i + 1].rstrip(":,;")))
               for i, t in enumerate(w))


def collide(model, out, blender, allow=()):
    """The model's --collide, read (see the module docstring). allow: patterns (strings) for the
    pair lines the model means, each matched against the whole of a pair line's text after
    "COLLIDE "; each pair line one matches is listed as allowed, with it."""
    allow = allow_patterns(allow)
    d = os.path.join(out, "collide")
    os.makedirs(d, exist_ok=True)
    log = os.path.join(out, "collide.log")
    res = dict(model=os.path.abspath(model), log=log, allow=[p for p, _ in allow])
    if not blender:
        res.update(returncode=None, lines=[], clash_lines=[], counts=[], allowed=[], not_allowed=[],
                   allow_unused=[p for p, _ in allow],
                   why="$BLENDER is not set: no Blender to run the model's --collide with")
        res["pass"] = False
        return res
    try:
        p = subprocess.run([blender, "-b", "--python-exit-code", "1", "--python-expr", LINE_BUFFERED,
                            "--python", os.path.abspath(model), "--", d, "--collide"],
                           capture_output=True, text=True, timeout=1800)
        text, code = p.stdout + p.stderr, p.returncode
    except (OSError, subprocess.TimeoutExpired) as e:
        text, code = str(e), None
    with open(log, "w") as f:
        f.write(text)
    lines = [ln for ln in (raw.strip() for raw in text.splitlines()) if re.match(r"COLLIDE\b", ln)]
    counts = [int(a or b) for ln in lines for a, b in COLLIDE_COUNT.findall(ln)]
    pairs = [ln for ln in lines if names_pair(collide_text(ln))]
    allowed, not_allowed = [], []
    for ln in pairs:
        hit = next((p for p, rx in allow if rx.fullmatch(collide_text(ln))), None)
        if hit is None:
            not_allowed.append(ln)
        else:
            allowed.append(dict(line=ln, pattern=hit))
    why = []
    if code != 0:
        why.append(f"Blender exited {code} (see {log})")
    if "Traceback" in text:
        why.append(f"the model raised an exception (a Traceback in {log})")
    if not lines:
        why.append("the model printed no COLLIDE line: has it a --collide?")
    elif not counts:
        why.append("the model printed no clash count")
    if not_allowed:
        why.append(f"{len(not_allowed)} clash line(s) not allowed ({len(allowed)} allowed), counts {counts}")
    elif sum(counts) > len(allowed):
        why.append(f"counts {counts} come to {sum(counts)} clash(es), more than the {len(allowed)} "
                   f"allowed pair line(s) account for")
    res.update(returncode=code, lines=lines, clash_lines=pairs, counts=counts, allowed=allowed,
               not_allowed=not_allowed, allow_unused=[p for p, _ in allow if p not in {a["pattern"] for a in allowed}],
               why="; ".join(why) or None)
    res["pass"] = not why
    return res


# ---------------------------------------------------------------- vanilla references

REFS = {
    "steam-turbine": dict(label="steam turbine", footprint=(3, 5), layers={
        "north": [("base/graphics/entity/steam-turbine/steam-turbine-V.png", "base"),
                  ("base/graphics/entity/steam-turbine/steam-turbine-V-shadow.png", "shadow")],
        "east": [("base/graphics/entity/steam-turbine/steam-turbine-H.png", "base"),
                 ("base/graphics/entity/steam-turbine/steam-turbine-H-shadow.png", "shadow")]}),
    "steam-engine": dict(label="steam engine", footprint=(3, 5), layers={
        "north": [("base/graphics/entity/steam-engine/steam-engine-V.png", "base"),
                  ("base/graphics/entity/steam-engine/steam-engine-V-shadow.png", "shadow")],
        "east": [("base/graphics/entity/steam-engine/steam-engine-H.png", "base"),
                 ("base/graphics/entity/steam-engine/steam-engine-H-shadow.png", "shadow")]}),
    "assembling-machine-3": dict(label="assembling machine 3", footprint=(3, 3), layers={
        "*": [("base/graphics/entity/assembling-machine-3/assembling-machine-3-base.png", "base"),
              ("base/graphics/entity/assembling-machine-3/assembling-machine-3-anim.png", "base"),
              ("base/graphics/entity/assembling-machine-3/assembling-machine-3-shadow.png", "shadow")]}),
    # entities.lua passes shift = util.by_pixel(0, -9) to these sprite_loads: added to the sidecar's
    "chemical-plant": dict(label="chemical plant", footprint=(3, 3), layers={
        d: [(f"base/graphics/entity/chemical-plant/chemical-plant-{d}-base.png", "base", dict(add=(0, -18))),
            (f"base/graphics/entity/chemical-plant/chemical-plant-{d}-anim-1.png", "base", dict(add=(0, -18))),
            (f"base/graphics/entity/chemical-plant/chemical-plant-{d}-anim-2.png", "base", dict(add=(0, -18))),
            ("base/graphics/entity/chemical-plant/chemical-plant-shadow.png", "shadow")]
        for d in ("north", "east", "south", "west")}),
    "oil-refinery": dict(label="oil refinery", footprint=(5, 5), layers={
        d: [(f"base/graphics/entity/oil-refinery/{d}/oil-refinery-{d}.png", "base"),
            (f"base/graphics/entity/oil-refinery/{d}/oil-refinery-shadow-{d}.png", "shadow")]
        for d in ("north", "east", "south", "west")}),
    "pumpjack": dict(label="pumpjack", footprint=(3, 3), layers={
        # the base's file name is built in mining-drill.lua (flipped or not), so its numbers are
        # copied from there: width 261, height 273, shift by_pixel(-2.25, -4.75) and (-2, -5);
        # the sheet holds one direction a column (x = width * (i - 1))
        d: [("base/graphics/entity/pumpjack/pumpjack-base.png", "base",
             dict(geom=(261, 273, (-4.5, -9.5)), col=i)),
            ("base/graphics/entity/pumpjack/pumpjack-horsehead.png", "base"),
            ("base/graphics/entity/pumpjack/pumpjack-base-shadow.png", "shadow",
             dict(geom=(261, 273, (-4.0, -10.0)), col=i)),
            ("base/graphics/entity/pumpjack/pumpjack-horsehead-shadow.png", "shadow")]
        for i, d in enumerate(("north", "east", "south", "west"))}),
    "fusion-generator": dict(label="fusion generator (working)", footprint=(3, 5), layers={
        d: [(f"space-age/graphics/entity/fusion-generator/{d}/fusion-generator-{d}.png", "base"),
            (f"space-age/graphics/entity/fusion-generator/{d}/fusion-generator-{d}-shadow.png", "shadow"),
            (f"space-age/graphics/entity/fusion-generator/{d}/fusion-generator-{d}-glow.png", "glow")]
        for d in ("north", "east", "south", "west")}),
    "foundry": dict(label="foundry", footprint=(5, 5), layers={
        "*": [("space-age/graphics/entity/foundry/foundry-base.png", "base"),
              ("space-age/graphics/entity/foundry/foundry-anim-1.png:foundry-anim.lua", "base"),
              ("space-age/graphics/entity/foundry/foundry-shadow.png", "shadow")]}),
    "electromagnetic-plant": dict(label="electromagnetic plant", footprint=(4, 4), layers={
        "*": [("space-age/graphics/entity/electromagnetic-plant/electromagnetic-plant-base.png", "base"),
              ("space-age/graphics/entity/electromagnetic-plant/electromagnetic-plant-main-rotate-1.png:"
               "electromagnetic-plant-main-rotate.lua", "base"),
              ("space-age/graphics/entity/electromagnetic-plant/electromagnetic-plant-base-shadow.png", "shadow")]}),
}
REF_DIR = {"": "north", "north": "north", "vertical": "north", "east": "east", "horizontal": "east",
           "south": "south", "west": "west"}
_PROTOS = None


def _shift(text):
    m = re.search(r"shift\s*=\s*util\.by_pixel(_hr)?\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)", text)
    if m:
        k = 1 if m.group(1) else 2                      # by_pixel: 32 px a tile; _hr: 64
        return float(m.group(2)) * k, float(m.group(3)) * k
    m = re.search(r"shift\s*=\s*\{\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\}", text)
    return (float(m.group(1)) * PPT, float(m.group(2)) * PPT) if m else (0.0, 0.0)


def sprite_geometry(rel):
    """(png path, width, height, shift px at 64 a tile, scale) of a vanilla sprite: from the .lua
    beside it (util.sprite_load, scale 0.5) or the prototype table that names it."""
    rel, _, side = rel.partition(":")
    png = os.path.join(FD, rel)
    lua = os.path.join(os.path.dirname(png), side) if side else png[:-4] + ".lua"
    if os.path.isfile(lua):
        with open(lua) as f:
            text, scale = f.read(), 0.5
    else:
        global _PROTOS
        if _PROTOS is None:
            _PROTOS = []
            for path_ in glob.glob(os.path.join(FD, "*", "prototypes", "**", "*.lua"), recursive=True):
                with open(path_) as f:
                    _PROTOS.append(f.read())
        mod, path = rel.split("/", 1)
        name = f'"__{mod}__/{path}"'
        text = None
        for t in _PROTOS:
            i = t.find(name)
            if i < 0:
                continue
            a, depth = i, 0
            while a > 0:
                a -= 1
                depth += {"}": 1, "{": -1}.get(t[a], 0)
                if depth < 0:
                    break
            b, depth = i, 0
            while b < len(t):
                depth += {"{": 1, "}": -1}.get(t[b], 0)
                if depth < 0:
                    break
                b += 1
            text = t[a:b]
            break
        if text is None:
            raise Usage(f"vanilla sprite {rel}: neither a .lua beside it nor a prototype naming it")
        m = re.search(r"scale\s*=\s*([\d.]+)", text)
        scale = float(m.group(1)) if m else 1.0
    w = int(re.search(r"width\s*=\s*(\d+)", text).group(1))
    h = int(re.search(r"height\s*=\s*(\d+)", text).group(1))
    return png, w, h, _shift(text), scale


def vanilla_sprite(rel, opts=None):
    """A vanilla sprite's frame 0 at 64 px a tile, and its shift in px: (image, sx, sy). opts:
    geom (w, h, (sx, sy)) when no .lua gives them; add (x, y) px, the prototype's own shift
    option, which util.sprite_load adds to the sidecar's; col, the frame column to take."""
    opts = opts or {}
    if "geom" in opts:
        (w, h, (sx, sy)), png, scale = opts["geom"], os.path.join(FD, rel.partition(":")[0]), 0.5
    else:
        png, w, h, (sx, sy), scale = sprite_geometry(rel)
    col = opts.get("col", 0)
    im = load(png).crop((col * w, 0, col * w + w, h))
    if abs(scale - 0.5) > 1e-6:
        k = scale * 2
        im = im.resize((round(w * k), round(h * k)), Image.LANCZOS)
    ax, ay = opts.get("add", (0, 0))
    return im, sx + ax, sy + ay


def vanilla(name, dn):
    """A reference in one of our directions: (label, footprint as it stands, still, shadow, light)
    on a canvas of its own, the origin at its centre."""
    ref = REFS[name]
    key = REF_DIR[dn]
    lays = ref["layers"].get(key) or ref["layers"].get("*") or ref["layers"].get(
        {"south": "north", "west": "east"}.get(key, "north")) or ref["layers"]["north"]
    fw, fh = ref["footprint"]
    foot = (fh, fw) if key in ("east", "west") else (fw, fh)
    parts = []
    for rel, role, *opts in lays:
        im, sx, sy = vanilla_sprite(rel, opts[0] if opts else None)
        parts.append((im, sx, sy, role))
    half = max([(max(foot) / 2 + 1) * PPT] + [max(abs(sx) + im.width / 2, abs(sy) + im.height / 2)
                                             for im, sx, sy, _ in parts])
    S = 2 * math.ceil(half + 4)
    still, shadow, light = Image.new("RGBA", (S, S)), Image.new("RGBA", (S, S)), Image.new("RGB", (S, S))
    for im, sx, sy, role in parts:
        lay = Image.new("RGBA", (S, S))
        lay.alpha_composite(im, (round(S / 2 + sx - im.width / 2), round(S / 2 + sy - im.height / 2)))
        if role == "shadow":
            a = lay.getchannel("A").point(lambda v: v // 2)
            shadow.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", lay.size).split(), a)))
        elif role == "glow":
            light = ImageChops.add(light, light_of(lay))
        else:
            still.alpha_composite(lay)
    return f"{ref['label']} ({key})", foot, still, shadow, light


def vanilla_figures(still, light, foot):
    S = still.width
    drawn = ImageChops.add(on_ground(still), light)
    out = dict(coverage=coverage(still, foot, (S / 2, S / 2)), tonal=tonal(still), finish=finish(still),
               colour=colour(drawn, still, still))
    if light.getbbox():
        out["glow"] = light_measures(light)
    return out


# ---------------------------------------------------------------- the sheet

def font(size, bold=False):
    f = "/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if bold else "") + ".ttf"
    return ImageFont.truetype(f, size) if os.path.exists(f) else ImageFont.load_default()


def captioned(im, lines, colour_=TXT):
    f = font(13)
    lines = [ln for ln in lines if ln]
    w = max([im.width] + [int(f.getlength(ln)) + 6 for ln in lines])
    out = Image.new("RGB", (w, im.height + 18 * len(lines) + 4), BG)
    d = ImageDraw.Draw(out)
    for i, ln in enumerate(lines):
        d.text((0, 18 * i), ln, font=f, fill=colour_ if i == 0 else TXT)
    out.paste(im.convert("RGB"), (0, 18 * len(lines) + 4))
    return out


def text_block(title, lines, width):
    f, fb = font(13), font(16, True)
    wrapped = []
    for ln in lines:
        while ln:
            cut = len(ln)
            while cut > 1 and f.getlength(ln[:cut]) > width - 20:
                cut = ln.rfind(" ", 0, cut - 1) if ln.rfind(" ", 0, cut - 1) > 0 else cut - 1
            wrapped.append(ln[:cut])
            ln = ln[cut:].lstrip()
    out = Image.new("RGB", (width, 30 + 17 * len(wrapped) + 8), BG)
    d = ImageDraw.Draw(out)
    d.text((0, 4), title, font=fb, fill=HEAD)
    for i, ln in enumerate(wrapped):
        d.text((0, 30 + 17 * i), ln, font=f, fill=TXT)
    return out


def rows_of(panels, max_w, gap=16):
    """Panels laid in rows no wider than max_w (a panel wider than that is scaled to fit)."""
    rows, cur, w = [], [], 0
    for p in panels:
        if p.width > max_w or p.height > max_w:
            k = min(max_w / p.width, max_w / p.height)
            p = p.resize((max(1, int(p.width * k)), max(1, int(p.height * k))), Image.LANCZOS)
        if cur and w + gap + p.width > max_w:
            rows.append(cur)
            cur, w = [], 0
        w += (gap if cur else 0) + p.width
        cur.append(p)
    if cur:
        rows.append(cur)
    out = []
    for r in rows:
        im = Image.new("RGB", (sum(p.width for p in r) + gap * (len(r) - 1), max(p.height for p in r)), BG)
        x = 0
        for p in r:
            im.paste(p, (x, 0))
            x += p.width + gap
        out.append(im)
    return out


PAGE_PAD = 18


def page_inner(max_side, pad=PAGE_PAD):
    """The widest (and tallest) block a page under max_side holds: max_side - 1 less the pads."""
    return max_side - 1 - 2 * pad


def pages(blocks, max_side, pad=PAGE_PAD, gap=14):
    """Stack blocks into images strictly under max_side either way (at most max_side - 1); returns
    the pages and the size one unsplit image would have had."""
    inner = page_inner(max_side, pad)
    blocks = [b for blk in blocks for b in (rows_of([blk], inner) if blk.width > inner or blk.height > inner
                                            else [blk])]
    unsplit = (max(b.width for b in blocks) + 2 * pad,
               sum(b.height for b in blocks) + gap * (len(blocks) - 1) + 2 * pad)
    out, cur, h = [], [], 0
    for b in blocks:
        if cur and h + gap + b.height > inner:
            out.append(cur)
            cur, h = [], 0
        h += (gap if cur else 0) + b.height
        cur.append(b)
    if cur:
        out.append(cur)
    ims = []
    for pg in out:
        im = Image.new("RGB", (max(b.width for b in pg) + 2 * pad, sum(b.height for b in pg) + gap * (len(pg) - 1)
                               + 2 * pad), BG)
        y = pad
        for b in pg:
            im.paste(b, (pad, y))
            y += b.height + gap
        ims.append(im)
    return ims, unsplit


def crop_to(im_list, pad=12):
    box = None
    for im in im_list:
        b = (im.getchannel("A") if im.mode == "RGBA" else im.convert("L")).getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    if box is None:
        return (0, 0, im_list[0].width, im_list[0].height)
    W, H = im_list[0].size
    return (max(0, box[0] - pad), max(0, box[1] - pad), min(W, box[2] + pad), min(H, box[3] + pad))


def footprint_outline(im, foot, origin, colour_=(110, 100, 90)):
    d = ImageDraw.Draw(im)
    fw, fh = foot
    x0, y0 = origin[0] - fw * PPT / 2, origin[1] - fh * PPT / 2
    d.rectangle((x0, y0, x0 + fw * PPT - 1, y0 + fh * PPT - 1), outline=colour_)
    return im


def seen(still, shadow, foot, origin, light=None):
    g = Image.new("RGBA", still.size, GROUND + (255,))
    footprint_outline(g, foot, origin)
    g.alpha_composite(shadow)
    g.alpha_composite(still)
    rgb = g.convert("RGB")
    return ImageChops.add(rgb, light) if light is not None else rgb


def fig_line(m):
    c, t, f = m.get("coverage", {}), m.get("tonal") or {}, m.get("finish") or {}
    if "plate" in t:
        t, f = t.get("still") or {}, f.get("still") or {}
    cn = c.get("corners_pct", {})
    return [f"cover {c.get('footprint_pct')} %, mass {c.get('mass_pct')} %, band {c.get('outer_band_pct')} %, "
            f"rise {c.get('rise_tiles')} t",
            f"corners NW {cn.get('NW')} NE {cn.get('NE')} SW {cn.get('SW')} SE {cn.get('SE')}",
            f"p50 {t.get('p50')} p95 {t.get('p95')} spread {t.get('spread')}; black {f.get('black_pct')} % "
            f"ratio {f.get('ratio')} darkchr {f.get('darkchr')}"]


def build_sheet(title, result, scenes, maps, pictures, refs, ports_png, max_side, out):
    blocks = []
    head = [f"source: {result['source']['src']}", f"directions: {result['source']['directions']}, footprint "
            f"{result['source']['footprint'][0]}x{result['source']['footprint'][1]} (as it faces north), 64 px a tile; "
            f"ground {GROUND}, shadows at half strength, glow added (emulated, not from a client)"]
    g = result["gates"]
    head.append("gates: joins " + ("none measured" if g["joins"] is None else "PASS" if g["joins"] else "FAIL")
                + ", collide " + ("not run" if g["collide"] is None else "PASS" if g["collide"] else "FAIL"))
    if result.get("collide"):
        c = result["collide"]
        head.append(f"collide: {c['model']}: " + (c["why"] or "no clash; " + "; ".join(c["lines"][-3:])))
        head += [f"collide: allowed by {al['pattern']!r}: {al['line']}" for al in c["allowed"]]
    blocks.append(text_block(title, head, 1600))
    for dn, sc in scenes.items():
        m = result["directions"][dn]
        foot = m["coverage"]["footprint"]
        ims = [seen(sc.still, sc.shadow, foot, sc.src.origin)]
        if sc.glows or sc.loop > 1:
            ims.append(seen(sc.paint(0), sc.shadow, foot, sc.src.origin, sc.light(0)))
        box = crop_to([sc.still, sc.shadow] + ([sc.light(0)] if sc.glows else []))
        panels = [captioned(ims[0].crop(box), [f"OURS {dn or '(one direction)'}, as seen (the still), 1x"]
                            + fig_line(m))]
        if len(ims) > 1:
            col = m["colour"]
            panels.append(captioned(ims[1].crop(box), ["working frame 0, light added, 1x",
                                                       f"blue {col['blue_pct']} %, pale {col['pale_px']} px, orange "
                                                       f"{col['orange_pct']} %",
                                                       f"white {col['white_px']} px, clipped {col['clipped_px']} px"]))
        if maps:
            mm = maps[dn]
            mv = Image.blend(on_ground(sc.still), Image.new("RGB", sc.still.size, BG), 0.5)
            mv.paste((255, 0, 255), mask=mm["moving"])
            mv.paste((0, 230, 255), mask=mm["strobe"])
            mo = m["motion"]
            panels.append(captioned(mv.crop(box), ["motion map: moving magenta, strobing cyan, 1x",
                                                   f"moving {mo['moving_pct']} %, strobe {mo['strobe_pct']} % "
                                                   f"over {mo['loop_frames']} frames",
                                                   f"wrap {mo['wrap_px']} px against steps "
                                                   f"{min(mo['step_px'] or [0])}-{max(mo['step_px'] or [0])}"]))
        for name in refs:
            label, rfoot, rs, rsh, rl = vanilla(name, dn)
            vm = result["vanilla"][name][dn]
            vb = crop_to([rs, rsh])
            img = seen(rs, rsh, rfoot, (rs.width / 2, rs.height / 2), rl if rl.getbbox() else None).crop(vb)
            panels.append(captioned(img, [f"VANILLA {label}, 1x"] + fig_line(vm), HEAD))
        blocks += rows_of(panels, page_inner(max_side))
        jp = []
        for j, (plain, marked) in zip(m["joins"], pictures[dn]):
            x, y, f = j["connection"]
            state = "PASS" if j["pass"] else "FAIL"
            cap = [f"JOIN {dn or ''} at ({x:g}, {y:g}) face {f}, pipe drawn {j['pipe_drawn']}, 4x: {state}"]
            if "gap" in j:
                g = j["gap"]
                cap.append(f"gap: {g['columns']} of {g['of_columns']} pipe-body columns with "
                           f"{g['ground_px_counted_from']}+ px of ground (at most {g['columns_allowed']}); "
                           f"the most in one {g['max_ground_px']} px")
                if j.get("beside"):
                    cap.append(f"information: beside {j['beside']['px']} px (strict {j['beside_strict']['px']}), "
                               f"band ground {j['band']['ground_px']} px")
            if j.get("why"):
                cap.append(j["why"])
            jp.append(captioned(plain, cap, GOOD if j["pass"] else BAD))
            jp.append(captioned(marked, ["marked: gap columns red (the gate); information only:",
                                         "building beside the pipe magenta, beside_strict's other pixels purple"]))
        if jp:
            blocks += rows_of(jp, page_inner(max_side))
    if ports_png and os.path.isfile(ports_png):
        blocks.append(captioned(Image.open(ports_png).convert("RGB"),
                                ["PORT PICTURES against assembler 3's outline, 6x: assembler 3 blue, ours orange, "
                                 "both white"]))
    lines = []
    for dn in scenes:
        lines.append(f"[{dn or 'one'}] " + json.dumps({k: v for k, v in result["directions"][dn].items()
                                                       if k in ("coverage", "tonal", "finish", "colour", "glow",
                                                                "motion")}))
    blocks.append(text_block("FIGURES (measures.json)", lines, 1600))
    ims, unsplit = pages(blocks, max_side)
    for old in glob.glob(os.path.join(out, "comparison*.png")):
        os.remove(old)
    paths = []
    for i, im in enumerate(ims):
        p = os.path.join(out, "comparison.png" if len(ims) == 1 else f"comparison-{i + 1}.png")
        im.save(p, optimize=True)
        paths.append(dict(path=p, size=list(im.size)))
    return paths, list(unsplit)


# ---------------------------------------------------------------- main

def parse_connection(s):
    m = re.fullmatch(r"\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([NESWnesw])\s*", s)
    if not m:
        raise Usage(f"--connection {s!r} is not X,Y,F (tiles, and a face N, E, S or W)")
    return (float(m.group(1)), float(m.group(2)), m.group(3).upper())


def parse_footprint(s):
    m = re.fullmatch(r"\s*(\d+)\s*[xX]\s*(\d+)\s*", s)
    if not m:
        raise Usage(f"--footprint {s!r} is not WxH in tiles")
    return [int(m.group(1)), int(m.group(2))]


def run(argv):
    ap = argparse.ArgumentParser(prog="measure.py", description="see the module docstring")
    ap.add_argument("src")
    ap.add_argument("--out")
    ap.add_argument("--connection", action="append", default=[])
    ap.add_argument("--vanilla", action="append", default=[])
    ap.add_argument("--collide")
    ap.add_argument("--collide-allow", action="append", default=[])
    ap.add_argument("--footprint")
    ap.add_argument("--directions")
    ap.add_argument("--plate")
    ap.add_argument("--title")
    ap.add_argument("--max-side", type=int, default=MAX_SIDE)
    a = ap.parse_args(argv)
    if not 400 <= a.max_side <= MAX_SIDE:
        raise Usage(f"--max-side {a.max_side}: between 400 and {MAX_SIDE}")
    for name in a.vanilla:
        if name not in REFS:
            raise Usage(f"--vanilla {name!r} is not one of {', '.join(REFS)}")
    if a.collide and not os.path.isfile(a.collide):
        raise Usage(f"--collide {a.collide}: no such model")
    if a.collide_allow and not a.collide:
        raise Usage("--collide-allow without --collide: nothing to allow")
    allow_patterns(a.collide_allow)
    src = Source(a.src, parse_footprint(a.footprint) if a.footprint else None, a.directions, a.plate)
    conns = src.connections([parse_connection(c) for c in a.connection])
    out = os.path.abspath(a.out or os.path.join(src.src, "measures"))
    if not a.out and "concept" in out.split(os.sep):
        raise Usage(f"--out is needed: the default, {out}, is inside a concept/ folder (committed design); "
                    f"give a directory outside it")
    os.makedirs(out, exist_ok=True)

    result = dict(source=dict(src=src.src, sheets=src.sheets, render_json=src.render_json,
                              directions=src.directions, footprint=src.footprint, px_per_tile=PPT,
                              connections=[list(c) for c in conns], vanilla=a.vanilla))
    result["collide"] = collide(a.collide, out, os.environ.get("BLENDER"), a.collide_allow) if a.collide else None

    result["directions"], scenes, maps, pictures = {}, {}, {}, {}
    for dn in src.dirs:
        m, sc, mp, pics = measure_direction(src, dn, conns)
        result["directions"][dn] = m
        scenes[dn], pictures[dn] = sc, pics
        if mp:
            maps[dn] = mp
    ports_png = None
    result["ports"] = None
    if src.ports and all(f"port-{f}" in src.port_meta for f in "NESW"):
        ports_png = os.path.join(out, "ports-vs-assembler-3.png")
        result["ports"] = measure_ports.main(src.ports, ports_png, quiet=True)
    result["vanilla"] = {}
    for name in a.vanilla:
        result["vanilla"][name] = {}
        for dn in src.dirs:
            _, foot, still, _, light = vanilla(name, dn)
            result["vanilla"][name][dn] = vanilla_figures(still, light, foot)

    joins = [j for dn in src.dirs for j in result["directions"][dn]["joins"]]
    result["gates"] = dict(joins=all(j["pass"] for j in joins) if joins else None,
                           collide=result["collide"]["pass"] if result["collide"] else None)
    result["pass"] = all(v is not False for v in result["gates"].values())
    title = a.title or f"measure.py: {src.src}"
    result["sheets"], result["sheet_unsplit_px"] = build_sheet(title, result, scenes, maps, pictures,
                                                               a.vanilla, ports_png, a.max_side, out)
    with open(os.path.join(out, "measures.json"), "w") as f:
        json.dump(result, f, indent=1)

    print(f"measures: {os.path.join(out, 'measures.json')}")
    for s in result["sheets"]:
        print(f"sheet: {s['path']} {s['size'][0]}x{s['size'][1]}")
    failed = []
    for dn in src.dirs:
        for j in result["directions"][dn]["joins"]:
            line = f"join {dn or '(one)'} {j['connection']}: " + ("PASS" if j["pass"] else f"FAIL: {j['why']}")
            print(line)
            if not j["pass"]:
                failed.append(line)
    if result["collide"]:
        c = result["collide"]
        for al in c["allowed"]:
            print(f"collide: allowed by {al['pattern']!r}: {al['line']}")
        for p in c["allow_unused"]:
            print(f"collide: --collide-allow {p!r} matched no pair line")
        line = "collide: " + ("PASS" if c["pass"] else f"FAIL: {c['why']}")
        print(line)
        if not c["pass"]:
            failed.append(line)
    if failed:
        print(f"measure.py: {len(failed)} gate(s) failed (numbers in {os.path.join(out, 'measures.json')})",
              file=sys.stderr)
        return 1
    return 0


def main():
    try:
        sys.exit(run(sys.argv[1:]))
    except Usage as e:
        print(f"measure.py: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
