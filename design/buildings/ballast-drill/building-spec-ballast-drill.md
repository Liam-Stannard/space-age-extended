# Ballast Drill — building spec

Ballast Drill. Mines kamacite ore by its own weight, and drains the patch at
half the rate.

---

# 1. Facts

- **Name:** Ballast Drill
- **What it does:** mines kamacite ore over a 13 × 13 area. Each ore it mines
  takes only half an ore from the patch.
- **Size and directions:** 5 × 5, 4 directions.
- **Where it can be built:** on kamacite ore, where gravity is 45 or more, so
  only the Core.
- **Power:** uses 600 kW.
- **Inputs and outputs:** no input; kamacite ore out of a chute on one face.
  Four fluid connections, which nothing uses today.
- **Speed:** mining speed 3, so 3 ore a second; 4 module slots.
- **Cost:** 60 steel plate, 40 iron gear wheels, 15 advanced circuits; 10 s.
- **Weight:** 40 kg, stack of 20.
- **Unlocked by:** Core survey.
- **Art:** signed off (2026-10-29).
- **Remnants and explosion:** TODO.
- **Art files:** `concept/ballast-drill/`.

---

# 3. Visual Design

## 3.1 Design Concept

A press, not a hammer: a heavy cast ring is winched up and dropped on a
shoulder, so the drill works by its own weight. It is low and wide, braced on
splayed legs. It must not be mistaken for a derrick: no tower, no headframe,
nothing turning on top.

## 3.2 Key Visual Features

* The **ballast ring**: a cast-iron ring with a hub and six spokes. It rides
  three guide columns round a fixed, capped central column. It lands on a
  hammered shoulder, its four lugs on four hydraulic snubbers.
* The **press frame**: two red-oxide gear-houses on the north columns' heads.
  Each holds a winch, with a spur gear, a copper drum and a wire rope down to
  the ring.
* The **raised cast plate** under everything. It fills the footprint, with its
  top at 0.85 tile and its wall unbroken on all four faces. The corners are
  open, and four splayed legs stand there on broad foot pads on the ground.
  Every other part stands on the plate top, or on a part that does.
* The **chute**: a framed port in the plate wall at ground level, on the face
  the ore leaves by. Its mouth is flush, with a short drag chain and its drive
  on the plate top. The other three ports are shut by flush bolted hatches.
* **Services and wear**: ribbed hoses, cable bundles, junction boxes, a tank
  and bottles. The two gear-houses are different castings, and the ore dust
  lies heavy on every ledge.

### Signature Feature

The ring rises slowly and drops hard. It lands dead on the shoulder, the frame
jolts, and a low ring of ore dust breaks out from under it. This shows the
drill is using its weight.

## 3.3 Colour Palette

Raw cast iron, with no paint but the red oxide.

| Role | Hex | Where |
| ---- | --- | ----- |
| Cast iron | `#3A3A3C` → `#5A5A5E` | chassis, legs and ring, with a faint blue-black sheen; the ring's top, wall and well kept apart in value |
| Red oxide | `#6A2618` → `#842E1E` | the painted area: gear-houses, drive cabinets, tank and bottles, chipped to the iron |
| Guide columns | `#8A8580` | the three columns, worn bright where the shoes run |
| Copper | `#8A5A32` | the winch drums |
| Hazard banding | `#C8A23A` | the leg feet only |
| Ore dust | `#7A6A55` | settled on ledges and round the shoulder |
| Working dust and falling ore | neutral pale grey, tinted by the ore | drawn only while mining |
| Status lamp | white, tinted by state | a lens on the plate top, south-west |

The status lamp is the only glow. It is red when idle or out of ore, yellow
when blocked, disabled or short of power, green when working, and dark with no
power. Nothing else glows: nothing here is hot.

Two replacement panels are a slightly different shade, and there are small
stencilled markings. Rust is dry orange on tops, with dark wet streaks below
fittings.

---

# 4. Factorio Visual Style

Style reference: vanilla's big mining drill, for its finish, scale and camera,
and for how it carries its red.

---

# 8. Connections

- **Ore out:** at the middle of the north face, at {0, −2.85}, out of the
  chute's mouth. It turns with the drill, and so does the chute.
- **Fluid in:** four fittings, closed, in the plate wall at the footprint
  edge. West face at {−2, −1}, east face at {2, −1}, and two on the south face
  at {−1, 2} and {1, 2}. North has none, because the ore comes out there.
- **On kamacite today** no ore needs a fluid. The drill shows its closed
  fittings and nothing else: no cover, no hose. A pipe laid beside it ends in
  vanilla's end cap. Facing east or south, the cap at the west fitting lies
  over the plate's lower-left corner; this is accepted.
- **On an ore that needs a fluid**, a pipe joins each fitting at the wall. No
  part of the pipe or its cover overhangs the wall or lies on the plate top.
  An unconnected fitting shows vanilla's pipe cover; a cover that faces north
  is hidden behind the drill. A small hose, of vanilla's pipe bore, runs from
  each fitting over the plate top in one curve, nozzle down.
- No electric connector shows. No inserter feeds it.

---

# 9. Working Animation

One stroke: 24 entries in 60 ticks, one second.

| # | Step | Entries | Ticks | What moves | Ease | Accent |
|---|---|---|---|---|---|---|
| 1 | Hang | 1–2 | 5 | the ring held at the top | hold | — |
| 2 | Fall | 3–6 | 10 | the ring falls onto the shoulder; the winch gears spin fast | eased, speeding up | entry 6: the ring lands dead; the frame jolts two pixels; the dust breaks out; a deep thud with a ground rumble |
| 3 | Settle | 7–13 | 17.5 | the ring rebounds one pixel and seats again; the frame's jolt dies; a slung hose swings and stills; the dust spreads and settles | snap, then hold | — |
| 4 | Lift | 14–24 | 27.5 | the ring is winched slowly up; the winch gears turn slowly | eased | entry 24: a small ratchet tick at the top of the lift |

The loop is not one craft: the drill mines 3 ore in each one-second stroke.
While mining, ore falls off the chute's mouth in step with the stroke. Under
the stroke runs a low, slow winch drone. No more than two landings sound at
once, so a row of drills rumbles rather than stacks. The chute's chain runs
its own loop: 5 entries, 10 ticks. Idle, the ring stops where it is, and no
dust or ore is drawn.

---

# 14. Icon

Rendered from the model: the whole machine, ring raised, every port shut, no
hoses. It must read at 32 px as a weight on a drill.
