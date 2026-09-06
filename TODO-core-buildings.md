# Core buildings — implementation checklist

Working list for the run that turns the nine drafted Core buildings into real
prototypes, and clears the three defects found alongside them. Tick items off
here as they land; this file is deleted when the list is empty.

## Defects found in existing buildings

- [ ] **B1 · Crane arm is corrupt.** 10 of the Bed Tender's 29 crane sprites
      have a destroyed alpha channel — max delta 255, more pixels changed than
      were ever opaque, so those segments render as solid blocks instead of a
      shaped arm. Damaged: `crane-1-1`, `crane-1-2`, `crane-3`, `crane-4`,
      `crane-5-1`, `crane-5-2`, `crane-6`, `crane-7-1`, `crane-7-2`, `crane-8`.
      Undamaged: the shadows, the reflections, `crane-2`, `crane-9`, `crane-10`.
      Fix `tools/recolour-crane.py` to preserve alpha, then re-run it.
- [ ] **B2 · Sealed roboport's port is too small.** Robots emerge wrongly. Two
      causes: `spawn_and_station_height` is still vanilla's `0.3`, tuned to
      vanilla's roof, and the iris is drawn closed with
      `door_animation_up`/`down` emptied — so robots come through a shut hatch.
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
