# Project Notes

- Primary work areas:
  - `src/VersoBlueprint`
  - `test-projects/Noperthedron` (core example project)
- Primary work branch at the repository root: `main`
- This harness applies to the extracted blueprint subproject rooted at `verso-blueprint/`
- Run long Lean/Lake/Elan commands via `script/lean-low-priority ...` so Codex keeps Lean builds at lower CPU priority by default.
- Main validation command:
  - `script/lean-low-priority ./generate-example-blueprints.sh`
- Validation output:
  - Default example-blueprint output is written to `_out/example-blueprints/{noperthedron,spherepackingblueprint}/`
  - Worktree previews should be written to the repository-root `_out/<worktree>/`
- The local `verso` dependency for this package lives at `..`

## Worktree and scope notes

- Treat `verso-blueprint/` as the package root for blueprint work.
- For extraction work that still touches the enclosing repository, keep changes tightly scoped and do not drift into unrelated root `verso` files.
- `WORKTREE_DASHBOARD.md` now lives at the package root in `/home/egallego/lean/verso-blueprint/WORKTREE_DASHBOARD.md`.
- The legacy file at `/home/egallego/lean/verso-blueprint-old/WORKTREE_DASHBOARD.md` is historical source material only; do not update it unless a separate archival task explicitly asks for that.

## General recommendations

- Avoid duplication strongly.
- Keep one source of truth for each data point.
- Avoid abbreviations in naming; backwards compatibility is not important yet.
- Do not introduce new inductives unless strictly necessary.
- For Codex-driven local work, wrap long-running `lake`, `lean`, `elan`, and `.lake/build/bin/*` commands with `script/lean-low-priority`.
- Override the default niceness only when needed via `BP_LEAN_NICENESS=<n>`.

## Important information about the Mathlib example project

- `test-projects/Noperthedron/` is a Mathlib project and should be handled carefully.
- When working in a feature worktree, copy the repository root `.lake` directory into that worktree so Mathlib artifacts can be reused.
- Run `script/lean-low-priority lake exe cache get` once in a fresh worktree if Lake starts repopulating Mathlib artifacts.
