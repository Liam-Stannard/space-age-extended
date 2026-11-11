#!/usr/bin/env python3
"""PreToolUse hook on Bash: the four rules agents have broken before.

  1. No polling loops: a `while`, `until` or `select` loop, an arithmetic
     `for ((...))` loop, or a `for` over a generated list, with `sleep`
     inside it.
  2. No deleting across shared scratch: `rm -r`, `find ... -delete` and
     `find ... -exec rm` under /tmp only two or more levels below a session
     scratchpad (scratchpad/<role>/<ticket>), never above that.
  3. No stopping processes by name: `pkill`, `killall`, and `kill` given PIDs
     from `pgrep` or `pidof`.
  4. No running the Factorio binary (any `.../bin/x64/factorio`, which is
     what `tools/paths.py factorio-bin` prints) except through
     tools/client/launch.sh.

**Why.** On 2026-10-10 an artist left 18 background loops of the form
`until grep -q "^exit" <log>; do sleep 30; done` running: it started a new one
about every ten minutes and never stopped the old ones, and one more polled a
folder that had been deleted, so it could never end. This hook used to allow
such a loop inside `timeout <= 3600` and refuse a duplicate of one already
running (a `ps` check); since 2026-11-11 (Liam: "Ban them") every such loop
with a sleep in it is refused, and the `ps` check is gone. A `while read` loop
with no sleep is not polling and passes. A `for` loop over a literal word
list (`for i in 1 2 3`, `for i in {1..60}`, `for f in *.png`) is bounded by
it and passes, sleep or not. With a sleep in it, `for ((;;))` and any other
arithmetic `for` is refused, and so is a `for` whose list is generated: a
$(...), backticks or a variable in it (`for i in $(seq 60)`, `for f in
$FILES`, `for x; do` over "$@") (Liam 2026-11-11, "Block it").

Later the same day an agent told to clear its own superseded scratch ran
`find <scratchpad> -mindepth 1 -maxdepth 1 ! -name <its folder> -exec rm -rf
{} +` and deleted every other agent's scratch, including a render that was
still running. Scratch is laid out scratchpad/<role>/<ticket>/, so a
recursive delete under /tmp is allowed only on a path at least two levels
below a session scratchpad (/tmp/claude-<uid>/<project>/<session>/scratchpad),
every level down to the second spelled out (no glob, no variable; a brace
list counts as the folders it names). The scratchpad itself, a role
folder, /tmp/claude-<uid>, /tmp and anything else under /tmp are refused.
Deletes outside /tmp are not this hook's business. Shell variables assigned
in the same command are expanded first, so `S=<scratchpad>; rm -rf "$S"/*`
is caught, and `cd`, `pushd` and `popd` are followed (a `cd` inside
`( ... )` ends with it), so `cd <scratchpad> && rm -rf *` is too.

pkill/killall (Liam 2026-11-11, "No pkill/killall") stop every process
matching a name: other agents' renders and clients, Liam's own game; `kill
$(pgrep ...)` and `pgrep ... | xargs kill` do the same and are refused with
them. And the game client is started only by launch.sh (Liam 2026-11-11,
"Factorio only via launch.sh"), which keeps it off Liam's display and
speakers. The hook sees only the Bash command's text, so a script that runs
the binary inside it (launch.sh, check-data-stage.sh) is never seen and
passes.

**How it reads a command.** The text is tokenised as the shell would: quotes,
escapes, `$(...)`, backticks, heredocs and comments. Only a word in command
position counts, so `grep -n pkill file`, `echo "while true; do sleep 1;
done"`, a commit message (quoted or in a heredoc) and `ls .../bin/x64/factorio`
all pass. Command substitutions and `bash -c`/`sh -c`/`eval`/`trap` strings,
and the command a `find -exec` runs (its `{}` and a `sh -c` string's "$1"
standing for find's start point), are read as commands. Wrappers (sudo, env,
timeout, nohup, setsid, xargs, xvfb-run, nice, stdbuf, ...) are looked
through to the command they run. A `for NAME in ...` variable stands for the
riskiest word in its list, so `for d in <scratchpad>/*; do rm -rf "$d"; done`
is caught, and `find <root> ... | xargs rm` is read as a delete of <root>.
Brace lists are expanded (`rm -rf /{tmp,var}` is a delete of /tmp).
`${X:-word}`, `${X-word}`, `${X:=word}` and `${X=word}` are the variable's
value when this command sets X, else the word (expanded the same way, and
`:=`/`=` then set X to it); every other `${X...}` form (`#`, `%`, `/`, `:+`,
`:?`, ...) is read as plain `$X`. Not seen: a script file's contents, a shell
function's body where it is called, a `python3 -c` string,
`pgrep ... | while read p; do kill "$p"; done`.

Known false blocks, left as they are (2026-11-11): a variable set by `read`
or a function's arguments counts as unset (`read d; rm -rf "$d"/*` is
refused as `rm -rf /*`); a `cd` in a function body is followed where the
function is defined; a `case` pattern's `)` inside `( ... )` or `$(...)` ends
that subshell or substitution early, so what follows is misread.

**Fail-open or closed.** A hook error never blocks: bad JSON passes, and an
internal error exits 1 (Claude Code shows the message and runs the command).
A command nested more than MAX_DEPTH levels deep ($(...), backticks, shell
strings) is refused: it cannot be read, and no real command is that deep.
Rules 1, 3 and 4 need nothing outside the command text. In rule 2 a variable
this command sets counts as set even when its value is unknown
(`d=$(mktemp -d); rm -rf "$d"/*` passes). A variable it does not set is
empty (the Bash tool keeps no shell state between calls), so a target that is
only such variables, slashes and `*` (`"$X"/*`, `"$OUT/$NAME"`) is refused:
it is `/`, `/*` or `*`. Otherwise a target the hook cannot place passes (a
path starting with an unset or unknown variable, a relative path after a `cd`
it cannot follow), but a glob or variable at or above the second level under
/tmp is refused.

Exit 2 blocks the command and hands the message on stderr back to the agent.
"""
import fnmatch
import json
import posixpath
import re
import sys

