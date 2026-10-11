"""A review MP4 of a sound against its motion, at game speed.

So a sound can be heard against the animation it is cued to before any
prototype names it: the animation plays as the game plays it, the bed loops
under it, and each accent fires on its frame every cycle. With a vanilla clip
beside it, the two play side by side and the sound switches halfway: ours for
`loops` of our cycles, then vanilla's for the whole number of its own cycles
nearest that (at least one; --vs-loops says otherwise), a bar under the panel
being heard.

  review.py <out.mp4> --frames <src> --speed 0.4 [--bed <sound>[@vol]]
            [--accent <frame>:<sound>[,<sound>...][@vol] ...] [--loops 4]
            [--scale 1] [--sheet W H LINE_LENGTH FRAME_COUNT] [--sequence 1,1,2,...]
            [--vs-frames <src> --vs-speed ... --vs-bed ... --vs-accent ...
             --vs-scale ... --vs-sheet ... --vs-sequence ... --vs-loops N]

  <src>    a GIF; a directory of PNG frames, taken in name order; a glob of
           them ("renders/stroke-*.png"); or, with --sheet, one sprite sheet
           cut into FRAME_COUNT frames of W x H, LINE_LENGTH to a row -- the
           way a vanilla sheet is read, so a vanilla machine can sit beside
           ours. --sequence plays the frames in a vanilla `frame_sequence`'s
           order (1-based, as the prototype writes it), and an accent's frame
           then counts in the sequence, as derive.working_sound's check does
           (taken to be the engine's count; not yet measured in a client).
  <sound>  a file or a game path; @vol is the linear volume the prototype's
           Sound will carry (1 if left out). An accent with several sounds
           plays them in turn, one a cycle, as variations do.

**Game speed:** the video is 60 frames a second, one per tick, and tick t shows
animation frame floor(t x speed) -- the frame the engine draws. A cycle lasts
frames / speed ticks, and the video `loops` cycles: 24 frames at 0.4 is 60
ticks, so 4 loops is 4.000 s. An accent on frame n of cycle k sounds at
(k x frames + n) / speed / 60 s, sfx.frame()'s time; the frame itself shows
from the first tick at or after that, so where n / speed is not a whole number
of ticks the sound leads its picture by under one tick (17 ms). The MP4 is
exactly that long; AAC pads its last packet, so its audio, decoded, runs about
20 ms past the end. A transparent GIF or PNG is drawn over a flat grey (--bg).

**Side by side, both panels run on the video's one clock** from tick 0, so the
picture never jumps when the sound changes over, and the vanilla half's
accents are placed where the vanilla picture reaches their frames -- part-way
through its cycle, if that is where the changeover falls.

**Pass the speed the animation plays at.** A drill's is its animation_speed;
a crafting machine's is that times its crafting speed (machines.lua says how
each of ours plays).

The mix is not normalised. If a clip's sounds sum past full scale the whole
track, both halves alike, is turned down by the same amount, and the run says
by how much, so ours and vanilla's keep their difference.

From a sound script: review.make(out, Clip(...), vs=Clip(...), loops=4). The
tool family, where sounds and reviews live and the setup line: see sfx.py.
"""

import argparse
import glob
import os
import sys
import tempfile
from dataclasses import dataclass, field

import imageio_ffmpeg
import numpy as np
import soundfile as sf
from scipy import ndimage

import sfx

FPS = sfx.TICKS_PER_SECOND
BAR = 6           # px: the bar under the panel being heard
GAP = 16          # px between panels


@dataclass
class Clip:
    """An animation and the sound that goes with it."""
    frames: object                 # path, glob, or a list of HxWx3/4 uint8 arrays
    speed: float                   # frames a tick, as played
    bed: object = None             # sound path or array, looped
    bed_volume: float = 1.0
    accents: list = field(default_factory=list)   # (frame, sound or [sounds], volume)
    sheet: tuple = None            # (width, height, line_length, frame_count)
    scale: float = 1.0
    sequence: list = None          # a frame_sequence, 1-based


# --- frames ------------------------------------------------------------------

def _decode(path):
    """Every frame of an image or GIF, as HxWx4 uint8, through the bundled ffmpeg."""
    gen = imageio_ffmpeg.read_frames(str(path), pix_fmt="rgba", bpp=4,
                                     output_params=["-fps_mode", "passthrough"])
    meta = next(gen)
    w, h = meta["size"]
    return [np.frombuffer(b, np.uint8).reshape(h, w, 4) for b in gen]


