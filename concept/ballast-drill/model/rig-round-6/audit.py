"""The support audit (task ballast-drill-ports, T03i: "Audit every part for support and list any
that float, before and after"). Imported by rig_parts.py (pass "support") and rig_take.py
(SAE_RIG_R5: the T03h build, for the before).

What it checks, on the drill at frame 0 (ring raised), dry and wet north:
  1. Connection: every mesh is a node; two touch when their BVHs overlap or a sampled vertex of
     either lies within TOUCH of the other's surface. A part touching the ground (its lowest point
     under 0.01) is grounded; everything reached from a grounded part through touching parts
     stands. FLOAT lists what does not: a part with nothing under or beside it to carry it.
     The ring and its ropes are checked as one assembly with the guide columns it rides (it hangs
     on the ropes; at frame 0 it touches nothing by design).
  2. Bearing: every structural part (a casting, wall, cabinet, bastion, roof, floor, plate,
     girder, post: its plan at least 0.25 across) is sampled on a 0.03 grid under its underside;
     a sample is borne if another part (or the ground) lies within BEAR straight under it. OPEN
     lists each structural part with any unborne underside: the share of its underside over open
     air, the deepest gap, and which parts carry the rest -- the voids under parts.
Writes <out>/support-<label>.json and prints SUPPORT lines.
"""
import json
import math
import os

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

TOUCH = 0.006
BEAR = 0.012
STRUCT = 0.25


def _mesh(G, o, dg):
    Binv = G["BODY"].matrix_world.inverted()
    e = o.evaluated_get(dg)
    me = e.to_mesh()
    mw = Binv @ o.matrix_world
    vs = [mw @ v.co for v in me.vertices]
    me.calc_loop_triangles()             # Blender's own tessellation: a concave n-gon is not a fan
    ps = [tuple(t.vertices) for t in me.loop_triangles]
    e.to_mesh_clear()
    return vs, ps


