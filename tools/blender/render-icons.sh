#!/usr/bin/env bash
# Renders item icons, one render per mip size, and packs them into 120x64 strips.
#
# An item icon is a Blender script in concept/items/<family>/ calling
# icon_rig.main (see icon_rig.py: the camera, the buildings' sun, the framing);
# icon_post.py finishes each size by the script's rules and packs the strips
# through tools/key-icons.py --mips.
#
# Usage: tools/blender/render-icons.sh <icons.py> <out-dir> [--only item[,item]]
#   <out-dir>/hi                 the 4x renders and icons.json
#   <out-dir>/sizes              each size, finished       (icon_post.py)
#   <out-dir>/downscale          the 64 shrunk, for comparison
#   <out-dir>/strips[-downscale]/<finish>/<item>.png, and masters/
# Each run empties these first. Ends, pass or fail, by writing
# <out-dir>/render.done ("exit <code>") and printing it last, as render.sh does:
# start this in the background and let the harness say when it exits.
# Blender is the one tools/paths.conf names (BLENDER, read through
# tools/paths.sh); exit 1, naming the file and the key, when it cannot be used.
set -euo pipefail

USAGE="usage: render-icons.sh <icons.py> <out-dir> [--only item[,item]]"
SCRIPT="${1:?$USAGE}"
OUT="${2:?$USAGE}"
shift 2
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../paths.sh"
sae_blender BLENDER_BIN || exit 1

mkdir -p "$OUT"
rm -f "$OUT/render.done"
trap 'code=$?; echo "exit $code" > "$OUT/render.done"; echo "exit $code"' EXIT
rm -rf "${OUT:?}/hi" "${OUT:?}/sizes" "${OUT:?}/downscale" "${OUT:?}/strips" "${OUT:?}/strips-downscale"
"$BLENDER_BIN" -b --python "$SCRIPT" -- "$OUT/hi" "$@" > "$OUT/blender.log" 2>&1 \
  || { tail -20 "$OUT/blender.log"; exit 1; }
grep '^icon ' "$OUT/blender.log" || true
python3 "$HERE/icon_post.py" "$OUT/hi" "$OUT"
