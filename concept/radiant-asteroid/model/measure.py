"""T01's acceptance measures for the radiant asteroid's maps, against promethium's.

    <python with numpy and Pillow> measure.py <promethium dir> <maps dir> [out.json]

<promethium dir> is space-age/graphics/entity/asteroid/promethium, <maps dir> the folder
radiant_asteroid.py wrote (maps/, holding small/ and chunk/). numpy is not in the system
Python and Pillow is not in Blender's: a venv made with --system-site-packages plus
`pip install numpy` runs it.

  1 sizes      the same file count, canvas and mode per size as promethium's
  2 normals    vanilla's convention, channel by channel: at the outline every normal faces
               outward, so with R = x (east +) and G = y (south +) the outline's normals
               point away from the rock (share of outline px, mean cosine); R rises from west
               to east and G from north to south (correlation with column and row); |RG| <= 1;
               B the facing component; each channel's p5/p50/p95 beside vanilla's
  3 blue       every drawn (alpha >= 230; the shader cuts below 0.9) blue pixel (blue the largest channel, chroma >= 24) in the colour and
               subsurface maps sits on the radiant ramp: hue 213-235 (the ramp
               #000000 > #04103A > #0B2A8C > #1F63FF > #5A9CFF/#73ADFF as Blender renders it
               spans 215.1-233.1; +-2 for 8-bit rounding), no cyan lean (G/B <= 0.70; #73ADFF is 0.68),
               none paler than #73ADFF (R <= 115); no other hue with chroma >= 24. Cyan lean
               (G/B > 0.70) counts only saturated pixels (chroma/max > 0.5): a little ramp blue
               over grey rock has G near B with its hue still the ramp's
  4 white      no white in the colour and subsurface maps: pack.py's definition, every channel
               245 or over. A blue channel at 255 is reported, not failed: it is the ramp's own
               colour (#1F63FF, #5A9CFF and #73ADFF all have blue FF)
"""
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

# the ramp as Blender draws it (stops interpolated in linear light, sRGB-encoded, 8-bit, chroma
# >= 24) spans hue 215.1-233.1, from #73ADFF/#5A9CFF down to its dark navy; +-2 for rounding
RAMP_HUE = (213.0, 235.0)


def rgba(p):
    return np.array(Image.open(p).convert("RGBA")).astype(float)


def hue(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    c = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, (g - b) / c % 6, np.where(mx == g, (b - r) / c + 2, (r - g) / c + 4))
    return h * 60, mx - mn


