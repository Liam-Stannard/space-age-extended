---
name: factorio-art-measure
description: Measure a building's model or sheets for this mod the agreed way, with tools/blender/measure.py: coverage, corners, rise, finish, glow and blue share, pale and clipped pixels, motion and strobe as the engine plays them, pipe joins by the no-gap rule, collide, and a comparison sheet beside vanilla. Use whenever a round, a model or a sign-off needs figures; never measure ad hoc.
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
- A resource model (an ore, a vent) is measured a cell at a time, its cells keyed "SS-VV" where a building's directions go; it has no joins, and --connection is refused. Its stateless_visualisation is measured as a building's animations are.

## 2. The bars
The bars, and which figure checks each, are in
`.claude/skills/factorio-task/knowledge/standards.md`. What is
measure.py's own:
- joins: a pipe-body column with a gap of 2 px or more is a gap column;
  more than 2 fail the join. Beside the pipe is information only.
- collide: catches loose ends, runs through parts and parts in the
  ground only for runs the model records with `tools/blender/runs.py`;
  everything else, and every contact listed as meant, is the by-eye
  check on the crops sheet.
- white and clipped: pack.py has rolled highlights off every drawn
  sheet but light passes since 2026-10-20 (render.json `rolloff`, on by
  default), so a new sheet has no pixel at 245 or over. Sheets packed
  before that remain: compare across the date only with the newer
  sheet packed `rolloff: false`.
- tonal is still recorded in measures.json; it is not a bar and is not
  quoted.

## 3. Timing
measure.py plays each layer's frame_sequence at its animation_speed, as
the engine does (render.json; meta.json). A loop longer than 1200 drawn
frames or an hour of ticks is measured from tick 0 and marked
loop_complete false: say so when quoting it.

## 4. Report
Quote measures.json's figures for the bars standards.md names, beside
the vanilla ones; name the comparison sheet's absolute path (pages are
under 8000 px); state any bar not met, and any target (coverage) missed.
