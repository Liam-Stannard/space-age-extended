# Vulcanus ↔ Fulgora: Cross-Planet Industrial Integration

## Design Intent

This proposal extends the existing Factorio: Space Age mechanics by creating a deeper relationship between **Vulcanus** and **Fulgora**. It is the first tree built to the pattern set out in [the overall mod design framework](framework.md) — see that document for the design philosophy, the cross-planet tree template, and the evaluation checklist this tree is held to.

### The shipping principle, applied to this tree

Per framework §2.1, shipping is only ever justified when a single recipe requires two inputs that exist exclusively on different planets. Every cross-planet leg in this design is anchored on that rule:

| Leg | Anchor |
|---|---|
| Vulcanus → Fulgora: **Calcite** | Scrap Remelting needs Scrap (Fulgora-only) + Calcite (Vulcanus-only) |
| Fulgora → Vulcanus: **Catalyst Rod** | Magmatic Core needs Lava (Vulcanus-only, unshippable bulk fluid) + Catalyst Rod (Fulgora chain) |
| Vulcanus → Fulgora: **Depleted Catalyst Rod** | Reprocessing runs where the Holmium chain is |

The core concept is a two-way industrial relationship:

> **Fulgora recovers and refines its own waste stream using imported Vulcanus reagents; Fulgora's refined catalyst then unlocks a Vulcanus-only lava process. Each planet produces one half of a shared capstone.**

---

# 1. Scrap Remelting

## Concept

Fulgora's Scrap is currently primarily processed through the Recycler into a variety of useful manufactured components.

A second option would be introduced:

> **Remelt Scrap into a bulk molten material stream.**

This gives the player a meaningful choice between recovering manufactured components and recovering bulk metals.

### Location

**Fulgora** — Scrap is a Fulgora-exclusive material and is far too bulky to ship.

### Building

**Foundry**

The Foundry is already the appropriate building because it is the game's existing high-throughput molten-metal processing building. It is built on Fulgora for this purpose.

### Recipe: Scrap Remelting

**Inputs**

- Scrap
- Calcite *(imported from Vulcanus — this is the load-bearing cross-planet dependency)*
- Heat

**Output**

- Molten Scrap

### Design considerations

Molten Scrap should be a **fluid**.

This allows the existing Factorio fluid system to handle:

- Pipes
- Pumps
- Storage tanks
- Fluid wagons

Molten Scrap never needs to leave Fulgora, so space-platform fluid logistics is not a requirement of this design.

The recipe should be high-throughput, reflecting the Foundry's role as an industrial remelting facility.

The goal is not to make Scrap universally more valuable. Instead, it introduces a second strategic use for Scrap.

### Why Calcite matters

Calcite does not exist on Fulgora under any circumstances. Because Scrap Remelting requires it, a player who wants the entire refining chain must maintain a Vulcanus → Fulgora Calcite supply line. This is what stops the chain collapsing into a purely local Fulgora process.

### Player choice

The Fulgora player can choose:

**Recycler route**

> Scrap → Recycler → manufactured components

or:

**Remelting route**

> Scrap → Foundry → Molten Scrap → bulk metal recovery

This is an important part of the design: the two routes should have different purposes rather than one simply replacing the other.

---

# 2. Ferrous / Non-Ferrous Separation

## Concept

Molten Scrap is intentionally a mixed and impure material.

The next stage is to separate it into broad metallic classes.

### Location

**Fulgora**

### Building

**Electromagnetic Plant**

The Electromagnetic Plant is appropriate because the new process uses electromagnetic technology to manipulate and separate molten material.

### Recipe: Separate Molten Scrap

**Input**

- Molten Scrap
- Electricity

**Outputs**

- Molten Ferrous Metal
- Molten Non-Ferrous Metal

Both outputs are fluids.

### Process

```text
Molten Scrap
     |
     v
Electromagnetic Separation
     |
 +---+---+
 |       |
 v       v
Ferrous  Non-Ferrous
```

The separation stage deliberately does not immediately produce individual metals.

This gives the system an intermediate stage and makes the process feel like a genuine industrial refining chain.

---

# 3. Ferrous Refinement

## Concept

The ferrous stream is processed back into the Foundry's existing molten iron production chain.

### Location

**Fulgora**

### Building

**Foundry**

### Recipe: Ferrous Refinement

**Input**

- Molten Ferrous Metal
- Heat

**Output**

- Molten Iron

**Ferrous Refinement does not require Calcite.** Calcite is already the gate on Scrap Remelting; taxing a second step with the same imported resource would over-concentrate friction on one material.

### The deliberate iron surplus — the Fulgorian twist

The Scrap Remelting → separation ratios are **deliberately asymmetric**: the chain produces considerably more Molten Iron than the chain itself consumes downstream.

Copper Foil (Section 6) takes only a small amount of Molten Iron, and Catalyst Rod (Section 8) takes only a small amount of Iron Plate. The rest is genuine surplus stranded on Fulgora with no natural local consumer.

