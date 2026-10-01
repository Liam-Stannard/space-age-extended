"""Layered industrial finish, shared by every building.

Why layers: vanilla's finish is not one colour with noise on it. Looked at closely
(assembling machine 3 at 4x) every pixel differs, and the variation comes from
distinct physical layers, each with its own mask:

  paint      the base colour, jittered per part so no two plates match
  bare metal where paint has worn through: on edges, and in patches; brighter,
             more metallic and smoother, so it catches the sun as highlights
  rust       in cavities and in streaks running down vertical faces
  dust       settled on upward faces, broken up by noise
  grime      darkest in contact lines and recesses (ambient occlusion)
  grain      photo-scanned structure (see TEX below), or the building's own
             concept swatch, so nothing renders as a gradient

All masks are driven by world position so a pattern runs continuously across
neighbouring parts instead of restarting on each rivet. Scales are per tile
(one Blender unit): at 64 px per tile, anything finer than ~60 is sub-pixel and
only survives because the render is supersampled.
"""
import os

import bpy

import rig

# Photo-scanned structure (ambientCG, CC0), baked to greyscale masks by
# textures/bake_masks.py: only the PATTERN is taken from the photos -- where paint
# has chipped to rust, where it is scratched, how it streaks -- never the
# colour, which stays the spec palette.
TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures")


class _G:
    """Tiny helper around a node tree, to keep the graph readable."""

    def __init__(self, mat):
        self.n = mat.node_tree.nodes
        self.l = mat.node_tree.links

    def node(self, kind, **inputs):
        nd = self.n.new(kind)
        for k, v in inputs.items():
            if isinstance(v, bpy.types.NodeSocket):
                self.l.new(v, nd.inputs[k])
            else:
                nd.inputs[k].default_value = v
        return nd

    def math(self, op, a, b=None, clamp=False):
        nd = self.n.new("ShaderNodeMath")
        nd.operation = op
        nd.use_clamp = clamp
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, bpy.types.NodeSocket):
                self.l.new(v, nd.inputs[i])
            else:
                nd.inputs[i].default_value = v
        return nd.outputs[0]

    def remap(self, v, lo, hi, to_lo=0.0, to_hi=1.0):
        nd = self.node("ShaderNodeMapRange", Value=v)
        nd.inputs["From Min"].default_value = lo
        nd.inputs["From Max"].default_value = hi
        nd.inputs["To Min"].default_value = to_lo
        nd.inputs["To Max"].default_value = to_hi
        return nd.outputs[0]

    def noise(self, vec, scale, detail=4.0, rough=0.55, distortion=0.0):
        nd = self.node("ShaderNodeTexNoise", Vector=vec, Scale=scale, Detail=detail,
                       Roughness=rough, Distortion=distortion)
        return nd.outputs["Fac"]

    def mixc(self, fac, a, b):
        """Colour mix; a and b are sockets or RGBA tuples."""
        nd = self.n.new("ShaderNodeMix")
        nd.data_type = "RGBA"
        for idx, v in ((0, fac), (6, a), (7, b)):
            if isinstance(v, bpy.types.NodeSocket):
                self.l.new(v, nd.inputs[idx])
            else:
                nd.inputs[idx].default_value = v
        return nd.outputs[2]

    def mixf(self, fac, a, b):
        nd = self.n.new("ShaderNodeMix")
        nd.data_type = "FLOAT"
        for idx, v in ((0, fac), (2, a), (3, b)):
            if isinstance(v, bpy.types.NodeSocket):
                self.l.new(v, nd.inputs[idx])
            else:
                nd.inputs[idx].default_value = v
        return nd.outputs[0]

    def mulc(self, col, fac):
        nd = self.n.new("ShaderNodeMix")
        nd.data_type = "RGBA"
        nd.blend_type = "MULTIPLY"
        nd.inputs[0].default_value = 1.0
        for idx, v in ((6, col), (7, fac)):
            if isinstance(v, bpy.types.NodeSocket):
                self.l.new(v, nd.inputs[idx])
            else:
                nd.inputs[idx].default_value = v
        return nd.outputs[2]

    def image(self, path, vec, scale, data=True):
        """Box-projected image, so it wraps any part without UVs."""
        img = bpy.data.images.load(path, check_existing=True)
        if data:
            img.colorspace_settings.name = "Non-Color"
        mp = self.node("ShaderNodeMapping", Vector=vec)
        mp.inputs["Scale"].default_value = (scale, scale, scale)
        nd = self.n.new("ShaderNodeTexImage")
        nd.image = img
        nd.projection = "BOX"
        nd.projection_blend = 0.25
        self.l.new(mp.outputs[0], nd.inputs["Vector"])
        return nd

    def gray(self, v):
        """Float socket -> grey colour socket."""
        nd = self.n.new("ShaderNodeCombineColor")
        for i in range(3):
            self.l.new(v, nd.inputs[i])
        return nd.outputs[0]


