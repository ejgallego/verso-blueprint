#!/usr/bin/env bash

set -euo pipefail

package_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$package_root"

if [ "${1:-}" = "--help" ]; then
  cat <<'EOF'
usage: ./scripts/validate-test-blueprints.sh [pytest args...]

Generate the in-repo test blueprint outputs under `_out/test-blueprints/`,
then run any configured standalone panel and browser regression checks.

Any extra arguments are forwarded to pytest.
EOF
  exit 0
fi

./scripts/generate-test-blueprints.sh

pytest_args=("$@")

python3 - <<'PY' "$package_root" "${pytest_args[@]}"
import shutil
import subprocess
import sys
from pathlib import Path

from scripts.blueprint_harness_paths import default_test_blueprint_site_dir
from scripts.blueprint_test_blueprints import default_test_blueprint_manifest, load_test_blueprints_manifest

package_root = Path(sys.argv[1])
pytest_args = sys.argv[2:]
fixtures = load_test_blueprints_manifest(default_test_blueprint_manifest(package_root))

for fixture in fixtures:
    site_dir = default_test_blueprint_site_dir(fixture.slug, package_root)
    if fixture.panel_regression_script:
        command = [
            sys.executable,
            str(package_root / fixture.panel_regression_script),
            "--site-dir",
            str(site_dir),
        ]
        subprocess.run(command, cwd=package_root, check=True)
    if fixture.browser_tests_path:
        tests_path = package_root / fixture.browser_tests_path
        use_uv = shutil.which("uv") is not None
        if use_uv:
            command = [
                "env",
                "UV_CACHE_DIR=/tmp/verso-blueprint-uv-cache",
                "uv",
                "run",
                "--project",
                str(tests_path),
                "--extra",
                "test",
                "python",
                "-m",
                "pytest",
            ]
        else:
            command = [sys.executable, "-m", "pytest"]
        command += [
            str(tests_path),
            "-q",
            "--browser",
            "chromium",
            "--site-dir",
            str(site_dir),
            *pytest_args,
        ]
        subprocess.run(command, cwd=package_root, check=True)
PY
