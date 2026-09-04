# The Cross-Planet Tree

The mod is not one feature. It is a **pattern**, applied once per planet pair.
This document is the pattern and the register of which pairs have claimed what.

---

## 1. The shape

Every tree is describable in these seven parts. A proposal that cannot fill in
1–5 is not ready to be balanced.

1. **Two planets.** One pair per tree.
2. **A forcing anchor in each direction** — at least one recipe that cannot be
   completed without importing a resource exclusively native to the other world
   ([principles §1](01-principles.md)). Round trips, where material physically
   returns (a depleted catalyst, a spent coolant), create more sustained
   logistics pressure than one-way exports and are preferred where the mechanic
   supports one honestly.
3. **A processing chain on each planet**, built from existing specialised
   buildings, feeding an existing production concern on that world rather than
   standing up a parallel economy beside it.
4. **A shared capstone.** Each planet produces one half; neither half is useful
   alone; the combining recipe is craftable anywhere, because both inputs are
   already planet-locked by their own production. The capstone is the proof the
   player built out both sides.
5. **A platform payoff** — the capstone unlocks one
   [platform capability](03-platform-system.md) that answers one
   [corridor band](04-corridor.md) no other tree answers.
6. **Interaction.** The capability draws on at least one shared platform resource
   and changes the arithmetic of at least one other capability.
7. **A technology progression** that gates each stage sensibly and ends in the
   platform technology, with explicit cross-dependencies where a step genuinely
   needs both halves of the chain.

## 2. Capstone requirements

Capstone items are **clean, self-contained, freely shippable end products**: no
planet-locked property, no fluid state, no decay mechanic.

This is not so a final technology can tally them — [the corridor](04-corridor.md)
gates on traversal, not on an ingredient list. It is because these items have to
be freighted two million kilometres down a supply line and consumed in bulk at
the far end. A capstone that spoils, or that only works where it was made, cannot
make that trip.

## 3. Anchor variety

Trees should not reskin each other. The first tree's anchors are a bulk mineral
reagent and an unshippable bulk fluid; a second tree built on the same shape
teaches the player nothing new. Prefer anchors that are constrained in a
different *kind* of way — perishability, temperature, pressure, volume, a
resource that can only be processed in transit.

This is a real constraint on pair selection, not a preference. If two trees'
logistics feel the same to build, one of them is redundant however different its
items are.

## 4. Progression spread

Three of the five subsystems currently sit behind Aquilo, and the corridor sits
past the Solar System Edge. That bunches the mod's content into the stretch of
the game where most players stop.

When choosing a pair for an open subsystem, **earlier is better where the anchor
allows it**. A tree a player can start before Aquilo is worth more to the mod
than a marginally more elegant one they will reach only if they were going to
finish anyway.

---

## 5. The tree register

Pair assignments below are **provisional** until that tree's anchor has actually
survived the [checklist](01-principles.md#the-checklist). The subsystem claims
are firm — no two trees share one — but a pair that cannot produce an honest
anchor gets replaced, not bent.

| # | Pair | Subsystem | Capability | Capstone | Status |
|---|---|---|---|---|---|
| 1 | Vulcanus ↔ Fulgora | Power | Quench Turbine + coolant loop | Thermionic Assembly | Built and engine-verified; only phase 1 played — [spec](trees/vulcanus-fulgora.md) |
| 2 | Vulcanus ↔ Aquilo *(provisional)* | Structure | Ablative hull | — | Not designed |
| 3 | Fulgora ↔ Aquilo *(provisional)* | Asteroid processing | Electrode Array | — | Not designed |
| 4 | *unassigned* | Thrust | Electric propulsion | — | Not designed |
| 5 | Nauvis ↔ Fulgora *(provisional)* | Defence | Deflector Field | — | Not designed |

**The optional tier.** Trees beyond these five make the corridor *cheaper*, never
possible: the Cryostat, the Growth Chamber, Enriched Oxidiser and the Capacitor
Rail Battery are the current candidates. Optional trees may overlap each other
freely — redundancy is only forbidden on the mandatory path, where it is exactly
what would make a tree skippable.

**Gleba is currently absent from the mandatory five.** That is a live problem
given §3: Gleba's spoilage clock is the most distinct anchor in the game and it
is sitting in the optional tier. Thrust is the one unassigned pair. Either it
becomes Gleba's, or the mod should accept honestly that its most interesting
anchor is optional content. This is an open decision, recorded in
[decisions.md](decisions.md).

---

Next: what the capabilities plug into — [the platform system](03-platform-system.md).
