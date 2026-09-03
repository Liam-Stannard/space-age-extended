# Icon generation prompts

Instructions for generating final icon art for `space-age-extended`, to replace the
current flat-shape placeholders (`graphics/icons/`, `graphics/icons/fluid/`,
`graphics/technology/`). Written for pasting into an AI image-generation tool one
entry at a time — each entry below is a self-contained prompt.

This covers the 21 **flat 2D icon** files only (items, fluids, recipe icons,
technology icons). It does **not** cover the Quench Turbine's in-world entity
sprite (the animated object placed on the map) — that's a different, more
technical asset (multi-layer, shadow-separated, 8-frame animation,
engine-scale) outside what a general image-generation tool can produce
directly, and is out of scope for this document. That sprite is currently
vanilla's steam turbine recoloured by `tools/recolour-turbine.py`.

---

## Global style guide — prepend or keep in mind for every prompt below

> Factorio "Space Age" item icon. Small rendered industrial object, painted in
> a semi-realistic sci-fi/industrial style — not flat, not cartoon, not photo-
> real. Three-quarter / slightly top-down perspective, as if resting on a
> workbench. Soft single-direction studio lighting from the upper-left,
> visible specular highlight, subtle ambient occlusion where surfaces meet,
> gentle drop shadow beneath/behind the object. The object fills roughly
> 75–85% of the frame, centered, with even padding on all sides. Background is
> fully transparent. No text, no logos, no watermark, no border, no frame,
> no ground/platform under the object, no scene or background elements.
> Square canvas.

Technical notes for the tool/output:

- **Generate large, we downscale ourselves.** Ask for a square canvas at the
  largest size the tool supports (1024×1024 is ideal); we'll resize down to
  the game's actual icon size (64×64 for items/fluids/recipes, 256×256 for
  technologies) and generate mipmaps afterward. Don't ask the tool to target
  64px directly — that's too small for any generator to render cleanly.
- **Transparent background (PNG, alpha channel) is required.** If the tool
  can't do transparency, generate on a flat, unambiguous solid color that
  doesn't appear anywhere in the object itself (e.g. pure magenta `#FF00FF`
  or a checkerboard) so the background can be keyed out afterward — call this
  out explicitly in the prompt if needed.
- **Silhouette has to read at tiny size.** These get displayed as small as
  32px and 16px in-game. Keep the object shape bold and simple — one clear
  focal read, not a busy composition — even though the render itself can have
  real detail and shading.
- **Recolor/restyle rather than redesign**, where a "current placeholder
  description" is given below — that's what our existing flat placeholder
  icon (already in the repo) depicts; the goal is a properly rendered version
  of the same concept, not a different concept.
- Keep a **consistent lighting angle and rendering treatment across all 20**
  so they read as one icon set once dropped into the game together.

---

## Items — 64×64, `graphics/icons/`

### Copper Foil — `copper-foil.png`

**What it is:** A thin rolled sheet of copper, refined from Fulgora's
non-ferrous scrap stream. Used as a drop-in replacement for Copper Cable in
several electronics recipes — it's a *sheet*, not the thick cast ingot that
Copper Plate already is, so it needs to read as thin and flexible, not another
copper ingot.

**Current placeholder:** flat solid orange-copper circle with a darker copper
outline ring, no shading.

**Prompt:**
> A thin, slightly curled sheet of bright copper foil, catching a warm orange-
> pink metallic sheen along its rolled edge. Reads clearly as thin and pliable
> — not a thick ingot or plate. [+ global style guide]

---

### Catalyst Rod — `catalyst-rod.png`

**What it is:** A one-time-use consumable catalyst — a crystalline rod made
from Holmium Ore, Copper Foil, and Iron Plate, held at an angle. It's
*charged* — should read as energetic/valuable, not inert.

**Current placeholder:** an angled metallic capsule/rod with dark grey-metal
end caps and a glowing amber-gold stripe running down its center.

**Prompt:**
> A crystalline metal rod held at a diagonal angle, dark polished-metal end
> caps at each tip, a bright glowing amber-gold energy core running the
> length of the rod visible through a faceted crystal window in its body. The
> glow should read as "charged" and valuable. [+ global style guide]

---

### Depleted Catalyst Rod — `depleted-catalyst-rod.png`

**What it is:** The spent version of the Catalyst Rod above, after its
one-time use — same physical object, but visibly dead/used up. Ships back to
Fulgora for reprocessing rather than being discarded.

**Current placeholder:** the same rod shape as Catalyst Rod, but the core glow
is dulled to a muddy grey-tan instead of bright amber, with a dark crack
running across it.

