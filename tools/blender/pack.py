#!/usr/bin/env python3
"""Pack a render directory into the sheets the prototype loads, with their numbers.

  python3 pack.py <render-dir> <out-dir>

What to pack comes from the model's render.json (contract.py): its passes, its
animations, its directions, its footprint and its canvas. Every pass was
rendered on that one canvas with the entity origin exactly at its centre, so
every layer's shift is its crop's centre minus that point, computed rather than
measured and adjusted. Crops keep a 1 px transparent rim. A glow pass drops its
isolated specks of render noise (SPECK_PX) from both its crop and its sheet, so its
size and shift do not change from one render of the same model to the next, and then
keeps only the smallest box that holds LIGHT_SHARE (99.9 %) of its light -- alpha times
luminance -- so a faint haze too wide to be a speck does not stretch it either (glow_layer).
An animated glow keeps every pixel of its light, its faint tail too (GLOW_FLOOR).

Sheets are named for the pass's declared sheet (and the animation's name), with
-<direction> after it when the model has more than one direction; meta.json
keys are the sheet names. Its "checks" are per direction when there are several.

An animated glow layer (an animation of kind "glow", contract.py) is packed like
any animation, each frame turned to light first (glow_frame): its checks are
<name>_white_px (pixels of the light itself clipped to white), <name>_clipped_px
(pixels it drives to white added over its plate layer's frame on the plate, that
were not white without it -- with every other glow over the same plate layer added
too, as the engine draws them), both the most in any frame and both 0 to pass,
<name>_frames (its frames and its plate layer's, equal), <name>_edge_px (pixels of
the light, bloom and all, on the canvas's edge, the most in any frame: 0 to pass,
or the edge cuts the tail) and <name>_light (frame 0's peak luminance and its core
and halo shares, as the radiant-look study measured vanilla's glows:
concept/radiant-look/model/look_common.py).

An animation that declares a frame_sequence or a hold (contract.py) is packed like any
other, its frames once each in order; its meta.json entry gains frame_sequence, the
order the engine plays them in (1-based, a hold written out: the prototype's
frame_sequence as it stands), and its checks <name>_sequence: the entries it plays
(the actual length every other layer drawn with it must have) and the frames it never
shows. A glow animation carries its plate layer's. An animation that declares an
animation_speed gets it in its meta.json entry as animation_speed, as declared (a glow its
plate layer's), for measure.py to play it at.

The footprint cut (render.json's `cut`, contract.py): before anything is packed or
checked, every render but a shadow's -- plate, still, glow, paint and light passes,
and every animation frame -- is cleared past the footprint's edges it names (not a
slide's tracked part either: it is only measured, for its centroid, and never drawn),
as the footprint stands in that direction (cut_mask), so the plate and a glow's own
pixels are no wider (E, W) or lower (S) than the footprint. A glow animation's bloom
(glow_frame) is added after the cut, from the light the cut left, so its halo may spill
past a cut edge, as light does (Liam, 2026-10-19: "Halo may cross"). checks cut_px
gives, per render, the pixels with any alpha the cut cleared or thinned, counted on the
render before any bloom; {} = nothing reached past the edge.

The remnants pass (kind "remnants", contract.py): the wreck the corpse prototype draws, its
shadow baked in. Vanilla's building remnants are one sprite sheet with the shadow in it and no
shadow layer of its own (base/prototypes/entity/remnants.lua: steam-turbine-remnants at
2739-2765, steam-engine 1073-1099, boiler 1129-1155, chemical plant 2907-2933), whose
part-transparent pixels are near black (those under alpha 200 average RGB 1-8 at alpha 60-90,
on those four and on assembling machine 2's and the electric mining drill's): the shadow and
the darkened ground round the wreck. So the render is cleaned of the catcher's haze below NOISE, as a shadow is, and
otherwise packed as it is, colour, shadow and all, and it is never cut. Every direction's
render goes into one sheet, as vanilla's: one column (line_length 1), one row per entry of
contract.remnant_rows -- north, east, south, west for "four"; vertical, horizontal, vertical,
horizontal for "horizontal-vertical", as steam-turbine-remnants repeats its two; one row for
"one" -- every row cropped to the one box that holds every direction's wreck (with the 1 px
rim), since a RotatedAnimation has one size and one shift for all its directions. The shift is
from the centre of the pass's own canvas (contract.canvas_of). Its meta.json entry, keyed by
the pass's sheet with no direction after it: size (one row), shift, direction_count (the rows),
line_length 1, rows (the render drawn in each row, top to bottom), kind "remnants" and
final_render_layer "remnants" (what every vanilla building's remnants set, remnants.lua:2753;
the corpse's default is "corpse", CorpsePrototype). It goes after every other sheet, before
"checks". Checks, per direction (the sheet's name before each):
  _shadow_px    the shadow baked in: pixels part transparent (alpha under 255) and near black
                (every channel at or under SHADOW_RGB), and their share of the wreck's area
                (every pixel kept, alpha above NOISE). Fewer than SHADOW_MIN_PX, or a share under
                SHADOW_SHARE, fails the pack: a wreck lies on the ground, and one rendered
                without the catcher has no shadow but its edges' anti-aliasing over nothing
  _edge_px      pixels of it (alpha above NOISE) on its canvas's outermost row or column: 0, or
                the canvas cuts the wreck or its shadow off (a remnants pass may have a canvas
                of its own, larger, for that); above 0 fails the pack
  _reach_tiles  how far past each edge of the footprint (N, E, S, W, the footprint as it stands
                in that direction, on the screen) the debris -- pixels of the wreck itself,
                alpha over DEBRIS_ALPHA and not near black -- and everything kept (the shadow
                too) reach, in tiles; below 0, short of the edge. Information: vanilla's
                turbine keeps its debris inside (-0.45 to -0.03) and its shadow reaches 0.11 to
                0.64; the chemical plant's debris goes 0.61 past its north edge, its shadow 2.23
                past its east.

The highlight roll-off (Liam, 2026-10-20, the Vent Pump's: "Accept, add to the shared rig", then
"On by default, new renders only"; then "Yes, animations and wrecks too"): every sheet the engine
draws as it is -- plate, glow and paint passes, every animation but a light one, and the remnants
sheet -- is rolled off as it is written (roll): a pixel whose brightest channel m passes KNEE (236) is
scaled whole, every channel by the one factor that takes m to KNEE + (TOP - KNEE) *
(1 - exp(-(m - KNEE) / (TOP - KNEE))) -- TOP 244: 255 lands on 243.3, so once rounded no channel is
over 244, and no rolled pixel is white to white() or measure.py's white_px (every channel 245 or over) --
each channel rounded up or down, whichever of the eight keeps the hue nearest the pixel's own
(within 0.49 degrees on every colour; a grey stays grey) and then lies nearest the exact scale.
Alpha is never touched, nor is any pixel at or under KNEE, so crops, sizes and shifts are as
they were. Only the sheets change: every check is made on the renders as rendered (a glow
animation's white and clipped pixels too), so the roll-off never hides a light the model
over-drives. Light passes and light animations are never rolled: their white is the engine's to
tint. Nor is a shadow, which is black. checks rolloff_px gives, per direction, each rolled sheet's
pixels changed and the most any channel moved (the remnants sheet's, that direction's render in
it). preview.py draws through the same roll-off, so the review is what ships (Liam: "Match
shipped"). A model opts out with "rolloff": false in render.json (contract.py); its sheets and
meta.json are then as before the roll-off, byte for byte, and so is its preview.

Exits 1, naming the animation and the direction, when a turning part's centroid
drifts by more than LIMIT_PX across its frames, or a sliding part's is more than
LIMIT_PX off its declared curve or off its line in any frame, measured from frame 0
(Packer.slide; naming those frames), or a glow animation clips or
reaches the canvas's edge, or a wreck has no shadow or reaches its canvas's edge.
meta.json is written first.
"""
import functools
import itertools
import json
import math
import os
import re
import sys
from fractions import Fraction
from PIL import Image, ImageChops, ImageFilter

