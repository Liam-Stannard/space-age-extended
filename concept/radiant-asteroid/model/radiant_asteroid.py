"""The radiant asteroid and its chunk: colour, normal and roughness maps for the engine's
asteroid shader, in the radiant family's look B (the signed-off chunk icon,
concept/items/radiant/radiant_icons_b.py; graphics/icons/radiant-chunk.png).

    <BLENDER> -b --python \
        concept/radiant-asteroid/model/radiant_asteroid.py -- <out-dir> [--only small|chunk]

(<BLENDER>: the binary tools/paths.conf names; `python3 tools/paths.py` prints it)

writes <out-dir>/maps/{small,chunk}/asteroid-radiant-<size>-{colour,normal,roughness}-NN.png,
<out-dir>/raw/ (the 4x renders) and <out-dir>/render.done ("exit 0").

What the engine wants, read off its own files rather than assumed
(Factorio data/core/graphics/shaders/asteroid.frag; space-age/prototypes/entity/asteroid.lua
140-161 and 193-220; the promethium PNGs, measured channel by channel):
  sizes      small 128 px, 7 variations; chunk 50 px, 6 variations (sizes_resolution).
             Each variation's rock is framed to the same longest extent, in px, as
             promethium's variation of the same number (TARGET), centred.
  colour     RGBA, straight alpha; the shader premultiplies it, multiplies it by its lights
             and cuts every pixel under alpha 0.9.
  normal     screen space, linear ("View: Raw"): R = x, 1 east; G = y, 1 SOUTH; B = facing
             (the shader ignores B and rebuilds z from R and G). Promethium's alpha is its
             colour alpha bled ~1 px; its RGB runs a little past the edge. Same here.
  roughness  RGB is the subsurface colour the shader adds on the unlit side (promethium's
             red); A is the roughness, low (promethium: median 7-16 of 255, p95 73-94).

The rock: look B's chunk recipe, the same slate, groove and vein field, copied from
radiant_icons_b.py (which renders on import, so cannot be imported): a convex-hull rock,
the veins a Voronoi crack network with a hot narrow line on B's ramp and a wider dim seam
in a scorched groove. The asteroid adds crust lumps to break the hull's outline (FFF #350).
The light goes into two maps: B's ramp into the subsurface colour (roughness RGB), at full
strength, and mixed in place of the rock in the colour map's veins so the lit side shows it -- the
engine has no emission, and promethium carries its red the same two ways.
"""
import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
sys.path.insert(0, os.path.join(REPO, "concept", "items"))

import rig  # noqa: E402
from icon_kit import link, obj_coords  # noqa: E402
from materials import _G, layered  # noqa: E402

SS = 4
# look B (radiant_icons_b.py; radiant.py's glow ramp)
BGLOW = [(0.0, "#000000"), (0.25, "#04103A"), (0.55, "#0B2A8C"), (0.8, "#1F63FF"), (1.0, "#5A9CFF")]
SLATE = "#4E4D4B"
SLATE_BARE = "#807E7A"
GROOVE = "#141820"

# promethium's per-variation longest extent, px (bbox of alpha > 0)
TARGET = {"small": (102, 105, 104, 103, 87, 83, 99), "chunk": (41, 43, 44, 40, 38, 37)}
SIZES = {
    #        canvas  vein cells, width, keep   light gain  hull points  lumps  bump scale, strength
    "small": dict(px=128, veins=(2.3, 0.055, 0.47), gain=1.6, pts=(18, 24), lumps=(1, 3), bump=(7.0, 0.6)),
    "chunk": dict(px=50, veins=(2.0, 0.055, 0.45), gain=1.8, pts=(14, 18), lumps=(0, 0), bump=(4.5, 0.45)),
}
COLOUR_LIGHT = 0.85   # how far the veins' light replaces the rock in the colour map
AO_SHARE = 0.45       # how much ambient occlusion darkens the colour map's cavities
ROUGH = (0.0, 0.40)   # roughness out to the alpha channel (promethium: p5-p95 0-0.37, median 0.03-0.16)


# ---------------------------------------------------------------- the material

def ramp(g, fac, stops=BGLOW):
    nd = g.node("ShaderNodeValToRGB", Fac=fac)
    cr = nd.color_ramp
    cr.elements[0].position, cr.elements[0].color = stops[0][0], rig.srgb(stops[0][1])
    cr.elements[1].position, cr.elements[1].color = stops[-1][0], rig.srgb(stops[-1][1])
    for p, h in stops[1:-1]:
        e = cr.elements.new(p)
        e.color = rig.srgb(h)
    return nd.outputs["Color"]


