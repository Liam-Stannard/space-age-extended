"""Reaction Plant redesign, round 5: F, the Circulator -- colour and detail (texturing only).

  $BLENDER -b --python r5_circulator.py -- <out-dir> [--frames N] [--quick] [--only working|idle]
           [--ss K] [--ports | --colourmap] [--sun E]

Liam on round 4: "the model is good but the textures could be improved, everything is the
same, add some colour and more details to break up the rust texture." The model (shape,
layout, pipe pictures, silhouette) is round 4's, approved; round 5 changes the surfaces:

  - a palette per part, in vanilla's idiom (r5_colour_study.py): the reactor and the pots
    in the signature lead, the scrubber oxide red, the feed drum ochre, the receiver and
    every motor weathered green, the pump house, the make-up pot and the filter leaves
    cream, the exchanger and the instrument house grey, the vent condenser copper, the
    skids, saddles and frames dark steel, the pipes, flanges and straps bare steel; red and
    yellow handwheels and marking rings; blue only in the legs.
  - worn_paint() in place of round 4's vanilla_idiom(), which laid one rust mottle over
    every material: paint keeps its colour, chipped to metal or rust at edges, rust in
    the seams, at the foot and down from the bands, a dirt film and streaks, shaded
    undersides, a few wiped patches.
  - details() (surface only, nothing changes the outline): bolted inspection plates,
    riveted seams, weld rings and beads, manways, ID plates and hazard tags (no text),
    brass gauges with red needles, cable labels, pipe-marking rings, oil stains on the
    ground at the feet (at most 45 % opaque, under the outline's alpha threshold).
  - the sun 8.8 (round 4 8.0, whose p95 fell short).

Writes into <out-dir>, at K x sprite size (default rig.SS = 4) on a 512 x 448 sprite
canvas with the entity origin at (208, 272):

  working-NN.png     running, frame NN of the 24-frame loop, on the shadow catcher
  idle.png           stopped and unlit, frame 0, on the shadow catcher
  plate.png          idle without the ground: the plate alone (finish.py, tonal.py, cover)
  plate-working.png  frame 0 running, without the ground

With --ports instead: port-<face>.png and cover-<face>.png on a 448 x 448 canvas, the
origin at its centre, and render.json declaring the four faces' ports, for
tools/blender/downsample.py and pack_ports.py (unchanged); the pictures are round 4's in
round 5's materials (the south one in the receiver's green). With --colourmap:
colourmap.png, every part flat in its palette group's key colour, unlit, and
colourmap.json (group -> key colour). Units are tiles; north is +Y. Nothing is adopted.
"""
import math
import os
import random
import re
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import rig  # noqa: E402
import contract  # noqa: E402
from materials import TEX, layered, hazard_pattern, _G  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0]
QUICK = "--quick" in argv
PORTS = "--ports" in argv
COLMAP = "--colourmap" in argv
SUN_E = float(argv[argv.index("--sun") + 1]) if "--sun" in argv else 8.8   # round 4 8.0: its p95 fell short
NF = int(argv[argv.index("--frames") + 1]) if "--frames" in argv else 24
ONLY = argv[argv.index("--only") + 1] if "--only" in argv else None
os.makedirs(OUT, exist_ok=True)

CANVAS = (512, 448)
CENTRE = (208, 272)
PORT_CANVAS = (448, 448)
SSK = int(argv[argv.index("--ss") + 1]) if "--ss" in argv else rig.SS

sc = rig.reset()
sc.cycles.samples = 16 if QUICK else 96
ROOT = rig.turntable(rig.stretch_root())
PI = math.pi

# ---------------------------------------------------------------- the signature finish, warmed
# Heights (z_top, run length) the bloom hangs from: the reactor's bands and its head
# flange, the scrubber's bands. World z, so one material serves every vessel.
BLOOM_TOPS = ((0.5, 0.32), (1.25, 0.42), (2.0, 0.42), (2.62, 0.5), (3.05, 0.4), (0.95, 0.3), (1.65, 0.4))


def lead_finish(tops=BLOOM_TOPS, bloom=1.0, gain=1.0):
    """Weathered lead sheet (round 4's, unchanged): a dull warm grey in sheets of slightly
    different age; the bloom -- the white salts lead grows where the solution weeps -- a
    dry cream hanging in runs below every band and flange and crusted in the seams."""
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


GRAIN = (0.94, 1.04)   # the photo grain's range, from layered()'s 0.7-1.22: vanilla's speckle is low
BUMP = 0.08            # the photo relief's strength, from layered()'s 0.3


def soften_grain(mat, lo=0.86, hi=1.1):
    """FFF #146 in numbers (finish.py's ratio, the study's soft): narrow the shared
    layered()'s photo grain on this concept's own materials (materials.py untouched)."""
    for nd in mat.node_tree.nodes:
        if nd.type == "MAP_RANGE" and abs(nd.inputs["To Min"].default_value - 0.7) < 1e-6 \
                and abs(nd.inputs["To Max"].default_value - 1.22) < 1e-6:
            nd.inputs["To Min"].default_value = lo
            nd.inputs["To Max"].default_value = hi
        if nd.type == "BUMP" and BUMP is not None:
            nd.inputs["Strength"].default_value = BUMP


