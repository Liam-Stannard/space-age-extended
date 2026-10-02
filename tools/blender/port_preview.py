#!/usr/bin/env python3
"""The building's ports in every direction, with vanilla pipes joined to them.

  python3 port_preview.py <out-dir> <out.png>

<out-dir> is render.sh's, run with --ports: the ports and directions come from
<out-dir>/ports/render.json (contract.py), the sheets and their shifts from
<out-dir>/sheets and <out-dir>/sheets/ports and the meta.json beside each.

One row per direction. The engine turns a building's fluid connections with it,
clockwise, and draws each with the picture for the face it now points out of,
from the tile it points into -- so in each direction every declared port is
turned, and its fitting (port-<face>, and cover-<face> while nothing is joined
to it) is drawn from that tile with the sheet's shift. A port joined to a pipe
gets a vanilla straight pipe centred on that tile; the rest are capped. The two
panels of a row join alternate ports, so every port is seen both ways in every
direction. A face with no sheet of its own is a picture the engine would ask for
and the model did not render: it is outlined red on its tile and named.

Layers as the engine draws them: the shadows, the north-facing fittings
(secondary_draw_orders north = -1, behind the building), the plate with every
animation at frame 0, then the other fittings. The tile grid is drawn over it.
"""
import json
import os
import sys
from PIL import Image, ImageDraw

import contract

FD = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity/pipe")
VANILLA_PPT = 64                        # a high-resolution vanilla sprite's px to a tile
GROUND = (58, 52, 46, 255)
GAP = (30, 30, 30, 255)
GRID = (255, 255, 255, 40)
MISSING = (255, 60, 60, 255)
ORDER = "NESW"
LABEL, PAD, MARGIN = 14, 8, 2           # MARGIN: tiles of ground round the footprint


def fail(msg):
    sys.exit(f"port_preview.py: {msg}")


def read_json(path):
    if not os.path.isfile(path):
        fail(f"{path} is missing: run render.sh with --ports first")
    with open(path) as f:
        return json.load(f)


