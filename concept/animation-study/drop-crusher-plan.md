# Drop Crusher plan, both methods (animation study, T02)

A plan for animating the Drop Crusher the way the foundry is animated, and a
comparison of two ways to make it. It is for Liam to judge. Nothing is rendered and
nothing in the mod changes. Read `foundry.md` (T01) first.

- **Timeline sheet:** `concept/animation-study/drop-crusher-timeline.png` (2920 × 1640):
  every shipped frame, the crown's height now and planned, the plan's steps and accents.
- **Every figure:** `concept/animation-study/drop-crusher-figures.json`.
- **Script:** `concept/animation-study/drop_crusher_plan.py`. Run `foundry_study.py`
  first. A second run writes the same files, byte for byte.

The two methods:

- **A (ours):** the plate is one frame. The moving parts are a separate layer, a
  window round the collar, one frame per step.
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
- **Fall:** 8 frames, distance as t squared. **80 ticks, 1.33 s.**
- **No hold anywhere.** The crown moves on all 24 frame changes. It reaches the top on 6
  and starts down on 7. It lands on 14 and leaves the seat on 15.
- **14.1 %** of the drawn building changes during the loop. The foundry: 46.4 %.
- The moving-parts window (191 × 136) is already **62 %** of the building's pixel count.
- Sheets: **2.74 MiB** raw RGBA (sum in the table below).

## The plan: a foundry-style timeline

**60 frames at `animation_speed` 0.5.**

- **Sum:** 60 / (0.5 × 1 × 0.5) = **240 ticks**, the recipe's 240. One drop a craft, as now.
- One frame every **4 ticks**, 15 frames a second. Close to the foundry's 3.125 ticks.
- Every frame 0–59 is in exactly one step. **Sum:** 14 + 6 + 2 + 6 + 1 + 13 + 18 = **60**.

| # | Step | Frames | Length | Ticks | What moves | Ease | Accents |
| - | ---- | ------ | ------ | ----- | ---------- | ---- | ------- |
| 1 | Wind-up, upper half | 0–13 | 14 | 56 | crown climbs the rack, gears turn, pawl ticks over the teeth | even, then slows over the last 4 frames into the top | 6 pawl |
| 2 | Top hold | 14–19 | 6 | 24 | nothing: crown held by the pawl | hold | — |
| 3 | Trip | 20–21 | 2 | 8 | pawl kicks clear | snap | 20 trip |
| 4 | Fall | 22–27 | 6 | 24 | crown drops; gears spin back with the rack | faster every frame (t squared) | — |
| 5 | Land | 28 | 1 | 4 | crown seated flush; gears stop dead | hard stop | 28 drop |
| 6 | Seated hold | 29–41 | 13 | 52 | nothing, except the pawl drops back onto the rack on 36–37 | hold; one 2-frame snap | — |
| 7 | Wind-up, lower half | 42–59 | 18 | 72 | motor takes up the load; crown leaves the seat | slow in over 4 frames, then even | 50 pawl, 58 pawl |

Checks (all computed by the script):

- **Frame 0** is the crown at **61 %** of its travel, between the clicks on 58 and 6,
  held by the pawl. That is the spec's cocked rest pose. **No accent is on frame 0.**
- **Rise, top hold and trip:** 14 + 6 + 2 + 18 = **40 frames**, two thirds.
  **Fall, landing and seated hold:** 6 + 1 + 13 = **20 frames**, one third.
- **The fall:** each frame drops further than the last (2, 6, 10, 14, 18, 22, then 27 %
  of the travel). The last step is the biggest: the hard stop.
- **The crown holds still on 21 of 60 frame changes: 84 ticks.** Now it holds on none.
- **Five accents, as now:** three pawl clicks every 8 frames (50, 58, 6), the trip (20),
  the drop (28). Same sounds, new frames.
- The idle animation still holds frame 0, so a stopped crusher still rests cocked.

