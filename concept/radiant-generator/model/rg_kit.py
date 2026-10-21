"""Radiant Generator, the shipping model: the shared kit (concept/radiant-generator/model/).

Round 7's kit (options/round-7/r7_kit.py: the Carousel Foundry refined, signed off by Liam
2026-10-19, "Sign off") copied, its parts and their finish unchanged, with what the shipping
model needs (spec: concept/radiant-generator/building-spec-radiant-generator.md):

  - the light through tools/blender/radiant.py (spec 3.3): round 7's own isotope() materials
    are replaced by radiant.Radiant liquids of its four shapes -- the collector head's
    bullseye port a disc, the plate rack's slot a slot, the tube emitters tubes, the well's
    mouth a surface -- with flicker 0 and no pulse; round 7's strength curves
    (window_lit(), the slot's breathing, tube_phase(), well_lit()) applied per window after
    radiant's pose() (strength_curves()). The glass over them is radiant's: the tubes'
    envelopes its round glass, the port's and slot's panes its thin pane.
  - layers (spec 7): every pivot that moves names the layer it belongs to (pivot(layer=)),
    and every part under it is in that layer (layer_of()); everything else is the plate.
  - a parent stack (frame(), in the model), so the wreck can build kit parts tilted and sunk.
  - run(), glow_pass() and the round's own --frames/--pick/--colourmap are gone: the model
    script renders the passes render.json declares.

Units are tiles; north is +Y. The canvas is the model's (radiant_generator.py), the entity
origin at its centre (contract.py). Nothing here is adopted; nothing goes to graphics/.
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import rig  # noqa: E402
import radiant  # noqa: E402
from materials import TEX, layered, hazard_pattern, _G  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0]
os.makedirs(OUT, exist_ok=True)


def opt(name, default):
    return type(default)(argv[argv.index(name) + 1]) if name in argv else default


# the canvas, sprite px, the entity origin at its centre (contract.py): round 7's 512 x 448 had
# the origin at (208, 272), 304 px east of it for the shadow and 272 above for the rise and the
# crane's shadow; centred, both kept
CANVAS = (608, 544)
CENTRE = (CANVAS[0] // 2, CANVAS[1] // 2)
PI = math.pi

sc = rig.reset()
sc.cycles.samples = 80
ROOT = rig.turntable(rig.stretch_root())


# ---------------------------------------------------------------- the finish (Reaction Plant round 5)
def lead_finish(tops, bloom=1.0, gain=1.0):
    """Weathered lead sheet: a dull warm grey in sheets of different age; the bloom (white
    lead salts) a dry cream hanging in runs below every band and flange, crusted in seams."""
    def pat(g):
        geo = g.node("ShaderNodeNewGeometry")
        pos, nrm = geo.outputs["Position"], geo.outputs["Normal"]
        z = g.node("ShaderNodeSeparateXYZ", Vector=pos).outputs["Z"]
        nz = g.node("ShaderNodeSeparateXYZ", Vector=nrm).outputs["Z"]
        tone = g.remap(g.noise(pos, 1.8, detail=2), 0.42, 0.58)
        base = g.mixc(tone, rig.srgb("#66625C"), rig.srgb("#86807A"))
        if gain != 1.0:
            base = g.mulc(base, (gain, gain, gain * 0.98, 1.0))
        if not bloom:
            return base
        vertical = g.remap(nz, 0.5, 0.1)
        st = g.node("ShaderNodeMapping", Vector=pos)
        st.inputs["Scale"].default_value = (1.0, 1.0, 0.3)
        runs = g.image(f"{TEX}/maps/rust_streak.png", st.outputs[0], 0.8).outputs["Color"]
        patches = g.remap(g.noise(pos, 5, detail=3), 0.62, 0.74)
        hang = None
        for top, length in tops:
            below = g.math("MULTIPLY", g.remap(z, top - length, top), g.remap(z, top + 0.015, top))
            hang = below if hang is None else g.math("MAXIMUM", hang, below)
        streak = g.math("MULTIPLY", g.math("MULTIPLY", hang, g.remap(runs, 0.35, 0.7)), vertical)
        ao = g.node("ShaderNodeAmbientOcclusion", Distance=0.1).outputs["AO"]
        cav = g.math("MULTIPLY", g.math("SUBTRACT", 1.0, ao), g.remap(g.noise(pos, 22, detail=4), 0.4, 0.6))
        m = g.math("ADD", g.math("MULTIPLY", streak, 1.3), g.math("MULTIPLY", cav, 1.2))
        m = g.math("ADD", m, g.math("MULTIPLY", patches, 0.4))
        m = g.math("MULTIPLY", m, 0.8 * bloom, clamp=True)
        crust = g.mixc(g.noise(pos, 37, detail=3), rig.srgb("#B4A486"), rig.srgb("#D8CAA6"))
        return g.mixc(m, base, crust)
    return pat


def soften_grain(mat, lo=0.94, hi=1.04, bump=0.08):
    for nd in mat.node_tree.nodes:
        if nd.type == "MAP_RANGE" and abs(nd.inputs["To Min"].default_value - 0.7) < 1e-6 \
                and abs(nd.inputs["To Max"].default_value - 1.22) < 1e-6:
            nd.inputs["To Min"].default_value = lo
            nd.inputs["To Max"].default_value = hi
        if nd.type == "BUMP":
            nd.inputs["Strength"].default_value = bump


def worn_paint(mat, paint, chips=0.5, under="#4A4642", rust=0.5, wiped=0.4, warm=0.6, sheen=None, mottle=0.12,
               film=0.3):
    """The Reaction Plant's round-5 finish, unchanged: paint keeps its colour, chipped to
    metal or rust at edges, rust in the seams, at the foot and down from the bands, a dirt
    film and streaks, shaded undersides, a few wiped patches."""
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    col = next(l for l in nt.links if l.to_socket == bsdf.inputs["Base Color"]).from_socket
    rough_link = next((l for l in nt.links if l.to_socket == bsdf.inputs["Roughness"]), None)
    rough = rough_link.from_socket if rough_link is not None else None
    met_link = next((l for l in nt.links if l.to_socket == bsdf.inputs["Metallic"]), None)
    g = _G(mat)
    geo = g.node("ShaderNodeNewGeometry")
    pos, normal = geo.outputs["Position"], geo.outputs["Normal"]
    ao = g.node("ShaderNodeAmbientOcclusion", Distance=0.25).outputs["AO"]
    cav = g.math("SUBTRACT", 1.0, ao)
    if mottle:
        big = g.noise(pos, 3.2, detail=5, rough=0.6, distortion=0.4)
        rm = g.math("MULTIPLY", g.remap(big, 0.6, 0.7), mottle, clamp=True)
        col = g.mixc(rm, col, rig.srgb("#5A3418"))
    if film:
        fm = g.math("MULTIPLY", g.remap(g.noise(pos, 4.5, detail=6, rough=0.62, distortion=0.3), 0.38, 0.7), film,
                    clamp=True)
        col = g.mixc(fm, col, g.mulc(col, rig.srgb("#8A7258")))
    wipe = None
    if wiped:
        wipe = g.math("MULTIPLY", g.remap(g.noise(pos, 2.4, detail=2, rough=0.4), 0.6, 0.68), wiped, clamp=True)
        clean = g.mulc(rig.srgb(paint), (1.06, 1.05, 1.02, 1.0))
        col = g.mixc(wipe, col, g.mixc(0.3, clean, col))
    if chips:
        bevel = g.node("ShaderNodeBevel", Radius=0.06).outputs[0]
        dot = g.node("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        g.l.new(bevel, dot.inputs[0])
        g.l.new(normal, dot.inputs[1])
        edge = g.remap(dot.outputs["Value"], 0.998, 0.93)
        flake = g.noise(pos, 15, detail=4, rough=0.72, distortion=0.8)
        thr = g.math("SUBTRACT", 0.63, g.math("MULTIPLY", edge, 0.14))
        bare = g.math("MULTIPLY", g.math("GREATER_THAN", flake, thr), chips, clamp=True)
        rim = g.math("MULTIPLY", g.math("GREATER_THAN", flake, g.math("SUBTRACT", thr, 0.03)), chips, clamp=True)
        col = g.mixc(rim, col, rig.srgb("#4E2A14"))
        metal = g.mixc(g.noise(pos, 60, detail=2), rig.srgb(under), g.mulc(rig.srgb(under), (1.35, 1.32, 1.28, 1)))
        rusty = g.mixc(g.noise(pos, 31, detail=3), rig.srgb("#4A230E"), rig.srgb("#7E4420"))
        metal = g.mixc(g.remap(g.noise(pos, 5.5, detail=2), 0.45, 0.55), metal, rusty)
        col = g.mixc(bare, col, metal)
        if met_link is not None:
            nt.links.new(g.mixf(bare, met_link.from_socket, 0.6), bsdf.inputs["Metallic"])
        if rough is not None:
            rough = g.mixf(bare, rough, 0.4)
    if film:
        nz0 = g.node("ShaderNodeSeparateXYZ", Vector=normal).outputs["Z"]
        st = g.node("ShaderNodeMapping", Vector=pos)
        st.inputs["Scale"].default_value = (1.0, 1.0, 0.15)
        runs = g.remap(g.image(f"{TEX}/maps/rust_streak.png", st.outputs[0], 1.6).outputs["Color"], 0.5, 0.85)
        streak = g.math("MULTIPLY", g.math("MULTIPLY", runs, g.remap(nz0, 0.6, 0.2)), 0.55 * film * 2, clamp=True)
        col = g.mixc(streak, col, g.mulc(col, rig.srgb("#7A6450")))
        nz = g.node("ShaderNodeSeparateXYZ", Vector=normal).outputs["Z"]
        down = g.math("MULTIPLY", g.remap(nz, 0.1, -0.7), 0.55 * min(1.0, film * 2), clamp=True)
        col = g.mixc(down, col, g.mulc(col, rig.srgb("#6A5440")))
        zz = g.node("ShaderNodeSeparateXYZ", Vector=pos).outputs["Z"]
        foot = g.math("MULTIPLY", g.remap(zz, 0.32, 0.04), g.remap(g.noise(pos, 8, detail=4, rough=0.6), 0.45, 0.62),
                      clamp=True)
        col = g.mixc(g.math("MULTIPLY", foot, rust, clamp=True), col,
                     g.mixc(g.noise(pos, 19, detail=3), rig.srgb("#40200C"), rig.srgb("#7A4220")))
    if rust:
        rc = g.mixc(g.noise(pos, 9, detail=4), rig.srgb("#3A1C0A"), rig.srgb("#7A4220"))
        seam = g.math("MULTIPLY", g.math("MULTIPLY", cav, 2.2),
                      g.remap(g.noise(pos, 14, detail=4), 0.35, 0.6), clamp=True)
        col = g.mixc(g.math("MULTIPLY", seam, rust, clamp=True), col, rc)
    col = g.mulc(col, (1.0 + 0.02 * warm, 1.0, 1.0 - 0.06 * warm, 1.0))
    dm = g.noise(pos, 7.5, detail=5, rough=0.6)
    col = g.mulc(col, g.gray(g.remap(dm, 0.3, 0.7, 0.8, 1.04)))
    fg = g.noise(pos, 22, detail=4, rough=0.7)
    col = g.mulc(col, g.gray(g.remap(fg, 0.3, 0.7, 0.84, 1.06)))
    dirt = g.math("MULTIPLY", cav, 1.2, clamp=True)
    if wipe is not None:
        dirt = g.math("MULTIPLY", dirt, g.math("SUBTRACT", 1.0, g.math("MULTIPLY", wipe, 0.6)))
    col = g.mixc(dirt, col, rig.srgb("#352820"))
    nt.links.new(col, bsdf.inputs["Base Color"])
    if rough is not None:
        r = rough
        if wipe is not None:
            r = g.mixf(wipe, r, 0.34)
        if sheen is not None:
            sh = g.mixf(g.remap(dm, 0.4, 0.62), sheen, min(0.8, sheen + 0.3))
            r = g.mixf(0.75, r, sh)
        nt.links.new(r, bsdf.inputs["Roughness"])
    return mat


WET = ("#3A1E0C", "#7A4018")
RUNS = ((0.62, 0.3), (0.95, 0.3), (1.35, 0.3), (1.65, 0.35))
M = {}
FINISH = {}
COLOURS = {}              # material -> (colour-map group, key hex): round 7's, kept


def paint(key, hexc, under, group, keyhex, chips=0.65, rust=0.65, wiped=0.25, warm=0.3, film=0.42, metal=None,
          **kw):
    """A painted unit in vanilla's idiom: a layered() part with worn_paint() over it."""
    args = dict(metal=metal or under, paint_metal=0.08, paint_rough=0.58, wear=0.25, rust=0.16, dust=0.35,
                grime=0.65, jitter=0.06, ground=0.8, drips=RUNS, drip=0.85, rust_tint=WET)
    args.update(kw)
    M[key] = layered(key, hexc, **args)
    FINISH[key] = (hexc, chips, under, rust, wiped, warm, None, 0.2, film)
    COLOURS[key] = (group, keyhex)


