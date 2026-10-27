---
name: factorio-art-measure
description: Measure a building's model or sheets for this mod the agreed way, with tools/blender/measure.py: coverage, corners, rise, tonal, finish, glow and blue share, pale and clipped pixels, motion and strobe as the engine plays them, pipe joins by the no-gap rule, collide, and a comparison sheet beside vanilla. Use whenever a round, a model or a sign-off needs figures; never measure ad hoc.
argument-hint: <render.sh out-dir | sheets dir> [--vanilla <name>]
---

Every figure an artist, reviewer or tester quotes comes from
`tools/blender/measure.py`. A per-round script is written only for a figure
measure.py cannot give, and says why.

## 1. Run it
    python3 tools/blender/measure.py <src> --out <dir> \
        [--vanilla <name> ...] [--collide <model.py> [--collide-allow <pattern> ...]]
- <src>: render.sh's out-dir, or a packed sheets directory (then give
  --footprint WxH, and --directions if the names don't say).
- --out: always outside concept/ (scratch, or the round's own folder).
- --vanilla: the comparable building(s), named in the spec or the task.
- --collide on every model round; an allow pattern names one meant contact
  as its whole line, never a wildcard.

## 2. The bars it checks against
The bars are factorio-building-round's "Bars at every stage from options
on". Two are measure.py's own:
- joins: no gap of 2 px or more in more than 2 of the pipe body's columns
  (beside the pipe is information only; clipping is Liam's eye);
- collide: 0 clashes not allowed.
- clipping, by eye as well as `--collide`: at 2x in every direction, no
  cable, hose, pipe or effect passes through another part or into the
  ground, and every end is visibly fastened (gland, clamp, collar, flange
  or nozzle). `--collide` catches loose ends, runs through parts and parts in the
  ground only for runs the model records with `tools/blender/runs.py`.
  For everything else, and for any contact listed as meant, this by-eye
  check is the only one.
- white and clipped: since 2026-10-20 pack.py rolls highlights off every
  drawn sheet but light passes (render.json `rolloff`, on by default):
  new sheets have no pixel at 245 or over, so white_px is the shipped
  look's. Compare sheets packed before and after only with the newer
  packed `rolloff: false`.

## 3. Timing
measure.py plays each layer's frame_sequence at its animation_speed, as
the engine does (render.json; meta.json). A loop longer than 1200 drawn
frames or an hour of ticks is measured from tick 0 and marked
loop_complete false: say so when quoting it.

## 4. Report
Quote measures.json's figures beside the vanilla ones, name the
comparison sheet's absolute path (pages are under 8000 px), and state any
bar not met. Never sign off: Liam judges the look.
