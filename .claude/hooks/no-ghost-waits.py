#!/usr/bin/env python3
"""PreToolUse hook on Bash: the four rules agents have broken before.

  1. No polling loops: a `while` or `until` loop with `sleep` inside it.
  2. No deleting across shared scratch: `rm -r`, `find ... -delete` and
     `find ... -exec rm` under /tmp only two or more levels below a session
     scratchpad (scratchpad/<role>/<ticket>), never above that.
  3. No `pkill` or `killall`.
  4. No running the Factorio binary (any `.../bin/x64/factorio`, which is
     what `tools/paths.py factorio-bin` prints) except through
     tools/client/launch.sh.

**Why.** On 2026-10-10 an artist left 18 background loops of the form
`until grep -q "^exit" <log>; do sleep 30; done` running: it started a new one
about every ten minutes and never stopped the old ones, and one more polled a
folder that had been deleted, so it could never end. This hook used to allow
such a loop inside `timeout <= 3600` and refuse a duplicate of one already
running (a `ps` check); since 2026-11-11 (Liam: "Ban them") every while/until
loop with a sleep in it is refused, and the `ps` check is gone. A `while read`
loop with no sleep is not polling and passes; a `for` loop is not checked.

Later the same day an agent told to clear its own superseded scratch ran
`find <scratchpad> -mindepth 1 -maxdepth 1 ! -name <its folder> -exec rm -rf
{} +` and deleted every other agent's scratch, including a render that was
still running. Scratch is laid out scratchpad/<role>/<ticket>/, so a
recursive delete under /tmp is allowed only on a path at least two levels
below a session scratchpad (/tmp/claude-<uid>/<project>/<session>/scratchpad),
every level down to the second spelled out (no glob, no unset variable). The
scratchpad itself, a role folder, /tmp/claude-<uid>, /tmp and anything else
under /tmp are refused. Deletes outside /tmp are not this hook's business.
Shell variables assigned in the same command are expanded first, so
`S=<scratchpad>; rm -rf "$S"/*` is caught, and `cd` is followed, so
`cd <scratchpad> && rm -rf *` is too.

pkill/killall (Liam 2026-11-11, "No pkill/killall") stop every process
matching a name: other agents' renders and clients, Liam's own game. And the
game client is started only by launch.sh (Liam 2026-11-11, "Factorio only via
launch.sh"), which keeps it off Liam's display and speakers. The hook sees only
the Bash command's text, so a script that runs the binary inside it
(launch.sh, check-data-stage.sh) is never seen and passes.

**How it reads a command.** The text is tokenised as the shell would: quotes,
escapes, `$(...)`, backticks, heredocs and comments. Only a word in command
position counts, so `grep -n pkill file`, `echo "while true; do sleep 1;
done"`, a commit message (quoted or in a heredoc) and `ls .../bin/x64/factorio`
all pass. Command substitutions and `bash -c`/`sh -c`/`eval`/`trap` strings
are read as commands. Wrappers (sudo, env, timeout, nohup, setsid, xargs,
xvfb-run, nice, stdbuf, ...) are looked through to the command they run. A
`for NAME in ...` variable stands for the riskiest word in its list, so
`for d in <scratchpad>/*; do rm -rf "$d"; done` is caught, and
`find <root> ... | xargs rm` is read as a delete of <root>. Not seen: a
script file's contents, a shell function's body where it is called, a
`python3 -c` string.

**Fail-open or closed.** A hook error never blocks: bad JSON passes, and an
internal error exits 1 (Claude Code shows the message and runs the command).
Rules 1, 3 and 4 need nothing outside the command text. In rule 2 a target
the hook cannot place passes (a path starting with a variable it cannot
resolve, a relative path after a `cd` it cannot resolve), but an unresolved
variable or glob at or above the second level under /tmp is refused, and so
is an unresolved variable followed directly by a glob (`"$X"/*`: with X unset
that is `rm -rf /*`).

Exit 2 blocks the command and hands the message on stderr back to the agent.
"""
import fnmatch
import json
import posixpath
import re
import sys

HOOK = ".claude/hooks/no-ghost-waits.py"
UNK = "\x00"            # stands for text the hook cannot know (an unset variable, $(...))
GLOB = set("*?[{") | {UNK}
MAX_DEPTH = 12          # nested $(...) / bash -c levels read

