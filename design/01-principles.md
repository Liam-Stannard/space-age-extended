# Principles

The rules every part of the mod is held to. They exist to be *applied*, not
admired: each one is written so that a concrete proposal can fail it.

---

## 1. Shipping must be forced by resource locality

Every Space Age building — Foundry, Electromagnetic Plant, Chemical Plant,
Recycler, Cryogenic Plant, Biochamber — can be built on any planet with the right
prerequisites. One hard consequence follows:

> **Building placement can never justify cross-planet shipping.** If a recipe
> could be run locally, a rational player builds the machine locally rather than
> shipping the output.

Shipping is justified in exactly one situation: **a single recipe requires two
inputs that exist exclusively on different planets**, so one of them must
physically move. Every cross-planet leg in the mod traces to that, never to a
cost bonus and never to a scripted restriction.

If a proposed leg can be defeated by "the player just builds the machine on the
other planet," the leg is broken and needs a different anchor.

## 2. Decisions, not multipliers

A feature earns its place by creating a *choice*: is this material worth more
processed route A or route B, how much import capacity do I need, what do I do
with this byproduct. A multiplier cannot be traded against anything, so it
produces no factory-design problem.

The same rule governs platform capabilities: one that can be installed without
changing how any other capability is used is a shopping-list item, not a payoff.

## 3. Minimal footprint on vanilla systems

- **No Quality mechanics.** Quality stays the module-driven system it already is.
  No quality-gated recipes, no new tiers.
- **No redundant building tiers.** No Mk II of anything vanilla already has. New
  behaviour comes from new recipes on existing buildings.
- **At most one new building per tree**, and only where it introduces a mechanic
  no existing building has. If the behaviour can be a recipe, it is a recipe.
- **No item bloat.** A new item needs a mechanical reason to be distinct — it
  must be a fluid for pipe logistics, or shippable independently of its
  neighbours in the chain. "Feels like more content" is not a reason.
- **No placement gimmicks.** No recipe is ever restricted to "must be built on
  planet X." Every planet lock comes from a resource unconditionally exclusive to
  that planet.

## 4. Each planet keeps its identity

Both planets in a tree contribute something the other cannot replicate by
relocating buildings — a material, a native process, or a manufacturing
speciality intrinsic to that world in vanilla. A tree that could be re-skinned
onto a different pair without changing its substance has not engaged with what
makes those two worlds distinct.

## 5. Byproducts are the player's problem

A chain that produces only a clean output is less interesting than one that hands
the player something they did not ask for: surplus material, a spent catalyst, a
contaminated fluid. Every byproduct needs **at least two viable outlets** using
existing systems — never one mandatory sink, never a dead end that must be
voided.

## 6. Degrade, don't destroy

A mistake should be visible and correctable. Out on the corridor the intended
failure is limping home knowing what to build, not losing the platform. There is
no meltdown anywhere in the mod, only worse exchange rates.

## 7. Vanilla is untouched up to the Edge

The line is the vanilla win condition. Everything up to it is optional and
additive. Everything past it is the mod's own territory, and the mod is allowed
to require the mod's own content there — because the corridor is physically
impassable without it, not because a recipe demands a token.

The corollary, stated plainly: **every mandatory tree is a single point of
failure.** If one is tedious it blocks the destination rather than being skipped.
That is why the mandatory set is kept to five, why those five are played before
any optional depth is built, and why a tree that proves unfun must be
demotable — see [the roadmap](06-roadmap.md).

---

## The checklist

A tree proposal answers yes to all of these before any recipe number is tuned.
Balancing an anchor that does not hold wastes the tuning that follows it.

- [ ] Does every cross-planet shipment trace to a recipe that cannot be completed
      without an exclusively-local resource from the other planet? *(§1)*
- [ ] Does each planet contribute something the other could not replicate by
      relocating buildings? *(§4)*
- [ ] No Quality mechanics, no redundant building tier, at most one new building?
      *(§3)*
- [ ] Is every new item mechanically justified rather than flavour? *(§3)*
- [ ] Does every byproduct have at least two existing-system outlets? *(§5)*
- [ ] Can a player ignore the tree entirely and still reach the vanilla win
      condition? *(§7)*
- [ ] Does it fit the [tree pattern](02-tree-pattern.md) — two planets, a forcing
      anchor, per-planet chains, a shared capstone, a platform payoff, a coherent
      technology progression?
- [ ] Does it claim a platform subsystem no other tree has claimed, and does its
      capability draw on at least one shared resource and feed at least one other
      capability? *([03](03-platform-system.md))*
- [ ] Is the capstone item clean, stable and freely shippable, with no
      planet-locked property, fluid state or decay mechanic?
- [ ] If it is on the mandatory path, is it the only answer to its corridor band,
      and is that band's hazard qualitative rather than a quantity check?
      *([04](04-corridor.md))*
