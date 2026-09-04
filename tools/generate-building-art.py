#!/usr/bin/env python3
"""Fire a filled-in building spec's image prompts at OpenAI's image API.

The spec documents in graphics/ carry their generation prompts in fenced
```text blocks under known headings (see building-spec-template.md §11 and
§16). This reads those blocks straight out of the markdown, so the prompts
that get generated are always the prompts in the document -- there is no
second copy to drift.

DALL-E 2 and 3 are retired; their successor is the gpt-image-* family, which
is what --model defaults to. Transparent backgrounds are requested directly,
so no magenta keying step is needed.

Usage:
  tools/generate-building-art.py graphics/building-spec-vent-pump.md
  tools/generate-building-art.py <spec> --only master,icon
  tools/generate-building-art.py <spec> --list
  tools/generate-building-art.py <spec> --tag v2 --quality medium

Output lands in graphics/entity/<building>/concept/<tag>-<slug>.png.
Needs an OpenAI key in OPEN_API_KEY (or OPENAI_API_KEY).
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request

API = "https://api.openai.com/v1/images/generations"

# Heading -> output slug. Order is generation order: the concept sheet is
# stage 0 and is approved before anything else is generated.
SECTIONS = [
    ("## Concept Sheet Prompt", "sheet"),
    ("## Master Concept Prompt", "master"),
    ("### North", "north"),
    ("### East", "east"),
    ("### South", "south"),
    ("### West", "west"),
    ("### Main Structure", "layer-structure"),
    ("### Working Machinery", "layer-machinery"),
    ("### Glow / Lighting", "layer-glow"),
    ("### Effects", "layer-effects"),
    ("### Icon Prompt", "icon"),
]

MASTER_REF = re.compile(r"\[Master prompt\]\s*", re.I)
SKIP = re.compile(r"^\s*(not required|do not generate)", re.I)


def blocks(spec_text):
    """Pull the first ```text fence following each known heading."""
    found = {}
    for heading, slug in SECTIONS:
        i = spec_text.find("\n" + heading)
        if i < 0:
            continue
        m = re.search(r"```text\n(.*?)```", spec_text[i:], re.S)
        if not m:
            continue
        body = m.group(1).strip()
        if SKIP.match(body) or not body:
            continue
        found[slug] = body
    return found


def expand(prompts):
    """Splice the master prompt into the ones that reference it."""
    master = prompts.get("master")
    out = {}
    for slug, body in prompts.items():
        if slug != "master" and MASTER_REF.search(body):
            if not master:
                sys.exit(f"{slug} references [Master prompt] but none was found")
            body = MASTER_REF.sub("", body).strip()
            body = master + "\n\n" + body
        out[slug] = body
    return out


def generate(key, model, prompt, size, quality, background):
    body = {"model": model, "prompt": prompt, "n": 1, "size": size,
            "quality": quality, "background": background, "output_format": "png"}
    req = urllib.request.Request(
        API, data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--only", help="comma-separated slugs, e.g. master,icon")
    ap.add_argument("--list", action="store_true", help="show slugs and exit")
    ap.add_argument("--tag", default="v1", help="filename prefix (default v1)")
    ap.add_argument("--model", default="gpt-image-2")
    ap.add_argument("--size", default="1024x1024")
    ap.add_argument("--quality", default="high")
    ap.add_argument("--background", default="transparent")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    spec_text = open(args.spec, encoding="utf-8").read()

    name = re.sub(r"^building-spec-|\.md$", "",
                  os.path.basename(args.spec))
    outdir = os.path.join(repo, "graphics", "entity", name, "concept")

    prompts = expand(blocks(spec_text))
    if args.only:
        want = [s.strip() for s in args.only.split(",")]
        missing = [s for s in want if s not in prompts]
        if missing:
            sys.exit("no such prompt(s) in this spec: " + ", ".join(missing))
        prompts = {s: prompts[s] for s in want}

    if not prompts:
        sys.exit("no ```text prompt blocks found -- is this spec filled in?")

    if args.list or args.dry_run:
        for slug, body in prompts.items():
            print(f"--- {slug}  ({len(body)} chars) -> "
                  f"graphics/entity/{name}/concept/{args.tag}-{slug}.png")
            if args.dry_run:
                print(body + "\n")
        return

    key = os.environ.get("OPEN_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("Set OPEN_API_KEY (or OPENAI_API_KEY) first.")

    os.makedirs(outdir, exist_ok=True)
    failed = 0
    for slug, body in prompts.items():
        path = os.path.join(outdir, f"{args.tag}-{slug}.png")
        try:
            data = generate(key, args.model, body, args.size,
                            args.quality, args.background)
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            try:
                detail = json.loads(detail)["error"]["message"]
            except Exception:
                detail = detail[:400]
            print(f"  FAILED  {slug}: HTTP {e.code} -- {detail}", file=sys.stderr)
            failed += 1
            continue
        with open(path, "wb") as f:
            f.write(base64.b64decode(data["data"][0]["b64_json"]))
        usage = data.get("usage") or {}
        print(f"  ok  {slug} -> {os.path.relpath(path, repo)}"
              + (f"  ({usage.get('total_tokens')} tokens)" if usage else ""))

    if failed:
        sys.exit(f"{failed} of {len(prompts)} prompt(s) failed.")
    print(f"Generated {len(prompts)} image(s) into "
          f"graphics/entity/{name}/concept/")


if __name__ == "__main__":
    main()
