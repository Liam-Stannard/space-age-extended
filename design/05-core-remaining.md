# The Core — what is left to finish

State as of 2026-09-09. This is the working list for taking the Core from "loads
and plays" to "finished", ordered by what blocks what.

**Updated 2026-09-09 after a balance pass on the opening hours.** The Core did
not play at all before it: the technology tree contained a hard deadlock that
made every building on the planet unreachable. §5 records what that was and what
else the same analysis turned up.

Everything here was checked against the engine's own data-raw dump rather than
against the source, because most of this mod's asset paths are built by Lua
rather than written out — see `tools/check-dumped-graphics.py`.

**Where things stand.** 24 technologies, 52 items, 10 fluids, 64 recipes and
sixteen buildings, of which five still wear borrowed art. The mod loads clean:
data stage, graphics, resolved-path and recipe checks all pass, and the tree is
now walked by a reachability check as well — see §5.

---

## 1. Blocking — the line is not real yet

### 1.1 Four capstone products are one-ingredient stubs

`sae-magnetar-alloy-stub`, `sae-cultured-alloy-stub`, `sae-bio-polymer-stub` and
`sae-cryoprotectant-stub` each turn **one iron plate** into a capstone product.
They exist so the Core's line loads and can be playtested; they are not gameplay.

Only Fulgora ↔ Aquilo is real, and it is the model to follow: cryogen →
fluorinated holmium → superconducting winding, three technologies, a recovered
fluid loop, and every step needing something the other planet has.

| Tree | Capstone | State |
| ---- | -------- | ----- |
| Fulgora ↔ Aquilo | Superconducting winding | **real** — 3 techs, 4 recipes |
| Vulcanus ↔ Fulgora | Magnetar alloy | stub |
| Vulcanus ↔ Gleba | Cultured alloy | stub |
| Fulgora ↔ Gleba | Bio-polymer | stub |
| Gleba ↔ Aquilo | Cryoprotectant | stub |

**This is the single largest piece of work left in the mod**, and it is four
trees, not one. Until it lands, four fifths of the endgame's demand on the rest
of the solar system is fictional.

### 1.2 The production line is too short

Design §5 promises the mod's largest chain. Measured, the Core's own line is
currently **three stages deep** from local resource to Field Coil Segment, which
is shorter than Gleba's. `design/06-core-production-tree.md` is the draft that
fixes this; implementing it is a large job in its own right and it depends on
1.1 landing first, because several new intermediates consume capstones.

### 1.3 Metal carbonyl does not exist

Design §5 describes it — metal that travels through pipes, built from imported
carbon, giving the corridor a permanent cargo unrelated to the capstones. There
is no prototype, no recipe and no technology. It is the most interesting
chemistry available to the Core and it is entirely unbuilt.

---

## 2. Art

### 2.1 Vent Pump — not started

**Three buildings still wear borrowed sprites**, plus the crust vent tile: the
Ballast Drill, the Ring Mast and the Crust Turbine. The Drop Crusher and the Vent
Pump both came off this list on 2026-09-10.

**The data stage now says so itself, and it did not before.** `placeholder_art`
logged the moment it was called — which is before a building's own plates are
attached — so five buildings that had shipped art were still announcing
themselves as placeholders at every load, and the Vent Pump, which never called
it, was announcing nothing at all. It records intent now, `own_graphics` strikes
a name off, and `derive.log_placeholders()` reports the survivors at the end of
data.lua. The count is checkable rather than a thing to measure by hand.

**The Vent Pump is done** — four directional plates, four shadows and a
sixteen-frame working glow, all four directions, cut from one rotation strip with
every shift measured rather than chosen.

Two things its spec had wrong turned up on the way. It claimed the working layer
needed **one** direction "because the sight port and flow disc sit on the stack,
which does not rotate" — the port is on the *riser*, which is the fluid box and
therefore the one part that must turn. And §6.2 asked for a **steam** layer on a
planet whose own §5 says there is no air. Both corrected.

Of the three that remain, the **Ring Mast** and the **Ballast Drill** have no
design chosen and need a five-option round each. The **Crust Turbine** has no
spec section of its own — it lives inside the Crust Tap brief as "a companion
generator" — so its brief has to be written before options can be drawn. The
**crust vent tile** is the odd one out: three sheets at 1x/2x/4x with sixteen
variants each, plus five transition groups and their masks, all of which must
tile seamlessly. `tools/build-whisker-bed-tile.py` and the whisker bed are the
precedent.

Its spec has already solved the hard part and this should be followed exactly:
the four directions are the *same machine from the same camera* with only the
plumbing rotated a quarter turn. §5 is explicit — **do not ask for four
viewpoints**, ask for four arrangements, or the generator returns a turntable
that cannot be used. The locked `v4-sheet.png` already draws all four correctly.

