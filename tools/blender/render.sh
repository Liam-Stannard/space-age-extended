#!/usr/bin/env bash
# Renders a building model and packs it into the sheets its prototype loads.
#
# A model is a Blender Python script that lives beside its spec, in
# concept/<building>/model/ -- design, like the master plate it replaces; only
# signed-off sheets move to graphics/. This directory is the shared pipeline:
#
#   rig.py        camera, sun and colour management, calibrated off vanilla
#   contract.py   render.json: what a model declares (footprint, canvas,
#                 directions, passes, animations, ports) and what its renders
#                 are called; the packers act on nothing else
#   materials.py  the layered finish every building uses
#   downsample.py renders are 4x; this brings them to sprite size
#   pack.py       plate/glow/shadow/light/animation sheets, shifts, geometry checks
#   pack_ports.py pipe_picture / pipe_covers sheets
#   finish.py, tonal.py, preview.py, port_preview.py   measures and review sheets
#   test/box.py   a 2x2 test model that exercises every path through the packers
#
# The model is run as: blender -b --python <model.py> -- <dir> [--ports | --icon]
# and must write <dir>/render.json (contract.declare) and the renders it declares;
# with --icon, <dir>/icon.png.
#
# Blender is not in the repo: point $BLENDER at a binary (the portable Linux
# tarball needs no install).
#
# Usage: tools/blender/render.sh <model.py> <out-dir> [--ports] [--icon]
#   <out-dir>/renders  per-pass renders at sprite size
#   <out-dir>/sheets   packed sheets + meta.json (shifts, sizes, checks)
#   <out-dir>/sheets/ports     with --ports
#   <out-dir>/sheets/icon.png  with --icon: the 64 px mipmap strip
#                              (tools/key-icons.py; its keyed master in sheets/masters/)
set -euo pipefail

USAGE="usage: render.sh <model.py> <out-dir> [--ports] [--icon]"
MODEL="${1:?$USAGE}"
OUT="${2:?$USAGE}"
shift 2
PORTS="" ICON=""
for flag in "$@"; do
  case "$flag" in
    --ports) PORTS=1 ;;
    --icon) ICON=1 ;;
    *) echo "$USAGE" >&2; exit 2 ;;
  esac
done
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLENDER="${BLENDER:?set BLENDER to a Blender 5 binary}"

mkdir -p "$OUT"
"$BLENDER" -b --python "$MODEL" -- "$OUT/hi" > "$OUT/blender.log" 2>&1 \
  || { tail -20 "$OUT/blender.log"; exit 1; }
python3 "$HERE/downsample.py" "$OUT/hi" "$OUT/renders"
python3 "$HERE/pack.py" "$OUT/renders" "$OUT/sheets" > /dev/null
python3 -c "import json,sys; print('checks', json.load(open(sys.argv[1]))['checks'])" "$OUT/sheets/meta.json"
python3 "$HERE/contract.py" plates "$OUT/renders" | while read -r plate; do
  python3 "$HERE/finish.py" "$plate"
  python3 "$HERE/tonal.py" "$plate"
done

if [ -n "$PORTS" ]; then
  "$BLENDER" -b --python "$MODEL" -- "$OUT/ports-hi" --ports > "$OUT/blender-ports.log" 2>&1 \
    || { tail -20 "$OUT/blender-ports.log"; exit 1; }
  python3 "$HERE/downsample.py" "$OUT/ports-hi" "$OUT/ports"
  python3 "$HERE/pack_ports.py" "$OUT/ports" "$OUT/sheets/ports" > /dev/null
  echo "ports packed: $OUT/sheets/ports"
fi

if [ -n "$ICON" ]; then
  "$BLENDER" -b --python "$MODEL" -- "$OUT/icon" --icon > "$OUT/blender-icon.log" 2>&1 \
    || { tail -20 "$OUT/blender-icon.log"; exit 1; }
  [ -f "$OUT/icon/icon.png" ] || { echo "the model rendered no $OUT/icon/icon.png" >&2; exit 1; }
  python3 "$HERE/../key-icons.py" "$OUT/sheets" "$OUT/icon/icon.png:icon"
  echo "icon keyed: $OUT/sheets/icon.png"
fi
