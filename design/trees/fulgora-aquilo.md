# Fulgora ↔ Aquilo — holmium in the cold

**Built.** The first tree, and the template for the other four.

| | |
|---|---|
| Available after | Aquilo |
| Mechanic | The cold loop |
| Capstone product | Superconducting winding |
| Capstone building | Superconducting store |
| Endgame role | The field coil's **conductor**, and one of the two intermediates the geodynamic pack needs |

---

## 1. The pairing

**Fulgora contributes** holmium, which exists nowhere else, and electrolyte, which
cannot leave the planet.

**Aquilo contributes** fluorine and ammonia, neither of which can leave either.

Neither world can finish the chain alone, and neither can be substituted by
moving a machine — which is the whole test.

## 2. The crossing

Both legs are forced by fluids that have no barrel:

| Leg | Carries | Forced because |
|---|---|---|
| Fulgora → Aquilo | holmium plate | **fluorine** cannot leave Aquilo, and fluorination needs it |
| Aquilo → Fulgora | fluorinated holmium | **electrolyte** cannot leave Fulgora, and the winding needs it |

The material makes a round trip. It leaves as a plate, comes back as something
only the other world could have made of it, and leaves again as a winding.

## 3. The mechanic — the cold loop

Every step drinks **cold cryogen** and hands back **spent cryogen**. Layouts are
loops rather than lines, and the chiller is an overhead that scales with machine
count rather than with throughput.

Recovering spent cryogen costs **ammonia**, which has no barrel — so cryogen is
either made on Aquilo or shipped cold in barrels. Running the chain anywhere else
means paying freight forever, which is the quiet pressure that keeps the pairing
honest.

## 4. The chain

```
Fulgora                          Aquilo
  holmium plate  ───────────────>  fluorinated holmium
                                     (fluorine + cold cryogen)
                                          │
  superconducting winding  <──────────────┘
    (electrolyte + cold cryogen)
          │
          ├─> superconducting store        the capstone building
          └─> field conductor  ──────────> the Core
```

## 5. The capstone building — the superconducting store

500 MJ, taking 20 MW in or out. It is the thing a world of spikes has always
wanted:

- **When earned:** Fulgora's lightning arrives faster than anything can spend it.
- **Getting to the Core:** a platform's draw is uneven, and this smooths it.
- **On the Core:** arc storms are episodic and a mast loses what it caught unless
  something can swallow it. This is that something.

It is an option rather than an upgrade: a vanilla accumulator is far cheaper per
joule, and this one exists for surge, not for capacity.

## 6. Technologies

Three, on packs the player already makes — this is a cross-planet tree, not Core
content.

| Technology | Unlocks |
|---|---|
| **Cryogen loop** | cold cryogen, and recovering spent cryogen |
| **Holmium fluorination** | the Aquilo step |
| **Superconducting winding** | the capstone product and the store |

## 7. Verified

- Fluorine, electrolyte and ammonia all have **no barrel item**, so both legs and
  the cryogen recovery are genuinely forced.
- The chain loads and its recipes sit in the right machines: chemistry on Aquilo,
  electromagnetics on Fulgora.

## 8. Still open

- **Numbers.** Every ratio here is a first guess; none is playtested.
- **Whether the round trip is a chore or a loop.** It is the mod's first real
  cross-planet chain, so this is the thing to watch first.
