"""What a model tells the packers: render.json, and the names its renders take.

A model writes render.json beside its renders (declare(), below), and pack.py
and pack_ports.py read it (load()). Neither packer knows a building, a size or
a pass: everything they act on is declared here.

  footprint   [w, h] in tiles, as the model faces north
  canvas      [w, h] in sprite px of the renders beside this file; the entity
              origin is the canvas centre
  directions  "one", "four" (north, east, south, west) or
              "horizontal-vertical" (vertical = as modelled, horizontal = turned
              to face east). A model with more than one renders every pass per
              direction by turning its root about the vertical axis, camera
              fixed, into <pass>-<direction>.png
  passes      [{name, kind, sheet, over}], one render each per direction:
                plate   the machine; Appendix C is measured on it
                shadow  the ground catcher alone; packed black
                glow    this pass minus the `over` pass, drawn additively
                paint   this pass where it differs from the `over` pass, drawn
                        as ordinary paint over it: a working layer such as
                        frost, rime or a heat seam that the idle plate must not
                        carry, shown only while the machine works
                light   a white-cut lens the engine tints (alpha above 8 kept)
                still   every animation at frame 0 with the machine: the
                        reference for the frame-0 check; not packed
                remnants  the machine's wreck, what its corpse prototype draws once
                        it is destroyed: the wreck alone, lying on the ground
                        catcher, rendered so its shadow is caught in the same
                        picture -- vanilla's remnants have no shadow layer, the
                        shadow is baked into the one sprite -- with debris free to
                        lie past the footprint. Never cut (`cut`), like a shadow.
                        At most one. pack.py packs every direction's render into
                        one sheet in vanilla's layout (remnant_rows, below; its
                        docstring has the sheet and its checks), named for its
                        sheet alone, so the sheet may not be a name another sheet
                        or animation takes in any direction ("base-north") nor
                        "checks". Its own `canvas`
                        (optional, this kind only): [w, h] in sprite px, when the
                        wreck spreads past the model's canvas; the entity origin is
                        its centre too
  animations  [{name, frames, motion, path}], frames <name>-NN.png (and
              <name>-NN-<direction>.png). motion "turn": a part turning about
              its own axis, held to its centroid. motion "slide": a part moving
              in a straight line, whose `path` is its motion curve -- one
              [x, y, z] per frame, the part's offset in tiles as modelled
              (facing north; x east, y north, z up), the same numbers the model
              moves it by. Its centroid in every frame must land on that curve,
              and on its line, to within 1 px. A slide whose layer carries
              parts that do not move on the path (gears, a pawl, anything
              driven by it) names one that does in `track`: frames
              <name>-<track>-NN.png render that part alone, and the curve is
              held to their centroid instead; they are measured, not packed.
              motion "flow": contents moving in place -- gas or fluid in a
              sight glass, bubbles drifting through it -- with no part to hold
              to a centroid or a curve: no motion check (the model measures it).
              motion "cycle": parts running round a closed path -- a drag chain's
              flights, a belt -- whose layer has no one part to hold to a point or
              a line. Packed like any animation, with no positional check: the
              model is responsible for its frames closing the loop.
              working (optional, off by default): true marks a paint animation
              the engine draws only while the machine works -- ore particles,
              dust, with synced_fadeout -- so it is no part of the stopped machine
              and stays out of the frame-0 check, and a frame of it may be empty.
              kind (optional): "paint" (the default), drawn as ordinary paint
              and part of the stopped machine, so its frame 0 is held to the
              still; or "light", a white-cut layer the engine tints, packed as a
              light pass is (alpha above 8 kept) and drawn only while working,
              so it is not part of the still; or "glow", an animated glow layer
              (the radiant solution's light, tools/blender/radiant.py): each frame
              rendered as its own pass, the sun and sky off so it is the light
              alone and what it lights, drawn additively while working. It names
              in `over` the paint animation it is the light of -- its plate layer,
              with the same number of frames, frame for frame -- and its motion is
              "flow". Several glows may be over one plate layer (windows whose light
              is bloomed differently: radiant.py's per-shape bloom); the pack adds
              them all when it checks for clipping. Packed like any animation, as
              light (each frame's colour times its alpha), with an optional
              `bloom` [[radius px, gain], ...] added: for each stage the frame
              blurred by a Gaussian of that radius, times gain, all added back to
              it (vanilla's soft halo; the helper's is a tight halo and a wide
              tail). It fails the pack if any frame clips to white, alone or added
              to its plate layer's frame over the plate.
              turns (optional, a slide's): true (the default) when the model turns
              its root to face each direction, so the path turns with it; false when
              the root stays put in every direction (only some parts change with
              it), so the path is read as modelled in all of them
              frame_sequence (optional): the order the engine plays the frames in, for
              a motion that is not a plain loop -- one played once a craft with a rest
              between, as the reaction plant's press. Exactly the prototype's
              frame_sequence: frame numbers 1-based (k is the render <name>-<k-1>), in
              any order, repeated or not used at all, at most SEQUENCE_MAX (255)
              entries, the engine's limit on an animation's actual length
              (AnimationFrameSequence, 2.1). The frames are rendered and packed once
              each; the sequence only says how they play.
              hold (optional, instead of frame_sequence): {frame, entries, each}, the
              sequence a motion with a rest takes, written short: every frame in order,
              each `each` times (a whole number, default 1), then frame `frame` (1-based,
              as frame_sequence) `entries` times more. The press, 16 frames at 14 fps
              then shut for the rest of a 20 s craft at animation_speed 7/60:
              {"frame": 1, "entries": 108, "each": 2}, 2 x 16 + 108 = 140 entries.
              pack.py writes the sequence either one gives into meta.json, as
              frame_sequence beside the sheet's frames, and its length among the
              checks; preview.py --gif plays it. A glow animation declares neither: it
              is drawn frame for frame with its plate layer, so it plays that layer's
              sequence (sequence(), below)
              animation_speed (optional): the prototype's animation_speed, the entries
              (of frame_sequence, or the frames in order) the layer goes forward a tick
              at the machine's own speed: a number above 0, 1 (the engine's default)
              one a tick, 7/60 one every 60/7 ticks. Left out, the layer has no declared
              speed, and measure.py takes the engine's default, 1. Each layer may have
              its own, as a working_visualisation of its own; layers put together in one
              Animation's `layers` all run at the first one's speed (AnimationPrototype,
              2.1: "animation_speed ... of the first layer are used for all layers"), so
              give those one speed. pack.py copies it into meta.json; measure.py plays
              each layer at it. A glow animation declares none: it plays its plate
              layer's (speed(), below)
  ports       [{tile, face, neck}]: one fitting per face, `tile` the centre of the
              footprint tile it sits on (tiles, y down, entity centre 0,0, as a
              pipe connection's position), `face` N, E, S or W. Rendered with
              the model facing north, as port-<face>.png and cover-<face>.png.
              "neck": true (optional, off by default) keeps a part of the
              fitting joined to the rest only by a neck too faint for the noise
              floor -- a thin strip, as on assembler 3's west outline -- which
              pack_ports.py otherwise drops (its docstring says when to use it).
              Every face the ports reach must have a port declared on it: the
              engine draws each connection with the picture of the face it points
              to, whichever way the building stands. The faces the ports reach
              (reached_faces(), below) are each port's face turned clockwise -- N to
              E, E to S, S to W, W to N -- through every angle the model is
              rendered at (DIRECTIONS): 0 for "one", so a port reaches only its own
              face; 0 and 90 for "horizontal-vertical", so N reaches N and E, and S
              reaches S and W; 0, 90, 180 and 270 for "four", so any port reaches all
              four faces. With ports_turn true, through all four angles, whatever
              the directions. A face reached with no port on it fails the contract,
              naming the faces missing
  ports_turn  (optional; false when left out) true when the engine turns the
              ports through all four directions though the model is rendered in
              fewer: the Vacuum Furnace, drawn once, whose input turns with the
              building. Left out of render.json when not given, so a model without
              it declares what it always did
  rig         {elevation, px_per_tile}: the camera's, copied from rig.py by
              declare(), so the packers can put a tile on the screen
  cut         (optional; none when left out) the footprint's edges past which
              pack.py clears every render but the shadow's before it packs: the
              plate's pixels and a glow's own pixels go, so no part of the machine
              is drawn past them. Any of "E" and "W" (the plate no wider than the
              footprint) and "S" (nothing below its south edge). A glow animation's
              bloom is added after the cut, from what is left, so its halo may
              spill past a cut edge, as light does (Liam, 2026-10-19: "Halo may
              cross"). The edges
              are the footprint's as it stands in each direction, on the screen:
              east is the right in every direction, as in the world, not the
              model's own east face turned. Not "N": a building rises over its
              north edge, and a cut there would take its top off. Cut on the
              sprite-size renders, every pass and frame alike (the still too, so
              frame 0 still matches it; not a slide's tracked part, which is only
              measured, never drawn); a pixel the edge crosses keeps the share
              of its alpha inside. pack.py counts what it cleared (meta.json's
              cut_px, counted on the renders before any bloom is added) and
              preview.py draws the renders cut the same way.

Run as a script, it lists a render directory's plate renders, one per direction:
  python3 contract.py plates <render-dir>
"""
import json
import math
import os
import sys

