#!/usr/bin/env python3
"""pack.glow_layer's floor -- any channel over LAYER_FLOOR is light, not its luma (T08h) -- held to its docs.

  python3 tools/blender/test/test_glow_floor.py [--out <dir>] [--baseline <git-rev>
                                                [--renders <render-out> ...]]

Nothing is rendered here. The fixture models are test_glow_crop.py's, a 2x2 plate on a 256 px
canvas with a glow pass, lit instead by a soft disc of light (radius RADIUS px, every channel falling
straight to 0 at its edge from the hue at its centre) in one of HUES: deep blue (the
Radiant Generator's dying blue, its wreck glow's hue), cyan, orange, green and grey. "The old rule" is
glow_layer with its floor judged on luma, as before T08h: this tree's glow_layer with pack.brightest
standing in as PIL's L, so nothing else differs. --baseline names a commit from before T08h (347bccc):
its contract.py and pack.py, taken out with `git show`, are run beside this tree's. --renders names
render.sh output directories to pack with both, with --baseline. Everything is written under --out
(default: a new directory under the system's temporary one, named when it starts) and kept; the
table, per fixture and per glow sheet of every --renders directory, is <out>/glow-floor.json.

Exits 0 when every case below comes out as listed, 1 naming those that do not.

  floor      pack.brightest is each pixel's brightest channel (300 random pixels); a pure hue's
             last value at luma 8 or under, the old rule's floor: blue 74, red 28, green 14, grey 8.
  deep-blue  the deep-blue fixture packed: pack.py exits 0; glow.png opaque on exactly the pixels
             whose brightest added channel is over the floor, their colour as added, and alpha 0
             everywhere else, its crop their box with the 1 px rim; that fringe -- opaque, at luma 8
             or under -- is there (pixels, and the most blue among them, printed) and every pixel of
             it was clear under the old rule.
  hues       per hue, glow_layer against the old rule: grey byte for byte the same (luma is the
             brightest channel on a grey); every other hue gains a fringe and loses nothing, the
             old sheet's pixels the same where it was opaque. Gained pixels per hue in the table.
  untouched  with --baseline: glow_frame (an animated glow, GLOW_FLOOR, already per channel) and
             paint_layer byte for byte as the baseline's on the deep-blue fixture, with and without a
             bloom; glow_layer byte for byte as the baseline's old rule (the fixtures, every hue).
  baseline   with --baseline: the baseline's pack.py on the deep-blue fixture keeps no fringe pixel.
             On the fixture and every --renders directory, every file the two pack.py's write but
             the still glows' sheets (glow passes, and a wreck's glow) byte for byte as the
             baseline's, and meta.json the same but for those sheets' size and shift; for each such
             sheet, information: whether it changed, old and new size and shift, opaque pixels,
             pixels gained and lost, the brightest channel and the luma of those gained, the share
             of the sheet's light (alpha x luma) they add, and the pixels clear (alpha 0) in both whose
             faint colour differs (a speck newly over the floor is dropped colour and all).
"""
import argparse
import json
import os
import random
import shutil
import sys
import tempfile

from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
import contract  # noqa: E402
import pack  # noqa: E402
import test_glow_crop as gc  # noqa: E402

FAILED = []
CANVAS, PPT, PLATE_RGB = gc.CANVAS, gc.PPT, gc.PLATE_RGB
CENTRE = (120, 120)                     # the disc's centre, on the plate (64-192)
RADIUS = 18
# each hue at the disc's centre: what the light adds over the plate (40, 40, 40), under 255 - 40
HUES = {
    "deep-blue": (6, 30, 110),          # the Radiant Generator's wreck glow at its brightest: (5, 24, 83)
    "cyan": (20, 140, 150),
    "orange": (200, 90, 20),            # the Vacuum Furnace's port glow
    "green": (60, 110, 80),             # the Reaction Plant's
    "grey": (120, 120, 120),
}


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(f"{case}: {detail}")


def luma(rgb):
    """PIL's L of one colour, as convert("L") rounds it."""
    r, g, b = rgb
    return (r * 19595 + g * 38470 + b * 7471 + 0x8000) >> 16


def old_rule(lit, under, mod=pack):
    """glow_layer as before T08h: the floor judged on luma (mod.brightest standing in as PIL's L)."""
    keep, mod.brightest = mod.brightest, lambda rgb: rgb.convert("L")
    try:
        return mod.glow_layer(lit, under)
    finally:
        mod.brightest = keep


# ---------------------------------------------------------------- the fixtures

