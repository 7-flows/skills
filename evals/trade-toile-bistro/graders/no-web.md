---
type: regex
target: last_message
# A founder off the web gets their own trade back, not a software playbook (C26).
pattern: '\b(landing page|sign-?up (form|page)|website visitors?|visitors? (to|on) the (site|page)|website|online ads?|targeted ads|ad budget|support tickets?|pricing tiers?)\b'
flags: i
match: not_contains
---
