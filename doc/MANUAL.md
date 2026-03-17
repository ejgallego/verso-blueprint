# Blueprint Manual

This document explains the current Blueprint authoring surface in this
repository.

A Blueprint is a mathematical project document that mixes informal exposition
with links to Lean declarations, dependency information, and generated summary
and graph pages.

Verso is the document system used to write and render those documents.

It is organized around two reader questions:

1. what can I write in a Blueprint source file?
2. what does that source render into?

Operational workflow lives in
[`MAINTAINER_GUIDE.md`](./MAINTAINER_GUIDE.md). Architecture background and planned
cleanup live in [`DESIGN_RATIONALE.md`](./DESIGN_RATIONALE.md) and
[`ROADMAP.md`](./ROADMAP.md).

## What You Can Write

### Document Skeleton

A Blueprint project currently has three main pieces:

- a `Contents` module that assembles the document
- one or more chapter modules containing the document content
- a small `Main` executable that renders the site

Example source entry points:

- [`verso-noperthedron/Contents.lean`](https://github.com/ejgallego/verso-noperthedron/blob/main/Contents.lean)
- [`verso-noperthedron/Main.lean`](https://github.com/ejgallego/verso-noperthedron/blob/main/Main.lean)
- [`verso-sphere-packing/SpherePackingBlueprint/Contents.lean`](https://github.com/ejgallego/verso-sphere-packing/blob/main/SpherePackingBlueprint/Contents.lean)
- [`verso-sphere-packing/SpherePackingBlueprintMain.lean`](https://github.com/ejgallego/verso-sphere-packing/blob/main/SpherePackingBlueprintMain.lean)

<!-- Future inline image: example document landing page or rendered chapter index. -->

### A Minimal Blueprint File Set

The smallest useful setup usually has three files:

1. one chapter file with the actual Blueprint blocks
2. one `Contents` file that assembles the document
3. one `Main` file that renders the site

Minimal chapter example:

```lean
import Verso
import VersoManual
import VersoBlueprint

open Verso.Genre
open Verso.Genre.Manual
open Informal

#doc (Manual) "Chapter" =>

:::definition "def:sample"
A sample informal definition.
:::

:::theorem "thm:sample" (lean := "Nat.add")
This theorem uses {uses "def:sample"}[].
:::

:::proof "thm:sample"
Proof sketch.
:::
```

Minimal `Contents.lean` example:

```lean
import Verso
import VersoManual
import VersoBlueprint
import VersoBlueprint.Commands.Graph
import VersoBlueprint.Commands.Summary
import VersoBlueprint.Commands.Bibliography
import Chapter

open Verso.Genre
open Verso.Genre.Manual
open Informal

#doc (Manual) "Contents" =>

{include 0 Chapter}

{blueprint_graph}
{bp_summary}
{bp_bibliography}
```

Minimal `Main.lean` example:

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

This three-file shape is the main thing to understand before worrying about the
larger reference blueprints.

### Core Content Blocks

Blueprint chapters use block directives for mathematical content. The main ones
used in the current examples are:

- `:::definition "..."`
- `:::lemma_ "..."`
- `:::theorem "..."`
- `:::corollary "..."`
- `:::proof "..."`

Typical usage:

```md
:::definition "def:sample"
A sample informal definition.
:::

:::theorem "thm:sample" (lean := "Nat.add")
This theorem uses {uses "def:sample"}[].
:::

:::proof "thm:sample"
Proof sketch.
:::
```

The `:::proof "..."` block attaches to the earlier statement with the same
label.

Example source modules:

- [`verso-noperthedron/Chapters/Noperthedron.lean`](https://github.com/ejgallego/verso-noperthedron/blob/main/Chapters/Noperthedron.lean)
- [`verso-sphere-packing/SpherePackingBlueprint/Chapters/SpherePackings.lean`](https://github.com/ejgallego/verso-sphere-packing/blob/main/SpherePackingBlueprint/Chapters/SpherePackings.lean)

<!-- Future inline image: one rendered theorem block with its attached proof. -->

### How Blocks Connect to Lean

Statement-like blocks can connect to Lean in three main ways:

1. inline labeled Lean code blocks
2. external declarations via `(lean := "...")`
3. manual completion via `(leanok := true)`

Inline example:

````md
:::lemma_ "lem:sample"
Informal statement.
:::

```lean "lem:sample"
theorem sample : True := by
  trivial
```
````

External declaration example:

```md
:::theorem "thm:sample" (lean := "Nat.add")
...
:::
```

Manual completion example:

```md
:::theorem "thm:planned" (leanok := true)
...
:::
```

Notes:

- `(lean := "...")` points at Lean-owned declaration names
- Blueprint label conventions do not rewrite external Lean names
- current examples include both single-name and comma-separated external
  declaration strings

Example source modules:

- [`verso-noperthedron/Chapters/Noperthedron.lean`](https://github.com/ejgallego/verso-noperthedron/blob/main/Chapters/Noperthedron.lean)
- [`verso-sphere-packing/SpherePackingBlueprint/Chapters/ModularForms.lean`](https://github.com/ejgallego/verso-sphere-packing/blob/main/SpherePackingBlueprint/Chapters/ModularForms.lean)

<!-- Future inline image: local block header showing Lean badge and code-panel link. -->

### Groups and Authors

Use `:::group` to declare a reusable group label and the text shown for that
group:

```md
:::group "local_linear_algebra"
Linear-algebra lemmas for local geometry.
:::
```

Use `:::author` to declare author metadata:

```md
:::author "alice" (name := "Alice Example") (url := "https://example.com/alice")
:::
```

Group labels and author ids are global within the document state.

Example source modules:

- [`verso-noperthedron/Authors.lean`](https://github.com/ejgallego/verso-noperthedron/blob/main/Authors.lean)
- [`verso-sphere-packing/SpherePackingBlueprint/Chapters/SpherePackings.lean`](https://github.com/ejgallego/verso-sphere-packing/blob/main/SpherePackingBlueprint/Chapters/SpherePackings.lean)

<!-- Future inline image: author panel or grouped summary section. -->

### Statement Metadata

Statement-like directives may also declare extra metadata:

```md
:::lemma_ "lem:pythagoras" (parent := "local_linear_algebra") (priority := "high")
...
:::
```

Current metadata fields:

- `(parent := "...")`
- `(owner := "...")`
- `(tags := "...")`
- `(effort := "small" | "medium" | "large")`
- `(priority := "high" | "medium" | "low")`
- `(pr_url := "https://github.com/org/repo/pull/123")`

How these relationships work:

- `parent := "..."` points at a `:::group`
- `owner := "..."` points at a `:::author`
- `priority` expresses author intent and may be used by summary or other
  overview pages
- the remaining fields are currently display-oriented metadata

Duplicate handling is conservative:

- same `parent` or `priority` value: warning, existing value kept
- different `parent` or `priority` value: error, existing value kept

## What It Renders

### Rendered Statement Blocks

Statement headers always show the Lean badge `L∃∀N`.

There are three main ways an informal statement can be associated with Lean:

1. `inline`
   The statement has an associated labeled Lean code block. The badge links to
   the rendered code panel for that block.
2. `external`
   The statement uses `(lean := "...")` to point at external Lean declarations.
   The badge summarizes those declarations instead of a local code block.
3. `userOk`
   The statement uses `(leanok := true)` as a manual assertion that the Lean
   side is complete.

If none of those states is present, the header still renders a muted `L∃∀N`
badge as a stable placeholder for "no associated Lean code or declarations".

The exact chip vocabulary and presentation details are still provisional. The
stable point for authors is that the local block header indicates whether Lean
content is present, missing, or incomplete, and links into the associated Lean
material when available.

More detailed distinctions, including tooltip wording and status refinement, are
still expected to evolve.

### Summary Page Behavior

`blueprint_summary` and `bp_summary` render a summary page for the current
Blueprint document.

Today that page uses dependency data, completion state, and metadata to provide
an overview of the document and highlight work that may deserve attention next.

The exact summary layout and ranking policy are still expected to evolve. The
stable point for authors is that group and statement metadata may influence
summary organization and prioritization.

<!-- Future inline image: summary page with group rollups and priority cards. -->

### Dependency Graph Behavior

`blueprint_graph` renders a dependency-oriented view of the current Blueprint
document.

Group metadata may be used to visually organize the graph, but grouping is
structural metadata only and does not change dependency edges.

<!-- Future inline image: dependency graph with grouped clusters. -->

## Blueprint Options

Set Blueprint options with ordinary Lean `set_option` commands in the module
that elaborates the Blueprint chapter or document:

```lean
set_option verso.blueprint.numbering global
set_option verso.blueprint.foldProofs true
```

Current options:

- `verso.blueprint.numbering`
  - default: `sub`
  - `sub`: chapter-prefixed numbering such as `Theorem 5.5`
  - `global`: document-order numbering such as `Theorem 27`
  - `local`: legacy local numbering without a chapter prefix
- `verso.blueprint.foldProofs`
  - default: `true`
  - folds proof bodies in rendered Lean code panels after `by`
- `verso.blueprint.trimTeXLabelPrefix`
  - default: `false`
  - trims TeX-style label prefixes when deriving Lean names
- `verso.blueprint.math.lint`
  - default: `true`
  - runs best-effort KaTeX validation during elaboration
- `verso.blueprint.externalCode.strictResolve`
  - default: `false`
  - upgrades unresolved or ambiguous `(lean := "...")` names from warnings to
    errors
- `verso.blueprint.externalCode.sourceLinkTemplate`
  - default: `""` (disabled)
  - builds source links for external declarations using `{path}`, `{relpath}`,
    `{module}`, `{line}`, and `{column}`
- `verso.blueprint.graph.defaultDirection`
  - default: `TB`
  - sets the fallback graph direction for `blueprint_graph` when
    `(direction := ...)` is omitted
- `verso.blueprint.profile`
  - default: `false`
  - enables timing logs for Blueprint directive and code-block elaboration

Project-specific option examples:

- [`verso-noperthedron/Contents.lean`](https://github.com/ejgallego/verso-noperthedron/blob/main/Contents.lean)
- [`verso-noperthedron/Chapters/Noperthedron.lean`](https://github.com/ejgallego/verso-noperthedron/blob/main/Chapters/Noperthedron.lean)
- [`verso-noperthedron/OPTIONS.md`](https://github.com/ejgallego/verso-noperthedron/blob/main/OPTIONS.md)

## Preview Manifest

Blueprint builds emit a shared preview manifest at:

`html-multi/-verso-data/blueprint-preview-manifest.json`

Most authors do not need this file for routine writing. It is mainly useful
for:

- runtime preview support in generated sites
- tooling and integration work
- inspection and debugging

It is the canonical runtime source for informal statement and proof preview
bodies. It also carries metadata such as `label`, `facet`, `kind`, optional
`href`, optional `parent`, dependencies, owner display name, tags, priority,
effort, and rendered `html`.

Useful inspection flags on a Blueprint executable:

```bash
lake exe noperthedron --dump-schema
lake exe noperthedron --dump-manifest
lake exe noperthedron --help
```

- `--dump-schema` prints the JSON Schema for the manifest
- `--dump-manifest` prints the generated manifest JSON instead of writing the
  site and then reading the file
- `--help` includes these manifest-related flags alongside the usual manual
  rendering options

## Current Limits

- parent/group metadata is structural only; it does not change proof status or
  dependency edges
- group labels are metadata, not first-class reference targets
- unresolved Blueprint references currently degrade locally at the call site;
  they are not accumulated into a global diagnostics report
- the local block-header group chip is shown only when a parent is shared by
  multiple entries, or when a `parent := "..."` label is present without a
  matching `:::group`
