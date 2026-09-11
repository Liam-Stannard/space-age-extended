# Icon generation — grouped sheets, one per production chain

How the mod's 29 flat 2D icons get made, a production chain at a time.

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

Technologies get **their own sheet**, prompted the same way. They were
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

