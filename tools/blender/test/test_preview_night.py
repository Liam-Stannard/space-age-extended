#!/usr/bin/env python3
"""preview.py's wreck glow and night view (T08f; the default since T08f-2) and its glows' haze
cleared (T08f-3) held to its docs.

  python3 tools/blender/test/test_preview_night.py [--out <dir>] [--baseline <git-rev>
                                                   [--renders <render-out> ...]]

Nothing is rendered here. Two fixtures are drawn with PIL. The wreck's is test_remnants_glow.py's
(a 2x2 plate on a 192 px canvas, its wreck on a 256 px canvas of its own, four directions, the
wreck again with a blue light in its mouth as the glow's render), with and without its glow. The
building's is one direction, a 2x2 plate on a 192 px canvas with a layer of every kind preview.py
draws, each on pixels of its own: a shadow east of the plate, a glow pass (orange, over the
plate), a paint pass (frost), a light pass (the lamp), a paint animation (a red bar) with a glow
animation over it (cyan) and a light animation (a white beacon). Each fixture is drawn again with
haze: its glow's render a little brighter than the plate (the building's glow pass) or the wreck (the
wreck's glow) over a band of its own -- the plate's or the debris's foot, the shadow, bare film -- by
(4, 6, 8), luma 6, every channel at or under pack.LAYER_FLOOR, so pack.glow_layer leaves the band
clear but coloured.
--baseline names a commit from before T08f (fbe533d): its contract.py, pack.py and preview.py, taken
out with `git show`, are run beside this tree's, its preview.py both as it is and with its glow
passes' haze cleared (baseline_preview.py: the colour pack.glow_layer leaves where its alpha is 0,
and nothing else). Everything is written under --out (default: a new directory under the system's
temporary one, named when it starts) and kept: its night-*.png are the sheets to look at.

Exits 0 when every case below comes out as listed, 1 naming those that do not. "Dimmed" is a
colour times preview.NIGHT (0.15), each channel rounded.

  building  the panel by day as before (this test's own composition of pack.py's layers, in
            preview.py's order, each glow's colour added only where its alpha is above 0, pixel for
            pixel), and at night the same composition with the ground, the plate, the paint
            animation's frame and the paint pass dimmed, every glow and light as by day: pixel for
            pixel, idle and working. Probes, working: the ground (11, 10, 9); the plate and the
            frost dimmed; the shadow off the plate within 1 of its day pixel dimmed; the glow pass
            and the glow animation adding by night what they add by day (night minus the dimmed
            plate under it = day minus the plate); the lamp and the beacon the same pixels as by
            day. With haze: pack.glow_layer leaves colour on the band's
            clear pixels (so there is haze to clear), and every panel, idle and working, by day and
            at night, pixel for pixel as without it; the sheet (night rows and all) and a --gif of the
            bar the same bytes as without it.
  wreck     by day, the wreck panel without its glow plus the glow (pack.glow_layer of its renders,
            rolled off) added: the same pixels wherever the glow is clear, brighter in every core;
            at night, the ground dimmed, the debris dimmed, and every core pixel the dimmed floor
            plus the glow, as by day. With haze: pack.glow_layer leaves colour on the band's clear
            pixels, and in each direction the wreck panel, by day and at night, pixel for pixel as
            without it.
  sheet     by default (no flag), every model has a night row under each direction's, every
            place in it the panel at night, placed and gridded as the day one is: the building
            (two rows, idle and working), the wreck-glow fixture and the fixture without its glow
            (eight rows each, the wreck's place too); the wreck-glow fixture's day row's wreck
            place the wreck with its glow. --night: the same bytes as the default. --day-only:
            one row per direction, no night row (the building one row of two panels, each
            fixture four rows), the wreck-glow fixture's wreck place still the wreck with its
            glow. With --adopted, the adopted place in the night row empty, the others filled.
            Refused: --night with --day-only, --night with --gif. --gif by default, and with
            --day-only, exit 0, the two GIFs the same bytes.
  identity  with --baseline. With --day-only, the fixture without its glow and the building fixture:
            preview.py's sheet byte for byte as the baseline's, both as it is and with its haze
            cleared (neither fixture has any), and the building's GIF of the bar likewise; the
            building with haze: its sheet as the baseline's with its haze cleared, and not as the
            baseline's as it is (which draws the haze). On every --renders directory (render.sh
            output: its renders/): preview.py's sheet with --day-only, and a GIF of its first
            animation (no flag), byte for byte as the baseline's with its haze cleared (no flag),
            both exiting the same; the sheet nowhere brighter than the baseline's as it is, in any
            channel (information: how many pixels are darker, and by how much at most); and
            preview.py with no flag, exit 0 and twice the --day-only sheet's rows (night-<label>.png
            kept for review).
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
import contract  # noqa: E402
import pack  # noqa: E402
import preview  # noqa: E402
import test_remnants_glow as rg  # noqa: E402
import baseline_preview  # noqa: E402

FAILED = []
ROWS = {}                               # a --renders label: its --day-only sheet's height (compare)
CANVAS = (192, 192)
PPT = 64
PLATE = (32, 32, 160, 160)              # x0, y0, x1, y1, ends exclusive
PLATE_RGB = (90, 90, 90)
SHADOW = (150, 60, 190, 140)            # an ellipse east of the plate, black, alpha 200
GLOW = (40, 40, 60, 60)                 # the glow pass: the plate lit orange here
GLOW_ADDS = (150, 80, 20)
FROST = (100, 40, 120, 60)              # the paint pass
FROST_RGB = (180, 200, 230)
LAMP = (140, 140, 146, 146)             # the light pass: a white lens
BAR = (40, 100, 80, 110)                # the paint animation's frame 0 (frame 1 two px east)
BAR_RGB = (150, 40, 40)
FAN_GLOW = (90, 100, 110, 110)          # the glow animation: cyan light on film
FAN_GLOW_RGB = (20, 140, 150)
BEACON = (60, 130, 64, 134)             # the light animation: white
HAZE = (10, 150, 182, 175)              # the building's haze band: the plate's foot and the ground under it
WRECK_HAZE = (20, 152, 236, 215)        # the wreck's: the debris's foot, its shadow and the bare film
HAZE_ADDS = (4, 6, 8)                   # luma 6, no channel over pack.LAYER_FLOOR (8)
K = preview.NIGHT


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(f"{case}: {detail}")


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def same_bytes(a, b):
    with open(a, "rb") as fa, open(b, "rb") as fb:
        return fa.read() == fb.read()


def dimmed(rgb):
    return tuple(round(c * K) for c in rgb)


def rect(dr, box, fill):
    dr.rectangle((box[0], box[1], box[2] - 1, box[3] - 1), fill=fill)


# ---------------------------------------------------------------- the building fixture

def plate_im():
    im = Image.new("RGBA", CANVAS)
    rect(ImageDraw.Draw(im), PLATE, PLATE_RGB + (255,))
    return im


def hazed(im, box):
    """im with HAZE_ADDS added to the colour of every pixel in box, its alpha as it was: the haze."""
    px = im.load()
    for x in range(box[0], box[2]):
        for y in range(box[1], box[3]):
            r, g, b, a = px[x, y]
            px[x, y] = (r + HAZE_ADDS[0], g + HAZE_ADDS[1], b + HAZE_ADDS[2], a)
    return im


def haze_px(glow):
    """A glow sheet's pixels that are clear (alpha 0) but carry colour."""
    return sum(1 for r, g, b, a in glow.get_flattened_data() if a == 0 and (r or g or b))


