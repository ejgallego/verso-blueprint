#!/usr/bin/env bash

set -euo pipefail

package_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$package_root"

exec ./scripts/validate-reference-blueprints.sh "$@"
