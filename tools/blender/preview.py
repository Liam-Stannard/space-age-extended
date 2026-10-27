#!/usr/bin/env python3
"""A model's review sheet: its renders composited the way the engine layers them.

  python3 preview.py <render-dir> <out.png> [--adopted <png> [...]] [--day-only]
  python3 preview.py <render-dir> <out.gif> --gif <animation> --speed <animation_speed> [--day-only]

<render-dir> is render.sh's <out-dir>/renders. What to draw comes from its
render.json (contract.py): every pass and frame there is on one canvas, at
sprite size, with the entity origin at its centre, so the layers register by
construction and nothing is placed by hand.

The sheet has two rows per direction, by day and under it at night (below), every panel
on one ground with the footprint's tile grid drawn over it (the footprint itself brighter):

  idle      each shadow pass at 50 %, the plate, each animation at frame 0 (but
            those marked working), and each light pass tinted as the engine tints
            the status lamp when idle
  working   the same, with the working layers in the order render.json declares
            them, each as pack.py packs it: a paint pass drawn as paint, a glow
            pass added, a glow animation's frame added over the animations; the
            lamp tinted as when working

A model that declares a remnants pass (contract.py) gets a third panel in each row, its
wreck: the render as pack.py packs it (cleaned of the catcher's haze, never cut), shadow and
all, on the same ground and grid, so the debris past the footprint shows against it. The
panels grow to the wreck's own canvas when it is larger. A model without one draws as it
always did. A wreck that declares a glow (the remnants pass's `glow`) has it added over the
wreck, as pack.py packs it (its render minus the wreck's, kept to its light box, rolled off).

The night view (T08f; the default since T08f-2, Liam 2026-10-21: "Night by default") puts a
second row under each direction's, every panel under its day one: the same panel at night. The
model of night is the simplest the engine's rules allow: every layer drawn as by day, in the
same order, but each layer the engine darkens -- the ground, the plate, a paint pass, each
paint animation's frame, the wreck -- with its colour times NIGHT (0.15: the Core's darkest,
darkness 0.85, its min_brightness), and every layer drawn as a glow (draw_as_glow, which shows
day and night at full colour) as by day: a glow pass and a glow animation added, a light pass's
lamp and a light animation drawn over, the wreck's glow added. The shadow, black, is as by day.
So a glow on top of everything is the scene times 0.15 with the glow added. The adopted plate is
vanilla's, whose glows are not known here: its night panel is left empty. The grid is drawn as by
day. --day-only leaves the night rows out, every one (a wreck's glow is then seen by day only): one
row per direction, byte for byte the sheet from before the night view, but for a wreck's glow,
which that did not draw, and a glow's haze, which it did (below). --night, the default, is still
taken.

What a prototype draws only in the dark -- a LightDefinition, a draw_as_light layer -- no render
carries: a model declares it (render.json's `lights`, contract.py; T08g, Liam 2026-10-21: "Declare
them"), and the building's night panels draw it -- never a day panel, nor the wreck's, which the
building's lights do not reach; a light declared working, in the working panel alone. An
approximation of the engine's light, kept as simple as the night itself: a light raises the
brightness the scene is drawn at, from 0.15 towards the day's. Each light is a picture of light --
a layer's own picture, read from the game's data (<FACTORIO_ROOT>/data, tools/paths.conf), or
for a definition __core__/graphics/light-medium.png -- each channel times its alpha (the engine
premultiplies a sprite as it loads it: BlendMode, 2.1), sized and centred where the prototype puts
it (a layer's picture at its scale, 32 px of it a tile at 1; a definition's 2 x size tiles across,
size being the radius: LightDefinition, 2.1), times its colour (a layer's tint, its alpha left out;
a definition's intensity times its color). The lights are added up into one map, and each layer
the night darkens is drawn at NIGHT plus the map there, at most 1 (the day), instead of NIGHT: each
channel times min(1, 0.15 + light), rounded. So a light lights what is under it in its own colour,
the ground and the machine alike, never brighter than by day; the night row's ground past the
canvas too. Glows, the lamp and the shadow are as without it. Where no light reaches, the panel is
as without any, byte for byte. Not modelled: how the engine blends lights that overlap (here they
add), whether it caps them at the day as here, the picture it draws a definition with
(light-medium.png is this preview's stand-in), a definition's minimum_darkness and flicker. Judge a
light's look in a client: the preview shows where it falls and roughly how strong it is.

--adopted puts the adopted plate(s) first in each row, one per direction in the
order render.json lists them, on the same ground at the same scale (a sheet's
px_per_tile px to a tile, as the engine draws a high-resolution sprite) with the
same grid: the review sheet the artist's definition asks for. Each is centred
on the entity origin and moved by its shift, given in tiles after an @ as its
prototype gives it -- the vanilla chemical plant's north base, for one, is
util.by_pixel(0, -9) in the prototype plus by_pixel(1, 0) in its .lua:

  --adopted chemical-plant-north-base.png@0.03125,-0.28125

--gif writes a looping GIF of one animation playing in the working panel, every
direction side by side, at game speed: 60 x animation_speed frames a second, by day
only (--night is refused with it; --day-only, what it draws anyway, is taken). A
glow animation, the plate layer it is over and every other glow over that layer
play together, whichever is named.
A GIF counts time in hundredths of a second, so each frame is held to the
nearest hundredth of when the engine would show it and the loop as a whole
runs at the game's rate. An animation that declares a frame_sequence or a hold
(contract.py) plays in that order, a held frame shown for as long as its run of
entries lasts; a glow plays its plate layer's.

Every render but a shadow is drawn cut to the footprint as pack.py cuts it, when
render.json declares a `cut`: cut first, then a glow animation's bloom added, so the
halo may spill past a cut edge as it does in the sheets.

A glow -- a glow pass, a glow animation's frame, the wreck's glow -- adds its colour only where its
alpha is above 0, by day and at night (T08f-3; Liam, 2026-10-21: "Fix in preview, day and night"):
pack.glow_layer leaves a glow pass's faint difference from its plate (at or under LAYER_FLOOR) as
colour on pixels it leaves clear, and pack.add_light adds colour whatever the alpha, so drawn as
they came they put a faint haze over the whole panel, far past the sheet's crop. A glow
animation's frame carries no colour where it is clear, so it draws as it did; a glow pass's (and a
wreck glow's) may, so a glowing model's working panel can be a little darker than before, by day
too, wherever that haze lay.

Every layer but a shadow or a light is drawn through pack.py's highlight roll-off (pack.roll),
as its sheet carries it -- the plate, a paint or glow pass's layer, each animation's frame but a
light one's, the wreck -- each before it is drawn over the rest, so the review is what ships
(Liam, 2026-10-20: "Match shipped"). A model whose render.json opts out (rolloff false) is drawn
as it was before the roll-off, byte for byte.
"""
import argparse
import os
import sys
from PIL import Image, ImageChops, ImageDraw, ImageMath

sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # tools/paths.py
import contract  # noqa: E402
import pack  # noqa: E402
import paths  # noqa: E402

GROUND = (74, 66, 58, 255)
GAP = (30, 30, 30, 255)                 # between panels
GRID = (255, 255, 255, 40)
FOOTPRINT = (255, 255, 255, 110)
# the status lamp's colours, idle and working: vanilla's electric mining drill's
# status_colors, which the reaction plant copies
LAMP = {False: (255, 0, 0, 255), True: (0, 255, 0, 255)}
LABEL = 14                              # px of label strip over each panel
PAD = 8
# the scene's brightness at night: the Core's darkness 0.85 at its darkest (min_brightness 0.15)
NIGHT = 0.15
DEFINITION_PICTURE = "__core__/graphics/light-medium.png"     # this preview's stand-in for a LightDefinition's
SPRITE_PX_PER_TILE = 32                 # a sprite's px to a tile at scale 1


class Lights:
    """The light that reaches each px of a panel at night (the module's docstring): per channel the
    lights added up (sums, "F"), and the brightness the scene is drawn at there, min(1, NIGHT + it)."""

    def __init__(self, sums):
        self.sums = sums
        self.k = [ImageMath.lambda_eval(lambda e: e["min"](e["s"] + NIGHT, 1.0), s=c) for c in sums]
        # where any light reaches: elsewhere the scene is drawn at NIGHT, as without lights
        self.mask = ImageMath.lambda_eval(lambda e: (e["r"] + e["g"] + e["b"] > 0) * 255,
                                          r=sums[0], g=sums[1], b=sums[2]).convert("L")

    def crop(self, box):
        return Lights([c.crop(box) for c in self.sums])

    def dim(self, im):
        """im (RGBA) at night under these lights: each channel times its brightness, rounded, alpha
        kept; where no light reaches, dim(im, NIGHT) byte for byte."""
        base = dim(im, NIGHT).split()
        lit = [ImageMath.lambda_eval(lambda e: e["v"] * e["k"] + 0.5, v=c.convert("F"), k=k).convert("L")
               for c, k in zip(im.split()[:3], self.k)]
        return Image.merge("RGBA", [Image.composite(li, b, self.mask) for li, b in zip(lit, base[:3])] + [base[3]])


