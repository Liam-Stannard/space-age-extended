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

**Phases 0–8 are built.** The Core exists as a planet with its own terrain, three sited
resources and four mechanics; the corridor reaches it; the sixth technology tree and the
geodynamic science pack are in; the Ignition Array fires and wins the game; and the first
of the five cross-planet trees — Fulgora ↔ Aquilo — is real rather than stubbed.

**Nothing has been played.** Every number in the mod is a first guess, verified against
the engine but never against a person.

## What is left

Roughly in the order worth doing.

### 1. Play it

This is the one that decides the rest. The open question is whether the Core is
interesting to build on or a chore in a pretty coat — specifically whether the
vent → settle → cast loop has enough going on, whether whisker beds read as a farm or as
waiting, and whether a strike every ninety seconds is weather or an annoyance.

Until that is answered, everything below is speculative polish.

### 2. Four trees are still stubs

Vulcanus ↔ Fulgora, Vulcanus ↔ Gleba, Fulgora ↔ Gleba and Gleba ↔ Aquilo all craft their
capstone product from an iron plate, labelled placeholder. Each needs what
[Fulgora ↔ Aquilo](design/trees/fulgora-aquilo.md) got, and that document is the template:

- an **anchor** that makes the crossing impossible to dodge by moving a machine,
- a **chain on each world**,
- a **capstone building** that is useful when earned, on the way to the Core, and there,
- **4–10 technologies**.

The anchors are the risky part. A tree whose crossing a player can sidestep is broken
however good it looks, and the rule it has to satisfy is
[principles §1](design/01-principles.md).

### 3. Two things only a client can check

- **Do chunks from a seeded asteroid reach a collector?** The unproven half of
  [spike S3](design/spikes.md). Chunks are not entities the search API can see, and the
  vanilla control failed identically, so the headless rig cannot answer it.
- **Storm rate and damage.** No natural strike was ever observed headlessly — Fulgora
  produced none either under the same conditions — so 600 damage every ninety seconds is
  still an assertion.

### 4. Art

Sprites and icons are all vanilla stand-ins. Two mismatches worth knowing beyond the
sprite work itself:

- the **whisker plant renders as a Gleba tree**, because its prototype is a copy of
  `tree-plant`;
- the **whisker bed tile is a clone of stone path**, so a farm cannot be told apart from
  a concrete pad.

Terrain is a choice rather than a default. `prototypes/core/map-gen.lua` defines four
palettes and selects one with a single `PALETTE` constant at the top of the file:

| Palette | What it looks like |
|---|---|
| `struck-nickel` *(selected)* | Grey mineral ground and cool unlit cracks, with a sparse blue-violet scorch. Electrical rather than molten, so it ties to the arc storms and does not read as a second Vulcanus |
| `iron-crust` | Black and grey ground and dark ash, with no lit tile anywhere. Heat exists only where the player built for it |
| `frozen-crust` | Cold ground cut by hot veins where the interior comes close -- the design document's own sentence, made visible |
| `ashen-furnace` | Ash with common orange heat tiles. The most dramatic, and the closest to Vulcanus |

Each palette carries its own temperature, moisture and aux expressions, because tiles
choose themselves along those three axes and a tile list on its own decides nothing.
Space Age's volcanic tiles and Alien Biomes' mineral, snow and heat tiles are listed
separately, so without the pack a palette degrades to its Space Age half rather than to a
guess. **Not yet seen in game**: the four palettes are tuned from Alien Biomes' published
autoplace windows, not from a screenshot, and the exact spread each one produces still
wants a fresh surface and an eye. Switching palettes only affects chunks that do not
exist yet.

### 5. Balance is arithmetic, not play

The parity between what the technology tree costs and what the Ignition Array costs was
calculated, not felt. The hundred segments, the pack cost, ore richness and vent decline
are all untested.

### 6. Tidying

`design/04-the-core.md` still lists the intermediates and end products as open; they are
built. And the branch names do not describe their contents — `arc-mast-art` carries
Phase 8 and the climate fix, because that was the branch checked out when they were
committed.

## Layout

```
design/              the specification, and the plan
prototypes/          (empty until Phase 1)
locale/en/           strings
graphics/            art specs and, later, art
migrations/          renames across versions
tools/               data-stage check, art generation and sprite pipeline
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

## Building art

Per-building specifications live in [graphics/](graphics/) — copy
[building-spec-template.md](graphics/building-spec-template.md) and fill it in
*before* commissioning art. Its appendices carry the prompt anatomy, the
browser-generation workflow and the production pipeline; read them first, since
most of what is in them was learned the expensive way.

```
tools/generate-building-art.py <spec> --list     # the prompts, for the browser
tools/process-building-art.py <plate> --report   # measure a plate; never eyeball one
tools/process-building-art.py <plate> --dekey    # recover alpha from a flattened export
tools/derive-glow.py  --lit A --unlit B          # recover the additive glow layer
tools/build-glow-frames.py --glow G              # spritesheets from one plate
```

Two rules worth stating here rather than only in the template: **once a design
is locked, every later image is an edit of the approved file, never a fresh
generation**, and **plates are judged by measurement, not by looking at them** —
a transparent PNG takes the colour of whatever the viewer puts behind it.

Behavioural checks run on a headless server driven over RCON — see
[design/spikes.md](design/spikes.md#the-rig) for the harness, including the two
gotchas that cost time: the server exits on stdin EOF, and with no client attached it
free-runs, so measure against `game.tick` deltas rather than wall-clock sleeps.
