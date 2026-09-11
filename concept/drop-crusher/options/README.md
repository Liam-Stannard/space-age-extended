# Drop Crusher — five options

Five designs to be **compared, not refined**. That is the method the Ignition
Array arrived at after four sets and twenty concepts, and it is the method this
building has never had: the Drop Crusher is on **version 10**, and all ten are
refinements of one idea. Refining one idea makes it a better version of itself
and never tells you whether it was the right idea.

Each option is a page with its own prompt. Nothing here is adopted; when one is
picked, the rest of this directory goes, the way `array-options/` lost nineteen
pages the day option R was chosen.

| Option | One line | What moves |
| ------ | -------- | ---------- |
| **A — the Sealed Hammer** | The incumbent: a tall armoured cylinder with the forged crown rising from a collar in its roof | a crown, ~33 % of the box |
| **B — the Twin Tower** | Two heavy square towers on one base, their crowns falling out of step so the machine is never still | two crowns, ~70 % |
| **C — the Beam Engine** | A rocking beam and counterweight on an A-frame over a sealed drum — the weight is hauled up by a beam you can see | a beam, ~85 % |
| **D — the Ratchet Crown** | A low wide drum whose entire roof is a toothed winding wheel, clacking round against a pawl | the roof, ~83 % |
| **E — the Skip Tower** | A slender tower with an external skip hoist: it lifts the *ore* and drops it, which is what the locale actually says | a skip, full height |

**A is carried as a fair comparison, not as the favourite.** It is what §3.1
currently locks and what ten versions have converged on, and if none of the other
four beats it that is worth knowing.

## The constraints, agreed before drawing

1. **3 × 3 with no sideways overhang.** Height above the footprint is fine and
   Factorio does it everywhere; width is not, and a plate that overhangs makes a
   row of machines interleave. The Arc Mast is the standing lesson at 3.14 tiles
   on a 3-tile pitch.
2. **Tier 0 — Foothold, and it must not be modernised.** §4 is unusually firm:
   riveted plate, cast housings, **exposed gears**, rack and pawl, weld seams,
   hazard tape, honest wear. This is the baseline the endgame is measured
   against, so a sealed composite shell here costs the whole ladder its bottom
   rung.
3. **It reads as itself beside the other grey 3 × 3 machines.** This is the
   constraint doing the most work. The Dross Classifier is a low stepped box, the
   Vacuum Furnace is a welded drum with a clamped lid, the Whisker Comber is a
   standing drum with a domed lid. **Three of the five options here deliberately
   stop being a drum.**
4. **It never draws what it makes.** No ore, no fines, no grit, no dust, at any
   port, hatch or opening, anywhere on the sheet. On this building the rule bites
   twice: it is a crusher, so a generator will want to show it crushing.
5. **Sealed, because an open frame surrounds a permanently empty anvil.** §3.1's
   load-bearing decision, and vanilla's own crusher agrees — a sealed housing
   with its rollers in a recessed bay, for exactly this reason. No visible anvil
   bed, no jaw plates, no gullet.

## Two engine facts that are not style opinions

**No output chute, spout, boom, bin or tray — on any option.** This is an
`assembling-machine`: it holds its output in an inventory and has no output
*position*, so an inserter may stand on any adjacent tile. A chute promises the
player something the entity cannot keep. §3.2 records that three rounds were
spent arguing about the size and placement of two discharge chutes before this
surfaced.

**No fluid connection, and no pipe flange anywhere in the art.** §8: `Fluids —
none`. The prototype has no fluid box, so a drawn flange is a socket a player can
never plumb. Every prompt says so in terms, because v1 came back with copper
hydraulics on a building with no fluid box.

*The instruction about fluid connections lining up with the foundry's applies to
the Ring Mast, the Crust Turbine and the Vent Pump, which do have fluid boxes. It
does not apply here, and saying so is the point: the right number of pipes on
this machine is zero.*

## The lights, which are new to this building

