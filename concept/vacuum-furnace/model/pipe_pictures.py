#!/usr/bin/env python3
"""The furnace's pipe pictures: rendered from the model, cut to assembler 3's sheets.

  python3 pipe_pictures.py <ports-render-dir> <out-dir> [--compare <png>] [--align <png>]

<ports-render-dir> holds port-<face>.png and axis-<face>.png, the model run with
--ports and downsampled (tools/blender/downsample.py): each face's fitting alone
(with its backplate, and without it), lit by the rig, on the port canvas with the
entity origin at its centre.

Spec 8 and template rule 6, as Liam set them on 2026-10-02: the input's pipe
picture is a stub on the vanilla pipe's own centreline, its flange the size of the
pipe's bolted end ring, in the building's own metal; on assembler 3's sheet size
and shift, its outline within 2 px of assembler 3's. This cuts each render to
vanilla's own sheet rectangle (its size, and its shift from the .lua beside it,
placed as the engine places a pipe picture: from the centre of the tile the
connection points into) and keeps the render's own alpha.

The pipe, measured: vanilla's straight pipes (base/graphics/entity/pipe), centred on
the tile the input points into. Horizontal: axis 1.0 px above the tile's centre, the
bolted end ring 52 px tall. Vertical: axis 0.5 px right of it, the ring 51 px wide.
Against them, on axis-<face>.png (the stub alone): its end flange's centre and size
-- at its tallest column for east and west, its widest row for north and south.

Measured, per face, on our alpha against assembler 3's:
  bbox      at alpha over 127 (the drawn silhouette) and over 0 (with the soft rim)
  beyond    the most alpha our render has just outside the rectangle, which the cut drops
  missed    px vanilla draws that ours does not
  extra     px ours draws that vanilla does not
  far_px    the farthest any edge pixel of either silhouette lies from the other's edge
Nothing is filled.

--align draws, for each face, assembler 3's picture and ours side by side, each on
its shift with two vanilla pipe tiles attached as the engine draws them (the
south pipe over the picture, the others under it), the pipe's axis marked, at 4x.

meta.json: per face, the sheet's size and shift (as util.by_pixel on scale 0.5,
and in tiles), and these measures.
"""
import json
import os
import re
import sys

from PIL import Image, ImageDraw

DATA = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity/assembling-machine-3")
PPT = 64                                                # sprite px to a tile, ours and vanilla's
MARGIN = 4
PIPES = os.path.join(os.path.dirname(DATA), "pipe")
# vanilla's straight pipe as drawn: axis offset from its tile's centre (px, screen
# x right, y down) and the end ring's size across the pipe (px)
RING = {"EW": dict(axis=-1.0, size=52), "NS": dict(axis=0.5, size=51)}
OUTSIDE = {"N": (0, -2), "E": (2, 0), "S": (0, 2), "W": (-2, 0)}   # the input's turns: {0, 1} -> the tile it points into


