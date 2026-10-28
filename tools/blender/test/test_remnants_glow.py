#!/usr/bin/env python3
"""The wreck's glow (a remnants pass's `glow`, contract.py; pack.py) held to its docs.

  python3 tools/blender/test/test_remnants_glow.py [--out <dir>] [--baseline <git-rev>
                                                   [--renders <render-out> ...]]

Nothing is rendered here. A fixture model is drawn with PIL: a 2x2 plate on a 192 px canvas, and
its wreck on a 256 px canvas of its own, four directions -- a slab of debris over a part-transparent
black shadow, its mouth's floor dark -- and the wreck again with its light on (the glow's render): a
40 x 16 px core in the mouth adding (30, 95, 241), whose blue passes pack.KNEE so the roll-off has
something to roll, in a 3 px ring adding (12, 38, 96), the mouth at a different place in each
direction. In north, one group of SPECK_PX pixels of haze (luma 9, over LAYER_FLOOR) far from the
mouth, under 1 - pack.LIGHT_SHARE of the light. --baseline names a commit from before the wreck's
glow (a71471c): its contract.py, pack.py and preview.py, taken out with `git show`, are run beside
this tree's. Everything is written under --out (default: a new directory under the system's
temporary one, named when it starts) and kept.

Exits 0 when every case below comes out as listed, 1 naming those that do not.

  contract   the fixture accepted; refused, each naming its field: a glow on the plate
             (passes[0].glow), a glow that is a string, one with no sheet, one with a key past name
             and sheet, a name that is a pass's ("idle"), a name or sheet that is not a name ("",
             "a/b"), a sheet that is the wreck's own ("remnants"), the plate's ("base"), one the
             plate's sheet takes in a direction ("base-north") or "checks" (passes[1].glow.*);
             "base-vertical" accepted in the four-direction fixture.
  sheet      the fixture packed: exit 0; meta.json's glow entry has direction_count 4, line_length 1,
             rows north, east, south, west, kind "remnants", draw_as_glow true and blend_mode
             "additive", and comes after the wreck's and before "checks", with no entry per direction;
             remnants-glow.png is size[0] x 4 size[1]; each row is pack.glow_layer of that direction's
             renders (glow minus wreck), rolled off (pack.roll), cut at the box its size and shift give
             on the 256 px canvas, pixel for pixel; that box is the union of the four directions' light,
             each side 1 px (the rim) from one; every pixel of each mouth's core kept, opaque; each row
             keeps at least LIGHT_SHARE of its direction's light; the haze outside the box, though the
             box of every lit pixel (the crop before T06) reaches it. Per direction, its
             remnants-glow_white_px 0, after the wreck's checks; rolloff_px names remnants-glow, with
             pixels changed (the core's blue).
  options    rolloff false: every row glow_layer's, unrolled, and no rolloff_px; cut [E, W, S]: the glow
             sheet byte for byte as uncut, and cut_px names no glow render.
  refused    a glow render missing in east: non-zero, naming wreck-lit-east.png, nothing written; one at
             the model's canvas (192) in south: non-zero, naming the 256x256 canvas; one that lights
             nothing (the wreck itself) in west: non-zero, naming it empty. Over-driven (the core
             white in north): exit 0 and remnants-glow_white_px over 0 in north, 0 elsewhere --
             information, as a glow pass's.
  layouts    as horizontal-vertical (north as vertical, east as horizontal): four rows, vertical,
             horizontal, vertical, horizontal, rows 1 and 3 and rows 2 and 4 the same bytes, 1 and 2
             not; as one direction (north): direction_count 1, the sheet its size. measure.py on that
             one: the glow sheet no layer of the building, with render.json and with the sheets alone
             (there listed as ignored, as the wreck is).
  identity   the fixture without its glow: every file but remnants-glow.png byte for byte as with it,
             and meta.json as with it less the glow's entry, its white_px checks and its rolloff_px
             entries, in the same order. preview.py exits 0 on the fixture (it draws the glow, by day
             and at night, since T08f: test_preview_night.py holds it to that).
  baseline   with --baseline: on the fixture, the baseline's pack.py (which knows no glow, and leaves
             it be) writes every file this tree's does but remnants-glow.png, byte for byte, and
             meta.json as this tree's less the glow (as in identity). On every --renders directory
             (render.sh output: its renders/), pack.py's sheets and meta.json, and preview.py's sheet
             (this tree's with --day-only, its default since T08f-2 having night rows), byte for byte
             as the baseline's (its preview.py run with its glow passes' haze cleared, as this tree's
             draws them since T08f-3: baseline_preview.py), and both exit the same; this tree's pack.py
             and preview.py run there with their glow floor set aside (floor_aside.py: judged on luma,
             as before T08h, and nothing else changed), as the baseline's judges it
             (test_glow_floor.py holds the floor).
"""
import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import contract  # noqa: E402
import measure  # noqa: E402
import pack  # noqa: E402
import baseline_preview  # noqa: E402
import floor_aside  # noqa: E402

