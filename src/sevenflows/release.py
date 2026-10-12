"""Tag a release only on a full, fresh, green eval run.

`claude plugin eval` exits 0 when every case it ran meets the threshold, but
it never checks the with/without delta, and a run narrowed by --tag or --case
exits 0 too. The release reads the run's JSON and holds it to the whole
promise: every case on disk, three runs each, all perfect, the plugin ahead.
"""

import json
import re
import subprocess
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sevenflows.package import package

Runner = Callable[[Sequence[str]], str]

RUNS = 3
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
# A change here after the run started means the run graded something else.
GRADED = ["skills", "evals", "method", ".claude-plugin"]


def _run(command: Sequence[str]) -> str:
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout


def eval_cases(root: Path) -> set[str]:
    evals = root / "evals"
    return {
        p.parent.name
        for pattern in ("*/prompt.md", "*/case.yaml")
        for p in evals.glob(pattern)
    }


def _when(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


def refusals(result: Any, cases: set[str], changed_at: datetime) -> list[str]:
    """Every reason this eval run can't carry a release; empty means it can."""
    if result.get("partial"):
        return [f"the run stopped early: {result.get('partialReason', 'unknown')}"]
    found: list[str] = []
    ran = {c["name"] for c in result["cases"]}
    if missing := sorted(cases - ran):
        found.append(f"not in this run: {', '.join(missing)}")
    if gone := sorted(ran - cases):
        found.append(f"no longer a case: {', '.join(gone)}")
    for case in result["cases"]:
        name, runs = case["name"], case["arms"]["with"]
        if len(runs) < RUNS:
            found.append(
                f"{name} ran {len(runs)} time{'s' * (len(runs) != 1)}, not {RUNS}"
            )
        elif any(run.get("skippedPaidGraders") for run in runs):
            found.append(f"{name}: the cost ceiling skipped its judges")
        elif (score := case["aggregates"]["score"]) < 1:
            found.append(f"{name} scored {score:.2f}, not 1.00")
    delta = result["aggregates"].get("meanDelta")
    if delta is None:
        found.append("the run has no no-plugin arm to beat")
    elif delta <= 0:
        found.append(
            f"with the plugin the suite scores {delta:+.2f} against no plugin"
            " — it must be higher"
        )
    started = datetime.fromisoformat(result["startedAt"])
    if started < changed_at:
        found.append(
            f"the run started {_when(started)}, before the last change to the "
            f"skills or evals at {_when(changed_at)}"
        )
    return found


def changelog_entry(changelog: str, version: str) -> str | None:
    """The body of `## [version]`, or None when it is missing or empty."""
    heading = re.search(rf"^## \[{re.escape(version)}\].*$", changelog, re.MULTILINE)
    if heading is None:
        return None
    # A section ends at the next version, or at the link references that
    # Keep a Changelog puts at the foot of the file.
    body = re.split(r"\n## |\n\[[^\]]+\]: ", changelog[heading.end() :], maxsplit=1)[0]
    body = body.strip()
    return body or None


def _repo(root: Path, version: str, run: Runner) -> list[str]:
    found: list[str] = []
    if run(["git", "tag", "-l", f"v{version}"]).strip():
        found.append(f"v{version} is already tagged")
    if run(["git", "status", "--porcelain"]).strip():
        found.append("the working tree has changes")
    if (branch := run(["git", "branch", "--show-current"]).strip()) != "main":
        found.append(f"releases leave from main, not {branch}")
    elif run(["git", "rev-parse", "HEAD"]) != run(["git", "rev-parse", "origin/main"]):
        found.append("main is not pushed to origin")
    plugin = json.loads((root / ".claude-plugin" / "plugin.json").read_text())
    if plugin["version"] != version:
        found.append(f"plugin.json says {plugin['version']}, not {version}")
    return found


def release(
    root: Path,
    version: str,
    results: Path,
    run: Runner = _run,
    dry_run: bool = False,
) -> list[str]:
    """Tag v<version> and publish one ZIP per skill; return refusals instead."""
    if not SEMVER.match(version):
        return [f"{version} is not a SemVer version (X.Y.Z)"]
    notes = changelog_entry(
        (root / "CHANGELOG.md").read_text(encoding="utf-8"), version
    )
    found = [] if notes else [f"CHANGELOG.md has no entry for {version}"]
    found += _repo(root, version, run)
    try:
        result = json.loads(results.read_text(encoding="utf-8"))
    except OSError, ValueError:
        return [*found, f"cannot read the eval results at {results}"]
    changed = run(["git", "log", "-1", "--format=%cI", "--", *GRADED]).strip()
    found += refusals(result, eval_cases(root), datetime.fromisoformat(changed))
    if found or dry_run:
        return found
    archives = package(root)
    tag, title = f"v{version}", f"7 Flows {version}"
    run(["git", "tag", "-a", tag, "-m", title])
    run(["git", "push", "origin", tag])
    run(
        [
            "gh", "release", "create", tag, *map(str, archives),
            "--verify-tag", "--title", title, "--notes", str(notes),
        ]
    )  # fmt: skip
    return []
