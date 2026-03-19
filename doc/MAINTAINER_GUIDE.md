# Blueprint Maintainer Guide

Last updated: 2026-03-17

This document is the repository-level workflow guide for maintaining Blueprint
support in `verso-blueprint` and its published reference blueprints.

It focuses on:

- generation and validation commands
- output locations
- CI and GitHub Pages publication for the reference blueprints
- linked-worktree usage
- repository-local policy for the external reference-blueprint validation harness

End-user onboarding lives in
[`../project_template/README.md`](../project_template/README.md),
[`GETTING_STARTED.md`](./GETTING_STARTED.md), and [`MANUAL.md`](./MANUAL.md).
Architecture background lives in [`DESIGN_RATIONALE.md`](./DESIGN_RATIONALE.md).
Planned cleanup and follow-up work live in [`ROADMAP.md`](./ROADMAP.md).

## Scope

This is a maintainer document for this repository. It is not the end-user guide
for starting a Blueprint project or learning every Blueprint directive.

## Current Command Surface

The supported repository-local entry points are:

```bash
./scripts/generate-reference-blueprints.sh
./scripts/validate-reference-blueprints.sh
python3 -m scripts.blueprint_harness create-worktree <name>
python3 -m scripts.blueprint_harness land-main <source-ref>
python3 -m scripts.blueprint_harness main-status
python3 -m scripts.blueprint_harness --help
python3 -m scripts.blueprint_reference_harness projects
python3 -m scripts.blueprint_reference_harness edit <project>
python3 -m scripts.blueprint_reference_harness sync
python3 -m scripts.blueprint_reference_harness prune
python3 -m scripts.blueprint_reference_harness --help
python3 -m scripts.blueprint_harness paths
python3 -m scripts.blueprint_harness sync-root-lake
python3 -m scripts.blueprint_harness worktree-sync
python3 -m scripts.blueprint_harness worktree-list
python3 -m scripts.blueprint_harness worktree-claim
python3 -m scripts.blueprint_harness worktree-status
python3 -m scripts.blueprint_harness worktree-release
python3 -m scripts.blueprint_harness worktree-prune-candidates
python3 -m scripts.blueprint_harness worktree-retire
```

The shell wrappers are the normal front door for day-to-day work. The Python
modules are the single source of truth for orchestration and path resolution:
`blueprint_harness.py` for worktree and landing flows, and
`blueprint_reference_harness.py` for reference-project lifecycle flows.

The default project catalog lives at `tests/harness/projects.json`. It includes
the in-repo starter template plus the external reference blueprint repositories,
and it is the extension point for future ephemeral GitHub checkout validations.

## Everyday Workflows

### Generate the Reference Blueprints

```bash
./scripts/generate-reference-blueprints.sh
```

This builds and renders the current reference blueprint projects:

- `project-template`
- `noperthedron`
- `spherepackingblueprint`

### Run the Default Validation Flow

```bash
./scripts/validate-reference-blueprints.sh
```

The default validation path:

- generates the reference blueprint sites
- runs the static Noperthedron code-panel regression check
- runs the browser regression suite

Lean tests are intentionally opt-in:

```bash
./scripts/validate-reference-blueprints.sh --run-lean-tests
```

### Select Projects or Forward Test Flags

The harness supports narrowing the example set and forwarding extra pytest
arguments:

```bash
python3 -m scripts.blueprint_reference_harness generate --project noperthedron
python3 -m scripts.blueprint_reference_harness validate --project noperthedron --pytest-arg -k --pytest-arg preview
```

Run `python3 -m scripts.blueprint_reference_harness --help` for the full flag surface.

To inspect the active catalog:

```bash
python3 -m scripts.blueprint_reference_harness projects
```

To warm the shared reference blueprint cache and prepare local clones for the
current checkout:

```bash
python3 -m scripts.blueprint_reference_harness sync
```

To remove stale harness-managed reference caches and orphaned local clones:

```bash
python3 -m scripts.blueprint_reference_harness prune --dry-run
python3 -m scripts.blueprint_reference_harness prune
```

## Output Layout

In the root checkout, generated artifacts go under:

- `_out/reference-blueprints/project-template/`
- `_out/reference-blueprints/noperthedron/`
- `_out/reference-blueprints/spherepackingblueprint/`

In a linked worktree, generated artifacts go under the shared repo-root preview
area:

- `_out/<worktree>/reference-blueprints/project-template/`
- `_out/<worktree>/reference-blueprints/noperthedron/`
- `_out/<worktree>/reference-blueprints/spherepackingblueprint/`

To print the resolved paths for the current checkout, run:

