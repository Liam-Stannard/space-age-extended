#!/usr/bin/env python3
"""Vent Pump (T07c): the agreed effects as sheets the coder can attach, and where each one goes.

  python3 -B effects.py --model-json <render.sh out-dir>/model.json --out <dir>

Liam, 2026-10-21 (T07, Q5): the wisp "A2" (the head tank's gas offtake, a melt-lit fume, working only),
and the effects E2 (embers off the skimmings bin), E3 (the melt's orange ground light: a light, seen only
at night), E4 (cold breath at the stop valve each charge), E5 (a violet-grey purge puff from the float
chamber each charge). Drawn here procedurally (PIL: soft puffs under a moving noise, sparks with a short
trail), not rendered in Blender and not copied from vanilla, at the model's scale: 64 px a tile, drawn at
scale 0.5, as every sheet the model packs. E3 is not a sheet: it is a light (LightDefinition), given in
effects.json.

How each attaches (the chemical plant's way: vanilla's chemical-plant smoke is a working_visualisation
animation placed per direction with north_position ... west_position, its windows a sprite per
direction): every effect is one working_visualisation of the mining drill, drawn only while working,
`fadeout = true`, its animation's `shift` the sheet's own anchor (the source point's offset from the
frame's centre, negated) and its position per direction the model's anchor for that direction
(model.json "effects", measured off the model: where the offtake, the bin, the valve and the float
chamber stand in each variation). The two puffs synced to the charges (E4, E5) are 24 frames at the
loop's animation_speed 0.2 and no constant_speed, so they run with the machine's own loop; the wisp and
the embers have loops of their own (constant_speed). Unchecked in a client: the sync, the fade, the layer.

Writes into --out: wisp-a2.png, embers-e2.png, cold-breath-e4.png, purge-e5.png (each a sheet), and
effects.json (each sheet's frame size, frames, line_length, speed, blend, anchor, and per direction its
position, plus E3's light).
"""
import argparse
import json
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("--model-json", required=True)
ap.add_argument("--out", required=True)
A = ap.parse_args()
os.makedirs(A.out, exist_ok=True)
MODEL = json.load(open(A.model_json))
ANCH = MODEL["effects"]
DIRS = ("north", "east", "south", "west")
PPT = 64                        # px a tile on the sheet (drawn at scale 0.5)


def noise(w, h, seed, blur):
    rnd = random.Random(seed)
    im = Image.new("L", (w, h))
    im.putdata([rnd.randint(0, 255) for _ in range(w * h)])
    im = im.filter(ImageFilter.GaussianBlur(blur))
    lo, hi = im.getextrema()
    return im.point(lambda v: round(255 * (v - lo) / max(1, hi - lo)))


