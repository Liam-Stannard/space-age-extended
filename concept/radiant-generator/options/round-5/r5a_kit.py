"""Radiant Generator, round 5, suggestions 1-5: the shared kit (imported by r5a_<n>_*.py).

Round 5 asks for a generator, not a reactor, finished to the Reaction Plant's round-5
standard. This kit carries that standard over unchanged in approach (the Reaction Plant
worktree is read, not edited): reaction-plant-redesign/concept/reaction-plant/options/
round-5/r5_circulator.py's worn_paint(), the per-part palette in vanilla's idiom, the
lead finish with its bloom, the details (inspection plates, ID panels, hazard tags,
gauges, rivets, weld rings, oil stains) and the sun at 8.8. What is new here:

  - radiant(): the isotope's light, #1F63FF -> #73ADFF, an emissive whose strength each
    model drives per frame (a pulse, a chase, a flicker); 0 in idle.
  - pivot(): an empty that moving parts are built under, posed per frame by ANIM. The
    shared materials pattern in world space, so every moving part carries geometry
    that shows it turning (stripes, spokes, bolts), as the Reaction Plant's couplings do.
  - label(): a numbered point on the cell-to-wire chain, written to labels.json in 1x
    sprite px (x = 208 + 64 X, y = 272 - 64 (Y + Z/2)) for the sheet.
  - run(): renders idle, plate, plate-working and the working loop, or the colour map.

  $BLENDER -b --python r5a_<n>_<name>.py -- <out-dir> [--frames N] [--quick] [--only working|idle]
           [--colourmap] [--ss K]

Units are tiles; north is +Y; the canvas is 512 x 448 sprite px with the entity origin at
(208, 272), as the Reaction Plant's, for every footprint. Nothing here is adopted.
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import rig  # noqa: E402
from materials import TEX, layered, hazard_pattern, _G  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "/tmp/r5a"
QUICK = "--quick" in argv
COLMAP = "--colourmap" in argv
NF_ARG = int(argv[argv.index("--frames") + 1]) if "--frames" in argv else None
ONLY = argv[argv.index("--only") + 1] if "--only" in argv else None
SSK = int(argv[argv.index("--ss") + 1]) if "--ss" in argv else rig.SS
SUN_E = 8.8
os.makedirs(OUT, exist_ok=True)

CANVAS = (512, 448)
CENTRE = (208, 272)
PI = math.pi

sc = rig.reset()
sc.cycles.samples = 16 if QUICK else 80
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
GROUP = {}


def paint(key, hexc, under, group, keyhex, chips=0.65, rust=0.65, wiped=0.25, warm=0.3, film=0.42, metal=None,
          **kw):
    """A painted unit in vanilla's idiom: a layered() part with worn_paint() over it."""
    args = dict(metal=metal or under, paint_metal=0.08, paint_rough=0.58, wear=0.25, rust=0.16, dust=0.35,
                grime=0.65, jitter=0.06, ground=0.8, drips=RUNS, drip=0.85, rust_tint=WET)
    args.update(kw)
    M[key] = layered(key, hexc, **args)
    FINISH[key] = (hexc, chips, under, rust, wiped, warm, None, 0.2, film)
    GROUP[key] = (group, keyhex)


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
    M["label"] = layered("label", "#D8CCAE", paint_metal=0.0, paint_rough=0.7, wear=0.2, rust=0.0, dust=0.3,
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
        GROUP["cable_" + n_] = ("cables", "#A070C0")
    for k, m in M.items():
        soften_grain(m)
        if k in FINISH:
            p, ch, und, ru, wi, wa, sh, mo, fi = FINISH[k]
            worn_paint(m, p, chips=ch, under=und, rust=ru, wiped=wi, warm=wa, sheen=sh, mottle=mo, film=fi)
    GROUP.update({
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
    glass = bpy.data.materials.new("glass")
    glass.use_nodes = True
    gb = glass.node_tree.nodes["Principled BSDF"]
    gb.inputs["Base Color"].default_value = rig.srgb("#C8D8E0")
    gb.inputs["Roughness"].default_value = 0.06
    gb.inputs["IOR"].default_value = 1.47
    gb.inputs["Transmission Weight"].default_value = 0.92
    gb.inputs["Coat Weight"].default_value = 0.4
    M["glass"] = glass
    pane = bpy.data.materials.new("pane")
    pane.use_nodes = True
    pb = pane.node_tree.nodes["Principled BSDF"]
    pb.inputs["Base Color"].default_value = rig.srgb("#D8E4EA")
    pb.inputs["Roughness"].default_value = 0.04
    pb.inputs["IOR"].default_value = 1.08
    pb.inputs["Transmission Weight"].default_value = 1.0
    pb.inputs["Specular IOR Level"].default_value = 0.25
    M["pane"] = pane
    lamp = bpy.data.materials.new("lamp")
    lamp.use_nodes = True
    lb = lamp.node_tree.nodes["Principled BSDF"]
    lb.inputs["Base Color"].default_value = rig.srgb("#203020")
    lb.inputs["Emission Color"].default_value = rig.srgb("#40FF60")
    lb.inputs["Emission Strength"].default_value = 3.0
    M["lamp"] = lamp
    LAMPS.append(lb.inputs["Emission Strength"])
    _oil_material()


LAMPS = []
GLOWS = []        # (strength socket, base, fn(t) -> multiplier)
PHASES = []       # (value node, cycles per loop)
GLOW = 2.4


def radiant(name, mode="flow", scale=6.0, k=1, bright=1.0, fn=None, arms=3):
    """The isotope's light: an emissive blue, #1F63FF -> #73ADFF over a dark navy, its
    pattern moving with a phase (bands along local Z, or a swirl about it) and its strength
    set per frame by fn(t) (a pulse, a chase); 0 in idle. Seen only where the isotope's
    light is: slots, windows, gaps."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    phase = N.new("ShaderNodeValue")
    PHASES.append((phase, k))
    noise = N.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale * 0.7
    noise.inputs["Detail"].default_value = 3.0
    L.new(tc.outputs["Object"], noise.inputs["Vector"])
    if mode == "flow":
        wave = N.new("ShaderNodeTexWave")
        wave.bands_direction = "Z"
        wave.inputs["Scale"].default_value = scale
        wave.inputs["Distortion"].default_value = 11.0
        wave.inputs["Detail"].default_value = 4.0
        wave.inputs["Detail Scale"].default_value = 1.5
        L.new(tc.outputs["Object"], wave.inputs["Vector"])
        neg = N.new("ShaderNodeMath")
        neg.operation = "MULTIPLY"
        neg.inputs[1].default_value = -1.0
        L.new(phase.outputs[0], neg.inputs[0])
        L.new(neg.outputs[0], wave.inputs["Phase Offset"])
        pat = wave.outputs["Fac"]
    else:
        sep = N.new("ShaderNodeSeparateXYZ")
        L.new(tc.outputs["Object"], sep.inputs[0])
        ang = N.new("ShaderNodeMath")
        ang.operation = "ARCTAN2"
        L.new(sep.outputs[1], ang.inputs[0])
        L.new(sep.outputs[0], ang.inputs[1])
        rad = N.new("ShaderNodeVectorMath")
        rad.operation = "LENGTH"
        L.new(tc.outputs["Object"], rad.inputs[0])
        a1 = N.new("ShaderNodeMath")
        a1.operation = "MULTIPLY"
        a1.inputs[1].default_value = float(arms)
        L.new(ang.outputs[0], a1.inputs[0])
        r1 = N.new("ShaderNodeMath")
        r1.operation = "MULTIPLY"
        r1.inputs[1].default_value = scale * 2.2
        L.new(rad.outputs["Value"], r1.inputs[0])
        s1 = N.new("ShaderNodeMath")
        s1.operation = "ADD"
        L.new(a1.outputs[0], s1.inputs[0])
        L.new(r1.outputs[0], s1.inputs[1])
        nz = N.new("ShaderNodeMath")
        nz.operation = "MULTIPLY"
        nz.inputs[1].default_value = 2.5
        L.new(noise.outputs["Fac"], nz.inputs[0])
        s2 = N.new("ShaderNodeMath")
        s2.operation = "ADD"
        L.new(s1.outputs[0], s2.inputs[0])
        L.new(nz.outputs[0], s2.inputs[1])
        s3 = N.new("ShaderNodeMath")
        s3.operation = "SUBTRACT"
        L.new(s2.outputs[0], s3.inputs[0])
        L.new(phase.outputs[0], s3.inputs[1])
        sn = N.new("ShaderNodeMath")
        sn.operation = "SINE"
        L.new(s3.outputs[0], sn.inputs[0])
        mr = N.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = -1.0
        L.new(sn.outputs[0], mr.inputs["Value"])
        pat = mr.outputs["Result"]
    mix = N.new("ShaderNodeMix")
    mix.data_type = "FLOAT"
    mix.inputs["Factor"].default_value = 0.45 if mode == "flow" else 0.22
    L.new(pat, mix.inputs["A"])
    L.new(noise.outputs["Fac"], mix.inputs["B"])
    ramp = N.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position, cr.elements[0].color = 0.25, rig.srgb("#0B2A8C")
    cr.elements[1].position, cr.elements[1].color = 0.8, rig.srgb("#73ADFF")
    e = cr.elements.new(0.52)
    e.color = rig.srgb("#1F63FF")
    L.new(mix.outputs["Result"], ramp.inputs["Fac"])
    dark = N.new("ShaderNodeMix")
    dark.data_type = "RGBA"
    dark.inputs["Factor"].default_value = 0.95     # unlit, a near-black navy: idle shows no blue
    L.new(ramp.outputs["Color"], dark.inputs["A"])
    dark.inputs["B"].default_value = rig.srgb("#0A1022")
    L.new(dark.outputs["Result"], b.inputs["Base Color"])
    L.new(ramp.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Roughness"].default_value = 0.3
    b.inputs["Emission Strength"].default_value = GLOW * bright
    GLOWS.append((b.inputs["Emission Strength"], GLOW * bright, fn))
    M[name] = m
    GROUP[name] = ("the isotope's light", "#3070FF")
    return name


# ---------------------------------------------------------------- geometry
OBJS = []
ANIM = []
LABELS = []
STAINS = []


def _finish(o, mat, bevel=0.012, smooth=False, parent=None):
    o.data.materials.append(M[mat])
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments, mod.limit_method = bevel, 2, "ANGLE"
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    o.parent = parent or ROOT
    if mat.startswith("rg_"):
        o.visible_diffuse = False      # the light shows in its opening; it does not wash the metal blue
        o.visible_glossy = False
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


def bundle(pts, cols=("red", "grey", "yellow", "black"), r=0.014):
    P = catmull(pts)
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
            cyl(tuple(p), r * 2.9, 0.045, "label", rot=along(T[i]), verts=12, bevel=0.002)
            nxt += 0.4


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


def gauge(loc, facing, r=0.07, live=None):
    """A brass-cased gauge, cream face, red needle. live(t) -> needle angle offset, or None."""
    t = Vector(facing).normalized()
    cyl(loc, r, 0.03, "brass", rot=along(t), verts=24, bevel=0.004)
    cyl(tuple(Vector(loc) + t * 0.017), r * 0.8, 0.006, "gauge", rot=along(t), verts=24, bevel=0)
    piv = pivot(tuple(Vector(loc) + t * 0.022), along(t))
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


def pivot(loc, rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new("pivot", None)
    sc.collection.objects.link(e)
    e.parent = parent or ROOT
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


def coupling(x, y, z, r, axis=(0, 0, 1), mat="brass", turns=1.0, ease=None):
    """A six-lobed spider coupling with a hazard stripe, turning `turns` a loop (whole or half turns)."""
    root = pivot((x, y, z), along(axis))
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


# ---------------------------------------------------------------- the run
def run(meta, nf=24):
    nf = NF_ARG or nf
    SUN = rig.sun(SUN_E)
    SUN.data.color = (1.0, 0.94, 0.82)
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.24
    meta = dict(meta, frames=nf, canvas=CANVAS, origin=CENTRE, labels=LABELS)
    json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=1)
    if COLMAP:
        flat = {}
        for o in OBJS:
            for i, m in enumerate(o.data.materials):
                grp, hexc = GROUP.get(m.name, ("(unassigned)", "#FF00FF"))
                if hexc not in flat:
                    fm = bpy.data.materials.new("flat" + hexc)
                    fm.use_nodes = True
                    nt = fm.node_tree
                    nt.nodes.remove(nt.nodes["Principled BSDF"])
                    em = nt.nodes.new("ShaderNodeEmission")
                    em.inputs["Color"].default_value = rig.srgb(hexc)
                    nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
                    flat[hexc] = fm
                o.data.materials[i] = flat[hexc]
        for o in STAINS:
            o.hide_render = True
        SUN.hide_render = True
        sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
        sc.view_settings.look = "None"
        sc.view_settings.exposure = 0.0
        sc.cycles.samples = 8
        rig.camera(*CANVAS, centre_px=CENTRE, ss=2)
        pose(0.0, False)
        rig.render(os.path.join(OUT, "colourmap.png"))
        groups = {}
        for k, (grp, hexc) in GROUP.items():
            if any(m.name == k for o in OBJS for m in o.data.materials) or True:
                groups.setdefault(grp, hexc)
        json.dump(groups, open(os.path.join(OUT, "colourmap.json"), "w"), indent=1)
        print("done")
        return
    rig.camera(*CANVAS, centre_px=CENTRE, ss=SSK)
    ground = rig.ground_catcher()
    ground.parent = ROOT
    rig.bounce_ground()
    if ONLY in (None, "idle"):
        pose(0.0, False)
        rig.render(os.path.join(OUT, "idle.png"))
        ground.hide_render = True
        rig.render(os.path.join(OUT, "plate.png"))
        ground.hide_render = False
    if ONLY in (None, "working"):
        for f in range(nf):
            pose(f / nf, True)
            rig.render(os.path.join(OUT, f"working-{f:02d}.png"))
    print("done")


def pose(t, on):
    for p in ANIM:
        p(t, on)
    for node, k in PHASES:
        node.outputs[0].default_value = 2 * PI * k * t
    for sock, v, fn in GLOWS:
        sock.default_value = (v * (fn(t) if fn else 1.0)) if on else 0.0
    for s in LAMPS:
        s.default_value = 3.0 if on else 0.0
