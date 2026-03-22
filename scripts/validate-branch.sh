#!/usr/bin/env bash

set -euo pipefail

package_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$package_root"

if [ "${1:-}" = "--help" ]; then
  cat <<'EOF'
usage: ./scripts/validate-branch.sh [pytest args...]

Run the full branch-validation workflow:

- Lean tests
- Python harness/unit tests
- reference blueprint generation under `_out/reference-blueprints/`
- test blueprint generation under `_out/test-blueprints/`
- local code-panel regression and browser suite against `preview_runtime_showcase`

Any extra arguments are forwarded to the final pytest invocation.
EOF
  exit 0
fi

./scripts/lean-low-priority lake test

python3 -m unittest \
  tests.harness.test_blueprint_test_blueprints \
  tests.harness.test_blueprint_harness_projects \
  tests.harness.test_blueprint_harness_cli \
  tests.harness.test_blueprint_harness_worktrees \
  tests.harness.test_harness_entrypoints

./scripts/generate-reference-blueprints.sh
./scripts/validate-test-blueprints.sh "$@"
