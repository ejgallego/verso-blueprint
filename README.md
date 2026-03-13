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
```
