#!/usr/bin/env bash
# tools/client/launch.sh -- the only way an agent starts a Factorio client.
#
# It runs the graphical client headless on a private Xvfb display, against a
# given worktree, with nothing reaching Liam's desktop or speakers, and stops
# everything it started when it ends, however it ends.
#
# Usage:
#   tools/client/launch.sh --task NAME [options] [-- factorio-args...]
#   tools/client/launch.sh --recover RUN_DIR
#
# The client is <FACTORIO_ROOT>/bin/x64/factorio, FACTORIO_ROOT being the one
# tools/paths.conf names in the repo this script is in (tools/paths.sh); exit 1,
# naming the file and the key, when that cannot be read or does not exist.
#
# Options:
#   --task NAME        Required. Evidence goes to <repo>/evidence/NAME/client-<stamp>-<pid>/
#                      (git-ignored), <repo> being the repo this script is in.
#   --worktree DIR     The mod to load (a checkout with info.json). Default: <repo>.
#                      It is symlinked into a scratch mod directory; ~/.factorio
#                      and ~/.factorio/mods are never read or written.
#   --mod PATH         An extra mod (a folder with info.json, or name_version.zip),
#                      symlinked in and enabled. Repeatable. base, elevated-rails,
#                      quality, recycler and space-age are always enabled.
#   --audio            Sound on, into a null sink: a null sink is loaded and made
#                      the default sink (and checked) before the client starts;
#                      the client's streams and the default are watched every
#                      0.5 s and the client is killed at once if either leaves
#                      it; afterwards the original default is restored and the
#                      module unloaded. Record from <sink>.monitor (run.json
#                      audio.monitor). Without --audio the client gets
#                      --disable-audio. While the run lasts, every other app's
#                      sound also goes to the null sink.
#   --timeout SECONDS  Hard limit on the run, 1-3600 (default 600).
#   --done-file NAME   Stop when <write-data>/script-output/NAME exists.
#   --until-log REGEX  Stop when the client's log matches REGEX (grep -E), e.g.
#                      'Factorio initialised' for a sprite-load check.
#   --screen WxHxD     Xvfb screen (default 1920x1080x24).
#   --recover RUN_DIR  After a launcher was killed outright (SIGKILL): stop what
#                      that run started and put the sound back. Only the run's
#                      own processes are touched: its recorded session (leader
#                      start time checked), its gate.pid, setsid/sh/env/
#                      xvfb-run/factorio processes carrying its config path, and its
#                      Xvfb (PID and start time, or exact command line). The
#                      sound is touched only once none of them is left, no
#                      factorio runs and the lock is free. Refuses while that
#                      launcher still runs. Every run logs its own recover line.
#
# Factorio arguments after `--` are an allow-list (anything else is refused):
#   --load-game FILE, --create FILE, --load-scenario [MOD/]NAME,
#   --map-gen-settings FILE, --map-settings FILE, --map-gen-seed SEED,
#   --preset NAME, --exchange-string STRING, --until-tick TICK,
#   --verbose, --disable-migration-window.
# Each value is its own argument and may not start with '-'. --config,
# --mod-directory and --disable-audio are the launcher's.
#
# The client runs as
#   setsid env -u WAYLAND_DISPLAY -u WAYLAND_SOCKET SDL_VIDEO_DRIVER=x11
#     SDL_VIDEODRIVER=x11 SteamAppId=427520 SteamGameId=427520
#     xvfb-run -a -s "-screen 0 WxHxD" factorio --config <run>/config.ini
#     --mod-directory <scratch> [--disable-audio] [factorio-args]
# behind a gate: the shell that starts the new session writes its PID to
# gate.pid and stops itself before anything runs; the launcher records the
# session in run.json, then lets it go. A signal at any point after the gate
# exists kills it (and everything in its session) before the sound is touched. Once the real binary is up
# the launcher reads /proc/<pid>/environ and cmdline and kills it at once if
# WAYLAND_DISPLAY is set or (without --audio) --disable-audio is missing.
#
# Refuses (exit 3) while any factorio process runs or another launcher holds
# the lock: on this machine a second client's Steam connect can reach the first.
#
# The run directory holds launch.log (this script), factorio.log (the client's
# output), pids.txt (every PID it started, as seen), run.json (the record),
# gate.pid and data/ (the client's write-data; script-output/ is in there).
#
# Exit: 0 stopped as asked (done-file, until-log, or the timeout when no stop
# condition was given) or the client exited 0; 1 client exited non-zero or the
# setup failed; 2 usage; 3 refused; 4 audio setup failed; 5 cleanup left
# something behind; 6 a safety guard killed the client; 124 timed out waiting
# for a stop condition; 130 SIGINT; 143 SIGTERM; 129 SIGHUP. A second signal
# during cleanup skips the waiting and kills at once; the sound is still put
# back.
#
# Test only: SAE_LAUNCH_TEST_HOLD=before-session makes the launcher pause for
# 60 s after the gated session exists but before run.json names it, so that
# --recover can be shown to find it from gate.pid and the config path;
# SAE_LAUNCH_TEST_HOLD=after-release pauses 60 s after the gate is released but
# before the client is looked for, to show a stop in that window. Never set it
# outside such a test. Neither it nor the launcher's own SAE_LAUNCH_* variables
# reach the client.

set -uo pipefail
# Started with `&` from a script, bash enters with SIGINT ignored, and an
# ignored-at-entry signal can be neither trapped nor reset: Ctrl-C/SIGINT would
# then do nothing. Start again once with SIGINT at its default so it is ours.
if [ -z "${SAE_LAUNCH_SIGINT_RESET:-}" ] \
   && (( 0x$(awk '/^SigIgn/ { print $2 }' "/proc/$$/status") & 0x2 )); then
  SAE_LAUNCH_SIGINT_RESET=1 exec env --default-signal=INT bash "${BASH_SOURCE[0]}" "$@"
fi
# A closed stderr must not kill the launcher half-way through its cleanup.
trap '' PIPE

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
NULL_PREFIX="sae_client_null_"
LOCK_FILE="${XDG_RUNTIME_DIR:-/tmp}/sae-factorio-client.lock"
CONF_KEY="default.configured.audio.sink"

usage() { sed -n '2,/^$/{s/^# \{0,1\}//;p}' "${BASH_SOURCE[0]}" >&2 2>/dev/null; exit "${1:-2}"; }
die() { echo "launch.sh: $*" >&2 2>/dev/null; exit 2; }

LOG=""
log() {  # to the run's log first, then (if anyone is listening) to stderr
  local line
  line="$(date +%H:%M:%S.%N | cut -c1-12) $*"
  [ -n "$LOG" ] && printf '%s\n' "$line" >> "$LOG"
  printf '%s\n' "$line" >&2 2>/dev/null || :
}

