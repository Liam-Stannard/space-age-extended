#!/usr/bin/env python3
"""A model's declared night-only lights (T08g: render.json's `lights`, contract.py; pack.py's
meta.json "lights"; preview.py's night rows) held to their docs.

  python3 tools/blender/test/test_night_lights.py [--out <dir>] [--baseline <git-rev>
                                                  [--renders <render-out> ...]]

Nothing is rendered here. Two fixtures, drawn with PIL, each written twice, with and without
lights. The building is test_preview_night.py's (one direction, a 2x2 plate on a 192 px canvas
with a layer of every kind preview.py draws), its lights: "lens", a draw_as_light layer of
__core__/graphics/light-medium.png at scale 0.3 tinted blue, working only, east of north over
the plate, reaching past the canvas's top; "foot", a definition (intensity 0.55, size 0.5,
orange) on the glow pass, drawn idle too. The turning one is test_remnants_glow.py's (four
directions, a wreck with its glow), its light "lamp", a layer at a shift of its own in each
direction. The pictures are read from the game's data (<FACTORIO_ROOT>/data, tools/paths.conf, as
preview.py).
Everything is written under --out (default: a new directory under the system's temporary one,
named when it starts) and kept: night-lights.png is the sheet to look at.

Exits 0 when every case below comes out as listed, 1 naming those that do not.

  contract  both fixtures validate, and a model of four directions takes one shift for all;
            refused, each naming its field: an unknown kind, a field missing, a field of the
            other kind, intensity 0 and 1.5, size 0, a color of two numbers or above 1, a filename
            not __<mod>__/<path>.png, width 0, scale 0, a tint of five numbers, a shift per
            direction missing one or on a model of one direction, a name twice, working "yes", a
            sheet named "lights" (taken without lights).
  pack      meta.json "lights" as pack.py's docstring lists it, after every sheet and before
            "checks" (the building's: shift [x, y]; the turning one's: {direction: [x, y]} for
            each, and a model taking one shift for all has it written out for each); every sheet
            byte for byte as without lights, and meta.json as without them but for "lights".
  preview   by day, every panel and the --day-only sheet byte for byte as without lights, and a
            --gif too; the wreck's panels, day and night, too; at night, past every light's reach
            (its picture's box, a px round it) each panel byte for byte as without lights, and
            inside it the ground and the plate brighter; at each light's centre, on the plate,
            each channel the plate's (90) times min(1, 0.15 + its colour times light-medium's
            centre, premultiplied), within 2, and a quarter and a half of the foot's radius (its
            size) east of its centre the same with light-medium's px there, within 3 (so size is
            read as the radius, the picture premultiplied); the lens, working only, not in the
            idle panel (there as without lights); the glow pass adding at night under the foot
            what it adds by day, the lamp and the beacon (in the lens's reach) as without lights;
            the sheet's night row lighting the ground past the canvas (the lens over the top), its
            day row not, and its working night place the panel under lights the size of the
            panel, placed and gridded as the sheet places it; the turning fixture lit at each
            direction's own shift and as without lights at the others'. FACTORIO_ROOT wrong (a copy
            of tools/blender whose paths.conf names no install): the sheet refused naming
            FACTORIO_ROOT, --day-only drawn; a layer's width and height not
            its picture's: refused, naming them.
  identity  with --baseline. On every --renders directory (render.sh output: its renders/), none
            declaring lights: pack.py's outputs, every file, and preview.py's sheet (no flag,
            and --day-only) and a GIF of its first animation, byte for byte as the baseline's.
"""
import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
import contract  # noqa: E402
import preview  # noqa: E402
import paths  # noqa: E402 (tools/, on the path preview put it on)
import test_preview_night as pn  # noqa: E402
import test_remnants_glow as rg  # noqa: E402

FAILED = []
K = preview.NIGHT
LM = "__core__/graphics/light-medium.png"
PPT = 64
LENS = dict(name="lens", kind="layer", filename=LM, width=300, height=300, scale=0.3, tint=[0.29, 0.53, 1.0],
            shift=[0.84375, -0.5625], working=True)     # 180 px across, centred (150, 60): x 60 to 240, y -30 to 150
FOOT = dict(name="foot", kind="definition", intensity=0.55, size=0.5, color=[1.0, 0.48, 0.18],
            shift=[-0.71875, -0.71875])               # 64 px across, centred (50, 50): on the glow pass
