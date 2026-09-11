# Planet brief — The Core

The one asset nothing else in `graphics/` covers. A planet is neither an item
icon (see [icon-sheet-prompts.md](../../templates/icon-sheet-prompts.md)) nor a building plate
(see [building-spec-template.md](../../templates/building-spec-template.md)), so it gets its own
short brief.

**What is wrong today.** `prototypes/core/planet.lua` borrows Aquilo outright:

```lua
icon              = "__space-age__/graphics/icons/starmap-planet-aquilo.png",
icon_size         = 512,
starmap_icon      = "__space-age__/graphics/icons/starmap-planet-aquilo.png",
starmap_icon_size = 512,
```

So the destination the whole mod is built toward appears in the navigation view
as **an ice world** — close to the opposite of what it is. `check-data-stage.sh`
passes because the path is real; it is just the wrong planet's.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Starmap render | square, 512 | Reads as metal-and-heat, not as ice and not as lava | **passed — `graphics/planet/core/concept/v2-starmap.png`** |
| 1 | Small icon | 120×64 strip | **Derived, not generated** — see §4 | **passed — `graphics/icons/core.png`** |

### Where generation happens

Browser — ChatGPT's image tool. Template Appendices B and C apply.

---

# 1. What it is

**The Core of the Shattered Planet.** The intact metallic heart of a world that
came apart, still out there past the point where every vanilla platform turns
back. From the locale:

> *A frozen crust over a hot interior; no air, no water, nothing that ever
> lived. Everything arrives down the corridor.*

Three facts from `planet.lua` the art has to honour:

| Fact | Consequence for the render |
| ---- | -------------------------- |
| `magnetic-field = 0` | A dead dynamo. This is the thing the Ignition Array restarts, so the planet must look **inert**, not energetic — no aurora, no field lines, no crackle. |
| `pressure = 5`, no water tile can ever place | No atmosphere and no ocean. **No cloud layer, no blue, no white weather** — Aquilo's soft haze is exactly wrong. |
| `magnitude = 1.2` | It renders *larger* than Nauvis on the starmap. It gets looked at, so it has to hold up big. |

---

# 2. What vanilla actually does

Measured off the shipped files rather than assumed, because the conventions are
not what you would guess:

* **Two separate assets, not one.** `icon` is a **120×64 mipmap strip** (64/32/
  16/8 packed left to right, the same format `tools/key-icons.py` already
  writes). `starmap_icon` is a **512×512** render with `starmap_icon_size = 512`.
  The mod currently points both at the 512 file, which is why it also needs
  `icon_size = 512` — a 512 px render doing a 64 px job.
* **Transparent background.** No stars, no nebula, no scenery, no cast shadow.
* **The body fills the canvas**, roughly 90–95% edge to edge.
* **No terminator.** The disc is not half in shadow and there is no crescent.
  Aquilo is lit from the upper-left and falls off to a dark lower-right limb;
  the whole disc is still rendered.
* **Emissive worlds get a rim.** Vulcanus carries a warm atmospheric halo
  around its whole circumference because it is incandescent. Aquilo has none.
* **The texture is the biome from orbit** at continent scale — big legible
  features, not fine detail.

`starmap-shattered-planet.png` is the other reference that matters: a cloud of
red-black fragments around a hot centre. **The Core is the heart of that
object**, and should read as its relative.

---

# 3. Design concept

A **dark metallic sphere, frozen over, cracked open in places.**

The read, in order of importance:

1. **Metal, not rock and not ice.** The crust is iron-nickel — grey-brown, dull,
   faintly reflective in the way a meteorite is. This is the single thing that
   separates it from every other planet in the game.
2. **A frozen skin over a hot inside.** Pale grey-white frost lies in broad
   patches over the metal. Where the crust is broken, deep orange heat shows
   through in a **sparse network of fracture lines** — sparse being the point.
   Vulcanus is molten with cracks of rock; the Core is solid with cracks of
   heat.
3. **The heart of a shattered world.** A thin, sparse belt of dark red-black
   debris hangs around it, matching vanilla's shattered planet. Sparse enough
   that the sphere still dominates — this is a detail, not a ring system.

**The two anti-reads, and both are live:**

* **Not Aquilo.** No blue, no white cloud, no atmospheric haze, no snowfield.
  The frost is a thin skin on metal, not a world made of ice.