HOOK = ".claude/hooks/no-ghost-waits.py"
UNK = "\x00"            # text set by this command but unknown to the hook: $(...), $((...))
UNSET = "\x01"          # a variable this command does not set: empty when it runs
VAGUE = UNK + UNSET
GLOB = set("*?[{") | set(VAGUE)
MAX_DEPTH = 24          # nested $(...) / backticks / bash -c levels read; deeper is refused
KILL_BY_NAME = {"pgrep", "pidof"}

MSG_LOOP = (
    "a polling loop: a while, until or select loop, a `for ((...))` loop or a `for` over a "
    "generated list ($(...), a variable), with `sleep` in it. Polling loops are banned. "
    "Instead: start the job itself (render.sh, launch.sh, a server) with the Bash tool's "
    "run_in_background; the harness tells you when it exits, no loop needed. To wait for a "
    "process you did not start, `timeout <seconds> tail --pid=<pid> -f /dev/null` (at most "
    "3600 s). render.sh writes <out-dir>/render.done "
    "('exit <code>') when it ends. A fixed number of tries is a word list: `for i in 1 2 3`."
)
MSG_SCRATCH = (
    "this deletes {what}. Under /tmp only a folder two or more levels below the session "
    "scratchpad may be deleted (scratchpad/<role>/<ticket>, or deeper), every level down to "
    "that one spelled out: no glob and no variable (a brace list counts as the folders it "
    "names). Never the scratchpad, a role folder, /tmp/claude-<uid>, /tmp or anything else in "
    "/tmp: other agents work there. "
    "Instead: delete the folder you created yourself by its exact path, e.g. "
    "`rm -r <scratchpad>/<role>/<ticket>`."
)
MSG_STOP = (
    "Instead: stop by PID from your own launch, never by name: `kill <pid>` with the PID "
    "run_in_background gave you, or the ones launch.sh lists in <run>/pids.txt (it stops them "
    "itself; `tools/client/launch.sh --recover <run>` cleans up after a crash)."
)
MSG_PKILL = ("`{name}` stops every process matching a name, including other agents' jobs and "
             "Liam's game. " + MSG_STOP)
