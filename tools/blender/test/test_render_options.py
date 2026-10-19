#!/usr/bin/env python3
"""render.sh --collide, render.json's frame_sequence and hold, and the footprint cut, held to their docs.

  python3 tools/blender/test/test_render_options.py <box-out> [--radiant <radiant-out>] [--out <dir>]

<box-out> is render.sh's <out-dir> for the test box (test/box.py, or test/collide_box.py, which
is box.py with a --collide); <radiant-out> the same for test/radiant_box.py, for a glow playing
its plate layer's sequence (skipped without it). Nothing is rendered here: copies of their
renders, with render.json edited, are packed by pack.py and drawn by preview.py, and
render.sh's collide step is run with a stand-in Blender, a shell script that prints the
COLLIDE lines it is given. The collide step on the box itself takes Blender: collide_box.py's
docstring has the two runs. Everything is written under --out (default <box-out>/options-test)
and kept.

Exits 0 when every case below comes out as listed, 1 naming those that do not.

  contract   render.json's new fields refused when wrong, each naming its field: a
             frame_sequence with a frame outside 1..frames, empty, or over 255 entries; a hold
             without entries, with a key it does not know, or over 255 entries written out;
             both at once; either on a glow animation; a cut naming N, a face twice, or not
             a list. Accepted: 255 entries exactly, a hold with and without each, cut [].
  sequence   hold {frame 1, entries 6, each 2} on the slider: meta.json's slider-<direction>
             carries frame_sequence [1,1,2,2,3,3,4,4,1,1,1,1,1,1], checks slider_sequence
             entries 14, unused []; every sheet byte for byte as packed without it, and the
             rest of meta.json the same. frame_sequence [2,2,1]: entries 3, unused [3, 4].
             pack.py exits non-zero on frame_sequence [5]. preview.py --gif at
             animation_speed 0.25 (15 fps): the hold's GIF is five frames (1, 2, 3, 4, then 1
             held for six entries), held [130, 140, 130, 130, 400] ms, its first and last
             frame the same picture; without it, four frames held [70, 60, 70, 70].
             With <radiant-out>: a hold on "window" is carried by window-glow and
             column-glow too.
  cut        cut [E, W, S] on the box's own renders: the plate's faint haze one pixel past
             its edges (alpha 3) cleared, so base is 2 tiles + the 1 px rims wide (130 px,
             134 uncut) and half_width_tiles and footprint_rows_tiles stay 1.0; cut_px lists
             the renders it touched, never a shadow; the shadow sheet byte for byte as
             uncut. A block painted past the east and south edges of the plate and the still:
             uncut, half_width_tiles and footprint_rows_tiles over 1; cut, base byte for byte
             as the box's own cut. cut [E] alone: east block gone, south block kept. A block
             painted on the shadow past the edges survives the cut. preview.py draws the
             renders cut as pack.py does (the painted plate, cut, draws as the box's own,
             cut). A slide's tracked part, with a copy of it riding across the east edge,
             is never cut: its measured path cut as uncut (and the cut would have moved
             its centroid). cut_mask: an edge across a pixel keeps the share inside (128
             for a half);
             a footprint turned east swaps its width and height.
  collide    render.sh --collide with a stand-in Blender: a clash line and "clashes 1" ->
             exit 1, "collide: FAIL", render.done "exit 1", nothing rendered; "clashes 0" ->
             "collide: PASS" and the render goes ahead (the stand-in then fails it); nothing
             printed -> FAIL ("printed no COLLIDE line"), nothing rendered; a run without
             --collide clears the last run's collide.log and collide/. A "COLLIDE meant
             <a> x <b>" line with "clashes 1": FAIL alone, PASS with a --collide-allow
             naming the whole pair line (1 allowed, and the render goes ahead), a second
             pattern that matched nothing printed as such; a pattern that is not a regular
             expression, or --collide-allow without --collide: exit 2.
"""
import argparse
import copy
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import contract  # noqa: E402
import pack  # noqa: E402
import preview  # noqa: E402

