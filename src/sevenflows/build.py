"""Copy the method's source files into the skills that carry them.

claude.ai copies only a skill's own folder into its sandbox, so every skill
needs its own copy; the method is still written once, under method/.
"""

from collections.abc import Mapping, Sequence
from pathlib import Path

# Each skill's share of the method, as paths under method/.
MANIFEST: dict[str, list[str]] = {
    "7flows-test": ["test/toile.md"],
}

Manifest = Mapping[str, Sequence[str]]


def _header(source: str) -> str:
    return (
        f"<!-- Copied from method/{source} by `sevenflows build`. Edit there. -->\n\n"
    )


def _expected(root: Path, manifest: Manifest) -> dict[Path, str]:
    expected: dict[Path, str] = {}
    for skill, sources in manifest.items():
        for source in sources:
            text = (root / "method" / source).read_text(encoding="utf-8")
            target = root / "skills" / skill / "references" / Path(source).name
            # references/ is flat, so two sources with one basename would
            # silently overwrite each other.
            if target in expected:
                raise ValueError(f"{skill}: two sources would land on {target.name}")
            expected[target] = _header(source) + text
    return expected


def _present(root: Path) -> set[Path]:
    # Every skill, not just the manifest's: one dropped from the manifest
    # must not keep shipping its old copies.
    return {p for p in (root / "skills").glob("*/references/*") if p.is_file()}


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