This is intentional and thematically correct. Fulgora's identity is being handed a chaotic input you did not ask for — Scrap's composition is junk, not a curated resource — and the refining chain inherits that character.

**The player chooses how to deal with it. No new mechanic is required:**

- Cast it into **Iron Plate** via the Foundry's existing casting recipe and feed conventional production.
- Cast it into any solid and run it through the **Recycler** if genuinely unwanted — so even the overflow stays inside Fulgora's existing economy rather than becoming pure waste.
- Build out storage and accept it as a buffered byproduct.

This answers Section 14's "should the output ratio reflect Scrap's actual composition" question: **yes, deliberately, in surplus.**

### Design goal

The player should have two viable sources:

```text
Iron Ore → Foundry → Molten Iron
```

and

```text
Scrap
  ↓
Molten Scrap
  ↓
Molten Ferrous
  ↓
Molten Iron
```

The Scrap route should be useful for recovering material from Fulgora's enormous waste stream without making conventional Vulcanus iron production obsolete.

---

# 4. Non-Ferrous Separation

## Concept

The non-ferrous stream contains the materials that are particularly interesting for the Fulgora/Vulcanus interaction.

The primary useful outputs are:

- Molten Copper
- A Holmium-rich residue

### Location

**Fulgora**

### Building

**Electromagnetic Plant**

### Recipe: Non-Ferrous Separation

**Input**

- Molten Non-Ferrous Metal
- Electricity

**Outputs**

- Molten Copper
- Holmium-rich Residue

The Holmium component should be relatively small.

The purpose is to create a **secondary recovery route**, not to replace Fulgora's existing Holmium production.

---

# 5. Holmium Extraction

## Concept

Rather than producing Holmium directly from the non-ferrous stream, Holmium is concentrated into a residue and then extracted in a separate stage.

This creates a more believable and interesting refining chain.

### Location

**Fulgora**

### Building

**Electromagnetic Plant**

### Recipe: Holmium Extraction

**Inputs**

- Holmium-rich Residue
- Electricity

**Output**

- Holmium Ore

**Holmium Extraction does not require Sulfuric Acid.** Sulfuric Acid is a Vulcanus-native resource with no Fulgora source, and this process runs on Fulgora — requiring it would add a second import with no design payoff. The Sulfuric Acid recovered at the capstone stage (Section 8) instead feeds the Processing Unit recipes, which consume it in vanilla.

### Process

```text
Molten Non-Ferrous
        |
        v
Non-Ferrous Separation
     |          |
     v          v
Molten Copper  Holmium-rich Residue
                    |
                    v
             Holmium Extraction
                    |
                    v
                Holmium Ore
```

The Holmium yield should be deliberately low enough that this acts as supplementary recovery rather than making existing Fulgora Holmium production redundant. **Holmium is not a selling point of this chain** — it is a trickle recovered as a side effect of doing the chain for other reasons.

### Variant recipe: Depleted Catalyst Rod reprocessing

Unlocked at Technology 5 (Section 13), not here, because Depleted Catalyst Rods do not exist until then.

**Inputs**

- Depleted Catalyst Rod
- Electricity

**Output**

- Holmium Ore *(reduced yield)*

This closes the Catalyst Rod loop — spent rods return from Vulcanus and re-enter the Holmium stream rather than becoming dead-end waste.

---

# 6. Copper Foil

The Electromagnetic Plant's electronics recipes are fed by a copper form cast directly from molten material.

The key idea is:

> **Use the Foundry to manufacture a copper form specifically suited to electromagnetic electronics production.**

## Recipe: Copper Foil

### Location

**Fulgora** — both inputs are produced locally by the separation chain, so there is no reason to ship anything for this step.

### Building

**Foundry**

### Inputs

- Molten Copper
- Molten Iron *(small amount)*
- Heat

### Output

- Copper Foil

### Why the Molten Iron input

Copper Foil is not a free "skip a step" gain — it has its own material cost. The small Molten Iron requirement:

- prevents the chain being strictly superior to conventional copper processing
- ties the **Ferrous** half of the Section 2 split into the same downstream product as the Non-Ferrous half, so both outputs of the original separation feed one coherent chain rather than dangling separately
- gives the iron surplus a genuine, if partial, local consumer

The ratio should stay heavily skewed toward copper — this is "copper with a little iron for structure", not a 50/50 alloy.

### Production chain

```text
Molten Copper   Molten Iron (small)
      |               |
      +-------+-------+
              |
              v
           Foundry
              |
              v
         Copper Foil
              |
              v
    Electromagnetic Plant
```

The important design feature is that Copper Foil avoids an unnecessary:

> Molten Copper → Copper Plate → Copper Foil

chain.

The Foundry directly creates the specialised copper form. **This is the chain's actual selling point:** a player using it removes an entire assembler tier — no dedicated Copper Cable assemblers feeding circuits — replacing it with direct Foundry output. Fewer buildings, fewer belts, one less bottleneck to balance.

