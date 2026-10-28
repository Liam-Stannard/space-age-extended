#!/usr/bin/env python3
"""Vent Pump, round 5 (T05): a variant's 4x renders packed as 1x sheets for measure.py.

  python3 vp5_pack.py <render-dir> <out-dir>

measure.py (factorio-tools-skills worktree, tools/blender/measure.py, committed there, reviewed PASS)
reads a packed sheets directory: meta.json and the sheets, 64 px a tile, each placed at its shift
(tiles) from the entity's origin. This writes, from a variant's renders (vpb5_08_gas_lift_tower.py,
352 px canvas at 1x, the origin at (160, 208)):

  base.png      the plate (idle, no ground) at 1x: the plate measure.py names "base"
  shadow.png    the catcher's shadow alone (working frame 0 where the plate is empty)
  working.png   the working loop at 1x, 8 frames a row, the shadow cut away (alpha held to the
                plate's, dilated a px, so a moving part stays whole): an animation drawn as paint
  meta.json     {"base": {size, shift}, "shadow": {size, shift}, "working": {size, shift, frames,
                line_length}}

Downsampled as tools/blender/downsample.py does (premultiplied, LANCZOS), then the highlight roll-off
again (vp5_roll.py: the downsample's overshoot at a bright edge lands px back on 255).
"""
import json
import os
import sys

from PIL import Image, ImageChops, ImageFilter

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vp5_roll import roll  # noqa: E402  (vp5_shoulder.py's roll-off again after the downsample)

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
C, ORIGIN = 352, (160, 208)
SHIFT = [(C / 2 - ORIGIN[0]) / 64, (C / 2 - ORIGIN[1]) / 64]
meta = json.load(open(os.path.join(src, "meta.json")))
nf = meta["frames"]


def down(name):
    im = Image.open(os.path.join(src, name)).convert("RGBa")
    return roll(im.resize((C, C), Image.LANCZOS).convert("RGBA"))


plate = down("plate.png")
plate.save(os.path.join(out, "base.png"))
pa = plate.getchannel("A")
keep = pa.point(lambda v: 255 if v > 0 else 0).filter(ImageFilter.MaxFilter(3))
w0 = down("working-00.png")
sh = w0.copy()
sh.putalpha(ImageChops.multiply(w0.getchannel("A"), ImageChops.invert(keep)))
sh.save(os.path.join(out, "shadow.png"))
line = 8
rows = (nf + line - 1) // line
sheet = Image.new("RGBA", (C * line, C * rows))
for f in range(nf):
    fr = down(f"working-{f:02d}.png")
    fr.putalpha(ImageChops.multiply(fr.getchannel("A"), keep))
    sheet.paste(fr, ((f % line) * C, (f // line) * C))
sheet.save(os.path.join(out, "working.png"))
json.dump({"base": dict(size=[C, C], shift=SHIFT), "shadow": dict(size=[C, C], shift=SHIFT),
           "working": dict(size=[C, C], shift=SHIFT, frames=nf, line_length=line)},
          open(os.path.join(out, "meta.json"), "w"), indent=1)
print(out, nf, "frames")
