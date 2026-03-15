# Verso Blueprint

This folder contains the extracted blueprint-specific package while the split
from the parent Verso checkout is in progress.

The package lives here:

- `src/VersoBlueprint`
- `test-projects/Noperthedron`
- `test-projects/Sphere-Packing-Lean`
- `tests`

During this transition, the package depends on `verso` via the Git dependency
declared in `lakefile.lean`:

```bash
require verso from git "https://github.com/leanprover/verso"@"main"
```

Useful commands:

```bash
lake build
lake test
./generate-example-blueprints.sh
./validate-example-blueprints.sh
./validate-example-blueprints.sh --run-lean-tests
python3 -m script.blueprint_harness sync-root-lake
python3 -m script.blueprint_harness paths
```

The public local harness surface is intentionally small:

- `./generate-example-blueprints.sh`
- `./validate-example-blueprints.sh`
- `./validate-example-blueprints.sh --run-lean-tests`
- `python3 -m script.blueprint_harness sync-root-lake`
- `python3 -m script.blueprint_harness paths`

In linked worktrees under `.worktrees/<name>`, the harness writes artifacts to
the shared repository-root preview area `_out/<name>/example-blueprints`. By
default, linked worktrees sync `.lake/` from the root checkout and reuse the
root-built executables instead of rebuilding dependencies locally. Pass
`--allow-local-build` only when you intentionally want the linked worktree to
run `lake build` or `lake test` itself.

`./validate-example-blueprints.sh` intentionally skips Lean tests by default and
focuses on generation plus static/browser regression checks. Use
`--run-lean-tests` when you explicitly want `lake test` included in the run.