def build_materials(lead_tops):
    M["lead"] = layered("lead", "#6A6258", metal="#BCB4A2", paint_metal=0.3, paint_rough=0.55, wear=0.3,
                        rust=0.06, dust=0.5, grime=0.8, jitter=0.08, ground=0.75, pattern=lead_finish(lead_tops),
                        drips=tuple((t - 0.03, l * 0.8) for t, l in lead_tops), drip=0.6, rust_tint=WET)
    FINISH["lead"] = ("#7A746C", 0.0, "#8A8478", 0.55, 0.2, 0.6, 0.5, 0.4, 0.4)
    M["lead_new"] = layered("lead_new", "#7A7266", metal="#B4AC9C", paint_metal=0.35, paint_rough=0.55, wear=0.2,
                            rust=0.0, dust=0.3, grime=0.6, jitter=0.03, ground=0.5,
                            pattern=lead_finish(lead_tops, bloom=0.0, gain=1.12))
    FINISH["lead_new"] = ("#7A7266", 0.0, "#8A8478", 0.2, 0.2, 0.6, 0.38, 0.1, 0.15)
    paint("oxide", "#6E2C1E", "#4A403A", "oxide red paint", "#B0402A", chips=0.75, rust=0.7, metal="#5A4E46",
          paint_rough=0.7)
    paint("ochre", "#9C7426", "#4E463E", "ochre paint", "#D8A830", chips=0.55, film=0.45, metal="#5E544A",
          paint_rough=0.55)
    paint("green", "#4E6034", "#4A443E", "weathered green paint", "#5E8A38", chips=0.7, metal="#5A544C",
          paint_rough=0.62)
    paint("cream", "#ACA084", "#4E463E", "cream paint", "#E8DCB8", wiped=0.3, film=0.45, metal="#5E564C",
          paint_rough=0.6)
    paint("grey", "#6E6A62", "#8A8478", "grey paint", "#8A9098", chips=0.6, warm=0.5, film=0.4, metal="#9A9488",
          paint_rough=0.55, paint_metal=0.15)
    paint("teal", "#3E6462", "#4A443E", "teal paint (the radiant family's roofs)", "#40A0A0", chips=0.6,
          metal="#5A544C", paint_rough=0.6)
    M["dark_steel"] = layered("dark_steel", "#3E3934", metal="#8C8272", paint_metal=0.35, paint_rough=0.55,
                              wear=0.4, rust=0.35, dust=0.35, grime=0.7, ground=0.8, rust_tint=WET)
    FINISH["dark_steel"] = ("#3E3934", 0.3, "#8C8272", 0.7, 0.15, 0.6, 0.45, 0.25, 0.2)
    M["bare"] = layered("bare", "#A8A090", metal="#D8D0BE", paint_metal=0.85, paint_rough=0.3, wear=0.5,
                        rust=0.16, dust=0.12, grime=0.5, ground=0.6)
    FINISH["bare"] = ("#A8A090", 0.0, "#D8D0BE", 0.45, 0.2, 0.5, 0.2, 0.1, 0.25)
    M["seam"] = layered("seam", "#8A8070", metal="#B0A690", paint_metal=0.7, paint_rough=0.4, wear=0.3,
                        rust=0.25, dust=0.0, jitter=0.04, ground=0.7)
    FINISH["seam"] = ("#8A8070", 0.0, "#B0A690", 0.4, 0.0, 0.6, None, 0.0, 0.0)
    M["bolt"] = layered("bolt", "#5A4A3A", metal="#A89880", paint_metal=0.5, paint_rough=0.5, wear=0.5,
                        rust=0.75, dust=0.2, grime=0.6, rust_tint=WET)
    FINISH["bolt"] = ("#5A4A3A", 0.0, "#A89880", 0.8, 0.0, 0.8, None, 0.3, 0.0)
    M["copper"] = layered("copper", "#94592C", metal="#D09060", paint_metal=0.9, paint_rough=0.32, wear=0.45,
                          rust=0.04, dust=0.2, grime=0.5, patina=0.9)
    FINISH["copper"] = ("#94592C", 0.0, "#D09060", 0.15, 0.25, 0.3, 0.26, 0.05, 0.35)
    M["brass"] = layered("brass", "#9A7438", metal="#D0AC66", paint_metal=0.9, paint_rough=0.35, wear=0.5,
                         rust=0.1, dust=0.2)
    FINISH["brass"] = ("#9A7438", 0.0, "#D0AC66", 0.2, 0.3, 0.3, 0.28, 0.0, 0.2)
    M["ceramic"] = layered("ceramic", "#B8AE98", metal="#8A8070", paint_metal=0.0, paint_rough=0.7, wear=0.2,
                           rust=0.05, dust=0.4, grime=0.6, jitter=0.05)
    FINISH["ceramic"] = ("#B8AE98", 0.3, "#6A6052", 0.3, 0.0, 0.4, None, 0.0, 0.35)
    M["hose"] = layered("hose", "#5E4636", metal="#9A7E66", paint_metal=0.0, paint_rough=0.62, wear=0.35,
                        rust=0.0, dust=0.5, grime=0.6, jitter=0.06)
    FINISH["hose"] = ("#5E4636", 0.0, "#5E4636", 0.0, 0.2, 0.5, None, 0.0, 0.2)
    M["hose_k"] = layered("hose_k", "#38302A", metal="#7A6E62", paint_metal=0.0, paint_rough=0.6, wear=0.35,
                          rust=0.0, dust=0.55, grime=0.5, jitter=0.06)
    FINISH["hose_k"] = ("#38302A", 0.0, "#38302A", 0.0, 0.2, 0.6, None, 0.0, 0.0)
    M["lag"] = layered("lag", "#9A8A68", metal="#B0A080", paint_metal=0.0, paint_rough=0.9, wear=0.25,
                       rust=0.15, dust=0.5, grime=0.7, jitter=0.1, ground=0.6)
    FINISH["lag"] = ("#9A8A68", 0.0, "#9A8A68", 0.45, 0.2, 0.6, None, 0.2, 0.45)
    for k, c in (("red", "#A8301E"), ("yellow", "#D0A428")):
        M[k] = layered(k, c, metal="#6A5A50", paint_metal=0.05, paint_rough=0.5, wear=0.35, rust=0.1, dust=0.2,
                       grime=0.4, jitter=0.04)
        FINISH[k] = (c, 0.5, "#6A5A50", 0.3, 0.0, 0.0, None, 0.0, 0.2)
    M["hazard"] = layered("hazard", "#B8962E", paint_metal=0.1, paint_rough=0.85, wear=0.6, rust=0.3, dust=0.6,
                          grime=0.6, pattern=lambda g: g.mixc(0.25, hazard_pattern(g), (0.16, 0.12, 0.08, 1.0)))
    FINISH["hazard"] = ("#B8962E", 0.4, "#5A4E46", 0.4, 0.0, 0.4, None, 0.1, 0.3)
    M["stencil"] = layered("stencil", "#CEC2A4", metal="#5A5044", paint_metal=0.05, paint_rough=0.8, wear=0.5,
                           rust=0.2, dust=0.3, grime=0.4, jitter=0.05)
    FINISH["stencil"] = ("#CEC2A4", 0.4, "#5A5044", 0.4, 0.0, 0.4, None, 0.0, 0.3)
    # the cable sleeves' label paint: round 7's #D8CCAE, worn to metal and rough 0.7, threw sun glints at 255
    # that the glow's faintest tail tipped to white (pack.py's clipped check, T08): the cream paint (spec 3.3), matte
    M["label"] = layered("label", "#ACA084", paint_metal=0.0, paint_rough=0.9, wear=0.0, rust=0.0, dust=0.3,
                         grime=0.3, jitter=0.08)
    M["gauge"] = layered("gauge", "#DCD2BA", paint_metal=0.0, paint_rough=0.3, wear=0.1, rust=0.0, dust=0.2,
                         grime=0.4)
    M["needle"] = layered("needle", "#9A2A1A", paint_metal=0.0, paint_rough=0.5, wear=0.0, rust=0.0, dust=0.0,
                          grime=0.0)
    M["rubber"] = layered("rubber", "#26201C", metal="#4A4038", paint_metal=0.0, paint_rough=0.6, wear=0.1,
                          rust=0.0, dust=0.3, grime=0.3)
    M["dark"] = layered("dark", "#1E1814", paint_metal=0.0, paint_rough=0.8, wear=0.0, rust=0.0, dust=0.0,
                        grime=0.0)
    for n_, c_, e_ in (("red", "#9E4430", "#C88068"), ("yellow", "#B89440", "#DCC488"),
                       ("green", "#5A6E42", "#98A880"), ("black", "#34302C", "#746C64"),
                       ("grey", "#4A443E", "#7C746A")):
        M["cable_" + n_] = layered("cable_" + n_, c_, metal=e_, paint_metal=0.0, paint_rough=0.5, wear=0.3,
                                   rust=0.0, dust=0.3, grime=0.4, jitter=0.05)
        COLOURS["cable_" + n_] = ("cables", "#A070C0")
    for k, m in M.items():
        soften_grain(m)
        if k in FINISH:
            p, ch, und, ru, wi, wa, sh, mo, fi = FINISH[k]
            worn_paint(m, p, chips=ch, under=und, rust=ru, wiped=wi, warm=wa, sheen=sh, mottle=mo, film=fi)
    COLOURS.update({
        "lead": ("lead (holds the isotope)", "#8C8880"), "lead_new": ("lead (holds the isotope)", "#8C8880"),
        "dark_steel": ("dark steel", "#3A3634"), "bare": ("bare steel", "#D0D4D8"),
        "seam": ("bare steel", "#D0D4D8"), "bolt": ("rusty bolts and rivets", "#7A3A12"),
        "copper": ("copper (bus, coils)", "#E07838"), "brass": ("brass", "#C8A050"),
        "ceramic": ("ceramic", "#F4F0E0"),
        "hose": ("rubber hose, tan", "#7A5A40"), "hose_k": ("rubber hose, black", "#1E1A18"),
        "rubber": ("rubber hose, black", "#1E1A18"), "dark": ("rubber hose, black", "#1E1A18"),
        "lag": ("lagging canvas", "#B8A27A"),
        "red": ("red accents", "#E02818"), "yellow": ("yellow accents", "#F4D020"),
        "hazard": ("hazard and ID panels", "#F0E048"), "stencil": ("hazard and ID panels", "#F0E048"),
        "label": ("hazard and ID panels", "#F0E048"), "gauge": ("brass", "#C8A050"),
        "needle": ("brass", "#C8A050"), "glass": ("glass", "#A0E0F0"), "pane": ("glass", "#A0E0F0"),
        "lamp": ("red accents", "#E02818"), "oil": ("oil stains", "#FF00FF"),
    })
    glass = bpy.data.materials.new("glass_r7")
    glass.use_nodes = True
    gb = glass.node_tree.nodes["Principled BSDF"]
    gb.inputs["Base Color"].default_value = rig.srgb("#18222C")
    gb.inputs["Roughness"].default_value = 0.08
    gb.inputs["Alpha"].default_value = 0.2      # round 7: a film, not refraction (round 6's fireflies)
    gb.inputs["Coat Weight"].default_value = 0.4
    M["glass"] = glass                 # round 7's film glass: no longer on any window (kept for reference)
    M["tube_glass"] = R.glass("tube_glass")            # radiant.py: round the tube emitters
    pane = bpy.data.materials.new("pane_r7")       # its name left free for radiant.py's pane
    pane.use_nodes = True
    pb = pane.node_tree.nodes["Principled BSDF"]
    pb.inputs["Base Color"].default_value = rig.srgb("#10161C")
    pb.inputs["Roughness"].default_value = 0.05
    pb.inputs["Alpha"].default_value = 0.22
    pb.inputs["Specular IOR Level"].default_value = 0.4
    M["pane_r7"] = pane                # round 7's pane, replaced by radiant.py's over the port and the slot
    M["pane"] = R.glass("pane", pane=True)
    # round 7: the glass's thin highlight (a reflection, the same lit or idle) and the
    # silhouettes inside the light (plates and cells, backlit: dark, a dull rim on top)
    gl = bpy.data.materials.new("glint")
    gl.use_nodes = True
    glb = gl.node_tree.nodes["Principled BSDF"]
    glb.inputs["Base Color"].default_value = rig.srgb("#DCE6EE")
    glb.inputs["Roughness"].default_value = 0.2
    glb.inputs["Emission Color"].default_value = rig.srgb("#D4E2F2")
    glb.inputs["Emission Strength"].default_value = 0.3
    M["glint"] = gl
    M["sil"] = layered("sil", "#2A1F18", metal="#6A4A34", paint_metal=0.6, paint_rough=0.45, wear=0.3,
                       rust=0.0, dust=0.1, grime=0.6)
    M["bezel"] = layered("bezel", "#16130F", metal="#4A443C", paint_metal=0.3, paint_rough=0.6, wear=0.15,
                         rust=0.0, dust=0.1, grime=0.3)
    COLOURS.update({"glint": ("glass", "#A0E0F0"), "sil": ("copper (bus, coils)", "#E07838"),
                  "bezel": ("dark steel", "#3A3634")})
    lamp = bpy.data.materials.new("lamp")
    lamp.use_nodes = True
    lb = lamp.node_tree.nodes["Principled BSDF"]
    lb.inputs["Base Color"].default_value = rig.srgb("#203020")
    lb.inputs["Emission Color"].default_value = rig.srgb("#40FF60")
    lb.inputs["Emission Strength"].default_value = 3.0
    M["lamp"] = lamp
    LAMPS.append(lb.inputs["Emission Strength"])
    LAMP_B.append(lb)
    _oil_material()


LAMPS = []
LAMP_B = []


def lamp_cut(on):
    """The status lamps' lenses as the light pass wants them: lit white for the engine to tint;
    else the plate's dark green glass (spec 7: the lamps light while working)."""
    for lb in LAMP_B:
        lb.inputs["Emission Color"].default_value = (1, 1, 1, 1) if on else rig.srgb("#40FF60")
        lb.inputs["Emission Strength"].default_value = 1.0 if on else 0.0
        lb.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1) if on else rig.srgb("#203020")


def glint(on):
    """The glass's thin highlight is a faint emitter (round 7): off in a glow pass, which must
    carry the isotope's light alone."""
    b = M["glint"].node_tree.nodes["Principled BSDF"]
    b.inputs["Emission Strength"].default_value = 0.3 if on else 0.0


# ---------------------------------------------------------------- geometry
OBJS = []
ANIM = []
PARENT = []            # the parent stack (the wreck builds inside tilted frames); empty: ROOT
LAYER = {}             # pivot name -> the layer it moves in (spec 7)
GROUP = {}             # object name -> "machine" or "wreck"
CUR = ["machine"]
LABELS = []
STAINS = []
FLOOR = set()          # the deck's slabs and their grating bars (the collide check's: units stand on them)
UNIT = {}              # object name -> the top-level kit call that built it (the collide check's units)
RUN_ENDS = {}          # a hose's, pipe's, lagged run's, trunk's or bundle's unit -> its two end points
_UNIT = [None]
_NEXT_UNIT = [0]


def unit(fn):
    """Every part a top-level kit call builds is one unit (nested calls stay in their caller's)."""
    def wrapped(*a, **k):
        if _UNIT[0] is not None:
            return fn(*a, **k)
        _NEXT_UNIT[0] += 1
        _UNIT[0] = _NEXT_UNIT[0]
        try:
            out = fn(*a, **k)
            if fn.__name__ in ("hose", "pipe", "lagged", "trunk", "bundle", "tray"):
                pts = list(k.get("lead_in") or ()) + list(a[0]) + list(k.get("lead_out") or ())
                RUN_ENDS[_UNIT[0]] = (Vector(pts[0]), Vector(pts[-1]))
            return out
        finally:
            _UNIT[0] = None
    wrapped.__name__ = fn.__name__
    return wrapped


def _finish(o, mat, bevel=0.012, smooth=False, parent=None):
    o.data.materials.append(M[mat])
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments, mod.limit_method = bevel, 2, "ANGLE"
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    o.parent = parent or (PARENT[-1] if PARENT else ROOT)
    if mat in LIQUIDS:
        # radiant.py reads a window's shape in its object's own coordinates, centred on it; box()
        # applies its location into the mesh (transform_apply's default), so the slot's floor read
        # 0.75-1.75 and its light was 0 everywhere: re-centre the mesh on the object
        vs = [v.co for v in o.data.vertices]
        c = Vector([(min(v[i] for v in vs) + max(v[i] for v in vs)) / 2 for i in range(3)])
        if c.length > 1e-6:
            from mathutils import Matrix
            o.data.transform(Matrix.Translation(-c))
            o.location = o.location + c
        R.lit(o)                       # radiant.py: its light spills on the rims round it (rim_spill)
    GROUP[o.name] = CUR[-1]
    UNIT[o.name] = _UNIT[0] if _UNIT[0] is not None else -len(OBJS)
    OBJS.append(o)
    return o


def box(loc, size, mat, rz=0.0, rot=None, bevel=0.012, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot or (0, 0, rz))
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, bevel, parent=parent)


def cyl(loc, r, h, mat, rot=(0, 0, 0), verts=48, bevel=0.01, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    return _finish(bpy.context.active_object, mat, bevel, smooth=True, parent=parent)


def cone(loc, r1, r2, h, mat, rot=(0, 0, 0), verts=48, parent=None):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=h, location=loc, rotation=rot)
    return _finish(bpy.context.active_object, mat, 0.008, smooth=True, parent=parent)


