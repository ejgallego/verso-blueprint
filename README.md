# Verso Blueprint

Verso Blueprint is a Lean package for writing mathematical blueprints in
[Verso](https://github.com/leanprover/verso): documents that combine informal
mathematical exposition, Lean-linked declarations, dependency structure, and
publishable HTML output.

It extends the Verso manual genre with Blueprint-specific directives, summary
views, dependency graphs, bibliography support, and interactive previews for
statements, proofs, and Lean code.

## Status

This repository is close to its first standalone release. The current code
layout is already representative of the package, with three pre-release
differences to keep in mind:

- The example projects still live in `test-projects/`; they will move to their
  own repositories.
- We will add a smaller starter project and a reusable template.
- We will add project scaffolding so users can run `lake exe bp new`.
- The preferred end-user generation interface is `lake exe blueprint-gen`; the
  Python harness in this repository is maintainer tooling for the in-repo
  examples, not the intended user entry point.

Until that scaffolding lands, the supported way to get started is to build this
repository and study the in-repo examples.

## What You Get

- Informal blueprint blocks for definitions, theorems, proofs, groups, authors,
  and related metadata.
- Links from informal statements to Lean code, either through inline labeled
  code blocks or external declarations via `(lean := "...")`.
- Generated Blueprint summary and dependency-graph pages.
- Shared preview data for hover panels and inline statement/proof previews.
- Bibliography integration with backreferences from the generated site.
- Repository-local generation and validation commands for example projects.

## Getting Started Today

### Prerequisites

- Lean toolchain `leanprover/lean4:v4.29.0-rc6`

### Clone and Build

```bash
git clone https://github.com/leanprover/verso-blueprint.git
cd verso-blueprint
script/lean-low-priority lake build
```

### Preferred User Interface

```bash
lake exe blueprint-gen --help
```

Release-facing documentation should treat `lake exe blueprint-gen` as the main
user-facing entry point for building Blueprint output from a Lean project.

Users should not need Python helper scripts or a system Graphviz installation
as part of the normal Blueprint workflow.

### Current Verso Workflow

Today, a Blueprint project still follows the standard Verso pattern: you
maintain both

1. the Blueprint Lean source files, and
2. a small `lean_exe` target that renders the document into `_out/`.

In other words, a Blueprint is not just a set of chapter files. It also needs a
generator binary, typically driven with `lake exe ...`.

### Lake Setup

At the Lake level, a Blueprint project needs:

1. a dependency on this package,
2. one or more Lean modules containing the Blueprint content,
3. a `lean_exe` target that renders the document.

In this repository, that looks like this in [lakefile.lean](./lakefile.lean):

```lean
require verso from git "https://github.com/leanprover/verso"@"main"
require mathlib from git "https://github.com/leanprover-community/mathlib4"@"v4.29.0-rc6"

lean_lib Noperthedron where
  srcDir := "test-projects/Noperthedron"
  roots := #[`Authors, `Contents, `Chapters, `Noperthedron, `Bibliography, `Macros]

lean_exe noperthedron where
  srcDir := "test-projects/Noperthedron"
  root := `Main
  supportInterpreter := true
```

The important part is the split of responsibilities:

- the `lean_lib` target holds the Blueprint source modules,
- the `lean_exe` target is the renderer you run with `lake exe ...`.

### Current Repository Example Flow

Until the packaging work is finished, this repository still uses a local
maintainer harness for the in-repo examples:

```bash
./generate-example-blueprints.sh
./validate-example-blueprints.sh
```

That flow generates the current example sites at:

- `_out/example-blueprints/noperthedron/`
- `_out/example-blueprints/spherepackingblueprint/`

The default validation path:

- regenerates the example sites,
- runs the static Noperthedron panel regression check,
- runs the browser regression suite.

Lean tests are opt-in:

```bash
./validate-example-blueprints.sh --run-lean-tests
```

## A Small Blueprint Fragment

The exact project template is still being finalized, but the core authoring
model already looks like this:

```lean
import VersoManual
import VersoBlueprint
import VersoBlueprint.Commands.Graph
import VersoBlueprint.Commands.Summary
import VersoBlueprint.Commands.Bibliography

open Verso
open Verso.Genre.Manual
open Informal

#doc (Manual) "Contents" =>

:::definition "def:sample"
A sample informal definition.
:::

:::theorem "thm:sample" (lean := "Nat.add")
This theorem uses {uses "def:sample"}[].
:::

:::proof "thm:sample"
Proof sketch.
:::

{blueprint_graph}
{bp_summary}
{bp_bibliography}
```

And the corresponding executable is a small `Main.lean`-style entry point that
turns that document into site output:

```lean
import VersoManual
import VersoBlueprint.PreviewManifest
import Contents

open Verso Doc
open Verso.Genre Manual

def main (args : List String) : IO UInt32 :=
  Informal.PreviewManifest.manualMainWithSharedPreviewManifest
    (%doc Contents)
    args
    (extensionImpls := by exact extension_impls%)
```

That binary is the thing that ultimately writes `_out/...` when you run
`lake exe ...`. This is standard Verso workflow today, even if we want to make
it more turnkey.

## Manifest JSON

Blueprint builds emit a shared preview manifest at:

`html-multi/-verso-data/blueprint-preview-manifest.json`

The current executable entry points also support JSON-oriented inspection flags:

```bash
lake exe noperthedron --dump-schema
lake exe noperthedron --dump-manifest
lake exe noperthedron --output _out/noperthedron
```

- `--dump-schema` prints the JSON Schema for the shared preview manifest.
- `--dump-manifest` prints the generated manifest JSON instead of writing the
  site and then reading the file.
- `--output <dir>` writes the rendered site to the selected output directory.

For complete working examples, see:

- [`test-projects/Noperthedron`](./test-projects/Noperthedron)
- [`test-projects/Sphere-Packing-Lean`](./test-projects/Sphere-Packing-Lean)

## Repository Layout

- `src/VersoBlueprint`
  - the Blueprint library itself
- `tests`
  - library and rendering regression tests
- `browser-tests`
  - browser-level regression coverage for generated sites
- `script`
  - the local generation/validation harness
- `test-projects`
  - current pre-release example blueprints

## Working in Linked Worktrees

The maintainer harness is worktree-aware. Useful commands:

```bash
python3 -m script.blueprint_harness --help
python3 -m script.blueprint_harness paths
python3 -m script.blueprint_harness sync-root-lake
```

For new implementation work, prefer starting from a linked worktree under
`.worktrees/` and keep the root checkout as the stable base.

In linked worktrees, the harness writes artifacts to the shared repo-root
preview area under `_out/<worktree>/...` and prefers reusing the root checkout's
prepared `.lake` artifacts instead of rebuilding Mathlib locally.

## Documentation

- [`MANUAL.md`](./MANUAL.md)
  - directive-level notes, options, and rendering behavior
- [`doc/blueprint/USER_MANUAL.md`](./doc/blueprint/USER_MANUAL.md)
  - maintainer-oriented generation and validation workflow
- [`doc/blueprint/DESIGN_RATIONALE.md`](./doc/blueprint/DESIGN_RATIONALE.md)
  - architecture and implementation rationale
- [`doc/blueprint/ROADMAP.md`](./doc/blueprint/ROADMAP.md)
  - planned cleanup and follow-up work
- [`WORKTREE_DASHBOARD.md`](./WORKTREE_DASHBOARD.md)
  - current linked-worktree inventory for local development

## Near-Term Release Plan

Before the first release, we expect to:

1. move the current example projects out of this repository,
2. add a simpler starter example and a reusable project template,
3. expose project scaffolding through `lake exe bp new`,
4. make `lake exe blueprint-gen` the clear default interface for end users.

The current repo is already the right place to evaluate the library and its
rendering model; the main remaining work is packaging and onboarding.