def worn_paint(mat, paint, chips=0.5, under="#4A4642", rust=0.5, wiped=0.4, warm=0.6, sheen=None, mottle=0.12,
               film=0.3):
    """Round 5's finish over a layered() part, in place of round 4's vanilla_idiom(), which
    laid one broad rust-and-ochre mottle over everything until every part was the same
    brown. Vanilla's paint stays the paint's colour across a surface, and the wear is local:

      - chips: small flakes knocked off to the metal underneath (`under`), thickest at
        edges and corners, sparse on the flats, each with a thin rust rim;
      - rust where it forms, not all over: in the seams and contact lines (AO), at the
        foot (layered()'s ground), down from the bands and fittings (layered()'s drips);
        `mottle` keeps only a faint trace of round 4's broad mottle;
      - wiped patches: a few hand-sized areas where the dust and grime are rubbed off,
        the paint cleaner and a little glossier (round handles, panels, a ladder);
      - warm-brown dirt in the contact lines, and a warm cast, kept from round 4;
      - sheen: a lower roughness on round bare parts, so a cream band runs along them."""
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
    # a trace of broad weathering, much fainter than round 4's
    if mottle:
        big = g.noise(pos, 3.2, detail=5, rough=0.6, distortion=0.4)
        rm = g.math("MULTIPLY", g.remap(big, 0.6, 0.7), mottle, clamp=True)
        col = g.mixc(rm, col, rig.srgb("#5A3418"))
    # a dirt film: paint in service is never clean -- warm-brown, broken, a few px to a tile
    if film:
        fm = g.math("MULTIPLY", g.remap(g.noise(pos, 4.5, detail=6, rough=0.62, distortion=0.3), 0.38, 0.7), film,
                    clamp=True)
        col = g.mixc(fm, col, g.mulc(col, rig.srgb("#8A7258")))
    # wiped: low-frequency, high threshold -- a few clean patches
    wipe = None
    if wiped:
        wipe = g.math("MULTIPLY", g.remap(g.noise(pos, 2.4, detail=2, rough=0.4), 0.6, 0.68), wiped, clamp=True)
        clean = g.mulc(rig.srgb(paint), (1.06, 1.05, 1.02, 1.0))
        col = g.mixc(wipe, col, g.mixc(0.3, clean, col))
    # chips: flakes a few px across, densest along edges and corners, each to the metal or
    # to rust beneath, with a thin rust rim
    if chips:
        bevel = g.node("ShaderNodeBevel", Radius=0.06).outputs[0]
        dot = g.node("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        g.l.new(bevel, dot.inputs[0])
        g.l.new(normal, dot.inputs[1])
        edge = g.remap(dot.outputs["Value"], 0.998, 0.93)            # 1 near an edge
        flake = g.noise(pos, 15, detail=4, rough=0.72, distortion=0.8)
        thr = g.math("SUBTRACT", 0.63, g.math("MULTIPLY", edge, 0.14))  # easier to chip at edges
        bare = g.math("MULTIPLY", g.math("GREATER_THAN", flake, thr), chips, clamp=True)
        rim = g.math("MULTIPLY", g.math("GREATER_THAN", flake, g.math("SUBTRACT", thr, 0.03)), chips, clamp=True)
        col = g.mixc(rim, col, rig.srgb("#4E2A14"))                 # the rust rim round a chip
        metal = g.mixc(g.noise(pos, 60, detail=2), rig.srgb(under), g.mulc(rig.srgb(under), (1.35, 1.32, 1.28, 1)))
        rusty = g.mixc(g.noise(pos, 31, detail=3), rig.srgb("#4A230E"), rig.srgb("#7E4420"))
        metal = g.mixc(g.remap(g.noise(pos, 5.5, detail=2), 0.45, 0.55), metal, rusty)
        col = g.mixc(bare, col, metal)
        if met_link is not None:
            nt.links.new(g.mixf(bare, met_link.from_socket, 0.6), bsdf.inputs["Metallic"])
        if rough is not None:
            rough = g.mixf(bare, rough, 0.4)
    # dirt streaks: dark-brown runs down the vertical faces (washed dirt, not rust)
    if film:
        nz0 = g.node("ShaderNodeSeparateXYZ", Vector=normal).outputs["Z"]
        st = g.node("ShaderNodeMapping", Vector=pos)
        st.inputs["Scale"].default_value = (1.0, 1.0, 0.15)
        runs = g.remap(g.image(f"{TEX}/maps/rust_streak.png", st.outputs[0], 1.6).outputs["Color"], 0.5, 0.85)
        streak = g.math("MULTIPLY", g.math("MULTIPLY", runs, g.remap(nz0, 0.6, 0.2)), 0.55 * film * 2, clamp=True)
        col = g.mixc(streak, col, g.mulc(col, rig.srgb("#7A6450")))
    # undersides: baked-in shade and grime on the faces turned to the ground, as vanilla's
    # vessels darken into their lower halves
    if film:
        nz = g.node("ShaderNodeSeparateXYZ", Vector=normal).outputs["Z"]
        down = g.math("MULTIPLY", g.remap(nz, 0.1, -0.7), 0.55 * min(1.0, film * 2), clamp=True)
        col = g.mixc(down, col, g.mulc(col, rig.srgb("#6A5440")))
        # rust patches at the foot, where water stands
        zz = g.node("ShaderNodeSeparateXYZ", Vector=pos).outputs["Z"]
        foot = g.math("MULTIPLY", g.remap(zz, 0.32, 0.04), g.remap(g.noise(pos, 8, detail=4, rough=0.6), 0.45, 0.62),
                      clamp=True)
        col = g.mixc(g.math("MULTIPLY", foot, rust, clamp=True), col,
                     g.mixc(g.noise(pos, 19, detail=3), rig.srgb("#40200C"), rig.srgb("#7A4220")))
    # rust in the seams and contact lines only
    if rust:
        rc = g.mixc(g.noise(pos, 9, detail=4), rig.srgb("#3A1C0A"), rig.srgb("#7A4220"))
        seam = g.math("MULTIPLY", g.math("MULTIPLY", cav, 2.2),
                      g.remap(g.noise(pos, 14, detail=4), 0.35, 0.6), clamp=True)
        col = g.mixc(g.math("MULTIPLY", seam, rust, clamp=True), col, rc)
    # warm cast
    col = g.mulc(col, (1.0 + 0.02 * warm, 1.0, 1.0 - 0.06 * warm, 1.0))
    # dirt mottle at a few px, gentler than round 4's, and a fine grime breakup at 1-2 px
    dm = g.noise(pos, 7.5, detail=5, rough=0.6)
    col = g.mulc(col, g.gray(g.remap(dm, 0.3, 0.7, 0.8, 1.04)))
    fg = g.noise(pos, 22, detail=4, rough=0.7)
    col = g.mulc(col, g.gray(g.remap(fg, 0.3, 0.7, 0.84, 1.06)))
    # warm-brown dirt in the contact lines
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


WET = ("#3A1E0C", "#7A4018")        # rust runs below fittings
# Paint heights the rust runs hang from: bands, flanges, nozzle rings (world z)
RUNS = ((0.62, 0.3), (0.95, 0.3), (1.35, 0.3), (1.65, 0.35))
# (name, paint, under-metal, colour-map group). The per-part palette: what each piece of
# equipment is painted or made of (see PALETTE on the sheet).
M = {
    # the signature: the vessels' lead cladding (reactor, settling pot, drop box, leg caps, press leaves)
    "lead": layered("lead", "#6A6258", metal="#BCB4A2", paint_metal=0.3, paint_rough=0.55, wear=0.3,
                    rust=0.06, dust=0.5, grime=0.8, jitter=0.08, ground=0.75, pattern=lead_finish(),
                    drips=tuple((t - 0.03, l * 0.8) for t, l in BLOOM_TOPS), drip=0.6, rust_tint=WET),
    "lead_new": layered("lead_new", "#7A7266", metal="#B4AC9C", paint_metal=0.35, paint_rough=0.55, wear=0.2,
                        rust=0.0, dust=0.3, grime=0.6, jitter=0.03, ground=0.5,
                        pattern=lead_finish(bloom=0.0, gain=1.12)),
    # oxide red: the scrubber (the foundry's red vessel)
    "oxide": layered("oxide", "#6E2C1E", metal="#5A4E46", paint_metal=0.1, paint_rough=0.7, wear=0.25,
                     rust=0.18, dust=0.35, grime=0.6, jitter=0.06, ground=0.8, drips=RUNS, drip=0.85,
                     rust_tint=WET),
    # ochre: the feed drum, the ladder (the chemical plant's yellow)
    "ochre": layered("ochre", "#9C7426", metal="#5E544A", paint_metal=0.08, paint_rough=0.55, wear=0.25,
                     rust=0.15, dust=0.35, grime=0.6, jitter=0.05, ground=0.8, drips=RUNS, drip=0.85,
                     rust_tint=WET),
    # weathered green: the receiver and every motor (the refinery's green tanks)
    "green": layered("green", "#4E6034", metal="#5A544C", paint_metal=0.08, paint_rough=0.62, wear=0.25,
                     rust=0.18, dust=0.4, grime=0.65, jitter=0.07, ground=0.75, drips=RUNS, drip=0.85,
                     rust_tint=WET),
    # cream / off-white: the pump house, the make-up pot, the press's filter leaves (the storage tank,
    # the foundry's units)
    "cream": layered("cream", "#ACA084", metal="#5E564C", paint_metal=0.06, paint_rough=0.6, wear=0.25,
                     rust=0.15, dust=0.3, grime=0.7, jitter=0.05, ground=0.85, drips=RUNS, drip=0.85,
                     rust_tint=WET),
    # grey-painted steel: the exchanger, the instrument house
    "grey": layered("grey", "#6E6A62", metal="#9A9488", paint_metal=0.15, paint_rough=0.55, wear=0.3,
                    rust=0.2, dust=0.35, grime=0.7, jitter=0.06, ground=0.8, drips=RUNS, drip=0.85,
                    rust_tint=WET),
    # dark steel: skids, saddles, foot rings, the press frame, headers, valve bodies
    "dark_steel": layered("dark_steel", "#3E3934", metal="#8C8272", paint_metal=0.35, paint_rough=0.55,
                          wear=0.4, rust=0.35, dust=0.35, grime=0.7, ground=0.8, rust_tint=WET),
    # bare bright steel: pipes, flanges, straps, nozzles, rails -- vanilla's pale pipe metal
    "bare": layered("bare", "#A8A090", metal="#D8D0BE", paint_metal=0.85, paint_rough=0.3, wear=0.5,
                    rust=0.16, dust=0.12, grime=0.5, ground=0.6),
    "seam": layered("seam", "#8A8070", metal="#B0A690", paint_metal=0.7, paint_rough=0.4, wear=0.3,
                    rust=0.25, dust=0.0, jitter=0.04, ground=0.7),
    # bolt heads and rivets: where the rust lives
    "bolt": layered("bolt", "#5A4A3A", metal="#A89880", paint_metal=0.5, paint_rough=0.5, wear=0.5,
                    rust=0.75, dust=0.2, grime=0.6, rust_tint=WET),
    # copper: the vent condenser and its coil (verdigris in the cavities)
    "copper": layered("copper", "#94592C", metal="#D09060", paint_metal=0.9, paint_rough=0.32, wear=0.45,
                      rust=0.04, dust=0.2, grime=0.5, patina=0.9),
    "brass": layered("brass", "#9A7438", metal="#D0AC66", paint_metal=0.9, paint_rough=0.35, wear=0.5,
                     rust=0.1, dust=0.2),
    # hoses: tan and black rubber
    "hose": layered("hose", "#5E4636", metal="#9A7E66", paint_metal=0.0, paint_rough=0.62, wear=0.35,
                    rust=0.0, dust=0.5, grime=0.6, jitter=0.06),
    "hose_k": layered("hose_k", "#38302A", metal="#7A6E62", paint_metal=0.0, paint_rough=0.6, wear=0.35,
                      rust=0.0, dust=0.55, grime=0.5, jitter=0.06),
    # lagging: cream-tan canvas, steel straps
    "lag": layered("lag", "#9A8A68", metal="#B0A080", paint_metal=0.0, paint_rough=0.9, wear=0.25,
                   rust=0.15, dust=0.5, grime=0.7, jitter=0.1, ground=0.6),
    # accents: handwheels, pipe-marking rings, ID panels, cable labels, hazard tape
    "red": layered("red", "#A8301E", metal="#6A5A50", paint_metal=0.05, paint_rough=0.5, wear=0.35,
                   rust=0.1, dust=0.2, grime=0.4, jitter=0.04),
    "yellow": layered("yellow", "#D0A428", metal="#6A5A50", paint_metal=0.05, paint_rough=0.5, wear=0.35,
                      rust=0.1, dust=0.25, grime=0.4, jitter=0.04),
    "hazard": layered("hazard", "#B8962E", paint_metal=0.1, paint_rough=0.85, wear=0.6, rust=0.3,
                      dust=0.6, grime=0.6,
                      pattern=lambda g: g.mixc(0.25, hazard_pattern(g), (0.16, 0.12, 0.08, 1.0))),
    "stencil": layered("stencil", "#CEC2A4", metal="#5A5044", paint_metal=0.05, paint_rough=0.8, wear=0.5,
                       rust=0.2, dust=0.3, grime=0.4, jitter=0.05),
    "label": layered("label", "#D8CCAE", paint_metal=0.0, paint_rough=0.7, wear=0.2, rust=0.0, dust=0.3,
                     grime=0.3, jitter=0.08),
    "gauge": layered("gauge", "#DCD2BA", paint_metal=0.0, paint_rough=0.3, wear=0.1, rust=0.0,
                     dust=0.2, grime=0.4),
    "needle": layered("needle", "#9A2A1A", paint_metal=0.0, paint_rough=0.5, wear=0.0, rust=0.0, dust=0.0,
                      grime=0.0),
    "rubber": layered("rubber", "#26201C", metal="#4A4038", paint_metal=0.0, paint_rough=0.6, wear=0.1,
                      rust=0.0, dust=0.3, grime=0.3),
    "slab": layered("slab", "#4A4038", metal="#A49480", paint_metal=0.25, paint_rough=0.55, wear=0.45,
                    rust=0.3, dust=0.2, grime=0.6, jitter=0.0),
    "dark": layered("dark", "#1E1814", paint_metal=0.0, paint_rough=0.8, wear=0.0, rust=0.0, dust=0.0, grime=0.0),
}
# cables: muted, warm; never blue -- blue is the solution's alone
for _n, _c, _e in (("red", "#9E4430", "#C88068"), ("yellow", "#B89440", "#DCC488"),
                   ("green", "#5A6E42", "#98A880"), ("black", "#34302C", "#746C64"),
                   ("grey", "#4A443E", "#7C746A")):
    M["cable_" + _n] = layered("cable_" + _n, _c, metal=_e, paint_metal=0.0, paint_rough=0.5, wear=0.3,
                               rust=0.0, dust=0.3, grime=0.4, jitter=0.05)
M["cable_blue"] = M["cable_grey"]

FINISH = {   # (paint hex, chips, under-metal, seam rust, wiped, warm, sheen, mottle, film)
    "lead": ("#7A746C", 0.0, "#8A8478", 0.55, 0.2, 0.6, 0.5, 0.4, 0.4),
    "lead_new": ("#7A7266", 0.0, "#8A8478", 0.2, 0.2, 0.6, 0.38, 0.1, 0.15),
    "oxide": ("#6E2C1E", 0.75, "#4A403A", 0.7, 0.25, 0.3, None, 0.2, 0.4),
    "ochre": ("#9C7426", 0.55, "#4E463E", 0.65, 0.25, 0.3, None, 0.2, 0.45),
    "green": ("#4E6034", 0.7, "#4A443E", 0.65, 0.25, 0.3, None, 0.2, 0.4),
    "cream": ("#ACA084", 0.65, "#4E463E", 0.65, 0.3, 0.3, None, 0.18, 0.45),
    "grey": ("#6E6A62", 0.6, "#8A8478", 0.65, 0.25, 0.5, None, 0.2, 0.4),
    "dark_steel": ("#3E3934", 0.3, "#8C8272", 0.7, 0.15, 0.6, 0.45, 0.25, 0.2),
    "bare": ("#A8A090", 0.0, "#D8D0BE", 0.45, 0.2, 0.5, 0.2, 0.1, 0.25),
    "seam": ("#8A8070", 0.0, "#B0A690", 0.4, 0.0, 0.6, None, 0.0, 0.0),
    "bolt": ("#5A4A3A", 0.0, "#A89880", 0.8, 0.0, 0.8, None, 0.3, 0.0),
    "copper": ("#94592C", 0.0, "#D09060", 0.15, 0.25, 0.3, 0.26, 0.05, 0.35),
    "brass": ("#9A7438", 0.0, "#D0AC66", 0.2, 0.3, 0.3, 0.28, 0.0, 0.2),
    "hose": ("#5E4636", 0.0, "#5E4636", 0.0, 0.2, 0.5, None, 0.0, 0.2),
    "hose_k": ("#38302A", 0.0, "#38302A", 0.0, 0.2, 0.6, None, 0.0, 0.0),
    "lag": ("#9A8A68", 0.0, "#9A8A68", 0.45, 0.2, 0.6, None, 0.2, 0.45),
    "red": ("#A8301E", 0.5, "#6A5A50", 0.3, 0.0, 0.0, None, 0.0, 0.2),
    "yellow": ("#D0A428", 0.5, "#6A5A50", 0.3, 0.0, 0.0, None, 0.0, 0.2),
    "hazard": ("#B8962E", 0.4, "#5A4E46", 0.4, 0.0, 0.4, None, 0.1, 0.3),
    "stencil": ("#CEC2A4", 0.4, "#5A5044", 0.4, 0.0, 0.4, None, 0.0, 0.3),
    "slab": ("#4A4038", 0.3, "#A49480", 0.5, 0.0, 0.8, None, 0.2, 0.2),
}
for _k, _m in M.items():
    if GRAIN:
        soften_grain(_m, *GRAIN)
    if _k in FINISH:
        p, ch, und, ru, wi, wa, sh, mo, fi = FINISH[_k]
        worn_paint(_m, p, chips=ch, under=und, rust=ru, wiped=wi, warm=wa, sheen=sh, mottle=mo, film=fi)

# The colour map: each material's group and a key colour (render --colourmap)
GROUP = {
    "lead": ("lead (signature)", "#8C8880"), "lead_new": ("lead (signature)", "#8C8880"),
    "oxide": ("oxide red paint", "#B0402A"), "ochre": ("ochre paint", "#D8A830"),
    "green": ("weathered green paint", "#5E8A38"), "cream": ("cream paint", "#E8DCB8"),
    "grey": ("grey paint", "#8A9098"), "dark_steel": ("dark steel", "#3A3634"),
    "bare": ("bare steel", "#D0D4D8"), "seam": ("bare steel", "#D0D4D8"),
    "bolt": ("rusty bolts and rivets", "#7A3A12"), "slab": ("dark steel", "#3A3634"),
    "copper": ("copper", "#E07838"), "brass": ("brass", "#C8A050"),
    "hose": ("rubber hose, tan", "#7A5A40"), "hose_k": ("rubber hose, black", "#1E1A18"),
    "rubber": ("rubber hose, black", "#1E1A18"), "dark": ("rubber hose, black", "#1E1A18"),
    "lag": ("lagging canvas", "#B8A27A"),
    "red": ("red accents (handwheels, rings)", "#E02818"), "yellow": ("yellow accents", "#F4D020"),
    "hazard": ("hazard and ID panels", "#F0E048"), "stencil": ("hazard and ID panels", "#F0E048"),
    "label": ("hazard and ID panels", "#F0E048"), "gauge": ("brass", "#C8A050"), "needle": ("brass", "#C8A050"),
    "glass": ("glass and the solution", "#3070FF"), "pane": ("glass and the solution", "#3070FF"),
    "bubble": ("glass and the solution", "#3070FF"), "fleck": ("glass and the solution", "#3070FF"),
    "lamp": ("red accents (handwheels, rings)", "#E02818"), "oil": ("oil stains", "#FF00FF"),
}
for _k in M:
    if _k.startswith("cable_"):
        GROUP[_k] = ("cables", "#A070C0")

# ---------------------------------------------------------------- round 2's helpers (r2_blockout.py), the hose's ribs coarsened
# glass: thick, slightly smoky borosilicate
glass = bpy.data.materials.new("glass")
glass.use_nodes = True
gb = glass.node_tree.nodes["Principled BSDF"]
gb.inputs["Base Color"].default_value = rig.srgb("#C8D8E0")
gb.inputs["Roughness"].default_value = 0.06
gb.inputs["IOR"].default_value = 1.47
gb.inputs["Transmission Weight"].default_value = 0.92
gb.inputs["Coat Weight"].default_value = 0.4
M["glass"] = glass
# a flat window seen at 30 deg: thin, low-reflection, or it mirrors the sky grey
pane = bpy.data.materials.new("pane")
pane.use_nodes = True
pb = pane.node_tree.nodes["Principled BSDF"]
pb.inputs["Base Color"].default_value = rig.srgb("#D8E4EA")
pb.inputs["Roughness"].default_value = 0.04
pb.inputs["IOR"].default_value = 1.08
pb.inputs["Transmission Weight"].default_value = 1.0
pb.inputs["Specular IOR Level"].default_value = 0.25
M["pane"] = pane

PHASES = []       # (value node, cycles per loop): set per frame
GLOWS = []        # emission strength nodes, 0 when idle
GLOW = 2.4


def fluid(name, mode, scale=6.0, k=1, arms=3, bright=1.0):
    """The radiant solution: an emissive blue whose pattern moves with a phase.

    mode "flow": bands along the object's local Z, distorted by noise, travelling
    k band-widths a loop. mode "swirl": a spiral of `arms` arms about local Z,
    turning k/arms of a revolution a loop. Dark troughs, bright crests, inside
    #1F63FF -> #73ADFF; with the light off, a dark navy liquid with a sheen.
    """
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
        nz = N.new("ShaderNodeMath")
        nz.operation = "MULTIPLY"
        nz.inputs[1].default_value = 2.5
        L.new(noise.outputs["Fac"], nz.inputs[0])
        s1 = N.new("ShaderNodeMath")
        s1.operation = "ADD"
        L.new(a1.outputs[0], s1.inputs[0])
        L.new(r1.outputs[0], s1.inputs[1])
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
    dark.inputs["Factor"].default_value = 0.82
    L.new(ramp.outputs["Color"], dark.inputs["A"])
    dark.inputs["B"].default_value = rig.srgb("#0A1022")
    L.new(dark.outputs["Result"], b.inputs["Base Color"])
    L.new(ramp.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Roughness"].default_value = 0.15
    b.inputs["Emission Strength"].default_value = GLOW * bright
    GLOWS.append((b.inputs["Emission Strength"], GLOW * bright))
    M[name] = m
    return name


def emissive(name, hexcol, bright=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#141C30")
    b.inputs["Emission Color"].default_value = rig.srgb(hexcol)
    b.inputs["Emission Strength"].default_value = GLOW * bright
    GLOWS.append((b.inputs["Emission Strength"], GLOW * bright))
    M[name] = m
    return name


emissive("bubble", "#A8CCFF", 1.3)
lamp = bpy.data.materials.new("lamp")
lamp.use_nodes = True
lb = lamp.node_tree.nodes["Principled BSDF"]
lb.inputs["Base Color"].default_value = rig.srgb("#203020")
lb.inputs["Emission Color"].default_value = rig.srgb("#40FF60")
lb.inputs["Emission Strength"].default_value = 3.0
M["lamp"] = lamp
LAMP_ON = lb.inputs["Emission Strength"]
M["fleck"] = layered("fleck", "#1A1E28", paint_metal=0.2, paint_rough=0.5, wear=0, rust=0, dust=0, grime=0)

# ---------------------------------------------------------------- geometry
OBJS = []
ANIM = []          # callables(t in [0,1)) that pose the moving parts
STUBS = []


def _finish(o, mat, bevel=0.012, smooth=False, parent=None):
    o.data.materials.append(M[mat])
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments, mod.limit_method = bevel, 2, "ANGLE"
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    o.parent = parent or ROOT
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


def torus(loc, major, minor, mat, rot=(0, 0, 0), seg=48, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, rotation=rot,
                                     major_segments=seg, minor_segments=10)
    return _finish(bpy.context.active_object, mat, 0, smooth=True, parent=parent)


def annulus(loc, r_in, r_out, h, mat, rot=(0, 0, 0), seg=64, parent=None):
    """A thick ring: a frame, a collar, a hoop with its middle open."""
    me = bpy.data.meshes.new("annulus")
    bm = bmesh.new()
    rows = []
    for r, z in ((r_out, -h / 2), (r_out, h / 2), (r_in, h / 2), (r_in, -h / 2)):
        rows.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z))
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


def head(x, y, z, r, h, mat, up=True):
    """A dished head: the top of a sphere, squashed to height h."""
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
    # scale only: the head keeps its own origin, so a drum can turn it about its end
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _finish(o, mat, 0, smooth=True)


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


def sweep(P, r, mat, corr=0.0, pitch=0.03, seg=16):
    T, N, B = frames(P)
    s = [0.0]
    for a_, b_ in zip(P, P[1:]):
        s.append(s[-1] + (b_ - a_).length)
    me = bpy.data.meshes.new("sweep")
    bm = bmesh.new()
    rings = []
    for i, p in enumerate(P):
        rr = r * (1 + corr * (0.5 + 0.5 * math.cos(2 * math.pi * s[i] / pitch)))
        rings.append([bm.verts.new(p + rr * (math.cos(2 * math.pi * k / seg) * N[i]
                                             + math.sin(2 * math.pi * k / seg) * B[i])) for k in range(seg)])
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
    return _finish(o, mat, 0, smooth=True), P, T, s


def hose(pts, r=0.085, mat="hose"):
    """A fat corrugated hose with crimped ferrules and big nuts at both ends."""
    P = catmull(pts)
    sweep(P, r, mat, corr=0.055, pitch=0.095, seg=18)  # round 4: ribs shallower, less small detail
    for p, q in ((P[0], P[1]), (P[-1], P[-2])):
        t = (p - q).normalized()
        cyl(tuple(p - t * 0.05), r * 1.3, 0.11, "bare", rot=along(t), verts=20, bevel=0.006)
        torus(tuple(p - t * 0.09), r * 1.3, 0.010, "bare", rot=along(t), seg=20)
        cyl(tuple(p + t * 0.005), r * 1.6, 0.04, "brass", rot=along(t), verts=6, bevel=0.0)
    return P


def mark(P, frac, mat, r, w=0.035):
    """A pipe-marking ring (round 5): a painted band round a line at frac of its length,
    the colour saying what it carries -- never blue."""
    i = max(1, min(len(P) - 2, int(frac * (len(P) - 1))))
    t = (P[i + 1] - P[i - 1]).normalized()
    cyl(tuple(P[i]), r + 0.008, w, mat, rot=along(t), verts=24, bevel=0.003)


def lagged(pts, r=0.11, bands=0.22, marks=()):
    """A lagged pipe: canvas-wrapped insulation with steel straps, flanged ends."""
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


def pipe(pts, r=0.06, mat="bare", marks=()):
    P = catmull(pts)
    sweep(P, r, mat, seg=16)
    for f, m in marks:
        mark(P, f, m, r)
    return P


def bundle(pts, cols=("red", "blue", "yellow", "black"), r=0.014):
    P = catmull(pts)
    T, N, B = frames(P)
    s = [0.0]
    for a_, b_ in zip(P, P[1:]):
        s.append(s[-1] + (b_ - a_).length)
    n = len(cols)
    for k, c in enumerate(cols):
        off = [r * 1.3 * (math.cos(2 * math.pi * k / n + 9 * s[i]) * N[i]
                          + math.sin(2 * math.pi * k / n + 9 * s[i]) * B[i]) for i in range(len(P))]
        sweep([p + o for p, o in zip(P, off)], r, "cable_" + c, seg=8)
    # round 5: cable labels, cream sleeves round the bundle every ~0.4 tile
    nxt = 0.2
    for i, p in enumerate(P):
        if s[i] >= nxt and s[i] < s[-1] - 0.1:
            cyl(tuple(p), r * 2.9, 0.045, "label", rot=along(T[i]), verts=12, bevel=0.002)
            nxt += 0.4


def bolts(cx, cy, z, R, n, r=0.022, mat="bolt"):
    for i in range(n):
        a = 2 * math.pi * i / n
        cyl((cx + R * math.cos(a), cy + R * math.sin(a), z), r, 0.025, mat, verts=6, bevel=0)


def band(x, y, z, r, h=0.07, mat="lead", lugs=2, lug_a=-math.pi / 2):
    cyl((x, y, z), r + 0.025, h, mat, verts=64)
    for i in range(lugs):
        a = lug_a + 2 * math.pi * i / lugs
        box((x + (r + 0.05) * math.cos(a), y + (r + 0.05) * math.sin(a), z), (0.06, 0.06, h + 0.05),
            "dark_steel", rz=a, bevel=0.006)


def flange_ring(x, y, z, r, mat="dark_steel", h=0.06, nb=16):
    cyl((x, y, z), r + 0.045, h, mat, verts=64)
    bolts(x, y, z + h / 2 + 0.008, r + 0.03, nb, r=0.016)


def gauge(loc, facing, r=0.07):
    """A brass-cased gauge: a cream face, a red needle."""
    t = Vector(facing).normalized()
    cyl(loc, r, 0.03, "brass", rot=along(t), verts=24, bevel=0.004)
    cyl(tuple(Vector(loc) + t * 0.017), r * 0.8, 0.006, "gauge", rot=along(t), verts=24, bevel=0)
    u = t.cross(Vector((0, 0, 1)))
    u = u.normalized() if u.length > 1e-6 else Vector((1, 0, 0))
    box(tuple(Vector(loc) + t * 0.022 + u * r * 0.2), (r * 0.9, 0.006, 0.012), "needle",
        rz=math.atan2(u.y, u.x) + 0.6, bevel=0)


def handwheel(loc, r=0.09, axis=(0, 0, 1), mat="red"):
    """A valve handwheel: red or yellow paint, worn to metal (vanilla's chemical plant)."""
    t = Vector(axis).normalized()
    torus(loc, r, 0.016, mat, rot=along(t), seg=24)
    for k in range(3):                       # spokes
        a = 2 * PI * k / 3
        o = Vector((math.cos(a), math.sin(a), 0))
        q = t.to_track_quat("Z", "Y")
        o = q @ o
        cyl(tuple(Vector(loc) + o * r / 2), 0.008, r, mat, rot=along(o), verts=6, bevel=0)
    cyl(loc, 0.022, 0.05, "bare", rot=along(t), verts=12)


def coupling(x, y, z, r, axis=(0, 0, 1), mat="brass"):
    """A free-turning six-lobed spider coupling: its own object, posed per frame."""
    root = bpy.data.objects.new("coupling", None)
    sc.collection.objects.link(root)
    root.parent = ROOT
    root.location = (x, y, z)
    root.rotation_euler = along(axis)
    cyl((0, 0, 0), r * 0.55, 0.09, "dark_steel", verts=24, parent=root)
    for i in range(6):
        a = 2 * math.pi * i / 6
        box((r * 0.7 * math.cos(a), r * 0.7 * math.sin(a), 0), (r * 0.5, r * 0.32, 0.075), mat,
            rz=a, bevel=0.006, parent=root)
    box((0, 0, 0.047), (r * 0.25, r * 1.5, 0.012), "hazard", bevel=0, parent=root)   # a stripe to see it turn
    base = root.rotation_euler.copy()

    def pose(t):
        root.rotation_euler = base
        root.rotation_euler.rotate_axis("Z", 2 * math.pi / 6 * t)
    ANIM.append(pose)
    return root


def bubbles(cx, cy, z0, z1, r, n, seed, front=True):
    """Bright bubbles rising in the gap between the fluid and the glass; each
    climbs exactly the column's height a loop, so the loop is seamless."""
    rnd = random.Random(seed)
    objs = []
    for i in range(n):
        a = (-math.pi / 2 + rnd.uniform(-1.1, 1.1)) if front else rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0.008, 0.02)
        o = sphere((0, 0, 0), rr, "bubble", seg=10)
        objs.append((o, a, rnd.random(), rr))
    H = z1 - z0

    def pose(t):
        for o, a, ph, rr in objs:
            u = (ph + t) % 1.0
            o.location = (cx + r * math.cos(a + 0.4 * math.sin(6.28 * (u + ph))),
                          cy + r * math.sin(a + 0.4 * math.sin(6.28 * (u + ph))), z0 + H * u)
    ANIM.append(pose)



