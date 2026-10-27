#!/usr/bin/env python3
"""Vent Pump model (T07d): the embers (E2) before and after, their holdout check, and the 1x GIF with every effect.

  python3 -B review_t07d.py --run <render.sh out-dir> --check <vent_pump.py --ember-check out-dir>
        --before <T07c's sheets and effects: a dir with sheets/ and effects/> --effects <effects.py --out>
        --ends <vent_pump.py --ends out-dir> --out <concept/vent-pump/model> --scratch <dir>

Liam, 2026-10-21, on T07c's embers: "Enbers don't really look right and aren't the right perspective, they're
infront of parts of the model which are closed to the camera than the box"; "Just apply my picks" (only the
embers change). T07c drew them in PIL as a flat sprite placed over the whole machine; T07d renders them in the
model (vent_pump.py, E2), each frame with every other part held out, and packs them as the layers embers (the
cinders, unlit) and embers-light (their light, a glow).

Writes into --out (each page under 8000 px a side):
  review-t07d-embers.png   per direction: the bin before (T07c) and after (T07d) at the same ticks, 3x; the
                           holdout map (the parts nearer the camera than the bin's slag, and where each
                           version's ember pixels fall on them); the ember layer's 48 frames over the plate;
                           the figures (the ray check per direction, the before count, the layers' sizes)
  review-t07d-strips.png   the ember layer's 48 frames over the working machine, per direction, 2x
  review-t07d-runs.png     Liam's standing check (2026-10-21), by eye: per direction the machine working at 2x
                           with every run's two ends numbered (vent_pump.py --ends: each hose, pipe and cable,
                           and where its ends sit), a 3x crop of each end, and every effect at 2x at four ticks
  effects-1x.gif           the four directions working with every effect (A2 wisp, E2 embers, E4 cold breath
                           but facing south, E5 purge), 48 frames over the 2 s loop, 1x
and into --scratch: effects-2x.gif (north, 2x; not for git).

Composed from the packed sheets as measure.py composes them: each sheet at its shift, shadows at half
strength, glows added as light. Unchecked in a client.
"""
import argparse
import json
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import measure  # noqa: E402

ap = argparse.ArgumentParser()
for k in ("run", "check", "before", "effects", "ends", "out", "scratch"):
    ap.add_argument("--" + k, required=True)
A = ap.parse_args()
os.makedirs(A.scratch, exist_ok=True)
PPT = 64
GROUND = (74, 66, 58)
BG = (30, 28, 26)
TXT = (226, 220, 210)
HEAD = (240, 200, 120)
DIRS = ("north", "east", "south", "west")
NF, NFE = 24, 48
META = json.load(open(os.path.join(A.run, "sheets", "meta.json")))
DECL = json.load(open(os.path.join(A.run, "renders", "render.json")))
C = DECL["canvas"][0]
CHECK = json.load(open(os.path.join(A.check, "ember-check.json")))
FX = json.load(open(os.path.join(A.effects, "effects.json")))["effects"]
FX_OLD = json.load(open(os.path.join(A.before, "effects", "effects.json")))["effects"]
SHEETS = os.path.join(A.run, "sheets")
TOP = 128                   # headroom over the canvas: the wisp rises past its top


def font(n, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if bold else "") + ".ttf", n)


F1, FB = font(13), font(16, True)
_cache = {}


def sheet_im(path):
    if path not in _cache:
        _cache[path] = Image.open(path).convert("RGBA")
    return _cache[path]


