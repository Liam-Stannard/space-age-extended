#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the Core's production-tree diagram as a standalone HTML page.

The picture the design documents did not have: `06-core-production-tree.md`
describes eleven tiers in prose and one ASCII sketch, and neither shows what a
reader actually needs -- where the two rails enter, which boxes exist today and
which are drafted, and where the line ends or can stall.

Everything is laid out on an explicit grid and every long edge carries its own
waypoints. There is no router: a node is placed by tier and column, and an edge
that cannot go straight down names the lane it travels in. That is deliberate
rather than lazy -- an auto-router on a graph this dense produces crossings
nobody chose, and the alternative is a layout tool the repository would then
have to carry.

**Edit this script, never the generated HTML.** The output is 50KB of markup
with the coordinates baked in; a hand-edit is lost the next time anyone runs
this, and there is no way to tell by looking.

Two things worth knowing before moving anything:

- The gaps between tiers are routing lanes, not padding. Horizontal runs sit at
  fixed y offsets inside them (see the T8 arrivals at 1018 / 1030 / 1042, which
  are three supplies bussed in and have to stay apart), and vertical runs use
  the gaps between columns. Widening a box eats a lane.
- Labels carry a background rectangle so they mask the lines they cross. Move a
  label onto a line it should not mask and the line disappears under it, which
  looks like a missing edge rather than a misplaced label.

The marks come from `07-sinks-and-dead-ends.md`: a double edge where the line
genuinely ends, and an amber badge where a product can back up and stall the
tier that makes it. Keep the two in step.

