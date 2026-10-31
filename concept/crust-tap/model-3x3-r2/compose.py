#!/usr/bin/env python3
"""T15 (gas-pump-3x3): the Gas Pump's packed sheets with vanilla's pipe (joined) and vanilla's pipe cover
(unconnected) at its one connection, four directions, drawn in the engine's order; the reach past the 3x3 edge
and every vanilla pixel shown over the building, measured.

  python3 compose.py <sheets-dir> <out-dir> [--ports] [--stub <masks-dir>] [--ew-pipe over|under]

The method is evidence/ballast-drill-t03m/compose.py's, for this building (64 px a tile, the entity origin at the
canvas centre, each sheet at its meta.json shift):
  shadows       the shadow sheet and vanilla's cover shadow, one union at half strength;
  before        what the engine sorts before the pump: a vanilla pipe on a tile north of its centre, and the north
                cover (the T13 client shots: the pumpjack's and the Gas Pump's north cover is drawn behind them);
                facing east or west the pipe's tile is level with the centre: under by default (measure.py's
                stricter reading), --ew-pipe over to draw the other;
  the pump      base (the plate), then mech frame 0 (the engine always draws it); the glass only while working,
                left out; with --ports, the pipe_picture as shipped (gp_port: north behind, the rest over);
  after         a vanilla pipe on a tile south of the centre; the south, east and west covers (secondary draw
                order 1: over the pump).
Measured per direction and state (alpha >= 128, shadows not counted):
  reach_px      the furthest opaque px past the footprint edge in the outlet's lane (the target tile's width),
                of the pump's own sheets and of everything drawn (vanilla's cover reaches N 22, E 13, S 20, W 12)
  over          vanilla pixels shown over an opaque px of the pump: count, and how far into the footprint they
                reach past the edge line (rise_px); with --stub, how many of them lie off the stub (the fitting's
                own mask, rendered by the model: everything else of the pump is "body")
  cover_shown   the share of the cover's opaque px that shows (a cover drawn behind the pump can be hidden by it)
"""
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw

FD = "/mnt/data/SteamLibrary/steamapps/common/Factorio/data/base/graphics/entity/"
PPT = 64
S = 512
GROUND = (74, 66, 58)
DIRS = ("north", "east", "south", "west")
FACE = {"north": "N", "east": "E", "south": "S", "west": "W"}
VEC = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
VAN_REACH = {"N": 22, "E": 13, "S": 20, "W": 12}          # vanilla's cover (evidence/gas-pump-outlet reach.json)
HALF = 1.5


