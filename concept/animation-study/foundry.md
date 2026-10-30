# The foundry, frame by frame (animation study, T01)

A study of how vanilla's foundry animation is built and timed. It is for Liam to
judge. Nothing here is signed off, and nothing in the mod changes.

- **Timeline sheet:** `concept/animation-study/foundry-timeline.png` (2704 × 1324).
- **Part regions:** `concept/animation-study/foundry-parts.png`.
- **Every figure:** `concept/animation-study/foundry-figures.json`.
- **Script:** `concept/animation-study/foundry_study.py`. It reads only the game's files.
  Run it again and it writes the same three files, byte for byte.
- **Crops I named the parts from:** `evidence/animation-study/crops/`.

## How it was measured

- The script cuts the 128 frames out of `foundry-anim-1.png` and `-2.png`.
- For each frame it counts the pixels whose colour changes by more than 12 levels
  before the next frame. I call that the **motion energy**. It is a stand-in for
  speed, not a distance. A part that moves faster changes more pixels.
- I drew six boxes round the parts that move (see the parts image). The script
  measures each box separately. A part counts as **moving** on a frame when its
  energy is over a quarter of its own peak.
- **Eases** come from the shape of each motion's energy: how high it starts and
  how high it ends, against its peak. "Slow in" starts under 45 % of the peak.
  "Snap" is a motion of 6 frames or fewer.
- **I chose the steps and the box edges by eye.** The script checks them against
  the data. It reports the nearest part start or stop to each step's first frame
  (0, −4, +6, +1, −1, 0, 0 frames).

## Timing

- 128 frames at `animation_speed` 0.16, crafting speed 4, progress 0.5.
- **Sum:** 128 / (0.16 × 4 × 0.5) = **400 ticks a loop**, 6.67 s.
- That is 0.32 frames a tick: one frame every 3.125 ticks, 19.2 frames a second.
- The loop is not one craft. It runs at the machine's rate while it works.

## What moves

| Part | What it is | When it moves (frames) | Ease | Longest hold |
| --- | --- | --- | --- | --- |
| head | hatch on top of the tower | 118–30, 78–103 (and a 3-frame flick at 60–62) | medium in and out; slow out on opening | 29 frames by the threshold; truly still only about 68–74 (see limits) |
| launder | red trough telescoping out on the west | 12–43 out, 76–103 back | slow in going out; slow out coming back | 36 frames |
| arm | red pouring hood that comes down on the crucible | 8–48 down, 72–105 up | slow in going down; slow out going up | 30 frames |
| crucible | sinks into its pit, rises, tips and pours | 5–54, 71–120 | medium in, slow out; then slow in, slow out | 16 frames |
| moulds | cast boxes round the tower's foot | 1–7, 25–99, 101–103 | medium; even through the long run | 25 frames |
| flap | pale ejector plate, north-west | 51–72 (drifts back, near the threshold), 118–123 (kicks out), 125–127 (bounce) | even speed on the return; snaps out | 51 frames |

- **46.4 %** of the drawn pixels change at some point in the loop. The task file
  quotes 48 % from the earlier research, measured with a different threshold.
- **No frame is ever still.** All 128 frame changes move something.
- The quietest change is frame 123 to 124: 1062 pixels, **1.0 %** of the building.
- The busiest is frame 84 to 85: 11,340 pixels, **11.1 %** of the building.

## The loop in seven steps

Every frame 0 to 127 is in exactly one step. **Sum:** 16 + 22 + 10 + 26 + 26 + 18 + 10 = **128**.

