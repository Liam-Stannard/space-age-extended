# The Core — full production tree (draft)

A draft of the Core's complete line, deep enough to be the mod's largest chain
rather than its shortest. **This is a design document, not an implementation
record.** Nothing here is built yet; `design/05-core-remaining.md` says what is.

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

The sketch above is the shape only. The drawn version —
[`diagrams/core-production-tree.html`](diagrams/core-production-tree.html), built
by `tools/build-core-tree-diagram.py` — carries what this cannot: which boxes
exist today against which are drafted, where the two rails enter and at which
tier each capstone lands, and the marks from `07-sinks-and-dead-ends.md`.
Regenerate it rather than editing it.

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
| Kamacite plate | 2 kamacite ore | furnace | **exists** — should become 3 crushed kamacite, so T1 is not bypassable |
| Settled melt · dross · steam | 100 molten kamacite | foundry | **exists**, two recipes (metal-heavy / steam-heavy) |
| Cast ingot | 100 settled melt | foundry | **exists** |
| **Phosphide flux** | schreibersite concentrate + settled melt | foundry | New. Consumed in T3 and T8; the reason T1 is not optional |

**Make the plate recipe consume crushed ore.** Right now smelting takes raw ore,
so the whole beneficiation tier can be skipped. Routing plate through crushed
kamacite is a one-line change that makes T1 load-bearing.

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
| **Whisker prepreg** | whisker tow + **bio-polymer** | assembler | Fibre in a matrix. This is where Fulgora ↔ Gleba's capstone enters, one tier earlier than now |
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
| Fulgora ↔ Gleba | Bio-polymer | consumed earlier, in prepreg | *(see note)* |
| Gleba ↔ Aquilo | Cryoprotectant | consumed earlier, in dilution charge | *(see note)* |

**Note on the two that moved.** Bio-polymer and cryoprotectant now enter at T5
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

**Vacuum is the Core's one free advantage** and nothing currently uses it. A step
that is cheap here and would need an expensive sealed process on any other planet
is worth having, because it gives the player something the Core is *good* at
rather than only things it lacks.

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

**14 new items and 2 new fluids**, none of them filler:

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

**Two of these tiers create a dead end**, and both are cheap to avoid at
implementation time: T1's fines have no sink until T3 exists, and T9's coil
assembly as drafted drops welded plate, leaving cold welding with nothing
ongoing to do. See `07-sinks-and-dead-ends.md` §4, which also carries the
byproduct stalls the existing line already has.

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
