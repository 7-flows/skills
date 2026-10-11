#!/usr/bin/env bash
# Seeds the notes K left at an earlier sitting.
set -euo pipefail
f="$(dirname "$0")/../_fixtures"
mkdir -p 7flows-notes/pieces
cp "$f/profile.md" 7flows-notes/profile.md
cp "$f/toile-invoicing-closed.md" 7flows-notes/pieces/2026-10-01-toile-designer-invoicing.md