def rock_mat(name, spec, seed):
    """look B's chunk rock (radiant_icons_b.rock_mat), returning the sockets each map reads."""
    cells, width, keep = spec["veins"]
    offset = Vector((seed * 3.17, seed * 1.71, seed * 2.33))

    def field(g):
        p = g.node("ShaderNodeVectorMath", Vector=obj_coords(g))
        p.operation = "ADD"
        p.inputs[1].default_value = offset
        p = p.outputs["Vector"]
        warp = g.node("ShaderNodeVectorMath")
        warp.operation = "ADD"
        g.l.new(p, warp.inputs[0])
        nz = g.node("ShaderNodeTexNoise", Vector=p, Scale=2.5, Detail=2.0)
        g.l.new(nz.outputs["Color"], warp.inputs[1])
        vor = g.node("ShaderNodeTexVoronoi", Vector=warp.outputs["Vector"], Scale=cells)
        vor.feature = "DISTANCE_TO_EDGE"
        part = g.remap(g.noise(p, 3.2, detail=2), keep - 0.03, keep + 0.03)
        return vor.outputs["Distance"], part, p

    def pattern(g):
        d, part, _ = field(g)
        groove = g.math("MULTIPLY", g.remap(d, width * 2.2, width * 0.5), part, clamp=True)
        return g.mixc(groove, rig.srgb(SLATE), rig.srgb(GROOVE))

    m = layered(name, SLATE, metal=SLATE_BARE, paint_metal=0.4, paint_rough=0.45, wear=0.45,
                rust=0.0, dust=0.0, grime=0.5, jitter=0.05, pattern=pattern)
    g = _G(m)
    bsdf = g.n["Principled BSDF"]
    # rock bump (radiant_icons_b._rock_bump), replacing layered's
    old = [n for n in g.n if n.bl_idname == "ShaderNodeBump"][0]
    p = obj_coords(g)
    sc, st = spec["bump"]
    h = g.math("ADD", g.noise(p, sc, detail=6, rough=0.65), g.math("MULTIPLY", g.noise(p, 30.0, detail=3), 0.4))
    bump = g.node("ShaderNodeBump", Strength=st, Distance=0.05, Height=h)
    g.l.new(old.outputs["Normal"], bump.inputs["Normal"])
    g.l.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    # the light: a hot narrow line, a soft seam round it
    d, part, _ = field(g)
    hot = g.remap(d, width * 0.75, width * 0.15)
    seam = g.remap(d, width * 1.9, width * 0.2)
    fac = g.math("MULTIPLY", g.math("ADD", g.math("MULTIPLY", seam, 0.62), g.math("MULTIPLY", hot, 0.38)),
                 part, clamp=True)
    fac = g.math("MINIMUM", g.math("MULTIPLY", fac, spec["gain"]), 1.0)
    light = ramp(g, fac)
    base = bsdf.inputs["Base Color"].links[0].from_socket
    rough = bsdf.inputs["Roughness"].links[0].from_socket
    ao = g.node("ShaderNodeAmbientOcclusion", Distance=0.15).outputs["AO"]
    groove = g.math("MULTIPLY", g.remap(d, width * 2.2, width * 0.5), part, clamp=True)
    return m, dict(base=base, rough=rough, normal=bump.outputs["Normal"], light=light, ao=ao, fac=fac,
                   groove=groove)


def emission_for(m, s, kind):
    """Point the material's output at one map, as a flat emission."""
    g = _G(m)
    out = g.n["Material Output"]
    if kind == "colour":
        # the light takes the rock's place where it shows (a mix, not an add: faint navy added
        # onto warm slate made a lavender grey off the ramp, hue 233-245)
        shade = g.gray(g.mixf(AO_SHARE, 1.0, s["ao"]))
        rockcol = g.mulc(s["base"], shade)
        # under the light, the groove's own cool dark (#141820), not the grime layered() puts in
        # cavities: the ramp blended over brown grime went purple (hue 236-238)
        under = g.mixc(g.math("MINIMUM", g.math("MULTIPLY", s["fac"], 4.0), 1.0), rockcol, rig.srgb(GROOVE))
        col = g.mixc(g.math("MULTIPLY", g.math("MINIMUM", g.math("MULTIPLY", s["fac"], 2.0), 1.0), COLOUR_LIGHT),
                     under, s["light"])
    elif kind == "sss":
        col = s["light"]
    elif kind == "rough":
        # layered's roughness (worn edges smooth, paint rough) broken up by a noise of the rock's
        # own scale, as promethium's varies across a face; the scorched grooves the roughest
        p = obj_coords(g)
        r = g.remap(s["rough"], 0.18, 0.6, 0.0, 1.0)
        r = g.math("MULTIPLY", r, g.remap(g.noise(p, 5.0, detail=4), 0.3, 0.7, 0.15, 1.6))
        r = g.math("ADD", r, g.math("MULTIPLY", s["groove"], 0.9))
        col = g.gray(g.remap(r, 0.0, 1.6, ROUGH[0], ROUGH[1]))
    elif kind == "normal":
        sep = g.node("ShaderNodeSeparateXYZ", Vector=s["normal"]).outputs
        r = g.math("ADD", g.math("MULTIPLY", sep["X"], 0.5), 0.5)
        gg = g.math("ADD", g.math("MULTIPLY", sep["Y"], -0.5), 0.5)   # world +Y is north; G is 1 south
        b = g.math("MAXIMUM", sep["Z"], 0.0)
        cc = g.n.new("ShaderNodeCombineColor")
        for i, v in enumerate((r, gg, b)):
            g.l.new(v, cc.inputs[i])
        col = cc.outputs[0]
    em = g.node("ShaderNodeEmission", Strength=1.0)
    g.l.new(col, em.inputs["Color"])
    g.l.new(em.outputs[0], out.inputs["Surface"])


