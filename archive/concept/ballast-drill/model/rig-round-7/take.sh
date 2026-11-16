#!/usr/bin/env bash
# One take of the rig round (task ballast-drill-ports, T03d; T03f: rig-round-3, the frame; T03g:
# rig-round-4, the cast take's gaps filled; T03h: rig-round-5, the drill on a raised plate; T03i:
# rig-round-6, the drill rebuilt to option B2 on the 0.85 plate), end to end:
#   take.sh <take> <out-dir>
# 1. the B2 body's own passes (rig_take.py's anim pass: plate, still, shadow, lamp, chute, ore,
#    stroke, dust, the take's dry rig in the plate) through tools/blender/render.sh: the gear-houses,
#    guide columns and shoes the stroke draws moved, so nothing is taken from the signed-off sheets
# 2. the wet rig layers through render.sh --collide (the clash check first: a clash stops it)
# 3. combine.py: wet and dry sheets directories, as the engine layers them (the animated layers
#    from step 1)
# 4. measure.py on both (joins at the big drill's four connections, turned)
# SAE_RIG_ONE=north: that direction alone (rig_parts.py ONE), for the proof.
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
CONN=(--connection -2,-1,W --connection 2,-1,E --connection 1,2,S --connection -1,2,S)

SAE_RIG_TAKE="$TAKE" SAE_RIG_PASS=rig "$REPO/tools/blender/render.sh" "$MODEL" "$OUT/rig" --collide
SAE_RIG_TAKE="$TAKE" SAE_RIG_PASS=anim "$REPO/tools/blender/render.sh" "$MODEL" "$OUT/plate"
ONEARG=()
[ -n "${SAE_RIG_ONE:-}" ] && ONEARG=(--one "$SAE_RIG_ONE")
python3 "$HERE/combine.py" "$OUT/plate/sheets" "$OUT/plate" "$OUT/rig" "$OUT/wet" "${ONEARG[@]}"
python3 "$HERE/combine.py" "$OUT/plate/sheets" "$OUT/plate" "$OUT/rig" "$OUT/dry" --dry "${ONEARG[@]}"
python3 "$REPO/tools/blender/measure.py" "$OUT/wet" --footprint 5x5 --out "$OUT/measures-wet" "${CONN[@]}" \
  --title "Ballast drill rig, take $TAKE, wet" > "$OUT/measure-wet.log" 2>&1 || echo "measure wet: exit $?"
python3 "$REPO/tools/blender/measure.py" "$OUT/dry" --footprint 5x5 --out "$OUT/measures-dry" \
  --title "Ballast drill rig, take $TAKE, dry" > "$OUT/measure-dry.log" 2>&1 || echo "measure dry: exit $?"
tail -3 "$OUT/measure-wet.log"
