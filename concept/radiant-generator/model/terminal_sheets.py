"""T08k's review sheets: the terminal box on the tube column's plinth, before and after, and the power's
path traced from the tubes to the switchgear. Plain Python (PIL), run after two --study renders:

  python3 terminal_sheets.py <before look-00.png> <after look-00.png> <out-dir>

Both renders are the model's --study 0 look (frame 0 working, on the ground catcher, 4x: 256 px a tile),
as T08i's tray-t08i.png and T08j's terminal-t08j.png were cut from. Writes, in <out-dir>:
  terminal-t08k.png   before | after in tray-t08i.png's framing (4x), the box at 8x, the glands at 8x
  path-t08k.png       the whole path at 4x, each joint numbered and named
  terminal-t08k-phone.png   the top sheet, phone-sized: the after crop, the before beside it, the path key
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

BEFORE, AFTER, OUT = sys.argv[1:4]
PPT = 256                                   # 4x render: px a tile
W_, H_ = Image.open(AFTER).size
BG = (30, 30, 30)
TXT, HEAD = (235, 235, 235), (240, 228, 120)


def font(n):
    for p in ("/usr/share/fonts/TTF/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, n)
    return ImageFont.load_default()


F, FS, FB = font(20), font(17), font(24)


def load(p):
    im = Image.open(p).convert("RGBA")
    bg = Image.new("RGBA", im.size, BG + (255,))
    bg.alpha_composite(im)
    return bg.convert("RGB")


B, A = load(BEFORE), load(AFTER)


def px(x, y, z):
    """Model point (tiles) to 4x render px: the rig's 60 degree camera, so screen up is y + z/2."""
    return W_ / 2 + x * PPT, H_ / 2 - (y + 0.5 * z) * PPT


def crop(im, box, k=1):
    c = im.crop(box)
    return c.resize((c.width * k, c.height * k), Image.NEAREST) if k != 1 else c


def tag(im, text):
    d = ImageDraw.Draw(im)
    d.text((5, 3), text, fill=(255, 255, 255), font=F, stroke_width=2, stroke_fill=(0, 0, 0))
    return im


def sheet(rows, title, w=None):
    """rows: (caption, [images]) -> one sheet."""
    pad = 16
    width = w or max(sum(i.width for i in ims) + pad * (len(ims) + 1) for _, ims in rows)
    height = 50 + sum(36 + max(i.height for i in ims) + pad for _, ims in rows)
    S = Image.new("RGB", (width, height), BG)
    d = ImageDraw.Draw(S)
    d.text((pad, 12), title, fill=TXT, font=FB)
    y = 50
    for cap, ims in rows:
        d.text((pad, y + 6), cap, fill=HEAD, font=F)
        y += 36
        x = pad
        for i in ims:
            S.paste(i, (x, y))
            x += i.width + pad
        y += max(i.height for i in ims) + pad
    return S


# tray-t08i.png's framing: the tube-column tray, 4x (found in the T08j render by matching its 'after' crop)
FRAME = (1640, 1000, 1960, 1440)
# the box and its glands, 8x
BOXZ = (1730, 1100, 1890, 1380)
GLANDZ = (1750, 1190, 1870, 1290)
rows = [
    ("Tube-column tray (Liam's framing, as tray-t08i.png), 4x", [tag(crop(B, FRAME), "before"), tag(crop(A, FRAME), "after")]),
    ("the terminal box, 8x: bus clamp on its bushing, lid, glands", [tag(crop(B, BOXZ, 2), "before"),
                                                                    tag(crop(A, BOXZ, 2), "after")]),
    ("the glands and the cables straight into the tray's open end, 12x", [tag(crop(B, GLANDZ, 3), "before (12x)"),
                                                                     tag(crop(A, GLANDZ, 3), "after (12x)")]),
]
sheet(rows, "T08k terminal box, before (T08j, 347bccc)  |  after (T08k), frame 0 working").save(
    os.path.join(OUT, "terminal-t08k.png"))

