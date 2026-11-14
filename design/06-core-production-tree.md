# The Core — full production tree (draft)

A draft of the Core's complete line, deep enough to be the mod's largest chain
rather than its shortest. **This is a design document, not an implementation
record.** Where the code stands against it, per tier:

| Tier | Built |
| ---- | ----- |
| T1 | crushed kamacite and fines |
| T2 | kamacite plate only |
| T3–T11 | nothing: cut back to the landing |

---

## Why this document exists

Design `04-the-core.md` §5 promises "the mod's largest chain, and the only one
that cannot be built anywhere else". Measured against what is actually in the
mod, it is currently **three stages deep** from local resource to Field Coil
Segment:

```
molten kamacite -> settled melt -> cast ingot -> homogenised ingot -> field conductor
```

Gleba's nutrient chain is deeper than that. The promise is not being kept.

This draft takes it to **eleven tiers**, with every new intermediate justified by
one of the Core's four established mechanics rather than added for length. The
test each one has to pass: *if this step were deleted, would the player notice
anything other than fewer clicks?* Anything that fails it is not here.

---

## The constraints every step obeys

Repeated from `04-the-core.md` because they are what make this line the Core's
and not a generic ore chain:

1. **Nothing burns.** Pressure 5 refuses every combustion prototype. Heat comes
   from the melt or from the arc storms; never from a flame.
2. **No carbon, no water, no organics** are local. Every one arrives by freight,
   which keeps the corridor alive after the megaproject is finished.
3. **Gravity separates on the surface; orbit does what gravity forbids.** 50 g
   pulls a melt apart by density. Zero g lets things mix, and lets a crystal grow
   without slumping under its own weight.
4. **Helium-3 throttles the melt.** The rare vent gates the abundant one, so the
   two are one siting problem.
5. **Research competes with construction.** Geodynamic science eats the same
   intermediates the Field Coil Segment does.

A sixth, new here and load-bearing for tiers 1 and 6:

6. **The Core has no magnetic field, so it cannot separate magnetically until it
   makes one.** `magnetic-field = 0` already refuses the electromagnetic plant as
   a *manufactured* item. Magnetic beneficiation therefore needs an imported
   plant early, and later needs the mod's own field coils — the player ends up
   using the thing they are building to build more of it.

---

## The tree

```
                          IMPORTED                         LOCAL
        carbon · water · ice · organics        kamacite ore · molten kamacite
        five capstone products                 helium-3 · radiant chunks
                    |                                      |
  T1   ................................ BENEFICIATION ......................
                                    crushed kamacite, fines, schreibersite
                    |                                      |
  T2   ................................ PRIMARY METALLURGY .................
                       kamacite plate · settled melt · dross · steam
                    |                                      |
  T3   ................................ CARBONYL CHEMISTRY .................
             metal carbonyl gas <-> carbon monoxide (recovered)
                          carbonyl powder -> sintered preform
                    |                                      |
  T4   ................................ ORBITAL CRYSTAL ....................
              cast ingot -> zone-refined boule -> kamacite wafer
                    |                                      |
  T5   ................................ FIBRE AND COMPOSITE ................
              seed plate -> whiskers -> whisker tow -> prepreg
                    |                                      |
  T6   ................................ CRYOGENICS .........................
                helium-3 -> dilution charge -> cryostat core
                    |                                      |
  T7   ................................ THE FIVE INTEGRATIONS ..............
       conductor · core billet · frame · sleeve · coolant charge
                    |
  T8   ................................ SUBASSEMBLIES ......................
              coil lamination · winding pack · vacuum cell
                    |
  T9   ................................ MAJOR ASSEMBLIES ...................
                    coil assembly · coolant loop
                    |
  T10  ................................ FIELD COIL SEGMENT .................
                    |
  T11  ................................ IGNITION ARRAY .....................
```

---

## T1 — Beneficiation

Kamacite is a real meteoritic iron-nickel alloy, and real meteorites carry
**schreibersite**, an iron-nickel phosphide. That single mineralogical fact
gives the Core a phosphorus source it can defend, and phosphorus is what tiers 3
and 8 need for fluxing and brazing.