MSG_LOOP = (
    "a while/until loop with `sleep` in it is a polling loop, and polling loops are banned. "
    "Instead: start the job itself (render.sh, launch.sh, a server) with the Bash tool's "
    "run_in_background; the harness tells you when it exits, no loop needed. To wait for a "
    "process you did not start, `timeout <seconds> tail --pid=<pid> -f /dev/null` (at most "
    "3600 s). render.sh writes <out-dir>/render.done ('exit <code>') when it ends."
)
MSG_SCRATCH = (
    "this deletes {what}. Under /tmp only a folder two or more levels below the session "
    "scratchpad may be deleted (scratchpad/<role>/<ticket>, or deeper), every level down to "
    "that one spelled out: no glob and no variable this command does not set. Never the "
    "scratchpad, a role folder, /tmp/claude-<uid>, /tmp or anything else in /tmp: other agents "
    "work there. Instead: delete the folder you created yourself by its exact path, e.g. "
    "`rm -r <scratchpad>/<role>/<ticket>`."
)
MSG_PKILL = (
    "`{name}` stops every process matching a name, including other agents' jobs and Liam's "
    "game. Instead: stop the processes you started by PID, `kill <pid>` (the PID "
    "run_in_background gave you; launch.sh lists its own in <run>/pids.txt and stops them "
    "itself, or `tools/client/launch.sh --recover <run>`)."
)
MSG_FACTORIO = (
    "this runs the Factorio binary directly ({path}). Instead: start a client only with "
    "`tools/client/launch.sh --task <name> ...` (headless, private display, no sound, stopped "
    "when it ends; see its --help), and check the data stage with tools/check-data-stage.sh."
)


class Blocked(Exception):
    pass


# --------------------------------------------------------------------------- tokens
# A word is a list of parts: ("lit", text, quoted), ("var", name), ("cmd", tokens, raw).
# A token is ("word", parts), ("op", text) or ("redir", text).

OPS = ("&&", "||", ";;", "|&", ";", "&", "|", "(", ")", "\n")
REDIR = re.compile(r"(?:\d+|&)?(?:<<<|<<-|<<|>>|>&|<&|<>|>\||>|<)")
META = set(" \t\n;&|()<>")


def skip_heredocs(text, i, pending):
    """i is just past a newline: skip each pending heredoc body."""
    for delim, strip_tabs in pending:
        while i < len(text):
            j = text.find("\n", i)
            line = text[i:] if j < 0 else text[i:j]
            i = len(text) if j < 0 else j + 1
            if (line.lstrip("\t") if strip_tabs else line) == delim:
                break
    pending.clear()
    return i


def tokenize(text, i=0, close=False):
    """Tokens of text from i; with close, stop at the `)` closing a `$(`. Never raises."""
    toks, pending, depth, n = [], [], 0, len(text)
    while i < n:
        c = text[i]
        if c in " \t":
            i += 1
        elif c == "\\" and text.startswith("\n", i + 1):
            i += 2
        elif c == "#":
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif c == "\n":
            toks.append(("op", "\n"))
            i = skip_heredocs(text, i + 1, pending)
        elif c in "<>" and text.startswith("(", i + 1):        # process substitution
            sub, i = tokenize(text, i + 2, close=True)
            toks.append(("word", [("cmd", sub, "")]))
        else:
            m = REDIR.match(text, i)
            if m:
                op = re.sub(r"^[\d&]+", "", m.group(0))
                i = m.end()
                toks.append(("redir", op))
                if op in ("<<", "<<-"):
                    while i < n and text[i] in " \t":
                        i += 1
                    parts, i = read_word(text, i)
                    pending.append(("".join(p[1] for p in parts if p[0] == "lit"), op == "<<-"))
                continue
            op = next((o for o in OPS if text.startswith(o, i)), None)
            if op:
                if op == "(":
                    depth += 1
                elif op == ")":
                    if close and depth == 0:
                        return toks, i + 1
                    depth -= 1
                toks.append(("op", op))
                i += len(op)
                continue
            parts, i = read_word(text, i)
            toks.append(("word", parts))
    return toks, i


def read_dollar(text, i):
    """text[i] is '$'; the part it starts and the index after it."""
    if text.startswith("$((", i):
        depth, j = 0, i + 1
        while j < len(text):
            depth += {"(": 1, ")": -1}.get(text[j], 0)
            j += 1
            if depth == 0:
                break
        return ("lit", UNK, True), j
    if text.startswith("$(", i):
        start = i + 2
        sub, j = tokenize(text, start, close=True)
        return ("cmd", sub, text[start:j - 1]), j
    if text.startswith("${", i):
        j = text.find("}", i)
        j = len(text) if j < 0 else j
        m = re.match(r"[A-Za-z_]\w*", text[i + 2:j])
        return ("var", m.group(0) if m else "?"), j + 1
    m = re.match(r"[A-Za-z_]\w*|[0-9@*#?$!-]", text[i + 1:])
    if m:
        return ("var", m.group(0)), i + 1 + m.end()
    return ("lit", "$", False), i + 1


