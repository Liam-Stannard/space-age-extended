1. When creating entities or prototypes, use similar vanilla entities or prototypes as examples to follow. Do not just deep-copy one; create an original.
2. Concept work is design, not implementation. Every concept image and option round lives in `./concept/<building>/`. Only signed-off or placeholder art lives in `./graphics/`; nothing in `./concept/` ships, and nothing in `./graphics/` or `./prototypes/` is a concept. A building's Blender model lives in `./concept/<building>/model/`, with the script that renders its plates and anything baked for it from its concept sheet. The shared render pipeline lives in `./tools/blender/`.
3. All design documentation lives in `./design/`. Each building's spec (`building-spec-<building>.md`) lives in `./design/buildings/<building>/`.
4. Outstanding tasks are logged as `./TODO.md` says.
5. Spec templates live in `./templates/`. Nowhere else.
6. Every piece of work goes on its own feature branch, named for the work. It is merged into `master` once it is ready, and the branch is deleted after the merge. Nothing is committed directly to `master`.
7. Every rule for how text is worded, and for how any `.md` file is changed, is in `DOCUMENTATION-LANGUAGE.md`.
8. No comments in code. Code is made readable by clear names, small functions and plain structure, not by comments.
