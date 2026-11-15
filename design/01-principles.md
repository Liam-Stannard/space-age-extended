# Principles

These are the rules every part of the mod must meet. Each principle says what it applies to and how it is checked; a rule that does not apply to a subject is not judged against it.

---

## 1. Limits use physics, not planet names

> A building or recipe can only be limited by something physical, like air pressure or gravity. Never by naming a planet.

Why: players can work out physics. "Only on Gleba" teaches them nothing.

- **Applies to:** every building and recipe
- **Fails when:** the limit names a planet instead of using something physical.
- **Concern when:** none.
- **Checked by:** the limits listed in the mod's data dump.
- **Vanilla precedent:** the biolab works only at Nauvis's air pressure.
- **Exceptions:** none
- **Source:** original principle

## 2. Every new item has a purpose

> Every new item, whether a product or a building, must have at least one clear purpose:
> - it brings in a new mechanic;
> - it fits into a tech tree, as a step the tree needs;
> - it uses up a byproduct that would otherwise pile up;
> - it gives the player a real choice, better in some cases and worse in others;
> - it is something that has to be shipped between planets;
> - it helps the player reach or survive the Core.
>
> Fluids count as items.

Why: "the chain feels bigger with another step" is not a purpose.

- **Applies to:** every new item and building
- **Fails when:** an item has none of these purposes.
- **Concern when:** its only purpose is being one more step in a chain.
- **Checked by:** the item's spec says which purpose it serves, and the mod's data dump shows it is used.
- **Vanilla precedent:** the foundry brings in a new mechanic (casting); the recycler uses up what you don't want.
- **Exceptions:** none
- **Source:** Liam, 2026-11-13

## 3. Each planet's tree extends it

> Each planet gets one tree that extends its own vanilla tech tree. Each tree adds at least:
> - one new building;
> - one new item that can be used on a space platform to help reach the Core.
>
> Anything in the mod that can be placed on a platform must have something to do there.

Why: every planet then plays a part in the journey to the Core, and nothing sits on a platform with no job.

- **Applies to:** each planet's tree; every building and item that can be placed on a platform
- **Fails when:** a tree adds no new building, or no item that helps a platform reach the Core; or something can be placed on a platform but nothing it needs can get there (like the Hydrogen Turbine).
- **Concern when:** the platform item is useful only on the way to the Core, or works on a platform only weakly.
- **Checked by:** the tree's spec lists its building and platform item; the mod's data dump shows its placement limits, and graph.py --planet space-platform shows its inputs can reach a platform.
- **Vanilla precedent:** each vanilla planet adds buildings that are useful on platforms, like Fulgora's EM plant and Aquilo's cryogenic plant.
- **Exceptions:** none
- **Source:** Liam, 2026-10-29 and 2026-11-13

## 4. Don't break progression or make resources cheap

> Changes to items or mechanics must not change vanilla's progression, or make any resource much cheaper to get.

Why: the player should still meet vanilla's challenges in vanilla's order. A cheap shortcut removes a challenge instead of adding one.

- **Applies to:** every item, building, recipe and mechanic in the mod
- **Fails when:** something lets the player skip or reorder vanilla's progression, or a resource costs 50% or less of its vanilla raw cost (graph.py, vanilla's route).
- **Concern when:** a resource is 20% or more cheaper than its vanilla raw cost.
- **Checked by:** graph.py --section tech for when things unlock, and --section cost and --section loops for cost, compared with vanilla.
- **Vanilla precedent:** none
- **Exceptions:** the win condition moves to the Core.
- **Source:** Liam, 2026-11-13

## 5. A tree gives the player a problem to solve

> A tree makes the player decide something, like a ratio, a route, or what to do with a byproduct. It never just adds a flat bonus.

Why: a flat bonus has no cost to weigh, so there is nothing to design.

- **Applies to:** each planet's tree
- **Fails when:** the tree's gain is a flat percentage with no cost the player chooses.
- **Concern when:** the choice exists but one answer is always best (judgement or playtest).
- **Checked by:** reading the tree's spec and recipes for a choice the player makes.
- **Vanilla precedent:** Gleba's spoilage forces the player to plan for speed.
- **Exceptions:** none
- **Source:** original principle

## 6. Every byproduct has a use

> Every byproduct has at least one use in the mod. Recycling it counts as a use only where its spec says recycling is the intended path.

Why: a byproduct with no use is a chore.

- **Applies to:** every chain in the mod, including the Core's
- **Fails when:** a byproduct has no use, or a loop makes more than can be used, so some must be destroyed (judgement or playtest).
- **Concern when:** its only use comes much later than the byproduct does.
- **Checked by:** the recipes in the mod's data dump that take each byproduct, and graph.py --section loops.
- **Vanilla precedent:** Fulgora's scrap gives many products, and each has a use.
- **Exceptions:** none
- **Source:** original principle, edited by Liam, 2026-11-13

## 7. Each tree's product must reach the Core

> The Core needs a product from every tree. Each tree must plan how that product gets to the Core, including its weight and whether it spoils on the way.

Why: the trip to the Core is part of the tree's design, not an afterthought.

- **Applies to:** each planet's tree, and its product
- **Fails when:** the product's weight is not set on purpose, or it spoils on the trip and the tree has no answer.
- **Concern when:** more than twice as many fit in a rocket as of the nearest vanilla item of the same kind: a building compared with vanilla buildings, an intermediate like LDS with vanilla intermediates.
- **Checked by:** graph.py --section weight for the product; its spoil time against the trip (judgement or playtest).
- **Vanilla precedent:** Gleba's science packs spoil, so the player must ship them fast.
- **Exceptions:** none
- **Source:** original principle

---

| # | Principle | Applies to |
|---|---|---|
| 1 | Limits use physics, not planet names | every building and recipe |
| 2 | Every new item has a purpose | every new item and building |
| 3 | Each planet's tree extends it | each tree; anything on a platform |
| 4 | Don't break progression or make resources cheap | every item, building, recipe and mechanic |
| 5 | A tree gives the player a problem to solve | each tree |
| 6 | Every byproduct has a use | every chain |
| 7 | Each tree's product must reach the Core | each tree's product |
