#!/usr/bin/env bash
set -euo pipefail

# Verifies that every graphics and sound path the mod names actually exists.
#
# The data stage does not open these files, so tools/check-data-stage.sh will
# happily pass a mod whose icons all point at nothing -- the failure only shows
# up when a client loads and refuses the mod outright. This catches it locally.
#
# Usage: tools/check-graphics.sh [path-to-factorio-data]

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DATA="${1:-}"
if [ -z "$DATA" ]; then
  for candidate in \
    "$HOME/.steam/debian-installation/steamapps/common/Factorio/data" \
    "$HOME/.steam/steam/steamapps/common/Factorio/data"; do
    [ -d "$candidate" ] && DATA="$candidate" && break
  done
fi
if [ -z "$DATA" ] || [ ! -d "$DATA" ]; then
  echo "Could not find Factorio's data directory. Pass it as the first argument." >&2
  exit 1
fi

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
done < <(grep -rhoE '"__[a-z-]+__/[^"]+\.(png|ogg)"' "$REPO_ROOT/prototypes" "$REPO_ROOT/data.lua" "$REPO_ROOT/data-updates.lua" 2>/dev/null | tr -d '"' | sort -u)

if [ "$missing" -gt 0 ]; then
  echo "Graphics check FAILED: $missing of $checked referenced files do not exist." >&2
  exit 1
fi

echo "Graphics OK -- all $checked referenced files exist."
