# Factorio Building — Art & Implementation Specification

**Ballast Drill.** First draft — a brief, enough to commission and judge a
concept sheet. Not a specification: §6, §12 and §13 stay open until a sheet is
approved and a canonical plate has been measured.

**The model, signed off 2026-10-29** (T03m, rig-round-8): the plate, chute ports and wet-only hoses of §3 and §8.

Named for what makes it work rather than for where it stands: the Core's own
drill, but "Core Drill" reads as a drill *for* cores, and every other building
here already says Core in its description.

---

# 0. Generation Contract

| # | Asset | Gate before moving on | State |
| - | ----- | --------------------- | ----- |
| 0 | Options and concept | Liam picks | **done: option B, the Ring Press** |
| 1 | Model | `--collide` 0; support audit 0 floating; coverage ≥ 92 % | **signed off 2026-10-29** (T03m, rig-round-8) |
| 2 | Connections | vanilla's pipe joins (no gap) at all 4 connections in all 4 directions, 16/16; nothing of vanilla's pipe or cover overhangs the wall | **16/16** |
| 3 | Animation | the stroke, dust and chute loop as signed off at round 6 | **done** |
| 4 | Wiring | sheets in `graphics/`, four directions, dry and wet | **in progress** (T03b) |
| 5 | Icon | legible at 32 px | done, from the round-7 model; re-render after wiring? |

---

# 1. Building Overview

**Building Name:** `Ballast Drill`
**Internal Prototype Name:** `sae-ballast-drill`

**Building Type:** `mining-drill`, built fresh against vanilla's
`big-mining-drill` as the reference for proportions and for
`resource_drain_rate_percent`.

**Purpose:** Works kamacite ore **without wasting it.** It is the Core's only drill and the only machine that works kamacite at all. It mines a little faster than the big mining drill (3.0 against 2.5), draws twice its power (600 kW), and takes half as much out of the patch for every ore it delivers.

**Why it matters:** kamacite patches *genuinely run out* (`decisions.md` D12) and
nothing else in the mod cares. This is the only building in the game whose
argument is "spend electricity to make a finite thing last", and on a planet
whose central tension is already electricity, that lands the trade in exactly the
right place.

**Locale** (locale/en/strings.cfg), item and building: *"A heavy drill that uses its own weight to mine. Depletes resources at a reduced rate."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 5×5, matching the big mining drill |
| Directions | 4 |
| Resource categories | `sae-kamacite` (the only drill that works kamacite) |
| `mining_speed` | **3.0**, past the big mining drill's 2.5 |
| `resource_drain_rate_percent` | **50** — vanilla precedent: `big-mining-drill.lua:568` |
| Energy | **600 kW**, electric, `secondary-input` |
| Surface conditions | `gravity` ≥ 45 — the Core alone |
| Module slots | 4 |

### Why it is not a reskin

`resource_drain_rate_percent` is the whole building. It is the one mining-drill
field that changes what a patch is *worth* rather than how fast it empties, and
vanilla uses it exactly once. Here it turns ore siting into a decision with a
cost attached, on the one planet where ore is finite by design.

**The gravity condition is the fiction and the balance in one line.** At 50 g the
drill can press down with its own mass instead of hammering, which is why it
wastes less — and it means the building cannot be carried to a world where ore is
effectively infinite and used as a straight upgrade.

---

# 3. Visual Design

## 3.1 Design Concept

A press, not a hammer. The machine's read is **weight brought to bear**: a broad
low chassis with a heavy ballast block riding above the cutting head, and legs
splayed wide enough that it is obviously bracing rather than standing.

**The anti-read is a derrick.** No tower, no headframe, no rotating superstructure.
Everything about this machine is low and wide, because its argument is mass.

**The whole machine stands on one raised cast plate** (Liam, 2026-10-28: *"Add the drill to a slighty raised plate so the pipe connections go into the wall"*; *"The whole structure should sit on top of the plate … no floating walls"*). The plate fills the footprint to its edge, its top at 0.85 tile, above the fittings. Its wall runs unbroken along all four faces, and the corners stay open, where the splayed legs stand on the ground. Every part stands on the plate top or on a part that does.

