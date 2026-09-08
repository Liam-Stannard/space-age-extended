# Factorio Building — Art & Implementation Specification

**Ignition Array — v2, the silo camera.**

**Nothing here is adopted, and nothing has been replaced.**
`building-spec-ignition-array.md` is still the spec the shipped art was built
to, `concept/v3-canonical.png` is still the locked plate, and
`prototypes/core/endgame.lua` still points at the pieces cut from it. This
document is a second, complete proposal that exists to be compared against the
first one and then either taken up or thrown away. Adopting it means
regenerating the base plate, which is why it is written down rather than done.

**What prompted it.** The Array is a `rocket-silo` deepcopy, and the two were
photographed side by side in-engine on the Core — same ground, same light, same
zoom — using the screenshot rig in §20. They do not share a camera:

| | vanilla rocket silo | Ignition Array (v1) |
| --- | ---: | ---: |
| shaft mouth, width ÷ height | **1.485** | **1.127** |
| plate content, width ÷ height | 1.028 | 1.003 |
| plate above origin ÷ below origin | 0.96 | 0.99 |

The plates sit on their footprints almost identically. What differs is the
camera: at the silo's tilt our 200 px-wide mouth would be **135 px tall, not
176** — about 30% too round — and where the silo shows its far inner wall,
its floor and the cradle lying in it, ours shows a lid.

**This is our own rule working exactly as written,** not a defect that slipped
through. Rule zero in `building-spec-template.md` says the camera is *"mostly
roof, with only a shallow near face visible"*, and every Core plate is generated
under it. The rocket silo is one of vanilla's least roof-like buildings. So v1
matches its own family and diverges from the one vanilla prototype it is a copy
of — which a player can actually see, because a vanilla silo has no surface
conditions and can be built on the Core.

**Read §3.1 and §4 first.** The camera is not a slider. Tilting to the silo's
angle changes what the building *is* — §3.1 — and pretending otherwise produces
a squashed version of v1 rather than a different machine.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review, **mouth aspect measured at 1.45–1.52** | **passed — `concept/v3-r2-sheet.png`, mouth measured at aspect 1.48 and 6.55 tiles** |
| 1 | Canonical view | square | Silhouette approved against §3.1 and §17; mouth measured again | **NOT passed. The local cut drops the four dark cable-trunk elbows; the sheet's ground cannot be keyed** |
| 2 | Idle plate (unlit) | square | Same machine, nothing lit | blocked on 1 |
| 3 | Directional frames | — | n/a — no rotation, see §5 | n/a |
| 4 | Glow plates | — | **not generated** — derived by `tools/build-array-glow.py` | blocked on 2 |
| 5 | Effects plate | — | **not generated** — derived, see §12 | blocked on 2 |
| 6 | Icon | square | Legible at 32 px | blocked on 1 |

**Stages 4 and 5 no longer need a generator at all,** and that is the single
biggest change to the contract. v1 assumed a lit twin plate would be generated
and differenced. The tools written since do it from one plate — see §12 — so a
re-plate costs stages 0, 1, 2 and 6, and everything else rebuilds by running
four scripts.

### Where generation happens

Browser — ChatGPT's image tool. Template Appendices B and C: attach the four
standing style references and an example sheet as a format reference, and once
the design is locked **edit the approved file rather than re-prompting**.

**The four references, cut by `tools/extract-style-references.py`:**
`assembling-machine-3` for the house camera, `foundry` for the current finish
and detail density, `electromagnetic-plant` for coils and heavy cable runs as a
subject, and `rocket-silo` for the deep end of the camera range. They bracket
the tilt, which is exactly what this version needs to get right — one reference
teaches one camera, four teach the range.

**The rocket silo is a camera reference and nothing else here, and the prompt
must say so.** §3.1's anti-read is unchanged: the silo is still the wrong
machine, and at a shared camera it is a more dangerous reference than it was at
v1's, not a safer one. Label it, and name in the prompt what must not be taken
from it — its doors, gantry, rocket and hazard striping.

A measured number in a prompt has never once produced a measured number in a
plate, so every round is checked against §13's measurement rather than by eye.

### Round log

Six rounds, all stage 0. Recorded in §19. **`concept/v3-r2-sheet.png` is the
locked design** -- the v2 building with vanilla's hole geometry, which Liam named
v3. Its mouth measures aspect **1.48** against vanilla's 1.481, and **6.55 tiles**
against vanilla's 6.25.

---

# 1. Building Overview

Unchanged from v1 in every particular; repeated so this document stands alone.

**Building Name:** `Ignition Array`

**Internal Prototype Name:** `sae-ignition-array`

**Building Type:** `rocket-silo`, deep-copied from `rocket-silo`.

**Planet / Environment:** The Core. `surface_conditions = pressure 1–9`.

**Purpose:** The win condition. 100 Field Coil Segments
(`fixed_recipe = "sae-field-coil-segment"`, `rocket_parts_required = 100`),
buried and fired at once. `launch_to_space_platforms = false`.

**Technology Unlock:** `sae-ignition-array`, tier 4, 1200 geodynamic science
packs at 60 s.

**Recipe:** 200 welded plate · 500 kamacite plate · 10 coil assembly ·
200 processing unit · 4 arc masts, 120 s.

---

# 2. Gameplay Dimensions

Unchanged. `9×9`; collision `[-4.42, -4.20] → [4.42, 4.20]`; no rotation;
2 MW idle, **50 MW active**; electric; `mining_time = 5`.

**One gameplay fact belongs here rather than in the art sections, because it
decides whether any of this animation is ever seen.** Measured on the rig over
several thousand ticks: the Array assembles a rocket, reaches
`waiting_to_launch_rocket`, and **stays there indefinitely** while it goes on
making parts for the next one. It never fires by itself. Something has to call
`launch_rocket()`. Until that is resolved the ignition sequence — the iris, the
shaft light, the column — is art the player may never trigger. See §21.

---

# 3. Visual Design

## 3.1 Design Concept

**The change in one sentence: v1 is a lid you look down on, and v2 is an
emplacement you look into.**

That is not a restatement of the camera; it follows from it. A 9×9 deck lying
flush with the ground, drawn at the silo's tilt, is simply a squashed deck —
shorter than it is wide, and worse than v1 in every way. Vanilla's silo plate is
628×612, near-square, on the same 9×9 footprint, and it can be because the
building is *tall*: the height it has gives back the vertical extent the tilt
takes away. Tilt the camera without giving the Array height and the plate loses
a fifth of its canvas for nothing.

So the Array stops being flush. It becomes a **shallow armoured revetment sunk
into the crust**, with a raised rim wall standing about a tile and a half above
grade, and the iris at the bottom of it. The camera then shows the **far inner
wall** — lined, ribbed, cabled — which is the single feature that makes vanilla's
silo read unmistakably as a shaft rather than a disc. Everything the player
looks at is arranged on the inside of a bowl.

**The wrong machine it must not be.** Unchanged and, if anything, sharper here.
A rocket silo is a building whose entire language is *something leaving*: blast
doors, a gantry, a rocket standing in a hole, exhaust, a launch. Taking the
silo's camera makes the anti-read harder to hold, not easier, because the two
buildings will now share a projection and a shaft. **No gantry, no rocket, no
nose cone, no exhaust bell, no launch clamps, no countdown lights, no hazard
chevrons.** Vanilla's yellow-and-black diagonal striping is the single strongest
"launch pad" signal in the game and must appear nowhere.

**How the two stay distinguishable at a glance:**

| | rocket silo | Ignition Array v2 |
| --- | --- | --- |
| what the shaft holds | a rocket lying in a cradle | a closed iris, then nothing |
| where the machinery is | crowded around the rim, outside | on the inner wall, facing in |
| striping | yellow/black hazard chevrons | none; pale nickel edging only |
| the opening | rectangular, doors slide clear | circular, blades part on a diagonal |
| plan shape | irregular, cluttered, asymmetric | octagonal, radial, ordered |
| what it says | something is leaving | something is going down |

