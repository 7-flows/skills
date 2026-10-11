# Decisions — 7 Flows Skills

Read before re-litigating anything. Newest first.

## 2026-10-11 — Hybrid: essentials inline, long text in references/
Context: the open entry below; owner chose Hybrid at the batch 1 boundary.
Decision: each method file marks its essentials (field names, order,
rules) between `<!-- core -->` and `<!-- /core -->`. The build writes those
regions into the skill's SKILL.md between generated markers, under the
hand-written head, and still copies the whole file to references/. A skill
runs from SKILL.md alone; references/ is depth, read when allowed. `method/`
stays the single source; `build --check` covers both outputs.
Rejected: inline everything (SKILL.md swells as flows land; loses
progressive disclosure); references only (headless runs work blind; C1's
"no other setup" fails on Claude Code).

## 2026-10-11 — Resolved (Hybrid, above): a plugin skill can't read its own references headless
Context: task 1.2 done-line. Installed from GitHub, `claude -p` fired
`7flows:7flows-test` and opened the Toile at Assumption, but the Read of
`references/toile.md` in the plugin cache was refused ("you haven't granted
it yet") — headless runs have no one to answer the prompt; interactive users
would be asked. K carried on without the field list.
Dead end: `allowed-tools: Read` in the skill frontmatter — under `-p` the
Skill call itself was then refused (a skill that grants tools needs approval
to run). Scoped `Read(${CLAUDE_SKILL_DIR}/**)` isn't an option: Claude Code
substitutes that variable only in Bash rules (code.claude.com/docs/en/skills).
Open for the batch 1 re-plan: carry each piece's text inside SKILL.md (no
reads, every agent), or keep `references/` and accept one read prompt on
Claude Code. Owner decides. Note: inside `claude plugin eval` with `Read`
granted, the reference loads (probe matched "The ten fields" in the
trace) — so evals won't catch this; only an ungranted run shows it.

## 2026-10-11 — Slice 1 architecture
Context: plan for SPEC slice 1 (C1–C24).
Decision: write the method once under `method/`; a build step copies each
skill's share into its own folder and fails on drift. claude.ai copies only
the skill's folder into its sandbox (claude.com/docs/skills/how-to), so a
skill cannot rely on a sibling's files. The repo is marketplace and plugin
at once, both named `7flows`, source `./` — `claude plugin validate --strict`
passes on that layout (plugins/marketplace-reference). Skills `7flows` (K)
and `7flows-test`, prefixed because `.agents/skills` is a shared namespace.
Descriptions ≤ 200 chars: support.claude.com 12512198 still says 200 while
claude.com docs say 1,024 — take the stricter. Close calls use the Wilson
90% interval against the pass line (NIST e-Handbook §7.2.4.1), run as a
script because mental arithmetic drifts. Evals run locally at release, on
the owner's account; CI runs only free gates.
Rejected: shared references via `${CLAUDE_PLUGIN_ROOT}` (Claude Code only;
breaks claude.ai ZIPs and Pi); textbook Wald interval (Brown, Cai &
DasGupta 2001: erratic at small n); "≥ 10 successes" rule (no authoritative
source); evals in CI (needs a paid credential in GitHub secrets, costs on
every push).

## 2026-10-11 — Stack and seeded rules
Context: craftsman init; the repo owns the method and the skills.
Decision: method as Markdown (one file per flow and mode) in this repo;
Agent Skills standard with spec-pure frontmatter (agentskills.io/specification)
so one tree serves Claude Code, claude.ai and `.agents/skills` agents (Pi,
pi.dev/docs/latest/skills); Claude plugin + marketplace from the same tree
(code.claude.com/docs/en/plugins-reference). Tooling in Python 3.14 via uv
with pytest, ruff, strict mypy — chosen by the owner over TypeScript on bun.
Skills: one router skill + one skill per flow; coach persona K, the master
cutter. Licences: method CC BY-SA 4.0, code and skills Apache-2.0.
Rejected: one skill per mode (crowds the skill list); a single monolithic coach
like Alicia (one description cannot trigger for every flow); TypeScript tooling.

## 2026-10-11 — One method, seven flows
Context: Core, Air, Max and Synergy sat on four different axes (stage, work
mode, size, AI); readers could not tell which applied, and the real gaps —
money, growth, people, governance, founder health — fit none of them.
Decision: one method, seven flows every company runs on, each with an atelier
signature mode: Test (the Toile), Sell (the Fitting), Earn (the Cloth), Gather
(the Atelier), Choose (the Cut), Make (the Stitch), Care (the House). Company
size, distributed work and agents are settings that tune each mode; people and
agents are one workforce. Audience: founders to SMEs, 1–500. Core, Air, Max
and Synergy are retired as the v1/X history; their 29 modes migrate in, with
three duplicate Core/Max pairs merged into size tiers.
Rejected: stage journey (Spark→Fit→Engine→Scale); core plus packs (repeats the
confusion at scale); diagnosis-only mode graph (no shape a reader can hold);
flow names Validate/Grow/Fund/Organize/Decide/Deliver/Steward (corporate
vocabulary — the roots are craft, impact and the couture house); enterprise
500+ scope.