def status_lamp(x, y, z):
    cyl((x, y, z), 0.045, 0.05, "dark_steel", verts=16)
    sphere((x, y, z + 0.035), 0.032, "lamp", seg=12)

# ======================================================================= round-2 kit
PI = math.pi


def valve(x, y, z=0.0, h=0.42, r=0.07, wheel="red"):
    """A standing gate valve: body, bonnet, stem and handwheel."""
    cyl((x, y, z + 0.1), r * 1.3, 0.2, "dark_steel", verts=20)
    cyl((x, y, z + 0.1 + h * 0.4), r * 0.7, h * 0.5, "bare", verts=16)
    handwheel((x, y, z + h), 0.085, mat=wheel)


def drum_ns(x, y0, y1, z, r, mat="grey", bands=(), saddles=(), band_mat="dark_steel"):
    """A drum lying north-south on saddles, with dished ends."""
    cyl((x, (y0 + y1) / 2, z), r, y1 - y0, mat, rot=(PI / 2, 0, 0), verts=48)
    for yy, s in ((y0, -1), (y1, 1)):
        h = head(x, yy, z, r, 0.13, mat)
        h.rotation_euler = (-s * PI / 2, 0, 0)
    for yy in bands:
        cyl((x, yy, z), r + 0.025, 0.07, band_mat, rot=(PI / 2, 0, 0), verts=48)
    for yy in saddles:
        box((x, yy, (z - r * 0.5) / 2 + 0.02), (r * 1.6, 0.12, z - r * 0.5 + 0.04), "dark_steel")


