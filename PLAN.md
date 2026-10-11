# Plan — 7 Flows Skills

Adapts at every batch boundary. The spec never moves.
Goal: slice 1 — a founder installs 7 Flows and runs the Test flow with K on
Claude Code, claude.ai and Pi (C1–C24).
Architecture: the method is written once under `method/` (CC BY-SA); a build
step copies each skill's share into `skills/<name>/references/` and
`scripts/`, so every skill folder stands alone (claude.ai copies only the
skill's own folder). The repo is both the marketplace and the one plugin,
`7flows`. Evals run locally at release; CI runs the free gates.
Constraints: skill frontmatter = the six spec fields, description ≤ 200
chars · plugin name `7flows`, skills `7flows` (K) and `7flows-test` ·
no top-level `bin/`, no hooks or agents · close-call rule = Wilson 90%.

Files:
- method/voice.md — K's voice rules and the banned-word list
- method/k.md — who K is, how K works a sitting, the intake
- method/notes.md — the notes folder: profile, piece records, open/closed
- method/flows.md — the seven flows and which are released
- method/test/toile.md — the Toile: ten fields, rules, quick Toile
- method/test/swatch.md — the Swatch: seven fields, rules
- method/test/close-calls.md — reading a result against the pass line
- skills/7flows/SKILL.md — K: intake, routing, notes (hand-written)
- skills/7flows-test/SKILL.md — Test flow: pick and run a piece (hand-written)
- skills/*/references/, skills/*/scripts/, skills/*/LICENSE* — generated, committed
- src/sevenflows/build.py — method/ → skills/ copy; `--check` fails on drift
- src/sevenflows/lint.py — frontmatter rules and banned words
- src/sevenflows/close_call.py — Wilson 90% verdict (stdlib, PEP 723)
- src/sevenflows/package.py — one ZIP per skill into dist/
- src/sevenflows/cli.py — `sevenflows build|lint|package` entry point
- .claude-plugin/plugin.json, .claude-plugin/marketplace.json
- evals/<case>/prompt.md, case.yaml, graders/*.md — behaviour cases
- LICENSE (Apache-2.0), LICENSE-METHOD (CC BY-SA 4.0), README.md, CHANGELOG.md
- .github/workflows/ci.yml — free gates on push

## State
2026-10-11 — batch 1 reviewed and closed (1.1–1.3; C5, C7 ticked).
Owner: Hybrid chosen (ADR); batch 2 approved, starting at 2.0.
- Learned: a plugin skill's Read of its own references/ is refused under
  `claude -p` (prompted interactively); `allowed-tools: Read` makes the
  Skill call itself need approval — dead end (ADR). Evals grant Read, so
  they can't see this. Owner chose Hybrid (ADR) — task 2.0.
- Review: fixed CLI exit-code tests, lint YAML/missing-file findings, build
  basename clash + orphan sweep, UTF-8, Toile example vs C17. Not
  reproduced: description over-firing on a code belief (3/3 silent; kept
  as eval silent-bug-belief). Rejected: 1.2 "not met" — its done-line was
  met; C1 is the unticked one.
- Gate hygiene: never pipe a gate through tail without pipefail — a red
  ruff hid behind exit 0 once (amended before push).
- Spend so far on evals: ~$1.80.

## Batch 1 — walking skeleton: the Toile fires
- [x] 1.1 Toile source, build and lint (C14). Doc: agentskills.io/specification
      (frontmatter, layout); docs.astral.sh/uv (project scripts).
      Files: create method/test/toile.md, skills/7flows-test/SKILL.md,
      src/sevenflows/{build,lint,cli}.py, tests/test_build.py,
      tests/test_lint.py; modify pyproject.toml (script `sevenflows`,
      dev dep skills-ref).
      Interfaces: produces `sevenflows build [--check]` (exit 1 on drift),
      `sevenflows lint` (exit 1 on any finding); build manifest maps
      method files → skill folders.
      Done: `uv run sevenflows build --check` exit 0; `uv run agentskills
      validate skills/7flows-test` prints "Valid skill"; a test proves a
      seventh frontmatter key and a 201-char description both fail lint.
- [x] 1.2 Plugin and marketplace from one repo (C5, C1). Doc:
      code.claude.com/docs/en/plugins-reference, /plugins/marketplace-reference,
      /plugins/cli-reference#plugin-validate.
      Files: create .claude-plugin/plugin.json, .claude-plugin/marketplace.json;
      modify AGENTS.md Gates.
      Interfaces: consumes skills/ from 1.1; plugin and marketplace both
      named `7flows`, source `./`.
      Done: `claude plugin validate . --strict` exit 0; after pushing,
      `claude plugin marketplace add 7-flows/skills` and `claude plugin
      install 7flows@7flows`, `claude -p "I think freelance designers would pay $49
      a month for invoicing"` opens a Toile at the Assumption field.
- [x] 1.3 First evals (C7; seeds C6 row 1). Doc: code.claude.com/docs/en/plugin-evals.
      Files: create evals/toile-from-belief/{prompt.md,graders/fired.md},
      evals/silent-{poem,typeerror,pdf,peru}/{prompt.md,graders/silent.md}.
      Interfaces: grader `tool_used: Skill` matching `7flows-test`; silent
      cases use `min: 0, max: 0, arm: both`.
      Done: `claude plugin eval . --runs 3 --trust-plugin` exit 0.

## Batch 2 — K and the full Toile
- [ ] 2.0 Hybrid build: essentials inline (C1). Doc: ADR 2026-10-11 Hybrid;
      code.claude.com/docs/en/skills (SKILL.md content).
      Files: modify src/sevenflows/build.py, method/test/toile.md (core
      markers), skills/7flows-test/SKILL.md (generated region),
      tests/test_build.py.
      Interfaces: produces `<!-- core -->…<!-- /core -->` in method files and
      `<!-- built from method/… — edit there -->` regions in SKILL.md; 2.1+
      consume both.
      Done: `build --check` fails on a hand-edited inline region; installed
      fresh from GitHub, `claude -p "I think freelance designers would pay
      $49 a month for invoicing"` names all ten fields' order without any
      Read being refused (stream-json shows no permission_denials) → tick C1.
- [ ] 2.1 K: intake, voice, language (C9, C12, C13). Doc:
      code.claude.com/docs/en/skills (bundled files); pi.dev/docs/latest/skills.
      Files: create method/{k,voice,notes,flows}.md, skills/7flows/SKILL.md;
      modify src/sevenflows/build.py (manifest), src/sevenflows/lint.py
      (banned words read from method/voice.md);
      create evals/intake-{fresh,skip,french}/, evals/voice-no-flattery/.
      Interfaces: produces notes layout `7flows-notes/profile.md`,
      `7flows-notes/pieces/<YYYY-MM-DD>-<piece>-<slug>.md` with frontmatter
      `piece`, `status: open|closed`, `opened`, `closed`; consumed by 2.3.
      Done: `uv run sevenflows lint` exit 0 over skills/ and method/; evals
      intake-fresh (`file_exists: 7flows-notes/profile.md`), intake-skip,
      intake-french (French reply, English field names) pass with
      `claude plugin eval . --tag k`.
- [ ] 2.2 The Toile at full cut (C10, C11, C15, C18, C20). Doc: method source
      core-x.md §Flow 1 (history); plugin-evals (llm graders).
      Files: modify method/test/toile.md, skills/7flows-test/SKILL.md;
      create evals/toile-{vague,pass-line-lock,close-needs-decision,quick}/.
      Interfaces: consumes notes layout from 2.1.
      Done: `claude plugin eval . --tag toile` exit 0; pass-line-lock case
      shows the refusal and the attempt under Learnings.
- [ ] 2.3 Two sittings and records (C16, C19). Doc: plugin-evals
      (case.yaml `context`, seeded workspace, `file_exists`).
      Files: modify method/notes.md, method/test/toile.md;
      create evals/toile-{resume,two-open,record-saved}/ with seeded
      7flows-notes/ fixtures.
      Interfaces: consumes notes layout from 2.1.
      Done: `claude plugin eval . --tag sittings` exit 0; record-saved case
      finds a dated record with `status: closed`.

## Batch 3 — close calls, the Swatch, honest routing
- [ ] 3.1 Close-call verdict (C17). Doc: NIST e-Handbook §7.2.4.1 (Wilson),
      §7.2.4.2 (sample size). Files: src/sevenflows/close_call.py,
      method/test/close-calls.md, tests/test_close_call.py, evals/toile-close-call/.
      Done: pytest shows 9/200, 10/200, 0/30 vs 5% → too close; 25/200 →
      pass; 2/200 → miss; eval toile-close-call passes.
- [ ] 3.2 The Swatch (C21; seeds C6 row 2). Doc: core-x.md §Flow 2
      (history); plugin-evals. Files: method/test/swatch.md,
      skills/7flows-test/SKILL.md, evals/swatch-{fires,anecdote,opens-toile}/.
      Done: `claude plugin eval . --tag swatch` exit 0.
- [ ] 3.3 Routing (C6, C8). Doc: plugin-evals; code.claude.com/docs/en/skills
      (descriptions and triggering). Files: skills/7flows/SKILL.md,
      method/flows.md, evals/route-{idea,k,sell-unreleased}/.
      Done: `claude plugin eval . --tag route` exit 0, and every C6 row's
      case (seeded in 1.3, 3.2) passes in the same run.

## Batch 4 — distribution and release
- [ ] 4.1 Licences and ZIPs (C23). Doc: claude.com/docs/skills/how-to
      (ZIP layout); spdx.org/licenses. Files: LICENSE, LICENSE-METHOD,
      src/sevenflows/package.py, tests/test_package.py.
      Done: each dist/<skill>.zip has `<skill>/SKILL.md` at its top level
      plus both licence texts.
- [ ] 4.2 Install page and Pi (C4). Doc: pi.dev/docs/latest/packages.
      Files: README.md. Done: in a fresh project, the README's Pi steps
      followed verbatim make `pi -p "K, let's work"` answer as K.
- [ ] 4.3 Release gate (C22, C24). Doc: plugin-evals (exit codes,
      --threshold); keepachangelog.com; cli.github.com/manual/gh_release_create.
      Files: CHANGELOG.md,
      .github/workflows/ci.yml, src/sevenflows/release.py.
      Done: release refuses to tag on a failing eval; on green it tags
      vX.Y.Z and attaches one ZIP per skill.
- [ ] 4.4 claude.ai acceptance (C2, C3). Doc: support.claude.com articles
      13837440 (plugins) and 12512198 (custom skills). Done: transcripts of a paid-plan
      marketplace install and a ZIP upload, each opening a Toile, saved
      under evidence/.

## Gaps
- 2.1: lint should enforce SKILL.md < 500 lines (AGENTS.md rule; review M7).
- 2.1: K's description is broad — rerun `--tag silent` in 2.1's Done line
  (review M6), not only at release.
- C1 not ticked: installed from GitHub, the Toile opens at Assumption, but
  the skill can't read `references/toile.md` without a permission grant
  (ADR 2026-10-11 "Open: a plugin skill can't read…") — "no other setup"
  isn't yet true. Decide at the batch 1 re-plan.
- 4.2: `claude plugin validate` advises a README install line
  (`/plugin install 7flows --marketplace 7-flows/skills`).
- C14 not ticked: the method text and its field-order test are in (1.1),
  but a *saved record* with the ten fields lands in 2.3 — tick C14 there.
- claude.ai acceptance (C2, C3) has no automated gate — manual evidence only.
- Unverified until 4.2/4.4: private-repo marketplaces on claude.ai; `pi
  install` from a git repo without package.json; claude.ai frontmatter
  strictness beyond the six fields.
