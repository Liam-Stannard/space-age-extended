# Overall Mod Design Framework

## 1. Vision

This mod extends Factorio: Space Age by deepening the relationships *between* planets. Vanilla Space Age gives each planet its own self-contained tech tree; a player can complete the game while treating Nauvis, Vulcanus, Fulgora, Gleba, and Aquilo as five separate factories connected only by rockets and platform cargo. This mod does not replace that experience — it adds an optional layer on top of it.

> **Every planet pair can have an industrial relationship worth building for, and the sum of those relationships becomes the mod's endgame.**

The mod is not one big feature. It is a **pattern**, applied once per planet pair that gets a tree. [Vulcanus ↔ Fulgora: Cross-Planet Industrial Integration](vulcanus-fulgora.md) is the first tree built to this pattern; this document is the pattern itself, independent of which specific tree implements it.

---

## 2. Core Design Philosophy

These rules apply to every cross-planet tree the mod adds, not just Vulcanus↔Fulgora.

### 2.1 The shipping principle

All Space Age buildings (Foundry, Electromagnetic Plant, Chemical Plant, Recycler, Cryogenic Plant, Biochamber, etc.) can be built on any planet with the right prerequisites. This has one hard consequence for design:

> **Building placement can never justify cross-planet shipping.** If a recipe could be run locally, a rational player will always build the machine locally rather than ship the output.

Shipping is only ever justified when **a single recipe requires two inputs that exist exclusively on different planets**, so one of them must physically move. Every cross-planet leg in every tree must be traceable to this rule — not to a scripted restriction, not to a cost bonus, but to genuine resource locality. If a proposed tree's justification for shipping can be defeated by "the player just builds the machine on the other planet instead," the tree is broken and needs a different anchor.

### 2.2 New production decisions, not flat bonuses

A tree succeeds when it creates a **choice** the player didn't have before — "is this material more valuable processed route A or route B," "how much import capacity do I need," "what do I do with this byproduct" — rather than a passive multiplier ("+15% productivity when using imported material"). Flat bonuses are efficient to implement and design but produce no factory-design problem, which is the actual goal.

### 2.3 Minimal footprint on existing systems

