#!/usr/bin/env python3
"""Build the Bed Tender crane's rotation sheets from one drawing per part.

**DO NOT RUN THIS. Its central assumption is false and it corrupts the arm.**

The claim below -- that vanilla's frames are one pose differing only in shading,
measured at "at most 26%" on part 5 -- does not generalise. Extracting frames 0,
32, 64 and 96 from vanilla's part 3 shows genuinely different views: different
shading, different self-occlusion, hoses on different sides, and frame 64 *empty*
because the part is hidden at that angle. Stamping one drawing into every frame
gives an arm whose segments never change as it swings, and which draws a segment
at angles where vanilla draws none. That is what "the crane arm is all messed up"
looked like in game.

The ten parts it wrote have been reverted to recoloured vanilla via
recolour-crane.py. Kept only as the record of an approach that was tried and
does not work; making it correct needs a 3D model, which is the same conclusion
recolour-crane.py reaches.


The crane is a turntable: seven parts, each a `rotated_sprite` with
`direction_count` 64 or 128, stored as a spritesheet of that many frames. It is
tempting to conclude that authoring one means drawing 128 angles per part. It
does not, and this tool is the proof.

**The engine does the rotation.** Every frame in vanilla's sheets is drawn with
the part *vertical*; the crane parts carry `rotated_sprite`, and the engine
selects and orients them. The frames are one pose seen from `direction_count`
camera azimuths, and what varies between them is shading and self-occlusion.
Measured on `agricultural-tower-crane-5`, frame 0 against the rest: the
silhouette differs by at most 26% and the colour by at most 47%, and the pose
not at all.

So one canonical vertical drawing per part, stamped into every frame, gives a
crane that swings correctly. What it gives up is that 26%: the truss detail and
the shading no longer shift as the camera comes round. At the 33 in-game px
these parts occupy that is a small and honest loss, and it is why the drawings
are asked for under flat, overcast, top-down light -- a strong side light baked
into a part that then rotates would be wrong at half the angles.

Placement is measured, not chosen. Each part's art is scaled and positioned to
the **median** content bounding box of vanilla's own frames, so it occupies the
same region of the frame that vanilla's did. The parts assemble by
`relative_position` and `static_length` in the prototype, which are unchanged, so
matching that region is what keeps the arm's joints meeting.

Shadows and reflections are not rebuilt: a shadow is alpha, and vanilla's is the
right shape for a part of this extent.

Run `recolour-crane.py` first and this second. That tool produces the whole set
of 29 files -- including the shadows, reflections and the two small fittings this
one does not touch -- and would overwrite these sheets if run afterwards.

**The shadows are still vanilla's shape.** A shadow is alpha, and vanilla's
silhouettes are close enough to these parts' extents to pass; redrawing them
would mean stamping our own parts through the shadow sheets' different frame
sizes and direction counts, which is worth doing only if they read wrong in a
client.

Usage:
  tools/build-crane-sheets.py --part arm_central --art path/to/drawing.png
  tools/build-crane-sheets.py --list
"""

import argparse
import os
import sys

from PIL import Image

VANILLA = ("space-age/graphics/entity/agricultural-tower/"
           "agricultural-tower-crane-")

# name -> (vanilla suffix list, frame w, h, columns, rows per file)
PARTS = {
    "hub":               (["1-1", "1-2"], 406, 330,  8, 8),
    "arm_inner":         (["3"],           82, 210, 16, 8),
    "arm_inner_joint":   (["4"],          100, 128, 16, 8),
    "arm_central":       (["5-1", "5-2"],  66, 774, 16, 4),
    "arm_central_joint": (["6"],           72, 144, 16, 8),
    "arm_outer":         (["7-1", "7-2"],  64, 628, 16, 4),
    "telescope":         (["8"],           44,  78, 16, 4),
}


def solid_bbox(im, thr=15):
    a = im.getchannel("A").point(lambda v: 255 if v > thr else 0)
    return a.getbbox()


def median_box(src_dir, part):
    """The median content box across every one of vanilla's frames.

    Frame 0 is one azimuth and can be an extreme; the median is where the part
    sits on average, which is the single placement that suits all of them.
    """
    suffixes, fw, fh, cols, rows = PARTS[part]
    boxes = []
    for suffix in suffixes:
        sheet = Image.open(os.path.join(src_dir, f"crane-{suffix}.png"
                                        if os.path.exists(os.path.join(
                                            src_dir, f"crane-{suffix}.png"))
                                        else f"{VANILLA}{suffix}.png")).convert("RGBA")
        for r in range(rows):
            for c in range(cols):
                fr = sheet.crop((c * fw, r * fh, (c + 1) * fw, (r + 1) * fh))
                bb = solid_bbox(fr)
                if bb:
                    boxes.append(bb)
    if not boxes:
        sys.exit(f"no content found in vanilla's {part} frames")
    med = []
    for i in range(4):
        vals = sorted(b[i] for b in boxes)
        med.append(vals[len(vals) // 2])
    return tuple(med), len(boxes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=sorted(PARTS))
    ap.add_argument("--art", help="one vertical drawing of this part, transparent")
    ap.add_argument("--data", default=os.path.expanduser(
        "~/.steam/debian-installation/steamapps/common/Factorio/data"))
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list:
        for name, (sfx, fw, fh, cols, rows) in sorted(PARTS.items()):
            print(f"  {name:<20} frame {fw}x{fh}  {len(sfx)} file(s) "
                  f"{cols}x{rows} = {len(sfx) * cols * rows} frames")
        return 0
    if not args.part or not args.art:
        sys.exit("--part and --art are required (or --list)")

    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = args.out_dir or os.path.join(repo, "graphics/entity/bed-tender/crane")
    os.makedirs(out_dir, exist_ok=True)

    suffixes, fw, fh, cols, rows = PARTS[args.part]
    box, n = median_box(os.path.join(args.data), args.part)
    bw, bh = box[2] - box[0], box[3] - box[1]
    print(f"  {args.part}: vanilla's median content box over {n} frames is "
          f"{box} ({bw}x{bh})")

    art = Image.open(args.art).convert("RGBA")
    ab = solid_bbox(art)
    art = art.crop(ab)
    # Fit the drawing into that box, keeping its own aspect, then centre it --
    # stretching a boom to an exact box would make it a different machine.
    scale = min(bw / art.width, bh / art.height)
    art = art.resize((max(1, round(art.width * scale)),
                      max(1, round(art.height * scale))), Image.LANCZOS)
    ox = box[0] + (bw - art.width) // 2
    oy = box[1] + (bh - art.height) // 2

    for suffix in suffixes:
        sheet = Image.new("RGBA", (cols * fw, rows * fh), (0, 0, 0, 0))
        for r in range(rows):
            for c in range(cols):
                sheet.alpha_composite(art, (c * fw + ox, r * fh + oy))
        path = os.path.join(out_dir, f"crane-{suffix}.png")
        sheet.save(path)
        print(f"  ok  {os.path.relpath(path, repo)}  {sheet.size}  "
              f"{cols * rows} frames of {fw}x{fh}, art at ({ox}, {oy}) "
              f"{art.width}x{art.height}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
