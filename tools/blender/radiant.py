"""The radiant solution's light, drawn one way in every model: a lamp behind smoked glass.

Chosen by Liam, 2026-10-12: candidate B of the radiant-look study (concept/radiant-look/),
with candidate C's rising bubbles in glass columns only. The light lives in the glow layer,
as vanilla's fusion reactor, centrifuge and nuclear reactor keep theirs: the plate's window
is dark smoked glass over a dim navy liquid with its internals readable, and the glow layer
-- a light-blue core (#5A9CFF) falling off to saturated blue, never white -- is drawn
additively over it, the same by day and by night.

One material per window does both jobs: pose() switches it between the stopped plate
("idle"), the working plate ("plate") and the glow pass ("glow"), and moves its pulse,
flicker and bubbles to a point in the loop. A model's loop, per direction:

    import radiant
    R = radiant.Radiant()                              # the defaults are the agreed tuning
    glass = R.glass("leg-glass")                       # round a column or a tube
    pane = R.glass("slot-pane", pane=True)             # a thin pane over a flat window
    liquid.data.materials.append(R.liquid("leg", "column", (0.2, 0.9)))
    R.lit(liquid)                                      # every object carrying a liquid()
    R.column_bubbles((x, y), 0.2, (z0, z1), parent=ROOT)        # glass columns only
    R.pose(0.0, "idle");  render the plate (bubbles hidden: they are working-only)
    for f in range(n):
        R.pose(f / n, "plate"); render <window>-NN   (the window parts, the housing held out)
        for each glow layer (one per bloom: see below):
            R.pose(f / n, "glow", shapes=its shapes)
            with R.glow_pass(hide=(ground, bounce)):
                render <its name>-NN                   (everything visible, lit by those liquids alone)
    DECL animations: R.window_animation("window", n),
                     R.glow_animation("window-glow", "window", n, ("disc", "slot", "tube")),
                     R.glow_animation("column-glow", "window", n, ("column", "surface"))

The bloom is per shape (BLOOM), and pack.py blooms a whole glow layer one way, so a model whose
windows have different blooms renders one glow layer for each: R.groups(shapes) says which of
its shapes can share one. A model with one shape of window has one glow layer.

pack.py turns each glow frame into light (its colour times its alpha), adds the bloom the
declaration carries and packs the frames into one sheet like any animation; it fails the
pack if the light clips (contract.py, pack.py).

Parameters (every one a keyword of Radiant(); the module constants are the defaults, tuned
into vanilla's range as the study measured it, concept/radiant-look/model/study-measures.json:
vanilla's plate under its glow L 29-65, glow peak 87-171, halo 77-88 %, core 2-8 %, never
clipped).

Per-shape strength (Liam, 2026-10-15): one emission does not suit every window. Through the
helper's first tuning (glow 0.9, plate 0.09 for all) the open well, with nothing over it, set
the peak (149) while the smoked panes over the port and the slot -- their transmission is
tinted by PANE, about a tenth -- held theirs to 11 and 29. So each shape has its own glow
and plate emission, measured on look_pieces.py's five pieces at 1x, each piece's light alone
(the rest blacked, padded so the tail is whole) as look_common.light_measures measured
vanilla, over the 16-frame loop (2026-10-15, blender.org 5.0.1 on the GPU):

    shape     glow   plate   bloom   glow peak  plate under  halo %     core %     clipped  tail
                                                the glow L                         px       reach
    column    1.8    0.09    WIDE    115-128    57-59        78.7-80.6  9.6-10.8   0        42
    tube      3.8    0.09    TIGHT   129-140    47-48        83.7-84.5  6.6-7.6    0        20
    disc      90     2.5     TIGHT   161-167    39-40        77.3-77.9  7.8-9.6    0        61
    slot      14     0.6     TIGHT   150-160    36-37        78.2-78.9  7.2-8.1    0        29
    surface   0.8    0.09    WIDE    143-163    60-63        79.9-81.5  5.7-6.8    0        39
    vanilla                          87-171     29-65        77-88      2-8        0
  The disc's and slot's numbers are large because their pane passes about a tenth of the
  light; their plate emission is raised for the same reason. A column's is held where its
  bare straps' sun glint (239 at 1x on look_pieces.py's) takes the light without clipping.
  Per-shape halo (Liam, 2026-10-15): with TIGHT a column's halo stayed at 70-73 % and an
  open surface's at 68-70 % at any peak inside 87-171 -- a broad, even body of light has too
  much of itself near its peak for a faint tail to outweigh -- so those two take WIDE.
  Tail reach: how far past its light (any channel over 8) the bloomed glow stays above
  pack.GLOW_FLOOR, px at 1x, the most on any side in any frame. It grows with the window's
  brightness as much as with the tail (the port's small, bright light reaches furthest), so
  leave about a tile (64 px) of canvas round every radiant window, or the canvas's edge cuts
  the tail and pack.py fails it (<glow>_edge_px): test/radiant_box.py's 192 px canvas cut its
  column's at 4 in blue, so it is 256.

  plate_emission  per shape (PLATE_EMISSION)  the liquid's emission in the working plate, on
                        PLATE_RAMP: a dim navy with the internals readable, dark enough that
                        the plate under the glow stays in vanilla's L 29-65. A number sets
                        every shape; a dict {shape: value} sets those shapes over the defaults
  glow_emission   per shape (GLOW_EMISSION)  the liquid's emission in the glow pass, on
                        GLOW_RAMP: each shape's peaks inside vanilla's 87-171 over the whole
                        loop, bloom and all. A number or a dict, as plate_emission. B at its
                        own brightness was Radiant(glow_emission=2.3, plate_emission=0.25)
  pulse           (0.84, 1.0)  the slow breathing pulse: every emission times lo -> hi -> lo
                        once a loop (a cosine; frame 0 is lo). None for a steady light
  pulse_cycles    1     breaths a loop (a whole number, so the loop closes)
  flicker         0.22  the drifting flicker: noise moving up through the liquid's light,
                        added to its core (+-flicker/2 on the 0..1 ramp). 0 for none
  flicker_scale   0.8   the flicker noise's scale, in windows (1/size): larger is finer
  flicker_rise    1.2   window sizes the flicker drifts up a loop (looped: two copies a
                        loop apart, crossfaded, so frame n is frame 0)
  core_power      0.8   how the light falls off from the window's middle (core ** power):
                        under 1 widens the hot middle
  core_gain       0.92  how near the ramp's top the middle gets (1 = the top, #5A9CFF)
  rim_spill       True  the liquid lights the rims and bezels round its opening, in the glow
                        and the plate both (its object is seen by diffuse and glossy rays);
                        False keeps the light inside the window
  bloom           per shape (BLOOM)  vanilla's soft halo, in stages: for each, the glow frame
                        blurred by a Gaussian of that radius (px at sprite size, its standard
                        deviation), times gain, added back. TIGHT ((3, 0.9), (16, 0.6)): B's
                        3 px halo and a faint 16 px tail, for a tube, a disc and a slot; WIDE
                        ((3, 0.9), (24, 1.0)), a fuller tail, for a column and a surface. One
                        stage list sets every shape; a dict {shape: stages} sets those shapes
                        over the defaults; None for none. Applied by pack.py from the
                        declaration (glow_animation): one bloom a glow layer, so windows of
                        different blooms are rendered as separate glow layers (groups())
  bubble_count    30    C's rising bubbles in a column (column_bubbles): how many
  bubble_size     (0.016, 0.028)  their radii, tiles (random in the range)
  bubble_speed    1     column heights each bubble rises a loop (a whole number)
  bubble_plate    0.6   their emission in the working plate (BUBBLE colour); 0 in idle
  bubble_glow     0.9   their emission in the glow pass (GLOW_RAMP's top: no pale top)

Colours (sRGB; the radiant blue is #1F63FF -> #73ADFF):
  GLASS       #55606E smoked glass round a column or tube, satin and uncoated (GLASS_ROUGHNESS
              0.15; B's was polished, 0.06 under a 0.5 coat: see glass()); PANE #4A5462 a thin
              flat pane
  LIQUID      #0C1838 the liquid's own colour, all a stopped machine shows; a dull sheen
              (LIQUID_ROUGHNESS 0.4, B's was 0.25: see liquid())
  PLATE_RAMP  #02081A > #0B2A8C > #1F63FF > #73ADFF > #E2EEFF  (dim, at plate_emission)
  GLOW_RAMP   #000000 > #04103A > #0B2A8C > #1F63FF > #5A9CFF  (saturated, no pale top:
              vanilla's glow layers are pure hue and never clip)
  BUBBLE      #73ADFF in the plate; GLOW_RAMP's top in the glow
"""
import contextlib
import math
import random

