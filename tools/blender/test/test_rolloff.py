#!/usr/bin/env python3
"""pack.py's highlight roll-off (roll, rolled; render.json's rolloff), and preview.py's, held to their docs.

  python3 tools/blender/test/test_rolloff.py [--out <dir>] [--baseline <git-rev>]
                                             [--renders <render-out> ...]

Nothing is rendered here. A fixture model is drawn with PIL: a 2x2 plate on a 256 px canvas whose
roof carries a sweep of clipped highlights -- every hue in 3 degree steps, at saturations from 0
to 1, at value 255 and 242 -- a row of whites, a part-transparent rim and a near-invisible one
(alpha 4) of white, over a body of (90, 96, 104); a glow pass that lights a black patch with
white, cream, orange and ice-white, so the light it adds clips; a paint animation (a hatch) with
a stripe of white, cream and ice-white highlights, under a glow animation whose light is a clipped
orange (red 255, not white, so the pack's own glow checks pass); a light pass, a white lens; and a
remnants pass, a wreck of clipped debris over its baked shadow. Every render directory is packed
twice by this tree: as it is (the roll-off on, its default) and as a copy whose render.json says
rolloff false (every other file a link to the original's). --baseline names the commit pack.py
stood at before the roll-off (f565b7d): its contract.py, pack.py and preview.py, taken out with
`git show`, pack and preview the opted-out copy too. --renders names
render.sh output directories (the test box's, a model's), packed as the fixture is; per sheet, the
pixels the roll-off changed and the most a channel moved go to <out>/rolloff.json. Everything is
written under --out (default: a new directory under the system's temporary one, named when it
starts) and kept.

"White" and "clipped" are the Vent Pump's (vp5_shoulder.py): a pixel with alpha 8 or more whose
every channel is 250 or over, and one with any channel at 255. "white()" is this pipeline's own
count, pack.white()'s (every channel 245 or over, as measure.py's white_px), which the roll-off's
top (TOP 244, Liam 2026-10-20: "Lower the top to 244") keeps every rolled pixel under.

Exits 0 when every case below comes out as listed, 1 naming those that do not.

  curve      shoulder(255) under TOP (244). rolled on every colour whose brightest channel is over
             KNEE (236), taken in order (r >= g >= b: rounding is the same for every order of the
             channels, and so is the hue's turn): its brightest channel at most TOP, rounding up
             and all, and under 245, white()'s (the brightest printed), every channel at
             most its own and within a level of the exact scale, the hue within 1 degree of the
             colour's (the worst printed), a grey still grey and a colour still a colour; on 20000
             random colours in any order, the same; on 20000 at or under KNEE, the colour itself.
             roll on random RGBA noise: alpha byte for byte, every pixel at or under KNEE byte for
             byte, every other its colour rolled, and the count and most it gives the true ones.
  contract   rolloff true and false accepted; 1, "false" and null refused naming rolloff.
             declare() with no rolloff writes no rolloff key; with rolloff=False, false.
  clipped    criterion 1. The fixture packed with the roll-off off: base.png, glow.png,
             hatch.png, hatch-glow.png and remnants.png each have clipped pixels, all but
             hatch-glow.png white ones too (the fixture is what it says). Packed with it on (exit
             0): 0 white and 0 clipped in every one, and 0 white() (pack.white); each pixel's hue
             within 1 degree of the same pixel's packed with it off, a grey still grey;
             meta.json's rolloff_px names those five sheets, each with pixels changed, and not
             the light pass's. lamp.png, the light pass, byte for byte as off, its white kept.
  knee       criterion 2. On the fixture and every --renders: the roll-off on against off, every
             file written by both; each sheet the roll-off reaches (plate, glow and paint passes',
             every animation's but a light one's, the remnants sheet) the same size, its alpha
             byte for byte, every pixel whose channels are all at or under KNEE byte for byte,
             and every other pixel's colour rolled(its colour off), each changed pixel counted and
             the most counted as rolloff_px gives them (the remnants sheet's per direction, from
             that direction's row), and 0 white() in each with it on; every other sheet (shadow,
             light) byte for byte; meta.json
             equal, every key in order, once each direction's rolloff_px is set aside, which is
             absent with it off.
  preview    preview.py on the fixture, the roll-off on and opted out. The idle panel: every
             pixel of the plate alone (opaque, no hatch or lamp over it) rolled(the plate's) on
             and the plate's own off, every opaque pixel of the hatch likewise; the lamp's pixels
             the same on and off (a light is never rolled); outside the lamp, 0 white and 0
             clipped on, and clipped pixels off. The wreck panel: every opaque pixel of the wreck
             rolled(its own) on and its own off; 0 white and 0 clipped on.
  opt-out    criterion 3, with --baseline: on the fixture and every --renders, the opted-out copy
             packed by this tree and by the baseline: every file, meta.json too, byte for byte,
             and both exit the same; and preview.py's sheet (and the fixture's GIF of the hatch)
             byte for byte as the baseline's.
"""
import argparse
import colorsys
import importlib.util
import json
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
import types

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import contract  # noqa: E402
import pack  # noqa: E402
import preview  # noqa: E402

