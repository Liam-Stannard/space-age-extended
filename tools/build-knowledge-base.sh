#!/usr/bin/env bash
set -euo pipefail

# Builds the local game knowledge base from the installed Factorio:
#
#   <main checkout>/knowledge-base/<game version>/
#     runtime-api.json      the install's doc-html copy, else lua-api.factorio.com/<version>/
#     prototype-api.json    the same
#     data-raw-dump.json    --dump-data of vanilla + Space Age (base, elevated-rails,
#                           quality, recycler, space-age), no other mod
#     data/core, data/base, data/elevated-rails, data/quality, data/recycler, data/space-age
#                           the game's .lua files and info.json, paths kept; no graphics or sound
#     MANIFEST              game version and build, when built, the root it came from, the
#                           mods the dump loaded, and each file's size, sha256 and source
#
# Usage: tools/build-knowledge-base.sh [--force]
#
# The folder is the main checkout's (the one every worktree shares), named by
# the binary's own --version. A folder for that version already there is left
# alone unless --force is given; then the new one is built beside it and only
# replaces it once complete, in one atomic exchange (mv --exchange). A folder
# whose MANIFEST names another version, or has none, is refused even with
# --force, and no other version's folder is ever touched. A run's hidden
# working folders (.<version>.building.XXXXXX) left by one that was killed, and
# the .<version>.old.XXXXXX folders left by the two-rename replace of the first
# version of this script, are removed by the next run of that version, under
# the lock. knowledge-base/ is git-ignored.
#
# Factorio is the one tools/paths.conf names (FACTORIO_ROOT), read through
# tools/paths.sh; if it is not there (the drive unmounted) this exits 1 naming
# the root and builds nothing. The whole run holds the lock
# tools/client/launch.sh takes (one Factorio at a time, and one build at a
# time), waiting for it at most SAE_DATA_STAGE_LOCK_WAIT seconds (default 600,
# as tools/check-data-stage.sh) and exiting 3 if it is still held then.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
USAGE="usage: tools/build-knowledge-base.sh [--force] (Factorio is the one tools/paths.conf names)"

FORCE=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    -h|--help) echo "$USAGE"; exit 0 ;;
    *) echo "$USAGE" >&2; exit 2 ;;
  esac
done

. "$REPO_ROOT/tools/paths.sh"
if ! sae_factorio_root GAME_ROOT || ! sae_factorio_bin GAME_BIN || ! sae_factorio_data GAME_DATA; then
  echo "build-knowledge-base: the Factorio install tools/paths.conf names is not there" \
       "(see above); nothing built." >&2
  exit 1
fi
GAME_MODS=(core base elevated-rails quality recycler space-age)   # data/'s six
for d in "${GAME_MODS[@]}"; do
  if [ ! -d "$GAME_DATA/$d" ]; then
    echo "build-knowledge-base: $GAME_DATA/$d: no such directory; nothing built." >&2
    exit 1
  fi
done

# The main checkout: the folder holding the .git every worktree shares.
GIT_COMMON="$(git -C "$REPO_ROOT" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" || GIT_COMMON=""
if [ -z "$GIT_COMMON" ] || [ "$(basename "$GIT_COMMON")" != ".git" ]; then
  echo "build-knowledge-base: cannot find the main checkout from $REPO_ROOT" \
       "(git common dir '${GIT_COMMON}'); nothing built." >&2
  exit 1
fi
KB_ROOT="$(dirname "$GIT_COMMON")/knowledge-base"

WORK=""
STAGE=""
cleanup() {
  [ -n "$WORK" ] && rm -rf -- "$WORK"
  [ -n "$STAGE" ] && rm -rf -- "$STAGE"
  return 0
}
trap cleanup EXIT
WORK="$(mktemp -d)"

# ------------------------------------------------------------------ the lock
# One Factorio at a time, with the test clients; see tools/check-data-stage.sh.
LOCK_FILE="${XDG_RUNTIME_DIR:-/tmp}/sae-factorio-client.lock"   # launch.sh's LOCK_FILE
LOCK_WAIT="${SAE_DATA_STAGE_LOCK_WAIT:-600}"
if ! [[ "$LOCK_WAIT" =~ ^[0-9]+$ ]] || [ "$LOCK_WAIT" -gt 3600 ]; then
  echo "SAE_DATA_STAGE_LOCK_WAIT must be 0-3600 seconds (got '$LOCK_WAIT')." >&2
  exit 2
fi
exec 9>>"$LOCK_FILE"
if ! flock -n 9; then
  echo "A test client's launcher holds $LOCK_FILE; waiting for it (at most ${LOCK_WAIT} s)." >&2
  if ! flock -w "$LOCK_WAIT" 9; then
    echo "REFUSED -- $LOCK_FILE is still held after ${LOCK_WAIT} s: a test client is running" \
         "(tools/client/launch.sh; one Factorio at a time). Nothing built." >&2
    pgrep -a -x factorio >&2 || true
    exit 3
  fi
  echo "The lock is free; building." >&2
fi

