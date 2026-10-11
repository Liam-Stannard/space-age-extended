"""Loudness and peak of any sound file, ours or vanilla's, side by side.

Used to match a sound to its vanilla equivalent: a new drill should sit as loud
as vanilla's drills do, before its prototype's `volume` says anything.

  loudness.py <file> [<file> ...] [--ref <file>] [--ffmpeg]

Each file is a path or a game path ("__space-age__/sound/entity/crusher/
crusher-loop.ogg"). For each it prints:

  LUFS     integrated loudness, ITU-R BS.1770-4 / EBU R128: K-weighted, 400 ms
           blocks every 100 ms, gated at -70 LUFS and then 10 LU under the
           ungated mean. Blank for a sound under 0.4 s, which has no block.
  M max    the loudest single 400 ms block (momentary), padded with silence
           for a sound shorter than one -- the figure to compare one-shots by.
  dBTP     true-ish peak: the sample peak after 4x oversampling.
  dBFS     sample peak.

--ref <file> adds a column: the gain that brings each file's integrated
loudness to the reference's (its momentary max, for a sound too short to have
one). --ffmpeg runs the bundled ffmpeg's `ebur128` filter on each file too and
prints its integrated figure beside ours, as a check on this one.

Channels are weighted as BS.1770 does (1.0 for left, right and centre); a mono
file is one channel, not two, as ffmpeg's ebur128 has it without `dualmono`.
The tool family, where sounds live and the setup line: see sfx.py's header.
"""

import argparse
import re
import subprocess
import sys

import numpy as np
from scipy import signal

BLOCK = 0.4          # s, the gating block
STEP = 0.1           # s, blocks overlap by 75%
ABS_GATE = -70.0     # LUFS
REL_GATE = -10.0     # LU under the absolute-gated mean
OFFSET = -0.691      # BS.1770's constant


def k_weighting(sr):
    """BS.1770's two K-weighting stages as SOS, designed for any sample rate.

    The standard gives coefficients at 48 kHz only; these are the analogue
    prototype's parameters as libebur128 and ffmpeg's ebur128 derive them, so
    44.1 kHz is weighted the way those measure it.
    """
    # Stage 1, the head's high shelf.
    f0, g, q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    k = np.tan(np.pi * f0 / sr)
    vh = 10 ** (g / 20.0)
    vb = vh ** 0.4996667741545416
    a0 = 1.0 + k / q + k * k
    shelf = [(vh + vb * k / q + k * k) / a0, 2.0 * (k * k - vh) / a0,
             (vh - vb * k / q + k * k) / a0,
             1.0, 2.0 * (k * k - 1.0) / a0, (1.0 - k / q + k * k) / a0]
    # Stage 2, the RLB high-pass.
    f0, q = 38.13547087602444, 0.5003270373238773
    k = np.tan(np.pi * f0 / sr)
    a0 = 1.0 + k / q + k * k
    hp = [1.0, -2.0, 1.0, 1.0, 2.0 * (k * k - 1.0) / a0, (1.0 - k / q + k * k) / a0]
    return np.array([shelf, hp])


def _weights(channels):
    # BS.1770 channel order L, R, C, LFE, Ls, Rs; the LFE is not measured.
    if channels <= 3:
        return np.ones(channels)
    w = np.array([1.0, 1.0, 1.0, 0.0, 1.41, 1.41] + [1.0] * max(channels - 6, 0))
    return w[:channels]


def _block_powers(z, sr, pad):
    """Weighted mean square of each 400 ms block, stepping 100 ms."""
    n, step = int(round(BLOCK * sr)), int(round(STEP * sr))
    if len(z) < n:
        if not pad:
            return np.zeros(0)
        z = np.concatenate([z, np.zeros(n - len(z))])
    csum = np.concatenate([[0.0], np.cumsum(z)])
    starts = np.arange(0, len(z) - n + 1, step)
    return (csum[starts + n] - csum[starts]) / n


def _db(amplitude):
    return 20.0 * np.log10(amplitude) if amplitude > 0 else -np.inf


