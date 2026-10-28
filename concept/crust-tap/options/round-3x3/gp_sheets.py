#!/usr/bin/env python3
"""Gas Pump 3x3, options round: each take's concept sheet and GIFs, and the contact sheet.

  python3 -B gp_sheets.py --full <renders> --he <helium renders> --measure <measure.py out> --out <round dir>
                          --gif2 <dir for the 2x GIFs, out of git> [--only 1,2,3]

<renders>/<n>/ is gp_<n>_*.py's output (idle, plate, 24 working frames, three turns, meta.json); <he>/<n>/ its
working frame 0 with the gas in helium-3's tint (--helium); <measure>/<n>/measures.json is measure.py's run
on gp_pack.py's sheets of it (with --vanilla pumpjack --connection 0,-1,N --footprint 3x3). Every figure on a
sheet is measure.py's; the drawing here is only the drawing.

Writes into <out>:
  <n>-<slug>.png          the take's sheet: working and idle at 2x with the vanilla pipe joined on the north
                          tile, the chain numbered over the gas and fuel paths, the motion map, the sight glass
                          in siderane and helium-3, key frames, the four turns, the figures beside the pumpjack's
  <n>-<slug>-1x.gif       the working loop at 1x, the pipe joined (24 frames, 70 ms)
  contact-sheet.png       the three takes beside vanilla's pumpjack, the 2x2 Gas Pump and the Vent Pump, at 1x
                          and the takes again at 2x
and the 2x GIFs into <gif2>.
"""
import argparse
import json
import os

from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
ap = argparse.ArgumentParser()
ap.add_argument("--full", required=True)
ap.add_argument("--he", required=True)
ap.add_argument("--measure", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--gif2", required=True)
ap.add_argument("--only", default="1,2,3")
ap.add_argument("--study", default=None, help="the pumpjack study's figures (gp_study.py --json)")
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
ap.add_argument("--ventpump", default="/home/liam-stannard/git/space-age-extended/.claude/worktrees/vent-pump-model/"
                "concept/vent-pump/options/round-5/08-gas-lift-tower-a-1x.gif")
args = ap.parse_args()
FD = args.factorio
os.makedirs(args.out, exist_ok=True)
os.makedirs(args.gif2, exist_ok=True)

CANVAS, ORIGIN = (352, 352), (160, 208)
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT, SUB, HEAD = (228, 222, 210), (175, 168, 156), (240, 200, 120)
GIF_MS = 70
GAS = (168, 217, 41)
FUEL = (214, 160, 96)
KEYF = {1: 6, 2: 6, 3: 15}       # the working frame shown big: the beam tilted, the rods out, the bell high

TAKES = {
    1: dict(slug="the-gas-jack", name="THE GAS JACK",
            pitch="Vanilla's pumpjack worked on gas: a walking beam nods on its samson post and lifts a compressor "
                  "rod out of the wellhead, a gas engine on the vent's own gas turning the cranks.",
            motion=["Walking beam, horsehead, bridle and the compressor's rod: one nod a loop (the crank one turn; "
                    "the beam -17 to +19 degrees, the rod about 0.7 tile end to end).",
                    "Cranks and counterweights: one turn a loop, on both sides of the gearbox; pitman arms with "
                    "them.",
                    "Gas engine flywheel and the coupling to the gearbox: two turns a loop.",
                    "Receiver's gauge: kicks on each delivery stroke.",
                    "Sight glass: the gas drifts through (paint, the vent's colour, no light); empty when idle.",
                    "Idle: everything stops where it is (frame 0: the head at the top of its nod), the glass dark."]),
    2: dict(slug="the-flywheel-compressor", name="THE FLYWHEEL COMPRESSOR",
            pitch="The 2x2 Gas Pump's flywheel and crank grown into an oilfield engine-compressor: a big spoked "
                  "flywheel, two opposed cylinders with their rods sliding in open frames, the scrubber over the vent.",
            motion=["Flywheel (south face, six spokes, a red lug): one turn a loop.",
                    "Both crossheads, piston rods and connecting rods: out and back once a loop, opposed (apart, "
                    "then together).",
                    "Power cylinders' rocker arms: nod once a loop, half a loop apart.",
                    "Gauge board (three needles) and the bottle's gauge: kick on the delivery stroke.",
                    "Sight glass on the east discharge: the gas drifts through; empty when idle.",
                    "Idle: everything stops where it is, the glass dark."]),
    3: dict(slug="the-gas-bell", name="THE GAS BELL",
            pitch="A gasholder over the vent: a square bell rises in its water-sealed tank as the vent fills it, "
                  "counterweights falling against it, and a blower driven by a gas engine draws it down.",
            motion=["The bell: rises 0.5 tile over two thirds of the loop as the vent fills it, drawn down in the "
                    "last third (slow up, quicker down).",
                    "Counterweights: move against the bell on their chains; the sheaves turn with them.",
                    "Gas engine flywheel and the two couplings of the blower's drive: two turns a loop.",
                    "Blower's gauge: kicks while the bell is drawn down.",
                    "Sight glass on the discharge: the gas drifts through; empty when idle.",
                    "Idle: everything stops where it is (the bell low), the glass dark."]),
}
COMMON = ("A lit Blender concept on the GPU in the Vent Pump's signed-off finish (its kit, variant (a) warmer paints: "
          "a paint per unit, worn paint, rust where it forms, the satin floor, the unlit catcher). 3x3, centred on the "
          "vent; one output, the middle of the north face ({0,-1}), a vanilla straight pipe on the next tile. Nothing "
          "glows: the gas in the sight glass is paint in the vent's colour (siderane #A8D929 here; helium-3 #8CC7E6 "
          "beside it). No power: a gas engine burns a slip of the vent's own gas (spec A.2, void). Not a model; "
          "nothing adopted; nothing in graphics/.")


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
                              size)


