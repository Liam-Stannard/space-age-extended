# Factorio Building — Art & Implementation Specification

**Crust Tap.** First draft — a brief, enough to commission and judge a concept
sheet. Not a specification: §6, §12 and §13 stay open until a sheet is approved
and a canonical plate has been measured.

**This brief covers two prototypes**, and that is a design decision rather than
an accident — see §2. The tap raises a fluid; a companion turbine turns it into
power. Vanilla steam cannot be used for the first half, and §20 records why.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | **Both** prototypes approved in one review | not started |
| 1 | Canonical view — tap | portrait 2:3 | Silhouette approved against §3 | blocked on 0 |
| 1b | Canonical view — turbine | landscape | May be derived; see §20 | blocked on 0 |
| 4 | Glow plate — tap | portrait 2:3 | Differenced against the unlit plate | blocked on 1 |
| 6 | Icons | square | Both legible at 32 px | blocked on 1 |

---

# 1. Building Overview

**Building Name:** `Crust Tap`
**Internal Prototype Name:** `sae-crust-tap`

**Building Type:** `offshore-pump`. Chosen for one reason: an offshore pump is
the only prototype in the game that **produces a fluid from nothing**, which is
exactly what drilling into a still-hot planetary interior should do.

**Purpose:** The Core's landing-day power. A tap sunk into the crust raises
superheated `sae-crust-steam`, which a companion turbine turns into a modest,
uncapped-by-weather trickle of electricity.

**Why it matters:** it closes the only genuine hole in the Core's opening hours.
Solar is `0`, nothing burns at pressure 5, the melt line needs helium and
machines the player has not built yet, and arc storms are episodic. Everything
else on this planet requires a factory to already exist. This does not.

**Locale:** *"The planet is still hot underneath. This is how you spend that."* /
*"Not much power, and it will never be much. But it is there the hour you land,
and it does not care whether the sky is doing anything."*

---

# 2. Gameplay Dimensions

## The tap

| | |
| --- | --- |
| Tile footprint | 2×2 |
| Directions | 4 (the outlet faces a different way in each) |
| Output | `sae-crust-steam` at **500 °C**, ~30/s |
| Energy | none — an offshore pump needs no power to run |
| Surface conditions | `gravity` ≥ 45 — the Core's surface alone |
| Placement | anywhere on the Core; **not** tile-restricted |

## The companion turbine

| | |
| --- | --- |
| Prototype | `generator`, `sae-crust-turbine` |
| Fluid box filter | `sae-crust-steam` only |
| Output | ~1.8 MW per turbine |
| Surface conditions | `pressure` ≤ 9 |

**Roughly one turbine per tap, and about 1.8 MW for the pair.** That is deliberate
and it should stay small: a foothold, not a power strategy. A player who tiles
fifty taps should still find the melt-and-steam line the better answer by a wide
margin, or the Core's central tension is undercut by its tutorial.

### Why two prototypes rather than one

Vanilla `steam` has `default_temperature = 15` (`base/prototypes/fluid.lua:42`),
and an offshore pump has no field to set an output temperature — it emits its
fluid at that fluid's default. A tap producing vanilla steam would therefore emit
**cold steam and no power at all**, which is precisely the silent failure that
`day-night-cycle = 0` caused for the arc storms (spike S9). So the mod defines its
own hot fluid, and a filtered turbine to drink it.

### Why it is not a reskin

An offshore pump that is not on water, produces a hot fluid, and is gated to the
heaviest world in the game is not a water pump. More to the point: nothing else in
Space Age gives a planet a **free, sited, permanently modest** power floor. Every
vanilla world's opening power is either burned or shone on.

---

# 3. Visual Design

## 3.1 Design Concept

A wellhead, not a pump. The building is a **capped bore** — a squat armoured
collar clamped over a hole in the crust, with a single insulated riser leaving one
side and heat visibly bleeding from the collar's seams.

**The anti-read is the offshore pump.** Vanilla's is a light open frame standing
in water with a visible impeller, and every part of that is wrong: there is no
water, no impeller, and nothing about this should look light.

## 3.2 Key Visual Features

* An **armoured collar**, low and heavy, clamped to the ground with visible
  ground-anchors — this thing is holding something in.
* A **single insulated riser** leaving one side and turning to horizontal.
* **Seam heat** — a thin line of dull orange in the joint between collar and
  ground, and nowhere else.
* **Scorched ground** in a tight ring around the base.

