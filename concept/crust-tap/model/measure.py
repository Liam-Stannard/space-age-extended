#!/usr/bin/env python3
"""The Crust Tap's pass criteria, measured off a render.sh output directory.

  python3 measure.py <out-dir> [measures.json]

  <out-dir>  render.sh's: <out-dir>/renders (idle-<d>, diag-mouth-<d>, diag-riser-<d>,
             diag-bare) and <out-dir>/sheets/meta.json

The task's criteria (.claude/tasks/crust-tap-model.md, with its 2026-10-02 amendment):

 1  the base square: pack.py's Appendix C checks per direction, restated, and the
    plate's full width in tiles (2.000 +- 0.02) and the offset of its centre;
 2  the riser's mouth on its connection: the mouth's flange collar rendered alone
    (diag-mouth-<d>), its position on the screen against the vanilla pipe sprite it
    meets, measured off base/graphics/entity/pipe here rather than remembered --
      north/south: the collar's ring against the vanilla pipe's joint ring (the
      flange ring a vertical pipe draws in the 20 px past the tile edge it joins on),
      its centre row and its centre column (the tube's); also its centre against the
      tile edge itself;
      east/west: the collar's outer face against the tile edge, and its centre row
      against the horizontal tube's;
    then the gap and the overlap: the plate and the vanilla pipe composited as the
    engine draws them, the run from the riser's body into the pipe walked along the
    riser's axis for any pixel under half alpha (a gap; the least alpha is reported),
    and the vanilla pipe's opaque
    pixels counted that land on the plate's own opaque pixels outside the mouth's
    collar (an overlap past the flange);
 3  the four plates against each other everywhere neither riser reaches: the reach is
    the riser's own silhouette (diag-riser-<d>, alpha > 0) dilated 2 px, together with
    the pixels the riser darkens by more than 8 against the bare collar (its shadow
    and its occlusion on the plate) -- the max channel difference outside it, and the
    count of pixels over 1;
 4  no pixel of the plate within spec 3.3's frost (#BFD8E8 -> #EAF4FA) or seam heat
    (#C8541E -> #E8A24A) ranges: within 12 (RGB distance) of the segment between the
    two ends;
 5  finish.py and tonal.py on every plate and on the adopted north plate (printed by
    render.sh; repeated here for the table);
 6  the sight glass's light layer (the 2026-10-09 amendment; every frame of it since the
    gas-pump-animation task): on the plate's canvas, nothing outside the glass (the glass as the plate shows it, diag-glass-<d>, its edge
    dilated a pixel), and neutral white (its channel means within 12).
"""
import itertools
import json
import os
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
BL = os.path.join(REPO, "tools", "blender")
FD = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity/pipe")
ADOPTED = os.path.join(REPO, "graphics", "entity", "crust-tap")
DIRS = ("north", "east", "south", "west")
PPT = 64
# spec 24: the connection tile (x, y down, tiles) and the face its pipe leaves by
CONN = {"north": ((0.5, -0.5), "N"), "east": ((0.5, 0.5), "E"), "south": ((-0.5, 0.5), "S"),
        "west": ((-0.5, -0.5), "W")}
STEP = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
FROST = ((0xBF, 0xD8, 0xE8), (0xEA, 0xF4, 0xFA))
SEAM = ((0xC8, 0x54, 0x1E), (0xE8, 0xA2, 0x4A))


def load(path):
    return Image.open(path).convert("RGBA")


def bbox(im, thr=128):
    return im.getchannel("A").point(lambda v: 255 if v > thr else 0).getbbox()