def layered(name, paint, metal="#948D80", paint_metal=0.15, paint_rough=0.5,
            wear=0.35, rust=0.35, dust=0.4, grime=0.6, jitter=0.10, pattern=None,
            swatch=None, swatch_scale=1.0):
    """A painted (or bare, with paint_metal high) part, worn in by use.

    pattern: optional callable(g) -> colour socket replacing the flat paint
             colour (the hazard tape uses it).
    swatch:  path to a tiling swatch baked from the building's concept sheet
             (concept/<building>/model/swatches/). It supplies the base colour
             AND grain, so the paint hex and the photo grain step aside.
    """
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    g = _G(m)
    bsdf = g.n["Principled BSDF"]
    pos = g.node("ShaderNodeNewGeometry").outputs["Position"]
    normal = g.node("ShaderNodeNewGeometry").outputs["Normal"]
    rand = g.node("ShaderNodeObjectInfo").outputs["Random"]

    # paint, jittered per part
    part = g.remap(rand, 0, 1, 1 - jitter, 1 + jitter)
    if swatch:
        # the concept sheet's own material: its colour and grain, our light
        base = g.image(swatch, pos, swatch_scale, data=False).outputs["Color"]
        blotch = g.remap(g.noise(pos, 5, detail=4), 0.35, 0.65, 0.9, 1.1)
        col = g.mulc(base, g.gray(g.math("MULTIPLY", part, blotch)))
    else:
        base = pattern(g) if pattern else rig.srgb(paint)
        # large blotches from noise; everything finer comes from the photo's grain
        blotch = g.remap(g.noise(pos, 5, detail=4), 0.35, 0.65, 0.78, 1.18)
        grain = g.remap(g.image(f"{TEX}/maps/grain.png", pos, 1.1).outputs["Color"], 0.0, 1.0, 0.7, 1.22)
        shade = g.math("MULTIPLY", g.math("MULTIPLY", part, blotch), grain)
        col = g.mulc(base, g.gray(shade))
        # warm/cool tint drift across a surface, as a painted, weathered plate has
        tint = g.mixc(g.noise(pos, 4, detail=3), (1.08, 0.98, 0.88, 1), (0.92, 0.98, 1.06, 1))
        col = g.mulc(col, tint)

    # wear-through to bare metal: edges, plus patches that grow from them
    bevel = g.node("ShaderNodeBevel", Radius=0.03).outputs[0]
    dot = g.node("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    g.l.new(bevel, dot.inputs[0])
    g.l.new(normal, dot.inputs[1])
    edge = g.remap(dot.outputs["Value"], 0.995, 0.9)
    patch = g.noise(pos, 13, detail=3, rough=0.5)
    edge_broken = g.math("MULTIPLY", edge, g.remap(patch, 0.35, 0.6), clamp=True)
    scratch = g.image(f"{TEX}/maps/scratch_mask.png", pos, 1.6).outputs["Color"]
    scratches = g.math("MULTIPLY", g.remap(scratch, 0.3, 0.9), 0.7)
    worn = g.math("MULTIPLY", g.math("MAXIMUM", edge_broken, scratches), wear, clamp=True)
    metal_col = g.mulc(rig.srgb(metal), g.gray(blotch))
    col = g.mixc(worn, col, metal_col)
    metallic = g.mixf(worn, paint_metal, 0.9)
    rough = g.mixf(worn, paint_rough, 0.18)

    # rust: in cavities, and streaked down vertical faces
    ao = g.node("ShaderNodeAmbientOcclusion", Distance=0.2).outputs["AO"]
    cavity = g.math("SUBTRACT", 1.0, ao)
    stretch = g.node("ShaderNodeMapping", Vector=pos)
    stretch.inputs["Scale"].default_value = (1.0, 1.0, 0.12)
    streak = g.remap(g.image(f"{TEX}/maps/rust_streak.png", stretch.outputs[0], 1.3).outputs["Color"],
                     0.55, 0.85)
    vertical = g.remap(g.node("ShaderNodeSeparateXYZ", Vector=normal).outputs["Z"], 0.5, 0.1)
    # rust islands where the photo's paint has chipped away
    islands = g.remap(g.image(f"{TEX}/maps/paint_mask.png", pos, 0.9).outputs["Color"], 0.6, 0.15)
    blooms = g.math("MULTIPLY", islands, 0.55)      # accents, not camouflage
    rust_mask = g.math("MULTIPLY",
                       g.math("ADD", g.math("ADD", g.math("MULTIPLY", cavity, 1.6),
                                            g.math("MULTIPLY", streak, vertical)), blooms),
                       rust, clamp=True)
    rust_col = g.mixc(g.image(f"{TEX}/maps/grain.png", pos, 2.3).outputs["Color"],
                      rig.srgb("#44220F"), rig.srgb("#94501F"))
    col = g.mixc(rust_mask, col, rust_col)
    rough = g.mixf(rust_mask, rough, 0.9)
    metallic = g.mixf(rust_mask, metallic, 0.05)

    # dust on upward faces
    up = g.remap(g.node("ShaderNodeSeparateXYZ", Vector=normal).outputs["Z"], 0.6, 0.95)
    dust_mask = g.math("MULTIPLY", g.math("MULTIPLY", up, g.remap(g.noise(pos, 11, detail=6), 0.55, 0.75)),
                       dust * 0.55, clamp=True)
    col = g.mixc(dust_mask, col, rig.srgb("#5C4E3C"))
    rough = g.mixf(dust_mask, rough, 0.95)

    # grime, darkest in contact lines
    col = g.mixc(g.math("MULTIPLY", cavity, grime * 2.2, clamp=True), col, rig.srgb("#2A1F16"))

    g.l.new(col, bsdf.inputs["Base Color"])
    g.l.new(metallic, bsdf.inputs["Metallic"])
    g.l.new(rough, bsdf.inputs["Roughness"])

    # pixel-scale bump: dents, and scratches that run one way
    # surface relief from the photo: the paint edge stands proud of the rust
    height = g.math("ADD", g.math("MULTIPLY", g.image(f"{TEX}/maps/paint_mask.png", pos, 0.9).outputs["Color"], 0.6),
                    g.math("MULTIPLY", scratches, -0.4))
    bump = g.node("ShaderNodeBump", Strength=0.3, Distance=0.004, Height=height)
    g.l.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def hazard_pattern(g):
    """Worn hazard tape: the photo's own stripe, already chipped to rust."""
    pos = g.node("ShaderNodeNewGeometry").outputs["Position"]
    return g.image(f"{TEX}/hazard-stripe.jpg", pos, 2.5,
                   data=False).outputs["Color"]


def emissive(name, hexcol):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = rig.srgb("#1C2420")
    bsdf.inputs["Roughness"].default_value = 0.2
    bsdf.inputs["Emission Color"].default_value = rig.srgb(hexcol)
    bsdf.inputs["Emission Strength"].default_value = 0.0
    return m