def one(colour_path):
    c = rgba(colour_path)
    n = rgba(colour_path.replace("-colour-", "-normal-"))
    r = rgba(colour_path.replace("-colour-", "-roughness-"))
    a = c[..., 3]
    m = a > 229
    H, W = a.shape
    ys, xs = np.nonzero(a > 0)
    x = n[..., 0] / 255 * 2 - 1
    y = n[..., 1] / 255 * 2 - 1
    zr = np.sqrt(np.clip(1 - x * x - y * y, 0, 1))
    rows = np.arange(H)[:, None]
    cols = np.arange(W)[None, :]
    qy = (ys.max() - ys.min()) * 0.25
    qx = (xs.max() - xs.min()) * 0.25
    # the outline: opaque pixels with a see-through 4-neighbour; outward is down the alpha slope
    soft = sum(np.roll(np.roll(a, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9
    gy, gx = np.gradient(soft)
    see = a <= 229
    edge = m & (np.roll(see, 1, 0) | np.roll(see, -1, 0) | np.roll(see, 1, 1) | np.roll(see, -1, 1))
    ox, oy = -gx, -gy
    cos = (x * ox + y * oy) / np.maximum(np.hypot(x, y) * np.hypot(ox, oy), 1e-9)
    corr = lambda u, v: float(np.corrcoef(u, v)[0, 1])
    out = dict(
        canvas=[W, H], mode=Image.open(colour_path).mode,
        extent=[int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)],
        fill=round(float(m.mean()), 3),
        normal=dict(
            R_left=round(float(x[m & (cols < xs.min() + qx)].mean()), 3),
            R_right=round(float(x[m & (cols > xs.max() - qx)].mean()), 3),
            G_top=round(float(y[m & (rows < ys.min() + qy)].mean()), 3),
            G_bottom=round(float(y[m & (rows > ys.max() - qy)].mean()), 3),
            outline_outward_share=round(float((cos[edge] > 0).mean()), 3),
            outline_mean_cos=round(float(cos[edge].mean()), 3),
            corr_R_column=round(corr(x[m], np.broadcast_to(cols, a.shape)[m]), 3),
            corr_G_row=round(corr(y[m], np.broadcast_to(rows, a.shape)[m]), 3),
            len_xy_max=round(float(np.sqrt(x * x + y * y)[m].max()), 3),
            B_minus_sqrt=round(float(np.abs(n[..., 2] / 255 - zr)[m].mean()), 3),
            p5_50_95={ch: [int(np.percentile(n[..., i][m], q)) for q in (5, 50, 95)]
                      for i, ch in enumerate("RGB")},
            alpha_px=int((n[..., 3] > 0).sum()), colour_alpha_px=int((a > 0).sum()),
        ),
        colour_lum_p5_50_95=[int(np.percentile((0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2])[m], q))
                             for q in (5, 50, 95)],
        rough_alpha_p5_50_95=[int(np.percentile(r[..., 3][m], q)) for q in (5, 50, 95)],
        sss_share_lit=round(float((r[..., :3].max(-1) > 40)[m].mean()), 3),
    )
    # what the engine draws: asteroid.frag multiplies every pixel by clamp((alpha - 0.9) * 10),
    # so nothing under alpha 230 shows. The verdict counts those; "_all" counts every pixel
    # with any alpha (the outline's faint edge too), for the record.
    for name, img, sel in (("colour", c, m), ("sss", r, m), ("colour_all", c, a > 0), ("sss_all", r, a > 0)):
        rgb = img[..., :3][sel]
        h, chroma = hue(rgb)
        blue = (rgb[:, 2] >= rgb[:, 0]) & (rgb[:, 2] >= rgb[:, 1]) & (chroma >= 24)
        other = (~blue) & (chroma >= 24)
        out[name] = dict(
            blue_px=int(blue.sum()),
            blue_off_ramp_hue=int((blue & ((h < RAMP_HUE[0]) | (h > RAMP_HUE[1]))).sum()),
            blue_cyan_lean=int((blue & (chroma > 0.5 * rgb.max(-1)) & (rgb[:, 1] > 0.70 * rgb[:, 2])).sum()),
            blue_paler_than_73ADFF=int((blue & (rgb[:, 0] > 115)).sum()),
            other_hue_px=int(other.sum()),
            blue_hue_range=[round(float(h[blue].min()), 1), round(float(h[blue].max()), 1)] if blue.any() else None,
            max_rgb=[int(v) for v in rgb.max(0)],
            white_px=int((rgb >= 245).all(-1).sum()),
            blue255_px=int((rgb[:, 2] >= 255).sum()),
            other_channel255_px=int((rgb[:, :2] >= 255).any(-1).sum()),
        )
    return out


def group(d):
    return {os.path.basename(p): one(p) for p in sorted(glob.glob(os.path.join(d, "*-colour-*.png")))}


def main():
    van, ours = sys.argv[1], sys.argv[2]
    res = {"vanilla": {}, "radiant": {}, "verdict": {}}
    for size in ("small", "chunk"):
        res["vanilla"][size] = group(os.path.join(van, size))
        res["radiant"][size] = group(os.path.join(ours, size))
    v = res["verdict"]
    for size in ("small", "chunk"):
        V, R = res["vanilla"][size], res["radiant"][size]
        files_v = sorted(os.listdir(os.path.join(van, size)))
        files_r = sorted(os.listdir(os.path.join(ours, size)))
        v[f"1 sizes {size}"] = dict(
            counts=[len(files_v), len(files_r)],
            canvases={tuple(x["canvas"]) for x in V.values()} == {tuple(x["canvas"]) for x in R.values()},
            extents_v=[x["extent"] for x in V.values()], extents_r=[x["extent"] for x in R.values()],
            pass_=len(files_v) == len(files_r) and len(V) == len(R)
            and {tuple(x["canvas"]) for x in V.values()} == {tuple(x["canvas"]) for x in R.values()}
            and all(x["mode"] == "RGBA" for x in R.values()))
        # a flipped or swapped channel turns the outline inward (share near 0) and the
        # correlations negative; a share under vanilla's lowest is a shape (an undercut ridge
        # on the outline), reported beside vanilla's, not a convention fault
        ok = all(x["normal"]["outline_outward_share"] > 0.5 and x["normal"]["corr_R_column"] > 0
                 and x["normal"]["corr_G_row"] > 0 and x["normal"]["len_xy_max"] <= 1.01 for x in R.values())
        v[f"2 normals {size}"] = dict(
            vanilla_outward_share=[x["normal"]["outline_outward_share"] for x in V.values()],
            radiant_outward_share=[x["normal"]["outline_outward_share"] for x in R.values()],
            vanilla_corr_R_col_G_row=[(x["normal"]["corr_R_column"], x["normal"]["corr_G_row"]) for x in V.values()],
            radiant_corr_R_col_G_row=[(x["normal"]["corr_R_column"], x["normal"]["corr_G_row"]) for x in R.values()],
            pass_=ok)
        bad = sum(x[k]["blue_off_ramp_hue"] + x[k]["blue_cyan_lean"] + x[k]["blue_paler_than_73ADFF"] + x[k]["other_hue_px"]
                  for x in R.values() for k in ("colour", "sss"))
        v[f"3 blue {size}"] = dict(off_ramp_px=bad, pass_=bad == 0)
        wc = sum(x[k]["white_px"] + x[k]["other_channel255_px"] for x in R.values() for k in ("colour", "sss"))
        v[f"4 white {size}"] = dict(white_or_RG255_px=wc,
                                    blue255_px=sum(x[k]["blue255_px"] for x in R.values() for k in ("colour", "sss")),
                                    pass_=wc == 0)
    txt = json.dumps(res, indent=1, default=str)
    if len(sys.argv) > 3:
        open(sys.argv[3], "w").write(txt)
    for k, x in v.items():
        print(k, "PASS" if x["pass_"] else "FAIL", {a: b for a, b in x.items() if a != "pass_"})


main()
