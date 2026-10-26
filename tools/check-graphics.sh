#!/usr/bin/env bash
set -euo pipefail

# Verifies that every graphics and sound path the mod names actually exists.
#
# The data stage does not open these files, so tools/check-data-stage.sh will
# happily pass a mod whose icons all point at nothing -- the failure only shows
# up when a client loads and refuses the mod outright. This catches it locally.
#
# Usage: tools/check-graphics.sh
#
# The game data is <FACTORIO_ROOT>/data, FACTORIO_ROOT being the one
# tools/paths.conf names (read through tools/paths.sh).

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ $# -gt 0 ]; then
  echo "usage: tools/check-graphics.sh (no arguments: the game data is the one tools/paths.conf names)" >&2
  exit 2
fi
. "$REPO_ROOT/tools/paths.sh"
sae_factorio_data DATA || exit 1

missing=0
checked=0

while read -r ref; do
  [ -z "$ref" ] && continue
  checked=$((checked + 1))
  case "$ref" in
    __base__/*)              real="$DATA/base/${ref#__base__/}" ;;
    __core__/*)              real="$DATA/core/${ref#__core__/}" ;;
    __space-age__/*)         real="$DATA/space-age/${ref#__space-age__/}" ;;
    __quality__/*)           real="$DATA/quality/${ref#__quality__/}" ;;
    __elevated-rails__/*)    real="$DATA/elevated-rails/${ref#__elevated-rails__/}" ;;
    __space-age-extended__/*) real="$REPO_ROOT/${ref#__space-age-extended__/}" ;;
    *) echo "  ?  unrecognised mod prefix: $ref"; continue ;;
  esac
  if [ ! -f "$real" ]; then
    echo "  MISSING  $ref"
    missing=$((missing + 1))
  fi
done < <(python3 "$REPO_ROOT/tools/collect-graphics-refs.py" \
           "$REPO_ROOT/prototypes" "$REPO_ROOT/data.lua" "$REPO_ROOT/data-updates.lua")

if [ "$missing" -gt 0 ]; then
  echo "Graphics check FAILED: $missing of $checked referenced files do not exist." >&2
  exit 1
fi

echo "Graphics OK -- all $checked referenced files exist."
