"""Hold every skill to the Agent Skills spec, to what claude.ai accepts, and
every method and skill text to K's voice."""

import re
from pathlib import Path

import yaml

SPEC_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
# The spec allows 1,024; support.claude.com's upload guide still says 200.
MAX_DESCRIPTION = 200
NAME = re.compile(r"^(?!.*--)[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
# Claude Code's skills guide: keep SKILL.md under 500 lines.
MAX_LINES = 499
VOICE = Path("method") / "voice.md"
# voice.md must name the words it bans, and so must every copy of it.
VOICE_REGION = re.compile(
    r"<!-- built from method/voice\.md — edit there -->\n.*?<!-- /built -->",
    re.DOTALL,
)


def _frontmatter(skill_md: Path) -> dict[str, object] | None:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if match is None:
        return None
    data = yaml.safe_load(match.group(1))
    return data if isinstance(data, dict) else None


def lint_skill(skill: Path) -> list[str]:
    folder = skill.name
    if not (skill / "SKILL.md").is_file():
        return [f"{folder}: SKILL.md is missing"]
    try:
        meta = _frontmatter(skill / "SKILL.md")
    except yaml.YAMLError:
        # A finding names the skill; a traceback leaves the reader to find it.
        return [f"{folder}: frontmatter is not valid YAML"]
    if meta is None:
        return [f"{folder}: SKILL.md has no frontmatter"]
    lines = (skill / "SKILL.md").read_text(encoding="utf-8").count("\n")
    findings = [
        f"{folder}: unknown frontmatter key '{key}'"
        for key in meta
        if key not in SPEC_FIELDS
    ]
    name = meta.get("name")
    if not isinstance(name, str) or not NAME.match(name):
        findings.append(f"{folder}: {name!r} is not a valid skill name")
    elif name != folder:
        findings.append(f"{folder}: name '{name}' does not match folder")
    description = meta.get("description")
    if not isinstance(description, str) or not description.strip():
        findings.append(f"{folder}: description is missing")
    elif len(description) > MAX_DESCRIPTION:
        findings.append(
            f"{folder}: description is {len(description)} chars, max {MAX_DESCRIPTION}"
        )
    if lines > MAX_LINES:
        findings.append(f"{folder}: SKILL.md is {lines} lines, max {MAX_LINES}")
    return findings


def banned_words(voice_md: Path) -> list[str]:
    """The first column of the table under "## Banned words", lowercased."""
    text = voice_md.read_text(encoding="utf-8")
    section = text.partition("## Banned words")[2].partition("\n## ")[0]
    rows = [line for line in section.splitlines() if line.startswith("|")]
    # rows[0] is the header, rows[1] the |---| separator.
    return [row.split("|")[1].strip().lower() for row in rows[2:]]


def lint_words(path: Path, root: Path, banned: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    # Blank the exempt region line for line, so findings keep true line numbers.
    text = VOICE_REGION.sub(lambda m: "\n" * m.group().count("\n"), text)
    patterns = [
        (word, re.compile(rf"\b{re.escape(word)}\w*", re.IGNORECASE)) for word in banned
    ]
    return [
        f"{path.relative_to(root)}:{number}: banned word '{word}'"
        for number, line in enumerate(text.splitlines(), start=1)
        for word, pattern in patterns
        if pattern.search(line)
    ]


def _voice(root: Path) -> list[str]:
    voice = root / VOICE
    if not voice.is_file():
        return [f"{VOICE} is missing — no banned words to check"]
    banned = banned_words(voice)
    if not banned:
        return [f"{VOICE} lists no banned words"]
    texts = sorted((root / "method").rglob("*.md")) + sorted(
        (root / "skills").rglob("*.md")
    )
    return [
        finding
        for path in texts
        if path.name != "voice.md"
        for finding in lint_words(path, root, banned)
    ]


def lint(root: Path) -> list[str]:
    return [
        finding
        for skill in sorted((root / "skills").iterdir())
        if skill.is_dir()
        for finding in lint_skill(skill)
    ] + _voice(root)
