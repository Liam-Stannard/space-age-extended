#!/usr/bin/env bash
set -euo pipefail

# Enforces the repository layout claude.md describes, so a rule that is easy to
# break by habit is caught by a script rather than by a review.
#
#   concept/<building>/   every concept image, spec and option round (design)
#   graphics/             signed-off or placeholder art only (implementation)
#   design/               design documentation
#   templates/            prompt templates
#   TODO.md               the only place a task is written down

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
fail=0

# 1. No concept directory anywhere under graphics/ or prototypes/.
if found="$(find graphics prototypes -type d -name concept 2>/dev/null)" && [ -n "$found" ]; then
  echo "concept directories outside concept/:" >&2; echo "$found" >&2; fail=1
fi

# 2. Markdown lives in design/, templates/, concept/ or the repo root.
if found="$(find graphics prototypes tools locale migrations -name '*.md' 2>/dev/null)" && [ -n "$found" ]; then
  echo "markdown outside design/, templates/, concept/ or the root:" >&2; echo "$found" >&2; fail=1
fi

# 3. Building specs and option rounds sit in concept/<building>/, never loose.
if found="$(find . -name 'building-spec-*.md' -not -path './concept/*' -not -path './.git/*' \
    -not -name 'building-spec-template.md' 2>/dev/null)" && [ -n "$found" ]; then
  echo "building specs outside concept/<building>/:" >&2; echo "$found" >&2; fail=1
fi

# 4. Task lists live in TODO.md only.
if found="$(find . \( -name 'TODO*.md' -o -name 'PROGRESS.md' \) -not -path './TODO.md' -not -path './.git/*' -not -path './.claude/*' 2>/dev/null)" \
    && [ -n "$found" ]; then
  echo "task lists other than TODO.md:" >&2; echo "$found" >&2; fail=1
fi

[ "$fail" -eq 0 ] && echo "Layout OK -- concept/, graphics/, design/, templates/ and TODO.md are where claude.md says."
exit "$fail"