# ---------------------------------------------------------------- the path, traced
JOINTS = [  # model point (tiles), label, the label's side
    ((2.25, 0.3, 1.28), "1 tube collector caps (5), finned copper", "L"),
    ((2.44, -0.4, 1.2), "2 copper bus along the caps", "R"),
    ((2.42, -1.02, 1.375), "3 bus bent up into the bushing clamp", "R"),
    ((2.17, -1.0, 1.3), "4 terminal box on the plinth, foot bolted", "L"),
    ((2.21, -1.22, 1.24), "5 a gland a cable, box south face", "L"),
    ((2.3, -1.43, 1.23), "6 tray, level, cables under ochre cleats", "R"),
    ((2.28, -1.62, 1.235), "7 off its open south end, over the edge", "R"),
    ((2.24, -1.74, 1.17), "8 gland on the switchgear's top", "L"),
]
PATHBOX = (1440, 560, 2080, 1520)
P = crop(A, PATHBOX).copy()
pw = 420
canvas = Image.new("RGB", (P.width + 2 * pw, P.height), BG)
canvas.paste(P, (pw, 0))
d = ImageDraw.Draw(canvas)
ys_l = ys_r = 0
for k, (p, text, side) in enumerate(JOINTS):
    x, y = px(*p)
    x, y = x - PATHBOX[0] + pw, y - PATHBOX[1]
    d.ellipse((x - 9, y - 9, x + 9, y + 9), outline=(255, 230, 60), width=3)
    lx = 10 if side == "L" else pw + P.width + 10
    ly = max(y - 12, (ys_l if side == "L" else ys_r))
    d.line((x + (-9 if side == "L" else 9), y, (pw - 8) if side == "L" else pw + P.width + 6, ly + 12),
           fill=(255, 230, 60), width=2)
    d.text((lx, ly), text, fill=TXT, font=FS)
    if side == "L":
        ys_l = ly + 30
    else:
        ys_r = ly + 30
path = sheet([("tubes -> bus -> box -> glands -> tray -> switchgear, 4x, frame 0 working", [canvas])],
             "T08k: the power's path from the tubes to the switchgear")
path.save(os.path.join(OUT, "path-t08k.png"))

# ---------------------------------------------------------------- the clipping check, by eye
# every end on the path, 4x (the render's own pixels) and the same at 12x: where a cable, the bus or a gland meets
# its host, nothing passes through a part and every end is held (gland, clamp or cleat). Working (look-00) and
# stopped (unlit-00, the idle the engine draws), where the light differs
UNLIT = AFTER.replace("look-", "unlit-")
U = load(UNLIT) if os.path.exists(UNLIT) else None
ENDS = [((2.42, -1.02, 1.375), "a  bus into its clamp, on the bushing"),
        ((2.29, -1.22, 1.24), "b  three glands, box south face"),
        ((2.3, -1.32, 1.23), "c  tray's open north end"),
        ((2.3, -1.45, 1.23), "d  the cleats"),
        ((2.3, -1.58, 1.23), "e  tray's open south end, over the edge"),
        ((2.24, -1.74, 1.15), "f  gland on the switchgear's top")]
crops = []
for p_, cap in ENDS:
    x, y = px(*p_)
    bx = (int(x) - 50, int(y) - 40, int(x) + 50, int(y) + 40)
    ims = [tag(crop(A, bx), "4x"), tag(crop(A, bx, 3), "12x working")]
    if U is not None:
        ims.append(tag(crop(U, bx, 3), "12x stopped"))
    crops.append((cap, ims))
sheet(crops, "T08k clipping check: every end on the path, frame 0").save(os.path.join(OUT, "clip-t08k.png"))

# ---------------------------------------------------------------- the phone sheet
ph = sheet([("after (T08k): the box on the plinth, 4x", [tag(crop(A, FRAME), "after"), tag(crop(B, FRAME), "before")]),
            ("the path, numbered", [canvas.resize((canvas.width * 2 // 3, canvas.height * 2 // 3), Image.LANCZOS)])],
           "Radiant Generator T08k: terminal box")
ph.thumbnail((1080, 99999), Image.LANCZOS)
ph.save(os.path.join(OUT, "terminal-t08k-phone.png"))
print("wrote", OUT)
