#!/usr/bin/env bash

set -euo pipefail

package_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$package_root"

if [ "${1:-}" = "--help" ]; then
  cat <<'EOF'
usage: ./scripts/validate-test-blueprints.sh [pytest args...]

Generate the in-repo test blueprint outputs under `_out/test-blueprints/`,
run the local code-panel regression check, and run the browser regression suite
against `preview_runtime_showcase`.

Any extra arguments are forwarded to pytest.
EOF
  exit 0
fi

./scripts/generate-test-blueprints.sh

site_dir="$(python3 - <<'PY'
from pathlib import Path
from scripts.blueprint_harness_paths import default_test_blueprint_site_dir

print(default_test_blueprint_site_dir("preview_runtime_showcase", Path.cwd()))
PY
)"

python3 tests/harness/preview_runtime_showcase/check_blueprint_code_panels.py --site-dir "$site_dir"

if command -v uv >/dev/null 2>&1; then
  env UV_CACHE_DIR=/tmp/verso-blueprint-uv-cache \
    uv run --project tests/browser --extra test python -m pytest \
      tests/browser -q --browser chromium --site-dir "$site_dir" "$@"
else
  python3 -m pytest tests/browser -q --browser chromium --site-dir "$site_dir" "$@"
fi
