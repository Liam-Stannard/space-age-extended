# The Core's power — the radiant cycle

The Core has no sunlight, no combustion and no water. Its power is one loop in
four stages, built from the two fluids the planet has and nothing else.

## 1. Nothing burns, and this is what that means

Pressure 5 refuses every burner prototype, so nothing on this planet can be
oxidised in the open — there is no open. It can be oxidised in a **liquid**.

That is the whole design. The pool is the reagent bath, and chemistry does what
fire is not allowed to.

## 2. The two fluids

| Fluid | Where | Supply |
|---|---|---|
| **Radiant solution** | drawn off the pool's shore with a crust tap | 6–30% of the surface (`map-gen.lua`), abundant |
| **Crust gas** | drawn off a crust vent with a crust tap | rare and clustered — patches a player travels to |

The solution is the corridor's isotope in suspension: **it carries the energy**.
The gas is the reagent that strips it out and drops it as a solid. That is why
enriching the solution yields more fuel and enriching the gas would not.

One building draws both. A crust tap standing on a vent gives gas; the same tap
standing on the shore gives solution, because the shore tile carries the fluid the
way the vent tile carries gas. **There is no extraction building in this document
that does not already exist.**

## 3. The first watt

The **crust turbine** burns crust gas for its `fuel_value` — 1.8 MW, three
turbines to a tap. It is outside the cycle on purpose, and it is the only power on
the planet that needs no power to make power: the reaction plant is an assembling
machine, and a recipe taking two fluids cannot be made in a pocket.

That makes it the Core's **black start**. A grid running on radiant fuel that
browns out stops its reaction plants, which stops the fuel, which stops the
generators — and nothing else here will break that loop. One turbine on a vent is
the way back.

Everything else in this document assumes it is standing.

## 4. The cycle

### Stage 1 — the basic reaction

**Reaction plant**: two fluids in, one item out, on a private category.

```
100 radiant solution + 100 crust gas → 1 radiant fuel
```

Burned in the **radiant generator** at 10 MW — 500 MJ a cell, so fifty seconds.
Its `burnt_result` is a **spent cell**, discarded at this stage.

Helium-3 appears nowhere in the power line. It keeps one job: throttling the
melt, and the two cold recipes.

### Stage 2 — solution enrichment

**Isotope centrifuge**, which returns at stages 3 and 4 the way vanilla's
centrifuge runs uranium processing, reprocessing and Kovarex.

```
200 radiant solution → 100 enriched solution
100 enriched solution + 100 crust gas → 3 radiant fuel
```

Two cells per 200 solution becomes three — and the same +50% on the crust gas,
which is the genuinely scarce half. Still fluids, still pipes: the complexity
added is a building and a ratio.

### Stage 3 — cell reprocessing

Three recipes across the two existing buildings.

```
4 spent cells + 50 crust gas  → 100 spent solution
100 spent solution            →  80 stripped solution + 2 radiant sludge
80 stripped solution          →  40 radiant solution
```

Roughly 40% of the solution back per cell burned. **This is the first stage that
runs backwards** — a belt leaving the power plant and returning to the chemistry.
Stages 1 and 2 are a line; this makes it a loop.

### Stage 4 — fuel enrichment

```
5 radiant fuel + 2 radiant sludge → 1 enriched radiant fuel
```

**Enriched radiant fuel is in its own fuel category**, so the radiant generator
cannot burn it. The **radiant reactor** is the only thing that will: 40 MW before
the neighbour bonus.

**The sludge is why this works.** Enrichment concentrates an isotope and sludge is
what is already concentrated, so stage 3's byproduct is stage 4's reagent — and
stage 4 cannot run unless stage 3 is running, whatever the technology tree says.
Nothing on this planet is thrown away; the dross, the fines and the tailings all
found homes, and so does this.

## 5. The ladder, and what each rung buys

| Stage | What is added | The reward |
|---|---|---|
| First watt | tap, turbine | 1.8 MW a turbine, no research |
| 1 | reaction plant, generator | 10 MW a generator |
| 2 | centrifuge | +50% fuel per solution *and* per gas |
| 3 | three recipes, a return belt | ~40% of the solution back |
| 4 | reactor | 40 MW, and a neighbour bonus |

Each rung improves a different part of the loop — the front, the back, then the
burner — rather than being a larger version of the last.

## 6. Where it sits in the tree

**Radiant power is tier 0**, a trigger technology carrying the reaction plant, the
fuel recipe and the radiant generator together. All three land at once because a
burner unlocked without its fuel is a recipe in the menu that cannot run.

Stages 2 to 4 are geodynamic technologies: **Solution enrichment**, **Cell
reprocessing**, **Radiant reactors**. Stage 1 at 10 MW a generator carries the
whole bootstrap comfortably, so the climb belongs after the science pack rather
than before it.

## 7. Not decided

- **Every quantity above is a first guess** — calculated against the engine,
  never played. The ratios that matter most are stage 2's +50% and stage 3's 40%
  recovery, because together they set whether the crust vents or the pool is the
  binding constraint.
- **Three new fluids for stage 3** (enriched, spent, stripped) is the heaviest
  cost in this document. Collapsing the chain to two steps would halve it, at the
  price of the multistage character stage 3 exists for.
- **`neighbour_bonus` with a custom fuel category** is assumed, not known. Stage
  4's whole reward rests on it. Data-stage spike.
- **Art.** Three new buildings — reaction plant, isotope centrifuge, radiant
  reactor. The radiant generator's plates already exist, and the crust tap and
  turbine keep theirs.