FAILED = []
MODEL = (192, 192)
CANVAS = (256, 256)                     # the wreck's own
PPT = 64
DIRS = ["north", "east", "south", "west"]
WRECK, LIT = "wreck", "wreck-lit"       # the remnants pass and its glow's render
SHEET, GLOW = "remnants", "remnants-glow"
DEBRIS = (70, 96, 186, 160)             # x0, y0, x1, y1, ends exclusive
DEBRIS_RGB = (70, 64, 58)
SHADOW = (40, 70, 220, 190)             # the ellipse's box: black, alpha 110
FLOOR_RGB = (10, 12, 14)                # the mouth's floor, under the core
CORE_ADDS = (30, 95, 241)               # its blue past pack.KNEE (236): rolled
RING_ADDS = (12, 38, 96)
RING = 3
# each direction's core: x0, y0 (40 x 16), inside the debris with its ring
CORE = {"north": (100, 112), "east": (120, 118), "south": (110, 130), "west": (84, 104)}
CORE_WH = (40, 16)
HAZE = (176, 150, 4)                    # north only: x0, y, length, a row of luma 9
HAZE_ADDS = (9, 9, 9)


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(f"{case}: {detail}")


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def packed(src, out, tools=TOOLS, aside=False):
    """pack.py (tools') src -> out: its exit code, output and meta.json (None if it wrote none).
    With aside, this tree's, its glow floor set aside (floor_aside.py)."""
    if os.path.exists(out):
        shutil.rmtree(out)
    if aside and tools != TOOLS:
        raise ValueError("packed: aside is for this tree's pack.py")
    code, text = run(floor_aside.command("pack.py", [src, out]) if aside else
                     [sys.executable, os.path.join(tools, "pack.py"), src, out])
    meta = os.path.join(out, "meta.json")
    return code, text, (json.load(open(meta)) if os.path.isfile(meta) else None)


def same_bytes(a, b):
    with open(a, "rb") as fa, open(b, "rb") as fb:
        return fa.read() == fb.read()


def files(d):
    return sorted(f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))) if os.path.isdir(d) else []


def same_dirs(a, b, skip=()):
    """Whether two directories hold the same files, byte for byte (but those in skip): (ok, why)."""
    fa, fb = [f for f in files(a) if f not in skip], [f for f in files(b) if f not in skip]
    if fa != fb:
        return False, f"files differ: {sorted(set(fa) ^ set(fb))}"
    bad = [f for f in fa if not same_bytes(os.path.join(a, f), os.path.join(b, f))]
    return not bad, f"differ: {bad}"


def checks_of(meta, d):
    return meta["checks"][d] if d else meta["checks"]


def load_decl(rdir):
    with open(os.path.join(rdir, contract.FILE)) as f:
        return json.load(f)


def save_decl(rdir, decl):
    with open(os.path.join(rdir, contract.FILE), "w") as f:
        json.dump(decl, f, indent=1)


def light(im):
    """An RGBA image's light: the sum of alpha x luma (PIL's L), alpha as a fraction."""
    im = im.convert("RGBA")
    return sum(a * v for a, v in zip(im.getchannel("A").get_flattened_data(),
                                     im.convert("RGB").convert("L").get_flattened_data())) / 255


# ---------------------------------------------------------------- the fixture

def plate():
    im = Image.new("RGBA", MODEL)
    ImageDraw.Draw(im).rectangle((32, 32, 159, 159), fill=(90, 90, 90, 255))
    return im


def core_box(d):
    x, y = CORE[d]
    return x, y, x + CORE_WH[0], y + CORE_WH[1]


