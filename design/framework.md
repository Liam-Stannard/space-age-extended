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
- **One new building per tree, at most, and only with a specific justification.** A new building is acceptable only when it introduces a genuine mechanic that no existing building has (see Vulcanus↔Fulgora's Quench Turbine, justified by an output-per-shipped-item that a recipe tier sets rather than the item, which nothing else in the game does). If the new behavior can be expressed as a recipe on an existing building, it must be.
- **No unnecessary intermediate-item bloat.** Every new item needs a mechanical reason to exist as a distinct item (usually: it needs to be a fluid for pipe/tank logistics, or it needs to be shippable/storable independent of its neighbors in the chain). "Feels like more content" is not a justification.
- **No building-placement gimmicks.** No recipe is ever restricted to "must be built on planet X" as an arbitrary rule. Every planet lock in every tree comes from a resource that is unconditionally exclusive to that planet (an ore, a fluid, a raw material) — never from a rule bolted onto the recipe itself.

### 2.4 Required for the mod's endgame

**Required for the mod's endgame.** The Core (Section 4.4) is the mod's own destination, and there is no reason the mod's endgame should be reachable without the mod's content. Reaching it requires the platform capabilities the trees produce, and it requires them because the corridor is physically impassable otherwise — not because a recipe demands a token. That corridor only starts past the point where a vanilla platform already turns back; vanilla's own Shattered Planet approach is untouched.

The line is the vanilla win condition. Everything up to it is optional. Everything past it is the mod, and the mod may ask for its own tools.

**The cost of this, stated plainly.** Every mandatory tree becomes a single point of failure: if one of them is tedious, it blocks the endgame instead of being skipped. So the mandatory set must be kept small — five — with the remaining trees adding depth that makes the corridor *cheaper* rather than *possible*. The mandatory five must also be the first trees playtested, because there is no longer an escape hatch if one of them is not fun.

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
5. **A platform-facing payoff** (Section 4) — the capstone item unlocks a space-platform technology that improves one platform subsystem **and answers one corridor hazard that no other tree answers** (Section 4.4). This is what turns a self-contained regional loop into a contribution to the mod's overall endgame.
6. **Interaction with the existing capabilities** (Section 4.5). A capability that can be installed without changing how any other capability is used is a shopping-list item, not a payoff.
7. **A completed technology progression** that gates each stage sensibly, ending in the platform technology, with cross-dependencies made explicit where a step genuinely needs both halves of the chain (as Vulcanus↔Fulgora Technology 3 requires both Technology 1 and Technology 2).

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
| Power | Electricity generation aboard a platform | **Claimed — Vulcanus↔Fulgora** (Quench Turbine, Section 9 of that doc) |
| Thrust | Engine output, fuel efficiency, or maneuverability | Open — mandatory |
| Asteroid processing | Improvements to how platforms capture, sort, or process asteroid chunks | Open — mandatory |
| Defence | Weapons, shielding, or damage mitigation against asteroids and threats | Open — mandatory |
| Structure | Hull integrity, platform size limits, or foundation mechanics | Open — mandatory |
| Cargo / logistics | Storage density, transfer speed, or automation of platform cargo | **Not a tree slot** — met by vanilla platform-to-platform transfer plus a depot buildout using existing buildings (endgame doc §3), not by a new capstone chain |

This list is a starting carve-up, not a fixed ceiling — if a future tree's natural payoff doesn't fit any open slot cleanly, the list should be revisited rather than forcing a fit. What matters is that two trees should not both claim the same subsystem; the point of the pattern is one coherent platform upgrade per tree, not a pile of competing power generators.

**The mandatory five, named.** Power, Structure, Thrust, Asteroid processing, and Defence — one tree each, one corridor band each (endgame doc §2a). Cargo/logistics sits outside this count because it isn't gated behind a capstone; the corridor itself is built from mechanics vanilla already provides. Any future subsystem beyond these five defaults to the optional tier (Section 4.4) unless a specific new corridor hazard is designed for it.

**No redundancy among the mandatory trees.** An earlier draft of this document deliberately gave every corridor hazard two answers from different pairs, so that no single tree became mandatory. Section 2.4 now says the opposite, and the two positions cannot both hold: redundancy is exactly what makes a tree skippable. For any hazard on the mandatory path there is **one** answer, from **one** tree. Trees outside the mandatory set may overlap freely, since their job is to make the corridor cheaper rather than passable.

**One power source.** A platform runs a single generator type, so the Quench Turbine's numbers set the exchange rate for every other capability's power cost. Its tuning cannot be finalised in isolation from the capabilities that draw on it.

### 4.3 Capstone shippability requirement

Every tree's capstone item (Section 3.4) must be **a clean, self-contained, freely shippable end product** with no planet-locked properties, fluid state, or decay mechanic of its own. This is what makes forward compatibility possible: a later mega-technology can consume one capstone item from each implemented tree without needing to know how any of them were produced. Vulcanus↔Fulgora's Thermionic Assembly is the reference example — it is craftable anywhere precisely because both of its own inputs are already planet-locked by their own production, so the assembly step itself carries no lock.

### 4.4 The endgame: the Core

Vanilla's Shattered Planet is not a destination. It no longer exists as a planet; a platform travels toward it, takes escalating damage, and eventually turns back or dies. Roughly halfway out the usable asteroids stop and are replaced by promethium chunks that crush into nothing, so a flying factory can no longer feed itself. Speed is punished, so it cannot be outrun.

The mod's endgame finishes that sentence: **the Core**, the intact metallic heart of the destroyed world, still out there past the point where every vanilla platform turns around. It is the first planet in the game that cannot be bootstrapped — metal and vacuum, no water, no oil, no biology, no lava — so everything arrives down a corridor the player has to build and then maintain.

**Gating is by traversal, not by ingredients.** A final technology that simply consumes one capstone from each tree is a checklist: the player looks up what is missing and grinds it. Instead, each distance band of the corridor removes a specific vanilla crutch, and the tree that answers it is the only thing that restores it. The corridor teaches its own requirements by killing platforms in legible, specific ways, and degradation-not-destruction means the player limps home knowing what to build.

Full hazard-to-tree mapping is in the endgame design document ([design/endgame.md](endgame.md)); what the capstones are spent on once a player arrives is in [design/core.md](core.md). The framework-level rules are:

- Each mandatory tree answers exactly one band (Section 4.2).
- Each band's failure must be **specific and legible** — a platform that dies out there should die of one identifiable thing.
- Nothing on the corridor may be brute-forced with quantity. Every gate is qualitative, or players will simply carry more railguns.

### 4.5 Capabilities must interact

Six trees each bolting an independent upgrade onto a platform produces a shopping list, not a system. The capabilities are bound together by making them compete for and feed the same five resources: **electricity, heat, ice, weight, and consumables.** Adding any one changes the arithmetic of the others.

Rules for any new capability:

1. Draw on at least one shared resource and feed at least one other capability.
2. No flat multipliers — a multiplier cannot be traded against anything.
3. Degrade, don't destroy; the player should be able to see the mistake and correct it.
4. Every capability must have a wrong platform to install it on.
5. Never relieve two of the five at once.

**Note on heat:** Vulcanus↔Fulgora's Power capability deliberately exposes **no** usable waste heat. An earlier draft made it a `reactor` with a real heat-pipe interface; that was abandoned because vanilla heat exchangers and steam turbines would have converted its rejected heat into roughly as much electricity again, which relieves Power twice over and breaks rule 5. The Quench Turbine has no heat network at all. Any future tree whose capability wants heat as an input must therefore introduce it, not assume a baseline — see [vulcanus-fulgora.md §9.2](vulcanus-fulgora.md#92-the-quench-turbine).

---

## 5. Status

### 5.1 Implemented trees

| Tree | Planets | Subsystem claimed | Capstone | Status |
|---|---|---|---|---|
| Cross-Planet Industrial Integration | Vulcanus ↔ Fulgora | Power (Quench Turbine) | Thermionic Assembly | Implemented, engine-verified, not yet playtested — see [Vulcanus ↔ Fulgora: Cross-Planet Industrial Integration](vulcanus-fulgora.md) |

### 5.2 Open slots

Thrust, asteroid processing, defence, and structure are all unclaimed. (Cargo/logistics is not a tree slot — see Section 4.2.) No specific planet pair is committed to any of these yet — per the scope of this document, that design work is deliberately left for when each tree is actually proposed, so that the anchor resources (Section 2.1) and planet-identity contributions (Section 2.5) can be worked out concretely rather than assumed in the abstract.

---

## 6. Evaluation Checklist for Future Trees

Before a new cross-planet tree proposal is accepted, it should be able to answer yes to each of the following:

- Does every cross-planet shipment trace to a recipe that literally cannot be completed without an exclusively-local resource from the other planet (Section 2.1)?
- Does the tree avoid new Quality mechanics, redundant building tiers, and more than one new building (Section 2.3)?
- Is every new item mechanically justified (fluid logistics, independent shippability) rather than existing purely for "more content" (Section 2.3)?
- Can a player ignore the tree entirely and still reach the vanilla win condition (Section 2.4)?
- If the tree is on the mandatory path, is it the *only* answer to its corridor hazard, and is that hazard qualitative rather than a quantity check (Sections 4.2, 4.4)?
- Does its capability draw on at least one shared platform resource and feed at least one other capability, rather than standing alone (Section 4.5)?
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
4. **Build and playtest the mandatory five before anything else.** Under Section 2.4 these have no escape hatch — a tree that is tedious now blocks the endgame rather than being skipped — so any tree on the mandatory path must prove it is fun before optional depth is added anywhere.
5. Tune the Quench Turbine only once several capabilities exist to draw on it, since it sets the power exchange rate for all of them (Section 4.2).
6. Design the Core and the corridor bands last, when the capabilities they gate on are known quantities rather than sketches.
