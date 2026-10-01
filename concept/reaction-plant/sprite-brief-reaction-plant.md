# FACTORIO / SPACE AGE BUILDING SPRITE — MASTER TEMPLATE

Use this template whenever designing or rendering a new Factorio building.

Replace all text inside [SQUARE BRACKETS] with the requirements for the new machine. Delete sections that are not required.

---

# 1. BUILDING

**NAME:** Reaction plant (`sae-reaction-plant`)

**TYPE / PURPOSE:**
A shielded batch reactor. Two fluids go in — radiant solution and crust gas — and the gas strips the isotope out of the solution and drops it as a solid radiant fuel cell. It is the Core's entire power supply: every cell the radiant generators burn is made here.

**FOOTPRINT:**
3 × 3 tiles.

**INTENDED TIER:**
Early game — tier 0, the foothold tier. Among the first four or five machines built on the planet, made on site out of plate.

**ENVIRONMENT / FAMILY:**
Custom planet — the Core, surface only (pressure 1–9). An airless world: no flame, no exhaust, no smoke, no steam. Family: the Core's warm iron-nickel (kamacite) plate and copper machines. It must separate at a glance from its nearest sibling, the Helium Concentrator (tall, sealed, frost-and-orange), and from the vanilla chemical plant it is derived from.

The machine must look like a genuine **Factorio / Space Age entity sprite**, not concept art, a side-view illustration, an isometric render, or a generic sci-fi machine.

The design should communicate its purpose mechanically. Large components should have a reason to exist. Prefer visible machinery, fabricated plate, cast housings, flanges, motors, gearboxes, brackets, clamps, cable fittings, inspection covers and maintenance hardware over arbitrary decorative detail.

---

# 2. TILE SCALE — HARD REQUIREMENT

Use Factorio's tile grid as the dimensional reference.

At normal game scale:

**1 tile = 32 × 32 displayed pixels.**

For high-resolution source artwork use:

**1 tile = 64 × 64 source pixels at scale 0.5.**

Therefore the MACHINE'S GROUND FOOTPRINT should correspond to:

* 1×1 = 64×64 px
* 2×2 = 128×128 px
* 3×3 = 192×192 px
* 4×4 = 256×256 px
* 5×5 = 320×320 px
* 6×6 = 384×384 px
* 7×7 = 448×448 px
* 8×8 = 512×512 px
* 9×9 = 576×576 px

These measurements refer to the **tile footprint at ground level**, NOT necessarily the total image canvas.

Tall machinery, overhanging components, pipes and shadows may extend beyond the footprint.

Do not simply scale the entire visible sprite to the footprint dimensions.

---

# 3. CAMERA — HARD REQUIREMENT

Use the Factorio building camera.

The camera looks **steeply down from above**, showing mostly roof/top surfaces while retaining a shallow amount of the near-facing vertical wall.

The building must be:

* square to the Factorio tile grid
* NOT rotated corner-on
* NOT isometric
* NOT drawn as a diamond
* NOT perspective-skewed toward a vanishing point
* NOT a flat overhead plan view
* NOT a side elevation

For a square building:

The ground footprint must visually read as a **square aligned with the frame**.

For a rectangular building:

The footprint must read as the correct rectangular tile ratio.

The near edge runs horizontally from left to right.

The left and right sides remain aligned with the frame.

Approximately:

**80% roof/top surfaces
20% shallow near-facing wall**

Adjust this slightly for tall or unusually low machinery while retaining the same Factorio camera.

Use an orthographic / game-sprite appearance rather than photographic perspective.

---

# 4. SPRITE ANCHOR

Define a fixed entity origin before rendering.

**ENTITY CENTRE:**
Centre of the tile footprint at ground level.

All states, directions and animation frames must use EXACTLY the same:

* canvas dimensions
* entity centre
* ground position
* camera
* scale
* rotation
* lighting direction
* silhouette position

Do not automatically centre the visible pixels if doing so moves the entity's ground anchor.

Tall structures may naturally occupy more space above the footprint than below it.

