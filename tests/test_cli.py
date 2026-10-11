from pathlib import Path

import pytest

from sevenflows.build import LICENCES, MANIFEST, build
from sevenflows.cli import main
from sevenflows.lint import LICENCE_LINE


def make_repo(root: Path) -> None:
    for skill, sources in MANIFEST.items():
        (root / "skills" / skill).mkdir(parents=True)
        (root / "skills" / skill / "SKILL.md").write_text(
            f"---\nname: {skill}\ndescription: Test a belief.\n"
            f"license: {LICENCE_LINE}\n---\n\nBody.\n"
        )
        for source in sources:
            (root / "method" / source).parent.mkdir(parents=True, exist_ok=True)
            (root / "method" / source).write_text("# Source\n")
    for name in LICENCES:
        (root / name).write_text(f"{name} text\n")
    (root / "method" / "voice.md").write_text(
        "## Banned words\n\n| Banned | Say instead |\n|---|---|\n| Leverage | Use |\n"
    )
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


def test_package_writes_one_zip_per_skill_and_names_them(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    make_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert main(["package"]) == 0
    out = capsys.readouterr().out
    for skill in MANIFEST:
        assert (tmp_path / "dist" / f"{skill}.zip").is_file()
        assert f"dist/{skill}.zip" in out


def test_package_exits_1_on_stale_copies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    make_repo(tmp_path)
    (tmp_path / "method" / "k.md").write_text("# Recut\n")
    monkeypatch.chdir(tmp_path)
    assert main(["package"]) == 1
    assert "run `sevenflows build`" in capsys.readouterr().out
