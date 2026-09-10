# Factorio Building — Art & Implementation Specification

**Crust Turbine.** First draft — a brief, enough to commission and judge a
concept sheet. Not a specification: §6, §12 and §13 stay open until a sheet is
approved and a canonical plate has been measured.

**This building had no spec of its own until 2026-09-10.** It lived inside
`building-spec-crust-tap.md` as "a companion generator", which was fine while it
was one line of Lua and became a problem the moment anyone had to draw it. The
tap's brief keeps the *pairing* argument — the two are commissioned together and
must read as a set — and everything about the turbine itself is here.

**The one sentence the whole design hangs on:** the tap sells **pressure, not
heat**. That is the Crust Tap's own line and it decides this machine completely.
Nothing here burns.

---

# 1. Building Overview

**Building Name:** `Crust Turbine`
**Internal Prototype Name:** `sae-crust-turbine`

**Building Type:** `generator`, derived from the steam turbine, with
`burns_fluid = true`.

**Purpose:** Turns crust gas into electricity. It is the second half of the
Core's landing-day power, and it is deliberately small.

**Why it matters:** it is the first generator a player builds on this planet, and
it sets the expectation that power here is *sited* — you go to where the vents
are. It should never look like a power strategy.

**Locale:** *"Pressure, let down."* / *"The crust vents at a pressure the surface
does not have. That difference is the whole machine."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 2 × 5 |
| Directions | 2 — horizontal and vertical, as a steam turbine |
| Output | **1.8 MW**, `max_power_output = "1800kW"`, `effectivity = 1` |
| Fluid | `sae-crust-gas`, filtered, `volume = 200`, `fluid_usage_per_tick = 0.15` (9/s) |
| Connections | **Two, one at each end of the long axis**, both `input-output` |
| Surface conditions | `pressure` ≤ 9 — the Core and platforms |

**`burns_fluid` ignores temperature entirely** and takes its power from the
fluid's `fuel_value`. Measured on the rig: a turbine burning gas at 25 °C with
`fuel_value = "200kJ"` produced exactly its declared 1.80 MW under load. That is
why the gas carries no temperature and the tap never declares one.

**`maximum_temperature` is mandatory even so.** Leaving it out fails the data
stage outright. It does no work in this mode; it still has to be declared.

**The pair is the unit.** Roughly one turbine per tap, about 1.8 MW for the two,
and a player who tiles fifty taps should still find the melt-and-steam line the
better answer by a wide margin — or the Core's central tension is undercut by its
own tutorial.

---

# 3. Visual Design

## 3.1 Design Concept

**A pressure let-down, not a boiler.** Gas at depth pressure expands through a
rotor and comes out at nothing; the energy is in the *difference*, not in any
heat. So this machine is **cold**. It has no firebox, no flame, no exhaust
stack, no heat stain and no warm light anywhere.

**Two anti-reads, and the second one is the sharp one.**

The first is vanilla's steam turbine, whose sprites this building currently
wears. Obvious, and easy to avoid.

The second is **vanilla's steam turbine as the player will actually meet it on
this planet** — because they build those here too, on the melt-and-steam line
(`04-the-core.md` §2). Two different turbines on one factory floor, one fed by a
pipe of crust gas and one by a pipe of 500 °C steam, and reversing them is a
mistake the player can make. **This machine must not look like a steam turbine at
all**, and the surest way is that it is visibly *cold*: frost where the other is
hot, no lagging, no insulation blankets, no heat.

## 3.2 Key Visual Features

* A **long low body** on the 2 × 5, lying along its axis — this is the flattest
  building in the set.
* A **let-down stage** at one end: a cast expansion housing, obviously where the
  pressure drops, with **frost** blooming on it. Cold is the signature.
* An **inline rotor casing** down the middle, smooth and pressure-rated.
* **Two flanges, one at each end**, identical, because gas passes straight
  through and turbines chain end to end.
* A **generator can** at the far end from the let-down stage, plainly electrical.

### Signature Feature

