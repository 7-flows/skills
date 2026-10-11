import re
from pathlib import Path

import pytest
import yaml

EVALS = Path(__file__).parent.parent / "evals"
PROMPTS = sorted(EVALS.glob("*/prompt.md"))


@pytest.mark.parametrize("prompt", PROMPTS, ids=lambda p: p.parent.name)
def test_every_eval_prompt_has_frontmatter_that_parses(prompt: Path) -> None:
    # `claude plugin eval` drops a case whose frontmatter fails to parse and
    # runs the rest — a description opening on a quoted phrase did it twice.
    head = prompt.read_text(encoding="utf-8").split("---\n")[1]
    meta = yaml.safe_load(head)
    assert meta["description"]
    assert meta["tags"]


SOURCE = EVALS / "voice-no-flattery" / "graders" / "no-banned-words.md"
COPIES = sorted(EVALS.glob("*/graders/no-jargon.md"))


@pytest.mark.parametrize("copy", COPIES, ids=lambda p: p.parent.parent.name)
def test_every_no_jargon_grader_is_the_voice_case_grader(copy: Path) -> None:
    # The eval runner has no shared graders, so each case carries a copy.
    assert copy.read_text(encoding="utf-8") == SOURCE.read_text(encoding="utf-8")


def test_every_banned_word_graded_is_in_the_voice() -> None:
    found = re.search(r"pattern: '\\b\((.+)\)'", SOURCE.read_text())
    assert found
    pattern = found.group(1)
    voice = (EVALS.parent / "method" / "voice.md").read_text().lower()
    for word in pattern.split("|"):
        assert word.replace("[sz]", "z") in voice, word
