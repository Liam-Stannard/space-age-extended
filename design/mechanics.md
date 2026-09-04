# Mechanics

The mod does not borrow vanilla's problems. It **creates** them, one per pair,
and each is taught alone before the endgame asks for all of them at once.

A mechanic qualifies only if it is: a genuinely new thing to design around,
Factorio-shaped rather than bolted on, and **implementable in prototypes** —
ideally with no control-stage script at all. The engine facts each one relies on
are named, and all were checked against a data dump of the installed game.

---

## The five

### 1. Charge — Vulcanus ↔ Fulgora

**The new problem: energy becomes a physical good, and it leaks.**

A cast cell is charged by Fulgora's lightning and discharged wherever it is
needed. It is not a battery in the vanilla sense — **it self-discharges on a
timer**, so a stockpile is a slowly emptying one. Energy can be *moved* but not
*hoarded*, which makes power a logistics problem instead of a generation one.

- **Why this pair.** Vulcanus casts the body; Fulgora is the only world where
  energy arrives free and in spikes. Neither half is any use alone: Fulgora
  cannot cast, Vulcanus has nothing to charge with.
- **Implementation.** Two items and a decay: `spoil_ticks` on the charged cell
  with `spoil_result` pointing at the depleted one, a custom `fuel_category` with
  a real `fuel_value`, and a burner generator that consumes it. Charging is an
  ordinary recipe with a large `energy_required` in an electromagnetic plant.
  All prototype-level.
- **Teaches.** That power can travel, and that buffering it costs you.
- **At the Core.** How a depot runs before anything local generates.

### 2. Maturation — Vulcanus ↔ Gleba

**The new problem: something that gets better if you leave it alone.**

A bio-mineral seeded on Gleba and kept in Vulcanus's heat **improves with age**.
It is spoilage run backwards: the timer is the process. The player's instinct —
push everything through as fast as possible — is exactly wrong, and a warehouse
becomes a production building.

- **Why this pair.** Gleba is the only world that grows anything; Vulcanus is the
  only one with heat to spare. Maturation needs both, and neither can do it
  alone.
- **Implementation.** `spoil_ticks` with a `spoil_result` that is a *better*
  item — the engine's spoilage is just a timer pointing at another item, and
  nothing requires the destination to be worse. Chains of two or three stages are
  free.
- **Teaches.** Deliberate storage. Sizing a buffer to a rate rather than to a
  fear.
- **At the Core.** The journey out stops being pure cost: cargo ripens en route,
  so the corridor's length becomes an asset for exactly one material.

### 3. Substrate — Fulgora ↔ Gleba

**The new problem: growing things where there is no ground.**

Fulgora has no soil and Gleba has no ore. A substrate manufactured from scrap
lets Gleba's organisms grow off-world — on a platform, in a depot, eventually on
the Core — but it is laid as **tiles**, so cultivation costs floor area rather
than machines, which is a cost the player has never had to plan for.

- **Why this pair.** The world with no soil supplying the ground; the world with
  no ore supplying the life. It is the sharpest complement in the system.
- **Implementation.** A mod tile for the substrate, a mod `plant` prototype with
  `growth_ticks` and an `autoplace.tile_restriction` naming that tile, and a
  cultivation tower with its own `surface_conditions`. Exactly the shape of
  vanilla's `tree-plant` and agricultural tower, which are 36,000 ticks and a
  tile restriction respectively.
- **Teaches.** Area as a production input, and growth time as a rate.
- **At the Core.** The only source of organic material anywhere out there.

### 4. Launch — Fulgora ↔ Aquilo

**The new problem: freight without rockets, but only between fixed points.**

A superconducting launcher throws cargo along a line the player has established,
consuming enormous power and a superconducting consumable instead of rocket
parts. It is cheaper per tonne than a rocket and far less flexible: it goes where
it was built to go, and nowhere else.

- **Why this pair.** Superconduction is Fulgora's holmium in Aquilo's cold;
  vanilla already makes that exact pairing and then never uses it for anything
  structural.
- **Implementation.** A `rocket-silo`-derived entity whose "rocket part" recipe
  is the mod's own, so freight cost is re-priced rather than removed. Native, no
  script. **Constraint:** the silo prototype requires gravity, so launchers are
  ground-to-orbit, not platform-to-platform — the corridor is built of hops
  between anchored points, which is the more interesting shape anyway.
- **Teaches.** That cheap freight is bought with infrastructure and power.
- **At the Core.** The supply line's backbone, and the thing that eventually
  reverses to carry Core material home.

### 5. Suspension — Gleba ↔ Aquilo

**The new problem: the clock can be stopped, at a price.**

Perishables can be suspended in an Aquilo-derived coolant and carried
indefinitely — but suspension consumes the coolant continuously, and waking the
cargo is a separate step at the far end. The player gains the ability to ship
Gleba's output anywhere, and inherits a cold chain to run.

- **Why this pair.** The world whose every product expires, against the only
  world cold enough to stop one.
- **Implementation.** A suspend recipe taking the perishable plus a cold fluid
  and yielding an item with no `spoil_ticks`; a wake recipe reversing it. Both
  ordinary recipes. The coolant loop is a fluid the player must keep cold, which
  is where the ongoing cost lives.
- **Teaches.** That preservation is a chain, not a checkbox.
- **At the Core.** How anything alive survives the longest journey in the game.

---

## How they combine

The Core is where all five are required at once, and the interesting part is that
they interfere with each other:

- **Charge** powers a depot, but charge decays, so a depot has to be *visited* on
  a schedule rather than stocked once.
- **Suspension** keeps cargo alive across the trip, but the coolant it consumes
  is itself freight, so preserving more means carrying more.
- **Maturation** wants the journey to be *long*; suspension wants it short.
  One material ripens while another is racing a clock, on the same ship.
- **Substrate** makes organics locally, which reduces what suspension has to
  carry — but costs floor area on a platform where every tile was launched.
- **Launch** is what makes any of it affordable, and it is the one thing that
  cannot be built where there is no ground yet.

That is the endgame in one paragraph: not five upgrades installed side by side,
but five rules that have to be balanced against each other in the same build.

---

## Alternates

Kept in case one of the five fails in design.

| Mechanic | Pair | The new problem | Implementable via |
|---|---|---|---|
| **Unstable intermediate** | any | An item that damages its machine if it sits, so buffers are impossible and throughput must be matched exactly | `spoil_to_trigger_result`, as vanilla's eggs use to hatch |
| **Vacuum curing** | any with a platform step | One step of a chain only runs at pressure 0, forcing a factory onto a platform | recipe `surface_conditions` at pressure 0, as thruster fuel does |
| **Cultures that must be fed** | Fulgora ↔ Gleba | A process that dies if the line ever stops, and restarting needs a seed shipped from the other world | a fast `spoil_ticks` on a culture the recipe both consumes and returns |
| **Heat as a travelling utility** | any | Mod buildings that require heating wherever they are, dragging a heat network along the chain | `heating_energy` on the entity; `entities_require_heating` is a planet property, so the Core can demand it |
| **Provoked ground** | Vulcanus ↔ Gleba | Production that attracts something, so scaling up has a defensive cost | `segmented-unit` and spawner prototypes — the most expensive option here, and the only one needing real new art |

---

## What this does not include

**Power generation.** Vanilla covers it to the Edge, and past the Edge it is
answered by a new asteroid type in the far field rather than by a pair — see
[the problem catalogue](problems.md#power-is-not-one-of-the-five). Charge moves
energy; it does not make it.
