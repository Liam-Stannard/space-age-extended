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
single value: no combustion of any kind, and no roboport networks. Working at
pressure 5 without any change: foundry, electromagnetic plant,
biochamber, recycler, chemical plant, assembler, electric furnace, nuclear
reactor, heat exchanger, steam turbine, drills, labs, accumulators, rails,
chests, cargo landing pad.

### Life and hazard

Nothing lives here, and nothing attacks. **Provisional:** the hazard is the
**arc storm** — lightning rarer and far heavier than Fulgora's (600 damage and
4000 MJ a strike, one every ninety seconds), which unprotected buildings take
in full and an **Arc Mast** catches and banks. The storm is therefore also half
the planet's power. It is built and measured (`prototypes/core/storms.lua`), but
it has not been played, and it is not yet confirmed as the final answer.


## 2. Resources

Three things, all sited, none of them enough.

### Metal ore — rich, scattered, finite

**Kamacite ore** — the real iron-nickel alloy of meteorite cores. Extremely rich
patches, spread widely, that genuinely run out. With no roboport
network available at first, that makes **belts and rails** the answer, and it
makes the Core a place the player expands across rather than a single pad they
build on.

**Only the Ballast Drill will work it.** The ore carries its own
`resource-category`, `sae-kamacite`, so no drill shipped in from anywhere else
touches it. 

### Melt vents — a fluid, infinite but declining

Scattered vents tapped by a **vent pump**, yielding **molten kamacite**: hot,
metal-bearing, and **unbarrelable**, so it can never leave the planet. Rate
declines with draw the way crude oil does, so a vent is permanent, worth building
around, and eventually wants company.

**Drawing melt costs helium-3.** The melt vent requires an input of **helium-3**
to draw (`minable.required_fluid`).


### Gas vents — volatiles, rare

**Helium-3**: primordial gas trapped since the planet formed, which is genuinely
what a planetary interior holds. Inert, cryogenic and precious — a scarce reagent
rather than a bulk utility, which is the right character for the rarer of the two
vents.

It is doubly load-bearing: melt cannot be drawn without it, so the rare resource
throttles the abundant one. Beyond that it is the atmosphere for sealed processes
(including the sealed roboport, §9) and an ingredient in the science pack.

### What the Core never has

**No carbon, no water, no organics.** No coal, no oil, nothing that ever lived.

No copper either. Plastics, explosives, anything biological and every drop of
water arrive from outside — ice caught on the corridor, organics from Gleba, the
rest by freight. The vents give the Core an industry. They do not give it
independence, and that is deliberate: the corridor has to keep running after the
megaproject is built.

**Two of those absences are answered rather than merely endured**, and §11 is
where: the Core builds the heavy half of a rocket and all of its own circuitry
without copper, carbon or oil. What it can never build is a capstone, which is
what §3 actually rests on.

## 3. Why the Core can never become self-sufficient

The structural guarantee, and the reason the whole mod holds together:

> **Every capstone product can only be made on the two planets whose tree
> produces it**, because each is anchored on a material or a condition exclusive
> to those worlds. The final line consumes all five.

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

### Stage 1 — the five integrations

A field coil has five parts: a conductor, a magnetic core, insulation, a coolant
and a frame. There are five trees. **Each capstone becomes one part of the coil**,
and each is integrated through a *different* local input, so the five
technologies are five different problems rather than one repeated.

| Tree | Capstone product | Local input | Intermediate | Coil part |
|---|---|---|---|---|
| Fulgora ↔ Aquilo | **Superconducting winding** | homogenised ingot — made in orbit | **Field conductor** | Conductor |
| Vulcanus ↔ Fulgora | **Magnetar alloy** | settled melt | **Magnetic core billet** | Core |
| Vulcanus ↔ Gleba | **Cultured alloy** | whisker tow — combed whiskers | **Reinforced frame** | Frame |
| Fulgora ↔ Gleba | **Bio-polymer** | whisker felt and raw molten kamacite | **Insulation sleeve** | Insulation |
| Gleba ↔ Aquilo | **Cryoprotectant fluid** | helium-3 | **Coolant charge** | Coolant |

As built in `prototypes/core/intermediates.lua`.

Every capstone is therefore *visibly in the thing being built*. A player looking
at a Field Coil Segment can trace each of its parts back to a pair of planets and
the chain that produced it.

### Stage 2 — the end products

