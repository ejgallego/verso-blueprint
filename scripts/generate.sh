#!/usr/bin/env bash

set -euo pipefail

package_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$package_root"

exec ./scripts/generate-reference-blueprints.sh "$@"
