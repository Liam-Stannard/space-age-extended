# The Core

The mod's destination: a planet past the Shattered Planet, reached down a
corridor flown on space platforms. Arrival is not the ending — **the game is won
by completing a production line on and above the Core**, and that line consumes
one product from every capstone plus materials that exist nowhere else.

---

## 1. What the Core is

The intact metallic heart of the destroyed world. A frozen crust over a
still-hot iron-nickel interior, no atmosphere worth the name, and the densest
body in the system.

### Surface properties

| Property | Value | Consequence |
|---|---|---|
| **pressure** | **5** | Rocket silo works (needs ≥1). **Refused:** boiler, stone and steel furnace, heating tower, roboport, burner inserter — all need ≥10. Nothing burns here |
| **gravity** | **50** | The heaviest world in the game. Everything gravity-gated works: chests (≥0.1), rails, vehicles, cargo landing pad (≥1) |
| **magnetic-field** | **0** | A dead dynamo. No electromagnetic plant or recycler can be *manufactured* here |
| **solar-power** | **0** | Solar panels produce nothing at all, rather than a trickle |
| **day-night-cycle** | none / very long | A sky that does not move |

**Pressure 5 is the load-bearing number.** It gives the Core its character in a
single value: no combustion of any kind, and no roboport networks. Note that the
conditions live on *those specific vanilla prototypes* — a mod could add a burner
with no conditions at all. This mod deliberately does not. Nothing burns on the
Core, and the heat network below is why that costs the player no capability.

Working at pressure 5 without any change: foundry, electromagnetic plant,
biochamber, recycler, chemical plant, assembler, electric furnace, nuclear
reactor, heat exchanger, steam turbine, drills, labs, accumulators, rails,
chests, cargo landing pad.

### Life and hazard

**No living enemies.** Nothing ever grew here.

The hazard is **arc storms** — the remnant dynamo discharging through a metallic
crust. Damage arrives as weather rather than as an attack, and the answer is
infrastructure, not turrets: attractors that catch a strike and **bank it as
power**. It is Fulgora's lesson on a world that looks nothing like Fulgora, and
it means the thing that damages you is also the thing that runs you, once you
have built for it.

## 2. Resources

Three things, all sited, none of them enough.

### Metal ore — rich, scattered, finite

Extremely rich patches, spread widely, that genuinely run out. With no roboport
network available at first, that makes **belts and rails** the answer, and it
makes the Core a place the player expands across rather than a single pad they
build on.

### Melt vents — a fluid, infinite but declining

Scattered vents tapped by a dedicated pump, yielding **core melt**: hot,
metal-bearing, and **unbarrelable**, so it can never leave the planet. Rate
declines with draw the way crude oil does, so a vent is permanent, worth building
around, and eventually wants company.

**Melt has two uses, and they compete.**

| Path | Product |
|---|---|
| Cast it | The Core's own solid — the feedstock of the final line |
| Tap its heat | Heat into a network → exchangers → turbines → surface power |

Every megawatt is metal not cast, and the final line needs both. That competition
for one sited, rate-limited resource is the Core's central factory problem, and
nothing in vanilla poses it.

### Gas vents — volatiles, rare

The planet's trapped gas: the only source of **pressure and oxidiser** on an
airless world. Its own siting problem, since it is rarer than melt. It is what
makes sealed processes possible — including the pressurised roboport (below) —
and it supplies oxidiser to anything leaving again.

### What the Core never has

**No carbon, no water, no organics.** No coal, no oil, nothing that ever lived.

Plastics, explosives, anything biological and every drop of water arrive from
outside — ice caught on the corridor, organics from Gleba, the rest by freight.
The vents give the Core an industry. They do not give it independence, and that
is deliberate: the corridor has to keep running after the megaproject is built.

## 3. Why the Core can never become self-sufficient

The structural guarantee, and the reason the whole mod holds together:

> **Every capstone product can only be made on the two planets whose tree
> produces it**, because each is anchored on a material or a condition exclusive
> to those worlds. The final line consumes all five.

So the Core is permanently dependent by construction, not by a rule. A player
standing on it with a complete factory still needs Vulcanus, Fulgora, Gleba and
Aquilo running, and still needs the corridor carrying their output the whole
distance. Finishing the game does not switch the supply line off; it is what the
supply line was for.

## 4. The line spans surface and orbit

Part of the final production chain is completed on a **space platform in orbit
around the Core**, not on the ground. 2.1's platform-to-platform transfer, plus
cargo pods to and from the surface, make that a real logistics loop rather than a
scripted hand-off.

The split is enforced by the engine, exactly as vanilla enforces its own:

- **Orbit-only steps** take `surface_conditions` of gravity 0 — the same lock
  vanilla puts on space science, thruster fuel and promethium science.
- **Surface-only steps** need what only the ground has: the melt, the heat, the
  ore, the volatiles.