def wreck(d):
    """The wreck in direction d: debris over its shadow, the mouth's floor dark."""
    im = Image.new("RGBA", CANVAS)
    dr = ImageDraw.Draw(im)
    dr.ellipse(SHADOW, fill=(0, 0, 0, 110))
    dr.rectangle((DEBRIS[0], DEBRIS[1], DEBRIS[2] - 1, DEBRIS[3] - 1), fill=DEBRIS_RGB + (255,))
    x0, y0, x1, y1 = core_box(d)
    dr.rectangle((x0, y0, x1 - 1, y1 - 1), fill=FLOOR_RGB + (255,))
    return im


def lit(d, haze=True, white=False):
    """The wreck in direction d with its light on: the core, its ring, and (north) the haze."""
    im = wreck(d)
    px = im.load()
    x0, y0, x1, y1 = core_box(d)
    adds = {}
    for x in range(x0 - RING, x1 + RING):
        for y in range(y0 - RING, y1 + RING):
            adds[x, y] = CORE_ADDS if x0 <= x < x1 and y0 <= y < y1 else RING_ADDS
    if haze and d == "north":
        adds.update({(HAZE[0] + i, HAZE[1]): HAZE_ADDS for i in range(HAZE[2])})
    for (x, y), add in adds.items():
        r, g, b, a = px[x, y]
        px[x, y] = (min(255, r + add[0]), min(255, g + add[1]), min(255, b + add[2]), a)
    if white:
        ImageDraw.Draw(im).rectangle((x0, y0, x1 - 1, y1 - 1), fill=(255, 255, 255, 255))
    return im


def decl_of(directions="four"):
    return dict(footprint=[2, 2], canvas=list(MODEL), directions=directions,
                passes=[dict(name="idle", kind="plate", sheet="base"),
                        dict(name=WRECK, kind="remnants", sheet=SHEET, canvas=list(CANVAS),
                             glow=dict(name=LIT, sheet=GLOW))],
                animations=[], ports=[], rig=dict(elevation=60.0, px_per_tile=PPT))


def write_fixture(rdir, edit=None, directions="four", names=None):
    """The fixture's renders and render.json in rdir. names {direction: the fixture's direction it
    takes}, for another layout; edit(decl, rdir) after it is written."""
    if os.path.exists(rdir):
        shutil.rmtree(rdir)
    os.makedirs(rdir)
    names = names or {d: d for d in DIRS}
    decl = decl_of(directions)
    contract.validate(decl, rdir)
    for new, d in names.items():
        plate().save(os.path.join(rdir, contract.named("idle", new) + ".png"))
        wreck(d).save(os.path.join(rdir, contract.named(WRECK, new) + ".png"))
        lit(d).save(os.path.join(rdir, contract.named(LIT, new) + ".png"))
    if edit:
        edit(decl, rdir)
    save_decl(rdir, decl)
    return rdir


def row_box(entry, canvas=CANVAS):
    """The box on the wreck's canvas that a meta.json entry's size and shift say each row was cut from."""
    (w, h), (sx, sy) = entry["size"], entry["shift"]
    x0, y0 = round(canvas[0] / 2 + sx * PPT - w / 2), round(canvas[1] / 2 + sy * PPT - h / 2)
    return x0, y0, x0 + w, y0 + h


def rows_of(sheet, entry):
    w, h = entry["size"]
    return [sheet.crop((0, i * h, w, (i + 1) * h)) for i in range(entry["direction_count"])]


# ---------------------------------------------------------------- contract

def test_contract():
    print("contract")
    decl0 = decl_of()

    def case(label, edit, want_field=None):
        d = copy.deepcopy(decl0)
        edit(d)
        try:
            contract.validate(d, "test")
            check(label, want_field is None, "accepted, but should be refused naming " + str(want_field))
        except contract.ContractError as e:
            check(label, want_field is not None and f": {want_field}:" in str(e),
                  f"refused: {e}" if want_field is None else f"refused, not naming {want_field}: {e}")

    def glow(**kw):
        return lambda d: d["passes"][1]["glow"].update(**kw)
    case("the fixture accepted", lambda d: None)
    case("a glow on the plate refused", lambda d: d["passes"][0].update(glow=dict(name="x", sheet="y")),
         "passes[0].glow")
    case("a glow that is a string refused", lambda d: d["passes"][1].update(glow="wreck-lit"), "passes[1].glow")
    case("a glow with no sheet refused", lambda d: d["passes"][1]["glow"].pop("sheet"), "passes[1].glow")
    case("a glow with a key past name and sheet refused", glow(over="wreck"), "passes[1].glow")
    case("a glow named as a pass ('idle') refused", glow(name="idle"), "passes[1].glow.name")
    case("a glow named '' refused", glow(name=""), "passes[1].glow.name")
    case("a glow sheet 'a/b' refused", glow(sheet="a/b"), "passes[1].glow.sheet")
    for name in ("remnants", "base", "base-north", "checks"):
        case(f"a glow sheet {name!r} refused", glow(sheet=name), "passes[1].glow.sheet")
    case("a glow sheet 'base-vertical' accepted in a four-direction model", glow(sheet="base-vertical"))


