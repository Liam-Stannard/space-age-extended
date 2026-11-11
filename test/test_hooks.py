#!/usr/bin/env python3
"""The Bash hook, .claude/hooks/no-ghost-waits.py, against a table of commands.

  python3 test/test_hooks.py [-v]

Each row is a Bash command and what the hook must do with it: "allow" (exit 0) or one of the
four blocks (exit 2, its message on stderr): "loop" (a while/until loop with sleep in it),
"scratch" (a recursive delete above scratchpad/<role>/<ticket> under /tmp), "pkill"
(pkill/killall) or "factorio" (the game binary run directly). The command goes to the hook as
the PreToolUse JSON Claude Code sends, with cwd the repo root; nothing in it is run. The block
is told apart by the start of its message. -v prints every row, not only the failures.

Exits 0 when every row comes out as listed, 1 naming those that do not.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, ".claude", "hooks", "no-ghost-waits.py")

SP = "/tmp/claude-1000/-home-lstan-data-git-space-age-extended/f78b89ed-2ad6-4f84-8939-62aaf5301072/scratchpad"
OTHER_SP = "/tmp/claude-1000/-home-lstan-data-git-space-age-extended/0a1b2c3d-0000-4000-8000-000000000000/scratchpad"
FBIN = "/mnt/data/SteamLibrary/steamapps/common/Factorio/bin/x64/factorio"
LOG = SP + "/artist/drop-crusher-T03/render/render.log"

# What each block's message starts with, after "Blocked by .claude/hooks/no-ghost-waits.py: ".
SIGNS = {
    "loop": "a while/until loop with `sleep`",
    "scratch": "this deletes",
    "pkill": None,                      # "`pkill` stops ..." or "`killall` stops ..."
    "factorio": "this runs the Factorio binary",
}

TABLE = [
    # ---- the acceptance line
    (f'until grep -q "^exit" {LOG}; do sleep 30; done', "loop"),
    (f"find {SP} -mindepth 1 -maxdepth 1 ! -name artist-render -exec rm -rf {{}} +", "scratch"),
    ("tools/client/launch.sh --task T04 -- --disable-audio", "allow"),
    ("tools/check-data-stage.sh", "allow"),
    ("timeout 600 tail --pid=1 -f /dev/null", "allow"),

    # ---- loops: a while/until with sleep anywhere inside it
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
    # not polling
    ("while read -r f; do echo \"$f\"; done < list.txt", "allow"),
    ("while IFS= read -r line; do printf '%s\\n' \"$line\"; done <<'EOF'\na\nb\nEOF", "allow"),
    ("x=0; while [ $x -lt 3 ]; do x=$((x+1)); done", "allow"),
    ("while true; do break; done; sleep 5", "allow"),         # the sleep is after the loop
    ("sleep 2", "allow"),
    ("echo sleep | while read c; do echo \"$c\"; done", "allow"),
    ("while true; do sleeper; done", "allow"),
    ("for i in 1 2 3; do sleep 1; done", "allow"),            # a for loop is not checked
    ("echo \"while true; do sleep 1; done\"", "allow"),
    ("grep -n 'until grep -q' .claude/hooks/no-ghost-waits.py", "allow"),
    ("git commit -m \"Ban while/until loops with sleep in them\"", "allow"),
    ("cat > notes.txt <<'EOF'\nwhile true; do sleep 1; done\nEOF", "allow"),
    ("git commit -m \"$(cat <<'EOF'\nHook: no `while true; do sleep 1; done`, don't pkill.\n"
     "rm -rf /tmp is refused too (it's shared).\nEOF\n)\"", "allow"),
    ("# while true; do sleep 1; done\nls", "allow"),

    # ---- scratch deletes
    (f"rm -rf {SP}/coder/agent-setup-T04", "allow"),
    (f"rm -r {SP}/coder/agent-setup-T04/", "allow"),
    (f"rm -rf {SP}/coder/agent-setup-T04/*", "allow"),
    (f"rm -rf {SP}/coder/agent-setup-T04/renders/take-*", "allow"),
    (f"rm -rf {SP}/coder/agent-setup-T04 {SP}/coder/agent-setup-T05", "allow"),
    (f"rm -rf {OTHER_SP}/tester/T06", "allow"),
    (f"find {SP}/coder/agent-setup-T04 -name '*.tmp' -delete", "allow"),
    (f"find {SP}/coder/agent-setup-T04 -mindepth 1 -maxdepth 1 -exec rm -rf {{}} +", "allow"),
    (f"S={SP}; rm -rf \"$S/coder/agent-setup-T04\"", "allow"),
    (f"cd {SP}/coder && rm -rf agent-setup-T04", "allow"),
    (f"cd {SP}/coder/agent-setup-T04 && rm -rf *", "allow"),
    (f"find {SP} -maxdepth 2 -type d", "allow"),               # no delete
    (f"rm {SP}/coder/note.txt", "allow"),                       # not recursive
    ("rm -rf build/ evidence/T04", "allow"),                    # in the repo, not /tmp
    ("rm -rf /home/lstan/tmp/old", "allow"),
    ("rm -rf ~/scratch-old", "allow"),
    ("find . -name '__pycache__' -exec rm -rf {} +", "allow"),
    ("rm -rf \"$RUN_DIR\"", "allow"),                          # unknown variable: fail-open
    ("echo rm -rf /tmp", "allow"),
    ("git commit -m \"never rm -rf /tmp or find -delete the scratchpad\"", "allow"),
    ("grep -rn 'rm -rf' tools/", "allow"),
    (f"ls {SP} && du -sh {SP}/*", "allow"),
    # refused
    (f"rm -rf {SP}", "scratch"),
    (f"rm -rf {SP}/", "scratch"),
    (f"rm -rf {SP}/*", "scratch"),
    (f"rm -rf {SP}/coder", "scratch"),
    (f"rm -rf {SP}/coder/*", "scratch"),
    (f"rm -rf {SP}/coder/agent-*", "scratch"),
    (f"rm -rf {SP}/*/agent-setup-T04", "scratch"),
    (f"rm -rf {SP}/{{coder,artist}}", "scratch"),
    (f"rm -rf {SP}/coder/agent-setup-T04/../..", "scratch"),
    (f"rm -rf {SP}/coder/agent-setup-T04 {SP}", "scratch"),    # one bad target is enough
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
    ("rm -rf /tmp/claude-1000/-home-lstan-data-git-space-age-extended", "scratch"),
    ("rm -rf /tmp/claude-1000/-home-lstan-data-git-space-age-extended/f78b89ed-2ad6-4f84-8939-62aaf5301072", "scratch"),
    ("rm -rf /tmp/sae-old-render", "scratch"),                 # /tmp, not a scratchpad
    ("rm -rf /*", "scratch"),
    (f"S={SP}; rm -rf \"$S\"/*", "scratch"),
    (f"S={SP}; rm -rf \"${{S}}\"", "scratch"),
    (f"export S={SP} && rm -rf $S/*", "scratch"),
    (f"S={SP}; rm -rf \"$S/coder/$T\"", "scratch"),            # $T unset: that is $S/coder/
    ("rm -rf \"$S\"/*", "scratch"),                            # $S unset here: that is /*
    (f"cd {SP} && rm -rf *", "scratch"),
    (f"cd {SP} && find . -mindepth 1 -delete", "scratch"),
    (f"cd {SP}/coder/agent-setup-T04 && rm -rf ../../*", "scratch"),
    (f"find {SP} -name '*.png' -delete", "scratch"),
    (f"find {SP}/coder -mindepth 1 -maxdepth 1 -exec rm -rf {{}} +", "scratch"),
    (f"find {SP} -type d -execdir rm -r {{}} \\;", "scratch"),
    ("find /tmp -maxdepth 1 -name 'sae-*' -exec rm -rf {} +", "scratch"),
    (f"find -L {SP} -mindepth 1 -maxdepth 1 -print0 | xargs -0 rm -rf", "scratch"),
    (f"bash -c 'rm -rf {SP}/*'", "scratch"),
    (f"x=$(rm -rf {SP})", "scratch"),
    (f"for d in {SP}/*; do rm -rf \"$d\"; done", "scratch"),
    (f"for d in {SP}/coder/T04 {SP}; do rm -rf $d; done", "scratch"),
    (f"trap 'rm -rf {SP}/coder' EXIT; ls", "scratch"),
    # the same, allowed
    (f"for d in {SP}/coder/T04/take-1 {SP}/coder/T04/take-2; do rm -rf \"$d\"; done", "allow"),
    (f"trap 'rm -rf {SP}/coder/agent-setup-T04/run' EXIT; ls", "allow"),
    (f"rm -rf {SP}/coder/agent-setup-T04 2>/dev/null; ls {SP}", "allow"),

    # ---- pkill / killall
    ("pkill -f blender", "pkill"),
    ("killall factorio", "pkill"),
    ("killall -9 Xvfb", "pkill"),
    ("sudo pkill -TERM -x factorio", "pkill"),
    ("/usr/bin/pkill Xvfb", "pkill"),
    ("ls; pkill -9 Xvfb", "pkill"),
    ("timeout 5 pkill blender || true", "pkill"),
    ("bash -c \"pkill -f render.sh\"", "pkill"),
    ("n=$(pkill -c -f blender)", "pkill"),
    ("pgrep -f blender | xargs pkill -P", "pkill"),
    # by PID, or the word only mentioned
    ("kill 12345", "allow"),
    ("kill -TERM 12345 12346 && wait 12345", "allow"),
    ("pgrep -a -x factorio", "allow"),
    ("grep -n pkill .claude/hooks/no-ghost-waits.py", "allow"),
    ("man pkill", "allow"),
    ("command -v pkill killall", "allow"),
    ("echo 'do not pkill'", "allow"),
    ("git commit -m \"hook: block pkill and killall\"", "allow"),

    # ---- the Factorio binary
    (f"{FBIN} --version", "factorio"),
    (f"\"{FBIN}\" --dump-data", "factorio"),
    ("\"$(python3 tools/paths.py factorio-bin)\" --version", "factorio"),
    ("G=$(python3 tools/paths.py factorio-bin); \"$G\" --dump-data", "factorio"),
    ("source tools/paths.sh && sae_factorio_bin G && \"$G\" --version", "factorio"),
    ("cd /mnt/data/SteamLibrary/steamapps/common/Factorio && bin/x64/factorio --start-server s.zip", "factorio"),
    ("cd /mnt/data/SteamLibrary/steamapps/common/Factorio/bin/x64 && ./factorio --version", "factorio"),
    ("R=/mnt/data/SteamLibrary/steamapps/common/Factorio; $R/bin/x64/factorio --version", "factorio"),
    ("env -u WAYLAND_DISPLAY \"$ROOT/bin/x64/factorio\" --disable-audio", "factorio"),
    (f"xvfb-run -a -s '-screen 0 1280x720x24' {FBIN} --config c.ini", "factorio"),
    (f"nohup {FBIN} --disable-audio > /dev/null 2>&1 &", "factorio"),
    ("timeout 60 ~/factorio/bin/x64/factorio --version", "factorio"),
    (f"bash -c '{FBIN} --version'", "factorio"),
    # launch.sh, or the path only mentioned
    ("bash tools/client/launch.sh --task T06 --worktree /home/lstan/x -- --disable-audio", "allow"),
    ("tools/client/launch.sh --recover evidence/T06/client-1-2", "allow"),
    ("tools/client/launch.sh --help", "allow"),
    ("python3 tools/paths.py factorio-bin", "allow"),
    (f"ls -l {FBIN}", "allow"),
    (f"file {FBIN}; readlink -f {FBIN}", "allow"),
    ("[ -x \"$(python3 tools/paths.py factorio-bin)\" ] && echo present", "allow"),
    ("grep -rn 'bin/x64/factorio' tools/", "allow"),
    ("git commit -m \"Factorio only via launch.sh, never bin/x64/factorio\"", "allow"),

    # ---- ordinary work
    ("git status --short && git log --oneline -3", "allow"),
    ("python3 tools/check-recipes.py", "allow"),
    ("luacheck . --formatter plain | tail -20", "allow"),
    ("tools/blender/render.sh --model m.blend --out " + SP + "/artist/T03/render", "allow"),
    ("cat " + SP + "/artist/T03/render/render.done", "allow"),
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


def main():
    verbose = "-v" in sys.argv[1:]
    failed = []
    cases = [(c, want, bash(c)) for c, want in TABLE]
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
    print(f"{'FAIL' if failed else 'PASS'}: {len(cases) - len(failed)} of {len(cases)} rows as listed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
