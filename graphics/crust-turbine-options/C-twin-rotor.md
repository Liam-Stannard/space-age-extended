# Option C — the Twin Rotor

**One line.** Two rotor faces side by side down the body, counter-turning behind open grilles, so the motion is doubled and put where the camera looks.

**What moves:** two rotor faces, counter-turning — together roughly **2.6 tiles of a 5-tile
body, about 50 % of the box**, and set into the ROOF rather than a flank so the
top-down camera sees them square on.

## The idea

If the rotor is the only honest motion, use two of them and put them where they
can be seen.

A long low body carries **two open grilles set into its roof**, side by side down
the axis, with a dark rotor face turning behind each. They **counter-turn** — one
clockwise, one anticlockwise — so the machine is never symmetrical in motion and
never has a still frame.

The frosted let-down stage wraps the left end and a compact generator can sits
between the rotors and the right flange.

## Why it suits this machine

**It puts its motion on the roof**, which on Factorio's steeply-angled camera is
most of what a player sees. Option A's rotor is on a flank and half hidden; these
are presented square on.

**Counter-turning is legible and cheap.** It is one drawn face rotated about a
fixed centre, twice, in opposite directions — the motion `build-part-frames.py`
derives most cleanly from a flat plate — and it doubles the moving share for no
extra art.

**Two rotors also say "this is a stage machine"**, which is what an expansion
turbine is: gas drops pressure through more than one wheel.

## What it risks

**Two round faces side by side on a long body is a pair of fans**, and fans mean
cooling, and cooling means something hot nearby — the exact association this
building is trying to kill.

**Open grilles on a planet with no air are hard to justify.** A grille implies
airflow. It has to read as a guard over machinery, not a vent, and a generator
handed "grille" will draw louvres.

**And at 50 % it is still under vanilla's band**, so it pays the cost of an
animation without clearing the bar. If the round is going to move, option D moves
more.

## Concept Sheet Prompt