Usage: tools/build-core-tree-diagram.py [output.html]
"""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else \
    ROOT / "design" / "diagrams" / "core-production-tree.html"


W, H = 1270, 1610
X0, CW, PITCH, BH = 250, 148, 178, 44
LRAIL, RRAIL = 178, 1200

def cx(c): return X0 + (c - 1) * PITCH + CW / 2
def cl(c): return X0 + (c - 1) * PITCH
def cr(c): return cl(c) + CW

T = {1: 230, 2: 348, 3: 466, 4: 584, 5: 702, 6: 820, 7: 938,
     8: 1056, 82: 1124, 9: 1242, 10: 1360, 11: 1478}

out = []
def e(s): out.append(s)
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def band(tier, rows=1, extra=0):
    y = T[tier] - 40
    h = 40 + BH * rows + (24 if rows > 1 else 0) + 8 + extra
    e(f'<rect class="band" x="10" y="{y}" width="{W-20}" height="{h}" rx="3"/>')

def node(col, tier, lines, state="built", fluid=False, note=None, terminal=False, warn=False):
    x, y = cl(col), T[tier]
    rx = 21 if fluid else 3
    if terminal:
        e(f'<rect class="n-term" x="{x-4}" y="{y-4}" width="{CW+8}" height="{BH+8}" rx="{rx+2}"/>')
    e(f'<rect class="{"n-built" if state=="built" else "n-draft"}" x="{x}" y="{y}" '
      f'width="{CW}" height="{BH}" rx="{rx}"/>')
    if warn:
        e(f'<circle class="badge" cx="{x+CW-11}" cy="{y+12}" r="7.5"/>')
        e(f'<text class="t-badge" x="{x+CW-11}" y="{y+16}">!</text>')
    y0 = y + BH/2 - (len(lines)-1)*6.5 + 4
    for i, ln in enumerate(lines):
        e(f'<text class="t-node" x="{x+CW/2:.0f}" y="{y0+i*13:.0f}">{esc(ln)}</text>')
    if note:
        e(f'<text class="t-note" x="{x+CW/2:.0f}" y="{y+BH+13:.0f}">{esc(note)}</text>')

def chip(col, tier, label, tone, width=118, dx=0, drop=True, dashed=False, tag=None):
    x, y = cl(col) + dx, T[tier] - 38
    da = ';stroke-dasharray:4 3' if dashed else ''
    e(f'<rect class="chip" style="fill:var(--{tone}-f);stroke:var(--{tone}){da}" '
      f'x="{x}" y="{y}" width="{width}" height="26" rx="2"/>')
    e(f'<rect style="fill:var(--{tone})" x="{x}" y="{y}" width="3" height="26"/>')
    e(f'<text class="t-chip" style="fill:var(--{tone})" x="{x+11}" y="{y+17}">{esc(label)}</text>')
    if tag:
        e(f'<text class="t-chiptag" style="fill:var(--{tone})" x="{x+width-8}" y="{y+17}">{esc(tag)}</text>')
    if drop:
        e(f'<path class="ed" d="M {x+width/2:.0f} {y+26} L {x+width/2:.0f} {T[tier]}" marker-end="url(#ah)"/>')
    return x, y, width

def path(pts, cls="ed", label=None, lx=None, ly=None, anchor="middle", chars=None):
    d = "M " + " L ".join(f"{a:.0f} {b:.0f}" for a, b in pts)
    e(f'<path class="{cls}" d="{d}" marker-end="url(#ah)"/>')
    if label:
        w = (chars if chars else len(label)) * 5.3 + 10
        ax = {"middle": lx - w/2, "start": lx - 5, "end": lx - w + 5}[anchor]
        e(f'<rect class="lbl-bg" x="{ax:.0f}" y="{ly-9:.0f}" width="{w:.0f}" height="12" rx="2"/>')
        e(f'<text class="t-edge" style="text-anchor:{anchor}" x="{lx:.0f}" y="{ly:.0f}">{esc(label)}</text>')

def across(c1, c2, tier, label=None):
    y = T[tier] + BH/2
    path([(cr(c1), y), (cl(c2)-3, y)])
    if label:
        mx = (cr(c1)+cl(c2))/2; w = len(label)*5.3+10
        e(f'<rect class="lbl-bg" x="{mx-w/2:.0f}" y="{T[tier]-17:.0f}" width="{w:.0f}" height="12" rx="2"/>')
        e(f'<text class="t-edge" style="text-anchor:middle" x="{mx:.0f}" y="{T[tier]-7:.0f}">{esc(label)}</text>')

def stub(col, tier, lines):
    y = T[tier] + BH/2
    x = cl(col)
    path([(x-30, y), (x-3, y)], cls="ed")
    for i, ln in enumerate(lines):
        e(f'<text class="t-stub" style="text-anchor:end" x="{x-36}" y="{y-4+i*11:.0f}">{esc(ln)}</text>')

def tierlabel(tier, num, name, mach):
    y = T[tier]
    e(f'<text class="t-tnum" x="150" y="{y+15}">{num}</text>')
    e(f'<text class="t-tname" x="150" y="{y+30}">{esc(name)}</text>')
    e(f'<text class="t-tmach" x="150" y="{y+43}">{esc(mach)}</text>')

# ------------------------------------------------------------------ canvas
e(f'<svg viewBox="0 0 {W} {H}" role="img" class="tree" aria-label="'
  'The Core of the Shattered Planet, eleven production tiers deep. Kamacite ore and two vents enter from a local rail on the left; '
  'carbon, an electromagnetic plant and the five cross-planet capstone products enter from a corridor freight rail on the right. '
  'Beneficiation feeds primary metallurgy, carbonyl chemistry, orbital crystal growth, whisker fibre, cryogenics, five capstone integrations, '
  'subassemblies and major assemblies, ending in the Field Coil Segment and the Ignition Array.">')
e('<defs>'
  '<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
  '<path d="M 0 1.2 L 8.6 5 L 0 8.8 z" class="head"/></marker>'
  '<marker id="ahm" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
  '<path d="M 0 1.2 L 8.6 5 L 0 8.8 z" class="head-m"/></marker>'
  '<marker id="ahh" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
  '<path d="M 0 1.2 L 8.6 5 L 0 8.8 z" class="head-h"/></marker>'
  '</defs>')

band(1); band(2, extra=6); band(3); band(4); band(5); band(6)
band(7); band(8, rows=2); band(9); band(10); band(11, extra=12)

# ------------------------------------------------------------------ sources
e('<rect class="panel" x="24" y="34" width="588" height="140" rx="4"/>')
e('<rect class="panel" x="658" y="34" width="588" height="140" rx="4"/>')
e('<text class="t-panelh" style="fill:var(--molten)" x="44" y="58">LOCAL — THE CORE’S OWN GROUND</text>')
e('<text class="t-panelh" x="678" y="58">FREIGHT — WHAT THE CORRIDOR CARRIES</text>')
for i, (a, b) in enumerate([
        ("Kamacite ore", "the only solid ore, sited in the starting area"),
        ("Molten kamacite vent", "drawing it costs helium-3"),
        ("Helium-3 vent", "rare — it throttles the rich one"),
        ("Radiant chunks", "seeded from the Edge; fuel, not metal")]):
    y = 82 + i * 21
    e(f'<circle cx="48" cy="{y-4}" r="3" style="fill:var(--molten)"/>')
    e(f'<text class="t-src" x="60" y="{y}">{esc(a)}</text>')
    e(f'<text class="t-srcsub" x="{60+len(a)*6.5+10:.0f}" y="{y}">{esc(b)}</text>')
for i, (a, b) in enumerate([
        ("Carbon", "the carbonyl carrier — about 90% comes back"),
        ("Electromagnetic plant", "magnetic-field = 0: it cannot be built here"),
        ("Five capstone products", "one per cross-planet tree")]):
    y = 82 + i * 21
    e(f'<circle cx="682" cy="{y-4}" r="3" style="fill:var(--ink3)"/>')
    e(f'<text class="t-src" x="694" y="{y}">{esc(a)}</text>')
    e(f'<text class="t-srcsub" x="{694+len(a)*6.5+10:.0f}" y="{y}">{esc(b)}</text>')
for i, (nm, tone, tier) in enumerate([("F↔A", "fa", "T7"), ("V↔F", "vf", "T7"), ("V↔G", "vg", "T7"),
                                      ("F↔G", "fg", "T5"), ("G↔A", "ga", "T6")]):
    x = 698 + i * 106
    e(f'<rect x="{x}" y="148" width="54" height="18" rx="2" style="fill:var(--{tone}-f);stroke:var(--{tone})"/>')
    e(f'<text class="t-chip" style="fill:var(--{tone});text-anchor:middle" x="{x+27}" y="161">{nm}</text>')
    e(f'<text class="t-chip" style="fill:var(--ink3)" x="{x+60}" y="161">at {tier}</text>')

# ------------------------------------------------------------------ rails
e(f'<path class="rail rail-l" d="M {LRAIL} 174 L {LRAIL} 850"/>')
e(f'<path class="rail" d="M {RRAIL} 174 L {RRAIL} 900"/>')
e(f'<text class="t-rail" style="fill:var(--molten)" transform="rotate(-90 {LRAIL-14} 560)" x="{LRAIL-14}" y="560">LOCAL RESOURCES</text>')
e(f'<text class="t-rail" transform="rotate(-90 {RRAIL+18} 570)" x="{RRAIL+18}" y="570">CORRIDOR FREIGHT</text>')

def tap(col, tier, label, dx=-45, y=None):
    yy = y if y else T[tier] - 25
    x = cx(col) + dx
    path([(LRAIL, yy), (x, yy), (x, T[tier])], cls="ed tap")
    e(f'<text class="t-tap" x="{LRAIL+10}" y="{yy-7:.0f}">{esc(label)}</text>')

# =================================================================== T1
tierlabel(1, "T1", "BENEFICIATION", "crusher · EM plant")
node(1, 1, ["Crushed kamacite"], "draft")
node(2, 1, ["Kamacite fines"], "draft", warn=True)
node(4, 1, ["Schreibersite", "concentrate"], "draft")
cxx, cyy, cw = chip(4, 1, "electromagnetic plant", "cor", 132, dx=8, drop=False, dashed=True)
path([(RRAIL, cyy+13), (cxx+cw+3, cyy+13)], cls="ed cor")
path([(cxx+cw/2, cyy+26), (cxx+cw/2, T[1])], cls="ed dash")
tap(1, 1, "kamacite ore")
across(1, 2, 1, "tailings")
y1 = T[1] + BH/2
path([(cr(2), y1), (cl(4)-3, y1)])
e(f'<text class="t-edge" style="text-anchor:middle" x="{(cr(2)+cl(4))/2:.0f}" y="{y1-8:.0f}">magnetic separation</text>')

# =================================================================== T2
tierlabel(2, "T2", "PRIMARY METALLURGY", "foundry · gravity ≥ 45")
node(1, 2, ["Kamacite plate"], note="today: 2 raw ore, skipping T1")
node(2, 2, ["Settled melt"], fluid=True)
node(3, 2, ["Dross"], warn=True)
node(4, 2, ["Cast ingot"])
node(5, 2, ["Phosphide flux"], "draft")
tap(2, 2, "molten kamacite · 100")
path([(cx(1), T[1]+BH), (cx(1), T[2])], label="3 crushed", lx=cx(1)+5, ly=T[1]+BH+22, anchor="start")
ymid = T[2] + BH/2
path([(cr(2), ymid-8), (cl(3)-3, ymid-8)])
mx = (cr(2)+cl(3))/2
e(f'<rect class="lbl-bg" x="{mx-33:.0f}" y="{T[2]-17}" width="66" height="12" rx="2"/>')
e(f'<text class="t-edge" style="text-anchor:middle" x="{mx:.0f}" y="{T[2]-7}">2 per settle</text>')
path([(cl(3), ymid+8), (cr(2)+3, ymid+8)], cls="ed loop")
path([(cx(2), T[2]+BH), (cx(2), 404), (cx(4), 404), (cx(4), T[2]+BH)],
     label="100 melt → 1 ingot", lx=(cx(2)+cx(4))/2, ly=416)
path([(cx(2)+40, T[2]+BH), (cx(2)+40, 418), (cx(5), 418), (cx(5), T[2]+BH)],
     label="settled melt", lx=cx(5)-90, ly=430, anchor="end")
path([(cx(4), T[1]+BH), (cx(4), 300), (cx(5), 300), (cx(5), T[2])], label="phosphorus", lx=cx(5)-8, ly=312, anchor="end")

# =================================================================== T3
tierlabel(3, "T3", "CARBONYL CHEMISTRY", "chemical plant")
node(1, 3, ["Carbon monoxide"], "draft", fluid=True)
node(2, 3, ["Metal carbonyl"], "draft", fluid=True)
node(3, 3, ["Carbonyl powder"], "draft")
node(4, 3, ["Sintered preform"], "draft")
cxx, cyy, cw = chip(1, 3, "carbon", "cor", 100, drop=False)
path([(RRAIL, cyy+13), (cxx+cw+3, cyy+13)], cls="ed cor")
path([(cxx+cw/2, cyy+26), (cxx+cw/2, T[3])], cls="ed")
path([(cx(2), T[2]+BH), (cx(2), 440), (cx(1)+52, 440), (cx(1)+52, T[3])], label="settled melt", lx=cx(2)-6, ly=452, anchor="end")
path([(cx(2), T[1]+BH), (cx(2), 290), (413, 290), (413, 488), (cl(2)-3, 488)], label="kamacite fines", lx=407, ly=330, anchor="end")
across(1, 2, 3, "cold")
across(2, 3, 3, "hot")
across(3, 4, 3, "pressed")
path([(cx(3)-30, T[3]+BH), (cx(3)-30, 528), (cx(1), 528), (cx(1), T[3]+BH)], cls="ed loop",
     label="≈90% of the carbon monoxide comes back", lx=(cx(1)+cx(3))/2, ly=540)
path([(cx(5), T[2]+BH), (cx(5), 488), (cr(4)+3, 488)], label="phosphide flux", lx=cx(5)-8, ly=480, anchor="end")

# =================================================================== T4
tierlabel(4, "T4", "ORBITAL CRYSTAL", "in orbit · gravity 0")
node(5, 4, ["Homogenised ingot"])
node(4, 4, ["Zone-refined boule"], "draft")
node(3, 4, ["Kamacite wafer"], "draft")
path([(cx(4), T[2]+BH), (cx(4), 410), (941, 410), (941, T[4]+BH/2), (cl(5)-3, T[4]+BH/2)],
     label="cast ingot ×2", lx=947, ly=520, anchor="start")
y4 = T[4] + BH/2
path([(cl(5), y4), (cr(4)+3, y4)])
e(f'<text class="t-edge" style="text-anchor:middle" x="{(cl(5)+cr(4))/2:.0f}" y="{y4-8:.0f}">zoned</text>')
path([(cl(4), y4), (cr(3)+3, y4)])
e(f'<text class="t-edge" style="text-anchor:middle" x="{(cl(4)+cr(3))/2:.0f}" y="{y4-8:.0f}">sliced</text>')
tap(4, 4, "helium-3 — the rare vent reaches orbit", dx=-45)

# =================================================================== T5
tierlabel(5, "T5", "FIBRE AND COMPOSITE", "whisker beds · tender")
node(1, 5, ["Seed plate"])
node(2, 5, ["Kamacite whiskers"])
node(3, 5, ["Whisker tow"], "draft")
node(4, 5, ["Whisker prepreg"], "draft")
node(5, 5, ["Whisker felt"], "draft")
cxx, cyy, cw = chip(4, 5, "bio-polymer", "fg", 120, dx=16, drop=False, tag="F↔G")
path([(RRAIL, cyy+13), (cxx+cw+3, cyy+13)], cls="ed cor")
path([(cxx+cw/2, cyy+26), (cxx+cw/2, T[5])], cls="ed")
path([(cx(1), T[2]+BH), (cx(1), 410), (232, 410), (232, T[5]+BH/2), (cl(1)-3, T[5]+BH/2)],
     label="1 plate + 20 melt", lx=238, ly=648, anchor="start")
path([(cl(3), T[2]+BH/2), (591, T[2]+BH/2), (591, 690), (cx(2)+40, 690), (cx(2)+40, T[5])],
     label="beds are made of dross", lx=597, ly=648, anchor="start")
across(1, 2, 5, "grown, 4 min")
across(2, 3, 5, "combed")
across(3, 4, 5, "matrix")
path([(cx(2)+40, T[5]+BH), (cx(2)+40, 768), (cx(5), 768), (cx(5), T[5]+BH)],
     label="uncombed, low grade", lx=cx(3)-10, ly=780)

# =================================================================== T6
tierlabel(6, "T6", "CRYOGENICS", "cryogenic plant")
node(1, 6, ["Dilution charge"], "draft")
node(2, 6, ["Cryostat core"], "draft")
cxx, cyy, cw = chip(1, 6, "cryoprotectant", "ga", 132, dx=16, drop=False, tag="G↔A")
path([(RRAIL, cyy+13), (cxx+cw+3, cyy+13)], cls="ed cor")
path([(cxx+cw/2, cyy+26), (cxx+cw/2, T[6])], cls="ed")
path([(LRAIL, 842), (cl(1)-3, 842)], cls="ed tap")
e(f'<text class="t-tap" x="{LRAIL+10}" y="835">helium-3</text>')
across(1, 2, 6)
path([(cx(4), T[3]+BH), (cx(4), 528), (1150, 528), (1150, T[6]+BH/2), (cr(2)+3, T[6]+BH/2)],
     label="sintered preform", lx=1144, ly=660, anchor="end")
path([(cx(5), T[5]+BH), (cx(5), 790), (cx(2)+45, 790), (cx(2)+45, T[6])],
     label="whisker felt — insulation", lx=1010, ly=784, anchor="end")

# =================================================================== T7
tierlabel(7, "T7", "THE FIVE INTEGRATIONS", "one local mechanic each")
node(1, 7, ["Field conductor"])
node(2, 7, ["Magnetic core billet"], note="+ settled melt & flux, T2")
node(3, 7, ["Reinforced frame"])
node(5, 7, ["Geodynamic", "science pack"], terminal=True)
specs = [(1, "superconducting winding", "fa", 176, "F↔A"), (2, "magnetar alloy", "vf", 128, "V↔F"),
         (3, "cultured alloy", "vg", 128, "V↔G")]
path([(RRAIL, 894), (cl(1)+69, 894)], cls="ed cor")
for col, lab, tone, wch, tg in specs:
    cxx, cyy, cw = chip(col, 7, lab, tone, wch, drop=False, tag=tg)
    path([(cxx+cw/2, 894), (cxx+cw/2, cyy)], cls="ed cor")
    path([(cxx+cw/2, cyy+26), (cxx+cw/2, T[7])], cls="ed")
path([(cx(3), T[4]+BH), (cx(3), 660), (208, 660), (208, T[7]+BH/2), (cl(1)-3, T[7]+BH/2)],
     label="kamacite wafer", lx=214, ly=880, anchor="start")
path([(cx(4), T[5]+BH), (cx(4), 912), (725, 912), (725, T[7])], label="whisker prepreg", lx=870, ly=908, anchor="start")
ys = T[7] + BH + 22
path([(cx(1)+40, T[7]+BH), (cx(1)+40, ys), (cx(5), ys), (cx(5), T[7]+BH+4)], cls="ed sci",
     label="research: 1 conductor + 1 frame + 4 whiskers → 5 packs", lx=760, ly=ys+14)

# =================================================================== T8
tierlabel(8, "T8", "SUBASSEMBLIES", "assembler · cold weld")
node(1, 8, ["Winding pack"], "draft")
node(2, 8, ["Coil lamination"], "draft")
node(3, 8, ["Insulation sleeve"])
node(4, 8, ["Coolant charge"])
node(1, 82, ["Welded plate"], warn=True)
node(2, 82, ["Vacuum cell"], "draft")
path([(cx(1), T[7]+BH), (cx(1), T[8])], label="field conductor", lx=cx(1)+5, ly=T[7]+BH+24, anchor="start")
path([(cl(2), 842), (413, 842), (413, 1078), (cr(1)+3, 1078)], label="cryostat core", lx=419, ly=1040, anchor="start")
path([(1150, T[6]+BH/2), (1150, 1018), (cx(2), 1018), (cx(2), T[8])])
path([(cx(1), T[6]+BH), (cx(1), 876), (591, 876), (591, 1030), (cx(4)+40, 1030), (cx(4)+40, T[8])],
     label="dilution charge", lx=597, ly=1040, anchor="start")
path([(cx(4), 912), (cx(4), 1042), (cx(3)+45, 1042), (cx(3)+45, T[8])])
stub(1, 82, ["T2 plate ×4", "+ T5 whiskers ×2"])
path([(cx(2), T[8]+BH), (cx(2), T[82])])
path([(cx(3), T[8]+BH), (cx(3), 1112), (cx(2)+45, 1112), (cx(2)+45, T[82])])
e(f'<text class="t-vac" x="{cl(2)+10}" y="{T[82]+BH+14}">sealed in vacuum — free here, expensive anywhere else</text>')

# =================================================================== T9
tierlabel(9, "T9", "MAJOR ASSEMBLIES", "assembler · cold weld")
node(2, 9, ["Coil assembly"])
node(4, 9, ["Coolant loop"])
path([(cx(1)+44, T[8]+BH), (cx(1)+44, 1112), (405, 1112), (405, 1214), (cx(2)-45, 1214), (cx(2)-45, T[9])])
path([(cx(2), T[82]+BH), (cx(2), T[9])])
path([(cx(4), T[8]+BH), (cx(4), T[9])], label="+ T2 plate ×10", lx=cx(4)+5, ly=1170, anchor="start")
stub(2, 9, ["T7 billet + frame,", "T8 welded plate ×2"])
stub(4, 9, ["T6 cryostat core"])

# =================================================================== T10
tierlabel(10, "T10", "THE SEGMENT", "the array itself")
node(3, 10, ["Field Coil Segment"])
path([(cx(2), T[9]+BH), (cx(2), 1330), (cx(3)-40, 1330), (cx(3)-40, T[10])])
path([(cx(4), T[9]+BH), (cx(4), 1330), (cx(3)+40, 1330), (cx(3)+40, T[10])])

# =================================================================== T11
tierlabel(11, "T11", "IGNITION", "fires once")
x11, w11 = cl(2), CW + 2*PITCH
e(f'<rect class="n-term term-array" x="{x11-4}" y="{T[11]-4}" width="{w11+8}" height="66" rx="5"/>')
e(f'<rect class="n-array" x="{x11}" y="{T[11]}" width="{w11}" height="58" rx="3"/>')
e(f'<text class="t-array" x="{x11+w11/2:.0f}" y="{T[11]+26}">IGNITION ARRAY</text>')
e(f'<text class="t-arraysub" x="{x11+w11/2:.0f}" y="{T[11]+45}">100 segments · 50 MW while it runs · the game is won</text>')
path([(cx(3), T[10]+BH), (cx(3), T[11]-4)], cls="ed molten", label="× 100", lx=cx(3)+6, ly=1440, anchor="start")
stub(2, 11, ["arc mast ×4, welded plate ×200,", "kamacite plate ×500, proc. unit ×200"])
e('</svg>')
TREE = "\n".join(out)

# ------------------------------------------------------------------ figure 2
p = []
def q(s): p.append(s)
q('<svg viewBox="0 0 900 292" role="img" class="pwr" aria-label="'
  'The Core has three power sources: steam raised by settling the melt, radiant fuel crushed from seeded chunks and burned in a radiant generator, '
  'and arc masts catching storms. All three feed the Ignition Array\'s 50 megawatt draw, so power spent is metal not cast.">')
q('<defs><marker id="ah2" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
  '<path d="M 0 1.2 L 8.6 5 L 0 8.8 z" class="head"/></marker></defs>')
def b2(x, y, w, h, lines, cls="n-built", sub=None):
    q(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>')
    y0 = y + h/2 - (len(lines)-1)*6.5 + 4
    for i, ln in enumerate(lines):
        q(f'<text class="t-node" x="{x+w/2:.0f}" y="{y0+i*13:.0f}">{esc(ln)}</text>')
    if sub:
        q(f'<text class="t-note" x="{x+w/2:.0f}" y="{y+h+13:.0f}">{esc(sub)}</text>')
def a2(pts, label=None, lx=None, ly=None, cls="ed"):
    d = "M " + " L ".join(f"{a:.0f} {b:.0f}" for a, b in pts)
    q(f'<path class="{cls}" d="{d}" marker-end="url(#ah2)"/>')
    if label:
        q(f'<text class="t-edge" style="text-anchor:middle" x="{lx}" y="{ly}">{esc(label)}</text>')
b2(16, 44, 148, 40, ["Molten kamacite"])
b2(16, 140, 148, 40, ["Radiant chunk"])
b2(16, 226, 148, 40, ["Arc storm"], "n-draft")
b2(246, 24, 168, 34, ["Gravity settling"], "n-built", "60 melt · 150 steam")
b2(246, 88, 168, 34, ["Quenched settling"], "n-built", "25 melt · 900 steam")
b2(246, 140, 168, 40, ["Radiant fuel ×2"])
b2(246, 226, 168, 40, ["Arc mast"], "n-built", "35% efficient · 4000 MJ buffer")
b2(500, 44, 158, 40, ["Steam turbine"], "n-built", "≈1 turbine per vessel, quenched")
q('<circle class="badge" cx="647" cy="56" r="7.5"/>')
q('<text class="t-badge" x="647" y="60">!</text>')
b2(500, 140, 158, 40, ["Radiant generator"], "n-built", "10 MW")
b2(500, 226, 158, 40, ["Storm charge"], "n-built", "40 MW out")
q('<rect class="n-array" x="726" y="112" width="158" height="66" rx="3"/>')
q('<text class="t-array" x="805" y="142">50 MW</text>')
q('<text class="t-arraysub" x="805" y="161">the array, while it runs</text>')
a2([(164, 54), (246, 41)])
a2([(164, 74), (246, 105)])
a2([(164, 160), (246, 160)], "crushed", 205, 154)
a2([(164, 246), (246, 246)], "caught", 205, 240)
a2([(414, 41), (500, 56)], "150 steam", 457, 34)
a2([(414, 105), (500, 72)], "900 steam", 457, 116)
a2([(414, 160), (500, 160)])
a2([(414, 246), (500, 246)])
a2([(658, 64), (692, 64), (692, 128), (726, 128)])
a2([(658, 160), (692, 160), (692, 145), (726, 145)])
a2([(658, 246), (692, 246), (692, 162), (726, 162)])
q('<text class="t-vac" style="text-anchor:middle" x="330" y="200">the same melt is either metal or power</text>')
q('</svg>')
POWER = "\n".join(p)

TIERS = [
 ("T1","Beneficiation","Crushed kamacite, kamacite fines, schreibersite concentrate",
  "The dead dynamo. Magnetic separation needs an electromagnetic plant, and <code>magnetic-field = 0</code> refuses to let one be manufactured here — so the first one arrives by freight.","draft"),
 ("T2","Primary metallurgy","Kamacite plate, settled melt, dross, cast ingot, phosphide flux",
  "Gravity. Settling only runs at <code>gravity ≥ 45</code>, which is the Core alone — Vulcanus, the next heaviest, is 40. 100 molten kamacite gives either 60 melt + 150 steam or 25 melt + 900 steam.","mixed"),
 ("T3","Carbonyl chemistry","Carbon monoxide, metal carbonyl, carbonyl powder, sintered preform",
  "No carbon. Metal that travels through pipes: nickel and CO combine cold and separate hot, returning about 90% of the carbon monoxide. The corridor delivers a trickle, permanently.","draft"),
 ("T4","Orbital crystal growth","Homogenised ingot, zone-refined boule, kamacite wafer",
  "No gravity in orbit. A boule grown under 50 g slumps under its own weight; helium-3 rides the lift up as the cold end of the zone.","mixed"),
 ("T5","Fibre and composite","Seed plate, kamacite whiskers, whisker tow, prepreg, felt",
  "The farm. Single-crystal fibres are absurdly strong in one direction and useless in the others, so combing is a real step — and what is not worth combing becomes felt.","mixed"),
 ("T6","Cryogenics","Dilution charge, cryostat core",
  "The rare vent. Helium-3 stops being only a gate on the melt and becomes a product: every superconducting step downstream needs something cold.","draft"),
 ("T7","The five integrations","Field conductor, magnetic core billet, reinforced frame",
  "Each capstone is integrated through a <em>different</em> local mechanic, which is what stops the five technologies being one technology repeated. Geodynamic science eats the same parts.","built"),
 ("T8","Subassemblies","Coil lamination, winding pack, insulation sleeve, coolant charge, vacuum cell, welded plate",
  "Vacuum. Cold welding and vacuum sealing are cheap here and would need an expensive sealed process anywhere else — the one thing the Core is <em>good</em> at rather than short of.","mixed"),
 ("T9","Major assemblies","Coil assembly, coolant loop","Convergence: five planets, two vents and a farm meet in two items.","built"),
 ("T10","The segment","Field Coil Segment","The array's own fixed recipe. Nothing else makes it, and nowhere else can.","built"),
 ("T11","Ignition","Ignition Array","100 segments at 50 MW, then it fires once. Currently a rocket silo underneath, which is the mod's most contradictory frame.","built"),
]

rows = "\n".join(
 f'<tr><td class="tk"><span class="tnum">{a}</span></td><td class="tn">{b}<div class="tm">{c}</div></td>'
 f'<td class="ta">{dd}</td><td><span class="pill p-{st}">{ {"built":"built","draft":"drafted","mixed":"part built"}[st] }</span></td></tr>'
 for a, b, c, dd, st in TIERS)

HTML = f"""<title>Kamacite to Ignition</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;500&display=swap">
<style>
:root {{
  --bg:#E4E7E3; --panel:#F4F6F2; --panel2:#DCE0DA; --band:#EDF0EA;
  --ink:#14181A; --ink2:#525A56; --ink3:#8B948F; --rule:#C6CCC5;
  --molten:#BF4A19; --molten-f:#BF4A1914; --helium:#2C7986;
  --cor:#7C857F; --cor-f:#7C857F14;
  --fa:#3A6BB0; --fa-f:#3A6BB014; --vf:#8B3E9C; --vf-f:#8B3E9C14;
  --vg:#7A5E20; --vg-f:#7A5E2014; --fg:#2A8360; --fg-f:#2A836014;
  --ga:#1B7C8A; --ga-f:#1B7C8A14;
  --ok:#2A7A52; --ok-f:#2A7A5218; --warn:#9A6A15; --warn-f:#9A6A1518;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg:#0F1211; --panel:#1A1E1C; --panel2:#232825; --band:#161A18;
    --ink:#E7EBE6; --ink2:#A6B0AA; --ink3:#6E7A74; --rule:#2C322E;
    --molten:#E8703A; --molten-f:#E8703A1F; --helium:#59B2C1;
    --cor:#8B948E; --cor-f:#8B948E1A;
    --fa:#6E9BE0; --fa-f:#6E9BE01F; --vf:#C173D2; --vf-f:#C173D21F;
    --vg:#C0A055; --vg-f:#C0A0551F; --fg:#4FBD8C; --fg-f:#4FBD8C1F;
    --ga:#45B0BF; --ga-f:#45B0BF1F;
    --ok:#5CBF8B; --ok-f:#5CBF8B22; --warn:#D3A445; --warn-f:#D3A44522;
  }}
}}
:root[data-theme="dark"] {{
  --bg:#0F1211; --panel:#1A1E1C; --panel2:#232825; --band:#161A18;
  --ink:#E7EBE6; --ink2:#A6B0AA; --ink3:#6E7A74; --rule:#2C322E;
  --molten:#E8703A; --molten-f:#E8703A1F; --helium:#59B2C1;
  --cor:#8B948E; --cor-f:#8B948E1A;
  --fa:#6E9BE0; --fa-f:#6E9BE01F; --vf:#C173D2; --vf-f:#C173D21F;
  --vg:#C0A055; --vg-f:#C0A0551F; --fg:#4FBD8C; --fg-f:#4FBD8C1F;
  --ga:#45B0BF; --ga-f:#45B0BF1F;
  --ok:#5CBF8B; --ok-f:#5CBF8B22; --warn:#D3A445; --warn-f:#D3A44522;
}}
* {{ box-sizing: border-box; }}
body {{
  background: var(--bg); color: var(--ink);
  font: 400 15px/1.6 "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}}
.wrap {{ max-width: 1290px; margin: 0 auto; padding: 40px 20px 72px; display: flex; flex-direction: column; gap: 48px; }}
.col {{ max-width: 68ch; }}
h1, h2, h3 {{ font-family: "IBM Plex Sans Condensed", "IBM Plex Sans", sans-serif; font-weight: 600; text-wrap: balance; margin: 0; }}
h1 {{ font-size: clamp(34px, 5.5vw, 52px); line-height: 1.02; letter-spacing: -0.015em; }}
h2 {{ font-size: 25px; letter-spacing: -0.005em; }}
h3 {{ font-size: 16px; }}
p {{ margin: 0 0 14px; }}
p:last-child {{ margin-bottom: 0; }}
code {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 0.86em; background: var(--panel2); padding: 1px 5px; border-radius: 2px; }}
em {{ font-style: italic; }}
.eyebrow {{
  font-family: "IBM Plex Mono", monospace; font-size: 11px; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--molten); margin-bottom: 14px;
}}
header .deck {{ font-size: 18px; line-height: 1.55; color: var(--ink2); margin-top: 18px; max-width: 62ch; }}
.facts {{ display: flex; flex-wrap: wrap; gap: 8px 26px; margin-top: 22px;
  font-family: "IBM Plex Mono", monospace; font-size: 11.5px; color: var(--ink3); letter-spacing: 0.02em; }}