import contract

# Shadow catchers record faint sky occlusion everywhere; below this is noise. The
# animation checks lean on it: with no floor, that haze pulls box.py's slider
# centroid 1.06 px off, past LIMIT_PX.
NOISE = 24
LIMIT_PX = 1.0      # a turning part's drift, a sliding part's miss off its curve or its line
LAYER_FLOOR = 8     # a working layer's difference from its plate at or under this is sampling noise
# A glow's opaque pixels in a group of fewer than this (8-connected) are noise, not light:
# dropped from its crop and its sheet (glow_layer). Measured 2026-10-10 on box.py's four
# directions from three builds (blender.org's on the GPU and on the CPU, Ubuntu's on the
# CPU): every speck was one pixel, alone, in a row of alpha-3 pixels just under the
# footprint whose green flips between 0 and 85 from render to render (and between the
# lit and unlit passes), so clearing LAYER_FLOOR; two to four a direction, 41 to 118
# rows below the light, taking glow-east from 61x14 to 97x132 or 109x132 by which
# pixels flipped. The reaction plant (GPU and CPU) had a pair and a single of faint
# spill just over the floor (lit adds ~(8, 15, 11)) two and three rows over its windows,
# and on the CPU a lone (63, 0, 0) 39 rows under them, taking its glow from 58x10 to
# 58x13 or 58x52. The smallest real light measured was 46 px (a reaction-plant window;
# the furnace's sight port is 227, box.py's glow 649-708). So: specks of one and two
# pixels seen; 4 drops those with a pixel to spare, and is an order of magnitude under
# any light.
SPECK_PX = 4
# A glow pass (a still glow: one frame, glow_layer) keeps the smallest box that holds this
# share of its light, its light being each pixel's alpha times its luminance (PIL's "L", the
# luma the LAYER_FLOOR cut is made on), and nothing outside it: a faint wide haze over the
# floor, in groups too big to drop as specks, no longer stretches its crop (Liam, 2026-10-20:
# "99.5% of light, stills"; then, shown that 99.5 % also trimmed lit edges -- up to 55 % of the
# peak on the Reaction Plant's legs, 28 % on test/box.py's window -- "Accept, raise to 99.9%").
# Light passes keep their own crop (Liam: "No, glows only"). Glow animations keep every lit
# pixel (GLOW_FLOOR, below).
LIGHT_SHARE = 0.999
# An animated glow's frame (glow_frame) is cut where its light falls to this, not to
# LAYER_FLOOR: a bloom's faint tail fading out over the housing, cut at 8, left a visible
# edge round it (a step of 8 in blue, on test/radiant_box.py with radiant.py's 16 px tail,
# 2026-10-15); at 2 the step is under what the eye takes. Noise is still dropped as specks.
# For that tail it is not cropped to LIGHT_SHARE either: a box cut through a bloom is an edge.
GLOW_FLOOR = 2
MAX_SHEET_W = 8192  # wrap an animation's frames into rows past this
# A remnants render's shadow: a shadow catcher's pixels are black, part transparent; a lit
# part's edge over its own shadow is not (vanilla's remnants' shadows average RGB 1-8)
SHADOW_RGB = 8
DEBRIS_ALPHA = 128  # a remnants pixel above this, and not shadow, is the wreck itself
# The least shadow a wreck may carry, as a share of its area and in pixels. Measured
# 2026-10-20, cleaned below NOISE as pack.py cleans a wreck: vanilla's building remnants carry
# 24-52 % (steam turbine 39.5 and 52.1, steam engine 29.5-29.7, boiler 24.1 and 46.6, chemical
# plant 49.5, assembling machine 2 30.8-36.6, electric mining drill 43.2-47.0, oil refinery
# 25.1, pumpjack 25.5; at least 5625 px); test/box.py's wreck, over the catcher, 2.4-2.7 %
# (428-499 px): low debris on a plinth that covers the footprint casts little; the same wreck
# rendered with no catcher 0.0-0.02 % (0-3 px, the edges' anti-aliasing). So the floor sits
# between that leak and a wreck's least real shadow, not at vanilla's look, which is the
# model's to match (the check prints the share beside vanilla's).
SHADOW_SHARE = 0.01
SHADOW_MIN_PX = 64
# The highlight roll-off (roll): a pixel's brightest channel past KNEE is eased toward TOP. The
# Vent Pump's curve and knee (concept/vent-pump/options/round-5/vp5_shoulder.py and vp5_roll.py,
# vent-pump-model branch). Its top was 250, under its own white count (every channel 250 or over),
# but this pipeline counts white from 245 (white(), measure.py's white_px), and at 250 a rolled glint
# landed on 246 and still counted (Liam, 2026-10-20: "Lower the top to 244"). At 244 the curve
# tops out at 243.3, and rounded up 244: under 245.
KNEE = 236
TOP = 244


def clean(im):
    a = im.getchannel("A").point(lambda v: 0 if v < NOISE else v)
    im.putalpha(a)
    return im