**One white lens, and it is the only light on the machine.** §3.3 says *"No glow.
Nothing here is hot"*, and that stays — which makes the Drop Crusher the one
building in the set where the status lamp carries the whole idle/running/blocked
read on its own. Every other machine has a warm port to help it.

It is drawn **white** and the engine tints it: `apply_tint = "status"` with
`always_draw = true`, the way the Vacuum Furnace's lamp and vanilla's electric
mining drill do it. A lamp that only appears while working cannot report that the
machine has stopped, which is the one thing it exists to say.

So every prompt carries the same two-part instruction, and it is the part most
easily lost: **the lens is painted white in the hero view, the top-down view, the
detail panels and the silhouette, and drawn coloured ONLY inside the three-state
row.** A plate with an amber lamp baked into it is amber in every state for ever.

Each option puts the lens somewhere different on purpose, and each has to answer
the same question: *can you tell the three states apart at map zoom on a machine
with no other light on it?*

## The animation gate, applied before the plate exists

`04-the-core.md` and the Dross Classifier's §26 both say it plainly: **how much
of the machine moves is settled at spec time, and no stage after the master plate
can make the moving part bigger.** The Classifier was drawn, approved, measured
and shipped before anyone asked, and what the plate offered was a drive drum
occupying **5.2 %** of the machine's width, against 72 %, 101 % and 113 % on the
three vanilla machines it stands beside.

So the table above measures each option's moving part against its own 3-tile box,
and the number is a judging criterion rather than a note. **Option A is the
weakest of the five on it** — a crown lifting clear of a collar is about a third
of the box, and the ten versions that produced it never asked. That is exactly
the sort of thing a comparison round exists to surface and a refinement round
cannot.

## What to attach, every time

| Attachment | Why | Order |
| ---------- | --- | ----- |
| `assembling-machine-3` | The house camera, and this building's own assigned style reference in the art backlog (now `TODO.md`)'s plan | first |
| `foundry` | A big Space Age machine at the current art standard: finish and detail density | second |
| `ignition-array/concept/adopted/R-sheet.png` | Format example: our own approved sheet, panel layout only. Say in the prompt that the machine in it is a different building | last |

**Order matters now that this is scriptable.** The model weights the first
attachment most, so the house camera goes first and the format example last.

`tools/extract-style-references.py --only assembling-machine-3,foundry` cuts the
vanilla ones from their real layers at their real shifts. They are Wube's art:
extract to a scratch directory, attach, discard, **never commit**.

**The format example is the adopted Array sheet, not `radiant generator v2`.**
the art backlog (now `TODO.md`)'s plan names the v2 sheet for this building; the Vacuum Furnace
round already found that the v2 sheets are rejected designs carrying a
generator-added wordmark, and attaching one invites the wordmark back. The plan's
row should be corrected.

## How to generate these

`tools/generate-building-art.py` grew `--attach` for this round, so the option
sheets no longer have to be made by hand in a browser:

```bash
tools/extract-style-references.py --out /tmp/refs \
    --only assembling-machine-3,foundry

for opt in A-sealed-hammer; do   # the round's other four pages are deleted; see CHOSEN below
  tools/generate-building-art.py concept/drop-crusher/options/$opt.md \
      --only sheet --tag ${opt%%-*} --size 1536x1024 --quality high \
      --background opaque \
      --attach /tmp/refs/assembling-machine-3.png \
      --attach /tmp/refs/foundry.png \
      --attach concept/ignition-array/adopted/R-sheet.png \
      --outdir concept/drop-crusher/options   # round scratch; the winner moves to concept/adopted/
done
```

## How these get judged

**By measurement first.** `tools/check-sheet-style.py` scores a sheet against the
vanilla references for luminance, saturation and detail density, and it earned
its keep on the Array — it caught a whole set sitting at half vanilla's chroma
before anyone had to argue about it. **Two of its numbers do not work** and should
not be quoted: the *aspect* column reads the sheet's panel bounds rather than the
building, and `base_flatness` scored a plainly diamond-shaped base at 1.000.
Corner-on drawing is still found by eye.

