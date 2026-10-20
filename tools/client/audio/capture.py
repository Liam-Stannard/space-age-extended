#!/usr/bin/env python3
"""tools/client/audio/capture.py -- record a working building's sound against
its picture in a real client, and time its sound accents from the recording.

Usage:
  python3 tools/client/audio/capture.py --task NAME --spec FILE [--worktree DIR]
                                        [--timeout S] [--keep-raw] [--mod PATH]

  --task NAME     Evidence goes to <repo>/evidence/NAME/: the launcher's two run
                  directories (client-*) and this tool's own, audio-<stamp>-<pid>/,
                  which holds the MP4, accents.json and the sound guard's record.
  --spec FILE     What to record, as JSON (example: specs/drop-crusher.json):
                    entity, planet, tile, recipe, items [{name, count}]: the
                                  machine, where it stands and what it is fed
                                  (topped up every 30 ticks; output emptied)
                    supply_kw     the hidden supply, on from the first
                    daytime, zoom the fixed light (0 noon) and the camera's zoom
                    ready_after   ticks from the probe's start to `ready`
                    markers       {after_ready: [ticks...], offset: [x, y] tiles
                                  from the machine, size tiles, ticks_shown, sound}
                    start_after   ticks from `ready` to the ingredients going in
                    work_ticks    ticks recorded with the machine working
                    capture       {width, height, fps, rate}: the window's middle
                                  grabbed, and the audio's sample rate
                    mp4           {lead_seconds, video_bitrate, audio_bitrate}
                    stroke        the animation the accents count: its sheet
                                  (repo path), width, height, frame_count,
                                  line_length, shift, scale, as the prototype has it
                    sounds        {label: repo path}: the accents' sound files
                    expect        {accents: [{sound, frame}], tolerance_frames}:
                                  used only to judge what was measured
                    name          the MP4's name (<name>.mp4)
                    onset_rise_db optional: what counts as an onset (35; see
                                  analyse.py)
  --worktree DIR  The mod to load (default: this repo), as the launcher's.
  --mod PATH      An extra mod, as the launcher's. Repeatable.
  --timeout S     The recording run's limit in seconds (default 600).
  --keep-raw      Keep the raw capture (raw/: RGB frames and PCM, ~30 MB/s).

How it runs. Only through tools/client/launch.sh, twice: once to --create a
save with the probe mod (tools/client/audio/mod, copied to a scratch folder
with the spec beside it as config.lua), and once, in the launcher's --audio
mode, to load it. The launcher makes a null sink the default before the
client starts and puts the default back after; it records nothing itself.
When the probe writes `ready` (the machine built and idle, the camera on it),
this tool records, in one GStreamer pipeline on one clock:
  - the middle of the client's window (ximagesrc on the run's Xvfb display,
    capture.width x capture.height at capture.fps), and
  - the null sink's monitor (pulsesrc on run.json's audio.monitor),
each buffer kept with its timestamp. When the probe writes `enough`, the
recording stops and this tool writes the launcher's done-file, so the client
is stopped and the sound put back. analyse.py then times the accents and
writes the MP4 (see its header for how frames are mapped to time).

The sound guard. From before the client starts until after the launcher has
put the sound back, the default sink and every playback stream (pactl) are
sampled every 0.5 s into sound-samples.jsonl, and every PipeWire link made is
logged as it happens (pw-dump --monitor, kept gzipped). sound-guard.json then
judges: the default before and after are the same real sink; it was the null
sink in every sample while the client ran; every client stream was on the null
sink in every sample; and no PipeWire link ever ran from a client node to
anything but the null sink.

Exit: 0 recorded, analysed, every accent on its frame and the guard passed;
1 something failed or an accent missed (see the output); 2 usage; 3 the
launcher refused (another client running).
"""

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
LAUNCH = REPO / "tools/client/launch.sh"
sys.path.insert(0, str(HERE))
import analyse  # noqa: E402
import guard  # noqa: E402


class Failed(Exception):
    pass


def say(msg):
    print(f"capture: {msg}", flush=True)


def wait_for(cond, seconds, what, alive=None, step=0.05):
    """Poll cond() until true, at most `seconds`; give up early if alive() is false."""
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        v = cond()
        if v:
            return v
        if alive is not None and not alive():
            raise Failed(f"the launcher ended while waiting for {what}")
        time.sleep(step)
    raise Failed(f"timed out after {seconds:.0f} s waiting for {what}")


# ---------------------------------------------------------------- the recorder

