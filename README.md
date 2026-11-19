# Space Age Extended

An expansion for Factorio: Space Age 2.1. What the mod is: see
[00 — Vision](design/00-vision.md).

## The design

| | |
|---|---|
| [00 — Vision](design/00-vision.md) | What the mod is, its five trees, and the endgame |
| [01 — Principles](design/01-principles.md) | The rules every part of the mod meets, and what each applies to |
| [03 — The corridor](design/03-corridor.md) | The route past the Shattered Planet |
| [04 — The Core](design/04-the-core.md) | The planet, its surface and its resources |
| [06 — Core production tree](design/06-core-production-tree.md) | The Core's production line, as built |
| [08 — The Core's power](design/08-core-power.md) | The radiant cycle, in two stages |
| [09 — The Core's tech tree](design/09-core-tech-tree.md) | Each technology, its cost and what it needs |
| [Ideas](design/ideas.md) | Proposals nobody has ruled on — **never built without being agreed first** |

Each planet's tree spec lives in [design/trees/](design/trees/) and follows
[templates/tree-spec-template.md](templates/tree-spec-template.md). The old pair
specs there are being reworked ([TODO.md](TODO.md)).

How work is done in this repo — where design, concept art, templates and tasks
live — is set out in [claude.md](claude.md). Outstanding work is in
[TODO.md](TODO.md).

## Status

The mod is being rebuilt from the landing up, and nothing has been played yet.

## Checking a change

```
./tools/check-data-stage.sh
```

This loads the mod in the real game, then runs the checks listed in
.claude/skills/factorio-task/knowledge/pipeline.md (Data stage). The image check matters, because loading the mod does
not check images (see .claude/skills/factorio-task/knowledge/engine.md,
"Running a client on this machine"). `tools/check-graphics.sh` runs the image checks alone.

Behaviour is checked on a headless server, driven over RCON (`tools/rcon.py`).
Two things to know: the server stops when its input closes, and with no player
connected it runs as fast as it can, so time things in game ticks, not seconds.

## Building art

A building's spec is made from
[templates/building-spec-template.md](templates/building-spec-template.md). claude.md rules 2
and 3 say where the spec, the Blender model, the render pipeline and the art live.

## Icon art

Icons are made a production chain at a time, so a chain's icons look made from
each other. They are rendered in Blender; the tools are in
.claude/skills/factorio-task/knowledge/pipeline.md (Icons).
