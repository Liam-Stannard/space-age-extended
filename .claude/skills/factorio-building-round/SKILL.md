---
name: factorio-building-round
description: Run the next stage of a building's art for this mod (options, refine, spec, model, sign-off, wiring) with that stage's deliverables and gate, held to the bars in standards.md. Use when Liam asks for options, a new round, a model, or wiring for a building.
argument-hint: <building> <stage> [Liam's words]
---

Run stage `<stage>` for `<building>`. Quote Liam's words in the task file
amendment. Write the amendment (in `.claude/tasks/`), brief the agents
with `factorio-brief`, and stop at the stage's gate.

## The stages
1. **options** — first, one study sheet of how the comparable vanilla
   buildings meet their pipes, run their cables and mount their
   terminals. Then 3–10 genuinely different takes, each a lit Blender
   concept with a sheet (working and idle at 2x, the input-to-output
   chain labelled, motion map, measures), a 1x GIF and a pitch; one
   contact sheet beside the vanilla references and the Core's signed-off
   buildings. Gate: Liam picks or combines.
2. **refine** — the picked option reworked to Liam's notes; before/after
   crops of what changed. Gate: Liam signs off the concept.
3. **spec** — the building spec rewritten with `factorio-spec-wording`.
   Gate: wording agreed and written.
4. **model** — the shipping model in `concept/<building>/model/` through
   `tools/blender/render.sh --ports --icon`; every layer packed. Gate:
   Liam signs off the model.
5. **wiring** — sheets into `graphics/`, prototypes pointed at them, a
   client test. Gate: Liam signs off in game; then `factorio-ship`.

## Bars
Every stage from options on is held to
`.claude/skills/factorio-task/knowledge/standards.md`, each bar measured
as it says, with `factorio-art-measure`. This skill adds no bar of its
own.

## Parallel work
Split options across at most two artists, with filename prefixes and one
shared decision file for anything they must agree; the second to finish
builds the combined contact sheet. At most two Blender renders run at
once, whoever starts them (standing rules).
