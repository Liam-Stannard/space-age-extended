# Space Age Extended

A Factorio: Space Age mod that deepens the relationships *between* planets.
Vanilla gives each world its own self-contained tech tree; this mod adds an
optional layer on top, in which each planet pair gains a genuine two-way
industrial dependency, each of those trees ends in one space-platform
capability, and the accumulated capabilities open a destination vanilla leaves
unfinished.

A player who ignores the mod finishes Space Age exactly as before.

## Status

The Vulcanus ↔ Fulgora tree is implemented and verified against the real
engine. Only its first phase has been played by a human; the Quench Turbine and
the balance pass are engine-measured and unplayed.

The design documents are being reworked from scratch, so `design/` is currently
empty. Until that lands, the code itself is the record of what the mod does.

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

## Vulcanus ↔ Fulgora phasing

All four phases are implemented and engine-verified.

1. **Phase 1** — scrap refining chain (Molten Scrap → Copper Foil) — *played*
2. **Phase 2** — electromagnetic circuit alt-recipes
3. **Phase 3** — capstone (Catalyst Rod, Resonant Circuit, Magmatic Core,
   Thermionic Assembly)
4. **Phase 4** — the Quench Turbine and its quench recipe ladder