---

# 5. LIGHTING

Use Factorio-style directional lighting.

**Primary light:** upper-left.

Therefore:

* upper-left surfaces are generally brighter
* right/lower-facing recesses are darker
* contact occlusion is strongest beneath overhangs
* metal edges catch restrained highlights
* recesses remain readable without becoming black holes

Lighting must remain identical between all variants unless the light itself is the feature being animated.

Avoid cinematic rim lighting, studio photography, dramatic coloured environmental light or bloom covering mechanical detail.

---

# 6. MATERIAL LANGUAGE

Primary materials:

Riveted and bolted warm iron-nickel plate — the drum shell and the skirt, `#4A463F` → `#6E685C`
Lead sheet — the three shield bands and their lugs, duller and cooler than the shell, `#5A5A60` → `#7A7A80`; with dark cast iron `#3B3B40` for the motor block, the collars and the crown bearing housing
Copper and brass, used freely — the cable trunk, the port collars, the gutter joints, fittings and lugs, `#8A5A32` → `#C88A4A`

Accent colour:

Works teal `#2A7F7A` — a dark, matte, chipped paint. On the ROOF ONLY, on exactly two surfaces: the agitator drive guard and the inspection-hatch cover. Each is a solid painted area, never a line or an outline. It never glows and takes no bloom or rim light.

Functional/emissive colour:

Radiant green-white `#A8E8C0` → `#E8FFF0` — in the three sight slots ONLY. Plus one status-lamp lens on the roof, which the engine tints; it is drawn as a neutral lens.

Use believable Factorio industrial construction:

* fabricated steel plate
* cast iron / cast steel
* bolted flanges
* weld seams
* rivets or structural bolts where appropriate
* access covers
* hinges
* cable clips
* brackets
* bearings
* collars
* pipe unions
* mechanical guards
* motors and gearboxes
* inspection ports
* lifting points

Detail density should resemble official Factorio entities.

Avoid making every surface equally busy.

Large forms must remain clearly readable at gameplay zoom.

---

# 7. WEAR AND SURFACE FINISH

The machine should look USED rather than factory-new.

Use restrained:

* chipped paint
* exposed metal edges
* scratches
* grease around moving joints
* heat discolouration around hot components
* oxidation/rust where appropriate
* soot only where mechanically justified
* accumulated dirt in seams and recesses
* frost only around genuinely cryogenic components

Wear should reinforce the geometry rather than obscure it.

Do not cover the entire sprite in random noise.

---

# 8. PRIMARY FORM

The machine consists of:

A squat PRECIPITATION DRUM — a riveted cylinder plainly WIDER THAN IT IS TALL (about 2 : 1), centred on the footprint, about 2.2 tiles (≈ 141 source px) in diameter. It is the mass of the building and the thing the player reads at one tile: a low dark banded disc inside a square frame.

A square base around it: a continuous bolted SERVICE GUTTER running right round the very edge of the 3 × 3 footprint — a shallow channel of riveted plate, bare metal and copper, IDENTICAL on all four sides — and, rising off it, a low SKIRT of riveted plate with worn hazard tape on all four of its corners, the same on each. No side of the base is a front.

Three heavy LEAD SHIELD BANDS strapped round the drum, each a distinct band standing proud of the shell with plain riveted shell visible between them, each bolted through raised lugs. They must not flatten into stacked rings.

On the crown, an exposed AGITATOR DRIVE: a cast motor block under a teal-painted guard, an open gear train, and between them a free-turning six-armed SPIDER COUPLING sitting in a recessed bay over the crown bearing. The coupling is drawn FREE — a clear visible gap all the way round it, nothing bridging it to the motor, the gear or the bearing: no spoke, hose, bracket or cable crosses that gap. The bearing plate and drum roof beneath it are drawn complete. To one side of the roof, service furniture that need not be symmetric: a teal inspection-hatch cover, a gauge cluster, ladder cleats, and a copper cable trunk that runs across the roof and down the drum to the SKIRT — and stops there, never reaching the gutter or the footprint edge.

