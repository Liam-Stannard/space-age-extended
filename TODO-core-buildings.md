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

- [x] **B4 · The Ignition Array had no animations — DONE.** It inherited nothing
      but suppressed slots after B3, so it crafted and fired without a single
      thing moving. Built and verified in-engine:

      **The iris.** A rocket-silo's deck is a *ring* — vanilla's own
      `06-rocket-silo.png` has a hole through the middle, `hole_sprite` draws the
      shaft inside it, and the doors sit over the hole. Our plate had the closed
      iris painted on, so the doors would have parted to reveal a second iris
      underneath. `tools/cut-array-iris.py` now lifts the blades out of the
      approved plate — fitted at centre (302, 276), semi-axes 100 × 88, 93% of
      sampled rim points dark, bolts found at r = 88 by a brightness sweep, so the
      cut is at 83 × 73 and the collar stays on the deck. Closed, the two leaves
      are the plate again pixel for pixel. `tools/build-array-shaft.py` draws the
      shaft and its light on the same ellipse. Rendered: the iris parts on the
      NW-SE seam, along two cable trunks, and opens over 255 ticks.

      **The assembly glow.** `tools/build-array-glow.py` finds the four cable
      trunks in the plate by their copper and pulses violet inward along them,
      with the iris seams breathing in time. Derived from one plate, so no lit
      twin had to be generated and nothing can drift. Budget measured against
      vanilla rather than guessed: the silo's own crafting sheet is 2.9 Mpx, the
      full plate at 64 frames would be 23 Mpx, so it is drawn at half resolution
      and shipped at `scale = 1.0` — identical on screen, a quarter of the pixels
      — at 32 frames, landing on 3.29 Mpx.

      **The launch.** `tools/build-array-column.py` draws the discharge as a
      column of violet-white light: `rocket_sprite`, its glare, an 8-frame
      flicker at its foot, and the deck lit additively from its own shaft. Two
      inherited numbers were wrong and were found by rendering, not reasoning —
      `rocket_initial_offset` put the column eleven tiles south of the deck as a
      smear on the ground, and `rocket_visible_distance_from_center` at 0 left the
      parked discharge standing lit in the open shaft forever.

      **A screenshot rig, which is how any of this was checked.** The headless
      server cannot render — `take_screenshot` returns cleanly and writes nothing
      — so the graphical binary runs under xvfb with a `steam_appid.txt` to stop
      Steam relaunching it, a scratch mod driving the launch, and a watchdog that
      kills it on its own DONE line so it releases the write-data lock. Every
      number above came off a render.

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

### Raised by the Array animation work, for Liam to decide

1. ~~**The Array never fires by itself.**~~ **Resolved 2026-09-08 — the win
   condition is reachable and nothing needs changing.** Liam opened a loaded
   Array in a real game: the silo GUI carries a **Launch** button, disabled with
   *"Rocket is not ready"* until progress reaches 100%. So
   `launch_to_space_platforms = false` removes the *destination*, not the
   player's ability to fire, and the mod is completable as built.

   Worth recording how badly I mis-scoped this. I flagged it three times as
   possibly making the mod uncompletable, on the strength of a true observation —
   it never auto-launches — plus an assumption I never tested, that no button
   would appear without a destination. Two rendering routes failed to settle it
   (`take_screenshot` does not capture entity GUIs; `xwd` on the GL surface
   returns black) and a screenshot from the actual game answered it in one.
   **When a question is about what a player sees, the cheapest instrument is a
   player.**

   The same screenshot incidentally confirmed two things: the locale landed
   ("Ignition array", "Field coil segment"), and the ring mechanic is live —
   eleven ignition charges in the ingredient row.
2. **Does the Array's camera need to match the rocket silo's?** Photographed side
   by side in-engine: the silo's shaft mouth is 1.485 wide-to-tall, ours is
   1.127, so ours is about 30% too round, and where the silo shows its far inner
   wall ours shows a lid. This is template rule zero working as written — "mostly
   roof" — not a defect, but a vanilla silo has no surface conditions and can be
   built on the Core, so a player can see them together.
   `graphics/building-spec-ignition-array-v2.md` is a complete alternative spec
   at the silo's camera. **Nothing is adopted.** Taking it costs a re-plate plus
   the icon; the four tools rebuild every other asset from it.
