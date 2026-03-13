# Worktree Dashboard

Last updated: 2026-03-13 (migrated from the old monorepo dashboard; this file is now the active dashboard, and the old repo has been reduced to archival-only reference material)

## Active Worktrees

### `bp` (root checkout)

- Status: `active`
- Summary: extracted `VersoBlueprint` package on Lean `v4.29.0-rc6`; split-path and toolchain repair work completed in-place.
- Path: `/home/egallego/lean/verso-blueprint`
- Branch: `bp`
- Validation status:
  - `script/lean-low-priority ./generate-example-blueprints.sh`
- Resume commands/notes:
  - `git status --short`
  - `git log --oneline -1`

### `feat/harness-state-of-the-art-20260313`

- Status: `active`
- Summary: live auxiliary worktree on the extracted repo, currently at the same commit as `bp`.
- Path: `/home/egallego/lean/verso-blueprint/.worktrees/harness-state-of-the-art-20260313`
- Branch: `feat/harness-state-of-the-art-20260313`
- Validation status:
  - no independent validation beyond the shared `bp` head yet
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
  - the live worktree was recreated from `bp`, then overlaid with the surviving legacy snapshot content
  - because the extracted-layout base is still an uncommitted working-tree migration, this worktree currently carries the same rename-heavy base delta as `bp`
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
  - the live worktree was recreated from `bp`, then overlaid with the surviving legacy snapshot content
  - because the extracted-layout base is still an uncommitted working-tree migration, this worktree currently carries the same rename-heavy base delta as `bp`
- Resume commands/notes:
  - `cd /home/egallego/lean/verso-blueprint/.worktrees/lean-lean-interactive-latency-20260310`
  - `git status --short`
  - review `src/VersoBlueprint/Lean.lean` and related docs first when resuming latency work

## Legacy Migration Queue

These items originated in `/home/egallego/lean/verso-blueprint-old` before the package extraction.
They are tracked here so rebases and worktree reconstruction happen against the extracted layout,
not against the old monorepo bookkeeping.

### `legacy/feat-lean-commandm-incremental-20260306`

- Status: `imported` (owner action: reconstruct as extracted-package work and port/rebase selectively)
- Summary: legacy incremental elaboration branch imported from the old repo as a preservation ref.
- Source branch: `/home/egallego/lean/verso-blueprint-old` `feat/lean-commandm-incremental-20260306`
- Local branch: `legacy/feat-lean-commandm-incremental-20260306`
- Tip commit:
  - `23e23818` `docs(dashboard): sync with root dashboard`
- Associated legacy snapshot:
  - `/home/egallego/lean/verso-blueprint-old/.worktrees/lean-commandm-incremental-20260306`
- Migration notes:
  - the imported branch still carries the old monorepo layout and old dashboard churn
  - do not fast-forward-merge it into `bp`
  - port the substantive `VersoBlueprint` changes onto a fresh extracted-repo branch instead
- Resume commands/notes:
  - `git log --oneline legacy/feat-lean-commandm-incremental-20260306 --`
  - `git diff --stat bp...legacy/feat-lean-commandm-incremental-20260306`
  - inspect the legacy snapshot path if commit history is too noisy

### `legacy/feat-lsp-folding-chain`

- Status: `imported` (owner action: reconstruct as extracted-package work and port/rebase selectively)
- Summary: long-running folding-chain branch imported from the old repo as a preservation ref.
- Source branch: `/home/egallego/lean/verso-blueprint-old` `feat/lsp-folding-chain`
- Local branch: `legacy/feat-lsp-folding-chain`
- Tip commit:
  - `4cafd289` `verso: cleanup folding metadata plumbing and dedupe helpers`
- Associated legacy snapshot:
  - `/home/egallego/lean/verso-blueprint-old/.worktrees/lsp-folding-chain`
- Migration notes:
  - the branch predates the extraction and still touches wide monorepo surfaces
  - expect a manual port/rebase over the extracted layout, not a trivial `git rebase bp`
- Resume commands/notes:
  - `git log --oneline legacy/feat-lsp-folding-chain --`
  - `git diff --stat bp...legacy/feat-lsp-folding-chain`
  - prioritize blueprint-owned files under `src/VersoBlueprint`, `test-projects/Noperthedron`, and `tests`

## Notes

- The old dashboard at `/home/egallego/lean/verso-blueprint-old/WORKTREE_DASHBOARD.md` is now archival.
- The migrated snapshot directories `blueprint-data-review-20260312` and `lean-lean-interactive-latency-20260310` have been removed from `/home/egallego/lean/verso-blueprint-old/.worktrees/` after reconstruction here.
- Legacy branches were imported into this repo for preservation, and the two surviving snapshot-only worktrees have now been reconstructed here as live extracted-repo worktrees.
- When reviving legacy work, prefer fresh branches from `bp` and targeted ports over direct rebases of the pre-extraction history.
