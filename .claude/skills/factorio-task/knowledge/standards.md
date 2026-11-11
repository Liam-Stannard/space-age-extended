# Art standards Liam has set

The one list of bars a building's art is held to, from the options
stage on. Each line: the standard, Liam's words or the decision and the
date, and how it is checked. Figures come from
`tools/blender/measure.py` (factorio-art-measure); "by eye" means Liam's
judgement on the sheets. No figure here signs anything off.

## Form
- **A building, not a deck:** built up in height, filling its
  footprint; no flat base or plinth. Liam: "Not much should be visible
  on the area it covers as its a building" (2026-10-12). Coverage of
  92 % (the 3×3 and 5×5 showpieces' figure) is the target: reported
  every round, and a lower figure goes to Liam rather than failing the
  round (Liam, 2026-11-11: "Target, not gate"); the Reaction Plant was
  signed off at 85.8 %. Checked: coverage.
- **Raised casing allowed:** where the connections need a wall to
  enter, the lowest part may be a casing at pipe height filling the
  footprint, which the pipes enter and the machinery stands on, as in
  vanilla's assembler, foundry and cryogenic plant (Liam, 2026-10-28).
  Checked: by eye.
- **One structure:** the vessels and machines belong to a casing, frame
  or house they are set into or carried by, never units standing on
  the ground (Liam, Reaction Plant, 2026-10-21: "it would help if it
  looked more like a building than some tanks on the ground"). Checked:
  by eye.
- **Outline:** broken at the corners by equipment (FFF #350). Checked:
  corners.
- **Rise:** tall parts stay mostly inside the grid (Liam, Reaction
  Plant, 2026-10-11: "so any tall parts can mostly remain inside the
  grid as per the FFF"); rise above the north edge no more than
  vanilla's comparable building (refinery 0.97, fusion reactor 0.66).
  Checked: rise.
- **Clutter and asymmetry;** vanilla-like, not machined. Checked: by
  eye.

## Pipes
- **Each connection does a job:** it leads to the vessel or device that
  uses it, and inputs and outputs are seen doing their job, so the flow
  reads through the building in every direction, as on vanilla's
  chemical plant and oil refinery (Liam, Vent Pump, 2026-10-12; Reaction
  Plant, 2026-10-20). Or, as on vanilla's foundry, a pipe-height casing
  takes the fittings in its edge and carries the flow unseen (Liam,
  induction foundry, 2026-11-09: "Vanilla's way"). Checked: by eye.
- **Shown runs are plumbing:** straight lengths, few bends, each held
  by a bracket, rack or the vessel it joins, never loose elbows across
  a deck (Liam, induction foundry, 2026-11-09: "Still don't look like
  realistic structures"). Checked: by eye.
- **Bore:** a run keeps its connection's size, with no sudden narrowing
  after the fitting; a narrowing only where a visible reducer shows
  why, at a valve, pump or vessel nozzle; thin pipes only for side
  lines (dosing, instruments) (Liam, Reaction Plant, 2026-10-20).
  Checked: by eye.
- **Wall fittings:** every connection enters through a fitting set
  into the building's wall or casing (a recessed boss with a sleeve and
  flanges, as on the Reaction Plant's casing, or similar), never a stub
  standing off the machine; the pipe picture shows it open, and
  vanilla's cover is drawn when nothing is connected (Liam, 2026-10-21:
  "Every building, it doesn't necessarily have to be casing but
  anything similar would work as well"). Checked: by eye, in game.
- **Wall height:** the wall a fitting is set into stands at least the
  pipe's full diameter there, or curves round it: no flange or pipe
  overhangs its top edge, and the pipe picture paints nothing over the
  building (Liam, induction foundry, 2026-11-09). Checked: by eye.
- **Pipe pictures** are the model's own, to assembler 3's outline, in
  the building's metal; pipe covers are vanilla's (Liam, 2026-10-02).
  Checked: by eye.
- **Joins:** a join fails only on a gap between pipe and building, or
  on clipping; parts of the building beside the pipe are fine (Liam,
  2026-10-15: "surely parts of the building can be beside the pipe as
  long as it doesn't clip?"). Checked: joins (no gap of 2 px or more
  in more than 2 of the pipe body's columns); clipping by eye.

## Hoses and cables
- **Sized to the building:** bulky where they suit it, thin where a
  dense building would be buried (Liam, Reaction Plant, 2026-10-21:
  "Depends on the building"). Checked: by eye.
- **Fastened:** every end visibly fastened (a gland, clamp, collar,
  flange or nozzle), as if structurally connected (Liam, 2026-10-20:
  "when hoses connect to something they need to look like they're
  structurally connected"). Checked: collide (ends recorded with
  `tools/blender/runs.py`), and by eye on a crops sheet of every end.
- **No clipping:** no cable, hose, pipe or effect passes through
  another part or into the ground, at 2x in every direction (Liam,
  2026-10-21: "When the artist reviews can it check for clipping").
  Checked: collide, 0 clashes not allowed; and by eye for everything
  runs.py does not record and every contact listed as meant.

## Finish
- **Vanilla texturing:** a paint or metal per unit, worn paint, rust
  only where it forms, vanilla warmth and saturation (Liam,
  2026-10-11: "the texturing also doesn't fit basegame factorio", then
  "everything is the same, add some colour"). The reference is the
  latest signed-off model. Checked: finish, and by eye beside the
  reference.
- **No white:** pack.py rolls highlights off every drawn sheet but
  light passes, so no pixel reaches 245. Checked: white and clipped,
  0 px.
- **No frost or cold in a model;** cold comes from effects (Liam, Vent
  Pump, 2026-10-12). Checked: by eye.

## Light
- **Radiant:** blue `#1F63FF` → `#73ADFF`, drawn in look B: light
  behind dark smoked glass with dark internals, a soft glow layer, no
  pale cyan top, nothing clipped; C's rising bubbles in glass columns
  only (Liam, 2026-10-12), wherever the isotope is seen. Helper:
  `tools/blender/radiant.py`. Checked: glow, blue share.
- **Molten kamacite** may glow orange only where melt is seen. Checked:
  glow.
- **Other glows** when the glow shows the building's work (an energised
  coil, an arc, a lit window), as vanilla's foundry, electromagnetic
  plant and fusion reactor do: each named in the spec with its colour
  and when it shows, only while working (Liam, induction foundry,
  2026-11-09: "other parts of buildings should be able to glow").
  Checked: glow, against the spec's list.
- **Thin atmosphere:** the Core's pressure is above 0, so fire and
  explosion flashes are allowed; smoke is decided per effect (Liam,
  turbine, 2026-10-20). Checked: by eye.

## Motion
- **Seen at 1x:** a player notices the motion at 1x, every moving part
  has a job, there is an idle state, and nothing strobes at 1x;
  showpieces have impressive animation (Liam, 2026-10-11). Checked:
  motion, strobe.
- **Planned as steps:** a loop is planned as steps before it is
  modelled: each step's frames, the parts that move, their ease, and
  the sound it lands on. Every moving part holds still for part of the
  loop; the steps add up to the loop, and the loop to the recipe's
  ticks. Holds are played with a `frame_sequence`, not rendered again
  (Liam, Drop Crusher re-animation, 2026-11-08). Checked: by eye
  against the spec's step table.
- **Turning:** a building that turns keeps its signature parts facing
  the camera in every direction, with a per-direction variation where
  turning would hide them, as vanilla's chemical plant does. Checked:
  by eye, every direction.
