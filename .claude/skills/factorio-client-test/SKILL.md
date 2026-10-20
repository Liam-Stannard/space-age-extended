---
name: factorio-client-test
description: Test this mod in a real Factorio client or headless server the agreed way: tools/client/launch.sh for every client, shot/ for screenshots of a building in each direction and state, measure-seeds/ for map-gen checks across seeds, audio/ for a building's sound against its animation. Use whenever a ticket needs the game itself, not just the data stage.
argument-hint: <task name> <what to test>
---

Every game client an agent starts goes through `tools/client/launch.sh`.
Nothing reaches Liam's desktop or speakers, one Factorio runs at a time,
and everything started is stopped.

## 1. Before any run
- `tools/check-data-stage.sh` passes on the worktree first. It takes the
  launcher's lock: while a client runs it waits (at most
  SAE_DATA_STAGE_LOCK_WAIT, default 600 s) and exits 3 if the lock is
  still held: the data stage was not checked, not failed. Do not run it
  during a capture: it can take the lock between capture.py's two
  launches, and the recording is refused.
- `pgrep -af factorio`: if one runs, wait for it (bounded); the launcher's
  lock refuses a second one anyway.
- Evidence goes to <repo>/evidence/<task>/ (git-ignored); name its paths.

## 2. Pick the tool
- A building in game: `tools/client/shot/shot.sh --task <t> --spec <json>`
  -- every direction and state (working, idle, no power, no input), day
  and night, each zoom, a motion series, contact sheets under 8000 px. Any
  caught error or missing frame fails the run.
- Map generation: `tools/client/measure-seeds/measure.py --task <t>
  --seeds-file seeds/pool-placed-30.txt --reference
  reference/pool-placed-30.csv` -- the pool and patches per seed on a local
  headless server; `rings.py` for the landing with its rings drawn.
- Sound: `tools/client/audio/capture.py --task <t> --spec <json>` -- an MP4
  (VP9, plays in Chrome/Firefox/VLC) of the building with its sound and
  accents.json of where each accent lands, all through a null sink, with a
  guard proving nothing reached the speakers. raw/ is deleted unless
  --keep-raw; exit 3 when the launcher refuses at either launch; MP4s are
  git-ignored (`*.mp4`).
- Anything else: `tools/client/launch.sh --task <t> [--audio]` with a probe
  mod of your own in scratch, following shot/'s mod.

## 3. Rules the tools enforce; keep them when you go around them
- no WAYLAND_DISPLAY; SDL_VIDEO_DRIVER=x11; a private Xvfb;
- --disable-audio unless the test is about sound, then --audio (null sink
  verified as default first, restored after);
- the scratch mod directory only: ~/.factorio/mods is never read;
- stop by PID, never pkill; a launcher that will not stop is reported
  (exit 5 and --recover), never killed blind.

## 4. Report
Each criterion PASS, FAIL or NOT RUN with its evidence path; the absolute
path of every screenshot, sheet and MP4 for Liam; whether anything is left
running (it must not be). Never judge the look or the sound.