.facts b {{ color: var(--ink); font-weight: 500; }}
.rule {{ height: 1px; background: var(--rule); border: 0; margin: 0; }}
figure {{ margin: 0; }}
figcaption {{ font-size: 13px; color: var(--ink2); margin-top: 14px; max-width: 78ch; }}
.scroller {{ overflow-x: auto; padding-bottom: 6px; }}
svg.tree {{ width: 1250px; max-width: none; height: auto; display: block; }}
svg.pwr {{ width: 100%; max-width: 900px; height: auto; display: block; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 10px 24px; align-items: center; margin-bottom: 18px;
  font-family: "IBM Plex Mono", monospace; font-size: 11px; color: var(--ink2); }}
.legend span {{ display: inline-flex; align-items: center; gap: 7px; }}
.sw {{ width: 24px; height: 12px; border-radius: 2px; display: inline-block; }}
.sw-built {{ background: var(--panel); border: 1px solid var(--ink); }}
.sw-draft {{ border: 1px dashed var(--ink3); }}
.sw-fluid {{ background: var(--panel); border: 1px solid var(--ink); border-radius: 6px; }}
.sw-cap {{ background: var(--vf-f); border: 1px solid var(--vf); border-left: 3px solid var(--vf); }}
.sw-loc {{ background: var(--molten); height: 3px; border-radius: 0; }}
.sw-term {{ background: var(--panel); border: 1px solid var(--ink); box-shadow: 0 0 0 3px var(--bg), 0 0 0 4px var(--ink3); }}
.sw-loop {{ border-top: 2px dashed var(--helium); height: 0; }}
.badge-key {{ display: inline-flex; align-items: center; justify-content: center; width: 15px; height: 15px;
  border-radius: 50%; background: var(--warn-f); border: 1px solid var(--warn); color: var(--warn);
  font: 700 10px "IBM Plex Mono", monospace; font-style: normal; }}