# ---------------------------------------------------------------- the rock

def hull(bm, rng, centre, radii, n, rough=0.18):
    vs = []
    for _ in range(n):
        v = Vector((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1))).normalized()
        k = 1 + rough * noise.noise(v * 2.0 + Vector((rng.random() * 9, 1, 2)))
        vs.append(bm.verts.new(centre + Vector((v.x * radii[0], v.y * radii[1], v.z * radii[2])) * k))
    bmesh.ops.convex_hull(bm, input=vs)


def rock(size, index):
    spec = SIZES[size]
    rng = random.Random(1000 * (size == "chunk") + 17 * index + 3)
    bm = bmesh.new()
    # near-equal axes: promethium's rocks are chunky, longest/shortest extent 0.84-1.0, and so
    # is the icon's (0.62, 0.52, 0.5); flatter radii came out as slabs and slivers (60 x 84)
    radii = (0.62, rng.uniform(0.54, 0.62), rng.uniform(0.5, 0.58))
    hull(bm, rng, Vector(), radii, rng.randint(*spec["pts"]))
    body = [v.co.copy() for v in bm.verts]
    for _ in range(rng.randint(*spec["lumps"])):
        # seated on one of the body's own corners, half sunk into it: a sparse hull can sit
        # well inside its ellipsoid, and a lump placed on the ellipsoid floated free of it
        c = rng.choice(body) * 0.82
        r = rng.uniform(0.16, 0.24)
        hull(bm, rng, c, (r, r * rng.uniform(0.7, 1.0), r * 0.8), 9, rough=0.3)
    m, sockets = rock_mat(f"rock-{size}-{index}", spec, index + (50 if size == "chunk" else 0))
    ob = link(bm, f"rock-{size}-{index}", (m,), smooth=False)
    bev = ob.modifiers.new("bevel", "BEVEL")
    bev.width = 0.014 if size == "small" else 0.024
    bev.segments = 2
    bev.limit_method = "ANGLE"
    ob.rotation_euler = (rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), rng.uniform(0, 2 * math.pi))
    return ob, m, sockets


def frame(ob, size, index):
    """Ortho camera straight down, the rock's longest screen extent TARGET px, centred."""
    sc = bpy.context.scene
    px = SIZES[size]["px"]
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    pts = [ev.matrix_world @ v.co for v in me.vertices]
    ev.to_mesh_clear()
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
    longest = max(x1 - x0, y1 - y0)
    cam = sc.camera
    cam.data.ortho_scale = longest * px / TARGET[size][index]
    cam.location = ((x0 + x1) / 2, (y0 + y1) / 2, 20.0)
    sc.render.resolution_x = sc.render.resolution_y = px * SS


def scene():
    sc = rig.reset()
    sc.cycles.samples = 64
    sc.render.filter_size = 1.5
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
    sc.cycles.max_bounces = 0
    cd = bpy.data.cameras.new("cam")
    cd.type = "ORTHO"
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    return sc


# ---------------------------------------------------------------- 4x -> 1x

