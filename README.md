# Space Age Extended

A Factorio: Space Age mod adding deeper, optional industrial relationships between planets. The mod applies one repeatable pattern — a cross-planet tree — once per planet pair; each tree terminates in a space-platform capability so the trees add up to a shared endgame.

- Overall pattern and roadmap: [design/framework.md](design/framework.md)
- First implemented tree — Vulcanus ↔ Fulgora: Cross-Planet Industrial Integration: [design/vulcanus-fulgora.md](design/vulcanus-fulgora.md)
- The mod's endgame — the corridor, the mandatory five trees, and why: [design/endgame.md](design/endgame.md)
- What's actually on the Core once a player arrives: [design/core.md](design/core.md)

## Status

Design phase. No prototypes implemented yet.

## Planned structure

```
prototypes/
  item.lua
  fluid.lua
  recipe.lua
  technology.lua
  entity.lua        -- Thermionic Generator
locale/
  en/
    strings.cfg
graphics/
data.lua
data-updates.lua
control.lua          -- thermal efficiency mechanic for Thermionic Generator
info.json
```

## Implementation phasing

See [design doc §17](design/vulcanus-fulgora.md#17-recommended-implementation-phasing):

1. **Phase 1** — Scrap refining chain (Foundry/EM Plant recipes, Molten Scrap → Copper Foil)
2. **Phase 2** — Electromagnetic circuit alt-recipes
3. **Phase 3** — Capstone (Catalyst Rod, Resonant Circuit, Magmatic Core, Thermionic Assembly)
4. **Phase 4** — Thermionic Generator (space platform power)
