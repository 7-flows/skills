#!/usr/bin/env bash
# Seeds a business K met at an earlier sitting, so no intake runs.
set -euo pipefail
f="$(dirname "$0")/../_fixtures"
mkdir -p 7flows-notes/pieces
cp "$f/profile.md" 7flows-notes/profile.md
