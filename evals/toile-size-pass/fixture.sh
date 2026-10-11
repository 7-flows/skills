#!/usr/bin/env bash
# Seeds a Toile cut up to its Test design: 200 visitors, no Pass line yet.
set -euo pipefail
f="$(dirname "$0")/../_fixtures"
mkdir -p 7flows-notes/pieces
cp "$f/toile-invoicing-design.md" 7flows-notes/pieces/2026-10-01-toile-designer-invoicing.md