def load(path, k):
    im = Image.open(path).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    return im.convert("RGBa").resize((CANVAS[0] * k, CANVAS[1] * k), Image.LANCZOS).convert("RGBA")


def ground(size, origin, ppt, foot=(3, 3)):
    g = Image.new("RGBA", size, GROUND)
    ov = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    ox, oy = origin
    for i in range(-24, 25):
        d.line([(ox + (i + 0.5) * ppt, 0), (ox + (i + 0.5) * ppt, size[1])], fill=(255, 255, 255, 22))
        d.line([(0, oy + (i + 0.5) * ppt), (size[0], oy + (i + 0.5) * ppt)], fill=(255, 255, 255, 22))
    fw, fh = foot
    d.rectangle([ox - fw * ppt / 2, oy - fh * ppt / 2, ox + fw * ppt / 2, oy + fh * ppt / 2], outline=(255, 255, 255, 110))
    g.alpha_composite(ov)
    return g


def pipe_sprite(face, k):
    name = "pipe-straight-vertical" if face in "NS" else "pipe-straight-horizontal"
    im = Image.open(f"{FD}/base/graphics/entity/pipe/{name}.png").convert("RGBA")
    return im.resize((64 * k, 64 * k), Image.LANCZOS)


PORT = {"north": ((0, -2), "N"), "east": ((2, 0), "E"), "south": ((0, 2), "S"), "west": ((-2, 0), "W")}


def with_port(render, d, k):
    origin = (ORIGIN[0] * k, ORIGIN[1] * k)
    c = ground(render.size, origin, 64 * k)
    (tx, ty), face = PORT[d]
    im = pipe_sprite(face, k)
    c.alpha_composite(im, (round(origin[0] + tx * 64 * k - im.width / 2), round(origin[1] + ty * 64 * k - im.height / 2)))
    c.alpha_composite(render)
    return c


def text(d, xy, s, size=13, fill=TEXT, bold=False):
    d.text(xy, s, font=font(size, bold), fill=fill)