def puff_mask(r, seed, soft=0.45):
    """A soft, lumpy puff of radius r (px): a few blurred lobes, its alpha broken by a noise field."""
    s = max(8, int(r * 2.6))
    im = Image.new("L", (s, s))
    dr = ImageDraw.Draw(im)
    rnd = random.Random(seed)
    c = s / 2
    for k in range(5):
        a = rnd.uniform(0, 2 * math.pi)
        o = rnd.uniform(0, 0.35) * r
        rr = r * rnd.uniform(0.55, 0.8)
        x, y = c + o * math.cos(a), c + o * math.sin(a)
        dr.ellipse((x - rr, y - rr, x + rr, y + rr), fill=255)
    im = im.filter(ImageFilter.GaussianBlur(max(1.0, r * soft)))
    nz = noise(s, s, seed + 99, max(1.0, r * 0.25)).point(lambda v: 110 + v * 145 // 255)
    return ImageChops.multiply(im, nz)


def place(frame, mask, colour, alpha, at):
    """Paint `mask` (L) in `colour` at `alpha` (0-1) over frame (RGBA), centred at `at`."""
    layer = Image.new("RGBA", mask.size, colour + (0,))
    layer.putalpha(mask.point(lambda v: round(v * alpha)))
    x, y = round(at[0] - mask.width / 2), round(at[1] - mask.height / 2)
    tmp = Image.new("RGBA", frame.size)
    tmp.paste(layer, (x, y))
    frame.alpha_composite(tmp)


def lerp(a, b, u):
    return tuple(round(a[i] + (b[i] - a[i]) * u) for i in range(3))


def sheet(frames, line):
    w, h = frames[0].size
    out = Image.new("RGBA", (w * line, h * math.ceil(len(frames) / line)))
    for i, fr in enumerate(frames):
        out.paste(fr, ((i % line) * w, (i // line) * h))
    return out


def stats(frames, additive=False):
    peak_l, peak_a, white = 0, 0, 0
    for fr in frames:
        r, g, b, a = fr.split()
        if additive:
            r, g, b = (ImageChops.multiply(c, a) for c in (r, g, b))
        lum = Image.merge("RGB", (r, g, b)).convert("L")
        peak_l = max(peak_l, lum.getextrema()[1] if a.getextrema()[1] else 0)
        peak_a = max(peak_a, a.getextrema()[1])
        white += sum(1 for px in Image.merge("RGB", (r, g, b)).get_flattened_data() if min(px) >= 245)
    return dict(peak_luminance=peak_l, peak_alpha=peak_a, white_px=white)


# ---------------------------------------------------------------- A2: the wisp, a melt-lit fume off the gas offtake
WISP = dict(frames=32, size=(80, 176), src=(40, 166), line=8, speed=0.25)


def wisp():
    n, (w, h), (sx, sy) = WISP["frames"], WISP["size"], WISP["src"]
    m = 7                                   # puffs in flight; each is born again where its last one was
    lit, fume = (214, 122, 62), (118, 108, 102)
    frames = []
    for f in range(n):
        fr = Image.new("RGBA", (w, h))
        for i in range(m):
            age = (f / n + i / m) % 1.0       # seamless: the loop is one life of every puff
            rise = 140 * age ** 0.85
            x = sx + 5 * math.sin(2 * math.pi * (age * 1.3 + i * 0.37)) + 12 * age ** 1.5
            y = sy - rise
            r = 5 + 22 * age ** 0.9
            fade_in = min(1.0, age / 0.12)
            a = 0.8 * fade_in * (1 - age) ** 1.1
            col = lerp(lit, fume, min(1.0, age / 0.45))
            place(fr, puff_mask(r, 11 + i * 7), col, a, (x, y))
        frames.append(fr)
    return frames


# ---------------------------------------------------------------- E2: embers off the skimmings bin
EMBERS = dict(frames=24, size=(56, 104), src=(28, 92), line=12, speed=0.5)


def embers():
    n, (w, h), (sx, sy) = EMBERS["frames"], EMBERS["size"], EMBERS["src"]
    rnd = random.Random(5)
    sparks = [dict(phase=rnd.random(), x=rnd.uniform(-16, 16), drift=rnd.uniform(-8, 10), rise=rnd.uniform(48, 80),
                   life=rnd.uniform(0.35, 0.6), size=rnd.uniform(1.1, 1.9)) for _ in range(9)]
    frames = []
    for f in range(n):
        fr = Image.new("RGBA", (w * 4, h * 4))          # drawn at 4x, brought down for soft edges
        dr = ImageDraw.Draw(fr)
        for s in sparks:
            age = ((f / n) - s["phase"]) % 1.0
            if age > s["life"]:
                continue
            u = age / s["life"]
            x = sx + s["x"] + s["drift"] * u + 2 * math.sin(9 * u + s["phase"] * 6)
            y = sy - s["rise"] * u
            k = (1 - u) ** 0.7 * (0.75 + 0.25 * math.sin(40 * u + s["phase"] * 20))
            col = lerp((226, 130, 50), (178, 62, 26), u)
            for tail in range(3):                      # a short trail below it
                ty = y + tail * 2.2
                rr = s["size"] * (1 - tail * 0.28) * 4
                aa = round(255 * k * (1 - tail * 0.35))
                dr.ellipse((x * 4 - rr, ty * 4 - rr, x * 4 + rr, ty * 4 + rr), fill=col + (aa,))
        fr = fr.resize((w, h), Image.LANCZOS)
        halo = fr.filter(ImageFilter.GaussianBlur(2.2))
        halo.putalpha(halo.getchannel("A").point(lambda v: v // 2))     # a faint glow round each spark
        frames.append(Image.alpha_composite(halo, fr))
    return frames


# ---------------------------------------------------------------- E4 and E5: a puff at each charge, synced to the loop
COLD = dict(frames=24, size=(64, 72), src=(32, 60), line=12, speed=0.2, born=(1, 13), life=8,
            colour=(226, 229, 234), alpha=0.5, rise=30, r=(4, 15))
PURGE = dict(frames=24, size=(64, 80), src=(32, 68), line=12, speed=0.2, born=(4, 16), life=7,
             colour=(150, 138, 168), alpha=0.6, rise=36, r=(4, 14))


def synced_puff(cfg, seed):
    n, (w, h), (sx, sy) = cfg["frames"], cfg["size"], cfg["src"]
    frames = []
    for f in range(n):
        fr = Image.new("RGBA", (w, h))
        for b in cfg["born"]:
            age = (f - b) % n
            if age >= cfg["life"]:
                continue
            u = (age + 0.5) / cfg["life"]
            for k in range(3):                  # three lobes, the later ones higher and fainter
                uu = max(0.0, u - 0.12 * k)
                r = cfg["r"][0] + (cfg["r"][1] - cfg["r"][0]) * uu ** 0.8
                a = cfg["alpha"] * min(1.0, uu / 0.15 + 0.2) * (1 - u) ** 1.2 * (1 - 0.25 * k)
                x = sx + (k - 1) * 3 + 4 * uu
                y = sy - cfg["rise"] * uu ** 0.9 - 4 * k
                place(fr, puff_mask(r, seed + k * 13 + b), cfg["colour"], a, (x, y))
        frames.append(fr)
    return frames


# ---------------------------------------------------------------- write
def anchor_shift(cfg):
    """The animation's own shift (tiles): it puts the source point, not the frame's centre, on the position."""
    w, h = cfg["size"]
    return [round(-(cfg["src"][0] - w / 2) / PPT, 5), round(-(cfg["src"][1] - h / 2) / PPT, 5)]


def positions(key):
    return {f"{d}_position": ANCH[d][key]["shift_tiles"] for d in DIRS}


out = {"_": "Vent Pump effects (T07c): each a working_visualisation of sae-vent-pump; scale 0.5; "
            "drawn only while working; unchecked in a client", "effects": {}}
for name, cfg, frames, key, extra in (
        ("wisp-a2", WISP, wisp(), "wisp_a2",
         dict(what="A2: the boil-off wisp, a melt-lit fume rising off the head tank's gas offtake, working only",
              blend="normal (alpha)", constant_speed=True, fadeout=True, render_layer="wires (as the chemical plant's smoke)")),
        ("embers-e2", EMBERS, embers(), "embers_e2",
         dict(what="E2: embers rising off the slag in the skimmings bin, working only",
              blend="additive, draw_as_glow = true", constant_speed=True, fadeout=True, render_layer="object")),
        ("cold-breath-e4", COLD, synced_puff(COLD, 31), "cold_breath_e4",
         dict(what="E4: a breath of cold vapour off the stop valve's bonnet at each charge (born frames 1 and 13)",
              blend="normal (alpha)", constant_speed=False, fadeout=True, render_layer="object",
              south="facing south the stop valve stands behind the tower: draw this direction under the "
                    "entity (render_layer 'lower-object') or leave it out there; Liam's question")),
        ("purge-e5", PURGE, synced_puff(PURGE, 57), "purge_e5",
         dict(what="E5: a violet-grey purge puff off the float chamber's cap as each charge breaks out "
                   "(born frames 4 and 16)",
              blend="normal (alpha)", constant_speed=False, fadeout=True, render_layer="wires")),
):
    sh = sheet(frames, cfg["line"])
    sh.save(os.path.join(A.out, name + ".png"))
    additive = "additive" in extra["blend"]
    out["effects"][name] = dict(
        extra, file=name + ".png", width=cfg["size"][0], height=cfg["size"][1], frame_count=cfg["frames"],
        line_length=cfg["line"], scale=0.5, animation_speed=cfg["speed"], shift=anchor_shift(cfg),
        source_px=list(cfg["src"]), **positions(key), checks=stats(frames, additive))
    print(name, sh.size, out["effects"][name]["checks"])
out["effects"]["ground-light-e3"] = dict(
    what="E3: the melt's orange light on the ground round the tower's foot: a light, so the engine shows it only "
         "in the dark (the Core's sky is mostly dark: Liam, 2026-10-20)",
    light=dict(type="basic", intensity=0.55, size=7, color=[1.0, 0.48, 0.18]),
    note="a working_visualisation with a `light` and no animation, positioned per direction; or the drill's own "
         "light-defining fields if the coder prefers; intensity and size are proposals to judge in a client",
    **positions("ground_light_e3"))
json.dump(out, open(os.path.join(A.out, "effects.json"), "w"), indent=1)
print("wrote", A.out)