/* ---- SVG type and marks ---- */
.band {{ fill: var(--band); }}
.panel {{ fill: var(--panel); stroke: var(--rule); }}
.t-panelh {{ font: 500 11px "IBM Plex Mono", monospace; letter-spacing: 0.13em; fill: var(--ink3); }}
.t-src {{ font: 500 12px "IBM Plex Sans", sans-serif; fill: var(--ink); }}
.t-srcsub {{ font: 400 11.5px "IBM Plex Sans", sans-serif; fill: var(--ink3); }}
.t-node {{ font: 500 11.5px "IBM Plex Sans", sans-serif; fill: var(--ink); text-anchor: middle; }}
.t-note {{ font: 400 9.5px "IBM Plex Mono", monospace; fill: var(--ink3); text-anchor: middle; }}
.t-chip {{ font: 500 9.5px "IBM Plex Mono", monospace; }}
.t-chiptag {{ font: 500 9.5px "IBM Plex Mono", monospace; text-anchor: end; opacity: 0.8; }}
.t-chipsub {{ font: 500 9px "IBM Plex Mono", monospace; }}
.t-edge {{ font: 400 10px "IBM Plex Sans", sans-serif; fill: var(--ink2); }}
.t-tap {{ font: 500 10px "IBM Plex Mono", monospace; fill: var(--molten); }}
.t-stub {{ font: 400 9.5px "IBM Plex Mono", monospace; fill: var(--ink3); }}
.t-tnum {{ font: 700 15px "IBM Plex Mono", monospace; fill: var(--ink); text-anchor: end; }}
.t-tname {{ font: 500 9.5px "IBM Plex Mono", monospace; fill: var(--ink2); letter-spacing: 0.06em; text-anchor: end; }}
.t-tmach {{ font: 400 9.5px "IBM Plex Sans", sans-serif; fill: var(--ink3); text-anchor: end; }}
.t-rail {{ font: 500 10px "IBM Plex Mono", monospace; letter-spacing: 0.18em; fill: var(--ink3); text-anchor: middle; }}
.t-array {{ font: 700 17px "IBM Plex Sans Condensed", sans-serif; letter-spacing: 0.09em; fill: var(--molten); text-anchor: middle; }}
.t-arraysub {{ font: 400 10.5px "IBM Plex Mono", monospace; fill: var(--ink2); text-anchor: middle; }}
.t-vac {{ font: 400 10px "IBM Plex Sans", sans-serif; font-style: italic; fill: var(--ink3); }}
.n-built {{ fill: var(--panel); stroke: var(--ink); stroke-width: 1; }}
.n-draft {{ fill: none; stroke: var(--ink3); stroke-width: 1; stroke-dasharray: 5 3; }}
.n-array {{ fill: var(--molten-f); stroke: var(--molten); stroke-width: 1.5; }}
.n-term {{ fill: none; stroke: var(--ink3); stroke-width: 1; }}
.term-array {{ stroke: var(--molten); }}
.badge {{ fill: var(--warn-f); stroke: var(--warn); stroke-width: 1; }}
.t-badge {{ font: 700 10px "IBM Plex Mono", monospace; fill: var(--warn); text-anchor: middle; }}
.chip {{ stroke-width: 1; }}
.ed {{ fill: none; stroke: var(--ink3); stroke-width: 1; }}
.ed.tap {{ stroke: var(--molten); marker-end: url(#ahm); }}
.ed.molten {{ stroke: var(--molten); stroke-width: 1.5; marker-end: url(#ahm); }}
.ed.cor {{ stroke: var(--cor); }}
.ed.dash {{ stroke-dasharray: 4 3; }}
.ed.loop {{ stroke: var(--helium); stroke-dasharray: 6 3; marker-end: url(#ahh); }}
.ed.sci {{ stroke: var(--ink3); stroke-dasharray: 6 3; }}
.rail {{ fill: none; stroke: var(--rule); stroke-width: 5; stroke-linecap: round; }}
.rail-l {{ stroke: var(--molten); opacity: 0.32; }}
.head {{ fill: var(--ink3); }}
.head-m {{ fill: var(--molten); }}
.head-h {{ fill: var(--helium); }}
.lbl-bg {{ fill: var(--band); }}

/* ---- table ---- */
table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
th {{ font: 500 10.5px "IBM Plex Mono", monospace; letter-spacing: 0.11em; text-transform: uppercase;
  color: var(--ink3); text-align: left; padding: 0 14px 8px 0; border-bottom: 1px solid var(--rule); }}
td {{ padding: 14px 14px 14px 0; border-bottom: 1px solid var(--rule); vertical-align: top; }}
td:last-child, th:last-child {{ padding-right: 0; width: 92px; }}
.tk {{ width: 46px; }}
.tnum {{ font: 700 13px "IBM Plex Mono", monospace; color: var(--ink); }}
.tn {{ width: 250px; font-weight: 500; }}
.tm {{ font: 400 12px "IBM Plex Sans", sans-serif; color: var(--ink3); margin-top: 4px; }}
.ta {{ color: var(--ink2); font-size: 13.5px; line-height: 1.5; }}
.pill {{ display: inline-block; font: 500 10px "IBM Plex Mono", monospace; letter-spacing: 0.05em;
  padding: 3px 7px; border-radius: 2px; white-space: nowrap; }}
.p-built {{ background: var(--ok-f); color: var(--ok); }}
.p-draft {{ background: var(--panel2); color: var(--ink3); }}
.p-mixed {{ background: var(--warn-f); color: var(--warn); }}

.risks {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(430px, 1fr)); gap: 16px 40px; }}
.risk {{ border-top: 1px solid var(--rule); padding-top: 14px; }}
.rh {{ display: flex; align-items: center; gap: 9px; margin-bottom: 8px; }}
.rh h3 {{ margin: 0; }}
.rh .pill {{ margin-left: auto; }}
.risk p {{ font-size: 13.5px; color: var(--ink2); line-height: 1.55; }}
.risk .when {{ font: 500 12px "IBM Plex Mono", monospace; color: var(--ink); margin-top: 10px; }}
.two {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 34px; }}
.note h3 {{ margin-bottom: 8px; }}
.note p {{ font-size: 14px; color: var(--ink2); }}
.spine {{ font-family: "IBM Plex Mono", monospace; font-size: 12.5px; line-height: 2.1; color: var(--ink2); }}
.spine b {{ color: var(--ink); font-weight: 500; }}
.spine .arw {{ color: var(--molten); padding: 0 4px; }}
footer {{ font-size: 12.5px; color: var(--ink3); }}
footer a {{ color: var(--ink2); }}
@media (prefers-reduced-motion: no-preference) {{ html {{ scroll-behavior: smooth; }} }}
</style>

<div class="wrap">
<header>
  <div class="eyebrow">Space Age Extended · the Core of the Shattered Planet</div>
  <h1>Kamacite to Ignition</h1>
  <p class="deck">The Core's whole production line, drawn end to end: what the planet gives you,
  what the corridor has to carry, and the eleven tiers between a vent and the array that ends the game.
  Solid boxes are in the mod today; dashed boxes are the draft in
  <code>design/06&#8209;core&#8209;production&#8209;tree.md</code>.</p>
  <div class="facts">
    <span><b>11</b> tiers</span><span><b>34</b> nodes</span>
    <span><b>3</b> stages deep today &rarr; <b>10</b> drafted</span>
    <span><b>5</b> capstones, entering at T5, T6 and T7</span>
    <span><b>100</b> segments to fire</span>
  </div>
</header>

<hr class="rule">

<figure>
  <div class="legend">
    <span><i class="sw sw-built"></i>built</span>
    <span><i class="sw sw-draft"></i>drafted</span>
    <span><i class="sw sw-fluid"></i>fluid</span>
    <span><i class="sw sw-cap"></i>arrives by freight</span>
    <span><i class="sw sw-loc"></i>local resource</span>
    <span><i class="sw sw-term"></i>the line ends here</span>
    <span><i class="sw sw-loop"></i>recovered and reused</span>
    <span><i class="badge-key">!</i>can stall or dead-end</span>
  </div>
  <div class="scroller">{TREE}</div>
  <figcaption><strong>Figure 1.</strong> Every tier is anchored on something the Core has or lacks, and reads
  left to right within itself, top to bottom between tiers. The two rails are the point of the planet: nothing
  organic, wet or combustible is on the left, and the right-hand rail never stops running — carbon is recovered
  at about 90%, not consumed once. Two capstones (bio-polymer and cryoprotectant) enter deep in the line rather
  than at the last moment, so a lagging cross-planet tree starves the Core early and visibly. Two kinds of mark were
  added after tracing every sink: a double edge where the line genuinely ends, and an amber <strong>!</strong>
  where a product can back up and stall the tier that makes it.</figcaption>
</figure>

<hr class="rule">

<section>
  <h2>Where it can stall</h2>
  <p class="col" style="color:var(--ink2);margin:10px 0 26px">Nothing in the mod is orphaned — the three
  products no recipe consumes are taken by the silo's rocket parts, by research, and by being fired. What is
  worth watching is the shape of the sinks: an output that cannot leave stops the recipe that made it, and two
  of the Core's outputs are unconditional.</p>
  <div class="risks">
    <div class="risk">
      <div class="rh"><span class="badge-key">!</span><h3>Steam</h3><span class="pill p-mixed">built line</span></div>
      <p>Both settling recipes emit it every craft — 150 metal-heavy, 900 quenched — and nothing in the mod
      consumes it. Its only sink is a vanilla turbine, which stops drawing the moment the grid is satisfied. A
      well-powered Core therefore stalls its own settling, and settling is the root of the whole tree.</p>
      <p class="when">Decide during balancing: feature, or defect needing a steam sink that is not power.</p>
    </div>
    <div class="risk">
      <div class="rh"><span class="badge-key">!</span><h3>Dross</h3><span class="pill p-mixed">built line</span></div>
      <p>Two per settle, into an item slot that blocks when full. Whisker beds are a one-time cost, so
      resettling is the only steady sink — about one resettler per seven vessels, for 4% more molten kamacite.
      The ratio works; what matters is that it is mandatory rather than an efficiency nicety.</p>
      <p class="when">Make its necessity legible rather than discoverable by stalling.</p>
    </div>
    <div class="risk">
      <div class="rh"><span class="badge-key">!</span><h3>Kamacite fines</h3><span class="pill p-draft">created by the draft</span></div>
      <p>T1 makes them as tailings and T3's metal carbonyl is their only sink — while the same draft routes
      kamacite plate through crushed ore, so beneficiation stops being optional. Build T1 before T3, as the
      draft's own order suggests, and the crusher backs up and takes plate with it.</p>
      <p class="when">Before implementing T1: give fines a sink that exists at T1, or land T3 alongside it.</p>
    </div>
    <div class="risk">
      <div class="rh"><span class="badge-key">!</span><h3>Welded plate</h3><span class="pill p-draft">created by the draft</span></div>
      <p>Today the coil assembly consumes two, which keeps cold welding on every segment's critical path. The
      draft's T9 assembly drops it, leaving only arc masts, the roboport and the array — all one-time builds.
      One of the Core's four signature mechanics then quietly runs out of work.</p>
      <p class="when">Before implementing T8–T9: keep it in the coil assembly, or route it into the vacuum cell.</p>
    </div>
  </div>
</section>

<hr class="rule">

<section>
  <h2>Tier by tier</h2>
  <p class="col" style="color:var(--ink2);margin-top:10px;margin-bottom:24px">Each step earns its place by a
  mechanic rather than by length. The test: if this step were deleted, would the player notice anything other
  than fewer clicks?</p>
  <table>
    <thead><tr><th></th><th>Tier</th><th>Anchored on</th><th>State</th></tr></thead>
    <tbody>
{rows}
    </tbody>
  </table>
</section>

<hr class="rule">

<section>
  <h2>What the line runs on</h2>
  <p class="col" style="color:var(--ink2);margin:10px 0 26px">Nothing burns on the Core — pressure 5 refuses
  every combustion prototype — so power comes off the melt, out of the corridor's chunks, or out of the sky.
  The array's 50 MW is the reason the settling choice bites.</p>
  <figure>
    {POWER}
    <figcaption><strong>Figure 2.</strong> One settling vessel is worth roughly one turbine when quenched, and
    about six times the electricity for less than half the metal. Every megawatt the array draws while it runs is
    melt that was not cast into the segments it also needs.</figcaption>
  </figure>
</section>

<hr class="rule">

<section class="two">
  <div class="note">
    <h3>What is actually built</h3>
    <p>Three stages from local resource to Field Coil Segment, which is shorter than Gleba's nutrient chain and
    does not keep design §5's promise of the mod's largest chain:</p>
    <p class="spine"><b>molten kamacite</b><span class="arw">&rarr;</span><b>settled melt</b><span class="arw">&rarr;</span><b>cast ingot</b><span class="arw">&rarr;</span><b>homogenised ingot</b><span class="arw">&rarr;</span><b>field conductor</b></p>
    <p>The draft takes that to ten, adding 14 items and 2 fluids — none of them one-in, one-out. Every added tier
    either branches (T1's two streams, T5's two grades), loops (T3's recovered carbon monoxide) or converges
    (T6's three inputs).</p>
  </div>
  <div class="note">
    <h3>What would make it worse</h3>
    <p><strong>Tedium instead of depth.</strong> Ten tiers of one-in-one-out recipes is a conveyor, not a factory.
    Any new step that neither branches, loops nor converges should be cut.</p>
    <p><strong>The corridor becoming the bottleneck.</strong> Carbon recovery is the dial. If freight limits the
    endgame it turns into a shipping puzzle, which is Space Age's problem, not this mod's.</p>
    <p><strong>Burying the capstones.</strong> Moving two of them deeper makes lagging trees bite sooner, but the
    player still has to see five planets in the thing they are building — which is why the intermediates keep the
    capstones' names in their ingredient lists.</p>
  </div>
</section>

<hr class="rule">

<footer>
  Drawn from <code>design/06-core-production-tree.md</code> and the prototypes that exist today
  (<code>prototypes/core/recipes.lua</code>, <code>intermediates.lua</code>, <code>endgame.lua</code>,
  <code>storms.lua</code> and <code>corridor.lua</code>). Four of the five capstone products are still
  one-ingredient stubs, so every arrival on the right-hand rail below F&#8596;A is a placeholder in the mod as it
  stands. Quantities shown are the ones in the source; everything in the draft tiers is a first guess. The sink analysis
  behind the marks — how it was checked, and what it did not check — is written up in
  <code>design/07-sinks-and-dead-ends.md</code>.
</footer>
</div>
"""
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(HTML)
print(f"wrote {OUT} ({len(HTML):,} bytes)")