DIRECTIONS = {
    "one": [("", 0)],
    "four": [("north", 0), ("east", 90), ("south", 180), ("west", 270)],
    "horizontal-vertical": [("vertical", 0), ("horizontal", 90)],
}
KINDS = ("plate", "shadow", "glow", "paint", "light", "still", "remnants")
# The engine direction each row of a remnants sheet is drawn for, top to bottom, and the render
# drawn in it: vanilla's building remnants are one column (line_length 1) of direction_count
# rows, north, east, south, west -- steam-turbine-remnants a 460x1632 sheet of four 460x408
# rows at scale 0.5 (base/prototypes/entity/remnants.lua:2739-2765) -- or one row for a
# building that does not turn (chemical-plant-remnants, remnants.lua:2907-2933). The steam
# turbine builds only north and east and its sheet still has four rows, the vertical wreck in
# 1 and 3, the horizontal in 2 and 4 (they differ in 50 and 118 px by 15 at most), so a
# horizontal-vertical model's two renders fill four rows the same way.
REMNANT_ROWS = {
    "one": [""],
    "four": ["north", "east", "south", "west"],
    "horizontal-vertical": ["vertical", "horizontal", "vertical", "horizontal"],
}
WORKING = ("glow", "paint")             # the kinds drawn over an `over` plate while working
MOTIONS = ("turn", "slide", "flow", "cycle")
ANIM_KINDS = ("paint", "light", "glow")
FACES = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}     # tiles, y down
FACE_ORDER = "NESW"                     # clockwise seen from above: a quarter turn is one step on
CUT_FACES = ("E", "W", "S")             # the footprint edges `cut` may name: not N
HOLD_KEYS = ("frame", "entries", "each")
SEQUENCE_MAX = 255                      # the engine's limit on an animation's actual length
FILE = "render.json"


