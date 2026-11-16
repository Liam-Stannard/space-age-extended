#!/usr/bin/env python3
"""The Ballast Drill's sounds, built from the spec's §3.4: a bed and two accents.

  tools/audio/.venv/bin/python concept/ballast-drill/sound/ballast_drill_sound.py

writes sound/ballast-drill/bed.ogg, landing.ogg and ratchet.ogg, then reads each
back and checks it: 44.1 kHz stereo Vorbis, sample peak under 1.0, and for the bed
the wrap measured (the step across it against every other step in the file).

**The stroke** is 24 frames at 0.4 frames a tick: one second. Frame 5 is the
landing (0.208 s), frame 23 the top of the lift (0.958 s).

**bed.ogg** -- a low, slow winch drone. Vanilla's big mining drill working loop
(`big-mining-drill-working-loop.ogg`, 4.32 s), seven semitones down and
low-passed, so its whirr becomes a slow grind; under it a 41 Hz drone with its
octave, and a brown-noise rumble, all swelling over a 6 s period with a third
of a hertz in it so it never pulses against the one-second stroke. The vanilla
layer is made to loop by crossfading its own continuation into its start; the
tones repeat exactly in 6 s, so they need none.

**landing.ogg** -- frame 5. A deep, dead thud with a short ground rumble: the
stomper's stomp (`stomper-stomp-1.ogg`, the deepest impact vanilla has, its
energy under 120 Hz) cut to 0.85 s and mostly gone by 0.6 s; the mech armour
landing on concrete (`mech-armor-land-concrete-2.ogg`) for the hit itself,
low-passed so nothing rings; a sine falling 62 to 34 Hz for the weight; brown
noise under 110 Hz for the ground; a lift at 160 Hz so small speakers hear it,
and a soft saturator that brings the hit's peak down into the body. Silent by
0.85 s, before the next landing a second later.

**ratchet.ogg** -- frame 23. A small tick: the first tooth of the refinery's gear
(`oil-refinery-gear-1.ogg`), a 3 ms click and a short pawl ping, then a second,
softer tooth 40 ms later.

Levels (measured, see the report): each file sits near its vanilla counterpart's
own file level and the volume the prototype should carry is VOLUME below, so the
mix as heard matches the big mining drill's (working loop 0.3, drilling loop 0.7,
start clank 0.75) -- review_ballast_drill.py measures both.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools" / "audio"))

import numpy as np  # noqa: E402
import sfx  # noqa: E402
import loudness  # noqa: E402

OUT = REPO / "sound" / "ballast-drill"
FRAMES, SPEED = 24, 0.4
LANDING_FRAME, RATCHET_FRAME = 5, 23

# What each Sound's `volume` should be when it is wired (proposed, not wired).
VOLUME = {"bed": 0.3, "landing": 0.55, "ratchet": 0.6}   # landing 0.5 -> 0.55, Liam 2026-10-11

BMD = "__space-age__/sound/entity/big-mining-drill/"
BED_SECONDS = 6.0


def loopify(x, length, xfade):
    """`length` s of `x` that loops: its continuation after `length` crossfaded into its start."""
    n, k = sfx.samples(length), sfx.samples(xfade)
    if len(x) < n + k:
        raise ValueError("loopify: need length + xfade of material")
    y = x[:n].copy()
    t = np.linspace(0.0, 1.0, k, dtype=np.float64)[:, None]
    y[:k] = x[:k] * np.sin(0.5 * np.pi * t) + x[n:n + k] * np.cos(0.5 * np.pi * t)
    return y.astype(np.float32)


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
    wl = sfx.load(BMD + "big-mining-drill-working-loop.ogg")
    wl = np.tile(wl, (3, 1))                                # 12.96 s of a seamless loop
    grind = sfx.pitch(wl, -7)                               # 19.4 s, a fifth down
    grind = sfx.lowpass(grind, 3200, order=2)
    grind = sfx.low_shelf(grind, 140, 3.0)
    grind = sfx.trim(grind, 2.0)                            # past the filters' start-up
    grind = loopify(grind, BED_SECONDS, 0.6)

    t = np.arange(sfx.samples(BED_SECONDS)) / sfx.SR
    swell = (1.0 + 0.18 * np.sin(2 * np.pi * t / 3.0))[:, None]   # two swells in 6 s
    drone = (0.6 * sfx.tone(BED_SECONDS, 41.0, "saw") + 0.4 * sfx.tone(BED_SECONDS, 82.0))
    drone = sfx.lowpass(np.tile(drone, (2, 1)), 260)[sfx.samples(BED_SECONDS):]  # filtered as a loop
    rumble_src = sfx.lowpass(sfx.noise(BED_SECONDS + 3.0, "brown", seed=11), 120)
    rumble = loopify(sfx.trim(rumble_src, 1.0), BED_SECONDS, 0.8)

    mix = (sfx.gain(grind, 0.0) + sfx.gain(drone, -18.0) * swell + sfx.gain(rumble, -15.0) * swell)
    mix = sfx.highpass(np.tile(mix, (2, 1)), 28, order=2)[sfx.samples(BED_SECONDS):]  # filtered as a loop
    # Level: the working loop's own, less 3 LU -- "pitched down and quieter".
    return quiet_start(sfx.match_loudness(mix, BMD + "big-mining-drill-working-loop.ogg", -3.0))


def landing():
    L = 0.85
    stomp = sfx.trim(sfx.load("__space-age__/sound/enemies/stomper/stomper-stomp-1.ogg"), 0.0, L)
    stomp = sfx.envelope(stomp, [(0, 1), (0.06, 1), (0.25, 0.45), (0.6, 0.08), (L, 0)])
    hit = sfx.load("__space-age__/sound/entity/mech-armor/mech-armor-land-concrete-2.ogg")
    hit = sfx.lowpass(hit, 2200)
    body = sfx.tone(0.5, 62.0, "sine", to_hz=34.0)
    body = sfx.envelope(body, [(0, 0), (0.003, 1), (0.08, 0.7), (0.3, 0.12), (0.5, 0)])
    ground = sfx.lowpass(sfx.noise(L, "brown", seed=5), 110)
    ground = sfx.envelope(ground, [(0, 0), (0.015, 1), (0.12, 0.75), (0.45, 0.2), (L, 0)])
    # Liam, 2026-10-11: hit harder, clearly heading the Core's single sounds. The
    # weight (stomp, sine, ground) came up 3-4 dB against the hit, and a shelf under
    # 90 Hz adds to it; nothing above 2 kHz was added, so it stays dead.
    x = sfx.layer(sfx.gain(stomp, -3.0), sfx.gain(hit, 3.0), sfx.gain(body, -5.0),
                  sfx.gain(ground, -6.0))
    x = sfx.eq(x, 160, 4.0, q=0.8)            # so a laptop speaker still hears the weight
    x = sfx.low_shelf(x, 90, 3.0)
    x = sfx.highpass(x, 26, order=2)
    x = sfx.fade(sfx.trim(x, 0, L), fade_out=0.15)
    # Squeezed through a soft saturator: the hit's sharp peak comes down to the body,
    # so the thud is dense and dead rather than a click on top of a rumble.
    x = sfx.normalize(x, 0.0)
    x = np.tanh(2.2 * x) / np.tanh(2.2)
    return sfx.normalize(x, -1.0)


def ratchet():
    gear = sfx.trim(sfx.load("__base__/sound/oil-refinery-accents/oil-refinery-gear-1.ogg"), 0.015, 0.075)
    gear = sfx.fade(gear, 0.002, 0.03)
    click = sfx.bandpass(sfx.noise(0.004, seed=3), 2000, 7000)
    click = sfx.fade(click, 0.0005, 0.003)
    ping = sfx.layer(sfx.tone(0.04, 2350.0), sfx.gain(sfx.tone(0.04, 3720.0), -6))
    ping = sfx.envelope(ping, [(0, 1), (0.04, 0)], db=False)
    tooth = sfx.layer(sfx.gain(gear, 0), sfx.gain(click, -8), sfx.gain(ping, -20))
    x = sfx.Mix(0.16).add(tooth).add(tooth, ms=40, gain_db=-7).render()
    x = sfx.highpass(x, 300)
    return sfx.normalize(x, -6.0)


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
    files = {"bed": bed(), "landing": landing(), "ratchet": ratchet()}
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