def read_backtick(text, i):
    j, raw = i + 1, []
    while j < len(text) and text[j] != "`":
        if text[j] == "\\" and j + 1 < len(text):
            raw.append(text[j + 1])
            j += 2
            continue
        raw.append(text[j])
        j += 1
    inner = "".join(raw)
    return ("cmd", tokenize(inner)[0], inner), j + 1


def read_word(text, i):
    parts, n = [], len(text)
    while i < n and text[i] not in META:
        c = text[i]
        if c == "\\":
            if text.startswith("\n", i + 1):
                i += 2
                continue
            parts.append(("lit", text[i + 1:i + 2], True))
            i += 2
        elif c == "'":
            j = text.find("'", i + 1)
            j = n if j < 0 else j
            parts.append(("lit", text[i + 1:j], True))
            i = j + 1
        elif c == "$" and text.startswith("$'", i):
            j = i + 2
            while j < n and text[j] != "'":
                j += 2 if text[j] == "\\" else 1
            parts.append(("lit", text[i + 2:j], True))
            i = j + 1
        elif c == '"':
            i += 1
            while i < n and text[i] != '"':
                if text[i] == "\\" and i + 1 < n:
                    if text[i + 1] == "\n":
                        i += 2
                        continue
                    keep = text[i + 1] in '$`"\\'
                    parts.append(("lit", text[i + 1] if keep else text[i:i + 2], True))
                    i += 2
                elif text[i] == "$":
                    part, i = read_dollar(text, i)
                    parts.append(part if part[0] != "lit" else ("lit", part[1], True))
                elif text[i] == "`":
                    part, i = read_backtick(text, i)
                    parts.append(part)
                else:
                    j = i
                    while j < n and text[j] not in '"\\$`':
                        j += 1
                    parts.append(("lit", text[i:j], True))
                    i = j
            i += 1
        elif c == "$":
            part, i = read_dollar(text, i)
            parts.append(part)
        elif c == "`":
            part, i = read_backtick(text, i)
            parts.append(part)
        else:
            j = i
            while j < n and text[j] not in META and text[j] not in "\\'\"$`":
                j += 1
            parts.append(("lit", text[i:j], False))
            i = j
    return parts, i


# --------------------------------------------------------------------------- words
class Value:
    """A word as far as the hook can know it: text with UNK where it cannot, and the
    raw text of every command substitution it holds."""

    def __init__(self, text, subs):
        self.text, self.subs = text, subs

    @property
    def known(self):
        return UNK not in self.text


def evaluate(parts, env):
    text, subs = [], []
    for p in parts:
        if p[0] == "lit":
            text.append(p[1])
        elif p[0] == "var":
            v = env.get(p[1])
            text.append(v.text if v else UNK)
            subs.extend(v.subs if v else [])
        else:
            text.append(UNK)
            subs.append(p[2])
    return Value("".join(text), subs)


def plain(parts):
    """The word's text if it is one unquoted literal (a reserved word can only be that)."""
    return parts[0][1] if len(parts) == 1 and parts[0][0] == "lit" and not parts[0][2] else None


ASSIGN = re.compile(r"([A-Za-z_]\w*)\+?=")


def assignment(parts):
    if parts and parts[0][0] == "lit" and not parts[0][2]:
        m = ASSIGN.match(parts[0][1])
        if m:
            return m.group(1), [("lit", parts[0][1][m.end():], False)] + parts[1:]
    return None


# --------------------------------------------------------------------------- checks
class Ctx:
    def __init__(self, cwd, depth=0):
        self.env, self.cwd, self.depth = {}, cwd, depth
        self.loops = []         # open loops, innermost last: [keyword, has_sleep]
        self.sleep = False      # a sleep was run anywhere in this text
        self.pipe_find = None   # the start points of a find earlier in this pipeline


def mark_sleep(ctx):
    ctx.sleep = True
    for frame in ctx.loops:
        frame[1] = True


