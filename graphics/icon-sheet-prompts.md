# Icon generation — grouped sheets, one per production chain

How the mod's 29 flat 2D icons get made. It replaces the per-icon approach in
[icon-prompts.md](icon-prompts.md), which is **stale**: that document was
written for the Thermionic design of Fulgora ↔ Aquilo (Copper Foil, Catalyst
Rod, Molten Scrap, Thermionic Assembly) and not one of those prototypes exists
in the mod any more. Nothing in it should be generated.

Entity sprites are a different problem and have their own document —
[building-spec-template.md](building-spec-template.md). Its Appendix A (prompt
anatomy), B (browser generation) and C (production pipeline) apply here too and
are not repeated below; read them first.

---

## Why grouped, and not one icon at a time

Every icon in this mod is seen next to its siblings — in a recipe tooltip, in
the crafting menu, on a belt. What matters is not whether one icon is good but
whether the eight icons of a chain read as **eight things made from each
other**. Generated one at a time, they do not: the same brief produces a
different metal, a different light and a different sense of scale on every run,
and the drift is invisible until they are seen together.

So a chain is generated as one image. The generator is shown the whole family
at once and has to make them differ from each other on purpose — cast ingot
against homogenised ingot, cold cryogen against spent cryogen — which is
exactly the read the player needs and the thing a per-icon prompt cannot ask
for.

It is also cheaper. Five sheets replace twenty-nine generations.

### The two-sheet rule

Each chain produces two images, in order:

| | Sheet | Canvas | What it is for |
| - | ----- | ------ | -------------- |
| **A** | Review sheet | landscape 3:2 | Labelled cells on dark charcoal, plus a palette strip. Judged as one image: does the family hang together, does each object read at a glance, is any pair too close to tell apart? |
| **B** | Harvest sheet | landscape 3:2 | The *same* objects, unlabelled, evenly spaced on a flat neutral field. Cut into cells and fed to `tools/key-icons.py`. |

**Sheet B is an edit of Sheet A, never a fresh generation.** This is the rule
from the template's Appendix B and it is not optional here: the whole point of
the exercise is that the approved family survives into the files, and asking
for the same nine objects again produces nine different objects.

### Harvesting

Two commands, and neither involves a generator:

```
tools/cut-icon-sheet.py <harvest sheet> <dir> name1 name2 ...   # sheet -> one PNG per icon
tools/key-icons.py graphics/icons <dir>/name1.png:name1 ...     # PNG -> 64px mipmap strip
```

`cut-icon-sheet.py` does not assume the grid the prompt asked for — generators
never space cells evenly. It takes the background colour from the border band,
marks every pixel far enough from it, and splits the mask into rows and then
columns on runs of empty scanlines, so it finds the objects wherever they
actually landed. It prints what it found and warns if the count does not match
the names given, which is the check that the sheet is harvestable at all.

`key-icons.py` then does the rest — keys the flat background out, crops to
the object's bounding box, squares it, downsamples to 64 px and bakes the
120×64 mipmap strip the repo's `icon_mipmaps = 4` expects. It also writes a
keyed 1024 px master under `masters/` so the keying can be judged at full size.

Technologies get **their own sheet**, at the end of this document. They were
originally to be generated one at a time — they are 256 px illustrated scenes
rather than objects on a bench — but the grouping argument applies to them just
as strongly, and one sheet of four came back usable first time. They are cut the
same way and keyed with `--size 256`, because vanilla ships a technology icon as
a 480×256 strip exactly as it ships a 64 px icon as 120×64.

---

## Global style guide — carried by every sheet prompt below

> Factorio "Space Age" item icons. Each object is a small rendered industrial
> item painted in a semi-realistic sci-fi/industrial style — not flat, not
> cartoon, not photo-real. Three-quarter view, slightly from above, as if
> resting on a workbench. Soft single-direction studio lighting from the
> upper-left, a visible specular highlight, subtle ambient occlusion where
> surfaces meet. Every object in the sheet is lit from the same direction, at
> the same intensity, at the same apparent scale and level of detail, and
> rendered at the same distance — they are one set. Each object fills roughly
> 75–85% of its own cell, centred, with even padding.

Two constraints that are worth more than the wording:

- **Silhouette before detail.** These display at 32 px and at 16 px. One clear
  focal read per object, bold shape, no busy composition — the render underneath
  can carry as much detail as it likes.
- **Adjacent icons must not collide.** Where two items in a chain are the same
  object in two states (cast/homogenised ingot, cold/spent cryogen, radiant/
  seeded chunk) the prompt names the *one* difference that has to carry the
  read, and says it must survive being shrunk to 16 px. Colour alone does not
  survive; shape and value do.

### The 16 px test, and why it is not optional

**Judge every sheet by downsampling it, not by looking at it.** This is the icon
equivalent of the template's "measure every plate" rule, and it has caught a
collision on every chain generated so far — twice on sheets that looked
excellent at full size.

Cut the cells out of the sheet and resize each to 16×16, then look at the row
with the labels covered. Two failures recur, and neither is visible at full
resolution:

