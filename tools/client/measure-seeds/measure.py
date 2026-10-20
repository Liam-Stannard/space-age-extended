#!/usr/bin/env python3
"""tools/client/measure-seeds/measure.py -- the map-gen seed harness: the
nearest pool and the starting patches round the landing, seed by seed, on a
headless Factorio server driven over RCON.

Usage:
  tools/client/measure-seeds/measure.py --task NAME (--seeds A,B,... | --seeds-file FILE)
      [--settings FILE] [--reference FILE] [--worktree DIR] [--mod PATH]...
      [--seed-timeout S] [--timeout S]

  --task NAME        Evidence goes to <repo>/evidence/NAME/seeds-<stamp>-<pid>/ (git-ignored).
  --seeds A,B,...    Seeds to measure; with --seeds-file, these come after the file's.
  --seeds-file FILE  One seed a line, '#' comments (seeds/pool-placed-30.txt: the
                     pool-placed table's 30).
  --settings FILE    What to measure and the rule it is held to (default
                     settings/core.json): planet, landing, radius (tiles of chunks
                     generated round the landing), pool and shore tiles, rule
                     {none_within, nearest_min, nearest_max}, the placed pool's
                     bearing expression, the starting patches (entity; reach,
                     bearing and radius as numbers or noise-expression names;
                     turn, the preferred bearing in turns from reference_bearing;
                     expect, an exact count), map_gen overrides one level deep
                     (e.g. {"autoplace_controls": {"sae-gas-vent": {...}}}).
  --reference FILE   Recorded values to compare with (reference/pool-placed-30.csv):
                     a CSV, '#' comments, a `seed` column, an optional `source`
                     column, and any of the measured columns below but seconds and
                     error. Checked when read (usage error, exit 2): an unknown
                     column, a seed twice, a number column whose cell is not a
                     number, a yes/no column (pass, nearest_is_placed, *_placed,
                     *_dry) whose cell is not yes or no. A blank cell is not
                     compared; a row all blank is "not recorded" (reported, not a
                     failure). Distances match within 0.05 tiles (the table's one
                     decimal), bearings within 0.5 degree on the circle (-180 and
                     179.9 match), eighths within 0.05 round the eight, counts
                     exactly, yes/no as words. The run fails if a seed in both lists
                     has a recorded value that differs or is missing from the
                     measure, or if nothing at all was compared (no shared seed).
  --worktree DIR     The mod to load (default: this repo).
  --mod PATH         An extra mod (folder or .zip), e.g. alien-biomes. Repeatable.
  --seed-timeout S   Longest wait for one seed (default 300).
  --timeout S        Hard limit on the whole run, 60-3600 (default 3600).

The server: `factorio --start-server-load-scenario base/freeplay` with a scratch
mod directory (the worktree symlinked in, plus the harness mod in mod/ with the
settings as config.lua), write-data in the run directory, RCON and the game port
bound to 127.0.0.1 on free ports, not public, not on the LAN, a random game
password, no WAYLAND_DISPLAY or DISPLAY. It refuses (exit 3) while any factorio
runs or while tools/client/launch.sh holds its lock, and holds that lock itself
for the whole run, so no client can start beside it. Each seed is one RCON
command, /sae-measure-seed <seed>, answered with one JSON line (mod/control.lua
says what is measured). The server is stopped with /quit, then SIGTERM, then
SIGKILL, by its session; the run fails (exit 5) if anything of it is left.

Written to the run directory: seeds.csv and seeds.json (the per-seed table),
seeds.jsonl (each reply as it came), compare.csv (with --reference), summary.txt
(the table as text and the summary line), run.json (the record: seeds, settings,
mods, ports, PIDs, versions, exit), server.log and data/ (the server's own).
The summary line is also printed last.

Measured columns: seed, pass, pool, pool_x, pool_y, pool_tiles_within_<N>, shore,
placed_bearing_deg, placed_off_eighths, placed_area, nearest_is_placed, and per
patch <key>_reach, _bearing_deg, _off_deg, _n, _wet, _stray, _nearest,
_centroid, _placed, _dry; seconds, error. pool/shore: nearest tile centre to the
landing; <key>_reach: the patch centre's distance; _nearest/_centroid: of the
entities placed; _dry: placed (n > 0, or n == expect) and none on pool or shore.

Exit: 0 every seed passes the rule (nearest pool in [nearest_min, nearest_max],
no pool tile within none_within, every patch placed and dry) and, with
--reference, matches every recorded value; 1 a seed failed, errored or does not
match; 2 usage; 3 refused; 4 the server could not be started or reached;
5 cleanup left a process behind; 130/143 interrupted.
"""