def drum_ew(x0, x1, y, z, r, mat="grey", bands=(), saddles=(), band_mat="dark_steel"):
    """A drum lying east-west on saddles, with dished ends."""
    cyl(((x0 + x1) / 2, y, z), r, x1 - x0, mat, rot=(0, PI / 2, 0), verts=48)
    for xx, s in ((x0, -1), (x1, 1)):
        h = head(xx, y, z, r, 0.13, mat)
        h.rotation_euler = (0, s * PI / 2, 0)
    for xx in bands:
        cyl((xx, y, z), r + 0.025, 0.07, band_mat, rot=(0, PI / 2, 0), verts=48)
    for xx in saddles:
        box((xx, y, (z - r * 0.5) / 2 + 0.02), (0.12, r * 1.6, z - r * 0.5 + 0.04), "dark_steel")


def vtank(x, y, r, h, mat="grey", bands=(), top="lead", lug_a=-PI / 2, nozzle=(0.3, 0.0), band_mat="dark_steel"):
    """A standing vessel on a cast foot ring, banded, dished head, a nozzle."""
    cyl((x, y, 0.07), r + 0.08, 0.14, "dark_steel", verts=64)
    cyl((x, y, h / 2 + 0.07), r, h - 0.14, mat, verts=64)
    for z in bands:
        band(x, y, z, r, mat=band_mat, lug_a=lug_a)
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


def pump(x, y, d=(1, 0), s=1.0, z0=0.0):
    """A pump skid along d, standing at z0: motor (olive), free coupling, volute. Returns the volute's outlet top."""
    dx, dy = d
    L, Wd = 1.05 * s, 0.55 * s
    box((x, y, z0 + 0.07), (L if dx else Wd, Wd if dx else L, 0.14), "dark_steel")
    mx, my = x - dx * 0.3 * s, y - dy * 0.3 * s
    zc = z0 + 0.14 + 0.2 * s
    box((mx, my, zc), (0.4 * s if dx else 0.38 * s, 0.38 * s if dx else 0.4 * s, 0.4 * s), "green")
    for i in range(5):
        o = 0.065 * s * (i - 2)
        box((mx + (0 if dx else o), my + (o if dx else 0), zc + 0.21 * s),
            (0.36 * s if dx else 0.025, 0.025 if dx else 0.36 * s, 0.025), "dark_steel", bevel=0)
    coupling(x, y, zc, 0.15 * s, axis=(dx, dy, 0))
    vx, vy = x + dx * 0.3 * s, y + dy * 0.3 * s
    cyl((vx, vy, zc + 0.02), 0.22 * s, 0.24 * s, "dark_steel", rot=along((dx, dy, 0)), verts=32)
    cyl((vx, vy, zc + 0.27 * s), 0.07 * s, 0.16 * s, "bare", verts=16)
    return (vx, vy, zc + 0.36 * s)


def cellbox(x, y, w, d, h, wheel=True):
    """A lead-lined cell box: the solid product's drop box."""
    box((x, y, h / 2), (w, d, h), "lead", bevel=0.02)
    box((x, y, h + 0.015), (w - 0.14, d - 0.14, 0.03), "dark_steel", bevel=0.006)
    bolts(x, y, h + 0.04, min(w, d) / 2 - 0.08, 12, r=0.014)
    box((x, y - d / 2 - 0.005, h * 0.5), (w - 0.12, 0.02, 0.1), "hazard", bevel=0)
    if wheel:
        handwheel((x, y, h + 0.1), 0.12)


def cabinet(x, y, w, d, h, mat="grey"):
    """A control cabinet: louvres, a gauge and the status lamp on the south face."""
    box((x, y, h / 2), (w, d, h), mat, bevel=0.015)
    for i in range(4):
        box((x - w * 0.15, y - d / 2 - 0.01, h * 0.35 + 0.07 * i), (w * 0.45, 0.02, 0.025), "dark_steel", bevel=0)
    gauge((x + w * 0.25, y - d / 2 - 0.01, h * 0.7), (0, -1, 0.15), r=0.06)
    status_lamp(x + w * 0.25, y - d * 0.2, h + 0.02)


def drift(path, n, seed, mat="bubble", size=(0.012, 0.024), scale=(1, 1, 1), down=False):
    """n particles moving along path(u, a), u in [0,1) a loop: each covers the whole
    path exactly once a loop, so it wraps seamlessly. a is a fixed random in [-1,1)."""
    rnd = random.Random(seed)
    objs = []
    for i in range(n):
        o = sphere((0, 0, 0), rnd.uniform(*size), mat, scale=scale, seg=8)
        objs.append((o, rnd.random(), rnd.uniform(-1, 1)))

    def pose(t):
        for o, ph, a in objs:
            u = (ph + (-t if down else t)) % 1.0
            o.location = path(u, a)
    ANIM.append(pose)


def porthole(cx, cy, z, R, ang, r, name, k=3, arms=3, spin=0.0):
    """A bolted bullseye porthole on a vessel of radius R at angle ang: cast frame,
    a glass disc, the solution behind turning in an arms-armed vortex."""
    t = Vector((math.cos(ang), math.sin(ang), 0))
    u = t.cross(Vector((0, 0, 1))).normalized()
    w = Vector((0, 0, 1))
    c = Vector((cx, cy, z)) + t * (R - 0.02)
    cyl(tuple(c + t * 0.02), r + 0.04, 0.12, "grey", rot=along(t), verts=48)           # boss
    annulus(tuple(c + t * 0.1), r - 0.01, r + 0.1, 0.06, "dark_steel", rot=along(t))
    for i in range(12):
        a = 2 * PI * i / 12
        cyl(tuple(c + t * 0.135 + (r + 0.055) * (math.cos(a) * u + math.sin(a) * w)), 0.017, 0.025, "bare",
            rot=along(t), verts=6, bevel=0)
    cyl(tuple(c + t * 0.095), r, 0.02, "pane", rot=along(t), verts=48, bevel=0)
    fl = cyl(tuple(c + t * 0.07), r, 0.02, fluid(name, "swirl", scale=1.2 / r, k=k, arms=arms), rot=along(t),
             verts=48, bevel=0)
    fl.rotation_euler.rotate_axis("Z", spin)
    box(tuple(c + t * 0.115), (0.04, 0.04, 2 * r + 0.06), "bare", rz=ang + PI / 2, bevel=0.004)   # a bar
    return c


def helix(cx, cy, R, z0, z1, turns, a0=0.0, n_per=56):
    n = int(turns * n_per)
    return [Vector((cx + R * math.cos(a0 + 2 * PI * turns * i / n), cy + R * math.sin(a0 + 2 * PI * turns * i / n),
                    z0 + (z1 - z0) * i / n)) for i in range(n + 1)]


def strips(x0, x1, y, zb, h0, amp, n, name, waves=1.5):
    """The sloshing surface seen through a flat window: n vertical strips of fluid
    whose tops ride a travelling wave, whole wavelengths a loop."""
    W = (x1 - x0) / n
    fl = fluid(name, "flow", scale=3.0, k=1)
    objs = []
    for i in range(n):
        o = box((x0 + W * (i + 0.5), y, zb + h0 / 2), (W * 1.02, 0.08, h0), fl, bevel=0)
        objs.append((o, i / n))

    def pose(t):
        for o, f in objs:
            hh = h0 - amp + amp * math.sin(2 * PI * (waves * f - t))
            s = hh / h0                      # box() bakes its location: scale about the floor zb
            o.scale = (1, 1, s)
            o.location.z = zb * (1 - s)
    ANIM.append(pose)




