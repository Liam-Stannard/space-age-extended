#!/usr/bin/env python3
"""Pack a render directory into the sheets the prototype loads, with their numbers.

  python3 pack.py <render-dir> <out-dir>

What to pack comes from the model's render.json (contract.py): its passes, its
animations, its directions, its footprint and its canvas. Every pass was
rendered on that one canvas with the entity origin exactly at its centre, so
every layer's shift is its crop's centre minus that point, computed rather than
measured and adjusted. Crops keep a 1 px transparent rim.

Sheets are named for the pass's declared sheet (and the animation's name), with
-<direction> after it when the model has more than one direction; meta.json
keys are the sheet names. Its "checks" are per direction when there are several.

Exits 1, naming the animation and the direction, when a turning part's centroid
drifts by more than LIMIT_PX across its frames, or a sliding part's is more than
LIMIT_PX off its declared curve or off its line. meta.json is written first.
"""
import json
import math
import os
import sys
from PIL import Image, ImageChops

import contract

# Shadow catchers record faint sky occlusion everywhere; below this is noise. The
# animation checks lean on it: with no floor, that haze pulls box.py's slider
# centroid 1.06 px off, past LIMIT_PX.
NOISE = 24
LIMIT_PX = 1.0      # a turning part's drift, a sliding part's miss off its curve or its line
LAYER_FLOOR = 8     # a working layer's difference from its plate at or under this is sampling noise
MAX_SHEET_W = 8192  # wrap an animation's frames into rows past this


def clean(im):
    a = im.getchannel("A").point(lambda v: 0 if v < NOISE else v)
    im.putalpha(a)
    return im


def glow_layer(lit, under):
    """A glow pass's sheet: lit minus the plate under it, opaque wherever that is above noise.

    Drawn additively, so its colour is what the light adds.
    """
    diff = ImageChops.subtract(lit.convert("RGB"), under.convert("RGB"))
    alpha = diff.convert("L").point(lambda v: 255 if v > LAYER_FLOOR else 0)
    return Image.merge("RGBA", (*diff.split(), alpha))


def paint_layer(painted, under):
    """A paint pass's sheet: the pass itself, wherever it differs from the plate under it.

    Drawn as ordinary paint, so it keeps the pass's own colour and alpha there --
    frost over a pipe, or past the plate's edge -- and is clear everywhere else.
    """
    diff = ImageChops.difference(painted, under).split()
    most = diff[0]
    for band in diff[1:]:
        most = ImageChops.lighter(most, band)
    keep = most.point(lambda v: 255 if v > LAYER_FLOOR else 0)
    return Image.merge("RGBA", (*painted.convert("RGB").split(), ImageChops.multiply(keep, painted.getchannel("A"))))


def light_layer(lamp):
    """What a light pass's sheet keeps, on the full canvas: its crop, the box of alpha
    above 8 with a 1 px rim (Packer.box_of), and nothing outside it."""
    bb = lamp.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    out = Image.new("RGBA", lamp.size)
    if bb:
        bb = (bb[0] - 1, bb[1] - 1, bb[2] + 1, bb[3] + 1)
        out.paste(lamp.crop(bb), bb[:2])
    return out


