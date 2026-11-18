---
name: factorio-building-round
description: Run the next stage of a building's art for this mod (options, refine, spec, model, wiring) with that stage's deliverables and gate, held to the bars in standards.md. Use when Liam asks for options, a new round, a model, or wiring for a building.
argument-hint: <building> <stage> [Liam's words]
---

Run stage `<stage>` for `<building>`. Quote Liam's words in the task file
amendment. Write the amendment (in `.claude/tasks/`), brief the agents
with `factorio-brief`, and stop at the stage's gate.

## The stages
1. **options** — first, one study sheet of how the comparable vanilla
   buildings meet their pipes, run their cables and mount their
   terminals. Then 3–10 options, each different from the others. Each
   is a concept, made as `.claude/agents/artist.md` (Concepts) says, with
   a sheet, a 1x GIF and a pitch. The sheet shows it working and idle at
   2x, its input-to-output chain labelled, its motion map and its
   measures. One contact sheet sets the options beside the vanilla
   references and the Core's signed-off buildings. Gate: Liam picks or
   combines.
2. **refine** — the picked option reworked to Liam's notes; before/after
   crops of what changed. Gate: Liam signs off the concept.
3. **spec** — the building spec rewritten with `factorio-spec-wording`.
   Gate: wording agreed and written.
4. **model** — the shipping model, in the folder claude.md rule 2 gives,
   through `tools/blender/render.sh --ports --icon`; every layer packed.
   Gate: Liam signs off the model.
5. **wiring** — sheets into `graphics/`, prototypes pointed at them, a
   client test. Gate: Liam signs off in game; then `factorio-ship`.

## Bars
The bars are in `.claude/skills/factorio-task/knowledge/standards.md`.
This skill adds no bar of its own.

## Parallel work
Split options across artists, with filename prefixes and one shared
decision file for anything they must agree; the last to finish builds
the combined contact sheet. Render limits: see the standing rules.