def area(n_in, f):
    """the 4x render's pixels averaged in blocks: no ringing, so no overshoot at the outline
    (a Lanczos-3 trial rang there, and the faint alpha it left unpremultiplied to white)"""
    w = np.zeros((n_in // f, n_in))
    for i in range(n_in // f):
        w[i, i * f:(i + 1) * f] = 1.0 / f
    return w


def load(path):
    img = bpy.data.images.load(path)
    img.colorspace_settings.name = "Non-Color"
    w, h = img.size
    a = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(a)
    bpy.data.images.remove(img)
    return a.reshape(h, w, 4).astype(np.float64)


def save(arr, path):
    h, w = arr.shape[:2]
    img = bpy.data.images.new(os.path.basename(path), w, h, alpha=True, float_buffer=False)
    img.colorspace_settings.name = "Non-Color"
    img.alpha_mode = "STRAIGHT"
    img.pixels.foreach_set(np.round(np.clip(arr, 0, 1) * 255).astype(np.float32).ravel() / 255)
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def down(rgba, w):
    """premultiplied area filter; returns straight colour and alpha"""
    a = rgba[..., 3]
    pre = rgba[..., :3] * a[..., None]
    pa = np.clip(w @ a @ w.T, 0, 1)
    pc = np.stack([w @ pre[..., i] @ w.T for i in range(3)], -1)
    with np.errstate(invalid="ignore", divide="ignore"):
        c = np.where(pa[..., None] > 1e-4, pc / pa[..., None], 0)
    return np.clip(c, 0, 1), pa


def grow(rgb, valid, steps):
    """extend rgb outward from valid pixels by steps px (mean of valid neighbours)"""
    rgb, valid = rgb.copy(), valid.copy()
    for _ in range(steps):
        acc = np.zeros_like(rgb)
        cnt = np.zeros(valid.shape)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                v = np.roll(np.roll(valid, dy, 0), dx, 1)
                acc += np.roll(np.roll(rgb, dy, 0), dx, 1) * v[..., None]
                cnt += v
        new = (~valid) & (cnt > 0)
        rgb[new] = acc[new] / cnt[new][:, None]
        valid = valid | new
    return rgb, valid


def post(raw, out, size, index):
    px = SIZES[size]["px"]
    w = area(px * SS, SS)
    full = load(raw["colour"])
    col, alpha = down(full, w)
    alpha[alpha < 1.5 / 255] = 0
    inside = alpha > 0
    col[~inside] = 0
    sss, _ = down(load(raw["sss"]), w)
    rough, _ = down(load(raw["rough"]), w)
    n = load(raw["normal"])
    vec = np.stack([n[..., 0] * 2 - 1, n[..., 1] * 2 - 1, n[..., 2]], -1)
    nv, _ = down(np.concatenate([vec * 0.5 + 0.5, n[..., 3:4]], -1), w)   # averaged encoded,
    nv = nv * 2 - 1                                                           # then renormalised
    nv /= np.maximum(np.linalg.norm(nv, axis=-1, keepdims=True), 1e-6)
    nrgb = np.stack([nv[..., 0] * 0.5 + 0.5, nv[..., 1] * 0.5 + 0.5, np.clip(nv[..., 2], 0, 1)], -1)
    nrgb, _ = grow(nrgb, inside, 2)
    nalpha = alpha.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nalpha = np.maximum(nalpha, np.roll(np.roll(alpha, dy, 0), dx, 1))
    nrgb[nalpha == 0] = 0
    sss[~inside] = 0
    ra = rough[..., 0].copy()
    ra[~inside] = 0
    stem = f"asteroid-radiant-{size}-%s-{index + 1:02d}.png"
    os.makedirs(out, exist_ok=True)
    save(np.concatenate([col, alpha[..., None]], -1), os.path.join(out, stem % "colour"))
    save(np.concatenate([nrgb, nalpha[..., None]], -1), os.path.join(out, stem % "normal"))
    save(np.concatenate([sss, ra[..., None]], -1), os.path.join(out, stem % "roughness"))


# ---------------------------------------------------------------- main

PASSES = (("colour", "Standard"), ("sss", "Standard"), ("rough", "Raw"), ("normal", "Raw"))


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = os.path.abspath(argv[0])
    only = argv[argv.index("--only") + 1].split(",") if "--only" in argv else list(SIZES)
    for size in only:
        for index in range(len(TARGET[size])):
            sc = scene()
            ob, m, sockets = rock(size, index)
            frame(ob, size, index)
            raw = {}
            for kind, view in PASSES:
                emission_for(m, sockets, kind)
                sc.view_settings.view_transform = view
                path = os.path.join(out, "raw", size, f"{kind}-{index + 1:02d}.png")
                sc.render.filepath = path
                bpy.ops.render.render(write_still=True)
                raw[kind] = path
            post(raw, os.path.join(out, "maps", size), size, index)
            print(f"done {size} {index + 1}", flush=True)
    with open(os.path.join(out, "render.done"), "w") as f:
        f.write("exit 0\n")


try:
    main()
except Exception:
    import traceback
    traceback.print_exc()
    argv = sys.argv[sys.argv.index("--") + 1:]
    with open(os.path.join(os.path.abspath(argv[0]), "render.done"), "w") as f:
        f.write("exit 1\n")
    sys.exit(1)
