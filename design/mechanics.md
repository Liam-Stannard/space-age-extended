# Mechanics

**The mod creates its own problems.** Each tree introduces exactly one new rule
the player must design around, taught alone in that tree and required again at
the end, where the five combine.

A mechanic qualifies only if it is a genuinely new thing to design around,
Factorio-shaped rather than bolted on, and implementable in prototypes —
ideally with no control-stage script. Every engine fact cited here was checked
against a data dump of the installed game.

---

## Chosen

### Maturation — Vulcanus ↔ Gleba

**The new rule: something that gets better if you leave it alone.**

A bio-mineral seeded on Gleba and held in Vulcanus's heat **improves with age**.
It is spoilage run backwards: the timer is the process. The player's instinct —
push everything through as fast as it will go — is exactly wrong here, and a
warehouse becomes a production building.

**Why this pair.** Gleba is the only world that grows anything; Vulcanus is the
only one with heat to spare. Neither can mature anything alone.

**Implementation.** `spoil_ticks` with a `spoil_result` pointing at a *better*
item. The engine's spoilage is only a timer aimed at another item, and nothing
requires the destination to be a downgrade — so chains of two or three stages
cost nothing extra. No script.

**What it teaches.** Deliberate storage. Sizing a buffer to a rate rather than to
a fear, and buying throughput with floor space instead of machines.

**Where it lands at the end.** Both places, which is unusual:

- *On the corridor* — the journey to the Core is a platform run measured in real
  time, so one cargo ripens while everything else is merely costing money. The
  trip becomes productive for exactly one material.
- *On the Core* — it is the **central process**. The billet cast from core melt
  is unfinished when it leaves the mould and must age before the final line can
  use it, so the last stage can be widened but never rushed. See
  [the Core](05-the-core.md#8-maturation-as-the-cores-central-process).

---

## Still to choose

Four trees have no mechanic yet.

| Pair | Available after | Notes toward a mechanic |
|---|---|---|
| Vulcanus ↔ Fulgora | both | The system's heat against its electricity; two worlds that each bootstrap from a single input |
| Fulgora ↔ Gleba | both | The world with no soil against the world with no ore |
| Fulgora ↔ Aquilo | Aquilo | Holmium in the cold — vanilla makes superconductors from exactly this pairing and then builds nothing structural on it |
| Gleba ↔ Aquilo | Aquilo | The world whose every product expires against the only world cold enough to stop one |

The selection rules are in
[the tree pattern](02-tree-pattern.md#5-one-reserved-mechanic-per-tree). The
short version: a new rule rather than a new recipe, belonging to those two worlds
specifically, implementable in prototypes, load-bearing either on the corridor
platform or on the Core, and not a variation on a lesson another tree already
teaches.

---

## Considered and cut

Recorded so they are not re-proposed as new.

| Mechanic | Pair it was for | The idea | Why it went |
|---|---|---|---|
| **Charge** | Vulcanus ↔ Fulgora | Cast cells charged by lightning, self-discharging on a timer, so energy could be moved but never hoarded | Cut |
| **Substrate** | Fulgora ↔ Gleba | Ground manufactured from scrap so Gleba's organisms could grow off-world, paid for in floor tiles | Cut |
| **Launch** | Fulgora ↔ Aquilo | A superconducting silo re-pricing freight, fixed endpoint to fixed endpoint | Cut — and the silo prototype requires gravity, so it could never have worked platform-to-platform |
| **Suspension** | Gleba ↔ Aquilo | Perishables suspended in coolant, indefinitely, at the cost of a permanent cold chain | Cut |

Three of the four leaned on the spoilage timer, as maturation does. Whatever
replaces them should mostly draw on other parts of the engine — fluid
temperature, surface conditions, heat networks, tiles, plants, lightning,
asteroid definitions — so the five do not all turn out to be one idea in
different clothes.

---

## Engine features available, verified

Useful when judging whether a candidate is implementable.

| Feature | What it allows |
|---|---|
| `spoil_ticks`, `spoil_result` | An item that becomes another item after a time — better or worse |
| `spoil_to_trigger_result` | An item that *does something* when its timer runs out, as vanilla's eggs hatch |
| `surface_conditions` on recipes | A process locked to a physical property, as vanilla locks acid neutralisation to pressure 4000 |
| `surface_conditions` on entities | A building that can only stand somewhere, as the biolab is Nauvis-only and the agricultural tower Nauvis-and-Gleba-only |
| `heating_energy` + planet `entities_require_heating` | Buildings that need heat to run, and a world that demands it |
| `plant` + tile restrictions | Mod crops with `growth_ticks`, growing only on named tiles |
| `lightning` + `lightning-attractor` | Storms as hazard and as power, with a real energy buffer |
| Fluid temperature + `generator` | Power computed from a fluid's temperature, clipped at a cap |
| `asteroid-chunk`, `asteroid`, `space-connection` | New chunk types with their own spawn rates along a named route |
| Custom `fuel-category` | A fuel only certain machines will burn |
| Item `weight` vs `default_rocket_lift_weight` (1,000,000) | Freight cost per item, set deliberately rather than derived |