```bash
python3 -m scripts.blueprint_harness paths
```

`paths` prints the canonical worktree-aware output, cache, and checkout
locations used by the harness.

It also prints the shared reference blueprint cache root and the current
checkout's local clone root.

## Working from Linked Worktrees

For implementation work, create a linked worktree under `.worktrees/` and keep
the root checkout as the stable base:

```bash
python3 -m scripts.blueprint_harness create-worktree <name>
```

That command is intentionally heavyweight by default: after `git worktree add`
it syncs the root checkout's `.lake/` and warms the shared and per-worktree
reference blueprint clones. When `origin/main` exists, new worktrees now base
off `origin/main` by default rather than local `main`.

If you want to verify that the root checkout has not drifted before branching
or landing, use:

```bash
python3 -m scripts.blueprint_harness main-status
python3 -m scripts.blueprint_harness main-status --require-sync
```

To land one reviewed branch onto `main` safely from the root checkout, use:

```bash
python3 -m scripts.blueprint_harness land-main feat/some-branch
python3 -m scripts.blueprint_harness land-main feat/some-branch --cleanup
```

`land-main` refuses to proceed unless the root checkout is on a clean, in-sync
local `main`, and it only accepts fast-forward source refs. With `--cleanup`,
it also removes the source worktree and deletes the source branch when that can
be done safely.

After creation, ordinary `generate` and `validate` runs reuse the worktree's
current `.lake/`; they do not automatically resync it from the root checkout.

The harness is worktree-aware:

- in a linked worktree it writes artifacts to `_out/<worktree>/...`
- by default it prefers reusing the root checkout's prepared `.lake` artifacts
- it also keeps shared warmed reference blueprint caches under
  `.worktrees/_reference-blueprints/cache/`
- each checkout uses its own local reference blueprint clones under
  `.worktrees/_reference-blueprints/by-worktree/<checkout>/`
- local `lake build` and `lake test` in a linked worktree are disabled by
  default to avoid unnecessary dependency rebuilds

If you only want a bare linked checkout and plan to bootstrap it yourself, use:

```bash
python3 -m scripts.blueprint_harness create-worktree <name> --lightweight
```

When you do want to refresh a linked worktree from the root checkout and shared
reference cache, prefer:

```bash
python3 -m scripts.blueprint_harness sync-root-lake
python3 -m scripts.blueprint_reference_harness sync
```

If local rebuilding is actually required, opt in explicitly:

```bash
python3 -m scripts.blueprint_reference_harness generate --allow-local-build
python3 -m scripts.blueprint_reference_harness validate --allow-local-build --run-lean-tests
```

## Parallel Worktree Coordination

The local coordination layer is now machine-readable and untracked.

- `worktree-sync` scans `git worktree list` and refreshes local metadata under
  `.worktrees/`
- `worktree-list` shows the current local registry snapshot
- `worktree-claim` records owner, issue, summary, status, and write scope
- `worktree-status` shows one worktree record
- `worktree-release` marks a worktree done or otherwise retired
- `worktree-prune-candidates` lists merged clean linked worktrees that are good
  manual prune candidates
- `worktree-retire` removes one merged clean linked worktree, deletes its local
  branch when one exists, and prunes its stale reference clones
- detached linked worktrees are also retireable once their `HEAD` commit is
  reachable from `origin/main` or local `main`

The live local files are:

- `.worktrees/registry.json`
- `.worktrees/_meta/_root.json`
- `.worktrees/_meta/<name>.json`

These files are intentionally ignored by Git and should not be treated as
repository content.

Recommended workflow:

```bash
python3 -m scripts.blueprint_harness worktree-sync
python3 -m scripts.blueprint_harness worktree-claim --owner codex --summary "external harness rework" --scope scripts --scope tests/harness
python3 -m scripts.blueprint_harness worktree-list
python3 -m scripts.blueprint_harness worktree-prune-candidates
python3 -m scripts.blueprint_harness worktree-retire <name> --dry-run
```

## Reference Blueprint Notes

- `ejgallego/verso-noperthedron` has a heavy dependency footprint, so linked
  worktrees should normally sync `.lake/` from the root checkout before
  external validation
- the default baseline projects now live in external repositories, not inside
  this package checkout
- the harness warms shared reference blueprint checkouts once under
  `.worktrees/_reference-blueprints/cache/`
- each checkout gets its own local clone under
  `.worktrees/_reference-blueprints/by-worktree/<checkout>/`, seeded from the
  shared cache so transitive build artifacts stay warm across worktrees
- editable reference-project clones live separately under
  `.worktrees/_reference-blueprints/edit/<checkout>/` and are not touched by
  `reference-sync`, `generate`, or `reference-prune`
