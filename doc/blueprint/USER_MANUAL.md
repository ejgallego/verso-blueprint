# Blueprint User Manual

Last updated: 2026-03-15

This document is the repository-level manual for working with Blueprint in this
repo.

It focuses on practical usage and maintenance:

- how to validate the example blueprints,
- where generated artifacts land,
- where Blueprint-specific options and project-local policy live,
- which other docs to read next.

Design background lives in `DESIGN_RATIONALE.md`.
Planned cleanup and implementation work lives in `ROADMAP.md`.

## Scope

This is a maintainer-oriented manual for the Blueprint support in
`verso-blueprint`, not a full end-user syntax reference for every directive.

## Harness Status

This repository is intended to be developed AI-first. The public harness surface
should therefore stay small, explicit, and repository-local so humans and AI
agents use the same entry points.

Today, the current baseline is still the in-repo example flow centered on:

```bash
./generate-example-blueprints.sh
```

That baseline targets the projects under `test-projects/`. A fuller
worktree-aware harness is planned, but until it lands, treat any additional
helpers and refactor scaffolding as implementation details rather than stable
user-facing API.

## Target Public Harness Surface

As the harness refactor lands, the intended human-facing and AI-facing command
surface is:

```bash
./generate-example-blueprints.sh
./validate-example-blueprints.sh
python3 -m script.blueprint_harness sync-root-lake
python3 -m script.blueprint_harness paths
```

The design intent is:

- keep the root shell scripts as the obvious everyday entry points,
- keep the Python module as the single source of truth for orchestration,
- keep helper modules and internal command assembly out of the public surface,
- keep output locations and failure reporting predictable across root checkouts
  and linked worktrees.

## Current Validation Baseline

To validate the example Blueprint projects, run:

```bash
./validate-example-blueprints.sh
```

This default validation run:

- generates the example sites,
- runs the static Noperthedron panel regression check,
- runs the browser regression suite.

Lean tests are intentionally not part of the default validation path right now.
Run them explicitly with:

```bash
./validate-example-blueprints.sh --run-lean-tests
```

The generation phase builds:

- `noperthedron`
- `spherepackingblueprint`

Outputs go to:

- `_out/example-blueprints/noperthedron/`
- `_out/example-blueprints/spherepackingblueprint/`

For now, these in-repo `test-projects/` examples remain the supported baseline
for routine validation and regression checking.

## Planned External Project Support

External-project support is a planned harness capability, not a finished feature
yet.

The two important future scenarios are:

- testing a new or local `verso` checkout against this package,
- testing Blueprint projects that live in another repository.

When that support is added, the same repository-local harness surface should
remain the front door. In other words, users and AI agents should not need a
separate orchestration stack just because the Blueprint project or the `verso`
dependency lives elsewhere.

For now, we are happy using the in-repo `test-projects/` examples as the main
validation baseline while the external-project flow is still being designed.

## Shared Preview Manifest

Each generated Blueprint site emits a shared preview manifest at:

`html-multi/-verso-data/blueprint-preview-manifest.json`

This manifest is the canonical runtime source for Blueprint statement/proof
preview bodies. It also carries structured preview metadata such as:

- label
- facet
- kind
- parent
- dependencies
- ownership and triage fields

Useful CLI entry points:

```bash
lake exe noperthedron --dump-schema
lake exe noperthedron --dump-manifest
lake exe noperthedron --help
```

## Where Option Policy Lives

Repository-level Blueprint implementation notes live in this directory.

Project-local option policy stays with the project that owns it. In particular:

- `test-projects/Noperthedron/OPTIONS.md`

That file is currently the detailed option-policy reference for the
Noperthedron example, including:

- chapter-local `set_option` conventions,
- Blueprint-specific options already in use,
- example values and known follow-ups.

## Current Repo-Level Doc Set

- `USER_MANUAL.md`
  - operational guide for validating and maintaining Blueprint support here
- `DESIGN_RATIONALE.md`
  - architecture, ownership boundaries, preview rationale, and graph-status rationale
- `ROADMAP.md`
  - active priorities, planned cleanup phases, and near-term implementation work

## Practical Reading Order

1. Start here for commands and artifact locations.
2. Read `DESIGN_RATIONALE.md` to understand why the implementation is shaped the
   way it is.
3. Read `ROADMAP.md` before starting structural refactors.
