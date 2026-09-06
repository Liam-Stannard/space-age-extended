# The Core — what is left to finish

State as of 2026-09-06, written straight after the art pass that shipped five of
the seven buildings. This is the working list for taking the Core from "loads and
plays" to "finished", ordered by what blocks what.

Everything here was checked against the engine's own data-raw dump rather than
against the source, because most of this mod's asset paths are built by Lua
rather than written out — see `tools/check-dumped-graphics.py`.

**Where things stand.** 19 technologies, 35 items, 6 fluids, 39 recipes, seven
buildings of which five have their own art. The mod loads clean: data stage,
graphics, resolved-path and recipe checks all pass.

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

The last building without its own art, and the most expensive of the seven: four
directional frames **plus** an animation, where every other building needed one
or two plates.

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

### 3.2 The melt's metal-or-steam split has no pressure on it yet

Two settling recipes exist and differ correctly (60 melt + 150 steam against 25
melt + 900 steam). But nothing yet forces the choice to hurt, because power
demand on the Core is low. It becomes the central problem only when the line is
long enough to want the metal and hungry enough to want the steam — i.e. after
§1.2.

### 3.3 The sixth tree is 19 technologies, but shallow in places

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
