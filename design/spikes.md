# Spikes

Engine assumptions the design now rests on, none of them proven. Each is cheap to
test and expensive to be wrong about — three separate claims in this design have
already turned out false when measured, so nothing here is taken on trust.

**Run them in this order.** They are sorted by blast radius: the first can void
two documents, the last only changes a recipe.

---

## The rig

Both harnesses already exist and are known to work.

**Data stage** — `factorio --dump-data --mod-directory <scratch>/mods` writes
`~/.factorio/script-output/data-raw-dump.json`. Enough to prove a prototype
*loads*, and to read back what the engine made of it.

**Runtime** — a headless server driven over RCON:

```
factorio --create fresh.zip --mod-directory <scratch>/mods
sleep 600 | factorio --start-server fresh.zip --mod-directory <scratch>/mods \
  --port 34198 --rcon-port 27016 --rcon-password x \
  --server-settings settings.json      # allow_commands: "true"
```

Then a short Source-RCON client sending `/c ... rcon.print(...)`. Two gotchas
learned the hard way: the server closes on stdin EOF, hence the `sleep` pipe; and
with no client attached it free-runs far faster than real time, so **measure
against `game.tick` deltas, never wall-clock sleeps**.

---

## Results so far

| Spike | Status |
|---|---|
| S1 — is the Core buildable? | **PASS**, with one required addition |
| S2 — do the Core's conditions behave? | **PASS** on placement, growth and the sealed roboport; one gap found |
| S3 — does seeding work? | **PARTIAL** — the conversion works; the harvest half is unproven by this harness |
| S4 — can a vent require an input fluid? | **PASS** |

### S1 — PASS

Measured on a headless server with a scratch mod defining the planet and a
connection from the Shattered Planet:

- The planet loads, `create_surface()` generates ground, and the surface reports
  **pressure 5, gravity 50, solar-power 0** exactly as specified.
- Placement on it matches the design precisely: chests, inserters, rails,
  assemblers, foundries, electromagnetic plants, cryogenic plants, biochambers,
  recyclers, nuclear reactors, drills, the rocket silo and the cargo landing pad
  all place; **boilers, furnaces, heating towers, roboports, burner inserters,
  agricultural towers and biolabs are all refused.** Lightning rods are refused
  too, since the magnetic field is 0.
- The space connection resolves, a platform paths to it, departs under thruster
  power, and **arrives**: `state = waiting_at_station, location = sae-core`.

**The required addition: the Core needs a discovery technology.** A platform
reports `no_path` to our planet until the force has explicitly unlocked the
location. `research_all_technologies()` does not do it, because no technology
references our planet — vanilla gates each of its worlds behind a
`planet-discovery-*` technology with an `unlock-space-location` effect, and ours
needs the same. Without it the Core is unreachable however well-formed the
connection is.

*Also learned:* the Shattered Planet is a perfectly good waypoint — connections
from it path fine, so the corridor can genuinely start where vanilla's route
gives out.

### S2 — PASS, with a gap

- A **mod tile** places on the Core, and a **mod `plant`** placed on it grows to
  maturity on schedule and yields its harvest products when mined. Whisker
  growth is buildable exactly as designed.
- A **sealed roboport** with `surface_conditions` pressure 1–9 places on the
  Core and is **refused on Aquilo and on a space platform**, while the vanilla
  roboport is refused on the Core. The mid-tree bot unlock works, and it competes
  with nothing.

**The gap: there is no harvester.** The vanilla agricultural tower is refused on
the Core (it needs pressure 1000–2000), so whiskers can only be gathered by hand
unless the mod supplies **its own harvesting tower** with the Core's conditions.
That is a second new building on the Core, and it needs to be justified or
designed into an existing one.

*Not re-tested:* whether recipe `surface_conditions` block crafting at runtime.
Earlier work established they are a player-facing selection filter rather than a
runtime block, which is sufficient — players do not set recipes by script.

### S3 — PARTIAL

**The conversion works, and it is the novel half.** A projectile whose action
combines `damage` with `create-entity` destroyed a mod asteroid and left an
infected one in its place, in a single shot, with no script. The design's central
claim holds: you can seed a rock in flight.

**The harvest half is not proven, and the harness is why.** Destroying the
infected asteroid produced no chunk this test could see, and neither did the
**control** — a *vanilla* small asteroid, destroyed the same way beside a powered
collector, also yielded nothing observable. When the control fails, the
experiment says nothing about the mod. This needs an in-client test, or a rig
that shoots asteroids with a real turret rather than applying script damage.

Four things learned along the way, all of which would have cost hours later:

- **A chunk needs two prototypes.** Vanilla defines both an `asteroid-chunk`
  *and* an `item` of the same name; copying only the former gives a chunk with no
  item form. `prototypes.entity["metallic-asteroid-chunk"]` is `nil` — chunks are
  not entities, which is also why `find_entities_filtered` cannot see them.
- **`create-asteroid-chunk` is a first-class trigger effect**, and it is what
  vanilla's small asteroids use to yield chunks. The seeding design uses exactly
  the machinery the game already has.
- **Asteroids spawned on platform tiles are destroyed instantly.** They only
  survive in empty space beyond the foundation — which is where they naturally
  are, but it invalidates a naive test.
