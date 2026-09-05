# Art — what is left

State as of 2026-09-05. Written at the end of the session that produced the icon
chain sheets, the six building concept sheets and the planet art, so the next
session does not have to reconstruct it.

**Everything below is uncommitted.** Nothing has been staged or
committed, and the working tree also carries another session's in-flight changes
(`control.lua`, `prototypes/core/planet.lua`, `prototypes/core/storms.lua`,
`design/spikes.md`, `graphics/building-spec-arc-mast.md`,
`graphics/building-spec-template.md`, the arc-mast plates, and four
`tools/*.py`). Stage explicit paths; never `git add -A` here.

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

Every concept sheet is approved. **Only the Arc Mast has gone past stage 0** into
real sprites; the other five stop at "design locked".

| Building | Document | Sheet | Stages 1–6 |
| -------- | -------- | ----- | ---------- |
| Arc Mast | `building-spec-arc-mast.md` | locked | **done** — plates, glow, icon |
| Ignition Array | `building-spec-ignition-array.md` | `v2-sheet.png` | **all outstanding** |
| Vent Pump | `building-spec-vent-pump.md` | `v4-sheet.png` | **all outstanding** |
| Bed Tender | `building-spec-bed-tender.md` | `v2-sheet.png` | **all outstanding** |
| Sealed Roboport | `building-spec-sealed-roboport.md` | `v2-sheet.png` | **all outstanding** |
| Radiant Generator | `building-spec-radiant-generator.md` | `v2-sheet.png` | **all outstanding** |
| Superconducting Store | `building-spec-superconducting-store.md` | `v1-sheet.png` | **all outstanding** |

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

1. **Bed Tender** — no lit state at all, so no glow step. One plate, one shadow.
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

## 6. Two mismatches with no art plan at all

Both are flagged in the README and neither has a brief:

- [ ] The **whisker plant renders as a Gleba tree**, because its prototype copies
      `tree-plant`.
- [ ] The **whisker bed tile is a clone of stone path**, so a farm cannot be told
      apart from a concrete pad. Chain 2's whisker-bed *item* icon is done, but
      the in-world tile is a different asset.

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
