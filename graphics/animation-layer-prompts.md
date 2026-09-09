# Animation layer prompts — getting frames out of an approved base plate

How a building that already has an approved `base.png` gets the rest of its
graphics set: the working glow, the moving parts, the status lamp, the effect
plume, the idle overlay.

This is a companion to [building-spec-template.md](building-spec-template.md),
not a replacement. Its Appendix A (prompt anatomy), B (browser generation) and
C (production pipeline) apply to every prompt below and are not repeated —
read them first. The templates here fill the `### Working Machinery`,
`### Glow / Lighting` and `### Effects` headings of a spec's §11, which is
where `tools/generate-building-art.py` looks for them, plus two the template
does not currently have headings for.

---

## The rule: ask for states, never for frames

**A generator cannot hold a machine still while changing it.** This is the most
expensive lesson in the repository and three separate tools carry it in their
docstrings — `cut-plate-from-sheet.py` ("an image generator can change a design
or change a presentation; it cannot hold one still while changing the other"),
`derive-glow.py` ("ask one for 'just the light' and it invents geometry that
does not line up"), `build-glow-frames.py` ("generating 19 whole buildings would
let the geometry drift; a mask cannot").

Measured on a 28-frame sheet of one machine, 7×4, generated as complete renders:

| | frames | body pixels essentially constant across the sequence |
| - | -: | -: |
| Generated sheet, plume-free lower body, bbox-aligned | 28 | **9.2 %** |
| Vanilla `assembling-machine-3` | 64 | **40.2 %** |

Nine per cent. Every rivet, panel line and highlight was re-invented on every
frame, and the sheet also came back with no usable grid — irregular seams, no
transparent gutters, adjacent plumes bleeding across the cut, and an 11 px
vertical registration break between row 3 and row 4.

Vanilla does not work this way, and neither can we:

* **`assembling-machine-3`** stores its housing **once** — `base` is 196×192,
  `line_length = 1`, drawn with `repeat_count = 64` — and animates only a
  140×160 `anim` layer over it. The status light is likewise one 36×44 frame at
  `repeat_count = 64`.
* **Every furnace** (stone, steel, electric) goes further: `graphics_set.animation`
  is a **single still image** plus a shadow, with no `frame_count` at all. All
  the motion lives in `working_visualisations`.

So the generator is asked for **one more render per state** — a lit twin, a
part, a plume — always registered against the plate that was already approved.
The *frames* are then derived mechanically, by tools that cannot drift.

---

## The five types

| # | Type | Generated? | Frames it becomes | Prototype slot |
| - | ---- | ---------- | ----------------- | -------------- |
| 1 | **Lit twin** — the whole machine, working | Yes, as an edit of `base.png` | N, by mask | `working_visualisations[].animation` |
| 2 | **Moving part** — a piston, drum, fan, belt | As a *mask*, not as art | N, by transform | `graphics_set.animation` layer |
| 3 | **Status lamp** — one neutral lamp | Yes, tiny, once | 1, `repeat_count = N` | `working_visualisations[]` + `status_colors` |
| 4 | **Effect** — plume, dust, discharge | Yes, alone on transparency | N, by mask | `working_visualisations[]`, `fadeout = true` |
| 5 | **Idle overlay** — body drawn under both states | Rarely; usually `base.png` itself | 1 | `idle_animation` + `always_draw_idle_animation` |

The shadow is never generated. `tools/process-building-art.py` derives it from
the plate's own alpha.

---

## Before you write any of them: is this type applicable?

Found by trying to run all five against real buildings in the tree. Three of
the five turned out not to apply to the building they were first aimed at, and
none of the three failures is visible from the template alone.

**Type 1 needs the building to glow.** Check §3.3 first. The Dross Classifier's
palette section ends *"**No glow.** Dross is cold by the time it gets here — it
is what settled out."* A lit twin of that machine is a spec violation however
good the plate is, and the prompt would have got one anyway, because the
generator has no way to know. If §3.3 says no glow, write `Not required — see
§3.3` and stop.

**Type 3 needs the lamp to already exist on the plate.** The template says
"locate it", which quietly assumes there is something to locate. The Dross
Classifier has no indicator lens anywhere on `base.png`, and an *edit* cannot
add one — asking for it is asking the generator to invent geometry, which is
the failure mode this whole document is built to avoid. A building that wants a
status lamp it does not have needs the lamp in the **base plate**, added at
plate-cut time and then isolated by Type 3; or drawn separately and positioned
by hand against measured coordinates.

**Type 2 must pass its own table before it gets a prompt.** The Dross
Classifier's one moving part is the eccentric flywheel, and it turns about a
horizontal axle seen three-quarters on — out of the view plane, which the
table in Type 2 marks **No**. The honest layer for that machine is not a
generated part at all: the whole housing rides on leaf springs, so the working
animation is `base.png` itself translated a pixel or two on a cycle, derived by
transform with nothing generated. Run the table before writing the prompt, not
after.

**Type 5 has no run, by design.** It is `base.png`. If a filled spec has
anything else under it, something has gone wrong.

The general shape: **three of the five types are edits of an approved plate,
and an edit can only ever subtract or relight.** Anything the layer needs that
is not already in `base.png` has to get there at plate-cut time.

---

# Type 1 — Lit twin (working glow)

The default for this mod. Almost every building here is a box that glows when
it runs, which is the furnace pattern, and the furnace pattern is one still
body plus a `working_visualisation`.

**It is an edit, not a generation.** Attach the approved `base.png` and ask for
the same machine with its light on. Asking for "the glow only" produces
geometry that does not register — that is `derive-glow.py`'s opening paragraph,
and it cost six pixels of offset the first time.

### Prompt

```text
FACTORIO SPACE AGE BUILDING -- LIT TWIN OF AN APPROVED PLATE

== SOURCE ==
The attached image is the finished, approved sprite for this machine. Return
the SAME machine with its working light on. Do not redesign it. Do not move,
rescale, re-pose or re-detail any part of it. Every rivet, panel seam, pipe run
and edge must land on the same pixel it lands on now.

== CAMERA ==
Unchanged from the attached image. Viewed from the game's characteristic
45-degree top-down perspective, square to the tile grid.

== WHAT CHANGES ==
Only emitted light, and only in these places:
- [where the light comes from, one bullet each, named by the part it sits on]
- [e.g. "the three inspection ports on the front face"]
- [e.g. "the seam between the drum and the frame"]

== LIGHT ==
- Colour: [#HEX], brightening to [#HEX] at the hottest cores
- The light spills onto the metal immediately around each source and falls off
  within [N] pixels. It does not wash the whole machine.
- No bloom past the silhouette. No lens flare, no starburst, no glare disc.

== WHAT DOES NOT CHANGE ==
- The silhouette, in every particular.
- The unlit metal: same colour, same value, same wear. If a surface is not
  next to a light source it is byte-for-byte what it was.
- The background stays fully transparent.

== FORBIDDEN ==
[Name the wrong object the lit version could collapse into. On the Core:
"must not read as a furnace or a fire -- nothing burns on this world, there is
no atmosphere and no combustion. The light is electrical."]

== OUTPUT ==
One image, same aspect ratio as the attached plate, transparent background,
no text, no logos, no UI, no ground texture, no background scenery,
no baked drop shadow.
```

### Accept or reject

Reject on the numbers, not on the look — Appendix B is explicit that eyeballing
a transparent plate over a viewer's background produced two confident and
completely wrong findings.

```bash
python3 - <<'EOF'
from PIL import Image, ImageChops, ImageStat
lit = Image.open('concept/vN-lit.png').convert('RGBA')
unl = Image.open('graphics/entity/<building>/base.png').convert('RGBA')
assert lit.size == unl.size, ('size changed', lit.size, unl.size)
# The silhouette must be the same silhouette.
a = ImageChops.difference(lit.getchannel('A'), unl.getchannel('A'))
print('alpha drift: mean %.2f  max %d' % (ImageStat.Stat(a).mean[0], a.getextrema()[1]))
# The machine must not have moved.
d = ImageChops.difference(lit.convert('RGB'), unl.convert('RGB'))
changed = d.convert('L').point(lambda v: 255 if v > 8 else 0)
print('lit area: %.1f%% of pixels changed by more than 8'
      % (100 * ImageStat.Stat(changed).mean[0] / 255))
EOF
```

**Two things this needs that the first draft of it did not say**, both found by
running it:

1. **Normalise first.** The result does not come back at the plate's size — a
   1024×1536 or 1254×1254 canvas is what you get, whatever the prompt asked
   for. Trim both images to their own alpha bbox and scale the result to the
   plate's before differencing, or run it through
   `tools/process-building-art.py` first.
2. **Measure the noise floor, don't guess a threshold.** That rescale changes
   every edge by itself. Round-trip the *unmodified* plate through the
   generator's output size and back, run the same numbers, and read the real
   measurement against that:

   ```python
   rt = plate.resize((1024, 1536), Image.LANCZOS).resize(plate.size, Image.LANCZOS)
   ```

   Measured on the arc mast's 224×345 plate the floor is **alpha drift 0.56,
   changed area 3.4 %**. Anything near those numbers is the resample, not the
   generator.

**Pass:** alpha drift within about twice the floor, and the changed area
confined to the regions the prompt named. **Fail:** alpha drift an order of
magnitude over the floor — it re-proportioned the machine, and `derive-glow.py`
will land the result off-register, which is the exact bug that tool's docstring
records. Check the **trimmed aspect** of both while you are there; a few per
cent of drift there is the same defect stated more legibly.

Say *regenerate* rather than *edit* when the silhouette is wrong; an edit
preserves the shape being rejected.

Watch for the null result too: the superconducting store's lit twin came back
pixel-identical five rounds running, re-encoded each time so the file size
moved while the pixels did not. `ImageChops.difference` catches it; file size
does not.

### Turning it into frames

```bash
tools/derive-glow.py --lit concept/vN-lit.png --unlit graphics/entity/<b>/base.png \
    --out graphics/entity/<b>/glow-plate.png --width W --height H --top-margin M
tools/build-glow-frames.py --glow graphics/entity/<b>/glow-plate.png \
    --out-dir graphics/entity/<b>
```

If the twin came back identical, `tools/split-glow.py` separates a single lit
render into base and glow by colour instead — one render, no twin needed.

---

# Type 2 — Moving part

**Read this before writing the prompt: most moving parts should not be
generated at all.**

`tools/build-crane-sheets.py` is kept in the tree purely as the record of this
going wrong. Stamping one drawing into every frame of a rotating part gives an
arm whose segments never change as they swing and which draws a segment at
angles where vanilla draws none — "the crane arm is all messed up". Anything
that rotates **out of the view plane** needs a 3D model or a recolour of
vanilla's sheet; `tools/recolour-crane.py` is what that looks like.

What *is* derivable from one drawing is motion that stays in the view plane:

| Motion | Derivable from one plate? | How |
| ------ | ------------------------- | --- |
| Piston, ram, shuttle | Yes | translate along its axis |
| Wheel or fan seen face-on | Yes | rotate about the view axis |
| Belt, chain, conveyor | Yes | scroll a masked strip |
| Light travelling along a run | Yes | `build-glow-frames.py` |
| Drum, turntable, arm swinging | **No** | 3D model, or recolour vanilla |

### Do not ask for the part. Ask for a mask of it.

**The obvious prompt does not work, and it was tried.** "Draw the component by
itself, on transparency, at exactly the size and position it occupies" returns
the component correct in every particular and **centred on its own canvas**.
Measured on the Dross Classifier's drive: it came back at x 0.28–0.76, y
0.20–0.58 of a square canvas, where on the plate it sits up at the top of the
roofline. The art was fine. Nothing in the file said where it went, and the
prompt had asked in as many words.

That is the general result: the generator is reliable about *what* to draw and
unreliable about *where* to put it. So ask it only for the *what* — **which
pixels** — and do the *where* yourself.

The prompt therefore returns the **whole machine, unmoved**, with the one
component flooded in flat magenta. The magenta is a stencil, and
`tools/cut-part-by-mask.py` fits it to the plate and cuts the part out of
`base.png` with it. Every pixel that ships is the approved pixel; the generator
never draws anything that survives into the game.

Magenta because §11 of the template already picked `#FF00FF` as the key colour
for this mod, *"chosen because it appears nowhere on the building"*.

### Prompt

```text
FACTORIO SPACE AGE BUILDING -- COMPONENT MASK

== SOURCE ==
The attached image is the finished, approved sprite for this machine. Return
the SAME image, at the same size, with the machine in exactly the same place in
the frame. Change ONE thing and nothing else.

== THE ONE CHANGE ==
Fill [name and locate the component: "the eccentric drive assembly -- the dark
offset flywheel and its copper-banded hub, on the raised pedestal at the high
end of the roofline"] with FLAT, UNIFORM, PURE MAGENTA #FF00FF.

Flat means flat: one single colour, no shading, no gradient, no highlight, no
texture, no outline, no edge darkening. A solid silhouette of that component
and nothing more.

== EVERYTHING ELSE ==
Unchanged. Same pixels, same position, same size, same framing, same
transparent background. Do not redraw [the housing, the springs, the bins].
Do not move, rescale, crop or re-centre the machine. Do not change any other
colour anywhere in the image.

== WHY THIS MATTERS ==
This is a segmentation mask, not artwork. The magenta region will be used to
cut that component out of the original image, so its EDGE is the only thing
that carries any value: it must follow the true outline of [the part] exactly,
including where it passes behind [the housing].

== FORBIDDEN ==
No magenta anywhere except on that one component. No magenta glow, no magenta
spill, no magenta fringe, no magenta on [the pedestal or the roofline]. No
partial transparency in the magenta.

== OUTPUT ==
One image, [aspect], same aspect ratio and pixel dimensions as the attached
plate, fully transparent background, no text, no logos, no UI, no ground
texture, no background scenery, no baked drop shadow.
```

### Accept or reject

`tools/cut-part-by-mask.py` gates it for you and refuses three ways: a
silhouette IoU below `--min-iou` (it returned a different shape, not a recolour
of this one), a keyed region under 0.2 % (nothing was flooded — check the key
colour), and one over 60 % (it flooded the machine, not a component).

Measured on the Dross Classifier's drive, first attempt: **silhouette IoU
0.9871**, keyed region **5.9 %** of the machine, and the cut part landing at
(77, 5)–(131, 49) on a 200×189 plate — the top of the roofline, which is where
the drive is. The fit is what absorbs the generator's drift: the render came
back at 1254×1254 and re-proportioned, and the search found the scale and offset
that put its silhouette back on the plate's to within 1.3 %.

**What it does not fix.** The flooded edge is approximate — the generator paints
a rough silhouette, so the stencil ran a little wide into the roofline above the
drive. That matters less than it looks, and the reason is worth knowing:

* **The housing layer stays whole.** In the layered prototype `base.png` is
  drawn complete underneath, so an over-wide stencil paints identical pixels
  back over themselves and is invisible.
* **It only matters where the part moves off its own hole.** A wheel rotating
  about its centre covers the same disc in every frame, so the hole never shows
  and the edge can be sloppy. A piston that *translates* exposes what was behind
  it, and there the housing has to be repainted behind the part by hand — which
  is a plate-cut job, not a prompt.

### Getting it moving

`tools/build-part-frames.py`. It takes the cut part on the plate's canvas and
writes the sheet, and because every frame is the same pixels under a different
transform, nothing can drift.

```bash
tools/cut-part-by-mask.py --plate base.png --mask concept/vN-mask.png \
    --out part.png --housing-out housing.png
tools/build-part-frames.py --part part.png --mode spin --frames 16 --out drive.png
```

`--housing-out` matters: a part that moves must not leave a second, stationary
copy of itself showing through from underneath, so the static layer is the plate
**with the part removed**, not the plate.

Three modes, and the fourth case that is not one:

| `--mode` | For | Cycle |
| -------- | --- | ----- |
| `slide` | a piston, ram or shuttle along its axis | sine, so it returns |
| `spin` | a wheel or fan whose face is toward the camera | full turn about a measured centroid |
| `shake` | the whole machine oscillating on its mounts | sine plus a perpendicular at twice the rate — a figure of eight, because a straight line reads as the sprite sliding rather than the machine shaking |
| *(none)* | **a drum, turntable or arm turning out of the view plane** | **there isn't one** |

**The last row, demonstrated.** `spin` was run on the Dross Classifier's drive
— a three-quarter-view drum — and the result is a barrel tumbling end over end,
because rotating a picture of a cylinder in the image plane rotates its
highlights and its foreshortening with it. It reads as a sticker on a
turntable, which is `build-crane-sheets.py`'s finding arrived at from the other
direction. **`spin` is only honest when the axis points at the camera.**

**There is no free shift.** `animated_shift` on a working visualisation is
parsed by a crafting machine, but what it follows is
`shift_animation_waypoints`, which is a `MiningDrillPrototype` field — probed on
2.1.17, an assembling machine silently ignores it on both `graphics_set` and the
prototype root. A machine that moves costs frames.

That is worth stating plainly because `shake` breaks this document's own rule:
it stores the whole plate once per frame. The rule stands for everything else,
and `shake` is the exception that has no alternative — measured at 8 frames of a
200×189 plate it costs 91 KB, which is the right trade for a building whose
entire read is that it is vibrating. Keep the frame count low; the offsets are
integers and a two-pixel amplitude only has so many distinct positions in it
(the tool warns when consecutive frames come out identical).

### Wiring it up

```lua
graphics_set = {
  animation = {
    layers = {
      { filename = ART .. "housing.png", repeat_count = N, ... },  -- part removed
      { filename = ART .. "drive.png",   frame_count  = N, ... },  -- the motion
      { filename = ART .. "base-shadow.png", repeat_count = N, draw_as_shadow = true, ... },
    }
  }
}
```

`repeat_count` on the housing is the whole trick: it is one stored frame. For
`shake` there is no part layer at all — the shake sheet *is* the animation, and
the shadow wants shaking with it or the machine reads as sliding over its own
shadow.

---

# Type 3 — Status lamp

The cheapest state read in the game and this mod uses it nowhere yet.

**Measured against 2.1.17, not assumed.** `graphics_set.status_colors` is
parsed by both `assembling-machine` and `furnace` — an invalid colour value
errors, an unknown state name is silently ignored, and probing each name that
way enumerates the set the engine actually reads:

```
no_power   idle   no_minable_resources   insufficient_input
full_output   disabled   working   low_power
```

`apply_tint = "status"` is likewise validated on a crafting machine's working
visualisation. No vanilla crafting machine uses either — only the mining drill
does — so a blocked vanilla assembler is pixel-identical to an idle one. Ours
need not be.

**The lamp is generated once, neutral, so the engine can tint it.** A lamp
drawn green cannot be tinted red.

### Prompt

```text
FACTORIO SPACE AGE BUILDING -- STATUS LAMP

== SOURCE ==
The attached image is the finished, approved sprite for this machine. Draw ONE
small indicator lamp from it, by itself, on a fully transparent background, at
exactly the size and position it occupies in the attached image.

== THE LAMP ==
[Locate it: "the round lens on the left shoulder of the housing".]

== CAMERA ==
Unchanged from the attached image. Viewed from the game's characteristic
45-degree top-down perspective, square to the tile grid. [If the lamps run
around something round, say so explicitly: "a ring of lamps around a dome is
therefore an ELLIPSE, wider than it is tall, not a circle seen from directly
above."]

== COLOUR -- THIS IS THE IMPORTANT PART ==
The lens is NEUTRAL WHITE, #FFFFFF at its centre, falling to a soft neutral
grey at its rim. It has NO hue at all -- not green, not amber, not blue. The
game colours it at runtime and a lens drawn in any colour cannot be recoloured.

== FORM ==
- A lit lens only: the glass and the light in it.
- No bezel, no housing, no metal surround, no screws.
- Soft falloff of no more than [N] pixels past the lens edge.

== FORBIDDEN ==
No machine, no panel, no ground, no shadow, no coloured light of any kind.

== OUTPUT ==
One image, same aspect ratio and pixel dimensions as the attached plate,
fully transparent background, no text, no logos, no UI, no ground texture,
no background scenery, no baked drop shadow.
```

### Accept or reject

```bash
python3 -c "
from PIL import Image, ImageStat
im = Image.open('concept/vN-lamp.png').convert('RGBA')
r,g,b = ImageStat.Stat(im.convert('RGB'), im.getchannel('A')).mean[:3]
print('lit-mean RGB %.0f %.0f %.0f  -- spread %.1f (want < 6)' % (r,g,b, max(r,g,b)-min(r,g,b)))"
```

A channel spread over ~6 means it has a hue and the tint will fight it.

**Do not calibrate this against vanilla's own lamp.** Run the check on
`assembling-machine-3-status-light.png` and it fails: mean RGB 2/12/1, a spread
of 11.2 — it is painted green, because vanilla never tints it. Copying that
plate and adding `apply_tint = "status"` gives a lamp that is green plus the
status colour in every state, and a red "blocked" that reads as murky yellow.

### Wiring it up

```lua
graphics_set.status_colors =
{
  no_power    = { 0, 0, 0, 0 },       -- drawn as nothing
  idle        = { 0.25, 0.25, 0.30, 1 },
  working     = { 0.45, 0.85, 0.40, 1 },
  full_output = { 0.95, 0.80, 0.20, 1 },   -- blocked
  insufficient_input = { 0.90, 0.35, 0.25, 1 },
  low_power   = { 0.95, 0.80, 0.20, 1 },
  disabled    = { 0.30, 0.30, 0.35, 1 },
}
graphics_set.working_visualisations =
{
  {
    apply_tint  = "status",
    always_draw = true,        -- required, or it only draws while working
    animation   = { filename = ART .. "status-lamp.png", repeat_count = N,
                    blend_mode = "additive", draw_as_glow = true, ... },
  }
}
```

`always_draw = true` is not optional — without it the lamp is drawn only in the
working state, which is the one state that needed no lamp. And mind that a
misspelled state name costs nothing at load and simply never lights:
`full_ouput` will pass `check-data-stage.sh` in silence.

---

# Type 4 — Effect (plume, dust, discharge)

The one type where a multi-frame generation is legitimate, because the effect
has no fixed geometry to drift — a plume that differs every frame is a plume
behaving correctly.

It still may not contain the machine. Generate the effect **alone**, on
transparency, and composite it as its own working visualisation.

**On the Core, read §10 of the building's spec before writing this prompt.**
Nothing burns here and there is no atmosphere: `building-spec-radiant-generator.md`
calls a steam engine "the single most wrong object" for exactly this reason, and
a steam plume is the same mistake in a smaller frame. Vented gas in vacuum
disperses in a cone and vanishes; it does not billow.

### Prompt

```text
FACTORIO SPACE AGE BUILDING -- EFFECT PLATE, [N] FRAMES

== SUBJECT ==
[The effect, in one clause: "a thin cone of vented gas flashing to vapour".]
Nothing else is in frame. No machine, no metal, no ground, no horizon.

== LAYOUT ==
One image, a grid of [C] columns by [R] rows, [N] cells used. Cells are equal
size and evenly spaced, with clear empty margins between them so they can be
cut apart. No cell's content may cross into a neighbouring cell.

== SEQUENCE ==
Read left to right, top to bottom, as consecutive moments of one event:
- Cell 1: [what it looks like at the start]
- Cells 2 to [k]: [how it grows]
- Cells [k+1] to [N]: [how it disperses]
- Cell [N] leads back into cell 1 with no visible jump.

== ANCHOR ==
The effect issues from the SAME point in every cell: [x] across and [y] down
within its cell. It does not wander between frames.

== APPEARANCE ==
- Colour: [#HEX] at the source, fading to [#HEX] and to nothing at the edges.
- [Density, direction, spread angle.]

== FORBIDDEN ==
[The wrong physics: "must not read as smoke or steam -- this is vacuum, so it
disperses in a straight cone and vanishes. No billowing, no curling, no soot,
no fire, no sparks."]

== OUTPUT ==
[Aspect], fully transparent background, no text, no logos, no UI, no ground
texture, no background scenery, no baked drop shadow.
```

### Accept or reject

The grid is what fails. Check it before anything else, because a sheet with no
gutters cannot be cut at all:

```bash
python3 -c "
from PIL import Image
im = Image.open('concept/vN-effect.png').convert('RGBA'); a = im.getchannel('A')
w,h = a.size; px = a.load()
col = [sum(px[x,y] for y in range(h)) for x in range(w)]
gaps = sum(1 for v in col if v == 0)
print('fully transparent columns: %d of %d' % (gaps, w))
print('-> if this is ~0 the frames touch and the sheet cannot be cut')"
```

Then cut on the measured gutters, not on `width / columns` — the generator will
not have used an even pitch.

### Wiring it up

```lua
{
  fadeout = true,          -- eases out when the machine stops, rather than cutting
  animation = { filename = ART .. "effect.png", width = W, height = H,
                frame_count = N, line_length = C, animation_speed = S,
                draw_as_glow = false, ... },
}
```

`fadeout = true` is what every vanilla furnace uses and is the difference
between a machine that stops and a machine that blinks off.

---

# Type 5 — Idle overlay

Only needed when the body must be drawn **under both states** — the centrifuge
and the electromagnetic plant pattern, `always_draw_idle_animation = true` with
a separate `idle_animation`.

For nearly every building in this mod the answer is *not required*: the
furnaces prove that a single still `animation` plus fading working
visualisations covers idle and working between them, and an assembler's frozen
`animation` covers idle by itself. Reach for this only when idle needs its own
*motion* — something that turns over whether the machine is crafting or not.

**No new generation.** The idle overlay is `base.png`. If idle genuinely needs
its own movement, that is a Type 2 part with its own frame count, layered under
the working animation:

```lua
graphics_set = {
  always_draw_idle_animation = true,
  idle_animation = { layers = { base_layers() } },
  animation      = { layers = { base_layers(), working_layers() } },
}
```

Write `Not required — see §6.2` under the spec heading rather than deleting it,
so `tools/generate-building-art.py` keeps skipping it and the heading stays put.

---

# Where these land in a spec

| This document | Spec §11 heading | Generator slug |
| ------------- | ---------------- | -------------- |
| Type 1, lit twin | `### Glow / Lighting` | `layer-glow` |
| Type 2, moving part | `### Working Machinery` | `layer-machinery` |
| Type 3, status lamp | *(no heading yet — add under `## Layer Prompts`)* | — |
| Type 4, effect | `### Effects` | `layer-effects` |
| Type 5, idle overlay | *(no heading — `Not required` in `### Working Machinery`)* | — |

Adding Type 3 to the pipeline means one line in `SECTIONS` in
`tools/generate-building-art.py` and one heading in the template's §11.

And when the new `graphics_set` goes onto a derived machine, set it through
`derive.own_graphics(p, set)` rather than assigning `p.graphics_set` directly.
Vanilla's `working_sound` accents name the vanilla animations they are cued to,
and a machine that replaces its graphics set while keeping them refuses to
load — `Working visualisation "warm-up" doesn't exist`. That helper strips both
the accents and the gated `main_sounds`.

---

# First test run — what each type actually returned

Four prompts, filled from the templates above and run through the browser route
of Appendix B against real plates in this tree. Recorded because the numbers are
the calibration, and because three of the four failed in ways the templates did
not predict.

| Type | Building | Verdict |
| ---- | -------- | ------- |
| 1 lit twin | Arc Mast | **Art excellent, registration failed** |
| 2 moving part | Dross Classifier | **Isolation passed, registration failed** |
| 3 status lamp | Sealed Roboport | **Colour passed, camera failed** |
| 4 effect | Dross Classifier | **Passed, grid partially compliant** |

**Type 1.** The best of the four to look at: light in exactly the four places
the prompt named, violet with white cores, electrical rather than fiery, the
silhouette and the unlit metal apparently untouched. The gate disagreed —
alpha drift 5.41 against a 0.56 floor, changed area 39 % against 3.4 %, and a
trimmed-aspect drift of **4.7 %**. The machine was quietly re-proportioned by
about a twentieth, which no one would catch by eye and which puts every glow
pixel off-register. **This is the case the gate exists for**, and it is why the
thresholds above are now expressed against a measured floor.

**Type 2.** The isolation worked perfectly — the flywheel and hub alone, no
housing, no springs, right metal, clean alpha. And it came back centred on its
own canvas at x 0.28–0.76, y 0.20–0.58, where on the plate the drive sits up at
the top of the roofline. Exactly the "usual failure" the template names. The
part is usable, but only after being placed by measurement; nothing about the
returned file says where it goes.

**Type 3.** Passed the hue gate at spread **5.5**, against **62.0** for the
amber `lamps.png` already in the tree — the gate discriminates, though 5.5
against a threshold of 6 is closer than it looks and the threshold may want
loosening to 8 with more samples. It failed on geometry: the returned ring has
a bbox aspect of **0.984**, a circle in plan view, where the shipped plate's
ring is **1.290**, an ellipse at the 45-degree camera. The cause was a missing
`== CAMERA ==` section — Types 1 and 2 had one, Type 3 did not. Appendix B is
already explicit that the camera is "the rule most often lost, and the one
whose loss is least obvious"; it went missing from a template written by
someone who had just read that sentence. The section is now in.

**Type 4.** The one unqualified success, and the only type that is a real
multi-frame generation. Twelve cells, dust lifting and falling back in a
ballistic arc with readable grains and no billowing — the vacuum physics in the
FORBIDDEN section landed — and cell 12 loops back into cell 1. The grid was
partially compliant: gutters at 2 of the 3 column seams, one of them landing
exactly on the declared pitch and one 16 px off, and no gutter at all at the
third. Cut on the measured gutters, which is what this document already says to
do, and it is usable as it stands.

**The pattern across all four:** the generator is good at *what to draw* and
unreliable at *where to put it*. Every one of the four failures was positional —
proportion, placement, projection, pitch. None was artistic. Budget the review
effort accordingly, and keep every gate geometric.
