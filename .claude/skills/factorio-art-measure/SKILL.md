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
- --out: your scratch, or the round's own folder.
- --vanilla: the comparable building(s), named in the spec or the task.
- --collide on every model round; an allow pattern names one meant contact
  as its whole line, never a wildcard.
- A resource model (an ore, a vent) is measured a cell at a time, its cells keyed "SS-VV" where a building's directions go; it has no joins, and --connection is refused. Its stateless_visualisation is measured as a building's animations are.

## 2. The bars
The bars, and which figure checks each, are in
`.claude/skills/factorio-task/knowledge/standards.md`. What is
measure.py's own:
- joins: the bar is in standards.md (Pipes, Joins). Its `beside` figure
  in measures.json is information only.
- collide: what it covers, and what is left to the eye, is in
  standards.md (Hoses and cables, No clipping).
- white and clipped: the bar is "No white" in standards.md. Sheets
  packed before 2026-10-20 were not rolled off, so compare across that
  date only with the newer sheet packed `rolloff: false`.
- tonal is still recorded in measures.json; it is not a bar and is not
  quoted.

## 3. Timing
measure.py plays each layer's frame_sequence (render.json; meta.json) at
the rate `.claude/skills/factorio-task/knowledge/engine.md` (Animation
and sound) gives, with the animation progress it is given or the model
declares, and the crafting speed it is given (default 1). Where it reads
the docs its own way, or does not model the engine, its header says. A
loop longer than 1200 drawn frames or an hour of ticks is measured from
tick 0 and marked loop_complete false: say so when quoting it.

## 4. Report
Quote measures.json's figures as `DOCUMENTATION-LANGUAGE.md` §6.7 says.
