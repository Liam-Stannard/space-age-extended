# The Problem Catalogue

**Working document.** Before a tree can be assigned to a pair, we need to know
what problems are actually worth solving. This is the raw list, sorted into
categories, with a proposed shortlist at the end.

A problem earns a place here only if **vanilla leaves it unsolved or solves it
expensively**. Anything Space Age already handles well is not a problem, it is a
feature the mod would be stepping on.

---

## A. Freight — getting material between worlds

| Problem | What vanilla does | Why it still bites |
|---|---|---|
| **Every shipment costs a rocket** | Rocket parts from processing units, low density structures, rocket fuel | It is a real per-trip tax on any cross-planet chain; a chain that ships continuously is paying it forever |
| **Fluids barely travel** | Barrels — but nine fluids have none at all (`lava`, `molten-iron`, `molten-copper`, `holmium-solution`, `electrolyte`, `ammonia`, `ammoniacal-solution`, `fluorine`, `lithium-brine`) | Whole categories of material simply cannot leave their world |
| **Bootstrapping a new world** | Ship everything until local production stands up | The most tedious hours in the game, repeated per planet, and the Core makes it permanent |
| **Round trips are slow** | Platform flies, waits, returns | A dependency that needs material back is painful in a way a one-way export is not |

## B. Time — things that expire

| Problem | Numbers | Why it bites |
|---|---|---|
| **Spoilage does not stop for transit** | nutrients 5 min, yumako mash 3 min, jelly 4 min, pentapod egg 15 min, biter egg 30 min, yumako/jellynut 60 min, bioflux 120 min | Gleba's entire output is on a clock, and a rocket does not pause it. Anything Gleba sends must survive the trip or be sent as something else |
| **Nothing preserves** | Freezing exists on Aquilo as a hazard, never as a tool | The game has a world that stops things and a world whose things need stopping, and never connects them |
| **The endgame journey is long** | — | On a route measured in millions of kilometres, time itself becomes the hazard |

## C. Environment — what a world forbids

| Problem | What vanilla does | Why it bites |
|---|---|---|
| **Aquilo freezes everything** | Heat pipes and heating towers, fuelled from imports | Heat is a second logistics network layered on the first, and it is the reason Aquilo is hard |
| **Space refuses most buildings** | Measured: no boiler, furnace, heating tower, roboport, chest, rocket silo, biolab or agricultural tower at pressure 0 | A platform is not a small factory; whole approaches are unavailable there |
| **Vulcanus has no water** | Everything runs on lava, acid and calcite instead | An entire branch of vanilla chemistry is missing on the hottest world |
| **The Core forbids nearly everything** | — | No fluids, no combustion, no biology. Whatever works there has to have been designed elsewhere |

## D. Energy — power where it is hard

Vanilla solves power well for most of the game: solar and nuclear on Nauvis,
lightning on Fulgora, solar again on Vulcanus at 400. **Power is only a problem
late**, and then it is a severe one.

| Problem | Numbers | Why it bites |
|---|---|---|
| **Aquilo has no sun** | solar-power 1, against Nauvis 100 and Vulcanus 400 | Solar is worthless; the answer is fission or fusion, both of which need a supply chain before they produce a watt |
| **Nuclear in space needs water** | Ice must be captured and melted before a reactor makes anything | Power becomes a function of asteroid capture rate |
| **Fusion is gated behind Aquilo** | Cells need ammonia, which cannot be barrelled | The best platform power source cannot exist until the hardest planet is running |
| **Distance kills solar entirely** | — | Past the Edge there is no sun at all, and the Core cannot burn anything |

## E. Threat — damage and defence

| Problem | What vanilla does | Why it bites |
|---|---|---|
| **Asteroid damage scales with distance and speed** | Guns and ammunition, shipped up | Ammunition is a consumable that must be freighted, so range is capped by cargo |
| **Gleba fights back** | Pentapods respond to spores; stompers are genuinely dangerous | The only world where expanding production has a military cost |
| **The promethium field** | Nothing — it is where runs end | Density exceeds any ammunition economy a hold can carry |

## F. Scarcity — what a world simply does not have

| World | Has | Lacks entirely |
|---|---|---|
| **Vulcanus** | lava, tungsten, calcite, coal, sulfuric acid geysers | water, biology, electronics feedstock |
| **Fulgora** | scrap, and everything comes out of it | soil, biology, ore veins, fresh water |
| **Gleba** | plants, stone, water, bacteria that yield ore | ore veins, oil, metals of its own |
| **Aquilo** | crude oil, fluorine, lithium brine, ammonia, ice | solids of almost every kind, warmth, light |

The two most interesting rows are Fulgora and Gleba: **the world with no soil and
the world with no ore**, each of which manufactures what it lacks out of what it
has.

## G. Space — floor area

| Problem | Why it bites |
|---|---|
| **Platform tiles are expensive** | Every tile is foundation the player paid to launch; a chain that needs twenty buildings does not fit |
| **Depots and outposts** | Anything parked far away has to be compact enough to be worth building at all |

---

## Proposed shortlist

Five problems, each with a form at unlock and a form at the Core, and each
belonging to two worlds in particular. **This is the proposal to argue with, not
a decision.**

| # | Problem | At unlock | At the Core | Natural worlds |
|---|---|---|---|---|
| 1 | **Making a world's waste into a world's want** | Fulgora drowns in scrap output it cannot use; Gleba has no ore | The Core has one material and needs everything | Fulgora ↔ Gleba |
| 2 | **Stopping the clock** | Gleba's output cannot survive a trip anywhere | The longest journey in the game, carrying things that expire | Gleba ↔ Aquilo |
| 3 | **Holding ground that fights back** | Gleba's pentapods, and platforms under asteroid fire | The promethium field, where ammunition economics break | Vulcanus ↔ Gleba |
| 4 | **Throwing material further than a rocket can** | Every cross-planet shipment costs a rocket, forever | A supply line no rocket chain can sustain | Fulgora ↔ Aquilo |
| 5 | **Power where there is no sun and nothing burns** | Aquilo, where solar reads 1 and fusion is gated behind the planet itself | The Core: no light, no oxygen, no combustion | Vulcanus ↔ Fulgora? — *see below* |

**The problem with problem 5.** Power is now correctly a late problem, but its
natural pair is a mid-game one. Three ways out:

- **Give power to an Aquilo tree** and move something else to Vulcanus ↔
  Fulgora. But both Aquilo pairs already hold strong problems.
- **Let Vulcanus ↔ Fulgora hold power but land its capstone late in its own
  tree**, so the tree opens mid-game and its payoff arrives around Aquilo.
- **Use the reserve pair.** Vulcanus ↔ Aquilo is heat against cold and is the
  most natural power tree in the system — it was set aside only because it put
  three trees behind Aquilo.

My preference is the second: a tree can open early and still end late, and
Vulcanus ↔ Fulgora is genuinely the heat-and-electricity pairing. But the third
is the honest answer if power turns out to want Aquilo's cold.

**What Vulcanus ↔ Fulgora would hold instead**, if power moves: the pairing's own
strongest idea is that Fulgora's scrap yields holmium and Vulcanus's lava yields
tungsten, and neither world can use the other's specialty without the other's
process — which points at *materials that cannot be made anywhere else* rather
than at a capability. That is a weaker capstone premise, which is part of why I
prefer keeping power there.