## 3.2 Key Visual Features

* A **ballast block** — the tallest element, an unadorned slab of metal riding on
  four visible guide rails above the head.
* **Splayed bracing legs** at the four corners, each with a broad foot pad.
* A **cutting head** under the block, mostly hidden, seen only as a rim of
  disturbed ground.
* A **chute through a port in the plate wall** on the face the ore leaves by: a low framed port at ground level, its mouth flush, the plate bridging it, the chute's drive on the plate top over it. The other three faces' ports are shut with a flush bolted hatch.
* **The raised cast plate** under everything, its wall unbroken, the corners open for the legs.
* **Hoses only when connected:** on an ore that needs a fluid, a hose leaves each connected fitting over the plate top to where the fluid is used, 0.32 bore as vanilla's, one curve, nozzle down.

### Signature Feature

**The ballast ring rises slowly and drops hard on the working loop** — a
one-second stroke: a slow lift, a short hang, a fast fall, and a dead stop on the
landing shoulder that jolts through the frame. At the landing a low ring of ore
dust breaks out from under the ring and settles before the next lift; the dust is
a working layer tinted by the ore, never drawn on an idle drill. It is the
animation that says *this machine is using gravity*, and it is the reason the
building reads at a glance.

## 3.3 Colour Palette

**Signature finish (Liam, 2026-10-09).** Every Core building shares one base — dark
steel, the shared rust, dust and ground dirt — so they read as one planet's machines.
Each also carries one material of its own on its main surfaces, so a player tells them
apart by colour before shape, as vanilla's electric furnace, assembler and foundry
are told apart. Within the building, variation comes from replacement panels in a
slightly different shade, small stencilled markings, and rust that differs by place:
dry orange on tops, dark wet streaks below fittings.

**This building's: raw cast iron.** No paint: the chassis, legs and ring are
graphite grey `#3A3A3C` → `#5A5A5E` with a faint blue-black mill-scale sheen, and the
ore dust (`#7A6A55`) settles heavy on every ledge. The heaviest machine is all mass
and no finish; hazard banding stays on the leg feet only.


| Role | Hex | Where |
| ---- | --- | ----- |
| Chassis and legs | `#4A463F` → `#6E685C` | the mass of the building |
| Ballast ring | `#3A3A3C` → `#5A5A5E` | cast iron, the heaviest mass; its top face, wall and well kept apart in value |
| Press frame accent | `#6A2618` → `#842E1E` | red oxide paint on the gear-houses, drive cabinets, tank and bottles, chipped to the iron |
| Guide rails | `#8A8580` | four verticals |
| Hazard banding | `#C8A23A` | leg feet only, sparingly |
| Ore dust | `#7A6A55` | ground disturbance under the head |

**No glow at all.** Nothing on this machine is hot or energised; it is a weight
on a rail. A drill that glows would read as a smelter.

## 3.4 Sound (Liam, 2026-10-11)

A bed and two accents, all cued to the stroke (24 frames, one second). The
**bed** is a low, slow winch drone, the big mining drill's working loop
pitched down and quieter, heard while the drill works. The **landing** on
frame 5 is the building's voice: a deep, dead thud with a short ground rumble
under it, landing with the dust; the heaviest single sound on the Core. A
small **ratchet tick** on frame 23, at the top of the lift. Built from
vanilla's big-drill and impact sounds plus scripted layers, matched to the
big mining drill's loudness, and capped so a row of drills rumbles rather
than stacks.

---

# 4. Factorio Visual Style

## Technology tier and visual register

**Tier 0 — Foothold.** Crude and mechanical: bolted plate, cast legs, exposed guide rails, visible wear on the cutting head. A landing-day machine.

See the template's *"Technology tier sets the visual register"* — the player
should be able to read their progress off the factory floor without opening the
tech tree, so this building's surface treatment is set by where it sits on
`04-the-core.md` §6's ladder, not by taste.



