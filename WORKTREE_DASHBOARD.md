# Worktree Dashboard

Last updated: 2026-03-13 (migrated from the old monorepo dashboard; this file is now the active dashboard, and the old repo has been reduced to archival-only reference material)

## Active Worktrees

### `main` (root checkout)

- Status: `active`
- Summary: extracted `VersoBlueprint` package on Lean `v4.29.0-rc6`; the extracted layout, toolchain repair, and migration bookkeeping baseline now live on `main`.
- Path: `/home/egallego/lean/verso-blueprint`
- Branch: `main`
- Validation status:
  - `script/lean-low-priority ./generate-example-blueprints.sh`
- Resume commands/notes:
  - `git status --short`
  - `git log --oneline -1`

### `feat/harness-state-of-the-art-20260313`

- Status: `active`
- Summary: live auxiliary worktree on the extracted repo, currently based on the shared `main` head.
- Path: `/home/egallego/lean/verso-blueprint/.worktrees/harness-state-of-the-art-20260313`
- Branch: `feat/harness-state-of-the-art-20260313`
- Validation status:
  - no independent validation beyond the shared `main` head yet
- Resume commands/notes:
  - `cd /home/egallego/lean/verso-blueprint/.worktrees/harness-state-of-the-art-20260313`
  - `git status --short`

### `feat/blueprint-data-review-20260312`

- Status: `active` (reconstructed from a legacy snapshot onto the extracted package layout)
- Summary: revived review-oriented worktree carrying forward the legacy data/API audit context on top of the current extracted repo shape.
- Path: `/home/egallego/lean/verso-blueprint/.worktrees/blueprint-data-review-20260312`
- Branch: `feat/blueprint-data-review-20260312`
- Source snapshot:
  - `/home/egallego/lean/verso-blueprint-old/.worktrees/blueprint-data-review-20260312`
- Validation status:
  - no independent validation beyond the shared extracted-layout baseline yet
- Migration notes:
  - the live worktree was recreated from `main`, then overlaid with the surviving legacy snapshot content
  - the branch has been re-anchored onto the committed extracted-package baseline on `main`, so its current diff reflects the surviving legacy overlay rather than the package extraction itself
- Resume commands/notes:
  - `cd /home/egallego/lean/verso-blueprint/.worktrees/blueprint-data-review-20260312`
  - `git status --short`
  - compare with the archival snapshot if needed before committing new review notes

### `feat/lean-lean-interactive-latency-20260310`

- Status: `active` (reconstructed from a legacy snapshot onto the extracted package layout)
- Summary: revived latency-focused worktree for the Lean block interactive fast path and related documentation follow-up.
- Path: `/home/egallego/lean/verso-blueprint/.worktrees/lean-lean-interactive-latency-20260310`
- Branch: `feat/lean-lean-interactive-latency-20260310`
- Source snapshot:
  - `/home/egallego/lean/verso-blueprint-old/.worktrees/lean-lean-interactive-latency-20260310`
- Validation status:
  - no independent validation beyond the shared extracted-layout baseline yet
- Migration notes:
  - the live worktree was recreated from `main`, then overlaid with the surviving legacy snapshot content
  - the branch has been re-anchored onto the committed extracted-package baseline on `main`, so its current diff reflects the surviving legacy overlay rather than the package extraction itself
- Resume commands/notes:
  - `cd /home/egallego/lean/verso-blueprint/.worktrees/lean-lean-interactive-latency-20260310`
  - `git status --short`
  - review `src/VersoBlueprint/Lean.lean` and related docs first when resuming latency work

### `feat/lean-commandm-incremental-20260306`

- Status: `active` (fresh extracted-repo port branch seeded from the surviving legacy snapshot)
- Summary: reconstructed port branch for the incremental Lean fence / command snapshot line, now rebased conceptually onto the committed extracted-package baseline.
- Path: `/home/egallego/lean/verso-blueprint/.worktrees/lean-commandm-incremental-20260306`
- Branch: `feat/lean-commandm-incremental-20260306`
- Source preservation refs:
  - branch: `legacy/feat-lean-commandm-incremental-20260306`
  - snapshot: `/home/egallego/lean/verso-blueprint-old/.worktrees/lean-commandm-incremental-20260306`
