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
| Ignition Array | `building-spec-ignition-array.md` | `v2-sheet.png` | **base plate done**, wired, launch furniture emptied; iris / shaft / lamps / 64-frame glow / rocket entity outstanding |
| Vent Pump | `building-spec-vent-pump.md` | `v4-sheet.png` | **all outstanding** — 4 directional frames plus an animation, the most expensive of the seven |

## 5b. Nine briefs, no sheets, nothing generated

Drafted 2026-09-06 from the Core production-chain review. Each is a **brief** in
the sense §5's four brief-first specs began as: enough to commission and judge a
concept sheet, with §6, §12 and §13 deliberately open. **None is at stage 0 yet**,
and three carry a question that has to be answered before art is worth
commissioning — the last column says which.

| Building | Document | Blocked on |
| -------- | -------- | ---------- |
| Drop Crusher | `building-spec-drop-crusher.md` | nothing — **start here**; vanilla's crusher is space-only, so T1 cannot exist without it |
| Ballast Drill | `building-spec-ballast-drill.md` | nothing |
| Dross Classifier | `building-spec-dross-classifier.md` | nothing |
| Coil Separator | `building-spec-coil-separator.md` | nothing |
| Whisker Comber | `building-spec-whisker-comber.md` | its two consumers (T5 prepreg, T6 cryostat) do not exist |
| Helium Concentrator | `building-spec-helium-concentrator.md` | **§20** — it turns helium from a hard cap into a price, which rewrites `decisions.md` D12 |
| Vacuum Furnace | `building-spec-vacuum-furnace.md` | **§20** — the sintering recipe's shape decides whether it can be a `furnace` at all |
| Crust Tap | `building-spec-crust-tap.md` | **spiked (S10)** — both halves work, but the pump needs a fluid-bearing tile, so the tap is now **sited**: it also needs a tile prototype, a map-gen entry and tile art |
| Ignition Ring Mast | `building-spec-ignition-ring-mast.md` | **clear** — mechanic agreed, and spike S11 passed: spoilage ticks in the silo, charges vanish cleanly, nothing rots mid-craft |

Every one of the nine is a **first draft**: gameplay numbers are placeholders,
and none has been read back off a prototype, because no prototype exists.

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
5. **Ignition Array** — largest surface, and §6.1 scopes it down before starting.

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
- [ ] **Ignition Array's rocket is a real problem** and §6.1 of its spec scopes
      it: the engine spawns a `rocket-silo-rocket` and plays a launch sequence on
      a world where the whole point is that nothing leaves. The fix is a custom
      `sae-ignition-column` entity — a column of light rising out of the shaft,
      not a vehicle. Separate asset, after the building.
- [ ] Cosmetic: the Ignition Array v2 sheet carries a *Factorio Space Age*
      wordmark the generator added unasked. Harmless on an internal document;
      remove it before the sheet is shown anywhere outside the repo, and never
      carry it into a plate.

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
