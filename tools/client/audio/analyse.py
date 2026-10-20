#!/usr/bin/env python3
"""tools/client/audio/analyse.py -- time a building's sound accents from a
capture.py recording, and write the MP4.

  python3 tools/client/audio/analyse.py <audio-dir>     (re-run on a kept raw/)

Inputs, all in <audio-dir> (capture.py writes them): raw/video.rgb +
video.json, raw/audio.s16 + audio.json, geometry.json, spec.json,
probe-status.jsonl. Pure Python with Pillow and GStreamer (gi); no numpy.

**One clock.** Every video frame and every audio buffer carries its timestamp
from the one GStreamer pipeline that recorded both (its running time, in
nanoseconds). A video frame's time is its own timestamp; an audio sample's is
its buffer's timestamp plus its place in the buffer over the sample rate.
Every time below is on that clock, in seconds.

**Which animation frame is on screen** is read from the picture, never from
the prototype's accent frames. The stroke sheet (spec.stroke) is cut into its
frames and scaled as the engine draws them (scale x zoom), and each recorded
frame is compared with every one of them where that sheet frame is opaque
(mean absolute luminance difference, the sprite placed by its shift from the
camera, which sits on the machine, then registered by a small search). The
best is the frame shown. Over the working part of the recording the shown
frame is unwrapped (it only ever steps forward, 0 to 23 and round) and a line
fitted to it: phase(t) = rate x t + c, phase + 0.5 being the middle of a frame
shown from phase's whole number to the next. So any time t maps to a
fractional animation frame, phase(t) mod frame_count; the frame shown at t is
its whole part. The fit's residuals and the frames that disagree with it are
reported. Each onset also carries frame_in_last_grab, the frame matched in the
last video grab at or before it: the picture itself, not the fit, so it can
trail the phase by up to one grab (1/fps).

**Where the sounds start** is read from the audio alone. The mono mix is split
into three bands (below 250 Hz, 250-2500 Hz, above 2500 Hz); each band's RMS
is taken every 2 ms; the rise at each step is how far each band's level
stands above its own median 6-50 ms before, summed over the bands, in dB. An
onset is a rise that is the highest within +-30 ms and at least
spec.onset_rise_db (35 dB by default: in the runs so far the crusher's
accents rose 37.6-81.7, the bed's own beat 10-31, the drop's grit tail up to
35.6 and the bed starting up 46.7 -- so some that are not accents clear it;
they match no file, are reported as "unknown", and are never judged), its
time the first 2 ms step of that rise to reach half of it. Each onset is then labelled by the
sound file it matches best
(spec.sounds): the same bands and steps worked out on each file, correlated
(normalised, per band, weighted by the file's own band energy) against the
recording over 400 ms from the onset, allowing the file's own onset to sit
within +-16 ms of it. An onset that matches no file at 0.5 or better is
"unknown". The labels say only which sound it is; the times are the
recording's.

**Accents.** Each labelled onset's phase gives the frame it sounded on. The
markers (a flash and a click the probe starts on one tick, before the machine
starts) measure the recording chain: the strongest onset within -0.25..+0.35 s
of each flash is its click, and the click's onset minus the flash's first
recorded frame is the delay of the sound behind the picture through the
engine, the sinks and the capture (to the video's 1/fps). It is reported, and
the frame each accent lands on is given both as recorded and with that delay
taken off; only the recorded one is judged. The two markers' tick gap over
their time gap also gives the game's seconds a tick, which places the start
(the ingredients going in, a tick the probe logs) on the clock.

Judged against spec.expect (and only there). An accent cued on frame F should
start as frame F starts, at phase F, so its error is phase - F in frames
(negative: it sounded before frame F was on screen). Pass: every expected
accent found on every pass of its frame from the start on (the first stroke
after start-up included), each within tolerance_frames as recorded, and no
labelled onset anywhere else.
"""

import json
import math
import sys
import time
from array import array
from pathlib import Path

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

HOP_S = 0.002
BANDS = (("low", None, 250.0), ("mid", 250.0, 2500.0), ("high", 2500.0, None))
WINDOW_S = 0.4
MATCH_MIN = 0.5
ONSET_DB = 35.0       # the default rise, summed over the bands, that counts as an onset
NMS_HOPS = 15         # +-30 ms