---

# 7. Electromagnetic Circuit Recipes

## Concept

The Electromagnetic Plant gains **alternative recipes** for existing electronic products.

This does **not** introduce new circuit item tiers.

Existing products remain unchanged:

- Electronic Circuit
- Advanced Circuit
- Processing Unit

### Alt-recipe mechanics

These are alternative recipes in the vanilla Space Age sense — unlocked alongside the base recipe and toggled per-machine via the recipe selector, exactly like Fulgora's existing Scrap-based electronics alt recipes. **No separate recipe-unlock technology is required**; the technologies in Section 13 unlock the alt recipes alongside their other content.

Because the player toggles rather than runs both simultaneously in one building, each alt recipe only needs to be better *when the player has committed to a Copper Foil supply chain* — not universally competitive.

### Substitution rule

**Copper Foil substitutes only for the copper content of each vanilla recipe.** Non-copper, non-iron inputs (Plastic, Sulfuric Acid) stay identical to vanilla, keeping balancing to a single tunable variable: Copper Foil's copper-equivalent value. Electronic Circuit's Iron Plate input is the one exception — see §7.1 — substituted for Molten Iron at vanilla's own casting-iron ratio, since the Electromagnetic Plant already sits downstream of this mod's own molten-iron chain and skipping the cast is a value-neutral efficiency, not a balance change.

### Vanilla baselines

| Recipe | Time | Vanilla inputs | Copper content |
|---|---|---|---|
| Electronic Circuit | 0.5s | 3 Copper Cable + 1 Iron Plate | 3 Copper Cable |
| Advanced Circuit | 6s | 4 Copper Cable + 2 Electronic Circuit + 2 Plastic Bar | 4 Copper Cable |
| Processing Unit | 10s | 20 Electronic Circuit + 2 Advanced Circuit + 5 Sulfuric Acid | none direct — 80 Copper Cable embedded |

---

## 7.1 Electromagnetic Electronic Circuit

### Building

**Electromagnetic Plant**

### Inputs