def wrap(s, size, width):
    f = font(size)
    out, line = [], ""
    for w in s.split(" "):
        t = (line + " " + w).strip()
        if f.getlength(t) > width and line:
            out.append(line)
            line = w
        else:
            line = t
    if line:
        out.append(line)
    return out


def block(title, paras, width, size=14, tight=False):
    lines = []
    for p in paras:
        lines += wrap(p, size, width - 24) + ([] if tight else [""])
    im = Image.new("RGBA", (width, 34 + len(lines) * (size + 5)), BG)
    d = ImageDraw.Draw(im)
    text(d, (10, 6), title, 16, HEAD, bold=True)
    y = 32
    for ln in lines:
        text(d, (14, y), ln, size)
        y += size + 5
    return im


def captioned(im, cap, size=14):
    lines = cap.split("\n")
    w = max([im.width] + [int(font(size, True).getlength(ln)) + 10 for ln in lines])
    hh = 6 + (size + 6) * len(lines)
    c = Image.new("RGBA", (w, im.height + hh), BG)
    d = ImageDraw.Draw(c)
    for i, ln in enumerate(lines):
        text(d, (4, 4 + (size + 6) * i), ln, size, HEAD if i == 0 else SUB, bold=(i == 0))
    c.alpha_composite(im, (0, hh))
    return c


def hrow(ims, gap=14):
    r = Image.new("RGBA", (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), BG)
    x = 0
    for i in ims:
        r.alpha_composite(i, (x, 0))
        x += i.width + gap
    return r


def vstack(ims, gap=14, width=None):
    r = Image.new("RGBA", (width or max(i.width for i in ims), sum(i.height for i in ims) + gap * (len(ims) - 1)), BG)
    y = 0
    for i in ims:
        r.alpha_composite(i, (0, y))
        y += i.height + gap
    return r


def gif(frames, path):
    strip = Image.new("RGB", (frames[0].width, frames[0].height * len(frames)))
    for i, f in enumerate(frames):
        strip.paste(f.convert("RGB"), (0, i * f.height))
    pal = strip.quantize(colors=256)
    q = [f.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=GIF_MS, loop=0, optimize=True)
    return round(os.path.getsize(path) / 1e6, 2)


def numbered(im, labels, off, k):
    d = ImageDraw.Draw(im)
    for L in labels:
        x, y = (L["px"][0] - off[0]) * k, (L["px"][1] - off[1]) * k
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=(240, 200, 120), outline=(20, 18, 16), width=2)
        s = str(L["n"])
        w = font(15, True).getlength(s)
        d.text((x - w / 2, y - 9), s, font=font(15, True), fill=(20, 18, 16))
    return im


def overlay(base2, meta, off, k=2):
    im = Image.blend(base2.convert("RGB"), Image.new("RGB", base2.size, (24, 22, 20)), 0.5).convert("RGBA")
    d = ImageDraw.Draw(im)
    for R in sorted(meta["routes"], key=lambda R: R["kind"] == "gas"):
        col = GAS if R["kind"] == "gas" else FUEL
        P = [((x - off[0]) * k, (y - off[1]) * k) for x, y in R["px"]]
        segs = [P]
        if R["kind"] == "fuel":
            segs, acc, on, cur = [], 0.0, True, [P[0]]
            for a, b in zip(P, P[1:]):
                acc += ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
                if on:
                    cur.append(b)
                if acc > (14 if on else 8):
                    if on and len(cur) > 1:
                        segs.append(cur)
                    on, acc, cur = not on, 0.0, [b]
            if on and len(cur) > 1:
                segs.append(cur)
        for sg in segs:
            d.line(sg, fill=(12, 10, 8), width=8, joint="curve")
        for sg in segs:
            d.line(sg, fill=col, width=4, joint="curve")
        acc = 0.0
        for a, b in zip(P, P[1:]):
            L = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
            acc += L
            if acc >= 44 and L > 0.5:
                acc = 0.0
                ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
                tip = (b[0] + ux * 6, b[1] + uy * 6)
                l_ = (b[0] - ux * 7 - uy * 7, b[1] - uy * 7 + ux * 7)
                r_ = (b[0] - ux * 7 + uy * 7, b[1] - uy * 7 - ux * 7)
                d.polygon([tip, l_, r_], fill=col, outline=(12, 10, 8))
    numbered(im, meta["labels"], off, k)
    leg = Image.new("RGBA", (im.width, 28), BG)
    dl = ImageDraw.Draw(leg)
    dl.line([(8, 14), (40, 14)], fill=GAS, width=5)
    text(dl, (46, 6), "the gas, vent to outlet", 13)
    dl.line([(260, 14), (292, 14)], fill=FUEL, width=5)
    text(dl, (298, 6), "fuel slip to the engine (dashed)", 13)
    return vstack([im, leg], 0)