def vanilla(face):
    stem = os.path.join(DATA, f"assembling-machine-3-pipe-{face}")
    lua = open(stem + ".lua").read()
    bx, by = (float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", lua).groups())
    return Image.open(stem + ".png").convert("RGBA"), (bx, by)


def edge(mask, w, h):
    return {(x, y) for y in range(h) for x in range(w) if mask[y][x] and any(
        not (0 <= x + dx < w and 0 <= y + dy < h and mask[y + dy][x + dx])
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}


def far(a, b):
    """The farthest any pixel of edge a lies from edge b (Chebyshev-free: Euclidean)."""
    if not a or not b:
        return float("inf")
    return max(min(((x - u) ** 2 + (y - v) ** 2) ** 0.5 for u, v in b) for x, y in a)


def strip_shadow(im):
    """Vanilla's straight pipe carries its shadow painted in (pure black, alpha under 250)."""
    px = [(0, 0, 0, 0) if p[3] and max(p[:3]) <= 2 and p[3] < 250 else p for p in im.get_flattened_data()]
    o = Image.new("RGBA", im.size)
    o.putdata(px)
    return o


def draw_align(aligns, path, k=4):
    """Each face: vanilla's picture and ours, on their shift, two vanilla pipe tiles attached."""
    VIEW = {"S": (-56, 40, 56, 232), "N": (-56, -232, 56, -64), "E": (56, -56, 232, 56), "W": (-232, -56, -56, 56)}
    rows = []
    for face, van, ours, ox, oy in aligns:
        x0v, y0v, x1v, y1v = VIEW[face]
        panes = []
        for pic in (van, ours):
            c = Image.new("RGBA", (x1v - x0v, y1v - y0v), (74, 66, 58, 255))
            tx, ty = OUTSIDE[face]
            name = "pipe-straight-vertical" if face in "NS" else "pipe-straight-horizontal"
            pipe = strip_shadow(Image.open(os.path.join(PIPES, name + ".png")).convert("RGBA"))
            def put(im, px, py):
                c.alpha_composite(im, (round(px - x0v), round(py - y0v)))
            dx, dy = tx // 2, ty // 2                   # OUTSIDE is the first tile out: 2 tiles from the centre
            pipes = [(pipe, (dx * n) * PPT - 64, (dy * n) * PPT - 64) for n in (2, 3)]
            if face != "S":
                for im, px, py in pipes:
                    put(im, px, py)
            put(pic, ox, oy)
            if face == "S":
                for im, px, py in pipes:
                    put(im, px, py)
            big = c.resize((c.width * k, c.height * k), Image.NEAREST)
            d = ImageDraw.Draw(big, "RGBA")
            if face in "EW":
                y = (RING["EW"]["axis"] - y0v) * k
                d.line([(0, y), (big.width, y)], fill=(0, 255, 255, 140))
            else:
                x = (RING["NS"]["axis"] - x0v) * k
                d.line([(x, 0), (x, big.height)], fill=(0, 255, 255, 140))
            panes.append(big)
        row = Image.new("RGBA", (panes[0].width * 2 + 8, panes[0].height + 14), (30, 30, 30, 255))
        for i, (pane, name) in enumerate(zip(panes, ("assembler 3", "furnace"))):
            row.alpha_composite(pane, (i * (pane.width + 8), 14))
            ImageDraw.Draw(row).text((i * (pane.width + 8) + 4, 1), f"{face}: {name} -- cyan: the pipe's axis",
                                     fill=(220, 220, 220, 255))
        rows.append(row)
    W = max(r.width for r in rows)
    sheet = Image.new("RGBA", (W, sum(r.height + 8 for r in rows)), (30, 30, 30, 255))
    y = 0
    for r in rows:
        sheet.alpha_composite(r, (0, y))
        y += r.height + 8
    sheet.save(path)


def main(src, out, compare=None, align=None):
    os.makedirs(out, exist_ok=True)
    meta, panels, aligns = {}, [], []
    for face in "NESW":
        ours = Image.open(os.path.join(src, f"port-{face}.png")).convert("RGBA")
        cx, cy = ours.width / 2, ours.height / 2
        van, (bx, by) = vanilla(face)
        w, h = van.size
        tx, ty = OUTSIDE[face]
        # the sheet's centre on our canvas, as the engine places it
        mx, my = cx + (tx + bx / 32) * PPT, cy + (ty + by / 32) * PPT
        x0, y0 = mx - w / 2, my - h / 2
        if x0 != int(x0) or y0 != int(y0):
            sys.exit(f"pipe_pictures.py: {face}: vanilla's sheet lands off the pixel grid at ({x0}, {y0})")
        x0, y0 = int(x0), int(y0)
        cut = ours.crop((x0, y0, x0 + w, y0 + h))
        # what our render reaches outside vanilla's rectangle is extra too
        # what our render reaches just outside vanilla's rectangle is extra too (within
        # MARGIN px of it: the north flange's lower half, further down, is behind the hull)
        outside = sum(1 for yy in range(y0 - MARGIN, y0 + h + MARGIN) for xx in range(x0 - MARGIN, x0 + w + MARGIN)
                      if not (x0 <= xx < x0 + w and y0 <= yy < y0 + h) and ours.getpixel((xx, yy))[3] > 127)
        ca, va = cut.load(), van.load()
        mine = [[ca[x, y][3] > 127 for x in range(w)] for y in range(h)]
        theirs = [[va[x, y][3] > 127 for x in range(w)] for y in range(h)]
        missed = sum(1 for y in range(h) for x in range(w) if theirs[y][x] and not mine[y][x])
        extra = sum(1 for y in range(h) for x in range(w) if mine[y][x] and not theirs[y][x]) + outside
        e_m, e_t = edge(mine, w, h), edge(theirs, w, h)
        far_px = round(max(far(e_m, e_t), far(e_t, e_m)), 2)

        # the stub alone: its end flange against the pipe's end ring
        ax_im = Image.open(os.path.join(src, f"axis-{face}.png")).convert("RGBA")
        aa = ax_im.getchannel("A").load()
        if face in "EW":
            sign = 1 if face == "E" else -1
            cols = [int(cx + sign * u) for u in range(88, 97)]          # the last 9 px out to the edge
            best = None
            for c in cols:
                ys = [y for y in range(ax_im.height) if aa[c, y] > 127]
                if ys and (best is None or ys[-1] + 1 - ys[0] > best[1]):
                    best = (c, ys[-1] + 1 - ys[0], (ys[0] + ys[-1] + 1) / 2 - cy)
            ring = RING["EW"]
            flange = dict(size_px=best[1], centre_px=best[2], at_col_u=round((best[0] + 0.5 - cx) / PPT, 3))
        else:
            # rows of the end disc or flange: past 1.4 tiles out from the origin
            rows = [y for y in range(ax_im.height) if (y - cy) * (1 if face == "S" else -1) > 1.4 * PPT]
            best = None
            for r in rows:
                xs = [x for x in range(ax_im.width) if aa[x, r] > 127]
                if xs and (best is None or xs[-1] + 1 - xs[0] > best[1]):
                    best = (r, xs[-1] + 1 - xs[0], (xs[0] + xs[-1] + 1) / 2 - cx)
            ring = RING["NS"]
            flange = dict(size_px=best[1], centre_px=best[2], at_row_v=round((cy - best[0] - 0.5) / PPT, 3))
        axis_off = round(flange["centre_px"] - ring["axis"], 2)
        size_diff = flange["size_px"] - ring["size"]

        def box(im, thr):
            return im.getchannel("A").point(lambda v: 255 if v > thr else 0).getbbox()
        # anything our render draws beyond vanilla's rectangle, at any alpha: the sheet
        # is cut to the rectangle, so it would be lost
        beyond = max([ours.getpixel((xx, yy))[3] for yy in range(y0 - MARGIN, y0 + h + MARGIN)
                      for xx in range(x0 - MARGIN, x0 + w + MARGIN)
                      if not (x0 <= xx < x0 + w and y0 <= yy < y0 + h)] or [0])
        bb = dict(ours_127=box(cut, 127), vanilla_127=box(van, 127), ours_0=box(cut, 0), vanilla_0=box(van, 0))
        bb_diff = max(abs(a - b) for a, b in zip(bb["ours_127"], bb["vanilla_127"]))
        sheet = cut                                       # our render, our alpha: nothing filled
        sheet.save(os.path.join(out, f"pipe-{face}.png"))
        meta[f"pipe-{face}"] = dict(
            size=[w, h], by_pixel=[bx, by], shift=[round(bx / 32, 5), round(by / 32, 5)],
            alpha="the model's own", bbox=bb, bbox_diff_px=bb_diff, beyond_alpha_max=beyond,
            axis=dict(flange=flange, pipe=ring, axis_offset_px=axis_off, flange_minus_ring_px=size_diff,
                      note="the stub's end flange (axis-<face>.png) against vanilla's straight pipe as drawn "
                           "in the tile the input points into: centre offset across the pipe, and size across it"),
            silhouette=dict(missed=missed, extra=extra, far_px=far_px, filled=0,
                            note="our silhouette (alpha > 127) against assembler 3's: px vanilla draws that "
                                 "ours misses, px ours draws that vanilla does not (inside the sheet and up to "
                                 "4 px beyond it), the farthest edge disagreement in px; nothing is filled"))
        print(f"pipe-{face}: axis offset {axis_off:+} px  flange {flange['size_px']} px vs pipe ring {ring['size']} px "
              f"({size_diff:+})")
        print(f"pipe-{face}: {w}x{h} by_pixel({bx:g}, {by:g})  bbox>127 ours {bb['ours_127']} vanilla "
              f"{bb['vanilla_127']} (diff {bb_diff} px)  bbox>0 ours {bb['ours_0']} vanilla {bb['vanilla_0']}  "
              f"beyond-rect alpha max {beyond}  missed {missed}  extra {extra}  far {far_px} px  filled 0")
        if compare:
            k = 6
            panel = Image.new("RGBA", (w * 3 * k + 16, h * k), (74, 66, 58, 255))
            for i, im in enumerate((van, cut)):
                bg = Image.new("RGBA", im.size, (74, 66, 58, 255))
                bg.alpha_composite(im)
                panel.paste(bg.resize((w * k, h * k), Image.NEAREST), (i * (w * k + 8), 0))
            diff = Image.new("RGBA", (w, h), (74, 66, 58, 255))
            dp = diff.load()
            for y in range(h):
                for x in range(w):
                    m, t = mine[y][x], theirs[y][x]
                    dp[x, y] = (255, 255, 255, 255) if m and t else (255, 60, 60, 255) if t else \
                        (60, 160, 255, 255) if m else (74, 66, 58, 255)
            panel.paste(diff.resize((w * k, h * k), Image.NEAREST), (2 * (w * k + 8), 0))
            panels.append(panel)
        aligns.append((face, van, cut, x0 - cx, y0 - cy))
    with open(os.path.join(out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    if align:
        draw_align(aligns, align)
    if compare:
        W = max(p.width for p in panels)
        sheet = Image.new("RGBA", (W, sum(p.height + 8 for p in panels)), (30, 30, 30, 255))
        y = 0
        for p in panels:
            sheet.alpha_composite(p, (0, y))
            y += p.height + 8
        ImageDraw.Draw(sheet)
        sheet.save(compare)


if __name__ == "__main__":
    a = sys.argv[1:]
    opt = {}
    for flag in ("--compare", "--align"):
        if flag in a:
            i = a.index(flag)
            opt[flag[2:]] = a[i + 1]
            del a[i:i + 2]
    if len(a) != 2:
        sys.exit("usage: pipe_pictures.py <ports-render-dir> <out-dir> [--compare <png>] [--align <png>]")
    main(a[0], a[1], opt.get("compare"), opt.get("align"))