# ---------------------------------------------------------------- the sheet and its checks

def glow_before_box(d):
    """glow_layer's light before the light box: lit minus the wreck over the floor, specks dropped."""
    diff = ImageChops.subtract(lit(d).convert("RGB"), wreck(d).convert("RGB"))
    alpha = pack.drop_specks(pack.brightest(diff).point(lambda v: 255 if v > pack.LAYER_FLOOR else 0))
    return Image.merge("RGBA", (*diff.split(), alpha))


def test_sheet(out):
    print("sheet and checks")
    src = write_fixture(os.path.join(out, "fixture"))
    code, text, meta = packed(src, os.path.join(out, "fixture-sheets"))
    check("the fixture packs: exit 0", code == 0, text[-400:])
    if meta is None:
        return None
    m = meta.get(GLOW, {})
    want = dict(direction_count=4, line_length=1, rows=DIRS, kind="remnants", draw_as_glow=True,
                blend_mode="additive")
    check("meta.json remnants-glow: direction_count 4, line_length 1, rows N E S W, kind remnants, draw_as_glow, "
          "blend_mode additive", {k: m.get(k) for k in want} == want, f"{m}")
    keys = list(meta)
    check("meta.json: the glow's entry after the wreck's, before checks, none per direction",
          keys[-3:] == [SHEET, GLOW, "checks"] and not any(k.startswith(GLOW + "-") for k in keys), f"{keys}")
    sheet = Image.open(os.path.join(out, "fixture-sheets", GLOW + ".png")).convert("RGBA")
    w, h = m["size"]
    check(f"remnants-glow.png is {w} x 4 x {h}", sheet.size == (w, 4 * h), f"{sheet.size}")
    u = row_box(m)
    layers = {d: pack.glow_layer(lit(d), wreck(d)) for d in DIRS}
    rows = rows_of(sheet, m)
    for i, d in enumerate(m["rows"]):
        check(f"row {i + 1} ({d}): glow_layer of its renders, rolled off, cut at size and shift, pixel for pixel",
              rows[i].tobytes() == pack.roll(layers[d])[0].crop(u).tobytes())
    bbs = [lay.getchannel("A").getbbox() for lay in layers.values()]
    tight = (min(b[0] for b in bbs) - u[0], min(b[1] for b in bbs) - u[1],
             u[2] - max(b[2] for b in bbs), u[3] - max(b[3] for b in bbs))
    check("the one box holds every direction's light, each side 1 px (the rim) from one", tight == (1, 1, 1, 1),
          f"margins {tight}")
    for i, d in enumerate(m["rows"]):
        x0, y0, x1, y1 = core_box(d)
        a = rows[i].getchannel("A")
        check(f"{d}: every pixel of the core kept, opaque",
              all(a.getpixel((x - u[0], y - u[1])) == 255 for x in range(x0, x1) for y in range(y0, y1)))
        before, kept = light(glow_before_box(d)), light(layers[d])
        check(f"{d}: keeps {100 * kept / before:.3f} % of its light, at least {100 * pack.LIGHT_SHARE:g} %",
              kept >= pack.LIGHT_SHARE * before)
    hx, hy, hn = HAZE
    old = glow_before_box("north").getchannel("A").getbbox()
    check(f"the haze outside the box {u}; the box of every lit pixel ({old}) reaches it",
          not (u[0] <= hx < u[2] and u[1] <= hy < u[3])
          and old[0] <= hx and hx + hn <= old[2] and old[1] <= hy < old[3])
    haze_share = 1 - light(layers["north"]) / light(glow_before_box("north"))
    check(f"the haze is {100 * haze_share:.3f} % of north's light, under {100 * (1 - pack.LIGHT_SHARE):.3g} % "
          f"(the fixture is what it says)", 0 < haze_share < 1 - pack.LIGHT_SHARE)
    for d in DIRS:
        c = checks_of(meta, d)
        ck = list(c)
        white = c.get(f"{GLOW}_white_px", [None])[0]
        check(f"{d}: remnants-glow_white_px 0, after the wreck's checks",
              white == 0 and ck.index(f"{GLOW}_white_px") == ck.index(f"{SHEET}_reach_tiles") + 1, f"{white}, {ck}")
        r = c.get("rolloff_px", [{}])[0].get(GLOW)
        check(f"{d}: rolloff_px names remnants-glow, with pixels changed", r is not None and r["px"] > 0, f"{r}")
    return meta


