# Project Notes

## Scope

- Repository root: `/home/egallego/lean/verso-blueprint`
- This repository is the standalone `verso-blueprint` package root.
- Primary work areas:
  - `src/VersoBlueprint`
  - `tests`
  - `tests/browser`
  - `scripts`
  - `doc`
- Primary branch at the repository root: `main`

## Worktree Policy

- Start new implementation work in a linked worktree under `.worktrees/`, not in
  the root checkout.
- Treat the root checkout as the stable base used to seed worktrees, sync
  shared `.lake` artifacts, and host shared preview output.
- If a task starts in the root checkout and requires code changes, stop before
  editing and move the work into a linked worktree unless the user explicitly
  asks to work on the root checkout itself.
- Create linked worktrees only via `python3 -m scripts.blueprint_harness create-worktree <name>`.
- Do not create sibling checkouts or ad hoc `git worktree add` paths unless you
  are debugging the harness itself.
- Worktree preview output should be written to the repository-root
  `_out/<worktree>/`.
- Do not keep a tracked worktree dashboard at the package root.
- Keep local coordination state untracked under `.worktrees/`.
- Preferred local coordination files:
  - `.worktrees/registry.json`
  - `.worktrees/_meta/_root.json`
  - `.worktrees/_meta/<name>.json`
- `/home/egallego/lean/verso-blueprint-old/WORKTREE_DASHBOARD.md` is archival
  only; do not update it unless the user explicitly asks for archival work.
- Feature and legacy worktree branches are local-only by default. Do not push
  anything except `main` to `origin` unless the user explicitly asks for that
  push.

## Release Status

- The code is near release.
- The reference blueprints now live in their own repositories:
  `ejgallego/verso-noperthedron` and `ejgallego/verso-sphere-packing`.
- A smaller starter example, a reusable template, and `lake exe bp new` are
  planned but not landed yet.
- End-user docs should treat `lake exe blueprint-gen` as the preferred
  Blueprint generation interface.
- End-user docs should not require Python helper scripts or a system Graphviz
  installation for normal package usage.
- End-user docs should also explain the current standard Verso workflow
  honestly: a Blueprint project owns both the Blueprint source modules and a
  small `lean_exe` generator binary that writes `_out/`.
- When editing docs or agent guidance, distinguish clearly between current
  behavior and planned release behavior.

## Commands

- Run long `lake`, `lean`, `elan`, and `.lake/build/bin/*` commands via
  `scripts/lean-low-priority ...`.
- Preferred user-facing interface:
  - `lake exe blueprint-gen ...`
- Main build/test commands:
  - `scripts/lean-low-priority lake build`
  - `scripts/lean-low-priority lake test`
  - `./scripts/generate-reference-blueprints.sh`
  - `./scripts/validate-reference-blueprints.sh`
  - `./scripts/validate-reference-blueprints.sh --run-lean-tests`
- Harness commands:
  - `python3 -m scripts.blueprint_harness --help`
  - `python3 -m scripts.blueprint_harness sync-root-lake`
  - `python3 -m scripts.blueprint_harness paths`
  - `python3 -m scripts.blueprint_harness worktree-sync`
  - `python3 -m scripts.blueprint_harness worktree-list`
  - `python3 -m scripts.blueprint_harness worktree-status`
  - `python3 -m scripts.blueprint_harness worktree-claim`
  - `python3 -m scripts.blueprint_harness worktree-release`
  - `python3 -m scripts.blueprint_harness worktree-prune-candidates`
  - `python3 -m scripts.blueprint_harness worktree-retire`
  - `python3 -m scripts.blueprint_reference_harness --help`
  - `python3 -m scripts.blueprint_reference_harness projects`
  - `python3 -m scripts.blueprint_reference_harness generate`
  - `python3 -m scripts.blueprint_reference_harness validate`
  - `python3 -m scripts.blueprint_reference_harness sync`
  - `python3 -m scripts.blueprint_reference_harness edit <project>`
  - `python3 -m scripts.blueprint_reference_harness prune`
- The Python harness is maintainer tooling for this repository's in-repo
  own tests plus ephemeral checkout validations, not the preferred end-user
  interface.
- Default validation-catalog output in the root checkout:
  - `_out/reference-blueprints/{project-template,preview_runtime_showcase,noperthedron,spherepackingblueprint}/`
- Default validation-catalog output in a linked worktree:
  - `_out/<worktree>/reference-blueprints/{project-template,preview_runtime_showcase,noperthedron,spherepackingblueprint}/`
- Shared warmed reference blueprint cache for external git-checkout projects:
  - `.worktrees/_reference-blueprints/cache/{noperthedron,spherepackingblueprint}/`
- Current-checkout local reference blueprint clones for external git-checkout projects:
  - `.worktrees/_reference-blueprints/by-worktree/<checkout>/{noperthedron,spherepackingblueprint}/`

## Mathlib and Worktree Reuse

- `ejgallego/verso-noperthedron` is Mathlib-heavy and should be handled
  carefully.
- In linked worktrees, prefer `python3 -m scripts.blueprint_harness sync-root-lake`
  before allowing local rebuilds.
- If Lake starts repopulating Mathlib artifacts unnecessarily, try
  `scripts/lean-low-priority lake exe cache get`.

## Approval Policy

- Avoid approval/escalation requests unless they are actually required.
- Do not request approval for routine local reads, repo-local edits, `git
  status`, `git diff`, or sandbox-safe local build/test commands.
- Prefer repo-local scripts and already-approved command prefixes over alternate
  commands that trigger avoidable auth prompts.
- Documentation work, local code edits, and ordinary repo inspection should
  stay fully local.
- Do not push branches, install global tools, or write outside the workspace
  unless the user explicitly asks or the task genuinely requires it.

## Documentation Map

- `README.md`: user-facing overview and getting-started guide
- `doc/CONTRIBUTING.md`: branch, commit, PR, and local worktree coordination
  conventions
- `doc/MANUAL.md`: feature semantics, options, and rendering notes
- `doc/MAINTAINER_GUIDE.md`: maintainer-oriented harness workflow
- `doc/DESIGN_RATIONALE.md`: architecture rationale
- `doc/ROADMAP.md`: planned cleanup and follow-up work
- `doc/UPSTREAM_TODO.md`: items that should eventually be upstreamed to `verso`

## General Recommendations

- Avoid duplication strongly.
- Keep one source of truth for each data point.
- Prefer descriptive names over abbreviations.
- Do not introduce new inductives unless strictly necessary.
- When adding or updating file authorship headers, prefer the name of the human
  driving the work, not the AI assistant name.
- Prefer the documented public harness entry points over ad hoc internal command
  sequences.
- Prefer branch names of the form `feat/<slug>`, `fix/<slug>`, `docs/<slug>`,
  `chore/<slug>`, or local-only `wip/<slug>`.
- Prefer commit subjects of the form `type(scope): summary`.
