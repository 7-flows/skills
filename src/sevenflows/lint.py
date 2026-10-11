"""Hold every skill to the Agent Skills spec and to what claude.ai accepts."""

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
    return findings


def lint(root: Path) -> list[str]:
    return [
        finding
        for skill in sorted((root / "skills").iterdir())
        if skill.is_dir()
        for finding in lint_skill(skill)
    ]