FAILED = []
CANVAS = (256, 256)
PPT = 64
BODY = (90, 96, 104, 255)
SWEEP = (66, 70)                        # the sweep's top-left on the canvas: 120 hues across
SATS = (0.0, 0.01, 0.02, 0.04, 0.08, 0.15, 0.3, 0.5, 0.75, 1.0)
VALUES = (255, 242)
PATCH = (100, 150, 140, 170)            # the black the glow pass lights: x0, y0, x1, y1
LIGHTS = ((255, 255, 255), (255, 236, 200), (255, 140, 40), (240, 250, 255))
HATCH = (156, 150, 176, 170)            # the paint animation's patch, the glow animation's light on it
HATCH_RGB = (30, 30, 30, 255)
HATCH_LIGHT = ((255, 150, 30), (255, 110, 0))     # its two frames
WHITE = 245                             # pack.white()'s threshold, and measure.py's white_px: every channel
STRIPE = (150, 175)                     # the hatch's highlights, a row of each, left of and under its glow
STRIPE_RGB = ((255, 255, 255), (255, 200, 90), (250, 252, 255))
LAMP = (70, 150, 90, 165)               # the light pass's lens: white over a warm white
WRECK = (100, 100, 140, 120)            # the wreck's debris, its shadow as tall again under it
ROLLED_KINDS = ("plate", "glow", "paint")   # the passes whose sheets the roll-off reaches (and every animation
#                                             but a light one, and the remnants sheet)


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(f"{case}: {detail}")


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def packed(src, out, tools=TOOLS):
    """pack.py (tools') src -> out: its exit code, output and meta.json (None if it wrote none)."""
    if os.path.exists(out):
        shutil.rmtree(out)
    code, text = run([sys.executable, os.path.join(tools, "pack.py"), src, out])
    meta = os.path.join(out, "meta.json")
    return code, text, (json.load(open(meta)) if os.path.isfile(meta) else None)


def load_decl(rdir):
    with open(os.path.join(rdir, contract.FILE)) as f:
        return json.load(f)


def dirs_of(decl):
    return [d for d, _ in contract.DIRECTIONS[decl["directions"]]]


def checks_of(meta, d):
    return meta["checks"][d] if d else meta["checks"]


def opted_out(src, dst):
    """A copy of a render directory whose render.json says rolloff false, every other file a link
    to the original's (renders are large; pack.py only reads them)."""
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    for f in os.listdir(src):
        if f != contract.FILE and os.path.isfile(os.path.join(src, f)):
            os.symlink(os.path.join(os.path.abspath(src), f), os.path.join(dst, f))
    decl = load_decl(src)
    decl["rolloff"] = False
    with open(os.path.join(dst, contract.FILE), "w") as f:
        json.dump(decl, f, indent=1)
    return dst


def rolled_names(decl):
    """The per-direction sheets the roll-off reaches, by name: plate, glow and paint passes', every
    animation's but a light one's."""
    return [p["sheet"] for p in decl["passes"] if p["kind"] in ROLLED_KINDS] + \
        [a["name"] for a in decl["animations"] if a.get("kind", "paint") != "light"]


def remnants_sheet(decl):
    """The remnants pass's sheet (one for every direction), or None."""
    return next((p["sheet"] for p in decl["passes"] if p["kind"] == "remnants"), None)


def white_clipped(im):
    """The Vent Pump's counts: (white, clipped) pixels with alpha 8 or more."""
    w = c = 0
    for r, g, b, a in im.convert("RGBA").get_flattened_data():
        if a >= 8:
            w += min(r, g, b) >= 250
            c += max(r, g, b) == 255
    return w, c


