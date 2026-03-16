# Blueprint Design Rationale

Last updated: 2026-03-16

This document records the current architecture boundaries and the reasons the
Blueprint implementation is shaped the way it is.

It is intentionally not:

- the user-facing reference for options and rendering details
- the maintainer workflow guide
- the change backlog

Those responsibilities live in
[`MANUAL.md`](./MANUAL.md),
[`USER_MANUAL.md`](./USER_MANUAL.md), and
[`ROADMAP.md`](./ROADMAP.md).

## Architecture Snapshot

### Canonical Semantic Source

The canonical semantic source remains `Environment.State.data`. Rendering and
UI layers are expected to project from that state, not invent parallel sources
of truth.

### Command Split

Command modules are split by concern:

- `VersoBlueprint/Commands/Graph.lean`
- `VersoBlueprint/Commands/Summary.lean`
- `VersoBlueprint/Commands/Bibliography.lean`
- shared command JS in `VersoBlueprint/Commands/Common.lean`

Shared preview and rendering helpers live in `VersoBlueprint/Lib/`, notably:

- `HoverRender.lean`
- `PreviewSource.lean`

Command CSS is likewise split per command:

- `Commands/graph.css`
- `Commands/summary.css`
- `Commands/bibliography.css`

## Rendering Clients

Active consumers of Blueprint traversal data fall into three broad groups:

1. local link and block rendering:
   - `Inline.informal`
   - `Block.informal`
   - `Block.informalCode`
2. global rendered outputs:
   - `Block.graph`
   - `Block.summary`
   - `Block.bibliography`
3. widget/runtime clients:
   - preview consumers built on `PreviewSource`

This split is why one-source-of-truth pressure matters so much: local blocks,
global pages, and runtime widgets all need to agree on the same semantics while
projecting them differently.

## External Declaration Model

The external declaration flow is intentionally staged:

1. `(lean := "...")` references become `Data.ExternalRef`.
2. Snapshot and enrichment add presence, provenance, optional `sourceHref?`,
   and declaration rendering results.
3. Informal block rendering turns those snapshots into hover and panel views.
4. Summary and graph logic read the same snapshots for status reporting.

The goal is to avoid a world where local rendering, global status, and preview
surfaces each re-resolve external declarations differently.

## Ownership Boundaries

Two naming domains must stay distinct:

1. Blueprint node labels are Blueprint-owned metadata.
2. `(lean := "...")` names are Lean-owned identifiers.

That boundary matters because convenience policies for Blueprint labels must not
quietly rewrite or reinterpret external Lean declaration names.

## Preview Rationale

### Shared Browser Runtime

Preview behavior is correctness-sensitive and previously drifted through
copy-paste. The shared browser-side runtime therefore owns reusable preview
operations such as:

- template collection and decoding
- math rendering for inserted preview bodies
- anchored-panel positioning
- close-button policy
- subtree hydration for nested preview content

The goal is consistent preview behavior across inline references, summary
panels, graph panels, and other Blueprint surfaces.

### Separate Informal and Lean-Code Preview Identities

Statement and proof previews are keyed by `(label, facet)`. Lean-code previews
use `Informal.LeanCodePreview` under a Lean-name-oriented namespace.

That split is deliberate:

- statement/proof previews are blueprint-entry overviews
- Lean-code previews are declaration-centric navigation

The UI can converge while the identity schemes remain distinct.

### One Retrieval Surface for Callers

Even though traversal-time and widget/runtime paths use different internal
storage boundaries, call sites should converge on `PreviewSource` rather than
decode multiple payload forms directly.

### Self-Contained Snippet Rendering

Rendered HTML hovers are page-output scoped, while editor and LSP hovers are
info-tree scoped. Isolated renderers therefore cannot rely on shared hover-id
tables unless they also participate in the surrounding hover environment. That
is why Blueprint sometimes rewrites isolated hover payloads into self-contained
HTML.

## Graph and Completion Rationale

### Two-Track Status Model

The graph pipeline computes two orthogonal tracks per node:

- statement track (`StatementStatus`) drives border color
- proof/background track (`ProofStatus`) drives fill color

This keeps "can I state it?" separate from "can I finish the proof?" instead of
collapsing all progress into one overloaded color.

### Completion Policy

Completion blocking policy is centralized in `Informal.Data.ProvedStatus` via:

- `blocksStatementCompletion`
- `blocksProofCompletion`
- `anyBlocksStatementCompletion`
- `anyBlocksProofCompletion`

Definitions and theorem-like nodes intentionally differ:

- definitions are blocked by both type-side and body-side gaps
- theorem-like statements are blocked only by statement/type gaps
- proof completion is blocked by any gap

### Precision and Warning Policy

Inline code has finer-grained provenance than external declaration snapshots.
The UI should expose useful external information without pretending it has the
same precision as local literate code.

Warning conditions such as missing external declarations, local `sorry`, and
Lean-only-without-informal-statement are modeled separately from fill colors.
That keeps progress state and warning state orthogonal.

## Active Tension Points

These are the current architectural fault lines that still deserve care:

1. status semantics can still drift between local block rendering and global
   outputs
2. preview retrieval still has multiple internal representations and adapters
3. external hover and panel rendering still share concepts that are not fully
   unified in one view model
4. preview regressions are easy to miss without traversal-level regression
   coverage

Those concerns motivate the cleanup priorities tracked in
[`ROADMAP.md`](./ROADMAP.md).