import bpy

import rig

# per window shape: the liquid's emission in the working plate and in the glow pass (see the
# module docstring for how each was measured)
PLATE_EMISSION = dict(column=0.09, tube=0.09, disc=2.5, slot=0.6, surface=0.09)
GLOW_EMISSION = dict(column=1.8, tube=3.8, disc=90.0, slot=14.0, surface=0.8)
PULSE = (0.84, 1.0)
FLICKER = 0.22
FLICKER_SCALE = 0.8
FLICKER_RISE = 1.2
CORE_POWER = 0.8
CORE_GAIN = 0.92
# per window shape: the soft halo pack.py adds to the glow layer, [(radius px, gain), ...]
TIGHT = ((3.0, 0.9), (16.0, 0.6))     # B's 3 px halo and a faint 16 px tail
WIDE = ((3.0, 0.9), (24.0, 1.0))      # the same halo and a wider, fuller tail
BLOOM = dict(column=WIDE, tube=TIGHT, disc=TIGHT, slot=TIGHT, surface=WIDE)
BUBBLES = dict(count=30, size=(0.016, 0.028), speed=1)
BUBBLE_PLATE, BUBBLE_GLOW = 0.6, 0.9

GLASS = "#55606E"
GLASS_ROUGHNESS = 0.15      # the round glass: satin and uncoated, so its glint never reaches white
PANE = "#4A5462"
LIQUID = "#0C1838"
LIQUID_ROUGHNESS = 0.4      # a dull sheen: an open surface must not mirror the sun white (see liquid())
PLATE_RAMP = [(0.0, "#02081A"), (0.35, "#0B2A8C"), (0.60, "#1F63FF"), (0.82, "#73ADFF"), (1.0, "#E2EEFF")]
GLOW_RAMP = [(0.0, "#000000"), (0.25, "#04103A"), (0.55, "#0B2A8C"), (0.80, "#1F63FF"), (1.0, "#5A9CFF")]
BUBBLE = "#73ADFF"