### Signature Feature

**The seam glow at ground level.** It is the only building in the mod whose light
comes from *underneath* it, and that reads instantly as "this is tapping the
planet rather than running on it".

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Collar and anchors | `#3E3B36` → `#5E584E` | the mass of the building |
| Riser insulation | `#8A8580` | the single pipe |
| Seam heat | `#C8541E` → `#E8A24A` | ground joint only, dull |
| Scorched ground | `#2E2A26` | tight ring at the base |

**Dull orange, not bright.** This is conducted heat through metal, not a flame.
If it reads as fire it contradicts the planet.

---

# 4. Factorio Visual Style

2×2 and very low, so the camera sees almost entirely roof and the ring of
scorched ground. That is the right emphasis: the interesting thing about this
building is where it is, not how tall it is. Style reference to attach: the
**pumpjack**, cropped and upscaled, for the wellhead read. **Do not attach the
offshore pump.**

---

# 5. Building Orientation

* [x] North · [x] East · [x] South · [x] West

**Direction count:** `4`. The riser is the fluid box, and a riser pointing the
wrong way is the fluid box in the wrong place.

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| `sae-crust-steam` out | the riser's tip, per `fluid_source_offset` | must match the art in all four directions |
| Electric | none | the tap draws no power |
| Items | none | no inserter ever touches this building |

`fluid_source_offset` has to be measured off each directional plate, exactly as
the Ballast Drill's `vector_to_place_result` does. A riser drawn on one face and
declared on another is the same class of defect as the arc mast's first
`lightning_strike_offset`.

---

# 11. Generation Requirements

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio Space
Age industrial wellhead, every panel drawn from the game's characteristic
45-degree top-down perspective. The machine is a low squat two-by-two armoured
collar clamped over a bore in dark metallic ground on an airless world. Heavy
ground anchors bolt it down. A single pale insulated pipe rises from one side and
turns horizontal. A thin dull orange line of conducted heat glows in the joint
where the collar meets the ground, and nowhere else on the machine. A tight ring
of scorched near-black ground surrounds the base. Very dark grey-brown armour,
pale grey insulated riser. No water, no impeller, no open frame, no flame, no
smoke, no bright fire. Panels: main view, top-down view, side elevation, a detail
of the collar-to-ground seam and its heat line, and a lit/unlit pair.
```

---

# 15. Factorio Prototype — sketch

```lua
{
  type = "offshore-pump",
  name = "sae-crust-tap",
  pumping_speed = 30,
  fluid_box = { filter = "sae-crust-steam", --[[ ... ]] },
  fluid_source_offset = { --[[ measured per direction; see §8 ]] },
  surface_conditions = { { property = "gravity", min = 45 } }
  -- NOTE: vanilla's offshore pump restricts placement through
  -- `tile_buildability_rules` and `collision_mask` on the entity, not through
  -- any offshore-pump field. Both must be cleared here, or the tap will only
  -- build next to water that does not exist.
}
```

Plus `sae-crust-steam` (`default_temperature = 500`, `max_temperature = 500`) and
`sae-crust-turbine`, a `generator` whose fluid box filters that fluid.

---

# 16. Icon

The collar seen from slightly above with the riser leaving one side and the seam
line beneath it. Must read at 32 px as *"a capped hole with heat under it"*.

---

# 20. Open questions

- **The cheaper alternative, recorded so it is a choice.** A single
  `electric-energy-interface` producing ~1.8 MW would deliver the same gameplay
  in one prototype with no fluid, no turbine and no art for a second building.
  It is rejected here because a power source you cannot see working is not
  Factorio-shaped, and because a piped fluid gives the player something to route.
  If the art budget bites, this is the first thing to fall back to.
- **Turbine art may be derived rather than generated.** `tools/recolour-turbine.py`
  already exists — written for the superseded Quench Turbine — and recolours
  vanilla's steam turbine. Reusing it would make the companion turbine nearly
  free.
- **Placement rules need a real test.** Clearing an offshore pump's
  `tile_buildability_rules` so it builds on open ground is not something vanilla
  does anywhere. It should be proven on the headless rig before art is
  commissioned, in the manner of spike S9 — this is exactly the shape of
  assumption that failed silently there.
- **It must not obsolete the arc masts.** If storms survive I1, a tap that is
  merely *steadier* than a mast will win on convenience. Keeping the tap small and
  strictly capped is what preserves both.
