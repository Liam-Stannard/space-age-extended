---
name: factorio-building-round
description: Run the next stage of a building's art for this mod (options, refine, spec, model, sign-off, wiring) with that stage's bars, deliverables and gate. Use when Liam asks for options, a new round, a model, or wiring for a building.
argument-hint: <building> <stage> [Liam's words]
---

Run stage `<stage>` for `<building>`. Quote Liam's words in the task file
amendment. Write the amendment (in `.claude/tasks/`), brief the agents
with `factorio-brief`, and stop at the stage's gate.

## The stages
1. **options** — 3–10 genuinely different takes, each a lit Blender
   concept with a sheet (working and idle at 2x, the input-to-output chain
   labelled, motion map, measures), a 1x GIF and a pitch; one contact
   sheet beside the vanilla references and the Core's signed-off
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

## Bars at every stage from options on
- **A building, not a deck:** coverage of the footprint ≥ 92 % (the 3×3
  and 5×5 showpieces' figure), built up in height, no flat base or plinth;
  the outline broken at the corners by equipment (FFF #350).
- **Rise** above the north edge no more than vanilla's comparable building
  (refinery 0.97, fusion reactor 0.66).
- **Finish:** the latest signed-off model's (paint per unit, worn paint,
  rust only where it forms, vanilla warmth and saturation); tonal p50
  ~75–81, p95 into vanilla's range.
- **Light:** the radiant look (`tools/blender/radiant.py`) wherever the
  isotope is seen; molten metal orange only where melt is seen; nothing
  else glows.
- **Pipes:** each connection leads to the vessel or device that uses it,
  so the flow reads through the building as on vanilla's chemical plant
  and oil refinery. A run from a connection keeps the connection's size:
  no sudden narrowing after the fitting, and a narrowing only where a
  visible reducer shows why, at a valve, pump or vessel nozzle; thin pipes
  only for side lines (dosing, instruments). A model that turns reads that
  way in every direction. Each connection enters the building through a
  fitting set into its wall or casing (a recessed boss with a sleeve and
  flanges, as on the Reaction Plant's casing, or similar), never a stub
  standing off the machine; the pipe picture shows it open, and vanilla's
  cover is drawn when nothing is connected. Its own pipe pictures to
  assembler 3's outline;
  vanilla covers; joins checked with `factorio-art-measure`. Before the
  options stage, study how the comparable vanilla buildings meet their
  pipes.
- **Motion** a player notices at 1x, every moving part with a job; an
  idle state; nothing that strobes at 1x.
- Measures always taken with `factorio-art-measure`, never ad hoc.

## Parallel work
Split options across at most two artists, with filename prefixes and one
shared decision file for anything they must agree; the second to finish
builds the combined contact sheet. Keep at most three agents running at
once on this machine.
