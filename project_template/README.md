# Project Template

This folder is a copyable starter Blueprint project.

The goal is not to show every feature. The goal is to give you one small
project that already has the right moving parts:

- chapter files with real Blueprint blocks
- a Blueprint top-level file
- a `blueprint-gen` executable
- rendered graph and summary pages

## File Layout

```text
project_template/
  .gitignore
  lakefile.lean
  lean-toolchain
  ProjectTemplate.lean
  ProjectTemplate/
    Blueprint.lean
    Chapters/
      Addition.lean
      Multiplication.lean
  ProjectTemplateMain.lean
```

The important files are:

- `ProjectTemplate/Chapters/Addition.lean`: the first chapter
- `ProjectTemplate/Chapters/Multiplication.lean`: the second chapter
- `ProjectTemplate/Blueprint.lean`: the Blueprint top-level file
- `ProjectTemplateMain.lean`: the rendering entry point
- `lakefile.lean`: the package definition and the `blueprint-gen` executable

## What the template demonstrates

- labels that identify Blueprint nodes
- `:::definition`, `:::theorem`, and `:::proof`
- local Lean code attached to a Blueprint label
- a statement linked to an existing Lean declaration
- group and author metadata
- rendered progress summary and dependency graph pages
- basic math rendering in the informal text

## Recommended workflow

1. Copy this folder into a new repository.
2. Rename `ProjectTemplate` to your project name.
3. Keep the `blueprint-gen` executable and top-level file structure.
4. Replace the addition and multiplication chapters with your own content.

Typical commands:

```bash
lake update
lake exe blueprint-gen --output _out/site
```

Run `lake update` once after copying the template. After that, use
`lake exe blueprint-gen` whenever you want to regenerate the site.

## About dependencies

The template currently pins `verso` and `verso-blueprint` from Git. Replace
those refs with release tags when you move to a released version.

## Next step

Continue with [doc/GETTING_STARTED.md](../doc/GETTING_STARTED.md).
