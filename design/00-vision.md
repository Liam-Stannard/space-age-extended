# Vision

An expansion to Factorio: Space Age 2.1 in which the player builds **cross-planetary
production lines between pairs of planets**.

Vanilla gives each world a self-contained tech tree. A factory on Vulcanus and a
factory on Fulgora never need each other; rockets carry finished goods, not
dependencies. This mod makes the pairs themselves productive — a chain that only
completes when material from both worlds meets in the same recipe.

---

## Five pairs

There are ten possible pairs across Nauvis, Vulcanus, Fulgora, Gleba and
Aquilo. **Five of them get trees**, at least for now — enough that the endgame
draws on the whole system, few enough that each tree can be built properly and
actually played.

## A tree per pair

Each chosen pair gets a **small tree of its own**:

- **Around 4–10 technologies.** Small enough to be finished, not a second
  planetary tech tree bolted onto the first.
- **Its own production lines**, spanning both worlds, with material physically
  moving between them.
- **New mechanics, buildings or items where the pairing calls for them** —
  themed to those two planets specifically, and to the chain that leads up to
  them. What Vulcanus and Fulgora do together should not be re-skinnable onto
  another pair.

## When a tree becomes available

Progression follows Space Age's own. **A pair's tree opens once the player has
completed the vanilla tech trees of both its planets.** Nothing new is gated on
anything but the vanilla progress the player would be making anyway.

That falls out naturally into an order: pairs among the early and mid planets
become available as the player finishes each of them, and **Aquilo's pairs come
last**, because Aquilo itself does. The mod's own content spreads across the
back half of a normal playthrough rather than arriving all at once.

## The capstone

Every tree ends in a **capstone technology** that unlocks two things:

1. **A product** — the item the whole tree exists to make.
2. **An entity built from that product**, which is genuinely useful to the player
   as they progress through the mod.

The capstone is what proves both halves of the pair were built out, and the
entity is what makes finishing a tree worth doing at the time rather than only
at the end.

## The endgame

The endgame lies **beyond the Shattered Planet, at the Core** — a real planet
with a landable surface and its own orbit, past the point where vanilla's route
gives out.

**The win condition moves there.** Vanilla's ending is the Solar System Edge;
the mod's is the Core, and the game is finished by what the player builds on it.
Getting there is the journey; the production line there is the ending. On the Core
the player builds a **final, complex production line** — the largest in the mod —
whose inputs are:

- **an item from every capstone**, so the final chain cannot be built without
  having built the pairs, and
- **new items found only out there**, on the Core itself or in the promethium
  space between it and the rest of the system.

That is the shape of the whole mod in one line: **each pair teaches you to move
material between two worlds; the Core asks you to do it from every world at
once, at the far end of the longest supply line in the game.**

---

## Consequences worth being clear about

**Every tree built is a tree required.** Because the final production line
consumes an item from every capstone, none of the five is skippable. That is
what makes the pairs add up to an ending rather than a menu — and it means a
tree that plays badly blocks the ending instead of being ignored, so each one
has to be played before the next is designed.

**The win condition moving is a real change to vanilla**, and the only one the
mod makes. Everything else is additive: a player can still reach the Solar
System Edge exactly as before, it simply is not where the game ends any more.

## The engine hook for the ending

Space Age's victory is not hard-coded. It fires from
`core/lualib/space-finish-script.lua` when a space platform's
`last_visited_space_location` matches `victory_location`, which defaults to
`solar-system-edge` — and it exposes a remote interface to move it:

```lua
remote.call("space_finish_script", "set_victory_location", "<location>")
```

So relocating the ending to the Core is directly supported, with one caveat:
that hook fires on **arrival in orbit**, not on finishing anything. If the
ending is to be the final production line rather than the trip, the mod sets
`set_no_victory(true)` and calls `game.set_game_state` itself when the line
delivers. Which of those two the ending is remains to be decided.

## Still open

- **Which five pairs.** One candidate worth considering is a closed loop —
  Nauvis↔Vulcanus, Vulcanus↔Fulgora, Fulgora↔Gleba, Gleba↔Aquilo,
  Aquilo↔Nauvis — because every planet then appears in exactly two trees, no
  world becomes a mere supplier, and the availability order spreads across the
  playthrough. Not decided.
- **What the capstone entities are.** Per-pair variety is the intent: some
  planetside, some on platforms, whatever suits that pairing. What each one
  actually is gets decided with its tree.
- **Whether the ending is arrival or completion** — see above.
