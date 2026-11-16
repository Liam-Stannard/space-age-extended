#!/usr/bin/env python3
"""The ore particles against the amended criterion (the task, 2026-10-09: bulk, ore and the
west pipe picture): neutral (no channel mean more than 12 from another), a loop over 24
frames, and falling from our own chute's mouth within the bay.

  python3 measure_ore.py <out-dir>

<out-dir> is render.sh's output directory: renders/ore-NN-<d>.png and ore-loop-<d>.png,
chute-00-<d>.png, all on the model's canvas with the origin at its centre. Per direction:
  means     the alpha-weighted R, G, B of every frame's chunks, and the spread among them
  loop      the largest channel difference between frame 24 (rendered) and frame 0
  across    the ore's extent across the face, every frame together, against the chute's
            (tiles from the face's centre line): within it is within the bay
  from      where the ore's extent starts along the face's normal, against the chute's
            mouth (the face edge, 2.5 tiles out): the ore falls from the mouth outward
"""
import os
import sys

from PIL import Image, ImageChops

PPT = 64
DIRS = ("north", "east", "south", "west")


def bbox_tiles(im):
    bb = im.getchannel("A").point(lambda a: 255 if a > 24 else 0).getbbox()
    W, H = im.size
    return ((bb[0] - W / 2) / PPT, (bb[1] - H / 2) / PPT, (bb[2] - W / 2) / PPT, (bb[3] - H / 2) / PPT)


def main(out_dir):
    R = os.path.join(out_dir, "renders")
    for d in DIRS:
        frames = [Image.open(os.path.join(R, f"ore-{f:02d}-{d}.png")).convert("RGBA") for f in range(24)]
        loop = Image.open(os.path.join(R, f"ore-loop-{d}.png")).convert("RGBA")
        chute = Image.open(os.path.join(R, f"chute-00-{d}.png")).convert("RGBA")
        sums, wsum = [0.0, 0.0, 0.0], 0.0
        union = Image.new("RGBA", frames[0].size, (0, 0, 0, 0))
        for fr in frames:
            for r, g, b, a in fr.get_flattened_data():
                if a > 24:
                    w = a / 255
                    sums[0] += r * w
                    sums[1] += g * w
                    sums[2] += b * w
                    wsum += w
            union.alpha_composite(fr)
        means = [s / wsum for s in sums]
        spread = max(means) - min(means)
        dloop = max(max(p) for p in ImageChops.difference(loop, frames[0]).get_flattened_data())
        ox0, oy0, ox1, oy1 = bbox_tiles(union)
        cx0, cy0, cx1, cy1 = bbox_tiles(chute)
        # across the face and along its normal, on the screen (north and south: x across;
        # east and west: y across, foreshortened on the screen as the camera draws it)
        if d in ("north", "south"):
            across, c_across = (ox0, ox1), (cx0, cx1)
            start = -oy1 if d == "north" else oy0                        # nearest the body
            mouth = -cy0 if d == "north" else cy1
        else:
            across, c_across = (oy0, oy1), (cy0, cy1)
            start = ox0 if d == "east" else -ox1
            mouth = cx1 if d == "east" else -cx0
        inside = c_across[0] - 1 / PPT <= across[0] and across[1] <= c_across[1] + 1 / PPT
        print(f"{d:5s}  means R {means[0]:.1f} G {means[1]:.1f} B {means[2]:.1f}  spread {spread:.1f} "
              f"({'neutral' if spread <= 12 else 'NOT neutral'})  loop max diff {dloop}  "
              f"across {across[0]:+.2f}..{across[1]:+.2f} vs chute {c_across[0]:+.2f}..{c_across[1]:+.2f} "
              f"({'within' if inside else 'OUTSIDE'})  starts {start:+.2f} vs mouth {mouth:+.2f} "
              f"({(start - mouth) * PPT:+.0f} px)")


if __name__ == "__main__":
    main(*sys.argv[1:])
