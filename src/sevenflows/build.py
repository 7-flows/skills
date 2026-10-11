"""Copy the method's source files into the skills that carry them.

claude.ai copies only a skill's own folder into its sandbox, so every skill
needs its own copy; the method is still written once, under method/.

A source's essentials, marked `<!-- core -->`…`<!-- /core -->`, are also
written into the skill's SKILL.md: a headless Claude Code run can't read the
skill's references/ without a grant (ADR 2026-10-11 Hybrid).
"""

import re
from collections.abc import Mapping, Sequence
from pathlib import Path

# Each skill's share of the method, as paths under method/.
MANIFEST: dict[str, list[str]] = {
    "7flows": ["k.md", "voice.md", "notes.md", "flows.md"],
    # The Test skill must stand alone (a claude.ai user may upload only it),
    # so it carries K's voice and the notes layout it saves into.
    "7flows-test": [
        "test/toile.md",
        "test/close-calls.md",
        "test/swatch.md",
        "voice.md",
        "notes.md",
    ],
}

Manifest = Mapping[str, Sequence[str]]

# Repo-root licence texts every skill carries: a skill uploaded alone must
# still say which terms its code (Apache-2.0) and its method text (CC BY-SA)
# come under.
LICENCES = ("LICENSE", "LICENSE-METHOD")


def _header(source: str) -> str:
    return (
        f"<!-- Copied from method/{source} by `sevenflows build`. Edit there. "
        "7 Flows method text, CC BY-SA 4.0 — see LICENSE-METHOD. -->\n\n"
    )


CORE = re.compile(r"<!-- core -->\n(.*?)<!-- /core -->", re.DOTALL)
# The blank line before a region belongs to it, so removing one leaves the
# hand-written head exactly as written. Editors may trim the file's final
# newline, so the closing marker may end the file.
REGION = re.compile(
    r"\n?<!-- built from method/(\S+) — edit there -->\n.*?<!-- /built -->(?:\n|\Z)",
    re.DOTALL,
)


def _core(source: str, text: str) -> str | None:
    regions = CORE.findall(text)
    if text.count("<!-- core -->") != len(regions):
        raise ValueError(f"method/{source}: unclosed <!-- core --> marker")
    return "\n".join(regions) if regions else None


def _region(source: str, core: str) -> str:
    return f"<!-- built from method/{source} — edit there -->\n{core}<!-- /built -->\n"


def _inlined(skill_md: str, cores: dict[str, str]) -> str:
    """Rewrite SKILL.md's built regions in place; append new ones at the end."""
    placed: set[str] = set()

    def rewrite(match: re.Match[str]) -> str:
        source = match.group(1)
        if source not in cores or source in placed:
            return ""
        placed.add(source)
        return "\n" + _region(source, cores[source])

    text = REGION.sub(rewrite, skill_md)
    for source, core in cores.items():
        if source not in placed:
            text = text.rstrip("\n") + "\n\n" + _region(source, core)
    return text


def _licences(root: Path) -> dict[str, str]:
    texts: dict[str, str] = {}
    for name in LICENCES:
        if not (root / name).is_file():
            raise ValueError(f"{name} is missing at the repo root")
        texts[name] = (root / name).read_text(encoding="utf-8")
    return texts


def _expected(root: Path, manifest: Manifest) -> dict[Path, str]:
    expected: dict[Path, str] = {}
    licences = _licences(root)
    for skill, sources in manifest.items():
        for name, text in licences.items():
            expected[root / "skills" / skill / name] = text
        cores: dict[str, str] = {}
        for source in sources:
            text = (root / "method" / source).read_text(encoding="utf-8")
            if (core := _core(source, text)) is not None:
                cores[source] = core
            target = root / "skills" / skill / "references" / Path(source).name
            # references/ is flat, so two sources with one basename would
            # silently overwrite each other.
            if target in expected:
                raise ValueError(f"{skill}: two sources would land on {target.name}")
            expected[target] = _header(source) + text
        skill_md = root / "skills" / skill / "SKILL.md"
        if skill_md.is_file():
            current = skill_md.read_text(encoding="utf-8")
            if REGION.search(current) or cores:
                expected[skill_md] = _inlined(current, cores)
        elif cores:
            raise ValueError(
                f"{skill}: SKILL.md is missing, nowhere to inline the core"
            )
    return expected


def _present(root: Path) -> set[Path]:
    # Every skill, not just the manifest's: one dropped from the manifest
    # must not keep shipping its old copies.
    copies = [*(root / "skills").glob("*/references/*")]
    copies += [p for name in LICENCES for p in (root / "skills").glob(f"*/{name}")]
    return {p for p in copies if p.is_file()}


def check(root: Path, manifest: Manifest = MANIFEST) -> list[Path]:
    """Return every copy that is missing, stale, or no longer in the manifest."""
    expected = _expected(root, manifest)
    drifted = [
        path
        for path, text in expected.items()
        if not path.is_file() or path.read_text(encoding="utf-8") != text
    ]
    drifted += sorted(_present(root) - expected.keys())
    return drifted


def build(root: Path, manifest: Manifest = MANIFEST) -> None:
    expected = _expected(root, manifest)
    for stale in _present(root) - expected.keys():
        stale.unlink()
    for path, text in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