def check_text(text, ctx):
    """Read text as commands in a child context; carry its sleep up into ctx's loops."""
    if ctx.depth >= MAX_DEPTH:
        return
    child = Ctx(ctx.cwd, ctx.depth + 1)
    child.env = dict(ctx.env)
    walk(tokenize(text)[0], child)
    if child.sleep:
        mark_sleep(ctx)


def check_tokens(toks, ctx):
    if ctx.depth >= MAX_DEPTH:
        return
    child = Ctx(ctx.cwd, ctx.depth + 1)
    child.env = dict(ctx.env)
    walk(toks, child)
    if child.sleep:
        mark_sleep(ctx)


def subs_of(parts, ctx):
    for p in parts:
        if p[0] == "cmd":
            check_tokens(p[1], ctx)


KEYWORD_THEN_COMMAND = {"do", "then", "else", "elif", "if", "{", "}", "!", "time", "fi", "esac"}


def walk(toks, ctx):
    words, skip_next, for_header = [], False, None
    for tok in toks:
        kind = tok[0]
        if kind == "redir":
            skip_next = True
            continue
        if kind == "word":
            parts = tok[1]
            subs_of(parts, ctx)
            if skip_next:
                skip_next = False
                continue
            if for_header is not None:
                if plain(parts) == "do":
                    bind_for(for_header, ctx)
                    for_header = None
                else:
                    for_header.append(parts)
                continue
            word = plain(parts) if not words else None
            if word in ("while", "until"):
                ctx.loops.append([word, False])
            elif word in ("for", "select"):
                ctx.loops.append([word, False])
                for_header = []
            elif word == "done":
                if ctx.loops:
                    frame = ctx.loops.pop()
                    if frame[0] in ("while", "until") and frame[1]:
                        raise Blocked(MSG_LOOP)
            elif word in KEYWORD_THEN_COMMAND:
                pass
            else:
                words.append(parts)
            continue
        # an operator ends the simple command
        op, skip_next = tok[1], False
        if for_header is not None and op in (";", "\n"):
            continue            # `for x in a b; do`: the header runs to `do`
        simple(words, ctx, piped=op in ("|", "|&"))
        words = []
        if op not in ("|", "|&"):
            ctx.pipe_find = None
    simple(words, ctx, piped=False)
    if any(f[0] in ("while", "until") and f[1] for f in ctx.loops):
        raise Blocked(MSG_LOOP)     # a loop with no `done` yet, a sleep in it


def bind_for(header, ctx):
    """`for NAME in WORD...`: NAME takes the word a delete of it would refuse, if one
    would (`for d in <scratchpad>/*; do rm -rf "$d"; done`), else the first word."""
    if not header or plain(header[0]) is None:
        return
    name, items = plain(header[0]), header[1:]
    items = items[1:] if items and plain(items[0]) == "in" else []
    vals = [evaluate(w, ctx.env) for w in items]
    chosen = vals[0] if vals else Value(UNK, [])
    for v in vals:
        try:
            check_target(v.text, ctx)
        except Blocked:
            chosen = v
            break
    ctx.env[name] = chosen


WRAP_VALUE_OPTS = {
    "sudo": {"-u", "-g", "-C", "-D", "-h", "-p", "-r", "-t", "-U", "-T"},
    "env": {"-u", "-C", "-S", "--unset", "--chdir", "--split-string"},
    "timeout": {"-s", "-k", "--signal", "--kill-after"},
    "nice": {"-n", "--adjustment"},
    "ionice": {"-c", "-n", "-p", "--class", "--classdata"},
    "stdbuf": {"-i", "-o", "-e", "--input", "--output", "--error"},
    "xargs": {"-a", "-d", "-E", "-e", "-I", "-i", "-L", "-l", "-n", "-P", "-s",
              "--arg-file", "--delimiter", "--max-args", "--max-procs", "--max-chars",
              "--process-slot-var", "--replace", "--max-lines", "--eof"},
    "xvfb-run": {"-n", "-s", "-e", "-f", "-p", "-w", "--server-num", "--server-args",
                 "--error-file", "--auth-file", "--xauth-protocol", "--wait"},
    "setsid": set(), "nohup": set(), "exec": {"-a"}, "command": set(), "builtin": set(),
    "time": {"-f", "-o", "--format", "--output"}, "chrt": set(), "taskset": set(),
    "strace": {"-e", "-o", "-p", "-s", "-u"}, "ltrace": {"-e", "-o", "-p", "-s", "-u"},
    "flock": {"-w", "-E", "-c", "--timeout", "--conflict-exit-code"},
    "unbuffer": set(), "doas": {"-u", "-C"}, "catchsegv": set(),
}
SHELLS = {"bash", "sh", "zsh", "dash", "ksh", "fish"}
DECLARE = {"export", "local", "declare", "typeset", "readonly"}