class Recorder:
    """The window's middle and the null sink's monitor, on one pipeline clock.

    Every buffer is written raw as it arrives, with its timestamp (running time
    of the pipeline, in ns): raw/video.rgb (RGB24 frames) + video.json, and
    raw/audio.s16 (S16LE interleaved) + audio.json. Nothing is encoded while
    the client runs, so the recording takes as little CPU from it as it can.
    """

    def __init__(self, raw, display, xauth, box, fps, monitor, rate):
        self.raw = raw
        x, y, w, h = box
        self.w, self.h, self.rate = w, h, rate
        # ximagesrc opens the display through Xlib, which reads XAUTHORITY.
        os.environ["XAUTHORITY"] = xauth
        desc = (
            f"ximagesrc name=vsrc display-name={display} use-damage=false show-pointer=false "
            f"startx={x} starty={y} endx={x + w - 1} endy={y + h - 1} "
            f"! video/x-raw,framerate={fps}/1 ! videoconvert ! video/x-raw,format=RGB,width={w},height={h} "
            f"! appsink name=vsink emit-signals=true sync=false "
            f"pulsesrc name=asrc device={monitor} client-name=sae-audio-capture "
            f"! audioconvert ! audioresample ! audio/x-raw,format=S16LE,rate={rate},channels=2,layout=interleaved "
            f"! appsink name=asink emit-signals=true sync=false"
        )
        self.desc = desc
        self.pipe = Gst.parse_launch(desc)
        self.vf = open(raw / "video.rgb", "wb")
        self.af = open(raw / "audio.s16", "wb")
        self.vts, self.ats = [], []
        self.lock = threading.Lock()
        self.errors = []
        self.pipe.get_by_name("vsink").connect("new-sample", self._video)
        self.pipe.get_by_name("asink").connect("new-sample", self._audio)

    def _take(self, sink, f, ts, unit):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        ok, info = buf.map(Gst.MapFlags.READ)
        if not ok:
            self.errors.append("could not map a buffer")
            return Gst.FlowReturn.ERROR
        try:
            data = bytes(info.data)
        finally:
            buf.unmap(info)
        with self.lock:
            f.write(data)
            ts.append({"pts": buf.pts, "n": len(data) // unit,
                       "discont": bool(buf.get_flags() & Gst.BufferFlags.DISCONT)})
        return Gst.FlowReturn.OK

    def _video(self, sink):
        return self._take(sink, self.vf, self.vts, self.w * self.h * 3)

    def _audio(self, sink):
        return self._take(sink, self.af, self.ats, 4)

    def start(self):
        if self.pipe.set_state(Gst.State.PLAYING) == Gst.StateChangeReturn.FAILURE:
            raise Failed("the recording pipeline would not start")
        self.check()

    def check(self):
        bus = self.pipe.get_bus()
        while True:
            m = bus.pop_filtered(Gst.MessageType.ERROR)
            if not m:
                break
            err, dbg = m.parse_error()
            self.errors.append(f"{err.message} ({dbg})")
        if self.errors:
            raise Failed("recording: " + "; ".join(self.errors))

    def stop(self):
        if self.pipe is None:
            return
        self.pipe.send_event(Gst.Event.new_eos())
        bus = self.pipe.get_bus()
        bus.timed_pop_filtered(5 * Gst.SECOND, Gst.MessageType.EOS | Gst.MessageType.ERROR)
        self.pipe.set_state(Gst.State.NULL)
        self.pipe = None
        with self.lock:
            self.vf.close()
            self.af.close()
        (self.raw / "video.json").write_text(json.dumps(
            {"width": self.w, "height": self.h, "format": "RGB", "frames": self.vts}))
        (self.raw / "audio.json").write_text(json.dumps(
            {"rate": self.rate, "channels": 2, "format": "S16LE", "buffers": self.ats}))


# ---------------------------------------------------------------- the client

def client_env(pid):
    env = {}
    raw = Path(f"/proc/{pid}/environ").read_bytes()
    for item in raw.split(b"\0"):
        k, _, v = item.partition(b"=")
        env[k.decode(errors="replace")] = v.decode(errors="replace")
    return env


def factorio_window(display, xauth):
    """The client's window on the Xvfb display: (x, y, w, h), root coordinates."""
    out = subprocess.run(["xwininfo", "-root", "-tree", "-display", display],
                         capture_output=True, text=True, timeout=10,
                         env={**os.environ, "XAUTHORITY": xauth, "DISPLAY": display}).stdout
    best = None
    for line in out.splitlines():
        if "actorio" not in line:
            continue
        m = re.search(r"(\d+)x(\d+)[+-]-?\d+[+-]-?\d+\s+\+(-?\d+)\+(-?\d+)\s*$", line)
        if m:
            w, h, x, y = (int(v) for v in m.groups())
            if best is None or w * h > best[2] * best[3]:
                best = (x, y, w, h)
    return best