TASK="" WORKTREE="$REPO_ROOT" AUDIO=0 TIMEOUT=600 DONE_FILE="" UNTIL_LOG=""
SCREEN="1920x1080x24" RECOVER=""
EXTRA_MODS=() PASS=()
need() { [ "$2" -ge 2 ] || die "$1 needs a value"; }
while [ $# -gt 0 ]; do
  case "$1" in
    --task) need "$1" $#; TASK="$2"; shift 2 ;;
    --worktree) need "$1" $#; WORKTREE="$2"; shift 2 ;;
    --mod) need "$1" $#; EXTRA_MODS+=("$2"); shift 2 ;;
    --audio) AUDIO=1; shift ;;
    --timeout) need "$1" $#; TIMEOUT="$2"; shift 2 ;;
    --done-file) need "$1" $#; DONE_FILE="$2"; shift 2 ;;
    --until-log) need "$1" $#; UNTIL_LOG="$2"; shift 2 ;;
    --screen) need "$1" $#; SCREEN="$2"; shift 2 ;;
    --recover) need "$1" $#; RECOVER="$2"; shift 2 ;;
    -h|--help) usage 0 ;;
    --) shift; PASS=("$@"); break ;;
    *) die "unknown option '$1' (factorio's own arguments go after --)" ;;
  esac
done

# ---------------------------------------------------------------- helpers

session_pids() {  # every process in session $1: "pid comm"
  ps -e -o pid=,sid=,comm= | awk -v s="$1" '$2 == s { print $1, $3 }'
}

alive_in_session() {  # pid $1 is alive and still in session $2 (not a reused PID)
  local sid
  sid="$(ps -o sid= -p "$1" 2>/dev/null | tr -d ' ')"
  [ -n "$sid" ] && [ "$sid" = "$2" ]
}

proc_start() {  # start time of pid $1 in clock ticks since boot (field 22 of stat)
  sed 's/^.*) //' "/proc/$1/stat" 2>/dev/null | awk '{ print $20 }'
}

pids_with_arg() {  # every process whose command line contains the string $1
  local d p
  for d in /proc/[0-9]*; do
    p="${d#/proc/}"
    [ "$p" = "$$" ] && continue
    { tr '\0' '\n' < "$d/cmdline"; } 2>/dev/null | grep -qxF -- "$1" && echo "$p"
  done
}

remove_stale_x_lock() {  # xvfb_pid display -- only a lock that dead Xvfb wrote
  local n="${2#:}"
  [ -n "$1" ] && [[ "$n" =~ ^[0-9]+$ ]] || return 0
  [ -d "/proc/$1" ] && return 0
  if [ -f "/tmp/.X$n-lock" ] && [ "$(tr -d ' \n' < "/tmp/.X$n-lock" 2>/dev/null)" = "$1" ]; then
    rm -f -- "/tmp/.X$n-lock" "/tmp/.X11-unix/X$n" && log "removed stale /tmp/.X$n-lock of Xvfb $1"
  fi
}

is_real_factorio() {  # pid $1 runs the Factorio binary itself, not a shell wrapper
  local exe
  exe="$(readlink "/proc/$1/exe" 2>/dev/null)" || return 1
  [ "$(basename "$exe")" = factorio ]
}

default_sink() { pactl get-default-sink 2>/dev/null; }
configured_sink() {  # no reader in here quits early, so nothing writes into a closed pipe
  local v
  v="$(pw-metadata 0 "$CONF_KEY" 2>/dev/null | sed -n "s/.*value:'\([^']*\)'.*/\1/p")"
  printf '%s\n' "${v%%$'\n'*}"
}
sink_index() { pactl -f json list sinks 2>/dev/null | jq -r --arg n "$1" '.[] | select(.name == $n) | .index'; }
sink_exists() { pactl list short sinks 2>/dev/null | awk -v n="$1" '$2 == n { f = 1 } END { exit !f }'; }
same_json() { [ "$(jq -cS . <<< "${1:-null}" 2>/dev/null)" = "$(jq -cS . <<< "${2:-null}" 2>/dev/null)" ]; }
null_modules() {  # every loaded module-null-sink that made sink $1
  pactl list short modules 2>/dev/null \
    | awk -v a="sink_name=$1" '$2 == "module-null-sink" { for (i = 3; i <= NF; i++) if ($i == a) print $1 }'
}
client_streams() {  # PID -> "sink-input sink" for every stream the client owns
  # Factorio's PipeWire stream carries no PID itself; its client does. Any
  # stream that says it is Factorio counts too (only one client ever runs).
  jq -rn --arg p "$1" \
    --argjson c "$(pactl -f json list clients 2>/dev/null || echo '[]')" \
    --argjson s "$(pactl -f json list sink-inputs 2>/dev/null || echo '[]')" '
    ($c | map(select(.properties["application.process.id"] == $p
                     or .properties["pipewire.sec.pid"] == $p) | .index | tostring)) as $ids
    | $s[]
    | select((.client | tostring) as $cl | any($ids[]; . == $cl)
             or .properties["application.process.id"] == $p
             or .properties["application.id"] == "com.factorio.Factorio")
    | "\(.index) \(.sink)"'
}