# ---------------------------------------------------------------- curve

def test_curve():
    print("curve")
    check(f"shoulder(255) = {pack.shoulder(255):.2f}, under TOP {pack.TOP}", pack.shoulder(255) < pack.TOP)
    raw = pack.rolled.__wrapped__          # not cached: every colour is asked once

    def bad_of(rgb):
        out = raw(rgb)
        k = pack.shoulder(max(rgb)) / max(rgb)
        miss = pack.hue_miss(rgb, out)
        if max(out) > pack.TOP or max(out) >= WHITE:
            return miss, f"{rgb} -> {out}: over TOP, or at white()'s {WHITE}"
        if any(o > c or abs(o - c * k) >= 1 for o, c in zip(out, rgb)):
            return miss, f"{rgb} -> {out}: not within a level of the exact scale {k:.4f}, or brighter"
        if miss > 1:
            return miss, f"{rgb} -> {out}: hue turned {miss:.2f} degrees"
        return miss, None
    worst, bad, n, top = 0.0, [], 0, 0
    for m in range(pack.KNEE + 1, 256):
        for g in range(m + 1):
            for b in range(g + 1):
                miss, why = bad_of((m, g, b))
                worst, n, top = max(worst, miss), n + 1, max(top, *raw((m, g, b)))
                if why:
                    bad.append(why)
    check(f"every colour over the knee in order ({n}): the brightest rolled channel {top}, at most TOP {pack.TOP} "
          f"and under {WHITE}; within a level of the scale, hue within 1 degree (worst {worst:.3f}), grey kept grey",
          not bad and top <= pack.TOP and top < WHITE, f"{len(bad)}: {bad[:4]}")
    rnd = random.Random(20261020)
    bad = []
    for _ in range(20000):
        rgb = [rnd.randint(0, 255) for _ in range(3)]
        rgb[rnd.randrange(3)] = rnd.randint(pack.KNEE + 1, 255)
        why = bad_of(tuple(rgb))[1]
        if why:
            bad.append(why)
    check("20000 random colours over the knee, in any order: the same", not bad, str(bad[:4]))
    low = [tuple(rnd.randint(0, pack.KNEE) for _ in range(3)) for _ in range(20000)]
    check("20000 random colours at or under the knee: the colour itself", all(raw(c) == c for c in low))

    noise = Image.new("RGBA", (97, 61))
    px = [tuple(rnd.choice((rnd.randint(0, 255), rnd.randint(200, 255), 255)) for _ in range(4))
          for _ in range(97 * 61)]
    noise.putdata(px)
    out, count, most = pack.roll(noise)
    got = list(out.get_flattened_data())
    want_n = want_most = 0
    bad = []
    for i, (a, b) in enumerate(zip(px, got)):
        if max(a[:3]) <= pack.KNEE:
            ok = a == b
        else:
            ok = b == (*raw(a[:3]), a[3])
            if b != a:
                want_n += 1
                want_most = max(want_most, *(x - y for x, y in zip(a, b)))
        if not ok:
            bad.append((i, a, b))
    check("roll on noise: alpha and every pixel at or under the knee byte for byte, the rest rolled",
          not bad and out.getchannel("A").tobytes() == noise.getchannel("A").tobytes(), str(bad[:4]))
    check(f"roll on noise: {count} px changed, the most {most}, as counted", (count, most) == (want_n, want_most),
          f"counted {want_n}, {want_most}")


# ---------------------------------------------------------------- contract

