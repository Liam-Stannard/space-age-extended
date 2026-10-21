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
- Bulky hoses, clutter, asymmetry; vanilla-like, not machined.
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

## Light
- Radiant blue `#1F63FF` → `#73ADFF`, drawn in look B: light behind dark
  smoked glass with dark internals, a soft glow layer, no pale cyan top,
  nothing clipped; C's rising bubbles in glass columns only (Liam,
  2026-10-12). Helper: `tools/blender/radiant.py`.
- Molten kamacite may glow orange only where melt is seen.
- No frost or cold in a model; cold comes from effects (Liam, Vent Pump,
  2026-10-12).

## Process
- No `.md`, spec, TODO or design wording written without Liam's
  agreement (claude.md rule 8).
- Commit, merge and push are separate permissions; push only when told.
- No migrations before 1.0 (Liam).
- Sound: vanilla references plus scripted files only.
- Show every image: open it on the desktop and send it; absolute paths.
- Clean up /tmp scratch and stop Xvfb, Blender and Factorio after each job.
