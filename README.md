# 7 Flows Skills

The 7 Flows method for founders and the people who act, as Agent Skills.
K, the master cutter, keeps your business notes and works the Test flow
with you: a belief tried on real people before you build on it.

Two skills ship today:

- `7flows` — K. Call K, or bring a business problem; K names the next piece.
- `7flows-test` — the Test flow: the Toile tests a belief, the Swatch reads
  what customers keep telling you.

## Install

Pick the place you work. Then say **"K, let's work"**.

### Claude Code

In a session, in your project:

```text
/plugin install 7flows --marketplace 7-flows/skills
```

Choose a scope when asked. From your shell instead:

```bash
claude plugin install 7flows --marketplace 7-flows/skills
```

### claude.ai — from the marketplace

Plugins come with every paid plan (Pro, Max, Team, Enterprise).

1. Open **Customize** in the left sidebar, then the **Plugins** tab.
2. Click **Add**, then **Add marketplace**, then **Add from a repository**.
3. Enter `7-flows/skills`.
4. On the **Discover** tab, select **7 Flows** and click **Add**.

### claude.ai — upload the skills

On any plan, with **Code execution and file creation** on (Settings →
Capabilities; on Team and Enterprise, an owner turns it on).

1. Download `7flows.zip` and `7flows-test.zip` from the latest
   [release](https://github.com/7-flows/skills/releases).
2. Open **Customize** → **Skills**, click **+**, then **Create skill** →
   **Upload a skill**.
3. Upload each ZIP, one at a time.

### Pi

In your project:

```bash
pi install git:github.com/7-flows/skills -l
pi
```

The first time, Pi asks whether to trust this project: say yes, or the
skills won't load. `/trust` keeps that answer for later sessions. For a
one-off run, `pi -a -p "K, let's work"` trusts the project for that run
only.

### Other agents

The skills follow the [Agent Skills](https://agentskills.io) standard. An
agent that reads `.agents/skills/` can use them: copy `skills/7flows` and
`skills/7flows-test` into your project's `.agents/skills/`. We test on
Claude Code, claude.ai and Pi; others may work.

## Your notes

K keeps your work in `7flows-notes/` in your project: a profile, and one
record per piece. They are plain Markdown — yours to read, edit and keep.
On claude.ai, where there is no project folder, K hands each record over
as a file; attach it to a new chat to pick up where you left off.

## Licence

The 7 Flows method — everything under `method/` and its copies in each
skill's `references/` and SKILL.md — is licensed under
[CC BY-SA 4.0](LICENSE-METHOD). The skills' code and tooling are licensed
under [Apache-2.0](LICENSE). Every skill folder and every release ZIP
carries both texts.
