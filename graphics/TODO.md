# Art — what is left

State as of 2026-09-05, second art session. The icons, technology icons, planet
and six concept sheets are **committed** (`83b7512`). This session took the Bed
Tender from a locked design to shipped sprites and found the defect that every
remaining building will hit.

The working tree still carries another session's in-flight arc-mast work
(`control.lua`, `prototypes/core/planet.lua`, `design/spikes.md`,
`tools/generate-building-art.py`, the arc-mast concept plates, `tools/rcon.py`
and `graphics/icons/arc-mast.png`). Stage explicit paths; never `git add -A`
here.

---

## The defect to expect on every remaining building

**The concept sheets are drawn at a shallower camera than Factorio's
projection.** The Bed Tender's first plate came back 3.00 tiles wide by 1.84
deep — aspect **1 : 0.61** — against a vanilla 3×3 plate's **1 : 0.96**. It
passed `--report` on transparency, palette and body-metal luminance, because
none of those can see projection.

Check the **trimmed aspect** first, against a real vanilla building of the same
footprint, and fix it with a *regenerate* carrying a vanilla sprite as a camera
reference. It is written up in the template's Appendix C, under *Measure the
camera before anything else*, with the comparator table.

Two tool gaps this exposed, both fixed:

- **`check-graphics.sh` was not checking any building plate.** It grepped for a
  whole quoted path, and every sprite block writes `local ART = "__mod__/dir/"`
  then `ART .. "base.png"` — so the arc mast's four plates had never been
  verified. `tools/collect-graphics-refs.py` now resolves those bindings; the
  reference count went from 52 to 59.
- **`process-building-art.py` had no `--bottom-margin`**, so a cut plate always
  landed flush on the canvas floor and could not pass the pipeline's own check 2
  (alpha zero along both edge rows). The arc mast measures `B255` because of it.

## Fluid connections carry no effects — audit the shipped plates

Settled 2026-09-10 and written up as **convention 5** in the template: a flange,
stub or port is bare machine metal. No frost, no ice, no heat glow, no scorch,
no lagging, no fluid tint. The building's signature — the crust turbine's rime,
the vacuum furnace's heat — stops a tile short of the edge.

Two reasons: the engine stamps its **own** neutral cover
(`derive.pipe_covers()`) over an unconnected port, so a treated stub ends up with
a bare grey flange sitting in it; and a fluid box is a *socket*, not a fluid —
the same port carries whatever the player pipes into it.

The remaining option rounds were rewritten to match. **Still to check against
plates that already shipped**, none of which were drawn under this rule:

- [ ] Crust Tap — the spec calls its seam *frost + heat*; confirm neither reaches
      a connection
- [ ] Helium Concentrator — frosted, and it has fluid boxes on three faces
- [ ] Vacuum Furnace — heat, same question
- [ ] Ring Mast options A, B and C — generated before the rule, and all three
      drew a frost-jacketed inlet. Whichever wins, the frost comes off at
      **master-plate** stage, which is a separate generation anyway.
- [ ] Crust Turbine options A, B, D and E — the brief carried the rule and the
      generator ignored it: rime runs right out onto the end flanges. Same fix,
      same stage.

---

---

## Done — items 1 to 4

All four completed on 2026-09-05 and verified with `./tools/check-data-stage.sh`
(data stage OK, **52 referenced files all present**, recipes OK).

**1. Icons wired in.** All five chains cut, keyed and installed — 24 to
`graphics/icons/`, five fluids to `graphics/icons/fluid/`. Every prototype
repointed off its vanilla placeholder across nine files.

**2. Technology icons.** Generated as **one sheet of four** rather than
individually, accepted first round, keyed with the new `--size 256` option and
installed to `graphics/technology/`. `foothold()` and `geodynamic()` in
`technology.lua` now take an optional icon and default to the old stand-in, so
the three technologies with art get it and the rest are unchanged.

**3. Recipe icons.** Built natively as two-layer `icons` arrays, no generation:
gravity settling, quenched settling, radiant crushing, seeded crushing.

**4. The planet.** `planet.lua` wired to `core.png` and `starmap-core.png`;
`icon_size = 512` deleted. The other session's `day-night-cycle` change in that
file was not touched.

### Three tool bugs this pass exposed and fixed

Worth knowing, because each would have silently degraded future art:

- **`cut-icon-sheet.py` padded out-of-bounds crops with black.** A wide cell near
  a sheet edge came back with black bars welded on, which `key-icons.py` then
  read as a second background colour. Island-drop counts in the tens of thousands
  were this, not the art.