def motion_map(plate2, frames2):
    base = plate2.convert("RGB")
    f0 = frames2[0].convert("RGB")
    move = None
    for f in frames2[1:]:
        dd = ImageChops.difference(f0, f.convert("RGB")).convert("L").point(lambda v: 255 if v > 30 else 0)
        move = dd if move is None else ImageChops.lighter(move, dd)
    out = Image.blend(base, Image.new("RGB", base.size, (40, 36, 32)), 0.55)
    out.paste((230, 40, 200), mask=move)
    o = out.convert("RGBA")
    o.putalpha(ImageChops.lighter(plate2.getchannel("A"), move))
    return o


def bbox_of(ims, pad=8):
    box = None
    for im in ims:
        b = im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    box = (min(box[0], ORIGIN[0] - 112), min(box[1], ORIGIN[1] - 168), max(box[2], ORIGIN[0] + 112),
           max(box[3], ORIGIN[1] + 112))
    return (max(0, box[0] - pad), max(0, box[1] - pad), min(CANVAS[0], box[2] + pad), min(CANVAS[1], box[3] + pad))


def figures(n):
    p = os.path.join(args.measure, str(n), "measures.json")
    return json.load(open(p)) if os.path.exists(p) else None


def fig_lines(M, study):
    if M is None:
        return ["(measure.py not run)"]
    D = M["directions"][""]
    c, t, f = D["coverage"], D["tonal"]["plate"], D["finish"]["plate"]
    mo, col = D.get("motion", {}), D.get("colour", {})
    joins = M.get("joins") or D.get("joins")
    jl = []
    for j in (joins if isinstance(joins, list) else [joins] if joins else []):
        jl.append(f"{j.get('connection', '')} {'PASS' if j.get('pass') else 'FAIL'} {j.get('why') or ''}".strip())
    out = [f"Coverage {c['footprint_pct']} % of the footprint (bar 92 %), mass {c['mass_pct']} %, corners "
           + ", ".join(f"{k} {v}" for k, v in c["corners_pct"].items())
           + f", outer band {c['outer_band_pct']} %. Rise {c['rise_tiles']} tile over the north edge (bar: the "
           f"pumpjack's, below). Extent {c['extent_tiles'][0]} x {c['extent_tiles'][1]} tiles.",
           f"Tonal (plate) p5 {t['p5']}, p50 {t['p50']}, p95 {t['p95']}, spread {t['spread']} (the mod ~75-81; p95 into "
           f"vanilla's range). Finish: black {f['black_pct']} %, fine {f['fine']}, mid {f['mid']}, dark chroma "
           f"{f['darkchr']}.",
           f"Motion over the loop: moving {mo.get('moving_pct')} % of the covered px, strobe {mo.get('strobe_pct')} % "
           f"(r7's: reversing 3+ times a loop). Colour: blue {col.get('blue_pct')} %, orange {col.get('orange_pct')} %, "
           f"white {col.get('white_px')} px, glow: none (no glow layer)."]
    if jl:
        out.append("Pipe join, north (measure.py, the no-gap rule): " + "; ".join(jl))
    if study:
        sc = study["coverage"]
        out.append(f"Vanilla pumpjack (measure.py's own composite): coverage {sc['footprint_pct']} %, corners "
                   + ", ".join(f"{k} {v}" for k, v in sc["corners_pct"].items())
                   + f", rise {sc['rise_tiles']} tile; tonal p50 {study['tonal']['p50']}, p95 {study['tonal']['p95']}; "
                   f"moving {study['moving_pct']} %, strobe {study['strobe_pct']} %.")
    return out


