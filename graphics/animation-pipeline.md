# Animating a building, the way vanilla does it

A procedure, in order, from a filled building spec to a loaded `graphics_set`.
Follow it top to bottom. Every step says what to do, what to paste into the
generator, and what number decides whether the result is kept.

The companion documents are [building-spec-template.md](building-spec-template.md)
— Appendix A is the prompt anatomy every prompt below obeys, Appendix B is the
browser route — and [animation-layer-prompts.md](animation-layer-prompts.md),
which is the reference for each layer *type*. This is the order to do them in.

---

## What vanilla actually ships

Read off `space-age/prototypes/entity/electromagnetic-plant-pictures.lua`,
which is the fullest example in the game, and cross-checked against
`assembling-machine-3` and the three furnaces.

| Plate family | Frames | Flags | Carries |
| ------------ | -----: | ----- | ------- |
| `-base` | **1** | — | the whole static housing, **and all of its baked lighting** |
| `-base-shadow` | **1** | `draw_as_shadow` | the housing's shadow |
| `-main-<phase>` | N | — | the moving mechanism, one sheet per phase |
| `-shadow-<phase>` | N | `draw_as_shadow` | **the mechanism's own moving shadow** |
| `-lights-<phase>` | N | `draw_as_glow` | emissive, registered frame-for-frame to `-main` |
| `-frozen` | 1 | — | Aquilo only; not applicable on the Core |
| status lamp | **1** | `draw_as_glow`, `apply_tint = "status"` | the state colour |

Four things fall out of that table, and they are the whole reason this document
exists:

1. **The housing is stored once.** `assembling-machine-3` draws a 196×192 base
   with `repeat_count = 64` under a 140×160 animated layer. It never re-renders
   the machine.
2. **The moving layer has its own shadow, animated to match.** The plant ships
   `shadow-warm-up`, `shadow-rotate`, `shadow-rotate-continue` and
   `shadow-cool-down`. A part that moves and whose shadow does not is a part
   sliding over a picture of itself.
3. **The baked lighting lives in the layer that never moves.** This is the
   constraint everything else is downstream of. A specular is fixed in world
   space; if it is painted onto a surface that turns, it turns with it, which is
   backwards.
4. **States are a first-class prototype feature.** `graphics_set.states` is a
   named state machine — `idle`, `warm-up`, `working-1`, `cool-down` — with
   durations and `next_active` / `next_inactive` transitions, and each working
   visualisation is bound to states with `draw_in_states`. The electromagnetic
   plant is an `assembling-machine`, so all of it is available to us.

---

# Stage 0 — Decide the split before you generate anything

**Fill §6.2 and §7 of the spec first.** Not as paperwork: the split decides what
Stage 1's prompt has to ask for, and a plate generated without it cannot be
separated afterwards. Everything that went wrong in this repo's first attempt
went wrong here.

Write down, for this building:

* **Which parts move**, named and located. If the answer is "none", the machine
  is a furnace: one still plate plus working visualisations, and you can skip to
  Stage 6.
* **How each one moves** — and check it against the table in
  animation-layer-prompts.md Type 2. Translation, in-plane rotation and rotation
  about a part's own axis are derivable. An arm that presents a different shape
  at every angle is not, at any price.
* **What must not move.** The template asks for this and it is the line that
  stops a generator drawing a piston on a machine that has none.

---

# Stage 1 — The master plate, generated so it *can* be split

**This is where the animation is won or lost.** The plate is generated once, and
every later stage is constrained by it. A machine drawn without regard to the
split gives you a housing you cannot animate and a part you cannot move.

Add these four sections to the master prompt in §11, on top of Appendix A's
normal anatomy:

```text
== MOVING PARTS -- READ THIS BEFORE DRAWING THEM ==
[Name each part that will be animated.]

Each of those parts must be drawn so that its movement can be seen:
- It carries a feature that REPEATS around its travel: a ring of bolts across
  a wheel face, flutes or ribs along a drum, spokes, a keyway, a chain of
  links. Something a viewer can track from one frame to the next.
- Those features are HIGH CONTRAST against the part they sit on, and evenly
  spaced.
- The part is drawn COMPLETE and unoccluded: nothing overlaps it, nothing
  crops it, no pipe or bracket passes in front of it.

== LIGHTING ON MOVING PARTS ==
The moving parts carry NO baked highlight, NO specular, NO bright reflection
and NO cast shadow of their own. Light them flatly and evenly. Every
directional light in this image falls on the fixed housing only.

This is not a style preference. A highlight belongs to the lamp, not to the
metal: when the part turns, the highlight must stay where it is. Painted onto
the surface it turns with the part, which reads as the machine being lit from
a light that is spinning.

== THE FIXED HOUSING ==
Everything that is not a named moving part is the housing, and it carries all
of the scene's lighting, wear, dirt and cast shadow. Make it read as solid and
lit.

== SEPARATION ==
Draw a clear, unambiguous boundary where each moving part meets the housing:
a visible gap, a rim, a bearing collar or a change of material. No part may
blend or fade into the housing.
```