def turned(port, deg):
    """A port as the engine has it once the building is turned `deg` clockwise."""
    x, y = port["tile"]
    face = port["face"]
    for _ in range(deg // 90):
        x, y = -y, x                            # a quarter clockwise, y down
        face = ORDER[(ORDER.index(face) + 1) % 4]
    return dict(tile=[x, y], face=face)


class Scene:
    def __init__(self, out_dir):
        self.sheets = os.path.join(out_dir, "sheets")
        self.ports = os.path.join(self.sheets, "ports")
        try:
            self.decl = contract.load(os.path.join(out_dir, "ports"))
        except contract.ContractError as e:
            fail(str(e))
        if not self.decl["ports"]:
            fail(f"{out_dir}/ports/render.json declares no ports")
        self.meta = read_json(os.path.join(self.sheets, "meta.json"))
        self.port_meta = read_json(os.path.join(self.ports, "meta.json"))
        self.ppt = float(self.decl["rig"]["px_per_tile"])
        fw, fh = self.decl["footprint"]
        n = max(fw, fh) + 2 * MARGIN
        self.size = (round(n * self.ppt),) * 2
        self.centre = (self.size[0] / 2, self.size[1] / 2)
        self.missing = set()
        if not os.path.isfile(os.path.join(FD, "pipe-straight-vertical.png")):
            fail(f"no vanilla pipe sprites in {FD}: set FACTORIO_DATA to the game's data directory")

    def sprite(self, path, scale=1.0):
        im = Image.open(path).convert("RGBA")
        if scale != 1.0:
            im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
        return im

    def put(self, canvas, im, tx, ty):
        """im centred on the point (tx, ty) tiles from the entity centre."""
        cx, cy = self.centre[0] + tx * self.ppt, self.centre[1] + ty * self.ppt
        canvas.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2)))

    def sheet(self, canvas, stem, frame_size=None, shadow=False):
        """A packed sheet (its first frame, for an animation) at its meta.json shift; a shadow at 50 %."""
        if stem not in self.meta:
            fail(f"{self.sheets}/meta.json has no {stem!r}: pack it from the same render")
        im = self.sprite(os.path.join(self.sheets, stem + ".png"))
        if frame_size:
            im = im.crop((0, 0, *frame_size))
        if shadow:
            im.putalpha(im.getchannel("A").point(lambda v: v // 2))
        self.put(canvas, im, *self.meta[stem]["shift"])

    def fitting(self, canvas, port, joined):
        """Draw a port's fitting; True if the model rendered no sheet for its face."""
        tx, ty = contract.outside(port)
        lacking = False
        for kind in ("port",) + (() if joined else ("cover",)):
            key = f"{kind}-{port['face']}"
            if key not in self.port_meta:
                self.missing.add(key)
                lacking = True
                continue
            dx, dy = self.port_meta[key]["shift"]
            self.put(canvas, self.sprite(os.path.join(self.ports, key + ".png")), tx + dx, ty + dy)
        return lacking

    def outline(self, canvas, port):
        x, y = port["tile"]
        left = self.centre[0] + (x - 0.5) * self.ppt
        top = self.centre[1] + (y - 0.5) * self.ppt
        ImageDraw.Draw(canvas).rectangle([round(left), round(top), round(left + self.ppt) - 1,
                                          round(top + self.ppt) - 1], outline=MISSING, width=2)

    def pipe(self, canvas, port):
        name = "pipe-straight-vertical" if port["face"] in "NS" else "pipe-straight-horizontal"
        self.put(canvas, self.sprite(os.path.join(FD, name + ".png"), self.ppt / VANILLA_PPT),
                 *contract.outside(port))

    def grid(self, canvas, footprint):
        draw = ImageDraw.Draw(canvas, "RGBA")
        for axis, n in ((0, footprint[0]), (1, footprint[1])):
            o, size = self.centre[axis], canvas.size[axis]
            k = -int((o + n / 2 * self.ppt) // self.ppt) - 1
            while o + (n / 2 + k) * self.ppt < size:
                v = round(o + (n / 2 + k) * self.ppt)
                if 0 <= v < size:
                    draw.line([(v, 0), (v, canvas.height - 1)] if axis == 0 else [(0, v), (canvas.width - 1, v)],
                              fill=GRID)
                k += 1

    def draw(self, d, deg, joined):
        """The building facing d, with a pipe on the ports whose index is in `joined`."""
        decl = self.decl
        ports = [turned(p, deg) for p in decl["ports"]]
        canvas = Image.new("RGBA", self.size, GROUND)
        for p in decl["passes"]:
            if p["kind"] == "shadow":
                self.sheet(canvas, contract.named(p["sheet"], d), shadow=True)
        for i, p in enumerate(ports):
            if i in joined:
                self.pipe(canvas, p)
        lacking = []
        for i, p in enumerate(ports):
            if p["face"] == "N" and self.fitting(canvas, p, i in joined):
                lacking.append(p)
        plate = next(p for p in decl["passes"] if p["kind"] == "plate")
        self.sheet(canvas, contract.named(plate["sheet"], d))
        for a in decl["animations"]:
            stem = contract.named(a["name"], d)
            self.sheet(canvas, stem, self.meta.get(stem, {}).get("size"))
        for i, p in enumerate(ports):
            if p["face"] != "N" and self.fitting(canvas, p, i in joined):
                lacking.append(p)
        self.grid(canvas, contract.footprint_in(decl, d))
        for p in lacking:
            self.outline(canvas, p)
        return canvas, ports


def main(out_dir, out):
    scene = Scene(out_dir)
    decl = scene.decl
    n = len(decl["ports"])
    sets = [{i for i in range(n) if i % 2 == 0}, {i for i in range(n) if i % 2 == 1}]
    rows = []
    for d, deg in contract.DIRECTIONS[decl["directions"]]:
        row = []
        for joined in sets:
            canvas, ports = scene.draw(d, deg, joined)
            piped = [f"{p['face']}{tuple(p['tile'])}" for i, p in enumerate(ports) if i in joined] or ["none"]
            text = f"{d or decl['directions']}: piped {', '.join(piped)}"
            panel = Image.new("RGBA", (canvas.width, canvas.height + LABEL), GAP)
            panel.alpha_composite(canvas, (0, LABEL))
            ImageDraw.Draw(panel).text((4, 2), text, fill=(220, 220, 220, 255))
            row.append(panel)
            for i, p in enumerate(ports):
                if i in joined:
                    print(f"{d or decl['directions']}: port {p['face']} on tile {p['tile']}: "
                          f"pipe on tile {list(contract.outside(p))}")
        rows.append(row)
    pw, ph = rows[0][0].size
    sheet = Image.new("RGBA", (PAD + 2 * (pw + PAD), PAD + len(rows) * (ph + PAD)), GAP)
    for r, row in enumerate(rows):
        for c, im in enumerate(row):
            sheet.alpha_composite(im, (PAD + c * (pw + PAD), PAD + r * (ph + PAD)))
    sheet.save(out)
    print(f"{out}: {len(rows)} row(s)")
    if scene.missing:
        print(f"port_preview.py: no sheet for {', '.join(sorted(scene.missing, key=lambda k: (k[0], ORDER.index(k[-1]))))}"
              f" -- the engine draws a picture for every face a port turns to, and the model rendered "
              f"none for these (outlined red)", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: port_preview.py <out-dir> <out.png>")
    main(sys.argv[1], sys.argv[2])
