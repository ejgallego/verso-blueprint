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
script/lean-low-priority lake build
```

### Learn the Authoring Model

Start with [doc/MANUAL.md](./doc/MANUAL.md).

That document covers:

- the smallest useful Blueprint file layout
- the main Blueprint block forms
- how blocks connect to Lean
- the current rendering surface and options

The intended package-facing generation interface is `lake exe blueprint-gen`.

If you want to inspect or maintain the example projects in this repository, see
[doc/MAINTAINER_GUIDE.md](./doc/MAINTAINER_GUIDE.md).

## Acknowledgements and Related Work

Verso Blueprint builds on:

- [Verso](https://github.com/leanprover/verso), the document system used to
  write and render Blueprint documents
- [Lean 4](https://lean-lang.org/) and its package ecosystem
- [mathlib4](https://github.com/leanprover-community/mathlib4), which many real
  Blueprint projects depend on

This repository also includes larger example Blueprint projects under
[`test-projects`](./test-projects), including Noperthedron and
Sphere-Packing-Lean.

## Documentation

- [doc/MANUAL.md](./doc/MANUAL.md): authoring surface, rendering semantics, and
  options
- [doc/MAINTAINER_GUIDE.md](./doc/MAINTAINER_GUIDE.md): repository-local
  workflow for example generation, validation, and linked worktrees
- [doc/DESIGN_RATIONALE.md](./doc/DESIGN_RATIONALE.md): architecture and design
  rationale
- [doc/ROADMAP.md](./doc/ROADMAP.md): active cleanup and follow-up work
- [doc/UPSTREAM_TODO.md](./doc/UPSTREAM_TODO.md): items intended to move back
  into `verso`
- [WORKTREE_DASHBOARD.md](./WORKTREE_DASHBOARD.md): linked-worktree inventory
