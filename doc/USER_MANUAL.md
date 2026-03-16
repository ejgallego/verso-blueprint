# Blueprint Maintainer Guide

Last updated: 2026-03-16

This document is the repository-level workflow guide for maintaining Blueprint
support in `verso-blueprint`.

It focuses on:

- generation and validation commands
- output locations
- linked-worktree usage
- repository-local policy for the in-repo example projects

Syntax and rendering semantics live in
[`MANUAL.md`](./MANUAL.md). Architecture background lives in
[`DESIGN_RATIONALE.md`](./DESIGN_RATIONALE.md). Planned cleanup and follow-up
work live in [`ROADMAP.md`](./ROADMAP.md).

## Scope

This is a maintainer document for this repository. It is not the end-user guide
for authoring every Blueprint directive.

## Current Command Surface

The supported repository-local entry points are:

```bash
./generate-example-blueprints.sh
./validate-example-blueprints.sh
python3 -m script.blueprint_harness --help
python3 -m script.blueprint_harness paths
python3 -m script.blueprint_harness sync-root-lake
```

The shell wrappers are the normal front door for day-to-day work. The Python
module is the single source of truth for orchestration and path resolution.

## Everyday Workflows

### Generate the Example Sites

```bash
./generate-example-blueprints.sh
```

This builds and renders the current in-repo example sites:

- `noperthedron`
- `spherepackingblueprint`

### Run the Default Validation Flow

```bash
./validate-example-blueprints.sh
```

The default validation path:

- generates the example sites
- runs the static Noperthedron code-panel regression check
- runs the browser regression suite

Lean tests are intentionally opt-in:

```bash
./validate-example-blueprints.sh --run-lean-tests
```

### Select Examples or Forward Test Flags

The harness supports narrowing the example set and forwarding extra pytest
arguments:

```bash
python3 -m script.blueprint_harness generate --example noperthedron
python3 -m script.blueprint_harness validate --example noperthedron --pytest-arg -k --pytest-arg preview
```

Run `python3 -m script.blueprint_harness --help` for the full flag surface.

## Output Layout

In the root checkout, generated artifacts go under:

- `_out/example-blueprints/noperthedron/`
- `_out/example-blueprints/spherepackingblueprint/`

In a linked worktree, generated artifacts go under the shared repo-root preview
area:

- `_out/<worktree>/example-blueprints/noperthedron/`
- `_out/<worktree>/example-blueprints/spherepackingblueprint/`

To print the resolved paths for the current checkout, run:

```bash
python3 -m script.blueprint_harness paths
```

## Working from Linked Worktrees

For implementation work, use a linked worktree under `.worktrees/` and keep the
root checkout as the stable base.

The harness is worktree-aware:

- in a linked worktree it writes artifacts to `_out/<worktree>/...`
- by default it prefers reusing the root checkout's prepared `.lake` artifacts
- local `lake build` and `lake test` in a linked worktree are disabled by
  default to avoid unnecessary Mathlib rebuilds

Before rebuilding from a linked worktree, prefer:

```bash
python3 -m script.blueprint_harness sync-root-lake
```

If local rebuilding is actually required, opt in explicitly:

```bash
python3 -m script.blueprint_harness generate --allow-local-build
python3 -m script.blueprint_harness validate --allow-local-build --run-lean-tests
```

## Example Project Notes

- `test-projects/Noperthedron/` is Mathlib-heavy, so linked worktrees should
  normally sync `.lake/` from the root checkout before any local build
- the in-repo `test-projects/` remain the supported baseline for routine
  validation during this pre-release phase
- the Python harness is maintainer tooling for those examples, not the intended
  long-term end-user interface

## Shared Preview Artifact

Each generated Blueprint site includes a shared preview manifest at:

`html-multi/-verso-data/blueprint-preview-manifest.json`

See [`MANUAL.md`](./MANUAL.md) for the manifest semantics and executable
inspection flags.

## Project-Local Option Policy

Repository-level Blueprint reference material lives in the main doc set. Project
specific option policy should stay with the project that owns it.

Current example-specific reference:

- [`test-projects/Noperthedron/OPTIONS.md`](../../test-projects/Noperthedron/OPTIONS.md)

## Documentation Reading Order

1. Start here for commands, outputs, and worktree behavior.
2. Read [`MANUAL.md`](./MANUAL.md) for Blueprint options and rendering
   semantics.
3. Read [`DESIGN_RATIONALE.md`](./DESIGN_RATIONALE.md) before touching
   architecture boundaries.
4. Read [`ROADMAP.md`](./ROADMAP.md) before starting structural cleanup.
