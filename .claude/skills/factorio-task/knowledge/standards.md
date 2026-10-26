# Art and process standards Liam has set

Each line: the standard, Liam's words or the decision, and the date.

## Buildings
- A building, not a deck: footprint coverage ≥ 92 %, no flat base or
  plinth; Liam: "Not much ground should be visible on the area it covers
  as its a building" (2026-10-12). The outline is still broken at the
  corners by equipment (FFF #350; the Reaction Plant model, 85.8 %).
- Tall parts stay mostly inside the grid: Liam chose 5×5 for the Reaction
  Plant "so any tall parts can mostly remain inside the grid as per the
  FFF" (2026-10-11). Rise no more than vanilla's comparable building.
- Vanilla texturing: Liam, "the texturing also doesn't fit basegame
  factorio" then "everything is the same, add some colour" (2026-10-11):
  a paint or metal per unit, worn paint, rust only where it forms,
  vanilla warmth and saturation. Reference: the Reaction Plant model
  (`concept/reaction-plant/model/circulator.py`).
- Tonal p50 ~75–81 accepted as the mod's look; p95 into vanilla's range.
- Clutter and asymmetry; vanilla-like, not machined. Hoses sized to the
  building: bulky where they suit it, thin where a dense building would
  be buried; every hose and cable end visibly fastened (Liam, Reaction
  Plant, 2026-10-20/21: "when hoses connect to something they need to
  look like they're structurally connected"; "Depends on the building").
- Every pipe input and output leads to a device that uses it; inputs and
  outputs visible doing their job (Liam, Vent Pump, 2026-10-12).
- Connections lead to the vessel that uses them, sized to the connection
  (no sudden halving of a run), and the flow reads through the building in
  every direction (Liam, Reaction Plant, 2026-10-20).
- Pipe joins: no gap and no edge of either object showing; the pipe's end
  ring is the joint, as on vanilla's steam turbine (Liam, turbine,
  2026-10-11: "There is still a gap between the joints. That is a fail.").
- Animated parts a player notices at 1x; showpieces have impressive
  animation (Liam, 2026-10-11).
- One building, not units on the ground: the vessels belong to a casing,
  frame or house (Liam, Reaction Plant, 2026-10-21: "it would help if it
  looked more like a building than some tanks on the ground").
- Every connection enters through a fitting set into the building's
  wall, open, with vanilla's cover when unconnected (Liam, 2026-10-21:
  "Every building, it doesn't necessarily have to be casing but anything
  similar would work as well").
- Clipping is checked by eye as well as by `--collide`, with crops of
  every run's ends (Liam, 2026-10-21: "When the artist reviews can it
  check for clipping").

## Light
- Radiant blue `#1F63FF` → `#73ADFF`, drawn in look B: light behind dark
  smoked glass with dark internals, a soft glow layer, no pale cyan top,
  nothing clipped; C's rising bubbles in glass columns only (Liam,
  2026-10-12). Helper: `tools/blender/radiant.py`.
- Molten kamacite may glow orange only where melt is seen.
- No frost or cold in a model; cold comes from effects (Liam, Vent Pump,
  2026-10-12).
- The Core has a thin atmosphere (pressure > 0): fire and explosion
  flashes are allowed; smoke is decided per effect (Liam, turbine,
  2026-10-20).

## Process
- No `.md`, spec, TODO or design wording written without Liam's
  agreement (claude.md rule 8).
- Commit, merge and push are separate permissions; push only when told.
- No migrations before 1.0 (Liam).
- Sound: vanilla references plus scripted files only.
- Show every image: open it on the desktop and send it; absolute paths.
- Clean up /tmp scratch and stop Xvfb, Blender and Factorio after each job.
- Unknowns are asked as questions with options, never settled by a
  default (Liam, 2026-10-20: "If you don't know something don't make
  assumptions, ask questions so the task is unambiguous").
- Visual questions come with their images, sent to Liam's phone first
  (Liam, 2026-10-21).
