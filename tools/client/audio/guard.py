"""tools/client/audio/guard.py -- the record that nothing reached the speakers.

Used by capture.py around the launcher's --audio run; the launcher does the
routing (a null sink made the default before the client starts, put back
after) and kills the client if a stream leaves it. This is the evidence, kept
independently of the launcher:

  sound-samples.jsonl  every 0.5 s, from before the client starts until after
                       the launcher has put the sound back: the default sink,
                       the configured default, every playback stream (pactl's
                       sink-inputs) with its sink, and whether a factorio
                       process is running.
  pw-links.json        every PipeWire link that existed or was made while the
                       guard ran, each with the nodes at its two ends, from
                       pw-dump --monitor (its raw log kept as pw-dump.json.gz).
  sound-guard.json     the verdict (judge()).

Every helper it starts (pactl, pw-metadata, pw-dump) runs in a session of its
own, so a Ctrl-C at the terminal reaches only capture.py, which then stops
them itself; none is left behind and none dies half-way through a reading.
start() and stop() may each be called at any point, any number of times, and
judge() reports a record cut short as incomplete rather than raising.
"""

import gzip
import json
import re
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

CLIENT = re.compile(r"factorio", re.I)
UNREAD_MAX = 0.10     # the share of samples while the client ran that may fail to read the default


def _run(cmd, tries=3):
    """A helper's output, or None if it failed every try. Its own session, so a
    terminal Ctrl-C cannot kill it mid-reading; stopped here, by PID, if it
    hangs or this process is interrupted while it runs."""
    for _ in range(tries):
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                                    start_new_session=True)
        except OSError:
            return None
        try:
            out, _ = proc.communicate(timeout=5)
        except BaseException:
            proc.kill()
            proc.wait()
            if not isinstance(sys.exc_info()[1], subprocess.TimeoutExpired):
                raise
            continue
        if proc.returncode == 0:
            return out
    return None


def factorio_pids():
    pids = []
    for d in Path("/proc").iterdir():
        if d.name.isdigit():
            try:
                if (d / "comm").read_text().strip() == "factorio":
                    pids.append(int(d.name))
            except OSError:
                pass
    return pids


def snapshot():
    sinks = {}
    try:
        for s in json.loads(_run(["pactl", "-f", "json", "list", "sinks"]) or "[]"):
            sinks[s["index"]] = s["name"]
    except ValueError:
        pass
    inputs = []
    try:
        for i in json.loads(_run(["pactl", "-f", "json", "list", "sink-inputs"]) or "[]"):
            p = i.get("properties", {})
            inputs.append({"index": i["index"], "sink": i["sink"], "sink_name": sinks.get(i["sink"]),
                           "app": p.get("application.name"), "binary": p.get("application.process.binary"),
                           "pid": p.get("application.process.id"), "media": p.get("media.name")})
    except ValueError:
        pass
    conf = re.search(r"value:'([^']*)'", _run(["pw-metadata", "0", "default.configured.audio.sink"]) or "")
    default = _run(["pactl", "get-default-sink"])
    # None, not "", when it could not be read: an unread default is no evidence
    # either way, and is counted as such.
    return {"t": time.time(), "default": default.strip() if default else None,
            "configured": conf.group(1) if conf else None,
            "factorio": factorio_pids(), "inputs": inputs}


def is_client_input(i, fpid):
    return (CLIENT.search(i.get("binary") or "") or CLIENT.search(i.get("app") or "")
            or (fpid is not None and str(i.get("pid")) == str(fpid)))