import argparse
import csv
import fcntl
import json
import os
import secrets
import shutil
import signal
import socket
import statistics
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True  # no __pycache__ beside the tools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

sys.path.insert(0, os.path.join(common.REPO_ROOT, "tools"))
import rcon  # noqa: E402

PROG = "measure.py"
SERVERDATA_EXECCOMMAND = 2


class Interrupted(Exception):
    def __init__(self, signum):
        super().__init__(f"signal {signum}")
        self.signum = signum


class HarnessError(Exception):
    """The server could not be started or reached: exit 4."""


def on_signal(signum, _frame):
    raise Interrupted(signum)


def free_port(kind):
    with socket.socket(socket.AF_INET, kind) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Server:
    """One headless server, started in its own session and stopped by it."""

    def __init__(self, run_dir, mods_dir, log):
        self.run_dir, self.mods_dir, self.log = run_dir, mods_dir, log
        self.proc = None
        self.conn = None
        self.rcon_port = free_port(socket.SOCK_STREAM)
        self.game_port = free_port(socket.SOCK_DGRAM)
        self.password = secrets.token_hex(16)
        self.pids = []

    def start(self):
        data = os.path.join(self.run_dir, "data")
        os.makedirs(data)
        cfg = os.path.join(data, "config.ini")
        with open(cfg, "w", encoding="utf-8") as f:
            f.write("[path]\nread-data=__PATH__executable__/../../data\nwrite-data=%s\n" % data)
        ss = os.path.join(self.run_dir, "server-settings.json")
        with open(ss, "w", encoding="utf-8") as f:
            json.dump({"name": "sae-measure-seeds", "description": "", "tags": [], "max_players": 0,
                       "visibility": {"public": False, "lan": False},
                       "game_password": secrets.token_hex(16), "require_user_verification": False,
                       "allow_commands": "admins-only", "autosave_interval": 9999, "autosave_slots": 1,
                       "auto_pause": False, "only_admins_can_pause_the_game": True,
                       "autosave_only_on_server": True}, f, indent=1)
        cmd = [common.factorio_bin(), "--start-server-load-scenario", "base/freeplay",
               "--config", cfg, "--mod-directory", self.mods_dir, "--server-settings", ss,
               "--bind", f"127.0.0.1:{self.game_port}",
               "--rcon-bind", f"127.0.0.1:{self.rcon_port}", "--rcon-password", self.password]
        env = {k: v for k, v in os.environ.items() if k not in ("WAYLAND_DISPLAY", "WAYLAND_SOCKET", "DISPLAY")}
        self.log(f"starting: {' '.join(c if c != self.password else '<password>' for c in cmd)}")
        out = open(os.path.join(self.run_dir, "server.log"), "w", encoding="utf-8")
        # stdin stays an open pipe: the server quits on EOF. The stop signals are
        # held off from just before the spawn until self.proc is set, so an
        # interrupt cannot land between the two and leave the server unknown to
        # stop(); the child gets them unblocked again before it runs factorio.
        held = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)
        signal.pthread_sigmask(signal.SIG_BLOCK, held)
        try:
            self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT,
                                         env=env, start_new_session=True,
                                         preexec_fn=lambda: signal.pthread_sigmask(signal.SIG_UNBLOCK, held))
            self.pids.append(self.proc.pid)
            with open(os.path.join(self.run_dir, "pids.txt"), "a", encoding="utf-8") as f:
                f.write(f"{self.proc.pid} factorio server (session leader)\n")
        finally:
            out.close()
            signal.pthread_sigmask(signal.SIG_UNBLOCK, held)
        self.log(f"server pid {self.proc.pid} (session leader), rcon 127.0.0.1:{self.rcon_port}, "
                 f"game 127.0.0.1:{self.game_port}")

    def connect(self, limit):
        """Wait (bounded) for RCON to answer, the server still alive."""
        end = time.monotonic() + limit
        while time.monotonic() < end:
            if self.proc.poll() is not None:
                raise HarnessError(f"the server exited ({self.proc.returncode}) before RCON was up; see server.log")
            try:
                self.conn = rcon.Rcon(port=self.rcon_port, password=self.password, timeout=10)
                return
            except OSError:
                time.sleep(1)
            except SystemExit as e:  # rcon.py's way of saying auth failed or the line closed
                raise HarnessError(f"RCON: {e}") from None
        raise HarnessError(f"RCON did not answer within {limit} s")

    def call(self, command, timeout):
        """Send a command; return its reply. A second command marks the reply's end,
        so a slow seed is waited for rather than cut off."""
        c = self.conn
        rid = c._send(SERVERDATA_EXECCOMMAND, command)
        end = c._send(SERVERDATA_EXECCOMMAND, "/sae-measure-end")
        c.sock.settimeout(timeout)
        parts = []
        while True:
            try:
                got, body = c._recv()
            except socket.timeout:
                raise HarnessError(f"no reply to '{command}' within {timeout} s") from None
            except SystemExit as e:  # rcon.py: the connection closed (the server died?)
                raise HarnessError(f"RCON during '{command}': {e}") from None
            if got == rid:
                parts.append(body)
            elif got == end:
                return "".join(parts).strip()

    def stop(self):
        """/quit, then SIGTERM, then SIGKILL to the session; returns what is left."""
        if self.proc is None:
            return []
        quit_sent = False
        if self.proc.poll() is None and self.conn is not None:
            try:
                self.conn.sock.settimeout(5)
                self.conn._send(SERVERDATA_EXECCOMMAND, "/quit")
                quit_sent = True
                self.log("sent /quit")
            except OSError as e:
                self.log(f"/quit not sent: {e}")
        if quit_sent:
            try:
                self.proc.wait(timeout=60)
            except subprocess.TimeoutExpired:
                pass
        for sig, wait in ((signal.SIGTERM, 15), (signal.SIGKILL, 10)):
            left = session_pids(self.proc.pid)
            if self.proc.poll() is None or left:
                self.log(f"sending {sig.name} to session {self.proc.pid}: {left}")
                try:
                    os.killpg(self.proc.pid, sig)
                except ProcessLookupError:
                    pass
                try:
                    self.proc.wait(timeout=wait)
                except subprocess.TimeoutExpired:
                    pass
        if self.conn is not None:
            try:
                self.conn.sock.close()
            except OSError:
                pass
        left = session_pids(self.proc.pid)
        if self.proc.poll() is None:
            left.append(self.proc.pid)
        self.log(f"server exit {self.proc.returncode}; left: {left or 'nothing'}")
        return left