**Primary Visual Theme:** a buried coil array seen *into*, not down on.

**Overall Appearance:** an octagonal armoured revetment set into the crust,
filling the 9×9. Its rim wall rises about a tile and a half and is thickest on
the near side, where the camera shows its outer face; on the far side the camera
shows the wall's **inner** face, and that is where the machine lives. Ranged
around that inner wall, tilted inward and downward: the **segment cradles**,
each holding one pale blue field coil segment nose-down toward the centre. Below
them, the **capacitor banks** as a ring of ribbed drums standing against the
wall. At the bottom of the bowl, flat, a **closed iris** of overlapping armoured
leaves. Four **cable trunks** cross the rim at the diagonals and drop down the
inner wall to the shaft collar.

**Silhouette:** a heavy octagonal ring with a dark bowl inside it and a closed
eye at the bottom. At map zoom: a thick-walled ring, unmistakably a hole with a
lid, unmistakably not a launch pad.

**Visual Complexity:** `High`. Detail concentrates on the far inner wall, which
is where the camera is looking.

**Visual Age:** `Experimental` — over-instrumented, braced, cabled, monitored;
a machine that has never been fired.

---

## 3.2 Key Visual Features

* A **raised octagonal rim wall**, about 1.5 tiles above grade, with the near
  face showing outer armour and bolt courses, and the far face showing its
  **inner** lining — ribs, cable runs, catwalk, inspection lamps.
* A **closed iris** at the bottom of the bowl: heavy overlapping armoured
  leaves, seams radiating from the centre, drawn as a **1.48 : 1 ellipse** and
  measured, not judged.
* A **ring of segment cradles** on the inner wall, each tilted inward and down,
  each holding a pale-blue coil segment nose-first toward the shaft.
* **Capacitor banks** standing against the inner wall between the cradles:
  ribbed drums on end, cabled into a collar around the iris.
* **Four cable trunks** crossing the rim at the diagonals and running *down* the
  inner wall — the only elements that cross from outside to inside, and the ones
  that carry the assembly glow.
* A **shaft collar** where the wall meets the iris: the mounting ring, bolted,
  with the cradle lamps set into it.

### Signature Feature

**You can see into it, and what you see is a lid.** The camera shows the inside
of the far wall and, at the bottom of it, a closed eye. No other building in the
game shows you an interior arranged around a hole it intends to fire *into*.
Vanilla's silo shows you an interior arranged around a hole something intends to
leave through — the same view, the opposite meaning.

---

## 3.3 Colour Palette

Unchanged from v1. It is the Core's palette and it ties the Array to the Arc
Mast and Vent Pump; nothing about the camera touches it.

**Primary:** dark iron-nickel grey-brown machined casing, `#4A463F` → `#6E685C`.

**Secondary:** pale nickel-white `#B9B4A8` on bolt rings, deck edging, cradle
frames — and now also on the rim's top course, which is the building's
strongest line at map zoom.

**Accent — the segments:** field-coil pale blue `#8FA8D8`. The only cool colour,
marking the thing being consumed.

**Accent — copper:** `#8A5A32`, cable trunk terminations and capacitor busbars.

**Working Glow:** violet-white `#C9B6FF` → `#FFFFFF`, at the iris seams and
along the cable trunks. Must match `sae-arc`, which is vanilla's `lightning`
unmodified, because the arc masts powering this thing are in frame beside it.
Nothing glows at rest.

**Warning / Status Lights:** amber `#FFB13B`, in the shaft collar. See §21 for
what the engine will and will not do with these.

**One addition v1 did not need — the interior value range.** The inner wall is
in shadow and the shaft is darker still, so the plate carries a longer value
range than any other building in the set. Keep the inner wall between `#2A2823`
and `#4A463F` and the shaft mouth below `#1A1916`, or the bowl flattens out and
the whole point of the camera is lost.

---

# 4. Factorio Visual Style

### Required characteristics

* [x] 45-degree top-down Factorio perspective — **named in the prompt**
* [x] Strong readable silhouette
* [x] Appropriate visual scale
* [x] Industrial construction
* [x] Clear separation between major components
* [x] Subtle wear and grime
* [x] No photorealism · no text · no logos · no characters · no UI

**This is the *tall* camera case, and that is the whole difference from v1.**
v1 §4 says explicitly: *"do not add the Arc Mast's leaning-toward-the-viewer
clause — that is for towers, and using it here will tilt a 9×9 deck into a
wall."* That instruction was right for a flush deck and is wrong for this
version. Here the building has a rim wall with real height, the camera shows the
far wall's inner face, and the prompt must say so.

**The failure mode to watch for is the opposite of v1's.** v1 risked a deck
tilted into a wall. v2 risks a **bowl deep enough to read as a crater or a
cooling tower** — a well with no machine in it. The rim is a tile and a half,
not five; the bowl is shallow; the cradles and capacitor banks must stay legible
as equipment rather than dissolving into wall texture.

### Style Reference Buildings

1. `Rocket silo` (base) — **camera only**
2. `Nuclear reactor` (base)
3. `Electromagnetic plant` (Space Age)

**Reason for references:**
From the **rocket silo**, take the camera and nothing else: how deep the mouth
sits, how much inner wall is visible, how the far lining is lit against the near
rim. Its doors, gantry, rocket and hazard striping are the anti-read in §3.1 and
must not appear. From the **nuclear reactor**, the read of a large heavy
dangerous installation that fills its footprint and is one machine, not a
compound. From the **electromagnetic plant**, coils, windings and heavy cable
runs treated as a visual subject in their own right.

---

# 5. Building Orientation

## Required Directions

* [x] North · [ ] East · [ ] South · [ ] West

**Direction count:** `1`

`rocket-silo` has no direction and cannot be rotated. The design is radial, so
one frame carries everything — and at this camera the plate is no longer
symmetric top-to-bottom, which makes the single fixed orientation a help rather
than a constraint: near wall and far wall can be drawn as different things.

---

# 6. Sprite Assets Required

## 6.1 Main Building

**The slot table is now measured against the engine rather than proposed.**
Everything below has been built and photographed in-engine for v1; a re-plate
changes what the pieces look like, not which slots exist or how they behave.

| Slot | Frames | Plan |
| ---- | -----: | ---- |
| `base_day_sprite` | 1 | **Replace** — the rim, the inner wall, the cradles, the collar. **With the iris removed**: see the note below. |
| `shadow_sprite` | 1 | **Replace** — derived from the base plate. |
| `door_back_sprite` | 1 | **Replace** — the NE half of the iris, cut from the plate. |
| `door_front_sprite` | 1 | **Replace** — the SW half. |
| `hole_sprite` | 1 | **Replace** — the shaft below the blades. |
| `hole_light_sprite` | 1 | **Replace** — but see §21: this slot was never observed drawing. |
| `red_lights_back_sprites` / `red_lights_front_sprites` | 1 each | **Replace** — amber collar lamps. See §21 before relying on them. |
| assembly glow (`working_visualisations`) | 32 | **Replace, derived** — one entry, `sae-assembly`, half-resolution at `scale = 1.0`. See §12. |
| `rocket_glow_overlay_sprite` | 1 | **Replace, derived** — the bowl lit from its own shaft, additive. |
| `rocket_shadow_overlay_sprite` | 1 | **Suppress.** Light casts no shadow. |
| `base_front_sprite`, `satellite_animation`, `arm_01/02/03` | — | **Suppress.** |
| the five `*_frozen` plates | — | **Suppress.** Pressure-locked to the Core; it can never freeze. |
| `filter`, `engine`, `steam-1`, `steam-2`, `turbine` | — | **Suppress.** Launch-pad furniture on a world where nothing burns. |
| the rocket (`rocket-silo-rocket`) | — | **Replace the entity** — `sae-ignition-discharge`, a column of light. |

**The mouth and both leaves are vanilla's, adopted wholesale — see §13.** The
hole is 400 × 270 at shift (−0.15625, +0.5), which is 6.25 × 4.22 tiles and
aspect 1.481, and the two halves are cut from the approved plate using vanilla's
own leaf alpha masks at vanilla's own shifts. Everything about how they part is
then correct by construction rather than by measurement.

