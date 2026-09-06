# Art pass — running checklist

Live tracker for the session that started 2026-09-05. `TODO.md` is the standing
record of what the art *is*; this is what is being done to it right now. Tick as
you go, and keep the "how it was verified" column honest — "looks fine" is not a
verification, and this repo has a long history of that costing rounds.

## A. Defects found in the first in-game test

| | Item | State | Verified by |
| - | ---- | ----- | ----------- |
| A1 | Store ring dark while fully charged | **done** | Cause: `chargable_graphics` has no charge-level slot; the two animations are one-shots on charge events. Ring moved into `picture` as an always-on additive glow at 90%. |
| A2 | Bed Tender arm floating above the hub | **done** | `crane.origin` z 4.6 → 2.75, the 1.85 tiles measured off the screenshot at 37.3 px/tile. |
| A3 | Re-verify A1 and A2 in a client | open | Needs the game. |

## B. Assets that were still vanilla placeholders

| | Item | State | Verified by |
| - | ---- | ----- | ----------- |
| B1 | Whisker bed tile was stone path | **done** | Recoloured from vanilla's sheets so the tiling contract survives; luminance 60 vs the Core's basalt at 22; all 26 resolved paths checked against the engine's data-raw dump. |
| B2 | Whisker plant renders as a Gleba tree | **done** | Four kamacite whisker clusters replacing vanilla's eight trees (checked: vanilla's are same-size visual variants in a 4x2 grid, not a growth sequence). 1.94-2.11 tiles wide, alpha zero on all four edges. Engine dump: **0 references to Gleba's planted-tree left**, 4/4/4 variations, mining throws metal particles not yumako leaves, selection box brought down from a tree's 3.8 tiles to the clump's 2.0. |
| B3 | Bed Tender crane is vanilla's tower arm | **done — now bespoke** | Superseded by real art: seven parts drawn once each and stamped across their rotation sheets by `build-crane-sheets.py`, placed on the **median content box of vanilla's own frames** so the joints still meet. All 29 sheets match vanilla's dimensions, **0 mismatches**. Shadows remain vanilla's shape. Previously (still true of the rest of the set): recoloured, not redrawn: the crane is a 9-part turntable, 64-128 rotation frames per part, 29 files / 37.7 Mpx, rendered from a 3D model — no generator can produce 64 consistent angles. Vanilla runs hue 20-70 at body luminance 72-150; ours runs 65-123 with the same part-to-part spread. Engine dump: 42 paths resolve, 33 ours, **0 vanilla crane sheets left**. Movement is still vanilla's. **Correction, same session:** a bespoke crane is *not* out of reach — the engine does the rotation (all 128 frames are drawn vertical; `direction_count = 128` on `rotated_sprite`), so one canonical image per part replicated across the direction slots would work. See building-spec-bed-tender.md section 20. |

## C. Buildings

| | Building | State | Verified by |
| - | -------- | ----- | ----------- |
| C0 | Arc Mast | done (earlier session) | Re-measured this session: centred, 3.000 tiles, sheets fit their grids. |
| C1 | Bed Tender | **done** | 3.000 tiles; 3 in a row overlap 90 px at alpha > 1 and **0 px above alpha 80**. |
| C2 | Superconducting Store | **done** | 2.000 tiles; ring glow found on the plate's own groove; charge sweeps around the channel. |
| C3 | Sealed Roboport | **done** | 4.000 tiles; 2×2 block tiles cleanly. Three vanilla slots deliberately emptied — see the prototype comment. |
| C4 | Radiant Generator | **done** | Two plates, one per direction axis, drawn not rotated. North/south **3.000 tiles** wide, deck 4.95 of 5.00; east/west **5.000 tiles** wide, deck 3.20 of 3.00 (over-deep, so it overhangs rather than gaps). Both edges clear and centred to 0.0 px. Glow split out by hue rather than differenced — one generation per direction. Horizontal took three rounds: 0.39 → 0.43 → 0.51, the jump coming from a **square** canvas rather than 3:2, which had been pushing a flat composition. |
| C5 | Vent Pump | open | |
| C6 | Ignition Array | **base plate done** | **9.000 × 8.969 tiles**, centred to 0.0 px, edges clear, palette in range at luminance 82. Every launch-pad slot emptied — blast doors, engine bell, steam vents, extractor fans, rocket overlays — because on a world whose premise is that nothing leaves, each is a lie *and* would draw over our deck. **Still open:** the iris halves, the shaft and its light, the cradle lamps, the 64-frame crafting glow, and the replacement rocket entity of §6.1. |

