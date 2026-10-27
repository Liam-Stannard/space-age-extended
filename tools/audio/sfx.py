"""The sound library every sound script imports: read, shape, layer, write.

A building's sound is made the way its art is: by a script that can be run
again, measured against vanilla's equivalent, reviewed by Liam against its
motion, and only then wired into its prototype. The tools that do it:

  sfx.py       this file: vanilla sounds by game path, layering and timing in
               ms or animation frames, gain, speed, fades, envelopes, filters,
               EQ, noise and tones, and .ogg out in vanilla's own format
  loudness.py  integrated loudness (LUFS, ITU-R BS.1770) and true peak, ours
               beside vanilla's, and the gain that matches one to the other:
               loudness.py <file-or-game-path> ... [--ref <file>] [--ffmpeg]
  review.py    an MP4 of a sound against its animation, at game speed, beside
               a vanilla clip if wanted: review.py --help

**Where sounds live:** sound/<building>/ holds the game files a prototype
loads (__space-age-extended__/sound/<building>/<name>.ogg); concept/<building>/
sound/ holds the scripts that make them and the review MP4s -- design, like a
model, so nothing there ships.

**Setup**, once, from the repo root, no sudo (the venv is git-ignored):

  python3 -m venv tools/audio/.venv && tools/audio/.venv/bin/pip install -r tools/audio/requirements.txt

and every tool, and every sound script, runs under tools/audio/.venv/bin/python.
A sound script imports this file with

  sys.path.insert(0, "<repo>/tools/audio"); import sfx

**A sound here is a numpy array** of float32 samples, shape (samples, channels),
at SR. Every function takes one and returns a new one; nothing is changed in
place. Times are seconds unless a name says otherwise; `ms()` and `frame()`
turn milliseconds and animation frames into seconds.

**The format is vanilla's, measured** (2026-10-11, every .ogg under the
Factorio data directory, 4539 files): 4419 are 44100 Hz stereo Vorbis, 113
44100 Hz mono, six 22050 Hz and one 48000 Hz; of the 607 under entity and
mining sounds, 602 are 44100 Hz stereo. Each one checked with ffmpeg is a
nominal 160 kb/s. So `load()` brings anything to 44100 Hz stereo and `write()`
writes 44100 Hz stereo Vorbis near 160 kb/s.

**Animation frames:** an animation at `animation_speed` s advances s frames a
tick, 60 ticks a second, so frame n begins n / s / 60 s after frame 0 -- frame
8 of a 24-frame animation at 0.4 is at 0.333 s and the loop is 1 s long. Frames
count from 0, as derive.working_sound's accent frames do. A crafting machine's
animation also runs at its crafting speed (machines.lua says how each of ours
plays); pass the speed it actually plays at.

**The Factorio data directory** is <FACTORIO_ROOT>/data, FACTORIO_ROOT being
the one tools/paths.conf names (tools/paths.py). A game path,
"__base__/sound/x.ogg", resolves under it; "__space-age-extended__/..."
resolves to this repo. `sfx.py` run alone prints this and that directory.
"""

import os
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # tools/
import paths  # noqa: E402   tools/paths.py: where Factorio is

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from scipy import signal  # noqa: E402

SR = 44100          # vanilla's sample rate, measured: see the header
CHANNELS = 2        # and its channel layout
TICKS_PER_SECOND = 60
# libsndfile's Vorbis setting: quality is 1 - this, on Vorbis's 0..1 scale, and
# 0.5 is Vorbis q5, nominally 160 kb/s at 44.1 kHz stereo -- vanilla's rate.
VORBIS_COMPRESSION = 0.5

REPO_ROOT = Path(__file__).resolve().parents[2]


# --- finding and reading files -------------------------------------------

def data_dir():
    """Factorio's data directory: <FACTORIO_ROOT>/data, from tools/paths.conf (paths.PathsError when not)."""
    return Path(paths.factorio_data())


def resolve(path):
    """A file path, or a game path such as "__base__/sound/x.ogg", as a Path."""
    s = str(path)
    if s.startswith("__"):
        mod, _, rest = s[2:].partition("__/")
        if not rest:
            raise ValueError(f"not a game path: {s}")
        root = REPO_ROOT if mod == "space-age-extended" else data_dir() / mod
        p = root / rest
    else:
        p = Path(s).expanduser()
    if not p.is_file():
        raise FileNotFoundError(f"{s}: no such file ({p})")
    return p


