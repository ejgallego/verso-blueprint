# Project Template

This folder is a copyable starter Blueprint project.

The goal is not to show every feature. The goal is to give you one small
project that already has the right moving parts:

- a chapter with real Blueprint blocks
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
  ProjectTemplateMain.lean
```

The important files are:

- `ProjectTemplate/Chapters/Addition.lean`: the first chapter, using a real
  addition example
- `ProjectTemplate/Blueprint.lean`: the Blueprint top-level file
- `ProjectTemplateMain.lean`: the rendering entry point
- `lakefile.lean`: the package definition and the `blueprint-gen` executable

## What The Template Demonstrates

- `:::definition`, `:::theorem`, and `:::proof`
- a local Lean code block attached to a Blueprint label
- a statement linked to an existing Lean declaration
- group and author metadata
- rendered summary and graph pages
- basic math rendering in the informal text

The experimental widget is not enabled by default in this starter template.

## Recommended Workflow

1. Copy this folder into a new repository.
2. Rename `ProjectTemplate` to your project name.
3. Keep the `blueprint-gen` executable and top-level file structure.
4. Replace the addition chapter with your own content.

Typical commands:

```bash
lake update
lake exe blueprint-gen --output _out/site
```

## About Dependencies

The template currently pins `verso` and `verso-blueprint` from Git. Replace
those refs with release tags when you move to a released version.
