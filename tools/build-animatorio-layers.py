#!/usr/bin/env python3
"""Turn an Animatorio asset into the two layers Factorio actually wants.

Animatorio (https://github.com/Onoulade/Animatorio) animates a *whole* sprite:
give it a static plate and a `piston` layer and it hands back N complete frames.
That is the right thing for a preview and the wrong thing for an entity. Vanilla
does not ship N copies of a machine -- look at the biochamber
(`space-age/prototypes/entity/biochamber-pictures.lua`): one static plate at
`frame_count = 1, repeat_count = 64`, and a *small* animated layer over it. Only
the part that moves is paid for 64 times.

So this splits Animatorio's output back into that pair:

    housing   the plate with one rectangular window punched out, one frame
    frames    that window's contents, N frames, packed into a sheet

and the split is checked rather than asserted: every frame is reassembled from
the two layers and compared to Animatorio's own composite. It must be exact --
not close -- because the two layers are drawn at the same `scale` and any drift
shows up as a seam around the window.

**Why the frames are not rendered at Animatorio's own phases.** Its `piston`
offers `sine` or `triangle`, and both are symmetric: the fall takes as long as
the rise, and a weight that falls at the speed it rose reads as being *lowered*.
That is the exact failure `building-spec-drop-crusher.md` §9 warns about, and
frames play at a constant rate, so the acceleration has to live in the spacing.

Its phase-to-displacement map is `t = 0.5 - 0.5*cos(2*pi*p)`, which is monotonic
over `p` in [0, 1/2], so it inverts. We choose the displacement per frame -- two
thirds of the loop to a constant-speed geared rise, one third to a fall whose
distance goes as t squared -- solve back for the phase that produces it, and ask
Animatorio for *that* frame. Nothing is patched; the tool is called at the
phases we want.

**Frame 0 is the plate, byte for byte.** The fall starts at rest, and the piston
handler returns without touching the frame at zero displacement. That matters
more than it looks: an assembling machine with no `idle_animation` stops on a
frame, and a stopped crusher should be the still that was approved -- the crown
standing proud of its collar -- not a machine caught mid-stroke. It is checked
below too.

Usage:
  tools/build-animatorio-layers.py --asset graphics/entity/<b>/stroke.json \\
      --window 79 0 127 54 \\
      --housing-out graphics/entity/<b>/stroke-housing.png \\
      --frames-out graphics/entity/<b>/stroke.png

  --animatorio PATH, or $ANIMATORIO, must point at a checkout of the tool.
"""

import argparse
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image


def load_animatorio(path):
    """Import Animatorio from a checkout that is not on the path."""
    if path is None:
        sys.exit("build-animatorio-layers: pass --animatorio PATH or set "
                 "$ANIMATORIO to a checkout of github.com/Onoulade/Animatorio")
    path = Path(path).expanduser().resolve()
    if not (path / "generate_animations.py").is_file():
        sys.exit(f"build-animatorio-layers: no generate_animations.py under {path}")
    sys.path.insert(0, str(path))
    import asset_store
    import generate_animations
    return asset_store, generate_animations


def displacement(i, frames, fall):
    """0 is the crown seated at the top of the stroke -- the plate; 1 is the bottom.

    Two thirds of the loop lifts at a constant rate, because a rack and pinion
    has no other speed. One third falls, and the distance goes as the square of
    the time, because gravity is the entire premise of the building.
    """
    if i <= fall:
        return (i / fall) ** 2
    return 1 - (i - fall) / (frames - fall)


def phase_for(d):
    """Invert Animatorio's t = 0.5 - 0.5*cos(2*pi*p) on its rising half."""
    return math.acos(max(-1.0, min(1.0, 1 - 2 * d))) / math.tau


def pack(frames, columns):
    w, h = frames[0].size
    rows = math.ceil(len(frames) / columns)
    sheet = Image.new("RGBA", (w * columns, h * rows))
    for i, frame in enumerate(frames):
        sheet.paste(frame, ((i % columns) * w, (i // columns) * h))
    return sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asset", required=True, type=Path)
    ap.add_argument("--window", required=True, type=int, nargs=4,
                    metavar=("X0", "Y0", "X1", "Y1"),
                    help="the rectangle the animated layer covers, in plate pixels")
    ap.add_argument("--housing-out", required=True, type=Path)
    ap.add_argument("--frames-out", required=True, type=Path)
    ap.add_argument("--animatorio", default=os.environ.get("ANIMATORIO"))
    ap.add_argument("--fall", type=int, default=8,
                    help="frames given to the fall; the rest lift (default 8 of 24)")
    ap.add_argument("--columns", type=int, default=6)
    a = ap.parse_args()

    store, ga = load_animatorio(a.animatorio)
    asset = json.loads(a.asset.read_text())
    here = a.asset.parent
    plate = Image.open(here / asset["source"]).convert("RGBA")
    count = int(asset.get("frame_count", 24))

    composites = [
        ga.animate_frame(plate, asset["motions"],
                         phase_for(displacement(i, count, a.fall)),
                         asset.get("lighting"))
        for i in range(count)
    ]

    x0, y0, x1, y1 = a.window
    if (x1 - x0) % 2 or (y1 - y0) % 2:
        sys.exit("build-animatorio-layers: the window must be even in both axes, "
                 "or its centre lands on half an in-game pixel at scale 0.5")

    # The plate, with the window punched clean out. Everything the stroke can
    # touch lives in that hole; everything else is the approved plate untouched.
    housing = plate.copy()
    housing.paste((0, 0, 0, 0), (x0, y0, x1, y1))
    frames = [c.crop((x0, y0, x1, y1)) for c in composites]

    # Prove the pair reassembles. A seam here is a seam in the game.
    for i, composite in enumerate(composites):
        # The hole is fully transparent, so drawing the window over it in the
        # engine lands the window's own pixels -- feathered edges included.
        rebuilt = housing.copy()
        rebuilt.paste(frames[i], (x0, y0))
        if rebuilt.tobytes() != composite.tobytes():
            sys.exit(f"build-animatorio-layers: frame {i} does not reassemble -- "
                     f"the window is too small for what the motion moves")
    if composites[0].tobytes() != plate.tobytes():
        sys.exit("build-animatorio-layers: frame 0 is not the plate; a stopped "
                 "machine would not show the still that was approved")

    a.housing_out.parent.mkdir(parents=True, exist_ok=True)
    housing.save(a.housing_out)
    sheet = pack(frames, a.columns)
    sheet.save(a.frames_out)

    # What the prototype has to say, worked out here rather than by hand. The
    # window's centre is offset from the plate's, and that offset is the layer's
    # shift -- in tiles, on top of whatever shift the plate already carries.
    dx = ((x0 + x1) / 2 - plate.width / 2) / 64
    dy = ((y0 + y1) / 2 - plate.height / 2) / 64
    print(f"housing {a.housing_out.name}: {housing.size}, one frame")
    print(f"frames  {a.frames_out.name}: {sheet.size}, {count} frames, "
          f"line_length {a.columns}, each {x1 - x0}x{y1 - y0}")
    print(f"window shift, to add to the plate's own: {{ {dx:g}, {dy:g} }}")
    print(f"reassembles exactly on all {count} frames; frame 0 is the plate")
    px = sheet.size[0] * sheet.size[1] + housing.size[0] * housing.size[1]
    print(f"cost {px:,} px against {plate.width * plate.height * count:,} "
          f"for a full-plate sheet")


if __name__ == "__main__":
    main()