def torus(loc, major, minor, mat, rot=(0, 0, 0), seg=48, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, rotation=rot,
                                     major_segments=seg, minor_segments=10)
    return _finish(bpy.context.active_object, mat, 0, smooth=True, parent=parent)


def annulus(loc, r_in, r_out, h, mat, rot=(0, 0, 0), seg=64, parent=None):
    me = bpy.data.meshes.new("annulus")
    bm = bmesh.new()
    rows = []
    for r, z in ((r_out, -h / 2), (r_out, h / 2), (r_in, h / 2), (r_in, -h / 2)):
        rows.append([bm.verts.new((r * math.cos(2 * PI * k / seg), r * math.sin(2 * PI * k / seg), z))
                     for k in range(seg)])
    for i in range(4):
        a_, b_ = rows[i], rows[(i + 1) % 4]
        for k in range(seg):
            j = (k + 1) % seg
            bm.faces.new((a_[k], a_[j], b_[j], b_[k]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("annulus", me)
    sc.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    return _finish(o, mat, 0.006, smooth=True, parent=parent)


def sphere(loc, r, mat, scale=(1, 1, 1), seg=24, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2)
    o = bpy.context.active_object
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, 0, smooth=True, parent=parent)


def head(x, y, z, r, h, mat, up=True, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0), segments=48, ring_count=24)
    o = bpy.context.active_object
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if (v.co.z < -0.01 if up else v.co.z > 0.01)], context="VERTS")
    bm.to_mesh(me)
    bm.free()
    o.scale = (r, r, h)
    o.location = (x, y, z)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _finish(o, mat, 0, smooth=True, parent=parent)


def prism(loc, r, h, mat, n=8, rz=0.0, bevel=0.015, parent=None):
    """An n-sided upright prism: a cast or plated polygonal body, its flats kept flat."""
    o = cyl(loc, r, h, mat, rot=(0, 0, rz), verts=n, bevel=bevel, parent=parent)
    for p in o.data.polygons:
        p.use_smooth = False
    return o


def sector(loc, r_in, r_out, a0, a1, h, mat, rot=(0, 0, 0), seg=8, parent=None):
    """An annular sector plate (a wedge of a wheel) in the local XY plane, h thick."""
    me = bpy.data.meshes.new("sector")
    bm = bmesh.new()
    rows = []
    for r, z in ((r_out, -h / 2), (r_out, h / 2), (r_in, h / 2), (r_in, -h / 2)):
        rows.append([bm.verts.new((r * math.cos(a0 + (a1 - a0) * k / seg), r * math.sin(a0 + (a1 - a0) * k / seg), z))
                     for k in range(seg + 1)])
    for i in range(4):
        a_, b_ = rows[i], rows[(i + 1) % 4]
        for k in range(seg):
            bm.faces.new((a_[k], a_[k + 1], b_[k + 1], b_[k]))
    for k in (0, seg):
        f = [rows[i][k] for i in range(4)]
        bm.faces.new(f if k == seg else list(reversed(f)))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("sector", me)
    sc.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    return _finish(o, mat, 0.004, parent=parent)


def along(t):
    return Vector(t).normalized().to_track_quat("Z", "Y").to_euler()


def catmull(pts, step=0.01):
    P = [Vector(p) for p in pts]
    ext = [2 * P[0] - P[1]] + P + [2 * P[-1] - P[-2]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1:i + 3]
        n = max(2, math.ceil((p2 - p1).length / step))
        for k in range(n):
            t = k / n
            out.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (3 * p1 - p0 - 3 * p2 + p3) * t * t * t))
    out.append(P[-1])
    return out