# restore_sound NULL_SINK ORIG_DEFAULT ORIG_CONFIGURED
# The one way both the launcher and --recover put the sound back. Only what is
# still the run's own is changed: the default goes back only if it is still the
# null sink, the configured value only if it still names the null sink (and is
# then written back exactly as it was, or removed if there was none). Then every
# module that made the null sink is unloaded, and all of it is verified.
# Sets SOUND_RESULT; returns non-zero if anything is left of the run's sound.
restore_sound() {
  local sink="$1" orig="$2" orig_conf="$3" conf_was_ours=0 cur m rc=0
  SOUND_RESULT=""
  same_json "$(configured_sink)" "{\"name\":\"$sink\"}" && conf_was_ours=1
  cur="$(default_sink)"
  if [ "$cur" = "$sink" ]; then
    if [ -n "$orig" ]; then
      pactl set-default-sink "$orig" || log "AUDIO: could not set the default sink back to $orig"
    fi
  elif [ "$cur" != "$orig" ]; then
    log "AUDIO: the default sink is now '$cur', not the run's; left as it is"
    SOUND_RESULT="default left at '$cur'; "
  fi
  if [ "$conf_was_ours" = 1 ]; then
    if [ -n "$orig_conf" ]; then
      pw-metadata 0 "$CONF_KEY" "$orig_conf" Spa:String:JSON > /dev/null
    else
      pw-metadata -d 0 "$CONF_KEY" > /dev/null
    fi
  fi
  for m in $(null_modules "$sink"); do
    pactl unload-module "$m" && log "AUDIO: unloaded module $m ($sink)"
  done
  if [ -n "$(null_modules "$sink")" ] || sink_exists "$sink"; then
    log "AUDIO: FAIL -- $sink is still loaded"; rc=1
  fi
  if [ "$(default_sink)" = "$sink" ] || same_json "$(configured_sink)" "{\"name\":\"$sink\"}"; then
    log "AUDIO: FAIL -- the default still names $sink"; rc=1
  fi
  if [ -z "$SOUND_RESULT" ]; then
    if [ "$(default_sink)" != "$orig" ] || ! same_json "$(configured_sink)" "$orig_conf"; then
      log "AUDIO: FAIL -- default sink before ($orig / ${orig_conf:-unset}) and after ($(default_sink) / $(configured_sink)) differ"
      rc=1
    fi
  fi
  if [ "$rc" = 0 ]; then
    [ -z "$SOUND_RESULT" ] && SOUND_RESULT="default restored; "
    SOUND_RESULT+="$sink unloaded (verified)"
  fi
  [ "$rc" = 0 ] || SOUND_RESULT+="FAILED"
  log "AUDIO: default sink after: $(default_sink) (configured $(configured_sink)) -- $SOUND_RESULT"
  return "$rc"
}

# ---------------------------------------------------------------- --recover

if [ -n "$RECOVER" ]; then
  RECOVER="$(cd "$RECOVER" 2>/dev/null && pwd)" || die "no such run directory"
  J="$RECOVER/run.json"
  [ -f "$J" ] || die "no run.json in $RECOVER"
  LOG="$RECOVER/launch.log"
  log "recover: started for $RECOVER"
  rc=0
  # The launcher itself must be gone: recovering under a live launcher races its cleanup.
  LPID="$(jq -r '.launcher.pid // empty' "$J")" LSTART="$(jq -r '.launcher.start // empty' "$J")"
  if [ -n "$LPID" ] && [ -n "$LSTART" ] && [ "$(proc_start "$LPID")" = "$LSTART" ]; then
    log "recover: REFUSED -- the launcher $LPID is still running; send it SIGINT instead"
    exit 3
  fi
  # Where the run lives, as the launcher wrote it (not as typed here).
  RUN_DIR="$(jq -r '.run_dir // empty' "$J")"
  [ -n "$RUN_DIR" ] && [ -d "$RUN_DIR" ] || die "run.json has no usable run_dir"
  [ "$(cd "$RUN_DIR" && pwd -P)" = "$(cd "$RECOVER" && pwd -P)" ] \
    || log "recover: note -- run.json's run_dir is $RUN_DIR; using that"
  CONFIG="$RUN_DIR/config.ini"
  # What belongs to the run, each checked before anything is killed:
  #  - the recorded session, if its leader still has the recorded start time;
  #  - the gate named in gate.pid, if it is its own session and carries the
  #    run's config path (covers a session run.json never named);
  #  - the run's own kinds of process (setsid, sh gate, env, xvfb-run, factorio) whose
  #    arguments include the run's config path, and the session such a
  #    process leads;
  #  - the run's Xvfb, by run.json's PID and start time, or by pids.txt's
  #    exact command line (it carries the run's unique xvfb-run auth path).
  declare -A MINE=()
  add_session() { local p; while read -r p _; do [ -n "$p" ] && MINE[$p]=1; done < <(session_pids "$1"); }
  launch_kind() { case "$(ps -o comm= -p "$1" 2>/dev/null)" in setsid|sh|env|xvfb-run|factorio) return 0 ;; esac; return 1; }
  SID="$(jq -r '.session // empty' "$J")" SSTART="$(jq -r '.session_start // empty' "$J")"
  if [ -n "$SID" ]; then
    if [ -n "$SSTART" ] && [ "$(proc_start "$SID")" = "$SSTART" ]; then
      add_session "$SID"
    elif [ -d "/proc/$SID" ]; then
      log "recover: PID $SID is not the recorded session leader any more (start time differs); not touching it"
    fi
  fi
  G="$(cat "$RUN_DIR/gate.pid" 2>/dev/null)"
  if [[ "$G" =~ ^[0-9]+$ ]] && [ "$(ps -o sid= -p "$G" 2>/dev/null | tr -d ' ')" = "$G" ] && launch_kind "$G" \
     && { tr '\0' '\n' < "/proc/$G/cmdline"; } 2>/dev/null | grep -qxF -- "$CONFIG"; then
    add_session "$G"
  fi
  for pid in $(pids_with_arg "$CONFIG"); do
    launch_kind "$pid" || { log "recover: $pid ($(ps -o comm= -p "$pid" 2>/dev/null)) names the config but is not one of the run's processes; not touching it"; continue; }
    MINE[$pid]=1
    [ "$(ps -o sid= -p "$pid" 2>/dev/null | tr -d ' ')" = "$pid" ] && add_session "$pid"
  done
  XR="$(jq -r '.xvfb_pid // empty' "$J")" XS="$(jq -r '.xvfb_start // empty' "$J")"
  if [ -n "$XR" ] && [ -n "$XS" ] && [ "$(proc_start "$XR")" = "$XS" ] \
     && [ "$(ps -o comm= -p "$XR" 2>/dev/null)" = Xvfb ]; then
    MINE[$XR]=1
  fi
  while read -r pid comm rest; do
    [ "$comm" = Xvfb ] && [ -d "/proc/$pid" ] || continue
    [ "$({ tr '\0' ' ' < "/proc/$pid/cmdline"; } 2>/dev/null | cut -c1-300 | sed 's/ *$//')" = "$rest" ] && MINE[$pid]=1
  done < <(cat "$RUN_DIR/pids.txt" 2>/dev/null)
  if [ "${#MINE[@]}" -gt 0 ]; then
    log "recover: the run's processes: $(for p in "${!MINE[@]}"; do printf '%s(%s) ' "$p" "$(ps -o comm= -p "$p")"; done)"
    XVFB_TMP="" XP="" XD=""
    for p in "${!MINE[@]}"; do
      if [ "$(ps -o comm= -p "$p" 2>/dev/null)" = Xvfb ]; then
        XP="$p"
        XD="$({ tr '\0' '\n' < "/proc/$p/cmdline"; } 2>/dev/null | sed -n '2p')"
        XVFB_TMP="$({ tr '\0' '\n' < "/proc/$p/cmdline"; } 2>/dev/null \
          | sed -n 's#^\(.*/xvfb-run\.[^/]*\)/Xauthority$#\1#p')"
      fi
    done
    # The client first (xvfb-run then stops its Xvfb and tidies up), then the rest.
    for p in "${!MINE[@]}"; do
      is_real_factorio "$p" && { log "recover: SIGTERM factorio $p"; kill -TERM "$p" 2>/dev/null; }
    done
    for _ in $(seq 30); do
      left=0; for p in "${!MINE[@]}"; do is_real_factorio "$p" && left=1; done
      [ "$left" = 0 ] && break; sleep 0.1
    done
    for sig in TERM KILL; do
      for p in "${!MINE[@]}"; do
        [ -d "/proc/$p" ] || continue
        log "recover: SIG$sig $p ($(ps -o comm= -p "$p" 2>/dev/null))"
        kill -"$sig" "$p" 2>/dev/null; kill -CONT "$p" 2>/dev/null
      done
      for _ in $(seq 20); do
        left=0; for p in "${!MINE[@]}"; do [ -d "/proc/$p" ] && left=1; done
        [ "$left" = 0 ] && break; sleep 0.1
      done
    done
    for p in "${!MINE[@]}"; do
      [ -d "/proc/$p" ] && { log "recover: FAIL -- $p is still running"; rc=5; }
    done
    case "$XVFB_TMP" in
      /tmp/xvfb-run.*) [ -d "$XVFB_TMP" ] && rm -r -- "$XVFB_TMP" && log "recover: removed $XVFB_TMP" ;;
    esac
    remove_stale_x_lock "$XP" "$XD"
  else
    log "recover: no process of this run is running"
  fi
  MODS_DIR="$(jq -r '.mods_dir // empty' "$J")"
  case "$MODS_DIR" in
    */sae-client-mods.*) [ -d "$MODS_DIR" ] && rm -r -- "$MODS_DIR" && log "recover: removed $MODS_DIR" ;;
  esac
  rm -rf -- "${RUN_DIR:?}/data/temp" "${RUN_DIR:?}/data/crop-cache.dat"
  SINK="$(jq -r '.audio.null_sink // empty' "$J")"
  if [ -n "$SINK" ]; then
    # Only with no client anywhere and the lock free: unloading the null sink
    # under a live client would move its sound to the speakers.
    exec 9>>"$LOCK_FILE"
    locked=0
    for _ in $(seq 20); do flock -n 9 && { locked=1; break; }; sleep 0.1; done
    if [ "$rc" != 0 ] || [ "$locked" = 0 ] || pgrep -x factorio > /dev/null; then
      log "recover: REFUSED to touch the sound -- a factorio runs or the lock is held:"
      pgrep -a -x factorio >&2 2>/dev/null
      exit 5
    fi
    restore_sound "$SINK" "$(jq -r '.audio.default_before // empty' "$J")" \
      "$(jq -r '.audio.configured_before // empty' "$J")" || rc=5
  fi
  [ "$rc" = 0 ] && log "recover: done; nothing of that run is left"
  exit $rc