| # | Step | Frames | Length | Moves | Holds | Sound accents |
| - | ---- | ------ | ------ | ----- | ----- | ------------- |
| 1 | Reset | 0–15 | 16 | crucible rights itself after the pour; arm starts down slowly; hatch closing | flap | 2 pipe-out |
| 2 | Close and lower | 16–37 | 22 | launder slides out; arm comes down; crucible sinks; hatch closes; moulds start | flap | 18 slide-close |
| 3 | Clamp | 38–47 | 10 | arm locks onto the crucible; launder reaches its stop | hatch, flap | 39 clamp, 43 slide-stop |
| 4 | Charge (hold) | 48–73 | 26 | moulds turn, gathering speed; flap drifts back slowly | launder; arm from 49 to 71; the hatch mostly (it creeps until about 67, below the threshold, and flicks at 60–62) | 64 fire-whoosh + metal-clunk |
| 5 | Open and raise | 74–99 | 26 | arm lifts; launder runs back; hatch opens; crucible climbs; moulds finish | flap | 74 slide-open |
| 6 | Tip and pour | 100–117 | 18 | crucible tips forward and pours | flap | 106 pipe-in + smoke-puff, 110 pour |
| 7 | Eject | 118–127 | 10 | flap snaps out and bounces; rocks drop; hatch starts to close | launder, arm, moulds | 120 rocks, 126 blade |

### Every accent, matched to a step

The game declares **12 accents on 10 frames** (`entities.lua`, the foundry's
`sound_accents`). The task file lists 10. It misses the second accent on 64 and the
pour on 110. All 12 are matched here. None is on frame 0.

| Frame | Sound | Step | What it lands on (measured) |
| ----- | ----- | ---- | --------------------------- |
| 2 | pipe-out | 1 Reset | the moulds' short step (1–7) starts; the top puff of smoke starts on 4 |
| 18 | slide-close | 2 Close and lower | launder is sliding out (from 12); hatch closing |
| 39 | clamp | 3 Clamp | arm reaches the crucible (its motion ends on 48) |
| 43 | slide-stop | 3 Clamp | **the launder stops on 43**, the exact frame |
| 64 | fire-whoosh | 4 Charge | the middle of the hold; light is swelling back |
| 64 | metal-clunk | 4 Charge | the same frame; two sounds give the hold its event |
| 74 | slide-open | 5 Open and raise | arm starts up on 72, launder on 76, hatch on 78 |
| 106 | pipe-in | 6 Tip and pour | arm, launder and hatch have just stopped (103–105) |
| 106 | smoke-puff | 6 Tip and pour | the west smoke puff shows from 110 |
| 110 | pour | 6 Tip and pour | crucible tipping |
| 120 | rocks | 7 Eject | **the crucible stops on 120**; the flap is out (118–123) |
| 126 | blade | 7 Eject | the flap's bounce (125–127) |

**The pattern:** accents mostly sit on starts and stops. There are three exceptions:
18 lands in the middle of the launder's slide, 64 marks the middle of the longest hold,
and 110 lands in the middle of the crucible's tip.

## What the lights and smoke add

- **Lights** (`foundry-lights`, 380 × 326, 128 frames, additive, `draw_as_glow`,
  `flicker`, fades out when the machine stops). They follow the hatch.
  - Brightest on frame 2 (10,912 lit pixels). Dimmest on frame 40 (3,865): **35 %**
    of the peak, as the hatch shuts and the arm clamps.
  - They swell back during the hold (about 6,800 by frame 52), dip again near 76,
    then come up hard from 84 to 92 as the hatch opens, and stay high through the pour.
  - So the glow is a second timeline. It breathes slowly under the fast parts.
- **Smoke** (three 128-frame layers, all fade out when the machine stops):
  - `smoke_1` (204 × 168, east, by the crucible): never off. It swells twice, near
    24–36 and 76–88, while the big parts move.
  - `smoke_2` (98 × 160, west): one puff. It shows from 110, four frames after the
    smoke-puff accent, peaks on 14, then thins out over almost the whole loop.
  - `smoke_3` (58 × 62, on top): a small puff from 4 to 35, peaking on 23.
  - A fourth smoke, the chimney, is vanilla's chemical-plant smoke at constant speed.
    It does not follow the loop.
