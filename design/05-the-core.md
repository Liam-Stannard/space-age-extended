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
Core, and it costs the player no capability: surface power comes from the arc
storms and from steam raised off the melt (§2), neither of which needs a flame.

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

**Kamacite ore** — the real iron-nickel alloy of meteorite cores. Extremely rich
patches, spread widely, that genuinely run out. With no roboport
network available at first, that makes **belts and rails** the answer, and it
makes the Core a place the player expands across rather than a single pad they
build on.

### Melt vents — a fluid, infinite but declining

Scattered vents tapped by a **vent pump**, yielding **molten kamacite**: hot,
metal-bearing, and **unbarrelable**, so it can never leave the planet. Rate
declines with draw the way crude oil does, so a vent is permanent, worth building
around, and eventually wants company.

**Drawing melt costs helium-3.** The melt vent requires an input of **helium-3**
to draw, the way vanilla's uranium ore requires 10 sulfuric acid per mining
operation (`minable.required_fluid`). The rarer resource therefore throttles the
abundant one, and the two vent types become a single coupled siting problem
rather than two independent ones.

*To verify:* vanilla only uses `required_fluid` on a solid resource. A vent pump
needs both an input and an output fluid box, which the mining drill prototype
supports, but no vanilla prototype does both at once — worth a spike before this
is depended on.

**Melt splits between metal and power, and the split is a recipe choice.**
Settling comes in two forms: one yields more settled melt and a little steam, the
other yields less melt and a great deal of steam at 500 °C, which drives ordinary
turbines. Recipes may output a fluid at a fixed temperature — vanilla's
`acid-neutralisation` emits steam at exactly 500 — so this needs no heat network,
no heat pipes and nothing borrowed from Aquilo.

Every megawatt is metal not cast, and the final line needs both. That competition
for one sited, rate-limited resource is the Core's central factory problem, and
nothing in vanilla poses it.

### Gas vents — volatiles, rare

**Helium-3**: primordial gas trapped since the planet formed, which is genuinely
what a planetary interior holds. Inert, cryogenic and precious — a scarce reagent
rather than a bulk utility, which is the right character for the rarer of the two
vents.

It is doubly load-bearing: melt cannot be drawn without it, so the rare resource
throttles the abundant one. Beyond that it is the atmosphere for sealed processes
(including the sealed roboport, §9) and an ingredient in the science pack.

**What it is not** is a source of oxygen. The Core has no oxidiser of its own,
and nothing there burns.

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

**The round trip is physically motivated, not a logistics rule.** The Core has
the highest gravity in the game and the platform above it has none, and the same
material needs both:

- **On the surface, weight separates.** Molten kamacite settles under 50g into a
  dense fraction and dross, with no energy and no reagent.
- **In orbit, nothing settles.** The same material alloys evenly precisely
  because gravity cannot pull it apart again.

So the player goes up to escape gravity and comes back down to use it. The split
is enforced by the engine exactly as vanilla enforces its own:

- **Orbit-only steps** take `surface_conditions` of gravity 0 — the same lock
  vanilla puts on space science, thruster fuel and promethium science.
- **Surface-only steps** take gravity ≥ 45, which is the Core alone (Vulcanus,
  the next heaviest, is exactly 40).
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
local: the melt, the whiskers, the helium-3, or a step that only runs in orbit.