def adds(hue):
    """{(x, y): (r, g, b)}: what the disc of `hue` adds over the plate, every pixel it adds anything to."""
    out = {}
    cx, cy = CENTRE
    for y in range(cy - RADIUS, cy + RADIUS + 1):
        for x in range(cx - RADIUS, cx + RADIUS + 1):
            f = 1 - ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / RADIUS
            if f > 0:
                c = tuple(round(v * f) for v in HUES[hue])
                if any(c):
                    out[(x, y)] = c
    return out


def lit(hue):
    im = gc.plate()
    px = im.load()
    for (x, y), c in adds(hue).items():
        r, g, b, _ = px[x, y]
        px[x, y] = (r + c[0], g + c[1], b + c[2], 255)
    return im


def write_fixture(rdir, hue):
    if os.path.exists(rdir):
        shutil.rmtree(rdir)
    os.makedirs(rdir)
    decl = dict(footprint=[2, 2], canvas=list(CANVAS), directions="one",
                passes=[dict(name="idle", kind="plate", sheet="base"),
                        dict(name="working", kind="glow", over="idle", sheet="glow")],
                animations=[], ports=[], rig=dict(elevation=60.0, px_per_tile=PPT))
    contract.validate(decl, rdir)
    with open(os.path.join(rdir, contract.FILE), "w") as f:
        json.dump(decl, f, indent=1)
    gc.plate().save(os.path.join(rdir, "idle.png"))
    lit(hue).save(os.path.join(rdir, "working.png"))
    return rdir


