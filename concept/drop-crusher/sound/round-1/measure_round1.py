#!/usr/bin/env python3
"""Round 1's figures: each accent of each option beside today's, and the sheet.

  <venv>/bin/python concept/drop-crusher/sound/round-1/measure_round1.py [--captures DIR]

Run the option scripts first. Writes, beside this file, figures.json and
figures.png (the sheet), and prints the table.

Per accent file (today's: sound/drop-crusher/; each option's: round-1/<X>/):

  LUFS     integrated loudness (loudness.py, BS.1770); blank under 0.4 s
  M max    the loudest 400 ms block (loudness.py): the figure that compares
           one-shots, and the one each option is level-matched on
  peak     sample peak, dBFS; dBTP, the 4x-oversampled peak (loudness.py)
  attack   10-90 % rise time of the envelope, ms: the mono mix's RMS over a
           1 ms sliding window; from its first sample at 10 % of its maximum
           to its first at 90 %
  steepest the steepest 1 ms step of that envelope within 30 ms of its 10 %
           point, dB/ms: how hard the strike hits. A fade-in moves the 10 %
           point later, so the 10-90 % time can shrink while the strike gets
           softer (the drop's hit peaks 16 ms in); this is the figure that
           shows it
  >4 kHz   the share of the file's energy above 4 kHz, % (the mono mix's
           power spectrum, whole file)

Also each set as the game mixes it (review.clip_audio: bed and accents at the
volumes machines.lua gives them, the frames it cues them on): one crusher for
three strokes, and six -- the same sound six times, started 0, 37, 83, 121, 158
and 203 ticks apart as in the bank capture -- summed with no distance falloff,
the worst case. And with --captures, every MP4 in DIR named round1-*.mp4 (the
capture's own recordings): its audio from the machine's start, measured the
same way.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "tools" / "audio"))
sys.path.insert(0, str(HERE.parent))

import numpy as np  # noqa: E402
import imageio_ffmpeg  # noqa: E402
import sfx  # noqa: E402
import loudness  # noqa: E402
import review  # noqa: E402
import drop_crusher_sound as dc  # noqa: E402

SETS = {"today": REPO / "sound" / "drop-crusher", "A": HERE / "A", "B": HERE / "B", "C": HERE / "C"}
LABEL = {"today": "today (shipped)", "A": "A gentle: 8 kHz, 35 %, 5 ms",
         "B": "B medium: 5 kHz, 60 %, 10 ms", "C": "C strong: 3.5 kHz, 85 %, 15 ms"}
ACCENTS = ("drop", "trip", "pawl")
OFFSETS = (0, 37, 83, 121, 158, 203)       # the bank capture's starts, ticks
STROKE_TICKS = int(round(24 / dc.SPEED))   # 240


def mono(x):
    return x.astype(np.float64).mean(axis=1)


def envelope(x, win=0.001):
    w = sfx.samples(win)
    return np.sqrt(np.convolve(mono(x) ** 2, np.ones(w) / w, mode="full")[:len(x)])


def attack_ms(x):
    e = envelope(x)
    p = e.max()
    t10, t90 = int(np.argmax(e >= 0.1 * p)), int(np.argmax(e >= 0.9 * p))
    return (t90 - t10) / sfx.SR * 1000.0


def steepest(x):
    e = envelope(x)
    p = e.max()
    edb = 20 * np.log10(e / p + 1e-9)
    i0, w, n = int(np.argmax(e >= 0.1 * p)), sfx.samples(0.001), sfx.samples(0.03)
    return float((edb[i0 + w:i0 + n] - edb[i0:i0 + n - w]).max())


def hf_share(x, hz=4000.0):
    spec = np.abs(np.fft.rfft(mono(x))) ** 2
    f = np.fft.rfftfreq(len(x), 1.0 / sfx.SR)
    return float(spec[f > hz].sum() / spec.sum() * 100.0)


def figures(x):
    m = loudness.measure(x, sfx.SR)
    return {"lufs": m["integrated"], "mmax": m["momentary_max"], "dbtp": m["true_peak"],
            "peak_dbfs": float(20 * np.log10(np.abs(x).max())), "attack_ms": attack_ms(x),
            "steepest_db_ms": steepest(x), "hf_pct": hf_share(x)}


def clip(d):
    s = lambda n: str(d / f"{n}.ogg")  # noqa: E731
    acc = [(dc.DROP_FRAME, s("drop"), dc.VOLUME["drop"]), (dc.TRIP_FRAME, s("trip"), dc.VOLUME["trip"])]
    acc += [(f, s("pawl"), dc.VOLUME["pawl"]) for f in dc.PAWL_FRAMES]
    return review.Clip(frames=None, speed=dc.SPEED, bed=s("bed"), bed_volume=dc.VOLUME["bed"], accents=acc)


def mixes(d):
    c = clip(d)
    one = review.clip_audio(c, 24, 3 * STROKE_TICKS)
    total = 3 * STROKE_TICKS + max(OFFSETS)
    six = np.zeros((sfx.samples(total / 60), 2), np.float32)
    for off in OFFSETS:
        a = review.clip_audio(c, 24, total - off)
        s = sfx.samples(off / 60)
        six[s:s + len(a)] += a[:len(six) - s]
    six = six[sfx.samples(max(OFFSETS) / 60):]          # all six running
    return {"one": figures(one), "six": figures(six)}


def mp4_audio(path):
    out = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(path), "-vn",
                          "-f", "f32le", "-ac", "2", "-ar", str(sfx.SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32).reshape(-1, 2)


def captures(d, lead=0.6):
    res = {}
    for p in sorted(Path(d).rglob("round1-*.mp4")):
        x = mp4_audio(p)[sfx.samples(lead):]               # the MP4 opens 0.6 s before the start
        res[p.stem] = {"file": str(p), **figures(x)}
    return res


# --- the sheet -----------------------------------------------------------------

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
COLOUR = {"today": "#52514e", "A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a"}   # reference palette slots 1-3


def sheet(per, mix, cap, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2,
                         "ytick.color": INK2, "axes.edgecolor": GRID, "axes.facecolor": SURF,
                         "figure.facecolor": SURF, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6})
    fig = plt.figure(figsize=(15, 13.5))
    gs = fig.add_gridspec(4, 3, height_ratios=[1.1, 1.0, 1.0, 0.95], hspace=0.45, wspace=0.22)
    fig.suptitle("Drop Crusher, round 1: softer attacks, less high end (options A/B/C beside today's)",
                 fontsize=14, x=0.02, ha="left", y=0.99)
    fig.text(0.02, 0.952, "Each option: a low-pass (kHz), a transient shaper (% of the way from each crack to the "
             "body under it) and a fade-in on the strike (ms). Accents level-matched to today's on momentary max "
             "(M max),\nso the options differ in character, not loudness. Bed and frames unchanged.",
             color=INK2, fontsize=9.5)
    fig.text(0.02, 0.928, "attack 10-90 %: rise time of the 1 ms RMS envelope. A fade-in moves its 10 % point later, so "
             "it can shrink as the strike softens; 'steepest' (the hardest 1 ms step, dB/ms) shows how hard it hits.",
             color=INK2, fontsize=9.5)

    ax = fig.add_subplot(gs[0, :])
    ax.axis("off")
    cols = ["accent", "set", "LUFS", "M max", "peak dBFS", "dBTP", "attack (ms)", "steepest (dB/ms)",
            "> 4 kHz (%)"]
    rows = []
    for a in ACCENTS:
        for k in SETS:
            f = per[k][a]
            rows.append([a if k == "today" else "", LABEL[k], "-" if f["lufs"] is None else f"{f['lufs']:.1f}",
                         f"{f['mmax']:.1f}", f"{f['peak_dbfs']:.1f}", f"{f['dbtp']:.1f}",
                         f"{f['attack_ms']:.1f}", f"{f['steepest_db_ms']:.1f}", f"{f['hf_pct']:.1f}"])
    t = ax.table(cellText=rows, colLabels=cols, loc="center", cellLoc="right", colLoc="right",
                 colWidths=[0.06, 0.2, 0.07, 0.07, 0.08, 0.07, 0.13, 0.11, 0.09])
    t.auto_set_font_size(False)
    t.set_fontsize(9)
    t.scale(1, 1.25)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(GRID)
        cell.set_facecolor(SURF)
        if r == 0:
            cell.set_text_props(color=INK2, weight="bold")
        if c in (0, 1):
            cell.set_text_props(ha="left")
            cell._loc = "left"
        if c == 1 and r > 0:
            k = list(SETS)[(r - 1) % len(SETS)]
            cell.set_text_props(color=INK, weight="bold" if k == "today" else "normal")

    for i, a in enumerate(ACCENTS):
        ax = fig.add_subplot(gs[1, i])
        for k, d in SETS.items():
            x, _ = sfx.read(d / f"{a}.ogg")
            e = envelope(x)
            t_ms = np.arange(len(e)) / sfx.SR * 1000
            n = sfx.samples(0.06)
            ax.plot(t_ms[:n], 20 * np.log10(e[:n] + 1e-6), color=COLOUR[k], lw=2 if k != "today" else 1.6,
                    ls="--" if k == "today" else "-", label=LABEL[k])
        ax.set_ylim(-60, 0)
        ax.set_xlim(0, 60)
        ax.set_title(f"{a}.ogg: the first 60 ms (envelope, 1 ms RMS)", loc="left", fontsize=10)
        ax.set_xlabel("ms from the file's start")
        ax.set_ylabel("dBFS")
        if i == 0:
            ax.legend(frameon=False, fontsize=8, loc="lower right")

    for i, a in enumerate(ACCENTS):
        ax = fig.add_subplot(gs[2, i])
        for k, d in SETS.items():
            x, _ = sfx.read(d / f"{a}.ogg")
            spec = np.abs(np.fft.rfft(mono(x), n=1 << 17)) ** 2
            f = np.fft.rfftfreq(1 << 17, 1.0 / sfx.SR)
            centres = np.geomspace(50, 20000, 120)
            band = [spec[(f >= c / 2 ** (1 / 12)) & (f < c * 2 ** (1 / 12))].mean() for c in centres]
            ax.semilogx(centres, 10 * np.log10(np.array(band) + 1e-12), color=COLOUR[k],
                        lw=2 if k != "today" else 1.6, ls="--" if k == "today" else "-", label=LABEL[k])
        ax.axvline(4000, color=INK2, lw=0.8, ls=":")
        ax.set_xlim(50, 20000)
        top = ax.get_ylim()[1]
        ax.set_ylim(top - 70, top)
        ax.set_title(f"{a}.ogg: spectrum (1/6 octave); dotted line 4 kHz", loc="left", fontsize=10)
        ax.set_xlabel("Hz")
        ax.set_ylabel("dB (relative)")

    ax = fig.add_subplot(gs[3, :])
    ax.axis("off")
    cols = ["set", "one: LUFS", "M max", "dBTP", "> 4 kHz %", "six, summed: LUFS", "M max", "dBTP", "> 4 kHz %"]
    rows = []
    for k in SETS:
        o, s = mix[k]["one"], mix[k]["six"]
        rows.append([LABEL[k]] + [f"{v:.1f}" for v in (o["lufs"], o["mmax"], o["dbtp"], o["hf_pct"],
                                                         s["lufs"], s["mmax"], s["dbtp"], s["hf_pct"])])
    for name, c in (cap or {}).items():
        if name.endswith("-one"):
            six = cap.get(name[:-4] + "-six")
            rest = ([f"{six['lufs']:.1f}", f"{six['mmax']:.1f}", f"{six['dbtp']:.1f}", f"{six['hf_pct']:.1f}"]
                    if six else ["", "", "", ""])
            rows.append([f"in game: {name[7:-4]}", f"{c['lufs']:.1f}", f"{c['mmax']:.1f}", f"{c['dbtp']:.1f}",
                         f"{c['hf_pct']:.1f}"] + rest)
    t = ax.table(cellText=rows, colLabels=cols, loc="upper center", cellLoc="right", colLoc="right",
                 colWidths=[0.22, 0.12, 0.08, 0.08, 0.08, 0.14, 0.08, 0.08, 0.08])
    t.auto_set_font_size(False)
    t.set_fontsize(8.5)
    t.scale(1, 1.2)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(GRID)
        cell.set_facecolor(SURF)
        if r == 0:
            cell.set_text_props(color=INK2, weight="bold")
        if c == 0:
            cell.set_text_props(ha="left")
            cell._loc = "left"
    ax.set_title("As played. Offline: machines.lua's volumes and frames, three strokes; six = the same, started 0, "
                 "37, 83, 121, 158, 203 ticks apart, summed with no falloff.\nIn game: the sound capture's "
                 "recording (null sink, 48 kHz), from the machine's start; six = the bank capture, heard from "
                 "its top middle crusher.", loc="left", fontsize=9.5)
    fig.savefig(path, dpi=110)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--captures", help="folder of the capture MP4s (round1-*.mp4)")
    args = ap.parse_args()
    per = {k: {a: figures(sfx.read(d / f"{a}.ogg")[0]) for a in ACCENTS} for k, d in SETS.items()}
    mix = {k: mixes(d) for k, d in SETS.items()}
    cap = captures(args.captures) if args.captures else {}
    (HERE / "figures.json").write_text(json.dumps({"accents": per, "mixes": mix, "captures": cap}, indent=1))
    print(f"{'accent':6s} {'set':6s} {'LUFS':>6s} {'M max':>6s} {'peak':>6s} {'dBTP':>6s} {'attack':>7s} {'>4k%':>6s}")
    for a in ACCENTS:
        for k in SETS:
            f = per[k][a]
            lufs = "-" if f["lufs"] is None else f"{f['lufs']:.1f}"
            print(f"{a:6s} {k:6s} {lufs:>6s} {f['mmax']:6.1f} {f['peak_dbfs']:6.1f} {f['dbtp']:6.1f} "
                  f"{f["attack_ms"]:7.1f} {f["steepest_db_ms"]:6.1f} {f["hf_pct"]:6.1f}")
    for k in SETS:
        o, s = mix[k]["one"], mix[k]["six"]
        print(f"mix {k:6s} one: I {o['lufs']:.1f} M {o['mmax']:.1f} TP {o['dbtp']:.1f} hf {o['hf_pct']:.1f}  "
              f"six: I {s['lufs']:.1f} M {s['mmax']:.1f} TP {s['dbtp']:.1f} hf {s['hf_pct']:.1f}")
    for n, c in cap.items():
        print(f"captured {n}: I {c['lufs']:.1f} M {c['mmax']:.1f} TP {c['dbtp']:.1f} peak {c['peak_dbfs']:.1f} "
              f"hf {c['hf_pct']:.1f}")
    sheet(per, mix, cap, HERE / "figures.png")
    print(HERE / "figures.png")


if __name__ == "__main__":
    main()
