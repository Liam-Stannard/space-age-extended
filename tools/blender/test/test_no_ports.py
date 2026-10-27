#!/usr/bin/env python3
"""render.sh --ports on a model that declares no ports: "no ports", and the run goes on.

  python3 tools/blender/test/test_no_ports.py <out-dir>

Nothing is rendered: render.sh is run through a copy of tools/blender whose paths.conf names a
stand-in Blender (test_render_options.py's stand_in_tree), on the CPU so no probe runs. The
stand-in is a Python script. Run as a model's main pass it declares a 1 x 1 building, one
direction, a plate alone, with the ports in $FAKE_PORTS (JSON), and writes its plate at 4x;
run with --ports or --icon it renders nothing and exits 3, so any pass render.sh should not
have started fails the run. Everything is written under <out-dir> and kept.

Exits 0 when every case below comes out as listed, 1 naming those that do not.

  none       ports [], --ports: exit 0, "no ports" printed, render.done "exit 0", the main
             sheets packed; no Blender --ports pass (no blender-ports.log), and no ports-hi,
             ports or sheets/ports
  none+icon  ports [], --ports --icon: "no ports" printed, and the run goes on to the icon
             pass (blender-icon.log written; the stand-in fails it, exit 1)
  declared   one port on N, --ports: the --ports pass runs (blender-ports.log written; the
             stand-in fails it, exit 1), and "no ports" is not printed
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from test_render_options import stand_in_tree  # noqa: E402

FAILED = []

STAND_IN = """#!/usr/bin/env python3
# a stand-in Blender for test_no_ports.py: the main pass declares a 1 x 1 plate with $FAKE_PORTS;
# --ports and --icon render nothing and fail
import json, os, sys
from PIL import Image
args = sys.argv[sys.argv.index("--") + 1:]
if "--ports" in args or "--icon" in args:
    print("stand-in Blender: renders nothing for", args[1:], file=sys.stderr)
    sys.exit(3)
out = args[0]
os.makedirs(out, exist_ok=True)
decl = dict(footprint=[1, 1], canvas=[96, 96], directions="one",
            passes=[dict(name="idle", kind="plate", sheet="base")], animations=[],
            ports=json.loads(os.environ["FAKE_PORTS"]), rig=dict(elevation=60.0, px_per_tile=64))
with open(os.path.join(out, "render.json"), "w") as f:
    json.dump(decl, f, indent=1)
im = Image.new("RGBA", (384, 384))
for y in range(64, 320):        # a fine and a coarse grain, so finish.py has texture to measure
    for x in range(64, 320):
        v = 70 + (x * 7 + y * 13) % 23 + 30 * ((x // 32 + y // 32) % 2)
        im.putpixel((x, y), (v, v - 8, v - 18, 255))
im.save(os.path.join(out, "idle.png"))
"""


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(f"{case}: {detail}")


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: test_no_ports.py <out-dir>")
    d = os.path.abspath(sys.argv[1])
    if os.path.exists(d):
        shutil.rmtree(d)                    # each case's "nothing rendered" reads a fresh directory
    os.makedirs(d)
    blender = os.path.join(d, "blender")
    with open(blender, "w") as f:
        f.write(STAND_IN)
    os.chmod(blender, 0o755)
    render_sh = stand_in_tree(d, blender)
    model = os.path.join(HERE, "box.py")    # never run: the stand-in ignores the model it is given

    def render(name, ports, *flags):
        o = os.path.join(d, name)
        env = dict(os.environ, SAE_BLENDER_DEVICE="CPU", FAKE_PORTS=json.dumps(ports))
        p = subprocess.run(["bash", render_sh, model, o, *flags], capture_output=True, text=True, env=env)
        done = os.path.join(o, "render.done")
        done = open(done).read().strip() if os.path.isfile(done) else None
        return o, p.returncode, p.stdout + p.stderr, done

    def there(o, *names):
        return [n for n in names if os.path.exists(os.path.join(o, n))]

    print("no ports (render.sh --ports, a stand-in Blender)")
    o, code, text, done = render("none", [], "--ports")
    check("ports [], --ports: exit 0, 'no ports' printed, render.done exit 0",
          code == 0 and "no ports" in text and done == "exit 0", f"exit {code}, done {done!r}: {text[-400:]}")
    check("ports [], --ports: the main sheets packed", os.path.isfile(os.path.join(o, "sheets", "meta.json")),
          text[-400:])
    left = there(o, "blender-ports.log", "ports-hi", "ports", os.path.join("sheets", "ports"))
    check("ports [], --ports: no --ports pass, nothing of one left", not left, f"found {left}")

    o, code, text, done = render("none-icon", [], "--ports", "--icon")
    check("ports [], --ports --icon: 'no ports' printed, the icon pass runs (the stand-in fails it)",
          "no ports" in text and there(o, "blender-icon.log") and not there(o, "blender-ports.log")
          and code == 1 and done == "exit 1", f"exit {code}, done {done!r}: {text[-400:]}")

    o, code, text, done = render("declared", [dict(tile=[0, 0], face="N")], "--ports")
    check("a port on N, --ports: the --ports pass runs (the stand-in fails it), no 'no ports'",
          there(o, "blender-ports.log") and "no ports" not in text and code == 1 and done == "exit 1",
          f"exit {code}, done {done!r}: {text[-400:]}")

    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
