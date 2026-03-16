# Blueprint Manual

This document is the reference page for the current Blueprint-specific authoring
and rendering surface in this repository.

It covers:

- Blueprint options
- node and group metadata
- Lean-summary semantics
- summary/graph behavior
- shared preview-manifest output

Operational workflow lives in
[`doc/blueprint/USER_MANUAL.md`](./doc/blueprint/USER_MANUAL.md). Architecture
background and planned cleanup live in
[`doc/blueprint/DESIGN_RATIONALE.md`](./doc/blueprint/DESIGN_RATIONALE.md) and
[`doc/blueprint/ROADMAP.md`](./doc/blueprint/ROADMAP.md).

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

## Lean Association States

Statement headers always show the Lean badge `L∃∀N`.

There are three meaningful association states for an informal statement:

1. `inline`
   The statement has an associated labeled Lean code block. The badge links to
   the rendered code panel for that block.
2. `external`
   The statement uses `(lean := "...")` to point at external Lean declarations.
   The badge summarizes those declarations instead of a local code block.
3. `userOk`
   The statement uses `(leanok := true)` as a manual assertion that the Lean
   side is complete.

If none of those states is present, the header still renders a muted `L∃∀N`
badge as a stable placeholder for "no associated Lean code or declarations".

The compact header view is derived from a richer internal model:

- provenance/source track:
  - `inline`
  - `external`
  - `userOk`
  - `none`
- completion track:
  - `proved`
  - `missing`
  - `axiomLike`
  - `containsSorry`

The rendered chip vocabulary is intentionally small:

- `✓ L∃∀N`: Lean side is present and complete
- `⚠ L∃∀N`: Lean side is present but contains `sorry`
- `! L∃∀N`: external Lean references are missing
- `A L∃∀N`: Lean side is axiom-like
- `X L∃∀N`: there is no associated Lean code yet

Tooltip content carries the finer-grained distinction between statement-side and
proof-side incompleteness.

## Structural Metadata

### Group Labels

Use `:::group` to declare a group label and display header:

```md
:::group "local_linear_algebra"
Linear-algebra lemmas for local geometry.
:::
```

- the positional argument is the group label used by `parent := "..."`
- group labels are global in the Blueprint state
- redeclaring the same group with the same rendered header emits a warning
- redeclaring a group with a different rendered header emits an error

### Node Metadata

Statement-like Blueprint directives may declare structural and triage metadata:

```md
:::lemma_ "lem:pythagoras" (parent := "local_linear_algebra") (priority := "high")
...
:::
```

Supported fields:

- `(parent := "...")`
- `(owner := "...")`
- `(tags := "analysis, critical")`
- `(effort := "small" | "medium" | "large")`
- `(priority := "high" | "medium" | "low")`
- `(pr_url := "https://github.com/org/repo/pull/123")`

Author metadata is declared separately:

```md
:::author "alice" (name := "Alice Example") (url := "https://example.com/alice")
:::
```

Duplicate handling for `parent` and `priority` is conservative:

- same value: warning, existing value kept
- different value: error, existing value kept

## Summary and Graph Behavior

The `parent` and metadata fields currently affect two global outputs.

### Blueprint Summary

`blueprint_summary` and `bp_summary` combine dependency data, completion state,
and metadata into:

- inventory-oriented sections for counts and theorem-like entries by parent
- triage sections such as actionable priorities, statement/proof reuse, and
  ranked next steps
- structure and coverage sections such as informal-only, ready-to-formalize,
  blocked, root, and leaf views
- per-parent health rollups, using the declared `:::group` title when available

Explicit `(priority := "...")` metadata acts as an author override in actionable
ranking and parent-group next-step selection.

### Dependency Graph

`blueprint_graph` renders parent groups as Graphviz clusters:

- the `:::group` header text becomes the cluster label when available
- groups with only one child are filtered out
- grouping is structural metadata only and does not change dependency edges

## Shared Preview Manifest

Blueprint builds emit a shared preview manifest at:

`html-multi/-verso-data/blueprint-preview-manifest.json`

This file is the canonical runtime source for informal statement and proof
preview bodies. It also carries metadata such as `label`, `facet`, `kind`,
optional `href`, optional `parent`, dependencies, owner display name, tags,
priority, effort, and rendered `html`.

Useful inspection flags on a Blueprint executable:

```bash
lake exe noperthedron --dump-schema
lake exe noperthedron --dump-manifest
lake exe noperthedron --help
```

- `--dump-schema` prints the JSON Schema for the manifest
- `--dump-manifest` prints the generated manifest JSON instead of writing the
  site and then reading the file
- `--help` includes these manifest-related flags alongside the usual manual
  rendering options

## Current Limits

- parent/group metadata is structural only; it does not change proof status or
  dependency edges
- group labels are metadata, not first-class reference targets
- unresolved Blueprint references currently degrade locally at the call site;
  they are not accumulated into a global diagnostics report
- the local block-header group chip is shown only when a parent is shared by
  multiple entries, or when a `parent := "..."` label is present without a
  matching `:::group`