The riser's molten sight port is an orange glow, so `split-glow.py` recovers it
from a lit plate in one generation rather than two.

### 2.2 Ignition Array — deck only

Shipped: the deck, the cradle ring, the closed iris, the shadow, the icon, and
every launch-pad slot emptied. Outstanding, all from spec §6.1:

- iris halves as `door_back_sprite` / `door_front_sprite`
- the shaft under the iris (`hole_sprite`) and the violet light rising from it
- the amber cradle lamps
- the 64-frame crafting glow, derived not drawn
- **the replacement rocket entity** — a `sae-ignition-column` that is a column of
  light rising out of the shaft rather than a vehicle. Until this exists the
  engine still spawns a rocket on a world whose entire premise is that nothing
  leaves. This is the most contradictory frame in the mod and it is still there.

### 2.3 Bed Tender crane — movement, not material

The parts are ours now, but the **joint layout and animation are still vanilla's**,
so the arm folds like an agricultural tower's. Changing that needs the crane
prototype's `relative_position` / `static_length` geometry reworked, which is a
gameplay-shaped job rather than an art one.

Shadows are also still vanilla's silhouettes. They pass at this size; worth a
look in a client before deciding.

### 2.4 Arc Mast — two small defects, another session's files

- `graphics/icons/arc-mast.png` is a bare 64×64, the only icon in the mod that is
  not a 120×64 mipmap strip.
- `graphics/entity/arc-mast/base.png` has alpha 255 along its bottom row — it was
  cut before `--bottom-margin` existed, so it ends on a razor line with no
  antialiased rim. One command to recut.

### 2.5 Nothing has been verified in a client

Every measurement in this pass is a local one. The pipeline is blunt about the
limit: the arc mast passed every local check and still shipped four geometry
defects, all found by pulling frames out of a screen capture. Outstanding:

- the store's ring lit at rest, and the charge sweep travelling round it
- the bed tender's arm sitting on its drawn bearing after `crane.origin` z 4.6 → 2.75
- the roboport on its 4×4, and whether the emptied iris reads as sealed or as missing
- the radiant generator in both orientations, and whether N/S at luminance 61
  reads too dark against the Core's own dark basalt
- the whisker farm: bed tile, four cluster variants, and growth
- the ignition array at 9×9

---

## 3. Gameplay not yet built

### 3.1 The vent-pump coupling is unverified

Design §2 flags it: no vanilla prototype has both `minable.required_fluid` and an
output fluid box at once. The Core's central siting problem — helium throttling
melt — rests on that working. Spike it before depending on it further.

### 3.2 The melt's metal-or-steam split — partly addressed

Two settling recipes exist and differ correctly (60 melt + 150 steam against 25
melt + 900 steam). This used to read "nothing yet forces the choice to hurt,
because power demand on the Core is low", and it blamed the wrong side of the
ledger. **Demand was never the binding constraint; supply that cost nothing
was.** An arc mast produced 6.9 MW on average, for free, for ever — against
+2.96 MW net from a quenched vessel that consumes melt, helium and the metal the
melt would have become. Nobody was ever going to take that trade.

Two changes since:

- **Mast efficiency 0.35 → 0.12**, putting a mast at 2.36 MW. The order is now
  crust turbine 1.80 < mast 2.36 < quenched settling 2.96, so the melt route is
  the best sustained power on the planet again and the split is a decision. The
  4000 MJ burst is untouched, because the burst is the character.
- **A third claimant on the steam.** The valve processor
  (`04-the-core.md` §11) takes 100 steam at 500 °C as a bake-out, so electronics
  now compete with electricity for the same byproduct.

Still open: the radiant generator is 10 MW on free corridor asteroid fuel and
works on the Core (`pressure ≤ 9`). It is the same shape of leak the mast was,
arriving later. Restricting it to gravity 0 would keep its stated purpose — the
corridor's own power, made where it is spent — and close the surface bypass.

### 3.3 The sixth tree is 24 technologies, but shallow in places

Five of them are the integration techs, one per capstone, and four of those gate
recipes whose inputs are stubs. Their real cost cannot be judged until 1.1 lands.

### 3.4 Geodynamic science is untuned

Design §6 says to start it deliberately expensive and tune down, because a cheap
pack collapses the endgame into a segment grind. It has never been played against
a real line, so the most important number in the tree is still a guess.

---

## 4. Suggested order

1. **Vent Pump art** — finishes the buildings, and it is one generation.
2. **Ignition column** — removes the rocket, the mod's worst contradiction.
3. **The four capstone chains** — the biggest job, and everything downstream
   assumes it.
4. **The long production tree** (`06-core-production-tree.md`) — needs 3.
5. **Metal carbonyl** — best done with 4, since it feeds it.
6. **A full client playtest**, then tune geodynamic science against it.
7. The remaining Ignition Array art, and the crane's movement.

---

## 5. The balance pass of 2026-09-09

