#!/usr/bin/env python3
"""The Bash hook, .claude/hooks/no-ghost-waits.py, against a table of commands.

  python3 test/test_hooks.py [-v]

Each row is a Bash command and what the hook must do with it: "allow" (exit 0) or one of the
blocks (exit 2, its message on stderr): "loop" (a polling loop: while/until/select, or an
arithmetic for, with sleep in it), "scratch" (a recursive delete above
scratchpad/<role>/<ticket> under /tmp), "pkill" (pkill/killall), "killname" (kill given
pgrep/pidof's PIDs), "factorio" (the game binary run directly) or "deep" (nested past the
hook's MAX_DEPTH). The command goes to the hook as the PreToolUse JSON Claude Code sends, with
cwd the repo root; nothing in it is run. The block is told apart by the start of its message.
-v prints every row, not only the failures.

Exits 0 when every row comes out as listed, 1 naming those that do not.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, ".claude", "hooks", "no-ghost-waits.py")

PROJ = "/tmp/claude-1000/-home-lstan-data-git-space-age-extended"
SESSION = PROJ + "/f78b89ed-2ad6-4f84-8939-62aaf5301072"
SP = SESSION + "/scratchpad"
OTHER_SP = PROJ + "/0a1b2c3d-0000-4000-8000-000000000000/scratchpad"
T04 = SP + "/coder/agent-setup-T04"
FROOT = "/mnt/data/SteamLibrary/steamapps/common/Factorio"
FBIN = FROOT + "/bin/x64/factorio"
LOG = SP + "/artist/drop-crusher-T03/render/render.log"

# What each block's message starts with, after "Blocked by .claude/hooks/no-ghost-waits.py: ".
SIGNS = {
    "loop": "a polling loop",
    "scratch": "this deletes",
    "pkill": None,                      # "`pkill` stops ..." or "`killall` stops ..."
    "killname": "this kills processes found by name",
    "factorio": "this runs the Factorio binary",
    "deep": "this command nests",
}

TABLE = [
    # ---- the acceptance line
    (f'until grep -q "^exit" {LOG}; do sleep 30; done', "loop"),
    (f"find {SP} -mindepth 1 -maxdepth 1 ! -name artist-render -exec rm -rf {{}} +", "scratch"),
    ("tools/client/launch.sh --task T04 -- --disable-audio", "allow"),
    ("tools/check-data-stage.sh", "allow"),
    ("timeout 600 tail --pid=1 -f /dev/null", "allow"),

    # ---- loops: a while/until/select with sleep anywhere inside it
    ("while true; do sleep 5; done", "loop"),
    ("while sleep 5; do ls; done", "loop"),
    ("while :\ndo\n  test -f done.txt && break\n  sleep 10\ndone", "loop"),
    ("until [ -f out/render.done ]; do /usr/bin/sleep 2; done; cat out/render.done", "loop"),
    ("while kill -0 1234; do timeout 5 sleep 1; done", "loop"),
    ("while true; do echo \"$(sleep 1)\"; done", "loop"),
    ("while true; do for i in 1 2; do sleep 1; done; done", "loop"),
    ("while read -r f; do sleep 1; echo \"$f\"; done < list.txt", "loop"),
    (f"timeout 3600 bash -c 'until grep -q \"^exit\" {LOG}; do sleep 30; done'", "loop"),
    ("nohup sh -c \"while true; do sleep 60; done\" > /dev/null &", "loop"),
    ("x=$(while true; do sleep 1; done)", "loop"),
    ("eval 'while true; do sleep 1; done'", "loop"),
    ("ls | while read l; do sleep 1; done", "loop"),
    ("while true; do sleep 1", "loop"),                       # no `done` yet
    ("select x in a b; do sleep 1; done", "loop"),
    # for loops (fix 1): arithmetic for polls, a word list is bounded
    ("for ((;;)); do sleep 1; done", "loop"),
    ("for (( ; ; )); do test -f x && break; sleep 5; done", "loop"),
    ("for ((i=0; i<100000; i++)); do sleep 1; done", "loop"),
    ("for ((i=0; i<3; i++)); do echo $i; done", "allow"),       # no sleep
    ("for i in 1 2 3; do sleep 1; done", "allow"),
    ("for f in *.png; do sleep 1; optipng \"$f\"; done", "allow"),
    ("for f in *.png; do echo \"$f\"; done", "allow"),
    # a generated word list polls (round 3, Liam: "Block it"); a literal one does not
    ("for i in $(seq 60); do grep -q done log && break; sleep 10; done", "loop"),
    ("for i in {1..60}; do sleep 1; done", "allow"),
    ("for f in $FILES; do sleep 1; done", "loop"),
    ("for f in $(ls); do echo \"$f\"; done", "allow"),         # no sleep
    ("for i in `seq 5`; do sleep 1; done", "loop"),
    ("for f in \"$@\"; do sleep 1; done", "loop"),
    ("for x; do sleep 1; done", "loop"),                       # over "$@"
    ("F='a b'; for f in $F; do sleep 1; done", "loop"),        # a variable, set or not
    ("for i in 1 2 $((n+1)); do sleep 1; done", "loop"),
    ("for i in 1 2 \"$(date)\"; do echo $i; done", "allow"),
    # not polling
    ("while read -r f; do echo \"$f\"; done < list.txt", "allow"),
    ("while IFS= read -r line; do printf '%s\\n' \"$line\"; done <<'EOF'\na\nb\nEOF", "allow"),
    ("x=0; while [ $x -lt 3 ]; do x=$((x+1)); done", "allow"),
    ("while true; do break; done; sleep 5", "allow"),         # the sleep is after the loop
    ("sleep 2", "allow"),
    ("echo sleep | while read c; do echo \"$c\"; done", "allow"),
    ("while true; do sleeper; done", "allow"),
    ("echo \"while true; do sleep 1; done\"", "allow"),
    ("grep -n 'until grep -q' .claude/hooks/no-ghost-waits.py", "allow"),
    ("git commit -m \"Ban while/until loops with sleep in them\"", "allow"),
    ("cat > notes.txt <<'EOF'\nwhile true; do sleep 1; done\nEOF", "allow"),
    ("git commit -m \"$(cat <<'EOF'\nHook: no `while true; do sleep 1; done`, don't pkill.\n"
     "rm -rf /tmp is refused too (it's shared).\nEOF\n)\"", "allow"),
    ("# while true; do sleep 1; done\nls", "allow"),

    # ---- scratch deletes
    (f"rm -rf {T04}", "allow"),
    (f"rm -r {T04}/", "allow"),
    (f"rm -rf {T04}/*", "allow"),
    (f"rm -rf {T04}/renders/take-*", "allow"),
    (f"rm -rf {T04}/{{a,b}}", "allow"),
    (f"rm -rf {SP}/coder/{{T04,T05}}", "allow"),               # two ticket folders
    (f"rm -rf {T04} {SP}/coder/agent-setup-T05", "allow"),
    (f"rm -rf {OTHER_SP}/tester/T06", "allow"),
    (f"find {T04} -name '*.tmp' -delete", "allow"),
    (f"find {T04} -mindepth 1 -maxdepth 1 -exec rm -rf {{}} +", "allow"),
    (f"find {T04} -mindepth 1 -maxdepth 1 -exec sh -c 'rm -rf \"$1\"' _ {{}} \\;", "allow"),
    (f"S={SP}; rm -rf \"$S/coder/agent-setup-T04\"", "allow"),
    (f"cd {SP}/coder && rm -rf agent-setup-T04", "allow"),
    (f"cd {T04} && rm -rf *", "allow"),
    (f"find {SP} -maxdepth 2 -type d", "allow"),               # no delete
    (f"find {SP} -name '*.log' -exec grep -l error {{}} +", "allow"),
    (f"rm {SP}/coder/note.txt", "allow"),                       # not recursive
    ("rm -rf build/ evidence/T04", "allow"),                    # in the repo, not /tmp
    ("rm -rf /home/lstan/tmp/old", "allow"),
    ("rm -rf ~/scratch-old", "allow"),
    ("find . -name '__pycache__' -exec rm -rf {} +", "allow"),
    ("rm -rf \"$RUN_DIR\"", "allow"),                          # unset: `rm -rf ""`, nothing
    ("echo rm -rf /tmp", "allow"),
    ("git commit -m \"never rm -rf /tmp or find -delete the scratchpad\"", "allow"),
    ("grep -rn 'rm -rf' tools/", "allow"),
    (f"ls {SP} && du -sh {SP}/*", "allow"),
    (f"for d in {T04}/take-1 {T04}/take-2; do rm -rf \"$d\"; done", "allow"),
    (f"trap 'rm -rf {T04}/run' EXIT; ls", "allow"),
    (f"rm -rf {T04} 2>/dev/null; ls {SP}", "allow"),
    # a cd in a subshell or a pushd/popd pair does not leak (fix 3)
    ("(cd /tmp && ls); rm -rf build", "allow"),
    ("pushd /tmp >/dev/null; ls; popd >/dev/null; rm -rf build", "allow"),
    ("(cd /tmp; (cd claude-1000 && ls); ls) && rm -rf build", "allow"),
    ("pushd /tmp; rm -rf build", "scratch"),                   # still in /tmp: /tmp/build
    ("(cd /tmp && rm -rf build)", "scratch"),
    # a variable the command sets counts as set, even from $(...) (fix 4)
    ("d=$(mktemp -d); touch $d/a; rm -rf \"$d\"/*", "allow"),
    ("d=`mktemp -d`; rm -rf \"$d\"", "allow"),
    ("OUT=$(pwd)/out; rm -rf \"$OUT\"/*", "allow"),
    # ${X:-word} and kin: the word when X is not set here, else X (round 3, finding A)
    ("rm -rf \"${D:-/tmp}\"", "scratch"),
    (f"rm -rf \"${{D:-{SP}}}\"", "scratch"),
    (f"rm -rf \"${{D-{SP}}}\"", "scratch"),
    (f"rm -rf \"${{D:={SP}}}\"", "scratch"),
    ("rm -rf \"${D=/tmp/}\"", "scratch"),
    (f": \"${{D:={SP}}}\"; rm -rf \"$D\"/*", "scratch"),      # := sets D for later
    (f"rm -rf \"${{D:-${{E:-{SP}}}}}\"", "scratch"),          # nested default
    (f"rm -rf ${{D:-\"{SP}/coder\"}}/*", "scratch"),
    ("rm -rf \"${D:-/tmp/claude-1000/*}\"", "scratch"),
    (f"D={SP}; rm -rf \"${{D:-{T04}}}\"", "scratch"),          # D set: its value
    ("rm -rf \"${D#x}\"/*", "scratch"),                         # other forms: plain $D, unset
    ("rm -rf \"${OUT:-build}\"/*", "allow"),
    (f"rm -rf \"${{D:-{T04}}}\"", "allow"),
    (f"D={T04}; rm -rf \"${{D:-/tmp}}\"", "allow"),
    ("rm -rf \"${D:-$(mktemp -d)}\"", "allow"),                # default set, value unknown
    ("rm -rf \"${D:+/tmp}\"", "allow"),                        # plain $D: unset, `rm -rf ""`
    ("x=\"${X:-$(pkill y)}\"", "pkill"),                       # a default's $(...) is read
    ("echo " + "${X:-" * 400, "deep"),
    # refused
    (f"rm -rf {SP}", "scratch"),
    (f"rm -rf {SP}/", "scratch"),
    (f"rm -rf {SP}/*", "scratch"),
    (f"rm -rf {SP}/coder", "scratch"),
    (f"rm -rf {SP}/coder/*", "scratch"),
    (f"rm -rf {SP}/coder/agent-*", "scratch"),
    (f"rm -rf {SP}/*/agent-setup-T04", "scratch"),
    (f"rm -rf {SP}/{{coder,artist}}", "scratch"),
    (f"rm -rf {T04}/../..", "scratch"),
    (f"rm -rf {T04} {SP}", "scratch"),                         # one bad target is enough
    (f"rm -fr -- {SP}", "scratch"),
    (f"rm --recursive --force {SP}/coder", "scratch"),
    (f"sudo rm -rf {SP}/*", "scratch"),
    (f"\\rm -rf {SP}/*", "scratch"),
    (f"/usr/bin/rm -rf {SP}", "scratch"),
    ("rm -rf /tmp", "scratch"),
    ("rm -rf /tmp/", "scratch"),
    ("rm -rf /tmp/*", "scratch"),
    ("rm -rf /tmp/claude-1000", "scratch"),
    ("rm -rf /tmp/claude-1000/*", "scratch"),
    (f"rm -rf {PROJ}", "scratch"),
    (f"rm -rf {SESSION}", "scratch"),
    ("rm -rf /tmp/sae-old-render", "scratch"),                 # /tmp, not a scratchpad
    ("rm -rf /*", "scratch"),
    ("rm -rf /{tmp,var}", "scratch"),                          # brace list
    ("rm -rf /{var,t{mp,ext}}", "scratch"),
    (f"S={SP}; rm -rf \"$S\"/*", "scratch"),
    (f"S={SP}; rm -rf \"${{S}}\"", "scratch"),
    (f"export S={SP} && rm -rf $S/*", "scratch"),
    (f"S={SP}; rm -rf \"$S/coder/$T\"", "scratch"),            # $T unset: that is $S/coder/
    ("rm -rf \"$S\"/*", "scratch"),                            # $S unset here: that is /*
    ("rm -rf \"$X\"*", "scratch"),                             # unset: `*`, all of cwd
    ("rm -rf \"$OUT/$NAME\"", "scratch"),                      # both unset: `rm -rf /`
    ("rm -rf \"$OUT\"/\"$NAME\"/*", "scratch"),
    (f"cd {SP} && rm -rf *", "scratch"),
    (f"cd {SP} && find . -mindepth 1 -delete", "scratch"),
    (f"cd {T04} && rm -rf ../../*", "scratch"),
    (f"find {SP} -name '*.png' -delete", "scratch"),
    (f"find {SP}/coder -mindepth 1 -maxdepth 1 -exec rm -rf {{}} +", "scratch"),
    (f"find {SP} -type d -execdir rm -r {{}} \\;", "scratch"),
    (f"find {SP} -name '*.png' -exec rm {{}} +", "scratch"),   # rm of files, every agent's
    ("find /tmp -maxdepth 1 -name 'sae-*' -exec rm -rf {} +", "scratch"),
    (f"find -L {SP} -mindepth 1 -maxdepth 1 -print0 | xargs -0 rm -rf", "scratch"),
    # find -exec running a shell string (fix 5)
    (f"find {SP} -mindepth 1 -maxdepth 1 ! -name x -exec sh -c 'rm -rf \"$1\"' _ {{}} \\;",
     "scratch"),
    (f"find {SP} -mindepth 1 -maxdepth 1 -exec bash -c 'rm -rf \"$@\"' _ {{}} +", "scratch"),
    (f"find {SP} -mindepth 1 -exec sh -c 'rm -r {{}}' \\;", "scratch"),
    (f"find {SP} -mindepth 1 -exec sudo rm -rf {{}} +", "scratch"),
    (f"find {SP} -exec sh -c 'rm \"$1\"' _ {{}} \\;", "scratch"),
    (f"find {SP} -mindepth 1 -maxdepth 1 -exec sh -c 'for d; do rm -rf \"$d\"; done' _ {{}} +",
     "scratch"),
    (f"bash -c \"bash -c 'rm -rf {SP}/coder'\"", "scratch"),
    (f"bash -c 'rm -rf {SP}/*'", "scratch"),
    (f"x=$(rm -rf {SP})", "scratch"),
    (f"for d in {SP}/*; do rm -rf \"$d\"; done", "scratch"),
    (f"for d in {SP}/coder/T04 {SP}; do rm -rf $d; done", "scratch"),
    (f"trap 'rm -rf {SP}/coder' EXIT; ls", "scratch"),

    # ---- pkill / killall
    ("pkill -f blender", "pkill"),
    ("killall factorio", "pkill"),
    ("killall -9 Xvfb", "pkill"),
    ("sudo pkill -TERM -x factorio", "pkill"),
    ("/usr/bin/pkill Xvfb", "pkill"),
    ("ls; pkill -9 Xvfb", "pkill"),
    ("timeout 5 pkill blender || true", "pkill"),
    ("bash -c \"pkill -f render.sh\"", "pkill"),
    ("bash -c \"bash -c 'pkill x'\"", "pkill"),
    ("n=$(pkill -c -f blender)", "pkill"),
    ("pgrep -f blender | xargs pkill -P", "pkill"),
    ("find . -name '*.pid' -exec pkill -F {} \\;", "pkill"),
    # kill by name through pgrep/pidof (fix 2)
    ("kill $(pgrep blender)", "killname"),
    ("kill -9 $(pgrep -f 'render.sh --model')", "killname"),
    ("kill `pidof Xvfb`", "killname"),
    ("kill -TERM $(pidof factorio) 2>/dev/null", "killname"),
    ("P=$(pgrep -x factorio); kill $P", "killname"),
    ("kill $(echo $(pgrep blender))", "killname"),
    ("pgrep -f blender | xargs kill", "killname"),
    ("pgrep -f blender | xargs -r kill -9", "killname"),
    ("pidof Xvfb | xargs kill", "killname"),
    ("bash -c 'kill $(pgrep blender)'", "killname"),
    ("kill $(pgrep -P $$)", "killname"),                      # pgrep all the same
    # by PID, or the word only mentioned
    ("kill 12345", "allow"),
    ("kill \"$PID\"", "allow"),
    ("kill -TERM 12345 12346 && wait 12345", "allow"),
    ("kill $(cat evidence/T06/client-1/pids.txt)", "allow"),
    ("xargs kill < evidence/T06/client-1/pids.txt", "allow"),
    ("pgrep -a x", "allow"),
    ("pgrep -a -x factorio", "allow"),
    ("pgrep -f blender | wc -l", "allow"),
    ("grep -n pkill .claude/hooks/no-ghost-waits.py", "allow"),
    ("man pkill", "allow"),
    ("command -v pkill killall", "allow"),
    ("echo 'do not pkill'", "allow"),
    ("echo \"kill $(pgrep x)\" > notes.txt", "allow"),       # echo runs, not kill
    ("git commit -m \"hook: block pkill and killall\"", "allow"),

    # ---- the Factorio binary
    (f"{FBIN} --version", "factorio"),
    (f"\"{FBIN}\" --dump-data", "factorio"),
    ("\"$(python3 tools/paths.py factorio-bin)\" --version", "factorio"),
    ("G=$(python3 tools/paths.py factorio-bin); \"$G\" --dump-data", "factorio"),
    ("source tools/paths.sh && sae_factorio_bin G && \"$G\" --version", "factorio"),
    (f"cd {FROOT} && bin/x64/factorio --start-server s.zip", "factorio"),
    (f"cd {FROOT}/bin/x64 && ./factorio --version", "factorio"),
    (f"R={FROOT}; $R/bin/x64/factorio --version", "factorio"),
    ("env -u WAYLAND_DISPLAY \"$ROOT/bin/x64/factorio\" --disable-audio", "factorio"),
    (f"xvfb-run -a -s '-screen 0 1280x720x24' {FBIN} --config c.ini", "factorio"),
    (f"nohup {FBIN} --disable-audio > /dev/null 2>&1 &", "factorio"),
    ("timeout 60 ~/factorio/bin/x64/factorio --version", "factorio"),
    (f"bash -c '{FBIN} --version'", "factorio"),
    # launch.sh, or the path only mentioned
    ("bash tools/client/launch.sh --task T06 --worktree /home/lstan/x -- --disable-audio",
     "allow"),
    ("tools/client/launch.sh --recover evidence/T06/client-1-2", "allow"),
    ("tools/client/launch.sh --help", "allow"),
    ("python3 tools/paths.py factorio-bin", "allow"),
    (f"ls -l {FBIN}", "allow"),
    (f"file {FBIN}; readlink -f {FBIN}", "allow"),
    ("[ -x \"$(python3 tools/paths.py factorio-bin)\" ] && echo present", "allow"),
    ("grep -rn 'bin/x64/factorio' tools/", "allow"),
    ("git commit -m \"Factorio only via launch.sh, never bin/x64/factorio\"", "allow"),

    # ---- nesting (fix 6): read to MAX_DEPTH, refused past it, never a crash
    ("echo " + "$(" * 20 + "pkill x" + ")" * 20, "pkill"),
    ("echo " + "$(" * 20 + "ls" + ")" * 20, "allow"),
    ("echo " + "$(" * 400 + "ls" + ")" * 400, "deep"),
    ("echo " + "$(" * 400, "deep"),                             # never closed
    ("echo " + "<(" * 400 + "ls" + ")" * 400, "deep"),
    ("echo " + "(" * 400 + "ls" + ")" * 400, "allow"),          # plain parens: no nesting read
    ("echo " + "${" * 400, "allow"),

    # ---- ordinary work
    ("git status --short && git log --oneline -3", "allow"),
    ("python3 tools/check-recipes.py", "allow"),
    ("luacheck . --formatter plain | tail -20", "allow"),
    (f"tools/blender/render.sh --model m.blend --out {SP}/artist/T03/render", "allow"),
    (f"cat {SP}/artist/T03/render/render.done", "allow"),
    ("", "allow"),
]


def run(payload):
    p = subprocess.run([sys.executable, HOOK], input=payload, capture_output=True,
                       text=True, timeout=20)
    return p.returncode, p.stderr.strip()


def verdict(code, err):
    if code == 0:
        return "allow"
    if code != 2:
        return f"exit {code}"
    msg = err.split(": ", 1)[1] if ": " in err else err
    for name, sign in SIGNS.items():
        if sign and msg.startswith(sign):
            return name
    if msg.startswith(("`pkill` stops", "`killall` stops")):
        return "pkill"
    return "block (unknown message)"


def bash(command, tool="Bash"):
    return json.dumps({
        "session_id": "f78b89ed-2ad6-4f84-8939-62aaf5301072",
        "transcript_path": "/home/lstan/.claude/projects/x/f78b89ed.jsonl",
        "cwd": ROOT,
        "permission_mode": "default",
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": {"command": command, "description": "test"},
    })


def label_of(command):
    return command if len(command) <= 200 else command[:90] + " ... " + command[-40:]


def main():
    verbose = "-v" in sys.argv[1:]
    failed = []
    cases = [(label_of(c), want, bash(c)) for c, want in TABLE]
    cases += [
        ("(a Read tool call)", "allow", bash("rm -rf /tmp", tool="Read")),
        ("(not JSON)", "allow", "not json {"),
        ("(no tool_input)", "allow", json.dumps({"tool_name": "Bash"})),
    ]
    for label, want, payload in cases:
        code, err = run(payload)
        got = verdict(code, err)
        ok = got == want
        if not ok:
            failed.append(label)
        if verbose or not ok:
            print(f"{'ok  ' if ok else 'FAIL'} {want:8} got {got:8} {label!r}")
            if not ok and err:
                print(f"       stderr: {err}")
    print(f"{'FAIL' if failed else 'PASS'}: {len(cases) - len(failed)} of {len(cases)} rows "
          "as listed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
