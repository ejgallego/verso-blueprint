# Contributing

This repository uses a two-layer coordination model:

- GitHub issues and pull requests are the shared, durable record.
- `.worktrees/` metadata is the local, untracked coordination layer for
  parallel work.

## Branch Conventions

- Use `feat/<slug>` for user-facing or architectural changes.
- Use `fix/<slug>` for bug fixes.
- Use `docs/<slug>` for documentation-only work.
- Use `chore/<slug>` for maintenance and cleanup.
- Use `wip/<slug>` only for local-only exploratory branches that are not ready
  for review.

Prefer including the issue number or stable task slug when one exists.

## Commit Conventions

Prefer concise imperative subjects in the form:

```text
type(scope): summary
```

Examples:

- `feat(harness): add local worktree registry commands`
- `fix(preview): preserve inline proof-gap precision`
- `docs(maintainer): document worktree claim workflow`

Keep the subject line tight enough for `git log --oneline`. Avoid generic
subjects such as `Update files` or `misc cleanup`.

## Pull Request Conventions

- PR titles should usually match the intended squash-merge commit title.
- PR bodies should state:
  - the problem
  - the scope of the change
  - validation performed
  - notable risks or follow-up
- When the work came from a local worktree, include the worktree name and write
  scope in the PR body or draft notes.

See the repository PR template for the preferred structure.

## Local Worktree Coordination

For local maintainer automation, keep the CLI split in mind:

- use `python3 -m scripts.blueprint_harness ...` for worktree management,
  branch landing, and local coordination metadata
- use `python3 -m scripts.blueprint_reference_harness ...` for reference
  project generation, validation, cache sync, and editable reference clones

Use the harness commands to manage local coordination metadata:

```bash
python3 -m scripts.blueprint_harness worktree-sync
python3 -m scripts.blueprint_harness worktree-list
python3 -m scripts.blueprint_harness worktree-claim --owner <name> --summary <text> --scope <path>
python3 -m scripts.blueprint_harness worktree-status
python3 -m scripts.blueprint_harness worktree-release
```

By default, only clean up worktrees or branches created or landed by the
current session. Do not retire or delete unrelated local worktrees unless the
owner or the user explicitly asks for that cleanup.

Local metadata lives under ignored `.worktrees/` paths:

- `.worktrees/registry.json`
- `.worktrees/_meta/_root.json`
- `.worktrees/_meta/<name>.json`

That data is intentionally not tracked in Git.