def glow_layer(lit, under):
    """A glow pass's sheet, on the full canvas: lit minus the plate under it, opaque wherever
    that is above noise inside the box that holds LIGHT_SHARE of its light.

    Drawn additively, so its colour is what the light adds. Isolated specks -- any
    8-connected group of fewer than SPECK_PX opaque pixels -- are dropped, colour and
    all, so the crop (and so the sheet's size and shift) is the light's own and does
    not move with render noise; nothing dropped is drawn either. So is every opaque pixel
    outside light_box -- the smallest box holding LIGHT_SHARE of the light the specks left,
    a pixel's light its alpha times its luminance -- so the crop (Packer.box_of, any alpha,
    with its 1 px rim) is that box, and a faint haze too wide to be a speck drops out of the
    sheet instead of stretching it. At a LIGHT_SHARE of 1 the box is every opaque pixel's
    and the sheet is as it was before the box.
    """
    diff = ImageChops.subtract(lit.convert("RGB"), under.convert("RGB"))
    luma = diff.convert("L")
    alpha = luma.point(lambda v: 255 if v > LAYER_FLOOR else 0)
    kept = drop_specks(alpha)
    # alpha is 0 or 255, so a pixel's light is its luminance where it is opaque
    bb = light_box(ImageChops.multiply(luma, kept), LIGHT_SHARE)
    if bb is not None:                  # None, no light: Packer.box_of refuses the empty layer
        inside = Image.new("L", kept.size)
        inside.paste(255, bb)
        kept = ImageChops.multiply(kept, inside)
    # clear the dropped pixels' colour too (a preview adds the colour and ignores alpha);
    # every other pixel, faint or not, is left exactly as it was
    keep = ImageChops.invert(ImageChops.subtract(alpha, kept)).convert("RGB")
    return Image.merge("RGBA", (*ImageChops.multiply(diff, keep).split(), kept))


def light_box(light, share=LIGHT_SHARE):
    """The smallest box (x0, y0, x1, y1, ends exclusive) holding at least `share` of an L
    image's light, the sum of its values; None when it has none.

    Smallest by area, exactly: every pair of rows that could bound it is tried, from the
    rows nearest the light outward, with the narrowest run of columns between them that holds
    the share (two pointers over the columns' sums). Of boxes of one area, the one with the
    most light wins, then the topmost, then the leftmost. A box this small has light on every
    edge, so its bounding box of lit pixels is itself.
    """
    lit = light.getbbox()
    if lit is None:
        return None
    lx, ly, rx, ry = lit
    w, h = rx - lx, ry - ly
    px = list(light.crop(lit).get_flattened_data())
    # cum[y][x]: column x's light in rows above y
    cum = [[0] * w]
    for y in range(h):
        prev, row = cum[-1], px[y * w:(y + 1) * w]
        cum.append([a + b for a, b in zip(prev, row)])
    total = sum(cum[h])
    need = math.ceil(total * Fraction(str(share)))
    spare = total - need                # light that may be left out above and below together
    rows = [sum(r) for r in cum]        # light in the rows above y
    tops = [y for y in range(h) if rows[y] <= spare]
    bottoms = [y for y in range(1, h + 1) if total - rows[y] <= spare]

    def narrowest(sums):
        """The narrowest run of columns holding `need`, the most light for that width:
        (width, -light, x0), or None."""
        found, s, x0 = None, 0, 0
        for x1, v in enumerate(sums):
            s += v
            while s - sums[x0] >= need:
                s -= sums[x0]
                x0 += 1
            if s >= need:
                key = (x1 + 1 - x0, -s, x0)
                found = key if found is None or key < found else found
        return found

    floor_w = narrowest(cum[h])[0]      # no box is narrower than the narrowest over every row
    best = None                         # (area, -light, y0, x0, width, height)
    for y0 in reversed(tops):
        for y1 in bottoms:
            if y1 <= y0:
                continue
            if best is not None and (y1 - y0) * floor_w > best[0]:
                break                   # taller from here, never narrower than floor_w
            if rows[y1] - rows[y0] < need:
                continue
            got = narrowest([a - b for a, b in zip(cum[y1], cum[y0])])
            if got is None:
                continue
            key = ((y1 - y0) * got[0], got[1], y0, got[2], got[0], y1 - y0)
            if best is None or key < best:
                best = key
    _, _, y0, x0, bw, bh = best
    return (lx + x0, ly + y0, lx + x0 + bw, ly + y0 + bh)


def drop_specks(alpha):
    """alpha (0 or 255) with every 8-connected group of fewer than SPECK_PX opaque pixels cleared."""
    w, h = alpha.size
    px = list(alpha.get_flattened_data())
    seen = bytearray(w * h)
    for start, v in enumerate(px):
        if not v or seen[start]:
            continue
        seen[start] = 1
        group, todo = [start], [start]
        while todo:
            i = todo.pop()
            x, y = i % w, i // w
            for ny in range(max(y - 1, 0), min(y + 2, h)):
                for nx in range(max(x - 1, 0), min(x + 2, w)):
                    j = ny * w + nx
                    if px[j] and not seen[j]:
                        seen[j] = 1
                        group.append(j)
                        todo.append(j)
        if len(group) < SPECK_PX:
            for i in group:
                px[i] = 0
    out = Image.new("L", alpha.size)
    out.putdata(px)
    return out


def glow_frame(render, bloom=None):
    """An animated glow's frame as the sheet carries it: the light, drawn additively.

    The render is the light alone on transparent film (the sun and sky off; the parts it
    does not light render black), so the light is its colour times its alpha. bloom
    [[radius, gain], ...] adds, for each stage, the light blurred by a Gaussian of that
    radius (its standard deviation, px), times gain -- every stage blurred from the light
    itself, not from the stage before: the soft halo vanilla's glows carry. Opaque wherever
    any channel is above GLOW_FLOOR (the channel, as a blue light's luminance is a third of
    its blue), with specks of render noise dropped as glow_layer drops them.
    """
    r, g, b, a = render.convert("RGBA").split()
    light = Image.merge("RGB", [ImageChops.multiply(c, a) for c in (r, g, b)])
    halos = [light.filter(ImageFilter.GaussianBlur(radius)).point(lambda v, k=gain: min(255, round(v * k)))
             for radius, gain in bloom or ()]
    for halo in halos:
        light = ImageChops.add(light, halo)
    most = ImageChops.lighter(ImageChops.lighter(*light.split()[:2]), light.getchannel("B"))
    alpha = drop_specks(most.point(lambda v: 255 if v > GLOW_FLOOR else 0))
    return Image.merge("RGBA", (*ImageChops.multiply(light, Image.merge("RGB", (alpha,) * 3)).split(), alpha))


def add_light(under, glow):
    """under (RGBA) with a glow sheet's frame added, as the engine adds it: RGB only."""
    lit = ImageChops.add(under.convert("RGB"), glow.convert("RGB"))
    return Image.merge("RGBA", (*lit.split(), under.getchannel("A")))


