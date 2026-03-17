# Blueprint Manual

This document is the current reference for Blueprint authoring and rendering.

If you are starting a first project, read
[project_template/README.md](../project_template/README.md) and
[GETTING_STARTED.md](./GETTING_STARTED.md) before this manual.

## Contents

- [Mental Model](#mental-model)
- [Labels and Node Identity](#labels-and-node-identity)
- [Minimal Project Shape](#minimal-project-shape)
- [The Blueprint Top-Level File](#the-blueprint-top-level-file)
- [A First Chapter](#a-first-chapter)
- [Core Block Forms](#core-block-forms)
- [Connecting Blocks to Lean](#connecting-blocks-to-lean)
- [Math and TeX](#math-and-tex)
- [Groups, Authors, and Metadata](#groups-authors-and-metadata)
- [Rendering Surface](#rendering-surface)
- [Metadata Export and Preview Manifest](#metadata-export-and-preview-manifest)
- [The `blueprint-gen` Executable](#the-blueprint-gen-executable)
- [Blueprint Options](#blueprint-options)
- [Experimental Widget](#experimental-widget)
- [Current Limits](#current-limits)

## Mental Model

A Blueprint project usually owns three things:

- chapter modules containing the mathematical content
- a Blueprint top-level file that assembles the document
- a `blueprint-gen` executable that renders the site

The Blueprint top-level file is often called `Contents.lean` in existing
projects, but the filename is not special. What matters is that one module
assembles the chapters and chooses the rendered overview pages.

## Labels and Node Identity

Blueprint nodes are identified by labels chosen by the author.

Examples:

- statement labels such as `addition_spec` and `addition_zero_right`
- group labels such as `addition_core`
- author ids such as `jason`

These identifiers are used by:

- `{uses "addition_spec"}[]` references
- labeled inline Lean code blocks
- `@[blueprint "label"]` on compiled Lean declarations
- summary and graph nodes
- preview lookup and exported metadata

Choose labels early and treat them as stable project identifiers.

## Minimal Project Shape

The starter template in [project_template/](../project_template/) uses this
layout:

```text
ProjectTemplate/
  Blueprint.lean
  Chapters/
    Addition.lean
    Multiplication.lean
ProjectTemplate.lean
ProjectTemplateMain.lean
lakefile.lean
```

The role of each file is:

- `ProjectTemplate/Chapters/Addition.lean`: a chapter with Blueprint blocks
- `ProjectTemplate/Chapters/Multiplication.lean`: another chapter with the same
  pattern
- `ProjectTemplate/Blueprint.lean`: the Blueprint top-level file
- `ProjectTemplateMain.lean`: the renderer entry point
- `lakefile.lean`: the package definition and the `blueprint-gen` executable

## The Blueprint Top-Level File

The Blueprint top-level file assembles the rendered document.

Example:

```lean
import Verso
import VersoManual
import VersoBlueprint
import VersoBlueprint.Commands.Graph
import VersoBlueprint.Commands.Summary
import ProjectTemplate.Chapters.Addition
import ProjectTemplate.Chapters.Multiplication

open Verso.Genre
open Verso.Genre.Manual
open Informal

#doc (Manual) "Starter Blueprint" =>

This small Blueprint tracks a few basic facts about addition and multiplication
on natural numbers.

{include 0 ProjectTemplate.Chapters.Addition}
{include 0 ProjectTemplate.Chapters.Multiplication}

{blueprint_graph}
{blueprint_summary}
```

This file decides:

- which chapter modules are included
- whether the dependency graph is rendered
- whether the summary page is rendered
- whether other global pages such as the bibliography are rendered

## A First Chapter

The following chapter example uses descriptive labels and a real mathematical
story about addition.

````lean
import Verso
import VersoManual
import VersoBlueprint

open Verso.Genre
open Verso.Genre.Manual
open Informal

#doc (Manual) "Addition" =>

:::group "addition_core"
Core statements about addition on natural numbers.
:::

:::author "project_author" (name := "Project Author")
:::

:::definition "addition_spec" (parent := "addition_core")
We write $`a + b`$ for the result of adding $`b`$ to $`a`$.
This Blueprint starts with the most basic sanity checks around that operation.
:::

:::theorem "addition_zero_right" (parent := "addition_core") (owner := "project_author") (tags := "starter, arithmetic") (effort := "small") (priority := "high")
For every natural number $`n`$, adding zero on the right leaves it unchanged:
$`n + 0 = n`$.
This is the first sanity check for {uses "addition_spec"}[].
:::

:::proof "addition_zero_right"
Induct on $`n`$. The base case is immediate and the inductive step unfolds one
successor on each side.
:::

```lean "addition_zero_right"
theorem addition_zero_right (n : Nat) : n + 0 = n := by
  simp
```

:::theorem "addition_assoc" (parent := "addition_core") (lean := "Nat.add_assoc")
For all natural numbers $`a`$, $`b`$, and $`c`$, addition is associative:
$`(a + b) + c = a + (b + c)`$.
This is another consequence of {uses "addition_spec"}[].
:::

:::proof "addition_assoc"
Lean already provides this theorem as `Nat.add_assoc`, so this Blueprint entry
links to an existing declaration instead of restating the code locally.
:::
````

This example shows the core pattern:

- define an informal mathematical object
- attach later statements to it with `uses`
- keep informal proofs close to the statement
- connect to Lean either locally or through an existing declaration

## Core Block Forms

Blueprint chapters commonly use:

- `:::definition "label_1"`
- `:::lemma_ "label_2"`
- `:::theorem "label_3"`
- `:::corollary "label_4"`
- `:::proof "label_3"`

`:::proof "label_3"` attaches to the earlier statement with the same label.

## Connecting Blocks to Lean

Statement-like blocks can connect to Lean in three main ways.

### Inline Lean code

Attach a labeled Lean code block to the same Blueprint label:

````md
:::theorem "addition_zero_right"
For every natural number $`n`$, $`n + 0 = n`$.
:::

```lean "addition_zero_right"
theorem addition_zero_right (n : Nat) : n + 0 = n := by
  simp
```
````

This is the clearest way to connect a Blueprint entry to local formalization
work in the same project.

### Compiled code tagged with `@[blueprint "addition_assoc_compiled"]`

Use the `@[blueprint "label"]` attribute when a compiled definition or theorem
should appear as a Lean-owned Blueprint node:

```lean
/-- Associativity of addition, exposed as a Lean-owned blueprint node. -/
@[blueprint "addition_assoc_compiled"]
theorem addition_assoc_compiled (a b c : Nat) : (a + b) + c = a + (b + c) := by
  simpa [Nat.add_assoc]
```

This mode is useful when the formal declaration already exists as ordinary Lean
code and you want to register it as a Blueprint node.

### Existing Lean declarations

Use `(lean := "Nat.add_assoc")` when Lean already owns the declaration and you
want an informal Blueprint node to point at it:

```md
:::theorem "addition_assoc" (lean := "Nat.add_assoc")
For all natural numbers $`a`$, $`b`$, and $`c`$, addition is associative.
:::
```

This links the Blueprint entry to an existing Lean declaration without copying
the declaration body into the chapter.

Notes:

- `(lean := "Nat.add_assoc")` points at Lean-owned declaration names
- `@[blueprint "addition_assoc_compiled"]` registers a Lean-owned Blueprint node
- Blueprint labels are Blueprint-owned metadata
- Blueprint label conventions do not rewrite external Lean names

## Math and TeX

Blueprint supports ordinary Verso math syntax inside the informal text.

Examples:

- inline math: `$`n + 0 = n`$`
- display math: `$$(a + b) + c = a + (b + c)$$`

Projects can also define reusable TeX macros:

```lean
tex_prelude r#"\newcommand{\NatAdd}{\mathbin{+}}"#
```

After that, Blueprint math can use the macro in rendered pages:

```md
We write $`a \NatAdd b`$ for addition on natural numbers.
```

Blueprint also supports best-effort KaTeX linting during elaboration. KaTeX is
the renderer used by the generated HTML, so this helps catch math problems
before the final site render.

## Groups, Authors, and Metadata

Use `:::group` to define reusable group metadata:

```md
:::group "group_1"
Core statements for the first chapter.
:::
```

Use `:::author` to define author metadata:

```md
:::author "author_1" (name := "Jason Example")
:::
```

Statement-like directives can carry:

- `(parent := "group_1")`
- `(owner := "author_1")`
- `(tags := "starter, arithmetic")`
- `(effort := "small" | "medium" | "large")`
- `(priority := "high" | "medium" | "low")`
- `(pr_url := "https://github.com/org/repo/pull/123")`

These fields are primarily used by rendered overview pages and project triage
views.

## Rendering Surface

### Rendered statement blocks

Rendered statement headers show a Lean status badge and related metadata.
When local or external Lean material is available, the rendered page links or
previews the associated content.

### Dependency graph

`blueprint_graph` renders a dependency-oriented view of the current Blueprint
document.

Group metadata may be used to organize the presentation, but grouping does not
change dependency edges.

### Progress summary

`blueprint_summary` renders a summary page for the current Blueprint document.

That page uses dependency data, metadata, and Lean status to present:

- automatic progress counts
- blockers and incomplete declarations
- project triage information
- grouped rollups by parent, owner, and tags

### Bibliography page

`bp_bibliography` and `blueprint_bibliography` render the bibliography entries
registered in the document.

Projects that do not use citations can omit this page entirely.

### Math-enabled previews

Blueprint pages support shared previews in generated HTML, including math
rendering through KaTeX.

## Metadata Export and Preview Manifest

Blueprint builds emit a shared preview manifest at:

`html-multi/-verso-data/blueprint-preview-manifest.json`

Most authors do not need this file for routine writing. It is mainly useful
for:

- runtime preview support in generated sites
- tooling and integration work
- metadata export for other tools
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

## The `blueprint-gen` Executable

The recommended project-facing interface is an executable named
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
  - upgrades unresolved or ambiguous external Lean names from warnings to errors
- `verso.blueprint.externalCode.sourceLinkTemplate`
  - default: `""` (disabled)
  - builds source links for external declarations using `{path}`, `{relpath}`,
    `{module}`, `{line}`, and `{column}`
- `verso.blueprint.graph.defaultDirection`
  - default: `TB`
  - sets the fallback graph direction for `blueprint_graph` when
    `(direction := ...)` is omitted
- `verso.blueprint.debug.commands`
  - default: `false`
  - emits debug info logs while elaborating Blueprint graph, summary, and
    bibliography commands
- `verso.blueprint.profile`
  - default: `false`
  - enables timing logs for Blueprint directive and code-block elaboration

## Experimental Widget

The widget surface is experimental.

To enable it, import `VersoBlueprint.Widget` explicitly in the project that
wants to use it.

## Current Limits

- parent/group metadata is structural only; it does not change proof status or
  dependency edges
- group labels are metadata, not first-class reference targets
- unresolved Blueprint references currently degrade locally at the call site;
  they are not accumulated into a global diagnostics report
- some rendering details and summary ranking policies are still expected to
  evolve
