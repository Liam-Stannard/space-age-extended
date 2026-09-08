# Ignition Array — the plate plan

**What this is.** Every dimension the Array's art must hit, so a generation round
can be drawn *to* the slots rather than fitted into them afterwards.

**`tools/build-array-plan.py` is the source of all of it.** Every number in this
document is derived there from vanilla's `rocket-silo` prototype, and the three
images it emits are drawn from the same constants — so the prose, the diagrams
and the template cannot drift apart. Run it after changing anything here.

  * `concept/plate-paint-template.png` — **the one to attach to a prompt.**
  * `concept/plate-plan-deck.png` — the dimensioned drawing, for a human.
  * `concept/plate-plan-lid.png` — the lid and the true seam angle.

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

### The numbers to put in a prompt

Percentages and fractions do not survive: "about two thirds wide" and "a fifth
taller" produced a hole at aspect 1.76 against a 1.48 target. Give arithmetic on
a round base instead, so the generator has a sum to check itself against rather
than a judgement to make.

> **If the building is 1000 units wide, it is 975 tall.**
> **The hole is 637 wide and 430 tall — exactly 1.4815 : 1.**
> **Its centre is 478 from the left edge and 527 from the top.**
> **Its edges: left 159, right 796, top 312, bottom 742.**
> **So the ring is 159 thick on the left, 204 on the right, 312 at the top and
> 232 at the bottom, and the hole is 0.637 of the building's width.**

Every one of those is the same geometry as the table above, scaled so the deck's
width is 1000. `concept/plate-plan-deck.png` carries them as labelled dimension
lines on the drawing itself, the ring included.

The hole is **not centred** — it sits low and a little left, because vanilla's
opening is half a tile south of the entity origin. Drawing it centred is the
single easiest way to get this wrong, and 478 / 527 rather than 500 / 487 is what
says so.

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

On the same 1000-unit base: **the lid is 669 wide and 452 tall**, again exactly
1.4815 : 1, centred on the hole at 478 / 527.

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

1. `concept/plate-paint-template.png` — **the silhouette to paint inside.**
   Flat grey where armour goes, flat magenta where the hole and the ground go,
   at exactly the proportions above.
2. The four standing style references from
   `tools/extract-style-references.py` (see the template, Appendix B).

The magenta stays. It keys cleanly, where the dark ground the earliest sheets
used cannot be keyed at all — the building's own dark parts run luminance 18–59
against a ground of 20–64.

### Show the ring, do not describe it

Rounds 1–3 were handed a diagram that drew the *hole* — a filled ellipse on a
dark ground — and stated everything else in words and arithmetic. The hole came
out right every time and the ring never did, because **the ring was the one
quantity there was nothing to copy**. r3 put the hole at 0.582 of the deck where
vanilla is at 0.637, which is not carelessness; it is a free variable being
filled in.

So the ask is now "paint inside this shape" rather than "draw a building with
these measurements". That is the same move that worked first time on v3, when
vanilla's actual hole sprite was handed over and the opening came back correct
immediately. Section 8's conclusion — a generator hits a shape it is shown and
not a ratio it is told — is the reason, and the template applies it to the ring
as well as the hole.

Two things still have to be said in words, because no template can show them:
the magenta inside the ring is background seen **through** a hole rather than a
coloured disc, and the template is a **geometry diagram, not artwork** — its flat
grey is a region to fill, not a colour to copy.

## 7. Accepting a round

Reject on any of these rather than adjusting afterwards — adjusting afterwards
is what produced five mutually inconsistent numbers last time.

| Check | Target |
| --- | --- |
| Opening aspect | 1.45 – 1.52 (target **1.4815**) |
| Opening width, on a 1000-wide building | 600 – 680 (target **637**) |
| Opening height, on a 1000-wide building | 405 – 460 (target **430**) |
| Opening centre, on a 1000-wide building | 460–500 across (target **478**), 505–555 down (target **527**) |
| Seam angle | 100° – 116° |
| Background | flat magenta, keys with no holes or ledges |
| Lit anything | none |

---

## 8. Round log

| Round | Aspect | Hole/deck | Centre | Verdict |
| --- | ---: | ---: | --- | --- |
| deck r1 | 1.76 | 0.578 | 50.0% / 53.1% | **the hole is real** — reject on aspect and size |