## D. Review

| | Item | State |
| - | ---- | ----- |
| D1 | Each building re-read against its master spec §13/§17/§18 | **done — all pass** |
| D2 | Each building exercised in a client, not just loaded | open |
| D3 | Specs and `TODO.md` brought up to date | open |

## Tooling changed this session

- `tools/collect-graphics-refs.py` — new. `check-graphics.sh` could not see
  `ART .. "base.png"`, so it had **never checked a single building plate**.
  52 → 64 references.
- `process-building-art.py` — `--bottom-margin` (no cut plate could pass the
  pipeline's own edge check without it), `--stretch-y`, and a de-key that reads
  both checkerboard greys off the border and drops islands.
- `derive-glow.py` — mirrors the two new cutting options, or the glow lands
  where the plate is not.
- `build-glow-frames.py` — `--mode ring`. Column mode still reproduces the arc
  mast's shipped sheets byte for byte.
- `ring-glow.py` — new; finds a recessed ring on a plate and lights it.
- `build-whisker-bed-tile.py` — new.
- `check-data-stage.sh` — runs against a scratch write-data directory, so it
  works with a client open instead of demanding the lock.
- `recolour-crane.py` — new; the Bed Tender's arm, from vanilla's turntable.
- `check-dumped-graphics.py` — new, and the important one. Checks paths **as the
  engine resolved them**, out of the data-raw dump, so it sees the ones Lua
  builds by concatenation or `gsub`. `check-graphics.sh` sees 65 files; this sees
  **387**, of which 112 are the mod's own. It caught the radiant generator's
  plates going unchecked on the same day `collect-graphics-refs.py` was written.
- `check-data-stage.sh` — also fixed a bug this session introduced: after the
  scratch-directory change the recipe check was still reading the **stale** dump
  from `~/.factorio`, answering questions about a mod that no longer existed.
- `split-glow.py` — new. The reverse of `derive-glow.py`: generate the machine
  **lit** and take the light back out by hue, for when the lit twin will not
  come. Closes the mask before using it, because an emissive slot's burnt-out
  core has no hue and fails the window that catches its own rim.

## D1 — the review, measured

Every colour plate the mod ships, checked against the tile span its own spec
calls load-bearing. Declared size is what the prototype tells the engine; actual
is what the file is.

| Building | Declared | Actual | Span | Target | Centred | Edges clear | Body lum |
| -------- | -------- | ------ | ---- | ------ | ------- | ----------- | -------- |
| Arc Mast | 224×345 | 224×345 | 3.000 | 3.00 | +0.0 | **no — bottom 255** | 84 |
| Bed Tender | 224×189 | 224×189 | 3.000 | 3.00 | +0.0 | yes | 81 |
| Superconducting Store | 160×164 | 160×164 | 2.000 | 2.00 | +0.0 | yes | 101 |
| Sealed Roboport | 288×306 | 288×306 | 4.000 | 4.00 | +0.0 | yes | 81 |
| Radiant Generator N/S | 224×414 | 224×414 | 3.000 | 3.00 | +0.0 | yes | 61 |
| Radiant Generator E/W | 352×233 | 352×233 | 5.000 | 5.00 | +0.0 | yes | 74 |
| Ignition Array | 608×602 | 608×602 | 9.000 | 9.00 | +0.0 | yes | 82 |

Declared equals actual everywhere, every span is exact, everything is centred.
Two notes, neither a blocker:

* **The arc mast's bottom edge is alpha 255** — it was cut before
  `--bottom-margin` existed, so it ends on a razor line with no antialiased rim.
  It is another session's plate and was left alone; recutting is a one-command
  fix whenever that session is done with it.
* **Radiant Generator N/S measures 61** against the §3.3 floor of 70, and the
  Store measures 101 against a ceiling of 105. Both are inside the tolerance
  `--report` uses and neither reads wrong beside its neighbours, but the
  generator is the darkest thing the mod ships and is worth a look in a client
  against the Core's basalt, which is itself dark.
