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
./scripts/generate-test-blueprints.sh
./scripts/validate-test-blueprints.sh
./scripts/validate-branch.sh
./scripts/validate-reference-blueprints.sh
python3 -m scripts.blueprint_harness --help
python3 -m scripts.blueprint_reference_harness --help
```

If you are starting new implementation work, create a linked worktree through
the harness:

```bash
python3 -m scripts.blueprint_harness create-worktree <name> --owner codex --lock --priority P1 --summary "short description"
```

That command is intentionally heavyweight by default: it creates the git
worktree, syncs the root checkout's `.lake/`, and warms the reference blueprint
clones used by the current checkout. When `origin/main` exists, the new
worktree defaults to `origin/main` rather than local `main` as its base. If
you only want the linked checkout itself, use:

```bash
python3 -m scripts.blueprint_harness create-worktree <name> --lightweight
```

If you want to verify that local `main` is still in sync with the preferred
main ref before branching or landing, use:

```bash
python3 -m scripts.blueprint_harness main-status
python3 -m scripts.blueprint_harness main-status --require-sync
```

To land one reviewed branch onto `main` from the root checkout, use:

```bash
python3 -m scripts.blueprint_harness land-main feat/some-branch
python3 -m scripts.blueprint_harness land-main feat/some-branch --cleanup
```

From a linked worktree, do not treat `lake build` or `lake test` as the
default next step. Ordinary `generate` and `validate` runs reuse the current
worktree `.lake/`; they do not automatically resync it from the root checkout.

If you want to refresh the worktree from the root checkout and shared reference
cache, prefer:

```bash
python3 -m scripts.blueprint_harness sync-root-lake
python3 -m scripts.blueprint_reference_harness sync
```

For rendering and browser regressions, prefer the in-repo test blueprints under
`tests/test_blueprints/` over the external reference blueprints. The default
browser suite now builds and serves
`tests/test_blueprints/preview_runtime_showcase/` when you run:

```bash
uv run --project tests/browser --extra test python -m pytest tests/browser -q --browser chromium
```

Use `./scripts/validate-test-blueprints.sh` when you want the local panel and
browser regressions against `_out/test-blueprints/preview_runtime_showcase/`.

Use `./scripts/validate-branch.sh` as the canonical pre-merge check when you
want all tests plus both artifact families rebuilt:

```bash
./scripts/validate-branch.sh
```

That command runs Lean tests, the Python harness/unit tests, regenerates
`_out/reference-blueprints/`, regenerates `_out/test-blueprints/`, and then
runs the local panel/browser regressions.

The shared reference cache remains responsible for warmed external-project
dependency state, including project-specific Mathlib builds.

Use `worktree-list` as the local dashboard for parallel work. It combines the
small manual records under `.worktrees/_meta/` with live Git state such as the
current branch, dirty status, and commit distance from `main`. `worktree-list`
already refreshes that metadata before printing; `worktree-sync` remains only
as a compatibility alias for the same dashboard command. Locked worktrees are
the ones another active session should not touch.

When you run `generate`, `validate`, or `sync` from the root checkout while it
is on `main`, the reference CLI expects that checkout to stay clean and in
sync. Use `--allow-unsafe-root-main` only as an explicit maintainer override.

If you want to make manual changes in one external reference blueprint repo,
use a separate editable clone instead of the disposable validation clones:

```bash
python3 -m scripts.blueprint_reference_harness edit noperthedron
python3 -m scripts.blueprint_reference_harness edit spherepackingblueprint --branch feat/update-figures
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
  Thin wrapper for `python3 -m scripts.blueprint_reference_harness generate`.
- `generate-test-blueprints.sh`
  Thin wrapper for the local test-blueprint generator.
- `validate-test-blueprints.sh`
  Generate and validate the local test blueprint fixtures.
- `validate-branch.sh`
  Full pre-merge validation entry point: all tests plus both artifact families.
- `validate-reference-blueprints.sh`
  Thin wrapper for `python3 -m scripts.blueprint_reference_harness validate`.
- `lean-low-priority`
  Small wrapper that lowers scheduler priority for long Lean/Lake commands.
- `blueprint_harness.py`
  Worktree, branch-landing, and coordination CLI.
- `blueprint_reference_harness.py`
  Reference-blueprint generation, validation, and reference-checkout CLI.
- `blueprint_harness_cli.py`
  Shared argparse helper functions used by both CLIs.
- `blueprint_harness_projects.py`
  Project-manifest loader and schema checks for
  [`tests/harness/projects.json`](../tests/harness/projects.json).
- `blueprint_harness_references.py`
  Reference-blueprint checkout, editable-clone setup, local override, cache
  warm-up, and prune helpers shared by the reference CLI.
- `blueprint_harness_utils.py`
  Shared process-launch helpers used by the harness modules.
- `blueprint_harness_paths.py`
  Worktree-aware path resolution for `_out/` and reference-blueprint
  directories.
- `blueprint_harness_worktrees.py`
  Local worktree-coordination helpers for ignored metadata under `.worktrees/`.
- `prepare_reference_blueprints_pages.py`
  Helper used by the Pages publication flow to stage a combined site artifact
  from generated reference and test blueprint output.
- `__init__.py`
  Package marker for `python3 -m scripts ...` entry points.

## Useful Inspection Commands

If you want to inspect the current harness state instead of reading code, start
with:

```bash
./scripts/generate-test-blueprints.sh
python3 -m scripts.blueprint_reference_harness projects
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
