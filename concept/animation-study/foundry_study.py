#!/usr/bin/env python3
"""The foundry, frame by frame: every figure in foundry.md, recomputed from the game files.

Usage:
    python3 foundry_study.py [--game <Factorio data dir>] [--out <dir>]

Defaults: the game at /mnt/data/SteamLibrary/steamapps/common/Factorio/data and
--out the directory this script sits in. Writes:
    foundry-figures.json    every number foundry.md quotes
    foundry-timeline.png    the timeline sheet: key frames, step labels, part lanes,
                            the lights and smoke curves, the accents
    foundry-parts.png       frame 0 with the part regions the lanes measure
It reads nothing but the game's files and writes nothing but those three. Two runs
give byte-identical files (no clock, no randomness, fixed drawing order).

What is authored and what is measured. The steps (STEPS) and the part regions
(PARTS) are authored: named by looking at the frames. Everything else is measured,
and the steps are checked against the measurement: every frame 0..127 in exactly one
step, the step lengths adding to 128, every accent the game declares falling in a
step, and each step boundary reported with the nearest part start or stop the data
finds. Motion is measured as "motion energy": the pixels of a part's region whose
premultiplied colour changes by more than THRESH levels from one frame to the next.
It is a proxy for speed, not a displacement: a textured part sliding faster changes
more pixels a frame, until it saturates.
"""
import argparse
import hashlib
import json
import os
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = 128
SPEED = 0.16                 # foundry-pictures.lua: foundry_animation_speed
CRAFTING_SPEED = 4           # entities.lua: the foundry's crafting_speed
PROGRESS = 0.5               # CraftingMachineGraphicsSet.animation_progress default
THRESH = 12                  # levels of premultiplied colour that count as a change
ACTIVE = 0.25                # a part moves on a frame when its smoothed energy is over this share of its peak

# The part regions, in the anim layer's frame (338 x 354 px), x0, y0, x1, y1.
# Named by looking at the frames (README: c-*.png crops in the evidence folder).
PARTS = [
    ("head", "charge head: the hatch on top of the tower", (140, 15, 260, 110)),
    ("launder", "launder: the red trough that telescopes out on the west", (55, 100, 155, 215)),
    ("arm", "pouring arm: the red hood that comes down onto the crucible", (225, 120, 295, 205)),
    ("crucible", "crucible: sinks into its pit, rises, tips and pours", (215, 205, 300, 290)),
    ("moulds", "mould ring: the cast boxes round the tower's foot", (50, 230, 215, 320)),
    ("flap", "ejector plate: the pale plate on the north-west that kicks out", (0, 60, 50, 145)),
]

# The steps: (first frame, last frame, name, what happens). Authored; checked below.
STEPS = [
    (0, 15, "Reset", "The crucible rights itself after the last pour; the mould ring settles."),
    (16, 37, "Close and lower", "The head's hatch closes, the launder telescopes out, the crucible sinks into its pit."),
    (38, 47, "Clamp", "The pouring arm comes down onto the crucible and locks; the launder reaches its stop."),
    (48, 73, "Charge (hold)", "Arm, launder and hatch hold still; the mould ring turns; the fire and the clunk land mid-hold."),
    (74, 99, "Open and raise", "The arm lifts, the launder runs back in, the hatch opens and the crucible climbs out."),
    (100, 117, "Tip and pour", "The crucible tips forward and pours; a puff from the pipe."),
    (118, 127, "Eject", "The ejector plate snaps out, the rocks drop, the plate bounces; the loop closes on frame 0."),
]


def load_frames(path_stem, w, h, files, line, rows, mode="RGBA"):
    out = []
    for f in files:
        im = np.asarray(Image.open(f"{path_stem}{f}").convert(mode)).astype(np.int16)
        for r in range(rows):
            for c in range(line):
                out.append(im[r * h:(r + 1) * h, c * w:(c + 1) * w])
    return np.stack(out)