fi

# ---------------------------------------------------------------- arguments

[ -n "$TASK" ] || die "--task NAME is required"
[[ "$TASK" =~ ^[A-Za-z0-9._-]+$ ]] || die "--task must be letters, digits, . _ -"
[[ "$TIMEOUT" =~ ^[0-9]+$ ]] && [ "$TIMEOUT" -ge 1 ] && [ "$TIMEOUT" -le 3600 ] \
  || die "--timeout must be 1-3600 seconds"
[[ "$SCREEN" =~ ^[0-9]+x[0-9]+x[0-9]+$ ]] || die "--screen must be WxHxD"
[ -f "$WORKTREE/info.json" ] || die "no info.json in --worktree $WORKTREE"
WORKTREE="$(cd "$WORKTREE" && pwd)"
i=0
while [ "$i" -lt "${#PASS[@]}" ]; do
  a="${PASS[$i]}"
  case "$a" in
    --load-game|--create|--load-scenario|--map-gen-settings|--map-settings|--map-gen-seed|--preset|--exchange-string|--until-tick)
      [ $((i + 1)) -lt "${#PASS[@]}" ] || die "factorio argument $a needs a value"
      v="${PASS[$((i + 1))]}"
      [ -n "$v" ] && [ "${v#-}" = "$v" ] || die "factorio argument $a has no value (got '$v')"
      i=$((i + 2)) ;;
    --verbose|--disable-migration-window)
      i=$((i + 1)) ;;
    *) die "factorio argument '$a' is not allowed (see the allow-list in --help)" ;;
  esac
done
for cmd in xvfb-run setsid flock jq; do
  command -v "$cmd" >/dev/null || die "$cmd is not installed"
done
if [ "$AUDIO" = 1 ]; then
  for cmd in pactl pw-metadata; do command -v "$cmd" >/dev/null || die "$cmd is not installed"; done
fi

. "$REPO_ROOT/tools/paths.sh"
sae_factorio_bin GAME_BIN || exit 1

mod_name_of() {  # PATH -> mod name
  local p="$1" b
  if [ -d "$p" ]; then
    jq -r '.name' "$p/info.json"
  else
    b="$(basename "$p" .zip)"
    echo "${b%_*}"
  fi
}
MOD_NAME="$(mod_name_of "$WORKTREE")"
[ -n "$MOD_NAME" ] && [ "$MOD_NAME" != null ] || die "no mod name in $WORKTREE/info.json"
EXTRA_NAMES=() EXTRA_PATHS=()
for m in "${EXTRA_MODS[@]}"; do
  [ -e "$m" ] || die "--mod $m does not exist"
  if [ -d "$m" ]; then [ -f "$m/info.json" ] || die "--mod $m has no info.json"
  else [[ "$m" == *.zip ]] || die "--mod $m is neither a folder nor a .zip"; fi
  n="$(mod_name_of "$m")"
  [ "$n" != "$MOD_NAME" ] || die "--mod $m is the worktree's mod ($n)"
  EXTRA_NAMES+=("$n")
  EXTRA_PATHS+=("$(cd "$(dirname "$m")" && pwd)/$(basename "$m")")
done

# ---------------------------------------------------------------- refusals

exec 9>>"$LOCK_FILE"
if ! flock -n 9; then
  echo "launch.sh: REFUSED -- another launcher holds $LOCK_FILE (one client at a time)." >&2 2>/dev/null
  exit 3
fi
if RUNNING="$(pgrep -a -x factorio)"; then
  echo "launch.sh: REFUSED -- a factorio process is already running (one client at a time):" >&2 2>/dev/null
  echo "$RUNNING" >&2 2>/dev/null
  exit 3