1. **Surface differences vanish; only silhouette survives.** Chain 1's cast and
   homogenised ingot were the same block with different banding — perfectly
   clear at 1536 px, literally the same icon at 16 px. The fix is never "make
   the texture stronger"; it is to give the two objects different *shapes*.
2. **Small details are erased entirely.** Chain 2's seed plate had crystal
   sprouts that simply disappeared, leaving a plain slab indistinguishable from
   the cold-welded plate beside it. A detail that carries an item's identity has
   to be large enough to break the object's outline.

### Standard tail, verbatim on every sheet prompt

```text
Painted semi-realistic industrial game art. Consistent lighting, scale and
rendering across every cell. No characters, no photorealism, no logos, no
watermark, no border or frame around the sheet, no ground texture or scenery
under the objects, no baked drop shadows between cells.
```

---

# Chain 1 — Melt and cast

The Core's own loop: draw melt from a vent on helium it cannot make, let fifty
gravities take the dross out of it, cast what is left. Eight icons, and the
palette is iron-nickel grey against melt orange against a single cold blue.

| Icon | File | What it is |
| ---- | ---- | ---------- |
| Kamacite ore | `icons/kamacite-ore.png` | The iron-nickel alloy of a planetary core, exposed by the shattering |
| Molten kamacite | `icons/fluid/molten-kamacite.png` | Metal-bearing melt from a vent; too hot and heavy to barrel |
| Helium-3 | `icons/fluid/helium-3.png` | Primordial gas, inert, cold and scarce — the only thing that lifts melt |
| Settled melt | `icons/fluid/settled-melt.png` | Melt with the dross gone out of it |
| Dross | `icons/dross.png` | What sinks out under fifty gravities. Ground for beds |
| Cast ingot | `icons/cast-ingot.png` | Uneven: the heavy fraction settled while it cooled |
| Homogenised ingot | `icons/homogenised-ingot.png` | The same ingot, alloyed evenly, because in orbit nothing settles |
| Kamacite plate | `icons/kamacite-plate.png` | The chain's workhorse plate |

**The pair that has to survive 16 px:** cast ingot and homogenised ingot are
the same billet. The difference is *banding* — the cast one is visibly layered,
heavy at the bottom; the homogenised one is uniform. Carry it in value, not hue.

## Sheet A prompt

```text
A single landscape reference sheet of eight Factorio Space Age item icons for
one production chain, laid out as a 4 by 2 grid of labelled cells on a dark
charcoal background, in the style of a game art bible page. Each cell holds one
rendered object, three-quarter view slightly from above as if resting on a
workbench, lit from the upper-left, all eight at the same apparent scale and
level of detail so they read as one set.

Top row, left to right. One: a rough chunk of iron-nickel meteoric ore, dark
grey-brown crust broken open to show a bright metallic silver-grey interior
with a faint crystalline lattice pattern in the exposed face. Two: a small pool
of molten metal, dense and heavy-looking, glowing orange-white at its centre
and cooling to a dark scabbed grey-brown skin at its rim. Three: a compact
volume of pale ice-blue gas, wisping at the edges, with a bright near-white
core; it reads as cold and inert, not as steam and not as a flame. Four: a
small pool of clean molten metal, brighter and more even than cell two, an
unbroken mirror-bright orange-gold surface with no scum or skin on it at all.

Bottom row, left to right. Five: a loose heap of dull grey-brown granular slag,
matte, powdery, entirely without shine or glow. Six: a cast metal ingot lying at
a slight angle, visibly layered in horizontal bands, the lower bands darker and
denser than the upper ones, one corner rough where it was struck from the mould.
Seven: the same ingot shape at the same angle, but completely uniform in tone
end to end, smooth, faintly iridescent, with no banding whatsoever. Eight: a
flat rectangular metal plate with slightly bevelled edges and a brushed
grey-silver surface with a faint warm undertone.

Cells six and seven must be recognisably the same object in two states, and the
one difference that separates them is the banding, which has to stay legible
when the icons are shrunk to sixteen pixels: cell six layered and bottom-heavy,
cell seven uniform.

Palette across the whole sheet: iron-nickel grey #6E6A62 through #B4B0A6, melt
orange #E8863A through #FFD27A, dross brown-grey #5A5248, and one cold pale
blue #B8D8E8 used only in cell three. Keep the sheet's greys neutral and avoid
drifting warm.

Small caption labels under each cell are wanted: KAMACITE ORE, MOLTEN KAMACITE,
HELIUM-3, SETTLED MELT, DROSS, CAST INGOT, HOMOGENISED INGOT, KAMACITE PLATE.
Include a strip of eight colour swatches along the bottom edge.

Painted semi-realistic industrial game art. Consistent lighting, scale and
rendering across every cell. No characters, no photorealism, no logos, no
watermark, no border or frame around the sheet, no ground texture or scenery
under the objects, no baked drop shadows between cells.
```

## Sheet B prompt — run only after Sheet A is approved, attached

