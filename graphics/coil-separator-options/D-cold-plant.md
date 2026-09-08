# Option D — the Cold Plant

> ## ADOPTED — this is the Coil Separator
>
> Chosen 2026-09-08 by Liam from five options drawn against each other. The sheet
> is locked at `graphics/entity/coil-separator/concept/options/D-sheet.png`. Every other option in this directory is
> rejected and its page has been deleted; the README keeps the record of what the
> five were and what the round measured.

### Why it won

It draws the argument instead of the object. Every other option draws a magnet;
this one draws the refrigeration a magnet needs on a world with no field to
borrow -- which is the only design in the five that explains the 2.5 MW on the
tooltip, and the reason the building exists at all.

It also lands the tier hardest. Cryogenic jacketing is tier 3's own vocabulary
and here it is structural rather than decorative, and at luminance 70.2 it is one
of the brightest, most readable sheets in the round.

The risk was that it would not read as a separator, and the sheet answers that
better than expected: the unlit/lit pair shows the base slot carrying the whole
read with very little light, which is the discipline the containment rule wanted
everywhere.

### What to fix in production, found on review

1. **It reads as a plant before it reads as a separator**, exactly as the
   option page predicted. The defence is the slot: it must be unmistakable at
   normal zoom, brighter and wider than in the concept, and it must be the first
   thing the eye finds. If stage 1 comes back with the slot subordinate to the
   vessel, that is a failed round.
2. **It is the least saturated sheet of the fifteen, at 0.136**, because the
   design has almost no copper in it by construction. The copper has to come back
   somewhere honest: the trunking's flanged joints, the terminal blocks, the
   condenser frame's fittings. This one needs it more than the other two.
3. **Vanilla's cryogenic plant is a real building the player will own**, and it
   is on Aquilo, not here -- but a screenshot of the two side by side is the only
   way to know this is not a copy of it. Do that before locking stage 1.
4. **The spec is now wrong in three places** and has been rewritten: §3.1
   described "a machine built around a hole", §3.2 made the coil throat the
   signature feature, and §16 asked for an icon of a toroid seen square-on. None
   of that survives -- the coil is buried and the icon is a vessel, a condenser
   stack and one lit slot.

**One line.** Nine tenths cooling plant and one tenth magnet: a jacketed vessel and a condenser stack, with the field visible only as a slot glowing at the base.

## The idea

Take the spec at its word -- *the field is expensive here* -- and draw the
cost instead of the field. The building is a cryogenic plant: a fat jacketed
vessel standing off-centre, a finned condenser stack beside it, frost collars,
relief valves, heavy insulated trunking looping between them. The coil is buried
inside the vessel and the player never sees it. All that shows of the actual
separation is a narrow horizontal slot at the base of the vessel with cold light
standing in it.

The joke is the proportion: a machine this big, to make a field that small.

## Why it suits this machine

It is the only option that explains the 2.5 MW on the tooltip. Every other
design draws a magnet; this one draws the refrigeration a magnet needs on a world
with no field to borrow, which is the argument the building exists to make.

It also lands the tier hardest. Cryogenic jacketing is tier 3's own vocabulary,
and this is the one design where it is structural rather than decorative.

## What it risks

**It may not read as a separator at all.** A vessel and a condenser stack
could be a chemical plant, a cryogenic plant or a storage tank, and the only thing
saying otherwise is one lit slot. That is the honest risk, and it is why the slot
is drawn large enough to be seen at normal zoom.

**Vanilla already has a cryogenic plant**, and this must not read as ours of it.
The prompt names that.

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
Coil Separator -- option D, the Cold Plant.
A heavy dark three-by-three magnetic separator drawn as the refrigeration plant a
magnet needs, with the magnet itself buried out of sight.

== FORM ==
- A sealed chassis filling the 3x3 footprint, carrying two masses of unequal size
- A fat cylindrical JACKETED VESSEL standing off-centre, pale cryogenic
  jacketing over a dark shell, banded with frost collars and capped with a
  domed head
- Beside it, a CONDENSER STACK: a close-packed bank of fins in a heavy frame,
  about two thirds the vessel's height
- Insulated trunking looping between vessel and stack, thick, lagged, with
  flanged joints -- all of it staying inside the footprint