def centroid(im):
    a = im.getchannel("A")
    px = list(a.get_flattened_data())
    w = sum(px)
    return (sum(v * (i % a.width) for i, v in enumerate(px)) / w,
            sum(v * (i // a.width) for i, v in enumerate(px)) / w)


class Packer:
    def __init__(self, src, out, decl):
        self.src, self.out, self.decl = src, out, decl
        cw, ch = decl["canvas"]
        self.origin = (cw / 2, ch / 2)
        self.ppt = float(decl["rig"]["px_per_tile"])
        self.meta = {}
        self.over = []      # every animation past LIMIT_PX, as a line to exit with

    def open(self, stem):
        im = Image.open(os.path.join(self.src, stem + ".png")).convert("RGBA")
        if list(im.size) != list(self.decl["canvas"]):
            sys.exit(f"pack.py: {stem}.png is {im.size[0]}x{im.size[1]}, but render.json "
                     f"declares a {self.decl['canvas'][0]}x{self.decl['canvas'][1]} canvas")
        return im

    def box_of(self, alpha, what, thr=0):
        bb = alpha.point(lambda v: 255 if v > thr else 0).getbbox()
        if bb is None:
            sys.exit(f"pack.py: {what} is empty: nothing in it above alpha {thr}")
        x0, y0, x1, y1 = bb
        return (x0 - 1, y0 - 1, x1 + 1, y1 + 1)

    def shift(self, bb):
        return (round(((bb[0] + bb[2]) / 2 - self.origin[0]) / self.ppt, 5),
                round(((bb[1] + bb[3]) / 2 - self.origin[1]) / self.ppt, 5))

    def save(self, im, bb, sheet, **extra):
        im.crop(bb).save(os.path.join(self.out, sheet + ".png"))
        self.meta[sheet] = dict(size=(bb[2] - bb[0], bb[3] - bb[1]), shift=self.shift(bb), **extra)

    # ---------------------------------------------------------------- one direction

    def direction(self, d):
        decl = self.decl
        renders = {}
        for p in decl["passes"]:
            stem = contract.named(p["name"], d)
            renders[p["name"]] = self.open(stem)
        checks = {}
        plate = next(p for p in decl["passes"] if p["kind"] == "plate")
        idle = renders[plate["name"]]

        for p in decl["passes"]:
            if p["kind"] == "still":
                continue                    # a reference for the frame-0 check, not a sheet
            im, sheet = renders[p["name"]], contract.named(p["sheet"], d)
            what = contract.named(p["name"], d) + ".png"
            if p["kind"] == "plate":
                self.save(im, self.box_of(im.getchannel("A"), what), sheet)
            elif p["kind"] == "shadow":
                a = clean(im).getchannel("A")
                blk = Image.merge("RGBA", (*Image.new("RGB", im.size, (0, 0, 0)).split(), a))
                self.save(blk, self.box_of(a, what), sheet)
            elif p["kind"] == "glow":
                under = renders[p["over"]]
                layer = glow_layer(im, under)
                self.save(layer, self.box_of(layer.getchannel("A"), what + " minus its plate"), sheet)
                # Light the glow drove to white: white in the lit pass and not already
                # white under it (a glint on bare steel is). Over-driven emission clips
                # there, and the glow layer, being lit minus unlit, comes out grey
                # instead of the light's colour.
                white = sum(1 for w, i in zip(im.convert("RGB").get_flattened_data(),
                                              under.convert("RGB").get_flattened_data())
                            if min(w) >= 245 and min(i) < 245)
                checks[f"{p['sheet']}_white_px"] = (
                    white, "pixels the working light clipped to white; 0 = the light keeps its colour")
            elif p["kind"] == "paint":
                layer = paint_layer(im, renders[p["over"]])
                self.save(layer, self.box_of(layer.getchannel("A"), what + " where it differs from its plate"), sheet)
            elif p["kind"] == "light":
                self.save(im, self.box_of(im.getchannel("A"), what, 8), sheet)

        frame0 = []
        for a in decl["animations"]:
            name, n = a["name"], int(a["frames"])
            frames = [clean(self.open(contract.frame(name, f, d))) for f in range(n)]
            u = None
            for f, fr in enumerate(frames):
                b = self.box_of(fr.getchannel("A"), contract.frame(name, f, d) + ".png")
                u = b if u is None else (min(u[0], b[0]), min(u[1], b[1]), max(u[2], b[2]), max(u[3], b[3]))
            fw, fh = u[2] - u[0], u[3] - u[1]
            line = max(1, min(n, MAX_SHEET_W // fw))
            sheet = Image.new("RGBA", (fw * line, fh * math.ceil(n / line)))
            for i, fr in enumerate(frames):
                sheet.paste(fr.crop(u), ((i % line) * fw, (i // line) * fh))
            stem = contract.named(name, d)
            sheet.save(os.path.join(self.out, stem + ".png"))
            self.meta[stem] = dict(size=(fw, fh), shift=self.shift(u), frames=n, line_length=line)
            frame0.append(frames[0])

            cs = [centroid(fr) for fr in frames]
            if a["motion"] == "turn":
                # A part turned about its own axis keeps its centroid (given the
                # symmetry its loop relies on); one turned about anywhere else
                # drifts frame to frame.
                drift = max(math.hypot(cx - cs[0][0], cy - cs[0][1]) for cx, cy in cs)
                checks[f"{name}_drift_px"] = (round(drift, 2), f"centroid travel across the {n} frames; "
                                              "~0 = turning in place, must stay within 1")
                if round(drift, 2) > LIMIT_PX:
                    self.over.append(f"animation {name!r}, {where(d)}: its centroid drifts {round(drift, 2)} px "
                                     f"across its frames; a part turning about its own axis stays within "
                                     f"{LIMIT_PX:g}")
            else:
                path = checks[f"{name}_path_px"] = self.slide(a, cs, d)
                if max(path["off_curve"], path["off_line"]) > LIMIT_PX:
                    self.over.append(f"animation {name!r}, {where(d)}: a frame is {path['off_curve']} px off "
                                     f"its declared curve and {path['off_line']} px off its line; both stay "
                                     f"within {LIMIT_PX:g} (declared {path['declared']}, measured "
                                     f"{path['measured']})")

        if frame0:
            # The spec's frame-0 rule: the plate with every animation's frame 0 over
            # it is the stopped machine. Held to a single render of it (the still),
            # not to the byte: two renders of different scenes sample differently,
            # and a caught shadow is not a real one.
            still = next(p for p in decl["passes"] if p["kind"] == "still")
            comp = idle.copy()
            for fr in frame0:
                comp.alpha_composite(fr)
            diff0 = [max(px) for px in ImageChops.difference(
                comp, renders[still["name"]]).get_flattened_data()]
            checks["frame0_vs_still"] = (max(diff0), round(sum(1 for v in diff0 if v > 8) / len(diff0), 4),
                                         "max channel difference, and share of pixels over 8 (sampling noise)")

        # Appendix C's four measurements, on the plate, against the footprint as it
        # stands in this direction
        fw_tiles, fh_tiles = contract.footprint_in(decl, d)
        ox, oy = self.origin
        vis = idle.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
        base = Image.open(os.path.join(self.out, contract.named(plate["sheet"], d) + ".png")).getchannel("A")
        W, H = base.size
        appendix = {
            "centre_offset_px": (vis[0] + vis[2]) / 2 - ox,
            "edge_alpha_max": max(max(base.getpixel((0, y)), base.getpixel((W - 1, y))) for y in range(H))
                              + max(max(base.getpixel((x, 0)), base.getpixel((x, H - 1))) for x in range(W)),
            "half_width_tiles": (max(abs(vis[0] - ox), abs(vis[2] - ox)) / self.ppt,
                                 f"{fw_tiles / 2} = footprint width / 2"),
            "footprint_rows_tiles": ((vis[3] - oy) / self.ppt,
                                     f"bottom edge below origin; {fh_tiles / 2} = on the footprint"),
        }
        appendix.update(checks)
        return appendix

    def slide(self, anim, cs, d):
        """A part moving in a straight line, held to the curve the model declared.

        The declared path, put on the screen for this direction, is where the part
        should be in each frame; its centroid is where it is. The centroid sits a
        fixed distance from whatever point the path follows, so that offset is
        fitted (the mean over the frames) and what is left in each frame is the
        miss: along the line, the frame is off the curve; across it, off the line.
        """
        want = [contract.screen(self.decl, p, d) for p in anim["path"]]
        ox = sum(c[0] - w[0] for c, w in zip(cs, want)) / len(cs)
        oy = sum(c[1] - w[1] for c, w in zip(cs, want)) / len(cs)
        far = max(((w[0] - want[0][0], w[1] - want[0][1]) for w in want), key=lambda v: math.hypot(*v))
        ux, uy = far[0] / math.hypot(*far), far[1] / math.hypot(*far)
        got, along, across = [], [], []
        for c, w in zip(cs, want):
            rx, ry = c[0] - ox - w[0], c[1] - oy - w[1]
            got.append(round((c[0] - ox - want[0][0]) * ux + (c[1] - oy - want[0][1]) * uy, 2))
            along.append(rx * ux + ry * uy)
            across.append(-rx * uy + ry * ux)
        return dict(declared=[round((w[0] - want[0][0]) * ux + (w[1] - want[0][1]) * uy, 2) for w in want],
                    measured=got,
                    off_curve=round(max(abs(v) for v in along), 2),
                    off_line=round(max(abs(v) for v in across), 2),
                    note="each frame's position along the line, declared and measured (px from frame 0's "
                         "declared point); the most any frame is off the curve and off the line: both must "
                         "stay within 1")

    def run(self):
        dirs = [d for d, _ in contract.DIRECTIONS[self.decl["directions"]]]
        per = {d: self.direction(d) for d in dirs}
        self.meta["checks"] = per[""] if dirs == [""] else per
        return self.meta


def where(d):
    return f"direction {d}" if d else "its one direction"


def missing(src, decl):
    """Every render the declaration promises that is not in src."""
    want = []
    for d, _ in contract.DIRECTIONS[decl["directions"]]:
        want += [(f"pass {p['name']!r}", contract.named(p["name"], d)) for p in decl["passes"]]
        want += [(f"animation {a['name']!r}", contract.frame(a["name"], f, d))
                 for a in decl["animations"] for f in range(int(a["frames"]))]
    return [(what, stem) for what, stem in want if not os.path.isfile(os.path.join(src, stem + ".png"))]


def main(src, out):
    try:
        decl = contract.load(src)
    except contract.ContractError as e:
        sys.exit(f"pack.py: {e}")
    if not decl["passes"]:
        sys.exit(f"pack.py: {src}/render.json declares no passes to pack")
    gone = missing(src, decl)
    if gone:
        sys.exit(f"pack.py: {src} is missing {len(gone)} declared render(s):\n" +
                 "\n".join(f"  {stem}.png  ({what})" for what, stem in gone))
    os.makedirs(out, exist_ok=True)
    packer = Packer(src, out, decl)
    meta = packer.run()
    with open(os.path.join(out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(json.dumps(meta, indent=1))
    if packer.over:             # meta.json is written first, so the numbers can be read
        sys.exit(f"pack.py: {len(packer.over)} animation check(s) over {LIMIT_PX:g} px "
                 f"(numbers in {out}/meta.json):\n" + "\n".join(f"  {o}" for o in packer.over))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: pack.py <render-dir> <out-dir>")
    main(sys.argv[1], sys.argv[2])