def session_pids(sid):
    r = subprocess.run(["ps", "-e", "-o", "pid=,sid="], capture_output=True, text=True, check=False)
    out = []
    for line in r.stdout.splitlines():
        p, s = line.split()
        if int(s) == sid:
            out.append(int(p))
    return out


# ------------------------------------------------------------------ tables

def flat(res, settings):
    """One measured reply -> one CSV row."""
    n = settings["rule"]["none_within"]
    row = {"seed": res["seed"]}
    if "error" in res:
        row["error"] = res["error"]
        row["pass"] = False
        return row
    pool, shore, pp = res["pool"], res["shore"], res.get("placed_pool") or {}
    at = pool.get("at") or [None, None]
    row.update({
        "pass": res["pass"],
        "pool": pool.get("nearest"), "pool_x": at[0], "pool_y": at[1],
        f"pool_tiles_within_{fmt(n)}": pool["tiles_within"],
        "shore": shore.get("nearest"),
        "placed_bearing_deg": pp.get("bearing_deg"), "placed_off_eighths": pp.get("off_eighths"),
        "placed_area": pp.get("area"), "nearest_is_placed": pp.get("nearest_is_placed"),
    })
    for p in res["patches"]:
        k = p["key"]
        for f in ("reach", "bearing_deg", "off_deg", "n", "wet", "stray", "nearest", "centroid", "placed", "dry"):
            row[f"{k}_{f}"] = p.get(f)
    return row