On the near face: three narrow horizontal SIGHT SLOTS low on the drum's near shoulder, each in a bolted steel housing. They are the only light on the machine. Below them the skirt and the gutter, as on every other side.

Twelve identical FLUID PORT MOUTHS, three to each side of the gutter, one on the centre-line of every edge tile — see §9. They are the only pipe-like shapes on the machine. Nothing else connects: no power connector, no chute, no hatch for items.

One STATUS LAMP lens on the roof in a metal bezel (engine-tinted). The three sight slots (dark when idle, radiant green-white when working). No other lamps, no windows.

Maintain this design exactly between all alternate sprite states.

---

# 9. INPUT / OUTPUT PIPE OPTION

**FLUID CONNECTIONS:** YES

If NO:

Do not add arbitrary pipes, sockets, hose connections or pipe-looking decoration.

If YES:

Number of fluid connections:

3 in the prototype — 2 inputs and 1 output. They ROTATE with the entity while the building itself does not turn, so over the four directions every one of the twelve edge-tile positions is used. The plate therefore carries TWELVE identical port mouths, three per side, and the engine activates three of them at a time.

Connection 1:

* Type: INPUT
* Edge: NORTH (as placed facing north; turns with the entity)
* Tile position: [-1, -1.5] — prototype `position {-1, -1}`, `direction north`, volume 1000
* Fluid appearance: none. Nothing on or near the port may name a fluid — which fluid a box takes follows the recipe's ingredient order and swaps between recipes
* Pipe material: cast iron neck with a bolted copper/brass collar, bare metal, no paint

Connection 2:

* Type: INPUT
* Edge: NORTH (turns with the entity)
* Tile position: [+1, -1.5] — prototype `position {1, -1}`, `direction north`, volume 1000
* Fluid appearance: none
* Pipe material: as connection 1

Connection 3:

* Type: OUTPUT — dormant under the only current recipe, whose product is solid; live with no recipe set and under the future stage-3 fluid recipe
* Edge: SOUTH (turns with the entity)
* Tile position: [0, +1.5] — prototype `position {0, 1}`, `direction south`, volume 1000
* Fluid appearance: none
* Pipe material: as connection 1