def deck(x0, y0, x1, y1, h=0.12, mat="dark_steel", stripe=True):
    """A low bolted plant deck under the low run (a skid, not the building's base)."""
    box(((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0, y1 - y0, h), mat, bevel=0.015)
    n = max(2, int((x1 - x0) / 0.35))
    for i in range(n + 1):
        xx = x0 + 0.06 + (x1 - x0 - 0.12) * i / n
        for yy in (y0 + 0.06, y1 - 0.06):
            cyl((xx, yy, h + 0.008), 0.018, 0.02, "bare", verts=6, bevel=0)
    if stripe:
        box(((x0 + x1) / 2, y0 - 0.004, h * 0.55), ((x1 - x0) * 0.6, 0.012, h * 0.5), "hazard", bevel=0)


def barrels(x, y, n=3, seed=0, z=0.0):
    rnd = random.Random(seed)
    for dx, dy in [(0, 0), (0.27, 0.06), (0.12, -0.23), (-0.15, -0.2), (0.4, -0.18), (-0.27, 0.05)][:n]:
        m = rnd.choice(["grey", "grey", "green", "lead", "hazard"])
        cyl((x + dx, y + dy, z + 0.19), 0.12, 0.38, m, verts=24)
        for zz in (0.1, 0.28):
            torus((x + dx, y + dy, z + zz), 0.122, 0.011, "bare", seg=24)
        cyl((x + dx + 0.05, y + dy + 0.03, z + 0.385), 0.025, 0.02, "brass", verts=8)


def jbox(x, y, w=0.32, d=0.22, h=0.4, mat="grey", z=0.0):
    box((x, y, z + h / 2), (w, d, h), mat, bevel=0.01)
    box((x, y - d / 2 - 0.01, z + h * 0.55), (w * 0.7, 0.02, h * 0.6), "dark_steel", bevel=0.004)
    cyl((x + w * 0.3, y, z + h + 0.04), 0.03, 0.08, "bare", verts=8)


def exchanger(x0, x1, y, z, r, mat="grey"):
    """A shell-and-tube exchanger on saddles: flanged channel heads and two nozzles."""
    drum_ew(x0, x1, y, z, r, mat=mat, bands=(), saddles=(x0 + 0.25, x1 - 0.25))
    for xx in (x0 + 0.08, x1 - 0.08):
        cyl((xx, y, z), r + 0.06, 0.07, "dark_steel", rot=(0, PI / 2, 0), verts=40)
        for i in range(10):
            a = 2 * PI * i / 10
            cyl((xx, y + (r + 0.035) * math.cos(a), z + (r + 0.035) * math.sin(a)), 0.014, 0.09, "bare",
                rot=(0, PI / 2, 0), verts=6, bevel=0)
    for xx in (x0 + 0.45, x1 - 0.45):
        cyl((xx, y, z + r + 0.06), 0.07, 0.14, "bare", verts=16)


def riser(x, y, z1, r=0.09, mat="bare"):
    cyl((x, y, z1 / 2), r, z1, mat, verts=20)
    for z in (0.15, z1 - 0.08):
        cyl((x, y, z), r + 0.04, 0.05, "dark_steel", verts=20)


def reel(x, y, axis=(1, 0, 0)):
    """A hose reel: two cheeks, a drum of black hose."""
    t = Vector(axis).normalized()
    box((x, y, 0.12), (0.5, 0.5, 0.24) if t.x else (0.5, 0.5, 0.24), "dark_steel")
    for s in (-1, 1):
        cyl(tuple(Vector((x, y, 0.42)) + t * 0.17 * s), 0.27, 0.03, "green", rot=along(t), verts=32)
    cyl((x, y, 0.42), 0.2, 0.3, "hose_k", rot=along(t), verts=32)
    for k in range(5):
        torus(tuple(Vector((x, y, 0.42)) + t * (-0.12 + 0.06 * k)), 0.2, 0.035, "hose_k", rot=along(t), seg=24)


# ======================================================================= round-3 kit
def arc_panel(cx, cy, r, z0, z1, a0, a1, mat, seg=24):
    """A curved sheet laid on a vessel of radius r between angles a0..a1: a
    replacement panel or a stencil field, standing just proud of the wall."""
    me = bpy.data.meshes.new("arc")
    bm = bmesh.new()
    rows = []
    for rr in (r, r + 0.012):
        ring = []
        for k in range(seg + 1):
            a = a0 + (a1 - a0) * k / seg
            ring.append((bm.verts.new((cx + rr * math.cos(a), cy + rr * math.sin(a), z0)),
                         bm.verts.new((cx + rr * math.cos(a), cy + rr * math.sin(a), z1))))
        rows.append(ring)
    inner, outer = rows
    for k in range(seg):
        bm.faces.new((outer[k][0], outer[k + 1][0], outer[k + 1][1], outer[k][1]))
        bm.faces.new((inner[k][1], inner[k + 1][1], inner[k + 1][0], inner[k][0]))
        bm.faces.new((inner[k][1], outer[k][1], outer[k + 1][1], inner[k + 1][1]))
        bm.faces.new((inner[k + 1][0], outer[k + 1][0], outer[k][0], inner[k][0]))
    for k in (0, seg):
        s = 1 if k == 0 else -1
        f = (inner[k][0], outer[k][0], outer[k][1], inner[k][1])
        bm.faces.new(f if s > 0 else tuple(reversed(f)))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("arc", me)
    sc.collection.objects.link(o)
    return _finish(o, mat, 0.004, smooth=True)


def weld_ring(cx, cy, z, r):
    torus((cx, cy, z), r + 0.004, 0.011, "seam", seg=72)


def rivet_ring(cx, cy, z, r, n, mat="bolt", rr=0.019):
    for i in range(n):
        a = 2 * PI * (i + 0.5) / n
        sphere((cx + r * math.cos(a), cy + r * math.sin(a), z), rr, mat, scale=(1, 1, 0.8), seg=8)


def vessel_band(cx, cy, z, r, n_rivets=16, lugs=3, lug_a=-PI / 2):
    """A steel band: riveted both edges, bolted lugs. Rust runs from it (the plate's drips),
    the lead's bloom hangs below it."""
    band(cx, cy, z, r, h=0.075, mat="bare", lugs=lugs, lug_a=lug_a)
    rivet_ring(cx, cy, z, r + 0.032, n_rivets)


def vertical_seams(cx, cy, r, z0, z1, angles):
    for a in angles:
        box((cx + (r + 0.004) * math.cos(a), cy + (r + 0.004) * math.sin(a), (z0 + z1) / 2),
            (0.02, 0.02, z1 - z0), "seam", rz=a, bevel=0.005)


def press(x0, x1, y, d=0.72):
    """A plate-and-frame filter press lying E-W: cast feet and rails, leaves of lead and
    plate, the hydraulic head at the east end, a drip tray below."""
    L = x1 - x0
    box(((x0 + x1) / 2, y, 0.05), (L + 0.05, d + 0.06, 0.1), "dark_steel")                      # drip tray
    for s in (-1, 1):
        box(((x0 + x1) / 2, y + s * (d / 2 - 0.03), 0.66), (L, 0.06, 0.07), "bare", bevel=0.008)  # rails
    box((x0 + 0.06, y, 0.4), (0.12, d, 0.72), "dark_steel")                                       # tail stand
    n = int((L - 0.5) / 0.1)
    for i in range(n):
        xx = x0 + 0.17 + 0.1 * i
        box((xx, y, 0.4), (0.094, d - 0.1, 0.5 + 0.02 * (i % 3 == 0)), "lead" if i % 2 else "grey",
            bevel=0.006)
    hx = x0 + 0.17 + 0.1 * n + 0.12
    box((hx, y, 0.42), (0.16, d + 0.02, 0.78), "dark_steel")                                       # head
    cyl((hx + 0.18, y, 0.45), 0.13, 0.26, "green", rot=(0, PI / 2, 0), verts=24)            # ram cylinder
    handwheel((hx + 0.34, y, 0.45), 0.14, axis=(1, 0, 0))
    box(((x0 + x1) / 2, y - d / 2 - 0.035, 0.05), (L * 0.8, 0.01, 0.06), "hazard", bevel=0)
    return hx


def stencil(loc, size, rz):
    box(loc, size, "stencil", rz=rz, bevel=0.002)


def tray(pts, w=0.16):
    """A cable tray on stand-off posts: a shallow channel, the bundle lying in it."""
    P = catmull(pts, 0.05)
    for a_, b_ in zip(P[::3], P[3::3]):
        m = (a_ + b_) / 2
        t = (b_ - a_)
        box(tuple(m), (w, t.length + 0.01, 0.02), "bare", rz=math.atan2(t.y, t.x) - PI / 2, bevel=0.003)


# ======================================================================= the circulator, round 4
# The plan (tiles, x east, y north; the footprint is +-2.5). The middle three tiles of
# every edge meet it with a wall, for the pipe pictures (template rule 6); the corners
# drop out unevenly (FFF #350): the north-west and north-east hold round vessels with
# ground round them, the south-west and south-east are ground. The mass is three piles:
# the reactor with its legs and the compressor (the centre and east), the scrubber and
# the feed drum (the west), the press house, the receiver and the pump house (the south).
RX, RY, R, H = 1.3, 0.1, 0.9, 3.05
LEGS = [(-0.32, 0.62, 2, "fl_f1"), (0.12, -0.72, -2, "fl_f2")]
Z0, Z1, LR = 0.42, 2.45, 0.27
EDGE = 2.465                     # a wall's face at the footprint edge, less a hair


def reactor():
    cyl((RX, RY, 0.08), R + 0.12, 0.16, "dark_steel", verts=72)
    bolts(RX, RY, 0.17, R + 0.07, 20, r=0.018)
    cyl((RX, RY, H / 2 + 0.08), R, H - 0.16, "lead", verts=96)
    for z in (0.5, 1.25, 2.0, 2.65):
        vessel_band(RX, RY, z, R, n_rivets=12, lug_a=-PI / 2 - 0.4)
    for z in (0.88, 1.62):
        weld_ring(RX, RY, z, R)
    vertical_seams(RX, RY, R, 0.55, 1.2, (-2.0, -0.4))
    vertical_seams(RX, RY, R, 1.3, 1.95, (-1.2, 0.6))
    arc_panel(RX, RY, R, 1.3, 1.95, -2.4, -1.75, "lead_new")
    arc_panel(RX, RY, R + 0.002, 2.08, 2.26, -1.85, -1.25, "stencil")
    # the head: lead, the agitator drive and its motor, a manway
    head(RX, RY, H, R, 0.3, "lead")
    flange_ring(RX, RY, H + 0.005, R - 0.02, mat="bare", h=0.06, nb=20)
    cyl((RX + 0.42, RY - 0.32, H + 0.26), 0.19, 0.12, "dark_steel", verts=32)
    bolts(RX + 0.42, RY - 0.32, H + 0.33, 0.15, 8, r=0.018)
    cyl((RX - 0.48, RY + 0.3, H + 0.28), 0.07, 0.18, "bare", verts=16)          # relief valve
    cyl((RX - 0.48, RY + 0.3, H + 0.39), 0.1, 0.07, "brass", verts=6, bevel=0)
    cyl((RX - 0.1, RY - 0.05, H + 0.34), 0.22, 0.18, "dark_steel", verts=32)
    coupling(RX - 0.1, RY - 0.05, H + 0.47, 0.17)
    box((RX + 0.24, RY + 0.24, H + 0.44), (0.36, 0.38, 0.32), "green", rz=0.3)
    bundle([(RX + 0.24, RY + 0.42, H + 0.47), (RX + 0.5, RY + 0.62, H + 0.1), (RX + 0.66, RY + 0.55, 2.4)],
           cols=("black", "yellow"))
    ladder(RX + 0.44, RY - R * 0.88 - 0.05, 0.2, H - 0.05, axis="x")
    gauge((RX - 0.05, RY - R - 0.02, 1.0), (0.0, -1, 0.15), r=0.08)
    # the east wall at tile 0 is the reactor's own foot; at tile +1 its side nozzle runs
    # out to the edge on a pot, at tile -1 the instrument house
    pipe([(RX + R * 0.62, RY + R * 0.75, 0.62), (2.0, 1.0, 0.62), (2.1, 1.0, 0.62)], r=0.13, mat="bare",
         marks=((0.45, "yellow"),))
    vtank(2.12, 1.02, 0.32, 1.15, "lead", bands=(0.55,), top="dark_steel", nozzle=(0.0, 0.0))
    flange_ring(1.86, 0.95, 0.62, 0.1, mat="dark_steel", h=0.04, nb=6)


def legs():
    for lx, ly, k, nm in LEGS:
        cyl((lx, ly, 0.2), LR + 0.1, 0.4, "dark_steel", verts=40)
        bolts(lx, ly, 0.41, LR + 0.06, 8, r=0.018)
        flange_ring(lx, ly, Z0 - 0.03, LR, mat="bare", h=0.06, nb=12)
        flange_ring(lx, ly, Z1 + 0.01, LR, mat="bare", h=0.06, nb=12)
        cyl((lx, ly, (Z0 + Z1) / 2), LR, Z1 - Z0, "glass", verts=48, bevel=0)
        fl = cyl((lx, ly, (Z0 + Z1) / 2), LR - 0.05, Z1 - Z0 - 0.02, fluid(nm, "flow", scale=3.2, k=k), verts=48,
                 bevel=0)
        fl.visible_diffuse = False      # the solution lights its glass, not the lead beside it
        band(lx, ly, (Z0 + Z1) / 2, LR, h=0.07, mat="bare", lugs=2, lug_a=0.3)
        for j in range(4):
            a = 2 * PI * (j + 0.5) / 4 + 0.3
            box((lx + (LR + 0.01) * math.cos(a), ly + (LR + 0.01) * math.sin(a), (Z0 + Z1) / 2),
                (0.045, 0.045, Z1 - Z0), "bare", rz=a, bevel=0.006)
        cyl((lx, ly, Z1 + 0.16), LR * 0.78, 0.24, "dark_steel", verts=32)
        head(lx, ly, Z1 + 0.28, LR * 0.78, 0.1, "lead")
    (ax, ay, _, _), (bx, by, _, _) = LEGS
    drift(lambda u, a: (ax + (LR - 0.04) * math.cos(-PI / 2 + a), ay + (LR - 0.04) * math.sin(-PI / 2 + a),
                        Z0 + 0.04 + (Z1 - Z0 - 0.08) * u), 20, 11)
    drift(lambda u, a: (bx + (LR - 0.05) * math.cos(-PI / 2 + a), by + (LR - 0.05) * math.sin(-PI / 2 + a),
                        Z0 + 0.04 + (Z1 - Z0 - 0.08) * u), 16, 12, mat="fleck", size=(0.014, 0.024),
          scale=(1.5, 1, 0.6), down=True)
    # the loop's top: fat hoses from each leg's cap into the reactor's shoulder
    hose([(ax, ay, Z1 + 0.42), (ax + 0.14, ay + 0.06, 3.0), (0.3, 0.62, 3.05), (RX - R + 0.04, RY + 0.3, 2.74)],
         r=0.13, mat="hose")
    hose([(bx, by, Z1 + 0.42), (bx + 0.16, by + 0.02, 2.95), (0.62, -0.55, 2.8),
          (RX - R * 0.62, RY - R * 0.72, 2.4)], r=0.13, mat="hose_k")
    # the loop's foot: a cast header from the reactor's foot to both legs, a valve on it
    pipe([(RX - R + 0.02, RY + 0.25, 0.3), (0.3, 0.5, 0.24), (ax + LR, ay, 0.24)], r=0.11, mat="dark_steel",
         marks=((0.5, "red"),))
    pipe([(RX - R * 0.65, RY - R * 0.7, 0.3), (0.65, -0.68, 0.24), (bx + LR, by, 0.24)], r=0.11, mat="dark_steel",
         marks=((0.5, "red"),))
    valve(0.15, 0.0, 0.0, 0.62)
    return ax, ay, bx, by


def north():
    """The north edge's wall at tiles -1, 0, +1: a low exchanger on saddles, under the
    band the north pictures draw in (behind the building). The north-west corner holds
    the scrubber, round, ground round it; the north-east the vent condenser."""
    sx, sy, sr, sh = -1.99, 1.85, 0.5, 1.85
    cyl((sx, sy, 0.07), sr + 0.08, 0.14, "dark_steel", verts=64)
    cyl((sx, sy, sh / 2 + 0.07), sr, sh - 0.14, "oxide", verts=64)
    for z in (0.95, 1.65):
        vessel_band(sx, sy, z, sr, n_rivets=9, lugs=2, lug_a=-PI / 4)
    head(sx, sy, sh, sr, 0.2, "oxide")
    nx, ny = sx + 0.16, sy - 0.16
    cyl((nx, ny, sh + 0.2), 0.09, 0.16, "bare", verts=24)
    flange_ring(nx, ny, sh + 0.28, 0.08, mat="bare", h=0.04, nb=6)
    arc_panel(sx, sy, sr + 0.002, 1.18, 1.32, -1.6, -0.9, "stencil")
    tx, ty = 2.04, 1.92
    vtank(tx, ty, 0.4, 1.75, "copper", bands=(0.7, 1.35), top="dark_steel", nozzle=None)
    cyl((tx - 0.1, ty - 0.06, 1.98), 0.06, 0.28, "copper", verts=16)
    torus((tx - 0.1, ty - 0.06, 2.12), 0.07, 0.02, "copper", seg=16)
    exchanger(-1.55, 1.55, 2.14, 0.38, 0.3, mat="grey")
    stencil((0.15, 1.81, 0.52), (0.5, 0.01, 0.12), 0.0)
    # the crust-gas compressor, low, behind the legs
    box((0.35, 1.36, 0.08), (1.05, 0.52, 0.16), "dark_steel")
    cyl((0.15, 1.36, 0.4), 0.24, 0.48, "dark_steel", rot=(0, PI / 2, 0), verts=32)
    for i in range(4):
        cyl((-0.03 + 0.12 * i, 1.36, 0.4), 0.265, 0.03, "bare", rot=(0, PI / 2, 0), verts=32, bevel=0)
    box((0.66, 1.36, 0.38), (0.38, 0.4, 0.42), "green")
    coupling(0.42, 1.36, 0.38, 0.12, axis=(1, 0, 0))
    hose([(0.15, 1.36, 0.66), (0.08, 1.05, 0.98), (LEGS[0][0] + 0.2, LEGS[0][1] + 0.2, 1.25)], r=0.1, mat="hose")
    # the scrubber's line, high, into the reactor head
    hose([(nx, ny, sh + 0.32), (-1.3, 1.35, 2.35), (-0.4, 1.12, 2.8), (0.6, 0.85, 3.12),
          (RX - 0.25, RY + 0.42, 3.22)], r=0.12, mat="hose")
    hose([(1.35, 2.08, 0.78), (1.6, 1.42, 1.12), (RX + 0.3, RY + R - 0.02, 1.25)], r=0.1, mat="hose_k")
    pipe([(tx - 0.32, ty - 0.12, 0.9), (1.88, 1.25, 0.95), (RX + 0.45, RY + R * 0.75, 0.95)], r=0.07, mat="copper")


def west():
    """The feed drum lying north-south: the west wall at tiles -1, 0, +1. Its south head
    stops short of the corner, and its north end runs into the scrubber's foot."""
    drum_ns(-1.97, -1.5, 1.12, 0.6, 0.5, mat="ochre", bands=(-0.75, 0.45), saddles=(-1.0, 0.7))
    box((-1.9, -0.1, 1.1), (0.34, 0.4, 0.07), "green")
    stencil((-1.46, -0.15, 0.66), (0.01, 0.55, 0.15), 0.0)
    gauge((-1.47, 0.3, 0.8), (1, 0, 0.3), r=0.08)
    ax, ay = LEGS[0][0], LEGS[0][1]
    hose([(-1.5, 0.38, 0.5), (-1.0, 0.3, 0.36), (ax - LR - 0.08, ay - 0.08, 0.3)], r=0.11, mat="hose")
    # a dosing pump between the drum and the riser, olive, on its skid
    skid(-1.42, -0.05, -0.62, 0.32, 0.1)
    box((-1.2, 0.13, 0.3), (0.34, 0.3, 0.3), "green")
    cyl((-0.85, 0.13, 0.28), 0.14, 0.22, "dark_steel", rot=(0, PI / 2, 0), verts=24)
    coupling(-1.0, 0.13, 0.28, 0.09, axis=(1, 0, 0))
    hose([(-0.85, 0.13, 0.45), (-0.62, 0.3, 0.7), (ax - 0.18, ay - 0.2, 0.62)], r=0.06, mat="hose_k")
    # the scrubber's drain header, on its skid behind the make-up pot
    skid(-1.5, 1.12, -0.5, 1.76, 0.12)
    lagged([(-1.5, 1.46, 0.36), (-1.0, 1.42, 0.38), (-0.52, 1.36, 0.36)], r=0.13,
           marks=((0.62, "green"),))
    valve(-0.75, 1.62, 0.12, 0.5, wheel="yellow")
    # the settling pot between the drum and the downcomer: the hollow filled with one mass
    vtank(-0.92, -0.92, 0.44, 1.4, "lead", bands=(0.6, 1.05), top="dark_steel", nozzle=(0.3, 0.3))
    hose([(-0.92 + 0.13, -0.92 + 0.13, 1.72), (-0.55, -0.7, 1.9), (LEGS[1][0] - LR - 0.02, LEGS[1][1] + 0.05, 1.7)],
         r=0.1, mat="hose")
    hose([(-1.5, -0.95, 0.45), (-1.3, -1.25, 0.3), (-0.92, -1.42, 0.3)], r=0.09, mat="hose_k")
    # the feed main from the drum to the riser's foot, lagged, a valve station on it
    lagged([(-1.48, 0.95, 0.42), (-1.05, 0.95, 0.45), (-0.62, 0.85, 0.4), (LEGS[0][0] - LR, LEGS[0][1] + 0.05, 0.32)],
           r=0.11, marks=((0.3, "green"), (0.62, "yellow")))
    # the make-up pot over the feed main, olive-banded lead: the hollow behind the dosing pump
    vtank(-1.02, 0.62, 0.3, 1.05, "cream", bands=(0.5,), top="dark_steel", nozzle=(0.2, -0.3))
    hose([(-1.02 + 0.06, 0.62 - 0.09, 1.35), (-0.8, 0.5, 1.5), (LEGS[0][0] - LR - 0.02, LEGS[0][1] - 0.05, 1.45)],
         r=0.08, mat="hose_k")
    bundle([(-1.42, -0.62, 0.4), (-1.0, -0.55, 0.14), (-0.5, -0.2, 0.14), (LEGS[1][0] - 0.3, LEGS[1][1], 0.3)],
           cols=("red", "black", "grey"))


def skid(x0, y0, x1, y1, h, mat="dark_steel"):
    box(((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0, y1 - y0, h), mat, bevel=0.012)
    for xx in (x0 + 0.06, x1 - 0.06):
        for yy in (y0 + 0.06, y1 - 0.06):
            cyl((xx, yy, h + 0.008), 0.022, 0.02, "bare", verts=6, bevel=0)


def south():
    """Three masses meeting the south edge: the press house at tile -1 (the filter press
    on its lead-lined drop box: the solid out), the filtrate receiver at tile 0 (the
    output's wall: its picture stands on the receiver's flank), the pump house at +1.
    The south-west and south-east corners are ground."""
    bx, by = LEGS[1][0], LEGS[1][1]
    # the drop box, lead-lined, with the press standing on it
    box((-1.02, -1.98, 0.27), (0.98, 0.9, 0.54), "lead", bevel=0.025)
    box((-1.02, -2.43 - 0.005, 0.27), (0.8, 0.02, 0.12), "hazard", bevel=0)
    cyl((-1.02, -1.98, 0.56), 0.36, 0.04, "dark_steel", verts=32)
    L0, L1, yp, d = -1.42, -0.62, -1.98, 0.66
    for s_ in (-1, 1):
        box(((L0 + L1) / 2, yp + s_ * (d / 2 - 0.03), 1.18), (L1 - L0, 0.07, 0.08), "bare", bevel=0.01)
    box((L0 + 0.06, yp, 0.9), (0.12, d, 0.7), "dark_steel")
    for i in range(5):
        box((L0 + 0.2 + 0.1 * i, yp, 0.9), (0.09, d - 0.08, 0.56), "lead" if i % 2 else "cream", bevel=0.01)
    box((L1 - 0.1, yp, 0.92), (0.18, d + 0.04, 0.76), "dark_steel")
    cyl((L1 + 0.08, yp, 0.95), 0.14, 0.2, "green", rot=(0, PI / 2, 0), verts=24)
    handwheel((L1 + 0.22, yp, 0.95), 0.15, axis=(1, 0, 0), mat="yellow")
    # the filtrate receiver: lying east-west on saddles, its flank at the edge
    skid(-0.58, -2.46, 0.66, -1.6, 0.12)
    drum_ew(-0.55, 0.62, -2.04, 0.58, 0.4, mat="green", bands=(-0.25, 0.3), saddles=(-0.35, 0.42))
    stencil((0.05, -2.43, 0.62), (0.36, 0.01, 0.1), 0.0)
    hose([(L1 - 0.1, yp + 0.2, 1.32), (-0.35, -1.55, 1.2), (-0.1, -1.75, 0.95)], r=0.1, mat="hose_k")
    # the pump house: the motor olive, it lifts the downcomer's return
    box((1.12, -1.98, 0.42), (0.86, 0.92, 0.84), "cream", bevel=0.025)
    for i in range(4):
        box((0.9, -2.445, 0.3 + 0.1 * i), (0.36, 0.02, 0.035), "dark_steel", bevel=0)
    gauge((1.35, -2.45, 0.62), (0, -1, 0.15), r=0.07)
    status_lamp(1.42, -2.2, 0.86)
    pv = pump(1.1, -1.9, (-1, 0), 0.75, z0=0.84)
    hose([pv, (0.7, -1.55, 1.45), (0.4, -1.25, 1.25), (bx + 0.1, by - LR - 0.04, 0.9)], r=0.12, mat="hose")
    # under the legs, west of the downcomer: the sampling cabinet, where the precipitate is drawn off
    box((-0.38, -0.5, 0.38), (0.44, 0.42, 0.76), "oxide", bevel=0.02)
    box((-0.38, -0.72, 0.42), (0.3, 0.02, 0.36), "dark_steel", bevel=0.004)
    gauge((-0.26, -0.73, 0.62), (0, -1, 0.2), r=0.06)
    hose([(-0.38, -0.5, 0.8), (-0.2, -0.62, 1.0), (LEGS[1][0] - LR - 0.02, LEGS[1][1] + 0.08, 1.05)], r=0.05,
         mat="cable_black")
    # between the legs' feet and the south units: the sampling manifold, low, its valves
    skid(-0.48, -1.55, 0.62, -1.1, 0.14)
    cyl((0.07, -1.32, 0.32), 0.15, 0.95, "dark_steel", rot=(0, PI / 2, 0), verts=24)
    for xx, wh in ((-0.3, "red"), (0.07, "yellow"), (0.42, "red")):
        valve(xx, -1.32, 0.3, 0.45, wheel=wh)
    bundle([(1.42, -1.6, 0.85), (1.6, -1.2, 0.2), (RX + R * 0.55, RY - R * 0.75, 0.45)],
           cols=("red", "yellow", "black"))


def east():
    """The east edge: the instrument house at tile -1, the reactor's foot at 0, the side
    nozzle's pot at +1 (reactor()). The south-east corner is ground."""
    box((2.1, -1.0, 0.65), (0.66, 0.84, 1.3), "grey", bevel=0.025)
    for i in range(4):
        box((2.1, -1.43, 0.45 + 0.08 * i), (0.4, 0.02, 0.03), "dark_steel", bevel=0)
    gauge((1.76, -0.85, 0.95), (-1, -0.2, 0.2), r=0.07)
    status_lamp(2.2, -0.9, 1.32)
    bundle([(2.0, -0.6, 1.2), (1.95, -0.3, 0.3), (RX + R * 0.8, RY - R * 0.5, 0.35)], cols=("grey", "red"))


# ======================================================================= round 5: the details
# Small surface detail only: the model (shape, layout, pipe pictures, silhouette) is
# approved as round 4 left it. Each piece sits on a surface the camera sees (south-facing
# walls and the tops) and none changes the outline.
def on_wall(cx, cy, r, ang, z, out=0.0):
    """A point on a standing vessel's wall at angle ang, height z, `out` proud of it;
    and the outward normal."""
    n = Vector((math.cos(ang), math.sin(ang), 0))
    return Vector((cx, cy, z)) + n * (r + out), n


def insp_plate(cx, cy, r, ang, z0, z1, half, mat="bare", nb=3):
    """A bolted inspection plate on a vessel: a curved cover, a bolt row down each side
    and along top and bottom."""
    arc_panel(cx, cy, r + 0.004, z0, z1, ang - half, ang + half, mat)
    for a in (ang - half * 0.82, ang + half * 0.82):
        for k in range(nb):
            p, n = on_wall(cx, cy, r, a, z0 + (z1 - z0) * (k + 0.5) / nb, 0.018)
            cyl(tuple(p), 0.014, 0.018, "bolt", rot=along(n), verts=6, bevel=0)
    for zz in (z0 + 0.025, z1 - 0.025):
        for k in range(3):
            p, n = on_wall(cx, cy, r, ang - half * 0.4 + half * 0.4 * k, zz, 0.018)
            cyl(tuple(p), 0.014, 0.018, "bolt", rot=along(n), verts=6, bevel=0)


def rivet_column(cx, cy, r, ang, z0, z1, step=0.075):
    """A riveted vertical seam: a strap and a row of rivet heads (the foundry's panels)."""
    vertical_seams(cx, cy, r, z0, z1, (ang,))
    n = int((z1 - z0) / step)
    for k in range(n + 1):
        p, _ = on_wall(cx, cy, r, ang, z0 + step * k, 0.016)
        sphere(tuple(p), 0.016, "bolt", scale=(1, 1, 0.8), seg=8)


def flat_plate(loc, w, h, face="S", mat="bare", bolts_=True):
    """A bolted plate on a flat south (or top) face."""
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
    """An identification plate, no text: a cream field, a coloured band across it, four
    corner screws."""
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


def weld_ring_x(x, y, z, r):
    torus((x, y, z), r + 0.004, 0.01, "seam", rot=(0, PI / 2, 0), seg=64)


def weld_ring_y(x, y, z, r):
    torus((x, y, z), r + 0.004, 0.01, "seam", rot=(PI / 2, 0, 0), seg=64)


def manway_top(x, y, z, r=0.13, nb=10):
    """A bolted manway cover on a top: a disc, its bolt ring, a lifting handle."""
    cyl((x, y, z + 0.015), r, 0.03, "bare", verts=32, bevel=0.004)
    bolts(x, y, z + 0.035, r - 0.025, nb, r=0.012)
    torus((x, y, z + 0.05), 0.04, 0.008, "yellow", rot=(PI / 2, 0, 0), seg=16)


OIL = bpy.data.materials.new("oil")
OIL.use_nodes = True
M["oil"] = OIL


def _oil_material():
    """Oil and wet dirt on the ground: a dark, slightly glossy film whose coverage is a
    broken noise inside an elliptical falloff -- at most 45 % opaque, so the plate's
    outline (alpha over 128) is not changed by it."""
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


_oil_material()
STAINS = []


def stain(x, y, rx, ry, rz=0.0):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, 0.004), rotation=(0, 0, rz))
    o = bpy.context.active_object
    o.scale = (rx * 2, ry * 2, 1)
    bpy.ops.object.transform_apply(scale=True)
    o.visible_shadow = False
    STAINS.append(o)
    return _finish(o, "oil", 0)


