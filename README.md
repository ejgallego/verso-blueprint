# Verso Blueprint

Verso Blueprint is a Lean package for writing mathematical blueprints in
[Verso](https://github.com/leanprover/verso).

It lets you write project documents that combine:

- informal mathematical exposition
- links to Lean declarations
- dependency-aware summary and graph pages
- generated HTML output with interactive previews

## Quick Start

### Build the Package

```bash
git clone https://github.com/leanprover/verso-blueprint.git
cd verso-blueprint
scripts/lean-low-priority lake build
```

### Learn the Authoring Model

Start with [doc/MANUAL.md](./doc/MANUAL.md).

That document covers:

- the smallest useful Blueprint file layout
- the main Blueprint block forms
- how blocks connect to Lean
- the current rendering surface and options

The intended package-facing generation interface is `lake exe blueprint-gen`.

If you want to inspect or maintain the reference blueprints used by this
repository, see
[doc/MAINTAINER_GUIDE.md](./doc/MAINTAINER_GUIDE.md).

## Acknowledgements and Related Work

Verso Blueprint builds on:

- [Verso](https://github.com/leanprover/verso), the document system used to
  write and render Blueprint documents
- [Lean 4](https://lean-lang.org/) and its package ecosystem
- [mathlib4](https://github.com/leanprover-community/mathlib4), which many real
  Blueprint projects depend on

This repository validates and publishes larger reference Blueprint projects from
external repositories:

- [`ejgallego/verso-noperthedron`](https://github.com/ejgallego/verso-noperthedron)
- [`ejgallego/verso-sphere-packing`](https://github.com/ejgallego/verso-sphere-packing)

## Documentation

- [doc/MANUAL.md](./doc/MANUAL.md): authoring surface, rendering semantics, and
  options
- [doc/MAINTAINER_GUIDE.md](./doc/MAINTAINER_GUIDE.md): repository-local
  workflow for reference blueprint generation, validation, CI publication, and
  linked worktrees
- [doc/CONTRIBUTING.md](./doc/CONTRIBUTING.md): branch, commit, PR, and local
  worktree coordination conventions
- [doc/DESIGN_RATIONALE.md](./doc/DESIGN_RATIONALE.md): architecture and design
  rationale
- [doc/ROADMAP.md](./doc/ROADMAP.md): active cleanup and follow-up work
- [doc/UPSTREAM_TODO.md](./doc/UPSTREAM_TODO.md): items intended to move back
  into `verso`