FAILED = []


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(f"{case}: {detail}")


def renders_copy(src, dst, edit=None):
    """A copy of a render directory, its render.json edited by edit(decl)."""
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    if edit:
        path = os.path.join(dst, contract.FILE)
        with open(path) as f:
            decl = json.load(f)
        edit(decl)
        with open(path, "w") as f:
            json.dump(decl, f, indent=1)
    return dst


def run(cmd, env=None):
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return p.returncode, p.stdout + p.stderr


def packed(src, out):
    """pack.py src -> out: its exit code, output and meta.json (None if it wrote none)."""
    if os.path.exists(out):
        shutil.rmtree(out)
    code, text = run([sys.executable, os.path.join(TOOLS, "pack.py"), src, out])
    meta = os.path.join(out, "meta.json")
    return code, text, (json.load(open(meta)) if os.path.isfile(meta) else None)


def same_bytes(a, b):
    with open(a, "rb") as fa, open(b, "rb") as fb:
        return fa.read() == fb.read()


def sheets(d):
    return sorted(f for f in os.listdir(d) if f.endswith(".png"))


def differs(a, b):
    """Whether two images differ in any channel (getbbox alone reads only an RGBA's alpha)."""
    return ImageChops.difference(a.convert("RGBA"), b.convert("RGBA")).getbbox(alpha_only=False) is not None


def gif_frames(path):
    im = Image.open(path)
    out = []
    for i in range(im.n_frames):
        im.seek(i)
        out.append((im.convert("RGB"), im.info["duration"]))
    return out


# ---------------------------------------------------------------- contract

def test_contract(decl0):
    print("contract")

    def case(label, edit, want_field=None):
        d = copy.deepcopy(decl0)
        edit(d)
        try:
            contract.validate(d, "test")
            check(label, want_field is None, "accepted, but should be refused naming " + str(want_field))
        except contract.ContractError as e:
            check(label, want_field is not None and f": {want_field}:" in str(e),
                  f"refused: {e}" if want_field is None else f"refused, not naming {want_field}: {e}")
    slider = "animations[0]"

    def anim(**kw):
        return lambda d: d["animations"][0].update(**kw)
    case("frame_sequence 255 entries accepted", anim(frame_sequence=[1] * 255))
    case("frame_sequence 256 entries refused", anim(frame_sequence=[1] * 256), f"{slider}.frame_sequence")
    case("frame_sequence frame 0 refused", anim(frame_sequence=[0, 1]), f"{slider}.frame_sequence")
    case("frame_sequence frame past frames refused", anim(frame_sequence=[5]), f"{slider}.frame_sequence")
    case("frame_sequence empty refused", anim(frame_sequence=[]), f"{slider}.frame_sequence")
    case("hold accepted", anim(hold=dict(frame=1, entries=6)))
    case("hold with each accepted", anim(hold=dict(frame=4, entries=6, each=3)))
    case("hold without entries refused", anim(hold=dict(frame=1)), f"{slider}.hold")
    case("hold with an unknown key refused", anim(hold=dict(frame=1, entries=2, at=3)), f"{slider}.hold")
    case("hold frame 0 refused", anim(hold=dict(frame=0, entries=2)), f"{slider}.hold.frame")
    case("hold each 0 refused", anim(hold=dict(frame=1, entries=2, each=0)), f"{slider}.hold.each")
    case("hold over 255 written out refused", anim(hold=dict(frame=1, entries=250, each=2)), f"{slider}.hold")
    case("frame_sequence and hold together refused", anim(frame_sequence=[1], hold=dict(frame=1, entries=1)),
         f"{slider}.hold")
    case("cut [] accepted", lambda d: d.update(cut=[]))
    case("cut [E, W, S] accepted", lambda d: d.update(cut=["E", "W", "S"]))
    case("cut N refused", lambda d: d.update(cut=["E", "N"]), "cut")
    case("cut a face twice refused", lambda d: d.update(cut=["E", "E"]), "cut")
    case("cut a string refused", lambda d: d.update(cut="EW"), "cut")

    def glow_with_hold(d):
        d["animations"].append(dict(name="slider-light", frames=4, motion="flow", kind="glow", over="slider",
                                    hold=dict(frame=1, entries=2)))
    case("hold on a glow animation refused", glow_with_hold, "animations[1].hold")


