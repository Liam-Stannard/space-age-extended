# The Tree Pattern

**Preliminary — a first proposal, written to be argued with.** The parts marked
*open* are the ones I am least sure about.

Five trees get designed one at a time, months apart, and they still have to feel
like one mod. That only works if they share a shape. This document is that shape:
what a tree is made of, in what order, and what every tree owes the endgame.

---

## 1. Anatomy

A tree is four stages and 4–10 technologies.

### Stage 1 — The opening (1 technology)

One recipe that cannot be completed without material from the other planet. It
should be **cheap, early in the tree, and slightly annoying** — the player has to
ship something before they have any infrastructure for shipping it.

Its job is to teach the pairing in one recipe. A player who researches this and
nothing else should already understand what these two worlds do for each other.

### Stage 2 — The two chains (2–5 technologies)

Each planet builds out its own side: processing the import, refining what it
sends, dealing with what comes out that nobody asked for. This is the bulk of the
tree and where its factory-design problems live.

The two chains should be **researchable in either order**, so a player who has
one planet developed further than the other is not blocked.

### Stage 3 — The convergence (1 technology)

One technology whose prerequisites are the last technology of *both* chains. It
unlocks the intermediate that only exists when both sides are running — the point
where the tree stops being two chains and becomes one.

This is the tree's structural proof: the technology graph itself shows that both
halves were built.

### Stage 4 — The capstone (1 technology)

Unlocks two things:

- **the product** — the item the tree exists to make, and
- **the building** — made from that product, using the tree's own materials.

---

## 2. The crossing

Every tree names, in one sentence each:

- **What must move, and why it cannot be made locally**, tracing to one of the
  four anchors in [the principles](01-principles.md#the-four-honest-anchors).
- **What moves the other way**, or an honest statement of why the tree is
  one-directional.

**Try not to use the same anchor twice.** One tree built on an immovable fluid,
one on a placement-locked building, one on a native process, one on a recipe
condition — five trees leaning on four anchors will repeat one of them, but they
should not repeat two.

This is an effort, not a rule. **Where the anchor and the theme disagree, the
theme wins**: a tree that fits its two worlds and reuses an anchor is better than
one that reaches for an unused anchor and stops making sense. Note the
duplication in the register and move on.

## 3. The one new mechanic

Each tree may introduce **one thing that is not just recipes** — a fluid that
behaves oddly, a material that changes state in transit, a building with a
mechanic no vanilla building has. One, not several, and it must be the thing the
pairing suggests rather than a mechanic looking for a home.

A tree with no new mechanic at all is acceptable if its chains are interesting;
a tree with three is not a tree, it is a mod of its own.

## 4. The capstone contract

The capstone is the only part of a tree that the rest of the mod depends on, so
it is the part with rules.

**The product**

- It is what the final production line on the Core consumes, so the tree decides
  how it gets there — including an answer for spoilage, if it spoils.
- It has an explicit weight. That number is the freight cost of the endgame.
- It is consumed by the tree's own building too, so demand for it never stops:
  building more of the building costs more of the product.

**The building**

- **Made from the product**, so it cannot exist before the tree is finished.
- **Uses the tree's materials and mechanic**, so it reads as that chain's
  conclusion rather than a generic reward.
- **Never a strict upgrade** to anything vanilla provides.

A capstone building has a life across the whole rest of the game, in four steps:

1. **Useful in the mid-game**, where the tree unlocks, for its own sake. A player
   who never goes near the Core should still want it.
2. **Useful in getting to the Core** — the same capability, applied to the
   problem of crossing a distance nothing else crosses.
3. **Useful in surviving the Core**, where almost nothing works and everything
   arrives from somewhere else.
4. **Expandable out there.** A building may gain a further use on the way to or
   on the Core — an extension, a second recipe, a mode that only makes sense at
   the far end.

Step 4 is what keeps the endgame from being a checklist: the buildings the player
already knows become the tools they solve the Core with, rather than five
trophies plus a new toolkit.

## 5. One reserved problem per tree

Five buildings that each do a different thing make a toolkit. Five that all
improve throughput make a shopping list. So the problems are **reserved up
front**, like the pairs, rather than discovered on the fourth tree when three are
already built.

Each problem is a thing the player struggles with in the mid-game *and* a thing
that stands between them and the Core:

| Problem | Mid-game version | Endgame version |
|---|---|---|
| **Power where the usual sources fail** | Generating where solar is poor and fuel has to be shipped | The Core has no sun worth the name and nothing burns |
| **Moving material over distance** | The cost and friction of interplanetary freight | A supply line longer than anything in the game |
| **Protection from what is out there** | Surviving what attacks a platform or a base | The field between the Edge and the Core |
| **Refining what is locally available** | Turning a local waste stream into something worth having | Nothing arrives that was not made from what is out there |
| **Keeping material viable** | Spoilage, decay, temperature, things that expire in transit | A journey long enough that time itself is the hazard |

Provisional assignment, confirmed when each tree is designed:

| Problem | Tree | Why that pairing |
|---|---|---|
| Power | Nauvis ↔ Vulcanus | Vulcanus is heat and metal; Nauvis is fuel and industry |
| Moving material | Fulgora ↔ Aquilo | Electromagnetics and superconduction is how you throw something a long way |
| Protection | Nauvis ↔ Gleba | Nauvis is where the player learned to be attacked; Gleba is what does the attacking best |
| Refining locally | Vulcanus ↔ Fulgora | The system's two recycling worlds — lava casting and scrap |
| Keeping material viable | Gleba ↔ Aquilo | The world that spoils against the world that freezes |

If a tree's theme insists on a different building, **swap two slots rather than
duplicating one**. Two trees solving the same problem is the failure this table
exists to prevent.

## 6. What a tree owes the Core

Every tree contributes exactly one product to the final production line. Beyond
that:

- The tree should still be worth building for a player who has not reached the
  Core, which is most players most of the time.
- It should leave behind something that keeps running: the product's demand
  continues, so the chain does not become a one-off unlock.

---

## 7. The register

| Pair | Available after | Problem reserved | Anchor | Mechanic | Capstone | Status |
|---|---|---|---|---|---|---|
| Nauvis ↔ Vulcanus | Vulcanus | Power | — | — | — | Not designed |
| Nauvis ↔ Gleba | Gleba | Protection | — | — | — | Not designed |
| Vulcanus ↔ Fulgora | both | Refining locally | — | — | — | Not designed |
| Gleba ↔ Aquilo | Aquilo | Keeping material viable | — | — | — | Not designed |
| Fulgora ↔ Aquilo | Aquilo | Moving material | — | — | — | Not designed |

Each row fills in as its tree is designed. The empty columns are the decisions
this document exists to force: a tree is not ready while any of them is blank.

## 8. The per-tree document

Each `design/trees/<pair>.md` follows the same headings, so the five can be read
against each other:

```
1. The pairing          what each world contributes that the other cannot get
2. The crossing         what moves, both ways, and the anchor that forces it
3. The opening          stage 1, in one recipe
4. <Planet A>'s chain   recipes, buildings, byproducts
5. <Planet B>'s chain   the same
6. The convergence      the intermediate that needs both
7. The capstone         the product and the building
8. Technologies         the ladder, with prerequisites
9. What it owes the Core how the product gets there
10. Open questions      what is not decided
```
