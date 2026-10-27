"""This tree's pack.py and preview.py run with T08h's glow floor set aside: for the tests that hold
this tree's sheets or previews byte for byte to a baseline from before T08h.

Since T08h pack.glow_layer judges a still glow's light against LAYER_FLOOR by its brightest channel
(pack.brightest), not its luma, so a faint deep blue keeps its fringe, and a blue speck now over the
floor is dropped by the speck filter, colour and all. test_glow_floor.py holds that change to a
baseline from before it (347bccc): only the still glows' sheets move. set_aside(pack) makes
pack.brightest PIL's L, so glow_layer is the old rule (test_glow_floor.py's old_rule, which that test
holds byte for byte to 347bccc's glow_layer) and nothing else changes: glow_layer is brightest's only
reader. command() runs this tree's pack.py or preview.py so, in a process of its own. pack.py and
preview.py themselves are not touched.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)

# argv: tools, this directory, a LIGHT_SHARE or "", the script, its args. pack.py is run through its
# main() (run as a script it would define brightest afresh); preview.py imports pack, so it is run as is.
BOOT = ("import os, runpy, sys; sys.path.insert(0, sys.argv[1]); sys.path.insert(1, sys.argv[2]); "
        "import pack, floor_aside; floor_aside.set_aside(pack); "
        "pack.LIGHT_SHARE = float(sys.argv[3]) if sys.argv[3] else pack.LIGHT_SHARE; "
        "sys.argv = sys.argv[4:]; "
        "pack.main(*sys.argv[1:]) if os.path.basename(sys.argv[0]) == 'pack.py' "
        "else runpy.run_path(sys.argv[0], run_name='__main__')")


def old_floor(rgb):
    """What glow_layer judged a light by against LAYER_FLOOR before T08h: its luma (PIL's L)."""
    return rgb.convert("L")


def set_aside(pack):
    """pack (a module) with its glow floor judged on luma, as before T08h (old_floor)."""
    pack.brightest = old_floor


def command(script, args, light_share=None):
    """The command that runs this tree's script ("pack.py" or "preview.py") with args, its glow floor
    set aside (set_aside); with light_share, pack.LIGHT_SHARE set to it first."""
    if script not in ("pack.py", "preview.py"):
        raise ValueError(f"floor_aside.command: {script} is not pack.py or preview.py")
    share = "" if light_share is None else repr(float(light_share))
    return [sys.executable, "-c", BOOT, TOOLS, HERE, share, os.path.join(TOOLS, script), *args]
