# The Corridor

The route from the Solar System Edge to [the Core](04-the-core.md), **flown on
space platforms**. It is where the mod's cargo travels, where its one shared
mechanic lives, and the only place the player meets the far field.

---

## 1. What vanilla leaves out there

- **Past the midpoint of the Shattered Planet route the useful chunks stop.**
  Metallic, carbonic and oxide die away and promethium replaces them.
- **Promethium is inert.** It has no crushing recipe at all — the only entry
  vanilla gives it returns 25% of the chunk and nothing else.
- **Damage scales with speed**, so the corridor cannot be outrun.
- The Shattered Planet is not a destination; you travel toward it and turn back.

The mod does not undo any of that. It adds **one** new asteroid type and otherwise
flies vanilla's mix for the way to the Shattered Planet
(`prototypes/core/planet.lua`), metallic, carbonic and oxide chunks included.
Whether carbon, ice and ore stay freight is therefore open.

## 2. Seeding the field

Cut back with the landing: the seeded asteroid and the seed missile are gone, and
the corridor has no mechanic of its own for now.

## 3. Power out there

**Provisional.** What is built, and may yet change: the corridor's one new
asteroid is the **radiant asteroid**, which yields nothing when it dies. A radiant
chunk and its crushing recipe remain, but nothing yields the chunk (Liam,
2026-10-20: "Fine as designed"). **Radiant fuel**, a fuel in its own category
that only the **radiant generator** burns, is made on the Core from radiant
solution and crust gas ([08-core-power.md](08-core-power.md)). The generator
carries a pressure ≤ 9 condition, so it works on platforms and on the Core and
nowhere else. None of it has been
played, and the names and numbers are first guesses.


## 4. Still open

- **How long the route is**, and whether it is one connection or several hops.
- **Whether parked depots are part of the design**, or the corridor is flown
  end to end.
- **Whether the radiant chain above is the answer**, or a placeholder for one.
- **The ammunition economy** — seeding costs missiles, harvesting costs ordinary
  ammunition, and both are freight until the field itself supplies them.
- **The spike**: whether a projectile can destroy an asteroid and create another
  in one trigger, and whether collectors gather the resulting chunks.