```text
Using the attached approved sheet as the source, produce a clean harvest sheet
of the same eight objects. Every object is unchanged in design, proportion,
colour, lighting direction and level of detail; this is a re-layout, not a
redesign, and nothing may be re-interpreted.

Changes permitted, and only these: (1) remove all caption text, panel labels,
the swatch strip and every cell divider line; (2) place the eight objects on a
flat, even, mid-grey field of a single uniform colour, the same colour behind
every object, with no gradient, vignette, texture or lighting falloff anywhere
in the background; (3) space them on a regular 4 by 2 grid with generous even
margins so that no object touches or overlaps another and none is clipped by
the sheet edge; (4) drop the contact shadows so each object sits on the flat
field with nothing under it.

Keep the same reading order as the approved sheet: kamacite ore, molten
kamacite, helium-3, settled melt on the top row; dross, cast ingot, homogenised
ingot, kamacite plate on the bottom row.
```

---

# Chain 2 — Whisker beds

Metal grown rather than smelted. Gleba farms food; the Core farms kamacite, on
ground made from what the melt threw away. Four icons, and the family's whole
identity is *crystal*: everything here is grown, faceted and silver-white,
which is what separates it from Chain 1's cast and poured metal.

| Icon | File | What it is |
| ---- | ---- | ---------- |
| Seed plate | `icons/seed-plate.png` | Plant it on a bed and it grows |
| Kamacite whiskers | `icons/kamacite-whiskers.png` | Metal that crystallised rather than being cast |
| Cold-welded plate | `icons/welded-plate.png` | Two clean surfaces, touched in vacuum until they forgot they were two |
| Whisker bed | `icons/whisker-bed.png` | Ground made from what the melt threw away (a tile item) |

**The trap:** the seed plate and the cold-welded plate are both plates. The
seed plate is small, thin and has something growing *on* it; the welded plate is
thick, doubled, and has a visible seam through its edge.

## Sheet A prompt

```text
A single landscape reference sheet of four Factorio Space Age item icons for
one production chain, laid out as a 2 by 2 grid of labelled cells on a dark
charcoal background, in the style of a game art bible page. Each cell holds one
rendered object, three-quarter view slightly from above as if resting on a
workbench, lit from the upper-left, all four at the same apparent scale and
level of detail so they read as one set.

One: a small square metal plate scored in a fine grid, with three tall thick
silver-white crystal spikes clustered off-centre on it, each roughly as tall as
the plate is wide, rising clear above the plate so the object's outline is a
slab with spikes coming off it. The plate is small; the spikes read first. Two:
a dense cluster of long, thin, needle-like metal crystals fanning outward from a
common base, brilliant silver-white with faint blue-grey shadows between the
needles, sharp and fibrous, clearly grown rather than cut or cast, with no base
plate under it. Three: a thick rectangular metal plate seen at a slight angle,
visibly made of two plates pressed face to face with the upper one offset
sideways from the lower so the silhouette is a stepped double slab with a
visible ledge, and a fine continuous seam line between them; the surfaces are
clean, matte and unscorched, with no weld bead, no melt, no heat discolouration
anywhere. Four: a square slab of compacted dark grey-brown granular ground, its
top deeply furrowed in rows, with a dense cluster of five or six silver crystal
spikes rising from one corner.

Cells one and three are both plates and must not be confusable: cell one is a
small slab dominated by the spikes above it; cell three is a stepped double slab
with nothing growing on it. Cells one, two and four all carry crystal and must
still differ in silhouette: one is spikes on a base, two is a radial fan with no
base, four is a furrowed brown bed with spikes at one corner.

Palette across the whole sheet: crystal silver-white #D6DAE0 through #FFFFFF
for everything grown, iron-nickel grey #6E6A62 through #B4B0A6 for everything
worked, and dross brown-grey #5A5248 for the bed ground. No heat, no glow, no
orange anywhere on this sheet — nothing in this chain was ever hot.

Small caption labels under each cell are wanted: SEED PLATE, KAMACITE WHISKERS,
COLD-WELDED PLATE, WHISKER BED. Include a strip of six colour swatches along
the bottom edge.

Painted semi-realistic industrial game art. Consistent lighting, scale and
rendering across every cell. No characters, no photorealism, no logos, no
watermark, no border or frame around the sheet, no ground texture or scenery
under the objects, no baked drop shadows between cells.
```

## Sheet B prompt — run only after Sheet A is approved, attached

```text
Using the attached approved sheet as the source, produce a clean harvest sheet
of the same four objects. Every object is unchanged in design, proportion,
colour, lighting direction and level of detail; this is a re-layout, not a
redesign, and nothing may be re-interpreted.

Changes permitted, and only these: (1) remove all caption text, panel labels,
the swatch strip and every cell divider line; (2) place the four objects on a
flat, even, mid-grey field of a single uniform colour, the same colour behind
every object, with no gradient, vignette, texture or lighting falloff anywhere
in the background; (3) space them in one row of four with generous even margins
so that no object touches or overlaps another and none is clipped by the sheet
edge; (4) drop the contact shadows so each object sits on the flat field with
nothing under it.

Keep the reading order: seed plate, kamacite whiskers, cold-welded plate,
whisker bed.
```

---

# Chain 3 — The field coil

The Core's reason to exist. Five capstone products arrive from four worlds and
are consumed here, each with a different local input, into five intermediates;
the intermediates combine into two end products; only those build a segment.
Nine icons, and the family problem is the opposite of the other chains: these
are nine *manufactured components*, and they will collapse into nine grey
lumps unless each one keeps the colour of the world it came from.