- **No Quality changes.** Quality stays the existing module-driven system across every tree. No quality-gated recipes, no new quality tiers.
- **No redundant building tiers.** No "Mk II" versions of Foundry, Electromagnetic Plant, Chemical Plant, Recycler, or any other existing building. New behavior comes from new recipes on existing buildings, not new buildings that do what an existing one already does.
- **One new building per tree, at most, and only with a specific justification.** A new building is acceptable only when it introduces a genuine mechanic that no existing building has (see Vulcanus↔Fulgora's Thermionic Generator, justified by a temperature-dependent efficiency curve that nothing else in the game has). If the new behavior can be expressed as a recipe on an existing building, it must be.
- **No unnecessary intermediate-item bloat.** Every new item needs a mechanical reason to exist as a distinct item (usually: it needs to be a fluid for pipe/tank logistics, or it needs to be shippable/storable independent of its neighbors in the chain). "Feels like more content" is not a justification.
- **No building-placement gimmicks.** No recipe is ever restricted to "must be built on planet X" as an arbitrary rule. Every planet lock in every tree comes from a resource that is unconditionally exclusive to that planet (an ore, a fluid, a raw material) — never from a rule bolted onto the recipe itself.

### 2.4 Optional, not mandatory

A player must be able to finish the game, including reaching Aquilo and any endgame content, using only vanilla planetary tech trees. Every cross-planet tree is a strictly optional layer that makes certain problems easier or certain outcomes better, never a hard gate. The "vanilla-only" playstyle must remain fully viable throughout.

### 2.5 Each planet keeps its identity

A planet must never become a generic resource depot for another. Both planets in a tree contribute something the other planet's economy cannot replicate by relocating buildings — a material, a native process, or a manufacturing specialty that is intrinsic to that planet's identity in vanilla Space Age. If a tree could be re-skinned onto a different planet pair without changing its substance, it has not actually engaged with what makes those two planets distinct.

### 2.6 Byproducts are the player's problem

Chains that produce a "clean" output only are less interesting than chains that produce something the player has to make an active decision about (surplus material, a spent catalyst, a contaminated fluid). Every such byproduct needs **at least two viable outlets** using existing systems — never a single mandatory sink, and never a dead end that must be voided.

---

## 3. The Cross-Planet Tree Template

Every tree the mod adds should be describable in this shape:

1. **Two planets.** Each tree connects exactly one pair.
2. **A forcing anchor in each direction.** At least one recipe that can only be completed by importing a resource that is exclusively native to the other planet (Section 2.1). Trees may be one-way (only one planet exports) or round-trip (material physically returns, e.g. a depleted catalyst); round-trip loops create more sustained logistics pressure and are preferred where the mechanic naturally supports it.
3. **A processing chain on each planet**, built from existing specialized buildings, that turns the imported resource plus local materials into something meaningful — ideally reusing an existing production concern on that planet (e.g. feeding into Fulgora's existing electronics chain, or Vulcanus's existing metallurgy chain) rather than creating a fully parallel economy.
4. **A shared capstone**, where each planet is responsible for producing one half, and the two halves combine (usually via a recipe craftable anywhere) into a single top-tier item. Neither half is useful without the other — the capstone is the proof that the player actually built out both sides.
5. **A platform-facing payoff** (Section 4) — the capstone item unlocks a space-platform technology that improves one platform subsystem. This is what turns a self-contained regional loop into a contribution to the mod's overall endgame.
6. **A completed technology progression** that gates each stage sensibly, ending in the platform technology, with cross-dependencies made explicit where a step genuinely needs both halves of the chain (as Vulcanus↔Fulgora Technology 3 requires both Technology 1 and Technology 2).

A tree proposal should be checked against this template before any recipe numbers are tuned. If a proposed tree can't fill in items 1–5 above, it isn't ready.

---

## 4. The Platform-Capability Pattern

### 4.1 Why platforms are the unifying endgame

Space platforms are the one context every planet's player eventually shares, and vanilla Space Age gives them comparatively little planet-specific development — platform tech is mostly generic (thrusters, asteroid collectors, basic weapons) regardless of which planets a player has visited. This is the gap the mod's endgame targets:

> **Each cross-planet tree terminates in a technology that improves a different space platform subsystem. The accumulated set of platform capabilities across all implemented trees becomes the mod's endgame goal.**

### 4.2 Subsystem carve-up

To keep trees from competing for the same payoff, each tree claims a distinct platform subsystem. The rough carve-up:

| Subsystem | Description | Status |
|---|---|---|
| Power | Electricity generation aboard a platform | **Claimed — Vulcanus↔Fulgora** (Thermionic Generator, Section 9 of that doc) |
| Thrust | Engine output, fuel efficiency, or maneuverability | Open |
| Asteroid processing | Improvements to how platforms capture, sort, or process asteroid chunks | Open |
| Cargo / logistics | Storage density, transfer speed, or automation of platform cargo | Open |
| Defence | Weapons, shielding, or damage mitigation against asteroids and threats | Open |
| Structure | Hull integrity, platform size limits, or foundation mechanics | Open |

This list is a starting carve-up, not a fixed ceiling — if a future tree's natural payoff doesn't fit any open slot cleanly, the list should be revisited rather than forcing a fit. What matters is that two trees should not both claim the same subsystem; the point of the pattern is one coherent platform upgrade per tree, not a pile of competing power generators.

### 4.3 Capstone shippability requirement

Every tree's capstone item (Section 3.4) must be **a clean, self-contained, freely shippable end product** with no planet-locked properties, fluid state, or decay mechanic of its own. This is what makes forward compatibility possible: a later mega-technology can consume one capstone item from each implemented tree without needing to know how any of them were produced. Vulcanus↔Fulgora's Thermionic Assembly is the reference example — it is craftable anywhere precisely because both of its own inputs are already planet-locked by their own production, so the assembly step itself carries no lock.

### 4.4 The eventual endgame

Once multiple trees exist, a final technology should require **several trees' platform capabilities simultaneously** — for example, a platform configuration that can only survive a route or destination that breaks a conventionally-equipped platform. This is intentionally deferred: it should be designed once there are at least two or three implemented trees to draw on, not speculatively designed around trees that don't exist yet.

---

## 5. Status

### 5.1 Implemented trees

| Tree | Planets | Subsystem claimed | Capstone | Status |
|---|---|---|---|---|
| Cross-Planet Industrial Integration | Vulcanus ↔ Fulgora | Power (Thermionic Generator) | Thermionic Assembly | Design complete, see [Vulcanus ↔ Fulgora: Cross-Planet Industrial Integration](vulcanus-fulgora.md) |

### 5.2 Open slots

Thrust, asteroid processing, cargo/logistics, defence, and structure are all unclaimed. No specific planet pair is committed to any of these yet — per the scope of this document, that design work is deliberately left for when each tree is actually proposed, so that the anchor resources (Section 2.1) and planet-identity contributions (Section 2.5) can be worked out concretely rather than assumed in the abstract.

---

## 6. Evaluation Checklist for Future Trees

Before a new cross-planet tree proposal is accepted, it should be able to answer yes to each of the following:

- Does every cross-planet shipment trace to a recipe that literally cannot be completed without an exclusively-local resource from the other planet (Section 2.1)?
- Does the tree avoid new Quality mechanics, redundant building tiers, and more than one new building (Section 2.3)?
- Is every new item mechanically justified (fluid logistics, independent shippability) rather than existing purely for "more content" (Section 2.3)?
- Can a player ignore the tree entirely and still complete the game (Section 2.4)?
- Does each planet contribute something the other could not replicate by relocating buildings (Section 2.5)?
- Does every byproduct have at least two existing-system outlets (Section 2.6)?
- Does the tree fit the template in Section 3 — two planets, a forcing anchor, per-planet chains, a shared capstone, a platform payoff, a coherent tech progression?
- Does the tree claim a platform subsystem that no other implemented tree has already claimed (Section 4.2)?
- Is the capstone item clean, stable, and freely shippable with no planet-locked properties (Section 4.3)?

A tree that fails any of these should be reworked before recipe-level balancing begins — balancing an anchor that doesn't hold, or a building that duplicates an existing one, wastes the tuning effort that follows it.

---

## 7. Roadmap Guidance

1. Finish implementing and playtesting the Vulcanus↔Fulgora tree in full (its own four-phase plan is in Section 17 of that document).
2. Use what that playtesting reveals — which mechanics felt satisfying, which byproducts were tedious versus interesting, whether the shipping loop held up at scale — to refine this framework before starting a second tree.
3. Pick the second tree's planet pair and subsystem deliberately: prefer a pairing and subsystem combination that exercises a different kind of anchor resource (e.g. a perishable/spoiling resource from Gleba, rather than another bulk-fluid anchor like Lava) so the mod's trees stay mechanically distinct from each other rather than reskinning the same shape.
4. Only after at least two trees are implemented, begin designing the multi-capability endgame technology described in Section 4.4.
