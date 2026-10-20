#!/usr/bin/env python3
"""Round 3's figures: the drop's tail, each take beside round 2 C's and today's.

  <venv>/bin/python concept/drop-crusher/sound/round-3/measure_round3.py [--captures DIR]

Writes figures.json and figures.png beside this file and prints the tables.
Every figure of round 2's measure_round2.py for each accent (see its header and
round 1's), and for the drop the crackle in its tail -- everything after its
first 150 ms, the hit itself left out:

  >2k dBFS   the level of the tail above 2 kHz (the mono mix through a 4th-order
             high-pass at 2 kHz, RMS), dBFS
  >2k %      the tail's share of its own energy above 2 kHz, %
  crest dB   that band's peak over its RMS: how far single clicks stand out
  clicks/s   the roughness: 1 ms steps of that band's envelope that stand
             more than 10 dB over the median of the 40 ms around them (and
             above -60 dBFS), per second of tail

With --captures, every round3-*.mp4 under DIR is measured as round 1's and 2's
are (from the machine's start), and the drop's crackle is measured in the
single captures too: the same four figures over each drop's tail window
(150 ms to 1.5 s after its frame), from the capture's own accents.json
(the drop's onsets).
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROUND1, ROUND2 = HERE.parent / "round-1", HERE.parent / "round-2"
sys.path.insert(0, str(ROUND1))
sys.path.insert(0, str(ROUND2))

import numpy as np  # noqa: E402
import measure_round1 as m1  # noqa: E402
import measure_round2 as m2  # noqa: E402
import sfx  # noqa: E402

SETS = {"today": m1.REPO / "sound" / "drop-crusher", "R2 C": ROUND2 / "C",
        "R3 A": HERE / "A", "R3 B": HERE / "B", "R3 C": HERE / "C"}
LABEL = {"today": "today (shipped)", "R2 C": "round 2 C", "R3 A": "R3 A: grit out",
         "R3 B": "R3 B: grit -> low settle", "R3 C": "R3 C: grit -> crunch on the hit only"}
COLOUR = {"today": "#52514e", "R2 C": "#9a988f", "R3 A": "#2a78d6", "R3 B": "#eb6834", "R3 C": "#1baf7a"}
STYLE = {"today": "--", "R2 C": ":"}
SKIP = 0.15


def hf_band(m):
    return sfx.highpass(m, 2000)[:, 0].astype(np.float64)


def crackle_of(m, sr=sfx.SR):
    """The four crackle figures of a mono tail (already cut to start after the hit)."""
    hp = hf_band(m) if sr == sfx.SR else hf_band(m)
    rms = float(np.sqrt((hp ** 2).mean()))
    share = float((hp ** 2).sum() / max((m ** 2).sum(), 1e-20) * 100)
    crest = float(20 * np.log10(np.abs(hp).max() / max(rms, 1e-12)))
    w = sfx.samples(0.001)
    e = np.sqrt(np.convolve(hp ** 2, np.ones(w) / w, "same"))[::w]
    med = np.array([np.median(e[max(0, i - 20):i + 20]) for i in range(len(e))])
    clicks = float(((e > 3.16 * med) & (e > 1e-3)).sum() / (len(hp) / sr))
    return {"hf_tail_dbfs": float(20 * np.log10(rms + 1e-12)), "hf_tail_pct": share, "crest_db": crest,
            "clicks_per_s": clicks}


def crackle(x):
    return crackle_of(m1.mono(x)[sfx.samples(SKIP):])


def capture_crackle(mp4, accents_json):
    """The drop tails in a capture: 150 ms to 1.5 s after each drop's onset, pooled."""
    a = m1.mp4_audio(mp4).astype(np.float64).mean(1)
    r = json.loads(Path(accents_json).read_text())
    # the MP4 opens lead_seconds before the start; onset times are on the capture's clock
    t_mp4 = r["start_s"] - 0.6
    tails = []
    for e in r["onsets"]:
        if e["sound"] != "drop" and e.get("cued_frame") != 14:
            continue
        s = sfx.samples(e["t_s"] - t_mp4 + SKIP)
        tails.append(a[s:s + sfx.samples(1.35)])
    if not tails:
        return None
    return {**crackle_of(np.concatenate(tails)), "drops": len(tails)}


