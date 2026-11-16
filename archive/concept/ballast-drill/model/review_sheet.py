#!/usr/bin/env python3
"""The Ballast Drill's finished review sheet.

  python3 review_sheet.py <out-dir> <review.png>

  <out-dir>  render.sh's output directory, run with --ports --icon: renders/ (idle,
             still, shadow, lamp, chute-NN, stroke-NN, ore-NN, door) and sheets/
             (meta.json, icon.png)

Its companions, from the shared tools:
  preview.py <out-dir>/renders <stroke.gif> --gif stroke --speed 0.4   the stroke at game speed
  port_preview.py <out-dir> <pipes.png>          the pipe pictures on every connection

Layered as the engine draws them, on one ground at 64 px a tile with the tile grid: the
shadow at 50 %, the plate, the chute's frame, the stroke's frame, the ore's and the dust's
frames (while working), and the status lamp's white lens tinted with vanilla's mining-drill colours.

Row 1: the adopted plate; then facing north, east, south and west, working (lamp green,
       ore falling). On each: vanilla's big-mining-drill output rectangle (cyan) and our
       chute's crop (magenta), vanilla's output-particles rectangle (yellow) and our
       ore's crop (white), with the offsets in the label.
Row 2: idle (lamp red) facing north; the press at 1.5x, working, frames 0, 4, 5, 7, 10 and
       18 of the stroke (raised, falling, the landing, the dust out, settling, lifting).
Row 3: the chute and its ore at 3x in every direction, shut bay and working.
Row 4: the icon strip, and the icon at 1x on the ground.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import review_blockout as rb  # noqa: E402   the ground, the grid and vanilla's sheets

REPO = rb.REPO
O, C, PPT = rb.O, rb.C, rb.PPT
DIRS = rb.DIRS
LAMP = {"working": (0, 255, 0), "idle": (255, 0, 0)}     # vanilla's mining drill's status colours
PARTICLES = {d: rb.vanilla(d[0].upper(), "output-particles") for d in DIRS}


def tint_lamp(lamp, rgb):
    """The white-cut lens tinted as the engine tints it: its light times the status colour."""
    lum = lamp.convert("L")
    return Image.merge("RGBA", (*[lum.point(lambda v, c=c: v * c // 255) for c in rgb], lamp.getchannel("A")))


def main(out_dir, dest):
    R = os.path.join(out_dir, "renders")
    meta = json.load(open(os.path.join(out_dir, "sheets", "meta.json")))
    ren = lambda stem: Image.open(os.path.join(R, stem + ".png")).convert("RGBA")  # noqa: E731

    def machine(d, f_stroke=0, f_chain=0, f_ore=None, status="working", with_shadow=True):
        c = rb.panel()
        if with_shadow:
            rb.shadow(c, ren(f"shadow-{d}"))
        rb.put(c, ren(f"idle-{d}"))
        rb.put(c, ren(f"chute-{f_chain:02d}-{d}"))
        rb.put(c, ren(f"stroke-{f_stroke:02d}-{d}"))
        if f_ore is not None:
            rb.put(c, ren(f"ore-{f_ore:02d}-{d}"))
            rb.put(c, ren(f"dust-{f_stroke:02d}-{d}"))      # (round 6) working only, as the ore
        lamp = ren(f"lamp-{d}")
        c.alpha_composite(tint_lamp(lamp, LAMP[status]), (round(O - lamp.width / 2), round(O - lamp.height / 2)))
        return c

    def rect(dd, w, h, sx, sy, col):
        dd.rectangle([O + sx * PPT - w / 2, O + sy * PPT - h / 2, O + sx * PPT + w / 2, O + sy * PPT + h / 2],
                     outline=col)

    # row 1
    r1 = []
    c = rb.panel()
    ad = (lambda im: (lambda c: (c.paste(im, (0, 0)), c)[1])(Image.new("RGBA", (im.width, im.height + 49))))(Image.open(os.path.join(HERE, "sheets", "base-north.png")).convert("RGBA"))  # the model's plate (shift 0, -0.25): padded 49 px so the 0.13281 placement below lands it
    rb.put(c, ad, 0, 0.13281)
    rb.grid(c)
    rb.label(c, "adopted plate (base.png)")
    r1.append(c)
    for d in DIRS:
        c = machine(d, f_ore=6)
        rb.grid(c)
        dd = ImageDraw.Draw(c, "RGBA")
        v, vx, vy = rb.vanilla(d[0].upper(), "output")
        rect(dd, v.width, v.height, vx, vy, (0, 230, 255, 220))
        m = meta[f"chute-{d}"]
        rect(dd, *m["size"], *m["shift"], (255, 60, 220, 220))
        p, px_, py_ = PARTICLES[d]
        rect(dd, p.width, p.height, px_, py_, (255, 230, 0, 200))
        o = meta[f"ore-{d}"]
        rect(dd, *o["size"], *o["shift"], (255, 255, 255, 220))
        # (the amended criterion: the ore falls from our chute's mouth, within the bay; it
        # is no longer measured against vanilla's particle shift, drawn yellow for reference)
        rb.label(c, f"{d} working: chute off vanilla ({(m['shift'][0] - vx) * PPT:+.1f}, "
                    f"{(m['shift'][1] - vy) * PPT:+.1f}) px; ore centre from chute's "
                    f"({(o['shift'][0] - m['shift'][0]) * PPT:+.0f}, {(o['shift'][1] - m['shift'][1]) * PPT:+.0f})")
        r1.append(c)

    # row 2
    r2 = []
    c = machine("north", status="idle")
    rb.grid(c)
    rb.label(c, "north, idle (lamp red): no ore")
    r2.append(c)
    box = (round(O - 1.9 * PPT), round(O - 2.4 * PPT), round(O + 1.9 * PPT), round(O + 0.6 * PPT))
    for f in (0, 4, 5, 7, 10, 18):          # (round 6) raised, falling, landing, dust, settling, lifting
        c = machine("north", f_stroke=f, f_ore=f, with_shadow=False)
        im = c.crop(box).resize(((box[2] - box[0]) * 3 // 2, (box[3] - box[1]) * 3 // 2), Image.LANCZOS)
        dr = ImageDraw.Draw(im)
        dr.rectangle([0, 0, 130, 15], fill=(20, 20, 20, 200))
        dr.text((4, 2), f"stroke frame {f}", fill=(235, 235, 235, 255))
        r2.append(im)

    # row 3: the chute and its ore, shut and working
    r3 = []
    for d in DIRS:
        cx, cy = meta[f"chute-{d}"]["shift"]
        for working in (False, True):
            c = rb.panel()
            rb.put(c, ren(f"idle-{d}"))
            if working:
                rb.put(c, ren(f"chute-00-{d}"))
            rb.put(c, ren(f"stroke-00-{d}"))
            if working:
                rb.put(c, ren(f"ore-06-{d}"))
            one = c.crop((round(O + (cx - 0.8) * PPT), round(O + (cy - 0.8) * PPT),
                          round(O + (cx + 0.9) * PPT), round(O + (cy + 0.9) * PPT)))
            im = one.resize((one.width * 3, one.height * 3), Image.NEAREST)
            dr = ImageDraw.Draw(im)
            dr.rectangle([0, 0, im.width, 15], fill=(20, 20, 20, 200))
            dr.text((4, 2), f"{d} {'working' if working else 'shut'}", fill=(235, 235, 235, 255))
            r3.append(im)

    # row 4: the icon
    r4 = []
    icon = Image.open(os.path.join(out_dir, "sheets", "icon.png")).convert("RGBA")
    strip = Image.new("RGBA", (icon.width * 3, icon.height * 3), rb.GROUND)
    strip.alpha_composite(icon.resize((icon.width * 3, icon.height * 3), Image.NEAREST))
    r4.append(strip)

    rows = [rb.row(r1), rb.row(r2), rb.row(r3[:4]), rb.row(r3[4:]), rb.row(r4)]
    W = max(r.width for r in rows)
    sheet = Image.new("RGBA", (W, sum(r.height for r in rows) + 10 * (len(rows) - 1)), rb.GAP)
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height + 10
    sheet.save(dest)
    print(dest, sheet.size)


if __name__ == "__main__":
    main(*sys.argv[1:])