def test_contract(rdir):
    print("contract")
    decl0 = load_decl(rdir)
    for label, v, ok in (("true", True, True), ("false", False, True), ("1", 1, False), ('"false"', "false", False),
                         ("null", None, False)):
        d = dict(decl0, rolloff=v)
        try:
            contract.validate(d, "test")
            check(f"rolloff {label} {'accepted' if ok else 'refused'}", ok, "accepted")
        except contract.ContractError as e:
            check(f"rolloff {label} {'accepted' if ok else 'refused, naming rolloff'}",
                  not ok and ": rolloff:" in str(e), str(e))
    sys.modules.setdefault("rig", types.SimpleNamespace(ELEVATION=math.radians(decl0["rig"]["elevation"]),
                                                         PX_PER_TILE=decl0["rig"]["px_per_tile"]))
    given = {k: decl0[k] for k in ("footprint", "canvas", "directions", "passes", "animations", "ports")}
    with tempfile.TemporaryDirectory() as tmp:
        plain = contract.declare(os.path.join(tmp, "plain"), **given)
        off = contract.declare(os.path.join(tmp, "off"), rolloff=False, **given)
        with open(os.path.join(tmp, "off", contract.FILE)) as f:
            written = json.load(f)
    check("declare() without rolloff: no rolloff key", "rolloff" not in plain, str(sorted(plain)))
    check("declare(rolloff=False): render.json says false", written.get("rolloff") is False and
          off.get("rolloff") is False, str(written.get("rolloff")))


# ---------------------------------------------------------------- the fixture

def plate():
    im = Image.new("RGBA", CANVAS)
    d = ImageDraw.Draw(im)
    d.rectangle((64, 64, 191, 191), fill=BODY)
    x0, y0 = SWEEP
    for row, (s, v) in enumerate((s, v) for v in VALUES for s in SATS):
        for i in range(120):
            r, g, b = colorsys.hsv_to_rgb(i * 3 / 360, s, 1.0)
            im.putpixel((x0 + i, y0 + row), (round(r * v), round(g * v), round(b * v), 255))
    y = y0 + len(SATS) * len(VALUES)
    for i, c in enumerate(((255, 255, 255), (252, 251, 250), (250, 250, 250), (245, 247, 255), (237, 237, 237))):
        d.line((x0, y + i, x0 + 119, y + i), fill=c + (255,))
    d.line((64, 64, 64, 191), fill=(255, 255, 255, 128))        # a part-transparent rim, white
    d.line((191, 64, 191, 191), fill=(255, 250, 240, 4))        # a near-invisible one: not counted
    d.rectangle((PATCH[0], PATCH[1], PATCH[2] - 1, PATCH[3] - 1), fill=(0, 0, 0, 255))
    return im


def lit():
    im = plate()
    w = (PATCH[2] - PATCH[0]) // len(LIGHTS)
    d = ImageDraw.Draw(im)
    for i, c in enumerate(LIGHTS):
        d.rectangle((PATCH[0] + i * w, PATCH[1], PATCH[0] + (i + 1) * w - 1, PATCH[3] - 1), fill=c + (255,))
    return im


def hatch():
    im = Image.new("RGBA", CANVAS)
    d = ImageDraw.Draw(im)
    d.rectangle((HATCH[0], HATCH[1], HATCH[2] - 1, HATCH[3] - 1), fill=HATCH_RGB)
    for i, c in enumerate(STRIPE_RGB):
        d.line((STRIPE[0], STRIPE[1] + i, STRIPE[0] + 29, STRIPE[1] + i), fill=c + (255,))
    return im


def lamp():
    im = Image.new("RGBA", CANVAS)
    d = ImageDraw.Draw(im)
    mid = (LAMP[1] + LAMP[3]) // 2
    d.rectangle((LAMP[0], LAMP[1], LAMP[2] - 1, mid - 1), fill=(255, 255, 255, 255))
    d.rectangle((LAMP[0], mid, LAMP[2] - 1, LAMP[3] - 1), fill=(250, 240, 230, 255))
    return im


def wreck():
    im = Image.new("RGBA", CANVAS)
    w = WRECK[2] - WRECK[0]
    for y in range(WRECK[1], WRECK[3]):
        for i in range(w):
            r, g, b = colorsys.hsv_to_rgb(i / w, (y - WRECK[1]) / (WRECK[3] - WRECK[1]), 1.0)
            im.putpixel((WRECK[0] + i, y), (round(255 * r), round(255 * g), round(255 * b), 255))
    ImageDraw.Draw(im).rectangle((WRECK[0], WRECK[3], WRECK[2] - 1, 2 * WRECK[3] - WRECK[1] - 1), fill=(0, 0, 0, 100))
    return im