def light_stats(glow, thresh=12):
    """Peak luminance, and the core (>= 60 % of the peak) and halo (<= 25 %) shares of the
    lit pixels (any channel over thresh): look_common.light_measures' numbers."""
    L = [0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]
         for p in glow.convert("RGB").get_flattened_data() if max(p) > thresh]
    if not L:
        return dict(peak=0, core=0.0, halo=0.0)
    pk = max(L)
    return dict(peak=round(pk), core=round(100 * sum(1 for v in L if v >= 0.6 * pk) / len(L), 1),
                halo=round(100 * sum(1 for v in L if v <= 0.25 * pk) / len(L), 1))


def edge_px(alpha):
    """Opaque pixels on the image's outermost row or column: where a layer meets the canvas's edge."""
    w, h = alpha.size
    return sum(alpha.crop(b).histogram()[255] for b in ((0, 0, w, 1), (0, h - 1, w, h), (0, 1, 1, h - 1),
                                                         (w - 1, 1, w, h - 1)))


def white(im):
    """Where every channel is 245 or over: 255, else 0."""
    r, g, b = im.convert("RGB").split()
    return ImageChops.darker(ImageChops.darker(r, g), b).point(lambda v: 255 if v >= 245 else 0)


def shoulder(m):
    """Where the roll-off takes a brightest channel m: m itself at or under KNEE; past it eased
    toward TOP, never reaching it (255 -> 243.3)."""
    return m if m <= KNEE else KNEE + (TOP - KNEE) * (1 - math.exp(-(m - KNEE) / (TOP - KNEE)))


def hue(rgb):
    """A colour's hue in degrees (HSV's, 0-360), or None for a grey."""
    r, g, b = rgb
    hi, lo = max(rgb), min(rgb)
    if hi == lo:
        return None
    c = hi - lo
    h = (g - b) / c if hi == r else (b - r) / c + 2 if hi == g else (r - g) / c + 4
    return (60 * h) % 360


def hue_miss(a, b):
    """Degrees between two colours' hues: 0 for two greys, 360 for a grey and a colour."""
    ha, hb = hue(a), hue(b)
    if ha is None or hb is None:
        return 0 if ha is None and hb is None else 360
    d = abs(ha - hb) % 360
    return min(d, 360 - d)


@functools.lru_cache(maxsize=1 << 16)
def rolled(rgb):
    """One pixel's colour (r, g, b) rolled off: as it is when its brightest channel m is at or under
    KNEE; past it, every channel times shoulder(m) / m, each rounded down or up -- of the eight
    ways, the one whose hue is nearest the colour's own, then nearest the exact scale, then the
    first. Rounding each to its nearest would turn a pale colour's hue by up to 30 degrees, as a
    level is much of its chroma; this keeps it within 0.49 everywhere (test/test_rolloff.py)."""
    m = max(rgb)
    if m <= KNEE:
        return rgb
    k = shoulder(m) / m
    exact = [c * k for c in rgb]
    ways = itertools.product(*(sorted({math.floor(v), math.ceil(v)}) for v in exact))
    return min(ways, key=lambda w: (hue_miss(rgb, w), sum((c - v) ** 2 for c, v in zip(w, exact)), w))


def roll(im):
    """An RGBA image with its highlights rolled off (rolled, on every pixel's colour; alpha as it
    was, every pixel whose channels are all at or under KNEE byte for byte), the pixels it changed
    and the most any channel moved."""
    im = im.convert("RGBA")
    red, green, blue, _ = im.split()
    over = ImageChops.lighter(ImageChops.lighter(red, green), blue).point(lambda v: 255 if v > KNEE else 0)
    if over.getbbox() is None:
        return im, 0, 0
    px = bytearray(im.tobytes())
    changed = most = 0
    for run in re.finditer(rb"\xff+", over.tobytes()):
        for i in range(4 * run.start(), 4 * run.end(), 4):
            was = tuple(px[i:i + 3])
            now = rolled(was)
            if now != was:
                px[i:i + 3] = bytes(now)
                changed += 1
                most = max(most, *(a - b for a, b in zip(was, now)))
    return Image.frombytes("RGBA", im.size, bytes(px)), changed, most


def paint_layer(painted, under):
    """A paint pass's sheet: the pass itself, wherever it differs from the plate under it.

    Drawn as ordinary paint, so it keeps the pass's own colour and alpha there --
    frost over a pipe, or past the plate's edge -- and is clear everywhere else.
    """
    diff = ImageChops.difference(painted, under).split()
    most = diff[0]
    for band in diff[1:]:
        most = ImageChops.lighter(most, band)
    keep = most.point(lambda v: 255 if v > LAYER_FLOOR else 0)
    return Image.merge("RGBA", (*painted.convert("RGB").split(), ImageChops.multiply(keep, painted.getchannel("A"))))


def light_layer(lamp):
    """What a light pass's sheet keeps, on the full canvas: its crop, the box of alpha
    above 8 with a 1 px rim (Packer.box_of), and nothing outside it."""
    bb = lamp.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    out = Image.new("RGBA", lamp.size)
    if bb:
        bb = (bb[0] - 1, bb[1] - 1, bb[2] + 1, bb[3] + 1)
        out.paste(lamp.crop(bb), bb[:2])
    return out


def cut_mask(decl, direction):
    """The footprint cut (render.json's `cut`) on the canvas in a direction: an L image, 255
    inside the edges cut at, 0 past them, and on a pixel an edge crosses the share of it
    inside. None when the model declares no cut.

    The edges are the footprint's as it stands in that direction, its centre the entity
    origin (the canvas's centre), px_per_tile to a tile: east and west its screen right and
    left, south its bottom edge on the ground.
    """
    faces = decl.get("cut") or ()
    if not faces:
        return None
    cw, ch = decl["canvas"]
    ppt = float(decl["rig"]["px_per_tile"])
    fw, fh = contract.footprint_in(decl, direction)
    left = cw / 2 - fw / 2 * ppt if "W" in faces else -math.inf
    right = cw / 2 + fw / 2 * ppt if "E" in faces else math.inf
    bottom = ch / 2 + fh / 2 * ppt if "S" in faces else math.inf

    def band(lo, hi, n):
        # each pixel's share of [i, i + 1) inside [lo, hi), as 0-255, laid out one row long
        im = Image.new("L", (n, 1))
        im.putdata([round(255 * max(0.0, min(i + 1, hi) - max(i, lo))) for i in range(n)])
        return im
    cols = band(left, right, cw).resize((cw, ch), Image.NEAREST)
    rows = band(-math.inf, bottom, ch).transpose(Image.Transpose.TRANSPOSE).resize((cw, ch), Image.NEAREST)
    return ImageChops.multiply(cols, rows)