**Prompt:**
> The same crystalline metal rod as [Catalyst Rod] at the same angle, but its
> internal core is dark, dull and grey-brown instead of glowing — visibly
> spent, not energized. A visible crack or fracture line runs across the
> crystal. The metal end caps look slightly scorched or tarnished. [+ global
> style guide]

---

### Resonant Circuit — `resonant-circuit.png`

**What it is:** A high-tier circuit board — literally builds *on top of* a
Processing Unit rather than sitting parallel to it, so it should read as more
advanced than a normal circuit, not just "another green PCB."

**Current placeholder:** a small dark-green PCB square with copper/gold trace
lines and a glowing blue central chip.

**Prompt:**
> A compact dark-green printed circuit board, fine copper-gold trace lines
> running across its surface, with a single glowing blue-white chip at its
> center pulsing with visible energy — more advanced and "alive" looking
> than an ordinary circuit board. [+ global style guide]

---

### Magmatic Core — `magmatic-core.png`

**What it is:** The Vulcanus half of the capstone — forged from Lava,
Tungsten, and a shipped-in Catalyst Rod. Should read as genuinely molten/hot,
Vulcanus's signature material.

**Current placeholder:** a glowing yellow-white-hot sphere seen through gaps
in a dark, cracked crust ring, with visible bright cracks and a small
specular highlight.

**Prompt:**
> A roughly spherical chunk of solidified volcanic material with a dark,
> cracked obsidian-like crust, glowing molten orange-yellow light bleeding out
> through the cracks and from a visible molten core beneath the crust. Reads
> as hot, heavy, and dangerous. [+ global style guide]

---

### Thermionic Assembly — `thermionic-assembly.png`

**What it is:** The tree's capstone item — Resonant Circuit + Magmatic Core
combined. Should visually read as *both halves fused into one object*, not a
new unrelated design — literally the fusion of the electromagnetic (blue) and
thermal (orange) halves of the tree.

**Current placeholder:** a silver-grey metal module housing a blue glowing
gem on one side and an orange glowing gem on the other, connected by a thin
purple energy arc.

**Prompt:**
> A compact polished metal module/housing, rounded rectangular, with two
> recessed circular sockets set into its face — one holding a glowing blue
> gem-like component, the other a glowing orange-red gem-like component — the
> two connected by a thin arcing tendril of purple-violet energy across the
> housing's surface. Should clearly read as "two different technologies
> fused into one finished part." [+ global style guide]

---

### Quench Turbine — `quench-turbine.png`

**What it is:** The item that places the platform-mounted Quench Turbine —
a generator that runs on Quench Vapour and converts it to electricity, clipping
any vapour hotter than it can use. It is the *cold* machine in a hot process,
so it should not read as a furnace: think cryogenic turbomachinery, not a
boiler.

**Current placeholder:** vanilla's steam-turbine icon, recoloured to a
cryogenic teal by `tools/recolour-turbine.py`. Good enough to play with, but
it is derived art rather than drawn art.

**Prompt:**
> A compact industrial turbine module seen three-quarter on: a bladed turbine
> rotor visible through a circular housing opening, heavy pipework and
> flanges around it, painted in cool cyan-teal accents over dark grey-green
> metal, with pale frost or condensation gathering on the intake side. It
> should read as a precision cryogenic turbine, cold and machined, not as a
> furnace or boiler. No flame, no orange glow. [+ global style guide]

---

## Fluids — 64×64, `graphics/icons/fluid/`

Fluid icons in Factorio are simpler than item icons — usually a small glowing
"puddle" or liquid-surface glyph, not a solid object, since the fluid itself
is what's shown flowing through pipes. Keep these flatter/more abstract than
the item prompts above, but still lit and shaded, not flat color.

### Molten Scrap — `fluid/molten-scrap.png`

**What it is:** Fulgora's messy, unrefined remelted scrap — a mixed, impure
molten stream, not yet separated into anything useful. Should look churned
and dirty, not clean.

**Current placeholder:** a murky grey-brown glowing liquid, darker at the
rim.

**Prompt:**
> A small pool/surface of murky, churning molten metal — muddy grey-brown
> with dull orange-red heat glow showing through in patches, flecks of
> different metal colors visible swirling through it (hints of copper and
> iron tones), clearly impure and unrefined rather than a clean single
> material. [+ global style guide, but flatter/more liquid-surface than a
> solid object]

---

### Molten Ferrous Metal — `fluid/molten-ferrous-metal.png`