**What the plan does not add:** no smoke, no dust, no glow, no shake of the building
on landing, no new sound. None is in the spec. They are listed as questions below.

## The two methods, side by side

Sheet sizes are raw RGBA, 4 bytes a pixel, before the engine's atlas packing.
Render times come from other buildings' Blender logs (no Blender was run); see the
notes under the table.

| | A: moving parts as a layer | B: whole building every frame |
| --- | --- | --- |
| **Sheet, 60 frames** | 198×234 + 254×195 + 13×14 + 191×136 × 60 = 1,654,604 px × 4 B = **6.31 MiB** | 198×234 × 60 + 254×195 + 13×14 = 2,829,632 px × 4 B = **10.79 MiB** |
| B with a moving shadow too | — | 198×234 × 60 + 254×195 × 60 + 13×14 = 5,751,902 px × 4 B = **21.94 MiB** |
| Sheet layout | 191 × 136 frames, 10 a row: 1910 × 816, one file | 198 × 234 frames, 10 a row: 1980 × 1404, one file |
| Against the foundry's 150.2 MiB | 6.31 / 150.2 = 4.2 % | 10.79 / 150.2 = 7.2 % |
| Against the foundry's anim alone, 58.4 MiB | 10.8 % | 18.5 % |
| **Render, vent pump r2 log** (3×3, nearest size) | 11.2 + 3 × 1.93 + 60 × 1.15 + 2 × 60 × 1.15 = **224.0 s (3.7 min)** | 11.2 + 3 × 1.93 + 60 × 1.93 + 2 × 60 × 1.15 = **270.8 s (4.5 min)** |
| **Render, ballast drill t03m log** (5×5) | 168.5 + 3 × 4.78 + 60 × 3.93 + 2 × 60 × 1.19 = **561.4 s (9.4 min)** | 168.5 + 3 × 4.78 + 60 × 4.78 + 2 × 60 × 1.19 = **612.4 s (10.2 min)** |
| **Render, reaction plant t09d log** (5×5, slowest) | 118.5 + 3 × 6.64 + 60 × 3.22 + 2 × 60 × 0.72 = **418.0 s (7.0 min)** | 118.5 + 3 × 6.64 + 60 × 6.64 + 2 × 60 × 0.72 = **623.2 s (10.4 min)** |
| B with a moving shadow (vent pump log) | — | 270.8 + 60 × 3.62 = **488.0 s** |
| Light and shadow moving with the parts | Yes on the roof: the crown's and gears' shadows on the roof are in the layer now. No outside the window. | Yes everywhere in the building's frame. |
| The crown's shadow on the ground | Still (as shipped, by choice) | Still, unless the shadow is animated too (doubles the sheet) |
| A jolt of the whole building on landing | Cannot | Can (not in the spec) |
| Parts joined to the building (hoses, cables) flexing | Cannot | Can |
| **The stillness test** (each moving part drawn free, what it uncovers already on the plate) | Must pass. The shipped model passes it. | Not needed to render. The spec still asks it as a design rule. |
| Static parts the same in every frame | Yes, by construction: one plate frame | Not guaranteed: each frame is a new render. Sampling noise could make the still parts shimmer. Not measured. |
| Frame 0 equals the still | Checked by the packer (`frame0_vs_still`) | True by construction |
| Tools | Exist: render.json animations, pack.py, measure.py | Not built: no whole-building animated plate in the contract. Unverified how much work. |

### Notes on the render estimates

- **Each sum is:** startup to the first saved render + 3 one-off passes (still,
  shadow, lamp) at the whole-building time + 60 animation frames + 2 check renders a
  frame (the Drop Crusher model renders a gear-only and a crown-only frame for every
  animation frame, for its checks).
