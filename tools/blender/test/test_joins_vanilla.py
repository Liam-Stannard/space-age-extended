#!/usr/bin/env python3
"""measure.py's join gate held to vanilla: every pipe join of 12 vanilla buildings passes, and
a joint with a gap cut into it fails.

  python3 tools/blender/test/test_joins_vanilla.py [--sheet <out.png>]

Exits 0 when all 128 vanilla joins pass, the gap fixture fails and every probe below comes out
as pinned; 1 otherwise, naming them. Reads the vanilla data (FACTORIO_DATA, default the Steam
install) and nothing else; no Blender, no client. --sheet writes every join at 4x (plain and
marked) to one image, split past 8000 px as measure.py splits its sheets (<out>-2.png and on).

Each building is put together as the engine draws it, from its prototype: frame 0 of every
layer that is not a shadow, at its shift (measure.vanilla_sprite, which adds what the .lua
beside a sprite does not say: the chemical plant's sprite_load shift, the pumpjack base's
column per direction), the pipe pictures at their connections for the buildings that have
them, all four directions (horizontal and vertical for the steam engine and turbine), and the
connections from the fluid boxes, turned with the building. Left out: the cryogenic plant
(its stubs are spread over many animation layers) and the fusion generator's fusion-pipe
connections (not ordinary pipes); its two ordinary outputs are in.

The gap fixture: vanilla's steam turbine, vertical, with the south stub cut away across the
pipe body's width (x -20..20 px) from 36 px above the footprint's south edge down to it: the
pipe there meets nothing. Its south join must fail; its other three must still pass.

The probes (PROBES) pin the gate's thresholds -- the agreed rule, ground of 2 px or more in at
most 2 of the pipe body's columns -- on a flat block with a stub: a 37 px stub on a vertical
pipe (39 px body) passes and 36 and 35 px fail; on a horizontal pipe (41 px body) a 39 px stub
passes and 38 px fails; a 41 px stub 3 px off the axis passes and 4 px fails; a building
ending 1 px short of the pipe passes and 2 px fails; and these all fail: a 1 px dark line
(alpha 160) laid in front of a gap (north, east, west), a 1 or 2 px lip following the south
pipe's rounded end with the body 20 px behind it, and a fitting detached from the body with
ground behind it (south, north, east).
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import contract  # noqa: E402
import measure  # noqa: E402

C = 896                                     # every building's canvas, the origin at its centre
B, SA = "base/graphics/entity/", "space-age/graphics/entity/"
FOUR = ("north", "east", "south", "west")
FACE_NAME = dict(N="north", E="east", S="south", W="west")
CHEM = dict(add=(0, -18))                   # entities.lua: shift = util.by_pixel(0, -9)


def foundry_layers(d):
    """foundry-pictures.lua: the pipe sets are working visualisations; in north and south the
    north set draws behind the main animation."""
    pipe = {k: (SA + f"foundry/foundry-pipe-connections-{k}.png",) for k in FOUR}
    body = [(SA + "foundry/foundry-base.png",), (SA + "foundry/foundry-anim-1.png:foundry-anim.lua",)]
    if d in ("north", "south"):
        return [pipe["north"]] + body + [pipe["south"]]
    return body + ([pipe["east"], pipe["west"]] if d == "east" else [pipe["west"], pipe["east"]])


ENTITIES = {
    "assembling-machine-2": dict(
        foot=(3, 3), dirs="four", conns=[(0, -1, "N"), (0, 1, "S")],
        layers=lambda d: [(B + "assembling-machine-2/assembling-machine-2-base.png",),
                          (B + "assembling-machine-2/assembling-machine-2-anim.png",)],
        pipes=lambda f: B + f"assembling-machine-2/assembling-machine-2-pipe-{f}.png"),
    "assembling-machine-3": dict(
        foot=(3, 3), dirs="four", conns=[(0, -1, "N"), (0, 1, "S")],
        layers=lambda d: [(B + "assembling-machine-3/assembling-machine-3-base.png",),
                          (B + "assembling-machine-3/assembling-machine-3-anim.png",)],
        pipes=lambda f: B + f"assembling-machine-3/assembling-machine-3-pipe-{f}.png"),
    "chemical-plant": dict(
        foot=(3, 3), dirs="four", conns=[(-1, -1, "N"), (1, -1, "N"), (-1, 1, "S"), (1, 1, "S")],
        layers=lambda d: [(B + f"chemical-plant/chemical-plant-{d}-base.png", CHEM),
                          (B + f"chemical-plant/chemical-plant-{d}-anim-1.png", CHEM),
                          (B + f"chemical-plant/chemical-plant-{d}-anim-2.png", CHEM)]),
    "oil-refinery": dict(
        foot=(5, 5), dirs="four",
        conns=[(-1, 2, "S"), (1, 2, "S"), (-2, -2, "N"), (0, -2, "N"), (2, -2, "N")],
        layers=lambda d: [(B + f"oil-refinery/{d}/oil-refinery-{d}.png",)]),
    "steam-engine": dict(
        foot=(3, 5), dirs="horizontal-vertical", conns=[(0, -2, "N"), (0, 2, "S")],
        layers=lambda d: [(B + "steam-engine/steam-engine-" + ("V" if d == "vertical" else "H") + ".png",)]),
    "steam-turbine": dict(
        foot=(3, 5), dirs="horizontal-vertical", conns=[(0, -2, "N"), (0, 2, "S")],
        layers=lambda d: [(B + "steam-turbine/steam-turbine-" + ("V" if d == "vertical" else "H") + ".png",)]),
    "boiler": dict(
        foot=(3, 2), dirs="four", conns=[(-1, 0.5, "W"), (1, 0.5, "E"), (0, -0.5, "N")],
        layers=lambda d: [(B + f"boiler/boiler-{d[0].upper()}-idle.png",)]),
    "heat-exchanger": dict(
        foot=(3, 2), dirs="four", conns=[(-1, 0.5, "W"), (1, 0.5, "E"), (0, -0.5, "N")],
        layers=lambda d: [(B + f"heat-exchanger/heatex-{d[0].upper()}-idle.png",)]),
    "pumpjack": dict(
        foot=(3, 3), dirs="four", conns=[(1, -1, "N")],
        layers=lambda d: [(B + "pumpjack/pumpjack-base.png",
                           dict(geom=(261, 273, (-4.5, -9.5)), col=FOUR.index(d))),
                          (B + "pumpjack/pumpjack-horsehead.png",)]),
    "foundry": dict(
        foot=(5, 5), dirs="four", conns=[(-1, 2, "S"), (1, 2, "S"), (-1, -2, "N"), (1, -2, "N")],
        layers=foundry_layers),
    "electromagnetic-plant": dict(
        foot=(4, 4), dirs="four",
        conns=[(-1.5, 0.5, "W"), (1.5, -0.5, "E"), (0.5, 1.5, "S"), (-0.5, -1.5, "N")],
        layers=lambda d: [(SA + "electromagnetic-plant/electromagnetic-plant-base.png",),
                          (SA + "electromagnetic-plant/electromagnetic-plant-main-rotate-1.png:"
                           "electromagnetic-plant-main-rotate.lua",)],
        pipes=lambda f: SA + "electromagnetic-plant/pipe-connections/"
        f"electromagnetic-plant-pipe-{FACE_NAME[f]}.png"),
    "fusion-generator": dict(
        foot=(3, 5), dirs="four", conns=[(-1, -2, "N"), (1, -2, "N")],
        layers=lambda d: [(SA + f"fusion-generator/{d}/fusion-generator-{d}.png",)]),
}


class Canvas:
    """What measure.join() reads off a Source: the canvas, its origin, how to place a sprite."""

    size, origin, ports, port_meta = C, (C / 2, C / 2), None, {}
    place = measure.Source.place


class Built:
    """What measure.join() reads off a Scene: the building as drawn, and its canvas."""

    def __init__(self, still):
        self.src, self.still = Canvas(), still


def put(canvas, rel, opts=None, at=(0, 0)):
    im, sx, sy = measure.vanilla_sprite(rel, opts)
    canvas.alpha_composite(im, (round(C / 2 + at[0] * measure.PPT + sx - im.width / 2),
                                round(C / 2 + at[1] * measure.PPT + sy - im.height / 2)))


def building(e, dn, deg):
    cv = Image.new("RGBA", (C, C))
    for rel, *opts in e["layers"](dn):
        put(cv, rel, opts[0] if opts else None)
    for c in e["conns"] if "pipes" in e else ():
        x, y, f = measure.turn(c, deg)
        dx, dy = measure.FACE[f]
        put(cv, e["pipes"](f), at=(x + dx, y + dy))
    return cv


def joins(name, e, cut=None):
    """Every join of one building: [(label, result, (plain, marked))]."""
    out = []
    for dn, deg in contract.DIRECTIONS[e["dirs"]]:
        cv = building(e, dn, deg)
        if cut and dn == cut[0]:
            cut[1](cv)
        for c in e["conns"]:
            cc = measure.turn(c, deg)
            res, pics = measure.join(Built(cv), cc)
            out.append((f"{name} {dn} ({cc[0]:g}, {cc[1]:g}) {cc[2]}", res, pics))
    return out


def rect(im, x0, y0, x1, y1, fill=(150, 140, 120, 255)):
    """Fill x0..x1, y0..y1 (px from the origin, half-open) on a canvas."""
    ImageDraw.Draw(im).rectangle((C // 2 + x0, C // 2 + y0, C // 2 + x1 - 1, C // 2 + y1 - 1), fill=fill)
    return im


def block(half_w=80, half_h=120):
    """A flat body: x +-half_w, y +-half_h px (a 3x5's plate stops 40 px short of its north and
    south edges, y +-160; a 3x3's, half_w 80, 16 px short of its east and west edges, x +-96)."""
    return rect(Image.new("RGBA", (C, C)), -half_w, -half_h, half_w, half_h, (110, 105, 95, 255))


def lip(t):
    """The flat body ending at y 120 and a t px lip hugging the south pipe's rounded end."""
    im = block()
    pipe = Canvas().place(measure.load(os.path.join(measure.PIPE, "pipe-straight-vertical.png")), (0, 0),
                          at=(0, 3))
    P, px, o = measure.pipe_mask(pipe).load(), im.load(), C // 2
    for c in range(o - 40, o + 40):
        r = next((r for r in range(o, C) if P[c, r]), None)
        for k in range(1, t + 1 if r is not None else 0):
            px[c, r - k] = (150, 140, 120, 255)
    return im


S_, N_, E_, W_ = (0, 2, "S"), (0, -2, "N"), (1, 0, "E"), (-1, 0, "W")
DARK_LINE = (40, 40, 40, 160)
# (name, building, connection, should pass): the gate's thresholds, pinned. A vertical pipe's body
# is 39 px, a horizontal one's 41.
PROBES = [
    ("stub 41 px, south", lambda: rect(block(), -20, 120, 21, 160), S_, True),
    ("stub 41 px, north", lambda: rect(block(), -20, -160, 21, -120), N_, True),
    ("stub 41 px, east", lambda: rect(block(80, 80), 80, -20, 96, 21), E_, True),
    ("stub 39 px, east (the narrowest that passes a horizontal pipe)", lambda: rect(block(80, 80), 80, -19, 96, 20),
     E_, True),
    ("stub 38 px, east", lambda: rect(block(80, 80), 80, -19, 96, 19), E_, False),
    ("stub 37 px, south (the narrowest that passes a vertical pipe)", lambda: rect(block(), -18, 120, 19, 160), S_,
     True),
    ("stub 36 px, south", lambda: rect(block(), -18, 120, 18, 160), S_, False),
    ("stub 35 px, south", lambda: rect(block(), -17, 120, 18, 160), S_, False),
    ("stub 35 px, north", lambda: rect(block(), -17, -160, 18, -120), N_, False),
    ("stub 41 px 2 px off the axis, south", lambda: rect(block(), -18, 120, 23, 160), S_, True),
    ("stub 41 px 3 px off the axis, south", lambda: rect(block(), -17, 120, 24, 160), S_, True),
    ("stub 41 px 4 px off the axis, south", lambda: rect(block(), -16, 120, 25, 160), S_, False),
    ("building ending 1 px short, north", lambda: rect(block(), -20, -159, 21, -120), N_, True),
    ("building ending 1 px short, east", lambda: rect(block(80, 80), 80, -20, 95, 21), E_, True),
    ("building ending 2 px short, north", lambda: rect(block(), -20, -158, 21, -120), N_, False),
    ("building ending 2 px short, east", lambda: rect(block(80, 80), 80, -20, 94, 21), E_, False),
    ("thin line: stub 6 px short, a 1 px dark line (alpha 160) at the edge, north",
     lambda: rect(rect(block(), -20, -154, 21, -120), -30, -160, 30, -159, DARK_LINE), N_, False),
    ("thin line, east", lambda: rect(rect(block(80, 80), 80, -20, 90, 21), 95, -30, 96, 30, DARK_LINE), E_, False),
    ("thin line, west", lambda: rect(rect(block(80, 80), -90, -20, -80, 21), -96, -30, -95, 30, DARK_LINE), W_,
     False),
    ("rounded lip, 1 px, on the south pipe's end, body 20 px back", lambda: lip(1), S_, False),
    ("rounded lip, 2 px", lambda: lip(2), S_, False),
    ("detached fitting, south (ground 8 px behind it)", lambda: rect(block(), -20, 128, 21, 160), S_, False),
    ("detached fitting, north", lambda: rect(block(), -20, -160, 21, -128), N_, False),
    ("detached fitting, east", lambda: rect(block(80, 80), 86, -20, 96, 21), E_, False),
]


def cut_south_stub(cv):
    """Clear x -20..20 px, from 36 px above the 3x5's south edge (y 160) down to it."""
    o = C // 2
    cv.paste((0, 0, 0, 0), (o - 20, o + 124, o + 21, o + 160))


def panel(label, res, pics):
    plain, marked = pics
    k = 160                                   # the middle +-40 px of the 4x crops
    p = Image.new("RGB", (4 * k + 6, 2 * k + 40), measure.BG)
    p.paste(plain.crop((320 - k, 320 - k, 320 + k, 320 + k)), (0, 40))
    p.paste(marked.crop((320 - k, 320 - k, 320 + k, 320 + k)), (2 * k + 6, 40))
    d = ImageDraw.Draw(p)
    f = measure.font(11)
    d.text((0, 0), label + f", pipe {res['pipe_drawn']}", font=f, fill=measure.HEAD)
    g = res.get("gap") or {}
    d.text((0, 16), f"{'PASS' if res['pass'] else 'FAIL'}: {g.get('columns')} gap columns, longest "
           f"{g.get('max_ground_px')} px; beside {res.get('beside', {}).get('px')} px (information)",
           font=f, fill=measure.GOOD if res["pass"] else measure.BAD)
    return p


def main(argv):
    sheet = argv[argv.index("--sheet") + 1] if "--sheet" in argv else None
    failed, panels, n = [], [], 0
    for name, e in ENTITIES.items():
        rows = joins(name, e)
        n += len(rows)
        bad = [label for label, res, _ in rows if not res["pass"]]
        failed += [f"vanilla join failed: {label}" for label in bad]
        worst = max(res["gap"]["columns"] for _, res, _ in rows)
        print(f"{name:22s} {len(rows):2d} joins, {len(rows) - len(bad):2d} pass; most gap columns {worst}")
        panels += [panel(*r) for r in rows]
    gap = joins("gap fixture: steam-turbine", ENTITIES["steam-turbine"], cut=("vertical", cut_south_stub))
    for label, res, _ in gap:
        south = label.endswith("(0, 2) S") and " vertical " in label
        ok = (not res["pass"]) if south else res["pass"]
        print(f"{label}: {'PASS' if res['pass'] else 'FAIL'} ({res['gap']['columns']} gap columns), "
              f"wanted {'FAIL' if south else 'PASS'}")
        if not ok:
            failed.append(f"gap fixture: {label} should {'fail' if south else 'pass'}")
    panels += [panel(*r) for r in gap]
    for name, make, conn, want in PROBES:
        res, pics = measure.join(Built(make()), conn)
        ok = res["pass"] == want
        print(f"probe {name}: {'PASS' if res['pass'] else 'FAIL'} ({res['gap']['columns']} gap columns), "
              f"wanted {'PASS' if want else 'FAIL'}")
        if not ok:
            failed.append(f"probe {name} should {'pass' if want else 'fail'}")
        panels.append(panel(f"probe: {name}", res, pics))
    if n != 128:
        failed.append(f"expected 128 vanilla joins, assembled {n}")
    if sheet:
        head = measure.text_block("measure.py join gate on vanilla: no gap", [
            f"{n} vanilla joins of {len(ENTITIES)} buildings, and the gap fixture (the steam turbine with its "
            "south stub cut away). Each at 4x: plain, then marked (gap columns red; beside, information, "
            "magenta)."], 7900)
        ims, _ = measure.pages([head] + measure.rows_of(panels, 7900, 10), measure.MAX_SIDE)
        stem = sheet[:-4] if sheet.endswith(".png") else sheet
        for i, im in enumerate(ims):
            path = f"{stem}.png" if i == 0 else f"{stem}-{i + 1}.png"
            im.save(path, optimize=True)
            print(f"sheet: {path} {im.size[0]}x{im.size[1]}")
    if failed:
        print("\n".join(failed), file=sys.stderr)
        return 1
    print(f"OK: {n} vanilla joins pass; the gap fixture's south join fails; {len(PROBES)} probes as pinned")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