- `reference-prune` cleans up stale project caches and local clones when
  worktrees or manifest entries disappear
- the Python harness rewrites the cloned project's `lakefile.lean` locally so
  `VersoBlueprint` resolves to the checkout under test before running
  `lake update`
- external reference repositories should commit `lake-manifest.json`; when that
  tracked manifest is present, the harness updates only `VersoBlueprint` so
  transitive dependencies such as `verso` stay pinned to the project's tested
  revisions
- the Python harness is maintainer tooling for those validations, not the main
  package-facing authoring interface

To prepare one editable external reference checkout for manual changes, use:

```bash
python3 -m scripts.blueprint_reference_harness edit noperthedron
python3 -m scripts.blueprint_reference_harness edit spherepackingblueprint --branch feat/update-figures
```

Those editable clones are ordinary developer checkouts intended for local
edits and future PRs; they intentionally do not reuse the disposable cache
reset flow that the validation harness uses.

## CI and Pages

The repository includes these GitHub Actions workflows:

- `.github/workflows/ci.yml`
- `.github/workflows/reference-blueprints.yml`

`ci.yml` is the main verification workflow. It splits checks into four jobs:

- `Blueprint Build`
- `Blueprint Tests`
- `Harness Tests`
- `Reference Blueprint Build`

`reference-blueprints.yml` is the publication workflow. On pushes to `main`, it:

- runs the reference blueprint generation flow
- stages a Pages artifact under `_site/`
- uploads and deploys that artifact to GitHub Pages
- uses the shared reference-checkout mode in CI to avoid duplicating warmed
  `.lake/` trees on the GitHub runner

The staged Pages artifact layout is:

- `_site/index.html`
- `_site/reference-blueprints/noperthedron/`
- `_site/reference-blueprints/spherepackingblueprint/`

The staging helper is:

- `python3 ./scripts/prepare_reference_blueprints_pages.py`

## External Project Validation Direction

The harness is now project-driven rather than example-hardcoded.

- the default catalog points at `ejgallego/verso-noperthedron` and
  `ejgallego/verso-sphere-packing`
- catalog entries can also describe ephemeral `git_checkout` projects hosted
  outside this repository
- external entries should declare the repository ref plus the build and
  generation commands needed after checkout
- the harness currently rewrites the cloned `lakefile.lean` dependency line so
  external test projects exercise the local `VersoBlueprint` checkout instead
  of the committed upstream dependency
- the current local override injection expects a `lakefile.lean` project that
  declares `VersoBlueprint` from the official `leanprover/verso-blueprint` Git
  repository, but it tolerates different official Git refs and URL spellings
- local worktree bookkeeping is intentionally not tracked in the repository

Minimal external catalog entry shape:

```json
{
  "id": "some-user-project",
  "source": {
    "kind": "git_checkout",
    "repository": "https://github.com/org/some-user-project.git",
    "ref": "main",
    "project_root": "."
  },
  "build_command": ["lake", "build"],
  "generate_command": ["lake", "exe", "blueprint-gen", "--output", "{output_dir}"],
  "site_subdir": "html-multi"
}
```

That override policy is now the default maintainer behavior: the external
projects keep their committed dependency pointed at the official upstream repo,
while the harness swaps in a local path dependency ephemerally during
validation.

## Shared Preview Artifact

Each generated Blueprint site includes a shared preview manifest at:

`html-multi/-verso-data/blueprint-preview-manifest.json`

See [`MANUAL.md`](./MANUAL.md) for the manifest semantics and executable
inspection flags.

## Project-Local Option Policy

Repository-level Blueprint reference material lives in the main doc set. Project
specific option policy should stay with the project that owns it.

Current example-specific reference:

- [`ejgallego/verso-noperthedron/OPTIONS.md`](https://github.com/ejgallego/verso-noperthedron/blob/main/OPTIONS.md)

## Documentation Reading Order

1. Read [`../project_template/README.md`](../project_template/README.md) and
   [`GETTING_STARTED.md`](./GETTING_STARTED.md) for the user-facing project
   shape.
2. Read [`MANUAL.md`](./MANUAL.md) for authoring, rendering, and options.
3. Return here for repository-local commands, outputs, and worktree behavior.
4. Read [`CONTRIBUTING.md`](./CONTRIBUTING.md) for branch, commit, PR, and
   local coordination conventions.
5. Read [`DESIGN_RATIONALE.md`](./DESIGN_RATIONALE.md) before touching
   architecture boundaries.
6. Read [`ROADMAP.md`](./ROADMAP.md) before starting structural cleanup.