class ContractError(Exception):
    """A model's declaration, or its renders, do not hold to the contract."""


def named(stem, direction):
    """A pass's or sheet's file stem in one direction."""
    return f"{stem}-{direction}" if direction else stem


def frame(anim, f, direction=""):
    return named(f"{anim}-{f:02d}", direction)


def track_frame(anim, track, f, direction):
    """A slide's tracked part, alone, in frame f: measured, never packed."""
    return frame(f"{anim}-{track}", f, direction)


def _played(anim):
    """The entries an animation that declares frame_sequence or hold plays, 1-based."""
    if "frame_sequence" in anim:
        return list(anim["frame_sequence"])
    h = anim["hold"]
    return [k for k in range(1, anim["frames"] + 1) for _ in range(h.get("each", 1))] + [h["frame"]] * h["entries"]


def sequence(decl, anim):
    """The frame_sequence the engine plays an animation in, 1-based as the prototype takes it:
    its own frame_sequence, its hold written out, or -- a glow -- its plate layer's. None when
    it plays its frames once each, in order."""
    if anim.get("kind") == "glow":
        anim = next(a for a in decl["animations"] if a["name"] == anim["over"])
    return _played(anim) if "frame_sequence" in anim or "hold" in anim else None


def speed(decl, anim):
    """The animation_speed the engine plays an animation at: its own, or -- a glow -- its plate
    layer's. None when it declares none (the engine then takes 1)."""
    if anim.get("kind") == "glow":
        anim = next(a for a in decl["animations"] if a["name"] == anim["over"])
    return anim.get("animation_speed")