- Copper Foil *(replaces 3 Copper Cable)*
- Molten Iron ×10 *(replaces 1 Iron Plate, at vanilla's own casting-iron ratio — skips the cast entirely rather than requiring the player to cast Molten Iron to Iron Plate and back)*

### Output

- Electronic Circuit

Value-neutral substitution against the vanilla recipe on both inputs now — copper by Copper Foil, iron by the same ratio vanilla's own casting-iron recipe already uses.

---

## 7.2 Electromagnetic Advanced Circuit

### Building

**Electromagnetic Plant**

### Inputs

- Copper Foil *(replaces 4 Copper Cable)*
- Electronic Circuit ×2 *(unchanged)*
- Plastic Bar ×2 *(unchanged)*

### Output

- Advanced Circuit

Clean 1:1 substitution against the vanilla recipe.

---

## 7.3 Electromagnetic Processing Unit

### Building

**Electromagnetic Plant**

### Inputs

- Copper Foil *(replaces the copper embedded in a portion of the Electronic Circuit input)*
- Electronic Circuit *(reduced count)*
- Advanced Circuit ×2 *(unchanged)*
- Sulfuric Acid ×5 *(unchanged)*

### Output

- Processing Unit

### Balancing note

Processing Unit has **no direct copper input** in vanilla — its 80 Copper Cable-equivalent is embedded inside its 20 Electronic Circuits. Substituting Copper Foil for some of those circuits therefore also removes the **1 Iron Plate each circuit carries**, so this recipe implicitly discounts iron as well as copper.

This is accepted deliberately: the substitution is a copper-cost-intermediate replacement rather than a strict copper-for-copper trade. It must be priced with that iron discount in mind rather than tuned as though only copper changed.

---

# 8. Capstone: Resonant Electromagnetics

The chain terminates in a genuinely new top-tier item, produced by a mechanic that does not exist elsewhere in Space Age: a **consumable catalyst**.

## 8.1 Catalyst Rod

### Location

**Fulgora**

### Building

**Electromagnetic Plant**

### Inputs

- Holmium Ore
- Copper Foil
- Iron Plate *(from the deliberate iron surplus — its premium use)*

### Output

- Catalyst Rod

The Catalyst Rod draws on all three final materials of the earlier chain in a single item, and is the only recipe that gives the surplus iron a high-value destination.

## 8.2 Resonant Circuit

### Location

**Fulgora**

### Building

**Electromagnetic Plant**

### Inputs

- Processing Unit
- Copper Foil
- Catalyst Rod ×1 *(consumed)*

### Outputs

- **Resonant Circuit**
- Depleted Catalyst Rod
- Contaminated Sulfuric Acid

### The catalyst mechanic

The Catalyst Rod is **one-time use**: consumed 1:1 per craft, returning a Depleted Catalyst Rod plus a contaminated byproduct. This is a normal Factorio recipe shape — no engine feature is being assumed. Factorio has no native "installed item that wears down with use"; this achieves the same feel using standard multi-output recipes.

Two byproducts means the capstone recipe hands the player a mess to deal with — the third time this chain does so (chaotic Scrap composition, surplus Molten Iron, now spent rods and dirty acid). This is the design's consistent Fulgoran voice, not three unrelated decisions.

Resonant Circuit consumes Processing Unit as an ingredient rather than sitting parallel to it, making it a literal tier above Technology 4's output — the first recipe in the tree that builds *on top of* an earlier tree recipe instead of alongside it.

Resonant Circuit itself is catalyst-free, stable, and freely shippable — a clean standalone component.

## 8.3 Purify Contaminated Sulfuric Acid

### Building

**Chemical Plant**

### Inputs

- Contaminated Sulfuric Acid
- Calcite *(mirrors vanilla Acid Neutralisation, which the player already knows)*

### Outputs

- Sulfuric Acid *(feeds the Processing Unit recipes of Section 7)*
- Steam *(feeds turbines / power)*

This reuses a fluid the chain already consumes rather than inventing a new waste material, and deliberately echoes vanilla's existing acid → steam conversion so it reads as a variant of a known system.

## 8.4 Magmatic Core

The Vulcanus half of the capstone.

### Location

**Vulcanus — necessarily.** Lava is an unlimited, unshippable bulk fluid that exists nowhere else. This is the only kind of anchor that survives universally-buildable machines.

### Building

**Foundry**

### Inputs

- Lava *(bulk)*
- Tungsten Ore or Tungsten Plate
- Catalyst Rod *(shipped from Fulgora)*

### Outputs

- **Magmatic Core**
- Depleted Catalyst Rod *(ships back to Fulgora for reprocessing — Section 5)*

### Why this works

- **Lava** forces the recipe onto Vulcanus; no amount of building portability circumvents it.
- **Catalyst Rod** forces the Fulgora dependency; it requires Holmium, Copper Foil and Iron Plate, all products of the Fulgora chain.
- **Depleted Rod return** makes traffic genuinely round-trip rather than two unrelated one-way flows.
- The catalyst mechanic is reused rather than being a single-recipe curiosity.

## 8.5 Thermionic Assembly — the capstone item

**Resonant Circuit + Magmatic Core → Thermionic Assembly**

Craftable **anywhere**. Both inputs are already location-locked by their own production, so the player has necessarily engaged with both planets to reach this point; making final assembly portable is a reward rather than a loophole.

The name reflects its composition: thermionic emission is heat-driven electron flow, which is precisely the fusion of the Magmatic Core (thermal, Vulcanus) and the Resonant Circuit (electromagnetic, Fulgora).

### Forward compatibility

Each future cross-planet tree is intended to terminate in its own capstone, with a later mega-technology consuming one of each. The Thermionic Assembly is therefore designed as a **clean, self-contained, shippable end product**: with no fragile or planet-locked properties.

Within this tree it has exactly one use — Technology 6's Thermionic Generator (Section 9).

---

# 9. Technology 6: The Thermionic Generator

## Design premise: every cross-planet tree improves space platforms

Space platforms are the one context every planet pair shares, and they are the part of Space Age least served by planetary technology trees. The intended pattern for this mod is therefore:

> **Each cross-planet technology tree terminates in a technology that improves space platforms in a different way — and the accumulated platform capabilities become the mod's endgame goal.**

To keep the trees from competing, each should improve a **different platform subsystem**. The available carve-up is roughly: power, thrust, asteroid processing, cargo/logistics, defence, structure.

**Vulcanus/Fulgora takes power.** Fulgora is the game's power-identity planet and Vulcanus supplies the thermal half, so the pairing is natural.

The eventual endgame should require several trees' platform capabilities simultaneously — for example a platform that can only survive conditions or reach a destination that breaks a conventionally-equipped one. That design is deferred until more trees exist.

## 9.1 The gap this fills

Platform power currently has three options, and a hole between them:

| | Solar | Nuclear | Fusion |
|---|---|---|---|
| Fuel source | none | Nauvis (uranium) | **Aquilo only** — fusion cells need ammonia, which cannot be barreled |
| Unlocked | early | mid | very late (Aquilo) |
| Platform weakness | fails on outer routes (0.42 kW/panel at Aquilo) | bulky; fuel cells burn while platforms idle awaiting request conditions | none — but you must already have reached Aquilo |

The hole is the stretch between **"solar stops working"** and **"you have reached Aquilo."** Today that gap is bridged only by nuclear, which players actively dislike on platforms, and solar-only platforms routinely strand themselves in Aquilo orbit.

**The Thermionic Generator fills exactly that gap.** It arrives before Aquilo and solves the problem that currently blocks players from reaching it.

It should **not** compete with fusion on density — fusion remains the endgame king. Its advantages are availability, no idle waste, and no water requirement; its cost is a lower peak output and an active cooling requirement.

## 9.2 Thermionic Generator

### Location

**Space platforms.**

### Crafted from

- Thermionic Assembly

### Operating inputs — two independent streams

- **Magmatic Core** — fuel, shipped up from Vulcanus. Determines power output.
- **Ice** — coolant, gathered locally from oxide asteroids. Determines how much of that output survives the efficiency curve.

These are **not** combined into a fuel item. They are consumed separately by the running generator, which is what makes the thermal mechanic tunable: the player controls fuel rate and cooling rate independently.

### Output

**Electricity (primary) plus rejected heat via a real heat-pipe interface (secondary — a cooling avenue, not an independent power source).** Earlier drafts of this design excluded any heat-pipe interface, reasoning that a generator emitting heat could be shipped to Aquilo and trivialize that planet's defining challenge. That concern doesn't hold: the Thermionic Generator can only ever be built on a space platform (surface-gated via `surface_conditions`), and Factorio's heat-pipe network is strictly surface-local — a platform's heat pipes can never connect into a planet's own heat network, including while in Aquilo's orbit. The heat-pipe interface is therefore exposed as an additional, optional cooling avenue alongside Ice: connecting real heat pipes lets a thermal bus pull heat away, and because heat conduction scales with temperature difference, a hotter/less-efficient generator drains faster automatically — this falls directly out of real heat-network physics, not a separate hand-authored mechanic. This does not change the generator's electricity-only *power* output; heat exposure draws down the same internal temperature the efficiency curve already tracks, it isn't a second, independent power channel.

## 9.3 The thermal mechanic

Nothing in vanilla has a temperature-dependent efficiency curve for a generator. Nuclear has heat but as a fixed system; fusion has none.

**Behaviour:**

1. The generator **self-heats** as it produces power.
2. **Ice consumption removes heat**, and so does a connected heat-pipe network if the player builds one (§9.2) — the two cooling avenues are independent and stack; a real heat-pipe network draws harder the hotter the generator runs, since heat conduction scales with temperature difference, which is real Factorio heat-network physics rather than a second hand-authored curve.
3. As temperature rises above the optimal band, efficiency **declines gradually**.
4. Past an **overheat threshold**, output drops **sharply** — the machine keeps running but is barely worth its footprint until it cools.
5. Equilibrium temperature is a function of load versus total cooling throughput (ice plus whatever a connected heat-pipe network draws).

### Why this shape

- **Gradual decline is a warning the player can act on.** The cliff punishes ignoring it.
- **Degradation, not destruction.** A platform that stops catching oxide asteroids limps rather than dies — it can still make port, and a heat-pipe network gives it a second, genuine cooling channel that measurably slows the slide toward overheat and can meaningfully extend how long it holds strong output. That channel alone doesn't reach a stable equilibrium or "recover" the generator the way a properly-supplied Ice setup does (§9.4) — it's a real delay, not a substitute — but more/better-distributed pipes still help, and it's never nothing.
- **Cooling throughput becomes the scaling decision**, not generator count. Run lean and accept lower steady-state output, or oversize the ice supply (and/or the heat-pipe network) to hold peak efficiency.
- **Viability scales with asteroid capture**, which is already the core platform gameplay loop.

### Why Magmatic Core as the ongoing fuel

This makes the Vulcanus leg **permanently load-bearing**. Magmatic Core stops being a one-time capstone ingredient and becomes a consumable, so any player running Thermionic Generators must keep the Catalyst Rod → Vulcanus → Magmatic Core → Depleted Rod loop running indefinitely rather than dismantling it after crafting the capstone once.

## 9.4 Open questions for this technology

- Optimal temperature band, overheat threshold, and the steepness of the gradient.
- Ice consumed per unit of heat removed.
- Peak MW output — must sit meaningfully below fusion's 50–125 MW per generator.
- Magmatic Core burn rate versus realistic Vulcanus export capacity.
- Footprint versus an equivalent nuclear setup (should be smaller, or the earlier availability is its only advantage).
- Whether an orbital production step should be added later. Currently the platform imports Magmatic Cores and catches ice with no manufacturing step of its own; the location constraint is already real, since Magmatic Core can only be made on Vulcanus.
- The heat-interface's `heat_buffer` numbers (`max_temperature` 2000, `specific_heat` 3MJ, `max_transfer` 10MW) are provisional placeholders, same tone as everything else in this list — chosen to be a meaningful heat sink a player has to actually build infrastructure for, not a trivial instant dump that would make Ice pointless, but not tuned against any real target throughput. `specific_heat` was raised from an initial 1MJ after a headless in-engine A/B test showed 1MJ let even a minimal handful of directly-touching heat pipes fully solve cooling and hold a fuel-only, zero-ice generator at full efficiency indefinitely — the opposite of the intended "heat pipes are a genuine but additional avenue, not a substitute for Ice" design. At 3MJ, a small/partial pipe hookup (touching only a few of the interface's twelve connection points) is only marginally helpful, and even a full hookup (all twelve points, still just directly-touching pipes, no distribution network) only delays overheat rather than preventing it, since nothing downstream of the interface actually dissipates the heat it receives — it only redistributes it, so any heat-pipe hookup is a finite buffer, never a permanent substitute for Ice's real per-interval removal. Independently measured (headless in-engine, fuel-only, zero ice): the maximum possible 12-point hookup holds full power for roughly ~50–55s before efficiency starts declining, then reaches MIN_EFFICIENCY (fully floored) by roughly ~100–105s total; with no heat pipes at all, the same fuel-only generator floors in roughly ~20–22s. These are approximate and illustrative, not exact guarantees — they will shift if `specific_heat`/`max_transfer` or the abstract curve's own constants are retuned later — but they're the actual measured numbers for the current constants, superseding this rebalance's own original estimate.
- The abstract-temperature-to-Celsius mapping used to drive that heat-interface (`scripts/thermionic-curve.lua`'s `abstract_temperature_to_heat_buffer_celsius`, currently a simple 1:1 clamp) is likewise provisional — it was picked so the existing curve's own landmarks (the 600 optimal-band edge, the 800 overheat threshold) read as plausible real degrees Celsius, not against any measured target.

**Note for future trees:** this generator is now a real source of usable rejected heat on any platform running it, in addition to electricity. Per `framework.md` §4.5 rule 5 ("never relieve two of the five shared resources at once"), any future platform capability that wants to consume heat as an input should treat this generator's waste heat as an existing baseline already present on Power-tree platforms, not a resource this generator is competing to provide — flagged here for whoever designs the Thrust/Structure/Asteroid/Defence trees.

---

# 10. Optional Holmium-Based Electronics Extension

**Deferred. Not part of Phase 1 or Phase 2.**

A possible late-stage extension is to give Holmium a secondary role in advanced electromagnetic manufacturing — for example an alternative Processing Unit recipe using Copper Foil, Advanced Circuit and Holmium Plate.

This is excluded for now because it adds a second Holmium sink before the first (plain Holmium Extraction) has been tested, and because Holmium's role in this design is deliberately a trickle.

It should not create a mandatory dependency:

> Scrap → Holmium → Copper Foil → Electronics

---

# 11. Complete Production Loop

```text
                              FULGORA
                                 |
                               Scrap
                                 |
                      +----------+----------+
                      |                     |
                      v                     v
                   Recycler            Foundry: Remelting <---- Calcite
                      |                     |                  (from VULCANUS)
              Existing outputs        Molten Scrap
                                            |
                                            v
                                  EM Plant: Separation
                                            |
                                   +--------+--------+
                                   |                 |
                                   v                 v
                            Molten Ferrous    Molten Non-Ferrous
                                   |                 |
                                   v            +----+----+
                            Molten Iron         |         |
                            (SURPLUS ->         v         v
                             cast / Recycler)  Molten   Holmium-
                                   |           Copper   rich Residue
                                   |             |          |
                                   |             |          v
                                   |             |   Holmium Extraction
                                   |             |          |
                                   +------+------+          v
                                          |            Holmium Ore
                                          v                 |
                                    Foundry: Copper Foil    |
                                          |                 |
                         +----------------+---------+       |
                         |                |         |       |
                         v                v         |       |
                  EM Plant circuits:                |       |
                  Electronic / Advanced /           |       |
                  Processing Unit                   |       |
                         |                          |       |
                         |     +--------------------+-------+
                         |     |
                         v     v
                    EM Plant: Catalyst Rod
                              |
                    +---------+----------+
                    |                    |
                    v                    v
          EM Plant: Resonant      Space Logistics
             Circuit                     |
           (+ Depleted Rod               v
            + Contaminated            VULCANUS
              Acid)                      |
                    |                    v
                    |          Foundry: Magmatic Core <---- Lava + Tungsten
                    |                    |
                    |          +---------+---------+
                    |          |                   |
                    |          v                   v
                    |    Magmatic Core      Depleted Catalyst Rod
                    |          |                   |
                    |          |            Space Logistics
                    |          |                   |
                    |          |                   v
                    |          |             FULGORA: reprocess
                    |          |             -> Holmium Ore
                    |          |
                    +----+-----+
                         |
                         v
              THERMIONIC ASSEMBLY
                (craftable anywhere)
                         |
                         v
              THERMIONIC GENERATOR
                         |
                         v
                 SPACE PLATFORM
                    /         \
                   /           \
        Magmatic Core          Ice
        (shipped fuel)    (local coolant)
                   \           /
                    \         /
                  Electricity, on a
                temperature-dependent
                   efficiency curve
```

This creates a genuine cross-planet loop:

> **Vulcanus's Calcite unlocks Fulgora's waste refining; Fulgora's Catalyst Rod unlocks Vulcanus's lava metallurgy; each planet produces one half of a shared capstone; and the capstone powers space platforms using ongoing supply from both.**

---

# 12. Why This Fits Space Age

## Existing buildings remain relevant

No new production buildings are required.

### Foundry

Already handles molten metal, high-throughput metallurgy, and direct molten-material production.

It gains:

- Scrap Remelting
- Ferrous Refinement
- Copper Foil
- Magmatic Core

### Electromagnetic Plant

Already represents Fulgora's advanced electromagnetic manufacturing.

It gains:

- Molten Scrap separation
- Non-Ferrous separation
- Holmium extraction (and Depleted Rod reprocessing)
- Electromagnetic circuit alt recipes
- Catalyst Rod
- Resonant Circuit

### Chemical Plant

Gains:

- Purify Contaminated Sulfuric Acid

### Recycler

Remains unchanged. Its role is still:

> Scrap → recover manufactured components.

The new system simply gives Scrap an additional route — and gives surplus cast iron a disposal path.

---

# 13. What This Proposal Avoids

### No Quality changes

Quality remains entirely within the existing Quality system and module progression. There are no quality-dependent recipes, no new quality mechanics, no new quality tiers, no changes to Quality Modules 1–3.

### No new machine tiers

There is no Foundry Mk II, Electromagnetic Plant Mk II, or Advanced Recycler.

### No generic productivity bonus

The system does not simply provide "+15% productivity when using Vulcanus materials." The player gets new production decisions instead.

### No building-placement gimmicks

No recipe is gated on being built on a particular planet. Every location constraint in this design comes from **resource locality** — Scrap, Calcite, Lava — which cannot be circumvented by building elsewhere.

### No unnecessary new resources

New material concepts, all functional:

- Molten Scrap
- Molten Ferrous Metal
- Molten Non-Ferrous Metal
- Holmium-rich Residue
- Copper Foil *(no longer a balancing question mark — it carries the chain's core selling point)*
- Catalyst Rod / Depleted Catalyst Rod
- Contaminated Sulfuric Acid
- Resonant Circuit
- Magmatic Core
- Thermionic Assembly

### One new building, with a justification

The **Thermionic Generator** is the design's only new building. It is not a tier of anything — it is a power source with a mechanic (temperature-dependent efficiency) that no existing building has, filling a documented gap in platform power between solar and Aquilo-locked fusion. See Section 9.

---

# 14. Technology Progression

## Technology 1 — Metallurgical Recovery

**Requires:** Metallurgic Science, Electromagnetic Science

**Unlocks:**

- Scrap Remelting
- Molten Scrap
- Ferrous / Non-Ferrous separation
- Ferrous Refinement

*Molten Iron output deliberately exceeds downstream demand; surplus is handled via existing Foundry casting and the Recycler. No new recipe required.*

---

## Technology 2 — Advanced Material Recovery

**Requires:** Technology 1, plus additional progression in both planetary science trees

**Unlocks:**

- Non-Ferrous Separation
- Holmium Extraction *(no Sulfuric Acid input)*
- Improved separation processes

---

## Technology 3 — Electromagnetic Metallurgy

**Requires:** Technology 1 **and** Technology 2 *(explicit — Copper Foil needs both Ferrous and Non-Ferrous output)*

**Unlocks:**

- Copper Foil
- Electromagnetic Electronic Circuit *(alt recipe)*
- Electromagnetic Advanced Circuit *(alt recipe)*

---

## Technology 4 — Integrated Electronics

**Requires:** Technology 3

**Unlocks:**

- Electromagnetic Processing Unit *(alt recipe)*

---

## Technology 5 — Resonant Electromagnetics *(capstone)*

**Requires:** Technology 3 **and** Technology 4

**Unlocks:**

- Catalyst Rod
- Resonant Circuit
- Magmatic Core
- Depleted Catalyst Rod reprocessing
- Purify Contaminated Sulfuric Acid
- **Thermionic Assembly** *(the capstone item)*

---

## Technology 6 — Thermionic Power *(platform capability)*

**Requires:** Technology 5

**Unlocks:**

- **Thermionic Generator** — space platform building, crafted from Thermionic Assembly

This is the tree's platform contribution under the pattern described in Section 9: every cross-planet tree ends in a technology that improves a different platform subsystem. This tree takes **power**.

Magmatic Core becomes an ongoing consumable at this point rather than a one-time ingredient, keeping the Vulcanus leg of the loop permanently active.

---

# 15. Core Design Principles

## 14.1 Optional, not mandatory

The new chains should be attractive without making existing factories invalid. A player should still be able to operate a conventional Vulcanus metal factory, a conventional Fulgora recycling factory, and a conventional electronics factory without the cross-planet system.

## 14.2 Each planet contributes something unique

**Fulgora contributes:** Scrap, recycling, electromagnetic technology, Holmium, the Catalyst Rod.

**Vulcanus contributes:** Calcite, Lava, Tungsten, high-volume thermal metallurgy.

Neither planet is merely a supplier of generic resources — and neither can substitute for the other by relocating buildings.

## 14.3 The chain should create factory-design problems

- "Is this Scrap more valuable as manufactured components or as bulk molten metal?"
- "How much Calcite import capacity do I need to sustain remelting?"
- "What do I actually do with all this surplus iron?"
- "Should my electronics run the conventional chain or the Copper Foil chain?"
- "How many Catalyst Rods per rocket, and can I keep the Depleted Rod return flowing?"

## 14.4 Byproducts are the player's problem

Three times over — chaotic Scrap composition, surplus Molten Iron, spent rods and contaminated acid — this design hands the player something they did not ask for and does not prescribe the answer. Existing buildings always provide at least two valid outlets.

---

# 16. Open Balancing Questions

### Resolved

- ~~Should Copper Foil require a secondary ingredient?~~ **Yes — a small amount of Molten Iron.**
- ~~Should the output ratio reflect Scrap's actual composition?~~ **Yes — deliberately asymmetric, iron in surplus.**
- ~~Should Ferrous Refinement require Calcite?~~ **No.**
- ~~Should Holmium Extraction require Sulfuric Acid?~~ **No.**
- ~~How much Holmium should be recovered?~~ **A deliberate trickle; supplementary only.**
- ~~Are the circuit recipes alternatives or parallel options?~~ **Alt recipes, toggled per-machine, no separate unlock tech.**

### Still open

**Scrap Remelting**

- How much Scrap produces one unit of Molten Scrap?
- How much Calcite is consumed? (This sets the whole chain's import burden.)
- Is the process more or less material-efficient than recycling?
- Should remelting produce any waste?

**Ferrous / Non-Ferrous separation**

- Should the split be deterministic?
- Should there be a small waste stream?
- Exactly how large should the iron surplus be? Large enough to be a real problem, small enough not to be crippling.

**Copper Foil**

- Copper-equivalent value (the single tunable for all three circuit alt recipes).
- Molten Iron ratio — must stay heavily copper-skewed.
- Should the Foundry's existing productivity apply normally?

**Circuit recipes**

Compare against vanilla on raw resource consumption, machine count, power consumption, intermediate item count, throughput, and space. The integrated chain should be **strong in the right circumstances**, not universally optimal.

**Capstone**

- Catalyst Rod cost vs. how many crafts it should feel worth.
- Magmatic Core lava/tungsten volumes.
- Contaminated Sulfuric Acid volume vs. Processing Unit demand — should purification roughly close the loop, or run at a deficit?

**Thermionic Generator**

See Section 9.4 for the full list — temperature band, overheat threshold, gradient steepness, ice per unit heat, peak MW versus fusion, footprint, and whether an orbital production step is added later.

---

# 17. Recommended Implementation Phasing

### Phase 1 — refining chain

1. Scrap Remelting *(with Calcite import)*
2. Molten Scrap → Ferrous / Non-Ferrous
3. Ferrous → Molten Iron *(with deliberate surplus)*
4. Non-Ferrous → Molten Copper + Holmium-rich Residue
5. Holmium-rich Residue → Holmium Ore
6. Molten Copper + Molten Iron → Copper Foil

### Phase 2 — electronics

7. Electromagnetic Electronic Circuit
8. Electromagnetic Advanced Circuit
9. Electromagnetic Processing Unit

### Phase 3 — capstone

10. Catalyst Rod
11. Resonant Circuit *(+ Depleted Rod, + Contaminated Acid)*
12. Purify Contaminated Sulfuric Acid
13. Magmatic Core *(Vulcanus)*
14. Depleted Catalyst Rod reprocessing
15. Thermionic Assembly

### Phase 4 — platform power

16. Thermionic Generator
17. Temperature/efficiency mechanic and ice cooling
18. Magmatic Core export logistics at sustained consumption rates

Test after each phase whether the resulting production loops actually create interesting factory layouts. If they do, further expansion should focus on **deepening these interactions**, not adding more resources or more buildings.

---

# Summary

The strongest version of the Vulcanus/Fulgora relationship is not a new machine or a flat efficiency bonus.

It is a **closed industrial loop** built from existing systems, in which every cross-planet shipment is forced by resource locality rather than by artificial building restrictions:

> **Calcite → Scrap Remelting → Separation → Copper Foil → Circuits → Catalyst Rod → (ship) → Lava + Tungsten → Magmatic Core → (ship back) → Thermionic Assembly → Thermionic Generator**

Fulgora provides recycling, electromagnetic processing, and the catalyst.

Vulcanus provides the reagent, the lava, and the thermal metallurgy.

Each planet produces one half of a shared capstone, and neither half can be made without the other. The player is rewarded for connecting the two without being forced to do so.

The tree then terminates in a **space platform capability** — the pattern intended for every cross-planet tree in this mod, with the accumulated platform improvements forming the eventual endgame. This tree claims **power**, filling the real gap between failing solar and Aquilo-locked fusion, and in doing so converts the Vulcanus leg from a one-time crafting requirement into a permanent supply line.
