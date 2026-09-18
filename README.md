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
| [05 — What is left on the Core](design/05-core-remaining.md) | The capstone stubs, and why they block the line |
| [06 — Core production tree](design/06-core-production-tree.md) | Draft of a deeper Core line |
| [07 — Implementation plan](design/07-roadmap.md) | What gets built, in what order, and how it is proved |
| [08 — The Core's power](design/08-core-power.md) | The radiant cycle, in four stages |
| [Mechanics](design/mechanics.md) | One new rule per tree, plus the corridor — to be decided |
| [Ideas](design/ideas.md) | Proposals nobody has ruled on — **never built without being agreed first** |

Per-tree specifications live in [design/trees/](design/trees/). Only
[Fulgora ↔ Aquilo](design/trees/fulgora-aquilo.md) is written.

How work is done in this repo — where design, concept art, templates and tasks
live — is set out in [claude.md](claude.md). Outstanding work is in
[TODO.md](TODO.md) and nowhere else.

## Status

The Core exists as a planet with its own terrain, three sited resources and its
mechanics; the corridor reaches it; the sixth technology tree and the geodynamic
science pack are in; and the Ignition Array fires and wins the game. Of the five
cross-planet trees, Fulgora ↔ Aquilo is real and the other four craft their
capstone from a stub recipe. That is `master`.

**This branch is the landing slice.** It carries only what is being brought up
to quality first: the three landing technologies (Crust tapping, Core survey,
Radiant power), the crusher, drill and vacuum furnace, the radiant chunk line
that feeds the generator, and the five cross-planet capstone products. The melt
line, the geodynamic pack, the Array and everything past the landing stay on
`master`, and the game does not end here.

**Nothing has been played.** Every number in the mod is a first guess, verified against
the engine but never against a person.

## Layout

```
design/              the specification — changed only by agreement
concept/<building>/  every concept; design, never shipped
templates/           prompt and spec templates
prototypes/          the data stage, split by area (core/, trees/, corridor.lua)
graphics/            implementation: signed-off or placeholder art only
locale/en/           strings
migrations/          renames across versions
tools/               data-stage checks, art generation and sprite pipeline
data.lua             data stage entry point
control.lua          runtime: the win condition
TODO.md              every outstanding task
info.json
```

## Verifying a change

```
./tools/check-data-stage.sh     # loads the mod against the real engine, then checks
                                # images, dumped graphics paths, recipes and
                                # technology reachability
```

The image checks matter: the data stage never opens image files, so a mod whose
icons all point at nothing loads cleanly and is then refused outright by a
client. `tools/check-graphics.sh` runs on its own too.

Behavioural checks run on a headless server driven over RCON (`tools/rcon.py`).
Two gotchas that cost time: the server exits on stdin EOF, and with no client
attached it free-runs, so measure against `game.tick` deltas rather than
wall-clock sleeps.

## Building art

Copy [templates/building-spec-template.md](templates/building-spec-template.md)
to `concept/<building>/building-spec-<building>.md` and fill it in *before* commissioning
art. Its appendices carry the prompt anatomy, the browser-generation workflow and
the production pipeline; read them first, since most of what is in them was
learned the expensive way.

```
tools/generate-building-art.py <spec> --list     # the prompts, for the browser
tools/process-building-art.py <plate> --report   # measure a plate; never eyeball one
tools/process-building-art.py <plate> --dekey    # recover alpha from a flattened export
tools/derive-glow.py  --lit A --unlit B          # recover the additive glow layer
```

Every concept goes under `concept/<building>/`. A plate moves to
`graphics/entity/<building>/` only once it is signed off.

## Icon art

Icons are generated a **production chain at a time**, not one at a time, because
what matters is whether the icons of a chain read as things made from each other
— and generated separately they do not.
[templates/icon-sheet-prompts.md](templates/icon-sheet-prompts.md) sets out the
method: a labelled review sheet, then a flat-background harvest sheet produced by
*editing* the approved one, cut and keyed by tools rather than by a generator.

```
tools/cut-icon-sheet.py <harvest sheet> <dir> name1 name2 ...  # sheet -> one PNG per icon
tools/key-icons.py graphics/icons <dir>/name1.png:name1 ...    # PNG -> 64px mipmap strip
```

Two rules worth stating here rather than only in the template: **once a design
is locked, every later image is an edit of the approved file, never a fresh
generation**, and **plates are judged by measurement, not by looking at them** —
a transparent PNG takes the colour of whatever the viewer puts behind it.
