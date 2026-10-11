#!/usr/bin/env bash
# Seeds a bakery's Toile cut up to its Test design: 10 regulars asked.
set -euo pipefail
f="$(dirname "$0")/../_fixtures"
mkdir -p 7flows-notes/pieces
cp "$f/toile-bakery-design.md" 7flows-notes/pieces/2026-10-02-toile-sourdough-preorder.md
