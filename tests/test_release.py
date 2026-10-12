import json
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from sevenflows.build import LICENCES, MANIFEST, build
from sevenflows.release import (
    changelog_entry,
    eval_cases,
    refusals,
    release,
)

CHANGED = datetime(2026, 10, 12, 9, 0, tzinfo=UTC)
CASES = {"toile-quick", "swatch-fires"}


def case(name: str, score: float = 1.0, runs: int = 3, without: float = 0.5) -> Any:
    run = {"score": score, "skippedPaidGraders": False, "error": None}
    return {
        "name": name,
        "aggregates": {"score": score, "scoreWithout": without},
        "arms": {"with": [run] * runs, "without": [run] * runs},
    }


def result(*cases: Any, started: str = "2026-10-12T10:00:00.000Z") -> Any:
    return {
        "schemaVersion": 1,
        "startedAt": started,
        "partial": False,
        "aggregates": {"meanDelta": 0.4},
        "cases": list(cases) or [case(n) for n in sorted(CASES)],
    }


def test_a_full_green_run_after_the_last_change_ships() -> None:
    assert refusals(result(), CASES, CHANGED) == []


def test_a_case_below_a_perfect_score_refuses() -> None:
    run = result(case("toile-quick", score=0.93), case("swatch-fires"))
    assert refusals(run, CASES, CHANGED) == ["toile-quick scored 0.93, not 1.00"]


def test_a_case_with_fewer_than_three_runs_refuses() -> None:
    run = result(case("toile-quick", runs=1), case("swatch-fires"))
    assert refusals(run, CASES, CHANGED) == ["toile-quick ran 1 time, not 3"]


def test_a_run_whose_judges_were_skipped_refuses() -> None:
    skipped = case("toile-quick")
    skipped["arms"]["with"] = [{"score": 1.0, "skippedPaidGraders": True}] * 3
    run = result(skipped, case("swatch-fires"))
    assert refusals(run, CASES, CHANGED) == [
        "toile-quick: the cost ceiling skipped its judges"
    ]


def test_a_filtered_run_refuses_and_names_the_missing_cases() -> None:
    run = result(case("toile-quick"))
    assert refusals(run, CASES, CHANGED) == ["not in this run: swatch-fires"]


def test_a_case_no_longer_on_disk_refuses() -> None:
    run = result(*(case(n) for n in [*sorted(CASES), "old-case"]))
    assert refusals(run, CASES, CHANGED) == ["no longer a case: old-case"]


def test_a_partial_run_refuses() -> None:
    run = result()
    run["partial"], run["partialReason"] = True, "cost_ceiling"
    assert refusals(run, CASES, CHANGED) == ["the run stopped early: cost_ceiling"]


def test_the_plugin_must_score_higher_than_no_plugin() -> None:
    run = result()
    run["aggregates"]["meanDelta"] = 0.0
    assert refusals(run, CASES, CHANGED) == [
        "with the plugin the suite scores +0.00 against no plugin — it must be higher"
    ]


def test_a_run_without_the_no_plugin_arm_refuses() -> None:
    run = result()
    del run["aggregates"]["meanDelta"]
    assert refusals(run, CASES, CHANGED) == ["the run has no no-plugin arm to beat"]


def test_a_run_older_than_the_last_change_refuses() -> None:
    run = result(started="2026-10-12T08:59:59.000Z")
    assert refusals(run, CASES, CHANGED) == [
        "the run started 2026-10-12 08:59 UTC, before the last change to the "
        "skills or evals at 2026-10-12 09:00 UTC"
    ]


def test_eval_cases_are_the_folders_with_a_prompt_or_a_case_file(
    tmp_path: Path,
) -> None:
    for name, file in [("a", "prompt.md"), ("b", "case.yaml"), ("_fixtures", "x.md")]:
        (tmp_path / "evals" / name).mkdir(parents=True)
        (tmp_path / "evals" / name / file).write_text("")
    (tmp_path / "evals" / "results" / "2026").mkdir(parents=True)
    assert eval_cases(tmp_path) == {"a", "b"}


CHANGELOG = """# Changelog

## [Unreleased]

## [0.2.0] - 2026-11-01
### Added
- The Sell flow.

## [0.1.0] - 2026-10-12
### Added
- K and the Test flow.
"""


def test_changelog_entry_is_the_versions_section_body() -> None:
    assert changelog_entry(CHANGELOG, "0.1.0") == "### Added\n- K and the Test flow."
    assert changelog_entry(CHANGELOG, "0.2.0") == "### Added\n- The Sell flow."


def test_a_version_without_an_entry_has_none() -> None:
    assert changelog_entry(CHANGELOG, "0.3.0") is None
    assert changelog_entry("## [0.3.0] - 2026-12-01\n\n", "0.3.0") is None


