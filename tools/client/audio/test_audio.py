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
"""

import json
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
