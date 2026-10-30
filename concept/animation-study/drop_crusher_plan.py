#!/usr/bin/env python3
"""The Drop Crusher plan: every figure drop-crusher-plan.md quotes, recomputed.

Usage:
    python3 drop_crusher_plan.py [--repo <space-age-extended checkout>] [--evidence <dir>] [--out <dir>]

Run foundry_study.py first: this reads its foundry-figures.json for the foundry's side
of every comparison. Reads the shipped Drop Crusher sheets and meta.json
(graphics/entity/drop-crusher/, concept/drop-crusher/model/sheets/meta.json) and the
Blender logs named in LOGS (no Blender is run). Writes:
    drop-crusher-figures.json    every number in the plan
    drop-crusher-timeline.png    the planned loop against the shipped one, and the steps
Two runs give byte-identical files.

The plan (PLAN) is authored; the script checks it: the steps cover every frame once,
add up to the loop, the loop is the recipe's 240 ticks at the chosen speed, no
accent sits on frame 0, and frame 0 is the cocked rest pose the spec asks for.
"""
import argparse
import hashlib
import json
import os
import re
import statistics

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.normpath(os.path.join(HERE, "..", ".."))
EVIDENCE_DEFAULT = "/home/lstan/data/git/space-age-extended/evidence"

PROGRESS = 0.5          # CraftingMachineGraphicsSet.animation_progress default (knowledge/engine.md)
CRAFTING_SPEED = 1      # the Drop Crusher (spec §15, machines.lua)
RECIPE_TICKS = 240      # sae-crushing: 4 s, one drop a craft (spec §2)

# ---- the shipped loop (machines.lua, drop_crusher.py): 24 frames, speed 0.2
NOW = dict(frames=24, speed=0.2, top=6, seat=14, rise=16, fall=8,
           accents=[(14, "drop"), (18, "pawl"), (22, "pawl"), (2, "pawl"), (6, "trip")])

# ---- the plan: 60 frames at speed 0.5. Steps in frame order: first, last, name, motion, ease.
PLAN_FRAMES = 60
PLAN_SPEED = 0.5
PLAN = [
    (0, 12, "Wind-up, upper half", "crown climbs the rack, gears turn, pawl ticks over the teeth",
     "even speed, slowing over the last 4 frame changes into the top"),
    (13, 19, "Top hold", "crown at the top (reached on 13), held by the pawl; gears stopped", "hold"),
    (20, 21, "Trip", "pawl kicks clear of the rack", "snap (2 frames)"),
    (22, 27, "Fall", "crown drops; gears spin back with the rack",
     "faster every frame (t squared): 7 frame changes, 21 to the seat on 28, 28 ticks"),
    (28, 28, "Land", "crown seated flush in the collar; gears stop dead", "hard stop"),
    (29, 41, "Seated hold", "everything still; the pawl drops back onto the rack on 36-37", "hold, one 2-frame snap"),
    (42, 59, "Wind-up, lower half", "motor takes up the load, crown leaves the seat", "slow in over 4 frames, then even"),
]
PLAN_ACCENTS = [(6, "pawl"), (20, "trip"), (28, "drop"), (50, "pawl"), (58, "pawl")]
PLAN_TOP_REACHED, PLAN_TRIP, PLAN_LAND = 13, 20, 28
FALL_FROM = 21                     # the last frame at the top: the fall is the frame changes 21 -> 28
PAWL_REENGAGE = (36, 37)

# ---- Blender logs for render-time estimates: (label, path under evidence, canvas, samples note)
LOGS = [
    ("vent pump r2 (3x3, nearest in size)", "gas-pump-t15/r2/blender.log",
     dict(full="still", layer="mech", qa=None)),
    ("ballast drill t03m s2 north (5x5)", "ballast-drill-t03m/s2/north/plate/blender.log",
     dict(full="still", layer="stroke", qa="stroke-ring")),
    ("reaction plant t09d north (5x5, slowest)", "rp-t09d/run-north/blender.log",
     dict(full="still", layer="drive", qa="press-pack")),
]


def lift_now(f):
    """The shipped crown height above its seat, as a share of the travel (drop_crusher.py lift())."""
    s = (f + 10) % 24
    if s <= 16:
        return s / 16
    k = (s - 16) / 8
    return 1 - k * k


