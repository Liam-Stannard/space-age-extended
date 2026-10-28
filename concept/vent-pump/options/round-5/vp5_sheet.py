#!/usr/bin/env python3
"""Vent Pump, round 5 (T05): the Gas Lift Tower's texture variants -- sheets, GIFs, close-ups, measures.

  python3 -B vp5_sheet.py --full <renders> --cmap <cmap-dir> --r4 <round-4 render dir of concept 8>
                          --r5raw <the base working frame 0, not rolled off>
                          --measure <measure.py outputs, one folder per variant> --out <dir>

<renders>/<v>/ for v in base, a, b, c: vpb5_08_gas_lift_tower.py's output, after vp5_shoulder.py.
Writes into <out>:
  08-gas-lift-tower-variants.png   the sheet: the variants labelled, at 1x and 2x, beside vanilla's
                                   pumpjack, chemical plant and foundry at the same zoom; the
                                   figures per variant beside vanilla's and the Reaction Plant
                                   model's; the 4x close-ups (glass, melt, a painted unit);
                                   before/after round 4; the glow-only check; the paint per unit
  08-gas-lift-tower-<v>.png        each variant's still (working frame 0, 2x, the ports joined)
  08-gas-lift-tower-<v>-1x.gif     each variant working at 1x (24 frames, 70 ms)
  08-gas-lift-tower-<v>-2x.gif     the same at 2x (keep out of git)
  08-gas-lift-tower-<v>-closeups.png  the three 4x close-ups (the helium glass, the melt, a painted unit)
  measures.json                    the figures

measure.py (tools/blender/measure.py in the factorio-tools-skills worktree, committed there, reviewed
PASS) is imported read-only for vanilla's references and figures; its own per-variant runs
(coverage, rise, tonal, finish, motion, strobe, the pipe joins) are read from <measure>/<v>/.
"""
import argparse
import colorsys
import glob
import json
import os
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "round-4"))
import vp4_measure as GM  # noqa: E402
sys.path.insert(0, HERE)
from vp5_roll import roll  # noqa: E402  (the roll-off again after each downsample)
MTOOLS = "/home/liam-stannard/git/space-age-extended/.claude/worktrees/factorio-tools-skills/tools/blender"
sys.path.insert(0, MTOOLS)
import measure as MT  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--full", required=True)
ap.add_argument("--cmap", required=True)
ap.add_argument("--r4", required=True)
ap.add_argument("--r5raw", required=True, help="the base's working frame 0 before the roll-off (--only working --frames 1)")
ap.add_argument("--measure", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
V = ["base", "a", "b", "c"]
NAME = {"base": "base: round 4's surfacing, the clipping fixes only",
        "a": "(a) warmer paints", "b": "(b) heavier wear and rust where it forms", "c": "(c) cleaner, newer"}
CANVAS, ORIGIN = (352, 352), (160, 208)
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT = (228, 222, 210)
SUB = (175, 168, 156)
HEAD = (240, 200, 120)
GIF_MS = 70
RP = ("the Reaction Plant model (circulator.py, its measures.txt): the still p5 5, p50 75, p95 166; finish black "
      "8.6 %, fine 7.14, mid 10.77, ratio 0.66, darkchr 14.6 (its plate: p50 73, p95 164; black 10.6 %, ratio 0.65)")


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def load(path, k):
    """A 4x render at k x (premultiplied LANCZOS, as downsample.py; the catcher's faint fog cut, as round 3;
    the highlight roll-off applied again at 2x and 1x, vp5_roll.py)."""
    im = Image.open(path).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    if k == 4:
        return im
    return roll(im.convert("RGBa").resize((CANVAS[0] * k, CANVAS[1] * k), Image.LANCZOS).convert("RGBA"))


def ground(size, origin, ppt):
    g = Image.new("RGBA", size, GROUND)
    ov = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(-30, 31):
        d.line([(origin[0] + (i + 0.5) * ppt, 0), (origin[0] + (i + 0.5) * ppt, size[1])], fill=(255, 255, 255, 22))
        d.line([(0, origin[1] + (i + 0.5) * ppt), (size[0], origin[1] + (i + 0.5) * ppt)], fill=(255, 255, 255, 22))
    d.rectangle([origin[0] - 1.5 * ppt, origin[1] - 1.5 * ppt, origin[0] + 1.5 * ppt, origin[1] + 1.5 * ppt],
                outline=(255, 255, 255, 90))
    g.alpha_composite(ov)
    return g


PIPE = Image.open(f"{args.factorio}/base/graphics/entity/pipe/pipe-straight-vertical.png").convert("RGBA")


def with_ports(render, k):
    """On the ground, a vanilla straight pipe on the tile outside each port (ports.txt, as round 3)."""
    o = (ORIGIN[0] * k, ORIGIN[1] * k)
    c = ground(render.size, o, 64 * k)
    p = PIPE.resize((64 * k, 64 * k), Image.LANCZOS)
    for ty in (-2, 2):
        c.alpha_composite(p, (round(o[0] - p.width / 2), round(o[1] + ty * 64 * k - p.height / 2)))
    c.alpha_composite(render)
    return c


def on_ground(im):
    g = Image.new("RGBA", im.size, GROUND)
    g.alpha_composite(im)
    return g


VIEW1 = (16, 24, 320, 352)


def view(im, k):
    return im.crop(tuple(v * k for v in VIEW1))


def gif(frames, path):
    strip = Image.new("RGB", (frames[0].width, frames[0].height * len(frames)))
    for i, f in enumerate(frames):
        strip.paste(f.convert("RGB"), (0, i * f.height))
    pal = strip.quantize(colors=256, method=Image.Quantize.LIBIMAGEQUANT)
    q = [f.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=GIF_MS, loop=0, optimize=True)
    return round(os.path.getsize(path) / 1e6, 2)


def wc(im):
    """White (alpha >= 8, every channel >= 250) and clipped (alpha >= 8, any channel 255) px."""
    w = c = 0
    for r, g, b, a in im.get_flattened_data():
        if a < 8:
            continue
        if r >= 250 and g >= 250 and b >= 250:
            w += 1
        if r == 255 or g == 255 or b == 255:
            c += 1
    return w, c


def tool(name, path):
    r = subprocess.run([sys.executable, "-B", os.path.join(REPO, "tools", "blender", name), path], capture_output=True,
                       text=True)
    return " ".join(r.stdout.split()[1:]).split("(vanilla")[0].strip()


# ---------------------------------------------------------------- per variant
MEAS, VIEWS = {}, {}
for v in V:
    d = os.path.join(args.full, v)
    meta = json.load(open(os.path.join(d, "meta.json")))
    nf = meta["frames"]
    m = dict(name=NAME[v], palette=meta.get("palette"), worn=meta.get("worn"), layer=meta.get("layer"))
    frames = sorted(glob.glob(os.path.join(d, "*.png")))
    frames = [p for p in frames if not os.path.basename(p).startswith("hemask")]
    tot = {1: [0, 0], 2: [0, 0], 4: [0, 0]}
    per = {}
    for p in frames:
        for k in (1, 2, 4):
            w, c = wc(load(p, k))
            tot[k][0] += w
            tot[k][1] += c
            if w or c:
                per.setdefault(os.path.basename(p), {})[f"{k}x"] = [w, c]
    m["whole_frame"] = {f"{k}x": dict(white=tot[k][0], clipped=tot[k][1]) for k in (1, 2, 4)}
    m["whole_frame_frames"] = len(frames)
    m["whole_frame_where"] = per
    rw = os.path.join(d, "raw_wc.json")
    m["whole_frame_raw"] = json.load(open(rw))["total"] if os.path.exists(rw) else None
    m["glass"] = GM.measure(d, CANVAS, nf)
    peaks = []
    for p in sorted(glob.glob(os.path.join(d, "heglow-*.png"))):
        peaks.append(MT.light_measures(MT.light_of(load(p, 1)))["peak"])
    m["he_peak_measure_py"] = dict(max=max(peaks), min=min(peaks), frames=len(peaks))
    plate1 = load(os.path.join(d, "plate.png"), 1)
    pp = os.path.join(args.out, f"_plate-{v}.png")
    plate1.save(pp)
    m["tonal_plate"] = tool("tonal.py", pp)
    m["finish_plate"] = tool("finish.py", pp)
    os.remove(pp)
    m["pipes"] = len(meta.get("pipes", []))
    m["pipes_loose"] = sum(1 for P in meta.get("pipes", []) if not P["ok"])
    mj = os.path.join(args.measure, v, "measures.json")
    if os.path.exists(mj):
        mm = json.load(open(mj))
        dd = mm["directions"][next(iter(mm["directions"]))]
        m["measure_py"] = dict(coverage=dd["coverage"], tonal=dd["tonal"], finish=dd["finish"], motion=dd["motion"],
                               joins=dd["joins"], gates=mm["gates"], passed=mm["pass"])
    w1 = [view(with_ports(load(os.path.join(d, f"working-{f:02d}.png"), 1), 1), 1) for f in range(nf)]
    w2 = [view(with_ports(load(os.path.join(d, f"working-{f:02d}.png"), 2), 2), 2) for f in range(nf)]
    m["gif_1x_mb"] = gif(w1, os.path.join(args.out, f"08-gas-lift-tower-{v}-1x.gif"))
    m["gif_2x_mb"] = gif(w2, os.path.join(args.out, f"08-gas-lift-tower-{v}-2x.gif"))
    w2[0].convert("RGB").save(os.path.join(args.out, f"08-gas-lift-tower-{v}.png"))
    idle2 = view(with_ports(load(os.path.join(d, "idle.png"), 2), 2), 2)
    wf = [load(os.path.join(d, f"working-{f:02d}.png"), 1) for f in range(nf)]
    cov = MT.covered(wf[0].getchannel("A"))
    rgb = [MT.on_ground(f) for f in wf]
    mv = ImageChops.multiply(MT.moving(rgb), cov)
    sb = ImageChops.multiply(MT.strobe(rgb), cov)
    mm = Image.blend(rgb[0], Image.new("RGB", rgb[0].size, GROUND[:3]), 0.55).convert("RGBA")
    mm.paste((255, 0, 255, 255), (0, 0), mv)
    mm.paste((0, 255, 255, 255), (0, 0), sb)
    n_cov = max(1, MT.count(cov))
    m["motion_map"] = dict(moving_pct=round(100 * MT.count(mv) / n_cov, 2), strobe_px=MT.count(sb),
                           strobe_pct=round(100 * MT.count(sb) / n_cov, 2))
    VIEWS[v] = dict(w1=w1, w2=w2, idle2=idle2, meta=meta, d=d, motion=view(mm, 1))
    MEAS[v] = m
    print(v, json.dumps({k: m[k] for k in ("whole_frame", "tonal_plate", "finish_plate", "pipes_loose")}))

# ---------------------------------------------------------------- vanilla, at the same zoom
VAN = {}
for name in ("pumpjack", "chemical-plant", "foundry"):
    label, foot, still, shadow, light = MT.vanilla(name, "")
    fig = MT.vanilla_figures(still, light, foot)
    S = still.width
    g = Image.new("RGBA", (S, S), GROUND)
    g.alpha_composite(shadow)
    g.alpha_composite(still)
    VAN[name] = dict(label=label, im=g, fig=fig)

# ---------------------------------------------------------------- the glow-only check (criterion 9)
cm = Image.open(os.path.join(args.cmap, "colourmap.png")).convert("RGB")
groups = json.load(open(os.path.join(args.cmap, "colourmap.json")))
inv = {tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)): g for g, h in groups.items()}
ALLOWED = {g for g in groups if g.startswith(("molten", "helium (the liquid", "glass"))}


