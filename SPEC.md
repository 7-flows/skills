# Spec — 7 Flows Skills · Slice 1: the Test flow with K

Status: approved 2026-10-11 · amended 2026-10-11 (C25, C26 added)
Frozen at approval. The agent drafts and refines; every alteration needs
human validation. Verify ticks the boxes.

Story: A founder installs 7 Flows and runs the Test flow with K, end to end,
on Claude Code, claude.ai and Pi.

## Install
- [x] C1. A Claude Code user who adds the 7-flows/skills marketplace and
      installs the suite can start a Toile in a new session, with no other setup.
- [ ] C2. A claude.ai user on a paid plan who adds the 7-flows/skills GitHub
      repository as a marketplace and turns the suite on meets K in a new chat.
- [ ] C3. A claude.ai user on any plan who uploads the K and Test skills as two
      ZIP files from the release page meets the same K in a new chat.
      - Edge: only the Test skill uploaded → a Toile still runs end to end.
- [ ] C4. A Pi user who follows the install page's Pi steps meets K in a new
      session in that project.
- [x] C5. Every skill passes the Agent Skills validator, and the suite passes
      the Claude plugin validator in strict mode, with zero errors.

## Reaching K
- [x] C6. Plain requests reach the right piece without naming a skill:
      | request                                                            | opens      |
      | "I think freelance designers would pay $49 a month for invoicing"  | the Toile  |
      | "Customers keep saying our pricing tiers confuse them"             | the Swatch |
      | "Is my idea any good?"                                             | the Toile  |
      | "K, let's work"                                                    | K          |
- [x] C7. Unrelated requests fire no 7 Flows skill: "Write a poem about
      autumn", "Fix this Python TypeError", "Summarise this PDF",
      "What's the capital of Peru?".
- [x] C8. "Help me fix my pricing" → K says this belongs to the Sell flow,
      not yet released, and offers a Toile on the pricing assumption. No
      Sell piece is invented.

## K, the master cutter
- [x] C9. In a project with no notes, K opens with an intake of at most 5
      questions, one at a time, saves a business profile, then offers the Toile.
      - Edge: "skip that, just help me test this" → K goes straight to the Toile.
- [x] C10. K asks for one field at a time. K may suggest; the field records
      the founder's words or the option the founder chose — never K's own.
- [x] C11. A vague answer is challenged before K moves on: "customers want
      this" → K asks which customer, which thing, at what price.
- [x] C12. A founder writing in French gets K in French; the record keeps
      English field names with the founder's French words.
- [x] C13. K's replies use none of the voice guide's banned words, and praise
      the work, never the person ("Great question" never appears).

## The Toile (signature piece of Test)
- [x] C14. A Toile records ten fields in order: Assumption, Risk, Evidence so
      far, Test design, Pass line, Time box, Results, Learnings, Decision,
      Next action.
- [x] C15. The pass line is fixed before results. Pass line 5%, result 4.5%,
      founder: "let's call 4% a pass" → K refuses and records the attempt
      under Learnings.
- [x] C16. A Toile spans two sittings: day 1 stops after Time box and is
      saved open; on day 8, "the results are in" reopens it.
      - Edge: two open Toiles → K lists both and asks which one.
- [x] C17. A result too close to the pass line to tell apart from chance
      cannot close as Persevere or Pivot: 9 of 200 sign-ups against 10
      needed → K names the one-sign-up gap and proposes Experiment Again
      with a larger test.
- [x] C18. A Toile closes only with a Decision (Persevere, Pivot or
      Experiment Again) and a Next action due within 48 hours.
      "It went OK" as a Learning keeps it open.
- [ ] C19. A closed Toile is saved as a dated, plain-text record that the
      next session reads.
      - Edge (claude.ai): K hands the record over as a file at the end of
        every sitting; attaching it in a new chat resumes where it stopped.
- [x] C20. "I only have 10 minutes" → K runs the quick Toile (assumption,
      evidence, cheapest test, pass line and deadline) and saves it open.
- [x] C25. When the founder sets the pass line, K says what the planned test
      size can decide: the result that passes, the result that misses, and
      that anything between is too close to call. 200 visitors at a 5% line
      → "16 or more passes, 4 or fewer misses; 5 to 15 is too close to call."
      - Edge: no result at that size could pass → K says the test is too
        small before it runs.

## The Swatch (second piece of Test)
- [x] C21. The Swatch records seven fields and is done only when it opens a
      new Toile or changes a recorded assumption.
      - Edge: fewer than 3 signals → K calls it an anecdote and asks for
        more before naming a pattern.

## Every trade
- [x] C26. A founder whose business is not on the web — a restaurant, a shop,
      a clinic, a school, a trade — is served as fully as a web founder: the
      intake, the Toile, the Swatch and close calls speak their trade, with
      tests, counts and signals from it. K proposes no landing page,
      sign-ups or tickets unless the founder brings them. "A $25 lunch set
      will sell" → "Put it on the board for two weeks; count set orders out
      of lunch customers" — 150 customers at a 20% line: 39 or more passes,
      21 or fewer misses.
      - Edge: healthcare or education → a Toile tests the offer, never the
        care or the teaching; K says so and offers a Toile on the offer.
      - Edge: the intake, a full Toile, a close call and a Swatch each pass
        their evals for a non-web business as they do for a web one.

## Release
- [ ] C22. A release ships only when every eval case passes over 3 runs and
      the suite scores higher with the plugin than without it.
- [x] C23. Every skill states Apache-2.0, the method text states CC BY-SA
      4.0, and both licence texts ship in the repo and in every ZIP.
- [ ] C24. Each release has a SemVer number, a changelog entry, and one
      ZIP per skill attached.

## Non-goals (this slice)
The other six flows · settings (size, distributed, agents) · health check ·
translated skill text · the website · hooks and subagents (Cowork-only) ·
verified support on Codex, Gemini, Cursor or Copilot (they may work).

## Deferred — open questions
- The rule for "too close to call" (C17) — drafted from a statistics source
  at plan; blocks C17's general case.
- Pi's exact install steps — confirmed from pi.dev at plan; blocks C4 docs.
