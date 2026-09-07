# Core buildings — implementation checklist

Working list for the run that turns the nine drafted Core buildings into real
prototypes, and clears the three defects found alongside them. Tick items off
here as they land; this file is deleted when the list is empty.

## Defects found in existing buildings

- [x] **B1 · Crane arm is corrupt — FIXED.** 10 of the Bed Tender's 29 crane sprites
      have a destroyed alpha channel — max delta 255, more pixels changed than
      were ever opaque, so those segments render as solid blocks instead of a
      shaped arm. Damaged: `crane-1-1`, `crane-1-2`, `crane-3`, `crane-4`,
      `crane-5-1`, `crane-5-2`, `crane-6`, `crane-7-1`, `crane-7-2`, `crane-8`.
      Undamaged: the shadows, the reflections, `crane-9`, `crane-10`.

      **The cause was not the recolour.** `tools/build-crane-sheets.py` had
      deliberately replaced those exact ten parts with bespoke art, stamping one
      canonical vertical drawing into every frame of each rotation sheet. Its
      argument was that vanilla's frames are all the same pose and differ only in
      shading — measured at "at most 26%" on part 5, then generalised to the set.

      That does not hold. Extracting frames 0, 32, 64 and 96 from vanilla's part 3
      shows genuinely different views: different shading, different self-occlusion,
      hoses on different sides, and **frame 64 empty**, because the part is hidden
      at that angle. Ours drew the same strut in all four — so the arm's segments
      never changed as it swung, and a segment appeared at angles where vanilla
      draws nothing.

      Fixed by re-running `tools/recolour-crane.py`, which restores recoloured
      vanilla geometry for all ten. Verified: **0 alpha mismatches** across all 29
      sprites, and part 3's frames 0 and 32 now differ by 23.91 mean where they
      previously differed by 0. This is exactly the case `recolour-crane.py`'s own
      docstring makes — *"an image generator cannot produce 64 consistent angles
      of anything"*.
- [x] **B2 · Sealed roboport's port is too small — FIXED.** Robots emerge wrongly. Two
      **Measured.** Vanilla's door frame is 97 px — a **1.52 tile** opening. The
      aperture drawn on our dome is a connected 46 × 36 px blob: **0.72 × 0.56
      tiles**, which is **47% of vanilla's width and 45% of its area**. A
      construction robot is about half a tile across, so ours is barely wider than
      the robot coming through it.

      **Fixed in the prototype.** Robots were also spawning at vanilla's
      `spawn_and_station_height = 0.3`, tuned to vanilla's low mouth — a third of
      a tile off the ground, *inside* our deck and below the hole. Measured off
      the plate (306 px at scale 0.5, shift −0.09375, so the top edge is 2.48
      tiles up): the iris centre sits **0.94** tiles above the origin and the dome
      crown **1.62**. Set to those, with the render-layer swap moved from 0.87 —
      which was halfway up our dome — to the crown.

      **Art fixed too.** The locked plate was *edited* rather than regenerated,
      per the README rule, and everything but the iris came back unchanged. The
      aperture is now 80 × 69 px — 1.25 × 1.08 tiles, **114% of vanilla's**
      70 × 64. Widening it moved its centre down the dome, so
      `spawn_and_station_height` went 0.94 → **0.75** to follow it. `lamps.png`
      still registers: 2 of its 3,563 lit pixels fall inside the new iris.

      *Correction to the first measurement in this entry:* the "47% of vanilla"
      figure compared our aperture interior against vanilla's **door sprite
      width** (97 px), which was not like-for-like. Measured the same way on both,
      the old aperture was **66%** of vanilla's. Too small either way.
- [ ] **B3 · Audit every derived prototype for inherited leftovers.** The
      Ignition Array is a `rocket-silo` and must not keep silo crafting
      animations, launch furniture or anything else that describes a delivery it
      never makes. Same sweep for the arc mast, vent pump, bed tender, sealed
      roboport, whisker plant, radiant generator and superconducting store.

## The nine buildings

- [ ] **N1 · Drop Crusher** — `assembling-machine`, 3×3, `sae-crushing`, gravity ≥ 45
- [ ] **N2 · Ballast Drill** — `mining-drill`, 5×5, `resource_drain_rate_percent = 50`
- [ ] **N3 · Dross Classifier** — `assembling-machine`, 3×3, `sae-classification`
- [ ] **N4 · Coil Separator** — `assembling-machine`, 3×3, `sae-separation`
- [ ] **N5 · Whisker Comber** — `assembling-machine`, 3×3, `sae-fibre`
- [ ] **N6 · Helium Concentrator** — `assembling-machine`, 3×3, `sae-degassing`, 3 fluid boxes
- [ ] **N7 · Vacuum Furnace** — `furnace`, 3×3, `smelting` + `sae-sintering`, flux fluid box
- [ ] **N8 · Crust Tap** — `offshore-pump`, 2×2, + `sae-crust-gas` fluid + `sae-crust-turbine`
- [ ] **N9 · Ignition Ring Mast** — `assembling-machine`, 3×3, fixed recipe, helium fluid box

## Closing out

- [ ] **C1 · Recipes, categories and items** for everything above
- [ ] **C2 · Technologies** placing each building on the ladder at its tier
- [ ] **C3 · Review each implementation for correctness**, one at a time
- [ ] **C4 · `tools/check-data-stage.sh` green**, including the recipe and
      graphics checks