def lua_table(path):
    """The plain numbers of a graphics .lua file: width, height, line_length, shift."""
    t = open(path).read()
    d = {}
    for k in ("width", "height", "line_length", "lines_per_file"):
        m = re.search(rf"\b{k}\s*=\s*(\d+)", t)
        if m:
            d[k] = int(m.group(1))
    m = re.search(r"by_pixel\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)", t)
    if m:
        d["shift_px"] = [float(m.group(1)), float(m.group(2))]
    d["files"] = len(re.findall(r'"-\d+\.png"', t)) or 1
    return d


def accents(entities_lua):
    """The foundry's sound accents, in declaration order: (frame, sound stem)."""
    t = open(entities_lua).read()
    i = t.index('name = "foundry"')
    j = t.index("sound_accents", i)
    k = t.index("max_sounds_per_prototype", j)
    out = []
    for line in t[j:k].splitlines():
        m = re.search(r"foundry/(foundry-[\w-]+?)(?:\.ogg|\")", line)
        f = re.search(r"frame\s*=\s*(\d+)", line)
        if m and f:
            out.append((int(f.group(1)), m.group(1)))
    return out


def runs(flags):
    """Circular runs of True: (start, length)."""
    n = len(flags)
    if flags.all():
        return [(0, n)]
    start = int(np.argmin(flags))           # a False frame: start scanning after it
    res, i = [], 0
    while i < n:
        f = (start + i) % n
        if flags[f]:
            j = i
            while j < n and flags[(start + j) % n]:
                j += 1
            res.append(((start + i) % n, j - i))
            i = j
        else:
            i += 1
    return sorted(res)