# ---------------------------------------------------------------- the version
VERSION_TEXT="$("$GAME_BIN" --version 2>&1)" || {
  echo "build-knowledge-base: $GAME_BIN --version failed:" >&2
  echo "$VERSION_TEXT" >&2
  exit 1
}
VERSION_LINE="$(printf '%s\n' "$VERSION_TEXT" | grep -m1 '^Version: ' || true)"
VERSION_RE='^Version: ([0-9]+\.[0-9]+\.[0-9]+) \(build ([0-9]+)'
if ! [[ "$VERSION_LINE" =~ $VERSION_RE ]]; then
  echo "build-knowledge-base: cannot read the version from $GAME_BIN --version:" >&2
  echo "$VERSION_TEXT" >&2
  exit 1
fi
VERSION="${BASH_REMATCH[1]}"
BUILD="${BASH_REMATCH[2]}"
DEST="$KB_ROOT/$VERSION"

if [ -e "$DEST" ] || [ -L "$DEST" ]; then
  HAVE=""
  if [ -d "$DEST" ] && [ ! -L "$DEST" ] && [ -f "$DEST/MANIFEST" ]; then
    HAVE="$(sed -n 's/^game-version: //p' "$DEST/MANIFEST" | head -1)"
  fi
  if [ "$HAVE" != "$VERSION" ]; then
    echo "REFUSED -- $DEST is there but is not a $VERSION knowledge base" \
         "(its MANIFEST names '${HAVE:-nothing}'). Not overwriting it, even with --force." >&2
    exit 1
  fi
  if [ "$FORCE" = 0 ]; then
    echo "REFUSED -- $DEST is already built for $VERSION. Rebuild it with --force." >&2
    exit 1
  fi
fi

mkdir -p -- "$KB_ROOT"
# A killed run's working folders for this version (and .old.* ones, which the
# two-rename replace of the first version of this script made). The lock is
# held for the whole of every run, so none of these belongs to a live one.
shopt -s nullglob
for stale in "$KB_ROOT/.$VERSION.building."?????? "$KB_ROOT/.$VERSION.old."??????; do
  if [ -d "$stale" ] && [ ! -L "$stale" ]; then
    echo "Removing $stale, left by a run that did not finish." >&2
    rm -rf -- "$stale"
  fi
done
shopt -u nullglob
STAGE="$(mktemp -d "$KB_ROOT/.$VERSION.building.XXXXXX")"
chmod 755 -- "$STAGE"                # mktemp's 0700 would outlive the rename
echo "Building the $VERSION (build $BUILD) knowledge base in $STAGE" >&2

# ------------------------------------------------------------- the API JSON
SOURCES="$WORK/sources.tsv"          # file <TAB> source, for the MANIFEST
: > "$SOURCES"
for f in runtime-api.json prototype-api.json; do
  if [ -f "$GAME_ROOT/doc-html/$f" ]; then
    cp -- "$GAME_ROOT/doc-html/$f" "$STAGE/$f"
    chmod 644 -- "$STAGE/$f"         # the install's copies are executable
    printf '%s\t%s\n' "$f" "$GAME_ROOT/doc-html/$f" >> "$SOURCES"
  else
    URL="https://lua-api.factorio.com/$VERSION/$f"
    echo "No $GAME_ROOT/doc-html/$f; fetching $URL" >&2
    if ! curl -fsSL --max-time 120 -o "$STAGE/$f" -- "$URL"; then
      echo "build-knowledge-base: could not fetch $URL; nothing built." >&2
      exit 1
    fi
    printf '%s\t%s\n' "$f" "$URL" >> "$SOURCES"
  fi
  # This version's, or nothing: checked before the dump is run.
  python3 -I -c '
import json, sys
path, version, source = sys.argv[1:]
try:
    with open(path, encoding="utf-8") as f:
        got = json.load(f).get("application_version")
except (OSError, ValueError, AttributeError) as e:
    sys.exit(f"build-knowledge-base: {source} is not readable API JSON ({e}); nothing built.")
if got != version:
    sys.exit(f"build-knowledge-base: {source} is for Factorio {got!r}, not the installed {version}; nothing built.")
' "$STAGE/$f" "$VERSION" "$(tail -n 1 "$SOURCES" | cut -f2)"
done

# ------------------------------------------------------------------ the dump
# A scratch write-data directory (so ~/.factorio's lock and dump are not
# touched) and a scratch mod directory holding only a mod-list: Factorio loads
# core and the five mods under data/ and nothing else.
mkdir -p "$WORK/data" "$WORK/mods"
cat > "$WORK/data/config.ini" <<EOF
[path]
read-data=__PATH__executable__/../../data
write-data=$WORK/data
EOF
cat > "$WORK/mods/mod-list.json" <<EOF
{
  "mods": [
    {"name": "base", "enabled": true},
    {"name": "elevated-rails", "enabled": true},
    {"name": "quality", "enabled": true},
    {"name": "recycler", "enabled": true},
    {"name": "space-age", "enabled": true}
  ]
}
EOF
LOG_FILE="$WORK/dump.log"
set +e
"$GAME_BIN" --dump-data --config "$WORK/data/config.ini" \
    --mod-directory "$WORK/mods" > "$LOG_FILE" 2>&1
STATUS=$?
set -e

