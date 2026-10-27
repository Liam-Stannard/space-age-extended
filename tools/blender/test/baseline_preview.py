"""A baseline's preview.py, run as preview.py has drawn a glow since T08f-3: for the tests that hold
this tree's preview.py byte for byte to a baseline's.

Since T08f-3 preview.py adds a glow's colour only where its alpha is above 0 (its docstring), and
pack.glow_layer, which every baseline's preview.py draws a glow pass through, leaves faint colour
on pixels it leaves clear: a baseline draws that haze, this tree does not. command() runs a
baseline's preview.py with its pack.glow_layer's colour cleared wherever its alpha is 0 (cleared,
this test's own), and nothing else changed, so a byte-for-byte match sets the haze aside and
nothing else. pack.py itself is not touched: a baseline's pack.py runs as it was.
"""
import os
import sys

from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))

# argv: the baseline's tools, this directory, preview.py, its args
BOOT = ("import runpy, sys; sys.path.insert(0, sys.argv[1]); sys.path.insert(1, sys.argv[2]); "
        "import pack, baseline_preview; baseline_preview.clear_haze(pack); "
        "sys.argv = sys.argv[3:]; runpy.run_path(sys.argv[0], run_name='__main__')")


def cleared(glow):
    """A glow sheet (RGBA) with no colour where its alpha is 0, its alpha as it was."""
    a = glow.getchannel("A")
    seen = a.point(lambda v: 255 if v else 0)
    return Image.merge("RGBA", (*ImageChops.multiply(glow.convert("RGB"), Image.merge("RGB", (seen,) * 3)).split(), a))


def clear_haze(pack):
    """pack (a module) with its glow_layer's output cleared (cleared)."""
    was = pack.glow_layer
    pack.glow_layer = lambda lit, under: cleared(was(lit, under))


def command(tools, args):
    """The command that runs tools' preview.py with args, its glow passes' haze cleared."""
    return [sys.executable, "-c", BOOT, tools, HERE, os.path.join(tools, "preview.py"), *args]
