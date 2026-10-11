#!/usr/bin/env bash
# Seeds the bistro's lunch-set Toile, cut to Evidence so far: Test design is next.
set -euo pipefail
f="$(dirname "$0")/../_fixtures"
mkdir -p 7flows-notes/pieces
cp "$f/profile-bistro.md" 7flows-notes/profile.md
cp "$f/toile-bistro-evidence.md" 7flows-notes/pieces/2026-10-01-toile-lunch-set.md