3. **`hole_light_sprite` was never observed drawing.** Wired, file present, and
   across two full rendered launches no light from it appeared at any phase. The
   ignition read currently rests on `rocket_glow_overlay_sprite` and the column.
4. **Cumulative cradle lamps: answered, and they are possible.** Not through the
   prototype — `red_lights_back_sprites` is a blink cycle driven by
   `light_blinking_speed` and `times_to_blink`, not a counter, and 2.1.17's
   `LuaEntity` has no `disabled_working_visualisations`, so named working
   visualisations cannot be switched per entity from script either. Both were
   probed on a live 2.1.17 server rather than inferred.

   The route that does work is `control.lua` plus `LuaRendering`.
   `rendering.draw_sprite`, `draw_animation` and `draw_light` all exist, a drawn
   object's `intensity` is settable after creation (so a charge can ramp rather
   than step), and the charge level is readable straight off the entity as
   `(rocket_parts + crafting_progress) / prototype.rocket_parts_required` — a
   smooth 0–1 across the whole build, not one step per part.

5. **The doors are cosmetic.** `door_back_sprite` and `door_front_sprite` are
   optional: a silo with both nil loads, and on a headless 2.1.17 server one ran
   the entire launch sequence in lockstep with a vanilla silo beside it —
   identical states on identical ticks, both rockets away. The door phases
   (`doors_opening`, `doors_opened`, `doors_closing`) still elapse; nothing
   stalls. So a charging animation can replace the doors outright rather than
   sitting alongside them.

### The Ignition Array — settled

**The Array is the Suspended Core**, chosen from twenty concepts across four sets
and implemented: plates cut, doors and shaft removed, charge drawn from
`control.lua`, and the whole thing exercised on a headless server through charge
and launch to the ending. See `graphics/array-options/` for the decision record
and `tools/build-ignition-array.py` for the plates.

Everything below this line describes **v3, which was rejected**, and is kept only
because its measurements explain why the plate plan exists.

### The Ignition Array's v3 art — superseded, kept for the record

Stage 0 passed: `concept/v3-r2-sheet.png` is the locked design, mouth measured at
**1.48** against vanilla's 1.481. Stage 1 took eight failed re-renders before the
method was found — hand the generator **vanilla's own hole sprite on flat
magenta** and ask it to build the machine around it, in one positive sentence.
Describing a proportion never survived a re-render; handing over the object did.

Two plates are now in hand and measured — `concept/v3-around-hole.png` (the deck
ring, mouth 1.48) and `concept/v3-lid.png` (the closed lid, 1.346). What is left
is assembly, not generation, and the full list with its ordering is in
`graphics/building-spec-ignition-array-v2.md` under **"What is left on the
Ignition Array"**. Nothing about the Array is committed.

## The nine buildings

All in `prototypes/core/machines.lua`, with their items and build recipes beside
them, and their crafting recipes in `recipes.lua`. Art is a **documented
stand-in**: each wears a size-matched vanilla machine's sprites until its plate
exists, marked by a `derive.placeholder_art` call so every one is greppable and
logged at data stage.

- [x] **N1 · Drop Crusher** — `assembling-machine`, 3×3, `sae-crushing`, gravity ≥ 45
- [x] **N2 · Ballast Drill** — `mining-drill`, 5×5, `resource_drain_rate_percent = 50`
- [x] **N3 · Dross Classifier** — `assembling-machine`, 3×3, `sae-classification`
- [x] **N4 · Coil Separator** — `assembling-machine`, 3×3, `sae-separation`
- [x] **N5 · Whisker Comber** — `assembling-machine`, 3×3, `sae-fibre`
- [x] **N6 · Helium Concentrator** — `assembling-machine`, 3×3, `sae-degassing`, 3 fluid boxes
- [x] **N7 · Vacuum Furnace** — `furnace`, 3×3, `smelting` + `sae-sintering`, flux fluid box
- [x] **N8 · Crust Tap** — `offshore-pump`, 2×2, + `sae-crust-gas` fluid + `sae-crust-turbine`
      — in `prototypes/core/crust-tap.lua`. Five prototypes, not one: a fluid, a
      private collision layer, a sited vent tile, the tap and the turbine.
      **Proven end to end on the rig at exactly 1,800,000 W**, the declared
      figure to the watt.