| Item | Made from | Where | Why it exists |
| ---- | --------- | ----- | ------------- |
| **Crushed kamacite** | 1 kamacite ore | crusher | Splits ore into two streams so beneficiation is a choice, not a formality |
| **Kamacite fines** | byproduct of crushing | — | The tailings; feeds T3 rather than being waste, so nothing is simply deleted |
| **Schreibersite concentrate** | crushed kamacite, **magnetic separation** | electromagnetic plant | The Core's only phosphorus. Needs a field the planet does not have — see constraint 6 |

**The magnetic gate is the point of this tier.** Magnetic separation needs an
electromagnetic plant, which `magnetic-field = 0` forbids *manufacturing* on the
Core. So the first one is freight, and the player feels the planet's dead dynamo
as a supply problem long before the Ignition Array explains it thematically.

---

## T2 — Primary metallurgy

Mostly built already. One addition and one change.

| Item | Made from | Where | Status |
| ---- | --------- | ----- | ------ |
| Kamacite plate | 3 crushed kamacite | furnace | **done** — re-sourced, so T1 is not bypassable. Note the consequence: this put the Drop Crusher on the critical path to its own ingredient, so the crusher and the Ballast Drill are priced in freight |
| Settled melt · dross · steam | 100 molten kamacite | foundry | **exists**, two recipes (metal-heavy / steam-heavy) |
| Cast ingot | 100 settled melt | foundry | **exists** |
| **Phosphide flux** *(fluid)* | schreibersite concentrate + settled melt | foundry | New. Consumed in T3 and T8; the reason T1 is not optional. **A fluid, settled 2026-09-06** — see below |

**Phosphide flux is a fluid, not an item.** Spike S12 showed a `furnace` can
auto-select a recipe from one item plus one fluid, which is what lets the Vacuum
Furnace sinter powder *and* flux while still picking its own recipe from what is
inserted. The cost is that flux is piped rather than belted, and can be tanked but
not chested. See `concept/vacuum-furnace/building-spec-vacuum-furnace.md`.

**Make the plate recipe consume crushed ore.** *Done.* It was a one-line change
and it made T1 load-bearing — and it also made the mod unplayable for a while,
because crushing is the only source of crushed kamacite and fines, those are the
only routes to a plate, and the Drop Crusher was costed at 40 kamacite plate. The
first crusher could never be built.

**The rule that came out of it:** anything on the critical path to the first
kamacite plate is priced in freight, and everything after it is priced in plate.
That is the Gas Pump, the Siderane turbine, the Ballast Drill and the Drop
Crusher. The Vent Pump now comes after the first plate and is still priced in
freight. It is the same argument this tier already makes about the first
electromagnetic plant, applied consistently.

---

## T3 — Carbonyl chemistry

The chemistry `04-the-core.md` §5 already wants, drawn out properly. Nickel and
carbon monoxide combine into a **gas** at low temperature and separate again at
high temperature, depositing metal of extraordinary purity and **releasing the
carbon monoxide to be used again**.

| Item | Made from | Where | Why it exists |
| ---- | --------- | ----- | ------------- |
| **Carbon monoxide** (fluid) | carbon (imported) + settled melt | chemical plant | The carrier. Imported carbon enters the Core here and almost nowhere else |
| **Metal carbonyl** (fluid) | kamacite fines + carbon monoxide, cold | chemical plant | Metal that travels through pipes — the mechanically distinctive thing the Core can do |
| **Carbonyl powder** | metal carbonyl, hot | chemical plant | Ultra-pure metal, and **90% of the carbon monoxide comes back** |
| **Sintered preform** | carbonyl powder + phosphide flux | assembler | Powder pressed into a shape; the feedstock for T8's laminations |

**Carbon is a catalyst with losses, not a consumable.** Recovering 90% means the
corridor delivers a trickle rather than a torrent, which is the right weight for
freight: enough that losing the supply line hurts, not so much that the Core
becomes a carbon importer above all else. It also gives the player a genuine
efficiency target — module the decomposition and the freight bill falls.

**It consumes the fines.** T1's tailings are T3's feedstock, so the crusher's
byproduct has somewhere to go and beneficiation stops feeling lossy.

---

## T4 — Orbital crystal growth

The lift already exists for homogenisation. This gives it more to do, and gives
a better reason than "mixing is easier": **a crystal grown in gravity slumps
under its own weight.** Zone refining in free fall is one of the few things
microgravity is genuinely, industrially good for.

