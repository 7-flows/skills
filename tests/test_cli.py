from pathlib import Path

import pytest

from sevenflows.build import MANIFEST, build
from sevenflows.cli import main


def make_repo(root: Path) -> None:
    for skill, sources in MANIFEST.items():
        (root / "skills" / skill).mkdir(parents=True)
        (root / "skills" / skill / "SKILL.md").write_text(
            f"---\nname: {skill}\ndescription: Test a belief.\n---\n\nBody.\n"
        )
        for source in sources:
            (root / "method" / source).parent.mkdir(parents=True, exist_ok=True)
            (root / "method" / source).write_text("# Source\n")
    build(root)


# The Skills gate trusts these exit codes, so a drift must turn it red.
def test_build_check_exits_0_when_clean(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    make_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert main(["build", "--check"]) == 0


def test_build_check_exits_1_on_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    make_repo(tmp_path)
    (tmp_path / "method" / "test" / "toile.md").write_text("# Recut\n")
    monkeypatch.chdir(tmp_path)
    assert main(["build", "--check"]) == 1


def test_lint_exits_0_when_clean(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    make_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert main(["lint"]) == 0


def test_lint_exits_1_on_a_finding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    make_repo(tmp_path)
    (tmp_path / "skills" / "7flows-test" / "SKILL.md").write_text("No frontmatter.\n")
    monkeypatch.chdir(tmp_path)
    assert main(["lint"]) == 1
