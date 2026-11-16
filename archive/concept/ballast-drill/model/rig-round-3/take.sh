#!/usr/bin/env bash
# One take of the rig round (task ballast-drill-ports, T03d; T03f: rig-round-3, the frame), end to end:
#   take.sh <take> <out-dir>
# 1. the plate (casings cut back, the dry rig) through tools/blender/render.sh
# 2. the wet rig layers through render.sh --collide (the clash check first: a clash stops it)
# 3. combine.py: wet and dry sheets directories, as the engine layers them
# 4. measure.py on both (joins at the big drill's four connections, turned), and on the
#    signed-off sheets for the finish beside them
# Writes <out-dir>/take.done ("exit <code>") when it ends.
set -euo pipefail
TAKE="${1:?take}"
OUT="${2:?out-dir}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
mkdir -p "$OUT"
rm -f "$OUT/take.done"
trap 'code=$?; echo "exit $code" > "$OUT/take.done"' EXIT
MODEL="$HERE/rig_take.py"
SIGNED="$REPO/concept/ballast-drill/model/sheets"
CONN=(--connection -2,-1,W --connection 2,-1,E --connection 1,2,S --connection -1,2,S)

SAE_RIG_TAKE="$TAKE" SAE_RIG_PASS=plate "$REPO/tools/blender/render.sh" "$MODEL" "$OUT/plate"
SAE_RIG_TAKE="$TAKE" SAE_RIG_PASS=rig "$REPO/tools/blender/render.sh" "$MODEL" "$OUT/rig" --collide
python3 "$HERE/combine.py" "$SIGNED" "$OUT/plate" "$OUT/rig" "$OUT/wet"
python3 "$HERE/combine.py" "$SIGNED" "$OUT/plate" "$OUT/rig" "$OUT/dry" --dry
python3 "$REPO/tools/blender/measure.py" "$OUT/wet" --footprint 5x5 --out "$OUT/measures-wet" "${CONN[@]}" \
  --title "Ballast drill rig, take $TAKE, wet" > "$OUT/measure-wet.log" 2>&1 || echo "measure wet: exit $?"
python3 "$REPO/tools/blender/measure.py" "$OUT/dry" --footprint 5x5 --out "$OUT/measures-dry" \
  --title "Ballast drill rig, take $TAKE, dry" > "$OUT/measure-dry.log" 2>&1 || echo "measure dry: exit $?"
tail -3 "$OUT/measure-wet.log"