| Icon | File | Comes from |
| ---- | ---- | ---------- |
| Field conductor | `icons/field-conductor.png` | Fulgora ↔ Aquilo, drawn in freefall |
| Magnetic core billet | `icons/magnetic-core-billet.png` | Vulcanus ↔ Fulgora, cast into settled melt |
| Reinforced frame | `icons/reinforced-frame.png` | Vulcanus ↔ Gleba, reinforced with grown metal |
| Insulation sleeve | `icons/insulation-sleeve.png` | Fulgora ↔ Gleba, poured around in raw melt |
| Coolant charge | `icons/coolant-charge.png` | Gleba ↔ Aquilo, charged with helium that never left |
| Coil assembly | `icons/coil-assembly.png` | The four solid intermediates, assembled |
| Coolant loop | `icons/coolant-loop.png` | The charges, plumbed into a loop |
| Field coil segment | `icons/field-coil-segment.png` | Assembly + loop. A hundred of these win the game |
| Geodynamic science pack | `icons/geodynamic-science-pack.png` | Only assemblable on the Core |

**The read that matters most:** the field coil segment is the last object
before the endgame and has to look like it contains the two things above it —
the assembly's coil and the loop's plumbing, in one sealed unit. It is the only
icon in the mod a player will stare at a hundred times.

**Science pack shape is fixed by convention.** Every science pack in the game
is a bottle or flask silhouette. Do not invent a new container for it; the
player finds it by silhouette in a menu of eleven others.

## Sheet A prompt

```text
A single landscape reference sheet of nine Factorio Space Age item icons for
one production chain, laid out as a 3 by 3 grid of labelled cells on a dark
charcoal background, in the style of a game art bible page. Each cell holds one
rendered object, three-quarter view slightly from above as if resting on a
workbench, lit from the upper-left, all nine at the same apparent scale and
level of detail so they read as one set.

Top row, left to right. One: a tight coil of fine drawn wire with a faint
blue-white sheen, wound on a small dark spindle, the winding perfectly even.
Two: a short heavy cylindrical metal billet standing on end, dark and dense,
with a dull violet-grey sheen and one machined bright face. Three: an open
rectangular frame or cradle of welded struts, pale grey metal, with thin
silver-white crystal fibres visibly bound along its inner members.

Middle row, left to right. Four: a short thick tube or sleeve of matte cream
polymer, one end cut open to show the dark metal it was poured around. Five: a
sealed metal capsule standing upright, heavily ribbed, frost gathering on its
lower half, a small pale blue window near its top.

Six: a finished cylindrical component built from the four objects above it —
the drawn winding wrapped around the dark billet, held inside the strut frame,
with the cream sleeve visible at one end. It must read as an assembly of parts
that are individually recognisable from cells one to four.

Bottom row, left to right. Seven: a closed loop of ribbed metal pipework
doubling back on itself, pale frost along its length, with two capsule-shaped
reservoirs set into the run. Eight: a single sealed heavy cylindrical unit,
armoured, with a dark banded coil visible through a long slot down one side and
frosted pipework wrapping its outside; it must read as cell six and cell seven
combined and sealed into one finished part, the most substantial and most
finished-looking object on the sheet. Nine: a science pack — a stoppered glass
laboratory flask of the standard Factorio science pack silhouette, filled with
a dark, faintly luminous grey-violet fluid with a slow mineral swirl in it, a
metal collar at the neck.

Palette across the whole sheet: iron-nickel grey #6E6A62 through #B4B0A6 as the
common metal, and one accent hue per origin, kept distinct — superconductor
blue-white #9FC4E8 in cells one and six, magnetar violet-grey #7A6E8A in cells
two and nine, grown silver-white #D6DAE0 in cell three, cream polymer #D8CBAC in
cell four, and cold blue #B8D8E8 in cells five and seven. Cell eight carries
several of them at once because it contains the others.

Small caption labels under each cell are wanted: FIELD CONDUCTOR, MAGNETIC CORE
BILLET, REINFORCED FRAME, INSULATION SLEEVE, COOLANT CHARGE, COIL ASSEMBLY,
COOLANT LOOP, FIELD COIL SEGMENT, GEODYNAMIC SCIENCE PACK. Include a strip of
eight colour swatches along the bottom edge.

Painted semi-realistic industrial game art. Consistent lighting, scale and
rendering across every cell. No characters, no photorealism, no logos, no
watermark, no border or frame around the sheet, no ground texture or scenery
under the objects, no baked drop shadows between cells.
```

## Sheet B prompt — run only after Sheet A is approved, attached