**Frost, on the machine that makes the power.** Every other warm thing on this
planet glows; this one goes cold when it works. It is the clearest possible
statement that no fire is involved, and it pairs it with the tap, whose riser is
frost-collared for the same reason.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Body and casing | `#4A463F` → `#6E685C` | the mass of the building |
| Let-down frost | `#BFD8E8` → `#E8F2F8` | the expansion housing only |
| Generator can | `#5A5047` | the electrical end |
| Flanges and fittings | `#8A857C` | both ends |
| Copper and brass | `#8A5A32` → `#C88A4A` | bus runs, terminal box, flange faces |

**No glow of any kind.** Not orange, not white, not blue. The only light on this
building is the status lens the engine tints.

---

# 4. Factorio Visual Style

**Tier 0 — Foothold.** Riveted plate, cast housings, bolted flanges, weld seams,
honest wear — the same register as the Drop Crusher and the Ballast Drill, and
priced in freight like them: 20 steel plate, 10 pipe, 20 iron gear wheels.

Style reference to attach: the **steam turbine**, with the standing disclaimer
that it is a reference for *finish and scale only* and that this machine's whole
job is to not be it.

---

# 5. Building Orientation

* [x] Horizontal
* [x] Vertical

**Direction count:** `2`. A `generator` draws `horizontal_animation` and
`vertical_animation`, not four frames — and both connections are on the long
axis, so a quarter turn is the only rotation that means anything.

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| Crust gas | **both ends of the long axis**, `[0, 2]` and `[0, −2]` | `input-output`, filtered to `sae-crust-gas` |
| Electric | no visible connector | poles reach it wirelessly |
| Items | none | no inserter ever touches this building |

**Both ends, and they are identical.** Gas passes straight through so turbines
chain end to end, exactly as steam turbines do — and the art must make that
obvious, because a player who cannot see that it chains will build them in a row
with a pipe between each pair and wonder why it looks wrong.

**Each flange sits square to the end it is on and points straight out of it**,
axis-aligned, stopping flush at the middle of that tile edge. The template's §8
rule applies in full: there is no diagonal hookup, and a connector angled across
a corner is one the player can never join cleanly.

---

# 9. Working Animation

**A rotor turning behind a grille, and frost that thickens.** The rotor is the
honest motion — it is what the machine physically does — and it can be a face
pointed at the camera, which is the one rotation this project's tooling derives
cleanly from a flat plate (`build-part-frames.py --mode spin`).

**Do not animate the frost as a cycle.** Frost forming and melting on a loop
reads as the machine stopping and starting. If frost changes at all it should
track *state*, not time.

---


# 11. Generation Requirements

## Master Concept Prompt

Stage 1. **Attach `graphics/entity/crust-turbine/concept/adopted/E-sheet.png` and
nothing else** — same machine as the sheet's hero view, not a new design.

**The frost comes off the collars.** The adopted sheet ran rime onto both end
flanges, and those flanges *are* the two fluid connections. Template convention 5.

**Measure the camera before cutting anything.** Every option in this round came
back nearer side-on than Factorio's projection; check the trimmed aspect against
a real 2×5 vanilla plate and regenerate with a vanilla sprite as camera reference
if it misses. `TODO.md`, *The defect to expect on every remaining building*.