def _lufs(power):
    return OFFSET + 10.0 * np.log10(power) if power > 0 else -np.inf


def measure(x, sr):
    """Loudness figures of a (samples, channels) array at rate `sr`."""
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = x[:, None]
    kw = signal.sosfilt(k_weighting(sr), x, axis=0)
    z = (kw ** 2) @ _weights(x.shape[1])          # weighted sum over channels

    blocks = _block_powers(z, sr, pad=False)
    integrated = None
    gated = blocks[[_lufs(b) > ABS_GATE for b in blocks]] if len(blocks) else blocks
    if len(gated):
        rel = _lufs(gated.mean()) + REL_GATE
        final = gated[[_lufs(b) > rel for b in gated]]
        if len(final):
            integrated = _lufs(final.mean())

    momentary = _block_powers(z, sr, pad=True)
    up = signal.resample_poly(x, 4, 1, axis=0)
    true_peak = float(np.max(np.abs(up))) if up.size else 0.0
    sample_peak = float(np.max(np.abs(x))) if x.size else 0.0
    return {
        "integrated": integrated,
        "momentary_max": _lufs(momentary.max()) if len(momentary) else -np.inf,
        "true_peak": _db(true_peak),
        "sample_peak": _db(sample_peak),
        "seconds": len(x) / sr,
        "sr": sr,
        "channels": x.shape[1],
    }


def measure_file(path):
    import sfx  # here, so measure() works without sfx's dependencies loaded
    x, sr = sfx.read(path)
    return measure(x, sr)


def ffmpeg_integrated(path):
    """The bundled ffmpeg's ebur128 integrated loudness of a file, in LUFS."""
    import imageio_ffmpeg
    import sfx
    out = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-nostats", "-hide_banner",
                          "-i", str(sfx.resolve(path)), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True, check=True).stderr
    summary = out[out.rfind("Summary:"):]
    m = re.search(r"I:\s+(-?[\d.]+|-inf|nan)\s+LUFS", summary)
    return float(m.group(1)) if m else None


def _fmt(v, width=7, places=1):
    return " " * (width - 1) + "-" if v is None or not np.isfinite(v) else f"{v:{width}.{places}f}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="sound files or game paths")
    ap.add_argument("--ref", help="the file to match the others to")
    ap.add_argument("--ffmpeg", action="store_true", help="also show ffmpeg ebur128's integrated LUFS")
    a = ap.parse_args(argv)

    files = ([a.ref] if a.ref else []) + [f for f in a.files if f != a.ref]
    rows = [(f, measure_file(f)) for f in files]
    ref = rows[0][1] if a.ref else None

    head = f"{'LUFS':>7} {'M max':>7} {'dBTP':>7} {'dBFS':>7} {'secs':>6} {'Hz':>6} ch"
    if a.ffmpeg:
        head += f" {'ffmpeg':>7} {'diff':>6}"
    if ref:
        head += f" {'to ref':>7}"
    print(head + "  file")
    for i, (f, m) in enumerate(rows):
        line = (f"{_fmt(m['integrated'])} {_fmt(m['momentary_max'])} {_fmt(m['true_peak'])} "
                f"{_fmt(m['sample_peak'])} {m['seconds']:6.2f} {m['sr']:6d} {m['channels']:2d}")
        if a.ffmpeg:
            ff = ffmpeg_integrated(f)
            diff = None if ff is None or m["integrated"] is None else m["integrated"] - ff
            line += f" {_fmt(ff)} {_fmt(diff, 6, 2)}"
        if ref:
            if i == 0:
                line += f" {'(ref)':>7}"
            elif ref["integrated"] is not None and m["integrated"] is not None:
                line += f" {ref['integrated'] - m['integrated']:+7.1f}"
            else:
                line += f" {ref['momentary_max'] - m['momentary_max']:+6.1f}M"
        print(line + "  " + str(f))
    return 0


if __name__ == "__main__":
    sys.exit(main())