class Failed(Exception):
    pass


# ---------------------------------------------------------------- audio DSP

def biquad(x, kind, f0, fs, q=0.7071):
    """One RBJ-cookbook low- or high-pass section over a list of floats."""
    w = 2 * math.pi * f0 / fs
    c, s = math.cos(w), math.sin(w)
    alpha = s / (2 * q)
    if kind == "lp":
        b0, b1, b2 = (1 - c) / 2, 1 - c, (1 - c) / 2
    else:
        b0, b1, b2 = (1 + c) / 2, -(1 + c), (1 + c) / 2
    a0, a1, a2 = 1 + alpha, -2 * c, 1 - alpha
    b0, b1, b2, a1, a2 = b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0
    y = [0.0] * len(x)
    x1 = x2 = y1 = y2 = 0.0
    for i, v in enumerate(x):
        o = b0 * v + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, v, y1, o
        y[i] = o
    return y


def band_envelopes(x, fs):
    """Each band's RMS every HOP_S, as lists. Fourth-order (two sections) edges."""
    hop = int(round(fs * HOP_S))
    out = {}
    for name, lo, hi in BANDS:
        y = x
        if lo:
            y = biquad(biquad(y, "hp", lo, fs), "hp", lo, fs)
        if hi:
            y = biquad(biquad(y, "lp", hi, fs), "lp", hi, fs)
        n = len(y) // hop
        out[name] = [math.sqrt(sum(v * v for v in y[k * hop:(k + 1) * hop]) / hop) for k in range(n)]
    return out


def decode(path, rate):
    """A sound file as mono floats at `rate`, through GStreamer."""
    pipe = Gst.parse_launch(
        "filesrc name=src ! decodebin ! audioconvert ! audioresample "
        f"! audio/x-raw,format=S16LE,rate={rate},channels=1,layout=interleaved ! appsink name=sink sync=false")
    pipe.get_by_name("src").set_property("location", str(path))
    sink = pipe.get_by_name("sink")
    pipe.set_state(Gst.State.PLAYING)
    data = bytearray()
    while True:
        sample = sink.emit("try-pull-sample", 10 * Gst.SECOND)
        if sample is None:
            break
        buf = sample.get_buffer()
        ok, info = buf.map(Gst.MapFlags.READ)
        if ok:
            data += bytes(info.data)
            buf.unmap(info)
    pipe.set_state(Gst.State.NULL)
    if not data:
        raise Failed(f"could not decode {path}")
    a = array("h")
    a.frombytes(bytes(data))
    return [v / 32768.0 for v in a]


def db(v):
    return 20 * math.log10(v + 1e-7)


