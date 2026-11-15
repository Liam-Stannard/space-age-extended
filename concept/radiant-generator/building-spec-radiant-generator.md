# Radiant Generator — building spec

Radiant Generator. Burns radiant fuel for electricity, and hands back a spent
cell for each one.

---

# 1. Facts

- **Name:** Radiant Generator
- **What it does:** burns radiant fuel to make electricity. Each fuel it burns
  leaves a spent cell.
- **Size and directions:** 5 × 5; one drawing for all four directions.
- **Where it can be built:** pressure 9 or less, so today the Core and space
  platforms (TODO, pressure 200).
- **Power:** makes up to 10 MW.
- **Inputs and outputs:** radiant fuel only, in 2 fuel slots; one spent cell
  out for each fuel burnt, into 1 slot. Inserters load and empty it.
- **Speed:** one radiant fuel lasts 50 s at full output.
- **Cost:** 20 processing units, 20 low density structures, 40 steel plate;
  20 s.
- **Weight:** 40 kg, stack of 10.
- **Unlocked by:** Radiant power.
- **Art:** signed off (2026-10-27).

---

# 3. Visual Design

## 3.1 Design Concept

The Carousel Foundry: a power plant where the fuel can be followed to the wire.
The fuel is drawn as cells. A carousel carries them, a crane swaps them into a
lead crucible, tubes turn its heat to current, and a converter and transformer
send it out. It must not read as a steam engine: no pistons, rods, crank or
flywheel, no boiler, chimney or exhaust, no steam, smoke or fire, and no orange
heat. It must not look like the Hydrogen turbine or the Reaction Plant.

## 3.2 Key Visual Features

* The **carousel**, the west half: a lead-clad, banded drum and a turntable of
  eight lead-capped cell pockets. A loading hood with two charging ports feeds
  it. A geared motor's pinion turns the ring gear, which has 27 coarse teeth so
  it does not flicker. A **collector head** with a bolted bullseye port sits
  over the pocket before the pick. Spent cells leave the hood down a chute into
  a lead bin on the west face.
* The **twin-hoist crane**, ochre, on rails on the north shield housing and on
  posts along the crucible's south face. Its bridge has no hazard stripes, so it
  does not flicker as it runs. The **lead crucible** holds the plate rack, seen
  through a glazed slot, and a served well whose lid lifts while the crane
  works it.
* **Five thermionic tubes**, banded, on the crucible's east flank: glass, a lit
  emitter low in each, finned copper caps. The copper bus runs under the caps'
  fins, with no strap to each cap, into a grey terminal box bolted to the tube
  column's base. The box's lid is level with the tube caps, and the box hides
  the first tube's lower glass. Three cables leave it through glands into an
  open cable tray with ochre cleats, and run to the switchgear.
* The **rotary converter** along the south: an open commutator with eight dark
  copper bars, brush gear, a coupling, the AC machine and an exciter. The
  switchgear and the DC bus tray sit in the south-east. The transformer and the
  armoured trunks sit in the south-west.
* **Cooling and clutter:** a pump and hoses, a radiator on the north shield
  housing, an expansion tank in the north-east corner; gas bottles, valves,
  barrels, ladders and stains. Equipment runs to the edges and breaks the
  corners unevenly; no flat deck shows.

### Signature Feature

The crane's cell swap: it lifts a fresh cell from the carousel and lowers it
into the crucible while the spent one comes back. It makes the chain from fuel
to wire visible.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Lead | `#6A6258`, new lead `#7A7266` | carousel drum and table, crucible, loading hood, bin |
| Grey paint | `#6E6A62` | shield housing, radiator, tank, AC machine, cabinet, terminal box |
| Teal paint | `#3E6462` | housing roof, tank top |
| Ochre paint | `#9C7426` | crane, ladders, tray cleats |
| Weathered green | `#4E6034` | motors, switchgear cabinet |
| Cream paint | `#ACA084` | transformer, exciter |
| Oxide red | `#6E2C1E` | pump |
| Dark steel | `#3E3934` | decks, frames, foot rings |
| Copper | `#94592C` | collector plates, tube caps, bus |
| The isotope's light | `#1F63FF` → `#73ADFF` | bullseye port, plate-rack slot, tube emitters, well's mouth |
| Status lamps | green, `#00FF00` tint | the lamps, lit only while working |
| Night lights | the isotope's blue, steady | one at each of the four openings, while working |
| Wreck's dying blue | `#1F63FF` → `#0B2A8C`, faint (0.4) | the wreck's well; glows at night |

The isotope's light is one light in four openings. Each is a bright core
grading to deep blue at the rim, behind glass with a thin highlight and a dark
bezel, and its glow stays tight to the opening. The plates, cells and tube
grids show dark against it. It does not flicker, and no pattern moves inside
it; only its strength moves (§9). The engine's own flickering burner light
stays. Orange is for copper and paint only; nothing glows orange. Idle, nothing
is lit.

---

# 4. Factorio Visual Style

Style reference: vanilla's nuclear reactor and fusion reactor, for the bulk and
cooling of a power plant; it takes the nuclear reactor's 5 × 5 boxes. Vanilla's
steam engine and steam turbine are what it must not resemble.

---

# 8. Connections

No pipes and no electric connector: poles in reach take its power. Inserters
load fuel and take spent cells from any side. The loading hood's two charging
ports show where fuel goes in. The chute and lead bin on the west face show
where spent cells come out. The armoured trunks in the south-west show where
power leaves. None of these limits where an inserter or pole stands. Every pipe
and hose on it is its own coolant plumbing.

---

# 9. Working Animation

| # | Step | Entries | Ticks | What moves | Ease | Accent |
|---|---|---|---|---|---|---|
| 1 | Pick | 1–4 | 16.8 | hoist A lowers, takes the fresh cell from the pocket and rises | eased | — |
| 2 | Return | 5–10 | 25.2 | the bridge shifts; hoist B lowers the spent cell into the pocket and rises | eased | — |
| 3 | Run out | 11–16 | 25.2 | the bridge runs east to the crucible; the carousel starts to index | eased | — |
| 4 | Swap | 17–26 | 42 | hoist B lifts the spent cell from the well; the bridge shifts; hoist A sets the fresh one in | eased | — |
| 5 | Run back | 27–32 | 25.2 | the bridge runs back to the carousel | eased | — |

The loop is 32 entries, one crane cycle, at 4.2 ticks (70 ms) an entry: 134.4
ticks. It has no craft to match. This is the pace Liam signed off, at full
output; the engine slows it as output falls. The carousel indexes one pocket
over entries 12–20, its pinion turning with it, and the port dims to 50 % while
it does. The well's lid is up over entries 17–27, and the well's light rises
over three entries as it lifts. Through the loop the commutator turns half a
turn; the couplings and gauge needles turn; the five tubes swell in turn along
the row, twice a loop, between 70 and 100 %; the slot's light breathes twice a
loop, between 84 and 100 %.

Idle, the machine freezes where it stopped, with nothing lit. It looks the same
with no fuel and with no demand. It dies in a fireball and sparks, without
smoke, and leaves its own wreck. Sound: vanilla's fusion generator's for now;
its own later.

---

# 14. Icon

Rendered from the model: the whole machine, working, with its openings and
lamps lit. Kept as rendered.
