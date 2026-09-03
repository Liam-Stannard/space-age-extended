#!/usr/bin/env python3
"""Generate the Thermionic Generator's derived sprite sheets from vanilla's
nuclear-reactor graphics.

Why this exists: prototypes/entity.lua reuses vanilla nuclear reactor's
sprites for the generator's body, but two things can't be used as-is.

1. Heat-pipe connection patches. Vanilla's reactor-connect-patches.png
   (and the -heated variant) are 768x128 sheets: 12 columns of 64x64
   patches, one per heat_buffer connection in vanilla's order
   (N corner-left, N mid, N corner-right, E corner-top, E mid,
   E corner-bottom, S corner-right, S mid, S corner-left, W corner-bottom,
   W mid, W corner-top), with row 0 = connected and row 1 = disconnected.
   ReactorPrototype requires `variation_count >= #heat_buffer.connections`,
   and the generator has 16 connections (4 per side, in order
   N,N,N,N,E,E,E,E,S,S,S,S,W,W,W,W), so this script builds 16-column
   (1024x128) sheets by mapping each side's four connections onto vanilla's
   [corner, mid, mid, corner] columns for that side -- 1-based vanilla
   columns 1,2,2,3 / 4,5,5,6 / 7,8,8,9 / 10,11,11,12 -- for both rows.

The generated files are committed to graphics/entity/thermionic-generator/
so the mod doesn't need this script at load time; re-run it if the
mapping or the source sprites change.

Usage:
    tools/generate-thermionic-graphics.py [path-to-factorio-data-dir]

The data dir is the one containing base/ (defaults to the Steam install
path tools/check-data-stage.sh also looks in). Requires Pillow.
"""

import os
import sys

from PIL import Image

DEFAULT_DATA_DIR = os.path.expanduser(
    "~/.steam/debian-installation/steamapps/common/Factorio/data"
)
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO_ROOT, "graphics", "entity", "thermionic-generator")

PATCH = 64
VANILLA_COLUMNS = 12
ROWS = 2
# 0-based vanilla column for each of the generator's 16 connections.
COLUMN_MAP = [0, 1, 1, 2, 3, 4, 4, 5, 6, 7, 7, 8, 9, 10, 10, 11]


def build_patch_sheet(src_path, dst_path):
    src = Image.open(src_path).convert("RGBA")
    expected = (PATCH * VANILLA_COLUMNS, PATCH * ROWS)
    if src.size != expected:
        raise SystemExit(f"{src_path}: expected {expected}, got {src.size}")
    dst = Image.new("RGBA", (PATCH * len(COLUMN_MAP), PATCH * ROWS), (0, 0, 0, 0))
    for row in range(ROWS):
        for dst_col, src_col in enumerate(COLUMN_MAP):
            box = (src_col * PATCH, row * PATCH, (src_col + 1) * PATCH, (row + 1) * PATCH)
            dst.paste(src.crop(box), (dst_col * PATCH, row * PATCH))
    dst.save(dst_path, optimize=True)
    print(f"wrote {dst_path} {dst.size}")


def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATA_DIR
    reactor_dir = os.path.join(data_dir, "base", "graphics", "entity", "nuclear-reactor")
    if not os.path.isdir(reactor_dir):
        raise SystemExit(f"no nuclear-reactor graphics dir at {reactor_dir}")
    os.makedirs(OUT_DIR, exist_ok=True)
    build_patch_sheet(
        os.path.join(reactor_dir, "reactor-connect-patches.png"),
        os.path.join(OUT_DIR, "connect-patches.png"),
    )
    build_patch_sheet(
        os.path.join(reactor_dir, "reactor-connect-patches-heated.png"),
        os.path.join(OUT_DIR, "connect-patches-heated.png"),
    )


if __name__ == "__main__":
    main()