class SoundGuard:
    def __init__(self, out):
        self.out = Path(out)
        self.run_dir = None
        self.fpid = None
        self.before = self.after = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._thread = None
        self._dump = None
        self._dump_file = None
        self._samples = None
        self._started = self._stopped = False

    def _write(self, row):
        with self._lock:
            if self._samples is not None:
                self._samples.write(json.dumps(row) + "\n")
                self._samples.flush()

    def start(self):
        """Each part is recorded as soon as it exists, so stop() finds whatever
        an interrupt left half-started."""
        if self._started:
            return
        self._started = True
        self._samples = open(self.out / "sound-samples.jsonl", "w")
        self.before = snapshot()
        self._write({"phase": "before", **self.before})
        self._dump_file = open(self.out / "pw-dump.json", "w")
        self._dump = subprocess.Popen(["pw-dump", "--monitor", "--no-colors"], stdout=self._dump_file,
                                      stderr=subprocess.DEVNULL, start_new_session=True)
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        self._thread = thread     # only once it runs: stop() joins only a started thread

    def _loop(self):
        while not self._stop.wait(0.5):
            self._write({"phase": "during", **snapshot()})

    def stop(self):
        """Safe at any point after start() began, and more than once."""
        if not self._started or self._stopped:
            return
        self._stopped = True
        self._stop.set()
        if self._thread is not None and self._thread.is_alive():
            # A round of readings is at most 4 helpers x 3 tries x 5 s; wait it
            # out, so no helper outlives the guard.
            self._thread.join(timeout=70)
        if self.before is not None:
            self.after = snapshot()
            self._write({"phase": "after", **self.after})
        if self._dump is not None:
            self._dump.send_signal(signal.SIGINT)
            try:
                self._dump.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._dump.kill()
                self._dump.wait(timeout=5)
        for f in (self._dump_file, self._samples):
            if f is not None:
                with self._lock:
                    f.close()
        self._samples = None

    def helpers_left(self):
        """PIDs this guard started that are still running (pw-dump; the sampler
        thread's helpers end with the thread)."""
        return [self._dump.pid] if self._dump is not None and self._dump.poll() is None else []

    # ------------------------------------------------------------ PipeWire links

    def links(self):
        """Every link seen in the pw-dump log, with its end nodes' names as they were."""
        path, gz = self.out / "pw-dump.json", self.out / "pw-dump.json.gz"
        if path.exists():
            text = path.read_text(errors="replace")
        elif gz.exists():
            text = gzip.decompress(gz.read_bytes()).decode(errors="replace")
        else:
            text = ""
        dec = json.JSONDecoder()
        nodes, seen, pos = {}, {}, 0
        while True:
            m = re.compile(r"\S").search(text, pos)
            if not m:
                break
            try:
                batch, pos = dec.raw_decode(text, m.start())
            except ValueError:
                break   # a last batch cut short when pw-dump was stopped
            for o in batch if isinstance(batch, list) else [batch]:
                oid, info = o.get("id"), o.get("info")
                if info is None:
                    nodes.pop(oid, None)
                    continue
                if o.get("type") == "PipeWire:Interface:Node":
                    props = info.get("props") or {}
                    old = nodes.get(oid, {})
                    nodes[oid] = {**old, **{k: props[k] for k in (
                        "node.name", "application.name", "application.process.binary",
                        "application.process.id", "media.class", "media.name") if k in props}}
                elif o.get("type") == "PipeWire:Interface:Link":
                    a, b = info.get("output-node-id"), info.get("input-node-id")
                    if a is None or b is None:
                        continue
                    key = (oid, a, b)
                    if key not in seen:
                        seen[key] = {"link": oid, "from_id": a, "to_id": b,
                                     "from": dict(nodes.get(a, {})), "to": dict(nodes.get(b, {}))}
        if path.exists():
            with open(path, "rb") as f, gzip.open(self.out / "pw-dump.json.gz", "wb") as g:
                g.write(f.read())
            path.unlink()
        return list(seen.values())

    # ------------------------------------------------------------ verdict

    def judge(self):
        """The verdict; a record cut short (no before or after reading, no
        samples file) is reported as incomplete, and fails, rather than raised."""
        try:
            return self._judge()
        except (OSError, ValueError, KeyError, TypeError) as e:
            verdict = {"pass": False, "incomplete": True, "problems": [f"incomplete record: {e!r}"],
                       "summary": f"incomplete record ({e!r}): nothing is shown either way"}
            try:
                (self.out / "sound-guard.json").write_text(json.dumps(verdict, indent=1))
            except OSError:
                pass
            return verdict

    def _judge(self):
        null = None
        run = {}
        if self.run_dir and (Path(self.run_dir) / "run.json").exists():
            run = json.loads((Path(self.run_dir) / "run.json").read_text())
            null = (run.get("audio") or {}).get("null_sink")
        samples = [json.loads(line) for line in open(self.out / "sound-samples.jsonl")]
        during = [s for s in samples if s["phase"] == "during" and s["factorio"]]
        problems = []
        b, a = self.before, self.after
        if b is None or a is None or b["default"] is None or a["default"] is None:
            raise ValueError("the default sink was not read both before and after the run")
        if not null:
            problems.append("no null sink in the run's run.json")
        if b["default"] != a["default"] or b["configured"] != a["configured"]:
            problems.append(f"default before {b['default']} ({b['configured']}) != after {a['default']} "
                            f"({a['configured']})")
        if null and b["default"] == null:
            problems.append("the default was already the null sink before the run")
        if not during:
            problems.append("no sample was taken while the client ran")
        # An unread default is no evidence either way: the run has to have read
        # it in at least 90 % of the samples taken while the client ran.
        unread = [s for s in during if s["default"] is None]
        if during and len(unread) == len(during):
            problems.append(f"no sample read the default while the client ran (0 of {len(during)})")
        elif during and len(unread) > UNREAD_MAX * len(during):
            problems.append(f"{len(unread)} of {len(during)} samples while the client ran could not read the "
                            f"default (more than {UNREAD_MAX:.0%})")
        off_default = [s for s in during if s["default"] is not None and s["default"] != null]
        if off_default:
            problems.append(f"{len(off_default)} samples while the client ran had the default "
                            f"{sorted({s['default'] for s in off_default})}")
        streams, off_streams = {}, []
        for s in during:
            for i in s["inputs"]:
                if is_client_input(i, self.fpid):
                    streams.setdefault(i["index"], set()).add(i["sink_name"])
                    if i["sink_name"] != null:
                        off_streams.append((s["t"], i))
        if not streams:
            problems.append("no client stream was seen in any sample")
        if off_streams:
            problems.append(f"{len(off_streams)} sample(s) had a client stream off the null sink")
        links = self.links()

        def client_node(n):
            return (CLIENT.search(n.get("application.process.binary") or "")
                    or CLIENT.search(n.get("application.name") or "")
                    or (self.fpid is not None and str(n.get("application.process.id")) == str(self.fpid)))
        client_links = [lk for lk in links if client_node(lk["from"])]
        bad_links = [lk for lk in client_links if lk["to"].get("node.name") != null]
        if not client_links:
            problems.append("no PipeWire link from a client node was seen")
        if bad_links:
            problems.append(f"{len(bad_links)} PipeWire link(s) ran from a client node to something else: "
                            + ", ".join(sorted({str(lk['to'].get('node.name')) for lk in bad_links})))
        (self.out / "pw-links.json").write_text(json.dumps(links, indent=1))
        verdict = {
            "pass": not problems,
            "null_sink": null,
            "default_before": {"default": b["default"], "configured": b["configured"]},
            "default_after": {"default": a["default"], "configured": a["configured"]},
            "default_during": sorted({s["default"] for s in during if s["default"] is not None}),
            "samples_while_client_ran": len(during),
            "samples_default_unread": len(unread),
            "client_streams": {str(k): sorted(map(str, v)) for k, v in streams.items()},
            "client_links": [{"link": lk["link"], "from": lk["from"].get("node.name") or lk["from"].get(
                "application.name"), "to": lk["to"].get("node.name")} for lk in client_links],
            "launcher_audio": run.get("audio"),
            "problems": problems,
        }
        verdict["summary"] = (
            f"default {b['default']} before, {verdict['default_during']} in {len(during)} samples while the "
            f"client ran, {a['default']} after; client streams {verdict['client_streams']}; "
            f"{len(client_links)} client link(s), all to {null}"
            + (f"; {len(unread)} sample(s) could not read the default" if unread else "")
            if not problems else "; ".join(problems))
        (self.out / "sound-guard.json").write_text(json.dumps(verdict, indent=1))
        return verdict


if __name__ == "__main__":
    # Re-judge an evidence folder: guard.py <audio-dir> <launcher-run-dir> [factorio-pid]
    g = SoundGuard(sys.argv[1])
    g.run_dir = sys.argv[2]
    g.fpid = int(sys.argv[3]) if len(sys.argv) > 3 else None
    rows = [json.loads(line) for line in open(Path(sys.argv[1]) / "sound-samples.jsonl")]
    g.before = next((r for r in rows if r["phase"] == "before"), None)
    g.after = next((r for r in rows if r["phase"] == "after"), None)
    print(json.dumps(g.judge(), indent=1))