fi
if [ "$AUDIO" = 1 ]; then
  case "$(default_sink)" in
    "$NULL_PREFIX"*)
      echo "launch.sh: REFUSED -- the default sink is $(default_sink), left by an earlier run; use --recover on its run directory." >&2 2>/dev/null
      exit 3 ;;
  esac
fi

# ---------------------------------------------------------------- run directory

STAMP="$(date +%Y%m%d-%H%M%S)"
RUN="$REPO_ROOT/evidence/$TASK/client-$STAMP-$$"
mkdir -p "$RUN/data" || die "cannot create $RUN"
LOG="$RUN/launch.log" FLOG="$RUN/factorio.log" PIDS_FILE="$RUN/pids.txt"
: > "$PIDS_FILE" || { echo "launch.sh: cannot write in $RUN" >&2 2>/dev/null; exit 1; }

MODS_DIR=""
LEADER="" LEADER_REAPED=0 SID="" SID_START="" FPID="" FPID_START="" XVFB_PID="" XVFB_START="" XVFB_DISPLAY="" XVFB_TMP="" DISPLAY_USED=""
STOP_REASON="" CLIENT_EXIT="" EXIT_CODE=0 CLEANED=0 ESCALATE=0 STARTED_AT="$(date +%s)"
NULL_SINK="" NULL_INDEX="" ORIG_SINK="" ORIG_CONFIGURED="" SOUND_RESULT=""
AFTER_SINK="" AFTER_CONFIGURED="" AUDIO_CHECKS=0 SURVIVORS=""
MY_START="$(proc_start $$)" SID_RECORDED="" GATE_FILE="$RUN/gate.pid"
declare -A STARTED=() STREAMS=()

