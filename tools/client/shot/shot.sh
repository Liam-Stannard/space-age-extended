#!/usr/bin/env bash
# tools/client/shot/shot.sh -- screenshot one building in every requested
# direction and state, by day and night, at each zoom, in a real client.
#
# Usage:
#   tools/client/shot/shot.sh --task NAME --spec FILE [--worktree DIR] [--timeout S]
#
#   --task NAME     Evidence goes to <repo>/evidence/NAME/ (the launcher's run
#                   directories; the shots are in the second one's
#                   data/script-output/sae-shot/, the contact sheet(s) and
#                   motion.json in that run directory itself).
#   --spec FILE     What to shoot, as JSON (example: specs/crust-turbine.json):
#                     entity        the entity prototype's name (required)
#                     planet        the planet whose own surface it is built on,
#                                   so surface conditions hold (default nauvis)
#                     tile          optional: lay this tile on the cleared patch
#                     directions    any of north, east, south, west
#                     daytimes      [{name, daytime}], 0 noon, 0.5 midnight
#                     zooms         [{name, zoom}], 1 is the game's 32 px a tile
#                     margin        tiles of ground round the footprint (3)
#                     shift         [x, y] tiles to move the frame (0, 0)
#                     settle_ticks  ticks between building and shooting (120)
#                     clear_radius  tiles cleared of entities and decoratives (20)
#                     motion        optional {frames, every, daytime, zoom}: the
#                                   same view `frames` times `every` ticks apart,
#                                   after the stills: <state>/motion-<dir>-<n>.png
#                     states        [{name, fluids: [{name, amount}], refill,
#                                    items: [{name, count}], recipe,
#                                    power: "none" | "load" | "supply",
#                                    load_kw, supply_kw}]
#                   power "load" puts a hidden energy interface drawing load_kw
#                   on a hidden pole (a generator's work); "supply" one
#                   supplying supply_kw (a consumer's power); "none" no pole at
#                   all. refill tops the fluids up every tick while it settles.
#   --worktree DIR  The mod to load (default: this repo), as the launcher's.
#   --mod PATH      An extra mod for both runs, as the launcher's (e.g.
#                   ~/.factorio/mods/alien-biomes_0.8.0.zip). Repeatable.
#   --timeout S     The shooting run's limit (default 900).
#
# Runs only through tools/client/launch.sh, twice: once to --create a save with
# the probe mod (tools/client/shot/mod, copied to a scratch folder with the
# spec beside it as config.lua), once to load it and shoot. The probe writes,
# under script-output/sae-shot/: <state>/<direction>-<daytime>-<zoom>.png,
# <state>/state.json (each copy's direction as built, status, output, fluids),
# log.txt, errors.txt (only if it caught an error), and `done`; the launcher
# stops on `done`. Then contact.py makes the contact sheet(s), none over 8000 px
# on a side.
#
# Exit: 0 every expected still and motion frame was written and the probe caught
# no error; 1 something failed (an error in errors.txt, a frame missing, the
# launcher's run, or the contact sheet: see the output);
# 2 usage; the launcher's own refusal (3) is passed on.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
LAUNCH="$REPO_ROOT/tools/client/launch.sh"

die() { echo "shot.sh: $*" >&2; exit 2; }
need() { [ "$2" -ge 2 ] || die "$1 needs a value"; }

TASK="" SPEC="" WORKTREE="$REPO_ROOT" TIMEOUT=900
EXTRA=()
while [ $# -gt 0 ]; do
  case "$1" in
    --task) need "$1" $#; TASK="$2"; shift 2 ;;
    --spec) need "$1" $#; SPEC="$2"; shift 2 ;;
    --worktree) need "$1" $#; WORKTREE="$2"; shift 2 ;;
    --timeout) need "$1" $#; TIMEOUT="$2"; shift 2 ;;
    --mod) need "$1" $#; EXTRA+=(--mod "$2"); shift 2 ;;
    -h|--help) sed -n '2,/^$/{s/^# \{0,1\}//;p}' "${BASH_SOURCE[0]}" >&2; exit 0 ;;
    *) die "unknown option '$1'" ;;
  esac