**The other piece of engine architecture that must be understood before drawing
anything: the deck has a hole in it.** Vanilla's `base_day_sprite` is a *ring* —
open `06-rocket-silo.png` and the middle is transparent. `hole_sprite` is the
shaft interior drawn inside that gap, and the two door sprites sit over the hole
and are slid apart by the engine. A closed iris painted into the base plate
therefore cannot work: the doors part at ignition and reveal a second, closed
iris underneath. v1 shipped exactly that mistake and it was found by rendering
the launch, not by reading the prototype.

So the plate is generated **with the iris drawn closed**, as a complete picture,
and `tools/cut-array-iris.py` then lifts the blades out and hands back a deck
with a hole, plus two leaves that recombine into the original pixel for pixel.
The generator never has to draw an open shaft or a half-open iris.

**Engine facts measured for v1, all of which carry over unchanged:**

* `door_opening_speed = 0.00392` → **255 ticks**, about 4.3 seconds, from shut
  to fully open.
* The leaves are slid apart along the **NE–SW axis** — vanilla's rest at
  x = +1.16 and x = −0.88 — so the seam runs NW–SE. On this building that puts
  the parting line along two of the cable trunks, which is where a seam wants to
  be. Confirmed by rendering: the iris opens as a widening diagonal slit.
* **The blades cannot turn, and the art has to admit it.** `door_back_sprite`
  and `door_front_sprite` are `Sprite`, not `Animation` — checked in the dump,
  they carry `filename`, `width`, `height`, `shift`, `scale` and no
  `frame_count`. The engine has exactly one move available to them: translating
  two still images apart over 255 ticks. A camera iris whose blades rotate open
  is not merely expensive here, it is impossible.

  v1 shipped a bladed disc cut in half and slid apart, and at 9×9 on a dark
  planet it read acceptably — but it is a lie, and at this camera the mouth is
  larger and more central, so the lie gets more visible rather than less. So the
  lid is redrawn honestly: **one heavy structural seam on the NW–SE diagonal**,
  with edge armour, a meeting lip and locking dogs, splitting it into an
  upper-right and a lower-left half. The overlapping bladed pattern stays as
  raised relief on each half, so it still reads as a shutter mechanism rather
  than a manhole cover, but the thing that opens is the thing that is drawn as
  opening.
* The leaves retract **under the deck** rather than sliding across it, so no
  half-leaf is ever seen stranded on the rim.
* `working_sound.sound_accents` name their visualisation by string. Empty the
  visualisations without clearing the accents and the data stage refuses to load
  with `Working visualisation "crafting" doesn't exist`.

---

## 6.2 Animation Layers

| Layer | Required | Animated | Frames |
| ----- | -------: | -------: | -----: |
| Main structure | ✓ | No | 1 |
| Machinery | — | — | — |
| Pistons | — | — | — |
| Belts | — | — | — |
| Fans | — | — | — |
| Lights | ✓ | engine-driven | — |
| Glow | ✓ | ✓ | **32** |
| Steam | — | — | — |

**32 frames, not v1's 64, and that is a measurement rather than a compromise.**
Vanilla's own crafting sheet is 208×210 at 64 frames — 2.9 Mpx. A glow across
this 608×602 plate at 64 frames is 23 Mpx, eight times what the engine spends on
the building this one is copied from. Drawn at half the plate's resolution and
shipped at `scale = 1.0` instead of `0.5` it is identical on screen at a quarter
of the pixels; at 32 frames that lands on 3.3 Mpx, level with vanilla.

**Animation FPS:** `animation_speed = 0.65`, inherited.

**Loop:** yes, ~1.6 s. Continuous while assembling; nothing at rest.

---

# 7. Layer Structure

```text
Building
│
├── Shadow
├── Base            rim wall, inner wall, collar — with the iris cut out
├── Hole            the shaft, drawn inside the cut
├── Doors           the two iris halves, over the hole
├── Static Machinery cradles, capacitor banks, segments
├── Lighting        amber collar lamps
├── Glow            assembly pulses; shaft light; the column
└── Effects         none baked
```

### Layer Notes

**Shadow:** derived from the base plate. The rim wall makes the building taller
than v1, so the shadow is longer and the canvas may need to grow — measure it,
do not assume it fits as v1's did. The Core's sky never moves; the shadow is
fixed.

**Base:** the rim, both wall faces, the collar, the grating. Almost the whole
machine. Generated with the iris in place and cut afterwards — §6.1.

**Static Machinery:** cradles, capacitor banks, and the coil segments in them.
All on the inner wall, all facing in.

**Pipes:** none. Coolant sleeves are painted, not plumbed; nothing fluid
connects to this building.

**Lighting:** the amber collar lamps, on the engine's red-lights slots. §21.

**Glow:** derived, never drawn — §12.

---

# 8. Input / Output Visualisation

A `rocket-silo` takes its parts from any tile touching the footprint and has no
fluid box, so there is no hard connection geometry and the plate carries no pipe
flanges or port positions. The cradles and trunks are structure, not connections.

**One thing that is positional, and it matters more at this camera than it did
at v1's.** `rocket_entity` rises from the centre. Nothing may occlude the shaft,
and — new to this version — **the near rim wall must not stand in front of the
rising column.** At a tilted camera a raised near wall is drawn over anything
behind and below it. Keep the near rim low enough, or open enough, that a column
leaving the shaft is not clipped by the building's own lip. This is the single
geometric risk the flat camera did not have, and it is checked by rendering, in
§17.

## Item Inputs

| Input | Location | Direction |
| ----- | -------- | --------- |
| `sae-field-coil-segment` ingredients | any edge of the 9×9 | inserter or bot |

## Item Outputs

| Output | Location | Direction |
| ------ | -------- | --------- |
| None | — | — |

## Fluid Inputs / Outputs

None.

## Energy

| Flow | Location | Connection Type |
| ---- | -------- | --------------- |
| In — 50 MW active | anywhere in a pole's supply area | electric network |

### Visual Requirement

The player must read **how full the array is** at a glance. At this camera the
cradle ring is on the far inner wall, tilted toward the viewer, which is a
*better* place to read fill state from than v1's flat ring — the segments are
seen face-on rather than end-on. Empty cradles must read empty.

---

# 9. Working Animation

## Animation Concept

Two events, and they are not the same one.

**Assembly** is continuous: violet pulses travel **inward** along the four cable
trunks, over the rim and down the inner wall to the collar, and the iris seams
take the light up and breathe in time. Continuous rather than per-completion,
because crafting time varies and anything depicting "a segment finished" drifts
out of step with the machine.

**Ignition** is one-shot and engine-driven: the iris opens over 255 ticks, the
shaft floods, and the column leaves.

**The trunk run is longer and better at this camera,** and it is the one place
the tilt straightforwardly improves the animation: at v1's flat camera the
pulses travel across a deck; here they cross the rim and drop down a wall, so
the light visibly goes *down* into the machine.

### Sequence

1. Idle — everything dark, iris shut, collar lamps out.
2. Assembly — violet pulses inward along the trunks and down the wall.
3. The iris seams glow faintly, in time with the pulses.
4. A segment completes — one more collar lamp lights and stays lit. **See §21:
   the engine may not do this.**
5. Full — the collar ring reading loaded.
6. Ignition — the iris opens, the shaft floods, the column rises, and the
   sequence does not return to idle.

**Frame Count:** `32` assembly glow · iris, lamps and column engine-driven

**FPS:** `animation_speed = 0.65`

---

# 10. Effects

## Working Effects

* [x] Glow
* [ ] Steam · [ ] Smoke · [ ] Sparks · [ ] Flames
* [x] Electrical arcs
* [x] Other: light rising from the open shaft at ignition

### Prohibited effects, and why

**No steam.** Inherited rather than invented: vanilla's silo ships two 64-frame
steam sheets and a turbine, all suppressed in §6.1. Pressure 5 is the Core's
defining number — nothing burns and nothing vents. A steam plume contradicts the
rule that refuses boilers and furnaces on the planet.

