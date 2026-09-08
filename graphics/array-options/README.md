# The Ignition Array — five options

The Array is the last building in the mod and the one the whole Core exists to
let you build. Its shape has never actually been *chosen*: v1, v2 and v3 are one
idea refined three times, not three ideas compared. This directory is the
comparison that never happened.

**Nothing here is adopted.** Five options, one gets picked, the other four are
deleted.

---

## The only three constraints

Everything else — silhouette, massing, palette, whether there is a bore at all —
is open. Previous rounds were fenced in by a plate plan derived from vanilla's
rocket silo; that plan existed to make two door leaves close over a hole, and
**the doors are gone**, proved cosmetic on a live 2.1.17 server. The fence went
with them.

### 1. It fits inside 9 × 9. No overhang.

Not "roughly", and not vanilla's 9% proud. `build-array-plates.py` scales the
plate to the footprint exactly and raises rather than emitting one that spills.
Art that overhangs overlaps whatever is built beside it.

The practical consequence for a design: **height costs width.** A tall building
drawn in this camera eats its own footprint, so anything tower-shaped has to be
squat or it will be scaled down until the base looks small.

### 2. It suits the Core, and what the Core makes.

From `design/04-the-core.md` and the Array's own recipe, and these are not
flavour notes — each one rules things out:

* **A dead dynamo.** `magnetic-field = 0`. The Array's whole purpose is to
  restart it: `control.lua` says it "delivers nothing — it fires a current into
  the crust". It is not a rocket, and it should not look like one.
* **Nothing burns.** `pressure = 5`, no atmosphere. **No flame, no exhaust, no
  steam, no smoke, ever** — vanilla's six silo working visualisations were
  deleted for exactly this. A plume is not a stylistic slip here, it contradicts
  the planet.
* **Gravity 50, the heaviest world in the game.** Everything is squat, braced
  and anchored. Nothing cantilevers, nothing is delicate.
* **It is superconducting, so it is cold.** The chain ends in coolant loops and
  cryogen. Frost and rime are on-theme; glowing-hot metal is not.
* **Arc storms are canon furniture.** The recipe contains **4 arc masts**, so
  masts are literally part of this machine, not decoration.
* **Iron-nickel.** Kamacite plate and welded plate, 700 of them: weathered
  grey-brown steel and rust, not painted panels.
* **Violet is discharge.** The one saturated colour, and it is earned.

### 3. It shows how charged it is.

The Array assembles **100 `sae-field-coil-segment`s** before it can fire, which
is a long, visible investment, and until now the building said nothing about it.

`control.lua` drives this through `LuaRendering` — verified on 2.1.17, along with
the fact that no prototype field can do it. The level is read straight off the
entity:

```lua
(e.rocket_parts + e.crafting_progress) / e.prototype.rocket_parts_required
```

`crafting_progress` is the segment in flight, so that is a **smooth 0 → 1 across
the whole build**, not a hundred clicks. `rendering.draw_sprite`,
`draw_animation` and `draw_light` all exist and a drawn object's `intensity` is
settable after creation, so a charge can ramp continuously.

**So each option has to answer: where does a 0-to-1 fill live, and is it legible
at normal zoom?** A design whose charge is a subtle tint on one small part is a
design that fails this constraint even if it is the prettiest.

---

## How the five differ

| | Massing | Charge lives in | Palette |
|---|---|---|---|
| **A** Coil Ring | squat ring around a wide bore | the 100 segments themselves, filling around the ring | rust and steel |
| **B** Mast Cluster | braced deck, four corner masts | four insulator stacks, filling base to tip | steel, ceramic, copper |
| **C** Cryostat | one fat insulated drum | rime receding off the vessel | white-blue, frost |
| **D** Busbar Yard | flat open switchyard | capacitor rows filling across the deck | copper and grey |
| **E** Crust Anchor | six legs driven into the ground | the electrode, and the crust around it | rock, dark iron |

Judge them on the three constraints, in order, and on one more thing that is not
a constraint but decides it: **does it look like the last thing you build?**

---

## The second set — F to J, at the tier the Array actually sits at

**A to E were written in the wrong visual register, and the repo already said so.**
`building-spec-template.md`, "Technology tier sets the visual register", puts the
Array at **tier 4 — the goal**: *exotic; barely reads as machinery. Field effects,
superconducting elements, monolithic surfaces with no seams at all, contained
light doing the work.*

A to E are riveted, bolted, weathered, rust in the seams. That is **tier 0**, the
vocabulary of the landing-day machines — the Drop Crusher, the Ballast Drill, the
Crust Tap. Drawing the last building in the game in the same language as the
first one throws away the thing the ladder exists for: *"the player should be able
to read their own progress off the factory floor without opening the tech tree."*

So F to J are the same design space at tier 4. Not a coat of paint — the register
changes the forms, because at tier 4 a lattice mast becomes a cast emitter and a
strapped dewar becomes a solid block.

| | Tier-0 original | Massing | Charge lives in |
|---|---|---|---|
| **F** Field Ring | A | seamless torus round an open bore | light inside a containment gap |
| **G** Emitter Array | B | flat deck, four cast pylons | translucent bands up each pylon |
| **H** Cryo Monolith | C | one chamfered jacketed block | light under the surface, in cut channels |
| **I** Inlaid Plate | D | almost flat, set into the ground | inlaid traces filling to a central node |
| **J** Containment Well | E | a bowl, and a ring hovering over it | the ring rises and lights |

**The guard that matters for this set:** tier 4 must not become generic science
fiction. It is still Factorio — physical, weighty, industrial — and futuristic
through *material and finish*, not through neon strip lighting, holograms or
glowing panel lines. That sentence is in every F–J prompt for a reason.
