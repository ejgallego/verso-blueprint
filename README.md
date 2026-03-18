# Verso Blueprint

Verso Blueprint is a Lean package for writing Blueprint documents in
[Verso](https://github.com/leanprover/verso).

A Blueprint project combines:

- informal mathematical exposition
- links to local Lean code or existing Lean declarations
- automatic tracking of formalization progress by analyzing the associated Lean
  code and declarations, including incomplete declarations such as `sorry`
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
- a site-generation executable that resolves forward references, computes
  metadata, and writes the generated output under `_out/`

`verso-blueprint` provides the Blueprint directives, rendering commands, preview
runtime, and support library code. The starter layout in
[project_template/](./project_template/) shows the recommended shape.

## Core Features

### Labelled nodes and rich directives

Every Blueprint node is identified by a label such as `addition_spec` or
`addition_right_identity`. Those labels drive cross-references, graph nodes,
summary entries, code associations, and metadata export.

When roles such as `{uses "foo"}[]` or citations have an empty payload,
Blueprint can automatically render text such as `Theorem N`.

Typical directives look like:

- `:::definition "addition_spec" (lean := "Nat.add, Nat.succ")`
- `:::theorem "addition_right_identity" (owner := "jason") (priority := "high")`
- `:::proof "addition_right_identity"`

````md
:::definition "addition_spec" (lean := "Nat.add, Nat.succ")
We write $`a + b` for the result of adding $`b` to $`a`.
:::

:::theorem "addition_right_identity" (owner := "jason") (priority := "high")
For every natural number $`n`, adding zero on the right leaves it unchanged:
$`n + 0 = n`.
:::

```lean "addition_right_identity"
theorem nat_add_zero_right (n : Nat) : n + 0 = n := by
  simp
```
````

### Connecting to Lean

Blueprint supports three main ways to connect informal nodes to Lean:

- inline code with a labeled Lean code block
- compiled code tagged with `@[blueprint "addition_right_identity"]`
- existing declarations referenced with `(lean := "Nat.add_assoc")`

```lean
@[blueprint "addition_right_identity"]
theorem nat_add_zero_right (n : Nat) : n + 0 = n := by
  simp
```

```md
:::theorem "addition_assoc" (lean := "Nat.add_assoc, Nat.add_comm")
This informal node is linked to existing compiled Lean declarations.
:::
```

### Math and TeX

Blueprint supports inline math such as ``$`n + 0 = n` `` and display math such as
``$$`\sum_{i=0}^{n} i = \frac{n(n+1)}{2}` ``. It also supports TeX preludes via
`tex_prelude` and best-effort KaTeX linting during elaboration. KaTeX is the
renderer used by the generated HTML.

### Rendering to HTML

Blueprint can render:

- chapter pages
- a dependency graph with `blueprint_graph`
- a progress summary view with `blueprint_summary`
- a bibliography page with `blueprint_bibliography`
- math-enabled previews and cross-links

Progress is computed automatically from the status of the associated Lean code
and declarations, so the HTML summary and graph views stay aligned with the
formal side. In particular, incomplete Lean declarations such as `sorry`
contribute automatically to the reported progress state.

### Metadata export

Blueprint can dump structured metadata for other tools, including the shared
preview manifest and its schema. These are command-line flags passed to the
generator binary, such as `--dump-manifest` and `--dump-schema`.

### Widget

The widget surface is experimental. Import `VersoBlueprint.Widget` explicitly if
you want to enable it.

## Reference Blueprints

The repository also tracks larger reference blueprints.

- [`ejgallego/verso-noperthedron`](https://github.com/ejgallego/verso-noperthedron),
  [rendered site](https://leanprover.github.io/verso-blueprint/reference-blueprints/noperthedron/)
- [`ejgallego/verso-sphere-packing`](https://github.com/ejgallego/verso-sphere-packing),
  [rendered site](https://leanprover.github.io/verso-blueprint/reference-blueprints/spherepackingblueprint/)

## Documentation

### User Documentation

Read these in order:

1. [project_template/README.md](./project_template/README.md): copyable starter
   project and file layout
2. [doc/GETTING_STARTED.md](./doc/GETTING_STARTED.md): first Blueprint walkthrough
3. [doc/MANUAL.md](./doc/MANUAL.md): authoring and rendering reference

### Developer Documentation

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

Verso Blueprint builds directly on:

- [Verso](https://github.com/leanprover/verso), the document system used to
  write and render Blueprint documents
- [Lean 4](https://lean-lang.org/), the language and tooling used to elaborate
  the document and connect it to formal code

Verso Blueprint has also been greatly inspired by:

- [Patrick Massot's Lean blueprints](https://github.com/PatrickMassot/leanblueprint)
- [LeanArchitect](https://github.com/hanwenzhu/LeanArchitect)
- Side to side blueprints by Eric Vergo