SHAPES = ("column", "tube", "disc", "slot", "surface")
MODES = ("idle", "plate", "glow")


class _Graph:
    """Node-building shorthand for one material."""

    def __init__(self, mat):
        self.n = mat.node_tree.nodes
        self.l = mat.node_tree.links

    def new(self, kind, **ins):
        nd = self.n.new(kind)
        for k, v in ins.items():
            self.put(v, nd.inputs[k])
        return nd

    def put(self, v, sock):
        if isinstance(v, bpy.types.NodeSocket):
            self.l.new(v, sock)
        else:
            sock.default_value = v

    def op(self, operation, a, b=None, clamp=False):
        nd = self.n.new("ShaderNodeMath")
        nd.operation = operation
        nd.use_clamp = clamp
        for i, v in enumerate((a, b)):
            if v is not None:
                self.put(v, nd.inputs[i])
        return nd.outputs[0]

    def value(self):
        return self.n.new("ShaderNodeValue")

    def vec(self, x, y, z):
        nd = self.n.new("ShaderNodeCombineXYZ")
        for i, v in enumerate((x, y, z)):
            self.put(v, nd.inputs[i])
        return nd.outputs[0]

    def vadd(self, a, b):
        nd = self.n.new("ShaderNodeVectorMath")
        nd.operation = "ADD"
        self.l.new(a, nd.inputs[0])
        self.l.new(b, nd.inputs[1])
        return nd.outputs[0]

    def ramp(self, fac, stops):
        nd = self.new("ShaderNodeValToRGB", Fac=fac)
        cr = nd.color_ramp
        cr.elements[0].position, cr.elements[0].color = stops[0][0], rig.srgb(stops[0][1])
        cr.elements[1].position, cr.elements[1].color = stops[-1][0], rig.srgb(stops[-1][1])
        for p, h in stops[1:-1]:
            cr.elements.new(p).color = rig.srgb(h)
        return nd.outputs["Color"]

    def mixc(self, fac, a, b):
        nd = self.n.new("ShaderNodeMix")
        nd.data_type = "RGBA"
        for idx, v in ((0, fac), (6, a), (7, b)):
            self.put(v, nd.inputs[idx])
        return nd.outputs[2]