def area(box):
    return (box[2] - box[0]) * (box[3] - box[1])


def building(rdir, haze=False):
    if os.path.exists(rdir):
        shutil.rmtree(rdir)
    os.makedirs(rdir)
    decl = dict(footprint=[2, 2], canvas=list(CANVAS), directions="one",
                passes=[dict(name="idle", kind="plate", sheet="base"),
                        dict(name="still", kind="still", sheet="still"),
                        dict(name="shadow", kind="shadow", sheet="shadow"),
                        dict(name="working", kind="glow", sheet="glow", over="idle"),
                        dict(name="frost", kind="paint", sheet="frost", over="idle"),
                        dict(name="lamp", kind="light", sheet="lamp")],
                animations=[dict(name="bar", frames=2, motion="cycle"),
                            dict(name="bar-glow", frames=2, motion="flow", kind="glow", over="bar"),
                            dict(name="beacon", frames=2, motion="flow", kind="light")],
                ports=[], rig=dict(elevation=60.0, px_per_tile=PPT))
    contract.validate(decl, rdir)

    def save(im, stem):
        im.save(os.path.join(rdir, stem + ".png"))
    save(plate_im(), "idle")
    save(plate_im(), "still")
    im = Image.new("RGBA", CANVAS)
    ImageDraw.Draw(im).ellipse(SHADOW, fill=(0, 0, 0, 200))
    save(im, "shadow")
    im = plate_im()
    rect(ImageDraw.Draw(im), GLOW, tuple(min(255, p + a) for p, a in zip(PLATE_RGB, GLOW_ADDS)) + (255,))
    save(hazed(im, HAZE) if haze else im, "working")
    im = plate_im()
    rect(ImageDraw.Draw(im), FROST, FROST_RGB + (255,))
    save(im, "frost")
    im = Image.new("RGBA", CANVAS)
    rect(ImageDraw.Draw(im), LAMP, (255, 255, 255, 255))
    save(im, "lamp")
    for f in range(2):
        for stem, box, fill in (("bar", BAR, BAR_RGB), ("bar-glow", FAN_GLOW, FAN_GLOW_RGB),
                                ("beacon", BEACON, (255, 255, 255))):
            im = Image.new("RGBA", CANVAS)
            rect(ImageDraw.Draw(im), (box[0] + 2 * f, box[1], box[2] + 2 * f, box[3]), fill + (255,))
            save(im, contract.frame(stem, f, ""))
    rg.save_decl(rdir, decl)
    return rdir


