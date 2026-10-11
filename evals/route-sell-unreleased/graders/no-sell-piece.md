---
type: regex
target: files
# The piece sits right after the date in a record's name.
pattern: '7flows-notes/pieces/\d{4}-\d{2}-\d{2}-(fitting|sell)'
match: not_contains
---