**No engine exhaust, no flame, no smoke.** All launch-pad furniture, all wrong
for a machine that fires downward. This applies to the column too: what leaves
the shaft is light, and the flicker at its foot is the discharge unsteadying,
not combustion.

**No sparks.** Same reason as the Arc Mast: sparks read as combustion or
grinding, and the colour budget belongs to the field.

**No hazard striping.** New to v2 and the most important prohibition in this
section. Yellow-and-black chevrons are the strongest launch-pad signal vanilla
has, and at a shared camera they would collapse the distinction §3.1 exists to
protect.

---

# 11. DALL·E Generation Requirements

**Canvas:** square. Largest size available. Transparent background.

**Attach all four standing references on every round** — `assembling-machine-3`,
`foundry`, `electromagnetic-plant`, `rocket-silo` — cut by
`tools/extract-style-references.py`. The prompts below name the silo explicitly
as a camera reference and say what must not be taken from it; keep that wording
if the prompt is edited. The mouth aspect is the entire purpose of this version
and prose has never produced it on its own, so check every round against §13's
measurement.

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio Space
Age building, every panel drawn from the game's characteristic 45-degree
top-down perspective, laid out as labelled panels on a dark charcoal
background, in the style of a game art bible page.

Panels: a large hero view of the building; an in-game icon panel showing it
simplified to a 64x64 item icon; a tile-grid panel showing it on a 9x9 tile
grid; three close-up detail panels showing the closed central iris, one segment
cradle holding a pale blue coil segment, and a cable trunk crossing the rim and
running down the inner wall; a layer breakdown row showing shadow, rim, inner
wall, cradle ring, iris and glow separated; a row of animation key frames
showing violet light pulsing inward along the trunks and down the wall; and a
palette strip of eight swatches.

The building in every panel is the same machine: a heavy octagonal armoured
revetment sunk into bare metallic ground, filling a nine by nine tile
footprint. Its rim wall stands about a tile and a half above the ground. The
camera is tilted enough that you look INTO the bowl and see the inner face of
the far wall, while the near wall shows only its outer armour. Ranged around
that inner face, tilted inward and downward, is a ring of short cradles, each
holding one pale blue coil segment nose-down toward the centre, with ribbed
capacitor drums standing against the wall between them. At the bottom of the
bowl lies a closed iris of heavy overlapping armoured leaves, drawn as a wide
flattened ellipse about one and a half times wider than it is tall. Four thick
armoured cable trunks cross the rim at the diagonals and run down the inner
wall to a bolted collar around the iris.

Dark iron-nickel grey-brown metal, #4A463F to #6E685C, with the inner wall
darker, between #2A2823 and #4A463F, and the shaft mouth darker still. Pale
nickel-white #B9B4A8 on the rim's top course and the bolt rings; pale blue
#8FA8D8 on the coil segments only; copper #8A5A32 at the cable terminations;
violet-white #C9B6FF only in the animation and glow panels.

It must read as a heavy buried electrical installation that fires downward into
the ground, never as a rocket launch pad: no rocket, no nose cone, no gantry,
no exhaust bell, no launch clamps, no rectangular blast doors, no countdown
lights, and above all no yellow-and-black hazard striping anywhere. Panel
labels and small caption text are wanted on this sheet. Painted semi-realistic
industrial game art. No characters, no photorealism.
```

---

## Master Concept Prompt

```text
Factorio Space Age industrial building sprite art, viewed from the game's
characteristic 45-degree top-down perspective: a heavy buried coil array,
standing alone, drawn as a game asset with no perspective vanishing point.

Camera: looking down from above and slightly from the south, tilted enough that
you can see INTO the building. Square to the tile grid: the near face parallel
to the bottom edge, the side faces parallel to the left and right edges. Not
rotated corner-on, and not a flat front elevation.

The attached images are STYLE AND CAMERA REFERENCES ONLY. Match their camera,
rendering, finish and level of detail; do NOT copy their design, shape, colours
or components. Take the rendering quality and detail density from the large
orange-and-steel machine and the blue coil machine. Take the CAMERA from the
large machine with the round hole in the middle: match how deeply it is tilted,
how much of its far inner wall is visible, and how flattened its circular
opening is drawn -- and take nothing else from it at all, in particular not its
doors, not its gantry, not the vehicle lying in it, and none of its yellow and
black striping.

The building is a heavy octagonal armoured revetment sunk into bare metallic
ground, filling a nine by nine tile footprint. Its rim wall stands about a tile
and a half above the ground, and is thickest on the near side, where only its
outer armour and bolt courses are visible. On the far side the camera sees the
wall's INNER face, and that is where the machine lives: a ring of short cradles
tilted inward and downward, each holding one pale blue coil segment nose-down
toward the centre, with ribbed capacitor drums standing against the wall
between them.

At the bottom of the bowl, lying flat, is a closed iris made of heavy
overlapping armoured leaves with hairline seams radiating from the middle. The
iris is drawn as a wide flattened ellipse, about one and a half times wider
than it is tall, because it is a circle seen at this tilt. Four thick armoured
cable trunks cross the rim at the diagonals and run down the inner wall to a
bolted collar around the iris.

Everything on this machine points down and inward: every cradle tilts toward
the centre, every cable runs down to the shaft, and the bottom is a closed lid.

Materials: dark iron-nickel grey-brown machined metal, the body reading around
#554E45 and staying inside #4A463F to #6E685C. The inner wall sits in shadow,
between #2A2823 and #4A463F, and the shaft mouth is darker than either. Pale
nickel-white #B9B4A8 confined to the rim's top course, bolt rings and cradle
frames; pale blue #8FA8D8 on the coil segments only; copper #8A5A32 only at the
cable terminations. Metal dust, scuffing and restrained wear.

State: cold and unlit. No glow, no light, no electricity visible anywhere, and
the status lamps dark.

It must read as a heavy electrical installation that fires downward into the
ground, and never as a rocket launch pad or anything preparing to take off: no
rocket, no nose cone, no gantry, no exhaust bell, no engine, no launch clamps,
no rectangular blast doors, no countdown lights, nothing pointing at the sky,
no fire, no smoke, no exhaust, no steam, and no yellow-and-black hazard
striping anywhere on it.

