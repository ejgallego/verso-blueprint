# Blueprint Roadmap

Last updated: 2026-03-16

This document tracks active cleanup and follow-up work for Blueprint support in
this repository.

It is not the place for:

- operational commands and workflow details
- option and rendering reference material
- architecture explanation

Those live in
[`MAINTAINER_GUIDE.md`](./MAINTAINER_GUIDE.md),
[`MANUAL.md`](./MANUAL.md), and
[`DESIGN_RATIONALE.md`](./DESIGN_RATIONALE.md).

## Guiding Constraints

The current cleanup work should preserve these constraints:

1. keep one semantic source of truth for Blueprint data and status derivation
2. keep command, traversal, and runtime paths aligned through shared library
   APIs
3. add regression coverage before large structural splits
4. keep the public maintainer harness small, explicit, and repository-local

## Active Workstreams

### Duplicate Identity Hardening

Goal: make duplicate Blueprint identities fail clearly instead of being accepted
locally or silently overwritten during imported-state aggregation.

Work:

1. reject invalid nested and duplicate block declarations before they mutate the
   active environment stack
2. make `Data.register` and block elaboration agree on whether a declaration was
   accepted, ignored, or rejected
3. detect imported collisions in
   `Informal.Environment.informalExt.addImportedFn` instead of silently letting
   later inserts overwrite earlier ones
4. apply the same collision policy to node labels, group labels, and author ids

Tests still needed:

1. same-module duplicate label cases in `Tests.BlueprintInformal`
2. nested invalid block cases in `Tests.BlueprintInformal`
3. cross-module duplicate labels via sibling providers plus one importing test
   module
4. cross-module duplicate groups and duplicate authors via the same pattern
5. transitive-import coverage so reexports cannot bypass collision detection

### Shared Status Semantics

Goal: remove the remaining duplicated status recomputation.

Work:

1. define a shared status record derived from `Data.Node` plus external
   declaration checks
2. route graph, summary, and local block status badges through that record
3. keep the compact UI vocabulary stable while centralizing the semantics behind
   it

### Preview API Consolidation

Goal: keep `PreviewSource` as the only retrieval abstraction visible to callers.

Work:

1. audit call sites for direct preview decoding
2. replace ad hoc decoding with shared APIs
3. keep traversal and widget adapters separate internally, but behind the same
   interface
4. consolidate widget preview cache (`elabStx`) and traversal preview cache
   (`PreviewCache.Entry`) behind one phase-safe representation
5. unify preview labels and titles behind one canonical API so graph, summary,
   and other surfaces stop mixing resolved titles, raw labels, and local
   fallbacks
6. reduce duplicated preview-domain decode logic across renderers
7. unify preview UI behavior across graph panels and summary hovers where that
   can be done without overcoupling the renderers
8. remove temporary runtime workarounds such as the graph preview handler
   `setTimeout` fallback once the underlying lifecycle is verified stable

### Validation Hardening

Goal: expand the regression surface before deeper refactors.

Work:

1. add targeted regression coverage for graph previews, summary previews,
   bibliography citations/backrefs, and widget statement preview rendering
2. keep generating example sites after boundary changes
3. prefer behavior-preserving refactors until the regression surface is broader
4. add direct regression coverage for preview-cache keying and JSON roundtrips

### Harness and External Project Support

Goal: keep the maintainer harness direct and repository-local while expanding it
carefully beyond the in-repo examples.

Work:

1. keep the current shell wrappers thin and ergonomic
2. keep the Python harness as the single source of truth for orchestration and
   path logic
3. validate both root-checkout and linked-worktree flows end to end
4. stabilize output-path conventions for generation, static checks, and browser
   checks
5. add the minimum path and dependency override surface needed for testing a
   local `verso` checkout
6. add the minimum project override surface needed for Blueprint projects that
   live outside this repository

## UI Follow-Ups

These are secondary to semantic consolidation, but still worthwhile:

1. hide zero-value summary cards and sections by default
2. collapse duplicate blocker lists into one filtered blockers section
3. prefer one primary theorem list by default instead of parallel repeated
   views
4. use compact status chips where possible
5. consider a compact-mode toggle once the semantics are stable
6. revisit the graph page with a CSS-first layout architecture so canvas sizing
   is less runtime-driven

## Risks to Watch

1. silent divergence between local and global status rendering
2. preview regressions that compile-only checks will not catch
3. imported duplicate collisions for labels, groups, or authors
4. workflow drift across long-lived worktrees and branches