TURN_AT = {"north": [0.5, -0.5], "east": [0.5, 0.5], "south": [-0.5, 0.5], "west": [-0.5, -0.5]}
TURN = dict(name="lamp", kind="layer", filename=LM, width=300, height=300, scale=0.12, tint=[0.2, 1.0, 0.4],
            shift=TURN_AT)                            # 72 px across


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(f"{case}: {detail}")


def run(cmd, env=None):
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return p.returncode, p.stdout + p.stderr


def same_bytes(a, b):
    with open(a, "rb") as fa, open(b, "rb") as fb:
        return fa.read() == fb.read()


def with_lights(src, dst, lights):
    """A copy of the fixture src as dst, its render.json declaring lights."""
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    decl = rg.load_decl(dst)
    decl["lights"] = lights
    contract.validate(decl, dst)
    rg.save_decl(dst, decl)
    return dst


def centre_of(li, d, canvas):
    s = li["shift"][d] if isinstance(li["shift"], dict) else li["shift"]
    return canvas[0] / 2 + s[0] * PPT, canvas[1] / 2 + s[1] * PPT


def across(li):
    """A light's picture's width in px on the panel."""
    return 2 * li["size"] * PPT if li["kind"] == "definition" else li["width"] * li["scale"] * PPT / 32


def reach(li, d, canvas, x, y):
    """Whether (x, y) is within a light's picture's box, a px round it."""
    cx, cy = centre_of(li, d, canvas)
    r = across(li) / 2 + 1
    return abs(x - cx) <= r and abs(y - cy) <= r