Painted semi-realistic industrial game art, strong readable silhouette, nine
tiles across, fully transparent background with nothing painted behind the
object, no text, no logos, no characters, no UI, no ground texture, no
background scenery, no baked drop shadow.
```

---

## Layer Prompts

Not needed. Everything below the base plate is derived from it — §12 — so there
is nothing to prompt for beyond the canonical view and its unlit twin.

---

# 12. Image Processing

### Processing Checklist

* [ ] Remove background
* [ ] Remove unwanted shadows/background objects
* [ ] Crop to building
* [ ] **Measure the mouth aspect — §13. Reject at 0 or 1 if outside 1.45–1.52**
* [ ] Match Factorio scale
* [ ] Align to tile grid
* [ ] Run `tools/cut-array-iris.py`
* [ ] Run `tools/build-array-shaft.py`
* [ ] Run `tools/build-array-glow.py`
* [ ] Run `tools/build-array-column.py`
* [ ] Optimise PNGs

Run `tools/process-building-art.py <plate> --report` before judging any plate,
and `--dekey` if it came back flattened onto a checkerboard.

**The four tools already exist and a re-plate does not change them.** This is
the part of the work v1 paid for that v2 inherits free. All four derive from one
approved plate, so re-generating that plate and re-running them rebuilds every
shipped asset:

| Tool | Reads | Writes |
| --- | --- | --- |
| `cut-array-iris.py` | `concept/base-closed.png` | `base.png` (holed), `door-back.png`, `door-front.png` |
| `build-array-shaft.py` | the fitted ellipse | `hole.png`, `hole-light.png` |
| `build-array-glow.py` | `concept/base-closed.png` | `working.png`, 32 frames |
| `build-array-column.py` | nothing | `column.png`, `column-glare.png`, `column-flame.png`, `ignition-glow.png` |

Each prints the exact `width`, `height` and `shift` for the prototype, so no
geometry is ever typed by hand.

**Three things must be re-measured for a new plate**, and they are the only
edits the tools need:

1. **`CX, CY` and the iris radii**, in `cut-array-iris.py` and shared by
   `build-array-shaft.py` and `build-array-glow.py`. Fitted by sampling the dark
   rim ellipse — v1's fit landed at centre (302, 276), semi-axes 100 × 88, with
   93% of sampled points dark, and the bolt ring at r = 88 by a brightness sweep,
   so the blades were cut at 83 × 73 and the collar left on the deck. **At v2's
   camera the two radii diverge sharply** — expect roughly 100 × 67 rather than
   100 × 88 — and the fitting code handles that without change.
2. **The seam angle** in `seam_mask`. It is a 45° cut because the engine slides
   the leaves on the NE–SW axis. That does not change with the camera, but a
   45° cut through a *flattened* ellipse is no longer a 45° line on screen;
   check the parting reads along the trunks and adjust the polygon if not.
3. **The trunk corridor test** in `build-array-glow.py`. It currently keeps
   copper pixels within `abs(abs(dx) - abs(dy)) <= 70` of the diagonals and
   outside `r = 150`. A tilted plate compresses the north–south diagonals, so
   this becomes an ellipse test rather than a square one.

**The glow is no longer differenced, and no lit twin plate is needed.** v1's
plan was Appendix C's lit-minus-unlit. What shipped instead finds the trunks in
the plate itself by their copper — §3.3 puts copper only on trunk terminations
and busbars — and masks a travelling pulse along them. One plate, no
registration risk, no second generation round.

---

# 13. Sprite Dimensions

**Tile Size:** `32` px in-game · **Scale:** `0.5` → `64` source px per tile

**Building Width:** `9` tiles → `288` in-game px → `576` source px

**Building Height:** `9` tiles of footprint, but the plate is taller: the rim
wall adds height above grade. Vanilla's silo is 628 × 612 on the same footprint.
Expect a similar canvas; **measure it, do not assume v1's 608 × 602.**

**Sprite Width / Height:** `[measure after stage 1]`

**Shift:** `[measure after stage 1]`

### The mouth: vanilla's geometry, adopted wholesale

**This supersedes the aspect chase, and it is the single most useful decision in
this document.** Four rounds were spent nudging a generator toward an aspect
ratio — 1.48, then 1.77, then 1.66, then 1.55 — while a second, harder question
sat unanswered underneath it: at what angle do the two halves actually part?
Both questions disappear if the mouth simply *is* vanilla's mouth.

Take the hole's size, shape and position from `rocket-silo`, and cut the two
halves with vanilla's own leaf alpha masks at vanilla's own shifts. Then the
pieces the engine moves are, geometrically, the pieces it was built to move: the
seam is right, the travel is right and the clearance is right by construction,
with nothing left to measure.

**The geometry, read off the engine's own prototype:**

| Slot | Source px | Shift (tiles) | On screen |
| --- | ---: | ---: | ---: |
| `hole_sprite` | 400 × 270 | −0.15625, +0.5 | **6.25 × 4.22 tiles**, aspect **1.481** |
| `door_back_sprite` | 312 × 286 | +1.15625, +0.375 | 4.88 × 4.47 tiles |
| `door_front_sprite` | 332 × 300 | −0.875, +1.03125 | 5.19 × 4.69 tiles |

Note the mouth sits **half a tile south of the entity origin**, not centred, and
that is inherited too.

**What this means for the plate.** The mouth is **6.25 tiles across a 9-tile
building — about seven tenths of its width.** For comparison, v1's iris is 2.59
tiles and the v2 sheets drew roughly 3.5 to 4. The rim wall becomes a fairly
narrow band around a large hole, and the building reads as mostly shaft. That is
a bigger change than any of the four v2 rounds attempted, and it is the change
that finally earns §3.1's claim that this is an emplacement you look into.

**The seam, measured off vanilla's leaf masks rather than inferred.** 226 sample
rows through the overlap of the two leaves give a seam at **≈51° from
horizontal**, leaning down to the right, with a **step partway along where the
two leaves interlock** — they do not meet on a straight line.

An earlier reading of this document said the seam was near-vertical, on the
grounds that the two leaves' resting shifts differ by (2.03, −0.66), an axis
17.9° above horizontal. That was wrong: the shift difference describes where the
leaves' bounding boxes sit, not where they part. The masks are the evidence.

### Checking a plate

| | width | height | aspect |
| --- | ---: | ---: | ---: |
| vanilla `01-rocket-silo-hole.png` content | 398 | 268 | **1.481** |
| v1 iris rim (fitted) | 200 | 176 | 1.136 |
| v2 sheet, round 4 | — | — | 1.55 |
| **target** | — | — | **1.481, by construction** |

**Fixed points.** Vanilla's plates, for reference only: `06-rocket-silo.png`
628 × 612, `00-rocket-silo-shadow.png` 656 × 600, `04-door-back.png` 312 × 286,
`05-door-front.png` 332 × 300, `01-rocket-silo-hole.png` 400 × 270. The
replacements need not match these sizes. Because every piece is cut from one
plate on one canvas, their shifts are derived together and printed by the tools.

**Spritesheet:** `working.png`, 32 frames at half plate resolution, 6 per row.
At v1's plate that was 1824 × 1806, 3.29 Mpx.

**Frame Count:** `1` base · `1` shadow · `1` each door · `1` hole ·
`1` hole light · `32` glow · `8` column flame

---

# 14. File Structure

```text
graphics/
├── icons/
│   └── ignition-array.png
└── entity/
    └── ignition-array/
        ├── concept/
        │   ├── base-closed.png    the approved plate, iris intact — the source
        │   └── ...                generated concepts, not shipped
        ├── base.png               the deck with the iris cut out
        ├── base-shadow.png        draw_as_shadow
        ├── door-back.png          iris, NE half     — cut from base-closed
        ├── door-front.png         iris, SW half     — cut from base-closed
        ├── hole.png               the shaft interior
        ├── hole-light.png         light standing in the shaft
        ├── working.png            32 frames, the assembly glow
        ├── column.png             the discharge, rocket_sprite
        ├── column-glare.png       rocket_glare_overlay_sprite
        ├── column-flame.png       8 frames, rocket_flame_animation
        └── ignition-glow.png      rocket_glow_overlay_sprite, additive
```

`concept/base-closed.png` is the important one and it is new since v1 was
written. It is the approved plate with the iris still on it, and it is what all
three cutting tools read. `base.png` is a *derived* file with a hole in it and
must never be treated as the master.

---

# 15. Factorio Prototype

**Prototype Type:** `rocket-silo` · **Prototype Name:** `sae-ignition-array`

### Graphics

Implemented and in `prototypes/core/endgame.lua`. A re-plate changes the numbers
in these tables, not their shape, and every number is printed by the tool that
writes the file it points at.

```lua
local IA = "__space-age-extended__/graphics/entity/ignition-array/"

array.base_day_sprite   = { IA .. "base.png",   ... }   -- the deck, holed
array.shadow_sprite     = { IA .. "base-shadow.png", draw_as_shadow = true, ... }
array.door_back_sprite  = { IA .. "door-back.png",  ... }
array.door_front_sprite = { IA .. "door-front.png", ... }
array.hole_sprite       = { IA .. "hole.png",       ... }
array.hole_light_sprite = { IA .. "hole-light.png", draw_as_glow = true, ... }

array.rocket_glow_overlay_sprite =
  { IA .. "ignition-glow.png", blend_mode = "additive", draw_as_glow = true, ... }

