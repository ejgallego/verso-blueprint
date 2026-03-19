# Blueprint Roadmap

Last updated: 2026-03-19

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
2. keep generating reference blueprint sites after boundary changes
3. prefer behavior-preserving refactors until the regression surface is broader
4. add direct regression coverage for preview-cache keying and JSON roundtrips

### Harness and External Project Support

Goal: keep the maintainer harness direct and repository-local while expanding it
carefully beyond the current baseline external reference blueprints.

Work:

1. keep the current shell wrappers thin and ergonomic
2. keep the Python harness as the single source of truth for orchestration,
   path logic, and project catalog loading
3. keep the project catalog explicit and small, with baseline external
   reference blueprints plus opt-in ephemeral GitHub checkout coverage
4. validate both root-checkout and linked-worktree flows end to end
5. stabilize output-path conventions for generation, static checks, and browser
   checks
6. add low-cost Python unit coverage for harness manifest and path logic so
   every harness change does not require a full example rebuild
7. add the minimum path and dependency override surface needed for testing a
   local `verso` checkout
8. add the minimum project override surface needed for Blueprint projects that
   live outside this repository
9. upstream a Lake improvement so updating one overridden dependency does not
   rewrite unrelated pinned transitive dependencies or require harness-side
   manifest cleanup to keep `verso` and `subverso` aligned with tracked
   reference manifests
10. add PR preview deployment that reuses the assembled reference `_site`
    artifact from CI instead of rebuilding the sites through a separate
    preview-only workflow

### Template Delivery and Client CI

Goal: provide a user-facing starter that can build and deploy a Blueprint site
to GitHub Pages, while keeping documentation and regression coverage anchored in
this repository.

Work:

1. keep a local in-repo template/example as the documentation-facing source of
   truth for project shape, authoring patterns, and generator wiring
2. add a root-level `.github/workflows/` Pages workflow plus one local CI
   script to the in-repo template so the user-facing contract is explicit and
   testable
3. add main-repository CI coverage that materializes the local template as a
   fresh standalone repository and runs that template-owned CI script end to
   end
4. keep the maintainer harness out of the user-facing template CI contract; the
   harness should validate or materialize templates, not be required by client
   repositories
5. evaluate whether to publish a separate external template repository as a
   generated or synchronized output of the local template source of truth,
   rather than maintaining two hand-edited templates
6. avoid Git submodules for template delivery unless a concrete synchronization
   problem remains unsolved by one-way export or sync automation
7. evaluate a dedicated `verso-blueprint` GitHub Action for the stable
   build-and-deploy path once the template workflow contract has settled
8. keep local smoke coverage and one real GitHub-hosted canary deployment
   separate, so routine PR validation does not depend on cross-repository Pages
   deployment

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
5. tracked local-worktree bookkeeping leaking into the public repository surface
6. drift between the local documented template, any exported external template,
   and the eventual GitHub Action contract
