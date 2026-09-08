# Option C — the Spinner

> ## ADOPTED — this is the Whisker Comber
>
> Chosen 2026-09-08 by Liam from five options drawn against each other. The sheet
> is locked at `graphics/entity/whisker-comber/concept/options/C-sheet.png`. Every other option in this directory is
> rejected and its page has been deleted; the README keeps the record of what the
> five were and what the round measured.

### Why it won

It is the only one of the five that stops being a box. The Comber's standing
problem, stated in its own spec, is that it is a low grey machine that sorts
things standing next to a low grey machine that sorts things -- and a squat
standing drum separates from the Dross Classifier at any zoom, in any direction,
with no detail at all.

The vertical axis is also the honest answer to gravity 50: spinning about the
vertical is the one axis where the Core's gravity is not fighting the bearings.

Of the four it beat, A is the better-measured sheet and the safer machine, but it
is the box again; B reads as a machine waiting rather than working; D reads as
the Drop Crusher's cousin; and E's two lanes did not come back unequal enough to
carry the idea that justified them.

### What to fix in production, found on review

1. **It must not become the Sealed Roboport.** That building is a smooth dome
   and it is already on the Core. This one stays squat, bolted and industrial:
   the ring of toggle dogs, the lifting eye, the balance bosses round the waist
   and the louvred drive skirt are the difference, and every one of them has to
   survive stage 1.
2. **It is the least detailed sheet of the fifteen, at 0.114**, against vanilla's
   0.144 floor. A round shell gives the eye less to hold, which is exactly why
   vanilla covers its round machines in hardware. More instrumentation, more
   panel breaks, more fittings on the skirt -- and let the copper out, which
   fixes the saturation at the same time.
3. **The two recipes are not drawn, and that is accepted.** The comb-versus-mat
   choice is the reason this building exists, and this design does not show it;
   option E was the one that did, and it was not picked. If the choice needs to
   be visible later, it belongs in a `working_visualisation` that only plays
   while the machine is crafting, not in a second permanent lane.
4. **The draw-off guide is the one part that can lie.** It stands over the lid
   with two polished rollers and nothing between them, which is correct. It must
   never be drawn with tow in it, and it must not be aimed at a tile.

**One line.** A squat vertical drum with a domed lid and a draw-off arch, aligning fibre by spinning it rather than combing it.

## The idea

Turn the machine on its end. A heavy vertical drum occupies most of the
footprint, capped with a domed lid on a ring of dogs; inside, a spinning head
throws the material against the wall and it comes off aligned. The tow is drawn
off through a small arched guide standing over the lid.

The read is centrifugal: everything about the shape says *this spins*, from the
ring of dogs to the balance bosses round the drum's waist.

## Why it suits this machine

It is the only round building in the set, and that is the point. The
Classifier's options are boxes and cylinders lying down; a standing drum is
immediately separable at any zoom.

A vertical axis is also the honest answer to gravity 50: spinning about the
vertical is the one axis where the Core's gravity does not fight the bearings, and
that is the sort of detail this mod's design notes like.

## What it risks

**It could read as a tank, a silo or a fermenter**, all of which are
vessels rather than machines. The balance bosses, the dogged lid and the drive
skirt at the base are the defence, and they must be prominent.

**A domed lid is a hatch**, and the Sealed Roboport already owns the dome-on-the-
Core silhouette. This one has to be squat and industrial where that one is
smooth.

## Concept Sheet Prompt