def lift_plan(f):
    """The planned crown height above its seat, as a share of the travel, frame f of 60."""
    s = (f + 32) % 60                       # seat-first step: 0 = landing
    if s == 0 or 1 <= s <= 13:
        return 0.0                          # landed, seated hold
    if 14 <= s <= 45:                       # wind-up, 32 frames: ease in 4, even, ease out 4
        t = s - 13                          # 1..32
        # trapezoid speed profile, integrated: ramps over 4 frames each end
        def pos(x):
            a, n = 4.0, 32.0
            v = 1.0 / (n - a)               # even speed so the total is 1
            if x <= a:
                return v * x * x / (2 * a)
            if x <= n - a:
                return v * (a / 2 + (x - a))
            y = n - x
            return 1 - v * y * y / (2 * a)
        return pos(t)
    if 46 <= s <= 53:
        return 1.0                          # top hold and trip
    k = (s - 53) / 7                        # fall: s 54..59, landing at s 60 = 0
    return 1 - k * k


def parse_log(path):
    ts, names = [], []
    for line in open(path, errors="replace"):
        m = re.match(r"\s*(\d+):(\d+\.\d+)\s+render\s+\| Saved: .*/([^/]+)\.png", line)
        if m:
            ts.append(int(m.group(1)) * 60 + float(m.group(2)))
            names.append(m.group(3))
    groups = {}
    for i in range(1, len(ts)):
        g = re.sub(r"-(north|east|south|west)$", "", names[i])
        g = re.sub(r"-\d+$", "", g)
        groups.setdefault(g, []).append(ts[i] - ts[i - 1])
    return dict(first_save_s=round(ts[0], 1), total_s=round(ts[-1], 1), renders=len(ts),
                groups={g: dict(n=len(v), median=round(statistics.median(v), 2)) for g, v in groups.items()})


def mib(px):
    return round(px * 4 / 2 ** 20, 2)