- **`cut-icon-sheet.py` squared the crop *box*,** so a wide, short scene reached
  down into the row beneath and harvested part of its neighbour. It now crops the
  object's own pixels and centres them on a square background field.
- **`key-icons.py` only ever baked 64 px strips**, and its docstring cited
  `icon_mipmaps = 4` — a property removed in Factorio 2.0, where the engine infers
  mipmaps from the image being wider than `icon_size`. It now takes `--size`.

One thing the tools cannot fix: `key-icons.py` drops regions not connected to the
main mass, which is correct for a building plate and wrong for a scene with
deliberately floating elements. The *Core discovery* technology icon is keyed by
hand for that reason — see `icon-sheet-prompts.md`.

## 5. Buildings — six designs locked, one building actually built

Every concept sheet is approved. **The Arc Mast and the Bed Tender have gone
past stage 0** into real sprites; the other five stop at "design locked".

| Building | Document | Sheet | Stages 1–6 |
| -------- | -------- | ----- | ---------- |
| Arc Mast | `building-spec-arc-mast.md` | locked | **done** — plates, glow, icon |
| Bed Tender | `building-spec-bed-tender.md` | `v2-sheet.png` | **done** — plate, shadow, bin layer, icon, recoloured crane, wired |
| Superconducting Store | `building-spec-superconducting-store.md` | `v1-sheet.png` | **done** — plate, shadow, ring glow, charge/discharge, icon, wired |
| Sealed Roboport | `building-spec-sealed-roboport.md` | `v2-sheet.png` | **done** — plate, shadow, lamp glow, icon, wired; three vanilla slots emptied |
| Radiant Generator | `building-spec-radiant-generator.md` | `v2-sheet.png` | **done** — both directions, glow split by hue, icon, wired |
| Ignition Array | `building-spec-ignition-array.md` | `concept/adopted/R-sheet.png` | **done** — the design was replaced (option R, the Suspended Core), then plate, shadow, charge glow, icon, discharge column and prototype all shipped; charged and launched on a server |
| Vent Pump | `building-spec-vent-pump.md` | `v4-sheet.png` | **all outstanding** — 4 directional frames plus an animation, the most expensive of the seven |

## 5b. Nine drafted concept sheets, none locked

Drafted 2026-09-06 from the Core production-chain review, then taken through
stage 0 in one sitting. **All nine are drafts.** Nothing is approved, so
Appendix C's *"once a design is locked, stop prompting"* rule has not started
applying to any of them, and stage 1 is blocked on the whole set being locked
together.

| Building | Sheet | Rounds | Notes for the lock review |
| -------- | ----- | ------ | ------------------------- |
| Drop Crusher | `v2-sheet.png` | 2 | v1 had copper hydraulics on a building with no fluid box; carriage read as an equipment box; too squat. All fixed. See its §19 |
| Ballast Drill | `v1-sheet.png` | 1 | **Two concerns.** No visible cutting head, so it reads as a press rather than a mining machine. And it shares a silhouette family with the Drop Crusher — posts plus a dark block |
| Dross Classifier | `v1-sheet.png` | 1 | Strong and clearly distinct. Palette added a "flywheel brown" not in §3.3 |
| Coil Separator | `v1-sheet.png` | 1 | The signature coil throat landed, field contained inside the aperture only |
| Whisker Comber | `v1-sheet.png` | 1 | The before-and-after read landed: tangle in, ordered ribbon out |
| Helium Concentrator | `v1-sheet.png` | 1 | The two-temperature split landed — frost at the waist, hot lower third |
| Vacuum Furnace | `v1-sheet.png` | 1 | Got the three-state row right: RUNNING / BLOCKED / IDLE, which is S12's latch drawn |
| Crust Tap | `v1-sheet.png` | 1 | Two-temperature read landed; burst disc and choke both present |
| Ignition Ring Mast | `v1-sheet.png` | 1 | The critical anti-read landed — no cage, no electrode, closed dark cap. It will not be confused with the Arc Mast |

### Redraw in progress — the whole set is being regenerated

The convention review found faults in eight of nine sheets, so rather than
refining each one the whole set is being redrawn against rewritten prompts. The
four rules now live in the template's §8 and in every prompt.