array.graphics_set = { working_visualisations = { {
  name = "sae-assembly", render_layer = "object", draw_as_glow = true,
  light = { intensity = 0.55, size = 14, color = { r = 0.62, g = 0.48, b = 1.0 } },
  animation = { filename = IA .. "working.png", blend_mode = "additive",
                width = 304, height = 301, frame_count = 32, line_length = 6,
                animation_speed = 0.65, scale = 1.0 },
} } }
```

### Other Visual Properties

```text
The rocket:
array.rocket_entity = "sae-ignition-discharge", a deep copy of
rocket-silo-rocket with every vehicle sprite, flame, smoke plume and takeoff
sound removed, and three slots replaced: rocket_sprite (the column),
rocket_glare_overlay_sprite (its bloom) and rocket_flame_animation (the flicker
at its foot, 8 frames -- the only animated slot the rocket prototype has).

Two inherited numbers on it are wrong for a column of light and were corrected
by measurement rather than reasoning:

  rocket_initial_offset            { 0, 3.5 } -> { 0, 0 }
      Vanilla's rocket starts three and a half tiles SOUTH of the silo origin,
      low on the pad. Inherited, the discharge appeared eleven tiles south of
      the deck as a bright smear on the ground beside the machine.

  rocket_visible_distance_from_center   2.75 -> 1.0
      How far the rocket must travel before the engine draws it, which is what
      hides a rocket still inside its building. Set to 0 -- on the reasoning
      that a column standing in the shaft should be visible -- the parked
      discharge stood lit in the open shaft indefinitely, because the Array
      reaches waiting_to_launch_rocket and stays there. See section 21.

Lights:
red_lights_back_sprites / red_lights_front_sprites, as the amber collar lamps.
See section 21 before designing around cumulative lamps.

Fluid Boxes: none.       Circuit Connections: inherited.
```

---

# 16. Icon

**Icon Required:** ✓ · **Icon Size:** `64×64`

**Icon Concept:** the same compression as v1 — dark octagon, bright ring, closed
iris, one violet seam, trunks dropped because four diagonals turn the silhouette
into a star at 16 px. **The icon changes with the camera**: at v2 it gains a
visible rim wall and a flattened eye, and it must be re-derived from the new
plate. It is not shared between versions.

### Icon Prompt

```text
Factorio "Space Age" item icon. A small rendered industrial object on a
workbench: a heavy octagonal armoured revetment with a raised rim wall, seen
from above and slightly from the front so you look into it. Ranged around the
inner face of the far wall is a ring of short cradles holding pale blue coil
segments; at the bottom lies a closed iris cap drawn as a wide flattened
ellipse, with one hairline violet-white seam across it. Dark iron-nickel
grey-brown metal, #4A463F to #6E685C, with a darker interior and pale
nickel-white bolt rings.

Semi-realistic sci-fi industrial painting, not flat, not cartoon, not
photo-real. Three-quarter view from slightly above, close to the game's
characteristic 45-degree top-down perspective. Soft single-direction lighting
from the upper left, visible specular highlight, subtle ambient occlusion,
gentle drop shadow behind the object. The object fills roughly 85% of the
frame, centred. Bold simple silhouette that still reads at very small size.
Fully transparent background, square canvas, no ground or platform under the
object, no text, no logos, no watermark, no border, no scene elements.
```

---

# 17. Visual QA Checklist

### Building

* [ ] **Mouth aspect measured at 1.45–1.52** — the reason this version exists
* [ ] Correct tile size — fills 9×9 without overflowing it
* [ ] Rim wall reads as about 1.5 tiles, not as a crater or a cooling tower
* [ ] Far inner wall is visible and carries the machinery
* [ ] Near rim shows outer armour only
* [ ] Correct scale · clear silhouette · looks like Factorio
* [ ] Bare metal — no vegetation, no snow
* [ ] **No yellow-and-black hazard striping anywhere**
* [ ] Does not read as a rocket launch pad, a nuclear reactor, or a radar
* [ ] Fill state is readable — empty cradles look empty

### Animation

* [ ] Assembly glow travels **inward**, over the rim and down the wall
* [ ] Iris halves recombine into the approved plate pixel for pixel
* [ ] Iris parts on the NW–SE seam, along the trunks
* [ ] Static components remain static
* [ ] No steam, no engine, no turbine anywhere

### Generated-art defects

* [ ] Alpha measured clear by `--report`, never judged from a preview
* [ ] Palette measured inside `#4A463F`–`#6E685C`, interior inside `#2A2823`–`#4A463F`
* [ ] No baked drop shadow, no ground plane
* [ ] Nothing glows on the base plate

### In-Game — photograph it, do not reason about it

Every one of these is checked with the rig in §20, against a vanilla rocket silo
placed beside it on the Core.

* [ ] **Mouth aspect matches the silo's on screen, side by side**
* [ ] The near rim does not clip the rising column — §8
* [ ] Doors and hole align with the base through the whole 255-tick opening
* [ ] Shadow aligns and does not double
* [ ] Inserters reach the deck edge correctly
* [ ] Recognisable at map zoom as the endgame building
* [ ] **Judged at night.** The Core is held at `daytime = 0.5` with
      `freeze_daytime`, so that is the only light this building is ever seen in.

---

# 18. Final Asset Checklist

```text
[ ] Concept sheet
[ ] Master concept / canonical view
[x] Directional sprites          n/a, one direction
[ ] concept/base-closed.png      the approved plate, iris intact
[ ] base.png                     tools/cut-array-iris.py
[ ] door-back.png / door-front.png   tools/cut-array-iris.py
[ ] base-shadow.png
[ ] hole.png / hole-light.png    tools/build-array-shaft.py
[ ] working.png                  tools/build-array-glow.py
[ ] collar lamps
[x] column.png and friends       tools/build-array-column.py -- plate-independent
[ ] Icon
[x] Factorio prototype           already wired; sizes and shifts re-measured
[ ] In-game test, beside a vanilla silo, at night
```

---

# 19. Design Notes / Iteration History

| Round | Asset | What came back | Verdict | Fix asked for |
| ----- | ----- | -------------- | ------- | ------------- |
| 1 | sheet | **The measurement landed first time: the iris is drawn at aspect 1.48**, against a 1.45–1.52 target and vanilla's 1.485. Checked by overlaying candidate ellipses at 1.30, 1.48 and 1.65 on the hero panel — 1.48 traces the bolt ring exactly, the other two miss. The prohibitions held too: **no hazard striping anywhere**, and it reads as an installation firing downward rather than a launch pad. Rim and inner wall are separated and named in the layer breakdown. The palette is the specified one. All requested panels are present, and the format example's layout came across **without** its palette or design bleeding in, which is the failure this pipeline has hit before. | **Accept the camera. Not yet the design.** | Four corrections: (1) it is named PLANETARY IGNITION SHAFT — my prompt never gave it a name, so give it one, `Ignition Array`; (2) the bowl is too shallow — the iris reads as a lid near the top rather than lying at the bottom of a shaft, and §3.1 wants the far inner wall standing above it and carrying the machinery; (3) the cradles are upright drums ranged around the ring rather than **tilted nose-down toward the centre**, which is the same correction the v1 sheet needed at its round 1; (4) the cable trunks are wrong — the brief asks for **four** thick armoured trunks at the diagonals, and it drew many black rubber hose bundles all round the rim, which read as plumbing rather than heavy electrical runs and pulled an unrequested eighth swatch into the palette. Minor: the plan reads as a rounded square rather than an octagon. |

| 2 | sheet | Four of the five corrections landed. The name is right, the plan is now an unmistakable **octagon** in both the hero and the top view, the cradles are **tilted inward and downward** with their segments leaning over the shaft, and the rubber hose bundles are gone along with their palette swatch — back to the seven specified colours. Still no hazard striping. **But the measurement broke.** Asked to make the bowl deeper while keeping the iris exactly as drawn, the generator deepened it by *tilting the camera further over*, and the mouth flattened from 1.48 to **1.77** — now as far past vanilla's 1.485 as v1 was short of it. | **Design accepted. Camera must come back.** | Two things. (1) **Depth must come from wall height, not from camera tilt.** Say so explicitly: keep the camera exactly where round 1 had it, and get the extra depth by making the rim wall taller. Give the target as a proportion the generator can see rather than a number it cannot — the iris is about one and a half times wider than tall, *not* nearly twice. (2) The trunks are still eight or so armoured conduits ranged around the rim; there must be exactly **four**, one at each diagonal corner. |