def placed(stem, f=0):
    m = META[stem]
    w, h = m["size"]
    im = sheet_im(os.path.join(SHEETS, stem + ".png"))
    if "frames" in m:
        ll, f = m["line_length"], f % m["frames"]
        im = im.crop(((f % ll) * w, (f // ll) * h, (f % ll) * w + w, (f // ll) * h + h))
    out = Image.new("RGBA", (C, C + TOP))
    out.alpha_composite(im, (round(C / 2 + m["shift"][0] * PPT - w / 2), round(TOP + C / 2 + m["shift"][1] * PPT - h / 2)))
    return out


def machine(d, f):
    """T07c's machine (unchanged in T07d) working at frame f: shadow, plate, mech, riser, glass, their light, the green lens."""
    out = Image.new("RGBA", (C, C + TOP), GROUND + (255,))
    a = placed(f"shadow-{d}").getchannel("A").point(lambda v: v // 2)
    out.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", out.size).split(), a)))
    for st in ("base", "mech", "riser", "glass"):
        out.alpha_composite(placed(f"{st}-{d}", f))
    rgb = out.convert("RGB")
    for st in ("riser-light", "glass-light"):
        rgb = ImageChops.add(rgb, measure.light_of(placed(f"{st}-{d}", f)))
    return ImageChops.add(rgb, measure.light_of(placed(f"lens-working-glow-{d}")))


def new_embers(rgb, d, fe):
    out = rgb.convert("RGBA")
    out.alpha_composite(placed(f"embers-{d}", fe))
    return ImageChops.add(out.convert("RGB"), measure.light_of(placed(f"embers-light-{d}", fe)))


def fx_frame(fx, src, name, k):
    e = fx[name]
    im = sheet_im(os.path.join(src, e["file"]))
    w, h, ll = e["width"], e["height"], e["line_length"]
    k %= e["frame_count"]
    return im.crop(((k % ll) * w, (k // ll) * h, (k % ll) * w + w, (k // ll) * h + h))


def fx_layer(fx, src, name, d, k):
    e = fx[name]
    fr = fx_frame(fx, src, name, k)
    px, py = e[f"{d}_position"]
    sx, sy = e["shift"]
    lay = Image.new("RGBA", (C, C + TOP))
    lay.alpha_composite(fr, (round(C / 2 + (px + sx) * PPT - fr.width / 2), round(TOP + C / 2 + (py + sy) * PPT - fr.height / 2)))
    return lay


def fx_place(rgb, fx, src, name, d, k):
    lay = fx_layer(fx, src, name, d, k)
    if "additive" in fx[name]["blend"]:
        return ImageChops.add(rgb, measure.light_of(lay))
    out = rgb.convert("RGBA")
    out.alpha_composite(lay)
    return out.convert("RGB")


def old_embers(rgb, d, tick):
    k = math.floor(tick * FX_OLD["embers-e2"]["animation_speed"])
    return fx_place(rgb, FX_OLD, os.path.join(A.before, "effects"), "embers-e2", d, k)


def frame_at(tick):
    return math.floor(tick * 0.2) % NF, math.floor(tick * 0.4) % NFE


def with_fx(d, tick, embers="new"):
    f, fe = frame_at(tick)
    rgb = machine(d, f)
    src = A.effects
    rgb = fx_place(rgb, FX, src, "wisp-a2", d, math.floor(tick * FX["wisp-a2"]["animation_speed"]))
    if embers == "new":
        rgb = new_embers(rgb, d, fe)
    elif embers == "old":
        rgb = old_embers(rgb, d, tick)
    if d != "south":                                # Liam, 2026-10-21: "Leave E4 out facing south"
        rgb = fx_place(rgb, FX, src, "cold-breath-e4", d, f)
    return fx_place(rgb, FX, src, "purge-e5", d, f)


# ---------------------------------------------------------------- layout helpers
def up(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def captioned(im, lines, width=None, f=F1):
    width = max(width or 0, im.width)
    h = 6 + 17 * len(lines)
    out = Image.new("RGB", (width, im.height + h), BG)
    out.paste(im, (0, 0))
    dr = ImageDraw.Draw(out)
    for i, ln in enumerate(lines):
        dr.text((2, im.height + 4 + 17 * i), ln, fill=TXT, font=f)
    return out


def row(panels, gap=12):
    w = sum(p.width for p in panels) + gap * (len(panels) - 1)
    out = Image.new("RGB", (w, max(p.height for p in panels)), BG)
    x = 0
    for p in panels:
        out.paste(p, (x, 0))
        x += p.width + gap
    return out


def column(blocks, gap=22):
    w = max(b.width for b in blocks)
    out = Image.new("RGB", (w + 2 * gap, sum(b.height for b in blocks) + gap * (len(blocks) + 1)), BG)
    y = gap
    for b in blocks:
        out.paste(b, (gap, y))
        y += b.height + gap
    return out


def text_block(title, lines, width):
    out = Image.new("RGB", (width, 30 + 18 * len(lines)), BG)
    dr = ImageDraw.Draw(out)
    dr.text((0, 4), title, fill=HEAD, font=FB)
    for i, ln in enumerate(lines):
        dr.text((0, 30 + 18 * i), ln, fill=TXT, font=F1)
    return out


def rect_of(lay, thr=1):
    return lay.getchannel("A").point(lambda v: 255 if v >= thr else 0).getbbox()


def union(boxes):
    boxes = [b for b in boxes if b]
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))


def pad(b, p):
    return (max(0, b[0] - p), max(0, b[1] - p), min(C, b[2] + p), min(C + TOP, b[3] + p))


# ---------------------------------------------------------------- the holdout map: before and after on it
def near_mask(d):
    raw = open(os.path.join(A.check, f"near-{d}.pgm"), "rb").read()
    head = raw.split(b"\n", 1)
    w, h = (int(v) for v in head[0].split()[1:3])
    m = Image.frombytes("L", (w, h), head[1])
    out = Image.new("L", (C, C + TOP))
    out.paste(m, (0, TOP))
    return out


def count_on(mask, lay, thr=16):
    a = lay.getchannel("A").point(lambda v: 255 if v >= thr else 0)
    both = ImageChops.multiply(a, mask)
    return sum(1 for v in both.get_flattened_data() if v), a


TICKS = (3, 21, 38, 56)
W_PAGE = 0
blocks, figures = [], []
for d in DIRS:
    near = near_mask(d)
    # before: T07c's own 24-frame loop, each frame on the map; after: the 48 frames, paint or light
    old_px, old_union = 0, Image.new("L", near.size)
    for k in range(FX_OLD["embers-e2"]["frame_count"]):
        n, a = count_on(near, fx_layer(FX_OLD, os.path.join(A.before, "effects"), "embers-e2", d, k))
        old_px += n
        old_union = ImageChops.lighter(old_union, a)
    new_px, new_union = 0, Image.new("L", near.size)
    boxes = []
    for fe in range(NFE):
        for st in ("embers", "embers-light"):
            lay = placed(f"{st}-{d}", fe)
            n, a = count_on(near, lay)
            new_px += n
            new_union = ImageChops.lighter(new_union, a)
            boxes.append(rect_of(lay))
    boxes.append(rect_of(fx_layer(FX_OLD, os.path.join(A.before, "effects"), "embers-e2", d, 0)))
    for k in range(FX_OLD["embers-e2"]["frame_count"]):
        boxes.append(rect_of(fx_layer(FX_OLD, os.path.join(A.before, "effects"), "embers-e2", d, k)))
    box = pad(union(boxes), 14)
    # crops, before and after at the same ticks (the rest of the effects off: the bin alone is judged)
    bef = [up(with_fx(d, t, "old").crop(box), 3) for t in TICKS]
    aft = [up(with_fx(d, t, "new").crop(box), 3) for t in TICKS]
    # the map: the machine stopped, the near parts red; T07c's ember pixels cyan on them, yellow off them;
    # T07d's the same (the ray check below is the strict one)
    still = machine(d, 0)
    red = Image.new("RGB", still.size, (200, 40, 40))
    base = Image.composite(Image.blend(still, red, 0.55), still, near)

    def overlay(un):
        on = ImageChops.multiply(un, near)
        off = ImageChops.subtract(un, near)
        im = Image.composite(Image.new("RGB", base.size, (60, 230, 255)), base, on)
        return Image.composite(Image.new("RGB", base.size, (255, 230, 60)), im, off)
    maps = [up(overlay(old_union).crop(box), 3), up(overlay(new_union).crop(box), 3)]
    ck = CHECK["directions"][d]
    figures.append(f"{d}: after (ray check, {ck['frames']} frames, paint and light): {ck['px']} ember px tested, "
                   f"fail {ck['fail_px']} (alpha <= {ck['fail_alpha_max']}, each {max([x['px_from_seen'] for x in ck.get('fails', [])], default=0)} px "
                   f"from a seen spark: the 4x resample's edge), excess {ck['excess_px']}, rays behind a part {ck['behind_rays']} (held out); "
                   f"before (T07c, 24 frames): {old_px} ember px-frames on parts nearer than the slag; "
                   f"after on the same map: {new_px}")
    b1 = captioned(row(bef), [f"{d} BEFORE (T07c, PIL sprite over the machine): ticks {', '.join(map(str, TICKS))}, 3x"])
    b2 = captioned(row(aft), [f"{d} AFTER (T07d, rendered with the machine held out): the same ticks, 3x"])
    b3 = captioned(row(maps), [f"{d} map, left T07c, right T07d: red = parts", "nearer than the slag (0.1 tile);",
                               "ember px over a loop: cyan on red, yellow off"])
    blocks.append((d, b1, b2, b3, box))

# strips: the ember layer's 48 frames over the working machine, 2x, per direction, 12 frames a row
strips = []
for d, *_r, box in blocks:
    frs = [up(new_embers(machine(d, fe // 2), d, fe).crop(box), 2) for fe in range(NFE)]
    rows_ = [captioned(row(frs[k:k + 12], 2), [f"{d}: frames {k}-{k + 11}"]) for k in range(0, NFE, 12)]
    strips.append(column(rows_, 4))
meta_lines = []
for d in DIRS:
    m, ml = META[f"embers-{d}"], META[f"embers-light-{d}"]
    meta_lines.append(f"{d}: embers {m['size'][0]}x{m['size'][1]} shift {tuple(m['shift'])}; embers-light "
                      f"{ml['size'][0]}x{ml['size'][1]} shift {tuple(ml['shift'])}; {m['frames']} frames, line {m['line_length']}, "
                      f"speed {m.get('animation_speed')}")
pages = [text_block("T07d: E2 embers rendered in the model, every other part held out (Liam, 2026-10-21)", [
    "Before: T07c's PIL sprite, one picture for every direction, drawn over the whole machine. After: 16 sparks off the slag in the "
    "skimmings bin, real objects in vent_pump.py, rendered per direction",
    "with every part of the machine held out at the machine's frame (f // 2), so what stands nearer the camera hides them in the sheet "
    "itself; the other effects are T07c's, unchanged.",
    "Ray check (vent_pump.py --ember-check): every ember pixel cast back as 4x4 rays; it fails when drawn (alpha >= 16) with no ray "
    "seeing a spark first and one meeting a spark behind a part."] + figures + meta_lines, 2000)]
dir_cols = [column([b1, b2, b3], 8) for d, b1, b2, b3, box in blocks]
pages.append(column([row(dir_cols[:2], 30), row(dir_cols[2:], 30)], 10))
page = column(pages)
if page.height > 7900 or page.width > 7900:
    k = min(7900 / page.height, 7900 / page.width)
    page = page.resize((int(page.width * k), int(page.height * k)), Image.LANCZOS)
p = os.path.join(A.out, "review-t07d-embers.png")
page.save(p, optimize=True)
print(p, page.size)
strip_page = column([text_block("T07d: the ember layer, every frame (embers then embers-light added) over the working machine, 2x",
                                 ["Two ember frames to each machine frame (f // 2): the mech parts behind them move in step."], 1600)]
                    + [row(strips[:2], 30), row(strips[2:], 30)])
if strip_page.height > 7900 or strip_page.width > 7900:
    k = min(7900 / strip_page.height, 7900 / strip_page.width)
    strip_page = strip_page.resize((int(strip_page.width * k), int(strip_page.height * k)), Image.LANCZOS)
p = os.path.join(A.out, "review-t07d-strips.png")
strip_page.save(p, optimize=True)
print(p, strip_page.size)


# ---------------------------------------------------------------- Liam's standing check: every run's ends, every effect
ENDS = json.load(open(os.path.join(A.ends, "ends.json")))
F2 = font(11)
runs_pages = [text_block("Runs and effects by eye (Liam, 2026-10-21): every hose, pipe and cable's two ends; every effect, 2x", [
    "Left: the machine working (frame 0, every layer), 2x, each run's ends marked a/b with its number; crossings judged on it. Right: "
    "each end cropped 3x (36 px round it).",
    "Ends placed from the model (vent_pump.py --ends): where the run's first and last points stand, projected. The model's own end check "
    f"(within 0.04 tile of a part): {sum(r['ok'] for r in ENDS)} of {len(ENDS)} runs.",
    "Below each: the four directions with every effect (A2, E2, E4 but south, E5) at ticks 3, 21, 38, 56, 2x."], 2400)]
for d in DIRS:
    rr = [r for r in ENDS if r["direction"] == d]
    work = machine(d, 0)
    big = up(work, 2)
    dr = ImageDraw.Draw(big)
    crops = []
    for i, r in enumerate(rr, 1):
        for tag, e in zip("ab", r["ends"]):
            x = C / 2 + e["screen"][0] * PPT
            y = TOP + C / 2 + e["screen"][1] * PPT
            dr.ellipse((2 * x - 5, 2 * y - 5, 2 * x + 5, 2 * y + 5), outline=(80, 255, 120), width=2)
            dr.text((2 * x + 6, 2 * y - 7), f"{i}{tag}", fill=(80, 255, 120), font=F2)
            cr = work.crop((round(x) - 18, round(y) - 18, round(x) + 18, round(y) + 18))
            cr = up(cr, 3)
            ImageDraw.Draw(cr).rectangle((51, 51, 56, 56), outline=(80, 255, 120))
            crops.append(captioned(cr, [f"{i}{tag} {e['to']}"], f=F2))
    bx = ImageChops.difference(work, Image.new("RGB", work.size, GROUND)).getbbox()
    full = big.crop((2 * bx[0] - 30, 2 * bx[1] - 20, 2 * bx[2] + 60, 2 * bx[3] + 20))
    legend = [f"{i}. {r['name']} ({'ok' if r['ok'] else 'LOOSE'}: {' / '.join(str(e['to']) for e in r['ends'])})" for i, r in enumerate(rr, 1)]
    grid = []
    for k in range(0, len(crops), 8):
        grid.append(row(crops[k:k + 8], 4))
    right = column(grid, 6)
    leg = text_block(f"{d}: {len(rr)} runs", legend, 520)
    fxs = [with_fx(d, t) for t in TICKS]
    fb = pad(union([ImageChops.difference(im, Image.new("RGB", im.size, GROUND)).getbbox() for im in fxs]), 4)
    fx_row = row([up(im.crop(fb), 2) for im in fxs], 8)
    runs_pages.append(column([row([full, column([leg, right], 4)], 14),
                              captioned(fx_row, [f"{d}: every effect, ticks {', '.join(map(str, TICKS))}, 2x"])], 6))
page = column(runs_pages)
if page.height > 7900 or page.width > 7900:
    k = min(7900 / page.height, 7900 / page.width)
    page = page.resize((int(page.width * k), int(page.height * k)), Image.LANCZOS)
p = os.path.join(A.out, "review-t07d-runs.png")
page.save(p, optimize=True)
print(p, page.size)


# ---------------------------------------------------------------- the GIFs
def loop(d_list, k=1):
    ticks = [i * 2.5 for i in range(NFE)]          # an ember frame each: 2.5 ticks at speed 0.4
    frames = [[with_fx(d, t) for d in d_list] for t in ticks]
    box = union([im.getbbox() and ImageChops.difference(im, Image.new("RGB", im.size, GROUND)).getbbox()
                 for ims in frames for im in ims])
    box = pad(box, 6)
    return [row([up(im.crop(box), k) for im in ims], 8) for ims in frames]


DUR = [40, 40, 50] * 16                     # ms, 41.7 on average: 2.5 ticks at 60 a second
fr = loop(DIRS)
p = os.path.join(A.out, "effects-1x.gif")
fr[0].save(p, save_all=True, append_images=fr[1:], duration=DUR, loop=0, optimize=True)
print(p, fr[0].size, os.path.getsize(p))
fr2 = loop(("north", "south"), k=2)
p2 = os.path.join(A.scratch, "effects-2x.gif")
fr2[0].save(p2, save_all=True, append_images=fr2[1:], duration=DUR, loop=0)
print(p2, fr2[0].size)