def dim(im, by):
    """im (RGBA) with its colour times by, its alpha kept; im itself when by is 1 (the day). by may be
    Lights: the night under them."""
    if isinstance(by, Lights):
        return by.dim(im)
    if by == 1:
        return im
    r, g, b, a = im.split()
    return Image.merge("RGBA", [c.point(lambda v: round(v * by)) for c in (r, g, b)] + [a])


def add_glow(under, glow):
    """under (RGBA) with a glow added as pack.add_light adds it (RGB only, under's alpha kept), but
    only where the glow's alpha is above 0: its colour on a clear pixel is not drawn (the module's
    docstring, T08f-3)."""
    seen = glow.getchannel("A").point(lambda v: 255 if v else 0)
    lit = ImageChops.multiply(glow.convert("RGB"), Image.merge("RGB", (seen,) * 3))
    return pack.add_light(under, lit)


def ground(by=1):
    """The ground's colour, by day (by 1) or at night (NIGHT)."""
    return GROUND if by == 1 else tuple(round(c * by) for c in GROUND[:3]) + (255,)


def ground_im(size, by=1):
    """The ground, size px: by day, at night, or at night under Lights."""
    if isinstance(by, Lights):
        return by.dim(Image.new("RGBA", size, GROUND))
    return Image.new("RGBA", size, ground(by))


def game_picture(filename):
    """A picture as a prototype names it (__<mod>__/<path>), read from the game's data (tools/paths.conf)."""
    mod, _, rest = filename[2:].partition("__/")
    path = os.path.join(paths.factorio_data(), mod, rest)
    if not os.path.isfile(path):
        sys.exit(f"preview.py: a declared light's picture {filename} is not at {path}: FACTORIO_ROOT in "
                 f"{paths.CONF} names no install with it")
    return Image.open(path).convert("RGBA")


def premultiplied(im):
    """A light's picture as the engine loads it: each channel times its alpha, 0 to 1 ("F" each)."""
    a = im.getchannel("A").convert("F")
    return [ImageMath.lambda_eval(lambda e: e["c"] * e["a"] / 65025.0, c=c.convert("F"), a=a)
            for c in im.split()[:3]]


