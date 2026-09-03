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

Within this tree it has exactly one use — Technology 6's Quench Turbine (Section 9).

---

# 9. Technology 6: The Quench Turbine

## Design premise: every cross-planet tree improves space platforms

Space platforms are the one context every planet pair shares, and they are the part of Space Age least served by planetary technology trees. The intended pattern for this mod is therefore:

> **Each cross-planet technology tree terminates in a technology that improves space platforms in a different way — and the accumulated platform capabilities become the mod's endgame goal.**

To keep the trees from competing, each should improve a **different platform subsystem**. The available carve-up is roughly: power, thrust, asteroid processing, cargo/logistics, defence, structure.

**Vulcanus/Fulgora takes power.** Fulgora is the game's power-identity planet and Vulcanus supplies the thermal half, so the pairing is natural.

## 9.1 The gap this fills

Platform power currently has three options, and a hole between them:

| | Solar | Nuclear | Fusion |
|---|---|---|---|
| Fuel source | none | Nauvis (uranium) | **Aquilo only** — fusion cells need ammonia, which cannot be barreled |
| Unlocked | early | mid | very late (Aquilo) |
| Platform weakness | fails on outer routes (0.42 kW/panel at Aquilo) | bulky; fuel cells burn while platforms idle awaiting request conditions | none — but you must already have reached Aquilo |

The hole is the stretch between **"solar stops working"** and **"you have reached Aquilo."**

The Quench Turbine spans that gap, but deliberately **does not close it cheaply**. Before Aquilo the only quench recipe available is the lean one, which throws most of each Magmatic Core away; a platform can be powered, but only by running the Vulcanus/Fulgora line hard enough to hurt. Reaching Aquilo unlocks the recipe that makes the same core worth nearly seven times as much. Power is therefore something the player *improves* across the mid-game rather than solves once.

Its standing advantage over nuclear is that it genuinely does not idle: a `generator` draws fluid only when the grid asks for it, and the quench recipe stalls when its output backs up, so a platform parked at a waypoint consumes no cores at all. That is measured, not asserted (§9.5).

## 9.2 The Quench Turbine

### Location

**Space platforms**, gated by a real surface property (`pressure = 0`) exactly as vanilla gates its own thruster — not by a planet-name rule (framework.md §2.3).

### Crafted from

Two Thermionic Assemblies.

### Operating input

**Quench Vapour**, made on the platform by a quench recipe on an ordinary chemical plant. The turbine itself is a plain `generator`: the engine computes its output from flow, the fluid's heat capacity and its temperature, and **clips anything above `maximum_temperature`**.

### Why Magmatic Core stopped being a fuel

Because a fuel item has exactly one value. An *ingredient* can be worth different amounts depending on the recipe that consumes it, and that is the entire mechanic — see §9.3. Magmatic Core therefore has no `fuel_value` and no fuel category at all, so nothing can burn it directly and bypass the ladder.

### What this replaced, and why

Earlier drafts made the generator a `reactor` with a scripted temperature/efficiency curve, a hidden power interface, a hidden coolant container and a custom GUI. That design could not survive vanilla's heat network. A reactor's heat buffer feeds *every* consumer attached to it, and heat exchangers plus steam turbines would have turned its waste heat into roughly as much electricity again, making the generator's own output irrelevant. The one native fix was to hold the whole network below the heat exchanger's 500-degree `min_working_temperature`, which works but leaves the temperature scale fighting the efficiency curve, and still needs a script to remove heat.

The Quench Turbine reaches the same goal — output per shipped core is a decision the player tunes — with no heat network, no hidden entities, and no runtime script at all. `control.lua` is now empty.

## 9.3 The mechanic: clipping, not a curve

A quench recipe fixes the temperature of the vapour it makes. The turbine cannot use vapour hotter than 315°C, so:

- a recipe that makes **a little very hot** vapour wastes most of the core, and
- a recipe that makes **a lot at exactly the cap** wastes nothing.

Efficiency per core is thus a property of the recipe the player can run, enforced by the engine's own generator arithmetic rather than by a hand-authored curve. The ladder:

| Tier | Technology | Per craft | Vapour | Electricity per core |
|---|---|---|---|---|
| 1 — Lean Quench | `sae-thermionic-power` | 1 Core + 10 Ice | 60 at 900°C | **90 MJ** (clipped) |
| 2 — Cryogenic Quench | `sae-cryogenic-quenching` | 1 Core + 40 Ice + 100 Fluoroketone-cold | 400 at 315°C | **600 MJ** |
| 3 — corridor tier | deferred | tier 2 plus a new asteroid-derived resource | — | designed with the endgame |

