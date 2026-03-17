# Blueprint Manual

This document is the current reference for Blueprint authoring and rendering.

If you are starting a first project, read
[project_template/README.md](../project_template/README.md) and
[GETTING_STARTED.md](./GETTING_STARTED.md) before this manual.

## Mental Model

A Blueprint project usually owns three things:

- chapter modules containing the mathematical content
- a Blueprint top-level file that assembles the document
- a small `blueprint-gen` executable that renders the site

The Blueprint top-level file is often called `Contents.lean` in existing
projects, but the filename is not special. What matters is that one module
assembles the chapters and chooses the rendered overview pages.

## Minimal Project Shape

The starter template in [project_template/](../project_template/) uses this
layout:

```text
ProjectTemplate/
  Blueprint.lean
  Chapters/
    Addition.lean
ProjectTemplate.lean
ProjectTemplateMain.lean
lakefile.lean
```

The role of each file is:

- `ProjectTemplate/Chapters/Addition.lean`: a chapter with Blueprint blocks
- `ProjectTemplate/Blueprint.lean`: the Blueprint top-level file
- `ProjectTemplateMain.lean`: the renderer entry point
- `lakefile.lean`: the package definition and the `blueprint-gen` executable

## The Blueprint Top-Level File

The Blueprint top-level file assembles the rendered document.

Example:

`````lean
import Verso
import VersoManual
import VersoBlueprint
import VersoBlueprint.Commands.Graph
import VersoBlueprint.Commands.Summary
import ProjectTemplate.Chapters.Addition

open Verso.Genre
open Verso.Genre.Manual
open Informal

#doc (Manual) "Starter Blueprint" =>

This small Blueprint tracks a few basic facts about addition on natural numbers.

{include 0 ProjectTemplate.Chapters.Addition}

{blueprint_graph}
{bp_summary}
```

This file decides:

- which chapter modules are included
- whether the dependency graph is rendered
- whether the summary page is rendered
- whether other global pages such as the bibliography are rendered

## A First Chapter

The following chapter example uses descriptive labels and a real mathematical
story about addition.

`````
import Verso
import VersoManual
import VersoBlueprint

open Verso.Genre
open Verso.Genre.Manual
open Informal

#doc (Manual) "Addition" =>

:::group "addition.core"
Core statements about addition on natural numbers.
:::

:::author "starter.author" (name := "Project Author")
:::

:::definition "addition.spec" (parent := "addition.core")
We write $`a + b`$ for the result of adding $`b`$ to $`a`$.
This Blueprint starts with the most basic sanity checks around that operation.
:::

:::theorem "addition.zero_right" (parent := "addition.core") (owner := "starter.author") (tags := "starter, arithmetic") (effort := "small") (priority := "high")
For every natural number $`n`$, adding zero on the right leaves it unchanged:
$`n + 0 = n`$.
This is the first sanity check for {uses "addition.spec"}[].
:::

:::proof "addition.zero_right"
Induct on $`n`$. The base case is immediate and the inductive step unfolds one
successor on each side.
:::

```lean "addition.zero_right"
theorem addition_zero_right (n : Nat) : n + 0 = n := by
  simp
```

:::theorem "addition.assoc" (parent := "addition.core") (lean := "Nat.add_assoc")
For all natural numbers $`a`$, $`b`$, and $`c`$, addition is associative:
$`(a + b) + c = a + (b + c)`$.
This is another consequence of {uses "addition.spec"}[].
:::

:::proof "addition.assoc"
Lean already provides this theorem as `Nat.add_assoc`, so this Blueprint entry
links to an existing declaration instead of restating the code locally.
:::
`````

This example shows the core pattern:

- define an informal mathematical object
- attach later statements to it with `uses`
- keep informal proofs close to the statement
- connect to Lean either locally or through an existing declaration

## Core Block Forms

Blueprint chapters commonly use:

- `:::definition "..."`
- `:::lemma_ "..."`
- `:::theorem "..."`
- `:::corollary "..."`
- `:::proof "..."`

`:::proof "label"` attaches to the earlier statement with the same label.

## Connecting Blocks to Lean

Statement-like blocks can connect to Lean in three main ways.

### Local Lean code

Attach a labeled Lean code block to the same Blueprint label:

````md
:::theorem "addition.zero_right"
For every natural number $`n`$, $`n + 0 = n`$.
:::

```lean "addition.zero_right"
theorem addition_zero_right (n : Nat) : n + 0 = n := by
  simp
```
````

This is the clearest way to connect a Blueprint entry to local formalization
work in the same project.