| 3 | sheet | **The split lid landed exactly as asked**: one heavy structural seam across the lid with edge armour down both sides, a meeting lip and locking dogs, with the bladed pattern kept as raised relief on each half. The `DETAIL: CLOSED IRIS` panel shows the seam, and `DETAIL: CABLE TRUNK` was replaced with `DETAIL: IRIS OPEN` showing the two halves slid apart with the shaft between them. Everything held from round 2 — name, octagon, seven swatches, no striping — and the rim wall is taller, so the bowl is deeper without the camera moving as far. **The aspect came back from 1.77 to 1.66**, measured the same way. | **Closest yet. Two things left.** | (1) The aspect is still outside 1.45–1.52 — one more nudge, and it is worth saying "a little less flattened again" rather than giving a ratio, because ratios have not moved it and side-by-side comparisons with its own earlier sheets have. (2) **The seam is on the wrong diagonal.** It is drawn lower-left to upper-right; it must run **upper-left to lower-right**. This is not taste: the engine slides the two leaves apart along the NE–SW axis, so the seam has to be perpendicular to that, and a seam on the other diagonal would have the halves parting the wrong way. Minor: the cradles have drifted back to standing on top of the rim pointing outward, rather than leaning inward over the shaft as they did in round 2. |

| 4 | sheet | **Everything asked for landed, in one pass.** The seam is on the correct diagonal — upper-left to lower-right — which is the one the engine can actually part, and the `IRIS OPEN` panel was mirrored with it. The cradles lean inward over the lid again, mounted on the inner wall. Name, octagon, trunks, seven swatches, taller rim wall and the absence of hazard striping all held. **Aspect 1.55**, measured the same way as every round before it. | **Candidate design.** | Nothing outstanding. One residual, stated rather than chased: 1.55 is just outside the 1.45–1.52 band and 4% off vanilla's 1.485. Two further rounds spent on it would each risk regressing something that has already landed — round 2 broke the aspect fixing depth, round 3 drifted the cradles fixing the seam — and the difference is not visible without the two buildings side by side. It also does not propagate: `cut-array-iris.py` fits the ellipse off whatever plate it is given, so a 4% deviation costs registration nothing. |

**Aspect across the four rounds**, all measured by overlaying candidate ellipses
on the drawn bolt ring rather than by eye:

| Round | Aspect | Note |
| ---: | ---: | --- |
| 1 | **1.48** | on target first time |
| 2 | 1.77 | broke it — depth was taken from camera tilt |
| 3 | 1.66 | recovering, seam on the wrong diagonal |
| 4 | **1.55** | seam correct, cradles correct; a hair flat |
| — | *1.485* | *vanilla rocket silo, the thing being matched* |
| — | *1.127* | *v1, for comparison* |

| v3-1 | sheet | The design change landed in one pass. **The mouth is now the building**: a narrow rim band around a large lid, which is the read §3.1 has been arguing for since this document was written. The seam is steeper and has the **interlocking step**, still running upper-left to lower-right. The cradles were re-fitted rather than merely scaled — shorter, set into the inner wall, still leaning in over the lid, not overlapping it and not pushed off the footprint. Name, octagon, trunks, seven swatches, every panel and the absence of striping all held. Lid aspect measured **1.41**, the closest any round has come to vanilla's 1.481. | **The design is right. The size overshot.** | Asked for seven tenths of the building's width and got **0.84** — a lid of about **7.6 tiles on a 9-tile machine**, against vanilla's **6.25**, so roughly 20% too big. That matters now rather than being a nicety: the halves are to be cut with vanilla's leaf stencils, so a plate drawn around a 7.6 tile lid would leave a ring of orphaned lid material on the deck once a 6.25 tile hole is taken out of it. One more nudge down. |

| v3-2 | sheet | **Attaching a diagram did in one round what four rounds of prose could not.** The mouth is measured at **aspect 1.48** against vanilla's 1.481, and **6.55 tiles wide** against vanilla's 6.25 — inside 5% on size and essentially exact on shape. Everything from v3-1 held: the stepped seam upper-left to lower-right, the cradles leaning in over the lid, the octagon, the trunks, the seven swatches, every panel, no striping. | **Accepted. This is the design.** | None. Stage 1, the canonical view, is next. Keep attaching `concept/ring-geometry-reference.png` to every round from here so the mouth cannot drift again. |

**Mouth across every round**, all measured by overlaying candidate ellipses on
the drawn ring:

| Round | Aspect | Mouth width |
| --- | ---: | ---: |
| v2 r1 | 1.48 | — |
| v2 r2 | 1.77 | — |
| v2 r3 | 1.66 | — |
| v2 r4 | 1.55 | ~4 tiles |
| v3 r1 | 1.41 | 7.58 tiles |
| **v3 r2** | **1.48** | **6.55 tiles** |
| *vanilla rocket silo* | *1.481* | *6.25 tiles* |

| s1-1 | canonical view | Presentation is right and measured so: `process-building-art.py --report` gives **25% clear alpha, "transparency ok"**, body metal **#504337 at luminance 69, inside the palette**, square canvas, no text, no baked shadow, nothing lit. | **Rejected. The mouth regressed.** | The mouth came back at **aspect 1.12** — back where v1 was, and undoing the six rounds that got it to 1.48, *even though the geometry diagram was attached again*. The composition drifted too: the rim became a uniform ring of blocks, the four cable trunks merged into it instead of crossing it, and the cradle count changed. It redesigned rather than reproduced. **The lesson is that attaching the approved image is not enough on its own once the canvas and background also change** — too much is being asked to move at once. Next attempt should change one thing at a time: ask only for the background to be removed, and forbid any change to the building whatsoever. |

| s1-2 | canonical view | Asked for **one change only** — delete the background, alter nothing else, "if you laid your result over the attached image they should line up exactly" — with the approved building as the sole attachment and the geometry diagram deliberately withheld. Presentation again correct: **23% clear alpha, transparency ok**, body metal **#534438 at luminance 70**, inside the palette. | **Rejected. Same regression.** | The mouth came back at **1.13**, and the rim was rebuilt as a uniform ring of blocks with the trunks merged into it, exactly as in round 1. **Two different framings of the request produced the same failure, so this is not a prompting problem.** The image tool does not edit; it re-renders from what it sees, and a re-render re-interprets proportion every time. Stop asking it. Key the background out locally instead — the approved hero is already the right building at the right proportions, and a local cut cannot drift. |

**The rule this establishes**, and it belongs in the template rather than only
here: *a generator can be asked to change a design or to change a presentation,
but not to preserve one while changing the other.* Background removal, canvas
changes and crops are image operations and belong in `tools/`, not in a prompt.

