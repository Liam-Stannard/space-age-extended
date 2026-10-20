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
#   finish.py, tonal.py, preview.py, port_preview.py   measures and review sheets:
#                 preview.py <out-dir>/renders <sheet.png> [--adopted <png> ...]
#                 port_preview.py <out-dir> <sheet.png>   (after --ports)
#   test/box.py   a 2x2 test model that exercises every path through the packers
#
# The model is run as: blender -b --python <model.py> -- <dir> [--ports | --icon]
# and must write <dir>/render.json (contract.declare) and the renders it declares;
# with --icon, <dir>/icon.png.
#
# Blender is not in the repo: point $BLENDER at a binary (the portable Linux
# tarball needs no install).
#
# **Render device:** $SAE_BLENDER_DEVICE, GPU or CPU; unset means GPU (Liam,
# 2026-10-10). The GPU needs blender.org's build -- a distro package has no GPU
# kernels -- so point $BLENDER at it; SAE_BLENDER_DEVICE=CPU renders on the CPU.
#   SAE_BLENDER_DEVICE=CPU tools/blender/render.sh <model.py> <out-dir>
# GPU is Cycles on OptiX, CUDA if Blender finds no OptiX device (rig.use_device
# enables it in Blender's preferences, which a -b run has none of). The run
# prints the device first: for GPU, a probe Blender reports the backend and the
# card before anything renders, and the run stops there if there is none --
# it never falls back to the CPU unasked. Every Blender pass logs the same
# "render device:" line in its blender*.log. Samples and every other render
# setting are the same on either device.
#
# Usage: tools/blender/render.sh <model.py> <out-dir> [--ports] [--icon]
#                                [--collide [--collide-allow <pattern> ...]]
#   <out-dir>/renders  per-pass renders at sprite size
#   <out-dir>/sheets   packed sheets + meta.json (shifts, sizes, checks)
#   <out-dir>/sheets/ports     with --ports
#   <out-dir>/sheets/icon.png  with --icon: the 64 px mipmap strip
#                              (tools/key-icons.py; its keyed master in sheets/masters/)
#   <out-dir>/collide.log      with --collide: all the model's --collide run printed
#   <out-dir>/collide/         with --collide: what that run wrote (a collide.txt, say)
# These directories, and the 4x renders behind them (<out-dir>/hi, ports-hi and
# icon), belong to this script: each run empties them all first, so nothing a
# model no longer renders, and no sheet packed from it, survives from an earlier
# run. A run without --ports, --icon or --collide leaves none of those behind either.
#
# **--collide** runs the model's own clash check first, before anything renders:
#   $BLENDER -b --python-exit-code 1 --python-expr <make Python's output line-buffered> \
#            --python <model.py> -- <out-dir>/collide --collide
# (measure.py's collide(), which runs it: the --python-expr keeps Blender's own output from
# cutting a COLLIDE line in two)
# A model with a --collide moves every part through every frame and tests it against
# the rest, printing lines that start "COLLIDE". They are read by measure.py's collide
# step -- one rule for both tools, given in its docstring: a line naming a pair ("<a> x
# <b>"), or a clash count above 0, is a clash; so is Blender failing, a Traceback, or
# no count at all (a model with no --collide prints none).
# --collide-allow <pattern> (repeatable, with --collide) is measure.py's: a contact the
# model means, as a regular expression that names the whole pair line -- it must match
# all of the line's text after "COLLIDE ", not just part of it -- and a line it matches
# is allowed. A pattern that matched no line is listed as unused. A clash ends the run
# there, exit 1 (exit 2 for a pattern that is not a regular expression, or that matches
# the empty string, as ".*" or "" do), with nothing rendered. Either way it prints the
# pair lines no pattern allows (the first 40), the lines naming a count, how many lines
# were allowed, any unused pattern, and the verdict. test/collide_box.py is the test box
# with a --collide.
#
# **Waiting for a run:** start this script itself in the background and let
# the harness say when it exits; do not write a polling loop beside it. Every
# run ends, pass or fail, by writing <out-dir>/render.done holding one line,
# "exit <code>", and printing the same line last -- so anything that does have
# to wait on a file has one that always arrives. render.done is removed when a
# run starts, so a stale one never answers for a new run.
set -euo pipefail