- [x] **N9 · Ignition Ring Mast** — `assembling-machine`, 3×3, fixed recipe, helium fluid box

### Review of the eight, and what it found

Audited against a data dump rather than by reading the Lua, because that is the
only way the last round of these bugs was visible either.

**One real leak, and it was invisible in the source.** The Coil Separator is
copied from the electromagnetic plant for its art, and it silently arrived with
that plant's **+50% base productivity** — `effect_receiver` is inherited and
nothing in the file mentions it. Caught in the dump, fixed in
`prototypes/derive.lua`, which now strips it for every derived prototype.

`derive.lua` is the other output of this stage: it encodes the B3 findings as
code rather than as a memory, clearing inherited `localised_name` (the "Tree"
bug), `factoriopedia_simulation` (the vanilla-machine-on-our-page bug), frozen
art, water reflections, emissions on a planet with no pollutant, and now
`effect_receiver`. Verified clean across all eight.

**Two required re-sourcings, both demanded by a spec rather than chosen.** Plate
smelting now takes crushed kamacite instead of raw ore, or tier one is skippable
and the Drop Crusher is decoration. Whisker beds are laid on bed-grade dross
instead of raw dross, or the Dross Classifier has nothing that needs it.

**The ring mechanic is live.** The Field Coil Segment recipe now takes an
ignition charge, and the charge spoils in ten seconds with no spoil result — so
a mast has to stand within a few seconds of belt of the Array. Nothing in the
engine can require one building to be near another; real belt time does it.

### Review of N8, and what it found

Nothing here was visible from the data stage, which is the whole point of the
building: S10's lesson is that a broken tap reports `working` and yields nothing.
Four bugs, each of which looked correct until measured on the rig.

**The vent tile never generated.** A planet's `autoplace_settings.tile` is a
whitelist, and a tile absent from it is excluded no matter what its own autoplace
says. Sixteen chunks produced exactly zero vents until the tile was listed in
`map-gen.lua`.

**The autoplace threshold had to be measured, not guessed**, and the first four
readings were non-monotonic — 0.72 → 3.9%, 1.05 → 6.8%, 1.18 → 2.99%, 1.27 →
4.13% — because every run generated a *fresh map seed*. Pinning the seed made it
monotonic immediately: 1.10 → 0.90%, 1.18 → 0.46%, 1.24 → 0.13%. Settled at
**1.38 with feature scale 1/40: 1.31% coverage in 6 fields** per 384×384, largest
800 tiles. Vents are a place you travel to, which is what makes power a location
rather than a tuning number.

**`fluid_source_offset = { 0, 0 }` drew nothing.** On a 2×2 that offset lands on
the corner where the four footprint tiles meet. The tap reported `working` with
0.0 fluid — S10's exact silent failure, reproduced by my own first draft. Moved
to `{ 0.5, 0.5 }`, squarely inside one tile.

**An offshore pump does not buffer.** Even correct, it read 0.0 for ever until
something was connected. Piped to a tank it filled at 0.5/tick as declared; the
zero was the test, not the tap.

**The one thing that looked broken was the test, not the tap.**
`tile_buildability_rules` appeared not to bite — a tap could seemingly be built
on bare ground. It cannot. `can_place_entity` *defaults to a lenient check that
ignores tile buildability entirely*; asked the way a player actually builds,
with `build_check_type = manual`, the answer is `vent=true, bare=false`. The two
other check types both return true off-vent, which is why the first reading was
misleading. Anything testing a buildability rule must pass `manual`.