Both are 10-second crafts, so one chemical plant at speed 1 consumes 6 cores/min: **9 MW** of turbine feed on tier 1, **60 MW** on tier 2. One turbine converts **18 MW**.

Tier 2 is gated twice over: on vanilla's own `cryogenic-plant` technology, and on Fluoroketone, which only Aquilo can make.

### The Fluoroketone loop is closed, not consumed

The tier-2 recipe returns its Fluoroketone hot. A cryogenic plant cannot be built on a platform (it requires pressure ≥ 10), so **Radiative Fluoroketone Cooling** — a vacuum-only chemical-plant recipe — returns it to cold in space. Fluoroketone is therefore an *initial fill* shipped up in barrels, not an ongoing import; what Aquilo permanently supplies is the technology and that fill. Roughly ten radiating plants per quench plant is the footprint cost of tier-2 density.

**Note on how vacuum-only recipes behave.** Recipe `surface_conditions` are a player-facing selection filter: the recipe does not appear in a machine's recipe list on a surface that doesn't match. They are *not* a runtime crafting block — a recipe forced onto a wrong-surface machine by script or console will happily craft. This was verified against vanilla's own gravity-0 `space-science-pack`, which behaves identically on Nauvis when set by script. Nothing is wrong with the mod's recipe; this is simply what the mechanism is.

## 9.4 Why this shape

- **Degradation, not destruction.** Running the lean recipe is expensive, never fatal (framework.md §4.5 rule 3). There is no meltdown and no failure state, only a worse exchange rate.
- **Cooling throughput is still the scaling decision**, now expressed as Ice throughput per core rather than as a coolant tank. Viability still scales with asteroid capture, which is already the core platform loop.
- **The Vulcanus leg stays permanently load-bearing.** Magmatic Core is a consumable, so the Catalyst Rod → Vulcanus → Magmatic Core → Depleted Rod loop must keep running indefinitely.
- **There is a wrong platform to install it on** (rule 4): one with no oxide asteroids for Ice, or no room for the radiator field tier 2 needs.

Versus fusion, the honest comparison is no longer "meaningfully below 50 MW". One turbine is 18 MW and one tier-2 quench plant feeds three of them, so a quench installation is **denser than fusion per building and far larger per installation** once the chemical plants and radiators are counted — and unlike fusion it depends on a supply line that can be cut.

## 9.5 Verified against the engine

Measured on a headless server over RCON, not derived by hand:

| Check | Result |
|---|---|
| Turbine at the 315°C cap | 18.000 MW |
| Vapour at 900°C | 18.000 MW — clipped, not 53 MW |
| Vapour at 200°C | 11.100 MW — output is linear in temperature, so the clip is real |
| Vapour below the fluid box minimum | 0 MW |
| No electrical demand | 0 MW, no vapour consumed |
| ~3 MW demand | 3.000 MW, 1.97 vapour/s of the 12/s maximum |
| Lean Quench | 60 vapour per core |
| Cryogenic Quench | 400 vapour per core, 100 Fluoroketone returned hot |
| Radiative cooling | hot Fluoroketone → cold, on a platform |
| Technology gating | tier-2 recipes disabled until `sae-cryogenic-quenching` |
| Placement | builds on a platform, refused on Nauvis |

## 9.6 Open questions

- Whether tier 1 at 90 MJ/core is *expensive* or *impossible* in play: 100 MW needs roughly 11 chemical plants and 67 cores/min. If it reads as impossible, raise tier 1 toward 150 MJ/core before touching anything else — the ratio between tiers (about 1 : 6.7) is the thing to preserve, not the absolute numbers.
- The radiator ratio (currently ~10 plants per quench plant) has not been playtested for how it *feels* to lay out.
- Tier 3's asteroid-derived resource, deferred to the endgame design.
- The turbine's art is derived from vanilla's steam turbine, recoloured to a cryogenic teal (`tools/recolour-turbine.py`), and the Quench Vapour icon is a gradient-mapped sibling drop in the same teal (`tools/derive-vapour-icon.py`). Both are derived rather than drawn; a real render would still be better.

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

The **Quench Turbine** is the design's only new building. It is not a tier of anything — it is a power source whose output per shipped Magmatic Core is set by which quench recipe the player has unlocked, which no existing building does, filling a documented gap in platform power between solar and Aquilo-locked fusion. Every other part of the mechanic runs on ordinary chemical plants. See Section 9.

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