def test_options(out):
    print("options")
    off = write_fixture(os.path.join(out, "rolloff-off"), lambda d, _: d.update(rolloff=False))
    code, text, meta = packed(off, os.path.join(out, "rolloff-off-sheets"))
    check("rolloff false: exit 0", code == 0, text[-300:])
    if meta:
        m = meta[GLOW]
        rows = rows_of(Image.open(os.path.join(out, "rolloff-off-sheets", GLOW + ".png")).convert("RGBA"), m)
        u = row_box(m)
        check("rolloff false: every row glow_layer's, unrolled",
              all(r.tobytes() == pack.glow_layer(lit(d), wreck(d)).crop(u).tobytes() for r, d in zip(rows, m["rows"])))
        check("rolloff false: no rolloff_px", not any("rolloff_px" in checks_of(meta, d) for d in DIRS))
    cut = write_fixture(os.path.join(out, "cut"), lambda d, _: d.update(cut=["E", "W", "S"]))
    code, text, meta = packed(cut, os.path.join(out, "cut-sheets"))
    check("cut [E, W, S]: exit 0, the glow sheet byte for byte as uncut",
          code == 0 and same_bytes(os.path.join(out, "cut-sheets", GLOW + ".png"),
                                   os.path.join(out, "fixture-sheets", GLOW + ".png")), text[-300:])
    named = [k for d in DIRS for k in checks_of(meta, d).get("cut_px", [{}])[0] if k.startswith(LIT)] if meta else ["?"]
    check("cut [E, W, S]: cut_px names no glow render", not named, f"{named}")


def test_refused(out):
    print("refused")

    def gone(_, dst):
        os.remove(os.path.join(dst, contract.named(LIT, "east") + ".png"))
    code, text, _ = packed(write_fixture(os.path.join(out, "gone"), gone), os.path.join(out, "gone-sheets"))
    check("a glow render missing in east: non-zero, naming wreck-lit-east.png, nothing written",
          code != 0 and "wreck-lit-east.png" in text and not files(os.path.join(out, "gone-sheets")),
          f"exit {code}: {text[-300:]}")

    def small(_, dst):
        f = os.path.join(dst, contract.named(LIT, "south") + ".png")
        Image.open(f).crop((32, 32, 224, 224)).save(f)
    code, text, _ = packed(write_fixture(os.path.join(out, "small"), small), os.path.join(out, "small-sheets"))
    check("a glow render at the model's canvas in south: non-zero, naming the 256x256 canvas",
          code != 0 and "wreck-lit-south.png is 192x192" in text and "256x256 canvas" in text,
          f"exit {code}: {text[-300:]}")

    def dark(_, dst):
        wreck("west").save(os.path.join(dst, contract.named(LIT, "west") + ".png"))
    code, text, _ = packed(write_fixture(os.path.join(out, "dark"), dark), os.path.join(out, "dark-sheets"))
    check("a glow that lights nothing in west: non-zero, naming it empty",
          code != 0 and "wreck-lit-west.png minus its wreck is empty" in text, f"exit {code}: {text[-300:]}")

    def hot(_, dst):
        lit("north", white=True).save(os.path.join(dst, contract.named(LIT, "north") + ".png"))
    code, text, meta = packed(write_fixture(os.path.join(out, "white"), hot), os.path.join(out, "white-sheets"))
    whites = {d: checks_of(meta, d)[f"{GLOW}_white_px"][0] for d in DIRS} if meta else {}
    check("over-driven in north: exit 0 (information, as a glow pass's), white_px over 0 there, 0 elsewhere",
          code == 0 and whites.get("north", 0) > 0 and all(whites[d] == 0 for d in DIRS[1:]),
          f"exit {code}, {whites}: {text[-300:]}")


# ---------------------------------------------------------------- other layouts