- **Asteroids only persist while the platform is travelling.** On a stationary
  platform they vanish within a second, so any asteroid test has to be run under
  way.

### S4 — PASS

**A fluid resource can require an input fluid, and a drill can hold both fluid
boxes.** Measured on the Core with a vent resource carrying
`minable.required_fluid` and a pumpjack-derived drill given the electric mining
drill's `input_fluid_box`:

| State | Result |
|---|---|
| No helium-3 supplied | status **`missing_required_fluid`** — the engine refuses to draw |
| Helium-3 inserted | status **`working`**, molten kamacite accumulating (279 → 349 over five seconds), helium consumed as it goes |
| Helium drained again | status returns to **`missing_required_fluid`** and output stops |

So helium-3 gating the melt draw works exactly as designed — the rare resource
throttles the abundant one — and the engine even provides a dedicated,
player-legible status for the failure. No fallback needed.

### Engine change worth knowing

**Recipes in 2.1 use `categories = {...}`, not `category = "..."`.** The data
stage refuses the old form outright: *"In RecipePrototype, `category` and
`additional_categories` got merged into `categories` table."*

---

## S1 — Is the Core buildable at all?

**The claim.** A landable planet can be added past the Shattered Planet, with its
own orbit and a space connection reaching it.

**Test.** A scratch mod defining a `planet` with our surface properties
(pressure 5, gravity 50, magnetic-field 0, solar-power 0) and a `space-connection`
from `shattered-planet`. Over RCON: `game.planets["<core>"].create_surface()`,
force-generate chunks, place an entity, and confirm a platform can be given the
route.

**Pass:** the surface generates, entities place, and the connection appears as a
navigable destination.

**If it fails:** [the corridor](03-corridor.md) and [the Core](04-the-core.md)
are both void, and the mod becomes five trees plus a shared endgame that has to
live somewhere else. Better to learn this in a day than after four trees.

## S2 — Do the Core's conditions behave?

**The claims.** Four separate ones, all cheap to check together:

| Claim | Test |
|---|---|
| A recipe with `surface_conditions` gravity ≥ 45 is available on the Core and nowhere else | Check availability on the Core, Vulcanus (40) and a platform |
| A `plant` with a mod tile restriction grows at pressure 5 | Place the tile, plant, advance ticks, harvest |
| A roboport with `surface_conditions` pressure 1–9 places on the Core and refuses everywhere else | `can_place_entity` on the Core, Aquilo (300) and a platform (0) |
| Personal roboports work at pressure 5 | Equip and build a ghost |

**Pass:** all four behave as the surface-condition tables predict.

**If it fails:** the Core's austerity has to be enforced some other way, and the
sealed roboport — the mid-tree milestone — may not be possible.

## S3 — Does seeding work?

**The claim.** A projectile's action can destroy an asteroid *and* place a
different asteroid in its position, and collectors will gather the chunks that
one yields.

**Test.** Define a mod asteroid with a terminal `dying_trigger_effect`, an
infected variant whose dying effect creates a mod chunk, and a projectile whose
action combines `damage` with `create-entity`. On a platform over RCON: spawn the
asteroid, fire the projectile at it, confirm the infected entity exists and the
original is gone; destroy the infected one and confirm chunks appear and a
collector picks them up.

**Pass:** one shot converts the rock, and the chunks enter a collector.

**If it fails:** the corridor's mechanic needs another shape — most likely the
infection becomes a *chunk* transformation done in a crusher rather than an
entity transformation done in flight, which is less interesting but entirely
native.

## S4 — Can a vent require an input fluid?

**The claim.** A fluid resource can carry `minable.required_fluid`, and a drill
can hold both an input and an output fluid box, so drawing molten kamacite can
cost helium-3.

**Why it is doubtful.** Vanilla uses `required_fluid` only on uranium ore, a
*solid*. Every vanilla fluid resource — crude oil, lithium brine, the acid geyser,
the fluorine vent — is drawn with no input at all.

**Test.** Define the resource and a mining drill with both fluid boxes; place it
on a patch; confirm it stalls without helium-3 and produces with it.

**If it fails:** gate the melt somewhere else — most simply, the settling recipes
consume helium-3 rather than the vent doing so. The design intent survives; only
the location of the cost moves.

## S5 — Confirmations, not discoveries

Quick checks on things the data already implies. Ten minutes each, worth doing
before building on them.

- **`spoil_result` may point at a better item** — maturation depends on it.
  Nothing in the format requires a downgrade, and vanilla's own bacteria spoil
  *into ore*, so this is close to proven already.
- **A recipe can output steam at 500 °C into ordinary turbines** — vanilla's
  `acid-neutralisation` already does exactly this.
- **A machine can be powered by a custom fuel category** — the biochamber burns
  nutrients, which is the same shape.
- **An item's `weight` overrides the derived value** — verified previously, and
  the reason capstone freight cost is a decision rather than an accident.

---

## What to do with the results

Every spike either confirms a line in the design documents or forces a specific,
already-identified fallback. Record each outcome in
[decisions.md](decisions.md) — including the ones that pass, since "we checked
this" is worth as much as "we changed this."
