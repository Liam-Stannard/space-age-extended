# Space Age Extended

A Factorio: Space Age mod that deepens the relationships *between* planets.
Vanilla gives each world its own self-contained tech tree; this mod adds an
optional layer on top, in which each planet pair gains a genuine two-way
industrial dependency, each of those trees ends in one space-platform
capability, and the accumulated capabilities open a destination vanilla leaves
unfinished.

A player who ignores the mod finishes Space Age exactly as before.

## The design documents

Read in order; each owns exactly one thing.

| | |
|---|---|
| [00 — Vision](design/00-vision.md) | What the mod is, and what it is not |
| [01 — Principles](design/01-principles.md) | The rules everything is held to, and the checklist a tree must pass |
| [02 — The cross-planet tree](design/02-tree-pattern.md) | The repeatable pattern, and the register of which pair claims what |
| [03 — The platform system](design/03-platform-system.md) | Capabilities, the five shared resources, and how they interact |
| [04 — The corridor](design/04-corridor.md) | The endgame journey: bands, hazards, depots |
| [05 — The Core](design/05-the-core.md) | The destination, and what the capstones are spent on |
| [06 — Roadmap](design/06-roadmap.md) | Milestones, exit criteria, kill criteria |
| [Decisions](design/decisions.md) | Settled reversals and open questions, recorded once |
| [Tree 1 — Vulcanus ↔ Fulgora](design/trees/vulcanus-fulgora.md) | The one implemented tree, at specification detail |

`PROGRESS.md` is the implementation status snapshot — what is built, how it was
verified, and how to resume.

## Status

Tree 1 is implemented and verified against the real engine. Only its first phase
has been played by a human; the Quench Turbine and the balance pass are
engine-measured and unplayed. Trees 2–5, the corridor and the Core are designed
on paper.

The next thing that happens is [M0](design/06-roadmap.md#m0--play-what-exists) —
playtest what exists — because every other document assumes it is good.

## Structure

```
prototypes/
  item.lua
  fluid.lua
  recipe.lua
  technology.lua
  entity.lua        -- the Quench Turbine
locale/en/strings.cfg
graphics/            -- icons and the turbine's entity sheets
migrations/          -- item/recipe renames across versions
tools/               -- data-stage check, derived-art scripts
data.lua
data-updates.lua
control.lua          -- empty; the mod is entirely prototype-driven
info.json
```

## Tree 1 phasing

All four phases are implemented and engine-verified; see
[the tree spec §17](design/trees/vulcanus-fulgora.md#17-recommended-implementation-phasing).

1. **Phase 1** — scrap refining chain (Molten Scrap → Copper Foil) — *played*
2. **Phase 2** — electromagnetic circuit alt-recipes
3. **Phase 3** — capstone (Catalyst Rod, Resonant Circuit, Magmatic Core,
   Thermionic Assembly)
4. **Phase 4** — the Quench Turbine and its quench recipe ladder