def details():
    # ---- the reactor (lead): a bolted inspection plate low on its front, a hazard tag and
    # an ID plate under the stencil, a rivet column on the replacement sheet's edge
    insp_plate(RX, RY, R, -2.12, 0.62, 0.98, 0.22, mat="lead_new")
    p, _ = on_wall(RX, RY, R, -1.55, 2.4, 0.0)
    hazard_tag((p.x, p.y - 0.004, 2.4), 0.22, 0.07)
    rivet_column(RX, RY, R, -2.42, 1.32, 1.93)
    rivet_column(RX, RY, R, -1.73, 1.32, 1.93)
    p, _ = on_wall(RX, RY, R, -1.3, 1.68, 0.0)
    gauge((p.x, p.y - 0.02, 1.68), (0.35, -1, 0.15), r=0.065)
    # ---- the scrubber (oxide red): riveted panel seams, weld rings, an inspection plate,
    # a gauge, a red pipe-marking band on its nozzle
    sx, sy, sr = -1.99, 1.85, 0.5
    for a in (-2.15, -1.05):
        rivet_column(sx, sy, sr, a, 1.0, 1.6)
    weld_ring(sx, sy, 1.3, sr)
    insp_plate(sx, sy, sr, -2.45, 1.12, 1.5, 0.3, mat="bare")
    p, _ = on_wall(sx, sy, sr, -0.75, 1.42, 0.0)
    gauge((p.x, p.y - 0.01, 1.42), (0.6, -1, 0.15), r=0.06)
    cyl((sx + 0.16, sy - 0.16, 1.95), 0.098, 0.04, "red", verts=24, bevel=0.003)
    # ---- the feed drum (ochre): weld rings round it, a longitudinal weld bead, a bolted
    # manway on top, an ID plate and a hazard tag on its flank
    for yy in (-0.2, 0.92):
        weld_ring_y(-1.97, yy, 0.6, 0.5)
    box((-1.97 + 0.2, -0.2, 0.6 + 0.46), (0.018, 2.4, 0.018), "seam", bevel=0.004)
    manway_top(-1.97, -1.12, 1.1)
    id_panel((-1.97, -1.69, 0.66), 0.22, 0.14, stripe="green")
    # ---- the make-up pot (cream): a gauge and a red ID band
    cyl((-1.02, 0.62, 0.86), 0.31, 0.05, "red", verts=40, bevel=0.003)
    p, _ = on_wall(-1.02, 0.62, 0.3, -1.9, 0.62, 0.0)
    gauge((p.x, p.y - 0.01, 0.62), (-0.4, -1, 0.15), r=0.05)
    # ---- the settling pot (lead): a manway on its head
    manway_top(-0.92 - 0.14, -0.92 - 0.1, 1.4 + 0.1, r=0.1, nb=8)
    # ---- the vent condenser (copper): rivet columns, an ID plate on its band
    for a in (-2.0, -1.0):
        rivet_column(2.04, 1.92, 0.4, a, 0.2, 0.65)
        rivet_column(2.04, 1.92, 0.4, a, 0.78, 1.3)
    p, _ = on_wall(2.04, 1.92, 0.4, -1.55, 1.04, 0.0)
    gauge((p.x, p.y - 0.01, 1.04), (0, -1, 0.15), r=0.06)
    # ---- the receiver (green): weld rings, a manway on top, a hazard tag on its west head side
    for xx in (-0.02, 0.48):
        weld_ring_x(xx, -2.04, 0.58, 0.4)
    manway_top(0.32, -2.0, 0.98, r=0.11, nb=8)
    # ---- the pump house (cream): a riveted top edge, a hazard tag, an ID plate, a bolted
    # inspection plate
    for k in range(11):
        cyl((0.74 + 0.077 * k, -2.452, 0.79), 0.013, 0.014, "bolt", rot=(PI / 2, 0, 0), verts=6, bevel=0)
    hazard_tag((1.42, -2.44, 0.3), 0.18, 0.12)
    id_panel((1.15, -2.44, 0.2), 0.2, 0.12, stripe="red")
    # ---- the instrument house (grey): a hazard band, an ID plate, a bolted plate
    hazard_tag((2.1, -1.425, 1.16), 0.56, 0.06)
    id_panel((1.92, -1.425, 0.95), 0.2, 0.13, stripe="yellow")
    flat_plate((2.28, -1.425, 0.86), 0.18, 0.2, mat="bare")
    # ---- the sampling cabinet (oxide): an ID plate on its top
    id_panel((-0.38, -0.5, 0.76), 0.26, 0.16, stripe="yellow", face="T")
    # ---- the press: a hazard tag on the head
    hazard_tag((-0.72, -2.335, 1.12), 0.14, 0.06)
    # ---- the compressor (dark steel, green motor): a gauge on its casing
    gauge((0.15, 1.1, 0.5), (0, -1, 0.3), r=0.055)
    # ---- oil and wet dirt on the ground at the feet: under the pumps and the press, at
    # the reactor's foot, the legs' feet, the drum's saddles
    stain(1.05, -2.42, 0.42, 0.14, 0.1)
    stain(-1.0, -2.45, 0.5, 0.12, -0.05)
    stain(2.3, -1.52, 0.22, 0.12)
    stain(1.55, -0.95, 0.3, 0.25)
    stain(-0.5, -1.62, 0.35, 0.12)
    stain(-1.65, -1.6, 0.25, 0.15)
    stain(-2.2, -1.0, 0.15, 0.3)
    stain(2.3, 0.4, 0.15, 0.3)
    stain(1.85, -1.95, 0.32, 0.22, 0.4)
    stain(-1.95, -2.05, 0.28, 0.2, -0.3)
    stain(-0.2, -2.42, 0.3, 0.1)