| s1-3 | canonical view | **Cut locally by `tools/cut-plate-from-sheet.py` instead of asked for.** `--report`: **19% clear alpha, transparency ok**, 656 x 631. The mouth measures **1.48** — unchanged, as it must be when nothing is redrawn. | **Passed. `concept/v3cam-canonical.png`.** (Not `v3-canonical.png` -- that name was already taken by v1's own third round, which is a genuine trap in this folder.) | Two small things, neither blocking: a thin dark fringe survives along part of the outer edge where the closing dilated past the silhouette, and the body-metal sample reads luminance 64 against a palette floor of 70 because the cut includes more of the dark recesses than a sheet crop does. Both are measurement artefacts of the cut, not of the art. |

**Why the local cut is not enough either, measured.** Sampled across the plate,
the building's own dark parts run **luminance 18-59** and the sheet's ground runs
**20-64**. They are the same range. There is no threshold, no neighbour-relative
growth and no closing radius that separates them: tighten it and the four dark
cable-trunk elbows at the diagonals vanish, because they are darker than much of
the ground; loosen it and slabs of ground stay welded to the silhouette. Six
parameter settings were tried and every one landed on one side or the other of
that trade.

**The fix is upstream, not in the tool.** The sheet is drawn on a dark mottled
ground, and that is what makes the cut impossible. A sheet -- or a hero panel --
drawn on a plain, bright, contrasting ground keys in one pass with no tuning at
all. Asking for that is a *presentation* change to a sheet, which is the one
thing this generator has been reliable at; it is the design-preserving edit it
cannot do. Ask for the approved building on flat magenta.

**The resolution worry was unfounded, and the number is worth recording.** The
building's drawn footprint is 594 px across on the sheet. That footprint is 9
tiles, so the plate carries **66 px per tile against the 64 a `scale = 0.5`
sprite needs** — a 3% *oversample*. It downscales by 0.97 to land exactly on 576
px, losing nothing. A generated plate would have given more headroom, but there
was never a shortfall.

**How the cut works, since the technique generalises.** The background cannot be
keyed by brightness: the shaft inside the building is exactly as dark as the
ground outside it, and a threshold punches straight through the lid. So the tool
grows inward from the canvas border and the growth is *neighbour-relative* -- a
pixel joins the background only if it is within a few levels of the pixel it was
reached from. The sheet's ground is a slow mottle and passes everywhere; the
building's edge is a hard step and stops it. Then three passes finish it: a
morphological closing wide enough to seal the shadow channels between the rim
blocks, which the growth otherwise pours through; a fill of anything transparent
the border cannot reach, because a building has no enclosed holes; and a
largest-component filter to drop the scraps of sheet ground that a vignette had
cut off from the border.

---

## What is left on the Ignition Array

The blocker is solved and the method is known. What remains is assembly.

**The breakthrough, so it is not lost:** eight re-renders failed to hold the
mouth at 1.48 — every one reverted to 1.12–1.34 — until the generator was handed
**vanilla's actual hole sprite on a flat magenta field** and asked, in one
sentence with no negatives, to *build the machine around it*. That produced 1.48
first time. Describing a shape does not survive a re-render; giving it the shape
as an object does. Flat magenta then makes the cut trivial, where the old dark
sheet ground was unkeyable — the building's own dark parts (luminance 18–59) and
that ground (20–64) are the same range.

**Assets in hand**, all in `concept/`:

| File | What it is | Measured |
| --- | --- | --- |
| `v3-around-hole.png` | the deck ring, built around the true hole, on magenta | mouth **1.48**, 5.87 tiles |
| `v3-lid.png` | the closed lid, stepped seam upper-left to lower-right, on magenta | **1.346** |
| `v3-r2-sheet.png` | the locked design sheet | mouth 1.48, 6.55 tiles |
| `ring-geometry-reference.png` | the 9x9 grid with vanilla's opening on it | 6.25 x 4.22 tiles |

**Remaining, in order:**

1. **Square the lid's aspect.** It came back at 1.346 against 1.481. A lid is an
   ellipse, so scaling it vertically by 0.909 lands it exactly — a safe local
   operation on an isolated symmetric object, not a redraw. No further round.
2. **Cut both plates.** `cut-plate-from-sheet.py --key` on each; the magenta
   keys cleanly (16% clear alpha, no holes, no ledges).
3. **Excise vanilla's shaft pixels** from `v3-around-hole.png`. They are Wube's
   art and must not ship. This costs nothing: §6.1 requires the base plate to be
   a *ring* with a hole through it anyway, so the cut removes them as a matter of
   course. Verify nothing of it survives before shipping.
4. **Split the lid** into `door-back.png` and `door-front.png` on its drawn seam,
   using vanilla's leaf stencils per §13.
5. **Draw the shaft** (`hole.png`) and its light — `build-array-shaft.py` already
   does this; re-run on the new ellipse.
6. **Re-derive the glow** — `build-array-glow.py`, whose trunk-corridor test needs
   the ellipse update noted in §12.
7. **Measure and wire**, then stages 2 and 6 (unlit plate, icon).

**One bug in the tool to fix first.** `cut-plate-from-sheet.py` assumes the crop
border is background: its hole-fill treats any transparency the border cannot
reach as an enclosed hole. Crop even a few pixels outside the magenta and the
whole background is "filled" and the key silently returns nothing. Crop inside
the key colour, or make the fill notice when the border is not background.

---

### Version 2 — why this document exists

Written after the v1 art was implemented, rendered in-engine and photographed
beside the prototype it is a copy of. Three things are settled and should not be
relitigated by whoever runs the first round:

1. **The camera change forces a design change.** Tilting a flush 9×9 deck does
   not give the silo's read; it gives a squashed deck. The Array has to gain a
   rim wall and an interior, or the tilt costs a fifth of the canvas and buys
   nothing. §3.1.
2. **The anti-read gets harder, not easier.** Sharing a camera and a shaft with
   the rocket silo removes two of the things that currently keep them apart. The
   striping ban in §10 and the difference table in §3.1 are load-bearing.
3. **The pipeline survives the re-plate.** Four tools derive every shipped asset
   from one approved plate, and only three measured constants change. That is
   what makes this version cheap enough to consider at all: stages 0, 1, 2 and 6,
   then run four scripts.

### What is *not* being claimed

That v1 is wrong. It is internally consistent, it matches the Core set, and it
matches template rule zero. The case for v2 is narrow: it matches the vanilla
building it is a copy of, and the player can put the two side by side.

### Final

`[not decided]`

---

# 20. The screenshot rig

New since v1, and the reason anything in this document is measured rather than
argued. The headless server cannot render — `game.take_screenshot` returns
without error and writes nothing — so the *graphical* binary is run under a
virtual framebuffer instead:

```
xvfb-run -a -s "-screen 0 1280x1024x24" env LIBGL_ALWAYS_SOFTWARE=1 \
  factorio --load-game <save> --mod-directory <mods> --config <config>
```

Three things make it work:

* **A `steam_appid.txt` in the working directory.** Without it the Steam API
  answers "Steam requires game restart" and re-launches through Steam.
* **A scratch mod** that builds the Array, powers it, drives it through a launch
  and calls `game.take_screenshot` at each stage.
* **A watchdog.** The client has no way to quit itself from script, so the run
  is ended by watching its own log for the rig's DONE line and killing it.
  Otherwise it holds the write-data lock and the next run cannot start.

Every claim in §13 and §21 was measured this way. Software GL makes each
screenshot expensive, so shoot the sequence and nothing else.

---

# 21. Open engine questions

Three things the v1 work turned up that this version does not resolve, all of
which affect what is worth drawing.

**1. ~~The Array never fires by itself.~~ Resolved: it does not need to.** The
silo GUI carries a Launch button, disabled with "Rocket is not ready" below 100%
and available at it — checked in a real game rather than inferred.
`launch_to_space_platforms = false` removes the destination, not the trigger, so
the ignition sequence is art the player *will* see. The original note follows.

**The Array never fires by itself.** It assembles a rocket, reaches
`waiting_to_launch_rocket` and stays there indefinitely — measured over several
thousand ticks — while it goes on making parts for the next one. Something must
call `launch_rocket()`. With `launch_to_space_platforms = false` there is no
destination to send it to, so whether the player has any way to trigger it needs
checking in a real game. **Until this is answered, the entire ignition sequence
is art that may never play.** It is a gameplay question, not an art one, but it
sets the value of §9 steps 4–6.

**2. `hole_light_sprite` was never observed drawing.** It is wired, the file
exists, and across two full rendered launch sequences no light from it appeared
at any phase. Either the engine gates it on something we do not trigger, or it
is drawn only for a rocket whose engine is lit — ours has no flame. The
ignition read currently rests on `rocket_glow_overlay_sprite` and the column
instead. Worth an isolated test before drawing a plate for it.

**3. Cumulative collar lamps may not be possible.** §9 step 4 wants one lamp per
completed segment, lit and staying lit. `red_lights_back_sprites` is a single
sprite driven by `light_blinking_speed` and `times_to_blink`, which is a blink
cycle, not a counter. If the engine will not light them progressively, fill state
has to be carried by the cradles and the assembly glow instead — which the
camera in this version happens to help with, since the cradles are seen face-on.