def frames(P):
    T = [(P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized() for i in range(len(P))]
    up = Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((1, 0, 0))
    N = [T[0].cross(up).normalized()]
    for i in range(1, len(P)):
        n = N[-1] - T[i] * N[-1].dot(T[i])
        N.append(n.normalized() if n.length > 1e-6 else N[-1])
    B = [t.cross(n) for t, n in zip(T, N)]
    return T, N, B


def sweep(P, r, mat, corr=0.0, pitch=0.03, seg=16, parent=None):
    T, N, B = frames(P)
    s = [0.0]
    for a_, b_ in zip(P, P[1:]):
        s.append(s[-1] + (b_ - a_).length)
    me = bpy.data.meshes.new("sweep")
    bm = bmesh.new()
    rings = []
    for i, p in enumerate(P):
        rr = r * (1 + corr * (0.5 + 0.5 * math.cos(2 * PI * s[i] / pitch)))
        rings.append([bm.verts.new(p + rr * (math.cos(2 * PI * k / seg) * N[i]
                                             + math.sin(2 * PI * k / seg) * B[i])) for k in range(seg)])
    for a_, b_ in zip(rings, rings[1:]):
        for k in range(seg):
            j = (k + 1) % seg
            bm.faces.new((a_[k], a_[j], b_[j], b_[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("sweep", me)
    sc.collection.objects.link(o)
    return _finish(o, mat, 0, smooth=True, parent=parent), P, T, s


def hose(pts, r=0.085, mat="hose"):
    P = catmull(pts)
    sweep(P, r, mat, corr=0.055, pitch=0.095, seg=18)
    for p, q in ((P[0], P[1]), (P[-1], P[-2])):
        t = (p - q).normalized()
        cyl(tuple(p - t * 0.05), r * 1.3, 0.11, "bare", rot=along(t), verts=20, bevel=0.006)
        torus(tuple(p - t * 0.09), r * 1.3, 0.010, "bare", rot=along(t), seg=20)
        cyl(tuple(p + t * 0.005), r * 1.6, 0.04, "brass", rot=along(t), verts=6, bevel=0.0)
    return P


def mark(P, frac, mat, r, w=0.035):
    i = max(1, min(len(P) - 2, int(frac * (len(P) - 1))))
    t = (P[i + 1] - P[i - 1]).normalized()
    cyl(tuple(P[i]), r + 0.008, w, mat, rot=along(t), verts=24, bevel=0.003)


def lagged(pts, r=0.11, bands=0.22, marks=()):
    P = catmull(pts)
    for f, m in marks:
        mark(P, f, m, r, 0.05)
    _, P, T, s = sweep(P, r, "lag", seg=20)
    nxt = bands / 2
    for i, p in enumerate(P):
        if s[i] >= nxt and s[i] < s[-1] - 0.05:
            torus(tuple(p), r + 0.004, 0.009, "bare", rot=along(T[i]), seg=24)
            nxt += bands
    for p, t in ((P[0], T[0]), (P[-1], T[-1])):
        cyl(tuple(p), r * 1.25, 0.04, "bare", rot=along(t), verts=24, bevel=0.005)
    return P


def pipe(pts, r=0.06, mat="bare", marks=(), flanges=True):
    P = catmull(pts)
    _, P, T, s = sweep(P, r, mat, seg=16)
    for f, m in marks:
        mark(P, f, m, r)
    if flanges:
        for p, t in ((P[0], T[0]), (P[-1], T[-1])):
            cyl(tuple(p), r * 1.4, 0.03, "dark_steel", rot=along(t), verts=16, bevel=0.004)
    return P


def gland(p, t, r_b):
    """A cable gland where a bundle of overall radius r_b enters its host at p, the bundle arriving
    along t (unit, pointing into the host): a brass hex body standing out of the host's face and a
    dark lock-nut ring on it (T08d: every cable end visibly fastened)."""
    rg = r_b * 1.1 + 0.004
    cyl(tuple(p - t * 0.028), rg, 0.05, "brass", rot=along(t), verts=6, bevel=0.003)
    cyl(tuple(p - t * 0.004), rg * 1.15, 0.012, "dark_steel", rot=along(t), verts=16, bevel=0.002)
    cyl(tuple(p - t * 0.058), rg * 0.85, 0.016, "bare", rot=along(t), verts=12, bevel=0.002)


def bundle(pts, cols=("red", "grey", "yellow", "black"), r=0.014, glands=(False, False), sleeve_ok=None):
    """Cables twisted along pts. glands (start, end): a gland where that end enters its host, the
    end point on the host's face and the run arriving square to it (T08d); the cables go on 0.02
    into the host, so no gap shows round the gland. sleeve_ok(p): False where no label sleeve may
    sit (T08i: in a tray, where its cleats hold the cables and a sleeve would stand through the floor)."""
    P = catmull(pts)
    for k_, on in enumerate(glands):
        if on:
            a_, b_ = (P[0], P[1]) if k_ == 0 else (P[-1], P[-2])
            t = (a_ - b_).normalized()
            if k_ == 0:
                P.insert(0, a_ + t * 0.02)
            else:
                P.append(a_ + t * 0.02)
    T, N, B = frames(P)
    s = [0.0]
    for a_, b_ in zip(P, P[1:]):
        s.append(s[-1] + (b_ - a_).length)
    n = len(cols)
    for k, c in enumerate(cols):
        off = [r * 1.3 * (math.cos(2 * PI * k / n + 9 * s[i]) * N[i]
                          + math.sin(2 * PI * k / n + 9 * s[i]) * B[i]) for i in range(len(P))]
        sweep([p + o for p, o in zip(P, off)], r, "cable_" + c, seg=8)
    nxt = 0.2
    for i, p in enumerate(P):
        if s[i] >= nxt and s[i] < s[-1] - 0.1:
            if sleeve_ok is None or sleeve_ok(p):       # one skipped keeps its place in the 0.4 rhythm
                cyl(tuple(p), r * 2.9, 0.045, "label", rot=along(T[i]), verts=12, bevel=0.002)
            nxt += 0.4
    rb = r * 1.3 + r
    for k_, on in enumerate(glands):
        if on:
            i, j = (1, 2) if k_ == 0 else (len(P) - 2, len(P) - 3)
            gland(P[i], (P[i] - P[j]).normalized(), rb)


def trunk(pts, r=0.07, mat="cable_black"):
    """An armoured power cable: a fat black run with steel cleats, a gland at each end."""
    P = catmull(pts)
    _, P, T, s = sweep(P, r, mat, corr=0.03, pitch=0.05, seg=16)
    nxt = 0.25
    for i, p in enumerate(P):
        if s[i] >= nxt and s[i] < s[-1] - 0.1:
            cyl(tuple(p), r * 1.25, 0.04, "bare", rot=along(T[i]), verts=16, bevel=0.003)
            nxt += 0.35
    for p, t in ((P[0], T[0]), (P[-1], T[-1])):
        cyl(tuple(p), r * 1.5, 0.08, "brass", rot=along(t), verts=6, bevel=0.004)
    return P


def bolts(cx, cy, z, R, n, r=0.022, mat="bolt", parent=None):
    for i in range(n):
        a = 2 * PI * i / n
        cyl((cx + R * math.cos(a), cy + R * math.sin(a), z), r, 0.025, mat, verts=6, bevel=0, parent=parent)


def band(x, y, z, r, h=0.07, mat="dark_steel", lugs=2, lug_a=-PI / 2):
    cyl((x, y, z), r + 0.025, h, mat, verts=64)
    for i in range(lugs):
        a = lug_a + 2 * PI * i / lugs
        box((x + (r + 0.05) * math.cos(a), y + (r + 0.05) * math.sin(a), z), (0.06, 0.06, h + 0.05),
            "dark_steel", rz=a, bevel=0.006)


def flange_ring(x, y, z, r, mat="dark_steel", h=0.06, nb=16):
    cyl((x, y, z), r + 0.045, h, mat, verts=64)
    bolts(x, y, z + h / 2 + 0.008, r + 0.03, nb, r=0.016)


def rivet_ring(cx, cy, z, r, n, mat="bolt", rr=0.019):
    for i in range(n):
        a = 2 * PI * (i + 0.5) / n
        sphere((cx + r * math.cos(a), cy + r * math.sin(a), z), rr, mat, scale=(1, 1, 0.8), seg=8)


def vessel_band(cx, cy, z, r, n_rivets=16, lugs=3, lug_a=-PI / 2):
    band(cx, cy, z, r, h=0.075, mat="bare", lugs=lugs, lug_a=lug_a)
    rivet_ring(cx, cy, z, r + 0.032, n_rivets)


def weld_ring(cx, cy, z, r):
    torus((cx, cy, z), r + 0.004, 0.011, "seam", seg=72)


def gauge(loc, facing, r=0.07, live=None, layer=None):
    """A brass-cased gauge, cream face, red needle. live(t) -> needle angle offset, or None."""
    t = Vector(facing).normalized()
    cyl(loc, r, 0.03, "brass", rot=along(t), verts=24, bevel=0.004)
    cyl(tuple(Vector(loc) + t * 0.017), r * 0.8, 0.006, "gauge", rot=along(t), verts=24, bevel=0)
    piv = pivot(tuple(Vector(loc) + t * 0.022), along(t), layer=layer)
    box((r * 0.35, 0, 0), (r * 0.8, 0.012, 0.006), "needle", bevel=0, parent=piv)
    base = piv.rotation_euler.copy()

    def pose(tt, on):
        piv.rotation_euler = base
        a = 0.9 + (live(tt) if (live and on) else 0.0) if on else -0.9
        piv.rotation_euler.rotate_axis("Z", a)
    ANIM.append(pose)


def handwheel(loc, r=0.09, axis=(0, 0, 1), mat="red"):
    t = Vector(axis).normalized()
    torus(loc, r, 0.016, mat, rot=along(t), seg=24)
    for k in range(3):
        a = 2 * PI * k / 3
        o = t.to_track_quat("Z", "Y") @ Vector((math.cos(a), math.sin(a), 0))
        cyl(tuple(Vector(loc) + o * r / 2), 0.008, r, mat, rot=along(o), verts=6, bevel=0)
    cyl(loc, 0.022, 0.05, "bare", rot=along(t), verts=12)


def pivot(loc, rot=(0, 0, 0), parent=None, layer=None):
    """An empty to build parts under; `layer`, when it moves, the layer of spec 7 it is in."""
    e = bpy.data.objects.new("pivot", None)
    sc.collection.objects.link(e)
    e.parent = parent or (PARENT[-1] if PARENT else ROOT)
    if layer:
        LAYER[e.name] = layer
    e.location = loc
    e.rotation_euler = rot
    return e


def spin(piv, turns_per_loop, axis="Z", ease=None):
    """Turn a pivot about its own axis: turns_per_loop whole turns (or a fraction that
    lands on a symmetric pose) each loop; ease(t) -> progress in [0, 1) for indexing."""
    base = piv.rotation_euler.copy()

    def pose(t, on):
        piv.rotation_euler = base
        u = (ease(t) if ease else t) if on else 0.0
        piv.rotation_euler.rotate_axis(axis, 2 * PI * turns_per_loop * u)
    ANIM.append(pose)


def coupling(x, y, z, r, axis=(0, 0, 1), mat="brass", turns=1.0, ease=None, layer=None):
    """A six-lobed spider coupling with a hazard stripe, turning `turns` a loop (whole or half turns)."""
    root = pivot((x, y, z), along(axis), layer=layer)
    cyl((0, 0, 0), r * 0.55, 0.09, "dark_steel", verts=24, parent=root)
    for i in range(6):
        a = 2 * PI * i / 6
        box((r * 0.7 * math.cos(a), r * 0.7 * math.sin(a), 0), (r * 0.5, r * 0.32, 0.075), mat, rz=a, bevel=0.006,
            parent=root)
    box((0, 0, 0.047), (r * 0.25, r * 1.5, 0.012), "hazard", bevel=0, parent=root)
    spin(root, turns, ease=ease)
    return root


def valve(x, y, z=0.0, h=0.42, r=0.07, wheel="red"):
    cyl((x, y, z + 0.1), r * 1.3, 0.2, "dark_steel", verts=20)
    cyl((x, y, z + 0.1 + h * 0.4), r * 0.7, h * 0.5, "bare", verts=16)
    handwheel((x, y, z + h), 0.085, mat=wheel)


def drum_ew(x0, x1, y, z, r, mat="grey", bands=(), saddles=(), band_mat="dark_steel"):
    cyl(((x0 + x1) / 2, y, z), r, x1 - x0, mat, rot=(0, PI / 2, 0), verts=48)
    for xx, s in ((x0, -1), (x1, 1)):
        h = head(xx, y, z, r, 0.13, mat)
        h.rotation_euler = (0, s * PI / 2, 0)
    for xx in bands:
        cyl((xx, y, z), r + 0.025, 0.07, band_mat, rot=(0, PI / 2, 0), verts=48)
    for xx in saddles:
        box((xx, y, (z - r * 0.5) / 2 + 0.02), (0.12, r * 1.6, z - r * 0.5 + 0.04), "dark_steel")


def drum_ns(x, y0, y1, z, r, mat="grey", bands=(), saddles=(), band_mat="dark_steel"):
    cyl((x, (y0 + y1) / 2, z), r, y1 - y0, mat, rot=(PI / 2, 0, 0), verts=48)
    for yy, s in ((y0, -1), (y1, 1)):
        h = head(x, yy, z, r, 0.13, mat)
        h.rotation_euler = (-s * PI / 2, 0, 0)
    for yy in bands:
        cyl((x, yy, z), r + 0.025, 0.07, band_mat, rot=(PI / 2, 0, 0), verts=48)
    for yy in saddles:
        box((x, yy, (z - r * 0.5) / 2 + 0.02), (r * 1.6, 0.12, z - r * 0.5 + 0.04), "dark_steel")


def vtank(x, y, r, h, mat="grey", bands=(), top="dark_steel", nozzle=(0.3, 0.0), band_mat="dark_steel"):
    cyl((x, y, 0.07), r + 0.08, 0.14, "dark_steel", verts=64)
    cyl((x, y, h / 2 + 0.07), r, h - 0.14, mat, verts=64)
    for z in bands:
        band(x, y, z, r, mat=band_mat)
    hh = min(0.24, r * 0.38)
    head(x, y, h, r, hh, top)
    if nozzle:
        nx, ny = x + nozzle[0] * r, y + nozzle[1] * r
        cyl((nx, ny, h + hh * 0.7 + 0.06), 0.085, 0.16, "bare", verts=24)
        flange_ring(nx, ny, h + hh * 0.7 + 0.14, 0.08, mat="bare", h=0.035, nb=8)
    return h + hh


def ladder(x, y, z0, z1, axis="y", mat="ochre"):
    for z in [z0 + 0.3 * i for i in range(int((z1 - z0) / 0.3) + 1)]:
        box((x, y, z), (0.04, 0.16, 0.025) if axis == "y" else (0.16, 0.04, 0.025), mat, bevel=0.004)
    for s in (-1, 1):
        o = (0, s * 0.08) if axis == "y" else (s * 0.08, 0)
        box((x + o[0], y + o[1], (z0 + z1) / 2), (0.025, 0.025, z1 - z0), mat, bevel=0.003)


def skid(x0, y0, x1, y1, h, mat="dark_steel"):
    box(((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0, y1 - y0, h), mat, bevel=0.012)
    for xx in (x0 + 0.06, x1 - 0.06):
        for yy in (y0 + 0.06, y1 - 0.06):
            cyl((xx, yy, h + 0.008), 0.022, 0.02, "bare", verts=6, bevel=0)


def status_lamp(x, y, z):
    cyl((x, y, z), 0.045, 0.05, "dark_steel", verts=16)
    sphere((x, y, z + 0.035), 0.032, "lamp", seg=12)


def motor(x, y, z, d=(1, 0), s=1.0, mat="green"):
    """A drive motor along d: a ribbed body, a terminal box, feet. Returns its shaft end."""
    dx, dy = d
    L, R = 0.42 * s, 0.17 * s
    box((x, y, z - R * 0.85), (L * 0.8 if dx else R * 1.8, R * 1.8 if dx else L * 0.8, 0.06), "dark_steel")
    cyl((x, y, z), R, L, mat, rot=along((dx, dy, 0)), verts=32)
    for k in range(5):
        o = -L * 0.35 + L * 0.7 * k / 4
        torus((x + dx * o, y + dy * o, z), R + 0.004, 0.012, mat, rot=along((dx, dy, 0)), seg=32)
    box((x - dy * 0.0, y + dx * 0.0, z + R + 0.04), (0.13 * s, 0.11 * s, 0.08), mat, bevel=0.008)
    cyl((x - dx * L * 0.5, y - dy * L * 0.5, z), R * 0.8, 0.04, "dark_steel", rot=along((dx, dy, 0)), verts=24)
    return (x + dx * L * 0.5, y + dy * L * 0.5, z)


def jbox(x, y, w=0.32, d=0.22, h=0.4, mat="grey", z=0.0):
    box((x, y, z + h / 2), (w, d, h), mat, bevel=0.01)
    box((x, y - d / 2 - 0.01, z + h * 0.55), (w * 0.7, 0.02, h * 0.6), "dark_steel", bevel=0.004)
    cyl((x + w * 0.3, y, z + h + 0.04), 0.03, 0.08, "bare", verts=8)


def cabinet(x, y, w, d, h, mat="grey", lamp=True):
    box((x, y, h / 2), (w, d, h), mat, bevel=0.015)
    for i in range(4):
        box((x - w * 0.15, y - d / 2 - 0.01, h * 0.35 + 0.07 * i), (w * 0.45, 0.02, 0.025), "dark_steel", bevel=0)
    if lamp:
        status_lamp(x + w * 0.25, y - d * 0.2, h + 0.02)


def stencil(loc, size, rz=0.0):
    box(loc, size, "stencil", rz=rz, bevel=0.002)


def flat_plate(loc, w, h, face="S", mat="bare", bolts_=True):
    x, y, z = loc
    if face == "S":
        box((x, y - 0.006, z), (w, 0.012, h), mat, bevel=0.003)
        if bolts_:
            for sx_ in (-1, 1):
                for sz_ in (-1, 1):
                    cyl((x + sx_ * (w / 2 - 0.025), y - 0.014, z + sz_ * (h / 2 - 0.025)), 0.012, 0.012, "bolt",
                        rot=(PI / 2, 0, 0), verts=6, bevel=0)
    else:
        box((x, y, z + 0.006), (w, h, 0.012), mat, bevel=0.003)
        if bolts_:
            for sx_ in (-1, 1):
                for sy_ in (-1, 1):
                    cyl((x + sx_ * (w / 2 - 0.025), y + sy_ * (h / 2 - 0.025), z + 0.014), 0.012, 0.012, "bolt",
                        verts=6, bevel=0)


def id_panel(loc, w, h, stripe="red", face="S"):
    x, y, z = loc
    flat_plate(loc, w, h, face, "stencil")
    if face == "S":
        box((x, y - 0.014, z + h * 0.15), (w * 0.92, 0.006, h * 0.28), stripe, bevel=0)
    else:
        box((x, y + h * 0.15, z + 0.014), (w * 0.92, h * 0.28, 0.006), stripe, bevel=0)


def hazard_tag(loc, w, h, face="S"):
    x, y, z = loc
    if face == "S":
        box((x, y - 0.007, z), (w, 0.014, h), "hazard", bevel=0.002)
    else:
        box((x, y, z + 0.007), (w, h, 0.014), "hazard", bevel=0.002)


def manway_top(x, y, z, r=0.13, nb=10):
    cyl((x, y, z + 0.015), r, 0.03, "bare", verts=32, bevel=0.004)
    bolts(x, y, z + 0.035, r - 0.025, nb, r=0.012)
    torus((x, y, z + 0.05), 0.04, 0.008, "yellow", rot=(PI / 2, 0, 0), seg=16)


def radiator(x0, x1, y, z0, z1, mat="grey", tube="copper", fins=14, face=(0, -1)):
    """A vacuum radiator panel standing E-W: a framed dark-steel sheet with a copper
    serpentine and fin ribs. Radiation is the only way heat leaves here; no fans."""
    w, h = x1 - x0, z1 - z0
    box(((x0 + x1) / 2, y, (z0 + z1) / 2), (w, 0.05, h), "dark_steel", bevel=0.006)
    for k in range(fins + 1):
        xx = x0 + w * k / fins
        box((xx, y - 0.035, (z0 + z1) / 2), (0.022, 0.03, h - 0.02), mat, bevel=0.004)
    for zz in (z0 + 0.02, z1 - 0.02):
        box(((x0 + x1) / 2, y - 0.02, zz), (w + 0.04, 0.08, 0.05), mat, bevel=0.008)
    for zz in (z0 + 0.12 + (h - 0.24) * i / 3 for i in range(4)):
        cyl(((x0 + x1) / 2, y - 0.06, zz), 0.022, w - 0.04, tube, rot=(0, PI / 2, 0), verts=12, bevel=0)


def label(n, text, pos):
    LABELS.append(dict(n=n, text=text, world=list(pos),
                       px=[CENTRE[0] + 64 * pos[0], CENTRE[1] - 64 * (pos[1] + pos[2] / 2)]))


OIL = None


def _oil_material():
    global OIL
    OIL = bpy.data.materials.new("oil")
    OIL.use_nodes = True
    M["oil"] = OIL
    nt = OIL.node_tree
    g = _G(OIL)
    out = nt.nodes["Material Output"]
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#1C140C")
    b.inputs["Roughness"].default_value = 0.3
    tc = g.node("ShaderNodeTexCoord").outputs["Generated"]
    sep = g.node("ShaderNodeSeparateXYZ", Vector=tc)
    dx = g.math("SUBTRACT", sep.outputs["X"], 0.5)
    dy = g.math("SUBTRACT", sep.outputs["Y"], 0.5)
    rr = g.math("SQRT", g.math("ADD", g.math("MULTIPLY", dx, dx), g.math("MULTIPLY", dy, dy)))
    fall = g.remap(rr, 0.5, 0.15)
    pos = g.node("ShaderNodeNewGeometry").outputs["Position"]
    blot = g.remap(g.noise(pos, 6, detail=5, rough=0.6, distortion=0.5), 0.42, 0.62)
    alpha = g.math("MULTIPLY", g.math("MULTIPLY", fall, blot), 0.8, clamp=True)
    alpha = g.math("MINIMUM", alpha, 0.45)
    tr = g.node("ShaderNodeBsdfTransparent")
    mix = g.node("ShaderNodeMixShader", Fac=alpha)
    g.l.new(tr.outputs[0], mix.inputs[1])
    g.l.new(b.outputs[0], mix.inputs[2])
    g.l.new(mix.outputs[0], out.inputs["Surface"])


def stain(x, y, rx, ry, rz=0.0):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, 0.004), rotation=(0, 0, rz))
    o = bpy.context.active_object
    o.scale = (rx * 2, ry * 2, 1)
    bpy.ops.object.transform_apply(scale=True)
    o.visible_shadow = False
    STAINS.append(o)
    return _finish(o, "oil", 0)


def ease_index(t, hold=0.45):
    """An indexing move: still for `hold` of the loop, then a smooth step through one index."""
    if t < hold:
        return 0.0
    u = (t - hold) / (1 - hold)
    return u * u * (3 - 2 * u)


def pose(t, on=True):
    """Every moving part at t (0..1 through the loop). The light is posed apart (pose_light)."""
    for p in ANIM:
        p(t, on)


# ================================================================ round 6: the combined machine
def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def ramp(t, a, b):
    return smooth((t - a) / (b - a))


MOVE = (0.34, 0.62)                 # the carousel's index, inside the crane's run to the crucible
LID = (0.47, 0.83)                  # the served well's lid off


def index_u(t, on=True):
    return ramp(t, *MOVE) if on else 0.0


def crane_state(t):
    """The twin hoist's timeline: (bridge key, drop A, drop B, A carries fresh, B carries spent).
    The bridge key is 'P+' (A over the pick), 'P-' (B over the pick), 'W-' (B over the well),
    'W+' (A over the well), or a blend (key0, key1, u)."""
    if t < 0.12:
        b = ("P+", "P+", 0.0)
    elif t < 0.18:
        b = ("P+", "P-", ramp(t, 0.12, 0.18))
    elif t < 0.30:
        b = ("P-", "P-", 0.0)
    elif t < 0.50:
        b = ("P-", "W-", ramp(t, 0.30, 0.50))
    elif t < 0.62:
        b = ("W-", "W-", 0.0)
    elif t < 0.68:
        b = ("W-", "W+", ramp(t, 0.62, 0.68))
    elif t < 0.80:
        b = ("W+", "W+", 0.0)
    else:
        b = ("W+", "P+", ramp(t, 0.80, 1.0))

    def tri(a, m, c):
        return ramp(t, a, m) if t < m else 1.0 - ramp(t, m, c)
    dA = tri(0.0, 0.06, 0.12) if t < 0.12 else (tri(0.68, 0.74, 0.80) if 0.68 <= t < 0.80 else 0.0)
    dB = tri(0.18, 0.24, 0.30) if 0.18 <= t < 0.30 else (tri(0.50, 0.56, 0.62) if 0.50 <= t < 0.62 else 0.0)
    carryA = 0.06 <= t < 0.74
    carryB = t < 0.24 or t >= 0.56
    return b, dA, dB, carryA, carryB


def pick_content(t):
    """What the pick pocket holds while the crane works it (before the index)."""
    if t < 0.06:
        return "fresh"
    if t < 0.24:
        return "empty"
    return "spent"


def lid_open(t, on=True):
    if not on:
        return 0.0
    return ramp(t, LID[0], LID[0] + 0.05) * (1.0 - ramp(t, LID[1] - 0.05, LID[1]))


def cell(loc, fresh=True, parent=None, r=0.085, h=0.3):
    """A radiant cell in its lead can: fresh (new lead, a yellow band, a bright cap) or spent
    (bloomed lead, a dark band). Returns its objects."""
    x, y, z = loc
    n0 = len(OBJS)
    cyl((x, y, z), r, h, "lead_new" if fresh else "lead", verts=20, parent=parent)
    torus((x, y, z + h * 0.18), r + 0.003, 0.012, "yellow" if fresh else "dark", seg=20, parent=parent)
    cyl((x, y, z + h / 2 + 0.015), r * 1.08, 0.03, "bare" if fresh else "dark_steel", verts=20, parent=parent)
    torus((x, y, z + h / 2 + 0.05), 0.026, 0.008, "dark_steel", rot=(PI / 2, 0, 0), seg=10, parent=parent)
    return OBJS[n0:]


def floor(notches=(), seed=6, x0=-2.47, x1=2.47, n=10):
    """The building's floor, edge to edge: bolted deck slabs of differing height (a raft of
    skids, not one plinth), grating and chequer plates among them; the notches (x0, y0, x1, y1)
    are left out, and they break the outline."""
    rnd = random.Random(seed)
    w = (x1 - x0) / n
    for i in range(n):
        for j in range(n):
            cx, cy = x0 + w * (i + 0.5), x0 + w * (j + 0.5)
            if any(a <= cx <= c and b <= cy <= d for a, b, c, d in notches):
                continue
            h = rnd.choice((0.07, 0.09, 0.11, 0.13))
            mat = rnd.choice(("dark_steel", "dark_steel", "dark_steel", "grey", "bare"))
            FLOOR.add(box((cx, cy, h / 2), (w - 0.012, w - 0.012, h), mat, bevel=0.01).name)
            if mat == "bare":
                for k in range(5):
                    FLOOR.add(box((cx, cy - w * 0.4 + w * 0.2 * k, h + 0.004), (w * 0.86, 0.018, 0.008), "dark_steel",
                                  bevel=0).name)
            elif rnd.random() < 0.6:
                for sx in (-1, 1):
                    for sy in (-1, 1):
                        FLOOR.add(cyl((cx + sx * (w / 2 - 0.05), cy + sy * (w / 2 - 0.05), h + 0.005), 0.014, 0.012,
                                      "bolt", verts=6, bevel=0).name)


def housing(x0, y0, x1, y1, h, mat="grey", roof="teal", seams=0.45, louvres=False, dress=True):
    """A heavy steel housing: the body in its unit's paint, plate seams with rivet lines, a
    lipped roof in the family's teal, lifting eyes."""
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    box((xm, ym, h / 2), (x1 - x0, y1 - y0, h), mat, bevel=0.02)
    box((xm, ym, h + 0.03), (x1 - x0 + 0.06, y1 - y0 + 0.06, 0.06), roof, bevel=0.012)
    box((xm, ym, h + 0.075), (x1 - x0 - 0.12, y1 - y0 - 0.12, 0.03), roof, bevel=0.008)
    nx = max(1, int((x1 - x0) / seams))
    for k in range(1, nx):
        xx = x0 + (x1 - x0) * k / nx
        box((xx, y0 - 0.008, h / 2), (0.035, 0.02, h - 0.04), "dark_steel", bevel=0.003)
        for z in [0.08 + 0.1 * i for i in range(int((h - 0.12) / 0.1))]:
            sphere((xx + 0.035, y0 - 0.012, z), 0.011, "bolt", scale=(1, 0.7, 1), seg=6)
    if not dress:
        return            # FIX 6: a crane rail runs on this roof; its eyes, hatch, vents and conduit stood in the bridge's way
    for xx in (x0 + 0.12, x1 - 0.12):
        torus((xx, ym, h + 0.11), 0.035, 0.009, "yellow", rot=(PI / 2, 0, 0), seg=12)
    # roof dressing: a bolted hatch, vent boxes, a conduit along the roof
    w_, d_ = x1 - x0, y1 - y0
    if w_ > 0.6 and d_ > 0.6:
        manway_top(x0 + w_ * 0.3, y0 + d_ * 0.62, h + 0.09, r=0.12, nb=8)
        for k, fx in enumerate((0.62, 0.8)):
            box((x0 + w_ * fx, y0 + d_ * 0.35, h + 0.16), (0.18, 0.22, 0.14), "grey", bevel=0.01)
            for j in range(3):
                box((x0 + w_ * fx, y0 + d_ * 0.35 - 0.112, h + 0.12 + 0.035 * j), (0.15, 0.012, 0.018), "dark_steel",
                    bevel=0)
        pipe([(x0 + 0.08, y0 + d_ * 0.2, h + 0.15), (x1 - 0.08, y0 + d_ * 0.2, h + 0.15)], r=0.03, mat="bare",
             marks=((0.4, "yellow"),))
    elif w_ > 1.0:
        pipe([(x0 + 0.08, ym, h + 0.15), (x1 - 0.08, ym, h + 0.15)], r=0.03, mat="bare", marks=((0.3, "yellow"),))
        for k in range(int(w_ / 0.8)):
            box((x0 + 0.4 + 0.8 * k, ym - 0.06, h + 0.14), (0.16, 0.1, 0.1), "grey", bevel=0.008)
    if louvres:
        for k in range(4):
            box((xm, y0 - 0.012, h * 0.45 + 0.07 * k), ((x1 - x0) * 0.45, 0.025, 0.03), "dark_steel", bevel=0.003,
                rot=(0.5, 0, 0))


def strap(c, X, Y, Z, path, width, thick, mat):
    """A flat steel band: its mid-line path [(v, u), ...] in the plane through c spanned by Y (v) and
    Z (u), the band width along X and thick across the path (T08i: a tray's cleat)."""
    me = bpy.data.meshes.new("strap")
    bm = bmesh.new()
    n_ = len(path)
    rings = []
    for i, (v, u) in enumerate(path):
        a_, b_ = path[max(i - 1, 0)], path[min(i + 1, n_ - 1)]
        tv, tu = b_[0] - a_[0], b_[1] - a_[1]
        ln = math.hypot(tv, tu) or 1.0
        nv, nu = -tu / ln, tv / ln                 # the path's normal in the (v, u) plane
        ring = []
        for sx, sn in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            q = c + X * (sx * width / 2) + Y * (v + sn * nv * thick / 2) + Z * (u + sn * nu * thick / 2)
            ring.append(bm.verts.new(q))
        rings.append(ring)
    for a_, b_ in zip(rings, rings[1:]):
        for k in range(4):
            j = (k + 1) % 4
            bm.faces.new((a_[k], a_[j], b_[j], b_[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("strap", me)
    sc.collection.objects.link(o)
    return _finish(o, mat, 0)


TRAY_HC = 0.06          # the cables' centre over a tray's floor line
TRAY_FLOOR = 0.0125     # the floor's top over its line
TRAY_FRAME = set()      # a tray's floor, rails and cleats: the collide check holds its own cables off them (T08i)


def tray(pts, w=0.2, cols=("black", "red", "grey"), lead_in=None, lead_out=None, legs=(), cleat_step=0.45):
    """A cable tray in straight runs between points (the floor's centre line), cables laid on its
    floor. T08d: each run's floor and rails pitched along it, so a sloping run's cables lie in it
    instead of passing through it (round 7's boxes stayed level); the cables' centre TRAY_HC over the
    floor line (the floor's top 0.0125, the bundle 0.046 round its line). lead_in / lead_out: the
    points the cables come from before the tray and go on to after it, each ending in a gland on
    its host (bundle()). legs: x positions along the tray (the run there) of a stand from the deck
    to the floor.
    T08i (Liam 2026-10-21, "it still doesn't look like it should be like that"): T08d's clamp was a
    flat bar across the tray's top on two posts, and the cables ran under it, so from above they read
    as passing through a rung, with the label sleeves standing inside it. As vanilla's cables are
    held (the substation's leads clipped along its frame, the accumulator's draped over its cans):
    the tray is open, top and ends, the cables lie on its floor and leave over its open ends, and
    each cleat is a band that wraps over the bundle and is bolted to the floor either side of it, 0.08
    in from each end of every straight run (none on a bend, where the bundle rounds the corner) and at
    most cleat_step apart between; the cables follow the floor's line through points 0.05 apart (round
    7's few far-apart points let the spline bow off it); no label sleeve inside the tray."""
    def frame_of(a, b):
        d = b - a
        rz = math.atan2(d.y, d.x)
        pitch = math.atan2(d.z, math.hypot(d.x, d.y))
        R_ = Matrix.Rotation(rz, 3, "Z") @ Matrix.Rotation(-pitch, 3, "Y")
        return R_, R_.to_euler()
    P_ = [Vector(p) for p in pts]
    for a, b in zip(P_, P_[1:]):
        L = (b - a).length
        mid = (a + b) / 2
        R_, eul = frame_of(a, b)
        X_, Y_, Z_ = R_.col[0], R_.col[1], R_.col[2]
        TRAY_FRAME.add(box(tuple(mid), (L + 0.02, w, 0.025), "dark_steel", rot=eul, bevel=0.004).name)
        for s in (-1, 1):
            TRAY_FRAME.add(box(tuple(mid + Y_ * s * w / 2 + Z_ * 0.035), (L + 0.02, 0.018, 0.07), "ochre", rot=eul,
                               bevel=0.003).name)
    # the cleats: the band's inner face 0.01 clear of the bundle (0.046 round its line), down to the
    # floor's top either side, its feet out to 0.021 short of the rails and a bolt in each
    rb, th = 0.046, 0.006
    rm = rb + 0.01 + th / 2
    fl = TRAY_FLOOR - TRAY_HC + th / 2                    # the feet's mid-line, on the floor (cable axis frame)
    fo = w / 2 - 0.009 - 0.012                            # the feet's outer end, clear of the rails
    arch = [(rm * math.cos(PI - PI * k / 12), rm * math.sin(PI - PI * k / 12)) for k in range(13)]
    path = [(-fo, fl), (-rm - th / 2, fl), (-rm, fl + th / 2)] + arch + [(rm, fl + th / 2), (rm + th / 2, fl), (fo, fl)]
    at = []
    for a, b in zip(P_, P_[1:]):
        L = (b - a).length
        n_in = max(1, math.ceil((L - 0.16) / cleat_step))
        at += [(a, b, (0.08 + (L - 0.16) * k / n_in) / L) for k in range(n_in + 1)] if L > 0.2 else [(a, b, 0.5)]
    for a, b, f_ in at:
        q = a + (b - a) * f_
        R_, _ = frame_of(a, b)
        X_, Y_, Z_ = R_.col[0], R_.col[1], R_.col[2]
        c = q + Z_ * TRAY_HC
        TRAY_FRAME.add(strap(c, X_, Y_, Z_, path, 0.032, th, "ochre").name)
        for s in (-1, 1):
            cyl(tuple(c + Y_ * s * (rm + th / 2 + fo) / 2 + Z_ * (fl + th / 2 + 0.004)), 0.009, 0.008, "bolt",
                rot=R_.to_euler(), verts=6, bevel=0)
    for xl in legs:
        for a, b in zip(P_, P_[1:]):
            if min(a.x, b.x) - 1e-6 <= xl <= max(a.x, b.x) + 1e-6 and abs(b.x - a.x) > 1e-6:
                q = a + (b - a) * ((xl - a.x) / (b.x - a.x))
                break
        else:
            continue
        box((q.x, q.y, (q.z - 0.0125) / 2), (0.045, 0.045, q.z - 0.0125), "ochre", bevel=0.004)
        box((q.x, q.y, 0.015), (0.13, 0.13, 0.03), "dark_steel", bevel=0.004)
    lifted = [p + Vector((0, 0, TRAY_HC)) for p in P_]
    line = [lifted[0]]
    for a, b in zip(lifted, lifted[1:]):
        n_ = max(1, math.ceil((b - a).length / 0.05))
        line += [a + (b - a) * (k / n_) for k in range(1, n_ + 1)]

    def off_tray(p):
        for a, b in zip(lifted, lifted[1:]):
            d = b - a
            t = max(0.0, min(1.0, (p - a).dot(d) / d.length_squared))
            if (p - (a + d * t)).length < w / 2 + 0.06:
                return False
        return True
    run = list(lead_in or ()) + line + list(lead_out or ())
    bundle(run, cols=cols, r=0.02, glands=(bool(lead_in), bool(lead_out)), sleeve_ok=off_tray)


def tube(x, y, z0, k, h=0.8, arm=(0, 0), arm_len=0.0):
    """A thermionic converter tube: a bolted socket, the glass envelope with the hot emitter
    lit low in it (the cell's heat, the isotope's light), a copper collector cap finned to
    radiate, a ceramic terminal. arm: the lead heat arm's direction into the crucible."""
    cyl((x, y, z0 + 0.11), 0.16, 0.22, "dark_steel", verts=24)
    bolts(x, y, z0 + 0.225, 0.13, 6, r=0.012)
    cyl((x, y, z0 + 0.22 + h / 2), 0.115, h, "tube_glass", verts=32, bevel=0)
    # round 7: a slim emitter column low in the glass (the light), its grid and supports
    # standing in front of it as dark silhouettes, a dark collar where it leaves the socket,
    # and one thin highlight down the glass
    ze, he = z0 + 0.22 + h * 0.3, h * 0.4
    cyl((x, y, ze), 0.06, he, f"rg_tube{k}", verts=32, bevel=0)
    for j in range(4):
        torus((x, y, ze - he * 0.36 + he * 0.24 * j), 0.071, 0.005, "bezel", seg=24)
    for a in (-0.6, 0.6):
        cyl((x + 0.075 * math.sin(a), y - 0.075 * math.cos(a), ze), 0.007, he * 1.15, "bezel", verts=6, bevel=0)
    cyl((x, y, ze - he / 2 - 0.03), 0.078, 0.07, "bezel", verts=24, bevel=0)
    cyl((x, y, z0 + 0.22 + h * 0.75), 0.02, h * 0.42, "bare", verts=8, bevel=0)
    box((x - 0.072, y - 0.085, z0 + 0.22 + h * 0.5), (0.014, 0.006, h * 0.72), "glint", rz=-0.7, bevel=0)
    # T08i, a study aid for Liam's question (not a decision): --tube-band dark draws the glass's two bands
    # in dark steel, --tube-band low drops the upper one (tube 0's upper band, cut by the bus terminal
    # block, shows as a bare arc that reads as a lead); keep (the default) is the adopted look
    band = opt("--tube-band", "keep")
    for f in (0.08, 0.6):
        if band == "low" and f > 0.5:
            continue
        torus((x, y, z0 + 0.22 + h * f), 0.117, 0.012, "dark_steel" if band == "dark" else "bare", seg=24)
    zc = z0 + 0.22 + h
    cyl((x, y, zc + 0.05), 0.13, 0.12, "copper", verts=24)
    for j in range(8):
        a = 2 * PI * j / 8 + 0.2
        box((x + 0.16 * math.cos(a), y + 0.16 * math.sin(a), zc + 0.06), (0.13, 0.02, 0.15), "copper", rz=a,
            bevel=0.003)
    cyl((x, y, zc + 0.15), 0.035, 0.08, "ceramic", verts=12)
    cyl((x, y, zc + 0.2), 0.016, 0.04, "copper", verts=8, bevel=0)
    if arm_len:
        ax, ay = arm
        box((x + ax * arm_len / 2, y + ay * arm_len / 2, z0 + 0.32),
            (abs(ax) * arm_len + 0.16 if ax else 0.16, abs(ay) * arm_len + 0.16 if ay else 0.16, 0.18), "lead_new",
            bevel=0.01)
    return zc + 0.22


def tube_phase(i, n, t, cycles=2):
    """The chase: each tube brightens in turn along its row, `cycles` times a loop."""
    u = (t * cycles - i / n) % 1.0
    return 0.7 + 0.3 * (0.5 + 0.5 * math.cos(2 * PI * u))       # round 7: a swell, not a blink (0.45-1.0 in round 6)


def carousel(cx, cy, RR, n=8, zd=0.8, pick_a=0.0, L=4, drive_a=None, with_head=True, label_n=(3, 2), head_back=2):
    """Round 5 #3's turning magazine on a heavy lead-clad drum. Pockets index one step a loop
    (MOVE); a pocket holds a fresh cell from the loading hood round to the pick station, a
    spent one from the pick round to the hood (where the swap is hidden). The collector head
    reads the cell one station before the pick. Returns the pick point (x, y, top z)."""
    step = 2 * PI / n
    RP = RR * 0.66
    # the fixed drum, lead clad and banded, on a dark-steel foot ring
    cyl((cx, cy, 0.09), RR + 0.16, 0.18, "dark_steel", verts=96)
    bolts(cx, cy, 0.19, RR + 0.11, 28, r=0.018)
    cyl((cx, cy, 0.18 + (zd - 0.42) / 2), RR + 0.06, zd - 0.42, "lead", verts=96)
    for z in (0.32, zd - 0.36):
        vessel_band(cx, cy, z, RR + 0.06, n_rivets=24, lugs=4, lug_a=-PI / 4)
    for k in range(6):
        a = 2 * PI * k / 6 + 0.3
        box((cx + (RR + 0.07) * math.cos(a), cy + (RR + 0.07) * math.sin(a), 0.18 + (zd - 0.42) / 2),
            (0.03, 0.035, zd - 0.48), "seam", rz=a, bevel=0.002)
    annulus((cx, cy, zd - 0.27), RR - 0.2, RR + 0.1, 0.06, "dark_steel", seg=96)
    # the turning table
    piv = pivot((cx, cy, 0.0), layer="carousel")
    table = cyl((0, 0, zd - 0.11), RR, 0.22, "lead_new", verts=96, parent=piv)
    cyl((0, 0, zd - 0.215), RR + 0.03, 0.04, "bare", verts=96, parent=piv)
    nt = int(RR * 22)                  # round 7: half the teeth (round 6's pitch was one index-frame's travel)
    for k in range(nt):
        a = 2 * PI * k / nt
        box(((RR + 0.04) * math.cos(a), (RR + 0.04) * math.sin(a), zd - 0.12), (0.06, 0.045, 0.14), "dark_steel",
            rz=a, bevel=0.004, parent=piv)
    pockets = []
    for k in range(n):
        a = pick_a + step * k
        px, py = RP * math.cos(a), RP * math.sin(a)
        cyl((px, py, zd + 0.035), 0.19, 0.07, "dark_steel", verts=32, parent=piv)
        cyl((px, py, zd + 0.075), 0.15, 0.03, "lead", verts=32, parent=piv)
        cyl((px, py, zd + 0.085), 0.1, 0.03, "dark", verts=24, bevel=0, parent=piv)
        bolts(px, py, zd + 0.075, 0.17, 4, r=0.014, parent=piv)   # round 7: 4, not 8 (they twinkled in the index)
        bore(table, (px, py), 0.095, zd - 0.11)   # FIX 14: the pocket's bore, which the hoists' cells go down
        fresh = cell((px, py, zd - 0.04), True, parent=piv)
        spent = cell((px, py, zd - 0.04), False, parent=piv)
        pockets.append((k, fresh, spent))
        b = a + step / 2
        box(((RR - 0.1) * math.cos(b), (RR - 0.1) * math.sin(b), zd + 0.005), (0.2, 0.06, 0.012), "hazard", rz=b,
            bevel=0, parent=piv)
        box(((RP - 0.05) * math.cos(b), (RP - 0.05) * math.sin(b), zd + 0.008), (RR * 0.5, 0.035, 0.016), "seam",
            rz=b, bevel=0, parent=piv)
    spin(piv, 1 / n, ease=lambda t: index_u(t))

    def contents(t, on):
        u = index_u(t, on)
        for k, fresh, spent in pockets:
            s = (k + u) % n
            if s < 1e-3 or s > n - 1e-3:
                c = pick_content(t) if (on and t < MOVE[0]) else "fresh"
            elif s <= L + 1e-3:
                c = "spent"
            else:
                c = "fresh"
            if not on:
                c = "fresh" if (s < 1e-3 or s > L + 1e-3) else "spent"
            for o in fresh:
                o.hide_render = c != "fresh"
            for o in spent:
                o.hide_render = c != "spent"
    ANIM.append(contents)
    # the fixed hub: a lead dome over the centre bearing
    hr = min(0.5, RR * 0.36)
    cyl((cx, cy, zd + 0.2025), hr, 0.395, "lead", verts=64)      # FIX 4: its foot 0.005 over the turning table
    head(cx, cy, zd + 0.4, hr, hr * 0.6, "lead")
    vessel_band(cx, cy, zd + 0.22, hr, n_rivets=12)
    manway_top(cx + hr * 0.25, cy + hr * 0.2, zd + 0.4 + hr * 0.55, r=0.1, nb=8)
    status_lamp(cx - hr * 0.4, cy - hr * 0.3, zd + 0.4 + hr * 0.42)
    # the loading hood over stations L-0.6 .. L+1.6: where spent cells drop out and fresh go in
    a0, a1 = pick_a + step * (L - 0.6), pick_a + step * (L + 1.6)
    sector((cx, cy, zd + 0.5), RP - 0.3, RR + 0.12, a0, a1, 0.06, "lead", seg=16)
    sector((cx, cy, zd + 0.24), RR + 0.04, RR + 0.12, a0, a1, 0.5, "lead", seg=16)
    # FIX 1 (--collide): the inner wall and the end walls stop at zd + 0.2, over the pockets' cells, where
    # round 7's reached the table's top and the turning table ran through them; the slot they leave is
    # where the cells go under the hood
    sector((cx, cy, zd + 0.35), RP - 0.3, RP - 0.22, a0, a1, 0.3, "lead", seg=16)
    sector((cx, cy, zd + 0.555), RR - 0.05, RR + 0.14, a0, a1, 0.04, "dark_steel", seg=16)
    for a in (a0, a1):
        box((cx + (RP + RR - 0.18) / 2 * math.cos(a), cy + (RP + RR - 0.18) / 2 * math.sin(a), zd + 0.37),
            (RR - RP + 0.42, 0.06, 0.32), "lead", rz=a, bevel=0.01)
    am = pick_a + step * (L + 0.5)
    for k, da in enumerate((-0.3, 0.3)):                     # the two charging ports: the fuel slots
        a = am + da * step
        px, py = cx + (RP + 0.1) * math.cos(a), cy + (RP + 0.1) * math.sin(a)
        cyl((px, py, zd + 0.6), 0.13, 0.12, "lead_new", verts=8)
        cyl((px, py, zd + 0.665), 0.1, 0.02, "dark", verts=24, bevel=0)
        torus((px, py, zd + 0.665), 0.11, 0.012, "yellow", seg=24)
    ax, ay = cx + (RR + 0.3) * math.cos(am), cy + (RR + 0.3) * math.sin(am)
    label(1, "cells in: two charging ports on the loading hood", (cx + (RP + 0.1) * math.cos(am),
                                                                    cy + (RP + 0.1) * math.sin(am), zd + 0.65))
    # the spent chute and its lead bin outside the rim
    # FIX 2: the chute 0.1 further out, clear of the ring gear's teeth (round 7's crossed them)
    box((cx + (RR + 0.25) * math.cos(am), cy + (RR + 0.25) * math.sin(am), zd - 0.05), (0.3, 0.26, 0.12), "lead_new",
        rz=am, rot=(0, 0.5, am), bevel=0.008)
    out = dict(load=(ax, ay), pick=(cx + RP * math.cos(pick_a), cy + RP * math.sin(pick_a), zd + 0.12))
    # the collector head, one station before the pick
    if with_head:
        ah = pick_a - step * head_back
        hp = pivot((cx, cy, 0.0), (0, 0, ah))
        x0, x1 = RP - 0.3, RR + 0.22
        for s in (-1, 1):
            box((RR + 0.18, s * 0.27, (zd + 0.55) / 2), (0.16, 0.12, zd + 0.55), "oxide", parent=hp)
        box(((x0 + x1) / 2, 0, zd + 0.48), (x1 - x0, 0.62, 0.22), "oxide", bevel=0.02, parent=hp)
        box((RP, 0, zd + 0.3), (0.42, 0.42, 0.18), "oxide", bevel=0.015, parent=hp)
        for k in range(5):
            box((x0 + 0.08 + 0.1 * k, 0, zd + 0.65), (0.03, 0.5, 0.14), "grey", bevel=0.003, parent=hp)
        wp = (RR - 0.12, 0, zd + 0.62)
        tilt = (0, 0.45, 0)
        o = pivot(wp, tilt, parent=hp)
        # round 7: a bolted bullseye port, smaller, the light recessed behind a dark bezel
        # and a thick lens, a guard bar across it as a silhouette, a highlight on the glass
        cyl((0, 0, -0.01), 0.19, 0.03, "dark_steel", verts=40, parent=o)
        annulus((0, 0, 0.012), 0.1, 0.18, 0.05, "dark_steel", seg=48, parent=o)
        annulus((0, 0, 0.034), 0.09, 0.112, 0.012, "bezel", seg=48, parent=o)
        cyl((0, 0, 0.008), 0.1, 0.006, "rg_window", verts=48, bevel=0, parent=o)
        box((0, 0, 0.02), (0.2, 0.016, 0.014), "bezel", rz=0.5, bevel=0, parent=o)
        cyl((0, 0, 0.03), 0.1, 0.008, "pane", verts=48, bevel=0, parent=o)
        sector((0, 0, 0.036), 0.07, 0.078, 1.9, 2.8, 0.003, "glint", seg=8, parent=o)
        for k in range(10):
            a = 2 * PI * k / 10
            cyl((0.15 * math.cos(a), 0.15 * math.sin(a), 0.04), 0.012, 0.02, "bolt", verts=6, bevel=0, parent=o)
        hx, hy = cx + RP * math.cos(ah), cy + RP * math.sin(ah)
        out["head"] = (hx, hy, zd + 0.6)
        label(label_n[0], "collector head: reads each cell's charge before the pick", out["head"])
    # the drive: a geared motor on a pinion at the ring gear
    if drive_a is not None:
        gx, gy = cx + (RR + 0.28) * math.cos(drive_a), cy + (RR + 0.28) * math.sin(drive_a)
        dp = pivot((gx, gy, 0.0), (0, 0, drive_a))
        # FIX 5: the pinion 0.05 further out, its teeth beside the ring gear's (round 7's crossed them),
        # and the gear case's inner face drawn back past it (round 7's case held the pinion inside it)
        box((0.13, 0, zd * 0.5), (0.2, 0.42, zd - 0.05), "dark_steel", parent=dp)
        box((0.15, 0, zd - 0.02), (0.24, 0.46, 0.06), "green", parent=dp)
        pin = pivot((gx - 0.09 * math.cos(drive_a), gy - 0.09 * math.sin(drive_a), zd - 0.12), layer="drive")
        for k in range(10):
            a = 2 * PI * k / 10
            box((0.09 * math.cos(a), 0.09 * math.sin(a), 0), (0.05, 0.035, 0.14), "bare", rz=a, bevel=0, parent=pin)
        spin(pin, 2, ease=lambda t: index_u(t))
        tx, ty = -math.sin(drive_a), math.cos(drive_a)
        motor(gx + 0.08 * math.cos(drive_a), gy + 0.08 * math.sin(drive_a), zd + 0.22, d=(tx, ty), s=0.7)
        coupling(gx + 0.08 * math.cos(drive_a) - tx * 0.3, gy + 0.08 * math.sin(drive_a) - ty * 0.3, zd + 0.22, 0.1,
                 axis=(tx, ty, 0), turns=3, ease=lambda t: index_u(t), layer="drive")
        label(label_n[1], "carousel drive: geared motor, pinion on the ring gear", (gx, gy, zd + 0.3))
    return out


WELL_GLOW = lambda t: lid_open(t)          # noqa: E731


def crane(axis, rails, z_rail, c0, P, W, zP, zW, u_lo, u_hi, d=0.38, label_n=4, rail_posts=None, posts_on=None):
    """Round 5 #4's gantry with a twin hoist, travelling along `axis` ('x' or 'y') on two rails at
    cross positions `rails`; the trolley sits at cross position c0; P and W are the pick and the
    well along the travel axis, zP and zW their tops. Rails run u_lo .. u_hi."""
    def W3(u, v, z):
        return (u, v, z) if axis == "x" else (v, u, z)

    def S3(a, b, c):
        return (a, b, c) if axis == "x" else (b, a, c)
    # the rails, on their housings' copings (the caller builds the housings) or on posts
    for v in rails:
        box(W3((u_lo + u_hi) / 2, v, z_rail), S3(u_hi - u_lo, 0.14, 0.1), "ochre", bevel=0.01)
        box(W3((u_lo + u_hi) / 2, v, z_rail + 0.065), S3(u_hi - u_lo, 0.05, 0.03), "bare", bevel=0.004)
        for u in (u_lo + 0.05, u_hi - 0.05):
            box(W3(u, v, z_rail + 0.1), S3(0.06, 0.16, 0.12), "hazard", bevel=0.004)
        for u in rail_posts or ():
            if posts_on and not posts_on(u, v):
                continue          # FIX 10: round 7's posts stood inside the shield housing that carries this rail
            box(W3(u, v, z_rail / 2), S3(0.14, 0.14, z_rail), "ochre", bevel=0.012)
            box(W3(u, v, 0.08), S3(0.3, 0.3, 0.16), "dark_steel")
    span = abs(rails[1] - rails[0])
    vm = (rails[0] + rails[1]) / 2
    br = pivot((0, 0, 0), layer="crane")
    for v in rails:
        box(W3(0, v, z_rail + 0.17), S3(0.46, 0.22, 0.2), "ochre", bevel=0.015, parent=br)
        for s in (-1, 1):
            cyl(W3(s * 0.13, v, z_rail + 0.12), 0.06, 0.24, "dark_steel",
                rot=(PI / 2, 0, 0) if axis == "x" else (0, PI / 2, 0), verts=16, parent=br)
    for du in (-0.13, 0.13):
        box(W3(du, vm, z_rail + 0.27), S3(0.07, span + 0.1, 0.26), "ochre", bevel=0.008, parent=br)
        box(W3(du, vm, z_rail + 0.41), S3(0.12, span + 0.1, 0.025), "ochre", bevel=0.004, parent=br)
        box(W3(du, vm, z_rail + 0.14), S3(0.12, span + 0.1, 0.025), "ochre", bevel=0.004, parent=br)
    for k in range(0):                 # round 7: the bridge's hazard ticks twinkled as it ran; dropped
        box(W3(-0.17, rails[0] + 0.25 * (1 if rails[1] > rails[0] else -1) + (k * 0.32) * (1 if rails[1] > rails[0] else -1),
               z_rail + 0.3), S3(0.012, 0.13, 0.12), "hazard", bevel=0, parent=br)
    # the trolley: two hoists side by side across the bridge, A (fresh in) and B (spent out);
    # it traverses a hoist's pitch d to put one or the other over the station
    tr = pivot((0, 0, 0), parent=br)
    drum_rot = (0, PI / 2, 0) if axis == "x" else (PI / 2, 0, 0)
    box(W3(0, 0, z_rail + 0.5), S3(0.46, d + 0.4, 0.18), "ochre", bevel=0.015, parent=tr)
    for s in (-1, 1):
        cyl(W3(0, s * d / 2, z_rail + 0.62), 0.09, 0.34, "dark_steel", rot=drum_rot, verts=24, parent=tr)
        for du in (-0.18, 0.18):
            cyl(W3(du, s * d / 2, z_rail + 0.62), 0.11, 0.02, "ochre", rot=drum_rot, verts=24, parent=tr)
    box(W3(0.3, 0, z_rail + 0.55), S3(0.16, 0.22, 0.16), "green", bevel=0.01, parent=tr)
    box(W3(0, -d / 2, z_rail + 0.595), S3(0.3, 0.07, 0.012), "yellow", bevel=0, parent=tr)
    box(W3(0, d / 2, z_rail + 0.595), S3(0.3, 0.07, 0.012), "red", bevel=0, parent=tr)
    hooks = []
    for s, fresh in ((-1, True), (1, False)):
        hk = pivot((0, 0, 0), parent=tr)
        box((0, 0, 0), (0.2, 0.2, 0.1), "yellow" if fresh else "red", bevel=0.01, parent=hk)
        sphere((0, 0, -0.06), 0.035, "dark_steel", parent=hk)
        objs = cell((0, 0, -0.24), fresh, parent=hk)
        cab = [cyl((0, 0, 0.5), 0.009, 1.0, "dark_steel", verts=6, bevel=0, parent=tr) for _ in (0, 1)]
        hooks.append((s, hk, objs, cab))
    z_up = z_rail - 0.02
    LIFT = 0.025          # FIX 6: the bridge rides 0.025 higher, its wheels on the rails' caps (round 7's sank 0.02 into them)
    ukey = {"P+": P, "P-": P, "W-": W, "W+": W}
    vkey = {"P+": c0 + d / 2, "W+": c0 + d / 2, "P-": c0 - d / 2, "W-": c0 - d / 2}

    def pose(t, on):
        tt = t if on else 0.0
        (k0, k1, u), dA, dB, cA, cB = crane_state(tt)
        b = ukey[k0] + (ukey[k1] - ukey[k0]) * u
        v = vkey[k0] + (vkey[k1] - vkey[k0]) * u
        br.location = W3(b, 0, 0)
        br.location.z = LIFT
        tr.location = W3(0, v, 0)
        zs = zP if abs(b - P) < abs(b - W) else zW
        for (s, hk, objs, cab), dd, carry in ((hooks[0], dA, cA), (hooks[1], dB, cB)):
            z = z_up + (zs + 0.08 - z_up) * dd
            hk.location = W3(0, s * d / 2, z - LIFT)
            top = z_rail + 0.55
            for j, o in enumerate(cab):
                o.scale = (1, 1, max(0.02, top - z))
                o.location = W3((j - 0.5) * 0.06, s * d / 2, (top + z) / 2 - LIFT)
            for o in objs:
                o.hide_render = not carry
    ANIM.append(pose)
    lp = (P + W) / 2
    label(label_n, "twin-hoist crane: A carries the fresh cell to the well, B the spent one back",
          W3(lp, c0, z_rail + 0.5))
    return br


def bore(o, xy, r, z):
    """A round hole r across through o at xy (a boolean difference with a hidden cutter, applied)."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r, depth=0.6, location=(xy[0], xy[1], z))
    cut = bpy.context.active_object
    cut.parent = o.parent
    bpy.context.view_layer.update()
    m = o.modifiers.new("bore", "BOOLEAN")
    m.operation, m.object, m.solver = "DIFFERENCE", cut, "EXACT"
    o.modifiers.move(len(o.modifiers) - 1, 0)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    o.modifiers.clear()
    o.data = me
    bpy.data.objects.remove(cut)


def crucible(x0, x1, y0, y1, zt, well, slot, hinge="N", plates="x", label_n=5, bus_to=None):
    """Round 5 #4's lead crucible holding round 5 #7's plate rack: the cells stand between
    copper collector plates (seen through the glazed slot, the floor of light between them);
    the served well, its bolted lid lifted by the hinge while the crane works it."""
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    box((xm, ym, 0.08), (x1 - x0 + 0.14, y1 - y0 + 0.14, 0.16), "dark_steel")
    box((xm, ym, (zt + 0.16) / 2), (x1 - x0, y1 - y0, zt - 0.16), "lead", bevel=0.03)
    for xx in [x0 + 0.3 + i * 0.55 for i in range(int((x1 - x0 - 0.3) / 0.55) + 1)]:
        if xx < x1 - 0.1:
            box((xx, y0 - 0.01, (zt + 0.16) / 2), (0.08, 0.04, zt - 0.14), "bare", bevel=0.005)
    for yy in [y0 + 0.3 + i * 0.55 for i in range(int((y1 - y0 - 0.3) / 0.55) + 1)]:
        if yy < y1 - 0.1:
            box((x1 + 0.01, yy, (zt + 0.16) / 2), (0.04, 0.08, zt - 0.14), "bare", bevel=0.005)
    weld = [zt - 0.25, 0.4]
    for z in weld:
        box((xm, y0 - 0.006, z), (x1 - x0 - 0.02, 0.012, 0.025), "seam", bevel=0)
    # the roof: lead plates round the slot and the well, a dark-steel coping
    sx0, sx1, sy0, sy1 = slot
    box((xm, ym, zt + 0.03), (x1 - x0 + 0.08, y1 - y0 + 0.08, 0.06), "dark_steel", bevel=0.01)
    for (a, b, c, d_) in ((x0, sx0, y0, y1), (sx1, x1, y0, y1), (sx0, sx1, y0, sy0), (sx0, sx1, sy1, y1)):
        if b - a > 0.02 and d_ - c > 0.02:
            o = box(((a + b) / 2, (c + d_) / 2, zt + 0.09), (b - a, d_ - c, 0.06), "lead_new", bevel=0.012)
            if a < well[0] < b and c < well[1] < d_:
                bore(o, well, 0.11, zt + 0.09)   # FIX 7: the well's mouth through it
    # lid panels over the rest of the roof, bolted, with handles; a raised lead collar
    # round the well and lagged heat arms between the lids
    rnd = random.Random(3)
    nx_, ny_ = max(1, int((x1 - x0) / 0.42)), max(1, int((y1 - y0) / 0.42))
    lw, lh = (x1 - x0) / nx_, (y1 - y0) / ny_
    for i in range(nx_):
        for j in range(ny_):
            lx, ly = x0 + lw * (i + 0.5), y0 + lh * (j + 0.5)
            if sx0 - lw / 2 < lx < sx1 + lw / 2 and sy0 - lh / 2 < ly < sy1 + lh / 2:
                continue
            if math.hypot(lx - well[0], ly - well[1]) < 0.42:
                continue
            hgt = rnd.choice((0.03, 0.05, 0.08))
            box((lx, ly, zt + 0.12 + hgt / 2), (lw - 0.06, lh - 0.06, hgt), "lead" if rnd.random() < 0.6 else "lead_new",
                bevel=0.01)
            torus((lx, ly, zt + 0.13 + hgt), 0.03, 0.007, "yellow", rot=(PI / 2, 0, 0), seg=12)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    cyl((lx + sx * (lw / 2 - 0.07), ly + sy * (lh / 2 - 0.07), zt + 0.125 + hgt), 0.012, 0.012,
                        "bolt", verts=6, bevel=0)
    # FIX 7: round 7's well sat under a solid lead disc that covered its mouth (and that the crane's
    # cells went through); it is a ring, so the mouth is open as spec 3.3 has it
    annulus((well[0], well[1], zt + 0.13), 0.11, 0.36, 0.08, "lead", seg=48)
    annulus((well[0], well[1], zt + 0.13), 0.11, 0.385, 0.075, "bare", seg=48)     # FIX 7: vessel_band's band, a ring
    for i in range(4):
        a = PI / 4 + 2 * PI * i / 4
        box((well[0] + 0.41 * math.cos(a), well[1] + 0.41 * math.sin(a), zt + 0.13), (0.06, 0.06, 0.125), "dark_steel",
            rz=a, bevel=0.006)
    rivet_ring(well[0], well[1], zt + 0.13, 0.392, 14)
    # the slot: plates and cells, the floor of light, glazing on a bolted frame
    # round 7: the light is a floor deep in the slot, a dark liner round it (the frame's
    # shadow), the plates and the cells standing in it as dark silhouettes
    box(((sx0 + sx1) / 2, (sy0 + sy1) / 2, zt + 0.07), (sx1 - sx0, sy1 - sy0, 0.02), "rg_floor", bevel=0)
    for (lx, ly, lw_, lh_) in (((sx0 + sx1) / 2, sy0 + 0.012, sx1 - sx0, 0.024),
                              ((sx0 + sx1) / 2, sy1 - 0.012, sx1 - sx0, 0.024),
                              (sx0 + 0.012, (sy0 + sy1) / 2, 0.024, sy1 - sy0),
                              (sx1 - 0.012, (sy0 + sy1) / 2, 0.024, sy1 - sy0)):
        box((lx, ly, zt + 0.155), (lw_, lh_, 0.17), "bezel", bevel=0)
    if plates == "x":
        npl = int((sx1 - sx0) / 0.13)
        xs = [sx0 + 0.07 + i * (sx1 - sx0 - 0.14) / (npl - 1) for i in range(npl)]
        for i, xx in enumerate(xs):
            box((xx, (sy0 + sy1) / 2, zt + 0.15), (0.03, sy1 - sy0 - 0.06, 0.15), "sil", bevel=0.003)
            if i < npl - 1 and i % 2 == 0:
                for yy in [sy0 + 0.1 + j * 0.15 for j in range(max(1, int((sy1 - sy0 - 0.06) / 0.15)))]:
                    cyl(((xx + xs[i + 1]) / 2, yy, zt + 0.14), 0.034, 0.13, "bezel", verts=16)
                    cyl(((xx + xs[i + 1]) / 2, yy, zt + 0.21), 0.038, 0.014, "sil", verts=16, bevel=0)
    else:
        npl = int((sy1 - sy0) / 0.1)
        ys = [sy0 + 0.04 + i * (sy1 - sy0 - 0.08) / (npl - 1) for i in range(npl)]
        for i, yy in enumerate(ys):
            box(((sx0 + sx1) / 2, yy, zt + 0.16), (sx1 - sx0 - 0.04, 0.025, 0.13), "copper", bevel=0.003)
            if i < npl - 1 and i % 2 == 0:
                for xx in [sx0 + 0.12 + j * 0.2 for j in range(int((sx1 - sx0 - 0.1) / 0.2))]:
                    cyl((xx, (yy + ys[i + 1]) / 2, zt + 0.15), 0.03, 0.1, "lead_new", verts=12)
    # the pane inset 0.01 from its frame: round 7's ran into the frame's boxes, and with radiant.py's
    # transmissive pane the overlapping volumes took the slot's light out of the glow pass (peak 3, now 99)
    box(((sx0 + sx1) / 2, (sy0 + sy1) / 2, zt + 0.235), (sx1 - sx0 - 0.02, sy1 - sy0 - 0.02, 0.012), "pane", bevel=0)
    box((sx0 + (sx1 - sx0) * 0.22, sy1 - 0.045, zt + 0.243), ((sx1 - sx0) * 0.2, 0.007, 0.002), "glint", bevel=0)
    for (a, b) in ((sx0, sy0), (sx1, sy1)):
        box(((sx0 + sx1) / 2, b, zt + 0.19), (sx1 - sx0 + 0.08, 0.05, 0.1), "dark_steel", bevel=0.004)
        box((a, (sy0 + sy1) / 2, zt + 0.19), (0.05, sy1 - sy0 + 0.08, 0.1), "dark_steel", bevel=0.004)
    if plates == "x":
        for xx in [sx0 + (sx1 - sx0) * i / 4 for i in range(1, 4)]:
            box((xx, (sy0 + sy1) / 2, zt + 0.245), (0.03, sy1 - sy0, 0.03), "dark_steel", bevel=0.003)
    else:
        for yy in [sy0 + (sy1 - sy0) * i / 4 for i in range(1, 4)]:
            box(((sx0 + sx1) / 2, yy, zt + 0.245), (sx1 - sx0, 0.03, 0.03), "dark_steel", bevel=0.003)
    # the collector bus: two copper bars on ceramic stand-offs along the slot's long sides
    long_x = (sx1 - sx0) >= (sy1 - sy0)
    for s in (-1, 1):
        if long_x:
            yy = (sy0 + sy1) / 2 + s * ((sy1 - sy0) / 2 + 0.1)
            box(((sx0 + sx1) / 2, yy, zt + 0.25), (sx1 - sx0, 0.05, 0.035), "copper", bevel=0.005)
            for xx in (sx0 + 0.1, (sx0 + sx1) / 2, sx1 - 0.1):
                cyl((xx, yy, zt + 0.18), 0.03, 0.1, "ceramic", verts=12)
        else:
            xx = (sx0 + sx1) / 2 + s * ((sx1 - sx0) / 2 + 0.1)
            box((xx, (sy0 + sy1) / 2, zt + 0.25), (0.05, sy1 - sy0, 0.035), "copper", bevel=0.005)
            for yy in (sy0 + 0.1, (sy0 + sy1) / 2, sy1 - 0.1):
                cyl((xx, yy, zt + 0.18), 0.03, 0.1, "ceramic", verts=12)
    # the served well: a lead collar, its lit mouth, the hinged bolted lid
    wx, wy = well
    annulus((wx, wy, zt + 0.15), 0.11, 0.2, 0.18, "lead_new", seg=40)
    annulus((wx, wy, zt + 0.15), 0.1, 0.112, 0.17, "bezel", seg=40)
    cyl((wx, wy, zt + 0.085), 0.105, 0.006, "rg_well", verts=40, bevel=0)
    for j in range(3):            # FIX 7: three guide pins at the rim (round 7's three cell tops filled the
        a = 2 * PI * j / 3 + 0.4  # mouth, in the hoisted cell's way)
        cyl((wx + 0.095 * math.cos(a), wy + 0.095 * math.sin(a), zt + 0.12), 0.008, 0.07, "bezel", verts=8)
    # FIX 8: the hinge 0.03 further out (0.23), the knuckle clear of the collar as the lid swings
    hd = {"N": (0, 0.23, "X", -1), "S": (0, -0.23, "X", 1), "E": (0.23, 0, "Y", 1), "W": (-0.23, 0, "Y", -1)}[hinge]
    hp = pivot((wx + hd[0], wy + hd[1], zt + 0.26), layer="lid")
    cyl((-hd[0], -hd[1], 0.02), 0.19, 0.04, "grey", verts=32, parent=hp)
    for k in range(8):
        a = 2 * PI * k / 8
        cyl((-hd[0] + 0.15 * math.cos(a), -hd[1] + 0.15 * math.sin(a), 0.045), 0.012, 0.015, "bolt", verts=6, bevel=0,
            parent=hp)
    torus((-hd[0], -hd[1], 0.05), 0.04, 0.009, "yellow", rot=(PI / 2, 0, 0), seg=12, parent=hp)
    box((0, 0, 0.02), (0.12 if hd[2] == "X" else 0.06, 0.06 if hd[2] == "X" else 0.12, 0.06), "dark_steel",
        parent=hp)        # FIX 8: 0.02 higher, clear of the collar as the lid swings
    base = hp.rotation_euler.copy()

    def lid(t, on):
        hp.rotation_euler = base
        hp.rotation_euler.rotate_axis(hd[2], hd[3] * 1.9 * lid_open(t, on))
    ANIM.append(lid)
    stencil((xm - (x1 - x0) * 0.22, y0 - 0.008, zt * 0.55), (0.5, 0.012, 0.1))
    hazard_tag((xm + (x1 - x0) * 0.15, y0 - 0.008, zt * 0.8), 0.7, 0.05)
    id_panel((xm + (x1 - x0) * 0.15, y0 - 0.01, zt * 0.45), 0.24, 0.13, stripe="red")
    label(label_n, "lead crucible: cells between copper collector plates (the plate rack)",
          ((sx0 + sx1) / 2, (sy0 + sy1) / 2, zt))
    return (wx, wy, zt + 0.24)


def converter(x0, x1, y, zc, R=0.38, dc_east=True, label_n=8, glow_fn=None, leads=None):
    """Round 5 #7's rotary converter along X: the DC motor (green) with its commutator open and
    its brush gear, the coupling, the AC machine (grey, ribbed), the exciter (cream), on a heavy
    bedplate. The commutator turns one turn a loop (a hazard key on it so the turn reads)."""
    sgn = 1 if dc_east else -1
    xm = (x0 + x1) / 2
    hb = zc - R + 0.08
    cxm0 = (x1 - 0.16 + 0.015) if dc_east else (x0 + 0.16 - 0.015)
    # FIX 9: a pit in the bedplate under the commutator, its floor at 0.2, so the turning drum, its
    # bars, keys and riser clear the bed (round 7's ran 0.04 into it); the south and north rims kept
    box((xm, y, 0.1), (x1 - x0, 2 * R + 0.24, 0.2), "dark_steel", bevel=0.015)
    px0, px1 = cxm0 - 0.21, cxm0 + 0.21
    for a_, b_ in ((x0, px0), (px1, x1)):
        if b_ - a_ > 0.02:
            box(((a_ + b_) / 2, y, 0.2 + (hb - 0.2) / 2), (b_ - a_, 2 * R + 0.24, hb - 0.2), "dark_steel", bevel=0.01)
    for s_ in (-1, 1):
        box(((px0 + px1) / 2, y + s_ * (R + 0.08), 0.2 + (hb - 0.2) / 2), (px1 - px0, 0.08, hb - 0.2), "dark_steel",
            bevel=0.006)
    for xx in [x0 + 0.15 + i * (x1 - x0 - 0.3) / 5 for i in range(6)]:
        for s in (-1, 1):
            box((xx, y + s * (R + 0.13), 0.07), (0.16, 0.06, 0.14), "dark_steel", bevel=0.006)
            cyl((xx, y + s * (R + 0.13), 0.15), 0.02, 0.03, "bolt", verts=6, bevel=0)
    Lt = x1 - x0
    cxm = cxm0                     # the commutator (FIX 9: 0.015 further east, clear of the motor's end ring)
    dc0 = cxm - sgn * 0.185
    dc1 = dc0 - sgn * Lt * 0.3
    cpl = dc1 - sgn * 0.12
    ac0 = cpl - sgn * 0.12
    ac1 = ac0 - sgn * Lt * 0.33
    ex = ac1 - sgn * 0.14
    # DC motor
    cyl(((dc0 + dc1) / 2, y, zc), R, abs(dc1 - dc0), "green", rot=(0, PI / 2, 0), verts=48)
    for xx in (dc0, dc1):
        cyl((xx, y, zc), R + 0.03, 0.05, "dark_steel", rot=(0, PI / 2, 0), verts=48)
    for k in range(4):
        cyl((dc0 + (dc1 - dc0) * (k + 0.5) / 4, y, zc), R + 0.012, 0.025, "green", rot=(0, PI / 2, 0), verts=48)
    box(((dc0 + dc1) / 2, y + 0.1, zc + R + 0.06), (0.32, 0.22, 0.14), "grey", bevel=0.01)
    torus(((dc0 + dc1) / 2, y - 0.12, zc + R + 0.02), 0.04, 0.01, "yellow", rot=(PI / 2, 0, 0), seg=12)
    id_panel(((dc0 + dc1) / 2, y - R - 0.005, zc - 0.05), 0.22, 0.11, stripe="green")
    # the commutator, open: copper drum, mica bars, riser, a hazard key; the brush rocker ring
    com = pivot((cxm, y, zc), (0, PI / 2, 0), layer="commutator")
    cyl((0, 0, 0), R * 0.8, 0.3, "copper", verts=36, parent=com)
    for k in range(8):                 # round 7: 8 bars in a dark copper (12 black ones strobed at 1x)
        a = 2 * PI * k / 8 + PI / 8
        box((R * 0.805 * math.cos(a), R * 0.805 * math.sin(a), 0), (0.04, 0.035, 0.28), "sil", rz=a, bevel=0,
            parent=com)
    cyl((0, 0, -0.125 * sgn), R * 0.9, 0.05, "copper", verts=36, parent=com)   # FIX 9: the riser off the end ring
    box((R * 0.82, 0, 0.0), (0.04, 0.1, 0.28), "hazard", bevel=0, parent=com)
    box((-R * 0.82, 0, 0.0), (0.04, 0.1, 0.28), "hazard", bevel=0, parent=com)   # round 7: two keys, a half-turn symmetry
    cyl((0, 0, 0.19 * sgn), 0.07, 0.1, "bare", verts=16, parent=com)
    spin(com, 0.5)                     # round 7: half a turn a loop (8 frames a bar; round 6's 2.7 strobed)
    # the brush gear above the drum only, on a rocker arm from the north side
    for k, a in enumerate((0.35, 0.95, 1.55)):
        by_, bz = y + R * 0.92 * math.cos(a), zc + R * 0.92 * math.sin(a)
        box((cxm, by_, bz), (0.12, 0.07, 0.09), "brass", rot=(a, 0, 0), bevel=0.004)
    box((cxm, y + R * 0.95 + 0.03, zc * 0.55), (0.08, 0.06, zc * 1.1), "dark_steel", bevel=0.005)
    if leads:          # T08d: the caller's route for the brush leads, a gland at each end
        bundle(leads(cxm), cols=("red", "black"), r=0.022, glands=(True, True))
    else:
        bundle([(cxm, y + R * 0.98, zc + 0.15), (cxm + sgn * 0.2, y + R + 0.1, zc + 0.35),
                (cxm + sgn * 0.25, y + 0.1, zc + R + 0.3)], cols=("red", "black"), r=0.022)
    # coupling, AC machine, exciter
    cyl((cpl, y, zc), 0.07, 0.3, "bare", rot=(0, PI / 2, 0), verts=16)
    coupling(cpl, y, zc, 0.15, axis=(1, 0, 0), turns=1, layer="coupling-converter")
    Ra = R * 1.08
    cyl(((ac0 + ac1) / 2, y, zc), Ra, abs(ac1 - ac0), "grey", rot=(0, PI / 2, 0), verts=48)
    nrib = int(abs(ac1 - ac0) / 0.07)
    for k in range(nrib):
        cyl((ac0 + (ac1 - ac0) * (k + 0.5) / nrib, y, zc), Ra + 0.025, 0.02, "dark_steel", rot=(0, PI / 2, 0),
            verts=48, bevel=0)
    for xx in (ac0, ac1):
        cyl((xx, y, zc), Ra + 0.04, 0.06, "dark_steel", rot=(0, PI / 2, 0), verts=48)
    box(((ac0 + ac1) / 2, y - 0.05, zc + Ra + 0.08), (0.42, 0.3, 0.16), "grey", bevel=0.012)
    for k in range(3):
        cyl(((ac0 + ac1) / 2 - 0.12 + 0.12 * k, y - 0.05, zc + Ra + 0.2), 0.03, 0.1, "ceramic", verts=12)
    meter = ((ac0 + ac1) / 2 + 0.2 * sgn, y - Ra - 0.01, zc + 0.05)
    gauge(meter, (0, -1, 0.2), r=0.075, live=lambda t: 0.25 * math.sin(2 * PI * t) + 0.1, layer="gauge-converter")
    hazard_tag(((ac0 + ac1) / 2 - 0.1 * sgn, y - Ra - 0.01, zc - 0.2), 0.36, 0.05)
    cyl((ex, y, zc), R * 0.55, 0.2, "cream", rot=(0, PI / 2, 0), verts=32)
    cyl((ex - sgn * 0.11, y, zc), R * 0.45, 0.03, "dark_steel", rot=(0, PI / 2, 0), verts=32)
    label(label_n, "rotary converter: open commutator (DC in) driving the AC machine", (cxm, y, zc + R))
    return dict(ac_top=((ac0 + ac1) / 2, y - 0.05, zc + Ra + 0.25), com=(cxm, y, zc), ex=ex)


def transformer(x, y, w, d, h, mat="cream", label_n=9, fin_gaps=()):
    """A transformer: a ribbed tank, fin radiators on the south and the exposed flank, a
    conservator drum on top, three bushings. fin_gaps: x positions where a south fin is left out
    for a cable to leave the tank between its neighbours (T08d)."""
    box((x, y, 0.1), (w + 0.1, d + 0.1, 0.2), "dark_steel")
    box((x, y, 0.2 + h / 2), (w, d, h), mat, bevel=0.02)
    nf = int(w / 0.09)
    for k in range(nf):
        if any(abs(x - w / 2 + 0.06 + (w - 0.12) * k / (nf - 1) - g) < 0.03 for g in fin_gaps):
            continue
        box((x - w / 2 + 0.06 + (w - 0.12) * k / (nf - 1), y - d / 2 - 0.04, 0.2 + h * 0.48), (0.025, 0.08, h * 0.8),
            mat, bevel=0.004)
    nf = int(d / 0.09)
    for k in range(nf):
        box((x + w / 2 + 0.04, y - d / 2 + 0.06 + (d - 0.12) * k / (nf - 1), 0.2 + h * 0.48), (0.08, 0.025, h * 0.8),
            mat, bevel=0.004)
    box((x, y, 0.2 + h + 0.03), (w + 0.06, d + 0.06, 0.05), "dark_steel", bevel=0.006)
    drum_ew(x - w * 0.35, x + w * 0.25, y + d * 0.28, 0.2 + h + 0.2, 0.11, mat="grey", saddles=(x - w * 0.25, x + w * 0.15))
    for k in range(3):
        cyl((x - w * 0.25 + w * 0.25 * k, y - d * 0.15, 0.2 + h + 0.13), 0.04, 0.2, "ceramic", verts=12)
        for z in (0.06, 0.12):
            cyl((x - w * 0.25 + w * 0.25 * k, y - d * 0.15, 0.2 + h + 0.06 + z), 0.055, 0.02, "ceramic", verts=12)
        cyl((x - w * 0.25 + w * 0.25 * k, y - d * 0.15, 0.2 + h + 0.25), 0.02, 0.05, "copper", verts=8)
    id_panel((x - w * 0.15, y - d / 2 - 0.09, 0.2 + h * 0.62), 0.24, 0.12, stripe="yellow")
    gauge((x + w * 0.25, y - d / 2 - 0.09, 0.2 + h * 0.75), (0, -1, 0.15), r=0.06,
          live=lambda t: 0.12 * math.sin(2 * PI * 2 * t), layer="gauge-transformer")
    status_lamp(x + w * 0.3, y + d * 0.2, 0.2 + h + 0.08)
    label(label_n, "transformer", (x, y, 0.2 + h))
    return (x, y, 0.2 + h + 0.25)


def window_lit(t):
    """The collector head's window: full while a cell waits under it, dimming as the table moves."""
    if t < MOVE[0] or t >= MOVE[1]:
        return 1.0                     # round 7: steady (round 6 rippled +-10 % three times a loop)
    u = (t - MOVE[0]) / (MOVE[1] - MOVE[0])
    return 0.5 + 0.5 * (0.5 + 0.5 * math.cos(2 * PI * u))   # dims to 50 % in the index (round 6: 20 %)


def well_lit(t):
    """The well's mouth: rises over three frames as the lid lifts and falls as it closes (round 6
    switched it in 1.6 frames)."""
    return ramp(t, LID[0], LID[0] + 0.1) * (1.0 - ramp(t, LID[1] - 0.08, LID[1]))


# spec 3.3: radiant.py, flicker 0, no pulse (round 7's curves instead). The port's glow emission from
# radiant.py's 90 to 18: under this pane, in this bezel, its light saturated at 90 (peak 214 at 1x with
# its bloom, the render (94, 234, 254); vanilla's glows 87-171) and drove white; measured at 25: 171,
# at 12: 123 (T08, the debug glow render). The slot (112) and the tubes (115) keep radiant.py's own.
# The well's open mouth takes radiant.py's TIGHT bloom, not its WIDE default for a surface: with WIDE it
# is a glow layer of its own, and with the lid shut that layer is empty in frames 0-14 and 27-31,
# which pack.py refuses; TIGHT puts all four openings in one glow layer (T08; Liam's to confirm).
R = radiant.Radiant(pulse=None, flicker=0.0, glow_emission=dict(disc=18.0), bloom=dict(surface=radiant.TIGHT))
LIQUIDS = {}           # material name -> (shape, curve(t) -> strength multiplier)


def liquid(name, shape, size, curve):
    m = R.liquid(name, shape, size)
    M[name] = m
    COLOURS[name] = ("the isotope's light", "#3070FF")
    LIQUIDS[name] = (shape, curve)
    return name


def lights(rows, port=0.1, well=0.105, slot=(0.5, 0.19), tube=(0.06, 0.18)):
    """The isotope's light in its four openings, one radiant.py liquid each (spec 3.3), with
    round 7's strength curves: the port steady, dimming to 50 % while the table indexes
    (window_lit); the slot breathing +-8 % twice a loop; the tubes swelling in turn along their
    row twice a loop, 70-100 % (tube_phase); the well's mouth rising over three frames as its
    lid lifts (well_lit). Sizes are each window's half-extents, as radiant.liquid() takes them.
    Returns the tube material index per (row, i)."""
    liquid("rg_window", "disc", (port,), window_lit)
    liquid("rg_well", "surface", (well,), well_lit)
    liquid("rg_floor", "slot", slot, lambda t: 0.92 + 0.08 * math.cos(2 * PI * t * 2))
    idx = {}
    k = 0
    for r, n in enumerate(rows):
        for i in range(n):
            liquid(f"rg_tube{k}", "tube", tube, (lambda ii, nn: (lambda t: tube_phase(ii, nn, t)))(i, n))
            idx[(r, i)] = k
            k += 1
    return idx


def pose_light(t, mode, shapes=None):
    """radiant's pose (idle, plate or glow) at t, then each window's own strength curve."""
    R.pose(t, mode, shapes)
    for name, (shape, curve) in LIQUIDS.items():
        b = M[name].node_tree.nodes["Principled BSDF"]
        b.inputs["Emission Strength"].default_value *= curve(t)


def lamps(on):
    for s_ in LAMPS:
        s_.default_value = 3.0 if on else 0.0


def layer_of(o):
    """The layer (spec 7) an object moves in: its nearest pivot's that names one; None: the plate."""
    p = o.parent
    while p is not None:
        if p.name in LAYER:
            return LAYER[p.name]
        p = p.parent
    return None


# every top-level kit call builds one unit (the collide check's classifier, as the circulator's kit())
for _fn in ("box", "cyl", "cone", "torus", "annulus", "sphere", "head", "prism", "sector", "hose", "lagged", "pipe",
            "bundle", "trunk", "bolts", "band", "flange_ring", "rivet_ring", "vessel_band", "weld_ring", "gauge",
            "handwheel", "coupling", "valve", "drum_ew", "drum_ns", "vtank", "ladder", "skid", "status_lamp", "motor",
            "jbox", "cabinet", "stencil", "flat_plate", "id_panel", "hazard_tag", "manway_top", "radiator", "cell",
            "housing", "tray", "tube", "carousel", "crane", "crucible", "converter", "transformer"):
    globals()[_fn] = unit(globals()[_fn])