# ---------------------------------------------------------------- sequence

def test_sequence(box, out, radiant):
    print("sequence")
    src = os.path.join(box, "renders")
    base = renders_copy(src, os.path.join(out, "seq-none"))
    code0, text0, meta0 = packed(base, os.path.join(out, "seq-none-sheets"))
    check("the box packs as it is", code0 == 0, text0[-400:])
    dirs = [d for d, _ in contract.DIRECTIONS[json.load(open(os.path.join(src, contract.FILE)))["directions"]]]

    held = renders_copy(src, os.path.join(out, "seq-hold"),
                        lambda d: d["animations"][0].update(hold=dict(frame=1, entries=6, each=2)))
    code, text, meta = packed(held, os.path.join(out, "seq-hold-sheets"))
    check("hold: pack.py exits 0", code == 0, text[-400:])
    want = [1, 1, 2, 2, 3, 3, 4, 4] + [1] * 6
    for d in dirs:
        stem = contract.named("slider", d)
        check(f"hold: meta.json {stem} frame_sequence", meta[stem].get("frame_sequence") == want,
              f"{meta[stem].get('frame_sequence')}")
        got = checks_of(meta, d)["slider_sequence"][0]
        check(f"hold: checks slider_sequence ({d})", got == dict(entries=14, unused=[]), f"{got}")
    same = all(same_bytes(os.path.join(out, "seq-none-sheets", f), os.path.join(out, "seq-hold-sheets", f))
               for f in sheets(os.path.join(out, "seq-none-sheets")))
    check("hold: every sheet byte for byte as without it", same and sheets(os.path.join(out, "seq-none-sheets"))
          == sheets(os.path.join(out, "seq-hold-sheets")))
    stripped = copy.deepcopy(meta)
    for d in dirs:
        stripped[contract.named("slider", d)].pop("frame_sequence")
        checks_of(stripped, d).pop("slider_sequence")
    check("hold: the rest of meta.json as without it", stripped == meta0)

    seqd = renders_copy(src, os.path.join(out, "seq-list"),
                        lambda d: d["animations"][0].update(frame_sequence=[2, 2, 1]))
    code, text, meta = packed(seqd, os.path.join(out, "seq-list-sheets"))
    got = checks_of(meta, dirs[0])["slider_sequence"][0] if meta else None
    check("frame_sequence [2,2,1]: entries 3, unused [3, 4]", code == 0 and got == dict(entries=3, unused=[3, 4]),
          f"exit {code}, {got}")

    bad = renders_copy(src, os.path.join(out, "seq-bad"), lambda d: d["animations"][0].update(frame_sequence=[5]))
    code, text, _ = packed(bad, os.path.join(out, "seq-bad-sheets"))
    check("frame_sequence [5]: pack.py refuses it", code != 0 and "frame_sequence" in text,
          f"exit {code}: {text[-300:]}")

    fps = 60 * 0.25
    for label, rdir, order in (("hold", held, [k - 1 for k in want]), ("no sequence", base, [0, 1, 2, 3])):
        gif = os.path.join(out, f"slider-{label.replace(' ', '-')}.gif")
        code, text = run([sys.executable, os.path.join(TOOLS, "preview.py"), rdir, gif, "--gif", "slider",
                          "--speed", "0.25"])
        runs = [e for e in range(len(order)) if e == 0 or order[e] != order[e - 1]] + [len(order)]
        ticks = [round(100 * e / fps) for e in runs]
        durations = [10 * (b - a) for a, b in zip(ticks, ticks[1:])]
        frames = gif_frames(gif) if code == 0 else []
        check(f"preview --gif, {label}: {len(durations)} frames held {durations} ms",
              [ms for _, ms in frames] == durations, f"exit {code}, got {[ms for _, ms in frames]}; {text[-300:]}")
        if label == "hold" and frames:
            check("preview --gif, hold: its last frame (the hold) is its first (frame 1)",
                  not differs(frames[0][0], frames[-1][0]))

    if radiant:
        rsrc = os.path.join(radiant, "renders")
        rd = renders_copy(rsrc, os.path.join(out, "seq-radiant"),
                          lambda d: next(a for a in d["animations"] if a["name"] == "window").update(
                              hold=dict(frame=1, entries=4)))
        code, text, meta = packed(rd, os.path.join(out, "seq-radiant-sheets"))
        want_r = list(range(1, 9)) + [1] * 4
        rdirs = [d for d, _ in contract.DIRECTIONS[json.load(open(os.path.join(rd, contract.FILE)))["directions"]]]
        ok = code == 0 and all(meta[contract.named(n, d)].get("frame_sequence") == want_r
                               for n in ("window", "window-glow", "column-glow") for d in rdirs)
        check("radiant: a hold on window is carried by window-glow and column-glow", ok, text[-400:])


