# Drop Crusher plan, both methods (animation study, T02)

**The answer, in three lines:**
- **Method:** A, the moving parts as a layer over a one-frame plate (as now).
- **Frames and speed:** a 60-entry `frame_sequence` over 44 sheet frames, `animation_speed` 0.5: 240 ticks, one craft.
- **Sheets:** 4.73 MiB raw RGBA (now 2.74 MiB; the foundry's working sheets 150.2 MiB).

This is a plan for animating the Drop Crusher the way the foundry is animated, and a
comparison of two ways to make it. It is for Liam to judge. Nothing is rendered and
nothing in the mod changes. Read `foundry.md` (T01) first.

- **Timeline sheet:** `concept/animation-study/drop-crusher-timeline.png` (2920 × 1680):
  every shipped frame, the crown's height now and planned, the plan's steps and accents.
- **Every figure:** `concept/animation-study/drop-crusher-figures.json`.
- **Script:** `concept/animation-study/drop_crusher_plan.py`. Run `foundry_study.py`
  first. A second run writes the same files, byte for byte.

The two methods:

- **A (ours):** the plate is one frame. The moving parts are a separate layer, a
  window round the collar, one frame per pose.
- **B (the foundry's):** the whole building is rendered again for every frame.

## What the spec asks for

The spec has no §6.2. Its motion story is in §3.1, §3.2, §3.4 and §9:

- The crown is **wound up** a rack by two geared drums, held by a pawl, then the
  pawl **kicks clear** and it **drops**, landing **seated flush** in its collar.
- **Frame 0 is cocked:** the weight just past halfway up, held by the pawl between
  two clicks. That is the rest pose. No accent may sit on frame 0.
- **Three sounds:** pawl clicks on the wind-up, the trip at the top, the drop on landing.
- **The fall is faked in frame spacing:** slow wind-up, faster and faster fall, hard stop.
  About two thirds of the frames to the rise and trip, one third to the fall and impact.
- **It is a rhythm, not an event.** One loop is one craft: 4 s, 240 ticks at crafting speed 1.
- **Nothing is hot.** No glow (§3.3). Nothing burns, so **no smoke**.

## The shipped animation, measured

- 24 frames at `animation_speed` 0.2. **Sum:** 24 / (0.2 × 1 × 0.5) = **240 ticks**.
  That is one frame every **10 ticks**, 6 frames a second. The foundry runs at 19.2.
- **Rise:** 16 frames at even speed. No ease in or out.
- **Fall:** top on frame 6, seated on 14. **Sum:** 14 − 6 = 8 frame changes × 10 ticks = **80 ticks, 1.33 s.**
- **No hold anywhere.** The crown moves on all 24 frame changes. It reaches the top on 6
  and starts down on 7. It lands on 14 and leaves the seat on 15.
- **14.1 %** of the drawn building changes during the loop. The foundry: 46.4 %.
- The moving-parts window is a 191 × 136 box. Its area (25,976 px) is **62 %** of the
  building's opaque pixel count (41,611). That compares a box with drawn pixels; the
  window itself is partly empty.
- Sheets: **2.74 MiB** raw RGBA (sum in the notes below).

## The plan: a foundry-style timeline

**60 frames at `animation_speed` 0.5, played as a `frame_sequence`.**

- **Sum:** 60 / (0.5 × 1 × 0.5) = **240 ticks**, the recipe's 240. One drop a craft, as now.
- One entry every **4 ticks**, 15 a second. Close to the foundry's 3.125 ticks.
- Every frame 0–59 is in exactly one step. **Sum:** 13 + 7 + 2 + 6 + 1 + 13 + 18 = **60**.

| # | Step | Frames | Length | Ticks | What moves | Ease | Accents |
| - | ---- | ------ | ------ | ----- | ---------- | ---- | ------- |
| 1 | Wind-up, upper half | 0–12 | 13 | 52 | crown climbs the rack, gears turn, pawl ticks over the teeth | even, then slows over the last 4 changes into the top | 6 pawl |
| 2 | Top hold | 13–19 | 7 | 28 | nothing: the crown reaches the top on 13 and is held by the pawl | hold | — |
| 3 | Trip | 20–21 | 2 | 8 | pawl kicks clear; the crown is still at the top | snap | 20 trip |
| 4 | Fall | 22–27 | 6 | 24 | crown drops; gears spin back with the rack | faster every frame (t squared) | — |
| 5 | Land | 28 | 1 | 4 | crown seated flush; gears stop dead | hard stop | 28 drop |
| 6 | Seated hold | 29–41 | 13 | 52 | nothing, except the pawl drops back onto the rack on 36–37 | hold; one 2-frame snap | — |
| 7 | Wind-up, lower half | 42–59 | 18 | 72 | motor takes up the load; crown leaves the seat | slow in over 4 frames, then even | 50 pawl, 58 pawl |

Checks (all computed by the script):

- **Frame 0** is the crown at **61 %** of its travel, between the clicks on 58 and 6,
  held by the pawl. That is the spec's cocked rest pose. **No accent is on frame 0.**
- **Rise, top hold and trip:** 13 + 7 + 2 + 18 = **40 frames**, two thirds.
  **Fall, landing and seated hold:** 6 + 1 + 13 = **20 frames**, one third.
- **The fall, counted as the shipped one is** (frame changes from the last frame at the
  top to the seat): top until 21, seated on 28. **Sum:** 28 − 21 = 7 changes × 4 ticks =
  **28 ticks, 0.47 s**. The shipped fall is 80 ticks, so the plan's is **2.9 times faster**.
- Each change drops further than the last: 2, 6, 10, 14, 18, 22, then 27 % of the travel.
  The last is the biggest: the hard stop.
- **The crown holds still on 21 of 60 changes: 84 ticks** (13 to 21, and 28 to 41). Now it holds on none.
- **Five accents, as now:** three pawl clicks every 8 frames (50, 58, 6), the trip (20),
  the drop (28). Same sounds, new frames. They count the sequence's entries from 0.

### The frame_sequence

Held frames repeat one sheet frame, so only **44 sheet frames** are needed.
**Sum:** 13 wind-up + 1 top + 2 trip + 6 fall + 1 seated with the pawl clear + 2 pawl
drop-in + 1 seated with the pawl in + 18 wind-up = **44**.

- **Animation:** 60 entries. Entries 13–19 all play sheet frame 14 (1-based), entries
  28–35 sheet frame 23, entries 38–41 sheet frame 26. The full list is
  `frame_sequence.animation` in the figures file.
- **Idle:** a 60-entry sequence holding sheet frame 1 (frame 0, cocked), so a stopped
  crusher still rests cocked. The idle needs the same count as the animation, as now.
- **Accent frames count the sequence's entries from 0.** This is settled (Reaction Plant
  T04/T10, 2026-10-29). The mod already ships one: the Reaction Plant's 140-entry
  sequence with an accent on entry 21. (This branch's `knowledge/engine.md` predates the
  fix and still says "not yet verified".)
- **Holds are identical by construction:** a held entry is the same image, not a new render.

**What the plan does not add:** no smoke, no dust, no glow, no shake of the building
on landing, no new sound. None is in the spec. They are listed as questions below.

## The two methods, side by side

Both with the sequence: 60 entries, 44 sheet frames. Sums are in the notes below.

| | A: moving parts as a layer | B: whole building every frame |
| --- | --- | --- |
| Sheets | **4.73 MiB** | **7.97 MiB** (B with a moving shadow: about twice that) |
| Against the foundry's 150.2 MiB | 3.1 % | 5.3 % |
| Render time (3 logs) | **2.8 to 7.7 min** | **3.4 to 8.3 min** |
| B against A | — | 8 % to 44 % longer |
| Shadows of moving parts on the roof | Yes: in the layer now | Yes |
| Anything outside the window changing | No | Yes |
| The crown's shadow on the ground | Still (as now, by choice) | Still, unless the shadow is animated too |
| A jolt of the building on landing | Cannot | Can (not in the spec) |
| Hoses or cables joined to the building flexing | Cannot | Can |
| **The stillness test** (each moving part drawn free; what it uncovers already on the plate) | Must pass. The shipped model passes it. | Not needed to render. The spec still asks it as a design rule. |
| Static parts the same in every frame | Yes: one plate frame | In holds, yes (one image). Between moving frames each is a new render; sampling noise could make still parts shimmer. Not measured. |
| Frame 0 equals the still | Checked by the packer (`frame0_vs_still`) | True by construction |
| Tools | Exist: render.json animations with `frame_sequence`, pack.py, measure.py | Not built: no whole-building animated plate in the contract |

### Notes: the sums

**Sheets** (raw RGBA, 4 bytes a pixel, before the engine's atlas packing):

- A, 44 frames: 198×234 + 254×195 + 13×14 + 191×136 × 44 = 1,238,988 px × 4 B = **4.73 MiB**.
- B, 44 frames: 198×234 × 44 + 254×195 + 13×14 = 2,088,320 px × 4 B = **7.97 MiB**.
- A against the foundry: 4.73 / 150.2 = 3.1 %. B: 7.97 / 150.2 = 5.3 %.
- Shipped (A, 24 frames): 198×234 + 254×195 + 13×14 + 191×136 × 24 = 719,468 px × 4 B = **2.74 MiB**.
- Sheet layout, A: 191 × 136 frames, 10 a row, 5 rows: one file of 1910 × 680.

**Render time.** Each sum is: startup to the first saved render + 3 one-off passes
(still, shadow, lamp) at the whole-building time + 44 animation frames + 2 check renders
a frame (the model renders a gear-only and a crown-only frame for every animation frame).

| Log | A, 44 frames | B, 44 frames |
| --- | --- | --- |
| vent pump r2 | 11.2 + 3 × 1.93 + 44 × 1.15 + 2 × 44 × 1.15 = **168.8 s** | 11.2 + 3 × 1.93 + 44 × 1.93 + 2 × 44 × 1.15 = **203.1 s** |
| ballast drill t03m | 168.5 + 3 × 4.78 + 44 × 3.93 + 2 × 44 × 1.19 = **460.5 s** | 168.5 + 3 × 4.78 + 44 × 4.78 + 2 × 44 × 1.19 = **497.9 s** |
| reaction plant t09d | 118.5 + 3 × 6.64 + 44 × 3.22 + 2 × 44 × 0.72 = **343.5 s** | 118.5 + 3 × 6.64 + 44 × 6.64 + 2 × 44 × 0.72 = **493.9 s** |

- B against A: 203.1 / 168.8 = 1.20; 497.9 / 460.5 = 1.08; 493.9 / 343.5 = 1.44.
- Without the sequence (60 frames) every figure is higher, by 16 layer and 32 check
  renders: A 224.0 / 561.4 / 418.0 s, B 270.8 / 612.4 / 623.2 s (in the figures file).
- Shipped (A, 24 frames), vent pump log: 11.2 + 3 × 1.93 + 24 × 1.15 + 2 × 24 × 1.15 = 99.8 s.

**The logs** (all GPU, OptiX, RTX 5080), parsed by
`evidence/animation-study/blender-log-timings.py`, output in
`evidence/animation-study/blender-log-timings.txt`:

- `evidence/gas-pump-t15/r2/blender.log` (vent pump, 3×3, nearest in size): still
  1.93 s, `mech` frame 1.15 s, startup 11.2 s. It has no check pass, so the check
  renders use the `mech` time.
- `evidence/ballast-drill-t03m/s2/north/plate/blender.log` (5×5): still 4.78 s,
  `stroke` frame 3.93 s, `stroke-ring` check 1.19 s, startup 168.5 s.
- `evidence/rp-t09d/run-north/blender.log` (5×5, slowest): still 6.64 s, `drive`
  frame 3.22 s, `press-pack` check 0.72 s, startup 118.5 s.
- Each time is the gap between two saved renders, so it includes setting up the next pass.
- **No Drop Crusher log exists.** Its canvas (320 × 304, rendered at 4×) and samples
  (48) are smaller than these buildings', so these are likely upper bounds.

### Frame-count options (no sequence, raw RGBA)

| Frames | Speed | Ticks a frame | Frames a second | A | B |
| ------ | ----- | ------------- | --------------- | - | - |
| 24 (now) | 0.2 | 10 | 6 | 2.74 MiB | 4.43 MiB |
| 48 | 0.4 | 5 | 12 | 5.12 MiB | 8.67 MiB |
| 60 | 0.5 | 4 | 15 | 6.31 MiB | 10.79 MiB |
| 96 | 0.8 | 2.5 | 24 | 9.88 MiB | 17.16 MiB |

- A = 96,044 + 191×136 × frames; B = 198×234 × frames + 49,712. Here
  96,044 = 198×234 + 254×195 + 13×14 and 49,712 = 254×195 + 13×14. Times 4 B.
  Example, 60 frames, A: 96,044 + 25,976 × 60 = 1,654,604 px × 4 B = 6.31 MiB.
- Every speed is the frame count over 120, so every loop is exactly 240 ticks.
- With a sequence, only the distinct poses count, as above.

## Now against the plan

| | Shipped | Plan |
| --- | --- | --- |
| Entries / sheet frames | 24 / 24 | 60 / 44 |
| Ticks a frame | 10 | 4 |
| Loop | 240 ticks, one craft | 240 ticks, one craft |
| Wind-up | 16 frame changes, even speed, no ease | 32 frame changes, eased in and out |
| Hold at the top | none | 13–19, then the trip on 20–21 |
| Fall (top to seat) | 8 changes, 80 ticks, 1.33 s | 7 changes, 28 ticks, 0.47 s |
| Last step of the fall | 23 % of the travel | 27 % of the travel |
| Seated hold | none | 13 frames, 52 ticks |
| Pawl | clear from top to seat, back in at the seat | kicks clear in 2 frames; drops back in 2 frames during the seated hold |
| Crown still | 0 of 24 changes | 21 of 60 (84 ticks) |
| Accents | pawl 18, 22, 2; trip 6; drop 14 | pawl 50, 58, 6; trip 20; drop 28 |
| Frame 0 | cocked, 63 % up | cocked, 61 % up |
| Idle | 24 entries holding frame 0 | 60 entries holding frame 0 |
| Sheet (A) | 2.74 MiB | 4.73 MiB |

The biggest change is the fall. Today it takes a third of the loop and reads as a
lowering. In the plan it takes about a ninth, and the time it gives back goes into two
holds. That is the foundry's pattern: slow motion, a hold, a snap, a hold.

## Recommendation

**Method A with a `frame_sequence`: 60 entries over 44 sheet frames, `animation_speed` 0.5.**

- All the Drop Crusher's moving parts are on the roof, inside one window. B would
  re-render a building that does not move, to gain nothing the spec asks for.
- A costs less: 4.73 MiB against 7.97, and 8–44 % less render time.
- The sequence saves 16 layer renders and 1.58 MiB, and makes the holds identical by
  construction. It carries no engine risk: accent counting with a sequence is settled,
  and the Reaction Plant already ships one.
- A keeps every still part identical in every frame. B might make them shimmer between moving frames.
- A's tools exist and passed on this building already.
- B is the right method for a building whose motion spreads over most of it, as the
  foundry's does (46 % of its pixels). The Drop Crusher moves 14 %.

This is a recommendation, not a decision. T03 is Liam's.

## Open questions for Liam

1. **Frame count.** (a) keep 24; (b) 48 at 0.4; (c) **60 entries at 0.5**; (d) 96 at 0.8.
   Recommend (c): 4 ticks a frame is near the foundry, and the sheet stays small.
2. **The fall's length.** The spec gives "the last third to the fall and impact".
   (a) **the third includes the seated hold**: a 28-tick fall and a 13-frame hold (the plan);
   (b) the fall takes the whole third, as now (80 ticks), with no hold;
   (c) between: about a 40-tick fall and a 9-frame hold. Recommend (a): a fast fall reads as a drop.
   Note: `machines.lua` line 219 records that Liam once judged a faster stroke "too fast"
   (speed 0.2 played the whole loop twice as fast). The plan keeps the loop's rate, one
   drop every 240 ticks, but makes the fall itself about 3 times faster. A client check
   of the feel is still needed.
3. **The holds.** A 7-frame hold at the top (then a 2-frame trip) and a 13-frame hold on
   the seat: (a) **yes**; (b) shorter; (c) none. Recommend (a).
4. **A sound for the pawl dropping back in (36–37).** (a) **no new sound**, the five
   accents as now; (b) a new soft click, through a sound task. Recommend (a).
5. **`frame_sequence` for the holds.** (a) render all 60 frames: 6.31 MiB (A), 10.79 (B);
   (b) **a sequence: 60 entries over 44 sheet frames**: 4.73 MiB (A), 7.97 (B), 16 fewer
   layer renders, holds identical by construction. Accent frames count the sequence's
   entries from 0 (settled, Reaction Plant T04/T10, 2026-10-29; the Reaction Plant ships a
   140-entry sequence with an accent on entry 21), so there is no engine risk. Recommend (b).
6. **Anything outside the spec:** a jolt of the building on landing, dust from the
   seat, a moving ground shadow. (a) **none**; (b) choose some, which needs a spec
   change first. Recommend (a). The spec has no dust and no smoke, and nothing burns.
7. **Text that the plan would make stale, for a later wording task.** If the plan goes
   ahead, these all describe the 24-frame stroke and would change with it:
   - spec §3.4 (signed off 2026-10-11): "24 frames, four seconds", the frame story
     (0–6 wind up, 6 top, 7–13 fall, 14 seated) and the accent frames 18, 22, 2, 6, 14;
   - spec §9's stroke story and §0's table; §9 and §13 also still describe the older
     Animatorio stroke (48 × 54 window, 288 × 216 sheet), not the shipped Blender one
     (191 × 136, 24 frames);
   - `prototypes/core/machines.lua`: the stroke and phase notes (about lines 135–160),
     the timing note and `DC_FRAMES`/`DC_SPEED` (about lines 210–232), and the accent
     comments and frames (about lines 370–416).
   (a) **change them through factorio-spec-wording and the re-animation task's code
   review, once T03 is decided**; (b) leave them. Recommend (a). I have touched none of them.
8. **T03.** (a) **a re-animation task for the Drop Crusher: method A, a 60-entry sequence
   over 44 frames, speed 0.5**; (b) the same with method B; (c) stop here. Recommend (a).

## Wording the study proposes (not written anywhere)

For Liam to agree separately, through factorio-spec-wording.

- **knowledge/standards.md, under Buildings:** "A loop is planned as steps before it
  is modelled: each step's frames, the parts that move, their ease, and the sound it
  lands on. Every moving part holds still for part of the loop; sounds mostly sit on
  starts and stops, with some inside a motion or a hold; the steps add up to the loop,
  and the loop to the recipe's ticks. Holds are played with a `frame_sequence`, not
  rendered again. (Vanilla foundry: each part rests for much of its 128 frames, and no
  frame is fully still.)"
- **The spec template's animation section:** add a timeline table (step, frames,
  ticks, what moves, ease, accent) and two checks: the frames add up; the loop's ticks
  equal one craft, or say why not.
- **knowledge/engine.md:** this branch's copy still says accent counting with a
  `frame_sequence` is "not yet verified". The fix is on another branch; it lands at merge.