DUMP="$WORK/data/script-output/data-raw-dump.json"
if [ $STATUS -ne 0 ] || grep -qE '^ *[0-9.]+ Error' "$LOG_FILE" || [ ! -f "$DUMP" ]; then
  echo "build-knowledge-base: --dump-data FAILED (exit $STATUS); nothing built:" >&2
  cat "$LOG_FILE" >&2
  exit 1
fi
mv -- "$DUMP" "$STAGE/data-raw-dump.json"
printf '%s\t%s\n' "data-raw-dump.json" \
  "$GAME_BIN --dump-data (mod-list: base, elevated-rails, quality, recycler, space-age; no other mod)" \
  >> "$SOURCES"

# ---------------------------------------------------- the Lua, the MANIFEST
# The Lua copy, the checks on what was built, and the MANIFEST.
python3 -I - "$STAGE" "$GAME_DATA" "$GAME_ROOT" "$VERSION" "$BUILD" \
    "$VERSION_LINE" "$SOURCES" "$LOG_FILE" "${GAME_MODS[@]}" <<'PY'
import datetime
import hashlib
import json
import os
import re
import shutil
import sys

stage, game_data, game_root, version, build, version_line, sources_tsv, log_file = sys.argv[1:9]
game_mods = sys.argv[9:]


def fail(msg):
    print(f"build-knowledge-base: {msg}; nothing built.", file=sys.stderr)
    sys.exit(1)


sources = {}
with open(sources_tsv, encoding="utf-8") as f:
    for line in f:
        name, src = line.rstrip("\n").split("\t", 1)
        sources[name] = src

# The dump must hold vanilla prototypes.
try:
    with open(os.path.join(stage, "data-raw-dump.json"), encoding="utf-8") as f:
        raw = json.load(f)
except (OSError, ValueError) as e:
    fail(f"the data-raw dump is not readable JSON ({e})")
# (The oil refinery is an assembling-machine; the foundry is Space Age's.)
for kind, name in (("assembling-machine", "oil-refinery"), ("assembling-machine", "foundry")):
    if name not in raw.get(kind, {}):
        fail(f'the data-raw dump has no data.raw["{kind}"]["{name}"]')

# The mods the dump loaded, from its log.
mods = []
with open(log_file, encoding="utf-8", errors="replace") as f:
    for line in f:
        m = re.search(r"Loading mod (\S+) (\S+) \(", line)
        if m and f"{m.group(1)} {m.group(2)}" not in mods:
            mods.append(f"{m.group(1)} {m.group(2)}")
names = sorted({m.split(" ")[0] for m in mods})
expected = sorted(game_mods)
if names != expected:
    fail(f"the dump loaded the mods {names}, not {expected}")

# The prototype Lua: .lua files and info.json, paths kept.
for top in game_mods:
    src_top = os.path.join(game_data, top)
    for dirpath, dirnames, filenames in os.walk(src_top):
        dirnames.sort()
        for fn in sorted(filenames):
            if not (fn.endswith(".lua") or fn == "info.json"):
                continue
            src = os.path.join(dirpath, fn)
            rel = os.path.join("data", os.path.relpath(src, game_data))
            dst = os.path.join(stage, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            sources[rel] = src

# The MANIFEST: every file in the folder but itself.
rows = []
total = 0
for dirpath, dirnames, filenames in os.walk(stage):
    dirnames.sort()
    for fn in sorted(filenames):
        path = os.path.join(dirpath, fn)
        rel = os.path.relpath(path, stage)
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        size = os.path.getsize(path)
        total += size
        rows.append((rel, size, h.hexdigest(), sources[rel]))
rows.sort()

now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
out = [
    "# Factorio game knowledge base, built by tools/build-knowledge-base.sh. Do not edit.",
    "# Verify, in this folder: awk -F'\\t' '!/^#/ && NF==4 {print $3\"  \"$1}' MANIFEST | sha256sum -c --quiet",
    f"game-version: {version}",
    f"game-build: {build}",
    f"game-version-line: {version_line}",
    f"built-utc: {now}",
    f"factorio-root: {game_root}",
    f"dump-mods: {', '.join(mods)}",
    f"files: {len(rows)}",
    f"total-bytes: {total}",
    "",
    "# path<TAB>bytes<TAB>sha256<TAB>source",
]
out += [f"{rel}\t{size}\t{digest}\t{src}" for rel, size, digest, src in rows]
with open(os.path.join(stage, "MANIFEST"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print(f"{len(rows)} files, {total} bytes; dump loaded {', '.join(mods)}", file=sys.stderr)
PY

# ------------------------------------------------------------- into place
# Replacing is one exchange, so there is always a whole folder at $DEST; the
# old one ends up at $STAGE and goes with it. -T: never into a $DEST that is
# there by now (mv then fails, and the trap removes $STAGE).
if [ -d "$DEST" ]; then
  mv --exchange -T -- "$STAGE" "$DEST"
  rm -rf -- "$STAGE"
else
  mv -T -- "$STAGE" "$DEST"
fi
STAGE=""
echo "Knowledge base for Factorio $VERSION (build $BUILD) built: $DEST"