| Item | Made from | Where | Why it exists |
| ---- | --------- | ----- | ------------- |
| Homogenised ingot | 2 cast ingot | orbit | **exists** |
| **Zone-refined boule** | homogenised ingot + helium-3 | orbit | A single crystal. Helium-3 is the cold end of the zone; the rare vent reaches into orbit |
| **Kamacite wafer** | 1 boule | orbit | Sliced. The substrate every superconducting step needs |

The boule step puts helium-3 on the platform, which means the lift carries a
*fluid* both ways and the two vents stop being a purely surface concern.

---

## T5 — Fibre and composite

Whiskers are single-crystal metal fibres, and single-crystal fibres are absurdly
strong in tension and useless in every other direction. That is a real material
property and it earns two steps: **aligning** them, then **binding** them.

| Item | Made from | Where | Why it exists |
| ---- | --------- | ----- | ------------- |
| Kamacite whiskers | grown on beds from seed plates | bed tender | **exists** |
| **Whisker tow** | 8 whiskers | assembler | Combed into one direction. Strength is directional, so alignment is a step |
| **Whisker prepreg** | whisker tow + **the Vulcanus ↔ Aquilo capstone** (to be designed; was bio-polymer) | assembler | Fibre in a matrix. This is where Vulcanus ↔ Aquilo's capstone enters, one tier earlier than now |
| **Whisker felt** | 4 whiskers, low grade | assembler | Unaligned. Cheap thermal insulation for T6 — a use for whiskers that are not worth combing |

Two grades from one crop is what makes the farm interesting: the player chooses
how much of the harvest is worth the extra step, and the answer changes as the
line grows.

---

## T6 — Cryogenics

Superconduction needs cold, and helium-3 is the working fluid of real dilution
refrigerators. This is where the Core's rarest resource stops being a gate and
becomes a product.

| Item | Made from | Where | Why it exists |
| ---- | --------- | ----- | ------------- |
| **Dilution charge** | helium-3 + cryoprotectant (**Gleba ↔ Aquilo capstone**) | cryogenic plant | The refrigerant. Puts the fifth capstone one tier deeper |
| **Cryostat core** | dilution charge + whisker felt + sintered preform | assembler | A cold vessel: refrigerant, insulation, structure. Three tiers converge |

**Every downstream superconducting step needs one**, so the rare vent is felt at
the end of the line as well as the beginning.

---

## T7 — The five integrations

Unchanged in shape from `04-the-core.md` §5, deepened in inputs. Each capstone is
still integrated through a *different* local mechanic, which is what stops the
five technologies being one technology repeated.

| Tree | Capstone | Local input | Intermediate |
| ---- | -------- | ----------- | ------------ |
| Fulgora ↔ Aquilo | Superconducting winding | **kamacite wafer** (T4) | Field conductor |
| Vulcanus ↔ Fulgora | Magnetar alloy | settled melt + **phosphide flux** (T2) | Magnetic core billet |
| Vulcanus ↔ Gleba | Cultured alloy | **whisker prepreg** (T5) | Reinforced frame |
| Vulcanus ↔ Aquilo | to be designed (was bio-polymer) | consumed earlier, in prepreg | *(see note)* |
| Gleba ↔ Aquilo | Cryoprotectant | consumed earlier, in dilution charge | *(see note)* |

**Note on the two that moved.** The insulation capstone and cryoprotectant now enter at T5
and T6 rather than at T7. That is deliberate: it means two capstones are consumed
*deep* in the line rather than at the last moment, so a lagging tree starves the
Core early and visibly instead of only blocking the final assembly. The insulation
sleeve and coolant charge still exist as T8 subassemblies — they are simply built
from the prepreg and the dilution charge rather than from raw capstones.

---

## T8 — Subassemblies

| Item | Made from | Why it exists |
| ---- | --------- | ------------- |
| **Coil lamination** | sintered preform + phosphide flux | Thin plates, vacuum-brazed. The flux from T1/T2 pays off here |
| **Winding pack** | field conductor + cryostat core | The conductor only works cold; this is where that becomes true mechanically |
| **Insulation sleeve** | whisker prepreg + molten kamacite | **exists**, re-sourced from prepreg |
| **Coolant charge** | dilution charge + kamacite plate | **exists**, re-sourced from the dilution charge |
| **Vacuum cell** | coil lamination + insulation sleeve | Sealed in vacuum — free on the Core and impossible anywhere else |

