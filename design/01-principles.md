# Principles

Five trees, designed one at a time, have to end up feeling like one mod. These
are the rules that make that true. Each is written so that a concrete proposal
can **fail** it — a principle that cannot be failed is decoration.

---

## 1. The crossing must be forced

This is the load-bearing rule, and it exists because of one engine fact: **every
building in Space Age can be built on any planet** once its technology is
researched. A Foundry works on Fulgora, an Electromagnetic Plant works on
Vulcanus.

> **Building placement never justifies shipping.** If a recipe could be run on
> the other planet, a rational player builds the machine there instead of
> freighting the output.

A cross-planet leg exists only where **one recipe needs two inputs that are each
exclusive to a different world**, so one of them physically has to move. Every
leg in every tree traces back to that.

Some materials cannot move at all, which makes them the strongest anchors
available. Vanilla marks them `auto_barrel = false`, so there is no barrel and
no way to put them in a rocket:

| World | Immovable fluids |
|---|---|
| Vulcanus | `lava`, `molten-iron`, `molten-copper` |
| Fulgora | `holmium-solution`, `electrolyte` |
| Aquilo | `ammoniacal-solution`, `ammonia`, `fluorine`, `lithium-brine` |

A recipe consuming one of those can only ever run on its own world. If the same
recipe also needs something only another world produces, the crossing is
guaranteed by physics rather than by rule — and that is the shape to reach for
first.

**Never lock a recipe to a planet by name.** No `surface_conditions` invented to
force a location, no "craftable only on Gleba." The lock comes from the
ingredient or it does not exist. Also worth knowing: `surface_conditions` is a
player-facing *filter*, not a runtime block — a recipe forced onto the wrong
surface by script still crafts.

## 2. Both planets send

A pair is not a supply route. If material only ever travels one way, one planet
is a mine and the other is the factory, and the tree could have been a single
planet's chain with an import.

Every tree moves material **in both directions**. The strongest form is a round
trip — something leaves, comes back changed, and leaves again — because it keeps
both legs running for as long as the player uses the tree, rather than only
while they are building it out.

## 3. A tree is small and finishable

**4–10 technologies.** A tree is a chapter, not a second planetary tech tree.
The player should be able to see its end from its beginning.

That budget is spent carefully:

- **New items** need a mechanical reason to be separate — it has to be a fluid,
  or it has to be storable and shippable on its own, or it carries a spoil
  clock. "The chain feels more substantial with another step" is not a reason.
- **New buildings** are rarer still. If the behaviour can be a recipe on an
  existing building, it is a recipe. The **capstone building is the tree's
  budget of one**; a second needs a mechanic that genuinely has no home in
  anything vanilla provides.
- **No parallel tiers.** Never a better Foundry, a better Recycler, a better
  Assembler. New behaviour, not the same behaviour with bigger numbers.

## 4. The theme has to be unrepeatable

For every tree, name the thing each planet contributes that **the other could
not obtain by building differently**. If both answers are not specific to those
two worlds, the tree has not engaged with them.

The test: could this tree be re-skinned onto a different pair by renaming its
items? If yes, it is generic content wearing a planet's colours, and the pairing
is doing no work.

## 5. Nothing threatens vanilla balance

The mod **adds**; it does not alter. No vanilla recipe, item or building is
modified. New recipes that output vanilla items are fine — a new route to a
known thing is content; changing the known thing is not.

For capstone buildings specifically:

- **An option, never a strict upgrade.** If installing one makes a vanilla
  building pointless, it is wrong. It should be better in some circumstances and
  worse in others, and the player should be able to say which.
- **It must not deflate a vanilla resource.** A chain that makes holmium or
  tungsten trivially abundant has not added a production line, it has removed
  one.

The single deliberate exception in the whole mod is the win condition, which
moves to the Core. Everything else vanilla does, it keeps doing.

## 6. The chain poses a problem, not a bonus

A flat multiplier — "+15% when using imported material" — cannot be traded
against anything, so it creates no factory to design. A tree earns its place by
making the player decide something: what ratio to run, how much import capacity
to build, which of two routes a material is worth more in, what to do with what
comes out that they did not ask for.

Where a chain produces a byproduct, it needs **at least two outlets** the player
can already build. Never one mandatory sink, and never something that must be
voided.

## 7. Gated only by vanilla progress

A pair's tree opens when **both its planets' vanilla tech trees are complete**,
and nothing else gates it. The mod never puts vanilla content behind mod
content, and never asks the player to detour before they would naturally arrive.

## 8. Capstone products must survive the journey

The endgame consumes one product from every capstone, on the Core, at the far
end of the longest supply line in the game. That imposes a hard shape on all
five:

- **A plain item.** No fluid-only capstone; it has to sit in a rocket and a
  cargo bay.
- **No spoil clock.** Spoilage keeps running in transit, so a perishable
  capstone would be undeliverable however good the logistics.
- **No planet-locked property** — nothing that only functions where it was made.
- **An explicit `weight`.** The engine derives weight from the recipe when it is
  not set, and the default is 100 against a rocket's 1,000,000 lift, i.e.
  10,000 per rocket. Fluid-heavy recipes derive absurdly cheap freight this way.
  Every capstone product sets its weight deliberately, because that number *is*
  the cost of the endgame's supply line.

A tree may use spoilage, fluids and locked materials as much as it likes
internally. The constraint applies to the one item that has to reach the Core.

## 9. The player can see why

The reason a material has to cross should be legible **in the recipe**. A player
who opens the capstone chain ought to be able to work out, without a wiki, which
ingredient came from where and why it could not have been made locally.

The same applies to failure: when something does not work, the cause should be
one identifiable thing.

---

## Checklist

Before a tree's recipes are worth tuning, it should answer yes to all of these.

- [ ] Does every crossing trace to a recipe that cannot be completed without a
      material exclusive to the other planet? *(§1)*
- [ ] Is any planet lock an ingredient rather than a rule? *(§1)*
- [ ] Does material move in both directions? *(§2)*
- [ ] Is it 4–10 technologies, with every new item mechanically justified and at
      most the one capstone building? *(§3)*
- [ ] Can you name what each planet contributes that the other could not get by
      building differently? *(§4)*
- [ ] Is the capstone building an option rather than a strict upgrade, and does
      the tree leave every vanilla resource and building as valuable as it
      found them? *(§5)*
- [ ] Does the chain create a decision rather than a bonus, and does every
      byproduct have two outlets? *(§6)*
- [ ] Does it open on vanilla progress alone? *(§7)*
- [ ] Is the capstone product a plain, non-spoiling, unlocked item with an
      explicit weight? *(§8)*
- [ ] Could a player work out from the recipes why the crossing is necessary?
      *(§9)*