def vanilla():
    """The vanilla pipe sprites' joint geometry, in sprite px from the sprite's centre
    (the tile centre): a 128 px sprite, 64 px to a tile."""
    v, h = load(os.path.join(FD, "pipe-straight-vertical.png")), load(os.path.join(FD, "pipe-straight-horizontal.png"))
    W = v.width

    def opaque(im, x, y):
        return im.getpixel((x, y))[3] >= 240

    # the vertical pipe's joint ring: the rows above the tile's top edge (row 32) that hold
    # sprite at all, and its tube's columns at mid-height
    ring_rows = [y for y in range(0, 32) if any(opaque(v, x, y) for x in range(W))]
    tube_cols = [x for x in range(W) if opaque(v, x, 64) and v.getpixel((x, 64))[0] > 20]
    ring_cols = [x for x in range(W) if any(opaque(v, x, y) for y in ring_rows)]
    # the horizontal pipe's tube rows at its middle column (the shadow below is black, partly
    # transparent), and its flange columns
    hcols = [x for x in range(W) if any(opaque(h, x, y) for y in range(128))]
    trows = [y for y in range(128) if opaque(h, 64, y) and max(h.getpixel((64, y))[:3]) > 20]
    frows = [y for y in range(128) if opaque(h, hcols[0] + 1, y) and max(h.getpixel((hcols[0] + 1, y))[:3]) > 20]
    return dict(
        ring_rows=(min(ring_rows) - 64, max(ring_rows) + 1 - 64),         # from the tile centre
        ring_centre_past_edge=32 - (min(ring_rows) + max(ring_rows) + 1) / 2,
        ring_width=len(ring_cols), tube_width=len(tube_cols),
        tube_col_centre=(min(tube_cols) + max(tube_cols) + 1) / 2 - 64,
        htube_rows=(min(trows) - 64, max(trows) + 1 - 64), htube_centre=(min(trows) + max(trows) + 1) / 2 - 64,
        hflange_rows=(min(frows) - 64, max(frows) + 1 - 64), hcols=(min(hcols) - 64, max(hcols) + 1 - 64),
    )


def criterion_2(r, van):
    out = {}
    for d in DIRS:
        (tx, ty), face = CONN[d]
        m = load(os.path.join(r, f"diag-mouth-{d}.png"))
        W, H = m.size
        ox, oy = W / 2, H / 2
        x0, y0, x1, y1 = bbox(m)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        res = {"collar_box_px": [x0, y0, x1, y1]}
        if face in "NS":
            # the tile edge's row and the vanilla joint ring's centre row (the ring sits
            # past the edge on the far side, as the next pipe's sprite draws it)
            edge = oy + (ty + (-0.5 if face == "N" else 0.5)) * PPT
            ring = edge - van["ring_centre_past_edge"]
            res.update(edge_row=edge, collar_centre_row=cy, vanilla_ring_centre_row=ring,
                       off_vanilla_ring_px=round(cy - ring, 2), off_tile_edge_px=round(cy - edge, 2),
                       collar_centre_col=cx, tube_centre_col=ox + tx * PPT + van["tube_col_centre"],
                       off_tube_col_px=round(cx - (ox + tx * PPT + van["tube_col_centre"]), 2),
                       collar_width_px=x1 - x0, vanilla_ring_width_px=van["ring_width"])
        else:
            edge = ox + (tx + (0.5 if face == "E" else -0.5)) * PPT
            outer = x1 if face == "E" else x0
            tube = oy + ty * PPT + van["htube_centre"]
            res.update(edge_col=edge, collar_face_col=outer, off_tile_edge_px=outer - edge,
                       collar_centre_row=cy, vanilla_tube_centre_row=tube, off_tube_row_px=round(cy - tube, 2),
                       collar_height_px=y1 - y0,
                       vanilla_flange_height_px=van["hflange_rows"][1] - van["hflange_rows"][0])
        out[d] = res
    return out


def pipe_on(plate, d):
    """The plate with a vanilla straight pipe in the tile the connection points into,
    drawn in the engine's order (by y: a pipe north of the tap under it, south over it)."""
    (tx, ty), face = CONN[d]
    dx, dy = STEP[face]
    px, py = tx + dx, ty + dy
    name = "pipe-straight-vertical" if face in "NS" else "pipe-straight-horizontal"
    sp = load(os.path.join(FD, name + ".png"))
    W, H = plate.size
    at = (round(W / 2 + px * PPT - sp.width / 2), round(H / 2 + py * PPT - sp.height / 2))
    lay = Image.new("RGBA", plate.size)
    lay.alpha_composite(sp, at)
    if py < 0:                        # the pipe's centre is north of the tap's: drawn first
        comp = lay.copy()
        comp.alpha_composite(plate)
    else:
        comp = plate.copy()
        comp.alpha_composite(lay)
    return comp, lay