- **The logs** (all GPU, OptiX, RTX 5080), parsed by
  `evidence/animation-study/blender-log-timings.py`, output in
  `evidence/animation-study/blender-log-timings.txt`:
  - `evidence/gas-pump-t15/r2/blender.log`: still 1.93 s, `mech` frame 1.15 s,
    startup 11.2 s. It has no check pass, so the check renders use the `mech` time.
  - `evidence/ballast-drill-t03m/s2/north/plate/blender.log`: still 4.78 s,
    `stroke` frame 3.93 s, `stroke-ring` check 1.19 s, startup 168.5 s.
  - `evidence/rp-t09d/run-north/blender.log`: still 6.64 s, `drive` frame 3.22 s,
    `press-pack` check 0.72 s, startup 118.5 s.
- **Each time is the gap between two saved renders.** It includes setting up the next
  pass, not only the render.
- **No Drop Crusher log exists.** Its canvas (320 × 304, rendered at 4×) and samples
  (48) are smaller than these three buildings', so these are likely upper bounds.
- **B costs 9 % to 49 % more render time than A** (612.4 / 561.4 and 623.2 / 418.0).
  Either is minutes, not hours.
- **Today's 24-frame A, for scale:** 11.2 + 3 × 1.93 + 24 × 1.15 + 2 × 24 × 1.15 = 99.8 s
  on the vent pump log.

### Frame-count options (both methods, raw RGBA)

| Frames | Speed | Ticks a frame | Frames a second | A | B |
| ------ | ----- | ------------- | --------------- | - | - |
| 24 (now) | 0.2 | 10 | 6 | 96,044 + 191×136 × 24 = 719,468 px = 2.74 MiB | 198×234 × 24 + 49,712 = 1,161,680 px = 4.43 MiB |
| 48 | 0.4 | 5 | 12 | 96,044 + 191×136 × 48 = 1,342,892 px = 5.12 MiB | 198×234 × 48 + 49,712 = 2,273,648 px = 8.67 MiB |
| **60 (plan)** | 0.5 | 4 | 15 | 96,044 + 191×136 × 60 = 1,654,604 px = 6.31 MiB | 198×234 × 60 + 49,712 = 2,829,632 px = 10.79 MiB |
| 96 | 0.8 | 2.5 | 24 | 96,044 + 191×136 × 96 = 2,589,740 px = 9.88 MiB | 198×234 × 96 + 49,712 = 4,497,584 px = 17.16 MiB |

Here 96,044 = 198×234 + 254×195 + 13×14 (plate, shadow, lamp) and 49,712 = 254×195 + 13×14.
Every speed is the frame count over 120, so every loop is exactly 240 ticks.

**With `frame_sequence` for the holds**, only 44 different frames are needed:
14 wind-up + 2 trip + 6 fall + 1 land + 2 pawl drop-in + 1 seated with the pawl in
+ 18 wind-up = 44. A: 198×234 + 254×195 + 13×14 + 191×136 × 44 = 1,238,988 px = 4.73 MiB.
B: 198×234 × 44 + 254×195 + 13×14 = 2,088,320 px = 7.97 MiB. But see question 5.

## Now against the plan

| | Shipped | Plan |
| --- | --- | --- |
| Frames | 24 | 60 |
| Ticks a frame | 10 | 4 |
| Loop | 240 ticks, one craft | 240 ticks, one craft |
| Wind-up | 16 frames, even speed, no ease | 32 frames, eased in and out |
| Hold at the top | none | 6 frames, 24 ticks |
| Trip | inside the top frame | 2 frames of the pawl kicking clear |
| Fall | 8 frames, 80 ticks (1.33 s) | 6 frames, 24 ticks (0.4 s) |
| Last step of the fall | 23 % of the travel | 27 % of the travel |
| Seated hold | none | 13 frames, 52 ticks |
| Pawl | clear from top to seat, back in at the seat | kicks clear in 2 frames; drops back in 2 frames, during the seated hold |
| Crown still | 0 of 24 frame changes | 21 of 60 (84 ticks) |
| Accents | pawl 18, 22, 2; trip 6; drop 14 | pawl 50, 58, 6; trip 20; drop 28 |
| Frame 0 | cocked, 63 % up | cocked, 61 % up |
| Sheet (A) | 2.74 MiB | 6.31 MiB |

