# Reaction Plant — building spec

Reaction Plant. Turns radiant solution and hydrogen into radiant fuel.

---

# 1. Facts

- **Name:** Reaction Plant
- **What it does:** turns radiant solution and hydrogen into radiant fuel. It
  runs only its own recipes, and today there is one.
- **Size and directions:** 5 × 5, 4 directions; it can be mirrored.
- **Where it can be built:** pressure 1 to 9, so only the Core (TODO, pressure
  200).
- **Power:** uses 1.5 MW of electricity.
- **Inputs and outputs:** two fluid inputs on the north face and one fluid
  output on the south face, which no recipe uses yet. 100 radiant solution and
  100 hydrogen make 1 radiant fuel, which an inserter takes out.
- **Speed:** crafting speed 1, so one radiant fuel every 20 s; 3 module slots.
- **Cost:** 60 kamacite plate, 30 pipe, 20 advanced circuits; 10 s.
- **Weight:** 40 kg, stack of 20.
- **Unlocked by:** Radiant power.
- **Art:** signed off (2026-10-28; sight glasses and stubs 2026-10-29; press
  2026-10-30). The remnants and explosion are the oil refinery's for now.

---

# 3. Visual Design

## 3.1 Design Concept

A thermosiphon you watch go round: a foothold crew's kit piled onto one riveted
casing, with a lead-clad reactor and two glass legs, the blue climbing one and
falling down the other. It must not be mistaken for vanilla's chemical plant
(chimneys over a shed), the oil refinery (towers and flare stacks) or a storage
tank. It burns nothing, so there is no plume: the condenser drips and never steams.

## 3.2 Key Visual Features

Positions are given facing north.

* The **casing**: one riveted housing, 0.85 tile tall, over the whole
  footprint. The reactor, the two glass legs, the condenser and the settling pot
  stand up through its roof in bolted collars. The front corners are broken by
  the filter press (south-west) and the pump house (south-east).
* Two fat, strapped **glass legs**: in the riser the blue climbs with bright
  bubbles; in the downcomer it falls with dark flecks.
* The **agitator drive** on the reactor head: a shaft, a big five-spoked
  pulley, a laced belt and the motor's small pulley.
* The **filter press** on its lead-lined **drop box**. Five thin leaves; the
  head and the tail stand are bolted down. The cake falls into a dark chute
  mouth in the box's lid and is never seen leaving. Hazard tape on the box's
  south face is allowed.
* **A unit over each connection**, on the roof, joined by a riser with a
  visible reducer: the feed drum over the solution's, the compressor's bottle
  (on legs) over the hydrogen's, the receiver over the output's. A sight glass
  on each input line. Every hose and cable lands in a port (a bolted nozzle, a
  reducer, a saddle clamp or a gland); only the compressor's discharge stack
  ends without one. The gauges are double-size dials on stems: two on the
  reactor, one on the scrubber.

### Signature Feature

The glass loop, the blue going round, legible at one tile. Its finish is
weathered lead, one material among several.

## 3.3 Colour Palette

Every unit has its own paint.

| Role | Hex | Where |
| ---- | --- | ----- |
| Casing (the painted area) | `#8E8572`, grey trim | the housing |
| Lead | `#66625C` → `#86807A`, bloom `#B4A486` → `#D8CAA6` | reactor, settling pot, drop box, leg caps, every other filter leaf |
| Oxide red | `#6E2C1E` | scrubber, sampling cabinet |
| Ochre | `#9C7426` | feed drum, ladder |
| Weathered green | `#4E6034` | receiver, motors, press ram |
| Cream | `#ACA084` | pump house, make-up pot, filter leaves |
| Grey | `#6E6A62` | exchanger, instrument house |
| Dark steel | `#3E3934` | skids, saddles, frames, headers, the stubs |
| Bare steel | `#A8A090` | pipes, flanges, straps |
| Copper / brass | `#94592C` / `#9A7438` | condenser / gauges, nuts |
| Hoses / lagging | `#5E4636`, `#38302A` / `#9A8A68` | hoses and lagging |
| Accents | `#A8301E`, `#D0A428` | handwheels, marking rings |
| Filter cake | `#8C8476` | the cake, seen only in motion |
| Radiant light | the radiant blue (standards.md, Light; `tools/blender/radiant.py`) | the two legs only, while working |
| Status lamps | tinted by the engine | the pump house and the instrument house |
| Sight glasses | tinted by the recipe's fluids | one on each input line |

