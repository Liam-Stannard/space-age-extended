# Option R — the Suspended Core

> ## ADOPTED — this is the Ignition Array
>
> Chosen 2026-09-08 from twenty concepts across four sets. The sheet and its
> panels are locked at `concept/ignition-array/adopted/`.
> Everything else in this directory is a rejected option and can be deleted.

### Why it won

It is the only option that clears every constraint at once. Measured against the
four vanilla style references by `tools/check-sheet-style.py`, all three bands
pass — luminance 65.3 (band 63.2–90.4), saturation 0.262 (0.230–0.490), detail
density 0.185 (0.144–0.261) — and its base flatness is 0.904, so it is drawn
square-on to the tile grid where P and S were drawn corner-on.

Beyond the numbers: no rocket read, a base that actually fills its 9 × 9 instead
of leaving bare ground inside it, an unmistakable silhouette, and a charge that
works in two channels at once.

### Four things to fix in production, found on review

1. **It glows at rest, and it must not.** The hero and top-down panels both show
   violet in the drum beneath the sphere and at the equator band. `base_day_sprite`
   has to be the *unlit* machine; the glow is a separate overlay driven from
   `control.lua`. `R-charge-000.png` is the correct reference for the base — the
   hero is effectively the building at about 25%.
2. **The sphere is not suspended.** The brief asked for open air between sphere
   and base; the render puts a lit drum under it. That is a change to the idea —
   "held in the air" was this option's headline — but it is the better machine:
   it gives the charge somewhere to live and it is far easier to draw a shadow
   for. Recorded as a deliberate departure, not a defect.
3. **The discharge frame has a smoke plume.** The Core has no atmosphere to carry
   one and `pressure = 5` means nothing burns. The discharge is light and arcs
   only; the cloud goes.
4. **The sheet cannot be keyed.** It is on charcoal, and this building's own
   darks overlap the ground's luminance — the exact failure recorded in the plate
   plan. Production needs a magenta render, generated as an *edit of the locked
   image* rather than a fresh prompt.

**One line.** A colossal sphere held off the ground in the middle of a heavy frame, with clear air all round it.

*Set 4: built for spectacle. Same register as set 3.*

## The idea

A vast object held in the air is the single most arresting silhouette
available, and the gap under the sphere is the part that sells it: you can see
daylight where support should be.

It is also the clearest possible statement that the machine has done something
the player could not do forty hours ago.

## Why this is a spectacle

The Array is the last building in the mod and the thing the whole Core exists to
let you build, and sets 1–3 all drew it as a machine rather than an event.

The footprint stays 9 × 9 and nothing spills sideways — that constraint stands.
**Height is where the drama goes**, which is how Factorio itself does it: the oil
refinery and the big mining drill both draw well above their collision boxes, and
that is not the overhang that was rejected on the r4 deck. Human-scale cues —
walkways, handrails, ladders, access hatches, warning stripes — are what make the
mass read as enormous rather than as a small object drawn large.

Everything the Core demands still holds: a dead dynamo rather than a rocket,
nothing that burns, braced for gravity 50, cold because it is superconducting.

## The charge display

the recessed bands on the sphere filling with violet from the bottom of
the sphere upward, the whole shell lit and the gap beneath it glowing at 100%

## Concept Sheet Prompt

```text
FACTORIO SPACE AGE BUILDING -- CONCEPT SHEET

== CAMERA ==
Match the attached vanilla sprites exactly: steeply down from above, MOSTLY ROOF
with only a shallow near face. Square to the tile grid. Not rotated corner-on.
Not a flat front elevation.
This building is TALL, so it leans into frame and you see more of its near face
than you would on a squat machine -- but the camera itself does not change and
the base is still square to the grid.
The four attached sprites are style references only: match the camera, rendering,
finish, LEVEL OF DETAIL and COLOUR TEMPERATURE; do NOT copy the design, shape or
components.

== BUILDING ==
Ignition Array - option R, Suspended Core.
A colossal sphere held off the ground in the middle of a heavy frame,
with clear air all round it.

== SCALE ==
- THE LAST BUILDING IN THE GAME. It must read as an event, not as another
  machine. It towers over everything around it.
- Its base occupies a 9x9 tile square and NOTHING spills sideways past that
  square. Height is where the drama lives: the structure rises to roughly one
  and a half to two times the base's width.
- Put human-scale cues on it so the mass reads as enormous rather than as a
  small object drawn big: service walkways, handrails, ladders, access hatches,
  small inspection platforms, warning stripes at the base.
- The silhouette must be readable and distinctive at a glance, from far away,
  with no detail at all.

== FORM ==
- A heavy square machined frame with four thick towers at its corners
- Four massive arms reaching inward and upward from the towers to grip a single
  enormous sphere suspended in the middle, well clear of the ground
- Open air visible between the sphere and the base underneath it
- The sphere is a machined shell: segmented plates, flush seams, recessed bands,
  a jacketed equator
- Service platforms and handrails on the towers, ladders up the outside

== COLOUR ==
- Body casing: #4A463F to #6E685C, WARM low-value iron-nickel, machined not cast
- Pale nickel-white: #B9B4A8, on chamfers, covers and end caps
- Copper and brass: #8A5A32, VISIBLE and used freely on bus runs, joints and
  fittings. This is what keeps the building warm.
- Cryogenic jacket: #A8B6C2, cold pale blue-grey, on the jacketed parts only
- Charge: violet-white #C9B6FF ramping to #FFFFFF, in the charge frames only
- WARM, not cold. The attached sprites are brown-grey with copper and brass in
  them. A cold blue-grey monochrome building is wrong.

== RULES ==
- ADVANCED BUT STILL FACTORIO. Late tech tree: machined surfaces, sealed
  housings, flush covers, chamfered forms, indicator lamps, cryogenic jacketing,
  light used as a material, machinery implied rather than exposed.
- KEEP FACTORIO'S MECHANICAL DENSITY. Panel breaks, recessed vents, service
  hatches, grilles, bolt rings on covers, pipe and cable runs, greebles in the
  shadows, honest wear. Manufactured hardware, not a smooth prop.
- Not tier zero: NO field rivets everywhere, no rust sheets, no exposed gears
  or linkages. Fasteners exist but are neat and purposeful.
- Airless metallic world, gravity 50: massive, braced, immensely heavy.
- Nothing burns here. No flame, no exhaust, no steam, no smoke, no fire, anywhere.
- Nothing glows at rest. Violet appears only in the charge and discharge frames.
- Not generic science fiction: no neon strip lighting, no holograms, no decals.
- Must read as a machine holding a core, not as a planet, a ball on a stand,
  a water tower or a wrecking ball. The arms grip; they do not lift.

== PANELS ==
- A large hero view of the building
- A silhouette panel: the same building as a flat black shape on grey, to
  show it is readable with no detail at all
- A tile-grid panel from directly overhead on a 9x9 tile grid, the base
  inside the grid with no part crossing the edge sideways
- Three close-up detail panels: one arm's grip where it meets the sphere; the jacketed band round the
sphere's equator; a corner tower's service platform and ladder
- A row of five charge key frames labelled 0%, 25%, 50%, 75%, 100%, showing
  the recessed bands on the sphere filling with violet from the bottom of
the sphere upward, the whole shell lit and the gap beneath it glowing at 100%
- One large discharge panel: the moment it fires
- A palette strip of eight colour swatches

== OUTPUT ==
One landscape concept sheet, 3:2, labelled panels on a dark charcoal background,
in the style of a game art bible page. Panel labels only; no other text.
```
