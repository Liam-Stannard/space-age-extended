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

Three more are **per-building style references**, one machine each, because the
nine-building set came back looking like one machine drawn nine times when they
all shared a reference. These are the ones cut so far:

  centrifuge             Dross Classifier
  nuclear-reactor        Coil Separator -- heavy, dark, contained power. It
                         covers the ground the electromagnetic plant would,
                         while that machine is the separator's anti-read and so
                         must not be attached to it at all.
  recycler               Whisker Comber
  chemical-plant         Helium Concentrator
  cryogenic-plant        Vacuum Furnace
  pumpjack               Crust Tap -- and this one is also that building's
                         anti-read, so the prompt must label it a camera
                         reference and say what must not be taken from it.

Two more are **connection references** rather than style ones:

  pump, pipe             how vanilla draws a fluid connector, and the pipe that
                         has to mate with it. Attach these when the thing being
                         got right is the stub itself: a player's pipe arrives at
                         the tile boundary and nowhere else, so the building's
                         own art has to end in something that meets it.

Use --only to cut a subset: the standard four plus the one this building owns.

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
    "centrifuge": [
        ("base/graphics/entity/centrifuge/centrifuge-ABC-integration.png",
         246, 250, 0.015625, 0.09375, 1, 0),
        ("base/graphics/entity/centrifuge/centrifuge-ABC.png",
         194, 248, -0.078125, -0.5625, 8, 0),
    ],
    "nuclear-reactor": [
        ("base/graphics/entity/nuclear-reactor/reactor.png",
         302, 318, -0.15625, -0.21875, 1, 0),
    ],
    "recycler": [
        # The recycler ships in its own data mod, not in space-age.
        ("recycler/graphics/entity/recycler/recycler-N.png",
         170, 304, 0.0625, -0.203125, 8, 0),
    ],
    "chemical-plant": [
        ("base/graphics/entity/chemical-plant/chemical-plant-north-base.png",
         204, 292, 0.03125, -0.28125, 1, 0),
    ],
    "cryogenic-plant": [
        ("space-age/graphics/entity/cryogenic-plant/cryogenic-plant-main.png",
         380, 396, 0.09375, -0.109375, 1, 0),
        ("space-age/graphics/entity/cryogenic-plant/cryogenic-plant-glass.png",
         274, 228, 0.125, -0.234375, 1, 0),
    ],
    # Connection references: how vanilla draws a fluid connector that a player's
    # pipe actually mates with. Attached when a building's pipe stub is the thing
    # being got right, not its style.
    "pump": [
        ("base/graphics/entity/pump/pump-north.png",
         103, 164, 0.25, -0.0265625, 8, 0),
    ],
    "pipe": [
        ("base/graphics/entity/pipe/pipe-straight-vertical.png",
         128, 128, 0, 0, 1, 0),
    ],
    # Added for the Ballast Drill and the Crust Turbine option rounds. The drill
    # is this mod's own drill's parent; the turbine is the building the Crust
    # Turbine exists to NOT be, attached so a sheet can be checked against it.
    "big-mining-drill": [
        ("space-age/graphics/entity/big-mining-drill/North/big-mining-drill-N-still.png",
         324, 324, 0, -0.375, 1, 0),
    ],
    "steam-turbine": [
        ("base/graphics/entity/steam-turbine/steam-turbine-H.png",
         320, 245, 0, -0.0859375, 4, 0),
    ],
    "pumpjack": [
        ("base/graphics/entity/pumpjack/pumpjack-base.png",
         261, 273, -0.0703125, -0.1484375, 1, 0),
        ("base/graphics/entity/pumpjack/pumpjack-horsehead.png",
         206, 172, -0.140625, -0.90625, 8, 0),
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
    ap.add_argument("--only", help="comma-separated subset, e.g. "
                                   "assembling-machine-3,foundry,centrifuge")
    args = ap.parse_args()

    wanted = REFERENCES
    if args.only:
        names = [n.strip() for n in args.only.split(",")]
        missing = [n for n in names if n not in REFERENCES]
        if missing:
            raise SystemExit("unknown reference(s): %s" % ", ".join(missing))
        wanted = {n: REFERENCES[n] for n in names}

    if not os.path.isdir(DATA):
        raise SystemExit("Factorio data not found at %s" % DATA)
    os.makedirs(args.out, exist_ok=True)

    for name, layers in wanted.items():
        img = build(layers)
        path = os.path.join(args.out, name + ".png")
        img.save(path)
        print("  %-24s %4dx%-4d  %s" % (name, img.width, img.height, path))

    print("\nAttach the standard four to every generation round, plus the one this"
          "\nbuilding owns. Vanilla art -- scratch only, never copied into the repo.")


if __name__ == "__main__":
    main()