**No item is a dead end any more.** Whisker tow now makes the reinforced frame
(which took raw whiskers before — one tow is eight whiskers, so the frame costs
exactly what it did and the comb becomes a step rather than a refinement),
whisker felt goes into the insulation sleeve it is thermally suited to, and the
sintered preform goes into the Ignition Array itself. Schreibersite was fixed a
stage earlier by phosphide flux.

The preform sits in the **Array's** recipe rather than the segment's, and that is
a constraint rather than a preference: the segment is unlocked by
`sae-field-coils`, which the Coil Separator's build cost sits behind, which the
flux sits behind, which the preform sits behind. A preform in the segment would
ask the player to make one before the research that allows it. Verified: no
dependency cycle, and no technology unlocks a recipe whose ingredients do not
yet exist.

*Superseded — the note below is kept for the record:*

**Three items were dead ends**, knowingly: whisker tow, whisker felt and
schreibersite have no consumer yet. Their consumers — prepreg, the cryostat core
and phosphide flux — are tier 4+ in `design/06-core-production-tree.md` and are
not implemented. They are produced but not yet wanted.

### C3 review of the nine, after C2

Four checks, all against a data dump rather than by reading the Lua.

**Every new prototype was missing its locale — 29 of them.** In game they would
have read `Unknown key: item-name.sae-drop-crusher`. Names and descriptions are
written for all of them. The 60 that still appear "missing" are generated barrel
and recycling recipes, which localise themselves from the names above:
`sae-drop-crusher-recycling` resolves to `["recipe-name.recycling",
["entity-name.sae-drop-crusher"]]`. False positives, checked rather than assumed.

**All eight machines match their specs exactly** — energy, module slots and
crafting categories compared field by field against section 2 of each master
spec. 8/8.

**No recipe asks for more fluid connections than its machine has.** Checked
across every `sae-*` recipe against every machine carrying its category, which
is the failure `check-recipes.py` exists for and the one that fails silently at
runtime rather than at load.

**The spoilage mechanic is wired as designed:** the charge carries 600 ticks and
no spoil result, and the Field Coil Segment recipe genuinely lists it.

## Raised by Liam, not yet done

- [x] **Group the Core's buildings and items together in the crafting menu** —
      done, in `prototypes/core/groups.lua`. Vanilla's own pattern rather than an
      invented one: Space Age gives a planet a *subgroup* inside the existing
      groups, not a group of its own — `vulcanus-processes`, `fulgora-processes`
      and `aquilo-processes` all sit under `intermediate-products` at orders k–p,
      and every planet's machines stay in `production` beside the rest. So the
      Core takes `sae-core-processes` at order **q**, the next letter after
      Aquilo, and `sae-core-machines` at **eb**, straight after
      `production-machine`.

      **52 prototypes re-pointed in one pass** — 35 chain items and 17 machines —
      ordered by the production tree rather than the alphabet, so reading the
      menu top to bottom reads the factory in build order. Ten fluids ordered to
      match. Verified against a dump: no duplicate orders, and the only mod item
      left outside is the geodynamic science pack, which stays with the other
      science packs on purpose.

## Closing out

- [x] **C1 · Recipes, categories and items** for everything above — done. Every
      building has an item, a build recipe and a crafting category, and every
      category now has recipes in it. The last gap was `sae-sintering`, carried
      by the Vacuum Furnace with nothing running in it; the sintered preform
      fills it (`prototypes/core/recipes.lua`), which is half that furnace's
      reason to exist.
- [x] **C2 · Technologies** placing each building on the ladder at its tier — done;
      two new techs, and the whole ladder walked in dependency order to prove every
      recipe is reachable and nothing unlocks before its ingredients exist.
- [x] **C3 · Review each implementation for correctness**, one at a time — done
      after each stage. Found the inherited +50% productivity on the Coil
      Separator, the missing locale for all 29 prototypes, and four N8 bugs.
- [x] **C4 · `tools/check-data-stage.sh` green**, including the recipe and
      graphics checks — passing on 2.1.17: data stage loads clean, all 70
      referenced graphics files exist, 568 dumped references resolve, and every
      mod recipe fits a machine that can hold its fluids.
