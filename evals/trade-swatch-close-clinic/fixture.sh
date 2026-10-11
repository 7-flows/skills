#!/usr/bin/env bash
# Seeds the clinic's Swatch, cut to "So what": fields 6 and 7 are left.
set -euo pipefail
f="$(dirname "$0")/../_fixtures"
mkdir -p 7flows-notes/pieces
cp "$f/profile-clinic.md" 7flows-notes/profile.md
cp "$f/swatch-clinic-sowhat.md" 7flows-notes/pieces/2026-10-05-swatch-early-hours.md
