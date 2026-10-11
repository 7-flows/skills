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


def test_the_swatch_has_the_seven_fields_in_order() -> None:
    assert field_names(METHOD / "test" / "swatch.md") == [
        "Source",
        "Signals",
        "Pattern",
        "Strength",
        "So what",
        "Assumption touched",
        "Action",
    ]


# A founder off the web must find their own trade in every example table, not
# translate a software one (C26).
WEB = re.compile(
    r"\b(page|website|online|visitors?|sign-?ups?|signed up|tickets?|tiers?|app"
    r"|ads?|churn\w*|onboarding|users?|subscri\w*|newsletter|email list|checkout"
    r"|clicks?|instagram|online shop)\b",
    re.IGNORECASE,
)


def example_columns(piece: Path) -> list[list[str]]:
    rows = re.findall(r"^\| \d+ \| \*\*.+?\*\* \|(.*)\|$", piece.read_text(), re.M)
    cells = [[c.strip() for c in row.split("|")][1:] for row in rows]
    return [list(column) for column in zip(*cells, strict=True)]


def test_every_piece_has_an_example_off_the_web() -> None:
    for piece in ("toile.md", "swatch.md"):
        columns = example_columns(METHOD / "test" / piece)
        assert len(columns) >= 2, f"{piece}: one example column only"
        # A quoted example, not a dash or blank standing in for one.
        assert all(re.fullmatch(r'".{3,}"', c) for col in columns for c in col), (
            f"{piece}: an example cell is not a quoted example"
        )
        assert any(not any(WEB.search(c) for c in col) for col in columns), (
            f"{piece}: every example column leans on the web"
        )


def toile_core() -> str:
    return (METHOD / "test" / "toile.md").read_text().split("<!-- core -->")[1]


def test_the_toile_tests_the_offer_never_the_care() -> None:
    core = toile_core()
    assert "never the care" in core
    assert "a Toile on the offer instead" in core


def test_web_tools_wait_for_the_founder() -> None:
    assert "unless the founder brings" in toile_core()