def pipe_lines(meta):
    out = []
    for P in meta["pipes"]:
        e = P["ends"]
        out.append(f"{'OK' if P['ok'] else 'LOOSE'} -- {P['name']}: from {e[0]['to'] or 'AIR'} to {e[1]['to'] or 'AIR'}")
    return out


# ---------------------------------------------------------------- the references
def ref_pumpjack():
    PJ = f"{FD}/base/graphics/entity/pumpjack"
    S = 448
    O = S // 2
    c = Image.new("RGBA", (S, S))
    sh = Image.new("RGBA", (S, S))

    def put(cv, im, sx, sy):
        cv.alpha_composite(im, (round(O + sx - im.width / 2), round(O + sy - im.height / 2)))
    put(sh, Image.open(f"{PJ}/pumpjack-base-shadow.png").convert("RGBA").crop((0, 0, 261, 273)), -4.0, -10.0)
    put(sh, Image.open(f"{PJ}/pumpjack-horsehead-shadow.png").convert("RGBA").crop((0, 0, 292, 78)), 35.5, 29.0)
    put(c, Image.open(f"{PJ}/pumpjack-base.png").convert("RGBA").crop((0, 0, 261, 273)), -4.5, -9.5)
    put(c, Image.open(f"{PJ}/pumpjack-horsehead.png").convert("RGBA").crop((0, 0, 206, 172)), -9.0, -58.0)
    g = ground((S, S), (O, O), 64)
    a = sh.getchannel("A").point(lambda v: v // 2)
    g.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (S, S)).split(), a)))
    g.alpha_composite(c)
    return g.crop((O - ORIGIN[0], O - ORIGIN[1], O - ORIGIN[0] + CANVAS[0], O - ORIGIN[1] + CANVAS[1]))