* **Not Vulcanus.** Not molten, not glowing overall, no lava seas, no
  incandescent halo. The heat is *contained* and only visible through cracks.

---

## 3.1 Colour palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Metallic crust | `#4A463F` → `#6E685C` | the body of the sphere |
| Exposed nickel sheen | `#8A8580` | broad plates catching the light |
| Frost patches | `#B8C4C8` → `#D6DAE0` | broad patches over the metal |
| Interior heat | `#D96B29` → `#FFB25A` | fracture lines only |
| Debris | `#3A2422` → `#8A3A2A` | the thin surrounding belt |

Deliberately shares the mod's own building palette (`#4A463F`–`#6E685C`) and its
melt orange (`#D96B29`), so the planet and the machinery on it read as one world.

---

# 4. Producing the small icon

**Do not generate it.** Vanilla's `aquilo.png` is the same sphere shrunk, and the
repo already has the tool:

```
tools/key-icons.py graphics/icons starmap-core.png:core
```

That crops to the object, squares it, downsamples to 64 px and bakes the 120×64
mipmap strip. Then the prototype becomes:

```lua
icon              = "__space-age-extended__/graphics/icons/core.png",
icon_mipmaps      = 4,
starmap_icon      = "__space-age-extended__/graphics/icons/starmap-core.png",
starmap_icon_size = 512,
```

Note `icon_size = 512` **goes away** — that line only exists to prop up the
placeholder.

---

# 5. Generation prompt

```text
A planet seen from space, rendered as a Factorio Space Age starmap planet icon,
matching the art style of that game's existing planet icons exactly: a single
sphere filling almost the whole square canvas edge to edge, painted in a
semi-realistic industrial science-fiction style, on a fully transparent
background with no stars, no nebula, no scenery and no cast shadow.

Follow the game's lighting convention: the sphere is lit from the upper left and
falls away to a darker limb at the lower right, but the whole disc is rendered
and visible. There is no terminator line and no crescent; the planet is not half
in shadow.

The planet is the exposed metallic core of a shattered world. Its surface is
dark iron-nickel metal, grey-brown and dully reflective like a cut meteorite,
#4A463F to #6E685C, with broader plates of brighter bare nickel #8A8580 catching
the light. Broad irregular patches of pale grey-white frost, #B8C4C8 to #D6DAE0,
lie over the metal like a thin skin rather than like snow cover. A sparse network
of deep fracture lines runs across the surface, and only inside those fractures
does a hot interior show through, glowing deep orange #D96B29 to #FFB25A. The
cracks are thin and few; most of the sphere is cold dark metal.

Around the planet hangs a thin, sparse belt of dark red-black rock fragments,
#3A2422 to #8A3A2A, drifting at a shallow angle, few enough that the sphere
clearly dominates the image. It should read as the intact heart left behind by a
world that came apart.

Surface features are at continent scale so they stay legible when the icon is
small: broad frost fields, broad metal plates, long fracture systems. No fine
detail.

It must not read as an ice world: no blue, no white cloud layer, no atmospheric
haze, no snowfields, no weather of any kind. It must equally not read as a lava
or volcanic world: the planet is solid and cold on the outside, not molten, with
no lava seas, no overall glow and no bright incandescent halo around its
circumference. The heat is contained and visible only through the cracks.

Painted semi-realistic industrial game art, square canvas, transparent
background, no text, no logos, no watermark, no border or frame, no characters,
no photorealism.
```

---

# 6. Round log

| Round | Asset | What came back | Verdict | Fix asked for |
| ----- | ----- | -------------- | ------- | ------------- |
| 1 | starmap | Two candidates came back (ChatGPT ran an A/B). Both landed the read: metallic crust with bare nickel plates catching the upper-left light, broad frost fields, a sparse network of orange fracture lines, a debris belt, no atmospheric halo, real alpha. **A was kept**; `v1-starmap-alt.png` is B, retained for comparison. | **Design accepted; composition rejected** | Two fixes: (1) the fragments drift across the planet's face, which reads as the planet breaking apart when it is the one thing that did not — move them clear of the disc; (2) enlarge the sphere to fill the canvas nearly edge to edge, as vanilla frames a planet. |