class Git:
    """Stands in for git and gh: answers queries, records every command."""

    def __init__(self, root: Path, **answers: str) -> None:
        self.root = root
        self.calls: list[list[str]] = []
        self.answers = {
            "status": "",
            "branch": "main\n",
            "head": "abc\n",
            "upstream": "abc\n",
            "tags": "",
            "changed": "2026-10-12T09:00:00+00:00\n",
            **answers,
        }

    def __call__(self, command: Sequence[str]) -> str:
        self.calls.append(list(command))
        key = {
            ("git", "status"): "status",
            ("git", "branch"): "branch",
            ("git", "tag"): "tags",
            ("git", "log"): "changed",
        }.get((command[0], command[1]))
        if command[:2] == ["git", "rev-parse"]:
            key = "upstream" if "origin/main" in command else "head"
        return self.answers[key] if key else ""

    def wrote(self) -> list[list[str]]:
        reads = {"status", "branch", "rev-parse", "log"}
        return [
            c
            for c in self.calls
            if c[1] not in reads and not (c[1] == "tag" and "-l" in c)
        ]


def make_repo(root: Path, version: str = "0.1.0") -> Path:
    for name in LICENCES:
        (root / name).write_text(f"{name} text\n")
    for skill, sources in MANIFEST.items():
        (root / "skills" / skill).mkdir(parents=True)
        (root / "skills" / skill / "SKILL.md").write_text(f"---\nname: {skill}\n---\n")
        for source in sources:
            (root / "method" / source).parent.mkdir(parents=True, exist_ok=True)
            (root / "method" / source).write_text("# Source\n")
    build(root)
    (root / ".claude-plugin").mkdir()
    (root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "7flows", "version": version})
    )
    (root / "CHANGELOG.md").write_text(CHANGELOG)
    for name in CASES:
        (root / "evals" / name).mkdir(parents=True)
        (root / "evals" / name / "prompt.md").write_text("")
    results = root / "results.json"
    results.write_text(json.dumps(result()))
    return results


def test_a_green_release_tags_pushes_and_attaches_one_zip_per_skill(
    tmp_path: Path,
) -> None:
    results = make_repo(tmp_path)
    git = Git(tmp_path)
    assert release(tmp_path, "0.1.0", results, git) == []
    zips = [str(tmp_path / "dist" / f"{skill}.zip") for skill in MANIFEST]
    assert git.wrote() == [
        ["git", "tag", "-a", "v0.1.0", "-m", "7 Flows 0.1.0"],
        ["git", "push", "origin", "v0.1.0"],
        [
            "gh",
            "release",
            "create",
            "v0.1.0",
            *zips,
            "--verify-tag",
            "--title",
            "7 Flows 0.1.0",
            "--notes",
            "### Added\n- K and the Test flow.",
        ],
    ]


def test_a_failing_eval_never_tags(tmp_path: Path) -> None:
    results = make_repo(tmp_path)
    results.write_text(
        json.dumps(result(case("toile-quick", 0.6), case("swatch-fires")))
    )
    git = Git(tmp_path)
    assert release(tmp_path, "0.1.0", results, git) == [
        "toile-quick scored 0.60, not 1.00"
    ]
    assert git.wrote() == []
    assert not (tmp_path / "dist").exists()


def test_a_dry_run_checks_everything_and_writes_nothing(tmp_path: Path) -> None:
    results = make_repo(tmp_path)
    git = Git(tmp_path)
    assert release(tmp_path, "0.1.0", results, git, dry_run=True) == []
    assert git.wrote() == []


@pytest.mark.parametrize(
    ("version", "answers", "refusal"),
    [
        ("1.0", {}, "1.0 is not a SemVer version (X.Y.Z)"),
        ("0.2.1", {}, "CHANGELOG.md has no entry for 0.2.1"),
        ("0.2.0", {}, "plugin.json says 0.1.0, not 0.2.0"),
        ("0.1.0", {"tags": "v0.1.0\n"}, "v0.1.0 is already tagged"),
        ("0.1.0", {"status": " M README.md\n"}, "the working tree has changes"),
        ("0.1.0", {"branch": "spike\n"}, "releases leave from main, not spike"),
        ("0.1.0", {"upstream": "def\n"}, "main is not pushed to origin"),
    ],
)
def test_the_release_refuses_what_it_cannot_ship(
    tmp_path: Path, version: str, answers: dict[str, str], refusal: str
) -> None:
    results = make_repo(tmp_path)
    git = Git(tmp_path, **answers)
    assert refusal in release(tmp_path, version, results, git)
    assert git.wrote() == []


def test_unreadable_results_are_a_refusal_not_a_crash(tmp_path: Path) -> None:
    make_repo(tmp_path)
    missing = tmp_path / "nowhere.json"
    assert release(tmp_path, "0.1.0", missing, Git(tmp_path)) == [
        f"cannot read the eval results at {missing}"
    ]


def test_the_link_references_at_the_foot_stay_out_of_the_notes() -> None:
    footed = CHANGELOG + (
        "\n[unreleased]: https://github.com/7-flows/skills/compare/v0.1.0...HEAD\n"
        "[0.1.0]: https://github.com/7-flows/skills/releases/tag/v0.1.0\n"
    )
    assert changelog_entry(footed, "0.1.0") == "### Added\n- K and the Test flow."