MSG_KILLNAME = ("this kills processes found by name ({how}), which takes in other agents' "
                "jobs and Liam's game. " + MSG_STOP)
MSG_FACTORIO = (
    "this runs the Factorio binary directly ({path}). Instead: start a client only with "
    "`tools/client/launch.sh --task <name> ...` (headless, private display, no sound, stopped "
    "when it ends; see its --help), and check the data stage with tools/check-data-stage.sh."
)
MSG_DEEP = (
    f"this command nests $(...), backticks or shell strings more than {MAX_DEPTH} levels deep, "
    "too deep for the hook to read, so it is refused rather than run unchecked. Instead: "
    "split it into simpler steps."
)


class Blocked(Exception):
    pass


class TooDeep(Blocked):
    def __init__(self):
        super().__init__(MSG_DEEP)


# --------------------------------------------------------------------------- tokens
# A word is a list of parts: ("lit", text, quoted), ("var", name), ("cmd", tokens, raw),
# or ("var", name, op, parts) for ${name:-word} and the like, op one of :- - := =.
# A token is ("word", parts), ("op", text) or ("redir", text).

OPS = ("&&", "||", ";;", "|&", ";", "&", "|", "(", ")", "\n")
REDIR = re.compile(r"(?:\d+|&)?(?:<<<|<<-|<<|>>|>&|<&|<>|>\||>|<)")
META = set(" \t\n;&|()<>")
_NEST = [0]             # tokenize() calls open now: $(...) inside $(...) inside ...


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


def nested(fn, *args):
    """fn(*args), one level deeper: past MAX_DEPTH levels, TooDeep."""
    _NEST[0] += 1
    try:
        if _NEST[0] > MAX_DEPTH:
            raise TooDeep()
        return fn(*args)
    finally:
        _NEST[0] -= 1


def tokenize(text, i=0, close=False):
    """Tokens of text from i; with close, stop at the `)` closing a `$(`. Raises only
    TooDeep, past MAX_DEPTH nested substitutions."""
    return nested(_tokenize, text, i, close)


def brace_end(text, k):
    """The index of the `}` closing a `${` whose body starts at k (len(text) if none)."""
    depth, n = 1, len(text)
    while k < n:
        c = text[k]
        if c == "\\":
            k += 2
        elif c in "'`":
            e = text.find(c, k + 1)
            k = n if e < 0 else e + 1
        elif c == '"':
            k += 1
            while k < n and text[k] != '"':
                k += 2 if text[k] == "\\" else 1
            k += 1
        elif text.startswith("$(", k) and not text.startswith("$((", k):
            k = tokenize(text, k + 2, close=True)[1]
        elif text.startswith("${", k):
            depth += 1
            k += 2
        elif c == "}":
            depth -= 1
            if depth == 0:
                return k
            k += 1
        else:
            k += 1
    return n


def default_word(s):
    """The parts of a ${X:-word} default: one word, its blanks and operators kept."""
    return nested(_default_word, s)


def _default_word(s):
    parts, k = [], 0
    while k < len(s):
        if s[k] in META:
            parts.append(("lit", s[k], True))
            k += 1
        else:
            got, after = read_word(s, k)
            parts.extend(got)
            k = after if after > k else k + 1
    return parts