def cut(im, mask):
    """im (RGBA) cut to mask (cut_mask): alpha times the share inside, and the pixels wholly
    outside cleared to (0, 0, 0, 0), colour and all, as a glow's colour is read without its
    alpha. Returns it and the pixels with any alpha the cut cleared or thinned."""
    a = im.getchannel("A")
    touched = ImageChops.multiply(a.point(lambda v: 255 if v else 0), mask.point(lambda v: 255 if v < 255 else 0))
    keep = mask.point(lambda v: 255 if v else 0)
    rgb = ImageChops.multiply(im.convert("RGB"), Image.merge("RGB", (keep,) * 3))
    return Image.merge("RGBA", (*rgb.split(), ImageChops.multiply(a, mask))), touched.histogram()[255]


def wreck_parts(im):
    """A remnants render's (cleaned) shadow and debris, as L masks of 0 and 255: the shadow part
    transparent and near black (SHADOW_RGB), the debris above DEBRIS_ALPHA and not near black."""
    r, g, b, a = im.split()
    lit = ImageChops.lighter(ImageChops.lighter(r, g), b).point(lambda v: 255 if v > SHADOW_RGB else 0)
    part = a.point(lambda v: 255 if 0 < v < 255 else 0)
    shadow = ImageChops.subtract(part, lit)
    debris = ImageChops.multiply(lit, a.point(lambda v: 255 if v > DEBRIS_ALPHA else 0))
    return shadow, debris


def reach(bb, decl, direction, canvas):
    """How far a box (x0, y0, x1, y1, px) reaches past each edge of the footprint as it stands in
    a direction, on a canvas whose centre is the entity origin: {N, E, S, W} in tiles, below 0
    short of the edge; None for no box."""
    if bb is None:
        return None
    ppt = float(decl["rig"]["px_per_tile"])
    fw, fh = contract.footprint_in(decl, direction)
    cx, cy = canvas[0] / 2, canvas[1] / 2
    return dict(N=round((cy - fh / 2 * ppt - bb[1]) / ppt, 2), E=round((bb[2] - cx - fw / 2 * ppt) / ppt, 2),
                S=round((bb[3] - cy - fh / 2 * ppt) / ppt, 2), W=round((cx - fw / 2 * ppt - bb[0]) / ppt, 2))


