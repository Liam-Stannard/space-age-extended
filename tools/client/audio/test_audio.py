#!/usr/bin/env python3
"""tools/client/audio/test_audio.py -- checks of capture.py and analyse.py that
need no game client.

  python3 tools/client/audio/test_audio.py

- write_mp4 starts its audio on the first sample at or after the MP4's start,
  so a start within half a sample of the one before encodes (it raised
  OverflowError on a -4167 ns timestamp, 2026-10-20).
- label_onsets tells the crusher's pawl from its trip and from the pebble in its
  drop, from the shipped sound files mixed as the engine plays them.
- capture.py exits 3 when the launcher refuses, at the first launch (the save)
  or the second (the recording), and leaves no raw/ behind. A stand-in for
  launch.sh is used: no Factorio is started. The second case starts the sound
  guard, which only reads (pactl, pw-metadata, pw-dump) and stops its helpers.
- analyse.run on synthetic recordings (no client): the crusher's stroke sheet
  drawn grab by grab as its frame_sequence plays it (4 ticks an entry), the
  markers' flashes and clicks, and the shipped sounds mixed in on their
  entries. On entries 50, 58, 6, 20 and 28 every pass is on time; the trip
  moved 3 entries on is judged late. The same sheet without a frame_sequence,
  its frames played in order, is judged in frames as before.
"""

import json
import math
import os
import signal
import sys
import tempfile
import unittest
from array import array
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyse  # noqa: E402

RATE = 48000


class FakeVideo:
    def __init__(self, times, w=64, h=48):
        self.w, self.h, self.size, self.t = w, h, w * h * 3, times

    def frame_bytes(self, i):
        return bytes([(i * 20) % 256]) * self.size