def fmt(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def columns(settings):
    n = fmt(settings["rule"]["none_within"])
    cols = ["seed", "pass", "pool", "pool_x", "pool_y", f"pool_tiles_within_{n}", "shore",
            "placed_bearing_deg", "placed_off_eighths", "placed_area", "nearest_is_placed"]
    for p in settings["patches"]:
        cols += [f"{p['key']}_{f}" for f in ("reach", "bearing_deg", "off_deg", "n", "wet", "stray",
                                              "nearest", "centroid", "placed", "dry")]
    return cols + ["seconds", "error"]


def is_yes_no(col):
    return col in ("pass", "nearest_is_placed") or col.endswith("_placed") or col.endswith("_dry")


def read_reference(path, settings):
    """{seed: {column: cell}} with blank cells dropped; every column and cell checked
    against what measure.py measures, so nothing in it can go uncompared."""
    with open(path, encoding="utf-8", newline="") as f:
        lines = [ln for ln in f if not ln.lstrip().startswith("#") and ln.strip()]
    reader = csv.DictReader(lines)
    head = reader.fieldnames or []
    if "seed" not in head:
        raise common.Usage(f"{path}: no seed column")
    comparable = set(columns(settings)) - {"seed", "seconds", "error"}
    unknown = [c for c in head if c not in comparable and c not in ("seed", "source")]
    if unknown:
        raise common.Usage(f"{path}: not a measured column: {', '.join(repr(c) for c in unknown)} "
                           f"(measured: {', '.join(sorted(comparable))})")
    if len(set(head)) != len(head):
        raise common.Usage(f"{path}: a column is named twice")
    ref = {}
    for n, r in enumerate(reader, 2):
        if None in r:
            raise common.Usage(f"{path}: data row {n} has more cells than the header")
        seed = common.parse_seed((r["seed"] or "").strip(), f"{path}: data row {n}")
        if seed in ref:
            raise common.Usage(f"{path}: seed {seed} is listed twice")
        cells = {}
        for col, v in r.items():
            v = (v or "").strip()
            if col in ("seed", "source") or v == "":
                continue
            if is_yes_no(col):
                if v not in ("yes", "no"):
                    raise common.Usage(f"{path}: seed {seed}, {col}: '{v}' is not yes or no")
            else:
                try:
                    float(v)
                except ValueError:
                    raise common.Usage(f"{path}: seed {seed}, {col}: '{v}' is not a number") from None
            cells[col] = v
        ref[seed] = {"cells": cells, "source": (r.get("source") or "").strip()}
    return ref


def tolerance(col):
    if col.endswith("_n") or col.endswith("_wet") or col.endswith("_stray") or col.startswith("pool_tiles_within_"):
        return 0.0
    if col.endswith("_deg"):
        return 0.5
    return 0.05


def difference(col, got, want):
    """Measured minus recorded; bearings on the circle (degrees), eighths round the eight."""
    d = float(got) - float(want)
    if col.endswith("_deg"):
        d = (d + 180) % 360 - 180
    elif col.endswith("_eighths"):
        d = (d + 4) % 8 - 4
    return d


def compare(rows, ref):
    """-> (compare rows, per-seed verdicts {seed: 'match'|'differs'|'not recorded'|'not in reference'},
    fields compared). A recorded value the measure lacks (an errored seed) counts as differing."""
    out, verdict, total = [], {}, 0
    for row in rows:
        s = row["seed"]
        rec = ref.get(s)
        if rec is None:
            verdict[s] = "not in reference"
            continue
        if not rec["cells"]:
            verdict[s] = "not recorded"
            continue
        differs = 0
        for col, want in rec["cells"].items():
            got = row.get(col)
            diff = ""
            if got is None:
                ok = False
            elif is_yes_no(col):
                ok = fmt(got) == want
            else:
                diff = difference(col, got, want)
                ok = abs(diff) <= tolerance(col) + 1e-9
            differs += not ok
            total += 1
            out.append({"seed": s, "column": col, "recorded": want, "measured": fmt(got),
                        "diff": "" if diff == "" else f"{diff:+.3f}", "match": "yes" if ok else "NO",
                        "source": rec["source"]})
        verdict[s] = "match" if differs == 0 else "differs"
    return out, verdict, total


def text_table(rows, settings):
    n = fmt(settings["rule"]["none_within"])
    keys = [p["key"] for p in settings["patches"]]
    head = f"{'seed':>10} | {'pool':>6} | {'in' + n:>4} | {'shore':>6} | placed | " + " | ".join(
        f"{k:^24}" for k in keys) + " | pass"
    out = [head]
    for r in rows:
        if r.get("error"):
            out.append(f"{r['seed']:>10} | ERROR {r['error']}")
            continue
        cells = []
        for k in keys:
            cells.append(f"{fmt(r[k + '_reach']):>4}t {float(r[k + '_off_deg']):+5.0f}deg n{r[k + '_n']:>4} "
                         f"wet{r[k + '_wet']}{'' if r[k + '_dry'] else ' X'}")
        pool = "none" if r["pool"] is None else f"{r['pool']:.1f}"
        shore = "none" if r["shore"] is None else f"{r['shore']:.1f}"
        out.append(f"{r['seed']:>10} | {pool:>6} | {r['pool_tiles_within_' + n]:>4} | {shore:>6} | "
                   f"{fmt(r['nearest_is_placed']):>6} | " + " | ".join(f"{c:<24}" for c in cells)
                   + f" | {'PASS' if r['pass'] else 'FAIL'}")
    return out


def summarise(rows, settings, verdict, compared=None):
    rule = settings["rule"]
    n = fmt(rule["none_within"])
    good = [r for r in rows if not r.get("error")]
    pools = [r["pool"] for r in good if r["pool"] is not None]
    keys = [p["key"] for p in settings["patches"]]
    in_band = sum(1 for r in good
                  if r["pool"] is not None and rule["nearest_min"] <= r["pool"] <= rule["nearest_max"])
    within = [r for r in good
              if r["pool_tiles_within_" + n] > 0 or (r["pool"] is not None and r["pool"] < rule["none_within"])]
    dry = sum(1 for r in good for k in keys if r[k + "_dry"])
    parts = [f"{len(rows)} seeds"]
    if pools:
        parts.append(f"nearest pool min {min(pools):.1f}, median {statistics.median(pools):.1f}, max {max(pools):.1f}")
    parts.append(f"in {fmt(rule['nearest_min'])}-{fmt(rule['nearest_max'])}: {in_band}/{len(rows)}")
    parts.append(f"pool within {n}: {len(within)} seeds")
    parts.append(f"patches placed and dry: {dry}/{len(rows) * len(keys)}")
    errors = len(rows) - len(good)
    if errors:
        parts.append(f"errors: {errors}")
    ok = errors == 0 and all(r["pass"] for r in good)
    if verdict is not None:
        vs = list(verdict.values())
        rec = [v for v in vs if v in ("match", "differs")]
        parts.append(f"reference: {vs.count('match')}/{len(rec)} recorded seeds match, {compared} fields compared"
                     + (f", {vs.count('not recorded')} not recorded" if vs.count("not recorded") else "")
                     + (f", {vs.count('not in reference')} not in it" if vs.count("not in reference") else "")
                     + ("; NOTHING COMPARED" if not compared else ""))
        ok = ok and vs.count("differs") == 0 and bool(compared)
    return "measure-seeds: " + "; ".join(parts) + (" -> PASS" if ok else " -> FAIL"), ok


# -------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(prog=PROG, add_help=False)
    ap.add_argument("--task")
    ap.add_argument("--seeds")
    ap.add_argument("--seeds-file")
    ap.add_argument("--settings", default=common.DEFAULT_SETTINGS)
    ap.add_argument("--reference")
    ap.add_argument("--worktree", default=common.REPO_ROOT)
    ap.add_argument("--mod", action="append", default=[])
    ap.add_argument("--seed-timeout", type=int, default=300)
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("-h", "--help", action="store_true")
    try:
        a = ap.parse_args()
    except SystemExit:
        sys.exit(2)
    if a.help:
        print(__doc__)
        return 0
    try:
        if not a.task or "/" in a.task or a.task.startswith("."):
            raise common.Usage("--task NAME is required (a plain name)")
        if not 60 <= a.timeout <= 3600:
            raise common.Usage("--timeout must be 60-3600")
        if a.seed_timeout < 10:
            raise common.Usage("--seed-timeout must be at least 10")
        seeds = common.read_seeds(a.seeds, a.seeds_file)
        settings = common.load_settings(a.settings)
        ref = read_reference(a.reference, settings) if a.reference else None
        worktree = os.path.abspath(a.worktree)
        wt_name = common.mod_name_of(worktree)
        extra = []
        for m in a.mod:
            m = os.path.abspath(m)
            if not os.path.exists(m):
                raise common.Usage(f"--mod {m} does not exist")
            extra.append(m)
    except (common.Usage, OSError, ValueError, KeyError) as e:
        common.die(PROG, str(e))

    for sig in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, on_signal)

    lock = open(common.LOCK_FILE, "a", encoding="utf-8")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        common.die(PROG, f"REFUSED -- tools/client/launch.sh (or another harness) holds {common.LOCK_FILE}", 3)
    running = common.running_factorio()
    if running:
        common.die(PROG, "REFUSED -- a factorio process is already running (one at a time):\n" + running, 3)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    run_dir = os.path.join(common.REPO_ROOT, "evidence", a.task, f"seeds-{stamp}-{os.getpid()}")
    os.makedirs(run_dir)
    log_path = os.path.join(run_dir, "measure.log")

    def log(s):
        line = time.strftime("%H:%M:%S ") + s
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line, file=sys.stderr, flush=True)

    log(f"run dir: {run_dir}")
    record = {"task": a.task, "seeds": seeds, "settings_file": os.path.abspath(a.settings), "settings": settings,
              "reference": os.path.abspath(a.reference) if a.reference else None, "worktree": worktree,
              "extra_mods": extra, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    scratch = tempfile.mkdtemp(prefix="sae-measure-seeds.")
    server = None
    rows, raw = [], []
    code = 0
    t_end = time.monotonic() + a.timeout
    try:
        mods = os.path.join(scratch, "mods")
        os.makedirs(mods)
        os.symlink(worktree, os.path.join(mods, wt_name))
        common.build_mod(mods, {"mode": "server", "settings": settings})
        names = []
        for m in extra:
            if m.endswith(".zip"):  # name_version.zip, as the engine wants it
                names.append(os.path.basename(m)[:-4].rsplit("_", 1)[0])
                os.symlink(m, os.path.join(mods, os.path.basename(m)))
            else:
                names.append(common.mod_name_of(m))
                os.symlink(m, os.path.join(mods, names[-1]))
        enabled = ["base", "elevated-rails", "quality", "recycler", "space-age", wt_name] + names + [common.MOD_NAME]
        with open(os.path.join(mods, "mod-list.json"), "w", encoding="utf-8") as f:
            json.dump({"mods": [{"name": n, "enabled": True} for n in enabled]}, f, indent=1)
        record["mods_enabled"] = enabled

        server = Server(run_dir, mods, log)
        server.start()
        record.update(rcon_port=server.rcon_port, game_port=server.game_port, server_pid=server.proc.pid)
        server.connect(min(300, max(10, t_end - time.monotonic())))
        hello = server.call("/sae-measure-ping", 60)
        try:
            record["active_mods"] = json.loads(hello)["mods"]
        except (ValueError, KeyError):
            raise HarnessError(f"the harness mod did not answer the ping: {hello!r}") from None
        log("ready: " + ", ".join(record["active_mods"]))

        jsonl = os.path.join(run_dir, "seeds.jsonl")
        for i, seed in enumerate(seeds, 1):
            left = t_end - time.monotonic()
            if left < 5:
                raise HarnessError(f"--timeout reached after {i - 1} of {len(seeds)} seeds")
            t0 = time.monotonic()
            reply = server.call(f"/sae-measure-seed {seed}", min(a.seed_timeout, left))
            secs = time.monotonic() - t0
            try:
                res = json.loads(reply)
            except ValueError:
                res = {"seed": seed, "error": f"not JSON: {reply[:300]!r}"}
            with open(jsonl, "a", encoding="utf-8") as f:
                f.write(json.dumps(res) + "\n")
            raw.append(res)
            row = flat(res, settings)
            row["seconds"] = round(secs, 1)
            rows.append(row)
            log(f"{i}/{len(seeds)} seed {seed}: " + (f"ERROR {res['error']}" if "error" in res else
                f"pool {res['pool']['nearest']}, within {fmt(settings['rule']['none_within'])}: "
                f"{res['pool']['tiles_within']}, patches dry {res['patches_dry']}, {'PASS' if res['pass'] else 'FAIL'}")
                + f" ({secs:.1f} s)")
    except HarnessError as e:
        log(f"FAILED: {e}")
        code = 4
    except Interrupted as e:
        log(f"interrupted ({e})")
        code = 128 + e.signum
    except KeyboardInterrupt:
        log("interrupted (SIGINT)")
        code = 130
    finally:
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            signal.signal(sig, signal.SIG_IGN)
        left = server.stop() if server else []
        if server:
            record["pids"] = server.pids
            record["left_behind"] = left
            record["server_exit"] = server.proc.returncode if server.proc else None
        if left:
            code = 5
        # rmtree unlinks the symlinks in there (the worktree, extra mods); it does not follow them.
        shutil.rmtree(scratch)
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()

    # Tables, whatever happened: what was measured is kept.
    try:
        with open(os.path.join(run_dir, "server.log"), encoding="utf-8", errors="replace") as f:
            first = f.readline()
        record["factorio"] = first.split("; ", 1)[-1].strip()  # "Factorio 2.1.22 (build ...)"
    except OSError:
        pass
    cols = columns(settings)
    with open(os.path.join(run_dir, "seeds.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: fmt(r.get(c)) for c in cols})
    verdict = compared = None
    if ref is not None:
        cmp_rows, verdict, compared = compare(rows, ref)
        with open(os.path.join(run_dir, "compare.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["seed", "column", "recorded", "measured", "diff", "match", "source"])
            w.writeheader()
            w.writerows(cmp_rows)
    line, ok = summarise(rows, settings, verdict, compared)
    if len(rows) < len(seeds):
        line = line.replace(" -> PASS", " -> FAIL") + f" (only {len(rows)} of {len(seeds)} seeds measured)"
        ok = False
    text = [f"Seed harness, {record.get('factorio', '')}; landing {settings['landing']}, "
            f"chunks to {settings['radius']} tiles, planet {settings['planet']}.",
            "pool/shore: nearest tile centre to the landing; in<N>: pool tiles within N; placed: the nearest "
            "pool tile is the placed pool's; patch: centre distance, bearing off preferred, entities n, "
            "wet (on pool/shore); X = not placed and dry.", ""]
    text += text_table(rows, settings)
    if verdict is not None:
        text += ["", "Against the reference (" + os.path.abspath(a.reference) + "):"]
        text += [f"  {s}: {v}" for s, v in verdict.items()]
    text += ["", line]
    with open(os.path.join(run_dir, "summary.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(text) + "\n")
    record.update(finished=time.strftime("%Y-%m-%dT%H:%M:%S%z"), summary=line,
                  verdict=verdict and {str(k): v for k, v in verdict.items()},
                  reference_fields_compared=compared)
    if code == 0 and not ok:
        code = 1
    record["exit"] = code
    with open(os.path.join(run_dir, "seeds.json"), "w", encoding="utf-8") as f:
        json.dump({"seeds": raw, "rows": rows}, f, indent=1)
    with open(os.path.join(run_dir, "run.json"), "w", encoding="utf-8") as f:
        json.dump(record, f, indent=1)
    log(f"table: {os.path.join(run_dir, 'seeds.csv')}")
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
