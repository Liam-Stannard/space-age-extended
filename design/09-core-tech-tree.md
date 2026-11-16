# The Core — tech tree

The Core has its own tech tree, the sixth after the five planets' trees. Its
science pack can only be made on the Core.

## 1. Geodynamic science

The geodynamic science pack is made from items of the Core's own line, so the
tree only advances with a factory running on the Core. Its recipe is locked to
the Core.

## 2. The ladder

Tier 0, the foothold, is in the mod. The tiers above it wait on
`06-core-production-tree.md`.

### Core discovery

- **Description:** makes the Core reachable. Until it is researched, no platform
  can set a course there.
- **Cost:** 500 units of every vanilla science pack except military, up to
  promethium (eleven packs), 60 seconds each.
- **Purpose:** opens the Core as a destination.
- **Depends on:** Promethium science pack.

### Hydrogen extraction

- **Description:** a gas pump and a hydrogen turbine: enough power to begin
  with, and no more.
- **Cost:** none. It is a trigger: mine a boulder on the Core.
- **Purpose:** the Core's first power (see 08-core-power.md, section 2, for restarting after a blackout).
- **Depends on:** Core discovery.

### Kamacite processing

- **Description:** the Heavy crusher, crushing, kamacite smelting, and
  fines smelting.
- **Cost:** none. It is a trigger: mine kamacite ore, which only the big
  mining drill can.
- **Purpose:** turns ore into crushed kamacite and fines, and both into
  plate.
- **Depends on:** Hydrogen extraction.

### Vent tapping

- **Description:** the Vent Pump (see its spec).
- **Cost:** none. It is a trigger: craft 50 kamacite fines.
- **Purpose:** opens the kamacite vents.
- **Depends on:** Kamacite processing, and Uranium mining (the game
  needs it; see engine.md).

### Radiant power

- **Description:** radiant precipitation, the radiant generator, and
  radiant chunk crushing.
- **Cost:** none. It is a trigger: craft a Vent Pump.
- **Purpose:** power that doesn't run out. The fuel and the generator
  come together, so the generator never arrives without its fuel.
- **Depends on:** Vent tapping.

Power stage 2 (`08-core-power.md`) will be a geodynamic technology, placed
when the tiers above 0 are planned.
