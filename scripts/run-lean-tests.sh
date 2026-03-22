#!/usr/bin/env bash

set -euo pipefail

package_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$package_root"

./scripts/lean-low-priority lake build verso-blueprint-tests
./scripts/lean-low-priority ./.lake/build/bin/verso-blueprint-tests
