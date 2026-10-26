"""Vanilla references for the radiant look study: each a plate and its glow layers, composed
at 64 px a tile from the game's own sheets (frame 0), as the prototypes place them.

comp(canvas, layers) -> (plate RGBA, additive light RGB)
A layer: (path, w, h, line_length, frame, shift_x, shift_y [util.by_pixel], mode)
  mode "n" paint, "add" additive glow (draw_as_glow), "tintblue" paint tinted #1F63FF
  (the chemical plant's recipe-tinted liquid, shown in the radiant blue)
"""
import os
import sys

from PIL import Image, ImageChops

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../tools"))
import paths  # noqa: E402   tools/paths.py: where Factorio is

D = paths.factorio_data() + "/"
B = "base/graphics/entity/"
S = "space-age/graphics/entity/"


def frame(path, w, h, ll, i=0):
    im = Image.open(D + path).convert("RGBA")
    x, y = (i % ll) * w, (i // ll) * h
    return im.crop((x, y, x + w, y + h))


REFS = {
    "chemical-plant": ((240, 300), [(B + "chemical-plant/chemical-plant-north-base.png", 204, 292, 1, 0, 1, 0, "n"),
                                    (B + "chemical-plant/chemical-plant-liquid-north.png", 66, 44, 6, 0, 23, 15, "tintblue"),
                                    (B + "chemical-plant/chemical-plant-north-anim-1.png", 114, 68, 4, 0, -0.5, -27, "n")]),
    "oil-refinery": ((360, 450), [(B + "oil-refinery/north/oil-refinery-north.png", 356, 446, 1, 0, 0, -10, "n"),
                                  (B + "oil-refinery/north/oil-refinery-lights-north.png", 302, 248, 1, 0, -2.5, -49.5, "add")]),
    "nuclear-reactor": ((330, 330), [(B + "nuclear-reactor/reactor.png", 302, 318, 1, 0, -5, -7, "n"),
                                     (B + "nuclear-reactor/reactor-lights-color.png", 320, 320, 1, 0, -1, -6, "add")]),
    "fusion-generator": ((250, 380), [(S + "fusion-generator/north/fusion-generator-north.png", 244, 376, 3, 0, -2, -2, "n"),
                                      (S + "fusion-generator/north/fusion-generator-north-glow.png", 202, 336, 3, 0, 0, -4, "add")]),
    "fusion-reactor": ((450, 460), [(S + "fusion-reactor/fusion-reactor-main.png", 444, 456, 1, 0, 1, -5.5, "n"),
                                    (S + "fusion-reactor/fusion-reactor-glow.png", 396, 428, 1, 0, 1.5, -11, "add")]),
    "centrifuge": ((210, 270), [(B + "centrifuge/centrifuge-ABC.png", 194, 248, 8, 0, -2.5, -18, "n"),
                                (B + "centrifuge/centrifuge-ABC-light.png", 200, 262, 8, 0, -0.5, -13.5, "add")]),
    "uranium-ore": ((128, 128), [(B + "uranium-ore/uranium-ore.png", 128, 128, 8, 5, 0, 0, "n"),
                                 (B + "uranium-ore/uranium-ore-glow.png", 128, 128, 8, 5, 0, 0, "add")]),
    "cryogenic-plant": ((390, 400), [(S + "cryogenic-plant/cryogenic-plant-main.png", 380, 396, 1, 0, 3, -3.5, "n"),
                                     (S + "cryogenic-plant/cryogenic-plant-anim6-base.png", 74, 102, 8, 0, 30.5, 49, "n"),
                                     (S + "cryogenic-plant/cryogenic-plant-anim1-base.png", 122, 94, 8, 0, -8, -43.5, "n"),
                                     (S + "cryogenic-plant/cryogenic-plant-anim1-working.png", 106, 64, 8, 0, -7, -38, "n"),
                                     (S + "cryogenic-plant/cryogenic-plant-anim3-working.png", 20, 106, 16, 0, 65.5, -8.5, "n"),
                                     (S + "cryogenic-plant/cryogenic-plant-glass.png", 274, 228, 1, 0, 4, -7.5, "n"),
                                     (S + "cryogenic-plant/cryogenic-plant-working-lights.png", 110, 162, 8, 0, 41, -51, "add"),
                                     (S + "cryogenic-plant/cryogenic-plant-anim6-working-light.png", 74, 102, 8, 0, 30.5, 49, "add")]),
    "lithium-brine": ((170, 124), [(S + "lithium-brine/lithium-brine.png", 166, 120, 4, 0, 1.5, 4.5, "n")]),
}


def comp(canvas, layers):
    W, H = canvas
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow = Image.new("RGB", (W, H))
    for path, w, h, ll, i, sx, sy, mode in layers:
        f = frame(path, w, h, ll, i)
        x, y = int(round(W / 2 + sx * 2 - w / 2)), int(round(H / 2 + sy * 2 - h / 2))
        if mode == "add":
            g = Image.new("RGB", (W, H))
            g.paste(f.convert("RGB"), (x, y))
            glow = ImageChops.add(glow, g)
            continue
        if mode == "tintblue":
            a = f.getchannel("A")
            L = f.convert("L")
            f = Image.merge("RGBA", (L.point(lambda v: v * 0x1F // 255), L.point(lambda v: v * 0x63 // 255), L, a))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.paste(f, (x, y))
        base = Image.alpha_composite(base, layer)
    return base, glow