def criterion_2_join(r, c2):
    out = {}
    for d in DIRS:
        (tx, ty), face = CONN[d]
        plate = load(os.path.join(r, f"idle-{d}.png"))
        comp, lay = pipe_on(plate, d)
        W, H = plate.size
        mouth = load(os.path.join(r, f"diag-mouth-{d}.png")).getchannel("A").point(lambda v: 255 if v > 8 else 0)
        # the collar's outline, its open bore filled: what lies inside the flange
        outside = mouth.copy()
        ImageDraw.floodfill(outside, (0, 0), 128)
        mouth = outside.point(lambda v: 0 if v == 128 else 255)
        # the walk along the riser's axis: from the plate's side of the collar into the pipe
        if face in "NS":
            x = round(c2[d]["collar_centre_col"])
            ys = range(round(c2[d]["collar_centre_row"]), 0 if face == "N" else H, -1 if face == "N" else 1)
            line = [(x, y) for y in ys][:40]
        else:
            y = round(c2[d]["collar_centre_row"])
            xs = range(round(c2[d]["collar_face_col"]) - 4, W if face == "E" else 0, 1 if face == "E" else -1)
            line = [(x, y) for x in xs][:40]
        # a gap is a pixel the ground shows through: under half alpha (the collar's own
        # anti-aliased edge on the tile boundary is not one; its alpha is reported too)
        gaps = [p for p in line if comp.getpixel(p)[3] < 128]
        least = min(comp.getpixel(p)[3] for p in line)
        # vanilla's pipe over (or under) the plate's own pixels, outside the mouth's collar
        pa = plate.getchannel("A")
        # the vanilla pipe itself, not the shadow its sprite carries (black, part transparent)
        la = Image.eval(lay.convert("RGB").convert("L"), lambda v: 255 if v > 20 else 0)
        la = ImageChops.multiply(la, lay.getchannel("A").point(lambda v: 255 if v > 200 else 0))
        if ty + STEP[face][1] < 0:
            # drawn under the plate (north of it): what shows of the vanilla pipe past our
            # collar, across the joint ring's rows -- the ring overhanging ours
            if face in "NS":
                e = round(c2[d]["edge_row"])
                band = lambda i: e - 20 <= i // W <= e           # noqa: E731  the ring's rows
            else:
                e = round(c2[d]["edge_col"])
                # the flange's columns on the tap's side of the edge (vanilla's own flange
                # stands in its own tile, beside ours)
                band = (lambda i: e <= i % W <= e + 5) if face == "W" else (lambda i: e - 5 <= i % W < e)  # noqa: E731
            hits = [i for i, (p, l, m) in enumerate(zip(pa.get_flattened_data(), la.get_flattened_data(),
                                                         mouth.get_flattened_data()))
                    if l and p <= 128 and not m and band(i)]
        else:
            # drawn over the plate: the vanilla pipe over the plate's own pixels, past our collar
            hits = [i for i, (p, l, m) in enumerate(zip(pa.get_flattened_data(), la.get_flattened_data(),
                                                         mouth.get_flattened_data())) if p > 128 and l and not m]
        over = len(hits)
        if hits:
            xs, ys = [i % W for i in hits], [i // W for i in hits]
            out.setdefault("_where", {})[d] = [min(xs), min(ys), max(xs), max(ys)]
        out[d] = dict(gap_px_on_axis=len(gaps), least_alpha_on_axis=least, axis_walk_px=len(line),
                      overlap_px_outside_collar=over,
                      overlap_box=out.get("_where", {}).get(d))
        comp.save(os.path.join(r, f"diag-joined-{d}.png"))
    return out


def criterion_3(r):
    bare = load(os.path.join(r, "diag-bare.png"))
    reach = {}
    for d in DIRS:
        sil = load(os.path.join(r, f"diag-riser-{d}.png")).getchannel("A").point(lambda v: 255 if v > 0 else 0)
        sil = sil.filter(ImageFilter.MaxFilter(5))
        idle = load(os.path.join(r, f"idle-{d}.png"))
        darker = ImageChops.subtract(bare.convert("RGBa"), idle.convert("RGBa")).convert("RGB").convert("L").point(
            lambda v: 255 if v > 8 else 0)
        reach[d] = ImageChops.lighter(sil, darker.filter(ImageFilter.MaxFilter(3)))
    out = {}
    for a, b in itertools.combinations(DIRS, 2):
        # premultiplied: a nearly transparent pixel's colour is not drawn, and the
        # downsample leaves arbitrary colour at alpha 1
        ia, ib = (load(os.path.join(r, f"idle-{x}.png")).convert("RGBa") for x in (a, b))
        mask = ImageChops.lighter(reach[a], reach[b])
        diff = ImageChops.difference(ia, ib)
        worst, over1, n = 0, 0, 0
        for px, m in zip(diff.get_flattened_data(), mask.get_flattened_data()):
            if m:
                continue
            v = max(px)
            n += 1
            worst = max(worst, v)
            over1 += v > 1
        out[f"{a}-{b}"] = dict(max_diff=worst, px_over_1=over1, px_compared=n)
    return out


def near_segment(c, seg, tol=12):
    (a, b) = seg
    ab = [b[i] - a[i] for i in range(3)]
    t = sum((c[i] - a[i]) * ab[i] for i in range(3)) / sum(v * v for v in ab)
    t = max(0.0, min(1.0, t))
    return sum((c[i] - (a[i] + t * ab[i])) ** 2 for i in range(3)) <= tol * tol


def criterion_4(r):
    out = {}
    for d in DIRS:
        im = load(os.path.join(r, f"idle-{d}.png"))
        px = [p[:3] for p in im.get_flattened_data() if p[3] > 0]
        out[d] = dict(frost_px=sum(near_segment(c, FROST) for c in px),
                      seam_px=sum(near_segment(c, SEAM) for c in px))
    return out


def criterion_glass(r, frames=None):
    """The sight glass's light layer (the task's 2026-10-09 amendment): rendered on the
    plate's own canvas (so it registers by construction), nothing of it outside the glass,
    and neutral white -- the means of its channels within 12 of each other -- so the
    engine's tint alone decides its colour. (The gas-pump-animation task: the layer is an
    animation now, sight-glass-NN-<d>; every frame is held to the same, and the worst frame
    reported.)"""
    if frames is None:
        frames = len([f for f in os.listdir(r) if f.startswith("sight-glass-") and f.endswith("-north.png")])
    out = {}
    for d in DIRS:
        idle = load(os.path.join(r, f"idle-{d}.png"))
        glass = load(os.path.join(r, f"diag-glass-{d}.png")).getchannel("A").point(lambda v: 255 if v > 8 else 0)
        glass = glass.filter(ImageFilter.MaxFilter(3))          # its anti-aliased edge
        rows = []
        for f in range(frames):
            light = load(os.path.join(r, f"sight-glass-{f:02d}-{d}.png"))
            lit = light.getchannel("A").point(lambda v: 255 if v > 8 else 0)
            px = [p for p, a in zip(light.get_flattened_data(), lit.get_flattened_data()) if a]
            outside = sum(1 for a, g in zip(lit.get_flattened_data(), glass.get_flattened_data()) if a and not g)
            w = sum(p[3] for p in px) or 1
            mean = [round(sum(p[c] * p[3] for p in px) / w, 1) for c in range(3)]
            rows.append(dict(same_canvas=light.size == idle.size, px=len(px), outside_glass_px=outside,
                             mean_rgb=mean, channel_spread=round(max(mean) - min(mean), 1),
                             luminance_range=[min(round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in px),
                                              max(round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in px)]))
        out[d] = dict(frames=frames, all_same_canvas=all(x["same_canvas"] for x in rows),
                      outside_glass_px_max=max(x["outside_glass_px"] for x in rows),
                      channel_spread_max=max(x["channel_spread"] for x in rows),
                      px_range=[min(x["px"] for x in rows), max(x["px"] for x in rows)],
                      frame0=rows[0])
    return out


def measures(paths):
    rows = []
    for p in paths:
        f = subprocess.run([sys.executable, os.path.join(BL, "finish.py"), p], capture_output=True, text=True).stdout
        t = subprocess.run([sys.executable, os.path.join(BL, "tonal.py"), p], capture_output=True, text=True).stdout
        rows.append((p, f.strip(), t.strip()))
    return rows


def main(out, dump=None):
    r = os.path.join(out, "renders")
    meta = json.load(open(os.path.join(out, "sheets", "meta.json")))
    van = vanilla()
    c1 = {}
    for d in DIRS:
        im = load(os.path.join(r, f"idle-{d}.png"))
        x0, _, x1, _ = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
        c1[d] = dict(pack=meta["checks"][d], width_tiles=round((x1 - x0) / PPT, 4),
                     centre_offset_px=(x0 + x1) / 2 - im.width / 2)
    c2 = criterion_2(r, van)
    j = criterion_2_join(r, c2)
    c3 = criterion_3(r)
    c4 = criterion_4(r)
    glass = criterion_glass(r)
    c5 = measures([os.path.join(r, f"idle-{d}.png") for d in DIRS] + [os.path.join(ADOPTED, "base-north.png")])
    res = dict(vanilla=van, c1=c1, c2=c2, c2_join=j, c3=c3, c4=c4, glass=glass, c5=[(os.path.basename(p), f, t) for p, f, t in c5])
    print(json.dumps(res, indent=1))
    if dump:
        with open(dump, "w") as f:
            json.dump(res, f, indent=1)


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit("usage: measure.py <out-dir> [measures.json]")
    main(*sys.argv[1:])