```text
FACTORIO SPACE AGE BUILDING -- CONCEPT SHEET

== CAMERA ==
Match the attached vanilla sprites exactly: looking steeply down from above,
MOSTLY ROOF with only a shallow near face visible. Square to the tile grid --
the near face parallel to the bottom edge of the frame, the side faces parallel
to the left and right edges. The square base must read as a SQUARE, never as a
diamond or a rhombus. Not rotated corner-on. Not a flat front elevation.
The attached vanilla sprites are STYLE references only: match the camera,
rendering, finish, LEVEL OF DETAIL and COLOUR TEMPERATURE; do NOT copy the
design, shape or components. The attached sheet of our own is a FORMAT reference
only: match its panel layout and information panels. The machine in it is a
different building of ours and this one must look like nothing else.

== BUILDING ==
Whisker Comber -- option C, the Spinner.
A three-by-three fibre-aligning machine built as a squat vertical drum with a
spinning head inside it.

== FORM ==
- A squat heavy DRUM standing on the 3x3 footprint, about as tall as it is wide,
  with a machined shell and a low skirt where it meets the ground
- A domed LID on top, held by a ring of toggle dogs, with a lifting eye at its
  crown -- squat and bolted, not smooth and seamless
- A ring of BALANCE BOSSES around the drum's waist, evenly spaced, each a small
  machined pad -- the detail that says this thing spins
- A guarded DRIVE SKIRT at the base with cooling louvres and a cable entry
- A small arched DRAW-OFF GUIDE standing over one edge of the lid, a pair of
  polished rollers in it, EMPTY
- One guarded infeed port low on the shell, shut

== COLOUR ==
- Chassis and hood: #4A463F to #6E685C, warm low-value iron-nickel, machined
- Working cylinders and combs: #8A8580, pale grey steel
- Needle glints: #D8D4CC, fine and sparing, on the needled surfaces only
- Pale nickel-white: #B9B4A8, on chamfers, guards and end caps
- Copper and brass: #8A5A32, on the drive end and bearing caps only
- WARM, not cold. The attached sprites are brown-grey with copper in them.

== RULES ==
- REGISTER: TIER 1-2, integration and precision plant. Machined casing, flush panels, guarded mechanisms, few visible fasteners on the primary faces, some cabling and instrumentation. Not tier zero: no field rivets everywhere, no rust sheets. Not tier four either: no seamless monolith, no light used as a material. The needled working parts inside are the only crude thing about it.
- Draw NO loose material anywhere: no ore, powder, grit, fibre, debris or
  product on the ground, in bins, at chutes, in trays, or spilling from the
  machine. Factorio machines never show what they make, so every chute, port,
  bin, tray and mouth is drawn as EMPTY machinery.
- The working chamber is enclosed. An open frame around an empty bed advertises
  that emptiness on every tick and the machine reads as idle while it runs.
- NO output port and no output chute aimed at a tile: this machine holds its
  products until an inserter takes them, and the inserter may stand on any
  adjacent tile. Vanilla's assembling machines draw no output port at all.
- Nothing extends sideways past the 3x3 footprint. Height above it is fine;
  width is not.
- No pipe flanges and no fluid connections: this machine has no fluid box. No
  visible electrical connector either -- power arrives from a pole off-frame.
- Airless metallic world, gravity 50: nothing burns and nothing blows about.
  No flame, no exhaust, no steam, no smoke, no fire, no dust cloud, anywhere.
- NOTHING GLOWS. This machine is mechanical throughout: no lit panels, no
  emissive anything, no field effects.
- The material this machine handles would cut you: it looks GUARDED. Hoods,
  interlocks, warning plates on the guards themselves -- but no hazard chevrons
  used as wallpaper.
- Not generic science fiction: no neon strip lighting, no holograms, no decals,
  no hazard chevrons used as decoration.
- FORBIDDEN READS: it must NOT read as a textile mill -- no wooden framing, no
  spindles, no bobbins, no spools, no thread, no cloth, nothing that belongs in
  a mill. And it must not read as a plain crate or a shipping container.
  It must not read as a storage tank, a silo, a fermenter or a boiler: the
  balance bosses, the dogged lid and the drive skirt are what make it a machine.
  It must not be a smooth seamless dome -- that is another of our buildings.

== PANELS ==
- A large hero view of the whole building
- A silhouette panel: the same building as a flat black shape on grey, to prove
  it is readable with no detail at all
- A top-down view from directly overhead, WITHOUT grid lines drawn on it
- Two close-up detail panels: the lid's toggle dogs and lifting eye; and the draw-off guide's rollers standing over the lid, empty
- A two-frame state pair: the machine stopped and running: the same view with the draw-off rollers turned between frames
- A palette strip of six colour swatches

== OUTPUT ==
One landscape concept sheet, 3:2, labelled panels on a dark charcoal background,
in the style of a game art bible page. Title the sheet WHISKER COMBER -- SPINNER -- use exactly
that name, do not invent a generic descriptive title. Panel labels only; no
other text anywhere on the sheet.
```

## Round 1 — what came back

`graphics/entity/whisker-comber/concept/options/C-sheet.png`, generated 2026-09-08 from the prompt above with the four attachments named
in the README.

**Measured:** luminance **66.5**, saturation **0.194**, edge density **0.114**.
Band from the four vanilla references: luminance 63.2-90.4, saturation 0.230-0.490, edge density 0.144-0.261. The *aspect* column `check-sheet-style.py` prints is meaningless on a whole sheet -- it measures the sheet's panel bounds, not the building -- so its "perspective low" verdict is ignored here, as `array-options/README.md` says it must be.

**What landed.** A squat standing drum with a dogged lid, balance bosses round
the waist, a louvred drive skirt and the draw-off guide over the lid. It is the
only round building in the set and separates instantly at any zoom.

**What to weigh.** Two problems. Its dome is close to the Sealed Roboport's, and
that building is already on the Core. And at 0.114 it is the least detailed sheet
of the fifteen -- a round shell gives the eye less to hold, which is exactly why
vanilla covers its round machines in hardware.