def read(path):
    """A sound file exactly as stored: (samples, channels) float32, and its rate."""
    x, sr = sf.read(str(resolve(path)), dtype="float32", always_2d=True)
    return x, sr


def conform(x, sr_in, sr=SR, channels=CHANNELS):
    """Bring a sound to a sample rate and channel count (mono is duplicated)."""
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 1:
        x = x[:, None]
    if sr_in != sr:
        f = Fraction(sr, sr_in)
        x = signal.resample_poly(x, f.numerator, f.denominator, axis=0).astype(np.float32)
    if x.shape[1] != channels:
        if x.shape[1] == 1:
            x = np.repeat(x, channels, axis=1)
        elif channels == 1:
            x = x.mean(axis=1, keepdims=True)
        else:
            raise ValueError(f"cannot make {x.shape[1]} channels into {channels}")
    return x


def load(path, sr=SR, channels=CHANNELS):
    """A sound file, or a vanilla one by game path, at SR and CHANNELS."""
    x, sr_in = read(path)
    return conform(x, sr_in, sr, channels)


def write(path, x, sr=SR, compression=VORBIS_COMPRESSION):
    """Write an .ogg (Vorbis), refusing to clip: fix the gain, not the file."""
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 1:
        x = x[:, None]
    peak = float(np.max(np.abs(x))) if x.size else 0.0
    if peak > 1.0:
        raise ValueError(f"{path}: peak {20 * np.log10(peak):+.2f} dBFS would clip; "
                         "lower the gain (normalize() or gain())")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), x, sr, format="OGG", subtype="VORBIS", compression_level=compression)
    return path


# --- time ------------------------------------------------------------------

def ms(n):
    """n milliseconds, in seconds."""
    return n / 1000.0


def frame(n, speed):
    """When frame n of an animation at animation_speed `speed` begins, in seconds."""
    return n / speed / TICKS_PER_SECOND


def loop_seconds(frames, speed):
    """How long one cycle of a `frames`-frame animation at `speed` lasts."""
    return frame(frames, speed)


def samples(seconds, sr=SR):
    return int(round(seconds * sr))


def seconds(x, sr=SR):
    return len(x) / sr


# --- making sounds ---------------------------------------------------------

def silence(length, sr=SR, channels=CHANNELS):
    return np.zeros((samples(length, sr), channels), dtype=np.float32)


def noise(length, color="white", seed=None, stereo=True, sr=SR, channels=CHANNELS):
    """Noise at peak 1.0: white, pink (-3 dB/octave) or brown (-6 dB/octave).

    `stereo=False` puts the same noise in every channel; True makes each its
    own, which sounds wide. `seed` makes it repeatable, as a script should be.
    """
    n = samples(length, sr)
    rng = np.random.default_rng(seed)
    cols = channels if stereo else 1
    w = rng.standard_normal((n, cols))
    if color != "white":
        power = {"pink": 0.5, "brown": 1.0}.get(color)
        if power is None:
            raise ValueError(f"noise colour {color!r}: white, pink or brown")
        spec = np.fft.rfft(w, axis=0)
        f = np.fft.rfftfreq(n, 1.0 / sr)
        f[0] = f[1] if n > 1 else 1.0
        spec /= (f ** power)[:, None]
        w = np.fft.irfft(spec, n=n, axis=0)
    w = w - w.mean(axis=0)
    w /= max(float(np.max(np.abs(w))), 1e-12)
    if not stereo:
        w = np.repeat(w, channels, axis=1)
    return w.astype(np.float32)


def tone(length, hz, wave="sine", to_hz=None, sr=SR, channels=CHANNELS):
    """A tone at peak 1.0: sine, square, saw or triangle, swept to `to_hz` if given."""
    n = samples(length, sr)
    f = np.full(n, float(hz)) if to_hz is None else np.geomspace(hz, to_hz, n)
    phase = np.cumsum(f) / sr                      # in cycles
    p = phase - np.floor(phase)
    if wave == "sine":
        y = np.sin(2 * np.pi * phase)
    elif wave == "square":
        y = np.where(p < 0.5, 1.0, -1.0)
    elif wave == "saw":
        y = 2.0 * p - 1.0
    elif wave == "triangle":
        y = 1.0 - 4.0 * np.abs(p - 0.5)
    else:
        raise ValueError(f"wave {wave!r}: sine, square, saw or triangle")
    return np.repeat(y[:, None], channels, axis=1).astype(np.float32)


# --- shaping ---------------------------------------------------------------

def _2d(x):
    x = np.asarray(x, dtype=np.float32)
    return x[:, None] if x.ndim == 1 else x