def font(size):
    for p in ("/usr/share/fonts/TTF/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO_DEFAULT)
    ap.add_argument("--evidence", default=EVIDENCE_DEFAULT)
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    F = json.load(open(os.path.join(a.out, "foundry-figures.json")))
    GD = os.path.join(a.repo, "graphics", "entity", "drop-crusher")
    meta = json.load(open(os.path.join(a.repo, "concept", "drop-crusher", "model", "sheets", "meta.json")))
    fig = {}

    # ---- timing
    def timing(frames, speed):
        fpt = speed * CRAFTING_SPEED * PROGRESS
        return dict(frames=frames, speed=speed, frames_per_tick=fpt, ticks_per_frame=round(1 / fpt, 3),
                    loop_ticks=round(frames / fpt, 3), fps=round(60 * fpt, 2),
                    sum=f"{frames} / ({speed} x {CRAFTING_SPEED} x {PROGRESS}) = {frames / fpt:g} ticks")
    fig["timing_now"] = timing(NOW["frames"], NOW["speed"])
    fig["timing_plan"] = timing(PLAN_FRAMES, PLAN_SPEED)
    fig["timing_foundry"] = F["timing"]
    fig["frame_count_options"] = [dict(timing(n, n / 120), speed_exact=(n / 120) == round(n / 120, 4))
                                  for n in (24, 36, 48, 60, 72, 96, 120)]

    # ---- the plan's checks
    cover = np.zeros(PLAN_FRAMES, int)
    for s, e, *_ in PLAN:
        cover[s:e + 1] += 1
    fig["plan_steps"] = [dict(first=s, last=e, frames=e - s + 1, ticks=round((e - s + 1) / fig["timing_plan"]["frames_per_tick"], 1),
                              name=n, motion=m, ease=es, accents=[[f, k] for f, k in PLAN_ACCENTS if s <= f <= e])
                         for s, e, n, m, es in PLAN]
    lp = [lift_plan(f) for f in range(PLAN_FRAMES)]
    ln = [lift_now(f) for f in range(NOW["frames"])]
    rise = sum(st["frames"] for st in fig["plan_steps"] if st["name"].startswith(("Wind", "Top", "Trip")))
    fig["plan_checks"] = dict(
        every_frame_once=bool((cover == 1).all()),
        frames_sum=" + ".join(str(st["frames"]) for st in fig["plan_steps"]) + f" = {sum(st['frames'] for st in fig['plan_steps'])}",
        loop_ticks=fig["timing_plan"]["loop_ticks"], recipe_ticks=RECIPE_TICKS,
        loop_matches_recipe=abs(fig["timing_plan"]["loop_ticks"] - RECIPE_TICKS) < 1e-6,
        accent_on_frame_0=any(f == 0 for f, _ in PLAN_ACCENTS),
        frame0_lift=round(lp[0], 3), frame0_between_clicks=[58, 6],
        rise_top_trip_frames=rise, fall_land_hold_frames=PLAN_FRAMES - rise,
        rise_share=round(rise / PLAN_FRAMES, 3),
        top_is_1=lp[PLAN_TOP_REACHED] == 1.0, seated_on_land=lp[PLAN_LAND] == 0.0,
        fall_increments=[round(lp[f + 1] - lp[f], 3) for f in range(FALL_FROM, PLAN_LAND)],
        top_reached_frame=min(f for f in range(PLAN_FRAMES) if lp[f] == 1.0))
    fig["lift_plan"] = [round(v, 4) for v in lp]

    # the frame_sequence: one sheet frame per distinct pose (crown height, pawl state)
    def pawl(f):
        if f in (PLAN_TRIP, PLAN_TRIP + 1):
            return f"kick-{f}"
        if PLAN_TRIP + 2 <= f < PAWL_REENGAGE[0]:
            return "clear"
        if f in PAWL_REENGAGE:
            return f"drop-{f}"
        return "engaged"
    keys, seq = [], []
    for f in range(PLAN_FRAMES):
        k = (round(lp[f], 6), pawl(f))
        if k not in keys:
            keys.append(k)
        seq.append(keys.index(k) + 1)              # 1-based, as the engine's frame_sequence
    fig["frame_sequence"] = dict(
        entries=len(seq), unique_frames=len(keys), animation=seq, idle=[1] * PLAN_FRAMES,
        note="accent frames count the sequence's entries from 0 (settled: Reaction Plant T04/T10, 2026-10-29)")
    fig["lift_now"] = [round(v, 4) for v in ln]

    def holds(lift):
        n = len(lift)
        still = [abs(lift[(f + 1) % n] - lift[f]) < 1e-9 for f in range(n)]
        return sum(still)
    fig["crown_still_transitions"] = dict(now=holds(ln), plan=holds(lp))
    fig["crown_still_ticks"] = dict(
        now=round(holds(ln) / fig["timing_now"]["frames_per_tick"], 1),
        plan=round(holds(lp) / fig["timing_plan"]["frames_per_tick"], 1))
    # both counted the same way: frame changes from the last frame at the top to the seat
    now_changes = NOW["seat"] - NOW["top"]                 # 6 -> 14: 8
    plan_changes = PLAN_LAND - FALL_FROM                   # 21 -> 28: 7
    fall_now_ticks = now_changes / fig["timing_now"]["frames_per_tick"]
    fall_plan_ticks = plan_changes / fig["timing_plan"]["frames_per_tick"]
    fig["fall"] = dict(now_changes=now_changes, now_ticks=fall_now_ticks, now_seconds=round(fall_now_ticks / 60, 3),
                       plan_changes=plan_changes, plan_ticks=fall_plan_ticks, plan_seconds=round(fall_plan_ticks / 60, 3),
                       faster=round(fall_now_ticks / fall_plan_ticks, 2),
                       sum=f"now {NOW['seat']} - {NOW['top']} = {now_changes} changes x 10 ticks = {fall_now_ticks:g}; "
                           f"plan {PLAN_LAND} - {FALL_FROM} = {plan_changes} changes x 4 ticks = {fall_plan_ticks:g}",
                       now_last_step=round(ln[NOW["seat"] - 1] - ln[NOW["seat"]], 3), plan_last_step=round(lp[27] - lp[28], 3))

    # ---- the shipped sheets, measured
    base = np.asarray(Image.open(os.path.join(GD, "base.png")).convert("RGBA")).astype(np.int16)
    stroke = np.asarray(Image.open(os.path.join(GD, "stroke.png")).convert("RGBA")).astype(np.int16)
    sw, sh = meta["stroke"]["size"]
    frames = [stroke[:, i * sw:(i + 1) * sw] for i in range(meta["stroke"]["frames"])]
    bw, bh = meta["base"]["size"]
    # where the stroke window sits on the base canvas, from the two shifts (64 px a tile)
    # a sprite's entity origin sits at size / 2 - 64 x shift in its own pixels
    ox = round((bw / 2 - 64 * meta["base"]["shift"][0]) - (sw / 2 - 64 * meta["stroke"]["shift"][0]))
    oy = round((bh / 2 - 64 * meta["base"]["shift"][1]) - (sh / 2 - 64 * meta["stroke"]["shift"][1]))
    comp = []
    for fr in frames:
        c = base.copy().astype(float)
        sub = c[oy:oy + sh, ox:ox + sw]
        al = fr[..., 3:4] / 255.0
        sub[..., :3] = fr[..., :3] * al + sub[..., :3] * (1 - al)
        sub[..., 3:4] = 255 * al + sub[..., 3:4] * (1 - al)
        comp.append(c.astype(np.int16))
    comp = np.stack(comp)
    pm = comp[..., :3] * comp[..., 3:4] // 255
    chg = np.abs(np.roll(pm, -1, 0) - pm).max(-1) > 12
    alpha = (comp[..., 3] > 0).any(0)
    fig["now_measured"] = dict(
        stroke_window_on_base=[ox, oy, sw, sh],
        moving_share_of_opaque=round(float((chg.any(0) & alpha).sum()) / float(alpha.sum()), 4),
        foundry_moving_share=F["moving_share_of_opaque"],
        changed_px_per_frame=[int(v) for v in chg.reshape(len(frames), -1).sum(1)],
        stroke_path_declared_px=meta["checks"]["stroke_path_px"]["declared"])
    fig["now_measured"]["window_share_of_building"] = round(sw * sh / float(alpha.sum()), 3)

    # ---- sheet budgets (raw RGBA, 4 bytes a px, before atlas packing)
    W, H = meta["base"]["size"]
    SWD, SHD = meta["base-shadow"]["size"]
    LW, LH = meta["status-lamp"]["size"]
    still_px = W * H + SWD * SHD + LW * LH

    def method_a(n):
        px = still_px + sw * sh * n
        return dict(px=px, mib=mib(px), sum=f"{W}x{H} + {SWD}x{SHD} + {LW}x{LH} + {sw}x{sh} x {n} = {px} px x 4 B = {mib(px)} MiB")

    def method_b(n, shadow_moves=False):
        px = W * H * n + SWD * SHD * (n if shadow_moves else 1) + LW * LH
        s = f"{W}x{H} x {n} + {SWD}x{SHD}" + (f" x {n}" if shadow_moves else "") + f" + {LW}x{LH} = {px} px x 4 B = {mib(px)} MiB"
        return dict(px=px, mib=mib(px), sum=s)
    fig["budget"] = dict(
        foundry_working_mib=F["budget"]["working_rgba_mib"], foundry_sum=F["budget"]["sum_working"],
        foundry_anim_mib=round(2 * 2704 * 2832 * 4 / 2 ** 20, 2),
        now_A24=method_a(24), plan_A60=method_a(PLAN_FRAMES), plan_B60=method_b(PLAN_FRAMES),
        plan_B60_shadow=method_b(PLAN_FRAMES, True), B24=method_b(24),
        options={n: dict(A=method_a(n), B=method_b(n)) for n in (24, 48, 60, 96)},
        unique_frames_with_sequence=dict(frames=len(keys), sum="13 wind-up + 1 top + 2 trip + 6 fall + 1 seated, pawl clear + 2 pawl drop-in + 1 seated, pawl in + 18 wind-up = 44", A=method_a(len(keys)), B=method_b(len(keys))),
        sheet_layout=dict(
            A60=f"{sw} x {sh} frames, 10 to a row: {sw * 10} x {sh * 6} px, one file",
            B60=f"{W} x {H} frames, 10 to a row: {W * 10} x {H * 6} px, one file"))

    # ---- render time from the logs
    logs = {}
    for label, rel, roles in LOGS:
        p = os.path.join(a.evidence, rel)
        L = parse_log(p)
        g = L["groups"]
        t_full = g[roles["full"]]["median"]
        t_layer = g[roles["layer"]]["median"]
        t_qa = g[roles["qa"]]["median"] if roles["qa"] else t_layer
        start = L["first_save_s"]
        n = PLAN_FRAMES

        def est(frame_t, frames, label_frame):
            # startup (to the first saved render) + 3 one-off passes (still, shadow, lamp) at the
            # whole-building time + the animation frames + 2 QA renders a frame (gear, crown track)
            tot = start + 3 * t_full + frames * frame_t + 2 * frames * t_qa
            return dict(seconds=round(tot, 1), minutes=round(tot / 60, 1),
                        sum=f"{start} + 3 x {t_full} + {frames} x {frame_t} ({label_frame}) + 2 x {frames} x {t_qa} (QA) = {tot:.1f} s")
        u = len(keys)
        logs[label + " [sequence]"] = dict(log=p, A44=est(t_layer, u, "layer"), B44=est(t_full, u, "whole building"))
        logs[label] = dict(log=p, startup_s=start, t_full_s=t_full, t_layer_s=t_layer, t_qa_s=t_qa,
                           roles=roles, renders=L["renders"], total_s=L["total_s"],
                           A_now24=est(t_layer, 24, "layer"), A60=est(t_layer, n, "layer"),
                           B60=est(t_full, n, "whole building"),
                           B60_shadow=dict(seconds=round(est(t_full, n, "")["seconds"] + n * g["shadow"]["median"], 1),
                                           sum=est(t_full, n, "whole building")["sum"].split(" = ")[0]
                                           + f" + {n} x {g['shadow']['median']} (shadow) = "
                                           + f"{est(t_full, n, '')['seconds'] + n * g['shadow']['median']:.1f} s"))
    fig["render_time"] = logs

    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "drop-crusher-figures.json"), "w") as fh:
        json.dump(fig, fh, indent=1)
    draw(fig, comp, a.out)
    for f in ("drop-crusher-figures.json", "drop-crusher-timeline.png"):
        p = os.path.join(a.out, f)
        print(f, hashlib.sha256(open(p, "rb").read()).hexdigest()[:16])
    print("checks:", fig["plan_checks"])