def test_layouts(out):
    print("layouts")
    hv = write_fixture(os.path.join(out, "hv"), directions="horizontal-vertical",
                       names=dict(vertical="north", horizontal="east"))
    code, text, meta = packed(hv, os.path.join(out, "hv-sheets"))
    check("horizontal-vertical: exit 0", code == 0, text[-400:])
    if meta:
        m = meta[GLOW]
        sheet = Image.open(os.path.join(out, "hv-sheets", GLOW + ".png")).convert("RGBA")
        rows = rows_of(sheet, m)
        check("horizontal-vertical: four rows, vertical, horizontal, vertical, horizontal",
              m["direction_count"] == 4 and m["rows"] == ["vertical", "horizontal"] * 2
              and sheet.size == (m["size"][0], 4 * m["size"][1]), f"{m}, {sheet.size}")
        check("horizontal-vertical: rows 1 and 3, 2 and 4 the same, 1 and 2 not",
              rows[0].tobytes() == rows[2].tobytes() and rows[1].tobytes() == rows[3].tobytes()
              and rows[0].tobytes() != rows[1].tobytes())

    one = os.path.join(out, "one")
    write_fixture(os.path.join(one, "renders"), directions="one", names={"": "north"})
    code, text, meta = packed(os.path.join(one, "renders"), os.path.join(one, "sheets"))
    check("one direction: exit 0", code == 0, text[-400:])
    if not meta:
        return
    m = meta[GLOW]
    sheet = Image.open(os.path.join(one, "sheets", GLOW + ".png"))
    check("one direction: direction_count 1, one row, the sheet its size",
          m["direction_count"] == 1 and m["rows"] == [""] and list(sheet.size) == list(m["size"]), f"{m}, {sheet.size}")
    try:
        s = measure.Source(one)
        stems = [lay.stem for lay in s.layers[""]]
        check("measure.py, one direction, with render.json: the glow sheet no layer", GLOW not in stems, f"{stems}")
    except measure.Usage as e:
        check("measure.py, one direction: reads it", False, str(e))
    alone = os.path.join(out, "one-sheets-alone", "sheets")       # no renders/ beside it: no render.json
    if os.path.exists(os.path.dirname(alone)):
        shutil.rmtree(os.path.dirname(alone))
    shutil.copytree(os.path.join(one, "sheets"), alone)
    try:
        s = measure.Source(alone, footprint=[2, 2])
        stems = [lay.stem for lay in s.layers[""]]
        check("measure.py, one direction, the sheets alone: the glow sheet no layer, listed as ignored",
              GLOW not in stems and any(i.startswith(GLOW + " (remnants") for i in s.ignored[""]),
              f"layers {stems}, ignored {s.ignored['']}")
    except measure.Usage as e:
        check("measure.py, the sheets alone: reads them", False, str(e))


# ---------------------------------------------------------------- identity

def without_glow(meta):
    """meta.json as it would be with no glow: its entry, its white_px checks, its rolloff_px entries gone."""
    meta = copy.deepcopy(meta)
    meta.pop(GLOW, None)
    per = meta["checks"].values() if all(d in meta["checks"] for d in DIRS) else [meta["checks"]]
    for c in per:
        c.pop(f"{GLOW}_white_px", None)
        if "rolloff_px" in c:
            c["rolloff_px"][0].pop(GLOW, None)
    return meta


def drop_glow(decl, dst):
    for d in DIRS:
        os.remove(os.path.join(dst, contract.named(LIT, d) + ".png"))
    decl["passes"][1].pop("glow")


def test_identity(out, meta_with):
    print("identity")
    bare = write_fixture(os.path.join(out, "no-glow"), drop_glow)
    code, text, meta = packed(bare, os.path.join(out, "no-glow-sheets"))
    check("without the glow: exit 0", code == 0, text[-300:])
    ok, why = same_dirs(os.path.join(out, "no-glow-sheets"), os.path.join(out, "fixture-sheets"),
                        skip=("meta.json", GLOW + ".png"))
    check("without the glow: every sheet byte for byte as with it", ok, why)
    if meta and meta_with:
        stripped = without_glow(meta_with)
        check("without the glow: meta.json as with it less the glow's entry, checks and rolloff_px entries, "
              "in order", json.dumps(stripped) == json.dumps(meta))
    code, text = run([sys.executable, os.path.join(TOOLS, "preview.py"), os.path.join(out, "fixture"),
                      os.path.join(out, "preview.png")])
    check("preview.py on the fixture: exit 0", code == 0, text[-300:])
    code2, _ = run([sys.executable, os.path.join(TOOLS, "preview.py"), bare, os.path.join(out, "preview-no-glow.png")])
    same = code == code2 == 0 and same_bytes(os.path.join(out, "preview.png"), os.path.join(out, "preview-no-glow.png"))
    print(f"  info  preview.py draws the fixture as without its glow: {same} (False since T08f, the wreck panel "
          f"carrying its glow, and T08f-2, a night row by default; test_preview_night.py)")