| End product | From | Made by |
|---|---|---|
| **Coil assembly** | field conductor + magnetic core billet + reinforced frame + insulation sleeve + welded plate | **Cold welding** — joined in vacuum, slowly, at almost no power |
| **Coolant loop** | coolant charge + kamacite plate | Ordinary assembly on the surface |

Cold welding earns its place here: research uses the material sciences
(settling, growth, homogenisation), construction uses the joining.

### Stage 3 — the segment

**Field Coil Segment** = coil assembly + coolant loop. Nothing else. The
capstones are three stages below it, which is what makes the Core a factory
rather than an assembly point.

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
none — so it is unlocked late, by **Carbonyl Chemistry** after Magnetic
Separation, and built from **imported carbon**. That is a feature rather than an obstacle: it gives the corridor a
permanent cargo that has nothing to do with the capstones, and it means the
Core's best chemistry is paid for with freight from home.

## 6. The sixth tech tree

The Core carries the mod's **sixth technology tree** — twenty-one technologies,
and the only tree whose research currency is manufactured on site.

### Geodynamic science

A new science pack, crafted from the **intermediates** of the Core's own line
(§5) — the same intermediates the end products need.

### The recipe

**Geodynamic science pack** — 1 field conductor + 1 reinforced frame +
4 kamacite whiskers → 5 packs, 20 s, in an assembler, recipe locked to pressure
1–9. One recipe.

The pack touches three of the Core's four mechanics: the conductor carries
orbital homogenisation, the frame carries whisker growth and the whiskers
themselves carry the farm's tile. Two rules:

- **Locked to pressure 1–9.** Labs carry no surface conditions, so research
  itself can happen anywhere; the *pack* cannot be made anywhere but here. The
  tree therefore has to be advanced by a factory genuinely running on the Core.
  Vanilla gates its own packs the same way — electromagnetic at magnetic field
  99, metallurgic at pressure 4000, cryogenic at 100–600.
- **It requires one orbit-made intermediate.** The field conductor needs a
  homogenised ingot, so the platform overhead is load-bearing from the first
  geodynamic technology rather than switching on at the end.

### The ladder

Twenty-one technologies in five tiers, shaped so the endgame builds rather
than arriving flat.

| Tier | Technologies | Notes |
|---|---|---|
| **0 — Foothold** | **Core Discovery** (an `unlock-space-location` technology — measured: the planet is unreachable without one) · Core Survey (vent pump, drill, crusher, smelting) · Crust Tapping (landing-day power) · Gravity Settling (the melt split, and casting) · Whisker Beds (tiles, seeding, harvest) · Arc Masts · Cold Welding · **Orbital Lift** (§11) · **Vacuum Electronics** (§11) | Researched on packs the player already makes, since no geodynamic pack exists yet |
| **1 — Integration** | Five technologies, one per capstone. **Conductor** and **Frame** come first, on vanilla packs — the two the science pack needs. **Billet**, **Sleeve** and **Coolant** follow, on geodynamic packs, in any order |
| **2 — Geodynamic Science** | The pack itself | Needs the Conductor and the Frame; required by everything after |
| **3 — The Core's own goods** | **Field Coils** (coil assembly, coolant loop, the Ring Mast, the ignition charge) · Corridor Seeding · Magnetic Separation · Carbonyl Chemistry · the **sealed roboport** (§9), which needs Field Coils and cold welding | The mid-tree milestone: after hours of belts and personal bots, the Core starts working like a factory |
| **4 — The goal** | Ignition Array, which also unlocks the Field Coil Segment | Costs escalate steeply — the Array's research alone running into thousands of packs |

### Three things this shape gets right

**The pack cannot be first.** It is made from intermediates, and intermediates
need a capstone product plus a local input — so the opening hours run on vanilla
packs and local bootstrapping, and geodynamic science arrives only once the
corridor is genuinely delivering. The tree's currency is earned rather than
granted on landing. Some technologies will be trigger techs to aid players progress through the mod.

**The climax is the last technologies.** With costs escalating steeply, the
ramp is felt rather than announced, and the final stretch becomes one sustained
decision about how to split a single production line between knowing more and
building more.

**The five integration technologies must not be five of the same technology.**
They share a shape — capstone plus local input yields intermediate — so what
saves them is that each integrates through a **different local input**: one
through settled melt, one through the helium, one through an orbit-only ingot,
one through combed whiskers, one through felt and raw melt. Then each capstone lands somewhere
different in the Core's economy, and five reads as five.

## 7. The completion goal — restarting the dynamo

The Core's field is dead: `magnetic-field` reads 0. **The mod is completed by restarting it.**

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

