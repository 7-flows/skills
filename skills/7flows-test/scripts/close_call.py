# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Call a Toile's result against its pass line: pass, miss, or too close.

    python3 scripts/close_call.py SUCCESSES TRIALS PASS_LINE
    python3 scripts/close_call.py 9 200 5%
    python3 scripts/close_call.py --plan 200 5%

With --plan, before the test runs: which results the planned size can call.

The range is the Wilson 90% interval (NIST e-Handbook §7.2.4.1). A pass line
inside it is too close to tell from chance. The larger test is sized by
§7.2.4.2: enough trials to tell the rate seen from the line, one-sided
alpha 0.05 (the same 1.645 as the range) and beta 0.10, continuity-corrected.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from statistics import NormalDist

# Stdlib only: the script runs wherever the skill folder lands — claude.ai's
# sandbox, Pi, a founder's laptop — with nothing to install.
Z = NormalDist().inv_cdf(0.95)
Z_POWER = NormalDist().inv_cdf(0.90)


@dataclass(frozen=True)
class Verdict:
    call: str
    low: float
    high: float
    needed: int
    short: int
    size: int | None


def wilson(successes: int, trials: int) -> tuple[float, float]:
    p = successes / trials
    z2 = Z * Z
    centre = p + z2 / (2 * trials)
    spread = Z * math.sqrt(p * (1 - p) / trials + z2 / (4 * trials * trials))
    scale = 1 + z2 / trials
    return (centre - spread) / scale, (centre + spread) / scale


def size(line: float, rate: float) -> int:
    delta = abs(rate - line)
    root = Z * math.sqrt(line * (1 - line)) + Z_POWER * math.sqrt(rate * (1 - rate))
    return math.ceil((root / delta) ** 2 + 1 / delta)


def verdict(successes: int, trials: int, line: float) -> Verdict:
    low, high = wilson(successes, trials)
    # The line is "the number that means the belief holds": reaching it counts.
    needed = math.ceil(line * trials - 1e-9)
    short = max(needed - successes, 0)
    if low >= line:
        return Verdict("pass", low, high, needed, short, None)
    if high < line:
        return Verdict("miss", low, high, needed, short, None)
    rate = successes / trials
    # On the line itself no test size can tell the two apart.
    bigger = size(line, rate) if rate != line else None
    return Verdict("too close", low, high, needed, short, bigger)


@dataclass(frozen=True)
class Plan:
    needed: int
    passes: int | None
    misses: int | None


def plan(trials: int, line: float) -> Plan:
    # The verdict's own edges, so the plan and the call never disagree.
    calls = [verdict(x, trials, line).call for x in range(trials + 1)]
    passing = [x for x, call in enumerate(calls) if call == "pass"]
    missing = [x for x, call in enumerate(calls) if call == "miss"]
    return Plan(
        verdict(0, trials, line).needed,
        passing[0] if passing else None,
        missing[-1] if missing else None,
    )


def _percent(x: float, places: int = 1) -> str:
    return f"{x * 100:.{places}f}%"


def _apart(rate: float, line: float) -> tuple[str, str]:
    # "To tell 33.3% from 33.3%" reads as nonsense: add places until they differ.
    places = 1
    while places < 6 and _percent(rate, places) == _percent(line, places):
        places += 1
    return _percent(rate, places), _percent(line, places)


def _say(successes: int, trials: int, line: float, v: Verdict) -> str:
    lines = [
        f"{v.call.upper()}: {successes} of {trials} is {_percent(successes / trials)}"
        f" against a pass line of {_percent(line)} ({v.needed} of {trials}).",
        f"The 90% range runs {_percent(v.low)} to {_percent(v.high)}.",
    ]
    if v.short:
        lines.append(f"{v.short} short of the {v.needed} the line asks for.")
    if v.call == "too close":
        lines.append("Too close to tell from chance: not a Persevere, not a Pivot.")
        if v.size is None:
            lines.append("The result sits on the line; no larger test separates them.")
        else:
            seen, wanted = _apart(successes / trials, line)
            lines.append(f"To tell {seen} from {wanted} takes about {v.size:,} trials.")
            lines.append(
                f"Propose: Experiment Again, the same test run to about {v.size:,}."
            )
    return "\n".join(lines)


def _say_plan(trials: int, line: float, p: Plan) -> str:
    head = (
        f"{trials} trials against a pass line of {_percent(line)}"
        f" ({p.needed} of {trials})."
    )
    if p.passes is None:
        return "\n".join(
            [
                f"TOO SMALL: {head}",
                f"Not even {trials} of {trials} clears the line beyond chance.",
                "No result can pass: raise the size before the test runs.",
            ]
        )
    low = 0 if p.misses is None else p.misses + 1
    lines = [f"PLAN: {head}", f"{p.passes} or more passes."]
    if p.misses is None:
        lines.append(f"No result can miss: even 0 of {trials} is too close to call.")
    else:
        lines.append(f"{p.misses} or fewer misses.")
    if low < p.passes:
        between = str(low) if low == p.passes - 1 else f"{low} to {p.passes - 1}"
        lines.append(f"{between} is too close to call.")
    return "\n".join(lines)


def _line(text: str) -> float:
    if not text.endswith("%"):
        raise ValueError("give the pass line as a percent, e.g. 5%")
    return float(text.removesuffix("%")) / 100


def main(argv: list[str]) -> int:
    usage = (
        "usage: close_call.py SUCCESSES TRIALS PASS_LINE  (e.g. 9 200 5%)\n"
        "       close_call.py --plan TRIALS PASS_LINE     (e.g. --plan 200 5%)"
    )
    planning = argv[:1] == ["--plan"]
    try:
        if planning:
            successes, trials, line = 0, int(argv[1]), _line(argv[2])
        else:
            successes, trials = int(argv[0]), int(argv[1])
            line = _line(argv[2])
    except (IndexError, ValueError) as error:
        print(f"{error}\n{usage}", file=sys.stderr)
        return 2
    if trials < 1 or not 0 <= successes <= trials:
        print(
            f"successes must be 0 to {trials} trials, and trials 1 or more",
            file=sys.stderr,
        )
        return 2
    if not 0 < line < 1:
        print("the pass line must be above 0% and below 100%", file=sys.stderr)
        return 2
    if planning:
        print(_say_plan(trials, line, plan(trials, line)))
    else:
        print(_say(successes, trials, line, verdict(successes, trials, line)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
