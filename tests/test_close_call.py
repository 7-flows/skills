import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = (
    Path(__file__).parent.parent
    / "skills"
    / "7flows-test"
    / "scripts"
    / "close_call.py"
)


def load() -> ModuleType:
    # The script ships inside the skill folder, not the package: claude.ai and
    # Pi get only that folder.
    spec = importlib.util.spec_from_file_location("close_call", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["close_call"] = module
    spec.loader.exec_module(module)
    return module


close_call = load()


@pytest.mark.parametrize(
    ("successes", "trials"),
    [(9, 200), (10, 200), (0, 30)],
)
def test_results_near_a_five_percent_line_are_too_close(
    successes: int, trials: int
) -> None:
    assert close_call.verdict(successes, trials, 0.05).call == "too close"


def test_well_above_the_line_is_a_pass() -> None:
    assert close_call.verdict(25, 200, 0.05).call == "pass"


def test_well_below_the_line_is_a_miss() -> None:
    assert close_call.verdict(2, 200, 0.05).call == "miss"


def test_the_range_is_wilson_at_ninety_percent() -> None:
    # Worked by hand from NIST e-Handbook §7.2.4.1, z = 1.6449.
    v = close_call.verdict(9, 200, 0.05)
    assert v.low == pytest.approx(0.0264, abs=1e-4)
    assert v.high == pytest.approx(0.0758, abs=1e-4)


def test_the_gap_counts_what_the_line_needed() -> None:
    v = close_call.verdict(9, 200, 0.05)
    assert (v.needed, v.short) == (10, 1)
    assert close_call.verdict(25, 200, 0.05).short == 0


def test_the_size_matches_the_nist_worked_example() -> None:
    # NIST e-Handbook §7.2.4.2: p0 0.10, p1 0.20, one-sided alpha 0.05, beta 0.10,
    # 112 with the continuity correction.
    assert close_call.size(0.10, 0.20) == 112


def test_a_too_close_call_names_a_larger_test() -> None:
    assert close_call.verdict(0, 30, 0.05).size == 72
    assert close_call.verdict(9, 200, 0.05).size > 200


def test_a_result_exactly_on_the_line_has_no_size() -> None:
    assert close_call.verdict(10, 200, 0.05).size is None


def test_the_command_line_says_the_call_and_the_gap(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert close_call.main(["9", "200", "5%"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("TOO CLOSE")
    assert "1 short of the 10" in out
    assert "2.6% to 7.6%" in out
    assert "Propose: Experiment Again, the same test run to about 15,783." in out


@pytest.mark.parametrize(
    "argv",
    [["201", "200", "5%"], ["0", "0", "5%"], ["9", "200", "5"], ["9", "200", "120%"]],
)
def test_impossible_input_is_refused_with_a_reason(
    argv: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    assert close_call.main(argv) == 2
    assert capsys.readouterr().err.strip()


def test_a_line_that_floats_just_over_a_whole_count_still_needs_that_count() -> None:
    # 0.07 * 100 is 7.000000000000001 in floating point.
    assert close_call.verdict(7, 100, 0.07).needed == 7


def test_rates_that_round_alike_are_shown_apart(
    capsys: pytest.CaptureFixture[str],
) -> None:
    close_call.main(["1", "3", "33.3%"])
    assert "from 33.3% takes" not in capsys.readouterr().out


@pytest.mark.parametrize(
    ("trials", "line", "passes", "misses"),
    [(200, 0.05, 16, 4), (150, 0.20, 39, 21)],
)
def test_a_planned_size_names_the_pass_and_the_miss(
    trials: int, line: float, passes: int, misses: int
) -> None:
    plan = close_call.plan(trials, line)
    assert (plan.passes, plan.misses) == (passes, misses)
    # The bounds are the verdict's own edges, not a second rule.
    assert close_call.verdict(passes, trials, line).call == "pass"
    assert close_call.verdict(passes - 1, trials, line).call == "too close"
    assert close_call.verdict(misses, trials, line).call == "miss"
    assert close_call.verdict(misses + 1, trials, line).call == "too close"


def test_a_size_no_result_can_pass_is_too_small() -> None:
    assert close_call.plan(10, 0.8).passes is None


def test_a_size_no_result_can_miss_says_so() -> None:
    assert close_call.plan(20, 0.05).misses is None


def test_the_command_line_sizes_a_plan(capsys: pytest.CaptureFixture[str]) -> None:
    assert close_call.main(["--plan", "200", "5%"]) == 0
    out = capsys.readouterr().out
    assert "16 or more passes" in out
    assert "4 or fewer misses" in out
    assert "5 to 15 is too close to call" in out


def test_the_command_line_warns_a_plan_is_too_small(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert close_call.main(["--plan", "10", "80%"]) == 0
    assert capsys.readouterr().out.startswith("TOO SMALL")


@pytest.mark.parametrize(
    "argv", [["--plan", "0", "5%"], ["--plan", "200"], ["--plan", "200", "5"]]
)
def test_an_impossible_plan_is_refused_with_a_reason(
    argv: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    assert close_call.main(argv) == 2
    assert capsys.readouterr().err.strip()