**Then by silhouette**, which on this building is the whole contest. Every sheet
carries a silhouette panel: if the option is not identifiable as a flat black
shape beside a stepped box, a welded drum and a domed drum, it will not be
identifiable at map zoom either.

**And the copper is not rationed.** Fifteen sheets in an earlier round all came
back under vanilla's saturation floor of 0.230, the worst at 0.136, because every
prompt confined copper to one place. The adopted Array prompt says copper and
brass are *"VISIBLE and used freely on bus runs, joints and fittings"* and
measures 0.262. Every prompt here says the same — which matters on a building
whose palette is grey armour, a dark weight and one yellow stripe.

**The tile-grid panel is deliberately absent.** Every concept sheet in this repo
has drawn a grid that does not line up with the building on it, because a
generator has no idea where the tile edges are. These prompts ask for a plain
top-down view instead, and the footprint is measured on the real plate later with
`tools/check-footprint.py`.

---

## Four things in the spec raised rather than quietly resolved

**1. §8 and §3.2 contradict each other about the chutes.** §3.2 says *"No output
port of any sort"* and explains why. §8's table still says the chutes are
*"honest decoration in the way a vanilla furnace's hopper is"*, and §3.3's palette
still has a row for *"Ore and fines — the two chutes, coarse and fine"*. §3.2 is
the one that survived the argument and it is what these prompts follow. **§8's
last line and §3.3's last palette row should be struck**, because a generator
handed both will draw a chute.

**2. §16's icon describes a building that no longer exists.** *"The carriage
mid-fall between two posts, with the anvil beneath"* is the open-frame design
that versions 3 to 6 replaced. The icon has to be redrawn from whichever option
wins, and §16 should be emptied until then.

**3. §20's two open questions are now closed by the code, and the spec has not
noticed.** *"Do the fines have a home yet?"* — yes: `sae-fines-smelting` takes
4 fines to a plate, and `sae-metal-carbonyl` takes 4 more, both implemented.
*"One recipe or two?"* — one, with two products, as implemented. Neither changes
the art now that there are no chutes to be simultaneous or alternate, but §20
should record that they are settled.

**4. §3.3 has no status lamp in it, and no copper.** Seven palette rows, none of
them a warm metal and none of them a lens. A building drawn to exactly that
palette measures below vanilla's saturation floor by arithmetic. **§3.3 should
gain two rows**: `#FFFFFF` for the lamp lens, and `#8A5A32` → `#C88A4A` for
copper and brass on bus runs, gear furniture and bolt lines. The discipline that
comes with the second: copper is a *material* and never glows, so it can never be
mistaken for the lamp.

## The anti-reads

**Vanilla's crusher**, which is a rotating mill built for zero g — the opposite
machine, and §1 says so. It is not attached and it is named in words in every
prompt instead.

**A jaw crusher.** No opposed plates, no gnashing, no gullet.

**A silo or a tank.** The moving mass and the exposed mechanism are what stop
this reading as storage, which is the failure mode of any sealed vertical vessel.

**And, new to this round: the Vacuum Furnace and the Whisker Comber.** Both were
locked after this building's last version, both are drums, and one of them has a
dogged lid on its roof. Option A is a drum with a collar on its roof. Options B,
C, D and E each go somewhere neither can follow.

---

## Round 1 — two sheets, and two failure modes worth recording

Generated 2026-09-09 through `tools/generate-building-art.py --attach` and, when
the API key turned out to have no credits, through the browser with the same
three attachments in the same order.

| Option | Sheet | Luminance | Saturation | Edge density |
| ------ | ----- | --------: | ---------: | -----------: |
| A — the Sealed Hammer | `concept/adopted/A-sheet.png` | 63.0 | **0.264** | **0.158** |
| B — the Twin Tower | *deleted; survives in `concept/round-1-contact-sheet.png`* | 56.8 | **0.259** | **0.146** |
| C, D, E | not generated | — | — | — |
| **vanilla band** | | 63.2–90.4 | 0.230–0.490 | 0.144–0.261 |