All twelve mouths — [-1, 0, +1] along each of the four edges — are drawn identically: same size, same collar, same bore, same wear. No mouth is marked as an input, an output, or as belonging to a fluid. Where two mouths meet at a corner tile, their necks share one plain cast corner block, the same at all four corners. The engine stamps its own fitting (vanilla's assembler-2 pipe picture, 52 × 20 source px — about 0.8 × 0.3 tiles) and its grey covers over whichever mouths are live, so each painted neck stays inside that 0.8 × 0.3-tile rectangle and the drum and skirt stand back from it: a north stub is drawn BEHIND the machine and must still read.

### FACTORIO PIPE CONNECTION DESIGN

Fluid connections should resemble the readable connection language of vanilla Factorio machines.

Each connection must have:

* a **large open pipe mouth**
* a short projecting neck
* a substantial raised metal/flanged rim
* a clearly visible DARK RECESSED BORE
* enough diameter to remain readable at gameplay scale
* a mechanically believable attachment to the building

The opening must NOT look like:

* a blanked-off circular plate
* a tiny socket
* a button
* a painted circle
* a flat cap

Because of the steep Factorio camera, horizontal circular pipe mouths should appear as appropriately **foreshortened ellipses**.

Connection mouths should be large enough to read immediately as fluid connections.

For a 3-tile-wide machine, a major fluid socket may be roughly **0.7–0.9 tile in external diameter** where the design permits.

Default target:

**approximately 0.8 tile external diameter.**

At 2× source scale this corresponds to approximately:

**51 px external diameter per 0.8 tile.**

The dark bore is smaller inside the metal flange.

Do not allow decorative plumbing to obscure the actual connectable mouth.

---

# 10. CONNECTION ALIGNMENT

Pipe mouths should align deliberately with the Factorio tile grid.

Specify the connection's tile coordinate rather than placing it visually by eye.

Example for a 3×3 footprint:

North edge:
[-1, -1.5] [0, -1.5] [1, -1.5]

South edge:
[-1, +1.5] [0, +1.5] [1, +1.5]

West edge:
[-1.5, -1] [-1.5, 0] [-1.5, +1]

East edge:
[+1.5, -1] [+1.5, 0] [+1.5, +1]

Adjust actual prototype coordinates to match the entity definition.

Visually, the pipe should terminate exactly where the game connection is expected.

---

# 11. OPTIONAL ITEM INPUT / OUTPUT

**ITEM CONNECTION REQUIRED:** NO

If YES:

Required readable interface:

None. The fuel cell is held in the machine's output inventory until an inserter takes it from any adjacent tile. Draw no chute, tray, bin, hatch or belt mouth, and no product anywhere — no cells, powder, grit or debris on, in or beside the machine.

Location:

None.

The visual opening should suggest the machine's function but should not interfere with belt placement unless intentionally designed to do so.

Do not add an output chute solely because the machine produces an item. Factorio machines frequently output through game logic without a literal chute.

---

# 12. UNLIT STATE

Produce an **UNLIT / IDLE sprite**.

This is the master mechanical sprite.

All structural geometry is fully rendered.

Powered/emissive features are dark:

* lamps off
* windows dark
* glowing slots dark
* coils unpowered
* heated seams dark
* plasma/electrical effects absent

However, the physical objects that contain those lights remain visible.

Example:

A status lamp still has its glass lens and metal bezel, but the lens is dark.

A furnace window still exists, but there is no orange glow inside.

---

# 13. LIT STATE

Produce a corresponding **LIT / ACTIVE sprite**.

CRITICAL:

The lit sprite must be **pixel-aligned with the unlit sprite**.

Do NOT regenerate or reinterpret the whole building independently.

Between UNLIT and LIT states, preserve exactly:

* silhouette
* component positions
* pipes
* bolts
* scratches
* dents
* grime
* rust
* shadows
* highlights
* camera
* framing
* scale
* texture
* geometry

ONLY the defined powered elements change.

Lit elements:

The three sight slots low on the drum's near shoulder, lit from inside at a constant brightness, with a short soft bloom on the shell immediately around each slot. Nothing else: not the teal paint, not the copper, not the drive head, not the status lamp (the engine tints that), not any port mouth, and nothing on or within half a tile of any footprint edge.

Colours:

Radiant green-white `#A8E8C0` → `#E8FFF0`. No orange, no pale blue, no teal light.

Glow should originate from a physical source.

Keep the source bright but maintain visible structure around it.

Avoid excessive bloom.

The difference between lit and unlit frames should ideally be isolatable by image subtraction.

---

# 14. OPTIONAL EMISSIVE / LIGHT MASK

If useful, also produce a separate transparent emissive layer.

Transparent everywhere except:

* illuminated windows
* lamp lenses
* electrical arcs
* plasma
* glowing seams
* status indicators
* other genuine light sources

Do not include ordinary reflected illumination in the core emissive mask unless requested.

This allows the powered state to be composited over the static machine.

---

# 15. OPTIONAL WORKING ANIMATION

**ANIMATED:** YES

If YES:

Frame count:

12

Animated components:

The spider coupling on the crown, and nothing else. It rotates about its own vertical shaft. It has six-fold symmetry, so 60° is the whole loop: twelve frames at 5° per frame, 0° to 55°, and frame 11 leads back into frame 0. (This supersedes the 360° / frame-count rule below for this part; a full turn would be the same twelve frames six times.)

Static components:

Everything else: the gutter, all twelve port mouths, the skirt, the drum, the three shield bands and their lugs, the sight slots and their housings, the motor block and its teal guard, the fixed gear of the gear train, the crown bearing plate and the recessed bay under the coupling, the inspection-hatch cover, the cable trunk, the gauge cluster, the ladder cleats, the status lamp, every bolt, rivet, scratch and stain, and the shadow.

All frames must share exactly the same:

* canvas
* anchor
* footprint
* building position
* camera
* scale
* shadows unless motion genuinely changes them
* static pixel content

Do not allow frame-to-frame drift.

Do not slightly regenerate the whole building for every frame.

Animate ONLY the component that is actually moving.

Frame 0 is the start of the loop.

The final frame must lead naturally back to frame 0.

Do NOT duplicate frame 0 as the final frame unless specifically required by the animation system.

For rotation:

Frame angle = 360° / frame count.

For reciprocating machinery:

Define exact top and bottom stroke positions before rendering intermediate frames.

---

# 16. OPTIONAL DIRECTIONAL VARIANTS

**DIRECTIONS REQUIRED:** 1

For four-direction machines:

Produce:

NORTH
EAST
SOUTH
WEST

Unless the whole entity genuinely rotates, preserve the main machine design and move only the directional connection/component that logically changes.

Do not accidentally turn a four-direction sprite request into four different camera angles.

The Factorio camera stays fixed.

---

# 17. OPTIONAL SHADOW LAYER

Where required, provide a separate shadow sprite.

The shadow must correspond exactly to the machine geometry.

Lighting direction remains fixed.

Use transparent background.

Shadow should not contain opaque pieces of the machine.

Avoid giant soft photographic shadows.

Use the restrained readable shadow language of Factorio.

---

# 18. TRANSPARENCY

Final game sprite:

**fully transparent background.**

Do not include:

* floor
* terrain
* tile texture
* vignette
* backdrop
* gradient
* horizon
* atmospheric fog
* decorative border

Unless specifically requested for a concept sheet.

Do not accidentally bake a rectangular semi-transparent haze into the canvas.

Preserve clean alpha around the silhouette.

---

# 19. CONTACT WITH THE GROUND

Even on a transparent background the machine must convincingly sit on the ground plane.

Use:

* contact darkening
* underside shadows where appropriate
* feet / base plates
* grounded structural weight

Do not make the object appear to float.

But do not paint permanent terrain underneath it.

---

# 20. GAMEPLAY READABILITY TEST

The sprite must work at three viewing scales.

### FULL SIZE

Mechanical details are readable.

### NORMAL GAMEPLAY ZOOM

Primary machine function and silhouette remain clear.

### SMALL / ZOOMED OUT

The machine still has a distinctive:

* silhouette
* dominant colour grouping
* major mechanical feature
* orientation

Tiny decorative features should not be required to understand the sprite.

---

# 21. COLOUR AND CONTRAST

Prioritise local mechanical readability.

Adjacent components should be distinguishable through:

* material change
* value change
* edge definition
* recess shadow
* restrained colour difference

Do not use outlines around the entire object.

Do not use modern cel-shading.

Avoid pure white except for very small bright lamps/highlights.

Avoid pure black except for extremely deep recesses.

---

# 22. ICON

If an inventory icon is required:

Create a dedicated **64×64 source icon** intended for display at scale 0.5 where appropriate.

Do not merely shrink the full building sprite without checking readability.

Crop around the most distinctive portion of the machine.

Simplify insignificant fine detail.

Maintain the same:

* materials
* colour palette
* silhouette language
* lighting direction

Transparent background.

---

# 23. OPTIONAL MASKS

When requested provide separate masks for:

MOVING PART — the spider coupling, and the recessed bay it turns in

EMISSIVE PART — the three sight slots and their bloom

TEAM/TINT COLOUR — the status-lamp lens only (the engine tints it by machine status)

PIPE CONNECTION — the twelve port mouths

OTHER — none

Masks must use exactly the same coordinates as the master sprite.

No scaling, recropping or repositioning between masks.

For a binary selection mask use:

**#FF00FF** for selected pixels
transparent everywhere else

unless another mask format is specified.

---

# 24. CONCEPT SHEET OPTION

If this request is for a CONCEPT SHEET rather than the final sprite, include only the requested panels.

Suggested sheet:

1. Title and purpose
2. Large hero sprite
3. Unlit state
4. Lit state
5. Tile-footprint diagram
6. Pipe / connection diagram
7. Mechanical close-up
8. Layer breakdown
9. Optional animation breakdown
10. 64×64 icon
11. Material / colour palette

Concept sheets may use a neutral presentation background.

Final sprites may not.

---

# 25. FINAL SPRITE OPTION

If this request is for the MASTER GAME SPRITE:

Produce ONE clean isolated machine.

No:

* title
* labels
* captions
* borders
* concept sketches
* tile grid
* arrows
* measurements
* colour palette
* inset images

Transparent background only.

---

# 26. EXPORT / FRAME CONSISTENCY

Recommended working resolution:

**2× Factorio resolution — 64 source pixels per tile, displayed with scale 0.5.**

Use enough extra canvas around the tile footprint for:

* height
* overhangs
* fluid connectors
* mechanical movement
* shadows

Do not crop moving or projecting components.

For sprite sheets:

Every animation cell must have exactly the same width and height.

Maintain a fixed origin in every cell.

Leave explicit spacing between preview frames if making a review sheet so pixels from neighbouring frames never intersect.

For the actual game spritesheet, use the frame dimensions expected by the prototype definition.

---

# 27. HARD DESIGN LOCKS

The following features may NOT be redesigned:

The squat banded drum: wider than it is tall, three distinct lead shield bands on bolted lugs with plain shell between them

The exposed agitator drive on the crown, with the six-armed spider coupling drawn FREE — a visible gap all round, nothing bridging it

The uniform base: a bolted gutter and skirt identical on all four sides, twelve identical open port mouths three to a side, and no side that reads as a front

The colour placement: works teal on the roof only (drive guard and inspection-hatch cover), radiant green-white in the three sight slots only, bare metal and copper everywhere at the edge — and the teal and the green-white never adjacent

The following dimensions are HARD measurements:

Ground footprint 3.000 × 3.000 tiles = 192 × 192 source px, the outer edge of the gutter landing on that line; nothing crosses it

Each port mouth 0.8 tile = 51 source px external diameter, its neck no more than 0.3 tile (≈ 20 px) deep, centred on the centre-line of its edge tile at [-1, 0, +1]; the three mouths on a side together span about four fifths of that side

Spider coupling animation: 12 frames, 5° per frame, 60° loop; frame 0 identical to the unlit master sprite

If an existing reference sprite is supplied, preserve everything not explicitly listed as changing.

A correction request is NOT permission to reinterpret the entire machine.

---

# 28. PROHIBITED CHANGES

Do NOT:

* rotate the camera
* turn the footprint into a diamond
* alter the building's footprint
* make the image photorealistic
* use strong perspective
* introduce arbitrary pipes
* introduce arbitrary chimneys
* introduce random antennas
* add decorative glowing strips without function
* change the material palette between states
* change lighting between lit and unlit states
* resize components between animation frames
* move static bolts or scratches between frames
* crop the sprite tightly to the machine footprint
* paint terrain into a final transparent sprite

Additional building-specific prohibitions:

It must not read as a vanilla chemical plant, a Helium Concentrator or a storage tank: no chimneys, exhaust stacks, smoke, flame or steam (there is no air here), no red-and-white paint, no tall ribbed drum, no riser leaving the top, no frost, no pale blue, no orange glow

No side may be a front: no porch, loading bay, stepped deck, asymmetric skirt, hazard marking on some corners and not others, or pipework at any one edge; no pipe runs down the outside of the machine to the gutter; no paint, tint, stain, fluid colour or glow on or within half a tile of any footprint edge; no port mouth drawn differently from the other eleven

No output chute and no product anywhere; and the teal never glows, never takes a bloom or rim light, and never touches or sits beside the green-white light

---

# 29. FINAL QUALITY CHECK

Before accepting the sprite verify:

□ Correct tile footprint
□ 64 source px per tile at 2× production scale
□ Correct Factorio steep top-down camera
□ Ground footprint square to frame
□ Correct entity anchor
□ Upper-left lighting
□ Transparent background
□ Clear silhouette at gameplay size
□ Materials match vanilla Factorio visual language
□ Connections align to intended tile locations
□ Fluid connections have open dark bores, not blank caps
□ No unintended pipes or ports
□ Lit and unlit states are pixel-aligned
□ Only specified emissive elements change between states
□ Animation has no frame drift
□ Directional variants retain the same camera
□ Adequate padding prevents clipping
□ No concept-sheet furniture in final sprite
□ No unexplained redesigns

---

# 30. BUILD-SPECIFIC BRIEF

**BUILDING:**
Reaction plant

**FOOTPRINT:**
3 × 3

**FUNCTION:**
Shielded batch reactor: radiant solution + crust gas in, a solid radiant fuel cell out. The Core's whole power supply passes through it.

**PRIMARY FORM:**
A squat riveted precipitation drum, wider than it is tall, strapped in three lead shield bands, standing on a low skirt inside a square bolted service gutter that is identical on all four sides.

**DISTINCTIVE FEATURE:**
The banded drum with an exposed agitator drive turning on its crown — a free spider coupling between a teal-guarded motor block and the crown bearing — and three green-white sight slots low on the near shoulder.

**MATERIALS:**
Riveted warm iron-nickel plate `#4A463F`–`#6E685C`; lead bands `#5A5A60`–`#7A7A80`; dark cast iron `#3B3B40`; copper and brass used freely `#8A5A32`–`#C88A4A`. Tier-0 finish: rivets, bolts, cast housings, weld seams, rust staining, wear. Nothing flush or seamless.

**ACCENT COLOUR:**
Works teal `#2A7F7A`, dark matte chipped paint, roof only: the drive guard and the inspection-hatch cover.

**FLUID CONNECTIONS:**
2 inputs north at [-1, -1.5] and [+1, -1.5], 1 output south at [0, +1.5]; they rotate with the entity while the building does not. Drawn as twelve identical open-bored mouths, three per side, 0.8 tile (51 px) across, none marked as input, output or fluid.

**ITEM INPUT/OUTPUT:**
NONE — no chute, no hatch, no product drawn.

**UNLIT ELEMENTS:**
The three sight slots dark behind their housings; the status-lamp lens dark in its bezel; the coupling stopped at frame 0.

**LIT ELEMENTS:**
The three sight slots only, radiant green-white `#A8E8C0`–`#E8FFF0`, constant brightness, short soft bloom on the shell around each.

**ANIMATION:**
The spider coupling only: 12 frames, 5° per frame, 60° seamless loop. Everything else static.

**DIRECTIONS:**
1

**HARD DIMENSIONS:**
Footprint 192 × 192 source px exactly (3.000 tiles), nothing crossing it; port mouths 51 px external diameter, necks ≤ 20 px deep, on the edge-tile centre-lines; drum about 2.2 tiles (≈ 141 px) in diameter and about half as tall as it is wide; whole sprite not wider than it is tall.

**DESIGN LOCKS:**
Squat banded drum; free spider coupling on the crown; uniform gutter with twelve identical mouths and no front; teal on the roof only, green-white in the slots only, never adjacent.

**PROHIBITIONS:**
No chimneys, exhaust, smoke, flame, steam, frost, orange or red-and-white; no front face; no pipework down the outside or at any one edge; no paint, stain or glow within half a tile of an edge; no output chute or product; no glowing teal.

**OUTPUT:**
CONCEPT SHEET (round 5) — title and purpose, large hero sprite, unlit state, lit state, top view with tile-footprint and the twelve port positions, drive-head close-up showing the gap round the coupling, shield-band-and-lug close-up, layer breakdown, 64×64 icon, material / colour palette. Then, once approved: MASTER SPRITE (unlit) → LIT+UNLIT PAIR → ANIMATION SHEET → ICON → MASKS.
