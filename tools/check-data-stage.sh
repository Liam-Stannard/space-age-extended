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
LOG_FILE="$(mktemp)"
cleanup() { rm -rf "$SCRATCH_MODS" "$LOG_FILE"; }
trap cleanup EXIT

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
"$FACTORIO_BIN" --dump-data --mod-directory "$SCRATCH_MODS" > "$LOG_FILE" 2>&1
STATUS=$?
set -e

if [ $STATUS -ne 0 ] || grep -qE '^ *[0-9.]+ Error' "$LOG_FILE"; then
  echo "Data stage FAILED (exit $STATUS):" >&2
  cat "$LOG_FILE" >&2
  exit 1
fi

echo "Data stage OK -- $MOD_NAME loaded cleanly alongside base/space-age."