reactor()
legs()
north()
west()
south()
east()
details()

# ---------------------------------------------------------------- the pipe pictures (--ports)
#
# Template rules 6 and 7, as the Ballast Drill builds them (concept/ballast-drill/model/
# ballast_drill.py, fitting()): assembler 3's picture for each face, rendered in this
# plant's own steel -- a backplate traced from assembler 3's pixels (alpha over 127), laid
# where the engine draws each one, and on it a flanged stub on the vanilla pipe's
# centreline out to where the pipe's bolted end ring lands. One picture per face: facing
# north the inputs are at tiles -1 and +1 on the north face and the output at 0 on the
# south; turned, the same pictures land on every face. port-<face> is open (a dark bore),
# cover-<face> the same fitting capped, for pack_ports.py; the covers the prototype will
# use are vanilla's (pipecoverspictures()), as the sheets draw them.
VANILLA = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity/assembling-machine-3")
H_AXIS_V = 1.0 / 64          # horizontal pipe: axis, screen tiles above its tile's centre
V_AXIS_U = 0.5 / 64          # vertical pipe: axis, screen tiles right of its tile's centre
H_RING_R = 26 / 64 / 1.118
V_RING_R = 25.5 / 64
ZA = 0.42                    # the stubs' axis height, as the drill's
HC = 0.85                    # the south wall's height there (the receiver's top, the houses' roofs)
E5 = 2.495                   # the wall's face: the footprint edge, less a hair
DECL = dict(footprint=(5, 5), directions="four", passes=[], animations=[],
            ports=[dict(tile=(-1, -2), face="N"), dict(tile=(2, -1), face="E"),
                   dict(tile=(0, 2), face="S"), dict(tile=(-2, 0), face="W", neck=True)])