```text
FACTORIO SPACE AGE BUILDING -- CONCEPT SHEET

== CAMERA ==
Match the attached vanilla sprites exactly: looking steeply down from above,
MOSTLY ROOF with only a shallow near face visible. Square to the tile grid --
the near face parallel to the bottom edge of the frame, the side faces parallel
to the left and right edges. The footprint must read as a RECTANGLE square to the
grid, never as a diamond or a rhombus. Not rotated corner-on. Not a flat side
elevation. Draw it HORIZONTAL: the long axis running left to right.
The attached vanilla sprites are STYLE references only: match the camera,
rendering, finish, LEVEL OF DETAIL and COLOUR TEMPERATURE; do NOT copy the
design, shape or components.

== BUILDING ==
Crust Turbine -- option C, the Twin Rotor.
A TWO-BY-FIVE generator on an airless metal world. Gas comes up from the crust at
depth pressure, expands through the machine, and leaves at nothing: the power is
in the pressure difference. NOTHING BURNS. This is a COLD machine.

== FORM ==
- A LONG LOW BODY lying along the 2x5, riveted, flat
- TWO OPEN GRILLES SET INTO THE ROOF, side by side down the axis, each guarding a
  dark ROTOR FACE presented SQUARE ON to the camera. They are GUARDS over
  machinery, not air vents -- heavy bars, not fine louvres
- The two rotors COUNTER-TURN: one clockwise, one anticlockwise
- At the LEFT end a cast LET-DOWN STAGE wrapping the body, carrying a thick bloom
  of pale FROST
- Between the rotors and the right flange, a compact GENERATOR CAN with a brass
  TERMINAL BOX
- IDENTICAL bolted FLANGES closing both ends, square to the tile edges
- A small round white STATUS LENS on the near flank, between the two grilles
- Riveted seams, bolt lines, lifting lugs, honest wear

== COLOUR ==
- Body, grilles and can: #4A463F to #6E685C, dark warm iron-nickel
- Rotor faces: #2E2C29, dark, with bright machined edges up to #8A857C so the
  blades catch light as they turn
- Flanges and grille bars: #8A857C, brighter than the body
- Let-down frost: #BFD8E8 to #E8F2F8, pale blue-white rime, matte, never glowing
- Status lens: #FFFFFF, painted white
- Copper and brass: #8A5A32 to #C88A4A, VISIBLE and used freely on bus runs, the
  terminal box, flange faces and fittings. This is what keeps the building warm
  in colour on a machine that is cold in fact. Do not ration it.

== RULES ==
- REGISTER: TIER 0, the landing-day machines. Riveted plate, cast housings,
  bolted flanges, weld seams, honest wear. It is built from freight -- steel,
  pipe and gear wheels -- and should look like it came off a cargo pod. Nothing
  sealed, nothing chamfered, no composite shells, no jacketing.
- IT IS COLD AND NOTHING BURNS. No firebox, no burner, no flame, no exhaust
  stack, no chimney, no smoke, no heat stain, no lagging, no insulation blanket,
  no hot pipe. NO GLOW OF ANY KIND ANYWHERE -- not orange, not white, not blue.
  The only light on this building is the status lens.
- FROST IS THE SIGNATURE. Pale blue-white rime, #BFD8E8 to #E8F2F8, blooming
  where the pressure drops. It does NOT glow; it is a surface, not a light.
- EXACTLY TWO FLUID CONNECTIONS, one at each END of the long axis, and they are
  IDENTICAL. Gas passes straight through and these machines chain end to end, so
  the art must make chaining obvious. Each flange sits SQUARE to the end it is on
  and points STRAIGHT out of it, stopping flush at the middle of that tile edge.
  Axis-aligned, never diagonal, never out of a corner.
- THE FLUID CONNECTIONS THEMSELVES ARE BARE. Every flange, stub and port is
  plain machine metal: no frost, no rime, no ice, no heat glow, no scorch, no
  lagging, no colour treatment of any kind. Whatever the fluid does to the
  body of the building, it STOPS SHORT of the connection. The engine caps an
  unconnected port with its own neutral flange, and a treated stub would not
  match it.
- NO OTHER PORTS. No pipe on the flanks, no stub, no cap, no blank, no spare
  socket, no valve tree. Two connections and no more.
- A small round white STATUS LENS on the body. It is PAINTED WHITE in the hero
  view, the top-down view, the detail panels and the silhouette -- the engine
  colours it in game -- and drawn coloured ONLY inside the three-state row.
- Draw NO loose material and NO product: no arcs, no sparks, no crackle, no
  lightning, nothing at the terminal box, nothing on the ground.
- Nothing extends sideways past the 2x5 footprint except the two end flanges.
  No visible electrical connector -- power arrives from a pole off-frame.
- Airless metallic world: nothing blowing about, no dust, no vapour plume. Frost
  clings to the metal; it does not steam off it.
- Not generic science fiction: no neon strip lighting, no holograms, no decals,
  no hazard chevrons used as decoration.
- FORBIDDEN READS: it must NOT read as a STEAM TURBINE -- no lagged pipework, no
  insulation blankets, no boiler, no hot end, nothing that suggests heat. The
  player builds real steam turbines on this same planet and reversing the two is
  a mistake this design exists to prevent. Also not a pump, not a compressor
  station, and not a locomotive.

== PANELS ==
- A large hero view of the whole building
- A silhouette panel: the same building as a flat black shape on grey, to prove
  it is readable with no detail at all
- A top-down view from directly overhead, WITHOUT grid lines drawn on it
- Two close-up detail panels: one roof grille with its rotor face square on behind the bars; and the frosted let-down stage wrapping the left end
- An END-ON view showing one flange square to the tile edge, and a second panel showing TWO of these machines chained end to end
- A FOUR-FRAME MOTION ROW of the same view: both rotors at rest positions; a quarter turn, one each way; a half turn; three quarters -- the two never align, so there is no still frame
- A THREE-STATE ROW of the same view, three frames: RUNNING with the status lens
  glowing GREEN and the frost at its thickest; BLOCKED with the lens AMBER; IDLE
  with the lens dark and the frost thinnest. NOTHING on this building glows in
  any of the three
- A palette strip of eight colour swatches

== OUTPUT ==
One landscape concept sheet, 3:2, labelled panels on a dark charcoal background,
in the style of a game art bible page. Title the sheet CRUST TURBINE -- TWIN ROTOR -- use
exactly that name, do not invent a generic descriptive title. Panel labels only;
no other text anywhere on the sheet. No logos, wordmarks or watermarks anywhere.
```