class Model:
    def __init__(self, src):
        self.src = src
        try:
            self.decl = contract.load(src)
        except contract.ContractError as e:
            sys.exit(f"preview.py: {e}")
        if not self.decl["passes"]:
            sys.exit(f"preview.py: {src}/render.json declares no passes to draw")
        gone = pack.missing(src, self.decl)
        if gone:
            sys.exit(f"preview.py: {src} is missing {len(gone)} declared render(s):\n" +
                     "\n".join(f"  {stem}.png  ({what})" for what, stem in gone))
        self.directions = [d for d, _ in contract.DIRECTIONS[self.decl["directions"]]]
        self.ppt = float(self.decl["rig"]["px_per_tile"])
        self.masks = {d: pack.cut_mask(self.decl, d) for d in self.directions}
        self.roll_on = self.decl.get("rolloff", True)
        self.pictures = {}                  # a declared light's picture by filename: its size, premultiplied

    def picture(self, li):
        """A light's picture, premultiplied (the module's docstring); a layer's held to its width and height."""
        name = li.get("filename", DEFINITION_PICTURE)
        if name not in self.pictures:
            im = game_picture(name)
            self.pictures[name] = (im.size, premultiplied(im))
        size, pic = self.pictures[name]
        if li["kind"] == "layer" and size != (li["width"], li["height"]):
            sys.exit(f"preview.py: light {li['name']!r}: {name} is {size[0]}x{size[1]}, but render.json "
                     f"declares it {li['width']}x{li['height']} (one frame: the whole picture)")
        return pic

    def light_map(self, d, working, size, centre):
        """The lights that reach a panel of size px in direction d, the entity origin at centre (Lights), or
        None when the model declares none that are drawn (a working one only while working)."""
        shown = [li for li in self.decl.get("lights", ()) if working or not li.get("working")]
        if not shown:
            return None
        sums = [Image.new("F", size, 0.0) for _ in range(3)]
        for li in shown:
            shift = li["shift"][d] if isinstance(li["shift"], dict) else li["shift"]
            if li["kind"] == "definition":
                w = h = 2 * li["size"] * self.ppt
                mult = [li["intensity"] * c for c in li.get("color", (1, 1, 1))]
            else:
                w, h = (li[k] * li["scale"] * self.ppt / SPRITE_PX_PER_TILE for k in ("width", "height"))
                mult = li.get("tint", (1, 1, 1))[:3]
            w, h = max(1, round(w)), max(1, round(h))
            at = (round(centre[0] + shift[0] * self.ppt - w / 2), round(centre[1] + shift[1] * self.ppt - h / 2))
            for c, (pic, m) in enumerate(zip(self.picture(li), mult)):
                one = Image.new("F", size, 0.0)
                one.paste(pic.resize((w, h), Image.Resampling.BILINEAR), at)
                sums[c] = ImageMath.lambda_eval(lambda e: e["s"] + e["one"] * e["m"], s=sums[c], one=one, m=m)
        return Lights(sums)

    def shipped(self, im):
        """A layer as its sheet carries it: rolled off (pack.roll), unless the model opts out."""
        return pack.roll(im)[0] if self.roll_on else im

    def open(self, stem, d, cut_it=True, canvas=None):
        """A render of direction d, cut to the footprint as pack.py cuts it (render.json's `cut`)
        unless cut_it is false: a shadow is never cut. canvas: the size it must be, when not the
        model's (a remnants pass's own)."""
        im = Image.open(os.path.join(self.src, stem + ".png")).convert("RGBA")
        want = list(canvas or self.decl["canvas"])
        if list(im.size) != want:
            sys.exit(f"preview.py: {stem}.png is {im.size[0]}x{im.size[1]}, but render.json "
                     f"declares a {want[0]}x{want[1]} canvas")
        if cut_it and self.masks[d] is not None:
            im = pack.cut(im, self.masks[d])[0]
        return im

    def kind(self, kind):
        return [p for p in self.decl["passes"] if p["kind"] == kind]

    def panel(self, d, working, frames=None, night=False, light=None):
        """The building in direction d on the ground, at canvas size. frames: {animation: frame}, else 0.
        night: at night (the module's docstring), every layer but a glow or a light darkened, under the
        model's declared lights; light: those lights (Lights) at canvas size, when the caller has them."""
        frames = frames or {}
        k = NIGHT if night else 1
        plate = self.open(contract.named(self.kind("plate")[0]["name"], d), d)
        if night:
            k = light or self.light_map(d, working, plate.size, (plate.width / 2, plate.height / 2)) or k
        im = ground_im(plate.size, k)
        black = Image.new("RGBA", plate.size, (0, 0, 0, 255))
        for p in self.kind("shadow"):
            alpha = pack.clean(self.open(contract.named(p["name"], d), d, cut_it=False)).getchannel("A")
            im.paste(black, (0, 0), alpha.point(lambda v: v // 2))
        im.alpha_composite(dim(self.shipped(plate), k))
        glows = []
        for a in self.decl["animations"]:
            if a.get("working") and not working:
                continue                    # drawn only while the machine works (contract.py)
            fr = self.open(contract.frame(a["name"], frames.get(a["name"], 0), d), d)
            if a.get("kind") == "glow":
                glows.append(self.shipped(pack.glow_frame(fr, a.get("bloom"))))     # added below, while working
            elif a.get("kind") == "light":
                im.alpha_composite(pack.clean(fr))      # a white the engine tints: never rolled off
            else:
                im.alpha_composite(dim(self.shipped(pack.clean(fr)), k))
        for g in glows if working else ():
            im = add_glow(im, g)
        for p in self.decl["passes"] if working else ():
            if p["kind"] not in contract.WORKING:
                continue
            layer = self.open(contract.named(p["name"], d), d)
            under = self.open(contract.named(p["over"], d), d)
            if p["kind"] == "paint":
                im.alpha_composite(dim(self.shipped(pack.paint_layer(layer, under)), k))
            else:
                im = add_glow(im, self.shipped(pack.glow_layer(layer, under)))
        for p in self.kind("light"):
            lamp = pack.light_layer(self.open(contract.named(p["name"], d), d))
            im.alpha_composite(ImageChops.multiply(lamp, Image.new("RGBA", lamp.size, LAMP[working])))
        return im

    def remnants(self):
        """The remnants pass, or None."""
        return next(iter(self.kind("remnants")), None)

    def wreck(self, d, night=False):
        """The remnants pass in direction d on the ground, at its canvas's size, as pack.py packs it,
        its glow (when it declares one) added over it; None when the model declares none. night: at
        night (the module's docstring), the ground and the wreck darkened, the glow as by day."""
        p = self.remnants()
        if p is None:
            return None
        k = NIGHT if night else 1
        canvas = contract.canvas_of(self.decl, p)
        im = Image.new("RGBA", tuple(canvas), ground(k))
        wreck = pack.clean(self.open(contract.named(p["name"], d), d, cut_it=False, canvas=canvas))
        im.alpha_composite(dim(self.shipped(wreck), k))
        if "glow" in p:
            lit = self.open(contract.named(p["glow"]["name"], d), d, cut_it=False, canvas=canvas)
            im = add_glow(im, self.shipped(pack.glow_layer(lit, wreck)))
        return im


def grid(im, origin, footprint, ppt):
    """The tile grid, aligned to the footprint, over the whole panel; the footprint brighter."""
    draw = ImageDraw.Draw(im, "RGBA")
    ox, oy = origin
    for axis, n in ((0, footprint[0]), (1, footprint[1])):
        o = (ox, oy)[axis]
        size = im.size[axis]
        first = o + (n / 2) * ppt                   # the footprint's far edge, then every tile from it
        k = -int(first // ppt) - 1
        while first + k * ppt < size:
            v = round(first + k * ppt)
            if 0 <= v < size:
                line = [(v, 0), (v, im.height - 1)] if axis == 0 else [(0, v), (im.width - 1, v)]
                draw.line(line, fill=GRID)
            k += 1
    w, h = footprint[0] * ppt, footprint[1] * ppt
    draw.rectangle([round(ox - w / 2), round(oy - h / 2), round(ox + w / 2), round(oy + h / 2)],
                   outline=FOOTPRINT)


def corner(art_size, origin, shift=(0, 0)):
    """Where place() puts art's top left corner."""
    return round(origin[0] + shift[0] - art_size[0] / 2), round(origin[1] + shift[1] - art_size[1] / 2)


def place(art, size, origin, shift=(0, 0), by=1):
    """art centred on the panel's origin, moved by shift (px), on the ground (at night when by is NIGHT,
    and under Lights the size of the panel when by is them)."""
    im = ground_im(size, by)
    im.alpha_composite(art, corner(art.size, origin, shift))
    return im


def adopted_arg(arg):
    """<png>[@<x>,<y>]: a plate and its shift in tiles."""
    path, _, shift = arg.rpartition("@") if "@" in arg else (arg, "", "")
    try:
        x, y = (float(v) for v in shift.split(",")) if shift else (0.0, 0.0)
    except ValueError:
        sys.exit(f"preview.py: --adopted {arg}: the shift after @ is not <x>,<y> in tiles")
    if not os.path.isfile(path):
        sys.exit(f"preview.py: --adopted {path}: no such file")
    return path, (x, y)


def label(im, text):
    out = Image.new("RGBA", (im.width, im.height + LABEL), GAP)
    out.alpha_composite(im, (0, LABEL))
    ImageDraw.Draw(out).text((4, 2), text, fill=(220, 220, 220, 255))
    return out


def sheet(rows):
    """rows: [[panel, ...], ...], every panel the same size; a None leaves its place empty."""
    pw, ph = rows[0][0].size
    cols = max(len(r) for r in rows)
    out = Image.new("RGBA", (PAD + cols * (pw + PAD), PAD + len(rows) * (ph + PAD)), GAP)
    for r, row in enumerate(rows):
        for c, im in enumerate(row):
            if im is not None:
                out.alpha_composite(im, (PAD + c * (pw + PAD), PAD + r * (ph + PAD)))
    return out


def review(model, out, adopted, night=True):
    decl = model.decl
    if adopted and len(adopted) != len(model.directions):
        sys.exit(f"preview.py: --adopted takes one plate per direction: render.json declares "
                 f"{len(model.directions)} ({decl['directions']}), and {len(adopted)} given")
    adopted = [adopted_arg(a) for a in adopted]
    plates = [(Image.open(path).convert("RGBA"), (x * model.ppt, y * model.ppt)) for path, (x, y) in adopted]
    # the model's canvas, and a remnants pass's own when it has one
    canvases = [decl["canvas"]] + [contract.canvas_of(decl, p) for p in model.kind("remnants")]
    cw, ch = max(c[0] for c in canvases), max(c[1] for c in canvases)
    pw = max([cw] + [p.width + 2 * abs(s[0]) for p, s in plates]) + 2 * PAD
    ph = max([ch] + [p.height + 2 * abs(s[1]) for p, s in plates]) + 2 * PAD
    pw, ph = int(-(-pw // 1)), int(-(-ph // 1))
    pw, ph = pw + pw % 2, ph + ph % 2
    origin = (pw / 2, ph / 2)
    rows = []
    for i, d in enumerate(model.directions):
        name = d or decl["directions"]
        fp = contract.footprint_in(decl, d)
        panels, dark = [], []           # the day row, and the night row under it (None: left empty)
        if plates:
            plate, shift = plates[i]
            panels.append((place(plate, (pw, ph), origin, shift),
                           f"{name}: adopted" + (f" @{adopted[i][1][0]:g},{adopted[i][1][1]:g}" if any(shift) else "")))
            dark.append(None)           # vanilla's glows are not known here
        for working, what in ((False, "idle"), (True, "working")):
            panels.append((place(model.panel(d, working), (pw, ph), origin), f"{name}: {what}"))
            if not night:
                dark.append(None)
                continue
            # the declared lights over the whole panel, so they reach the ground past the canvas too
            lit = model.light_map(d, working, (pw, ph), origin)
            x, y = corner(decl["canvas"], origin)
            art = model.panel(d, working, night=True, light=lit and lit.crop((x, y, x + decl["canvas"][0],
                                                                              y + decl["canvas"][1])))
            dark.append((place(art, (pw, ph), origin, by=lit or NIGHT), f"{name}: {what} at night"))
        wreck = model.wreck(d)
        if wreck is not None:
            panels.append((place(wreck, (pw, ph), origin), f"{name}: wreck"))
            dark.append((place(model.wreck(d, night=True), (pw, ph), origin, by=NIGHT), f"{name}: wreck at night")
                        if night else None)
        for im, _ in panels + [p for p in dark if p is not None]:
            grid(im, origin, fp, model.ppt)
        rows.append([label(im, text) for im, text in panels])
        if any(dark):
            rows.append([label(*p) if p is not None else None for p in dark])
    sheet(rows).save(out)
    print(f"{out}: {len(rows)} row(s), {', '.join(d or decl['directions'] for d in model.directions)}"
          f"{', each with a night row under it' if len(rows) > len(model.directions) else ''}; "
          f"panels {pw}x{ph}, origin at {origin}, {model.ppt:g} px a tile")


def gif(model, out, name, speed):
    anims = {a["name"]: a for a in model.decl["animations"]}
    if name not in anims:
        sys.exit(f"preview.py: render.json declares no animation {name!r}"
                 f" (it declares {', '.join(map(repr, anims)) or 'none'})")
    if not speed > 0:
        sys.exit(f"preview.py: --speed {speed} is not an animation_speed above 0")
    n = anims[name]["frames"]
    # a glow animation and its plate layer are one animation in the engine, frame for frame:
    # whichever is asked for, the plate layer and every glow over it play
    plate = anims[name]["over"] if anims[name].get("kind") == "glow" else name
    together = {name, plate} | {a["name"] for a in anims.values() if a.get("kind") == "glow" and a["over"] == plate}
    # the order the engine plays them in: render.json's frame_sequence or hold (1-based), else each once
    seq = contract.sequence(model.decl, anims[plate])
    order = [k - 1 for k in seq] if seq else list(range(n))
    fps = 60 * speed
    shown = sorted(set(order))
    frames = {}
    for f in shown:
        row = [model.panel(d, True, {a: f for a in together}) for d in model.directions]
        im = Image.new("RGBA", (sum(p.width for p in row), row[0].height), GROUND)
        for i, p in enumerate(row):
            im.alpha_composite(p, (i * p.width, 0))
        frames[f] = im.convert("RGB")
    # one palette for the loop, so nothing flickers between frames
    w, h = frames[shown[0]].size
    strip = Image.new("RGB", (w, h * len(shown)))
    for i, f in enumerate(shown):
        strip.paste(frames[f], (0, i * h))
    palette = strip.quantize(colors=256)
    frames = {f: im.quantize(palette=palette, dither=Image.Dither.NONE) for f, im in frames.items()}
    # entry e is up from e / fps seconds; a run of entries on one frame (a hold) is one GIF
    # frame, up from its first entry to the next run's: each held to the hundredth, as a GIF counts
    runs = [e for e in range(len(order)) if e == 0 or order[e] != order[e - 1]] + [len(order)]
    ticks = [round(100 * e / fps) for e in runs]
    durations = [10 * (b - a) for a, b in zip(ticks, ticks[1:])]
    if min(durations) < 20:
        print(f"preview.py: at {fps:g} frames a second some frames are held under 2/100 s, "
              f"which most viewers slow to 1/10 s", file=sys.stderr)
    seen = [frames[order[e]] for e in runs[:-1]]
    seen[0].save(out, save_all=True, append_images=seen[1:], duration=durations, loop=0)
    played = f"its frame_sequence, {len(order)} entries of its {n} frames" if seq else f"{n} frames"
    print(f"{out}: {name}, {played} at {fps:g} a second (held {durations} ms), looping")


def main():
    ap = argparse.ArgumentParser(description="A model's review sheet, or one animation as a GIF.")
    ap.add_argument("render_dir")
    ap.add_argument("out")
    ap.add_argument("--adopted", nargs="+", default=[], metavar="PNG[@X,Y]",
                    help="the adopted plate(s), one per direction, each with its prototype shift in tiles")
    ap.add_argument("--day-only", action="store_true",
                    help="no night rows: one row per direction, by day (the module's docstring)")
    ap.add_argument("--night", action="store_true",
                    help="a night row under each direction's, every panel at night: the default")
    ap.add_argument("--gif", metavar="ANIMATION", help="write a GIF of this animation instead of the sheet")
    ap.add_argument("--speed", type=float, metavar="ANIMATION_SPEED",
                    help="the prototype's animation_speed, for --gif")
    args = ap.parse_args()
    if (args.gif is None) != (args.speed is None):
        ap.error("--gif and --speed go together")
    if args.gif and args.adopted:
        ap.error("--adopted is for the sheet, not the GIF")
    if args.gif and args.night:
        ap.error("--night is for the sheet, not the GIF")
    if args.night and args.day_only:
        ap.error("--night and --day-only cannot go together")
    model = Model(args.render_dir)
    if args.gif:
        gif(model, args.out, args.gif, args.speed)
    else:
        review(model, args.out, args.adopted, night=not args.day_only)


if __name__ == "__main__":
    main()
