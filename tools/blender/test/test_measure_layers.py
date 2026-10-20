#!/usr/bin/env python3
"""measure.py's layers_alone, light and pack_checks figures, held to their docs.

  python3 tools/blender/test/test_measure_layers.py --out <dir>

Nothing is rendered: small sheets are drawn here and written under --out (kept), and measure.py
is run on them. Exits 0 when every case below comes out as listed, 1 naming those that do not.

  changed      two frames: a pixel 8 apart in one channel is not counted, 9 apart is; alpha
               counts as a channel.
  layer_alone  four frames (blank, a 2 x 2 block, the block moved clear of itself, blank):
               step_px [4, 8, 4], wrap_px 0, step_range [4, 8], wrap_within_steps false,
               most_changed_px 8 between frames [1, 2]; a change of 24 is not a most-changed
               pixel and 25 is; with cap 3 the four frames give most_changed_px null and a note.
  light        a frame of (255, 255, 255, 255), (200, 100, 0, 128) and (0, 0, 0, 8): px 2,
               mean_rgb [236.6, 203.2, 169.8], channel_spread 66.8, luminance_range [118, 255];
               a blank second frame: px_range [0, 2], channel_spread_max 66.8.
  pack_checks  four directions: that direction's checks; one direction (not keyed): all of
               them; no checks: null.
  run          a four-direction sheets directory (a plate, a 3-frame paint animation, a 2-frame
               light layer, a one-frame light): exit 0; layers_alone names the animation and the
               2-frame light, not the one-frame one; light names both lights; pack_checks is
               meta.json's for each direction; the light layers are still listed as ignored.
  crust tap    when concept/crust-tap/model holds its sheets and measures-animation.json (the old
               measure_animation.py's output on those sheets): measure.py on them gives its
               c2 step_px, wrap_px, glass steps, c4 most_changed_px, between_frames and c3 glass
               figures in every direction, identical. Skipped when either is missing.
"""
import argparse
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BL = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(BL))
sys.path.insert(0, BL)
import measure  # noqa: E402

FAILED = []
DIRS = ("north", "east", "south", "west")


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(f"{case}: {detail}")


def blank(w=8, h=8):
    return Image.new("RGBA", (w, h))


def block(at, w=8, h=8, colour=(200, 200, 200, 255)):
    im = blank(w, h)
    im.paste(colour, (at[0], at[1], at[0] + 2, at[1] + 2))
    return im


def test_changed():
    a = blank(4, 4)
    b = blank(4, 4)
    b.putpixel((0, 0), (8, 0, 0, 0))
    b.putpixel((1, 0), (0, 9, 0, 0))
    b.putpixel((2, 0), (0, 0, 0, 9))
    n = measure.changed(a, b, 8)
    check("changed: 8 apart not counted, 9 counted, alpha a channel", n == 2, f"got {n}")


def test_layer_alone():
    frames = [blank(), block((0, 0)), block((4, 4)), blank()]
    r = measure.layer_alone(frames)
    want = dict(frames=4, frame_px=[8, 8], step_px=[4, 8, 4], wrap_px=0, step_range=[4, 8],
                wrap_within_steps=False, most_changed_px=8, between_frames=[1, 2])
    check("layer_alone: steps, wrap, most changed", r == want, f"got {r}")
    a = blank()
    b = block((0, 0), colour=(24, 0, 0, 0))
    c = block((0, 0), colour=(25, 0, 0, 0))
    check("layer_alone: 24 apart is not a most-changed pixel", measure.layer_alone([a, b])["most_changed_px"] == 0)
    check("layer_alone: 25 apart is", measure.layer_alone([a, c])["most_changed_px"] == 4)
    r = measure.layer_alone(frames, cap=3)
    check("layer_alone: over the cap, most_changed_px null with a note",
          r["most_changed_px"] is None and r["between_frames"] is None and "note" in r and r["step_px"] == [4, 8, 4],
          f"got {r}")


def test_light():
    f0 = blank(3, 1)
    f0.putpixel((0, 0), (255, 255, 255, 255))
    f0.putpixel((1, 0), (200, 100, 0, 128))
    f0.putpixel((2, 0), (0, 0, 0, 8))
    r = measure.light_figures([f0, blank(3, 1)])
    want0 = dict(px=2, mean_rgb=[236.6, 203.2, 169.8], channel_spread=66.8, luminance_range=[118, 255])
    check("light: frame 0", r["frame0"] == want0, f"got {r['frame0']}")
    check("light: px_range and channel_spread_max over a blank frame too",
          r["px_range"] == [0, 2] and r["channel_spread_max"] == 66.8 and r["frames"] == 2, f"got {r}")


def test_pack_checks():
    four = {"checks": {d: {"x": i} for i, d in enumerate(DIRS)}}
    one = {"checks": {"centre_offset_px": 0.0, "frame0_vs_still": [1, 0.0, "n"]}}
    check("pack_checks: a direction's own", measure.pack_checks(four, "east") == {"x": 1})
    check("pack_checks: one direction, all of them", measure.pack_checks(one, "") == one["checks"])
    check("pack_checks: none", measure.pack_checks({}, "north") is None)


