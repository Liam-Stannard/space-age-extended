1. Do not modify any file in `design/` without explicit agreement from me.
2. When creating entities or prototypes, use similar vanilla entities or prototypes as examples to follow. Do not just deep-copy one; create an original.
3. Concept work is design, not implementation. Every concept image, building spec (`building-spec-<building>.md`) and option round lives in `./concept/<building>/`. Only signed-off or placeholder art lives in `./graphics/`; nothing in `./concept/` ships, and nothing in `./graphics/` or `./prototypes/` is a concept.
4. All design documentation lives in `./design/`.
5. Every outstanding task is logged in `./TODO.md` and removed once complete. Todos are logged nowhere else.
6. Prompt templates live in `./templates/`. Nowhere else.
7. Every piece of work goes on its own feature branch, named for the work. It is merged into `master` once it is ready, and the branch is deleted after the merge. Nothing is committed directly to `master`.