```text
FACTORIO SPACE AGE BUILDING SPRITE -- MASTER PLATE

Redraw the machine in the ATTACHED SHEET's hero view as a single clean game
sprite. Same building, same design, same camera. Do not redesign it, do not
add or remove parts, and do not draw any panels, labels, text, borders or
background furniture.

== WHAT IT IS ==
The Crust Turbine: a 2x5 generator on an airless metal world, lying HORIZONTAL
with its long axis running left to right. Gas comes up from the crust at depth
pressure, expands through the machine, and leaves at nothing -- the power is in
the pressure difference and NOTHING BURNS. A long low body of plain riveted
plate, deliberately quiet. THREE HEAVY MACHINED COLLARS, all the same design: a
bright machined ring with a full circle of bolts round it. Two of them are the
end flanges; the third frames a window in the middle of the near flank with a
dark rotor face behind it. The let-down stage sits UNDER the left-hand collar
rather than beside it, with pale frost blooming from beneath it and running back
along the body. A compact generator can at the right, low, with a brass terminal
box and cleated cable runs. A small round white status lens on the middle
collar's rim.

== CAMERA ==
Looking steeply down from above, MOSTLY ROOF with only a shallow near face
visible, square to the tile grid: the near face parallel to the bottom edge of
the frame, the side faces parallel to the left and right edges. The footprint
reads as a RECTANGLE square to the grid, never a diamond or a rhombus. Not
rotated corner-on, not a side elevation. Match the attached sheet's hero view
exactly.

== HARD REQUIREMENTS ==
- ONE machine, centred, filling the frame, nothing else in the image
- FULLY TRANSPARENT BACKGROUND. No ground, no floor, no shadow on the ground,
  no grid, no vignette, no backdrop of any kind
- THE TWO END COLLARS ARE BARE MACHINED METAL. NO FROST, no rime, no ice, no
  pale blue, no lagging, no colour treatment of any kind on either end collar or
  the bolts round it. The frost STOPS SHORT of them. This is the one thing this
  render changes from the attached sheet, and it matters because those two
  collars are the machine's two fluid connections
- The frost lives UNDER THE LEFT-HAND COLLAR and on the BODY behind it, matte,
  never glowing -- a surface, not a light
- The two end collars are IDENTICAL and square to the tile edges, so a row of
  these machines reads as chaining end to end
- The STATUS LENS is PAINTED WHITE -- a plain white lens, not lit, not coloured,
  not glowing. The engine colours it in game
- IT IS COLD AND NOTHING BURNS. No firebox, no burner, no flame, no exhaust
  stack, no chimney, no smoke, no heat stain, no lagging, no insulation blanket.
  NO GLOW OF ANY KIND ANYWHERE
- NO OTHER PORTS. No pipe on the flanks, no stub, no cap, no blank, no spare
  socket, no valve tree. Two connections and no more
- No arcs, no sparks, no crackle, nothing at the terminal box, nothing on the
  ground
- Nothing extends sideways past the 2x5 footprint except the two end collars
- It must NOT read as a STEAM TURBINE: no lagged pipework, no insulation
  blankets, no boiler, no hot end
- No text, no labels, no logos, no wordmarks, no watermarks

== OUTPUT ==
One landscape image, the machine alone on transparency, sharp and clean at full
resolution, in the rendering and finish of the attached sheet.
```

# 12. Master plate — two attempts, both rejected on camera

`concept/master-v1.png` and `concept/master-v2.png`, 2026-09-10. Both are kept
because the *design* in them is right and only the camera is wrong; whoever picks
this up next should redraw the camera, not the machine.

**What is right in them.** Three matching machined collars, the two end ones
bare metal with the frost stopping short of them — convention 5, and the whole
reason E was adopted. A white status lens with a bezel on the middle collar. The
terminal box and cleated runs. Nothing hot, nothing glowing, transparent
background.

**What is wrong.** Both are drawn as a flat plan view from directly overhead:
there is no near face at all. Measured:

| | width × height | aspect |
| --- | --- | --- |
| master-v1 | 1383 × 450 | **1:0.33** |
| master-v2 | 1383 × 450 | **1:0.33** |
| a 2×5 ground square, alone, seen straight down | — | 1:0.40 |
| vanilla `steam-turbine-H`, the same 2×5 footprint | 320 × 245 | **1:0.77** |

A drawing shallower than its own footprint cannot be right: at 1:0.33 the machine
is drawn *longer relative to its depth than five tiles by two actually are*, so
there is no scaling that makes both axes land, and `--stretch-y` would need to be
about 2.3 — far past the 1.2 the tool's docstring calls the limit.

**The regenerate did not move it.** The second attempt asked in as many words for
a shallow near face and a deeper footprint, and came back byte-for-byte the same
composition. Two attempts is where this stops; the next one should carry the
vanilla steam turbine as a camera reference *and* say the near-face band is
mandatory, or the plate should be built by editing the approved image's geometry
rather than asking again.

**Nothing is wired.** The Crust Turbine still wears its placeholder sprites and
still appears in the data stage's placeholder report. That is deliberate: a plate
cut from either of these would tile wrong against every other building on the
planet.

---

# 20. Open questions

- **Does it need a rotor window at all?** A sealed machine with nothing visible
  moving is defensible for a pressure let-down, and it would make the building
  cheaper and quieter beside its tap. The options round should test it.
- **How hard should the pairing be pushed?** The tap is the Bolted Collar, and a
  turbine that echoes its collar detail would read as a set — at the cost of
  looking like one machine cut in half. Worth one option out of five.
