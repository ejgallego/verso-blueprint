# Project Notes

## Scope

- Repository root: `/home/egallego/lean/verso-blueprint`
- This repository is the standalone `verso-blueprint` package root.
- Primary work areas:
  - `src/VersoBlueprint`
  - `tests`
  - `browser-tests`
  - `script`
  - `test-projects/` for the current pre-release example blueprints
- Primary branch at the repository root: `main`

## Worktree Policy

- Start new implementation work in a linked worktree under `.worktrees/`, not in
  the root checkout.
- Treat the root checkout as the stable base used to seed worktrees, sync
  shared `.lake` artifacts, and host shared preview output.
- If a task starts in the root checkout and requires code changes, stop before
  editing and move the work into a linked worktree unless the user explicitly
  asks to work on the root checkout itself.
- Create linked worktrees only via `python3 -m script.blueprint_harness create-worktree <name>`.
- Do not create sibling checkouts or ad hoc `git worktree add` paths unless you
  are debugging the harness itself.
- Worktree preview output should be written to the repository-root
  `_out/<worktree>/`.
- `WORKTREE_DASHBOARD.md` lives at the package root and is the live index of
  active worktrees.
- `/home/egallego/lean/verso-blueprint-old/WORKTREE_DASHBOARD.md` is archival
  only; do not update it unless the user explicitly asks for archival work.
- Feature and legacy worktree branches are local-only by default. Do not push
  anything except `main` to `origin` unless the user explicitly asks for that
  push.

## Release Status

- The code is near release.
- `test-projects/` still lives in this repository today, but those example
  projects are expected to move to their own repositories.
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
  `script/lean-low-priority ...`.
- Preferred user-facing interface:
  - `lake exe blueprint-gen ...`
- Main build/test commands:
  - `script/lean-low-priority lake build`
  - `script/lean-low-priority lake test`
  - `./scripts/generate-example-blueprints.sh`
  - `./scripts/validate-example-blueprints.sh`
  - `./scripts/validate-example-blueprints.sh --run-lean-tests`
- Harness commands:
  - `python3 -m script.blueprint_harness --help`
  - `python3 -m script.blueprint_harness generate`
  - `python3 -m script.blueprint_harness validate`
  - `python3 -m script.blueprint_harness sync-root-lake`
  - `python3 -m script.blueprint_harness paths`
- The Python harness is maintainer tooling for this repository's in-repo
  examples, not the preferred end-user interface.
- Default example output in the root checkout:
  - `_out/example-blueprints/{noperthedron,spherepackingblueprint}/`
- Default example output in a linked worktree:
  - `_out/<worktree>/example-blueprints/{noperthedron,spherepackingblueprint}/`

## Mathlib and Worktree Reuse

- `test-projects/Noperthedron/` is Mathlib-heavy and should be handled
  carefully.
- In linked worktrees, prefer `python3 -m script.blueprint_harness sync-root-lake`
  before allowing local rebuilds.
- If Lake starts repopulating Mathlib artifacts unnecessarily, try
  `script/lean-low-priority lake exe cache get`.

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
