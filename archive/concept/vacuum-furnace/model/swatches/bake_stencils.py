#!/usr/bin/env python3
"""The Vacuum Furnace's stencilled markings, as masks the model projects onto its plates.

  python3 concept/vacuum-furnace/model/swatches/bake_stencils.py

Spec 3.3, "Signature finish": within the building, variation comes partly from
small stencilled markings: one per face at most, bold enough to
read at 2x (round 2) -- the unit's number on the south face, VAC on the hatch. Each mask is white where the paint went on, black
where it did not, with a stencil's bridges cut through the letters; the model
(vacuum_furnace.py, STENCILS) places it on a face, colours it and wears it, so
nothing here carries colour. Sized for a mark 6-8 px tall on the sheet: plain
heavy shapes, because finer lettering does not survive the downsample.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"


def text(name, s, w, h):
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT, int(h * 1.05))
    box = d.textbbox((0, 0), s, font=font)
    d.text(((w - (box[2] - box[0])) / 2 - box[0], (h - (box[3] - box[1])) / 2 - box[1]), s, fill=255, font=font)
    # a stencil's bridges: thin gaps across the letters' middles
    for y in (round(h * 0.48),):
        d.rectangle([0, y, w, y + max(1, h // 24)], fill=0)
    im.save(os.path.join(HERE, f"stencil_{name}.png"))


text("07", "07", 192, 120)
text("vac", "VAC", 288, 112)
