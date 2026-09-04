# The Corridor

The mod's endgame is not a hero ship. It is a **supply line** — a chain of parked
refinery-depots strung out past the Solar System Edge, each processing local
promethium into consumables, each defended and powered, feeding the expedition
platforms running between them. Building it is a logistics problem at a scale
nothing else in the game asks for. Maintaining it is the endgame.

---

## 1. What vanilla actually does out there

The design falls almost entirely out of these facts, so they are worth stating
exactly.

- **The win condition is the Solar System Edge**, 100,000 km out. Everything past
  it is post-game.
- **The Shattered Planet is not a destination.** Achievements fire at 10,000 /
  30,000 / 60,000 km along the way; the nominal distance is on the order of two
  million kilometres, and you turn back, get stranded, or die.
- **Roughly halfway out, the useful asteroids stop.** Metallic, carbonic and
  oxide chunks die away and are replaced by promethium, which yields nothing
  usable. A flying factory stops being able to feed itself.
- **Speed is punished.** Damage scales with velocity, so the corridor cannot be
  outrun.
- **2.1 made depots possible.** Platforms can transfer items to each other at
  non-planet locations, and stationary platforms take significantly less damage.
  Parked forward bases are viable for the first time — which is what makes a
  corridor a buildable thing rather than a metaphor.

## 2. Gating by traversal, not by ingredients

A final technology that consumes one capstone per tree is a checklist: the player
reads a tooltip, sees what is missing, and grinds it.

Instead, **each distance band removes one thing the player has been relying on,
and one capability restores it.** The corridor teaches its own requirements by
killing platforms in specific, diagnosable ways at specific distances.

Three rules make that work:

- **One dominant failure per band.** A platform that dies at the midpoint should
  do so with a full power grid and an intact hull, so the player learns
  *feedstock* rather than "the corridor is hard." Each band must bite well before
  the next band's hazard is in range.
- **Nothing may be brute-forced with quantity.** Every gate is qualitative, or
  players will simply carry more railguns and a bigger hold.
- **Hazards are written as a class of resource being removed**, never as "the
  thing tree N happens to make." That keeps the failure legible while leaving the
  assignment re-arrangeable if a tree turns out to be unfun.

## 3. The bands

| Band | What is removed | Restored by |
|---|---|---|
| **1 — past the Edge** | Repair throughput. Impact rate outruns bot repair; hulls lose structure faster than they can be patched | **Structure** — ablative hull |
| **2 — the midpoint** | Feedstock. Usable chunks vanish and the flying factory starves | **Asteroid processing** — lixiviation makes promethium yield fuel, oxidiser, ammunition and a water trickle |
| **3 — post-midpoint** | Chemical propellant. Oxidiser can no longer be resupplied, so a raised speed ceiling cannot be exploited | **Thrust** — electric propulsion, fed by the residue lixiviation already leaves behind |
| **4 — deep field** | Every vanilla power source in turn. Solar is dead; nuclear's exchangers starve once oxide capture stops feeding them water; fusion coolant cannot be re-cooled in vacuum and must be barrelled from Aquilo forever | **Power** — the quench chain, whose coolant loop closes on the platform and whose ice draw the refinery's own trickle can cover |
| **5 — dense field** | The ammunition economy. Chaff density exceeds anything a hold can carry | **Defence** — a deflector field, with ammunition made from the asteroids themselves |
| **6 — duration** | Time. The run is now long enough that the egg clock, floor space and the ice contest each bite | **The optional tier** — cheapening, never enabling |

Bands 1–5 are the mandatory path, one band per mandatory tree. Band 6 is where
optional trees live: a player who skipped them still finishes, but the run is
longer, tighter and more expensive.

**The order is forced.** Thrust's propellant is a byproduct of asteroid
processing, and Power's ice comes from the same residue stream, so band 2 must
work before 3 or 4 can. That is the shape the design wants — several capabilities
required simultaneously in a specific order, rather than a checklist.

**The loop worth keeping.** The corridor's defining fact is that the only thing
out there is useless. The mod's answer is to make that thing the fuel, the
ammunition and the propellant. You survive the promethium field by eating it.

## 4. The corridor, not the ship

Depots are the actual new gameplay. Each is a parked platform: a refinery running
lixiviation on local promethium, a quench installation powering it, a deflector
holding the chaff off, and cargo transfer to whatever passes through.

This also answers the objection that a generator fuelled from Vulcanus cannot be
resupplied two million kilometres out. It cannot — unless there is a chain to
carry it, and building that chain is the point.

**Distance is the whole balance problem.** Long enough that the depot chain is
mandatory; short enough that a run is not an afternoon. That number gets set by
playtesting one depot hop, not by lore.

## 5. Arrival

The final technology is researched on the Core, and **the gate is arrival
itself**. A player standing there has necessarily built the hull, the refinery,
the propulsion, the power chain and the deflector, because nothing else survives
the bands. Re-checking that with an ingredient list would convert a journey into
an inventory audit.

Research there should require something that exists **only** on the Core, so the
technology cannot be finished in Nauvis orbit by someone who visited once.
Arrival is the gate; staying is the cost.

What it unlocks should be infinite research fed by the Core, not an ending.
Vanilla's post-game is infinite research, and an ending that switches the
corridor off would waste the most interesting thing the mod built.

---

## 6. Risks

**The route may not be moddable.** A location past the Shattered Planet, with its
own asteroid distribution and a landable surface at the end, is the largest
technical assumption in the mod. It is unverified. Verify it before any further
design work rests on it — see [roadmap M1](06-roadmap.md).

**Do not devalue vanilla's promethium.** Making promethium yield usable material
also makes ordinary Shattered Planet science runs easier. Restrict lixiviation
output to corridor consumables — propellant, oxidiser, ammunition, water — never
anything exportable, or price it so poorly it is only worth doing where nothing
else exists.

**Do not move the win condition.** The Edge stays the game's ending. This is
post-post-game and strictly additive.

**Legibility is a hard requirement, not polish.** If a platform can fail at the
midpoint for three overlapping reasons, the corridor stops teaching and starts
feeling arbitrary.

**Every mandatory tree is a single point of failure.** If one proves unfun in
play, it gets demoted to band 6 and an optional tree promoted in its place. That
swap must remain possible, which is why §2 writes hazards as removed resources
rather than as named products.

---

Next: [the Core](05-the-core.md).