One glow: the radiant light, in the two legs, at one strength, only while
working. Idle, the legs are a still dark navy. The blue sits more than a tile
from every edge. There is no other blue but the solution's sight glass: no blue
cable, paint or lamp.

The two status lamps are the only other light, and they are always drawn: red
when idle or short of input, yellow when the output is full, the plant is
disabled or power is low, green when working, dark with no power. The sight
glasses are paint, not light; with no recipe set they are grey.

---

# 4. Factorio Visual Style

Tier 0, the foothold: hoses, lagging, bolted plate, strapped glass and visible
wear. Do not tidy it up. The shielding is lead sheet riveted on, not sealed
plant.

* Oil refinery and chemical plant: the massing, the hoses, the fluid window.
* Chemical plant, oil refinery, cryogenic plant and foundry: how a pipe meets
  the casing.
* Pumpjack and storage tank: surfaces and wear.
* Foundry and electromagnetic plant: colour.

---

# 8. Connections

Facing north, with today's recipe: the solution's input at {−1, −2} (north
face, west of centre), the hydrogen's at {1, −2} (north face, east of centre),
and the output at {0, 2} (south face, centre). All three turn with the
building.

Each connection meets a low stub in the housing. Vanilla's pipe joins it with no
gap, and vanilla's cover sits on it when nothing is joined. A north cover is
drawn behind the building. While the plant runs its recipe, the output has no
fluid box, so its stub shows no cover. The stub must look right both ways.

No marking names a fluid; the sight glass on each line shows it. Mirrored, the
two inputs swap fluids and the glasses swap tints. There is no output chute:
an inserter takes the fuel from any side. No electric connector shows.

The circuit connector stands on a terminal box with a cable gland, on the
housing wall facing the camera, in every direction; it uses vanilla's face-on
connector. A port hidden by the model in one direction is accepted. Nothing
crosses ±2.5; the art is 5 tiles wide, and facing east and west one faint pixel
reaches past the edge, accepted at sign-off.

---

# 9. Working Animation

The filter press runs once a craft. It opens to the west: the leaf pack backs
off 0.18 tile along the rails towards the tail stand. An entry is 60/7 ticks;
ticks are rounded.

| # | Step | Entries | Ticks | What moves | Ease | Accent |
|---|---|---|---|---|---|---|
| 1 | Shut | 1–2 | 17 | nothing | hold | — |
| 2 | Open | 3–10 | 69 | the leaf pack backs off west | eased | — |
| 3 | Hang | 11–12 | 17 | the cake hangs on its leaf | hold | — |
| 4 | Fall | 13–20 | 69 | the cake peels away and falls, gathering speed | eased | — |
| 5 | Land | 21–22 | 17 | the cake lands in the drop box | snap | entry 22; landing sound (stand-in) |
| 6 | Close | 23–32 | 86 | the leaf pack closes | eased | — |
| 7 | Hold | 33–140 | 925 | nothing | hold | — |

The 140 entries take 1200 ticks, one craft at crafting speed 1.

The rest runs one 24-frame loop of about 1.7 s, all through the craft:

* the legs: the bands rise two wavelengths a loop in the riser and fall in the
  downcomer; bubbles go up and flecks go down. They carry the glow.
* the agitator drive: the big pulley turns 144° a loop, the motor's pulley a
  full turn.
* the compressor, dosing-pump and pump couplings: 60° a loop.
* the three gauge needles, which twitch.
* the condenser drip: beads run down the copper, and two drops a loop fall from
  a drain cock on its south-east flank, inside the footprint, onto a wet patch.

Idle, everything stops where it is and the legs go dark navy. The press stays
where it stopped: usually shut, but open if the power was cut mid-craft.

---

# 14. Icon

The lead reactor and its two lit legs, rendered from the model, legible at
32 px. In alt mode the recipe icon is drawn at twice the size, at the centre.