def opt(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def load(p):
    return Image.open(p).convert("RGBA")


def layer(im, shift, at=(0, 0)):
    c = Image.new("RGBA", (S, S))
    c.alpha_composite(im, (round(S / 2 + (at[0] + shift[0]) * PPT - im.width / 2),
                           round(S / 2 + (at[1] + shift[1]) * PPT - im.height / 2)))
    return c


def solid(im):
    return im.getchannel("A").point(lambda v: 255 if v >= 128 else 0)


class Sheets:
    def __init__(self, d):
        self.d = d
        self.meta = json.load(open(os.path.join(d, "meta.json")))
        pm = os.path.join(d, "ports", "meta.json")
        self.ports = json.load(open(pm)) if os.path.isfile(pm) else {}

    def frame(self, stem, f=0):
        m = self.meta[stem]
        im = load(os.path.join(self.d, stem + ".png"))
        w, h = m["size"]
        line = m.get("line_length", 1)
        return im.crop(((f % line) * w, (f // line) * h, (f % line) * w + w, (f // line) * h + h)), m["shift"]


def lane_reach(mask, face, tgt):
    """Furthest px of mask past the footprint edge, in the target tile's lane."""
    a = mask.load()
    tx, ty = S / 2 + tgt[0] * PPT, S / 2 + tgt[1] * PPT
    e = PPT * HALF
    best = 0
    if face in "NS":
        xs = range(int(tx - 32), int(tx + 32))
        ys = range(0, int(S / 2 - e)) if face == "N" else range(int(S / 2 + e), S)
    else:
        ys = range(int(ty - 32), int(ty + 32))
        xs = range(int(S / 2 + e), S) if face == "E" else range(0, int(S / 2 - e))
    for y in ys:
        for x in xs:
            if a[x, y]:
                p = {"N": (S / 2 - e) - y, "S": y + 1 - (S / 2 + e), "E": x + 1 - (S / 2 + e), "W": (S / 2 - e) - x}[face]
                best = max(best, p)
    return best


def rise_into(mask, face):
    """How far px of mask reach past the edge line into the footprint (from the face's side)."""
    bb = mask.getbbox()
    if bb is None:
        return 0
    e = PPT * HALF
    return {"N": bb[3] - (S / 2 - e), "S": (S / 2 + e) - bb[1], "E": (S / 2 + e) - bb[0], "W": bb[2] - (S / 2 - e)}[face]


def count(m):
    return sum(1 for v in m.tobytes() if v)


def compose(sh, d, mode, ports=False, stub=None, ew_pipe="under"):
    f = FACE[d]
    vx, vy = VEC[f]
    tile = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}[f]
    tgt = (tile[0] + vx, tile[1] + vy)
    cov_name = {"N": "north", "E": "east", "S": "south", "W": "west"}[f]
    if mode == "pipe":
        van = load(FD + "pipe/pipe-straight-" + ("vertical" if f in "NS" else "horizontal") + ".png")
        van_sh = None
        before = tgt[1] < 0 or (tgt[1] == 0 and ew_pipe == "under")
    else:
        van = load(FD + f"pipe-covers/pipe-cover-{cov_name}.png")
        van_sh = load(FD + f"pipe-covers/pipe-cover-{cov_name}-shadow.png")
        before = f == "N"
    V = layer(van, (0, 0), tgt)
    shadows = [layer(*sh.frame(f"shadow-{d}"))] + ([layer(van_sh, (0, 0), tgt)] if van_sh else [])
    acc = Image.new("L", (S, S))
    for s_ in shadows:
        acc = ImageChops.lighter(acc, s_.getchannel("A"))
    c = Image.new("RGBA", (S, S), GROUND + (255,))
    shl = Image.new("RGBA", (S, S))
    shl.putalpha(acc.point(lambda v: v // 2))
    c.alpha_composite(shl)
    bld = Image.new("RGBA", (S, S))
    bld.alpha_composite(layer(*sh.frame(f"base-{d}")))
    bld.alpha_composite(layer(*sh.frame(f"mech-{d}", 0)))
    port_back = port_front = None
    if ports and sh.ports:
        m = sh.ports[f"port-{f}"]
        P = layer(load(os.path.join(sh.d, "ports", f"port-{f}.png")), m["shift"], tgt)
        port_back, port_front = (P, None) if f == "N" else (None, P)
    own = bld.copy()
    for p_ in (port_back, port_front):
        if p_ is not None:
            own = Image.alpha_composite(p_, own) if p_ is port_back else Image.alpha_composite(own, p_)
    if port_back is not None:
        c.alpha_composite(port_back)
    if before:
        c.alpha_composite(V)
    c.alpha_composite(bld)
    if port_front is not None:
        c.alpha_composite(port_front)
    if not before:
        c.alpha_composite(V)
    Vs, Os = solid(V), solid(own)
    shown = Vs if not before else ImageChops.subtract(Vs, solid(bld))
    over = ImageChops.multiply(shown, Os) if not before else Image.new("L", (S, S))
    res = dict(direction=d, face=f, state="joined" if mode == "pipe" else "unconnected",
               vanilla_drawn="under the pump" if before else "over the pump",
               reach_px=dict(pump=lane_reach(Os, f, tgt), all=lane_reach(ImageChops.lighter(Os, Vs), f, tgt),
                             vanilla_cover_bar=VAN_REACH[f]),
               over=dict(px=count(over), rise_px=rise_into(over, f)))
    if mode == "cover":
        res["cover_shown_pct"] = round(100 * count(shown) / max(1, count(Vs)), 1)
    if stub is not None:
        sm = os.path.join(stub, f"stub-{d}.png")
        if os.path.isfile(sm):
            mm = json.load(open(os.path.join(stub, "meta.json")))[f"stub-{d}"]
            St = solid(layer(load(sm), mm["shift"]))
            off = ImageChops.subtract(over, St)
            res["over"]["off_stub_px"] = count(off)
            res["over"]["off_stub_rise_px"] = rise_into(off, f)
            res["_off"] = off
    res["_over"], res["_tgt"] = over, tgt
    return c, res


def marked(c, res):
    out = c.copy()
    out.paste(Image.new("RGBA", (S, S), (255, 160, 0, 255)), (0, 0), res["_over"].point(lambda v: 110 if v else 0))
    if "_off" in res:
        out.paste(Image.new("RGBA", (S, S), (255, 0, 0, 255)), (0, 0), res["_off"].point(lambda v: 200 if v else 0))
    dr = ImageDraw.Draw(out, "RGBA")
    e = PPT * HALF
    dr.rectangle([S / 2 - e, S / 2 - e, S / 2 + e - 1, S / 2 + e - 1], outline=(255, 60, 60, 200))
    f, tgt = res["face"], res["_tgt"]
    tx, ty = S / 2 + tgt[0] * PPT, S / 2 + tgt[1] * PPT
    for lim, col in ((res["reach_px"]["all"], (255, 220, 0, 255)), (VAN_REACH[f], (0, 220, 255, 255))):
        if f == "N":
            dr.line([(tx + 34, S / 2 - e - lim), (tx + 44, S / 2 - e - lim)], fill=col, width=2)
        elif f == "S":
            dr.line([(tx + 34, S / 2 + e + lim - 1), (tx + 44, S / 2 + e + lim - 1)], fill=col, width=2)
        elif f == "E":
            dr.line([(S / 2 + e + lim - 1, ty + 34), (S / 2 + e + lim - 1, ty + 44)], fill=col, width=2)
        else:
            dr.line([(S / 2 - e - lim, ty + 34), (S / 2 - e - lim, ty + 44)], fill=col, width=2)
    return out


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    sh = Sheets(src)
    figs = []
    for d in DIRS:
        for mode in ("pipe", "cover"):
            c, r = compose(sh, d, mode, ports="--ports" in sys.argv, stub=opt("--stub"), ew_pipe=opt("--ew-pipe", "under"))
            c.convert("RGB").save(os.path.join(out, f"{d}-{mode}.png"))
            marked(c, r).convert("RGB").save(os.path.join(out, f"{d}-{mode}-marked.png"))
            figs.append({k: v for k, v in r.items() if not k.startswith("_")})
            print(json.dumps(figs[-1]))
    json.dump(figs, open(os.path.join(out, "compose.json"), "w"), indent=1)
