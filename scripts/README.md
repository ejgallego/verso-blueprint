# `scripts/`

This directory contains repository-local maintainer tooling for
`verso-blueprint`.

For package-facing usage, the preferred entry point is still
`lake exe blueprint-gen`, not the Python harness here. Start with the
top-level [`README.md`](../README.md) and [`doc/MANUAL.md`](../doc/MANUAL.md).

For repository maintenance, the canonical workflow document is
[`doc/MAINTAINER_GUIDE.md`](../doc/MAINTAINER_GUIDE.md). This README is
intentionally narrower: it tells you which files under `scripts/` are normal
entry points, which ones are implementation details, and where to look next
for the full workflow.

## Start Here

The normal repository-facing entry points are:

```bash
./scripts/generate-reference-blueprints.sh
./scripts/validate-reference-blueprints.sh
python3 -m scripts.blueprint_harness --help
```

If you are starting new implementation work, create a linked worktree through
the harness:

```bash
python3 -m scripts.blueprint_harness create-worktree <name>
```

That command is intentionally heavyweight by default: it creates the git
worktree, syncs the root checkout's `.lake/`, and warms the reference blueprint
clones used by the current checkout. If you only want the linked checkout
itself, use:

```bash
python3 -m scripts.blueprint_harness create-worktree <name> --lightweight
```

From a linked worktree, do not treat `lake build` or `lake test` as the
default next step. Ordinary `generate` and `validate` runs reuse the current
worktree `.lake/`; they do not automatically resync it from the root checkout.

If you want to refresh the worktree from the root checkout and shared reference
cache, prefer:

```bash
python3 -m scripts.blueprint_harness sync-root-lake
python3 -m scripts.blueprint_harness reference-sync
```

Use `./scripts/lean-low-priority ...` for long `lake`, `lean`, and
`.lake/build/bin/*` commands when you intentionally run them.

For non-default harness flows such as project selection, forwarded pytest
arguments, opt-in Lean tests, or `--allow-local-build`, defer to
[`doc/MAINTAINER_GUIDE.md`](../doc/MAINTAINER_GUIDE.md) or
`python3 -m scripts.blueprint_harness --help` rather than treating this README
as the full command reference.

## What Lives Here

- `generate-reference-blueprints.sh`
  Thin wrapper for `python3 -m scripts.blueprint_harness generate`.
- `validate-reference-blueprints.sh`
  Thin wrapper for `python3 -m scripts.blueprint_harness validate`.
- `lean-low-priority`
  Small wrapper that lowers scheduler priority for long Lean/Lake commands.
- `blueprint_harness.py`
  Main maintainer CLI. This is the single source of truth for orchestration and
  subcommand wiring.
- `blueprint_harness_projects.py`
  Project-manifest loader and schema checks for
  [`tests/harness/projects.json`](../tests/harness/projects.json).
- `blueprint_harness_references.py`
  Reference-blueprint checkout, local override, cache warm-up, and prune
  helpers extracted from the main harness CLI.
- `blueprint_harness_utils.py`
  Shared process-launch helpers used by the harness modules.
- `blueprint_harness_paths.py`
  Worktree-aware path resolution for `_out/` and reference-blueprint
  directories.
- `blueprint_harness_worktrees.py`
  Local worktree-coordination helpers for ignored metadata under `.worktrees/`.
- `prepare_reference_blueprints_pages.py`
  Helper used by the Pages publication flow to stage a site artifact from
  generated reference blueprint output.
- `__init__.py`
  Package marker for `python3 -m scripts ...` entry points.

## Useful Inspection Commands

If you want to inspect the current harness state instead of reading code, start
with:

```bash
python3 -m scripts.blueprint_harness projects
python3 -m scripts.blueprint_harness paths
```

The active project catalog lives in
[`tests/harness/projects.json`](../tests/harness/projects.json). The current
workflow and flag semantics live in
[`doc/MAINTAINER_GUIDE.md`](../doc/MAINTAINER_GUIDE.md).

## Read Next

- [`../README.md`](../README.md) for the package overview and end-user entry
  points
- [`../doc/MANUAL.md`](../doc/MANUAL.md) for Blueprint authoring and rendering
  semantics
- [`../doc/MAINTAINER_GUIDE.md`](../doc/MAINTAINER_GUIDE.md) for the canonical
  repository maintenance workflow
- [`../doc/CONTRIBUTING.md`](../doc/CONTRIBUTING.md) for branch, commit, PR,
  and local worktree conventions