- Relief valves and instrument heads on the vessel's crown
- At the base of the vessel, a narrow horizontal SLOT, the machine's only
  opening, wide enough to read at a glance, with the field standing in it
- No visible coil anywhere: the magnet is inside the vessel

== COLOUR ==
- Chassis: #4A463F to #6E685C, warm low-value iron-nickel, machined and sealed
- Coil windings: #8A5A32 to #C88A4A, copper and brass -- the only warm bright
  material on the building, and confined to the coil itself
- Bus bars and conductors: #8A8580, pale grey, flat and visibly overbuilt
- Pale nickel-white: #B9B4A8, on chamfers, covers and end caps
- Field: #6A5AC8 to #B0A8F0, cold blue-violet, INSIDE THE APERTURE ONLY
- WARM metal with a COLD light in it. The chassis must not drift blue.

== RULES ==
- REGISTER: TIER 3, the Core's own goods -- advanced, quiet, sealed. Seamless welded shells, chamfered forms, no visible fasteners on the primary faces, cryogenic jacketing where it is earned, light used as a material. No rivets, no rust, no exposed gears or linkages. But it is HEAVY and visibly strained: this machine makes a magnetic field on a world that has none, and it should look expensive to run.
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
- THE GLOW IS CONTAINED. A steady cold blue-violet appears ONLY inside the
  aperture named below, and never anywhere else: not on the chassis, not as a
  rim light, not leaking round an edge, not as a haze in the air. It is steady,
  not flickering: this is a field, not electricity arcing.
- No arcs, no lightning, no sparks, no electrical discharge of any kind.
- Not generic science fiction: no neon strip lighting, no holograms, no decals,
  no hazard chevrons used as decoration.
- FORBIDDEN READS: it must NOT read as vanilla's electromagnetic plant -- no white
  or pale laboratory panelling, no clean bright shell, no violet field effect
  playing over the outside of the building. Vanilla's plant is the machine this
  one exists to replace, and it must look like a heavier, darker, older answer.
  It must not read as a turbine intake, a fan, a rocket engine bell or a
  loudspeaker.
  It must not read as vanilla's cryogenic plant, a chemical plant or a storage
  tank: the slot at the base, the condenser stack's mass and the absence of any
  pipe connection to the outside world are what separate it.

== PANELS ==
- A large hero view of the whole building
- A silhouette panel: the same building as a flat black shape on grey, to prove
  it is readable with no detail at all
- A top-down view from directly overhead, WITHOUT grid lines drawn on it
- Two close-up detail panels: the vessel's frost collars and jacket seam; and the condenser stack's fin bank in its frame
- A two-frame state pair: the machine unlit and lit: the base slot dark, then with steady cold light standing in it and no light anywhere else
- A palette strip of six colour swatches

== OUTPUT ==
One landscape concept sheet, 3:2, labelled panels on a dark charcoal background,
in the style of a game art bible page. Title the sheet COIL SEPARATOR -- COLD PLANT -- use exactly
that name, do not invent a generic descriptive title. Panel labels only; no
other text anywhere on the sheet.
```

## Round 1 — what came back

`graphics/entity/coil-separator/concept/options/D-sheet.png`, generated 2026-09-08 from the prompt above with the four attachments named
in the README.

**Measured:** luminance **70.2**, saturation **0.136**, edge density **0.129**.
Band from the four vanilla references: luminance 63.2-90.4, saturation 0.230-0.490, edge density 0.144-0.261. The *aspect* column `check-sheet-style.py` prints is meaningless on a whole sheet -- it measures the sheet's panel bounds, not the building -- so its "perspective low" verdict is ignored here, as `array-options/README.md` says it must be.

**What landed.** Exactly what the option asked for: a jacketed vessel, a
condenser stack, lagged trunking, and one narrow lit slot at the base doing all
the work. The unlit/lit pair proves the read survives with that little light.

**What to weigh.** The predicted risk arrived -- it reads as a chemical or
cryogenic plant first and a separator second, and at 0.136 it is the least
saturated sheet of the fifteen, because the design has almost no copper in it by
construction. If this one is picked, the copper has to come back somewhere.