class WriteMp4(unittest.TestCase):
    def encode(self, t_from):
        t0 = 10.0
        lr = array("h", [0, 0] * (RATE * 2))           # 2 s of stereo silence
        audio = {"rate": RATE, "left_right": lr, "t0": t0}
        video = FakeVideo([t_from + n / 30 for n in range(15)])
        spec = {"capture": {"fps": 30}, "mp4": {"video_bitrate": 100000, "audio_bitrate": 64000}}
        with tempfile.TemporaryDirectory(prefix="sae-t09-mp4.") as d:
            path = Path(d) / "x.mp4"
            r = analyse.write_mp4(path, video, audio, t_from, video.t[-1], spec)
            self.assertGreater(path.stat().st_size, 0)
            return r

    def test_start_within_half_a_sample(self):
        # 0.2 of a sample past sample 24000: the old rounding took 24000 and
        # stamped it -4167 ns, which a buffer's unsigned pts cannot hold.
        analyse.Gst.init(None)
        for frac in (0.2, 0.49, 0.5, 0.51, 0.99, 0.0):
            with self.subTest(frac=frac):
                self.encode(10.0 + (RATE // 2 + frac) / RATE)

    def test_start_before_the_audio(self):
        analyse.Gst.init(None)
        self.encode(9.9)


class Labels(unittest.TestCase):
    """The crusher's shipped sounds, mixed as the engine plays them: a drop, a
    pawl 0.67 s later under its tail (frame 18), and an onset on the drop's
    own pebble 0.8 s in, which matches pawl.ogg until the drop is taken out."""

    def test_the_drops_pebble_is_no_pawl(self):
        import random
        analyse.Gst.init(None)
        repo = HERE.parents[2]
        files = {k: analyse.decode(repo / f"sound/drop-crusher/{k}.ogg", RATE) for k in ("drop", "pawl", "trip")}
        rnd = random.Random(9)
        mix = [rnd.gauss(0, 0.002) for _ in range(RATE * 4)]
        for name, at, gain in (("drop", 1.0, 0.35), ("pawl", 1.0 + 4 / 6, 0.6), ("trip", 3.0, 0.5)):
            i0 = int(at * RATE)
            for i, v in enumerate(files[name]):
                if i0 + i < len(mix):
                    mix[i0 + i] += gain * v
        cands = [{"t": t, "rise_db": 40.0} for t in (1.004, 1.0 + 4 / 6 + 0.004, 1.801 + 0.004, 3.004)]

        def labels(sounds):
            m = analyse.Matcher(mix, RATE, 0.0, {k: files[k] for k in sounds})
            taken, left = analyse.label_onsets(m, cands, analyse.MATCH_MIN)
            return {round(c["o"]["t"], 3): c["now"][0][0] for c in taken}, [round(c["o"]["t"], 3) for c in left]

        got, left = labels(("drop", "pawl", "trip"))
        self.assertEqual(got, {1.004: "drop", 1.671: "pawl", 3.004: "trip"})
        self.assertEqual(left, [1.805])
        # Without the drop to explain it, the pebble is taken for a pawl: the
        # case above is a real one.
        got, _ = labels(("pawl", "trip"))
        self.assertEqual(got.get(1.805), "pawl")


REPO = HERE.parents[2]
CRUSHER_SPEC = HERE / "specs/drop-crusher.json"


def build_run(out, spec, repo, cues, ticks_per_step=4, work_ticks=600, seed=3):
    """A recording as capture.py leaves it (raw/, geometry.json,
    probe-status.jsonl), drawn and mixed here instead of by a client.

    The stroke sheet's frames are cut and scaled as Stroke cuts them and laid
    on a fixed noisy ground, 1 px right and 1 px up of where the spec puts them
    (for the registration to find). Every 2 ticks a grab (30 fps), half a tick
    after the tick it shows (grabs are not locked to the game's ticks): before
    the start the idle (sheet frame 0), from it the animation, one step
    (entry, or sheet frame without a frame_sequence) every ticks_per_step
    ticks, from step 0. Markers flash and click on capture ticks 20 and 50,
    the machine starts on tick 80. cues: [(sound name, step)]: the file is
    played on the tick each pass of that step starts, 6 ms late (the engine's
    chain), up to 25 ticks before the recording ends (a pass closer to
    the end is not judged, so its sound would be a stray)."""
    from PIL import Image
    import random
    out = Path(out)
    raw = out / "raw"
    raw.mkdir(parents=True)
    rnd = random.Random(seed)
    w, h, cam, fps = 400, 300, (300.0, 230.0), 30
    st = spec["stroke"]
    seq = analyse.sequence_of(st) or list(range(st["frame_count"]))
    k = st["scale"] * spec.get("zoom", 1)
    sheet = Image.open(repo / st["filename"]).convert("RGBA")
    sw, sh = max(1, round(st["width"] * k)), max(1, round(st["height"] * k))
    x0 = int(round(cam[0] + st["shift"][0] * 32 - st["width"] * k / 2)) + 1
    y0 = int(round(cam[1] + st["shift"][1] * 32 - st["height"] * k / 2)) - 1
    ground = Image.frombytes("RGB", (w, h), bytes(rnd.randrange(60, 140) for _ in range(w * h * 3)))
    pictures = []
    for i in range(st["frame_count"]):
        col, row = i % st["line_length"], i // st["line_length"]
        fr = sheet.crop((col * st["width"], row * st["height"], (col + 1) * st["width"], (row + 1) * st["height"]))
        im = ground.copy()
        im.paste(fr.resize((sw, sh), Image.BOX), (x0, y0), fr.resize((sw, sh), Image.BOX))
        pictures.append(im)
    m = spec["markers"]
    msz = m.get("size", 2) * 32
    mx, my = cam[0] + m["offset"][0] * 32, cam[1] + m["offset"][1] * 32
    marks, start, end = (20, 50), 80, 80 + work_ticks
    t_video, t_audio = 5.0, 4.98       # the pipeline's clock, s, at capture tick 0

    def step_at(tick):
        return (tick - start) // ticks_per_step if tick >= start else 0

    frames, vts = bytearray(), []
    for tick in range(0, end + 1, 60 // fps):
        im = pictures[seq[step_at(tick) % len(seq)]]
        if any(mk <= tick < mk + m.get("ticks_shown", 6) for mk in marks):
            im = im.copy()
            im.paste((255, 255, 255), (int(mx), int(my), int(mx + msz), int(my + msz)))
        frames += im.tobytes()
        vts.append({"pts": int(round((t_video + (tick + 0.5) / 60) * 1e9))})
    (raw / "video.rgb").write_bytes(bytes(frames))
    (raw / "video.json").write_text(json.dumps({"width": w, "height": h, "format": "RGB", "frames": vts}))

    n_samples = int((t_video + (end + 30) / 60 - t_audio) * RATE)
    mix = [rnd.gauss(0, 0.002) for _ in range(n_samples)]

    def place(x, tick, gain):
        i0 = int(round((t_video + tick / 60 + 0.006 - t_audio) * RATE))
        for i, v in enumerate(x[:max(0, n_samples - i0)]):
            mix[i0 + i] += gain * v
    click = [rnd.uniform(-1, 1) * math.exp(-i / (0.004 * RATE)) for i in range(int(0.03 * RATE))]
    for mk in marks:
        place(click, mk, 0.5)
    files = {name: analyse.decode(repo / p, RATE) for name, p in spec["sounds"].items()}
    gains = {"drop": 0.35, "pawl": 0.6, "trip": 0.5}
    loop = len(seq) * ticks_per_step
    for name, step in cues:
        tick = start + step * ticks_per_step
        while tick <= end - 25:
            place(files[name], tick, gains.get(name, 0.5))
            tick += loop
    lr = array("h")
    for v in mix:
        s = max(-32767, min(32767, int(round(v * 32767))))
        lr.extend((s, s))
    (raw / "audio.s16").write_bytes(lr.tobytes())
    bufs, pos = [], 0
    while pos < n_samples:
        n = min(1024, n_samples - pos)
        bufs.append({"pts": int(round((t_audio + pos / RATE) * 1e9)), "n": n, "discont": pos == 0})
        pos += n
    (raw / "audio.json").write_text(json.dumps({"rate": RATE, "channels": 2, "format": "S16LE", "buffers": bufs}))
    (out / "geometry.json").write_text(json.dumps({"camera_px_in_box": list(cam)}))
    game = 1000                         # the game's tick at capture tick 0
    rows = [{"tick": game + marks[0], "what": "marker 1"}, {"tick": game + marks[1], "what": "marker 2"},
            {"tick": game + start, "what": "start"}]
    (out / "probe-status.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))


def synthetic_spec(**stroke):
    spec = json.loads(CRUSHER_SPEC.read_text())
    spec["name"] = "synthetic"
    spec["capture"] = {"width": 400, "height": 300, "fps": 30, "rate": RATE}
    spec["mp4"] = {"lead_seconds": 0.6, "video_bitrate": 200000, "audio_bitrate": 64000}
    spec["markers"]["after_ready"] = [20, 50]
    spec["stroke"].update(stroke)
    return spec


def analysed(spec, cues, **kw):
    analyse.Gst.init(None)
    with tempfile.TemporaryDirectory(prefix="sae-t06a-audio.") as d:
        build_run(d, spec, REPO, cues, **kw)
        analyse.run(d, spec, REPO)
        res = json.loads((Path(d) / "accents.json").read_text())
        res["frames_csv"] = (Path(d) / "frames.csv").read_text().splitlines()
        return res


def describe(res):
    """What a test prints: the verdict, each cue's timing, the fit."""
    return (f"pass={res['pass']}  {res['summary']}\n  fit: {res['fit']['rate_frames_per_s']} a second, "
            f"sd {res['fit']['residual_sd_frames']}, ticks/entry {res.get('ticks_per_entry')}, "
            f"tolerance {res['tolerance_frames']} = {res.get('tolerance_ticks')} ticks")


class FrameSequence(unittest.TestCase):
    """The crusher's 60-entry frame_sequence over its 44 sheet frames, judged
    in entries (T06a)."""

    CUES = [("pawl", 50), ("pawl", 58), ("pawl", 6), ("trip", 20), ("drop", 28)]

    def check_on_time(self, res, skip=()):
        for j in res["accents"]:
            if (j["sound"], j["frame"]) in skip:
                continue
            with self.subTest(sound=j["sound"], entry=j["frame"]):
                self.assertTrue(j["pass"])
                self.assertGreaterEqual(len(j["passes"]), 2)
                for p in j["passes"]:
                    self.assertTrue(p["found"])
                    self.assertEqual(p["timing"], "on time")
                    self.assertLess(abs(p["frames_from_cue"]), 0.5)

    def test_sounds_on_their_entries_are_on_time(self):
        res = analysed(synthetic_spec(), self.CUES)
        print("\n[on their entries] " + describe(res))
        self.assertTrue(res["pass"], res["summary"])
        self.assertEqual(len(res["accents"]), 5)
        self.check_on_time(res)
        self.assertEqual(res["stray_labelled_onsets"], [])
        self.assertEqual(res["unit"], "frame_sequence entry")
        self.assertAlmostEqual(res["ticks_per_entry"], 4.0, delta=0.05)
        self.assertAlmostEqual(res["tolerance_ticks"], 4.0, delta=0.05)
        self.assertAlmostEqual(res["fit"]["rate_frames_per_s"], 15.0, delta=0.05)
        # Held frames told apart by time: every grab of sheet frame 13 (14,
        # 1-based) after the start is on one of entries 13-19, and the
        # entries are seen through the hold, not one entry for all of it.
        head = res["frames_csv"][0].split(",")
        self.assertEqual(head[-1], "entry")
        start = res["start_s"]
        held = [int(r.split(",")[-1]) for r in res["frames_csv"][1:]
                if r.split(",")[2] == "13" and float(r.split(",")[1]) > start + 0.3]
        self.assertTrue(held)
        self.assertTrue(set(held) <= set(range(13, 20)), held)
        self.assertGreaterEqual(len(set(held)), 3, held)

    def test_a_trip_three_entries_on_is_late(self):
        cues = [c for c in self.CUES if c[0] != "trip"] + [("trip", 23)]
        res = analysed(synthetic_spec(), cues)
        print("\n[trip on 23] " + describe(res))
        self.assertFalse(res["pass"])
        trip = next(j for j in res["accents"] if j["sound"] == "trip")
        self.assertFalse(trip["pass"])
        self.assertGreaterEqual(len(trip["passes"]), 2)
        for p in trip["passes"]:
            self.assertTrue(p["found"])
            self.assertEqual(p["timing"], "late")
            self.assertAlmostEqual(p["frames_from_cue"], 3.0, delta=0.5)
            self.assertAlmostEqual(p["ticks_from_cue"], 12.0, delta=2.0)
        self.assertEqual(trip["late"], len(trip["passes"]))
        self.assertEqual(res["stray_labelled_onsets"], [])
        self.check_on_time(res, skip={("trip", 20)})


class NoFrameSequence(unittest.TestCase):
    """Without a frame_sequence the clock counts sheet frames, as before T06a."""

    def test_frames_in_order_judged_in_frames(self):
        spec = synthetic_spec()
        del spec["stroke"]["frame_sequence"]
        spec["expect"]["accents"] = [{"sound": "drop", "frame": 21}, {"sound": "pawl", "frame": 30},
                                     {"sound": "pawl", "frame": 36}, {"sound": "pawl", "frame": 4},
                                     {"sound": "trip", "frame": 14}]
        cues = [(a["sound"], a["frame"]) for a in spec["expect"]["accents"]]
        res = analysed(spec, cues, ticks_per_step=5, work_ticks=560)
        print("\n[no frame_sequence] " + describe(res))
        self.assertTrue(res["pass"], res["summary"])
        self.assertAlmostEqual(res["fit"]["rate_frames_per_s"], 12.0, delta=0.05)
        for j in res["accents"]:
            for p in j["passes"]:
                self.assertLess(abs(p["frames_from_cue"]), 0.5)
                self.assertNotIn("timing", p)
        for key in ("unit", "ticks_per_entry", "tolerance_ticks"):
            self.assertNotIn(key, res)
        self.assertNotIn("unit", res["fit"])
        self.assertEqual(res["frames_csv"][0], "i,t_s,frame,score,next_frame,next_score")


FAKE_LAUNCH = """#!/usr/bin/env bash
# A stand-in for launch.sh: creates the save, or refuses (exit 3) where told.
create="" audio=0
while [ $# -gt 0 ]; do
  case "$1" in --create) create="$2"; shift 2 ;; --audio) audio=1; shift ;; *) shift ;; esac
done
if [ -n "$create" ]; then
  [ "$SAE_T09_REFUSE" = create ] && { echo "launch.sh: REFUSED -- (stand-in) lock held" >&2; exit 3; }
  echo zip > "$create"; exit 0
fi
[ "$audio" = 1 ] && [ "$SAE_T09_REFUSE" = record ] && { echo "launch.sh: REFUSED -- (stand-in) lock held" >&2; exit 3; }
exit 1
"""


class CaptureRefused(unittest.TestCase):
    def run_capture(self, where, check):
        import capture
        handlers = {s: signal.getsignal(s) for s in capture._SIGNALS}
        argv, launch, repo = sys.argv, capture.LAUNCH, capture.REPO
        with tempfile.TemporaryDirectory(prefix="sae-t09-capture.") as d:
            d = Path(d)
            fake = d / "launch.sh"
            fake.write_text(FAKE_LAUNCH)
            fake.chmod(0o755)
            os.environ["SAE_T09_REFUSE"] = where
            capture.LAUNCH, capture.REPO = fake, d
            sys.argv = ["capture.py", "--task", "t09-refused", "--spec", str(HERE / "specs/drop-crusher.json")]
            try:
                rc = capture.main()
            finally:
                sys.argv, capture.LAUNCH, capture.REPO = argv, launch, repo
                del os.environ["SAE_T09_REFUSE"]
                for s, h in handlers.items():
                    signal.signal(s, h)
            outs = list((d / "evidence/t09-refused").glob("audio-*"))
            self.assertEqual(len(outs), 1)
            self.assertEqual(rc, 3)
            self.assertFalse((outs[0] / "raw").exists())
            check(outs[0])

    def test_refused_at_the_save(self):
        def check(out):
            self.assertIn("REFUSED", (out / "launch-create.log").read_text())
            self.assertFalse((out / "launch-record.log").exists())
        self.run_capture("create", check)

    def test_refused_at_the_recording(self):
        def check(out):
            self.assertIn("REFUSED", (out / "launch-record.log").read_text())
            self.assertIn("pass", json.loads((out / "sound-guard.json").read_text()))
        self.run_capture("record", check)


if __name__ == "__main__":
    unittest.main(verbosity=2)
