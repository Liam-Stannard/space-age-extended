#!/usr/bin/env python3
"""measure.py's sheet font: DejaVu Sans where Debian or Arch keep it, or from fc-match, else said.

  python3 tools/blender/test/test_measure_font.py --out <dir>

Nothing is rendered or drawn: measure.font_file() and measure.font() are called with FONT_DIRS
and PATH pointed at directories under --out (kept), each case with the lookup's cache emptied.

Exits 0 when every case below comes out as listed, 1 naming those that do not.

  here       on this machine: DejaVuSans.ttf and DejaVuSans-Bold.ttf found; font(13) and
             font(16, bold) are those files at 13 and 16, as the sheets were set
  dirs       Debian's /usr/share/fonts/truetype/dejavu is in FONT_DIRS, first, and Arch's
             /usr/share/fonts/TTF is there too; a directory in FONT_DIRS holding the file is
             where it is found, with fc-match off the PATH
  fc-match   FONT_DIRS empty: the file fc-match names is used when it is DejaVuSans.ttf, and
             not when it names another font (fc-match's substitute when DejaVu is missing)
  none       neither: font_file() is None, stderr names the file once over two calls, and
             font(13) is still 13 px (Pillow's default font at that size), not shrunk
"""
import argparse
import contextlib
import io
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import measure  # noqa: E402

FAILED = []
REGULAR, BOLD = "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(f"{case}: {detail}")


@contextlib.contextmanager
def lookup(dirs, path):
    """font_file() with FONT_DIRS and PATH as given, its cache emptied before and after; yields stderr."""
    keep_dirs, keep_path = measure.FONT_DIRS, os.environ.get("PATH", "")
    measure.FONT_DIRS, os.environ["PATH"] = tuple(dirs), path
    measure._FONT_FILES.clear()
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            yield err
    finally:
        measure.FONT_DIRS, os.environ["PATH"] = keep_dirs, keep_path
        measure._FONT_FILES.clear()


def fake_fc_match(bin_dir, answer):
    os.makedirs(bin_dir, exist_ok=True)
    p = os.path.join(bin_dir, "fc-match")
    with open(p, "w") as f:
        f.write(f"#!/bin/sh\nprintf '%s' '{answer}'\n")
    os.chmod(p, 0o755)
    return bin_dir


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    out = ap.parse_args().out
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    measure._FONT_FILES.clear()

    print("here")
    reg, bold = measure.font_file(), measure.font_file(True)
    check(f"{REGULAR} and {BOLD} found on this machine", reg and bold and os.path.basename(reg) == REGULAR
          and os.path.basename(bold) == BOLD, f"{reg}, {bold}")
    if not (reg and bold):
        print(f"FAIL: {len(FAILED)} case(s) failed (no DejaVu Sans here: the rest needs it)")
        sys.exit(1)
    f13, f16 = measure.font(13), measure.font(16, True)
    check("font(13) is DejaVu Sans at 13, font(16, bold) DejaVu Sans Bold at 16",
          getattr(f13, "path", None) == reg and f13.size == 13 and getattr(f16, "path", None) == bold
          and f16.size == 16, f"{getattr(f13, 'path', f13)} {getattr(f13, 'size', '')}, "
                              f"{getattr(f16, 'path', f16)} {getattr(f16, 'size', '')}")

    print("dirs")
    check("Debian's directory first in FONT_DIRS, Arch's there too",
          measure.FONT_DIRS[0] == "/usr/share/fonts/truetype/dejavu" and "/usr/share/fonts/TTF" in measure.FONT_DIRS,
          str(measure.FONT_DIRS))
    empty, holding, no_fc = (os.path.join(out, n) for n in ("empty", "holding", "no-fc-match"))
    for d in (empty, holding, no_fc):
        os.makedirs(d)
    shutil.copy(reg, holding)
    with lookup([empty, holding], no_fc):
        got = measure.font_file()
    check("a FONT_DIRS directory holding the file: found there", got == os.path.join(holding, REGULAR), str(got))

    print("fc-match")
    with lookup([empty], fake_fc_match(os.path.join(out, "fc-dejavu"), reg)):
        got = measure.font_file()
    check("FONT_DIRS empty, fc-match names DejaVuSans.ttf: used", got == reg, str(got))
    with lookup([empty], fake_fc_match(os.path.join(out, "fc-other"), bold)) as err:
        got = measure.font_file()
    check("FONT_DIRS empty, fc-match names another font: not used", got is None and REGULAR in err.getvalue(),
          f"{got}; {err.getvalue()!r}")

    print("none")
    with lookup([empty], no_fc) as err:
        got, again = measure.font_file(), measure.font_file()
        f = measure.font(13)
    said = err.getvalue()
    check("no font: None, stderr names the file once", got is None and again is None and said.count(REGULAR) == 1
          and said.count("measure.py:") == 1, repr(said))
    check("no font: font(13) is still 13 px", getattr(f, "size", None) == 13, f"{f!r} {getattr(f, 'size', None)}")

    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
