# Vacuum Furnace — building spec

Vacuum Furnace. A sealed electric furnace. Its job is still to be decided
(TODO).

---

# 1. Facts

- **Name:** Vacuum Furnace
- **What it does:** smelts. It picks its recipe from what it is fed. Today it
  runs only plain smelting; its job is still to be decided (TODO).
- **Size and directions:** 3 × 3, 4 directions. One drawing for all four; only
  the pipe ports turn, so the fluid line runs north–south or east–west.
- **Where it can be built:** pressure 9 or less, so today the Core and
  platforms (TODO, pressure 200).
- **Power:** uses 1.2 MW of electricity.
- **Inputs and outputs:** one item slot in, one out. It runs every smelting
  recipe, among them 4 kamacite fines → 1 kamacite plate in 9.6 s, and
  3 crushed kamacite → 1 kamacite plate in 6.4 s. A fluid line passes through
  it, north face to south face, and holds 2000; no recipe uses it.
- **Speed:** crafting speed 1.5, so a plate every 6.4 s from fines and every
  4.27 s from crushed kamacite. 2 module slots.
- **Cost:** 50 kamacite plate, 10 processing unit; 10 s.
- **Weight:** 40 kg, stack of 20.
- **Unlocked by:** Vacuum sintering.
- **Art:** signed off (2026-10-09).

---

# 3. Visual Design

## 3.1 Design Concept

A sealed pressure vessel: a squat welded drum with no door, no chimney and no
fire showing. A heavy clamped hatch in the roof is the only way in. It must not
be mistaken for vanilla's electric furnace, with its open front and glowing
throat.

## 3.2 Key Visual Features

* A **welded hull** that fills the 3 × 3, with no base. An octagonal hull with
  walls leaning back, and the round drum on its centre. Plates in two courses,
  each plate its own tone and standing slightly proud of the next; every seam
  is a continuous weld, never bolted or gasketed. Bolted stiffeners and bolt
  rows, angle iron worn bare down every corner, a kerbed, mitre-welded cap
  rail. Newer replacement panels, and one newer plate bolted on askew on the
  south-west chamfer.
* A **flat clamped hatch**, round, on the centre of the roof and level with the
  rail. It is welded from six plates and held by eight radial dogs, each a few
  degrees off true. A faded hazard ring runs under the dogs, worn and scuffed
  where they are worked. No dome and no lifting eye. Off its symmetry: the
  viewport's cover, hinged on a knuckle and strapped back, its gasket showing;
  a vacuum-break angle valve with its handwheel and vent; a welded repair patch
  set askew. A copper ring, clamped in brass, runs round the hatch on the deck.
* **Three radiator stacks**, at the north-west, north-east and south-west
  corners, set into niches on the diagonal. Each is a bulky column of oval fins
  in brass collars between steel posts, with caps, cap bolts, a bleed plug and
  a top rail, on a foot block. Each stack's loop is heavy steel pipe in flanged
  spools: out of a nozzle in the cap rail beside its corner, never the copper
  ring, over the rail's edge, down the chamfer on a stand-off bracket and into
  the stack's top collar, with a short return from the foot collar into the
  hull. No loop crosses the middle of a face.
* A **vacuum pump** in the south-east niche: a barrel with a heavy flywheel
  upright in front of it, on its motor's shaft. The wheel stands free, with a
  gap all round, and the pump and niche behind it are fully modelled. Its rim
  is turned bright, so the dark spokes read moving against it. A vacuum gauge
  lies flat on the barrel's head, its dull dial deep in a hood. A suction valve
  wheel faces south-west; a brass gauge line runs into the hull through a
  gland; a starter box on the south-east chamfer feeds the motor through a
  conduit, with thick leads. A ribbed evacuation hose runs from a flanged port
  on the hatch, through a steel elbow with a brass clamp, over the rail and
  clipped down to a flanged inlet on the pump; a heavier hose runs from a stub
  on the east rail, along it and down into the pump's other side.
* **Services and wear**, laid on in plain view, all lying on the rail, the
  walls or the ground, so nothing rises above the furnace. A heaped cable
  bundle in an open tray round the front rail, and a muted, darker bundle in a
  tray along the north. Two grey-green junction boxes with glands, and drops to
  clamps on the radiator stacks. A brass maker's plate on the south face, a
  stencilled number, rust run down from the rail and the fittings, grime
  rising from the ground, oil soaked into the ground under the pump, and
  verdigris on the copper. No frost anywhere.

### Signature Feature

