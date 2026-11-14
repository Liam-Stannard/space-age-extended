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
- **Cost:** 500 units of all eleven vanilla science packs, up to promethium, 60
  seconds each.
- **Purpose:** opens the Core as a destination.
- **Depends on:** Promethium science pack.

### Hydrogen extraction

- **Description:** a gas pump and a hydrogen turbine: enough power to begin
  with, and no more.
- **Cost:** none. It is a trigger: mine a boulder on the Core.
- **Purpose:** the Core's first power, and its way back after a blackout.
- **Depends on:** Core discovery.

### Core survey

- **Description:** the Ballast Drill, the only drill that mines kamacite ore.
- **Cost:** none. It is a trigger: craft a gas pump.
- **Purpose:** the first ore out of the ground.
- **Depends on:** Hydrogen extraction.

### Gravity crushing

- **Description:** the Drop Crusher, crushing, and kamacite smelting.
- **Cost:** none. It is a trigger: craft a Ballast Drill.
- **Purpose:** turns ore into crushed kamacite and fines, and crushed kamacite
  into plate.
- **Depends on:** Core survey.

### Vacuum sintering

- **Description:** the Vacuum Furnace, and fines smelting.
- **Cost:** none. It is a trigger: craft 50 kamacite fines.
- **Purpose:** gives the crusher's fines a use.
- **Depends on:** Gravity crushing.

### Vent tapping

- **Description:** the Vent Pump, which draws molten kamacite from a kamacite
  vent.
- **Cost:** none. It is a trigger: craft a Vacuum Furnace.
- **Purpose:** opens the kamacite vents.
- **Depends on:** Vacuum sintering, and Uranium mining, which the game needs
  before any drill can mine with a fluid.

### Radiant power

- **Description:** the Reaction Plant, radiant precipitation, the radiant
  generator, and radiant chunk crushing.
- **Cost:** none. It is a trigger: craft a Vent Pump.
- **Purpose:** power that doesn't run out. The plant, the fuel and the generator
  come together, so the generator never arrives without its fuel.
- **Depends on:** Vent tapping.

Power stages 2 to 4 (`08-core-power.md`) will be geodynamic technologies, placed
when the tiers above 0 are planned.
