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
2. **A building constructed from that product.**

The building is where the tree pays off. It should **use the elements of the
tree that caps it** — its materials, its fluids, its mechanic — so that it reads
as the conclusion of that specific chain rather than a generic reward. It has to
be **useful at the moment the player earns it**, and **useful again in the
endgame**, when the final production line is being supplied.

**It must not threaten vanilla Space Age balance.** A capstone building is a new
option, never a strict upgrade to something vanilla already provides. If
installing one makes a vanilla building pointless, it is wrong.

The capstone is also what proves both halves of the pair were built out: the
product cannot exist unless material from both planets met somewhere in the
chain.

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

**The game is won on completion, not on arrival.** Reaching the Core is not the
ending; the ending is the final production line running and delivering. Arrival
only earns the right to start building it.

## The engine hook for the ending

Space Age's victory is not hard-coded. It fires from
`core/lualib/space-finish-script.lua` when a space platform's
`last_visited_space_location` matches `victory_location`, which defaults to
`solar-system-edge`, and it exposes a remote interface:

```lua
remote.call("space_finish_script", "set_no_victory", true)
```

Since the ending is completion rather than arrival, the mod **disables the
vanilla trigger** and calls `game.set_game_state{game_finished = true,
player_won = true, can_continue = true, victorious_force = ...}` itself when the
final line delivers. `set_victory_location` exists too, but pointing it at the
Core would fire the ending the moment a platform reached orbit, which is exactly
what this design does not want.

## Which five pairs

Two rules settle the shape:

- **Every planet appears in exactly two trees.** With five planets and five
  pairs that makes a closed loop, and it means no world is only ever a supplier
  to another — each one both sends and receives.
- **No pair reuses existing work.** The five are designed fresh.

The working set:

| Pair | Available after | Theme, in one phrase |
|---|---|---|
| **Nauvis ↔ Vulcanus** | Vulcanus | The first cross-planet chain a player meets |
| **Nauvis ↔ Gleba** | Gleba | Perishable material against Nauvis logistics |
| **Fulgora ↔ Gleba** | both | Scrap electronics against biology |
| **Vulcanus ↔ Aquilo** | Aquilo | The temperature extremes of the system |
| **Fulgora ↔ Aquilo** | Aquilo | Electromagnetics against cryogenics |

That gives two trees available in the early-to-mid game, one in the middle, and
two after Aquilo — which is also where the endgame sits, so the run-up to the
Core has content of its own.

**The consequence to be explicit about:** Vulcanus ↔ Fulgora is not among them,
and that is the pair the repository has already implemented. The existing
technologies, recipes and the Quench Turbine fall outside the five. They are
either deleted, or kept as a sixth tree outside the endgame requirement — that
choice is not made here.

## Still open

- **What each capstone building is.** Per-pair variety is the intent; each is
  decided with its own tree.
- **What the final production line on the Core actually makes**, and what the
  new Core and promethium-space materials are.