def canvas_of(decl, p):
    """The canvas a pass's renders are on, [w, h] sprite px: its own (a remnants pass's) or the model's."""
    return p.get("canvas", decl["canvas"])


def remnant_rows(decl):
    """The render (its direction's name) drawn in each row of a remnants sheet, top to bottom:
    REMNANT_ROWS for the model's directions."""
    return REMNANT_ROWS[decl["directions"]]


def footprint_in(decl, direction):
    """The footprint as the engine sees it in a direction: turned a quarter, w and h swap."""
    w, h = decl["footprint"]
    deg = dict(DIRECTIONS[decl["directions"]])[direction]
    return (h, w) if deg % 180 else (w, h)


def each_direction(root, directions):
    """Turn `root` to face each direction in turn, yielding its name.

    Clockwise seen from above, as the engine turns a building: north (+Y, the
    way it was modelled) goes to east (+X). The camera and sun stay put, so the
    light falls on each face as it would in game.
    """
    for name, deg in DIRECTIONS[directions]:
        root.rotation_euler.z = -math.radians(deg)
        yield name
    root.rotation_euler.z = 0.0


def declare(out_dir, *, footprint, canvas, directions, passes=(), animations=(), ports=(), cut=None,
            ports_turn=None):
    """Write render.json into out_dir: called by a model, in Blender, before it renders."""
    import rig          # in Blender only: the packers read the numbers from render.json
    decl = dict(footprint=footprint, canvas=canvas, directions=directions,
                passes=passes, animations=animations, ports=ports,
                rig=dict(elevation=math.degrees(rig.ELEVATION), px_per_tile=rig.PX_PER_TILE))
    if cut is not None:
        decl["cut"] = cut   # left out when not given, so a model without one declares what it always did
    if ports_turn is not None:
        decl["ports_turn"] = ports_turn     # likewise
    validate(decl, out_dir)
    decl = json.loads(json.dumps(decl))     # as the packers will read it: tuples are lists
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, FILE), "w") as f:
        json.dump(decl, f, indent=1)
    return decl


def load(render_dir):
    path = os.path.join(render_dir, FILE)
    if not os.path.isfile(path):
        raise ContractError(f"{path} is missing: the model did not declare itself "
                            f"(contract.declare writes it beside the renders)")
    try:
        with open(path) as f:
            decl = json.load(f)
    except (ValueError, UnicodeDecodeError) as e:
        raise ContractError(f"{path}: is not JSON: {e}") from None
    validate(decl, path)
    return decl