# ---------------------------------------------------------------- baseline

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


def compare(label, rdir, out, base):
    """This tree's pack.py and preview.py (their glow floor set aside: floor_aside.py) and the baseline's
    on one render directory: byte for byte."""
    print(f"baseline: {label}")
    mine, theirs = os.path.join(out, f"{label}-mine"), os.path.join(out, f"{label}-base")
    codes = []
    for tools, o in ((TOOLS, mine), (base, theirs)):
        code, text, _ = packed(rdir, os.path.join(o, "sheets"), tools, aside=tools == TOOLS)
        codes.append(code)
        if code:
            print(f"    pack.py ({'this tree' if tools == TOOLS else 'baseline'}) exit {code}: {text[-200:]}")
        day = ["--day-only"] if tools == TOOLS else []     # night rows by default since T08f-2
        args = [rdir, os.path.join(o, "preview.png"), *day]
        # the baseline's glow passes' haze cleared, as this tree's preview.py draws them (T08f-3);
        # this tree's glow floor set aside, as the baseline's judges it (T08h)
        pcode, ptext = run(floor_aside.command("preview.py", args) if tools == TOOLS
                           else baseline_preview.command(tools, args))
        codes.append(pcode)
        if pcode:
            print(f"    preview.py ({'this tree' if tools == TOOLS else 'baseline'}) exit {pcode}: {ptext[-200:]}")
    check(f"{label}: pack.py and preview.py exit as the baseline's ({codes[:2]}, baseline {codes[2:]})",
          codes[:2] == codes[2:])
    ok, why = same_dirs(os.path.join(mine, "sheets"), os.path.join(theirs, "sheets"))
    n = len(files(os.path.join(mine, "sheets")))
    check(f"{label}: pack.py's sheets and meta.json, this tree's floor set aside, byte for byte as the baseline's "
          f"({n} files)", ok and n > 0, why)
    ok, why = same_dirs(mine, theirs)
    check(f"{label}: preview.py's sheet byte for byte as the baseline's, its haze cleared, this tree's floor set "
          f"aside", ok and "preview.png" in
          files(mine), why)


def test_baseline(out, base, renders):
    print("baseline")
    code, text, meta = packed(os.path.join(out, "fixture"), os.path.join(out, "fixture-sheets-base"), base)
    check("the fixture, baseline pack.py: exit 0", code == 0, text[-300:])
    ok, why = same_dirs(os.path.join(out, "fixture-sheets-base"), os.path.join(out, "fixture-sheets"),
                        skip=("meta.json", GLOW + ".png"))
    check("the fixture, baseline pack.py: every sheet but remnants-glow.png byte for byte as this tree's, and no "
          "glow sheet", ok and GLOW + ".png" not in files(os.path.join(out, "fixture-sheets-base")), why)
    mine = json.load(open(os.path.join(out, "fixture-sheets", "meta.json")))
    check("the fixture, baseline pack.py: meta.json as this tree's less the glow",
          meta is not None and json.dumps(meta) == json.dumps(without_glow(mine)))
    for r in renders:
        compare(os.path.basename(os.path.normpath(r)), os.path.join(r, "renders"), out, base)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out")
    ap.add_argument("--baseline", metavar="GIT_REV")
    ap.add_argument("--renders", nargs="+", default=[], metavar="RENDER_OUT")
    a = ap.parse_args()
    if a.renders and not a.baseline:
        ap.error("--renders goes with --baseline")
    out = a.out or tempfile.mkdtemp(prefix="remnants-glow-test-")
    os.makedirs(out, exist_ok=True)
    print(f"writing under {out}")
    base = baseline_tools(a.baseline, out) if a.baseline else None
    test_contract()
    meta = test_sheet(out)
    test_options(out)
    test_refused(out)
    test_layouts(out)
    test_identity(out, meta)
    if base:
        test_baseline(out, base, [os.path.abspath(r) for r in a.renders])
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
