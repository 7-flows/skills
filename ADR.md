# Decisions — 7 Flows Skills

Read before re-litigating anything. Newest first.

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