### Existing Lean declarations

Use `(lean := "...")` when Lean already owns the declaration:

```md
:::theorem "addition.assoc" (lean := "Nat.add_assoc")
For all natural numbers $`a`$, $`b`$, and $`c`$, addition is associative.
:::
```

This links the Blueprint entry to an existing Lean declaration without copying
the declaration body into the chapter.

### Manual completion markers

Use `(leanok := true)` when you want to record that the Lean side is complete
without attaching a local code block or an explicit external declaration:

```md
:::theorem "addition.plan.complete" (leanok := true)
This entry is manually marked as complete on the Lean side.
:::
```

Notes:

- `(lean := "...")` points at Lean-owned declaration names
- Blueprint labels are Blueprint-owned metadata
- Blueprint label conventions do not rewrite external Lean names

## Groups, Authors, and Metadata

Use `:::group` to define reusable group metadata:

```md
:::group "addition.core"
Core statements about addition on natural numbers.
:::
```

Use `:::author` to define author metadata:

```md
:::author "starter.author" (name := "Project Author")
:::
```

Statement-like directives can carry:

- `(parent := "...")`
- `(owner := "...")`
- `(tags := "...")`
- `(effort := "small" | "medium" | "large")`
- `(priority := "high" | "medium" | "low")`
- `(pr_url := "https://github.com/org/repo/pull/123")`

These fields are primarily used by rendered overview pages and project triage
views.

## Rendering Surface

### Rendered statement blocks

Rendered statement headers show a stable Lean status badge. That badge indicates
whether the statement is connected to:

1. local labeled Lean code
2. an external Lean declaration
3. a manual completion marker

When local or external Lean material is available, the rendered page links or
previews the associated content.

### Dependency graph

`blueprint_graph` renders a dependency-oriented view of the current Blueprint
document.

Group metadata may be used to organize the presentation, but grouping does not
change dependency edges.

### Summary page

`bp_summary` and `blueprint_summary` render a summary page for the current
Blueprint document.

That page uses dependency data, completion state, and metadata to present:

- coverage information
- blockers
- project triage information
- grouped rollups by parent, owner, and tags

### Bibliography page

`bp_bibliography` and `blueprint_bibliography` render the bibliography entries
registered in the document.

Projects that do not use citations can omit this page entirely.

### Math rendering and previews

Blueprint pages support math rendering and shared previews in generated HTML.

The stable point for authors is simple:

- write the informal mathematics directly in the chapter
- render the site through `blueprint-gen`
- let the generated site provide the preview and navigation behavior

## The `blueprint-gen` Executable

The recommended project-facing interface is a small executable named
`blueprint-gen`.

Minimal example:

```lean
import VersoManual
import VersoBlueprint.PreviewManifest
import ProjectTemplate.Blueprint

open Verso Doc
open Verso.Genre Manual

def main (args : List String) : IO UInt32 :=
  Informal.PreviewManifest.manualMainWithSharedPreviewManifest
    (%doc ProjectTemplate.Blueprint)
    args
    (extensionImpls := by exact extension_impls%)
```

This executable belongs to the Blueprint project, not to the `verso-blueprint`
package checkout.

Typical usage:

```bash
lake exe blueprint-gen --output _out/site
```

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

## Preview Manifest

Blueprint builds emit a shared preview manifest at:

`html-multi/-verso-data/blueprint-preview-manifest.json`

Most authors do not need this file for routine writing. It is mainly useful
for:

- runtime preview support in generated sites
- tooling and integration work
- inspection and debugging

Useful inspection flags on a Blueprint executable:

```bash
lake exe blueprint-gen --dump-schema
lake exe blueprint-gen --dump-manifest
lake exe blueprint-gen --help
```

- `--dump-schema` prints the JSON Schema for the manifest
- `--dump-manifest` prints the generated manifest JSON instead of writing the
  site and then reading the file
- `--help` includes these manifest-related flags alongside the usual rendering
  options

## Experimental Widget

Blueprint also has a widget-based graph panel surface driven by
`#show_graph "label"`.

This feature is currently experimental.

Treat it as:

- useful for developer workflows and exploration
- separate from the normal `blueprint-gen` site-generation path
- likely to evolve faster than the core authoring surface

## Current Limits

- parent/group metadata is structural only; it does not change proof status or
  dependency edges
- group labels are metadata, not first-class reference targets
- unresolved Blueprint references currently degrade locally at the call site;
  they are not accumulated into a global diagnostics report
- some rendering details and summary ranking policies are still expected to
  evolve