def write_fixture(rdir):
    if os.path.exists(rdir):
        shutil.rmtree(rdir)
    os.makedirs(rdir)
    decl = dict(footprint=[2, 2], canvas=list(CANVAS), directions="one",
                passes=[dict(name="idle", kind="plate", sheet="base"),
                        dict(name="still", kind="still"),
                        dict(name="working", kind="glow", over="idle", sheet="glow"),
                        dict(name="lamp", kind="light", sheet="lamp"),
                        dict(name="wreck", kind="remnants", sheet="remnants")],
                animations=[dict(name="hatch", frames=2, motion="flow"),
                            dict(name="hatch-glow", frames=2, motion="flow", kind="glow", over="hatch")],
                ports=[], rig=dict(elevation=60.0, px_per_tile=PPT))
    contract.validate(decl, rdir)
    with open(os.path.join(rdir, contract.FILE), "w") as f:
        json.dump(decl, f, indent=1)
    plate().save(os.path.join(rdir, "idle.png"))
    still = plate()
    still.alpha_composite(hatch())
    still.save(os.path.join(rdir, "still.png"))
    lit().save(os.path.join(rdir, "working.png"))
    lamp().save(os.path.join(rdir, "lamp.png"))
    wreck().save(os.path.join(rdir, "wreck.png"))
    for f, c in enumerate(HATCH_LIGHT):
        hatch().save(os.path.join(rdir, contract.frame("hatch", f) + ".png"))
        film = Image.new("RGBA", CANVAS)
        ImageDraw.Draw(film).rectangle((HATCH[0], HATCH[1], HATCH[2] - 1, HATCH[3] - 1), fill=c + (255,))
        film.save(os.path.join(rdir, contract.frame("hatch-glow", f) + ".png"))
    return rdir


def pack_both(label, rdir, out):
    """rdir packed by this tree with the roll-off on (as declared) and off (an opted-out copy):
    (on dir, off dir, on meta, off meta, opted-out render dir), the metas None on a failed pack."""
    off_src = opted_out(rdir, os.path.join(out, f"{label}-renders-off"))
    on, off = os.path.join(out, f"{label}-on"), os.path.join(out, f"{label}-off")
    code_on, text_on, meta_on = packed(rdir, on)
    code_off, text_off, meta_off = packed(off_src, off)
    check(f"{label}: pack.py exits the same on and off ({code_on}, {code_off})", code_on == code_off,
          text_on[-300:] + text_off[-300:])
    return on, off, meta_on, meta_off, off_src


# ---------------------------------------------------------------- clipped (criterion 1)

def test_clipped(out):
    print("clipped")
    src = write_fixture(os.path.join(out, "fixture-renders"))
    on, off, meta_on, meta_off, _ = pack_both("fixture", src, out)
    check("fixture: pack.py exits 0, roll-off on", meta_on is not None and os.path.isfile(os.path.join(on, "base.png")))
    if meta_on is None or meta_off is None:
        return src
    for sheet, need_white in (("base", True), ("glow", True), ("hatch", True), ("hatch-glow", False),
                              ("remnants", True)):
        a = Image.open(os.path.join(off, sheet + ".png")).convert("RGBA")
        b = Image.open(os.path.join(on, sheet + ".png")).convert("RGBA")
        w0, c0 = white_clipped(a)
        w1, c1 = white_clipped(b)
        check(f"{sheet}.png off: {w0} white, {c0} clipped (the fixture clips)", c0 > 0 and (w0 > 0 or not need_white))
        check(f"{sheet}.png on: 0 white, 0 clipped ({w1}, {c1})", (w1, c1) == (0, 0))
        n0, n1 = (pack.white(im).histogram()[255] for im in (a, b))
        check(f"{sheet}.png on: 0 white() (every channel {WHITE} or over; {n0} off)", n1 == 0)
        misses = [pack.hue_miss(p[:3], q[:3]) for p, q in zip(a.get_flattened_data(), b.get_flattened_data())]
        check(f"{sheet}.png on: every pixel's hue within 1 degree of its own off (worst {max(misses):.3f}), a grey "
              f"still grey", a.size == b.size and max(misses) <= 1, f"{sum(1 for m in misses if m > 1)} px over")
    rolls = meta_on["checks"].get("rolloff_px", [{}])[0]
    want = ["base", "glow", "hatch", "hatch-glow", "remnants"]
    check(f"meta.json's rolloff_px names {', '.join(want)}, each with pixels changed, and not lamp ({rolls})",
          sorted(rolls) == want and all(v["px"] > 0 for v in rolls.values()))
    a, b = (open(os.path.join(o, "lamp.png"), "rb").read() for o in (off, on))
    w = white_clipped(Image.open(os.path.join(on, "lamp.png")))[0]
    check(f"lamp.png, the light pass: byte for byte as off, its white kept ({w} white px)", a == b and w > 0)
    return src