### 5.1 What was wrong

The tree was walked mechanically: for every technology, with only its transitive
prerequisites researched, can each recipe it unlocks actually be crafted — every
ingredient obtainable, and a machine of its category buildable? The check found
**thirty failures, and one of them was fatal.**

**Kamacite plate could not be made at all**, and it is an ingredient in twenty
recipes:

```
sae-drop-crusher      cost 40 kamacite plate
  └─ only machine with category sae-crushing
       └─ sae-crushing is the only source of crushed kamacite and fines
            └─ which are the only two routes to a kamacite plate
```

Nothing else in the game makes kamacite plate, so it could not be imported
either. Every one of the Core's technologies unlocked recipes that were
unreachable. The mod loaded, passed every check in the repo, and could not be
played past the landing pad.

It was introduced by a change that was right in itself — re-sourcing plate onto
crushed kamacite so beneficiation could not be skipped — which nobody followed
through to the crusher's own price.

### 5.2 What changed

| | Fix |
|---|---|
| **The deadlock** | Drop Crusher priced in steel rather than kamacite plate. The rule now: **on the critical path to the first plate, it comes out of the corridor** — crusher, drill, vent pump, crust tap, crust turbine |
| **Welded plate** | Off the Ballast Drill, Vacuum Furnace, Helium Concentrator and Arc Mast. It needs whiskers, so it arrived three technologies after those unlocked — which left the Vacuum Furnace unbuildable through exactly the stretch it exists to cover |
| **Landing-day power** | Crust tap and turbine priced in steel, so `sae-crust-tapping` is reachable when its own prerequisites say it is |
| **Six prerequisites** | `sae-integration-conductor` ← gravity settling *and* `sae-fa-superconducting-winding`; `sae-sealed-roboports` ← field coils; `sae-ignition-array` ← arc masts; the Field Coil Segment moved to unlock with the Array it is crafted inside; `sae-cryogen-recovery` moved one technology later, to sit with the thing that makes spent cryogen |
| **Power** | Arc mast efficiency 0.35 → 0.12 — see §3.2 |
| **The Ballast Drill** | Was strictly worse than an imported big mining drill on every axis. Kamacite now carries its own `resource-category`, so nothing but the Ballast Drill works it; speed 1.3 → 3.0 and 900 → 600 kW |
| **The lift and the circuits** | Four new recipes and two technologies — `04-the-core.md` §11 |

The check is now `tools/check-tech-reachability.py`, run by
`check-data-stage.sh` alongside the others. It is the only check in the repo
that can see this class of fault: the data stage proves the mod loads,
`check-dumped-graphics.py` proves every asset resolves, and neither has any
opinion about whether the game can be played.

### 5.3 What testing the checker found

A check that has never failed proves nothing, so the deadlock was reintroduced
deliberately to watch the new tool catch it. **It did not.** The tool was right
and the mod was wrong in a second way: kamacite plate really was obtainable, via
`advanced-circuit-recycling`.

`__recycler__` walks every recipe in the game and generates `<product>-recycling`
by inverting it. When two recipes make the same product, whichever the iteration
reaches last silently becomes the recycling result **for everyone**. The Core's
four alternates had therefore rewritten vanilla's own:

| Recycling recipe | Was returning | Should return |
| --- | --- | --- |
| `advanced-circuit-recycling` | emitter array, kamacite plate | electronic circuit, plastic, copper cable |
| `processing-unit-recycling` | emitter array, welded plate | electronic circuit, advanced circuit |
| `low-density-structure-recycling` | whisker tow | steel, copper, plastic |
| `rocket-fuel-recycling` | kamacite plate | solid fuel |

So recycling an advanced circuit on Fulgora returned kamacite — the Core's
exclusive metal, in every scrap line in the game, on every planet. Nothing in
the repo could have caught that except a check that asks what is obtainable.

The fix is `auto_recycle = false`, which is the opt-out the generator actually
reads; Space Age sets it on 73 of its own recipes. **`allow_decomposition` is
not it** — the recycler sets that flag on the recipes it *creates* and never
reads it on the ones it consumes, so setting it looks right, changes nothing,
and the dump still shows the damage. Any future alternate route to a vanilla
item needs the same line.

### 5.4 Still open from the same pass

- **The radiant generator is free power on the Core** — §3.2.
- **The mast's buffer no longer means what it says.** `buffer_capacity` is
  4000 MJ, sized to hold one strike; at 0.12 a strike banks 480 MJ, so it now
  holds eight. Harmless, and arguably good — the mast rides out the 90-second
  gaps itself — but it makes the Superconducting Store less necessary than the
  design intends. Drop it to ~500 MJ if the store should stay load-bearing.
- **The four capstone stubs still make every integration technology's real cost
  unknowable** (§1.1), and the other four integrations will each need the
  cross-tree prerequisite the conductor just got.