write_state() {
  local pids_json streams_json
  pids_json="$(for p in "${!STARTED[@]}"; do printf '%s %s\n' "$p" "${STARTED[$p]}"; done \
    | jq -R -s 'split("\n") | map(select(length > 0) | split(" ") | {pid: (.[0] | tonumber), comm: .[1]}) | sort_by(.pid)')"
  streams_json="$(for s in "${!STREAMS[@]}"; do printf '%s\n' "${STREAMS[$s]}"; done | jq -R -s 'split("\n") | map(select(length > 0))')"
  jq -n \
    --arg task "$TASK" --arg run "$RUN" --arg worktree "$WORKTREE" --arg mod "$MOD_NAME" --arg mods_dir "$MODS_DIR" \
    --arg bin "$GAME_BIN" --arg mode "$([ "$AUDIO" = 1 ] && echo audio || echo disable-audio)" \
    --arg lpid "$$" --arg lstart "$MY_START" \
    --arg leader "$LEADER" --arg sid "$SID_RECORDED" --arg sstart "$SID_START" --arg fpid "$FPID" --arg xvfb "$XVFB_PID" \
    --arg fstart "$FPID_START" --arg xstart "$XVFB_START" \
    --arg display "$DISPLAY_USED" --arg reason "$STOP_REASON" --arg client_exit "$CLIENT_EXIT" \
    --arg exit "$EXIT_CODE" --arg survivors "$SURVIVORS" \
    --arg null_sink "$NULL_SINK" --arg before "$ORIG_SINK" \
    --arg before_conf "$ORIG_CONFIGURED" --arg after "$AFTER_SINK" --arg after_conf "$AFTER_CONFIGURED" \
    --arg sound "$SOUND_RESULT" --arg checks "$AUDIO_CHECKS" \
    --argjson pids "$pids_json" --argjson streams "$streams_json" \
    --args '{
      task: $task, run_dir: $run, worktree: $worktree, mod: $mod, mods_dir: $mods_dir, factorio_bin: $bin,
      mode: $mode, factorio_args: $ARGS.positional,
      launcher: {pid: ($lpid | tonumber), start: $lstart},
      leader: ($leader | tonumber? // null), session: ($sid | tonumber? // null), session_start: $sstart,
      factorio_pid: ($fpid | tonumber? // null), factorio_start: $fstart,
      xvfb_pid: ($xvfb | tonumber? // null), xvfb_start: $xstart,
      display: $display, pids_started: $pids, stop_reason: $reason,
      client_exit: ($client_exit | tonumber? // null), exit: ($exit | tonumber),
      survivors: ($survivors | split(" ") | map(select(length > 0))),
      audio: (if $mode == "audio" then {
        null_sink: $null_sink, monitor: ($null_sink + ".monitor"),
        default_before: $before, configured_before: $before_conf,
        default_after: $after, configured_after: $after_conf, result: $sound,
        checks_while_running: ($checks | tonumber), client_streams: $streams } else null end)
    }' -- "${PASS[@]}" > "$RUN/run.json.tmp" && mv "$RUN/run.json.tmp" "$RUN/run.json"
}

record_pids() {
  [ -n "$SID" ] || return 0
  local pid comm
  while read -r pid comm; do
    [ -n "$pid" ] || continue
    if [ -z "${STARTED[$pid]:-}" ]; then
      STARTED[$pid]="$comm"
      printf '%s %s %s\n' "$pid" "$comm" "$({ tr '\0' ' ' < "/proc/$pid/cmdline"; } 2>/dev/null | cut -c1-300)" >> "$PIDS_FILE"
    fi
    [ "$comm" = Xvfb ] && [ -z "$XVFB_PID" ] && note_xvfb "$pid"
  done < <(session_pids "$SID")
}

note_xvfb() {  # remember the run's Xvfb: PID, start time, display and xvfb-run's auth folder
  local args
  args="$({ tr '\0' '\n' < "/proc/$1/cmdline"; } 2>/dev/null)"
  [ -n "$args" ] || return 0
  XVFB_PID="$1" XVFB_START="$(proc_start "$1")"
  XVFB_DISPLAY="$(sed -n '2p' <<< "$args")"
  XVFB_TMP="$(sed -n 's#^\(.*/xvfb-run\.[^/]*\)/Xauthority$#\1#p' <<< "$args")"
}

wait_gone() {  # pid sid tenths -- cut short by a second signal
  local i=0
  while [ "$i" -lt "$3" ] && [ "$ESCALATE" = 0 ] && alive_in_session "$1" "$2"; do sleep 0.1; i=$((i + 1)); done
  ! alive_in_session "$1" "$2"
}

wait_gone_always() {  # pid sid tenths -- not cut short, even by a second signal
  local i=0
  while [ "$i" -lt "$3" ] && alive_in_session "$1" "$2"; do sleep 0.1; i=$((i + 1)); done
}

session_empty_within() {  # tenths
  local i=0
  while [ "$i" -lt "$1" ] && [ -n "$(session_pids "$SID")" ]; do sleep 0.1; i=$((i + 1)); done
  [ -z "$(session_pids "$SID")" ]
}

find_gate() {  # tenths -- set SID from gate.pid once the gate is its own stopped session
  local i=0 g
  while [ "$i" -lt "$1" ]; do
    g="$(cat "$GATE_FILE" 2>/dev/null)"
    if [[ "$g" =~ ^[0-9]+$ ]] && [ "$(ps -o sid= -p "$g" 2>/dev/null | tr -d ' ')" = "$g" ] \
       && [[ "$(ps -o stat= -p "$g" 2>/dev/null)" == T* ]]; then
      SID="$g"; return 0
    fi
    sleep 0.1; i=$((i + 1))
  done
  return 1
}

stop_client() {  # stop the client, then whatever is left of the session
  local pid comm g
  if [ -z "$SID" ] && [ -n "$LEADER" ]; then
    # Stopped before the gate was found: find it now (it may still be writing
    # gate.pid), or failing that kill what $! was.
    if ! find_gate 20; then
      g="$(cat "$GATE_FILE" 2>/dev/null)"
      [[ "$g" =~ ^[0-9]+$ ]] && [ "$(ps -o sid= -p "$g" 2>/dev/null | tr -d ' ')" = "$g" ] && SID="$g"
    fi
    if [ -z "$SID" ]; then
      log "no gate session found; SIGKILL $LEADER"
      kill -KILL "$LEADER" 2>/dev/null
      wait "$LEADER" 2>/dev/null
      LEADER_REAPED=1
      return 0
    fi
    log "gate session $SID found during cleanup"
  fi
  [ -n "$SID" ] || return 0
  record_pids
  if [ -z "$FPID" ]; then
    # Never released, or released but the client not yet up: nothing to lose,
    # except that Xvfb, if it is up, removes its display lock and socket only
    # on SIGTERM; so it goes first, with its second of grace.
    if [ -n "$XVFB_PID" ] && alive_in_session "$XVFB_PID" "$SID"; then
      log "SIGTERM $XVFB_PID (Xvfb) -- the client never started"
      kill -TERM "$XVFB_PID" 2>/dev/null
      wait_gone_always "$XVFB_PID" "$SID" 10
    fi
    while read -r pid comm; do
      [ -n "$pid" ] || continue
      log "SIGKILL $pid ($comm) -- the client never started"; kill -KILL "$pid" 2>/dev/null
    done < <(session_pids "$SID")
    session_empty_within 20
  fi
  if [ -n "$FPID" ] && alive_in_session "$FPID" "$SID"; then
    # Once initialised it quits on SIGTERM in about a second; while it is still
    # loading sprites it ignores SIGTERM, and there is nothing there to lose.
    local grace=20
    grep -q 'Factorio initialised' "$FLOG" 2>/dev/null && grace=50
    log "stopping factorio $FPID (SIGTERM)"
    kill -TERM "$FPID" 2>/dev/null
    if ! wait_gone "$FPID" "$SID" "$grace"; then
      log "factorio $FPID still up after SIGTERM; SIGKILL"
      kill -KILL "$FPID" 2>/dev/null
      wait_gone "$FPID" "$SID" 30
    fi
  fi
  # With the client gone xvfb-run kills its Xvfb and exits by itself.
  [ "$ESCALATE" = 0 ] && alive_in_session "$SID" "$SID" && wait_gone "$SID" "$SID" 30
  if [ -n "$(session_pids "$SID")" ]; then
    while read -r pid comm; do
      [ -n "$pid" ] || continue
      log "SIGTERM $pid ($comm)"; kill -TERM "$pid" 2>/dev/null; kill -CONT "$pid" 2>/dev/null
    done < <(session_pids "$SID")
    # Even after a second signal: Xvfb removes its display lock on SIGTERM
    # within a few milliseconds, and not at all on SIGKILL.
    session_empty_within 10
    while read -r pid comm; do
      [ -n "$pid" ] || continue
      log "SIGKILL $pid ($comm)"; kill -KILL "$pid" 2>/dev/null
    done < <(session_pids "$SID")
    session_empty_within 20
  fi
  if [ -n "$LEADER" ] && [ "$LEADER_REAPED" = 0 ]; then
    wait "$LEADER" 2>/dev/null
    local st=$?
    [ -n "$CLIENT_EXIT" ] || CLIENT_EXIT=$st
    LEADER_REAPED=1
  fi
  # xvfb-run removes its auth folder on a normal exit; not after SIGKILL.
  if [ -n "$XVFB_TMP" ] && [ -d "$XVFB_TMP" ]; then
    case "$XVFB_TMP" in /tmp/xvfb-run.*) rm -r -- "$XVFB_TMP" && log "removed leftover $XVFB_TMP" ;; esac
  fi
  remove_stale_x_lock "$XVFB_PID" "$XVFB_DISPLAY"
}

restore_audio() {
  [ "$AUDIO" = 1 ] && [ -n "$NULL_SINK" ] || return 0
  if [ -n "$SID" ] && [ -n "$(session_pids "$SID")" ]; then
    log "AUDIO: the client's session is still alive; the null sink stays so nothing reaches the speakers -- run the recover line"
    EXIT_CODE=5; return
  fi
  if [ -n "$LEADER" ] && [ "$LEADER_REAPED" = 0 ] && [ -d "/proc/$LEADER" ]; then
    log "AUDIO: $LEADER (the gate's starter) is still alive; the null sink stays"
    EXIT_CODE=5; return
  fi
  if pgrep -x factorio > /dev/null; then
    log "AUDIO: a factorio process is running; the null sink stays so nothing reaches the speakers"
    EXIT_CODE=5; return
  fi
  restore_sound "$NULL_SINK" "$ORIG_SINK" "$ORIG_CONFIGURED" || EXIT_CODE=5
  AFTER_SINK="$(default_sink)" AFTER_CONFIGURED="$(configured_sink)"
}

cleanup() {
  [ "$CLEANED" = 1 ] && return
  CLEANED=1
  # A second signal does not stop the cleanup; it only skips the waiting.
  trap 'ESCALATE=1; log "second signal: killing at once"' INT TERM HUP
  stop_client
  restore_audio
  local p
  SURVIVORS=""
  for p in "${!STARTED[@]}"; do
    alive_in_session "$p" "$SID" && SURVIVORS+="$p "
  done
  [ -n "$SID" ] && [ -n "$(session_pids "$SID")" ] && SURVIVORS+="session-$SID "
  [ -n "$LEADER" ] && [ "$LEADER_REAPED" = 0 ] && [ -d "/proc/$LEADER" ] && SURVIVORS+="$LEADER "
  if [ -n "$SURVIVORS" ]; then
    log "FAIL -- still running after cleanup: $SURVIVORS"
    EXIT_CODE=5
  else
    log "all ${#STARTED[@]} PIDs started are gone: $(printf '%s ' "${!STARTED[@]}")${LEADER:+(and setsid $LEADER)}"
  fi
  [ -n "$MODS_DIR" ] && [ -d "$MODS_DIR" ] && rm -r -- "$MODS_DIR"
  rm -rf -- "${RUN:?}/data/temp" "${RUN:?}/data/crop-cache.dat"
  log "stop: ${STOP_REASON:-none}; client exit ${CLIENT_EXIT:-none}; launcher exit $EXIT_CODE"
  write_state || log "could not write the final run.json"
  flock -u 9
  exit "$EXIT_CODE"
}

on_signal() {
  STOP_REASON="signal $1"
  case "$1" in INT) EXIT_CODE=130 ;; TERM) EXIT_CODE=143 ;; HUP) EXIT_CODE=129 ;; esac
  log "received SIG$1; cleaning up"
  cleanup
}
trap cleanup EXIT
trap 'on_signal INT' INT
trap 'on_signal TERM' TERM
trap 'on_signal HUP' HUP