```text
Using the attached approved sheet as the source, produce a clean harvest sheet
of the same nine objects. Every object is unchanged in design, proportion,
colour, lighting direction and level of detail; this is a re-layout, not a
redesign, and nothing may be re-interpreted. In particular the coil assembly,
the coolant loop and the field coil segment must keep the exact relationship
they have in the approved sheet: the segment still visibly contains the other
two.

Changes permitted, and only these: (1) remove all caption text, panel labels,
the swatch strip and every cell divider line; (2) place the nine objects on a
flat, even, mid-grey field of a single uniform colour, the same colour behind
every object, with no gradient, vignette, texture or lighting falloff anywhere
in the background; (3) space them on a regular 3 by 3 grid with generous even
margins so that no object touches or overlaps another and none is clipped by
the sheet edge; (4) drop the contact shadows so each object sits on the flat
field with nothing under it.

Keep the same reading order as the approved sheet, row by row.
```

---

# Chain 4 — Fulgora ↔ Aquilo

The one cross-planet tree that is built. Every step drinks cold and hands back
warm, which is the whole mechanic, so the pair of cryogen fluids is the most
important read on the sheet. Four icons.

| Icon | File | What it is |
| ---- | ---- | ---------- |
| Cold cryogen | `icons/fluid/cold-cryogen.png` | Cold enough to make holmium behave |
| Spent cryogen | `icons/fluid/spent-cryogen.png` | Warm, and useless until something cold is done to it again |
| Fluorinated holmium | `icons/fluorinated-holmium.png` | Holmium that has met fluorine |
| Superconducting winding | `icons/superconducting-winding.png` | A conductor that loses nothing |

**The pair that has to survive 16 px:** cold and spent cryogen are the same
fluid in two states, and the player reads them constantly because the loop only
works when both are plumbed. Cold is saturated blue and *still*; spent is
washed-out grey-teal and *convecting*, with visible movement in it. Do not
make spent cryogen orange — it is not hot, it is merely no longer cold.

**And one cross-chain collision to avoid.** The superconducting winding is a
**torus with a hole through it**, never a spool — chain 3's field conductor is
already a blue-wired spool on a spindle, and the first round of this sheet drew
the winding as a second one. The two sit next to each other in the conductor's
own recipe, so they must not share a silhouette. This is the failure the
per-chain 16 px test cannot catch on its own: **check a new chain's icons
against the chains already locked, not only against each other.**

## Sheet A prompt

```text
A single landscape reference sheet of four Factorio Space Age item and fluid
icons for one production chain, laid out as a 2 by 2 grid of labelled cells on
a dark charcoal background, in the style of a game art bible page. Each cell
holds one rendered subject, lit from the upper-left, all four at the same
apparent scale and level of detail so they read as one set. The two fluid cells
are flatter and more abstract than the two object cells — a liquid surface
rather than a solid thing on a bench — but still lit and shaded, never flat
colour.

One: a small pool of deep saturated blue liquid, perfectly still, mirror-
smooth, with a hard bright specular highlight and a fine rime of frost around
its rim. It reads as intensely, statically cold. Two: the same pool of the same
liquid, but drained of saturation to a pale washed grey-teal, its surface
visibly convecting in slow curls, the frost gone from the rim and the highlight
soft and diffuse. It must read as the same fluid in a used state, not as a
different substance, and it must not read as hot: no orange, no red, no glow.
Three: a small flat wafer or plate of pale metal held at a slight angle, its
surface an iridescent violet-to-pink sheen over a silver base, with a fine
crystalline frosted bloom across one face where the fluorine took. Four: a
self-supporting toroidal coil — a doughnut-shaped ring of fine pale blue-white
wire wound tightly around on itself, with no spool, no reel, no flanges and no
central hub of any kind, one short loose wire end tailing off it and a fine
frost sheen where the windings meet. Its silhouette is an open ring with a hole
through the middle.

Cells one and two must be recognisably the same fluid in two states, and the
difference has to survive being shrunk to sixteen pixels: cell one deep,
saturated and still, cell two pale, desaturated and moving.

Palette across the whole sheet: cryogen blue #2E6FB0 through #8FC4EE, spent
grey-teal #7E9AA0 through #B9C9CC, holmium violet-pink #B98FD8 through #E8C2E0,
and superconductor blue-white #9FC4E8. Keep the whole sheet cold; there is no
warm colour anywhere in this chain.

Small caption labels under each cell are wanted: COLD CRYOGEN, SPENT CRYOGEN,
FLUORINATED HOLMIUM, SUPERCONDUCTING WINDING. Include a strip of six colour
swatches along the bottom edge.

Painted semi-realistic industrial game art. Consistent lighting, scale and
rendering across every cell. No characters, no photorealism, no logos, no
watermark, no border or frame around the sheet, no ground texture or scenery
under the objects, no baked drop shadows between cells.
```

## Sheet B prompt — run only after Sheet A is approved, attached

```text
Using the attached approved sheet as the source, produce a clean harvest sheet
of the same four subjects. Every subject is unchanged in design, proportion,
colour, lighting direction and level of detail; this is a re-layout, not a
redesign, and nothing may be re-interpreted. The two cryogen cells must keep
exactly the difference they have in the approved sheet.

Changes permitted, and only these: (1) remove all caption text, panel labels,
the swatch strip and every cell divider line; (2) place the four subjects on a
flat, even, mid-grey field of a single uniform colour, the same colour behind
every subject, with no gradient, vignette, texture or lighting falloff anywhere
in the background; (3) space them in one row of four with generous even margins
so that nothing touches, overlaps or is clipped by the sheet edge; (4) drop the
contact shadows so each subject sits on the flat field with nothing under it.

Keep the reading order: cold cryogen, spent cryogen, fluorinated holmium,
superconducting winding.
```