def draw(fig, comp, out):
    W = 2920
    fT, fS, fL = font(36), font(26), font(22)
    H = 1680
    im = Image.new("RGB", (W, H), (24, 24, 24))
    d = ImageDraw.Draw(im)
    d.text((20, 14), "Drop Crusher: the shipped stroke (24 frames, 10 ticks a frame) against the plan "
                     "(60 frame_sequence entries over 44 sheet frames, 4 ticks an entry). One loop = 240 ticks = one craft.", fill=(235, 235, 235), font=fS)
    # shipped frames, composited over the plate, 1x, cropped round the roof
    y0 = 60
    d.text((20, y0), "Shipped, every frame: the roof, sheet pixels at 2x (the plate with the stroke layer on it):",
           fill=(220, 220, 220), font=fL)
    cw, ch = 120, 100
    for i in range(24):
        fr = comp[i]
        imf = Image.fromarray(fr.astype(np.uint8), "RGBA")
        bg = Image.new("RGBA", imf.size, (38, 38, 38, 255))
        bg.alpha_composite(imf)
        c = bg.crop((39, 0, 39 + cw, ch)).resize((cw * 2, ch * 2), Image.NEAREST).convert("RGB")
        r, k = divmod(i, 12)
        x, y = 20 + k * (cw * 2 + 2), y0 + 34 + r * (ch * 2 + 34)
        im.paste(c, (x, y))
        d.text((x + 4, y + ch * 2 + 2), str(i), fill=(255, 220, 90), font=fL)
    # lift curves against ticks
    gx0, gx1, gy0, gy1 = 120, W - 40, 620, 1000
    d.rectangle((gx0, gy0, gx1, gy1), outline=(90, 90, 90))
    d.text((20, gy0 - 40), "Crown height above its seat (share of the 0.7-tile travel) against ticks; "
                           "dots = frames. Grey: shipped. Orange: plan.", fill=(220, 220, 220), font=fL)

    def X(t):
        return gx0 + (gx1 - gx0) * t / 240

    def Y(v):
        return gy1 - (gy1 - gy0) * v
    for t in range(0, 241, 20):
        d.line((X(t), gy1, X(t), gy1 + 8), fill=(150, 150, 150))
        d.text((X(t) - 14, gy1 + 10), str(t), fill=(170, 170, 170), font=fL)
    for series, tpf, col in ((fig["lift_now"], 10, (160, 160, 160)), (fig["lift_plan"], 4, (255, 160, 50))):
        n = len(series)
        pts = [(X(f * tpf), Y(series[f])) for f in range(n)]
        for f in range(n):                   # a frame holds for its ticks: draw it as steps
            x0, x1 = X(f * tpf), X((f + 1) * tpf)
            d.line((x0, Y(series[f]), x1, Y(series[f])), fill=col, width=4)
            d.line((x1, Y(series[f]), x1, Y(series[(f + 1) % n])), fill=col, width=2)
        for p in pts:
            d.ellipse((p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5), fill=col)
    for f, k in NOW["accents"]:
        d.text((X(f * 10) - 8, gy0 + 6), k[0].upper(), fill=(200, 200, 200), font=fL)
    for f, k in PLAN_ACCENTS:
        d.line((X(f * 4), gy0, X(f * 4), gy1), fill=(255, 90, 60), width=2)
        d.text((X(f * 4) + 4, gy0 + 34), f"{f} {k}", fill=(255, 140, 110), font=fL)
    d.text((gx0, gy1 + 40), "Letters at the top: shipped accents (P pawl, T trip, D drop). Red lines: planned accents, "
                            "labelled with their frame.", fill=(180, 180, 180), font=fL)
    # plan steps bar, frames
    sy = 1120
    d.text((20, sy - 40), "The plan, frame by frame (60 frames; frame 0 = cocked rest pose, as the spec asks):",
           fill=(220, 220, 220), font=fL)
    px = (W - 40) / 60
    pal = [(70, 110, 170), (90, 140, 90), (170, 90, 60), (140, 80, 140), (200, 60, 60), (90, 140, 90), (70, 110, 170)]
    for i, st in enumerate(fig["plan_steps"]):
        x0, x1 = 20 + st["first"] * px, 20 + (st["last"] + 1) * px
        d.rectangle((x0, sy, x1 - 2, sy + 170), fill=pal[i])
        lines = [f"{i + 1}. {st['name']}", f"{st['first']}-{st['last']} ({st['frames']} f, {st['ticks']:g} t)"] + \
                _wrap(d, st["ease"], x1 - x0 - 12, fL)
        if x1 - x0 < 120:                    # too narrow to name: the number, named in the key below
            lines = [f"{i + 1}."]
        for j, t in enumerate(lines[:5]):
            d.text((x0 + 6, sy + 6 + j * 32), _fit(d, t, x1 - x0 - 10, fL), fill=(255, 255, 255), font=fL)
    for f, k in PLAN_ACCENTS:
        x = 20 + (f + 0.5) * px
        d.line((x, sy + 170, x, sy + 200), fill=(255, 90, 60), width=3)
        d.text((x - 10, sy + 204), f"{f} {k}", fill=(255, 140, 110), font=fL)
    # lanes: crown, gears, pawl
    narrow = [f"{i + 1}. {st['name']} ({st['first']}-{st['last']}, {st['frames']} f)"
              for i, st in enumerate(fig["plan_steps"]) if (st["last"] + 1 - st["first"]) * px < 120]
    d.text((20, sy + 236), "Narrow steps: " + ";  ".join(narrow), fill=(220, 220, 220), font=fL)
    ly = sy + 280
    lanes = [("crown moving", [abs(fig["lift_plan"][(f + 1) % 60] - fig["lift_plan"][f]) > 1e-9 for f in range(60)]),
             ("gears turning", [abs(fig["lift_plan"][(f + 1) % 60] - fig["lift_plan"][f]) > 1e-9 for f in range(60)]),
             ("pawl moving", [f in (20, 21) or f in PAWL_REENGAGE for f in range(60)])]
    for j, (name, on) in enumerate(lanes):
        y = ly + j * 50
        d.rectangle((20, y, W - 20, y + 40), fill=(34, 34, 34))
        for f in range(60):
            if on[f]:
                d.rectangle((20 + f * px, y + 6, 20 + (f + 1) * px - 2, y + 34), fill=(230, 180, 70))
        d.text((26, y + 8), name, fill=(255, 255, 255), font=fL, stroke_width=2, stroke_fill=(0, 0, 0))
    im.save(os.path.join(out, "drop-crusher-timeline.png"), optimize=False)


def _wrap(d, text, width, f):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > width and cur:
            out.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        out.append(cur)
    return out


def _fit(d, text, width, f):
    while text and d.textlength(text, font=f) > width:
        text = text[:-2] + "…" if len(text) > 2 else ""
    return text


if __name__ == "__main__":
    main()