- **Quench Turbine** — space platform building, crafted from Thermionic Assembly
- **Lean Quench** — the tier-1 quench recipe that feeds it

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
- ~~How much Calcite is consumed?~~ **2 per 25 Scrap (per 100 Molten Scrap).** Well above lava-casting's 1 per 250 molten metal, so the import is still real, but no longer dwarfing the metal it fluxes (an earlier 10 did).
- ~~Is remelting more or less material-efficient than recycling?~~ **Less, deliberately.** ~0.24 iron + 0.15 copper plate per Scrap against recycling's ~0.6 iron-equivalent plus circuits/LDS. Its niche is *deterministic bulk plate* for a base drowning in gears, not a recycling replacement. (An earlier 50-molten-scrap version was ~5x below recycling on iron alone — too low to serve even that niche.)
- ~~Copper Foil's copper-equivalent value~~ **1 Foil = 15 molten copper = 1.5 copper plate = exactly the 3 Copper Cable it replaces.** Electronic Circuit is value-neutral, Advanced gets a ~25% copper edge, Processing Unit carries only the deliberate iron discount of §7.3. (An earlier 10-foil-per-craft version made each foil worth 0.15 plate — a ~10x discount that made the alt recipes universally dominant.)
- ~~Contaminated Sulfuric Acid volume vs. Processing Unit demand~~ **Runs at ~3x surplus** — 15 acid recovered per Resonant Circuit against 5 consumed per Processing Unit.
- Holmium yield, made concrete: **~0.016 ore per Scrap** via a 90/10 non-ferrous split, just above recycling's 1% — a genuine supplement. (An earlier 95/5 split landed at ~0.008, *below* recycling, so the path added nothing.)

### Still open

**Scrap Remelting**

- Should remelting produce any waste?
- Whether 25 Scrap → 100 Molten Scrap is the right *absolute* throughput once real Fulgora scrap rates are playtested — the ratio to recycling above is settled, the volume is not.

**Ferrous / Non-Ferrous separation**

- Should the split be deterministic?
- Should there be a small waste stream?
- Exactly how large the iron surplus ends up. With Copper Foil at one per craft, copper is now the chain's bottleneck and the iron surplus is correspondingly larger — is it "a real problem" or crippling?

**Copper Foil**

- Molten Iron ratio — 15:1 copper-skewed today; must stay so.
- Should the Foundry's existing productivity apply normally?

**Circuit recipes**

Compare against vanilla on raw resource consumption, machine count, power consumption, intermediate item count, throughput, and space. The integrated chain should be **strong in the right circumstances**, not universally optimal. Copper value is now neutral, so this comparison is about the *molten-iron* substitution and machine count, not copper.

**Capstone**

- Catalyst Rod cost (1 Holmium Ore + 2 Foil + 5 Iron Plate) vs. how many crafts it should feel worth — cheap in ingredients, gated purely by holmium.
- Magmatic Core lava/tungsten volumes (500 lava + 5 Tungsten Plate) — unchanged and unevaluated. Now also the ongoing consumable: one chemical plant quenching flat out consumes 360 cores/hour, i.e. ~360 holmium ore + ~1800 tungsten ore per hour, feeding 9MW on tier 1 or 60MW on tier 2.

**Quench Turbine**

See Section 9.6 — every number is engine-verified but none is playtested. The open call is whether tier 1 at 90MJ per core is expensive or simply impossible (100MW needs ~11 chemical plants and 67 cores/min), and whether the tier-2 radiator field (~10 plants per quench plant) is a satisfying layout problem or just floor space.

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

16. Quench Turbine and Quench Vapour
17. The quench recipe ladder (Lean, then Cryogenic) and the radiative Fluoroketone loop
18. Magmatic Core export logistics at sustained consumption rates

Test after each phase whether the resulting production loops actually create interesting factory layouts. If they do, further expansion should focus on **deepening these interactions**, not adding more resources or more buildings.

---

# Summary

The strongest version of the Vulcanus/Fulgora relationship is not a new machine or a flat efficiency bonus.

It is a **closed industrial loop** built from existing systems, in which every cross-planet shipment is forced by resource locality rather than by artificial building restrictions:

> **Calcite → Scrap Remelting → Separation → Copper Foil → Circuits → Catalyst Rod → (ship) → Lava + Tungsten → Magmatic Core → (ship back) → Thermionic Assembly → Quench Turbine**

Fulgora provides recycling, electromagnetic processing, and the catalyst.

Vulcanus provides the reagent, the lava, and the thermal metallurgy.

Each planet produces one half of a shared capstone, and neither half can be made without the other. The player is rewarded for connecting the two without being forced to do so.

The tree then terminates in a **space platform capability** — the pattern intended for every cross-planet tree in this mod, with the accumulated platform improvements forming the eventual endgame. This tree claims **power**, filling the real gap between failing solar and Aquilo-locked fusion, and in doing so converts the Vulcanus leg from a one-time crafting requirement into a permanent supply line.