def opaque(im):
    """The (x, y) of an RGBA image's pixels with any alpha."""
    w = im.width
    return {(i % w, i // w) for i, a in enumerate(im.getchannel("A").get_flattened_data()) if a}


# ---------------------------------------------------------------- floor

def test_floor():
    print("floor")
    rnd = random.Random(8)
    px = [tuple(rnd.randrange(256) for _ in range(3)) for _ in range(300)]
    im = Image.new("RGB", (len(px), 1))
    im.putdata(px)
    check("pack.brightest: each pixel's brightest channel (300 random)",
          list(pack.brightest(im).get_flattened_data()) == [max(p) for p in px])
    for name, unit, want in (("blue", (0, 0, 1), 74), ("red", (1, 0, 0), 28), ("green", (0, 1, 0), 14),
                             ("grey", (1, 1, 1), 8)):
        last = max(v for v in range(256) if luma(tuple(v * u for u in unit)) <= pack.LAYER_FLOOR)
        check(f"pure {name}: luma {pack.LAYER_FLOOR} or under up to {last} (want {want})", last == want)


# ---------------------------------------------------------------- deep blue

def test_deep_blue(out):
    print("deep-blue")
    src = write_fixture(os.path.join(out, "deep-blue-renders"), "deep-blue")
    code, text, meta = gc.packed(src, os.path.join(out, "deep-blue-sheets"))
    check("pack.py exits 0", code == 0, text[-400:])
    if meta is None:
        return {}
    a = adds("deep-blue")
    light = {p for p, c in a.items() if max(c) > pack.LAYER_FLOOR}
    fringe = {p for p in light if luma(a[p]) <= pack.LAYER_FLOOR}
    xs, ys = [x for x, _ in light], [y for _, y in light]
    box = (min(xs) - 1, min(ys) - 1, max(xs) + 2, max(ys) + 2)
    want_size = [box[2] - box[0], box[3] - box[1]]
    g = meta["glow"]
    check(f"glow.png {want_size[0]} x {want_size[1]}: the box of every pixel over the floor, with its rim",
          list(g["size"]) == want_size, str(g))
    sheet = Image.open(os.path.join(out, "deep-blue-sheets", "glow.png")).convert("RGBA")
    on = Image.new("RGBA", CANVAS)
    on.paste(sheet, gc.box_on(g, CANVAS)[:2])
    check(f"glow.png's box where it lies: {box}", gc.box_on(g, CANVAS) == box, str(gc.box_on(g, CANVAS)))
    got = opaque(on)
    check(f"opaque on exactly the {len(light)} pixels whose brightest added channel is over "
          f"{pack.LAYER_FLOOR}", got == light, f"{len(got - light)} extra, {len(light - got)} missing")
    wrong = [p for p in light & got if on.getpixel(p) != a[p] + (255,)]
    check("their colour as added, opaque", not wrong, str(wrong[:5]))
    check("alpha 0 everywhere else (glow_layer leaves a clear pixel's faint colour as it was: preview.py "
          "clears it, T08f-3)",
          all(on.getpixel((x, y))[3] == 0 for x in range(box[0], box[2]) for y in range(box[1], box[3])
              if (x, y) not in light))
    deepest = max((a[p][2] for p in fringe), default=0)
    check(f"the fringe is there: {len(fringe)} px opaque at luma {pack.LAYER_FLOOR} or under, blue up to "
          f"{deepest}", fringe and fringe <= got)
    old = opaque(old_rule(lit("deep-blue"), gc.plate()))
    check(f"every fringe pixel was clear under the old rule (it kept {len(old)} px, now {len(got)})",
          not (fringe & old))
    return dict(size=want_size, opaque_px=len(got), fringe_px=len(fringe), fringe_blue_max=deepest,
                old_rule_opaque_px=len(old))


# ---------------------------------------------------------------- hues

def test_hues():
    print("hues")
    table = {}
    for hue in HUES:
        lit_, under = lit(hue), gc.plate()
        new, old = pack.glow_layer(lit_, under), old_rule(lit_, under)
        on_new, on_old = opaque(new), opaque(old)
        gained, lost = on_new - on_old, on_old - on_new
        same_where_old = all(new.getpixel(p) == old.getpixel(p) for p in on_old)
        table[hue] = dict(opaque_old=len(on_old), opaque_new=len(on_new), gained=len(gained), lost=len(lost),
                          gained_max_channel=max((max(new.getpixel(p)[:3]) for p in gained), default=0))
        if hue == "grey":
            check("grey: byte for byte as under the old rule", new.tobytes() == old.tobytes())
        else:
            check(f"{hue}: gains a fringe of {len(gained)} px (brightest channel up to "
                  f"{table[hue]['gained_max_channel']}), loses none, the same where the old was opaque",
                  gained and not lost and same_where_old, str(table[hue]))
    return table


# ---------------------------------------------------------------- with --baseline

def test_untouched(out, base):
    print("untouched")
    old = gc.load_module(os.path.join(base, "pack.py"), "pack_baseline")
    film = lit("deep-blue")                         # a light render on film: glow_frame reads colour x alpha
    for bloom in (None, [[4, 0.5], [12, 0.25]]):
        check(f"glow_frame byte for byte as the baseline's (bloom {bloom})",
              pack.glow_frame(film, bloom).tobytes() == old.glow_frame(film, bloom).tobytes())
    check("paint_layer byte for byte as the baseline's",
          pack.paint_layer(film, gc.plate()).tobytes() == old.paint_layer(film, gc.plate()).tobytes())
    for hue in HUES:
        check(f"{hue}: the old rule here byte for byte as the baseline's glow_layer",
              old_rule(lit(hue), gc.plate()).tobytes() == old.glow_layer(lit(hue), gc.plate()).tobytes())
    test_dir = os.path.join(out, "deep-blue-renders")
    code, _, meta = gc.packed(test_dir, os.path.join(out, "deep-blue-sheets-old"), base)
    fringe = {p for p, c in adds("deep-blue").items() if luma(c) <= pack.LAYER_FLOOR < max(c)}
    if meta is None:
        check("the baseline's pack.py packs the deep-blue fixture", False, f"exit {code}")
        return
    on = Image.new("RGBA", CANVAS)
    on.paste(Image.open(os.path.join(out, "deep-blue-sheets-old", "glow.png")).convert("RGBA"),
             gc.box_on(meta["glow"], CANVAS)[:2])
    check(f"the baseline's pack.py keeps none of the fringe ({len(fringe)} px)", not (fringe & opaque(on)))


def still_glows(decl):
    """{sheet: (rows, canvas)} of every sheet glow_layer makes: each glow pass's in every direction (one
    row, the model's canvas), and a wreck's glow (one sheet, a row per remnant_rows entry, its canvas)."""
    dirs = [d for d, _ in contract.DIRECTIONS[decl["directions"]]]
    out = {contract.named(p["sheet"], d): (1, decl["canvas"])
           for p in decl["passes"] if p["kind"] == "glow" for d in dirs}
    for p in decl["passes"]:
        if p["kind"] == "remnants" and p.get("glow"):
            out[p["glow"]["sheet"]] = (len(contract.remnant_rows(decl)), contract.canvas_of(decl, p))
    return out


def sheet_stats(old, new):
    """Two packings of one sheet, on one canvas (RGBA each): the pixels gained and lost and what they
    hold."""
    on_old, on_new = opaque(old), opaque(new)
    gained, lost = on_new - on_old, on_old - on_new
    clear = [i for i, (a, b) in enumerate(zip(old.get_flattened_data(), new.get_flattened_data()))
             if a[3] == b[3] == 0 and a[:3] != b[:3]]
    light = sum(new.getpixel(p)[3] / 255 * luma(new.getpixel(p)[:3]) for p in on_new)
    added = sum(new.getpixel(p)[3] / 255 * luma(new.getpixel(p)[:3]) for p in gained)
    return dict(opaque_old=len(on_old), opaque_new=len(on_new), gained=len(gained), lost=len(lost),
                gained_max_channel=max((max(new.getpixel(p)[:3]) for p in gained), default=0),
                gained_max_luma=max((luma(new.getpixel(p)[:3]) for p in gained), default=0),
                gained_light_pct=round(100 * added / light, 3) if light else 0.0, clear_recoloured=len(clear))


def on_canvas(path, entry, canvas, rows):
    """A packed sheet set back on its canvas, a canvas a row, one above the other."""
    im = Image.open(path).convert("RGBA")
    w, h = entry["size"]
    x0, y0 = gc.box_on(entry, canvas)[:2]
    out = Image.new("RGBA", (canvas[0], canvas[1] * rows))
    for r in range(rows):
        out.paste(im.crop((0, r * h, w, (r + 1) * h)), (x0, y0 + r * canvas[1]))
    return out


def compare(label, rdir, out, base):
    print(f"baseline: {label}")
    with open(os.path.join(rdir, contract.FILE)) as f:
        decl = json.load(f)
    mine, theirs = os.path.join(out, f"{label}-mine"), os.path.join(out, f"{label}-base")
    runs = {}
    for who, tools, o in (("this tree", TOOLS, mine), ("baseline", base, theirs)):
        code, text, meta = gc.packed(rdir, o, tools)
        runs[who] = (code, meta)
        if meta is None:
            check(f"{label}: pack.py ({who}) writes meta.json", False, f"exit {code}: {text[-300:]}")
            return {}
    check(f"{label}: pack.py exits the same ({runs['this tree'][0]}, baseline {runs['baseline'][0]})",
          runs["this tree"][0] == runs["baseline"][0])
    glows = still_glows(decl)
    names = sorted(set(os.listdir(mine)) | set(os.listdir(theirs)))
    differ = [n for n in names if n != "meta.json" and n[:-4] not in glows and
              (not os.path.isfile(os.path.join(mine, n)) or not os.path.isfile(os.path.join(theirs, n)) or
               open(os.path.join(mine, n), "rb").read() != open(os.path.join(theirs, n), "rb").read())]
    check(f"{label}: every file but the still glows' sheets ({', '.join(glows) or 'none'}) byte for byte as "
          f"the baseline's", not differ, str(differ))
    ma, mb = (json.loads(json.dumps(runs[w][1])) for w in ("this tree", "baseline"))
    rows = {}
    for g, (n, canvas) in glows.items():
        same = open(os.path.join(mine, g + ".png"), "rb").read() == open(os.path.join(theirs, g + ".png"), "rb").read()
        row = dict(changed=not same or ma[g] != mb[g], old=dict(size=mb[g]["size"], shift=mb[g]["shift"]),
                   new=dict(size=ma[g]["size"], shift=ma[g]["shift"]))
        row.update(sheet_stats(on_canvas(os.path.join(theirs, g + ".png"), mb[g], canvas, n),
                               on_canvas(os.path.join(mine, g + ".png"), ma[g], canvas, n)))
        rows[g] = row
        print(f"  {g}: {'CHANGED' if row['changed'] else 'unchanged'} {row}")
        for m in (ma, mb):
            m[g] = {k: v for k, v in m[g].items() if k not in ("size", "shift")}
    check(f"{label}: meta.json the same but for the still glows' size and shift", ma == mb,
          f"keys differing: {[k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k)]}")
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out")
    ap.add_argument("--baseline", metavar="GIT_REV")
    ap.add_argument("--renders", nargs="+", default=[], metavar="RENDER_OUT")
    a = ap.parse_args()
    if a.renders and not a.baseline:
        ap.error("--renders goes with --baseline")
    out = a.out or tempfile.mkdtemp(prefix="glow-floor-test-")
    os.makedirs(out, exist_ok=True)
    print(f"writing under {out}")
    test_floor()
    table = {"deep-blue": test_deep_blue(out), "hues": test_hues()}
    if a.baseline:
        base = gc.baseline_tools(a.baseline, out)
        test_untouched(out, base)
        table["renders"] = {"fixture": compare("fixture", os.path.join(out, "deep-blue-renders"), out, base)}
        for r in a.renders:
            label = os.path.basename(os.path.normpath(r))
            table["renders"][label] = compare(label, os.path.join(os.path.abspath(r), "renders"), out, base)
    with open(os.path.join(out, "glow-floor.json"), "w") as f:
        json.dump(table, f, indent=1)
    print(f"  the table: {os.path.join(out, 'glow-floor.json')}")
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