- Validation status:
  - `script/lean-low-priority lake build VersoBlueprint.Lean VersoBlueprint.Informal.Code`
  - `script/lean-low-priority ./generate-example-blueprints.sh /home/egallego/lean/verso-blueprint/_out/lean-commandm-incremental-20260306/example-blueprints`
- Migration notes:
  - recreated from current `main`, then overlaid with blueprint-owned surfaces from the surviving legacy snapshot before being narrowed back down to the real fast-path port
  - current tracked diff is intentionally limited to `src/VersoBlueprint/Lean.lean`, `src/VersoBlueprint/Informal/Code.lean`, and `test-projects/Noperthedron/OPTIONS.md`
  - the current branch implements an opt-in `verso.blueprint.lean.fastPath` mode; the older inner command-snapshot reuse experiment has not been rebuilt yet against the extracted repo
- Resume commands/notes:
  - `cd /home/egallego/lean/verso-blueprint/.worktrees/lean-commandm-incremental-20260306`
  - `git status --short`
  - compare with `legacy/feat-lean-commandm-incremental-20260306` only when snapshot context is insufficient

## Legacy Migration Queue

These items originated in `/home/egallego/lean/verso-blueprint-old` before the package extraction.
They are tracked here so rebases and worktree reconstruction happen against the extracted layout,
not against the old monorepo bookkeeping.

### `legacy/feat-lean-commandm-incremental-20260306`

- Status: `preserved` (owner action: use the live extracted-repo port worktree for ongoing work)
- Summary: legacy incremental elaboration branch imported from the old repo as a preservation ref.
- Source branch: `/home/egallego/lean/verso-blueprint-old` `feat/lean-commandm-incremental-20260306`
- Local branch: `legacy/feat-lean-commandm-incremental-20260306`
- Tip commit:
  - `23e23818` `docs(dashboard): sync with root dashboard`
- Associated legacy snapshot:
  - `/home/egallego/lean/verso-blueprint-old/.worktrees/lean-commandm-incremental-20260306`
- Migration notes:
  - the imported branch still carries the old monorepo layout and old dashboard churn
  - do not fast-forward-merge it into `main`
  - live port work now happens in `feat/lean-commandm-incremental-20260306`
- Resume commands/notes:
  - `git log --oneline legacy/feat-lean-commandm-incremental-20260306 --`
  - `git diff --stat main...legacy/feat-lean-commandm-incremental-20260306`
  - inspect the legacy snapshot path if commit history is too noisy

## Notes

- The old dashboard at `/home/egallego/lean/verso-blueprint-old/WORKTREE_DASHBOARD.md` is now archival.
- The migrated snapshot directories `blueprint-data-review-20260312` and `lean-lean-interactive-latency-20260310` have been removed from `/home/egallego/lean/verso-blueprint-old/.worktrees/` after reconstruction here.
- The leftover archival scratch directory `tex-macro-import-20260305` has been removed from `/home/egallego/lean/verso-blueprint-old/.worktrees/`.
- The `lsp-folding-chain` line has been retired and removed from both the extracted repo and the archival old-tree snapshot set.
- The extracted package baseline is now tracked on `main`, and the reconstructed snapshot worktrees have been re-anchored onto that committed base.
- Feature and legacy worktree branches are local-only by default; do not push them to `origin` unless the user explicitly requests that publication step.
- The `verso.blueprint.lean.fastPath` option remains branch-local on `feat/lean-commandm-incremental-20260306` until that branch is reviewed and merged.
- Legacy branches were imported into this repo for preservation, the two surviving snapshot-only worktrees were reconstructed here, and a fresh extracted-repo port worktree now exists for the preserved `lean-commandm` line.
- When reviving legacy work, prefer fresh branches from `main` and targeted ports over direct rebases of the pre-extraction history.