def ref_gas_pump():
    """The 2x2 Gas Pump as shipped (graphics/entity/gas-pump/, the prototype's shifts), facing north, its output
    pipe at {0.5, -0.5} north (spec A.5) on the tile beyond, the glass tinted siderane, frame 0."""
    GP = os.path.join(REPO, "graphics", "entity", "gas-pump")
    S = 352
    O = ORIGIN
    g = ground((S, S), O, 64, foot=(2, 2))

    def put(im, sx, sy):
        g.alpha_composite(im, (round(O[0] + sx * 64 - im.width / 2), round(O[1] + sy * 64 - im.height / 2)))
    put(pipe_sprite("N", 1), 0.5, -1.5)
    shd = Image.open(f"{GP}/base-shadow-north.png").convert("RGBA")
    a = shd.getchannel("A").point(lambda v: v // 2)
    put(Image.merge("RGBA", (*Image.new("RGB", shd.size).split(), a)), 0.35938, -0.03125)
    put(Image.open(f"{GP}/base-north.png").convert("RGBA"), 0.0, -0.15625)
    put(Image.open(f"{GP}/pump-north.png").convert("RGBA").crop((0, 0, 69, 50)), 0.47656, -0.21875)
    gl = Image.open(f"{GP}/sight-glass-north.png").convert("RGBA").crop((0, 0, 21, 18))
    rgb = ImageChops.multiply(gl.convert("RGB"), Image.new("RGB", gl.size, GAS))
    put(Image.merge("RGBA", (*rgb.split(), gl.getchannel("A"))), -0.13281, -0.75)
    return g


def ref_vent_pump():
    im = Image.open(args.ventpump)
    im.seek(0)
    return im.convert("RGBA")


# ---------------------------------------------------------------- one take
FIRST, FIRST2, MEAS = {}, {}, {}
study = json.load(open(args.study)) if args.study else None


def build(n):
    o = TAKES[n]
    d = os.path.join(args.full, str(n))
    meta = json.load(open(os.path.join(d, "meta.json")))
    nf = meta["frames"]
    w1 = [load(os.path.join(d, f"working-{f:02d}.png"), 1) for f in range(nf)]
    w2 = [load(os.path.join(d, f"working-{f:02d}.png"), 2) for f in range(nf)]
    idle1, idle2 = load(os.path.join(d, "idle.png"), 1), load(os.path.join(d, "idle.png"), 2)
    plate2 = load(os.path.join(d, "plate.png"), 2)
    he2 = load(os.path.join(args.he, str(n), "working-00.png"), 2)
    bb1 = bbox_of([idle1] + w1[::3])
    bb2 = tuple(2 * v for v in bb1)
    g1 = [with_port(f, "north", 1).crop(bb1) for f in w1]
    g2 = [with_port(f, "north", 2).crop(bb2) for f in w2]
    gi2 = with_port(idle2, "north", 2).crop(bb2)
    kf = KEYF[n]
    FIRST[n], FIRST2[n] = g1[kf], g2[kf]
    s1 = gif(g1, os.path.join(args.out, f"{n}-{o['slug']}-1x.gif"))
    s2 = gif(g2, os.path.join(args.gif2, f"{n}-{o['slug']}-2x.gif"))
    paths = overlay(g2[kf], meta, bb1)
    mm = motion_map(plate2.crop(bb2), [f.crop(bb2) for f in w2])
    mmg = ground(mm.size, ((ORIGIN[0] - bb1[0]) * 2, (ORIGIN[1] - bb1[1]) * 2), 128)
    mmg.alpha_composite(mm)
    # the sight glass in both gases, 4x: where helium's frame 0 differs from siderane's
    diff = ImageChops.difference(w2[0].convert("RGB"), he2.convert("RGB")).convert("L").point(lambda v: 255 if v > 12 else 0)
    gb = diff.getbbox()
    glass = []
    if gb:
        cx, cy = (gb[0] + gb[2]) / 2, (gb[1] + gb[3]) / 2
        hw, hh = max(48, (gb[2] - gb[0]) / 2 + 24), max(40, (gb[3] - gb[1]) / 2 + 24)
        box = (int(cx - hw), int(cy - hh), int(cx + hw), int(cy + hh))
        for im, cap in ((with_port(w2[0], "north", 2), "siderane (#A8D929)"),
                        (with_port(he2, "north", 2), "helium-3 (#8CC7E6)"),
                        (with_port(idle2, "north", 2), "idle: empty")):
            c = im.crop(box)
            glass.append(captioned(c.resize((c.width * 2, c.height * 2), Image.NEAREST), cap, 13))
    RC = (8, 24, 344, 352)
    rots = [captioned(with_port(w1[0], "north", 1).crop(RC), "north (as built)", 13)]
    for dn in ("east", "south", "west"):
        rots.append(captioned(with_port(load(os.path.join(d, f"rot-{dn}.png"), 1), dn, 1).crop(RC), dn, 13))
    keys = [captioned(g1[i], f"frame {i}", 12) for i in range(0, nf, 3)]
    M = figures(n)
    MEAS[n] = dict(gif_1x_mb=s1, gif_2x_mb=s2, pipes=len(meta["pipes"]),
                   loose=sum(1 for P in meta["pipes"] if not P["ok"]))
    r1 = hrow([captioned(g2[kf], f"WORKING, 2x (frame {kf} of {nf}), the vanilla pipe joined north"),
               captioned(gi2, "IDLE, 2x (stopped where it is, the glass empty)")])
    r2 = hrow([captioned(paths, "THE CHAIN, 2x: the gas from the vent to the outlet, numbered"),
               captioned(mmg, "MOTION MAP, 2x: magenta changes over the loop")])
    W = max(r1.width, r2.width) + 20
    head_lines = wrap(COMMON, 14, W - 24)
    head_ = Image.new("RGBA", (W, 76 + 20 * len(head_lines)), BG)
    dd = ImageDraw.Draw(head_)
    text(dd, (10, 6), f"GAS PUMP 3x3, OPTIONS -- TAKE {n}: {o['name']}", 24, HEAD, True)
    for i, ln in enumerate(wrap(o["pitch"], 16, W - 24)):
        text(dd, (10, 40 + 22 * i), ln, 16, TEXT, True)
    y0 = 40 + 22 * len(wrap(o["pitch"], 16, W - 24)) + 6
    head_ = head_.crop((0, 0, W, y0 + 20 * len(head_lines) + 6))
    dd = ImageDraw.Draw(head_)
    for i, ln in enumerate(head_lines):
        text(dd, (10, y0 + 20 * i), ln, 14, SUB)
    chain = [f"{L['n']}. {L['text']}" for L in sorted(meta["labels"], key=lambda L: L["n"])]
    parts = [head_, r1, r2, block("THE CHAIN (the numbers above)", chain, W, tight=True)]
    if glass:
        parts.append(captioned(hrow(glass), "THE SIGHT GLASS, 4x: the gas as paint in the vent's colour"))
    parts += [captioned(vstack([hrow(rots[:2], 10), hrow(rots[2:], 10)], 10), "FOUR TURNS, 1x (working frame 0, the whole machine turned; the output "
                                        "turns with it)"),
              captioned(vstack([hrow(keys[:4], 6), hrow(keys[4:], 6)], 6), f"KEY FRAMES, 1x (every third of {nf}; the loop at 70 ms a frame in the GIF)"),
              block("MOTION (for spec 6.2)", o["motion"], W, tight=True),
              block("MEASURED (tools/blender/measure.py on gp_pack.py's 1x sheets, north)", fig_lines(M, study), W),
              block("EVERY LINE GOES SOMEWHERE (the kit's check_ends: each end in a part, or within 0.04 t)",
                    pipe_lines(meta), W, size=12, tight=True)]
    sheet = vstack(parts, width=W)
    pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
    pad.alpha_composite(sheet, (10, 10))
    path = os.path.join(args.out, f"{n}-{o['slug']}.png")
    pad.convert("RGB").save(path)
    print(path, pad.size, MEAS[n])


for n in [int(v) for v in args.only.split(",")]:
    build(n)

if len(FIRST) == 3:
    refs = [("vanilla pumpjack 3x3 (frame 0)", ref_pumpjack()), ("the 2x2 Gas Pump now (siderane)", ref_gas_pump()),
            ("the Vent Pump 3x3 (round 5 (a), signed off)", ref_vent_pump())]
    rowr = hrow([captioned(im, cap, 13) for cap, im in refs], 16)
    row1 = hrow([captioned(FIRST[n], f"{n}. {TAKES[n]['name'].title()}", 13) for n in (1, 2, 3)], 16)
    row2 = hrow([captioned(FIRST2[n], f"{n}. {TAKES[n]['name'].title()}, 2x", 13) for n in (1, 2, 3)], 16)
    W = max(rowr.width, row1.width, row2.width) + 20
    head_ = Image.new("RGBA", (W, 60), BG)
    dd = ImageDraw.Draw(head_)
    text(dd, (10, 6), "GAS PUMP 3x3 -- OPTIONS: THREE TAKES BESIDE THE REFERENCES", 20, HEAD, True)
    text(dd, (10, 34), "64 px a tile, one ground. Top: vanilla's pumpjack, the 2x2 Gas Pump as shipped, the Vent Pump. "
                       "Then the three takes at 1x (working), and at 2x.", 13, SUB)
    sheet = vstack([head_, rowr, row1, row2], 16, width=W)
    pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
    pad.alpha_composite(sheet, (10, 10))
    pad.convert("RGB").save(os.path.join(args.out, "contact-sheet.png"))
    print(os.path.join(args.out, "contact-sheet.png"), pad.size)
json.dump(MEAS, open(os.path.join(args.gif2, "sheet-sizes.json"), "w"), indent=1)