def write_sheets(d):
    """A four-direction sheets directory: base, pump (3 frames), glass (a 2-frame light), lens."""
    os.makedirs(d, exist_ok=True)
    meta = {"checks": {}}
    for dn in DIRS:
        base = Image.new("RGBA", (128, 128), (90, 90, 90, 255))
        base.save(os.path.join(d, f"base-{dn}.png"))
        meta[f"base-{dn}"] = dict(size=[128, 128], shift=[0.0, 0.0])
        sheet = blank(24, 8)
        for f, at in enumerate(((0, 0), (2, 2), (4, 4))):
            sheet.paste(block(at), (8 * f, 0))
        sheet.save(os.path.join(d, f"pump-{dn}.png"))
        meta[f"pump-{dn}"] = dict(size=[8, 8], shift=[0.25, 0.25], frames=3, line_length=3)
        glass = blank(8, 4)
        glass.paste((255, 255, 255, 255), (0, 0, 2, 2))
        glass.paste((250, 250, 250, 255), (4, 0, 7, 3))
        glass.save(os.path.join(d, f"glass-{dn}.png"))
        meta[f"glass-{dn}"] = dict(size=[4, 4], shift=[-0.25, 0.0], frames=2, line_length=2, kind="light")
        blank(4, 4).save(os.path.join(d, f"status-lens-{dn}.png"))
        meta[f"status-lens-{dn}"] = dict(size=[4, 4], shift=[0.0, 0.5])
        meta["checks"][dn] = dict(centre_offset_px=0.0, frame0_vs_still=[0, 0.0, "note"], tag=dn)
    with open(os.path.join(d, "meta.json"), "w") as f:
        json.dump(meta, f)
    return meta


def test_run(out):
    sd = os.path.join(out, "sheets")
    meta = write_sheets(sd)
    code = measure.run([sd, "--out", os.path.join(out, "measures"), "--footprint", "2x2"])
    check("run: exit 0", code == 0, f"exit {code}")
    with open(os.path.join(out, "measures", "measures.json")) as f:
        m = json.load(f)["directions"]
    for dn in DIRS:
        r = m[dn]
        check(f"run {dn}: layers_alone names pump and glass, not the lens",
              sorted(r["layers_alone"]) == [f"glass-{dn}", f"pump-{dn}"], f"got {sorted(r['layers_alone'])}")
        check(f"run {dn}: light names glass and the lens", sorted(r["light"]) == [f"glass-{dn}", f"status-lens-{dn}"],
              f"got {sorted(r['light'])}")
        g = r["light"][f"glass-{dn}"]
        check(f"run {dn}: glass px_range [4, 9]", g["px_range"] == [4, 9], f"got {g}")
        check(f"run {dn}: pack_checks copied", r["pack_checks"] == meta["checks"][dn], f"got {r['pack_checks']}")
        check(f"run {dn}: lights still listed as ignored",
              sum("not drawn here" in i for i in r["ignored"]) == 2, f"got {r['ignored']}")


def test_crust_tap(out):
    t = os.path.join(REPO, "concept", "crust-tap", "model")
    ref = os.path.join(t, "measures-animation.json")
    if not (os.path.isfile(ref) and os.path.isfile(os.path.join(t, "sheets", "meta.json"))):
        print("  SKIP  crust tap: its sheets or measures-animation.json are not there")
        return
    code = measure.run([os.path.join(t, "sheets"), "--out", os.path.join(out, "crust-tap"), "--footprint", "2x2"])
    check("crust tap: exit 0", code == 0, f"exit {code}")
    with open(ref) as f:
        old = json.load(f)
    with open(os.path.join(out, "crust-tap", "measures.json")) as f:
        new = json.load(f)["directions"]
    for dn in DIRS:
        pump, glass, light = (new[dn]["layers_alone"][f"pump-{dn}"], new[dn]["layers_alone"][f"sight-glass-{dn}"],
                              new[dn]["light"][f"sight-glass-{dn}"])
        c2, c4, c3 = old["c2"][dn], old["c4"][dn], old["c3"][dn]
        got = dict(step_px=pump["step_px"], wrap_px=pump["wrap_px"], glass_step_range=glass["step_range"],
                   glass_wrap_px=glass["wrap_px"], most_changed_px=pump["most_changed_px"],
                   between_frames=pump["between_frames"], channel_spread_max=light["channel_spread_max"],
                   px_range=light["px_range"], frame0=[light["frame0"][k] for k in ("px", "mean_rgb", "channel_spread",
                                                                                     "luminance_range")])
        want = dict(step_px=c2["step_px"], wrap_px=c2["wrap_px"], glass_step_range=c2["glass_step_range"],
                    glass_wrap_px=c2["glass_wrap_px"], most_changed_px=c4["most_changed_px"],
                    between_frames=c4["between_frames"], channel_spread_max=c3["channel_spread_max"],
                    px_range=c3["px_range"], frame0=[c3["frame0"][k] for k in ("px", "mean_rgb", "channel_spread",
                                                                                "luminance_range")])
        bad = {k: (want[k], got[k]) for k in want if want[k] != got[k]}
        check(f"crust tap {dn}: measure_animation.py's figures identical", not bad, f"old, new: {bad}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    test_changed()
    test_layer_alone()
    test_light()
    test_pack_checks()
    test_run(a.out)
    test_crust_tap(a.out)
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