**What it is:** The separated iron-family stream, pulled out of Molten Scrap
— cleaner and hotter-looking than the raw scrap melt, on its way to becoming
vanilla Molten Iron.

**Current placeholder:** a silvery-blue-grey glowing liquid.

**Prompt:**
> A small pool/surface of bright, glowing molten iron-grey metal — white-hot
> at its brightest points fading to a cooler steel-blue-grey at the edges.
> Clean and metallic-looking, in contrast to Molten Scrap's murky impurity.
> [+ global style guide, but flatter/more liquid-surface than a solid object]

---

### Molten Non-Ferrous Metal — `fluid/molten-non-ferrous-metal.png`

**What it is:** The separated copper-family stream pulled out of Molten Scrap
— warm copper-orange tones, about to be split further into Molten Copper +
Holmium-rich Residue.

**Current placeholder:** a warm orange-red glowing liquid.

**Prompt:**
> A small pool/surface of glowing molten metal in warm copper-orange and
> reddish tones, bright and clean-looking like refined liquid copper, with a
> faint secondary color variation hinting that other metals are still mixed
> in. [+ global style guide, but flatter/more liquid-surface than a solid
> object]

---

### Holmium-rich Residue — `fluid/holmium-rich-residue.png`

**What it is:** A concentrated, unglamorous byproduct sludge — deliberately
*not* glowing/molten (it's a cool residue, not a hot metal), thick and
mineral-rich, waiting to have its trace Holmium extracted.

**Current placeholder:** a thick violet-purple liquid, not glowing.

**Prompt:**
> A small pool/surface of thick, murky violet-purple sludge with a faint
> metallic sheen — a mineral-rich waste residue, not glowing or molten, cool
> rather than hot, viscous rather than free-flowing. [+ global style guide,
> but flatter/more liquid-surface than a solid object; no heat glow]

---

### Contaminated Sulfuric Acid — `fluid/contaminated-sulfuric-acid.png`

**What it is:** A dirty byproduct of the capstone's Resonant Circuit recipe —
ordinary Sulfuric Acid, but visibly fouled, before it gets purified back into
usable acid + steam.

**Current placeholder:** a murky olive-yellow-green droplet shape with darker
contamination flecks and small bubbles.

**Prompt:**
> A small pool/surface of murky, sickly yellow-green liquid with visible dark
> contamination flecks and a few small bubbles breaking the surface — reads
> as a dirtied, hazardous version of an ordinary chemical fluid rather than
> something exotic. [+ global style guide, but flatter/more liquid-surface
> than a solid object]

---

### Quench Vapour — `fluid/quench-vapour.png`

**What it is:** What comes off a Magmatic Core when it is quenched with Ice —
the Quench Turbine's working fluid. Hot in fiction, but drawn cold: the whole
fluid set already has two saturated oranges and an olive, and cyan-teal is the
only hue left that stays legible at 16px. It also deliberately matches the
turbine that consumes it.

**Current placeholder:** a sibling fluid drop gradient-mapped to teal by
`tools/derive-vapour-icon.py`.

**Prompt:**
> A luminous cyan-teal vapour or gas — a soft, glowing volume of pale
> blue-green mist with a bright near-white core, wisping at the edges rather
> than holding a hard liquid outline. It should read as an energetic gas under
> pressure, not as a liquid drop and not as steam. Keep the silhouette compact
> and centred so it stays legible at 16px. [+ global style guide]

---

## Recipe icons — 64×64, `graphics/icons/`

Only recipes whose name doesn't match a single output item need their own
icon (Factorio otherwise defaults to that item's icon automatically). Only
two recipes in this mod need one, because both split one input into two
different outputs.

### Separate Molten Scrap — `separate-molten-scrap.png`

**What it is:** The Electromagnetic Plant recipe that splits Molten Scrap
into Molten Ferrous Metal + Molten Non-Ferrous Metal. Should read as "one
input, two outputs" via an electromagnetic-separation visual, not as either
output alone.

**Current placeholder:** a flat murky-brown circle representing the mixed
input.

**Prompt:**
> A stylized electromagnetic separation moment: a single murky grey-brown
> molten stream entering from one side, visibly splitting into two distinct
> glowing streams — one silvery-steel colored, one warm copper-orange
> colored — pulled apart by a faint blue electromagnetic field/arc effect
> between them. Reads clearly as "one thing becoming two things." [+ global
> style guide]

---

### Non-Ferrous Separation — `non-ferrous-separation.png`

**What it is:** The Electromagnetic Plant recipe that splits Molten
Non-Ferrous Metal into vanilla Molten Copper + Holmium-rich Residue. Same
"split" visual language as Separate Molten Scrap above, but with the
non-ferrous/copper-toned input and the copper + violet-residue outputs.

**Current placeholder:** a flat copper-orange circle representing the input.

**Prompt:**
> A stylized electromagnetic separation moment: a single warm copper-orange
> molten stream entering from one side, visibly splitting into two distinct
> streams — one bright glowing copper-orange (clean Molten Copper), one
> thick murky violet-purple (Holmium-rich Residue) — pulled apart by a faint
> blue electromagnetic field/arc effect between them. [+ global style guide]

---

## Technologies — 256×256, `graphics/technology/`

Vanilla technology icons tend to be a fuller illustrated scene rather than a
single small object — give the generator more room to depict a moment or
composition, not just an isolated item.

### Metallurgical Recovery — `metallurgical-recovery.png`

**What it unlocks:** Scrap Remelting, Molten Scrap, Ferrous/Non-Ferrous
separation, Ferrous Refinement — the start of the whole refining chain.

**Prompt:**
> A technology icon depicting scrap metal fragments being drawn into and
> melting within an industrial furnace, glowing molten metal pooling below,
> chaotic mixed-metal fragments on one side transitioning into a clean glowing
> liquid stream on the other — visually establishes "junk becomes refined
> material." [+ global style guide, illustrated-scene composition rather
> than a single object, richer/busier than an item icon]

---

### Advanced Material Recovery — `advanced-material-recovery.png`

**What it unlocks:** Non-Ferrous Separation and Holmium Extraction — the
deeper refining stage that recovers a trickle of Holmium as a byproduct.

**Prompt:**
> A technology icon depicting a stream of molten copper-orange liquid being
> split by an electromagnetic field into a clean bright copper stream and a
> small, precious-looking glint of violet Holmium residue — emphasizing that
> the Holmium is a small, valuable trickle recovered from a much larger
> process, not the main product. [+ global style guide, illustrated-scene
> composition rather than a single object]

---

### Electromagnetic Metallurgy — `electromagnetic-metallurgy.png`

**What it unlocks:** Copper Foil, and the Electromagnetic Electronic/Advanced
Circuit alt-recipes — where refined Fulgora materials start feeding directly
into electronics.

**Prompt:**
> A technology icon depicting a sheet of bright copper foil being drawn
> directly into a glowing circuit board, copper and pale blue-white
> electromagnetic energy visually merging at the point of contact —
> represents refined metal becoming an electronic component. [+ global style
> guide, illustrated-scene composition rather than a single object]

---

### Integrated Electronics — `integrated-electronics.png`

**What it unlocks:** The Electromagnetic Processing Unit alt-recipe — the
top tier of the circuit substitution chain.

**Prompt:**
> A technology icon depicting a Processing Unit chip glowing with intricate
> internal blue-white energy patterns, partially wrapped or interwoven with
> a thin ribbon of copper foil — represents the most advanced circuit tier
> in the substitution chain. [+ global style guide, illustrated-scene
> composition rather than a single object]

---

### Resonant Electromagnetics — `resonant-electromagnetics.png`

**What it unlocks:** The full capstone chain — Catalyst Rod, Resonant
Circuit, Magmatic Core, Depleted Rod reprocessing, Purify Contaminated
Sulfuric Acid, and the Thermionic Assembly itself.

**Current placeholder:** a glowing purple core with two orbiting rings, one
ring carrying a small blue node, the other carrying a small orange node —
deliberately echoing the blue (Resonant Circuit) and orange (Magmatic Core)
items this tech unlocks.

**Prompt:**
> A technology icon depicting a glowing violet-purple energy core at the
> center, with two elliptical orbit rings sweeping around it at different
> angles like an atom diagram — one ring carrying a small glowing blue node,
> the other carrying a small glowing orange node — representing the fusion
> of the tree's electromagnetic (blue) and thermal (orange) halves into one
> capstone technology. [+ global style guide, illustrated-scene composition
> rather than a single object]

---

### Thermionic Power — `thermionic-power.png`

**What it unlocks:** The Thermionic Generator — the tree's platform payoff,
turning heat into electricity with an active-cooling balancing act.

**Prompt:**
> A technology icon depicting a glowing amber-orange heat core radiating
> outward into crackling blue-white electrical energy, with a thin ring or
> wisp of pale icy-blue coolant visibly wrapping around and containing the
> reaction — represents heat being actively converted into stable power
> under active cooling. [+ global style guide, illustrated-scene composition
> rather than a single object]