def ease(e):
    """Ease of one run from its energy curve: how it starts and how it stops."""
    peak = e.max()
    if peak == 0 or len(e) <= 6:
        return f"snap ({len(e)} frames)"
    k = max(1, min(3, len(e) // 4))
    a, b = e[:k].mean() / peak, e[-k:].mean() / peak

    def word(v, inout):
        return f"slow {inout}" if v < 0.45 else (f"snap {inout}" if v >= 0.7 else f"medium {inout}")
    if a >= 0.7 and b >= 0.7:
        return "even speed, hard start and stop"
    return f"{word(a, 'in')}, {word(b, 'out')}"


def font(size):
    for p in ("/usr/share/fonts/TTF/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default="/mnt/data/SteamLibrary/steamapps/common/Factorio/data")
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    G = os.path.join(a.game, "space-age", "graphics", "entity", "foundry") + "/"
    ENT = os.path.join(a.game, "space-age", "prototypes", "entity", "entities.lua")

    meta = {n: lua_table(G + n + ".lua") for n in
            ("foundry-anim", "foundry-base", "foundry-shadow", "foundry-lights", "foundry-smoke_1",
             "foundry-smoke_2", "foundry-smoke_3", "foundry-status-lamp", "foundry-frozen",
             "foundry-pipe-connections-north", "foundry-pipe-connections-east",
             "foundry-pipe-connections-south", "foundry-pipe-connections-west",
             "foundry-pipe-connections-north-frozen", "foundry-pipe-connections-east-frozen",
             "foundry-pipe-connections-south-frozen", "foundry-pipe-connections-west-frozen")}
    am = meta["foundry-anim"]
    A = load_frames(G + "foundry-anim", am["width"], am["height"], ["-1.png", "-2.png"], 8, 8)
    lm = meta["foundry-lights"]
    L = load_frames(G + "foundry-lights", lm["width"], lm["height"], ["-1.png", "-2.png"], 8, 8, "RGB")
    smokes = {}
    for s in ("foundry-smoke_1", "foundry-smoke_2", "foundry-smoke_3"):
        m = meta[s]
        smokes[s] = load_frames(G + s, m["width"], m["height"], [".png"], 8, 16)
    assert A.shape[0] == L.shape[0] == FRAMES and all(v.shape[0] == FRAMES for v in smokes.values())

    # ---- motion
    pm = A[..., :3] * A[..., 3:4] // 255
    nxt = np.roll(pm, -1, 0)
    chg = np.abs(nxt - pm).max(-1) > THRESH          # chg[f]: what changes from f to f + 1
    alpha = A[..., 3] > 0
    opaque = int(alpha[0].sum())
    ever = chg.any(0) & alpha.any(0)
    figures = dict(
        source=dict(game=a.game, anim=f"{am['width']}x{am['height']}", frames=FRAMES, threshold=THRESH),
        moving_share_of_opaque=round(float(ever.sum()) / float(alpha.any(0).sum()), 4),
        changed_px_per_frame=[int(x) for x in chg.reshape(FRAMES, -1).sum(1)],
        opaque_px_frame0=opaque,
    )
    cpf = np.array(figures["changed_px_per_frame"])
    figures["quietest_transition"] = [int(cpf.argmin()), int(cpf.min()), round(float(cpf.min()) / opaque, 4)]
    figures["busiest_transition"] = [int(cpf.argmax()), int(cpf.max()), round(float(cpf.max()) / opaque, 4)]
    figures["transitions_with_nothing_moving"] = int((cpf == 0).sum())

    parts = {}
    for name, desc, (x0, y0, x1, y1) in PARTS:
        e = chg[:, y0:y1, x0:x1].reshape(FRAMES, -1).sum(1).astype(float)
        es = (np.roll(e, 1) + e + np.roll(e, -1)) / 3
        on = es > ACTIVE * es.max()
        rs = []
        for s, n in runs(on):
            idx = [(s + i) % FRAMES for i in range(n)]
            rs.append(dict(start=s, end=(s + n - 1) % FRAMES, frames=n, ease=ease(es[idx]),
                           peak_frame=int(idx[int(np.argmax(es[idx]))])))
        holds = runs(~on)
        parts[name] = dict(desc=desc, box=[x0, y0, x1, y1], energy=[int(v) for v in e],
                           moving=[bool(v) for v in on], runs=rs,
                           moving_frames=int(on.sum()),
                           longest_hold=max((n for _, n in holds), default=0))
    figures["parts"] = parts

    # ---- lights and smoke
    lum = L.max(-1)
    figures["lights"] = dict(
        mean_level=[round(float(v), 2) for v in lum.reshape(FRAMES, -1).mean(1)],
        lit_px=[int(v) for v in (lum > 32).reshape(FRAMES, -1).sum(1)])
    lp = np.array(figures["lights"]["lit_px"])
    figures["lights"]["peak_frame"] = int(lp.argmax())
    figures["lights"]["dimmest_frame"] = int(lp.argmin())
    figures["lights"]["peak_over_dimmest"] = round(float(lp.max()) / max(1.0, float(lp.min())), 2)
    figures["smoke"] = {}
    for s, S in smokes.items():
        al = S[..., 3].reshape(FRAMES, -1).sum(1) / 255.0
        vis = al > 0.05 * al.max()
        figures["smoke"][s] = dict(alpha_sum=[round(float(v), 1) for v in al], peak_frame=int(al.argmax()),
                                   visible_runs=[dict(start=s0, frames=n) for s0, n in runs(vis)])

    # ---- steps: coverage, accents, what moves, boundaries against the data
    cover = np.zeros(FRAMES, int)
    for s, e, *_ in STEPS:
        cover[s:e + 1] += 1
    acc = accents(ENT)
    events = sorted({r["start"] for p in parts.values() for r in p["runs"]} |
                    {(r["end"] + 1) % FRAMES for p in parts.values() for r in p["runs"]})
    steps = []
    for s, e, name, what in STEPS:
        fr = list(range(s, e + 1))
        moving = {p: round(sum(parts[p]["moving"][f] for f in fr) / len(fr), 2) for p in parts}
        movers = [p for p, v in moving.items() if v >= 0.5]
        holders = [p for p, v in moving.items() if v == 0]
        eases = {}
        for p in movers:                    # the whole motion the step is part of, not the slice
            def overlap(r):
                return sum(1 for i in range(r["frames"]) if s <= (r["start"] + i) % FRAMES <= e)
            r = max(parts[p]["runs"], key=overlap)
            eases[p] = f"{r['start']}-{r['end']}: {r['ease']}"
        deltas = [((ev - s + 64) % FRAMES) - 64 for ev in events]
        dist = min(deltas, key=lambda v: (abs(v), v))
        steps.append(dict(first=s, last=e, frames=e - s + 1, name=name, what=what,
                          moving_share=moving, movers=movers, still=holders, eases=eases,
                          accents=[[f, n] for f, n in acc if s <= f <= e],
                          changed_px_mean=round(float(cpf[s:e + 1].mean()), 0),
                          lights_lit_px_mean=round(float(lp[s:e + 1].mean()), 0),
                          nearest_part_event_to_start=dist))
    figures["steps"] = steps
    figures["accents"] = [[f, n] for f, n in acc]
    figures["checks"] = dict(
        every_frame_once=bool((cover == 1).all()),
        frames_sum=int(sum(st["frames"] for st in steps)),
        accents_declared=len(acc),
        accent_frames_distinct=len({f for f, _ in acc}),
        accents_in_a_step=sum(1 for f, _ in acc if cover[f] == 1),
        accent_on_frame_0=any(f == 0 for f, _ in acc),
    )
    tps = SPEED * CRAFTING_SPEED * PROGRESS
    figures["timing"] = dict(frames_per_tick=round(tps, 4), loop_ticks=round(FRAMES / tps, 2),
                             loop_seconds=round(FRAMES / tps / 60, 3), frame_ms=round(1000 / (tps * 60), 2),
                             sum=f"{FRAMES} / ({SPEED} x {CRAFTING_SPEED} x {PROGRESS}) = {FRAMES / tps:.1f} ticks")

    # ---- the base layer under the anim layer: what of it is ever seen
    B = np.asarray(Image.open(G + "foundry-base.png").convert("RGBA"))
    bm = meta["foundry-base"]

    def origin(m):
        return (m["width"] / 2 - 2 * m["shift_px"][0], m["height"] / 2 - 2 * m["shift_px"][1])
    ob, oa = origin(bm), origin(am)
    dx, dy = int(round(ob[0] - oa[0])), int(round(ob[1] - oa[1]))
    cov = np.zeros(B.shape[:2], bool)
    cov[dy:dy + am["height"], dx:dx + am["width"]] = alpha.all(0)  # anim opaque in every frame
    base_op = B[..., 3] > 0
    figures["base_layer"] = dict(offset_in_base_px=[dx, dy], base_opaque_px=int(base_op.sum()),
                                 base_px_never_under_anim=int((base_op & ~cov).sum()),
                                 share_seen=round(float((base_op & ~cov).sum()) / float(base_op.sum()), 4))

    # ---- sheet budget
    files = sorted(f for f in os.listdir(G) if f.endswith(".png"))
    budget = []
    for f in files:
        im = Image.open(G + f)
        w, h = im.size
        budget.append(dict(file=f, size=[w, h], mode=im.mode, bytes_on_disk=os.path.getsize(G + f),
                           rgba_bytes=w * h * 4))
    tot_px = sum(b["size"][0] * b["size"][1] for b in budget)
    tot = sum(b["rgba_bytes"] for b in budget)
    working = [b for b in budget if not b["file"].startswith(("foundry-remnants", "foundry-frozen",
                                                               "foundry-reflection"))
               and "frozen" not in b["file"]]
    wt = sum(b["rgba_bytes"] for b in working)
    figures["budget"] = dict(
        files=budget, file_count=len(budget), total_px=tot_px, total_rgba_bytes=tot,
        total_rgba_mib=round(tot / 2 ** 20, 1),
        sum_all=" + ".join(f"{b['size'][0]}x{b['size'][1]}" for b in budget) + f" = {tot_px} px x 4 B = {tot / 2**20:.1f} MiB",
        working_rgba_mib=round(wt / 2 ** 20, 1),
        sum_working=" + ".join(f"{b['size'][0]}x{b['size'][1]}" for b in working) + f" = {wt // 4} px x 4 B = {wt / 2**20:.1f} MiB",
        anim_share_of_working=round(sum(b["rgba_bytes"] for b in working if "anim" in b["file"]) / wt, 3),
        on_disk_mib=round(sum(b["bytes_on_disk"] for b in budget) / 2 ** 20, 1))

    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "foundry-figures.json"), "w") as fh:
        json.dump(figures, fh, indent=1)

    draw_parts(A, a.out)
    draw_timeline(A, figures, a.out)
    for f in ("foundry-figures.json", "foundry-timeline.png", "foundry-parts.png"):
        p = os.path.join(a.out, f)
        print(f, hashlib.sha256(open(p, "rb").read()).hexdigest()[:16])
    c = figures["checks"]
    print("checks:", c)
    for st in steps:
        print(f"{st['first']:3d}-{st['last']:3d} {st['frames']:3d} {st['name']:16s} movers={st['movers']} "
              f"still={st['still']} accents={st['accents']} boundary~event {st['nearest_part_event_to_start']:+d}")


PAL = [(230, 80, 70), (90, 190, 90), (240, 200, 60), (70, 150, 230), (230, 140, 50), (190, 110, 220)]
STEP_PAL = [(120, 120, 120), (70, 110, 170), (170, 90, 60), (90, 140, 90), (150, 120, 60), (140, 80, 140), (60, 140, 150)]


def onbg(fr):
    im = Image.fromarray(fr.astype(np.uint8), "RGBA")
    bg = Image.new("RGBA", im.size, (38, 38, 38, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def draw_parts(A, out):
    im = onbg(A[0]).resize((338 * 2, 354 * 2), Image.NEAREST)
    d = ImageDraw.Draw(im)
    f = font(22)
    for i, (name, _, (x0, y0, x1, y1)) in enumerate(PARTS):
        d.rectangle((x0 * 2, y0 * 2, x1 * 2 - 1, y1 * 2 - 1), outline=PAL[i], width=3)
        d.text((x0 * 2 + 6, y0 * 2 + 4), name, fill=PAL[i], font=f, stroke_width=2, stroke_fill=(0, 0, 0))
    im.save(os.path.join(out, "foundry-parts.png"), optimize=False)


def draw_timeline(A, F, out):
    W = 2704
    px = W / FRAMES                         # 21.125 px a frame
    fT, fS, fL = font(40), font(26), font(22)
    thumbs = list(range(0, FRAMES, 4))      # 32 key frames, every 4th, two rows of 16
    tw, th = 169, 177
    top = 70
    lanes = len(PARTS) + 2                  # parts, lights, smoke
    lane_h = 60
    strip_y = top
    steps_y = strip_y + 2 * (th + 30) + 20
    lane_y = steps_y + 140
    acc_y = lane_y + lanes * lane_h + 10
    H = acc_y + 190
    im = Image.new("RGB", (W, H), (24, 24, 24))
    d = ImageDraw.Draw(im)
    tt = F["timing"]
    d.text((20, 14), f"Vanilla foundry: one 128-frame loop, {tt['loop_ticks']:.0f} ticks ({tt['loop_seconds']:.2f} s) "
                     f"at crafting speed 4.  Key frames every 4th; steps; what moves; lights, smoke, sound.",
           fill=(235, 235, 235), font=fS)
    for i, f in enumerate(thumbs):
        r, c = divmod(i, 16)
        x, y = c * tw, strip_y + r * (th + 30)
        im.paste(onbg(A[f]).resize((tw, th), Image.LANCZOS), (x, y + 26))
        d.text((x + 4, y), f"{f}", fill=(255, 220, 90), font=fL)
    # steps bar
    for i, st in enumerate(F["steps"]):
        x0, x1 = st["first"] * px, (st["last"] + 1) * px
        d.rectangle((x0, steps_y, x1 - 2, steps_y + 126), fill=STEP_PAL[i])
        d.text((x0 + 8, steps_y + 6), f"{i + 1}. {st['name']}", fill=(255, 255, 255), font=fS)
        d.text((x0 + 8, steps_y + 42), f"{st['first']}-{st['last']}  ({st['frames']} f)", fill=(240, 240, 240), font=fL)
        for j, line in enumerate(_wrap(d, "still: " + (", ".join(st["still"]) or "nothing"), x1 - x0 - 14, fL)[:2]):
            d.text((x0 + 8, steps_y + 70 + 26 * j), line, fill=(230, 230, 230), font=fL)
    # lanes
    names = [p[0] for p in PARTS]
    for li, name in enumerate(names + ["lights", "smoke"]):
        y = lane_y + li * lane_h
        d.rectangle((0, y, W, y + lane_h - 4), fill=(34, 34, 34))
        if name in F["parts"]:
            e = np.array(F["parts"][name]["energy"], float)
            mvg = F["parts"][name]["moving"]
            col = PAL[li]
        elif name == "lights":
            e = np.array(F["lights"]["lit_px"], float)
            mvg = [True] * FRAMES
            col = (255, 170, 60)
        else:
            e = sum(np.array(s["alpha_sum"]) for s in F["smoke"].values())
            mvg = [True] * FRAMES
            col = (170, 170, 190)
        if name in ("lights", "smoke"):     # these never stop: show their swing, min to max
            e = 0.15 + 0.85 * (e - e.min()) / max(1.0, e.max() - e.min())
        else:
            e = e / max(1.0, e.max())
        for f in range(FRAMES):
            h = int((lane_h - 10) * e[f])
            c = col if mvg[f] else tuple(v // 3 for v in col)
            d.rectangle((f * px, y + lane_h - 6 - h, (f + 1) * px - 2, y + lane_h - 6), fill=c)
        d.text((8, y + 4), name, fill=(255, 255, 255), font=fL, stroke_width=2, stroke_fill=(0, 0, 0))
    # step boundaries over the lanes
    for st in F["steps"]:
        x = st["first"] * px
        d.line((x, steps_y, x, acc_y), fill=(255, 255, 255), width=2)
    # accents
    seen = {}
    for f, n in F["accents"]:
        k = seen.get(f, 0)
        seen[f] = k + 1
        x = f * px + px / 2
        d.line((x, lane_y, x, acc_y + 20), fill=(255, 80, 80), width=3)
        tx = min(x - 10, W - 10 - d.textlength(n.replace("foundry-", ""), font=fL))
        d.text((tx, acc_y + 24 + k * 64), f"{f}", fill=(255, 120, 120), font=fL)
        d.text((tx, acc_y + 50 + k * 64), n.replace("foundry-", ""), fill=(255, 190, 190), font=fL)
    d.text((20, H - 34), "Part lanes: bar height = pixels changed that frame (motion energy); dim = below the moving "
                         "threshold. Lights: lit pixels; smoke: summed alpha of the three smoke layers (both min to max). "
                         "Red lines: the 12 sound accents.", fill=(190, 190, 190), font=fL)
    im.save(os.path.join(out, "foundry-timeline.png"), optimize=False)


def _wrap(d, text, width, f):
    out, cur = [], ""
    for w in text.split():
        s = (cur + " " + w).strip()
        if d.textlength(s, font=f) > width and cur:
            out.append(cur)
            cur = w
        else:
            cur = s
    if cur:
        out.append(cur)
    return out


def _fit(d, text, width, f):
    while text and d.textlength(text, font=f) > width:
        text = text[:-2] + "…" if len(text) > 2 else ""
    return text


if __name__ == "__main__":
    main()
