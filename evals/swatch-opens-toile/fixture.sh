#!/usr/bin/env bash
# Seeds a Swatch cut up to "So what" at an earlier sitting.
set -euo pipefail
f="$(dirname "$0")/../_fixtures"
mkdir -p 7flows-notes/pieces
cp "$f/profile-tiers.md" 7flows-notes/profile.md
cp "$f/swatch-tiers-sowhat.md" 7flows-notes/pieces/2026-10-05-swatch-tier-confusion.md