def unwrap(vals):
    """Index of the word actually run, looking through wrappers, and whether xargs feeds
    it; len(vals) when nothing is run (`command -v pkill` only looks a name up)."""
    i, via_xargs = 0, False
    while i < len(vals):
        name = posixpath.basename(vals[i].text)
        if name not in WRAP_VALUE_OPTS:
            return i, via_xargs
        via_xargs |= name == "xargs"
        takes = WRAP_VALUE_OPTS[name]
        i += 1
        while i < len(vals):
            a = vals[i].text
            if name in ("env", "sudo", "doas") and ASSIGN.match(a):
                i += 1
            elif a == "--":
                i += 1
                break
            elif a.startswith("-") and len(a) > 1:
                if name == "command" and a in ("-v", "-V"):
                    return len(vals), via_xargs
                i += 2 if a in takes else 1
            else:
                break
        if name in ("timeout", "taskset", "flock", "chrt") and i < len(vals):
            i += 1          # timeout's duration, taskset's mask, flock's lock file, chrt's priority
    return i, via_xargs


def simple(words, ctx, piped):
    """One simple command: assignments, then the command and its arguments."""
    while words and assignment(words[0]):
        name, value = assignment(words[0])
        ctx.env[name] = evaluate(value, ctx.env)
        words = words[1:]
    if not words:
        return
    vals = [evaluate(w, ctx.env) for w in words]
    i, via_xargs = unwrap(vals)
    if i >= len(vals):
        return
    cmd, args = vals[i], vals[i + 1:]
    name = posixpath.basename(cmd.text)

    if name in DECLARE:
        for w in words[i + 1:]:
            a = assignment(w)
            if a:
                ctx.env[a[0]] = evaluate(a[1], ctx.env)
        return
    if name in ("cd", "pushd"):
        target = next((a for a in args if not a.text.startswith("-")), None)
        if target is None:
            ctx.cwd = None
        elif target.known and ctx.cwd is not None:
            ctx.cwd = posixpath.normpath(posixpath.join(ctx.cwd, target.text))
        elif target.known and target.text.startswith("/"):
            ctx.cwd = posixpath.normpath(target.text)
        else:
            ctx.cwd = None
        return
    if name == "sae_factorio_bin" and args:     # tools/paths.sh: sets $1 to the binary
        ctx.env[args[0].text] = Value(UNK, ["factorio-bin"])
        return
    if name in SHELLS:
        for k, a in enumerate(args):
            if a.text.startswith("-") and not a.text.startswith("--") and "c" in a.text:
                if k + 1 < len(args):
                    check_text(args[k + 1].text, ctx)
                return
            if not a.text.startswith("-"):
                return              # a script file: not seen
        return
    if name == "eval":
        check_text(" ".join(a.text for a in args), ctx)
        return
    if name == "trap" and args and not args[0].text.startswith("-"):
        check_text(args[0].text, ctx)       # run later, on the signal
        return

    if name in ("pkill", "killall"):
        raise Blocked(MSG_PKILL.format(name=name))
    if name == "sleep":
        mark_sleep(ctx)
    if is_factorio(cmd, ctx):
        shown = cmd.text if cmd.text.strip(UNK) else "the path tools/paths.py factorio-bin prints"
        raise Blocked(MSG_FACTORIO.format(path=shown.replace(UNK, "$?")))
    if name == "rm":
        check_rm(args, ctx, via_xargs)
    elif name == "find":
        check_find(args, ctx, piped)


def is_factorio(cmd, ctx):
    if any("factorio-bin" in s or "factorio_bin" in s for s in cmd.subs):
        return True
    path = cmd.text
    if path.startswith("~"):
        path = "/home/_" + path[1:]
    if cmd.known and not path.startswith("/") and ctx.cwd is not None and "/" in path:
        path = posixpath.join(ctx.cwd, path)
    path = posixpath.normpath(path) if path else path
    return path == "bin/x64/factorio" or path.endswith("/bin/x64/factorio")


def check_rm(args, ctx, via_xargs):
    recursive, targets, opts = False, [], True
    for a in args:
        t = a.text
        if opts and t == "--":
            opts = False
        elif opts and t.startswith("--"):
            recursive |= t == "--recursive"
        elif opts and t.startswith("-") and len(t) > 1:
            recursive |= "r" in t or "R" in t
        else:
            targets.append(t)
    if via_xargs and ctx.pipe_find:
        targets.extend(ctx.pipe_find)           # find <root> | xargs rm: the root is the target
        recursive = True
    if recursive:
        for t in targets:
            check_target(t, ctx)


