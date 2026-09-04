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

## 3. Every tree teaches one new mechanic

**The mod creates its own problems rather than borrowing vanilla's.** Each tree
introduces exactly one new rule the player has to design around — a material that
changes with time, a process that cannot be buffered, a resource that behaves
unlike anything vanilla has — and that rule *is* the tree's problem.

One per tree, and it is mandatory. A tree with no new mechanic is a set of
recipes; a tree with three is a mod of its own.

Three requirements:

1. **It comes from the pairing.** The mechanic should be the thing those two
   worlds together suggest, not a mechanic looking for a home.
2. **It is taught alone.** The player meets it in that tree, in isolation, with
   room to fail at it cheaply.
3. **It is load-bearing at the end.** The Core, or the corridor to it, requires
   it — so learning it was not a detour. The endgame is where the five combine.

The mechanics themselves are in [mechanics.md](mechanics.md).

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

## 5. One reserved mechanic per tree

Five mechanics that each teach a different lesson make a toolkit. Five that are
variations on one idea make a theme. So mechanics are **reserved up front**, like
the pairs, rather than discovered on the fourth tree when three are built.

The test for a candidate mechanic:

- **Is it a new rule, or a new recipe?** If the player's existing instincts still
  work, it is content rather than a mechanic.
- **Does it belong to those two worlds?** If it could be moved to another pair
  unchanged, the pairing is doing no work.
- **Is it implementable in prototypes?** Preferably with no control-stage script.
- **Where does it land at the end** — on the corridor platform, or on the Core?
  It has to be one of the two, or the tree is a side quest.
- **Does it collide with another tree's mechanic?** If two trees teach the same
  lesson, swap one out rather than running both.

**Power is not on the list.** Vanilla covers it to the Edge and fusion answers
Aquilo; it only becomes hard past the Edge, where there is no sun and nothing
burns. That is solved on the corridor by a new asteroid type, not by a pair —
see [the problem catalogue](problems.md#power-is-not-one-of-the-five).

## 6. What a tree owes the Core

Every tree contributes exactly one product to the final production line. Beyond
that:

- The tree should still be worth building for a player who has not reached the
  Core, which is most players most of the time.
- It should leave behind something that keeps running: the product's demand
  continues, so the chain does not become a one-off unlock.

---

## 7. The register

| Pair | Available after | Mechanic taught | Anchor | Capstone product | Endgame role | Status |
|---|---|---|---|---|---|---|
| Vulcanus ↔ Fulgora | both | — | — | **Magnetar alloy** | The coil's magnetic core | Capstone chosen |
| **Vulcanus ↔ Gleba** | both | **Maturation** | — | **Cultured alloy** | The coil's frame; also ripens on the corridor run | Mechanic + capstone |
| Fulgora ↔ Gleba | both | — | — | **Bio-polymer** | The coil's insulation | Capstone chosen |
| Fulgora ↔ Aquilo | Aquilo | — | — | **Superconducting winding** | The coil's conductor | Capstone chosen |
| Gleba ↔ Aquilo | Aquilo | — | — | **Cryoprotectant fluid** | The coil's coolant | Capstone chosen |

**The capstones are one decomposition.** A field coil has five parts — conductor,
magnetic core, insulation, coolant, frame — and there are five trees, so each
supplies one. See [the Core](05-the-core.md#stage-1--the-five-integrations) for
how each is integrated through a different local input.

Each tree still owes a **building** made from its product, and a mechanic:
four of the five mechanics are unchosen.

Vulcanus and Fulgora appear twice, Gleba and Fulgora three times; with four
worlds and five pairs the even loop is not available, and Fulgora carrying three
is the price of keeping the mid-game populated. Watch that Fulgora does not end
up doing the same job in all three.

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
