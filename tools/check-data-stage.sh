#!/usr/bin/env bash
set -euo pipefail

# Smoke-tests that the mod's data stage loads cleanly, without opening a
# game window. Requires a local Factorio (Space Age) install; this does NOT
# run in CI, since Factorio isn't redistributable to a CI runner -- run it
# locally before pushing.
#
# Usage: tools/check-data-stage.sh [path-to-factorio-binary]

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MOD_NAME="$(grep -o '"name" *: *"[^"]*"' "$REPO_ROOT/info.json" | head -1 | sed -E 's/.*"([^"]+)"$/\1/')"

FACTORIO_BIN="${1:-}"
if [ -z "$FACTORIO_BIN" ]; then
  for candidate in \
    "$HOME/.steam/debian-installation/steamapps/common/Factorio/bin/x64/factorio" \
    "$HOME/.steam/steam/steamapps/common/Factorio/bin/x64/factorio" \
    "$(command -v factorio 2>/dev/null || true)"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
      FACTORIO_BIN="$candidate"
      break
    fi
  done
fi
if [ -z "$FACTORIO_BIN" ] || [ ! -x "$FACTORIO_BIN" ]; then
  echo "Could not find a Factorio binary. Pass its path as the first argument." >&2
  exit 1
fi

SCRATCH_MODS="$(mktemp -d)"
SCRATCH_DATA="$(mktemp -d)"
LOG_FILE="$(mktemp)"
cleanup() { rm -rf "$SCRATCH_MODS" "$SCRATCH_DATA" "$LOG_FILE"; }
trap cleanup EXIT

# --dump-data takes ~/.factorio/.lock, so it refuses to run while a client is
# open -- "Couldn't acquire exclusive lock". Pointing Factorio at a scratch
# write-data directory sidesteps the contention entirely, so this check works
# with the game running instead of asking anyone to close it.
cat > "$SCRATCH_DATA/config.ini" <<EOF
[path]
read-data=__PATH__executable__/../../data
write-data=$SCRATCH_DATA
EOF

ln -s "$REPO_ROOT" "$SCRATCH_MODS/$MOD_NAME"
cat > "$SCRATCH_MODS/mod-list.json" <<EOF
{
  "mods": [
    {"name": "base", "enabled": true},
    {"name": "elevated-rails", "enabled": true},
    {"name": "quality", "enabled": true},
    {"name": "recycler", "enabled": true},
    {"name": "space-age", "enabled": true},
    {"name": "$MOD_NAME", "enabled": true}
  ]
}
EOF

set +e
"$FACTORIO_BIN" --dump-data --config "$SCRATCH_DATA/config.ini" \
    --mod-directory "$SCRATCH_MODS" > "$LOG_FILE" 2>&1
STATUS=$?
set -e

if [ $STATUS -ne 0 ] || grep -qE '^ *[0-9.]+ Error' "$LOG_FILE"; then
  echo "Data stage FAILED (exit $STATUS):" >&2
  cat "$LOG_FILE" >&2
  exit 1
fi

echo "Data stage OK -- $MOD_NAME loaded cleanly alongside base/space-age."

# The data stage never opens image files, so a mod with broken icon paths passes
# here and is then refused outright by a client. Check them too.
"$REPO_ROOT/tools/check-graphics.sh" || exit 1

# And that concepts, specs, templates and tasks are where claude.md says they are.
"$REPO_ROOT/tools/check-layout.sh" || exit 1
DATA_DIR="$(dirname "$(dirname "$FACTORIO_BIN")")/../data"
DATA_DIR="$(cd "$DATA_DIR" && pwd)"

# And a recipe can name more fluids than any machine in its category has boxes
# for. The data stage accepts that, set_recipe accepts it, and the machine then
# sits there doing nothing. The dump the run above produced has the answer.
#
# The dump comes from the scratch write-data directory this run just used, not
# from ~/.factorio -- pointing at the latter went stale the moment this script
# stopped writing there, and a stale dump answers questions about a version of
# the mod that no longer exists.
DUMP="$SCRATCH_DATA/script-output/data-raw-dump.json"
if [ -f "$DUMP" ]; then
  # Paths as the engine resolved them, which is the only way to see the ones Lua
  # builds by concatenation -- check-graphics.sh cannot, and most of this mod's
  # sprite paths are built that way. See tools/check-dumped-graphics.py.
  python3 "$REPO_ROOT/tools/check-dumped-graphics.py" "$DUMP" "$DATA_DIR" || exit 1
  "$REPO_ROOT/tools/check-recipes.py" "$DUMP" || exit 1
  # And whether the game can be played, which is a different question from
  # whether it loads. Everything above proves prototypes are well-formed and
  # their assets exist; none of it notices a technology that unlocks a recipe
  # whose ingredients no reachable machine can make. See the tool's own header
  # for the one that got through.
  "$REPO_ROOT/tools/check-tech-reachability.py" "$DUMP" || exit 1
else
  echo "Checks skipped -- no data-raw dump at $DUMP" >&2
  exit 1
fi