- **Status lamp:** one frame, repeated. It never moves.
- **Shadow:** one frame, repeated 128 times. **The shadow does not move.**
- **The west pipe picture is animated** (128 frames of 44 × 190), because moving parts
  pass it. The other three pipe pictures are one frame.

## How the stills hold the eye

- Nothing ever stops completely. But **every part rests for a long time**: 16 to 51
  frames each by the threshold, out of 128. (The head's 29 is mostly a slow creep; see limits.)
- **One big motion leads at a time.** The launder and arm go out together, then
  hold. The crucible rises, then tips. The flap kicks last.
- **Motions overlap at their ends.** The launder stops on 43, the arm on 48, the
  crucible on 54. Each one settles while the next is already going. Nothing stops
  on the same frame as everything else.
- **The long hold is never dead.** In step 4 the arm and launder are still and the
  hatch nearly so. Meanwhile the moulds turn and gather speed (their motion energy rises
  from 2,783 to 3,617 changed pixels a frame across the hold), the flap drifts back, the
  light swells back, and a sound lands in the middle (64).
- **Snaps come after slow motions.** The flap's 6-frame kick (118–123) follows the
  crucible's slow tip. The contrast is what makes it read.

## Sheet budget

Raw RGBA, 4 bytes a pixel, before the engine packs its atlases. I have not checked
what the engine's own packing and sprite compression do to this.

| Sheet | Size | Files | Raw RGBA |
| ----- | ---- | ----- | -------- |
| anim (the building, 128 frames) | 2704 × 2832 | 2 | 58.4 MiB |
| lights (128 frames) | 3040 × 2608 | 2 | 60.5 MiB |
| smoke_1, smoke_2, smoke_3 (128 frames each) | 1632 × 2688, 784 × 2560, 464 × 992 | 3 | 26.2 MiB |
| west pipe (128 frames) | 1408 × 760 | 1 | 4.1 MiB |
| base, shadow, status lamp, other pipes | one frame each | 6 | 1.1 MiB |

- **Sum (working sheets):** 2704×2832 + 2704×2832 + 356×384 + 3040×2608 + 3040×2608
  + 18×190 + 176×50 + 188×68 + 1408×760 + 514×214 + 1632×2688 + 784×2560 + 464×992
  + 122×142 = 39,385,348 px × 4 B = **150.2 MiB**.
- With the frozen, remnant and reflection sheets: **151.8 MiB**. All 21 files are
  29.2 MiB on disk.
- The building's own frames are **38.9 %** of the working budget. The glow is as big
  as the building.
- **The foundry is not quite "the whole building every frame".** A one-frame base
  sits under the anim layer. Only **13.5 %** of the base's pixels are ever seen
  (11,391 of 84,533): its outer rim. The anim layer is 338 × 354 and is the building.

## What this means for us (input to T02)

1. Holds matter as much as motion. Each part rests for a quarter of the loop or more.
2. Accents mostly go on starts and stops; a few go inside a motion or the long hold.
3. Light gets its own slow curve, under the fast parts.
4. The frame rate is high: about 19 frames a second at the foundry's speed.
5. The shadow stays still, even on a building where half the pixels move.

## Limits of this study

- **Some holds sit at the threshold.** A part counts as moving when its energy is over a
  quarter of its own peak. The head's energy from 31 to 65 is about 200 changed pixels a
  frame, 21 % of its peak (937): just under the line. So its "longest hold, 29 frames"
  is overstated: it creeps through most of that, and is truly still only about 68–74.
  The flap's drift (51–72) and the head's flick (60–62) sit just over the line in the
  same way. The steps and accents do not depend on these edges.

- Motion energy is a stand-in for speed. A part that changes colour as it moves
  (light falling across it) can read as moving faster than it is.
- Some boxes overlap a little (the arm comes down into the crucible's box). The
  timeline shows the arm and the crucible running together near 40–48 for that reason.
- The names of the parts are mine. Wube has not published what each part is.