GROUPS = {}


def vanilla_mask(face, tile):
    """Assembler 3's picture for `face`: its drawn pixels (i, j), and the screen px of
    its top-left from the origin, drawn from the tile the port at `tile` points into.
    Closed by a pixel, as the drill's, so the west picture's thin strip stays joined."""
    stem = os.path.join(VANILLA, f"assembling-machine-3-pipe-{face}")
    bx, by = (float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)",
                                           open(stem + ".lua").read()).groups())
    img = bpy.data.images.load(stem + ".png", check_existing=True)
    w, h = img.size
    px = list(img.pixels)
    drawn = {(i, j) for j in range(h) for i in range(w) if px[((h - 1 - j) * w + i) * 4 + 3] > 127 / 255}
    n8 = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)]
    grown = {(i + a, j + b) for i, j in drawn for a, b in n8}
    drawn = {(i, j) for i, j in grown if all((i + a, j + b) in grown for a, b in n8)} | drawn
    dx, dy = contract.FACES[face]
    tx, ty = tile[0] + dx, tile[1] + dy
    return drawn, (tx + bx / 32) * 64 - w / 2, (ty + by / 32) * 64 - h / 2


def slab(face, tile, lift, mat="slab"):
    drawn, x0, y0 = vanilla_mask(face, tile)
    me = bpy.data.meshes.new(f"slab-{face}")
    bm = bmesh.new()
    corners = {}

    def corner(i, j):
        if (i, j) not in corners:
            corners[(i, j)] = bm.verts.new(lift((x0 + i) / 64, -(y0 + j) / 64))
        return corners[(i, j)]
    for i, j in drawn:
        bm.faces.new((corner(i, j + 1), corner(i + 1, j + 1), corner(i + 1, j), corner(i, j)))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(f"slab-{face}", me)
    sc.collection.objects.link(o)
    return _finish(o, mat, 0)


def rivet(loc, r=0.017):
    return sphere(loc, r, "bolt", scale=(1, 1, 0.7), seg=8)


def nut(loc, r, h, rot):
    o = cyl(loc, r, h, "bare", rot=rot, verts=6, bevel=0)
    o.rotation_euler.rotate_axis("Z", random.uniform(0, PI / 3))
    return o


def fitting(p, cap):
    face, tile = p["face"], p["tile"]
    g = f"{'cover' if cap else 'port'}-{face}"
    first = len(OBJS)
    cx, cy = tile[0], -tile[1]
    if face == "S":
        yw = -(E5 + 0.035)

        def lift(u, v):                      # the wall's plane; above it, back over the top
            z = 2 * (v - yw)
            return Vector((u, yw, z)) if z <= HC else Vector((u, yw + (v - yw - HC / 2), HC + 0.004))
        slab(face, tile, lift, "green")     # the receiver's own green shell, the wall it stands in
        ax = (PI / 2, 0, 0)
        x = cx + V_AXIS_U
        for k in range(11):                  # a bolt row along the plate's top edge, and down its sides
            rivet((x - 0.36 + 0.072 * k, yw - 0.012, HC - 0.06))
        for z in (0.12, 0.42, 0.7):
            for sx_ in (-0.39, 0.39):
                rivet((x + sx_, yw - 0.012, z))
        for k in range(11):                  # and round the cover plate the wall's top folds into
            rivet((x - 0.34 + 0.068 * k, yw + 0.33, HC + 0.012))
        for k in range(1, 5):
            for sx_ in (-0.39, 0.39):
                rivet((x + sx_, yw + 0.07 * k, HC + 0.012))
        box((x, yw + 0.17, HC + 0.006), (0.7, 0.012, 0.012), "seam", bevel=0)
        ye = -2.53 - ZA / 2                  # the end ring widest 0.47 above the outside tile's centre
        annulus((x, yw - 0.03, ZA), 0.3, 0.42, 0.05, "bare", rot=ax)                        # wall flange
        for k in range(14):
            t = 2 * PI * k / 14
            rivet((x + 0.37 * math.cos(t), yw - 0.06, ZA + 0.37 * math.sin(t)), 0.016)
        cyl((x, (yw + ye) / 2, ZA), 0.28, abs(ye - yw), "bare", rot=ax, verts=48, bevel=0.0)
        cyl((x, ye + 0.03, ZA), V_RING_R - 0.02, 0.06, "bare", rot=ax, verts=48, bevel=0.01)
        for k in range(8):
            t = 2 * PI * (k + 0.5) / 8
            nut((x + 0.33 * math.cos(t), ye - 0.002, ZA + 0.33 * math.sin(t)), 0.02, 0.014, ax)
        cyl((x, ye - 0.003, ZA), 0.2 if not cap else V_RING_R - 0.06, 0.006, "dark" if not cap else "bare",
            rot=ax, verts=32, bevel=0.0)
    elif face == "N":
        yw = E5 + 0.035

        def lift(u, v):                      # behind the building, on the north wall's plane
            return Vector((u, yw, 2 * (v - yw)))
        slab(face, tile, lift, "dark_steel")
        for k in range(7):                   # the flange's bolts, round its upper half, inside the outline
            t = 0.35 + (PI - 0.7) * k / 6
            u, v = cx + V_AXIS_U + 0.3 * math.cos(t), 2.5 + 0.2 * math.sin(t)
            rivet((u, yw - 0.015, 2 * (v - yw)), 0.016)
    else:
        sgn = 1 if face == "E" else -1
        x0 = sgn * 2.22                      # the neck's root, where the plane leans out from (as VF's)

        def lift(u, v):                      # edge-on to the camera: a plane leaning out from the wall
            z = ZA - sgn * 1.6 * (u - x0)
            return Vector((u, v - z / 2, z))
        slab(face, tile, lift, "dark_steel")
        ya = cy + H_AXIS_V - ZA / 2
        ax = (0, PI / 2, 0)
        xf = sgn * (2.5 - 0.03)
        cyl(((x0 + xf) / 2, ya, ZA), 0.24, abs(xf - x0), "bare", rot=ax, verts=48, bevel=0.0)     # neck
        cyl((xf, ya, ZA), H_RING_R - 0.02, 0.045, "bare", rot=ax, verts=48, bevel=0.006)
        for k in range(8):
            t = 2 * PI * (k + 0.5) / 8
            nut((xf - sgn * 0.025, ya + 0.27 * math.cos(t), ZA + 0.27 * math.sin(t)), 0.018, 0.012, ax)
    GROUPS[g] = OBJS[first:]


# ---------------------------------------------------------------- lights, passes
SUN = rig.sun(SUN_E)
SUN.data.color = (1.0, 0.94, 0.82)     # a warm white: vanilla's highlights are cream (the study's lightW)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.24

if COLMAP:
    # the colour map: every part in its palette group's flat key colour, unlit
    import json
    flat = {}
    for o in OBJS:
        for i, m in enumerate(o.data.materials):
            grp, hexc = GROUP.get(m.name, ("glass and the solution", "#3070FF") if m.name.startswith("fl_")
                                  else ("(unassigned)", "#FF00FF"))
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
    sc.cycles.samples = 16
    rig.camera(*CANVAS, centre_px=CENTRE, ss=SSK)
    rig.render(os.path.join(OUT, "colourmap.png"))
    groups = {}
    for k, (grp, hexc) in GROUP.items():
        groups.setdefault(grp, hexc)
    json.dump(groups, open(os.path.join(OUT, "colourmap.json"), "w"), indent=1)
    print("done")
    sys.exit(0)

if PORTS:
    random.seed(4)
    BODY = list(OBJS)
    for p_ in DECL["ports"]:
        fitting(p_, cap=False)
        fitting(p_, cap=True)
    BOUNCE = rig.bounce_ground()
    contract.declare(OUT, canvas=PORT_CANVAS, **DECL)
    rig.camera(*PORT_CANVAS, ss=SSK)
    for f in "NESW":
        for kind in ("port", "cover"):
            show = set(map(id, GROUPS[f"{kind}-{f}"]))
            for o in OBJS:
                o.hide_render = id(o) not in show
            rig.render(os.path.join(OUT, f"{kind}-{f}.png"))
    print("done")
    sys.exit(0)

rig.camera(*CANVAS, centre_px=CENTRE, ss=SSK)
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()


def pose(t):
    for p in ANIM:
        p(t)
    for node, k in PHASES:
        node.outputs[0].default_value = 2 * math.pi * k * t


def working(on):
    for sock, v in GLOWS:
        sock.default_value = v if on else 0.0
    LAMP_ON.default_value = 3.0 if on else 0.0


if ONLY in (None, "idle"):
    pose(0.0)
    working(False)
    rig.render(os.path.join(OUT, "idle.png"))
    GROUND.hide_render = True
    rig.render(os.path.join(OUT, "plate.png"))
    working(True)
    rig.render(os.path.join(OUT, "plate-working.png"))
    GROUND.hide_render = False
if ONLY in (None, "working"):
    working(True)
    for f in range(NF):
        pose(f / NF)
        rig.render(os.path.join(OUT, f"working-{f:02d}.png"))
print("done")