FIND_EXPR = re.compile(r"^[-(!),]")


def check_find(args, ctx, piped):
    k = 0
    while k < len(args) and (args[k].text in ("-H", "-L", "-P") or args[k].text.startswith(("-O", "-D"))):
        k += 2 if args[k].text == "-D" else 1
    starts = []
    while k < len(args) and not FIND_EXPR.match(args[k].text):
        starts.append(args[k].text)
        k += 1
    starts = starts or ["."]
    expr = [a.text for a in args[k:]]
    deletes = "-delete" in expr
    for j, a in enumerate(expr):
        if a in ("-exec", "-execdir", "-ok", "-okdir"):
            run = expr[j + 1:j + 3]
            if run and run[0] in ("sudo", "command", "env"):
                run = run[1:]
            if run and posixpath.basename(run[0]) == "rm":
                deletes = True
    if deletes:
        for s in starts:
            check_target(s, ctx)
    elif piped:
        ctx.pipe_find = starts


SCRATCH = ("tmp", re.compile(r"claude-\d+\Z"), None, None, "scratchpad", None, None)


def check_target(t, ctx):
    """Refuse a recursive delete of t unless it is outside /tmp or deep enough in scratch."""
    if not t:
        return
    if t.startswith(UNK):
        # A variable this command does not set: where it points is unknown, so the target
        # passes -- unless all that follows it is a glob of everything in it.
        tail = t.lstrip(UNK).lstrip("/")
        if tail and set(tail) <= {"*", UNK}:
            raise Blocked(MSG_SCRATCH.format(
                what="everything in a folder named by a variable this command does not set "
                     "(if it is unset, that is everything in /)"))
        return
    if t.startswith("~"):
        return                                  # home, not /tmp
    if not t.startswith("/"):
        if ctx.cwd is None:
            return                              # after a cd the hook cannot follow
        t = posixpath.join(ctx.cwd, t)
    p = posixpath.normpath(t)
    p = "/" + p.lstrip("/")
    comps = [c for c in p.split("/") if c]
    if not comps:
        return                                  # `/` itself: not this hook's business
    first = comps[0]
    if set(first) & GLOB:
        if not fnmatch.fnmatchcase("tmp", first.replace(UNK, "*")):
            return
        raise Blocked(MSG_SCRATCH.format(what=f"{p.replace(UNK, '$?')}, which takes in /tmp"))
    if first != "tmp":
        return                                  # outside /tmp
    for level, want in enumerate(SCRATCH):
        if level >= len(comps):
            raise Blocked(MSG_SCRATCH.format(what=what_is(comps)))
        c = comps[level]
        if set(c) & GLOB:
            raise Blocked(MSG_SCRATCH.format(
                what=f"{p.replace(UNK, '$?')}: a glob or unset variable in "
                     f"/{'/'.join(comps[:level])}/, at or above the level that may go"))
        if (isinstance(want, str) and c != want) or (hasattr(want, "match") and not want.match(c)):
            raise Blocked(MSG_SCRATCH.format(what=f"{p}, which is in /tmp but not in a "
                                                  "session scratchpad's <role>/<ticket> folders"))


def what_is(comps):
    p = "/" + "/".join(comps)
    names = {1: "/tmp itself", 2: "/tmp/claude-<uid> itself", 3: f"a project's folder ({p})",
             4: f"a session's folder ({p})", 5: f"the session scratchpad ({p})",
             6: f"a role folder in the scratchpad ({p}), every ticket's scratch in it"}
    return names.get(len(comps), p)


# --------------------------------------------------------------------------- main
def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(data, dict) or data.get("tool_name") != "Bash":
        return 0
    cmd = (data.get("tool_input") or {}).get("command") or ""
    cwd = data.get("cwd")
    cwd = posixpath.normpath(cwd) if isinstance(cwd, str) and cwd.startswith("/") else None
    try:
        walk(tokenize(cmd)[0], Ctx(cwd))
    except Blocked as b:
        print(f"Blocked by {HOOK}: {b}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001 -- a hook bug must never block every command
        print(f"{HOOK}: internal error ({type(e).__name__}: {e}); this command was not "
              "checked. Please report it.", file=sys.stderr)
        sys.exit(1)