```
five capstone products         molten kamacite · whiskers · helium-3 · orbit
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

### Metal carbonyl — the chemistry that arrives later

Metals dissolve into carbon monoxide as a gas and deposit again as ultra-pure
powder when it decomposes. It is real industrial chemistry, and mechanically it
is the most interesting thing available to the Core: **metal that travels
through pipes.**

It cannot be a vent product, because forming it needs carbon and the Core has
none — so it is an intermediate unlocked later and built from **imported
carbon**. That is a feature rather than an obstacle: it gives the corridor a
permanent cargo that has nothing to do with the capstones, and it means the
Core's best chemistry is paid for with freight from home.

## 6. The sixth tech tree

The Core carries the mod's **sixth technology tree** — at least ten technologies,
and the only tree whose research currency is manufactured on site.

### Geodynamic science

A new science pack, crafted from the **intermediates** of the Core's own line
(§5) — the same intermediates the end products need.

> Research and construction draw on one supply. **Every pack burned is a segment
> delayed.**

That is the endgame's central decision, one layer above the melt's
metal-or-steam split, and it is why the pack's cost is the most important number
in the tree.
Start it deliberately expensive and tune down: if the pack is cheap, research is
a formality and the endgame collapses into a segment grind.

*Geodynamic* after geodynamics, the study of planetary interiors and the fields
they generate — which is precisely what the Ignition Array exists to restart. It
also matches vanilla's habit of naming a pack after a field of study:
metallurgic, electromagnetic, agricultural, cryogenic.

### The recipe

**Geodynamic science pack** — 20 s, in an assembler, recipe locked to pressure
1–9. One recipe, not five alternates.

| Ingredient | Why it is there |
|---|---|
| **Two fixed intermediates** | The competition with construction: every pack is a Field Coil Segment delayed |
| **Kamacite whiskers** | Ties research rate to growing *area*, so knowledge costs ground |
| **Homogenised alloy** | Made in orbit only, so the lift is load-bearing from the first technology |
| **Helium-3** | From the rarer vent, which already throttles the melt |

**Two intermediates rather than five.** Research opens once two specific trees
are delivering, while the Field Coil Segment still needs all five. That keeps the
goal maximally demanding without letting one lagging tree freeze the entire Core
tech tree — and it means the two trees named here are the ones a player is
pushed to finish first.

The pack touches three of the Core's four mechanics — settling, growth and
orbital homogenisation — and leaves **cold welding** to the Field Coil Segment.
Research uses the material sciences; construction uses the joining.

Three rules:

- **Locked to pressure 1–9.** Labs carry no surface conditions, so research
  itself can happen anywhere; the *pack* cannot be made anywhere but here. The
  tree therefore has to be advanced by a factory genuinely running on the Core.
  Vanilla gates its own packs the same way — electromagnetic at magnetic field
  99, metallurgic at pressure 4000, cryogenic at 100–600.
- **It does not mature.** Maturation belongs to the billet. Putting it on
  research as well would make every rate in the endgame a function of floor
  space, which is one turn of the screw too many.
- **It should probably require one orbit-made intermediate**, so the platform
  overhead is load-bearing from the first technology rather than switching on at
  the end. Open, but preferred.

### The ladder

Fifteen technologies in five tiers — comfortably past the ten-technology floor,
and shaped so the endgame builds rather than arriving flat.

| Tier | Technologies | Notes |
|---|---|---|
| **0 — Foothold** | Core Survey (vent pump, working the ore) · Gravity Settling (the melt split, and casting) · Whisker Beds (tiles, seeding, harvest) · Helium Extraction (the gas vent) | Researched on packs the player already makes, since no geodynamic pack exists yet |
| **1 — Integration** | Five technologies, one per capstone: each unlocks the recipe consuming that product with a local input to make an intermediate | **Researchable in any order**, so a player whose Gleba line is ahead of their Aquilo line is never blocked |
| **2 — Geodynamic Science** | The pack itself | Unlocked once the first intermediate exists; required by everything after |
| **3 — The Core's own goods** | The end products, and the **pressurised roboport** (§9) | The mid-tree milestone: after hours of belts and personal bots, the Core starts working like a factory |
| **4 — The goal** | Field Coil Segment · Ignition Array | Costs escalate steeply — the Array's research alone running into thousands of packs |

### Three things this shape gets right

**The pack cannot be first.** It is made from intermediates, and intermediates
need a capstone product plus a local input — so the opening hours run on vanilla
packs and local bootstrapping, and geodynamic science arrives only once the
corridor is genuinely delivering. The tree's currency is earned rather than
granted on landing.

**The climax is the last three technologies.** With costs escalating steeply, the
ramp is felt rather than announced, and the final stretch becomes one sustained
decision about how to split a single production line between knowing more and
building more.

**The five integration technologies must not be five of the same technology.**
They share a shape — capstone plus local input yields intermediate — so what
saves them is that each integrates through a **different local input**: one
through the settling line, one through the helium, one through an orbit-only step, one
through matured billet, one through raw melt. Then each capstone lands somewhere
different in the Core's economy, and five reads as five.

## 7. The completion goal — restarting the dynamo

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

**Rate is set by time and area, not by machines.** Settling takes as long as it
takes, whiskers grow at the rate they grow, and cold welding cannot be hurried —
so the answer to "faster" is more floor, not better machines. That is the one
production problem in the game more assemblers cannot solve.

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

## 8. The Core's own mechanics

Four rules that exist nowhere else in the game. Between them they give the Core a
production identity built on **weight, vacuum, time and the absence of gravity**,
rather than on the heat and electricity every other world runs on.

### Gravity settling — surface only

Molten kamacite separates into a dense fraction and dross **because it is heavy**.
No energy, no reagent, no catalyst: a tall vessel and time. It works here because
the Core's gravity is 50, and nowhere else because Vulcanus, the next heaviest
world, is 40.

*Implementation:* `surface_conditions` gravity ≥ 45 on the recipe. Nothing in
vanilla uses gravity as a production condition — only as a space-or-ground
switch.

### Orbital homogenisation — orbit only

The same material, taken up to the platform, alloys **evenly precisely because
nothing settles**. Gravity is the thing being escaped.

*Implementation:* `surface_conditions` gravity 0, the same lock vanilla puts on
space science. Paired with settling, it is what makes the surface/orbit lift a
permanent loop rather than a hand-off (§4).

### Cold welding — vacuum

In real vacuum, clean metal surfaces bond on contact. Joining costs almost no
power and cannot be hurried: the machine is a clamp, not a furnace.

*Implementation:* `surface_conditions` pressure ≤ 9 with a long
`energy_required` and negligible machine energy usage. A production step whose
cost is **place and patience** rather than throughput — the game has never had
one.

### Whisker growth — surface, on tiles

Kamacite whiskers crystallise out of the melt over time on seeded plates, and are
harvested like a crop. Growing area, not machine count, is the throughput.

*Implementation:* the `plant` prototype with `growth_ticks` and a tile
restriction, plus a harvesting tower — vanilla's agriculture machinery used for
**mineral** growth. Gleba farms food; the Core farms metal.

### Where maturation went

Maturation — the Vulcanus ↔ Gleba mechanic — was previously written here as the
Core's central process. It has moved: **its endgame home is the corridor**, where
cargo ripens during a platform run measured in real time, so the journey pays for
exactly one material.

Two time-based material processes on one planet would have blurred into each
other. Each now has a single home: maturation is a warehouse that ages, whisker
growth is a field you build and harvest.

## 9. Bots are earned

Personal roboports work at pressure 5 — verified, the equipment carries no
surface conditions — so the player can blueprint-build from their armour on day
one, slowly, within their own radius. What does not exist is a network.

A **pressurised roboport**, unlocked by a technology on the Core and built from
capstone products and volatiles, restores it. Give it `surface_conditions` of
pressure 1–9 and it works here and **nowhere else in the game**: not on platforms
(pressure 0), not on any vanilla planet (Aquilo is the lowest at 300). It is a
new building that competes with nothing, and it turns bots from an assumption
into a milestone.

## 10. Still open

- **How rich, and how scattered**, in numbers.
- **What the intermediates and end products actually are** — the two middle
  stages of §5 are named but not designed.
- **Which local input each of the five integration technologies uses** — the
  fix for them reading as one technology repeated (§6).
- **The geodynamic pack's cost**, which sets how sharply research competes with
  construction.
- **What the promethium-space material is** — the working assumption is a
  decaying isotope that loses charge in storage whether used or not, so corridor
  power can be produced and spent but never banked.
- **Which two intermediates the pack takes**, since that decides which trees a
  player is pushed to finish first.
- **The spike on `required_fluid` for a fluid resource** (§2).
- **What the end products are**, and how many of them there should be.
- **How many segments**, and how the 100 divides across the aging floor.