def grp(c):
    best = min(inv, key=lambda k: sum(abs(k[i] - c[i]) for i in range(3)))
    return inv[best] if sum(abs(best[i] - c[i]) for i in range(3)) < 40 else None


def glow_check(d):
    """Every glow on alone (glowall-NN.png: the sun, sky and ground off), at 2x on black: px with
    luminance >= 24, sorted by the colour map's group under them (the colour map is idle and still,
    2x). Allowed: the melt, the helium liquid, glass (the riser's and the sight glass's windows)."""
    lit_in, lit_out, where = 0, 0, {}
    cmp_ = cm.load()
    acc = None
    for p in sorted(glob.glob(os.path.join(d, "glowall-*.png"))):
        im = load(p, 2)
        blk = Image.new("RGBA", im.size, (0, 0, 0, 255))
        blk.alpha_composite(im)
        L = blk.convert("L")
        acc = L if acc is None else ImageChops.lighter(acc, L)
    a = acc.load()
    for y in range(acc.height):
        for x in range(acc.width):
            if a[x, y] >= 24:
                g = grp(cmp_[x, y])
                if g in ALLOWED:
                    lit_in += 1
                else:
                    lit_out += 1
                    where[g or "unmapped"] = where.get(g or "unmapped", 0) + 1
    return dict(lit_allowed=lit_in, lit_elsewhere=lit_out, elsewhere_by_group=where), acc


