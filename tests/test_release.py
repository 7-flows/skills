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
    assert refusals(run, CASES, CHANGED) == [
        "toile-quick scored 0.93, not 1.00, and has no fresh re-run"
    ]


def test_a_case_with_fewer_than_three_runs_refuses() -> None:
    run = result(case("toile-quick", runs=1), case("swatch-fires"))
    assert refusals(run, CASES, CHANGED) == ["toile-quick ran 1 time, not 3"]


def test_a_run_whose_judges_were_skipped_refuses() -> None:
    skipped = case("toile-quick")
    skipped["arms"]["with"] = [{"score": 1.0, "skippedPaidGraders": True}] * 3
    run = result(skipped, case("swatch-fires"))
    assert refusals(run, CASES, CHANGED) == [
        "toile-quick had its judges skipped by the cost ceiling"
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
        "toile-quick scored 0.60, not 1.00, and has no fresh re-run"
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


def test_times_from_another_zone_are_told_in_utc() -> None:
    paris = datetime.fromisoformat("2026-10-12T11:00:00+02:00")
    run = result(started="2026-10-12T08:30:00.000Z")
    assert refusals(run, CASES, paris) == [
        "the run started 2026-10-12 08:30 UTC, before the last change to the "
        "skills or evals at 2026-10-12 09:00 UTC"
    ]


# C22: a short case gets one fresh 3-run re-run, and every failed run of the
# full run is read and logged as a judge's misread.
def short_run() -> Any:
    short = case("toile-quick", score=0.67)
    short["arms"]["with"] = [{"score": 1.0}, {"score": 0.0}, {"score": 1.0}]
    return result(short, case("swatch-fires"))


def rerun(score: float = 1.0, started: str = "2026-10-12T11:00:00.000Z") -> Any:
    return result(case("toile-quick", score=score), started=started)


READ = "- toile-quick run 2: misread — one question; the judge counted the hint\n"


def test_a_short_case_with_a_perfect_fresh_rerun_and_its_reading_ships() -> None:
    assert refusals(short_run(), CASES, CHANGED, [rerun()], READ) == []


def test_a_rerun_that_falls_short_refuses() -> None:
    assert refusals(short_run(), CASES, CHANGED, [rerun(0.89)], READ) == [
        "toile-quick re-run scored 0.89, not 1.00"
    ]


def test_a_rerun_older_than_the_full_run_is_no_rerun() -> None:
    old = rerun(started="2026-10-12T09:30:00.000Z")
    assert refusals(short_run(), CASES, CHANGED, [old], READ) == [
        "toile-quick scored 0.67, not 1.00, and has no fresh re-run"
    ]


def test_a_partial_rerun_is_no_rerun() -> None:
    partial = rerun()
    partial["partial"] = True
    assert refusals(short_run(), CASES, CHANGED, [partial], READ) == [
        "toile-quick scored 0.67, not 1.00, and has no fresh re-run"
    ]


def test_a_rerun_with_fewer_than_three_runs_refuses() -> None:
    short = result(case("toile-quick", runs=2), started="2026-10-12T11:00:00.000Z")
    assert refusals(short_run(), CASES, CHANGED, [short], READ) == [
        "toile-quick re-run ran 2 times, not 3"
    ]


@pytest.mark.parametrize(
    "readings",
    [
        "",
        "- toile-quick run 1: misread — wrong run\n",
        "- toile-quick run 2: misread —\n",
        "- toile-quick run 2: K's slip — asked two things\n",
    ],
)
def test_every_failed_run_must_be_read_as_a_misread_with_a_reason(
    readings: str,
) -> None:
    assert refusals(short_run(), CASES, CHANGED, [rerun()], readings) == [
        "toile-quick run 2 failed and is not logged as a misread with its reason"
    ]


def test_the_latest_fresh_rerun_is_the_one_that_counts() -> None:
    first = rerun(0.89, started="2026-10-12T11:00:00.000Z")
    second = rerun(1.0, started="2026-10-12T12:00:00.000Z")
    assert refusals(short_run(), CASES, CHANGED, [second, first], READ) == []


def test_a_release_reads_its_reruns_and_the_versions_readings(
    tmp_path: Path,
) -> None:
    results = make_repo(tmp_path)
    results.write_text(json.dumps(short_run()))
    again = tmp_path / "rerun.json"
    again.write_text(json.dumps(rerun()))
    (tmp_path / "evals" / "readings").mkdir()
    (tmp_path / "evals" / "readings" / "v0.1.0.md").write_text(READ)
    git = Git(tmp_path)
    assert release(tmp_path, "0.1.0", results, git, reruns=[again]) == []
    assert git.wrote()[0][:4] == ["git", "tag", "-a", "v0.1.0"]


def test_logging_the_readings_does_not_make_the_run_stale(tmp_path: Path) -> None:
    results = make_repo(tmp_path)
    git = Git(tmp_path)
    release(tmp_path, "0.1.0", results, git, dry_run=True)
    log = next(c for c in git.calls if c[1] == "log")
    assert ":(exclude)evals/readings" in log


def test_an_unreadable_rerun_is_a_refusal(tmp_path: Path) -> None:
    results = make_repo(tmp_path)
    missing = tmp_path / "nowhere.json"
    assert release(tmp_path, "0.1.0", results, Git(tmp_path), reruns=[missing]) == [
        f"cannot read the eval results at {missing}"
    ]


def test_a_run_whose_session_errored_refuses_whatever_its_score() -> None:
    run = result()
    runs = run["cases"][0]["arms"]["with"]
    runs[1] = {**runs[1], "error": "exit 1: You've hit your limit"}
    assert refusals(run, CASES, CHANGED) == [
        "swatch-fires run 2 ended in an error: exit 1: You've hit your limit"
    ]


def test_an_errored_session_without_the_plugin_refuses_too() -> None:
    run = result()
    run["cases"][1]["arms"]["without"] = [{"score": 0.0, "error": "timed out"}] * 3
    assert refusals(run, CASES, CHANGED) == [
        "toile-quick run 1 without the plugin ended in an error: timed out",
        "toile-quick run 2 without the plugin ended in an error: timed out",
        "toile-quick run 3 without the plugin ended in an error: timed out",
    ]
