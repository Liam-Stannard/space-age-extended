#!/usr/bin/env python3
"""Tonal spread against vanilla: the gap check-sheet-style.py does not measure.

  python3 tonal.py <plate.png> [...]
"""
import sys
from PIL import Image
for path in sys.argv[1:]:
    im = Image.open(path).convert("RGBA")
    px = [p for p in im.get_flattened_data() if p[3] > 200]
    L = sorted(0.299 * r + 0.587 * g + 0.114 * b for r, g, b, a in px)
    q = lambda f: round(L[int(f * (len(L) - 1))])
    print(f"{path[-40:]:40s} p5 {q(.05):3d}  p50 {q(.5):3d}  p95 {q(.95):3d}  spread {q(.95) - q(.05):3d}"
          "   (vanilla: p50 41-63, p95 143-189, spread 140-177)")
