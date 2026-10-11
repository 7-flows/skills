<!-- Copied from method/notes.md by `sevenflows build`. Edit there. -->

# The notes

K keeps the work in plain text, in a folder the founder owns. Any agent,
and any person, can read it; nothing lives only in one chat. The next
sitting starts by reading it.

<!-- core -->
## The notes folder

```
7flows-notes/
  profile.md
  pieces/
    2026-10-11-toile-designer-invoicing.md
```

- One folder, `7flows-notes/`, at the root of the project.
- `profile.md` holds the business, from the intake.
- `pieces/` holds one file per piece of work, named
  `<YYYY-MM-DD>-<piece>-<slug>.md`: the date it opened, the piece in
  lowercase, and a few words of the belief.

## profile.md

```markdown
# Profile

- **Makes:** <one sentence>
- **For:** <the person it is for>
- **Money:** <how money comes in>
- **Workforce:** <people, where they sit, agents>
- **Least sure of:** <the belief>

Updated: <YYYY-MM-DD>
```

## A piece record

```markdown
---
piece: toile
status: open
opened: 2026-10-11
closed:
---

# Toile — <the belief, in a few words>

## Assumption
<the founder's words>
```

`status` is `open` until the piece's last field is filled, then `closed`,
with the date in `closed`. Field names stay in English; the words under
them are the founder's.
<!-- /core -->