guard_kill() {  # a safety guard tripped: the client goes now
  log "GUARD: $*"
  [ -n "$FPID" ] && kill -KILL "$FPID" 2>/dev/null
  STOP_REASON="guard: $*" EXIT_CODE=6
  exit 6
}

setup_fail() { STOP_REASON="setup failed: $*"; EXIT_CODE=1; log "SETUP FAILED -- $*"; exit 1; }

log "run dir: $RUN"
log "if this launcher is killed outright, run: $SCRIPT_DIR/launch.sh --recover $RUN"
write_state || setup_fail "cannot write $RUN/run.json"

# ---------------------------------------------------------------- scratch mods and config

MODS_DIR="$(mktemp -d -t sae-client-mods.XXXXXX)" || setup_fail "mktemp"
write_state || setup_fail "cannot write $RUN/run.json"
ln -s "$WORKTREE" "$MODS_DIR/$MOD_NAME" || setup_fail "symlink $MOD_NAME"
for k in "${!EXTRA_PATHS[@]}"; do
  m="${EXTRA_PATHS[$k]}"
  if [ -d "$m" ]; then link="$MODS_DIR/${EXTRA_NAMES[$k]}"; else link="$MODS_DIR/$(basename "$m")"; fi
  ln -s "$m" "$link" || setup_fail "symlink $m"
done
printf '%s\n' base elevated-rails quality recycler space-age "${EXTRA_NAMES[@]}" "$MOD_NAME" \
  | jq -R -s '{mods: (split("\n") | map(select(length > 0) | {name: ., enabled: true}))}' \
  > "$MODS_DIR/mod-list.json" || setup_fail "mod-list.json"

cat > "$RUN/config.ini" <<EOF || setup_fail "config.ini"
; Written by tools/client/launch.sh for this run only.
[path]
read-data=__PATH__executable__/../../data
write-data=$RUN/data

[general]
locale=en

[other]
enable-steam-networking=false
enable-blueprint-storage-cloud-sync=false
enable-new-mods=false

[graphics]
full-screen=false
EOF

# Check what was written, not that the writes returned 0.
[ "$(sed -n 's/^write-data=//p' "$RUN/config.ini")" = "$RUN/data" ] || setup_fail "config.ini write-data is not $RUN/data"
[ "$(readlink "$MODS_DIR/$MOD_NAME")" = "$WORKTREE" ] && [ -f "$MODS_DIR/$MOD_NAME/info.json" ] \
  || setup_fail "$MODS_DIR/$MOD_NAME does not lead to $WORKTREE"
for k in "${!EXTRA_PATHS[@]}"; do
  m="${EXTRA_PATHS[$k]}"
  if [ -d "$m" ]; then link="$MODS_DIR/${EXTRA_NAMES[$k]}"; else link="$MODS_DIR/$(basename "$m")"; fi
  [ "$(readlink "$link")" = "$m" ] && [ -e "$link" ] || setup_fail "$link does not lead to $m"
done
[ "$(jq -r '[.mods[].name] | join(" ")' "$MODS_DIR/mod-list.json" 2>/dev/null)" \
  = "$(printf '%s ' base elevated-rails quality recycler space-age "${EXTRA_NAMES[@]}" "$MOD_NAME" | sed 's/ $//')" ] \
  || setup_fail "mod-list.json does not list the mods"
log "checked config.ini (write-data $RUN/data), mod links and mod-list.json"
log "worktree: $WORKTREE (mod $MOD_NAME)${EXTRA_NAMES[*]:+; extra mods: ${EXTRA_NAMES[*]}}"
log "factorio: $GAME_BIN"

# ---------------------------------------------------------------- audio

AUDIO_ARGS=(--disable-audio)
AUDIO_ENV=()
if [ "$AUDIO" = 1 ]; then
  AUDIO_ARGS=()
  ORIG_SINK="$(default_sink)" ORIG_CONFIGURED="$(configured_sink)"
  [ -n "$ORIG_SINK" ] || { log "AUDIO: cannot read the default sink"; EXIT_CODE=4; exit 4; }
  log "AUDIO: default sink before: $ORIG_SINK (configured ${ORIG_CONFIGURED:-unset})"
  # The name is recorded before the module exists, so a signal at any point
  # from here on still finds and unloads it by name.
  NULL_SINK="$NULL_PREFIX$$"
  write_state || setup_fail "cannot write $RUN/run.json"
  if ! m="$(pactl load-module module-null-sink "sink_name=$NULL_SINK" \
        "sink_properties=device.description=SAE-client-null-$$")"; then
    log "AUDIO: could not load module-null-sink"; EXIT_CODE=4; exit 4
  fi
  log "AUDIO: loaded module $m ($NULL_SINK)"
  pactl set-default-sink "$NULL_SINK"
  for _ in $(seq 20); do
    [ "$(default_sink)" = "$NULL_SINK" ] && break
    sleep 0.1
  done
  if [ "$(default_sink)" != "$NULL_SINK" ]; then
    log "AUDIO: the default sink is $(default_sink), not $NULL_SINK -- not starting the client"
    EXIT_CODE=4; exit 4
  fi
  NULL_INDEX="$(sink_index "$NULL_SINK")"
  log "AUDIO: verified default sink = $NULL_SINK (index $NULL_INDEX) before the client starts"
  AUDIO_ENV=("PULSE_SINK=$NULL_SINK")