def differ(a, b):
    """The px where two same-sized RGBA images differ, as a set of (x, y)."""
    diff = ImageChops.difference(a, b)
    w = a.width
    return {(i % w, i // w) for i, p in enumerate(diff.get_flattened_data()) if any(p)}


def centre_value(f=0.0):
    """light-medium's px a share f of its radius east of its centre, as the engine loads it
    (premultiplied), 0 to 1: at its centre when f is 0."""
    im = Image.open(os.path.join(paths.factorio_data(), "core", "graphics", "light-medium.png")).convert("RGBA")
    r, _, _, a = im.getpixel((im.width // 2 + round(f * im.width / 2), im.height // 2))
    return r * a / 65025


# ---------------------------------------------------------------- contract

def test_contract(bdir, tdir):
    print("contract")
    for label, d in (("the building", bdir), ("the turning fixture", tdir)):
        try:
            contract.load(d)
            ok, why = True, ""
        except contract.ContractError as e:
            ok, why = False, str(e)
        check(f"{label} with lights validates", ok, why)
    base = rg.load_decl(tdir)
    one_for_all = copy.deepcopy(base)
    one_for_all["lights"][0]["shift"] = [0.25, 0.25]
    try:
        contract.validate(one_for_all, "x")
        check("a model of four directions takes one shift for all", True)
    except contract.ContractError as e:
        check("a model of four directions takes one shift for all", False, str(e))
    bdecl = rg.load_decl(bdir)
    nolights = {k: v for k, v in bdecl.items() if k != "lights"}

    def light(**edit):
        """FOOT edited: a field given None is left out."""
        li = dict(FOOT)
        for k, v in edit.items():
            if v is None:
                li.pop(k)
            else:
                li[k] = v
        return li

    cases = [
        ("an unknown kind", "lights[0].kind", bdecl, [light(kind="lamp")]),
        ("a definition without size", "lights[0].size", bdecl, [light(size=None)]),
        ("a definition with a layer's scale", "lights[0].scale", bdecl, [light(scale=1)]),
        ("intensity 0", "lights[0].intensity", bdecl, [light(intensity=0)]),
        ("intensity 1.5", "lights[0].intensity", bdecl, [light(intensity=1.5)]),
        ("size 0", "lights[0].size", bdecl, [light(size=0)]),
        ("a color of two numbers", "lights[0].color", bdecl, [light(color=[1, 0])]),
        ("a color above 1", "lights[0].color", bdecl, [light(color=[1, 0, 255])]),
        ("a filename not __<mod>__/<path>.png", "lights[0].filename", bdecl, [dict(LENS, filename="light-medium.png")]),
        ("width 0", "lights[0].width", bdecl, [dict(LENS, width=0)]),
        ("scale 0", "lights[0].scale", bdecl, [dict(LENS, scale=0)]),
        ("a tint of five numbers", "lights[0].tint", bdecl, [dict(LENS, tint=[1, 1, 1, 1, 1])]),
        ("a shift per direction missing one", "lights[0].shift", base,
         [dict(TURN, shift={k: v for k, v in TURN_AT.items() if k != "west"})]),
        ("a shift per direction on a model of one", "lights[0].shift", bdecl, [dict(FOOT, shift={"": [0, 0]})]),
        ("a name twice", "lights[1].name", bdecl, [FOOT, dict(LENS, name="foot")]),
        ("working \"yes\"", "lights[0].working", bdecl, [light(working="yes")]),
        ("not a list", "lights", bdecl, {"foot": FOOT}),
    ]
    for label, field, decl, lights in cases:
        bad = copy.deepcopy(decl)
        bad["lights"] = lights
        try:
            contract.validate(bad, "x")
            check(f"refused: {label}", False, "taken")
        except contract.ContractError as e:
            check(f"refused: {label}, naming {field}", f"x: {field}:" in str(e), str(e))
    named = copy.deepcopy(nolights)
    named["passes"][0]["sheet"] = "lights"
    try:
        contract.validate(named, "x")
        taken = True
    except contract.ContractError:
        taken = False
    named["lights"] = [FOOT]
    try:
        contract.validate(named, "x")
        check("refused: a sheet named \"lights\" with lights declared (taken without)", False, "taken")
    except contract.ContractError as e:
        check("refused: a sheet named \"lights\" with lights declared (taken without)",
              taken and "x: lights:" in str(e), str(e))


# ---------------------------------------------------------------- pack

def test_pack(out, pairs):
    print("pack")
    for label, plain, lit, want in pairs:
        po, pl = os.path.join(out, f"pack-{label}-plain"), os.path.join(out, f"pack-{label}-lights")
        for src, o in ((plain, po), (lit, pl)):
            if os.path.exists(o):
                shutil.rmtree(o)
            code, text = run([sys.executable, os.path.join(TOOLS, "pack.py"), src, o])
            check(f"{label}: pack.py exits 0 ({os.path.basename(src)})", code == 0, text[-300:])
        mp, ml = (json.load(open(os.path.join(o, "meta.json"))) for o in (po, pl))
        keys = list(ml)
        check(f"{label}: meta.json \"lights\" after every sheet, before \"checks\"",
              keys[-2:] == [contract.LIGHTS_KEY, "checks"] and contract.LIGHTS_KEY not in mp, f"{keys}")
        check(f"{label}: meta.json \"lights\" as documented", ml.get(contract.LIGHTS_KEY) == want,
              json.dumps(ml.get(contract.LIGHTS_KEY)))
        rest = {k: v for k, v in ml.items() if k != contract.LIGHTS_KEY}
        check(f"{label}: meta.json as without lights but for \"lights\"", rest == mp)
        sheets = sorted(f for f in os.listdir(po) if f.endswith(".png"))
        check(f"{label}: every sheet ({len(sheets)}) byte for byte as without lights",
              sheets == sorted(f for f in os.listdir(pl) if f.endswith(".png"))
              and all(same_bytes(os.path.join(po, f), os.path.join(pl, f)) for f in sheets))


def want_meta():
    lens = dict(kind="layer", filename=LM, width=300, height=300, scale=0.3, tint=[0.29, 0.53, 1.0],
                draw_as_light=True, shift=[0.84375, -0.5625], working=True)
    foot = dict(kind="definition", type="basic", intensity=0.55, size=0.5, color=[1.0, 0.48, 0.18],
                shift=[-0.71875, -0.71875], working=False)
    lamp = dict(kind="layer", filename=LM, width=300, height=300, scale=0.12, tint=[0.2, 1.0, 0.4],
                draw_as_light=True, shift=TURN_AT, working=False)
    return {"lens": lens, "foot": foot}, {"lamp": lamp}


# ---------------------------------------------------------------- preview

def sheet_of(rdir, png, *extra, tools=TOOLS):
    code, text = run([sys.executable, os.path.join(tools, "preview.py"), rdir, png, *extra])
    return code, text, (Image.open(png).convert("RGBA") if code == 0 else None)


def stand_in_tree(d):
    """d/tools/blender: tools/blender's scripts (not its tests or textures) and tools/paths.py, with a
    paths.conf naming an install that is not there (FACTORIO_ROOT); returned, for sheet_of's tools."""
    if os.path.exists(d):
        shutil.rmtree(d)
    root = os.path.join(d, "tools")
    shutil.copytree(TOOLS, os.path.join(root, "blender"),
                    ignore=shutil.ignore_patterns("test", "textures", "__pycache__"))
    shutil.copy2(os.path.join(os.path.dirname(TOOLS), "paths.py"), root)
    with open(os.path.join(root, "paths.conf"), "w") as f:
        f.write("# the stand-in, for test_night_lights.py: no install here\n"
                f"FACTORIO_ROOT={os.path.join(d, 'no-such-factorio')}\n")
    return os.path.join(root, "blender")


def test_preview(out, bplain, blit, tplain, tlit):
    print("preview")
    mp, ml = preview.Model(bplain), preview.Model(blit)
    canvas = tuple(mp.decl["canvas"])
    lights = ml.decl["lights"]
    for working in (False, True):
        what = "working" if working else "idle"
        check(f"by day, {what}: byte for byte as without lights",
              ml.panel("", working).tobytes() == mp.panel("", working).tobytes())
        nl, np_ = ml.panel("", working, night=True), mp.panel("", working, night=True)
        shown = [li for li in lights if working or not li.get("working")]
        moved = differ(nl, np_)
        stray = sorted(p for p in moved if not any(reach(li, "", canvas, *p) for li in shown))
        check(f"at night, {what}: past every light's reach, byte for byte as without lights ({len(moved)} px moved)",
              not stray and moved, f"{len(stray)} px past it, e.g. {stray[:5]}")
        for li in shown:
            cx, cy = (round(v) for v in centre_of(li, "", canvas))
            a, b = nl.getpixel((cx, cy)), np_.getpixel((cx, cy))
            check(f"at night, {what}: the plate brighter at {li['name']}'s centre ({b[:3]} -> {a[:3]})",
                  sum(a[:3]) > sum(b[:3]))
            if working != li.get("working", False):
                continue                    # the foot's centre, working, is under the glow pass too: idle is bare plate
            mult = [li["intensity"] * c for c in li["color"]] if li["kind"] == "definition" else li["tint"][:3]
            want = [90 * min(1.0, K + m * centre_value()) for m in mult]
            check(f"at night, {what}: at {li['name']}'s centre each channel 90 x min(1, 0.15 + its colour x "
                  f"light-medium's centre), within 2", all(abs(g - w) <= 2 for g, w in zip(a, want)),
                  f"{a[:3]}, want {[round(w, 1) for w in want]}")
    idle, idle0 = ml.panel("", False, night=True), mp.panel("", False, night=True)
    # the foot's falloff: size is its radius (2 x size tiles across), its picture premultiplied
    mult = [FOOT["intensity"] * c for c in FOOT["color"]]
    for f in (0.25, 0.5):
        cx, cy = centre_of(FOOT, "", canvas)
        x, y = round(cx + f * FOOT["size"] * PPT), round(cy)
        got = idle.getpixel((x, y))[:3]
        want = [90 * min(1.0, K + m * centre_value(f)) for m in mult]
        check(f"idle at night, {f:g} of the foot's radius (size {FOOT['size']} tiles) east of its centre: each "
              f"channel 90 x min(1, 0.15 + its colour x light-medium there, premultiplied), within 3",
              all(abs(g - w) <= 3 for g, w in zip(got, want)), f"{got}, want {[round(w, 1) for w in want]}")
    cx, cy = (round(v) for v in centre_of(LENS, "", canvas))
    check("the lens, working only, not in the idle panel (its centre as without lights)",
          idle.getpixel((cx, cy)) == idle0.getpixel((cx, cy)))
    work = ml.panel("", True, night=True)
    gx, gy = 50, 50                         # the glow pass, under the foot
    day_adds = [w - i for w, i in zip(ml.panel("", True).getpixel((gx, gy))[:3],
                                      ml.panel("", False).getpixel((gx, gy)))]
    night_adds = [w - i for w, i in zip(work.getpixel((gx, gy))[:3], idle.getpixel((gx, gy))[:3])]
    check(f"the glow pass under the foot adds at night what it adds by day {day_adds}",
          day_adds == night_adds and any(day_adds), f"night adds {night_adds}")
    wp = mp.panel("", True, night=True)
    for name, (x, y) in (("the lamp", (143, 143)), ("the beacon", (62, 132))):
        check(f"{name}, in the lens's reach, at night as without lights",
              reach(LENS, "", canvas, x, y) and work.getpixel((x, y)) == wp.getpixel((x, y)))

    # the sheet
    code, text, s = sheet_of(blit, os.path.join(out, "night-lights.png"))
    code0, text0, s0 = sheet_of(bplain, os.path.join(out, "night-plain.png"))
    pw = ph = canvas[0] + 2 * preview.PAD
    check("the sheet: exit 0, a night row", code == code0 == 0 and s.size == s0.size == (
        preview.PAD + 2 * (pw + preview.PAD), pn.tall(2, ph)), f"{text[-300:]}{text0[-300:]}")
    if s and s0:
        day = (0, 0, s.width, preview.PAD + ph + preview.LABEL + preview.PAD)
        check("the sheet's day row byte for byte as without lights", s.crop(day).tobytes() == s0.crop(day).tobytes())
        # above the canvas, under the lens: the panel's ground past the canvas
        x = preview.PAD + (pw + preview.PAD) + preview.PAD + round(centre_of(LENS, "", canvas)[0])
        y_night = preview.PAD + (ph + preview.LABEL + preview.PAD) + preview.LABEL + preview.PAD // 2
        y_day = preview.PAD + preview.LABEL + preview.PAD // 2
        g = preview.ground(K)
        check("the night row lights the ground past the canvas, under the lens",
              s.getpixel((x, y_night))[2] > g[2] and s0.getpixel((x, y_night)) == g,
              f"{s.getpixel((x, y_night))} (without lights {s0.getpixel((x, y_night))})")
        check("the day row does not", s.getpixel((x, y_day)) == s0.getpixel((x, y_day)) == preview.GROUND)
        cell = pn.body(pn.cell(s, 1, 1, pw, ph))
        lm = ml.light_map("", True, (pw, ph), (pw / 2, ph / 2))
        x0, y0 = preview.corner(canvas, (pw / 2, ph / 2))
        art = ml.panel("", True, night=True, light=lm.crop((x0, y0, x0 + canvas[0], y0 + canvas[1])))
        want = preview.place(art, (pw, ph), (pw / 2, ph / 2), by=lm)
        preview.grid(want, (pw / 2, ph / 2), (2, 2), PPT)
        want = Image.alpha_composite(Image.new("RGBA", want.size, preview.GAP), want)
        check("the sheet's working night place: the panel under the panel-wide lights, placed, gridded",
              cell.tobytes() == want.tobytes())
    for args, label in ((["--day-only"], "--day-only sheet"), (["--gif", "bar", "--speed", "1"], "--gif of the bar")):
        ext = ".gif" if "--gif" in args else ".png"
        a, b = os.path.join(out, "lit" + args[0] + ext), os.path.join(out, "plain" + args[0] + ext)
        c1, t1 = run([sys.executable, os.path.join(TOOLS, "preview.py"), blit, a, *args])
        c2, t2 = run([sys.executable, os.path.join(TOOLS, "preview.py"), bplain, b, *args])
        check(f"the {label}: byte for byte as without lights", c1 == c2 == 0 and same_bytes(a, b),
              (t1 + t2)[-300:])

    wrong_root = stand_in_tree(os.path.join(out, "no-install"))
    code, text, _ = sheet_of(blit, os.path.join(out, "x.png"), tools=wrong_root)
    check("FACTORIO_ROOT wrong: the sheet refused, naming FACTORIO_ROOT", code != 0 and "FACTORIO_ROOT" in text,
          f"exit {code}: {text[-200:]}")
    code, text, _ = sheet_of(blit, os.path.join(out, "x.png"), "--day-only", tools=wrong_root)
    check("FACTORIO_ROOT wrong: --day-only drawn (no light drawn)", code == 0, text[-200:])
    wrong = with_lights(bplain, os.path.join(out, "building-wrong-size"), [dict(LENS, width=200)])
    code, text, _ = sheet_of(wrong, os.path.join(out, "x.png"))
    check("a layer's width and height not its picture's: refused, naming them",
          code != 0 and "300x300" in text and "200x300" in text, f"exit {code}: {text[-200:]}")

    # the turning fixture
    tp, tl = preview.Model(tplain), preview.Model(tlit)
    for d in rg.DIRS:
        check(f"{d}: the wreck, by day and at night, byte for byte as without lights",
              all(tl.wreck(d, night=n).tobytes() == tp.wreck(d, night=n).tobytes() for n in (False, True)))
        nl, np_ = tl.panel(d, True, night=True), tp.panel(d, True, night=True)
        mine = [round(v) for v in centre_of(TURN, d, rg.MODEL)]
        others = {o: [round(v) for v in centre_of(TURN, o, rg.MODEL)] for o in rg.DIRS if o != d}
        lit_here = sum(nl.getpixel(tuple(mine))[:3]) > sum(np_.getpixel(tuple(mine))[:3])
        dark_there = all(nl.getpixel(tuple(p)) == np_.getpixel(tuple(p)) for p in others.values())
        check(f"{d}: lit at its own shift {TURN_AT[d]}, as without lights at the others'", lit_here and dark_there,
              f"{nl.getpixel(tuple(mine))} vs {np_.getpixel(tuple(mine))}")
    code, text, s = sheet_of(tlit, os.path.join(out, "night-lights-turning.png"))
    code0, text0, s0 = sheet_of(tplain, os.path.join(out, "night-plain-turning.png"))
    check("the turning fixture's sheet: exit 0, the size of the one without lights",
          code == code0 == 0 and s.size == s0.size, (text + text0)[-300:])


# ---------------------------------------------------------------- identity

def baseline_tools(rev, out):
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


def same_dirs(a, b):
    fa, fb = sorted(os.listdir(a)), sorted(os.listdir(b))
    return fa == fb and all(same_bytes(os.path.join(a, f), os.path.join(b, f)) for f in fa), len(fa)


def test_identity(out, base, renders):
    print("identity")
    for r in renders:
        label = os.path.basename(os.path.normpath(r))
        rdir = os.path.join(r, "renders")
        decl = contract.load(rdir)
        check(f"{label}: declares no lights", "lights" not in decl)
        res = {}
        for who, tools in (("mine", TOOLS), ("base", base)):
            o = os.path.join(out, f"{label}-{who}")
            if os.path.exists(o):
                shutil.rmtree(o)
            os.makedirs(o)
            code, text = run([sys.executable, os.path.join(tools, "pack.py"), rdir, os.path.join(o, "pack")])
            jobs = [("sheet.png", []), ("day-only.png", ["--day-only"])]
            if decl["animations"]:
                jobs.append(("anim.gif", ["--gif", decl["animations"][0]["name"], "--speed", "1"]))
            codes = [code]
            for name, extra in jobs:
                c, t = run([sys.executable, os.path.join(tools, "preview.py"), rdir, os.path.join(o, name), *extra])
                codes.append(c)
                text += t
            res[who] = (o, codes, text, [n for n, _ in jobs])
        (om, cm, tm, jobs), (ob, cb, tb, _) = res["mine"], res["base"]
        check(f"{label}: pack.py and preview.py exit as the baseline's ({cm}, baseline {cb})", cm == cb,
              (tm + tb)[-300:])
        same, n = same_dirs(os.path.join(om, "pack"), os.path.join(ob, "pack"))
        check(f"{label}: pack.py's outputs ({n} files) byte for byte as the baseline's", same)
        for name in jobs:
            a, b = os.path.join(om, name), os.path.join(ob, name)
            check(f"{label}: preview.py's {name} byte for byte as the baseline's",
                  os.path.exists(a) and os.path.exists(b) and same_bytes(a, b))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out")
    ap.add_argument("--baseline", metavar="GIT_REV")
    ap.add_argument("--renders", nargs="+", default=[], metavar="RENDER_OUT")
    a = ap.parse_args()
    if a.renders and not a.baseline:
        ap.error("--renders goes with --baseline")
    out = a.out or tempfile.mkdtemp(prefix="night-lights-test-")
    os.makedirs(out, exist_ok=True)
    print(f"writing under {out}")
    bplain = pn.building(os.path.join(out, "building"))
    blit = with_lights(bplain, os.path.join(out, "building-lights"), [LENS, FOOT])
    tplain = rg.write_fixture(os.path.join(out, "turning"))
    tlit = with_lights(tplain, os.path.join(out, "turning-lights"), [TURN])
    one = with_lights(tplain, os.path.join(out, "turning-one-shift"), [dict(TURN, shift=[0.25, 0.25])])
    test_contract(blit, tlit)
    bwant, twant = want_meta()
    one_want = {"lamp": dict(twant["lamp"], shift={d: [0.25, 0.25] for d in rg.DIRS})}
    test_pack(out, [("building", bplain, blit, bwant), ("turning", tplain, tlit, twant),
                    ("turning-one-shift", tplain, one, one_want)])
    test_preview(out, bplain, blit, tplain, tlit)
    if a.baseline:
        test_identity(out, baseline_tools(a.baseline, out), [os.path.abspath(r) for r in a.renders])
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
