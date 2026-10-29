#!/usr/bin/env python3
"""Study sheet: how vanilla's big mining drill integrates its fluid rig (task
ballast-drill-ports, T03d, before the takes).

  python3 study_sheet.py <out.png>

Per direction a row: dry (graphics_set: no pipe layers), wet with vanilla's covers, wet piped,
then the three wet layers alone over the dry drill ghosted (pipe-connections = behind,
-front, -shadow), then 2x crops of the wet drill at each of the direction's four connections
(the connection's tile ringed in blue). A notes panel says what the sheet shows.
Drawn at 1.5x (96 px a tile), the crops at 2x, on preview.py's ground; shadows at half strength.
"""
import sys

from PIL import Image, ImageDraw

import vanilla_bmd as v

CELL = 400
HEAD = 24
CROP = 2.4          # tiles round a connection, drawn at 2x
NOTES = [
    "What vanilla's big mining drill does with its fluid rig (space-age big-mining-drill.lua:124-175, 345, 434, 627-628):",
    "1. Frame: the dry drill (graphics_set) is an open gantry frame; it carries no pipework at all. The wet set "
    "(wet_mining_graphics_set, only on an ore that needs a fluid) adds three always-drawn layers per direction.",
    "2. Pipework: two runs per direction, each linking one side connection to the rear connection round the corner "
    "between them (facing north: W(-2,-1) to S(-1,2), E(2,-1) to S(1,2)). They lie along the frame's outer rails, "
    "low, hugging the perimeter, and never cross the output face.",
    "3. Where a run meets a connection: a cast junction body sits on the connection's tile (a squat flanged body on "
    "the rear face, a bulbous elbow on a side face), the run entering it from the side; the cover or the pipe joins "
    "the body, not the frame. The run keeps one bore (about half a tile on the screen) from body to body, clamped "
    "with collars at intervals, bent round the corner in one sweep.",
    "4. Layers: pipe-connections (behind) holds the parts north of the drill's middle and is drawn over the still "
    "and output, under the support and still-front; -front holds the rest, over still-front; -shadow with it.",
    "5. Dry against wet: dry shows the frame only (no stub, no socket); wet reads as plumbing added to the same "
    "frame, outermost and on top of it, so nothing clips: the pipes pass over the frame, never into it.",
]


def label(dr, x, y, text, size=15, fill=(240, 200, 90)):
    dr.text((x, y), text, fill=fill, font=v.font(size))


def crop2x(img, at):
    cx, cy = img.width / 2 + at[0] * v.PPT, img.height / 2 + at[1] * v.PPT
    h = CROP / 2 * v.PPT
    c = img.crop((round(cx - h), round(cy - h), round(cx + h), round(cy + h)))
    return c.resize((c.width * 2, c.height * 2), Image.LANCZOS)


def main():
    out = sys.argv[1]
    cols = ["dry (graphics_set)", "wet, vanilla covers", "wet, piped", "pipe-connections (behind)",
            "pipe-connections-front", "pipe-connections-shadow"]
    cw = round(CROP * v.PPT * 2)
    W = len(cols) * CELL * 3 // 2 + 2 * cw
    notes_h = 30 + 22 * len(NOTES) + 12
    H = 40 + notes_h + len(v.DIRS) * (2 * cw + HEAD)
    sheet = Image.new("RGB", (W, H), (32, 32, 34))
    dr = ImageDraw.Draw(sheet)
    label(dr, 10, 8, "Vanilla's big mining drill: its fluid rig per direction, dry and wet (study for the Ballast "
          "Drill's rig, T03d)", 22, (240, 240, 240))
    y = 44
    for i, n in enumerate(NOTES):
        label(dr, 12, y + 22 * i, n, 15, (225, 225, 225) if i else (240, 200, 90))
    y0 = 40 + notes_h
    for r, d in enumerate(v.DIRS):
        y = y0 + r * (2 * cw + HEAD)
        cs = v.conns(d)
        dry = v.vanilla(d, wet=False, size=(CELL, CELL))
        imgs = [dry, v.vanilla(d, size=(CELL, CELL)), v.vanilla(d, cover=False, size=(CELL, CELL)),
                v.alone(d, "pipe-connections", (CELL, CELL), ghost=dry),
                v.alone(d, "pipe-connections-front", (CELL, CELL), ghost=dry),
                v.alone(d, "pipe-connections-shadow", (CELL, CELL), shadow=True, ghost=dry)]
        for k, (lab, im) in enumerate(zip(cols, imgs)):
            label(dr, k * CELL * 3 // 2 + 6, y + 4, f"{d}: {lab} (1.5x)")
            big = v.grid(im, conns_=cs).convert("RGB").resize((CELL * 3 // 2, CELL * 3 // 2), Image.LANCZOS)
            sheet.paste(big, (k * CELL * 3 // 2, y + HEAD))
        wet = v.grid(v.vanilla(d, size=(CELL + 200, CELL + 200)), conns_=cs)
        for k, (x, yy, f) in enumerate(cs):
            cx, cy = len(cols) * CELL * 3 // 2 + (k % 2) * cw, y + HEAD + (k // 2) * cw
            sheet.paste(crop2x(wet, (x, yy)).convert("RGB"), (cx, cy))
            label(dr, cx + 6, cy + 4, f"2x: {f}({x},{yy})", 14, (150, 210, 255))
    assert max(sheet.size) < 8000, sheet.size
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
