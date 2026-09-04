# Mechanics

**The mod creates its own problems.** Each tree introduces exactly one new rule
the player must design around, taught alone in that tree and required again at
the end, where the five combine.

A mechanic qualifies only if it is a genuinely new thing to design around,
Factorio-shaped rather than bolted on, and implementable in prototypes —
ideally with no control-stage script. Every engine fact cited here was checked
against a data dump of the installed game.

---

## The six

Five trees, one corridor. Two rest on the spoil timer and four do not, which is
the balance we want: the timer is a strong tool and a limited one.

### Maturation — Vulcanus ↔ Gleba

**The rule: something that gets better if you leave it alone.** A bio-mineral
seeded on Gleba and held in Vulcanus's heat improves with age. Spoilage run
backwards: the timer is the process, and the player's instinct to push everything
through fast is exactly wrong.

*Implementation:* `spoil_ticks` with a `spoil_result` pointing at a **better**
item. The engine's spoilage is only a timer aimed at another item; nothing
requires the destination to be a downgrade.

*At the end:* the corridor. The run to the Core is measured in real time, so one
cargo ripens while everything else merely costs money — the only thing in the mod
that makes the journey's length an asset.

*Capstone:* cultured alloy, which becomes the coil's frame.

### Surge production — Vulcanus ↔ Fulgora

**The rule: rate follows available power, not machine count.** These recipes draw
so hard against such small buffers that a second machine does nothing while the
first is browning out. You scale by capturing peaks — collectors, accumulators,
discharge timing — not by copying the line.

*Implementation:* native and needs nothing new. Factorio already slows electric
machines under brownout; the mechanic comes from the alloy's recipes having
enormous instantaneous draw. On Fulgora the line visibly surges with the
lightning.

*At the end:* the Core's arc storms are the same problem without the lightning-rod
tutorial. A player who learned to build for peaks arrives ready.

*Capstone:* magnetar alloy, which becomes the coil's magnetic core.

### The living line — Fulgora ↔ Gleba

**The rule: a process that cannot be paused.** The polymer line runs on a culture
the recipe both consumes and returns. Stall it — a backed-up output, a power cut,
a belt gap — and the culture spoils in the machine. You do not lose a batch, you
lose the line, and restarting takes a fresh seed.

*Implementation:* a culture item with a short `spoil_ticks`, present on both
sides of the recipe.

*At the end:* running something that can never stop, in the least forgiving place
in the game, at the far end of the longest supply line.

*Capstone:* bio-polymer, which becomes the coil's insulation.

### The cold loop — Fulgora ↔ Aquilo

**The rule: every machine takes cryogen in and returns it spent.** Not power — a
fluid, with a return leg. Layouts must be loops rather than lines, and the
chiller is an overhead that scales with machine count rather than throughput.

*Implementation:* the hot/cold fluid pair vanilla already uses for fluoroketone,
generalised from one machine to a whole tree. The novelty is the layout problem;
Factorio almost never forces a return line.

*At the end:* the coil chain is the Core's most machine-dense line, so the loop
overhead lands where floor space is worst.

*Capstone:* superconducting winding, which becomes the coil's conductor.

### Seed stock — Gleba ↔ Aquilo

**The rule: insurance you have to manufacture in advance.** A frozen seed, made
from a live culture and cryoprotectant, does not spoil — and it is the only way
to restart a biological line that died. Cheap while things are running,
impossible once they have stopped.

*Implementation:* a recipe producing a non-spoiling seed, and another reviving it
into a live culture. The seed itself has no timer, so this is the *answer* to
spoilage rather than an instance of it.

*At the end:* the recovery for the living line's failure, two million kilometres
from Gleba — and the payload of the corridor's seeding missile below. Factorio
has no recovery mechanic anywhere; nothing you build *in case*.

*Capstone:* cryoprotectant fluid, which becomes the coil's coolant.

### Seeding the field — the corridor

**The rule: you have to sow before you can reap.** The mod adds one asteroid type
to the far field. Shoot it plainly and it yields the corridor's power material.
Fire a **bio missile** into it instead and it becomes an *infected asteroid* — a
crop rather than a mineral — which harvests into organics.

Same rock, two harvests. Every asteroid in range is a small bet about what the
run needs more of, and the answer changes with distance.

*Implementation:* vanilla asteroids already carry a `dying_trigger_effect` that
`create-entity`s their smaller siblings — destroying a rock and putting a
different one in its place is the pattern the game already uses. The missile's
action does both in one trigger list: damage enough to destroy, and
`create-entity` for the infected version. Our asteroid gets a **terminal** dying
effect, so ordinary fire destroys it and yields nothing — using the wrong weapon
wastes the rock, which is the mechanic teaching itself.

*Why it matters:* it inverts the logistics. Rather than hauling bulk organics two
million kilometres, you ship **light seed** and grow heavy cargo where it is
needed. Nothing in vanilla does this; every other space resource arrives whether
you act or not.

*The payload is seed stock itself*, so Gleba ↔ Aquilo's insurance and the
corridor's ammunition are the same item, and the field's biology traces to a
planet that cannot be relocated.

*Spike required:* whether a projectile's action can destroy an asteroid and place
another in the same trigger, and whether collectors gather chunks produced that
way. Both look right in the prototype data; neither is proven.

## Considered and cut

Recorded so they are not re-proposed as new.

| Mechanic | Pair it was for | The idea | Why it went |
|---|---|---|---|
| **Charge** | Vulcanus ↔ Fulgora | Cast cells charged by lightning, self-discharging on a timer, so energy could be moved but never hoarded | Cut |
| **Substrate** | Fulgora ↔ Gleba | Ground manufactured from scrap so Gleba's organisms could grow off-world, paid for in floor tiles | Cut |
| **Launch** | Fulgora ↔ Aquilo | A superconducting silo re-pricing freight, fixed endpoint to fixed endpoint | Cut — and the silo prototype requires gravity, so it could never have worked platform-to-platform |
| **Suspension** | Gleba ↔ Aquilo | Perishables suspended in coolant, indefinitely, at the cost of a permanent cold chain | Cut |

Three of the four leaned on the spoilage timer, as maturation does. Whatever
replaces them should mostly draw on other parts of the engine — fluid
temperature, surface conditions, heat networks, tiles, plants, lightning,
asteroid definitions — so the five do not all turn out to be one idea in
different clothes.

---

## Engine features available, verified

Useful when judging whether a candidate is implementable.

| Feature | What it allows |
|---|---|
| `spoil_ticks`, `spoil_result` | An item that becomes another item after a time — better or worse |
| `spoil_to_trigger_result` | An item that *does something* when its timer runs out, as vanilla's eggs hatch |
| `surface_conditions` on recipes | A process locked to a physical property, as vanilla locks acid neutralisation to pressure 4000 |
| `surface_conditions` on entities | A building that can only stand somewhere, as the biolab is Nauvis-only and the agricultural tower Nauvis-and-Gleba-only |
| `heating_energy` + planet `entities_require_heating` | Buildings that need heat to run, and a world that demands it |
| `plant` + tile restrictions | Mod crops with `growth_ticks`, growing only on named tiles |
| `lightning` + `lightning-attractor` | Storms as hazard and as power, with a real energy buffer |
| Fluid temperature + `generator` | Power computed from a fluid's temperature, clipped at a cap |
| `asteroid-chunk`, `asteroid`, `space-connection` | New chunk types with their own spawn rates along a named route |
| Custom `fuel-category` | A fuel only certain machines will burn |
| Item `weight` vs `default_rocket_lift_weight` (1,000,000) | Freight cost per item, set deliberately rather than derived |