def _core(g, shape, size):
    """0 at the window's edge, 1 in its middle: where the body of light reads hottest.

    Read in the object's own coordinates, so a window keeps its light however it is placed."""
    s = g.new("ShaderNodeSeparateXYZ", Vector=g.new("ShaderNodeTexCoord").outputs["Object"]).outputs
    if shape in ("column", "tube"):
        facing = g.new("ShaderNodeLayerWeight", Blend=0.5).outputs["Facing"]
        return g.op("POWER", g.op("SUBTRACT", 1.0, facing, clamp=True), 1.6)
    if shape in ("disc", "surface"):
        r = g.op("DIVIDE", g.op("SQRT", g.op("ADD", g.op("MULTIPLY", s["X"], s["X"]),
                                             g.op("MULTIPLY", s["Y"], s["Y"]))), size[0])
        return g.op("SUBTRACT", 1.0, g.op("POWER", g.op("MINIMUM", r, 1.0), 1.5), clamp=True)
    across = g.op("SUBTRACT", 1.0, g.op("ABSOLUTE", g.op("DIVIDE", s["Y"], size[1])), clamp=True)
    ends = g.op("SUBTRACT", 1.0, g.op("POWER", g.op("ABSOLUTE", g.op("DIVIDE", s["X"], size[0])), 4.0),
                clamp=True)
    return g.op("MULTIPLY", g.op("POWER", across, 0.7), ends)


def _looped(g, tex, p, drift, phase):
    """tex moved by `drift` over a loop and back where it started at its end: two copies a
    loop apart, crossfaded -- tex(p + d t)(1 - t) + tex(p + d (t - 1)) t -- with the contrast
    the crossfade flattens in mid-loop given back."""
    def shifted(t):
        return g.vadd(p, g.vec(*(g.op("MULTIPLY", t, d) for d in drift)))
    a = tex(shifted(phase))
    b = tex(shifted(g.op("SUBTRACT", phase, 1.0)))
    mix = g.new("ShaderNodeMix", Factor=phase, A=a, B=b)
    mix.data_type = "FLOAT"
    dev = g.op("SUBTRACT", mix.outputs["Result"], 0.5)
    w = g.op("ADD", 1.0, g.op("MULTIPLY", g.op("MULTIPLY", phase, g.op("SUBTRACT", 1.0, phase)), 1.6))
    return g.op("ADD", 0.5, g.op("MULTIPLY", dev, w))


def _per_shape(what, v):
    """An emission keyword as {shape: strength}: a number for every shape, or a dict of some
    shapes over that keyword's per-shape defaults."""
    base = dict(PLATE_EMISSION if what == "plate_emission" else GLOW_EMISSION)
    if isinstance(v, (int, float)):
        return {k: float(v) for k in base}
    bad = set(v) - set(SHAPES)
    if bad:
        raise ValueError(f"{what}: {', '.join(sorted(bad))} not one of {', '.join(SHAPES)}")
    base.update(v)
    return base


def _shapes(shapes):
    """A shape or several, as a tuple of known shapes."""
    shapes = (shapes,) if isinstance(shapes, str) else tuple(shapes)
    bad = [sh for sh in shapes if sh not in SHAPES]
    if bad or not shapes:
        raise ValueError(f"shapes {shapes!r}: each one of {', '.join(SHAPES)}")
    return shapes


def _bloom(v):
    """The bloom keyword as {shape: ((radius, gain), ...) or ()}: None for none, one stage list
    for every shape, or a dict of some shapes' stage lists over BLOOM."""
    def stages(b):
        return tuple(tuple(float(c) for c in st) for st in b) if b else ()
    if v is None:
        return {sh: () for sh in SHAPES}
    if isinstance(v, dict):
        bad = set(v) - set(SHAPES)
        if bad:
            raise ValueError(f"bloom: {', '.join(sorted(bad))} not one of {', '.join(SHAPES)}")
        return {sh: stages(v.get(sh, BLOOM[sh])) for sh in SHAPES}
    return {sh: stages(v) for sh in SHAPES}


