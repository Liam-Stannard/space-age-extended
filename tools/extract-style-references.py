#!/usr/bin/env python3
"""Cut clean single-frame reference sprites out of the local Factorio install.

Every generation round attaches vanilla sprites so the generator has the game's
camera and finish in front of it rather than a paragraph describing them. Four
buildings carry that job, and between them they bracket the range a Core
building can sit in:

  assembling-machine-3   the house camera. The most-seen machine in the game and
                         the one a player's eye is calibrated to.
  foundry                a big Space Age machine at the current art standard --
                         the finish and detail density to match.
  rocket-silo            the deep end: a building you look *into*, with a visible
                         far inner wall. The camera reference for anything with
                         a shaft.
  electromagnetic-plant  coils, windings and heavy cable runs treated as a
                         subject in their own right.

**These files are Wube's art and must never be copied into the repo.** They are
written to a scratch directory, attached to a prompt, and thrown away; the mod
ships none of them. That is why this is a tool that extracts them on demand
rather than a `graphics/reference/` folder.

Each sprite is composited from its real layers at their real shifts, read off a
data-stage dump, so what gets attached is the machine as the engine assembles
it rather than a raw sheet with the animation tiled across it. Shadows are left
out: the plates we generate must not carry a baked one, and attaching a
reference with one invites exactly that.

  tools/extract-style-references.py [--out DIR]
"""

import argparse
import os

from PIL import Image

# The Steam install. Everything below is relative to <install>/data.
DATA = os.path.expanduser(
    "~/.steam/debian-installation/steamapps/common/Factorio/data")

# name -> list of (relative path, width, height, shift_x, shift_y, line_length, frame)
# Widths, heights and shifts are the engine's own, read from a data-raw dump.
# Shift is in tiles; the plates are drawn at 2x and shipped at scale 0.5, so one
# tile is 64 source pixels.
REFERENCES = {
    "assembling-machine-3": [
        ("base/graphics/entity/assembling-machine-3/assembling-machine-3-base.png",
         196, 192, -0.015625, 0.078125, 1, 0),
        ("base/graphics/entity/assembling-machine-3/assembling-machine-3-anim.png",
         140, 160, 0.03125, -0.5, 8, 0),
    ],
    "foundry": [
        ("space-age/graphics/entity/foundry/foundry-base.png",
         356, 384, -0.015625, -0.296875, 1, 0),
    ],
    "rocket-silo": [
        ("base/graphics/entity/rocket-silo/06-rocket-silo.png",
         628, 612, 0.0625, 0.109375, 1, 0),
    ],
    "electromagnetic-plant": [
        ("space-age/graphics/entity/electromagnetic-plant/"
         "electromagnetic-plant-main-rotate-continue.png",
         220, 302, 0.0625, -0.375, 8, 0),
    ],
}

PX_PER_TILE = 64


def frame(path, w, h, line_length, index):
    sheet = Image.open(path).convert("RGBA")
    col, row = index % line_length, index // line_length
    return sheet.crop((col * w, row * h, col * w + w, row * h + h))


def build(layers):
    """Composite layers onto one canvas, each centred at its own shift."""
    placed = []
    for rel, w, h, sx, sy, line, idx in layers:
        img = frame(os.path.join(DATA, rel), w, h, line, idx)
        cx, cy = sx * PX_PER_TILE, sy * PX_PER_TILE
        placed.append((img, cx - w / 2, cy - h / 2))   # top-left, relative to origin

    left = min(x for _, x, _ in placed)
    top = min(y for _, _, y in placed)
    right = max(x + im.width for im, x, _ in placed)
    bottom = max(y + im.height for im, _, y in placed)

    out = Image.new("RGBA", (int(right - left), int(bottom - top)), (0, 0, 0, 0))
    for im, x, y in placed:
        out.alpha_composite(im, (int(x - left), int(y - top)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("TMPDIR", "/tmp") + "/sae-style-refs")
    args = ap.parse_args()

    if not os.path.isdir(DATA):
        raise SystemExit("Factorio data not found at %s" % DATA)
    os.makedirs(args.out, exist_ok=True)

    for name, layers in REFERENCES.items():
        img = build(layers)
        path = os.path.join(args.out, name + ".png")
        img.save(path)
        print("  %-24s %4dx%-4d  %s" % (name, img.width, img.height, path))

    print("\nAttach all four to every generation round. Vanilla art -- scratch only,"
          "\nnever copied into the repo.")


if __name__ == "__main__":
    main()
