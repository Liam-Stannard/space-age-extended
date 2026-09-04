# Principles

Five trees, designed one at a time, have to end up feeling like one mod. These
are the rules that make that true. Each is written so that a concrete proposal
can **fail** it — a principle that cannot be failed is decoration.

---

## 1. The crossing must be forced

A cross-planet leg only exists if the player **cannot just do the work locally**.
So it matters exactly what the engine will and will not let them move.

### What is actually locked

Almost every production building can be **placed** anywhere. The Foundry,
Electromagnetic Plant, Cryogenic Plant, Biochamber, Recycler, Chemical Plant and
Assembler carry no surface conditions as entities — ship one to a platform or
another world and it works.

What is locked is the **recipe that manufactures them**, by surface property:

| Building recipe | Condition | Which means |
|---|---|---|
| `foundry`, `big-mining-drill`, turbo belts | pressure 4000 | Vulcanus only |
| `electromagnetic-plant`, `recycler`, `lightning-rod` | magnetic field ≥ 99 | Fulgora only |
| `biochamber`, the soils, `pentapod-egg` | pressure 2000 | Gleba only |
| `cryogenic-plant`, `fusion-reactor`, `fusion-generator` | pressure 100–600 | Aquilo only |
| `biolab`, `tree-seed`, `fish-breeding` | pressure 1000 | Nauvis only |

So a machine is *made* in one place and *used* anywhere. **Manufacture is not a
crossing** — the player builds it once and ships it, and the chain then runs
wherever they like.

A few entities genuinely cannot be placed everywhere, and those are real
constraints: `thruster`, `crusher`, `asteroid-collector` and the platform hub
need pressure 0 or gravity 0, so they are space-only; rails, vehicles, chests,
the rocket silo, boilers, stone and steel furnaces, roboports and burner
inserters all need gravity or pressure above zero, so they are ground-only.

### The three honest anchors

A leg is forced when one of these is true, and only then:

1. **An ingredient that cannot move.** Vanilla marks these `auto_barrel = false`
   — there is no barrel, so there is no rocket:

   | World | Immovable fluids |
   |---|---|
   | Vulcanus | `lava`, `molten-iron`, `molten-copper` |
   | Fulgora | `holmium-solution`, `electrolyte` |
   | Aquilo | `ammoniacal-solution`, `ammonia`, `fluorine`, `lithium-brine` |

2. **A surface condition on the recipe itself**, which is how vanilla locks its
   own processes — `acid-neutralisation` to pressure 4000, the bacteria and
   soils to 2000, each science pack to its own world. The surface properties
   available to separate them:

   | | pressure | gravity | magnetic field | solar |
   |---|---|---|---|---|
   | Nauvis | 1000 | 10 | 90 | 100 |
   | Vulcanus | 4000 | 40 | 25 | 400 |
   | Fulgora | 800 | 8 | **99** | 20 |
   | Gleba | 2000 | 20 | 25 | 50 |
   | Aquilo | 300 | 15 | 10 | 1 |
   | Platform | 0 | 0 | — | — |

3. **A placement-locked entity**, where the process needs a building that only
   works in one environment.

### The rule that survives all of it

> **A lock must describe a physical fact about the place, never name it.**

Pressure, gravity, magnetic field, an ingredient that has no container — these
are readable, and a player can reason about them. "Craftable only on Gleba"
teaches nothing and is arbitrary even when it produces the same outcome. Vanilla
never does it, and neither does this mod.

## 2. Both planets sending is the default, not the law

A pair should not be a supply route with a mine at one end. When material moves
only one way, the tree is really one planet's chain with an import, and the
partner is interchangeable.

So **two-way is the default, and the strongest form is a round trip** — something
leaves, comes back changed, and leaves again, which keeps both legs alive for as
long as the player uses the tree rather than only while they build it.

But it is not a law. Some pairings are honestly one-directional, and forcing a
return leg onto them invents a reason to ship something back. Where a tree is
one-way, that has to be a deliberate answer to "what does the receiving planet
give back," not an omission — usually the answer is that it gives back the
capstone itself, which only it can assemble.

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

## 8. The capstone product has to reach the Core

The endgame consumes a product from every capstone, on a planet at the far end
of the longest supply line in the game. That does not dictate what the product
*is* — it dictates that **getting it there is part of the tree's design, not an
afterthought**.

A product that spoils is allowed, and may well be the point: a perishable
capstone turns its delivery into a race and gives its tree a character none of
the others have. What is not allowed is designing one without deciding how it
survives the trip. If it spoils, the tree owns that problem — a preserved form,
a cold chain, a shorter-lived intermediate refreshed at a depot, or a Core line
that accepts the spoiled result as a legitimate input.

The one thing to get right mechanically is **weight**. The engine derives it
from the recipe when it is not set, and the default is 100 against a rocket's
1,000,000 lift — 10,000 items per rocket. A fluid-heavy recipe derives freight
that is nearly free, which quietly deletes the logistics the tree exists to
create. Every capstone product sets its weight deliberately, because that number
*is* the cost of the endgame's supply line.

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
- [ ] Does every lock describe a physical property or an immovable ingredient,
      rather than naming a planet? *(§1)*
- [ ] Does material move both ways — or, if not, is the one-way shape a
      deliberate answer rather than an omission? *(§2)*
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
- [ ] Does the capstone product have a decided route to the Core, including an
      answer for spoilage if it spoils, and an explicit weight? *(§8)*
- [ ] Could a player work out from the recipes why the crossing is necessary?
      *(§9)*
