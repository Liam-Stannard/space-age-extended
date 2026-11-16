#!/usr/bin/env python3
"""Round 2's figures: each accent of each option beside today's and round 1's.

  <venv>/bin/python concept/drop-crusher/sound/round-2/measure_round2.py [--captures DIR]

Run the option scripts first. Writes figures.json and figures.png beside this
file and prints the table. Every figure of round 1's measure_round1.py (LUFS,
M max, peak, dBTP, attack 10-90 %, steepest, > 4 kHz: see its header), plus:

  centroid  the spectral centroid, Hz: the power-weighted mean frequency of
            the mono mix's spectrum over the whole file -- where the sound's
            weight sits
  < 300 Hz  the share of the file's energy below 300 Hz, %: its low body

The offline mixes and the in-game captures are as round 1's (with --captures,
every round2-*.mp4 under DIR).
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROUND1 = HERE.parent / "round-1"
sys.path.insert(0, str(ROUND1))

import numpy as np  # noqa: E402
import measure_round1 as m1  # noqa: E402
import sfx  # noqa: E402

SETS = {"today": m1.REPO / "sound" / "drop-crusher",
        "R1 A": ROUND1 / "A", "R1 B": ROUND1 / "B", "R1 C": ROUND1 / "C",
        "R2 A": HERE / "A", "R2 B": HERE / "B", "R2 C": HERE / "C"}
LABEL = {"today": "today (shipped)", "R1 A": "round 1 A", "R1 B": "round 1 B", "R1 C": "round 1 C",
         "R2 A": "R2 A: -2/-3 st, light body", "R2 B": "R2 B: -4/-5 st, body",
         "R2 C": "R2 C: -7/-8 st, strong body"}
PLOTTED = ("today", "R1 B", "R2 A", "R2 B", "R2 C")
COLOUR = {"today": "#52514e", "R1 B": "#9a988f", "R2 A": "#2a78d6", "R2 B": "#eb6834", "R2 C": "#1baf7a"}
STYLE = {"today": "--", "R1 B": ":"}


BASE_FIGURES = m1.figures


def spectrum(x):
    p = np.abs(np.fft.rfft(m1.mono(x))) ** 2
    return np.fft.rfftfreq(len(x), 1.0 / sfx.SR), p


def figures(x):
    f, p = spectrum(x)
    out = BASE_FIGURES(x)
    out["centroid_hz"] = float((f * p).sum() / p.sum())
    out["low_pct"] = float(p[f < 300].sum() / p.sum() * 100)
    return out


def captures(d):
    res = {}
    for p in sorted(Path(d).rglob("round2-*.mp4")):
        x = m1.mp4_audio(p)[sfx.samples(0.6):]
        res[p.stem] = {"file": str(p), **figures(x)}
    return res


def sheet(per, mix, cap, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    INK, INK2, GRID, SURF = m1.INK, m1.INK2, m1.GRID, m1.SURF
    plt.rcParams.update({"font.size": 9, "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2,
                         "ytick.color": INK2, "axes.edgecolor": GRID, "axes.facecolor": SURF,
                         "figure.facecolor": SURF, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6})
    fig = plt.figure(figsize=(15, 17))
    gs = fig.add_gridspec(4, 3, height_ratios=[1.45, 0.9, 0.9, 0.8], hspace=0.42, wspace=0.22,
                          top=0.91, bottom=0.03)
    fig.suptitle("Drop Crusher, round 2: a heavier, lower body (options A/B/C beside today's and round 1's)",
                 fontsize=14, x=0.02, ha="left", y=0.985)
    fig.text(0.02, 0.952, "Drop and pawls: pitched down (semitones, drop/pawl), an iron body laid under the strike, "
             "then round 1 B's softening (5 kHz, 60 %, 10 ms); trip: round 1 B's file (A, B) or C's (C).\n"
             "Every accent level-matched to today's on momentary max (M max). Bed and frames unchanged. "
             "centroid: power-weighted mean frequency; < 300 Hz: share of energy below 300 Hz.",
             color=INK2, fontsize=9.5)

    ax = fig.add_subplot(gs[0, :])
    ax.axis("off")
    cols = ["accent", "set", "LUFS", "M max", "peak dBFS", "attack (ms)", "steepest (dB/ms)", "> 4 kHz %",
            "centroid (Hz)", "< 300 Hz %"]
    rows = []
    for a in m1.ACCENTS:
        for k in SETS:
            f = per[k][a]
            rows.append([a if k == "today" else "", LABEL[k], "-" if f["lufs"] is None else f"{f['lufs']:.1f}",
                         f"{f['mmax']:.1f}", f"{f['peak_dbfs']:.1f}", f"{f['attack_ms']:.1f}",
                         f"{f['steepest_db_ms']:.1f}", f"{f['hf_pct']:.1f}", f"{f['centroid_hz']:.0f}",
                         f"{f['low_pct']:.1f}"])
    t = ax.table(cellText=rows, colLabels=cols, loc="center", cellLoc="right", colLoc="right",
                 colWidths=[0.06, 0.2, 0.065, 0.065, 0.08, 0.08, 0.11, 0.08, 0.09, 0.08])
    t.auto_set_font_size(False)
    t.set_fontsize(8.5)
    t.scale(1, 1.18)
    keys = list(SETS)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(GRID)
        cell.set_facecolor(SURF)
        if r == 0:
            cell.set_text_props(color=INK2, weight="bold")
        if c in (0, 1):
            cell.set_text_props(ha="left")
            cell._loc = "left"
        if c == 1 and r > 0:
            k = keys[(r - 1) % len(keys)]
            cell.set_text_props(color=INK if k in ("today",) or k.startswith("R2") else INK2,
                                weight="bold" if k == "today" else "normal")

    for i, a in enumerate(m1.ACCENTS):
        ax = fig.add_subplot(gs[1, i])
        for k in PLOTTED:
            x, _ = sfx.read(SETS[k] / f"{a}.ogg")
            e = m1.envelope(x)
            n = min(len(e), sfx.samples(0.15))
            ax.plot(np.arange(n) / sfx.SR * 1000, 20 * np.log10(e[:n] + 1e-6), color=COLOUR[k],
                    lw=1.6 if k in STYLE else 2, ls=STYLE.get(k, "-"), label=LABEL[k])
        ax.set_ylim(-60, 0)
        ax.set_xlim(0, 150)
        ax.set_title(f"{a}.ogg: the first 150 ms (envelope, 1 ms RMS)", loc="left", fontsize=10)
        ax.set_xlabel("ms from the file's start")
        ax.set_ylabel("dBFS")
        if i == 2:
            ax.legend(frameon=False, fontsize=8, loc="upper right")

    for i, a in enumerate(m1.ACCENTS):
        ax = fig.add_subplot(gs[2, i])
        for k in PLOTTED:
            x, _ = sfx.read(SETS[k] / f"{a}.ogg")
            spec = np.abs(np.fft.rfft(m1.mono(x), n=1 << 17)) ** 2
            f = np.fft.rfftfreq(1 << 17, 1.0 / sfx.SR)
            centres = np.geomspace(30, 20000, 130)
            band = [spec[(f >= c / 2 ** (1 / 12)) & (f < c * 2 ** (1 / 12))].mean() for c in centres]
            ax.semilogx(centres, 10 * np.log10(np.array(band) + 1e-12), color=COLOUR[k],
                        lw=1.6 if k in STYLE else 2, ls=STYLE.get(k, "-"), label=LABEL[k])
        ax.axvline(300, color=INK2, lw=0.8, ls=":")
        ax.axvline(4000, color=INK2, lw=0.8, ls=":")
        ax.set_xlim(30, 20000)
        top = ax.get_ylim()[1]
        ax.set_ylim(top - 70, top)
        ax.set_title(f"{a}.ogg: spectrum (1/6 octave); dotted 300 Hz, 4 kHz", loc="left", fontsize=10)
        ax.set_xlabel("Hz")
        ax.set_ylabel("dB (relative)")

    ax = fig.add_subplot(gs[3, :])
    ax.axis("off")
    cols = ["set", "one: LUFS", "M max", "dBTP", "centroid Hz", "< 300 Hz %", "six: LUFS", "M max", "dBTP",
            "centroid Hz", "< 300 Hz %"]
    rows = []
    for k in ("today", "R2 A", "R2 B", "R2 C"):
        o, s = mix[k]["one"], mix[k]["six"]
        rows.append([f"offline: {LABEL[k]}"] + [f"{o['lufs']:.1f}", f"{o['mmax']:.1f}", f"{o['dbtp']:.1f}",
                                                 f"{o['centroid_hz']:.0f}", f"{o['low_pct']:.1f}",
                                                 f"{s['lufs']:.1f}", f"{s['mmax']:.1f}", f"{s['dbtp']:.1f}",
                                                 f"{s['centroid_hz']:.0f}", f"{s['low_pct']:.1f}"])
    for name, c in cap.items():
        if not name.endswith("-one"):
            continue
        six = cap.get(name[:-4] + "-six")
        row = [f"in game: {name[7:-4]}", f"{c['lufs']:.1f}", f"{c['mmax']:.1f}", f"{c['dbtp']:.1f}",
               f"{c['centroid_hz']:.0f}", f"{c['low_pct']:.1f}"]
        row += ([f"{six['lufs']:.1f}", f"{six['mmax']:.1f}", f"{six['dbtp']:.1f}", f"{six['centroid_hz']:.0f}",
                 f"{six['low_pct']:.1f}"] if six else [""] * 5)
        rows.append(row)
    t = ax.table(cellText=rows, colLabels=cols, loc="upper center", cellLoc="right", colLoc="right",
                 colWidths=[0.24, 0.07, 0.07, 0.07, 0.08, 0.08, 0.07, 0.07, 0.07, 0.08, 0.08])
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
    ax.set_title("As played. Offline: machines.lua's volumes and frames, three strokes; six = started 0, 37, 83, "
                 "121, 158, 203 ticks apart, summed with no falloff.\nIn game: the sound capture's recording "
                 "(null sink), from the machine's start; six = the bank capture, heard from its top middle crusher.",
                 loc="left", fontsize=9.5)
    fig.savefig(path, dpi=110)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--captures")
    args = ap.parse_args()
    per = {k: {a: figures(sfx.read(d / f"{a}.ogg")[0]) for a in m1.ACCENTS} for k, d in SETS.items()}
    m1.figures = figures                      # the mixes measured with the new figures too
    mix = {k: m1.mixes(SETS[k]) for k in ("today", "R2 A", "R2 B", "R2 C")}
    m1.figures = BASE_FIGURES
    cap = captures(args.captures) if args.captures else {}
    (HERE / "figures.json").write_text(json.dumps({"accents": per, "mixes": mix, "captures": cap}, indent=1))
    print(f"{'accent':6s} {'set':6s} {'LUFS':>6s} {'M max':>6s} {'peak':>6s} {'attack':>7s} {'steep':>6s} "
          f"{'>4k%':>6s} {'cent':>6s} {'<300%':>6s}")
    for a in m1.ACCENTS:
        for k in SETS:
            f = per[k][a]
            lufs = "-" if f["lufs"] is None else f"{f['lufs']:.1f}"
            print(f"{a:6s} {k:6s} {lufs:>6s} {f['mmax']:6.1f} {f['peak_dbfs']:6.1f} {f['attack_ms']:7.1f} "
                  f"{f['steepest_db_ms']:6.1f} {f['hf_pct']:6.1f} {f['centroid_hz']:6.0f} {f['low_pct']:6.1f}")
    for k, v in mix.items():
        o, s = v["one"], v["six"]
        print(f"mix {k:5s} one: I {o['lufs']:.1f} M {o['mmax']:.1f} TP {o['dbtp']:.1f} cent {o['centroid_hz']:.0f} "
              f"low {o['low_pct']:.1f}  six: I {s['lufs']:.1f} M {s['mmax']:.1f} TP {s['dbtp']:.1f}")
    for n, c in cap.items():
        print(f"captured {n}: I {c['lufs']:.1f} M {c['mmax']:.1f} TP {c['dbtp']:.1f} cent {c['centroid_hz']:.0f} "
              f"low {c['low_pct']:.1f} hf {c['hf_pct']:.1f}")
    sheet(per, mix, cap, HERE / "figures.png")
    print(HERE / "figures.png")


if __name__ == "__main__":
    main()