---

# Chain 5 — The corridor

What the far field gives you if you take it as it is, and what it gives you if
you sowed first. Four icons, and this is the only chain set in deep space
rather than on a planet — the objects are rock, and the one manufactured thing
among them should look out of place.

| Icon | File | What it is |
| ---- | ---- | ---------- |
| Radiant chunk | `icons/radiant-chunk.png` | The one rock the far field still offers. Inert until crushed |
| Seeded chunk | `icons/seeded-chunk.png` | A rock that was infected and left to take |
| Radiant fuel | `icons/radiant-fuel.png` | Made where it is burned, from the only material out here |
| Seed missile | `icons/seed-missile.png` | A frozen culture with a rocket around it |

**The pair that has to survive 16 px:** radiant and seeded chunk are both
asteroid fragments. Radiant is bare rock with a light *inside* it; seeded is
the same rock with something pale and organic growing *across* its surface. The
difference is internal glow versus external growth, and it must read in
silhouette, so the seeded chunk's growth has to break its outline.

## Sheet A prompt

```text
A single landscape reference sheet of four Factorio Space Age item icons for
one production chain, laid out as a 2 by 2 grid of labelled cells on a dark
charcoal background, in the style of a game art bible page. Each cell holds one
rendered object, three-quarter view slightly from above, lit from the upper-
left, all four at the same apparent scale and level of detail so they read as
one set.

One: an angular fragment of dark grey asteroid rock, its faces sharp and
freshly broken, with a network of fine fractures running through it that glow a
soft cool green-white from within, as though the light is inside the stone
rather than on it. The outline of the rock is clean and unbroken. Two: a
fragment of the same dark rock at the same size, but with pale grey-green
organic growth spreading across its surface — a crust of fine filaments and
small nodules that spills over the rock's edges and visibly breaks its
silhouette. The rock beneath does not glow. Three: a squat hexagonal fuel
slug lying on its side at a slight diagonal, distinctly wider than it is tall,
with flat hexagonal end faces, heavy chamfered metal edges, and a cool
green-white glow showing out of the open end face toward the viewer. It is
clearly made rather than found, and should look out of place beside the two
rocks. It must not be a standing canister — chain 3's coolant charge already
owns that silhouette. Four: a slim missile with a blunt rounded nose rather than a sharp
point, held at a slight diagonal, its casing pale frosted metal, four small fins
at the tail, and a small round window near the nose showing a pale green-white
frozen culture inside.

Cells one and two must be recognisably the same rock in two states, and the
difference has to survive being shrunk to sixteen pixels and read in silhouette
alone: cell one is bare rock with light inside it and a clean outline, cell two
is rock with growth over it and a broken, fuzzy outline.

Palette across the whole sheet: asteroid grey #4A4A4E through #8A8A90, radiant
green-white #A8E8C0 through #E8FFF0 used only as internal light, pale organic
grey-green #9FB89A, and frosted metal #C0C8CC. The background of each cell is
dark; keep the rocks genuinely dark so the radiant light reads.

Small caption labels under each cell are wanted: RADIANT CHUNK, SEEDED CHUNK,
RADIANT FUEL, SEED MISSILE. Include a strip of six colour swatches along the
bottom edge.

Painted semi-realistic industrial game art. Consistent lighting, scale and
rendering across every cell. No characters, no photorealism, no logos, no
watermark, no border or frame around the sheet, no ground texture or scenery
under the objects, no baked drop shadows between cells.
```

## Sheet B prompt — run only after Sheet A is approved, attached

```text
Using the attached approved sheet as the source, produce a clean harvest sheet
of the same four objects. Every object is unchanged in design, proportion,
colour, lighting direction and level of detail; this is a re-layout, not a
redesign, and nothing may be re-interpreted. The radiant chunk keeps its clean
outline and internal glow; the seeded chunk keeps the growth that breaks its
outline.

Changes permitted, and only these: (1) remove all caption text, panel labels,
the swatch strip and every cell divider line; (2) place the four objects on a
flat, even, mid-grey field of a single uniform colour, the same colour behind
every object, with no gradient, vignette, texture or lighting falloff anywhere
in the background — mid-grey, not dark, even though the approved sheet was dark;
(3) space them in one row of four with generous even margins so that nothing
touches, overlaps or is clipped by the sheet edge; (4) drop the contact shadows
so each object sits on the flat field with nothing under it.

Keep the reading order: radiant chunk, seeded chunk, radiant fuel, seed missile.
```

---

# Recipe icons

Only a recipe whose name does not match a single output item needs its own
icon; Factorio otherwise falls back to the output's. Four qualify, all of them
because they split one input into two outputs or run the same vessel two ways.

They are **not** generated. Each is a composite of icons this document already
produces, and a composite assembled from the real files is exact, free and
cannot drift:

| Recipe | Built from |
| ------ | ---------- |
| `sae-gravity-settling` | Settled melt, with dross small in the corner |
| `sae-quenched-settling` | Settled melt, with vanilla steam small in the corner |
| `sae-radiant-crushing` | Radiant chunk, with radiant fuel small in the corner |
| `sae-seeded-crushing` | Seeded chunk, with its output small in the corner |

Factorio composes these natively — an `icons` array of two layers with the
second `scale`d down and `shift`ed into a corner. No image work at all.

---

# Technologies — 256 px, `graphics/technology/`

Four technologies carry the tree's shape and are worth drawing; the rest keep
borrowing. Vanilla technology icons are an illustrated *scene* rather than an
object on a bench, so the cells are busier than an item chain's — but they are
still generated as **one sheet of four**, on the same flat field, and harvested
with the same two tools:

```
tools/cut-icon-sheet.py graphics/technology/concept/v1-sheet.png <dir> \
    core-discovery gravity-settling whisker-beds field-coils
tools/key-icons.py --size 256 graphics/technology <dir>/core-discovery.png:sae-core-discovery ...
```

**One of the four needs keying by hand.** `key-icons.py` drops pixel regions not
connected to the main mass, which is right for a building plate and wrong for
*Core discovery*, whose debris ring and course arrow are deliberately floating —
the tool removed them and left a bare sphere that then collided with the planet's
own starmap icon. That cell is keyed with a plain distance-from-background ramp
and no island removal. The other three connect to themselves and key normally.

The four prompts below are kept as the record of what each cell asks for; the
sheet prompt that was actually sent is their four scene descriptions in one
message, on a flat mid-grey field with no labels.

### Core discovery — `sae-core-discovery.png`

```text
A Factorio Space Age technology icon, 256 pixels square, illustrated as a small
scene rather than a single object. A dark metallic planetary core hanging in
black space, its surface a frozen grey crust cracked open in places to show a
dull orange heat beneath, with the scattered debris of a shattered world
drifting in a broad ring around it and one faint plotted course line arriving
from off-frame. It should read as a destination that has just become reachable.
Painted semi-realistic industrial game art, richer and busier than an item
icon, no text, no logos, no characters, transparent background.
```

### Gravity settling — `sae-gravity-settling.png`

```text
A Factorio Space Age technology icon, 256 pixels square, illustrated as a small
scene rather than a single object. A tall narrow industrial settling vessel cut
away to show molten metal standing inside it, clean bright orange-gold metal in
the upper two thirds and dark grey-brown dross visibly sunk into a dense layer
at the bottom, with a heavy downward weight to the whole composition. It should
read as separation done by weight alone rather than by any machine. Painted
semi-realistic industrial game art, richer and busier than an item icon, no
text, no logos, no characters, transparent background.
```

### Whisker beds — `sae-whisker-beds.png`

```text
A Factorio Space Age technology icon, 256 pixels square, illustrated as a small
scene rather than a single object. A prepared bed of dark grey-brown granular
ground seen at a low three-quarter angle, with clusters of fine silver-white
metal crystals growing up out of it in rows, some short and new, some tall and
fully grown, catching a cold pale light. Nothing is hot and nothing is
mechanical; this is agriculture in metal. Painted semi-realistic industrial game
art, richer and busier than an item icon, no text, no logos, no characters,
transparent background.
```

### Field coils — `sae-field-coils.png`

```text
A Factorio Space Age technology icon, 256 pixels square, illustrated as a small
scene rather than a single object. A single heavy sealed cylindrical coil
segment shown centrally, armoured, with a dark banded winding visible through a
slot down its side and frosted pipework wrapping its outside, and behind it a
receding row of identical segments fading into darkness to imply a great many
more. A faint violet-white field line arcs around the foreground segment.
Painted semi-realistic industrial game art, richer and busier than an item icon,
no text, no logos, no characters, transparent background.
```

---

# Round log

Record every generation here, one row per attempt, so a later session can see
what was already tried and rejected.

