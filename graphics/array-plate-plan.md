# Ignition Array — the plate plan

**What this is.** Every dimension the Array's art must hit, so a generation round
can be drawn *to* the slots rather than fitted into them afterwards. Two
diagrams accompany it and are the things to attach to a prompt:
`concept/plate-plan-deck.png` and `concept/plate-plan-lid.png`.

**Why it exists.** The previous attempt derived each plate's size, scale and
shift independently — every one from its own content, its own centroid, its own
measured ellipse. Five numbers that were each defensible and collectively wrong,
because nothing tied them to one another: the doors stopped closing over the
hole and the lid stopped reading as a circle. Correcting the numbers one at a
time made each better and the composition no better.

Every number below is read off vanilla's `rocket-silo` prototype, because that
is the machine whose doors the engine knows how to open. Nothing here is chosen.

---

## 1. The slots, exactly as vanilla defines them

All five ship at `scale = 0.5`, so **one tile is 64 source pixels**.

| Slot | Canvas | Shift (tiles) | On screen |
| --- | ---: | ---: | ---: |
| `base_day_sprite` | 628 × 612 | 0.0625, 0.109375 | 9.81 × 9.56 tiles |
| `shadow_sprite` | 656 × 600 | 0.625, −0.125 | 10.25 × 9.38 |
| `hole_sprite` | 400 × 270 | −0.15625, **+0.5** | 6.25 × 4.22 |
| `door_back_sprite` | 312 × 286 | **+1.15625**, 0.375 | 4.88 × 4.47 |
| `door_front_sprite` | 332 × 300 | **−0.875**, 1.03125 | 5.19 × 4.69 |

`hole_light_sprite` shares the hole's canvas and shift exactly.

**These shifts are meaningful only relative to one another.** That is the whole
lesson of the last attempt. The engine parts the two leaves along the vector
between their rest shifts and expects them to clear a hole sitting half a tile
south of the origin, beneath a deck sitting slightly north of it.

---

## 2. Everything located in one frame

Taking the deck plate as the reference canvas, the **entity origin sits at
(310, 299)** — that is `canvas centre − shift × 64`.

| Thing | In deck-plate pixels |
| --- | --- |
| Entity origin | (310, 299) |
| 9 × 9 footprint | x 22 … 598, y 11 … 587 |
| **The opening** | **400 × 270, centred (300, 331)** — x 100…500, y 196…466 |
| `door_back` canvas | x 228 … 540, y 180 … 466 |
| `door_front` canvas | x 88 … 420, y 215 … 515 |

As proportions of the deck plate, which is what a generator can actually work
to: the opening is **63.7% of the width and 44.1% of the height**, with its
centre **47.8% across and 54.1% down**. It is *not* centred — it sits low and a
little left, and drawing it centred is the single easiest way to get this wrong.

The opening's aspect is **1.481**. That number has been the whole difficulty of
this building; it is fixed here by construction.

---

## 3. The deck plate — `base.png`

**628 × 612, transparent background.**

* An octagonal armoured ring filling the plate, its outer edge at or just inside
  the 9 × 9 footprint marked in the diagram.
* **A hole straight through it**, 400 × 270 at (300, 331), fully transparent.
  This is not optional and not decoration: `hole_sprite` draws the shaft inside
  that gap and the two doors sit over it. A deck with the lid painted on cannot
  work — the doors part at ignition and reveal a second, closed lid underneath,
  which is exactly what the first version of this building shipped.
* The ring carries the machinery: cradles, capacitor drums, the four cable
  trunks, the bolted collar around the opening.
* Nothing lit. No glow, no lamps, no violet.

## 4. The lid — one image, split locally

Generate the lid **whole**, as a single ellipse, and let
`build-array-plates.py` cut it. Splitting is deterministic; asking a generator
for two halves that fit together is not.

**420 × 284** — five per cent proud of the opening, so the closed lid tucks
under the collar instead of butting against it. Measured at exactly the
opening's size it covered 87% and left a hairline of ring showing all the way
round.

**The seam runs at 108° from horizontal** — steep, leaning left at the top,
right at the bottom. This is a correction to every sheet drawn so far, which
used roughly 45°.

The angle is not taste. The engine slides the leaves apart along the vector
between their rest shifts, which is **(+2.031, −0.656) tiles** — east and
slightly north. A seam has to be perpendicular to the direction its halves
separate, or they grind past each other instead of opening. Perpendicular to
that vector is 108°, not 45°.

Give the seam real weight: heavy edge armour down both sides, a meeting lip,
locking dogs, and a step partway along where the two halves interlock — vanilla's
own leaves are stepped rather than meeting on a straight line.

## 5. The shaft — `hole.png`

**400 × 270**, the same canvas as the opening. The interior of a vertical shaft
seen from Factorio's tilted camera: **the far wall is the lit one**, bright along
the top of the mouth and falling to black at the bottom.

That is worth stating plainly because it caused three wrong measurements. The
shaft is *not* uniformly dark, and anything that looks for dark pixels to find
the opening measures the floor instead — which is how the lid came to be sized
40% too small.

---

## 6. What to attach to a generation round

1. `concept/plate-plan-deck.png` — the footprint and the opening, to scale.
2. `concept/plate-plan-lid.png` — the lid and the true seam angle.
3. The four standing style references from
   `tools/extract-style-references.py` (see the template, Appendix B).
4. A flat magenta background, which keys cleanly — the dark ground the earlier
   sheets used cannot be keyed at all, because the building's own dark parts run
   luminance 18–59 against a ground of 20–64.

State in the prompt that the plan images are **geometry diagrams, not artwork**:
their colours, flat shading and grid lines must not be copied.

## 7. Accepting a round

Reject on any of these rather than adjusting afterwards — adjusting afterwards
is what produced five mutually inconsistent numbers last time.

| Check | Target |
| --- | --- |
| Opening aspect | 1.45 – 1.52 |
| Opening width, as a fraction of deck width | 0.60 – 0.68 |
| Opening centre, across / down | 46–50% / 52–57% |
| Seam angle | 100° – 116° |
| Background | flat magenta, keys with no holes or ledges |
| Lit anything | none |
