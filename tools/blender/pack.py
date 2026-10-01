#!/usr/bin/env python3
"""Pack a render directory into the sheets the prototype loads, with their numbers.

  python3 pack.py <render-dir> <out-dir>

Every pass was rendered on one 256x256 canvas with the entity origin exactly at
the canvas centre, so every layer's shift is its crop's centre minus that point,
computed rather than measured and adjusted. Crops keep a 1 px transparent rim.
"""
import json
import sys
from PIL import Image, ImageChops

D, OUT = sys.argv[1], sys.argv[2]
import os
os.makedirs(OUT, exist_ok=True)
ORIGIN = 128.0
PPT = 64.0          # source px per tile at scale 0.5


NOISE = 24          # shadow catchers record faint sky occlusion everywhere; below this is noise


def clean(im):
    a = im.getchannel("A").point(lambda v: 0 if v < NOISE else v)
    im.putalpha(a)
    return im


def box_of(alpha, thr=0):
    bb = alpha.point(lambda v: 255 if v > thr else 0).getbbox()
    x0, y0, x1, y1 = bb
    return (x0 - 1, y0 - 1, x1 + 1, y1 + 1)


def shift(bb):
    return (round(((bb[0] + bb[2]) / 2 - ORIGIN) / PPT, 5),
            round(((bb[1] + bb[3]) / 2 - ORIGIN) / PPT, 5))


meta = {}

idle = Image.open(f"{D}/idle.png").convert("RGBA")
bb = box_of(idle.getchannel("A"))
idle.crop(bb).save(f"{OUT}/base.png")
meta["base"] = dict(size=(bb[2] - bb[0], bb[3] - bb[1]), shift=shift(bb))

sh = clean(Image.open(f"{D}/shadow.png").convert("RGBA"))
a = sh.getchannel("A")
blk = Image.merge("RGBA", (*Image.new("RGB", sh.size, (0, 0, 0)).split(), a))
sbb = box_of(a)
blk.crop(sbb).save(f"{OUT}/shadow.png")
meta["shadow"] = dict(size=(sbb[2] - sbb[0], sbb[3] - sbb[1]), shift=shift(sbb))

diff = ImageChops.subtract(Image.open(f"{D}/working.png").convert("RGB"), idle.convert("RGB"))
ga = diff.convert("L").point(lambda v: 255 if v > 8 else 0)      # below 8 is sampling noise
gbb = box_of(ga)
glow = Image.merge("RGBA", (*diff.split(), ga))
glow.crop(gbb).save(f"{OUT}/glow.png")
meta["glow"] = dict(size=(gbb[2] - gbb[0], gbb[3] - gbb[1]), shift=shift(gbb))

lamp = Image.open(f"{D}/lamp.png").convert("RGBA")
lbb = box_of(lamp.getchannel("A"), 8)
lamp.crop(lbb).save(f"{OUT}/status-lamp.png")
meta["lamp"] = dict(size=(lbb[2] - lbb[0], lbb[3] - lbb[1]), shift=shift(lbb))

frames = [clean(Image.open(f"{D}/coupling-{f:02d}.png").convert("RGBA")) for f in range(12)]
u = None
for fr in frames:
    b = box_of(fr.getchannel("A"))
    u = b if u is None else (min(u[0], b[0]), min(u[1], b[1]), max(u[2], b[2]), max(u[3], b[3]))
fw, fh = u[2] - u[0], u[3] - u[1]
sheet = Image.new("RGBA", (fw * 12, fh))
for i, fr in enumerate(frames):
    sheet.paste(fr.crop(u), (i * fw, 0))
sheet.save(f"{OUT}/coupling.png")
meta["coupling"] = dict(size=(fw, fh), shift=shift(u), frames=12, line_length=12)


def centroid(im):
    a = im.getchannel("A")
    px = list(a.get_flattened_data())
    w = sum(px)
    return (sum(v * (i % a.width) for i, v in enumerate(px)) / w,
            sum(v * (i // a.width) for i, v in enumerate(px)) / w)


# The coupling has six-fold symmetry, so turned about its own shaft its centroid
# stays put; one turned about anywhere else drifts frame to frame.
c0 = centroid(frames[0])
drift = max(((cx - c0[0]) ** 2 + (cy - c0[1]) ** 2) ** 0.5 for cx, cy in map(centroid, frames))

# The spec's frame-0 rule: the plate with frame 0 over it is the stopped machine.
# Held to a single render of it (still.png), not to the byte: two renders of
# different scenes sample differently, and a caught shadow is not a real one.
comp = idle.copy()
comp.alpha_composite(frames[0])
diff0 = [max(px) for px in ImageChops.difference(
    comp, Image.open(f"{D}/still.png").convert("RGBA")).get_flattened_data()]

# Light the glow drove to white: white in working.png and not already white in
# idle.png (a glint on bare steel is). Over-driven emission clips there, and the
# glow layer, being working minus idle, comes out grey instead of the light's colour.
glow_white = sum(1 for w, i in zip(Image.open(f"{D}/working.png").convert("RGB").get_flattened_data(),
                                   idle.convert("RGB").get_flattened_data())
                 if min(w) >= 245 and min(i) < 245)

# Appendix C's four measurements, on the base plate
A = idle.getchannel("A")
vis = A.point(lambda v: 255 if v > 20 else 0).getbbox()
base = Image.open(f"{OUT}/base.png").getchannel("A")
W, H = base.size
meta["checks"] = {
    "centre_offset_px": (vis[0] + vis[2]) / 2 - ORIGIN,
    "edge_alpha_max": max(max(base.getpixel((0, y)), base.getpixel((W - 1, y))) for y in range(H))
                      + max(max(base.getpixel((x, 0)), base.getpixel((x, H - 1))) for x in range(W)),
    "half_width_tiles": max(abs(vis[0] - ORIGIN), abs(vis[2] - ORIGIN)) / PPT,
    "footprint_rows_tiles": ((vis[3] - ORIGIN) / PPT, "bottom edge below origin; 1.5 = on the footprint"),
    "coupling_drift_px": (round(drift, 2), "centroid travel across the 12 frames; ~0 = turning in place"),
    "frame0_vs_still": (max(diff0), round(sum(1 for v in diff0 if v > 8) / len(diff0), 4),
                        "max channel difference, and share of pixels over 8 (sampling noise)"),
    "glow_white_px": (glow_white, "pixels the working light clipped to white; 0 = the light keeps its colour"),
}
json.dump(meta, open(f"{OUT}/meta.json", "w"), indent=1)
print(json.dumps(meta, indent=1))