def _tokenize(text, i, close):
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
        j = brace_end(text, i + 2)
        body = text[i + 2:j]
        m = re.match(r"([A-Za-z_]\w*|[0-9@*])(:?[-=])?", body)
        if not m:
            return ("var", "?"), j + 1              # ${#X}, ${!X}: not a path
        if m.group(2):                              # ${X:-word} ${X-word} ${X:=word} ${X=word}
            return ("var", m.group(1), m.group(2), default_word(body[m.end():])), j + 1
        return ("var", m.group(1)), j + 1           # ${X}, and ${X#..} ${X%..} ${X/..} ${X:+..}
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
    """A word as far as the hook can know it: text with UNK/UNSET where it cannot, and the
    raw text of every command substitution it holds."""

    def __init__(self, text, subs):
        self.text, self.subs = text, subs

    @property
    def known(self):
        return not set(self.text) & set(VAGUE)


SPECIAL = set("#?$!-0")     # $#, $?, $$, $!, $-, $0: always set, value unknown
RAN = {}                    # a substitution's raw text -> the commands it runs


def evaluate(parts, env):
    text, subs = [], []
    for p in parts:
        if p[0] == "lit":
            text.append(p[1])
        elif p[0] == "var":
            v = env.get(p[1])
            if v is None and len(p) == 4:       # ${X:-word}, X not set here: the word
                v = evaluate(p[3], env)
                if p[2].endswith("="):          # ${X:=word} sets X too
                    env[p[1]] = v
            text.append(v.text if v else UNK if p[1] in SPECIAL else UNSET)
            subs.extend(v.subs if v else [])
        else:
            text.append(UNK)
            subs.append(p[2])
    return Value("".join(text), subs)


def shown(text):
    return text.replace(UNK, "$?").replace(UNSET, "$?")


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
    def __init__(self, cwd, depth=0, find_exec=False):
        self.env, self.cwd, self.depth, self.find_exec = {}, cwd, depth, find_exec
        self.loops = []         # open loops, innermost last: [keyword, has_sleep, polls]
        self.sleep = False      # a sleep was run anywhere in this text
        self.ran = set()        # every command run in this text (substitutions' too)
        self.dirs = []          # pushd's stack
        self.saved = []         # (cwd, env, dirs) at each open `(`
        self.pipe_find = None   # the start points of a find earlier in this pipeline
        self.pipe_pgrep = False  # a pgrep/pidof earlier in this pipeline

    def child(self):
        if self.depth >= MAX_DEPTH:
            raise TooDeep()
        c = Ctx(self.cwd, self.depth + 1, self.find_exec)
        c.env = dict(self.env)
        return c

    def adopt(self, child):
        """What a child context ran counts here too: its sleeps mark this text's loops."""
        if child.sleep:
            mark_sleep(self)
        self.ran |= child.ran


def mark_sleep(ctx):
    ctx.sleep = True
    for frame in ctx.loops:
        frame[1] = True


def check_text(text, ctx):
    """Read text as commands in a child context."""
    child = ctx.child()
    walk(tokenize(text)[0], child)
    ctx.adopt(child)


def subs_of(parts, ctx):
    for p in parts:
        if p[0] == "cmd":
            child = ctx.child()
            walk(p[1], child)
            ctx.adopt(child)
            RAN[p[2]] = RAN.get(p[2], set()) | child.ran
        elif p[0] == "var" and len(p) == 4:
            subs_of(p[3], ctx)                  # ${X:-$(cmd)}


KEYWORD_THEN_COMMAND = {"do", "then", "else", "elif", "if", "{", "}", "!", "time", "fi", "esac"}
POLLS = {"while": True, "until": True, "select": True, "for": False}


def end_loop(frame):
    if frame[1] and frame[2]:
        raise Blocked(MSG_LOOP)


