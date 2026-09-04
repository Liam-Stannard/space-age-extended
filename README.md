# Space Age Extended

An expansion for Factorio: Space Age 2.1 in which the player builds **cross-planetary
production lines between pairs of worlds**.

Vanilla gives each planet a self-contained tech tree; nothing on one world genuinely
needs anything from another. This mod makes the pairs themselves productive — a chain
that only completes when material from both planets meets in the same recipe. Each pair
has a small tree of its own ending in a **capstone**, and the five capstones feed a final
production line on the **Core of the Shattered Planet**, where the game is won.

## The design

| | |
|---|---|
| [00 — Vision](design/00-vision.md) | What the mod is, the five pairs, and how it ends |
| [01 — Principles](design/01-principles.md) | The rules every tree is held to, and the checklist |
| [02 — The cross-planet tree](design/02-tree-pattern.md) | The repeatable shape, and the register |
| [03 — The corridor](design/03-corridor.md) | The route past the Edge, and seeding the field |
| [04 — The Core](design/04-the-core.md) | The destination, its mechanics, and the sixth tech tree |
| [05 — Implementation plan](design/05-roadmap.md) | What gets built, in what order, and how it is proved |
| [Mechanics](design/mechanics.md) | The six new rules, one per tree plus the corridor |
| [Decisions](design/decisions.md) | What was settled, what it replaced, and why |
| [Spikes](design/spikes.md) | Engine assumptions, and what measuring them found |
| [Problems](design/problems.md) | Twenty frictions from a vanilla playthrough, as source material |

Per-tree specifications live in [design/trees/](design/trees/); none is written yet.

## Status

**Phase 0 complete.** The previous implementation — a single Vulcanus ↔ Fulgora tree
ending in the Quench Turbine — has been removed; it was built to a design that no longer
applies. The mod currently loads and adds nothing.

Next is Phase 1: the Core as a place. Spikes S1, S2 and S4 have passed against the real
engine, and S3 is half proven.

## Layout

```
design/              the specification, and the plan
prototypes/          (empty until Phase 1)
locale/en/           strings
graphics/            art specs and, later, art
migrations/          renames across versions
tools/               data-stage check, art derivation scripts
data.lua             data stage entry point
control.lua          runtime; near-empty by design
info.json
```

## Verifying a change

```
./tools/check-data-stage.sh     # loads the mod against the real engine,
                                # then verifies every referenced image exists
```

The second half matters: the data stage never opens image files, so a mod whose
icons all point at nothing loads cleanly here and is then refused outright by a
client. `tools/check-graphics.sh` runs on its own too.

Behavioural checks run on a headless server driven over RCON — see
[design/spikes.md](design/spikes.md#the-rig) for the harness, including the two
gotchas that cost time: the server exits on stdin EOF, and with no client attached it
free-runs, so measure against `game.tick` deltas rather than wall-clock sleeps.