Both are inside vanilla's saturation and edge-density bands, which is the copper
instruction working again. Both sit at or under the luminance floor, which is
what a deliberately dark tier-0 building should do.

**Both sheets got the thing most likely to go wrong right:** the lamp lens is
painted white in the hero view, the top-down, the details and the silhouette, and
coloured only inside the three-state row. Neither drew a chute, a pipe, a flange
or a grain of loose material.

### Failure 1 — the format example bled its building into the output

One generation came back as a **purple glowing sphere in an A-frame with a
lightning column**: the Ignition Array, which was attached as the *format*
reference. It kept the Array's design, its charge sequence and its glow, on a
building whose spec says nothing here is hot.

The prompt already says the attached sheet is "a FORMAT reference only… the
machine in it is a different building of ours and this one must look like nothing
else", and that was not enough. The image itself went with the round's other
rejected art; the lesson is recorded here and in the art backlog (now `TODO.md`)'s reference
plan, which no longer names a format example for this building.

**What to change before the next round:** attach a format example whose building
is as unlike the subject as possible, or crop the format example down to its
*panel furniture* — labels, boxes, the palette strip — with the machine removed.
The second is better and is a small tooling job.

### Failure 2 — grabbing "the last big image on the page" is not safe

ChatGPT is a single-page app, and navigating to a new chat does **not** clear the
previous conversation's images from the DOM. Grabbing the largest image after a
generation therefore returned, variously: the previous option's sheet, and the
1536 × 1024 R-sheet *attachment*, which matches any "big image" filter.

Two files were mislabelled before this was caught, and were only sorted out
because **every sheet draws its own title** — which is now a load-bearing reason
for the `Title the sheet …` line, not just a nicety.

**The reliable signals**, both used in the end: no `button[data-testid="stop-button"]`
present, and the image count on the page higher than the number of attachments.
A generation typically takes 90–150 seconds.

### C, D and E are outstanding

**D failed three times** with ChatGPT's own "Something went wrong. Please try
again." — server-side, not a prompt problem, and not worth a fourth attempt in
the same sitting. C and E were not reached. All five prompts are written and
identical in their shared constraints, so the round can be finished whenever the
service is behaving.

---

## CHOSEN — option A, the Sealed Hammer

Picked by Liam on 2026-09-09. Its page is the only one left in this directory;
the other four are deleted. What survives of the round is this README, the
winner's page with its production notes, the locked sheet at
`concept/drop-crusher/adopted/A-sheet.png`, and
`concept/round-1-contact-sheet.png`, which holds both drawn options at reduced
size.

**Chosen because the design ten versions converged on turned out to be sound**,
and the sheet is the first evidence of that rather than another assertion of it.
The stroke reads against the collar, the roof carries mechanism where the camera
looks, and the buttresses make the silhouette stepped rather than the plain drum
this page feared when it listed A's risks.

**What the round actually cost, and what it bought.** Two generations of five;
three prompts written and never drawn. Both drawn sheets landed inside vanilla's
saturation and edge-density bands, and both obeyed every hard constraint —
no chute, no pipe, no loose material, no glow, and the lamp painted white
everywhere except the state row.

**The runner-up is B, the Twin Tower**, and it is the one to go to if the Sealed
Hammer proves too close to the Vacuum Furnace and the Whisker Comber at stage 1.
Two peaks is a silhouette nothing else on this planet has, it moves ~70 % of its
box against A's ~33 %, and its sheet was the cleaner of the two on the
three-state row. It measured slightly darker (56.8 against 63.0) and slightly
less dense (0.146 against 0.158).

**The comparison this round did not get to make.** C, D and E were never drawn,
so the two strongest answers to the animation gate — the Beam Engine at ~85 %
and the Ratchet Crown at ~83 %, both of which put more of the machine in motion
than either sheet here — remain untested. If stage 1 finds the crown too small a
gesture, that is where to look, and the prompts are recoverable from this file's
history.
