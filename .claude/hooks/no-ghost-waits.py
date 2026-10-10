#!/usr/bin/env python3
"""PreToolUse hook on Bash: no unbounded or duplicate polling loops, and no
deleting across a shared scratch root.

On 2026-10-10 an artist left 18 background loops of the form
`until grep -q "^exit" <log>; do sleep 30; done` running: it started a new one
about every ten minutes and never stopped the old ones, and one more polled a
folder that had been deleted, so it could never end. This refuses the two
shapes that produce a ghost:

  - a polling loop (`until` or `while` with a `sleep` in it) not bounded by
    `timeout <seconds>` of at most an hour;
  - a polling loop identical to one that is already running.

`while read` loops with no sleep are not polling and pass.

**The scratch guard.** Later the same day an agent told to clear its own
superseded scratch ran `find <scratchpad> -mindepth 1 -maxdepth 1 ! -name
<its folder> -exec rm -rf {} +` and deleted every other agent's scratch,
including a render that was still running. So a command is refused if it
deletes (`rm -r`, `find ... -delete` or `-exec rm`) a scratch root itself or
everything in it: the session scratchpad (/tmp/claude-<uid>/<project>/<session>/scratchpad),
/tmp/claude-<uid> and /tmp. Naming folders inside the root is allowed.
Shell variables assigned in the same command are expanded first, so
`S=<scratchpad>; rm -rf "$S"/*` is caught too.

Exit 2 blocks the command and hands the message on stderr back to the agent.
"""
import json
import re
import subprocess
import sys

MAX_SECONDS = 3600

ADVICE = (
    "Instead: run the job itself (render.sh, the game client) with the Bash "
    "tool's run_in_background, and the harness tells you when it exits -- no "
    "loop needed. render.sh writes <out-dir>/render.done ('exit <code>') when "
    "it ends. If a wait is truly needed, use ONE loop at a time, wrapped in "
    "`timeout <seconds>` (at most 3600), watching the job's PID, and stop it "
    "when you are done."
)


def block(reason):
    print(f"Blocked by .claude/hooks/no-ghost-waits.py: {reason}\n{ADVICE}", file=sys.stderr)
    sys.exit(2)


ROOT = r"(?:/tmp/claude-\d+/[^/\s'\"]+/[^/\s'\"]+/scratchpad|/tmp/claude-\d+|/tmp)"
# The root itself, or a glob of everything in it, as a whole word.
ROOT_TARGET = re.compile(ROOT + r"/?\*?(?=[\s'\";)|&]|$)")


def expand_vars(cmd):
    """Substitute VAR=value assignments made in the command itself."""
    assigns = dict((m.group(1), m.group(3)) for m in
                   re.finditer(r"\b([A-Za-z_]\w*)=(['\"]?)([^\s;'\"]+)\2", cmd))
    for name, value in assigns.items():
        cmd = re.sub(r'"?\$\{?' + name + r'(?!\w)\}?"?', value, cmd)
    return cmd


def deletes_a_root(cmd):
    text = expand_vars(cmd)
    for seg in re.split(r"[;&|]+|\n", text):
        seg = seg.strip()
        rm = re.match(r"(?:sudo\s+)?rm\s+(.*)", seg)
        if rm and re.search(r"(?:^|\s)-\w*[rR]", rm.group(1)) and ROOT_TARGET.search(rm.group(1)):
            return True
        fd = re.match(r"find\s+(\S+)(.*)", seg)
        if fd and re.search(r"-delete\b|-exec\s+rm\b|-execdir\s+rm\b", fd.group(2)) \
                and re.fullmatch(ROOT + r"/?", fd.group(1).strip("'\"")):
            return True
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    if data.get("tool_name") != "Bash":
        return
    cmd = (data.get("tool_input") or {}).get("command") or ""

    if deletes_a_root(cmd):
        print("Blocked by .claude/hooks/no-ghost-waits.py: this deletes a shared "
              "scratch root (the session scratchpad, /tmp/claude-<uid> or /tmp) or "
              "everything in it. Other agents work there. Delete only folders you "
              "created yourself, each by its exact path.", file=sys.stderr)
        sys.exit(2)

    loop = re.search(r"\b(until|while)\b(?!\s+(IFS=\S*\s+)?read\b)", cmd)
    if not loop or not re.search(r"\bsleep\b", cmd[loop.start():]):
        return

    bounds = [int(n) for n in re.findall(r"\btimeout\s+(?:-\S+\s+)*(\d+)s?\b", cmd)]
    if not bounds:
        block("a polling loop with no `timeout` around it can run forever.")
    if min(bounds) > MAX_SECONDS:
        block(f"timeout {min(bounds)} is over the {MAX_SECONDS} s limit.")

    # The loop text as it would appear in a running shell's command line.
    # Cut at the loop's own `done` and before any closing quote, which the
    # running shell's args do not carry.
    body = cmd[loop.start():]
    end = re.search(r"\bdone\b", body)
    body = body[:end.end()] if end else body
    key = re.sub(r"\s+", " ", body[:120]).strip().strip("'\"")
    try:
        ps = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.SubprocessError):
        return
    running = [line for line in ps.splitlines()
               if key in re.sub(r"\s+", " ", line) and "no-ghost-waits" not in line]
    if running:
        block("an identical polling loop is already running; wait on that one, "
              "or stop it before starting another.")


if __name__ == "__main__":
    main()