| Building | State |
| -------- | ----- |
| Drop Crusher | **`v4-sheet.png`** — clean on all four rules; chutes now wide-left and narrow-right on opposite faces |
| Ballast Drill | **`v2-sheet.png`** — clean; gained the toothed cutting head, so it reads as a mining machine at last |
| Dross Classifier | **LOCKED — option A, the Shaker Deck**, chosen from five on 2026-09-08. `concept/adopted/A-sheet.png` |
| Coil Separator | **LOCKED — option D, the Cold Plant**, chosen from five. The coil is buried; the machine is the refrigeration it needs. `concept/adopted/D-sheet.png` |
| Whisker Comber | **LOCKED — option C, the Spinner**, chosen from five. A standing drum, not a low box. `concept/adopted/C-sheet.png` |
| Helium Concentrator | **LOCKED — option C, the Twin Bottles**, chosen from five on 2026-09-09. Two unequal vessels, hot and cold, bridged at the waist. `concept/adopted/C-sheet.png` |
| Vacuum Furnace | **LOCKED — option A, the Pot**, chosen from five. A sealed welded drum with one clamped hatch and one lit sight port. `concept/adopted/A-sheet.png` |
| Crust Tap | **LOCKED — option A, the Bolted Collar**, chosen from five after two regenerations for the pipe connection. `concept/adopted/A-sheet.png` |
| Ignition Ring Mast | not yet redrawn |

### The five-option round, and what it is worth repeating for

Three of the nine were taken through **five designs each, compared rather than
refined** — the method the Ignition Array arrived at after four sets, and the one
that answers "was this the right idea?" rather than "is this a better version of
the idea?". Fifteen sheets, one generation apiece, a fresh conversation per option
so nothing bled between them. Decision records are in
`dross-classifier-options/`, `coil-separator-options/` and
`whisker-comber-options/`; each keeps the winner's page, the README, and a
contact sheet of all five at reduced size. The twelve losing pages and their
full-size sheets are deleted.

**Three prompt changes came out of it and should carry to the remaining four
buildings:**

* **Name the machine in the title line.** Every sheet in the set so far had
  titled itself ORE PRESS or MAGNETIC SEPARATOR, because the prompts described
  the machine and never named it. All fifteen came back correctly titled.
* **Ask for no tile-grid panel.** Every grid ever drawn in this repo failed to
  line up with the building on it. The prompts asked for a plain top-down view
  instead, and the footprint is measured on the real plate with
  `check-footprint.py`.
* **Ask for a silhouette panel.** It is the cheapest possible map-zoom check and
  it decided at least two of the three picks.

**And one prompt mistake, measured:** all fifteen sheets came back under vanilla's
saturation floor of 0.230, the worst at 0.136, because each prompt confined
copper to one place (*"the drive end only"*, *"the coil itself"*). The adopted
Array prompt says copper is "VISIBLE and used freely on bus runs, joints and
fittings" and measures 0.262. Let the copper out.

**Two art-direction corrections drove this, both from Liam.**

*Both hatches in the same square.* The Drop Crusher's two chutes sat side by side
inside one tile, so they read as one output and there was nowhere to put a second
belt. Now rule 3 in the template, and it also applied to the Dross Classifier and
the Coil Separator.

*Everything looks the same instead of unique.* The cause was the format example
doing more than layout — the Ballast Drill came back with **identical palette
swatch values** to the Drop Crusher. Two changes: every building now gets its own
**distinct vanilla style reference**, none repeated across the nine, and the
format example **rotates** through the older approved sheets rather than being one
sheet for everything. The prompt also now says in terms that the second image is a
layout reference only, that the machine in it is a different building, and that
this one must look like nothing else.

**The uniqueness fix is not yet proven.** It has only been through the Drop
Crusher, which was always going to look like itself. The first real test is the
next building drawn against a reference it has not seen.

### The reference plan, so it is not re-derived

| Building | Vanilla style reference | Format example |
| -------- | ----------------------- | -------------- |
| Drop Crusher | assembling machine 3 | **none — see the warning below** |
| Ballast Drill | big mining drill | sealed roboport v2 |
| Dross Classifier | centrifuge | bed tender v2 |
| Coil Separator | nuclear reactor | superconducting store v1 |
| Whisker Comber | recycler | sealed roboport v2 |
| Helium Concentrator | chemical plant | vent pump v4 |
| Vacuum Furnace | cryogenic plant | **ignition array `concept/adopted/R-sheet.png`** — the v2 sheet this row used to name is a rejected design carrying a generator-added wordmark |
| Crust Tap | pumpjack | arc mast v4 |
| Ignition Ring Mast | our own ignition array | radiant generator v1 |

