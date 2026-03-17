# Verso Blueprint

Verso Blueprint is a Lean package for writing Blueprint documents in
[Verso](https://github.com/leanprover/verso).

A Blueprint project combines:

- informal mathematical exposition
- links to local Lean code or existing Lean declarations
- rendered overview pages such as dependency graphs and summaries
- HTML output with previews and navigation

## Start Here

If you want to start a Blueprint project today, read these in order:

1. [project_template/README.md](./project_template/README.md)
2. [doc/GETTING_STARTED.md](./doc/GETTING_STARTED.md)
3. [doc/MANUAL.md](./doc/MANUAL.md)

The repository's Python harness and maintainer scripts are not part of the
normal end-user workflow.

## Current Project Shape

Today a Blueprint project usually owns three things:

- chapter modules containing the actual mathematical content
- a Blueprint top-level file that assembles chapters and rendered overview pages
- a small `lean_exe` named `blueprint-gen` that writes the generated site to
  `_out/`

`verso-blueprint` provides the Blueprint directives, rendering commands, preview
runtime, and support library code. The `blueprint-gen` executable belongs to
the Blueprint project itself. The starter layout in
[project_template/](./project_template/) shows the recommended shape.

## Core Features

### Writing the document

Blueprint chapters are written with directives such as:

- `:::definition`
- `:::lemma_`
- `:::theorem`
- `:::corollary`
- `:::proof`

These blocks are designed to keep the informal mathematical story close to the
formal Lean side.

### Connecting statements to Lean

A statement can connect to Lean in three main ways:

- a labeled local Lean code block
- an existing Lean declaration via `(lean := "...")`
- a manual completion marker via `(leanok := true)`

This lets one project mix already-formalized results, local formalization work,
and still-planned material.

### Rendering

Blueprint can render:

- chapter pages
- a dependency graph with `blueprint_graph`
- a summary page with `bp_summary` or `blueprint_summary`
- a bibliography page with `bp_bibliography` or `blueprint_bibliography`
- math-enabled HTML with shared previews

For normal Blueprint project usage, this does not require the repository's
Python helper scripts or a system Graphviz installation.

### Metadata and organization

Statements can carry groups, owners, tags, effort estimates, priorities, and
related metadata. The rendered summary and graph pages use that data to present
the project structure.

### Widget

Blueprint also has a widget-based graph panel surface. It is currently
experimental and should be treated as a developer-facing feature rather than the
main website-generation workflow.

## Larger Examples

The repository also validates and publishes larger reference Blueprint projects:

- [`ejgallego/verso-noperthedron`](https://github.com/ejgallego/verso-noperthedron)
- [`ejgallego/verso-sphere-packing`](https://github.com/ejgallego/verso-sphere-packing)

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