def walk(toks, ctx):
    words, skip_next, header = [], False, None      # header: a for/select loop's, to `do`
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
            if header is not None:
                if plain(parts) == "do":
                    if not ctx.loops[-1][2]:
                        ctx.loops[-1][2] = generated(header)
                        bind_for(header, ctx)
                    header = None
                else:
                    header.append(parts)
                continue
            word = plain(parts) if not words else None
            if word in POLLS:
                ctx.loops.append([word, False, POLLS[word]])
                if word in ("for", "select"):
                    header = []
            elif word == "done":
                if ctx.loops:
                    end_loop(ctx.loops.pop())
            elif word in KEYWORD_THEN_COMMAND:
                pass
            else:
                words.append(parts)
            continue
        # an operator ends the simple command
        op, skip_next = tok[1], False
        if header is not None:
            if op == "(" and not header and ctx.loops[-1][0] == "for":
                ctx.loops[-1][2] = True     # `for ((...))`: arithmetic, no word list
            continue                        # the header runs to `do`
        simple(words, ctx, piped=op in ("|", "|&"))
        words = []
        if op not in ("|", "|&"):
            ctx.pipe_find, ctx.pipe_pgrep = None, False
        if op == "(":
            ctx.saved.append((ctx.cwd, dict(ctx.env), list(ctx.dirs)))
        elif op == ")" and ctx.saved:
            ctx.cwd, ctx.env, ctx.dirs = ctx.saved.pop()    # a subshell's cd ends with it
    simple(words, ctx, piped=False)
    for frame in ctx.loops:
        end_loop(frame)             # a loop with no `done` yet


def generated(header):
    """A for loop's word list is made at run time: a $(...), backticks or a variable in it
    (`for i in $(seq 60)`, `for f in $FILES`, `for x; do` over "$@"); a literal list,
    brace range or glob is not."""
    if len(header) < 2 or plain(header[1]) != "in":
        return True
    return any(p[0] in ("cmd", "var") or (p[0] == "lit" and UNK in p[1])
               for word in header[2:] for p in word)


def bind_for(header, ctx):
    """`for NAME in WORD...`: NAME takes the word a delete of it would refuse, if one
    would (`for d in <scratchpad>/*; do rm -rf "$d"; done`), else the first word."""
    if not header or plain(header[0]) is None:
        return
    name, items = plain(header[0]), header[1:]
    if items and plain(items[0]) == "in":
        vals = [evaluate(w, ctx.env) for w in items[1:]]
    else:                                       # `for NAME; do`: over "$@"
        vals = [ctx.env["@"]] if "@" in ctx.env else []
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


def change_dir(target, ctx):
    if target is None:
        ctx.cwd = None                          # home, or pushd's swap
    elif target.known and ctx.cwd is not None:
        ctx.cwd = posixpath.normpath(posixpath.join(ctx.cwd, target.text))
    elif target.known and target.text.startswith("/"):
        ctx.cwd = posixpath.normpath(target.text)
    else:
        ctx.cwd = None


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
    ctx.ran.add(name)

    if name in DECLARE:
        for w in words[i + 1:]:
            a = assignment(w)
            if a:
                ctx.env[a[0]] = evaluate(a[1], ctx.env)
        return
    if name in ("cd", "pushd", "popd"):
        target = next((a for a in args if not a.text.startswith(("-", "+"))), None)
        if name == "popd":
            ctx.cwd = ctx.dirs.pop() if ctx.dirs else None
            return
        if name == "pushd":
            ctx.dirs.append(ctx.cwd)
        change_dir(target, ctx)
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
    if name in KILL_BY_NAME and piped:
        ctx.pipe_pgrep = True
    if name == "kill":
        check_kill(args, ctx, via_xargs)
    if name == "sleep":
        mark_sleep(ctx)
    if is_factorio(cmd, ctx):
        path = cmd.text if cmd.text.strip(VAGUE) else "the path tools/paths.py factorio-bin prints"
        raise Blocked(MSG_FACTORIO.format(path=shown(path)))
    if name == "rm":
        check_rm(args, ctx, via_xargs)
    elif name == "find":
        check_find(args, ctx, piped)


