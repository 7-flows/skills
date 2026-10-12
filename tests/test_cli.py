import subprocess
from pathlib import Path

import pytest

from sevenflows import cli
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


def test_release_prints_each_refusal_and_exits_1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    calls: list[tuple[str, Path, bool]] = []

    def refuse(root: Path, version: str, results: Path, dry_run: bool) -> list[str]:
        calls.append((version, results, dry_run))
        return ["toile-quick scored 0.93, not 1.00", "main is not pushed to origin"]

    monkeypatch.setattr(cli, "release", refuse)
    monkeypatch.chdir(tmp_path)
    assert main(["release", "0.1.0", "--results", "r.json"]) == 1
    assert calls == [("0.1.0", Path("r.json"), False)]
    assert capsys.readouterr().out == (
        "refused: toile-quick scored 0.93, not 1.00\n"
        "refused: main is not pushed to origin\n"
    )


def test_a_clean_dry_run_says_what_it_would_release(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "release", lambda *a, **k: [])
    monkeypatch.chdir(tmp_path)
    assert main(["release", "0.1.0", "--results", "r.json", "--dry-run"]) == 0
    assert capsys.readouterr().out == "would release v0.1.0\n"


def test_a_failing_git_or_gh_command_is_reported_not_a_traceback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fail(*args: object, **kwargs: object) -> list[str]:
        raise subprocess.CalledProcessError(1, ["gh", "release"], stderr="no auth\n")

    monkeypatch.setattr(cli, "release", fail)
    monkeypatch.chdir(tmp_path)
    assert main(["release", "0.1.0", "--results", "r.json"]) == 1
    assert capsys.readouterr().out == "gh release failed: no auth\n"