def opened(rdir, stem):
    return Image.open(os.path.join(rdir, stem + ".png")).convert("RGBA")


def dim(im, by):
    """This test's own: colour times by, rounded, alpha kept."""
    if by == 1:
        return im
    px = [(round(r * by), round(g * by), round(b * by), a) for r, g, b, a in im.get_flattened_data()]
    out = Image.new("RGBA", im.size)
    out.putdata(px)
    return out


def expected(rdir, working, night):
    """The building's panel as preview.py's docs compose it: by day, and at night with every layer
    but a glow or a light dimmed; each glow's colour added only where its alpha is above 0."""
    k = K if night else 1
    roll = (lambda im: pack.roll(im)[0])
    im = Image.new("RGBA", CANVAS, dimmed(preview.GROUND[:3]) + (255,) if night else preview.GROUND)
    alpha = pack.clean(opened(rdir, "shadow")).getchannel("A")
    im.paste(Image.new("RGBA", CANVAS, (0, 0, 0, 255)), (0, 0), alpha.point(lambda v: v // 2))
    im.alpha_composite(dim(roll(opened(rdir, "idle")), k))
    im.alpha_composite(dim(roll(pack.clean(opened(rdir, contract.frame("bar", 0, "")))), k))
    im.alpha_composite(pack.clean(opened(rdir, contract.frame("beacon", 0, ""))))
    if working:
        glows = (pack.glow_frame(opened(rdir, contract.frame("bar-glow", 0, ""))),
                 pack.glow_layer(opened(rdir, "working"), opened(rdir, "idle")))
        for g in glows:
            im = pack.add_light(im, baseline_preview.cleared(roll(g)))
        im.alpha_composite(dim(roll(pack.paint_layer(opened(rdir, "frost"), opened(rdir, "idle"))), k))
    lamp = pack.light_layer(opened(rdir, "lamp"))
    im.alpha_composite(ImageChops.multiply(lamp, Image.new("RGBA", lamp.size, preview.LAMP[working])))
    return im


def test_building(out):
    print("building")
    rdir = building(os.path.join(out, "building"))
    m = preview.Model(rdir)
    panels = {}
    for working in (False, True):
        for night in (False, True):
            got = m.panel("", working, night=night)
            panels[working, night] = got
            what = f"{'working' if working else 'idle'} {'at night' if night else 'by day'}"
            check(f"{what}: the documented composition, pixel for pixel",
                  got.tobytes() == expected(rdir, working, night).tobytes())
    day, nit = panels[True, False], panels[True, True]

    def px(im, x, y):
        return im.getpixel((x, y))[:3]
    check("the ground at night (11, 10, 9)", px(nit, 5, 5) == (11, 10, 9) == dimmed(preview.GROUND[:3]),
          f"{px(nit, 5, 5)}")
    for name, (x, y) in (("the plate", (80, 140)), ("the frost", (110, 50))):
        check(f"{name} dimmed", px(nit, x, y) == dimmed(px(day, x, y)), f"{px(day, x, y)} -> {px(nit, x, y)}")
    sx, sy = 175, 100
    check("the shadow off the plate within 1 of its day pixel dimmed",
          all(abs(a - b) <= 1 for a, b in zip(px(nit, sx, sy), dimmed(px(day, sx, sy)))) and px(day, sx, sy) !=
          preview.GROUND[:3], f"{px(day, sx, sy)} -> {px(nit, sx, sy)}")
    for name, (x, y), under in (("the glow pass", (50, 50), PLATE_RGB),
                                ("the glow animation", (100, 105), PLATE_RGB)):
        adds_day = tuple(a - b for a, b in zip(px(day, x, y), under))
        adds_night = tuple(a - b for a, b in zip(px(nit, x, y), dimmed(under)))
        check(f"{name} adds by night what it adds by day {adds_day}", adds_day == adds_night and any(adds_day),
              f"night adds {adds_night}")
    for name, (x, y) in (("the lamp", (143, 143)), ("the beacon", (62, 132))):
        check(f"{name} the same by night as by day", px(nit, x, y) == px(day, x, y),
              f"{px(day, x, y)} -> {px(nit, x, y)}")

    hz = building(os.path.join(out, "building-haze"), haze=True)
    n = haze_px(pack.glow_layer(opened(hz, "working"), opened(hz, "idle")))
    check(f"with haze: pack.glow_layer leaves colour on every clear pixel of the band ({n} of {area(HAZE)})",
          n == area(HAZE))
    mh = preview.Model(hz)
    for (working, night), want in panels.items():
        what = f"{'working' if working else 'idle'} {'at night' if night else 'by day'}"
        check(f"with haze, {what}: pixel for pixel as without it",
              mh.panel("", working, night=night).tobytes() == want.tobytes())
    return rdir, hz


# ---------------------------------------------------------------- the wreck

def haze_wreck(_decl, rdir):
    """write_fixture's edit: each direction's glow render with the haze band (WRECK_HAZE)."""
    for d in rg.DIRS:
        path = os.path.join(rdir, contract.named(rg.LIT, d) + ".png")
        hazed(Image.open(path).convert("RGBA"), WRECK_HAZE).save(path)


def test_wreck(out):
    print("wreck")
    src = rg.write_fixture(os.path.join(out, "wreck-glow"))
    bare = rg.write_fixture(os.path.join(out, "wreck-bare"), rg.drop_glow)
    hz = rg.write_fixture(os.path.join(out, "wreck-haze"), haze_wreck)
    m, mb, mh = preview.Model(src), preview.Model(bare), preview.Model(hz)
    for d in rg.DIRS:
        lit = Image.open(os.path.join(hz, contract.named(rg.LIT, d) + ".png")).convert("RGBA")
        n = haze_px(pack.glow_layer(lit, rg.wreck(d)))
        check(f"{d}: with haze, pack.glow_layer leaves colour on every clear pixel of the band ({n} of "
              f"{area(WRECK_HAZE)})", n == area(WRECK_HAZE))
        for night in (False, True):
            check(f"{d}: with haze, the wreck panel {'at night' if night else 'by day'} pixel for pixel as without it",
                  mh.wreck(d, night=night).tobytes() == m.wreck(d, night=night).tobytes())
        day, plain, nit = m.wreck(d), mb.wreck(d), m.wreck(d, night=True)
        glow = pack.roll(pack.glow_layer(rg.lit(d), rg.wreck(d)))[0]
        check(f"{d}: by day, the wreck without its glow plus the glow, pixel for pixel",
              day.tobytes() == pack.add_light(plain, glow).tobytes())
        clear = glow.getchannel("A").point(lambda v: 255 if v == 0 else 0)
        r, g, b, a = ImageChops.difference(day, plain).split()
        most = ImageChops.lighter(ImageChops.lighter(ImageChops.lighter(r, g), b), a)
        check(f"{d}: by day, the same pixels wherever the glow is clear",
              ImageChops.multiply(most, clear).getbbox() is None)
        x0, y0, x1, y1 = rg.core_box(d)
        brighter = all(sum(day.getpixel((x, y))[:3]) > sum(plain.getpixel((x, y))[:3])
                       for x in range(x0, x1) for y in range(y0, y1))
        check(f"{d}: by day, every core pixel brighter than without the glow", brighter)
        check(f"{d}: at night, the ground dimmed", nit.getpixel((2, 2))[:3] == dimmed(preview.GROUND[:3]),
              f"{nit.getpixel((2, 2))}")
        dx, dy = rg.DEBRIS[0] + 2, rg.DEBRIS[3] - 3
        check(f"{d}: at night, the debris dimmed", nit.getpixel((dx, dy))[:3] == dimmed(plain.getpixel((dx, dy))[:3]),
              f"{plain.getpixel((dx, dy))} -> {nit.getpixel((dx, dy))}")
        floor = dimmed(pack.roll(Image.new("RGBA", (1, 1), rg.FLOOR_RGB + (255,)))[0].getpixel((0, 0))[:3])
        full = all(nit.getpixel((x, y))[:3] == tuple(min(255, f + g) for f, g in zip(floor, glow.getpixel((x, y))[:3]))
                   for x in range(x0, x1) for y in range(y0, y1))
        check(f"{d}: at night, every core pixel the dimmed floor plus the glow as by day", full)
    return src, bare


# ---------------------------------------------------------------- the sheet

def cell(sheet, r, c, pw, ph):
    """Row r, column c's place on a sheet of pw x ph panels (each with its label strip)."""
    x, y = preview.PAD + c * (pw + preview.PAD), preview.PAD + r * (ph + preview.LABEL + preview.PAD)
    return sheet.crop((x, y, x + pw, y + ph + preview.LABEL))


def tall(rows, ph):
    """A sheet's height: rows of ph px panels, each with its label strip."""
    return preview.PAD + rows * (ph + preview.LABEL + preview.PAD)


def body(im):
    return im.crop((0, preview.LABEL, im.width, im.height))


def placed(art, pw, ph, decl, night, d=""):
    """A panel as the sheet shows it: placed, gridded, over the gap's colour (the label strip's)."""
    im = preview.place(art, (pw, ph), (pw / 2, ph / 2), by=K if night else 1)
    preview.grid(im, (pw / 2, ph / 2), contract.footprint_in(decl, d), float(decl["rig"]["px_per_tile"]))
    return Image.alpha_composite(Image.new("RGBA", im.size, preview.GAP), im)


def sheet_of(rdir, png, *extra):
    code, text = run([sys.executable, os.path.join(TOOLS, "preview.py"), rdir, png, *extra])
    return code, text, (Image.open(png).convert("RGBA") if code == 0 else None)


def empty(im):
    return im.getcolors(1) is not None and im.getcolors(1)[0][1] == preview.GAP


def night_places(s, m, cols, pw, ph, wreck_col=None):
    """The places of every direction's night row in s (cols of them) that are not the panel at night,
    placed and gridded; wreck_col: the wreck's place, when the model has one."""
    bad = []
    for i, d in enumerate(m.directions):
        for c in range(cols):
            if c == wreck_col:
                want = m.wreck(d, night=True)
            else:
                want = m.panel(d, c == 1, night=True)
            if body(cell(s, 2 * i + 1, c, pw, ph)).tobytes() != placed(want, pw, ph, m.decl, True, d).tobytes():
                bad.append(f"{d or 'one'} place {c + 1}")
    return bad


def test_sheet(out, building_dir, hazy, src, bare):
    print("sheet")
    m = preview.Model(building_dir)
    pw = ph = CANVAS[0] + 2 * preview.PAD
    wide = preview.PAD + 2 * (pw + preview.PAD)
    code, text, s = sheet_of(building_dir, os.path.join(out, "night-building.png"))
    check("by default, the building: a night row under the day row, two panels wide",
          code == 0 and s.size == (wide, tall(2, ph)), f"exit {code}, {s.size if s else text[-300:]}")
    if s:
        bad = night_places(s, m, 2, pw, ph)
        check("by default, the building: each night place the panel at night (idle, working), placed, gridded",
              not bad, ", ".join(bad))
    code, text, n = sheet_of(building_dir, os.path.join(out, "building-night-flag.png"), "--night")
    check("--night: the same bytes as the default", code == 0 and s is not None and n.tobytes() == s.tobytes(),
          f"exit {code}: {text[-300:]}")
    code, text, s = sheet_of(building_dir, os.path.join(out, "building-day.png"), "--day-only")
    check("--day-only, the building: one row, two panels wide (no night row)",
          code == 0 and s.size == (wide, tall(1, ph)), f"exit {code}, {s.size if s else text[-300:]}")
    adopted = os.path.join(out, "adopted.png")
    plate_im().save(adopted)
    code, text, s = sheet_of(building_dir, os.path.join(out, "night-building-adopted.png"), "--adopted", adopted)
    check("by default with --adopted: the adopted place in the night row empty, the others filled",
          code == 0 and empty(cell(s, 1, 0, pw, ph)) and not empty(cell(s, 1, 1, pw, ph))
          and not empty(cell(s, 1, 2, pw, ph)), f"exit {code}: {text[-300:]}")
    code, text, _ = sheet_of(building_dir, os.path.join(out, "x.png"), "--night", "--day-only")
    check("--night with --day-only refused", code != 0 and "cannot go together" in text, f"exit {code}: {text[-200:]}")
    gif = [sys.executable, os.path.join(TOOLS, "preview.py"), building_dir]
    code, text = run(gif + [os.path.join(out, "x.gif"), "--gif", "bar", "--speed", "1", "--night"])
    check("--night with --gif refused", code != 0 and "--night is for the sheet" in text, f"exit {code}: {text[-200:]}")
    code, text = run(gif + [os.path.join(out, "bar.gif"), "--gif", "bar", "--speed", "1"])
    code2, text2 = run(gif + [os.path.join(out, "bar-day-only.gif"), "--gif", "bar", "--speed", "1", "--day-only"])
    check("--gif by default and with --day-only: exit 0, the same bytes",
          code == code2 == 0 and same_bytes(os.path.join(out, "bar.gif"), os.path.join(out, "bar-day-only.gif")),
          f"exit {code}, {code2}: {(text + text2)[-300:]}")
    hazy_png = os.path.join(out, "night-building-haze.png")
    code, text, _ = sheet_of(hazy, hazy_png)
    check("with haze, the building's sheet by default (night rows and all): the same bytes as without it",
          code == 0 and same_bytes(os.path.join(out, "night-building.png"), hazy_png), f"exit {code}: {text[-300:]}")
    code, text = run([sys.executable, os.path.join(TOOLS, "preview.py"), hazy, os.path.join(out, "bar-haze.gif"),
                      "--gif", "bar", "--speed", "1"])
    check("with haze, the building's --gif of the bar: the same bytes as without it",
          code == 0 and same_bytes(os.path.join(out, "bar.gif"), os.path.join(out, "bar-haze.gif")),
          f"exit {code}: {text[-300:]}")

    pw = ph = rg.CANVAS[0] + 2 * preview.PAD
    for label, rdir in (("the wreck-glow fixture", src), ("the fixture without its glow", bare)):
        w = preview.Model(rdir)
        stem = "night-wreck" if rdir == src else "night-wreck-bare"
        code, text, s = sheet_of(rdir, os.path.join(out, stem + ".png"))
        check(f"{label}, by default: 8 rows (a night row under each direction's)",
              code == 0 and s.size[1] == tall(8, ph), f"exit {code}: {text[-300:]}")
        if s:
            bad = night_places(s, w, 3, pw, ph, wreck_col=2)
            check(f"{label}, by default: every night place the panel at night (idle, working, wreck), placed, "
                  "gridded", not bad, ", ".join(bad))
            if rdir == src:
                for i, d in enumerate(rg.DIRS):
                    check(f"{label}, {d}: day row's wreck place the wreck with its glow, placed, gridded",
                          body(cell(s, 2 * i, 2, pw, ph)).tobytes()
                          == placed(w.wreck(d), pw, ph, w.decl, False, d).tobytes())
        day_stem = "wreck-day-only" if rdir == src else "wreck-bare-day-only"
        code, text, s = sheet_of(rdir, os.path.join(out, day_stem + ".png"), "--day-only")
        check(f"{label}, --day-only: 4 rows (no night row)", code == 0 and s.size[1] == tall(4, ph),
              f"exit {code}: {text[-300:]}")
        if s and rdir == src:
            check(f"{label}, --day-only: each wreck place the wreck with its glow",
                  all(body(cell(s, i, 2, pw, ph)).tobytes() == placed(w.wreck(d), pw, ph, w.decl, False, d).tobytes()
                      for i, d in enumerate(rg.DIRS)))


# ---------------------------------------------------------------- identity

def baseline_tools(rev, out):
    d = os.path.join(out, f"baseline-{rev}")
    os.makedirs(d, exist_ok=True)
    top = subprocess.run(["git", "-C", TOOLS, "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                         check=True).stdout.strip()
    rel = os.path.relpath(TOOLS, top)
    for f in ("contract.py", "pack.py", "preview.py"):
        body_ = subprocess.run(["git", "-C", top, "show", f"{rev}:{rel}/{f}"], capture_output=True, check=True).stdout
        with open(os.path.join(d, f), "wb") as fh:
            fh.write(body_)
    return d


def darker(mine, theirs):
    """(brighter, darker, most): of two same-sized sheets, the pixels where mine is brighter than
    theirs in any channel, those where it is darker in some and brighter in none, and the most a
    channel of mine falls under theirs."""
    a, b = Image.open(mine).convert("RGBA"), Image.open(theirs).convert("RGBA")
    up, down = ImageChops.subtract(a, b), ImageChops.subtract(b, a)
    brighter = sum(1 for p in up.get_flattened_data() if any(p))
    fell = sum(1 for p, q in zip(down.get_flattened_data(), up.get_flattened_data()) if any(p) and not any(q))
    return brighter, fell, max(hi for _, hi in down.getextrema())


def compare(label, rdir, out, base, gif_of=None, plain="same"):
    """This tree's preview.py and the baseline's on rdir: the sheet (this tree's with --day-only), and a
    GIF of gif_of (no flag in either), byte for byte as the baseline's with its haze cleared
    (baseline_preview). The baseline's as it is: plain "same", byte for byte as well; "haze", the
    sheet not (the fixture's haze, which it draws); "render", the sheet nowhere brighter (listed)."""
    jobs = [("preview.png", ["--day-only"])]
    if gif_of:
        jobs.append(("anim.gif", ["--gif", gif_of, "--speed", "1"]))
    for name, extra in jobs:
        res = {}
        for who in ("mine", "base", "base-plain"):
            o = os.path.join(out, f"{label}-{who}")
            os.makedirs(o, exist_ok=True)
            args = [rdir, os.path.join(o, name), *[f for f in extra if who == "mine" or f != "--day-only"]]
            if who == "mine":
                cmd = [sys.executable, os.path.join(TOOLS, "preview.py"), *args]
            elif who == "base":
                cmd = baseline_preview.command(base, args)
            else:
                cmd = [sys.executable, os.path.join(base, "preview.py"), *args]
            code, text = run(cmd)
            res[who] = (code, os.path.join(o, name), text)
        (c1, f1, t1), (c2, f2, t2), (c3, f3, _) = res["mine"], res["base"], res["base-plain"]
        mine = " (this tree's with --day-only)" if "--day-only" in extra else ""
        check(f"{label}: preview.py's {name}{mine} byte for byte as the baseline's with its haze cleared "
              f"(exit {c1}, baseline {c2})", c1 == c2 and (c1 != 0 or same_bytes(f1, f2)), (t1 + t2)[-300:])
        if c1 != 0 or c3 != 0:
            check(f"{label}: preview.py's {name} and the baseline's as it is exit 0 ({c1}, {c3})", False)
        elif plain == "same":
            check(f"{label}: preview.py's {name}{mine} byte for byte as the baseline's as it is too (no haze)",
                  same_bytes(f1, f3))
        elif name != "preview.png":
            pass                        # a GIF's palette is its own: held to the cleared baseline's only
        elif plain == "haze":
            check(f"{label}: preview.py's {name}{mine} not as the baseline's as it is (which draws the haze)",
                  not same_bytes(f1, f3))
        else:
            up, fell, most = darker(f1, f3)
            check(f"{label}: preview.py's {name}{mine} nowhere brighter than the baseline's as it is", up == 0,
                  f"{up} px brighter")
            print(f"  info  {label}: against the baseline's as it is, {fell} px darker, by {most} at most "
                  f"in a channel (the haze cleared)")
        if c1 == 0 and "--day-only" in extra:
            ROWS[label] = Image.open(f1).size[1]


def test_identity(out, base, renders, building_dir, hazy, bare):
    print("identity")
    compare("building", building_dir, out, base, "bar")
    compare("building-haze", hazy, out, base, plain="haze")
    compare("wreck-bare", bare, out, base)
    for r in renders:
        label = os.path.basename(os.path.normpath(r))
        rdir = os.path.join(r, "renders")
        anims = contract.load(rdir)["animations"]
        compare(label, rdir, out, base, anims[0]["name"] if anims else None, plain="render")
        night = os.path.join(out, f"night-{label}.png")
        code, text = run([sys.executable, os.path.join(TOOLS, "preview.py"), rdir, night])
        n = len(contract.DIRECTIONS[contract.load(rdir)["directions"]])
        day_h = ROWS.get(label)
        # the --day-only sheet is PAD + n rows of (panel + PAD); the default has 2n of them
        want = day_h and preview.PAD + 2 * (day_h - preview.PAD)
        got = Image.open(night).size[1] if code == 0 else None
        check(f"{label}: no flag, exit 0 and {2 * n} rows (twice --day-only's {n})", code == 0 and got == want,
              f"exit {code}, {got} px high, want {want}: {text[-300:]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out")
    ap.add_argument("--baseline", metavar="GIT_REV")
    ap.add_argument("--renders", nargs="+", default=[], metavar="RENDER_OUT")
    a = ap.parse_args()
    if a.renders and not a.baseline:
        ap.error("--renders goes with --baseline")
    out = a.out or tempfile.mkdtemp(prefix="preview-night-test-")
    os.makedirs(out, exist_ok=True)
    print(f"writing under {out}")
    base = baseline_tools(a.baseline, out) if a.baseline else None
    building_dir, hazy = test_building(out)
    src, bare = test_wreck(out)
    test_sheet(out, building_dir, hazy, src, bare)
    if base:
        test_identity(out, base, [os.path.abspath(r) for r in a.renders], building_dir, hazy, bare)
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