GLOW, GLOWIM = {}, {}
for v in V:
    GLOW[v], GLOWIM[v] = glow_check(VIEWS[v]["d"])
    MEAS[v]["glow_only"] = GLOW[v]

# ---------------------------------------------------------------- the sheet
PAD = 16


def wrap(s, size, width):
    f = font(size)
    out, line = [], ""
    for w in s.split():
        t = (line + " " + w).strip()
        if f.getlength(t) > width and line:
            out.append(line)
            line = w
        else:
            line = t
    if line:
        out.append(line)
    return out


def cap(im, s, size=12, width=None):
    width = max(im.width, width or 0)
    lines = []
    for i, c in enumerate(s.split("\n")):
        lines += [(ln, i == 0) for ln in wrap(c, size, width)]
    h = len(lines) * (size + 5) + 4
    o = Image.new("RGBA", (width, im.height + h), BG)
    d = ImageDraw.Draw(o)
    for i, (ln, b) in enumerate(lines):
        d.text((0, i * (size + 5)), ln, font=font(size, b), fill=TEXT if b else SUB)
    o.alpha_composite(im, (0, h))
    return o


def hrow(ims, gap=14):
    o = Image.new("RGBA", (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), BG)
    x = 0
    for i in ims:
        o.alpha_composite(i, (x, 0))
        x += i.width + gap
    return o


