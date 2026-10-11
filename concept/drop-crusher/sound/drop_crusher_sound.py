#!/usr/bin/env python3
"""The Drop Crusher's sounds, built from the spec's §3.4: a bed and three accents.

  tools/audio/.venv/bin/python concept/drop-crusher/sound/drop_crusher_sound.py

writes sound/drop-crusher/bed.ogg, pawl.ogg, trip.ogg and drop.ogg, then reads
each back and checks it: 44.1 kHz stereo Vorbis, sample peak under 1.0, and for
the bed the wrap measured.

**The stroke** is 24 frames at 0.1 frames a tick in game (animation_speed 0.2 x
crafting speed 1 x animation_progress 0.5, measured in a client: machines.lua),
so four seconds, one drop a craft. Frames 0 to 16 are the geared wind-up, 16 the
top, where the pawl trips; 17 to 23 the fall; frame 0 the landing. A frame is
1/6 s: the pawl clicks at 0.667, 1.333 and 2.000 s, the trip at 2.667 s.

**Which frames click.** §3.4 says the pawl clicks "on the wind-up (frames 0-16,
every fourth frame)": 0, 4, 8, 12 and 16. Frame 0 already carries the drop and
frame 16 the trip -- the trip *is* the pawl's last tooth, kicking clear -- so the
clicks are wired on 4, 8 and 12 and the other two are left to the bigger sounds
(a click under the drop would never be heard, and costs a sound).

**bed.ogg** -- a low motor hum. A 47 Hz rotor and its harmonics; a faint 611 Hz
whine from a 13-tooth pinion on it; vanilla's crusher loop
(`crusher-loop.ogg`) an octave down and under 600 Hz, so its crunching becomes
the gearbox's grumble; brown noise under 200 Hz. 8 s, two strokes: every tone
repeats exactly in 8 s and the vanilla layer is crossfaded into its own start.
And a faint breath of cooling-fan air, 1.2 to 6 kHz: without it the bed has
nothing above 2 kHz but the codec's own noise, and Vorbis's few-thousandths
mismatch between a file's two ends then stood 23 dB out of it at the wrap
(measured, -74 against -97 dBFS). The loop is also turned round to start at
its quietest zero crossing (quiet_start), which takes the step across the wrap
from 0.0052 to under 0.001.

**pawl.ogg** -- a small, dry click: one tooth of the cryogenic plant's gears
(`cp-anim5-gears.ogg`), a 3 ms click and a short ping.

**trip.ogg** -- frame 16. A sharp metallic clack as the pawl kicks clear: the
foundry's clamp (`foundry-clamp.ogg`), with a struck-steel click whose partials
(1180, 2770, 4430 Hz, inharmonic, as a bar's are) ring for under 0.1 s.

**drop.ogg** -- frame 0. A crushing impact with grit and rock breaking: an oxide
asteroid breaking (`asteroid-damage-oxide-big-1.ogg`) for the break, the mech
armour landing on rock (`mech-armor-land-rock-2.ogg`) for the weight's hit, two
handfuls of pebbles (`walking/pebble/stones-1`, `-2`) scattering after it, a
falling sine for the weight and a crackle of grit that thins out over 0.7 s.

Levels: matched as a whole to the vanilla crusher as it plays (its loop at 0.8);
the volume each Sound should carry is VOLUME below. review_drop_crusher.py
measures both mixes.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools" / "audio"))

import numpy as np  # noqa: E402
import sfx  # noqa: E402
import loudness  # noqa: E402

OUT = REPO / "sound" / "drop-crusher"
FRAMES, SPEED = 24, 0.1            # as played in game
DROP_FRAME, TRIP_FRAME = 0, 16
PAWL_FRAMES = (4, 8, 12)

# What each Sound's `volume` should be when it is wired (proposed, not wired).
VOLUME = {"bed": 0.8, "pawl": 0.6, "trip": 0.5, "drop": 0.35}

CRUSHER = "__space-age__/sound/entity/crusher/crusher-loop.ogg"
BED_SECONDS = 8.0
AIR_DB = -20.0     # the fan's air: enough that the loop's wrap sits inside its own hiss


def loopify(x, length, xfade):
    """`length` s of `x` that loops: its continuation after `length` crossfaded into its start."""
    n, k = sfx.samples(length), sfx.samples(xfade)
    if len(x) < n + k:
        raise ValueError("loopify: need length + xfade of material")
    y = x[:n].copy()
    t = np.linspace(0.0, 1.0, k, dtype=np.float64)[:, None]
    y[:k] = x[:k] * np.sin(0.5 * np.pi * t) + x[n:n + k] * np.cos(0.5 * np.pi * t)
    return y.astype(np.float32)


def as_loop(f, x):
    """Apply filter `f` to a loop as the loop: run it over two copies and keep the second."""
    return f(np.tile(x, (2, 1)))[len(x):]


def quiet_start(x, window=0.02):
    """Turn a loop round so it starts, and wraps, at its quietest zero crossing.

    Vorbis reconstructs a file's two ends with a few thousandths of error, which is
    the signal there times a little; started where the loop is near silent the two
    ends meet with almost no step. Turning a loop round keeps it a loop.
    """
    w = sfx.samples(window)
    env = np.sqrt(np.convolve((x.astype(np.float64) ** 2).mean(1), np.ones(w) / w, mode="same"))
    r = int(np.argmin(env + 0.5 * np.abs(x).max(1)))
    return np.roll(x, -r, axis=0)


def bed():
    T = BED_SECONDS
    t = np.arange(sfx.samples(T)) / sfx.SR
    rotor = sum(a * sfx.tone(T, 47.0 * h) for h, a in ((1, 0.5), (2, 0.8), (3, 0.5), (4, 0.35), (6, 0.2), (8, 0.1)))
    rotor = rotor * (1.0 + 0.06 * np.sin(2 * np.pi * 0.5 * t))[:, None]       # 4 slow beats in 8 s
    whine = sfx.tone(T, 611.0) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * t))[:, None]

    grumble = sfx.load(CRUSHER)
    grumble = sfx.pitch(grumble, -12)                    # 32.7 s
    grumble = sfx.lowpass(grumble, 600)
    grumble = loopify(sfx.trim(grumble, 3.0), T, 1.0)
    floor = sfx.lowpass(sfx.noise(T + 3.0, "brown", seed=21), 200)
    floor = loopify(sfx.trim(floor, 1.0), T, 1.0)
    air = sfx.bandpass(sfx.noise(T + 3.0, "pink", seed=23), 1200, 6000)
    air = loopify(sfx.trim(air, 1.0), T, 1.0)

    mix = (sfx.gain(rotor, -12.0) + sfx.gain(whine, -36.0) + sfx.gain(grumble, 0.0)
           + sfx.gain(floor, -20.0) + sfx.gain(air, AIR_DB))
    mix = as_loop(lambda v: sfx.highpass(v, 30, order=2), mix)
    # Level: the vanilla crusher loop's file level, less 3 LU: a hum under the drops.
    return quiet_start(sfx.match_loudness(mix, CRUSHER, -3.0))


def pawl():
    tooth = sfx.trim(sfx.load("__space-age__/sound/entity/cryogenic-plant/cp-anim5-gears.ogg"), 0.0, 0.035)
    tooth = sfx.fade(tooth, 0.0005, 0.02)
    click = sfx.fade(sfx.bandpass(sfx.noise(0.003, seed=7), 1500, 6000), 0.0003, 0.002)
    ping = sfx.envelope(sfx.tone(0.03, 3100.0), [(0, 1), (0.03, 0)])
    x = sfx.layer(tooth, sfx.gain(click, -10), sfx.gain(ping, -22))
    x = sfx.highpass(sfx.pad(x, after=0.03), 400)
    return sfx.normalize(x, -6.0)


def trip():
    clamp = sfx.load("__space-age__/sound/entity/foundry/foundry-clamp.ogg")
    strike = sfx.fade(sfx.bandpass(sfx.noise(0.006, seed=9), 700, 8000), 0.0003, 0.004)
    ring = sfx.layer(*[sfx.envelope(sfx.gain(sfx.tone(0.12, hz), db), [(0, 1), (d, 0)])
                       for hz, db, d in ((1180.0, -6, 0.09), (2770.0, -9, 0.06), (4430.0, -14, 0.04))])
    x = sfx.layer(sfx.gain(clamp, -3), sfx.gain(strike, 2), sfx.gain(ring, 0))
    x = sfx.high_shelf(sfx.highpass(x, 120), 2500, 4.0)
    return sfx.normalize(x, -2.0)


def grit(length, seed, rate0=420.0, tail=0.7):
    """Sparse, thinning crackle: Poisson clicks, each a 1-3 ms burst of bandpassed noise."""
    rng = np.random.default_rng(seed)
    out = sfx.silence(length)
    t = 0.0
    while True:
        rate = rate0 * max(0.0, 1.0 - t / tail) ** 2 + 1e-6
        t += rng.exponential(1.0 / rate)
        if t >= min(length, tail):
            break
        n = sfx.samples(rng.uniform(0.001, 0.003))
        s = sfx.samples(t)
        burst = rng.standard_normal((n, 2)) * np.hanning(n)[:, None] * rng.uniform(0.2, 1.0)
        out[s:s + n] += burst[:len(out) - s].astype(np.float32)
    return sfx.bandpass(out, 1800, 7500)


def drop():
    L = 1.6
    brk = sfx.trim(sfx.load("__space-age__/sound/entity/asteroid/asteroid-damage-oxide-big-1.ogg"), 0, L)
    hit = sfx.load("__space-age__/sound/entity/mech-armor/mech-armor-land-rock-2.ogg")
    peb1 = sfx.load("__base__/sound/walking/pebble/stones-1.ogg")
    peb2 = sfx.load("__base__/sound/walking/pebble/stones-2.ogg")
    thump = sfx.envelope(sfx.tone(0.35, 75.0, to_hz=42.0),
                         [(0, 0), (0.002, 1), (0.06, 0.6), (0.25, 0.1), (0.35, 0)])
    m = sfx.Mix(L)
    m.add(brk, gain_db=-3)
    m.add(hit, gain_db=0)
    m.add(thump, gain_db=-8)
    m.add(peb1, ms=25, gain_db=-4)
    m.add(peb2, ms=110, gain_db=-9)
    m.add(grit(L, seed=4), gain_db=-6)
    x = sfx.fade(m.render(), fade_out=0.3)
    x = sfx.highpass(x, 30, order=2)
    x = sfx.normalize(x, 0.0)
    x = np.tanh(1.6 * x) / np.tanh(1.6)                  # pull the crack's peak down to its body
    return sfx.normalize(x, -1.0)


# --- checks ------------------------------------------------------------------

def wrap_check(x, hz=2000, win=0.005):
    """The wrap, measured as a click would show: energy above `hz` in a `win` window
    centred on the wrap of the decoded file played three times over, against the same
    window at every other point of the loop. A click is a burst of high frequencies, so
    the wrap passes if that window is no louder than the loop's own 99th percentile.
    Also the plain step across the wrap, against every sample-to-sample step."""
    n, w = len(x), sfx.samples(win)
    hf = sfx.highpass(np.tile(x, (3, 1)), hz).mean(axis=1)

    def level(c):
        s = hf[c - w // 2:c + w // 2]
        return 20 * np.log10(np.sqrt(float((s ** 2).mean())) + 1e-12)
    others = np.array([level(c) for c in range(n + w, 2 * n - w, w)])
    at_wrap = level(2 * n)
    steps = np.max(np.abs(np.diff(x, axis=0)), axis=1)
    step = float(np.max(np.abs(x[0] - x[-1])))
    return {"hf_wrap_db": at_wrap, "hf_median_db": float(np.median(others)),
            "hf_p99_db": float(np.percentile(others, 99)), "hf_max_db": float(others.max()),
            "hf_pctile": float((others < at_wrap).mean() * 100),
            "step": step, "step_pctile": float((steps < step).mean() * 100)}


def check(path, loop=False):
    import soundfile as sf
    info = sf.info(str(path))
    x, sr = sfx.read(path)
    m = loudness.measure(x, sr)
    peak = float(np.max(np.abs(x)))
    ok = (info.samplerate == 44100 and info.channels == 2 and info.format == "OGG"
          and info.subtype == "VORBIS" and peak <= 1.0)
    res = {"file": str(path), "sr": info.samplerate, "ch": info.channels,
           "fmt": f"{info.format}/{info.subtype}", "secs": round(len(x) / sr, 4),
           "peak": peak, "lufs": m["integrated"], "mmax": m["momentary_max"],
           "dbtp": m["true_peak"]}
    if loop:
        w = wrap_check(x)
        res["wrap"] = w
        ok = ok and w["hf_wrap_db"] <= w["hf_p99_db"]
    res["ok"] = ok
    return res


def main():
    files = {"bed": bed(), "pawl": pawl(), "trip": trip(), "drop": drop()}
    for name, x in files.items():
        sfx.write(OUT / f"{name}.ogg", x)
    for name in files:
        r = check(OUT / f"{name}.ogg", loop=(name == "bed"))
        line = (f"{name:8s} {r['fmt']} {r['sr']} Hz {r['ch']} ch {r['secs']:.3f} s  "
                f"peak {20 * np.log10(r['peak']):+.2f} dBFS  {r['dbtp']:+.2f} dBTP  "
                f"I {r['lufs'] if r['lufs'] is not None else float('nan'):.1f}  M {r['mmax']:.1f}")
        if "wrap" in r:
            w = r["wrap"]
            line += (f"\n         wrap: >2 kHz in 5 ms {w['hf_wrap_db']:.1f} dBFS against the loop's own "
                     f"median {w['hf_median_db']:.1f}, p99 {w['hf_p99_db']:.1f}, max {w['hf_max_db']:.1f} "
                     f"(percentile {w['hf_pctile']:.1f}); step {w['step']:.4f} (percentile {w['step_pctile']:.1f})")
        print(line + ("  OK" if r["ok"] else "  FAIL"))


if __name__ == "__main__":
    main()
