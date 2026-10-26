# tools/paths.sh -- reads tools/paths.conf, where this checkout's Factorio and
# Blender are, for the shell scripts. Sourced (this file is code; paths.conf is
# data, parsed here line by line and never sourced, eval'd or expanded):
#
#   . "<repo>/tools/paths.sh"
#   sae_factorio_bin GAME_BIN || exit 1    # <FACTORIO_ROOT>/bin/x64/factorio
#   sae_factorio_data GAME_DATA || exit 1  # <FACTORIO_ROOT>/data
#   sae_blender BLENDER_BIN || exit 1      # BLENDER
#
# Each sets the variable it is given, or prints why it cannot -- naming
# paths.conf and the key -- and returns 1: a key missing, empty or named twice,
# a path that does not exist, a line that is not KEY=value. The paths.conf read
# is the one beside this file, so each checkout reads its own. The format is in
# paths.conf; tools/paths.py is the same reader for Python.

SAE_PATHS_CONF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/paths.conf"

sae_paths_value() {  # KEY VAR: VAR = KEY's value, as written
  local _sae_value_key="$1" _sae_value_line _sae_value_text _sae_value_got="" _sae_value_found=0 _sae_value_n=0
  local _sae_value_re='^([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*=(.*)$'
  if [ ! -f "$SAE_PATHS_CONF" ] || [ ! -r "$SAE_PATHS_CONF" ]; then
    echo "$SAE_PATHS_CONF: cannot read it, so $_sae_value_key is unknown" >&2
    return 1
  fi
  while IFS= read -r _sae_value_line || [ -n "$_sae_value_line" ]; do
    _sae_value_n=$((_sae_value_n + 1))
    _sae_value_line="${_sae_value_line%$'\r'}"
    _sae_value_text="${_sae_value_line#"${_sae_value_line%%[![:space:]]*}"}"
    case "$_sae_value_text" in ''|'#'*) continue ;; esac
    if ! [[ "$_sae_value_text" =~ $_sae_value_re ]]; then
      echo "$SAE_PATHS_CONF: line $_sae_value_n is not KEY=value (reading $_sae_value_key)" >&2
      return 1
    fi
    [ "${BASH_REMATCH[1]}" = "$_sae_value_key" ] || continue
    if [ "$_sae_value_found" = 1 ]; then
      echo "$SAE_PATHS_CONF: $_sae_value_key is set twice (line $_sae_value_n)" >&2
      return 1
    fi
    _sae_value_found=1
    _sae_value_got="${BASH_REMATCH[2]}"
    _sae_value_got="${_sae_value_got#"${_sae_value_got%%[![:space:]]*}"}"
    _sae_value_got="${_sae_value_got%"${_sae_value_got##*[![:space:]]}"}"
  done < "$SAE_PATHS_CONF"
  if [ "$_sae_value_found" = 0 ]; then
    echo "$SAE_PATHS_CONF: no $_sae_value_key= line" >&2
    return 1
  fi
  if [ -z "$_sae_value_got" ]; then
    echo "$SAE_PATHS_CONF: $_sae_value_key is empty" >&2
    return 1
  fi
  printf -v "$2" '%s' "$_sae_value_got"
}

# Bash's locals are seen by the functions a function calls, and printf -v sets
# the innermost variable of that name: so each function's locals are its own
# (_sae_<function>_...), and a caller's VAR must not start with _sae_.

sae_factorio_root() {  # VAR: the Factorio install folder
  local _sae_root_value
  sae_paths_value FACTORIO_ROOT _sae_root_value || return 1
  if [ ! -d "$_sae_root_value" ]; then
    echo "$SAE_PATHS_CONF: FACTORIO_ROOT=$_sae_root_value: no such directory" >&2
    return 1
  fi
  printf -v "$1" '%s' "$_sae_root_value"
}

sae_factorio_bin() {  # VAR: <FACTORIO_ROOT>/bin/x64/factorio
  local _sae_bin_root
  sae_factorio_root _sae_bin_root || return 1
  if [ ! -f "$_sae_bin_root/bin/x64/factorio" ] || [ ! -x "$_sae_bin_root/bin/x64/factorio" ]; then
    echo "$SAE_PATHS_CONF: FACTORIO_ROOT=$_sae_bin_root has no executable bin/x64/factorio" >&2
    return 1
  fi
  printf -v "$1" '%s' "$_sae_bin_root/bin/x64/factorio"
}

sae_factorio_data() {  # VAR: <FACTORIO_ROOT>/data
  local _sae_data_root
  sae_factorio_root _sae_data_root || return 1
  if [ ! -d "$_sae_data_root/data/base" ]; then
    echo "$SAE_PATHS_CONF: FACTORIO_ROOT=$_sae_data_root has no data/base directory" >&2
    return 1
  fi
  printf -v "$1" '%s' "$_sae_data_root/data"
}

sae_blender() {  # VAR: the Blender binary
  local _sae_blender_path
  sae_paths_value BLENDER _sae_blender_path || return 1
  if [ ! -f "$_sae_blender_path" ] || [ ! -x "$_sae_blender_path" ]; then
    echo "$SAE_PATHS_CONF: BLENDER=$_sae_blender_path: no such executable file" >&2
    return 1
  fi
  printf -v "$1" '%s' "$_sae_blender_path"
}
