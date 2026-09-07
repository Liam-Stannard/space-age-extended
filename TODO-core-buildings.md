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
- [x] **B3 · Audit every derived prototype for inherited leftovers — DONE.**
      Fifteen `table.deepcopy` derivations swept mechanically, not by eye: one
      script listing every field still pointing at a vanilla asset, a second
      listing every field still byte-identical to its source. Both are kept at
      `/tmp/claude-1000/audit/` and are cheap to re-run after any new derivation.

      **Ignition Array** (`rocket-silo`) — the one named in the brief. It still
      carried the six vanilla crafting visualisations: `crafting`,
      `crafting-light`, an `engine` and *two steam plumes*, on a vacuum world
      where nothing burns. Emptying them exposed a second reference —
      `working_sound.sound_accents`, four welder and metal-rotation accents keyed
      by name to frames of the `crafting` animation, which is a hard load error
      once the animation is gone. Also cleared: `robot_door` (a silo roboport
      hatch, with passive-provider-chest sounds), the five Aquilo `*_frozen`
      sprites (an iced rocket silo laid over a machine that is pressure-locked to
      the Core and can never freeze), and the launch-sequence audio —
      `doors_sound`, `clamps_on/off_sound`, `raise_rocket_sound` and both alarms,
      all of them the sound of machinery that is now drawn as nothing.
      `rocket_entity` pointed at `rocket-silo-rocket`, so firing the Array sent a
      Factorio rocket up off the Core; it now has `sae-ignition-discharge`, the
      same rocket with every sprite, flame, glare, shadow and smoke plume emptied
      and its three takeoff roars removed.

      **Sealed roboport** — `frozen_patch` and `water_reflection` were vanilla's
      squat silhouette, wrong shape for a dome and pointless on a world with no
      ice and no water. `open_door_trigger_effect` / `close_door_trigger_effect`
      clunked vanilla's doors open and shut over an iris that is drawn
      permanently closed.

      **Arc mast** — its Factoriopedia preview is a *script*, and inherited it
      built a vanilla `lightning-collector` on screen and struck it with vanilla
      `lightning`. Both names swapped for ours. `water_reflection` dropped, and a
      duplicate assignment of the vanilla collector icon removed. Same preview
      bug on both corridor asteroids, which launched a vanilla
      `small-promethium-asteroid` across their own pages.

      **Whisker plant** — the worst of the sweep, because none of it stops the
      game loading. `localised_name = ["entity-name.tree"]` was inherited, and a
      hardcoded localised name beats the locale file: `strings.cfg` said
      "Kamacite whiskers" and the game said **"Tree"**. Its `order` filed it
      among Nauvis's forest. Its seven random `colors` are foliage variety, so
      the Core's one mineral crop grew pink and cyan whiskers; replaced with
      three neutrals. `agricultural_tower_tint` was Gleba's yellow-green, which
      is what the Bed Tender's crane flashes while handling it.

      **Emissions** — the Bed Tender vented 4 spores/minute (Gleba's tower
      spreading its crop) and the Vent Pump 10 pollution/minute. The Core sets no
      `pollutant_type` at all, so both were tooltip lines about an atmosphere
      that is not there.

      **One real hole, found by the sweep and closed.** Both Core vents were
      `basic-fluid` — the pumpjack's category — and a pumpjack has no surface
      conditions, so a player could land on the Core, drop an ordinary pumpjack
      on a melt vent and draw melt **for free**, walking straight past the
      helium-3 price the Vent Pump exists to charge. The vents now have their own
      `sae-vent` category and the Vent Pump takes only that, which closes it from
      both ends (the Vent Pump also stops being a pumpjack for Nauvis crude).
      Proven on the rig rather than argued: a `pumpjack` built on
      `sae-melt-vent` reports **`no_minable_resources`** with `mining_target =
      nil`, and a `sae-vent-pump` on the same tile reports
      **`missing_required_fluid`** with `mining_target = sae-melt-vent`.

      **Left inherited on purpose:** open/close and working sounds, circuit
      connector sprites, corpses and explosions. Reusing vanilla audio and
      connector art is ordinary modding, not a leftover.

      **Two art questions raised, not decided** — see the note under the nine
      buildings below.

### Raised by the B3 sweep, for Liam to decide

Neither is a leftover to delete — both are art calls, so they are written down
rather than acted on.

1. **The two corridor asteroids are visually identical to each other and to
   vanilla's.** `sae-radiant-asteroid` and `sae-seeded-asteroid` are both
   `small-promethium-asteroid` deepcopies and both still carry its graphics and
   its icon, while their chunks got icons of their own. So a rock that has been
   hit with a seed missile looks exactly like one that has not — and the player's
   whole job out there is to tell them apart.
2. **A seeded rock is promethium but breaks into carbonic chunks.**
   `sae-seeded-chunk` is a `carbonic-asteroid-chunk` copy, so the parent and the
   fragment are made of visibly different material.

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