# ---------------------------------------------------------------- cut

def paint(rdir, stems, boxes):
    for stem in stems:
        path = os.path.join(rdir, stem + ".png")
        im = Image.open(path).convert("RGBA")
        draw = ImageDraw.Draw(im)
        for b in boxes:
            draw.rectangle(b, fill=(200, 60, 40, 255))
        im.save(path)


def checks_of(meta, d):
    return meta["checks"][d] if d else meta["checks"]


def test_cut(box, out):
    print("cut")
    src = os.path.join(box, "renders")
    decl = json.load(open(os.path.join(src, contract.FILE)))
    dirs = [d for d, _ in contract.DIRECTIONS[decl["directions"]]]
    ppt = decl["rig"]["px_per_tile"]
    cw, ch = decl["canvas"]
    every = ["E", "W", "S"]

    _, _, meta0 = packed(renders_copy(src, os.path.join(out, "cut-none")), os.path.join(out, "cut-none-sheets"))
    own = renders_copy(src, os.path.join(out, "cut-own"), lambda d: d.update(cut=every))
    code, text, meta = packed(own, os.path.join(out, "cut-own-sheets"))
    check("cut [E, W, S], the box's own renders: pack.py exits 0", code == 0, text[-400:])
    for d in dirs:
        fw, fh = contract.footprint_in(decl, d)
        c, b = checks_of(meta, d), contract.named("base", d)
        check(f"cut own ({d}): base {fw * ppt + 2} px wide (uncut {meta0[b]['size'][0]})",
              meta[b]["size"][0] == fw * ppt + 2 and meta0[b]["size"][0] > fw * ppt + 2,
              f"cut {meta[b]['size']}, uncut {meta0[b]['size']}")
        check(f"cut own ({d}): half_width_tiles and footprint_rows_tiles {fw / 2}, {fh / 2}",
              c["half_width_tiles"][0] == fw / 2 and c["footprint_rows_tiles"][0] == fh / 2,
              f"{c['half_width_tiles'][0]}, {c['footprint_rows_tiles'][0]}")
        cut_px = c.get("cut_px", [None])[0]
        check(f"cut own ({d}): cut_px names the plate and no shadow",
              isinstance(cut_px, dict) and contract.named("idle", d) in cut_px
              and not any(k.startswith("shadow") for k in cut_px), f"{cut_px}")
        sh = contract.named("shadow", d) + ".png"
        check(f"cut own ({d}): the shadow sheet as uncut",
              same_bytes(os.path.join(out, "cut-none-sheets", sh), os.path.join(out, "cut-own-sheets", sh)))

    # a block past the east edge and one below the south edge, on the plate and the still
    def blocks(d):
        fw, fh = contract.footprint_in(decl, d)
        right, bottom = cw // 2 + fw * ppt // 2, ch // 2 + fh * ppt // 2
        return [(right, ch // 2 - 10, right + 9, ch // 2), (cw // 2 - 5, bottom, cw // 2 + 4, bottom + 9)]
    for name, faces in (("cut-paint-none", None), ("cut-paint", every), ("cut-paint-east", ["E"])):
        rd = renders_copy(src, os.path.join(out, name), (lambda d, f=faces: d.update(cut=f)) if faces else None)
        for d in dirs:
            paint(rd, [contract.named("idle", d), contract.named("still", d)], blocks(d))
    _, _, mp0 = packed(os.path.join(out, "cut-paint-none"), os.path.join(out, "cut-paint-none-sheets"))
    code, text, mp = packed(os.path.join(out, "cut-paint"), os.path.join(out, "cut-paint-sheets"))
    _, _, me = packed(os.path.join(out, "cut-paint-east"), os.path.join(out, "cut-paint-east-sheets"))
    for d in dirs:
        fw, fh = contract.footprint_in(decl, d)
        u, c, e = checks_of(mp0, d), checks_of(mp, d), checks_of(me, d)
        check(f"painted, uncut ({d}): half width and rows past the footprint",
              u["half_width_tiles"][0] > fw / 2 and u["footprint_rows_tiles"][0] > fh / 2,
              f"{u['half_width_tiles'][0]}, {u['footprint_rows_tiles'][0]}")
        b = contract.named("base", d) + ".png"
        check(f"painted, cut ({d}): base byte for byte as the box's own, cut",
              code == 0 and same_bytes(os.path.join(out, "cut-paint-sheets", b),
                                       os.path.join(out, "cut-own-sheets", b)),
              text[-300:])
        check(f"painted, cut ({d}): half width and rows on the footprint",
              c["half_width_tiles"][0] == fw / 2 and c["footprint_rows_tiles"][0] == fh / 2)
        check(f"painted, cut [E] ({d}): east block gone, south block kept",
              e["half_width_tiles"][0] == fw / 2 and e["footprint_rows_tiles"][0] > fh / 2,
              f"{e['half_width_tiles'][0]}, {e['footprint_rows_tiles'][0]}")

    sh = renders_copy(src, os.path.join(out, "cut-shadow"), lambda d: d.update(cut=every))
    for d in dirs:
        paint(sh, [contract.named("shadow", d)], blocks(d))
    _, _, ms = packed(sh, os.path.join(out, "cut-shadow-sheets"))
    for d in dirs:
        s = contract.named("shadow", d) + ".png"
        a = Image.open(os.path.join(out, "cut-shadow-sheets", s)).getchannel("A")
        a0 = Image.open(os.path.join(out, "cut-own-sheets", s)).getchannel("A")
        check(f"painted shadow, cut ({d}): the block survives (the shadow is never cut)",
              ms is not None and differs(a, a0))

    for d in dirs:
        same = True
        for working in (False, True):
            p1 = preview.Model(os.path.join(out, "cut-paint")).panel(d, working)
            p2 = preview.Model(own).panel(d, working)
            same &= not differs(p1, p2)
        differ = differs(preview.Model(os.path.join(out, "cut-paint-none")).panel(d, False),
                         preview.Model(os.path.join(out, "cut-none")).panel(d, False))
        check(f"preview ({d}): the painted plate, cut, draws as the box's own, cut (uncut, it does not)",
              same and differ, f"cut alike: {same}; uncut differs: {differ}")

    # a slide's tracked part is measured, never drawn: the cut leaves it whole. The slider tracked
    # as "part", whose frames carry a second copy of it riding with it across the east edge
    def tracked(decl_, faces):
        decl_["animations"][0]["track"] = "part"
        if faces:
            decl_["cut"] = faces
    moved = False
    for name, faces in (("cut-track-none", None), ("cut-track", every)):
        rd = renders_copy(src, os.path.join(out, name), lambda d_, f=faces: tracked(d_, f))
        for d in dirs:
            fw, _ = contract.footprint_in(decl, d)
            right = cw // 2 + fw * ppt // 2
            first = Image.open(os.path.join(rd, contract.frame("slider", 0, d) + ".png")).convert("RGBA")
            dx = right + 3 - pack.clean(first).getbbox()[2]     # the part's own extent, past the haze
            for f in range(decl["animations"][0]["frames"]):
                fr = Image.open(os.path.join(rd, contract.frame("slider", f, d) + ".png")).convert("RGBA")
                part = fr.copy()
                part.alpha_composite(fr, dest=(dx, 0))
                part.save(os.path.join(rd, contract.track_frame("slider", "part", f, d) + ".png"))
                if faces and not moved:
                    c0 = pack.centroid(pack.clean(part.copy()))
                    c1 = pack.centroid(pack.clean(pack.cut(part, pack.cut_mask(json.load(
                        open(os.path.join(rd, contract.FILE))), d))[0]))
                    moved = abs(c0[0] - c1[0]) > 0.5
    _, _, mt0 = packed(os.path.join(out, "cut-track-none"), os.path.join(out, "cut-track-none-sheets"))
    code, text, mt = packed(os.path.join(out, "cut-track"), os.path.join(out, "cut-track-sheets"))
    check("tracked part: the cut would move its centroid (so the case below means something)", moved)
    for d in dirs:
        p0 = checks_of(mt0, d)["slider_path_px"] if mt0 else {}
        p1 = checks_of(mt, d)["slider_path_px"] if mt else {}
        check(f"tracked part, cut ({d}): never cut, its measured path as uncut",
              code == 0 and p1.get("tracked") == "part" and p1.get("measured") == p0.get("measured"),
              f"exit {code}, uncut {p0.get('measured')}, cut {p1.get('measured')}: {text[-300:]}")

    half = dict(canvas=[193, 192], footprint=[2, 2], directions="one", rig=dict(px_per_tile=64, elevation=60),
                cut=["E", "W"])
    m = pack.cut_mask(half, "")
    cols = [m.getpixel((x, 96)) for x in (31, 32, 33, 159, 160, 161)]
    check("cut_mask: an edge across a pixel keeps the share inside", cols == [0, 128, 255, 255, 128, 0], f"{cols}")
    turned = dict(canvas=[256, 256], footprint=[3, 2], directions="four", rig=dict(px_per_tile=64, elevation=60),
                  cut=["E", "W", "S"])
    m = pack.cut_mask(turned, "east")           # 2 wide, 3 deep turned east
    got = ([m.getpixel((x, 100)) for x in (63, 64, 191, 192)], [m.getpixel((128, y)) for y in (223, 224)])
    check("cut_mask: a footprint turned east swaps its width and height", got == ([0, 255, 255, 0], [255, 0]),
          f"{got}")


# ---------------------------------------------------------------- collide

STAND_IN = """#!/bin/sh
# a stand-in Blender: with --collide prints $FAKE_COLLIDE; any other run fails, rendering nothing
for a in "$@"; do
  if [ "$a" = --collide ]; then printf '%b' "$FAKE_COLLIDE"; exit 0; fi
done
echo "stand-in Blender: renders nothing" >&2
exit 3
"""


def test_collide(out):
    print("collide (render.sh, a stand-in Blender)")
    d = os.path.join(out, "collide")
    if os.path.exists(d):
        shutil.rmtree(d)                    # each case's "nothing rendered" reads a fresh directory
    os.makedirs(d)
    blender = os.path.join(d, "blender")
    with open(blender, "w") as f:
        f.write(STAND_IN)
    os.chmod(blender, 0o755)
    model = os.path.join(HERE, "box.py")

    def render(name, printed, *flags):
        o = os.path.join(d, name)
        env = dict(os.environ, BLENDER=blender, SAE_BLENDER_DEVICE="CPU", FAKE_COLLIDE=printed)
        code, text = run(["bash", os.path.join(TOOLS, "render.sh"), model, o, *flags], env)
        done = open(os.path.join(o, "render.done")).read().strip() if os.path.isfile(os.path.join(o, "render.done")) \
            else None
        return o, code, text, done
    o, code, text, done = render("clash", "COLLIDE slider x stop: frames [3]\\nCOLLIDE clashes 1\\n", "--collide")
    check("a clash: exit 1, collide: FAIL, render.done exit 1, nothing rendered",
          code == 1 and "collide: FAIL" in text and done == "exit 1"
          and not os.path.exists(os.path.join(o, "blender.log")) and not os.path.exists(os.path.join(o, "renders")),
          f"exit {code}, done {done!r}: {text[-400:]}")
    check("a clash: the clash line printed", "COLLIDE slider x stop" in text, text[-400:])
    o2, code, text, done = render("clean", "COLLIDE clashes 0\\n", "--collide")
    check("no clash: collide: PASS, and the render goes ahead",
          "collide: PASS" in text and os.path.isfile(os.path.join(o2, "blender.log")) and done == "exit 1",
          f"exit {code}, done {done!r}: {text[-400:]}")
    o3, code, text, done = render("silent", "", "--collide")
    check("nothing printed: collide: FAIL (no COLLIDE line), nothing rendered",
          code == 1 and "printed no COLLIDE line" in text and not os.path.exists(os.path.join(o3, "blender.log")),
          f"exit {code}: {text[-400:]}")
    had = os.path.isfile(os.path.join(o, "collide.log")) and os.path.isdir(os.path.join(o, "collide"))
    _, code, text, _ = render("clash", "")
    check("a run without --collide clears the last one's collide.log and collide/",
          had and not os.path.exists(os.path.join(o, "collide.log")) and not os.path.exists(os.path.join(o, "collide"))
          and "collide:" not in text, f"before: {had}; {text[-300:]}")
    meant = "COLLIDE meant slider x roof: frames [0]\\nCOLLIDE clashes 1\\n"
    o4, code, text, _ = render("meant", meant, "--collide")
    check("a meant contact, no --collide-allow: FAIL, nothing rendered",
          code == 1 and "collide: FAIL" in text and not os.path.exists(os.path.join(o4, "blender.log")), text[-400:])
    # the pattern names the whole pair line after "COLLIDE ", as --collide-allow's rule has it
    whole = r"meant slider x roof: frames \[0\]"
    o5, code, text, _ = render("allowed", meant, "--collide", "--collide-allow", whole, "--collide-allow", "no such")
    check(f"a meant contact, --collide-allow {whole!r}: PASS, 1 allowed, the render goes ahead",
          "collide: PASS" in text and "1 pair line(s) allowed" in text
          and os.path.isfile(os.path.join(o5, "blender.log")), text[-400:])
    check("an allow pattern that matched nothing is printed", "--collide-allow 'no such' matched no pair line" in text,
          text[-400:])
    o6, code, text, _ = render("bad-pattern", meant, "--collide", "--collide-allow", "(")
    check("--collide-allow '(': exit 2, nothing rendered",
          code == 2 and "not a regular expression" in text and not os.path.exists(os.path.join(o6, "blender.log")),
          f"exit {code}: {text[-300:]}")
    _, code, text, _ = render("lone-allow", meant, "--collide-allow", "x")
    check("--collide-allow without --collide: exit 2", code == 2 and "goes with --collide" in text,
          f"exit {code}: {text[-300:]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("box")
    ap.add_argument("--radiant")
    ap.add_argument("--out")
    a = ap.parse_args()
    out = a.out or os.path.join(a.box, "options-test")
    os.makedirs(out, exist_ok=True)
    test_contract(json.load(open(os.path.join(a.box, "renders", contract.FILE))))
    test_sequence(a.box, out, a.radiant)
    test_cut(a.box, out)
    test_collide(out)
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