**Round 1 got the hard part right first time.** `concept/plan-deck-r1.png` has a
genuine hole straight through the deck showing background, which no previous
round of this building ever produced — every one of them painted a lid on and
left the engine nothing to open. The centre landed in band at 50.0% / 53.1%, the
octagon reads, the machinery sits on the inner wall, the palette is right and
nothing is lit.

Two numbers miss, and both are the same mistake in opposite directions: the hole
is too flat (**1.76** against a 1.45–1.52 band) and slightly too small (**0.578**
of the deck against 0.60–0.68). Flat and small together mean the *height* is what
is wrong — at the right height, 688 px wide would be 465 tall rather than 390,
which is both a 1.48 aspect and a bigger hole.

So the correction is one instruction: make the hole taller, not wider.

| deck r2 | 1.70 | 0.579 | 500 / 481 | numbers given as arithmetic; height moved 4% where 20% was asked |
| deck r3 | 1.62 | 0.582 | 501 / 476 | **fresh session, no history** — best building yet, aspect closest yet |
| deck r3 corrected | **1.481** | 0.582 | 501 / 476 | vertical stretch ×1.0928, applied locally |
| deck r4 | **1.493** | **0.648** | 494 / 527 | **PASS** — first round against the template, every band met |

**The template worked first time, and on the quantity that had never once come
back right.** r4 is `concept/plan-deck-r4.png`. Measured by
`tools/check-array-plate.py`:

| Check | r4 | Target | Band |
| --- | ---: | ---: | --- |
| Opening aspect | 1.493 | 1.4815 | 1.45 – 1.52 |
| Opening width | 648 | 637 | 600 – 680 |
| Opening height | 434 | 430 | 405 – 460 |
| Centre across | 494 | 478 | 460 – 500 |
| Centre down | 527 | 527 | 505 – 555 |
| Hole / deck | 0.648 | 0.637 | 0.60 – 0.68 |

Sixteen attempts stated the aspect and none landed inside the band; the first
one handed a shape to paint inside landed at 1.493 without the ratio being
mentioned at all. The building is 1000 × 976 against a plan of 1000 × 975, and
fitting the opening to vanilla's 6.25 tiles puts the deck at **9.65 × 9.42
tiles** against vanilla's 9.81 × 9.56 — the overhang problem is simply gone,
with no crop and no local correction of any kind.

The one number worth watching is the centre, at 494 across against a target of
478 and a band ending at 500. The ring is thinner on its right side than the
plan asks, by about 22 units on the 1000 base. It is inside the band and not
worth another round.

**Arithmetic did not move it either, and that is worth recording.** Round 2 gave
the exact figures — 637 wide, 430 tall, 1.4815 : 1, edges at 159/796/312/742 —
and the height moved four per cent where twenty was asked for. Round 3 started a
completely fresh session with no history of previous attempts, which produced the
best *building* of the whole run and got the aspect to 1.62, its closest. Neither
hit the band.

**The conclusion after roughly fifteen attempts across this building: a generator
will not hit a stated aspect ratio.** It will hit a *shape* it is shown, and it
will draw a hole when told the background must show through — both of those
worked first time — but a numeric ratio is not something it converges on.

**So the aspect is corrected locally, and that is the right division of labour.**
A hole is an ellipse; scaling the whole plate vertically by 1.0928 lands 1.619 on
1.4815 exactly, cannot distort anything (every feature scales together), and
takes one operation. Generate the design, measure the ellipse, scale to fit.

**What was still open after r3 was not the aspect but the ring's thickness.** The
hole is 0.582 of the deck's width where the plan wants 0.637, so the ring is
proportionally fatter than vanilla's. Fitting the hole to vanilla's 6.25 tiles
therefore puts the deck at **10.74 tiles** on a 9-tile footprint, against
vanilla's 9.81 — a 19% overhang rather than 9%.

Cropping 4.3% off each edge fixes it arithmetically and costs only a band of
plain outer armour, which was measured and drawn. **It was rejected in favour of
regenerating**, and rightly: a crop treats the symptom on every plate for the
rest of the building's life, where a template that shows the ring removes the
free variable once. Hence section 6.