def launch(args, extra, log_path):
    """Start the launcher in its own session: a Ctrl-C here reaches only this
    tool, which then stops the launcher once (SIGINT), the way it asks to be
    stopped, never with the SIGKILL subprocess.run would send."""
    cmd = [str(LAUNCH), "--task", args.task, "--worktree", args.worktree, *extra]
    say("launch.sh " + " ".join(cmd[1:]))
    f = open(log_path, "w")
    return subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, start_new_session=True), f


def run_dir_of(log_path):
    m = re.search(r" run dir: (\S+)", Path(log_path).read_text(errors="replace"))
    return Path(m.group(1)) if m else None


def stop_launcher(proc, seconds=90):
    if proc is None or proc.poll() is not None:
        return
    say(f"stopping the launcher {proc.pid} (SIGINT)")
    proc.send_signal(signal.SIGINT)
    try:
        proc.wait(timeout=seconds)
    except subprocess.TimeoutExpired:
        say(f"the launcher {proc.pid} is still up; SIGTERM")
        proc.terminate()
        proc.wait(timeout=30)


def probe_errors(out_dir):
    e = out_dir / "errors.txt"
    if e.exists() and e.read_text().strip():
        raise Failed("the probe caught errors:\n" + e.read_text())


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--task", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--worktree", default=str(REPO))
    ap.add_argument("--mod", action="append", default=[])
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--keep-raw", action="store_true")
    args = ap.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9._-]+", args.task):
        ap.error("--task must be letters, digits, . _ -")
    spec_text = Path(args.spec).read_text()
    spec = json.loads(spec_text)
    for k in ("entity", "markers", "start_after", "work_ticks", "capture", "stroke", "sounds"):
        if k not in spec:
            ap.error(f"the spec has no '{k}'")
    if "]==]" in spec_text:
        ap.error("the spec may not contain ]==]")
    args.worktree = str(Path(args.worktree).resolve())
    extra_mods = [a for m in args.mod for a in ("--mod", m)]

    Gst.init(None)
    out = REPO / "evidence" / args.task / f"audio-{time.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}"
    raw = out / "raw"
    raw.mkdir(parents=True)
    say(f"evidence: {out}")
    shutil.copy(args.spec, out / "spec.json")

    # Signals become exceptions, so the finally below always runs.
    def on_signal(signum, _frame):
        raise KeyboardInterrupt(f"signal {signum}")
    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGHUP, on_signal)

    scr = Path(tempfile.mkdtemp(prefix="sae-audio."))
    proc = logf = rec = snd = None
    run_dir = None
    rc = 1
    try:
        mod = scr / "sae-audio"
        shutil.copytree(HERE / "mod", mod)
        (mod / "config.lua").write_text("return [==[" + json.dumps(spec) + "]==]\n")

        say("creating the save")
        proc, logf = launch(args, [*extra_mods, "--mod", str(mod), "--timeout", "300",
                                   "--", "--create", str(scr / "audio.zip")], out / "launch-create.log")
        r = proc.wait(timeout=400)
        logf.close()
        proc = logf = None
        if r == 3:
            say("the launcher refused (a client is running); see launch-create.log")
            return 3
        if r != 0 or not (scr / "audio.zip").exists():
            raise Failed(f"creating the save failed (launcher exit {r}; see {out / 'launch-create.log'})")

        snd = guard.SoundGuard(out)
        snd.start()
        say(f"sound before: default {snd.before['default']}")
        proc, logf = launch(args, [*extra_mods, "--mod", str(mod), "--audio", "--timeout", str(args.timeout),
                                   "--done-file", "sae-audio/stop", "--", "--load-game", str(scr / "audio.zip")],
                            out / "launch-record.log")
        alive = lambda: proc.poll() is None  # noqa: E731
        run_dir = wait_for(lambda: run_dir_of(out / "launch-record.log"), 30, "the run directory", alive)
        snd.run_dir = run_dir
        say(f"client run: {run_dir}")
        probe_out = run_dir / "data/script-output/sae-audio"
        run_json = run_dir / "run.json"

        def client_up():
            try:
                j = json.loads(run_json.read_text())
            except (OSError, ValueError):
                return None
            return j if j.get("factorio_pid") and (j.get("audio") or {}).get("monitor") else None
        j = wait_for(client_up, 120, "the client", alive)
        fpid = j["factorio_pid"]
        snd.fpid = fpid
        monitor = j["audio"]["monitor"]
        wait_for(lambda: (probe_out / "ready").exists() or (probe_out / "errors.txt").exists(),
                 300, "the probe's `ready`", alive)
        probe_errors(probe_out)
        env = client_env(fpid)
        display, xauth = env.get("DISPLAY"), env.get("XAUTHORITY")
        if not display or not xauth:
            raise Failed(f"no DISPLAY/XAUTHORITY in factorio {fpid}'s environment")
        win = factorio_window(display, xauth)
        if not win:
            raise Failed(f"no Factorio window on {display}")
        cap = spec["capture"]
        cw, ch = cap["width"], cap["height"]
        if cw > win[2] or ch > win[3]:
            raise Failed(f"capture {cw}x{ch} is larger than the window {win[2]}x{win[3]}")
        box = (win[0] + (win[2] - cw) // 2, win[1] + (win[3] - ch) // 2, cw, ch)
        geometry = {"display": display, "window": dict(zip("xywh", win)), "box": dict(zip("xywh", box)),
                    "camera_px_in_box": [win[0] + win[2] / 2 - box[0], win[1] + win[3] / 2 - box[1]],
                    "monitor": monitor, "factorio_pid": fpid}
        say(f"window {win[2]}x{win[3]}+{win[0]}+{win[1]} on {display}; recording {cw}x{ch}+{box[0]}+{box[1]}"
            f" and {monitor}")

        rec = Recorder(raw, display, xauth, box, cap.get("fps", 30), monitor, cap.get("rate", 48000))
        rec.start()
        geometry["pipeline"] = rec.desc
        (out / "geometry.json").write_text(json.dumps(geometry, indent=1))
        work_s = (spec["start_after"] + spec["work_ticks"]) / 60
        wait_for(lambda: (rec.check() or (probe_out / "enough").exists() or (probe_out / "errors.txt").exists()),
                 work_s * 3 + 30, "the probe's `enough`", alive)
        rec.stop()
        rec = None
        probe_errors(probe_out)
        say("recorded; stopping the client")
        (probe_out / "stop").write_text("stop\n")
        try:
            lrc = proc.wait(timeout=120)
        except subprocess.TimeoutExpired:
            raise Failed("the launcher did not stop within 120 s of the done-file")
        say(f"launcher exit {lrc}")
        if lrc != 0:
            raise Failed(f"the recording run ended with launcher exit {lrc} (see launch-record.log)")
        rc = 0
    except Failed as e:
        say(f"FAILED: {e}")
        rc = 1
    except KeyboardInterrupt as e:
        say(f"interrupted ({e}); cleaning up")
        rc = 130
    except subprocess.TimeoutExpired:
        say("FAILED: the launcher outlived its own timeout")
        rc = 1
    finally:
        # The cleanup is bounded (the recorder 5 s, the launcher 120 s, the
        # guard 15 s) and must finish: further signals are ignored while it runs.
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            signal.signal(sig, signal.SIG_IGN)
        if rec is not None:
            rec.stop()
        stop_launcher(proc)
        if logf:
            logf.close()
        if snd is not None:
            snd.stop()
        shutil.rmtree(scr, ignore_errors=True)
        if run_dir is not None:
            for name in ("status.jsonl", "log.txt", "errors.txt"):
                p = run_dir / "data/script-output/sae-audio" / name
                if p.exists():
                    shutil.copy(p, out / f"probe-{name}")

    verdict = 1
    g = {"pass": False}
    if snd is not None:
        try:
            g = snd.judge()
            say(f"sound guard: {'PASS' if g['pass'] else 'FAIL'} -- {g['summary']}")
        except (OSError, ValueError, KeyError) as e:
            say(f"sound guard FAILED to judge: {e!r}")
    if rc == 0:
        try:
            res = analyse.run(out, spec, REPO)
            say(f"accents: {'PASS' if res['pass'] else 'FAIL'} -- {res['summary']}")
            say(f"MP4: {res['mp4']}")
            verdict = 0 if res["pass"] and g["pass"] else 1
        except analyse.Failed as e:
            say(f"analysis FAILED: {e}")
    if verdict == 0 and not args.keep_raw:
        shutil.rmtree(raw, ignore_errors=True)
    say(f"evidence: {out}")
    return rc if rc != 0 else verdict


if __name__ == "__main__":
    sys.exit(main())