USAGE="usage: render.sh <model.py> <out-dir> [--ports] [--icon] [--collide [--collide-allow <pattern> ...]]"
MODEL="${1:?$USAGE}"
OUT="${2:?$USAGE}"
shift 2
PORTS="" ICON="" COLLIDE="" ALLOW=()
while [ $# -gt 0 ]; do
  case "$1" in
    --ports) PORTS=1 ;;
    --icon) ICON=1 ;;
    --collide) COLLIDE=1 ;;
    --collide-allow) [ $# -ge 2 ] || { echo "$USAGE" >&2; exit 2; }; ALLOW+=("$2"); shift ;;
    *) echo "$USAGE" >&2; exit 2 ;;
  esac
  shift
done
if [ ${#ALLOW[@]} -gt 0 ] && [ -z "$COLLIDE" ]; then
  echo "render.sh: --collide-allow goes with --collide" >&2; exit 2
fi
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLENDER="${BLENDER:?set BLENDER to a Blender 5 binary}"

mkdir -p "$OUT"
rm -f "$OUT/render.done"
trap 'code=$?; echo "exit $code" > "$OUT/render.done"; echo "exit $code"' EXIT
SAE_BLENDER_DEVICE="$(echo "${SAE_BLENDER_DEVICE:-GPU}" | tr '[:lower:]' '[:upper:]')"
case "$SAE_BLENDER_DEVICE" in
  CPU|GPU) export SAE_BLENDER_DEVICE ;;
  *) echo "SAE_BLENDER_DEVICE must be CPU or GPU, not $SAE_BLENDER_DEVICE" >&2; exit 2 ;;
esac
if [ "$SAE_BLENDER_DEVICE" = GPU ]; then
  probe="$("$BLENDER" -b --factory-startup --python "$HERE/rig.py" 2>&1 | grep '^render device:' || true)"
  echo "${probe:-render device: GPU asked for, and the Blender probe said nothing}"
  case "$probe" in "render device: GPU "*" on "*) ;; *) exit 1 ;; esac
else
  echo "render device: CPU"
fi
rm -rf "${OUT:?}/hi" "${OUT:?}/renders" "${OUT:?}/sheets" \
  "${OUT:?}/ports-hi" "${OUT:?}/ports" "${OUT:?}/icon" "${OUT:?}/collide" "${OUT:?}/collide.log"
if [ -n "$COLLIDE" ]; then
  python3 - "$HERE" "$MODEL" "$OUT" "$BLENDER" "${ALLOW[@]}" <<'EOF' || exit $?
import sys
sys.path.insert(0, sys.argv[1])
import measure                                  # its collide step: one rule for both tools
try:
    res = measure.collide(*sys.argv[2:5], allow=sys.argv[5:])
except measure.Usage as e:
    print(f"render.sh: {e}", file=sys.stderr)
    sys.exit(2)
if res["allowed"]:
    print(f"collide: {len(res['allowed'])} pair line(s) allowed by --collide-allow (in {res['log']})")
for pattern in res.get("allow_unused", []):
    print(f"collide: --collide-allow {pattern!r} matched no pair line")
shown = [ln for ln in res["lines"] if ln in res["not_allowed"] or "clash" in ln.lower() or "overlap" in ln]
for line in shown[:40]:
    print(line)
if len(shown) > 40:
    print(f"... and {len(shown) - 40} more in {res['log']}")
print("collide: " + ("PASS" if res["pass"] else f"FAIL: {res['why']}") + f" ({res['log']})")
sys.exit(0 if res["pass"] else 1)
EOF
fi
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