**The sight port.** One small, deep-set circle of orange glass at the centre of
the hatch, in an otherwise cold, dark building. It tells a running furnace from
an idle one at a glance.

## 3.3 Colour Palette

The steel carries the heat the sealed furnace never shows: temper colours,
graded away from the heat, at the bold strength. They run in rings out from the
hatch across the roof and rail, in bands down the hull's top course, and down
each radiator from its inlet. Rust stays out of the tempered zones, so the
brown never reads as rust. The temper is paint, never a light.

| Role | Hex | Where |
| ---- | --- | ----- |
| Painted area | not yet assigned (TODO) | — |
| Hull paint | `#3E3B36`, panels `#45433E` | the hull and the pump body |
| Drum | `#5E584E` | the drum |
| Temper, hottest to coolest | `#3E4A66` blue → `#5C4A6E` purple → `#8A5A3A` brown → `#B8964A` straw, thin and pale → plain steel | roof, rail, the hull's top course, radiators |
| Hatch | `#958577`, warm beige | the hatch |
| Copper | `#94592C` | the dogs (bronze), the deck ring |
| Brass | `#9C7034` | radiator collars, clamps, gauge line, maker's plate |
| Radiators and loops | `#6E685C` | the three stacks and their loops |
| Bare steel | `#77716A` | the cap rail, posts and fittings |
| Flywheel | spokes `#55504A`, rim `#9A948C`, turned bright | the pump |
| Gauge | dial `#8E877B`, dull; needle `#2B2E33` | the pump |
| Hazard ring | `#B8962E`, faded | the hatch, under the dogs |
| Weld seams | `#7A7268` | fine lines on the hull and hatch |
| Hoses | `#93603F`, dull rust-brown rubber | the two hoses |
| Cables | red `#B24C38`, yellow `#CCA848`, blue `#5678A6`, green `#5E8452`; north bundle muted: black `#3A3836`, grey `#4C4A47`, slate `#4A5260` | the trays |
| Junction boxes | `#5A6052`, grey-green | the two boxes |
| Rust | dry `#8E4A1E` → `#B4682E` on tops; wet `#1E140E` → `#3A2416` below fittings | outside the tempered zones |
| Viewport glass | `#26292C`, dark and smoky | the centre of the hatch |
| Sight-port glow | `#FFD9A0` core → `#E8A24A` → deep red at the edge | the viewport only |
| Status: output full | `#66B3FF`, pale blue | the viewport glass |

One glow: the sight port, while the furnace works. Through the smoky glass it
shows a hot bed in uneven clumps with dark gaps, hottest at the centre and deep
red at the edge, so it reads as a furnace, never as an even lamp. It swells and
settles, never flickers like a flame, and fades out as the furnace stops. Its
light on the ground is a deep red-orange. The same glass is the status light:
pale blue when nothing takes the output; otherwise dark when the furnace is
not working. Nothing else lights, and the gauge dial stays dull so it never
reads as a second light.

---

# 4. Factorio Visual Style

Style reference: vanilla's foundry, for weight and finish and its bundled
cables; vanilla's electromagnetic plant, for its slack corrugated hoses.

---

# 8. Connections

One fluid line, through ports at the middle of the north face {0, −1} and the
south face {0, 1}; each can take fluid in or pass it out. Rotated, it runs
east–west; the drawing does not turn. Fluid passes straight through whatever
the furnace is smelting, so a row of furnaces shares one line. The hull's wall
meets the tile edge at the middle of every face, so the pipe always butts
against it. The pipe pictures are the model's own, to assembler 3's outline, in
the furnace's metal; the north one draws behind the building. Vanilla's cover
caps a port while nothing is joined to it. Items go in and out from any side.
No electric connector shows.

---

# 9. Working Animation

| # | Step | Entries | Ticks | What moves | Ease | Accent |
|---|---|---|---|---|---|---|
| 1 | Running | 1–16 | 32 | the flywheel turns 60°, a sixth of a turn, which its six spokes make a loop; the gauge needle swings about 14° at its working reading and back, once | wheel even; needle eased | — |

The loop is 32 ticks at the furnace's crafting speed of 1.5, and 48 at speed 1.
It is not tied to a craft: the pump runs steadily while the furnace works.
When it stops, the wheel and the needle hold on the frame they reached, so each
must look right at rest on any frame. The sight-port glow is not in the loop;
it swells and settles while working and fades out when the furnace stops.

---

# 14. Icon

Rendered from the model: the drum from slightly above, the hatch on top and
the orange sight port. It must read at 32 px as a sealed pot. The weld seams
and the radiator loops are dropped at small sizes.
