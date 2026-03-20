#!/usr/bin/env bash

set -euo pipefail

package_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$package_root"

output_root="$(python3 - <<'PY'
from pathlib import Path
from scripts.blueprint_harness_paths import detect_harness_layout

layout = detect_harness_layout(Path.cwd())
print(layout.test_blueprint_output_root)
PY
)"

if [ "$#" -eq 0 ]; then
  mapfile -t docs < <(./scripts/lean-low-priority lake exe blueprint-test-docs --list)
else
  docs=("$@")
fi

for doc in "${docs[@]}"; do
  ./scripts/lean-low-priority lake exe blueprint-test-docs "$doc" --output "$output_root/$doc"
done
