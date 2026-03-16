# Verso Blueprint

Verso Blueprint is a Lean package for writing mathematical blueprints in
[Verso](https://github.com/leanprover/verso). It extends the Verso manual genre
with Blueprint-specific directives, Lean-linked statements, dependency graphs,
summary views, bibliography support, and interactive previews for statements,
proofs, and Lean code.

## Status

This repository is close to its first standalone release.

Current pre-release realities:

- the example projects still live in [`test-projects`](./test-projects)
- the preferred end-user generation interface is `lake exe blueprint-gen`
- project scaffolding such as `lake exe bp new`, a smaller starter example, and
  a reusable template are planned but not landed yet

Release-facing documentation should treat `lake exe blueprint-gen` as the
intended front door. The Python harness in this repository is maintainer
tooling for the in-repo examples, not the long-term end-user workflow.

## What You Get

- informal blueprint blocks for definitions, lemmas, theorems, proofs, groups,
  authors, and related metadata
- links from informal statements to Lean code, either through inline labeled
  code blocks or external declarations via `(lean := "...")`
- generated summary and dependency-graph pages
- shared preview data for hover panels and inline statement/proof previews
- bibliography support with generated backreferences

## Getting Started Today

### Prerequisites

- Lean toolchain `leanprover/lean4:v4.29.0-rc6`

### Clone and Build

```bash
git clone https://github.com/leanprover/verso-blueprint.git
cd verso-blueprint
script/lean-low-priority lake build
```

### Evaluate the Current Examples

Until the starter template and scaffolding land, the supported way to evaluate
the package is to build the repository and inspect the in-repo examples:

```bash
./generate-example-blueprints.sh
./validate-example-blueprints.sh
```

For the maintainer validation workflow, linked-worktree behavior, and output
layout, see
[`doc/blueprint/USER_MANUAL.md`](./doc/blueprint/USER_MANUAL.md).

## Authoring Model Today

Blueprint projects currently follow the standard Verso workflow: the project
owns both the Blueprint source modules and a small `lean_exe` target that
renders the document into `_out/`.

In practice that means a Blueprint project needs:

1. a dependency on this package
2. one or more Lean modules containing the Blueprint content
3. a `lean_exe` target that renders the document

In this repository, the example setup in [lakefile.lean](./lakefile.lean) looks
like:

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

The `lean_lib` owns the Blueprint source modules. The `lean_exe` is the
renderer you run with `lake exe ...`.

## A Small Blueprint Fragment

The core authoring model already looks like this:

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

The corresponding executable is a small `Main.lean` entry point that writes the
site output:

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

Generated sites also include a shared preview manifest. For the manifest
location, flags, and rendering reference, see [MANUAL.md](./MANUAL.md).

## Repository Layout

- `src/VersoBlueprint`: the Blueprint library
- `tests`: library and rendering regression tests
- `browser-tests`: browser-level regression coverage for generated sites
- `script`: worktree-aware maintainer harness
- `test-projects`: current pre-release example blueprints

## Documentation Map

- [README.md](./README.md): package overview and current onboarding path
- [MANUAL.md](./MANUAL.md): options, metadata fields, rendering semantics, and
  preview-manifest reference
- [doc/blueprint/USER_MANUAL.md](./doc/blueprint/USER_MANUAL.md): maintainer
  workflow for generation, validation, and linked worktrees
- [doc/blueprint/DESIGN_RATIONALE.md](./doc/blueprint/DESIGN_RATIONALE.md):
  architecture and implementation rationale
- [doc/blueprint/ROADMAP.md](./doc/blueprint/ROADMAP.md): active cleanup and
  follow-up work
- [WORKTREE_DASHBOARD.md](./WORKTREE_DASHBOARD.md): linked-worktree inventory

## Examples

Complete working examples live in:

- [`test-projects/Noperthedron`](./test-projects/Noperthedron)
- [`test-projects/Sphere-Packing-Lean`](./test-projects/Sphere-Packing-Lean)