Once all parts are made the array should start to run the completion.


### What it leaves behind

A final science pack which can be used for some of the endless research.

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

The same condition now carries a second industry. **Vacuum electronics** (§11)
is the Core's answer to having no copper, and it is only possible where the
vacuum is free: a sealed emitter facing a gate across nothing at all. Cold
welding joins in vacuum; field emission *switches* in it.

### Whisker growth — surface, on tiles

Kamacite whiskers crystallise out of the melt over time on seeded plates, and are
harvested like a crop. Growing area, not machine count, is the throughput.

*Implementation:* the `plant` prototype with `growth_ticks` and a tile
restriction — measured working on the Core, growing to maturity and yielding its
products. Vanilla's agricultural tower needs pressure 1000–2000 and is refused
here, so the mod supplies its own: the **Bed Tender**. Gleba farms food; the
Core farms metal.

## 9. Bots are earned

Personal roboports work at pressure 5 — verified, the equipment carries no
surface conditions — so the player can blueprint-build from their armour on day
one, slowly, within their own radius. What does not exist is a network.

A **sealed roboport**, unlocked by a technology on the Core after Field Coils
and cold welding, restores it. Give it `surface_conditions` of
pressure 1–9 and it works here and **nowhere else in the game**: not on platforms
(pressure 0), not on any vanilla planet (Aquilo is the lowest at 300). It is a
new building that competes with nothing, and it turns bots from an assumption
into a milestone.

## 10. Still open

- **How rich, and how scattered**, in numbers.
- **The geodynamic pack's cost**, which sets how sharply research competes with
  construction.
- **What the promethium-space material is** — the working assumption is a
  decaying isotope that loses charge in storage whether used or not, so corridor
  power can be produced and spent but never banked.
- **The capstone buildings.** The products are chosen; each tree still has to
  design the building made *from* its product, and prove it is useful when
  earned, on the way out, and again at the Core.
- **Whether the arc storms stay** as the hazard and half the power (§1).

## 11. What the Core makes instead of importing it

Two absences looked like permanent freight and turned out to be design space.
Both were found the same way: by walking the technology tree and asking, at each
node, whether the recipes it unlocks can actually be crafted.

### Rocket Parts
§4 puts half the endgame in orbit, and every trip up costs a rocket. A rocket
part is a processing unit, a low density structure and a rocket fuel — and the
Core could originally make none.

Two alternates fix the heavy end, in the shape vanilla already uses for exactly
this — Vulcanus does not get a new rocket part, it gets
`casting-low-density-structure`; Gleba gets `rocket-fuel-from-jelly`. A planet
earns a different route to the same item.

| Alternate | From | Where | Why here |
|---|---|---|---|
| **Whisker-cast structure** | settled melt + whisker tow | foundry | Single-crystal fibre in a cast matrix. Low density because of what is *in* it. Ties the lift to the farm, so "launch more often" means more floor |
| **Crust-gas propellant** | crust gas + kamacite plate | chemical plant | Gives the crust vents a second job, so the tap stops being a building the player walks past after hour one. The lift is sited on the map, like everything else here |

### Circuits without copper

A sharp enough metal tip in a hard enough vacuum emits electrons under field
alone — cold, no heater, no semiconductor. That is field emission, it is real,
and vacuum microelectronics is prized in precisely the conditions this planet
has: no atmosphere to break down, and a radiation hardness no doped wafer
matches. **The switching element is a gap.**

Which means the Core's two dead ends are the two ingredients:

- **Whiskers are single-crystal metal fibres, and a field emitter is a sharp
  single-crystal tip.** The comber already aligns them, because a composite wants
  its fibres one way; an emitter array wants its tips one way for the same reason
  and the same recipe serves both.
- **Vacuum**, which `06-core-production-tree.md` T8 named as the Core's one free
  advantage and then observed that nothing used. All three recipes carry
  `pressure ≤ 9`, so they are refused everywhere else in the game. Aquilo, the
  lowest vanilla planet, is 300. A pressure of 10 is a device full of air.

```
1 whisker tow + 2 kamacite plate            ->  2 field emitter array
1 emitter array + 1 kamacite plate          ->  2 advanced circuit
3 emitter array + 1 welded plate + 100 steam ->  1 processing unit
```

### What this does not change

The corridor still brings all five capstone products, and steel, gears, electric
engines, pipe, accumulators, carbon and rockets besides. §3's guarantee was never
about circuits; it rests on the capstones, and it is untouched.