**The format example is the most dangerous attachment on the list.** On the Drop
Crusher's five-option round one generation came back as the *Ignition Array* —
the building in the attached format sheet — purple glow, charge sequence and all,
on a machine whose spec says nothing is hot. The prompt already said the sheet
was "a FORMAT reference only… the machine in it is a different building of ours",
and that was not enough. Until a machine-free crop of the panel furniture exists,
attach the format example only when the subject is plainly unlike it, and check
the output against the prompt's own title line before believing it.

**One thing to settle across all nine at lock time.** Every sheet titles itself
with a generic descriptive name — ORE PRESS, VIBRATING CLASSIFIER, MAGNETIC
SEPARATOR, GAS SEPARATOR, INDUSTRIAL FURNACE, INDUSTRIAL WELLHEAD, CHARGING POST
— because the prompts describe the machine rather than naming it. Harmless on a
reference sheet, but it means no sheet carries the name the mod actually uses.

**What made this work, and it is worth keeping.** Two attachments per generation:
a cropped and upscaled frame of a real vanilla building for camera and finish,
and an already-approved sheet of our own for format. The second one did the heavy
lifting — from the Drop Crusher onward, every sheet arrived with the right panel
set, information tables, layer-breakdown row, tile grid and swatch panel without
any of it being described in words. Appendix B says this; it is now measured.

**Every gameplay number in the nine specs is still a placeholder**, and none has
been read back off a prototype, because no prototype exists.

**One cross-cutting art item, from S13.** Nothing in this mod uses
`status_colors` with `apply_tint = "status"`, and every machine in it can stall
for a reason the player cannot see. Each of the nine should carry a small white
**fault lamp** lens — drawn once at 32 px, `draw_as_glow`, tinted by the engine,
and placed away from whatever the building's working glow is so the two are never
confused. It is the cheapest legibility win in the set, and it costs one sprite
per building rather than a concept round.

For each: canonical view, idle plate, directional frames where the prototype has
them, glow by differencing, sprite canvas, icon. Template Appendix C is the
pipeline and none of it should be asked of a generator.

**This is the part that is left, and it needs a browser.** Every building's spec
now names its slots, layers, files and prototype wiring, so the remaining work is
two generations per building — an unlit canonical plate and its lit twin — and
then mechanical processing:

```
tools/process-building-art.py <plate> --report          # measure first, always
tools/process-building-art.py <plate> --out-dir ... --name ... --width ... --height ...
tools/derive-glow.py --lit <lit> --unlit <unlit>        # the glow, by subtraction
tools/build-glow-frames.py --glow <plate>               # animation, by mask
tools/key-icons.py graphics/icons <plate>:<name>        # the icon
```

Order worth taking them in, cheapest first, because each one teaches the next:

1. ~~**Bed Tender**~~ — **done.** Two generation rounds: one to take the arm off
   and one to fix the camera. `base.png` 224×189 with 192 px (3.00 tiles) of
   visible content, `base-shadow.png` 363×189, `bin.png` for the collection
   bin's contents, icon derived from the plate. Three in a row overlap by 90 px
   at alpha > 1 and **0 px above alpha 80**. Still open: the in-client pass with
   the inherited crane actually turning, which is the only way to know the arm
   lands on the drawn bearing.
2. **Superconducting Store** — 2×2, one direction, one glow, exercises the
   travelling-mask animation path.
3. **Sealed Roboport** — 4×4, one direction, but the iris is a mask job and the
   dock offsets have to be verified on the cut plate.
4. **Radiant Generator** — two directions, so two of everything, and neither may
   be a rotation of the other.
5. ~~**Ignition Array**~~ — **done**, and it cost the most, because the design
   was replaced rather than refined halfway through: a v3 deck was cut, irised,
   shafted and glowed before twenty concepts across four sets replaced it with
   the Suspended Core. §6.1 still did its job — the shipped building is three
   plates and three discharge plates, not sixteen silo slots.

**Fill §13 from the plate as you go.** It is left open in every spec on purpose;
the Arc Mast's §13 records what guessing those numbers cost.

### Check §8 before drawing anything

Every building now carries a **§8 Connections** section giving the exact tile
coordinates the engine will draw connectors at. A concept sheet was approved
against §3 and §17 and *not* against §8, and the Vent Pump cost three extra
rounds for it. Two rules came out of that review:

* **Pipes only join in straight lines.** A connection has a tile and a facing,
  and the pipe meeting it runs axis-aligned out of that tile's edge. There are no
  diagonal hookups. A connection on a corner *tile* is still not diagonal — it
  faces straight out through an edge.