def check_kill(args, ctx, via_xargs):
    if via_xargs and ctx.pipe_pgrep:
        raise Blocked(MSG_KILLNAME.format(how="pgrep/pidof piped to xargs kill"))
    for a in args:
        for s in a.subs:
            found = RAN.get(s, set()) & KILL_BY_NAME
            if found:
                raise Blocked(MSG_KILLNAME.format(how=f"kill given {sorted(found)[0]}'s output"))


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
    recursive, targets, opts = ctx.find_exec, [], True     # under find, every rm counts
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
FIND_EXEC = ("-exec", "-execdir", "-ok", "-okdir")


def check_find(args, ctx, piped):
    k = 0
    while k < len(args) and (args[k].text in ("-H", "-L", "-P")
                             or args[k].text.startswith(("-O", "-D"))):
        k += 2 if args[k].text == "-D" else 1
    starts = []
    while k < len(args) and not FIND_EXPR.match(args[k].text):
        starts.append(args[k].text)
        k += 1
    starts = starts or ["."]
    expr = [a.text for a in args[k:]]
    acts = "-delete" in expr
    if acts:
        for s in starts:
            check_target(s, ctx)
    for j, a in enumerate(expr):
        if a in FIND_EXEC:
            run = []
            for x in expr[j + 1:]:
                if x in (";", "+"):
                    break
                run.append(x)
            acts = True
            for s in starts:
                find_exec(run, s, ctx)
    if not acts and piped:
        ctx.pipe_find = starts


def find_exec(run, start, ctx):
    """The command a find -exec runs, read with its {} -- and a shell string's "$1"... --
    standing for the start point (what it finds is in it; with no -mindepth, it itself)."""
    if not run:
        return
    child = ctx.child()
    child.find_exec = True
    for pos in list("123456789@*"):
        child.env[pos] = Value(start, [])
    words = [[("lit", x.replace("{}", start), True)] for x in run]
    simple(words, child, piped=False)
    ctx.adopt(child)


BRACE = re.compile(r"\{([^{}]*,[^{}]*)\}")


def braces(t, budget=64):
    """t with its innermost-first brace lists expanded (`/{tmp,var}`: /tmp and /var)."""
    m = BRACE.search(t) if t.count("{") <= 32 else None
    if not m:
        return [t]
    out = []
    for alt in m.group(1).split(","):
        out.extend(braces(t[:m.start()] + alt + t[m.end():], budget))
        if len(out) >= budget:
            break
    return out[:budget]


SCRATCH = ("tmp", re.compile(r"claude-\d+\Z"), None, None, "scratchpad", None, None)


def check_target(t, ctx):
    """Refuse a recursive delete of t unless it is outside /tmp or deep enough in scratch."""
    for alt in braces(t):
        check_one(alt, ctx)


def check_one(t, ctx):
    if not t:
        return
    lead = len(t) - len(t.lstrip(VAGUE))
    if lead:
        rest = t[lead:]
        if UNK in t[:lead]:
            return          # a variable this command sets, to a value the hook cannot know
        # only variables this command does not set, so empty when it runs
        if rest and set(rest) <= set("/*" + VAGUE):
            raise Blocked(MSG_SCRATCH.format(
                what=f"`{shown(t)}`: every variable in it is one this command does not set, "
                     "so it is empty, and this is `rm -rf /`, `/*` or `*`"))
        return              # where the rest is depends on what it was meant to be
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
        if not fnmatch.fnmatchcase("tmp", first.replace(UNK, "*").replace(UNSET, "*")):
            return
        raise Blocked(MSG_SCRATCH.format(what=f"{shown(p)}, which takes in /tmp"))
    if first != "tmp":
        return                                  # outside /tmp
    for level, want in enumerate(SCRATCH):
        if level >= len(comps):
            raise Blocked(MSG_SCRATCH.format(what=what_is(comps)))
        c = comps[level]
        if set(c) & GLOB:
            raise Blocked(MSG_SCRATCH.format(
                what=f"{shown(p)}: a glob or variable in /{'/'.join(comps[:level])}/, at or "
                     "above the level that may go"))
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