def turned(face, deg):
    """A face turned clockwise seen from above by deg (a multiple of 90), as the engine turns a building."""
    return FACE_ORDER[(FACE_ORDER.index(face) + deg // 90) % 4]


def reached_faces(decl):
    """The faces the model's ports reach, in N, E, S, W order: each port's face turned through
    every angle the model is rendered at (0 alone for "one"; 0 and 90 for "horizontal-vertical";
    0, 90, 180 and 270 for "four"), or through all four when ports_turn is true. Each needs a
    port declared on it (the contract's docstring, `ports`)."""
    angles = (0, 90, 180, 270) if decl.get("ports_turn") else [deg for _, deg in DIRECTIONS[decl["directions"]]]
    reached = {turned(p["face"], deg) for p in decl["ports"] for deg in angles}
    return [f for f in FACE_ORDER if f in reached]


def _number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _whole(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _seq(v, n=None):
    return isinstance(v, (list, tuple)) and (n is None or len(v) == n)


def _stem(v):
    """A name that can be a file stem: a non-empty string with no path in it."""
    return isinstance(v, str) and v.strip() != "" and "/" not in v and "\\" not in v


def validate(decl, where):
    """Hold a declaration to the contract, naming the field that breaks it.

    Every field is checked for its type as well as its value, so nothing the
    packers read can fail on them later with a bare KeyError or TypeError.
    """
    def bad(field, msg):
        raise ContractError(f"{where}: {field}: {msg}")

    if not isinstance(decl, dict):
        raise ContractError(f"{where}: is a {type(decl).__name__}, not an object of fields")
    for key in ("footprint", "canvas", "directions", "passes", "animations", "ports", "rig"):
        if key not in decl:
            bad(key, "is not declared")
    if not isinstance(decl["directions"], str) or decl["directions"] not in DIRECTIONS:
        bad("directions", f"{decl['directions']!r} is not one of {', '.join(DIRECTIONS)}")
    for key, unit in (("footprint", "tiles"), ("canvas", "px")):
        v = decl[key]
        if not (_seq(v, 2) and all(_whole(c) and c > 0 for c in v)):
            bad(key, f"{v!r} is not [w, h], two whole numbers of {unit} above 0")
    rig = decl["rig"]
    if not isinstance(rig, dict):
        bad("rig", f"{rig!r} is not an object {{elevation, px_per_tile}}")
    if not (_number(rig.get("elevation")) and 0 < rig["elevation"] < 90):
        bad("rig.elevation", f"{rig.get('elevation')!r} is not an angle in degrees between 0 and 90")
    if not (_number(rig.get("px_per_tile")) and rig["px_per_tile"] > 0):
        bad("rig.px_per_tile", f"{rig.get('px_per_tile')!r} is not a number of px above 0")
    for key in ("passes", "animations", "ports"):
        if not _seq(decl[key]):
            bad(key, f"{decl[key]!r} is not a list")
        for i, item in enumerate(decl[key]):
            if not isinstance(item, dict):
                bad(f"{key}[{i}]", f"{item!r} is not an object")

    names, sheets = set(), set()
    for i, p in enumerate(decl["passes"]):
        field = f"passes[{i}]"
        if "name" not in p:
            bad(f"{field}.name", "is missing: every pass needs a name, its renders' file stem")
        if not _stem(p["name"]):
            bad(f"{field}.name", f"{p['name']!r} is not a name (a non-empty string, no path in it)")
        if p["name"] in names:
            bad(f"{field}.name", f"{p['name']!r} is declared twice")
        names.add(p["name"])
        if p.get("kind") not in KINDS:
            bad(f"{field}.kind", f"{p.get('kind')!r} is not one of {', '.join(KINDS)}")
        if p["kind"] != "still":
            if not _stem(p.get("sheet")):
                bad(f"{field}.sheet", f"{p.get('sheet')!r}: pass {p['name']!r} names no sheet to pack into")
            if p["sheet"] in sheets:
                bad(f"{field}.sheet", f"{p['sheet']!r} is already another pass's sheet")
            sheets.add(p["sheet"])
        if "canvas" in p:
            if p["kind"] != "remnants":
                bad(f"{field}.canvas", f"{p['kind']} pass {p['name']!r} has a canvas of its own: only a remnants "
                    f"pass may (every other pass is on the model's canvas, which the packers register them on)")
            v = p["canvas"]
            if not (_seq(v, 2) and all(_whole(c) and c > 0 for c in v)):
                bad(f"{field}.canvas", f"{v!r} is not [w, h], two whole numbers of px above 0")
    kinds = [p["kind"] for p in decl["passes"]]
    if decl["passes"] and kinds.count("plate") != 1:
        bad("passes", f"declares {kinds.count('plate')} plate passes; Appendix C needs exactly one")
    if kinds.count("remnants") > 1:
        bad("passes", f"declares {kinds.count('remnants')} remnants passes; a corpse draws one wreck")
    for i, p in enumerate(decl["passes"]):
        if p["kind"] in WORKING and not any(q["name"] == p.get("over") and q["kind"] == "plate"
                                            for q in decl["passes"]):
            bad(f"passes[{i}].over", f"{p['kind']} pass {p['name']!r} is over {p.get('over')!r}, "
                f"which is not a plate pass")

    for i, a in enumerate(decl["animations"]):
        field = f"animations[{i}]"
        if "name" not in a:
            bad(f"{field}.name", "is missing: every animation needs a name, its frames' file stem")
        if not _stem(a["name"]):
            bad(f"{field}.name", f"{a['name']!r} is not a name (a non-empty string, no path in it)")
        if a["name"] in sheets:
            bad(f"{field}.name", f"{a['name']!r} is already the name of a sheet: an animation packs "
                f"into a sheet of its own name")
        sheets.add(a["name"])
        if not (_whole(a.get("frames")) and a["frames"] >= 2):
            bad(f"{field}.frames", f"{a.get('frames')!r}: animation {a['name']!r} needs a whole "
                f"number of frames, at least two")
        if a.get("motion") not in MOTIONS:
            bad(f"{field}.motion", f"{a.get('motion')!r} is not one of {', '.join(MOTIONS)}")
        if a.get("kind", "paint") not in ANIM_KINDS:
            bad(f"{field}.kind", f"{a.get('kind')!r} is not one of {', '.join(ANIM_KINDS)}")
        if "working" in a and not isinstance(a["working"], bool):
            bad(f"{field}.working", f"{a['working']!r} is not true or false")
        if "turns" in a and not isinstance(a["turns"], bool):
            bad(f"{field}.turns", f"{a['turns']!r} is not true or false")
        if a.get("kind") == "glow":
            if a["motion"] != "flow":
                bad(f"{field}.motion", f"glow animation {a['name']!r} is {a['motion']!r}: a glow is light "
                    f"moving in place, motion \"flow\"")
            bloom = a.get("bloom")
            if bloom is not None and not (_seq(bloom) and bloom and all(
                    _seq(st, 2) and all(_number(c) for c in st) and st[0] > 0 and st[1] >= 0 for st in bloom)):
                bad(f"{field}.bloom", f"{bloom!r} is not [[radius, gain], ...]: one stage or more, each a "
                    f"radius in px above 0 and a gain of 0 or more")
        if a["motion"] == "slide":
            path = a.get("path")
            if not (_seq(path, a["frames"]) and all(_seq(p, 3) and all(_number(c) for c in p) for p in path)):
                bad(f"{field}.path", f"slide {a['name']!r} needs a path of {a['frames']} [x, y, z] "
                    f"offsets in tiles, one per frame")
            steps = [[c - c0 for c, c0 in zip(p, path[0])] for p in path]
            far = max(steps, key=lambda v: math.hypot(*v))
            track = a.get("track")
            if track is not None and not _stem(track):
                bad(f"{field}.track", f"{track!r} is not a name: the part whose own frames the "
                    f"slide is measured on")
            if math.hypot(*far) == 0:
                bad(f"{field}.path", f"slide {a['name']!r} has a path that does not move")
            for v in steps:             # every offset parallel to the longest: one straight line
                cross = (v[1] * far[2] - v[2] * far[1], v[2] * far[0] - v[0] * far[2], v[0] * far[1] - v[1] * far[0])
                if math.hypot(*cross) > 1e-6 * math.hypot(*far) * max(1.0, math.hypot(*v)):
                    bad(f"{field}.path", f"slide {a['name']!r} has a path that is not a straight line")
        given = [k for k in ("frame_sequence", "hold") if k in a]
        if len(given) == 2:
            bad(f"{field}.hold", f"animation {a['name']!r} declares both frame_sequence and hold: a hold is "
                f"a frame_sequence written short, so one or the other")
        if given and a.get("kind") == "glow":
            bad(f"{field}.{given[0]}", f"glow animation {a['name']!r} is drawn frame for frame with its plate "
                f"layer {a.get('over')!r} and plays its sequence: declare the sequence there")
        if "animation_speed" in a:
            v = a["animation_speed"]
            if a.get("kind") == "glow":
                bad(f"{field}.animation_speed", f"glow animation {a['name']!r} is drawn frame for frame with its "
                    f"plate layer {a.get('over')!r} and plays at its speed: declare the speed there")
            if not (_number(v) and v > 0):
                bad(f"{field}.animation_speed", f"{v!r} is not a number above 0: the entries the layer goes "
                    f"forward a tick, as the prototype's animation_speed (1 = one a tick)")
        n = a["frames"]
        if "frame_sequence" in a:
            s = a["frame_sequence"]
            if not (_seq(s) and s and all(_whole(k) and 1 <= k <= n for k in s)):
                bad(f"{field}.frame_sequence", f"{s!r} is not a list of frame numbers, 1-based as the "
                    f"engine's: each a whole number from 1 to {n}, and at least one")
        if "hold" in a:
            h = a["hold"]
            if not (isinstance(h, dict) and {"frame", "entries"} <= set(h) and set(h) <= set(HOLD_KEYS)):
                bad(f"{field}.hold", f"{h!r} is not {{frame, entries}} with an optional each, and nothing else")
            if not (_whole(h["frame"]) and 1 <= h["frame"] <= n):
                bad(f"{field}.hold.frame", f"{h['frame']!r} is not a frame number from 1 to {n} (1-based, "
                    f"as frame_sequence): the frame held")
            if not (_whole(h["entries"]) and h["entries"] >= 1):
                bad(f"{field}.hold.entries", f"{h['entries']!r} is not a whole number above 0: the entries "
                    f"the frame is held for, after the frames have played")
            if not (_whole(h.get("each", 1)) and h.get("each", 1) >= 1):
                bad(f"{field}.hold.each", f"{h['each']!r} is not a whole number above 0: the entries each "
                    f"frame plays for")
        if given and len(_played(a)) > SEQUENCE_MAX:
            bad(f"{field}.{given[0]}", f"animation {a['name']!r} plays {len(_played(a))} entries; the engine "
                f"allows an animation {SEQUENCE_MAX} at most (AnimationFrameSequence)")
    for i, a in enumerate(decl["animations"]):
        if a.get("kind") != "glow":
            continue
        under = next((b for b in decl["animations"] if b["name"] == a.get("over")), None)
        if under is None or under.get("kind", "paint") != "paint":
            bad(f"animations[{i}].over", f"glow animation {a['name']!r} is over {a.get('over')!r}, which "
                f"is not a paint animation: a glow names the plate layer it is the light of")
        if under["frames"] != a["frames"]:
            bad(f"animations[{i}].frames", f"glow animation {a['name']!r} has {a['frames']} frames and "
                f"its plate layer {under['name']!r} {under['frames']}: one glow frame per plate frame")
    # A remnants sheet is one file for every direction, named for its sheet alone, where every
    # other sheet is named per direction: it must not be the name another sheet takes in some
    # direction (pack.py would write one over the other), nor meta.json's "checks".
    for i, p in enumerate(decl["passes"]):
        if p["kind"] != "remnants":
            continue
        others = [q["sheet"] for q in decl["passes"] if q["kind"] not in ("still", "remnants")] \
            + [a["name"] for a in decl["animations"]]
        taken = {named(s, d): s for s in others for d, _ in DIRECTIONS[decl["directions"]]}
        if p["sheet"] in taken:
            bad(f"passes[{i}].sheet", f"{p['sheet']!r} is the name sheet {taken[p['sheet']]!r} takes in one of the "
                f"model's directions: a remnants sheet is one file for every direction, and would be written over it")
        if p["sheet"] == "checks":
            bad(f"passes[{i}].sheet", "'checks' is meta.json's key for the checks, not a name a sheet can take")
    if any(a.get("kind", "paint") == "paint" for a in decl["animations"]) and decl["passes"] \
            and "still" not in kinds:
        bad("passes", "declares animations but no still pass to hold their frame 0 to")

    if "cut" in decl:
        cut = decl["cut"]
        if not (_seq(cut) and all(isinstance(f, str) and f in CUT_FACES for f in cut) and len(set(cut)) == len(cut)):
            bad("cut", f"{cut!r} is not a list of footprint edges to cut at, each once, of "
                f"{', '.join(CUT_FACES)} (not N: a building rises over its north edge)")

    w, h = decl["footprint"]
    faces = set()
    for i, p in enumerate(decl["ports"]):
        field = f"ports[{i}]"
        if not isinstance(p.get("face"), str) or p["face"] not in FACES:
            bad(f"{field}.face", f"{p.get('face')!r} is not one of N, E, S, W")
        if p["face"] in faces:
            bad(f"{field}.face", f"a second port on face {p['face']}: the engine draws one picture per face")
        faces.add(p["face"])
        if "neck" in p and not isinstance(p["neck"], bool):
            bad(f"{field}.neck", f"{p['neck']!r} is not true or false")
        if not (_seq(p.get("tile"), 2) and all(_number(c) for c in p["tile"])):
            bad(f"{field}.tile", f"{p.get('tile')!r} is not [x, y] in tiles")
        x, y = p["tile"]
        edge = {"N": y == -h / 2 + 0.5, "S": y == h / 2 - 0.5,
                "E": x == w / 2 - 0.5, "W": x == -w / 2 + 0.5}[p["face"]]
        inside = abs(x) <= w / 2 - 0.5 and abs(y) <= h / 2 - 0.5 and (x - (w - 1) / 2) % 1 == 0 \
            and (y - (h - 1) / 2) % 1 == 0
        if not (edge and inside):
            bad(f"{field}.tile", f"{list(p['tile'])} is not a tile centre on the {p['face']} edge "
                f"of a {w}x{h} footprint")
    if "ports_turn" in decl and not isinstance(decl["ports_turn"], bool):
        bad("ports_turn", f"{decl['ports_turn']!r} is not true or false")
    missing = [f for f in reached_faces(decl) if f not in faces]
    if missing:
        how = ("ports_turn turns them through all four directions" if decl.get("ports_turn")
               else f"directions {decl['directions']!r} turns them through "
               f"{', '.join(str(deg) for _, deg in DIRECTIONS[decl['directions']])} degrees")
        bad("ports", f"the ports reach face(s) {', '.join(missing)}, which no port is declared on: {how} "
            f"(declared: {', '.join(sorted(faces, key=FACE_ORDER.index))}), and the engine draws a "
            f"connection with the picture of the face it points to; declare a port on each")


def screen(decl, offset, direction):
    """A model-space offset (tiles: x east, y north, z up, as modelled) in screen px
    (x right, y down) once the building is turned to `direction`.

    The ground projects square (rig.py's STRETCH), so a tile across the ground is
    px_per_tile on the screen either way; a tile of height is cos(elevation) of that.
    """
    a = -math.radians(dict(DIRECTIONS[decl["directions"]])[direction])
    x, y, z = offset
    east, north = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
    ppt = decl["rig"]["px_per_tile"]
    return east * ppt, -(north + z * math.cos(math.radians(decl["rig"]["elevation"]))) * ppt


def outside(port):
    """Centre of the tile the port points into, which the engine draws its pipe picture from."""
    dx, dy = FACES[port["face"]]
    return port["tile"][0] + dx, port["tile"][1] + dy


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "plates":
        sys.exit("usage: contract.py plates <render-dir>")
    try:
        d = load(sys.argv[2])
    except ContractError as e:
        sys.exit(str(e))
    plate = next(p["name"] for p in d["passes"] if p["kind"] == "plate")
    for direction, _ in DIRECTIONS[d["directions"]]:
        print(os.path.join(sys.argv[2], named(plate, direction) + ".png"))
