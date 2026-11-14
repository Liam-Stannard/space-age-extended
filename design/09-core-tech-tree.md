# The Core — tech tree

**Draft, to review.** Moved as it was from `04-the-core.md` §6 (2026-11-14); not yet reviewed.

The Core carries the mod's **sixth technology tree** — twenty-one technologies,
and the only tree whose research currency is manufactured on site.

### Geodynamic science

A new science pack, crafted from the **intermediates** of the Core's own line
(§5) — the same intermediates the end products need.

### The recipe

**Geodynamic science pack** — 1 field conductor + 1 reinforced frame +
4 kamacite whiskers → 5 packs, 20 s, in an assembler, recipe locked to pressure
1–9. One recipe.

The pack touches three of the Core's four mechanics: the conductor carries
orbital homogenisation, the frame carries whisker growth and the whiskers
themselves carry the farm's tile. Two rules:

- **Locked to pressure 1–9.** Labs carry no surface conditions, so research
  itself can happen anywhere; the *pack* cannot be made anywhere but here. The
  tree therefore has to be advanced by a factory genuinely running on the Core.
  Vanilla gates its own packs the same way — electromagnetic at magnetic field
  99, metallurgic at pressure 4000, cryogenic at 100–600.
- **It requires one orbit-made intermediate.** The field conductor needs a
  homogenised ingot, so the platform overhead is load-bearing from the first
  geodynamic technology rather than switching on at the end.

### The ladder

Twenty-one technologies in five tiers, shaped so the endgame builds rather
than arriving flat.

| Tier | Technologies | Notes |
|---|---|---|
| **0 — Foothold** | **Core Discovery** (an `unlock-space-location` technology — measured: the planet is unreachable without one) · Crust Tapping (landing-day power, fired by mining a boulder) → Core Survey (the drill) → Gravity Crushing (crusher, smelting) → Vacuum Sintering (the furnace, fines) → Vent Tapping (the vent pump; also needs Uranium Mining) → Radiant Power, each after Crust Tapping a trigger technology fired by the step before it | Core Discovery is researched on packs the player already makes; the rest are triggers, and take none. No geodynamic pack exists yet |
| **1 — Integration** | Five technologies, one per capstone. **Conductor** and **Frame** come first, on vanilla packs — the two the science pack needs. **Billet**, **Sleeve** and **Coolant** follow, on geodynamic packs, in any order |
| **2 — Geodynamic Science** | The pack itself | Needs the Conductor and the Frame; required by everything after |
| **3 — The Core's own goods** | **Field Coils** (coil assembly, coolant loop, the Ring Mast, the ignition charge) · Corridor Seeding · Magnetic Separation · Carbonyl Chemistry · the **sealed roboport** (§9), which needs Field Coils and cold welding | The mid-tree milestone: after hours of belts and personal bots, the Core starts working like a factory |
| **4 — The goal** | Ignition Array, which also unlocks the Field Coil Segment | Costs escalate steeply — the Array's research alone running into thousands of packs |

### Three things this shape gets right

**The pack cannot be first.** It is made from intermediates, and intermediates
need a capstone product plus a local input — so the opening hours run on vanilla
packs and local bootstrapping, and geodynamic science arrives only once the
corridor is genuinely delivering. The tree's currency is earned rather than
granted on landing. Some technologies will be trigger techs to aid players progress through the mod.

**The climax is the last technologies.** With costs escalating steeply, the
ramp is felt rather than announced, and the final stretch becomes one sustained
decision about how to split a single production line between knowing more and
building more.

**The five integration technologies must not be five of the same technology.**
They share a shape — capstone plus local input yields intermediate — so what
saves them is that each integrates through a **different local input**: one
through settled melt, one through the helium, one through an orbit-only ingot,
one through combed whiskers, one through felt and raw melt. Then each capstone lands somewhere
different in the Core's economy, and five reads as five.