# ---------------------------------------------------------------- knee (criterion 2)

def compare_on_off(label, on, off, meta_on, meta_off, decl):
    """The roll-off on against off on one render directory: the sheets it reaches changed only past
    the knee, and only by rolled; every other file byte for byte; meta.json but for rolloff_px.
    Returns {sheet: {px, most}} as counted here."""
    names = sorted(set(os.listdir(on)) | set(os.listdir(off)))
    check(f"{label}: every file written both on and off ({len(names)})", set(os.listdir(on)) == set(os.listdir(off)),
          str(set(os.listdir(on)) ^ set(os.listdir(off))))
    per = {contract.named(n, d): (n, d) for n in rolled_names(decl) for d in dirs_of(decl)}
    wrecked = remnants_sheet(decl)
    reach = set(per) | ({wrecked} if wrecked else set())
    table, bad, other, rows = {}, [], [], {}
    for n in names:
        if n == "meta.json" or not n.endswith(".png") or not os.path.isfile(os.path.join(on, n)) \
                or not os.path.isfile(os.path.join(off, n)):
            continue
        if n[:-4] not in reach:
            if open(os.path.join(on, n), "rb").read() != open(os.path.join(off, n), "rb").read():
                other.append(n)
            continue
        a = Image.open(os.path.join(off, n)).convert("RGBA")
        b = Image.open(os.path.join(on, n)).convert("RGBA")
        if a.size != b.size or a.getchannel("A").tobytes() != b.getchannel("A").tobytes():
            bad.append(f"{n}: size or alpha differs")
            continue
        table[n[:-4]] = counted_roll(n, a, b, bad)
        table[n[:-4]]["white_off"] = pack.white(a).histogram()[255]
        if pack.white(b).histogram()[255]:
            bad.append(f"{n}: {pack.white(b).histogram()[255]} px white() with the roll-off on")
        if n[:-4] == wrecked and meta_on is not None:
            h = meta_on[wrecked]["size"][1]
            for i, d in enumerate(meta_on[wrecked]["rows"]):     # each direction's render, in its first row
                if d not in rows:
                    rows[d] = counted_roll(n, *(im.crop((0, i * h, a.width, (i + 1) * h)) for im in (a, b)), [])
    check(f"{label}: the sheets the roll-off reaches ({len(table)}) changed only past the knee, each pixel rolled, "
          f"alpha and size kept, 0 white() in each", not bad, f"{len(bad)}: {bad[:4]}")
    check(f"{label}: every other sheet byte for byte ({len([n for n in names if n.endswith('.png')]) - len(table)})",
          not other, str(other))
    if meta_on is None or meta_off is None:
        check(f"{label}: meta.json written on and off", False)
        return table
    on_c = {d: checks_of(meta_on, d).pop("rolloff_px", None) for d in dirs_of(decl)}
    off_c = {d: checks_of(meta_off, d).pop("rolloff_px", None) for d in dirs_of(decl)}
    check(f"{label}: no rolloff_px with it off", all(v is None for v in off_c.values()), str(off_c))
    counted = {d: on_c[d][0] if on_c[d] else None for d in dirs_of(decl)}
    want = {d: {s: dict(px=table[s]["px"], most=table[s]["most"]) for s, (_, sd) in per.items()
                if sd == d and s in table} for d in dirs_of(decl)}
    for d, v in rows.items():
        want[d][wrecked] = dict(px=v["px"], most=v["most"])
    # rolloff_px lists its sheets in the order pack.py rolls them; compared as sets of entries
    counted = {d: dict(sorted(c.items())) if c is not None else None for d, c in counted.items()}
    want = {d: dict(sorted(c.items())) for d, c in want.items()}
    check(f"{label}: rolloff_px in each direction, the sheets and numbers counted here", counted == want,
          f"meta {counted}, counted {want}")
    check(f"{label}: meta.json equal on and off, every key in order, once rolloff_px is set aside",
          json.dumps(meta_on) == json.dumps(meta_off))
    return table