The biggest change is the fall. Today it takes a third of the loop and reads as a
lowering. In the plan it takes a tenth, and the time it gives back goes into two holds.
That is the foundry's pattern: slow motion, a hold, a snap, a hold.

## Recommendation

**Method A, 60 frames at speed 0.5, every frame rendered (no `frame_sequence`).**

- All the Drop Crusher's moving parts are on the roof, inside one window. B would
  re-render 60 copies of a building that does not move, to gain nothing the spec asks for.
- A costs less: 6.31 MiB against 10.79, and 9–49 % less render time.
- A keeps the still parts identical in every frame. B might make them shimmer.
- A's tools exist and passed on this building already.
- B is the right method for a building whose motion spreads over most of it, as the
  foundry's does (46 % of its pixels). The Drop Crusher moves 14 %.

This is a recommendation, not a decision. T03 is Liam's.

## Open questions for Liam

1. **Frame count.** (a) keep 24; (b) 48 at 0.4; (c) **60 at 0.5**; (d) 96 at 0.8.
   Recommend (c): 4 ticks a frame is near the foundry, and the sheet stays small.
2. **The fall's length.** The spec gives "the last third to the fall and impact".
   (a) **the third includes the seated hold**: a 6-frame fall and a 13-frame hold (the plan);
   (b) the fall takes the whole third, as now (20 frames, 80 ticks), with no hold;
   (c) between: a 10-frame fall and a 9-frame hold. Recommend (a): a fast fall reads as a drop.
3. **The holds.** A 6-frame hold at the top and a 13-frame hold on the seat: (a) **yes**;
   (b) shorter; (c) none. Recommend (a).
4. **A sound for the pawl dropping back in (36–37).** (a) **no new sound**, the five
   accents as now; (b) a new soft click, through a sound task. Recommend (a).
5. **`frame_sequence` for the holds** saves 16 frames (1.58 MiB in A). The engine docs
   do not say whether accent frames count sequence entries or sheet frames
   (`knowledge/engine.md`: not yet verified). (a) **render all 60**; (b) use a
   sequence and verify the accents in a client first. Recommend (a).
6. **Anything outside the spec:** a jolt of the building on landing, dust from the
   seat, a moving ground shadow. (a) **none**; (b) choose some, which needs a spec
   change first. Recommend (a). The spec has no dust and no smoke, and nothing burns.
7. **Stale spec text, for a later wording task.** §0 still says the plate is a draft,
   and §9 and §13 describe the old Animatorio stroke (a 48 × 54 window, 288 × 216 sheet,
   "34 × 46 px moving part"). The shipped stroke is the Blender one: 191 × 136, 24 frames.
   (a) **fix it through factorio-spec-wording when T03 is decided**; (b) leave it.
   Recommend (a). I have not touched the spec.
8. **T03.** (a) **a re-animation task for the Drop Crusher, method A, 60 frames**;
   (b) the same with method B; (c) stop here. Recommend (a).

## Wording the study proposes (not written anywhere)

For Liam to agree separately, through factorio-spec-wording.

- **knowledge/standards.md, under Buildings:** "A loop is planned as steps before it
  is modelled: each step's frames, the parts that move, their ease, and the sound it
  lands on. Every moving part holds still for part of the loop; sounds sit on starts
  and stops; the steps add up to the loop, and the loop to the recipe's ticks. (Vanilla
  foundry: each part holds 16–51 of 128 frames, and no frame is fully still.)"
- **The spec template's animation section:** add a timeline table (step, frames,
  ticks, what moves, ease, accent) and two checks: the frames add up; the loop's ticks
  equal one craft, or say why not.
