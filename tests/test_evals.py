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