def counted_roll(n, a, b, bad):
    """One sheet (a off, b on): its pixels over the knee, those the roll-off changed and the most a
    channel moved; every pixel that is not as the roll-off makes it goes into bad."""
    changed = most = over = 0
    for p, q in zip(a.get_flattened_data(), b.get_flattened_data()):
        if max(p[:3]) <= pack.KNEE:
            if p != q:
                bad.append(f"{n}: {p} at or under the knee became {q}")
            continue
        over += 1
        if q[:3] != pack.rolled(p[:3]):
            bad.append(f"{n}: {p} became {q}, not {pack.rolled(p[:3])}")
        if p != q:
            changed += 1
            most = max(most, *(x - y for x, y in zip(p, q)))
    return dict(over_knee=over, px=changed, most=most)


def test_knee(out, fixture, renders):
    print("knee")
    table = {}
    for label, rdir in [("fixture", fixture)] + [(os.path.basename(os.path.normpath(r)), os.path.join(r, "renders"))
                                                  for r in renders]:
        on, off, meta_on, meta_off, _ = pack_both(label, rdir, out)
        table[label] = compare_on_off(label, on, off, meta_on, meta_off, load_decl(rdir))
        for s, v in table[label].items():
            print(f"    {label} {s}: {v['over_knee']} px over the knee, {v['px']} changed, the most by {v['most']}; "
                  f"{v['white_off']} white() off, 0 on")
    with open(os.path.join(out, "rolloff.json"), "w") as f:
        json.dump(table, f, indent=1)
    print(f"  the table: {os.path.join(out, 'rolloff.json')}")


# ---------------------------------------------------------------- preview

def test_preview(out, fixture):
    print("preview")
    off_src = os.path.join(out, "fixture-renders-off")
    on, off = preview.Model(fixture), preview.Model(off_src)
    src = {n: Image.open(os.path.join(fixture, n + ".png")).convert("RGBA") for n in ("idle", "hatch-00", "wreck")}
    x0, y0, x1, y1 = lamp().getchannel("A").getbbox()
    lamp_box = (x0 - 1, y0 - 1, x1 + 1, y1 + 1)        # light_layer's crop: its lens and the 1 px rim

    def in_lamp(x, y):
        return lamp_box[0] <= x < lamp_box[2] and lamp_box[1] <= y < lamp_box[3]
    p_on, p_off = on.panel("", False), off.panel("", False)
    w = p_on.width
    bad = {"plate": [], "hatch": [], "lamp": []}
    seen = {k: 0 for k in bad}
    for i, (a, b, pl, ha) in enumerate(zip(p_on.get_flattened_data(), p_off.get_flattened_data(),
                                           src["idle"].get_flattened_data(), src["hatch-00"].get_flattened_data())):
        x, y = i % w, i // w
        if in_lamp(x, y):
            seen["lamp"] += 1
            if a != b:
                bad["lamp"].append((x, y, a, b))
        elif ha[3] == 255:
            seen["hatch"] += 1
            if a != (*pack.rolled(ha[:3]), 255) or b != ha:
                bad["hatch"].append((x, y, a, b, ha))
        elif pl[3] == 255 and ha[3] == 0:
            seen["plate"] += 1
            if a != (*pack.rolled(pl[:3]), 255) or b != pl:
                bad["plate"].append((x, y, a, b, pl))
    for k, why in (("plate", "rolled(the plate's) on, the plate's own off"),
                   ("hatch", "rolled(the hatch's) on, the hatch's own off"),
                   ("lamp", "the same on and off: a light is never rolled")):
        check(f"idle panel, the {k}'s {seen[k]} px: {why}", seen[k] > 0 and not bad[k], str(bad[k][:3]))
    outside = [Image.new("RGBA", p_on.size), Image.new("RGBA", p_off.size)]
    for im, o in zip((p_on, p_off), outside):
        o.paste(im)
        o.paste((0, 0, 0, 255), lamp_box)
    (w_on, c_on), (_, c_off) = white_clipped(outside[0]), white_clipped(outside[1])
    check(f"idle panel outside the lamp: 0 white and 0 clipped on ({w_on}, {c_on}); clipped off ({c_off})",
          (w_on, c_on) == (0, 0) and c_off > 0)
    k_on, k_off = on.wreck(""), off.wreck("")
    bad = [(i, a, b, s) for i, (a, b, s) in enumerate(zip(k_on.get_flattened_data(), k_off.get_flattened_data(),
                                                           src["wreck"].get_flattened_data()))
           if s[3] == 255 and (a != (*pack.rolled(s[:3]), 255) or b != s)]
    n = src["wreck"].getchannel("A").point(lambda v: 255 if v == 255 else 0).histogram()[255]
    check(f"wreck panel, its {n} opaque px: rolled(the wreck's) on, its own off", n > 0 and not bad, str(bad[:3]))
    check(f"wreck panel on: 0 white and 0 clipped {white_clipped(k_on)}", white_clipped(k_on) == (0, 0))