def onsets(env, t0, threshold=ONSET_DB):
    """Template-free onsets: (time, hop, rise in dB summed over bands, level dB)."""
    names = [b[0] for b in BANDS]
    n = len(env[names[0]])
    L = {b: [db(v) for v in env[b]] for b in names}
    back0, back1 = 3, 25     # 6-50 ms before
    strength = [0.0] * n
    for k in range(back1, n):
        s = 0.0
        for b in names:
            past = L[b][k - back1:k - back0]
            ref = sorted(past)[len(past) // 2]
            s += max(0.0, L[b][k] - ref)
        strength[k] = s
    # A peak is the highest rise within +-NMS_HOPS (30 ms) of itself. No step
    # is skipped after one is found: a bed with a beat of its own (the
    # crusher's ticks every 64 ms) would otherwise set the grid and step over
    # the accent between two of its beats.
    found = []
    for k in range(back1, n):
        if strength[k] < threshold or strength[k] != max(strength[max(0, k - NMS_HOPS):k + NMS_HOPS + 1]):
            continue
        if found and found[-1]["peak_hop"] >= k - NMS_HOPS:
            continue         # a tie inside the same window
        # The rise's own start: back to the first step at half its height.
        half = strength[k] / 2
        m = k
        for _ in range(10):
            if strength[m - 1] < half:
                break
            m -= 1
        found.append({"t": t0 + m * HOP_S, "hop": m, "peak_hop": k, "rise_db": round(strength[k], 1),
                      "level_db": round(max(L[b][k] for b in names), 1)})
    return found


def template(x, fs):
    env = band_envelopes(x, fs)
    names = [b[0] for b in BANDS]
    w = int(round(WINDOW_S / HOP_S))
    total = [sum(env[b][k] for b in names) for k in range(len(env[names[0]]))]
    peak = max(total)
    onset = next(k for k, v in enumerate(total) if v >= 0.1 * peak)
    t = {}
    for b in names:
        seg = (env[b][onset:onset + w] + [0.0] * w)[:w]
        mean = sum(seg) / w
        z = [v - mean for v in seg]
        t[b] = (z, sum(v * v for v in z))
    energy = sum(t[b][1] for b in names) or 1.0
    return {"bands": t, "weights": {b: t[b][1] / energy for b in names}, "onset_hops": onset,
            "seconds": len(x) / fs}


def match(env, hop, tpl):
    """Weighted normalised correlation of the recording from `hop` with a template."""
    w = int(round(WINDOW_S / HOP_S))
    score = 0.0
    for b, (z, zz) in tpl["bands"].items():
        seg = env[b][hop:hop + w]
        if len(seg) < w or zz <= 0:
            return None
        mean = sum(seg) / w
        rr = sum((v - mean) ** 2 for v in seg)
        if rr <= 0:
            continue
        score += tpl["weights"][b] * sum(v * zv for v, zv in zip(seg, z)) / math.sqrt(rr * zz)
    return score


# ---------------------------------------------------------------- raw capture

def load_audio(raw):
    meta = json.loads((raw / "audio.json").read_text())
    rate = meta["rate"]
    a = array("h")
    a.frombytes((raw / "audio.s16").read_bytes())
    mono = [(a[i] + a[i + 1]) / 65536.0 for i in range(0, len(a) - 1, 2)]
    bufs = meta["buffers"]
    if not bufs:
        raise Failed("no audio was recorded")
    t0 = bufs[0]["pts"] / 1e9
    # The samples are taken as contiguous from the first buffer's time; how far
    # each buffer's own timestamp strays from that is the clock check.
    pos, worst = 0, 0.0
    discont = []
    for b in bufs:
        expect = t0 + pos / rate
        worst = max(worst, abs(b["pts"] / 1e9 - expect))
        if b["discont"] and pos:
            discont.append(round(b["pts"] / 1e9, 4))
        pos += b["n"]
    return {"rate": rate, "mono": mono, "left_right": a, "t0": t0, "worst_drift_s": worst,
            "discont": discont, "buffers": len(bufs)}


class Video:
    def __init__(self, raw):
        meta = json.loads((raw / "video.json").read_text())
        self.w, self.h = meta["width"], meta["height"]
        self.size = self.w * self.h * 3
        self.t = [f["pts"] / 1e9 for f in meta["frames"]]
        self.f = open(raw / "video.rgb", "rb")

    def image(self, i):
        self.f.seek(i * self.size)
        return Image.frombytes("RGB", (self.w, self.h), self.f.read(self.size))

    def frame_bytes(self, i):
        self.f.seek(i * self.size)
        return self.f.read(self.size)


# ---------------------------------------------------------------- which frame is shown

class Stroke:
    """The sheet's frames as the engine draws them, and the box they sit in."""

    def __init__(self, spec, geometry, repo, margin=8):
        st = spec["stroke"]
        zoom = spec.get("zoom", 1)
        k = st["scale"] * zoom
        sheet = Image.open(repo / st["filename"]).convert("RGBA")
        self.n = st["frame_count"]
        sw, sh = max(1, round(st["width"] * k)), max(1, round(st["height"] * k))
        cam = geometry["camera_px_in_box"]
        px = 32 * zoom
        cx, cy = cam[0] + st["shift"][0] * px, cam[1] + st["shift"][1] * px
        self.x0, self.y0 = int(round(cx - st["width"] * k / 2)), int(round(cy - st["height"] * k / 2))
        self.margin = margin
        self.box = (self.x0 - margin, self.y0 - margin, self.x0 + sw + margin, self.y0 + sh + margin)
        self.bw = self.box[2] - self.box[0]
        self.frames = []
        self.pictures = []
        for i in range(self.n):
            col, row = i % st["line_length"], i // st["line_length"]
            fr = sheet.crop((col * st["width"], row * st["height"], (col + 1) * st["width"], (row + 1) * st["height"]))
            fr = fr.resize((sw, sh), Image.BOX)
            self.pictures.append(fr)
            lum = fr.convert("RGB").convert("L").tobytes()
            alpha = fr.getchannel("A").tobytes()
            pts = [(y, x, lum[y * sw + x]) for y in range(sh) for x in range(sw) if alpha[y * sw + x] >= 250]
            self.frames.append(pts)
        self.sw, self.sh = sw, sh

    def roi(self, img):
        return img.crop(self.box).convert("L").tobytes()

    def scores(self, roi, dx=0, dy=0, step=1):
        out = []
        m, bw = self.margin, self.bw
        for pts in self.frames:
            sel = pts[::step]
            tot = 0
            for y, x, v in sel:
                tot += abs(roi[(y + m + dy) * bw + x + m + dx] - v)
            out.append(tot / max(1, len(sel)))
        return out

    def register(self, rois, reach=6):
        """The offset (dx, dy) that best fits the sampled frames, coarse then fine."""
        def cost(dx, dy):
            return sum(min(self.scores(r, dx, dy, step=3)) for r in rois)
        best = min(((cost(dx, dy), dx, dy) for dx in range(-reach, reach + 1, 2)
                    for dy in range(-reach, reach + 1, 2)))
        _, bx, by = best
        best = min(((cost(dx, dy), dx, dy) for dx in range(bx - 1, bx + 2) for dy in range(by - 1, by + 2)
                    if abs(dx) <= reach + 1 and abs(dy) <= reach + 1))
        return best[1], best[2], best[0] / len(rois)


def unwrap_fit(times, best, n, t_from):
    """Fit phase = rate * t + c to the shown frames from t_from on (see the header)."""
    pts = []
    u = None
    last = None
    for t, k in zip(times, best):
        if t < t_from:
            continue
        if last is None:
            u, last = k, k
            pts.append((t, u))
            continue
        d = (k - last) % n
        if d <= 3:
            u += d
        elif d >= n - 3:
            u -= n - d
        else:
            continue         # a frame that fits neither way: left out
        last = k
        pts.append((t, u))
    if len(pts) < 10:
        raise Failed("too few frames to fit the animation's clock")
    keep = pts
    for _ in range(3):
        mt = sum(t for t, _ in keep) / len(keep)
        mu = sum(u + 0.5 for _, u in keep) / len(keep)
        sxx = sum((t - mt) ** 2 for t, _ in keep)
        rate = sum((t - mt) * (u + 0.5 - mu) for t, u in keep) / sxx
        c = mu - rate * mt
        res = [(t, u, u + 0.5 - (rate * t + c)) for t, u in pts]
        keep = [(t, u) for t, u, r in res if abs(r) <= 1.0]
    sd = math.sqrt(sum(r * r for _, _, r in res if abs(r) <= 1.0) / max(1, len(keep)))
    outliers = [round(t, 3) for t, _, r in res if abs(r) > 1.0]
    return {"rate_frames_per_s": rate, "c": c, "residual_sd_frames": sd, "frames_used": len(keep),
            "frames_left_out": len(pts) - len(keep), "outlier_times": outliers[:50],
            "from_s": t_from, "to_s": pts[-1][0]}


# ---------------------------------------------------------------- markers

def flashes(video, spec, geometry):
    m = spec["markers"]
    zoom = spec.get("zoom", 1)
    px = 32 * zoom
    cam = geometry["camera_px_in_box"]
    size = m.get("size", 2) * px
    x0, y0 = cam[0] + m["offset"][0] * px, cam[1] + m["offset"][1] * px
    inner = (int(x0 + size * 0.25), int(y0 + size * 0.25), int(x0 + size * 0.75), int(y0 + size * 0.75))
    if inner[0] < 0 or inner[1] < 0 or inner[2] > video.w or inner[3] > video.h:
        raise Failed(f"the marker square {inner} is outside the recorded box")
    lum = []
    for i in range(len(video.t)):
        b = video.image(i).crop(inner).convert("L").tobytes()
        lum.append(sum(b) / len(b))
    base = sorted(lum)[len(lum) // 2]
    found, on = [], False
    for i, v in enumerate(lum):
        if v > base + 0.5 * (255 - base) and not on:
            found.append({"t": video.t[i], "frame": i, "lum": round(v, 1), "base_lum": round(base, 1)})
            on = True
        elif v <= base + 0.25 * (255 - base):
            on = False
    return found, inner


# ---------------------------------------------------------------- the MP4

def write_mp4(path, video, audio, t_from, t_to, spec):
    cap, mp = spec["capture"], spec.get("mp4", {})
    fps = cap.get("fps", 30)
    pipe = Gst.parse_launch(
        f"appsrc name=v format=time max-bytes=0 "
        f"caps=video/x-raw,format=RGB,width={video.w},height={video.h},framerate={fps}/1 "
        f"! videoconvert ! video/x-raw,format=I420 "
        f"! vp9enc target-bitrate={mp.get('video_bitrate', 1200000)} end-usage=vbr deadline=1000000 cpu-used=4 "
        f"threads=8 row-mt=true keyframe-max-dist={fps * 2} "
        # mp4mux takes VP9 only with its chroma format and bit depth in the
        # caps, which vp9parse would add and this machine does not have: they
        # are I420's, 4:2:0 at 8 bits, stated here.
        f"! capssetter caps=\"video/x-vp9,chroma-format=(string)4:2:0,bit-depth-luma=(uint)8,"
        f"bit-depth-chroma=(uint)8\" "
        f"! queue max-size-buffers=0 max-size-bytes=0 max-size-time=0 ! mp4mux name=mux faststart=true "
        f"! filesink name=out "
        f"appsrc name=a format=time caps=audio/x-raw,format=S16LE,rate={audio['rate']},channels=2,layout=interleaved "
        f"! audioconvert ! audioresample ! opusenc bitrate={mp.get('audio_bitrate', 128000)} "
        f"! queue max-size-buffers=0 max-size-bytes=0 max-size-time=0 ! mux.")
    pipe.get_by_name("out").set_property("location", str(path))
    vsrc, asrc = pipe.get_by_name("v"), pipe.get_by_name("a")
    bus = pipe.get_bus()
    pipe.set_state(Gst.State.PLAYING)
    # All the audio first (a few MB), so the muxer never waits on it while the
    # video, the slow half, is fed at the encoder's pace. Never a blocking push:
    # a buffer wrapped round Python bytes is freed on a streaming thread, which
    # needs the interpreter lock that a blocked push would be holding.
    rate = audio["rate"]
    lr = audio["left_right"]
    i0 = max(0, int(round((t_from - audio["t0"]) * rate)))
    i1 = min(len(lr) // 2, int(round((t_to - audio["t0"]) * rate)))
    chunk = rate // 10
    for i in range(i0, i1, chunk):
        j = min(i1, i + chunk)
        buf = Gst.Buffer.new_wrapped(lr[2 * i:2 * j].tobytes())
        buf.pts = int(round((audio["t0"] + i / rate - t_from) * 1e9))
        buf.duration = int(round((j - i) / rate * 1e9))
        asrc.emit("push-buffer", buf)
    asrc.emit("end-of-stream")
    idx = [i for i, t in enumerate(video.t) if t_from <= t <= t_to]
    for n, i in enumerate(idx):
        buf = Gst.Buffer.new_wrapped(video.frame_bytes(i))
        buf.pts = int(round((video.t[i] - t_from) * 1e9))
        nxt = video.t[idx[n + 1]] if n + 1 < len(idx) else video.t[i] + 1 / fps
        buf.duration = int(round((nxt - video.t[i]) * 1e9))
        for _ in range(60000):      # at most 10 minutes for the encoder to drain
            if vsrc.get_property("current-level-bytes") <= 40 * video.size:
                break
            err = bus.pop_filtered(Gst.MessageType.ERROR)
            if err:
                pipe.set_state(Gst.State.NULL)
                raise Failed(f"encoding the MP4 failed: {err.parse_error()[0].message}")
            time.sleep(0.01)
        vsrc.emit("push-buffer", buf)
    vsrc.emit("end-of-stream")
    msg = bus.timed_pop_filtered(600 * Gst.SECOND, Gst.MessageType.EOS | Gst.MessageType.ERROR)
    pipe.set_state(Gst.State.NULL)
    if msg is None or msg.type == Gst.MessageType.ERROR:
        raise Failed("encoding the MP4 failed" + (f": {msg.parse_error()[0].message}" if msg else " (timeout)"))
    return {"path": str(path), "seconds": round(t_to - t_from, 3), "frames": len(idx),
            "bytes": path.stat().st_size, "video": "VP9", "audio": f"Opus {audio['rate']} Hz stereo",
            "starts_at_s": round(t_from, 3)}


# ---------------------------------------------------------------- the run

def circ(d, n):
    """A frame difference brought into [-n/2, n/2)."""
    return (d + n / 2) % n - n / 2


def run(out, spec, repo):
    out, repo = Path(out), Path(repo)
    raw = out / "raw"
    Gst.init(None)
    geometry = json.loads((out / "geometry.json").read_text())
    status = [json.loads(line) for line in open(out / "probe-status.jsonl")]
    ticks = {r["what"]: r["tick"] for r in status if r["what"] != "tick"}
    video = Video(raw)
    audio = load_audio(raw)
    n = spec["stroke"]["frame_count"]
    if len(video.t) < 30:
        raise Failed(f"only {len(video.t)} video frames were recorded")

    # Markers: the flash in the picture, the click in the sound (the strongest
    # onset near each flash).
    fl, inner = flashes(video, spec, geometry)
    env = band_envelopes(audio["mono"], audio["rate"])
    found = onsets(env, audio["t0"], spec.get("onset_rise_db", ONSET_DB))
    marks = []
    for k, f in enumerate(fl):
        near = [o for o in found if -0.25 <= o["t"] - f["t"] <= 0.35]
        click = max(near, key=lambda o: o["rise_db"]) if near else None
        marks.append({"marker": k + 1, "flash_first_frame_s": round(f["t"], 4),
                      "click_onset_s": round(click["t"], 4) if click else None,
                      "click_rise_db": click["rise_db"] if click else None,
                      "sound_after_picture_s": round(click["t"] - f["t"], 4) if click else None})
    expected_marks = len(spec["markers"]["after_ready"])
    if len(marks) != expected_marks or any(m["click_onset_s"] is None for m in marks):
        raise Failed(f"markers: expected {expected_marks} flashes each with a click, found {marks}")
    chain = sum(m["sound_after_picture_s"] for m in marks) / len(marks)
    # Ticks to seconds from the two markers (the game's own rate, not assumed 60).
    t_ticks = [ticks[f"marker {k + 1}"] for k in range(len(marks))]
    tick_s = ((marks[-1]["flash_first_frame_s"] - marks[0]["flash_first_frame_s"]) / (t_ticks[-1] - t_ticks[0])
              if len(marks) > 1 else 1 / 60)
    t_start = marks[-1]["flash_first_frame_s"] + (ticks["start"] - t_ticks[-1]) * tick_s

    # The frame on screen in every recorded frame.
    stroke = Stroke(spec, geometry, repo)
    work = [i for i, t in enumerate(video.t) if t > t_start + 0.3]
    sample = [stroke.roi(video.image(i)) for i in work[::max(1, len(work) // 12)][:12]]
    dx, dy, reg_cost = stroke.register(sample)
    rows = []
    for i, t in enumerate(video.t):
        sc = stroke.scores(stroke.roi(video.image(i)), dx, dy)
        order = sorted(range(n), key=lambda k: sc[k])
        rows.append({"i": i, "t": round(t, 4), "frame": order[0], "score": round(sc[order[0]], 2),
                     "next": order[1], "next_score": round(sc[order[1]], 2)})
    with open(out / "frames.csv", "w") as f:
        f.write("i,t_s,frame,score,next_frame,next_score\n")
        for r in rows:
            f.write(f"{r['i']},{r['t']},{r['frame']},{r['score']},{r['next']},{r['next_score']}\n")
    fit = unwrap_fit(video.t, [r["frame"] for r in rows], n, t_start + 0.3)
    rate, c = fit["rate_frames_per_s"], fit["c"]

    def phase(t):
        return (rate * t + c) % n

    def shown(t):
        before = [r for r in rows if r["t"] <= t]
        return before[-1]["frame"] if before else None

    # Label every onset from the start on.
    tpls = {name: template(decode(repo / p, audio["rate"]), audio["rate"]) for name, p in spec["sounds"].items()}
    events = []
    for o in found:
        if o["t"] < t_start - 0.05:
            continue
        best = (None, -2.0, 0)
        for name, tp in tpls.items():
            for lag in range(-8, 9):
                h = o["hop"] - tp["onset_hops"] + lag
                if h < 0:
                    continue
                s = match(env, h, tp)
                if s is not None and s > best[1]:
                    best = (name, s, lag)
        label = best[0] if best[1] >= MATCH_MIN else "unknown"
        ph = phase(o["t"])
        events.append({"t_s": round(o["t"], 4), "since_start_s": round(o["t"] - t_start, 4),
                       "sound": label, "match": round(best[1], 3), "match_lag_ms": best[2] * HOP_S * 1000,
                       "best_file": best[0], "rise_db": o["rise_db"], "level_db": o["level_db"],
                       "phase": round(ph, 3), "frame_by_phase": int(ph), "frame_in_last_grab": shown(o["t"]),
                       "phase_less_chain_delay": round(phase(o["t"] - chain), 3)})

    # Judge against what was agreed (only here). An accent cued on frame F
    # should start as frame F starts, at phase F: its error is phase - F in
    # frames (negative: before frame F was on screen), within tolerance_frames.
    exp = spec.get("expect", {})
    tol = exp.get("tolerance_frames", 1)
    t_last = video.t[-1]
    judged = []
    labelled = [e for e in events if e["sound"] != "unknown"]
    used = set()
    ok = True
    for a in exp.get("accents", []):
        # Every time the animation reached this frame from the start on (the
        # first stroke after start-up included; the fit leaves its first 0.3 s
        # out, the passes do not), with a window's worth of recording after it.
        passes = []
        k = math.ceil((rate * t_start + c - a["frame"]) / n)
        for _ in range(10000):
            t_reach = (a["frame"] + k * n - c) / rate
            if t_reach > t_last - WINDOW_S:
                break
            passes.append(t_reach)
            k += 1
        hits = []
        for t_reach in passes:
            cands = [e for e in labelled if e["sound"] == a["sound"] and id(e) not in used
                     and abs(e["t_s"] - t_reach) <= (tol + 1) / rate]
            if not cands:
                hits.append({"frame_reached_s": round(t_reach, 4), "found": False})
                continue
            e = min(cands, key=lambda e: abs(e["t_s"] - t_reach))
            used.add(id(e))
            off = round(circ(e["phase"] - a["frame"], n), 3)
            off_c = round(circ(e["phase_less_chain_delay"] - a["frame"], n), 3)
            within = abs(off) <= tol
            e["cued_frame"] = a["frame"]
            e["frames_from_cue"] = off
            hits.append({"frame_reached_s": round(t_reach, 4), "found": True, "onset_s": e["t_s"],
                         "phase": e["phase"], "frames_from_cue": off, "frames_from_cue_less_chain_delay": off_c,
                         "frame_in_last_grab": e["frame_in_last_grab"], "within_tolerance": within})
        good = bool(hits) and all(h.get("within_tolerance") for h in hits)
        ok = ok and good
        judged.append({"sound": a["sound"], "frame": a["frame"], "passes": hits,
                       "measured_phases": [h["phase"] for h in hits if h["found"]],
                       "missing": sum(1 for h in hits if not h["found"]), "pass": good})
    stray = [e for e in labelled if id(e) not in used]
    if stray and exp.get("accents"):
        ok = False

    # The MP4: from just before the machine starts to the end.
    t_from = max(video.t[0], t_start - spec.get("mp4", {}).get("lead_seconds", 0.6))
    mp4 = write_mp4(out / f"{spec.get('name', 'capture')}.mp4", video, audio, t_from, video.t[-1], spec)

    summary = "; ".join(
        f"{j['sound']} {j['frame']}: at {j['measured_phases']}"
        + (f", {j['missing']} missing" if j["missing"] else "") + ("" if j["pass"] else " FAIL") for j in judged)
    if stray:
        summary += f"; {len(stray)} labelled onset(s) on no expected frame"
    result = {
        "pass": ok,
        "summary": summary,
        "how_frames_map_to_time": __doc__.split("**One clock.**")[1].split("Judged against")[0].strip(),
        "clock": {"video_frames": len(video.t), "video_first_s": round(video.t[0], 4),
                  "video_last_s": round(video.t[-1], 4), "audio_first_s": round(audio["t0"], 4),
                  "audio_seconds": round(len(audio["mono"]) / audio["rate"], 3),
                  "audio_buffers": audio["buffers"], "audio_worst_drift_s": round(audio["worst_drift_s"], 5),
                  "audio_discontinuities_s": audio["discont"]},
        "markers": {"found": marks, "sound_after_picture_s": round(chain, 4),
                    "seconds_per_tick": round(tick_s, 6), "square_px": inner},
        "start_s": round(t_start, 4),
        "registration": {"dx": dx, "dy": dy, "mean_best_score": round(reg_cost, 2),
                         "sprite_box_in_capture": [stroke.x0 + dx, stroke.y0 + dy, stroke.sw, stroke.sh]},
        "fit": {k: (round(v, 5) if isinstance(v, float) else v) for k, v in fit.items()},
        "accents": judged,
        "onsets": events,
        "stray_labelled_onsets": stray,
        "tolerance_frames": tol,
        "mp4": mp4,
    }
    (out / "accents.json").write_text(json.dumps(result, indent=1))
    sheet(out, video, stroke, rows, events, dx, dy)
    return {"pass": ok, "summary": summary, "mp4": mp4["path"]}


def sheet(out, video, stroke, rows, events, dx, dy):
    """For each labelled onset: the recorded box at that moment beside the sheet frame matched there, 3x."""
    ev = [e for e in events if e["sound"] != "unknown"]
    if not ev:
        return
    z = 3
    cw, chh = stroke.sw * z, stroke.sh * z
    W = 2 * cw + 30
    H = len(ev) * (chh + 24) + 10
    im = Image.new("RGB", (W, H), (40, 40, 40))
    d = ImageDraw.Draw(im)
    for r_i, e in enumerate(ev):
        y = 5 + r_i * (chh + 24)
        i = max(r["i"] for r in rows if r["t"] <= e["t_s"])
        x0, y0 = stroke.x0 + dx, stroke.y0 + dy
        crop = video.image(i).crop((x0, y0, x0 + stroke.sw, y0 + stroke.sh)).resize((cw, chh), Image.NEAREST)
        im.paste(crop, (5, y + 18))
        pic = stroke.pictures[rows[i]["frame"]]
        bg = Image.new("RGBA", pic.size, (90, 90, 90, 255))
        bg.alpha_composite(pic)
        im.paste(bg.convert("RGB").resize((cw, chh), Image.NEAREST), (cw + 25, y + 18))
        d.text((5, y + 2), f"{e['t_s']:.3f} s  {e['sound']}  phase {e['phase']:.2f}  "
                           f"recorded | sheet frame {rows[i]['frame']}", fill=(255, 255, 255))
    im.save(out / "onset-frames.png")


if __name__ == "__main__":
    d = Path(sys.argv[1])
    res = run(d, json.loads((d / "spec.json").read_text()), Path(__file__).resolve().parents[3])
    print(json.dumps(res, indent=1))
    sys.exit(0 if res["pass"] else 1)
