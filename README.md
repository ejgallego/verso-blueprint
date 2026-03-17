# Verso Blueprint

Verso Blueprint is a Lean package for writing Blueprint documents in
[Verso](https://github.com/leanprover/verso).

A Blueprint project combines:

- informal mathematical exposition
- links to local Lean code or existing Lean declarations
- rendered overview pages such as dependency graphs and progress summaries
- HTML output with previews, navigation, and exported metadata

## Start Here

If you want to start a Blueprint project today, read these in order:

1. [project_template/README.md](./project_template/README.md)
2. [doc/GETTING_STARTED.md](./doc/GETTING_STARTED.md)
3. [doc/MANUAL.md](./doc/MANUAL.md)

## Current Project Shape

Today a Blueprint project usually owns three things:

- chapter modules containing the mathematical content
- a Blueprint top-level file that assembles chapters and rendered overview pages
- an executable named `blueprint-gen` that resolves forward references,
  computes metadata, and writes the generated output under `_out/`

`verso-blueprint` provides the Blueprint directives, rendering commands, preview
runtime, and support library code. The starter layout in
[project_template/](./project_template/) shows the recommended shape.

## Core Features

### Labelled nodes and rich directives

Every Blueprint node is identified by a label such as `addition_spec` or
`addition_zero_right`. Those labels drive cross-references, graph nodes,
summary entries, code associations, and metadata export.

Typical directives look like:

- `:::definition "addition_spec" (lean := "Nat.add, Nat.succ")`
- `:::theorem "addition_zero_right" (owner := "jason") (priority := "high")`
- `:::proof "addition_zero_right"`

### Connecting to Lean

Blueprint supports three main ways to connect informal nodes to Lean:

- inline code with a labeled Lean code block
- compiled code tagged with `@[blueprint "addition_zero_right"]`
- existing declarations referenced with `(lean := "Nat.add_assoc")`

### Math and TeX

Blueprint supports inline math such as $`n + 0 = n`$, display math, TeX
preludes via `tex_prelude`, and best-effort KaTeX linting during elaboration.
KaTeX is the renderer used by the generated HTML.

### Rendering to HTML

Blueprint can render:

- chapter pages
- a dependency graph with `blueprint_graph`
- a progress summary view with `blueprint_summary`
- a bibliography page with `bp_bibliography` or `blueprint_bibliography`
- math-enabled previews and cross-links

Progress is computed automatically from the status of the associated Lean code
and declarations, so the HTML summary and graph views stay aligned with the
formal side.

### Metadata export

Blueprint can dump structured metadata for other tools, including the shared
preview manifest and its schema. The main entry points are `--dump-manifest` and
`--dump-schema`.

### Widget

The widget surface is experimental. Import `VersoBlueprint.Widget` explicitly if
you want to enable it.

## Reference Blueprints

The repository also tracks larger reference blueprints.

- [`ejgallego/verso-noperthedron`](https://github.com/ejgallego/verso-noperthedron),
  [CI publication](https://github.com/leanprover/verso-blueprint/actions/workflows/reference-blueprints.yml)
- [`ejgallego/verso-sphere-packing`](https://github.com/ejgallego/verso-sphere-packing),
  [CI publication](https://github.com/leanprover/verso-blueprint/actions/workflows/reference-blueprints.yml)

## Documentation

Read the docs in this order:

1. [project_template/README.md](./project_template/README.md): copyable starter
   project and file layout
2. [doc/GETTING_STARTED.md](./doc/GETTING_STARTED.md): first Blueprint walkthrough
3. [doc/MANUAL.md](./doc/MANUAL.md): authoring and rendering reference
4. [doc/CONTRIBUTING.md](./doc/CONTRIBUTING.md): contribution conventions for
   this repository
5. [doc/MAINTAINER_GUIDE.md](./doc/MAINTAINER_GUIDE.md): repository-local
   generation, validation, CI publication, and worktree workflow
6. [doc/DESIGN_RATIONALE.md](./doc/DESIGN_RATIONALE.md): architecture and design
   boundaries
7. [doc/ROADMAP.md](./doc/ROADMAP.md): active cleanup and follow-up work
8. [doc/UPSTREAM_TODO.md](./doc/UPSTREAM_TODO.md): items intended to move back
   into `verso`

## Acknowledgements

Verso Blueprint builds on:

- [Verso](https://github.com/leanprover/verso), the document system used to
  write and render Blueprint documents
- [Lean 4](https://lean-lang.org/), the language and tooling used to elaborate
  the document and connect it to formal code
- Patrick Massot's Lean blueprints
- LeanArchitect
- Eric's Vergo side-to-side blueprints