### The measurement, and what it overturned

Judged by eye, both candidates looked *too pale* — as though they had drifted
toward "Vulcanus with snow on it". That reading was wrong, and the numbers say
so. Body-luminance and hue coverage over the opaque pixels, against the two
worlds this planet is defined as not being:

| | median lum | dark (<110) | pale (>150) | warm/orange |
| --- | ---: | ---: | ---: | ---: |
| Vanilla Aquilo | 39 | 81% | 13% | 0.0% |
| **Candidate A** | **66** | **71%** | **13%** | **4.1%** |
| Candidate B | 55 | 78% | 12% | 3.0% |
| Vanilla Vulcanus | 70 | 78% | 9% | 33.3% |

Both sit exactly where the brief wanted them: between the two vanilla worlds in
luminance, carrying **the same pale fraction as Aquilo** (13%), and with heat
covering **an eighth of Vulcanus's** — sparse cracks, not a molten surface. Had
the eyeball finding been acted on, three rounds would have driven the planet
darker and colder for no reason, which is precisely the failure recorded in
[building-spec-template.md](../../templates/building-spec-template.md) Appendix C.

**Measure a planet the same way a plate is measured.** The disc is mostly dark
metal against a transparent background, so it takes the colour of whatever the
viewer puts behind it — and it is composited against black in the navigation
view but against a light background in an image viewer.

| 2 | starmap | Both fixes landed: every fragment is now clear of the disc, sitting as a sparse belt off the left and right limbs, and the sphere fills the canvas 100% × 96%. The surface came back unchanged. | **Accepted — this is the approved render** | None. |
| 3 | starmap | **Rejected — an over-correction, and my mistake.** v2 measured slightly warmer than v1 (warm 4.1% → 5.9%, median 66 → 72), so a round was spent asking for narrower, dimmer, intermittent fractures. It did the opposite of what was wanted: the heat was nearly extinguished (warm **0.9%**, against Aquilo's 0.0%) and the whole body got *paler and brighter*, not darker — median **93**, pale **33%**, which is two and a half times any vanilla planet's pale fraction. It reads as a cold moon. Kept at `v3-starmap.png` as the record. | **Reverted to v2** | None — stop. |

### The over-correction, recorded because it is the second time

The template's Appendix C says eyeballing a plate produced "a pale palette that
was in fact already below its target floor, which three refinements then drove
darker still". This is the same failure with the sign flipped, and it happened
*after* the measurement had already been done correctly:

| | median lum | dark (<110) | pale (>150) | warm | canvas fill |
| --- | ---: | ---: | ---: | ---: | --- |
| Vanilla Aquilo | 39 | 81% | 13% | 0.0% | 100%×100% |
| Core v1 | 66 | 71% | 13% | 4.1% | 100%×98% |
| **Core v2 — approved** | **72** | **68%** | **16%** | **5.9%** | **100%×96%** |
| Core v3 — rejected | 93 | 56% | 33% | 0.9% | 100%×100% |
| Vanilla Vulcanus | 70 | 78% | 9% | 33.3% | 99%×100% |

v2 was never a problem. Its warm coverage is **a sixth of Vulcanus's**, and its
drift from v1 was a rounding error next to the gap it needed to hold. The lesson
is not "measure" — that was done — it is **decide what the acceptable band is
before correcting, and check the drift against the band rather than against the
previous round.** A 1.8-point move in warm coverage is not a finding when the
thing being avoided sits 27 points away.

---

# 7. Wiring it up

The two files are produced and sit in `graphics/icons/`. The prototype change is
four lines in `prototypes/core/planet.lua`, replacing lines 18–21:

```lua
    icon              = "__space-age-extended__/graphics/icons/core.png",
    icon_mipmaps      = 4,
    starmap_icon      = "__space-age-extended__/graphics/icons/starmap-core.png",
    starmap_icon_size = 512,
```

`icon_size = 512` is deleted — it only existed to prop up the 512 px placeholder
standing in for a 64 px icon.

**Applied.** The other session's `day-night-cycle` change sits in the
`surface_properties` block further down the file and was not touched;
`./tools/check-data-stage.sh` passes with both new paths resolving.

Still on Aquilo's art after this: `sae-shattered-planet-core`, the space
connection, which has no icon of its own.
