"""Vent Pump, round 4, T01: the helium seen in glass -- one sight tank, four mixes.

  $BLENDER -b --python vp4_helium_study.py -- <out-dir> [--quick] [--frames N] [--mixes A,B,C,D]

Liam, 2026-10-15: "the helium should be able to be seen in something like a glass panel or
tank"; inside it "a mixture of" (1) grey-violet liquid with slow rising bubbles (#7E7488 /
#B6A6C8), (2) a faint violet glow from within, (3) a peach-pink helium-discharge glow. While
working the helium drains and bubbles; idle it is still and unlit. No frost, rime or cold colour.

One armoured glass sight tank on the lagged helium line, at the size it would have on a 3 x 3
Vent Pump (glass 0.35 t across, 1.06 t tall: 22 x 34 sprite px at 1x; vanilla's storage-tank
window is about 17 x 24), on a small skid, built with round 3's kit (../../round-3/vpa3_kit.py,
the Reaction Plant finish, the helium line's grey-violet lagging). The helium comes in at the
tank's foot (south) and leaves from its head (east, down, north): a stroke draws it, the level
drops and refills, the bubbles rise, the relief poppet lifts and the gauge swings.

The four mixes (the liquid and its bubbles change; nothing else does):
  A  violet body, peach-pink pulse: (1) + a faint (2) + a (3) flash on each stroke
  B  violet-to-peach gradient: (1) + (2) low in the column grading to (3) at the surface
  C  violet lit faintly violet: (1) + (2), a slow glow band rising, no peach
  D  artist's choice, the control: (1) alone, no glow (keeps round 3's "melt the only glow")

Per mix it writes, at 4x: <mix>/idle.png (on the ground, unlit, still), <mix>/working-NN.png
(on the ground), <mix>/emit-NN.png (the same frame with the sun, sky and ground off: only the
glow, for the glow peak); once: mask.png (the glass window, white on black, for the measures).
Strokes at (-0.16, 0.34) of the loop, as round 3's derrick; 32 frames, 66 ms (as round 3).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "round-3"))
from vpa3_kit import *  # noqa: F401,F403,E402
import vpa_kit as K  # noqa: E402
import bpy  # noqa: E402
import rig  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

MIXES = (argv[argv.index("--mixes") + 1] if "--mixes" in argv else "A,B,C,D").split(",")
NF = K.NF_ARG or 32
CANVAS1 = (160, 160)
CENTRE1 = (64, 96)
STROKES = (-0.16, 0.34)

build_materials3(((0.45, 0.3),))
# the line's ID bands, for this study only, a step darker than the kit's #B6A6C8: the kit's,
# square to this sun on top of a horizontal run, clip to 255 at 1x (T01 wants none)
K.M["he_band_s"] = layered("he_band_s", "#9C8CB0", metal="#6A6070", paint_metal=0.05, paint_rough=0.7, wear=0.3,
                           rust=0.05, dust=0.3, grime=0.4, jitter=0.05)
K.FINISH["he_band_s"] = ("#9C8CB0", 0.35, "#6A6070", 0.2, 0.0, 0.1, None, 0.0, 0.25)
K.soften_grain(K.M["he_band_s"])
K.worn_paint(K.M["he_band_s"], *K.FINISH["he_band_s"][:1], chips=0.35, under="#6A6070", rust=0.2, wiped=0.0,
             warm=0.1, sheen=None, mottle=0.0, film=0.25)
K.GROUP["he_band_s"] = K.GROUP["he_band"]
K.sc.cycles.samples = 16 if K.QUICK else 96
# glass over a glossy liquid: no caustic paths, indirect clamped (else the liquid is grain)
K.sc.cycles.caustics_reflective = False
K.sc.cycles.caustics_refractive = False
K.sc.cycles.blur_glossy = 1.0
K.sc.cycles.sample_clamp_indirect = 2.0
# and direct light clamped per sample under what the kit's look takes to 255: the sun's glints
# on glass, brass and the cream gauge face otherwise clip (T01: no white or clipped pixels)
CLAMP = float(argv[argv.index("--clamp") + 1]) if "--clamp" in argv else 1.0
K.sc.cycles.sample_clamp_direct = CLAMP

# ---------------------------------------------------------------- colours (Liam's families)
LIQ = "#7E7488"          # (1) the liquid, as it should read
LIQ_BASE = "#5A5088"     # its base colour: the kit's warm sun (1, .94, .82) and sky bring it to LIQ
BUB = "#B6A6C8"          # (1) the bubbles, as they should read
BUB_BASE = "#8676A2"     # their base colour: lit from above by the kit's sun they read as BUB
VIO = "#9C86CC"          # (2) the violet glow
PEACH = "#F2A296"        # (3) the helium-discharge peach-pink
# glow strengths, tuned so each glow's peak at 1x lands inside vanilla's 87-171
S = {"A": dict(v=0.30, p=0.38, bub=0.22), "B": dict(v=0.5, p=0.0, bub=0.3), "C": dict(v=0.7, p=0.0, bub=0.35),
     "D": dict(v=0.0, p=0.0, bub=0.0)}


def stroke(t):
    """The draw at each stroke: fast in (the level drops), slow out (it refills)."""
    return pulse(t, STROKES, rise=0.08, fall=0.36)


# ---------------------------------------------------------------- materials
def node(nt, kind, **inp):
    n = nt.nodes.new(kind)
    for k, v in inp.items():
        n.inputs[k].default_value = v
    return n


VAL = {}            # per mix: name -> Value node, set by pose


def liquid_mat(mix):
    """The liquid: grey-violet, glossy, its emission per mix. Values: 'str' (strength), 'pk'
    (violet -> peach mix, A), 'ph' (the rising band's phase)."""
    m = bpy.data.materials.new(f"he_liquid_{mix}")
    m.use_nodes = True
    nt = m.node_tree
    L = nt.links
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb(LIQ_BASE)
    b.inputs["Roughness"].default_value = 0.5        # glossier was a speckle of sun glints at 4x,
    b.inputs["Specular IOR Level"].default_value = 0.12   # and the sun's highlight on the surface clipped
    v = VAL.setdefault(mix, {})
    st = nt.nodes.new("ShaderNodeValue")
    pk = nt.nodes.new("ShaderNodeValue")
    ph = nt.nodes.new("ShaderNodeValue")
    v["str"], v["pk"], v["ph"] = [st], [pk], [ph]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Generated"], sep.inputs[0])
    # a soft band rising through the column (seamless: the wave's phase goes 2 pi a loop)
    wave = node(nt, "ShaderNodeTexWave", Scale=1.0, Distortion=1.2, Detail=1.0)
    wave.bands_direction = "Z"
    L.new(tc.outputs["Object"], wave.inputs["Vector"])
    neg = nt.nodes.new("ShaderNodeMath")
    neg.operation = "MULTIPLY"
    neg.inputs[1].default_value = -1.0
    L.new(ph.outputs[0], neg.inputs[0])
    L.new(neg.outputs[0], wave.inputs["Phase Offset"])
    shim = nt.nodes.new("ShaderNodeMapRange")
    shim.inputs["To Min"].default_value, shim.inputs["To Max"].default_value = 0.8, 1.0
    L.new(wave.outputs["Fac"], shim.inputs["Value"])
    if mix == "B":
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        cr = ramp.color_ramp
        cr.elements[0].position, cr.elements[0].color = 0.25, rig.srgb(VIO)
        cr.elements[1].position, cr.elements[1].color = 0.95, rig.srgb(PEACH)
        L.new(sep.outputs["Z"], ramp.inputs["Fac"])
        col = ramp.outputs["Color"]
    else:
        mixn = nt.nodes.new("ShaderNodeMix")
        mixn.data_type = "RGBA"
        mixn.inputs["A"].default_value = rig.srgb(VIO)
        mixn.inputs["B"].default_value = rig.srgb(PEACH)
        L.new(pk.outputs[0], mixn.inputs["Factor"])
        col = mixn.outputs["Result"]
    L.new(col, b.inputs["Emission Color"])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(st.outputs[0], mul.inputs[0])
    L.new(shim.outputs["Result"], mul.inputs[1])
    L.new(mul.outputs[0], b.inputs["Emission Strength"])
    name = f"he_liquid_{mix}"
    K.M[name] = m
    K.GROUP[name] = ("helium (liquid in the sight tank)", "#9C80D0")
    return name


def bubble_mat(mix):
    m = bpy.data.materials.new(f"he_bubble_{mix}")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb(BUB_BASE)
    b.inputs["Roughness"].default_value = 0.5        # a sharp sun glint on a bubble clips to 255
    b.inputs["Specular IOR Level"].default_value = 0.15
    st = nt.nodes.new("ShaderNodeValue")
    pk = nt.nodes.new("ShaderNodeValue")
    mixn = nt.nodes.new("ShaderNodeMix")
    mixn.data_type = "RGBA"
    mixn.inputs["A"].default_value = rig.srgb(VIO)
    mixn.inputs["B"].default_value = rig.srgb(PEACH)
    nt.links.new(pk.outputs[0], mixn.inputs["Factor"])
    nt.links.new(mixn.outputs["Result"], b.inputs["Emission Color"])
    nt.links.new(st.outputs[0], b.inputs["Emission Strength"])
    VAL[mix]["bpk"] = [pk]
    VAL[mix]["bstr"] = [st]
    name = f"he_bubble_{mix}"
    K.M[name] = m
    K.GROUP[name] = ("helium (liquid in the sight tank)", "#9C80D0")
    return name


def clear_glass():
    """Clear, warm-neutral glass, made as a window rather than a lens: mostly a transparent BSDF
    (rays go straight through, so the liquid behind takes the sun and the sky without caustics)
    with a faint rough gloss for its sheen. A refracting principled glass (IOR 1.1) put a white
    sun glint inside the column and left the liquid grainy; the kit's pane is faintly blue."""
    m = bpy.data.materials.new("he_glass")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = rig.srgb("#F2EEE8")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Color"].default_value = rig.srgb("#D8D2CC")
    gl.inputs["Roughness"].default_value = 0.18
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs["Fac"].default_value = 0.1
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    K.M["he_glass"] = m
    K.GROUP["he_glass"] = ("glass", "#C0B8B0")
    return "he_glass"


LIQ_M = {mx: liquid_mat(mx) for mx in MIXES}
BUB_M = {mx: bubble_mat(mx) for mx in MIXES}
GLASS = clear_glass()

# ---------------------------------------------------------------- the tank
Z0, Z1 = 0.2, 1.26              # the glass
RG = 0.175                       # the glass's outer radius (0.35 t across)
RL = 0.150                       # the liquid
pad(-0.42, -0.4, 0.5, 0.42, 0.07, "dark_steel", cut=0.14, corners=("SW", "NE"))
# the foot: a grey cast base on four feet, a bolted flange under the glass
for a in range(4):
    ang = PI / 4 + a * PI / 2
    box((0.18 * math.cos(ang), 0.18 * math.sin(ang), 0.1), (0.06, 0.06, 0.06), "dark_steel", rz=ang, bevel=0.006)
cyl((0, 0, 0.14), 0.185, 0.1, "grey", verts=40)
flange_ring(0, 0, 0.19, 0.2, mat="dark_steel", h=0.025, nb=10)
# the glass, the liquid, the bubbles; a dark backer on the far half inside the glass, so the
# empty glass above the level reads dark and the liquid reads against it (a sight glass's
# backing plate)
glass = annulus((0, 0, (Z0 + Z1) / 2), RG - 0.008, RG, Z1 - Z0, GLASS, seg=64)
# the glass is seen by the camera only: the liquid behind it takes the sun and the sky straight,
# not as caustics through it (which left it dark and grainy)
glass.visible_shadow = False
glass.visible_diffuse = False
glass.visible_glossy = False
sector((0, 0, (Z0 + Z1) / 2), RL + 0.004, RG - 0.01, 0.05, PI - 0.05, Z1 - Z0 - 0.01, "dark", seg=24)
lpiv = pivot((0, 0, Z0))
liquid = cyl((0, 0, 0.5), RL, 1.0, LIQ_M[MIXES[0]], verts=48, bevel=0, parent=lpiv)
liquid.visible_shadow = False
# the head: a bolted flange, a low grey cap, the relief poppet; the gauge on the outlet
flange_ring(0, 0, Z1 + 0.012, 0.2, mat="dark_steel", h=0.025, nb=10)
cyl((0, 0, Z1 + 0.06), 0.165, 0.07, "grey", verts=40)
head(0, 0, Z1 + 0.095, 0.165, 0.035, "grey")
poppet(-0.05, 0.05, Z1 + 0.1, stroke, lift=0.05, r=0.04)
# the cage: four tie rods at the diagonals with nuts (dark: bare, the front pair glint white
# against the glass)
for a in range(4):
    ang = PI / 4 + a * PI / 2
    x, y = 0.19 * math.cos(ang), 0.19 * math.sin(ang)
    cyl((x, y, (0.19 + Z1 + 0.03) / 2), 0.011, Z1 + 0.03 - 0.19, "dark_steel", verts=8, bevel=0)
    for z in (0.21, Z1 + 0.03):
        cyl((x, y, z), 0.019, 0.022, "dark_steel", verts=6, bevel=0)
def he_line_s(pts, r=0.05, bands=0.2):
    """Round 3's he_line() (lagged, banded, no flanges here) with the study's band material."""
    P = catmull(pts)
    _, P, T, s_ = sweep(P, r, "he_lag", seg=18)
    nxt = bands / 2
    for i, p_ in enumerate(P):
        if nxt <= s_[i] < s_[-1] - 0.06:
            cyl(tuple(p_), r + 0.007, 0.05, "he_band_s", rot=along(T[i]), verts=20, bevel=0.002)
            nxt += bands
    return P


# the helium line: in at the foot from the south, out of the head east, down and away north
he_line_s([(0, -0.62, 0.14), (0, -0.4, 0.14), (0, -0.19, 0.14)], r=0.05, bands=0.18)
cyl((0, -0.62, 0.14), 0.075, 0.03, "dark_steel", rot=(PI / 2, 0, 0), verts=20)
he_line_s([(0.165, 0, Z1 + 0.06), (0.3, 0, Z1 + 0.06), (0.37, 0.04, Z1 - 0.06), (0.38, 0.1, 0.6),
         (0.38, 0.2, 0.2), (0.38, 0.42, 0.14), (0.38, 0.6, 0.14)], r=0.045, bands=0.2)
# the line's flanges in dark steel (the kit's bare ones glint to 255 under this sun)
for p_, ax in (((0, -0.2, 0.14), (0, 1, 0)), ((0.17, 0, Z1 + 0.06), (1, 0, 0)), ((0.38, 0.6, 0.14), (0, 1, 0))):
    cyl(p_, 0.068, 0.03, "dark_steel", rot=along(ax), verts=20, bevel=0.004)
box((0.38, 0.12, 0.42), (0.1, 0.08, 0.05), "dark_steel", bevel=0.004)
# the outlet's pressure gauge, on a stem off the line, facing south: it swings with each stroke
cyl((0.3, -0.05, Z1 + 0.06), 0.01, 0.1, "bare", rot=(PI / 2, 0, 0), verts=8)


def gauge_s(loc, facing, r=0.05, live=None, face="ceramic"):
    """The kit's gauge() with its face in a choice of material: the kit's cream face, square to
    this sun, clips to 255 at 4x and 1x (T01 wants none)."""
    t = Vector(facing).normalized()
    cyl(loc, r, 0.03, "brass", rot=along(t), verts=24, bevel=0.004)
    cyl(tuple(Vector(loc) + t * 0.017), r * 0.8, 0.006, face, rot=along(t), verts=24, bevel=0)
    piv = pivot(tuple(Vector(loc) + t * 0.022), along(t))
    box((r * 0.35, 0, 0), (r * 0.8, 0.012, 0.006), "needle", bevel=0, parent=piv)
    base = piv.rotation_euler.copy()

    def pose(tt, on):
        piv.rotation_euler = base
        piv.rotation_euler.rotate_axis("Z", (0.9 + live(tt)) if on else -0.9)
    K.ANIM.append(pose)


gauge_s((0.3, -0.11, Z1 + 0.07), (0.0, -1, 0.3), r=0.05, live=lambda t: 1.3 * stroke(t) - 0.2)

# bubbles: each rises a whole number of column heights a loop (seamless), wobbling a little;
# hidden above the surface; idle there are none moving and none shown
import random  # noqa: E402
rnd = random.Random(7)
BUBBLES = []
for i in range(14):
    # the liquid is opaque: the bubbles rise against the glass on the side facing the camera,
    # each standing proud of the liquid's skin by half its radius
    a = rnd.uniform(-PI * 0.85, -PI * 0.15)
    r = rnd.uniform(0.02, 0.03)
    rr = RL - 0.5 * r              # its outside stays inside the glass (0.167)
    o = sphere((0, 0, 0), r, BUB_M[MIXES[0]], seg=12)
    o.visible_shadow = False
    BUBBLES.append(dict(o=o, x=rr * math.cos(a), y=rr * math.sin(a), r=r, u=rnd.random(), k=rnd.choice((1, 1, 2)),
                        w=rnd.uniform(0.006, 0.014), wp=rnd.random()))
H = Z1 - Z0 - 0.02
LEVEL0, DRAW = 0.88, 0.4


def level(t, on):
    return LEVEL0 - (DRAW * stroke(t) if on else 0.0)


def pose_tank(t, on):
    lv = level(t, on)
    lpiv.scale = (1, 1, H * lv)
    top = Z0 + H * lv
    for b in BUBBLES:
        z = Z0 + 0.03 + ((b["u"] + b["k"] * t) % 1.0) * H
        rise = (z - Z0) / H
        b["o"].location = (b["x"] + b["w"] * math.sin(2 * PI * (2 * t + b["wp"])), b["y"], z)
        s = 0.8 + 0.45 * rise
        b["o"].scale = (s, s, s)
        b["o"].hide_render = (not on) or z + b["r"] * s > top - 0.01


K.ANIM.append(pose_tank)


def set_mix(mix, t, on):
    for o in BUBBLES:
        o["o"].data.materials[0] = K.M[BUB_M[mix]]
    liquid.data.materials[0] = K.M[LIQ_M[mix]]
    s, v = S[mix], VAL[mix]
    st = stroke(t) if on else 0.0
    if mix == "A":
        lstr, lpk, bpk = s["v"] + s["p"] * st, st, st
    elif mix == "B":
        lstr, lpk, bpk = s["v"] * (1 + 0.25 * st), 0.0, 0.8
    else:
        lstr, lpk, bpk = s["v"] * (1 + 0.2 * st), 0.0, 0.0
    v["str"][0].outputs[0].default_value = lstr if on else 0.0
    v["pk"][0].outputs[0].default_value = lpk
    v["ph"][0].outputs[0].default_value = 2 * PI * t
    v["bpk"][0].outputs[0].default_value = bpk
    v["bstr"][0].outputs[0].default_value = (s["bub"] * (1 + st) if mix == "A" else s["bub"]) if on else 0.0


def pose_all(t, on, mix):
    for p in K.ANIM:
        p(t, on)
    set_mix(mix, t, on)


# ---------------------------------------------------------------- render
SUN = rig.sun(K.SUN_E)
SUN.data.color = (1.0, 0.94, 0.82)
BG = K.sc.world.node_tree.nodes["Background"]
BG.inputs["Strength"].default_value = 0.24
rig.camera(*CANVAS1, centre_px=CENTRE1, ss=K.SSK)
ground = rig.ground_catcher()
ground.parent = K.ROOT
rig.bounce_ground()
OUT = K.OUT


def lit(on):
    SUN.hide_render = not on
    BG.inputs["Strength"].default_value = 0.24 if on else 0.0
    ground.hide_render = not on
    for o in bpy.data.objects:
        if o.name.startswith("bounce"):
            o.hide_render = not on


for mix in MIXES:
    d = os.path.join(OUT, mix)
    os.makedirs(d, exist_ok=True)
    lit(True)
    pose_all(0.0, False, mix)
    rig.render(os.path.join(d, "idle.png"))
    for f in range(NF):
        pose_all(f / NF, True, mix)
        rig.render(os.path.join(d, f"working-{f:02d}.png"))
    if mix != "D" or "--emit-d" in argv:
        lit(False)
        for f in range(NF):
            pose_all(f / NF, True, mix)
            rig.render(os.path.join(d, f"emit-{f:02d}.png"))
    lit(True)

# the window mask: the glass white, everything else black, no light
black = bpy.data.materials.new("mask_black")
black.use_nodes = True
white = bpy.data.materials.new("mask_white")
white.use_nodes = True
for m_, c_ in ((black, (0, 0, 0, 1)), (white, (1, 1, 1, 1))):
    nt = m_.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = c_
    nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
pose_all(0.0, False, MIXES[0])
for o in K.OBJS:
    for i in range(len(o.data.materials)):
        o.data.materials[i] = white if o is glass else black
for o in K.STAINS:
    o.hide_render = True
lit(False)
K.sc.view_settings.look = "None"
K.sc.view_settings.exposure = 0.0
K.sc.cycles.samples = 8
rig.render(os.path.join(OUT, "mask.png"))
print("done")