def block(title, paras, width, size=13):
    lines = [(title, HEAD, True, size + 3)] if title else []
    for p in paras:
        for s in wrap(p, size, width):
            lines.append((s, SUB, False, size))
        lines.append(("", SUB, False, 3))
    o = Image.new("RGBA", (width, sum(l[3] + 5 for l in lines) + 4), BG)
    d = ImageDraw.Draw(o)
    y = 0
    for s, c, b, sz in lines:
        d.text((0, y), s, font=font(sz, b), fill=c)
        y += sz + 5
    return o


def up(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def mark_clip(im):
    """The px a channel of which is 255, in magenta."""
    o = im.copy()
    p = o.load()
    for y in range(o.height):
        for x in range(o.width):
            r, g, b, a = p[x, y]
            if a and max(r, g, b) == 255:
                p[x, y] = (255, 0, 255, 255)
    return o


def figs(v):
    m = MEAS[v]
    g = m["glass"]
    mp = m.get("measure_py", {})
    cov = mp.get("coverage", {})
    mo = mp.get("motion") or {}
    j = mp.get("joins", [])
    jt = "; ".join(f"{x['connection']}: gap {'none' if x['pass'] else 'FAIL'}" for x in j) if j else "not run"
    raw = m.get("whole_frame_raw") or {}
    rt = "; ".join(f"{k} {raw[k][0]} / {raw[k][1]}" for k in ("4x", "2x", "1x") if k in raw) or "not recorded"
    tp = (mp.get("tonal") or {}).get("plate") or {}
    ts = (mp.get("tonal") or {}).get("still") or {}
    fp = (mp.get("finish") or {}).get("still") or {}
    return [f"Whole frame, white / clipped px over {m['whole_frame_frames']} frames (idle, plate, 24 working, three "
            f"turns, 24 helium-glow, 8 glow-only). The model alone (before the roll-off): {rt}. After the "
            f"roll-off: 4x {m['whole_frame']['4x']['white']} / "
            f"{m['whole_frame']['4x']['clipped']}; 2x {m['whole_frame']['2x']['white']} / "
            f"{m['whole_frame']['2x']['clipped']}; 1x {m['whole_frame']['1x']['white']} / "
            f"{m['whole_frame']['1x']['clipped']}.",
            f"Helium glow peak {g['he_peak_1x']} (1x, T03's measure; measure.py's light_measures over the "
            f"{m['he_peak_measure_py']['frames']} helium-glow frames: {m['he_peak_measure_py']['min']}-"
            f"{m['he_peak_measure_py']['max']}), hue {g['he_hue_deg']}; pale cyan {g['pale_cyan_px']}, frost "
            f"{g['frost_px']}. Glow-only: lit px where the melt, the helium or a window is "
            f"{m['glow_only']['lit_allowed']}, elsewhere {m['glow_only']['lit_elsewhere']} "
            f"{m['glow_only']['elsewhere_by_group'] or ''}.",
            f"Coverage (measure.py, the still) {cov.get('footprint_pct')} %, rise {cov.get('rise_tiles')} tile. "
            f"Tonal (measure.py) the plate p5 {tp.get('p5')} p50 {tp.get('p50')} p95 {tp.get('p95')}, the still p5 "
            f"{ts.get('p5')} p50 {ts.get('p50')} p95 {ts.get('p95')}; finish (the still) black {fp.get('black_pct')} %, "
            f"fine {fp.get('fine')}, mid {fp.get('mid')}, ratio {fp.get('ratio')}, darkchr {fp.get('darkchr')}. "
            f"tonal.py on the plate: {m['tonal_plate']}; finish.py: {m['finish_plate']}.",
            f"Motion (measure.py): moving {mo.get('moving_pct')} %, strobe {mo.get('strobe_pct')} %. Pipe joins "
            f"(measure.py): {jt}. Pipe ends (vpb3_kit.check_ends): {m['pipes']} runs, {m['pipes_loose']} loose. "
            f"GIF 1x {m['gif_1x_mb']} MB, 2x {m['gif_2x_mb']} MB."]


rows = []
W = 1900
rows.append(block("VENT PUMP, ROUND 5 (T05) -- THE GAS LIFT TOWER IN THREE TEXTURE VARIANTS", [
    "Liam's pick (T04, 2026-10-15: 'Gas lift tower - now we can review the textures'; 'Two or three texture "
    "variants'). One model, one geometry, four surfacings: the base (round 4's surfacing with the clipping fixes "
    "only, for reference) and (a) warmer paints, (b) heavier wear and rust where it forms, (c) cleaner and newer. "
    "The helium sight glass in mix A in all four. 64 px a tile, one ground; vanilla's pumpjack, chemical plant and "
    "foundry drawn the same way (measure.py's references: sprite and shadow, frame 0).",
    "The clipping fixes (Liam: 'Fix both in the model'), in all four: the melt's crest #FF9E52 -> #F89A50 and its "
    "glow x0.72 (its crest renders R 245 alone at the charge's peak); bare steel, seams and nickel satin (roughness "
    ">= 0.62, metal <= 0.35); every worn edge satin too (roughness >= 0.6 on every surface but the melt and the "
    "helium liquid: the wear-through was polished to 0.18 and glinted on every unit); and the brightest paints a step "
    "down (yellow, red, hazard, lagging, bare, nickel, seam, two cable colours, the gauge faces, the helium bands "
    "#84769A) and the windows' gloss 0.1 -> 0.04. What still clips after these is mostly diffuse, the sunlit tops of "
    "the brightest paints under the kit's sun of 13.5: specular x0.5 and roughness 0.7 still left 34 px at 1x and "
    "took p50 to 69. A highlight roll-off on each render (vp5_shoulder.py: a px whose brightest channel passes 236 "
    "is scaled, hue kept, so it stays under 250) takes the rest; both counts are given below. For scale, vanilla's "
    "own sprites (measure.py's references) carry clipped px: pumpjack 6, foundry 137, assembler 3 191, chemical "
    "plant 464 (refinery 0).",
    "One lighting correction, the same in all four: the shadow catcher no longer bounces light onto the machine "
    "(it is a plane with no material, albedo 0.8, and it lit every frame drawn over it, idle, working and the turns, "
    "to p50 90-92 while the plate, rendered without it, read 76), and the sky lifted 0.32 -> 0.44 so the frames as "
    "seen read p50 ~75 as the plate does. Round 4's frames carry that bounce, so round 4 reads lighter in the "
    "before/after crops (section 6) than any round-5 variant.",
    "The one geometry change: the flow meter's dial smaller (r 0.15 -> 0.12) and tilted a little west, so the "
    "helium glass east of it reads.",
], W))
# 1. the variants labelled, beside vanilla
pan = [cap(VIEWS[v]["w1"][0], f"{NAME[v]}\nworking f0, 1x") for v in V]
for nm, vv in VAN.items():
    im = vv["im"]
    S = im.width
    c = 176
    pan.append(cap(im.crop((S // 2 - 152, S // 2 - 200, S // 2 + 152, S // 2 + 128)) if S >= 352 else im,
                   f"vanilla {vv['label']}\n1x, same zoom"))
rows.append(block("1. THE THREE VARIANTS (AND THE BASE) BESIDE VANILLA, 1x, 64 px A TILE", [], W))
rows.append(hrow(pan, 12))
rows.append(hrow([cap(VIEWS[v]["w2"][0], f"{NAME[v]}, working f0, 2x") for v in V], 12))
# figures
fig_lines = []
for v in V:
    fig_lines.append(block(NAME[v].upper(), figs(v), W, size=12))
van = []
for nm, vv in VAN.items():
    f = vv["fig"]
    van.append(f"{vv['label']}: coverage {f['coverage'].get('footprint_pct')} %, rise {f['coverage'].get('rise_tiles')} "
               f"tile; tonal p5 {f['tonal']['p5']}, p50 {f['tonal']['p50']}, p95 {f['tonal']['p95']}; finish black "
               f"{f['finish']['black_pct']} %, fine {f['finish']['fine']}, mid {f['finish']['mid']}, ratio "
               f"{f['finish']['ratio']}, darkchr {f['finish']['darkchr']}")
rows.append(block("THE FIGURES (1x)", ["Vanilla, measured by measure.py the same way: " + "; ".join(van) + ".", RP + ".",
                                        "The mod's look: p50 ~75-81; p95 into vanilla's 143-189."], W, size=12))
rows += fig_lines
# close-ups at 4x
rows.append(block("3. CLOSE-UPS AT 4x (WORKING FRAME 0): THE HELIUM GLASS, THE MELT (THE GLASS RISER), A PAINTED UNIT "
                  "(THE OXIDE RECOVERY COMPRESSOR)", [], W))
lab = {L["n"]: L["px"] for L in VIEWS["base"]["meta"]["labels"]}
gb = MEAS["base"]["glass"]["glass_box_1x"]
gc = ((gb[0] + gb[2]) / 2 * 4, (gb[1] + gb[3]) / 2 * 4)
boxes = {"glass": gc, "melt": (lab[4][0] * 4, lab[4][1] * 4 - 60), "paint": (lab[8][0] * 4, lab[8][1] * 4 + 60)}
for v in V:
    w4 = on_ground(load(os.path.join(VIEWS[v]["d"], "working-00.png"), 4))
    cr = []
    for k, (cx, cy) in boxes.items():
        cr.append(cap(w4.crop((round(cx - 150), round(cy - 150), round(cx + 150), round(cy + 150))), f"{k}, 4x"))
    row = cap(hrow(cr, 10), NAME[v], 13)
    rows.append(row)
    row.convert("RGB").save(os.path.join(args.out, f"08-gas-lift-tower-{v}-closeups.png"))
rows.append(block("11. MOTION MAP PER VARIANT (1x, 24 frames; magenta moving, cyan strobing: measure.py's moving() and "
                  "strobe())", ["Moving parts and their jobs: the bubbles in the glass riser (the gas lift itself), the "
                  "melt's flow bands in the riser and the head tank's window, the helium sight glass (level drops and "
                  "flushes pink at each charge), the flow meter's rotor and the line gauge (each charge), the float "
                  "chamber's lever (rocks with each charge), the compressor's coupling (recovery), the receiver's "
                  "gauge. Idle: all still, nothing lit (the idle frame)."], W))
rows.append(hrow([cap(VIEWS[v]["motion"], f"{v}: moving {MEAS[v]['motion_map']['moving_pct']} %, strobing "
                                          f"{MEAS[v]['motion_map']['strobe_px']} px") for v in V], 12))
# before / after round 4
rows.append(block("6. WHAT CHANGED FROM ROUND 4 (round 4, its clipped px; round 5's base, its clipped px before the "
                  "roll-off; 4x crops; magenta = a channel at 255)", [
    "The melt's crest (the glass riser, frame 0), satin steel and the paints a step down (the head tank's nickel "
    "bands and the yellow rails), and the dial (the flow meter and the helium glass). Round 4's crops are a step "
    "lighter overall: its frames carry the shadow catcher's bounce (see the top). Counts are on the raw 4x crop "
    "before round 5's roll-off for round 5 too, so they show what the model fixes alone did.",
], W))
r4w = on_ground(load(os.path.join(args.r4, "working-00.png"), 4))
r5w = on_ground(load(os.path.join(VIEWS["base"]["d"], "working-00.png"), 4))
lab4 = {L["n"]: L["px"] for L in json.load(open(os.path.join(args.r4, "meta.json")))["labels"]}
ba = {"the melt's crest": (lab[4][0] * 4, lab[4][1] * 4 - 60),
      "satin steel, the paints a step down": (lab[5][0] * 4, lab[5][1] * 4),
      "the dial and the glass": (lab[2][0] * 4 + 60, lab[2][1] * 4)}
bar = []
for k, (cx, cy) in ba.items():
    bx = (round(cx - 140), round(cy - 140), round(cx + 140), round(cy + 140))
    a_, b_ = r4w.crop(bx), r5w.crop(bx)
    wa, ca = wc(load(os.path.join(args.r4, "working-00.png"), 4).crop(bx))
    wb, cb = wc(load(os.path.join(args.r5raw, "working-00.png"), 4).crop(bx))
    b_raw = on_ground(load(os.path.join(args.r5raw, "working-00.png"), 4)).crop(bx)
    bar.append(cap(hrow([a_, mark_clip(a_), b_, mark_clip(b_raw)], 4),
                   f"{k}\nround 4: white {wa}, clipped {ca} | round 5: white {wb}, clipped {cb} (4x, this crop)"))
for b_ in bar:
    rows.append(b_)
# glow-only
rows.append(block("9. THE LIGHT ALONE (every glow on, the sun, sky and ground off; the brightest of 8 frames, 2x)", [
    "Lit (luminance >= 24) px sorted by the part under them in the colour map: only the melt, the helium's liquid and "
    "the windows (the riser's glass, the sight glass) may be lit.",
], W))
gl = []
for v in V:
    g = GLOWIM[v].convert("RGBA")
    gl.append(cap(g.crop((VIEW1[0] * 2, VIEW1[1] * 2, VIEW1[2] * 2, VIEW1[3] * 2)).resize((304, 328), Image.LANCZOS),
                  f"{v}: allowed {GLOW[v]['lit_allowed']}, elsewhere {GLOW[v]['lit_elsewhere']}"))
cmi = Image.open(os.path.join(args.cmap, "colourmap.png")).convert("RGBA")
gl.append(cap(cmi.crop((VIEW1[0] * 2, VIEW1[1] * 2, VIEW1[2] * 2, VIEW1[3] * 2)).resize((304, 328), Image.LANCZOS),
              "the colour map (2x): a paint or metal per unit"))
rows.append(hrow(gl, 12))
used = sorted(groups.items())
rows.append(block("8. PAINT PER UNIT (the colour map's groups)", ["; ".join(f"{g} {h}" for g, h in used)], W, size=12))
H = sum(r.height for r in rows) + PAD * (len(rows) + 1)
Wd = max(r.width for r in rows) + 2 * PAD
sheet = Image.new("RGBA", (Wd, H), BG)
y = PAD
for r in rows:
    sheet.alpha_composite(r, (PAD, y))
    y += r.height + PAD
if max(sheet.size) > 7900:
    k = 7900 / max(sheet.size)
    sheet = sheet.resize((round(sheet.width * k), round(sheet.height * k)), Image.LANCZOS)
sheet.convert("RGB").save(os.path.join(args.out, "08-gas-lift-tower-variants.png"))
json.dump(dict(variants=MEAS, vanilla={k: v["fig"] for k, v in VAN.items()}, reaction_plant=RP),
          open(os.path.join(args.out, "measures.json"), "w"), indent=1)
print("sheet", sheet.size)
