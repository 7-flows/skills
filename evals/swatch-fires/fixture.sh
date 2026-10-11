#!/usr/bin/env bash
# Seeds a business with three price tiers, met at an earlier sitting.
set -euo pipefail
f="$(dirname "$0")/../_fixtures"
mkdir -p 7flows-notes/pieces
cp "$f/profile-tiers.md" 7flows-notes/profile.md