class Radiant:
    """B's recipe for one model: its glass, its liquids, its bubbles, posed together.

    Every keyword is documented in the module docstring; the defaults are the agreed tuning."""

    def __init__(self, *, plate_emission=PLATE_EMISSION, glow_emission=GLOW_EMISSION, pulse=PULSE,
                 pulse_cycles=1, flicker=FLICKER, flicker_scale=FLICKER_SCALE, flicker_rise=FLICKER_RISE,
                 core_power=CORE_POWER, core_gain=CORE_GAIN, rim_spill=True, bloom=BLOOM,
                 bubble_count=BUBBLES["count"], bubble_size=BUBBLES["size"], bubble_speed=BUBBLES["speed"],
                 bubble_plate=BUBBLE_PLATE, bubble_glow=BUBBLE_GLOW):
        if not (isinstance(pulse_cycles, int) and pulse_cycles >= 1):
            raise ValueError(f"pulse_cycles {pulse_cycles!r}: a whole number of breaths a loop, at least 1")
        if not (isinstance(bubble_speed, int) and bubble_speed >= 1):
            raise ValueError(f"bubble_speed {bubble_speed!r}: a whole number of rises a loop, at least 1")
        self.plate_emission = _per_shape("plate_emission", plate_emission)
        self.glow_emission = _per_shape("glow_emission", glow_emission)
        self.bubble_emission = {"idle": 0.0, "plate": bubble_plate, "glow": bubble_glow}
        self.pulse, self.pulse_cycles = pulse, pulse_cycles
        self.flicker, self.flicker_scale, self.flicker_rise = flicker, flicker_scale, flicker_rise
        self.core_power, self.core_gain = core_power, core_gain
        self.rim_spill = rim_spill
        self.bloom = _bloom(bloom)
        self.bubble_count, self.bubble_size, self.bubble_speed = bubble_count, tuple(bubble_size), bubble_speed
        self._phases = []           # value nodes: the point in the loop, 0..1
        self._glow = []             # value nodes: 1 in the glow pass (GLOW_RAMP), else 0 (PLATE_RAMP)
        self._strengths = []        # (emission strength socket, {mode: strength}, shape)
        self._poses = []            # callables(t): the bubbles
        self.objects = []           # every object lit(), and every bubble
        self.bubbles = []           # the bubbles alone: working-only, a model hides them in its idle plate
        self._bubble_mat = None

    # ------------------------------------------------------------ materials

    def glass(self, name, pane=False):
        """Smoked glass: round a column or tube (GLASS), or a thin flat pane (pane=True, PANE).

        The round glass is satin and uncoated (GLASS_ROUGHNESS, Specular IOR Level 0.35, as the
        pane's), where B's was polished (0.06) under a 0.5 clear coat. The polished glass threw a
        sun glint down a column's side that was already white at 1x (255 on look_pieces.py's
        column, 242-245 at its edge) and the coat a grazing glint at its silhouette (219-233 on
        radiant_box.py's): the glow added over either clipped, which pack.py's <glow>_clipped_px
        fails. Satin and uncoated, the glint is a soft grey streak and the light over it keeps
        its colour. A model that wants its own glints on the radiant glass keeps them away from
        the hottest light, or the pack says where they clip."""
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = rig.srgb(PANE if pane else GLASS)
        b.inputs["Roughness"].default_value = 0.04 if pane else GLASS_ROUGHNESS
        b.inputs["IOR"].default_value = 1.08 if pane else 1.47
        b.inputs["Transmission Weight"].default_value = 0.9 if pane else 0.85
        b.inputs["Specular IOR Level"].default_value = 0.35
        return m

    def liquid(self, name, shape, size):
        """The radiant solution behind one window.

        shape: column | tube (a cylinder, local Z up), disc (a round port, local Z its normal),
               slot (a box, local X along it), surface (an open well's face, local Z up).
        size:  the window's half-extents in its object's units: (radius, half-height) for a
               column or tube, (radius,) or (radius, radius) for a disc or surface,
               (half-length, half-width) for a slot.
        Its emission, plate and glow, is its shape's (plate_emission, glow_emission): tuned
        for the window that shape is in look_pieces.py -- a disc and a slot under a smoked
        pane, a column and a tube in round glass, a surface open.

        Its surface is a dull sheen (LIQUID_ROUGHNESS, Specular IOR Level 0.35): at B's 0.25
        and the default specular an open surface mirrored the sun, a glint already ~233 in
        the stopped plate on look_pieces.py's well that the light under it drove to white.
        """
        if shape not in SHAPES:
            raise ValueError(f"shape {shape!r} is not one of {', '.join(SHAPES)}")
        size = tuple(size) if len(size) > 1 else (size[0], size[0])
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        g = _Graph(m)
        b = g.n["Principled BSDF"]
        phase = g.value()
        self._phases.append(phase)
        core = g.op("MULTIPLY", g.op("POWER", _core(g, shape, size), self.core_power), self.core_gain)
        if self.flicker:
            scale = 1.0 / max(0.06, min(size))
            p = g.new("ShaderNodeTexCoord").outputs["Object"]

            def noise(v):
                return g.new("ShaderNodeTexNoise", Vector=v, Scale=scale * self.flicker_scale,
                             Detail=2.0).outputs["Fac"]
            flick = _looped(g, noise, p, (0.0, 0.0, self.flicker_rise / scale), phase.outputs[0])
            core = g.op("ADD", core, g.op("MULTIPLY", g.op("SUBTRACT", flick, 0.5), self.flicker))
        fac = g.op("MINIMUM", g.op("MAXIMUM", core, 0.0), 1.0)
        glow = g.value()
        self._glow.append(glow)
        g.l.new(g.mixc(glow.outputs[0], g.ramp(fac, PLATE_RAMP), g.ramp(fac, GLOW_RAMP)),
                b.inputs["Emission Color"])
        b.inputs["Base Color"].default_value = rig.srgb(LIQUID)
        b.inputs["Roughness"].default_value = LIQUID_ROUGHNESS
        b.inputs["Specular IOR Level"].default_value = 0.35
        self._strengths.append((b.inputs["Emission Strength"], {
            "idle": 0.0, "plate": self.plate_emission[shape], "glow": self.glow_emission[shape]}, shape))
        return m

    def lit(self, obj):
        """Register an object carrying a liquid(): rim_spill decides whether its light reaches
        the parts round it (diffuse and glossy rays see it, or do not). Returns obj."""
        obj.visible_diffuse = self.rim_spill
        obj.visible_glossy = self.rim_spill
        self.objects.append(obj)
        return obj

    # ------------------------------------------------------------ C's rising bubbles

    def _bubble_material(self):
        if self._bubble_mat is None:
            m = bpy.data.materials.new("radiant-bubble")
            m.use_nodes = True
            g = _Graph(m)
            b = g.n["Principled BSDF"]
            b.inputs["Base Color"].default_value = rig.srgb("#1A2440")
            glow = g.value()
            self._glow.append(glow)
            g.l.new(g.mixc(glow.outputs[0], rig.srgb(BUBBLE), rig.srgb(GLOW_RAMP[-1][1])),
                    b.inputs["Emission Color"])
            self._strengths.append((b.inputs["Emission Strength"], self.bubble_emission, "column"))
            self._bubble_mat = m
        return self._bubble_mat

    def column_bubbles(self, centre, radius, z, *, parent=None, seed=11, inset=0.015,
                       arc=103.0, facing="camera"):
        """C's rising bubbles in a glass column: bubble_count spheres rising from z[0] to z[1],
        each bubble_speed times a loop, in the front of the liquid, so the loop closes.

        centre: (x, y) the column's axis; radius: the liquid's radius; z: (bottom, top), all in
        the coordinates of `parent` (the model's root), tiles.
        inset:  how far in from the liquid's surface the bubbles' centres ride, tiles: less
                than their radius, so each stands proud of the liquid.
        arc:    degrees of the column's round they rise in, centred on the facing.
        facing: "camera" -- the arc faces the camera in every direction, read from the
                parents' turn at each pose() (contract.each_direction turns the root) --
                or a fixed angle in degrees in the parent's frame (east 0, north 90).
        """
        rnd = random.Random(seed)
        mat = self._bubble_material()
        made = []
        for _ in range(self.bubble_count):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=rnd.uniform(*self.bubble_size), segments=8,
                                                 ring_count=4)
            o = bpy.context.active_object
            for poly in o.data.polygons:
                poly.use_smooth = True
            o.data.materials.append(mat)
            o.parent = parent
            made.append((o, rnd.random(), rnd.uniform(-1.0, 1.0)))
        r = radius - inset
        half = math.radians(arc) / 2

        def pose(t):
            for o, start, spread in made:
                if facing == "camera":
                    turn, p = 0.0, o.parent
                    while p is not None:
                        turn += p.rotation_euler.z
                        p = p.parent
                    mid = -math.pi / 2 - turn            # south, toward the camera, in world terms
                else:
                    mid = math.radians(facing)
                u = (start + self.bubble_speed * t) % 1.0
                a = mid + spread * half
                o.location = (centre[0] + r * math.cos(a), centre[1] + r * math.sin(a),
                              z[0] + (z[1] - z[0]) * u)
        self._poses.append(pose)
        objs = [o for o, _, _ in made]
        self.bubbles += objs
        self.objects += objs
        return objs

    # ------------------------------------------------------------ posing and passes

    def strength(self, t):
        """The breathing pulse at t (0..1 through the loop): lo at 0, hi half a breath on."""
        if not self.pulse:
            return 1.0
        lo, hi = self.pulse
        return lo + (hi - lo) * (0.5 - 0.5 * math.cos(2 * math.pi * self.pulse_cycles * t))

    def pose(self, t, mode, shapes=None):
        """Every liquid and bubble at t (0..1 through the loop) as `mode` draws it:
        idle (stopped, no light), plate (working, dim) or glow (the glow pass's light).
        shapes (glow only): the shapes whose light this glow layer carries -- the other
        liquids are dark in it, still there to occlude (bubbles are a column's). None: all."""
        if mode not in MODES:
            raise ValueError(f"mode {mode!r} is not one of {', '.join(MODES)}")
        shapes = _shapes(shapes) if shapes is not None else SHAPES
        k = self.strength(t)
        for ph in self._phases:
            ph.outputs[0].default_value = t
        for gl in self._glow:
            gl.outputs[0].default_value = 1.0 if mode == "glow" else 0.0
        for sock, levels, shape in self._strengths:
            lit = mode != "glow" or shape in shapes
            sock.default_value = levels[mode] * k if lit else 0.0
        for p in self._poses:
            p(t)

    @contextlib.contextmanager
    def glow_pass(self, hide=()):
        """The scene as the glow pass renders it: the sun and every other light off, the sky
        black, and `hide` (the ground catcher, the bounce floor) hidden, so the render is the
        liquid's light and what it lights round it; everything else stays as the model set it
        (visible, so it occludes and catches the rim spill). Restored on leaving."""
        sc = bpy.context.scene
        bg = sc.world.node_tree.nodes["Background"].inputs["Strength"]
        was = bg.default_value
        off = [o for o in sc.objects if o.type == "LIGHT" or o in hide]
        hidden = [o.hide_render for o in off]
        bg.default_value = 0.0
        for o in off:
            o.hide_render = True
        try:
            yield
        finally:
            bg.default_value = was
            for o, h in zip(off, hidden):
                o.hide_render = h

    # ------------------------------------------------------------ declaring

    def window_animation(self, name, frames, working=True):
        """The working window's plate layer, for render.json: paint, flow, drawn while working."""
        return dict(name=name, frames=frames, motion="flow", working=working)

    def groups(self, shapes):
        """shapes (a model's window shapes) grouped by their bloom: one glow layer each."""
        out = {}
        for sh in _shapes(shapes):
            out.setdefault(self.bloom[sh], []).append(sh)
        return [tuple(g) for g in out.values()]

    def glow_animation(self, name, over, frames, shapes):
        """A glow layer, for render.json: one glow frame per plate frame, carrying the light of
        `shapes` (a shape or several, rendered with pose(..., "glow", shapes)) with their bloom.
        Every one of them must have the same bloom (groups() sorts them)."""
        shapes = _shapes(shapes)
        blooms = {self.bloom[sh] for sh in shapes}
        if len(blooms) > 1:
            raise ValueError(f"glow animation {name!r}: {', '.join(shapes)} have different blooms; "
                             f"one glow layer each (Radiant.groups)")
        a = dict(name=name, kind="glow", over=over, frames=frames, motion="flow")
        bloom = blooms.pop()
        if bloom:
            a["bloom"] = [list(st) for st in bloom]
        return a