def gain(x, db):
    return (_2d(x) * np.float32(10 ** (db / 20.0))).astype(np.float32)


def speed(x, ratio):
    """Play faster (ratio > 1) or slower, pitch and length together, as tape does.

    It is what a Sound's `speed` does in game. ratio 2 is an octave up in half
    the time. Resampled through the nearest fraction with a denominator under
    1000, so the ratio is exact to about 1e-6.
    """
    f = Fraction(1.0 / ratio).limit_denominator(1000)
    return signal.resample_poly(_2d(x), f.numerator, f.denominator, axis=0).astype(np.float32)


def pitch(x, semitones):
    """speed() by a musical interval: +12 is an octave up, and half as long."""
    return speed(x, 2.0 ** (semitones / 12.0))


def _curve(n, kind):
    t = np.linspace(0.0, 1.0, n, dtype=np.float64)
    if kind == "linear":
        return t
    if kind == "cos":
        return 0.5 - 0.5 * np.cos(np.pi * t)
    if kind == "exp":                               # -60 dB to 0 dB, even in dB
        return np.where(t > 0, 10 ** (3 * (t - 1)), 0.0)
    raise ValueError(f"fade curve {kind!r}: linear, cos or exp")


def fade(x, fade_in=0.0, fade_out=0.0, curve="cos"):
    """Fade in over the first `fade_in` seconds and out over the last `fade_out`."""
    y = _2d(x).copy()
    a, b = min(samples(fade_in), len(y)), min(samples(fade_out), len(y))
    if a:
        y[:a] *= _curve(a, curve)[:, None]
    if b:
        y[len(y) - b:] *= _curve(b, curve)[::-1, None]
    return y.astype(np.float32)


def envelope(x, points, db=False):
    """Shape a sound by breakpoints [(seconds, level), ...], straight lines between.

    Level is a gain factor, or dB with `db=True`. Before the first point the
    first level holds, after the last the last. An attack-decay hit:
    envelope(x, [(0, 0), (0.005, 1), (0.25, 0.3), (0.6, 0)]).
    """
    y = _2d(x)
    ts = np.array([p[0] for p in points], dtype=np.float64)
    lv = np.array([p[1] for p in points], dtype=np.float64)
    if db:
        lv = 10 ** (lv / 20.0)
    g = np.interp(np.arange(len(y)) / SR, ts, lv)
    return (y * g[:, None]).astype(np.float32)


def _sos(x, sos):
    return signal.sosfilt(sos, _2d(x), axis=0).astype(np.float32)


def lowpass(x, hz, order=4):
    """Butterworth low-pass: keeps below `hz`. Causal, as a real filter is."""
    return _sos(x, signal.butter(order, hz, "lowpass", fs=SR, output="sos"))


def highpass(x, hz, order=4):
    """Butterworth high-pass: keeps above `hz`."""
    return _sos(x, signal.butter(order, hz, "highpass", fs=SR, output="sos"))


def bandpass(x, low_hz, high_hz, order=2):
    return _sos(x, signal.butter(order, [low_hz, high_hz], "bandpass", fs=SR, output="sos"))


def _biquad(kind, hz, db, q):
    # Robert Bristow-Johnson's Audio EQ Cookbook.
    a = 10 ** (db / 40.0)
    w = 2 * np.pi * hz / SR
    cw, alpha = np.cos(w), np.sin(w) / (2 * q)
    if kind == "peak":
        b = [1 + alpha * a, -2 * cw, 1 - alpha * a]
        d = [1 + alpha / a, -2 * cw, 1 - alpha / a]
    else:
        s = 2 * np.sqrt(a) * alpha
        sign = 1 if kind == "low" else -1
        b = [a * ((a + 1) - sign * (a - 1) * cw + s),
             sign * 2 * a * ((a - 1) - sign * (a + 1) * cw),
             a * ((a + 1) - sign * (a - 1) * cw - s)]
        d = [(a + 1) + sign * (a - 1) * cw + s,
             -sign * 2 * ((a - 1) + sign * (a + 1) * cw),
             (a + 1) + sign * (a - 1) * cw - s]
    return np.array([b + d]) / d[0]


def eq(x, hz, db, q=1.0):
    """A peaking EQ band: `db` of boost or cut centred on `hz`, width `q`."""
    return _sos(x, _biquad("peak", hz, db, q))


def low_shelf(x, hz, db, q=0.707):
    """Boost or cut everything below `hz` by `db`."""
    return _sos(x, _biquad("low", hz, db, q))