**Gate.** `tools/process-building-art.py <plate> --report` as usual — alpha
split, trimmed aspect against a vanilla comparator, body-metal luminance. Then
one extra check, on each part that is meant to move: run the row profile below
across it and look for **more than one peak**. One smooth ramp with a single
peak is a baked specular and no repeating feature, which is exactly the plate
that cannot be animated:

```bash
python3 -c "
from PIL import Image
b=Image.open('base.png').convert('RGBA'); px=b.load()
X0,X1,Y0,Y1 = 110,127,6,46          # the part, measured off the plate
for y in range(Y0,Y1):
    v=[sum(px[x,y][:3])/3 for x in range(X0,X1) if px[x,y][3]>0]
    if v: print('y%3d %5.1f %s'%(y,sum(v)/len(v),'#'*int(sum(v)/len(v)/4)))"
```

Reject and regenerate the plate here rather than discovering it at Stage 4. It
was discovered at Stage 4 once, on the Dross Classifier's drive: single peak of
141 at rows 14–17, nothing else, and no transform in the world fixes it.

---

# Stage 2 — One mask per moving part

The plate is approved and must never be regenerated. Every part is now lifted
out of it with a stencil.

**Do not ask for the part.** Asked for a component alone on transparency "at
exactly the position it occupies", the generator returns it correct and centred
on its own canvas. Ask for the whole machine with the part flooded instead —
full prompt and reasoning in animation-layer-prompts.md, Type 2.

```text
FACTORIO SPACE AGE BUILDING -- COMPONENT MASK

== SOURCE ==
The attached image is the finished, approved sprite for this machine. Return
the SAME image, at the same size, with the machine in exactly the same place in
the frame. Change ONE thing and nothing else.

== THE ONE CHANGE ==
Fill [name and locate the part] with FLAT, UNIFORM, PURE MAGENTA #FF00FF.

Flat means flat: one single colour, no shading, no gradient, no highlight, no
texture, no outline, no edge darkening. A solid silhouette of that component
and nothing more.

== EVERYTHING ELSE ==
Unchanged. Same pixels, same position, same size, same framing, same
transparent background. Do not redraw [the housing]. Do not move, rescale, crop
or re-centre the machine. Do not change any other colour anywhere.

== WHY THIS MATTERS ==
This is a segmentation mask, not artwork. The magenta region will be used to
cut that component out of the original image, so its EDGE is the only thing
that carries any value.

== FORBIDDEN ==
No magenta anywhere except on that one component. No magenta glow, spill or
fringe. No partial transparency in the magenta.

== OUTPUT ==
One image, [aspect], same aspect ratio and pixel dimensions as the attached
plate, fully transparent background, no text, no logos, no UI, no ground
texture, no background scenery, no baked drop shadow.
```

---

# Stage 3 — Cut the part out

```bash
tools/cut-part-by-mask.py --plate base.png --mask concept/vN-mask.png \
    --out part.png --housing-out housing.png --mask-out stencil.png
```

**Gate.** The tool refuses on a silhouette IoU below 0.90, on under 0.2 % keyed
and on over 60 % keyed. Read the IoU it prints: the Dross Classifier's drive
fitted at **0.9871**, and that fit is what absorbs the generator's drift — the
render arrives at a different size and re-proportioned, and the search puts its
silhouette back on the plate's.

`--housing-out` is not optional. A part that moves must not leave a second,
stationary copy of itself showing through from underneath.

---

# Stage 4 — Move it

```bash
tools/build-part-frames.py --part part.png --mode scroll --frames 12 \
    --region 106 5 130 46 --out main-rotate.png --shadow-out shadow-rotate.png
```

`--mode` is `slide`, `spin`, `ribs`, `scroll` or `shake` — pick it from Stage 0's
answer. **For a drum, use `ribs`.** It splits the region into the shading, which
is frozen, and the repeating surface feature, which is the only thing carried
round — because a barrel's light and shade belong to the lamp, not to the metal.
`scroll` moves both together and visibly lurches: measured on the Classifier's
drum, low-frequency movement across twelve frames is 23.2 under `scroll` against
6.2 under `ribs`.
`--shadow-out` gives you the `-shadow-<phase>` sheet vanilla ships alongside
every `-main-<phase>`, on its own canvas with its own shift, which the tool
prints. Use that shift.

**Gate.** The tool warns when consecutive frames come out identical — a cycle
whose frames are not distinct is a still with extra file size. Then look at it
moving, not at the sheet:

```bash
python3 -c "
from PIL import Image
im=Image.open('main-rotate.png').convert('RGBA'); hou=Image.open('housing.png').convert('RGBA')
W,H,C,N = 200,189,6,12
fs=[im.crop(((i%C)*W,(i//C)*H,(i%C+1)*W,(i//C+1)*H)) for i in range(N)]
o=[]
for f in fs:
    c=Image.new('RGBA',(W,H),(64,64,72,255)); c.alpha_composite(hou); c.alpha_composite(f)
    o.append(c.convert('RGB').resize((W*4,H*4),Image.NEAREST))
o[0].save('preview.gif',save_all=True,append_images=o[1:],duration=90,loop=0)"
```