# ---------------------------------------------------------------- opt-out (criterion 3)

def baseline_tools(rev, out):
    """contract.py, pack.py and preview.py as they stood at rev, in a directory of their own."""
    d = os.path.join(out, f"baseline-{rev}")
    os.makedirs(d, exist_ok=True)
    top = subprocess.run(["git", "-C", TOOLS, "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                         check=True).stdout.strip()
    rel = os.path.relpath(TOOLS, top)
    for f in ("contract.py", "pack.py", "preview.py"):
        body = subprocess.run(["git", "-C", top, "show", f"{rev}:{rel}/{f}"], capture_output=True, check=True).stdout
        with open(os.path.join(d, f), "wb") as fh:
            fh.write(body)
    return d


def load_module(path, name):
    sys.path.insert(0, os.path.dirname(path))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path.pop(0)


def test_opt_out(out, base, fixture, renders):
    print("opt-out")
    old = load_module(os.path.join(base, "pack.py"), "pack_baseline")
    check("the baseline has no roll-off (it is from before it)", not hasattr(old, "roll"))
    for label, rdir in [("fixture", fixture)] + [(os.path.basename(os.path.normpath(r)), os.path.join(r, "renders"))
                                                  for r in renders]:
        src = os.path.join(out, f"{label}-renders-off")       # pack_both's opted-out copy
        if not os.path.isdir(src):
            src = opted_out(rdir, src)
        mine, theirs = os.path.join(out, f"{label}-off"), os.path.join(out, f"{label}-old")
        code_m, _, _ = packed(src, mine)
        code_b, text_b, _ = packed(src, theirs, base)
        fm, fb = sorted(os.listdir(mine)), sorted(os.listdir(theirs))
        differ = [f for f in fm if f in fb and open(os.path.join(mine, f), "rb").read() !=
                  open(os.path.join(theirs, f), "rb").read()]
        check(f"{label}: opted out, every file byte for byte as the baseline's, meta.json too ({len(fm)} files; "
              f"baseline exit {code_b})", fm == fb and not differ and fm and code_b == code_m,
              f"files {sorted(set(fm) ^ set(fb))}, differ {differ}, exits {code_m} and {code_b}: {text_b[-300:]}")
        runs = [("preview.png", [])] + ([("hatch.gif", ["--gif", "hatch", "--speed", "0.25"])] if label == "fixture"
                                        else [])
        for name, extra in runs:
            got, why = [], ""
            for tools, o in ((TOOLS, mine + "-preview"), (base, theirs + "-preview")):
                os.makedirs(o, exist_ok=True)
                code, text = run([sys.executable, os.path.join(tools, "preview.py"), src, os.path.join(o, name),
                                  *extra])
                got.append(open(os.path.join(o, name), "rb").read() if code == 0 else None)
                why += "" if code == 0 else f"{tools}: exit {code}: {text[-200:]} "
            check(f"{label}: opted out, preview.py's {name} byte for byte as the baseline's",
                  got[0] is not None and got[0] == got[1], why)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out")
    ap.add_argument("--baseline", metavar="GIT_REV")
    ap.add_argument("--renders", nargs="+", default=[], metavar="RENDER_OUT")
    a = ap.parse_args()
    out = os.path.abspath(a.out or tempfile.mkdtemp(prefix="rolloff-test-"))
    os.makedirs(out, exist_ok=True)
    print(f"writing under {out}")
    renders = [os.path.abspath(r) for r in a.renders]
    test_curve()
    fixture = test_clipped(out)
    test_contract(fixture)
    test_knee(out, fixture, renders)
    test_preview(out, fixture)
    if a.baseline:
        test_opt_out(out, baseline_tools(a.baseline, out), fixture, renders)
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
