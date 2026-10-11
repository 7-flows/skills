#!/usr/bin/env bash
# Seeds the clinic's profile from an earlier intake.
set -euo pipefail
f="$(dirname "$0")/../_fixtures"
mkdir -p 7flows-notes/pieces
cp "$f/profile-clinic.md" 7flows-notes/profile.md