def support(G, rig, label, wet_dirs=("north",)):
    G["pose"](0)
    G["chain"](0)
    out_dir = G["OUT_DIR"]
    os.makedirs(out_dir, exist_ok=True)
    skip = ("dust", "ore", "chute", "_cutters")
    res = {"label": label, "views": {}}
    if os.environ.get("SAE_AUDIT_DEBUG"):
        wet_dirs = ()
    for view in ("dry",) + tuple(f"wet-{d}" for d in wet_dirs):
        if view.startswith("wet"):
            d = view.split("-", 1)[1]
            rig.place_pockets(d)
            extra = [f"rig-behind-{d}", f"rig-front-{d}"]
        else:
            rig.place_pockets(None)
            extra = []
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        groups = [g for g in G["PARTS"] if g not in skip and not g.startswith("rig-")
                  and not (g.startswith("door-") and g != "door-N")] + extra
        objs, data, samples = [], [], []
        for g in dict.fromkeys(groups):
            for o in G["PARTS"].get(g, []):
                if o.type not in ("MESH", "CURVE") or (o.hide_render and g not in extra):
                    continue
                vs, ps = _mesh(G, o, dg)
                if not ps:
                    continue
                objs.append((g, o))
                data.append((vs, ps))
                # the points that test a touch: the vertices and every face's centre, at most 600
                cs = [sum((vs[k] for k in p), Vector()) / len(p) for p in ps]
                pts = vs + cs
                samples.append(pts[::max(1, len(pts) // 600)])
        trees = [BVHTree.FromPolygons(vs, ps) for vs, ps in data]
        boxes = [(Vector([min(v[i] for v in vs) for i in range(3)]), Vector([max(v[i] for v in vs) for i in range(3)]))
                 for vs, _ in data]
        N = len(objs)
        adj = [set() for _ in range(N)]
        for i in range(N):
            lo, hi = boxes[i]
            for j in range(i + 1, N):
                l2, h2 = boxes[j]
                if any(lo[k] > h2[k] + TOUCH or l2[k] > hi[k] + TOUCH for k in range(3)):
                    continue
                if trees[i].overlap(trees[j]):
                    adj[i].add(j)
                    adj[j].add(i)
                    continue
                hit = False
                for a, b in ((i, j), (j, i)):
                    for v in samples[a]:
                        h = trees[b].find_nearest(v, TOUCH)
                        if h[0] is not None:
                            hit = True
                            break
                    if hit:
                        break
                if hit:
                    adj[i].add(j)
                    adj[j].add(i)
        # the ring hangs on its ropes from the winches: one assembly with what it rides
        ring_ids = [i for i, (g, o) in enumerate(objs) if g == "ring"]
        if ring_ids:
            anchor = [i for i, (g, o) in enumerate(objs) if o.active_material and o.active_material.name == "guide"]
            for i in ring_ids:
                for j in anchor:
                    adj[i].add(j)
                    adj[j].add(i)
        seen = set(i for i in range(N) if boxes[i][0].z < 0.01)
        todo = list(seen)
        while todo:
            i = todo.pop()
            for j in adj[i]:
                if j not in seen:
                    seen.add(j)
                    todo.append(j)
        floats = []
        for i in range(N):
            if i in seen:
                continue
            g, o = objs[i]
            lo, hi = boxes[i]
            m = o.active_material.name if o.active_material else ""
            floats.append(dict(name=o.name, mat=m, group=g, lo=[round(c, 3) for c in lo], hi=[round(c, 3) for c in hi]))
        # bearing of the structural parts
        opens = []
        for i in range(N):
            g, o = objs[i]
            lo, hi = boxes[i]
            if g in ("ring",) or lo.z < 0.01 or min(hi.x - lo.x, hi.y - lo.y) < STRUCT and max(hi.x - lo.x, hi.y - lo.y) < 0.5:
                continue
            m = o.active_material.name if o.active_material else ""
            if m in ("bolt", "tie", "seam", "stencil", "stencil_worn", "cable", "grease", "oil", "polish") or \
                    m.startswith("c_") or m.startswith("hose"):
                continue
            step = 0.03
            nx_, ny_ = max(1, int((hi.x - lo.x) / step)), max(1, int((hi.y - lo.y) / step))
            n_s, n_open, deep, carriers, pts_open = 0, 0, 0.0, {}, []
            cands = [k for k in range(N) if k != i and boxes[k][0].z <= hi.z and boxes[k][0].x <= hi.x and
                     boxes[k][1].x >= lo.x and boxes[k][0].y <= hi.y and boxes[k][1].y >= lo.y]
            for a in range(nx_):
                for b in range(ny_):
                    x = lo.x + (a + 0.5) * (hi.x - lo.x) / nx_
                    y = lo.y + (b + 0.5) * (hi.y - lo.y) / ny_
                    h = trees[i].ray_cast(Vector((x, y, lo.z - 0.5)), Vector((0, 0, 1)), hi.z - lo.z + 1)
                    if h[0] is None:
                        continue
                    zu = h[0].z
                    n_s += 1
                    org = Vector((x, y, zu - 0.0005))
                    # straight down from just under it, against every other part whose box is under the point
                    org = Vector((x, y, zu - 0.0005))
                    gap, by = zu, "ground"
                    for k in cands:
                        lk, hk = boxes[k]
                        if not (lk.x <= x <= hk.x and lk.y <= y <= hk.y and lk.z <= zu):
                            continue
                        hb = trees[k].ray_cast(org, Vector((0, 0, -1)), 10)
                        if hb[0] is None:
                            continue
                        gk = 0.0 if hb[1].z < -1e-6 else zu - hb[0].z
                        if gk < gap:
                            gap, by = gk, objs[k][1].name
                    if gap > BEAR:
                        n_open += 1
                        deep = max(deep, gap)
                        pts_open.append([round(x, 3), round(y, 3), round(zu, 3), round(gap, 3), by])
                    else:
                        carriers[by] = carriers.get(by, 0) + 1
            if n_s and n_open:
                opens.append(dict(name=o.name, mat=m, group=g, share=round(n_open / n_s, 3), samples=n_s,
                                  deepest_gap=round(deep, 3), lo=[round(c, 3) for c in lo], hi=[round(c, 3) for c in hi],
                                  carried_by=sorted(carriers, key=lambda k: -carriers[k])[:6],
                                  open_points=pts_open[::max(1, len(pts_open) // 40)]))
        opens.sort(key=lambda r: -r["share"] * r["samples"])
        res["views"][view] = dict(parts=N, grounded_reach=len(seen), floating=floats, open_under=opens)
        print(f"SUPPORT {label} {view}: {N} parts; {len(floats)} float; {len(opens)} structural parts with open air "
              f"under some of their underside", flush=True)
        for f_ in floats:
            print(f"SUPPORT FLOAT {view} {f_['name']} [{f_['mat']}] {f_['group']} lo {f_['lo']} hi {f_['hi']}", flush=True)
        for r in opens:
            print(f"SUPPORT OPEN {view} {r['name']} [{r['mat']}] {r['group']} share {r['share']} of {r['samples']}, "
                  f"gap to {r['deepest_gap']}; lo {r['lo']} hi {r['hi']}; carried by {r['carried_by']}", flush=True)
    rig.place_pockets(None)
    fn = os.path.join(out_dir, "support-" + label.split(" ")[0] + ".json")
    with open(fn, "w") as f:
        json.dump(res, f, indent=1)
    print("SUPPORT written", fn, flush=True)
