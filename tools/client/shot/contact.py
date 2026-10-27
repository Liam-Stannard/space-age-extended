#!/usr/bin/env python3
"""Contact sheet(s) of the screenshot probe's shots.

Usage: contact.py SHOT_DIR SPEC_JSON OUT_DIR

One block per state: a title with what the engine said of each copy (its
direction as built, status, output), then one row per zoom, each row every
direction by day and by night, captioned; and if the spec asks for motion
frames, a row of them, each captioned with how much it changed from the
previous frame (mean absolute difference over the frame, 0-255 per channel).
The same figures go to motion.json beside the sheet: per state and direction,
change[i] is from frame i to i + 1, null where either frame is missing (the
sheet then captions the change across the gap with how many steps it spans).
Rows wider than the limit, or taller than a page can hold, are scaled down to
fit; a block that does not fit on the rest of a page carries on, row by row,
on the next one ("(cont.)"), so no sheet reaches 8000 px on either side.
Writes OUT_DIR/contact-sheet.png, or contact-sheet-1.png, -2.png, ... and
prints each path and size.
"""
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageStat

# The sheet's font is measure.py's: DejaVu Sans Bold wherever the system keeps it (Debian,
# Arch, Fedora, openSUSE, or as fc-match names it), else Pillow's default at the size asked.
# measure.py needs only Pillow and its own tools/blender modules, not Blender.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "blender"))
import measure  # noqa: E402

LIMIT = 7900          # under 8000 px on the longer side, with room to spare
PAD = 16
TITLE_H = 40          # a block's title line
CAP_H = 30            # a row's captions above its images
# The tallest image a row may hold: one block title and one row on an
# otherwise empty page still fit within LIMIT.
MAX_IMAGE_H = LIMIT - 2 * PAD - TITLE_H - CAP_H - PAD


def font(size):
    return measure.font(size, bold=True)


def state_title(shot_dir, state):
    path = os.path.join(shot_dir, state, "state.json")
    try:
        with open(path) as f:
            st = json.load(f)
    except (OSError, ValueError):
        return f"{state}: (no state.json)"
    parts = []
    for c in st.get("copies", []):
        s = f"{c['requested']}->{c['actual']} {c['status']}"
        if "generated_kw" in c:
            s += f" {c['generated_kw']:.0f} kW"
        parts.append(s)
    return f"{state}: " + "; ".join(parts)


def fit(cells):
    """Scale a row's images alike so the row fits LIMIT wide and MAX_IMAGE_H tall."""
    wsum = sum(im.width for im, _ in cells)
    hmax = max(im.height for im, _ in cells)
    scale = min(1.0, (LIMIT - PAD * (len(cells) + 1)) / wsum, MAX_IMAGE_H / hmax)
    if scale >= 1.0:
        return cells
    return [(im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS), cap)
            for im, cap in cells]


def row_height(cells):
    return max(im.height for im, _ in cells) + CAP_H + PAD