def sheet(per, crk, cap, capcrk, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    INK, INK2, GRID, SURF = m1.INK, m1.INK2, m1.GRID, m1.SURF
    plt.rcParams.update({"font.size": 9, "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2,
                         "ytick.color": INK2, "axes.edgecolor": GRID, "axes.facecolor": SURF,
                         "figure.facecolor": SURF, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6})
    fig = plt.figure(figsize=(15, 15.5))
    gs = fig.add_gridspec(4, 2, height_ratios=[0.8, 1.0, 1.0, 0.95], hspace=0.42, wspace=0.18, top=0.91,
                          bottom=0.03)
    fig.suptitle("Drop Crusher, round 3: round 2 C without the crackle after the drop (takes A/B/C)",
                 fontsize=14, x=0.02, ha="left", y=0.985)
    fig.text(0.02, 0.945, "The crackle is the drop's grit layer (Poisson clicks, 1.8-7.5 kHz), pitched down and "
             "stretched in round 2 C. Each take treats only that layer; the rest is round 2 C\n(7 st down, 40 Hz "
             "iron body, round 1 B's softening, today's M max). Pawl and trip are round 2 C's files; bed today's. "
             "Tail = after the drop's first 150 ms.", color=INK2, fontsize=9.5)

    ax = fig.add_subplot(gs[0, :])
    ax.axis("off")
    cols = ["drop.ogg", "LUFS", "M max", "peak", "centroid", "<300 Hz %", ">4 kHz %",
            "tail >2k dBFS", "tail >2k %", "crest dB", "clicks/s"]
    rows = []
    for k in SETS:
        f, c = per[k]["drop"], crk[k]
        rows.append([LABEL[k], f"{f['lufs']:.1f}", f"{f['mmax']:.1f}", f"{f['peak_dbfs']:.1f}",
                     f"{f['centroid_hz']:.0f}", f"{f['low_pct']:.1f}", f"{f['hf_pct']:.1f}",
                     f"{c['hf_tail_dbfs']:.1f}", f"{c['hf_tail_pct']:.1f}", f"{c['crest_db']:.1f}",
                     f"{c['clicks_per_s']:.1f}"])
    t = ax.table(cellText=rows, colLabels=cols, loc="center", cellLoc="right", colLoc="right",
                 colWidths=[0.22, 0.06, 0.06, 0.07, 0.08, 0.07, 0.07, 0.1, 0.08, 0.07, 0.07])
    t.auto_set_font_size(False)
    t.set_fontsize(9)
    t.scale(1, 1.35)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(GRID)
        cell.set_facecolor(SURF)
        if r == 0:
            cell.set_text_props(color=INK2, weight="bold")
        if c == 0:
            cell.set_text_props(ha="left")
            cell._loc = "left"

    ax = fig.add_subplot(gs[1, 0])
    for k, d in SETS.items():
        x, _ = sfx.read(d / "drop.ogg")
        e = m1.envelope(x, 0.01)
        ax.plot(np.arange(len(e)) / sfx.SR, 20 * np.log10(e + 1e-6), color=COLOUR[k], lw=1.6 if k in STYLE else 2,
                ls=STYLE.get(k, "-"), label=LABEL[k])
    ax.set_ylim(-70, 0)
    ax.set_xlim(0, 2.4)
    ax.set_title("drop.ogg: the whole sound (envelope, 10 ms RMS)", loc="left", fontsize=10)
    ax.set_xlabel("s from the file's start")
    ax.set_ylabel("dBFS")
    ax.legend(frameon=False, fontsize=8, loc="upper right")

    ax = fig.add_subplot(gs[1, 1])
    for k, d in SETS.items():
        x, _ = sfx.read(d / "drop.ogg")
        hp = hf_band(m1.mono(x))
        w = sfx.samples(0.002)
        e = np.sqrt(np.convolve(hp ** 2, np.ones(w) / w, "same"))
        ax.plot(np.arange(len(e)) / sfx.SR, 20 * np.log10(e + 1e-6), color=COLOUR[k], lw=0.9 if k in STYLE else 1.2,
                ls="-", alpha=0.9, label=LABEL[k])
    ax.axvline(SKIP, color=INK2, lw=0.8, ls=":")
    ax.set_ylim(-90, -10)
    ax.set_xlim(0, 2.4)
    ax.set_title("drop.ogg above 2 kHz (2 ms RMS): the crackle; dotted line 150 ms", loc="left", fontsize=10)
    ax.set_xlabel("s from the file's start")
    ax.set_ylabel("dBFS")

    for i, k in enumerate(("R2 C", "R3 B")):
        ax = fig.add_subplot(gs[2, i])
        x, _ = sfx.read(SETS[k] / "drop.ogg")
        ax.specgram(m1.mono(x), NFFT=1024, Fs=sfx.SR, noverlap=768, cmap="Greys", vmin=-140, vmax=-30)
        ax.set_ylim(0, 8000)
        ax.set_title(f"{LABEL[k]}: spectrogram (0-8 kHz)", loc="left", fontsize=10)
        ax.set_xlabel("s")
        ax.set_ylabel("Hz")
        ax.grid(False)

    ax = fig.add_subplot(gs[3, :])
    ax.axis("off")
    cols = ["in game", "one: LUFS", "M max", "dBTP", "six: LUFS", "M max", "dBTP", "six vs today",
            "tails >2k dBFS", "crest dB", "clicks/s"]
    rows = []
    ref = cap.get("round3-today-six")
    for k in ("today", "R2C", "A", "B", "C"):
        pre = "round2-C" if k == "R2C" else f"round3-{k}"
        one, six = cap.get(f"{pre}-one"), cap.get(f"{pre}-six")
        cc = capcrk.get(f"{pre}-one")
        name = {"today": "today (as shipped)", "R2C": "round 2 C (ungrouped)"}.get(k, f"take {k} (grouped)")
        rows.append([name]
                    + ([f"{one['lufs']:.1f}", f"{one['mmax']:.1f}", f"{one['dbtp']:.1f}"] if one else [""] * 3)
                    + ([f"{six['lufs']:.1f}", f"{six['mmax']:.1f}", f"{six['dbtp']:.1f}"] if six else [""] * 3)
                    + ([f"{six['lufs'] - ref['lufs']:+.1f} LU"] if six and ref else [""])
                    + ([f"{cc['hf_tail_dbfs']:.1f}", f"{cc['crest_db']:.1f}", f"{cc['clicks_per_s']:.1f}"]
                       if cc else [""] * 3))
    t = ax.table(cellText=rows, colLabels=cols, loc="upper center", cellLoc="right", colLoc="right",
                 colWidths=[0.19, 0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.11, 0.13, 0.07, 0.07])
    t.auto_set_font_size(False)
    t.set_fontsize(9)
    t.scale(1, 1.3)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(GRID)
        cell.set_facecolor(SURF)
        if r == 0:
            cell.set_text_props(color=INK2, weight="bold")
        if c == 0:
            cell.set_text_props(ha="left")
            cell._loc = "left"
    ax.set_title("In game (the sound capture, null sink, from the machine's start). Takes run grouped like vanilla "
                 "(max_sounds_per_prototype 3; accents aggregated max_count 2,\nremove, count_already_playing) with "
                 "the drop's volume set to match today's bank; today's runs as shipped. Drop tails: 150 ms to 1.5 s "
                 "after each drop, single capture.", loc="left", fontsize=9.5)
    fig.savefig(path, dpi=110)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--captures")
    args = ap.parse_args()
    per = {k: {a: m2.figures(sfx.read(d / f"{a}.ogg")[0]) for a in m1.ACCENTS} for k, d in SETS.items()}
    crk = {k: crackle(sfx.read(d / "drop.ogg")[0]) for k, d in SETS.items()}
    cap, capcrk = {}, {}
    if args.captures:
        for p in sorted(Path(args.captures).rglob("round3-*.mp4")):
            x = m1.mp4_audio(p)[sfx.samples(0.6):]
            cap[p.stem] = {"file": str(p), **m2.figures(x)}
            aj = p.with_suffix(".accents.json")
            if p.stem.endswith("-one") and aj.exists():
                capcrk[p.stem] = capture_crackle(p, aj)
        r2 = ROUND2 / "C"
        for n in ("round2-C-one", "round2-C-six"):
            if (r2 / f"{n}.mp4").exists():
                cap[n] = {"file": str(r2 / f"{n}.mp4"), **m2.figures(m1.mp4_audio(r2 / f"{n}.mp4")[sfx.samples(0.6):])}
        if (r2 / "round2-C-one.accents.json").exists():
            capcrk["round2-C-one"] = capture_crackle(r2 / "round2-C-one.mp4", r2 / "round2-C-one.accents.json")
    (HERE / "figures.json").write_text(json.dumps({"accents": per, "drop_crackle": crk, "captures": cap,
                                                   "capture_crackle": capcrk}, indent=1))
    print(f"{'set':6s} {'accent':6s} {'LUFS':>6s} {'M max':>6s} {'peak':>6s} {'attack':>6s} {'steep':>6s} "
          f"{'>4k%':>5s} {'cent':>5s} {'<300%':>6s}")
    for k in SETS:
        for a in m1.ACCENTS:
            f = per[k][a]
            lufs = "-" if f["lufs"] is None else f"{f['lufs']:.1f}"
            print(f"{k:6s} {a:6s} {lufs:>6s} {f['mmax']:6.1f} {f['peak_dbfs']:6.1f} {f['attack_ms']:6.1f} "
                  f"{f['steepest_db_ms']:6.1f} {f['hf_pct']:5.1f} {f['centroid_hz']:5.0f} {f['low_pct']:6.1f}")
    print("drop tail crackle (after 150 ms): >2k dBFS, >2k %, crest dB, clicks/s")
    for k, c in crk.items():
        print(f"  {k:6s} {c['hf_tail_dbfs']:6.1f} {c['hf_tail_pct']:5.1f} {c['crest_db']:5.1f} {c['clicks_per_s']:6.1f}")
    for n, c in cap.items():
        print(f"captured {n}: I {c['lufs']:.1f} M {c['mmax']:.1f} TP {c['dbtp']:.1f} cent {c['centroid_hz']:.0f}")
    for n, c in capcrk.items():
        if c:
            print(f"captured crackle {n}: {c['drops']} drops, >2k {c['hf_tail_dbfs']:.1f} dBFS, "
                  f"{c['hf_tail_pct']:.1f} %, crest {c['crest_db']:.1f}, clicks/s {c['clicks_per_s']:.1f}")
    sheet(per, crk, cap, capcrk, HERE / "figures.png")
    print(HERE / "figures.png")


if __name__ == "__main__":
    main()