**Vacuum is the Core's one free advantage.** A step that is cheap here and would
need an expensive sealed process on any other planet is worth having, because it
gives the player something the Core is *good* at rather than only things it
lacks.

*Updated:* this used to read "and nothing currently uses it". Something does now
— **vacuum electronics**, `04-the-core.md` §11, which is how the Core makes
circuits without copper. The vacuum cell below is still worth building for the
same reason; it is no longer the only claim on the advantage.

---

## T9 — Major assemblies

| Item | Made from | Where |
| ---- | --------- | ----- |
| **Coil assembly** | winding pack + magnetic core billet + reinforced frame + vacuum cell | cold welding |
| **Coolant loop** | coolant charge + kamacite plate + cryostat core | assembler |

---

## T10 — Field Coil Segment

Unchanged: coil assembly + coolant loop. The capstones are now **five to seven
tiers below it** rather than three, which is what the design document claimed all
along.

## T11 — Ignition Array

100 segments, as now.

---

## What this adds

**15 new items and 3 new fluids**, none of them filler:

> crushed kamacite · kamacite fines · schreibersite concentrate · phosphide flux ·
> carbon monoxide *(fluid)* · metal carbonyl *(fluid)* · carbonyl powder ·
> sintered preform · zone-refined boule · kamacite wafer · whisker tow ·
> whisker prepreg · whisker felt · dilution charge · cryostat core ·
> coil lamination · winding pack · vacuum cell

Depth from local resource to Field Coil Segment goes from **3 stages to 10**.

Each tier is anchored on something the Core has or lacks:

| Tier | Anchored on |
| ---- | ----------- |
| T1 | The dead dynamo — magnetic separation needs an imported plant |
| T2 | Gravity — the melt splits by density under 50 g |
| T3 | No carbon — the corridor's permanent cargo, recovered at 90% |
| T4 | No gravity in orbit — crystals that cannot grow on the ground |
| T5 | The farm — two grades from one crop |
| T6 | The rare vent — helium-3 as a product, not only a gate |
| T8 | Vacuum — the one thing the Core is better at than anywhere else |

---

## Risks, and what would make this worse

**It could become tedious rather than deep.** Ten tiers of one-in-one-out
recipes is a conveyor, not a factory. Every tier above either branches (T1's two
streams, T5's two grades), loops (T3's recovered carbon monoxide), or converges
(T6's three inputs). Any new step that does none of those should be cut.

**It could make the corridor a bottleneck rather than a lifeline.** Carbon
recovery at 90% is the dial. If freight becomes the limiting factor the endgame
turns into a shipping puzzle, which is Space Age's problem and not this mod's.

**It could bury the capstones.** Moving bio-polymer and cryoprotectant deeper
makes lagging trees bite sooner, but if they are buried too deep the player stops
being able to see the five planets in the thing they are building — which
`04-the-core.md` §5 names as the point. The intermediates keep the capstones'
names in their ingredient lists for exactly this reason.

**Untested numbers.** Every quantity above is a placeholder. The one that matters
most is still geodynamic science's cost, for the reason §6 of the design document
gives: research and construction draw on one supply, and if the pack is cheap the
endgame collapses into a segment grind.

## Suggested build order

1. **T1–T2** — beneficiation and flux. Small, self-contained, and makes the
   existing smelting chain load-bearing.
2. **T3** — carbonyl. The most distinctive mechanic and it stands alone.
3. **T5** — fibre grades. Needs only the farm, which already works.
4. **T4, T6** — orbital crystal and cryogenics. Both need capstones, so they
   follow the four stub chains landing.
5. **T7–T9** — re-sourcing the existing intermediates onto the new tiers.

---

## From 04, to review

**Moved as it was from `04-the-core.md` §5 and §8 (2026-11-14); not yet reviewed against the rest of this document.**

### 04 §5 — The final production line

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
| Vulcanus ↔ Aquilo | **to be designed** | whisker felt and raw molten kamacite | **Insulation sleeve** | Insulation |
| Gleba ↔ Aquilo | **Cryoprotectant fluid** | helium-3 | **Coolant charge** | Coolant |

No intermediate is built: they went with the cut back to the landing.

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

### 04 §8 — The Core's own mechanics

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
