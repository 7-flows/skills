import re
from pathlib import Path

METHOD = Path(__file__).parent.parent / "method"


def field_names(piece: Path) -> list[str]:
    return re.findall(r"^\| \d+ \| \*\*(.+?)\*\* \|", piece.read_text(), re.MULTILINE)


def test_the_toile_has_the_ten_fields_in_order() -> None:
    assert field_names(METHOD / "test" / "toile.md") == [
        "Assumption",
        "Risk",
        "Evidence so far",
        "Test design",
        "Pass line",
        "Time box",
        "Results",
        "Learnings",
        "Decision",
        "Next action",
    ]
