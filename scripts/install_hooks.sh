#!/usr/bin/env bash
# One-time setup: point git at the tracked hooks in .githooks/.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
echo "Git hooks installed (core.hooksPath=.githooks)."