Composite it over the housing, always. A part judged on its own looks fine and
tells you nothing about whether it reads.

---

# Stage 5 — The housing's own shadow

Not generated. `tools/process-building-art.py` derives it from the plate's alpha
by a shear measured off vanilla's lightning collector. One frame,
`draw_as_shadow`, `repeat_count = N`.

---

# Stage 6 — The glow

Only if §3.3 says the building glows. **Check that first** — the Dross
Classifier's palette ends "No glow. Dross is cold by the time it gets here",
and a lit twin of it is a spec violation however good it looks.

Type 1 in animation-layer-prompts.md has the prompt. Then:

```bash
tools/derive-glow.py --lit concept/vN-lit.png --unlit base.png \
    --out glow-plate.png --width W --height H --top-margin M
tools/build-glow-frames.py --glow glow-plate.png --out-dir graphics/entity/<b>
```

**Gate.** Normalise, measure the noise floor by round-tripping the unmodified
plate through the generator's output size, and read the result against that —
0.56 alpha drift and 3.4 % changed area on a 224×345 plate. See Type 1.

If the glow is meant to sit on a *moving* part, it must be cut with the same
stencil from Stage 3 and moved with the same transform from Stage 4, or it will
swim.

---

# Stage 7 — The status lamp

One neutral-white lens, tinted by the engine. Type 3 has the prompt, and the
`== CAMERA ==` section in it is load-bearing: without it the lamps come back as
a circle in plan view rather than an ellipse at the game's camera.

**Gate.** Channel spread under about 6. Vanilla's own lamp fails this at 62,
because vanilla paints it green and never tints it — do not calibrate against it.

---

# Stage 8 — Assemble

```lua
local ART = "__space-age-extended__/graphics/entity/<building>/"
local N = 12

derive.own_graphics(machine,
{
  animation_progress = 0.25,
  always_draw_idle_animation = true,

  -- The state machine. Durations are in frames.
  states =
  {
    { name = "idle",    duration = 1, next_active = "working", next_inactive = "idle" },
    { name = "working", duration = N, next_active = "working", next_inactive = "idle" },
  },

  -- The housing: one stored frame, drawn under everything, in every state.
  idle_animation =
  {
    layers =
    {
      { filename = ART .. "housing.png", width = W, height = H, frame_count = 1, scale = 0.5, shift = SH },
      { filename = ART .. "base-shadow.png", width = SW, height = SHH, frame_count = 1,
        draw_as_shadow = true, scale = 0.5, shift = SHADOW_SHIFT },
    }
  },

  working_visualisations =
  {
    {
      name = "mechanism",
      draw_in_states = { "working" },
      animation =
      {
        layers =
        {
          { filename = ART .. "main-rotate.png",   width = W, height = H,
            frame_count = N, line_length = 6, scale = 0.5, shift = SH },
          { filename = ART .. "shadow-rotate.png", width = SW2, height = SH2,
            frame_count = N, line_length = 6, draw_as_shadow = true,
            scale = 0.5, shift = PART_SHADOW_SHIFT },
        }
      }
    },
    {
      name = "status",
      apply_tint  = "status",
      always_draw = true,                     -- or it only draws while working
      animation = { filename = ART .. "status-lamp.png", width = LW, height = LH,
                    repeat_count = N, blend_mode = "additive", draw_as_glow = true,
                    scale = 0.5, shift = LSH },
    },
  },

  status_colors =
  {
    no_power           = { 0, 0, 0, 0 },
    idle               = { 0.25, 0.25, 0.30, 1 },
    working            = { 0.45, 0.85, 0.40, 1 },
    full_output        = { 0.95, 0.80, 0.20, 1 },   -- blocked
    insufficient_input = { 0.90, 0.35, 0.25, 1 },
    low_power          = { 0.95, 0.80, 0.20, 1 },
    disabled           = { 0.30, 0.30, 0.35, 1 },
  },
})
```

Three things that will bite:

* **`derive.own_graphics`, not `p.graphics_set = ...`.** Vanilla's
  `working_sound` accents name the vanilla animations they are cued to, and a
  machine that replaces its graphics set while keeping them refuses to load:
  `Working visualisation "warm-up" doesn't exist`. The helper strips the accents
  and the gated `main_sounds`.
* **`always_draw = true` on the status lamp.** Without it the lamp draws only
  while working, which is the one state that needed no lamp.
* **A misspelled state name in `status_colors` is silently ignored.**
  `full_ouput` passes `check-data-stage.sh` and simply never lights. The eight
  the engine reads are `no_power`, `idle`, `no_minable_resources`,
  `insufficient_input`, `full_output`, `disabled`, `working`, `low_power` —
  probed on 2.1.17 against both `assembling-machine` and `furnace`.

---

# Stage 9 — The checks, in order

```bash
tools/check-graphics.sh        # every path the mod names exists
tools/check-data-stage.sh      # it loads alongside base and space-age
tools/check-footprint.py --tiles N <plate>
```

Then in game, and this is the only one that catches the real failures: build
two of them side by side, run one and starve the other, and watch. A machine
that reads as working when it is blocked has passed every check above.