def centroid(im):
    a = im.getchannel("A")
    px = list(a.get_flattened_data())
    w = sum(px)
    return (sum(v * (i % a.width) for i, v in enumerate(px)) / w,
            sum(v * (i // a.width) for i, v in enumerate(px)) / w)


class Packer:
    def __init__(self, src, out, decl):
        self.src, self.out, self.decl = src, out, decl
        cw, ch = decl["canvas"]
        self.origin = (cw / 2, ch / 2)
        self.ppt = float(decl["rig"]["px_per_tile"])
        self.meta = {}
        self.over = []      # every animation past LIMIT_PX, as a line to exit with
        self.clipped = []   # every glow animation that clips, as a line to exit with
        self.masks = {d: cut_mask(decl, d) for d, _ in contract.DIRECTIONS[decl["directions"]]}
        self.cut_px = {}    # per direction, {render stem: px the footprint cut cleared or thinned}
        self.wrecked = []   # every remnants check that fails, as a line to exit with
        self.roll_on = decl.get("rolloff", True)    # render.json's opt-out (contract.py)
        self.rolls = {}     # per direction, {sheet: its pixels the roll-off changed, the most a channel moved}
        self.wrecks = {}    # per direction, the remnants pass's render, cleaned and rolled off: packed into one sheet

    def open(self, stem, d, cut_it=True, canvas=None):
        """A render of direction d, cut to the footprint (render.json's `cut`) unless cut_it is false.
        canvas: the size it must be, when not the model's (a remnants pass's own)."""
        im = Image.open(os.path.join(self.src, stem + ".png")).convert("RGBA")
        want = list(canvas or self.decl["canvas"])
        if list(im.size) != want:
            sys.exit(f"pack.py: {stem}.png is {im.size[0]}x{im.size[1]}, but render.json "
                     f"declares a {want[0]}x{want[1]} canvas")
        if cut_it and self.masks[d] is not None:
            im, n = cut(im, self.masks[d])
            if n:
                self.cut_px.setdefault(d, {})[stem] = n
        return im

    def box_of(self, alpha, what, thr=0):
        bb = alpha.point(lambda v: 255 if v > thr else 0).getbbox()
        if bb is None:
            sys.exit(f"pack.py: {what} is empty: nothing in it above alpha {thr}")
        x0, y0, x1, y1 = bb
        return (x0 - 1, y0 - 1, x1 + 1, y1 + 1)

    def shift(self, bb, origin=None):
        """A crop's shift in tiles: its centre from the entity origin, the canvas's centre (origin,
        when the crop is off a canvas of its own)."""
        ox, oy = origin or self.origin
        return (round(((bb[0] + bb[2]) / 2 - ox) / self.ppt, 5),
                round(((bb[1] + bb[3]) / 2 - oy) / self.ppt, 5))

    def rolloff(self, im, sheet, d):
        """im rolled off (roll) for the sheet it goes into in direction d, what it changed recorded
        for checks rolloff_px; im as it is when the model opts out."""
        if not self.roll_on:
            return im
        im, n, most = roll(im)
        self.rolls.setdefault(d, {})[sheet] = dict(px=n, most=most)
        return im

    def save(self, im, bb, sheet, **extra):
        im.crop(bb).save(os.path.join(self.out, sheet + ".png"))
        self.meta[sheet] = dict(size=(bb[2] - bb[0], bb[3] - bb[1]), shift=self.shift(bb), **extra)

    # ---------------------------------------------------------------- one direction

    def direction(self, d):
        decl = self.decl
        renders = {}
        for p in decl["passes"]:
            stem = contract.named(p["name"], d)
            # a shadow falls past the footprint, and so does a wreck's debris and shadow
            renders[p["name"]] = self.open(stem, d, cut_it=p["kind"] not in ("shadow", "remnants"),
                                           canvas=contract.canvas_of(decl, p))
        checks = {}
        plate = next(p for p in decl["passes"] if p["kind"] == "plate")
        idle = renders[plate["name"]]

        for p in decl["passes"]:
            if p["kind"] == "still":
                continue                    # a reference for the frame-0 check, not a sheet
            im, sheet = renders[p["name"]], contract.named(p["sheet"], d)
            what = contract.named(p["name"], d) + ".png"
            if p["kind"] == "plate":
                self.save(self.rolloff(im, sheet, d), self.box_of(im.getchannel("A"), what), sheet)
            elif p["kind"] == "shadow":
                a = clean(im).getchannel("A")
                blk = Image.merge("RGBA", (*Image.new("RGB", im.size, (0, 0, 0)).split(), a))
                self.save(blk, self.box_of(a, what), sheet)
            elif p["kind"] == "glow":
                under = renders[p["over"]]
                layer = glow_layer(im, under)
                self.save(self.rolloff(layer, sheet, d), self.box_of(layer.getchannel("A"), what + " minus its plate"),
                          sheet)
                # Light the glow drove to white: white in the lit pass and not already
                # white under it (a glint on bare steel is). Over-driven emission clips
                # there, and the glow layer, being lit minus unlit, comes out grey
                # instead of the light's colour.
                white = sum(1 for w, i in zip(im.convert("RGB").get_flattened_data(),
                                              under.convert("RGB").get_flattened_data())
                            if min(w) >= 245 and min(i) < 245)
                checks[f"{p['sheet']}_white_px"] = (
                    white, "pixels the working light clipped to white; 0 = the light keeps its colour")
            elif p["kind"] == "paint":
                layer = paint_layer(im, renders[p["over"]])
                self.save(self.rolloff(layer, sheet, d),
                          self.box_of(layer.getchannel("A"), what + " where it differs from its plate"), sheet)
            elif p["kind"] == "light":
                self.save(im, self.box_of(im.getchannel("A"), what, 8), sheet)
            elif p["kind"] == "remnants":
                checks.update(self.wreck(p, clean(im), d, what))

        frame0 = []
        packed = {}         # every animation's frames, as packed: a glow's checks read its plate layer's
        for a in decl["animations"]:
            name, n = a["name"], int(a["frames"])
            light = a.get("kind", "paint") == "light"
            glow = a.get("kind") == "glow"
            # a light animation keeps what a light pass keeps (alpha above 8); a glow is turned to
            # light; paint is cleaned of the catchers' haze below NOISE
            frames = [light_layer(self.open(contract.frame(name, f, d), d)) if light
                      else glow_frame(self.open(contract.frame(name, f, d), d), a.get("bloom")) if glow
                      else clean(self.open(contract.frame(name, f, d), d)) for f in range(n)]
            packed[name] = frames
            working = a.get("working", False)
            u = None
            for f, fr in enumerate(frames):
                if working and fr.getchannel("A").getbbox() is None:
                    continue                 # a working layer may draw nothing in a frame (dust between landings)
                b = self.box_of(fr.getchannel("A"), contract.frame(name, f, d) + ".png", 8 if light else 0)
                u = b if u is None else (min(u[0], b[0]), min(u[1], b[1]), max(u[2], b[2]), max(u[3], b[3]))
            if u is None:
                sys.exit(f"pack.py: every frame of {contract.named(name, d)} is empty")
            fw, fh = u[2] - u[0], u[3] - u[1]
            line = max(1, min(n, MAX_SHEET_W // fw))
            sheet = Image.new("RGBA", (fw * line, fh * math.ceil(n / line)))
            for i, fr in enumerate(frames):
                sheet.paste(fr.crop(u), ((i % line) * fw, (i // line) * fh))
            stem = contract.named(name, d)
            if not light:
                sheet = self.rolloff(sheet, stem, d)     # its frames, unrolled, are what the checks read
            sheet.save(os.path.join(self.out, stem + ".png"))
            self.meta[stem] = dict(size=(fw, fh), shift=self.shift(u), frames=n, line_length=line)
            if light or glow:
                self.meta[stem]["kind"] = a["kind"]
            elif not working:
                frame0.append(frames[0])     # light and working layers draw only while working: not the still's
            seq = contract.sequence(decl, a)
            if seq is not None:
                self.meta[stem]["frame_sequence"] = seq
                checks[f"{name}_sequence"] = (
                    dict(entries=len(seq), unused=[k for k in range(1, n + 1) if k not in seq]),
                    f"the frame_sequence it plays in (meta.json, 1-based): its entries, the actual length every "
                    f"layer drawn with it must have ({contract.SEQUENCE_MAX} at most), and the frames it never shows")
            speed = contract.speed(decl, a)
            if speed is not None:
                self.meta[stem]["animation_speed"] = speed
            if a["motion"] == "flow":
                continue                     # contents moving in place: nothing to hold to a centroid
            if a["motion"] == "cycle":
                # a closed loop of parts (a chain's flights): nothing to hold to a
                # point or a line; packed, and the loop is the model's to close
                checks[f"{name}_cycle"] = (n, "frames of a closed loop; no positional check")
                continue

            cs = [centroid(fr) for fr in frames]
            if a["motion"] == "turn":
                # A part turned about its own axis keeps its centroid (given the
                # symmetry its loop relies on); one turned about anywhere else
                # drifts frame to frame.
                drift = max(math.hypot(cx - cs[0][0], cy - cs[0][1]) for cx, cy in cs)
                checks[f"{name}_drift_px"] = (round(drift, 2), f"centroid travel across the {n} frames; "
                                              "~0 = turning in place, must stay within 1")
                if round(drift, 2) > LIMIT_PX:
                    self.over.append(f"animation {name!r}, {where(d)}: its centroid drifts {round(drift, 2)} px "
                                     f"across its frames; a part turning about its own axis stays within "
                                     f"{LIMIT_PX:g}")
            else:
                if a.get("track"):
                    # the layer carries parts that do not ride the path; the
                    # part that does was rendered alone for this
                    # never cut: measured for its centroid, never drawn, and a cut part's centroid moves
                    cs = [centroid(clean(self.open(contract.track_frame(name, a["track"], f, d), d, cut_it=False)))
                          for f in range(n)]
                path = checks[f"{name}_path_px"] = self.slide(a, cs, d)
                if a.get("track"):
                    path["tracked"] = a["track"]
                if path["frames_over"]:
                    # named as the render measured: the tracked part's own, for a tracked slide
                    stems = [contract.track_frame(name, a["track"], f, d) if a.get("track")
                             else contract.frame(name, f, d) for f in path["frames_over"]]
                    shown = ", ".join(f"{f} ({s}.png)" for f, s in zip(path["frames_over"], stems))
                    self.over.append(f"animation {name!r}, {where(d)}: frame(s) {shown} more than "
                                     f"{LIMIT_PX:g} px off, measured from frame 0 (the still): at most "
                                     f"{path['off_curve']} px off its declared curve and {path['off_line']} px "
                                     f"off its line (declared {path['declared']}, measured {path['measured']})")

        for a in decl["animations"]:
            if a.get("kind") == "glow":
                siblings = [b["name"] for b in decl["animations"]
                            if b.get("kind") == "glow" and b["over"] == a["over"] and b["name"] != a["name"]]
                checks.update(self.glow_checks(a, packed, idle, d, siblings))

        if frame0:
            # The spec's frame-0 rule: the plate with every animation's frame 0 over
            # it is the stopped machine. Held to a single render of it (the still),
            # not to the byte: two renders of different scenes sample differently,
            # and a caught shadow is not a real one.
            still = next(p for p in decl["passes"] if p["kind"] == "still")
            comp = idle.copy()
            for fr in frame0:
                comp.alpha_composite(fr)
            diff0 = [max(px) for px in ImageChops.difference(
                comp, renders[still["name"]]).get_flattened_data()]
            checks["frame0_vs_still"] = (max(diff0), round(sum(1 for v in diff0 if v > 8) / len(diff0), 4),
                                         "max channel difference, and share of pixels over 8 (sampling noise)")

        # Appendix C's four measurements, on the plate, against the footprint as it
        # stands in this direction
        fw_tiles, fh_tiles = contract.footprint_in(decl, d)
        ox, oy = self.origin
        vis = idle.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
        base = Image.open(os.path.join(self.out, contract.named(plate["sheet"], d) + ".png")).getchannel("A")
        W, H = base.size
        appendix = {
            "centre_offset_px": (vis[0] + vis[2]) / 2 - ox,
            "edge_alpha_max": max(max(base.getpixel((0, y)), base.getpixel((W - 1, y))) for y in range(H))
                              + max(max(base.getpixel((x, 0)), base.getpixel((x, H - 1))) for x in range(W)),
            "half_width_tiles": (max(abs(vis[0] - ox), abs(vis[2] - ox)) / self.ppt,
                                 f"{fw_tiles / 2} = footprint width / 2"),
            "footprint_rows_tiles": ((vis[3] - oy) / self.ppt,
                                     f"bottom edge below origin; {fh_tiles / 2} = on the footprint"),
        }
        appendix.update(checks)
        if decl.get("cut"):
            appendix["cut_px"] = (self.cut_px.get(d, {}), f"per render, the px with alpha the footprint cut "
                                  f"({', '.join(decl['cut'])}) cleared or thinned; the shadow is never cut")
        if self.roll_on:
            appendix["rolloff_px"] = (self.rolls.get(d, {}), f"per sheet but a shadow's or a light's, the px the "
                                      f"highlight roll-off changed (brightest channel over {KNEE}, eased under "
                                      f"{TOP}, hue kept) and the most a channel moved; render.json's rolloff false "
                                      f"opts out")
        return appendix

    def glow_checks(self, anim, packed, plate, d, siblings=()):
        """An animated glow held to its light: never white, never driving its plate to white,
        one frame for each of its plate layer's. siblings: the other glow animations over the
        same plate layer (a model's windows of different blooms, radiant.py): the engine draws
        them all, so the clipping is counted with all of them added."""
        name, over = anim["name"], anim["over"]
        glows, unders = packed[name], packed[over]
        bare = clipped = edge = 0
        for f, (g, u) in enumerate(zip(glows, unders)):
            # the light, bloom and all, must fade out inside the canvas: at its edge the tail is cut
            edge = max(edge, edge_px(g.getchannel("A")))
            under = plate.copy()
            under.alpha_composite(u)
            bare = max(bare, white(g).histogram()[255])
            lit = add_light(under, g)
            for sib in siblings:
                lit = add_light(lit, packed[sib][f % len(packed[sib])])
            # white once the light is added, and not white without it (a glint already is)
            clipped = max(clipped, ImageChops.subtract(white(lit), white(under)).histogram()[255])
        out = {
            f"{name}_white_px": (bare, "the most pixels of the light, in any frame, clipped to white; 0 = it "
                                 "keeps its colour"),
            f"{name}_clipped_px": (clipped, f"the most pixels, in any frame, the light drives to white added over "
                                   f"{over!r} on the plate" + (f", with {', '.join(siblings)} added too" if siblings
                                                               else "") + "; 0 = nothing clips"),
            f"{name}_frames": ([len(glows), len(unders)], f"its frames and its plate layer {over!r}'s: equal"),
            f"{name}_edge_px": (edge, f"the most pixels, in any frame, of the light (bloom and all, above "
                                f"GLOW_FLOOR {GLOW_FLOOR}) on the canvas's edge; 0 = the tail fades out inside it"),
            f"{name}_light": (light_stats(glows[0]), "frame 0: peak luminance, core % (>= 60 % of the peak), "
                              "halo % (<= 25 %); vanilla's glows: peak 87-171, core 2-8, halo 77-88"),
        }
        if bare or clipped or len(glows) != len(unders):
            self.clipped.append(f"glow animation {name!r}, {where(d)}: {bare} px of the light white, {clipped} px "
                                f"driven to white over {over!r}, {len(glows)} frames to its {len(unders)}; "
                                f"all must be 0, and the frames equal")
        if edge:
            self.clipped.append(f"glow animation {name!r}, {where(d)}: its light reaches the canvas's edge ({edge} px "
                                f"on it in one frame), so the edge cuts its bloom's tail: widen the canvas "
                                f"(radiant.py: about a tile round every window)")
        return out

    def slide(self, anim, cs, d):
        """A part moving in a straight line, held to the curve the model declared.

        The declared path, put on the screen for this direction, is where the part
        should be in each frame; its centroid is where it is. The centroid sits a
        fixed distance from whatever point the path follows, and that offset is
        taken from frame 0 -- the still, the part as the stopped machine shows it
        (the frame-0 rule) -- so frame 0 misses by nothing and every other frame's
        miss is measured from it: along the line, the frame is off the curve; across
        it, off the line. Either past LIMIT_PX fails, and the frames that are
        (frames_over, numbered as their renders are) are named. Until 2026-10-20 the
        offset was the mean over the frames, which shared one frame's miss among the
        rest: on a 4-frame slide one frame up to ~1.33 px off passed (Liam: "From
        frame 0").
        """
        # a root that never turns (turns: false) leaves the path as modelled in every direction
        facing = d if anim.get("turns", True) else contract.DIRECTIONS[self.decl["directions"]][0][0]
        want = [contract.screen(self.decl, p, facing) for p in anim["path"]]
        ox, oy = cs[0][0] - want[0][0], cs[0][1] - want[0][1]
        far = max(((w[0] - want[0][0], w[1] - want[0][1]) for w in want), key=lambda v: math.hypot(*v))
        ux, uy = far[0] / math.hypot(*far), far[1] / math.hypot(*far)
        got, along, across = [], [], []
        for c, w in zip(cs, want):
            rx, ry = c[0] - ox - w[0], c[1] - oy - w[1]
            got.append(round((c[0] - ox - want[0][0]) * ux + (c[1] - oy - want[0][1]) * uy, 2))
            along.append(round(rx * ux + ry * uy, 2))
            across.append(round(-rx * uy + ry * ux, 2))
        return dict(declared=[round((w[0] - want[0][0]) * ux + (w[1] - want[0][1]) * uy, 2) for w in want],
                    measured=got,
                    off_curve=max(abs(v) for v in along),
                    off_line=max(abs(v) for v in across),
                    frames_over=[f for f, (a, b) in enumerate(zip(along, across)) if max(abs(a), abs(b)) > LIMIT_PX],
                    note="each frame's position along the line, declared and measured (px from frame 0's "
                         "point: the still's); the most any frame is off the curve and off the line, measured "
                         "from frame 0: both must stay within 1; frames_over, the frames that do not")

    def wreck(self, p, im, d, what):
        """A remnants pass's render in direction d, cleaned: kept for its sheet (wreck_sheet), and
        its checks -- the shadow baked in, nothing on the canvas's edge, how far it reaches."""
        canvas = contract.canvas_of(self.decl, p)
        self.box_of(im.getchannel("A"), what)         # an empty wreck is refused, as an empty pass is
        self.wrecks[d] = self.rolloff(im, p["sheet"], d)    # as the sheet carries it; the checks read im
        shadow, debris = wreck_parts(im)
        n_shadow = shadow.histogram()[255]
        area = im.getchannel("A").point(lambda v: 255 if v else 0).histogram()[255]
        share = n_shadow / area
        edge = edge_px(im.getchannel("A").point(lambda v: 255 if v else 0))
        name = p["sheet"]
        if n_shadow < SHADOW_MIN_PX or share < SHADOW_SHARE:
            self.wrecked.append(f"remnants {p['name']!r}, {where(d)}: no shadow baked in ({n_shadow} part-"
                                f"transparent near-black px, {100 * share:.2f} % of the wreck; at least "
                                f"{SHADOW_MIN_PX} and {100 * SHADOW_SHARE:g} %): render the wreck over the ground "
                                f"catcher, as vanilla's remnants carry their shadow in the one sprite")
        if edge:
            self.wrecked.append(f"remnants {p['name']!r}, {where(d)}: {edge} px of it on its canvas's edge, so the "
                                f"canvas cuts the wreck or its shadow off: give the pass a larger canvas of its own")
        return {
            f"{name}_shadow_px": (dict(px=n_shadow, share=round(share, 4)),
                                  f"pixels of shadow baked into the wreck (part transparent, every channel at most "
                                  f"{SHADOW_RGB}) and their share of its area; under {SHADOW_MIN_PX} px or "
                                  f"{SHADOW_SHARE:g} fails (no catcher); vanilla's remnants 0.24-0.52"),
            f"{name}_edge_px": (edge, "pixels of the wreck or its shadow on its canvas's edge; 0 = the canvas "
                                "holds it"),
            f"{name}_reach_tiles": (
                dict(debris=reach(debris.getbbox(), self.decl, d, canvas),
                     all=reach(im.getchannel("A").getbbox(), self.decl, d, canvas)),
                "how far past each footprint edge, as it stands in this direction, the debris (alpha over "
                f"{DEBRIS_ALPHA}, not near black) and everything kept (the shadow too) reach, tiles; below 0 short "
                "of it. Vanilla's turbine: debris -0.45 to -0.03, all 0.11 to 0.64"),
        }

    def wreck_sheet(self, p):
        """The remnants sheet: every direction's wreck, one row each in vanilla's order
        (contract.remnant_rows), all cropped to the one box that holds them all."""
        rows = contract.remnant_rows(self.decl)
        cw, ch = contract.canvas_of(self.decl, p)
        boxes = [self.box_of(im.getchannel("A"), contract.named(p["name"], d) + ".png")
                 for d, im in self.wrecks.items()]
        u = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
        w, h = u[2] - u[0], u[3] - u[1]
        sheet = Image.new("RGBA", (w, h * len(rows)))
        for i, d in enumerate(rows):
            sheet.paste(self.wrecks[d].crop(u), (0, i * h))
        sheet.save(os.path.join(self.out, p["sheet"] + ".png"))
        self.meta[p["sheet"]] = dict(size=(w, h), shift=self.shift(u, (cw / 2, ch / 2)), direction_count=len(rows),
                                     line_length=1, rows=rows, kind="remnants", final_render_layer="remnants")

    def run(self):
        dirs = [d for d, _ in contract.DIRECTIONS[self.decl["directions"]]]
        per = {d: self.direction(d) for d in dirs}
        for p in self.decl["passes"]:
            if p["kind"] == "remnants":
                self.wreck_sheet(p)
        self.meta["checks"] = per[""] if dirs == [""] else per
        return self.meta


def where(d):
    return f"direction {d}" if d else "its one direction"


def missing(src, decl):
    """Every render the declaration promises that is not in src."""
    want = []
    for d, _ in contract.DIRECTIONS[decl["directions"]]:
        want += [(f"pass {p['name']!r}", contract.named(p["name"], d)) for p in decl["passes"]]
        want += [(f"animation {a['name']!r}", contract.frame(a["name"], f, d))
                 for a in decl["animations"] for f in range(int(a["frames"]))]
        want += [(f"animation {a['name']!r}, tracked part {a['track']!r}",
                  contract.track_frame(a["name"], a["track"], f, d))
                 for a in decl["animations"] if a.get("track") for f in range(int(a["frames"]))]
    return [(what, stem) for what, stem in want if not os.path.isfile(os.path.join(src, stem + ".png"))]


def main(src, out):
    try:
        decl = contract.load(src)
    except contract.ContractError as e:
        sys.exit(f"pack.py: {e}")
    if not decl["passes"]:
        sys.exit(f"pack.py: {src}/render.json declares no passes to pack")
    gone = missing(src, decl)
    if gone:
        sys.exit(f"pack.py: {src} is missing {len(gone)} declared render(s):\n" +
                 "\n".join(f"  {stem}.png  ({what})" for what, stem in gone))
    os.makedirs(out, exist_ok=True)
    packer = Packer(src, out, decl)
    meta = packer.run()
    with open(os.path.join(out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(json.dumps(meta, indent=1))
    failed = []                 # meta.json is written first, so the numbers can be read
    if packer.over:
        failed.append(f"pack.py: {len(packer.over)} animation check(s) over {LIMIT_PX:g} px "
                      f"(numbers in {out}/meta.json):\n" + "\n".join(f"  {o}" for o in packer.over))
    if packer.clipped:
        failed.append(f"pack.py: {len(packer.clipped)} glow animation check(s) failed "
                      f"(numbers in {out}/meta.json):\n" + "\n".join(f"  {o}" for o in packer.clipped))
    if packer.wrecked:
        failed.append(f"pack.py: {len(packer.wrecked)} remnants check(s) failed "
                      f"(numbers in {out}/meta.json):\n" + "\n".join(f"  {o}" for o in packer.wrecked))
    if failed:
        sys.exit("\n".join(failed))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: pack.py <render-dir> <out-dir>")
    main(sys.argv[1], sys.argv[2])