def load_frames(clip):
    """The clip's animation frames, RGBA, scaled."""
    src = clip.frames
    if isinstance(src, (list, tuple)):
        frames = [np.asarray(f, np.uint8) for f in src]
        frames = [f if f.shape[2] == 4 else
                  np.concatenate([f, np.full(f.shape[:2] + (1,), 255, np.uint8)], 2) for f in frames]
    elif clip.sheet:
        w, h, line, count = clip.sheet
        sheet = _decode(sfx.resolve(src))[0]
        frames = [sheet[(i // line) * h:(i // line + 1) * h, (i % line) * w:(i % line + 1) * w]
                  for i in range(count)]
        if any(f.shape[:2] != (h, w) for f in frames):
            raise ValueError(f"{src}: a {sheet.shape[1]}x{sheet.shape[0]} sheet does not hold "
                             f"{count} frames of {w}x{h}, {line} to a row")
    else:
        s = str(src)
        if os.path.isdir(s):
            files = sorted(glob.glob(os.path.join(s, "*.png")))
        elif any(c in s for c in "*?["):
            files = sorted(glob.glob(s))
        else:
            files = None
        if files is not None:
            if not files:
                raise FileNotFoundError(f"no PNG frames in {s}")
            frames = [_decode(f)[0] for f in files]
        else:
            frames = _decode(sfx.resolve(s))
    if not frames:
        raise ValueError(f"{src}: no frames")
    if clip.sequence:
        if not all(1 <= i <= len(frames) for i in clip.sequence):
            raise ValueError(f"{src}: frame_sequence names a frame outside 1 to {len(frames)}")
        frames = [frames[i - 1] for i in clip.sequence]
    if clip.scale != 1:
        frames = [np.clip(ndimage.zoom(f.astype(np.float32), (clip.scale, clip.scale, 1), order=1),
                          0, 255).astype(np.uint8) for f in frames]
    return frames


def _over(rgba, bg):
    a = rgba[..., 3:4].astype(np.float32) / 255.0
    return (rgba[..., :3] * a + np.array(bg, np.float32) * (1 - a)).astype(np.uint8)


# --- sound -------------------------------------------------------------------

def _sound(s):
    return s if isinstance(s, np.ndarray) else sfx.load(s)


def clip_audio(clip, n_frames, ticks, start=0):
    """The clip's sound from tick `start` for `ticks` ticks: the bed looped, accents every cycle.

    The animation's clock is the video's, which starts at tick 0 for every
    panel, so a clip heard from a later tick is part-way through a cycle: its
    accents are placed where its picture reaches their frames, not counted
    from the start of its half. The bed starts with the half, as a working
    sound's loop does when a machine starts.
    """
    mix = sfx.Mix(ticks / FPS)
    if clip.bed is not None:
        mix.add(sfx.gain(_sound(clip.bed), 20 * np.log10(clip.bed_volume)), loop=True)
    first = int(np.floor(start * clip.speed / n_frames))
    last = int(np.ceil((start + ticks) * clip.speed / n_frames))
    for frame, sounds, volume in clip.accents:
        if not 0 <= frame < n_frames:
            raise ValueError(f"accent at frame {frame}: the animation has frames 0 to {n_frames - 1}")
        sounds = [_sound(s) for s in (sounds if isinstance(sounds, (list, tuple)) else [sounds])]
        for k in range(first, last + 1):
            at = sfx.frame(k * n_frames + frame, clip.speed) - start / FPS
            if 0 <= at < ticks / FPS:
                mix.add(sounds[k % len(sounds)], at, gain_db=20 * np.log10(volume))
    return mix.render()


# --- the video -----------------------------------------------------------------

def make(out, clip, vs=None, loops=4, vs_loops=None, bg=(72, 72, 72), audio_bitrate="192k"):
    """Write the review MP4; returns (seconds, ticks per cycle of each clip)."""
    clips = [clip] + ([vs] if vs else [])
    frames = [load_frames(c) for c in clips]
    cycles = [len(f) / c.speed for c, f in zip(clips, frames)]   # ticks, maybe fractional
    segs = [int(round(loops * cycles[0]))]                      # ticks each clip is heard
    if vs:
        n = vs_loops or max(1, int(round(segs[0] / cycles[1])))
        segs.append(int(round(n * cycles[1])))
    starts = np.cumsum([0] + segs)
    total = int(starts[-1])

    audio = np.concatenate([clip_audio(c, len(f), s, int(t0))
                            for c, f, s, t0 in zip(clips, frames, segs, starts)])
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 0.99:
        trim_db = 20 * np.log10(0.99 / peak)
        audio = sfx.gain(audio, trim_db)
        print(f"review: the mix peaks at {20 * np.log10(peak):+.1f} dBFS; "
              f"turned the whole track down {-trim_db:.1f} dB")

    # The canvas: panels side by side, tops aligned on the tallest, a bar row below.
    sizes = [f[0].shape[:2] for f in frames]
    height = max(h for h, _ in sizes) + 2 * BAR
    width = sum(w for _, w in sizes) + GAP * (len(clips) + 1)
    height += -height % 16
    width += -width % 16
    lefts, x = [], GAP
    for _, w in sizes:
        lefts.append(x)
        x += w + GAP

    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "track.wav")
        sf.write(wav, audio, sfx.SR, subtype="FLOAT")
        writer = imageio_ffmpeg.write_frames(
            str(out), (width, height), fps=FPS, codec="libx264", macro_block_size=16,
            quality=None, output_params=["-crf", "18", "-b:a", audio_bitrate, "-movflags", "+faststart"],
            audio_path=wav, audio_codec="aac", ffmpeg_log_level="error")
        writer.send(None)
        canvas = np.empty((height, width, 3), np.uint8)
        for t in range(total):
            canvas[:] = bg
            heard = int(np.searchsorted(starts, t, side="right")) - 1
            for i, (c, f) in enumerate(zip(clips, frames)):
                img = _over(f[int(np.floor(t * c.speed + 1e-9)) % len(f)], bg)
                h, w = img.shape[:2]
                canvas[BAR:BAR + h, lefts[i]:lefts[i] + w] = img
                if len(clips) > 1 and i == heard:
                    canvas[height - BAR:, lefts[i]:lefts[i] + w] = (230, 190, 60)
            writer.send(canvas.tobytes())
        writer.close()
    return total / FPS, cycles


# --- command line ----------------------------------------------------------------

def _sound_arg(text):
    """"<sound>[,<sound>...][@vol]" -> ([sounds], volume); an "@" not followed by a number is a path's."""
    body, _, vol = text.rpartition("@")
    try:
        return body.split(","), float(vol)
    except ValueError:
        return text.split(","), 1.0


def _clip(a, prefix):
    def g(key):
        return getattr(a, prefix + key)
    if g("frames") is None:
        return None
    if g("speed") is None:
        raise SystemExit(f"--{prefix.replace('_', '-')}speed is needed with --{prefix.replace('_', '-')}frames")
    bed, bed_vol = (None, 1.0)
    if g("bed"):
        sounds, bed_vol = _sound_arg(g("bed"))
        bed = sounds[0]
    accents = []
    for spec in g("accent") or []:
        frame, _, rest = spec.partition(":")
        sounds, vol = _sound_arg(rest)
        accents.append((int(frame), sounds, vol))
    return Clip(frames=g("frames"), speed=g("speed"), bed=bed, bed_volume=bed_vol,
                accents=accents, sheet=tuple(g("sheet")) if g("sheet") else None, scale=g("scale"),
                sequence=[int(v) for v in g("sequence").split(",")] if g("sequence") else None)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", help="the MP4 to write")
    for prefix, who in (("", "ours"), ("vs-", "the vanilla clip beside it")):
        ap.add_argument(f"--{prefix}frames", help=f"{who}: GIF, PNG directory or glob, or sheet")
        ap.add_argument(f"--{prefix}speed", type=float, help=f"{who}: animation frames a tick, as played")
        ap.add_argument(f"--{prefix}bed", help=f"{who}: the loop, <sound>[@volume]")
        ap.add_argument(f"--{prefix}accent", action="append",
                        help=f"{who}: <frame>:<sound>[,<sound>...][@volume], repeatable")
        ap.add_argument(f"--{prefix}sheet", type=int, nargs=4,
                        metavar=("W", "H", "LINE_LENGTH", "FRAME_COUNT"), help=f"{who}: cut a sprite sheet")
        ap.add_argument(f"--{prefix}scale", type=float, default=1.0, help=f"{who}: scale the frames")
        ap.add_argument(f"--{prefix}sequence", help=f"{who}: a frame_sequence, 1-based, comma-separated")
    ap.add_argument("--loops", type=int, default=4, help="animation cycles of ours (default 4)")
    ap.add_argument("--vs-loops", type=int, help="cycles of the vanilla clip (default: about as long as ours)")
    ap.add_argument("--bg", default="72,72,72", help="background r,g,b under transparency")
    a = ap.parse_args(argv)

    ours = _clip(a, "")
    if ours is None:
        ap.error("--frames is needed")
    vs = _clip(a, "vs_")
    seconds, cycles = make(a.out, ours, vs, loops=a.loops, vs_loops=a.vs_loops,
                           bg=tuple(int(v) for v in a.bg.split(",")))
    print(f"review: {a.out}: {seconds:.3f} s; a cycle is "
          + ", ".join(f"{c:g} ticks" for c in cycles))
    return 0


if __name__ == "__main__":
    sys.exit(main())