| Round | Sheet | What came back | Verdict | Fix asked for |
| ----- | ----- | -------------- | ------- | ------------- |
| 1 | Chain 1 A | Layout, labels, swatch strip and palette all correct first time; landscape 1536x1024. Top row is right: ore reads as broken crust over metal, helium-3 reads cold and not steam, settled melt reads clean. **Measured at 16 px, not eyeballed** — cells cut out of the sheet and downsampled. | **Top row accepted; bottom row rejected** | Four fixes: (1) molten kamacite reads as a burning rock with flames, must read as a liquid pool with a cooling skin; (2) cast and homogenised ingot are the same silhouette and are indistinguishable at 16 px — they must differ in shape, not surface; (3) kamacite plate is a third grey wedge, must be a thin flat slab; (4) dross is dark enough to vanish against the background at small size. |
| 2 | Chain 1 A | All four fixes landed. Molten kamacite now reads as a liquid pool with a stony cooling skin; cast ingot is a squat banded block, homogenised ingot a long clean bar, kamacite plate a thin flat slab, dross lighter and coarser. Re-measured at 16 px: **all eight are distinguishable by silhouette alone.** | **Accepted — chain 1 design locked** | None. |
| 3 | Chain 1 B | Harvest sheet, produced as an edit of the approved image in the same conversation. Objects came back unchanged; background is a flat #747373 with no gradient. `cut-icon-sheet.py` found 8 objects in 2 rows, and `key-icons.py` keyed them cleanly into 64 px strips. | **Accepted — pipeline proven end to end** | None. |
| 4 | Chain 2 A | Excellent rendering and palette; the crystal fan reads perfectly. But the camera came back as a strict flat isometric, which turned every plate into the same diamond, and at 16 px the seed plate's sprouts had vanished entirely, leaving it indistinguishable from the cold-welded plate. | **Whiskers accepted; the three slabs rejected** | Four fixes: (1) three-quarter workbench camera, not flat isometric; (2) seed plate's crystal spikes made tall enough to break the object's outline and dominate the read; (3) cold-welded plate's upper plate offset sideways so the silhouette is a stepped double slab; (4) whisker bed's crystals enlarged into a corner cluster and the furrows deepened. |
| 5 | Chain 2 A | All four fixes landed. Re-measured at 16 px: spikes-on-a-base, radial fan, stepped grey slab, furrowed brown bed — **four distinct silhouettes**. | **Accepted — chain 2 design locked** | None. |
| 6 | Chain 2 B | Harvest sheet as an edit of the approved image. Flat #757575 field, no labels; `cut-icon-sheet.py` found 4 objects in 1 row. | **Accepted** | None. |
| 7 | Chain 3 A | **Accepted first round**, and the strongest sheet so far. The assembly logic reads without being told: the coil assembly visibly contains the winding, frame and sleeve, and the field coil segment visibly contains the assembly and the loop. Science pack came back on the standard flask silhouette. Measured at 16 px: all nine distinct — spool, violet cylinder, open frame, cream tube, upright capsule, cream-ended assembly, ring, wide armoured segment, flask. | **Accepted — chain 3 design locked** | None. |
| 8 | Chain 3 B | Harvest sheet as an edit of the approved image. Flat #7E7E7E field; `cut-icon-sheet.py` found 9 objects in 3 rows. | **Accepted** | None. |
| 9 | Chain 4 A | The cryogen pair landed first time and is the best state-pair on any sheet: deep saturated blue with a frost rim against pale desaturated grey-teal, visibly convecting, no warm colour anywhere. Holmium wafer reads. **But the superconducting winding came back as a blue-wired spool — the same object as chain 3's field conductor**, which was already locked. | **Three of four accepted** | One fix: make the winding a self-supporting torus with a hole through it, no spool, no reel, no flanges. |
| 10 | Chain 4 A | Winding is now an unmistakable open ring and no longer collides with the field conductor's spool. Everything else came back unchanged. | **Accepted — chain 4 design locked** | None. |
| 11 | Chain 4 B | Harvest sheet as an edit of the approved image. Flat #787777 field; `cut-icon-sheet.py` found 4 objects in 1 row. | **Accepted** | None. |
| 12 | Chain 5 A | Rock pair landed first time and is the clearest state-pair yet — bare dark rock with light inside its fractures against the same rock swallowed by pale nodular growth that genuinely breaks the outline. Missile and fuel both read. **But radiant fuel came back as a tall upright capsule, the same silhouette as chain 3's coolant charge**, differing only in glow colour. | **Three of four accepted** | One fix: radiant fuel becomes a squat hexagonal slug lying on its side, glowing out of its end face. |
| 13 | Chain 5 A | Radiant fuel is now a horizontal hexagonal slug and no longer collides with the coolant charge. Everything else unchanged. | **Accepted — chain 5 design locked** | None. |
| 14 | Chain 5 B | Harvest sheet as an edit of the approved image. Flat #828281 field; `cut-icon-sheet.py` found 4 objects in 1 row. | **Accepted** | None. |

---

# Where this got to

All five chains are through **Sheet A and Sheet B**, and every harvest sheet cuts
cleanly — 29 objects found, 29 expected, no manual cropping anywhere. The route
is proven end to end on chain 1: sheet → `cut-icon-sheet.py` → `key-icons.py` →
a 120×64 mipmap strip with correct alpha.

**All of it is now wired into the mod.** The 29 icons are in `graphics/icons/`
and `graphics/icons/fluid/`, the four technology icons in
`graphics/technology/`, every prototype has been repointed off its vanilla
placeholder, and the four composite recipe icons are built natively from two
layers. `./tools/check-data-stage.sh` passes: 52 referenced files, all present.

The graphics check earned its keep immediately — it caught
`__base__/graphics/icons/carbon.png`, which does not exist (carbon ships in
`__space-age__`). That is a path a client would have refused the mod over, and
the data stage alone would never have noticed, because it never opens an image.

What still borrows vanilla art is exactly what should: the buildings whose
sprites do not exist yet, the five capstone stubs, and the three Fulgora ↔
Aquilo technologies.
| 15 | Technology sheet | **Accepted first round.** All four scenes as briefed: the cracked metallic core with its debris ring and arriving course line, the cut-away settling vessel with dross sunk to the bottom, the crystal rows growing out of prepared ground, and the sealed coil segment with a receding row behind it and a violet field line around it. Flat #797979 field, no labels, directly harvestable. | **Accepted — technology set locked** | None. |