done
[ -n "$TASK" ] || die "--task NAME is required"
[ -f "$SPEC" ] || die "--spec FILE is required (and must exist)"
# Tick counts must be whole-number literals ("frames": 4.0 is refused): jq 1.7
# keeps a literal's text, so 4.0 would print as 4.0 and break the shell's count.
jq -e '
  def whole: type == "number" and (tostring | test("^[0-9]+$"));
  (.entity | type == "string")
  and (.directions | length > 0) and (.daytimes | length > 0) and (.zooms | length > 0)
  and (.states | length > 0)
  and ([.states[].name, .directions[], .daytimes[].name, .zooms[].name]
       | all(type == "string" and test("^[A-Za-z0-9._-]+$")))
  and (.directions | all(. == "north" or . == "east" or . == "south" or . == "west"))
  and ((.settle_ticks // 120) | whole)
  and (.motion == null
       or (((.motion.frames // 2) | whole and . >= 1) and ((.motion.every // 6) | whole and . >= 1)))
' "$SPEC" > /dev/null || die "$SPEC is not a usable spec (see --help)"
JSON="$(jq -c . "$SPEC")"
case "$JSON" in *']==]'*) die "the spec may not contain ]==]" ;; esac

SCR="$(mktemp -d -t sae-shot.XXXXXX)" || die "mktemp"
cleanup() { [ -n "$SCR" ] && [ -d "$SCR" ] && rm -r -- "$SCR"; }
trap cleanup EXIT

cp -r -- "$HERE/mod" "$SCR/sae-shot" || exit 1
printf 'return [==[%s]==]\n' "$JSON" > "$SCR/sae-shot/config.lua" || exit 1

run_dir_of() { sed -n 's/.* run dir: //p' "$1" | head -n 1; }

echo "== creating the save"
"$LAUNCH" --task "$TASK" --worktree "$WORKTREE" --mod "$SCR/sae-shot" "${EXTRA[@]}" --timeout 300 \
  -- --create "$SCR/shot.zip" 2> "$SCR/create.err"
rc=$?
cat "$SCR/create.err" >&2
[ "$rc" = 0 ] && [ -f "$SCR/shot.zip" ] || { echo "shot.sh: creating the save failed (launcher exit $rc)" >&2; exit $(( rc == 3 ? 3 : 1 )); }

echo "== shooting"
"$LAUNCH" --task "$TASK" --worktree "$WORKTREE" --mod "$SCR/sae-shot" "${EXTRA[@]}" --timeout "$TIMEOUT" \
  --done-file sae-shot/done -- --load-game "$SCR/shot.zip" 2> "$SCR/shoot.err"
rc=$?
cat "$SCR/shoot.err" >&2
RUN="$(run_dir_of "$SCR/shoot.err")"
[ -n "$RUN" ] || { echo "shot.sh: the shooting run did not start (launcher exit $rc)" >&2; exit $(( rc == 3 ? 3 : 1 )); }
OUT="$RUN/data/script-output/sae-shot"
[ "$rc" = 0 ] || echo "shot.sh: the shooting run ended with launcher exit $rc" >&2

echo "== the probe's log"
cat "$OUT/log.txt" 2>/dev/null || echo "(no log.txt)"

# Every error the probe caught (pcall) is in errors.txt, and a failed setup
# also writes it into `done`: either fails the run, whatever files exist.
errors=0
if [ -s "$OUT/errors.txt" ]; then
  errors=1
  echo "shot.sh: the probe caught errors:" >&2
  sed 's/^/  /' "$OUT/errors.txt" >&2
fi
if [ -f "$OUT/done" ] && [ "$(cat "$OUT/done")" != "done" ]; then
  errors=1
  echo "shot.sh: the probe ended with: $(cat "$OUT/done")" >&2
fi

want=0 have=0
while read -r st; do
  for d in $(jq -r '.directions[]' "$SPEC"); do
    for t in $(jq -r '.daytimes[].name' "$SPEC"); do
      for z in $(jq -r '.zooms[].name' "$SPEC"); do
        want=$((want + 1))
        f="$OUT/$st/$d-$t-$z.png"
        if [ -s "$f" ]; then have=$((have + 1)); else echo "missing: $f" >&2; fi
      done
    done
  done
done < <(jq -r '.states[].name' "$SPEC")
echo "shots: $have of $want in $OUT"

# The motion frames count as the stills do: one missing fails the run.
frames="$(jq -r 'if .motion then (.motion.frames // 2) else 0 end' "$SPEC")"
mwant=0 mhave=0
if [ "$frames" -gt 0 ]; then
  while read -r st; do
    for d in $(jq -r '.directions[]' "$SPEC"); do
      for ((j = 0; j < frames; j++)); do
        mwant=$((mwant + 1))
        f="$OUT/$st/motion-$d-$j.png"
        if [ -s "$f" ]; then mhave=$((mhave + 1)); else echo "missing: $f" >&2; fi
      done
    done
  done < <(jq -r '.states[].name' "$SPEC")
  echo "motion frames: $mhave of $mwant in $OUT"
fi

python3 "$HERE/contact.py" "$OUT" "$SPEC" "$RUN" || { echo "shot.sh: contact sheet failed" >&2; exit 1; }
[ "$rc" = 0 ] && [ "$errors" = 0 ] && [ "$have" = "$want" ] && [ "$mhave" = "$mwant" ]