5×5 and low, so the camera shows a great deal of roof and very little face — the
ballast block and the four rails carry the whole silhouette. Style reference to
attach: the **big mining drill**, cropped and upscaled, with the standing
disclaimer.

---


# 5. Building Orientation

* [x] North · [x] East · [x] South · [x] West

**Direction count:** `4`. The chute faces a different way in each, and a drill whose chute does not match its belt is the single most confusing thing a
mining building can do.

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| Ore out | `vector_to_place_result` `{ 0, −2.85 }` — the **north** face, centred | must match the chute's mouth in all four directions; `{ 0, −2.85 }` kept (Liam: *"Grow canvas, keep spot"*) |
| Mining fluid in | four connections, vanilla's big-mining-drill layout | **declared, and nothing uses them yet** |
| Electric | no visible connector | poles reach it wirelessly |
| Items in | none | no inserter feeds this building |

```
          . . O . .        O = ore out, north face, centre
          . . . . .        W = fluid in, west face, one tile north of centre
      W . . . . . . E      E = fluid in, east face, one tile north of centre
          . . . . .        S = fluid in, south face, either side of centre
          . S . S .
```

**`vector_to_place_result` is the one number that cannot be guessed.** It has to
be measured off each directional plate so the ore appears at the chute's mouth and
not through the chassis.

**This table used to say "Fluids: none; no `input_fluid_box`; this drill takes no
reagent".** That was true of the mechanic and wrong about the prototype, which
inherited four connections from the big mining drill all along. They were briefly
cleared and are now kept deliberately: **a mining fluid for this drill is wanted
later, and the layout has to be settled before the plate is cut.** A flange added
to a finished plate is a repaint of all four directions.

**The layout is vanilla's, verbatim**, and that is the reason to use it — a player
who has plumbed a big mining drill has already learned this one. North takes no
connection, because north is where the ore comes out.

**Each connection enters a closed fitting in the plate wall**, and vanilla's pipe joins it there. Nothing of vanilla's pipe or cover may overhang the wall or lap onto the plate top (Liam, 2026-10-28: the overhang is *"Where the game pipe joins"*). The south face sits at the footprint edge like the other three (*"A: face back to edge"*).

**The hoses are wet-only.** The drill's dry graphics carry no plumbing. Its `wet_mining_graphics_set`, which the engine draws only on an ore that needs a fluid, adds the hoses from each fitting over the plate top (Liam: *"Keep wet-only, smaller"*). No `pipe_picture`. Vanilla's covers are on unconnected fittings, and north covers are hidden (`secondary_draw_orders = { north = -1 }`; Liam: *"Hide them"*).

So on kamacite today the drill shows its closed fittings in the plate wall and nothing else. The day an ore asks for a fluid, the hoses appear by themselves, in all four directions, and no plate is repainted.

---

# 15. Factorio Prototype — sketch

```lua
{
  type = "mining-drill",
  name = "sae-ballast-drill",
  resource_categories = { "sae-kamacite" },
  mining_speed = 3.0,
  resource_drain_rate_percent = 50,   -- big-mining-drill.lua:568 is the precedent
  energy_usage = "600kW",
  energy_source = { type = "electric", usage_priority = "secondary-input" },
  surface_conditions = { { property = "gravity", min = 45 } },
  module_slots = 4,
  vector_to_place_result = { 0, -2.85 },   -- the north face; turned by the engine (§8)
}
```

---

# 16. Icon

The ballast block on its rails, seen square on, with the cutting head as a dark
rim beneath. Must read at 32 px as *"a weight on a drill"* — if it reads as a
plain drill, the icon has failed, because the weight is the entire building.

---

# 20. Open questions

- **Does it replace the electric drill or sit beside it?** The brief assumes
  beside: the vanilla drill stays available and stays faster, so the choice is
  live on every patch. If playtesting shows nobody ever builds the fast one, the
  fix is to widen the speed gap, not to remove the option.
- **Interaction with mining productivity.** `uses_force_mining_productivity_bonus`
  is on by default, and productivity already reduces effective drain. Check the
  two do not stack into an ore patch that is functionally infinite.
