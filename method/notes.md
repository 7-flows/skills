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

- **Makes:** <what you make or offer, one sentence>
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

Every field heading of the piece appears, in the piece's order; a heading
stays empty until its field is cut. `status` is `open` until the piece
closes, then `closed`, with the date in `closed`. Field names stay in
English in every language; the words under them are the founder's.

## Reading the notes

- Open pieces are work in progress: pick one up at its first empty field.
- Closed pieces are what the business has learned. Recall the latest
  Decision and Next action in one line, and never cut a Toile on a belief
  already tested without saying so.

## No folder to write to

When there is no project folder to save into (a claude.ai chat), hand the
record over as a file, named as above, at the end of every sitting. A
record the founder attaches at the start of a chat is read like the notes
folder: the piece resumes at its first empty field.
<!-- /core -->
