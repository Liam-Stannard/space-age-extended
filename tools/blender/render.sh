#!/usr/bin/env bash
# Renders a building model and packs it into the sheets its prototype loads.
#
# A model is a Blender Python script that lives beside its spec, in
# concept/<building>/model/ -- design, like the master plate it replaces; only
# signed-off sheets move to graphics/. This directory is the shared pipeline:
#
#   rig.py        camera, sun and colour management, calibrated off vanilla
#   materials.py  the layered finish every building uses
#   downsample.py renders are 4x; this brings them to sprite size
#   pack.py       idle/glow/shadow/lamp/animation sheets, shifts, geometry checks
#   pack_ports.py pipe_picture / pipe_covers sheets
#   finish.py, tonal.py, preview.py, port_preview.py   measures and review sheets
#
# Blender is not in the repo: point $BLENDER at a binary (the portable Linux
# tarball needs no install).
#
# Usage: tools/blender/render.sh <model.py> <out-dir> [--ports]
#   <out-dir>/renders  per-pass renders at sprite size
#   <out-dir>/sheets   packed sheets + meta.json (shifts, sizes, checks)
#   <out-dir>/sheets/ports   with --ports
set -euo pipefail

MODEL="${1:?usage: render.sh <model.py> <out-dir> [--ports]}"
OUT="${2:?usage: render.sh <model.py> <out-dir> [--ports]}"
PORTS="${3:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLENDER="${BLENDER:?set BLENDER to a Blender 5.2 binary}"

mkdir -p "$OUT"
"$BLENDER" -b --python "$MODEL" -- "$OUT/hi" > "$OUT/blender.log" 2>&1 \
  || { tail -20 "$OUT/blender.log"; exit 1; }
python3 "$HERE/downsample.py" "$OUT/hi" "$OUT/renders"
python3 "$HERE/pack.py" "$OUT/renders" "$OUT/sheets" > /dev/null
python3 -c "import json,sys; print('checks', json.load(open(sys.argv[1]))['checks'])" "$OUT/sheets/meta.json"
python3 "$HERE/finish.py" "$OUT/renders/idle.png"
python3 "$HERE/tonal.py" "$OUT/renders/idle.png"

if [ "$PORTS" = "--ports" ]; then
  "$BLENDER" -b --python "$MODEL" -- "$OUT/ports-hi" --ports > "$OUT/blender-ports.log" 2>&1 \
    || { tail -20 "$OUT/blender-ports.log"; exit 1; }
  python3 "$HERE/downsample.py" "$OUT/ports-hi" "$OUT/ports"
  python3 "$HERE/pack_ports.py" "$OUT/ports" "$OUT/sheets/ports" > /dev/null
  echo "ports packed: $OUT/sheets/ports"
fi