fi

audio_check() {  # the default and every client stream must stay on the null sink
  local d idx sink
  d="$(default_sink)"
  [ "$d" = "$NULL_SINK" ] || guard_kill "default sink changed to '$d' during the run"
  while read -r idx sink; do
    [ -n "$idx" ] || continue
    if [ -z "${STREAMS[$idx]:-}" ]; then
      STREAMS[$idx]="sink-input $idx on sink $sink"
      log "AUDIO: client stream sink-input $idx on sink $sink"
    fi
    [ "$sink" = "$NULL_INDEX" ] || guard_kill "client stream $idx is on sink $sink, not the null sink $NULL_INDEX"
  done < <(client_streams "$FPID")
  AUDIO_CHECKS=$((AUDIO_CHECKS + 1))
}

# ---------------------------------------------------------------- launch

# The gate: in a new session (setsid) a shell writes its own PID to gate.pid
# and stops itself before anything else runs; the launcher lets it go only
# once run.json names the session. setsid always forks (--fork), so there is
# one path whether or not the launcher runs under job control: $! is setsid,
# which waits (--wait) and hands back the client's exit status, and the
# session is the gate's, known only from gate.pid.
setsid --fork --wait sh -c 'echo $$ > "$0" || exit 1; kill -STOP $$; exec "$@"' "$GATE_FILE" \
  env --default-signal=PIPE -u WAYLAND_DISPLAY -u WAYLAND_SOCKET \
  -u SAE_LAUNCH_SIGINT_RESET -u SAE_LAUNCH_TEST_HOLD \
  SDL_VIDEO_DRIVER=x11 SDL_VIDEODRIVER=x11 SteamAppId=427520 SteamGameId=427520 "${AUDIO_ENV[@]}" \
  xvfb-run -a -s "-screen 0 $SCREEN" \
  "$GAME_BIN" --config "$RUN/config.ini" --mod-directory "$MODS_DIR" \
  "${AUDIO_ARGS[@]}" "${PASS[@]}" > "$FLOG" 2>&1 < /dev/null &
LEADER=$!
find_gate 50 || setup_fail "the gate never became its own stopped session"
SID_START="$(proc_start "$SID")"
log "setsid $LEADER started gate session $SID (stopped)"
record_pids
if [ "${SAE_LAUNCH_TEST_HOLD:-}" = before-session ]; then
  log "TEST HOLD before-session: gate session $SID exists, run.json does not name it (60 s)"
  for _ in $(seq 120); do sleep 0.5; done
fi
SID_RECORDED="$SID"
write_state || setup_fail "cannot write $RUN/run.json"
log "session $SID recorded (start $SID_START); releasing it"
kill -CONT "$SID"
if [ "${SAE_LAUNCH_TEST_HOLD:-}" = after-release ]; then
  log "TEST HOLD after-release: the gate is released, the client not yet looked for (60 s)"
  for _ in $(seq 120); do sleep 0.5; record_pids; done
fi

# The Steam wrapper bin/x64/factorio is a shell script that execs the real
# binary under the same PID; wait for the real one.
for _ in $(seq 300); do
  record_pids
  FPID=""
  while read -r pid comm; do
    [ -z "$FPID" ] && [ "$comm" = factorio ] && is_real_factorio "$pid" && FPID="$pid"
  done < <(session_pids "$SID")
  [ -n "$FPID" ] && break
  [ -n "$(session_pids "$SID")" ] || break
  sleep 0.1
done
if [ -z "$FPID" ]; then
  STOP_REASON="client never started (see $FLOG)" EXIT_CODE=1
  log "$STOP_REASON"
  exit 1
fi
record_pids
FPID_START="$(proc_start "$FPID")"
[ -n "$XVFB_PID" ] || note_xvfb "$(session_pids "$SID" | awk '$2 == "Xvfb" && !f { print $1; f = 1 }')"
CLIENT_ENV="$({ tr '\0' '\n' < "/proc/$FPID/environ"; } 2>/dev/null)"
[ -n "$CLIENT_ENV" ] || guard_kill "cannot read factorio's environment"
DISPLAY_USED="$(sed -n 's/^DISPLAY=//p' <<< "$CLIENT_ENV")"
log "factorio $FPID ($(readlink "/proc/$FPID/exe")) on display $DISPLAY_USED (Xvfb $XVFB_PID)"

# The guards: checked on the process itself, not on what was asked for.
if grep -q '^WAYLAND_DISPLAY=' <<< "$CLIENT_ENV"; then
  guard_kill "WAYLAND_DISPLAY is set in factorio's environment"
fi
log "checked /proc/$FPID/environ: no WAYLAND_DISPLAY"
if [ "$AUDIO" = 0 ]; then
  { tr '\0' '\n' < "/proc/$FPID/cmdline"; } 2>/dev/null | grep -qx -- '--disable-audio' \
    || guard_kill "--disable-audio is missing from factorio's command line"
  log "checked /proc/$FPID/cmdline: --disable-audio present"
else
  audio_check
fi
write_state || log "could not write run.json"

# ---------------------------------------------------------------- run

DEADLINE=$((STARTED_AT + TIMEOUT))
DONE_PATH="$RUN/data/script-output/$DONE_FILE"
while :; do
  record_pids
  if ! alive_in_session "$FPID" "$SID"; then
    wait "$LEADER" 2>/dev/null
    CLIENT_EXIT=$?
    LEADER_REAPED=1
    STOP_REASON="client exited"
    log "client exited ($CLIENT_EXIT)"
    [ "$CLIENT_EXIT" = 0 ] || EXIT_CODE=1
    break
  fi
  [ "$AUDIO" = 1 ] && audio_check
  if [ -n "$DONE_FILE" ] && [ -e "$DONE_PATH" ]; then
    STOP_REASON="done-file $DONE_FILE"; log "$STOP_REASON appeared"; break
  fi
  if [ -n "$UNTIL_LOG" ] && grep -qE -- "$UNTIL_LOG" "$FLOG"; then
    STOP_REASON="until-log matched"; log "log matched /$UNTIL_LOG/"; break
  fi
  if [ "$(date +%s)" -ge "$DEADLINE" ]; then
    STOP_REASON="timeout ${TIMEOUT}s"
    if [ -n "$DONE_FILE" ] || [ -n "$UNTIL_LOG" ]; then
      EXIT_CODE=124; log "timed out after ${TIMEOUT}s waiting for the stop condition"
    else
      log "ran for ${TIMEOUT}s"
    fi
    break
  fi
  sleep 0.5
done
exit "$EXIT_CODE"
