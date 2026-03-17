# Getting Started

This guide is the shortest path from "I want a Blueprint project" to "I can
render a first site".

If you are new to Verso, the easiest approach is to copy the starter template
and keep the initial structure intact while you replace the example content.

## What You Are Building

A Blueprint project usually has three moving parts:

1. one or more chapter modules with the mathematical content
2. one Blueprint top-level file that assembles the document
3. one small `blueprint-gen` executable that renders the site

Many older examples call the top-level file `Contents.lean`. In this doc set we
refer to it as the Blueprint top-level file because the role matters more than
the filename.

## Start From the Template

Use [project_template/](../project_template/) as the starting point.

Its key files are:

- `ProjectTemplate/Chapters/Addition.lean`: the first chapter
- `ProjectTemplate/Blueprint.lean`: the Blueprint top-level file
- `ProjectTemplateMain.lean`: the generator executable entry point
- `lakefile.lean`: package configuration, including `blueprint-gen`

The template is intentionally small. It is meant to teach the shape of a
Blueprint project before you scale it up.

## The Three Verso Forms To Recognize First

If you are new to Verso, there are only three forms you need to understand at
the start:

- `#doc (Manual) "Title" =>` starts a document module
- `{include 0 Some.Module}` includes a chapter into the top-level file
- `:::...` blocks define Blueprint entries such as definitions and theorems

You can get a long way just by following those three patterns in the template.

## Learn the First Chapter

The chapter in
[project_template/ProjectTemplate/Chapters/Addition.lean](../project_template/ProjectTemplate/Chapters/Addition.lean)
shows the most important authoring patterns:

- a definition block
- a theorem block
- a proof block
- a `uses` link to another Blueprint entry
- a local Lean code block
- a statement linked to an existing Lean declaration
- optional metadata such as `parent`, `owner`, `tags`, `effort`, and `priority`

The example is about addition on natural numbers on purpose: it reads like a
real mathematical story, but it is still small enough to copy and adapt.

## Learn the Blueprint Top-Level File

The top-level file in
[project_template/ProjectTemplate/Blueprint.lean](../project_template/ProjectTemplate/Blueprint.lean)
does two jobs:

1. it includes the chapter modules into the document
2. it chooses which rendered overview pages to include

The starter template includes:

- the chapter itself with `{include ...}`
- a dependency graph with `{blueprint_graph}`
- a summary page with `{bp_summary}`

That is the core rendering surface most projects want first.

## Learn the Generator Executable

The executable in
[project_template/ProjectTemplateMain.lean](../project_template/ProjectTemplateMain.lean)
wraps the Verso manual renderer with Blueprint's shared preview-manifest step.

The corresponding `lakefile.lean` defines a user-facing executable named
`blueprint-gen`. That name is recommended because it makes the main workflow
obvious:

```bash
lake update
lake exe blueprint-gen --output _out/site
```

For normal project use, you do not need the repository's Python harness.

## What To Change First

After copying the template:

1. rename `ProjectTemplate` to your project name
2. change the document title in the Blueprint top-level file
3. replace the addition chapter with your own first chapter
4. keep the `blueprint-gen` executable and top-level file structure until your
   project is stable

## What To Read Next

After the first site renders:

1. read [doc/MANUAL.md](./MANUAL.md) for the full authoring surface
2. return to [project_template/README.md](../project_template/README.md) when
   you want to compare your project against the starter layout
3. ignore [doc/MAINTAINER_GUIDE.md](./MAINTAINER_GUIDE.md) unless you are
   maintaining this repository itself