- The **asteroid work happens in orbit by necessity** — crushers, collectors and
  thrusters are all space-only prototypes, so anything won from promethium space
  is processed above the planet and dropped.

That gives the endgame a shape no earlier part of the game has: a factory the
player has to run in two places at once, with a lift between them, where neither
half can complete a single item alone.

## 5. The final production line

The Core has **its own tech tree** — the sixth — and its own multi-stage
production line. This is the mod's largest chain, and the only one that cannot be
built anywhere else.

**The five capstone products are inputs to it, not parts of the goal.** Each
arrives from its own pair of planets and is *consumed* to make an intermediate
that only the Core can produce, because every intermediate also needs something
local: the melt, the heat, the volatiles, or a step that only runs in orbit.

```
five capstone products            core melt · heat · volatiles · orbit steps
        \                                 /
         +-------- intermediates --------+        (stage 1: each capstone
                        |                          consumed with a local input)
                        v
                  end products                    (stage 2: intermediates
                        |                          combined; the Core's own goods)
                        v
              Field Coil Segments                 (stage 3: built only from
                        |                          end products)
                        v
                 Ignition Array
```

Three consequences worth being explicit about:

- **No capstone touches the segment directly.** The dependency runs through two
  stages of local processing, so the Core is a factory rather than an assembly
  point, and the final part is genuinely the Core's own product.
- **Every stage is gated by a Core technology**, so arrival is the beginning of a
  progression rather than the end of one.
- **The chain spans surface and orbit** at more than one stage (§4), so both
  halves are live for the whole endgame rather than at a single hand-off.

## 6. The completion goal — restarting the dynamo

The Core's field is dead: `magnetic-field` reads 0, and the arc storms are what a
failing dynamo looks like. **The mod is completed by restarting it.**

That is the one ending whose meaning depends on being *here*. It explains the
hazard the player has been building against, it cannot be done anywhere else, and
it leaves something behind that still needs feeding.

### The Ignition Array

A `rocket-silo`-derived structure, so it behaves the way the player already
understands one: it accumulates parts, shows its progress, and fires once.

| | Vanilla rocket silo | Ignition Array |
|---|---|---|
| Parts required | 50 | **100** (starting point, to tune) |
| Part recipe | processing unit + LDS + rocket fuel, 3s | Field Coil Segment, from Core end products |
| Power | 250 kW idle, 3.99 MW active | An order of magnitude more, deliberately |
| Placement | pressure ≥ 1 | pressure 1–9 — the Core and nowhere else |

**Power is the point of the number.** The array should draw hard enough that it
forces the Core's central tension to its limit: every megawatt it takes is melt
that was not cast into the billets it also needs.

**Rate is set by maturation, not by machines.** Widen the aging floor or wait —
the one production problem in the game that more assemblers cannot solve.

### Winning

The array launches, the mod catches `on_rocket_launched` for that entity and
calls `game.set_game_state{game_finished = true, player_won = true,
can_continue = true}`. Vanilla's Solar System Edge victory is disabled at init
through the `space_finish_script` remote interface's `set_no_victory`.

### What it leaves behind

A restarted field **decays without upkeep**, so the array becomes a permanent
consumer: windings replaced forever, which keeps all five trees and the whole
corridor running after the credits. That is the difference between an ending and
a switch-off.

## 7. Maturation as the Core's central process

The one mechanic carried in from the trees. A billet cast from core melt is not
finished when it leaves the mould — it has to **age** before it becomes the
material the final line needs.

Implemented with the engine's own spoilage timer pointing at a *better* item
rather than a worse one; nothing requires the destination of `spoil_result` to be
a downgrade.

It means the last step cannot be rushed, only widened — the player buys
throughput with floor space and patience instead of with more machines, which is
a different problem from every other one the game has set them.

## 8. Bots are earned

Personal roboports work at pressure 5 — verified, the equipment carries no
surface conditions — so the player can blueprint-build from their armour on day
one, slowly, within their own radius. What does not exist is a network.

A **pressurised roboport**, unlocked by a technology on the Core and built from
capstone products and volatiles, restores it. Give it `surface_conditions` of
pressure 1–9 and it works here and **nowhere else in the game**: not on platforms
(pressure 0), not on any vanilla planet (Aquilo is the lowest at 300). It is a
new building that competes with nothing, and it turns bots from an assumption
into a milestone.

## 9. Still open

- **How rich, and how scattered**, in numbers.
- **What the intermediates and end products actually are** — the two middle
  stages of §5 are named but not designed.
- **Whether the sixth tech tree needs its own science pack**, or researches on
  packs the player already makes. A Core pack would fit the vision's "new items
  found on the Core or in promethium space"; existing packs keep the footprint
  smaller. Either way the *physical* gate is the recipe conditions, not the
  research.
- **What the promethium-space material is**, and how it enters the chain.
- **Whether volatiles have a third use** beyond oxidiser and pressurisation.
- **What gates the pressurised roboport** within the Core tree.
- **How many segments**, and how the 100 divides across the aging floor.