def high_shelf(x, hz, db, q=0.707):
    """Boost or cut everything above `hz` by `db`."""
    return _sos(x, _biquad("high", hz, db, q))


def trim(x, start=0.0, end=None):
    """The part of a sound from `start` to `end` seconds (end None: to the end)."""
    y = _2d(x)
    return y[samples(start):(None if end is None else samples(end))].copy()


def pad(x, before=0.0, after=0.0):
    y = _2d(x)
    return np.concatenate([np.zeros((samples(before), y.shape[1]), np.float32), y,
                           np.zeros((samples(after), y.shape[1]), np.float32)])


def pan(x, position):
    """Balance a stereo sound: -1 left only, 0 as it is, +1 right only.

    The far side is turned down, never the near side up, so nothing gets
    louder or clips (the engine places a sound in the stereo field itself).
    """
    y = _2d(x)
    g = np.array([min(1.0, 1.0 - position), min(1.0, 1.0 + position)], np.float32)
    return (y * g[None, :]).astype(np.float32)


def reverse(x):
    return _2d(x)[::-1].copy()


def peak_db(x):
    p = float(np.max(np.abs(x))) if np.size(x) else 0.0
    return 20 * np.log10(p) if p > 0 else -np.inf


def normalize(x, peak=-1.0):
    """Scale so the sample peak sits at `peak` dBFS."""
    return gain(x, peak - peak_db(x))


def match_loudness(x, reference, offset_db=0.0):
    """Scale to the integrated loudness of `reference` (array or path), plus offset.

    Only the gain is changed; check the result's true peak (loudness.measure)
    before writing it, since a quiet, peaky sound can be made to clip. Measure
    the written .ogg too: Vorbis moves integrated loudness by a few tenths of
    an LU (0.2 LU up on the big drill's loop, 2026-10-11).
    """
    import loudness  # here, not at the top: loudness.py imports nothing from sfx
    ref = load(reference) if not isinstance(reference, np.ndarray) else reference
    target, ours = loudness.measure(ref, SR)["integrated"], loudness.measure(x, SR)["integrated"]
    if target is None or ours is None:
        raise ValueError("too short to have an integrated loudness (under 0.4 s)")
    return gain(x, target - ours + offset_db)


# --- layering --------------------------------------------------------------

def layer(*sounds):
    """Sum sounds that all start at 0; the result is as long as the longest."""
    sounds = [_2d(s) for s in sounds]
    out = np.zeros((max(len(s) for s in sounds), sounds[0].shape[1]), np.float32)
    for s in sounds:
        out[:len(s)] += s
    return out


class Mix:
    """A timeline of a fixed length that sounds are placed on.

        m = Mix(loop_seconds(24, 0.4))                  # one 24-frame loop at 0.4
        m.add(bed, loop=True, gain_db=-6)
        m.add(thud, frame=5, speed=0.4)                 # lands on frame 5
        m.add(tick, ms=120)
        out = m.render()

    A sound that runs past the end is cut there, unless `wrap=True`, which
    folds its tail back to the start -- what a loop that repeats in game
    hears. `loop=True` repeats a sound from its start to the end of the mix.
    """

    def __init__(self, length, sr=SR, channels=CHANNELS):
        self.sr = sr
        self.buf = np.zeros((samples(length, sr), channels), np.float32)

    def add(self, sound, at=0.0, *, ms=None, frame=None, speed=None,
            gain_db=0.0, loop=False, wrap=False):
        """Place a sound at `at` seconds, or `ms`, or `frame` of an animation at `speed`."""
        if ms is not None:
            at = ms / 1000.0
        if frame is not None:
            if speed is None:
                raise ValueError("a frame needs the animation_speed it is a frame of")
            at = frame / speed / TICKS_PER_SECOND
        s = gain(sound, gain_db)
        n, start = len(self.buf), samples(at, self.sr)
        if loop and len(s):
            reps = int(np.ceil((n - start) / len(s))) if n > start else 0
            s = np.tile(s, (reps, 1))[:max(n - start, 0)]
        end = min(n, start + len(s))
        if start < n:
            self.buf[start:end] += s[:end - start]
        if wrap and start < n < start + len(s):
            tail = s[n - start:]
            while len(tail):
                k = min(len(tail), n)
                self.buf[:k] += tail[:k]
                tail = tail[k:]
        return self

    def render(self):
        return self.buf.copy()


if __name__ == "__main__":
    print(__doc__)
    print(f"Factorio data: {data_dir()}")