def main():
    shot_dir, spec_path, out_dir = sys.argv[1:4]
    with open(spec_path) as f:
        spec = json.load(f)
    title_font, cap_font = font(26), font(18)

    blocks = []
    motion_figures = {}
    for st in spec["states"]:
        name = st["name"]
        rows = []
        for z in spec["zooms"]:
            cells = []
            for d in spec["directions"]:
                for t in spec["daytimes"]:
                    p = os.path.join(shot_dir, name, f"{d}-{t['name']}-{z['name']}.png")
                    cap = f"{d} {t['name']} {z['name']}"
                    if os.path.exists(p):
                        cells.append((Image.open(p).convert("RGB"), cap))
                    else:
                        cells.append((None, cap + " MISSING"))
            hmax = max((im.height for im, _ in cells if im), default=100)
            cells = [(im if im is not None else Image.new("RGB", (hmax, hmax), (90, 0, 0)), cap)
                     for im, cap in cells]
            rows.append(fit(cells))
        m = spec.get("motion")
        if m:
            cells = []
            for d in spec["directions"]:
                prev, prev_j = None, None
                figures = motion_figures.setdefault(name, {}).setdefault(d, [])
                for j in range(m.get("frames", 2)):
                    # One figure per step j-1 -> j: the change, or None if either frame is missing.
                    p = os.path.join(shot_dir, name, f"motion-{d}-{j}.png")
                    if not os.path.exists(p):
                        cells.append((None, f"{d} motion {j} MISSING"))
                        if j > 0:
                            figures.append(None)
                        continue
                    im = Image.open(p).convert("RGB")
                    cap = f"{d} t+{j * m.get('every', 6)}"
                    delta = None
                    if prev is not None and prev.size == im.size:
                        delta = sum(ImageStat.Stat(ImageChops.difference(prev, im)).mean) / 3
                        cap += f" change {delta:.2f}"
                        if j - prev_j > 1:
                            cap += f" over {j - prev_j} steps"
                    if j > 0:
                        figures.append(round(delta, 3) if delta is not None and prev_j == j - 1 else None)
                    prev, prev_j = im, j
                    cells.append((im, cap))
            hmax = max((im.height for im, _ in cells if im), default=100)
            cells = [(im if im is not None else Image.new("RGB", (hmax, hmax), (90, 0, 0)), cap)
                     for im, cap in cells]
            rows.append(fit(cells))
        blocks.append((state_title(shot_dir, name), rows))

    def block_size(block):
        _, rows = block
        w = max(sum(im.width for im, _ in cells) + PAD * (len(cells) + 1) for cells in rows)
        h = TITLE_H + sum(row_height(cells) for cells in rows)
        return w, h

    if motion_figures:
        with open(os.path.join(out_dir, "motion.json"), "w") as f:
            json.dump(motion_figures, f, indent=1)
        for state, dirs in motion_figures.items():
            print(f"motion {state}: " + "; ".join(f"{d} {v}" for d, v in dirs.items()))

    # Pages are cut between rows: a block that does not fit on the rest of a
    # page goes on, under its title marked "(cont.)", on the next. fit() keeps
    # every row low enough that a title and one row fit on an empty page.
    pages, page, ph = [], [], PAD
    for title, rows in blocks:
        seg, cont = [], False
        for cells in rows:
            need = row_height(cells) + (0 if seg else TITLE_H)
            if ph + need > LIMIT and (page or seg):
                if seg:
                    page.append((title + (" (cont.)" if cont else ""), seg))
                    cont = True
                pages.append(page)
                page, ph, seg = [], PAD, []
                need = row_height(cells) + TITLE_H
            seg.append(cells)
            ph += need
        if seg:
            page.append((title + (" (cont.)" if cont else ""), seg))
    if page:
        pages.append(page)

    for n, page in enumerate(pages, 1):
        W = max(block_size(b)[0] for b in page)
        H = PAD + sum(block_size(b)[1] for b in page)
        sheet = Image.new("RGB", (W, H), (28, 28, 28))
        d = ImageDraw.Draw(sheet)
        y = PAD
        for title, rows in page:
            d.text((PAD, y), title, font=title_font, fill=(240, 200, 120))
            y += TITLE_H
            for cells in rows:
                x = PAD
                for im, cap in cells:
                    d.text((x, y), cap, font=cap_font, fill=(220, 220, 220))
                    sheet.paste(im, (x, y + 26))
                    x += im.width + PAD
                y += row_height(cells)
        name = "contact-sheet.png" if len(pages) == 1 else f"contact-sheet-{n}.png"
        path = os.path.join(out_dir, name)
        if max(sheet.size) >= 8000:  # cannot happen by the layout above; never save one if it does
            sys.exit(f"contact.py: {name} would be {sheet.size[0]}x{sheet.size[1]}, not saved")
        sheet.save(path, optimize=True)
        print(f"contact sheet: {path} {sheet.size[0]}x{sheet.size[1]}")


if __name__ == "__main__":
    main()