* **Vanilla puts the connector in the building's own art**, not in a generic
  engine-drawn stub. The foundry is the pattern: `pipe_picture =
  util.empty_sprite()`, `always_draw_covers = false`, and the flange revealed as
  a named `enable_working_visualisations` layer.

**All three conflicts the review found are fixed.** Two in the prototype, one in
the art; each is recorded in the building's own §8.

* **Sealed Roboport** — redrawn. Four recessed charging docks at the
  `charging_offsets`, and a central iris over the axis where `stationing_offset`
  puts robots. `concept/v2-sheet.png`. The building came out better for it: two
  routes that mean different things, robots through the roof, materials through
  the wall hatch.
* **Superconducting Store** — `charge_animation` and `discharge_animation`
  cleared, so vanilla's box-shaped glow cannot land on the cryostat drum. The
  five ring states of §9 replace them when the plate lands.
* **Bed Tender** — `crane.origin` moved to `{0, 0, 4.6}`, so the inherited arm
  pivots on the bearing the art draws.

- [x] **Fill the briefs out into specs.** Done for all four —
      `bed-tender`, `radiant-generator`, `sealed-roboport`,
      `superconducting-store` — and renamed to `building-spec-*.md`. Each now
      carries §6 sprite slots, §7 layer structure, §12 processing, §14 files,
      §15 prototype wiring, §17 QA and §18 checklist.
      **§13 Sprite Dimensions is deliberately left open** in every one: those
      numbers are *measured off the approved canonical plate*, as the Arc Mast's
      §13 records at length, and guessing them is what cost that building three
      rounds. Each §13 states the load-bearing constraint that *is* known in
      advance — the exact tile span the deck must occupy — and nothing else.
- [ ] **Bed Tender's crane is a separate prototype.** `agricultural-tower` points
      at `agricultural-tower-crane`, which defines the arm, joints, grip and
      their animations in its own right. It is not part of `graphics_set` and
      cannot be replaced by editing the building plate. Ship the hub first; the
      arm stays inherited and visibly mismatched until its own pass.
- [x] **Ignition Array's rocket** — done. `sae-ignition-discharge` is vanilla's
      rocket with its sprite, shadow, flame, glare and five smoke plumes emptied
      and its explosion removed, and `rocket_sprite` re-pointed at `column.png`:
      a column of light leaving, not a vehicle. Confirmed on a headless server —
      the launch runs and the ignition fires.
- [x] Cosmetic: the Ignition Array v2 sheet's unasked-for *Factorio Space Age*
      wordmark — **closed by the redesign.** `concept/v2-sheet.png` is a rejected
      sheet now and no shipped asset was ever cut from it. The rule it produced
      stands: never carry a generator's wordmark into a plate.

## 6. Two mismatches with no art plan at all — both now fixed

- [x] The **whisker plant rendered as a Gleba tree**. Replaced with four kamacite
      whisker clusters; the engine dump shows **zero references to
      `planted-tree` left**. It also grows: the `trunk == leaves + 1` frame rule
      turned out to exist *for* growth, so frame 0 is the clump at 62%.
- [x] The **whisker bed tile was a clone of stone path**. Recoloured from
      vanilla's own sheets so the tiling contract survives, measured at
      luminance 60 against the Core's basalt at 22.

## 7. What a session should run before believing anything

`./tools/check-data-stage.sh` now runs four checks, and the third is new and the
one that matters:

```
Data stage OK        -- the mod loads
Graphics OK          -- 67 paths written as whole string literals
Dumped graphics OK   -- 375 paths as the ENGINE resolved them, 115 of them ours
Recipes OK           -- every recipe fits a machine that can hold its fluids
```

The gap between 67 and 375 is the point. `check-graphics.sh` reads Lua source and
cannot see a path that was built rather than written, and this mod builds nearly
all of them. It reported "all 52 files exist" for months while checking **not one
building plate**.

---

## Two rules that cost the most to learn

Both are recorded at length in `building-spec-template.md` Appendix C,
`icon-sheet-prompts.md` and `planet-brief-the-core.md`, and both were re-proven
this session:

**Once a design is locked, stop prompting — edit the approved image.** A
generator asked to draw the same thing again re-interprets it every time.

**Judge by measurement, never by looking.** Downsample icons to 16 px; measure
plates and planet renders against the band you decided on beforehand. Eyeballing
produced two confident, completely wrong findings this session, and one
over-correction that had to be reverted — after the measurement had already been
done correctly. Check drift against the acceptable band, not against the
previous round.
